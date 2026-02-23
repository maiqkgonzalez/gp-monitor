import yaml

def leer_config():
    """Lee el archivo config.yaml y retorna el diccionario completo"""
    with open('config.yaml', 'r') as file:
        config_file = yaml.safe_load(file)
        return config_file

def obtener_firewalls():
    """Retorna solo la lista de firewalls del config"""
    config = leer_config()  # Reutiliza la función
    return config['firewalls']

if __name__ == "__main__":
    firewalls = obtener_firewalls()
    print("=== Firewalls configurados ===")
    
    # Bucle for para iterar la lista de firewalls
    for firewall in firewalls:
        # Imprimir las llaves 'name' y 'host'
        print(f"Nombre: {firewall['name']} | Host: {firewall['host']}")
        
        # Como gateway contiene una lista, iteramos sobre cada gateway
        for gateway in firewall['gateway']:
            print(f"  Gateway: {gateway}")
        print("---------------------------")
    
    # Se imprime UNA vez al final (fuera del for)
    print(f"\nTotal de firewalls: {len(firewalls)}")