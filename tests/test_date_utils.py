"""
Tests for the datetime parsing
"""
from datetime import timezone

from utils.date_time_utils import parseiso8601, formatiso8601


def test_iso_to_datetime():
    timestamp_str = "2020-10-04T18:57:51.159517Z"
    tstamp_value = parseiso8601(timestamp_str)
    assert formatiso8601(tstamp_value, timespec='microseconds') == timestamp_str
    assert tstamp_value.tzinfo is not None
    assert tstamp_value.tzinfo == timezone.utc