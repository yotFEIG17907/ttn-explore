"""
This is the ORM mapping, it maps classes to tables using SQLAlchemy mapping
"""
from datetime import timezone, datetime

from sqlalchemy import types, Column, Integer, Float, String, ForeignKey
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
    # means they will all be loaded when the sensor (the parent is loaded). So measurements would
    # be populated right away and would be a list. But 'dynamic' as shown here defers loading the
    # children and measurements in this case is an AppenderQuery and hows additional filtering to
    # be applied before getting the measurements; clearly if there are a lot of measurements
    # it is better to add a query to get the ones you want rather than getting them all. And of
    # course this will be measurements only for this sensor.
    measurements = relationship("TempHumidityMeasurement", back_populates="sensor", lazy='dynamic')

    def __repr__(self):
        return f"Sensor(Device ID {self.device_id} Name {self.device_name})"


class TempHumidityMeasurement(Base):
    """
    Represents a single temperature and humidity measurement. Designed for
    sensors that provide a reading of both temp and humidity in a single timestamped message.
    """
    __tablename__ = 'temphum'

    id = Column(Integer, primary_key=True)
    temp_c = Column(Float, nullable=False)
    humidity_percent = Column(Float, nullable=False)
    timestamp = Column(CustomDateTime, nullable=False)
    sensor_id = Column(String(16), ForeignKey('sensor.device_id'))
    sensor = relationship("Sensor", back_populates="measurements")

    def __repr__(self):
        return f"TempHumidityMeasurement(Device_ID={self.sensor.device_id}," \
               f"Device_Name={self.sensor.device_name}," \
               f"Temp_C={self.temp_c}, " \
               f"Humidity_Percent={self.humidity_percent}, " \
               f"Timestamp={formatiso8601(self.timestamp)})"
