#!/usr/bin/env python3
from threading import Lock
from base_class.cell import Cell
import random
from base_class.grid_status import GridState
import math

class GridMap():
    # 8 connected cells
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
        
        self.edge_map = {}
        # key: node index, value: list of connected neighbors
    
    def indices_to_id(self, r, c):
        return r * self.width + c
    
    def id_to_indices(self, id):
        return int(id / self.width), int(id % self.width)
    
    def add_edge(self, r1, c1, r2, c2):
        # O(n)
        if self.indices_to_id(r1, c1) not in self.edge_map:
            self.edge_map[self.indices_to_id(r1, c1)] = []
        if self.indices_to_id(r2, c2) not in self.edge_map:
            self.edge_map[self.indices_to_id(r2, c2)] = []    
        # print(f"id {self.indices_to_id(r1, c1)} connects to {self.edge_map[self.indices_to_id(r1, c1)]} : to add {self.indices_to_id(r2, c2)}")
        self.edge_map[self.indices_to_id(r1, c1)].append(self.indices_to_id(r2, c2))
        self.edge_map[self.indices_to_id(r2, c2)].append(self.indices_to_id(r1, c1))
        # print(f"id {self.indices_to_id(r1, c1)} connects to {self.edge_map[self.indices_to_id(r1, c1)]} : after added {self.indices_to_id(r2, c2)}")

    def remove_edge(self, r1, c1, r2, c2):
        # print(f"id {self.indices_to_id(r1, c1)} connects to {self.edge_map[self.indices_to_id(r1, c1)]} : to remove {self.indices_to_id(r2, c2)}")
        self.edge_map[self.indices_to_id(r1, c1)].remove(self.indices_to_id(r2, c2))
        self.edge_map[self.indices_to_id(r2, c2)].remove(self.indices_to_id(r1, c1))
        # print(f"id {self.indices_to_id(r1, c1)} connects to {self.edge_map[self.indices_to_id(r1, c1)]} : after remove {self.indices_to_id(r2, c2)}")
    
    def remove_cell_edge(self, cell1, cell2):
        self.remove_edge(cell1.r, cell1.c, cell2.r, cell2.c)
    
    def get_cell_neighbors_id(self, cell_):
        return self.get_neighbors(cell_.r, cell_.c)
    
    def get_cell_neighbors(self, cell_):
        ret = []
        for id in self.get_cell_neighbors_id(cell_):
            r, c = self.id_to_indices(id)
            ret.append(self.get_cell(r, c))
        return ret
    
    def has_edge(self, r1, c1, r2, c2):
        return self.indices_to_id(r2, c2) in self.edge_map[self.indices_to_id(r1, c1)]
    
    def get_neighbors(self, r, c):
        return self.edge_map[self.indices_to_id(r, c)] if self.indices_to_id(r, c) in self.edge_map else []

    def sanity(self):
        assert self._num_of_row > 0 and self._num_of_col > 0

    def get_cell(self, r, c):
        return self._grid[r][c]

    def update_cell(self, r, c, cell):
        self._mutex.acquire()
        self._grid[r][c] = cell
        self._mutex.release()

    def update_cell_state(self, cell_, grid_state):
        self.udpate_cell_state(cell_.r, cell_.c, grid_state)

    def udpate_cell_state(self, r, c, grid_state):
        self._mutex.acquire()
        self._grid[r][c].state = grid_state
        self._mutex.release()
    
    def reset(self):
        self.edge_map = {}
        for r in range(self._num_of_row):
            for c in range(self._num_of_col):
                self._grid[r][c].reset()        
                
    @property
    def height(self):
        return self._num_of_row
    
    @property
    def width(self):
        return self._num_of_col
    
    def is_valid_id(self, r, c):
        return r >= 0 and c >= 0 and c < self.width and r < self.height
    
    def get_potential_neighbors_cells(self, cell_):
        return self.get_potential_neighbors(cell_.r, cell_.c, True)
    
    def get_potential_neighbors(self, r, c, is_cell=False):
        # TODO: neighbor and direction should be hooked
        neighbors = []
        for offset in GridMap._offset:
            neighbor_r = r + offset[0]
            neighbor_c = c + offset[1]
            if self.is_valid_id(neighbor_r, neighbor_c):
                if is_cell:
                    neighbors.append(self.get_cell(neighbor_r, neighbor_c))
                else:
                    neighbors.append((neighbor_r, neighbor_c)) 
        return neighbors
    
    def get_edge_cost(self, r, c):
        '''
        if connected -> 1, else inf
        '''
        return math.inf

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
            after all cells are connected
            1. open more routes for cells
            '''
            g1r = random.randint(0, self.height - 1)
            g1c = random.randint(0, self.width - 1)

            id1 = g1r * self.width + g1c

            neighbors = self.get_potential_neighbors(g1r, g1c)
            random.shuffle(neighbors)
            for n in neighbors:
                if not in_same_group(id1, n[0] * self.width + n[1], parent):
                    parent[get_parent(n[0] * self.width + n[1], parent)] = id1
                    self.add_edge(n[0], n[1], g1r, g1c)
                    num_of_group -= 1
            
            # print(f"parent {parent}")
        
        return True
    
    def connect_all(self): 
        for r in range(self._num_of_row):
            for c in range(self._num_of_col):
                neighbors = self.get_potential_neighbors(r, c)
                for n in neighbors:
                    self.add_edge(n[0], n[1], r, c)


    

        