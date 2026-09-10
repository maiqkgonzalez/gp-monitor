import os
import yaml
import logging
from typing import List
from dotenv import load_dotenv


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
    """Returns the list of firewall dicts with api_key resolved from .env.

    config.yaml must define `api_key_env` (env var name) per firewall.
    Secrets are never stored in YAML, only referenced. Values are loaded
    from `.env` / process environment via python-dotenv.
    """
    
    firewalls_config = config

    if firewalls_config is None:
        raise ValueError("Config file is empty")

    try:
        firewalls = firewalls_config["firewalls"]

        if not isinstance(firewalls, list) or len(firewalls) == 0:
            raise ValueError("No firewalls defined in config")
    except KeyError:
        logging.error("The key 'firewalls' was not found in the YAML file..")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    # Load secrets from .env (no-op if file is missing; systemd can
    # provide them via EnvironmentFile instead).
    load_dotenv()

    for firewall in firewalls:
        name = firewall.get("name", "<unnamed>")
        env_var = firewall.get("api_key_env")

        if not env_var:
            raise ValueError(
                f"Firewall '{name}' is missing required key 'api_key_env' in config.yaml"
            )

        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(
                f"Missing env var {env_var} for firewall '{name}'. "
                f"Define it in .env (see .env.example)."
            )

        # Inject resolved secret in memory only; never write back to YAML.
        firewall["api_key"] = api_key

    return firewalls


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
