from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QGridLayout, QWidget, 
                             QSizePolicy, QListWidget, QFileDialog, QDialog, QLabel, QListWidgetItem, 
                             QDesktopWidget, QLineEdit, QCalendarWidget, QHBoxLayout, QComboBox, 
                             QProgressBar, QCheckBox, QFileIconProvider, QTreeWidget, QTreeWidgetItem, 
                             QRadioButton, QGroupBox, QMessageBox)
from PyQt5.QtGui import (QIcon, QFont, QFontMetrics, QPixmap, QCursor, QImage, QClipboard, QColor, QCloseEvent)
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QObject, QCoreApplication, QRect,QPoint, QDate, QFileInfo, QMimeDatabase
from PyQt5 import uic, QtGui, QtCore


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
import shutil
import mimetypes
import json
import random
from cyrtranslit import to_latin
import platform
if platform.system().lower() == "windows":
    import winreg

from typing import Union, Any

import settings_cls
import db_media_cls
import db_record_cls
import db_record_data_cls
import db_definition_cls
import text_handler_cls
import definition_cls
import text_filter_cls
import db_tag_cls
import UTILS
import qwidgets_util_cls
import timer_cls
from obj_file import File
from obj_image import Image


class DialogsQueue():
    """
    Contains a list of all open dialogs (lists, menus, notifications...).
    When the user presses ESC, the last dialog in the list will be closed.
    If the user has opened a dialog and then that dialog loses focus, this class
    allows the user to close the dialog by pressing the ESC key.
    Each dialog must add itself to this class and provide a 'close_me' method
    so that this class can close it.
    opened_dialogs (list):
        [ dialog (obj), name (str) ]
    """
    
    def __init__(self):
        self.opened_dialogs = []

    def dialog_method_add_dialog(self, dialog: QDialog, name: str):
        if name is None:
            UTILS.TerminalUtility.WarningMessage("Invalid parameter #1 = None", ["name"], exception_raised=True)
            return None
        if dialog is None:
            UTILS.TerminalUtility.WarningMessage("Invalid parameter #1 = None", ["dialog"], exception_raised=True)
            return None
        
        self.opened_dialogs.append([dialog, name])
    
    def dialog_method_remove_dialog(self, name: str):
        if name is None:
            UTILS.TerminalUtility.WarningMessage("Invalid parameter #1 = None", ["name"], exception_raised=True)
            return None
        index_to_remove = None
        for idx, item in enumerate(self.opened_dialogs):
            if item[1] == name:
                index_to_remove = idx
                break
        if index_to_remove is None:
            return
        item = self.opened_dialogs.pop(index_to_remove)
        return item

    def remove_last(self) -> bool:
        if self.opened_dialogs:
            idx = self.opened_dialogs(len(self.opened_dialogs) - 1)
            self.opened_dialogs[idx][0].close_me()
            self.opened_dialogs.pop(idx)
            return True
        return False
            
    def remove_all(self) -> bool:
        if self.opened_dialogs:
            dialogs = []
            for i in self.opened_dialogs:
                dialogs.append(i[0])
            for item in dialogs:
                item.close_me()
            self.opened_dialogs = []
            dialogs = []
            return True
        return False

    def has_opened_context_menu(self) -> bool:
        dialogs = False
        if self.opened_dialogs:
            for i in self.opened_dialogs:
                if (isinstance(i[0], ContextMenu)):
                    dialogs = True
                    break
        return dialogs

    def remove_all_context_menu(self):
        if self.opened_dialogs:
            dialogs = []
            for i in self.opened_dialogs:
                if (    isinstance(i[0], ContextMenu) 
                        or isinstance(i[0], InputBoxSimple) 
                        or isinstance(i[0], Calendar)
                        or isinstance(i[0], MessageInformation)
                        # or isinstance(i[0], text_handler_cls.DefinitonHint)
                        or isinstance(i[0], definition_cls.SynonymManager)):
                    dialogs.append(i)

            for item in dialogs:
                self.dialog_method_remove_dialog(item[1])
                item[0].close_me()
            dialogs = []
            return True
        return False


class ContextMenuItem(QPushButton):
    def __init__(self, settings: settings_cls.Settings, parent_widget, button_id, button_name, button_description, button_icon, widget_handler: qwidgets_util_cls.WidgetHandler = None):
        super().__init__(parent_widget)
        self.setMouseTracking(True)
        self.parent_widget = parent_widget
        self.btn_id = button_id
        self.btn_name = button_name
        self.btn_desc = button_description
        self.btn_icon = button_icon
        self.widget_handler = widget_handler
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self._set_button_text()
        self._define_buttons_apperance(self, "context_menu_button")
        # Define click event
        self.clicked.connect(self.me_clicked)

    def me_clicked(self):
        self.parent_widget.context_menu_item_event(self.btn_id, "click", self)

    def enterEvent(self, a0: QtCore.QEvent) -> None:
        if self.widget_handler:
            widget_obj = self.widget_handler.find_child(self, return_none_if_not_found=True)
            if widget_obj:
                widget_obj.EVENT_enter_event(a0)

        self.parent_widget.context_menu_item_event(self.btn_id, "enter")
        try:
            return super().enterEvent(a0)
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("Error in #1 enterEvent.\nException:\n#2", ["ContextMenuItem",str(e)])

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if self.widget_handler:
            widget_obj = self.widget_handler.find_child(self, return_none_if_not_found=True)
            if widget_obj:
                widget_obj.EVENT_leave_event(a0)

        self.parent_widget.context_menu_item_event(self.btn_id, "leave")
        try:
            return super().leaveEvent(a0)
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("Error in #1 leaveEvent.\nException:\n#2", ["ContextMenuItem",str(e)])

    def _set_button_text(self):
        self.setText(self.btn_name)
        self.setToolTip(self.btn_desc)

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        font = btn.font()
        font.setFamily(self.getv(f"{name}_font_name"))
        font.setPointSize(self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setStyleSheet("")
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        btn.setEnabled(self.getv(f"{name}_enabled"))
        btn.setVisible(self.getv(f"{name}_visible"))
        # Icon setup
        if self.btn_icon:
            btn.setIcon(QIcon(self.btn_icon))
            icon_size = int(btn.contentsRect().height() * self.getv("context_menu_item_marked_icon_height") / 100)
        else:
            if self.getv(f"{name}_icon_path"):
                btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
            icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
        # Widget Handler
        if self.widget_handler:
            self.widget_handler.add_QPushButton(self, {"allow_bypass_enter_event": False, "allow_bypass_leave_event": False})


class ContextMenu(QDialog):
    """
    Displays the context menu.
    menu_dict:
        position
        selected (list): A list of item IDs that should be marked as selected.
        separator (list): The separator will be displayed after the item with the specified ID
        disabled (list): List of disabled items
        use_icon_for_selected (bool): 
        result: id
        items (list): [ id, name, description, clickable, subitems[], icon_path ]
    """
    
    def __init__(self, settings: settings_cls.Settings, parent_widget, menu_dict: dict = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.setLayout(QGridLayout(self))
        self.parent_widget = parent_widget
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        if menu_dict:
            self.menu_dict = menu_dict
            self.main_menu = False
        else:
            self.menu_dict = self.get_appv("menu")
            self.main_menu = True

        self.load_widgets_handler()

        self._populate_menu_dict()
        self.buttons_list = []
        self.child_menu = None

        self._define_context_menu_win_apperance()
        self.populate_menu()
        self.normalize_buttons()

        self.widget_handler.activate()
        
        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)
        
        # Register the menu name to avoid conflicts with other menus.
        if self.main_menu:
            self._stt.app_setting_add("menu_id", self.my_name)
        
        for item in self.buttons_list:
            self.btn_icon_resize(item[0], item[0].btn_icon, item[0].btn_id)

        self.move_menu_to_appropriate_position()

        self.show()

        self.move_menu_to_appropriate_position()

        if self.main_menu:
            UTILS.LogHandler.add_log_record("#1: Menu displayed.", ["ContextMenu"], extract_to_variables=["menu_dict", self.menu_dict])

        if self.main_menu:
            self.exec_()
            if self.my_name != self.get_appv("menu_id"):
                self.get_appv("menu")["result"] = None

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog

        # Add frames

        # Add all Pushbuttons

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets

        # self.widget_handler.activate()

    def _populate_menu_dict(self):
        # Add icon_path field to items list if not exist
        for idx, item in enumerate(self.menu_dict["items"]):
            if len(item) == 5:
                self.menu_dict["items"][idx].append(None)
        
        # Define default values if value does not exist
        if "position" not in self.menu_dict:
            self.menu_dict["position"] = None

        if "result" not in self.menu_dict:
            self.menu_dict["result"] = None

        if "use_icon_for_selected" not in self.menu_dict:
            self.menu_dict["use_icon_for_selected"] = True

        if "separator" not in self.menu_dict:
            self.menu_dict["separator"] = []
        elif self.menu_dict["separator"] is None:
            self.menu_dict["separator"] = []

        if "disabled" not in self.menu_dict:
            self.menu_dict["disabled"] = []
        elif self.menu_dict["disabled"] is None:
            self.menu_dict["disabled"] = []

        if "selected" not in self.menu_dict:
            self.menu_dict["selected"] = []
        else:
            if isinstance(self.menu_dict["selected"], str):
                self.menu_dict["selected"] = [self.menu_dict["selected"]]
            elif self.menu_dict["selected"] is None:
                self.menu_dict["selected"] = []
            # Add selected prefix to item that are marked as selected
            for idx, item in enumerate(self.menu_dict["items"]):
                if item[0] in self.menu_dict["selected"]:
                    if self.menu_dict["use_icon_for_selected"]:
                        self.menu_dict["items"][idx][5] = self.getv("context_menu_item_marked_icon_path")
                    else:
                        if self.getv("context_menu_item_marked_prefix_enabled"):
                            item_text = self.menu_dict["items"][idx][1]
                            if item_text[:len(self.getv("context_menu_item_marked_prefix"))] != self.getv("context_menu_item_marked_prefix"):
                                self.menu_dict["items"][idx][1] = self.getv("context_menu_item_marked_prefix") + item_text
        for idx, item in enumerate(self.menu_dict["items"]):
            if not item[5]:
                self.menu_dict["items"][idx][5] = self.getv("context_menu_button_icon_path")

    def normalize_buttons(self):
        submenu_string = " ...>"
        if self.buttons_list:
            fm = QFontMetrics(self.buttons_list[0][0].font())
            # for item in self.menu_dict["items"]:
            #     if item[4]:
            #         has_subitems = True
            #         break
            # else:
            #     has_subitems = False
            
            # if has_subitems:
            max_width = 0
            for button_item in self.buttons_list:
                if fm.width(button_item[0].text() + submenu_string) > max_width:
                    max_width = fm.width(button_item[0].text() + submenu_string)

            buttons_text = []
            for button_item in self.menu_dict["items"]:
                if button_item[4]:
                    buttons_text.append([button_item[1], True])
                else:
                    buttons_text.append([button_item[1], False])

            for idx, button in enumerate(buttons_text):
                num_of_spaces = 0
                button_width = 0
                while button_width < max_width:
                    num_of_spaces += 1
                    if button[1]:
                        button_width = fm.width(button[0] + " "*num_of_spaces + submenu_string)
                    else:
                        button_width = fm.width(button[0] + " "*num_of_spaces)
                if button[1]:
                    self.buttons_list[idx][0].setText(button[0] + " "*(num_of_spaces-1) + submenu_string[1:])
                else:
                    self.buttons_list[idx][0].setText(button[0] + " "*(num_of_spaces-1))

    def move_menu_to_appropriate_position(self):
        glob_x = QDesktopWidget().availableGeometry().x()
        glob_y = QDesktopWidget().availableGeometry().y()
        glob_w = QDesktopWidget().availableGeometry().width()
        glob_h = QDesktopWidget().availableGeometry().height()
        
        if self.menu_dict["position"]:
            position = self.menu_dict["position"]
            if isinstance(position, str):
                x, y = position.split(",")
                x = int(x)
                y = int(y)
            else:
                x = position.x()
                y = position.y()

            # Check if position is within the screen
            if (x > (glob_x + glob_w - self.width())):
                x = x - self.width() - 2
            if (y > (glob_y + glob_h - self.height())):
                y = glob_y + glob_h - self.height()
             
            if x < 0:
                x = 0
            if y < 0:
                y = 0

            self.move(x + 1, y + 1)

    def close_me(self):
        # Unbind button leave and enter events
        for btn in self.buttons_list:
            menu_item: QPushButton = btn[0]
            if self.widget_handler:
                self.widget_handler.remove_child(menu_item)

            menu_item.enterEvent = None
            menu_item.leaveEvent = None

        # Unregister dialog
        if self.child_menu:
            self.child_menu.close()
        self.dialog_queue.dialog_method_remove_dialog(self.my_name)

        # Delete dialog
        if self.main_menu:
            UTILS.LogHandler.add_log_record("#1: Menu closed.", ["ContextMenu"])
            UTILS.DialogUtility.on_closeEvent(self)

    def populate_menu(self):
        counter = 0
        for item in self.menu_dict["items"]:
            menu_item = ContextMenuItem(self._stt, self, item[0], item[1], item[2], item[5], widget_handler=self.widget_handler)
            self.buttons_list.append([menu_item, item[3]])
            if item[0] in self.menu_dict["disabled"]:
                menu_item.setDisabled(True)
            self.layout().addWidget(menu_item, counter, 0)
            counter += 1
            if item[0] in self.menu_dict["separator"]:
                self.layout().addWidget(self.separator_item(), counter, 0)
                counter += 1
    
    def btn_icon_resize(self, btn: QPushButton, btn_id, btn_icon):
        if btn_icon:
            if btn_id in self.menu_dict["selected"]:
                icon_size = int(btn.contentsRect().height() * self.getv("context_menu_item_marked_icon_height") / 100)
            else:
                icon_size = int(btn.contentsRect().height() * self.getv("context_menu_button_icon_height") / 100)
            btn.setIconSize(QSize(icon_size, icon_size))
    
    def separator_item(self) -> QFrame:
        sep = QFrame(self)
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet(self.getv("context_menu_separator_stylesheet"))
        size = self.getv("context_menu_separator_size") + 2
        sep.setFixedHeight(size)
        return sep

    def leaveEvent(self, a0: QtCore.QEvent) -> None:
        if not self.child_menu:
            if not self.main_menu:
                self.close()
        return super().leaveEvent(a0)

    def context_menu_item_event(self, btn_id, event, item_obj: ContextMenuItem = None):
        if event == "click":
            btn_info = self._get_button_info(btn_id)
            if btn_info[3]:
                self.get_appv("menu")["result"] = btn_id
                self.close_submenu()
                self.sub_item_is_selected()
                UTILS.LogHandler.add_log_record("#1: User click on (#2) #3.", ["ContextMenu", item_obj.btn_id, item_obj.btn_name])
            else:
                UTILS.LogHandler.add_log_record("#1: User click #3 button: (#3) #4.", ["ContextMenu", "NonSelectable", item_obj.btn_id, item_obj.btn_name])
        if event == "enter":
            btn_info = self._get_button_info(btn_id)
            sub_items = btn_info[4]
            if self.child_menu:
                self.child_menu.close()
            if sub_items:
                new_dict = {"result": None}
                for button in self.buttons_list:
                    if button[0].btn_id == btn_info[0]:
                        glob_position = self.mapToGlobal(button[0].pos())
                        x = glob_position.x() + button[0].width()
                        y = glob_position.y()
                        new_dict["position"] = f"{x},{y}"
                        new_dict["rect"] = button[0].rect()
                        break
                new_dict["items"] = sub_items
                new_dict["selected"] = self.menu_dict["selected"]
                new_dict["separator"] = self.menu_dict["separator"]
                new_dict["disabled"] = self.menu_dict["disabled"]
                new_dict["use_icon_for_selected"] = self.menu_dict["use_icon_for_selected"]
                self.child_menu = ContextMenu(self._stt, self, new_dict)
                if new_dict["result"]:
                    self.menu_dict["result"] = new_dict["result"]
                    self.close()

    def sub_item_is_selected(self):
        if self.main_menu:
            self.close()
        else:
            self.parent_widget.sub_item_is_selected()

    def close_submenu(self):
        if self.child_menu:
            self.child_menu.close_submenu()
            if not self.main_menu:
                self.close()

    def _get_button_info(self, btn_id: int) -> list:
        for item in self.menu_dict["items"]:
            if item[0] == btn_id:
                return item
        return None
    
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def _define_context_menu_win_apperance(self):
        self.setStyleSheet(self.getv("context_menu_win_stylesheet"))
        self._set_margins(self.layout(), "context_menu_win")
        self._set_margins(self.layout(), "context_menu_win_layout")
        self.layout().setSpacing(self.getv("context_menu_win_layout_spacing"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        if not self.getv("context_menu_win_show_titlebar"):
            self.setWindowFlag(Qt.FramelessWindowHint)
        if self.getv("context_menu_win_width"):
            self.setFixedWidth(self.getv("context_menu_win_width"))
        if self.getv("context_menu_win_height"):
            self.setFixedHeight(self.getv("context_menu_win_height"))

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])


class InputBoxSimple(QDialog):
    """
    This class displays an input dialog and allows the user to enter some text.
    input_dict: (dict)
        id (int): ID like record_id
        name (str): The name that will be used to retrieve settings information
        input_hint (str): PlaceHolder text displayed in the input box
        title (str): Headline
        text (str): The text displayed in the input box
        description (str): The description shown below the input box
        result (str): The text that will be returned as a result
        position (str,QPoint): Optional
        user_definded_position (bool): Default=False
        size (str,QRect): Optional
        user_definded_size (bool): Default=True
        one_line (bool): Default=True, One line text (QLineEdit), if false (QTextEdit)
        calendar_on_double_click (bool): Def=False
        auto_show_calendar (bool): False
        auto_apply_calendar (bool): False
    """
    def __init__(self, settings: settings_cls.Settings, parent_widget, input_dict: dict = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.setMouseTracking(True)
        self.setLayout(QGridLayout(self))
        self.drag_mode = None
        self.parent_widget = parent_widget
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.input_dict = input_dict
        self.has_calendar = False

        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)

        self._define_input_dict()
        self._define_widgets()
        self._define_widgets_apperance()
        self._set_window_geometry()

        self.load_widgets_handler()
        
        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        if self.input_dict["one_line"]:
            self.txt_box.returnPressed.connect(self._txt_box_return_press)
        else:
            self.btn_ok.clicked.connect(self._btn_ok_click)
        self.txt_box.mouseMoveEvent = self._txt_box_mouse_move
        self.btn_resize.leaveEvent = self._btn_resize_leave_event
        self.btn_resize.mousePressEvent = self._btn_resize_mouse_press
        self.btn_resize.mouseReleaseEvent = self._btn_resize_mouse_release
        self.btn_resize.mouseMoveEvent = self._btn_resize_mouse_move
        self.txt_box.mouseDoubleClickEvent = self.txt_box_mouse_double_click
        self.txt_box.textChanged.connect(self._txt_box_text_changed)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["InputBoxSimple"], extract_to_variables=["input_dict", self.input_dict])
        if self.input_dict.get("auto_show_calendar"):
            if not self._insert_calendar_result():
                self.exec_()
        else:
            self.exec_()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.close()
            return
        return super().keyPressEvent(a0)

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        if self.input_dict["description"]:
            handle_dialog.add_window_drag_widgets(self.lbl_description)
        if self.input_dict["title"]:
            handle_dialog.add_window_drag_widgets(self.lbl_title)
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_box)

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def _txt_box_text_changed(self):
        if not self.input_dict.get("validator", None):
            return
        
        if self.input_dict["one_line"]:
            text = self.txt_box.text().lower()
        else:
            text = self.txt_box.toPlainText().lower()
        
        is_valid = False

        for item in self.input_dict["validator"].get("included", []):
            if item == text:
                is_valid = True
                break
        
        if not is_valid and self.input_dict["validator"].get("included", []):
            self._set_stylesheet_to_invalid()
            return

        is_valid = True

        for item in self.input_dict["validator"].get("excluded", []):
            if item == text:
                is_valid = False
                break
        
        if not is_valid:
            self._set_stylesheet_to_invalid()
            return

        if self.input_dict["one_line"]:
            self.txt_box.setStyleSheet(self.getv("block_input_box_name_one_line_stylesheet"))
        else:
            self.txt_box.setStyleSheet(self.getv(self.input_dict["name"] + "_stylesheet"))

    def _set_stylesheet_to_invalid(self):
        if self.input_dict["one_line"]:
            self.txt_box.setStyleSheet(self.getv("input_box_txt_box_invalid_entry_one_line_stylesheet"))
        else:
            self.txt_box.setStyleSheet(self.getv("input_box_txt_box_invalid_entry_stylesheet"))

    def txt_box_mouse_double_click(self, x):
        if self.input_dict["calendar_on_double_click"]:
            self._insert_calendar_result()

    def _insert_calendar_result(self) -> bool:
        if self.has_calendar:
            return False
        else:
            self.has_calendar = True
            cal_dict = {
                "name": "calendar",
                "result": None,
                "position": QCursor.pos()
                
            }
            self.txt_box.selectAll()
            Calendar(self._stt, self, cal_dict)
            if cal_dict["result"]:
                if self.input_dict.get("auto_apply_calendar"):
                    self.txt_box.clear()
                if self.input_dict["one_line"]:
                    self.txt_box.insert(cal_dict["result"])
                else:
                    self.txt_box.insertPlainText(cal_dict["result"])
                if self.input_dict.get("auto_apply_calendar"):
                    self._save_and_exit()
                self.has_calendar = False
                return True
                    
            self.has_calendar = False
            return False

    def _btn_resize_mouse_move(self, event):
        if self.input_dict["one_line"]:
            if self.drag_mode:
                self.drag_mode = [
                    self.pos().x(),
                    self.pos().y(),
                    QCursor.pos().x(),
                    QCursor.pos().y() ]
                w = self.drag_mode[2] - self.drag_mode[0]
                if w < 200:
                    w = 200
                self.resize(w, self.sizeHint().height())
        else:
            if self.drag_mode:
                self.drag_mode = [
                    # self.mapFromGlobal(self.pos()).x(),
                    # self.mapFromGlobal(self.pos()).y(),
                    self.pos().x(),
                    self.pos().y(),
                    QCursor.pos().x(),
                    QCursor.pos().y() ]
                w = self.drag_mode[2] - self.drag_mode[0]
                h = self.drag_mode[3] - self.drag_mode[1]
                if w < 200:
                    w = 200
                if h < 100:
                    h = 100
                self.resize(w, h)

    def _btn_resize_mouse_press(self, event):
        self.drag_mode = [
            self.pos().x(),
            self.pos().y(),
            QCursor.pos().x(),
            QCursor.pos().y() ]
        
    def _btn_resize_mouse_release(self, event):
        self.drag_mode = None

    def _txt_box_mouse_move(self, event):
        if self.input_dict["one_line"]:
            if event.localPos().x() in range(self.width() - self.btn_resize.width(), self.width()):
                self.btn_resize.setVisible(True)
        else:
            if event.localPos().x() in range(self.width() - self.btn_resize.width(), self.width()):
                if event.localPos().y() in range(self.height() - self.btn_resize.height(), self.height()):
                    self.btn_resize.setVisible(True)
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.input_dict["one_line"]:
            if event.localPos().x() in range(self.width() - self.btn_resize.width(), self.width()):
                if event.localPos().y() in range(self.height() - self.btn_resize.height(), self.height()):
                    self.btn_resize.setVisible(True)
        return super().mouseMoveEvent(event)

    def _btn_resize_leave_event(self, x):
        self.drag_mode = None
        self.btn_resize.setVisible(False)

    def _btn_ok_click(self):
        self._save_and_exit()

    def _txt_box_return_press(self):
        self._save_and_exit()

    def _save_and_exit(self):
        if self.input_dict["one_line"]:
            self.input_dict["result"] = self.txt_box.text()
            UTILS.LogHandler.add_log_record("#1: User confirmed entry.\nEntry: #2", ["InputBoxSimple", self.txt_box.text()])
        else:
            self.input_dict["result"] = self.txt_box.toPlainText()
            UTILS.LogHandler.add_log_record("#1: User confirmed entry.\nEntry: #2", ["InputBoxSimple", self.txt_box.toPlainText()])
        self.close()

    def _set_window_geometry(self):
        name = self.input_dict["name"]
        # Set Position
        x = None
        y = None
        if isinstance(self.input_dict["position"], str):
            pos_point = self._parse_position(self.input_dict["position"])
            x = pos_point[0]
            y = pos_point[1]
        elif isinstance(self.input_dict["position"], QPoint):
            x = self.input_dict["position"].x()
            y = self.input_dict["position"].y()
        # Set Size
        w = None
        h = None
        if self.input_dict["user_definded_size"]:
            if name in self._stt.app_setting_get_list_of_keys():
                user_size_string = self.get_appv(name)["size"]
                user_size = self._parse_position(user_size_string)
                w = user_size[0]
                h = user_size[1]
        if w is None or h is None:
            if isinstance(self.input_dict["size"], str):
                size_point = self._parse_position(self.input_dict["size"])
                w = size_point[0]
                h = size_point[1]
            elif isinstance(self.input_dict["size"], QRect):
                w = self.input_dict["size"].width()
                h = self.input_dict["size"].height()
        # Set Win Geometry
        if x is not None and y is not None:
            if x >=0 and y >=0:
                self.move(x, y)
        if w is not None and h is not None:
            if self.input_dict["one_line"]:
                self.resize(w, self.height())
            else:
                self.resize(w, h)

    def _parse_position(self, pos_string: str) -> tuple:
        pos_string = pos_string.strip("(")
        pos_string = pos_string.strip(")")
        pos_list = pos_string.split(",")
        if len(pos_list) == 2:
            x = int(pos_list[0])
            y = int(pos_list[1])
        else:
            return None
        return (x, y)

    def _define_input_dict(self):
        if "input_hint" not in self.input_dict:
            self.input_dict["input_hint"] = self.getl("input_box_placeholder")
        if "title" not in self.input_dict:
            self.input_dict["title"] = None
        if "description" not in self.input_dict:
            self.input_dict["description"] = None
        if "result" not in self.input_dict:
            self.input_dict["result"] = None
        if "position" not in self.input_dict:
            self.input_dict["position"] = None
        if "size" not in self.input_dict:
            self.input_dict["size"] = None
        if "user_definded_position" not in self.input_dict:
            self.input_dict["user_definded_position"] = False
        if "user_definded_size" not in self.input_dict:
            self.input_dict["user_definded_size"] = True
        if "one_line" not in self.input_dict:
            self.input_dict["one_line"] = True
        if "text" not in self.input_dict:
            self.input_dict["text"] = ""
        if "calendar_on_double_click" not in self.input_dict:
            self.input_dict["calendar_on_double_click"] = False

    def close_me(self):
        # Save user setting for position and size
        name = self.input_dict["name"]
        if name not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add(name, {}, save_to_file=True)
        self.get_appv(name)["position"] = f"{self.pos().x()},{self.pos().y()}"
        self.get_appv(name)["size"] = f"{self.width()},{self.height()}"
        # Unregister Dialog
        self.dialog_queue.dialog_method_remove_dialog(self.my_name)

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["InputBoxSimple"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _define_widgets(self):
        grid_count = 0
        # Title
        if self.input_dict["title"]:
            self.lbl_title: QLabel = QLabel(self)
            self.lbl_title.setText(self.input_dict["title"])
            self.lbl_title.setAlignment(Qt.AlignHCenter)
            self.layout().addWidget(self.lbl_title, grid_count, 0, 1, 2)
            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.lbl_title.setSizePolicy(size_policy)
            grid_count += 1
        # TxtBox
        if self.input_dict["one_line"]:
            self.txt_box: QLineEdit = QLineEdit(self)
            self.layout().addWidget(self.txt_box, grid_count, 0)
        else:
            self.txt_box: QTextEdit = QTextEdit(self)
            self.layout().addWidget(self.txt_box, grid_count, 0, 1, 2)
        self.txt_box.setText(self.input_dict["text"])
        self.txt_box.selectAll()
        if self.input_dict["input_hint"]:
            self.txt_box.setPlaceholderText(self.input_dict["input_hint"])
        grid_count += 1
        # Description
        if self.input_dict["description"]:
            self.lbl_description: QLabel = QLabel(self)
            self.lbl_description.setWordWrap(True)
            self.lbl_description.setText(self.input_dict["description"])
            self.lbl_description.setScaledContents(True)
            self.layout().addWidget(self.lbl_description, grid_count, 0, 1, 2)
            grid_count += 1
        # OK Button
        if not self.input_dict["one_line"]:
            self.btn_ok: QPushButton = QPushButton(self)
            self.layout().addWidget(self.btn_ok, grid_count, 0, Qt.AlignLeft)
        # Resize Button
        self.btn_resize: QPushButton = QPushButton(self)
        if self.input_dict["one_line"]:
            if self.input_dict["title"]:
                self.layout().addWidget(self.btn_resize, 1, 1, Qt.AlignRight)
            else:
                self.layout().addWidget(self.btn_resize, 0, 1, Qt.AlignRight)
        else:

            self.layout().addWidget(self.btn_resize, grid_count, 1, Qt.AlignRight)
        grid_count += 1

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["InputBoxSimple"])
        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        self._define_input_box_win_apperance()
        if self.input_dict["one_line"]:
            self._txt_box_apperance(self.txt_box, self.input_dict["name"], no_stylesheet=True)
            self.txt_box.setStyleSheet(self.getv("block_input_box_name_one_line_stylesheet"))
        else:
            self._txt_box_apperance(self.txt_box, self.input_dict["name"])

        if self.input_dict["title"]:
            self._define_labels_apperance(self.lbl_title, self.input_dict["name"] + "_title")
        if self.input_dict["description"]:
            self._define_labels_apperance(self.lbl_description, self.input_dict["name"] + "_description")
        if self.input_dict["one_line"]:
            self.btn_resize.setFixedSize(self.txt_box.height(), self.txt_box.height())
        else:
            self.btn_resize.setFixedSize(self.btn_ok.height(), self.btn_ok.height())
        if self.input_dict["one_line"]:
            self._define_buttons_apperance(self.btn_resize, "input_box_btn_resize", "_one_line")
        else:
            self._define_buttons_apperance(self.btn_resize, "input_box_btn_resize", "_multi_line")
        self.btn_resize.setVisible(False)
        self.btn_resize.setToolTip(self.getl("input_box_btn_resize_tt"))
        if not self.input_dict["one_line"]:
            self._define_buttons_apperance(self.btn_ok, "input_box_btn_ok", "")
            self.btn_ok.setText(self.getl("input_box_btn_ok_text"))
            self.btn_ok.setToolTip(self.getl("input_box_btn_ok_tt"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str, extra_icon, no_stylesheet: bool = False):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}{extra_icon}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}{extra_icon}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        if not no_stylesheet:
            btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))

    def _define_input_box_win_apperance(self):
        name = self.input_dict["name"]
        self.setStyleSheet(self.getv(f"{name}_win_stylesheet"))
        self._set_margins(self.layout(), f"{name}_win")
        self._set_margins(self.layout(), f"{name}_win_layout")
        self.layout().setSpacing(self.getv(f"{name}_win_layout_spacing"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        if not self.getv(f"{name}_win_show_titlebar"):
            self.setWindowFlag(Qt.FramelessWindowHint)

    def _txt_box_apperance(self, txt_box, name: str, no_stylesheet: bool = False):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setLineWrapMode(self.getv(f"{name}_line_wrap_mode"))
            txt_box.setAcceptRichText(self.getv(f"{name}_accept_rich_text"))
            txt_box.setCursorWidth(self.getv(f"{name}_cursor_width"))

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        if not no_stylesheet:
            txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)


class Calendar(QDialog):
    """
    Displays a calendar and allows the user to select a date.
    calendar_dict:
        name (str): Def=calendar , For saving setting
        position (x,y): Def: User Defined
        size (w,h): Def: User Defined
        date (str): date preselected
        show_buttons (bool): Def=False shows SELECT and CANCEL buttons
        show_date_info (bool): Def=True It shows the selected date in long form below the calendar
        result (str): Date selected by user
    """
    def __init__(self, settings: settings_cls.Settings, parent_widget, calendar_dict: dict = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.setLayout(QGridLayout(self))
        self.parent_widget = parent_widget
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.calendar_dict = calendar_dict
        self._populate_calendar_dictionary()

        self._define_widgets()
        self._define_widgets_apperance()
        self._set_window_geometry()
        self.cal_selection_changed()

        self.load_widgets_handler()

        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.cal.selectionChanged.connect(self.cal_selection_changed)
        self.cal.activated.connect(self.cal_date_activated)
        if self.calendar_dict["show_buttons"]:
            self.btn_cancel.clicked.connect(self.btn_cancel_click)
            self.btn_select.clicked.connect(self.btn_select_click)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["Calendar"], extract_to_variables=["calendar_dict", self.calendar_dict])
        QCoreApplication.processEvents()
        self.exec_()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.btn_cancel_click()
            return
        return super().keyPressEvent(a0)

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog

        # Add frames
        handle_dialog = self.widget_handler.add_QFrame(self)
        handle_dialog.add_window_drag_widgets(self)
        handle_dialog.properties.window_drag_enabled_with_body = True
        if self.calendar_dict["show_date_info"]:
            handle_dialog.add_window_drag_widgets(self.lbl_info)

        # Add all Pushbuttons
        if self.calendar_dict["show_buttons"]:
            self.widget_handler.add_QPushButton(self.btn_select)
            self.widget_handler.add_QPushButton(self.btn_cancel)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def btn_select_click(self):
        self.cal_date_activated(self.cal.selectedDate())

    def btn_cancel_click(self):
        UTILS.LogHandler.add_log_record("#1: User canceled date selection.", ["InputBoxSimple"])
        self.close()

    def _populate_calendar_dictionary(self):
        if "name" not in self.calendar_dict:
            self.calendar_dict["name"] = "calendar"
        if "date" not in self.calendar_dict:
            dt = DateTime(self._stt)
            self.calendar_dict["date"] = dt.make_date_dict()["date"]
        if "show_buttons" not in self.calendar_dict:
            self.calendar_dict["show_buttons"] = True
        if "show_date_info" not in self.calendar_dict:
            self.calendar_dict["show_date_info"] = True
        if "position" not in self.calendar_dict:
            self.calendar_dict["position"] = None
        if "size" not in self.calendar_dict:
            self.calendar_dict["size"] = None
        if "result" not in self.calendar_dict:
            self.calendar_dict["result"] = None

    def cal_date_activated(self, date: QDate):
        dt = DateTime(self._stt)
        date_dict = dt.make_date_dict(date)
        self.calendar_dict["result"] = date_dict["date"]
        UTILS.LogHandler.add_log_record("#1: User selected date. (#2)", ["Calendar", date_dict["date"]])
        # QCoreApplication.processEvents()
        self.close()

    def cal_selection_changed(self):
        if self.cal.selectedDate():
            self._show_date_in_lbl_info(self.cal.selectedDate())

    def _show_date_in_lbl_info(self, date: QDate) -> None:
        if self.calendar_dict["show_date_info"] and date is not None:
            dt = DateTime(self._stt)
            date_dict = dt.make_date_dict(date)
            date = f'{date_dict["day_name"]}, {date_dict["day"]}, {date_dict["month_name"]}, {date_dict["year"]}.'
            self.lbl_info.setText(date)

    def _set_window_geometry(self):
        name = self.calendar_dict["name"]
        # Set Position
        x = None
        y = None
        if self.calendar_dict["position"]:
            if isinstance(self.calendar_dict["position"], str):
                pos_point = self._parse_position(self.calendar_dict["position"])
                x = pos_point[0]
                y = pos_point[1]
            elif isinstance(self.calendar_dict["position"], QPoint):
                x = self.calendar_dict["position"].x()
                y = self.calendar_dict["position"].y()
        else:
            if name in self._stt.app_setting_get_list_of_keys():
                pos_point = self._parse_position(self.get_appv(name)["position"])
                x = pos_point[0]
                y = pos_point[1]
        # Set Size
        w = None
        h = None
        if self.calendar_dict["size"]:
            if isinstance(self.calendar_dict["size"], str):
                size_point = self._parse_position(self.calendar_dict["size"])
                w = size_point[0]
                h = size_point[1]
            elif isinstance(self.calendar_dict["size"], QRect):
                w = self.calendar_dict["size"].width()
                h = self.calendar_dict["size"].height()
        else:
            if name in self._stt.app_setting_get_list_of_keys():
                user_size_string = self.get_appv(name)["size"]
                user_size = self._parse_position(user_size_string)
                w = user_size[0]
                h = user_size[1]
        # Set Win Geometry
        if x is not None and y is not None:
            if x >=0 and y >=0:
                self.move(x, y)
        if w is not None and h is not None:
            self.resize(w, h)

    def _parse_position(self, pos_string: str) -> tuple:
        pos_string = pos_string.strip("(")
        pos_string = pos_string.strip(")")
        pos_list = pos_string.split(",")
        if len(pos_list) == 2:
            x = int(pos_list[0])
            y = int(pos_list[1])
        else:
            return None
        return (x, y)

    def _define_widgets(self):
        grid_count = 0
        if self.calendar_dict["show_buttons"]:
            if self.calendar_dict["show_date_info"]:
                row = 2
            else:
                row = 1
            self.btn_select: QPushButton = QPushButton(self)
            self.layout().addWidget(self.btn_select, row, 0, Qt.AlignRight)
            self.btn_cancel: QPushButton = QPushButton(self)
            self.layout().addWidget(self.btn_cancel, row, 1, Qt.AlignRight)
        
        self.cal: QCalendarWidget = QCalendarWidget(self)
        if self.calendar_dict["show_buttons"]:
            self.layout().addWidget(self.cal, grid_count, 0, 1, 2)
        else:
            self.layout().addWidget(self.cal, grid_count, 0)
        grid_count += 1
        
        if self.calendar_dict["show_date_info"]:
            self.lbl_info: QLabel = QLabel(self)
            if self.calendar_dict["show_buttons"]:
                self.layout().addWidget(self.lbl_info, grid_count, 0, 1, 2)
            else:
                self.layout().addWidget(self.lbl_info, grid_count, 0)
        grid_count += 1

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["Calendar"])
        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        self.setWindowTitle(self.getl("calendar_win_title_text"))
        self.setWindowIcon(QIcon(self.getv("calendar_win_icon_path")))
        if self.calendar_dict["show_buttons"]:
            self._define_buttons_apperance(self.btn_select, "calendar_btn_select")
            self.btn_select.setText(self.getl("calendar_btn_select_text"))
            self.btn_select.setToolTip(self.getl("calendar_btn_select_tt"))
            self._define_buttons_apperance(self.btn_cancel, "calendar_btn_cancel")
            self.btn_cancel.setText(self.getl("calendar_btn_cancel_text"))
            self.btn_cancel.setToolTip(self.getl("calendar_btn_cancel_tt"))
        if self.calendar_dict["show_date_info"]:
            self._define_labels_apperance(self.lbl_info, "calendar_lbl_info")
        self._define_calendar_widget(self.cal, "calendar_cal_widget")
        self.cal.setToolTip(self.getl("calendar_cal_widget_tt"))

    def _define_calendar_widget(self, cal: QCalendarWidget, name: str) -> None:
        cal.setFirstDayOfWeek(self.getv("first_day_of_week"))
        cal.setGridVisible(self.getv(f"{name}_grid_visible"))
        cal.setVerticalHeaderFormat(cal.NoVerticalHeader)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        cal.setFont(font)
        cal.setStyleSheet(self.getv(f"{name}_stylesheet"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))

    def close_me(self):
        # Save user setting for position and size
        name = self.calendar_dict["name"]
        if name not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add(name, {}, save_to_file=True)
        self.get_appv(name)["position"] = f"{self.pos().x()},{self.pos().y()}"
        self.get_appv(name)["size"] = f"{self.width()},{self.height()}"
        # Unregister Dialog
        self.dialog_queue.dialog_method_remove_dialog(self.my_name)

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["Calendar"])
        UTILS.DialogUtility.on_closeEvent(self)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)


class Selection(QDialog):
    """Displays a list of items that the user can select.
    The display data is provided in the app setting dictionary 'menu'.
    {selection}:[title](str) = Selection title
                [mode](str) = ('menu', 'list'),
                [multi-select](bool) = Select multiple items
                [checkable](bool) = Can items be checked
                [items](list) = list of keys [  id, 
                                                name, 
                                                description, 
                                                selected, 
                                                checked, 
                                                subitems(list)]
    """
    def __init__(self, settings: settings_cls.Settings, parent_obj: object = None,  selection_dict: dict = None, *args, **kwargs):
        super().__init__(parent_obj, *args, **kwargs)
        self.parent_obj = parent_obj
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value
        # Load GUI
        uic.loadUi(self.getv("selection_ui_file_path"), self)
        # Item definitions and settings required to display the context menu
        if selection_dict:
            self.selection_dict = selection_dict
        else:
            self.selection_dict = self.get_appv("selection")
        
        self.selection_dict["result"] = None

        self._set_widgets_text()
        self._define_widgets()
        self.setLayout(self.grid_layout)
        self._set_widgets_apperance()
        self._load_position()
        
        self._populate_list_widget()
        self.lst_items_current_item_changed()
        if self.lst_items.count() > 0:
            self.lst_items.setCurrentRow(0)

        if self._get_selected_items or self._get_checked_items:
            self.btn_select.setEnabled(True)
        else:
            self.btn_select.setEnabled(False)

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.keyPressEvent = self.key_press_event

        self.lst_items.itemChanged.connect(self.lst_items_item_changed)
        self.lst_items.currentItemChanged.connect(self.lst_items_current_item_changed)
        self.lst_items.itemClicked.connect(self.lst_items_item_clicked)
        self.lst_items.itemDoubleClicked.connect(self.lst_items_double_click)
        self.btn_select.clicked.connect(self.btn_select_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_select_all.clicked.connect(self.btn_select_all_click)
        self.btn_clear_all.clicked.connect(self.btn_clear_all_click)

        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["Selection"], extract_to_variables=["selection_dict", self.selection_dict])
        self.btn_select.setFocus()
        # UTILS.DialogUtility.on_focus_lost_close_me(self)
        self.exec_()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        handle_dialog.properties.close_on_lost_focus = True

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_items)

        self.widget_handler.activate()

    def key_press_event(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return:
            self.btn_select_click()
        elif a0.key() == Qt.Key_Escape:
            UTILS.LogHandler.add_log_record("#1: User canceled selection.", ["Selection"])
            self.close()
        return super().keyPressEvent(a0)

    def btn_cancel_click(self):
        UTILS.LogHandler.add_log_record("#1: User canceled selection.", ["Selection"])
        self.close()

    def btn_select_all_click(self):
        if self.selection_dict["checkable"]:
            item = self.lst_items.currentItem()
            for idx in range(self.lst_items.count()):
                self.lst_items.item(idx).setCheckState(Qt.Checked)
            if item is not None:
                self.lst_items.setCurrentItem(item)
        elif self.selection_dict["multi-select"]:
            for idx in range(self.lst_items.count()):
                self.lst_items.item(idx).setSelected(True)

    def btn_clear_all_click(self):
        if self.selection_dict["checkable"]:
            item = self.lst_items.currentItem()
            for idx in range(self.lst_items.count()):
                self.lst_items.item(idx).setCheckState(Qt.Unchecked)
            if item is not None:
                self.lst_items.setCurrentItem(item)
        elif self.selection_dict["multi-select"]:
            for idx in range(self.lst_items.count()):
                self.lst_items.item(idx).setSelected(False)

    def btn_select_click(self):
        if self.selection_dict["checkable"]:
            self.selection_dict["result"] = self._get_checked_items()
            self.set_appv("selection", self.selection_dict)
        else:
            self.selection_dict["result"] = self._get_selected_items()
            self.set_appv("selection", self.selection_dict)

        UTILS.LogHandler.add_log_record("#1: User selected items.\n#2", ["Selection", self.selection_dict["result"]])
        self.close()

    def lst_items_double_click(self):
        if self.selection_dict["checkable"]:
            if self.lst_items.currentItem().checkState() == Qt.Checked:
                self.lst_items.currentItem().setCheckState(Qt.Unchecked)
            else:
                self.lst_items.currentItem().setCheckState(Qt.Checked)
        elif (not self.selection_dict["checkable"]) and (not self.selection_dict["multi-select"]):
            self.btn_select_click()

    def lst_items_item_clicked(self):
        self._update_lbl_count_and_btn_select()

    def lst_items_item_changed(self, item: QListWidgetItem) -> None:
        if item is not None:
            self.lst_items.setCurrentItem(item)
        self._update_lbl_count_and_btn_select()

    def lst_items_current_item_changed(self) -> None:
        self._update_lbl_count_and_btn_select()
        
    def _update_lbl_count_and_btn_select(self):
        if self.selection_dict["multi-select"]:
            if self._get_selected_items():
                self.lbl_count.setText(self.getl("selection_list_lbl_count_has_data") + str(len(self._get_selected_items())))
                self.btn_select.setEnabled(True)
            else:
                self.lbl_count.setText(self.getl("selection_list_lbl_count_no_data"))
                self.btn_select.setEnabled(False)
        if self.selection_dict["checkable"]:
            if self._get_checked_items():
                self.lbl_count.setText(self.getl("selection_list_lbl_count_has_data") + str(len(self._get_checked_items())))
                self.btn_select.setEnabled(True)
            else:
                self.lbl_count.setText(self.getl("selection_list_lbl_count_no_data"))
                self.btn_select.setEnabled(False)

    def _get_selected_items(self) -> list:
        selected = []
        for row in range(self.lst_items.count()):
            item = self.lst_items.item(row)
            if item.isSelected():
                selected.append(item.data(Qt.UserRole))
        return selected

    def _get_checked_items(self) -> list:
        checked = []
        for row in range(self.lst_items.count()):
            item = self.lst_items.item(row)
            if item.checkState() == Qt.Checked:
                checked.append(item.data(Qt.UserRole))
        return checked

    def _populate_list_widget(self):
        self.lst_items.clear()
        for record in self.selection_dict["items"]:
            item = QListWidgetItem()
            item.setText(record[1])
            item.setData(Qt.UserRole, record[0])
            
            item_alignment = self.getv("selection_list_item_alignment")
            if item_alignment:
                if isinstance(item_alignment, str):
                    item_alignment = sum([x for x in item_alignment.split(",") if x != ""])
                item.setTextAlignment(item_alignment)
            
            if self.getv("selection_show_item_tooltip"):
                item.setToolTip(record[2])
            if self.selection_dict["multi-select"]:
                item.setSelected(record[3])
            if self.selection_dict["checkable"]:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if record[4]:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
            self.lst_items.addItem(item)

    def _load_position(self):
        x = self.getv("selection_win_pos_x")
        y = self.getv("selection_win_pos_y")
        w = self.getv("selection_win_width")
        h = self.getv("selection_win_height")
        if x == -1:
            x = self.pos().x()
        elif y == -1:
            y = self.pos().y()
        elif w == 0:
            w = self.width()
        elif h == 0:
            h = self.height()
        self.move(x, y)
        self.resize(w, h)
            
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        self.set_appv("selection", self.selection_dict)
        self.setv("selection_win_pos_x", self.pos().x())
        self.setv("selection_win_pos_y", self.pos().y())
        self.setv("selection_win_width", self.width())
        self.setv("selection_win_height", self.height())
        self.dialog_queue.dialog_method_remove_dialog(self.my_name)

        QCoreApplication.processEvents()
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["Selection"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _define_widgets(self):
        self.grid_layout: QGridLayout = self.findChild(QGridLayout, "grid_layout")
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lst_items: QListWidget = self.findChild(QListWidget, "lst_items")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.btn_select: QPushButton = self.findChild(QPushButton, "btn_select")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        if self.selection_dict["multi-select"] or self.selection_dict["checkable"]:
            self.btn_select_all: QPushButton = self.findChild(QPushButton, "btn_select_all")
            self.btn_clear_all: QPushButton = self.findChild(QPushButton, "btn_clear_all")

    def _set_widgets_text(self):
        self.lbl_title.setText(self.selection_dict["title"])
        self.btn_cancel.setText(self.getl("selection_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("selection_btn_cancel_tt"))
        self.btn_cancel.setStatusTip(self.getl("selection_btn_cancel_sb_text"))
        self.btn_select.setText(self.getl("selection_btn_select_text"))
        self.btn_select.setToolTip(self.getl("selection_btn_select_tt"))
        self.btn_select.setStatusTip(self.getl("selection_btn_select_sb_text"))
        if self.selection_dict["multi-select"] or self.selection_dict["checkable"]:
            self.btn_select_all.setText(self.getl("selection_btn_select_all_text"))
            self.btn_select_all.setToolTip(self.getl("selection_btn_select_all_tt"))
            self.btn_select_all.setStatusTip(self.getl("selection_btn_select_all_sb_text"))
            self.btn_clear_all.setText(self.getl("selection_btn_clear_all_text"))
            self.btn_clear_all.setToolTip(self.getl("selection_btn_clear_all_tt"))
            self.btn_clear_all.setStatusTip(self.getl("selection_btn_clear_all_sb_text"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["Selection"])
        self._set_widgets_apperance(settings_updated=True)

    def _set_widgets_apperance(self, settings_updated: bool = False):
        self._define_buttons_apperance(self.btn_cancel, "selection_btn_cancel")
        self._define_buttons_apperance(self.btn_select, "selection_btn_select")
        self.btn_select.setDefault(True)
        if self.selection_dict["multi-select"] or self.selection_dict["checkable"]:
            self._define_buttons_apperance(self.btn_select_all, "selection_btn_select_all")
            self._define_buttons_apperance(self.btn_clear_all, "selection_btn_clear_all")
        self._define_labels_apperance(self.lbl_count, "selection_lbl_count")
        self._define_selection_win_apperance()
        self._define_labels_apperance(self.lbl_title, "selection_lbl_title")
        self._define_list_widget_apperance(self.lst_items, "selection_lst")
        if not settings_updated:
            self.footer_spacer = self.grid_layout.itemAtPosition(5, 1)
            self.title_body_spacer = self.grid_layout.itemAtPosition(1, 0)
            self.body_footer_spacer = self.grid_layout.itemAtPosition(4, 0)
        self.title_body_spacer.spacerItem().changeSize(20, self.getv("selection_spacer_title-body_height"))
        self.body_footer_spacer.spacerItem().changeSize(20, self.getv("selection_spacer_body-footer_height"))
    
    def _define_list_widget_apperance(self, list_widget: QListWidget, name: str) -> None:
        list_widget.setFrameShape(self.getv(f"{name}_frame_shape"))
        list_widget.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        list_widget.setLineWidth(self.getv(f"{name}_line_width"))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        list_widget.setFont(font)
        list_widget.setStyleSheet(self.getv(f"{name}_stylesheet"))
        list_widget.setEnabled(self.getv(f"{name}_enabled"))
        list_widget.setVisible(self.getv(f"{name}_visible"))
        if self.selection_dict["multi-select"]:
            list_widget.setSelectionMode(list_widget.MultiSelection)
        
    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        btn.setEnabled(self.getv(f"{name}_enabled"))
        btn.setVisible(self.getv(f"{name}_visible"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))

    def _define_selection_win_apperance(self):
        self.setLayout(self.grid_layout)
        self.setStyleSheet(self.getv("selection_win_stylesheet"))
        self._set_margins(self.layout(), "selection_win")
        self._set_margins(self.layout(), "selection_win_layout")
        self.layout().setSpacing(self.getv("selection_win_layout_spacing"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        if not self.getv("selection_win_show_titlebar"):
            self.setWindowFlag(Qt.FramelessWindowHint)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))
        label.setVisible(self.getv(f"{name}_visible"))


class Notification(QDialog):
    """
    Displays PopUp notifications to the user.
    data_dict (dict):
        title (str): Def:"Notification"
        text (str)
        icon (str): Def:None, Icon path
        timer (int): Closing notification in x milliseconds
        show_close (bool): Def:False, Show close button
        show_ok (bool): Def:False, Show OK button
        animation (bool): Whether the appearance will be animated
        animation_from_bottom (bool) Def:True
        position (str): Def=bottom_right, Position relative to parent widget
            position values:
                posx, posy - (Absolute Pos)
                top_left
                top_right
                bottom_left
                bottom_right
    """

    def __init__(self, settings: settings_cls.Settings, parent_widget, data_dict: dict, play_sound: bool = True, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.data_dict = data_dict
        self.populate_data_dict()
        self.animation: BlockAnimation = None

        self._define_widgets()
        self._set_widgets_text()
        self._define_widgets_apperance()

        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        if self.data_dict["show_close"]:
            self.btn_close.clicked.connect(self.btn_close_click)
        if self.data_dict["show_ok"]:
            self.btn_ok.clicked.connect(self.btn_ok_click)

        self.show()

        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["Notification"], extract_to_variables=["data_dict", self.data_dict])
        
        if self.getv("notification_start_sound_enabled") and play_sound:
            self.notif_sound = UTILS.SoundUtility(self.getv("notification_start_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
            self.notif_sound.play()

        # Define geometry
        self._define_win_size()
        self._set_win_position()
        if self.data_dict["show_close"]:
            self.btn_close.raise_()
        
        # Animation
        if self.data_dict["animation"]:
            info = BlockAnimationInformation(self._stt, "notification_open", block_object=self, start_height=0, stop_height=self.height())
            if self.animation and not self.animation.is_finished():
                self.animation.force_finish()
            self.animation = BlockAnimation(info, self, move_object_up=True)
        if self.data_dict["fade"] and self.getv("notification_open_animation_steps_number") > 0:
            oracity_step = 1 / self.getv("notification_open_animation_steps_number")
            oracity = 0
            step_duration = self.getv("notification_open_animation_total_duration_ms") / self.getv("notification_open_animation_steps_number") / 1000
            for i in range(self.getv("notification_open_animation_steps_number")):
                oracity += oracity_step
                self.setWindowOpacity(oracity)
                time.sleep(step_duration)
            self.setWindowOpacity(1)
        # Timer
        if self.data_dict["timer"]:
            self.timer.start(duration=self.data_dict["timer"])

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.properties.window_drag_enabled = False

        # Add frames

        # Add all Pushbuttons
        if self.data_dict["show_close"]:
            self.widget_handler.add_QPushButton(self.btn_close)

        if self.data_dict["show_ok"]:
            self.widget_handler.add_QPushButton(self.btn_ok)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def btn_ok_click(self):
        UTILS.LogHandler.add_log_record("#1: User clicked #2 button.", ["Notification", "OK"])
        self.close()

    def btn_close_click(self):
        UTILS.LogHandler.add_log_record("#1: User clicked #2 button.", ["Notification", "CLOSE"])
        self.close()

    def timer_timeout(self, timer: timer_cls.SingleShotTimer):
        self.timer.stop()

        if self.data_dict["animation"]:
            try:
                info = BlockAnimationInformation(self._stt, "notification_open", block_object=self, start_height=self.height(), stop_height=0)
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage("Error in showing #1.\nException:\n#2", ["Notification", str(e)])
                self.close_me()
                return
            if self.animation and not self.animation.is_finished():
                self.animation.force_finish()
            self.animation = BlockAnimation(info, self, move_object_up=True)
        if self.data_dict["fade"] and self.getv("notification_open_animation_steps_number") > 0:
            oracity_step = 1 / self.getv("notification_open_animation_steps_number")
            oracity = 1
            step_duration = self.getv("notification_open_animation_total_duration_ms") / self.getv("notification_open_animation_steps_number") / 1000
            for i in range(self.getv("notification_open_animation_steps_number")):
                oracity -= oracity_step
                self.setWindowOpacity(oracity)
                time.sleep(step_duration)
            self.setWindowOpacity(0)
        self.close()

    def _set_win_position(self):
        if "position" in self.data_dict:
            p = self.data_dict["position"]
            if p.find(",") >= 0:
                position = p.split(",")
                self.move(int(position[0]), int(position[1]))
                return
            x = 0
            y = 0
            if p.find("bottom") >= 0:
                y = self.parent_widget.height() - self.height() + self.parent_widget.mapToGlobal(QPoint(0, 0)).y()
                if y < 0:
                    y = 0
            if p.find("top") >= 0:
                y = self.parent_widget.mapToGlobal(QPoint(0, 0)).y()
                if y < 0:
                    y = 0
            if p.find("right") >= 0:
                x = self.parent_widget.width() - self.width() + self.parent_widget.mapToGlobal(QPoint(0, 0)).x()
                if x < 0:
                    x = 0
            if p.find("left") >= 0:
                x = self.parent_widget.mapToGlobal(QPoint(0, 0)).x()
                if x < 0:
                    x = 0
            self.move(x, y)

    def _define_win_size(self):
        self.setContentsMargins(0, 0, 0, 0)

        # Calculate width and height
        if self.data_dict["title"]:
            title = self._text_width_height(self.lbl_title.text(), self.lbl_title.font())
            title_w = title[0]
            title_h = title[1]
        else:
            title_w = 0
            title_h = 0
        
        text = self._text_width_height(self.lbl_text.text(), self.lbl_text.font())
        expand_text_width = self.getv("notification_lbl_text_font_size")

        text_w = text[0] + expand_text_width
        text_h = text[1]

        if self.data_dict["show_ok"]:
            button = self._text_width_height(self.btn_ok.text(), self.btn_ok.font())
            button_w = button[0] + self.getv("notification_btn_ok_width_pad")
            button_h = button[1] + self.getv("notification_btn_ok_height_pad")
        else:
            button_w = 0
            button_h = 0

        margins = [int(x) for x in self.getv("notification_win_margins").split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]

        total_h = title_h + text_h + button_h + margins[1] + margins[3]
        total_h += self.getv("notification_title_text_spacer")
        total_h += self.getv("notification_text_button_spacer")

        icon_h = int(total_h / 2)
        icon_w = icon_h

        total_w = icon_w + margins[0] + margins[2]
        if text_w > title_w:
            total_w += text_w
        else:
            total_w += title_w
        total_w += self.getv("notification_icon_text_spacer")

        # Resize Window
        self.resize(total_w, total_h)

        # Setup widgets position
        if self.data_dict["title"]:
            self.lbl_title.move(margins[0], margins[1])
            self.lbl_title.resize((total_w - margins[0] - margins[2]), title_h)
            self.lbl_title.setAlignment(Qt.AlignHCenter)
        
        if self.data_dict["show_close"]:
            self.btn_close.move((total_w - margins[2] - self.btn_close.width()), margins[0])
        
        self.lbl_icon.move(margins[0], (int(total_h / 4)))
        self.lbl_icon.resize(icon_w, icon_h)
        if self.data_dict["icon"]:
            image = QPixmap(self.data_dict["icon"])    
        else:
            image = QPixmap(self.getv("notification_lbl_icon_icon_path"))
        scaled_image = image.scaled(self.lbl_icon.width(), self.lbl_icon.height())
        self.lbl_icon.setPixmap(scaled_image)

        self.lbl_text.move((margins[0] + icon_w + self.getv("notification_icon_text_spacer")), margins[1] + title_h + self.getv("notification_title_text_spacer"))
        self.lbl_text.resize(text_w, text_h)

        if self.data_dict["show_ok"]:
            self.btn_ok.move(int(total_w / 2 - button_w / 2), (total_h - margins[3] - button_h))
            self.btn_ok.resize(button_w, button_h)

    def _text_width_height(self, text: str, font: QFont) -> tuple:
        w = 0
        fm = QFontMetrics(font)
        wmax = 0
        h = 0
        txt_list = [x for x in text.split("\n") if x != ""]
        for i in txt_list:
            i_w = fm.width(i)
            if w < i_w:
                w = i_w
            h += fm.height() + 3
        return (w, h)

    def close_me(self, fast_close: bool = False) -> bool:
        if fast_close:
            self.timer.stop()
            self.timer.close_me()
            if self.animation:
                self.animation.force_finish()
        else:
            if self.animation and not self.animation.is_finished():
                UTILS.LogHandler.add_log_record("#1: Dialog close delayed.\n#2 will close dialog later.", ["Notification", "MainWin"])
                main_dict = {
                    "name": "notification",
                    "id": self.my_name,
                    "action": "try_to_close_me",
                    "object": self,
                    "validation": self.animation.is_finished,
                    "execute_function": self.close_me
                }
                self.get_appv("main_win").events(main_dict)
                return False

        self.dialog_queue.dialog_method_remove_dialog(self.my_name)
        self.timer.stop()

        if self.animation:
            self.animation.close_me()

        QCoreApplication.processEvents()
        self.timer.close_me()

        UTILS.LogHandler.add_log_record("#1: Dialog closed. (FastClose=#2)", ["Notification", fast_close], variables=[["fast_close", fast_close]])
        UTILS.DialogUtility.on_closeEvent(self)
        return True

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not self.close_me():
            a0.ignore()
            return
        return super().closeEvent(a0)

    def _define_widgets(self):
        if self.data_dict["title"]:
            self.lbl_title: QLabel = QLabel(self)
        if self.data_dict["show_close"]:
            self.btn_close: QPushButton = QPushButton(self)

        self.lbl_text: QLabel = QLabel(self)
        self.lbl_icon: QLabel = QLabel(self)

        if self.data_dict["show_ok"]:
            self.btn_ok: QPushButton = QPushButton(self)
        self.timer = timer_cls.SingleShotTimer(None, duration=5000, function_on_finished=self.timer_timeout)
            
    def _set_widgets_text(self):
        self.lbl_text.setText(self.data_dict["text"])
        if self.data_dict["title"]:
            self.lbl_title.setText(self.data_dict["title"])
        if self.data_dict["show_ok"]:
            self.btn_ok.setText(self.getl("notification_btn_ok_text"))
            self.btn_ok.setToolTip(self.getl("notification_btn_ok_tt"))
            self.btn_ok.setStatusTip(self.getl("notification_btn_ok_sb_text"))
        if self.data_dict["show_close"]:
            self.btn_close.setText(self.getl("notification_btn_close_text"))
            self.btn_close.setToolTip(self.getl("notification_btn_close_tt"))
            self.btn_close.setStatusTip(self.getl("notification_btn_close_sb_text"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["Notification"])
        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        self._define_notification_win_apperance()

        if self.data_dict["title"]:
            self._define_labels_apperance(self.lbl_title, "notification_lbl_title")
            if self.data_dict.get("font_size"):
                font_stylesheet = f"QLabel {{font-size: {self.data_dict['font_size']}px;}}"
                self.lbl_title.setStyleSheet(self.lbl_title.styleSheet() + font_stylesheet)

        if self.data_dict["show_close"]:
            self._define_buttons_apperance(self.btn_close, "notification_btn_close")

        self._define_labels_apperance(self.lbl_text, "notification_lbl_text")
        if self.data_dict.get("font_size"):
            font_stylesheet = f"QLabel {{font-size: {self.data_dict['font_size']}px;}}"
            self.lbl_text.setStyleSheet(self.lbl_text.styleSheet() + font_stylesheet)

        self.lbl_text.setWordWrap(True)

        self._define_labels_apperance(self.lbl_icon, "notification_lbl_icon")

        if self.data_dict["icon"]:
            image = QPixmap(self.data_dict["icon"])    
        else:
            image = QPixmap(self.getv("notification_lbl_icon_icon_path"))

        if self.data_dict["show_ok"]:
            self._define_buttons_apperance(self.btn_ok, "notification_btn_ok")

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))

    def _define_notification_win_apperance(self):
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet(self.getv("notification_win_stylesheet"))

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))
    
    def populate_data_dict(self):
        if "title" not in self.data_dict:
            self.data_dict["title"] = self.getl("notification_default_title")
        if "icon" not in self.data_dict:
            self.data_dict["icon"] = self.getv("notification_icon_path")
        if "show_close" not in self.data_dict:
            self.data_dict["show_close"] = False
        if "show_ok" not in self.data_dict:
            self.data_dict["show_ok"] = False
        if "animation" not in self.data_dict:
            if "fade" in self.data_dict:
                if self.data_dict["fade"] is False:
                    self.data_dict["animation"] = self.getv("notification_open_animation")
                else:
                    self.data_dict["animation"] = False
            else:
                self.data_dict["animation"] = self.getv("notification_open_animation")
        if "fade" not in self.data_dict:
            self.data_dict["fade"] = False
        if "animation_from_bottom" not in self.data_dict:
            self.data_dict["animation_from_bottom"] = True
        if "position" not in self.data_dict:
            self.data_dict["position"] = "bottom_right"
        if "timer" not in self.data_dict:
            self.data_dict["timer"] = None


class MessageInformation(QDialog):
    """ Displays a notification messagebox
    data_dict:
        title (str):
        text (str):
        icon_path (str):
        btn_ok_text (str):
        position (str, QPoint):
        pos_center (bool): Positions the center of the message box at the passed position
    """

    def __init__(self, settings: settings_cls.Settings, parent_widget, data_dict: dict, app_modal: bool = False, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.setLayout(QGridLayout())
        if app_modal:
            self.setWindowModality(Qt.ApplicationModal)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)

        # Variables
        self._data_dict = data_dict
        self._parent_widget = parent_widget
        self.drag_mode = None

        # Define widgets
        self._populate_data_dict()
        self._define_widgets()
        self._define_widgets_apperance()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)
        self.btn_ok.clicked.connect(self.btn_ok_click)

        self.show()
        
        self._set_position()
        if self._data_dict["pos_center"]:
            self.center_dialog()

        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["MessageInformation"], extract_to_variables=["data_dict", self._data_dict])
        self.exec_()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_text, self.lbl_icon])
        if self._data_dict["title"]:
            handle_dialog.add_window_drag_widgets([self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        handle_dialog.properties.close_on_lost_focus = True

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_QPushButton(self.btn_ok)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def _set_position(self):
        pos = self._data_dict["position"]
        if pos:
            if isinstance(pos, QPoint):
                self.move(pos.x(), pos.y())
            elif isinstance(pos, str):
                xy = self._parse_position(pos)
                self.move(xy[0], xy[1])
        screen = QDesktopWidget()
        if (self.pos().y() + self.height()) > screen.height():
            self.move(self.pos().x(), screen.height() - self.height())
        if (self.pos().x() + self.width()) > screen.width():
            self.move(screen.width() - self.width(), self.height())
    
    def center_dialog(self):
        x = self.pos().x() - self.width() / 2
        y = self.pos().y() - self.height() / 2
        if x < 0:
            x = 0
        elif y < 0:
            y = 0
        self.move(int(x), int(y))

    def btn_ok_click(self):
        self.close()

    def close_me(self):
        # Unregister Dialog
        self.dialog_queue.dialog_method_remove_dialog(self.my_name)

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["MessageInformation"])
        UTILS.DialogUtility.on_closeEvent(self)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def _populate_data_dict(self):
        self._data_dict["text"] = f'\n{self._data_dict["text"]}\n'
        if "title" not in self._data_dict:
            self._data_dict["title"] = None
        if "position" not in self._data_dict:
            self._data_dict["position"] = None
        if "icon_path" not in self._data_dict:
            self._data_dict["icon_path"] = None
        if "btn_ok_text" not in self._data_dict:
            self._data_dict["btn_ok_text"] = None
        if "pos_center" not in self._data_dict:
            self._data_dict["pos_center"] = None

    def _get_text_width(self, text: str, font: QFont) -> int:
        fm = QFontMetrics(font)
        return fm.width(text)

    def _define_widgets(self):
        grid_pos = 0
        if self._data_dict["title"]:
            self.lbl_title: QLabel = QLabel(self)
            self.lbl_title.setText(self._data_dict["title"])
            # self.lbl_title.setWordWrap(True)
            self.layout().addWidget(self.lbl_title, grid_pos, 0, 1, 2, Qt.AlignHCenter)
            grid_pos += 1
        
        self.lbl_text: QLabel = QLabel(self)
        self.lbl_text.setText(self._data_dict["text"])
        self.lbl_text.setWordWrap(True)
        self.layout().addWidget(self.lbl_text, grid_pos, 1)

        self.lbl_icon: QLabel = QLabel(self)
        self.layout().addWidget(self.lbl_icon, grid_pos, 0, Qt.AlignLeft)
        grid_pos += 1

        self.btn_ok: QPushButton = QPushButton(self)
        self.layout().addWidget(self.btn_ok, grid_pos, 0, 1, 2, Qt.AlignHCenter)
        if self._data_dict["btn_ok_text"]:
            self.btn_ok.setText(self._data_dict["btn_ok_text"])
        else:
            self.btn_ok.setText(self.getl("messagebox_information_btn_ok_text"))
        grid_pos += 1

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["MessageInformation"])
        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        # Win 
        self._define_message_win_apperance()
        
        # Title
        if self._data_dict["title"]:
            self._define_labels_apperance(self.lbl_title, "msg_box_title")
            # self.lbl_title.setFixedWidth(self._get_text_width(self.lbl_title.text(), self.lbl_title.font()))
            self.lbl_title.adjustSize()
        
        # Text
        self._define_labels_apperance(self.lbl_text, "msg_box_text")
        text_list = [x for x in self._data_dict["text"].split("\n") if x != ""]
        lbl_text_width = 0
        for line in text_list:
            if lbl_text_width < self._get_text_width(line, self.lbl_text.font()):
                lbl_text_width = self._get_text_width(line, self.lbl_text.font())
        self.lbl_text.setFixedWidth(lbl_text_width)

        # Button OK
        self._define_buttons_apperance(self.btn_ok, "msg_box_btn_ok")

        # Icon Label
        if self._data_dict["icon_path"]:
            icon_path = self._data_dict["icon_path"]
        else:
            icon_path = self.getv("messagebox_information_icon_path")
        self.lbl_icon.setStyleSheet(self.getv("msg_box_icon_stylesheet"))
        image = QPixmap(icon_path)
        self.lbl_icon.resize(self.getv("msg_box_icon_width"), self.getv("msg_box_icon_height"))
        scaled_image = image.scaled(self.lbl_icon.width(), self.lbl_icon.height())
        self.lbl_icon.setPixmap(scaled_image)

    def _parse_position(self, pos_string: str) -> tuple:
        if pos_string.lower().find("center") >=0:
            parent_pos = self._parent_widget.mapToGlobal(self._parent_widget.pos())
            x = parent_pos.x() + self._parent_widget.width() / 2 - self.width() / 2
            y = parent_pos.y() + self._parent_widget.height() / 2 - self.height() / 2
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            return (int(x), int(y))

        pos_string = pos_string.strip("(")
        pos_string = pos_string.strip(")")
        pos_list = [x.strip() for x in pos_string.split(",") if x != ""]
        if len(pos_list) == 2:
            x = int(pos_list[0])
            y = int(pos_list[1])
        else:
            return None
        return (x, y)

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
        if self.getv(f"{name}_width") > 0:
            btn.setFixedWidth(self.getv(f"{name}_width"))
        if self.getv(f"{name}_height") > 0:
            btn.setFixedHeight(self.getv(f"{name}_height"))

    def _define_message_win_apperance(self):
        self.setStyleSheet(self.getv("msg_info_win_stylesheet"))
        self._set_margins(self.layout(), "msg_info_win")
        self._set_margins(self.layout(), "msg_info_win_layout")
        self.layout().setSpacing(self.getv("msg_info_win_layout_spacing"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])


class MessageQuestion(QDialog):
    """ Displays a notification messagebox
    data_dict:
        title (str):
        text (str):
        icon_path (str):
        buttons (list):
            [ id, name, tooltip, icon, enabled ]
        position (str, QPoint): center_parent, center_screen
        pos_center (bool): Positions the center of the message box at the passed position
    """

    def __init__(self, settings: settings_cls.Settings, parent_widget, data_dict: dict, app_modal: bool = True, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.setLayout(QGridLayout())
        if app_modal:
            self.setWindowModality(Qt.ApplicationModal)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Register dialog
        self.my_name = str(time.time_ns())
        self.dialog_queue: DialogsQueue = self.get_appv("cm")
        self.dialog_queue.dialog_method_add_dialog(self, self.my_name)

        # Variables
        self._data_dict = data_dict
        self._parent_widget = parent_widget
        self.drag_mode = None

        # Define widgets
        self._populate_data_dict()
        self._define_widgets()
        self._define_widgets_apperance()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        for button in self._data_dict["buttons"]:
            button[-1].clicked.connect(self.button_clicked)

        self.show()
        
        self._set_position()
        if self._data_dict["pos_center"]:
            self.center_dialog()
        
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["MessageQuestion"], extract_to_variables=["data_dict", self._data_dict])

        self.exec_()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_text, self.lbl_icon])
        if self._data_dict["title"]:
            handle_dialog.add_window_drag_widgets([self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        handle_dialog.properties.close_on_lost_focus = True

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def button_clicked(self):
        button = self.sender()
        self._data_dict["result"] = int(button.objectName())
        UTILS.LogHandler.add_log_record('#1: User clicked "#2".', ["MessageQuestion", button.text()])
        self.close()

    def _set_position(self):
        pos = self._data_dict["position"]
        if pos:
            if isinstance(pos, QPoint):
                self.move(pos.x(), pos.y())
            elif isinstance(pos, str):
                if pos.lower().find("center") >= 0:
                    if pos.lower().find("screen") >= 0:
                        self._center_screen()
                    else:
                        self._center_parent()
                else:
                    xy = self._parse_position(pos)
                    self.move(xy[0], xy[1])
        screen = QDesktopWidget()
        if (self.pos().y() + self.height()) > screen.height():
            self.move(self.pos().x(), screen.height() - self.height())
        if (self.pos().x() + self.width()) > screen.width():
            self.move(screen.width() - self.width(), self.height())
        if self._data_dict["pos_center"]:
            self.center_dialog()

    def _center_screen(self):
        screen = QDesktopWidget()
        x = int(screen.width() / 2)
        y = int(screen.height() / 2)
        self.move(x, y)
        self.center_dialog()

    def _center_parent(self):
        par_xy = self._parent_widget.mapToGlobal(self._parent_widget.pos())
        x = int(par_xy.x() + self._parent_widget.width() / 2)
        y = int(par_xy.y() + self._parent_widget.height() / 2)
        local_pos = QPoint(x, y)
        local_pos = self._parent_widget.mapFromGlobal(local_pos)
        self.move(local_pos)
        self.center_dialog()

    def center_dialog(self):
        x = self.pos().x() - self.width() / 2
        y = self.pos().y() - self.height() / 2
        if x < 0:
            x = 0
        elif y < 0:
            y = 0
        self.move(int(x), int(y))

    def close_me(self):
        # Unregister Dialog
        self.dialog_queue.dialog_method_remove_dialog(self.my_name)

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["MessageQuestion"])
        UTILS.DialogUtility.on_closeEvent(self)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def _populate_data_dict(self):
        if "title" not in self._data_dict:
            self._data_dict["title"] = None
        if "position" not in self._data_dict:
            self._data_dict["position"] = None
        if "icon_path" not in self._data_dict:
            self._data_dict["icon_path"] = None
        if "pos_center" not in self._data_dict:
            self._data_dict["pos_center"] = None
        if "result" not in self._data_dict:
            self._data_dict["result"] = None

    def _get_text_width(self, text: str, font: QFont) -> int:
        fm = QFontMetrics(font)
        return fm.width(text)

    def _define_widgets(self):
        grid_pos = 0
        if self._data_dict["title"]:
            self.lbl_title: QLabel = QLabel(self)
            self.lbl_title.setText(self._data_dict["title"])
            self.lbl_title.setWordWrap(True)
            span_cols = len(self._data_dict["buttons"])
            if span_cols < 2:
                span_cols = 2
            self.layout().addWidget(self.lbl_title, grid_pos, 0, 1, span_cols, Qt.AlignHCenter)
            grid_pos += 1

        self.lbl_icon: QLabel = QLabel(self)
        self.layout().addWidget(self.lbl_icon, grid_pos, 0, Qt.AlignLeft)

        self.lbl_text: QLabel = QLabel(self)
        self.lbl_text.setText(self._data_dict["text"])
        self.lbl_text.setWordWrap(True)
        self.layout().addWidget(self.lbl_text, grid_pos, 1)
        grid_pos += 1

        # Set layout for buttons
        self.buttons_layout = QHBoxLayout()
        self.layout().addItem(self.buttons_layout, grid_pos, 0, 1, 2)

        # Make buttons list
        for i in range(len(self._data_dict["buttons"])):
            btn = QPushButton(self)
            self._define_buttons_apperance(btn, "msg_box_btn_ok")
            btn.setText(self._data_dict["buttons"][i][1])
            btn.setToolTip(self._data_dict["buttons"][i][2])
            btn.setIcon(QIcon(self._data_dict["buttons"][i][3]))
            btn.setEnabled(self._data_dict["buttons"][i][4])
            btn.setObjectName(str(self._data_dict["buttons"][i][0]))
            self.buttons_layout.addWidget(btn)
            self._data_dict["buttons"][i].append(btn)

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["MessageQuestion"])
        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        # Win 
        self._define_message_win_apperance()
        
        # Title
        if self._data_dict["title"]:
            self._define_labels_apperance(self.lbl_title, "msg_box_title")
            # self.lbl_title.setFixedWidth(self._get_text_width(self.lbl_title.text(), self.lbl_title.font()))
        
        # Text
        self._define_labels_apperance(self.lbl_text, "msg_box_text")
        text_list = [x for x in self._data_dict["text"].split("\n") if x != ""]
        lbl_text_width = 0
        for line in text_list:
            if lbl_text_width < self._get_text_width(line, self.lbl_text.font()):
                lbl_text_width = self._get_text_width(line, self.lbl_text.font())
        self.lbl_text.setFixedWidth(lbl_text_width)

        # Icon Label
        if self._data_dict["icon_path"]:
            icon_path = self._data_dict["icon_path"]
        else:
            icon_path = self.getv("messagebox_question_icon_path")
        self.lbl_icon.setStyleSheet(self.getv("msg_box_icon_stylesheet"))
        image = QPixmap(icon_path)
        self.lbl_icon.resize(self.lbl_title.height() + self.lbl_text.height(), self.lbl_title.height() + self.lbl_text.height())
        scaled_image = image.scaled(self.lbl_icon.width(), self.lbl_icon.height())
        self.lbl_icon.setPixmap(scaled_image)

    def _parse_position(self, pos_string: str) -> tuple:
        if pos_string.lower().find("center") >=0:
            parent_pos = self._parent_widget.mapToGlobal(self._parent_widget.pos())
            x = parent_pos.x() + self._parent_widget.width() / 2 - self.width() / 2
            y = parent_pos.y() + self._parent_widget.height() / 2 - self.height() / 2
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            return (int(x), int(y))

        pos_string = pos_string.strip("(")
        pos_string = pos_string.strip(")")
        pos_list = [x.strip() for x in pos_string.split(",") if x != ""]
        if len(pos_list) == 2:
            x = int(pos_list[0])
            y = int(pos_list[1])
        else:
            return None
        return (x, y)

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))

    def _define_message_win_apperance(self):
        self.setStyleSheet(self.getv("msg_info_win_stylesheet"))
        self._set_margins(self.layout(), "msg_info_win")
        self._set_margins(self.layout(), "msg_info_win_layout")
        self.layout().setSpacing(self.getv("msg_info_win_layout_spacing"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])


class FileDialog():
    def __init__(self, settings: settings_cls.Settings = None):
        self._stt = settings

    class FileInfo():
        def __init__(self, settings: settings_cls.Settings = None, file_path: str = None):
            self._file_path = file_path

            if settings:
                self._stt = settings
                self._date_format = f'{self._stt.get_setting_value("date_format")}  {self._stt.get_setting_value("time_format")}'
            else:
                self._stt = None
                self._date_format = ""

        def load_file(self, file_path: str):
            self._file_path = file_path

        def are_files_equal(self, file1: str, file2: str) -> bool:
            with open(file1, "rb") as file:
                hash1 = hashlib.md5(file.read()).digest()
            with open(file2, "rb") as file:
                hash2 = hashlib.md5(file.read()).digest()
            if hash1 == hash2:
                return True
            else:
                return False

        def _fp(self, file_path: str = None) -> str:
            if file_path is None:
                file_path = self._file_path
            if file_path is None:
                UTILS.TerminalUtility.WarningMessage("The file path cannot be None!", exception_raised=True)
                raise ValueError("The file path cannot be None!")
            return file_path

        def get_file_exstension_short_list(self, file_path: str = None) -> list:
            file_path = self._fp(file_path=file_path)

            exstension = os.path.splitext(file_path)[1]
            ext_result = self._get_ext(exstension, "short")
            return [x[1] for x in ext_result]

        def get_file_exstension_long_list(self, file_path: str = None) -> list:
            file_path = self._fp(file_path=file_path)

            exstension = os.path.splitext(file_path)[1]
            ext_result = self._get_ext(exstension, "long")
            return [x[1] for x in ext_result]

        def get_file_exstension_short_formated(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            exstension = os.path.splitext(file_path)[1]
            ext_result = self._get_ext(exstension, "short")
            
            if ext_result:
                result = ext_result[0][1]
            else:
                result = ""

            return result

        def get_file_exstension_long_formated(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            exstension = os.path.splitext(file_path)[1]
            ext_result = self._get_ext(exstension, "long")

            result = ""
            if len(ext_result) == 1:
                result = ext_result[0][1]
            else:
                for item in ext_result:
                    result += f"( {item[1]} ), "
                result = result.strip().strip(",")
            
            return result

        def _get_ext(self, extension: str, type: str) -> list:
            stt = "data/app/settings/file_ext.json"
            if not os.path.isfile(stt):
                return []
            
            with open(stt, "r", encoding="utf-8") as file:
                ext_dict = json.load(file)
            
            result = []
            if type == "short":
                ext_list = ext_dict["short"]
            elif type == "long":
                ext_list = ext_dict["long"]
            else:
                return []
            
            for item in ext_list:
                if item[0].lower() == extension.lower():
                    result.append(item)
            
            return result

        def size(self, file_path: str = None) -> int:
            file_path = self._fp(file_path=file_path)

            file_info = QFileInfo(file_path)
            if file_info.exists():
                return file_info.size()
            else:
                return -1

        def file_extension(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            result = os.path.splitext(file_path)[1]
            if not result:
                result = ""
            
            return result

        def size_formated(self, file_path: str = None) -> str:
            size = self.size(file_path)

            if size == -1:
                return "N/A"

            if self._stt:
                txt = f'{size} {self._stt.lang("bytes_text")}'
            else:
                txt = f'{size} b'
            
            if size > 1024:
                txt = f"{size/1024: .2f} Kb"
            if size > 1024*1024:
                txt = f"{size/1024/1024: .2f} Mb"
            if size > 1024*1024*1024:
                txt = f"{size/1024/1024/1024: .2f} Gb"

            return txt
        
        def created(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            file_info = QFileInfo(file_path)
            if file_info.exists() and file_info.birthTime().isValid():
                if self._date_format:
                    return file_info.birthTime().toPyDateTime().strftime(self._date_format)
                else:
                    return file_info.birthTime().toString()
            else:
                return ""

        def modified(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            file_info = QFileInfo(file_path)
            if file_info.exists() and file_info.lastModified().isValid():
                if self._date_format:
                    return file_info.lastModified().toPyDateTime().strftime(self._date_format)
                else:
                    return file_info.lastModified().toString()
            else:
                return ""

        def last_read(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            file_info = QFileInfo(file_path)
            if file_info.exists() and file_info.lastRead().isValid():
                if self._date_format:
                    return file_info.lastRead().toPyDateTime().strftime(self._date_format)
                else:
                    return file_info.lastRead().toString()
            else:
                return ""

        def icon(self, file_path: str = None) -> QIcon:
            file_path = self._fp(file_path=file_path)

            file_info = QFileInfo(file_path)
            if file_info.exists():
                file_icon_provider = QFileIconProvider()
                file_icon = file_icon_provider.icon(file_info)
                return file_icon
            else:
                return QIcon()

        def copy_file(self, file_path: str, destination: str):

            shutil.copy(file_path, destination)
        
        def absolute_path(self, file_path: str = None) -> str:
            file_path = self._fp(file_path=file_path)

            result = os.path.abspath(file_path)
            return result

    def delete_temp_folder(self):
        files = os.listdir(self._stt.get_setting_value("temp_folder_path").strip("/"))
        for file in files:
            txt = self._stt.get_setting_value("temp_folder_path") + file
            if os.path.isfile(txt):
                os.remove(txt)

    def get_file_type_image(self, file_or_media_id, size: QSize = None) -> QPixmap:
        if self._stt is None:
            return None

        if isinstance(file_or_media_id, int):
            file = None
            db_media = db_media_cls.Media(self._stt)
            if db_media.is_media_exist(file_or_media_id):
                db_media.load_media(file_or_media_id)
                file = db_media.media_file
            else:
                db_media = db_media_cls.Files(self._stt)
                if db_media.is_file_exist(file_or_media_id):
                    db_media.load_file(file_or_media_id)
                    file = db_media.file_file
            if file is None:
                return None
        elif isinstance(file_or_media_id, str):
            file = file_or_media_id
        else:
            return None
        
        file_ext = os.path.splitext(file)[1].strip(".")
        file_type_folder = self._stt.get_setting_value("file_type_folder_path")
        images = os.listdir(file_type_folder)
        image_file = None
        for image in images:
            if file_ext.lower() == image[:image.find(".")].lower():
                image_file = os.path.abspath(file_type_folder + image)
                break
        else:
            return None
        
        img = QPixmap()
        img.load(image_file)
        if size:
            img = img.scaled(size.width(), size.height(), Qt.KeepAspectRatio)
        
        return img

    def get_file_tooltip_text(self, file: str, settings: settings_cls.Settings = None) -> str:
        if self._stt is None:
            self._stt = settings

        if self._stt is None:
            return
        
        file_info = self.FileInfo(settings=self._stt)
        
        file_info.load_file(file)
        try:
            tooltip = self._stt.lang("file_add_list_item_tooltip")
            tooltip = tooltip.replace("#1", f'<span style="color: #ffff00; font-size: 24px;">{file}</span><br>')
            tooltip = tooltip.replace("#2", f'<span style="color: #9decec">{file_info.size(): ,.0f}</span> {self._stt.lang("bytes_text")} ({file_info.size_formated()})<br>')
            tooltip = tooltip.replace("#3", f'<span style="color: #9decec">{str(file_info.created())}</span><br>')
            tooltip = tooltip.replace("#4", f'<span style="color: #9decec">{str(file_info.modified())}</span><br>')
            tooltip = tooltip.replace("#5", f'<span style="color: #9decec">{str(file_info.last_read())}</span><br>')
            tooltip = tooltip.replace("#6", f'<br><span style="color: #ffff00">{str(self.get_default_system_app(file))}</span>')
        except Exception as e:
            tooltip = f"Error:\n{str(e)}"

        return tooltip

    def get_web_file_name(self, url: str) -> str:
        parsed_url = urlparse(url)
        file_name = parsed_url.path.split("/")[-1]
        return file_name
    
    def get_web_file_extension(self, url: str) -> str:
        try:
            response = urllib.request.urlopen(url)
            content_type = response.headers['Content-Type']
            file_extension = mimetypes.guess_extension(content_type)
        except Exception as e:
            file_extension = None
        
        return file_extension

    def get_file_from_web(self, url: str, destination_file: str) -> dict:
        """Downloads a file from the Internet and returns the dictionary.
        Returns {}:
            file_path (str): file location on local hdd
            mime_name (str): mime name
            mime_icon_name (str): mime_icon_name
            headers (str): headers
            result (bool): result of operation, false if error occurred
            error (str): error description if any
        """
        error_desc = ""
        # Get file
        try:
            file_name, headers = urllib.request.urlretrieve(url, destination_file)
        except Exception as e:
            error_desc = str(e)

        if not error_desc:
            # Get MIME Type
            mime_db = QMimeDatabase()
            mime_type = mime_db.mimeTypeForFile(file_name)
            mime_name = mime_type.name()
            mime_icon_name = mime_type.iconName()

            # Copy file to downloads folder
            # destination = destination_folder + os.path.split(file_name)[1]
            # shutil.copy(file_name, destination)

        if error_desc:
            result = {
                "source": None,
                "file_path": None,
                "mime_name": None,
                "mime_icon_name": None,
                "headers": None,
                "result": False,
                "error": error_desc
            }
        else:
            result = {
                "source": url,
                "file_path": destination_file,
                "mime_name": mime_name,
                "mime_icon_name": mime_icon_name,
                "headers": {x:y for x,y in zip(headers.keys(), headers.values())},
                "result": True,
                "error": ""
            }

        return result

    def show_save_file_dialog(self, title: str = "Save file:", directory: str = "", file_name: str = "", parent_widget: QWidget = None):
        UTILS.LogHandler.add_log_record("#1: Save file dialog displayed.", ["FileDialog"])
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(parent_widget)
        # file_dialog.setOptions(options)
        if file_name:
            file_dialog.selectFile(file_name)

        file_name, _ = file_dialog.getSaveFileName(None, title, directory=directory)        

        UTILS.LogHandler.add_log_record("#1: User selected: #2", ["FileDialog", file_name])
        if file_name:
            return file_name
        else:
            return None

    def show_dialog(self, title: str = "Select file:", directory: str = "", multi_select: bool = False, save_as: bool = False, file_filter: str = None, settings: settings_cls.Settings = None, parent_widget: QWidget = None):
        UTILS.LogHandler.add_log_record("#1: Select file(s) dialog displayed.", ["FileDialog"])
        if settings:
            image_desc = settings.lang("file_filter_images_ext_desc")
            animation_desc = settings.lang("file_filter_animation_ext_desc")
            all_desc = settings.lang("file_filter_all_ext_desc")
            video_desc = settings.lang("file_filter_video_ext_desc")
        else:
            image_desc = "Images"
            animation_desc = "Animation"
            all_desc = "All"
            video_desc = "Video"

        image_ext = "*.bmp *.cur *.gif *.ico *.jpg *.jpeg *.pbm *.pgm *.png *.ppm *.svg *.tif *.tiff *.xbm *.xpm"
        animation_ext = "*.gif *.webp *.mng"
        video_ext = "*.avi *.flv *.mkv *.mov *.mp4 *.mpeg *.mpg *.ogv *.rm *.swf *.vob *.wmv"

        file_dialog = QFileDialog(parent_widget)
        # file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        # Set dialog title
        file_dialog.setWindowTitle(title)
        # Set dialog directory
        if directory:
            file_dialog.setDirectory(directory)
        # Allow user to select either images of videos
        if file_filter:
            if file_filter == "images":
                file_dialog.setNameFilter(f"{image_desc} ({image_ext});;{all_desc} (*)")
            elif file_filter == "animation":
                file_dialog.setNameFilter(f"{animation_desc} ({animation_ext});;{all_desc} (*)")
            elif file_filter == "video":
                file_dialog.setNameFilter(f"{video_desc} ({video_ext});;{all_desc} (*)")
        else:
            file_dialog.setNameFilter(f"{all_desc} (*);;{image_desc} ({image_ext});;{animation_desc} ({animation_ext});;{video_desc} ({video_ext})")

        if multi_select:
            result, _ = file_dialog.getOpenFileNames()
        else:
            result, _ = file_dialog.getOpenFileName()

        UTILS.LogHandler.add_log_record("#1: User selected: #2", ["FileDialog", result])
        return result

    def show_dialog_select_folder(self, title: str = "Select folder:", directory: str = "", multi_select: bool = False):
        UTILS.LogHandler.add_log_record("#1: Select folder(s) dialog displayed.", ["FileDialog"])
        if os.path.isfile(directory):
            directory = os.path.split(directory)[0]
        
        if not os.path.isdir(directory):
            directory = ""

        if multi_select:
            result = QFileDialog.getExistingDirectory(None, title, directory=directory)
            UTILS.LogHandler.add_log_record("#1: User selected: #2", ["FileDialog", result])
            if result:
                result = result.split(",")
        else:
            result = QFileDialog.getExistingDirectory(None, title, directory=directory)
            UTILS.LogHandler.add_log_record("#1: User selected: #2", ["FileDialog", result])

        return result

    def get_default_external_icon_and_app(self, file_type: str) -> tuple:
        """ Returns (tuple):
                Icon: QPixmap()
                Default app full path (str)
        """
        file_type = "." + file_type.split(".")[-1]

        fip = QFileIconProvider()
        file_icon = fip.icon(QFileInfo(file_type))

        file_name = self.get_default_system_app(file_type)
        if file_name is None:
            file_name = ""

        return (file_icon, file_name)

    def get_default_system_app(self, ext: str) -> str:
        if platform.system().lower == "windows":
            return self.get_default_windows_app(ext)
        elif platform.system().lower == "linux":
            return self.get_default_linux_app(ext)
        else:
            # Unknown OS
            return None
    
    def get_default_linux_app(self, ext: str) -> str:
        mime = mimetypes.MimeTypes()
        mime_type = mime.types_map
        file_type = None
        for m_type in mime_type:
            for key, value in m_type.items():
                if key == ext or key == f".{ext}":
                    file_type = value
                    break
            if file_type:
                break
        
        import subprocess
        
        try:
            output = subprocess.check_output(["xdg-mime", "query", "default", file_type])
            application = output.decode().strip()
        except subprocess.CalledProcessError:
            application = None

        return application

    def get_default_windows_app(self, ext: str) -> str:
        """ Returns (str) default application full path
        """
        if ext.find(".") >= 0:
            ext = "." + ext.split(".")[-1]

        try:  # UserChoice\ProgId lookup initial
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{}\UserChoice'.format(ext)) as key:
                progid = winreg.QueryValueEx(key, 'ProgId')[0]
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Classes\{}\shell\open\command'.format(progid)) as key:
                path = winreg.QueryValueEx(key, '')[0]
        except:  # UserChoice\ProgId not found
            try:
                class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, ext)
                if not class_root:  # No reference from ext
                    class_root = ext  # Try direct lookup from ext
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
                    path = winreg.QueryValueEx(key, '')[0]
            except:  # Ext not found
                path = None
        # Path clean up, if any
        if path:  # Path found
            path = os.path.expandvars(path)  # Expand env vars, e.g. %SystemRoot% for ext .txt
            path = shlex.split(path, posix=False)[0]  # posix False for Windows operation
            path = path.strip('"')  # Strip quotes
        # Return
        return path

    def get_valid_local_files(self, files: list) -> list:
        if isinstance(files, str):
            files = [files]
        result = self._search_dirs(files)

        return result

    def _search_dirs(self, files: list):
        def unpack_dir(directory: str) -> list:
            content = os.listdir(directory)
            full_path = os.path.split(directory)[0]
            if full_path:
                full_path += "/"
            result = [full_path + x for x in content]
            return result

        file_list = []
        dir_list = []
        for file in files:
            if os.path.isfile(file):
                file_list.append(file)
            if os.path.isdir(file):
                dir_list.append(file + "/")
        
        for folder in dir_list:
            file_list = file_list + self._search_dirs(unpack_dir(folder))
        
        return file_list

    def return_valid_urls_from_text(self, text: str) -> list:
        """It analyzes the text and extracts from it all web addresses and paths to local files.
        Returns a list of urls/paths.
        """
        urls = []

        if not text:
            return urls

        text = text.replace("\n", " ")

        text_list = [x.strip() for x in text.split(" ") if x.strip() != ""]

        for item in text_list:
            if len(item) > 3:
                if item.lower()[:4] == "http":
                    urls.append(item)
                    continue
            if item.find(":/"):
                if os.path.isfile(item):
                    urls.append(item)
                    continue

        return urls


class FileInfo(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, file_id: int, *args, **kwargs):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._file_id = file_id
        self._disable_change_event = False

        # Load GUI
        uic.loadUi(self.getv("file_info_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        if self._is_valid_file_id(self._file_id):
            self._populate_widgets()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.txt_name.textChanged.connect(self.txt_name_text_changed)
        self.txt_desc.textChanged.connect(self.txt_desc_text_changed)
        self.btn_update.clicked.connect(self.btn_update_click)
        self.btn_open.clicked.connect(self.btn_open_click)
        self.btn_save_as.clicked.connect(self.btn_save_as_click)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["FileInfo"])
        if not self._is_valid_file_id(self._file_id):
            self._show_msg_invalid_file_id()
            self.close()

    def _show_msg_invalid_file_id(self):
        msg_dict = {
            "title": self.getl("file_info_msg_invalid_file_id_title"),
            "text": self.getl("file_info_msg_invalid_file_id_text").replace("#1", str(self._file_id)),
        }
        self._disable_change_event = True
        MessageInformation(self._stt, self, msg_dict, app_modal=True)
        self._disable_change_event = False

    def _is_valid_file_id(self, file_id: int) -> bool:
        db_media = db_media_cls.Files(self._stt)
        return db_media.is_file_exist(file_id)

    def btn_save_as_click(self):
        db_media = db_media_cls.Files(self._stt, self._file_id)
        file_name = os.path.split(db_media.file_file)[1]

        file_util = FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt)

        file_abs_path = file_info.absolute_path(db_media.file_file)

        result = file_util.show_save_file_dialog(title=self.getl("save_file_dialog_title"), file_name=file_name)

        if not result:
            return
        
        if not file_info.file_extension(result):
            result += file_info.file_extension(file_abs_path)

        if os.path.isfile(result):
            if not self._show_msg_question_file_exist():
                return
        
        file_info.copy_file(file_abs_path, result)
        
        self._disable_change_event = True
        self._show_msg_file_copied(result)
        self._disable_change_event = False

    def btn_open_click(self):
        db_media = db_media_cls.Files(self._stt, self._file_id)
        file_util = FileDialog()
        file_info = file_util.FileInfo()
        try:
            os.startfile(file_info.absolute_path(db_media.file_file))
            UTILS.LogHandler.add_log_record("#1: File opened with default application.", ["FileInfo"])
        except Exception as e:
            UTILS.LogHandler.add_log_record("#1: Error occurred in attempt to open file with default application.\n#2", ["FileInfo", str(e)])
            self._show_msg_open_failed(str(e))

    def btn_update_click(self):
        obj_file = File(self._stt, file_id=self._file_id)
        obj_file.FileName = self.txt_name.text()
        obj_file.FileDescription = self.txt_desc.toPlainText()
        obj_file.save()

        file_dict = {
            "name": self.txt_name.text(),
            "description": self.txt_desc.toPlainText()
        }

        UTILS.LogHandler.add_log_record("#1: File updated.", ["FileInfo"], variables=[["FileName", file_dict["name"]], ["FileDescription", file_dict["description"]]])
        self._show_msg_updated()
        self.btn_update.setEnabled(False)

    def _show_msg_question_file_exist(self) -> bool:
        msg_dict = {
            "title": self.getl("file_info_msg_file_exist_title"),
            "text": self.getl("file_info_msg_file_exist_text"),
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True]
            ]
        }
        self._dont_clear_menu = True
        MessageQuestion(self._stt, self, msg_dict)
        if msg_dict["result"] == 10:
            return True
        
        return False

    def _show_msg_file_copied(self, file_name: str):
        msg_dict = {
            "title": self.getl("file_info_msg_copied_title"),
            "text": self.getl("file_info_msg_copied_text") + "\n" + file_name,
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict)

    def _show_msg_updated(self):
        msg_dict = {
            "title": self.getl("file_info_msg_updated_title"),
            "text": self.getl("file_info_msg_updated_text"),
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict)

    def _show_msg_open_failed(self, error_string: str):
        msg_dict = {
            "title": self.getl("file_info_msg_open_failed_title"),
            "text": self.getl("file_info_msg_open_failed_text") + "\n" + error_string,
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict)

    def txt_name_text_changed(self):
        self.btn_update.setEnabled(True)

    def txt_desc_text_changed(self):
        self.btn_update.setEnabled(True)

    def btn_cancel_click(self):
        self.close()

    def _populate_widgets(self):
        db_media = db_media_cls.Files(self._stt, file_id=self._file_id)
        file_util = FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt, file_path=db_media.file_file)

        self.txt_name.setText(db_media.file_name)
        self.txt_desc.setText(db_media.file_description)
        self.txt_file_path.setText(db_media.file_file)
        self.txt_file_src.setText(db_media.file_http)
        
        icon = file_info.icon()
        if icon:
            self.btn_open.setIcon(icon)
        
        img: QPixmap = icon.pixmap(QSize(32, 32))
        img = img.scaled(self.lbl_icon.width(), self.lbl_icon.height(), Qt.KeepAspectRatio)
        self.lbl_icon.setPixmap(img)
        
        self.lbl_ext.setText(file_info.file_extension())
        
        self.txt_file_type.setText(file_info.get_file_exstension_short_formated())
        self.lbl_title_desc.setText(file_info.get_file_exstension_long_formated())
        txt = "\n".join(file_info.get_file_exstension_long_list())
        self.lbl_title_desc.setToolTip(txt)
        
        lbl_ext_tooltip = f'<span style="color: #ffff00; font-size: 30px;">{file_info.file_extension()}</span><br>' + self.lbl_ext.toolTip()
        self.lbl_ext.setToolTip(lbl_ext_tooltip)

        def_app = file_util.get_default_system_app(file_info.file_extension())
        if def_app:
            def_app_file = os.path.split(def_app)[1]
            def_app_path = def_app
        else:
            def_app_file = self.getl("file_info_unknown_default_app_text")
            def_app_path = ""

        self.txt_def_app.setText(def_app_file)
        self.txt_def_app.setToolTip(def_app_path)

        self.lbl_size_val.setText(file_info.size_formated())
        self.lbl_size_val.setToolTip(f'{file_info.size(): ,.0f} {self.getl("bytes_text")}')
        self.lbl_created_val.setText(file_info.created())
        self.lbl_modified_val.setText(file_info.modified())
        self.lbl_accessed_val.setText(file_info.last_read())

        self.lbl_title.setToolTip(file_util.get_file_tooltip_text(db_media.file_file, settings=self._stt))

    def _load_win_position(self):
        if "file_info_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("file_info_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu and not self._disable_change_event:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "file_info_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("file_info_win_geometry", {}, save_to_file=True)

        g = self.get_appv("file_info_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["FileInfo"])
        UTILS.DialogUtility.on_closeEvent(self)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w, self.lbl_title.height())
        self.lbl_title_desc.resize(w, self.lbl_title_desc.height())
        self.txt_name.resize(w - 250, self.txt_name.height())
        self.txt_desc.resize(w - 250, self.txt_desc.height())

        self.line.resize(w - 20, self.line.height())
        self.line_2.resize(w - 20, self.line_2.height())

        self.txt_file_path.resize(w - 250, self.txt_file_path.height())
        self.txt_file_src.resize(w - 250, self.txt_file_src.height())

        self.btn_cancel.move(w - 100, h - 30)
        self.btn_update.move(w - 140, self.btn_update.pos().y())

        return super().resizeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_title_desc: QLabel = self.findChild(QLabel, "lbl_title_desc")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_desc: QLabel = self.findChild(QLabel, "lbl_desc")
        self.lbl_icon: QLabel = self.findChild(QLabel, "lbl_icon")
        self.lbl_ext: QLabel = self.findChild(QLabel, "lbl_ext")
        self.lbl_file_type: QLabel = self.findChild(QLabel, "lbl_file_type")
        self.lbl_file_path: QLabel = self.findChild(QLabel, "lbl_file_path")
        self.lbl_def_app: QLabel = self.findChild(QLabel, "lbl_def_app")
        self.lbl_file_src: QLabel = self.findChild(QLabel, "lbl_file_src")
        self.lbl_size: QLabel = self.findChild(QLabel, "lbl_size")
        self.lbl_created: QLabel = self.findChild(QLabel, "lbl_created")
        self.lbl_modified: QLabel = self.findChild(QLabel, "lbl_modified")
        self.lbl_accessed: QLabel = self.findChild(QLabel, "lbl_accessed")
        self.lbl_size_val: QLabel = self.findChild(QLabel, "lbl_size_val")
        self.lbl_created_val: QLabel = self.findChild(QLabel, "lbl_created_val")
        self.lbl_modified_val: QLabel = self.findChild(QLabel, "lbl_modified_val")
        self.lbl_accessed_val: QLabel = self.findChild(QLabel, "lbl_accessed_val")

        self.txt_name: QLineEdit = self.findChild(QLineEdit, "txt_name")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.txt_file_type: QLineEdit = self.findChild(QLineEdit, "txt_file_type")
        self.txt_file_path: QLineEdit = self.findChild(QLineEdit, "txt_file_path")
        self.txt_def_app: QLineEdit = self.findChild(QLineEdit, "txt_def_app")
        self.txt_file_src: QLineEdit = self.findChild(QLineEdit, "txt_file_src")

        self.btn_save_as: QPushButton = self.findChild(QPushButton, "btn_save_as")
        self.btn_open: QPushButton = self.findChild(QPushButton, "btn_open")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_update: QPushButton = self.findChild(QPushButton, "btn_update")

        self.line: QFrame = self.findChild(QFrame, "line")
        self.line_2: QFrame = self.findChild(QFrame, "line_2")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("file_info_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("file_info_lbl_title_tt"))

        self.lbl_name.setText(self.getl("file_info_lbl_name_text"))
        self.lbl_name.setToolTip(self.getl("file_info_lbl_name_tt"))

        self.lbl_desc.setText(self.getl("file_info_lbl_desc_text"))
        self.lbl_desc.setToolTip(self.getl("file_info_lbl_desc_tt"))

        self.lbl_icon.setText("")
        self.lbl_icon.setToolTip(self.getl("file_info_lbl_icon_tt"))

        self.lbl_ext.setText("")
        self.lbl_ext.setToolTip(self.getl("file_info_lbl_ext_tt"))

        self.lbl_file_type.setText(self.getl("file_info_lbl_file_type_text"))
        self.lbl_file_type.setToolTip(self.getl("file_info_lbl_file_type_tt"))

        self.lbl_file_path.setText(self.getl("file_info_lbl_file_path_text"))
        self.lbl_file_path.setToolTip(self.getl("file_info_lbl_file_path_tt"))

        self.lbl_def_app.setText(self.getl("file_info_lbl_def_app_text"))
        self.lbl_def_app.setToolTip(self.getl("file_info_lbl_def_app_tt"))

        self.lbl_file_src.setText(self.getl("file_info_lbl_file_src_text"))
        self.lbl_file_src.setToolTip(self.getl("file_info_lbl_file_src_tt"))

        self.lbl_size.setText(self.getl("file_info_lbl_size_text"))
        self.lbl_size.setToolTip(self.getl("file_info_lbl_size_tt"))

        self.lbl_created.setText(self.getl("file_info_lbl_created_text"))
        self.lbl_created.setToolTip(self.getl("file_info_lbl_created_tt"))

        self.lbl_modified.setText(self.getl("file_info_lbl_modified_text"))
        self.lbl_modified.setToolTip(self.getl("file_info_lbl_modified_tt"))

        self.lbl_accessed.setText(self.getl("file_info_lbl_accessed_text"))
        self.lbl_accessed.setToolTip(self.getl("file_info_lbl_accessed_tt"))

        self.lbl_size_val.setText("")
        self.lbl_size_val.setToolTip(self.getl("file_info_lbl_size_val_tt"))

        self.lbl_created_val.setText("")
        self.lbl_created_val.setToolTip(self.getl("file_info_lbl_created_val_tt"))

        self.lbl_modified_val.setText("")
        self.lbl_modified_val.setToolTip(self.getl("file_info_lbl_modified_val_tt"))

        self.lbl_accessed_val.setText("")
        self.lbl_accessed_val.setToolTip(self.getl("file_info_lbl_accessed_val_tt"))

        self.btn_save_as.setText(self.getl("file_info_btn_save_as_text"))
        self.btn_save_as.setToolTip(self.getl("file_info_btn_save_as_tt"))

        self.btn_open.setText(self.getl("file_info_btn_open_text"))
        self.btn_open.setToolTip(self.getl("file_info_btn_open_tt"))

        self.btn_cancel.setText(self.getl("btn_cancel"))
        self.btn_cancel.setToolTip("")

        self.btn_update.setText(self.getl("file_info_btn_update_text"))
        self.btn_update.setToolTip(self.getl("file_info_btn_update_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["FileInfo"])
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_file_info_win_apperance()
        self._define_labels_apperance(self.lbl_title, "file_info_lbl_title")
        self._define_labels_apperance(self.lbl_title_desc, "file_info_lbl_title_desc")
        self._define_labels_apperance(self.lbl_name, "file_info_lbl_name")
        self._define_labels_apperance(self.lbl_desc, "file_info_lbl_desc")
        self._define_labels_apperance(self.lbl_icon, "file_info_lbl_icon")
        self._define_labels_apperance(self.lbl_ext, "file_info_lbl_ext")
        self._define_labels_apperance(self.lbl_file_type, "file_info_lbl_file_type")
        self._define_labels_apperance(self.lbl_file_path, "file_info_lbl_file_path")
        self._define_labels_apperance(self.lbl_def_app, "file_info_lbl_def_app")
        self._define_labels_apperance(self.lbl_file_src, "file_info_lbl_file_src")
        self._define_labels_apperance(self.lbl_size, "file_info_lbl_size")
        self._define_labels_apperance(self.lbl_created, "file_info_lbl_created")
        self._define_labels_apperance(self.lbl_modified, "file_info_lbl_modified")
        self._define_labels_apperance(self.lbl_accessed, "file_info_lbl_accessed")
        self._define_labels_apperance(self.lbl_size_val, "file_info_lbl_size_val")
        self._define_labels_apperance(self.lbl_created_val, "file_info_lbl_created_val")
        self._define_labels_apperance(self.lbl_modified_val, "file_info_lbl_modified_val")
        self._define_labels_apperance(self.lbl_accessed_val, "file_info_lbl_accessed_val")

        self._define_text_box_apperance(self.txt_name, "file_info_txt_name")
        self._define_text_box_apperance(self.txt_desc, "file_info_txt_desc")
        self._define_text_box_apperance(self.txt_file_type, "file_info_txt_file_type")
        self._define_text_box_apperance(self.txt_file_path, "file_info_txt_file_path")
        self._define_text_box_apperance(self.txt_def_app, "file_info_txt_def_app")
        self._define_text_box_apperance(self.txt_file_src, "file_info_txt_file_src")

        self._define_buttons_apperance(self.btn_save_as, "file_info_btn_save_as")
        self._define_buttons_apperance(self.btn_open, "file_info_btn_open")
        self._define_buttons_apperance(self.btn_cancel, "file_info_btn_cancel")
        self._define_buttons_apperance(self.btn_cancel, "file_info_btn_update")
        self.btn_update.setEnabled(False)

    def _define_file_info_win_apperance(self):
        self.setStyleSheet(self.getv("file_info_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("file_info_win_icon_path")))
        self.setWindowTitle(self.getl("file_info_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedHeight(610)
        self.setMinimumWidth(740)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))


class FileAdd(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._last_folder = ""
        self._name = ""
        self._desc = ""

        self.set_appv("file_add", None)
        
        # Load GUI
        uic.loadUi(self.getv("file_add_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_file.clicked.connect(self._btn_file_click)
        self.btn_cancel.clicked.connect(self._btn_cancel_click)
        self.btn_add_to_list.clicked.connect(self._btn_add_to_list_click)
        self.txt_file.returnPressed.connect(self._btn_add_to_list_click)
        self.lst_select.itemChanged.connect(self._lst_select_item_changed)
        self.lst_select.mouseDoubleClickEvent = self._lst_select_mouse_double_click
        self.lst_select.mouseReleaseEvent = self._lst_select_mouse_release
        self.btn_add.clicked.connect(self._btn_add_click)
        self.txt_file.textChanged.connect(self._txt_file_text_changed)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["FileAdd"])
        self.exec_()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()
        btn_file: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(self.btn_file, return_none_if_not_found=True)
        if btn_file:
            btn_file.properties.allow_bypass_leave_event = False
        else:
            UTILS.TerminalUtility.WarningMessage("All buttons added but #1 not found !", ["btn_file"])

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_file)

        # Add Selection Widgets

        # ADD Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_select)

        self.widget_handler.activate()

    def _lst_select_mouse_double_click(self, e):
        if self.lst_select.currentItem() is not None:
            self._open_file(self.lst_select.currentItem().text())

    def _btn_add_click(self):
        result = []
        file_names = []
        has_data = True
        while has_data:
            has_data = False
            for i in range(self.lst_select.count()):
                if self.lst_select.item(i).checkState() == Qt.Checked:
                    has_data = True
                    file_names.append(self.lst_select.item(i).text())
                    file_id = self._add_file_to_media_db(self.lst_select.item(i).text())
                    result.append(file_id)
                    break
        
        self.set_appv("file_add", result)
        UTILS.LogHandler.add_log_record("#1: File(s) selected by user.", ["FileAdd"], variables=[["File:", file] for file in file_names])
        self.close()

    def _add_file_to_media_db(self, file: str) -> int:
        # Find user file folder name
        user_folder = os.path.split(self.get_appv("user").db_path)[0] + f'/{self.get_appv("user").id}files/'

        # Save file to database and get ID
        db_file = db_media_cls.Files(self._stt)
        file_dict = {
            "name": self._name,
            "description": self._desc,
            "file": "",
            "http": self._get_source(file),
            "default": 100
        }
        file_id = db_file.add_file(file_dict)

        # Set file name for user file
        file_name = f"{file_id}_" + os.path.split(file)[1]
        user_file = user_folder + file_name

        # Copy file to user folder
        abs_user_path = os.path.abspath(user_file)
        self._create_directory_structure(abs_user_path)
        shutil.copy(file, abs_user_path)

        # Update database with user file name
        file_dict = {
            "file": user_file,
        }
        db_file.update_file(file_id, file_dict)

        obj_file = File(self._stt, file_id=file_id)
        obj_file.add_to_file_list()

        for i in range(self.lst_select.count()):
            if self.lst_select.item(i).text() == file:
                self._remove_item_from_list(self.lst_select.item(i))
                break
        
        return file_id
    
    def _get_source(self, file: str) -> str:
        down_dict = self._downloads_dict()
        if file in down_dict:
            return down_dict[file]["source"]
        
        return file

    def _lst_select_mouse_release(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            self._show_context_menu()
        QListWidget.mouseReleaseEvent(self.lst_select, e)

    def _lst_select_item_changed(self):
        self._update_counter()

    def _show_context_menu(self):
        if self.lst_select.currentItem() is None:
            return
        
        menu_dict = {
            "position": QCursor.pos(),
            "separator": [20],
            "items": [
                [10, self.getl("file_add_list_menu_open_text"), self.getl("file_add_list_menu_open_tt"), True, [], self.lst_select.currentItem().icon()],
                [20, self.getl("file_add_list_menu_remove_text"), self.getl("file_add_list_menu_remove_tt"), True, [], None],
                [30, self.getl("file_add_list_menu_set_name_text"), self.getl("file_add_list_menu_set_name_tt"), True, [], None],
                [40, self.getl("file_add_list_menu_set_desc_text"), self.getl("file_add_list_menu_set_desc_tt"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        ContextMenu(self._stt, self)
        
        result = self.get_appv("menu")["result"]
        if result == 10:
            self._open_file(self.lst_select.currentItem().text())
        elif result == 20:
            self._remove_item_from_list(self.lst_select.currentItem())
        elif result == 30:
            self._set_file_name()
        elif result == 40:
            self._set_file_description()

    def _open_file(self, file: str):
        try:
            os.startfile(file)
        except Exception as e:
            self._msg_cannot_open_file(f"{self.lst_select.currentItem().text()}\n{e}")

    def _set_file_name(self):
        data_dict = {
            "name": "block_input_box_name",
            "title": self.getl("file_add_input_name_title"),
            "text": self._name,
            "position": QCursor().pos()
        }
        self._dont_clear_menu = True
        InputBoxSimple(self._stt, self, data_dict)
        if data_dict["result"]:
            self._name = data_dict["result"]

    def _set_file_description(self):
        data_dict = {
            "name": "block_input_box_name",
            "title": self.getl("file_add_input_desc_title"),
            "text": self._desc,
            "position": QCursor().pos(),
            "one_line": False
        }
        self._dont_clear_menu = True
        InputBoxSimple(self._stt, self, data_dict)
        if data_dict["result"]:
            self._desc = data_dict["result"]

    def _remove_item_from_list(self, item: QListWidgetItem):
        down_dict = self._downloads_dict()
        if item.text() in down_dict:
            down_dict.pop(item.text())
            self._save_download_dict(down_dict)
            if os.path.isfile(item.text()):
                os.remove(item.text())
        self.lst_select.takeItem(self.lst_select.row(item))
        self._update_counter()

    def _update_counter(self):
        checked = 0
        for i in range(self.lst_select.count()):
            if self.lst_select.item(i).checkState() == Qt.Checked:
                checked += 1

        if checked:
            self.btn_add.setEnabled(True)
        else:
            self.btn_add.setEnabled(False)

        self.lbl_count.setText(self.getl("file_add_lbl_count_text").replace("#1", str(checked)).replace("#2", str(self.lst_select.count())))

    def _create_directory_structure(self, file: str):
        folder = os.path.split(file)[0]

        if not os.path.isdir(folder):
            os.mkdir(folder)

    def _add_file_to_list(self):
        if not self.txt_file.text():
            return
        
        file = [x for x in self.txt_file.text().split("\n") if x != ""]
        file_util = FileDialog()

        # Checks if select files are files on local drive
        files = file_util.get_valid_local_files(file)

        if not files:
            if self.get_appv("clipboard").mimeData().hasUrls():
                files = [x.toLocalFile() for x in self.get_appv("clipboard").mimeData().urls()]
                files = file_util.get_valid_local_files(files)

        if files:
            self._fill_list(files)
            self.txt_file.setText("")
            return
        
        # Check if selected url is valid file on web
        count = 0
        for single_file in file:
            count += 1
            self.lbl_title.setText(self.getl("file_add_lbl_title_working").replace("#1", str(count)).replace("#2", str(len(file))))
            QCoreApplication.processEvents()
            if single_file.lower().find("http") < 0:
                self._msg_file_not_found(single_file)
                return

            file_extension = file_util.get_web_file_extension(single_file)

            if file_extension is None:
                self._msg_file_not_found(single_file)
                continue

            file_name = file_util.get_web_file_name(single_file)
            
            if file_name:
                destination_file = self.getv("download_folder_path") + file_name
            else:
                destination_file = self.getv("download_folder_path") + str(time.time_ns())
            
            destination_file = os.path.abspath(destination_file)
            destination_file = os.path.splitext(destination_file)[0] + file_extension

            result = file_util.get_file_from_web(single_file, destination_file=destination_file)

            self._save_file_info(result)

            self._fill_list([result["file_path"]])
        
        self.lbl_title.setText(self.getl("file_add_lbl_title_text"))
        self.txt_file.setText("")

    def _save_file_info(self, file_dict: dict):
        info_path = self.getv("download_folder_path") + "my_journal_download_info.json"
        dowloaded_files = self._stt.custom_dict_load(info_path)
        
        if dowloaded_files is None:
            dowloaded_files = {}
        
        dowloaded_files[file_dict["file_path"]] = {
            "source": file_dict["source"],
            "mime_name": file_dict["mime_name"],
            "headers": file_dict["headers"]
        }
        self._stt.custom_dict_save(info_path, dowloaded_files)

    def _save_download_dict(self, down_dict: dict):
        info_path = self.getv("download_folder_path") + "my_journal_download_info.json"
        self._stt.custom_dict_save(info_path, down_dict)

    def _msg_file_not_found(self, file: str):
        msg_dict = {
            "title": self.getl("file_add_msg_file_not_found_title"),
            "text": f'{self.getl("file_add_msg_file_not_found_text")}\n{file}'
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict, app_modal=False)

    def _msg_cannot_open_file(self, file: str):
        msg_dict = {
            "title": self.getl("file_add_msg_cannot_open_title"),
            "text": f'{self.getl("file_add_msg_cannot_open_text")}\n{file}'
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict, app_modal=False)

    def _fill_list(self, files):
        file_util = FileDialog()
        
        file_info = file_util.FileInfo(settings=self._stt)

        for file in files:
            if self._is_file_in_list(file):
                continue

            file_info.load_file(file)

            item = QListWidgetItem()
            item.setCheckState(Qt.Checked)
            item.setText(file)
            item.setData(Qt.UserRole, file)
            icn = file_info.icon()
            if icn:
                item.setIcon(icn)
            
            item.setToolTip(file_util.get_file_tooltip_text(file, settings=self._stt))

            self.lst_select.addItem(item)
        
        self._update_counter()

    def _is_file_in_list(self, file: str) -> bool:
        result = False
        for i in range(self.lst_select.count()):
            if self.lst_select.item(i).text() == file:
                result = True
                break
        return result

    def _btn_add_to_list_click(self):
        self._add_file_to_list()

    def _txt_file_text_changed(self):
        if self.txt_file.text():
            self.btn_add_to_list.setEnabled(True)
        else:
            self.btn_add_to_list.setEnabled(False)

    def _btn_cancel_click(self):
        self.close()

    def _btn_file_click(self):
        file = FileDialog()
        result = file.show_dialog(directory=self._last_folder, multi_select=True)
        if result:
            if isinstance(result, str):
                self._last_folder = result
                self.txt_file.setText(result)
            else:
                self._last_folder = result[0]
                self.txt_file.setText("\n".join(result))

    def _load_downloads_folder(self):
        downloads = self._downloads_dict()
        if downloads:
            self._fill_list([x for x in downloads])

    def _downloads_dict(self) -> dict:
        downloads = self._stt.custom_dict_load(self.getv("download_folder_path") + "my_journal_download_info.json")
        return downloads

    def _load_win_position(self):
        if "file_add_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("file_add_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self._last_folder = g["last_folder"]
        self._load_downloads_folder()

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "file_add_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("file_add_win_geometry", {}, save_to_file=True)

        g = self.get_appv("file_add_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["last_folder"] = self._last_folder

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["FileAdd"])
        UTILS.DialogUtility.on_closeEvent(self)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w, self.lbl_title.height())
        self.txt_file.resize(w - 60, self.txt_file.height())
        self.btn_file.move(w - 40, self.btn_file.pos().y())
        self.btn_add_to_list.move(w - 170, self.btn_add_to_list.pos().y())
        self.lst_select.resize(w -20, h - 180)
        self.lbl_count.move(10, h - 30)
        self.btn_add.move(w - 270, h - 30)
        self.btn_cancel.move(w - 90, h - 30)

        return super().resizeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_file: QLabel = self.findChild(QLabel, "lbl_file")
        self.lbl_select: QLabel = self.findChild(QLabel, "lbl_select")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")

        self.txt_file: QLineEdit = self.findChild(QLineEdit, "txt_file")
        self.lst_select: QListWidget = self.findChild(QListWidget, "lst_select")

        self.btn_file: QPushButton = self.findChild(QPushButton, "btn_file")
        self.btn_add_to_list: QPushButton = self.findChild(QPushButton, "btn_add_to_list")
        self.btn_add: QPushButton = self.findChild(QPushButton, "btn_add")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("file_add_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("file_add_lbl_title_tt"))

        self.lbl_file.setText(self.getl("file_add_lbl_file_text"))
        self.lbl_file.setToolTip(self.getl("file_add_lbl_file_tt"))

        self.lbl_select.setText(self.getl("file_add_lbl_select_text"))
        self.lbl_select.setToolTip(self.getl("file_add_lbl_select_tt"))

        self.lbl_count.setText(self.getl("file_add_lbl_count_no_text"))
        self.lbl_count.setToolTip(self.getl("file_add_lbl_count_no_tt"))

        self.btn_add_to_list.setText(self.getl("file_add_btn_add_to_list_text"))
        self.btn_add_to_list.setToolTip(self.getl("file_add_btn_add_to_list_tt"))

        self.btn_add.setText(self.getl("file_add_btn_add_text"))
        self.btn_add.setToolTip(self.getl("file_add_btn_add_tt"))

        self.btn_cancel.setText(self.getl("file_add_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("file_add_btn_cancel_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["FileAdd"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self._define_file_add_win_apperance()
        self._define_labels_apperance(self.lbl_title, "file_add_lbl_title")
        self._define_labels_apperance(self.lbl_file, "file_add_lbl_file")
        self._define_labels_apperance(self.lbl_select, "file_add_lbl_select")
        self._define_labels_apperance(self.lbl_count, "file_add_lbl_count")

        self._define_text_box_apperance(self.txt_file, "file_add_txt_file")
        self.lst_select.setStyleSheet(self.getv("file_add_lst_select_stylesheet"))

        self._define_buttons_apperance(self.btn_file, "file_add_btn_file")
        self._define_buttons_apperance(self.btn_add_to_list, "file_add_btn_add_to_list")
        if not settings_updated:
            self.btn_add_to_list.setEnabled(False)
        self._define_buttons_apperance(self.btn_add, "file_add_btn_add")
        if not settings_updated:
            self.btn_add.setEnabled(False)
        self._define_buttons_apperance(self.btn_cancel, "file_add_btn_cancel")

    def _define_file_add_win_apperance(self):
        self.setStyleSheet(self.getv("file_add_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("file_add_win_icon_path")))
        self.setWindowTitle(self.getl("file_add_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(630, 370)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))


class DateTime():
    
    def __init__(self, settings: settings_cls.Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getv = settings.get_setting_value
        self.getl = settings.lang
        self.date_format_string = self.getv("date_format")
        self.time_format_string = self.getv("time_format")

    def get_today_date(self) -> str:
        date = datetime.date.today()
        result = date.strftime(self.date_format_string)
        return result

    def get_current_time(self) -> str:
        time = datetime.datetime.now()
        result = time.strftime(self.time_format_string)
        return result

    def get_current_date_and_time(self, with_long_names: bool = True):
        date = self.get_today_date()
        time = self.get_current_time()
        if with_long_names:
            date_dict = self.make_date_dict(date)
            result = f'{date_dict["day_name"]}, {date_dict["day"]} {date_dict["month_name"]} {date_dict["year"]} - {time}'
        else:
            result = date + " " + time
        return result

    def make_date_dict(self, date: str = "") -> dict:
        """Makes date dictionary.
        Args:
            date (str): Date in string format (dd.mm.yyyy.) Example:"31.03.2023."
        Returns:
            dict: A dictionary
                {   "date": str
                    "date_int": int
                    "day_name": str
                    "day": int
                    "month": int
                    "month_name": str   
                    "year": int
                    "day_in_week": int
                    "day_in_year": int
                    "week_in_year": int
                }
        """
        result = {}
        if isinstance(date, str):
            if not date:
                date = self.get_today_date()
            # Split date to day, month, year
            delimiters = [" ", ".", ";", "/", "-", "_", ":", ",", "|", "~", "*"]
            numbers = "0123456789"
            date_string = ""
            char_before = ""
            for char in date:
                if char in delimiters:
                    if char_before not in delimiters:
                        date_string += "."
                else:
                    if char in numbers:
                        date_string += char
                char_before = char
            date_string = date_string.strip(".")
            date = date_string.split(".")
            if len(date) != 3:
                return None
            if not (date[0].isdigit() and date[1].isdigit() and date[2].isdigit()):
                return None
            d = int(date[0])
            m = int(date[1])
            y = int(date[2])
        elif isinstance(date, tuple) or isinstance(date, list):
            if len(date) != 3:
                return None
            d = date[0]
            m = date[1]
            y = date[2]
        elif isinstance(date, QDate) or isinstance(date, datetime.date):
            d = date.day()
            m = date.month()
            y = date.year()
        else:
            return None
            
        if d not in range(1, 32) or m not in range(1, 13):
            return None

        try:
            date = datetime.date(y,m,d)
        except ValueError:
            return None
        day = date.isoweekday()
        day_in_year = int(date.strftime("%j"))
        day_name = self.getl("week_day" + str(day))
        week_in_year = int(date.strftime("%W"))
        month_name = self.getl("month" + date.strftime("%m"))
        date_int = self._date_integer(d, m, y)
        result["date"] = date.strftime(self.date_format_string)
        result["date_int"] = date_int
        result["day_name"] = day_name
        result["day"] = d
        result["month"] = m
        result["year"] = y
        result["day_in_week"] = day
        result["day_in_year"] = day_in_year
        result["week_in_year"] = week_in_year
        result["month_name"] = month_name

        return result

    def get_long_date(self, date: str) -> str:
        date_dict = self.make_date_dict(date=date)
        result = f'{date_dict["day_name"]}, {date_dict["day"]}. {date_dict["month_name"]} {date_dict["year"]}.'
        return result

    def _date_integer(self, day: int, month: int, year: int) -> int:
        def _add_leading_zeros(number: int, string_size: int) -> str:
            string = str(number)
            if len(string) == string_size:
                return string
            add_zeros = string_size - len(string)
            string = "0" * add_zeros + string
            return string
        
        result = _add_leading_zeros(year, 4) + _add_leading_zeros(month, 2) + _add_leading_zeros(day, 2)
        return int(result)

    def get_date_difference(self, from_date: str, to_date: str = "") -> int:
        if not from_date or not to_date:
            return 0

        date_from = datetime.datetime.strptime(from_date, self.getv("date_format"))
        if to_date:
            date_to = to_date
        else:
            date_to = datetime.datetime.today()
        diff = (date_to - date_from).days
        return diff


class BlockAnimationInformation():
    def __init__(self, settings: settings_cls.Settings, load_mode: str = None, animate_object: bool = None, block_object = None, start_height: int = 0, stop_height: int = 0, number_of_steps: int = None, total_duration: int = None):
        self.animate_object = True
        self.block_object = block_object
        self.start_height = start_height
        self.stop_height = stop_height
        self.number_of_steps = 0
        self.total_duration = 0
        self.in_layout = False

        if load_mode:
            self.getv = settings.get_setting_value
            if load_mode == "open":
                self.animate_object = self.getv("block_animation_on_open")
                self.number_of_steps = self.getv("block_animation_on_open_steps_number")
                self.total_duration = self.getv("block_animation_on_open_total_duration_ms")
                self.in_layout = True
            if load_mode == "close":
                self.animate_object = self.getv("block_animation_on_close")
                self.number_of_steps = self.getv("block_animation_on_close_steps_number")
                self.total_duration = self.getv("block_animation_on_close_total_duration_ms")
                self.in_layout = True
            if load_mode == "collapse":
                self.animate_object = self.getv("block_animation_on_collapse")
                self.number_of_steps = self.getv("block_animation_on_collapse_steps_number")
                self.total_duration = self.getv("block_animation_on_collapse_total_duration_ms")
                self.in_layout = True
            if load_mode == "expand":
                self.animate_object = self.getv("block_animation_on_expand")
                self.number_of_steps = self.getv("block_animation_on_expand_steps_number")
                self.total_duration = self.getv("block_animation_on_expand_total_duration_ms")
                self.in_layout = True
            if load_mode == "notification_open":
                self.animate_object = self.getv("notification_open_animation")
                self.number_of_steps = self.getv("notification_open_animation_steps_number")
                self.total_duration = self.getv("notification_open_animation_total_duration_ms")

        if animate_object is not None:
            self.animate_object = animate_object
        if number_of_steps is not None:
            self.number_of_steps = number_of_steps
        if total_duration is not None:
            self.total_duration = total_duration
        
        if self.number_of_steps < 1:
            self.number_of_steps = 10


class BlockAnimation():
    def __init__(self, block_animation_information: BlockAnimationInformation, block_object: QFrame = None, move_object_up: bool = False, *args, **kwargs):

        self.info = block_animation_information
        self.block_object = block_object
        self.move_object_up = move_object_up
        self.timer = None

        if self.block_object:
            self.info.block_object = self.block_object

        if self.move_object_up:
            self.y_start = self.info.block_object.pos().y() + self.info.block_object.height()
            self.y_start_reverse = self.info.block_object.pos().y()

        if not self.info.animate_object:
            self.info.block_object.setFixedHeight(self.info.stop_height)
            if self.move_object_up:
                y = self.y_start - self.info.stop_height
                if y > 0:
                    self.info.block_object.move(self.info.block_object.pos().x(), y)
            self._is_finished = True
        else:
            self.timer = timer_cls.ContinuousTimer(
                None,
                interval=(self.info.total_duration / self.info.number_of_steps),
                duration=self.info.total_duration,
                function_on_timeout=self.timeout,
                function_on_finished=self.finished,
                data = {"step": 1})
            
            self.start()

    def timeout(self, timer: timer_cls.ContinuousTimer):
        info = self.info
        step = timer.data["step"]
        timer.data["step"] = timer.data["step"] + 1
        if step > info.number_of_steps:
            step = info.number_of_steps

        step_size = int(abs(info.start_height - info.stop_height) / info.number_of_steps)
        
        try:
            if info.start_height < info.stop_height:
                if self.move_object_up:
                    y = self.y_start - step * step_size
                    if y > 0: 
                        if not self.info.in_layout:
                            info.block_object.move(info.block_object.pos().x(), y)
                info.block_object.setFixedHeight(step * step_size)
            else:
                info.block_object.setFixedHeight(info.start_height - step * step_size)
                if self.move_object_up:
                    y = self.y_start_reverse + step * step_size
                    if y > 0: 
                        if not self.info.in_layout:
                            info.block_object.move(info.block_object.pos().x(), y)
        except Exception as e:
            if timer:
                timer.stop()
            UTILS.TerminalUtility.WarningMessage("Error in #1 timeout.\nException:\n#2\nTimer is stopped.", ["BlockAnimation",str(e)])

        QCoreApplication.processEvents()

    def finished(self, timer: timer_cls.ContinuousTimer):
        try:
            self.info.block_object.setFixedHeight(self.info.stop_height)
            if self.move_object_up:
                y = self.y_start - self.info.stop_height
                if y > 0:
                    self.info.block_object.move(self.info.block_object.pos().x(), y)
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("#1: Error in #2 function.\nException:\n#3", ["BlockAnimation", "finished", str(e)])

        try:
            timer.stop()
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("#1: Error in #2 function. Timer does not exist.\nException:\n#3", ["BlockAnimation", "finished", str(e)])

        self._is_finished = True
        timer.close_me()
        self.timer = None

    def is_finished(self):
        return self._is_finished

    def force_finish(self):
        self.timer.stop()
        self.finished(self.timer)

    def close_me(self):
        if self.timer is not None:
            self.timer.stop()
            self.timer.close_me()
        self._is_finished = True

    def start(self):
        self._is_finished = False
        self.timer.start()
        return
        info = self.info
        if self.move_object_up:
            y_start = info.block_object.pos().y() + info.block_object.height()
            y_start_reverse = info.block_object.pos().y()
        if self.block_object:
            info.block_object = self.block_object
        if info.animate_object:
            step_size = int(abs(info.start_height - info.stop_height) / info.number_of_steps)
            step_duration = info.total_duration / info.number_of_steps / 1000
            
            for step in range(1, info.number_of_steps + 1):
                if info.start_height < info.stop_height:
                    if self.move_object_up:
                        y = y_start - step * step_size
                        if y > 0: 
                            info.block_object.move(info.block_object.pos().x(), y)
                    info.block_object.setFixedHeight(step * step_size)
                else:
                    info.block_object.setFixedHeight(info.start_height - step * step_size)
                    if self.move_object_up:
                        y = y_start_reverse + step * step_size
                        if y > 0: 
                            info.block_object.move(info.block_object.pos().x(), y)
                QCoreApplication.processEvents()
                time.sleep(step_duration)

        info.block_object.setFixedHeight(info.stop_height)
        if self.move_object_up:
            y = y_start - info.stop_height
            if y > 0:
                info.block_object.move(info.block_object.pos().x(), y)


class Signals(QObject):
    """This class serves to convey information to the button in the footer part that
    the object was detected so that the button could display that object correctly.
    """
    signalDetectedObject = pyqtSignal(bool)
    signalExpandAll = pyqtSignal()
    signalCollapseAll = pyqtSignal()
    signalBlockTextGiveFocus = pyqtSignal(int)
    signalSavedButtonCheckStatus = pyqtSignal(int)
    signalBlockControlBarInactive = pyqtSignal(bool, int)
    signalBlockDateFormatChanged = pyqtSignal()
    signalAutoCompleteSelected = pyqtSignal(dict)
    signalNewDefinitionAdded = pyqtSignal()
    signalPicBrowseShowContent = pyqtSignal(set)
    signalCloseAllBlocks = pyqtSignal()
    signalCloseAllDefinitions = pyqtSignal()
    signalSimpleDefinitionGeometryChanged = pyqtSignal(QFrame)
    signal_change_active_dict = pyqtSignal(dict)
    signal_app_settings_updated = pyqtSignal(dict)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_change_active_dict(self, dict_name: dict):
        self.signal_change_active_dict.emit(dict_name)

    def send_close_all_blocks(self):
        self.signalCloseAllBlocks.emit()

    def send_close_all_definitions(self):
        self.signalCloseAllDefinitions.emit()

    def send_pic_browse_show_content_signal(self, size: set):
        self.signalPicBrowseShowContent.emit(size)

    def send_detected_object_to_button(self, is_visible):
        self.signalDetectedObject.emit(is_visible)

    def send_expand_all_signal(self):
        self.signalExpandAll.emit()

    def send_collapse_all_signal(self):
        self.signalCollapseAll.emit()

    def block_text_give_focus(self, record_id: int):
        self.signalBlockTextGiveFocus.emit(record_id)

    def saved_button_check_status(self, record_id: int):
        self.signalSavedButtonCheckStatus.emit(record_id)

    def block_control_bar_inactive(self, set_inactive: bool = True, record_id: int = None):
        self.signalBlockControlBarInactive.emit(set_inactive, record_id)

    def block_date_format_changed(self):
        self.signalBlockDateFormatChanged.emit()

    def auto_complete_selected(self, data: dict):
        self.signalAutoCompleteSelected.emit(data)

    def new_definition_added(self):
        self.signalNewDefinitionAdded.emit()

    def simple_viev_geometry_changed(self, simple_def_object: QFrame):
        self.signalSimpleDefinitionGeometryChanged.emit(simple_def_object)

    def send_app_settings_updated(self, data: dict):
        self.signal_app_settings_updated.emit(data)


class AutoAddImageFrame(QFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self._parent_widget = parent_widget

        # Load GUI
        uic.loadUi(self.getv("auto_add_image_frame_ui_file_path"), self)

        self._define_widgets()
        self.setVisible(False)

        self.update_me()

        self.load_widgets_handler()

        # Connect Events with slots
        self.btn_exit.clicked.connect(self.btn_exit_clicked)
        self.keyPressEvent = self._key_press
        UTILS.LogHandler.add_log_record("#1: Frame loaded.", ["AutoAddImageFrame"])

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_QPushButton(self.btn_exit)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def _key_press(self, e):
        if e.key() == Qt.Key_Escape:
            self.btn_exit_clicked()

    def btn_exit_clicked(self):
        self._parent_widget.block_event("auto_add_images_frame", "close")

    def close_me(self):
        UTILS.LogHandler.add_log_record("#1: Frame deleted.", ["AutoAddImageFrame"])
        UTILS.DialogUtility.on_closeEvent(self)

    def update_me(self, image = None, info_text: str = None, is_error: bool = False):
        # Find size of parent widget
        w = self._parent_widget.contentsRect().width()
        h = self._parent_widget.contentsRect().height()

        # Resize QFrame
        self.move(0, 0)
        self.resize(w, h)

        # Arrange widgets
        self.lbl_pic.resize(h, h)
        
        self.lbl_title.move(h, 0)
        self.lbl_title.resize(abs(w - h), 60)
        
        self.lbl_info.move(h, 60)
        self.lbl_info.resize(abs(w - h), abs(h - 60))

        btn_y = h - 30
        if btn_y < 0:
            btn_y = 0
        btn_x = w - 300
        if btn_x < 0:
            btn_x = 0
        self.btn_exit.move(btn_x, btn_y)

        QCoreApplication.processEvents()
        self._load_picture(image)
        if info_text:
            if is_error:
                self.lbl_info.setStyleSheet("background-color: rgba(0, 85, 0, 0); color: red;")
            else:
                self.lbl_info.setStyleSheet("background-color: rgba(0, 85, 0, 0); color: yellow;")
            
            self.lbl_info.setText(info_text)
        QCoreApplication.processEvents()

    def _load_picture(self, image):
        if isinstance(image, QPixmap):
            img = image
        elif isinstance(image, int):
            db_media = db_media_cls.Media(self._stt, image)
            img = QPixmap()
            img.load(db_media.media_file)
        elif image is None:
            img = QPixmap()
            img.load(self.getv("auto_add_image_frame_lbl_pic_file_path"))

        size = self.lbl_pic.size()
        if img.height() > size.height() or img.width() > size.width():
            img = img.scaled(size, Qt.KeepAspectRatio)
        self.lbl_pic.setPixmap(img)

    def update_progress(self, text: str = None):
        if text is None:
            self.lbl_title.setText(self.getl("auto_add_image_frame_lbl_title_text"))
        else:
            self.lbl_title.setText(text)

    def _define_widgets(self):
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_info: QLabel = self.findChild(QLabel, "lbl_info")
        self.btn_exit: QPushButton = self.findChild(QPushButton, "btn_exit")

        self._define_widgets_text()

    def _define_widgets_text(self):
        self.lbl_pic.setText("")
        
        img = QPixmap()
        img.load(self.getv("auto_add_image_frame_lbl_pic_file_path"))
        self._load_picture(img)
        
        self.lbl_pic.setPixmap

        self.lbl_title.setText(self.getl("auto_add_image_frame_lbl_title_text"))
        
        self.lbl_info.setText(self.getl("auto_add_image_frame_lbl_info_start_text"))

        self.btn_exit.setText(self.getl("auto_add_image_frame_btn_exit_text"))
        self.btn_exit.setToolTip(self.getl("auto_add_image_frame_btn_exit_tt"))


class PictureInfo(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, media_id: int, *args, **kwargs):
        self._dont_clear_menu = False
        self._data_loaded = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._media_id = media_id
        self._dont_clear_menu = False
        self._clip: Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("picture_info_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        db_media = db_media_cls.Media(self._stt)
        if db_media.is_media_exist(self._media_id):
            db_media.load_media(self._media_id)
            self._image_file = db_media.media_file
            self._populate_widgets()
        else:
            self._error_no_media()
            self._media_id = None
            self._image_file = None

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_delete.clicked.connect(self.btn_delete_click)
        self.btn_update.clicked.connect(self.btn_update_click)
        self.btn_open_default.clicked.connect(self.btn_open_default_click)
        self.btn_close.clicked.connect(self.btn_close_click)
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.lst_used.mouseReleaseEvent = self.lst_used_mouse_release
        self.lst_used.itemDoubleClicked.connect(self.lst_used_mouse_double_click)
        self.txt_name.textChanged.connect(self.txt_name_text_changed)
        self.txt_desc.textChanged.connect(self.txt_desc_text_changed)

        self._data_loaded = True
        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["PictureInfo"])
        self._resize_widgets()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_name)
        self.widget_handler.add_TextBox(self.txt_desc)

        # Add Selection Widgets

        # ADD Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_used)

        self.widget_handler.activate()

    def btn_close_click(self):
        self.close()

    def lst_used_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self._show_list_menu()

    def lst_used_mouse_double_click(self, e: QtGui.QMouseEvent):
        if self.lst_used.currentItem() is None:
            return

        item_data = self.lst_used.currentItem().data(Qt.UserRole).lower()

        main_win_dict = {
            "name": "pic_info"
        }
        if item_data.find("block") >= 0:
            main_win_dict["action"] = "open_block"
            main_win_dict["id"] = int(item_data.split(" ")[-1])
            self.get_appv("main_win").events(main_win_dict)
        if item_data.find("def") >= 0:
            main_win_dict["action"] = "open_def"
            main_win_dict["id"] = int(item_data.split(" ")[-1])
            self.get_appv("main_win").events(main_win_dict)

    def _show_list_menu(self):
        if self.lst_used.currentItem() is None:
            return
        
        item_data_list = []
        for i in range(self.lst_used.count()):
            item_data = self.lst_used.item(i).data(Qt.UserRole).lower()
            if item_data.find("block") >= 0:
                item_data_list.append(int(item_data.split(" ")[-1]))
        
        item_data = self.lst_used.currentItem().data(Qt.UserRole).lower()
        
        menu_dict = {
            "position": QCursor.pos(),
            "items":[
                [10, self.getl("pic_info_lst_menu_open_text").replace("#1", self.lst_used.currentItem().text()), self.getl("pic_info_lst_menu_open_tt"), True, [], None]
            ]
        }
        
        if item_data.find("block") >= 0 and len(item_data_list) > 1:
            menu_dict["items"].append([20, self.getl("pic_info_lst_menu_open_all_text").replace("#1", str(len(item_data_list))), self.getl("pic_info_lst_menu_open_all_tt"), True, [], None])
        
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        ContextMenu(self._stt, self)
        
        main_win_dict = {
            "name": "pic_info"
        }
        
        if self.get_appv("menu")["result"] == 10:
            if item_data.find("block") >= 0:
                main_win_dict["action"] = "open_block"
                main_win_dict["id"] = int(item_data.split(" ")[-1])
                self.get_appv("main_win").events(main_win_dict)
            if item_data.find("def") >= 0:
                main_win_dict["action"] = "open_def"
                main_win_dict["id"] = int(item_data.split(" ")[-1])
                self.get_appv("main_win").events(main_win_dict)
        if self.get_appv("menu")["result"] == 20:
            main_win_dict["action"] = "open_block"
            main_win_dict["id"] = item_data_list
            self.get_appv("main_win").events(main_win_dict)

    def lbl_pic_mouse_press(self, e:QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self._show_context_menu()

    def _show_context_menu(self):
        disab = []
        if self._image_file is None:
            disab = [10, 20]
        if self._clip.is_clip_empty():
            disab.append(30)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "items":[
                [
                    10,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    20,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    30,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        ContextMenu(self._stt, self)
        if self.get_appv("menu")["result"] == 70:
            self._clip.copy_to_clip(self._media_id)
        if self.get_appv("menu")["result"] == 80:
            self._clip.copy_to_clip(self._media_id, add_to_clip=True)
        if self.get_appv("menu")["result"] == 90:
            self._clip.clear_clip()

    def btn_open_default_click(self):
        try:
            os.startfile(self._image_file.replace("/", "\\"))
            UTILS.LogHandler.add_log_record("#1: Image opened with default application.", ["PictureInfo"])
        except Exception as e:
            UTILS.LogHandler.add_log_record("#1: Error in attempt to open image with default application.\n#2", ["PictureInfo", str(e)])
            
    def _error_no_media(self):
        data_dict = {
            "title": self.getl("picture_info_msg_no_media_title"),
            "text": self.getl("picture_info_msg_no_media_text").replace("#1", str(self._media_id))
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, data_dict=data_dict, app_modal=False)

    def txt_name_text_changed(self):
        self.btn_update.setEnabled(True)

    def txt_desc_text_changed(self):
        self.btn_update.setEnabled(True)

    def btn_delete_click(self):
        if self._media_id is None:
            return

        UTILS.LogHandler.add_log_record("#1: About to delete image (ID=#2).", ["PictureInfo", self._media_id])
        db_media = db_media_cls.Media(self._stt, self._media_id)

        if not db_media.is_safe_to_delete(self._media_id):
            data_dict = {
                "title": self.getl("picture_browse_msg_cant_delete_title"),
                "text": self.getl("picture_browse_msg_cant_delete_text")
            }
            UTILS.LogHandler.add_log_record("#1: Image cannot be deleted. Reason: #2", ["PictureInfo", "In use in some block or definition"])
            self._dont_clear_menu = True
            MessageInformation(self._stt, self, data_dict=data_dict, app_modal=True)
            return

        data_dict = {
            "title": self.getl("picture_browse_msg_confirm_title"),
            "text": self.getl("picture_browse_msg_confirm_text"),
            "icon_path": db_media.media_file,
            "position": "center_parent",
            "buttons": [
                [1, self.getl("btn_yes"), "", None, True],
                [2, self.getl("btn_no"), "", None, True],
                [3, self.getl("btn_cancel"), "", None, True]
            ]
        }
        MessageQuestion(self._stt, self, data_dict, app_modal=True)
        if data_dict["result"] != 1:
            return

        db_media.delete_media(self._media_id)
        data_dict = {
            "title": "",
            "text": self.getl("picture_browse_msg_data_deleted_text"),
            "timer": 2000
        }
        self.hide()
        UTILS.LogHandler.add_log_record("#1: Image deleted.", ["PictureInfo"])
        Notification(self._stt, self._parent_widget, data_dict=data_dict)
        self.close()

    def btn_update_click(self):
        if self._media_id is None:
            return
        
        obj_image = Image(self._stt, image_id=self._media_id)
        obj_image.ImageName = self.txt_name.text()
        obj_image.ImageDescription = self.txt_desc.toPlainText()
        obj_image.save()

        self.btn_update.setEnabled(False)
        
        UTILS.LogHandler.add_log_record("#1: Image updated. (ID=#2)", ["PictureInfo", self._media_id])
        data_dict = {
            "title": "",
            "text": self.getl("picture_browse_msg_data_updated_text"),
            "timer": 2000
        }
        Notification(self._stt, self, data_dict=data_dict)

    def _populate_widgets(self):
        if not self._media_id:
            self.btn_delete.setEnabled(False)
            self.btn_open_default.setEnabled(False)
            self.btn_update.setEnabled(False)
            return
        
        db_media = db_media_cls.Media(self._stt, self._media_id)

        self.txt_name.setText(db_media.media_name)
        self.txt_desc.setText(db_media.media_description)
        self.lbl_file_val.setText(self.getl("pic_info_lbl_file_val_text").replace("#1", db_media.media_file))
        self.lbl_src_val.setText(self.getl("pic_info_lbl_src_val_text").replace("#1", db_media.media_http))

        file_util = FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt, os.path.abspath(db_media.media_file))
        date_util = DateTime(self._stt)
        date_long = date_util.get_long_date(file_info.created()[:11])
        tooltip = file_util.get_file_tooltip_text(os.path.abspath(db_media.media_file))
        before_days = date_util.get_date_difference(file_info.created()[:11])
        before_days = UTILS.DateTime.DateTimeObject(UTILS.DateTime.DateTime.now()) - UTILS.DateTime.DateTimeObject(file_info.created())
        before_days = before_days.total_days

        self.lbl_created.setText(f'{self.getl("pic_info_lbl_created_text")}<span style="color: {self.getv("pic_info_lbl_created_date_color")}";>{date_long}</span><br>{self.getl("pic_info_lbl_created_before_days_text").replace("#1", str(before_days))}')
        self.lbl_created.setToolTip(tooltip)
        
        self._populate_image_lbl()
        self._populate_used_list()

    def _populate_used_list(self, media_id: int = None):
        if media_id == None:
            media_id = self._media_id
        
        if media_id == None:
            return
        
        db_media = db_media_cls.Media(self._stt, media_id)
        self.lst_used.clear()

        blocks_ids = db_media.get_block_ids_that_use_media(self._media_id)
        defs_ids = db_media.get_definition_ids_that_use_media(self._media_id)

        if blocks_ids:
            db_rec = db_record_cls.Record(self._stt)
            for i in blocks_ids:
                db_rec.load_record(i)
                item = QListWidgetItem()
                txt = self.getl("picture_info_lst_used_item_block_text")
                txt += db_rec.RecordDate
                if db_rec.RecordName:
                    txt += f" - {db_rec.RecordName}"
                item.setText(txt)
                item.setData(Qt.UserRole, f"BLOCK: {db_rec.RecordID}")
                self.lst_used.addItem(item)

        if defs_ids:
            db_def = db_definition_cls.Definition(self._stt)
            for i in defs_ids:
                db_def.load_definition(i)
                item = QListWidgetItem()
                txt = self.getl("picture_info_lst_used_item_definition_text")
                txt += db_def.definition_name
                item.setText(txt)
                item.setData(Qt.UserRole, f"DEFINITION: {db_def.definition_id}")
                self.lst_used.addItem(item)

        if self.lst_used.count():
            self.lst_used.setCurrentRow(0)
        else:
            item = QListWidgetItem()
            txt = self.getl("picture_info_lst_used_item_no_data_text")
            item.setText(txt)
            item.setData(Qt.UserRole, f"NOT_USED")
            self.lst_used.addItem(item)

    def _populate_image_lbl(self):
        image_file = self._image_file
        
        img = QPixmap()
        img.load(image_file)

        size = self.lbl_pic.size()
        if img.height() > size.height() or img.width() > size.width():
            img = img.scaled(size, Qt.KeepAspectRatio)
        
        self.lbl_pic.setPixmap(img)

    def _load_win_position(self):
        if "picture_info_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("picture_info_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        if self._data_loaded:
            self._populate_used_list()
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "picture_info_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("picture_info_win_geometry", {}, save_to_file=True)

        g = self.get_appv("picture_info_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["PictureInfo"])
        UTILS.DialogUtility.on_closeEvent(self)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._resize_widgets()
        return super().resizeEvent(a0)

    def _resize_widgets(self):
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.frm_info.move(w - 510, h - 570)

        self.btn_close.move(w - 100, h - 30)
        
        self.lbl_title.resize(w, self.lbl_title.height())
        self.lbl_created.move(10, h - 40)
        self.lbl_created.resize(self.lbl_pic.width(), self.lbl_created.height())

        self.lbl_pic.resize(w - 520, h - 90)
        if self._image_file:
            self._populate_image_lbl()

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_created: QLabel = self.findChild(QLabel, "lbl_created")

        self.frm_info: QFrame = self.findChild(QFrame, "frm_info")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_file_val: QLabel = self.findChild(QLabel, "lbl_file_val")
        self.lbl_desc: QLabel = self.findChild(QLabel, "lbl_desc")
        self.lbl_src_val: QLabel = self.findChild(QLabel, "lbl_src_val")
        self.txt_name: QLineEdit = self.findChild(QLineEdit, "txt_name")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.btn_open_default: QPushButton = self.findChild(QPushButton, "btn_open_default")
        self.btn_delete: QPushButton = self.findChild(QPushButton, "btn_delete")
        self.btn_update: QPushButton = self.findChild(QPushButton, "btn_update")

        self.frm_used: QFrame = self.findChild(QFrame, "frm_used")
        self.lbl_used: QLabel = self.findChild(QLabel, "lbl_used")
        self.lst_used: QListWidget = self.findChild(QListWidget, "lst_used")

        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("pic_info_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("pic_info_lbl_title_tt"))

        self.lbl_name.setText(self.getl("pic_info_lbl_name_text"))
        self.lbl_name.setToolTip(self.getl("pic_info_lbl_name_tt"))

        self.lbl_file_val.setText(self.getl("pic_info_lbl_file_val_text"))
        self.lbl_file_val.setToolTip(self.getl("pic_info_lbl_file_val_tt"))

        self.lbl_desc.setText(self.getl("pic_info_lbl_desc_text"))
        self.lbl_desc.setToolTip(self.getl("pic_info_lbl_desc_tt"))

        self.lbl_src_val.setText(self.getl("pic_info_lbl_src_val_text"))
        self.lbl_src_val.setToolTip(self.getl("pic_info_lbl_src_val_tt"))

        self.txt_name.setPlaceholderText(self.getl("pic_info_txt_name_placeholder"))
        self.txt_desc.setPlaceholderText(self.getl("pic_info_txt_desc_placeholder"))

        self.btn_open_default.setText(self.getl("pic_info_btn_open_default_text"))
        self.btn_open_default.setToolTip(self.getl("pic_info_btn_open_default_tt"))

        self.btn_delete.setText(self.getl("pic_info_btn_delete_text"))
        self.btn_delete.setToolTip(self.getl("pic_info_btn_delete_tt"))

        self.btn_update.setText(self.getl("pic_info_btn_update_text"))
        self.btn_update.setToolTip(self.getl("pic_info_btn_update_tt"))

        self.lbl_used.setText(self.getl("pic_info_lbl_used_text"))
        self.lbl_used.setToolTip(self.getl("pic_info_lbl_used_tt"))

        self.btn_close.setText(self.getl("pic_info_btn_close_text"))
        self.btn_close.setToolTip(self.getl("pic_info_btn_close_tt"))

        self.lbl_created.setText("")

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["PictureInfo"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = True):
        self._define_picture_info_win_apperance()

        self._define_labels_apperance(self.lbl_title, "picture_browse_lbl_title")
        self._define_labels_apperance(self.lbl_name, "picture_browse_lbl_name")
        self._define_labels_apperance(self.lbl_desc, "picture_browse_lbl_desc")
        self._define_labels_apperance(self.lbl_file_val, "picture_browse_lbl_file_val")
        self._define_labels_apperance(self.lbl_src_val, "picture_browse_lbl_src_val")
        self._define_labels_apperance(self.lbl_created, "pic_info_lbl_created")

        self._define_buttons_apperance(self.btn_update, "picture_browse_btn_update")
        if not settings_updated:
            self.btn_update.setEnabled(False)
        self._define_buttons_apperance(self.btn_open_default, "picture_browse_btn_update")
        self._define_buttons_apperance(self.btn_delete, "picture_browse_btn_delete")

        self._define_buttons_apperance(self.btn_close, "picture_browse_btn_close")

        self._define_text_box_apperance(self.txt_name, "picture_browse_txt_name")
        self._define_text_box_apperance(self.txt_desc, "picture_browse_txt_desc")

        self._define_labels_apperance(self.lbl_used, "picture_info_lbl_used")

        self.lst_used.setStyleSheet(self.getv("picture_info_lst_used_stylesheet"))

        self.lbl_pic.setStyleSheet(self.getv("picture_info_lbl_pic_stylesheet"))

    def _define_picture_info_win_apperance(self):
        self.setStyleSheet(self.getv("picture_info_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("picture_info_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.getl("picture_info_win_title_text"))
        self.setMinimumSize(620, 620)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))


class SilentPictureAdd():
    """ Loads image from clipboard and saves in database.
    Usage:
        init class
        call 'add_image' method
            if image is found and successfuly saved returns image ID, else returns None
    """
    def __init__(self, settings: settings_cls.Settings):

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.clipboard_image_source = "N/A"

    def add_image(self, source: str = None) -> int:
        """Adding picture from clipboard
        If success returns image ID, else returns None
        """
        if source is None:
            result = self._silent_loader()
            return result
        
        self.clipboard_image_source = source
        result = self._silent_load_from_source(source)

        if result:
            media_id = self._silent_save_image(result, source)
            if media_id:
                return media_id
            else:
                return None
        else:
            return None

    def _silent_loader(self) -> int:
        mime_data = self.get_appv("clipboard").mimeData()
        result = None
        file_source = ""

        if mime_data.hasText():
            clip_text = self.get_appv("clipboard").text()
            file_source = clip_text
            self.clipboard_image_source = clip_text
            result = self._silent_load_from_source(clip_text)

        if mime_data.hasImage() and result is None:
            self.clipboard_image_source = "Clipboard Image"
            file_source = "http_clipboard" + str(time.time_ns())
            result = self._silent_load_from_clipboard()
        
        if result:
            media_id = self._silent_save_image(result, file_source)
            if media_id:
                return media_id
            else:
                return None
        else:
            return None

    def _silent_load_from_source(self, source: str) -> QPixmap:
        file_path = source

        error_text = ""
        img = QPixmap()

        if file_path.lower().find("http") >= 0:
            try:
                web_image = urllib.request.urlopen(file_path).read()
                result = img.loadFromData(web_image)
            except Exception as e:
                result = False
        else:            
            try:
                result = img.load(file_path)
            except Exception as e:
                result = False

        if result:
            return img
        else:
            return None

    def _silent_load_from_clipboard(self) -> QPixmap:
        img = QPixmap()
        try:
            result = img.convertFromImage(self.get_appv("clipboard").image())
        except Exception as e:
            result = None

        if result:
            return img
        else:
            return None

    def _silent_save_image(self, image: QPixmap, source: str) -> int:
        media_dict = {
            "name": "",
            "description": "",
            "http": source
        }

        db_media = db_media_cls.Media(self._stt)
        last_row_id = db_media.add_media(media_dict)

        user_set = self.get_appv("user").settings_path
        file_name, _ = os.path.split(user_set)
        if file_name:
            file_name = file_name + "/"
        file_name = file_name + str(self.get_appv("user").ActiveUserID)
        file_name = file_name + "images/"

        file_name = file_name + str(last_row_id) + "."

        if image.hasAlpha() or image.hasAlphaChannel():
            file_name += "png"
            self._create_directory_structure(file_name)
            image.save(file_name, "png")
        else:
            file_name += "jpg"
            self._create_directory_structure(file_name)
            image.save(file_name, "jpg")

        media_dict = {
            "file": file_name
        }
        db_media.update_media(last_row_id, media_dict)

        obj_image = Image(self._stt, image_id=last_row_id)
        obj_image.add_to_image_list()

        self.get_appv("log").write_log(f"SilentPictureAdd. Picture added. Source: {source}")

        return last_row_id

    def _create_directory_structure(self, file_path: str):
        directory = os.path.split(file_path)
        directory = directory[0]
        if not directory:
            return
        if not os.path.isdir(directory):
            os.mkdir(directory)


class PictureAdd(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, result: list, *args, **kwargs):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._last_file_name = ""
        self._loaded_image = None
        self._result = result
        self._txt_text = ""
        self._img_pixmap_original = None
        self._ignore_txt_file_text_change_event = False

        self._pic_name = ""
        self._pic_desc = ""

        # Load GUI
        uic.loadUi(self.getv("picture_add_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.txt_file.textChanged.connect(self._txt_file_text_changed)
        self.btn_file.clicked.connect(self._btn_file_click)
        self.btn_cancel.clicked.connect(self._btn_cancel_click)
        self.btn_add.clicked.connect(self._bnt_add_click)
        self.btn_show.clicked.connect(self._btn_show_click)
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.lbl_pic.mouseDoubleClickEvent = self.lbl_pic_mouse_double_click
        self.mousePressEvent = self._self_mouse_press
        self.mouseDoubleClickEvent = self._self_mouse_double_click
        self.keyPressEvent = self._key_press_event

        self.show()

        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["PictureAdd"])
        
        if self.chk_auto_load.isChecked():
            self.lbl_pic_mouse_double_click(None)
        
        self.exec_()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()
        btn_file: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(self.btn_file, return_none_if_not_found=True)
        if btn_file:
            btn_file.properties.allow_bypass_leave_event = False
        else:
            UTILS.TerminalUtility.WarningMessage("All Buttons are added but btn_file not found !")

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets
        self.widget_handler.add_Selection_Widget(self.chk_auto_load)

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _key_press_event(self, e: QtGui.QKeyEvent):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self._bnt_add_click()

    def _self_mouse_press(self, e):
        if e.button() == Qt.RightButton:
            self._show_context_menu()
        return super().mousePressEvent(e)

    def _self_mouse_double_click(self, e):
        mime_data = self.get_appv("clipboard").mimeData()
        if mime_data.hasText():
            self.txt_file.setText(self.get_appv("clipboard").text())

    def _create_directory_structure(self, file_path: str):
        directory = os.path.split(file_path)
        directory = directory[0]
        if not directory:
            return
        if not os.path.isdir(directory):
            os.mkdir(directory)

    def lbl_pic_mouse_double_click(self, e):
        mime_data = self.get_appv("clipboard").mimeData()
        if mime_data.hasText():
            self._ignore_txt_file_text_change_event = True
            self.txt_file.setText(self.get_appv("clipboard").text())
            result = self._show_image(self.txt_file.text())
            if not result:
                mime_data = self.get_appv("clipboard").mimeData()
                if mime_data.hasImage():
                    self._load_from_clipboard()
        elif mime_data.hasImage():
            self._load_from_clipboard()

    def lbl_pic_mouse_press(self, e):
        if e.button() == Qt.RightButton:
            self._show_context_menu()

    def _show_context_menu(self):
        mime_data = self.get_appv("clipboard").mimeData()
        if mime_data.hasImage():
            disabled = []
        else:
            disabled = [3]

        if self._loaded_image:
            menu_dict = {
                "position": QCursor.pos(),
                "disabled": disabled,
                "items": [
                    [
                        1,
                        self.getl("picture_add_cm_name_text"),
                        self.getl("picture_add_cm_name_tt"),
                        True,
                        [],
                        None
                    ],
                    [
                        2,
                        self.getl("picture_add_cm_desc_text"),
                        self.getl("picture_add_cm_desc_tt"),
                        True,
                        [],
                        None
                    ],
                    [
                        3,
                        self.getl("picture_add_cm_load_clip_text"),
                        self.getl("picture_add_cm_load_clip_tt"),
                        True,
                        [],
                        None
                    ]
                ]
            }
            self.set_appv("menu", menu_dict)
            self._dont_clear_menu = True
            ContextMenu(self._stt, self)
            
            if self.get_appv("menu")["result"] == 1:
                data_dict = {
                    "name": "block_input_box_name",
                    "title": self.getl("picture_add_input_name_title"),
                    "position": QCursor().pos()
                }
                self._dont_clear_menu = True
                InputBoxSimple(self._stt, self, data_dict)
                if data_dict["result"]:
                    self._pic_name = data_dict["result"]
            elif self.get_appv("menu")["result"] == 2:
                data_dict = {
                    "name": "block_input_box_name",
                    "title": self.getl("picture_add_input_desc_title"),
                    "position": QCursor().pos(),
                    "one_line": False
                }
                self._dont_clear_menu = True
                InputBoxSimple(self._stt, self, data_dict)
                if data_dict["result"]:
                    self._pic_desc = data_dict["result"]
            elif self.get_appv("menu")["result"] == 3:
                self._load_from_clipboard()
        else:
            menu_dict = {
                "position": QCursor.pos(),
                "disabled": disabled,
                "items": [
                    [
                        3,
                        self.getl("picture_add_cm_load_clip_text"),
                        self.getl("picture_add_cm_load_clip_tt"),
                        True,
                        [],
                        None
                    ]
                ]
            }
            self.set_appv("menu", menu_dict)
            self._dont_clear_menu = True
            ContextMenu(self._stt, self)
            if self.get_appv("menu")["result"] == 3:
                self._load_from_clipboard()

    def _load_from_clipboard(self):
        img = QPixmap()
        result = img.convertFromImage(self.get_appv("clipboard").image())
        file_path = "http_clipboard" + str(time.time_ns())

        if result:
            self._img_pixmap_original = QPixmap()
            self._img_pixmap_original.convertFromImage(self.get_appv("clipboard").image())
            self.lbl_pic.setText("")
            size = self.lbl_pic.maximumSize()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)
            self._loaded_image = file_path
            self.btn_add.setEnabled(True)
        else:
            self.lbl_pic.setText(self.getl("picture_add_no_clip_image"))
        QCoreApplication.processEvents()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.lbl_pic.setMaximumSize(self.contentsRect().width(), self.contentsRect().height() - 220)
        return super().resizeEvent(a0)

    def _btn_show_click(self):
        self._show_image(self.txt_file.text())

    def _show_image(self, image_path: str = None) -> bool:
        self.lbl_pic.setText(self.getl("please_wait"))
        QCoreApplication.processEvents()

        if image_path:
            file_path = image_path
        else:
            file_path = self.txt_file.text()
        
        error_text = ""
        if file_path.lower().find("http") >= 0:
            try:
                web_image = urllib.request.urlopen(file_path).read()
                img = QPixmap()
                result = img.loadFromData(web_image)
                self._img_pixmap_original = QPixmap()
                self._img_pixmap_original.loadFromData(web_image)
            except Exception as e:
                error_text = str(e)
                result = False
        else:            
            img = QPixmap()
            result = img.load(file_path)
            self._img_pixmap_original = QPixmap()
            self._img_pixmap_original.load(file_path)

        if result:
            self.lbl_pic.setText("")
            size = self.lbl_pic.maximumSize()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)
            self._loaded_image = file_path
            self.btn_add.setEnabled(True)
            return True
        else:
            self._loaded_image = None
            self.lbl_pic.setText(f'{self.getl("picture_add_no_loaded_pic_text")}\n{error_text}')
            self.btn_add.setEnabled(False)
            return False
    
    def _bnt_add_click(self):
        if self._loaded_image:
            media_dict = {
                "name": self._pic_name,
                "description": self._pic_desc
            }
            if self._loaded_image.lower().find("http") < 0:
                media_dict["http"] = f"http:Local File: {self._loaded_image}"
                db_media = db_media_cls.Media(self._stt)
                last_row_id = db_media.add_media(media_dict)
            else:
                media_dict["http"] = self._loaded_image
                db_media = db_media_cls.Media(self._stt)
                last_row_id = db_media.add_media(media_dict)

            img = self.lbl_pic.pixmap()
            user_set = self.get_appv("user").settings_path
            file_name, _ = os.path.split(user_set)
            if file_name:
                file_name = file_name + "/"
            file_name = file_name + str(self.get_appv("user").ActiveUserID)
            file_name = file_name + "images/"

            file_name = file_name + str(last_row_id) + "."
            if img.hasAlpha() or img.hasAlphaChannel():
                file_name += "png"
                self._create_directory_structure(file_name)
                if self._img_pixmap_original is None:
                    img.save(file_name, "png")
                else:
                    self._img_pixmap_original.save(file_name, "png")
            else:
                file_name += "jpg"
                self._create_directory_structure(file_name)
                if self._img_pixmap_original is None:
                    img.save(file_name, "jpg")
                else:
                    self._img_pixmap_original.save(file_name, "jpg")
            media_dict = {
                "file": file_name
            }
            db_media.update_media(last_row_id, media_dict)

            obj_image = Image(self._stt, image_id=last_row_id)
            obj_image.add_to_image_list()

            self._result.append(last_row_id)
            UTILS.LogHandler.add_log_record("#1: Image added.", ["PictureAdd"])
        self.close()

    def _btn_cancel_click(self):
        self.close()

    def _btn_file_click(self):
        file = FileDialog()
        result = file.show_dialog(directory=self._last_file_name)
        if result:
            self._last_file_name = result
            self.txt_file.setText(result)

    def _txt_file_text_changed(self):
        if self._ignore_txt_file_text_change_event:
            self._ignore_txt_file_text_change_event = False
            return
        
        if self.txt_file.text():
            self.btn_show.setEnabled(True)
            if abs(len(self.txt_file.text()) - len(self._txt_text)) > 1:
                self._btn_show_click()
        else:
            self.btn_show.setEnabled(False)
        self._txt_text = self.txt_file.text()

    def _load_win_position(self):
        if "add_picture_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("add_picture_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self._last_file_name = g["last_file_name"]
            self.chk_auto_load.setChecked(g.get("auto_load", False))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "add_picture_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("add_picture_win_geometry", {}, save_to_file=True)

        g = self.get_appv("add_picture_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["last_file_name"] = self._last_file_name
        g["auto_load"] = self.chk_auto_load.isChecked()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["PictureAdd"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_file: QLabel = self.findChild(QLabel, "lbl_file")
        self.txt_file: QLineEdit = self.findChild(QLineEdit, "txt_file")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.btn_file: QPushButton = self.findChild(QPushButton, "btn_file")
        self.btn_add: QPushButton = self.findChild(QPushButton, "btn_add")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_show: QPushButton = self.findChild(QPushButton, "btn_show")
        self.chk_auto_load: QCheckBox = self.findChild(QCheckBox, "chk_auto_load")
        self.gridLayout: QGridLayout = self.findChild(QGridLayout, "gridLayout")
        self.setLayout(self.gridLayout)

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("picture_add_win_title_text"))
        
        self.lbl_title.setText(self.getl("picture_add_title_text"))
        self.lbl_title.setToolTip(self.getl("picture_add_title_tt"))
        
        self.lbl_file.setText(self.getl("picture_add_lbl_file_text"))
        self.lbl_file.setToolTip(self.getl("picture_add_lbl_file_tt"))

        self.btn_file.setText(self.getl("picture_add_btn_file_text"))
        self.btn_file.setToolTip(self.getl("picture_add_btn_file_tt"))

        self.btn_add.setText(self.getl("picture_add_btn_add_text"))
        self.btn_add.setToolTip(self.getl("picture_add_btn_add_tt"))

        self.btn_cancel.setText(self.getl("picture_add_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("picture_add_btn_cancel_tt"))

        self.btn_show.setText(self.getl("picture_add_btn_show_text"))
        self.btn_show.setToolTip(self.getl("picture_add_btn_show_tt"))

        self.chk_auto_load.setText(self.getl("picture_add_chk_auto_load_text"))
        self.chk_auto_load.setToolTip(self.getl("picture_add_chk_auto_load_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["PictureAdd"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self._define_add_picture_win_apperance()
        self._define_labels_apperance(self.lbl_title, "picture_add_title")
        self._define_labels_apperance(self.lbl_file, "picture_add_lbl_file")
        
        self._define_buttons_apperance(self.btn_file, "picture_add_btn_file")
        self._define_buttons_apperance(self.btn_show, "picture_add_btn_show")
        if not settings_updated:
            self.btn_show.setEnabled(False)
        self._define_buttons_apperance(self.btn_add, "picture_add_btn_add")
        if not settings_updated:
            self.btn_add.setEnabled(False)
        self._define_buttons_apperance(self.btn_cancel, "picture_add_btn_cancel")

        self._define_text_box_apperance(self.txt_file, "picture_add_txt_file")

        self.chk_auto_load.setStyleSheet(self.getv("picture_add_chk_auto_load_stylesheet"))

    def _define_add_picture_win_apperance(self):
        self.setStyleSheet(self.getv("picture_add_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("picture_add_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))
        label.setVisible(self.getv(f"{name}_visible"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))


class PictureView(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, media_ids: list, start_with_media_id: int = None, application_modal: bool = True,*args, **kwargs):
        self._dont_clear_menu = False
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)
        self.setMouseTracking(True)

        # Define other variables
        self._resize_mode = False
        self._parent_widget = parent_widget
        self._media_ids = media_ids
        self._clip: Clipboard = self.get_appv("cb")
        if start_with_media_id:
            for idx, item in enumerate(self._media_ids):
                if item == start_with_media_id:
                    self._pic_counter = idx
                    break
            else:
                self._pic_counter = None
        else:
            self._pic_counter = None

        # Load GUI
        uic.loadUi(self.getv("picture_view_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        if len(self._media_ids) < 1:
            self._no_data_msg()
            self.btn_next.setEnabled(False)
            self.btn_save.setEnabled(False)
        elif len(self._media_ids) == 1:
            self.btn_next.setEnabled(False)

        self._populate_widgets()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_cancel.clicked.connect(self._btn_cancel_click)
        self.btn_next.clicked.connect(self._btn_next_click)
        self.btn_save.clicked.connect(self._btn_save_click)
        self.txt_name.textChanged.connect(self._txt_name_text_changed)
        self.txt_desc.textChanged.connect(self._txt_desc_text_changed)
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        
        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["PictureView"])
        if application_modal:
            self.exec_()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_name])
        handle_dialog.properties.window_drag_enabled_with_body = True

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_name)
        self.widget_handler.add_TextBox(self.txt_desc)

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def lbl_pic_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            if self._pic_counter is None:
                if self._media_ids:
                    self._pic_counter = 0
                else:
                    return

            media_id = self._media_ids[self._pic_counter]
            db_media = db_media_cls.Media(self._stt, media_id=media_id)

            file = FileDialog()
            file_icon, file_name = file.get_default_external_icon_and_app(db_media.media_file)
            disab = []
            if self._clip.is_clip_empty():
                disab.append(30)

            menu_dict = {
                "position": QCursor.pos(),
                "separator": [30],
                "disabled": disab,
                "items": [
                    [
                        10,
                        self.getl("image_menu_copy_text"),
                        self.getl("image_menu_copy_tt"),
                        True,
                        [],
                        self.getv("copy_icon_path")
                    ],
                    [
                        20,
                        self.getl("image_menu_add_to_clip_text"),
                        self.getl("image_menu_add_to_clip_tt"),
                        True,
                        [],
                        self.getv("copy_icon_path")
                    ],
                    [
                        30,
                        self.getl("image_menu_clear_clipboard_text"),
                        self._clip.get_tooltip_hint_for_clear_clipboard(),
                        True,
                        [],
                        self.getv("clear_clipboard_icon_path")
                    ],
                    [
                        40,
                        self.getl("picture_view_menu_open_with_external_text"),
                        self.getl("picture_view_menu_open_with_external_tt") + file_name,
                        True,
                        [],
                        file_icon
                    ]
                ]
            }
            self._dont_clear_menu = True
            self.set_appv("menu", menu_dict)
            ContextMenu(self._stt, self)
            if self.get_appv("menu")["result"] == 10:
                self._clip.copy_to_clip(int(self.lbl_pic.objectName()))
            elif self.get_appv("menu")["result"] == 20:
                self._clip.copy_to_clip(int(self.lbl_pic.objectName()), add_to_clip=True)
            elif self.get_appv("menu")["result"] == 30:
                self._clip.clear_clip()
            elif self.get_appv("menu")["result"] == 40:
                os.startfile(db_media.media_file.replace("/", "\\"))

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _txt_name_text_changed(self):
        self.btn_save.setEnabled(True)

    def _txt_desc_text_changed(self):
        self.btn_save.setEnabled(True)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.lbl_pic.resize(self.width() - 20, self.height() - 220)
        self.lbl_desc.move(self.lbl_desc.pos().x(), self.height() - 160)
        self.lbl_desc.resize(self.width() - 20, self.lbl_desc.height())
        self.txt_desc.move(self.txt_desc.pos().x(), self.height() - 140)
        self.txt_desc.resize(self.width() - 20, self.txt_desc.height())
        self.txt_name.resize(self.contentsRect().width() - self.txt_name.pos().x() - 10, self.txt_name.height())
        self.btn_next.move(self.width() - 380, self.height() - 30)
        self.btn_save.move(self.width() - 250, self.height() - 30)
        self.btn_cancel.move(self.width() - 120, self.height() - 30)
        if self._pic_counter is not None:
            self._show_picture()
        return super().resizeEvent(a0)

    def _populate_widgets(self):
        if self._pic_counter is None:
            if self._media_ids:
                self._pic_counter = 0
            else:
                return
        self._show_picture()

        media_id = self._media_ids[self._pic_counter]
        db_media = db_media_cls.Media(self._stt, media_id=media_id)
        if db_media.media_name:
            self.txt_name.setText(db_media.media_name)
        else:
            self.txt_name.setPlaceholderText(db_media.media_file)
            self.txt_name.setText("")
        if db_media.media_description:
            self.txt_desc.setText(db_media.media_description)
        else:
            self.txt_desc.setPlaceholderText(db_media.media_http)
            self.txt_desc.setText("")

    def _show_picture(self):
        media_id = self._media_ids[self._pic_counter]
        db_media = db_media_cls.Media(self._stt, media_id=media_id)

        self.lbl_pic.setText(self.getl("please_wait"))

        img = QPixmap()
        result = img.load(db_media.media_file)

        if result:
            self.lbl_pic.setText("")
            size = self.lbl_pic.size()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)
        else:
            self.lbl_pic.setText(f'{self.getl("picture_add_no_loaded_pic_text")}\n{db_media.media_file}')
            self.btn_save.setEnabled(False)

    def _no_data_msg(self):
        msg_dict = {
            "title": self.getl("picture_view_no_data_msg_title"),
            "text": self.getl("picture_view_no_data_msg_text")
        }
        self.show()
        QCoreApplication.processEvents()
        MessageInformation(self._stt, self._parent_widget, msg_dict, app_modal=True)

    def _btn_save_click(self):
        obj_image = Image(self._stt, image_id=self._media_ids[self._pic_counter])
        obj_image.ImageName = self.txt_name.text()
        obj_image.ImageDescription = self.txt_desc.toPlainText()
        obj_image.save()

        self.btn_save.setEnabled(False)
        ntf_dict = {
            "title": "",
            "text": self.getl("picture_view_ntf_saved_text"),
            "timer": 1000
        }
        notif = Notification(self._stt, self, ntf_dict)
        UTILS.LogHandler.add_log_record("#1: Image updated. (ID=#2)", ["PictureView", self._media_ids[self._pic_counter]])

    def _btn_next_click(self):
        if self._pic_counter == len(self._media_ids) - 1:
            self._pic_counter = 0
        else:
            self._pic_counter += 1
        self._populate_widgets()
        UTILS.LogHandler.add_log_record("#1: Next image loaded. (ID=#2)", ["PictureView", self._media_ids[self._pic_counter]])
        self.btn_save.setEnabled(False)

    def _btn_cancel_click(self):
        self.close()

    def _load_win_position(self):
        if "view_picture_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("view_picture_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "view_picture_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("view_picture_win_geometry", {}, save_to_file=True)

        g = self.get_appv("view_picture_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["PictureView"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_desc: QLabel = self.findChild(QLabel, "lbl_desc")
        self.txt_name: QLineEdit = self.findChild(QLineEdit, "txt_name")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        
        self.btn_next: QPushButton = self.findChild(QPushButton, "btn_next")
        self.btn_save: QPushButton = self.findChild(QPushButton, "btn_save")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")

        self.setMinimumSize(380, 250)

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("picture_view_win_title_text"))
        
        self.lbl_name.setText(self.getl("picture_view_lbl_name_text"))
        self.lbl_name.setToolTip(self.getl("picture_view_lbl_name_tt"))
        
        self.lbl_desc.setText(self.getl("picture_view_lbl_desc_text"))
        self.lbl_desc.setToolTip(self.getl("picture_view_lbl_desc_text"))

        self.btn_next.setText(self.getl("picture_view_btn_next_text"))
        self.btn_next.setToolTip(self.getl("picture_view_btn_next_tt"))

        self.btn_save.setText(self.getl("picture_view_btn_save_text"))
        self.btn_save.setToolTip(self.getl("picture_view_btn_save_tt"))

        self.btn_cancel.setText(self.getl("picture_view_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("picture_view_btn_cancel_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["PictureView"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self._define_view_picture_win_apperance()
        self._define_labels_apperance(self.lbl_name, "picture_view_lbl_name")
        self._define_labels_apperance(self.lbl_desc, "picture_view_lbl_desc")
        
        self._define_buttons_apperance(self.btn_next, "picture_view_btn_next")
        self._define_buttons_apperance(self.btn_save, "picture_view_btn_save")
        if not settings_updated:
            self.btn_save.setEnabled(False)
        self._define_buttons_apperance(self.btn_cancel, "picture_view_btn_cancel")

        self._define_text_box_apperance(self.txt_name, "picture_view_txt_name")
        self._define_text_box_apperance(self.txt_desc, "picture_view_txt_desc")

    def _define_view_picture_win_apperance(self):
        self.setStyleSheet(self.getv("picture_view_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("picture_view_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))
        label.setVisible(self.getv(f"{name}_visible"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))


class PictureBrowseItem(QLabel):
    def __init__(self, settings: settings_cls.Settings, parent_widget, media_id: int, force_show_image: bool = False, position_in_grid: int = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_widget = parent_widget
        self._media_id = media_id
        self._position_in_grid = position_in_grid
        self._show_image = force_show_image
        self._image_loaded = False
        
        self._setup_label()
        
        # Connect signal
        self.get_appv("signal").signalPicBrowseShowContent.connect(self.signal_load_content)

    def show_content(self):
        self._load_image()

    def signal_load_content(self, size):
        my_size = set(range(self.pos().y(), self.pos().y() + self.height()))
        if size & my_size:
            self._show_image = True
            self.show_content()
        # else:
        #     self._image_loaded = False
        #     self._show_image = False
        #     self.setPixmap(QPixmap())

    def you_are_marked(self, is_this_true: bool):
        if is_this_true:
            self.setFrameShape(3)
            self.setLineWidth(2)
        else:
            self.setFrameShape(0)
            self.setLineWidth(0)

    def you_are_deleted(self):
        self._media_id = None
        self.setText(self.getl("picture_browse_item_deleted_text"))

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._parent_widget.item_double_click_event(self._media_id, self)
        return super().mouseDoubleClickEvent(a0)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.RightButton:
            self._parent_widget.item_right_click_event(self._media_id, self)
        elif ev.button() == Qt.LeftButton:
            self._parent_widget.item_left_click_event(self._media_id, self)
        return super().mousePressEvent(ev)

    def _setup_label(self):
        self.setFixedSize(self.getv("picture_browse_item_size"), self.getv("picture_browse_item_size"))
        self.setAlignment(Qt.AlignCenter)
        
        self._load_image()

    def _load_image(self):
        if not self._show_image or self._image_loaded:
            return

        db_media = db_media_cls.Media(self._stt, self._media_id)
        img = QPixmap(db_media.media_file)
        size = self.size()
        if img.height() > size.height() or img.width() > size.width():
            img = img.scaled(size, Qt.KeepAspectRatio)
        self.setPixmap(img)
        
        self._image_loaded = True


class PictureBrowse(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, media_list: list = None, *args, **kwargs):
        self._dont_clear_menu = False
        self.can_be_deleted = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._last_item = None
        self._active_media_id = None
        self._stop_adding_images = False
        self._media_list = media_list
        self._fix_media_list()
        self._vertical_scroll_val = None
        self._clip: Clipboard = self.get_appv("cb")
    
        # Load GUI
        uic.loadUi(self.getv("picture_browse_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self.area.viewport().installEventFilter(self)
        self.area.installEventFilter(self)
        self.area.verticalScrollBar().installEventFilter(self)

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.txt_name.textChanged.connect(self.txt_name_text_changed)
        self.txt_desc.textChanged.connect(self.txt_desc_text_changed)
        self.btn_close.clicked.connect(self.btn_close_click)
        self.btn_update.clicked.connect(self.btn_update_click)
        self.btn_delete.clicked.connect(self.btn_delete_click)
        self.keyPressEvent = self._key_press_event
        self.area.keyPressEvent = self.area_key_press_event

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["PictureBrowse"])

        QCoreApplication.processEvents()
        self._populate_widgets()
        QCoreApplication.processEvents()
        self.lbl_title.setText(self.getl("picture_browse_lbl_title_text"))
        self._update_image_display()
        self.can_be_deleted = True

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_name)
        self.widget_handler.add_TextBox(self.txt_desc)

        # Add Selection Widgets

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def area_key_press_event(self, e):
        if e.key() == Qt.Key_Right:
            if self._last_item:
                pos = self._last_item._position_in_grid + 1
            else:
                if self.grid_layout.count():
                    self._last_item = self.grid_layout.itemAt(0).widget()
                pos = 0
            if self.grid_layout.count() > pos:
                self._last_item.you_are_marked(False)
                self._last_item = self.grid_layout.itemAt(pos).widget()
                self.area.ensureWidgetVisible(self._last_item)
                self._last_item.you_are_marked(True)
        elif e.key() == Qt.Key_Left:
            if self._last_item:
                pos = self._last_item._position_in_grid - 1
                if pos >= 0:
                    self._last_item.you_are_marked(False)
                    self._last_item = self.grid_layout.itemAt(pos).widget()
                    self.area.ensureWidgetVisible(self._last_item)
                    self._last_item.you_are_marked(True)
        if e.key() == Qt.Key_Down:
            if self._last_item:
                pos = self._last_item._position_in_grid + self.getv("picture_browse_items_in_row")
            else:
                if self.grid_layout.count():
                    self._last_item = self.grid_layout.itemAt(0).widget()
                pos = 0
            if self.grid_layout.count() > pos:
                self._last_item.you_are_marked(False)
                self._last_item = self.grid_layout.itemAt(pos).widget()
                self.area.ensureWidgetVisible(self._last_item)
                self._last_item.you_are_marked(True)
        elif e.key() == Qt.Key_Up:
            if self._last_item:
                pos = self._last_item._position_in_grid - self.getv("picture_browse_items_in_row")
                if pos >= 0:
                    self._last_item.you_are_marked(False)
                    self._last_item = self.grid_layout.itemAt(pos).widget()
                    self.area.ensureWidgetVisible(self._last_item)
                    self._last_item.you_are_marked(True)
        QScrollArea.keyPressEvent(self.area, e)
        
    def _key_press_event(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        else:
            QDialog.keyPressEvent(self, e)

    def eventFilter(self, obj, event):
        if self._vertical_scroll_val != self.area.verticalScrollBar().value():
            self._vertical_scroll_val = self.area.verticalScrollBar().value()
            self._update_image_display()
        return super().eventFilter(obj, event)

    def _update_image_display(self):
        visible_set = set(range(self.area.verticalScrollBar().value(), self.area.verticalScrollBar().value() + self.area.viewport().contentsRect().height() + 1))
        self.get_appv("signal").send_pic_browse_show_content_signal(visible_set)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _fix_media_list(self):
        if not self._media_list:
            return
        
        if isinstance(self._media_list[0], int):
            self._media_list = [[x] for x in self._media_list]

    def btn_delete_click(self):
        if self._active_media_id is None:
            return

        UTILS.LogHandler.add_log_record("#1: About to delete image. (ID=#2)", ["PictureBrowse", self._active_media_id])
        db_media = db_media_cls.Media(self._stt, self._active_media_id)

        if not db_media.is_safe_to_delete(self._active_media_id):
            data_dict = {
                "title": self.getl("picture_browse_msg_cant_delete_title"),
                "text": self.getl("picture_browse_msg_cant_delete_text")
            }
            UTILS.LogHandler.add_log_record("#1: Delete image canceled. Reason: #2", ["PictureBrowse", "In use in some block or definition"])
            self._dont_clear_menu = True
            MessageInformation(self._stt, self, data_dict=data_dict, app_modal=True)
            return

        data_dict = {
            "title": self.getl("picture_browse_msg_confirm_title"),
            "text": self.getl("picture_browse_msg_confirm_text"),
            "icon_path": db_media.media_file,
            "position": "center_parent",
            "buttons": [
                [1, self.getl("btn_yes"), "", None, True],
                [2, self.getl("btn_no"), "", None, True],
                [3, self.getl("btn_cancel"), "", None, True]
            ]
        }
        MessageQuestion(self._stt, self, data_dict, app_modal=True)
        if data_dict["result"] != 1:
            UTILS.LogHandler.add_log_record("#1: Delete image canceled by user.", ["PictureBrowse"])
            return

        db_media.delete_media(self._active_media_id)
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self._last_item.you_are_deleted()
        data_dict = {
            "title": "",
            "text": self.getl("picture_browse_msg_data_deleted_text"),
            "timer": 2000
        }
        Notification(self._stt, self, data_dict=data_dict)
        UTILS.LogHandler.add_log_record("#1: Image deleted.", ["PictureBrowse"])
        self.btn_delete.setEnabled(False)

    def btn_update_click(self):
        if self._active_media_id is None:
            return

        obj_image = Image(self._stt, image_id=self._active_media_id)
        obj_image.ImageName = self.txt_name.text()
        obj_image.ImageDescription = self.txt_desc.toPlainText()
        obj_image.save()

        self.btn_update.setEnabled(False)
        
        data_dict = {
            "title": "",
            "text": self.getl("picture_browse_msg_data_updated_text"),
            "timer": 2000
        }
        Notification(self._stt, self, data_dict=data_dict)
        UTILS.LogHandler.add_log_record("#1: Image updated. (ID=#2)", ["PictureBrowse", self._active_media_id])

    def btn_close_click(self):
        self.close()

    def txt_name_text_changed(self):
        self.btn_delete.setEnabled(True)
        self.btn_update.setEnabled(True)

    def txt_desc_text_changed(self):
        self.btn_delete.setEnabled(True)
        self.btn_update.setEnabled(True)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        
        self.lbl_title.resize(w, self.lbl_title.height())
        
        self.lbl_name.move(self.lbl_name.pos().x(), h - 190)
        self.lbl_desc.move(self.lbl_desc.pos().x(), h - 160)
        self.lbl_file.move(self.lbl_file.pos().x(), h - 190)
        self.lbl_src.move(self.lbl_src.pos().x(), h - 140)
        self.lbl_file_val.move(self.lbl_file_val.pos().x(), h - 170)
        self.lbl_file_val.resize(w - 460, self.lbl_file_val.height())
        self.lbl_src_val.move(self.lbl_src_val.pos().x(), h - 120)
        self.lbl_src_val.resize(w - 460, self.lbl_src_val.height())
        self.lbl_count.move(self.lbl_count.pos().x(), h - 30)

        self.txt_name.move(self.txt_name.pos().x(), h - 200)
        self.txt_desc.move(self.txt_desc.pos().x(), h - 160)

        self.btn_update.move(self.btn_update.pos().x(), h - 30)
        self.btn_delete.move(self.btn_delete.pos().x(), h - 30)
        self.btn_close.move(w - 90, h - 30)

        self.lin_delim.move(0, h - 220)
        self.lin_delim.resize(w, self.lin_delim.height())
        self.area.resize(w - 20, h - 300)

        self.frm_load.move(120, h - 60)

        return super().resizeEvent(a0)

    def _populate_widgets(self) -> None:
        self.frm_load.setVisible(True)

        if self._media_list:
            media_lst = self._media_list
        else:
            db_media = db_media_cls.Media(self._stt)
            media_lst = db_media.get_all_media()

        self.prg_load.setMaximum(len(media_lst))
        refresh_step = int(len(media_lst) / 25)
        if refresh_step < 1:
            refresh_step = 1
        if refresh_step > 30:
            refresh_step = 30
            
        counter = 1
        row = 0
        col = 0
        if self._media_list is not None:
            if len(self._media_list) < 50:
                force_show = True
            else:
                force_show = False
        else:
            force_show = False

        for i in media_lst:
            if counter < 25:
                lbl_item = PictureBrowseItem(self._stt, self, i[0], force_show_image=True, position_in_grid=counter-1)
            else:
                lbl_item = PictureBrowseItem(self._stt, self, i[0], force_show_image=force_show, position_in_grid=counter-1)
            
            self.grid_layout.addWidget(lbl_item, row, col)
            col += 1
            if col == self.getv("picture_browse_items_in_row"):
                col = 0
                row += 1
            self.prg_load.setValue(counter)

            if counter % refresh_step == 0:
                QCoreApplication.processEvents()
            counter += 1
            if self._stop_adding_images:
                break
        self.lbl_count.setText(self.getl("picture_browse_lbl_count_text").replace("#1", str(len(media_lst))))
        self.frm_load.setVisible(False)

    def _populate_data(self, media_id) -> None:
        db_media = db_media_cls.Media(self._stt, media_id)
        self.txt_name.setText(db_media.media_name)
        self.txt_desc.setText(db_media.media_description)
        self.lbl_file_val.setText(db_media.media_file)
        self.lbl_src_val.setText(db_media.media_http)
        self.btn_delete.setEnabled(True)
        self.btn_update.setEnabled(False)

    def _move_right(self):
        pass

    def item_double_click_event(self, media_id: int, item: QLabel):
        PictureView(self._stt, self, media_ids=[media_id], application_modal=False)

    def item_left_click_event(self, media_id: int, item: QLabel):
        self._populate_data(media_id)
        self._active_media_id = media_id
        if media_id is None:
            self.btn_update.setEnabled(False)

        if self._last_item:
            self._last_item.you_are_marked(False)
            item.you_are_marked(True)
            self._last_item = item
        else:
            item.you_are_marked(True)
            self._last_item = item

    def item_right_click_event(self, media_id: int, item: QLabel):
        self.item_left_click_event(media_id, item)
        db_media = db_media_cls.Media(self._stt, media_id=media_id)

        file = FileDialog()
        file_icon, file_name = file.get_default_external_icon_and_app(db_media.media_file)
        
        disab = []
        if self._clip.is_clip_empty():
            disab.append(17)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [17],
            "items": [
                [
                    10,
                    self.getl("picture_view_menu_copy_image_text"),
                    self.getl("picture_view_menu_copy_image_tt"),
                    True,
                    [],
                    self.getv("picture_view_menu_copy_icon_path")
                ],
                [
                    15,
                    self.getl("picture_view_menu_add_to_clip_image_text"),
                    self.getl("picture_view_menu_add_to_clip_image_tt"),
                    True,
                    [],
                    self.getv("picture_view_menu_copy_icon_path")
                ],
                [
                    17,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ],
                [
                    20,
                    self.getl("picture_view_menu_image_info_text"),
                    self.getl("picture_view_menu_image_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    30,
                    self.getl("picture_view_menu_open_with_external_text"),
                    self.getl("picture_view_menu_open_with_external_tt") + file_name,
                    True,
                    [],
                    file_icon
                ]
            ]
        }
        self._dont_clear_menu = True
        self.set_appv("menu", menu_dict)
        ContextMenu(self._stt, self)
        if self.get_appv("menu")["result"] == 10:
            image = QImage(db_media.media_file)
            self.get_appv("clipboard").setImage(image)
            self._clip.copy_to_clip(media_id=media_id, add_to_clip=False)
        if self.get_appv("menu")["result"] == 15:
            image = QImage(db_media.media_file)
            self.get_appv("clipboard").setImage(image)
            self._clip.copy_to_clip(media_id=media_id, add_to_clip=True)
        if self.get_appv("menu")["result"] == 17:
            self._clip.clear_clip()
        elif self.get_appv("menu")["result"] == 20:
            PictureInfo(self._stt, self, media_id)
        elif self.get_appv("menu")["result"] == 30:
            os.startfile(db_media.media_file.replace("/", "\\"))

    def _load_win_position(self):
        if "browse_picture_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("browse_picture_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        result = self.close_me()
        if not result:
            a0.ignore()
            return
        
        return super().closeEvent(a0)

    def close_me(self) -> bool:
        self._stop_adding_images = True
        QCoreApplication.processEvents()
        if "browse_picture_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("browse_picture_win_geometry", {}, save_to_file=True)

        g = self.get_appv("browse_picture_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        UTILS.LogHandler.add_log_record("#1: About to close dialog.", ["PictureBrowse"])
        result = UTILS.DialogUtility.on_closeEvent(self)
        if not result:
            event_dict = {
                "name": "delayed_action",
                "dialog_name": "PictureBrowse",
                "action": "try_to_close_me",
                "self": self,
                "issue": "Init method not finished",
                "validate_function": self.can_i_be_closed,
                "execute_function": self.close,
                "duration": 180000
            }
            
            self.get_appv("main_win").events(event_dict)
            UTILS.TerminalUtility.WarningMessage("#1: Unable to close dialog.\nMyJournal class will try to close it later.", "PictureBrowse")
            return False
        
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["PictureBrowse"])
        return True
    
    def can_i_be_closed(self) -> bool:
        return self.can_be_deleted

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_desc: QLabel = self.findChild(QLabel, "lbl_desc")
        self.lbl_file: QLabel = self.findChild(QLabel, "lbl_file")
        self.lbl_file_val: QLabel = self.findChild(QLabel, "lbl_file_val")
        self.lbl_src: QLabel = self.findChild(QLabel, "lbl_src")
        self.lbl_src_val: QLabel = self.findChild(QLabel, "lbl_src_val")
        
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")

        self.txt_name: QLineEdit = self.findChild(QLineEdit, "txt_name")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        
        self.btn_update: QPushButton = self.findChild(QPushButton, "btn_update")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_delete: QPushButton = self.findChild(QPushButton, "btn_delete")

        self.area: QScrollArea = self.findChild(QScrollArea, "area")
        self.lin_delim: QFrame = self.findChild(QFrame, "lin_delim")

        self.frm_load: QFrame = self.findChild(QFrame, "frm_load")
        self.lbl_load: QLabel = self.findChild(QLabel, "lbl_load")
        self.prg_load: QProgressBar = self.findChild(QProgressBar, "prg_load")

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("picture_browse_win_title_text"))
        
        self.lbl_title.setText(self.getl("picture_browse_lbl_title_wait_text"))
        self.lbl_title.setToolTip(self.getl("picture_browse_lbl_title_tt"))

        self.lbl_name.setText(self.getl("picture_browse_lbl_name_text"))
        self.lbl_name.setToolTip(self.getl("picture_browse_lbl_name_tt"))
        
        self.lbl_desc.setText(self.getl("picture_browse_lbl_desc_text"))
        self.lbl_desc.setToolTip(self.getl("picture_browse_lbl_desc_tt"))

        self.lbl_file.setText(self.getl("picture_browse_lbl_file_text"))
        self.lbl_file.setToolTip(self.getl("picture_browse_lbl_file_tt"))

        self.lbl_src.setText(self.getl("picture_browse_lbl_src_text"))
        self.lbl_src.setToolTip(self.getl("picture_browse_lbl_src_tt"))

        self.lbl_load.setText(self.getl("picture_browse_lbl_load_text"))
        self.lbl_load.setToolTip(self.getl("picture_browse_lbl_load_tt"))

        self.btn_update.setText(self.getl("picture_view_btn_update_text"))
        self.btn_update.setToolTip(self.getl("picture_view_btn_update_tt"))

        self.btn_delete.setText(self.getl("picture_view_btn_delete_text"))
        self.btn_delete.setToolTip(self.getl("picture_view_btn_delete_tt"))

        self.btn_close.setText(self.getl("picture_view_btn_close_text"))
        self.btn_close.setToolTip(self.getl("picture_view_btn_close_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["PictureBrowse"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self._define_browse_picture_win_apperance()
        self.setMinimumSize(500, 320)
        
        self._define_labels_apperance(self.lbl_title, "picture_browse_lbl_title")
        self._define_labels_apperance(self.lbl_name, "picture_browse_lbl_name")
        self._define_labels_apperance(self.lbl_desc, "picture_browse_lbl_desc")
        self._define_labels_apperance(self.lbl_file, "picture_browse_lbl_file")
        self._define_labels_apperance(self.lbl_src, "picture_browse_lbl_src")
        self._define_labels_apperance(self.lbl_file_val, "picture_browse_lbl_file_val")
        self._define_labels_apperance(self.lbl_src_val, "picture_browse_lbl_src_val")
        self._define_labels_apperance(self.lbl_count, "picture_browse_lbl_count")

        self._define_buttons_apperance(self.btn_update, "picture_browse_btn_update")
        self._define_buttons_apperance(self.btn_delete, "picture_browse_btn_delete")
        if not settings_updated:
            self.btn_delete.setEnabled(False)
        self._define_buttons_apperance(self.btn_close, "picture_browse_btn_close")
        if not settings_updated:
            self.btn_update.setEnabled(False)

        self._define_text_box_apperance(self.txt_name, "picture_browse_txt_name")
        self._define_text_box_apperance(self.txt_desc, "picture_browse_txt_desc")

        self.area.setStyleSheet(self.getv("picture_browse_area_stylesheet"))
        if not settings_updated:
            self.area_widget: QWidget = QWidget()
            self.grid_layout: QGridLayout = QGridLayout()
            self.area_widget.setLayout(self.grid_layout)
            self.area.setWidget(self.area_widget)

            self.frm_load.setVisible(False)

    def _define_browse_picture_win_apperance(self):
        self.setStyleSheet(self.getv("picture_browse_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("picture_browse_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))


class FunFactShow(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._fact_id = None
        self._next_id = None
        self._fact_data = self._stt.custom_dict_load(self.getv("fun_fact_file_path"))
        self._add_pictures_to_dict()
        self._clip: Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("fun_fact_show_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self.chk_show_on_start.setChecked(self.getv("fun_fact_show_on_start"))

        self._load_win_position()

        self._lang = self.cmb_lang.currentText()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.chk_show_on_start.stateChanged.connect(self.chk_show_on_start_state_changed)
        self.chk_translate.stateChanged.connect(self.chk_translate_state_changed)
        self.cmb_lang.currentTextChanged.connect(self.cmb_lang_current_text_changed)
        self.btn_close.clicked.connect(self.btn_close_click)
        self.btn_next.clicked.connect(self.btn_next_click)
        self.txt_id.returnPressed.connect(self._txt_id_return_pressed)
        self.txt_id.textChanged.connect(self._txt_id_text_changed)
        self.lbl_content.mouseDoubleClickEvent = self._lbl_content_mouse_double_click
        self.lbl_content.contextMenuEvent = self._lbl_content_context_menu_event

        self.lbl_fade1.mouseDoubleClickEvent = self._fade1_mouse_double_click
        self.lbl_fade2.mouseDoubleClickEvent = self._fade2_mouse_double_click
        self.lbl_fade3.mouseDoubleClickEvent = self._fade3_mouse_double_click
        self.lbl_fade4.mouseDoubleClickEvent = self._fade4_mouse_double_click
        self.lbl_fade5.mouseDoubleClickEvent = self._fade5_mouse_double_click
        self.lbl_fade6.mouseDoubleClickEvent = self._fade6_mouse_double_click
        self.lbl_fade7.mouseDoubleClickEvent = self._fade7_mouse_double_click

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["FunFactShow"])

        self._populate_widgets()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_id)

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def _lbl_content_context_menu_event(self, ev):
        if self.lbl_content.objectName():
            self._show_context_menu()
        else:
            QLabel.contextMenuEvent(self.lbl_content, ev)

    def _show_context_menu(self):
        disab = []
        if self._clip.is_clip_empty():
            disab.append(30)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [30],
            "items": [
                [
                    10,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    20,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    30,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ],
                [
                    40,
                    self.getl("picture_view_menu_open_with_external_text"),
                    self.getl("picture_view_menu_open_with_external_tt"),
                    True,
                    [],
                    None
                ]
            ]
        }
        self._dont_clear_menu = True
        self.set_appv("menu", menu_dict)
        ContextMenu(self._stt, self)
        if self.get_appv("menu")["result"] == 10:
            self._clip.copy_to_clip(media_id=self.lbl_content.objectName(), add_to_clip=False)
        if self.get_appv("menu")["result"] == 20:
            self._clip.copy_to_clip(media_id=self.lbl_content.objectName(), add_to_clip=True)
        if self.get_appv("menu")["result"] == 30:
            self._clip.clear_clip()
        elif self.get_appv("menu")["result"] == 40:
            os.startfile(self.lbl_content.objectName())

    def _fade1_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade1.text())
        self._txt_id_return_pressed()

    def _fade2_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade2.text())
        self._txt_id_return_pressed()

    def _fade3_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade3.text())
        self._txt_id_return_pressed()

    def _fade4_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade4.text())
        self._txt_id_return_pressed()

    def _fade5_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade5.text())
        self._txt_id_return_pressed()

    def _fade6_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade6.text())
        self._txt_id_return_pressed()

    def _fade7_mouse_double_click(self, e: QtGui.QMouseEvent):
        self.txt_id.setText(self.lbl_fade7.text())
        self._txt_id_return_pressed()

    def _lbl_content_mouse_double_click(self, e):
        if not self.lbl_content.objectName():
            self.txt_content.setVisible(True)
            self.lbl_content.setVisible(False)

    def _txt_id_text_changed(self):
        self.txt_id.setStyleSheet(self.getv("fun_fact_show_txt_id_stylesheet"))

    def _txt_id_return_pressed(self):
        f_if = None
        try:
            f_id = int(self.txt_id.text())
            if str(f_id) in self._fact_data:
                self._fact_id = f_id
                self._retranslate_content()
            else:
                self.txt_id.setStyleSheet(self.getv("fun_fact_show_txt_id_error_stylesheet"))
        except ValueError:
            self.txt_id.setStyleSheet(self.getv("fun_fact_show_txt_id_error_stylesheet"))

    def btn_next_click(self):
        self._populate_widgets(self._next_id)

    def btn_close_click(self):
        self.close()

    def cmb_lang_current_text_changed(self):
        self._retranslate_content()

    def chk_translate_state_changed(self):
        self._retranslate_content()

    def chk_show_on_start_state_changed(self):
        self.setv("fun_fact_show_on_start", self.chk_show_on_start.isChecked())

    def _populate_widgets(self, fact_id: int = None):
        if fact_id:
            self._fact_id = fact_id
        else:
            self._fact_id = random.randint(1, len(self._fact_data))

        self.lbl_content2.setText(self.lbl_content.text())
        if self.lbl_content.objectName():
            if self.lbl_content.pixmap():
                self.lbl_content2.setPixmap(self.lbl_content.pixmap())
        dont_animate = self.txt_content.isVisible()
        self._retranslate_content(pick_next_fact=True)
        if not dont_animate:
            dont_animate = self.txt_content.isVisible()
        if not dont_animate:
            self._animate_next_content()
        UTILS.LogHandler.add_log_record("#1: Content displayed. (ID=#2)", ["FunFactShow", self._fact_id])

    def _animate_next_content(self):
        self.lbl_content.setVisible(True)
        self.lbl_content2.setVisible(True)

        duration = 300
        steps = 50
        start = self.lbl_content.pos().y()
        end = self.contentsRect().height()
        scale = (end - start) / steps

        self.lbl_content2.setVisible(True)
        for i in range(steps):
            y1 = int((steps - i) * scale) + start
            y2 = int(i * scale) + start
            self.lbl_content2.move(10, y2)
            self.lbl_content.move(10, y1)
            QCoreApplication.processEvents()
            time.sleep(duration / steps / 1000)

        self.lbl_content2.setVisible(False)
        self.lbl_content.move(10, 150)

    def _retranslate_content(self, pick_next_fact: bool = False):
        fade7 = self.lbl_fade6.text()
        fade6 = self.lbl_fade5.text()
        fade5 = self.lbl_fade4.text()
        fade4 = self.lbl_fade3.text()
        fade3 = self.lbl_fade2.text()
        fade2 = self.lbl_fade1.text()
        fade1 = self.txt_id.text()
        self.lbl_title.setText(self.getl("fun_fact_show_lbl_title_working_text"))
        QCoreApplication.processEvents()

        original_text = self._fact_data[str(self._fact_id)]["content"]
        content_text = self._translate(self._fact_data[str(self._fact_id)]["content"])
        self.lbl_content.setObjectName("")
        if len(content_text) >= 6:
            if content_text[:6] == "|file|":
                self.lbl_content.setObjectName(content_text[6:])
                self._load_picture()

        if not self.lbl_content.objectName():
            self.lbl_content.setText(content_text)

        self.lbl_name.setText(self._translate(self._fact_data[str(self._fact_id)]["name"]))

        if pick_next_fact:
            self._next_id = random.randint(1, len(self._fact_data))
        
        self.lbl_next_val.setText(self._translate(self._fact_data[str(self._next_id)]["name"]))
        
        self._set_content_font_size()

        self.lbl_title.setText(self.getl("fun_fact_show_lbl_title_text"))
        self.txt_id.setText(str(self._fact_id))
        
        self.txt_content.setHtml(self._content_for_text_box(self.lbl_content.text()))

        if len(self.lbl_content.text()) > 1400:
            self.txt_content.setVisible(True)
            self.lbl_content.setVisible(False)
        else:
            self.txt_content.setVisible(False)
            self.lbl_content.setVisible(True)

        fade = [self.lbl_fade7.text(), fade2, fade3, fade4, fade5, fade6, fade7]
        if fade1 not in fade:
            self.lbl_fade1.setText(fade1)
            self.lbl_fade2.setText(fade2)
            self.lbl_fade3.setText(fade3)
            self.lbl_fade4.setText(fade4)
            self.lbl_fade5.setText(fade5)
            self.lbl_fade6.setText(fade6)
            self.lbl_fade7.setText(fade7)
        
        if self.txt_content.isVisible():
            self._show_metric(original_text)
        else:
            self._show_metric(original_text)

    def _show_metric(self, txt: str):
        self.lbl_metric.setText("")
        if not txt:
            return
        
        txt = txt.lower()

        repl = """!@#$%^&*()_º+=-[]{};':"\n\t|<>?"""
        repl = [x for x in repl]
        add_repl = ["million", "billion", "thousand", "hundred", "trillion", "quadrillion", "square", "sq.", "sq"]
        for i in add_repl:
            repl.append(i+"s per")
            repl.append(i+" per")
            repl.append(i+"s")
            repl.append(i)

        for i in repl:
            txt = txt.replace(i, " ")

        data = self._stt.custom_dict_load(self.getv("misc_file_path"))
        for i in data["numbers"]:
            if float(i[1]) >= 1:
                txt = txt.replace(f" {i[0].strip()} ", f" {i[1]} ")
            else:
                txt = txt.replace(f" {i[0].strip()} ", f"{i[1]} ")
        
        numer = "0123456789"
        start = 0
        while True:
            start = txt.find(".", start)
            if start == -1:
                break

            if start == 0:
                start = 1
                continue
            
            if txt[start-1:start] not in numer:
                txt = txt[:start] + " " + txt[start:]
                start = start + 2
            else:
                start += 1
        start = 0
        while True:
            start = txt.find(",", start)
            if start == -1:
                break

            if start == 0:
                start = 1
                continue
            
            if txt[start-1:start] not in numer:
                txt = txt[:start] + " " + txt[start:].replace(",", " ", 1)
                start = start + 2
            else:
                start += 1
        
        while True:
            txt = txt.replace("  ", " ")
            if txt.find("  ") == -1:
                break

        lbl_text = ""
        lbl_tt = ""

        for i in data["metric"]["unit"]:
            added_tt = False
            for j in data["metric"]["unit"][i]["syn"]:
                start = 0
                while True:
                    start = txt.find(f" {j} ", start)
                    if start < 1:
                        break

                    if txt.rfind(" ", 0, start) >= 0:
                        try_num = txt[txt.rfind(" ", 0, start):start].strip()
                        try_num = try_num.replace(",", "")
                        if try_num.rfind(".") == 0:
                            try_num = "0" + try_num
                        elif try_num.rfind(".") > 0:
                            if try_num.rfind(".") >= len(try_num) - 3:
                                try_num = try_num[:try_num.rfind(".")].replace(".", "") + try_num[try_num.rfind("."):]
                            else:
                                try_num = try_num.replace(".", "")
                        try:
                            value = eval(try_num)
                            lbl_text += self._calc_metric(i, value, data) + "\n"
                            if not added_tt:
                                lbl_tt += self._calc_metric(i, 1, data) + "\n"
                                added_tt = True
                            start += len(j) + 2
                            continue
                        except:
                            start += len(j) + 2
                            continue

                    start += len(j) + 2

        lbl_text = lbl_text.strip()
        lbl_tt = lbl_tt.strip()
        self.lbl_metric.setText(lbl_text)
        self.lbl_metric.setToolTip(lbl_tt)

    def _calc_metric(self, unit: str, value: float, data: dict) -> str:
        txt = ""
        for i in data["metric"]["conv"]:
            if unit.lower() in i[0].lower():
                eval_txt = i[2][i[2].find("=")+1:].lower().replace(unit.lower(), str(value)).strip()
                try:
                    eval_num = eval(eval_txt)
                except:
                    eval_num = None
                if eval_num is not None:
                    if eval_num < 20:
                        txt += f"{value} {i[0]} = {eval_num: ,.2f} {i[1]}\n"
                    else:
                        txt += f"{value} {i[0]} = {eval_num: ,.0f} {i[1]}\n"
        
        return txt.strip()

    def _load_picture(self):
        if not self.lbl_content.objectName():
            return False

        if not os.path.isfile(self.lbl_content.objectName()):
            return False
        
        self.lbl_content.setText("")
        img = QPixmap()
        img.load(self.lbl_content.objectName())
        img = img.scaled(self.lbl_content.width(), self.lbl_content.height(), Qt.KeepAspectRatio)
        self.lbl_content.setPixmap(img)

        return True

    def _add_pictures_to_dict(self):
        folder: str = os.path.abspath(self.getv("funfact_images_folder_path"))
        folder += "/" if not folder.endswith("/") else ""
        self._create_directory_structure(folder + "file.file")
        files = os.listdir(folder)
        count = len(self._fact_data) + 1
        
        for file in files:
            file_path = folder + file
            title = "Interesting Image: " + os.path.splitext(file)[0]
            content = f"|file|{file_path}"
            self._fact_data[str(count)] = {}
            self._fact_data[str(count)]["name"] = title
            self._fact_data[str(count)]["content"] = content
            count += 1

    def _create_directory_structure(self, file: str):
        folder = os.path.split(file)[0]

        if not os.path.isdir(folder):
            os.mkdir(folder)

    def _content_for_text_box(self, txt: str) -> str:
        txt_lines = txt.split("\n")
        result = ""
        for line in txt_lines:
            if line.upper() == line:
                if result:
                    result += "<br>"
                result += f'<span style="color: {self.getv("fun_fact_show_subtitle_color")}; font-size: {self.getv("fun_fact_show_subtitle_font_size")}px;">{line}</span><br>'
            else:
                result += f'<span style="color: {self.getv("fun_fact_show_normal_content_color")}; font-size: {self.getv("fun_fact_show_normal_content_font_size")}px;">{line}</span><br>'
        return result
    
    def _set_content_font_size(self):
        c_len = len(self.lbl_content.text())
        size = 14
        if c_len < 1000:
            size = 16
        if c_len < 700:
            size = 18
        if c_len < 400:
            size = 20
        if c_len < 200:
            size = 22
        font = self.lbl_content.font()
        font.setPointSize(size)
        self.lbl_content.setFont(font)

    def _translate(self, text: str) -> str:
        if self.cmb_lang.currentText() == "english" or not self.chk_translate.isChecked():
            return text
        
        code_from = "english"
        code_to = googletrans.LANGCODES[self.cmb_lang.currentText()]
        trans = Translator()
        translated_text = trans.translate(text, dest=code_to, src=code_from).text
        UTILS.LogHandler.add_log_record("#1: Content translated to #2.", ["FunFactShow", self.cmb_lang.currentText()])
        return translated_text

    def _load_win_position(self):
        if "fun_fact_show_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("fun_fact_show_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self.chk_translate.setChecked(g["translate"])
            if g["language"]:
                self.cmb_lang.setCurrentText(g["language"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "fun_fact_show_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("fun_fact_show_win_geometry", {}, save_to_file=True)

        g = self.get_appv("fun_fact_show_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["show_on_start"] = self.chk_show_on_start.isChecked()
        g["translate"] = self.chk_translate.isChecked()
        g["language"] = self.cmb_lang.currentText()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["FunFactShow"])
        UTILS.DialogUtility.on_closeEvent(self)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w, self.lbl_title.height())
        self.lbl_name.resize(w, self.lbl_name.height())
        
        self.lbl_content.resize(w - 20, h - 230)
        self._load_picture()

        self.lbl_content2.resize(w - 20, h - 230)
        self.lbl_content2.move(self.lbl_content.pos().x(), self.lbl_content.pos().y())
        self.txt_content.resize(w - 20, h - 230)
        self.txt_content.move(self.lbl_content.pos().x(), self.lbl_content.pos().y())

        self.lbl_rec.move(w - 10 - self.lbl_rec.width(), 5)
        self.cmb_lang.move(10, h - 30)
        self.chk_translate.move(160, h - 25)
        self.chk_show_on_start.move(270, h - 25)
        self.btn_next.move(w -260, h - 30)
        self.btn_close.move(w -100, h - 30)
        self.lbl_next.move(10, h - 60)
        self.lbl_next_val.move(120, h - 60)

        if w - 10 - self.lbl_metric.width() >= 0:
            self.lbl_metric.move(w - 10 - self.lbl_metric.width(), 40)
        else:
            self.lbl_metric.move(0, 40)

        return super().resizeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        
        self.lbl_next: QLabel = self.findChild(QLabel, "lbl_next")
        self.lbl_next_val: QLabel = self.findChild(QLabel, "lbl_next_val")

        self.lbl_content: QLabel = self.findChild(QLabel, "lbl_content")
        self.lbl_content2: QLabel = self.findChild(QLabel, "lbl_content2")
        self.txt_content: QTextEdit = self.findChild(QTextEdit, "txt_content")

        self.lbl_rec: QLabel = self.findChild(QLabel, "lbl_rec")
        self.txt_id: QLineEdit = self.findChild(QLineEdit, "txt_id")

        self.cmb_lang: QComboBox = self.findChild(QComboBox, "cmb_lang")
        self.chk_translate: QCheckBox = self.findChild(QCheckBox, "chk_translate")
        self.chk_show_on_start: QCheckBox = self.findChild(QCheckBox, "chk_show_on_start")
        self.btn_next: QPushButton = self.findChild(QPushButton, "btn_next")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")

        self.lbl_fade1: QLabel = self.findChild(QLabel, "lbl_fade1")
        self.lbl_fade2: QLabel = self.findChild(QLabel, "lbl_fade2")
        self.lbl_fade3: QLabel = self.findChild(QLabel, "lbl_fade3")
        self.lbl_fade4: QLabel = self.findChild(QLabel, "lbl_fade4")
        self.lbl_fade5: QLabel = self.findChild(QLabel, "lbl_fade5")
        self.lbl_fade6: QLabel = self.findChild(QLabel, "lbl_fade6")
        self.lbl_fade7: QLabel = self.findChild(QLabel, "lbl_fade7")

        self.lbl_metric: QLabel = self.findChild(QLabel, "lbl_metric")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("fun_fact_show_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("fun_fact_show_lbl_title_tt"))

        self.lbl_next.setText(self.getl("fun_fact_show_lbl_next_text"))
        self.lbl_next.setToolTip(self.getl("fun_fact_show_lbl_next_tt"))

        self.lbl_next_val.setToolTip(self.getl("fun_fact_show_lbl_next_val_tt"))

        self.chk_translate.setText(self.getl("fun_fact_show_chk_translate_text"))
        self.chk_translate.setToolTip(self.getl("fun_fact_show_chk_translate_tt"))

        self.cmb_lang.setToolTip(self.getl("fun_fact_show_cmb_lang_tt"))

        self.chk_show_on_start.setText(self.getl("fun_fact_show_chk_show_on_start_text"))
        self.chk_show_on_start.setToolTip(self.getl("fun_fact_show_chk_show_on_start_tt"))

        self.btn_next.setText(self.getl("fun_fact_show_btn_next_text"))
        self.btn_next.setToolTip(self.getl("fun_fact_show_btn_next_tt"))

        self.btn_close.setText(self.getl("fun_fact_show_btn_close_text"))
        self.btn_close.setToolTip(self.getl("fun_fact_show_btn_close_tt"))

        self.lbl_rec.setText(self.getl("fun_fact_show_lbl_rec_text").replace("#1", f"{len(self._fact_data): ,.0f}"))
        self.lbl_rec.setToolTip(self.getl("fun_fact_show_lbl_rec_tt"))

        self.lbl_fade1.setText("")
        self.lbl_fade2.setText("")
        self.lbl_fade3.setText("")
        self.lbl_fade4.setText("")
        self.lbl_fade5.setText("")
        self.lbl_fade6.setText("")
        self.lbl_fade7.setText("")
        self.lbl_metric.setText("")

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["FunFactShow"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self._define_fun_fact_show_win_apperance()
        self._define_labels_apperance(self.lbl_title, "fun_fact_show_lbl_title")
        self._define_labels_apperance(self.lbl_name, "fun_fact_show_lbl_name")
        self._define_labels_apperance(self.lbl_next, "fun_fact_show_lbl_next")
        self._define_labels_apperance(self.lbl_next_val, "fun_fact_show_lbl_next_val")
        self._define_labels_apperance(self.lbl_rec, "fun_fact_show_lbl_rec")

        self.cmb_lang.setStyleSheet(self.getv("fun_fact_show_cmb_lang_stylesheet"))
        self.chk_translate.setStyleSheet(self.getv("fun_fact_show_chk_translate_stylesheet"))
        self.chk_show_on_start.setStyleSheet(self.getv("fun_fact_show_chk_show_on_start_stylesheet"))

        self.btn_next.setStyleSheet(self.getv("fun_fact_show_btn_next_stylesheet"))
        self.btn_close.setStyleSheet(self.getv("fun_fact_show_btn_close_stylesheet"))

        self.lbl_content.setStyleSheet(self.getv("fun_fact_show_lbl_content_stylesheet"))
        self.lbl_content.setObjectName("")
        self.lbl_content2.setStyleSheet(self.getv("fun_fact_show_lbl_content_stylesheet"))
        self.lbl_content2.setObjectName("")
        self.lbl_content2.setVisible(False)
        self.txt_content.setStyleSheet(self.getv("fun_fact_show_txt_content_stylesheet"))
        
        self.txt_id.setStyleSheet(self.getv("fun_fact_show_txt_id_stylesheet"))
        
        if not settings_updated:
            self._setup_languages_combo_box()

    def _setup_languages_combo_box(self):
        self.cmb_lang.clear()
        for lang in googletrans.LANGCODES:
            self.cmb_lang.addItem(lang)

    def _define_fun_fact_show_win_apperance(self):
        self.setStyleSheet(self.getv("fun_fact_show_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("fun_fact_show_win_icon_path")))
        self.setWindowTitle(self.getl("fun_fact_show_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(600, 300)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))


class Translate(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, text: str = None, *agrs, **kwargs):
        super().__init__(parent_widget, *agrs, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_widget = parent_widget
        self._text = text
        UTILS.LogHandler.add_log_record("#1: Engine loaded.", ["Translate"])

    def show_gui(self, text: str = None):
        if text is not None:
            self._text = text

        # Load GUI
        uic.loadUi(self.getv("translate_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self._populate_widgets()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.txt_from.textChanged.connect(self._txt_from_text_changed)
        self.btn_close.clicked.connect(self.btn_close_click)
        self.btn_switch.clicked.connect(self.btn_switch_click)
        self.btn_trans.clicked.connect(self.btn_trans_click)
        self.btn_detect.clicked.connect(self.btn_detect_click)

        self.get_appv("log").write_log("Translate. init.")
        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["Translate"])

        title_text = self.lbl_title.text()
        self.lbl_title.setText("<span style='font-size: 100px;'>⌛</span>")
        QCoreApplication.processEvents()
        if self.chk_auto_paste_and_copy.isChecked() and self.get_appv("clipboard").text():
            self.txt_from.setPlainText(self.get_appv("clipboard").text())
            if self._populate_detection_label():
                self.btn_trans_click()
        self.lbl_title.setText(title_text)

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_from)
        self.widget_handler.add_TextBox(self.txt_to)

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def btn_detect_click(self):
        result = self._populate_detection_label()
        if result:
            self.cmb_from.setCurrentText(googletrans.LANGUAGES[result])

    def btn_trans_click(self):
        if not self.txt_from.toPlainText():
            return
        
        code_from = googletrans.LANGCODES[self.cmb_from.currentText()]
        code_to = googletrans.LANGCODES[self.cmb_to.currentText()]
        trans = Translator()
        translated_text = trans.translate(self.txt_from.toPlainText(), dest=code_to, src=code_from).text
        UTILS.LogHandler.add_log_record("#1: Text translated from #2 to #3.", ["Translate", self.cmb_from.currentText(), self.cmb_to.currentText()])
        if self.chk_latin.isChecked():
            translated_text = self.cirilica_u_latinicu(translated_text)
            UTILS.LogHandler.add_log_record("#1: Text converted to #2.", ["Translate", "Latin"])
        self.txt_to.setPlainText(translated_text)
        self.get_appv("clipboard").setText(translated_text)
        UTILS.LogHandler.add_log_record("#1: Text copied to #2.", ["Translate", "Clipboard"])

    def btn_switch_click(self):
        tmp = self.cmb_from.currentText()
        self.cmb_from.setCurrentText(self.cmb_to.currentText())
        self.cmb_to.setCurrentText(tmp)
        UTILS.LogHandler.add_log_record("#1: Languages switched. New setup: FROM #2 TO #3", ["Translate", self.cmb_from.currentText(), self.cmb_to.currentText()])

    def btn_close_click(self):
        self.close()

    def cirilica_u_latinicu(self, text: str) -> str:
        latinica_text = to_latin(text)
        return latinica_text

    def _txt_from_text_changed(self):
        if abs(len(self._text) - len(self.txt_from.toPlainText())) > 1:
            result = self._populate_detection_label()
            if result:
                self.cmb_from.setCurrentText(googletrans.LANGUAGES[result])
        self._text = self.txt_from.toPlainText()
        if self._text:
            self.btn_trans.setEnabled(True)
            self.btn_detect.setEnabled(True)
        else:
            self.btn_trans.setEnabled(False)
            self.btn_detect.setEnabled(False)

    def _populate_widgets(self):
        if self._text is None:
            self._text = ""
            self.btn_trans.setEnabled(False)
            self.btn_detect.setEnabled(False)
        self.txt_from.setText(self._text)
        
        self.cmb_from.addItems(googletrans.LANGCODES)
        self.cmb_to.addItems(googletrans.LANGCODES)
        
        self.cmb_to.setCurrentText(self.get_appv("user").language_name)
        result = self._populate_detection_label()
        if result:
            self.cmb_from.setCurrentText(googletrans.LANGUAGES[result])

    def _populate_detection_label(self) -> str:
        if self.txt_from.toPlainText():
            translator = Translator()
            lang = translator.detect(self.txt_from.toPlainText())
            detect_text = self.getl("translation_detected_text")
            try:
                detect_text += f"{googletrans.LANGUAGES[lang.lang]} ({int(lang.confidence*100)} %)"
                self.lbl_detected.setText(detect_text)
                return lang.lang
            except:
                self.lbl_detected.setText(self.getl("translation_detected_none_text"))
                return None

    def _load_win_position(self):
        if "translation_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("translation_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self.chk_latin.setChecked(g.setdefault("to_latin", True))
            self.chk_auto_paste_and_copy.setChecked(g.setdefault("auto_paste_and_copy", False))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "translation_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("translation_win_geometry", {}, save_to_file=True)

        g = self.get_appv("translation_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["to_latin"] = self.chk_latin.isChecked()
        g["auto_paste_and_copy"] = self.chk_auto_paste_and_copy.isChecked()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["Translate"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_from: QLabel = self.findChild(QLabel, "lbl_from")
        self.lbl_detected: QLabel = self.findChild(QLabel, "lbl_detected")
        self.lbl_to: QLabel = self.findChild(QLabel, "lbl_to")

        self.cmb_from: QComboBox = self.findChild(QComboBox, "cmb_from")
        self.cmb_to: QComboBox = self.findChild(QComboBox, "cmb_to")

        self.txt_from: QTextEdit = self.findChild(QTextEdit, "txt_from")
        self.txt_to: QTextEdit = self.findChild(QTextEdit, "txt_to")

        self.btn_trans: QPushButton = self.findChild(QPushButton, "btn_trans")
        self.btn_switch: QPushButton = self.findChild(QPushButton, "btn_switch")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_detect: QPushButton = self.findChild(QPushButton, "btn_detect")
        self.chk_latin: QCheckBox = self.findChild(QCheckBox, "chk_latin")
        self.chk_auto_paste_and_copy: QCheckBox = self.findChild(QCheckBox, "chk_auto_paste_and_copy")

        self.setLayout(self.gridLayout)

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("translation_win_title_text"))

        self.lbl_title.setText(self.getl("translation_title_text"))
        self.lbl_title.setToolTip(self.getl("translation_title_tt"))
        self.lbl_from.setText(self.getl("translation_from_text"))
        self.lbl_from.setToolTip(self.getl("translation_from_tt"))
        self.lbl_detected.setText(self.getl("translation_detected_text"))
        self.lbl_detected.setToolTip(self.getl("translation_detected_tt"))
        self.lbl_to.setText(self.getl("translation_to_text"))
        self.lbl_to.setToolTip(self.getl("translation_to_tt"))

        self.btn_trans.setText(self.getl("translation_btn_trans_text"))
        self.btn_trans.setToolTip(self.getl("translation_btn_trans_tt"))
        self.btn_switch.setText(self.getl("translation_btn_switch_text"))
        self.btn_switch.setToolTip(self.getl("translation_btn_switch_tt"))
        self.btn_close.setText(self.getl("translation_btn_close_text"))
        self.btn_close.setToolTip(self.getl("translation_btn_close_tt"))
        self.btn_detect.setText(self.getl("translation_btn_detect_text"))
        self.btn_detect.setToolTip(self.getl("translation_btn_detect_tt"))

        self.chk_latin.setText(self.getl("translation_chk_latin_text"))
        self.chk_latin.setToolTip(self.getl("translation_chk_latin_tt"))
        self.chk_auto_paste_and_copy.setText(self.getl("translation_chk_auto_paste_and_copy_text"))
        self.chk_auto_paste_and_copy.setToolTip(self.getl("translation_chk_auto_paste_and_copy_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["Translate"])
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_translate_win_apperance()
        self._define_labels_apperance(self.lbl_title, "translate_lbl_title")
        self._define_labels_apperance(self.lbl_from, "translate_lbl_from_to")
        self._define_labels_apperance(self.lbl_to, "translate_lbl_from_to")
        self._define_labels_apperance(self.lbl_detected, "translate_lbl_detected")
        
        self._define_buttons_apperance(self.btn_trans, "translate_btn_trans")
        self._define_buttons_apperance(self.btn_switch, "translate_btn_switch")
        self._define_buttons_apperance(self.btn_close, "translate_btn_close")
        self._define_buttons_apperance(self.btn_detect, "translate_btn_detect")

        self._define_text_box_apperance(self.txt_from, "translate_txt_from_to")
        self._define_text_box_apperance(self.txt_to, "translate_txt_from_to")

        self._define_combo_box_apperance(self.cmb_from, "translate_cmb_from_to")
        self._define_combo_box_apperance(self.cmb_to, "translate_cmb_from_to")

        self.chk_latin.setStyleSheet(self.getv("translate_chk_latin_stylesheet"))
        self.chk_auto_paste_and_copy.setStyleSheet(self.getv("translate_chk_auto_paste_and_copy_stylesheet"))

    def _define_translate_win_apperance(self):
        self.setStyleSheet(self.getv("translate_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("translate_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setFrameShape(self.getv(f"{name}_frame_shape"))
        label.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        label.setLineWidth(self.getv(f"{name}_line_width"))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        label.setFont(font)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))
        label.setVisible(self.getv(f"{name}_visible"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))
    
    def _define_text_box_apperance(self, txt_box, name: str):
        if isinstance(txt_box, QTextEdit):
            txt_box.setFrameShape(self.getv(f"{name}_frame_shape"))
            txt_box.setFrameShadow(self.getv(f"{name}_frame_shadow"))
            txt_box.setLineWidth(self.getv(f"{name}_line_width"))
            txt_box.setAcceptRichText(False)

        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        txt_box.setFont(font)

        txt_box.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_combo_box_apperance(self, cmb: QComboBox, name: str) -> None:
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        cmb.setFont(font)

        cmb.setStyleSheet(self.getv(f"{name}_stylesheet"))


class Clipboard():
    ID_LIST_MARKER = "@@@BDlist"
    BLOCK_MARKER = "B"
    DEFINITION_MARKER = "D"
    ID_DELIMITER = ","

    def __init__(self, settings: settings_cls.Settings):
        self._do_nothing = True
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._os_clip: QClipboard = self.get_appv("clipboard")
        try:
            self._clip = self._stt.custom_dict_load(self.getv("clipboard_file_path"))
        except:
            self._clip = {}
        self._drag_data: dict = None

        # Connect clipboard changes to slot
        self._os_clip.dataChanged.connect(self._clipboard_changed)

        QCoreApplication.processEvents()
        self._check_dict()
        self._do_nothing = False

    def set_drag_data(self, drag_data, drag_data_type: str, raise_object_after_drop: QWidget = None) -> None:
        """
        Sets the drag data to the clipboard
        """
        
        self._drag_data = {
            "data": drag_data,
            "type": drag_data_type,
            "raise": raise_object_after_drop
        }
        UTILS.LogHandler.add_log_record("#1: Function #2. Drag data set.", ["Clipboard", "set_drag_data"], extract_to_variables=["Drag Data", self._drag_data])

    def get_drag_data(self, delete_data: bool = True, raise_source_window: bool = True) -> dict:
        """
        Returns the drag data from the clipboard
        """
        
        data = self._drag_data

        if data is not None and data.get("raise", None) is not None and raise_source_window:
            self._drag_data["raise"].raise_()

        UTILS.LogHandler.add_log_record("#1: Function #2. Drag data read.", ["Clipboard", "get_drag_data"], extract_to_variables=["Drag Data", self._drag_data])
        
        if delete_data:
            self._drag_data = None

        return data

    def clear_drag_data(self) -> None:
        """
        Clears the drag data from the clipboard
        """
        
        self._drag_data = None

    def has_drag_data(self) -> bool:
        """
        Returns True if there is a drag data in the clipboard
        """
        
        return self._drag_data is not None

    def block_clip_copy_blocks(self, block_ids: Union[list, str, tuple]) -> int:
        """
        Removes all blocks from clipboard.
        Adds 'block_ids' blocks to clipboard

        Parameters
        ----------
        block_ids : Union[list, str, tuple] - The block IDs to add to the clipboard.
        
        Returns
        -------
        Number of ID-s added to clipboard
        """
        block_ids = self._ids_to_list(block_ids)
        if block_ids is None:
            return 0
        
        self._clip_remove_all_ids(self.BLOCK_MARKER)
        
        return self._add_ids_to_clip(block_ids, self.BLOCK_MARKER)

    def block_clip_add_blocks(self, block_ids: Union[list, str, tuple]) -> int:
        """
        Appends 'block_ids' blocks to clipboard

        Parameters
        ----------
        block_ids : Union[list, str, tuple] - The block IDs to add to the clipboard.
        
        Returns
        -------
        Number of ID-s added to clipboard
        """
        block_ids = self._ids_to_list(block_ids)
        if block_ids is None:
            return 0
        
        return self._add_ids_to_clip(block_ids, self.BLOCK_MARKER)

    def block_clip_remove_all_blocks(self, block_ids: Union[list, str, tuple, None]) -> int:
        """
        Removes all blocks from 'block_ids' list from clipboard
        If 'block_ids' is None, removes all blocks

        Parameters
        ----------
        block_ids : Union[list, str, tuple] - The block IDs
        
        Returns
        -------
        Number of ID-s removed from clipboard
        """
        block_ids = self._ids_to_list(block_ids, allow_none=True)
        
        return self._clip_remove_all_ids(self.BLOCK_MARKER, block_ids)

    def block_clip_number_of_items(self) -> int:
        """
        Returns number of blocks in clipboard
        """
        return len(self._clip_get_all_ids(id_marker=self.BLOCK_MARKER))

    def block_clip_ids_that_are_in_clipboard(self, ids: Union[str, int, list]) -> list:
        """
        Returns a list of block IDs that are in the clipboard.

        Parameters
        ----------
        ids : Union[str, int, list]
            The clip IDs to check.

        Returns
        -------
        list
            The list of block IDs that are in the clipboard.
        """
        ids = self._ids_to_list(ids)
        if ids is None:
            return []
        
        ids = self._fix_clip_ids(ids, self.BLOCK_MARKER)

        all_ids = self._clip_get_all_ids(id_marker=self.BLOCK_MARKER)

        return [x for x in ids if x in all_ids]

    def block_clip_items(self) -> list:
        items = self._clip_get_all_ids(id_marker=self.BLOCK_MARKER)
        return self._remove_clip_marker(items, self.BLOCK_MARKER)

    def def_clip_copy_defs(self, def_ids: Union[list, str, tuple]) -> int:
        """
        Removes all definitions from clipboard.
        Adds 'def_ids' definitions to clipboard

        Parameters
        ----------
        def_ids : Union[list, str, tuple] - The definition IDs to add to the clipboard.
        
        Returns
        -------
        Number of ID-s added to clipboard
        """
        def_ids = self._ids_to_list(def_ids)
        if def_ids is None:
            return 0
        
        self._clip_remove_all_ids(self.DEFINITION_MARKER)
        
        return self._add_ids_to_clip(def_ids, self.DEFINITION_MARKER)

    def def_clip_add_defs(self, def_ids: Union[list, str, tuple]) -> int:
        """
        Appends 'def_ids' definitions to clipboard

        Parameters
        ----------
        def_ids : Union[list, str, tuple] - The definition IDs to add to the clipboard.
        
        Returns
        -------
        Number of ID-s added to clipboard
        """
        def_ids = self._ids_to_list(def_ids)
        if def_ids is None:
            return 0
        
        return self._add_ids_to_clip(def_ids, self.DEFINITION_MARKER)

    def def_clip_remove_all_defs(self, def_ids: Union[list, str, tuple]) -> int:
        """
        Removes all definitions from 'def_ids' list from clipboard
        If 'def_ids' is None, removes all definitions

        Parameters
        ----------
        def_ids : Union[list, str, tuple] - The definition IDs
        
        Returns
        -------
        Number of ID-s removed from clipboard
        """
        def_ids = self._ids_to_list(def_ids, allow_none=True)
        
        return self._clip_remove_all_ids(self.DEFINITION_MARKER, def_ids)

    def def_clip_number_of_items(self) -> int:
        """
        Returns number of definitions in clipboard
        """
        return len(self._clip_get_all_ids(id_marker=self.DEFINITION_MARKER))

    def def_clip_ids_that_are_in_clipboard(self, ids: Union[str, int, list]) -> list:
        """
        Returns a list of definition IDs that are in the clipboard.

        Parameters
        ----------
        ids : Union[str, int, list]
            The definition IDs to check.

        Returns
        -------
        list
            The list of definition IDs that are in the clipboard.
        """
        ids = self._ids_to_list(ids)
        if ids is None:
            return []
        
        ids = self._fix_clip_ids(ids, self.DEFINITION_MARKER)

        all_ids = self._clip_get_all_ids(id_marker=self.DEFINITION_MARKER)

        return [x for x in ids if x in all_ids]

    def def_clip_items(self) -> list:
        items = self._clip_get_all_ids(id_marker=self.DEFINITION_MARKER)
        return self._remove_clip_marker(items, self.DEFINITION_MARKER)

    def _remove_clip_marker(self, clip_ids: list, id_marker: str) -> list:
        result = []

        for i in clip_ids:
            if i.startswith(id_marker):
                i = i[2:]
            
            result.append(i)
        
        return result
    
    def _fix_clip_ids(self, ids: list, id_marker: str) -> list:
        result = []

        for i in ids:
            if not i.startswith(id_marker):
                i = f"{id_marker}:{i}"
            
            result.append(i)
        
        return result

    def _add_ids_to_clip(self, ids: list, id_marker: str, unique: bool = True) -> int:
        clip_ids = self._clip_get_all_ids()

        count = 0
        for id_item in ids:
            if not id_item.startswith(id_marker):
                id_item = f"{id_marker}:{id_item}"

            if id_item in clip_ids and unique:
                continue
            
            clip_ids.append(id_item)
            count += 1
        
        clip_text = f'{self.ID_LIST_MARKER}({self.ID_DELIMITER.join(clip_ids)})'

        self._os_clip.setText(clip_text)

        return count

    def _clip_get_all_ids(self, id_marker: str = None) -> list:
        result = []

        data = self._os_clip.text()
        if not isinstance(data, str):
            return result

        pos = data.find(self.ID_LIST_MARKER)
        if pos == -1:
            return result

        start = data.find("(", pos)
        end = data.find(")", pos)
        if start == -1 or end == -1 or end <= start + 1:
            return result

        data = data[start:end].strip("()")
        data_list = data.split(self.ID_DELIMITER)

        for item in data_list:
            item = item.strip()
            if not item:
                continue

            if id_marker:
                if item[0] == id_marker:
                    result.append(item)
            else:
                result.append(item)
        
        return result

    def _clip_remove_all_ids(self, id_marker: str = None, ids_to_remove: list = None) -> int:
        data_list = self._clip_get_all_ids()

        result_list = []
        count = 0
        for item in data_list:
            if not item:
                continue

            if id_marker is not None:
                if ids_to_remove is not None:
                    if item[2:] in ids_to_remove:
                        if item[0] == id_marker:
                            count += 1
                            continue
                else:
                    if item[0] == id_marker:
                        count += 1
                        continue

            else:
                if ids_to_remove is not None:
                    if item[2:] in ids_to_remove:
                        count += 1
                        continue
                else:
                    count += 1
                    continue

            result_list.append(item)
        
        if result_list:
            result = self.ID_LIST_MARKER + "(" + self.ID_DELIMITER.join(result_list) + ")"
        else:
            result = ""

        self._os_clip.setText(result)
        return count

    def _ids_to_list(self, ids: Union[list, str, tuple], allow_none: bool = False) -> Union[list, None]:
        if isinstance(ids, int):
            ids = [str(ids)]
        elif isinstance(ids, str):
            if ids:
                ids = [ids]
            else:
                ids = []
        elif isinstance(ids, tuple) or isinstance(ids, list):
            ids = [str(x) for x in ids]
        else:
            if allow_none and ids is None:
                ids = None
            else:
                UTILS.LogHandler.add_log_record("#1: Invalid data for #2.\ntype(block_ids) = #3\nblock_ids = #4", ["Clipboard", "ID-s", type(ids), ids], warning_raised=True)
                ids = None
        
        return ids

    def _clipboard_changed(self):
        if self._do_nothing:
            return

        file_util = FileDialog(self._stt)

        if not self._os_clip.mimeData().hasUrls():
            return
        
        self.clear_clip(leave_os_clip=True)

        img = QPixmap()

        files = [x.toLocalFile() for x in self._os_clip.mimeData().urls()]
        files = file_util.get_valid_local_files(files)
        if files:
            self._clip["os"] = []
        for file in files:
            result = img.load(file)
            self._clip["os"].append([None, file, result])

    def save_os_clip_to_database(self):
        for idx, file in enumerate(self._clip["os"]):
            if file[2]:
                result = self._add_image_to_database(file[1])
                if result is None:
                    return
                self._clip["os"][idx] = [result, file[1], file[2]]
                self.copy_to_clip(result, add_to_clip=True)
            else:
                result = self._add_file_to_database(file[1])
                if result is None:
                    return
                self._clip["os"][idx] = [result, file[1], file[2]]
                self.copy_to_clip(result, add_to_clip=True)

        self._clip["os"] = [x for x in self._clip["os"] if x[0] is None]

    def get_tooltip_hint_for_files(self) -> str:
        files_list = [x for x in self._clip["os"] if x[2] is False]
        files_list += self._clip["files"]

        if len(files_list) == 0:
            result = self.getl("clipboard_file_tooltip_no_file")
        else:
            result = self.getl("clipboard_file_tooltip_many_files").replace("#1", str(len(files_list)))
            for file in files_list:
                result += file[1] + "\n"
        
        return result

    def get_tooltip_hint_for_images(self) -> str:
        images_list = [x for x in self._clip["os"] if x[2] is True]
        images_list = images_list + self._clip["images"]
        result = '<div class="image-line">'
        if len(images_list) == 1:
            img_size = 300
        if len(images_list) > 1:
            img_size = 200
        if len(images_list) > 6:
            img_size = 150
        if len(images_list) > 9:
            img_size = 100

        if len(images_list) == 0:
            result = self.getl("clipboard_image_tooltip_no_image")
        elif len(images_list) < 13:
            
            for i in range(len(images_list)):
                if i % 4 == 0 and i != 0:
                    result += '</div><div class="image-line">'
                result += f'<img src="{images_list[i][1]}" width={img_size} />'
            result += '</div>'
            result += '<style> .image-line {display: flex;} .image-line{margin-right: 10px;}</style>'
        else:
            result = self.getl("clipboard_image_tooltip_many_images").replace("#1", str(len(images_list)))
            for image in images_list:
                result += image[1] + "\n"
        return result

    def get_tooltip_hint_for_clear_clipboard(self) -> str:
        txt = self.getl("image_menu_clear_clipboard_tt") + "\n\n"
        for i in self._clip["images"]:
            txt += i[1] + "\n"
        for i in self._clip["files"]:
            txt += i[1] + "\n"
        for i in self._clip["os"]:
            txt += i[1] + "\n"
        return txt

    def get_paste_files_ids(self) -> list:
        self.save_os_clip_to_database()
        result = list(self.files_ids)
        if self.getv("delete_clipboard_on_paste"):
            self._clip["files"] = []
        return result

    def get_paste_images_ids(self) -> list:
        self.save_os_clip_to_database()
        result = list(self.images_ids)
        if self.getv("delete_clipboard_on_paste"):
            self._clip["images"] = []
        return result

    def is_clip_empty(self) -> bool:
        result = True
        if self._clip["os"]:
            result = False
        if self._clip["images"]:
            result = False
        if self._clip["files"]:
            result = False
        return result

    def copy_to_clip(self, media_id: int, add_to_clip: bool = False) -> bool:
        result = False
        if not add_to_clip:
            self.clear_clip()
        
        if isinstance(media_id, str):
            from_url = None
            if os.path.isfile(media_id):
                from_url = media_id
            else:
                from_url = self._get_image_from_url(media_id)
            
            if from_url:
                from_url = self._get_abs_path(from_url)
                self._clip["os"].append([None, from_url, True])
                return True
            return False

        if not isinstance(media_id, int):
            return
       
        if self.is_id_in_clip(media_id):
            return False

        db_media = db_media_cls.Media(self._stt)
        item_added = False
        if db_media.is_media_exist(media_id):
            db_media.load_media(media_id)
            self._clip["images"].append([media_id, self._get_abs_path(db_media.media_file), "image"])
            self._set_to_os_clip(self._get_abs_path(db_media.media_file))
            item_added = True

        db_media = db_media_cls.Files(self._stt)
        if db_media.is_file_exist(media_id):
            db_media.load_file(media_id)
            self._clip["files"].append([media_id, self._get_abs_path(db_media.file_file), "file"])
            self._set_to_os_clip(self._get_abs_path(db_media.file_file))
            item_added = True

        return item_added

    def clear_clip(self, leave_os_clip: bool = False):
        self._clip["images"] = []
        self._clip["files"] = []
        self._clip["os"] = []
        if not leave_os_clip:
            self.get_appv("clipboard").clear()

    def is_id_in_clip(self, media_id: int) -> bool:
        result = False

        if media_id in self.images_ids:
            result = True
        if media_id in self.files_ids:
            result = True

        return result

    def _get_image_from_url(self, url: str) -> str:
        """Downloads url image and returns filename
        """
        file_util = FileDialog(self._stt)
        file_name = file_util.get_web_file_name(url)
        destination = self.getv("temp_folder_path") + file_name
        self._create_directory_structure(destination)
        
        result_dict = file_util.get_file_from_web(url, destination)

        if result_dict["result"]:
            return result_dict["file_path"]
        else:
            return None

    def _save_clipboard_to_file(self):
        self._stt.custom_dict_save(self.getv("clipboard_file_path"), self._clip)        

    def _add_file_to_database(self, file: str) -> int:
        if not os.path.isfile(file):
            QMessageBox.critical(None, self.getl("error_text"), self.getl("error_file_not_found_text") + "\n" + file, QMessageBox.Ok)
            return None
        # Find user file folder name
        user_folder = os.path.split(self.get_appv("user").db_path)[0] + f'/{self.get_appv("user").id}files/'

        # Save file to database and get ID
        db_file = db_media_cls.Files(self._stt)
        file_dict = {
            "name": "",
            "description": "",
            "file": "",
            "http": file,
            "default": 100
        }
        file_id = db_file.add_file(file_dict)

        # Set file name for user file
        file_name = f"{file_id}_" + os.path.split(file)[1]
        user_file = user_folder + file_name

        # Copy file to user folder
        abs_user_path = self._get_abs_path(user_file)
        self._create_directory_structure(abs_user_path)
        shutil.copy(file, abs_user_path)

        # Update database with user file name
        file_dict = {
            "file": user_file,
        }
        db_file.update_file(file_id, file_dict)

        obj_file = File(self._stt, file_id=file_id)
        obj_file.add_to_file_list()

        return file_id

    def _add_image_to_database(self, file: str) -> int:
        if not os.path.isfile(file):
            QMessageBox.critical(None, self.getl("error_text"), self.getl("error_file_not_found_text") + "\n" + file, QMessageBox.Ok)
            return None
        # Find user images folder name
        user_folder = os.path.split(self.get_appv("user").db_path)[0] + f'/{self.get_appv("user").id}images/'

        # Save image to database and get ID
        db_image = db_media_cls.Media(self._stt)
        image_dict = {
            "name": "",
            "description": "",
            "file": "",
            "http": file,
            "default": 0
        }
        image_id = db_image.add_media(image_dict)

        # Set file name for user file
        image_name = f"{image_id}_" + os.path.split(file)[1]
        user_image = user_folder + image_name

        # Copy file to user folder
        abs_user_path = self._get_abs_path(user_image)
        self._create_directory_structure(abs_user_path)
        shutil.copy(file, abs_user_path)

        # Update database with user file name
        image_dict = {
            "file": user_image,
        }
        db_image.update_media(image_id, image_dict)

        obj_image = Image(self._stt, image_id=image_id)
        obj_image.add_to_image_list()

        return image_id

    def _set_to_os_clip(self, file: str):
        img = QPixmap()
        result = img.load(file)
        if result:
            self._os_clip.setPixmap(img)
            return

        self._os_clip.setText(file, mode=QClipboard.Clipboard)

    def _create_directory_structure(self, file: str):
        folder = os.path.split(file)[0]

        if not os.path.isdir(folder):
            os.mkdir(folder)

    def _get_abs_path(self, file: str) -> str:
        file_util = FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt, file_path=file)
        return file_info.absolute_path()
    
    def _check_dict(self):
        file_util = FileDialog(self._stt)

        if not isinstance(self._clip, dict):
            self._clip = {}

        if not "files" in self._clip:
            self._clip["files"] = []
        if not "images" in self._clip:
            self._clip["images"] = []
        if not "os" in self._clip:
            self._clip["os"] = []

        user_images = os.path.split(self.get_appv("user").db_path)[0] + f'/{self.get_appv("user").id}images'
        user_files = os.path.split(self.get_appv("user").db_path)[0] + f'/{self.get_appv("user").id}files'

        new_images = []
        new_files = []
        new_os = []

        for item in self._clip["images"]:
            if item[1].find(self._get_abs_path(user_images)) < 0:
                new_os.append(item[1])
            else:
                new_images.append(item)

        for item in self._clip["files"]:
            if item[1].find(self._get_abs_path(user_files)) < 0:
                new_os.append(item[1])
            else:
                new_files.append(item)
        
        for item in self._clip["os"]:
            if os.path.isfile(item[1]):
                new_os.append(item[1])
    
        current_os_clip = []
        if self._os_clip.mimeData().hasUrls():
            img = QPixmap()

            files = [x.toLocalFile() for x in self._os_clip.mimeData().urls()]
            files = file_util.get_valid_local_files(files)
            for file in files:
                result = img.load(file)
                current_os_clip.append([None, file, result])

        if current_os_clip != self._clip["os"]:
            new_os = []
            new_os = [x[1] for x in current_os_clip]

        self.clear_clip(leave_os_clip=True)

        self._clip["images"] = new_images
        self._clip["files"] = new_files

        img = QPixmap()
        new_os = file_util.get_valid_local_files(new_os)
        for file in new_os:
            result = img.load(file)
            current_os_clip.append([None, file, result])
        
        self._clip["os"] = current_os_clip

    @property
    def images_ids(self) -> list:
        result = [x[0] for x in self._clip["images"]]
        return result

    @property
    def files_ids(self) -> list:
        result = [x[0] for x in self._clip["files"]]
        return result

    @property
    def os_ids(self) -> list:
        result = [x[0] for x in self._clip["os"]]
        return result

    @property
    def number_of_images_in_clip(self) -> int:
        os_img = [x for x in self._clip["os"] if x[2]]
        result = len(self._clip["images"]) + len(os_img)
        return result
    
    @property
    def number_of_files_in_clip(self) -> int:
        os_files = [x for x in self._clip["os"] if not x[2]]
        result = len(self._clip["files"]) + len(os_files)
        return result
    

class ClipboardView(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._clip: Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("clipboard_view_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self._populate_widgets()

        self.chk_del_close.setChecked(self.getv("delete_clipboard_on_app_exit"))
        self.chk_del_paste.setChecked(self.getv("delete_clipboard_on_paste"))
        self.chk_del_tmp.setChecked(self.getv("delete_temp_folder_on_app_exit"))

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.tree_clip.currentChanged = self._tree_clip_current_changed
        self.btn_del_tmp.clicked.connect(self._btn_del_tmp_click)
        self.btn_clear.clicked.connect(self._btn_clear_click)
        self.btn_close.clicked.connect(self._btn_close_click)
        self.btn_refresh.clicked.connect(self._btn_refresh_click)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["ClipboardView"])

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets
        self.widget_handler.add_all_ItemBased_Widgets()

        self.widget_handler.activate()

    def _btn_refresh_click(self):
        self._clear_item_data()
        self._populate_widgets()

    def _btn_close_click(self):
        self.close()

    def _btn_clear_click(self):
        self._clip.clear_clip()
        self._populate_widgets()
        UTILS.LogHandler.add_log_record("#1: Clipboard cleared.", ["ClipboardView"])

    def _btn_del_tmp_click(self):
        file_util = FileDialog(self._stt)
        file_util.delete_temp_folder()
        self._populate_widgets()
        UTILS.LogHandler.add_log_record("#1: Temp folder cleared.", ["ClipboardView"])

    def _tree_clip_current_changed(self, x, y):
        if self.tree_clip.currentItem() is not None:
            self._show_item_data(self.tree_clip.currentItem().text(0))
    
    def _show_item_data(self, filename: str):
        self._clear_item_data()
        file_util = FileDialog(self._stt)
        if not os.path.isfile(filename):
            return

        file_info = file_util.FileInfo(self._stt, filename)

        self.lbl_clip_title.setText(self.tree_clip.currentItem().parent().text(0))

        self.lbl_size_val.setText(file_info.size_formated())
        self.lbl_file_val.setText(filename)
        
        img = QPixmap()
        img.load(filename)
        size = self.lbl_pic.size()
        img = img.scaled(size.width(), size.height(), Qt.KeepAspectRatio)
        self.lbl_pic.setPixmap(img)

    def _clear_item_data(self):
        self.lbl_clip_title.setText("")
        self.lbl_size_val.setText("")
        self.lbl_file_val.setText("")
        self.lbl_pic.setPixmap(QPixmap())

    def _populate_widgets(self):
        self.tree_clip.clear()
        self.tree_clip.invisibleRootItem().setText(0, "Clipboard")

        self._clip_int_img = QTreeWidgetItem()
        self._clip_int_img.setText(0, self.getl("clipboard_view_tree_item_int_img_text"))
        self._clip_int_file = QTreeWidgetItem()
        self._clip_int_file.setText(0, self.getl("clipboard_view_tree_item_int_file_text"))
        self._clip_os = QTreeWidgetItem()
        self._clip_os.setText(0, self.getl("clipboard_view_tree_item_os_text"))
        self._clip_tmp = QTreeWidgetItem()
        self._clip_tmp.setText(0, self.getl("clipboard_view_tree_item_tmp_text"))


        self.tree_clip.addTopLevelItem(self._clip_int_img)
        self.tree_clip.addTopLevelItem(self._clip_int_file)
        self.tree_clip.addTopLevelItem(self._clip_os)
        self.tree_clip.addTopLevelItem(self._clip_tmp)

        self._populate_data()

    def _populate_data(self):
        for file in self._clip._clip["images"]:
            item = QTreeWidgetItem()
            item.setText(0, file[1])
            item.setToolTip(0, f'{file[2]}\nID: {file[0]}\n{file[1]}')
            self._clip_int_img.addChild(item)
        for file in self._clip._clip["files"]:
            item = QTreeWidgetItem()
            item.setText(0, file[1])
            item.setToolTip(0, f'{file[2]}\nID: {file[0]}\n{file[1]}')
            self._clip_int_file.addChild(item)
        for file in self._clip._clip["os"]:
            item = QTreeWidgetItem()
            item.setText(0, file[1])
            item.setToolTip(0, file[1])
            self._clip_os.addChild(item)

        files = os.listdir(self.getv("temp_folder_path").strip("/"))
        for file in files:
            item = QTreeWidgetItem()
            txt = self.getv("temp_folder_path") + file
            item.setText(0, txt)
            item.setToolTip(0, txt)
            self._clip_tmp.addChild(item)

        self._clip_int_img.setExpanded(True)
        self._clip_int_file.setExpanded(True)
        self._clip_os.setExpanded(True)
        self._clip_tmp.setExpanded(True)

    def _load_win_position(self):
        if "clipboard_view_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("clipboard_view_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "clipboard_view_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("clipboard_view_win_geometry", {}, save_to_file=True)

        g = self.get_appv("clipboard_view_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        self.setv("delete_clipboard_on_app_exit", self.chk_del_close.isChecked())
        self.setv("delete_clipboard_on_paste", self.chk_del_paste.isChecked())
        self.setv("delete_temp_folder_on_app_exit", self.chk_del_tmp.isChecked())

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["ClipboardView"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_clip_title: QLabel = self.findChild(QLabel, "lbl_clip_title")
        self.lbl_size: QLabel = self.findChild(QLabel, "lbl_size")
        self.lbl_size_val: QLabel = self.findChild(QLabel, "lbl_size_val")
        self.lbl_file: QLabel = self.findChild(QLabel, "lbl_file")
        self.lbl_file_val: QLabel = self.findChild(QLabel, "lbl_file_val")
        self.lbl_clip: QLabel = self.findChild(QLabel, "lbl_clip")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")

        self.chk_del_close: QCheckBox = self.findChild(QCheckBox, "chk_del_close")
        self.chk_del_paste: QCheckBox = self.findChild(QCheckBox, "chk_del_paste")
        self.chk_del_tmp: QCheckBox = self.findChild(QCheckBox, "chk_del_tmp")

        self.btn_del_tmp: QPushButton = self.findChild(QPushButton, "btn_del_tmp")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_clear: QPushButton = self.findChild(QPushButton, "btn_clear")
        self.btn_refresh: QPushButton = self.findChild(QPushButton, "btn_refresh")

        self.tree_clip: QTreeWidget = self.findChild(QTreeWidget, "tree_clip")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("clipboard_view_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("clipboard_view_lbl_title_tt"))

        self.lbl_clip_title.setText("")

        self.lbl_size.setText(self.getl("clipboard_view_lbl_size_text"))
        self.lbl_size.setToolTip(self.getl("clipboard_view_lbl_size_tt"))

        self.lbl_size_val.setText("")

        self.lbl_file.setText(self.getl("clipboard_view_lbl_file_text"))
        self.lbl_file.setToolTip(self.getl("clipboard_view_lbl_file_tt"))

        self.lbl_file_val.setText("")

        self.lbl_clip.setText(self.getl("clipboard_view_lbl_clip_text"))
        self.lbl_clip.setToolTip(self.getl("clipboard_view_lbl_clip_tt"))

        self.lbl_pic.setText("")

        self.chk_del_close.setText(self.getl("clipboard_view_chk_del_close_text"))
        self.chk_del_close.setToolTip(self.getl("clipboard_view_chk_del_close_tt"))

        self.chk_del_paste.setText(self.getl("clipboard_view_chk_del_paste_text"))
        self.chk_del_paste.setToolTip(self.getl("clipboard_view_chk_del_paste_tt"))

        self.chk_del_tmp.setText(self.getl("clipboard_view_chk_del_tmp_text"))
        self.chk_del_tmp.setToolTip(self.getl("clipboard_view_chk_del_tmp_tt"))

        self.btn_del_tmp.setText(self.getl("clipboard_view_btn_del_tmp_text"))
        self.btn_del_tmp.setToolTip(self.getl("clipboard_view_btn_del_tmp_tt"))

        self.btn_close.setText(self.getl("clipboard_view_btn_close_text"))
        self.btn_close.setToolTip(self.getl("clipboard_view_btn_close_tt"))

        self.btn_clear.setText(self.getl("clipboard_view_btn_clear_text"))
        self.btn_clear.setToolTip(self.getl("clipboard_view_btn_clear_tt"))

        self.btn_refresh.setText(self.getl("clipboard_view_btn_refresh_text"))
        self.btn_refresh.setToolTip(self.getl("clipboard_view_btn_refresh_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["ClipboardView"])
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_clipboard_view_win_apperance()
        self._define_labels_apperance(self.lbl_title, "clipboard_view_lbl_title")
        self._define_labels_apperance(self.lbl_clip_title, "clipboard_view_lbl_clip_title")
        self._define_labels_apperance(self.lbl_size, "clipboard_view_lbl_size")
        self._define_labels_apperance(self.lbl_size_val, "clipboard_view_lbl_size_val")
        self._define_labels_apperance(self.lbl_file, "clipboard_view_lbl_file")
        self._define_labels_apperance(self.lbl_file_val, "clipboard_view_lbl_file_val")
        self._define_labels_apperance(self.lbl_pic, "clipboard_view_lbl_pic")
        self._define_labels_apperance(self.lbl_clip, "clipboard_view_lbl_clip")
        
        self.chk_del_close.setStyleSheet(self.getv("clipboard_view_chk_del_close_stylesheet"))
        self.chk_del_paste.setStyleSheet(self.getv("clipboard_view_chk_del_paste_stylesheet"))
        self.chk_del_tmp.setStyleSheet(self.getv("clipboard_view_chk_del_tmp_stylesheet"))

        self.tree_clip.setStyleSheet(self.getv("clipboard_view_tree_clip_stylesheet"))
        self.tree_clip.setHeaderHidden(True)

        self._define_button(self.btn_del_tmp, "clipboard_view_btn_del_tmp")
        self._define_button(self.btn_close, "clipboard_view_btn_close")
        self._define_button(self.btn_clear, "clipboard_view_btn_clear")
        self._define_button(self.btn_refresh, "clipboard_view_btn_refresh")

    def _define_clipboard_view_win_apperance(self):
        self.setStyleSheet(self.getv("clipboard_view_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("clipboard_view_win_icon_path")))
        self.setWindowTitle(self.getl("clipboard_view_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(1025, 535)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_button(self, button: QPushButton, name: str):
        button.setStyleSheet(self.getv(f"{name}_stylesheet"))
        button.setFlat(self.getv(f"{name}_flat"))
        button.setShortcut(self.getv(f"{name}_shortcut"))
        button.setIcon(QIcon(QPixmap(self.getv(f"{name}_icon_path"))))


class MediaExplorer(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        self._dont_clear_menu = False
        self._dont_send_signals = True

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)
        self.setWindowModality(Qt.ApplicationModal)

        # Define other variables
        self._parent_widget = parent_widget
        self.db_images = db_media_cls.Media(self._stt)
        self.db_files = db_media_cls.Files(self._stt)
        self._abort_operation = False
        self._clip: Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("media_explorer_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_progress_abort.clicked.connect(self._btn_progress_abort_click)
        self.btn_refresh.clicked.connect(self._btn_refresh_click)
        self.rbt_both.toggled.connect(self._rbt_both_toggled)
        self.rbt_file.toggled.connect(self._rbt_file_toggled)
        self.rbt_img.toggled.connect(self._rbt_img_toggled)
        self.chk_not_used.toggled.connect(self._chk_not_used_toggled)
        self.btn_find.clicked.connect(self._btn_find_click)
        self.txt_find.returnPressed.connect(self._btn_find_click)
        self.lst_items.currentItemChanged.connect(self._lst_items_current_item_changed)
        self.lst_items.mouseReleaseEvent = self._lst_items_mouse_release
        self.btn_duplicates.clicked.connect(self._btn_duplicates_click)
        self.tree_duplicates.currentChanged = self._tree_duplicates_current_changed
        self.tree_duplicates.mouseReleaseEvent = self._tree_duplicates_mouse_release
        self.btn_delete.clicked.connect(self._btn_delete_click)
        self.btn_delete_all.clicked.connect(self._btn_delete_all_click)
        self.btn_close.clicked.connect(self._btn_close_click)
        self.lbl_pic.mousePressEvent = self._lbl_pic_mouse_press
        self.btn_delete_duplicates.clicked.connect(self._btn_delete_duplicates_click)

        self.show()
        QCoreApplication.processEvents()
        self.get_appv("signal").send_close_all_blocks()
        self.get_appv("signal").send_close_all_definitions()
        self._dont_send_signals = False
        self._populate_widgets()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["MediaExplorer"])

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_find)

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets
        self.widget_handler.add_all_ItemBased_Widgets()

        self.widget_handler.activate()

    def _tree_duplicates_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            if self.tree_duplicates.currentItem() is not None:
                if self.tree_duplicates.currentItem().data(0, Qt.UserRole):
                    self._show_pic_context_menu(show_delete_duplicates=True)
        QTreeWidget.mouseReleaseEvent(self.tree_duplicates, e)

    def _lst_items_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            if self.lst_items.currentItem() is not None:
                self._show_pic_context_menu()
        QListWidget.mouseReleaseEvent(self.lst_items, e)

    def _lbl_pic_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self._show_pic_context_menu()

    def _show_pic_context_menu(self, show_delete_duplicates: bool = False):
        disab = []
        media_id = None
        if self.tree_duplicates.isVisible():
            if self.tree_duplicates.currentItem() is not None:
                media_id = self.tree_duplicates.currentItem().data(0, Qt.UserRole)
            if show_delete_duplicates:
                if self.tree_duplicates.currentItem().parent().childCount() <= 1:
                    disab.append(50)
        else:
            if self.lst_items.currentItem() is not None:
                media_id = self.lst_items.currentItem().data(Qt.UserRole)

        if media_id is None:
            return

        if self.db_images.is_media_exist(media_id):
            image = True
        else:
            image = False

        if self._clip.is_clip_empty():
            disab.append(40)

        if image:
            menu_dict = {
                "position": QCursor.pos(),
                "separator": [10],
                "disabled": disab,
                "items": [
                        [
                            10,
                            self.getl("media_explorer_lbl_pic_menu_image_open_text"),
                            self.getl("media_explorer_lbl_pic_menu_image_open_tt"),
                            True,
                            [],
                            self.lbl_pic.pixmap()
                        ],
                        [
                            20,
                            self.getl("image_menu_copy_text"),
                            self.getl("image_menu_copy_tt"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            30,
                            self.getl("image_menu_add_to_clip_text"),
                            self.getl("image_menu_add_to_clip_tt"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            40,
                            self.getl("image_menu_clear_clipboard_text"),
                            self._clip.get_tooltip_hint_for_clear_clipboard(),
                            True,
                            [],
                            self.getv("clear_clipboard_icon_path")
                        ]
                ]
            }
        else:
            menu_dict = {
                "position": QCursor.pos(),
                "separator": [10],
                "disabled": disab,
                "items": [
                        [
                            10,
                            self.getl("media_explorer_lbl_pic_menu_file_open_text"),
                            self.getl("media_explorer_lbl_pic_menu_file_open_tt"),
                            True,
                            [],
                            self.lbl_pic.pixmap()
                        ],
                        [
                            20,
                            self.getl("file_menu_copy_text"),
                            self.getl("file_menu_copy_tt"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            30,
                            self.getl("file_menu_add_to_clip_text"),
                            self.getl("file_menu_add_to_clip_tt"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            40,
                            self.getl("image_menu_clear_clipboard_text"),
                            self._clip.get_tooltip_hint_for_clear_clipboard(),
                            True,
                            [],
                            self.getv("clear_clipboard_icon_path")
                        ]
                ]
            }
        
        if show_delete_duplicates:
            menu_dict["separator"].append(40)
            menu_dict["items"].append([50, self.getl("media_explorer_menu_remove_duplicates_text"), self.getl("media_explorer_menu_remove_duplicates_tt"), True, [], self.getv("media_explorer_remove_duplicates_icon_path")])

        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]
        if result == 10:
            file_util = FileDialog(self._stt)
            file_info = file_util.FileInfo(self._stt)
            if image:
                self.db_images.load_media(media_id)
                os.startfile(file_info.absolute_path(self.db_images.media_file))
            else:
                self.db_files.load_file(media_id)
                os.startfile(file_info.absolute_path(self.db_files.file_file))
        elif result == 20:
            self._clip.copy_to_clip(media_id)
        elif result == 30:
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif result == 40:
            self._clip.clear_clip()
        elif result == 50:
            self._replace_duplicates(self.tree_duplicates.currentItem().parent(), base_item=self.tree_duplicates.currentItem())

    def _replace_duplicates(self, parent_item: QTreeWidgetItem, base_item: QTreeWidgetItem = None) -> bool:
        if parent_item.childCount() <= 1:
            return False
        
        if base_item is None:
            base_item = parent_item.child(0)
        
        repl_with = base_item.data(0, Qt.UserRole)

        repl_ids = []
        for i in range(parent_item.childCount()):
            media_id = parent_item.child(i).data(0, Qt.UserRole)
            if media_id != repl_with:
                repl_ids.append([media_id, parent_item.child(i)])
        
        db_rec_data = db_record_data_cls.RecordData(self._stt)
        db_def = db_definition_cls.Definition(self._stt)

        for i in repl_ids:
            blocks_ids, defs_ids = self._get_blocks_and_defs_that_use_media(i[0])
            
            for block in blocks_ids:
                rec_data_dict = db_rec_data.get_record_data_dict(block)

                for idx, j in enumerate(rec_data_dict["media"]):
                    if j == i[0]:
                        if repl_with in rec_data_dict["media"]:
                            rec_data_dict["media"].pop(idx)
                        else:
                            rec_data_dict["media"][idx] = repl_with
                for idx, j in enumerate(rec_data_dict["files"]):
                    if j == i[0]:
                        if repl_with in rec_data_dict["files"]:
                            rec_data_dict["files"].pop(idx)
                        else:
                            rec_data_dict["files"][idx] = repl_with
                    
                db_rec_data.update_record_data(rec_data_dict, block)
            
            for definition in defs_ids:
                db_def.load_definition(definition)
                def_dict = {}
                def_dict["media_ids"] = db_def.definition_media_ids
                for idx, j in enumerate(def_dict["media_ids"]):
                    if j == i[0]:
                        if repl_with in def_dict["media_ids"]:
                            def_dict["media_ids"].pop(idx)
                        else:
                            def_dict["media_ids"][idx] = repl_with
                db_def.update_definition(definition, def_dict)

        for i in range(len(repl_ids)):
            self._delete_media(repl_ids[0][0])
            repl_ids.pop(0)

        self._populate_data(repl_with)
    
    def _get_blocks_and_defs_that_use_media(self, media_id: int):
        db_media = db_media_cls.Media(self._stt)
        if db_media.is_media_exist(media_id):
            db_media.load_media(media_id)
            blocks_ids = db_media.get_block_ids_that_use_media(media_id)
            defs_ids = db_media.get_definition_ids_that_use_media(media_id)
        else:
            db_media = db_media_cls.Files(self._stt)
            if db_media.is_file_exist(media_id):
                db_media.load_file(media_id)
                blocks_ids = db_media.get_block_ids_that_use_file(media_id)
                defs_ids = []
            else:
                self.lbl_type.setText("Error.")
                return [], []

        return blocks_ids, defs_ids

    def _btn_delete_duplicates_click(self):
        if not self._msg_question_replace_all_duplicates():
            return
        
        UTILS.LogHandler.add_log_record("#1: About to delete all duplicates.", ["MediaExplorer"])
        # Set progress frame
        self.frm_progress.setVisible(True)

        for root_idx in range(self.tree_duplicates.topLevelItemCount()):
            self.prg_progress.setMaximum(self.tree_duplicates.topLevelItem(root_idx).childCount())
            self.prg_progress.setValue(0)

            for parent_idx in range(self.tree_duplicates.topLevelItem(root_idx).childCount()):
                self._replace_duplicates(self.tree_duplicates.topLevelItem(root_idx).child(parent_idx))

                # Check for Abort from user
                if self._abort_operation:
                    break

                # Update progress
                self.prg_progress.setValue(parent_idx)
                QCoreApplication.processEvents()

        self.frm_progress.setVisible(False)

        if self._abort_operation:
            self.btn_refresh.setVisible(True)
            self._abort_operation = False
            self._show_msg_aborted()
            UTILS.LogHandler.add_log_record("#1: Delete duplicates aborted by user.\nNot all duplicates could be removed.", ["MediaExplorer"])
        else:
            UTILS.LogHandler.add_log_record("#1: Duplicates deleted.", ["MediaExplorer"])
            self.btn_refresh.setVisible(False)

    def _btn_close_click(self):
        self.close()

    def _btn_delete_all_click(self):
        if not self._msg_question_delete_all_media():
            return

        self._items_list = self.db_images.get_all_media() + self.db_files.get_all_file()
        self._items_list = [[y for y in x] + [True] for x in self._items_list]

        # Set progress frame
        self.frm_progress.setVisible(True)
        self.prg_progress.setValue(0)
        self.prg_progress.setMaximum(len(self._items_list))
        scale = int(len(self._items_list) / 100)
        if scale < 1:
            scale = 1

        count = 0
        items = list(self._items_list)
        for idx, media in enumerate(items):
            if self._delete_media(media[0]):
                count += 1
            # Update progress
            if idx % scale == 0:
                self.prg_progress.setValue(idx)
                QCoreApplication.processEvents()

        self.frm_progress.setVisible(False)

        if self._abort_operation:
            self.btn_refresh.setVisible(True)
            self._abort_operation = False
            self._show_msg_aborted()
        else:
            self.btn_refresh.setVisible(False)

        UTILS.LogHandler.add_log_record("#1: Unused media is deleted.", ["MediaExplorer"])
        msg_dict = {
            "title": self.getl("media_explorer_msg_media_deleted_all_title"),
            "text": self.getl("media_explorer_msg_media_deleted_all_text").replace("#1", str(count))
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict, app_modal=True)

    def _update_counter(self):
        count = 0
        if self.tree_duplicates.isVisible():
            for i in range(self.tree_duplicates.topLevelItemCount()):
                root_item = self.tree_duplicates.topLevelItem(i)
                for j in range(root_item.childCount()):
                    parent_item = root_item.child(j)
                    count += parent_item.childCount()
        else:
            count = self.lst_items.count()

        self.lbl_count.setText(self.getl("media_explorer_lbl_count_text").replace("#1", str(count)).replace("#2", str(len(self._items_list))))

    def _btn_delete_click(self):
        if self.tree_duplicates.isVisible():
            if self.tree_duplicates.currentItem() is not None:
                media_id = self.tree_duplicates.currentItem().data(0, Qt.UserRole)
            else:
                return
        else:
            if self.lst_items.currentItem() is not None:
                media_id = self.lst_items.currentItem().data(Qt.UserRole)
            else:
                return
        if not media_id:
            return

        UTILS.LogHandler.add_log_record("#1: About to delete media. (ID=#2)", ["MediaExplorer", media_id])
        if self._is_media_safe_to_delete(media_id):
            if not self._msg_question_delete_media(media_id):
                UTILS.LogHandler.add_log_record("#1: Delete media aborted by user.", ["MediaExplorer"])
                return
            self._delete_media(media_id)
        else:
            UTILS.LogHandler.add_log_record("#1: Media could not be deleted. Reason: #2", ["MediaExplorer", "In use in some block or definition"])
            self._msg_media_is_used(media_id)
            return

        UTILS.LogHandler.add_log_record("#1: Media is deleted. (ID=#2)", ["MediaExplorer", media_id])
        self._msg_media_is_deleted()

    def _msg_media_is_deleted(self):
        msg_dict = {
            "title": self.getl("media_explorer_msg_media_deleted_title"),
            "text": self.getl("media_explorer_msg_media_deleted_text")
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict, app_modal=True)

    def _msg_media_is_used(self, media_id: int = None):
        txt = self.getl("media_explorer_msg_media_used_text")
        if media_id is not None:
            if self.db_images.is_media_exist(media_id):
                self.db_images.load_media(media_id)
                txt = f'<img src="{self.db_images.media_file}" width=150><br>' + txt.replace("#1", "<br>" + self.db_images.media_file)
            else:
                self.db_files.load_file(media_id)
                txt = txt.replace("#1", self.db_files.file_file)
        else:
            txt = txt.replace("#1", "")

        msg_dict = {
            "title": self.getl("media_explorer_msg_media_used_title"),
            "text": txt
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, msg_dict, app_modal=True)

    def _msg_question_delete_media(self, media_id: int) -> bool:
        txt = self.getl("media_explorer_delete_text")

        if self.db_images.is_media_exist(media_id):
            self.db_images.load_media(media_id)
            txt = f'<img src="{self.db_images.media_file}" width=150><br>' + txt.replace("#1", "<br>" + self.db_images.media_file)
        else:
            self.db_files.load_file(media_id)
            txt = txt.replace("#1", self.db_files.file_file)

        msg_dict = {
            "title": self.getl("media_explorer_delete_title"),
            "text": txt,
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True],
            ]
        }
        self._dont_clear_menu = True
        MessageQuestion(self._stt, self, msg_dict)
        if msg_dict["result"] == 10:
            return True
        return False

    def _msg_question_replace_all_duplicates(self) -> bool:
        msg_dict = {
            "title": self.getl("media_explorer_msg_question_delete_all_duplicates_title"),
            "text": self.getl("media_explorer_msg_question_delete_all_duplicates_text"),
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True],
            ]
        }
        self._dont_clear_menu = True
        MessageQuestion(self._stt, self, msg_dict)
        if msg_dict["result"] == 10:
            return True
        return False

    def _msg_question_delete_all_media(self) -> bool:
        msg_dict = {
            "title": self.getl("media_explorer_delete_all_title"),
            "text": self.getl("media_explorer_delete_all_text"),
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True],
            ]
        }
        self._dont_clear_menu = True
        MessageQuestion(self._stt, self, msg_dict)
        if msg_dict["result"] == 10:
            return True
        return False

    def _is_media_safe_to_delete(self, media_id: int) -> bool:
        if self.db_images.is_media_exist(media_id):
            self.db_images.load_media(media_id)
            return self.db_images.is_safe_to_delete(media_id)
        else:
            self.db_files.load_file(media_id)
            return self.db_files.is_safe_to_delete(media_id)

    def _delete_media(self, media_id: int) -> bool:
        if not self._is_media_safe_to_delete(media_id):
            return False
        
        result = None
        if self.db_images.is_media_exist(media_id):
            result = self.db_images.delete_media(media_id)
        else:
            result = self.db_files.delete_file(media_id)

        if self.tree_duplicates.isVisible():
            self._remove_item_from_tree(media_id)
            self._remove_item_from_list_items(media_id)
        else:
            self._remove_item_from_list_items(media_id)
        
        if result is not None:
            for idx, i in enumerate(self._items_list):
                if i[0] == media_id:
                    self._items_list.pop(idx)
                    break
            self._update_counter()
            self._clip.clear_clip()
            return True
        else:
            return False

    def _remove_item_from_list_items(self, media_id: int):
        for i in range(self.lst_items.count()):
            if self.lst_items.item(i).data(Qt.UserRole) == media_id:
                self.lst_items.takeItem(i)
                break

    def _remove_item_from_tree(self, media_id: int):
        for i in range(self.tree_duplicates.topLevelItemCount()):
            root_item = self.tree_duplicates.topLevelItem(i)
            for j in range(root_item.childCount()):
                parent_item = root_item.child(j)
                for k in range(parent_item.childCount()):
                    item = parent_item.child(k)
                    if item.data(0, Qt.UserRole) == media_id:
                        parent_item.removeChild(item)
                        return

    def _tree_duplicates_current_changed(self, x, y):
        if self.tree_duplicates.currentItem() is not None:
            id = self.tree_duplicates.currentItem().data(0, Qt.UserRole)
            if id:
                self._populate_data(id)

    def _btn_duplicates_click(self):
        if self.btn_duplicates.isChecked():
            self.btn_refresh.setVisible(False)
            self.rbt_both.setEnabled(False)
            self.rbt_img.setEnabled(False)
            self.rbt_file.setEnabled(False)
            self.chk_not_used.setEnabled(False)
            self.txt_find.setVisible(False)
            self.btn_find.setVisible(False)
            self.tree_duplicates.setVisible(True)
            self.btn_delete_duplicates.setVisible(True)
            self._calculate_duplicates()
        else:
            self.btn_refresh.setVisible(False)
            self.rbt_both.setEnabled(True)
            self.rbt_img.setEnabled(True)
            self.rbt_file.setEnabled(True)
            self.chk_not_used.setEnabled(True)
            self.txt_find.setVisible(True)
            self.btn_find.setVisible(True)
            self.tree_duplicates.setVisible(False)
            self.btn_delete_duplicates.setVisible(False)
            self._populate_widgets()

    def _calculate_duplicates(self):
        self._duplicates = {
            "img": {},
            "file": {}
        }
        # Find all file sizes
        self.frm_progress.setVisible(True)
        self.prg_progress.setValue(0)
        self.prg_progress.setMaximum(len(self._items_list))
        scale = int(len(self._items_list) / 100)
        if scale < 1:
            scale = 1

        file_util = FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt)
        file_sizes = []
        for idx, file in enumerate(self._items_list):
            file_sizes.append([file_info.size(file[3]), file[0], file[5], file[3]])

            # Update progress
            if idx % scale == 0:
                self.prg_progress.setValue(idx)
                QCoreApplication.processEvents()

            if self._abort_operation:
                break

        if self._abort_operation:
            self.frm_progress.setVisible(False)
            self.btn_refresh.setVisible(True)
            self._populate_tree_widget()
            self._abort_operation = False
            return
        else:
            self.btn_refresh.setVisible(False)

        file_sizes.sort()
        
        # Find Duplicates
        has_dupl = False
        count = 0
        j = 0
        for idx, i in enumerate(file_sizes):
            if idx < j:
                continue

            if i[2] < 100:
                media_type = "img"
            else:
                media_type = "file"

            for j in range(idx + 1 ,len(file_sizes)):
                if i[0] == file_sizes[j][0] and i[1] != file_sizes[j][1] and i[2] == file_sizes[j][2]:
                    if not file_info.are_files_equal(i[3], file_sizes[j][3]):
                        continue

                    if not has_dupl:
                        count += 1
                        duplicate_name = self.getl("duplicate_text").replace("#1", str(count))
                        self._duplicates[media_type][duplicate_name] = []
                        self._duplicates[media_type][duplicate_name].append(i)
                        self._duplicates[media_type][duplicate_name].append(file_sizes[j])
                        has_dupl = True
                    else:
                        self._duplicates[media_type][duplicate_name].append(file_sizes[j])
                else:
                    has_dupl = False
                    break
            
            # Update progress
            if idx % scale == 0:
                self.prg_progress.setValue(idx)
                QCoreApplication.processEvents()

            if self._abort_operation:
                break

        if self._abort_operation:
            self.frm_progress.setVisible(False)
            self.btn_refresh.setVisible(True)
            self._populate_tree_widget()
            self._abort_operation = False
            return
        else:
            self.btn_refresh.setVisible(False)

        self._populate_tree_widget()
        self.frm_progress.setVisible(False)

    def _populate_tree_widget(self):
        self.tree_duplicates.clear()
        
        img_item = QTreeWidgetItem()
        img_item.setText(0, self.getl("image_text"))
        file_item = QTreeWidgetItem()
        file_item.setText(0, self.getl("file_text"))
        self.tree_duplicates.addTopLevelItem(img_item)
        self.tree_duplicates.addTopLevelItem(file_item)

        for dupl in self._duplicates["img"]:
            dupl_item = QTreeWidgetItem()
            dupl_item.setText(0, dupl)
            img_item.addChild(dupl_item)

            for i in self._duplicates["img"][dupl]:
                item = QTreeWidgetItem()
                item.setText(0, i[3])
                item.setData(0, Qt.UserRole, i[1])
                dupl_item.addChild(item)

        for dupl in self._duplicates["file"]:
            dupl_item = QTreeWidgetItem()
            dupl_item.setText(0, dupl)
            file_item.addChild(dupl_item)

            for i in self._duplicates["file"][dupl]:
                item = QTreeWidgetItem()
                item.setText(0, i[3])
                item.setData(0, Qt.UserRole, i[1])
                dupl_item.addChild(item)

        img_item.setExpanded(True)
        file_item.setExpanded(True)

    def _lst_items_current_item_changed(self, x, y):
        if self.lst_items.currentItem() is not None:
            self._populate_data(self.lst_items.currentItem().data(Qt.UserRole))

    def _btn_find_click(self):
        self._populate_widgets()

    def _filter_apply(self, filter: str, text: str) -> bool:
        """Checking whether the text meets the filter criteria.
        SPACE = AND operator
        / = OR operator
        """
        if filter.find("/") >= 0:
            filter_items = [x.strip() for x in filter.split("/") if x.strip() != ""]
            filter_true = False
            for item in filter_items:
                if text.find(item) >= 0:
                    filter_true = True
                    break
            return filter_true
        elif filter.strip().find(" ") >= 0:
            filter_items = [x.strip() for x in filter.split(" ") if x.strip() != ""]
            filter_true = True
            for item in filter_items:
                if text.find(item) == -1:
                    filter_true = False
                    break
            return filter_true
        else:
            if text.find(filter) == -1:
                return False
            else:
                return True

    def _chk_not_used_toggled(self):
        self._populate_widgets()

    def _rbt_both_toggled(self):
        if self.rbt_both.isChecked():
            self._populate_widgets()

    def _rbt_file_toggled(self):
        if self.rbt_file.isChecked():
            self._populate_widgets()

    def _rbt_img_toggled(self):
        if self.rbt_img.isChecked():
            self._populate_widgets()

    def _btn_refresh_click(self):
        self._btn_duplicates_click()

    def _btn_progress_abort_click(self):
        self._abort_operation = True

    def _populate_data(self, media_id: int):
        self.lbl_pic.setPixmap(QPixmap())
        self.lbl_type.setToolTip("")

        file_util = FileDialog(self._stt)

        db_media = db_media_cls.Media(self._stt)
        if db_media.is_media_exist(media_id):
            db_media.load_media(media_id)
            file_image = QPixmap()
            file_image.load(db_media.media_file)
            file_image = file_image.scaled(self.lbl_pic.width(), self.lbl_pic.height(), Qt.KeepAspectRatio)

            if db_media.media_http[:4] == "http" and db_media.media_http[:14] != "http_clipboard":
                file_name = file_util.get_web_file_name(db_media.media_http)
            else:
                valid_file = file_util.get_valid_local_files([db_media.media_http])
                if valid_file:
                    file_name = os.path.split(db_media.media_http)[1]
                else:
                    file_name = self.getl("image_text")
        else:
            db_media = db_media_cls.Files(self._stt)

            if db_media.is_file_exist(media_id):
                db_media.load_file(media_id)
                file_info = file_util.FileInfo(self._stt, db_media.file_file)
                file_image = file_util.get_file_type_image(db_media.file_file, self.lbl_pic.size())
                if not file_image:
                    file_image = file_info.icon(db_media.file_file).pixmap(QSize(32, 32))
                if not file_image:
                    file_image = QPixmap()

                file_name = file_info.get_file_exstension_short_formated(db_media.file_file)
                if not file_name:
                    valid_file = file_util.get_valid_local_files([db_media.file_http])
                    if valid_file:
                        file_name = os.path.split(db_media.file_http)[1]
                    else:
                        file_name = f'({file_info.file_extension()}) {self.getl("file_text")}'
            else:
                self.lbl_type.setText("Error.")
                return

        self.lbl_type.setText(file_name)
        self.lbl_type.setToolTip(file_name)
        self.lbl_pic.setPixmap(file_image)

        self._populate_used_list(media_id)

    def _populate_used_list(self, media_id: int):
        if media_id == None:
            return
        
        self.lst_used.clear()

        db_media = db_media_cls.Media(self._stt)
        if db_media.is_media_exist(media_id):
            db_media.load_media(media_id)
            blocks_ids = db_media.get_block_ids_that_use_media(media_id)
            defs_ids = db_media.get_definition_ids_that_use_media(media_id)
        else:
            db_media = db_media_cls.Files(self._stt)
            if db_media.is_file_exist(media_id):
                db_media.load_file(media_id)
                blocks_ids = db_media.get_block_ids_that_use_file(media_id)
                defs_ids = []
            else:
                self.lbl_type.setText("Error.")
                return

        if blocks_ids:
            db_rec = db_record_cls.Record(self._stt)
            for i in blocks_ids:
                db_rec.load_record(i)
                item = QListWidgetItem()
                txt = self.getl("picture_info_lst_used_item_block_text")
                txt += f' ({db_rec.RecordID}) '
                txt += db_rec.RecordDate
                if db_rec.RecordName:
                    txt += f" - {db_rec.RecordName}"
                item.setText(txt)
                item.setToolTip(db_rec.RecordBody)
                item.setData(Qt.UserRole, f"BLOCK: {db_rec.RecordID}")
                self.lst_used.addItem(item)

        if defs_ids:
            db_def = db_definition_cls.Definition(self._stt)
            for i in defs_ids:
                db_def.load_definition(i)
                item = QListWidgetItem()
                txt = self.getl("picture_info_lst_used_item_definition_text")
                txt += db_def.definition_name
                item.setText(txt)
                item.setData(Qt.UserRole, f"DEFINITION: {db_def.definition_id}")
                self.lst_used.addItem(item)

        if self.lst_used.count():
            self.lst_used.setCurrentRow(0)
        else:
            item = QListWidgetItem()
            txt = self.getl("picture_info_lst_used_item_no_data_text")
            item.setText(txt)
            item.setData(Qt.UserRole, f"NOT_USED")
            self.lst_used.addItem(item)

    def _populate_widgets(self):
        self._items_list = self.db_images.get_all_media() + self.db_files.get_all_file()
        self._items_list = [[y for y in x] + [True] for x in self._items_list]

        # Set progress frame
        self.frm_progress.setVisible(True)
        self.prg_progress.setValue(0)
        self.prg_progress.setMaximum(len(self._items_list))
        scale = int(len(self._items_list) / 100)
        if scale < 1:
            scale = 1

        # Load the required classes
        file_util = FileDialog(self._stt)
        
        db_rec_data = db_record_data_cls.RecordData(self._stt)
        db_rec_data_list = db_rec_data.get_all_record_data()
        rec_list = []
        if db_rec_data_list:
            rec_list = set([x[3] for x in db_rec_data_list])
        
        db_def = db_definition_cls.Definition(self._stt)
        db_def_data_list = db_def.get_list_of_all_media_ids()
        def_list = []
        if db_def_data_list:
            def_list = set([x[0] for x in db_def_data_list])

        filter = self.txt_find.text().lower()

        # Populate QListWidget
        self.lst_items.clear()
        count = 0
        for idx, i in enumerate(self._items_list):
            # Check filter
            self._items_list[idx][-1] = True
            search_txt = f"{i[1]} {i[2]} {i[3]} {i[4]}".lower()
            if not self._filter_apply(filter, search_txt):
                self._items_list[idx][-1] = False
                continue

            # Get item text
            if i[5] < 100:
                txt = "IMG: "
            else:
                txt = "FILE: "

            if i[1]:
                txt += f"{i[1]}, "

            file_name = ""
            if i[5] < 100:
                if i[4].lower()[:4] == "http":
                    if i[4][:14] != "http_clipboard":
                        file_name = file_util.get_web_file_name(i[4])
                else:
                    valid_file = file_util.get_valid_local_files([i[4]])
                    if valid_file:
                        file_name = os.path.split(i[4])[1]
            else:
                valid_file = file_util.get_valid_local_files([i[3]])
                if valid_file:
                    file_name = os.path.split(i[3])[1]
                
            if file_name:
                txt += f'{file_name},       '
                
            if txt:
                txt += i[3]
            else:
                txt = i[3]
            
            # Get item tooltip
            tooltip = file_util.get_file_tooltip_text(i[3])

            # Get colors for image and file items
            img_color =QColor()
            img_color.setNamedColor(self.getv("media_explorer_image_item_list_color"))
            file_color = QColor()
            file_color.setNamedColor(self.getv("media_explorer_file_item_list_color"))

            # Set item properties
            item = QListWidgetItem()
            
            item.setText(txt)
            item.setToolTip(tooltip)
            item.setData(Qt.UserRole, i[0])
            if i[5] < 100:
                item.setBackground(img_color)
            else:
                item.setBackground(file_color)
            
            # Add item
            self.lst_items.addItem(item)

            if self.chk_not_used.isChecked():
                if i[0] in rec_list or i[0] in def_list:
                    self.lst_items.item(self.lst_items.count()-1).setHidden(True)
            if self.rbt_img.isChecked():
                if i[5] > 99:
                    self.lst_items.item(self.lst_items.count()-1).setHidden(True)
            if self.rbt_file.isChecked():
                if i[5] < 100:
                    self.lst_items.item(self.lst_items.count()-1).setHidden(True)
            if not self.lst_items.item(self.lst_items.count()-1).isHidden():
                count += 1
                self._items_list[idx][-1] = True
            else:
                self._items_list[idx][-1] = False
                self.lst_items.takeItem(self.lst_items.count() - 1)

            # Check for Abort from user
            if self._abort_operation:
                break

            # Update progress
            if idx % scale == 0:
                self.prg_progress.setValue(idx)
                QCoreApplication.processEvents()

        self.frm_progress.setVisible(False)
        self.lbl_count.setText(self.getl("media_explorer_lbl_count_text").replace("#1", str(count)).replace("#2", str(len(self._items_list))))

        if self._abort_operation:
            self.btn_refresh.setVisible(True)
            self._abort_operation = False
            self._show_msg_aborted()
        else:
            self.btn_refresh.setVisible(False)

    def _show_msg_aborted(self):
        data_dict = {
            "title": self.getl("media_explorer_msg_aborted_title"),
            "text": self.getl("media_explorer_msg_aborted_text"),
            "icon_path": self.getv("media_explorer_msg_aborted_icon_path")
        }
        self._dont_clear_menu = True
        MessageInformation(self._stt, self, data_dict=data_dict, app_modal=True)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        scale = 0.527
        w1 = int(w * scale) + 10

        self.lbl_title.resize(w, self.lbl_title.height())
        self.lst_items.resize(w1 - 10, h - 240)
        self.tree_duplicates.move(self.lst_items.pos().x(), self.lst_items.pos().y())
        self.tree_duplicates.resize(self.lst_items.width(), self.lst_items.height())
        self.lbl_type.move(w1 + 2, self.lbl_type.pos().y())
        self.lbl_type.resize(w - self.lbl_type.pos().x() - 10, self.lbl_type.height())
        self.lbl_pic.move(w1 + 2, self.lbl_pic.pos().y())
        self.lbl_pic.resize(w - self.lbl_type.pos().x() - 10, h - 400)
        self.lbl_used.move(w1 + 2, h - 290)
        self.lst_used.move(w1 + 2, h - 270)
        self.lst_used.resize(w - self.lbl_type.pos().x() - 10, self.lst_used.height())
        self.btn_delete.move(w1 + 2, h - 170)
        self.btn_delete_all.move(w1 + 120, h - 170)
        self.frm_controls.move(10, self.lst_items.pos().y() + self.lst_items.height())
        self.lbl_count.move(10, h - 40)
        self.btn_close.move(w - 120, h - 30)
         
        return super().resizeEvent(a0)

    def _load_win_position(self):
        if "media_explorer_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("media_explorer_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            if not self._dont_send_signals:
                self.get_appv("signal").send_close_all_blocks()
                self.get_appv("signal").send_close_all_definitions()

            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "media_explorer_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("media_explorer_win_geometry", {}, save_to_file=True)

        g = self.get_appv("media_explorer_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["MediaExplorer"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_type: QLabel = self.findChild(QLabel, "lbl_type")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.lbl_progress: QLabel = self.findChild(QLabel, "lbl_progress")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_used: QLabel = self.findChild(QLabel, "lbl_used")

        self.txt_find: QLineEdit = self.findChild(QLineEdit, "txt_find")

        self.lst_items: QListWidget = self.findChild(QListWidget, "lst_items")
        self.lst_used: QListWidget = self.findChild(QListWidget, "lst_used")

        self.rbt_both: QRadioButton = self.findChild(QRadioButton, "rbt_both")
        self.rbt_img: QRadioButton = self.findChild(QRadioButton, "rbt_img")
        self.rbt_file: QRadioButton = self.findChild(QRadioButton, "rbt_file")

        self.chk_not_used: QCheckBox = self.findChild(QCheckBox, "chk_not_used")

        self.frm_controls: QFrame = self.findChild(QFrame, "frm_controls")
        self.frm_progress: QFrame = self.findChild(QFrame, "frm_progress")

        self.prg_progress: QProgressBar = self.findChild(QProgressBar, "prg_progress")
        self.tree_duplicates: QTreeWidget = self.findChild(QTreeWidget, "tree_duplicates")

        self.btn_find: QPushButton = self.findChild(QPushButton, "btn_find")
        self.btn_delete: QPushButton = self.findChild(QPushButton, "btn_delete")
        self.btn_delete_all: QPushButton = self.findChild(QPushButton, "btn_delete_all")
        self.btn_delete_duplicates: QPushButton = self.findChild(QPushButton, "btn_delete_duplicates")
        self.btn_duplicates: QPushButton = self.findChild(QPushButton, "btn_duplicates")
        self.btn_progress_abort: QPushButton = self.findChild(QPushButton, "btn_progress_abort")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_refresh: QPushButton = self.findChild(QPushButton, "btn_refresh")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("media_explorer_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("media_explorer_lbl_title_tt"))

        self.lbl_type.setText("")
        self.lbl_pic.setText("")
        self.lbl_count.setText("")

        self.rbt_both.setText(self.getl("media_explorer_rbt_both_text"))
        self.rbt_both.setToolTip(self.getl("media_explorer_rbt_both_tt"))

        self.rbt_img.setText(self.getl("media_explorer_rbt_img_text"))
        self.rbt_img.setToolTip(self.getl("media_explorer_rbt_img_tt"))

        self.rbt_file.setText(self.getl("media_explorer_rbt_file_text"))
        self.rbt_file.setToolTip(self.getl("media_explorer_rbt_file_tt"))

        self.chk_not_used.setText(self.getl("media_explorer_chk_not_used_text"))
        self.chk_not_used.setToolTip(self.getl("media_explorer_chk_not_used_tt"))

        self.lbl_progress.setText(self.getl("media_explorer_lbl_progress_text"))
        self.lbl_progress.setToolTip(self.getl("media_explorer_lbl_progress_tt"))

        self.lbl_used.setText(self.getl("media_explorer_lbl_used_text"))
        self.lbl_used.setToolTip(self.getl("media_explorer_lbl_used_tt"))

        self.btn_delete.setText(self.getl("media_explorer_btn_delete_text"))
        self.btn_delete.setToolTip(self.getl("media_explorer_btn_delete_tt"))

        self.btn_delete_all.setText(self.getl("media_explorer_btn_delete_all_text"))
        self.btn_delete_all.setToolTip(self.getl("media_explorer_btn_delete_all_tt"))

        self.btn_progress_abort.setText(self.getl("media_explorer_btn_progress_abort_text"))
        self.btn_progress_abort.setToolTip(self.getl("media_explorer_btn_progress_abort_tt"))

        self.btn_duplicates.setText(self.getl("media_explorer_btn_duplicates_text"))
        self.btn_duplicates.setToolTip(self.getl("media_explorer_btn_duplicates_tt"))

        self.btn_find.setText(self.getl("media_explorer_btn_find_text"))
        self.btn_find.setToolTip(self.getl("media_explorer_btn_find_tt"))

        self.btn_close.setText(self.getl("media_explorer_btn_close_text"))
        self.btn_close.setToolTip(self.getl("media_explorer_btn_close_tt"))

        self.btn_delete_duplicates.setText(self.getl("media_explorer_btn_delete_duplicates_text"))
        self.btn_delete_duplicates.setToolTip(self.getl("media_explorer_btn_delete_duplicates_tt"))

        self.btn_refresh.setText(self.getl("media_explorer_btn_refresh_text"))
        self.btn_refresh.setToolTip(self.getl("media_explorer_btn_refresh_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["MediaExplorer"])
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self._define_media_explorer_win_apperance()

        self._define_labels_apperance(self.lbl_title, "media_explorer_lbl_title")
        self._define_labels_apperance(self.lbl_type, "media_explorer_lbl_type")
        self._define_labels_apperance(self.lbl_pic, "media_explorer_lbl_pic")
        self._define_labels_apperance(self.lbl_used, "media_explorer_lbl_used")
        self._define_labels_apperance(self.lbl_count, "media_explorer_lbl_count")
        self._define_labels_apperance(self.lbl_progress, "media_explorer_lbl_progress")

        self.txt_find.setStyleSheet(self.getv("media_explorer_txt_find_stylesheet"))
        self.lst_items.setStyleSheet(self.getv("media_explorer_lst_items_stylesheet"))
        self.lst_used.setStyleSheet(self.getv("media_explorer_lst_used_stylesheet"))
        self.prg_progress.setStyleSheet(self.getv("media_explorer_prg_progress_stylesheet"))

        self.rbt_both.setStyleSheet(self.getv("media_explorer_rbt_all_radio_stylesheet"))
        self.rbt_img.setStyleSheet(self.getv("media_explorer_rbt_all_radio_stylesheet"))
        self.rbt_file.setStyleSheet(self.getv("media_explorer_rbt_all_radio_stylesheet"))
        self.chk_not_used.setStyleSheet(self.getv("media_explorer_chk_not_used_stylesheet"))

        self.btn_find.setStyleSheet(self.getv("media_explorer_btn_find_stylesheet"))
        self.btn_delete.setStyleSheet(self.getv("media_explorer_btn_delete_stylesheet"))
        self.btn_delete_all.setStyleSheet(self.getv("media_explorer_btn_delete_all_stylesheet"))
        self.btn_duplicates.setStyleSheet(self.getv("media_explorer_btn_duplicates_stylesheet"))
        self.btn_delete_duplicates.setStyleSheet(self.getv("media_explorer_btn_delete_duplicates_stylesheet"))
        if not settings_updated:
            self.btn_delete_duplicates.setVisible(False)
        self.btn_close.setStyleSheet(self.getv("media_explorer_btn_close_stylesheet"))
        self.btn_progress_abort.setStyleSheet(self.getv("media_explorer_btn_progress_abort_stylesheet"))
        self.btn_refresh.setStyleSheet(self.getv("media_explorer_btn_refresh_stylesheet"))
        if not settings_updated:
            self.btn_refresh.setVisible(False)

        self.frm_controls.setStyleSheet(self.getv("media_explorer_frm_controls_stylesheet"))
        self.frm_progress.setStyleSheet(self.getv("media_explorer_frm_progress_stylesheet"))
        if not settings_updated:
            self.frm_progress.setVisible(False)
        
        self.tree_duplicates.setStyleSheet(self.getv("media_explorer_tree_duplicates_stylesheet"))
        if not settings_updated:
            self.tree_duplicates.setVisible(False)
            self.tree_duplicates.setHeaderHidden(True)

    def _define_media_explorer_win_apperance(self):
        self.setStyleSheet(self.getv("media_explorer_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("media_explorer_win_icon_path")))
        self.setWindowTitle(self.getl("media_explorer_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(740, 450)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))


class FindInApp(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_widget
        self._clip: Clipboard = self.get_appv("cb")
        self.db_images = db_media_cls.Media(self._stt)
        self.db_files = db_media_cls.Files(self._stt)
        self.db_rec = db_record_cls.Record(self._stt)
        self.db_def = db_definition_cls.Definition(self._stt)
        self._text_filter_obj = text_filter_cls.TextFilter()
        self._lst_result_right_button_pressed = False

        # Load GUI
        uic.loadUi(self.getv("find_in_app_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self._populate_widgets()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_close.clicked.connect(self._btn_close_click)
        self.btn_search_all.clicked.connect(self._btn_search_all_click)
        self.btn_find.clicked.connect(self._btn_find_click)
        self.txt_find.returnPressed.connect(self._btn_find_click)
        self.txt_find.textChanged.connect(self._txt_find_text_changed)
        self.txt_find.contextMenuEvent = self._txt_find_context_menu
        # self.txt_find.keyPressEvent = self._txt_find_key_press
        # self.lst_result.mouseReleaseEvent = self._lst_result_mouse_release
        self.lst_result.mousePressEvent = self._lst_result_mouse_press
        self.lst_result.mouseDoubleClickEvent = self._lst_result_mouse_double_click
        self.lst_result.itemPressed.connect(self.lst_result_start_drag)
        self.lbl_blocks.contextMenuEvent = self._lbl_blocks_mouse_release
        self.lbl_defs.contextMenuEvent = self._lbl_defs_mouse_release
        self.lbl_images.contextMenuEvent = self._lbl_images_mouse_release
        self.lbl_files.contextMenuEvent = self._lbl_files_mouse_release
        self.chk_case.stateChanged.connect(self._chk_case_state_changed)
        self.chk_words.stateChanged.connect(self._chk_words_state_changed)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["FindInApp"])

    def lst_result_start_drag(self, e):
        self.get_appv("cb").clear_drag_data()
        item = self.lst_result.currentItem()
        
        if item is not None:
            if self._lst_result_right_button_pressed:
                self._contex_menu()
                self._lst_result_right_button_pressed = False
                return
            
            data = item.data(Qt.UserRole)
            if data.startswith("B:"):
                self.get_appv("cb").set_drag_data(data, "block", self)
            elif data.startswith("D:"):
                self.get_appv("cb").set_drag_data(data, "def", self)
            elif data.startswith("I:"):
                self.get_appv("cb").set_drag_data(data, "image", self)
            elif data.startswith("F:"):
                self.get_appv("cb").set_drag_data(data, "file", self)
            
            self.lst_result.startDrag(Qt.CopyAction)

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_find, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets
        self.widget_handler.add_all_ItemBased_Widgets()

        self.widget_handler.activate()

    def _chk_case_state_changed(self, e: int):
        self._text_filter_obj.MatchCase = self.chk_case.isChecked()
        self._btn_find_click()
    
    def _chk_words_state_changed(self, e: int):
        self._text_filter_obj.SearchWholeWordsOnly = self.chk_words.isChecked()
        self._btn_find_click()

    def _lbl_blocks_mouse_release(self, e: QtGui.QMouseEvent):
        result = self._menu_select_all()
        
        if result == 10:
            self.chk_block_date.setChecked(True)
            self.chk_block_name.setChecked(True)
            self.chk_block_tags.setChecked(True)
            self.chk_block_text.setChecked(True)
            self.chk_block_def_syn.setChecked(True)
        elif result == 20:
            self.chk_block_date.setChecked(False)
            self.chk_block_name.setChecked(False)
            self.chk_block_tags.setChecked(False)
            self.chk_block_text.setChecked(False)
            self.chk_block_def_syn.setChecked(False)

    def _lbl_defs_mouse_release(self, e: QtGui.QMouseEvent):
        result = self._menu_select_all()

        if result == 10:
            self.chk_def_desc.setChecked(True)
            self.chk_def_name.setChecked(True)
            self.chk_def_syn.setChecked(True)
        elif result == 20:
            self.chk_def_desc.setChecked(False)
            self.chk_def_name.setChecked(False)
            self.chk_def_syn.setChecked(False)

    def _lbl_images_mouse_release(self, e: QtGui.QMouseEvent):
        result = self._menu_select_all()

        if result == 10:
            self.chk_img_desc.setChecked(True)
            self.chk_img_file.setChecked(True)
            self.chk_img_name.setChecked(True)
            self.chk_img_src.setChecked(True)
        elif result == 20:
            self.chk_img_desc.setChecked(False)
            self.chk_img_file.setChecked(False)
            self.chk_img_name.setChecked(False)
            self.chk_img_src.setChecked(False)

    def _lbl_files_mouse_release(self, e: QtGui.QMouseEvent):
        result = self._menu_select_all()

        if result == 10:
            self.chk_file_desc.setChecked(True)
            self.chk_file_file.setChecked(True)
            self.chk_file_name.setChecked(True)
            self.chk_file_src.setChecked(True)
        elif result == 20:
            self.chk_file_desc.setChecked(False)
            self.chk_file_file.setChecked(False)
            self.chk_file_name.setChecked(False)
            self.chk_file_src.setChecked(False)

    def _menu_select_all(self):
        menu_dict = {
            "position": QCursor.pos(),
            "items": [
                [
                    10,
                    self.getl("check_all_text"),
                    "",
                    True,
                    [],
                    self.getv("check_all_icon_path")
                ],
                [
                    20,
                    self.getl("check_none_text"),
                    "",
                    True,
                    [],
                    self.getv("check_none_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        ContextMenu(self._stt, self)
        return self.get_appv("menu")["result"]

    def _lst_result_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            e.ignore()
            self._contex_menu()
            return None
        QListWidget.mouseReleaseEvent(self.lst_result, e)

    def _lst_result_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self._lst_result_right_button_pressed = True
        else:
            self._lst_result_right_button_pressed = False
        QListWidget.mousePressEvent(self.lst_result, e)

    def _lst_result_mouse_double_click(self, e: QtGui.QMouseEvent):
        if self.lst_result.currentItem() is not None:
            item_type = self.lst_result.currentItem().data(Qt.UserRole)[:1]
            item_id = int(self.lst_result.currentItem().data(Qt.UserRole)[2:])

            if item_type == "B":
                data_dict = {
                    "name": "find_in_app",
                    "action": "open_block",
                    "id": item_id
                }
                self._parent_widget.events(data_dict)
            elif item_type == "D":
                data_dict = {
                    "name": "find_in_app",
                    "action": "open_definition",
                    "id": item_id
                }
                self._parent_widget.events(data_dict)
            elif item_type == "I":
                data_dict = {
                    "name": "find_in_app",
                    "action": "image_info",
                    "id": item_id
                }
                self._parent_widget.events(data_dict)
            elif item_type == "F":
                data_dict = {
                    "name": "find_in_app",
                    "action": "file_info",
                    "id": item_id
                }
                self._parent_widget.events(data_dict)

        QListWidget.mouseDoubleClickEvent(self.lst_result, e)

    def _txt_find_context_menu(self, e):
        disab = []
        if not self.txt_find.isUndoAvailable():
            disab.append(10)
        if not self.txt_find.isRedoAvailable():
            disab.append(20)
        selected_text = ""
        if self.txt_find.selectedText():
            selected_text = self.txt_find.selectedText()
        else:
            disab.append(30)
            disab.append(60)
        if self.txt_find.text():
            if not selected_text:
                selected_text = self.txt_find.text()
        else:
            disab.append(40)
        if not self.get_appv("clipboard").text():
            paste_text = ""
            disab.append(50)
        else:
            paste_text = self.get_appv("clipboard").text()
        
        if len(selected_text) > 40:
            selected_text = selected_text[:37] + "..."
        if len(paste_text) > 40:
            paste_text = paste_text[:37] + "..."

        menu_dict = {
            "separator": [20, 60],
            "disabled": disab,
            "items": [
                [
                    10,
                    self.getl("block_txt_box_menu_undo_text"),
                    self.getl("block_txt_box_menu_undo_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_undo_icon_path")
                ],
                [
                    20,
                    self.getl("block_txt_box_menu_redo_text"),
                    self.getl("block_txt_box_menu_redo_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_redo_icon_path")
                ],
                [
                    30,
                    self.getl("block_txt_box_menu_cut_text"),
                    self.getl("block_txt_box_menu_cut_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_cut_icon_path")
                ],
                [
                    40,
                    f'{self.getl("block_txt_box_menu_copy_text")} ({selected_text})',
                    self.getl("block_txt_box_menu_copy_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_copy_icon_path")
                ],
                [
                    50,
                    f'{self.getl("block_txt_box_menu_paste_text")} ({paste_text})',
                    self.getl("block_txt_box_menu_paste_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_paste_icon_path")
                ],
                [
                    60,
                    self.getl("block_txt_box_menu_delete_text"),
                    self.getl("block_txt_box_menu_delete_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_delete_icon_path")
                ]
            ]
        }

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter_obj)

        menu_dict = filter_menu.create_menu_dict(show_item_search_history=False, existing_menu_dict=menu_dict)

        self._dont_clear_menu = True

        result = filter_menu.show_menu(self, menu_dict=menu_dict)

        self.chk_case.setChecked(self._text_filter_obj.MatchCase)
        self.chk_words.setChecked(self._text_filter_obj.SearchWholeWordsOnly)

        if result in range(filter_menu.item_range_filter_setup[0], filter_menu.item_range_filter_setup[1]):
            self._btn_find_click()
        elif result == 10:
            self.txt_find.undo()
        elif result == 20:
            self.txt_find.redo()
        elif result == 30:
            self.txt_find.cut()
        elif result == 40:
            if self.txt_find.selectedText():
                self.txt_find.copy()
            else:
                self.get_appv("clipboard").setText(self.txt_find.text())
        elif result == 50:
            self.txt_find.paste()
        elif result == 60:
            if self.txt_find.selectedText():
                self.txt_find.setText(f"{self.txt_find.text()[:self.txt_find.selectionStart()]}{self.txt_find.text()[self.txt_find.selectionEnd():]}")

    def _contex_menu(self):
        if self.lst_result.currentItem() is None:
            return
        
        item_type = self.lst_result.currentItem().data(Qt.UserRole)[:1]
        item_id = int(self.lst_result.currentItem().data(Qt.UserRole)[2:])

        if item_type == "B":
            self._context_block(item_id)
        elif item_type == "D":
            self._context_definition(item_id)
        elif item_type == "I":
            self._context_image(item_id)
        elif item_type == "F":
            self._context_file(item_id)

    def _context_block(self, rec_id: int):
        disab = []
        all_block_ids = self.id_list_of_all_blocks()
        if all_block_ids:
            if len(all_block_ids) < 2:
                disab.append(20)
                disab.append(130)
                disab.append(140)
                disab.append(14010)
        
        full_item_id = f"B:{rec_id}"

        no_items_in_clip = self.get_appv("cb").block_clip_number_of_items()
        no_items_in_list = len(all_block_ids)
        no_items_found = len(self.get_appv("cb").block_clip_ids_that_are_in_clipboard(all_block_ids))
        if self.get_appv("cb").block_clip_ids_that_are_in_clipboard(rec_id):
            disab.append(11020)
        else:
            disab.append(11030)
        
        if no_items_found == no_items_in_list:
            disab.append(11050)
        
        if no_items_found == 0:
            disab.append(11060)
        
        if no_items_in_clip == 0:
            disab.append(11070)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [10, 30, 130, 11030, 11060],
            "items": [
                [
                    10,
                    self.getl("find_in_app_menu_open_block_text"),
                    self.getl("find_in_app_menu_open_block_tt"),
                    True,
                    [],
                    self.getv("mnu_view_blocks_icon_path")
                ],
                [
                    20,
                    self.getl("find_in_app_menu_open_all_blocks_text"),
                    self.getl("find_in_app_menu_open_all_blocks_tt"),
                    True,
                    [],
                    self.getv("mnu_view_blocks_icon_path")
                ],
                [
                    30,
                    self.getl("find_in_app_menu_open_all_diary_text"),
                    self.getl("find_in_app_menu_open_all_diary_tt"),
                    True,
                    [],
                    self.getv("mnu_diary_icon_path")
                ],
                [
                    110,
                    self.getl("block_context_copy_text"),
                    self.getl("block_context_copy_desc"),
                    True,
                    [
                        [
                            11010,
                            self.getl("block_context_copy_text") + f' ({self.getl("block_context_items_in_clip_text").replace("#1", str(no_items_in_clip))})',
                            self.getl("block_context_copy_desc"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            11020,
                            self.getl("block_context_copy_add_text") + f' ({self.getl("block_context_items_in_clip_text").replace("#1", str(no_items_in_clip))})',
                            self.getl("block_context_copy_add_desc"),
                            True,
                            [],
                            self.getv("copy_add_icon_path")
                        ],
                        [
                            11030,
                            self.getl("block_context_clear_text"),
                            self.getl("block_context_clear_desc"),
                            True,
                            [],
                            self.getv("clear_x_icon_path")
                        ],
                        [
                            11040,
                            self.getl("block_context_copy_all_text") + f' ({self.getl("block_context_items_in_list_text").replace("#1", str(no_items_in_list))})',
                            self.getl("block_context_copy_all_desc"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            11050,
                            self.getl("block_context_copy_add_all_text") + f' ({self.getl("block_context_items_in_list_text").replace("#1", str(no_items_in_list))})',
                            self.getl("block_context_copy_add_all_desc"),
                            True,
                            [],
                            self.getv("copy_add_icon_path")
                        ],
                        [
                            11060,
                            self.getl("block_context_clear_all_text") + f' ({self.getl("block_context_items_found_text").replace("#1", str(no_items_found)).replace("#2", str(no_items_in_list))})',
                            self.getl("block_context_clear_all_desc"),
                            True,
                            [],
                            self.getv("clear_x_icon_path")
                        ],
                        [
                            11070,
                            self.getl("block_context_clear_clip_text") + f' ({self.getl("block_context_items_in_clip_text").replace("#1", str(no_items_in_clip))})',
                            self.getl("block_context_clear_clip_desc"),
                            True,
                            [],
                            self.getv("clear_icon_path")
                        ],
                    ],
                    self.getv("copy_icon_path")
                ],
                [
                    120,
                    self.getl("block_context_send_to_text"),
                    "",
                    False,
                    [
                        [
                            12010,
                            self.getl("block_context_send_to_export_blocks_text"),
                            self.getl("block_context_send_to_export_blocks_desc"),
                            True,
                            [],
                            self.getv("export_icon_path")
                        ]
                    ],
                    self.getv("send_to_icon_path")
                ],
                [
                    130,
                    self.getl("block_context_send_to_all_text"),
                    "",
                    False,
                    [
                        [
                            13010,
                            self.getl("block_context_send_to_export_blocks_text"),
                            self.getl("block_context_send_to_export_blocks_desc"),
                            True,
                            [],
                            self.getv("export_icon_path")
                        ]
                    ],
                    self.getv("send_to_icon_path")
                ]
            ]
        }
        self._dont_clear_menu = True

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter_obj)
        
        menu_dict = filter_menu.create_menu_dict(existing_menu_dict=menu_dict,
                                                 show_match_case=False,
                                                 show_whole_words=False,
                                                 show_ignore_serbian_characters=False,
                                                 show_translate_cyrillic_to_latin=False)

        result = filter_menu.show_menu(self, menu_dict=menu_dict, full_item_ID=full_item_id)

        if result == 10:
            data_dict = {
                "name": "find_in_app",
                "action": "open_block",
                "id": rec_id
            }
            self._parent_widget.events(data_dict)
        elif result == 20:
            data_dict = {
                "name": "find_in_app",
                "action": "open_all_blocks",
                "id": None,
                "ids": all_block_ids
            }
            self._parent_widget.events(data_dict)
        elif result == 30:
            data_dict = {
                "name": "find_in_app",
                "action": "open_all_diary",
                "id": None,
                "ids": all_block_ids
            }
            self._parent_widget.events(data_dict)
        elif result == 110 or result == 11010:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "copy",
                "id": rec_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11020:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "copy_add",
                "id": rec_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11030:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "remove",
                "id": rec_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11040:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "copy",
                "id": all_block_ids
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11050:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "copy_add",
                "id": all_block_ids
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11060:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "remove",
                "id": all_block_ids
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11070:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "remove",
                "id": None
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 12010:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "send_to_export",
                "id": rec_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 13010:
            main_win_events_dict = {
                "name": "block_clipboard",
                "action": "send_to_export",
                "id": all_block_ids
            }
            self.get_appv("main_win").events(main_win_events_dict)

    def id_list_of_all_blocks(self) -> list:
        result = []
        for index in range(self.lst_result.count()):
            item = self.lst_result.item(index)
            if item.data(Qt.UserRole) and item.data(Qt.UserRole)[0].upper() == "B":
                result.append(int(item.data(Qt.UserRole)[2:]))
        
        return result

    def id_list_of_all_definitions(self) -> list:
        result = []
        for index in range(self.lst_result.count()):
            item = self.lst_result.item(index)
            if item.data(Qt.UserRole) and item.data(Qt.UserRole)[0].upper() == "D":
                result.append(int(item.data(Qt.UserRole)[2:]))
        
        return result

    def _context_definition(self, def_id: int):
        disab = []
        full_item_id = f"D:{def_id}"

        all_defs = self.id_list_of_all_definitions()
        if len(all_defs) < 2:
            disab.append(130)
            disab.append(140)
            disab.append(14010)

        no_items_in_clip = self.get_appv("cb").def_clip_number_of_items()
        no_items_in_list = len(all_defs)
        no_items_found = len(self.get_appv("cb").def_clip_ids_that_are_in_clipboard(all_defs))
        if self.get_appv("cb").def_clip_ids_that_are_in_clipboard(def_id):
            disab.append(11020)
        else:
            disab.append(11030)
        
        if no_items_found == no_items_in_list:
            disab.append(11050)
        
        if no_items_found == 0:
            disab.append(11060)
        
        if no_items_in_clip == 0:
            disab.append(11070)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [10, 130, 11030, 11060],
            "items": [
                [
                    10,
                    self.getl("find_in_app_menu_open_definition_text"),
                    self.getl("find_in_app_menu_open_definition_tt"),
                    True,
                    [],
                    self.getv("mnu_view_definitions_icon_path")
                ],
                [
                    110,
                    self.getl("definition_context_copy_text"),
                    self.getl("definition_context_copy_desc"),
                    True,
                    [
                        [
                            11010,
                            self.getl("definition_context_copy_text") + f' ({self.getl("block_context_items_in_clip_text").replace("#1", str(no_items_in_clip))})',
                            self.getl("definition_context_copy_desc"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            11020,
                            self.getl("definition_context_copy_add_text") + f' ({self.getl("block_context_items_in_clip_text").replace("#1", str(no_items_in_clip))})',
                            self.getl("definition_context_copy_add_desc"),
                            True,
                            [],
                            self.getv("copy_add_icon_path")
                        ],
                        [
                            11030,
                            self.getl("definition_context_clear_text"),
                            self.getl("definition_context_clear_desc"),
                            True,
                            [],
                            self.getv("clear_x_icon_path")
                        ],
                        [
                            11040,
                            self.getl("definition_context_copy_all_text") + f' ({self.getl("block_context_items_in_list_text").replace("#1", str(no_items_in_list))})',
                            self.getl("definition_context_copy_all_desc"),
                            True,
                            [],
                            self.getv("copy_icon_path")
                        ],
                        [
                            11050,
                            self.getl("definition_context_copy_add_all_text") + f' ({self.getl("block_context_items_in_list_text").replace("#1", str(no_items_in_list))})',
                            self.getl("definition_context_copy_add_all_desc"),
                            True,
                            [],
                            self.getv("copy_add_icon_path")
                        ],
                        [
                            11060,
                            self.getl("definition_context_clear_all_text") + f' ({self.getl("block_context_items_found_text").replace("#1", str(no_items_found)).replace("#2", str(no_items_in_list))})',
                            self.getl("definition_context_clear_all_desc"),
                            True,
                            [],
                            self.getv("clear_x_icon_path")
                        ],
                        [
                            11070,
                            self.getl("definition_context_clear_clip_text") + f' ({self.getl("block_context_items_in_clip_text").replace("#1", str(no_items_in_clip))})',
                            self.getl("definition_context_clear_clip_desc"),
                            True,
                            [],
                            self.getv("clear_icon_path")
                        ],
                    ],
                    self.getv("copy_icon_path")
                ],
                [
                    120,
                    self.getl("definition_context_send_to_text"),
                    "",
                    False,
                    [
                        [
                            12010,
                            self.getl("definition_context_send_to_export_definitions_text"),
                            self.getl("definition_context_send_to_export_definitions_desc"),
                            True,
                            [],
                            self.getv("export_icon_path")
                        ]
                    ],
                    self.getv("send_to_icon_path")
                ],
                [
                    130,
                    self.getl("definition_context_send_to_all_text"),
                    "",
                    False,
                    [
                        [
                            13010,
                            self.getl("definition_context_send_to_export_definitions_text"),
                            self.getl("definition_context_send_to_export_definitions_desc"),
                            True,
                            [],
                            self.getv("export_icon_path")
                        ]
                    ],
                    self.getv("send_to_icon_path")
                ]
            ]
        }
        self._dont_clear_menu = True

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter_obj)
        
        menu_dict = filter_menu.create_menu_dict(existing_menu_dict=menu_dict,
                                                 show_match_case=False,
                                                 show_whole_words=False,
                                                 show_ignore_serbian_characters=False,
                                                 show_translate_cyrillic_to_latin=False)

        result = filter_menu.show_menu(self, menu_dict=menu_dict, full_item_ID=full_item_id)

        if result == 10:
            data_dict = {
                "name": "find_in_app",
                "action": "open_definition",
                "id": def_id
            }
            self._parent_widget.events(data_dict)
        elif result == 110 or result == 11010:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "copy",
                "id": def_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11020:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "copy_add",
                "id": def_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11030:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "remove",
                "id": def_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11040:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "copy",
                "id": all_defs
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11050:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "copy_add",
                "id": all_defs
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11060:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "remove",
                "id": all_defs
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 11070:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "remove",
                "id": None
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 12010:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "send_to_export",
                "id": def_id
            }
            self.get_appv("main_win").events(main_win_events_dict)
        elif result == 13010:
            main_win_events_dict = {
                "name": "definition_clipboard",
                "action": "send_to_export",
                "id": all_defs
            }
            self.get_appv("main_win").events(main_win_events_dict)

    def _context_image(self, image_id: int):
        disab = []
        if self._clip.is_clip_empty():
            disab.append(50)

        full_item_id = f"I:{image_id}"

        menu_dict = {
            "position": QCursor.pos(),
            "separator": [20, 50],
            "disabled": disab,
            "items": [
                [
                    10,
                    self.getl("find_in_app_menu_image_info_text"),
                    self.getl("find_in_app_menu_image_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    20,
                    self.getl("find_in_app_menu_open_image_text"),
                    self.getl("find_in_app_menu_open_image_tt"),
                    True,
                    [],
                    self.getv("picture_view_win_icon_path")
                ],
                [
                    30,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    40,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    50,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self._dont_clear_menu = True

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter_obj)
        
        menu_dict = filter_menu.create_menu_dict(existing_menu_dict=menu_dict,
                                                 show_match_case=False,
                                                 show_whole_words=False,
                                                 show_ignore_serbian_characters=False,
                                                 show_translate_cyrillic_to_latin=False)

        result = filter_menu.show_menu(self, menu_dict=menu_dict, full_item_ID=full_item_id)

        if result == 10:
            data_dict = {
                "name": "find_in_app",
                "action": "image_info",
                "id": image_id
            }
            self._parent_widget.events(data_dict)
        elif result == 20:
            data_dict = {
                "name": "find_in_app",
                "action": "open_image",
                "id": image_id
            }
            self._parent_widget.events(data_dict)
        elif result == 30:
            self._clip.copy_to_clip(image_id)
        elif result == 40:
            self._clip.copy_to_clip(image_id, add_to_clip=True)
        elif result == 50:
            self._clip.clear_clip()

    def _context_file(self, file_id: int):
        disab = []
        if self._clip.is_clip_empty():
            disab.append(50)

        full_item_id = f"F:{file_id}"

        menu_dict = {
            "position": QCursor.pos(),
            "separator": [20, 50],
            "disabled": disab,
            "items": [
                [
                    10,
                    self.getl("find_in_app_menu_file_info_text"),
                    self.getl("find_in_app_menu_file_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    20,
                    self.getl("find_in_app_menu_open_file_text"),
                    self.getl("find_in_app_menu_open_file_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    30,
                    self.getl("file_menu_copy_text"),
                    self.getl("file_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    40,
                    self.getl("file_menu_add_to_clip_text"),
                    self.getl("file_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    50,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self._dont_clear_menu = True

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter_obj)
        
        menu_dict = filter_menu.create_menu_dict(existing_menu_dict=menu_dict,
                                                 show_match_case=False,
                                                 show_whole_words=False,
                                                 show_ignore_serbian_characters=False,
                                                 show_translate_cyrillic_to_latin=False)

        result = filter_menu.show_menu(self, menu_dict=menu_dict, full_item_ID=full_item_id)

        if result == 10:
            data_dict = {
                "name": "find_in_app",
                "action": "file_info",
                "id": file_id
            }
            self._parent_widget.events(data_dict)
        elif result == 20:
            try:
                self.db_files.load_file(file_id)
                os.startfile(os.path.abspath(self.db_files.file_file))
            except Exception as e:
                self.txt_find.setText(str(e))
        elif result == 30:
            self._clip.copy_to_clip(file_id)
        elif result == 40:
            self._clip.copy_to_clip(file_id, add_to_clip=True)
        elif result == 50:
            self._clip.clear_clip()

    def _txt_find_text_changed(self):
        if self._text_filter_obj.is_filter_in_document(self.txt_find.text(), "", ignore_cashe=True) is None and self.txt_find.text():
            self.txt_find.setStyleSheet(self.getv("find_in_app_txt_find_illegal_entry_stylesheet"))
            return
        else:
            self.txt_find.setStyleSheet(self.getv("find_in_app_txt_find_stylesheet"))

        if self.chk_auto_search.isChecked() and self.txt_find.text():
            self._btn_find_click()

    def _btn_find_click(self):
        self.lst_result.clear()
        if not self.txt_find.text():
            self._update_counter()
            return
        
        self._text_filter_obj.SearchWholeWordsOnly = self.chk_words.isChecked()
        self._text_filter_obj.MatchCase = self.chk_case.isChecked()

        self._text_filter_obj.clear_search_history()

        title = self.lbl_title.text()
        self.lbl_title.setText(self.getl("searching_text"))
        self.frm_searching.setVisible(True)
        QCoreApplication.processEvents()
        
        self._search_blocks()
        self._search_definitions()
        self._search_images()
        self._search_files()

        self.lbl_title.setText(title)
        self.frm_searching.setVisible(False)
        self._update_counter()
        UTILS.LogHandler.add_log_record("#1: Search performed. (#2)", ["FindInApp", self.txt_find.text()])

    def _update_counter(self):
        self.lbl_count.setText(self.getl("find_in_app_lbl_counter_text").replace("#1", str(self.lst_result.count())))

    def _search_blocks(self):
        records = self.db_rec.get_all_records()
        expr = self.db_def.get_list_of_all_expressions()
        defs = self.db_def.get_list_of_all_definitions_and_descriptions()
        
        find = self.txt_find.text()
        if not self.chk_case.isChecked():
            find = find.lower()

        # Make definition synonyms dict
        def_dict = {}
        start = 0
        self._text_filter_obj.SearchWholeWordsOnly = True
        for definition in defs:
            expr_list = []
            for expression in range(start, len(expr)):
                if definition[0] == expr[expression][1]:
                    expr_list.append(expr[expression][0])
                else:
                    start = expression
                    break
            txt = " ".join(expr_list)
            if not self.chk_case.isChecked():
                txt = txt.lower()
            special_find = " " + find
            special_find = special_find.replace("/", " ")
            special_find = special_find.replace(" !", " ")
            if self._text_filter_obj.is_any_filter_word_in_document(filter_text=special_find, document_text=txt):
                def_dict[definition[1]] = list(expr_list)

        self._text_filter_obj.SearchWholeWordsOnly = self.chk_words.isChecked()

        if self.chk_block_tags.isChecked():
            tags_db = db_tag_cls.Tag(self._stt)
            tags_list = tags_db.get_all_tags_translated()
            record_data_db = db_record_data_cls.RecordData(self._stt)
            record_data_list = [x for x in record_data_db.get_all_record_data() if x[2]]

        for record in records:
            txt = ""
            if self.chk_block_date.isChecked():
                txt += record[2] + "\n"
            if self.chk_block_name.isChecked():
                txt += record[1] + "\n"
            if self.chk_block_tags.isChecked():
                txt += self._get_tags_for_text(record[0], tags_list, record_data_list) + "\n"
            if self.chk_block_text.isChecked():
                txt += record[4]
            
            # Check if need to search synonyms
            if not self.chk_case.isChecked():
                txt = txt.lower()
                
            if self.chk_block_def_syn.isChecked():
                txt += " "
                txt += self._get_synonyms_for_text(txt, def_dict)
            
            txt = txt.strip()
            if not self.chk_case.isChecked():
                txt = txt.lower()

            if not self._text_filter_obj.is_filter_in_document(filter_text=find, document_text=txt):
                continue
            
            txt = f'{self.getl("block_text").upper()}: {record[2]} '
            if record[1]:
                txt += f"{record[1]} - "
            if record[4]:
                txt += record[4].split("\n")[0]
            
            item = QListWidgetItem()
            item.setText(txt)
            item.setToolTip(record[4])
            color = QColor()
            color.setNamedColor(self.getv("find_in_app_block_item_list_color"))
            item.setBackground(color)
            item.setData(Qt.UserRole, f"B:{record[0]}")
            self._text_filter_obj.save_search_history(f"B:{record[0]}")

            self.lst_result.addItem(item)

    def _get_tags_for_text(self, record_id: int, tags_list: list, record_data_list: list) -> str:
        result = ""
        in_record = False
        for data in record_data_list:
            if data[1] == record_id:
                in_record = True
                for tag in tags_list:
                    if data[2] == tag[0]:
                        result += f"{tag[1]} "
                        break
                else:
                    UTILS.TerminalUtility.WarningMessage("Tag for record #1 not found !\nTAG: #2", [data[1], data[2]])
            else:
                if in_record:
                    break
        
        return result

    def _get_synonyms_for_text(self, txt: str, def_dict: dict) -> str:
        result = "\n"
        txt = f" {txt} ".lower()
        END_OF_SENTENCE = {".", "!", "?", "\n", "\t", ",", ":", "(", ")"}

        for i in END_OF_SENTENCE:
            txt = txt.replace(i, " ")
        
        count = 0
        for i in def_dict:
            expressions = def_dict[i]
            for expression in expressions:
                for j in END_OF_SENTENCE:
                    expression = expression.replace(j, " ")
                expres = f" {expression} "
                if expres in txt:
                    count += 1
                    result += f"\n{count}.) DEFINITION: {i}   ({len(def_dict[i])})\n    Context: {expression}\n\n"
                    result += " ".join(def_dict[i])
                    result += "\n"
                    break
        
        return result

    def _search_definitions(self):
        defs = self.db_def.get_list_of_all_definitions_and_descriptions()
        records = []
        txt = ""
        expr = self.db_def.get_list_of_all_expressions()
        start = 0
        for i in defs:
            txt = ""
            for j in range(start, len(expr)):
                if expr[j][1] == i[0]:
                    txt += expr[j][0] + " "
                else:
                    records.append([i[0], i[1], i[2], txt])
                    start = j
                    break
            else:
                records.append([i[0], i[1], i[2], txt])
        
        find = self.txt_find.text()
        if not self.chk_case.isChecked():
            find = find.lower()

        for record in records:
            txt = ""
            if self.chk_def_name.isChecked():
                txt += record[1] + " "
            if self.chk_def_desc.isChecked():
                txt += record[2] + " "
            if self.chk_def_syn.isChecked():
                txt += record[3]
            
            txt = txt.strip()
            if not self.chk_case.isChecked():
                txt = txt.lower()

            if not self._text_filter_obj.is_filter_in_document(filter_text=find, document_text=txt):
                continue
            
            txt = f'{self.getl("definition_text").upper()}: {record[1]}'
            
            item = QListWidgetItem()
            item.setText(txt)
            if len(record[2]) > 1000:
                txt = record[2][:999] + "..."
            else:
                txt = record[2]
            item.setToolTip(txt)
            color = QColor()
            color.setNamedColor(self.getv("find_in_app_definition_item_list_color"))
            item.setBackground(color)
            item.setData(Qt.UserRole, f"D:{record[0]}")
            self._text_filter_obj.save_search_history(f"D:{record[0]}")

            self.lst_result.addItem(item)

    def _search_images(self):
        file_util = FileDialog(self._stt)
        records = self.db_images.get_all_media()
        find = self.txt_find.text()
        if not self.chk_case.isChecked():
            find = find.lower()

        for record in records:
            txt = ""
            if self.chk_img_name.isChecked():
                txt += record[1] + " "
            if self.chk_img_desc.isChecked():
                txt += record[2] + " "
            if self.chk_img_file.isChecked():
                txt += record[3] + " "
            if self.chk_img_src.isChecked():
                txt += record[4]
            
            txt = txt.strip()
            if not self.chk_case.isChecked():
                txt = txt.lower()

            if not self._text_filter_obj.is_filter_in_document(filter_text=find, document_text=txt):
                continue
            
            txt = f'{self.getl("image_text").upper()}: ({record[0]}) '
            if record[1]:
                txt += record[1]
            else:
                src_file_name = file_util.get_web_file_name(record[4])
                if src_file_name:
                    txt += src_file_name
                else:
                    txt += os.path.split(record[3])[1]
            
            item = QListWidgetItem()
            item.setText(txt)
            txt = f'<img src="{os.path.abspath(record[3])}" width = 150>'
            item.setToolTip(txt)

            color = QColor()
            color.setNamedColor(self.getv("find_in_app_image_item_list_color"))
            item.setBackground(color)
            item.setData(Qt.UserRole, f"I:{record[0]}")
            self._text_filter_obj.save_search_history(f"I:{record[0]}")

            self.lst_result.addItem(item)

    def _search_files(self):
        file_util = FileDialog(self._stt)
        records = self.db_files.get_all_file()
        find = self.txt_find.text()
        if not self.chk_case.isChecked():
            find = find.lower()

        for record in records:
            txt = ""
            if self.chk_file_name.isChecked():
                txt += record[1] + " "
            if self.chk_file_desc.isChecked():
                txt += record[2] + " "
            if self.chk_file_file.isChecked():
                txt += record[3] + " "
            if self.chk_file_src.isChecked():
                txt += record[4]
            
            txt = txt.strip()
            if not self.chk_case.isChecked():
                txt = txt.lower()

            if not self._text_filter_obj.is_filter_in_document(filter_text=find, document_text=txt):
                continue
            
            txt = f'{self.getl("file_text").upper()}: ({record[0]}) '
            if record[1]:
                txt += record[1]
            else:
                src_file_name = file_util.get_web_file_name(record[4])
                if src_file_name:
                    txt += src_file_name
                else:
                    txt += os.path.split(record[3])[1]
            
            item = QListWidgetItem()
            item.setText(txt)
            txt = file_util.get_file_tooltip_text(record[3])
            item.setToolTip(txt)

            color = QColor()
            color.setNamedColor(self.getv("find_in_app_file_item_list_color"))
            item.setBackground(color)
            item.setData(Qt.UserRole, f"F:{record[0]}")
            self._text_filter_obj.save_search_history(f"F:{record[0]}")

            self.lst_result.addItem(item)

    def _prepare_for_whole_words(self, txt: str) -> str:
        repl = """.!?"'|;:></[]{}=-_=)(*&^%$#@~`\t\n\\"""
        for i in repl:
            txt = txt.replace(i, " ")
        txt = " " + txt + " "
        return txt

    def _btn_search_all_click(self):
        self.chk_block_date.setChecked(True)
        self.chk_block_name.setChecked(True)
        self.chk_block_tags.setChecked(True)
        self.chk_block_text.setChecked(True)
        self.chk_block_def_syn.setChecked(True)
        self.chk_def_name.setChecked(True)
        self.chk_def_syn.setChecked(True)
        self.chk_def_desc.setChecked(True)
        self.chk_img_name.setChecked(True)
        self.chk_img_desc.setChecked(True)
        self.chk_img_file.setChecked(True)
        self.chk_img_src.setChecked(True)
        self.chk_file_name.setChecked(True)
        self.chk_file_desc.setChecked(True)
        self.chk_file_file.setChecked(True)
        self.chk_file_src.setChecked(True)

    def _btn_close_click(self):
        self.close()

    def _populate_widgets(self):
        self.lbl_blocks.setText(f'{self.lbl_blocks.text()} ({len(self.db_rec.get_all_records())})')
        self.lbl_defs.setText(f'{self.lbl_defs.text()} ({len(self.db_def.get_list_of_all_definitions())})')
        self.lbl_images.setText(f'{self.lbl_images.text()} ({len(self.db_images.get_all_media())})')
        self.lbl_files.setText(f'{self.lbl_files.text()} ({len(self.db_files.get_all_file())})')

        self._text_filter_obj.MatchCase = self.chk_case.isChecked()
        self._text_filter_obj.SearchWholeWordsOnly = self.chk_words.isChecked()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w, self.lbl_title.height())
        self.txt_find.resize(w - 130, self.txt_find.height())
        self.btn_find.move(w - 110, self.btn_find.pos().y())
        self.grp_search.resize(w - 20, self.grp_search.height())
        self.lst_result.resize(w - 20, h - 390)
        self.lbl_count.move(10, h - 40)
        self.btn_close.move(w - 120, h - 30)

        self.frm_searching.move(10, 113)
        self.frm_searching.resize(w - 20, self.frm_searching.height())
        self.lbl_searching.resize(self.frm_searching.width(), self.frm_searching.height())
         
        return super().resizeEvent(a0)

    def _load_win_position(self):
        if "find_in_app_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("find_in_app_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self.chk_case.setChecked(g["chk_case"])
            self.chk_auto_search.setChecked(g["chk_auto_search"])
            self.chk_block_date.setChecked(g["chk_block_date"])
            self.chk_block_name.setChecked(g["chk_block_name"])
            self.chk_block_tags.setChecked(g.get("chk_block_tags", False))
            self.chk_block_text.setChecked(g["chk_block_text"])
            if "chk_block_def_syn" in g:
                self.chk_block_def_syn.setChecked(g["chk_block_def_syn"])
            else:
                self.chk_block_def_syn.setChecked(True)
            if "chk_words" in g:
                self.chk_words.setChecked(g["chk_words"])
            else:
                self.chk_words.setChecked(False)
            self.chk_def_name.setChecked(g["chk_def_name"])
            self.chk_def_syn.setChecked(g["chk_def_syn"])
            self.chk_def_desc.setChecked(g["chk_def_desc"])
            self.chk_img_name.setChecked(g["chk_img_name"])
            self.chk_img_desc.setChecked(g["chk_img_desc"])
            self.chk_img_file.setChecked(g["chk_img_file"])
            self.chk_img_src.setChecked(g["chk_img_src"])
            self.chk_file_name.setChecked(g["chk_file_name"])
            self.chk_file_desc.setChecked(g["chk_file_desc"])
            self.chk_file_file.setChecked(g["chk_file_file"])
            self.chk_file_src.setChecked(g["chk_file_src"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "find_in_app_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("find_in_app_win_geometry", {}, save_to_file=True)

        g = self.get_appv("find_in_app_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["chk_case"] = self.chk_case.isChecked()
        g["chk_words"] = self.chk_words.isChecked()
        g["chk_auto_search"] = self.chk_auto_search.isChecked()
        g["chk_block_date"] = self.chk_block_date.isChecked()
        g["chk_block_name"] = self.chk_block_name.isChecked()
        g["chk_block_tags"] = self.chk_block_tags.isChecked()
        g["chk_block_text"] = self.chk_block_text.isChecked()
        g["chk_block_def_syn"] = self.chk_block_def_syn.isChecked()
        g["chk_def_name"] = self.chk_def_name.isChecked()
        g["chk_def_syn"] = self.chk_def_syn.isChecked()
        g["chk_def_desc"] = self.chk_def_desc.isChecked()
        g["chk_img_name"] = self.chk_img_name.isChecked()
        g["chk_img_desc"] = self.chk_img_desc.isChecked()
        g["chk_img_file"] = self.chk_img_file.isChecked()
        g["chk_img_src"] = self.chk_img_src.isChecked()
        g["chk_file_name"] = self.chk_file_name.isChecked()
        g["chk_file_desc"] = self.chk_file_desc.isChecked()
        g["chk_file_file"] = self.chk_file_file.isChecked()
        g["chk_file_src"] = self.chk_file_src.isChecked()

        self.get_appv("cb").clear_drag_data()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["FindInApp"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_blocks: QLabel = self.findChild(QLabel, "lbl_blocks")
        self.lbl_defs: QLabel = self.findChild(QLabel, "lbl_defs")
        self.lbl_images: QLabel = self.findChild(QLabel, "lbl_images")
        self.lbl_files: QLabel = self.findChild(QLabel, "lbl_files")
        self.lbl_result: QLabel = self.findChild(QLabel, "lbl_result")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")

        self.txt_find: QLineEdit = self.findChild(QLineEdit, "txt_find")
        self.grp_search: QGroupBox = self.findChild(QGroupBox, "grp_search")
        self.lst_result: QListWidget = self.findChild(QListWidget, "lst_result")

        self.chk_block_date: QCheckBox = self.findChild(QCheckBox, "chk_block_date")
        self.chk_block_name: QCheckBox = self.findChild(QCheckBox, "chk_block_name")
        self.chk_block_tags: QCheckBox = self.findChild(QCheckBox, "chk_block_tags")
        self.chk_block_text: QCheckBox = self.findChild(QCheckBox, "chk_block_text")
        self.chk_block_def_syn: QCheckBox = self.findChild(QCheckBox, "chk_block_def_syn")
        self.chk_def_name: QCheckBox = self.findChild(QCheckBox, "chk_def_name")
        self.chk_def_syn: QCheckBox = self.findChild(QCheckBox, "chk_def_syn")
        self.chk_def_desc: QCheckBox = self.findChild(QCheckBox, "chk_def_desc")
        self.chk_img_name: QCheckBox = self.findChild(QCheckBox, "chk_img_name")
        self.chk_img_desc: QCheckBox = self.findChild(QCheckBox, "chk_img_desc")
        self.chk_img_file: QCheckBox = self.findChild(QCheckBox, "chk_img_file")
        self.chk_img_src: QCheckBox = self.findChild(QCheckBox, "chk_img_src")
        self.chk_file_name: QCheckBox = self.findChild(QCheckBox, "chk_file_name")
        self.chk_file_desc: QCheckBox = self.findChild(QCheckBox, "chk_file_desc")
        self.chk_file_file: QCheckBox = self.findChild(QCheckBox, "chk_file_file")
        self.chk_file_src: QCheckBox = self.findChild(QCheckBox, "chk_file_src")

        self.chk_case: QCheckBox = self.findChild(QCheckBox, "chk_case")
        self.chk_words: QCheckBox = self.findChild(QCheckBox, "chk_words")
        self.chk_auto_search: QCheckBox = self.findChild(QCheckBox, "chk_auto_search")

        self.btn_find: QPushButton = self.findChild(QPushButton, "btn_find")
        self.btn_search_all: QPushButton = self.findChild(QPushButton, "btn_search_all")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")

        self.frm_searching: QFrame = self.findChild(QFrame, "frm_searching")
        self.lbl_searching: QLabel = self.findChild(QLabel, "lbl_searching")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("find_in_app_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("find_in_app_lbl_title_tt"))

        self.lbl_result.setText(self.getl("find_in_app_lbl_result_text"))
        self.lbl_result.setToolTip(self.getl("find_in_app_lbl_result_tt"))

        self.lbl_blocks.setText(self.getl("find_in_app_lbl_blocks_text"))
        self.lbl_blocks.setToolTip(self.getl("find_in_app_lbl_blocks_tt"))

        self.lbl_defs.setText(self.getl("find_in_app_lbl_defs_text"))
        self.lbl_defs.setToolTip(self.getl("find_in_app_lbl_defs_tt"))

        self.lbl_images.setText(self.getl("find_in_app_lbl_images_text"))
        self.lbl_images.setToolTip(self.getl("find_in_app_lbl_images_tt"))

        self.lbl_files.setText(self.getl("find_in_app_lbl_files_text"))
        self.lbl_files.setToolTip(self.getl("find_in_app_lbl_files_tt"))

        self.lbl_count.setText("")

        self.chk_case.setText(self.getl("find_in_app_chk_case_text"))
        self.chk_case.setToolTip(self.getl("find_in_app_chk_case_tt"))

        self.chk_words.setText(self.getl("find_in_app_chk_words_text"))
        self.chk_words.setToolTip(self.getl("find_in_app_chk_words_tt"))

        self.chk_auto_search.setText(self.getl("find_in_app_chk_auto_search_text"))
        self.chk_auto_search.setToolTip(self.getl("find_in_app_chk_auto_search_tt"))

        self.chk_block_date.setText(self.getl("find_in_app_chk_block_date_text"))
        self.chk_block_date.setToolTip(self.getl("find_in_app_chk_block_date_tt"))

        self.chk_block_name.setText(self.getl("find_in_app_chk_block_name_text"))
        self.chk_block_name.setToolTip(self.getl("find_in_app_chk_block_name_tt"))

        self.chk_block_tags.setText(self.getl("find_in_app_chk_block_tags_text"))
        self.chk_block_tags.setToolTip(self.getl("find_in_app_chk_block_tags_tt"))

        self.chk_block_text.setText(self.getl("find_in_app_chk_block_text_text"))
        self.chk_block_text.setToolTip(self.getl("find_in_app_chk_block_text_tt"))

        self.chk_block_def_syn.setText(self.getl("find_in_app_chk_block_def_syn_text"))
        self.chk_block_def_syn.setToolTip(self.getl("find_in_app_chk_block_def_syn_tt"))

        self.chk_def_name.setText(self.getl("find_in_app_chk_def_name_text"))
        self.chk_def_name.setToolTip(self.getl("find_in_app_chk_def_name_tt"))

        self.chk_def_syn.setText(self.getl("find_in_app_chk_def_syn_text"))
        self.chk_def_syn.setToolTip(self.getl("find_in_app_chk_def_syn_tt"))

        self.chk_def_desc.setText(self.getl("find_in_app_chk_def_desc_text"))
        self.chk_def_desc.setToolTip(self.getl("find_in_app_chk_def_desc_tt"))

        self.chk_img_name.setText(self.getl("find_in_app_chk_img_name_text"))
        self.chk_img_name.setToolTip(self.getl("find_in_app_chk_img_name_tt"))

        self.chk_img_desc.setText(self.getl("find_in_app_chk_img_desc_text"))
        self.chk_img_desc.setToolTip(self.getl("find_in_app_chk_img_desc_tt"))

        self.chk_img_file.setText(self.getl("find_in_app_chk_img_file_text"))
        self.chk_img_file.setToolTip(self.getl("find_in_app_chk_img_file_tt"))

        self.chk_img_src.setText(self.getl("find_in_app_chk_img_src_text"))
        self.chk_img_src.setToolTip(self.getl("find_in_app_chk_img_src_tt"))

        self.chk_file_name.setText(self.getl("find_in_app_chk_file_name_text"))
        self.chk_file_name.setToolTip(self.getl("find_in_app_chk_file_name_tt"))

        self.chk_file_desc.setText(self.getl("find_in_app_chk_file_desc_text"))
        self.chk_file_desc.setToolTip(self.getl("find_in_app_chk_file_desc_tt"))

        self.chk_file_file.setText(self.getl("find_in_app_chk_file_file_text"))
        self.chk_file_file.setToolTip(self.getl("find_in_app_chk_file_file_tt"))

        self.chk_file_src.setText(self.getl("find_in_app_chk_file_src_text"))
        self.chk_file_src.setToolTip(self.getl("find_in_app_chk_file_src_tt"))

        self.grp_search.setTitle(self.getl("find_in_app_grp_search_text"))

        self.btn_find.setText(self.getl("find_in_app_btn_find_text"))
        self.btn_find.setToolTip(self.getl("find_in_app_btn_find_tt"))

        self.btn_search_all.setText(self.getl("find_in_app_btn_search_all_text"))
        self.btn_search_all.setToolTip(self.getl("find_in_app_btn_search_all_tt"))

        self.btn_close.setText(self.getl("find_in_app_btn_close_text"))
        self.btn_close.setToolTip(self.getl("find_in_app_btn_close_tt"))

        self.lbl_searching.setText(self.getl("find_in_app_lbl_searching_text"))
        self.lbl_searching.setToolTip(self.getl("find_in_app_lbl_searching_tt"))

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["FindInApp"])
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_find_in_app_win_apperance()

        self._define_labels_apperance(self.lbl_title, "find_in_app_lbl_title")
        self._define_labels_apperance(self.lbl_result, "find_in_app_lbl_result")
        self._define_labels_apperance(self.lbl_count, "find_in_app_lbl_count")
        self._define_labels_apperance(self.lbl_blocks, "find_in_app_lbl_blocks")
        self._define_labels_apperance(self.lbl_defs, "find_in_app_lbl_defs")
        self._define_labels_apperance(self.lbl_images, "find_in_app_lbl_images")
        self._define_labels_apperance(self.lbl_files, "find_in_app_lbl_files")

        self.txt_find.setStyleSheet(self.getv("find_in_app_txt_find_stylesheet"))
        self.grp_search.setStyleSheet(self.getv("find_in_app_grp_search_stylesheet"))
        self.lst_result.setStyleSheet(self.getv("find_in_app_lst_result_stylesheet"))
        self.lst_result.setDragEnabled(True)
        self.lst_result.setContextMenuPolicy(Qt.CustomContextMenu)

        self.chk_case.setStyleSheet(self.getv("find_in_app_chk_case_stylesheet"))
        self.chk_words.setStyleSheet(self.getv("find_in_app_chk_words_stylesheet"))
        self.chk_auto_search.setStyleSheet(self.getv("find_in_app_chk_auto_search_stylesheet"))
        self.chk_block_date.setStyleSheet(self.getv("find_in_app_chk_block_date_stylesheet"))
        self.chk_block_name.setStyleSheet(self.getv("find_in_app_chk_block_name_stylesheet"))
        self.chk_block_tags.setStyleSheet(self.getv("find_in_app_chk_block_tags_stylesheet"))
        self.chk_block_text.setStyleSheet(self.getv("find_in_app_chk_block_text_stylesheet"))
        self.chk_block_def_syn.setStyleSheet(self.getv("find_in_app_chk_block_def_syn_stylesheet"))
        self.chk_def_name.setStyleSheet(self.getv("find_in_app_chk_def_name_stylesheet"))
        self.chk_def_syn.setStyleSheet(self.getv("find_in_app_chk_def_syn_stylesheet"))
        self.chk_def_desc.setStyleSheet(self.getv("find_in_app_chk_def_desc_stylesheet"))
        self.chk_img_name.setStyleSheet(self.getv("find_in_app_chk_img_name_stylesheet"))
        self.chk_img_desc.setStyleSheet(self.getv("find_in_app_chk_img_desc_stylesheet"))
        self.chk_img_file.setStyleSheet(self.getv("find_in_app_chk_img_file_stylesheet"))
        self.chk_img_src.setStyleSheet(self.getv("find_in_app_chk_img_src_stylesheet"))
        self.chk_file_name.setStyleSheet(self.getv("find_in_app_chk_file_name_stylesheet"))
        self.chk_file_desc.setStyleSheet(self.getv("find_in_app_chk_file_desc_stylesheet"))
        self.chk_file_file.setStyleSheet(self.getv("find_in_app_chk_file_file_stylesheet"))
        self.chk_file_src.setStyleSheet(self.getv("find_in_app_chk_file_src_stylesheet"))

        self._define_buttons_apperance(self.btn_find, "find_in_app_btn_find")
        self._define_buttons_apperance(self.btn_search_all, "find_in_app_btn_search_all")
        self._define_buttons_apperance(self.btn_close, "find_in_app_btn_close")

        self.frm_searching.setStyleSheet(self.getv("find_in_app_frm_searching_stylesheet"))
        self.frm_searching.setVisible(False)
        self._define_labels_apperance(self.lbl_searching, "find_in_app_lbl_searching")

    def _define_find_in_app_win_apperance(self):
        self.setStyleSheet(self.getv("find_in_app_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("find_in_app_win_icon_path")))
        self.setWindowTitle(self.getl("find_in_app_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(660, 430)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        btn.setShortcut(self.getv(f"{name}_shortcut"))
        if self.getv(f"{name}_icon_path"):
            btn.setIcon(QIcon(self.getv(f"{name}_icon_path")))
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))
        # Icon Size
        icon_size = int(btn.contentsRect().height() * self.getv(f"{name}_icon_height") / 100)
        btn.setIconSize(QSize(icon_size, icon_size))


class TextToHtmlRule():
    """
    TextToHtmlRule class to define styling rules for converting text to HTML.

    Parameters:

        text (str): The text to match this rule to.

        replace_with (str): Optional text to replace matched text with.

        bg_color (str): Background color.

        fg_color (str): Foreground/text color.

        font_family (str): Font family.

        font_size (int): Font size in px.

        font_bold (bool): Whether to bold text.

        font_italic (bool): Whether to italicize text. 

        font_underline (bool): Whether to underline text.

        letter_spacing (int): Letter spacing in px.

        line_height (float): Line height.

        text_align (str): Text alignment - left, right, center, justify.

        vertical_align (str): Vertical alignment - top, middle, bottom.

        white_space_wrap (bool): Whether to wrap text.

        text_opacity (float): Text opacity from 0 to 1.
        
    Methods:

        set_text_shadow(): Sets text shadow property.

        set_default_simple_shadow(): Applies default subtle shadow.

        set_default_offset_shadow(): Applies default offset shadow.

        set_default_blurred_shadow(): Applies default blurred shadow.

        get_text(): Gets rule match text, with new line as <br>.

        set_text(): Sets rule match text.

        get_css_style_content(): Gets full CSS style string for rule.

        has_css_style(): Checks if rule has any styling set.

    """

    def __init__(
            self,
            text: str = "",
            replace_with: str = None,
            bg_color: str = None,
            fg_color: str = None,
            font_family: str = None,
            font_size: int = None,
            font_bold: bool = None,
            font_italic: bool = None,
            font_underline: bool = None,
            letter_spacing: int = None,
            line_height: float = None,
            text_align: str = None,
            vertical_align: str = None,
            white_space_wrap: bool = None,
            text_opacity: float = None,
            link_href: str = None
            ) -> None:
        
        self.text = text
        self.replace_with = replace_with
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_family = font_family
        self.font_size = font_size
        self.font_bold = font_bold
        self.font_italic = font_italic
        self.font_underline = font_underline
        self.letter_spacing = letter_spacing
        self.line_height = line_height
        self.text_align = text_align
        self.vertical_align = vertical_align
        self.white_space_wrap = white_space_wrap
        self.text_opacity = text_opacity
        self.link_href = link_href
        
        self.text_shadow = None

        self.rule_name = f"{time.time_ns()} + {random.randint(0, 1000000)}"

    def set_text_shadow(
            self,
            offset_x: int = 0,
            offset_y: int = 0,
            blur_radius: int = 0,
            color: str = "black"
            ):
        """
        Sets the text shadow CSS property.

        Parameters:

            offset_x (int): Horizontal shadow offset in pixels. Default 0.  

            offset_y (int): Vertical shadow offset in pixels. Default 0.

            blur_radius (int): Blur radius for the shadow. Default 0.

            color (str): Color of the shadow as a CSS value. Default 'black'.

        Sets the text_shadow property to a string value with the provided parameters.

        This will set a text shadow effect on the text when applied in CSS.

        For example:

        set_text_shadow(offset_x=2, offset_y=2, color='grey')

        Would set a 2px horizontal and vertical grey shadow.

        """
        
        shadow = f'{offset_x}px {offset_y}px {blur_radius}px {color}'
        self.text_shadow = shadow

    def set_default_simple_shadow(self):
        self.set_text_shadow(offset_x=2,
                             offset_y=2,
                             color="#000000"
                             )
        
    def set_default_offset_shadow(self):
        self.set_text_shadow(offset_x=5,
                             offset_y=5,
                             blur_radius=2,
                             color="#ff0000"
                             )

    def set_default_blurred_shadow(self):
        self.set_text_shadow(offset_x=0,
                             offset_y=0,
                             blur_radius=5,
                             color="rgba(0,0,0,0.5)"
                             )

    def get_text(self) -> str:
        """
        Gets the text that will be matched for this rule.

        If replace_with is set, returns that text with newlines converted to <br>.
        Otherwise returns the original text value with newlines converted.

        The _fix_string() method handles converting newlines to <br> tags.

        Returns:
            str: The text to match for this rule, with newlines as <br>.
        """

        if self.replace_with is not None:
            return self._fix_string(self.replace_with)
        else:
            return self._fix_string(self.text)

    def set_text(self, text: str):
        self.text = text
        
    def _fix_string(self, text: str) -> str:
        if text:
            text = text.replace("\n", "<br>")
        return text

    def get_css_style_content(self, general_rule = None) -> str:
        """
        Generates a CSS style string for the rule based on set properties.

        Iterates through all style properties set on the rule and generates 
        a CSS style string concatenating property:value pairs.

        Removes any trailing whitespace and returns the style string.

        Returns an empty string if no properties are set.

        Returns:
            str: CSS style string for the rule.
        """

        style = ""

        if self.bg_color is not None:
            style += f" background-color: {self.bg_color}; "
        else:
            if general_rule:
                if general_rule.bg_color:
                    style += f" background-color: {general_rule.bg_color}; "

        if self.fg_color is not None:
            style += f" color: {self.fg_color}; "
        else:
            if general_rule:
                if general_rule.fg_color:
                    style += f" color: {general_rule.fg_color}; "

        if self.font_family is not None:
            style += f" font-family: {self.font_family}; "
        else:
            if general_rule:
                if general_rule.font_family:
                    style += f" font-family: {general_rule.font_family}; "

        if self.font_size is not None:
            style += f" font-size: {self.font_size}px; "
        else:
            if general_rule:
                if general_rule.font_size:
                    style += f" font-size: {general_rule.font_size}px; "

        if self.font_bold is not None:
            if self.font_bold:
                style += " font-weight: bold; "
        else:
            if general_rule:
                if general_rule.font_bold:
                    style += f" font-weight: bold; "

        if self.font_italic is not None:
            if self.font_italic:
                style += " font-style: italic; "
        else:
            if general_rule:
                if general_rule.font_italic:
                    style += " font-style: italic; "

        if self.font_underline is not None:
            if self.font_underline:
                style += " font-decoration: underline; "
        else:
            if general_rule:
                if general_rule.font_underline:
                    style += " font-decoration: underline; "

        if self.letter_spacing is not None:
            style += f" letter-spacing: {self.letter_spacing}px; "
        else:
            if general_rule:
                if general_rule.letter_spacing:
                    style += f" letter-spacing: {general_rule.letter_spacing}px; "

        if self.line_height is not None:
            style += f" line-height: {self.line_height}; "
        else:
            if general_rule:
                if general_rule.line_height:
                    style += f" line-height: {general_rule.line_height}; "

        if self.text_align is not None:
            style += f" text-align: {self.text_align}; "
        else:
            if general_rule:
                if general_rule.text_align:
                    style += f" text-align: {general_rule.text_align}; "

        if self.vertical_align is not None:
            style += f" vertical-align: {self.vertical_align}; "
        else:
            if general_rule:
                if general_rule.vertical_align:
                    style += f" vertical-align: {general_rule.vertical_align}; "

        if self.white_space_wrap is not None:
            if self.white_space_wrap:
                style += " white-space: wrap; "
            else:
                style += " white-space: nowrap; "
        else:
            if general_rule:
                if general_rule.white_space_wrap:
                    if general_rule.white_space_wrap:
                        style += " white-space: wrap; "
                    else:
                        style += " white-space: nowrap; "

        if self.text_opacity is not None:
            style += f" opacity: {self.text_opacity}; "
        else:
            if general_rule:
                if general_rule.text_opacity:
                    style += f" opacity: {general_rule.text_opacity}; "

        if self.text_shadow is not None:
            style += f" text-shadow: {self.text_shadow}; "
        else:
            if general_rule:
                if general_rule.text_shadow:
                    style += f" text-shadow: {general_rule.text_shadow}; "

        if style:
            style = style.rstrip(" ")
        
        return style

    def has_css_style(self) -> bool:
        if self.get_css_style_content():
            return True
        else:
            return False


class TextToHTML():
    """
    TextToHTML class to convert text to HTML with styling rules.

    Parameters:
        text (str): The text to convert to HTML.

    Attributes:
        text (str): The original text.
        rules (list): List of TextToHtmlRule objects. 
        general_rule (TextToHtmlRule): Default rule applied.

    Methods:

        reset_general_rule(): Reset general rule to default.

        set_text(): Set the text to convert.

        get_text(): Get the original text.

        add_rule(): Add a TextToHtmlRule to rules.

        delete_rule(): Delete a rule, or clear all rules.

        get_html(): Generate and return HTML string.

    Converts text to HTML by applying a general rule and additional
    specific rules. Rules match text snippets and define styling.
    """

    def __init__(self, text: str = "") -> None:

        self.text = self._fix_string(text)

        self.rules: list = []
        self.general_rule = TextToHtmlRule()

    def reset_general_rule(self):
        """
        Resets the general_rule attribute to a new TextToHtmlRule instance.

        This will reset any custom styling set on the existing general rule.
        The general rule is applied to any text not matched by other specific rules.
        """

        self.general_rule = TextToHtmlRule()

    def set_text(self, text: str):
        """
        Sets the text attribute to the provided text string.

        Parameters:
            text (str): The text to convert to HTML.

        Calls _fix_string() on the text to convert newlines to <br> tags.
        Sets the text attribute to the converted string.
        """

        self.text = self._fix_string(text)
    
    def get_text(self) -> str:
        """
        Gets the original text that was passed to the TextToHTML class.

        Returns:
            str: The original text string.
        """

        return self.text

    def add_rule(self, rule: TextToHtmlRule) -> None:
        """
        Adds a TextToHtmlRule object to the rules list.

        Parameters:
            rule (TextToHtmlRule): The rule object to add.

        Appends the rule to the end of the rules list.
        """
        if isinstance(rule, TextToHtmlRule):
            self.rules.append(rule)
        else:
            for i in rule:
                self.rules.append(i)

    def delete_rule(self, rule: TextToHtmlRule = None) -> bool:
        """
        Deletes a rule from the rules list.

        Parameters:
            rule (TextToHtmlRule): The rule object to delete.

        If rule is None, clears all rules in the list.

        Otherwise, loops through the rules list and removes 
        the rule with matching rule_name.

        Returns:
            bool: True if rule was deleted, False otherwise.
        """

        if isinstance(rule, TextToHtmlRule):
            return self._delete_rule(rule)
        elif rule is None:
            return self._delete_rule()
        else:
            success = True
            for item in rule:
                if not self._delete_rule(item):
                    success = False
        return success

    def _delete_rule(self, rule: TextToHtmlRule = None) -> bool:
        if rule is None:
            self.rules = []
            return True
        
        for idx, item in enumerate(self.rules):
            if item.rule_name == rule.rule_name:
                self.rules.pop(idx)
                return True
        return False

    def get_html(self) -> str:
        """
        Generates and returns the HTML string by applying rules.

        Checks that text is not empty, then gets a list of text slices 
        and matched rules using _get_slices(). 

        If there are slices, calls _create_html() to generate the HTML by 
        applying the rules on each text slice.

        Returns:
            str: The generated HTML string.
        """

        if not self.text:
            return ""

        slices = self._get_slices(self.text)
        html = None
        if slices:
            html = self._create_html(self.text, slices)
        
        return html

    def _fix_string(self, text: str) -> str:
        if text:
            text = text.replace("\n", "<br>")
        return text

    def _create_html(self, text: str, slices: list) -> str:
        result = ""
        for i in slices:
            style = i[2].get_css_style_content(self.general_rule)
            if style:
                style = f' style="{style}"'

            text_for_html = i[2].get_text().replace("\n", "<br>")
            txt = f'<span{style}>{text_for_html}</span>'
            if i[2].link_href:
                txt = f'<a href="{i[2].link_href}">{txt}</a>'
            result += txt
        
        return result

    def _get_slices(self, text: str) -> list:
        if not text:
            return []

        rule_positions = []

        for rule in self.rules:
            if rule.text:
                pos = self._get_rule_pos(text, rule)
                for i in pos:
                    rule_positions.append([i[0], i[1], rule])
        
        rule_positions.sort(key=lambda x: x[0])

        result = []
        pos = 0
        for item in rule_positions:
            if item[0] < pos:
                continue
            rule = self._get_general_rule(text, pos, item[0])
            if rule:
                result.append([pos, item[0], rule])
            result.append([item[0], item[1], item[2]])
            pos = item[1]

        if result:
            pos = result[-1][1]
        rule = self._get_general_rule(text, pos, None)
        if rule:
            result.append([pos, len(text), rule])

        return result

    def _get_general_rule(self, text: str, start_pos: int = None, end_pos: int = None) -> TextToHtmlRule:
        if start_pos is None:
            start_pos = 0
        if end_pos is None:
            end_pos = len(text)
        if end_pos - start_pos == 0:
            return None
        
        rule = copy.deepcopy(self.general_rule)
        rule.set_text(text[start_pos:end_pos])

        return rule

    def _get_rule_pos(self, text: str, rule: TextToHtmlRule) -> list:
        positions = []
        pos = 0
        while True:
            pos = text.find(rule.text, pos)
            if pos >= 0:
                start = pos
                end = start + len(rule.text)
                positions.append((start, end))
                pos += 1
            else:
                break
        
        return positions
    

class DefHintManager(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, win_position: QPoint = None):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_widget = parent_widget
        
        if "definition_hint_data" in self._stt.app_setting_get_list_of_keys():
            self.rejected_words = self.get_appv("definition_hint_data")["rejected"]
        else:
            self._stt.app_setting_add("definition_hint_data", {"rejected": []}, save_to_file=True)
            self.rejected_words = []

        self.definition_expressions = self._get_def_expressions()
        self.lfcr_tracker = 0
        self.ignore_text_changes = False

        # Load GUI
        uic.loadUi(self.getv("def_hint_manager_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._populate_widgets()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.cmb_sort.currentIndexChanged.connect(self.sort_changed)
        self.btn_cancel.clicked.connect(self.btn_cancel_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.txt_expressions.textChanged.connect(self.txt_expressions_changed)

        if win_position:
            self.move(win_position)
        else:
            self.move(QCursor.pos())

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["DefHintManager"])

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_expressions, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets
        self.widget_handler.add_all_ItemBased_Widgets()

        self.widget_handler.activate()

    def txt_expressions_changed(self):
        if self.ignore_text_changes:
            return
        
        lfcr_tracker = self.txt_expressions.toPlainText().count("\n")
        if lfcr_tracker != self.lfcr_tracker:
            self.lfcr_tracker = lfcr_tracker
            result = self.colorize_textbox()
            self.update_count_label(result)

    def update_count_label(self, struct_data: tuple = None):
        if struct_data:
            count_all, count_definition, count_repeated, count_too_small = struct_data
        else:
            count_all, count_definition, count_repeated, count_too_small = (None, None, None, None)
            count_all = len([x for x in self.txt_expressions.toPlainText().splitlines() if x.strip()])

        self.lbl_count.setText(self.getl("def_hint_count_label").replace("#1", str(count_all)))
        
        if count_definition is not None:
            tt = self.getl("def_hint_count_label_tt").replace("#1", str(count_all)).replace("#2", str(count_definition)).replace("#3", str(count_repeated)).replace("#4", str(count_too_small))
        else:
            tt = ""
        
        self.lbl_count.setToolTip(tt)

    def colorize_textbox(self):
        self.ignore_text_changes = True
        # Get cursor position
        cursor = self.txt_expressions.textCursor()
        cursor_position = cursor.position()

        text = self.txt_expressions.toPlainText()
        
        body = ""
        text_lines = text.splitlines()
        min_len = self.getv("definition_hint_minimum_word_lenght")
        count_all = 0
        count_definition = 0
        count_repeated = 0
        count_too_small = 0
        for item in text_lines:
            if item.strip() and len(item.strip()) < min_len:
                body += f"<span class='too_small'>{item}</span><br>"
                count_too_small += 1
            elif item.strip() in self.definition_expressions:
                body += f"<span class='definition'>{item}</span><br>"
                count_definition += 1
            elif item.strip() and text_lines.count(item.strip()) > 1:
                body += f"<span class='repeated'>{item}</span><br>"
                count_repeated += 1
            else:
                body += f"{item}<br>"
            
            if item.strip():
                count_all += 1
            
        
        html = f"""
<html>
<head>
<style>
.repeated {{ color: #adadad; }}
.too_small {{ color: #ffaa00; }}
.definition {{ color: #ff0000; }}
</style>
<body>
{body}
</body>
</html>
"""
        self.txt_expressions.setHtml(html)
        # Set cursor position
        cursor.setPosition(cursor_position)
        self.txt_expressions.setTextCursor(cursor)
        self.ignore_text_changes = False

        return (count_all, count_definition, count_repeated, count_too_small)

    def _get_def_expressions(self) -> list:
        db_def = db_definition_cls.Definition(self._stt)
        result = [x[0] for x in db_def.get_list_of_all_expressions() if x[0].strip()]
        
        return result

    def btn_cancel_clicked(self):
        self.close()

    def btn_save_clicked(self):
        result = self.sort_txtbox(1)
        self.get_appv("definition_hint_data")["rejected"] = result
        UTILS.LogHandler.add_log_record("#1: Data saved.", ["DefHintManager"])

        self.close()

    def sort_changed(self):
        if not self.cmb_sort.currentData():
            return
        
        expressions = self.sort_txtbox(self.cmb_sort.currentData())
        
        self.txt_expressions.setPlainText("\n".join(expressions))

    def sort_txtbox(self, sort_type: int) -> list:
        expressions = []
        min_len = self.getv("definition_hint_minimum_word_lenght")
        for item in self.txt_expressions.toPlainText().split("\n"):
            item = item.strip()
            if not item or item in self.definition_expressions or len(item) < min_len:
                continue
            if item not in expressions:
                expressions.append(item)

        if sort_type == 2:
            expressions.sort()
            return expressions
        if sort_type == 3:
            expressions.sort(key=lambda x: len(x), reverse=True)
            return expressions

        map_expressions_in_settings = []
        other_expressions = []
        for item in expressions:
            # Find index for item in rejected_words
            index = None
            if item in self.rejected_words:
                index = self.rejected_words.index(item)
            
            if index is not None:
                map_expressions_in_settings.append([index, item])
            else:
                other_expressions.append(item)
        
        map_expressions_in_settings.sort(key=lambda x: x[0])

        result = [x[1] for x in map_expressions_in_settings]
        result.extend(other_expressions)

        return result

    def _populate_widgets(self):
        # Populate TextBox
        self.txt_expressions.setPlainText("\n".join(self.rejected_words))
        self.colorize_textbox()
        self.update_count_label()
        self.lfcr_tracker = len(self.rejected_words)

        # Populate ComboBox
        self.cmb_sort.clear()

        self.cmb_sort.addItem(self.getl("def_hint_manager_cmb_sort_add_time"), 1)
        self.cmb_sort.addItem(self.getl("def_hint_manager_cmb_sort_alpha"), 2)
        self.cmb_sort.addItem(self.getl("def_hint_manager_cmb_sort_len"), 3)

        self.cmb_sort.setCurrentIndex(0)

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["DefHintManager"])
        self._setup_widgets_apperance()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["DefHintManager"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.cmb_sort: QComboBox = self.findChild(QComboBox, "cmb_sort")
        self.txt_expressions: QTextEdit = self.findChild(QTextEdit, "txt_expressions")
        self.btn_save: QPushButton = self.findChild(QPushButton, "btn_save")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.gridLayout: QGridLayout = self.findChild(QGridLayout, "gridLayout")
        self.setLayout(self.gridLayout)

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("def_hint_manager_lbl_title_text"))
        self.btn_save.setText(self.getl("btn_save"))
        self.btn_cancel.setText(self.getl("btn_cancel"))

    def _setup_widgets_apperance(self):
        self._define_def_hint_manager_win_apperance()

        self.lbl_title.setStyleSheet(self.getv("def_hint_manager_lbl_title_stylesheet"))
        self.cmb_sort.setStyleSheet(self.getv("def_hint_manager_cmb_sort_stylesheet"))
        self.txt_expressions.setStyleSheet(self.getv("def_hint_manager_txt_expressions_stylesheet"))
        self.btn_save.setStyleSheet(self.getv("def_hint_manager_btn_save_stylesheet"))
        self.btn_cancel.setStyleSheet(self.getv("def_hint_manager_btn_cancel_stylesheet"))
        self.lbl_count.setStyleSheet(self.getv("def_hint_manager_lbl_count_stylesheet"))

        self._set_margins(self.gridLayout, "def_hint_manager_layout")

    def _define_def_hint_manager_win_apperance(self):
        self.setStyleSheet(self.getv("def_hint_manager_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("def_hint_manager_win_icon_path")))
        self.setWindowTitle(self.getl("def_hint_manager_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])
