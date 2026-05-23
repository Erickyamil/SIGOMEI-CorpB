import uuid

import mysql.connector


class MySQLRepository:
    def __init__(self, db_config: dict):
        self.config = db_config

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def obtener_usuario_por_correo(self, correo: str) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id_usuario, correo, password_hash, rol, activo
                FROM usuario
                WHERE correo = %s AND activo = 1
                """,
                (correo,),
            )
            return cursor.fetchone() or {}
        finally:
            cursor.close()
            conn.close()

    def obtener_tecnico(self, id_tecnico: str) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id_tecnico, nombre, rfc, telefono, correo, estatus
                FROM tecnico
                WHERE id_tecnico = %s AND activo = 1
                """,
                (id_tecnico,),
            )
            tecnico = cursor.fetchone()
            if not tecnico:
                return {}

            cursor.execute(
                """
                SELECT especialidad, nivel, vigencia
                FROM certificacion_tecnico
                WHERE id_tecnico = %s
                """,
                (id_tecnico,),
            )
            tecnico["certificaciones"] = cursor.fetchall()
            return tecnico
        finally:
            cursor.close()
            conn.close()

    def obtener_equipo(self, id_equipo: str) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_equipo, nombre, tipo, marca, modelo, num_serie,
                    estado_operativo, criticidad
                FROM equipo
                WHERE id_equipo = %s AND activo = 1
                """,
                (id_equipo,),
            )
            return cursor.fetchone() or {}
        finally:
            cursor.close()
            conn.close()

    def listar_odms_activas(self) -> list:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id_odm, id_equipo, id_tecnico, fecha_programada, estado
                FROM orden_mantenimiento
                WHERE estado NOT IN ('Cancelada', 'Finalizada')
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def guardar_odm(self, payload: dict, id_usuario_creador: str) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            id_odm = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO orden_mantenimiento
                (
                    id_odm, id_equipo, id_tecnico, nota_original,
                    fecha_programada, fecha_estimada_cierre,
                    costo_estimado, estado, creado_por
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'En_revision', %s)
                """,
                (
                    id_odm,
                    payload["id_equipo"],
                    payload["id_tecnico"],
                    payload["nota_original"],
                    payload["fecha_programada"],
                    payload["fecha_estimada_cierre"],
                    payload["costo_estimado"],
                    id_usuario_creador,
                ),
            )
            conn.commit()
            return id_odm
        finally:
            cursor.close()
            conn.close()

    def obtener_odm(self, id_odm: str) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_odm, id_equipo, id_tecnico, nota_original, fecha_creacion,
                    fecha_programada, fecha_inicio, fecha_estimada_cierre,
                    fecha_cierre, costo_estimado, costo_real,
                    variacion_porcentual, estado, creado_por
                FROM orden_mantenimiento
                WHERE id_odm = %s
                """,
                (id_odm,),
            )
            return cursor.fetchone() or {}
        finally:
            cursor.close()
            conn.close()

    def listar_todas_las_odms(self) -> list:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    id_odm, id_equipo, id_tecnico, fecha_programada,
                    fecha_estimada_cierre, costo_estimado, costo_real,
                    variacion_porcentual, estado, creado_por
                FROM orden_mantenimiento
                ORDER BY fecha_creacion DESC
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def actualizar_estado_simple(self, id_odm: str, nuevo_estado: str, id_usuario: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            estado_anterior = self._obtener_estado_odm(cursor, id_odm)
            cursor.execute(
                "UPDATE orden_mantenimiento SET estado = %s WHERE id_odm = %s",
                (nuevo_estado, id_odm),
            )
            self._guardar_historial(cursor, "ODM", id_odm, estado_anterior, nuevo_estado, id_usuario)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def actualizar_estado_y_costo(
        self,
        id_odm: str,
        nuevo_estado: str,
        costo_real: float,
        variacion: float,
        id_usuario: str,
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            estado_anterior = self._obtener_estado_odm(cursor, id_odm)
            cursor.execute(
                """
                UPDATE orden_mantenimiento
                SET estado = %s,
                    costo_real = %s,
                    variacion_porcentual = %s,
                    fecha_cierre = CURDATE()
                WHERE id_odm = %s
                """,
                (nuevo_estado, costo_real, variacion, id_odm),
            )
            self._guardar_historial(cursor, "ODM", id_odm, estado_anterior, nuevo_estado, id_usuario)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def existe_rfc_tecnico(self, rfc: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM tecnico WHERE rfc = %s LIMIT 1", (rfc,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def guardar_tecnico(self, payload: dict) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            id_tecnico = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO tecnico
                (id_tecnico, nombre, rfc, telefono, correo, fecha_ingreso, estatus)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id_tecnico,
                    payload["nombre"],
                    payload["rfc"],
                    payload["telefono"],
                    payload["correo"],
                    payload["fecha_ingreso"],
                    payload.get("estatus", "Activo"),
                ),
            )
            conn.commit()
            return id_tecnico
        finally:
            cursor.close()
            conn.close()

    def actualizar_estatus_tecnico(self, id_tecnico: str, nuevo_estatus: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE tecnico SET estatus = %s WHERE id_tecnico = %s",
                (nuevo_estatus, id_tecnico),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def existe_num_serie_equipo(self, num_serie: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM equipo WHERE num_serie = %s LIMIT 1", (num_serie,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    def guardar_equipo(self, payload: dict) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            id_equipo = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO equipo
                (
                    id_equipo, nombre, tipo, marca, modelo, num_serie,
                    ubicacion, fecha_instalacion, estado_operativo, criticidad
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id_equipo,
                    payload["nombre"],
                    payload["tipo"],
                    payload["marca"],
                    payload["modelo"],
                    payload["num_serie"],
                    payload["ubicacion"],
                    payload["fecha_instalacion"],
                    payload.get("estado_operativo", "Operativo"),
                    payload.get("criticidad", "Media"),
                ),
            )
            conn.commit()
            return id_equipo
        finally:
            cursor.close()
            conn.close()

    def marcar_inactivo_equipo(self, id_equipo: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE equipo
                SET activo = 0, estado_operativo = 'Inactivo'
                WHERE id_equipo = %s
                """,
                (id_equipo,),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def _obtener_estado_odm(self, cursor, id_odm: str):
        cursor.execute("SELECT estado FROM orden_mantenimiento WHERE id_odm = %s", (id_odm,))
        row = cursor.fetchone()
        return row[0] if row else None

    def _guardar_historial(
        self,
        cursor,
        entidad_tipo: str,
        entidad_id: str,
        estado_anterior: str,
        estado_nuevo: str,
        id_usuario: str,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO historial_estado
            (id_historial, entidad_tipo, entidad_id, estado_anterior, estado_nuevo, id_usuario)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                entidad_tipo,
                entidad_id,
                estado_anterior,
                estado_nuevo,
                id_usuario,
            ),
        )
