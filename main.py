import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QVBoxLayout, QLabel


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        #self.window_width, self.window_height, = 1200, 800
        #self.setMinimumSize(self, self.window_width, self.window_height)

        label = QLabel('Hello World')

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(label)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet('''
        QWidget{
            font-size: 35px;
            }
    ''')

    myApp = MyApp()
    myApp.show()

    try:
        app.exec_();
    except SystemExit:
        print("Closing Method...")
