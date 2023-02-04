#!/usr/bin/env python3
from enum import Enum
from queue import PriorityQueue


class PlannerType(Enum):
    DIJKSTRA = 1
    A_STAR = 2
    D_STAR = 3
    D_STAR_LITE = 4
    RRT = 5

class PlanStatus:
    def __init__(self, succeed) -> None:
        self._path = []
        self._plan_succeed = succeed
    
    def add_node(self, node):
        self._path.insert(0, node)

class PlannerInterface:
    steps = [[1,0], [0,1], [-1,0], [0,-1]]
    def __init__(self): 
        self._priority_queue = PriorityQueue()

    def plan(self, grid_map):
        self._map_info = grid_map._map_info

    def get_neighbors(self, grid):
        ret = []
        for step in PlannerInterface.steps:
            r = grid.id()[0] + step[0]
            c = grid.id()[1] + step[1]
            if(self._map_info.is_valid_index(r, c)):
                ret.append([r, c])
            
        return ret