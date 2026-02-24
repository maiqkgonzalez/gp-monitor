import time
from config_reader import obtener_firewalls
from data_processor import procesar_firewall
from database import insertar_registros_batch
from datetime import datetime
from pathlib import Path
import logging

def ejecutar_ciclo(ciclos):
    '''
    Ejecuta cada ciclo completo. Lee el archivo config.yaml, consulta cada firewall con el API, procesa los datos y los inserta en la BD.

    Parameters:
    ciclos (int): Contador de cada vez que se ejecuta un ciclo.
    '''

    logging.info(f"Ciclo {ciclos}")

    #Obtener la lista con los diccionarios de firewalls del archivo config.yaml
    firewalls = obtener_firewalls()
    
    #Loop para iterar la lista
    for firewall in firewalls:
            try:
                #Procesar cada firewall para obtener los registros
                registros = procesar_firewall(firewall) 
            
                #Insertar en la base de datos
                insertar_registros_batch(registros)

                #Imprimir resumen
                for registro in registros:
                    if registro['status'] == "connected":
                        logging.info(f"✅ {registro['firewall']} [{registro['gateway']}]: {registro['num_usuarios']} usuarios")
                        ciclos += 1
                    elif registro['status'] == "disconnected":
                        logging.info(f"❌ {registro['firewall']} [{registro['gateway']}] desconectado")
                        ciclos += 1
            except Exception as e:
                logging.error(f"Error en {firewall['name']}: {e}")
    logging.info(f"{ciclos} registros guardados en la BD")


def main():
    '''Funcion pricipal que mantiene el script ejecutandose'''

    #Setup del loggin
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('gp_monitor.log'),
            logging.StreamHandler()
        ]
    )

    intervalo = 5

    #Logs de arranque
    logging.info("======= GlobalProtect Monitor Iniciado =======")
    logging.info(f"==== Intervalo de recoleccion: {intervalo} minutos ====")
    logging.info("Presiona Ctrl+C para detener....\n")
    
    #Bloque que valida que exista el config.yaml
    archivo = Path('config.yaml')

    if archivo.exists():
        logging.info("✔️ Archivo config.yaml encontrado\n")
        ciclos = 0

        while True:
            ciclos += 1
            ejecutar_ciclo(ciclos)
            time.sleep(intervalo * 60)
    else:
        logging.error("No se encontro el archivo config.yaml")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\n=== Monitor Detenido ===")