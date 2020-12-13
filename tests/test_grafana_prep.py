import json
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, TempHumidityMeasurement, Sensor, LoraEvent, ConnectEnum, ConnectionEvent
from sensors.db_streamer import Streamer
from tests.testdata import test_mixed_msgs
from utils.date_time_utils import get_utc_now


def test_make_grafana_json_datasource():
    # Use an in-memory database to test
    # Set this true to see all the SQL
    sql_logging_on = False
    engine = create_engine('sqlite:///:memory:', echo=sql_logging_on)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)
    timenow = get_utc_now()
    device_id = "xkksjdfsf"
    device_name = "My Test Device in the room"
    payload_bytes = str.encode(f"{device_id} {device_name}")

    sensor = Sensor(device_id=device_id, device_name=device_name)
    try:
        counter = 0
        for temp_c in [x / 10.0 for x in range(150, 300, 5)]:
            for humidity_percent in range(10, 40, 10):
                measurement = TempHumidityMeasurement(sensor=sensor,
                                                      counter=counter,
                                                      raw_message=payload_bytes,
                                                      temp_c=temp_c,
                                                      humidity_percent=humidity_percent,
                                                      timestamp=timenow)
                session.add(measurement)
                counter += 1
        session.commit()

        all_sensors = session.query(Sensor).all()
        for sensor in all_sensors:
            events = sensor.measurements.order_by(LoraEvent.counter).all()
            t_events = list(map(lambda x : [x.temp_c, int(x.timestamp.timestamp() * 1000.0)], events))
            h_events = list(map(lambda x : [x.humidity, int(x.timestamp.timestamp() * 1000.0)], events))
            data = [
                { "target": "temp",
                  "datapoints": t_events
                },
                {"target": "humidity",
                 "datapoints": h_events
                 }
            ]
            print()
            print(type(data))
            print(json.dumps(data))

    finally:
        session.close()
