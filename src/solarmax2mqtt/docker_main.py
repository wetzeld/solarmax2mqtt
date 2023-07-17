import logging
import os

from solarmax_query.constants import SolarMaxQueryKey
from .agent import SolarMaxMQTTAgent

DEFAULT_INVERTER_KEYS = (
    "status, alarm_code, ac_output, operating_hours, energy_year, energy_month, energy_day, energy_total, "
    "relative_output, voltage_dc, voltage_phase_one, current_dc, current_phase_one, temperature_power_unit_one, "
    "mains_frequency"
)


def get_inverter_keys() -> list[SolarMaxQueryKey]:
    keys = os.environ.get("INVERTER_KEYS", DEFAULT_INVERTER_KEYS)
    return [SolarMaxQueryKey[key.strip().upper()] for key in keys.split(",")]


kwargs = {
    "inverter_host": os.environ["INVERTER_HOST"],
    "inverter_keys": get_inverter_keys(),
}

if "INVERTER_PORT" in os.environ:
    kwargs["inverter_port"] = int(os.environ["INVERTER_PORT"])
if "INVERTER_INDEX" in os.environ:
    kwargs["inverter_index"] = int(os.environ["INVERTER_INDEX"])

if "MQTT_BROKER_HOST" in os.environ:
    kwargs["mqtt_broker_host"] = os.environ["MQTT_BROKER_HOST"]
if "MQTT_BROKER_PORT" in os.environ:
    kwargs["mqtt_broker_port"] = int(os.environ["MQTT_BROKER_PORT"])
if "MQTT_BROKER_USER" in os.environ and "MQTT_BROKER_PASSWORD" in os.environ:
    kwargs["mqtt_broker_auth"] = (
        os.environ["MQTT_BROKER_USER"],
        os.environ["MQTT_BROKER_PASSWORD"],
    )

if "MQTT_TOPIC" in os.environ:
    kwargs["mqtt_topic"] = os.environ["MQTT_TOPIC"]

num_log_level = getattr(logging, os.environ.get("LOG_LEVEL", "INFO"))
logging.basicConfig(
    format="%(asctime)s [%(levelname)-8s] %(name)-20s - %(message)s",
    level=num_log_level,
)

agent = SolarMaxMQTTAgent(**kwargs)
agent.run()
