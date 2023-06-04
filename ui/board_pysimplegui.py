#!/usr/bin/env python3
import PySimpleGUI as sg
from PySimpleGUI import TIMEOUT_KEY
import numpy as np
from enum import Enum
import queue
from threading import Thread, Event
from base_class.grid_status import GridState
from base_class.cell import Cell
from algorithm.planner_manager import PlannerManager
import copy

### great reference: https://k3no.medium.com/build-a-maze-with-python-920ac2266fe7
# TODO: consolidate the naming style for class static variable, member variable
# class member function, internal function


class PlanMeta():
    def __init__(self) -> None:
        self._src = self._dest = None
    
    def isGoodToPlan(self):
        return self._src is not None and self._dest is not None
    
    def udpate(self, cell):
        if cell.state == GridState.SRC:
            ret = self._src
            self._src = cell
            print(f"SRC {self._src}")
        elif cell.state == GridState.DEST:
            ret = self._dest
            self._dest = cell
            print(f"DEST {self._dest}")
        else:
            print("warning")
        return ret
    
    @property
    def src(self):
        return self._src
    
    @property
    def dest(self):
        return self._dest


class UiState(Enum):
    SELECT_SRC = 'SRC'
    SELECT_DEST = 'DEST'
    TOGGLE_OBSTABLE = 'TOGGLE'
    STANDBY = 'STANDBY'
    PLAN = 'PLAN'
    RESET = 'RESET'

class Board():
    def __init__(self, num_of_row, num_of_col, l = 20, d = 12) -> None:
        sg.theme('DarkGrey5')
        Cell._diameter = d
        Cell._hand_length = l
        self._width = num_of_col * 2 * (Cell._hand_length + Cell._diameter)
        self._height = num_of_row * 2 * (Cell._hand_length + Cell._diameter)
        self._direction = Cell.direction()
        self._state = UiState.STANDBY
        self.src = self.dest = self.toggle = self.plan = False
        self._update_queue = queue.Queue()
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
                 sg.Button('MAZE', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('MAZE')), 
                 sg.Button('RESET', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('RESET'))]]

        self._window = sg.Window('GridMaker',
                                    layout, resizable=True, finalize=True)
        self._graph = self._window['canvas']
        self._grid = []
        for r in range(num_of_row):
            r_list = []
            for c in range(num_of_col):
                r_list.append(Cell((2 * c + 1) * (Cell._hand_length + Cell._diameter), (2 * r + 1) * (Cell._hand_length + Cell._diameter), r, c))
            self._grid.append(r_list)
    
    def setMode(self, mode):
        # TODO: raise execption if invalid mode
        self._state = UiState(mode)
    
    def placeCell(self, cell_):
        ids = self.pos_to_index((cell_.x, cell_.y))
        self._grid[ids[1]][ids[0]] = cell_

    def drawHand(self, cell_, offset):
        x_start = cell_.x + offset[0]
        y_start = cell_.y + offset[1]
        x_end = cell_.x + offset[2]
        y_end = cell_.y + offset[3]
        if x_end <= 0 or x_end >= self._width or y_end <= 0 or y_end >= self._height:
            return
        self._graph.draw_line((x_start, y_start), (x_end, y_end), width = Cell._hand_width)


    def drawCenter(self, cell_):
        self._graph.draw_circle((cell_.x, cell_.y), Cell._diameter, fill_color=Cell._GridColorMap[cell_.state], line_color='black')

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
        c_id = int((val[0] + Cell._diameter)/ (Cell._hand_length + Cell._diameter))
        r_id = int((val[1] + Cell._diameter)/ (Cell._hand_length + Cell._diameter))
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
            self._update_queue.put(self._grid[r_id][c_id])
            prev = self._plan_meta.udpate(self._grid[r_id][c_id])
            if prev is not None:
                prev.state = GridState.UNVISITED
                self.placeCell(prev)
                self._update_queue.put(prev)
        elif self._state == UiState.TOGGLE_OBSTABLE:
            # should not toggle src or dest
            if self._grid[r_id][c_id].state not in [GridState.SRC, GridState.DEST]:
                self._grid[r_id][c_id].state = GridState.UNVISITED if self._grid[r_id][c_id].state == GridState.OCCUPIED else GridState.OCCUPIED           
                self._update_queue.put(self._grid[r_id][c_id])
                # update neighbors
                # the new information should trikle into the plannar
                neighbors = self._grid[r_id][c_id].get_neighbor()
                for n in neighbors:
                    if n[0] >= 0 and n[1] >= 0 and n[1] < len(self._grid[0]) and n[0] < len(self._grid):
                        self._update_queue.put(self._grid[n[0]][n[1]])                        
        
        return

    def _plan(self):
        # TODO & THOUGHT: 
        # grid/status should be an critical resources which used by the UI Thread/ Planner thread
        # when plan is clicked, send the request to the planner thread 
        # update queue shall update the status of the UI
        # status update queue should update the status change by the UI
        self._planner = Thread(target=PlannerManager.plan, args=(self._method,
                                                                 self._plannar_flag,
                                                                 self._plan_meta,
                                                                 self._update_queue,
                                                                 self._grid, # TODO: adding deepcopy of this hang 
                                                                 None))
        self._planner.start()
    
    def _plan_done(self):
        self._planner.join()
    
    def _reset(self):
        for i in range(len(self._grid)):
            for j in range(len(self._grid[0])):
                self._grid[i][j].state = GridState.UNVISITED
                self.drawCell(self._grid[i][j])

    def run(self):
        # TODO: Hook up to the button and ctrl-c
        # TODO: not kill properly
        # TODO: plot should be another thread, planner should be one thread
        # TODO: 

        self.drawAll()
        while True:
            while self._update_queue.qsize() > 0:
                self.drawCell(self._update_queue.get())
            if self._plannar_flag.is_set():
                self._plan_done()
                self._plannar_flag.clear()
                self._state = UiState.STANDBY
            event, values = self._window.read(timeout=100) # 100 ms
            # print(f"{event} : {values}")
            if event in (None, 'Exit'):
                break
            elif self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC, UiState.TOGGLE_OBSTABLE] and event == 'canvas':
                self.select(self.pos_to_index(values[event]))
            elif self._state == UiState.PLAN:
                self._plan()
            elif self._state == UiState.RESET:
                self._reset()
            elif callable(event):
                event()
        self._window.close()


def main():
    '''
    interactive mode
    select src, dest, toggle on/off obstacles
    maze creator
    '''
    b = Board(15, 10)
    b.run()

if __name__ == "__main__":
    main()