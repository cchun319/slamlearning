#!/usr/bin/env python3

class MapInfo:
    def __init__(self) -> None:
        self._src = self._dest = None
    
    def is_src(self, grid):
        return self._src.id() == grid.id()
    
    def is_dest(self, grid):
        return self._dest.id() == grid.id()