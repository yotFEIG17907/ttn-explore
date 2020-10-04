from src.sensors.db_streamer import Streamer
from tests.testdata import test_periodic_msgs


def test_on_message():
    # The topic is somewhat made up but all the topics look similar to this
    # Different kind of messages on the same topic
    topic = "skybar-sensors/devices/sky-bar-chill-room/up"
    streamer = Streamer()
    for msg in test_periodic_msgs:
        streamer.on_message(topic, msg)
