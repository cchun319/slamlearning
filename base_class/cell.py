#!/usr/bin/env python3

from functools import total_ordering
from base_class.grid_status import GridState
import math

class Pose():
    def __init__(self, x, y) -> None:
        self._x = x
        self._y = y

    def __eq__(self, other) -> bool:
        return self._x == other._x and self._y == other._y

# @total_ordering
class Cell():
    '''
    The class is the node in a graph
    '''
    _hand_length = 0
    _diameter = 0
    _hand_width = 5
    _GridColorMap = {GridState.SRC: 'green',
                    GridState.DEST: 'red',
                    GridState.UNVISITED: 'white',
                    GridState.VISITED: 'gray',
                    GridState.SEEN: 'yellow',
                    GridState.OCCUPIED: 'black',
                    GridState.PATH: 'blue'}

    def __init__(self, x, y, r, c, state = GridState.UNVISITED, cost = math.inf) -> None:
        self._x = x
        self._y = y
        self._r = r
        self._c = c
        self._state = state
        self._g = cost
        self._pred = None
        self.connected = []
    
    @property
    def r(self):
        return self._r
    
    @property
    def c(self):
        return self._c

    @property
    def g(self):
        return self._g
    
    @g.setter
    def g(self, val):
        self._g = val

    def __eq__(self, other):
        return self.g == other.g
    
    def __lt__(self, other):
        return self.g < other.g

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state):
        self._state = state
    
    @property
    def pred(self):
        return self._pred
    
    @pred.setter
    def pred(self, p):
        self._pred = p

    # x, y is for plotting purpose
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, y):
        self._y = y
    
    def __str__(self):
        return f"POS: ({self._x},{self._y}), -> ({self._r}, {self._c}), STATE: {self._state}"
    
    def relax(self, potential_pred):
        # print(f"relax {self} and {dest} {self.r - dest.r} {self.c - dest.c} and h {h}")
        self.g = min(self.g, potential_pred.g + 1)
        if self.g == potential_pred.g + 1:
            self.pred = potential_pred

    @property
    def pose(self):
        return Pose(self._r, self._c)
    
    def reset(self):
        self._g = math.inf
        self._state = GridState.UNVISITED
        self.connected.clear()    

class CellLFAStar(Cell):
    def __init__(self, x, y, r, c, state=GridState.UNVISITED, cost=math.inf) -> None:
        super().__init__(x, y, r, c, state, cost)
        self._rhs = math.inf
    
    @property
    def rhs(self):
        return self._rhs
    
    @rhs.setter
    def rhs(self, val):
        self._rhs = val

    def k1(self):
        return min(self.g, self.rhs) + h(n, goal)
    
    def k2(self):
        return min(self.g, self.rhs)

    def __eq__(self, other):
        return self.k1() == other.k1() and self.k2() == other.k2()
    
    def __lt__(self, other):
        return self.k1() < other.k1() or (self.k1() == other.k1() and self.k2() < other.k2())