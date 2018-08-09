from sys import argv, exit

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setCentralWidget(CustomWidget(self))
        self.show()


class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super(CustomWidget, self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        pass

    def mousePressEvent(self, event):
        print(event)

    def keyPressEvent(self, event):
        print(event)


if __name__ == "__main__":

    app = QApplication(argv)
    ex = MainWindow()
    exit(app.exec_())
