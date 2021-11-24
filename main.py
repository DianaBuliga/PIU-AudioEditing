import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)

        self.button.clicked.connect(self.print_value)
        self.button_2.clicked.connect(self.print_value2)

    def print_value(self):
        print(self.lineEdit_Entry.text())

    def print_value2(self):
        print("You got fooled!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Method...")
