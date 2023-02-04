#!/usr/bin/env python3
import unittest
from board import GridMap
from grid_status import *

class TestGridMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._g1 = GridMap(2, 3)
    
    def test_set_id(cls):
        cls.assertEqual(cls._g1.get_grid(1, 2).id(), [1, 2])  

if __name__ == '__main__':
    unittest.main()