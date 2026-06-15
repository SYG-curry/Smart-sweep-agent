from typing import Callable
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,   # 请求的数据封装
        handler: Callable[[ToolCallRequest], ToolMessage | Command]     # 执行的函数本身
) -> ToolMessage | Command:     # 工具执行的监控
    logger.info(f"工具执行: {request.tool_call['name']}")
    logger.info(f"工具参数: {request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"工具{request.tool_call['name']}调用成功")

        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败, 错误信息: {str(e)}")
        raise e

@before_model
def log_before_model(
        state: AgentState,      # 整个Agent智能体中的状态记录
        runtime: Runtime,       # 记录了整个执行过程中的上下文信息
):
    logger.info(f"[before model] model启动, 并附带{len(state['messages'])}消息")
    logger.debug(f"[before model] {type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")
    return None

# 每一次生成提示词之前调用该函数
@dynamic_prompt
def report_prompt_switch(request: ModelRequest):    # 动态切换提示词
    is_report = request.runtime.context.get("report", False)
    if is_report:       # 如果是报告生成场景, 则返回报告生成提示词内容
        return load_report_prompts()
    return load_system_prompts()




