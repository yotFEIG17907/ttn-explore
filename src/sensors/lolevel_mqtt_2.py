"""
TTN MQTT API Reference: https://www.thethingsnetwork.org/docs/applications/mqtt/api.html

This program uses Paho MQTT Client to make a SSL connection.  The source code for this client is here:
https://github.com/eclipse/paho.mqtt.python/blob/master/src/paho/

"""
import argparse
import configparser
import logging
import logging.config
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import models
from models.models import Base
from sensors.db_streamer import Streamer
from sensors.mqtt_comms import MqttComms

"""
Topic format <AppID>/devices/<DevID>/up
AppID is the name of the "Application" specified in the things network, which in this case is skybar-sensors
same as the username.
DevID is the friendly name of the device, as given in the Things Network device overview.
If <AppID> is + then it will subscribe to all users accessible with this user name.
If <DevID> is + then it will fetch all devices for the given application ID.
"""


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA Data Feed")
    parser.add_argument("-l", "--log-config", required=True, help="Path to logging configuration file")
    parser.add_argument("-i", "--ini-file", required=True,
                        help="Path to the INI file for configuration the application")
    parser.add_argument("-c", "--certs-file", required=True, help="Path to the MQTT trust store")
    parser.add_argument("-db", "--db-url", required=True, help="Database connection URL, e.g. sqlite:///:memory:")
    parser.add_argument("-v", "--verbose", required=False, help="SQL logging on or off, default is off",
                        type=str2bool,
                        default=False)
    args = parser.parse_args()
    return args


#
def main():
    args = parse_arguments()
    logging_configuration = args.log_config
    if not os.path.exists(logging_configuration):
        print("Path to logging configuration not found: ", logging_configuration)
        return

    log_folder = "target/logs"
    os.makedirs(log_folder, exist_ok=True)

    data_folder = "target/data"
    os.makedirs(data_folder, exist_ok=True)

    logging.config.fileConfig(logging_configuration, disable_existing_loggers=False)
    logger = logging.getLogger("lora.mqtt")

    mqtt_ca_path = args.certs_file
    ini_file_path = args.ini_file
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

    # Use an in-memory database to test
    # Set this true to see all the SQL
    sql_logging_on = args.verbose
    db_url = args.db_url
    logger.info(f"Database URL for the ORM {db_url}")
    engine = create_engine(db_url, echo=sql_logging_on)
    models.Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    streamer = Streamer(session_factory)

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
