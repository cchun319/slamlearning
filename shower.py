#!/usr/bin/env python3
import sys

# 1. Import QApplication and all the required widgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal, QObject
from board import GridMap
from functools import partial
from grid_status import GridState
from enum import Enum
from Dijkstra import Dijkstra
import queue
from time import time, sleep

class AppMode(Enum):
    STANDBY = 0
    SELECT_SRC = 1
    SELECT_DEST = 2

class Communicate(QObject):
    sig = pyqtSignal(int)

class MazeApp(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        self.communicate = Communicate()
        self.communicate.sig[int].connect(self._set_grid_item)
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
    
    def _set_mode(self, mode):
        self._mode = mode

    def _set_grid_item(self):
        if not self._grid_queue.empty():
            current_qsize = self._grid_queue.qsize()
            while current_qsize > 0:
                _item = self._grid_queue.get(True)
                current_qsize -= 1
                o_item = self.centralWidget().itemAt(_item.id()[0], _item.id()[1])
                # TODO: clean way to update the logic
                self.centralWidget().takeItem(_item.id()[0], _item.id()[1])
                self.centralWidget().setItem(_item.id()[0], _item.id()[1], _item)
                    
            self._grid_queue.task_done()

    def _select(self):
        r = self.centralWidget().currentRow()
        c = self.centralWidget().currentColumn()
        if self._mode == AppMode.SELECT_SRC:
            self._grid_map.set_grid_index_state(r, c, GridState.SRC)
            self._grid_queue.put(self._grid_map.get_grid(r, c))
        elif self._mode == AppMode.SELECT_DEST:
            self._grid_map.set_grid_index_state(r, c, GridState.DEST)
            self._grid_queue.put(self._grid_map.get_grid(r, c))
        self.communicate.sig.emit(0)

        self._mode = AppMode.STANDBY
    
    def _plan(self):
        ### TODO: might need to put this in another thread, read the algo. chosen
        print("plan started!")
        planner = Dijkstra()
        plan_status = planner.plan(self._grid_map, self._grid_queue, self.communicate)
        if plan_status.success():
            for node in plan_status.path():
                self._grid_queue.put(node)
        self.communicate.sig.emit(0)
        print("plan Done!")
    
    def _close(self):
        self.close()
    
    def _reset(self):
        ###
        self._grid_map.reset()
        for i in range(self._grid_map._map_info._r):
            for j in range(self._grid_map._map_info._c):
                self.centralWidget().takeItem(i, j)

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
        reset_button.clicked.connect(self._reset)
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