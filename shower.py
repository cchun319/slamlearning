#!/usr/bin/env python3
import sys

# 1. Import QApplication and all the required widgets
from PyQt5.QtWidgets import *
from board import GridMap
from functools import partial
from grid_status import GridState
from enum import Enum

class AppMode(Enum):
    STANDBY = 0
    SELECT = 1


class MazeApp(QMainWindow):

    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("QMainWindow")
        self._createToolBar()
        table = QTableWidget(20, 20, self)
        table.itemSelectionChanged.connect(self._select)
        self._grid_map = GridMap(20, 20)
        for i in range(20):    
            table.setColumnWidth(i, 30)
            table.setRowHeight(i, 30)
        self.setCentralWidget(table)
        self._createStatusBar()
    
    def _set_mode(self, mode):
        self._mode = mode
    
    def _select(self):
        r = self.centralWidget().currentRow()
        c = self.centralWidget().currentColumn()

    def _createToolBar(self):
        tools = QToolBar()
        tools.addAction("Exit", self.close)
        self.addToolBar(tools)

    def _createStatusBar(self):
        status = QStatusBar()
        container = QWidget()
        layout = QGridLayout(container)
        src_button = QPushButton("Set SRC")
        src_button.clicked.connect(partial(self._set_mode, AppMode.SELECT))
        dest_button = QPushButton("Set DEST")
        plan_button = QPushButton("Plan")
        shuffle_button = QPushButton("Shuffle")
        reset_button = QPushButton("Reset")
        layout.addWidget(src_button, 0, 0)
        layout.addWidget(dest_button, 0, 1)
        layout.addWidget(plan_button, 0, 2)
        layout.addWidget(shuffle_button, 1, 0)
        layout.addWidget(reset_button, 1, 1)
        drop_down = QComboBox()
        drop_down.addItems(['a1', 'a2'])
        layout.addWidget(drop_down, 1, 2)
        status.addPermanentWidget(container)
        self.setStatusBar(status)


def main():
    app = QApplication([])
    window = MazeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()