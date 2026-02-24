import requests
import urllib3
from config_reader import obtener_firewalls
from typing import Optional
import logging

#Deshabilitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_usuarios(host, api_key, gateway=None) -> Optional[str]:
    '''Por medio del API obtiene la lista completa de usuarios. (ejecuta el comando show global protect current user)'''
    try:
        url = f"https://{host}/api/" # URL basica para entrar al API del firewall

        #Parametros
        parametros =  {
        'type': 'op',
        'key': api_key
         }

        #If para identificar si hay gateway.
        if gateway:
            #Si existe gateway aplicara el comando especificando el gateway
            parametros['cmd'] = f'<show><global-protect-gateway><current-user><gateway>{gateway}</gateway></current-user></global-protect-gateway></show>'
        else:
            #Si no existe gateway aplicara el comando general
            parametros['cmd'] = '<show><global-protect-gateway><current-user></current-user></global-protect-gateway></show>'

        response = requests.get(url, params=parametros,verify=False,timeout=5)
        response.raise_for_status() #Excepcion para bad status codes (4XX-5XX)
        return response.text # Regresa la respuesta en texto 'crudo'
    
    #Manejo de errores
    except requests.exceptions.HTTPError as e:
        #Errores especificos de HTTP
        logging.error(f"HTTP error en {host}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexion en {host}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado en {host}: {e}")
        return None