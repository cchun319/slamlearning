#!/usr/bin/env python3
from base_class.grid_status import GridState
import queue

class PlanStatus:
    def __init__(self, succeed) -> None:
        self._path = []
        self._plan_succeed = succeed
    
    def success(self):
        return self._plan_succeed
    
    def add_node(self, node):
        self._path.insert(0, node)
    
    def path(self):
        return self._path

class Dijkstra():
    def __init__(self, plan_meta, grid, update_queue, toggle_queue):
        self._grid = grid
        self._plan_meta = plan_meta
        self._update_queue = update_queue
        self._toggle_queue = toggle_queue
        self._priority_queue = queue.PriorityQueue()
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
        # need to make sure src and dest are assigned
        src = self._plan_meta.src
        src.g = 0
        self._priority_queue.put(src)
        current_grid = None
        while not self._priority_queue.empty():
            current_grid = self._priority_queue.get()
            if self._plan_meta.dest.pose == current_grid.pose:
                break

            # update current grid
            self._grid[current_grid.r][current_grid.c].state = GridState.VISITED
            self._update_queue.put(current_grid)
            # TODO: update the grid in the map
            neighbors = current_grid.get_neighbor()
            for nei in neighbors:
                # nei might be already in the q, fastest way to update the g()?
                # check valid index
                if nei[0] < 0 or nei[1] < 0 or nei[0] >= len(self._grid) or nei[1] >= len(self._grid[1]) or \
                    self._grid[nei[0]][nei[1]].state == GridState.VISITED:
                    continue

                neighbor = self._grid[nei[0]][nei[1]]
                neighbor.relax(current_grid)
                neighbor.state = GridState.SEEN
                self._priority_queue.put(neighbor)
                # wait for evaluating
                self._update_queue.put(neighbor)
                # visualization

        # Done, get the path if reach dst
        status = PlanStatus(current_grid.pose == self._plan_meta.dest.pose)
        while status.success and current_grid.pose != src.pose:
            current_grid.state = GridState.PATH
            status.add_node(current_grid)
            current_grid = current_grid.pred

        return status

