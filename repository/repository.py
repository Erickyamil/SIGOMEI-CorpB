# sigomei_server/repository/repository.py
import mysql.connector

class MySQLRepository:
    def __init__(self, db_config: dict):
        self.config = db_config

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def obtener_tecnico(self, id_tecnico: str) -> dict:
        """Recupera un técnico con todas sus certificaciones según el DDL oficial."""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Selecciona las columnas reales definidas en tu tabla 'tecnico'
            cursor.execute(
                "SELECT id_tecnico, nombre, rfc, telefono, correo, estatus FROM tecnico WHERE id_tecnico = %s AND activo = 1", 
                (id_tecnico,)
            )
            tecnico = cursor.fetchone()
            if not tecnico:
                return {}

            # Consulta ajustada a la tabla certificacion_tecnico (especialidad, nivel, vigencia)
            cursor.execute(
                "SELECT especialidad, nivel, vigencia FROM certificacion_tecnico WHERE id_tecnico = %s", 
                (id_tecnico,)
            )
            tecnico["certificaciones"] = cursor.fetchall()
            return tecnico
        finally:
            cursor.close()
            conn.close()

    def obtener_equipo(self, id_equipo: str) -> dict:
        """Recupera un equipo por su ID utilizando las columnas oficiales del DDL."""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id_equipo, nombre, tipo, marca, modelo, num_serie, estado_operativo, criticidad FROM equipo WHERE id_equipo = %s AND activo = 1", 
                (id_equipo,)
            )
            return cursor.fetchone() or {}
        finally:
            cursor.close()
            conn.close()

    def listar_odms_activas(self) -> list:
        """Lista las ODMs activas para validaciones cruzadas (excluye Cancelada y Finalizada)."""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id_odm, id_equipo, id_tecnico, fecha_programada, estado FROM orden_mantenimiento WHERE estado NOT IN ('Cancelada', 'Finalizada')"
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def guardar_odm(self, payload: dict, id_usuario_creador: str) -> str:
        """Inserta una nueva ODM respetando la obligatoriedad de la FK 'creado_por' de tu DDL."""
        import uuid
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            id_odm = str(uuid.uuid4())
            # Query ajustado para incluir 'creado_por', requerido por la restricción de integridad referencial fk_odm_usuario
            query = """
                INSERT INTO orden_mantenimiento 
                (id_odm, id_equipo, id_tecnico, nota_original, fecha_programada, fecha_estimada_cierre, costo_estimado, estado, creado_por) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'En_revision', %s)
            """
            params = (
                id_odm,
                payload["id_equipo"],
                payload["id_tecnico"],
                payload["nota_original"],
                payload["fecha_programada"],
                payload["fecha_estimada_cierre"],
                payload["costo_estimado"],
                id_usuario_creador  # Id del usuario Supervisor o Admin que inició sesión
            )
            cursor.execute(query, params)
            conn.commit()
            return id_odm
        finally:
            cursor.close()
            conn.close()