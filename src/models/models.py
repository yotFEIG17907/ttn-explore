"""
This is the ORM mapping, it maps classes to tables using SQLAlchemy mapping
"""
from datetime import timezone, datetime

from sqlalchemy import types, Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

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


class TempHumidityMeasurement(Base):
    __tablename__ = 'temphum'

    id = Column(Integer, primary_key=True)
    temp_c = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    timestamp = Column(CustomDateTime, nullable=False)

    def __repr__(self):
        return f"TempHumidityMeasurement(Temp_C={self.temp_c}, " \
               f"Humidity={self.humidity}, " \
               f"Timestamp={formatiso8601(self.timestamp)})"
