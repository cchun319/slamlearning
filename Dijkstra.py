#!/usr/bin/env python3
from i_planner import PlannerInterface, PlannerType, PlanStatus
from grid_status import GridState
from time import time, sleep

class Dijkstra(PlannerInterface):
    def __init__(self):
        super().__init__()
    
    def plan(self, grid_map, grid_queue, communicate):
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
        super().plan(grid_map)
        # need to make sure src and dest are assigned
        self._communicate = communicate
        grid_queue.put(self._map_info.src())
        grid_queue.put(self._map_info.dest())
        src = self._map_info.src()
        src.set_g(0)
        self._priority_queue.put(src)
        current_grid = None
        while not (self._priority_queue.empty() or self._map_info.is_dest(current_grid)):
            current_grid = self._priority_queue.get()
            # update the grid
            grid_map.set_grid_state(current_grid, GridState.VISITED)
            grid_queue.put(current_grid)
            # TODO: update the grid in the map
            neighbors = self.get_neighbors(current_grid)
            for nei in neighbors:
                # nei might be already in the q, fastest way to update the g()?
                if grid_map.get_grid_state(nei) != GridState.VISITED: # check if the grid is already visited in the map
                    neighbor = grid_map.get_grid(nei[0], nei[1])
                    neighbor.relax(current_grid)
                    neighbor.set_state(GridState.SEEN)
                    self._priority_queue.put(neighbor)
                    grid_queue.put(neighbor)

            self._communicate.sig.emit(10)
            input()

        # Done, get the path if reach dst
        status = PlanStatus(self._map_info.is_dest(current_grid))
        while current_grid != src:
            current_grid.set_state(GridState.PATH)
            status.add_node(current_grid)
            current_grid = current_grid.pred()
        
        return status

        
        
