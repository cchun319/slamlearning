#!/usr/bin/env python3
from base_class.grid_status import GridState
from base_class.plan_status import PlanStatus
import time
import heapq
import math

class Dijkstra():
    def __init__(self):
        self._priority_queue = []
        # every method has a queue sorted with some value -> H()
        # should be implemented

        # The grid should be share between UI and planner for the
        # spontaneous adding/canceling obstacles
        # 
        # 1. take deepcopy of 2d grid, flatten and sort(PQ) with the rhs
        # 2. plan
        # 3. if user toggles cells, add/remove free space
        #       toggle_queue, indicate the cell is freed/occupied
        #       -> update 2d grid(O(1)) and the cell in PQ(O(n))
        #           -> if was visited
        #           -> if was seen
        #           -> if was occupied 
    
    def plan(self, plan_meta, grid, update_queue, toggle_queue, reset_event):
        '''
        pseudo
            set g() of src to 0
            add src to the priority q
            while q is not empty and current standpoint is not dest
                set the current status to visited
                get neighors of current grid
                    update g() of the neighbors and set the predecessor
                    put the neighbor into the q if it's unvisited
                    what if it's already in the q? is it ok to have same grid in the q?
                            is it possible to do this in parallel manner?
                       P(g=5) ---> U
                                   ^
                                   |
                                   P(g=2)
        '''
        # need to make sure src and dest are assigned
        # circular action -> [plan -> move -> plan -> move ...]

        self._grid = grid
        self._plan_meta = plan_meta
        self._update_queue = update_queue
        self._toggle_queue = toggle_queue

        src = self._plan_meta.src
        src.g = 0
        heapq.heappush(self._priority_queue, (src.g, src))
        current_grid = None
        while len(self._priority_queue) != 0:
            current_grid = heapq.heappop(self._priority_queue)[1]
            if self._plan_meta.dest.pose == current_grid.pose:
                break

            if self._grid.get_cell(current_grid.r, current_grid.c).state == GridState.VISITED:
                continue

            # update current grid
            self._grid.udpate_cell_state(current_grid.r, current_grid.c, GridState.VISITED)
            self._update_queue.put(current_grid)

            for nei in self._grid.get_cell_neighbors(current_grid):
                if nei.state == GridState.VISITED:
                    continue

                nei.relax(current_grid)
                nei.state = GridState.SEEN
                heapq.heappush(self._priority_queue, (nei.g + math.sqrt(math.pow(nei.r - self._plan_meta.dest.r, 2) + math.pow(nei.c - self._plan_meta.dest.c, 2)), nei))
                self._update_queue.put(nei)
            
            # TODO: only sleep when visulization
            time.sleep(0.05)

        # Done, get the path if reach dst
        status = PlanStatus(current_grid.pose == self._plan_meta.dest.pose)
        while status.success and current_grid.pose != src.pose:
            status.add_node(current_grid)
            current_grid = current_grid.pred

        self._update_queue.put(status)

        return status.success

