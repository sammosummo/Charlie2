"""Runs the main Qt application. This script is the one actually executed.

"""
from sys import argv, exit
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from charlie2.tools.mainwindow import MainWindow
from charlie2.tools.paths import logo_path


def run_app():

    print(QStyleFactory.keys())
    app = QApplication(argv)
    app.setWindowIcon(QIcon(logo_path))
    app.setStyle('Fusion')
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    ex = MainWindow()
    exit(app.exec_())
