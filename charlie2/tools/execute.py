from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from charlie2.tools.qt import MainWindow


if __name__ == '__main__':

    app = QApplication(argv)
    ex = MainWindow()
    exit(app.exec_())
