"""Demostración de las operaciones principales del simulador."""

import logging
import sys

from pyos_core.memory.exceptions import (
    BoundsException,
    InsufficientMemoryError,
    PageFault,
    ProcessNotFoundError,
)
from pyos_core.memory.memory_manager import MemoryManager


def run_demo() -> None:
    """Ejecuta traducciones y muestra los errores exigidos por el enunciado."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
        force=True,
    )
    manager = MemoryManager(total_frames=16, page_size=4096)
    manager.allocate_process(pid=0, num_pages=1)
    manager.allocate_process(pid=1, num_pages=3)
    manager.translate(pid=1, virtual_address=123)
    manager.translate(pid=1, virtual_address=9000)
    manager.allocate_process(pid=2, num_pages=1)
    manager.translate(pid=2, virtual_address=0)

    manager.evict_page(pid=1, page_number=1)
    try:
        manager.translate(pid=1, virtual_address=5000)
    except PageFault:
        pass

    try:
        manager.translate(pid=1, virtual_address=12288)
    except BoundsException:
        pass

    try:
        manager.translate(pid=404, virtual_address=0)
    except ProcessNotFoundError:
        pass

    try:
        MemoryManager(total_frames=1, page_size=4096).allocate_process(2, 2)
    except InsufficientMemoryError as error:
        logging.getLogger("pyos_core").error("[MEMORY ERROR] %s", error)


def main() -> None:
    """Punto de entrada para ``python -m pyos_core``."""
    run_demo()


if __name__ == "__main__":
    main()
