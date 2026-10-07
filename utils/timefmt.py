"""Shows the database's UTC timestamps in the computer's own time zone."""

from datetime import datetime, timezone


def to_local(timestamp, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Turn 'YYYY-MM-DD HH:MM:SS' in UTC, as SQLite stores it, into local time.

    Anything that cannot be read as a timestamp is returned as it is.
    """
    if timestamp is None:
        return ""
    try:
        moment = datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return str(timestamp)
    return moment.replace(tzinfo=timezone.utc).astimezone().strftime(fmt)
