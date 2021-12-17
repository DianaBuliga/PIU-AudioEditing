from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QSizePolicy, QSlider, QStyle, QVBoxLayout, QComboBox)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("PyQT Project")
        self.setStyleSheet("background-image: url(Artboard_85.png);")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.setAcceptDrops(True)
        videoWidget = QVideoWidget()

        #self.i

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create save action
        saveAction = QAction(QIcon('save.png'), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save File')
        saveAction.triggered.connect(self.saveFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        # saveMenu = menuBar.addMenu('&Save')
        # exitMenu = menuBar.addMenu('&Exit')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # exitMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        #Create position slider layout
        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(0, 0, 0, 0)

        # position slider create
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        sliderLayout.addWidget(self.positionSlider)

        # play button create
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        # speed play create
        self.comboSpeed = QComboBox()
        self.comboSpeed.addItems(["x0.5", "x1", "x2"])
        self.comboSpeed.setEnabled(False)
        self.comboSpeed.setGeometry(10, 10, 10, 10)

        # cut/done button create
        self.cutButton = QPushButton()
        self.cutButton.setEnabled(False)
        self.cutButton.setText("Cut")

        #save button create
        self.saveButton = QPushButton()
        self.saveButton.setEnabled(False)
        self.saveButton.setText("Save")

        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        # controlLayout.addWidget(self.positionSlider)
        # controlLayout.addWidget(self.)
        controlLayout.addWidget(self.comboSpeed)
        controlLayout.addWidget(self.cutButton)
        controlLayout.addWidget(self.saveButton)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(sliderLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.comboSpeed.setEnabled(True)
            self.cutButton.setEnabled(True)

    def saveFile(self):
        file = open(QFileDialog.getSaveFileName(self, 'Save File'))
        text = self.textEdit.toPlainText()
        file.write(text)
        file.close()

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())