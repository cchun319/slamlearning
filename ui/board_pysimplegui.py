#!/usr/bin/env python3
import PySimpleGUI as sg
from PySimpleGUI import TIMEOUT_KEY
from enum import Enum
from threading import Event
from base_class.grid_status import GridState
from base_class.cell import Cell
from algorithm.planner_manager import PlanMeta
import numpy as np

### great reference: https://k3no.medium.com/build-a-maze-with-python-920ac2266fe7
# TODO: consolidate the naming style for class static variable, member variable
# class member function, internal function


class UiState(Enum):
    SELECT_SRC = 'SRC'
    SELECT_DEST = 'DEST'
    TOGGLE_OBSTABLE = 'TOGGLE'
    STANDBY = 'STANDBY'
    PLAN = 'PLAN'
    RESET = 'RESET'
    MAZE = 'MAZE'

class Board():
    def __init__(self, num_of_row, num_of_col, msg_q, grid_map, update_queue) -> None:
        sg.theme('DarkGrey5')
        self._width = num_of_col * 2 * (Cell._hand_length + Cell._diameter)
        self._height = num_of_row * 2 * (Cell._hand_length + Cell._diameter)
        self._state = UiState.STANDBY
        self.src = self.dest = self.toggle = self.plan = False
        self._update_queue = update_queue
        self._plan_meta = PlanMeta()
        self._plannar_flag = Event()
        self._method = "DIJK"
        self._msg_q = msg_q
        self._grid_map = grid_map        
    
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
    
    def setMode(self, mode):
        # TODO: raise execption if invalid mode
        self._state = UiState(mode)

    def drawConnect(self, cellA, cellB):
        midx, midy = (cellA.x + cellB.x) / 2, (cellA.y + cellB.y) / 2 
        theta = np.arctan2(midy - cellB.y, midx - cellB.x)

        # end pts: center vector + direction vector * radius, direction vector can be gotten by mid - center vector
        self._graph.draw_line((cellA.x + Cell._diameter * np.cos(theta + np.pi), cellA.y + Cell._diameter * np.sin(theta + np.pi)),
                              (cellB.x + Cell._diameter * np.cos(theta), cellB.y + Cell._diameter * np.sin(theta)), width = Cell._hand_width)        

    def drawCenter(self, cell_):
        self._graph.draw_circle((cell_.x, cell_.y), Cell._diameter, fill_color=Cell._GridColorMap[cell_.state], line_color='black')

    def drawCell(self, cell_):
        if cell_.state != GridState.OCCUPIED:
            for neighbor in cell_.connected:
                self.drawConnect(cell_, neighbor)
        self.drawCenter(cell_)

    def drawAll(self):
        for i in range(self._grid_map.height):
            for j in range(self._grid_map.width):
                self.drawCell(self._grid_map.get_cell(i, j))
    
    def pixel_to_index(self, val):
        c_id = int((val[0] + Cell._diameter) / (Cell._hand_length + Cell._diameter))
        r_id = int((val[1] + Cell._diameter) / (Cell._hand_length + Cell._diameter))
        if r_id %2 == 0 or c_id %2 == 0:
            return (-1, -1)

        return (int((c_id - 1) / 2), int((r_id - 1) / 2))
    
    def select(self, indices):
        if indices == (-1,-1):
            return
        
        c_id = indices[0]
        r_id = indices[1]
        if self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC]:
            new_state = GridState.DEST if self._state == UiState.SELECT_DEST else GridState.SRC
            self._grid_map.udpate_cell_state(r_id, c_id, new_state)
            self._update_queue.put(self._grid_map.get_cell(r_id, c_id))
            prev = self._plan_meta.udpate(self._grid_map.get_cell(r_id, c_id))
            if prev is not None:
                self._grid_map.udpate_cell_state(prev.r, prev.c, GridState.UNVISITED)
                self._update_queue.put(prev)
        elif self._state == UiState.TOGGLE_OBSTABLE:
            # should not toggle src or dest
            if self._grid_map.get_cell(r_id, c_id).state not in [GridState.SRC, GridState.DEST]:
                new_state = GridState.UNVISITED if self._grid_map.get_cell(r_id, c_id).state == GridState.OCCUPIED else GridState.OCCUPIED
                self._grid_map.udpate_cell_state(r_id, c_id, new_state)
                self._update_queue.put(self._grid_map.get_cell(r_id, c_id))
                # update neighbors
                # the new information should trikle into the plannar
                neighbors = self._grid_map.get_neighbor(r_id, c_id)
                for n in neighbors:
                    self._update_queue.put(self._grid_map.get_cell(n[0], n[1]))                        
        
        return

    def _plan(self):
        # TODO & THOUGHT: 
        # grid/status should be an critical resources which used by the UI Thread/ Planner thread
        # when plan is clicked, send the request to the planner thread 
        # update queue shall update the status of the UI
        # status update queue should update the status change by the UI
        if self._plan_meta.isGoodToPlan():
            self._msg_q.put(self._plan_meta)
        else:
            print("Not ready for plan")
    
    def _plan_done(self):
        pass
    
    def _reset(self):
        self._graph.erase()
        self._grid_map.reset()
        self._plan_meta.reset()

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
            event, values = self._window.read(timeout=100) # 100 ms
            if event in (None, 'Exit'):
                self._msg_q.put('Exit')
                break
            elif self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC, UiState.TOGGLE_OBSTABLE] and event == 'canvas':
                self.select(self.pixel_to_index(values[event]))
            elif self._state == UiState.PLAN:
                self._plan()
                self._state = UiState.STANDBY
            elif self._state == UiState.RESET:
                self._reset()
                self.drawAll()
                self._state = UiState.STANDBY
            elif self._state == UiState.MAZE:
                # TODO: add a connect all button or consolidate things here
                # self._grid_map.connect_all()
                self._grid_map.make_maze()
                self.drawAll()
                self._state = UiState.STANDBY
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
