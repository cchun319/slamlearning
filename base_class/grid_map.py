#!/usr/bin/env python3
from threading import Lock
from base_class.cell import Cell
import random
from base_class.grid_status import GridState



class GridMap():
    _offset = [[0, 1], 
            [1, 1],
            [1, 0],
            [1, -1],
            [0, -1],
            [-1, -1],
            [-1, 0],
            [-1, -1]]

    def __init__(self, num_of_row, num_of_col) -> None:
        self._mutex = Lock()

        self._num_of_row = num_of_row 
        self._num_of_col = num_of_col

        self.sanity()

        self._grid = []
        for r in range(self._num_of_row):
            r_list = []
            for c in range(self._num_of_col):
                r_list.append(Cell((2 * c + 1) * (Cell._hand_length + Cell._diameter), (2 * r + 1) * (Cell._hand_length + Cell._diameter), r, c))
            self._grid.append(r_list)

    def sanity(self):
        assert self._num_of_row > 0 and self._num_of_col > 0

    def get_cell(self, r, c):
        return self._grid[r][c]

    def update_cell(self, r, c, cell):
        self._mutex.acquire()
        self._grid[r][c] = cell
        self._mutex.release()

    def udpate_cell_state(self, r, c, grid_state):
        self._mutex.acquire()
        self._grid[r][c].state = grid_state
        self._mutex.release()
    
    def reset(self):
        for r in range(self._num_of_row):
            for c in range(self._num_of_col):
                self._grid[r][c].reset()
                
    @property
    def height(self):
        return self._num_of_row
    
    @property
    def width(self):
        return self._num_of_col
    
    def connect_cell(self, r1, c1, r2, c2):
        self.get_cell(r1, c1).connected.append(self.get_cell(r2, c2))
        self.get_cell(r2, c2).connected.append(self.get_cell(r1, c1))
    
    def is_valid_id(self, r, c):
        return r >= 0 and c >= 0 and c < self.width and r < self.height
    
    def get_neighbor(self, r, c):
        # TODO: neighbor and direction should be hooked
        neighbors = []
        for offset in GridMap._offset:
            neighbor_r = r + offset[0]
            neighbor_c = c + offset[1]
            if self.is_valid_id(neighbor_r, neighbor_c):
                neighbors.append((neighbor_r, neighbor_c)) 
        return neighbors

    def make_maze(self):
        '''num_of_group = w * h
        while num_of_group != 1:
            random pick (i, j)
            random pick (a, b)
            check if they are same group, can also do reduce layer btw

            if same, drop
            else
            merge two group
                num_of_group - 1
        '''
        num_of_group = self.height * self.width 
        # for minimum spanning tree, minimum number of edge is num of cells - 1
        # it needs some redundent edges to ensure dest and src are connected

        parent = [-1] * num_of_group 
        # -1: means they are their own parent

        def in_same_group(id1, id2, parent):
            if id1 == id2:
                return True
            
            if parent[id1] < 0:
                parent[id1] = id1

            if parent[id2] < 0:
                parent[id2] = id2
            
            if parent[id1] != id1 and parent[id2] != id2:
                return in_same_group(parent[id1], parent[id2], parent)
            elif parent[id1] != id1:
                return in_same_group(parent[id1], id2, parent)
            elif parent[id2] != id2:
                return in_same_group(id1, parent[id2], parent) 

            return parent[id1] == parent[id2]

        def get_parent(id, parent):
            if id != parent[id]:             
                return get_parent(parent[id], parent)
            return id

        while num_of_group != 1:
            '''
            scenario of testing LFA*
            1. set src and dest
            2. plan and move current grid
            3. while the current grid is moving
            4. randomly close/open the routes on the path
            5. the graph may or may not connected, either way, planner should report the status with brief discription
                1. plan sucess -> current grid reaches the dest
                2. plan fail -> not conneted
                                current grid doesn't reach the dest


            after all cells are connected
            1. open more routes for cells
            '''
            g1r = random.randint(0, self.height - 1)
            g1c = random.randint(0, self.width - 1)

            id1 = g1r * self.width + g1c

            neighbors = self.get_neighbor(g1r, g1c)
            random.shuffle(neighbors)
            for n in neighbors:
                if not in_same_group(id1, n[0] * self.width + n[1], parent):
                    parent[get_parent(n[0] * self.width + n[1], parent)] = id1
                    self.connect_cell(n[0], n[1], g1r, g1c)
                    num_of_group -= 1
            
            # print(f"parent {parent}")
        
        return
    
    def connect_all(self): 
        for r in range(self._num_of_row):
            for c in range(self._num_of_col):
                neighbors = self.get_neighbor(r, c)
                for n in neighbors:
                    self.connect_cell(n[0], n[1], r, c)


    

        