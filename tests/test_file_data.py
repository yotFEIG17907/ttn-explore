from pathlib import Path
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, TempHumidityMeasurement, Sensor, Supervisory, LoraEvent
from sensors.db_streamer import Streamer


def test_on_message():
    # The topic is somewhat made up but all the topics look similar to this
    # Different kind of messages on the same topic
    # The messages come from a file of test data
    test_data_path = Path("./testdata/messages.txt")
    topic = "skybar-sensors/devices/sky-bar-chill-room/up"
    # Use an in-memory database to test
    # Set this true to see all the SQL
    sql_logging_on = False
    engine = create_engine('sqlite:///:memory:', echo=sql_logging_on)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    streamer = Streamer(Session)
    counter = 0
    expected_mixed_msg_count = 309
    expected_periodic_msg_count = 254
    expected_hmd_change_count = 2
    expected_sup_count = expected_mixed_msg_count - expected_periodic_msg_count \
                         - expected_hmd_change_count
    expected_measurement_count = expected_periodic_msg_count + expected_hmd_change_count
    expected_sensor_count = 3

    with open(test_data_path, "r") as reader:
        for msg in reader:
            streamer.on_message(topic, msg.encode("utf-8"))
            counter = counter + 1
        assert counter == expected_mixed_msg_count
    #
    # Now query for the events and see what is there
    session = Session()
    try:
        all_events = session.query(LoraEvent).all()  # type: List[LoraEvent]
        assert len(all_events) == expected_mixed_msg_count

        # Get the measurements
        all_measurements = session.query(TempHumidityMeasurement) \
            .all()  # type: List[TempHumidityMeasurement]
        assert len(all_measurements) == expected_measurement_count
        # Check supervisory
        all_sup = session.query(Supervisory).all()  # type: List[Supervisory]
        assert len(all_sup) == expected_sup_count
        # Get the sensors
        all_sensors = session.query(Sensor).all()  # type: List[Sensor]
        assert len(all_sensors) == expected_sensor_count

        # Get the sum of measurements and supervisory
        meas_count = 0
        sup_count = 0
        for sensor in all_sensors:
            meas_count = meas_count + len(sensor.measurements.all())
            sup_count = sup_count + len(sensor.supervisory.all())
        assert meas_count == expected_measurement_count
        assert sup_count == expected_sup_count


    finally:
        session.close()
