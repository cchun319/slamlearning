#!/usr/bin/env python3
import PySimpleGUI as sg
from PySimpleGUI import TIMEOUT_KEY
from enum import Enum
from base_class.grid_status import GridState
from base_class.cell import Cell
from base_class.plan_status import PlanStatus
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
    def __init__(self, msg_q, grid_map, update_queue, toggle_queue, reset_event) -> None:
        sg.theme('DarkGrey5')
        self._grid_map = grid_map        
        self._width = self._grid_map.width * 2 * (Cell._hand_length + Cell._diameter)
        self._height = self._grid_map.height * 2 * (Cell._hand_length + Cell._diameter)
        self._state = UiState.STANDBY
        self.src = self.dest = self.toggle = self.plan = False
        self._update_queue = update_queue
        self._plan_meta = PlanMeta()
        self._msg_q = msg_q
        self._toggle_queue = toggle_queue
        self._reset_event = reset_event

        self._previous_path = None # TODO?

        layout = [[sg.Graph((self._width, self._height),(0,0), (self._width, self._height),
                            background_color='white',
                            key='canvas', enable_events=True)],
                [sg.Exit(),
                 sg.Button('SRC', size=(5, 1), button_color='white on green', key = lambda: self.setMode('SRC')),
                 sg.Button('DEST', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('DEST')),
                 sg.Button('TOGGLE', size=(6, 1), button_color='white on green',key = lambda: self.setMode('TOGGLE')),
                 sg.Button('PLAN', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('PLAN')),
                 sg.Button('MAZE', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('MAZE')), 
                 sg.Button('RESET', size=(5, 1), button_color='white on green',  key = lambda: self.setMode('RESET')),
                 sg.Combo(['DIJK','A*', 'LFA*'], size=(5, 1), default_value='LFA*',enable_events=True, key='METHODS')]]

        self._window = sg.Window('GridMaker',
                                    layout, resizable=True, finalize=True)
        self._graph = self._window['canvas']
    
    def setMode(self, mode):
        # TODO: raise execption if invalid mode
        self._state = UiState(mode)

    def drawConnect(self, cellA, cellB, reset = False):
        default_color = 'white' if reset == True else 'black'
        midx, midy = (cellA.x + cellB.x) / 2, (cellA.y + cellB.y) / 2
        self._graph.draw_circle((midx, midy), Cell._diameter / 2, fill_color=default_color, line_color=default_color)
 
        theta = np.arctan2(midy - cellB.y, midx - cellB.x)

        # end pts: center vector + direction vector * radius, direction vector can be gotten by mid - center vector
        self._graph.draw_line((cellA.x + Cell._diameter * np.cos(theta + np.pi), cellA.y + Cell._diameter * np.sin(theta + np.pi)),
                              (cellB.x + Cell._diameter * np.cos(theta), cellB.y + Cell._diameter * np.sin(theta)), width = Cell._hand_width, color=default_color)        

    def drawCenter(self, cell_):
        self._graph.draw_circle((cell_.x, cell_.y), Cell._diameter, fill_color=Cell._GridColorMap[cell_.state], line_color='black')

    def drawCell(self, cell_, init = False):
        # TODO: clear the previous drawn passages
        if init == False:
            for neighbor in self._grid_map.get_potential_neighbors_cells(cell_):
                self.drawConnect(cell_, neighbor, True)
        for neighbor in self._grid_map.get_cell_neighbors(cell_):
            self.drawConnect(cell_, neighbor)
        self.drawCenter(cell_)

    def drawAll(self):
        for i in range(self._grid_map.height):
            for j in range(self._grid_map.width):
                self.drawCell(self._grid_map.get_cell(i, j), init=True)
    
    def pixel_to_raw_index(self, val):
        # TODO: + _diameter doesn't feel right
        c_id = int((val[0] + Cell._diameter) / (Cell._hand_length + Cell._diameter))
        r_id = int((val[1] + Cell._diameter) / (Cell._hand_length + Cell._diameter))

        return c_id, r_id

        # return (int((c_id - 1) / 2), int((r_id - 1) / 2))
    
    def select(self, pixels_coordinates):

        raw_c_id, raw_r_id = self.pixel_to_raw_index(pixels_coordinates)
        
        toggle_cell = raw_c_id % 2 == 1 and raw_r_id % 2 == 1

        if toggle_cell:
            r_id = int(raw_r_id / 2)
            c_id = int(raw_c_id / 2)
            if self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC]:
                new_state = GridState.DEST if self._state == UiState.SELECT_DEST else GridState.SRC
                self._grid_map.udpate_cell_state(r_id, c_id, new_state)
                self._update_queue.put(self._grid_map.get_cell(r_id, c_id))
                prev = self._plan_meta.udpate(self._grid_map.get_cell(r_id, c_id))
                if prev is not None:
                    self._grid_map.udpate_cell_state(prev.r, prev.c, GridState.UNVISITED)
                    self._update_queue.put(prev)
            elif self._grid_map.get_cell(r_id, c_id).state not in [GridState.SRC, GridState.DEST]:
                '''
                toggle cell (r, c)
                remove all connected passage from r, c
                remove all connected passage to r, c
                '''
                new_state = GridState.UNVISITED if self._grid_map.get_cell(r_id, c_id).state == GridState.OCCUPIED else GridState.OCCUPIED
                self._grid_map.udpate_cell_state(r_id, c_id, new_state)
                self._update_queue.put(self._grid_map.get_cell(r_id, c_id))
                # update neighbors
                neighbors = self._grid_map.get_cell_neighbors(self._grid_map.get_cell(r_id, c_id))
                for nei in neighbors:
                    # cut the connection
                    self._grid_map.remove_cell_edge(self._grid_map.get_cell(r_id, c_id), nei)
                    self._update_queue.put(nei)
                    self._toggle_queue.put(((r_id, c_id), (nei.r, nei.c)))                        

        elif self._state == UiState.TOGGLE_OBSTABLE:
            '''
            toggle passage (r1, c1), (r2, c2) -> a valid select radius between two cells
            '''
            # get the passage id pair (r1, c1, r2, c2)

            r1 = int((raw_r_id - 1) / 2)if raw_r_id % 2 == 0 else int(raw_r_id / 2)
            c1 = int((raw_c_id - 1) / 2)if raw_c_id % 2 == 0 else int(raw_c_id / 2)
            r2 = int((raw_r_id + 1) / 2)if raw_r_id % 2 == 0 else int(raw_r_id / 2)
            c2 = int((raw_c_id + 1) / 2)if raw_c_id % 2 == 0 else int(raw_c_id / 2)
            if self._grid_map.has_edge(r1, c1, r2, c2):
                self._grid_map.remove_edge(r1, c1, r2, c2)
            else:
                self._grid_map.add_edge(r1, c1, r2, c2)
            self._update_queue.put(self._grid_map.get_cell(r1, c1))                        
            self._update_queue.put(self._grid_map.get_cell(r2, c2))
            self._toggle_queue.put(((r1, c1), (r2, c2)))                       
        
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
    
    def drawPlanStatus(self, plan_status):
        # revert the prvious drawing
        if self._previous_path is not None:
            for p_path_node in self._previous_path:
                self._update_queue.put(p_path_node)

        # draw the path
        for path_node in plan_status.path():
            path_node.state = GridState.PATH
            self._update_queue.put(path_node)

        # draw start and end points
        # TODO: should this be from first and last element from the plan status?
        self._plan_meta.src.state = GridState.SRC
        self._plan_meta.dest.state = GridState.DEST
        self._update_queue.put(self._plan_meta.src)
        self._update_queue.put(self._plan_meta.dest)
        self._previous_path = plan_status.path()
    
    def _reset(self):
        self._graph.erase()
        self._grid_map.reset()
        self._plan_meta.reset()
        self._reset_event.set()

    def run(self):
        # TODO: Hook up to the button and ctrl-c
        # TODO: not kill properly

        self.drawAll()
        while True:
            while self._update_queue.qsize() > 0:
                thing_to_draw = self._update_queue.get()
                if isinstance(thing_to_draw, Cell):
                    self.drawCell(thing_to_draw)
                elif isinstance(thing_to_draw, PlanStatus):
                    self.drawPlanStatus(thing_to_draw)
                else:
                    print(f'UI not recognize the instance {thing_to_draw}')
            event, values = self._window.read(timeout=100) # 100 ms timeout for updating cell status on the board
            if event in (None, 'Exit'):
                self._reset_event.set()
                self._msg_q.put('Exit')
                break
            elif self._state in [UiState.SELECT_DEST, UiState.SELECT_SRC, UiState.TOGGLE_OBSTABLE] and event == 'canvas':
                self.select(values[event])
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
            elif event == 'METHODS':
                self._plan_meta.method = values['METHODS']
                print(f"update plan method val: {self._plan_meta}")
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
