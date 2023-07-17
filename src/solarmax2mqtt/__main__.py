import argparse
import logging

from solarmax_query.constants import SolarMaxQueryKey
from .agent import SolarMaxMQTTAgent

DEFAULT_QUERY_KEYS = [
    "status",
    "alarm_code",
    "ac_output",
    "operating_hours",
    "energy_year",
    "energy_month",
    "energy_day",
    "energy_total",
    "relative_output",
    "voltage_dc",
    "voltage_phase_one",
    "current_dc",
    "current_phase_one",
    "temperature_power_unit_one",
    "mains_frequency",
]


def parse_key(s: str) -> SolarMaxQueryKey:
    try:
        return SolarMaxQueryKey[s.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"{s!r} is not a valid SolarMax data key.") from None


def main():
    arg_parser = argparse.ArgumentParser(
        prog="python -m solarmax_query.mqtt",
        description="Queries a SolarMax inverter and publishes the data via MQTT.",
    )
    arg_parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "CRITICAL", "ERROR", "FATAL", "INFO", "WARN", "WARNING"],
        default="INFO",
    )
    arg_parser.add_argument(
        "-i",
        "--inverter-host",
        required=True,
        help="IP or hostname of the inverter to query.",
    )
    arg_parser.add_argument(
        "--inverter-port",
        type=int,
        default=12345,
        help="The TCP port number of the inverter.",
    )
    arg_parser.add_argument(
        "--inverter-index",
        type=int,
        default=1,
        help="The device address/index configured in the inverter.",
    )

    arg_parser.add_argument(
        "--query",
        action="append",
        choices=[k.name.lower() for k in SolarMaxQueryKey],
        help="The data keys to query and publish from the inverter. "
        "Can be specified multiple times to query more than one value. "
        "If not present, a default set of values is queried.",
    )

    arg_parser.add_argument("-b", "--mqtt-broker", default="localhost", help="IP or host of the MQTT broker")
    arg_parser.add_argument("--mqtt-broker-port", type=int, default=1883, help="TCP port number of the MQTT broker.")

    arg_parser.add_argument(
        "-t", "--mqtt-topic", default="inverter/solarmax", help="The MQTT topic the inverter data is published on."
    )

    args = arg_parser.parse_args()

    keys = args.query if args.query else DEFAULT_QUERY_KEYS
    keys = [SolarMaxQueryKey[key.strip().upper()] for key in keys]

    num_log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] %(name)-20s - %(message)s",
        level=num_log_level,
    )
    agent = SolarMaxMQTTAgent(
        inverter_keys=keys,
        inverter_host=args.inverter_host,
        inverter_index=args.inverter_index,
        inverter_port=args.inverter_port,
        mqtt_broker_host=args.mqtt_broker,
        mqtt_broker_port=args.mqtt_broker_port,
        # mqtt_broker_auth: tuple[str, str] | None = None,
        mqtt_topic=args.mqtt_topic,
    )

    agent.run()


if __name__ == "__main__":
    main()
