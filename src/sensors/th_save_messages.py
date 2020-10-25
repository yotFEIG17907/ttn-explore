"""
This pulls events from the database, and writes the wrong messages to a file for
subsequent use in testing.
"""
import argparse
import configparser
import logging
import logging.config
import os
from pathlib import Path
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, Sensor, TempHumidityMeasurement, Supervisory


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
    parser.add_argument("-db", "--db-url", required=True, help="Database connection URL, e.g. sqlite:///:memory:")
    parser.add_argument("-o", "--output-file", required=True, help="Raw messages will be written to this file")
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

    logging.config.fileConfig(logging_configuration, disable_existing_loggers=False)
    logger = logging.getLogger("event.validator")

    out_file_path = Path(args.output_file)
    os.makedirs(out_file_path.parent, exist_ok=True)
    logger.info(f"Messages will be written to {out_file_path}")

    ini_file_path = args.ini_file
    # The configuration file path will become a command-line argument
    config = configparser.ConfigParser()
    config.read(ini_file_path)

    # Set this true to see all the SQL
    sql_logging_on = args.verbose
    db_url = args.db_url
    logger.info(f"Database URL for the ORM {db_url}")
    engine = create_engine(db_url, echo=sql_logging_on)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    # Single-threaded batch operation
    # Need to look at both Temperature and Supervisory messages
    session = session_factory()
    try:
        with open(out_file_path, "w") as writer:
            measurements = session.query(TempHumidityMeasurement).\
                order_by(TempHumidityMeasurement.counter).all() # type: List[TempHumidityMeasurement]
            messages = [x.raw_message.decode("utf-8") + '\n' for x in measurements]
            writer.writelines(messages)
            supervisory = session.query(Supervisory).order_by(Supervisory.counter).all()
            s_messages = [x.raw_message.decode("utf-8") + '\n' for x in supervisory]
            writer.writelines(s_messages)

    finally:
        session.close()


if __name__ == "__main__":
    main()
