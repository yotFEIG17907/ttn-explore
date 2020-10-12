import json
import logging
from collections import namedtuple
from contextlib import contextmanager

from sqlalchemy.orm import scoped_session

from models.models import Sensor, TempHumidityMeasurement
from sensors.message_protocol import THSensorEventType, THSensorMsgType
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
        self.logger = logging.getLogger("lora.mqtt")

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
        try:
            measurement = json.loads(payload, object_hook=customMeasurementDecoder)
            # Temporary to gather more messages for testing
            self.logger.info(payload.decode())
            if measurement.payload_fields.msgtype == THSensorMsgType.SUPERVISORY.value:
                # Supervisory message - it has no data
                pass
            elif measurement.payload_fields.msgtype == THSensorMsgType.UPLINK.value:
                # Sensor event
                if measurement.payload_fields.sensor_event_type == THSensorEventType.PERIODIC.value or \
                        measurement.payload_fields.sensor_event_type == THSensorEventType.HMD_CHANGE_DECREASE.value or \
                        measurement.payload_fields.sensor_event_type == THSensorEventType.HMD_CHANGE_INCREASE.value or \
                        measurement.payload_fields.sensor_event_type == THSensorEventType.TEMP_CHANGE_DECREASE.value or \
                        measurement.payload_fields.sensor_event_type == THSensorEventType.TEMP_CHANGE_INCREASE.value:
                    device_id = measurement.hardware_serial
                    device_name = measurement.dev_id
                    temp_c = measurement.payload_fields.temp_c
                    humidity_percent = measurement.payload_fields.humidity_percent
                    timestamp = parseiso8601(measurement.metadata.time)
                    with self.session_scope() as session:
                        # Make a new device if this one does not exist
                        sensor = session.query(Sensor).get(device_id)
                        if sensor is None:
                            sensor = Sensor(device_id=device_id, device_name=device_name)
                        th_event = TempHumidityMeasurement(temp_c=temp_c,
                                                           humidity_percent=humidity_percent,
                                                           timestamp=timestamp,
                                                           raw_message=payload,
                                                           counter=measurement.counter,
                                                           sensor=sensor)
                        session.add(th_event)
                else:
                    self.logger.warning(f"Not one of the expected uplink messages" \
                                     f"{measurement.payload_fields.sensor_event_type}")
                    pass
            else:
                # Some other kind of message
                pass
        except Exception as e:
            self.logger.error(f"Exception parsing payload message {str(e)}")
            self.logger.error(f"Bad payload: {payload.decode()}")

    def on_disconnect(self, reason: str):
        self.logger.error(f"Upstream disconnected - {reason}")
