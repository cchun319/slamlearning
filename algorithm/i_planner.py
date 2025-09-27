#!/usr/bin/env python3
from enum import Enum
from queue import PriorityQueue
from PyQt5.QtCore import QObject, pyqtSignal, QObject, QThread


class PlannerType(Enum):
    DIJKSTRA = 1
    A_STAR = 2
    D_STAR = 3
    D_STAR_LITE = 4
    RRT = 5

class PlannerInterface(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    steps = [[1,0], [0,1], [-1,0], [0,-1]]
    def __init__(self, grid_map): 
        super().__init__()
        self._priority_queue = PriorityQueue()
        self._map_info = grid_map._map_info
        self._run = True
    def plan(self):
        pass

    def get_neighbors(self, grid):
        ret = []
        for step in PlannerInterface.steps:
            r = grid.id()[0] + step[0]
            c = grid.id()[1] + step[1]
            if(self._map_info.is_valid_index(r, c)):
                ret.append([r, c])
            
        return ret
    
    def terminate(self):
        self._run = False
    
    def running(self):
        return self._run