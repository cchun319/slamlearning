#!/usr/bin/env python3
import unittest
from queue import PriorityQueue
from grid_status import *

class TestGridStatus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._g1 = Grid(0, 0)
        cls._g2 = Grid(0, 0)
    
    def test_equal(cls):
        cls.assertEqual(cls._g1, cls._g2)

    def test_set(cls):
        cls.assertNotEqual(cls._g1.g(), 100)
        cls._g1.set_g(100)
        cls.assertEqual(cls._g1.g(), 100)
    
    def test_lt(cls):
        cls._g2.set_g(50)
        cls.assertGreater(cls._g1, cls._g2)

class TestPriorityQueue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._pq = PriorityQueue()
    
    def test_pq(cls):
        _g1 = Grid(0, 0, 100)
        _g2 = Grid(0, 0, 50)
        cls._pq.put(_g1)
        cls._pq.put(_g2)

        cls.assertEqual(_g2, cls._pq.get())
        cls._pq.get(False)
    
    def test_pq2(cls):
        cls.assertEqual(cls._pq.qsize(), 0)
        _g1 = Grid(0, 0, 100)
        _g2 = Grid(0, 0, 50)
        cls._pq.put(_g2)
        cls._pq.put(_g1)

        cls.assertEqual(_g2, cls._pq.get())
        cls.assertEqual(_g1, cls._pq.get())        

if __name__ == '__main__':
    unittest.main()