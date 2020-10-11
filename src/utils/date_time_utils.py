from datetime import datetime, timezone

from dateutil import parser as dp


def get_utc_now() -> datetime:
    """
    Gets current time in the UTC timezone
    :return: Datetime object for current time in UTC timezone
    """
    timenow = datetime.now(timezone.utc)
    return timenow


def formatiso8601(timestamp: datetime, timespec: str = 'milliseconds') -> str:
    """
    Format the given time in ISO 8601 format. If the zone is UTC thus the
    offset from UTC is +00:00 replace this with the letter Z
    :param timestamp: A unix timestamp object
    :param timespec: Specifies that resolution is to be used. The default is microseconds
    meaning the seconds field will have 3 places of decimals; supply 'microseconds' to
    get microsecond resolution (if your original datetime has the numbers). Nanoseconds
    not possible.
    :return: A string with the time formatted in ISO8601
    """
    return datetime.isoformat(timestamp, timespec=timespec).replace('+00:00', 'Z')


def parseiso8601(timestamp_str: str) -> datetime:
    """
    Parses a string in ISO8601 format with or without milliseconds.
    This requires the dateutil package
    :param timestamp_str: eg. 2020-10-04T18:57:51.159517049Z. Note: this
    shows the time to nanosecond resolution but is TBD on whether the datetime
    holds the value to nanosecond resolution.
    :return: datetime object with timezone
    """
    return dp.parse(timestamp_str).astimezone(timezone.utc)
