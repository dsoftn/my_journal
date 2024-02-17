from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QGridLayout, QWidget, 
                             QSizePolicy, QListWidget, QFileDialog, QDialog, QLabel, QListWidgetItem, 
                             QDesktopWidget, QLineEdit, QCalendarWidget, QHBoxLayout, QComboBox, 
                             QProgressBar, QCheckBox, QFileIconProvider, QTreeWidget, QTreeWidgetItem, 
                             QRadioButton, QGroupBox, QMessageBox, QApplication, QSpinBox)
from PyQt5.QtGui import (QMovie, QMouseEvent, QCursor, QPixmap)
from PyQt5.QtCore import (QSize, Qt, pyqtSignal, QObject, QCoreApplication, QRect,QPoint, QTimer, 
                          QDate, QFileInfo, QMimeDatabase, QEvent)
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtMultimedia import QSound


import warnings
import inspect
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
from cyrtranslit import to_latin

import settings_cls
from stylesheet_cls import StyleSheet
import utility_cls


def warning_message(message: str, arguments: list = None, print_only: bool = False, warning_type: type = RuntimeWarning):
    count = 1
    if arguments:
        if isinstance(arguments, str):
            arguments = [arguments]
        for argument in arguments:
            message = message.replace("#" + str(count), f'"\033[31m{argument}\033[33m"')
            count += 1

    text = f"\n\033[34mWarning: \033[33m{message}\033[0m"
    if print_only:
        print(text.strip())
    else:
        warnings.warn(text, warning_type)


class AbstractProperties:
    def __init__(self) -> None:

        self.sections = [
            "Widget_PushButton_Properties",
            "Widget_Dialog_Properties",
        ]

    def name(self):
        return self.__class__.__name__

    def from_dict(self, properties_dict: dict, only_dedicated: bool = True) -> None:
        """
        Set properties of the object from a dictionary, optionally filtering by dedicated properties.

        Parameters:
        properties_dict: dict
            A dictionary containing properties to be set on the object.
        only_dedicated: bool, optional
            If True, only properties dedicated to the object (properties that refer to this object) will be set (default is True).

        Raises:
        ValueError: If the properties_dict is not a dictionary, or if a property value is not a dictionary when expected.

        Notes:
        - Properties prefixed with '_' followed by the object's name (private properties) are skipped.
        - Nested properties within the object's name are set if not skipped and dedicated.

        Returns:
        None
        """
        if properties_dict is None:
            return
        
        if not isinstance(properties_dict, dict):
            raise ValueError(f"The properties_dict must be a dictionary not '{type(properties_dict)}'.")
        
        for section in properties_dict:
            if section.startswith(f"_{self.name()}"):
                warning_message("Property name in properties_dict #1 is not allowed. SKIPPED!", section)
                continue

            if section not in self.sections:
                dict_property_name = section
                if dict_property_name.startswith(f"{self.name()}_"):
                    dict_property_name = dict_property_name[len(f"{self.name()}_"):]

                if not only_dedicated or (only_dedicated and dict_property_name in self.__dict__):
                    self.__dict__[dict_property_name] = properties_dict[section]

            else:
                if not isinstance(properties_dict[section], dict):
                    raise ValueError(f"The properties_dict['{section}'] must be a dictionary not '{type(properties_dict[section])}'.")
                
                if section != self.name():
                    continue

                for property_name in properties_dict[section]:
                    if property_name.startswith(f"_{self.name()}"):
                        warning_message("Property name in properties_dict #1 is not allowed. SKIPPED!", property_name)
                        continue

                    dict_property_name = property_name
                    if dict_property_name.startswith(f"{self.name()}_"):
                        dict_property_name = dict_property_name[len(f"{self.name()}_"):]

                    if not only_dedicated or (only_dedicated and dict_property_name in self.__dict__):
                        self.__dict__[dict_property_name] = properties_dict[section][property_name]

    def to_dict(self) -> dict:
        result = {}
        for property_name, property_value in self.__dict__.items():
            if property_name.startswith(f"_{self.name()}"):
                continue

            result[property_name] = property_value
        
        return result


