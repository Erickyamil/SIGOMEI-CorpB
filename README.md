# SIGOMEI — Sistema de Gestión de Mantenimiento Industrial

**Universidad Veracruzana · Ingeniería de Software · Desarrollo de Sistemas en Red**

Proyecto E3 · Fase ROJO TDD

---

## Requisitos previos

| Herramienta | Versión mínima | Verificación |
|-------------|---------------|-------------|
| Python | 3.10 | `python --version` |
| pip | 23.0 | `pip --version` |
| Git | cualquiera | `git --version` |

No se requiere MySQL ni ningún servicio externo: la suite de pruebas usa **SQLite en memoria**.


## Instalar dependencias

```bash
pip install --upgrade pip
pip install pytest pytest-cov
```

Tabla de paquetes instalados:

| Paquete | Propósito |
|---------|-----------|
| `pytest` | Runner de pruebas unitarias |
| `pytest-cov` | Reporte de cobertura |

> **Nota fase ROJO:** no se instala ningún ORM (SQLAlchemy, etc.) porque la capa de repositorio aún lanza `NotImplementedError`. Se agrega en la fase VERDE.

---

## Estructura esperada del proyecto

Antes de ejecutar cualquier comando, confirma que el árbol de archivos tenga esta forma:

```
sigomei/
├── app.py                              ← punto de entrada Flask (fase ROJO: no arranca aún)
├── config.py
├── sigomei_server/
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── equipo.py
│   │   ├── odm.py
│   │   └── tecnico.py
│   ├── repository/
│   │   ├── __init__.py
│   │   └── repository.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── equipo_routes.py
│   │   ├── odm_routes.py
│   │   └── tecnico_routes.py
│   └── service/
│       ├── __init__.py
│       ├── service.py
│       └── validators.py
└── tests/
    ├── __init__.py
    └── test_validators.py
```

---

## Ejecutar la suite de pruebas

### Ejecución básica (fase ROJO — se esperan 55 FAILED)

```bash
python -m pytest tests/test_validators.py -v
```

Salida esperada al final:

```
55 failed, 2 passed in 0.48s
```

Esto confirma que el proyecto está en **fase ROJO**: las pruebas compilan e importan sin errores, pero las funciones aún lanzan `NotImplementedError`.

### Ejecución con reporte de cobertura

```bash
python -m pytest tests/test_validators.py \
    --cov=sigomei_server/service \
    --cov-report=term-missing \
    -v
```

### Ejecución de una sola clase de prueba

```bash
# Solo las pruebas de RN-01 (especialidad del técnico)
python -m pytest tests/test_validators.py::TestRN01Especialidad -v

# Solo las pruebas de RN-07 (transiciones de estado)
python -m pytest tests/test_validators.py::TestRN07Transiciones -v
```

### 5.4 Ejecución con salida corta (útil para CI)

```bash
python -m pytest tests/test_validators.py --tb=short
```

---

## Ciclo TDD — pasos para la fase VERDE

Una vez que la fase ROJO está confirmada (55 pruebas fallando), el flujo de
implementación es el siguiente:

1. Seleccionar una función en `sigomei_server/service/validators.py`.
2. Implementar la lógica hasta que los TCs correspondientes pasen.
3. Ejecutar la suite completa para detectar regresiones:

```bash
python -m pytest tests/test_validators.py -v
```

4. Repetir hasta alcanzar **55 passed**.

Objetivo de cobertura al finalizar la fase VERDE:

```bash
python -m pytest tests/test_validators.py \
    --cov=sigomei_server/service \
    --cov-report=term-missing
# Meta: >= 90 % de cobertura en validators.py
```

---

## Reglas de negocio implementadas en `validators.py`

| ID | Función | Excepción |
|----|---------|-----------|
| RN-01 | `validar_especialidad` | `EspecialidadIncompatibleException` |
| RN-02 | `validar_criticidad` | `CriticidadInsuficienteException` |
| RN-03 | `validar_equipo_disponible` | `EquipoOcupadoException` |
| RN-04 | `validar_tecnico_activo` | `TecnicoInactivoException` |
| RN-05 | `validar_fechas_odm` | `FechasIncoherentesException` |
| RN-06 | `validar_carga` | `CargaMaximaAlcanzadaException` |
| RN-07 | `validar_transicion` | `TransicionEstadoInvalidaException` |
| RN-08 | `validar_costo_cierre` | `CostoInvalidoException` |

---