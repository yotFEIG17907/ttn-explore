from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """
    Gets current time in the UTC timezone
    :return: Datetime object for current time in UTC timezone
    """
    timenow = datetime.now(timezone.utc)
    return timenow


def formatiso8601(timestamp: datetime) -> str:
    """
    Format the given time in ISO 8601 format. If the zone is UTC thus the
    offset from UTC is +00:00 replace this with the letter Z
    :param timestamp: A unix timestamp object
    :return: A string with the time formatted in ISO8601
    """
    return datetime.isoformat(timestamp, timespec='milliseconds').replace('+00:00', 'Z')
