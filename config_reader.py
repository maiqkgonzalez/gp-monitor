import yaml

def leer_config():
    """Lee el archivo config.yaml y retorna el diccionario completo"""
    with open('config.yaml', 'r') as file:
        config_file = yaml.safe_load(file)
        return config_file

def obtener_firewalls():
    """Retorna la lista de diccionarios de firewalls del config.yaml"""
    config = leer_config()  
    return config['firewalls']