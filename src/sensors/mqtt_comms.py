"""
A class to wrap dealing with the MQTT broker
"""
import paho.mqtt.client as mqtt


class MqttComms:
    client: mqtt.Client
    hostname: str
    ssl_port: int

    def __init__(self, cert_path: str, username: str, password: str, hostname: str, port: int):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(username=username, password=password)
        self.client.tls_set(ca_certs=cert_path)
        self.hostname = hostname
        self.ssl_port = port

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
            print(f"Some problem {str(e)})")
            self.client.loop_stop(force=True)
            self.client.disconnect()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc) + " " + mqtt.connack_string(rc))
        # subscribe for all devices of user
        client.subscribe('+/devices/+/up')
        print("Subscribed to messages for all devices")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
