from sensors.mqtt_comms import SensorListener


class Streamer(SensorListener):
    """
    This receives the payload and stores it to the database
    """

    def on_message(self, topic:bytes, payload: bytes):
        print(topic, payload.decode())

    def on_disconnect(self, reason: str):
        print(f"Upstream disconnected - {reason}")

