<!-- Guía inicial del repositorio PyOS-Core; describe su propósito y arquitectura. -->
# PyOS-Core: gestor de memoria virtual paginada

Proyecto académico de Sistemas Operativos que simula la asignación de marcos y la traducción de direcciones virtuales mediante paginación.

## Alcance

El simulador mantiene una tabla de páginas por proceso y distingue una traducción válida, un fallo de página, una dirección fuera de límites, un PID inexistente y una asignación que supera la RAM disponible.

## Estructura

```text
.
├── docs/                         # Enunciado e imagen de referencia
├── outputs/                      # Traza de consola generada por la demostración
├── src/
│   └── pyos_core/
│       ├── __main__.py           # Entrada para ejecutar el paquete
│       └── memory/
│           ├── exceptions.py     # Excepciones del dominio de memoria
│           ├── memory_manager.py # RAM, marcos libres y procesos
│           └── page_table.py     # Mapeo de páginas y validez
├── tests/
│   └── unit/                     # Pruebas por componente
└── pyproject.toml                # Metadatos y configuración del proyecto
```

## Componentes

- `PageTable` encapsula el mapeo página lógica-marco físico y el bit de validez. Las entradas se consultan como vistas de solo lectura.
- `MemoryManager` administra marcos, asigna espacios por proceso, traduce direcciones y permite retirar una página para demostrar un Page Fault.
- `exceptions.py` distingue límites, Page Fault, PID inexistente, falta de memoria y parámetros inválidos.
- `tests/unit/` cubre tablas, asignaciones, límites, traducciones e invariantes.

## Requisitos

- Python 3.10 o posterior.
- Sin dependencias de ejecución externas previstas para el simulador base.

## Ejecutar

Configura la ruta del paquete local y ejecuta la demostración:

```powershell
$env:PYTHONPATH = "src"
python -m pyos_core
```

La demostración imprime la salida de consola también guardada en `outputs/simulacion.txt`.

## Pruebas

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Referencia académica

Consulta `docs/PROMPT.md` y `docs/simulador-instrucciones.png` para los requisitos del módulo. `docs/IMPLEMENTATIONS.md` describe el diseño, las decisiones y la verificación de esta implementación.
