import mysql.connector
from mysql.connector import Error
# --- Configuración (REEMPLAZA ESTOS VALORES) ---
HOST = "localhost"
USER = "root"
PASSWORD = "12345"
DATABASE = "monster gym" # Asegúrate de que esta DB exista
# -----------------------------------------------

def crear_conexion(host, user, password, db):
    """Establece la conexión a la base de datos."""
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=db
        )
        if conexion.is_connected():
            print("✅ Conexión a MySQL exitosa.")
    except Error as e:
        print(f"❌ Error al conectar: '{e}'")
    return conexion

# Llamamos a la función para establecer la conexión
conn = crear_conexion(HOST, USER, PASSWORD, DATABASE)

def ejecutar_comando(conexion, comando_sql, datos=None):
    """Ejecuta una sentencia SQL (INSERT, UPDATE, DELETE)."""
    cursor = conexion.cursor()
    try:
        if datos:
            # Usamos %s para pasar los datos de forma segura (previene inyección SQL)
            cursor.execute(comando_sql, datos)
        else:
            cursor.execute(comando_sql)

        conexion.commit() # Guarda los cambios
        print(f"✨ Comando ejecutado con éxito. Filas afectadas: {cursor.rowcount}")
    except Error as e:
        print(f"❌ Error al ejecutar el comando: '{e}'")
    finally:
        cursor.close()

def ejecutar_comando(conexion, comando_sql, datos=None):
    """Ejecuta una sentencia SQL (INSERT, UPDATE, DELETE)."""
    cursor = conexion.cursor()
    try:
        if datos:
            # Usamos %s para pasar los datos de forma segura (previene inyección SQL)
            cursor.execute(comando_sql, datos)
        else:
            cursor.execute(comando_sql)

        conexion.commit() # Guarda los cambios
        print(f"✨ Comando ejecutado con éxito. Filas afectadas: {cursor.rowcount}")
    except Error as e:
        print(f"❌ Error al ejecutar el comando: '{e}'")
    finally:
        cursor.close()
 
