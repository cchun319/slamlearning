#!/usr/bin/env python3
import PySimpleGUI as sg
import numpy as np
from enum import Enum
import queue
from threading import Thread, Event
# from algorithm.planer_manager import PlanerManager
### great reference: https://k3no.medium.com/build-a-maze-with-python-920ac2266fe7

class PlanMeta():
    def __init__(self) -> None:
        self._src = self._dest = None
    
    def isGoodToPlan(self):
        return self._src is not None and self._dest is not None
    
    def udpate(self, cell):
        if cell.state == GridState.SRC:
            ret = self._src
            self._src = cell
        elif cell.state == GridState.DEST:
            ret = self._dest
            self._dest = cell
        else:
            print("warning")
        return ret

        

class GridState(Enum):
    UNVISITED = 1 # white
    VISITED = 2 # 
    SEEN = 3 # 
    OCCUPIED = 4 # obstacle black
    SRC = 5 # green
    DEST = 6 # red
    PATH = 7

class UiState(Enum):
    SELECT_SRC = 'SRC'
    SELECT_DEST = 'DEST'
    TOGGLE_OBSTABLE = 'TOGGLE'
    STANDBY = 'STANDBY'
    PLAN = 'PLAN'

class cell():
    _hand_length = 0
    _diameter = 0
    _hand_width = 5
    _GridColorMap = {GridState.SRC: 'green',
                    GridState.DEST: 'red',
                    GridState.UNVISITED: 'white',
                    GridState.VISITED: 'gray',
                    GridState.SEEN: 'yellow',
                    GridState.OCCUPIED: 'black',
                    GridState.PATH: 'blue'}
    _offset = [1, 0, -1, 0]
    def __init__(self, x, y, r, c, state = GridState.UNVISITED) -> None:
        self._x = x
        self._y = y
        self._r = r
        self._c = c
        self._state = state

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state):
        self._state = state 

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, y):
        self._y = y
    
    @staticmethod
    def direction():
        return [[0,  cell._diameter, 0,  cell._hand_length + cell._diameter],
                   [0, -cell._diameter, 0, -cell._hand_length - cell._diameter],
                   [cell._diameter, 0, cell._diameter + cell._hand_length, 0],
                   [-cell._diameter, 0, -cell._diameter -cell._hand_length, 0]]
    
    def __str__(self):
        return f"POS: ({self._x},{self._y}), STATE: {self._state}"
    
    def get_neighbor(self):
        # TODO: neighbor and direction should be hooked
        neighbors = []
        cid = 1
        for i in range(len(cell._offset)):
           neighbors.append((self._r + cell._offset[i], self._c + cell._offset[cid % len(cell._offset)])) 
           cid += 1
        return neighbors
    

