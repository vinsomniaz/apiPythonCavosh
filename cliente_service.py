import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

dbconfig = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_DATABASE,
    "port": DB_PORT,
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="cliente_pool",
    pool_size=5,
    pool_reset_session=True,
    **dbconfig,
)


class ClienteService:

    def _execute_sp(self, sp_name: str, params: dict):
        """Ejecutar Stored Procedures sin ORM, usando mysql-connector"""
        conn = None
        cursor = None

        try:
            conn = connection_pool.get_connection()
            cursor = conn.cursor(dictionary=True)

            placeholders = ", ".join(["%s"] * len(params))
            sql = f"CALL {sp_name}({placeholders})"

            values = list(params.values())
            cursor.execute(sql, values)

            conn.commit()

            try:
                rows = cursor.fetchall()
                return rows if rows else []
            except mysql.connector.errors.InterfaceError:
                return []

        except Exception as e:
            print(f"Error en SP {sp_name}: {e}")

            if conn:
                try:
                    conn.rollback()
                except Exception as rb_err:
                    print(f"Error haciendo rollback en {sp_name}: {rb_err}")

            return [{"error": "El servidor no está disponible"}]

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_cliente(self, correo: str, passwordd: str):
        results = self._execute_sp("sp_getCliente", {"correo": correo, "passwordd": passwordd})
        if results and "error" in results[0]:
            return {"error": results[0]["error"]}
        return results[0] if results else None

    def set_cliente(self, data: "ClienteSchema"):
        params = {
            "id": data.id,
            "nombres": data.nombres,
            "correo": data.correo,
            "passwordd": data.passwordd,
        }

        results = self._execute_sp("sp_setCliente", params)

        if results is None:
            return {"error": "Error al ejecutar SP"}

        if results and "error" in results[0]:
            return {"error": results[0]["error"]}

        # Insert
        if data.id == 0:
            if results and "insertID" in results[0]:
                data.id = results[0]["insertID"]
                return {
                    "id": data.id,
                    "nombres": data.nombres,
                    "correo": data.correo,
                }
            else:
                return {"error": "No se pudo insertar el cliente"}

        # Update
        if data.id > 0:
            return {
                "id": data.id,
                "nombres": data.nombres,
                "correo": data.correo,
            }

    def get_cliente_codigo(self, correo: str):
        results = self._execute_sp("sp_getClienteCodigo", {"correo": correo})

        if results:
            row = results[0]
            if "id" in row:
                return {"id": row["id"], "codigo": row["codigo"]}
            if "error" in row:
                return {"error": row["error"]}

        return {"error": "Error al generar el código."}

    def get_cliente_codigo_validar(self, id_cliente: int, codigo: str):
        params = {"_id": id_cliente, "_codigo": codigo}
        results = self._execute_sp("sp_getClienteCodigoValidar", params)

        if not results:
            return {"error": "El servidor no está disponible"}

        minutos = results[0].get("minutos", 0)

        if minutos > 0:
            return {"validacion": True, "minutos_restantes": minutos}
        else:
            return {"error": "Código inválido o ha caducado."}
