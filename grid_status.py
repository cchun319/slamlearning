#!/usr/bin/env python3

from enum import Enum
from functools import total_ordering
import math

class GridState(Enum):
    UNVISITED = 1
    VISITED = 2
    SEEN = 3
    OCCUPIED = 4

@total_ordering
class Grid:
    def __init__(self, row, col, cost = math.inf):
        self._row = row
        self._col = col
        self._state = GridState.UNVISITED
        self._g = cost

    def __eq__(self, other):
        return self.g() == other.g()
    
    def __lt__(self, other):
        return self.g() < other.g()

    def g(self):
        return self._g
    
    def set_g(self, g):
        self._g = g

    def h(self):
        pass