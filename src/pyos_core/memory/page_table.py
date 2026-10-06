"""Tabla de páginas de un proceso, separada de la administración de RAM."""

from types import MappingProxyType
from typing import Mapping

from pyos_core.memory.exceptions import InvalidPageMappingError


class PageTable:
    """Encapsula el mapeo página lógica -> marco físico y el bit de validez.

    La propiedad ``table`` conserva el formato conceptual del enunciado y
    expone una vista de solo lectura para proteger el estado interno.
    """

    def __init__(self) -> None:
        self._entries: dict[int, dict[str, int | bool | None]] = {}

    @property
    def table(self) -> Mapping[int, Mapping[str, int | bool | None]]:
        """Devuelve entradas inmutables con las claves ``frame`` y ``valid``."""
        snapshot = {
            page_number: MappingProxyType(entry.copy())
            for page_number, entry in self._entries.items()
        }
        return MappingProxyType(snapshot)

    def map_page(self, page_number: int, frame_number: int) -> None:
        """Asocia una página residente con un marco físico libre del proceso."""
        self._validate_index(page_number, "page_number")
        self._validate_index(frame_number, "frame_number")
        if page_number in self._entries:
            raise InvalidPageMappingError(
                f"La página lógica {page_number} ya tiene una entrada."
            )
        self._entries[page_number] = {"frame": frame_number, "valid": True}

    def mark_not_resident(self, page_number: int) -> int:
        """Marca una página como no residente y devuelve el marco que ocupaba."""
        self._validate_index(page_number, "page_number")
        entry = self._entries.get(page_number)
        if entry is None or not entry["valid"]:
            raise InvalidPageMappingError(
                f"La página lógica {page_number} no está mapeada como residente."
            )

        frame_number = entry["frame"]
        if not isinstance(frame_number, int):
            raise InvalidPageMappingError(
                f"La página lógica {page_number} no tiene un marco válido."
            )
        self._entries[page_number] = {"frame": None, "valid": False}
        return frame_number

    def get_entry(self, page_number: int) -> Mapping[str, int | bool | None] | None:
        """Obtiene una entrada de solo lectura o ``None`` si no existe."""
        entry = self._entries.get(page_number)
        if entry is None:
            return None
        return MappingProxyType(entry.copy())

    @staticmethod
    def _validate_index(value: int, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise InvalidPageMappingError(f"{name} debe ser un entero no negativo.")