class AbstractWidget:
    def __init__(self) -> None:
        self.widget: QWidget = None
        self.main_win: QWidget = None
        self.properties = None

        self.SUPER_CLASS_WIDGET = None

        self._tap_label: QLabel = None
        self._tap_sound: QSound = None

        self.__ignore_change_size = False
        self.__ignore_change_stylesheet = False
        self.__ignore_show_animation = False

    def _get_qwidget_class(self) -> QWidget:
        widget_type = self._get_widget_type()
        result = None
        if widget_type.lower() == "qpushbutton":
            result = QPushButton
        elif widget_type.lower() == "qlabel":
            result = QLabel
        elif widget_type.lower() == "qframe":
            result = QFrame
        elif widget_type.lower() == "qcheckbox":
            result = QCheckBox
        elif widget_type.lower() == "qcombobox":
            result = QComboBox
        elif widget_type.lower() == "qspinbox":
            result = QSpinBox
        elif widget_type.lower() == "qtextedit":
            result = QTextEdit
        elif widget_type.lower() == "qlineedit":
            result = QLineEdit
        elif widget_type.lower() == "qlistwidget":
            result = QListWidget


        if result is None:
            result = QWidget
            warning_message("Widget type not supported: #1", widget_type)
        
        return result

    def _get_widget_type(self) -> str:
        widget_type = str(type(self.widget))
        widget_type = widget_type[widget_type.rfind(".") + 1:widget_type.rfind("'")]
        return widget_type

    def _tap_event_change_size(self, e: QMouseEvent, e_enabled: bool, e_percent: int) -> QSize:
        if self.__ignore_change_size:
            return None, None
        
        if not e_enabled:
            return None, None
        
        self.__ignore_change_size = True

        scale = (100 + e_percent) / 100

        old_size = self.widget.size()
        old_pos = self.widget.pos()

        if self.widget.sizePolicy().horizontalPolicy() == QSizePolicy.Fixed:
            self.widget.setFixedWidth(int(self.widget.width() * scale))
        else:
            self.widget.resize(int(self.widget.width() * scale), self.widget.height())
        
        if self.widget.sizePolicy().verticalPolicy() == QSizePolicy.Fixed:
            self.widget.setFixedHeight(int(self.widget.height() * scale))
        else:
            self.widget.resize(self.widget.width(), int(self.widget.height() * scale))

        x = old_pos.x() + int((old_size.width() - self.widget.width()) / 2)
        y = old_pos.y() + int((old_size.height() - self.widget.height()) / 2)

        self.widget.move(x, y)

        self.widget.raise_()

        return old_size, old_pos
    
    def _tap_event_change_size_stop(self, old_size: QSize, old_pos: QPoint):
        try:
            if self.widget:
                if self.widget.sizePolicy().horizontalPolicy() == QSizePolicy.Fixed:
                    self.widget.setFixedWidth(old_size.width())
                else:
                    self.widget.resize(old_size.width(), self.widget.height())
                
                if self.widget.sizePolicy().verticalPolicy() == QSizePolicy.Fixed:
                    self.widget.setFixedHeight(old_size.height())
                else:
                    self.widget.resize(self.widget.width(), old_size.height())
        
                self.widget.move(old_pos.x(), old_pos.y())
        except Exception as e:
            warning_message(f"Exception in _tap_event_change_size_stop\n#1", [str(e)], print_only=True)

        self.__ignore_change_size = False

    def _tap_event_change_stylesheet(self, e: QMouseEvent, e_enabled: bool, e_qss: str) -> str:
        if self.__ignore_change_stylesheet:
            return None
        
        if not e_enabled:
            return None
        
        self.__ignore_change_stylesheet = True

        widget_type = self._get_widget_type()
        
        old_stylesheet = self.widget.styleSheet()
        old_style = StyleSheet(widget_name="QPushButton")
        old_style.stylesheet = old_stylesheet

        # Combine old and new stylesheet
        new_stylesheet = e_qss

        new_style = StyleSheet(widget_name="QPushButton")
        new_style.stylesheet = new_stylesheet
        new_style.widget_name = widget_type

        new_style.merge_stylesheet(stylesheet=old_style)

        new_stylesheet = new_style.stylesheet

        # Merge new and old stylesheet
        self.widget.setStyleSheet(new_stylesheet)

        return old_stylesheet

    def _tap_event_change_stylesheet_stop(self, old_stylesheet: str):
        try:
            if self.widget:
                self.widget.setStyleSheet(old_stylesheet)
        except Exception as e:
            warning_message(f"Exception in _tap_event_change_stylesheet_stop\n#1", [str(e)], print_only=True)

        self.__ignore_change_stylesheet = False

    def _tap_event_show_animation(self, e: QMouseEvent, e_enabled: bool, e_duration_ms: int, e_width: int, e_height: int, event_type: str) -> bool:
        if self.__ignore_show_animation:
            return None
        if isinstance(e, QMouseEvent):
            e_pos = e.globalPos()
        else:
            e_pos = QCursor().pos()

        if not e_enabled:
            return None
        
        self.__ignore_show_animation = True

        if self._tap_label is None:
            self._tap_label = self._create_tap_label(self.main_win, event_type=event_type)
        
        self._tap_label.move(self.main_win.mapFromGlobal(e_pos).x() - e_width // 2, self.main_win.mapFromGlobal(e_pos).y() - e_height // 2)
        self._tap_label.show()
        self._tap_label.raise_()
        try:
            self._tap_label.movie().jumpToFrame(0)
            frame_duration = self._tap_label.movie().nextFrameDelay()
            frame_count = self._tap_label.movie().frameCount()
            total_duration = frame_duration * frame_count
            desired_duration = int(e_duration_ms * 0.80)
            speed = total_duration / desired_duration
            self._tap_label.movie().setSpeed(int(speed*100))
        except:
            warning_message("Error setting the speed of the animation. (#1) type.", event_type, print_only=True)

        self._tap_label.movie().start()

        if self._tap_label.movie().isValid():
            return True
        
        return False

    def _tap_event_show_animation_stop(self):
        try:
            if self._tap_label:
                self._tap_label.movie().stop()
                self._tap_label.hide()
        except Exception as e:
            warning_message(f"Exception in _tap_event_show_animation_stop\n#1", [str(e)], print_only=True)

        self.__ignore_show_animation = False

    def _tap_event_play_sound(self, e: QMouseEvent, e_enabled: bool, e_file_path: str) -> bool:
        if not e_enabled:
            return None
        
        try:
            if self._tap_sound is None:
                self._tap_sound = QSound(e_file_path)

            self._tap_sound.play()
            return True
        except:
            return False

    def _create_tap_label(self, parent_widget: QWidget, event_type: str) -> QLabel:
        if event_type == "tap":
            bg_color = self.properties.tap_event_show_animation_background_color
            file = self.properties.tap_event_show_animation_file_path
            w = self.properties.tap_event_show_animation_width
            h = self.properties.tap_event_show_animation_height
        elif event_type == "enter":
            bg_color = self.properties.enter_event_show_animation_background_color
            file = self.properties.enter_event_show_animation_file_path
            w = self.properties.enter_event_show_animation_width
            h = self.properties.enter_event_show_animation_height
        elif event_type == "leave":
            bg_color = self.properties.leave_event_show_animation_background_color
            file = self.properties.leave_event_show_animation_file_path
            w = self.properties.leave_event_show_animation_width
            h = self.properties.leave_event_show_animation_height
        else:
            raise ValueError(f"Invalid event_type: {event_type}")

        lbl = QLabel(parent_widget)
        lbl.setStyleSheet(f"QLabel {{ background-color: {bg_color}; border: 0px;}}")
        lbl.setFixedSize(w, h)
        lbl.setScaledContents(True)
        tap_movie = QMovie(file)
        tap_movie.setScaledSize(QSize(w, h))
        lbl.setMovie(tap_movie)
        tap_movie.frameChanged.connect(self._tap_movie_frame_changed)
        lbl.hide()

        return lbl

    def _tap_movie_frame_changed(self, frame):
        try:
            if self._tap_label:
                if frame == self._tap_label.movie().frameCount() - 1:
                    self._tap_label.movie().setPaused(True)
        except Exception as e:
            warning_message(f"Exception in _tap_movie_frame_changed\n#1", [str(e)], print_only=True)

    def close_me(self):
        if self._tap_label is not None:
            self._tap_label.movie().stop()
            self._tap_label.movie().frameChanged.disconnect(self._tap_movie_frame_changed)
            self._tap_label.hide()
            self._tap_label.deleteLater()

        if self._tap_sound is not None:
            self._tap_sound.stop()
            self._tap_sound.deleteLater()

    def activate(self):
        warning_message("AbstractWidget.activate() not implemented (#1)", self.__class__.__name__, warning_type=UserWarning)

    def update_from_dict(self, properties_dict: dict, only_dedicated: bool = True) -> None:
        self.properties.from_dict(properties_dict, only_dedicated)

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result

    def _set_widget_cursor(self, cursor: str, widget: QWidget):
        if not cursor:
            widget.setCursor(QCursor())
        else:
            if self._get_integer(cursor) is not None:
                cur = QCursor()
                cur.setShape(self._get_integer(cursor))
                widget.setCursor(cur)
            else:
                img = QPixmap()
                result = img.load(cursor)
                if result:
                    if self.properties.cursor_keep_aspect_ratio:
                        img = img.scaled(self.properties.cursor_width, self.properties.cursor_height, Qt.KeepAspectRatio)
                    else:
                        img = img.scaled(self.properties.cursor_width, self.properties.cursor_height)
    
                    widget.setCursor(QCursor(img))
                else:
                    warning_message("Unable to set cursor: #1", cursor)


class GlobalWidgetsProperties(AbstractProperties):
    def __init__(self, settings_dict: dict) -> None:
        super().__init__()

        self.setup_default_properties(settings_dict)

    def setup_default_properties(self, settings_dict: dict):
        for section in self.sections:
            if section not in settings_dict:
                settings_dict[section] = {}
        
        # Pushbutton cursor
        self.Widget_PushButton_Properties_allow_cursor_change = settings_dict["Widget_PushButton_Properties"].get("allow_cursor_change", False)
        self.Widget_PushButton_Properties_cursor = settings_dict["Widget_PushButton_Properties"].get("cursor", "")
        self.Widget_PushButton_Properties_cursor_width = settings_dict["Widget_PushButton_Properties"].get("cursor_width", 20)
        self.Widget_PushButton_Properties_cursor_height = settings_dict["Widget_PushButton_Properties"].get("cursor_height", 20)
        self.Widget_PushButton_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_PushButton_Properties"].get("cursor_keep_aspect_ratio", True)
        # Allow bypass mouse press event
        self.Widget_PushButton_Properties_allow_bypass_mouse_press_event = settings_dict["Widget_PushButton_Properties"].get("allow_bypass_mouse_press_event", False)
        # Tap event - animation
        self.Widget_PushButton_Properties_tap_event_show_animation_enabled = settings_dict["Widget_PushButton_Properties"].get("tap_event_show_animation_enabled", False)
        self.Widget_PushButton_Properties_tap_event_show_animation_file_path = settings_dict["Widget_PushButton_Properties"].get("tap_event_show_animation_file_path", "")
        self.Widget_PushButton_Properties_tap_event_show_animation_duration_ms = settings_dict["Widget_PushButton_Properties"].get("tap_event_show_animation_duration_ms", 100)
        self.Widget_PushButton_Properties_tap_event_show_animation_width = settings_dict["Widget_PushButton_Properties"].get("tap_event_show_animation_width", 20)
        self.Widget_PushButton_Properties_tap_event_show_animation_height = settings_dict["Widget_PushButton_Properties"].get("tap_event_show_animation_height", 20)
        self.Widget_PushButton_Properties_tap_event_show_animation_background_color = settings_dict["Widget_PushButton_Properties"].get("tap_event_show_animation_background_color", "transparent")
        # Tap event - play sound
        self.Widget_PushButton_Properties_tap_event_play_sound_enabled = settings_dict["Widget_PushButton_Properties"].get("tap_event_play_sound_enabled", False)
        self.Widget_PushButton_Properties_tap_event_play_sound_file_path = settings_dict["Widget_PushButton_Properties"].get("tap_event_play_sound_file_path", "")
        # Tap event - change stylesheet
        self.Widget_PushButton_Properties_tap_event_change_stylesheet_enabled = settings_dict["Widget_PushButton_Properties"].get("tap_event_change_stylesheet_enabled", False)
        self.Widget_PushButton_Properties_tap_event_change_qss_stylesheet = settings_dict["Widget_PushButton_Properties"].get("tap_event_change_qss_stylesheet", "")
        self.Widget_PushButton_Properties_tap_event_change_stylesheet_duration_ms = settings_dict["Widget_PushButton_Properties"].get("tap_event_change_stylesheet_duration_ms", 100)
        # Tap event - change size
        self.Widget_PushButton_Properties_tap_event_change_size_enabled = settings_dict["Widget_PushButton_Properties"].get("tap_event_change_size_enabled", False)
        self.Widget_PushButton_Properties_tap_event_change_size_percent = settings_dict["Widget_PushButton_Properties"].get("tap_event_change_size_percent", 10)
        self.Widget_PushButton_Properties_tap_event_change_size_duration_ms = settings_dict["Widget_PushButton_Properties"].get("tap_event_change_size_duration_ms", 100)
        # Allow bypass enter event
        self.Widget_PushButton_Properties_allow_bypass_enter_event = settings_dict["Widget_PushButton_Properties"].get("allow_bypass_enter_event", False)
        # Enter event - animation
        self.Widget_PushButton_Properties_enter_event_show_animation_enabled = settings_dict["Widget_PushButton_Properties"].get("enter_event_show_animation_enabled", False)
        self.Widget_PushButton_Properties_enter_event_show_animation_file_path = settings_dict["Widget_PushButton_Properties"].get("enter_event_show_animation_file_path", "")
        self.Widget_PushButton_Properties_enter_event_show_animation_duration_ms = settings_dict["Widget_PushButton_Properties"].get("enter_event_show_animation_duration_ms", 100)
        self.Widget_PushButton_Properties_enter_event_show_animation_width = settings_dict["Widget_PushButton_Properties"].get("enter_event_show_animation_width", 20)
        self.Widget_PushButton_Properties_enter_event_show_animation_height = settings_dict["Widget_PushButton_Properties"].get("enter_event_show_animation_height", 20)
        self.Widget_PushButton_Properties_enter_event_show_animation_background_color = settings_dict["Widget_PushButton_Properties"].get("enter_event_show_animation_background_color", "transparent")
        # Enter event - play sound
        self.Widget_PushButton_Properties_enter_event_play_sound_enabled = settings_dict["Widget_PushButton_Properties"].get("enter_event_play_sound_enabled", False)
        self.Widget_PushButton_Properties_enter_event_play_sound_file_path = settings_dict["Widget_PushButton_Properties"].get("enter_event_play_sound_file_path", "")
        # Enter event - change stylesheet
        self.Widget_PushButton_Properties_enter_event_change_stylesheet_enabled = settings_dict["Widget_PushButton_Properties"].get("enter_event_change_stylesheet_enabled", False)
        self.Widget_PushButton_Properties_enter_event_change_qss_stylesheet = settings_dict["Widget_PushButton_Properties"].get("enter_event_change_qss_stylesheet", "")
        self.Widget_PushButton_Properties_enter_event_change_stylesheet_duration_ms = settings_dict["Widget_PushButton_Properties"].get("enter_event_change_stylesheet_duration_ms", 100)
        # Enter event - change size
        self.Widget_PushButton_Properties_enter_event_change_size_enabled = settings_dict["Widget_PushButton_Properties"].get("enter_event_change_size_enabled", False)
        self.Widget_PushButton_Properties_enter_event_change_size_percent = settings_dict["Widget_PushButton_Properties"].get("enter_event_change_size_percent", 10)
        self.Widget_PushButton_Properties_enter_event_change_size_duration_ms = settings_dict["Widget_PushButton_Properties"].get("enter_event_change_size_duration_ms", 100)
        # Allow bypass leave event
        self.Widget_PushButton_Properties_allow_bypass_leave_event = settings_dict["Widget_PushButton_Properties"].get("allow_bypass_leave_event", False)
        # Leave event - animation
        self.Widget_PushButton_Properties_leave_event_show_animation_enabled = settings_dict["Widget_PushButton_Properties"].get("leave_event_show_animation_enabled", False)
        self.Widget_PushButton_Properties_leave_event_show_animation_file_path = settings_dict["Widget_PushButton_Properties"].get("leave_event_show_animation_file_path", "")
        self.Widget_PushButton_Properties_leave_event_show_animation_duration_ms = settings_dict["Widget_PushButton_Properties"].get("leave_event_show_animation_duration_ms", 100)
        self.Widget_PushButton_Properties_leave_event_show_animation_width = settings_dict["Widget_PushButton_Properties"].get("leave_event_show_animation_width", 20)
        self.Widget_PushButton_Properties_leave_event_show_animation_height = settings_dict["Widget_PushButton_Properties"].get("leave_event_show_animation_height", 20)
        self.Widget_PushButton_Properties_leave_event_show_animation_background_color = settings_dict["Widget_PushButton_Properties"].get("leave_event_show_animation_background_color", "transparent")
        # Leave event - play sound
        self.Widget_PushButton_Properties_leave_event_play_sound_enabled = settings_dict["Widget_PushButton_Properties"].get("leave_event_play_sound_enabled", False)
        self.Widget_PushButton_Properties_leave_event_play_sound_file_path = settings_dict["Widget_PushButton_Properties"].get("leave_event_play_sound_file_path", "")
        # Leave event - change stylesheet
        self.Widget_PushButton_Properties_leave_event_change_stylesheet_enabled = settings_dict["Widget_PushButton_Properties"].get("leave_event_change_stylesheet_enabled", False)
        self.Widget_PushButton_Properties_leave_event_change_qss_stylesheet = settings_dict["Widget_PushButton_Properties"].get("leave_event_change_qss_stylesheet", "")
        self.Widget_PushButton_Properties_leave_event_change_stylesheet_duration_ms = settings_dict["Widget_PushButton_Properties"].get("leave_event_change_stylesheet_duration_ms", 100)
        # Leave event - change size
        self.Widget_PushButton_Properties_leave_event_change_size_enabled = settings_dict["Widget_PushButton_Properties"].get("leave_event_change_size_enabled", False)
        self.Widget_PushButton_Properties_leave_event_change_size_percent = settings_dict["Widget_PushButton_Properties"].get("leave_event_change_size_percent", 10)
        self.Widget_PushButton_Properties_leave_event_change_size_duration_ms = settings_dict["Widget_PushButton_Properties"].get("leave_event_change_size_duration_ms", 100)

        # DIALOG
        # Window drag
        self.Widget_Dialog_Properties_window_drag_enabled = settings_dict["Widget_Dialog_Properties"].get("window_drag_enabled", True)
        self.Widget_Dialog_Properties_window_drag_widgets = settings_dict["Widget_Dialog_Properties"].get("window_drag_widgets", [])
        self.Widget_Dialog_Properties_allow_drag_widgets_cursor_change = settings_dict["Widget_Dialog_Properties"].get("allow_drag_widgets_cursor_change", True)
        self.Widget_Dialog_Properties_start_drag_cursor = settings_dict["Widget_Dialog_Properties"].get("start_drag_cursor", "9")
        self.Widget_Dialog_Properties_end_drag_cursor = settings_dict["Widget_Dialog_Properties"].get("end_drag_cursor", "")
        self.Widget_Dialog_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_Dialog_Properties"].get("cursor_keep_aspect_ratio", True)
        self.Widget_Dialog_Properties_cursor_width = settings_dict["Widget_Dialog_Properties"].get("cursor_width", 20)
        self.Widget_Dialog_Properties_cursor_height = settings_dict["Widget_Dialog_Properties"].get("cursor_height", 20)


    def from_dict(self, properties_dict: dict) -> None:
        if not isinstance(properties_dict, dict):
            raise ValueError(f"The properties_dict must be a dictionary not '{type(properties_dict)}'.")
        
        for section in properties_dict:
            if section.startswith("_GlobalWidgetsProperties"):
                print (f"Warning: section in properties_dict '{section}' is not allowed. SKIPPED!")
                continue

            if section not in self.sections:
                self.__dict__[section] = properties_dict[section]
            else:
                if not isinstance(properties_dict[section], dict):
                    raise ValueError(f"The properties_dict['{section}'] must be a dictionary not '{type(properties_dict[section])}'.")

                for property_name in properties_dict[section]:
                    if property_name.startswith("_GlobalWidgetsProperties"):
                        print (f"Warning: property_name in properties_dict '{property_name}' is not allowed. SKIPPED!")
                        continue

                    self.__dict__[f"{section}_{property_name}"] = properties_dict[section][property_name]

    def to_dict(self) -> dict:
        result = {}
        for property_name, property_value in self.__dict__.items():
            if property_name.startswith("_GlobalWidgetsProperties"):
                continue

            result[property_name] = property_value
        
        return result


class Widget_PushButton_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:

        super().__init__()

        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties({})

        # Pushbutton cursor
        self.allow_cursor_change = kwargs.get("allow_cursor_change") if kwargs.get("allow_cursor_change") is not None else self.global_widgets_properties.Widget_PushButton_Properties_allow_cursor_change
        self.cursor = kwargs.get("cursor") if kwargs.get("cursor") is not None else self.global_widgets_properties.Widget_PushButton_Properties_cursor
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_PushButton_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_PushButton_Properties_cursor_height
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_PushButton_Properties_cursor_keep_aspect_ratio
        # Allow bypass mouse press event
        self.allow_bypass_mouse_press_event = kwargs.get("allow_bypass_mouse_press_event") if kwargs.get("allow_bypass_mouse_press_event") is not None else self.global_widgets_properties.Widget_PushButton_Properties_allow_bypass_mouse_press_event
        # Tap event - animation
        self.tap_event_show_animation_enabled = kwargs.get("tap_event_show_animation_enabled") if kwargs.get("tap_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_show_animation_enabled
        self.tap_event_show_animation_file_path = kwargs.get("tap_event_show_animation_file_path") if kwargs.get("tap_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_show_animation_file_path
        self.tap_event_show_animation_duration_ms = kwargs.get("tap_event_show_animation_duration_ms") if kwargs.get("tap_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_show_animation_duration_ms
        self.tap_event_show_animation_width = kwargs.get("tap_event_show_animation_width") if kwargs.get("tap_event_show_animation_width") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_show_animation_width
        self.tap_event_show_animation_height = kwargs.get("tap_event_show_animation_height") if kwargs.get("tap_event_show_animation_height") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_show_animation_height
        self.tap_event_show_animation_background_color = kwargs.get("tap_event_show_animation_background_color") if kwargs.get("tap_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_show_animation_background_color
        # Tap event - play sound
        self.tap_event_play_sound_enabled = kwargs.get("tap_event_play_sound_enabled") if kwargs.get("tap_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_play_sound_enabled
        self.tap_event_play_sound_file_path = kwargs.get("tap_event_play_sound_file_path") if kwargs.get("tap_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_play_sound_file_path
        # Tap event - change stylesheet
        self.tap_event_change_stylesheet_enabled = kwargs.get("tap_event_change_stylesheet_enabled") if kwargs.get("tap_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_change_stylesheet_enabled
        self.tap_event_change_qss_stylesheet = kwargs.get("tap_event_change_qss_stylesheet") if kwargs.get("tap_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_change_qss_stylesheet
        self.tap_event_change_stylesheet_duration_ms = kwargs.get("tap_event_change_stylesheet_duration_ms") if kwargs.get("tap_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_change_stylesheet_duration_ms
        # Tap event - change size
        self.tap_event_change_size_enabled = kwargs.get("tap_event_change_size_enabled") if kwargs.get("tap_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_change_size_enabled
        self.tap_event_change_size_percent = kwargs.get("tap_event_change_size_percent") if kwargs.get("tap_event_change_size_percent") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_change_size_percent
        self.tap_event_change_size_duration_ms = kwargs.get("tap_event_change_size_duration_ms") if kwargs.get("tap_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_tap_event_change_size_duration_ms
        # Allow bypass enter event
        self.allow_bypass_enter_event = kwargs.get("allow_bypass_enter_event") if kwargs.get("allow_bypass_enter_event") is not None else self.global_widgets_properties.Widget_PushButton_Properties_allow_bypass_enter_event
        # Enter event - animation
        self.enter_event_show_animation_enabled = kwargs.get("enter_event_show_animation_enabled") if kwargs.get("enter_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_show_animation_enabled
        self.enter_event_show_animation_file_path = kwargs.get("enter_event_show_animation_file_path") if kwargs.get("enter_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_show_animation_file_path
        self.enter_event_show_animation_duration_ms = kwargs.get("enter_event_show_animation_duration_ms") if kwargs.get("enter_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_show_animation_duration_ms
        self.enter_event_show_animation_width = kwargs.get("enter_event_show_animation_width") if kwargs.get("enter_event_show_animation_width") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_show_animation_width
        self.enter_event_show_animation_height = kwargs.get("enter_event_show_animation_height") if kwargs.get("enter_event_show_animation_height") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_show_animation_height
        self.enter_event_show_animation_background_color = kwargs.get("enter_event_show_animation_background_color") if kwargs.get("enter_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_show_animation_background_color
        # Enter event - play sound
        self.enter_event_play_sound_enabled = kwargs.get("enter_event_play_sound_enabled") if kwargs.get("enter_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_play_sound_enabled
        self.enter_event_play_sound_file_path = kwargs.get("enter_event_play_sound_file_path") if kwargs.get("enter_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_play_sound_file_path
        # Enter event - change stylesheet
        self.enter_event_change_stylesheet_enabled = kwargs.get("enter_event_change_stylesheet_enabled") if kwargs.get("enter_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_change_stylesheet_enabled
        self.enter_event_change_qss_stylesheet = kwargs.get("enter_event_change_qss_stylesheet") if kwargs.get("enter_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_change_qss_stylesheet
        self.enter_event_change_stylesheet_duration_ms = kwargs.get("enter_event_change_stylesheet_duration_ms") if kwargs.get("enter_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_change_stylesheet_duration_ms
        # Enter event - change size
        self.enter_event_change_size_enabled = kwargs.get("enter_event_change_size_enabled") if kwargs.get("enter_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_change_size_enabled
        self.enter_event_change_size_percent = kwargs.get("enter_event_change_size_percent") if kwargs.get("enter_event_change_size_percent") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_change_size_percent
        self.enter_event_change_size_duration_ms = kwargs.get("enter_event_change_size_duration_ms") if kwargs.get("enter_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_enter_event_change_size_duration_ms
        # Allow bypass leave event
        self.allow_bypass_leave_event = kwargs.get("allow_bypass_leave_event") if kwargs.get("allow_bypass_leave_event") is not None else self.global_widgets_properties.Widget_PushButton_Properties_allow_bypass_leave_event
        # Leave event - animation
        self.leave_event_show_animation_enabled = kwargs.get("leave_event_show_animation_enabled") if kwargs.get("leave_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_show_animation_enabled
        self.leave_event_show_animation_file_path = kwargs.get("leave_event_show_animation_file_path") if kwargs.get("leave_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_show_animation_file_path
        self.leave_event_show_animation_duration_ms = kwargs.get("leave_event_show_animation_duration_ms") if kwargs.get("leave_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_show_animation_duration_ms
        self.leave_event_show_animation_width = kwargs.get("leave_event_show_animation_width") if kwargs.get("leave_event_show_animation_width") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_show_animation_width
        self.leave_event_show_animation_height = kwargs.get("leave_event_show_animation_height") if kwargs.get("leave_event_show_animation_height") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_show_animation_height
        self.leave_event_show_animation_background_color = kwargs.get("leave_event_show_animation_background_color") if kwargs.get("leave_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_show_animation_background_color
        # Leave event - play sound
        self.leave_event_play_sound_enabled = kwargs.get("leave_event_play_sound_enabled") if kwargs.get("leave_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_play_sound_enabled
        self.leave_event_play_sound_file_path = kwargs.get("leave_event_play_sound_file_path") if kwargs.get("leave_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_play_sound_file_path
        # Leave event - change stylesheet
        self.leave_event_change_stylesheet_enabled = kwargs.get("leave_event_change_stylesheet_enabled") if kwargs.get("leave_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_change_stylesheet_enabled
        self.leave_event_change_qss_stylesheet = kwargs.get("leave_event_change_qss_stylesheet") if kwargs.get("leave_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_change_qss_stylesheet
        self.leave_event_change_stylesheet_duration_ms = kwargs.get("leave_event_change_stylesheet_duration_ms") if kwargs.get("leave_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_change_stylesheet_duration_ms
        # Leave event - change size
        self.leave_event_change_size_enabled = kwargs.get("leave_event_change_size_enabled") if kwargs.get("leave_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_change_size_enabled
        self.leave_event_change_size_percent = kwargs.get("leave_event_change_size_percent") if kwargs.get("leave_event_change_size_percent") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_change_size_percent
        self.leave_event_change_size_duration_ms = kwargs.get("leave_event_change_size_duration_ms") if kwargs.get("leave_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_PushButton_Properties_leave_event_change_size_duration_ms


class Widget_PushButton(AbstractWidget):
    def __init__(self, qpushbutton_widget: QPushButton, main_win: QWidget = None, properties_setup: Widget_PushButton_Properties = None) -> None:
        super().__init__()
        
        self.widget = qpushbutton_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_PushButton_Properties()
        if not isinstance(self.properties, Widget_PushButton_Properties):
            warning_message("Widget_PushButton_Properties type not supported: #1", type(self.properties))
            self.properties = Widget_PushButton_Properties()
            warning_message("Used default properties", print_only=True)

        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        self._setup_widget()

    def _setup_widget(self):
        # Tap Event
        if self.properties.allow_bypass_mouse_press_event:
            self.widget.mousePressEvent = lambda e: self.EVENT_mouse_press_event(e, return_event_to_super = True)
        # Enter Event
        if self.properties.allow_bypass_enter_event:
            self.widget.enterEvent = lambda e: self.EVENT_enter_event(e, return_event_to_super=True)
        # Leave Event
        if self.properties.allow_bypass_leave_event:
            self.widget.leaveEvent = lambda e: self.EVENT_leave_event(e, return_event_to_super=True)
        # Cursor
        if self.properties.allow_cursor_change:
            self._set_widget_cursor(self.properties.cursor, self.widget)

    def EVENT_mouse_press_event(self, e: QMouseEvent, return_event_to_super = False):
        if e.button() != Qt.LeftButton:
            if return_event_to_super:
                self.SUPER_CLASS_WIDGET.mousePressEvent(self.widget, e)
            return
        
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.tap_event_play_sound_enabled,
                                    e_file_path=self.properties.tap_event_play_sound_file_path
                                    )
        old_stylesheet = self._tap_event_change_stylesheet(e,
                                                            e_enabled=self.properties.tap_event_change_stylesheet_enabled,
                                                            e_qss=self.properties.tap_event_change_qss_stylesheet
                                                            )
        old_size, old_pos = self._tap_event_change_size(e,
                                                        e_enabled=self.properties.tap_event_change_size_enabled,
                                                        e_percent=self.properties.tap_event_change_size_percent
                                                        )
        start_animation = self._tap_event_show_animation(e,
                                                          e_enabled=self.properties.tap_event_show_animation_enabled,
                                                          e_duration_ms=self.properties.tap_event_show_animation_duration_ms,
                                                          e_width=self.properties.tap_event_show_animation_width,
                                                          e_height=self.properties.tap_event_show_animation_height,
                                                          event_type="tap"
                                                          )
            
        QCoreApplication.processEvents()

        if start_animation:
            QTimer.singleShot(self.properties.tap_event_show_animation_duration_ms, self._tap_event_show_animation_stop)
        elif start_animation is False:
            warning_message("Invalid animation: #1", self.properties.tap_event_show_animation_file_path)
        if old_stylesheet is not None:
            QTimer.singleShot(self.properties.tap_event_change_stylesheet_duration_ms, lambda old_stylesheet=old_stylesheet: self._tap_event_change_stylesheet_stop(old_stylesheet))
        if old_size is not None:
            QTimer.singleShot(self.properties.tap_event_change_size_duration_ms, lambda: self._tap_event_change_size_stop(old_size, old_pos))
        if sound_ok is False:
            warning_message("Invalid sound file: #1", self.properties.tap_event_play_sound_file_path)

        if return_event_to_super:
            self.SUPER_CLASS_WIDGET.mousePressEvent(self.widget, e)

    def EVENT_enter_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.enter_event_play_sound_enabled,
                                    e_file_path=self.properties.enter_event_play_sound_file_path
                                    )
        old_stylesheet = self._tap_event_change_stylesheet(e,
                                                            e_enabled=self.properties.enter_event_change_stylesheet_enabled,
                                                            e_qss=self.properties.enter_event_change_qss_stylesheet
                                                            )
        old_size, old_pos = self._tap_event_change_size(e,
                                                        e_enabled=self.properties.enter_event_change_size_enabled,
                                                        e_percent=self.properties.enter_event_change_size_percent
                                                        )
        start_animation = self._tap_event_show_animation(e,
                                                          e_enabled=self.properties.enter_event_show_animation_enabled,
                                                          e_duration_ms=self.properties.enter_event_show_animation_duration_ms,
                                                          e_width=self.properties.enter_event_show_animation_width,
                                                          e_height=self.properties.enter_event_show_animation_height,
                                                          event_type="enter"
                                                          )
            
        QCoreApplication.processEvents()

        if start_animation:
            QTimer.singleShot(self.properties.enter_event_show_animation_duration_ms, self._tap_event_show_animation_stop)
        elif start_animation is False:
            warning_message("Invalid animation: #1", self.properties.enter_event_show_animation_file_path)
        if old_stylesheet is not None:
            QTimer.singleShot(self.properties.enter_event_change_stylesheet_duration_ms, lambda old_stylesheet=old_stylesheet: self._tap_event_change_stylesheet_stop(old_stylesheet))
        if old_size is not None:
            QTimer.singleShot(self.properties.enter_event_change_size_duration_ms, lambda: self._tap_event_change_size_stop(old_size, old_pos))
        if sound_ok is False:
            warning_message("Invalid sound file: #1", self.properties.enter_event_play_sound_file_path)

        if return_event_to_super:
            self.SUPER_CLASS_WIDGET.enterEvent(self.widget, e)

    def EVENT_leave_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.leave_event_play_sound_enabled,
                                    e_file_path=self.properties.leave_event_play_sound_file_path
                                    )
        old_stylesheet = self._tap_event_change_stylesheet(e,
                                                            e_enabled=self.properties.leave_event_change_stylesheet_enabled,
                                                            e_qss=self.properties.leave_event_change_qss_stylesheet
                                                            )
        old_size, old_pos = self._tap_event_change_size(e,
                                                        e_enabled=self.properties.leave_event_change_size_enabled,
                                                        e_percent=self.properties.leave_event_change_size_percent
                                                        )
        start_animation = self._tap_event_show_animation(e,
                                                          e_enabled=self.properties.leave_event_show_animation_enabled,
                                                          e_duration_ms=self.properties.leave_event_show_animation_duration_ms,
                                                          e_width=self.properties.leave_event_show_animation_width,
                                                          e_height=self.properties.leave_event_show_animation_height,
                                                          event_type="leave"
                                                          )
            
        QCoreApplication.processEvents()

        if start_animation:
            QTimer.singleShot(self.properties.leave_event_show_animation_duration_ms, self._tap_event_show_animation_stop)
        elif start_animation is False:
            warning_message("Invalid animation: #1", self.properties.leave_event_show_animation_file_path)
        if old_stylesheet is not None:
            QTimer.singleShot(self.properties.leave_event_change_stylesheet_duration_ms, lambda old_stylesheet=old_stylesheet: self._tap_event_change_stylesheet_stop(old_stylesheet))
        if old_size is not None:
            QTimer.singleShot(self.properties.leave_event_change_size_duration_ms, lambda: self._tap_event_change_size_stop(old_size, old_pos))
        if sound_ok is False:
            warning_message("Invalid sound file: #1", self.properties.leave_event_play_sound_file_path)

        if return_event_to_super:
            self.SUPER_CLASS_WIDGET.leaveEvent(self.widget, e)


class Widget_Dialog_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:
        
        super().__init__()
        
        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties()

        # Drag Window
        self.window_drag_enabled = kwargs.get("window_drag_enabled") if kwargs.get("window_drag_enabled") is not None else self.global_widgets_properties.Widget_Dialog_Properties_window_drag_enabled
        self.window_drag_widgets = kwargs.get("window_drag_widgets") if kwargs.get("window_drag_widgets") is not None else self.global_widgets_properties.Widget_Dialog_Properties_window_drag_widgets
        self.allow_drag_widgets_cursor_change = kwargs.get("allow_drag_widgets_cursor_change") if kwargs.get("allow_drag_widgets_cursor_change") is not None else self.global_widgets_properties.Widget_Dialog_Properties_allow_drag_widgets_cursor_change
        self.start_drag_cursor = kwargs.get("start_drag_cursor") if kwargs.get("start_drag_cursor") is not None else self.global_widgets_properties.Widget_Dialog_Properties_start_drag_cursor
        self.end_drag_cursor = kwargs.get("end_drag_cursor") if kwargs.get("end_drag_cursor") is not None else self.global_widgets_properties.Widget_Dialog_Properties_end_drag_cursor
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_Dialog_Properties_cursor_keep_aspect_ratio
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_Dialog_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_Dialog_Properties_cursor_height


class Widget_Dialog(AbstractWidget):
    def __init__(self, qdialog_widget: QDialog, main_win: QWidget = None, properties_setup: Widget_Dialog_Properties = None) -> None:

        super().__init__()

        self.widget = qdialog_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_Dialog_Properties()
        if not isinstance(self.properties, Widget_Dialog_Properties):
            warning_message("Widget_Dialog_Properties not supported: #1", type(self.properties))
            self.properties = Widget_Dialog_Properties()
            warning_message("Used default Widget_Dialog_Properties", print_only=True)

        self.__drag_mode = None

    def activate(self):
        self._setup_widget()

    def _setup_widget(self):
        if self.properties.window_drag_enabled:
            self.enable_window_drag()
            self._set_drag_widgets_cursor()

    def add_window_drag_widgets(self, widgets: list[QWidget]):
        if widgets is None:
            for widget in self.widget.children():
                if isinstance(widget, QLabel) and widget.objectName() == "lbl_title":
                    self.properties.window_drag_widgets.append(widget)
                    break
            else:
                warning_message("Can't find DRAG WINDOW widget: #1", "lbl_title")
        elif isinstance(widgets, list) or isinstance(widgets, tuple):
            self.properties.window_drag_widgets.extend(widgets)
        elif isinstance(widgets, QWidget):
            self.properties.window_drag_widgets.append(widgets)
        else:
            warning_message("Invalid DRAG WINDOW widget type: #1", type(widgets))

    def enable_window_drag(self):
        for widget in self.properties.window_drag_widgets:
            widget: QWidget
            # widget.setMouseTracking(True)
            widget.mousePressEvent = lambda e: self.EVENT_drag_widget_mouse_press_event(e)
            widget.mouseMoveEvent = lambda e: self.EVENT_drag_widget_mouse_move_event(e)
            widget.mouseReleaseEvent = lambda e: self.EVENT_drag_widget_mouse_release_event(e)
    
    def disable_window_drag(self):
        for widget in self.properties.window_drag_widgets:
            # widget.setMouseTracking(False)
            widget.mousePressEvent = None
            widget.mouseMoveEvent = None
            widget.mouseReleaseEvent = None

    def EVENT_drag_widget_mouse_press_event(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.__drag_mode = {
                "win_x": self.widget.pos().x(),
                "win_y": self.widget.pos().y(),
                "mouse_x": QCursor().pos().x(),
                "mouse_y": QCursor().pos().y()
                }
            self._set_drag_widgets_cursor()
    
    def EVENT_drag_widget_mouse_move_event(self, e: QMouseEvent):
        if self.__drag_mode:
            x = QCursor().pos().x() - self.__drag_mode["mouse_x"]
            y = QCursor().pos().y() - self.__drag_mode["mouse_y"]
            self.widget.move(self.__drag_mode["win_x"] + x, self.__drag_mode["win_y"] + y)

    def EVENT_drag_widget_mouse_release_event(self, e: QMouseEvent):
        self.__drag_mode = None
        self._set_drag_widgets_cursor()

    def _set_drag_widgets_cursor(self):
        if not self.properties.window_drag_enabled or not self.properties.allow_drag_widgets_cursor_change:
            return

        for widget in self.properties.window_drag_widgets:
            if widget == self.widget:
                continue
            if self.__drag_mode:
                self._set_widget_cursor(self.properties.start_drag_cursor, widget)
            else:
                self._set_widget_cursor(self.properties.end_drag_cursor, widget)


class WidgetHandler:
    def __init__(self, main_win: QWidget, global_widgets_properties: GlobalWidgetsProperties = None) -> None:

        self.main_win = main_win if main_win is not None else self.widget
        
        if global_widgets_properties is not None:
            if isinstance(global_widgets_properties, GlobalWidgetsProperties):
                self.global_widgets_properties = global_widgets_properties
            elif isinstance(global_widgets_properties, dict):
                self.global_widgets_properties = GlobalWidgetsProperties()
                self.global_widgets_properties.from_dict(global_widgets_properties)
            else:
                warning_message("GlobalWidgetsProperties type not supported: #1", type(global_widgets_properties))
                warning_message("Using default GlobalWidgetsProperties", print_only=True)

        if self.global_widgets_properties is None:                
            self.global_widgets_properties = GlobalWidgetsProperties()

        self.__children = []

    def activate(self):
        for child in self.__children:
            child.activate()

    def add_child(self, widget: QWidget, widget_properties_dict: dict = None, force_widget_type: str = None) -> object:
        widget_obj = None

        if isinstance(widget, QPushButton) or (force_widget_type is not None and force_widget_type.lower() == "qpushbutton"):
            widget_default_properties_dict = Widget_PushButton_Properties(self.global_widgets_properties)
            widget_obj = Widget_PushButton(widget, self.main_win, widget_default_properties_dict)
            widget_obj.update_from_dict(widget_properties_dict)
        if isinstance(widget, QDialog) or (force_widget_type is not None and force_widget_type.lower() == "qdialog"):
            widget_default_properties_dict = Widget_Dialog_Properties(self.global_widgets_properties)
            widget_obj = Widget_Dialog(widget, self.main_win, widget_default_properties_dict)
            widget_obj.update_from_dict(widget_properties_dict)
        
        if widget_obj is None:
            warning_message("Widget type not supported: #1", type(widget))
            return None

        if widget not in [x.widget for x in self.__children]:
            self.__children.append(widget_obj)
            return widget_obj
        else:
            warning_message("Widget already added: #1", str(widget))
            return False

    def add_QDialog(self, widget: QDialog, widget_properties_dict: dict = None) -> Widget_Dialog:
        return self.add_child(widget, widget_properties_dict, force_widget_type="qdialog")
    
    def add_QPushButton(self, widget: QPushButton, widget_properties_dict: dict = None) -> Widget_PushButton:
        return self.add_child(widget, widget_properties_dict, force_widget_type="qpushbutton")

    def add_all_QPushButtons(self, widget_properties_dict: dict = None, deep_search: bool = True, starting_widget: QWidget = None) -> int:
        if starting_widget is None:
            starting_widget = self.main_win

        result = self._add_all_QPushButtons(start_widget=starting_widget, widget_properties_dict=widget_properties_dict, deep_search=deep_search)

        return result

    def _add_all_QPushButtons(self, start_widget: QWidget, widget_properties_dict: dict = None, deep_search: bool = True) -> int:
        count  = 0
        for child in start_widget.children():
            if child.children() and deep_search:
                count += self._add_all_QPushButtons(child, widget_properties_dict, deep_search)

            if isinstance(child, QPushButton):
                if self.add_child(child, widget_properties_dict):
                    count += 1
            
        return count

    def add_all_children(self, widget_properties_dict: dict = None, deep_search: bool = True, starting_widget: QWidget = None) -> int:
        if starting_widget is None:
            starting_widget = self.main_win
        count  = 0
        count += self.add_all_QPushButtons(widget_properties_dict, deep_search=deep_search, starting_widget=starting_widget)

        return count

    def find_child(self, widget: QWidget):
        for child in self.__children:
            if child.widget == widget:
                return child
        
        return None

    def remove_child(self, widget: QWidget) -> bool:
        for child in self.__children:
            if child.widget == widget:
                self.__children.remove(child)
                return True
        
        return False

    def update_from_dict(self, properties_dict: dict, only_dedicated: bool = True) -> None:
        for child in self.__children:
            child.update_from_dict(properties_dict, only_dedicated)
        
    def close_me(self):
        for child in self.__children:
            child.close_me()
        



import unittest

class TestYourClass(unittest.TestCase):
    def test_from_dict(self):
        # Create an instance of your class
        your_instance = Widget_PushButton_Properties()

        # Assertion 1
        properties_dict = {
            "tap_event_show_animation_file_path": "value1"
        }

        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "value1")

        # Assertion 2
        properties_dict = {
            "tap_event_show_animation_file_path": "value111"
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "value111")

        # Assertion 3
        properties_dict = {
            "_Widget_PushButton_Properties_tap_event_show_animation_file_path": "ve111"
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "value111")

        # Assertion 4
        properties_dict = {
            "Widget_PushButton_Properties_tap_event_show_animation_file_path": "111"
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "111")

        # Assertion 5
        properties_dict = {
            "Widget_PushButton_Properties": {
                "tap_event_show_animation_file_path": "222"
            }
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "222")

        # Assertion 6
        properties_dict = {
            "Widget_PushButton_Properties": {
                "Widget_PushButton_Properties_tap_event_show_animation_file_path": "33"
            }
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "33")

        # Assertion 7
        properties_dict = {
            "Widget_QLabel_Properties": {
                "Widget_PushButton_Properties_tap_event_show_animation_file_path": "44"
            }
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "33")

        # Assertion 8
        properties_dict = {
            "Widget_QLabel_Properties": {
                "Widget_QLabel_Properties_tap_event_show_animation_file_path": "44"
            }
        }
        your_instance.from_dict(properties_dict)
        self.assertEqual(your_instance.tap_event_show_animation_file_path, "33")
        self.assertEqual(your_instance.name(), "Widget_PushButton_Properties", "Class Name Error")
        
        properties_dict = "aaa"
        def func_that_raises_exception():
            your_instance.from_dict(properties_dict)
        self.assertRaises(ValueError, func_that_raises_exception)


if __name__ == '__main__':
    # unittest.main()
    app = QApplication([])
    a = QFrame()
    aa = str(type(a))
    aa = aa[aa.rfind(".") + 1:aa.rfind("'")]
    print(aa, type(aa))

