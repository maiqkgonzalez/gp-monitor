import yaml

def read_config() -> dict:
    """Reads the config.yaml file and returns the full dictionary."""
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def get_firewalls() -> list:
    """Returns the list of firewall dictionaries from config.yaml."""
    config = read_config()  
    return config['firewalls']