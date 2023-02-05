#!/usr/bin/env python3
import sys

# 1. Import QApplication and all the required widgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from board import GridMap
from functools import partial
from grid_status import GridState
from enum import Enum
from Dijkstra import Dijkstra
import queue
from threading import Thread, Event, Lock
from time import time, sleep

class AppMode(Enum):
    STANDBY = 0
    SELECT_SRC = 1
    SELECT_DEST = 2

class MazeApp(QMainWindow):

    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("Planner")
        self._mode = AppMode.STANDBY
        table = QTableWidget(20, 20, self)
        table.itemSelectionChanged.connect(self._select)
        self._grid_map = GridMap(20, 20)
        for i in range(20):    
            table.setColumnWidth(i, 30)
            table.setRowHeight(i, 30)
        self.setCentralWidget(table)
        self._createStatusBar()
        self._grid_queue = queue.Queue()
        self._lock = Lock()
        # update whenever receiving an item
        self._stop_flag = Event()
        freq = 5.0
        self._update_thread = Thread(target=self._set_grid_item, args=(self._stop_flag, freq, self._lock, )).start()
    
    def _set_mode(self, mode):
        self._mode = mode

    def _set_grid_item(self, flag, freq, lock):
        while not flag.is_set():
            # sleep(1 / freq)
            # _item = self._grid_queue.get()
            # self.centralWidget().takeItem(_item.id()[0], _item.id()[1])
            # self.centralWidget().setItem(_item.id()[0], _item.id()[1], _item)
            # lock.acquire()
            # print("drawer acquuired")
            if not self._grid_queue.empty():
                current_qsize = self._grid_queue.qsize()
                while current_qsize > 0:
                    _item = self._grid_queue.get(False)
                    current_qsize -= 1
                    o_item = self.centralWidget().itemAt(_item.id()[0], _item.id()[1])
                    # logic is messy here
                    if o_item is None or o_item.state() not in [GridState.SRC, GridState.DEST, GridState.VISITED]:
                        self.centralWidget().takeItem(_item.id()[0], _item.id()[1])
                        self.centralWidget().setItem(_item.id()[0], _item.id()[1], _item)

            # lock.release()
            # print("drawer acquuired")
            # sleep(1 / freq)


    
    def _select(self):
        r = self.centralWidget().currentRow()
        c = self.centralWidget().currentColumn()
        if self._mode == AppMode.SELECT_SRC:
            self._grid_map.set_grid_index_state(r, c, GridState.SRC)
            self._grid_queue.put(self._grid_map.get_grid(r, c))
        elif self._mode == AppMode.SELECT_DEST:
            self._grid_map.set_grid_index_state(r, c, GridState.DEST)
            self._grid_queue.put(self._grid_map.get_grid(r, c))

        self._mode = AppMode.STANDBY
    
    def _plan(self):
        ### TODO: read the algo. chosen
        print("plan started!")
        planner = Dijkstra()
        plan_status = planner.plan(self._grid_map, self._grid_queue, self._lock)            
        print("plan Done!")
    
    def _close(self):
        self._stop_flag.set()
        # self._update_thread.join()
        self.close()
    
    def _reset(self):
        ### 
        pass

    def _createStatusBar(self):
        status = QStatusBar()
        container = QWidget()
        layout = QGridLayout(container)
        src_button = QPushButton("Set SRC")
        src_button.clicked.connect(partial(self._set_mode, AppMode.SELECT_SRC))
        dest_button = QPushButton("Set DEST")
        dest_button.clicked.connect(partial(self._set_mode, AppMode.SELECT_DEST))
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(partial(self._close))
        plan_button = QPushButton("Plan")
        plan_button.clicked.connect(self._plan)
        shuffle_button = QPushButton("Shuffle")
        reset_button = QPushButton("Reset")
        layout.addWidget(src_button, 0, 0)
        layout.addWidget(dest_button, 0, 1)
        layout.addWidget(plan_button, 0, 2)
        layout.addWidget(shuffle_button, 1, 0)
        layout.addWidget(reset_button, 0, 3)
        layout.addWidget(exit_button, 1, 1)
        drop_down = QComboBox()
        drop_down.addItems(['a1', 'a2'])
        layout.addWidget(drop_down, 1, 2, 1, 3)
        status.addPermanentWidget(container)
        self.setStatusBar(status)


def main():
    app = QApplication([])
    window = MazeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()