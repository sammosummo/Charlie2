"""Runs the main Qt application. This script is the one actually executed.

"""
from logging import getLogger
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from charlie2.tools.mainwindow import MainWindow
from charlie2.tools.paths import logo_path


logger = getLogger(__name__)


def run_app():

    logger.info("initialising the application")
    app = QApplication(argv)
    logger.info("setting some global style options")
    app.setWindowIcon(QIcon(logo_path))
    app.setStyle("Fusion")
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    logger.info("executing the app")
    ex = MainWindow()
    exit(app.exec_())
