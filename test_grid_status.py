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

class TestGridBase(unittest.TestCase):
    def test_grid_base(cls):
        g = Point(1, 2)
        cls.assertEqual(g.x, 1)
        cls.assertEqual(g.y, 2)
    
    def test_g_setter(cls):
        g = Point(1, 2)
        g.x = 2
        g.y = 1
        cls.assertEqual(g.x, 2)
        cls.assertEqual(g.y, 1)
    
    def test_g_add(cls):
        g = Point(1, 2) + Point(1, 2)

        cls.assertEqual(g.x, 2)
        cls.assertEqual(g.y, 4)
    
    def test_g_sub(cls):
        g = Point(1, 2) - Point(1, 2)

        cls.assertEqual(g.x, 0)
        cls.assertEqual(g.y, 0)

if __name__ == '__main__':
    unittest.main()