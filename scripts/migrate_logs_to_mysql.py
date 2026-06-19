import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from session.models import AppLogORM
from utils.db import SessionLocal
from utils.path_tool import get_abs_path


LOG_LINE_PATTERN = re.compile(
    r"^(?P<created_at>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) "
    r"- (?P<logger_name>.*?) "
    r"- (?P<level>[A-Z]+) "
    r"- (?P<filename>.*?):(?P<lineno>\d+) "
    r"- (?P<message>.*)$"
)


def parse_log_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S,%f")


def flush_record(db, record):
    if not record:
        return 0

    # 防止重复迁移：同一个日志文件的同一行只导入一次
    exists = db.query(AppLogORM).filter(
        AppLogORM.source == "file_migration",
        AppLogORM.source_log_file == record["source_log_file"],
        AppLogORM.source_log_line == record["source_log_line"],
    ).first()

    if exists:
        return 0

    exception_text = None
    if record["extra_lines"]:
        exception_text = "\n".join(record["extra_lines"])

    log = AppLogORM(
        created_at=record["created_at"],
        logger_name=record["logger_name"],
        level=record["level"],
        level_no=record["level_no"],
        message=record["message"],

        filename=record["filename"],
        lineno=record["lineno"],

        source="file_migration",
        source_log_file=record["source_log_file"],
        source_log_line=record["source_log_line"],

        exception_text=exception_text,

        metadata_json=json.dumps(
            {
                "migration": True,
                "original_file": record["source_log_file"],
            },
            ensure_ascii=False,
        ),
    )

    db.add(log)
    return 1


def level_to_no(level: str) -> int:
    mapping = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    return mapping.get(level, 0)


def migrate_file(db, file_path: Path) -> int:
    imported_count = 0
    current_record = None

    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.rstrip("\n")
            match = LOG_LINE_PATTERN.match(line)

            if match:
                imported_count += flush_record(db, current_record)

                data = match.groupdict()

                current_record = {
                    "created_at": parse_log_time(data["created_at"]),
                    "logger_name": data["logger_name"],
                    "level": data["level"],
                    "level_no": level_to_no(data["level"]),
                    "filename": data["filename"],
                    "lineno": int(data["lineno"]),
                    "message": data["message"],
                    "source_log_file": str(file_path),
                    "source_log_line": line_no,
                    "extra_lines": [],
                }
            else:
                # traceback 或多行日志，挂到上一条日志后面
                if current_record:
                    current_record["extra_lines"].append(line)

        imported_count += flush_record(db, current_record)

    db.commit()
    return imported_count


def main():
    log_root = Path(get_abs_path("logs"))

    if not log_root.exists():
        print(f"logs folder not found: {log_root}")
        return

    log_files = sorted(log_root.glob("*.log"))

    if not log_files:
        print(f"no log files found in: {log_root}")
        return

    db = SessionLocal()

    try:
        total = 0

        for file_path in log_files:
            count = migrate_file(db, file_path)
            total += count
            print(f"migrated {count} rows from {file_path}")

        print(f"done, total imported: {total}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()