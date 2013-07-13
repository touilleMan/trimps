#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui, uic
from program import Program

class Ui(QtGui.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.ui.button_run.clicked.connect(self.run)
        self.ui.show()
        # Program is not started at the beginning
        self.program = Program(self.ui.widget_world.image)
        self.program_timer = QtCore.QTimer(self)
        self.program_timer.timeout.connect(self.program.update)
        self.program_running = False
        # Don't forget to connect the robot to the Qt world
        self.ui.widget_world.robot = self.program.robot

    def run(self):
        """Create the program and connect a timer to run it
           If the program is already started, stop it
        """
        if not self.program_running:
            self.program_timer.start(self.program.synchronise_step * 1000)
        else:
            self.program_timer.stop()
        self.program_running = not self.program_running

if __name__ == '__main__':
    # Create the Ui
    app = QtGui.QApplication(sys.argv)
    w = Ui()
    sys.exit(app.exec_())
