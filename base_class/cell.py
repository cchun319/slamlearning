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

@total_ordering
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
    _offset = [1, 0, -1, 0]
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
    
    def get_neighbor(self):
        # TODO: neighbor and direction should be hooked
        neighbors = []
        cid = 1
        for i in range(len(Cell._offset)):
           neighbors.append((self._r + Cell._offset[i], self._c + Cell._offset[cid % len(Cell._offset)])) 
           cid += 1
        return neighbors
    
    def relax(self, potential_pred, dest):
        h = math.pow(self.r - dest.r, 2) + math.pow(self.c - dest.c, 2)
        # print(f"relax {self} and {dest} {self.r - dest.r} {self.c - dest.c} and h {h}")
        self.g = min(self.g, potential_pred.g + 1 + h) # TODO: this has to be abstract, g + h and how to pass dest information
        if self.g == potential_pred.g + 1 + h:
            self.pred = potential_pred

    @property
    def pose(self):
        return Pose(self._r, self._c)
    
    def reset(self):
        self._g = math.inf
        self._state = GridState.UNVISITED
        self.connected.clear()    

class CellAStar(Cell):
    def __init__(self, x, y, r, c, state=GridState.UNVISITED, cost=math.inf) -> None:
        super().__init__(x, y, r, c, state, cost)
    
    def heuristic(self):
        # TODO: it needs the visibilities to the dest
        # and call by g function
        return 