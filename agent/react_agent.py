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

    def execute_stream(self, query: str, history: list | None = None):
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

        input_dict = {
            "messages": messages
        }

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

            if content:
                yield content.strip() + "\n"




if __name__ == '__main__':
    agent = ReactAgent()
    for chunk in agent.execute_stream("给我生成我的使用报告"):
        print(chunk, end="", flush=True)

