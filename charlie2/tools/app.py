"""Runs the main Qt application. This script is the one actually executed.

"""
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from charlie2.tools.mainwindow import MainWindow
from charlie2.tools.paths import logo_path


def run_app():

    app = QApplication(argv)
    app.setWindowIcon(QIcon(logo_path))
    ex = MainWindow()
    exit(app.exec_())
