import sys

from communication.socket_server import SIGOMEISocketServer
from config import DB_CONFIG, SERVER_HOST, SERVER_PORT
from repository.repository import MySQLRepository


def arrancar_servidor():
    print("=" * 80)
    print("            INICIALIZANDO SISTEMA DE GESTION INDUSTRIAL SIGOMEI              ")
    print("=" * 80)

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
