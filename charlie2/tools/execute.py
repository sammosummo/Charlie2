from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from charlie2.tools.qt import MainWindow
from charlie2.tools.paths import logo_path


if __name__ == '__main__':

    app = QApplication(argv)
    app.setWindowIcon(QIcon(logo_path))
    ex = MainWindow()
    exit(app.exec_())
