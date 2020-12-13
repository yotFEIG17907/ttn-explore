"""
A class to wrap dealing with the MQTT broker
Background reading: http://www.steves-internet-guide.com/into-mqtt-python-client/
"""
import logging
from abc import ABC, abstractmethod

import paho.mqtt.client as mqtt


class SensorListener(ABC):
    """
    An interface supported by an object that receives the payload from the messages
    """

    @abstractmethod
    def on_message(self, topic: bytes, payload: bytes):
        pass

    @abstractmethod
    def on_disconnect(self, reason: str):
        pass

    @abstractmethod
    def on_connection_event(self, reason: str) -> None:
        """
        Notifies the Sensor Listener of connection related events
        :param reason: Human readable and parseable text describing the event
        :return: None
        """
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
    qos: int  # The desired quality of service

    def __init__(self,
                 cert_path: str,
                 username: str,
                 password: str,
                 hostname: str,
                 port: int,
                 msg_listener: SensorListener = None):
        client_id = "kam-th-lora-10132020"
        # Clean session = False is to attempt to make a persistent subscriber
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311, clean_session=False)
        # Connect the client's callback functions to the methods in this class
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log
        self.client.on_subscribe = self.on_subscribe
        # See if leaving this as is will improve the re-connection
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(username=username, password=password)
        self.client.tls_set(ca_certs=cert_path)
        self.hostname = hostname
        self.ssl_port = port
        self.msg_listener = msg_listener
        self.logger = logging.getLogger("lora.mqtt")
        self.qos = 1  # At least once

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
        if rc == 0:
            # subscribe for all devices of user
            topic = '+/devices/+/up'
            res = client.subscribe(topic, qos=self.qos)
            if res[0] != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"Subscribe failed, the client is not really connected {res[0]}")
            msg = f"Subscribed to messages for all devices {topic} returned mid {res[1]}"
            self.logger.info(msg)
            self.msg_listener.on_connection_event(msg)
        else:
            msg = f"Connection failed {str(rc)} {mqtt.connack_string(rc)}"
            self.msg_listener.on_connection_event(msg)
            raise RuntimeError(msg)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        '''
        Callback for the subscribe call
        :param client:
        :param userdata:
        :param mid: Message id that was returned in the subscribe call
        :param granted_qos: The QOS that was granted to the subscriber
        :return: None
        '''
        self.logger.info(f"Subscribed mid {mid} Granted QOS {granted_qos}")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
        if self.msg_listener is not None:
            self.msg_listener.on_message(msg.topic, msg.payload)

    # The callback for when a disconnect message is received regarding the mqtt connection.
    def on_disconnect(self, client, userdata, rc):
        msg = f"Disconnected status {mqtt.error_string(rc)}"
        self.logger.warning(msg)
        if self.msg_listener is not None:
            msg = mqtt.error_string(rc)
            self.msg_listener.on_disconnect(mqtt.error_string(rc))
            self.msg_listener.on_connection_event(msg)

    def on_log(self, client, userdata, level, buf):
        """
        Log all MQTT protocol events, and the exceptions in callbacks
        that have been caught by Paho.
        """
        logging_level = mqtt.LOGGING_LEVEL[level]
        logging.log(logging_level, buf)
        self.msg_listener.on_connection_event(buf)
