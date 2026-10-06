"""Pruebas para el mapeo encapsulado de páginas lógicas."""

import unittest

from pyos_core.memory.exceptions import InvalidPageMappingError
from pyos_core.memory.page_table import PageTable


class PageTableTests(unittest.TestCase):
    def test_maps_page_to_resident_frame(self) -> None:
        table = PageTable()

        table.map_page(0, 4)

        self.assertEqual(table.table[0]["frame"], 4)
        self.assertTrue(table.table[0]["valid"])

    def test_invalidates_page_without_exposing_mutable_entries(self) -> None:
        table = PageTable()
        table.map_page(2, 7)

        table.mark_not_resident(2)

        self.assertIsNone(table.table[2]["frame"])
        self.assertFalse(table.table[2]["valid"])
        with self.assertRaises(TypeError):
            table.table[2]["valid"] = True

    def test_rejects_duplicate_page_mapping(self) -> None:
        table = PageTable()
        table.map_page(1, 3)

        with self.assertRaises(InvalidPageMappingError):
            table.map_page(1, 4)

    def test_rejects_negative_page_or_frame(self) -> None:
        table = PageTable()

        for page, frame in ((-1, 0), (0, -1)):
            with self.subTest(page=page, frame=frame):
                with self.assertRaises(InvalidPageMappingError):
                    table.map_page(page, frame)


if __name__ == "__main__":
    unittest.main()
