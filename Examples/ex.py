#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
from os import path, listdir as ld
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import QUrl, QDirIterator, Qt, QTime, QDate, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog, QAction, QHBoxLayout, QVBoxLayout, QSlider, QTableWidget, QTableWidgetItem, QLabel, QStyle, QMessageBox
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent

class App(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.player = QMediaPlayer( )
        self.playlist = QMediaPlaylist( )
        self.title = "AC&MM SOUND PLAYER"
        self.play = False
        self.dur = [ ]
        self.v = ""
        self.song = ""
        self.duration = 0
        self.s = 0
        self.m = 0
        self.color = 0  # 0- toggle to dark 1- toggle to light
        self.initUI( )

    def initUI(self):
        menuBar = self.menuBar( )
        fileMenu = menuBar.addMenu('File')
        windowMenu = menuBar.addMenu('Extra')

        folderAct = QAction('Open Folder', self)
        themeAct = QAction('Light or Dark theme', self)

        folderAct.setShortcut('Ctrl+D')
        themeAct.setShortcut('Ctrl+T')

        fileMenu.addAction(folderAct)
        windowMenu.addAction(themeAct)

        folderAct.triggered.connect(self.addFiles)
        themeAct.triggered.connect(self.toggleColors)

        self.controllers( )

        self.setWindowTitle(self.title)
        self.toggleColors( )
        self.show( )

    def controllers(self):
        black = "#000000"
        yellow = "#cfb119"
        wid = QWidget(self)
        self.setCentralWidget(wid)

        self.vbox = QVBoxLayout( )
        hbox1 = QHBoxLayout( )
        hbox1.setContentsMargins(0, 0, 0, 0)
        hbox3 = QHBoxLayout( )
        hbox3.setContentsMargins(0, 0, 0, 0)
        hbox2 = QHBoxLayout( )
        hbox2.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget( )
        vlb = QLabel("VOLUME")
        vlb.setStyleSheet(f"background-color: {black}; color: {yellow}")
        vlb.resize(10, 10)
        vlb.setFont(QFont('Sanserif', 12, QFont.Bold))
        self.valuelb = QLabel("100")
        self.valuelb.setStyleSheet(f"background-color: {black}; color: {yellow}")
        self.valuelb.resize(10, 10)
        self.volslider = QSlider(Qt.Horizontal, self)
        self.volslider.setFocusPolicy(Qt.NoFocus)
        self.volslider.valueChanged[int].connect(self.changeVolume)
        self.volslider.valueChanged.connect(self.changeValue)
        self.volslider.setMinimum(0)
        self.volslider.setMaximum(100)
        self.volslider.setValue(100)
        self.vsl = QLabel("START")
        self.vsl.setStyleSheet(f"background-color: {black}; color: {yellow}")
        self.vsl.setFont(QFont('Sanserif', 12, QFont.Bold))
        self.vsl.resize(10, 10)
        self.tlb = QLabel("END")
        self.tlb.setStyleSheet(f"background-color: {black}; color: {yellow}")
        self.tlb.resize(10, 10)
        self.tlb.setFont(QFont('Sanserif', 12, QFont.Bold))

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_Position)

        self.player.positionChanged.connect(self.position_Changed)

        playBtn = QPushButton(clicked = self.playhandler)  # play button
        playBtn.setIcon(self.style( ).standardIcon(QStyle.SP_MediaPlay))
        playBtn.setToolTip("Reproduzir um arquivo de áudio")
        playBtn.setStyleSheet(f"background-color: {black}; color: {yellow}")
        playBtn.resize(10, 10)
        pauseBtn = QPushButton(clicked = self.pausehandler)  # pause button
        pauseBtn.setIcon(self.style( ).standardIcon(QStyle.SP_MediaPause))
        pauseBtn.setToolTip("Pausar a reprodução de um arquivo de áudio.")
        pauseBtn.setStyleSheet(f"background-color: {black}; color: {yellow}")
        pauseBtn.resize(10, 10)
        stopBtn = QPushButton(clicked = self.stophandler)  # stop button
        stopBtn.setIcon(self.style( ).standardIcon(QStyle.SP_MediaStop))
        stopBtn.setToolTip("Encerrar a reprodução de um arquivo de áudio.")
        stopBtn.setStyleSheet(f"background-color: {black}; color: {yellow}")
        stopBtn.resize(10, 10)

        prevBtn = QPushButton('Prev', clicked = self.prevSong)
        prevBtn.setToolTip("Reproduzir o áudio anterior.")
        prevBtn.setStyleSheet(f"background-color: {black}; color: {yellow}")
        prevBtn.resize(10, 10)
        prevBtn.setFont(QFont('Sanserif', 12, QFont.Bold))
        shuffleBtn = QPushButton('Shuffle', clicked = self.shufflelist)
        shuffleBtn.setToolTip("Reproduzir a lista de áudios de forma aleatória.")
        shuffleBtn.setStyleSheet(f"background-color: {black}; color: {yellow}")
        shuffleBtn.resize(10, 10)
        shuffleBtn.setFont(QFont('Sanserif', 12, QFont.Bold))
        nextBtn = QPushButton('Next', clicked = self.nextSong)
        nextBtn.setToolTip("Reproduzir o áudio seguinte.")
        nextBtn.setStyleSheet(f"background-color: {black}; color: {yellow}")
        nextBtn.resize(10, 10)
        nextBtn.setFont(QFont('Sanserif', 12, QFont.Bold))

        controlArea = QVBoxLayout( )  # centralWidget
        controls = QHBoxLayout( )
        controls.setContentsMargins(0, 0, 0, 0)
        playlistCtrlLayout = QHBoxLayout( )
        playlistCtrlLayout.setContentsMargins(0, 0, 0, 0)

        controls.addWidget(playBtn)
        controls.addWidget(pauseBtn)
        controls.addWidget(stopBtn)

        playlistCtrlLayout.addWidget(prevBtn)
        playlistCtrlLayout.addWidget(shuffleBtn)
        playlistCtrlLayout.addWidget(nextBtn)

        controlArea.addLayout(self.vbox)
        hbox1.addWidget(vlb)
        hbox1.addWidget(self.volslider)
        hbox1.addWidget(self.valuelb)
        hbox2.addWidget(self.vsl)
        hbox2.addWidget(self.slider)
        hbox2.addWidget(self.tlb)

        controlArea.addLayout(hbox1)
        controlArea.addLayout(controls)
        controlArea.addLayout(playlistCtrlLayout)
        controlArea.addLayout(hbox2)
        wid.setLayout(controlArea)

        self.statusBar( )
        self.playlist.currentMediaChanged.connect(self.songChanged)

    def addFiles(self):
        if self.playlist.mediaCount( ) > 0:
            self.fileIterator( )
        else:
            self.fileIterator( )
            for x in range(len(self.fl)):
                self.player.setPlaylist(self.playlist)
                self.player.playlist( ).setCurrentIndex(-x)
                self.player.play( )
            self.player.durationChanged.connect(self.duration_Changed)
            self.player.stop( )
            print(self.dur)

    def on_click(self):
        self.play = True
        for currentQTableWidgetItem in self.table.selectedItems( ):
            self.row = currentQTableWidgetItem.row( ) + 1
            self.v = currentQTableWidgetItem.text( )
        self.playSong( )

    def fileIterator(self):
        black = "#000000"
        yellow = "#cfb119"
        folderChosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', '~')
        try:
            self.drt = folderChosen
            cam = [path.join(self.drt, nome) for nome in ld(self.drt) if path.isfile(path.join(self.drt, nome))]
            self.fl = [x[len(self.drt) + 1:] for x in cam]

            self.table.setStyleSheet(f"background-color: {black}; color: {yellow}")
            self.table.setRowCount(len(self.fl))
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(("Nº", "TITLE", 'TIME'))
            self.table.setVerticalHeaderLabels(("",) * len(self.fl))
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table.itemDoubleClicked.connect(self.on_click)
        except Exception as e:
            self.errors(e)

        if folderChosen != None:
            self.left = 400
            self.top = 100
            self.width = 600
            self.height = 600
            self.setGeometry(self.left, self.top, self.width, self.height)
            iter = QDirIterator(folderChosen)
            iter.next( )
            while iter.hasNext( ):
                if not iter.fileInfo( ).isDir( ) and iter.filePath( ) != '.':
                    fInfo = iter.fileInfo( )
                    if fInfo.suffix( ) in ('mp3', 'ogg', 'wav', 'm4a'):
                        for x in range(len(self.fl)):
                            self.table.setItem(x, 0, QTableWidgetItem(str(x + 1)))
                            self.table.setItem(x, 1, QTableWidgetItem(self.fl[x]))
                            # self.table.setItem(x, 2, QTableWidgetItem(self.d[x]))
                            self.table.setColumnWidth(0, 45)
                            self.table.setColumnWidth(1, 360)
                            self.table.setColumnWidth(2, 80)
                        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(iter.filePath( ))))
                    else:
                        self.table.hide( )
                        self.setGeometry(500, 300, 0, 0)
                        QMessageBox.warning(self, "AC&MM MUSIC PLAYER:", "ARQUIVO INCOMPATÍVEL.")
                        break
                iter.next( )
            self.vbox.addWidget(self.table)

    def playhandler(self):
        if self.playlist.mediaCount( ) == 0:
            self.addFiles( )
        elif self.playlist.mediaCount( ) != 0:
            self.player.play( )

    def pausehandler(self):
        self.player.pause( )

    def stophandler(self):
        self.userAction = 0
        self.player.stop( )
        self.playlist.clear( )
        self.statusBar( ).showMessage("Playlist is empty now")

    def changeVolume(self, value):
        self.player.setVolume(value)

    def changeValue(self):
        v = self.volslider.value( )
        self.valuelb.setText(str(v))

    def prevSong(self):
        if self.playlist.mediaCount( ) == 0:
            self.addFiles( )
        elif self.playlist.mediaCount( ) > 0:
            self.player.playlist( ).previous( )

    def shufflelist(self):
        self.playlist.shuffle( )

    def nextSong(self):
        if self.playlist.mediaCount( ) == 0:
            self.addFiles( )
        elif self.playlist.mediaCount( ) > 0:
            self.player.playlist( ).next( )

    def songChanged(self, media):
        yellow = "#cfb119"
        red = "#ff0000"
        if not media.isNull( ):
            try:
                url = media.canonicalUrl( )
                self.song = url.fileName( )
                for x in range(len(self.fl)):
                    if self.song == self.fl[x]:
                        self.table.item(x, 0).setBackground(QColor(red))
                        self.table.item(x, 0).setForeground(QColor(yellow))
                        self.table.item(x, 1).setBackground(QColor(red))
                        self.table.item(x, 1).setForeground(QColor(yellow))
                        #self.table.item(x, 2).setBackground(QColor(red))
                        #self.table.item(x, 2).setForeground(QColor(yellow))
                self.statusBar( ).showMessage(self.song)
            except Exception as e:
                self.errors(e)

    def toggleColors(self):
        palette = QPalette( )
        if self.color == 0:
            palette.setColor(QPalette.Window, QColor(0, 0, 0))
            palette.setColor(QPalette.WindowText, Qt.darkYellow)
            palette.setColor(QPalette.Base, QColor(0, 0, 0))
            palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.yellow)
            palette.setColor(QPalette.Button, QColor(95, 0, 0))
            palette.setColor(QPalette.ButtonText, Qt.yellow)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(235, 101, 54))
            palette.setColor(QPalette.Highlight, QColor(255, 217, 0))
            palette.setColor(QPalette.HighlightedText, Qt.darkYellow)
            app.setPalette(palette)
            self.color = 1  # black
        elif self.color == 1:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.AlternateBase, Qt.white)
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(66, 155, 248))
            palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 0  # white

    def set_Position(self, position):
        self.player.setPosition(position)

    def position_Changed(self, progress):
        progress //= 1000
        if not self.slider.isSliderDown( ):
            self.slider.setValue(progress)
        self.setCounter(progress)

    def duration_Changed(self, duration):
        duration //= 1000
        self.duration = duration
        totTime = QTime((duration // 3600) % 60, (duration // 60) % 60, duration % 60, (duration * 1000) % 1000);
        totStr = totTime.toString('hh:mm:ss')
        self.slider.setRange(0, duration)
        self.slider.setMaximum(duration)
        self.dur.append(totStr)
        print(totStr)

    def setCounter(self, currentInfo):
        duration = self.duration
        if currentInfo or duration:
            currentTime = QTime((currentInfo // 3600) % 60, (currentInfo // 60) % 60, currentInfo % 60, (currentInfo * 1000) % 1000)
            totalTime = QTime((duration // 3600) % 60, (duration // 60) % 60, duration % 60, (duration * 1000) % 1000);
            #format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            self.curStr = currentTime.toString('hh:mm:ss')
            self.totStr = totalTime.toString('hh:mm:ss')
        else:
            self.totStr = ""
            self.curStr = ""
        self.vsl.setText(self.curStr)
        self.tlb.setText(self.totStr)

    def playSong(self):
        try:
            if self.play:
                a = self.row - 1
                url = QUrl.fromLocalFile(f"{self.drt}/{self.fl[a]}")
                content = QMediaContent(url)
                self.player.setMedia(content)
                self.playhandler( )
        except Exception as e:
            self.errors(e)

    def errors(self, e):
        self.dia = QDate.currentDate( )
        self.hoje = self.dia.toString("dd/MM/yy")
        self.hora = QTime.currentTime( )
        self.hr_err = self.hora.toString("hh:mm:ss")
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info( )
        fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err = f"{self.hoje} \n{self.hr_err} \n{e} \n{exc_type} \n{fname} \n{exc_tb.tb_lineno} \n"
        print(err)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App( )
    sys.exit(app.exec_( ))