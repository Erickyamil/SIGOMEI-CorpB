# main_server.py
# Archivo de Arranque Principal — Servidor de Producción SIGOMEI Backend

import sys
from repository.repository import MySQLRepository
from communication.socket_server import SIGOMEISocketServer

def arrancar_servidor():
    print("=" * 80)
    print("            INICIALIZANDO SISTEMA DE GESTIÓN INDUSTRIAL SIGOMEI              ")
    print("=" * 80)

    # 1. Configuración de credenciales de red y persistencia local para MySQL 8.0
    # Modifica estos valores de acuerdo con los parámetros de tu servidor local
    db_config = {
        "host": "127.0.0.1",       # Tu localhost
        "user": "root",            # Tu usuario de MySQL
        "password": "tu_password",  # ¡Escribe aquí la contraseña de tu MySQL!
        "database": "sigomei_db",  # Base de datos oficial creada en tu Paso 5
        "port": 3306               # Puerto estándar de MySQL
    }

    print("[*] Conectando Capa de Persistencia con MySQL 8.0...")
    try:
        # 2. Instanciar el Repositorio de Producción con la configuración oficial
        repositorio_real = MySQLRepository(db_config)
        
        # 3. Inicializar el Servidor de Red Sockets TCP vinculándolo al puerto 9000
        servidor_red = SIGOMEISocketServer(host="0.0.0.0", port=9000, repository=repositorio_real)
        
        # 4. Encender el servidor (Se queda escuchando en un bucle infinito)
        servidor_red.iniciar()

    except KeyboardInterrupt:
        print("\n[-] Servidor apagado ordenadamente mediante interrupción de consola (Ctrl+C).")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] ERROR CRÍTICO AL INICIAR EL BACKEND: {e}")
        sys.exit(1)

if __name__ == "__main__":
    arrancar_servidor()