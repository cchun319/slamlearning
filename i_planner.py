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
    def __init__(self, map_info): 
        self._priority_queue = PriorityQueue()
        self._map_info = map_info
        pass

    def plan(self):
        pass

    def get_neighbors(self):
        pass

    def relax(self):
        pass