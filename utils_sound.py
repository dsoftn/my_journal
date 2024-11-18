from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from typing import Union, Any
import os

from utils_terminal import TerminalUtility
from utils_internet import InternetUtility
from utils_file import FileUtility
from utils_settings import UTILS_Settings
from utils_signal import Signal


class SoundUtility:
    MINIMUM_VOLUME_WHEN_FORCE_SOUND = 40

    def __init__(self, media_source: str = None, volume: int = 100, muted: bool = False, **kwargs) -> None:
        """
        SoundUtility with the specified media source and optional parameters.

        Parameters:
        -----------
        media_source : str, optional
            The media source (e.g., file path or URL) for the sound effects.

        **kwargs:
            Additional keyword arguments.
            force_sound : int, optional
                Sound will be played if force_sound is True regardless of the volume or muted state.

        """
        self.media_source = media_source
        self.player = QMediaPlayer()

        self.__volume = volume if volume in range(0, 101) else 100
        self.__muted = muted

        self.force_sound = kwargs.get("force_sound", False)
        if self.force_sound:
            self.__volume = self.MINIMUM_VOLUME_WHEN_FORCE_SOUND if self.__volume < self.MINIMUM_VOLUME_WHEN_FORCE_SOUND else self.__volume
            self.__muted = False

        self.set_volume(self.__volume)
        self.set_muted(self.__muted)

        # Connect events with slots
        Signal.signalVolumeChanged.connect(self.set_volume)
    
    def play(self, media_source: str = None) -> bool:
        if media_source:
            self.media_source = media_source

        if self.media_source is None:
            TerminalUtility.WarningMessage("Sound media source not defined")
            return False
        
        if isinstance(self.media_source, QMediaContent):
            self.player.setMedia(self.media_source)
        elif isinstance(self.media_source, str):
            self.media_source = FileUtility.get_absolute_path(self.media_source)
            if not os.path.isfile(self.media_source):
                result = self._load_file_from_internet(self.media_source)
                if result:
                    self.media_source = result
                else:
                    TerminalUtility.WarningMessage("Invalid media source\ntype(self.media_source): #1\nself.media_source = #2\nLocal file not found\nFile cannot be retrieved from internet", [type(self.media_source), self.media_source])
                    return False
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_source)))
        else:
            TerminalUtility.WarningMessage("Invalid media source\ntype(self.media_source): #1\nself.media_source = #2", [type(self.media_source), self.media_source])
            return False
        
        self.player.play()
        return True
    
    def _load_file_from_internet(self, media_source: str) -> Union[str, None]:
        if not media_source.startswith("http"):
            return None
        
        file_name = FileUtility.join_folder_and_file_name(UTILS_Settings.TEMP_FOLDER, "temp_sound_file")

        result = InternetUtility.download_file_from_internet_with_urllib(self.media_source, file_name)
        if result:
            return file_name
        
        result = InternetUtility.download_file_from_internet_with_requests(self.media_source, file_name)
        if result:
            return file_name
        
        return None

    def stop(self) -> bool:
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
            return True
        return False
    
    def pause(self) -> bool:
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            return True
        return False
    
    def isPlaying(self) -> bool:
        return self.player.state() == QMediaPlayer.PlayingState
    
    def isPaused(self) -> bool:
        return self.player.state() == QMediaPlayer.PausedState
    
    def isStopped(self) -> bool:
        return self.player.state() == QMediaPlayer.StoppedState
    
    def isFinished(self) -> bool:
        return self.player.state() == QMediaPlayer.StoppedState
    
    def set_volume(self, volume: int, data: dict = None) -> bool:
        if not isinstance(volume, int):
            TerminalUtility.WarningMessage("Invalid volume value type, expected #1\ntype(volume): #2\nvolume = #3", ["integer", type(volume), volume])
            return False

        if volume < 0 or volume > 100:
            TerminalUtility.WarningMessage("Invalid volume value, must be between #1 and #2\nvolume = #3", [0, 100, volume])
            return False

        if self.force_sound:
            if volume < self.MINIMUM_VOLUME_WHEN_FORCE_SOUND:
                self.__volume = self.MINIMUM_VOLUME_WHEN_FORCE_SOUND
                result = False
            else:
                self.__volume = volume
                result = True
            
            if data and data.get("muted"):
                result = False

            self.player.setVolume(self.__volume)
            return result
        
        if data:
            if data.get("muted") is not None:
                self.set_muted(data.get("muted"))

        self.player.setVolume(volume)
        self.__volume = volume
        return True
    
    def get_volume(self) -> int:
        return self.player.volume()
    
    def set_muted(self, muted: bool) -> bool:
        if not isinstance(muted, bool):
            TerminalUtility.WarningMessage("Invalid muted value type, expected #1\ntype(muted): #2\nmuted = #3", ["boolean", type(muted), muted])
            return False
        
        self.__muted = muted
        self.player.setMuted(self.__muted)

    def get_muted(self) -> bool:
        return self.__muted

    def get_media_source(self) -> Union[str, QMediaContent]:
        return self.media_source
    
    def set_media_source(self, media_source: Union[str, QMediaContent]):
        self.media_source = media_source
    
    def close(self):
        self.player.stop()

    def deleteLater(self):
        self.close()
        self.player.deleteLater()

    



