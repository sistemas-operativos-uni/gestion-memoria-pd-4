"""Excepciones del simulador de memoria paginada."""


class MemoryManagerError(Exception):
    """Base para errores esperados al administrar memoria."""


class PageFault(MemoryManagerError):
    """La página pertenece al proceso, pero no está residente en RAM."""


class BoundsException(MemoryManagerError):
    """La dirección virtual está fuera del espacio asignado al proceso."""


class ProcessNotFoundError(MemoryManagerError, KeyError):
    """El PID solicitado no tiene memoria asignada."""


class InsufficientMemoryError(MemoryManagerError, MemoryError):
    """No hay suficientes marcos libres para completar una asignación."""


class ProcessAlreadyAllocatedError(MemoryManagerError, ValueError):
    """El PID ya cuenta con una tabla de páginas en el administrador."""


class InvalidAllocationError(MemoryManagerError, ValueError):
    """Los parámetros de configuración o asignación no son válidos."""


class InvalidPageMappingError(MemoryManagerError, ValueError):
    """Una página o un marco no cumple las reglas de PageTable."""
