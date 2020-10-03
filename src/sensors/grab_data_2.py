"""
Experiment grabbing data from the temp sensors via TTN.
This script is from here: https://www.thethingsnetwork.org/docs/applications/python/
but the doc says the Python SDK has been discontinued and not to use it. But try it
until it stops working.

This just does the mqtt client, it could use the default access key. It just waits
for messages to arrive. The payload is converted by the raw payload converter that runs
in TTN. The messages should arrive every 30 minutes or so, depending on how I set
up the sensors; i.e. the period they are programmed to report at.

Useful links:
https://www.hivemq.com/blog/mqtt-essentials-part-10-alive-client-take-over/

"""
import configparser
import time

import ttn
from ttn import MQTTClient


def main():
    ini_file_path = "../../config/temp-sensors.ini"
    # The configuration file path will become a command-line argument
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    connection = config['ttn-explore.mqtt.connection']
    app_id = connection['username']  # This is the Application ID for this integration at TTN
    access_key = connection['password']  # This is the my-python-client application access key

    def uplink_callback(msg, client):
        print("Received uplink from ", msg.dev_id)
        print(msg)

    print("Making the TTN handler")
    handler = ttn.HandlerClient(app_id, access_key)

    print("Get data using mqtt client")
    # using mqtt client
    mqtt_client = handler.data()  # type: MQTTClient
    mqtt_client.set_uplink_callback(uplink_callback)
    print("Connecting....")
    mqtt_client.connect()
    wait_seconds = 60 * 60 * 24
    print(f"Now wait for {wait_seconds} seconds after connect")
    time.sleep(wait_seconds)
    print("Close the client")
    mqtt_client.close()


if __name__ == "__main__":
    main()
