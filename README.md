# ttn-explore
Exploring applications to use with my LoRA temp/humidity sensors.
Main language is Python 3.7

# Running it
As of time of writing the program has been run only within the PyCharm IDE. Run it like this:

`PycharmProjects/ttn/src/sensors/lolevel_mqtt_2.py --db-url sqlite:///./target/data/lora.mqtt.db -l ../../public-config/logging.config -i ../../config/temp-sensors.ini -c ../../certs/mqtt-ca.pem`

| Argument | Required? | Description |
| ---------|-------------|-----------|
| -l/--log-config | Yes | Path to the logging configuration file |
| -i/--ini-file | Yes | Path to an INI configuration file, see below |
| -c/--certs-file | Yes | Path to the MQTT client trust store, needed because connecting using SSL |
| -db/--db-url | Yes | The Database URL, this can be any database supported by SQLAlchemy, e.g. SQLite.|
| -v/--verbose | No | Default is false. If true then logging of SQL statements executed by SQLAlchemy is turned on |

## INI File ##

```
[DEFAULT]
# None so far

[ttn-explore.mqtt.connection]
# The parameters for the MQTT Connection
# This is the Application ID for this integration at TTN
username = Your-application-ID
# This is the my-python-client application access key
password = ttn-account-v2.Put-your-access-key-here
# The tail end of the handler name (ttn-handler-us-west)
region = us-west
# The mqtt SSL Port Number
sslport = 8883
# Keep Alive messages sent with maximum interval
keep_alive_seconds = 300
```
| Key | Description |
| ----|-------------|
| username | This is the username to use for the MQTT connection. This is in fact not your TTN username, it is the Application ID of the applicaion you created in TTN to grab the data that is captured by the gateway and forwarded to TTN |
| password | The password for the MQTT connection. This is the application access key, get it from the page for your application; you can make multiple access keys, you make a special one for this purpose |
| region | The tail end of the handler for your TTN application. The MQTT URL is created using this format string f"{region}.thethings.network"|
| sslport | The port number of the MQTT server |
| keep_alive_seconds | Maximum time to go without any messages; if nothing is sent for this number of seconds then a ping message will be sent to keep the connection alive. |

# Logging output
Logging is handled as defined by the logging configuration file. For my configuration file logs are written to `target/logs` under the `src/sensors` folder

# Data Output
Messages, errors and status are written to a SQLite database here: `src/sensors/target/data/lora.mqtt.db`
But of course, it depends on what the DB URL says. A new empty database with schema is created per the URL if it doesn't exist.
