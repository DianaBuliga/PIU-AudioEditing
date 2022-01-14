from os import path, listdir as ld

from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal, QSettings, QDirIterator
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QLabel,
                             QSizePolicy, QSlider, QStyle, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction

from moviepy.editor import *


class VideoWindow(QMainWindow):
    changeRate = pyqtSignal(float)
    fullScreenChanged = pyqtSignal(bool)
    VideoFileClip

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

        # Status Bar
        self.statusBar()
        self.statusBarStatus = 0
        self.handleStatusBar()

        # Variables used for the logic of loading the files (To be reviewed)

        self.editedMediaFile = None
        self.loadedSongsPaths = []
        self.playlistLoaded = False
        self.drt = None
        self.fl = []
        self.songPlaying = ""
        self.lastPlaylistIndex = 0

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # MAIN MENU ACTIONS

        # Create load folder action(To be reviewed)
        loadFolderAction = QAction(QIcon('../resources/icons/multiple.png'), '&Add Media Folder', self)
        loadFolderAction.setShortcut('Ctrl+F')
        loadFolderAction.setStatusTip('Open Media Folder')
        loadFolderAction.triggered.connect(self.openMediaFolder)

        # Create open action
        openAction = QAction(QIcon('../resources/icons/open.png'), '&Add Media File', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Media File')
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
        fileMenu.addAction(loadFolderAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # CREATING WIDGETS

        self.table = QTableWidget()

        self.playlist = QMediaPlaylist()
        # Create the MediaPlayerClass
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        # Set the table
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(("NR", "TITLE"))

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
        self.playButton.clicked.connect(self.playMusic)

        # Create the ShowPlaylistButton
        self.showPlaylistButton = QPushButton("Show Playlist")
        self.showPlaylistButton.setEnabled(False)
        self.showPlaylistButton.clicked.connect(self.showPlaylist)

        # Create FullScreenButton
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
        self.cutButton.clicked.connect(self.cutSong)

        # Create Save button
        self.saveButton = QPushButton()
        self.saveButton.setEnabled(False)
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveFile)

        # Create Exit button
        self.exitButton = QPushButton()
        self.exitButton.setText("Exit")
        self.exitButton.clicked.connect(self.exitCall)

        # Create Slider Timestamp Labels
        self.sliderTextMin = QLabel()
        self.sliderTextMin.setText("0:00")
        self.sliderTextMax = QLabel()
        self.sliderTextMax.setText("0:00")

        # Create position slider layout
        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(0, 0, 0, 0)
        sliderLayout.addWidget(self.playButton)
        sliderLayout.addWidget(self.sliderTextMin)
        sliderLayout.addWidget(self.playheadSlider)
        sliderLayout.addWidget(self.sliderTextMax)

        # Create control layout
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(110, 20, 0, 0)

        controlLayout.addWidget(self.fullScreenButton)
        controlLayout.addWidget(self.comboSpeed)
        controlLayout.addWidget(self.cutButton)
        controlLayout.addWidget(self.saveButton)
        controlLayout.addWidget(self.exitButton)
        controlLayout.addWidget(self.showPlaylistButton)

        # Add to the main layout
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(videoWidget)
        leftLayout.addLayout(sliderLayout)
        leftLayout.addLayout(controlLayout)
        leftLayout.addWidget(self.errorLabel)

        # Create playlist layout
        self.playlistLayout = QHBoxLayout()

        # Add to the final layout
        finalLayout = QVBoxLayout()
        finalLayout.addLayout(leftLayout)
        finalLayout.addLayout(self.playlistLayout)

        # Create a widget for window contents and makes it the main window and set it to have the layout
        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(finalLayout)

        self.changeRate.connect(self.mediaPlayer.setPlaybackRate)
        self.mediaPlayer.setPlaylist(self.playlist)
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.fullScreenButton.clicked.connect(videoWidget.setFullScreen)

    def showPlaylist(self):
        if self.playlistLoaded and self.table.isHidden() is False:
            self.table.hide()
            self.showPlaylistButton.setText("Show Playlist")
        elif self.table.isHidden():
            self.table.show()
            self.showPlaylistButton.setText("Hide Playlist")

    # Returns the speed chosen by choosing the comboSpeed
    def speed(self):
        return self.comboSpeed.itemData(self.comboSpeed.currentIndex())

    # Takes the speed and sends it to the mediaPlayer PlaybackRate
    def updateSpeed(self):
        self.changeRate.emit(self.speed())

    # Toggles between the play and pause state when pressing the button
    def playMusic(self):
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
        self.timeDisplayMin(position)

        # Sets the range for the slider between 0 and the duration of the media file

    def durationChanged(self, duration):
        self.playheadSlider.setRange(0, duration)
        self.timeDisplayMax(duration)

    def timeDisplayMax(self, duration):
        minutes = int(duration / 60000)
        seconds = int((duration - minutes * 60000) / 1000)
        self.sliderTextMax.setText('{}:{}'.format(minutes, seconds))

    def timeDisplayMin(self, position):
        minutes = int(position / 60000)
        seconds = int((position - minutes * 60000) / 1000)
        self.sliderTextMin.setText('{}:{}'.format(minutes, seconds))

    # Changes the timestamp of the media when moving the playheadSlider
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    # Displays the errorLabel when an error occurs to the videoPlayer
    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText(
            "Error: You must install codec if you are on Windows! " + self.mediaPlayer.errorString())

    # Sets the message shown in the status bar
    def handleStatusBar(self):
        if self.statusBarStatus == 0:
            self.statusBar().showMessage("No Loaded Media!")

    # Loads a selected media file into the videoplayer
    def loadMedia(self, musicPath):

        self.mediaPlayer.setMedia(QMediaContent(musicPath))
        self.mediaPlayer.play()
        self.playButton.setEnabled(True)
        self.comboSpeed.setEnabled(True)
        self.cutButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.fullScreenButton.setEnabled(True)

    # Lets you select one media file and add it to the "filenames" submenu
    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Add File", QDir.homePath(), "MP3(*.mp3);;MP4(*.mp4 );; OGG("
                                                                                     "*.ogg);; WAV(*.wav);; M4A("
                                                                                     "*.m4a);;All Files(*.*) ")
        if fileName != '':
            self.fl.append(fileName.split('/')[-1])
            self.loadedSongsPaths.append(fileName)
            self.createLoadedMediaAction(fileName)
            self.createTable()
            self.createTableRow()

            self.playlistLoaded = True
            self.showPlaylistButton.setEnabled(True)
            self.playlistLayout.addWidget(self.table)
            self.table.hide()
            self.showPlaylistButton.setText("Show Playlist")

    # Create new Load Media Action
    def createLoadedMediaAction(self, fileName):
        LoadedMediaAction = QAction(QIcon('../resources/icons/media.png'), fileName.split('/')[-1], self)
        LoadedMediaAction.setStatusTip(fileName.split('/')[-1])
        LoadedMediaAction.triggered.connect(lambda: self.loadMedia(QUrl.fromLocalFile(fileName)))
        self.loadedMediaMenu.addAction(LoadedMediaAction)

    # Lets you select multiple media files and add it to the "filenames" submenu
    def openMediaFolder(self):
        folderChosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', '~')
        if folderChosen != '':
            self.drt = folderChosen  # Path la director
            cam = [path.join(self.drt, name) for name in ld(self.drt) if
                   path.isfile(path.join(self.drt, name))]  # Lista de path-uri de director/melodie
            self.loadedSongsPaths += cam
            self.fl += [x[len(self.drt) + 1:] for x in cam]  # Lista de nume de melodii

            self.createTable()

            if folderChosen is not None:
                self.playlistLoaded = True
                self.showPlaylistButton.setEnabled(True)
                iterator = QDirIterator(folderChosen)
                iterator.next()
                while iterator.hasNext():
                    if not iterator.fileInfo().isDir() and iterator.filePath() != '.':
                        if iterator.fileInfo().suffix() in ('mp3', 'ogg', 'wav', 'm4a', 'mp4', 'wav'):
                            self.createLoadedMediaAction(self.fl[self.lastPlaylistIndex])
                            self.createTableRow()
                        else:
                            break
                    iterator.next()

                self.createLoadedMediaAction(self.fl[self.lastPlaylistIndex])
                self.createTableRow()

                self.playlistLayout.addWidget(self.table)
                self.table.hide()
                self.showPlaylistButton.setText("Show Playlist")

    def createTable(self):
        self.table.setRowCount(len(self.fl))
        self.table.setVerticalHeaderLabels(("",) * (len(self.fl)))

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.clickedItem)

    def createTableRow(self):
        self.table.setItem(self.lastPlaylistIndex, 0, QTableWidgetItem(str(self.lastPlaylistIndex + 1)))
        self.table.setItem(self.lastPlaylistIndex, 1, QTableWidgetItem(self.fl[self.lastPlaylistIndex]))

        self.table.setColumnWidth(0, 1 * self.frameGeometry().width() / 5)
        self.table.setColumnWidth(1, 3 * self.frameGeometry().width() / 5)

        self.lastPlaylistIndex = self.lastPlaylistIndex + 1

    def clickedItem(self):

        row = self.table.selectedItems()[0].row()
        self.songPlaying = self.loadedSongsPaths[row]
        url = QUrl.fromLocalFile(self.loadedSongsPaths[row])
        self.loadMedia(url)

    def cutSong(self):
        print(self.songPlaying)
        minim = 10
        maxim = 15
        self.editedMediaFile = VideoFileClip(self.songPlaying).subclip(minim, maxim)

    # Deprecated To be done after integration of moviepy
    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Media", "", "MP3(*.mp3);;MP4(*.mp4 );;All Files(*.*) ")
        self.editedMediaFile.write_videofile(filePath)

    # Exit the application
    def exitCall(self):
        self.close()
