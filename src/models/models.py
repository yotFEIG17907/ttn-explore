"""
This is the ORM mapping, it maps classes to tables using SQLAlchemy mapping
The message classes form a hierarchy. This is mapped to the database using
"Single Table Inheritance" described here: https://docs.sqlalchemy.org/en/13/orm/inheritance.html
"""
from datetime import timezone, datetime

from sqlalchemy import types, Column, Integer, Float, String, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from utils.date_time_utils import formatiso8601


class CustomDateTime(types.TypeDecorator):
    """
    Maps unix timestamp to a float
    """

    impl = types.Integer

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif value.tzinfo is None or value.tzinfo != timezone.utc:
            raise ValueError("There must be a TZ and it must be UTC")
        else:
            return value.timestamp()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            return datetime.fromtimestamp(value, timezone.utc)


Base = declarative_base()


class Sensor(Base):
    """
    Holds the key details about temp sensors. This class is specifically for temp and humidity
    because the relationship is explicit about the class. There is a one-to-many relationship
    between the sensor and the measurements. With some thought this class could become
    a base class for all sensors, maybe.
    """
    __tablename__ = 'sensor'

    device_id = Column(String(16), primary_key=True)
    device_name = Column(String(64), nullable=False)
    # Relationship, 1st arg is the name of the children class and the
    # 2nd argument is the table it back-populates.
    # 3rd argument specifies how the children are to be loaded. The default 'select'
    # means they will all be loaded when the sensor (the parent is loaded). So events would
    # be populated right away and would be a list. But 'dynamic' as shown here defers loading the
    # children and measurements in this case is an AppenderQuery and hows additional filtering to
    # be applied before getting the measurements; clearly if there are a lot of measurements
    # it is better to add a query to get the ones you want rather than getting them all. And of
    # course this will be events only for this sensor.
    # Note that LoraEvent is a base class for all the kinds of messages that a Sensor can
    # publish, e.g. Supervisory and Temperature and Humidity
    events = relationship("LoraEvent", back_populates="sensor", lazy='dynamic')
    measurements = relationship("TempHumidityMeasurement", back_populates="sensor", lazy='dynamic')
    supervisory = relationship("Supervisory", back_populates="sensor", lazy='dynamic')
    linkq = relationship("LinkQ", back_populates="sensor", lazy='dynamic')

    def __repr__(self):
        return f"Sensor(Device ID {self.device_id} Name {self.device_name})"


class LoraEvent(Base):
    """
    The base class for Events published by the Lora Sensors. There is only
    this table; all subclasses store their data in rows in this table; each row
    contains a union of the columns for all the subclasses with columns that
    do not apply to a particular subclass set to null. The base class has a type field
    that SQLAlchemy uses to identify the kind of each row
    """
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    type = Column(String(32))

    timestamp = Column(CustomDateTime, nullable=False)
    counter = Column(Integer, nullable=False)
    raw_message = Column(LargeBinary, nullable=False)
    sensor_id = Column(String(16), ForeignKey('sensor.device_id'))
    sensor = relationship("Sensor", back_populates="events")

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'event'
    }


class TempHumidityMeasurement(LoraEvent):
    """
    Represents a single temperature and humidity measurement. Designed for
    sensors that provide a reading of both temp and humidity in a single timestamped message.
    The columns must be nullable because other sibling classes won't have these.
    """
    temp_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'measurement'
    }

    def __repr__(self):
        return f"TempHumidityMeasurement(Device_ID={self.sensor.device_id}, " \
               f"Device_Name={self.sensor.device_name}, " \
               f"Counter={self.counter}, " \
               f"Temp_C={self.temp_c}, " \
               f"Humidity_Percent={self.humidity_percent}, " \
               f"Timestamp={formatiso8601(self.timestamp)})"


class Supervisory(LoraEvent):
    """
    Holds a single Supervisory message
    """

    __mapper_args__ = {
        'polymorphic_identity': 'supervisory'
    }

    def __repr__(self):
        return f"Supervisory(Device_ID={self.sensor.device_id}, " \
               f"Device_Name={self.sensor.device_name}, " \
               f"Counter={self.counter}, " \
               f"Timestamp={formatiso8601(self.timestamp)})"


class LinkQ(LoraEvent):
    """
    Holds a single Supervisory message
    """

    __mapper_args__ = {
        'polymorphic_identity': 'linkq'
    }

    def __repr__(self):
        return f"LinkQ(Device_ID={self.sensor.device_id}, " \
               f"Device_Name={self.sensor.device_name}, " \
               f"Counter={self.counter}, " \
               f"Timestamp={formatiso8601(self.timestamp)})"
