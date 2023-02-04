#!/usr/bin/env python3
from grid_status import Grid, GridState

class MapInfo:
    def __init__(self, num_of_row, num_of_col) -> None:
        self._src = self._dest = None
        self._r = num_of_row
        self._c = num_of_col
    
    def is_valid_index(self, r, c):
        return r >= 0 and self._r > r and c >= 0 and self._c > c

    def is_src(self, grid):
        if grid is None or self._src is None:
            return False
        return self._src.id() == grid.id()
    
    def is_dest(self, grid):
        if grid is None or self._dest is None:
            return False
        return self._dest.id() == grid.id()
    
    def src(self):
        return self._src

    def dest(self):
        return self._dest
    
    def update_info(self, grid):
        if grid.state() == GridState.SRC:
            self._src = grid
        elif grid.state() == GridState.DEST:
            self._dest = grid

class GridMap:
    def __init__(self, num_of_row, num_of_col) -> None:
        self._board = [[Grid(j, i) for i in range(num_of_col)] for j in range(num_of_row)]
        self._map_info = MapInfo(num_of_row, num_of_col)
    
    def set_grid_index_state(self, row, col, state):
        if not self._map_info.is_valid_index(row, col):
            return False
        # can any state change arbitrarily?
        self._board[row][col].set_state(state)
        self._map_info.update_info(self._board[row][col])

    def set_grid_state(self, grid, state):
        self.set_grid_index_state(grid.id()[0], grid.id()[1], state)
        
    def get_grid_state(self, grid):
        return self.get_grid(grid[0], grid[1]).state()

    def get_grid(self, row, col):
        if not self._map_info.is_valid_index(row, col):
            return None
        
        return self._board[row][col]