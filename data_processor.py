from api_connector import obtener_usuarios 
import datetime
from config_reader import obtener_firewalls

def contar_usuarios(output_comando):
    '''
    Cuenta y regresa el total de usuarios conectados.

    Parameters:
    output_comando (str): output que regresa la funcion obtener_usuarios.

    Return:
    int: current_user
    '''

    if output_comando is None:
        return None

    else:
        current_user = output_comando.count('<entry>') # Cada "<entry> en el XML que regresa el comando es un usuario"
        return current_user

def procesar_firewall(firewall):
    '''
    Procesa la informacion de cada firewall del archivo config.yaml. Regresa una lista con los registros para insertar en la BD.

    Parameters:
    firewall (list): lista de cada firewall del archivo config.yaml

    Return:
    list:Regresa una lista con los registros para insertar en la BD.
    ''' 
    lista_registros_db = []  # Lista vacia que se llenara despues con los diccionarios de firewalls

    #Bloque para generar el timestamp
    ahora = datetime.datetime.now() 
    tiempo = ahora.strftime('%Y-%m-%d %H:%M:%S') # Convertir a string
    
    #Variables para cada diccionario de firewalls
    nombre = firewall['name']
    host = firewall['host']
    api_key = firewall['api_key']
    gateways = firewall.get('gateway')
    
    #Bloque para diferenciar si tiene gateway o no (es una lista)
    if isinstance(gateways, list):
        for gateway in gateways:
            respuesta = obtener_usuarios(host, api_key, gateway)
            curren_users = contar_usuarios(respuesta)
            if curren_users is None:
                #Llenado del diccionario
                diccionario_registros_db = {
                    'firewall': nombre,
                    'gateway': gateway,
                    'num_usuarios': None,
                    'timestamp': tiempo,
                    'status': "disconnected"
                }
                lista_registros_db.append(diccionario) # Agregar el diccionario a la lista vacia
            else:
                #Llenado del diccionario
                diccionario = {
                    'firewall': nombre,
                    'gateway': gateway,
                    'num_usuarios': curren_users,
                    'timestamp': tiempo,
                    'status': "connected"
                }
                lista_registros_db.append(diccionario) # Agregar el diccionario a la lista vacia

    else:
        respuesta = obtener_usuarios(host, api_key)
        curren_users = contar_usuarios(respuesta)
        if curren_users is None: # Comprobar si current_users es None
            #Llenado del diccionario
            diccionario = {
                'firewall': nombre,
                'gateway': None,
                'num_usuarios': None,
                'timestamp': tiempo,
                'status': "disconnected"
                }
            lista.append(diccionario) # Agregar el diccionario a la lista vacia
        else:
            #Llenado del diccionario
            diccionario = {
                'firewall': nombre,
                'gateway': None,
                'num_usuarios': curren_users,
                'timestamp': tiempo,
                'status': "connected"
            }
            lista.append(diccionario) # Agregar el diccionario a la lista vacia
    return lista