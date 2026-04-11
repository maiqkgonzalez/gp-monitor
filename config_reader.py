import yaml
import logging
from typing import List


def read_config() -> dict:
    """Reads the config.yaml file and returns the full dictionary."""
    try:
        with open("config.yaml", "r") as file:
            return yaml.safe_load(file)

    except FileNotFoundError:
        logging.error(f"Configuration file not found")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML: {e}")
        raise


def get_firewalls(config: dict) -> List[dict]:
    """Returns the list with dictionary of firewall dictionaries from config.yaml."""
    firewalls_config = config

    if firewalls_config is None:
        raise ValueError("Config file is empty")

    try:
        firewalls = firewalls_config["firewalls"]

        if not isinstance(firewalls, list) or len(firewalls) == 0:
            raise ValueError("No firewalls defined in config")
        return firewalls

    except KeyError:
        logging.error("The key 'firewalls' was not found in the YAML file..")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise


def get_interval(config: dict) -> int:
    """Return the interval time for each monitor cycle. If was not found on config.yaml returns 5 by default"""
    interval_config = config.get("interval", 5)

    try:
        interval = int(interval_config)

        if interval <= 0:
            logging.warning("Invalid interval value. Seted to 5 minutes by default")
            return 5

        return interval

    except (ValueError, TypeError):
        logging.warning("Invalid interval value. Seted to 5 minutes by default")
        return 5
