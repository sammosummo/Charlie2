"""Runs the main Qt application. This script is the one actually executed.

"""
from logging import getLogger
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from charlie2.tools.mainwindow import MainWindow
from charlie2.tools.paths import logo_path


logger = getLogger(__name__)


def run_app():

    logger.info("called run_app()")
    app = QApplication(argv)
    logger.info("setting some global style options")
    app.setWindowIcon(QIcon(logo_path))
    app.setStyle("Fusion")
    ex = MainWindow()
    exit(app.exec_())
