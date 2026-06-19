import json
import logging
import sys
from datetime import datetime

from session.models import AppLogORM
from utils.db import SessionLocal


class DatabaseLogHandler(logging.Handler):
    """
        将 python logging 记录写入MySQL
        注意：
            1. 这里不能使用业务请求中的db session
            2. 每条日志单独创建短生命周期 session
            3. 写入失败不能再 logger.error, 否则会递归打印日志
    """
    def __init__(self, level=logging.INFO):
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord):
        db = SessionLocal()

        try:
            exception_text = None

            if record.exc_info:
                exception_text = self.formatException(record.exc_info)
            elif getattr(record, "exc_text", None):
                exception_text = record.exc_text

            metadata = {
                "created_by": "logging",
            }

            log = AppLogORM(
                created_at=datetime.fromtimestamp(record.created),
                logger_name=record.name,
                level=record.levelname,
                level_no=record.levelno,
                message=record.getMessage(),
                pathname=record.pathname,
                filename=record.filename,
                module=record.module,
                func_name=record.funcName,
                lineno=record.lineno,
                process_id=record.process,
                thread_id=str(record.thread),
                # 这个request_id 后面会通过 LogRecordFactory 注入
                request_id=getattr(record, "request_id", None),
                exception_text=exception_text,
                stack_text=getattr(record, "stack_info", None),
                source="runtime",
                metadata_json=json.dumps(metadata, ensure_ascii=False),
            )
            db.add(log)
            db.commit()
        except Exception as exc:
            db.rollback()
            # 不要在这logger.error, 否则日志会无限递归
            print(
                f"[DatabaseLogHandler] write log failed: {type(exc).__name__}:{exc}",
                file=sys.stderr,
            )
        finally:
            db.close()




















