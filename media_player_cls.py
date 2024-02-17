from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStyle, QSlider, 
                             QFrame, QSizePolicy, QSpacerItem)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl

import os
import sys


class MediaPlayer(QFrame):
    BG_COLOR_NORMAL = "#005500"
    BG_COLOR_HOVER = "#55aaff"
    BG_COLOR_DISABLED = "#aa0000"

    def __init__(self, parent_widget: QWidget = None, media_source: str|QUrl = None) -> None:
        super().__init__(parent_widget)

        self.parent_widget = parent_widget
        self.media_source = media_source
        self.playing = False
        self.paused = False

        self.media_player = QMediaPlayer(self)
        if media_content := self.media_content():
            self.media_player.setMedia(media_content)

        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        self._define_widget()

        # Events
        # self.sld_time.sliderMoved.connect(self.sld_time_moved)
        self.sld_time.mouseReleaseEvent = self.sld_time_moved
        self.media_player.positionChanged.connect(self.sld_time.setValue)
        self.media_player.durationChanged.connect(self.media_player_duration_changed)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)

        self.btn_start.clicked.connect(self.btn_start_click)
        self.btn_vol.clicked.connect(self.btn_vol_click)
        self.btn_pause.clicked.connect(self.btn_pause_click)
        self.sld_vol.valueChanged.connect(self.set_volume)

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.stop()
            self.media_player.setPosition(0)
            self.playing = False
            self.paused = False
            self.btn_start.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.btn_pause.setEnabled(False)

    def media_player_duration_changed(self, duration: int):
        self.sld_time.setRange(0, duration)

    def sld_time_moved(self, e):
        if self.sld_time.value() <= self.media_player.duration():
            self.media_player.stop()
            self.media_player.setPosition(self.sld_time.value())
            self.media_player.play()
        QSlider.mouseReleaseEvent(self.sld_time, e)

    def set_media_source(self, media_source: str|QUrl) -> bool:
        if media_source == "":
            self.setDisabled(True)
            return
        else:
            self.setEnabled(True)

        self.media_source = media_source
        if self.media_content():
            self.media_player.setMedia(self.media_content())
            self.sld_time.setEnabled(True)
            if not self.media_player.isVideoAvailable():
                self.video_widget.setVisible(False)
            return True
        return False

    def stop(self):
        self.media_player.stop()
        self.media_player.setPosition(0)
        self.playing = False
        self.paused = False
        self.btn_start.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_pause.setEnabled(False)

    def play(self):
        self.media_player.setPosition(self.sld_time.value())
        self.media_player.play()
        self.paused = False
        self.playing = True
        self.btn_start.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_pause.setEnabled(True)

    def btn_pause_click(self):
        if not self.playing:
            return
        if self.paused:
            self.media_player.play()
            self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.paused = False
        else:
            self.media_player.pause()
            self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.paused = True

    def btn_vol_click(self):
        if self.media_player.isMuted():
            self.media_player.setMuted(False)
            self.btn_vol.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        else:
            self.media_player.setMuted(True)
            self.btn_vol.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))

    def set_volume(self, value: int):
        self.media_player.setVolume(value)
    
    def btn_start_click(self):
        if self.playing:
            self.media_player.stop()
            self.media_player.setPosition(0)
            self.playing = False
            self.paused = False
            self.btn_start.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.btn_pause.setEnabled(False)
        else:
            self.media_player.setPosition(self.sld_time.value())
            self.media_player.play()
            self.paused = False
            self.playing = True
            self.btn_start.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
            self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.btn_pause.setEnabled(True)

    def media_content(self):
        if self.media_source is None:
            return None
        if isinstance(self.media_source, QUrl):
            self.media_source = self.media_source.url()
        if os.path.isfile(self.media_source):
            return QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.media_source)))
        else:
            return QMediaContent(QUrl(self.media_source))

    def _define_widget(self):
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        # Video Widget
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.v_layout.addWidget(self.video_widget)
        # Time
        self.sld_time = QSlider(Qt.Horizontal)
        self.sld_time.setParent(self)
        self.sld_time.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        if not self.media_content():
            self.sld_time.setEnabled(False)
        self.v_layout.addWidget(self.sld_time)
        # Controls
        self.btn_start = QPushButton(self)
        self.btn_start.setStyleSheet("QPushButton {background-color: " + self.BG_COLOR_NORMAL + ";} QPushButton:hover {background-color: " + self.BG_COLOR_HOVER + ";} QPushButton:disabled {background-color: " + self.BG_COLOR_DISABLED + ";}")
        self.btn_start.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_start.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.btn_pause = QPushButton(self)
        self.btn_pause.setStyleSheet("QPushButton {background-color: " + self.BG_COLOR_NORMAL + ";} QPushButton:hover {background-color: " + self.BG_COLOR_HOVER + ";} QPushButton:disabled {background-color: " + self.BG_COLOR_DISABLED + ";}")
        self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_pause.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.btn_pause.setEnabled(False)

        self.sld_vol = QSlider(Qt.Horizontal)
        self.sld_vol.setParent(self)
        self.sld_vol.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.sld_vol.setMaximum(100)
        self.sld_vol.setValue(self.media_player.volume())

        self.btn_vol = QPushButton(self)
        self.btn_vol.setStyleSheet("QPushButton {background-color: " + self.BG_COLOR_NORMAL + ";} QPushButton:hover {background-color: " + self.BG_COLOR_HOVER + ";} QPushButton:disabled {background-color: " + self.BG_COLOR_DISABLED + ";}")
        self.btn_vol.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.btn_vol.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.v_layout.addLayout(self.h_layout)
        self.h_layout.addWidget(self.btn_start, alignment=Qt.AlignLeft)
        self.h_layout.addWidget(self.btn_pause, alignment=Qt.AlignLeft)
        self.h_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.h_layout.addWidget(self.sld_vol, alignment=Qt.AlignRight)
        self.h_layout.addWidget(self.btn_vol, alignment=Qt.AlignRight)

        self.setLayout(self.v_layout)
        self.resize(200, 60)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    aa = "D:/1.mp4"
    print (os.path.isfile(aa))
    player = MediaPlayer(media_source=aa)
    player.show()
    sys.exit(app.exec_())
        
