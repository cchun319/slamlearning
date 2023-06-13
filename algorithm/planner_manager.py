#!/usr/bin/env python3
from enum import Enum
from algorithm.Dijk import Dijkstra
import time
from base_class.grid_status import GridState


class PlanMethod(Enum):
    DIJK = 'DIJK'
    A_STAR = 'A_STAR'

class PlanMeta():
    def __init__(self, method = PlanMethod.DIJK) -> None:
        self._src = self._dest = None
        self._method = method
    
    def isGoodToPlan(self):
        return self._src is not None and self._dest is not None
    
    def udpate(self, cell):
        if cell.state == GridState.SRC:
            ret = self._src
            self._src = cell
        elif cell.state == GridState.DEST:
            ret = self._dest
            self._dest = cell
        else:
            print("warning")
        return ret
    
    @property
    def src(self):
        return self._src
    
    @property
    def dest(self):
        return self._dest
    
    def __str__(self):
        return f"plan meta: source {self._src} | dest {self._dest} "
    
    def reset(self):
        self._src = self._dest = None        


class PlannerManager():
    @staticmethod
    def planner(method):
        if method == PlanMethod.DIJK:
            return Dijkstra()
        elif method == PlanMethod.A_STAR:
            return

    @staticmethod
    def run(msg_queue, update_queue, grid_map):
        while True:
            time.sleep(0.2)
            if msg_queue.qsize() > 0:
                s = msg_queue.get()
                print(f"received {s}")
                if s == 'Exit':
                    return 0
                elif isinstance(s, PlanMeta):
                    '''
                    event: flag to inform the planing is done, means reaching the destination
                    plan_meta: has source and destnation grids
                    update_queue: thread safe queue which lets UI thread know when to update the grid 
                    grid is the snapshot
                    '''
                    planner = PlannerManager.planner(s._method)
                    planner.plan(s, grid_map, update_queue, None)
