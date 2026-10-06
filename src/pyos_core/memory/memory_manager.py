"""Administrador de marcos físicos y traducción de direcciones virtuales."""

import logging
from collections.abc import Hashable

from pyos_core.memory.exceptions import (
    BoundsException,
    InsufficientMemoryError,
    InvalidAllocationError,
    PageFault,
    ProcessAlreadyAllocatedError,
    ProcessNotFoundError,
)
from pyos_core.memory.page_table import PageTable

logger = logging.getLogger("pyos_core")
logger.addHandler(logging.NullHandler())


class MemoryManager:
    """Simula una RAM dividida en marcos y espacios virtuales por PID."""

    def __init__(self, total_frames: int = 16, page_size: int = 4096) -> None:
        self._validate_positive_integer(total_frames, "total_frames")
        self._validate_positive_integer(page_size, "page_size")
        self.total_frames = total_frames
        self.page_size = page_size
        self.free_frames = list(range(total_frames))
        self.process_tables: dict[Hashable, PageTable] = {}
        self._process_page_counts: dict[Hashable, int] = {}

    def allocate_process(self, pid: Hashable, num_pages: int) -> PageTable:
        """Reserva todos los marcos requeridos y crea la tabla del proceso.

        La validación y la construcción de la tabla ocurren antes de mutar el
        administrador, de modo que una asignación fallida no deja reservas
        parciales.
        """
        self._validate_pid(pid)
        self._validate_positive_integer(num_pages, "num_pages")
        if pid in self.process_tables:
            raise ProcessAlreadyAllocatedError(f"El PID {pid!r} ya está asignado.")
        if num_pages > len(self.free_frames):
            raise InsufficientMemoryError(
                f"PID {pid!r} necesita {num_pages} marcos; quedan "
                f"{len(self.free_frames)} libres."
            )

        selected_frames = self.free_frames[:num_pages]
        page_table = PageTable()
        for page_number, frame_number in enumerate(selected_frames):
            page_table.map_page(page_number, frame_number)

        self.free_frames = self.free_frames[num_pages:]
        self.process_tables[pid] = page_table
        self._process_page_counts[pid] = num_pages
        logger.info("[ALLOC] PID=%s Pages=%d", pid, num_pages)
        for page_number, frame_number in enumerate(selected_frames):
            logger.info(
                "[MAP] PID=%s Page=%d -> Frame=%d", pid, page_number, frame_number
            )
        self._assert_consistent()
        return page_table

    def translate(self, pid: Hashable, virtual_address: int) -> int:
        """Traduce una dirección virtual o lanza una excepción específica."""
        try:
            page_table = self.process_tables.get(pid)
        except TypeError as error:
            logger.error("[PROCESS NOT FOUND] PID=%s is not allocated", pid)
            raise ProcessNotFoundError(
                f"El PID {pid!r} no tiene memoria asignada."
            ) from error
        if page_table is None:
            logger.error("[PROCESS NOT FOUND] PID=%s is not allocated", pid)
            raise ProcessNotFoundError(f"El PID {pid!r} no tiene memoria asignada.")

        if (
            isinstance(virtual_address, bool)
            or not isinstance(virtual_address, int)
            or virtual_address < 0
            or virtual_address >= self._process_page_counts[pid] * self.page_size
        ):
            logger.error(
                "[BOUNDS ERROR] PID=%s VA=%s is outside process address space",
                pid,
                virtual_address,
            )
            raise BoundsException(
                f"La dirección virtual {virtual_address!r} está fuera del "
                f"espacio asignado al PID {pid!r}."
            )

        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        logger.info("[TRANSLATE] PID=%s VA=%d", pid, virtual_address)
        logger.info("[PAGE] %d", page_number)
        logger.info("[OFFSET] %d", offset)

        entry = page_table.get_entry(page_number)
        if entry is None or entry["valid"] is not True:
            logger.error(
                "[PAGE FAULT] PID=%s Page=%d is not resident in RAM", pid, page_number
            )
            raise PageFault(
                f"La página {page_number} del PID {pid!r} no reside en RAM."
            )

        frame_number = entry["frame"]
        if not isinstance(frame_number, int) or not 0 <= frame_number < self.total_frames:
            raise RuntimeError("La tabla contiene un marco físico inválido.")

        physical_address = frame_number * self.page_size + offset
        logger.info("[FRAME] %d", frame_number)
        logger.info("[PHYSICAL] %d", physical_address)
        return physical_address

    def evict_page(self, pid: Hashable, page_number: int) -> int:
        """Retira una página de RAM para poder simular un Page Fault.

        No implementa swapping ni reemplazo automático; solo actualiza el bit
        de validez y devuelve el marco a la lista de libres.
        """
        page_table = self._get_process_table(pid)
        if (
            isinstance(page_number, bool)
            or not isinstance(page_number, int)
            or page_number < 0
            or page_number >= self._process_page_counts[pid]
        ):
            raise BoundsException(
                f"La página {page_number!r} está fuera del espacio del PID {pid!r}."
            )

        frame_number = page_table.mark_not_resident(page_number)
        self.free_frames.append(frame_number)
        self.free_frames.sort()
        logger.info(
            "[EVICT] PID=%s Page=%d -> Frame=%d is now free",
            pid,
            page_number,
            frame_number,
        )
        self._assert_consistent()
        return frame_number

    def _get_process_table(self, pid: Hashable) -> PageTable:
        try:
            return self.process_tables[pid]
        except (KeyError, TypeError) as error:
            logger.error("[PROCESS NOT FOUND] PID=%s is not allocated", pid)
            raise ProcessNotFoundError(
                f"El PID {pid!r} no tiene memoria asignada."
            ) from error

    def _allocated_frames(self) -> list[int]:
        """Recopila marcos residentes para comprobar las invariantes internas."""
        frames: list[int] = []
        for page_table in self.process_tables.values():
            for entry in page_table.table.values():
                frame_number = entry["frame"]
                if entry["valid"] is True and isinstance(frame_number, int):
                    frames.append(frame_number)
        return frames

    def _assert_consistent(self) -> None:
        free_frames = self.free_frames
        allocated_frames = self._allocated_frames()
        all_frames = free_frames + allocated_frames
        if (
            len(free_frames) != len(set(free_frames))
            or len(allocated_frames) != len(set(allocated_frames))
            or set(free_frames).intersection(allocated_frames)
            or set(all_frames) != set(range(self.total_frames))
        ):
            raise RuntimeError("El estado de marcos libres y asignados es inconsistente.")

    @staticmethod
    def _validate_positive_integer(value: int, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise InvalidAllocationError(f"{name} debe ser un entero positivo.")

    @staticmethod
    def _validate_pid(pid: Hashable) -> None:
        try:
            hash(pid)
        except TypeError as error:
            raise InvalidAllocationError("pid debe ser un identificador hashable.") from error
