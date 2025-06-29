import configparser
from datetime import datetime
from zoneinfo import ZoneInfo

cfg = configparser.ConfigParser()
cfg.read("config.ini")

user_timezone = cfg["timezonesetting"]["tz_setting"]

## this isn't used as we save the laptime as we get it from the api and do the conversions externally
## however, we keep it in for now so it can be used later if needed
def time_convert(raw: int) -> str:
    """Convert lap time from 1/10000 seconds to ``M:SS.mmm`` format."""
    ms_total = raw // 10
    secs, ms = divmod(ms_total, 1000)
    mins, secs = divmod(secs, 60)
    return f"{mins}:{secs:02d}.{ms:03d}"


def sr_convert(sr_number: int) -> float:
    """Convert safety rating stored as an integer to a float."""
    return sr_number / 100


def licence_from_level(level: int | None) -> str | None:
    """Return the licence letter for a numeric level."""
    mapping = {20: "A", 19: "A", 18: "A", 17: "A", 15: "B", 14: "B", 13: "B", 10: "C", 9: "C", 6: "D"}
    if level is None:
        return None
    return mapping.get(level)


def format_session_time(raw_time: str) -> str:
    """Convert an ISO timestamp to ``YYYY-MM-DD HH:MM:SS`` in user defined time."""
    dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
    tz_converted = dt.astimezone(ZoneInfo(user_timezone))
    return tz_converted.strftime("%Y-%m-%d %H:%M:%S")
