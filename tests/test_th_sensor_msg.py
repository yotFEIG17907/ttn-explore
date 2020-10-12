"""
Tests relating to parsing the TH Sensor messages
"""
import pytest

from sensors.message_protocol import THSensorEventType, THSensorMsgType


def test_sensor_event_enum():
    test_event_type = 3
    assert THSensorEventType.TEMP_CHANGE_INCREASE.description == "Temp report on change increase"
    assert int(THSensorEventType.TEMP_CHANGE_INCREASE) == test_event_type
    assert THSensorEventType.TEMP_CHANGE_INCREASE.value == test_event_type

    got_enum = THSensorEventType(test_event_type)
    assert got_enum == THSensorEventType.TEMP_CHANGE_INCREASE


def test_invalid_event_enum_value():
    """
    Test will fail if exception is not raised
    :return:
    """
    with pytest.raises(ValueError):
        got_num = THSensorEventType(1000)


def test_sensor_msg_enum():
    test_msg_type = 13
    assert THSensorMsgType.UPLINK.value == test_msg_type

def test_invalid_msg_enum_value():
    """
    Test will fail if exception is not raised
    :return:
    """
    with pytest.raises(ValueError):
        got_num = THSensorMsgType(1000)

