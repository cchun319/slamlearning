#!/usr/bin/env python3

from enum import Enum
from functools import total_ordering
import math
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

class GridState(Enum):
    UNVISITED = 1 # white
    VISITED = 2 # 
    SEEN = 3 # 
    OCCUPIED = 4 # obstacle black
    SRC = 5 # green
    DEST = 6 # red
    PATH = 7
    LOCAL_OVERCONSISTENT = 8
    LOCAL_CONSITENT = 9
    LOCAL_UNDERCONSISTENT = 10

@total_ordering
class Grid(QTableWidgetItem):
    GridColorMap = {GridState.SRC: Qt.green,
                    GridState.DEST: Qt.red,
                    GridState.UNVISITED: Qt.white,
                    GridState.VISITED: Qt.gray,
                    GridState.SEEN: Qt.yellow,
                    GridState.OCCUPIED: Qt.black,
                    GridState.PATH: Qt.blue}
    def __init__(self, row, col, cost = math.inf):
        super().__init__()
        self._row = row
        self._col = col
        self._state = GridState.UNVISITED
        self._g = cost
        self._pred = None
    
    def id(self):
        return [self._row, self._col]

    def __eq__(self, other):
        return self.g() == other.g()
    
    def __lt__(self, other):
        return self.g() < other.g()

    def g(self):
        return self._g
    
    def set_g(self, g):
        self._g = g

    def h(self):
        return 0

    def pred(self):
        return self._pred
    
    def set_pred(self, pred):
        self._pred = pred

    def relax(self, potential_pred):
        # set pred if relaxed
        self.set_g(min(self.g(), potential_pred.g() + 1)) # TODO: this has to abstract, g + h
        if self.g() == potential_pred.g() + 1:
            self.set_pred(potential_pred)

    def set_state(self, state):
        self._state = state
        self.setBackground(Grid.GridColorMap[self._state])

    def state(self):
        return self._state
    
    def reset(self):
        self.__init__(self._row, self._col)

@total_ordering
class GridLFA(QTableWidgetItem):
    GridColorMap = {GridState.SRC: Qt.green,
                    GridState.DEST: Qt.red,
                    GridState.UNVISITED: Qt.white,
                    GridState.VISITED: Qt.gray,
                    GridState.SEEN: Qt.yellow,
                    GridState.OCCUPIED: Qt.black,
                    GridState.PATH: Qt.blue}
    def __init__(self, row, col, cost = math.inf):
        super().__init__()
        self._row = row
        self._col = col
        self._state = GridState.UNVISITED
        self._g = cost
        self._pred = None
    
    def k1(self):
        pass

    def k2(self):
        pass
    
    def rhs(self, other):
        '''
        look ahead value of other.g + d(self, other)
        '''
        pass

    def h(self):
        return 0

    def id(self):
        return [self._row, self._col]

    def __eq__(self, other):
        return self.k1() == other.k1() and self.k2() == other.k2()
    
    def __lt__(self, other):
        return self.k1() < other.k1() or self.k2() < other.k2()

    def g(self):
        return self._g
    
    def set_g(self, g):
        self._g = g

    def pred(self):
        return self._pred
    
    def set_pred(self, pred):
        self._pred = pred

    def relax(self, potential_pred):
        # set pred if relaxed
        self.set_g(min(self.g(), potential_pred.g() + 1)) # TODO: this has to abstract, g + h
        if self.g() == potential_pred.g() + 1:
            self.set_pred(potential_pred)

    def set_state(self, state):
        self._state = state
        self.setBackground(Grid.GridColorMap[self._state])

    def state(self):
        return self._state
    
    def reset(self):
        self.__init__(self._row, self._col)


