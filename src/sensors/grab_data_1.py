"""
Experiment grabbing data from the temp sensors via TTN.
This script is from here: https://www.thethingsnetwork.org/docs/applications/python/
but the doc says the Python SDK has been discontinued and not to use it. But try it
until it stops working.

This script does two things: there is a MQTT client and an Application manager client.
With the MQTT client it starts and runs in the background, when messages arrive
they are provided to the callback. Since the sensors are programmed to report temperate
only every 15 minutes or so waiting 60 seconds is not good, but the sensor can be forced
to send a message using the magnet.

The other client is to the application manager which can do everything the Application Manager can do.

Access is complex; the access key is generated on the TTN site; at first I used the default key but
got Permission Denied when trying to get the devices; turned out this was because the default key is only
good for messages. After making a new access key and checking the boxes for settings, messages AND devices
it worked and I got a list of all (three that I have) devices. Going through this Python ttn package
simplifies all the access stuff. It is perhaps a good way to get started, but ultimately I want to
make a lower-level MQTT client and navigate the access and get tokens and all so it can get the data
directly from the MQTT broker.
"""
import time

import ttn


def main():
    app_id = "skybar-sensors"
    access_key = "ttn-account-v2.92MjVAmyy6BeREmwjiQDOZ51TEGfC-JayoaCjlAtPqc"

    def uplink_callback(msg, client):
        print("Received uplink from ", msg.dev_id)
        print(msg)

    print("Making the TTN handler")
    handler = ttn.HandlerClient(app_id, access_key)

    print("Get data using mqtt client")
    # using mqtt client
    mqtt_client = handler.data()
    mqtt_client.set_uplink_callback(uplink_callback)
    print("Connecting....")
    mqtt_client.connect()
    WAIT_SECONDS = 20
    print(f"Now wait for {WAIT_SECONDS} seconds after connect")
    time.sleep(WAIT_SECONDS)
    print("Close the client")
    mqtt_client.close()

    # using application manager client
    print("Get data using application manager client")
    app_client = handler.application()
    print("Got client, now get the application")
    my_app = app_client.get()
    print(my_app)
    print("Now get a list of my devices")
    my_devices = app_client.devices()
    print(my_devices)


if __name__ == "__main__":
    main()
