"""
A class to wrap dealing with the MQTT broker
"""
import logging
from abc import ABC, abstractmethod

import paho.mqtt.client as mqtt


class SensorListener(ABC):
    """
    An interface supported by an object that receives the payload from the messages
    """
    @abstractmethod
    def on_message(self, topic: bytes, payload:bytes):
        pass

    @abstractmethod
    def on_disconnect(self, reason: str):
        pass

class MqttComms:
    """
    A class that wraps the MQTT client and is an interface between
    it and a listener that handles the messages
    """
    client: mqtt.Client
    hostname: str
    ssl_port: int
    msg_listener: SensorListener

    def __init__(self,
                 cert_path: str,
                 username: str,
                 password: str,
                 hostname: str,
                 port: int,
                 msg_listener: SensorListener = None):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(username=username, password=password)
        self.client.tls_set(ca_certs=cert_path)
        self.hostname = hostname
        self.ssl_port = port
        self.msg_listener = msg_listener
        self.logger = logging.getLogger("lora.mqtt")

    def connect_and_start(self, keep_alive_seconds: int):
        self.client.connect(host=self.hostname, port=self.ssl_port, keepalive=keep_alive_seconds)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting. Which is great, if it disconnects the re-connection is automatic.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            self.client.loop_stop(force=True)
            self.client.disconnect()
        except Exception as e:
            self.logger.warning(f"Some problem {str(e)})")
            self.client.loop_stop(force=True)
            self.client.disconnect()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected with result code " + str(rc) + " " + mqtt.connack_string(rc))
        # subscribe for all devices of user
        client.subscribe('+/devices/+/up')
        self.logger.info("Subscribed to messages for all devices")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
        if self.msg_listener is not None:
            self.msg_listener.on_message(msg.topic, msg.payload)

    def on_disconnect(self, client, userdata, rc):
        self.logger.warning(f"Disconnected status {mqtt.error_string(rc)}")
        if self.msg_listener is not None:
            self.msg_listener.on_disconnect(mqtt.error_string(rc))