#!/usr/bin/env python3
from enum import Enum

class PlannerType(Enum):
    DIJKSTRA = 1
    A_STAR = 2
    D_STAR = 3
    D_STAR_LITE = 4
    RRT = 5

class PlannerInterface:
    def __init__(self): 
        pass

    def plan(self):
        pass

    def get_neighbors(self):
        pass