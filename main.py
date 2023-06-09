#!/usr/bin/env python3

import queue
from threading import Thread
from ui.board_pysimplegui import Board
from algorithm.planner_manager import PlannerManager
from base_class.grid_map import GridMap
from base_class.cell import Cell


def main():
    # thread pool [1.ui, 2.planner]
    request_queue = queue.Queue()
    update_queue = queue.Queue()

    Cell._diameter = 12
    Cell._hand_length = 20

    # row num and col num should from args
    grid_map = GridMap(10, 20)
    ui_t = Thread(name='UI', target=ui_entry, args=(request_queue, update_queue, grid_map))
    planner_t = Thread(name='Planner', target=PlannerManager.run, args=(request_queue, update_queue, grid_map))
    
    planner_t.start()
    ui_t.start()

    planner_t.join()
    ui_t.join()

def ui_entry(msg_q, update_queue, grid_map):
    b_ = Board(10, 20, msg_q, grid_map, update_queue)
    b_.run()

if __name__ == '__main__':
    main()