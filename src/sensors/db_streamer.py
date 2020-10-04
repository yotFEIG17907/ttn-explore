from src.sensors.mqtt_comms import SensorListener


class Streamer(SensorListener):
    """
    This receives the payload and stores it to the database
    """

    def on_message(self, topic:str, payload: str):
        print(topic, payload)

    def on_disconnect(self, reason: str):
        print(f"Upstream disconnected - {reason}")

