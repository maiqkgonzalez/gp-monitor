import sqlite3
import logging

def crear_tabla():
    '''Crea tabla registros'''
    with sqlite3.connect("usuarios_gp.db") as connection:
        cursor = connection.cursor()
        
        #Crear tabla
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            num_usuarios INTEGER,
            firewall TEXT NOT NULL,
            gateway TEXT,
            status TEXT NOT NULL
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()

def insertar_registro(firewall, gateway, num_usuarios, timestamp, status):
    '''
    Inserta el registro de cada firewall en la BD.
    '''
    try:
        with sqlite3.connect("usuarios_gp.db") as connection:
            cursor = connection.cursor()

            insert_query = '''
            INSERT INTO registros (firewall, gateway, num_usuarios, timestamp, status)
            VALUES (?, ?, ?, ?, ?);
            '''
            insert_values = (firewall, gateway, num_usuarios, timestamp, status)

            cursor.execute(insert_query, insert_values)
            connection.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error {e}")
        return False

def insertar_registros_batch(lista_registros):
    '''Inserta todos los registros de la lista de firewalls a la BD'''
    for registro in lista_registros:
        firewall = registro['firewall']
        gateway = registro['gateway']
        num_usuarios = registro['num_usuarios']
        timestamp = registro['timestamp']
        status = registro['status']

        insertar_registro(firewall, gateway, num_usuarios, timestamp, status)


if __name__ == "__main__":
    crear_tabla()
    print("Base de datos creada")