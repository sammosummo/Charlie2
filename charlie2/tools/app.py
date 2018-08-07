"""Runs the application.

"""
from logging import getLogger
from sys import argv, exit

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from charlie2.tools.mainwindow import MainWindow
from charlie2.tools.paths import logo_path

logger = getLogger(__name__)


def run_app() -> None:
    logger.debug("called run_app()")
    app = QApplication(argv)
    logger.debug("setting some global style options")
    app.setWindowIcon(QIcon(logo_path))
    app.setStyle("Fusion")
    ex = MainWindow()
    exit(app.exec_())
