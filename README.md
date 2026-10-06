<!-- Guía inicial del repositorio PyOS-Core; describe su propósito y arquitectura. -->
# PyOS-Core: gestor de memoria virtual paginada

Proyecto académico de Sistemas Operativos para organizar un simulador en Python de memoria virtual paginada.

## Alcance

La arquitectura prepara el trabajo para representar tablas de páginas, marcos físicos, asignación por proceso y traducción de direcciones virtuales. El simulador deberá distinguir una traducción válida, un fallo de página y un acceso fuera de los límites asignados.

## Estructura

```text
.
├── docs/                         # Enunciado e imagen de referencia
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

## Componentes previstos

- `PageTable` encapsulará el mapeo de página lógica a marco físico y su bit de validez.
- `MemoryManager` administrará los marcos disponibles, asignará páginas a procesos y coordinará traducciones.
- `exceptions.py` separará errores de límites de los fallos de página.
- `tests/unit/` alojará las pruebas de tablas, asignaciones, límites y traducciones.

## Requisitos

- Python 3.10 o posterior.
- Sin dependencias de ejecución externas previstas para el simulador base.

## Desarrollo

La lógica del simulador y las pruebas se añadirán en sus módulos correspondientes. La entrada de paquete prevista será `python -m pyos_core` una vez implementada.

## Referencia académica

Consulta `docs/PROMPT.md` y `docs/simulador-instrucciones.png` para los requisitos del módulo. `docs/IMPLEMENTATIONS.md` está reservado para futuras notas de implementación.
