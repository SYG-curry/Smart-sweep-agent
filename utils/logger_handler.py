import atexit
import logging
import logging.handlers
import queue
from api.context import request_id_var
from utils.db_log_handler import DatabaseLogHandler


# 日志格式配置
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

_log_listener = None

# 修改 Python 的日志 LogRecord 创建工厂，让它每次创建日志记录时，自动从请求上下文中取出 request_id 并附加进去
def _install_request_id_record_factory():
    """
        给每条 LogRecord 注入 request_id
        这样在任何地方写 logger.info()
        最终进入数据库时都能带上当前请求的 request_id
    """
    # 取出原始工厂
    old_factory = logging.getLogRecordFactory()

    # 避免重复包装
    if getattr(old_factory, "_smart_sweep_wrapped_", False):
        return

    def record_factory(*args, **kwargs):
        # 原始工厂创建标准LogRecord
        record = old_factory(*args, **kwargs)

        try:
            # 注入 request_id
            record.request_id = request_id_var.get(None)
        except Exception:
            record.request_id = None

        return record

    # 设置标记
    record_factory._smart_sweep_wrapped_ = True
    # 用 setLogRecordFactory 把新工厂安装到 logging 模块里. 从此以后，系统中任何 logger.info() 产生的日志记录都会自动包含 request_id 属性.
    logging.setLogRecordFactory(record_factory)

def _build_async_queue_handler(
        console_level: int,
        db_level: int,
) -> logging.Handler:
    """
        构造异步日志队列
        业务线程：
            logger.info()
                ↓
            QueueHandler 入队，立即返回
        后台线程：
            QueueListener 消费队列
                ↓
            控制台输出
            MySQL 写入
    """
    # 单例, 全局唯一
    global _log_listener
    # 无界队列
    log_queue = queue.Queue(-1)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    # 创建数据库处理器
    db_handler = DatabaseLogHandler(level=db_level)
    db_handler.setFormatter(DEFAULT_LOG_FORMAT)

    # 启动后台监听线程(消费者)
    _log_listener = logging.handlers.QueueListener(
        log_queue,
        console_handler,
        db_handler,
        respect_handler_level=True,     # 每个handler只处理符合自己级别的日志
    )
    _log_listener.start()       # 启动后台线程(全局唯一)

    atexit.register(_log_listener.stop)     # 注册优雅关闭

    # 创建QueueHandler(生产者)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    queue_handler.setLevel(min(console_level, db_level))

    return queue_handler


def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file = None,
) -> logging.Logger:
    _install_request_id_record_factory()

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logger.propagate = False

    queue_handler = _build_async_queue_handler(
        console_level=console_level,
        db_level=file_level,
    )


    logger.addHandler(queue_handler)

    return logger


# 快捷获取日志器
logger = get_logger()


if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")