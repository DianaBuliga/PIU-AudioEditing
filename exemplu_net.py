import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QUrl


class ListBoxWdget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Asta seteaza sa accepte drops
        self.resize(600, 600)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("audio/mp4"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("audio/mp4"):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("audio/mp4"):
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []

            print(event.mimeData().urls())


class AppDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)

        self.lstView = ListBoxWdget(self)

        self.btn = QPushButton('Get Value', self)
        self.btn.setGeometry(850, 400, 500, 50)


app = QApplication(sys.argv)
demo = AppDemo()
demo.show()

sys.exit(app.exec_())
