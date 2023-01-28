#!/usr/bin/env python3
from i_planner import PlannerInterface, PlannerType, PlanStatus
from queue import PriorityQueue
from grid_status import GridState
from board import MapInfo

class DIJKSTRA(PlannerInterface):
    def __init__(self):
        super().__init__()
    
    def plan(self):
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
        
        src.set_g(0)
        while not self._priority_queue.empty() and current_grid != dst:
            current_grid = self._priority_queue.get()
            current_grid.set_state(GridState.VISITED)
            neighbors = self.get_neighbors(current_grid)
            for nei in neighbors:
                # nei might be already in the q, fastest way to update the g()?
                
                if nei.state() == GridState.UNVISITED:
                    nei.set_q(min(nei.g(), current_grid.g() + 1))
                    if nei.g() == current_grid.g() + 1:
                        nei.set_pred(current_grid)
                    self._priority_queue.put(nei)
        
        # Done, get the path if reach dst
        status = PlanStatus(current_grid == dst)
        while current_grid != src:
            status.add_node(current_grid)
            current_grid = current_grid.pred()
        
        return status

        
        
