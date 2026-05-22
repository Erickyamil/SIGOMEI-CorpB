# services/service.py
# Capa de Servicio Completa — Coordina la persistencia con las Reglas de Negocio (RN)

from services.validators import (
    validar_tecnico_activo,
    validar_especialidad,
    validar_criticidad,
    validar_fechas_odm,
    validar_equipo_disponible,
    validar_carga,
    validar_transicion,
    validar_costo_cierre
)

class ServiceLayer:
    def __init__(self, repository):
        """
        Inyectamos la capa de persistencia (Repositorio)
        """
        self.repo = repository

    # ──────────────────────────────────────────────────────────────────────────
    # DOMINIO: ORDEN DE MANTENIMIENTO (ODM)
    # ──────────────────────────────────────────────────────────────────────────

    def crear_odm(self, payload: dict, id_usuario_creador: str) -> dict:
        """RF-39 / RF-04: Caso de Uso — Registrar una nueva ODM en el sistema."""
        tecnico = self.repo.obtener_tecnico(payload["id_tecnico"])
        equipo = self.repo.obtener_equipo(payload["id_equipo"])
        odms_activas = self.repo.listar_odms_activas()

        if not tecnico:
            return {"status": "ERR_NOT_FOUND", "message": "El técnico especificado no existe.", "data": None}
        if not equipo:
            return {"status": "ERR_NOT_FOUND", "message": "El equipo especificado no existe.", "data": None}

        try:
            validar_tecnico_activo(tecnico)                                # RN-04
            validar_especialidad(tecnico, equipo)                           # RN-01
            validar_criticidad(equipo, tecnico)                             # RN-02
            validar_fechas_odm(payload["fecha_programada"], payload["fecha_estimada_cierre"]) # RN-05
            validar_equipo_disponible(payload["id_equipo"], payload["fecha_programada"], odms_activas) # RN-03
            validar_carga(tecnico, odms_activas)                            # RN-06
        except Exception as e:
            return {"status": "ERR_BUSINESS", "message": str(e), "data": None}

        id_nueva_odm = self.repo.guardar_odm(payload, id_usuario_creador)
        return {
            "status": "OK",
            "message": "Orden de Mantenimiento creada exitosamente.",
            "data": {"id_odm": id_nueva_odm}
        }

    def actualizar_estado_odm(self, id_odm: str, nuevo_estado: str, id_usuario: str, costo_real: float = None) -> dict:
        """RF-14 / RF-19: Avanzar una ODM en su ciclo de vida (Máquina de estados)."""
        odm = self.repo.obtener_odm(id_odm)
        if not odm:
            return {"status": "ERR_NOT_FOUND", "message": "La ODM especificada no existe.", "data": None}

        estado_actual = odm["estado"]

        try:
            # 1. Validar si la transición de estados está permitida por la RN-07
            validar_transicion(estado_actual, nuevo_estado)

            # 2. Si pasa a estado Finalizada, validar obligatoriamente el costo real (RN-08)
            if nuevo_estado == "Finalizada":
                validar_costo_cierre(costo_real)
                # Calcular automáticamente variación porcentual si se cierra (RF-55)
                costo_estimado = float(odm["costo_estimado"])
                variacion = ((costo_real - costo_estimado) / costo_estimado) * 100
                self.repo.actualizar_estado_y_costo(id_odm, nuevo_estado, costo_real, variacion, id_usuario)
            else:
                self.repo.actualizar_estado_simple(id_odm, nuevo_estado, id_usuario)

            return {"status": "OK", "message": f"Estado de ODM actualizado con éxito a {nuevo_estado}.", "data": None}

        except Exception as e:
            return {"status": "ERR_BUSINESS", "message": str(e), "data": None}

    def obtener_odm(self, id_odm: str) -> dict:
        """Consulta los detalles de una ODM específica."""
        odm = self.repo.obtener_odm(id_odm)
        if not odm:
            return {"status": "ERR_NOT_FOUND", "message": "ODM no encontrada.", "data": None}
        return {"status": "OK", "message": "Éxito", "data": odm}

    def listar_odms(self) -> dict:
        """Lista todo el historial de órdenes registradas."""
        lista = self.repo.listar_todas_las_odms()
        return {"status": "OK", "message": "Éxito", "data": lista}

    # ──────────────────────────────────────────────────────────────────────────
    # DOMINIO: TÉCNICOS
    # ──────────────────────────────────────────────────────────────────────────

    def crear_tecnico(self, payload: dict) -> dict:
        """RF-35: Registrar un nuevo técnico en el sistema."""
        if self.repo.existe_rfc_tecnico(payload["rfc"]):
            return {"status": "ERR_BUSINESS", "message": "El RFC ya se encuentra registrado (Unicidad).", "data": None}
        
        id_tecnico = self.repo.guardar_tecnico(payload)
        return {"status": "OK", "message": "Técnico registrado exitosamente.", "data": {"id_tecnico": id_tecnico}}

    def cambiar_estatus_tecnico(self, id_tecnico: str, nuevo_estatus: str) -> dict:
        """RF-45: Modificar estatus (Activo/Inactivo) o baja lógica del técnico."""
        tecnico = self.repo.obtener_tecnico(id_tecnico)
        if not tecnico:
            return {"status": "ERR_NOT_FOUND", "message": "Técnico no encontrado.", "data": None}
        
        self.repo.actualizar_estatus_tecnico(id_tecnico, nuevo_estatus)
        return {"status": "OK", "message": "Estatus del técnico actualizado correctamente.", "data": None}

    def obtener_tecnico(self, id_tecnico: str) -> dict:
        """Consulta los detalles y certificaciones de un técnico."""
        tecnico = self.repo.obtener_tecnico(id_tecnico)
        if not tecnico:
            return {"status": "ERR_NOT_FOUND", "message": "Técnico no encontrado.", "data": None}
        return {"status": "OK", "message": "Éxito", "data": tecnico}

    # ──────────────────────────────────────────────────────────────────────────
    # DOMINIO: EQUIPOS INDUSTRIALES
    # ──────────────────────────────────────────────────────────────────────────

    def crear_equipo(self, payload: dict) -> dict:
        """RF-31: Registrar un nuevo equipo industrial en catálogo."""
        if self.repo.existe_num_serie_equipo(payload["num_serie"]):
            return {"status": "ERR_BUSINESS", "message": "El número de serie del equipo ya existe.", "data": None}
        
        id_equipo = self.repo.guardar_equipo(payload)
        return {"status": "OK", "message": "Equipo registrado con éxito.", "data": {"id_equipo": id_equipo}}

    def baja_equipo(self, id_equipo: str) -> dict:
        """RF-08: Baja lógica (Activo = 0) para preservar el historial relacional."""
        equipo = self.repo.obtener_equipo(id_equipo)
        if not equipo:
            return {"status": "ERR_NOT_FOUND", "message": "Equipo no encontrado.", "data": None}
        
        self.repo.marcar_inactivo_equipo(id_equipo)
        return {"status": "OK", "message": "Equipo dado de baja lógicamente con éxito.", "data": None}

    def obtener_equipo(self, id_equipo: str) -> dict:
        """Consulta los detalles de un equipo."""
        equipo = self.repo.obtener_equipo(id_equipo)
        if not equipo:
            return {"status": "ERR_NOT_FOUND", "message": "Equipo no encontrado.", "data": None}
        return {"status": "OK", "message": "Éxito", "data": equipo}