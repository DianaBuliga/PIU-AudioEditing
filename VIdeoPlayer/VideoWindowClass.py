from os import path, listdir as ld

from PyQt5.QtCore import QDir, Qt, QUrl, pyqtSignal, QSettings, QDirIterator, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QLabel,
                             QSizePolicy, QSlider, QStyle, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
                             QLineEdit, QMessageBox)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction

from moviepy.editor import *


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

        self.maxSeconds = None
        self.maxMinutes = None

        self.minSeconds = None
        self.minMinutes = None

        self.setWindowTitle("PyQT Project")

        # Get the previous settings
        self.setting_window = None

        # CSS for window
        self.setStyleSheet("background-color: #2c3338;"
                           "color: white;")

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
        menuBar.setStyleSheet("QMenuBar::item::selected{"
                              "background-color: #ffa500;}")

        # Add main menu drop-down buttons
        fileMenu = menuBar.addMenu('&File')
        self.loadedMediaMenu = menuBar.addMenu('&Loaded')
        fileMenu.setStyleSheet("QMenu::item::selected{"
                               "background-color: #ffa500;"
                               "color: black;}")

        # Add fileMenu drop-down actions
        fileMenu.addAction(loadFolderAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # CREATING WIDGETS

        self.table = QTableWidget()
        self.table.setStyleSheet("background-color: #2c3338; color: white;")
        self.table.setStyleSheet("QHeaderView::section{"
                                 "background-color: #2c3338; color: white;}")

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
        self.showPlaylistButton.setStyleSheet("QPushButton:hover{"
                                              "background-color: #ffa500;}")

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
        self.comboSpeed.setStyleSheet("QPushButton:hover{background-color: #ffa500;}")

        # Create Crop button
        self.finishEditButton = QPushButton()
        self.finishEditButton.setEnabled(False)
        self.finishEditButton.setHidden(True)
        self.finishEditButton.setText("CropFile")
        self.finishEditButton.clicked.connect(self.cutSong)
        self.finishEditButton.setStyleSheet("QPushButton:hover{background-color: #ffa500;}")

        # Create Left Margin TextArea
        self.leftMarginText = QLineEdit()
        self.leftMarginText.setHidden(True)
        self.leftMarginText.setText("0:00")
        self.leftMarginText.setStyleSheet("QLabel:hover{background-color: #ffa500;}")

        # Create Right Margin TextArea
        self.rightMarginText = QLineEdit()
        self.rightMarginText.setHidden(True)
        self.rightMarginText.setText("0:00")
        self.rightMarginText.setStyleSheet("QLabel:hover{background-color: #ffa500;}")

        # Create Crop button
        self.cutButton = QPushButton()
        self.cutButton.setEnabled(False)
        self.cutButton.setText("CropFile")
        self.cutButton.clicked.connect(self.cropPressed)
        self.cutButton.setStyleSheet("QPushButton:hover{background-color: #ffa500;}")

        # Create Save button
        self.saveButton = QPushButton()
        self.saveButton.setEnabled(False)
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveFile)
        self.saveButton.setStyleSheet("QPushButton:hover{background-color: #ffa500;}")

        # Create Exit button
        self.exitButton = QPushButton()
        self.exitButton.setText("Exit")
        self.exitButton.clicked.connect(self.exitCall)
        self.exitButton.setStyleSheet("QPushButton:hover{background-color: #ffa500;}")

        # Create Slider Timestamp Labels
        self.sliderTextMin = QLabel()
        self.sliderTextMin.setText("0:00")
        self.sliderTextMin.setStyleSheet("color: #ffa500;")
        self.sliderTextMax = QLabel()
        self.sliderTextMax.setText("0:00")
        self.sliderTextMax.setStyleSheet("color: #ffa500;")

        # Create position slider layout
        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(0, 0, 0, 0)
        sliderLayout.addWidget(self.playButton)
        sliderLayout.addWidget(self.sliderTextMin)
        sliderLayout.addWidget(self.playheadSlider)
        sliderLayout.addWidget(self.sliderTextMax)

        # Create control layout
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(100, 20, 100, 0)

        controlLayout.addWidget(self.fullScreenButton)
        controlLayout.addWidget(self.comboSpeed)
        controlLayout.addWidget(self.exitButton)
        controlLayout.addWidget(self.showPlaylistButton)

        # Create edit layout
        editLayout = QHBoxLayout()

        editLayout.setContentsMargins(100, 10, 100, 0)

        editLayout.addWidget(self.cutButton)
        editLayout.addWidget(self.saveButton)

        # Create Invisible Overlaping layout
        hiddenEditLayout = QVBoxLayout()

        hiddenEditLayout.setContentsMargins(100, 10, 100, 0)

        hiddenEditLayout.addWidget(self.leftMarginText)
        hiddenEditLayout.addWidget(self.rightMarginText)
        hiddenEditLayout.addWidget(self.finishEditButton)
        # Add to the main layout
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(videoWidget)
        leftLayout.addLayout(sliderLayout)
        leftLayout.addLayout(controlLayout)
        leftLayout.addLayout(editLayout)
        leftLayout.addLayout(hiddenEditLayout)
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
        self.maxMinutes = int(duration / 60000)
        self.maxSeconds = int((duration - self.maxMinutes * 60000) / 1000)
        self.sliderTextMax.setText('{}:{}'.format(self.maxMinutes, self.maxSeconds))

    def timeDisplayMin(self, position):
        self.minMinutes = int(position / 60000)
        self.minSeconds = int((position - self.minMinutes * 60000) / 1000)
        self.sliderTextMin.setText('{}:{}'.format(self.minMinutes, self.minSeconds))

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

        url = QUrl.fromLocalFile(musicPath)
        self.songPlaying = musicPath

        self.statusBar().showMessage("Now Playing : " + self.songPlaying.split('/')[-1])
        self.mediaPlayer.setMedia(QMediaContent(url))
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
        LoadedMediaAction.triggered.connect(lambda: self.loadMedia(fileName))
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
                            self.createLoadedMediaAction(cam[self.lastPlaylistIndex])
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
        self.loadMedia(self.loadedSongsPaths[row])

    def cutSong(self):
        print(self.songPlaying)

        minText = self.leftMarginText.text()
        maxText = self.rightMarginText.text()

        print("Recieved minText:" + minText)
        print("Recieved maxText:" + maxText)

        minTextMinute = minText.split(':')[0]
        minTextSecond = minText.split(':')[-1]

        print("Recieved minTextMinute:" + minTextMinute)
        print("Recieved minTextSecond:" + minTextSecond)

        maxTextMinute = maxText.split(':')[0]
        maxTextSecond = maxText.split(':')[-1]

        print("Recieved maxTextMinute:" + maxTextMinute)
        print("Recieved maxTextSecond:" + maxTextSecond)

        minimSec = int(int(minTextSecond) + int(int(minTextMinute) * 60))
        maximSec = int(int(maxTextSecond) + int(int(maxTextMinute) * 60))

        print(minimSec)
        print(maximSec)
        if (
                minimSec < 0
                or maximSec < 0
                or maximSec > self.maxSeconds + 60 * self.maxMinutes
                or minimSec > self.maxSeconds + 60 * self.maxSeconds
                or minimSec > maximSec
        ):

            QMessageBox.question(self, 'Failed!', "Invalid timestamps! ", QMessageBox.No,
                                 QMessageBox.No)
        else:
            self.editedMediaFile = VideoFileClip(self.songPlaying).subclip(minimSec, maximSec)
            QMessageBox.question(self, 'Successful!', "Your file has been successfuly croped, now save it!: ",
                                 QMessageBox.Ok,
                                 QMessageBox.Ok)
            self.rightMarginText.setText("0:0")
            self.rightMarginText.setHidden(True)

            self.leftMarginText.setText("0:0")
            self.leftMarginText.setHidden(True)

            self.finishEditButton.setEnabled(False)
            self.finishEditButton.setHidden(True)

    def cropPressed(self):
        self.rightMarginText.setText('{}:{}'.format(self.maxMinutes, self.maxSeconds))
        self.rightMarginText.setHidden(False)

        self.leftMarginText.setText('{}:{}'.format(self.minMinutes, self.minSeconds))
        self.leftMarginText.setHidden(False)

        self.finishEditButton.setEnabled(True)
        self.finishEditButton.setHidden(False)

    # Deprecated To be done after integration of moviepy
    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Media", "", "MP3(*.mp3);;MP4(*.mp4 );;All Files(*.*) ")
        self.editedMediaFile.write_videofile(filePath)

    # Exit the application
    def exitCall(self):
        self.close()
