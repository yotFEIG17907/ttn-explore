"""
This pulls events from the database, sorts them by device id and counter and then looks for gaps
the sequence which could indicate missing messages. Not working, this finds small gaps periodically
which are due to the Supervisory messages.

"""
import argparse
import configparser
import logging
import logging.config
import os
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, Sensor, LoraEvent, ConnectionEvent
from utils.date_time_utils import formatiso8601


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
        all_sensors = session.query(Sensor).all()
        for sensor in all_sensors:
            logger.info(sensor)
            all_th_events = sensor.events.order_by(
                LoraEvent.counter).all()  # type: List[LoraEvent]
            logger.info(f"  There are {len(all_th_events)} events")
            logger.info(f"  Lowest Counter {all_th_events[0].counter} Latest Counter {all_th_events[-1].counter}")
            logger.info(f"  First time {formatiso8601(all_th_events[0].timestamp)}" \
                        f"  Last time {formatiso8601(all_th_events[-1].timestamp)}")
            # Look for gaps
            mru_event = all_th_events[0]
            start_good_run = mru_event
            for event in all_th_events:
                if event.counter > mru_event.counter + 1:
                    gap = event.counter - mru_event.counter
                    good_run = mru_event.counter - start_good_run.counter
                    logger.warning(
                        f"Gap {gap} > 1 Run before this gap {good_run}, "\
                        f"{mru_event.counter} / {formatiso8601(mru_event.timestamp)}" \
                        f" {event.counter} / {formatiso8601(event.timestamp)}")
                    start_good_run = event
                mru_event = event
        all_connection_events = session.query(ConnectionEvent).all()
    #    for con_event in all_connection_events:
    #        logger.info(con_event)

    finally:
        session.close()


if __name__ == "__main__":
    main()
