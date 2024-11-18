from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QWidget, QSizePolicy, QListWidget, QDialog,
                             QLabel, QLineEdit, QCalendarWidget, QComboBox, QProgressBar, QCheckBox, QTreeWidget,
                             QRadioButton, QGroupBox, QSpinBox, QTableWidget, QTabWidget, QDockWidget,
                             QDialogButtonBox, QToolBox, QFontComboBox, QPlainTextEdit, QTimeEdit, QDateEdit,
                             QDateTimeEdit, QDial, QKeySequenceEdit, QDoubleSpinBox, QTextBrowser, QLCDNumber,
                             QToolButton, QDesktopWidget, QMainWindow)
from PyQt5.QtGui import QMovie, QMouseEvent, QCursor, QPixmap, QKeyEvent, QTextCursor
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QPoint, QEvent

import inspect
import os

from stylesheet_cls import StyleSheet
from timer_cls import TimerHandler
from timer_cls import SingleShotTimer
import UTILS


class ReturnEvent:
    SUPER_CLASS_WIDGET = None
    
    @classmethod
    def keyPressEvent(cls, widget, event):
        if cls.SUPER_CLASS_WIDGET:
            try:
                if isinstance(widget, QWidget):
                    cls.SUPER_CLASS_WIDGET.keyPressEvent(widget, event)
                else:
                    UTILS.TerminalUtility.WarningMessage("Widget not defined. KeyPressEvent not called")
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage(f"Exception in keyPressEvent\n#1", [str(e)])
        else:
            UTILS.TerminalUtility.WarningMessage("SUPER_CLASS_WIDGET not defined. KeyPressEvent not called")
    
    @classmethod
    def mousePressEvent(cls, widget, event):
        if cls.SUPER_CLASS_WIDGET:
            try:
                if isinstance(widget, QWidget):
                    cls.SUPER_CLASS_WIDGET.mousePressEvent(widget, event)
                else:
                    UTILS.TerminalUtility.WarningMessage("Widget not defined. MousePressEvent not called")
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage(f"Exception in mousePressEvent\n#1", [str(e)])
        else:
            UTILS.TerminalUtility.WarningMessage("SUPER_CLASS_WIDGET not defined. MousePressEvent not called")
    
    @classmethod
    def enterEvent(cls, widget, event):
        if cls.SUPER_CLASS_WIDGET:
            try:
                if isinstance(widget, QWidget):
                    cls.SUPER_CLASS_WIDGET.enterEvent(widget, event)
                else:
                    UTILS.TerminalUtility.WarningMessage("Widget not defined. EnterEvent not called")
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage(f"Exception in enterEvent\n#1", [str(e)])
        else:
            UTILS.TerminalUtility.WarningMessage("SUPER_CLASS_WIDGET not defined. EnterEvent not called")

    @classmethod
    def leaveEvent(cls, widget, event):
        if cls.SUPER_CLASS_WIDGET:
            try:
                if isinstance(widget, QWidget):
                    cls.SUPER_CLASS_WIDGET.leaveEvent(widget, event)
                else:
                    UTILS.TerminalUtility.WarningMessage("Widget not defined. LeaveEvent not called")
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage(f"Exception in leaveEvent\n#1", [str(e)])
        else:
            UTILS.TerminalUtility.WarningMessage("SUPER_CLASS_WIDGET not defined. LeaveEvent not called")


