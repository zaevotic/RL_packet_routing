import datetime
import inspect
from enum import Enum


class LogType(Enum):
    INFO="INFO"
    ERROR="ERROR"
    DEBUG="DEBUG"
    WARNING="WARNING"
    CRITICAL="CRITICAL"


def log(message,log_type=LogType.INFO,status="Success",
        general_logfile_path="app.log",print_log=False):
    if not isinstance(log_type,LogType):
        raise ValueError("log_type must be a LogType")

    timestamp=datetime.datetime.now().isoformat(timespec="milliseconds")
    frame=inspect.currentframe()
    caller=frame.f_back.f_code.co_name

    log_entry=f"{timestamp} {log_type.value} {caller} {status} {message}"

    if print_log:
        print(log_entry)

    with open(general_logfile_path,"a",encoding="utf-8") as f:
        f.write(log_entry+"\n")
