#!/usr/bin/env python3
import unittest
from grid_status import *

class TestGridMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    
    def test_set_id(cls):
        g1 = Grid(1, 2)
        g2 = Grid(1, 0, 0)
        g1.relax(g2)
        cls.assertEqual(g1.pred().id(), g2.id())  

if __name__ == '__main__':
    unittest.main()