# sigomei_server/service/service.py
# Capa de servicio — ESQUELETO (fase ROJO)
# No implementa lógica — delega a validators.py


class ServiceLayer:
    def __init__(self, repository):
        self.repo = repository

    def crear_odm(self, payload: dict) -> dict:
        raise NotImplementedError("crear_odm no implementado")

    def actualizar_estado_odm(self, payload: dict) -> dict:
        raise NotImplementedError("actualizar_estado_odm no implementado")

    def crear_tecnico(self, payload: dict) -> dict:
        raise NotImplementedError("crear_tecnico no implementado")

    def cambiar_estatus_tecnico(self, payload: dict) -> dict:
        raise NotImplementedError("cambiar_estatus_tecnico no implementado")

    def crear_equipo(self, payload: dict) -> dict:
        raise NotImplementedError("crear_equipo no implementado")

    def baja_equipo(self, payload: dict) -> dict:
        raise NotImplementedError("baja_equipo no implementado")
