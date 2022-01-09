from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QLabel,
                             QSizePolicy, QSlider, QStyle, QVBoxLayout, QComboBox)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
# from moviepy.video.io.VideoFileClip import VideoFileClip


class VideoWindow(QMainWindow):
    changeRate = pyqtSignal(float)
    fullScreenChanged = pyqtSignal(bool)

    # Methods for saving the state of the app
    def getSettingsValues(self):
        self.setting_window = QSettings('My App', 'Window Size')

    def closeEvent(self, event):
        self.setting_window.setValue('window_height', self.rect().height())
        self.setting_window.setValue('window_width', self.rect().width())

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)

        # Set the title of the project
        self.setWindowTitle("PyQT Project")

        # Get the previous settings
        self.setting_window = None

        # Get the size of the last instance the layout was in
        self.getSettingsValues()
        height = self.setting_window.value('window_height')
        width = self.setting_window.value('window_width')
        self.resize(int(width), int(height))

        # Variables used for the logic of loading the files (To be reviewed)

        self.index = 0
        self.savedIndex = 0
        self.filenames = []

        self.LoadedMediaActions = []
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # MAIN MENU ACTIONS

        # Create new action (To be reviewed)
        openMultipleAction = QAction(QIcon('../resources/icons/multiple.png'), '&Open multiple files', self)
        openMultipleAction.setShortcut('Ctrl+M')
        openMultipleAction.setStatusTip('Open media files')
        openMultipleAction.triggered.connect(self.openFile)

        # Create open action
        openAction = QAction(QIcon('../resources/icons/open.png'), '&Open single file', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open media file')
        openAction.triggered.connect(self.openFile)

        # Create save action
        saveAction = QAction(QIcon('../resources/icons/save.png'), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save File')
        saveAction.triggered.connect(self.saveFile)

        # Create exit action
        exitAction = QAction(QIcon('../resources/icons/exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()

        # Add main menu drop-down buttons
        fileMenu = menuBar.addMenu('&File')
        self.loadedMediaMenu = menuBar.addMenu('&Loaded')

        # Add fileMenu drop-down actions
        fileMenu.addAction(openMultipleAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # CREATING WIDGETS

        # Create the MediaPlayerClass
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        # Create Playlist
        self.playlist = QMediaPlaylist()

        # Create the PlayheadSlider
        self.playheadSlider = QSlider(Qt.Horizontal)
        self.playheadSlider.setRange(0, 0)
        self.playheadSlider.sliderMoved.connect(self.setPosition)

        # Create the PlayButton
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        # Create Full Screen button
        self.fullScreenButton = QPushButton("FullScreen")
        self.fullScreenButton.setEnabled(False)
        self.fullScreenButton.setCheckable(True)

        # Create Speed buttons
        self.comboSpeed = QComboBox(activated=self.updateSpeed)
        self.comboSpeed.setEnabled(False)
        self.comboSpeed.addItem("0.5x", 0.5)
        self.comboSpeed.addItem("0.75x", 0.75)
        self.comboSpeed.addItem("1.0x", 1.0)
        self.comboSpeed.addItem("1.25x", 1.25)
        self.comboSpeed.addItem("1.5x", 1.5)
        self.comboSpeed.setCurrentIndex(2)

        # Create Cut/Done button
        self.cutButton = QPushButton()
        self.cutButton.setEnabled(False)
        self.cutButton.setText("Cut")

        # Create Save button
        self.saveButton = QPushButton()
        self.saveButton.setEnabled(False)
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveFile)

        # Create Exit button
        self.exitButton = QPushButton()
        self.exitButton.setText("Exit")
        self.exitButton.clicked.connect(self.exitCall)

        # Create position slider layout
        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(0, 0, 0, 0)
        sliderLayout.addWidget(self.playheadSlider)

        # Create control layout
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(110, 20, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.fullScreenButton)
        controlLayout.addWidget(self.comboSpeed)
        controlLayout.addWidget(self.cutButton)
        controlLayout.addWidget(self.saveButton)
        controlLayout.addWidget(self.exitButton)

        # Add to the final layout
        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(sliderLayout)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Create a widget for window contents and makes it the main window and set it to have the layout
        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(layout)

        self.changeRate.connect(self.mediaPlayer.setPlaybackRate)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.fullScreenButton.clicked.connect(videoWidget.setFullScreen)

    # Returns the speed chosen by choosing the comboSpeed
    def speed(self):
        return self.comboSpeed.itemData(self.comboSpeed.currentIndex())

    # Takes the speed and sends it to the mediaPlayer PlaybackRate
    def updateSpeed(self):
        self.changeRate.emit(self.speed())

    # Toggles between the play and pause state when pressing the button
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    # Changes the icon of the play button depending on the videoPlayer state
    def mediaStateChanged(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    # Changes the position of the slider when it is dragged
    def positionChanged(self, position):
        self.playheadSlider.setValue(position)

    # Sets the range for the slider between 0 and the duration of the media file
    def durationChanged(self, duration):
        self.playheadSlider.setRange(0, duration)

    # Changes the timestamp of the media when moving the playheadSlider
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    # Displays the errorLabel when an error occurs to the videoPlayer
    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText(
            "Error: You must install codec if you are on Windows! " + self.mediaPlayer.errorString())

    # Loads a selected media file into the videoplayer
    def loadMedia(self, _index):
        if self.filenames:
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(self.filenames[_index])))
            self.playButton.setEnabled(True)
            self.comboSpeed.setEnabled(True)
            self.cutButton.setEnabled(True)
            self.saveButton.setEnabled(True)
            self.fullScreenButton.setEnabled(True)

    # Lets you select one media file and add it to the "filenames" submenu
    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath())
        index = self.index
        self.savedIndex = index
        if fileName != '':
            self.filenames.append(fileName)
            # Create new action
            LoadedMediaAction = QAction(QIcon('../resources/icons/media.png'), fileName.split('/')[-1], self)
            LoadedMediaAction.setStatusTip(fileName)
            LoadedMediaAction.triggered.connect(lambda: self.loadMedia(index))
            self.loadedMediaMenu.addAction(LoadedMediaAction)
            self.index = self.index + 1

    # Lets you select multiple media files and add it to the "filenames" submenu
    def openFiles(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, "Open Movie", QDir.homePath(), "mp3Files(*.mp3)")
        index = self.index
        self.savedIndex = index
        numOfFiles = len(fileNames)
        if fileNames != '':
            for fileName in fileNames:
                self.filenames.append(fileName)
                # Create new action
                LoadedMediaAction = QAction(QIcon('../resources/icons/media.png'), fileName.split('/')[-1], self)
                LoadedMediaAction.setStatusTip(fileName)
                LoadedMediaAction.triggered.connect(lambda: self.loadMedia(index))
                self.loadedMediaMenu.addAction(LoadedMediaAction)
                self.index = self.index + 1

    # Deprecated
    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "MP3(*.mp3);;MP4(*.mp4 );;All Files(*.*) ")
        if filePath == "":
            return
        self.filenames[self.savedIndex].save(filePath)

    # Exit the application
    def exitCall(self):
        self.close()
