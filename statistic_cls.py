from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout, QWidget, QSpacerItem,
                             QSizePolicy, QListWidget, QFileDialog, QDialog, QLabel, QListWidgetItem,  QLineEdit,
                             QMessageBox, QComboBox,  QProgressBar, QCheckBox, QKeySequenceEdit, QRadioButton,
                             QGroupBox, QGraphicsOpacityEffect, QSpinBox, QColorDialog, QFontDialog)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor, QColor, QMouseEvent, QMovie
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5 import uic, QtGui, QtCore

from collections import Counter
import time
import os
import json

import settings_cls
import utility_cls
import db_tag_cls
import media_player_cls
import text_filter_cls


class Statistic:
    END_OF_WORD = [" ", ",", ":", ";", ".", "!", "?", "\n", "\t", "(", ")", "/", "@", "#", "\"", "'", "{", "}", "[", "]", "_", "-", "*", "&", "^", "$", "+", "=", "|", "<", ">"]
    END_OF_SENTENCE = [".", "!", "?", "\n"]

    def __init__(self, settings: settings_cls.Settings):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("statistic_ui_file_path"), self)

        # Define variables



