# sigomei_server/service/validators.py
# Esqueleto de la capa de validación — FASE ROJO TDD
# Cada función es PURA: recibe dicts Python, retorna bool o lanza excepción
# Sin dependencias de red ni BD — testeable directamente con pytest

# ─── Excepciones de dominio ───────────────────────────────────────────────────

class EspecialidadIncompatibleException(Exception):
    """RN-01: La especialidad del técnico no cubre el tipo de equipo."""
    pass

class CriticidadInsuficienteException(Exception):
    """RN-02: Equipos Alta criticidad requieren técnico Nivel II o III."""
    pass

class EquipoOcupadoException(Exception):
    """RN-03: El equipo ya tiene una ODM activa en la misma fecha."""
    pass

class TecnicoInactivoException(Exception):
    """RN-04: No se puede asignar un técnico con estatus Inactivo."""
    pass

class FechasIncoherentesException(Exception):
    """RN-05: fecha_estimada_cierre debe ser posterior a fecha_programada."""
    pass

class CargaMaximaAlcanzadaException(Exception):
    """RN-06: El técnico ya alcanzó el máximo de órdenes En_Ejecucion."""
    pass

class TransicionEstadoInvalidaException(Exception):
    """RN-07: La transición de estado solicitada no está permitida."""
    pass

class CostoInvalidoException(Exception):
    """RN-08: El costo_real al cierre debe ser > 0."""
    pass


# ─── Máquina de estados ───────────────────────────────────────────────────────

TRANSICIONES_PERMITIDAS = {
    "En_revision":        {"Programada"},
    "Programada":         {"En_Ejecucion", "Cancelada"},
    "En_Ejecucion":       {"En_espera_material", "Finalizada", "Cancelada"},
    "En_espera_material": {"En_Ejecucion"},
    "Finalizada":         set(),
    "Cancelada":          set(),
}


# ─── RN-01 ────────────────────────────────────────────────────────────────────

def validar_especialidad(tecnico: dict, equipo: dict) -> bool:
    """
    RN-01 — El técnico debe tener certificación en la especialidad del equipo.

    :param tecnico: dict con clave 'certificaciones' (lista de dicts con 'especialidad')
    :param equipo:  dict con clave 'tipo'
    :raises EspecialidadIncompatibleException: si no hay coincidencia
    :returns: True si la validación pasa
    """
    raise NotImplementedError("RN-01 no implementado — fase ROJO")


# ─── RN-02 ────────────────────────────────────────────────────────────────────

def validar_criticidad(equipo: dict, tecnico: dict) -> bool:
    """
    RN-02 — Equipos de criticidad Alta exigen Nivel II o III en el técnico.

    :param equipo:  dict con clave 'criticidad' ('Baja'|'Media'|'Alta')
    :param tecnico: dict con clave 'certificaciones' (lista de dicts con 'nivel')
    :raises CriticidadInsuficienteException: si el nivel es insuficiente
    :returns: True si la validación pasa
    """
    raise NotImplementedError("RN-02 no implementado — fase ROJO")


# ─── RN-03 ────────────────────────────────────────────────────────────────────

def validar_equipo_disponible(id_equipo: str, fecha_programada: str, odms_activas: list) -> bool:
    """
    RN-03 — Un equipo no puede tener dos ODMs activas en la misma fecha.

    :param id_equipo:       identificador del equipo
    :param fecha_programada: fecha ISO 'YYYY-MM-DD'
    :param odms_activas:    lista de dicts con 'id_equipo', 'fecha_programada', 'estado'
    :raises EquipoOcupadoException: si ya existe conflicto de agenda
    :returns: True si el equipo está disponible
    """
    raise NotImplementedError("RN-03 no implementado — fase ROJO")


# ─── RN-04 ────────────────────────────────────────────────────────────────────

def validar_tecnico_activo(tecnico: dict) -> bool:
    """
    RN-04 — El técnico debe tener estatus 'Activo' para ser asignado.

    :param tecnico: dict con clave 'estatus' ('Activo'|'Inactivo')
    :raises TecnicoInactivoException: si el técnico no está activo
    :returns: True si el técnico está activo
    """
    raise NotImplementedError("RN-04 no implementado — fase ROJO")


# ─── RN-05 ────────────────────────────────────────────────────────────────────

def validar_fechas_odm(fecha_programada: str, fecha_estimada_cierre: str) -> bool:
    """
    RN-05 — fecha_estimada_cierre debe ser estrictamente posterior a fecha_programada.

    :param fecha_programada:       fecha ISO 'YYYY-MM-DD'
    :param fecha_estimada_cierre:  fecha ISO 'YYYY-MM-DD'
    :raises FechasIncoherentesException: si la fecha de cierre no es posterior
    :returns: True si las fechas son coherentes
    """
    raise NotImplementedError("RN-05 no implementado — fase ROJO")


# ─── RN-06 ────────────────────────────────────────────────────────────────────

def validar_carga(tecnico: dict, odms_activas: list, max_carga: int = 3) -> bool:
    """
    RN-06 — Un técnico no puede tener más de max_carga ODMs en estado En_Ejecucion.

    :param tecnico:     dict con clave 'id_tecnico'
    :param odms_activas: lista de dicts con 'id_tecnico' y 'estado'
    :param max_carga:   límite máximo (por defecto 3)
    :raises CargaMaximaAlcanzadaException: si se supera el límite
    :returns: True si hay capacidad disponible
    """
    raise NotImplementedError("RN-06 no implementado — fase ROJO")


# ─── RN-07 ────────────────────────────────────────────────────────────────────

def validar_transicion(estado_actual: str, estado_nuevo: str) -> bool:
    """
    RN-07 — Solo se permiten las transiciones de estado definidas en TRANSICIONES_PERMITIDAS.

    :param estado_actual: estado actual de la ODM
    :param estado_nuevo:  estado al que se quiere transicionar
    :raises TransicionEstadoInvalidaException: si la transición no está permitida
    :returns: True si la transición es válida
    """
    raise NotImplementedError("RN-07 no implementado — fase ROJO")


# ─── RN-08 ────────────────────────────────────────────────────────────────────

def validar_costo_cierre(costo_real: float) -> bool:
    """
    RN-08 — El costo_real al cerrar una ODM debe ser un valor numérico > 0.

    :param costo_real: valor monetario del cierre
    :raises CostoInvalidoException: si costo_real <= 0 o no es numérico
    :returns: True si el costo es válido
    """
    raise NotImplementedError("RN-08 no implementado — fase ROJO")
