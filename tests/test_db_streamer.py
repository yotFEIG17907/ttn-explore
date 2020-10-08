from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, TempHumidityMeasurement
from sensors.db_streamer import Streamer
from tests.testdata import test_periodic_msgs
from utils.date_time_utils import get_utc_now, formatiso8601


def test_on_message():
    # The topic is somewhat made up but all the topics look similar to this
    # Different kind of messages on the same topic
    topic = "skybar-sensors/devices/sky-bar-chill-room/up"
    streamer = Streamer()
    counter = 0
    for msg in test_periodic_msgs:
        streamer.on_message(topic, msg)
        counter = counter + 1
    assert counter == len(test_periodic_msgs)


def test_db_models():
    # Use an in-memory database to test
    # Set this true to see all the SQL
    sql_logging_on = False
    engine = create_engine('sqlite:///:memory:', echo=sql_logging_on)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    timenow = get_utc_now()
    measurement = TempHumidityMeasurement (temp_c=19.0, humidity=17, timestamp=timenow)
    session.add(measurement)
    session.commit()

    # Get the events
    all_events = session.query(TempHumidityMeasurement).all() # type List[TempHumidityMeasurement]
    assert len(all_events) > 0
    print()
    for event in all_events:
        print(event)