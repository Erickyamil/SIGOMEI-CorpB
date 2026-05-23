import json
import socket
import threading
from datetime import date, datetime
from decimal import Decimal

from services.service import ServiceLayer


class SIGOMEISocketServer:
    def __init__(self, host: str, port: int, repository):
        self.host = host
        self.port = port
        self.service = ServiceLayer(repository)
        self._shutdown = threading.Event()

    def iniciar(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            print(f"[*] SIGOMEI socket server escuchando en {self.host}:{self.port}")
            print("[*] Envia JSON por linea. Accion 'ping' para probar conectividad.")

            while not self._shutdown.is_set():
                client, address = server.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client, address),
                    daemon=True,
                )
                thread.start()

    def _handle_client(self, client: socket.socket, address) -> None:
        with client:
            print(f"[*] Cliente conectado: {address[0]}:{address[1]}")
            buffer = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                buffer += chunk

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    response = self._dispatch_line(line)
                    encoded = json.dumps(response, default=_json_default) + "\n"
                    client.sendall(encoded.encode("utf-8"))

    def _dispatch_line(self, line: bytes) -> dict:
        try:
            request = json.loads(line.decode("utf-8"))
            return self._dispatch(request)
        except json.JSONDecodeError as exc:
            return {"status": "ERR_BAD_REQUEST", "message": f"JSON invalido: {exc}", "data": None}
        except KeyError as exc:
            return {"status": "ERR_BAD_REQUEST", "message": f"Campo requerido faltante: {exc}", "data": None}
        except Exception as exc:
            return {"status": "ERR_INTERNAL", "message": str(exc), "data": None}

    def _dispatch(self, request: dict) -> dict:
        # Acepta "action" (protocolo interno) y "cmd" (protocolo del cliente)
        action = request.get("action") or request.get("cmd")
        payload = request.get("payload") or {}
        # id_usuario se extrae del payload (viene del token en producción)
        id_usuario = request.get("id_usuario") or payload.get("id_usuario")

        if action == "ping":
            return {"status": "OK", "message": "pong", "data": None}
        if action == "LOGIN":
            return self.service.verificar_credenciales(
                payload["correo"],
                payload["password_hash"],
            )
        if action == "crear_odm":
            return self.service.crear_odm(payload, id_usuario)
        if action == "actualizar_estado_odm":
            return self.service.actualizar_estado_odm(
                payload["id_odm"],
                payload["nuevo_estado"],
                id_usuario,
                payload.get("costo_real"),
            )
        if action == "obtener_odm":
            return self.service.obtener_odm(payload["id_odm"])
        if action == "listar_odms":
            return self.service.listar_odms()
        if action == "crear_tecnico":
            return self.service.crear_tecnico(payload)
        if action == "cambiar_estatus_tecnico":
            return self.service.cambiar_estatus_tecnico(payload["id_tecnico"], payload["nuevo_estatus"])
        if action == "obtener_tecnico":
            return self.service.obtener_tecnico(payload["id_tecnico"])
        if action == "crear_equipo":
            return self.service.crear_equipo(payload)
        if action == "baja_equipo":
            return self.service.baja_equipo(payload["id_equipo"])
        if action == "obtener_equipo":
            return self.service.obtener_equipo(payload["id_equipo"])

        return {
            "status": "ERR_BAD_REQUEST",
            "message": f"Accion no soportada: {action}",
            "data": None,
        }


def _json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
