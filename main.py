from PyQt5.QtCore import QDir, Qt, QUrl, qFuzzyCompare, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QComboBox)

from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from PyQt5.QtGui import QIcon
import sys


class VideoWindow(QMainWindow):
    changeRate = pyqtSignal(float)

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("PyQT Project")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.setAcceptDrops(True)
        videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # self.

        self.index = 0
        self.filenames = []

        self.LoadedMediaActions = []
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Create new action
        openMultipleAction = QAction(QIcon('resources/multiple.png'), '&Open multiple files', self)
        openMultipleAction.setShortcut('Ctrl+M')
        openMultipleAction.setStatusTip('Open media files')
        openMultipleAction.triggered.connect(self.openFile)

        # Create new action
        openAction = QAction(QIcon('resources/open.png'), '&Open single file', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open media file')
        openAction.triggered.connect(self.openFile)

        # Create save action
        saveAction = QAction(QIcon('resources/save.png'), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save File')
        saveAction.triggered.connect(self.saveFile)

        # Create exit action
        exitAction = QAction(QIcon('resources/exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')

        self.loadedMediaMenu = menuBar.addMenu('&Loaded')
        # fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create position slider layout
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
        self.comboSpeed = QComboBox(activated=self.updateRate)
        self.comboSpeed.setEnabled(False)
        self.comboSpeed.addItem("0.5x", 0.5)
        self.comboSpeed.addItem("1.0x", 1.0)
        self.comboSpeed.addItem("2.0x", 2.0)
        self.comboSpeed.setCurrentIndex(1)

        # cut/done button create
        self.cutButton = QPushButton()
        self.cutButton.setEnabled(False)
        self.cutButton.setText("Cut")

        # save button create
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

        self.changeRate.connect(self.setRate)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def loadMedia(self, _index):
        if self.filenames:
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.filenames[_index])))
            self.playButton.setEnabled(True)
            self.comboSpeed.setEnabled(True)
            self.cutButton.setEnabled(True)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        index = self.index
        if fileName != '':
            self.filenames.append(fileName)
            # Create new action
            LoadedMediaAction = QAction(QIcon('resources/media.png'), fileName.split('/')[-1], self)
            LoadedMediaAction.setStatusTip(fileName)
            LoadedMediaAction.triggered.connect(lambda: self.loadMedia(index))
            self.loadedMediaMenu.addAction(LoadedMediaAction)
            self.index = self.index + 1

    def saveFile(self):
        pass

    def openFiles(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

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

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def playbackRate(self):
        return self.comboSpeed.itemData(self.comboSpeed.currentIndex())

    def setRate(self, rate):
        for i in range(self.comboSpeed.count()):
            if qFuzzyCompare(rate, self.comboSpeed.itemData(i)):
                self.comboSpeed.setCurrentIndex(i)
                return

        self.comboSpeed.addItem("%dx" % rate, rate)
        self.comboSpeed.setCurrentIndex(self.comboSpeed.count() - 1)

    def updateRate(self):
        self.changeRate.emit(self.playbackRate())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())