class board():
    def __init__(self, num_of_row, num_of_col, l = 20, d = 12) -> None:
        sg.theme('DarkGrey5')
        cell._diameter = d
        cell._hand_length = l
        self._width = num_of_col * 2 * (cell._hand_length + cell._diameter)
        self._height = num_of_row * 2 * (cell._hand_length + cell._diameter)
        self._direction = cell.direction()
        self._state = UiState.STANDBY
        self.src = self.dest = self.toggle = self.plan = False
        self.update_queue = queue.Queue()
        self._plan_meta = PlanMeta()
        self._plannar_flag = Event()
        self._method = "DIJK"
        
    
        layout = [[sg.Graph((self._width, self._height),(0,0), (self._width, self._height),
                            background_color='white',
                            key='canvas', enable_events=True)],
                [sg.Exit(),
                 sg.Button('SRC', size=(5, 1), button_color='white on green', key = lambda: self.setMode('SRC')),
                 sg.Button('DEST', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('DEST')),
                 sg.Button('TOGGLE', size=(6, 1), button_color='white on green',key = lambda: self.setMode('TOGGLE')),
                 sg.Button('PLAN', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('PLAN')),
                 sg.Button('MAZE', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('MAZE'))]]

        self._window = sg.Window('GridMaker',
                                    layout, resizable=True, finalize=True)
        self._graph = self._window['canvas']
        self._grid = []
        for r in range(num_of_row):
            r_list = []
            for c in range(num_of_col):
                r_list.append(cell((2 * c + 1) * (cell._hand_length + cell._diameter), (2 * r + 1) * (cell._hand_length + cell._diameter), r, c))
            self._grid.append(r_list)
    
    def setMode(self, mode):
        # TODO: raise execption if invalid mode
        self._state = UiState(mode)
    
    def placeCell(self, cell_):
        ids = self.pos_to_index((cell_.x, cell_.y))
        self._grid[ids[0]][ids[1]] = cell_

    def drawHand(self, cell_, offset):
        x_start = cell_.x + offset[0]
        y_start = cell_.y + offset[1]
        x_end = cell_.x + offset[2]
        y_end = cell_.y + offset[3]
        if x_end <= 0 or x_end >= self._width or y_end <= 0 or y_end >= self._height:
            return
        self._graph.draw_line((x_start, y_start), (x_end, y_end), width = cell._hand_width)


    def drawCenter(self, cell_):
        self._graph.draw_circle((cell_.x, cell_.y), cell._diameter, fill_color=cell._GridColorMap[cell_.state], line_color='black')

    def drawCell(self, cell_):
        if cell_.state != GridState.OCCUPIED:
            for offset in self._direction:
                self.drawHand(cell_, offset)
        self.drawCenter(cell_)

    def drawAll(self):
        for i in range(len(self._grid)):
            for j in range(len(self._grid[0])):
                self.drawCell(self._grid[i][j])
    
    def pos_to_index(self, val):
        c_id = int((val[0] + cell._diameter)/ (cell._hand_length + cell._diameter))
        r_id = int((val[1] + cell._diameter)/ (cell._hand_length + cell._diameter))
        if r_id %2 == 0 or c_id %2 == 0:
            return (-1, -1)

        return (int((c_id - 1) / 2), int((r_id - 1) / 2))
    
    def select(self, indices):
        if indices == (-1,-1):
            return
        
        c_id = indices[0]
        r_id = indices[1]
        if self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC]:
            self._grid[r_id][c_id].state = GridState.DEST if self._state == UiState.SELECT_DEST else GridState.SRC
            self.update_queue.put(self._grid[r_id][c_id])
            prev = self._plan_meta.udpate(self._grid[r_id][c_id])
            if prev is not None:
                prev.state = GridState.UNVISITED
                self.placeCell(prev)
                self.update_queue.put(prev)
        elif self._state == UiState.TOGGLE_OBSTABLE:
            # should not toggle src or dest
            if self._grid[r_id][c_id].state not in [GridState.SRC, GridState.DEST]:
                self._grid[r_id][c_id].state = GridState.UNVISITED if self._grid[r_id][c_id].state == GridState.OCCUPIED else GridState.OCCUPIED           
                self.update_queue.put(self._grid[r_id][c_id])
                # update neighbors
                # the new information should trikle into the plannar
                neighbors = self._grid[r_id][c_id].get_neighbor()
                for n in neighbors:
                    if n[0] >= 0 and n[1] >= 0 and n[1] < len(self._grid[0]) and n[0] < len(self._grid):
                        self.update_queue.put(self._grid[n[0]][n[1]])                        
        
        return

    def _plan(self):
        self._planner = Thread(target=PlanerManager.plan, args=(self._method, self._plannar_flag, self.update_queue, self._grid))
        self._planner.start()
    
    def _plan_done(self):
        print("plan done close thread")
        self._planner.join()

    def run(self):
        # TODO: Hook up to the button and ctrl-c

        self.drawAll()
        while True:
            while self.update_queue.qsize() > 0:
                self.drawCell(self.update_queue.get())
            if self._plannar_flag.is_set():
                self._plan_done()
                self._plannar_flag.clear()
            event, values = self._window.read()
            # print(f"{event} : {values}")
            if event in (None, 'Exit'):
                break
            if self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC, UiState.TOGGLE_OBSTABLE] and event == 'canvas':
                self.select(self.pos_to_index(values[event]))
            if self._state == UiState.PLAN:
                self._plan()
            if callable(event):
                event()
        self._window.close()


def main():
    '''
    interactive mode
    select src, dest, toggle on/off obstacles
    maze creator
    '''
    b = board(15, 20)
    b.run()

if __name__ == "__main__":
    main()
