#!/usr/bin/env python3

from enum import Enum
from functools import total_ordering
import math
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
import abc

class GridState(Enum):
    UNVISITED = 1 # white
    VISITED = 2 # 
    SEEN = 3 # 
    OCCUPIED = 4 # obstacle black
    SRC = 5 # green
    DEST = 6 # red
    PATH = 7

class Point:
    def __init__(self, x, y) -> None:
        self._x = x
        self._y = y

    # TODO:
    def __str__(self) -> str:
        pass
    
    # TODO: https://stackoverflow.com/questions/1436703/what-is-the-difference-between-str-and-repr
    def __repr__(self) -> str:
        pass

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, val):
        self._x = val
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, val):
        self._y = val

    # TODO: 
    def __add__(self, other):
        return Point(self._x + other._x, self._y + other._y)
    
    def __sub__(self, other):
        return Point(self._x - other._x, self._y - other._y)
    
    def dist_to(self, other):
        pass

@total_ordering
class GridBase(abc.ABC):
    GridColorMap = {GridState.SRC: Qt.green,
                GridState.DEST: Qt.red,
                GridState.UNVISITED: Qt.white,
                GridState.VISITED: Qt.gray,
                GridState.SEEN: Qt.yellow,
                GridState.OCCUPIED: Qt.black,
                GridState.PATH: Qt.blue}
    def __init__(self, row, col, cost = math.inf) -> None:
        '''
        The grid must have
            - row, col -> indices
                - operation for indices, translation and rotation
            - comparator for different planning heuristics(what comes first)
            - walls?
            - predesucceor
            - g-value(current "distance" to the start)
            - rhs, a lookahead value based on the g-values of node's predecessors
                min(g(n') + d(n, n'), n': all possible predecessors) 
            - heuristic[optional]?
            - relax function[is this different for different planner?]
            - ? 
        '''
        self._pt = Point(row, col)
        self._state = GridState.UNVISITED
        self._g = cost
        self._pred = None
    
    @property
    def g(self):
        return self._g
    
    @g.setter
    def g(self, val):
        self._g = val
    
    @property
    def pred(self):
        return self._pred
    
    @pred.setter
    def pred(self, val):
        self._pred = val
    
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val
        self.setBackground(GridBase.GridColorMap[self._state])
    
    @abc.abstractmethod
    def __eq__(self, other):
        '''
        An advantage of abstract method over NotImplementedError is that you get an explicit Exception at instantiation time, not at method call time.
        '''
        pass
    
    @abc.abstractmethod
    def __lt__(self, other):
        pass

    @abc.abstractmethod
    def relax(self):
        pass


class GridDIJK(QTableWidgetItem, GridBase):
    def __init__(self, row, col, cost = math.inf):
        super().__init__(row, col, cost)
    
    def id(self):
        return [self._row, self._col]

    def __eq__(self, other):
        return self.g() == other.g()
    
    def __lt__(self, other):
        return self.g() < other.g()

    def set_heuristics(self, h):
        self._h = h

    def h(self, dst):
        if dst is None:
            return 1

        return (float(dst._row - self._row))**2 + (float(dst._col - self._col))**2

    def relax(self, potential_pred, dst = None):
        # set pred if relaxed
        self.g = min(self.g, potential_pred.g + self.h(dst)) # TODO: this has to abstract, g + h
        if self.g == (potential_pred.g + self.h(dst)):
            self.pred = potential_pred
    
    def reset(self):
        self.__init__(self._row, self._col)

'''
lifelong A*
    locally consistent
    underconsistent
    overconsistent
    k(n) = [k_1(n): min(g(n), h(n, dst) + rhs(n)), // -> f-value in A*
            k_2(n): min(g(n), rhs(n))]
    
    verify the search area
    like A* it doesn't gaurantee shortest path
'''
