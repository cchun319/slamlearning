#!/usr/bin/env python3

import queue
from threading import Thread
from ui.board_pysimplegui import Board
from algorithm.planner_manager import PlannerManager
from base_class.grid_map import GridMap
from base_class.cell import Cell
import argparse

def main():
    ''' 
    TODO:
    debug should be configurable for each class [ui, planner, ...]
    '''
    parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')
    
    parser.add_argument('--rows', type=int, default=10,
                    help='an integer for number of row')
    parser.add_argument('--cols', type=int, default=15,
                    help='an integer for number of column')

    args = parser.parse_args()

    request_queue = queue.Queue()
    update_queue = queue.Queue()

    Cell._diameter = 8
    Cell._hand_length = 20

    grid_map = GridMap(args.rows, args.cols)
    ui_t = Thread(name='UI', target=ui_entry, args=(request_queue, update_queue, grid_map))
    planner_t = Thread(name='Planner', target=PlannerManager.run, args=(request_queue, update_queue, grid_map))
    
    planner_t.start()
    ui_t.start()

    planner_t.join()
    ui_t.join()

def ui_entry(msg_q, update_queue, grid_map):
    b_ = Board(msg_q, grid_map, update_queue)
    b_.run()

if __name__ == '__main__':
    main()