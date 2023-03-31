import json
import os

from dotenv import load_dotenv
from producer import KafkaProducer
from configuration import get_config
import logging
from configparser import ConfigParser

import numpy as np
import cv2
from Lepton3 import Lepton

load_dotenv()

logger = logging.getLogger(__name__)

SERVICE_BASE_DIR = os.path.dirname(__file__)

environment = os.getenv("ENVIRONMENT")
logger.info(f"Setting up Inertial Sensor service for environment [{environment}]")
configuration = get_config(environment)

confluent_properties_file = open("kafka_cl[ient_properties.ini")
confluent_config_parser = ConfigParser()
confluent_config_parser.read_file(confluent_properties_file)
confluent_config = dict(confluent_config_parser['default'])


class IRSensorService:
    def __init__(self):
        self.formatted_data = []
        self.producer = KafkaProducer(confluent_config, configuration.get_kafka_ir_sensor_topic())

    def start_server(self):
        with Lepton() as l:
            a, _ = l.capture()
            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(a, 8, a)
            self.send(np.uint8(a))  # send to kafka

    def send(self, thermal_value):
        logger.info(f"Producing message to Kafka topic: {configuration.get_kafka_ir_sensor_topic()}")
        print(f"Producing message to Kafka topic: {configuration.get_kafka_ir_sensor_topic()}")

        sample = {
            "type": "calibration",
            "data": {
                "session": "978df625-0734-49e3-a84b-b684844a6907", # test session ID
                "thermal": thermal_value
            }
        }
        self.producer.produce(json.dumps(sample))

    def send_loop_sample(self):
        while True:
            self.send(38)


if __name__ == '__main__':
    ir_service = IRSensorService()
    ir_service.start_server()
