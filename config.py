import os


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


DB_CONFIG = {
    "host": os.getenv("SIGOMEI_DB_HOST", "127.0.0.1"),
    "user": os.getenv("SIGOMEI_DB_USER", "root"),
    "password": os.getenv("SIGOMEI_DB_PASSWORD", ""),
    "database": os.getenv("SIGOMEI_DB_NAME", "sigomei_db"),
    "port": _int_env("SIGOMEI_DB_PORT", 3306),
}

SERVER_HOST = os.getenv("SIGOMEI_SERVER_HOST", "127.0.0.1")
SERVER_PORT = _int_env("SIGOMEI_SERVER_PORT", 9000)
