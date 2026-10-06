"""Pruebas de asignación, protección y traducción de memoria paginada."""

import unittest

from pyos_core.memory.exceptions import (
    BoundsException,
    InsufficientMemoryError,
    InvalidAllocationError,
    PageFault,
    ProcessAlreadyAllocatedError,
    ProcessNotFoundError,
)
from pyos_core.memory.memory_manager import MemoryManager


class MemoryManagerTests(unittest.TestCase):
    def test_allocates_distinct_frames_and_translates_addresses(self) -> None:
        manager = MemoryManager(total_frames=8, page_size=4096)
        manager.allocate_process(1, 3)

        page_zero_frame = manager.process_tables[1].table[0]["frame"]
        page_two_frame = manager.process_tables[1].table[2]["frame"]
        resident_frames = [
            entry["frame"] for entry in manager.process_tables[1].table.values()
        ]
        self.assertEqual(manager.translate(1, 123), page_zero_frame * 4096 + 123)
        self.assertEqual(manager.translate(1, 9000), page_two_frame * 4096 + 808)
        self.assertEqual(len(set(resident_frames)), 3)

    def test_page_fault_is_distinct_from_bounds_error(self) -> None:
        manager = MemoryManager(total_frames=4, page_size=4096)
        manager.allocate_process(1, 2)
        manager.evict_page(1, 1)

        with self.assertRaises(PageFault):
            manager.translate(1, 4096)
        with self.assertRaises(BoundsException):
            manager.translate(1, 8192)

    def test_rejects_negative_and_non_integer_virtual_addresses(self) -> None:
        manager = MemoryManager(total_frames=2, page_size=4096)
        manager.allocate_process(1, 1)

        for address in (-1, 0.5, True):
            with self.subTest(address=address):
                with self.assertRaises(BoundsException):
                    manager.translate(1, address)  # type: ignore[arg-type]

    def test_reports_missing_process(self) -> None:
        manager = MemoryManager()

        with self.assertRaises(ProcessNotFoundError):
            manager.translate(404, 0)
        with self.assertRaises(ProcessNotFoundError):
            manager.translate([], 0)  # type: ignore[arg-type]

    def test_failed_allocation_keeps_memory_state_unchanged(self) -> None:
        manager = MemoryManager(total_frames=2, page_size=4096)
        manager.allocate_process(1, 1)
        frames_before = manager.free_frames.copy()
        processes_before = manager.process_tables.copy()

        with self.assertRaises(InsufficientMemoryError):
            manager.allocate_process(2, 2)

        self.assertEqual(manager.free_frames, frames_before)
        self.assertEqual(manager.process_tables, processes_before)

    def test_rejects_duplicate_pid_and_invalid_page_count(self) -> None:
        manager = MemoryManager(total_frames=4, page_size=4096)
        manager.allocate_process(1, 1)

        with self.assertRaises(ProcessAlreadyAllocatedError):
            manager.allocate_process(1, 1)
        for pages in (0, -1, 1.5, True):
            with self.subTest(pages=pages):
                with self.assertRaises(InvalidAllocationError):
                    manager.allocate_process(2, pages)  # type: ignore[arg-type]

    def test_processes_use_separate_page_tables_and_frames(self) -> None:
        manager = MemoryManager(total_frames=4, page_size=4096)
        manager.allocate_process("A", 1)
        manager.allocate_process("B", 1)

        self.assertIsNot(manager.process_tables["A"], manager.process_tables["B"])
        self.assertNotEqual(
            manager.process_tables["A"].table[0]["frame"],
            manager.process_tables["B"].table[0]["frame"],
        )

    def test_eviction_returns_frame_to_free_list(self) -> None:
        manager = MemoryManager(total_frames=2, page_size=4096)
        manager.allocate_process(1, 1)
        manager.evict_page(1, 0)

        self.assertEqual(manager.free_frames, [0, 1])
        self.assertEqual(manager.process_tables[1].table[0], {"frame": None, "valid": False})

    def test_rejects_non_positive_memory_configuration(self) -> None:
        for frames, page_size in ((0, 4096), (4, 0), (-1, 4096)):
            with self.subTest(frames=frames, page_size=page_size):
                with self.assertRaises(ValueError):
                    MemoryManager(total_frames=frames, page_size=page_size)


if __name__ == "__main__":
    unittest.main()
