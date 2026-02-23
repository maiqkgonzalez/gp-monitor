import sqlite3

def crear_tabla():
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
        print(f"Error {e}")
        return False

def insertar_registros_batch(lista_registros):
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

    #lista_prueba = [{'firewall': 'firewall_mty', 'gateway': 'Campus_GP_Gateway', 'num_usuarios': 0, 'timestamp': '2026-02-17 17:26:14'}, {'firewall': 'firewall_mty', 'gateway': 'Neoris_GP_Gateway', 'num_usuarios': 74, 'timestamp': '2026-02-17 17:26:14'}]

    #insertar_registros_batch(lista_prueba)
    