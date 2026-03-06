import time
from config_reader import get_firewalls, get_interval, read_config
from data_processor import process_firewall_data
from database import insert_batch_records
import logging


def run_monitor_cycle(cycle_count: int, list_firewalls: list):
    """
    Executes a complete monitoring cycle: queries APIs, processes data, and inserts into DB.
    """
    logging.info(f"Cycle {cycle_count}")
    firewalls = list_firewalls

    for firewall in firewalls:
        try:
            records = process_firewall_data(firewall)
            insert_batch_records(records)

            for record in records:
                if record["status"] == "connected":
                    logging.info(
                        f"✅ {record['firewall']} [{record['gateway']}]: {record['users']} users"
                    )
                elif record["status"] == "disconnected":
                    logging.info(
                        f"❌ {record['firewall']} [{record['gateway']}] disconnected"
                    )

        except Exception as e:
            logging.error(f"Error processing {firewall['name']}: {e}")


def main():
    """Main function that keeps the script running."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("gp_monitor.log"), logging.StreamHandler()],
    )
    config = read_config()
    interval_minutes = get_interval(config)

    logging.info("======= GlobalProtect Monitor Started =======")
    logging.info(f"==== Collection interval: {interval_minutes} minutes ====")
    logging.info("Press Ctrl+C to stop....")

    firewalls = get_firewalls(config)
    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            run_monitor_cycle(cycle_count, firewalls)
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        logging.info("=== Monitor Stopped ===")


if __name__ == "__main__":
    main()
