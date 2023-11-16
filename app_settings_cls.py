from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout,
    QGridLayout, QWidget, QSpacerItem, QSizePolicy, QListWidget, QFileDialog, QDialog,
    QLabel, QListWidgetItem, QDesktopWidget, QLineEdit, QCalendarWidget, QHBoxLayout,
    QComboBox, QSlider, QProgressBar, QCheckBox, QFileIconProvider, QApplication, QTreeWidget,
    QTreeWidgetItem, QRadioButton, QGroupBox)
from PyQt5.QtGui import (QIcon, QFont, QFontMetrics, QStaticText, QPixmap, QCursor, QDesktopServices,
     QImage, QClipboard, QColor)
from PyQt5.QtCore import (QMetaMethod, QSize, Qt, pyqtSignal, QObject, QCoreApplication, QRect,
    QPoint, QTimer, QThread, QDate, QEvent, QUrl, QFileInfo, QMimeDatabase)
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtMultimedia import QSound


from googletrans import Translator
import googletrans
import datetime
import time
import copy
import hashlib
import urllib.request
from urllib.parse import urlparse
import os
import shlex
import winreg
import shutil
import mimetypes
import json
import random

import settings_cls


class Settings(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("app_settings_ui_file_path"), self)

        # Create shared variable
        if "app_settings_shared_variable" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("app_settings_shared_variable", {})
        self.data: dict = self.get_appv("app_settings_shared_variable")

        # Define other variables
        self._parent_widget = parent_widget

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self._populate_widgets()

        # Connect events with slots

        self.show()

    def _populate_widgets(self):
        self.data = self._populate_data_variable()

    def _populate_data_variable(self) -> dict:
        self.menu = [
            "general"
        ]

        r = {}
        # Populate data dictionary

    def _save_data_variable(self, section: str = None):
        if section:
            section = [section]
        else:
            section = self.menu

    def _set_default_data_variable(self, section: str = None):
        if section:
            section = [section]
        else:
            section = self.menu
    
    def _load_win_position(self):
        if "app_settings_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("app_settings_win_geometry")
            x = g.setdefault("pos_x", self.pos().x())
            y = g.setdefault("pos_y", self.pos().y())
            w = g.setdefault("width", self.width())
            h = g.setdefault("height", self.height())
            self.move(x, y)
            self.resize(w, h)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if "app_settings_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("app_settings_win_geometry", {}, save_to_file=True)

        g = self.get_appv("app_settings_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        return super().closeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")

        self.area_menu: QScrollArea = self.findChild(QScrollArea, "area_menu")
        self.area_settings: QScrollArea = self.findChild(QScrollArea, "area_settings")

        self.btn_save: QPushButton = self.findChild(QPushButton, "btn_save")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")

        self.frm_menu: QFrame = self.findChild(QFrame, "frm_menu")

        # Menu item: General Settings
        self.frm_menu_general: QFrame = self.findChild(QFrame, "frm_menu_general")
        self.lbl_menu_general_icon: QLabel = self.findChild(QLabel, "lbl_menu_general_icon")
        self.lbl_menu_general_title: QLabel = self.findChild(QLabel, "lbl_menu_general_title")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("app_settings_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("app_settings_lbl_title_tt"))

        self.btn_save.setText(self.getl("app_settings_btn_save_text"))
        self.btn_save.setToolTip(self.getl("app_settings_btn_save_tt"))

        self.btn_cancel.setText(self.getl("btn_cancel"))

        # Menu item: General Settings
        self.lbl_menu_general_title.setText(self.getl("app_settings_lbl_menu_general_title_text"))
        self.lbl_menu_general_title.setToolTip(self.getl("app_settings_lbl_menu_general_title_tt"))
        self.frm_menu_general.setToolTip(self.getl("app_settings_lbl_menu_general_title_tt"))
        self.lbl_menu_general_icon.setToolTip(self.getl("app_settings_lbl_menu_general_title_tt"))


    def _setup_widgets_apperance(self):
        self._define_user_settings_win_apperance()

        self.btn_save.setStyleSheet(self.getv("app_settings_btn_save_text_stylesheet"))
        self.btn_cancel.setStyleSheet(self.getv("app_settings_btn_cancel_text_stylesheet"))

        self._define_labels_apperance(self.lbl_title, "app_settings_lbl_title")

        # Menu item: General Settings
        self.frm_menu_general.setStyleSheet(self.getv("app_settings_frm_menu_item_stylesheet"))
        self._define_labels_apperance(self.lbl_menu_general_title, "app_settings_lbl_menu_item")
        self._define_labels_apperance(self.lbl_menu_general_icon, "app_settings_lbl_menu_item")


    def _define_user_settings_win_apperance(self):
        self.setStyleSheet(self.getv("app_settings_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("app_settings_win_icon_path")))
        self.setWindowTitle(self.getl("app_settings_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        # self.setFixedSize(1025, 535)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))



