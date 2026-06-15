from contextvars import ContextVar

# ContextVar 为每个独立的协程上下文创建一份独立的副本，像是一个“请求级别的全局变量”，完美隔离不同请求的数据
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
request_start_time_var: ContextVar[float] = ContextVar("request_start_time", default=0.0)


