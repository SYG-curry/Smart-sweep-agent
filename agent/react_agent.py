from langchain.agents import create_agent
from agent.tools.agent_tools import rag_summarize, get_weather, get_user_location, get_user_id, \
    fetch_external_data, fill_context_for_report
from agent.tools.middleware import monitor_tool, report_prompt_switch, log_before_model
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[
                rag_summarize,
                get_weather,
                get_user_location,
                get_user_id,
                fetch_external_data,
                fill_context_for_report
            ],
            middleware=[
                monitor_tool,
                log_before_model,
                report_prompt_switch
            ]
        )

    def _build_input(self, query: str, history: list | None = None):
        messages = []

        if history:
            for item in history:
                messages.append({
                    "role": item.role,
                    "content": item.content,
                })

        messages.append({
            "role": "user",
            "content": query,
        })

        return {"messages": messages}

    # 不展示 thinking 过程，兼容旧 /api/chat 接口
    def execute_stream(self, query: str, history: list | None = None):
        input_dict = self._build_input(query, history)
        last_content = ""

        for chunk in self.agent.stream(
                input_dict,
                stream_mode="values",
                context={"report": False},
        ):
            if not isinstance(chunk, dict):
                continue

            chunk_messages = chunk.get("messages")
            if not chunk_messages:
                continue

            latest_message = chunk_messages[-1]
            content = getattr(latest_message, "content", None)
            if not content:
                continue

            if content.startswith(last_content):
                delta = content[len(last_content):]
            else:
                delta = content

            # last_content 必须保存完整内容，不能保存 delta
            last_content = content

            if delta:
                yield delta

    # 提取token文本
    def _extract_token_text(self, token) -> str:
        """
            从 langchain 的 token chunk中提取真实文本
            不同模型/版本返回结构可能略有差异
            1. token.content is str
            2. token.content is list
            3. token.content_blocks includes text block
            这里做兼容处理, 避免因为某一种结构变化导致前端没输出
        """
        content = getattr(token, "content", None)

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") in ("text", "text_delta"):
                        texts.append(item.get("text", ""))
                elif isinstance(item, str):
                    texts.append(item)
            return "".join(texts)

        content_blocks = getattr(token, "content_blocks", None)
        if isinstance(content_blocks, list):
            texts = []
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") in ("text", "text_delta"):
                    texts.append(block.get("text", ""))
            return "".join(texts)

        return ""

    # 识别工具调用
    def _extract_tool_name_from_token(self, token) -> str | None:
        """
            从 token chunk 中识别工具调用名称
            Agent执行时, 模型可能先输出 tool_call_chunk,
            例如决定调用 rag_summarize
            我们把它转成 thinking 事件, 显示在前端思考过程里
        """
        content_blocks = getattr(token, "content_blocks", None)

        if isinstance(content_blocks, list):
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "tool_call_chunk":
                    name = block.get("name")
                    if name:
                        return name

        content = getattr(token, "content", None)

        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_call_chunk":
                    name = item.get("name")
                    if name:
                        return name

        return None

    # 流式输出，展示 thinking 过程和最终 answer
    def execute_event_stream(self, query: str, history: list | None = None):
        """
            token 级流式输出
            输出结构化事件流，用于前端区分：
            1. thinking：小号灰色展示的执行过程
            2. answer：正常字号展示的最终答案

            注意：thinking 不是模型私有推理链，而是可解释的执行过程提示。
        """
        input_dict = self._build_input(query, history)

        yield {
            "type": "thinking",
            "content": "正在理解你的问题...\n"
        }

        called_tools = set()
        has_answer_started = False

        for token, metadata in self.agent.stream(
            input_dict,
            stream_mode="messages",
            context={"report": False}
        ):
            # metadata 可用于判断当前 token 来自哪个 langgraph 节点
            node_name = metadata.get("langgraph_node", "") if isinstance(metadata, dict) else ""

            # 1.识别工具调用 token
            tool_name = self._extract_tool_name_from_token(token)
            if tool_name and tool_name not in called_tools:
                called_tools.add(tool_name)
                yield {
                    "type": "thinking",
                    "content": f"正在调用工具 {tool_name}...\n"
                }
                continue

            # 2.如果当前节点是工具节点, 可以给一个工具执行中的提示
            if node_name == "tools":
                continue

            # 3.提取模型 token 文本
            text = self._extract_token_text(token)

            if not text:
                continue

            # 4.第一次真正输出答案前, 补一个 thinking 提示
            if not has_answer_started:
                has_answer_started = True
                if called_tools:
                    yield {
                        "type": "thinking",
                        "content": "工具结果已返回, 正在生成最终回答...\n"
                    }
                else:
                    yield {
                        "type": "thinking",
                        "content": "正在生成最终回答...\n"
                    }

            yield {
                "type": "answer",
                "content": text,
            }


if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)
