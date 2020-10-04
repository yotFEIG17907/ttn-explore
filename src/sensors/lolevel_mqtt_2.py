"""
TTN MQTT API Reference: https://www.thethingsnetwork.org/docs/applications/mqtt/api.html

This program uses Paho MQTT Client to make a SSL connection.  The source code for this client is here:
https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/
"""
import configparser

# The path is relative to the sensors folder which is where this script is
from src.sensors.db_streamer import Streamer
from src.sensors.mqtt_comms import MqttComms, SensorListener

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
keep_alive_seconds = connection.getint('keep_alive_seconds')

"""
Topic format <AppID>/devices/<DevID>/up
AppID is the name of the "Application" specified in the things network, which in this case is skybar-sensors
same as the username.
DevID is the friendly name of the device, as given in the Things Network device overview.
If <AppID> is + then it will subscribe to all users accessible with this user name.
If <DevID> is + then it will fetch all devices for the given application ID.
"""


#
def main():

    streamer = Streamer()

    comms = MqttComms(cert_path=mqtt_ca_path,
                      username=username,
                      password=password,
                      hostname=hostname,
                      port=sslport,
                      msg_listener=streamer)

    # Blocking call that keeps going until interrupted
    comms.connect_and_start(keep_alive_seconds=keep_alive_seconds)


if __name__ == "__main__":
    main()
