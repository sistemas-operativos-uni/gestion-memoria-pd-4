# Implementación de PyOS-Core

## Objetivo

Este documento registra la arquitectura y el comportamiento implementado para el módulo académico de gestión de memoria virtual paginada. Los requisitos funcionales de referencia están en `PROMPT.md` y en `simulador-instrucciones.png`.

## Arquitectura

```text
src/pyos_core/
├── __main__.py                 # Demostración ejecutable y trazas
└── memory/
    ├── exceptions.py           # Errores diferenciados del dominio
    ├── page_table.py            # Entradas página lógica -> marco
    └── memory_manager.py        # RAM, asignación y traducción

tests/unit/
├── test_page_table.py
└── test_memory_manager.py

outputs/simulacion.txt          # Salida observable de la demostración
```

La solución mantiene el dominio pequeño y sin dependencias externas. `PageTable` se ocupa de las entradas de un proceso. `MemoryManager` coordina la RAM, conserva una tabla por PID y aplica las reglas de asignación y traducción. El punto de entrada configura las trazas y demuestra los casos; el administrador no imprime directamente.

## Componentes implementados

### `PageTable`

- `map_page(page_number, frame_number)` registra una página residente y rechaza índices negativos, tipos inválidos o una página duplicada.
- `table` permite consultar el formato `page -> {frame, valid}` mediante vistas de solo lectura.
- `get_entry(page_number)` consulta una entrada sin exponer el estado mutable.
- `mark_not_resident(page_number)` invalida la página, limpia su marco asociado y devuelve el marco para que el administrador lo libere.

Una entrada válida siempre contiene un marco. Una entrada no residente contiene `frame=None` y `valid=False`.

### `MemoryManager`

El constructor `MemoryManager(total_frames=16, page_size=4096)` valida tamaños enteros positivos y prepara `free_frames` y `process_tables`.

`allocate_process(pid, num_pages)` valida el PID, el tamaño y la disponibilidad antes de cambiar el estado. Primero prepara la tabla completa y luego reserva los marcos. Si falta RAM, conserva intactos los marcos libres y los procesos existentes. Registra trazas `[ALLOC]` y `[MAP]`.

`translate(pid, virtual_address)` valida el proceso y el espacio virtual asignado, y luego calcula:

```text
page_number = virtual_address // page_size
offset      = virtual_address % page_size
physical    = frame_number * page_size + offset
```

Registra `[TRANSLATE]`, `[PAGE]`, `[OFFSET]`, `[FRAME]` y `[PHYSICAL]`. Solo retorna una dirección física cuando la entrada existe, es válida y apunta a un marco dentro de la RAM.

`evict_page(pid, page_number)` marca explícitamente una página como no residente y devuelve su marco a `free_frames`. Se usa para simular el caso Page Fault del ejercicio. No implementa swapping ni políticas de reemplazo.

### Excepciones

| Excepción | Situación |
| --- | --- |
| `PageFault` | La dirección pertenece al proceso, pero su página no reside en RAM. |
| `BoundsException` | PID válido con dirección o página fuera del espacio asignado. |
| `ProcessNotFoundError` | El PID no tiene espacio asignado. |
| `InsufficientMemoryError` | No quedan marcos suficientes para completar una asignación. |
| `ProcessAlreadyAllocatedError` | El PID ya está registrado. |
| `InvalidAllocationError` | Tamaño, configuración o identificador de proceso inválido. |
| `InvalidPageMappingError` | Mapeo inválido o página que no puede invalidarse. |

Todas derivan de `MemoryManagerError`, salvo sus clases base adicionales (`KeyError`, `MemoryError` o `ValueError`) que facilitan capturas estándar.

## Invariantes

- `total_frames` y `page_size` son enteros positivos; los booleanos no cuentan como enteros válidos.
- Cada proceso tiene una tabla separada y sus páginas reciben marcos exclusivos.
- La operación de asignación reserva todo o nada.
- Los marcos libres y residentes no se solapan ni contienen duplicados; juntos cubren todos los marcos físicos.
- El offset satisface `0 <= offset < page_size`.
- La dirección física siempre se calcula con `frame * page_size + offset`.
- Una dirección negativa, no entera o igual/superior a `num_pages * page_size` genera `BoundsException`.
- `PageFault` se usa solo para una página dentro del rango virtual que no está residente.

## Ejecución

Requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```powershell
$env:PYTHONPATH = "src"
python -m pyos_core
```

La demostración asigna tres páginas al PID 1, traduce una dirección de la página 0 y VA 9000, crea un segundo proceso, expulsa una página para mostrar Page Fault y maneja límites, PID ausente y RAM insuficiente. Las trazas se escriben en la salida estándar.

Para regenerar el documento de salida:

```powershell
$env:PYTHONPATH = "src"
New-Item -ItemType Directory -Force outputs | Out-Null
python -m pyos_core *> outputs/simulacion.txt
```

`outputs/simulacion.txt` contiene únicamente las trazas generadas por el programa.

## Pruebas

Las pruebas usan `unittest`, incluido en Python:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Los casos cubren asignación normal, traducción en página 0 y en otra página, cálculo de VA 9000 (página 2, offset 808), Page Fault, límites, PID inexistente, memoria insuficiente sin mutación parcial, aislamiento entre procesos, devolución de marcos y entradas inválidas.

## Alcance y decisiones

- Se usa una arquitectura `src/` con módulos separados por responsabilidad y pruebas unitarias sin dependencias adicionales.
- `PageTable` ofrece mapeos de solo lectura y operaciones explícitas de modificación para mantener el estado encapsulado.
- La asignación toma primero los marcos libres con menor número, para que las trazas sean reproducibles.
- El logger usa el canal `pyos_core`; una aplicación puede configurar su propio handler. La demostración configura salida a consola.
- La expulsión de página solo sirve para representar una página no residente y reutilizar su marco. El enunciado no solicita recuperar contenidos desde disco.
- No se añadieron TLB, swapping, segmentación, reemplazo de páginas, API, base de datos ni interfaz gráfica.
