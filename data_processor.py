from api_connector import get_connected_users 
import datetime
from typing import Optional

def count_users(command_output: str) -> Optional[int]:
    """
    Counts and returns the total number of connected users.
    """
    if command_output is None:
        return None
    
    # Each "<entry>" in the returned XML represents one user
    return command_output.count('<entry>')

def process_firewall_data(firewall: dict) -> list:
    """
    Processes information for each firewall. Returns a list of records to insert into the DB.
    """ 
    db_records_list = []  

    now = datetime.datetime.now() 
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S') 
    
    name = firewall['name']
    host = firewall['host']
    api_key = firewall['api_key']
    gateways = firewall.get('gateway')
    
    # Ensure gateways is an iterable list to avoid code repetition
    if not isinstance(gateways, list):
        gateways = [None] if gateways is None else [gateways]

    for gateway in gateways:
        response = get_connected_users(host, api_key, gateway)
        if response is not None:
            current_users = count_users(response)
            status = "connected"
        else:
            current_users = None
            status = "disconnected"
        
        
        record_dict = {
            'firewall': name,
            'gateway': gateway,
            'users': current_users,
            'timestamp': timestamp,
            'status': status
        }
        db_records_list.append(record_dict)

    return db_records_list