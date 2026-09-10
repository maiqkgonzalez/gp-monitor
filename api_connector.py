import requests
import urllib3
from typing import Optional
import logging

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_connected_users(
    host: str, api_key: str, gateway: Optional[str] = None
) -> Optional[str]:
    """
    Fetches the complete list of users via API (executes 'show global protect current user').
    """
    try:
        url = f"https://{host}/api/"

        params = {"type": "op", "key": api_key}
        # SECURITY: never log `params` or `response.url` — they contain the API key.

        if gateway:
            params["cmd"] = (
                f"<show><global-protect-gateway><current-user><gateway>{gateway}</gateway></current-user></global-protect-gateway></show>"
            )
        else:
            params["cmd"] = (
                "<show><global-protect-gateway><current-user></current-user></global-protect-gateway></show>"
            )

        response = requests.get(url, params=params, verify=False, timeout=5)
        response.raise_for_status()
        return response.text

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error on {host}: {e.response.status_code} {e.response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error on {host}: {type(e).__name__}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error on {host}: {type(e).__name__}")
        return None
