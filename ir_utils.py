from datetime import datetime


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
    mapping = {20: "A", 14: "B"}
    if level is None:
        return None
    return mapping.get(level)


def format_session_time(raw_time: str) -> str:
    """Convert an ISO timestamp to ``YYYY-MM-DD HH:MM:SS``."""
    dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")