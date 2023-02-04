#!/usr/bin/env python3
import unittest
from board import GridMap
from grid_status import *
from Dijkstra import Dijkstra

class TestDisk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._map = GridMap(3, 3)

    def test_map_with_no_obstable(cls):
        plannar = Dijkstra()
        cls._map.set_grid_index_state(0, 0, GridState.SRC)
        cls._map.set_grid_index_state(2, 2, GridState.DEST)

        status = plannar.plan(cls._map)

        cls.assertEqual(status._path, [[0,0],[1,0], [1,1], [1,2], [2,2]])
if __name__ == '__main__':
    unittest.main()