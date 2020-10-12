"""
Enums and classes relating to message fields
"""
from enum import Enum


class THSensorMsgType(Enum):
    """
    Enumerates values for RadioBridge TH Sensor messages
    https://radiobridge.com/documents/Common%20Sensor%20Messages.pdf
    """
    # These message types are common to all RadioBridge sensors
    RESET = 0, "Reset"
    SUPERVISORY = 1, "Supervisory"
    TAMPER = 2, "Tamper Event has occurred"
    LINK_QUALITY = 0xFB, "Link Quality sent after each downlink configuration change"
    ACK = 0xFE, "Downlink message acknowledgement"
    # These are specific to the Temperature-Humidity Sensors
    UPLINK = 0x0D, "Temperature Event"

    def __new__(cls, value: int, desc: str):
        member = object.__new__(cls)
        member._value_ = value
        member.description = desc
        return member

    def __int__(self):
        """
        Get the enum as an integer; to get this the enum has to be converted, e.g.
        my_enum = THSensorEventType.TEMP_ABOVE_UPPER
        print((int)my_enum)
        >> 1
        :return: The enum converted to an integer
        """
        return self._value_


class THSensorEventType(Enum):
    """
    Enumerates values for the various sensor measurement events,
    this is when msgtype field indicates this is a sensor event.
    Illustrates yet another way to create an enum with atttributes
    """

    PERIODIC = 0, "Periodic Report"
    TEMP_ABOVE_UPPER = 1, "Temperature above upper threshold"
    TEMP_BELOW_LOWER = 2, "Temperature below lower threshold"
    TEMP_CHANGE_INCREASE = 3, "Temp report on change increase"
    TEMP_CHANGE_DECREASE = 4, "Temp report on change decrease"
    HMD_ABOVE_UPPER = 5, "Humidity above upper threshold"
    HMD_BELOW_LOWER = 6, "Humidity below lower threshold"
    HMD_CHANGE_INCREASE = 7, "Humidity report on change increase"
    HMD_CHANGE_DECREASE = 8, "Humidity report on change decrease"

    def __new__(cls, value: int, desc: str):
        member = object.__new__(cls)
        member._value_ = value
        member.description = desc
        return member

    def __int__(self):
        """
        Get the enum as an integer; to get this the enum has to be converted, e.g.
        my_enum = THSensorEventType.TEMP_ABOVE_UPPER
        print((int)my_enum)
        >> 1
        :return: The enum converted to an integer
        """
        return self._value_
