#!/usr/bin/env python3
from enum import Enum
from algorithm.Dijk import Dijkstra


class PlanMethod(Enum):
    DIJK = 'DIJK'
    A_STAR = 'A_STAR'


class PlannerManager():
    @staticmethod
    def planner(method, grid, plan_meta, update_queue, toggle_queue):
        plan_method = PlanMethod(method)
        if plan_method == PlanMethod.DIJK:
            return Dijkstra(plan_meta, grid, update_queue, toggle_queue)
        elif plan_method == PlanMethod.A_STAR:
            return


    @staticmethod
    def plan(method, event, plan_meta, update_queue, grid, toggle_queue):
        '''
        event: flag to inform the planing is done, means reaching the destination
        plan_meta: has source and destnation grids
        update_queue: thread safe queue which lets UI thread know when to update the grid 
        grid is the snapshot
        '''
        planner = PlannerManager.planner(method, grid, plan_meta, update_queue, toggle_queue)
        plan_result = planner.plan()
        # while success:
        #     moveToDest(path)
        # plan function shall keep updating   the grid status
        # toggle on/off occupied grids could happen during plan/move
        event.set()
        # event should be set only when reaching the dest/ dead end
