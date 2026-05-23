import sys

import mysql.connector

from communication.socket_server import SIGOMEISocketServer
from config import DB_CONFIG, SERVER_HOST, SERVER_PORT
from repository.repository import MySQLRepository


def _verificar_conexion_db() -> None:
    """Hace un ping a MySQL al inicio para detectar credenciales/host incorrectos
    antes de aceptar peticiones. Sin esto, un fallo de BD queda enmascarado
    como ERR_INTERNAL en cada login y el cliente ve 'Credenciales incorrectas'.
    """
    print(f"[*] Validando conexion a MySQL en {DB_CONFIG['host']}:{DB_CONFIG['port']} "
          f"(usuario='{DB_CONFIG['user']}', db='{DB_CONFIG['database']}')...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.ping(reconnect=False)
        conn.close()
        print("[+] Conexion a MySQL exitosa.")
    except mysql.connector.Error as e:
        print(f"[-] ERROR: No se puede conectar a MySQL: {e}")
        print()
        print("    Sugerencias:")
        print("    - Verifique que el servicio MySQL este corriendo.")
        print("    - Configure las credenciales antes de arrancar el servidor:")
        print("      PowerShell:  $env:SIGOMEI_DB_PASSWORD = 'tu_password'")
        print("      CMD:         set SIGOMEI_DB_PASSWORD=tu_password")
        print("    - Variables disponibles: SIGOMEI_DB_HOST, SIGOMEI_DB_USER,")
        print("      SIGOMEI_DB_PASSWORD, SIGOMEI_DB_NAME, SIGOMEI_DB_PORT")
        sys.exit(1)


def arrancar_servidor():
    print("=" * 80)
    print("            INICIALIZANDO SISTEMA DE GESTION INDUSTRIAL SIGOMEI              ")
    print("=" * 80)

    _verificar_conexion_db()

    print("[*] Preparando capa de persistencia MySQL...")
    try:
        repositorio_real = MySQLRepository(DB_CONFIG)
        servidor_red = SIGOMEISocketServer(
            host=SERVER_HOST,
            port=SERVER_PORT,
            repository=repositorio_real,
        )
        servidor_red.iniciar()
    except KeyboardInterrupt:
        print("\n[-] Servidor apagado con Ctrl+C.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] ERROR CRITICO AL INICIAR EL BACKEND: {e}")
        sys.exit(1)


if __name__ == "__main__":
    arrancar_servidor()
