from PyQt5.QtWidgets import QApplication
import VideoWindowClass as vw
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('''

    ''')
    video_player = vw.VideoWindow()
    video_player.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Windows...")
