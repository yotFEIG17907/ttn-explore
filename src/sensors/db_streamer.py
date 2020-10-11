import json
from collections import namedtuple
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker, scoped_session, Session

from models.models import Sensor, TempHumidityMeasurement
from sensors.mqtt_comms import SensorListener
from utils.date_time_utils import parseiso8601


def customMeasurementDecoder(measurementDict):
    """
    Convert the dictionary into a named tuple
    :param measurementDict: A dictionary loaded from the JSON measurement measure
    :return: A NamedTuple that has all the values in an easily accessible format
    """
    return namedtuple('X', measurementDict.keys())(*measurementDict.values())


class Streamer(SensorListener):
    """
    This receives the payload and stores it to the database
    """

    def __init__(self, Session):
        self.Session = scoped_session(Session)

    @contextmanager
    def session_scope(self):
        """ Provide a transactional scope around a series of operations"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def on_message(self, topic: bytes, payload: bytes):
        measurement = json.loads(payload, object_hook=customMeasurementDecoder)
        if measurement.payload_fields.event_type == "Periodic Report":
            device_id = measurement.hardware_serial
            device_name = measurement.dev_id
            temp_c = measurement.payload_fields.temp_c
            humidity_percent = measurement.payload_fields.humidity_percent
            timestamp = parseiso8601(measurement.metadata.time)
            print(topic, f"dev_name {measurement.dev_id} dev_id {measurement.hardware_serial}")
            with self.session_scope() as session:
                # Make a new device if this one does not exist
                sensor = session.query(Sensor).get(device_id)
                if sensor is None:
                    sensor = Sensor(device_id=device_id, device_name=device_name)
                th_event = TempHumidityMeasurement (temp_c=temp_c,
                                                    humidity_percent=humidity_percent,
                                                    timestamp=timestamp,
                                                    sensor=sensor)
                session.add(th_event)

    def on_disconnect(self, reason: str):
        print(f"Upstream disconnected - {reason}")
