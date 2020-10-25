from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, TempHumidityMeasurement, Sensor, LoraEvent
from sensors.db_streamer import Streamer
from tests.testdata import test_mixed_msgs
from utils.date_time_utils import get_utc_now


def test_on_message():
    # The topic is somewhat made up but all the topics look similar to this
    # Different kind of messages on the same topic
    topic = "skybar-sensors/devices/sky-bar-chill-room/up"
    # Use an in-memory database to test
    # Set this true to see all the SQL
    sql_logging_on = False
    engine = create_engine('sqlite:///:memory:', echo=sql_logging_on)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    streamer = Streamer(Session)
    counter = 0
    expected_mixed_msg_count = 10
    expected_periodic_msg_count = 7
    expected_hmd_change_count = 2
    expected_event_count = expected_periodic_msg_count + expected_hmd_change_count
    expected_sensor_count = 3
    for msg in test_mixed_msgs:
        streamer.on_message(topic, msg)
        counter = counter + 1
    assert counter == expected_mixed_msg_count
    #
    # Now query for the events and see what is there
    session = Session()
    try:
        # Get all events
        all_events = session.query(LoraEvent).all()  # type: List[LoraEvent]
        assert len(all_events) == expected_mixed_msg_count

        # Get the measurements
        all_measurements = session.query(TempHumidityMeasurement).all()  # type: List[TempHumidityMeasurement]
        assert len(all_measurements) == expected_event_count

        # Get the sensors
        all_sensors = session.query(Sensor).all()  # type: List[Sensor]
        assert len(all_sensors) == expected_sensor_count
        print()
        for sensor in all_sensors:
            print(sensor, len(sensor.measurements.all()))
            print(sensor.measurements.all())
            print(sensor.supervisory.all())
    finally:
        session.close()


def test_db_models():
    # Use an in-memory database to test
    # Set this true to see all the SQL
    sql_logging_on = False
    engine = create_engine('sqlite:///:memory:', echo=sql_logging_on)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    timenow = get_utc_now()
    device_id = "xkksjdfsf"
    device_name = "My Test Device in the room"
    payload_bytes = str.encode(f"{device_id} {device_name}")

    sensor = Sensor(device_id=device_id, device_name=device_name)
    try:
        counter = 0
        for temp_c in [x / 10.0 for x in range(150, 300, 5)]:
            for humidity_percent in range(10, 40, 10):
                measurement = TempHumidityMeasurement(sensor=sensor,
                                                      counter=counter,
                                                      raw_message=payload_bytes,
                                                      temp_c=temp_c,
                                                      humidity_percent=humidity_percent,
                                                      timestamp=timenow)
                session.add(measurement)
                counter += 1
        session.commit()

        # Get the events
        all_events = session.query(TempHumidityMeasurement).all()  # type: List[TempHumidityMeasurement]
        assert len(all_events) == counter

        # Get the sensors
        all_sensors = session.query(Sensor).all()  # type: List[Sensor]
        assert len(all_sensors) == 1

        assert len(all_sensors[0].events.all()) == counter
    finally:
        session.close()
