import time
from config_reader import obtener_firewalls
from data_processor import procesar_firewall
from database import insertar_registros_batch
from datetime import datetime
from pathlib import Path
import logging

def ejecutar_ciclo(ciclos):
    #Bloque para el tiempo y ciclos
    #tiempo_actual = datetime.now().strftime('%H:%M:%S')
    logging.info(f"Ciclo {ciclos}")

    #Obtener la lista con los diccionarios de firewalls
    firewalls = obtener_firewalls()
    conteo_registros = 0

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
                        conteo_registros += 1
                    elif registro['status'] == "disconnected":
                        logging.info(f"❌ {registro['firewall']} [{registro['gateway']}] desconectado")
                        conteo_registros += 1
            except Exception as e:
                logging.error(f"Error en {firewall['name']}: {e}")
    logging.info(f"{conteo_registros} registros guardados en la BD")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('gp_monitor.log'),
            logging.StreamHandler()
        ]
    )

    intervalo = 5
    logging.info("======= GlobalProtect Monitor Iniciado =======")
    logging.info(f"==== Intervalo de recoleccion: {intervalo} minutos ====")
    logging.info("Presiona Ctrl+C para detener....\n")
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