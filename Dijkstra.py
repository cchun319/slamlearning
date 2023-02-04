#!/usr/bin/env python3
from i_planner import PlannerInterface, PlannerType, PlanStatus
from grid_status import GridState

class Dijkstra(PlannerInterface):
    def __init__(self):
        super().__init__()
    
    def plan(self, grid_map):
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
        src = self._map_info.src()
        src.set_g(0)
        self._priority_queue.put(src)
        current_grid = None
        while not (self._priority_queue.empty() or self._map_info.is_dest(current_grid)):
            current_grid = self._priority_queue.get()
            # update the grid
            grid_map.set_grid_state(current_grid, GridState.VISITED)
            # TODO: update the grid in the map
            neighbors = self.get_neighbors(current_grid)
            for nei in neighbors:
                # nei might be already in the q, fastest way to update the g()?
                if grid_map.get_grid_state(nei) != GridState.VISITED: # check if the grid is already visited in the map
                    neighbor = grid_map.get_grid(nei[0], nei[1])
                    neighbor.relax(current_grid)
                    self._priority_queue.put(neighbor)
        
        # Done, get the path if reach dst
        status = PlanStatus(self._map_info.is_dest(current_grid))
        while current_grid != src:
            status.add_node(current_grid)
            current_grid = current_grid.pred()
        
        return status

        
        
