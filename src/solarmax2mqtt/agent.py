import json
import logging
import time
from typing import Any

import paho.mqtt.client as mqtt

from solarmax_query import SolarMax
from solarmax_query.constants import SolarMaxQueryKey

LOGGER = logging.getLogger("SolarMaxMQTTAgent")


class SolarMaxMQTTAgent:
    def __init__(
        self,
        inverter_keys: list[SolarMaxQueryKey] | list[str],
        inverter_host: str,
        inverter_port: int = 12345,
        inverter_index: int = 1,
        mqtt_broker_host: str = "localhost",
        mqtt_broker_port: int = 1883,
        mqtt_broker_auth: tuple[str, str] | None = None,
        mqtt_topic: str = "inverter/solarmax",
    ):
        self.inverter_keys = inverter_keys
        self.solarmax = SolarMax(
            host=inverter_host, port=inverter_port, inverter_index=inverter_index
        )
        self.mqtt_broker_host = mqtt_broker_host
        self.mqtt_broker_port = mqtt_broker_port
        self.mqtt_topic = mqtt_topic

        self.client = mqtt.Client(client_id=f"SolarMax[{inverter_host}]")
        if mqtt_broker_auth is not None:
            self.client.username_pw_set(
                username=mqtt_broker_auth[0], password=mqtt_broker_auth[1]
            )
        self.client.enable_logger()

    def convert_key(self, key: str):
        try:
            return SolarMaxQueryKey(key).name.lower()
        except ValueError:
            return key

    def convert_keys(self, inverter_data: dict[str, Any]):
        result = {}
        for key, value in inverter_data.items():
            result[self.convert_key(key)] = value
        return result

    def run(self):
        # todo: handle disconnects / reconnects to inverter

        LOGGER.info(
            "Connecting to MQTT broker %s:%i...",
            self.mqtt_broker_host,
            self.mqtt_broker_port,
        )
        self.client.loop_start()
        self.client.connect(self.mqtt_broker_host, self.mqtt_broker_port)

        try:
            while True:
                data = self.convert_keys(self.solarmax.query(self.inverter_keys))
                LOGGER.info(data)

                publish_result = self.client.publish(self.mqtt_topic, json.dumps(data))
                if publish_result.rc != mqtt.MQTT_ERR_SUCCESS:
                    LOGGER.warning(
                        "Failed to publish message to MQTT broker! "
                        "Connected: %i, Error %i",
                        self.client.is_connected(),
                        publish_result.rc,
                    )

                time.sleep(5)

        except KeyboardInterrupt:
            LOGGER.info("Shutting down.")
            pass

        self.client.disconnect()
        self.client.loop_stop()
