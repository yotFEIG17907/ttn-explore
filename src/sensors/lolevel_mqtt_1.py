"""
TTN MQTT API Reference: https://www.thethingsnetwork.org/docs/applications/mqtt/api.html

This program uses Paho MQTT Client to make a SSL connection.  The source code for this client is here:
https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/
"""
import configparser

import paho.mqtt.client as mqtt

# The path is relative to the sensors folder which is where this script is
mqtt_ca_path = "../../certs/mqtt-ca.pem"
ini_file_path = "../../config/temp-sensors.ini"
# The configuration file path will become a command-line argument
config = configparser.ConfigParser()
config.read(ini_file_path)
connection = config['ttn-explore.mqtt.connection']
username = connection['username']  # This is the Application ID for this integration at TTN
password = connection['password']  # This is the my-python-client application access key
region = connection['region']
hostname = f"{region}.thethings.network"
sslport = connection.getint('sslport')

"""
Topic format <AppID>/devices/<DevID>/up
AppID is the name of the "Application" specified in the things network, which in this case is skybar-sensors
same as the username.
DevID is the friendly name of the device, as given in the Things Network device overview.
If <AppID> is + then it will subscribe to all users accessible with this user name.
If <DevID> is + then it will fetch all devices for the given application ID.
"""


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc) + " " + mqtt.connack_string(rc))
    # subscribe for all devices of user
    client.subscribe('+/devices/+/up')
    print("Subscribed to messages for all devices")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username=username, password=password)
    client.tls_set(ca_certs=mqtt_ca_path)

    client.connect(host=hostname, port=sslport, keepalive=60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting. Which is great, if it disconnects the re-connection is automatic.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop(force=True)
        client.disconnect()
    except Exception as e:
        print(f"Some problem {str(e)})")
        client.loop_stop(force=True)
        client.disconnect()


if __name__ == "__main__":
    main()
