"""
Visualize the temperature data
"""
import argparse
import configparser
import logging
import logging.config
import os
from collections import defaultdict
from time import sleep

import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from models.models import Base, Sensor


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


def query_to_list(rset):
    """List of result
    Return: columns name, list of result
    """
    result = []
    for obj in rset:
        instance = inspect(obj)
        items = instance.attrs.items()
        result.append([x.value for _,x in items])
    return instance.attrs.keys(), result

def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result


#
def main():
    args = parse_arguments()
    logging_configuration = args.log_config
    if not os.path.exists(logging_configuration):
        print("Path to logging configuration not found: ", logging_configuration)
        return

    log_folder = "target/viz-logs"
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
        plt.figure()
        all_sensors = session.query(Sensor).all()
        for sensor in all_sensors:
            logger.info(sensor)
            names, data = query_to_list(sensor.measurements.all())
            df2 = pd.DataFrame.from_records(data, columns=names)
            x = df2['timestamp']
            y1 = df2['temp_c']
            plt.plot(x,y1,label=f"{sensor.device_name} ({sensor.device_id})")
        # Need to call plt.show() to cause the plots to display
        # In PyCharm a window will open to show them
        plt.xlabel('Date/Time')
        plt.ylabel('Temp Deg C')
        plt.xticks(rotation=90)
        plt.legend()
        plt.show()
    finally:
        session.close()


if __name__ == "__main__":
    main()