class AbstractProperties:
    def __init__(self) -> None:

        self.sections = [
            "Widget_PushButton_Properties",
            "Widget_Dialog_Properties",
            "Widget_Frame_Properties",
            "Widget_ActionFrame_Properties",
            "Widget_TextBox_Properties",
            "Widget_Selection_Properties",
            "Widget_ItemBased_Properties"
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
            UTILS.TerminalUtility.WarningMessage("Variable #1 must be a dictionary.\ntype(properties_dict) = #2\nproperties_dict = #3", ["properties_dict", type(properties_dict), properties_dict], exception_raised=True)
            raise ValueError(f"The properties_dict must be a dictionary not '{type(properties_dict)}'.")
        
        for section in properties_dict:
            if section.startswith(f"_{self.name()}"):
                UTILS.TerminalUtility.WarningMessage("Property name in properties_dict #1 is not allowed. SKIPPED!", section)
                continue

            if section not in self.sections:
                dict_property_name = section
                if dict_property_name.startswith(f"{self.name()}_"):
                    dict_property_name = dict_property_name[len(f"{self.name()}_"):]

                if not only_dedicated or (only_dedicated and dict_property_name in self.__dict__):
                    self.__dict__[dict_property_name] = properties_dict[section]

            else:
                if not isinstance(properties_dict[section], dict):
                    UTILS.TerminalUtility.WarningMessage("The properties_dict[#1] must be a dictionary.\ntype(properties_dict[#2]) = #3\nproperties_dict[#4] = #5",[section, section, type(properties_dict[section]), section, properties_dict[section]], exception_raised=True)
                    raise ValueError(f"The properties_dict['{section}'] must be a dictionary not '{type(properties_dict[section])}'.")
                
                if section != self.name():
                    continue

                for property_name in properties_dict[section]:
                    if property_name.startswith(f"_{self.name()}"):
                        UTILS.TerminalUtility.WarningMessage("Property name in properties_dict #1 is not allowed. SKIPPED!", property_name)
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
    GUARD_DURATION = 200

    def __init__(self, timer_handler: TimerHandler = None) -> None:
        self.widget: QWidget = None
        self.main_win: QWidget = None
        self.properties = None

        self.SUPER_CLASS_WIDGET = None

        if timer_handler:
            self._timer_handler = timer_handler
            self.has_own_timer = False
        else:
            self._timer_handler: TimerHandler = TimerHandler(parent=self.widget, interval=25)
            self.has_own_timer = True
        
        self._stylesheet_timer = SingleShotTimer(parent=self._timer_handler
                                                , name="stylesheet"
                                                , duration=1
                                                , function_on_finished=self._tap_event_change_stylesheet_stop
                                                ,data={"completed": True})
        self._size_timer = SingleShotTimer(parent=self._timer_handler,
                                            name="size",
                                            duration=1,
                                            function_on_finished=self._tap_event_change_size_stop
                                            ,data={"completed": True})
        self._animation_timer = SingleShotTimer(parent=self._timer_handler,
                                                name="animation",
                                                duration=1,
                                                function_on_finished=self._tap_event_show_animation_stop
                                                ,data={"completed": True})
        self._timer_handler.add_timer(self._stylesheet_timer)
        self._timer_handler.add_timer(self._size_timer)
        self._timer_handler.add_timer(self._animation_timer)

        self.is_active = False

        self._tap_label: QLabel = None
        self._tap_sound: UTILS.SoundUtility = None

        self.__drag_mode = None
        self.__mask_label = None

    def _get_qwidget_class(self) -> QWidget:
        # widget_type = self._get_widget_type()
        result = None
        if isinstance(self.widget, QPushButton):
            result = QPushButton
        elif isinstance(self.widget, QDialog):
            result = QDialog
        elif isinstance(self.widget, QDesktopWidget):
            result = QDesktopWidget
        elif isinstance(self.widget, QMainWindow):
            result = QMainWindow
        elif isinstance(self.widget, QLabel):
            result = QLabel
        elif isinstance(self.widget, QCheckBox):
            result = QCheckBox
        elif isinstance(self.widget, QComboBox):
            result = QComboBox
        elif isinstance(self.widget, QSpinBox):
            result = QSpinBox
        elif isinstance(self.widget, QTextEdit):
            result = QTextEdit
        elif isinstance(self.widget, QLineEdit):
            result = QLineEdit
        elif isinstance(self.widget, QListWidget):
            result = QListWidget
        elif isinstance(self.widget, QTableWidget):
            result = QTableWidget
        elif isinstance(self.widget, QTreeWidget):
            result = QTreeWidget
        elif isinstance(self.widget, QCalendarWidget):
            result = QCalendarWidget
        elif isinstance(self.widget, QProgressBar):
            result = QProgressBar
        elif isinstance(self.widget, QRadioButton):
            result = QRadioButton
        elif isinstance(self.widget, QTabWidget):
            result = QTabWidget
        elif isinstance(self.widget, QDockWidget):
            result = QDockWidget
        elif isinstance(self.widget, QDialogButtonBox):
            result = QDialogButtonBox
        elif isinstance(self.widget, QGroupBox):
            result = QGroupBox
        elif isinstance(self.widget, QScrollArea):
            result = QScrollArea
        elif isinstance(self.widget, QToolBox):
            result = QToolBox
        elif isinstance(self.widget, QFontComboBox):
            result = QFontComboBox
        elif isinstance(self.widget, QPlainTextEdit):
            result = QPlainTextEdit
        elif isinstance(self.widget, QTimeEdit):
            result = QTimeEdit
        elif isinstance(self.widget, QDateTimeEdit):
            result = QDateTimeEdit
        elif isinstance(self.widget, QDateEdit):
            result = QDateEdit
        elif isinstance(self.widget, QDoubleSpinBox):
            result = QDoubleSpinBox
        elif isinstance(self.widget, QDial):
            result = QDial
        elif isinstance(self.widget, QKeySequenceEdit):
            result = QKeySequenceEdit
        elif isinstance(self.widget, QTextBrowser):
            result = QTextBrowser
        elif isinstance(self.widget, QLCDNumber):
            result = QLCDNumber
        elif isinstance(self.widget, QToolButton):
            result = QToolButton
        elif isinstance(self.widget, QFrame):
            result = QFrame

        if result is None:
            result = QWidget
            UTILS.TerminalUtility.WarningMessage("Widget type not supported: #1", str(type(self.widget)))
        
        return result

    def _get_widget_type(self) -> str:
        supported_classes = [
            "QPushButton",
            "QMainWindow",
            "QLabel",
            "QFrame",
            "QCheckBox",
            "QComboBox",
            "QSpinBox",
            "QTextEdit",
            "QLineEdit",
            "QListWidget",
            "QTableWidget",
            "QTreeWidget",
            "QCalendarWidget",
            "QProgressBar",
            "QRadioButton",
            "QTabWidget",
            "QDockWidget",
            "QDialogButtonBox",
            "QGroupBox",
            "QScrollArea",
            "QToolBox",
            "QFontComboBox",
            "QPlainTextEdit",
            "QTimeEdit",
            "QDateTimeEdit",
            "QDateEdit",
            "QDoubleSpinBox",
            "QDial",
            "QKeySequenceEdit",
            "QTextBrowser",
            "QLCDNumber",
            "QToolButton",
            "QDialog"
        ]

        found_widget_type = None
        for class_type in inspect.getmro(type(self.widget)):
            widget_type = str(class_type)
            widget_type = widget_type[widget_type.rfind(".") + 1:widget_type.rfind("'")]
            if widget_type in supported_classes:
                found_widget_type = widget_type
                break

        if found_widget_type is None:
            UTILS.TerminalUtility.WarningMessage("Widget type not supported: #1", str(type(self.widget)))
            found_widget_type = "QWidget"

        return widget_type

    def _tap_event_change_size(self, e: QMouseEvent, e_enabled: bool, e_percent: int) -> bool:
        if not e_enabled or self._size_timer is None:
            return False
        
        if self._size_timer.data["completed"]:
            self._size_timer.data["completed"] = False
            self._size_timer.data["old_size"] = self.widget.size()
            self._size_timer.data["old_pos"] = self.widget.pos()
            self._size_timer.set_duration(self.GUARD_DURATION)
            self._size_timer.start()

        old_size = self._size_timer.data["old_size"]
        old_pos = self._size_timer.data["old_pos"]

        scale = (100 + e_percent) / 100

        if self.widget.sizePolicy().horizontalPolicy() == QSizePolicy.Fixed:
            self.widget.setFixedWidth(int(old_size.width() * scale))
        else:
            self.widget.resize(int(old_size.width() * scale), old_size.height())
        
        if self.widget.sizePolicy().verticalPolicy() == QSizePolicy.Fixed:
            self.widget.setFixedHeight(int(old_size.height() * scale))
        else:
            self.widget.resize(old_size.width(), int(old_size.height() * scale))

        x = old_pos.x() + int((old_size.width() - self.widget.width()) / 2)
        y = old_pos.y() + int((old_size.height() - self.widget.height()) / 2)

        self.widget.move(x, y)

        self.widget.raise_()

        return True
    
    def _tap_event_change_size_stop(self, timer: SingleShotTimer):
        old_size: QSize = timer.data["old_size"]
        old_pos: QPoint = timer.data["old_pos"]

        try:
            if isinstance(self.widget, QWidget):
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
            UTILS.TerminalUtility.WarningMessage(f"Exception in _tap_event_change_size_stop\n#1", [str(e)], print_only=True)
        
        timer.data["completed"] = True

    def _tap_event_change_stylesheet(self, e: QMouseEvent, e_enabled: bool, e_qss: str) -> bool:
        if not e_enabled or self._stylesheet_timer is None:
            return False

        if self._stylesheet_timer.data["completed"]:
            self._stylesheet_timer.data["completed"] = False
            self._stylesheet_timer.data["old_stylesheet"] = self.widget.styleSheet()
            self._stylesheet_timer.set_duration(self.GUARD_DURATION)
            self._stylesheet_timer.start()

        old_stylesheet = self._stylesheet_timer.data["old_stylesheet"]

        widget_type = self._get_widget_type()
        
        old_style = StyleSheet(widget_name="QPushButton")
        old_style.stylesheet = old_stylesheet

        # Combine old and new stylesheet
        new_stylesheet = e_qss

        new_style = StyleSheet(widget_name="QPushButton")
        new_style.stylesheet = new_stylesheet
        new_style.widget_name = widget_type

        new_style.merge_stylesheet(stylesheet=old_style)

        new_stylesheet = new_style.stylesheet
        # print (f"OLD STYLESHEET:\n{old_stylesheet}\n\nNEW STYLESHEET:\n{new_stylesheet}\n\n")

        # Merge new and old stylesheet
        self.widget.setStyleSheet(new_stylesheet)

        return True

    def _tap_event_change_stylesheet_stop(self, timer: SingleShotTimer):
        if timer.data.get("old_stylesheet") is None:
            UTILS.TerminalUtility.WarningMessage("old_stylesheet not found in _tap_event_change_stylesheet_stop\nTimer name: #1\nTimer data: #2", [str(timer.name), str(timer.data)], print_only=True)
            return
        old_stylesheet = timer.data["old_stylesheet"]
        
        try:
            if isinstance(self.widget, QWidget):
                self.widget.setStyleSheet(old_stylesheet)
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("Exception in _tap_event_change_stylesheet_stop\n#1\nUnable to set stylesheet for widget.", [e])
        
        timer.data["completed"] = True

    def _tap_event_show_animation(self, e: QMouseEvent, e_enabled: bool, e_duration_ms: int, e_width: int, e_height: int, event_type: str) -> bool:
        if isinstance(e, QMouseEvent):
            e_pos = e.globalPos()
        else:
            e_pos = QCursor().pos()

        if not e_enabled or self._animation_timer is None:
            return None

        if self._animation_timer.data["completed"]:
            self._animation_timer.data["completed"] = False
            self._animation_timer.set_duration(self.GUARD_DURATION)
            self._animation_timer.start()
        else:
            return True

        if self._tap_label is None:
            self._tap_label = self._create_tap_label(self.main_win, event_type=event_type)
        
        self._tap_label.move(self.main_win.mapFromGlobal(e_pos).x() - e_width // 2, self.main_win.mapFromGlobal(e_pos).y() - e_height // 2)
        self._tap_label.show()
        self._tap_label.raise_()
        # try:
        #     self._tap_label.movie().jumpToFrame(0)
        #     frame_duration = self._tap_label.movie().nextFrameDelay()
        #     frame_count = self._tap_label.movie().frameCount()
        #     total_duration = frame_duration * frame_count
        #     desired_duration = int(e_duration_ms * 0.80)
        #     speed = total_duration / desired_duration
        #     self._tap_label.movie().setSpeed(int(speed*100))
        # except:
        #     UTILS.TerminalUtility.WarningMessage("Error setting the speed of the animation. (#1) type.", event_type, print_only=True)

        self._tap_label.movie().start()

        if self._tap_label.movie().isValid():
            return True
        
        return False

    def _tap_event_show_animation_stop(self, timer: SingleShotTimer):
        try:
            if self._tap_label:
                self._tap_label.movie().stop()
                self._tap_label.hide()
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage(f"Exception in _tap_event_show_animation_stop\n#1", [str(e)], print_only=True)
        
        timer.data["completed"] = True

    def _tap_event_play_sound(self, e: QMouseEvent, e_enabled: bool, e_file_path: str) -> bool:
        if not e_enabled:
            return None
        
        try:
            if not self._tap_sound:
                try:
                    sound_volume = self.main_win.getv("volume_value")
                    sound_muted = self.main_win.getv("volume_muted")
                except AttributeError:
                    sound_volume = 100
                    sound_muted = False
                    UTILS.TerminalUtility.WarningMessage("Error in _tap_event_play_sound. #1\n#2\nmain_win = #3\nVolume is set to #4, muted is set to #5", [str(e), "AttributeError: 'main_win' object has no attribute 'getv'", str(self.main_win), "100", "False"])
                
                self._tap_sound = UTILS.SoundUtility(e_file_path, volume=sound_volume, muted=sound_muted)
            if not self._tap_sound.isFinished():
                self._tap_sound.stop()

            self._tap_sound.play(e_file_path)
            
            return True
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("Exception in _tap_event_play_sound\n#1", [str(e)], print_only=True)
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
            UTILS.TerminalUtility.WarningMessage(f"Invalid event_type: #1\nMust be one of: #2, #3, #4", [event_type, "tap", "enter", "leave"], print_only=True, exception_raised=True)
            raise ValueError(f"Invalid event_type: {event_type}")

        lbl = QLabel(parent_widget)
        lbl.setStyleSheet(f"QLabel {{ background-color: {bg_color}; border: 0px;}}")
        lbl.setFixedSize(w, h)
        lbl.setScaledContents(True)
        tap_movie = QMovie(file)
        tap_movie.setScaledSize(QSize(w, h))
        lbl.setMovie(tap_movie)
        # tap_movie.frameChanged.connect(self._tap_movie_frame_changed)
        lbl.hide()

        return lbl

    def _tap_movie_frame_changed(self, frame):
        try:
            if self._tap_label:
                if frame == self._tap_label.movie().frameCount() - 1:
                    self._tap_label.movie().setPaused(True)
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage(f"Exception in _tap_movie_frame_changed\n#1", [str(e)], print_only=True)

    def close_me(self):
        if self._tap_label is not None:
            self._tap_label.movie().stop()
            # try:
            #     self._tap_label.movie().frameChanged.disconnect(self._tap_movie_frame_changed)
            # except:
            #     pass
            self._tap_label.hide()
            self._tap_label.deleteLater()
            self._tap_label = None

        if self._tap_sound is not None:
            self._tap_sound.stop()
            self._tap_sound.deleteLater()
        
        if self.__mask_label is not None:
            self.__mask_label.mousePressEvent = None
            self.__mask_label.hide()
            self.__mask_label.deleteLater()

        if self._size_timer:
            if self._size_timer.is_active() and self._size_timer.function_on_finished:
                self._size_timer.stop()
                self._size_timer.function_on_finished(self._size_timer)
            self._size_timer.stop()
        if self._animation_timer:
            if self._animation_timer.is_active() and self._animation_timer.function_on_finished:
                self._animation_timer.stop()
                self._animation_timer.function_on_finished(self._animation_timer)
            self._animation_timer.stop()
        if self._stylesheet_timer:
            if self._stylesheet_timer.is_active() and self._stylesheet_timer.function_on_finished:
                self._stylesheet_timer.stop()
                self._stylesheet_timer.function_on_finished(self._stylesheet_timer)
            self._stylesheet_timer.stop()
        if self._timer_handler:
            if self.has_own_timer:
                self._timer_handler.stop_all_timers()
                self._timer_handler.remove_all_timers()
                self._timer_handler.stop()
                self._timer_handler.deleteLater()
            else:
                if self._size_timer:
                    self._timer_handler.remove_timer(self._size_timer)
                if self._animation_timer:
                    self._timer_handler.remove_timer(self._animation_timer)
                if self._stylesheet_timer:
                    self._timer_handler.remove_timer(self._stylesheet_timer)
        
        self._size_timer = None
        self._animation_timer = None
        self._stylesheet_timer = None
        self._timer_handler = None

        property_dict = self.properties.to_dict()
        if property_dict.get("allow_bypass_mouse_press_event"):
            self.widget.mousePressEvent = None
        if property_dict.get("allow_bypass_enter_event"):
            self.widget.enterEvent = None
        if property_dict.get("allow_bypass_leave_event"):
            self.widget.leaveEvent = None
        if property_dict.get("window_drag_enabled"):
            self.disable_window_drag(property_dict.get("window_drag_widgets", []))
            self.widget.mousePressEvent = None
            self.widget.mouseMoveEvent = None
            self.widget.mouseReleaseEvent = None
        if property_dict.get("allow_bypass_key_press_event"):
            self.widget.keyPressEvent = None
        
    def activate(self):
        UTILS.TerminalUtility.WarningMessage("AbstractWidget.activate() not implemented (#1)", self.__class__.__name__, warning_type=UserWarning)

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
                    UTILS.TerminalUtility.WarningMessage("Unable to set cursor: #1", cursor)

    def add_window_drag_widgets(self, widgets: list[QWidget]):
        if widgets is None:
            for widget in self.widget.children():
                if isinstance(widget, QLabel) and widget.objectName() == "lbl_title":
                    self.properties.window_drag_widgets.append(widget)
                    break
            else:
                UTILS.TerminalUtility.WarningMessage("Can't find DRAG WINDOW widget: #1", "lbl_title")
        elif isinstance(widgets, list) or isinstance(widgets, tuple):
            self.properties.window_drag_widgets.extend(widgets)
        elif isinstance(widgets, QWidget):
            self.properties.window_drag_widgets.append(widgets)
        else:
            UTILS.TerminalUtility.WarningMessage("Invalid DRAG WINDOW widget type: #1", type(widgets))

    def enable_window_drag(self, drag_widgets: list, data: dict = None, forbidden_widgets: list = None):
        for widget in drag_widgets:
            if forbidden_widgets and widget in forbidden_widgets:
                continue

            widget: QWidget
            # widget.setMouseTracking(True)
            widget.mousePressEvent = lambda e, data=data: self.EVENT_drag_widget_mouse_press_event(e, data)
            widget.mouseMoveEvent = lambda e, data=data: self.EVENT_drag_widget_mouse_move_event(e, data)
            widget.mouseReleaseEvent = lambda e, data=data: self.EVENT_drag_widget_mouse_release_event(e, data)
    
    def disable_window_drag(self, drag_widgets: list):
        for widget in drag_widgets:
            # widget.setMouseTracking(False)
            widget.mousePressEvent = None
            widget.mouseMoveEvent = None
            widget.mouseReleaseEvent = None

    def EVENT_drag_widget_mouse_press_event(self, e: QMouseEvent, data: dict = None):
        if e.button() == Qt.LeftButton:
            self.widget.raise_()
            property_dict = self.properties.to_dict()

            self.__drag_mode = {
                "win_x": self.widget.pos().x(),
                "win_y": self.widget.pos().y(),
                "mouse_x": QCursor().pos().x(),
                "mouse_y": QCursor().pos().y(),
                "stylesheet": self.widget.styleSheet() if self.widget.styleSheet() else ""
                }
            if data is not None and data.get("boundaries"):
                if data["boundaries"] == "main_win":
                    max_x = self.main_win.width() - self.widget.width()
                    if max_x < 0:
                        max_x = 0
                    max_y = self.main_win.height() - self.widget.height()
                    if max_y < 0:
                        max_y = 0
                    self.__drag_mode["max_x"] = max_x
                    self.__drag_mode["max_y"] = max_y
                    self.__drag_mode["min_x"] = 0
                    self.__drag_mode["min_y"] = 0
    
            if property_dict.get("dragged_window_change_stylesheet_enabled"):
                self._set_stylesheet_on_dragged_widget()
            
            if property_dict.get("dragged_window_mask_label_enabled"):
                self._create_mask_label(self.widget)
            
            self._set_drag_widgets_cursor()

    def EVENT_drag_widget_mouse_move_event(self, e: QMouseEvent, data: dict = None):
        if self.__drag_mode:
            x = QCursor().pos().x() - self.__drag_mode["mouse_x"]
            y = QCursor().pos().y() - self.__drag_mode["mouse_y"]

            x += self.__drag_mode["win_x"]
            y += self.__drag_mode["win_y"]

            if self.__drag_mode.get("max_x") is not None and x > self.__drag_mode["max_x"]:
                x = self.__drag_mode["max_x"]
            if self.__drag_mode.get("max_y") is not None and y > self.__drag_mode["max_y"]:
                y = self.__drag_mode["max_y"]
            if self.__drag_mode.get("min_x") is not None and x < self.__drag_mode["min_x"]:
                x = self.__drag_mode["min_x"]
            if self.__drag_mode.get("min_y") is not None and y < self.__drag_mode["min_y"]:
                y = self.__drag_mode["min_y"]
            
            self.widget.move(x, y)

    def EVENT_drag_widget_mouse_release_event(self, e: QMouseEvent, data: dict = None):
        if self.__drag_mode:
            self.widget.setStyleSheet(self.__drag_mode["stylesheet"])
        self.__drag_mode = None
        self._remove_mask_label()
        self._set_drag_widgets_cursor()

    def _set_stylesheet_on_dragged_widget(self):
        widget_type = self._get_widget_type()
        
        old_stylesheet = self.widget.styleSheet()
        old_style = StyleSheet(widget_name="QFrame")
        old_style.stylesheet = old_stylesheet

        # Combine old and new stylesheet
        new_stylesheet = self.properties.dragged_window_stylesheet

        new_style = StyleSheet(widget_name="QFrame")
        new_style.stylesheet = new_stylesheet
        
        new_style.font_name = None
        new_style.font_size = None
        new_style.font_bold = None
        new_style.font_italic = None
        new_style.font_underline = None
        new_style.font_strikeout = None
        
        new_style.widget_name = widget_type

        new_style.merge_stylesheet(stylesheet=old_style)

        new_stylesheet = new_style.stylesheet

        # Merge new and old stylesheet
        self.widget.setStyleSheet(new_stylesheet)

    def _create_mask_label(self, widget):
        self.__mask_label = QLabel(widget)
        self.__mask_label.move(0, 0)
        self.__mask_label.resize(widget.width(), widget.height())
        self.__mask_label.setStyleSheet(self.properties.dragged_window_mask_label_stylesheet)
        self.__mask_label.setScaledContents(True)
        if self.properties.dragged_window_mask_label_animation_path:
            movie = QMovie(self.properties.dragged_window_mask_label_animation_path)
            self.__mask_label.setMovie(movie)
            movie.start()
        else:
            if self.properties.dragged_window_mask_label_image_path:
                self.__mask_label.setPixmap(QPixmap(self.properties.dragged_window_mask_label_image_path))
    
        self.__mask_label.mousePressEvent = self._remove_mask_label
        self.__mask_label.show()

    def _remove_mask_label(self, e: QMouseEvent = None):
        if self.__mask_label:
            if self.__mask_label.movie():
                self.__mask_label.movie().stop()
            self.__mask_label.setVisible(False)
            self.__mask_label.deleteLater()
            self.__mask_label = None
        if self.__drag_mode:
            self.widget.setStyleSheet(self.__drag_mode["stylesheet"])
            self.__drag_mode = None
            self._set_drag_widgets_cursor()

    def _set_drag_widgets_cursor(self):
        if not self.properties.window_drag_enabled or not self.properties.allow_drag_widgets_cursor_change:
            return

        for widget in self.properties.window_drag_widgets:
            if widget == self.widget or widget == self.main_win:
                continue
            if self.__drag_mode:
                self._set_widget_cursor(self.properties.start_drag_cursor, widget)
            else:
                self._set_widget_cursor(self.properties.end_drag_cursor, widget)


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

        # ACTION FRAME
        # ActionFrame cursor
        self.Widget_ActionFrame_Properties_allow_cursor_change = settings_dict["Widget_ActionFrame_Properties"].get("allow_cursor_change", False)
        self.Widget_ActionFrame_Properties_cursor = settings_dict["Widget_ActionFrame_Properties"].get("cursor", "")
        self.Widget_ActionFrame_Properties_cursor_width = settings_dict["Widget_ActionFrame_Properties"].get("cursor_width", 20)
        self.Widget_ActionFrame_Properties_cursor_height = settings_dict["Widget_ActionFrame_Properties"].get("cursor_height", 20)
        self.Widget_ActionFrame_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_ActionFrame_Properties"].get("cursor_keep_aspect_ratio", True)
        # Allow bypass mouse press event
        self.Widget_ActionFrame_Properties_allow_bypass_mouse_press_event = settings_dict["Widget_ActionFrame_Properties"].get("allow_bypass_mouse_press_event", False)
        # Tap event - animation
        self.Widget_ActionFrame_Properties_tap_event_show_animation_enabled = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_show_animation_enabled", False)
        self.Widget_ActionFrame_Properties_tap_event_show_animation_file_path = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_show_animation_file_path", "")
        self.Widget_ActionFrame_Properties_tap_event_show_animation_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_show_animation_duration_ms", 100)
        self.Widget_ActionFrame_Properties_tap_event_show_animation_width = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_show_animation_width", 20)
        self.Widget_ActionFrame_Properties_tap_event_show_animation_height = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_show_animation_height", 20)
        self.Widget_ActionFrame_Properties_tap_event_show_animation_background_color = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_show_animation_background_color", "transparent")
        # Tap event - play sound
        self.Widget_ActionFrame_Properties_tap_event_play_sound_enabled = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_play_sound_enabled", False)
        self.Widget_ActionFrame_Properties_tap_event_play_sound_file_path = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_play_sound_file_path", "")
        # Tap event - change stylesheet
        self.Widget_ActionFrame_Properties_tap_event_change_stylesheet_enabled = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_change_stylesheet_enabled", False)
        self.Widget_ActionFrame_Properties_tap_event_change_qss_stylesheet = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_change_qss_stylesheet", "")
        self.Widget_ActionFrame_Properties_tap_event_change_stylesheet_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_change_stylesheet_duration_ms", 100)
        # Tap event - change size
        self.Widget_ActionFrame_Properties_tap_event_change_size_enabled = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_change_size_enabled", False)
        self.Widget_ActionFrame_Properties_tap_event_change_size_percent = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_change_size_percent", 10)
        self.Widget_ActionFrame_Properties_tap_event_change_size_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("tap_event_change_size_duration_ms", 100)
        # Allow bypass enter event
        self.Widget_ActionFrame_Properties_allow_bypass_enter_event = settings_dict["Widget_ActionFrame_Properties"].get("allow_bypass_enter_event", False)
        # Enter event - animation
        self.Widget_ActionFrame_Properties_enter_event_show_animation_enabled = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_show_animation_enabled", False)
        self.Widget_ActionFrame_Properties_enter_event_show_animation_file_path = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_show_animation_file_path", "")
        self.Widget_ActionFrame_Properties_enter_event_show_animation_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_show_animation_duration_ms", 100)
        self.Widget_ActionFrame_Properties_enter_event_show_animation_width = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_show_animation_width", 20)
        self.Widget_ActionFrame_Properties_enter_event_show_animation_height = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_show_animation_height", 20)
        self.Widget_ActionFrame_Properties_enter_event_show_animation_background_color = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_show_animation_background_color", "transparent")
        # Enter event - play sound
        self.Widget_ActionFrame_Properties_enter_event_play_sound_enabled = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_play_sound_enabled", False)
        self.Widget_ActionFrame_Properties_enter_event_play_sound_file_path = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_play_sound_file_path", "")
        # Enter event - change stylesheet
        self.Widget_ActionFrame_Properties_enter_event_change_stylesheet_enabled = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_change_stylesheet_enabled", False)
        self.Widget_ActionFrame_Properties_enter_event_change_qss_stylesheet = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_change_qss_stylesheet", "")
        self.Widget_ActionFrame_Properties_enter_event_change_stylesheet_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_change_stylesheet_duration_ms", 100)
        # Enter event - change size
        self.Widget_ActionFrame_Properties_enter_event_change_size_enabled = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_change_size_enabled", False)
        self.Widget_ActionFrame_Properties_enter_event_change_size_percent = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_change_size_percent", 10)
        self.Widget_ActionFrame_Properties_enter_event_change_size_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("enter_event_change_size_duration_ms", 100)
        # Allow bypass leave event
        self.Widget_ActionFrame_Properties_allow_bypass_leave_event = settings_dict["Widget_ActionFrame_Properties"].get("allow_bypass_leave_event", False)
        # Leave event - animation
        self.Widget_ActionFrame_Properties_leave_event_show_animation_enabled = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_show_animation_enabled", False)
        self.Widget_ActionFrame_Properties_leave_event_show_animation_file_path = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_show_animation_file_path", "")
        self.Widget_ActionFrame_Properties_leave_event_show_animation_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_show_animation_duration_ms", 100)
        self.Widget_ActionFrame_Properties_leave_event_show_animation_width = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_show_animation_width", 20)
        self.Widget_ActionFrame_Properties_leave_event_show_animation_height = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_show_animation_height", 20)
        self.Widget_ActionFrame_Properties_leave_event_show_animation_background_color = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_show_animation_background_color", "transparent")
        # Leave event - play sound
        self.Widget_ActionFrame_Properties_leave_event_play_sound_enabled = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_play_sound_enabled", False)
        self.Widget_ActionFrame_Properties_leave_event_play_sound_file_path = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_play_sound_file_path", "")
        # Leave event - change stylesheet
        self.Widget_ActionFrame_Properties_leave_event_change_stylesheet_enabled = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_change_stylesheet_enabled", False)
        self.Widget_ActionFrame_Properties_leave_event_change_qss_stylesheet = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_change_qss_stylesheet", "")
        self.Widget_ActionFrame_Properties_leave_event_change_stylesheet_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_change_stylesheet_duration_ms", 100)
        # Leave event - change size
        self.Widget_ActionFrame_Properties_leave_event_change_size_enabled = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_change_size_enabled", False)
        self.Widget_ActionFrame_Properties_leave_event_change_size_percent = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_change_size_percent", 10)
        self.Widget_ActionFrame_Properties_leave_event_change_size_duration_ms = settings_dict["Widget_ActionFrame_Properties"].get("leave_event_change_size_duration_ms", 100)

        # DIALOG
        # Window drag
        self.Widget_Dialog_Properties_window_drag_enabled = settings_dict["Widget_Dialog_Properties"].get("window_drag_enabled", False)
        self.Widget_Dialog_Properties_window_drag_enabled_with_body = settings_dict["Widget_Dialog_Properties"].get("window_drag_enabled_with_body", False)
        self.Widget_Dialog_Properties_window_drag_widgets = settings_dict["Widget_Dialog_Properties"].get("window_drag_widgets", [])
        self.Widget_Dialog_Properties_allow_drag_widgets_cursor_change = settings_dict["Widget_Dialog_Properties"].get("allow_drag_widgets_cursor_change", False)
        self.Widget_Dialog_Properties_start_drag_cursor = settings_dict["Widget_Dialog_Properties"].get("start_drag_cursor", "")
        self.Widget_Dialog_Properties_end_drag_cursor = settings_dict["Widget_Dialog_Properties"].get("end_drag_cursor", "")
        self.Widget_Dialog_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_Dialog_Properties"].get("cursor_keep_aspect_ratio", True)
        self.Widget_Dialog_Properties_cursor_width = settings_dict["Widget_Dialog_Properties"].get("cursor_width", 20)
        self.Widget_Dialog_Properties_cursor_height = settings_dict["Widget_Dialog_Properties"].get("cursor_height", 20)
        # Mask Label
        self.Widget_Dialog_Properties_dragged_window_mask_label_enabled = settings_dict["Widget_Dialog_Properties"].get("dragged_window_mask_label_enabled", False)
        self.Widget_Dialog_Properties_dragged_window_mask_label_stylesheet = settings_dict["Widget_Dialog_Properties"].get("dragged_window_mask_label_stylesheet", "")
        self.Widget_Dialog_Properties_dragged_window_mask_label_image_path = settings_dict["Widget_Dialog_Properties"].get("dragged_window_mask_label_image_path", "")
        self.Widget_Dialog_Properties_dragged_window_mask_label_animation_path = settings_dict["Widget_Dialog_Properties"].get("dragged_window_mask_label_animation_path", "")
        # Call Close_me on ESCAPE
        self.Widget_Dialog_Properties_allow_bypass_key_press_event = settings_dict["Widget_Dialog_Properties"].get("allow_bypass_key_press_event", False)
        self.Widget_Dialog_Properties_call_close_me_on_escape = settings_dict["Widget_Dialog_Properties"].get("call_close_me_on_escape", False)
        # Close on Lost Focus
        self.Widget_Dialog_Properties_close_on_lost_focus = settings_dict["Widget_Dialog_Properties"].get("close_on_lost_focus", False)

        # FRAME
        # Frame drag
        self.Widget_Frame_Properties_window_drag_enabled = settings_dict["Widget_Frame_Properties"].get("window_drag_enabled", False)
        self.Widget_Frame_Properties_window_drag_enabled_with_body = settings_dict["Widget_Frame_Properties"].get("window_drag_enabled_with_body", False)
        self.Widget_Frame_Properties_window_drag_widgets = settings_dict["Widget_Frame_Properties"].get("window_drag_widgets", [])
        self.Widget_Frame_Properties_allow_drag_widgets_cursor_change = settings_dict["Widget_Frame_Properties"].get("allow_drag_widgets_cursor_change", False)
        self.Widget_Frame_Properties_start_drag_cursor = settings_dict["Widget_Frame_Properties"].get("start_drag_cursor", "9")
        self.Widget_Frame_Properties_end_drag_cursor = settings_dict["Widget_Frame_Properties"].get("end_drag_cursor", "")
        self.Widget_Frame_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_Frame_Properties"].get("cursor_keep_aspect_ratio", True)
        self.Widget_Frame_Properties_cursor_width = settings_dict["Widget_Frame_Properties"].get("cursor_width", 20)
        self.Widget_Frame_Properties_cursor_height = settings_dict["Widget_Frame_Properties"].get("cursor_height", 20)
        # Change style and add mask label
        self.Widget_Frame_Properties_dragged_window_change_stylesheet_enabled = settings_dict["Widget_Frame_Properties"].get("dragged_window_change_stylesheet_enabled", False)
        self.Widget_Frame_Properties_dragged_window_stylesheet = settings_dict["Widget_Frame_Properties"].get("dragged_window_stylesheet", "")
        self.Widget_Frame_Properties_dragged_window_mask_label_enabled = settings_dict["Widget_Frame_Properties"].get("dragged_window_mask_label_enabled", False)
        self.Widget_Frame_Properties_dragged_window_mask_label_stylesheet = settings_dict["Widget_Frame_Properties"].get("dragged_window_mask_label_stylesheet", "")
        self.Widget_Frame_Properties_dragged_window_mask_label_image_path = settings_dict["Widget_Frame_Properties"].get("dragged_window_mask_label_image_path", "")
        self.Widget_Frame_Properties_dragged_window_mask_label_animation_path = settings_dict["Widget_Frame_Properties"].get("dragged_window_mask_label_animation_path", "")

        # TEXTBOX
        # Allow bypass key press event
        self.Widget_TextBox_Properties_allow_bypass_key_press_event = settings_dict["Widget_TextBox_Properties"].get("allow_bypass_key_press_event", False)
        # Key Pressed - Play Sound
        self.Widget_TextBox_Properties_key_pressed_sound_enabled = settings_dict["Widget_TextBox_Properties"].get("key_pressed_sound_enabled", False)
        self.Widget_TextBox_Properties_key_pressed_sound_file_path = settings_dict["Widget_TextBox_Properties"].get("key_pressed_sound_file_path", "")
        # Key Pressed - change stylesheet
        self.Widget_TextBox_Properties_key_pressed_change_stylesheet_enabled = settings_dict["Widget_TextBox_Properties"].get("key_pressed_change_stylesheet_enabled", False)
        self.Widget_TextBox_Properties_key_pressed_change_qss_stylesheet = settings_dict["Widget_TextBox_Properties"].get("key_pressed_change_qss_stylesheet", "")
        self.Widget_TextBox_Properties_key_pressed_change_stylesheet_duration_ms = settings_dict["Widget_TextBox_Properties"].get("key_pressed_change_stylesheet_duration_ms", 500)
        # Key Pressed - change size
        self.Widget_TextBox_Properties_key_pressed_change_size_enabled = settings_dict["Widget_TextBox_Properties"].get("key_pressed_change_size_enabled", False)
        self.Widget_TextBox_Properties_key_pressed_change_size_percent = settings_dict["Widget_TextBox_Properties"].get("key_pressed_change_size_percent", 10)
        self.Widget_TextBox_Properties_key_pressed_change_size_duration_ms = settings_dict["Widget_TextBox_Properties"].get("key_pressed_change_size_duration_ms", 500)
        # RETURN Pressed - Play Sound
        self.Widget_TextBox_Properties_return_pressed_sound_enabled = settings_dict["Widget_TextBox_Properties"].get("return_pressed_sound_enabled", False)
        self.Widget_TextBox_Properties_return_pressed_sound_file_path = settings_dict["Widget_TextBox_Properties"].get("return_pressed_sound_file_path", "")
        # RETURN Pressed - change stylesheet
        self.Widget_TextBox_Properties_return_pressed_change_stylesheet_enabled = settings_dict["Widget_TextBox_Properties"].get("return_pressed_change_stylesheet_enabled", False)
        self.Widget_TextBox_Properties_return_pressed_change_qss_stylesheet = settings_dict["Widget_TextBox_Properties"].get("return_pressed_change_qss_stylesheet", "")
        self.Widget_TextBox_Properties_return_pressed_change_stylesheet_duration_ms = settings_dict["Widget_TextBox_Properties"].get("return_pressed_change_stylesheet_duration_ms", 500)
        # RETURN Pressed - change size
        self.Widget_TextBox_Properties_return_pressed_change_size_enabled = settings_dict["Widget_TextBox_Properties"].get("return_pressed_change_size_enabled", False)
        self.Widget_TextBox_Properties_return_pressed_change_size_percent = settings_dict["Widget_TextBox_Properties"].get("return_pressed_change_size_percent", 10)
        self.Widget_TextBox_Properties_return_pressed_change_size_duration_ms = settings_dict["Widget_TextBox_Properties"].get("return_pressed_change_size_duration_ms", 500)
        # ESCAPE Pressed - Play Sound
        self.Widget_TextBox_Properties_escape_pressed_sound_enabled = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_sound_enabled", False)
        self.Widget_TextBox_Properties_escape_pressed_sound_file_path = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_sound_file_path", "")
        # ESCAPE Pressed - change stylesheet
        self.Widget_TextBox_Properties_escape_pressed_change_stylesheet_enabled = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_change_stylesheet_enabled", False)
        self.Widget_TextBox_Properties_escape_pressed_change_qss_stylesheet = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_change_qss_stylesheet", "")
        self.Widget_TextBox_Properties_escape_pressed_change_stylesheet_duration_ms = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_change_stylesheet_duration_ms", 500)
        # ESCAPE Pressed - change size
        self.Widget_TextBox_Properties_escape_pressed_change_size_enabled = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_change_size_enabled", False)
        self.Widget_TextBox_Properties_escape_pressed_change_size_percent = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_change_size_percent", 10)
        self.Widget_TextBox_Properties_escape_pressed_change_size_duration_ms = settings_dict["Widget_TextBox_Properties"].get("escape_pressed_change_size_duration_ms", 500)
        # Smart parenthesis
        self.Widget_TextBox_Properties_smart_parenthesis_enabled = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_enabled", False)
        self.Widget_TextBox_Properties_smart_parenthesis_list = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_list", ["()", "[]", "{}", "''", '""'])
        self.Widget_TextBox_Properties_smart_parenthesis_list = self.parenthesis_list_validator(self.Widget_TextBox_Properties_smart_parenthesis_list)
        # Smart parenthesis - Play Sound
        self.Widget_TextBox_Properties_smart_parenthesis_sound_enabled = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_sound_enabled", False)
        self.Widget_TextBox_Properties_smart_parenthesis_success_sound_file_path = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_success_sound_file_path", "")
        self.Widget_TextBox_Properties_smart_parenthesis_fail_sound_file_path = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_fail_sound_file_path", "")
        # Smart parenthesis - change stylesheet
        self.Widget_TextBox_Properties_smart_parenthesis_change_stylesheet_enabled = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_change_stylesheet_enabled", False)
        self.Widget_TextBox_Properties_smart_parenthesis_change_qss_stylesheet = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_change_qss_stylesheet", "")
        self.Widget_TextBox_Properties_smart_parenthesis_change_stylesheet_duration_ms = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_change_stylesheet_duration_ms", 500)
        # Smart parenthesis - change size
        self.Widget_TextBox_Properties_smart_parenthesis_change_size_enabled = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_change_size_enabled", False)
        self.Widget_TextBox_Properties_smart_parenthesis_change_size_percent = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_change_size_percent", 10)
        self.Widget_TextBox_Properties_smart_parenthesis_change_size_duration_ms = settings_dict["Widget_TextBox_Properties"].get("smart_parenthesis_change_size_duration_ms", 500)
        # Illegal Entry - Play Sound
        self.Widget_TextBox_Properties_illegal_entry_validator = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_validator", None)
        self.Widget_TextBox_Properties_illegal_entry_sound_enabled = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_sound_enabled", False)
        self.Widget_TextBox_Properties_illegal_entry_sound_file_path = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_sound_file_path", "")
        # Illegal Entry - change stylesheet
        self.Widget_TextBox_Properties_illegal_entry_change_stylesheet_enabled = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_change_stylesheet_enabled", False)
        self.Widget_TextBox_Properties_illegal_entry_change_qss_stylesheet = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_change_qss_stylesheet", "")
        self.Widget_TextBox_Properties_illegal_entry_change_stylesheet_duration_ms = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_change_stylesheet_duration_ms", 500)
        # Illegal Entry - change size
        self.Widget_TextBox_Properties_illegal_entry_change_size_enabled = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_change_size_enabled", False)
        self.Widget_TextBox_Properties_illegal_entry_change_size_percent = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_change_size_percent", 10)
        self.Widget_TextBox_Properties_illegal_entry_change_size_duration_ms = settings_dict["Widget_TextBox_Properties"].get("illegal_entry_change_size_duration_ms", 500)

        # SELECTION WIDGETS
        # Selection cursor
        self.Widget_Selection_Properties_allow_cursor_change = settings_dict["Widget_Selection_Properties"].get("allow_cursor_change", False)
        self.Widget_Selection_Properties_cursor = settings_dict["Widget_Selection_Properties"].get("cursor", "")
        self.Widget_Selection_Properties_cursor_width = settings_dict["Widget_Selection_Properties"].get("cursor_width", 20)
        self.Widget_Selection_Properties_cursor_height = settings_dict["Widget_Selection_Properties"].get("cursor_height", 20)
        self.Widget_Selection_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_Selection_Properties"].get("cursor_keep_aspect_ratio", True)
        # Allow bypass mouse press event
        self.Widget_Selection_Properties_allow_bypass_mouse_press_event = settings_dict["Widget_Selection_Properties"].get("allow_bypass_mouse_press_event", False)
        # Tap event - animation
        self.Widget_Selection_Properties_tap_event_show_animation_enabled = settings_dict["Widget_Selection_Properties"].get("tap_event_show_animation_enabled", False)
        self.Widget_Selection_Properties_tap_event_show_animation_file_path = settings_dict["Widget_Selection_Properties"].get("tap_event_show_animation_file_path", "")
        self.Widget_Selection_Properties_tap_event_show_animation_duration_ms = settings_dict["Widget_Selection_Properties"].get("tap_event_show_animation_duration_ms", 100)
        self.Widget_Selection_Properties_tap_event_show_animation_width = settings_dict["Widget_Selection_Properties"].get("tap_event_show_animation_width", 20)
        self.Widget_Selection_Properties_tap_event_show_animation_height = settings_dict["Widget_Selection_Properties"].get("tap_event_show_animation_height", 20)
        self.Widget_Selection_Properties_tap_event_show_animation_background_color = settings_dict["Widget_Selection_Properties"].get("tap_event_show_animation_background_color", "transparent")
        # Tap event - play sound
        self.Widget_Selection_Properties_tap_event_play_sound_enabled = settings_dict["Widget_Selection_Properties"].get("tap_event_play_sound_enabled", False)
        self.Widget_Selection_Properties_tap_event_play_sound_file_path = settings_dict["Widget_Selection_Properties"].get("tap_event_play_sound_file_path", "")
        # Tap event - change stylesheet
        self.Widget_Selection_Properties_tap_event_change_stylesheet_enabled = settings_dict["Widget_Selection_Properties"].get("tap_event_change_stylesheet_enabled", False)
        self.Widget_Selection_Properties_tap_event_change_qss_stylesheet = settings_dict["Widget_Selection_Properties"].get("tap_event_change_qss_stylesheet", "")
        self.Widget_Selection_Properties_tap_event_change_stylesheet_duration_ms = settings_dict["Widget_Selection_Properties"].get("tap_event_change_stylesheet_duration_ms", 100)
        # Tap event - change size
        self.Widget_Selection_Properties_tap_event_change_size_enabled = settings_dict["Widget_Selection_Properties"].get("tap_event_change_size_enabled", False)
        self.Widget_Selection_Properties_tap_event_change_size_percent = settings_dict["Widget_Selection_Properties"].get("tap_event_change_size_percent", 10)
        self.Widget_Selection_Properties_tap_event_change_size_duration_ms = settings_dict["Widget_Selection_Properties"].get("tap_event_change_size_duration_ms", 100)
        # Allow bypass enter event
        self.Widget_Selection_Properties_allow_bypass_enter_event = settings_dict["Widget_Selection_Properties"].get("allow_bypass_enter_event", False)
        # Enter event - animation
        self.Widget_Selection_Properties_enter_event_show_animation_enabled = settings_dict["Widget_Selection_Properties"].get("enter_event_show_animation_enabled", False)
        self.Widget_Selection_Properties_enter_event_show_animation_file_path = settings_dict["Widget_Selection_Properties"].get("enter_event_show_animation_file_path", "")
        self.Widget_Selection_Properties_enter_event_show_animation_duration_ms = settings_dict["Widget_Selection_Properties"].get("enter_event_show_animation_duration_ms", 100)
        self.Widget_Selection_Properties_enter_event_show_animation_width = settings_dict["Widget_Selection_Properties"].get("enter_event_show_animation_width", 20)
        self.Widget_Selection_Properties_enter_event_show_animation_height = settings_dict["Widget_Selection_Properties"].get("enter_event_show_animation_height", 20)
        self.Widget_Selection_Properties_enter_event_show_animation_background_color = settings_dict["Widget_Selection_Properties"].get("enter_event_show_animation_background_color", "transparent")
        # Enter event - play sound
        self.Widget_Selection_Properties_enter_event_play_sound_enabled = settings_dict["Widget_Selection_Properties"].get("enter_event_play_sound_enabled", False)
        self.Widget_Selection_Properties_enter_event_play_sound_file_path = settings_dict["Widget_Selection_Properties"].get("enter_event_play_sound_file_path", "")
        # Enter event - change stylesheet
        self.Widget_Selection_Properties_enter_event_change_stylesheet_enabled = settings_dict["Widget_Selection_Properties"].get("enter_event_change_stylesheet_enabled", False)
        self.Widget_Selection_Properties_enter_event_change_qss_stylesheet = settings_dict["Widget_Selection_Properties"].get("enter_event_change_qss_stylesheet", "")
        self.Widget_Selection_Properties_enter_event_change_stylesheet_duration_ms = settings_dict["Widget_Selection_Properties"].get("enter_event_change_stylesheet_duration_ms", 100)
        # Enter event - change size
        self.Widget_Selection_Properties_enter_event_change_size_enabled = settings_dict["Widget_Selection_Properties"].get("enter_event_change_size_enabled", False)
        self.Widget_Selection_Properties_enter_event_change_size_percent = settings_dict["Widget_Selection_Properties"].get("enter_event_change_size_percent", 10)
        self.Widget_Selection_Properties_enter_event_change_size_duration_ms = settings_dict["Widget_Selection_Properties"].get("enter_event_change_size_duration_ms", 100)
        # Allow bypass leave event
        self.Widget_Selection_Properties_allow_bypass_leave_event = settings_dict["Widget_Selection_Properties"].get("allow_bypass_leave_event", False)
        # Leave event - animation
        self.Widget_Selection_Properties_leave_event_show_animation_enabled = settings_dict["Widget_Selection_Properties"].get("leave_event_show_animation_enabled", False)
        self.Widget_Selection_Properties_leave_event_show_animation_file_path = settings_dict["Widget_Selection_Properties"].get("leave_event_show_animation_file_path", "")
        self.Widget_Selection_Properties_leave_event_show_animation_duration_ms = settings_dict["Widget_Selection_Properties"].get("leave_event_show_animation_duration_ms", 100)
        self.Widget_Selection_Properties_leave_event_show_animation_width = settings_dict["Widget_Selection_Properties"].get("leave_event_show_animation_width", 20)
        self.Widget_Selection_Properties_leave_event_show_animation_height = settings_dict["Widget_Selection_Properties"].get("leave_event_show_animation_height", 20)
        self.Widget_Selection_Properties_leave_event_show_animation_background_color = settings_dict["Widget_Selection_Properties"].get("leave_event_show_animation_background_color", "transparent")
        # Leave event - play sound
        self.Widget_Selection_Properties_leave_event_play_sound_enabled = settings_dict["Widget_Selection_Properties"].get("leave_event_play_sound_enabled", False)
        self.Widget_Selection_Properties_leave_event_play_sound_file_path = settings_dict["Widget_Selection_Properties"].get("leave_event_play_sound_file_path", "")
        # Leave event - change stylesheet
        self.Widget_Selection_Properties_leave_event_change_stylesheet_enabled = settings_dict["Widget_Selection_Properties"].get("leave_event_change_stylesheet_enabled", False)
        self.Widget_Selection_Properties_leave_event_change_qss_stylesheet = settings_dict["Widget_Selection_Properties"].get("leave_event_change_qss_stylesheet", "")
        self.Widget_Selection_Properties_leave_event_change_stylesheet_duration_ms = settings_dict["Widget_Selection_Properties"].get("leave_event_change_stylesheet_duration_ms", 100)
        # Leave event - change size
        self.Widget_Selection_Properties_leave_event_change_size_enabled = settings_dict["Widget_Selection_Properties"].get("leave_event_change_size_enabled", False)
        self.Widget_Selection_Properties_leave_event_change_size_percent = settings_dict["Widget_Selection_Properties"].get("leave_event_change_size_percent", 10)
        self.Widget_Selection_Properties_leave_event_change_size_duration_ms = settings_dict["Widget_Selection_Properties"].get("leave_event_change_size_duration_ms", 100)

        # ITEM_BASED WIDGETS
        # ItemBased cursor
        self.Widget_ItemBased_Properties_allow_cursor_change = settings_dict["Widget_ItemBased_Properties"].get("allow_cursor_change", False)
        self.Widget_ItemBased_Properties_cursor = settings_dict["Widget_ItemBased_Properties"].get("cursor", "")
        self.Widget_ItemBased_Properties_cursor_width = settings_dict["Widget_ItemBased_Properties"].get("cursor_width", 20)
        self.Widget_ItemBased_Properties_cursor_height = settings_dict["Widget_ItemBased_Properties"].get("cursor_height", 20)
        self.Widget_ItemBased_Properties_cursor_keep_aspect_ratio = settings_dict["Widget_ItemBased_Properties"].get("cursor_keep_aspect_ratio", True)
        # Allow bypass mouse press event
        self.Widget_ItemBased_Properties_allow_bypass_mouse_press_event = settings_dict["Widget_ItemBased_Properties"].get("allow_bypass_mouse_press_event", False)
        # Tap event - animation
        self.Widget_ItemBased_Properties_tap_event_show_animation_enabled = settings_dict["Widget_ItemBased_Properties"].get("tap_event_show_animation_enabled", False)
        self.Widget_ItemBased_Properties_tap_event_show_animation_file_path = settings_dict["Widget_ItemBased_Properties"].get("tap_event_show_animation_file_path", "")
        self.Widget_ItemBased_Properties_tap_event_show_animation_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("tap_event_show_animation_duration_ms", 100)
        self.Widget_ItemBased_Properties_tap_event_show_animation_width = settings_dict["Widget_ItemBased_Properties"].get("tap_event_show_animation_width", 20)
        self.Widget_ItemBased_Properties_tap_event_show_animation_height = settings_dict["Widget_ItemBased_Properties"].get("tap_event_show_animation_height", 20)
        self.Widget_ItemBased_Properties_tap_event_show_animation_background_color = settings_dict["Widget_ItemBased_Properties"].get("tap_event_show_animation_background_color", "transparent")
        # Tap event - play sound
        self.Widget_ItemBased_Properties_tap_event_play_sound_enabled = settings_dict["Widget_ItemBased_Properties"].get("tap_event_play_sound_enabled", False)
        self.Widget_ItemBased_Properties_tap_event_play_sound_file_path = settings_dict["Widget_ItemBased_Properties"].get("tap_event_play_sound_file_path", "")
        # Tap event - change stylesheet
        self.Widget_ItemBased_Properties_tap_event_change_stylesheet_enabled = settings_dict["Widget_ItemBased_Properties"].get("tap_event_change_stylesheet_enabled", False)
        self.Widget_ItemBased_Properties_tap_event_change_qss_stylesheet = settings_dict["Widget_ItemBased_Properties"].get("tap_event_change_qss_stylesheet", "")
        self.Widget_ItemBased_Properties_tap_event_change_stylesheet_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("tap_event_change_stylesheet_duration_ms", 100)
        # Tap event - change size
        self.Widget_ItemBased_Properties_tap_event_change_size_enabled = settings_dict["Widget_ItemBased_Properties"].get("tap_event_change_size_enabled", False)
        self.Widget_ItemBased_Properties_tap_event_change_size_percent = settings_dict["Widget_ItemBased_Properties"].get("tap_event_change_size_percent", 10)
        self.Widget_ItemBased_Properties_tap_event_change_size_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("tap_event_change_size_duration_ms", 100)
        # Allow bypass enter event
        self.Widget_ItemBased_Properties_allow_bypass_enter_event = settings_dict["Widget_ItemBased_Properties"].get("allow_bypass_enter_event", False)
        # Enter event - animation
        self.Widget_ItemBased_Properties_enter_event_show_animation_enabled = settings_dict["Widget_ItemBased_Properties"].get("enter_event_show_animation_enabled", False)
        self.Widget_ItemBased_Properties_enter_event_show_animation_file_path = settings_dict["Widget_ItemBased_Properties"].get("enter_event_show_animation_file_path", "")
        self.Widget_ItemBased_Properties_enter_event_show_animation_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("enter_event_show_animation_duration_ms", 100)
        self.Widget_ItemBased_Properties_enter_event_show_animation_width = settings_dict["Widget_ItemBased_Properties"].get("enter_event_show_animation_width", 20)
        self.Widget_ItemBased_Properties_enter_event_show_animation_height = settings_dict["Widget_ItemBased_Properties"].get("enter_event_show_animation_height", 20)
        self.Widget_ItemBased_Properties_enter_event_show_animation_background_color = settings_dict["Widget_ItemBased_Properties"].get("enter_event_show_animation_background_color", "transparent")
        # Enter event - play sound
        self.Widget_ItemBased_Properties_enter_event_play_sound_enabled = settings_dict["Widget_ItemBased_Properties"].get("enter_event_play_sound_enabled", False)
        self.Widget_ItemBased_Properties_enter_event_play_sound_file_path = settings_dict["Widget_ItemBased_Properties"].get("enter_event_play_sound_file_path", "")
        # Enter event - change stylesheet
        self.Widget_ItemBased_Properties_enter_event_change_stylesheet_enabled = settings_dict["Widget_ItemBased_Properties"].get("enter_event_change_stylesheet_enabled", False)
        self.Widget_ItemBased_Properties_enter_event_change_qss_stylesheet = settings_dict["Widget_ItemBased_Properties"].get("enter_event_change_qss_stylesheet", "")
        self.Widget_ItemBased_Properties_enter_event_change_stylesheet_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("enter_event_change_stylesheet_duration_ms", 100)
        # Enter event - change size
        self.Widget_ItemBased_Properties_enter_event_change_size_enabled = settings_dict["Widget_ItemBased_Properties"].get("enter_event_change_size_enabled", False)
        self.Widget_ItemBased_Properties_enter_event_change_size_percent = settings_dict["Widget_ItemBased_Properties"].get("enter_event_change_size_percent", 10)
        self.Widget_ItemBased_Properties_enter_event_change_size_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("enter_event_change_size_duration_ms", 100)
        # Allow bypass leave event
        self.Widget_ItemBased_Properties_allow_bypass_leave_event = settings_dict["Widget_ItemBased_Properties"].get("allow_bypass_leave_event", False)
        # Leave event - animation
        self.Widget_ItemBased_Properties_leave_event_show_animation_enabled = settings_dict["Widget_ItemBased_Properties"].get("leave_event_show_animation_enabled", False)
        self.Widget_ItemBased_Properties_leave_event_show_animation_file_path = settings_dict["Widget_ItemBased_Properties"].get("leave_event_show_animation_file_path", "")
        self.Widget_ItemBased_Properties_leave_event_show_animation_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("leave_event_show_animation_duration_ms", 100)
        self.Widget_ItemBased_Properties_leave_event_show_animation_width = settings_dict["Widget_ItemBased_Properties"].get("leave_event_show_animation_width", 20)
        self.Widget_ItemBased_Properties_leave_event_show_animation_height = settings_dict["Widget_ItemBased_Properties"].get("leave_event_show_animation_height", 20)
        self.Widget_ItemBased_Properties_leave_event_show_animation_background_color = settings_dict["Widget_ItemBased_Properties"].get("leave_event_show_animation_background_color", "transparent")
        # Leave event - play sound
        self.Widget_ItemBased_Properties_leave_event_play_sound_enabled = settings_dict["Widget_ItemBased_Properties"].get("leave_event_play_sound_enabled", False)
        self.Widget_ItemBased_Properties_leave_event_play_sound_file_path = settings_dict["Widget_ItemBased_Properties"].get("leave_event_play_sound_file_path", "")
        # Leave event - change stylesheet
        self.Widget_ItemBased_Properties_leave_event_change_stylesheet_enabled = settings_dict["Widget_ItemBased_Properties"].get("leave_event_change_stylesheet_enabled", False)
        self.Widget_ItemBased_Properties_leave_event_change_qss_stylesheet = settings_dict["Widget_ItemBased_Properties"].get("leave_event_change_qss_stylesheet", "")
        self.Widget_ItemBased_Properties_leave_event_change_stylesheet_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("leave_event_change_stylesheet_duration_ms", 100)
        # Leave event - change size
        self.Widget_ItemBased_Properties_leave_event_change_size_enabled = settings_dict["Widget_ItemBased_Properties"].get("leave_event_change_size_enabled", False)
        self.Widget_ItemBased_Properties_leave_event_change_size_percent = settings_dict["Widget_ItemBased_Properties"].get("leave_event_change_size_percent", 10)
        self.Widget_ItemBased_Properties_leave_event_change_size_duration_ms = settings_dict["Widget_ItemBased_Properties"].get("leave_event_change_size_duration_ms", 100)

    def parenthesis_list_validator(self, parenthesis_list: list) -> list:
        result = []
        if isinstance(parenthesis_list, list) or isinstance(parenthesis_list, tuple):
            for parenthesis in parenthesis_list:
                if isinstance(parenthesis, str) and len(parenthesis) == 2:
                    result.append(parenthesis)
                else:
                    UTILS.TerminalUtility.WarningMessage("Invalid parenthesis '#1' in 'Widget_TextBox_Properties_smart_parenthesis_list'.", arguments=parenthesis, print_only=True)
        elif isinstance(parenthesis_list, str):
            parenthesis_list = parenthesis_list.split(",")
            for parenthesis in parenthesis_list:
                if isinstance(parenthesis, str) and len(parenthesis.strip()) == 2:
                    parenthesis = parenthesis.strip()
                    result.append(parenthesis)
                else:
                    UTILS.TerminalUtility.WarningMessage("Invalid parenthesis '#1' in 'Widget_TextBox_Properties_smart_parenthesis_list'.", arguments=parenthesis, print_only=True)

        return result

    def from_dict(self, properties_dict: dict) -> None:
        if not isinstance(properties_dict, dict):
            UTILS.TerminalUtility.WarningMessage("Variable #1 must be a dictionary.\ntype(properties_dict): #2\nproperties_dict = #3", ["properties_dict", type(properties_dict), properties_dict], exception_raised=True)
            raise ValueError(f"The properties_dict must be a dictionary not '{type(properties_dict)}'.")
        
        for section in properties_dict:
            if section.startswith("_GlobalWidgetsProperties"):
                print (f"Warning: section in properties_dict '{section}' is not allowed. SKIPPED!")
                continue

            if section not in self.sections:
                self.__dict__[section] = properties_dict[section]
            else:
                if not isinstance(properties_dict[section], dict):
                    UTILS.TerminalUtility.WarningMessage("Variable #1 must be a dictionary.\ntype(properties_dict[section]): #2\nproperties_dict[section] = #3", [f"properties_dict[{section}]", type(properties_dict[section]), properties_dict[section]], exception_raised=True)
                    raise ValueError(f"The properties_dict['{section}'] must be a dictionary not '{type(properties_dict[section])}'.")

                for property_name in properties_dict[section]:
                    if property_name.startswith("_GlobalWidgetsProperties"):
                        print (f"Warning: property_name in properties_dict '{property_name}' is not allowed. SKIPPED!")
                        continue

                    self.__dict__[f"{section}_{property_name}"] = properties_dict[section][property_name]

        self.Widget_TextBox_Properties_smart_parenthesis_list = self.parenthesis_list_validator(self.Widget_TextBox_Properties_smart_parenthesis_list)

    def to_dict(self) -> dict:
        result = {}
        for property_name, property_value in self.__dict__.items():
            if property_name.startswith("_GlobalWidgetsProperties"):
                continue

            result[property_name] = property_value
        
        return result


class Widget_TextBox_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:
        
        super().__init__()
        
        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties()

        # Allow bypass key press event
        self.allow_bypass_key_press_event = kwargs.get("allow_bypass_key_press_event") if kwargs.get("allow_bypass_key_press_event") is not None else self.global_widgets_properties.Widget_TextBox_Properties_allow_bypass_key_press_event
        # Key Pressed - Play Sound
        self.key_pressed_sound_enabled = kwargs.get("key_pressed_sound_enabled") if kwargs.get("key_pressed_sound_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_sound_enabled
        self.key_pressed_sound_file_path = kwargs.get("key_pressed_sound_file_path") if kwargs.get("key_pressed_sound_file_path") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_sound_file_path
        # Key Pressed - change stylesheet
        self.key_pressed_change_stylesheet_enabled = kwargs.get("key_pressed_change_stylesheet_enabled") if kwargs.get("key_pressed_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_change_stylesheet_enabled
        self.key_pressed_change_qss_stylesheet = kwargs.get("key_pressed_change_qss_stylesheet") if kwargs.get("key_pressed_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_change_qss_stylesheet
        self.key_pressed_change_stylesheet_duration_ms = kwargs.get("key_pressed_change_stylesheet_duration_ms") if kwargs.get("key_pressed_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_change_stylesheet_duration_ms
        # Key Pressed - change size
        self.key_pressed_change_size_enabled = kwargs.get("key_pressed_change_size_enabled") if kwargs.get("key_pressed_change_size_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_change_size_enabled
        self.key_pressed_change_size_percent = kwargs.get("key_pressed_change_size_percent") if kwargs.get("key_pressed_change_size_percent") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_change_size_percent
        self.key_pressed_change_size_duration_ms = kwargs.get("key_pressed_change_size_duration_ms") if kwargs.get("key_pressed_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_key_pressed_change_size_duration_ms

        # RETURN Pressed - Play Sound
        self.return_pressed_sound_enabled = kwargs.get("return_pressed_sound_enabled") if kwargs.get("return_pressed_sound_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_sound_enabled
        self.return_pressed_sound_file_path = kwargs.get("return_pressed_sound_file_path") if kwargs.get("return_pressed_sound_file_path") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_sound_file_path
        # RETURN Pressed - change stylesheet
        self.return_pressed_change_stylesheet_enabled = kwargs.get("return_pressed_change_stylesheet_enabled") if kwargs.get("return_pressed_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_change_stylesheet_enabled
        self.return_pressed_change_qss_stylesheet = kwargs.get("return_pressed_change_qss_stylesheet") if kwargs.get("return_pressed_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_change_qss_stylesheet
        self.return_pressed_change_stylesheet_duration_ms = kwargs.get("return_pressed_change_stylesheet_duration_ms") if kwargs.get("return_pressed_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_change_stylesheet_duration_ms
        # RETURN Pressed - change size
        self.return_pressed_change_size_enabled = kwargs.get("return_pressed_change_size_enabled") if kwargs.get("return_pressed_change_size_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_change_size_enabled
        self.return_pressed_change_size_percent = kwargs.get("return_pressed_change_size_percent") if kwargs.get("return_pressed_change_size_percent") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_change_size_percent
        self.return_pressed_change_size_duration_ms = kwargs.get("return_pressed_change_size_duration_ms") if kwargs.get("return_pressed_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_return_pressed_change_size_duration_ms

        # ESCAPE Pressed - Play Sound
        self.escape_pressed_sound_enabled = kwargs.get("escape_pressed_sound_enabled") if kwargs.get("escape_pressed_sound_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_sound_enabled
        self.escape_pressed_sound_file_path = kwargs.get("escape_pressed_sound_file_path") if kwargs.get("escape_pressed_sound_file_path") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_sound_file_path
        # ESCAPE Pressed - change stylesheet
        self.escape_pressed_change_stylesheet_enabled = kwargs.get("escape_pressed_change_stylesheet_enabled") if kwargs.get("escape_pressed_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_change_stylesheet_enabled
        self.escape_pressed_change_qss_stylesheet = kwargs.get("escape_pressed_change_qss_stylesheet") if kwargs.get("escape_pressed_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_change_qss_stylesheet
        self.escape_pressed_change_stylesheet_duration_ms = kwargs.get("escape_pressed_change_stylesheet_duration_ms") if kwargs.get("escape_pressed_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_change_stylesheet_duration_ms
        # ESCAPE Pressed - change size
        self.escape_pressed_change_size_enabled = kwargs.get("escape_pressed_change_size_enabled") if kwargs.get("escape_pressed_change_size_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_change_size_enabled
        self.escape_pressed_change_size_percent = kwargs.get("escape_pressed_change_size_percent") if kwargs.get("escape_pressed_change_size_percent") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_change_size_percent
        self.escape_pressed_change_size_duration_ms = kwargs.get("escape_pressed_change_size_duration_ms") if kwargs.get("escape_pressed_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_escape_pressed_change_size_duration_ms

        # Smart parenthesis
        self.smart_parenthesis_enabled = kwargs.get("smart_parenthesis_enabled") if kwargs.get("smart_parenthesis_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_enabled
        self.smart_parenthesis_list = kwargs.get("smart_parenthesis_list") if kwargs.get("smart_parenthesis_list") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_list
        # Smart parenthesis - Play Sound
        self.smart_parenthesis_sound_enabled = kwargs.get("smart_parenthesis_sound_enabled") if kwargs.get("smart_parenthesis_sound_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_sound_enabled
        self.smart_parenthesis_success_sound_file_path = kwargs.get("smart_parenthesis_success_sound_file_path") if kwargs.get("smart_parenthesis_success_sound_file_path") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_success_sound_file_path
        self.smart_parenthesis_fail_sound_file_path = kwargs.get("smart_parenthesis_fail_sound_file_path") if kwargs.get("smart_parenthesis_fail_sound_file_path") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_fail_sound_file_path
        # Smart parenthesis - change stylesheet
        self.smart_parenthesis_change_stylesheet_enabled = kwargs.get("smart_parenthesis_change_stylesheet_enabled") if kwargs.get("smart_parenthesis_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_change_stylesheet_enabled
        self.smart_parenthesis_change_qss_stylesheet = kwargs.get("smart_parenthesis_change_qss_stylesheet") if kwargs.get("smart_parenthesis_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_change_qss_stylesheet
        self.smart_parenthesis_change_stylesheet_duration_ms = kwargs.get("smart_parenthesis_change_stylesheet_duration_ms") if kwargs.get("smart_parenthesis_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_change_stylesheet_duration_ms
        # Smart parenthesis - change size
        self.smart_parenthesis_change_size_enabled = kwargs.get("smart_parenthesis_change_size_enabled") if kwargs.get("smart_parenthesis_change_size_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_change_size_enabled
        self.smart_parenthesis_change_size_percent = kwargs.get("smart_parenthesis_change_size_percent") if kwargs.get("smart_parenthesis_change_size_percent") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_change_size_percent
        self.smart_parenthesis_change_size_duration_ms = kwargs.get("smart_parenthesis_change_size_duration_ms") if kwargs.get("smart_parenthesis_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_smart_parenthesis_change_size_duration_ms

        # On Illegal Entry - Play Sound
        self.illegal_entry_validator = kwargs.get("illegal_entry_validator") if kwargs.get("illegal_entry_validator") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_validator
        self.illegal_entry_sound_enabled = kwargs.get("illegal_entry_sound_enabled") if kwargs.get("illegal_entry_sound_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_sound_enabled
        self.illegal_entry_sound_file_path = kwargs.get("illegal_entry_sound_file_path") if kwargs.get("illegal_entry_sound_file_path") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_sound_file_path
        # On Illegal Entry - change stylesheet
        self.illegal_entry_change_stylesheet_enabled = kwargs.get("illegal_entry_change_stylesheet_enabled") if kwargs.get("illegal_entry_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_change_stylesheet_enabled
        self.illegal_entry_change_qss_stylesheet = kwargs.get("illegal_entry_change_qss_stylesheet") if kwargs.get("illegal_entry_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_change_qss_stylesheet
        self.illegal_entry_change_stylesheet_duration_ms = kwargs.get("illegal_entry_change_stylesheet_duration_ms") if kwargs.get("illegal_entry_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_change_stylesheet_duration_ms
        # On Illegal Entry - change size
        self.illegal_entry_change_size_enabled = kwargs.get("illegal_entry_change_size_enabled") if kwargs.get("illegal_entry_change_size_enabled") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_change_size_enabled
        self.illegal_entry_change_size_percent = kwargs.get("illegal_entry_change_size_percent") if kwargs.get("illegal_entry_change_size_percent") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_change_size_percent
        self.illegal_entry_change_size_duration_ms = kwargs.get("illegal_entry_change_size_duration_ms") if kwargs.get("illegal_entry_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_TextBox_Properties_illegal_entry_change_size_duration_ms


class Widget_TextBox(AbstractWidget):
    MAX_HISTORY = 15

    def __init__(self, qdialog_widget: QDialog, main_win: QWidget = None, properties_setup: Widget_TextBox_Properties = None, timer_handler: TimerHandler = None) -> None:

        super().__init__(timer_handler=timer_handler)

        self.widget = qdialog_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_TextBox_Properties()
        self.history = []
        if not isinstance(self.properties, Widget_TextBox_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_TextBox_Properties not supported: #1\nUsed default Widget_TextBox_Properties", type(self.widget))
            self.properties = Widget_TextBox_Properties()

        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

    def _setup_widget(self):
        if self.properties.allow_bypass_key_press_event:
            self.widget.keyPressEvent = self.EVENT_key_press_event

    def EVENT_key_press_event(self, e: QKeyEvent):
        if isinstance(self.widget, QTextEdit):
            has_parenthesis = self.__add_smart_parenthesis_QTextEdit(e)
        elif isinstance(self.widget, QLineEdit):
            has_parenthesis = self.__add_smart_parenthesis_QLineEdit(e)
        else:
            UTILS.TerminalUtility.WarningMessage("Key press event failed. Unsupported widget type: #1\nKey press event cancelled.", type(self.widget))
            return

        # Update widget state
        if has_parenthesis is True:
            self._smart_parenthesis_update_state()
        elif has_parenthesis is False:
            self._smart_parenthesis_play_fail_sound()

        if not has_parenthesis:
            if has_parenthesis is False:
                play_sound = False
            else:
                play_sound = True
            
            if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
                if isinstance(self.widget, QLineEdit):
                    self.history_update(self.widget.text())
                self._return_press_update_state(play_sound=play_sound)
            elif e.key() == Qt.Key_Escape:
                self._escape_press_update_state(play_sound=play_sound)
            # Process key_up and key_down for LineEdit
            elif (e.key() == Qt.Key_Up or e.key() == Qt.Key_Down) and isinstance(self.widget, QLineEdit):
                self.history_move(self.widget.text(), "up" if e.key() == Qt.Key_Up else "down")
            else:
                self._key_press_update_state(play_sound=play_sound)

        # Update text in textbox. Smart parenthesis changed already text in textbox
        if not has_parenthesis and self.properties.allow_bypass_key_press_event:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.keyPressEvent(self.widget, e)

    def history_update(self, text: str):
        if not text.strip() or not isinstance(self.widget, QLineEdit):
            return
        
        if len(self.history) >= self.MAX_HISTORY:
            self.history.pop(0)
        
        if text in self.history:
            self.history.remove(text)
        
        self.history.append(text)

    def history_move(self, current_text: str, direction: str):
        if not isinstance(self.widget, QLineEdit):
            return

        if direction == "up":
            try:
                index = self.history.index(current_text)
            except ValueError:
                index = len(self.history)
            
            if index > 0:
                self.widget.setText(self.history[index - 1])
        elif direction == "down":
            try:
                index = self.history.index(current_text)
            except ValueError:
                self.widget.setText("")
                return
            
            if index < len(self.history) - 1:
                self.widget.setText(self.history[index + 1])

    def text_validation(self, is_text_valid: bool = None):
        if is_text_valid is None:
            if self._is_data_valid():
                return
        else:
            if is_text_valid:
                return

        self._illegal_entry_update_state()
    
    def _is_data_valid(self) -> bool:
        if self.properties.illegal_entry_validator:
            return self.properties.illegal_entry_validator()
        
        return True

    def _illegal_entry_update_state(self):
        # Sound
        self._illegal_entry_play_sound()

        # StyleSheet
        self._tap_event_change_stylesheet(e=None, e_enabled=self.properties.illegal_entry_change_stylesheet_enabled, e_qss=self.properties.illegal_entry_change_qss_stylesheet)
        if self.properties.illegal_entry_change_stylesheet_enabled:
            self._stylesheet_timer.set_duration(self.properties.illegal_entry_change_stylesheet_duration_ms)
            self._stylesheet_timer.start()
        
        # Widget size
        self._tap_event_change_size(None,
                                    e_enabled=self.properties.illegal_entry_change_size_enabled,
                                    e_percent=self.properties.illegal_entry_change_size_percent
                                    )
        if self.properties.illegal_entry_change_size_enabled:
            self._size_timer.set_duration(self.properties.illegal_entry_change_size_duration_ms)
            self._size_timer.start()

        QCoreApplication.processEvents()

    def _smart_parenthesis_update_state(self):
        # Sound
        self._smart_parenthesis_play_success_sound()

        # StyleSheet
        self._tap_event_change_stylesheet(e=None, e_enabled=self.properties.smart_parenthesis_change_stylesheet_enabled, e_qss=self.properties.smart_parenthesis_change_qss_stylesheet)
        if self.properties.smart_parenthesis_change_stylesheet_enabled:
            self._stylesheet_timer.set_duration(self.properties.smart_parenthesis_change_stylesheet_duration_ms)
            self._stylesheet_timer.start()

        # Widget size
        self._tap_event_change_size(None,
                                    e_enabled=self.properties.smart_parenthesis_change_size_enabled,
                                    e_percent=self.properties.smart_parenthesis_change_size_percent
                                    )
        if self.properties.smart_parenthesis_change_size_enabled:
            self._size_timer.set_duration(self.properties.smart_parenthesis_change_size_duration_ms)
            self._size_timer.start()
        
        QCoreApplication.processEvents()
    
    def _key_press_update_state(self, play_sound: bool = True):
        # Sound
        if play_sound:
            self._key_press_play_sound()

        # StyleSheet
        self._tap_event_change_stylesheet(e=None, e_enabled=self.properties.key_pressed_change_stylesheet_enabled, e_qss=self.properties.key_pressed_change_qss_stylesheet)
        if self.properties.key_pressed_change_stylesheet_enabled:
            self._stylesheet_timer.set_duration(self.properties.key_pressed_change_stylesheet_duration_ms)
            self._stylesheet_timer.start()

        # Widget size
        self._tap_event_change_size(None,
                                    e_enabled=self.properties.key_pressed_change_size_enabled,
                                    e_percent=self.properties.key_pressed_change_size_percent
                                    )
        if self.properties.key_pressed_change_size_enabled:
            self._size_timer.set_duration(self.properties.key_pressed_change_size_duration_ms)
            self._size_timer.start()
        
        QCoreApplication.processEvents()

    def _return_press_update_state(self, play_sound: bool = True):
        # Sound
        if play_sound:
            self._return_press_play_sound()

        # StyleSheet
        self._tap_event_change_stylesheet(e=None, e_enabled=self.properties.return_pressed_change_stylesheet_enabled, e_qss=self.properties.return_pressed_change_qss_stylesheet)
        if self.properties.return_pressed_change_stylesheet_enabled:
            self._stylesheet_timer.set_duration(self.properties.return_pressed_change_stylesheet_duration_ms)
            self._stylesheet_timer.start()

        # Widget size
        self._tap_event_change_size(None,
                                                        e_enabled=self.properties.return_pressed_change_size_enabled,
                                                        e_percent=self.properties.return_pressed_change_size_percent
                                                        )
        if self.properties.return_pressed_change_size_enabled:
            self._size_timer.set_duration(self.properties.return_pressed_change_size_duration_ms)
            self._size_timer.start()
        
        QCoreApplication.processEvents()

    def _escape_press_update_state(self, play_sound: bool = True):
        # Sound
        if play_sound:
            self._escape_press_play_sound()

        # StyleSheet
        self._tap_event_change_stylesheet(e=None, e_enabled=self.properties.escape_pressed_change_stylesheet_enabled, e_qss=self.properties.escape_pressed_change_qss_stylesheet)
        if self.properties.escape_pressed_change_stylesheet_enabled:
            self._stylesheet_timer.set_duration(self.properties.escape_pressed_change_stylesheet_duration_ms)
            self._stylesheet_timer.start()

        # Widget size
        self._tap_event_change_size(None,
                                                        e_enabled=self.properties.escape_pressed_change_size_enabled,
                                                        e_percent=self.properties.escape_pressed_change_size_percent
                                                        )
        if self.properties.escape_pressed_change_size_enabled:
            self._size_timer.set_duration(self.properties.escape_pressed_change_size_duration_ms)
            self._size_timer.start()
        
        QCoreApplication.processEvents()

    def __add_smart_parenthesis_QLineEdit(self, e: QKeyEvent) -> bool:
        if not self.properties.smart_parenthesis_enabled:
            return None
        
        if e.text() not in [x[0] for x in self.properties.smart_parenthesis_list]:
            return None
        
        self.widget: QLineEdit
        selected_text = self.widget.selectedText()
        
        if not selected_text:
            return False

        selection_start = self.widget.selectionStart()
        selection_end = self.widget.selectionEnd()
        text = self.widget.text()
        
        for parenthesis in self.properties.smart_parenthesis_list:
            if e.text() == parenthesis[0]:
                cur_pos = self.widget.cursorPosition()
                new_text = text[:selection_start] + f"{parenthesis[0]}{selected_text}{parenthesis[1]}" + text[selection_end:]
                self.widget.setText(new_text)
                self.widget.setCursorPosition(cur_pos)
                self.widget.setSelection(selection_start + 1, len(selected_text))
                return True
        
        return False

    def __add_smart_parenthesis_QTextEdit(self, e: QKeyEvent) -> bool:
        if not self.properties.smart_parenthesis_enabled:
            return None
        
        if e.key() not in [x[0] for x in self.properties.smart_parenthesis_list]:
            return None
        
        self.widget: QTextEdit
        cursor = self.widget.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            return False

        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()
        text = self.widget.toPlainText()
        
        for parenthesis in self.properties.smart_parenthesis_list:
            if e.key() == parenthesis[0]:
                cur_pos = cursor.position()
                new_text = text[:selection_start] + f"{parenthesis[0]}{selected_text}{parenthesis[1]}" + text[selection_end:]
                cursor.insertText(new_text)
                cursor.setPosition(cur_pos + 1)
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(selected_text))
                self.widget.setTextCursor(cursor)
                return True
        
        return False

    def _smart_parenthesis_play_success_sound(self):
        if not self.properties.smart_parenthesis_sound_enabled:
            return
        
        if not self.properties.smart_parenthesis_success_sound_file_path or not os.path.exists(self.properties.smart_parenthesis_success_sound_file_path):
            return
        
        self._tap_event_play_sound(e=None, e_enabled=True, e_file_path=self.properties.smart_parenthesis_success_sound_file_path)

    def _smart_parenthesis_play_fail_sound(self):
        if not self.properties.smart_parenthesis_sound_enabled:
            return
        
        if not self.properties.smart_parenthesis_fail_sound_file_path or not os.path.exists(self.properties.smart_parenthesis_fail_sound_file_path):
            return
        
        self._tap_event_play_sound(e=None, e_enabled=True, e_file_path=self.properties.smart_parenthesis_fail_sound_file_path)

    def _illegal_entry_play_sound(self):
        if not self.properties.illegal_entry_sound_enabled:
            return
        
        if not self.properties.illegal_entry_sound_file_path or not os.path.exists(self.properties.illegal_entry_sound_file_path):
            return
    
        self._tap_event_play_sound(e=None, e_enabled=True, e_file_path=self.properties.illegal_entry_sound_file_path)

    def _key_press_play_sound(self):
        if not self.properties.key_pressed_sound_enabled:
            return
        
        if not self.properties.key_pressed_sound_file_path or not os.path.exists(self.properties.key_pressed_sound_file_path):
            return
        
        self._tap_event_play_sound(e=None, e_enabled=True, e_file_path=self.properties.key_pressed_sound_file_path)

    def _return_press_play_sound(self):
        if not self.properties.return_pressed_sound_enabled:
            return
        
        if not self.properties.return_pressed_sound_file_path or not os.path.exists(self.properties.return_pressed_sound_file_path):
            return
    
        self._tap_event_play_sound(e=None, e_enabled=True, e_file_path=self.properties.return_pressed_sound_file_path)

    def _escape_press_play_sound(self):
        if not self.properties.escape_pressed_sound_enabled:
            return
        
        if not self.properties.escape_pressed_sound_file_path or not os.path.exists(self.properties.escape_pressed_sound_file_path):
            return
        
        self._tap_event_play_sound(e=None, e_enabled=True, e_file_path=self.properties.escape_pressed_sound_file_path)


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
    def __init__(self, qpushbutton_widget: QPushButton, main_win: QWidget = None, properties_setup: Widget_PushButton_Properties = None, timer_handler: TimerHandler = None) -> None:
        super().__init__(timer_handler=timer_handler)
        
        self.widget = qpushbutton_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_PushButton_Properties()
        if not isinstance(self.properties, Widget_PushButton_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_PushButton_Properties type not supported: #1\nUsed default properties", type(self.widget))
            self.properties = Widget_PushButton_Properties()

        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

    def _setup_widget(self):
        # Tap Event
        if self.properties.allow_bypass_mouse_press_event:
            self.widget.mousePressEvent = lambda e: self.EVENT_mouse_press_event(e, return_event_to_super = True)
            if isinstance(self.widget, QToolButton):
                self.widget.clicked.connect(self.EVENT_clicked_event)
        # Enter Event
        if self.properties.allow_bypass_enter_event:
            self.widget.enterEvent = lambda e: self.EVENT_enter_event(e, return_event_to_super=True)
        # Leave Event
        if self.properties.allow_bypass_leave_event:
            self.widget.leaveEvent = lambda e: self.EVENT_leave_event(e, return_event_to_super=True)
        # Cursor
        if self.properties.allow_cursor_change:
            self._set_widget_cursor(self.properties.cursor, self.widget)

    def EVENT_clicked_event(self):
        e = None
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.tap_event_play_sound_enabled,
                                    e_file_path=self.properties.tap_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.tap_event_change_stylesheet_enabled,
                                            e_qss=self.properties.tap_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.tap_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.tap_event_show_animation_file_path)
        if self.properties.tap_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.tap_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.tap_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.tap_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.tap_event_play_sound_file_path)

    def EVENT_mouse_press_event(self, e: QMouseEvent, return_event_to_super = False):
        if e and e.button() != Qt.LeftButton:
            if return_event_to_super:
                ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
                ReturnEvent.mousePressEvent(self.widget, e)
            return
        
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.tap_event_play_sound_enabled,
                                    e_file_path=self.properties.tap_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.tap_event_change_stylesheet_enabled,
                                            e_qss=self.properties.tap_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.tap_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.tap_event_show_animation_file_path)
        if self.properties.tap_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.tap_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.tap_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.tap_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.tap_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.mousePressEvent(self.widget, e)

    def EVENT_enter_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.enter_event_play_sound_enabled,
                                    e_file_path=self.properties.enter_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.enter_event_change_stylesheet_enabled,
                                            e_qss=self.properties.enter_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.enter_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.enter_event_show_animation_file_path)
        if self.properties.enter_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.enter_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.enter_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.enter_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.enter_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.enterEvent(self.widget, e)

    def EVENT_leave_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.leave_event_play_sound_enabled,
                                    e_file_path=self.properties.leave_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.leave_event_change_stylesheet_enabled,
                                            e_qss=self.properties.leave_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.leave_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.leave_event_show_animation_file_path)
        if self.properties.leave_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.leave_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.leave_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.leave_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.leave_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.leaveEvent(self.widget, e)


class Widget_Selection_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:

        super().__init__()

        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties({})

        # Selection cursor
        self.allow_cursor_change = kwargs.get("allow_cursor_change") if kwargs.get("allow_cursor_change") is not None else self.global_widgets_properties.Widget_Selection_Properties_allow_cursor_change
        self.cursor = kwargs.get("cursor") if kwargs.get("cursor") is not None else self.global_widgets_properties.Widget_Selection_Properties_cursor
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_Selection_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_Selection_Properties_cursor_height
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_Selection_Properties_cursor_keep_aspect_ratio
        # Allow bypass mouse press event
        self.allow_bypass_mouse_press_event = kwargs.get("allow_bypass_mouse_press_event") if kwargs.get("allow_bypass_mouse_press_event") is not None else self.global_widgets_properties.Widget_Selection_Properties_allow_bypass_mouse_press_event
        # Tap event - animation
        self.tap_event_show_animation_enabled = kwargs.get("tap_event_show_animation_enabled") if kwargs.get("tap_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_show_animation_enabled
        self.tap_event_show_animation_file_path = kwargs.get("tap_event_show_animation_file_path") if kwargs.get("tap_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_show_animation_file_path
        self.tap_event_show_animation_duration_ms = kwargs.get("tap_event_show_animation_duration_ms") if kwargs.get("tap_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_show_animation_duration_ms
        self.tap_event_show_animation_width = kwargs.get("tap_event_show_animation_width") if kwargs.get("tap_event_show_animation_width") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_show_animation_width
        self.tap_event_show_animation_height = kwargs.get("tap_event_show_animation_height") if kwargs.get("tap_event_show_animation_height") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_show_animation_height
        self.tap_event_show_animation_background_color = kwargs.get("tap_event_show_animation_background_color") if kwargs.get("tap_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_show_animation_background_color
        # Tap event - play sound
        self.tap_event_play_sound_enabled = kwargs.get("tap_event_play_sound_enabled") if kwargs.get("tap_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_play_sound_enabled
        self.tap_event_play_sound_file_path = kwargs.get("tap_event_play_sound_file_path") if kwargs.get("tap_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_play_sound_file_path
        # Tap event - change stylesheet
        self.tap_event_change_stylesheet_enabled = kwargs.get("tap_event_change_stylesheet_enabled") if kwargs.get("tap_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_change_stylesheet_enabled
        self.tap_event_change_qss_stylesheet = kwargs.get("tap_event_change_qss_stylesheet") if kwargs.get("tap_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_change_qss_stylesheet
        self.tap_event_change_stylesheet_duration_ms = kwargs.get("tap_event_change_stylesheet_duration_ms") if kwargs.get("tap_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_change_stylesheet_duration_ms
        # Tap event - change size
        self.tap_event_change_size_enabled = kwargs.get("tap_event_change_size_enabled") if kwargs.get("tap_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_change_size_enabled
        self.tap_event_change_size_percent = kwargs.get("tap_event_change_size_percent") if kwargs.get("tap_event_change_size_percent") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_change_size_percent
        self.tap_event_change_size_duration_ms = kwargs.get("tap_event_change_size_duration_ms") if kwargs.get("tap_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_tap_event_change_size_duration_ms
        # Allow bypass enter event
        self.allow_bypass_enter_event = kwargs.get("allow_bypass_enter_event") if kwargs.get("allow_bypass_enter_event") is not None else self.global_widgets_properties.Widget_Selection_Properties_allow_bypass_enter_event
        # Enter event - animation
        self.enter_event_show_animation_enabled = kwargs.get("enter_event_show_animation_enabled") if kwargs.get("enter_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_show_animation_enabled
        self.enter_event_show_animation_file_path = kwargs.get("enter_event_show_animation_file_path") if kwargs.get("enter_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_show_animation_file_path
        self.enter_event_show_animation_duration_ms = kwargs.get("enter_event_show_animation_duration_ms") if kwargs.get("enter_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_show_animation_duration_ms
        self.enter_event_show_animation_width = kwargs.get("enter_event_show_animation_width") if kwargs.get("enter_event_show_animation_width") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_show_animation_width
        self.enter_event_show_animation_height = kwargs.get("enter_event_show_animation_height") if kwargs.get("enter_event_show_animation_height") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_show_animation_height
        self.enter_event_show_animation_background_color = kwargs.get("enter_event_show_animation_background_color") if kwargs.get("enter_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_show_animation_background_color
        # Enter event - play sound
        self.enter_event_play_sound_enabled = kwargs.get("enter_event_play_sound_enabled") if kwargs.get("enter_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_play_sound_enabled
        self.enter_event_play_sound_file_path = kwargs.get("enter_event_play_sound_file_path") if kwargs.get("enter_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_play_sound_file_path
        # Enter event - change stylesheet
        self.enter_event_change_stylesheet_enabled = kwargs.get("enter_event_change_stylesheet_enabled") if kwargs.get("enter_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_change_stylesheet_enabled
        self.enter_event_change_qss_stylesheet = kwargs.get("enter_event_change_qss_stylesheet") if kwargs.get("enter_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_change_qss_stylesheet
        self.enter_event_change_stylesheet_duration_ms = kwargs.get("enter_event_change_stylesheet_duration_ms") if kwargs.get("enter_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_change_stylesheet_duration_ms
        # Enter event - change size
        self.enter_event_change_size_enabled = kwargs.get("enter_event_change_size_enabled") if kwargs.get("enter_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_change_size_enabled
        self.enter_event_change_size_percent = kwargs.get("enter_event_change_size_percent") if kwargs.get("enter_event_change_size_percent") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_change_size_percent
        self.enter_event_change_size_duration_ms = kwargs.get("enter_event_change_size_duration_ms") if kwargs.get("enter_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_enter_event_change_size_duration_ms
        # Allow bypass leave event
        self.allow_bypass_leave_event = kwargs.get("allow_bypass_leave_event") if kwargs.get("allow_bypass_leave_event") is not None else self.global_widgets_properties.Widget_Selection_Properties_allow_bypass_leave_event
        # Leave event - animation
        self.leave_event_show_animation_enabled = kwargs.get("leave_event_show_animation_enabled") if kwargs.get("leave_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_show_animation_enabled
        self.leave_event_show_animation_file_path = kwargs.get("leave_event_show_animation_file_path") if kwargs.get("leave_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_show_animation_file_path
        self.leave_event_show_animation_duration_ms = kwargs.get("leave_event_show_animation_duration_ms") if kwargs.get("leave_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_show_animation_duration_ms
        self.leave_event_show_animation_width = kwargs.get("leave_event_show_animation_width") if kwargs.get("leave_event_show_animation_width") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_show_animation_width
        self.leave_event_show_animation_height = kwargs.get("leave_event_show_animation_height") if kwargs.get("leave_event_show_animation_height") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_show_animation_height
        self.leave_event_show_animation_background_color = kwargs.get("leave_event_show_animation_background_color") if kwargs.get("leave_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_show_animation_background_color
        # Leave event - play sound
        self.leave_event_play_sound_enabled = kwargs.get("leave_event_play_sound_enabled") if kwargs.get("leave_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_play_sound_enabled
        self.leave_event_play_sound_file_path = kwargs.get("leave_event_play_sound_file_path") if kwargs.get("leave_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_play_sound_file_path
        # Leave event - change stylesheet
        self.leave_event_change_stylesheet_enabled = kwargs.get("leave_event_change_stylesheet_enabled") if kwargs.get("leave_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_change_stylesheet_enabled
        self.leave_event_change_qss_stylesheet = kwargs.get("leave_event_change_qss_stylesheet") if kwargs.get("leave_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_change_qss_stylesheet
        self.leave_event_change_stylesheet_duration_ms = kwargs.get("leave_event_change_stylesheet_duration_ms") if kwargs.get("leave_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_change_stylesheet_duration_ms
        # Leave event - change size
        self.leave_event_change_size_enabled = kwargs.get("leave_event_change_size_enabled") if kwargs.get("leave_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_change_size_enabled
        self.leave_event_change_size_percent = kwargs.get("leave_event_change_size_percent") if kwargs.get("leave_event_change_size_percent") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_change_size_percent
        self.leave_event_change_size_duration_ms = kwargs.get("leave_event_change_size_duration_ms") if kwargs.get("leave_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_Selection_Properties_leave_event_change_size_duration_ms


class Widget_Selection(AbstractWidget):
    def __init__(self, selection_widget: QWidget, main_win: QWidget = None, properties_setup: Widget_Selection_Properties = None, timer_handler: TimerHandler = None) -> None:
        super().__init__(timer_handler=timer_handler)
        
        self.widget = selection_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_Selection_Properties()
        if not isinstance(self.properties, Widget_Selection_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_Selection_Properties type not supported: #1\nUsed default properties.", type(self.widget))
            self.properties = Widget_Selection_Properties()

        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

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
        if e and e.button() != Qt.LeftButton:
            if return_event_to_super:
                ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
                ReturnEvent.mousePressEvent(self.widget, e)
            return
        
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.tap_event_play_sound_enabled,
                                    e_file_path=self.properties.tap_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.tap_event_change_stylesheet_enabled,
                                            e_qss=self.properties.tap_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.tap_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.tap_event_show_animation_file_path)
        if self.properties.tap_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.tap_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.tap_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.tap_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.tap_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.mousePressEvent(self.widget, e)

    def EVENT_enter_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.enter_event_play_sound_enabled,
                                    e_file_path=self.properties.enter_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.enter_event_change_stylesheet_enabled,
                                            e_qss=self.properties.enter_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            
        if start_animation:
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.enter_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.enter_event_show_animation_file_path)
        if self.properties.enter_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.enter_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.enter_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.enter_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.enter_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.enterEvent(self.widget, e)

        QCoreApplication.processEvents()

    def EVENT_leave_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.leave_event_play_sound_enabled,
                                    e_file_path=self.properties.leave_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.leave_event_change_stylesheet_enabled,
                                            e_qss=self.properties.leave_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.leave_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.leave_event_show_animation_file_path)
        if self.properties.leave_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.leave_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.leave_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.leave_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.leave_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.leaveEvent(self.widget, e)


class Widget_ItemBased_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:

        super().__init__()

        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties({})

        # ItemBased cursor
        self.allow_cursor_change = kwargs.get("allow_cursor_change") if kwargs.get("allow_cursor_change") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_allow_cursor_change
        self.cursor = kwargs.get("cursor") if kwargs.get("cursor") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_cursor
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_cursor_height
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_cursor_keep_aspect_ratio
        # Allow bypass mouse press event
        self.allow_bypass_mouse_press_event = kwargs.get("allow_bypass_mouse_press_event") if kwargs.get("allow_bypass_mouse_press_event") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_allow_bypass_mouse_press_event
        # Tap event - animation
        self.tap_event_show_animation_enabled = kwargs.get("tap_event_show_animation_enabled") if kwargs.get("tap_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_show_animation_enabled
        self.tap_event_show_animation_file_path = kwargs.get("tap_event_show_animation_file_path") if kwargs.get("tap_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_show_animation_file_path
        self.tap_event_show_animation_duration_ms = kwargs.get("tap_event_show_animation_duration_ms") if kwargs.get("tap_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_show_animation_duration_ms
        self.tap_event_show_animation_width = kwargs.get("tap_event_show_animation_width") if kwargs.get("tap_event_show_animation_width") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_show_animation_width
        self.tap_event_show_animation_height = kwargs.get("tap_event_show_animation_height") if kwargs.get("tap_event_show_animation_height") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_show_animation_height
        self.tap_event_show_animation_background_color = kwargs.get("tap_event_show_animation_background_color") if kwargs.get("tap_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_show_animation_background_color
        # Tap event - play sound
        self.tap_event_play_sound_enabled = kwargs.get("tap_event_play_sound_enabled") if kwargs.get("tap_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_play_sound_enabled
        self.tap_event_play_sound_file_path = kwargs.get("tap_event_play_sound_file_path") if kwargs.get("tap_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_play_sound_file_path
        # Tap event - change stylesheet
        self.tap_event_change_stylesheet_enabled = kwargs.get("tap_event_change_stylesheet_enabled") if kwargs.get("tap_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_change_stylesheet_enabled
        self.tap_event_change_qss_stylesheet = kwargs.get("tap_event_change_qss_stylesheet") if kwargs.get("tap_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_change_qss_stylesheet
        self.tap_event_change_stylesheet_duration_ms = kwargs.get("tap_event_change_stylesheet_duration_ms") if kwargs.get("tap_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_change_stylesheet_duration_ms
        # Tap event - change size
        self.tap_event_change_size_enabled = kwargs.get("tap_event_change_size_enabled") if kwargs.get("tap_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_change_size_enabled
        self.tap_event_change_size_percent = kwargs.get("tap_event_change_size_percent") if kwargs.get("tap_event_change_size_percent") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_change_size_percent
        self.tap_event_change_size_duration_ms = kwargs.get("tap_event_change_size_duration_ms") if kwargs.get("tap_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_tap_event_change_size_duration_ms
        # Allow bypass enter event
        self.allow_bypass_enter_event = kwargs.get("allow_bypass_enter_event") if kwargs.get("allow_bypass_enter_event") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_allow_bypass_enter_event
        # Enter event - animation
        self.enter_event_show_animation_enabled = kwargs.get("enter_event_show_animation_enabled") if kwargs.get("enter_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_show_animation_enabled
        self.enter_event_show_animation_file_path = kwargs.get("enter_event_show_animation_file_path") if kwargs.get("enter_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_show_animation_file_path
        self.enter_event_show_animation_duration_ms = kwargs.get("enter_event_show_animation_duration_ms") if kwargs.get("enter_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_show_animation_duration_ms
        self.enter_event_show_animation_width = kwargs.get("enter_event_show_animation_width") if kwargs.get("enter_event_show_animation_width") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_show_animation_width
        self.enter_event_show_animation_height = kwargs.get("enter_event_show_animation_height") if kwargs.get("enter_event_show_animation_height") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_show_animation_height
        self.enter_event_show_animation_background_color = kwargs.get("enter_event_show_animation_background_color") if kwargs.get("enter_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_show_animation_background_color
        # Enter event - play sound
        self.enter_event_play_sound_enabled = kwargs.get("enter_event_play_sound_enabled") if kwargs.get("enter_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_play_sound_enabled
        self.enter_event_play_sound_file_path = kwargs.get("enter_event_play_sound_file_path") if kwargs.get("enter_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_play_sound_file_path
        # Enter event - change stylesheet
        self.enter_event_change_stylesheet_enabled = kwargs.get("enter_event_change_stylesheet_enabled") if kwargs.get("enter_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_change_stylesheet_enabled
        self.enter_event_change_qss_stylesheet = kwargs.get("enter_event_change_qss_stylesheet") if kwargs.get("enter_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_change_qss_stylesheet
        self.enter_event_change_stylesheet_duration_ms = kwargs.get("enter_event_change_stylesheet_duration_ms") if kwargs.get("enter_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_change_stylesheet_duration_ms
        # Enter event - change size
        self.enter_event_change_size_enabled = kwargs.get("enter_event_change_size_enabled") if kwargs.get("enter_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_change_size_enabled
        self.enter_event_change_size_percent = kwargs.get("enter_event_change_size_percent") if kwargs.get("enter_event_change_size_percent") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_change_size_percent
        self.enter_event_change_size_duration_ms = kwargs.get("enter_event_change_size_duration_ms") if kwargs.get("enter_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_enter_event_change_size_duration_ms
        # Allow bypass leave event
        self.allow_bypass_leave_event = kwargs.get("allow_bypass_leave_event") if kwargs.get("allow_bypass_leave_event") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_allow_bypass_leave_event
        # Leave event - animation
        self.leave_event_show_animation_enabled = kwargs.get("leave_event_show_animation_enabled") if kwargs.get("leave_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_show_animation_enabled
        self.leave_event_show_animation_file_path = kwargs.get("leave_event_show_animation_file_path") if kwargs.get("leave_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_show_animation_file_path
        self.leave_event_show_animation_duration_ms = kwargs.get("leave_event_show_animation_duration_ms") if kwargs.get("leave_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_show_animation_duration_ms
        self.leave_event_show_animation_width = kwargs.get("leave_event_show_animation_width") if kwargs.get("leave_event_show_animation_width") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_show_animation_width
        self.leave_event_show_animation_height = kwargs.get("leave_event_show_animation_height") if kwargs.get("leave_event_show_animation_height") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_show_animation_height
        self.leave_event_show_animation_background_color = kwargs.get("leave_event_show_animation_background_color") if kwargs.get("leave_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_show_animation_background_color
        # Leave event - play sound
        self.leave_event_play_sound_enabled = kwargs.get("leave_event_play_sound_enabled") if kwargs.get("leave_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_play_sound_enabled
        self.leave_event_play_sound_file_path = kwargs.get("leave_event_play_sound_file_path") if kwargs.get("leave_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_play_sound_file_path
        # Leave event - change stylesheet
        self.leave_event_change_stylesheet_enabled = kwargs.get("leave_event_change_stylesheet_enabled") if kwargs.get("leave_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_change_stylesheet_enabled
        self.leave_event_change_qss_stylesheet = kwargs.get("leave_event_change_qss_stylesheet") if kwargs.get("leave_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_change_qss_stylesheet
        self.leave_event_change_stylesheet_duration_ms = kwargs.get("leave_event_change_stylesheet_duration_ms") if kwargs.get("leave_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_change_stylesheet_duration_ms
        # Leave event - change size
        self.leave_event_change_size_enabled = kwargs.get("leave_event_change_size_enabled") if kwargs.get("leave_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_change_size_enabled
        self.leave_event_change_size_percent = kwargs.get("leave_event_change_size_percent") if kwargs.get("leave_event_change_size_percent") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_change_size_percent
        self.leave_event_change_size_duration_ms = kwargs.get("leave_event_change_size_duration_ms") if kwargs.get("leave_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_ItemBased_Properties_leave_event_change_size_duration_ms


class Widget_ItemBased(AbstractWidget):
    def __init__(self, list_table_tree_widget: QWidget, main_win: QWidget = None, properties_setup: Widget_ItemBased_Properties = None, timer_handler: TimerHandler = None) -> None:
        super().__init__(timer_handler=timer_handler)
        
        self.widget = list_table_tree_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_ItemBased_Properties()
        if not isinstance(self.properties, Widget_ItemBased_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_ItemBased_Properties type not supported: #1\nUsed default properties.", type(self.widget))
            self.properties = Widget_ItemBased_Properties()

        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

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
        if e and e.button() != Qt.LeftButton:
            if return_event_to_super:
                ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
                ReturnEvent.mousePressEvent(self.widget, e)
            return
        
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.tap_event_play_sound_enabled,
                                    e_file_path=self.properties.tap_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.tap_event_change_stylesheet_enabled,
                                            e_qss=self.properties.tap_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.tap_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.tap_event_show_animation_file_path)
        if self.properties.tap_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.tap_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.tap_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.tap_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.tap_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.mousePressEvent(self.widget, e)

    def EVENT_enter_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.enter_event_play_sound_enabled,
                                    e_file_path=self.properties.enter_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.enter_event_change_stylesheet_enabled,
                                            e_qss=self.properties.enter_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.enter_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.enter_event_show_animation_file_path)
        if self.properties.enter_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.enter_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.enter_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.enter_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.enter_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.enterEvent(self.widget, e)

    def EVENT_leave_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.leave_event_play_sound_enabled,
                                    e_file_path=self.properties.leave_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.leave_event_change_stylesheet_enabled,
                                            e_qss=self.properties.leave_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.leave_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.leave_event_show_animation_file_path)
        if self.properties.leave_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.leave_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.leave_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.leave_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.leave_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.leaveEvent(self.widget, e)


class Widget_ActionFrame_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:

        super().__init__()

        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties({})

        # ActionFrame cursor
        self.allow_cursor_change = kwargs.get("allow_cursor_change") if kwargs.get("allow_cursor_change") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_allow_cursor_change
        self.cursor = kwargs.get("cursor") if kwargs.get("cursor") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_cursor
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_cursor_height
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_cursor_keep_aspect_ratio
        # Allow bypass mouse press event
        self.allow_bypass_mouse_press_event = kwargs.get("allow_bypass_mouse_press_event") if kwargs.get("allow_bypass_mouse_press_event") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_allow_bypass_mouse_press_event
        # Tap event - animation
        self.tap_event_show_animation_enabled = kwargs.get("tap_event_show_animation_enabled") if kwargs.get("tap_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_show_animation_enabled
        self.tap_event_show_animation_file_path = kwargs.get("tap_event_show_animation_file_path") if kwargs.get("tap_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_show_animation_file_path
        self.tap_event_show_animation_duration_ms = kwargs.get("tap_event_show_animation_duration_ms") if kwargs.get("tap_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_show_animation_duration_ms
        self.tap_event_show_animation_width = kwargs.get("tap_event_show_animation_width") if kwargs.get("tap_event_show_animation_width") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_show_animation_width
        self.tap_event_show_animation_height = kwargs.get("tap_event_show_animation_height") if kwargs.get("tap_event_show_animation_height") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_show_animation_height
        self.tap_event_show_animation_background_color = kwargs.get("tap_event_show_animation_background_color") if kwargs.get("tap_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_show_animation_background_color
        # Tap event - play sound
        self.tap_event_play_sound_enabled = kwargs.get("tap_event_play_sound_enabled") if kwargs.get("tap_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_play_sound_enabled
        self.tap_event_play_sound_file_path = kwargs.get("tap_event_play_sound_file_path") if kwargs.get("tap_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_play_sound_file_path
        # Tap event - change stylesheet
        self.tap_event_change_stylesheet_enabled = kwargs.get("tap_event_change_stylesheet_enabled") if kwargs.get("tap_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_change_stylesheet_enabled
        self.tap_event_change_qss_stylesheet = kwargs.get("tap_event_change_qss_stylesheet") if kwargs.get("tap_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_change_qss_stylesheet
        self.tap_event_change_stylesheet_duration_ms = kwargs.get("tap_event_change_stylesheet_duration_ms") if kwargs.get("tap_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_change_stylesheet_duration_ms
        # Tap event - change size
        self.tap_event_change_size_enabled = kwargs.get("tap_event_change_size_enabled") if kwargs.get("tap_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_change_size_enabled
        self.tap_event_change_size_percent = kwargs.get("tap_event_change_size_percent") if kwargs.get("tap_event_change_size_percent") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_change_size_percent
        self.tap_event_change_size_duration_ms = kwargs.get("tap_event_change_size_duration_ms") if kwargs.get("tap_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_tap_event_change_size_duration_ms
        # Allow bypass enter event
        self.allow_bypass_enter_event = kwargs.get("allow_bypass_enter_event") if kwargs.get("allow_bypass_enter_event") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_allow_bypass_enter_event
        # Enter event - animation
        self.enter_event_show_animation_enabled = kwargs.get("enter_event_show_animation_enabled") if kwargs.get("enter_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_show_animation_enabled
        self.enter_event_show_animation_file_path = kwargs.get("enter_event_show_animation_file_path") if kwargs.get("enter_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_show_animation_file_path
        self.enter_event_show_animation_duration_ms = kwargs.get("enter_event_show_animation_duration_ms") if kwargs.get("enter_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_show_animation_duration_ms
        self.enter_event_show_animation_width = kwargs.get("enter_event_show_animation_width") if kwargs.get("enter_event_show_animation_width") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_show_animation_width
        self.enter_event_show_animation_height = kwargs.get("enter_event_show_animation_height") if kwargs.get("enter_event_show_animation_height") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_show_animation_height
        self.enter_event_show_animation_background_color = kwargs.get("enter_event_show_animation_background_color") if kwargs.get("enter_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_show_animation_background_color
        # Enter event - play sound
        self.enter_event_play_sound_enabled = kwargs.get("enter_event_play_sound_enabled") if kwargs.get("enter_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_play_sound_enabled
        self.enter_event_play_sound_file_path = kwargs.get("enter_event_play_sound_file_path") if kwargs.get("enter_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_play_sound_file_path
        # Enter event - change stylesheet
        self.enter_event_change_stylesheet_enabled = kwargs.get("enter_event_change_stylesheet_enabled") if kwargs.get("enter_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_change_stylesheet_enabled
        self.enter_event_change_qss_stylesheet = kwargs.get("enter_event_change_qss_stylesheet") if kwargs.get("enter_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_change_qss_stylesheet
        self.enter_event_change_stylesheet_duration_ms = kwargs.get("enter_event_change_stylesheet_duration_ms") if kwargs.get("enter_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_change_stylesheet_duration_ms
        # Enter event - change size
        self.enter_event_change_size_enabled = kwargs.get("enter_event_change_size_enabled") if kwargs.get("enter_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_change_size_enabled
        self.enter_event_change_size_percent = kwargs.get("enter_event_change_size_percent") if kwargs.get("enter_event_change_size_percent") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_change_size_percent
        self.enter_event_change_size_duration_ms = kwargs.get("enter_event_change_size_duration_ms") if kwargs.get("enter_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_enter_event_change_size_duration_ms
        # Allow bypass leave event
        self.allow_bypass_leave_event = kwargs.get("allow_bypass_leave_event") if kwargs.get("allow_bypass_leave_event") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_allow_bypass_leave_event
        # Leave event - animation
        self.leave_event_show_animation_enabled = kwargs.get("leave_event_show_animation_enabled") if kwargs.get("leave_event_show_animation_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_show_animation_enabled
        self.leave_event_show_animation_file_path = kwargs.get("leave_event_show_animation_file_path") if kwargs.get("leave_event_show_animation_file_path") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_show_animation_file_path
        self.leave_event_show_animation_duration_ms = kwargs.get("leave_event_show_animation_duration_ms") if kwargs.get("leave_event_show_animation_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_show_animation_duration_ms
        self.leave_event_show_animation_width = kwargs.get("leave_event_show_animation_width") if kwargs.get("leave_event_show_animation_width") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_show_animation_width
        self.leave_event_show_animation_height = kwargs.get("leave_event_show_animation_height") if kwargs.get("leave_event_show_animation_height") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_show_animation_height
        self.leave_event_show_animation_background_color = kwargs.get("leave_event_show_animation_background_color") if kwargs.get("leave_event_show_animation_background_color") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_show_animation_background_color
        # Leave event - play sound
        self.leave_event_play_sound_enabled = kwargs.get("leave_event_play_sound_enabled") if kwargs.get("leave_event_play_sound_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_play_sound_enabled
        self.leave_event_play_sound_file_path = kwargs.get("leave_event_play_sound_file_path") if kwargs.get("leave_event_play_sound_file_path") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_play_sound_file_path
        # Leave event - change stylesheet
        self.leave_event_change_stylesheet_enabled = kwargs.get("leave_event_change_stylesheet_enabled") if kwargs.get("leave_event_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_change_stylesheet_enabled
        self.leave_event_change_qss_stylesheet = kwargs.get("leave_event_change_qss_stylesheet") if kwargs.get("leave_event_change_qss_stylesheet") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_change_qss_stylesheet
        self.leave_event_change_stylesheet_duration_ms = kwargs.get("leave_event_change_stylesheet_duration_ms") if kwargs.get("leave_event_change_stylesheet_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_change_stylesheet_duration_ms
        # Leave event - change size
        self.leave_event_change_size_enabled = kwargs.get("leave_event_change_size_enabled") if kwargs.get("leave_event_change_size_enabled") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_change_size_enabled
        self.leave_event_change_size_percent = kwargs.get("leave_event_change_size_percent") if kwargs.get("leave_event_change_size_percent") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_change_size_percent
        self.leave_event_change_size_duration_ms = kwargs.get("leave_event_change_size_duration_ms") if kwargs.get("leave_event_change_size_duration_ms") is not None else self.global_widgets_properties.Widget_ActionFrame_Properties_leave_event_change_size_duration_ms


class Widget_ActionFrame(AbstractWidget):
    def __init__(self, actionframe_widget: QPushButton, main_win: QWidget = None, properties_setup: Widget_PushButton_Properties = None, timer_handler: TimerHandler = None) -> None:
        super().__init__(timer_handler=timer_handler)
        
        self.widget = actionframe_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_ActionFrame_Properties()
        if not isinstance(self.properties, Widget_ActionFrame_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_ActionFrame_Properties type not supported: #1\nUsed default properties.", type(self.widget))
            self.properties = Widget_ActionFrame_Properties()

        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

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
        if e and e.button() != Qt.LeftButton:
            if return_event_to_super:
                ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
                ReturnEvent.mousePressEvent(self.widget, e)
            return
        
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.tap_event_play_sound_enabled,
                                    e_file_path=self.properties.tap_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.tap_event_change_stylesheet_enabled,
                                            e_qss=self.properties.tap_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.tap_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.tap_event_show_animation_file_path)
        if self.properties.tap_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.tap_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.tap_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.tap_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.tap_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.mousePressEvent(self.widget, e)

    def EVENT_enter_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.enter_event_play_sound_enabled,
                                    e_file_path=self.properties.enter_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.enter_event_change_stylesheet_enabled,
                                            e_qss=self.properties.enter_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.enter_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.enter_event_show_animation_file_path)
        if self.properties.enter_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.enter_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.enter_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.enter_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.enter_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.enterEvent(self.widget, e)

    def EVENT_leave_event(self, e: QEvent, return_event_to_super = False):
        sound_ok = self._tap_event_play_sound(e,
                                    e_enabled=self.properties.leave_event_play_sound_enabled,
                                    e_file_path=self.properties.leave_event_play_sound_file_path
                                    )
        self._tap_event_change_stylesheet(e,
                                            e_enabled=self.properties.leave_event_change_stylesheet_enabled,
                                            e_qss=self.properties.leave_event_change_qss_stylesheet
                                            )
        self._tap_event_change_size(e,
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
            if self._animation_timer:
                self._animation_timer.set_duration(self.properties.leave_event_show_animation_duration_ms)
                self._animation_timer.start()
        elif start_animation is False:
            UTILS.TerminalUtility.WarningMessage("Invalid animation: #1", self.properties.leave_event_show_animation_file_path)
        if self.properties.leave_event_change_stylesheet_enabled:
            if self._stylesheet_timer:
                self._stylesheet_timer.set_duration(self.properties.leave_event_change_stylesheet_duration_ms)
                self._stylesheet_timer.start()
        if self.properties.leave_event_change_size_enabled:
            if self._size_timer:
                self._size_timer.set_duration(self.properties.leave_event_change_size_duration_ms)
                self._size_timer.start()
        if sound_ok is False:
            UTILS.TerminalUtility.WarningMessage("Invalid sound file: #1", self.properties.leave_event_play_sound_file_path)

        if return_event_to_super:
            ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
            ReturnEvent.leaveEvent(self.widget, e)


class Widget_Dialog_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:
        
        super().__init__()
        
        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties()

        # Drag Window
        self.window_drag_enabled = kwargs.get("window_drag_enabled") if kwargs.get("window_drag_enabled") is not None else self.global_widgets_properties.Widget_Dialog_Properties_window_drag_enabled
        self.window_drag_enabled_with_body = kwargs.get("window_drag_enabled_with_body") if kwargs.get("window_drag_enabled_with_body") is not None else self.global_widgets_properties.Widget_Dialog_Properties_window_drag_enabled_with_body
        self.window_drag_widgets = []
        self.allow_drag_widgets_cursor_change = kwargs.get("allow_drag_widgets_cursor_change") if kwargs.get("allow_drag_widgets_cursor_change") is not None else self.global_widgets_properties.Widget_Dialog_Properties_allow_drag_widgets_cursor_change
        self.start_drag_cursor = kwargs.get("start_drag_cursor") if kwargs.get("start_drag_cursor") is not None else self.global_widgets_properties.Widget_Dialog_Properties_start_drag_cursor
        self.end_drag_cursor = kwargs.get("end_drag_cursor") if kwargs.get("end_drag_cursor") is not None else self.global_widgets_properties.Widget_Dialog_Properties_end_drag_cursor
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_Dialog_Properties_cursor_keep_aspect_ratio
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_Dialog_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_Dialog_Properties_cursor_height
        # Mask label
        self.dragged_window_mask_label_enabled = kwargs.get("dragged_window_mask_label_enabled") if kwargs.get("dragged_window_mask_label_enabled") is not None else self.global_widgets_properties.Widget_Dialog_Properties_dragged_window_mask_label_enabled
        self.dragged_window_mask_label_stylesheet = kwargs.get("dragged_window_mask_label_stylesheet") if kwargs.get("dragged_window_mask_label_stylesheet") is not None else self.global_widgets_properties.Widget_Dialog_Properties_dragged_window_mask_label_stylesheet
        self.dragged_window_mask_label_image_path = kwargs.get("dragged_window_mask_label_image_path") if kwargs.get("dragged_window_mask_label_image_path") is not None else self.global_widgets_properties.Widget_Dialog_Properties_dragged_window_mask_label_image_path
        self.dragged_window_mask_label_animation_path = kwargs.get("dragged_window_mask_label_animation_path") if kwargs.get("dragged_window_mask_label_animation_path") is not None else self.global_widgets_properties.Widget_Dialog_Properties_dragged_window_mask_label_animation_path
        # Call Close_me on ESCAPE
        self.allow_bypass_key_press_event = kwargs.get("allow_bypass_key_press_event") if kwargs.get("allow_bypass_key_press_event") is not None else self.global_widgets_properties.Widget_Dialog_Properties_allow_bypass_key_press_event
        self.call_close_me_on_escape = kwargs.get("call_close_me_on_escape") if kwargs.get("call_close_me_on_escape") is not None else self.global_widgets_properties.Widget_Dialog_Properties_call_close_me_on_escape
        # Close on Lost Focus
        self.close_on_lost_focus = kwargs.get("close_on_lost_focus") if kwargs.get("close_on_lost_focus") is not None else self.global_widgets_properties.Widget_Dialog_Properties_close_on_lost_focus


class Widget_Dialog(AbstractWidget):
    def __init__(self, qdialog_widget: QDialog, main_win: QWidget = None, properties_setup: Widget_Dialog_Properties = None, timer_handler: TimerHandler = None) -> None:

        super().__init__(timer_handler=timer_handler)

        self.widget = qdialog_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_Dialog_Properties()
        if not isinstance(self.properties, Widget_Dialog_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_Dialog_Properties not supported: #1\nUsed default Widget_Dialog_Properties.", type(self.widget))
            self.properties = Widget_Dialog_Properties()
        
        self.SUPER_CLASS_WIDGET = self._get_qwidget_class()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

    def _setup_widget(self):
        if self.properties.window_drag_enabled:
            forbidden_widgets = []
            if not self.properties.window_drag_enabled_with_body:
                forbidden_widgets.append(self.main_win)

            self.enable_window_drag(self.properties.window_drag_widgets, data=None, forbidden_widgets=forbidden_widgets)
            self._set_drag_widgets_cursor()
        
        if self.properties.allow_bypass_key_press_event:
            self.widget.keyPressEvent = self.EVENT_key_press_event

        if self.properties.close_on_lost_focus:
            self.widget.installEventFilter(self.widget)
            self.widget.eventFilter = self.EVENT_event_filter

    def EVENT_key_press_event(self, e: QKeyEvent):
        if e.key() == Qt.Key_Escape:
            try:
                self.widget.close_me()
            except AttributeError:
                pass

        ReturnEvent.SUPER_CLASS_WIDGET = self.SUPER_CLASS_WIDGET
        ReturnEvent.keyPressEvent(self.widget, e)

    def EVENT_event_filter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            self.widget.close_me()
        
        return False


class Widget_Frame_Properties(AbstractProperties):
    def __init__(self,
                 global_widgets_properties: GlobalWidgetsProperties = None,
                 **kwargs) -> None:
        
        super().__init__()
        
        self.global_widgets_properties = global_widgets_properties if global_widgets_properties is not None else GlobalWidgetsProperties()

        # Drag Window
        self.window_drag_enabled = kwargs.get("window_drag_enabled") if kwargs.get("window_drag_enabled") is not None else self.global_widgets_properties.Widget_Frame_Properties_window_drag_enabled
        self.window_drag_enabled_with_body = kwargs.get("window_drag_enabled_with_body") if kwargs.get("window_drag_enabled_with_body") is not None else self.global_widgets_properties.Widget_Frame_Properties_window_drag_enabled_with_body
        self.window_drag_widgets = []
        self.allow_drag_widgets_cursor_change = kwargs.get("allow_drag_widgets_cursor_change") if kwargs.get("allow_drag_widgets_cursor_change") is not None else self.global_widgets_properties.Widget_Frame_Properties_allow_drag_widgets_cursor_change
        self.start_drag_cursor = kwargs.get("start_drag_cursor") if kwargs.get("start_drag_cursor") is not None else self.global_widgets_properties.Widget_Frame_Properties_start_drag_cursor
        self.end_drag_cursor = kwargs.get("end_drag_cursor") if kwargs.get("end_drag_cursor") is not None else self.global_widgets_properties.Widget_Frame_Properties_end_drag_cursor
        self.cursor_keep_aspect_ratio = kwargs.get("cursor_keep_aspect_ratio") if kwargs.get("cursor_keep_aspect_ratio") is not None else self.global_widgets_properties.Widget_Frame_Properties_cursor_keep_aspect_ratio
        self.cursor_width = kwargs.get("cursor_width") if kwargs.get("cursor_width") is not None else self.global_widgets_properties.Widget_Frame_Properties_cursor_width
        self.cursor_height = kwargs.get("cursor_height") if kwargs.get("cursor_height") is not None else self.global_widgets_properties.Widget_Frame_Properties_cursor_height
        # Change style and add mask label
        self.dragged_window_change_stylesheet_enabled = kwargs.get("dragged_window_change_stylesheet_enabled") if kwargs.get("dragged_window_change_stylesheet_enabled") is not None else self.global_widgets_properties.Widget_Frame_Properties_dragged_window_change_stylesheet_enabled
        self.dragged_window_stylesheet = kwargs.get("dragged_window_stylesheet") if kwargs.get("dragged_window_stylesheet") is not None else self.global_widgets_properties.Widget_Frame_Properties_dragged_window_stylesheet
        self.dragged_window_mask_label_enabled = kwargs.get("dragged_window_mask_label_enabled") if kwargs.get("dragged_window_mask_label_enabled") is not None else self.global_widgets_properties.Widget_Frame_Properties_dragged_window_mask_label_enabled
        self.dragged_window_mask_label_stylesheet = kwargs.get("dragged_window_mask_label_stylesheet") if kwargs.get("dragged_window_mask_label_stylesheet") is not None else self.global_widgets_properties.Widget_Frame_Properties_dragged_window_mask_label_stylesheet
        self.dragged_window_mask_label_image_path = kwargs.get("dragged_window_mask_label_image_path") if kwargs.get("dragged_window_mask_label_image_path") is not None else self.global_widgets_properties.Widget_Frame_Properties_dragged_window_mask_label_image_path
        self.dragged_window_mask_label_animation_path = kwargs.get("dragged_window_mask_label_animation_path") if kwargs.get("dragged_window_mask_label_animation_path") is not None else self.global_widgets_properties.Widget_Frame_Properties_dragged_window_mask_label_animation_path


class Widget_Frame(AbstractWidget):
    def __init__(self, qframe_widget: QDialog, main_win: QWidget = None, properties_setup: Widget_Frame_Properties = None, timer_handler: TimerHandler = None) -> None:

        super().__init__(timer_handler=timer_handler)

        self.widget = qframe_widget
        self.main_win = main_win if main_win is not None else self.widget
        self.properties = properties_setup if properties_setup is not None else Widget_Frame_Properties()
        if not isinstance(self.properties, Widget_Frame_Properties):
            UTILS.TerminalUtility.WarningMessage("Widget_Dialog_Properties not supported: #1\nUsed default Widget_Dialog_Properties.", type(self.widget))
            self.properties = Widget_Frame_Properties()

    def activate(self):
        if not self.is_active:
            self._setup_widget()
            self.is_active = True

    def _setup_widget(self):
        if self.properties.window_drag_enabled:
            forbidden_widgets = []
            if not self.properties.window_drag_enabled_with_body:
                forbidden_widgets.append(self.widget)

            self.enable_window_drag(self.properties.window_drag_widgets, data={"boundaries": "main_win"}, forbidden_widgets=forbidden_widgets)
            self._set_drag_widgets_cursor()


class CompatibleWidget:
    def EVENT_mouse_press_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_mouse_press_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)

    def EVENT_enter_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_enter_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)

    def EVENT_leave_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_leave_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)

    def EVENT_key_press_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_key_press_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)
    
    def EVENT_drag_widget_mouse_press_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_drag_widget_mouse_press_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)

    def EVENT_drag_widget_mouse_move_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_drag_widget_mouse_move_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)

    def EVENT_drag_widget_mouse_release_event(self, *args, **kwargs):
        UTILS.TerminalUtility.WarningMessage("EVENT_drag_widget_mouse_release_event: Widget not found.  Used: #1", "CompatibleWidget", print_only=True)


class WidgetHandler:
    def __init__(self, main_win: QWidget, global_widgets_properties: GlobalWidgetsProperties = None) -> None:
        """
        Method of use:
        Create a dictionary with settings for "Global Widgets Properties"
            my_setting_dict = {
                "Widget_Dialog_Properties" : {
                    "window_drag_enabled": True,
                    "allow_drag_widgets_cursor_change": False
                    ...
                },
                "Widget_PushButton_Properties": {
                    "allow_bypass_mouse_press_event": False
                    ...
                }
                ...
            }

        Create a Global Widgets Properties object:
            global_settings = GlobalWidgetsProperties(my_setting_dict)

        Create a WidgetHandler object and pass it "global_settings"
        widget_handler = WidgetHandler(global_settings)

        Add the desired widgets:
            widget_handler.add_QDialog(my_dialog)
            widget_handler.add_QPushButton(my_button)
            ...
        You can also add a widget of any type (eg QLabel) as a PushButton Widget:
            widget_handler.add_QPushButton(my_label)

        If you have processed an event such as mousePressEvent for a widget in your code, then you should prevent the
        added widget from connecting automatically to that event.
        This most often happens when you have a QLabel widget that you added as a QPushButton and for which you processed the mousePressEvent event.
        You can do this in several ways:
        1.) When adding a widget:
        widget_handler.add_QPushButton(my_button, widget_properties_dict={"allow_bypass_mouse_press_event": False})
        2.) If you have already added a widget:
            my_button_object = my_button_object = widget_handler.find_child(my_button)
            my_button_object.properties.allow_bypass_mouse_press_event = False

        When you have turned off the event from the settings, you will have to manually connect this event to the
        widget action by manually calling the action in your mousePressEvent event:
            def mousePressEvent(self, e: QMouseEvent) -> None:
                my_widget_object = widget_handler.find(my_widget)
                my_widget_object.EVENT_mouse_press_event(e, return_event_to_super=False)
                # Some of you...

        After you have added and configured all the desired widgets, call the "activate" method:
            widget_handler.activate()

        After activation, it is no longer possible to change the binding of widgets with events.
        To do this you have to remove the widget and add it again.
        You remove the widget using the "remove_child" method:
            widget_handler.remove_child(my_widget)
        """
        self.main_win = main_win

        self.timer_handler = TimerHandler(parent=self.main_win, interval=25)
        
        if global_widgets_properties is not None:
            if isinstance(global_widgets_properties, GlobalWidgetsProperties):
                self.global_widgets_properties = global_widgets_properties
            elif isinstance(global_widgets_properties, dict):
                self.global_widgets_properties = GlobalWidgetsProperties()
                self.global_widgets_properties.from_dict(global_widgets_properties)
            else:
                UTILS.TerminalUtility.WarningMessage("GlobalWidgetsProperties type not supported: #1\nUsing default GlobalWidgetsProperties.", type(global_widgets_properties))

        if self.global_widgets_properties is None:                
            self.global_widgets_properties = GlobalWidgetsProperties()

        self.__children = []

    def activate(self):
        for child in self.__children:
            child.activate()

    def add_child(self, widget: QWidget, widget_properties_dict: dict = None, force_widget_type: str = None, main_win: QWidget = None) -> object:
        """
        Adds a widget to the WidgetHandler.
        Please use widget-specific methods instead of this method:
            add_QDialog(widget) - adding a Dialog
            add_QPushButton(widget) - adding buttons
            add_ActionFrame(widget) - adding eg side menu bar widget
            add_QFrame(widget) - adding a QFrame widget with options inside the QDialog
        """

        if not main_win:
            main_win = self.main_win

        widget_obj = None

        widget_type = None
        if force_widget_type is not None:
            if force_widget_type.lower() == "actionframe":
                widget_type = "actionframe"
            elif force_widget_type.lower() == "qpushbutton":
                widget_type = "qpushbutton"
            elif force_widget_type.lower() == "qdialog":
                widget_type = "qdialog"
            elif force_widget_type.lower() == "qframe":
                widget_type = "qframe"
            elif force_widget_type.lower() == "qlineedit" or force_widget_type.lower() == "qtextedit" or force_widget_type.lower() == "textbox":
                widget_type = "textbox"
            elif force_widget_type.lower() == "selection":
                widget_type = "selection"
            elif force_widget_type.lower() == "item_based":
                widget_type = "item_based"
        
        if widget_type is None:
            if isinstance(widget, QPushButton) or isinstance(widget, QToolButton):
                widget_type = "qpushbutton"
            elif isinstance(widget, QDialog):
                widget_type = "qdialog"
            elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
                widget_type = "textbox"
            elif self._is_selection_widget(widget):
                widget_type = "selection"
            elif self._is_item_based_widget(widget):
                widget_type = "item_based"

        if widget_type == "actionframe":
            widget_default_properties_dict = Widget_ActionFrame_Properties(self.global_widgets_properties)
            widget_obj = Widget_ActionFrame(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        elif widget_type == "qpushbutton":
            widget_default_properties_dict = Widget_PushButton_Properties(self.global_widgets_properties)
            widget_obj = Widget_PushButton(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        elif widget_type == "qdialog":
            widget_default_properties_dict = Widget_Dialog_Properties(self.global_widgets_properties)
            widget_obj = Widget_Dialog(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        elif widget_type == "qframe":
            widget_default_properties_dict = Widget_Frame_Properties(self.global_widgets_properties)
            widget_obj = Widget_Frame(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        elif widget_type == "textbox":
            widget_default_properties_dict = Widget_TextBox_Properties(self.global_widgets_properties)
            widget_obj = Widget_TextBox(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        elif widget_type == "selection":
            widget_default_properties_dict = Widget_Selection_Properties(self.global_widgets_properties)
            widget_obj = Widget_Selection(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        elif widget_type == "item_based":
            widget_default_properties_dict = Widget_ItemBased_Properties(self.global_widgets_properties)
            widget_obj = Widget_ItemBased(widget, main_win, widget_default_properties_dict, timer_handler=self.timer_handler)
            widget_obj.update_from_dict(widget_properties_dict)
        
        if widget_obj is None:
            UTILS.TerminalUtility.WarningMessage("Widget type not supported: #1", type(widget))
            return None

        if widget not in [x.widget for x in self.__children]:
            self.__children.append(widget_obj)
            return widget_obj
        else:
            UTILS.TerminalUtility.WarningMessage("Widget already added: #1", str(widget))
            return False

    def _is_selection_widget(self, widget: QWidget) -> bool:
        if (isinstance(widget, QCheckBox)
            or isinstance(widget, QComboBox)
            or isinstance(widget, QRadioButton)
            or isinstance(widget, QSpinBox)):
            return True
        
        return False

    def _is_item_based_widget(self, widget: QWidget) -> bool:
        if (isinstance(widget, QListWidget)
            or isinstance(widget, QTableWidget)
            or isinstance(widget, QTreeWidget)):
            return True
        
        return False

    def add_QDialog(self, widget: QDialog, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_Dialog:
        return self.add_child(widget, widget_properties_dict, force_widget_type="qdialog", main_win=main_win)
    
    def add_QPushButton(self, widget: QPushButton, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_PushButton:
        return self.add_child(widget, widget_properties_dict, force_widget_type="qpushbutton", main_win=main_win)

    def add_Selection_Widget(self, widget: QWidget, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_Selection:
        return self.add_child(widget, widget_properties_dict, force_widget_type="selection", main_win=main_win)

    def add_ItemBased_Widget(self, widget: QWidget, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_ItemBased:
        return self.add_child(widget, widget_properties_dict, force_widget_type="item_based", main_win=main_win)

    def add_ActionFrame(self, widget: QWidget, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_ActionFrame:
        return self.add_child(widget, widget_properties_dict, force_widget_type="actionframe", main_win=main_win)

    def add_QFrame(self, widget: QFrame, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_Frame:
        if main_win is None:
            if self.main_win == widget:
                main_win = QDesktopWidget()
        return self.add_child(widget, widget_properties_dict, force_widget_type="qframe", main_win=main_win)

    def add_TextBox(self, widget: QWidget, widget_properties_dict: dict = None, main_win: QWidget = None) -> Widget_TextBox:
        return self.add_child(widget, widget_properties_dict, main_win=main_win, force_widget_type="textbox")

    def add_all_QPushButtons(self, widget_properties_dict: dict = None, deep_search: bool = True, starting_widget: QWidget = None) -> int:
        if starting_widget is None:
            starting_widget = self.main_win

        result = self._add_all_QPushButtons(start_widget=starting_widget, widget_properties_dict=widget_properties_dict, deep_search=deep_search)

        return result

    def add_all_Selection_Widgets(self, widget_properties_dict: dict = None, deep_search: bool = True, starting_widget: QWidget = None) -> int:
        if starting_widget is None:
            starting_widget = self.main_win

        result = self._add_all_Selection_Widgets(start_widget=starting_widget, widget_properties_dict=widget_properties_dict, deep_search=deep_search)

        return result

    def add_all_ItemBased_Widgets(self, widget_properties_dict: dict = None, deep_search: bool = True, starting_widget: QWidget = None) -> int:
        if starting_widget is None:
            starting_widget = self.main_win

        result = self._add_all_ItemBased_Widgets(start_widget=starting_widget, widget_properties_dict=widget_properties_dict, deep_search=deep_search)

        return result

    def _add_all_ItemBased_Widgets(self, start_widget: QWidget, widget_properties_dict: dict = None, deep_search: bool = True) -> int:
        count  = 0
        for child in start_widget.children():
            if isinstance(child, QDialog):
                continue

            if child.children() and deep_search:
                count += self._add_all_ItemBased_Widgets(child, widget_properties_dict, deep_search)

            if self._is_item_based_widget(child):
                if self.add_child(child, widget_properties_dict, force_widget_type="item_based"):
                    count += 1
            
        return count

    def _add_all_Selection_Widgets(self, start_widget: QWidget, widget_properties_dict: dict = None, deep_search: bool = True) -> int:
        count  = 0
        for child in start_widget.children():
            if isinstance(child, QDialog):
                continue

            if child.children() and deep_search:
                count += self._add_all_Selection_Widgets(child, widget_properties_dict, deep_search)

            if self._is_selection_widget(child):
                if self.add_child(child, widget_properties_dict, force_widget_type="selection"):
                    count += 1
            
        return count

    def _add_all_QPushButtons(self, start_widget: QWidget, widget_properties_dict: dict = None, deep_search: bool = True) -> int:
        count  = 0
        for child in start_widget.children():
            if isinstance(child, QDialog):
                continue

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

    def find_child(self, widget: QWidget, return_none_if_not_found: bool = False) -> CompatibleWidget:
        for child in self.__children:
            if child.widget == widget:
                return child
        
        if return_none_if_not_found:
            return None
        
        return CompatibleWidget

    def remove_child(self, widget: QWidget) -> bool:
        for child in self.__children:
            if child.widget == widget:
                child.close_me()
                self.__children.remove(child)
                return True
        
        return False

    def update_from_dict(self, properties_dict: dict, only_dedicated: bool = True) -> None:
        for child in self.__children:
            child.update_from_dict(properties_dict, only_dedicated)
        
    def close_me(self):
        for child in self.__children:
            child.close_me()
        
        if self.timer_handler:
            self.timer_handler.stop_all_timers()
            self.timer_handler.remove_all_timers()
            self.timer_handler.close_me()
            self.timer_handler = None
        # QCoreApplication.processEvents()
        self.__children = []






