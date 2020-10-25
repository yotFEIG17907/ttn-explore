from pathlib import Path
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, TempHumidityMeasurement, Sensor, Supervisory
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
    expected_event_count = expected_periodic_msg_count + expected_hmd_change_count
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
        # Get the events
        all_events = session.query(TempHumidityMeasurement) \
            .all()  # type: List[TempHumidityMeasurement]
        assert len(all_events) == expected_event_count
        # Get the sensors
        all_sensors = session.query(Sensor).all()  # type: List[Sensor]
        assert len(all_sensors) == expected_sensor_count
        # Check supervisory
        all_sup = session.query(Supervisory).all()
        assert len(all_sup) == expected_sup_count
    finally:
        session.close()
