import time
from config_reader import obtener_firewalls
from data_processor import procesar_firewall
from database import insertar_registros_batch
from datetime import datetime
from pathlib import Path

def ejecutar_ciclo(ciclos):
    #Bloque para el tiempo y ciclos
    tiempo_actual = datetime.now().strftime('%H:%M:%S')
    print(f"[{tiempo_actual}] Ciclo {ciclos}")

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
                        print(f"  ✅ {registro['firewall']} [{registro['gateway']}]: {registro['num_usuarios']} usuarios")
                        conteo_registros += 1
                    elif registro['status'] == "disconnected":
                        print(f"  ❌ {registro['firewall']} [{registro['gateway']}] desconectado")
                        conteo_registros += 1
            except Exception as e:
                print(f"Error en {firewall['name']}: {e}")
    print(f"{conteo_registros} registros guardados en la BD")


def main():
    intervalo = 5
    print("======= GlobalProtect Monitor Iniciado =======")
    print(f"==== Intervalo de recoleccion: {intervalo} minutos ====")
    print("Presiona Ctrl+C para detener....\n")
    archivo = Path('config.yaml')

    if archivo.exists():
        print("✔️ Archivo config.yaml encontrado\n")
        ciclos = 0

        while True:
            ciclos += 1
            ejecutar_ciclo(ciclos)
            time.sleep(intervalo * 60)
    else:
        print("No se encontro el archivo config.yaml")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n=== Monitor Detenido ===")