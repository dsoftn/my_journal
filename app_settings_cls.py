from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout, QWidget, QSpacerItem,
                             QSizePolicy, QListWidget, QFileDialog, QDialog, QLabel, QListWidgetItem,  QLineEdit,
                             QMessageBox, QComboBox,  QProgressBar, QCheckBox, QKeySequenceEdit, QRadioButton,
                             QGroupBox, QGraphicsOpacityEffect, QSpinBox, QColorDialog, QFontDialog)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor, QColor, QMouseEvent, QMovie, QDrag, QDropEvent
from PyQt5.QtCore import Qt, QCoreApplication, QMimeData
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
import qwidgets_util_cls
from stylesheet_cls import StyleSheet
import UTILS
    

class AbstractFrame(QFrame):
    COLOR_GREEN = "#00ff00"
    COLOR_LIGHT_GREEN = "#aaff7f"
    COLOR_DARK_GREEN = "#004400"
    COLOR_WHITE = "#ffffff"
    COLOR_BLUE = "#00ffff"
    COLOR_LIGHT_BLUE = "#aaffff"
    COLOR_DARK_BLUE = "#00005b"
    COLOR_YELLOW = "#ffff00"
    COLOR_LIGHT_YELLOW = "#ffff7f"
    COLOR_RED = "#ff0000"
    COLOR_LIGHT_RED = "#ff7f7f"
    COLOR_DARK_RED = "#aa0000"
    COLOR_GREY = "#e6e6e6"
    COLOR_BLACK = "#000000"

    LINE_EDIT_STYLESHEET_DEFAULT = "QLineEdit {color: #ffff00; background-color: #006a00;} QLineEdit:hover {background-color: #009300;}"
    LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY = "QLineEdit {color: #ffff00; background-color: #aa0000;} QLineEdit:hover {background-color: #c30000;}"
    LINE_EDIT_STYLESHEET_AWAITING = "QLineEdit {color: #00007f; background-color: #ffff00;} QLineEdit:hover {background-color: #ffff7f;}"

    X_PADDING = 10
    Y_PADDING = 10
    X_SPACING = 10
    Y_SPACING = 5

    def __init__(self, parent_widget, settings: settings_cls.Settings) -> None:
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.cancel_animation = True

    def _define_frame(self, frame: QFrame, stylesheet: str = "QFrame {background-color: #666666;} QFrame:hover {background-color: #5b6166; border: 1px solid #00aaff;}", has_border: bool = False):
        # Main frame
        frame.setFrameShadow(QFrame.Plain)
        if has_border:
            frame.setFrameShape(QFrame.Box)
        else:
            frame.setFrameShape(QFrame.NoFrame)

        frame.setStyleSheet(stylesheet)

    def _create_line_edit(self,
                        parent_widget: QWidget,
                        stylesheet: str = LINE_EDIT_STYLESHEET_DEFAULT, 
                        center: bool = True,
                        font_size: int = 12
                        ) -> QLineEdit:
        
        lineedit = QLineEdit(parent_widget)
        lineedit.setStyleSheet(stylesheet)
        if center:
            lineedit.setAlignment(Qt.AlignCenter)
        lineedit.resize(60, 23)
        font = lineedit.font()
        font.setPointSize(font_size)
        lineedit.setFont(font)

        return lineedit

    def _create_combobox(self,
                        parent_widget: QWidget,
                        stylesheet: str = "QComboBox {color: rgb(255, 255, 0); background-color: rgb(0, 70, 0);} QComboBox:hover {background-color: rgb(0, 104, 0);}",
                        font_size: int = 12,
                        width: int = 140,
                        data: list = [],
                        ) -> QComboBox:
        
        cmb = QComboBox(parent_widget)
        cmb.setStyleSheet(stylesheet)
        font = cmb.font()
        font.setPointSize(font_size)
        cmb.setFont(font)
        cmb.adjustSize()
        cmb.resize(width, cmb.height())
        for item in data:
            if isinstance(item, (tuple, list)):
                cmb.addItem(item[0], item[1])
                if len(item) > 2 and item[2]:
                    cmb.setItemIcon(cmb.count() - 1, QIcon(QPixmap(item[2])))
            else:
                cmb.addItem(item)
        cmb.wheelEvent = lambda event: None

        return cmb

    def _create_label(self,
                        parent_widget: QWidget,
                        text: str = "",
                        width: int = None,
                        center: bool = True,
                        font_size: int = 12,
                        font_bold: bool = False,
                        fg_color: str = COLOR_GREEN,
                        hover_color: str = COLOR_LIGHT_GREEN,
                        bg_color = "transparent",
                        no_mouse_interaction: bool = False,
                        no_border_radius: bool = False
                        ) -> QLabel:

        label = QLabel(parent_widget)
        label.setText(text)
        if no_border_radius:
            stylesheet = f"QLabel {{color: {fg_color}; border: 0px; background-color: {bg_color}; border-radius: 0px;}} QLabel:hover {{color: {hover_color};}}"
        else:
            stylesheet = f"QLabel {{color: {fg_color}; border: 0px; background-color: {bg_color};}} QLabel:hover {{color: {hover_color};}}"
        label.setStyleSheet(stylesheet)
        if center:
            label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        font = label.font()
        font.setPointSize(font_size)
        font.setBold(font_bold)
        label.setFont(font)
        if no_mouse_interaction:
            label.setCursor(Qt.PointingHandCursor)
        else:
            label.setTextInteractionFlags(label.textInteractionFlags() | Qt.TextSelectableByMouse)
        label.setFixedWidth(width)
        label.adjustSize()

        return label

    def _create_button(self, 
                        parent_widget: QWidget,
                        text: str = "",
                        stylesheet: str = "QPushButton {color: rgb(0, 0, 83); background-color: rgb(170, 255, 127); border-radius: 15px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(0, 67, 0), stop:1 rgb(0, 161, 0)); color: rgb(255, 255, 0)}"
                        ) -> QPushButton:
        btn = QPushButton(parent_widget)
        btn.setText(text)
        btn.setStyleSheet(stylesheet)
        btn.setCursor(Qt.PointingHandCursor)
        btn.resize(75, 23)

        return btn

    def _create_checkbox(self,
                        parent_widget: QWidget,
                        text: str = "",
                        width: int = None,
                        center: bool = False,
                        font_size: int = 12,
                        font_bold: bool = True,
                        fg_color: str = COLOR_GREEN,
                        hover_color: str = COLOR_LIGHT_GREEN
                        ) -> QCheckBox:

        chk = QCheckBox(parent_widget)
        chk.setText(text)
        stylesheet = f"QCheckBox {{color: {fg_color}; border: 0px; background-color: transparent;}} QCheckBox:hover {{color: {hover_color};}}"
        chk.setStyleSheet(stylesheet)
        if center:
            chk.setAlignment(Qt.AlignCenter)
        font = chk.font()
        font.setPointSize(font_size)
        font.setBold(font_bold)
        chk.setFont(font)
        chk.setFixedWidth(width)
        chk.adjustSize()

        return chk

    def info_label_context_menu(self, data_dict: dict, stt: settings_cls.Settings):
        if not data_dict.get("main_win"):
            return

        item_keys = ""
        item_values = ""
        for item in data_dict.get("affected_keys", []):
            item_keys += item.get("key", "") + "\n"
            item_values += str(item.get("value", "")) + "\n" + "-"*50 + "\n"
        item_keys = item_keys.strip(" -\n")
        item_values = item_values.strip(" -\n")

        disab = []
        if not item_keys:
            disab.append(10)
        elif len(data_dict.get("affected_keys", [])) > 1:
            item_keys = "-" * 50 + "\n" + item_keys
        if not item_values:
            disab.append(20)
        elif len(data_dict.get("affected_keys", [])) > 1:
            item_values = "-" * 50 + "\n" + item_values

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "items": [
                [10, stt.lang("app_settings_info_label_context_menu_key_names_text"), stt.lang("app_settings_info_label_context_menu_key_names_tt") + f"\n{item_keys}", True, [], stt.get_setting_value("copy_icon_path")],
                [20, stt.lang("app_settings_info_label_context_menu_key_values_text"), stt.lang("app_settings_info_label_context_menu_key_values_tt") + f"\n{item_values}", True, [], stt.get_setting_value("copy_icon_path")]
            ]
        }

        data_dict["main_win"]._dont_clear_menu = True
        stt.app_setting_set_value("menu", menu_dict)
        utility_cls.ContextMenu(stt, data_dict["main_win"])

        if menu_dict["result"] == 10:
            stt.app_setting_get_value("clipboard").setText(item_keys)
        elif menu_dict["result"] == 20:
            stt.app_setting_get_value("clipboard").setText(item_values)

    def _create_info_label(self, parent_widget: QWidget, width: int = 25, height: int = 25) -> QLabel:
        label = QLabel(parent_widget)
        label.resize(width, height)
        self.set_image_to_label(self.getv("info_icon_path"), label, strech_to_label=True)
        label.setAlignment(Qt.AlignCenter)
        label.setCursor(Qt.PointingHandCursor)
        label.setStyleSheet("QLabel {background-color: transparent; border: 0px;}")

        return label

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result

    def _get_float(self, text: str) -> float:
        result = None
        try:
            result = float(text)
        except:
            result = None
        return result

    def set_image_to_label(self, image_path: str, label: QLabel, strech_to_label: bool = False, resize_label: bool = False, resize_label_fixed_w: bool = False, resize_label_fixed_h: bool = False) -> bool:
        if not os.path.isfile(image_path):
            return False

        img = QPixmap()
        has_image = img.load(os.path.abspath(image_path))
        if not has_image:
            return False

        if strech_to_label:
            label.setScaledContents(True)
        else:
            label.setScaledContents(False)
            if resize_label:
                scale = img.width() / img.height()
                if scale >= 1:
                    label.resize(int(label.height() * scale), label.height())
                else:
                    label.resize(label.width(), int(label.width() / scale))
            if resize_label_fixed_w:
                scale = img.height() / img.width()
                label.resize(label.width(), int(label.width() * scale))
            if resize_label_fixed_h:
                scale = img.width() / img.height()
                label.resize(int(label.height() * scale), label.height())

            img = img.scaled(label.width(), label.height(), Qt.KeepAspectRatio)

        label.setPixmap(img)

        return True

    def resize_notify(self, notify_function):
        if notify_function:
            notify_function(self.size())

    def animate_setting_resize(self, widget: QWidget, start_height: int, end_height: int, duration: int = None, steps: int = None, resize_notify_function = None):
        if self.cancel_animation:
            widget.setFixedHeight(end_height)
            return
        
        if duration is None:
            duration = self.getv("app_setting_item_animation_duration")
        if steps is None:
            steps = self.getv("app_setting_item_animation_steps")

        widget.setFixedHeight(start_height)
        step_val = int((end_height - start_height) / steps)

        for i in range(steps):
            if step_val > 0:
                try:
                    widget.setFixedHeight(start_height + (i * step_val))
                except Exception as e:
                    UTILS.TerminalUtility.WarningMessage("#1 failed to complete animation.\nException:\n#2", ["animate_setting_resize", str(e)])
                    return
            else:
                try:
                    widget.setFixedHeight(start_height - (i * abs(step_val)))
                except Exception as e:
                    UTILS.TerminalUtility.WarningMessage("#1 failed to complete animation.\nException:\n#2", ["animate_setting_resize", str(e)])
                    return
            
            if resize_notify_function:
                resize_notify_function()

            QCoreApplication.processEvents()
            time.sleep((duration / steps) / 1000)
            QCoreApplication.processEvents()
        
        try:
            widget.setFixedHeight(end_height)
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("#1 failed to complete animation.\nException:\n#2", ["animate_setting_resize", str(e)])
            return

    def close_me(self):
        for child in self.children():
            child.deleteLater()
        self.deleteLater()


class ItemCheckBox(AbstractFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, item_data: dict) -> None:
        super().__init__(parent_widget, settings)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._parent_widget = parent_widget
        self.item_data = item_data
        self.expanded = self.item_data.get("expanded", False)

        self._define_me()
        self.cancel_animation = not self.getv("app_setting_animate_item_resize")
        
        # Widget Handler
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(self, global_properties)
        self.widget_handler.add_child(self.lbl_info, {"allow_bypass_mouse_press_event": False, "allow_bypass_enter_event": False, "allow_bypass_leave_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_default_value, {"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_Selection_Widget(self.chk_key_name)
        self.widget_handler.activate()

    def _on_info_clicked(self, e: QMouseEvent):
        self.widget_handler.find_child(self.lbl_info).EVENT_mouse_press_event(e)
        if e.button() == Qt.LeftButton:
            if self.expanded:
                self.collapse()
            else:
                self.expand()
        elif e.button() == Qt.RightButton:
            self.info_label_context_menu(self.item_data, self._stt)

    def _on_info_hover_enter(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(1)
    
    def _on_info_hover_leave(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(0.5)

    def _on_default_value_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_default_value).EVENT_mouse_press_event(e)
            if self.item_data["default"].lower() == "true":
                self.chk_key_name.setCheckState(Qt.Checked)
            else:
                self.chk_key_name.setCheckState(Qt.Unchecked)

    def _on_checkbox_state_changed(self, e):
        data = {
            "key": self.item_data["key"],
            "value": self.chk_key_name.isChecked(),
            "affected_keys": self.item_data["affected_keys"],
            "is_valid": True
        }
        self.item_data["feedback_function"](data)

    def _on_chk_key_name_drop_event(self, e: QDropEvent):
        if e.mimeData().hasText():
            if e.mimeData().text().lower() == "true":
                self.chk_key_name.setCheckState(Qt.Checked)
                e.accept()
            elif e.mimeData().text().lower() == "false":
                self.chk_key_name.setCheckState(Qt.Unchecked)
                e.accept()
            else:
                e.ignore()
        else:
            e.ignore()

    def _on_chk_key_name_drag_enter_event(self, e):
        if e.mimeData().hasText():
            if e.mimeData().text().lower() in ["true", "false"]:
                e.accept()
            else:
                e.ignore()

    def expand(self):
        h = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + 10
        
        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = True
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()
    
    def collapse(self):
        h = self.chk_key_name.pos().y() + self.chk_key_name.height() + 10
        
        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = False
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()

    def _define_me(self):
        w = self.item_data["width"] - self.X_PADDING * 2

        # Main Frame
        self._define_frame(self)

        # Label Info
        self.lbl_info = self._create_info_label(self)
        self.lbl_info.move(w - 25, self.Y_PADDING)
        self.lbl_info.mousePressEvent = self._on_info_clicked
        self.lbl_info_opacity = QGraphicsOpacityEffect()
        self.lbl_info_opacity.setOpacity(0.5)
        self.lbl_info.setGraphicsEffect(self.lbl_info_opacity)
        self.lbl_info.enterEvent = self._on_info_hover_enter
        self.lbl_info.leaveEvent = self._on_info_hover_leave

        # CheckBox
        self.chk_key_name: QCheckBox = self._create_checkbox(self, 
                                               self.item_data["name"], 
                                               width=w - 25 - self.X_PADDING,
                                               center=False, 
                                               font_size=self.item_data.get("font_size", 14), 
                                               font_bold=True)
        self.chk_key_name.move(self.X_PADDING, self.Y_PADDING)
        self.chk_key_name.setCursor(Qt.PointingHandCursor)
        if str(self.item_data["value"]).lower() == "true":
            self.chk_key_name.setCheckState(Qt.Checked)
        else:
            self.chk_key_name.setCheckState(Qt.Unchecked)
        self.chk_key_name.stateChanged.connect(self._on_checkbox_state_changed)
        self.chk_key_name.setAcceptDrops(True)
        self.chk_key_name.dropEvent = self._on_chk_key_name_drop_event
        self.chk_key_name.dragEnterEvent = self._on_chk_key_name_drag_enter_event

        y = self.chk_key_name.pos().y() + self.chk_key_name.height() + self.Y_PADDING
        y = max(y, self.lbl_info.pos().y() + self.lbl_info.height() + self.Y_PADDING)

        # Description Label
        self.lbl_description = self._create_label(self, 
                                                 self.item_data["desc"], 
                                                 width=w, 
                                                 center=True, 
                                                 font_size=9, 
                                                 font_bold=False,
                                                 fg_color=self.COLOR_GREY,
                                                 hover_color=self.COLOR_GREY)
        self.lbl_description.move(self.X_PADDING, y)

        y = self.lbl_description.pos().y() + self.lbl_description.height() + self.Y_SPACING

        # Recommended Value Label
        self.lbl_recommneded_value = self._create_label(self,
                                                        self.item_data["recomm"],
                                                        width=w,
                                                        center=True,
                                                        font_size=9,
                                                        font_bold=False,
                                                        fg_color=self.COLOR_LIGHT_GREEN,
                                                        hover_color=self.COLOR_LIGHT_GREEN)
        self.lbl_recommneded_value.move(self.X_PADDING, y)

        y = self.lbl_recommneded_value.pos().y() + self.lbl_recommneded_value.height() + self.Y_SPACING

        # Default value label
        if self.item_data["default"] is None:
            text = self.getl("app_settings_no_default_value_text")
            lbl_default_fg_color = self.COLOR_RED
            lbl_default_hover_color = self.COLOR_DARK_RED
        else:
            text = self.getl("app_settings_lbl_default_value_text") + "\n" + self.item_data["default"]
            lbl_default_fg_color = self.COLOR_BLUE
            lbl_default_hover_color = self.COLOR_LIGHT_BLUE

        self.lbl_default_value = self._create_label(self,
                                                    text,
                                                    width=w,
                                                    center=True,
                                                    font_size=9,
                                                    font_bold=False,
                                                    fg_color=lbl_default_fg_color,
                                                    hover_color=lbl_default_hover_color)
        self.lbl_default_value.move(self.X_PADDING, y)
        self.lbl_default_value.setCursor(Qt.PointingHandCursor)
        
        if self.item_data["default"] is not None:
            self.lbl_default_value.mousePressEvent = self._on_default_value_clicked

        y = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + self.Y_PADDING

        self.setFixedSize(w + self.X_PADDING * 2, y)
        if self.expanded:
            self.expand()
        else:
            self.collapse()


class ItemTitle(AbstractFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, item_data: dict) -> None:
        super().__init__(parent_widget, settings)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._parent_widget = parent_widget
        self.item_data = item_data
        self.expanded = self.item_data.get("expanded", False)

        self._define_me()

    def _arange_text(self, text: str, font_size: int = 13, font_bold: bool = True, fg_color: str = "#ffffff") -> str:
        if not text.count("\n"):
            return text

        text1 = text.split("\n")[0]
        text2 = "\n" + "\n".join(text.split("\n")[1:])

        text_to_html = utility_cls.TextToHTML()
        # text_to_html.general_rule.fg_color = fg_color
        text_to_html.general_rule.font_size = font_size
        text_to_html.general_rule.font_bold = font_bold

        rule = utility_cls.TextToHtmlRule(text="#--1",
                                          replace_with=text2,
                                          font_size=font_size - self.item_data.get("font_shrink", 4),
                                          font_bold=False)

        text_to_html.set_text(f"{text1}#--1")
        text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def _define_me(self):
        self._define_frame(self, stylesheet="QFrame {background-color: #576666; border: 1px solid #00aa00; border-radius: 10px;}", has_border=True)
        w = self.item_data["width"] - self.X_PADDING * 2

        # Title label
        lbl_title_bg_color = self.item_data.get("bg_color", self.COLOR_LIGHT_BLUE)
        lbl_title_fg_color = self.item_data.get("fg_color", self.COLOR_DARK_BLUE)
        lbl_title_hover_color = self.item_data.get("hover_color", "#000000")
        h_size = self.item_data.get("spacing_height", self.Y_SPACING)
        title_center = self.item_data.get("title_center", True)
        font_size = self.item_data.get("font_size", 13)
        font_bold = self.item_data.get("font_bold", True)
        name = self.item_data.get("name", "")
        name = self._arange_text(name, font_size=font_size+2, font_bold=font_bold, fg_color=lbl_title_fg_color)

        if not title_center:
            name = f" {name}"

        no_border_radius = lbl_title_bg_color == self.COLOR_LIGHT_BLUE
        
        self.lbl_title = self._create_label(self, 
                                            name,
                                            width=w, 
                                            center=title_center, 
                                            font_size=font_size,
                                            font_bold=font_bold,
                                            fg_color=lbl_title_fg_color, 
                                            hover_color=lbl_title_hover_color,
                                            bg_color=lbl_title_bg_color,
                                            no_mouse_interaction=self.item_data.get("no_mouse_interaction", False),
                                            no_border_radius=no_border_radius
                                            )
        self.lbl_title.move(self.X_PADDING, h_size)

        h = self.lbl_title.height() + h_size * 2

        self.setFixedSize(self.item_data["width"], h)


class ItemInput(AbstractFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, item_data: dict) -> None:
        super().__init__(parent_widget, settings)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._parent_widget = parent_widget
        self.item_data = item_data
        self.expanded = self.item_data.get("expanded", False)
        self.lbl_color = None
        self.lbl_clear = None

        self._define_me()
        self.cancel_animation = not self.getv("app_setting_animate_item_resize")

        # Widget Handler
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(self, global_properties)
        self.widget_handler.add_child(self.lbl_info, {"allow_bypass_mouse_press_event": False, "allow_bypass_enter_event": False, "allow_bypass_leave_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_default_value, {"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        if self.lbl_color:
            self.widget_handler.add_child(self.lbl_color, {"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        if self.lbl_clear:
            self.widget_handler.add_child(self.lbl_clear, {"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        if self.item_data.get("validator_type") != "shortcut":
            self.widget_handler.add_TextBox(self.txt_input, {"allow_bypass_mouse_press_event": True}, main_win=self)
        self.widget_handler.activate()

    def is_tag_list_valid(self, text: str):
        tags_db = db_tag_cls.Tag(self._stt)
        if not text:
            return True

        text_list = text.split(",")
        
        tag_list = tags_db.get_all_tags()
        tag_id_list = [x[0] for x in tag_list]
        tt = ""
        for tag in text_list:
            tag = self._get_integer(tag)
            if tag not in tag_id_list:
                return False
            tags_db.populate_values(tag)
            tt += tags_db.get_tag_name_cleaned() + "\n"
        tt = tt.strip()
        self.txt_input.setToolTip(tt)
        
        return True

    def _on_input_changed(self):
        text = self.txt_input.text().strip()

        if self.item_data.get("validator_type"):
            data = {
                "key": self.item_data["key"],
                "value": text,
                "affected_keys": self.item_data["affected_keys"],
                "is_valid": False
            }

            if self.item_data.get("validator_type") == "tags":
                text = text.strip(" ,")
                data["value"] = text
                if result := self.is_tag_list_valid(text):
                    data["is_valid"] = True
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_DEFAULT)
                else:
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                    data["is_valid"] = False
                self.item_data["feedback_function"](data)
                return

            if self.item_data.get("validator_type") == "color":
                data["value"] = text
                result = self._stt._is_valid_color(text)
                if not text:
                    result = True

                if not result:
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                    self.lbl_color_sample.setStyleSheet(self.lbl_color_sample_value.replace("#--1", "transparent"))
                    data["is_valid"] = False
                else:
                    data["is_valid"] = True
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_DEFAULT)
                    self.lbl_color_sample.setStyleSheet(self.lbl_color_sample_value.replace("#--1", text))

                self.item_data["feedback_function"](data)
                return

            if self.item_data.get("validator_type") == "file":
                data["value"] = text
                if os.path.isdir(text):
                    data["is_valid"] = True
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_DEFAULT)
                else:
                    data["is_valid"] = False
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)

                self.item_data["feedback_function"](data)
                return
            
            if self.item_data.get("validator_type") == "margins":
                data["value"] = text
                result = self._validate_margins(text)
                if not result:
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                    data["is_valid"] = False
                else:
                    data["is_valid"] = True
                    data["value"] = result
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_DEFAULT)

                self.item_data["feedback_function"](data)
                return


        self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_DEFAULT)

        data = {
            "key": self.item_data["key"],
            "value": text,
            "affected_keys": self.item_data["affected_keys"],
            "is_valid": False
        }

        if not text:
            data["is_valid"] = False
            self.item_data["feedback_function"](data)
            return

        if self._type_of_item_data(self.item_data) == int:
            result = self._get_integer(text)
            if result is None:
                self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                data["is_valid"] = False
                self.item_data["feedback_function"](data)
                return
            else:
                if (self.item_data["max"] is not None and result > self.item_data["max"]) or (self.item_data["min"] is not None and result < self.item_data["min"]):
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                    data["is_valid"] = False
                    self.item_data["feedback_function"](data)
                    return
        elif self._type_of_item_data(self.item_data) == float:
            result = self._get_float(text)
            if result is None:
                self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                data["is_valid"] = False
                self.item_data["feedback_function"](data)
                return
            else:
                if (self.item_data["max"] is not None and result > self.item_data["max"]) or (self.item_data["min"] is not None and result < self.item_data["min"]):
                    self.txt_input.setStyleSheet(self.LINE_EDIT_STYLESHEET_ILLEGAL_ENTRY)
                    data["is_valid"] = False
                    self.item_data["feedback_function"](data)
                    return

        data["is_valid"] = True
        self.item_data["feedback_function"](data)

    def _validate_margins(self, text: str) -> str:
        if not text:
            return ""
        
        result = ""

        try:
            margins = [int(x) for x in text.split(",") if int(x) >= 0]
            if len(margins) == 4:
                result = ",".join([str(x) for x in margins])
        except:
            pass

        return result

    def _type_of_item_data(self, item_data: dict) -> str:
        if self._stt.is_setting_key_exist(item_data["key"]):
            return type(self.getv(item_data["key"]))
        if item_data.get("affected_keys"):
            return type(self.getv(item_data["affected_keys"][0]["key"]))

        UTILS.TerminalUtility.WarningMessage("Invalid item data! No valid type found.\nitem_data[key]: #1\nitem_data[affected_keys]: #2", [item_data.get("key"), item_data.get("affected_keys")], exception_raised=True)
        raise ValueError("Invalid item data! No valid type found.")

    def _on_info_clicked(self, e: QMouseEvent):
        lbl_info_height = self.lbl_info.height()
        self.widget_handler.find_child(self.lbl_info).EVENT_mouse_press_event(e)
        if e.button() == Qt.LeftButton:
            if self.expanded:
                self.collapse(lbl_info_height=lbl_info_height)
            else:
                self.expand()
        elif e.button() == Qt.RightButton:
            self.info_label_context_menu(self.item_data, self._stt)

    def _on_info_hover_enter(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(1)
    
    def _on_info_hover_leave(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(0.5)

    def _on_default_value_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_default_value).EVENT_mouse_press_event(e)
            if self.item_data.get("validator_type") == "shortcut":
                self.txt_input.setKeySequence(str(self.item_data["default"]))
            else:
                self.txt_input.setText(str(self.item_data["default"]))
    
    def expand(self):
        h = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + 10
        # self.setFixedHeight(h)
        
        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = True
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()
    
    def collapse(self, lbl_info_height: int = None):
        if lbl_info_height is None:
            lbl_info_height = self.lbl_info.height()
        h = max(self.txt_input.pos().y() + self.txt_input.height() + 10, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + 10, self.lbl_info.pos().y() + lbl_info_height + 10)

        if self.item_data.get("validator_type") == "shortcut":
            h = self.lbl_warning.pos().y() + self.lbl_warning.height() + self.Y_PADDING

        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = False
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()

    def _on_key_sequence_changed(self):
        text = self.txt_input.keySequence().toString()

        if not text:
            self.lbl_warning.setText(self.getl("app_setting_shortcut_select_warning_default_text"))
            self.lbl_warning.setStyleSheet(f"QLabel {{color: {self.COLOR_YELLOW};}}")
        else:
            keys_for_shortcut = []
            for key in self.item_data.get("validator_data", []):
                if key[0] == text:
                    keys_for_shortcut.append(key[1])
            if keys_for_shortcut:
                self.lbl_warning.setText(self.getl("app_setting_shortcut_select_warning_has_data_text"))
                tt = self.getl("app_setting_shortcut_select_warning_has_data_tt") + "\n" + "\n".join(keys_for_shortcut)
                self.lbl_warning.setToolTip(tt)
                self.lbl_warning.setStyleSheet(f"QLabel {{color: {self.COLOR_RED};}}")
            else:
                self.lbl_warning.setText(self.getl("app_setting_shortcut_select_warning_no_data_text"))
                self.lbl_warning.setToolTip(self.getl("app_setting_shortcut_select_warning_no_data_tt"))
                self.lbl_warning.setStyleSheet(f"QLabel {{color: {self.COLOR_GREEN};}}")

        data = {
            "key": self.item_data["key"],
            "value": text,
            "affected_keys": self.item_data["affected_keys"],
            "is_valid": True
        }

        self.item_data["feedback_function"](data)

    def _on_textbox_double_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            result = self._select_directory()
            if result:
                self.txt_input.setText(result)

    def _on_drop_event(self, e: QDropEvent):
        if e.mimeData().hasText():
            self.txt_input.setText(e.mimeData().text())
            e.accept()
        else:
            e.ignore()

    def _select_directory(self) -> str:
        folder_path = ""
        if os.path.exists(self.item_data["value"]):
            folder_path = self.item_data["value"]

        return QFileDialog.getExistingDirectory(self, self.getl("app_setting_directory_select_title"), folder_path)

    def _lbl_clear_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_clear).EVENT_mouse_press_event(e)
            self.txt_input.setKeySequence("")

    def _on_lbl_color_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_color).EVENT_mouse_press_event(e)
            color_dialog = QColorDialog(self)
            for i in range(16):
                color_dialog.setCustomColor(i, QColor("white"))

            if self._stt._is_valid_color(self.txt_input.text()):
                color_dialog.setCustomColor(0, QColor(self.txt_input.text()))
                color_dialog.setCurrentColor(QColor(self.txt_input.text()))
            if color_dialog.exec_() == QColorDialog.Accepted:
                color = color_dialog.selectedColor()
                self.txt_input.setText(color.name())
                self.lbl_color_sample.setStyleSheet(self.lbl_color_sample_value.replace("#--1", color.name()))

    def _define_me(self):
        w = self.item_data["width"] - self.X_PADDING * 2

        # Main Frame
        self._define_frame(self)

        # Input - LineEdit
        self.lbl_clear = None
        if self.item_data.get("validator_type") == "shortcut":
            self.txt_input = QKeySequenceEdit(self)
            self.txt_input.resize(60, 23)
            self.txt_input.setStyleSheet("QKeySequenceEdit {color: #00007f; background-color: #ffffff; border: 1px solid #ffff00;} QKeySequenceEdit:focus {background-color: #ffff00;} QKeySequenceEdit:hover {background-color: #ffff7f;}")
            self.txt_input.setKeySequence(str(self.item_data["value"]))
            self.txt_input.keySequenceChanged.connect(self._on_key_sequence_changed)
            self.txt_input.move(self.X_PADDING + 20, self.Y_PADDING)

            self.lbl_clear = QLabel(self)
            self.lbl_clear.setFixedSize(15, 15)
            self.lbl_clear.setScaledContents(True)
            self.lbl_clear.setPixmap(QPixmap(self.getv("cancel_icon_path")))
            self.lbl_clear.move(self.X_PADDING, self.Y_PADDING + 4)
            self.lbl_clear.mousePressEvent = self._lbl_clear_clicked
        else:        
            self.txt_input = self._create_line_edit(self)
            self.txt_input.setText(str(self.item_data["value"]))
            self.txt_input.textChanged.connect(self._on_input_changed)
            self.txt_input.dropEvent = self._on_drop_event
            self.txt_input.move(self.X_PADDING, self.Y_PADDING)
            
        if self.item_data.get("validator_type") == "margins":
            if not self.item_data.get("input_box_width"):
                self.item_data["input_box_width"] = 120

        if self.item_data.get("input_box_width"):
            self.txt_input.resize(self.item_data["input_box_width"], self.txt_input.height())
        
        if self.item_data.get("validator_type") == "file":
            self.txt_input.mouseDoubleClickEvent = self._on_textbox_double_click

        # Label Color
        color_w = 0
        if self.item_data.get("validator_type") == "color":
            self.txt_input.resize(100, self.txt_input.height())

            self.lbl_color_sample = QLabel(self)
            self.lbl_color_sample.setFixedSize(self.txt_input.height(), self.txt_input.height())
            self.lbl_color_sample_value = "QLabel {background-color: #--1; border: 0px;}"
            if self.item_data['value']:
                self.lbl_color_sample.setStyleSheet(self.lbl_color_sample_value.replace("#--1", self.item_data['value']))
            else:
                self.lbl_color_sample.setStyleSheet(self.lbl_color_sample_value.replace("#--1", "transparent"))
            self.lbl_color_sample.move(self.txt_input.pos().x() + self.txt_input.width() + self.X_SPACING, self.txt_input.pos().y())
            
            color_x = self.lbl_color_sample.pos().x() + self.lbl_color_sample.width() + self.X_SPACING

            self.lbl_color = self._create_info_label(self)
            self.lbl_color.setPixmap(QPixmap(self.getv("color_icon_path")))
            self.lbl_color.setStyleSheet("QLabel {border: 0px;} QLabel:hover {border: 1px solid #ffff00;}")
            self.lbl_color.move(color_x, self.txt_input.pos().y())
            self.lbl_color.resize(self.txt_input.height(), self.txt_input.height())
            self.lbl_color.setCursor(Qt.PointingHandCursor)
            self.lbl_color.mousePressEvent = self._on_lbl_color_clicked
            color_w += self.lbl_color_sample.width() + self.lbl_color.width() + self.X_SPACING * 3

        # Label Info
        self.lbl_info = self._create_info_label(self)
        self.lbl_info.move(w - 25, self.txt_input.pos().y())
        self.lbl_info.mousePressEvent = self._on_info_clicked
        self.lbl_info_opacity = QGraphicsOpacityEffect()
        self.lbl_info_opacity.setOpacity(0.5)
        self.lbl_info.setGraphicsEffect(self.lbl_info_opacity)
        self.lbl_info.enterEvent = self._on_info_hover_enter
        self.lbl_info.leaveEvent = self._on_info_hover_leave

        # Key Name Label
        lbl_key_name_width = w - (self.txt_input.width() + self.X_SPACING + self.lbl_info.width() + self.X_SPACING + 5 + color_w)
        if self.lbl_clear:
            lbl_key_name_width -= 20
            
        self.lbl_key_name = self._create_label(self, 
                                               self.item_data["name"], 
                                               width=lbl_key_name_width,
                                               center=True, 
                                               font_size=self.item_data.get("font_size", 14), 
                                               font_bold=True)
        self.lbl_key_name.move(self.txt_input.pos().x() + self.txt_input.width() + self.X_SPACING + color_w, self.Y_PADDING)
        self.lbl_key_name.mousePressEvent = self._on_info_clicked
        self.lbl_key_name.setCursor(Qt.PointingHandCursor)

        y = max(self.txt_input.pos().y() + self.txt_input.height() + self.Y_SPACING, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + self.Y_PADDING)
        y = max(y, self.lbl_info.pos().y() + self.lbl_info.height() + self.Y_PADDING)

        if self.item_data.get("validator_type") == "shortcut":
            y -= self.Y_PADDING
            y += self.Y_SPACING
            self.lbl_warning = self._create_label(self,
                                                  self.getl("app_setting_shortcut_select_warning_default_text"),
                                                  width=w,
                                                  center=True,
                                                  font_size=9,
                                                  font_bold=False,
                                                  fg_color=self.COLOR_YELLOW,
                                                  hover_color=self.COLOR_LIGHT_YELLOW)
            self.lbl_warning.move(self.X_PADDING, y)
            self.lbl_warning.setToolTip(self.getl("app_setting_shortcut_select_warning_default_tt"))
            y += self.lbl_warning.height() + self.Y_PADDING

        # Description Label
        self.lbl_description = self._create_label(self, 
                                                 self.item_data["desc"], 
                                                 width=w, 
                                                 center=True, 
                                                 font_size=9, 
                                                 font_bold=False,
                                                 fg_color=self.COLOR_GREY,
                                                 hover_color=self.COLOR_GREY)
        self.lbl_description.move(self.X_PADDING, y)

        y = self.lbl_description.pos().y() + self.lbl_description.height() + self.Y_SPACING

        # Recommended Value Label
        self.lbl_recommneded_value = self._create_label(self,
                                                        self.item_data["recomm"],
                                                        width=w,
                                                        center=True,
                                                        font_size=9,
                                                        font_bold=False,
                                                        fg_color=self.COLOR_LIGHT_GREEN,
                                                        hover_color=self.COLOR_LIGHT_GREEN)
        self.lbl_recommneded_value.move(self.X_PADDING, y)

        y = self.lbl_recommneded_value.pos().y() + self.lbl_recommneded_value.height() + self.Y_SPACING

        # Default value label
        if self.item_data["default"] is None:
            text = self.getl("app_settings_no_default_value_text")
            lbl_default_fg_color = self.COLOR_RED
            lbl_default_hover_color = self.COLOR_DARK_RED
        else:
            text = self.getl("app_settings_lbl_default_value_text") + "\n" + self.item_data["default"]
            lbl_default_fg_color = self.COLOR_BLUE
            lbl_default_hover_color = self.COLOR_LIGHT_BLUE

        self.lbl_default_value = self._create_label(self,
                                                    text,
                                                    width=w,
                                                    center=True,
                                                    font_size=9,
                                                    font_bold=False,
                                                    fg_color=lbl_default_fg_color,
                                                    hover_color=lbl_default_hover_color)
        self.lbl_default_value.move(self.X_PADDING, y)
        self.lbl_default_value.setCursor(Qt.PointingHandCursor)

        if self.item_data["default"] is not None:
            self.lbl_default_value.mousePressEvent = self._on_default_value_clicked

        y = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + self.Y_PADDING

        self.setFixedSize(w + self.X_PADDING * 2, y)
        if self.expanded:
            self.expand()
        else:
            self.collapse()


class ItemComboBox(AbstractFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, item_data: dict) -> None:
        super().__init__(parent_widget, settings)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._parent_widget = parent_widget
        self.item_data = item_data
        self.expanded = self.item_data.get("expanded", False)
        self.ignore_changes = False
        self.icon_enlarged = False

        self._define_me()
        self.cancel_animation = not self.getv("app_setting_animate_item_resize")

        # Widget Handler
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(self, global_properties)
        self.widget_handler.add_child(self.lbl_info, {"allow_bypass_mouse_press_event": False, "allow_bypass_enter_event": False, "allow_bypass_leave_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_default_value, {"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_Selection_Widget(self.cmb_input)
        self.widget_handler.activate()

    def _on_input_changed(self):
        if not self.cmb_input.currentText():
            return
        
        if self.ignore_changes:
            return

        if self.item_data.get("cmb_data") == "icon":
            if self.cmb_input.currentIndex() == 1:
                self.ignore_changes = True
                file_util = utility_cls.FileDialog(self._stt)
                file_path = file_util.show_dialog(title=self.item_data["name"], directory=os.path.dirname(self.cmb_input.currentData()), file_filter="images", settings=self._stt)
                if file_path:
                    img = QPixmap()
                    result = img.load(file_path)
                    if not result:
                        QMessageBox.warning(self, self.getl("app_settings_err_image_load"), self.getl("app_settings_err_image_load_text"))
                        self.ignore_changes = False
                        return
                    self.cmb_input.setItemData(1, file_path)
            
            if self.lbl_icon.isVisible():
                if self.cmb_input.currentData() != " custom" and self.cmb_input.currentData():
                    self.lbl_icon.setPixmap(QPixmap(self.cmb_input.currentData()))
                elif self.cmb_input.currentIndex() == 0:
                    self.lbl_icon.setPixmap(QPixmap())

            self.ignore_changes = False
            if self.cmb_input.currentData() == " custom":
                return
        if self.item_data.get("cmb_data") == "cursor":
            if self.cmb_input.currentIndex() == 1:
                self.ignore_changes = True
                file_util = utility_cls.FileDialog(self._stt)
                file_path = file_util.show_dialog(title=self.item_data["name"], directory=os.path.dirname(self.cmb_input.currentData()), file_filter="images", settings=self._stt)
                if file_path:
                    img = QPixmap()
                    result = img.load(file_path)
                    if not result:
                        QMessageBox.warning(self, self.getl("app_settings_err_image_load"), self.getl("app_settings_err_image_load_text"))
                        self.ignore_changes = False
                        return
                    self.cmb_input.setItemData(1, file_path)
            
            if self.lbl_icon.isVisible():
                self._set_lbl_icon_cursor()

            self.ignore_changes = False
            if self.cmb_input.currentData() == " custom":
                return

        if self.item_data.get("cmb_data") == "animation":
            if self.cmb_input.currentIndex() == 1:
                self.ignore_changes = True
                file_util = utility_cls.FileDialog(self._stt)
                file_path = file_util.show_dialog(title=self.item_data["name"], directory=os.path.dirname(self.cmb_input.currentData()), file_filter="animation", settings=self._stt)
                if file_path:
                    try:
                        anim = QMovie()
                        anim.setFileName(file_path)
                        result = anim.isValid()
                        anim.deleteLater()
                        anim = None
                    except:
                        result = False
                    
                    if not result:
                        QMessageBox.warning(self, self.getl("app_settings_err_image_load"), self.getl("app_settings_err_animation_load_text"))
                        self.ignore_changes = False
                        return
                    self.cmb_input.setItemData(1, file_path)
            
            if self.lbl_icon.isVisible():
                if self.cmb_input.currentData() != " custom" and self.cmb_input.currentData():
                    self.animation_movie.stop()
                    self.animation_movie = QMovie(self.cmb_input.currentData())
                    self.lbl_icon.setMovie(self.animation_movie)
                    self.animation_movie.start()
                elif self.cmb_input.currentIndex() == 0:
                    self.animation_movie.stop()
                    self.animation_movie = QMovie()
                    self.lbl_icon.setMovie(self.animation_movie)

            self.ignore_changes = False
            if self.cmb_input.currentData() == " custom":
                return
        elif self.item_data.get("cmb_data") == "sound":
            if self.cmb_input.currentIndex() == 1:
                self.ignore_changes = True
                file_util = utility_cls.FileDialog(self._stt)
                file_path = file_util.show_dialog(title=self.item_data["name"], directory=os.path.dirname(self.cmb_input.currentData()))
                if file_path:
                    img = QPixmap()
                    result = self._load_sound_to_player(file_path)
                    if not result:
                        QMessageBox.warning(self, self.getl("app_settings_err_image_load"), self.getl("app_settings_err_image_load_text"))
                        self.ignore_changes = False
                        return
                    self.cmb_input.setItemData(1, file_path)
            
            if self.cmb_input.currentData() != " custom" and self.cmb_input.currentData():
                self._load_sound_to_player(self.cmb_input.currentData())
            else:
                self._load_sound_to_player("")

            self.ignore_changes = False
            if self.cmb_input.currentData() == " custom":
                return

        data = {
            "key": self.item_data["key"],
            "value": self.cmb_input.currentData(),
            "affected_keys": self.item_data["affected_keys"],
            "is_valid": True
        }
        self.item_data["feedback_function"](data)

    def _set_lbl_icon_cursor(self, cursor_data: str = None):
        if cursor_data is None:
            cursor_data = self.cmb_input.currentData()
    
        if not cursor_data or cursor_data == " custom":
            self.lbl_icon.setCursor(QCursor())
        else:
            if self._get_integer(cursor_data) is not None:
                cur = QCursor()
                cur.setShape(self._get_integer(cursor_data))
                self.lbl_icon.setCursor(cur)
            else:
                self.lbl_icon.setCursor(QCursor(QPixmap(cursor_data)))

    def _on_info_clicked(self, e: QMouseEvent):
        lbl_info_height = self.lbl_info.height()
        self.widget_handler.find_child(self.lbl_info).EVENT_mouse_press_event(e)
        if e.button() == Qt.LeftButton:
            if self.expanded:
                self.collapse(lbl_info_height=lbl_info_height)
            else:
                self.expand()
        elif e.button() == Qt.RightButton:
            self.info_label_context_menu(self.item_data, self._stt)

    def _load_sound_to_player(self, file_path):
        result = self.mp_sound.set_media_source(file_path)
        
        return result

    def _on_info_hover_enter(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(1)
    
    def _on_info_hover_leave(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(0.5)

    def _on_default_value_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_default_value).EVENT_mouse_press_event(e)
            for item in range(self.cmb_input.count()):
                if str(self.cmb_input.itemData(item)) == str(self.item_data["default"]):
                    self.cmb_input.setCurrentIndex(item)
                    break

    def _on_lbl_icon_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            if self.icon_enlarged:
                self.lbl_icon.move(self.X_PADDING, max(self.Y_PADDING, self.cmb_input.pos().y() + self.cmb_input.height() - 40))
                self.lbl_icon.resize(40, 40)
                self.icon_enlarged = False
                self.lbl_icon.setStyleSheet("background-color: transparent;")
                self.collapse()
            else:
                w = self.lbl_info.pos().x() + self.lbl_info.width() - self.lbl_icon.pos().x()
                self.lbl_icon.raise_()
                self.lbl_icon.setStyleSheet("background-color: #5555ff;")
                self.lbl_icon.move(self.X_PADDING, self.Y_PADDING)
                self.lbl_icon.resize(w, w)
                self.icon_enlarged = True
                self.expand()

    def expand(self):
        h = max(self.lbl_default_value.pos().y() + self.lbl_default_value.height() + 10,
                self.lbl_icon.pos().y() + self.lbl_icon.height() + 10)

        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = True
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()
    
    def collapse(self, lbl_info_height: int = None):
        if lbl_info_height is None:
            lbl_info_height = self.lbl_info.height()
        h = max(self.cmb_input.pos().y() + self.cmb_input.height() + 10,
                self.lbl_key_name.pos().y() + self.lbl_key_name.height() + 10,
                self.lbl_info.pos().y() + lbl_info_height + 10)
        if self.lbl_icon.isVisible():
            h = max(self.lbl_icon.pos().y() + self.lbl_icon.height() + 10, h)

        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = False
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()

    def _get_cmb_data(self, data) -> list:
        if not isinstance(data, str):
            return data

        result = []

        if data == "frame_shape":
            result = [
                ["NoFrame", 0],
                ["Box", 1],
                ["Panel", 2],
                ["WinPanel", 3],
                ["HLine", 4],
                ["VLine", 5],
                ["StyledPanel", 6]
            ]
        elif data == "frame_shadow":
            result = [
                ["Plain", 16],
                ["Raised", 32],
                ["Sunken", 48]
            ]
        elif data == "long_date":
            result = [
                ["(0) - ShortDate", 0],
                ["(1) - ShowDayName", 1],
                ["(2) - ShowMonthName", 2],
                ["(3) - ShowDayMonthName", 3]
            ]
        elif data == "icon":
            image_folder = "data/app/images"
            images = os.listdir(image_folder)
            result = [
                [self.getl("app_settings_combobox_item_no_icon_text"), "", self.getv("no_icon_icon_path")],
                [self.getl("app_settings_combobox_item_icon_custom_text"), " custom", self.getv("custom_icon_icon_path")]
            ]
            for image in images:
                if image.endswith((".bmp", ".cur", ".gif", ".ico", ".jpg", ".jpeg", ".pbm", ".pgm", ".png", ".ppm", ".svg", ".tif", ".tiff", ".xbm", ".xpm")):
                    result.append([image, f"{image_folder}/{image}", ""])
        elif data == "animation":
            image_folder = "data/app/animation"
            images = os.listdir(image_folder)
            result = [
                [self.getl("app_settings_combobox_item_no_animation_text"), "", self.getv("no_icon_icon_path")],
                [self.getl("app_settings_combobox_item_animation_custom_text"), " custom", self.getv("custom_icon_icon_path")]
            ]
            for image in images:
                if image.endswith((".gif", ".webp", ".mng")):
                    result.append([image, f"{image_folder}/{image}", ""])
        elif data == "cursor":
            result = [
                ["(-) - Default", "", self.getv("no_icon_icon_path")],
                [self.getl("app_settings_combobox_item_custom_cursor_text"), " custom", self.getv("custom_icon_icon_path")],
                ["(0) - ArrowCursor", "0", ""],
                ["(1) - UpArrowCursor", "1", ""],
                ["(2) - CrossCursor", "2", ""],
                ["(3) - WaitCursor", "3", ""],
                ["(4) - IBeamCursor", "4", ""],
                ["(5) - SizeVerCursor", "5", ""],
                ["(6) - SizeHorCursor", "6", ""],
                ["(7) - SizeBDiagCursor", "7", ""],
                ["(8) - SizeFDiagCursor", "8", ""],
                ["(9) - SizeAllCursor", "9", ""],
                ["(10) - BlankCursor", "10", ""],
                ["(11) - SplitVCursor", "11", ""],
                ["(12) - SplitHCursor", "12", ""],
                ["(13) - PointingHandCursor", "13", ""],
                ["(14) - ForbiddenCursor", "14", ""],
                ["(15) - WhatsThisCursor", "15", ""],
                ["(16) - BusyCursor", "16", ""],
                ["(17) - OpenHandCursor", "17", ""],
                ["(18) - ClosedHandCursor", "18", ""],
                ["(19) - DragCopyCursor", "19", ""],
                ["(20) - DragMoveCursor", "20", ""],
                ["(21) - DragLinkCursor", "21", ""]
            ]
        elif data == "sound":
            sound_folder = "data/app/sounds"
            sounds = os.listdir(sound_folder)
            result = [
                [self.getl("app_settings_combobox_item_no_sound_text"), "", self.getv("no_sound_icon_path")],
                [self.getl("app_settings_combobox_item_sound_custom_text"), " custom", self.getv("custom_sound_icon_path")]
            ]
            for sound in sounds:
                if sound.endswith((".wav", ".mp3", ".ogg", ".aac")):
                    result.append([sound, f"{sound_folder}/{sound}", ""])
        elif data == "line_wrap_mode":
            result = [
                ["0 - NoWrap", 0],
                ["1 - WidgetWidth", 1],
                ["2 - FixedPixelWidth", 2],
                ["3 - FixedColumnWidth", 3]
            ]
        elif data == "align" or data == "alignment":
            result = [
                ["1 - AlignLeft", 1],
                ["2 - AlignRight", 2],
                ["4 - AlignHCenter", 4],
                ["8 - AlignJustify", 8],
                ["32 - AlignTop", 32],
                ["64 - AlignBottom", 64],
                ["128 - AlignVCenter", 128]
            ]
        elif data == "day_of_week":
            result = [
                [f"(1) - {self.getl('week_day1')}", 1],
                [f"(2) - {self.getl('week_day2')}", 2],
                [f"(3) - {self.getl('week_day3')}", 3],
                [f"(4) - {self.getl('week_day4')}", 4],
                [f"(5) - {self.getl('week_day5')}", 5],
                [f"(6) - {self.getl('week_day6')}", 6],
                [f"(7) - {self.getl('week_day7')}", 7]
            ]
        elif data == "extra_image_src":
            result = [
                [f"(1) - {self.getl('extra_image_src1')}", 1],
                [f"(2) - {self.getl('extra_image_src2')}", 2],
                [f"(3) - {self.getl('extra_image_src3')}", 3],
                [f"(4) - {self.getl('extra_image_src4')}", 4],
                [f"(5) - {self.getl('extra_image_src5')}", 5]
            ]
        elif data == "extra_image_layout":
            result = [
                [f"(1) - {self.getl('extra_image_layout1')}", 1],
                [f"(2) - {self.getl('extra_image_layout2')}", 2]
            ]
        elif data == "extra_image_animate_style":
            result = [
                [f"(0) - {self.getl('extra_image_animate_style0')}", 0],
                [f"(1) - {self.getl('extra_image_animate_style1')}", 1],
                [f"(2) - {self.getl('extra_image_animate_style2')}", 2],
                [f"(3) - {self.getl('extra_image_animate_style3')}", 3],
                [f"(4) - {self.getl('extra_image_animate_style4')}", 4],
                [f"(5) - {self.getl('extra_image_animate_style5')}", 5],
                [f"(6) - {self.getl('extra_image_animate_style6')}", 6]
            ]
        elif data == "dict_search_engine":
            result = [
                [f"(1) - {self.getl('dict_search_engine1')}", 1],
                [f"(2) - {self.getl('dict_search_engine2')}", 2]
            ]
        elif data == "label_content_type":
            result = [
                [f"(0) - {self.getl('label_content_type_text')}", 0],
                [f"(1) - {self.getl('label_content_type_image')}", 1],
                [f"(2) - {self.getl('label_content_type_animation')}", 2]
            ]
        elif data == "toolbar_button_style":
            result = [
                [f"(0) - {self.getl('ToolButtonIconOnly')}", 0],
                [f"(1) - {self.getl('ToolButtonTextOnly')}", 1],
                [f"(2) - {self.getl('ToolButtonTextBesideIcon')}", 2],
                [f"(3) - {self.getl('ToolButtonTextUnderIcon')}", 3]
            ]

        return result

    def _define_me(self):
        w = self.item_data["width"] - self.X_PADDING * 2

        # Main Frame
        self._define_frame(self)

        icon_shrink = 0
        widget_type = ""
        if self.item_data.get("cmb_data") in ["icon", "animation", "cursor"]:
            widget_type = self.item_data.get("cmb_data")
            icon_shrink = 50
        elif self.item_data.get("cmb_data") == "sound":
            widget_type = "sound"

        # Input - ComboBox
        cmb_data = self._get_cmb_data(self.item_data.get("cmb_data", []))
        cmb_font_size = 12
        if self.item_data.get("input_box_width") == -1:
            cmb_font_size = 14

        self.cmb_input = self._create_combobox(self,
                                               data=cmb_data,
                                               font_size=cmb_font_size
                                               )
        self.cmb_input.move(self.X_PADDING, self.Y_PADDING)
        for item in range(self.cmb_input.count()):
            if str(self.cmb_input.itemData(item)) == str(self.item_data["value"]):
                self.cmb_input.setCurrentIndex(item)
                break
        else:
            if self.item_data.get("input_box_width") == -1:
                self.cmb_input.setCurrentIndex(1)
                self.cmb_input.setItemData(1, str(self.item_data["value"]))

        if self.item_data.get("input_box_width"):
            if self.item_data["input_box_width"] > 0:
                self.cmb_input.resize(self.item_data["input_box_width"], self.cmb_input.height())
            elif self.item_data["input_box_width"] == -1:
                self.cmb_input.resize(w - icon_shrink, self.cmb_input.height())

        self.cmb_input.currentTextChanged.connect(self._on_input_changed)

        # Label Info
        self.lbl_info = self._create_info_label(self)
        self.lbl_info.move(w - 25, self.Y_PADDING)
        self.lbl_info.mousePressEvent = self._on_info_clicked
        self.lbl_info_opacity = QGraphicsOpacityEffect()
        self.lbl_info_opacity.setOpacity(0.5)
        self.lbl_info.setGraphicsEffect(self.lbl_info_opacity)
        self.lbl_info.enterEvent = self._on_info_hover_enter
        self.lbl_info.leaveEvent = self._on_info_hover_leave

        # Media Player widget
        sound_shrink = 0
        if widget_type == "sound":
            self.mp_sound = media_player_cls.MediaPlayer(self)
            self.mp_sound.move(self.X_PADDING, self.Y_PADDING)
            self._load_sound_to_player(self.item_data["value"])
            sound_shrink = self.mp_sound.width() + self.X_SPACING

        # Key Name Label
        width_shrink = self.cmb_input.pos().x() + self.cmb_input.width() + self.X_SPACING + self.lbl_info.width() + 5
        key_name_pos_x = self.cmb_input.pos().x() + self.cmb_input.width() + self.X_SPACING
        if self.item_data.get("input_box_width") == -1:
            width_shrink = self.lbl_info.width() + 5 + icon_shrink + sound_shrink + self.X_PADDING
            key_name_pos_x = self.X_PADDING + icon_shrink + sound_shrink

        self.lbl_key_name = self._create_label(self, 
                                               self.item_data["name"], 
                                               width=w - width_shrink,
                                               center=True, 
                                               font_size=self.item_data.get("font_size", 14),
                                               font_bold=True)
        self.lbl_key_name.move(key_name_pos_x, self.Y_PADDING)
        self.lbl_key_name.mousePressEvent = self._on_info_clicked
        self.lbl_key_name.setCursor(Qt.PointingHandCursor)
        
        
        if self.item_data.get("input_box_width") == -1:
            if widget_type in ["icon", "animation", "cursor"]:
                self.cmb_input.move(self.X_PADDING + icon_shrink, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + self.Y_SPACING)
            elif widget_type == "sound":
                self.cmb_input.move(self.X_PADDING + icon_shrink, max(self.mp_sound.pos().y() + self.mp_sound.height() + self.Y_SPACING, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + self.Y_SPACING))

        # Label Icon
        self.lbl_icon = QLabel(self)
        self.lbl_icon.move(self.X_PADDING, max(self.Y_PADDING, self.cmb_input.pos().y() + self.cmb_input.height() - 40))
        self.lbl_icon.resize(40, 40)
        self.lbl_icon.setScaledContents(True)
        self.lbl_icon.setStyleSheet("background-color: transparent;")
        
        if widget_type == "icon":
            self.lbl_icon.setPixmap(QPixmap(str(self.item_data["value"])))
        elif widget_type == "animation":
            self.animation_movie = QMovie(str(self.item_data["value"])) if self.item_data.get("value") else QMovie()
            self.lbl_icon.setMovie(self.animation_movie)
            if self.item_data.get("value"):
                self.animation_movie.start()
        elif widget_type == "cursor":
            self.lbl_icon.setAlignment(Qt.AlignCenter)
            self.lbl_icon.setText(self.getl("app_settings_cursor_cmb_icon_text"))
            self.lbl_icon.setStyleSheet("QLabel {color: #ffff00; background-color: #000000; border: 1px solid #00ff00;}")
            self._set_lbl_icon_cursor(self.item_data["value"])

        self.lbl_icon.setVisible(False)
        if self.item_data.get("cmb_data") in ["icon", "animation", "cursor"] and self.item_data.get("input_box_width") == -1:
            self.lbl_icon.setVisible(True)
        
        self.lbl_icon.mousePressEvent = self._on_lbl_icon_clicked

        y = max(self.cmb_input.pos().y() + self.cmb_input.height() + self.Y_PADDING, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + self.Y_PADDING)
        y = max(y, self.lbl_info.pos().y() + self.lbl_info.height() + self.Y_PADDING)
        if widget_type == "sound":
            y = max(y, self.mp_sound.pos().y() + self.mp_sound.height() + self.Y_PADDING)

        # Description Label
        self.lbl_description = self._create_label(self, 
                                                 self.item_data["desc"], 
                                                 width=w, 
                                                 center=True, 
                                                 font_size=9, 
                                                 font_bold=False,
                                                 fg_color=self.COLOR_GREY,
                                                 hover_color=self.COLOR_GREY)
        self.lbl_description.move(self.X_PADDING, y)

        y = self.lbl_description.pos().y() + self.lbl_description.height() + self.Y_SPACING

        # Recommended Value Label
        self.lbl_recommneded_value = self._create_label(self,
                                                        self.item_data["recomm"],
                                                        width=w,
                                                        center=True,
                                                        font_size=9,
                                                        font_bold=False,
                                                        fg_color=self.COLOR_LIGHT_GREEN,
                                                        hover_color=self.COLOR_LIGHT_GREEN)
        self.lbl_recommneded_value.move(self.X_PADDING, y)

        y = self.lbl_recommneded_value.pos().y() + self.lbl_recommneded_value.height() + self.Y_SPACING

        # Default value label
        if self.item_data["default"] is None:
            text = self.getl("app_settings_no_default_value_text")
            lbl_default_fg_color = self.COLOR_RED
            lbl_default_hover_color = self.COLOR_DARK_RED
        else:
            text = self.getl("app_settings_lbl_default_value_text") + "\n" + self.item_data["default"]
            lbl_default_fg_color = self.COLOR_BLUE
            lbl_default_hover_color = self.COLOR_LIGHT_BLUE

        self.lbl_default_value = self._create_label(self,
                                                    text,
                                                    width=w,
                                                    center=True,
                                                    font_size=9,
                                                    font_bold=False,
                                                    fg_color=lbl_default_fg_color,
                                                    hover_color=lbl_default_hover_color)
        self.lbl_default_value.move(self.X_PADDING, y)
        self.lbl_default_value.setCursor(Qt.PointingHandCursor)

        if self.item_data["default"] is not None:
            self.lbl_default_value.mousePressEvent = self._on_default_value_clicked

        y = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + self.Y_PADDING

        self.setFixedSize(w + self.X_PADDING * 2, y)
        if self.expanded:
            self.expand()
        else:
            self.collapse()


class ItemStyle(AbstractFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, item_data: dict) -> None:
        super().__init__(parent_widget, settings)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._parent_widget = parent_widget
        self.item_data = item_data
        self.expanded = self.item_data.get("expanded", False)

        self._define_me()
        self.cancel_animation = not self.getv("app_setting_animate_item_resize")

        # Widget Handler
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(self, global_properties)
        self.widget_handler.add_child(self.btn_set_style, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_info, {"allow_bypass_mouse_press_event": False, "allow_bypass_enter_event": False, "allow_bypass_leave_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_default_value, {"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.activate()

    def _on_set_style_clicked(self):
        if self.item_data.get("validator_type") is not None:
            self.item_data["feedback_function"](self.item_data, action=self.item_data.get("validator_type"))
        else:
            self.item_data["feedback_function"](self.item_data, action="set_style")
    
    def _on_default_value_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_default_value).EVENT_mouse_press_event(e)
            self.item_data["feedback_function"](self.item_data, action="set_style_default")
    
    def _on_info_clicked(self, e: QMouseEvent):
        lbl_info_height = self.lbl_info.height()
        self.widget_handler.find_child(self.lbl_info).EVENT_mouse_press_event(e)
        if e.button() == Qt.LeftButton:
            if self.expanded:
                self.collapse(lbl_info_height=lbl_info_height)
            else:
                self.expand()
        elif e.button() == Qt.RightButton:
            self.info_label_context_menu(self.item_data, self._stt)

    def _on_info_hover_enter(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(1)
    
    def _on_info_hover_leave(self, e: QMouseEvent):
        self.lbl_info_opacity.setOpacity(0.5)

    def expand(self):
        h = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + 10

        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = True
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()
    
    def collapse(self, lbl_info_height: int = None):
        if lbl_info_height is None:
            lbl_info_height = self.lbl_info.height()
        h = max(self.btn_set_style.pos().y() + self.btn_set_style.height() + 10, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + 10, self.lbl_info.pos().y() + lbl_info_height + 10)

        self.animate_setting_resize(self, start_height=self.height(), end_height=h, resize_notify_function=self.item_data.get("resize_notify_function"))

        self.expanded = False
        if self.item_data.get("resize_notify_function") is not None:
            self.item_data["resize_notify_function"]()

    def _define_me(self):
        w = self.item_data["width"] - self.X_PADDING * 2

        # Main Frame
        self._define_frame(self)

        # Set Style Button
        if self.item_data.get("validator_type") == "def_hint_edit":
            self.btn_set_style = self._create_button(self, self.getl("app_settings_btn_set_edit_text"))
        else:
            self.btn_set_style = self._create_button(self, self.getl("app_settings_btn_set_style_text"))
        
        self.btn_set_style.move(self.X_PADDING, self.Y_PADDING)
        self.btn_set_style.clicked.connect(self._on_set_style_clicked)

        # Label Info
        self.lbl_info = self._create_info_label(self)
        self.lbl_info.move(w - 25, self.btn_set_style.pos().y())
        self.lbl_info.mousePressEvent = self._on_info_clicked
        self.lbl_info_opacity = QGraphicsOpacityEffect()
        self.lbl_info_opacity.setOpacity(0.5)
        self.lbl_info.setGraphicsEffect(self.lbl_info_opacity)
        self.lbl_info.enterEvent = self._on_info_hover_enter
        self.lbl_info.leaveEvent = self._on_info_hover_leave

        # Key Name Label
        self.lbl_key_name = self._create_label(self, 
                                               self.item_data["name"], 
                                               width=w - (self.btn_set_style.pos().x() + self.btn_set_style.width() + self.X_SPACING + self.lbl_info.width() + 5),
                                               center=True, 
                                               font_size=self.item_data.get("font_size", 14), 
                                               font_bold=True)
        self.lbl_key_name.move(self.btn_set_style.pos().x() + self.btn_set_style.width() + self.X_SPACING, self.Y_PADDING)
        self.lbl_key_name.mousePressEvent = self._on_info_clicked
        self.lbl_key_name.setCursor(Qt.PointingHandCursor)

        y = max(self.btn_set_style.pos().y() + self.btn_set_style.height() + self.Y_SPACING, self.lbl_key_name.pos().y() + self.lbl_key_name.height() + self.Y_PADDING)
        y = max(y, self.lbl_info.pos().y() + self.lbl_info.height() + self.Y_PADDING)

        # Description Label
        self.lbl_description = self._create_label(self, 
                                                 self.item_data["desc"], 
                                                 width=w, 
                                                 center=True, 
                                                 font_size=9, 
                                                 font_bold=False,
                                                 fg_color=self.COLOR_GREY,
                                                 hover_color=self.COLOR_GREY)
        self.lbl_description.move(self.X_PADDING, y)

        y = self.lbl_description.pos().y() + self.lbl_description.height() + self.Y_SPACING

        # Recommended Value Label
        self.lbl_recommneded_value = self._create_label(self,
                                                        self.item_data["recomm"],
                                                        width=w,
                                                        center=True,
                                                        font_size=9,
                                                        font_bold=False,
                                                        fg_color=self.COLOR_LIGHT_GREEN,
                                                        hover_color=self.COLOR_LIGHT_GREEN)
        self.lbl_recommneded_value.move(self.X_PADDING, y)

        y = self.lbl_recommneded_value.pos().y() + self.lbl_recommneded_value.height() + self.Y_SPACING

        # Default value label
        if self.item_data["default"] is None:
            text = self.getl("app_settings_no_default_value_text")
            lbl_default_fg_color = self.COLOR_RED
            lbl_default_hover_color = self.COLOR_DARK_RED
        else:
            text = self.getl("app_settings_lbl_default_value_text") + "\n" + self.item_data["default"]
            lbl_default_fg_color = self.COLOR_BLUE
            lbl_default_hover_color = self.COLOR_LIGHT_BLUE

        self.lbl_default_value = self._create_label(self,
                                                    text,
                                                    width=w,
                                                    center=True,
                                                    font_size=9,
                                                    font_bold=False,
                                                    fg_color=lbl_default_fg_color,
                                                    hover_color=lbl_default_hover_color)
        self.lbl_default_value.move(self.X_PADDING, y)
        self.lbl_default_value.setCursor(Qt.PointingHandCursor)

        if self.item_data["default"] is not None:
            self.lbl_default_value.mousePressEvent = self._on_default_value_clicked

        y = self.lbl_default_value.pos().y() + self.lbl_default_value.height() + self.Y_PADDING

        self.setFixedSize(w + self.X_PADDING * 2, y)
        if self.expanded:
            self.expand()
        else:
            self.collapse()


class ItemsGroup(QFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, item_data: dict) -> None:
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._parent_widget = parent_widget
        self.item_data = item_data
        self.expanded = self.item_data.get("expanded", False)
        self.widgets = []
        self.widget_data_buffer = []

        self._define_me()

        # Widget Handler
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(self, global_properties)
        self.widget_handler.add_ActionFrame(self.title_widget, {"allow_bypass_mouse_press_event": False})

    def add_item(self, info_data: dict):
        if not self.expanded:
            self.widget_data_buffer.append(info_data)
            return
        else:
            self._show_buffered_items()
            self._show_item(info_data)

    def _show_buffered_items(self):
        while self.widget_data_buffer:
            self._show_item(self.widget_data_buffer.pop(0))
            QCoreApplication.processEvents()

    def _show_item(self, info_data: dict):
        """
        ["name"]
        ["key"]

        ["desc"] = None
        ["recomm"] = None
        ["affected_keys"] = None

        ["input_box_width"] = None
        ["validator_type"] = None
        ["validator_data"] = None
        ["cmb_data"] = None
        """
        item_data = self.item_data["empty_dict_function"]()
        item_data["name"] = info_data["name"]
        item_data["main_win"] = info_data.get("main_win")

        if info_data["item_type"] != "title":
            if info_data.get("affected_keys") is None:
                info_data["affected_keys"] = []
                info_data["affected_keys"].append([info_data["key"], "nn"])

            item_data["key"] = info_data["key"]
            item_data["affected_keys"] = self.item_data["make_affected_keys_list_function"](info_data["affected_keys"])
            self.item_data["populate_item_value_default_desc_recomm_min_max_function"](item_data)
            if info_data.get("desc") is not None:
                item_data["desc"] = info_data["desc"]
            if info_data.get("recomm") is not None:
                item_data["recomm"] = info_data["recomm"]
            
            if info_data.get("input_box_width") is not None:
                item_data["input_box_width"] = info_data["input_box_width"]
            if info_data.get("validator_type") is not None:
                item_data["validator_type"] = info_data["validator_type"]
            if info_data.get("validator_data") is not None:
                item_data["validator_data"] = info_data["validator_data"]
            if info_data.get("cmb_data") is not None:
                item_data["cmb_data"] = info_data["cmb_data"]
            if info_data.get("font_size") is not None:
                item_data["font_size"] = info_data["font_size"]

            item_data["resize_notify_function"] = self.resize_notify_function
        else:
            item_data["title_center"] = info_data.get("title_center", False)
            item_data["font_size"] = info_data.get("font_size", 12)
            item_data["font_bold"] = info_data.get("font_bold", False)
            if info_data.get("fg_color") is not None:
                item_data["fg_color"] = info_data["fg_color"]
            if info_data.get("bg_color") is not None:
                item_data["bg_color"] = info_data["bg_color"]
            if info_data.get("hover_color") is not None:
                item_data["hover_color"] = info_data["hover_color"]

        if info_data["item_type"] == "title":
            item = ItemTitle(self._stt, self, item_data)
        elif info_data["item_type"] == "checkbox":
            item = ItemCheckBox(self._stt, self, item_data)
        elif info_data["item_type"] == "input":
            item = ItemInput(self._stt, self, item_data)
        elif info_data["item_type"] == "combobox":
            item = ItemComboBox(self._stt, self, item_data)
        elif info_data["item_type"] == "style":
            item = ItemStyle(self._stt, self, item_data)

        self.widgets.append(item)

        self.layout().addWidget(item)
        self.resize_me(expanded=self.expanded)

    def _on_title_doubleclicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            if self.item_data.get("main_win"):
                self.item_data["main_win"].setDisabled(True)
            if self.title_widget:
                self.widget_handler.find_child(self.title_widget).EVENT_mouse_press_event(e)

            if self.item_data.get("loading_function"):
                self.item_data["loading_function"](True)
                QCoreApplication.processEvents()

            self.expanded = not self.expanded
            self._show_buffered_items()
            self.resize_me(expanded=self.expanded)
            if self.item_data.get("loading_function"):
                self.item_data["loading_function"](False)
            if self.item_data.get("main_win"):
                self.item_data["main_win"].setDisabled(False)

    def resize_notify_function(self):
        self.resize_me(self.expanded)

    def animate_setting_resize(self, widget: QWidget, start_height: int, end_height: int, duration: int = None, steps: int = None, resize_notify_function = None):
        if duration is None:
            duration = self.getv("app_setting_item_animation_duration")
        if steps is None:
            steps = self.getv("app_setting_item_animation_steps")

        widget.setFixedHeight(start_height)
        step_val = int((end_height - start_height) / steps)

        for i in range(steps):
            if step_val > 0:
                widget.setFixedHeight(start_height + (i * step_val))
            else:
                widget.setFixedHeight(start_height - (i * abs(step_val)))
            
            if resize_notify_function:
                resize_notify_function()

            QCoreApplication.processEvents()
            time.sleep((duration / steps) / 1000)
            QCoreApplication.processEvents()
        
        widget.setFixedHeight(end_height)

    def resize_me(self, expanded: bool = False):
        try:
            if expanded:
                h = sum([item.height() for item in self.widgets]) + self.title_widget.height()
            else:
                h = self.title_widget.height()
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("#1.#2 failed to complete resize.\nException:\n#3", ["AppSettings", "ItemsGroup", str(e)])
            return

        # self.animate_setting_resize(self, start_height=self.height(), end_height=h)

        h = 0
        if expanded:
            for item in self.widgets:
                item.setVisible(True)
                h += item.height()
        else:
            for item in self.widgets:
                item.setVisible(False)
        
        h += self.title_widget.height()

        self.setFixedHeight(h)

    def _define_me(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.group_layout = QVBoxLayout()
        self.group_layout.setSpacing(0)
        self.group_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.group_layout)

        data = {
            "name": self.item_data["name"],
            "expanded": self.expanded,
            "spacing_height": 10,
            "width": self.item_data.get("width", 300),
            "bg_color": self.item_data.get("bg_color") if self.item_data.get("bg_color") else "#000054",
            "fg_color": self.item_data.get("fg_color") if self.item_data.get("fg_color") else "#ffff00",
            "hover_color": self.item_data.get("hover_color") if self.item_data.get("hover_color") else "#55ffff",
            "no_mouse_interaction": True,
            "font_size": 14,
            "font_bold": True
        }
        self.title_widget = ItemTitle(self._stt, self, data)
        self.group_layout.addWidget(self.title_widget)
        
        self.title_widget.show()

        self.title_widget.mousePressEvent = self._on_title_doubleclicked

        self.setFixedWidth(self.item_data["width"])
        self.resize_me(self.expanded)

    def close_me(self):
        for widget in self.widgets:
            widget.close_me()
        self.deleteLater()


class ItemsGroupManager:
    """
    How to add a menu item :
     - add an item to the group. FUNCTION: show_general_settings -> Menu
        You need to define name for title, in menu settings, just change setting key
     - add and item to FUNCTION: list _menu_item_list

     Everything else is already done, item is automatically added to widgets list with all other menu items


     When adding some other settings make sure that:
      - add setting to apropriate section
      - add widgets like confirm button or cancel, dialog name, title ... to widgets list if they need to be shown in all widgets section
        section all widgets is already setup, no need to change anything
    """
    ITEM_FONT_SIZE = 12

    def __init__(self, settings: settings_cls.Settings, area_settings_widget: QWidget, data: dict):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.area_settings_widget = area_settings_widget
        self.data = data
        self.archive = {}
        self.search_items = {}
        self.item_group_empty_dictionary = self.data["item_group_empty_dictionary"]
        self._text_filter = text_filter_cls.TextFilter(ignore_serbian_characters=True)

        self.populate_archive()

    def show_general_settings(self, filter: dict = None, populate_archive: bool = False):
        section = self.getl("app_settings_lbl_menu_general_title_text")

        # General Title
        item_to_add = [
            self._title("app_sett_style_date_time_name", title_center=True),
            self._input("date_format_name", "date_format", input_box_width=130),
            self._input("time_format_name", "time_format", input_box_width=130),
            
            self._title("app_sett_style_log_name", title_center=True),
            self._input("number_of_saved_logs_name", "number_of_saved_logs"),
            self._checkbox("app_sett_style_pop_log_dialog_on_exception_style", "pop_log_dialog_on_exception", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_pop_log_dialog_on_warning_style", "pop_log_dialog_on_warning", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_keep_log_window_on_top_style", "keep_log_window_on_top", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_frameless_log_window_style", "frameless_log_window"),
            self._title("app_sett_style_log_messages_name", title_center=True),
            self._title("app_sett_style_log_messages_to_save_name"),
            self._checkbox("app_sett_style_record_normal_logs_style", "record_normal_logs", recomm_getl="widget_setting_false_recomm"),
            self._checkbox("app_sett_style_record_warning_logs_style", "record_warning_logs", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_record_exception_logs_style", "record_exception_logs", recomm_getl="widget_setting_true_recomm"),
            self._title("app_sett_style_log_messages_structure_name"),
            self._checkbox("app_sett_style_log_save_locals_style", "log_save_locals", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_log_save_globals_style", "log_save_globals", recomm_getl="widget_setting_false_recomm"),
            self._checkbox("app_sett_style_log_save_builtins_style", "log_save_builtins", recomm_getl="widget_setting_false_recomm"),
            self._checkbox("app_sett_style_log_save_module_code_style", "log_save_module_code", recomm_getl="widget_setting_false_recomm"),
            self._checkbox("app_sett_style_log_save_function_code_style", "log_save_function_code", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_sound_name", title_center=True),
            self._title("app_sett_style_statusbar_sound_frame_name"),
            self._checkbox("app_sett_style_frm_stb_volume_enabled_style", "frm_stb_volume_enabled"),
            self._checkbox("app_sett_style_frm_stb_volume_visible_style", "frm_stb_volume_visible"),
            self._input("app_sett_style_frm_stb_volume_fixed_width_style", "frm_stb_volume_fixed_width", input_box_width=60),
            self._checkbox("app_sett_style_allow_volume_muted_sound_style", "allow_volume_muted_sound"),
            self._combobox("app_sett_style_set_muted_sound_file_path_style", "set_muted_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._checkbox("app_sett_style_allow_volume_unmuted_sound_style", "allow_volume_unmuted_sound"),
            self._combobox("app_sett_style_set_unmuted_sound_file_path_style", "set_unmuted_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._title("app_sett_style_frm_stb_volume_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "frm_stb_volume_stylesheet", affected_keys=self._standard_affected_keys("frm_stb_volume_stylesheet", "qframe")),
            self._title("app_sett_style_btn_volume_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "btn_volume_stylesheet", affected_keys=self._standard_affected_keys("btn_volume_stylesheet", "qpushbutton")),
            self._title("app_sett_style_sld_volume_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "sld_volume_stylesheet", affected_keys=self._standard_affected_keys("sld_volume_stylesheet", "qslider")),
            self._title("app_sett_style_lbl_volume_value_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "lbl_volume_value_stylesheet", affected_keys=self._standard_affected_keys("lbl_volume_value_stylesheet", "qlabel")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_settings_app_group_title")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # StartUp
        item_to_add = [
            self._title("app_sett_style_at_start_name", title_center=True),
            self._checkbox("app_sett_style_add_block_at_start_style", "add_block_at_start"),
            self._checkbox("app_sett_style_auto_show_drafts_on_start_style", "auto_show_drafts_on_start", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_show_draft_blocks_collapsed_on_start_style", "show_draft_blocks_collapsed_on_start"),
            self._checkbox("app_sett_style_animate_adding_empty_blocks_at_start_style", "animate_adding_empty_blocks_at_start", affected_keys=[["mnu_unfinished_show_block_animation", "nn"], ["animate_adding_empty_blocks_at_start", "nn"]]),
            self._checkbox("app_sett_style_show_welcome_notification_style", "show_welcome_notification", recomm_getl="show_welcome_notification_desc"),
            self._checkbox("app_sett_style_fun_fact_show_on_start_style", "fun_fact_show_on_start"),

            self._title("app_sett_style_at_exit_name", title_center=True),
            self._checkbox("app_sett_style_show_closing_notification_style", "show_closing_notification"),

            self._title("app_sett_style_mainwin_title_animation_name", title_center=True),
            self._checkbox("app_sett_style_main_win_title_animate_style", "main_win_title_animate", desc_getl="main_win_title_animate_desc"),
            self._input("app_sett_style_main_win_title_animate_spaces_style", "main_win_title_animate_spaces", desc_getl="main_win_title_animate_spaces_desc", recomm_getl="main_win_title_animate_spaces_recomm"),
            self._input("app_sett_style_main_win_title_animate_step_duration_style", "main_win_title_animate_step_duration", desc_getl="main_win_title_animate_step_duration_desc", recomm_getl="main_win_title_animate_step_duration_recomm")
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_at_start_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Main menu
        item_to_add = [
            self._title("app_sett_style_menubar_general_name", title_center=True, font_size=18),

            self._title("app_sett_style_main_menu_general_name"),
            self._style("app_sett_style_widget_stylesheet_style", "menubar_stylesheet", affected_keys=self._standard_affected_keys("menubar_stylesheet", "qmenubar")),
            self._checkbox("app_sett_style_menubar_enabled_style", "menubar_enabled"),
            self._checkbox("app_sett_style_menubar_visible_style", "menubar_visible"),

            self._title("app_sett_style_main_menu_sound_name"),
            self._checkbox("app_sett_style_main_menu_sound_enabled_style", "main_menu_sound_enabled", desc_getl="main_menu_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "main_menu_sound_file_path", cmb_data="sound", input_box_width=-1),
            self._checkbox("app_sett_style_menu_item_sound_enabled_style", "menu_item_sound_enabled", desc_getl="main_menu_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "menu_item_sound_file_path", cmb_data="sound", input_box_width=-1),

            self._title("app_sett_style_main_menu_name", title_center=True, font_size=18),

            self._title("app_sett_style_main_menu_file_name"),
            self._style("app_sett_style_main_menu_stylesheet_style", "menu_file_stylesheet", affected_keys=self._standard_affected_keys("menu_file_stylesheet", "qmenu")),
            self._combobox("app_sett_style_menu_icon_path_style", "menu_file_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_tooltip_visible_style", "menu_file_tooltip_visible", desc_getl="app_sett_style_menu_tooltip_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_enabled_style", "menu_file_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "menu_file_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_main_menu_edit_name"),
            self._style("app_sett_style_main_menu_stylesheet_style", "menu_edit_stylesheet", affected_keys=self._standard_affected_keys("menu_edit_stylesheet", "qmenu")),
            self._combobox("app_sett_style_menu_icon_path_style", "menu_edit_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_tooltip_visible_style", "menu_edit_tooltip_visible", desc_getl="app_sett_style_menu_tooltip_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_enabled_style", "menu_edit_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "menu_edit_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_main_menu_view_name"),
            self._style("app_sett_style_main_menu_stylesheet_style", "menu_view_stylesheet", affected_keys=self._standard_affected_keys("menu_view_stylesheet", "qmenu")),
            self._combobox("app_sett_style_menu_icon_path_style", "menu_view_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_tooltip_visible_style", "menu_view_tooltip_visible", desc_getl="app_sett_style_menu_tooltip_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_enabled_style", "menu_view_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "menu_view_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_main_menu_user_name"),
            self._style("app_sett_style_main_menu_stylesheet_style", "menu_user_stylesheet", affected_keys=self._standard_affected_keys("menu_user_stylesheet", "qmenu")),
            self._combobox("app_sett_style_menu_icon_path_style", "menu_user_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_tooltip_visible_style", "menu_user_tooltip_visible", desc_getl="app_sett_style_menu_tooltip_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_enabled_style", "menu_user_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "menu_user_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_main_menu_help_name"),
            self._style("app_sett_style_main_menu_stylesheet_style", "menu_help_stylesheet", affected_keys=self._standard_affected_keys("menu_help_stylesheet", "qmenu")),
            self._combobox("app_sett_style_menu_icon_path_style", "menu_help_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_tooltip_visible_style", "menu_help_tooltip_visible", desc_getl="app_sett_style_menu_tooltip_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_enabled_style", "menu_help_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "menu_help_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_items_name", title_center=True, font_size=18),

            self._title("app_sett_style_menu_items_file_name", title_center=True, font_size=14),

            self._title("app_sett_style_menu_file_app_settings_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_file_app_settings_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_file_app_settings_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_file_app_settings_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_file_app_settings_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_file_app_settings_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_file_app_settings_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_file_mnu_import_blocks_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_import_blocks_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_import_blocks_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_import_blocks_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_import_blocks_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_import_blocks_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_import_blocks_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_file_mnu_export_blocks_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_export_blocks_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_export_blocks_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_export_blocks_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_export_blocks_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_export_blocks_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_export_blocks_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_file_mnu_import_def_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_import_def_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_import_def_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_import_def_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_import_def_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_import_def_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_import_def_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_file_mnu_export_def_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_export_def_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_export_def_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_export_def_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_export_def_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_export_def_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_export_def_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_file_mnu_open_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_open_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_open_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_open_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_open_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_open_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_open_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_file_mnu_file_save_active_block_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_file_save_active_block_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_file_save_active_block_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_file_save_active_block_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_file_save_active_block_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_file_save_active_block_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_file_save_active_block_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_items_edit_name", title_center=True, font_size=14),

            self._title("app_sett_style_menu_edit_mnu_add_block_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_add_block_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_add_block_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_add_block_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_add_block_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_add_block_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_add_block_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_edit_mnu_expand_all_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_expand_all_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_expand_all_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_expand_all_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_expand_all_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_expand_all_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_expand_all_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_edit_mnu_collapse_all_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_collapse_all_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_collapse_all_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_collapse_all_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_collapse_all_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_collapse_all_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_collapse_all_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_edit_mnu_unfinished_show_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_unfinished_show_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_unfinished_show_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_unfinished_show_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_unfinished_show_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_unfinished_show_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_unfinished_show_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_edit_mnu_edit_tags_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_edit_tags_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_edit_tags_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_edit_tags_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_edit_tags_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_edit_tags_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_edit_tags_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_edit_mnu_edit_definitions_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_edit_definitions_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_edit_definitions_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_edit_definitions_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_edit_definitions_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_edit_definitions_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_edit_definitions_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_edit_mnu_translation_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_translation_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_translation_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_translation_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_translation_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_translation_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_translation_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_items_view_name", title_center=True, font_size=14),

            self._title("app_sett_style_menu_view_mnu_diary_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_diary_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_diary_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_diary_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_diary_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_diary_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_diary_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_blocks_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_blocks_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_blocks_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_blocks_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_blocks_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_blocks_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_blocks_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_tags_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_tags_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_tags_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_tags_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_tags_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_tags_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_tags_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_definitions_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_definitions_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_definitions_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_definitions_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_definitions_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_definitions_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_definitions_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_images_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_images_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_images_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_images_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_images_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_images_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_images_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_fun_fact_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_fun_fact_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_fun_fact_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_fun_fact_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_fun_fact_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_fun_fact_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_fun_fact_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_clipboard_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_clipboard_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_clipboard_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_clipboard_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_clipboard_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_clipboard_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_clipboard_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_media_explorer_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_media_explorer_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_media_explorer_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_media_explorer_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_media_explorer_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_media_explorer_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_media_explorer_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_dicts_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_dicts_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_dicts_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_dicts_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_dicts_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_dicts_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_dicts_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_wiki_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_wiki_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_wiki_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_wiki_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_wiki_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_wiki_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_wiki_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_online_content_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_online_content_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_online_content_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_online_content_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_online_content_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_online_content_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_online_content_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_view_mnu_view_find_in_app_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_view_find_in_app_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_view_find_in_app_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_view_find_in_app_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_view_find_in_app_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_view_find_in_app_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_view_find_in_app_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_help_mnu_help_log_messages_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_help_log_messages_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_help_log_messages_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_help_log_messages_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_help_log_messages_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_help_log_messages_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_help_log_messages_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_help_mnu_help_statistic_name"),
            self._checkbox("app_sett_style_menu_enabled_style", "mnu_help_statistic_enabled", desc_getl="app_sett_style_menu_enabled_desc", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "mnu_help_statistic_visible", desc_getl="app_sett_style_menu_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_menu_icon_path_style", "mnu_help_statistic_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_menu_icon_visible_style", "mnu_help_statistic_icon_visible", desc_getl="app_sett_style_menu_icon_visible_desc", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_menu_shortcut_style", "mnu_help_statistic_shortcut", validator_type="shortcut", desc_getl="app_sett_shortcut_desc"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "mnu_help_statistic_shortcut_visible_in_menu", desc_getl="app_sett_style_menu_shortcut_visible_desc", recomm_getl="widget_setting_true_recomm"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_menu_main_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Context menu
        item_to_add = [
            self._title("app_sett_style_context_menu_general_name"),
            self._checkbox("app_sett_style_context_menu_item_marked_prefix_enabled_style", "context_menu_item_marked_prefix_enabled"),
            self._input("app_sett_style_context_menu_item_marked_prefix_style", "context_menu_item_marked_prefix"),
            self._combobox("app_sett_style_context_menu_item_marked_icon_path_style", "context_menu_item_marked_icon_path", cmb_data="icon", input_box_width=-1, desc_getl="context_menu_item_marked_icon_path_desc"),

            self._title("app_sett_style_context_menu_frame_name"),
            self._checkbox("app_sett_style_show_titlebar_style", "context_menu_win_show_titlebar", desc_getl="app_sett_style_win_show_titlebar_desc", recomm_getl="widget_setting_false_recomm"),
            self._style("app_sett_style_frame_stylesheet_style", "context_menu_win_stylesheet", affected_keys=self._standard_affected_keys("context_menu_win_stylesheet", "qdialog")),
            self._input("app_sett_style_context_menu_win_layout_spacing_style", "context_menu_win_layout_spacing"),
            self._input("app_sett_style_context_menu_win_width_style", "context_menu_win_width", recomm_getl="context_menu_win_layout_spacing_recomm"),
            self._input("app_sett_style_context_menu_win_height_style", "context_menu_win_height", recomm_getl="context_menu_win_layout_spacing_recomm"),

            self._title("app_sett_style_context_menu_item_name"),
            self._checkbox("app_sett_style_button_flat_style", "context_menu_button_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "context_menu_button_stylesheet", affected_keys=self._standard_affected_keys("context_menu_button_stylesheet", "qpushbutton")),

            self._title("app_sett_style_context_menu_separator_name"),
            self._input("app_sett_style_context_menu_separator_size_style", "context_menu_separator_size"),
            self._style("app_sett_style_button_stylesheet_style", "context_menu_separator_stylesheet", affected_keys=self._standard_affected_keys("context_menu_separator_stylesheet", "qframe")),

            self._title("app_sett_style_context_menu_icons_name"),
            self._combobox("app_sett_style_context_menu_item_write_line_icon_path_style", "context_menu_item_write_line_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_context_menu_item_calendar_icon_path_style", "context_menu_item_calendar_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_context_menu_item_cm_single_choice_icon_path_style", "context_menu_item_cm_single_choice_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_margins_name"),
            self._input("app_sett_style_widget_margins_style", "context_menu_win_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "context_menu_win_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "context_menu_win_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_context_menu_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Notification settings
        item_to_add = [
            self._title("app_sett_style_notification_frame_name"),
            self._style("app_settings_grp_style_gen_title", "notification_win_stylesheet", affected_keys="qdialog"),
            self._input("app_sett_style_notification_title_text_spacer_style", "notification_title_text_spacer"),
            self._input("app_sett_style_notification_text_button_spacer_style", "notification_text_button_spacer"),
            self._input("app_sett_style_notification_icon_text_spacer_style", "notification_icon_text_spacer"),
            self._checkbox("app_sett_style_notification_start_sound_enabled_style", "notification_start_sound_enabled"),
            self._combobox("app_sett_style_notification_start_sound_style", "notification_start_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),

            self._title("app_sett_style_notification_lbl_icon_name"),
            self._combobox("app_sett_style_notification_icon_path_style", "notification_icon_path", cmb_data="icon", input_box_width=-1, affected_keys=[["notification_lbl_icon_icon_path", "qlabel"], ["notification_icon_path", "qlabel"]]),
            self._combobox("app_sett_style_notification_block_remove_diary_icon_path_style", "notification_block_remove_diary_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_frame_shape_style", "notification_lbl_icon_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "notification_lbl_icon_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "notification_lbl_icon_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "notification_lbl_icon_stylesheet", affected_keys=self._standard_affected_keys("notification_lbl_icon_stylesheet", "qlabel")),

            self._title("app_sett_style_notification_open_animation_name"),
            self._checkbox("app_sett_style_notification_open_animation_style", "notification_open_animation"),
            self._input("app_sett_style_block_animation_on_open_steps_number_style", "notification_open_animation_steps_number", desc_getl="block_animation_steps_number_desc", recomm_getl="block_animation_on_close_steps_number_recomm"),
            self._input("app_sett_style_block_animation_on_collapse_total_duration_ms_style", "notification_open_animation_total_duration_ms", desc_getl="block_animation_duration_desc", recomm_getl="block_animation_on_close_total_duration_ms_recomm"),

            self._title("app_sett_style_notification_lbl_title_name"),
            self._combobox("app_sett_style_frame_shape_style", "notification_lbl_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "notification_lbl_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "notification_lbl_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "notification_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("notification_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_notification_lbl_text_name"),
            self._combobox("app_sett_style_frame_shape_style", "notification_lbl_text_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "notification_lbl_text_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "notification_lbl_text_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "notification_lbl_text_stylesheet", affected_keys=self._standard_affected_keys("notification_lbl_text_stylesheet", "qlabel")),

            self._title("app_sett_style_notification_btn_ok_name"),
            self._checkbox("app_sett_style_button_flat_style", "notification_btn_ok_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "notification_btn_ok_stylesheet", affected_keys=self._standard_affected_keys("notification_btn_ok_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "notification_btn_ok_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "notification_btn_ok_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_notification_btn_close_name"),
            self._checkbox("app_sett_style_button_flat_style", "notification_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "notification_btn_close_stylesheet", affected_keys=self._standard_affected_keys("notification_btn_close_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "notification_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "notification_btn_close_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_margins_name"),
            self._input("app_sett_style_widget_margins_style", "notification_win_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_notification_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # InputBox OneLine and MultiLine
        item_to_add = [
            self._title("app_sett_style_dialog_general_name"),
            self._style("app_sett_style_dialog_stylesheet_style", "block_input_box_name_win_stylesheet", affected_keys=self._standard_affected_keys("block_input_box_name_win_stylesheet", "qdialog")),
            self._checkbox("app_sett_style_show_titlebar_style", "block_input_box_name_win_show_titlebar", desc_getl="app_sett_style_win_show_titlebar_desc", recomm_getl="widget_setting_false_recomm"),
            self._input("app_sett_style_block_input_box_name_win_layout_spacing_style", "block_input_box_name_win_layout_spacing", desc_getl="block_input_box_name_win_layout_spacing_desc", recomm_getl="context_menu_win_layout_spacing_recomm"),

            self._title("app_sett_style_inputbox_title_name"),
            self._combobox("app_sett_style_frame_shape_style", "block_input_box_name_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "block_input_box_name_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "block_input_box_name_title_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "block_input_box_name_title_stylesheet", affected_keys=self._standard_affected_keys("block_input_box_name_title_stylesheet", "qlabel")),

            self._title("app_sett_style_inputbox_input_field_name"),
            self._combobox("app_sett_style_frame_shape_style", "block_input_box_name_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "block_input_box_name_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "block_input_box_name_line_width"),
            self._combobox("app_sett_style_body_txt_box_line_wrap_mode_style", "block_input_box_name_line_wrap_mode", cmb_data="line_wrap_mode", desc_getl="body_txt_box_line_wrap_mode_desc", recomm_getl="body_txt_box_line_wrap_mode_recomm"),
            self._checkbox("app_sett_style_body_txt_box_accept_rich_text_style", "block_input_box_name_accept_rich_text", desc_getl="body_txt_box_accept_rich_text_desc"),
            self._input("app_sett_style_body_txt_box_cursor_width_style", "block_input_box_name_cursor_width", desc_getl="body_txt_box_cursor_width_desc", recomm_getl="body_txt_box_cursor_width_recomm"),
            self._style("app_sett_style_block_input_box_name_one_line_stylesheet_style", "block_input_box_name_one_line_stylesheet", affected_keys=self._standard_affected_keys("block_input_box_name_one_line_stylesheet", "qlineedit")),
            self._style("app_sett_style_input_box_txt_box_invalid_entry_one_line_stylesheet_style", "input_box_txt_box_invalid_entry_one_line_stylesheet", affected_keys=self._standard_affected_keys("input_box_txt_box_invalid_entry_one_line_stylesheet", "qlineedit")),
            self._style("app_sett_style_block_input_box_name_stylesheet_style", "block_input_box_name_stylesheet", affected_keys=self._standard_affected_keys("block_input_box_name_stylesheet", "qtextedit")),
            self._style("app_sett_style_input_box_txt_box_invalid_entry_stylesheet_style", "input_box_txt_box_invalid_entry_stylesheet", affected_keys=self._standard_affected_keys("input_box_txt_box_invalid_entry_stylesheet", "qtextedit")),

            self._title("app_sett_style_inputbox_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "block_input_box_name_description_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "block_input_box_name_description_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "block_input_box_name_title_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "block_input_box_name_description_stylesheet", affected_keys=self._standard_affected_keys("block_input_box_name_description_stylesheet", "qlabel")),

            self._title("app_sett_style_inputbox_resize_button_name"),
            self._checkbox("app_sett_style_button_flat_style", "input_box_btn_resize_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "input_box_btn_resize_stylesheet", affected_keys=self._standard_affected_keys("input_box_btn_resize_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_inputbox_resize_button_oneline_style", "input_box_btn_resize_one_line_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_inputbox_resize_button_multiline_style", "input_box_btn_resize_multi_line_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_input_box_btn_ok_name"),
            self._checkbox("app_sett_style_button_flat_style", "input_box_btn_ok_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "input_box_btn_ok_stylesheet", affected_keys=self._standard_affected_keys("input_box_btn_ok_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "input_box_btn_ok_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "input_box_btn_ok_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_margins_name"),
            self._input("app_sett_style_widget_margins_style", "block_input_box_name_win_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "block_input_box_name_win_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "block_input_box_name_win_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_inputbox_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Calendar dialog settings
        item_to_add = [
            self._title("app_sett_style_calendar_general_name"),
            self._combobox("app_sett_style_first_day_of_week_style", "first_day_of_week", cmb_data="day_of_week", desc_getl="first_day_of_week_desc", recomm_getl="first_day_of_week_recomm"),
            self._checkbox("app_sett_style_calendar_cal_widget_grid_visible_style", "calendar_cal_widget_grid_visible", desc_getl="calendar_cal_widget_grid_visible_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "calendar_cal_widget_stylesheet", affected_keys=self._standard_affected_keys("calendar_cal_widget_stylesheet", "qcalendarwidget")),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "calendar_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_calendar_btn_select_name"),
            self._checkbox("app_sett_style_button_flat_style", "calendar_btn_select_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "calendar_btn_select_stylesheet", affected_keys=self._standard_affected_keys("calendar_btn_select_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "calendar_btn_select_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "calendar_btn_select_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_calendar_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "calendar_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "calendar_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("calendar_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "calendar_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "calendar_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_calendar_lbl_info_name"),
            self._combobox("app_sett_style_frame_shape_style", "calendar_lbl_info_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "calendar_lbl_info_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "calendar_lbl_info_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "calendar_lbl_info_stylesheet", affected_keys=self._standard_affected_keys("calendar_lbl_info_stylesheet", "qlabel"))
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_calendar_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # MessageBox Information
        item_to_add = [
            self._title("app_sett_style_messagebox_information_general_name"),
            self._style("app_sett_style_widget_stylesheet_style", "msg_info_win_stylesheet", affected_keys=self._standard_affected_keys("msg_info_win_stylesheet", "qdialog")),
            self._combobox("app_sett_style_messagebox_information_icon_path_style", "messagebox_information_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_msg_box_wrong_entry_icon_path_style", "msg_box_wrong_entry_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_messagebox_question_icon_path_style", "messagebox_question_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_block_footer_btn_delete_msg_icon_path_style", "block_footer_btn_delete_msg_icon_path", cmb_data="icon", input_box_width=-1),
            self._input("app_sett_style_msg_box_icon_width_style", "msg_box_icon_width", desc_getl="msg_box_icon_width_desc", recomm_getl="msg_box_icon_width_recomm"),
            self._input("app_sett_style_msg_box_icon_height_style", "msg_box_icon_height", desc_getl="msg_box_icon_height_desc", recomm_getl="msg_box_icon_width_recomm"),
            self._input("app_sett_style_block_input_box_name_win_layout_spacing_style", "msg_info_win_layout_spacing", desc_getl="block_input_box_name_win_layout_spacing_desc"),

            self._title("app_sett_style_msg_box_title_name"),
            self._combobox("app_sett_style_frame_shape_style", "msg_box_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "msg_box_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "msg_box_title_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "msg_box_title_stylesheet", affected_keys=self._standard_affected_keys("msg_box_title_stylesheet", "qlabel")),

            self._title("app_sett_style_msg_box_text_name"),
            self._combobox("app_sett_style_frame_shape_style", "msg_box_text_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "msg_box_text_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "msg_box_text_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "msg_box_text_stylesheet", affected_keys=self._standard_affected_keys("msg_box_text_stylesheet", "qlabel")),

            self._title("app_sett_style_msg_box_icon_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "msg_box_icon_stylesheet", affected_keys=self._standard_affected_keys("msg_box_icon_stylesheet", "qlabel")),

            self._title("app_sett_style_msg_box_btn_ok_name"),
            self._checkbox("app_sett_style_button_flat_style", "msg_box_btn_ok_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "msg_box_btn_ok_stylesheet", affected_keys=self._standard_affected_keys("msg_box_btn_ok_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "msg_box_btn_ok_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "msg_box_btn_ok_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_margins_name"),
            self._input("app_sett_style_widget_margins_style", "msg_info_win_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "msg_info_win_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "msg_info_win_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_messagebox_information_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Autocomplete
        item_to_add = [
            self._title("app_sett_style_autocomplete_general_name"),
            self._checkbox("app_sett_style_show_autocomplete_style", "show_autocomplete", desc_getl="show_autocomplete_desc"),
            self._input("app_sett_style_autocomplete_items_number_style", "autocomplete_items_number"),
            self._input("app_sett_style_autocomplete_button_width_pad_style", "autocomplete_button_width_pad"),
            self._input("app_sett_style_autocomplete_button_height_pad_style", "autocomplete_button_height_pad"),
            self._input("app_sett_style_autocomplete_items_in_memory_style", "autocomplete_items_in_memory"),
            self._input("app_sett_style_autocomplete_minimum_word_lenght_style", "autocomplete_minimum_word_lenght"),
            self._input("app_sett_style_autocomplete_max_number_of_suggested_words_style", "autocomplete_max_number_of_suggested_words"),

            self._title("app_sett_style_autocomplete_frame_name"),
            self._combobox("app_sett_style_frame_shape_style", "autocomplete_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "autocomplete_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "autocomplete_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "autocomplete_stylesheet", affected_keys=self._standard_affected_keys("autocomplete_stylesheet", "qframe")),

            self._title("app_sett_style_autocomplete_item_name"),
            self._checkbox("app_sett_style_button_flat_style", "autocomplete_btn_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "autocomplete_btn_stylesheet", affected_keys=self._standard_affected_keys("autocomplete_btn_stylesheet", "qpushbutton")),

            self._title("app_sett_style_autocomplete_selected_item_name"),
            self._style("app_sett_style_button_stylesheet_style", "autocomplete_selected_btn_stylesheet", affected_keys=self._standard_affected_keys("autocomplete_selected_btn_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_autocomplete_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Definition general settings
        item_to_add = [
            self._title("app_sett_style_definition_general_name"),
            self._input("app_sett_style_definition_minimum_word_lenght_style", "definition_minimum_word_lenght"),
            self._input("app_sett_style_definition_maximum_word_lenght_style", "definition_maximum_word_lenght"),
            self._input("app_sett_style_max_number_of_images_in_definition_style", "max_number_of_images_in_definition"),
            self._checkbox("app_sett_style_definition_show_on_mouse_hover_style", "definition_show_on_mouse_hover"),
            self._checkbox("app_sett_style_definition_text_mark_enabled_style", "definition_text_mark_enabled"),
            self._input("app_sett_style_definition_text_mark_color_style", "definition_text_mark_color", validator_type="color"),
            self._input("app_sett_style_definition_text_mark_background_style", "definition_text_mark_background", validator_type="color"),
            self._checkbox("app_sett_style_definition_text_mark_enabled_in_def_add_dialog_style", "definition_text_mark_enabled_in_def_add_dialog"),
            self._combobox("app_sett_style_notification_pop_up_sound_style", "notification_pop_up_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            
            self._title("app_sett_style_definition_in_block_name"),
            self._combobox("app_sett_style_frame_shape_style", "definition_view_simple_frame_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "definition_view_simple_frame_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "definition_view_simple_frame_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_view_simple_frame_stylesheet", affected_keys=self._standard_affected_keys("definition_view_simple_frame_stylesheet", "qframe")),
            self._style("app_sett_style_definition_view_simple_title_stylesheet_style", "definition_view_simple_title_stylesheet", affected_keys=self._standard_affected_keys("definition_view_simple_title_stylesheet", "qlabel")),
            self._style("app_sett_style_definition_view_simple_desc_stylesheet_style", "definition_view_simple_desc_stylesheet", affected_keys=self._standard_affected_keys("definition_view_simple_desc_stylesheet", "qlabel")),
            self._input("app_sett_style_definition_view_simple_width_style", "definition_view_simple_width"),
            self._input("app_sett_style_definition_view_simple_height_style", "definition_view_simple_height"),
            self._input("app_sett_style_definition_view_simple_delay_style", "definition_view_simple_delay"),
            self._combobox("app_sett_style_definition_view_simple_btn_resize_icon_path_style", "definition_view_simple_btn_resize_icon_path", cmb_data="icon", input_box_width=-1),
            self._style("app_sett_style_definition_view_simple_btn_resize_stylesheet_style", "definition_view_simple_btn_resize_stylesheet", affected_keys=self._standard_affected_keys("definition_view_simple_btn_resize_stylesheet", "qpushbutton")),
            self._style("app_sett_style_definition_view_simple_btn_close_stylesheet_style", "definition_view_simple_btn_close_stylesheet", affected_keys=self._standard_affected_keys("definition_view_simple_btn_close_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_definition_view_simple_btn_close_icon_path_style", "definition_view_simple_btn_close_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_extra_images_name", title_center=True, font_size=17),
            self._checkbox("app_sett_style_show_definition_extra_image_style", "show_definition_extra_image"),
            self._checkbox("app_sett_style_def_extra_image_show_next_after_hide_style", "def_extra_image_show_next_after_hide"),
            self._input("app_sett_style_def_extra_image_start_delay", "def_extra_image_start_delay"),
            self._input("app_sett_style_def_extra_image_max_number_of_images_style", "def_extra_image_max_number_of_images"),
            self._input("app_sett_style_def_extra_image_auto_hide_style", "def_extra_image_auto_hide"),
            self._input("app_sett_style_def_extra_image_auto_hide_fade_out_duration_style", "def_extra_image_auto_hide_fade_out_duration"),
            self._combobox("app_sett_style_def_extra_image_animate_style_style", "def_extra_image_animate_style", cmb_data="extra_image_animate_style", input_box_width=200),
            self._input("app_sett_style_def_extra_image_animate_show_style", "def_extra_image_animate_show"),
            self._input("app_sett_style_def_extra_image_min_visible_width_style", "def_extra_image_min_visible_width"),
            self._input("app_sett_style_def_extra_image_min_visible_height_style", "def_extra_image_min_visible_height"),
            self._input("app_sett_style_def_extra_image_total_display_period_style", "def_extra_image_total_display_period"),
            self._combobox("app_sett_style_def_extra_image_source_style", "def_extra_image_source", cmb_data="extra_image_src", input_box_width=160),
            self._input("app_sett_style_def_extra_image_custom_source_folder_path_style", "def_extra_image_custom_source_folder_path", validator_type="file"),
            self._checkbox("app_sett_style_def_extra_image_custom_source_add_subfolders_style", "def_extra_image_custom_source_add_subfolders"),
            self._combobox("app_sett_style_def_extra_image_layout_style", "def_extra_image_layout", cmb_data="extra_image_layout", input_box_width=200),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_definition_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Various icons
        item_to_add = [
            self._combobox("app_sett_style_check_all_icon_path_style", "check_all_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_check_none_icon_path_style", "check_none_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_find_def_on_internet_icon_path_style", "find_def_on_internet_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_mark_icon_path_style", "mark_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_pop_up_definition_icon_path_style", "pop_up_definition_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_images_icon_path_style", "images_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_select_icon_path_style", "select_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_pop_up_definition_extra_images_icon_path_style", "pop_up_definition_extra_images_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_continue_icon_path_style", "continue_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_repeat_icon_path_style", "repeat_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_source_icon_path_style", "source_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_warning_icon_path_style", "warning_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_layout_icon_path_style", "layout_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_list_icon_path_style", "list_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_apperance_icon_path_style", "apperance_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_def_updated_icon_path_style", "def_updated_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_options_icon_path_style", "options_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_add_schema_icon_path_style", "add_schema_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_update_schema_icon_path_style", "update_schema_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_delete_schema_icon_path_style", "delete_schema_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_synonyms_icon_path_style", "synonyms_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dictionaries_icon_path_style", "dictionaries_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_down_expand_icon_path_style", "down_expand_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_double_down_expand_icon_path_style", "double_down_expand_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_internet_icon_path_style", "internet_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_replace_icon_path_style", "replace_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_lock_bw_icon_path_style", "lock_bw_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_unlock_bw_icon_path_style", "unlock_bw_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_go_icon_path_style", "go_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_left_roll_icon_path_style", "left_roll_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_right_roll_icon_path_style", "right_roll_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_close_icon_path_style", "close_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_up_arrow_style", "up_arrow", cmb_data="icon", input_box_width=-1, desc_getl="app_sett_icon_path_desc"),
            self._combobox("app_sett_style_item_icon_path_style", "item_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_checked_icon_path_style", "checked_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_not_checked_icon_path_style", "not_checked_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_wiki_logo_icon_path_style", "wiki_logo_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_definition_data_find_icon_path_style", "definition_data_find_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_update_definition_icon_path_style", "update_definition_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_thumb_up_icon_path_style", "thumb_up_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_thumb_down_icon_path_style", "thumb_down_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_cancel_icon_path_style", "cancel_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_ok_icon_path_style", "ok_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_download_icon_path_style", "download_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_archive_icon_path_style", "archive_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_edit_icon_path_style", "edit_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_remove_icon_path_style", "remove_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_add_item_icon_path_style", "add_item_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_add_icon_path_style", "add_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_save_red_disk_icon_path_style", "save_red_disk_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_save_startup_icon_path_style", "startup_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_sinfo_icon_path_style", "info_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_window_icon_path_style", "window_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_widget_icon_path_style", "widget_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_no_icon_icon_path_style", "no_icon_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_custom_icon_icon_path_style", "custom_icon_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_color_icon_path_style", "color_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_no_sound_icon_path_style", "no_sound_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_custom_sound_icon_path_style", "custom_sound_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_up_collapse_icon_path_style", "up_collapse_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_find_icon_path_style", "find_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_matchcase_icon_path_style", "matchcase_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_whole_words_icon_path_style", "whole_words_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_key_icon_path_style", "key_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_value_icon_path_style", "value_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_wiki_logo_color_icon_path_style", "wiki_logo_color_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_various_icons_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

    def show_block_settings(self, filter: dict = None, populate_archive: bool = False):
        section = self.getl("app_settings_lbl_menu_startup_title_text")

        # Block Area
        item_to_add = [
            self._title("app_sett_style_scroll_area_name", title_center=True),
            self._combobox("app_sett_style_frame_shape_style", "scroll_area_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "scroll_area_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "scroll_area_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "scroll_area_stylesheet", affected_keys=self._standard_affected_keys("scroll_area_stylesheet", "qscrollarea")),
            self._checkbox("app_sett_style_widget_enabled_style", "scroll_area_enabled", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_widget_visible_style", "scroll_area_visible", recomm_getl="widget_setting_true_recomm"),
            self._title("app_sett_style_scroll_area_margins_name"),
            self._input("app_sett_style_scroll_area_margins_name", "scroll_area_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_scroll_area_widget_margins_style", "scroll_area_widget_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_scroll_area_widget_layout_margins_style", "scroll_area_widget_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "scroll_area_widget_layout_spacing", desc_getl="app_sett_style_spacing_desc"),

            self._title("app_sett_style_label_widget_name", title_center=True),
            self._combobox("app_sett_style_area_label_widget_frame_shape_style", "area_label_widget_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_area_label_widget_frame_shadow_style", "area_label_widget_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_area_label_widget_line_width_style", "area_label_widget_line_width"),
            self._style("app_sett_style_area_label_widget_stylesheet_style", "area_label_widget_stylesheet", affected_keys="qlabel"),
            self._checkbox("app_sett_style_widget_visible_style", "area_label_widget_visible", recomm_getl="widget_setting_true_recomm"),
            self._title("app_sett_style_area_label_content_type_name"),
            self._input("app_sett_style_area_label_widget_min_height_style", "area_label_widget_min_height"),
            self._combobox("app_sett_style_area_label_content_type_style", "area_label_content_type", cmb_data="label_content_type", input_box_width=190),
            self._combobox("app_sett_style_area_label_widget_icon_path_style", "area_label_widget_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_area_label_widget_animation_path_style", "area_label_widget_animation_path", cmb_data="animation", input_box_width=-1),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_area_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()
        
        # Block
        item_to_add = [
            self._title("app_sett_style_block_general_name"),
            self._checkbox("app_sett_style_add_block_at_start_style", "add_block_at_start"),
            self._input("app_sett_style_block_tag_added_at_start_style", "block_tag_added_at_start", input_box_width=150, validator_type="tags", validator_data=self._get_tags_and_desc_for_block_tag_at_start()[0], desc_str=self._get_tags_and_desc_for_block_tag_at_start()[1]),
            self._combobox("app_sett_style_win_block_controls_show_long_date_style", "win_block_controls_show_long_date", cmb_data="long_date", input_box_width=200, desc_getl="app_sett_style_win_block_controls_show_long_date_desc"),
            self._combobox("app_sett_style_frame_shape_style", "win_block_frame_shape", cmb_data="frame_shape", desc_getl="app_sett_style_frame_shape_desc", recomm_getl="win_block_frame_shape_recomm"),
            self._combobox("app_sett_style_frame_shadow_style", "win_block_frame_shadow", cmb_data="frame_shadow", desc_getl="app_sett_style_frame_shadow_desc", recomm_getl="win_block_frame_shadow_recomm"),
            self._input("app_sett_style_line_width_style", "win_block_line_width", desc_getl="app_sett_style_line_width_desc", recomm_getl="win_block_line_width_recomm"),
            self._style("app_sett_style_win_block_stylesheet_style", "win_block_stylesheet", affected_keys="qframe"),
            self._input("app_sett_style_widget_margins_style", "win_block_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "win_block_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "win_block_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
            self._input("app_sett_style_blocks_buttons_with_no_text_width_pad_style", "blocks_buttons_with_no_text_width_pad"),
            self._checkbox("app_sett_style_block_save_event_hide_save_btn_style", "block_save_event_hide_save_btn", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_block_show_saved_btn_if_save_is_hidden_style", "block_show_saved_btn_if_save_is_hidden", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_block_image_thumb_size_style", "block_image_thumb_size"),
            self._combobox("app_sett_style_win_block_notif_block_updated_style", "win_block_notif_block_updated_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_remember_user_resize_block_info_for_all_blocks_style", "remember_user_resize_block_info_for_all_blocks", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_active_block_name"),
            self._style("app_sett_style_win_block_controls_active_stylesheet_style", "win_block_controls_active_stylesheet", affected_keys="qframe"),

            self._title("app_sett_style_block_animation_on_open_name"),
            self._checkbox("app_sett_style_block_animation_on_open_style", "block_animation_on_open"),
            self._input("app_sett_style_block_animation_on_open_steps_number_style", "block_animation_on_open_steps_number", desc_getl="block_animation_steps_number_desc", recomm_getl="block_animation_on_open_steps_number_recomm"),
            self._input("app_sett_style_block_animation_on_open_total_duration_ms_style", "block_animation_on_open_total_duration_ms", desc_getl="block_animation_duration_desc", recomm_getl="block_animation_on_open_total_duration_ms_recomm"),

            self._title("app_sett_style_block_animation_on_close_name"),
            self._checkbox("app_sett_style_block_animation_on_close_style", "block_animation_on_close"),
            self._input("app_sett_style_block_animation_on_close_steps_number_style", "block_animation_on_close_steps_number", desc_getl="block_animation_steps_number_desc", recomm_getl="block_animation_on_close_steps_number_recomm"),
            self._input("app_sett_style_block_animation_on_close_total_duration_ms_style", "block_animation_on_close_total_duration_ms", desc_getl="block_animation_duration_desc", recomm_getl="block_animation_on_close_total_duration_ms_recomm"),

            self._title("app_sett_style_block_animation_on_collapse_name"),
            self._checkbox("app_sett_style_block_animation_on_collapse_style", "block_animation_on_collapse"),
            self._input("app_sett_style_block_animation_on_collapse_steps_number_style", "block_animation_on_collapse_steps_number", desc_getl="block_animation_steps_number_desc", recomm_getl="block_animation_on_collapse_steps_number_recomm"),
            self._input("app_sett_style_block_animation_on_collapse_total_duration_ms_style", "block_animation_on_collapse_total_duration_ms", desc_getl="block_animation_duration_desc", recomm_getl="block_animation_on_close_total_duration_ms_recomm"),

            self._title("app_sett_style_block_animation_on_expand_name"),
            self._checkbox("app_sett_style_block_animation_on_expand_style", "block_animation_on_expand"),
            self._input("app_sett_style_block_animation_on_expand_steps_number_style", "block_animation_on_expand_steps_number", desc_getl="block_animation_steps_number_desc", recomm_getl="block_animation_on_collapse_steps_number_recomm"),
            self._input("app_sett_style_block_animation_on_expand_total_duration_ms_style", "block_animation_on_expand_total_duration_ms", desc_getl="block_animation_duration_desc", recomm_getl="block_animation_on_close_total_duration_ms_recomm"),

            self._title("app_sett_style_block_titlebar_name"),
            self._combobox("app_sett_style_frame_shape_style", "win_block_controls_frame_shape", cmb_data="frame_shape", desc_getl="app_sett_style_frame_shape_desc", recomm_getl="win_block_controls_frame_shape_recomm"),
            self._combobox("app_sett_style_frame_shadow_style", "win_block_controls_frame_shadow", cmb_data="frame_shadow", desc_getl="app_sett_style_frame_shadow_desc", recomm_getl="win_block_frame_shadow_recomm"),
            self._input("app_sett_style_line_width_style", "win_block_controls_line_width", desc_getl="app_sett_style_line_width_desc", recomm_getl="win_block_controls_line_width_recomm"),
            self._style("app_sett_style_win_block_controls_stylesheet_style", "win_block_controls_stylesheet", affected_keys="qframe"),
            self._input("app_sett_style_widget_margins_style", "win_block_controls_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "win_block_controls_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "win_block_controls_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
            
            self._title("app_sett_style_block_data_block_name"),
            self._combobox("app_sett_style_frame_shape_style", "data_block_frame_shape", cmb_data="frame_shape", desc_getl="app_sett_style_frame_shape_desc", recomm_getl="win_block_controls_frame_shape_recomm"),
            self._combobox("app_sett_style_frame_shadow_style", "data_block_frame_shadow", cmb_data="frame_shadow", desc_getl="app_sett_style_frame_shadow_desc", recomm_getl="win_block_frame_shadow_recomm"),
            self._input("app_sett_style_line_width_style", "data_block_line_width", desc_getl="app_sett_style_line_width_desc", recomm_getl="win_block_controls_line_width_recomm"),
            self._style("app_sett_style_header_stylesheet_style", "data_block_stylesheet", affected_keys="qframe"),
            self._input("app_sett_style_widget_margins_style", "data_block_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "data_block_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "data_block_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
            
            self._title("app_sett_style_block_header_name"),
            self._combobox("app_sett_style_frame_shape_style", "header_frame_shape", cmb_data="frame_shape", desc_getl="app_sett_style_frame_shape_desc", recomm_getl="win_block_controls_frame_shape_recomm"),
            self._combobox("app_sett_style_frame_shadow_style", "header_frame_shadow", cmb_data="frame_shadow", desc_getl="app_sett_style_frame_shadow_desc", recomm_getl="win_block_frame_shadow_recomm"),
            self._input("app_sett_style_line_width_style", "header_line_width", desc_getl="app_sett_style_line_width_desc", recomm_getl="win_block_controls_line_width_recomm"),
            self._style("app_sett_style_header_stylesheet_style", "header_stylesheet", affected_keys="qframe"),
            self._input("app_sett_style_widget_margins_style", "header_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "header_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "header_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
            
            self._title("app_sett_style_block_body_name"),
            self._combobox("app_sett_style_frame_shape_style", "body_frame_shape", cmb_data="frame_shape", desc_getl="app_sett_style_frame_shape_desc", recomm_getl="win_block_controls_frame_shape_recomm"),
            self._combobox("app_sett_style_frame_shadow_style", "body_frame_shadow", cmb_data="frame_shadow", desc_getl="app_sett_style_frame_shadow_desc", recomm_getl="win_block_frame_shadow_recomm"),
            self._input("app_sett_style_line_width_style", "body_line_width", desc_getl="app_sett_style_line_width_desc", recomm_getl="win_block_controls_line_width_recomm"),
            self._style("app_sett_style_body_stylesheet_style", "body_stylesheet", affected_keys="qframe"),
            self._input("app_sett_style_widget_margins_style", "body_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "body_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "body_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
            
            self._title("app_sett_style_block_body_block_image_area_name"),
            self._style("app_sett_style_block_image_area_stylesheet_style", "block_image_area_stylesheet", affected_keys=self._standard_affected_keys("block_image_area_stylesheet", "qscrollarea")),
            self._input("app_sett_style_block_image_area_contents_margins_style", "block_image_area_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._style("app_sett_style_block_image_area_widget_stylesheet_style", "block_image_area_widget_stylesheet", affected_keys=self._standard_affected_keys("block_image_area_widget_stylesheet", "qwidget")),
            self._input("app_sett_style_block_image_area_widget_contents_margins_style", "block_image_area_widget_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_block_image_widget_layout_contents_margins_style", "block_image_widget_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "block_image_widget_layout_spacing", desc_getl="app_sett_style_spacing_desc"),

            self._title("app_sett_style_block_footer_name"),
            self._combobox("app_sett_style_frame_shape_style", "footer_frame_shape", cmb_data="frame_shape", desc_getl="app_sett_style_frame_shape_desc", recomm_getl="win_block_controls_frame_shape_recomm"),
            self._combobox("app_sett_style_frame_shadow_style", "footer_frame_shadow", cmb_data="frame_shadow", desc_getl="app_sett_style_frame_shadow_desc", recomm_getl="win_block_frame_shadow_recomm"),
            self._input("app_sett_style_line_width_style", "footer_line_width", desc_getl="app_sett_style_line_width_desc", recomm_getl="win_block_controls_line_width_recomm"),
            self._style("app_sett_style_footer_stylesheet_style", "footer_stylesheet", affected_keys="qframe"),
            self._input("app_sett_style_widget_margins_style", "footer_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "footer_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "footer_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Buttons
        item_to_add = [
            self._title("app_sett_style_win_block_buttons_general_name"),
            self._input("app_sett_style_blocks_buttons_text_width_pad_style", "blocks_buttons_text_width_pad", desc_getl="blocks_buttons_text_width_pad_desc", recomm_getl="blocks_buttons_text_width_pad_recomm"),
            self._input("app_sett_style_blocks_buttons_text_height_pad_style", "blocks_buttons_text_height_pad", desc_getl="blocks_buttons_text_height_pad_desc", recomm_getl="blocks_buttons_text_height_pad_recomm"),
            
            self._title("app_sett_style_win_block_control_buttons_name", title_center=True),
            self._title("app_sett_style_win_block_control_btn_day_name"),
            self._checkbox("app_sett_style_win_block_control_btn_day_visible_style", "win_block_control_btn_day_visible"),
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_day_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_day_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_day", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "win_block_control_btn_day_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_day_icon_path", cmb_data="icon", input_box_width=-1),
            
            self._title("app_sett_style_win_block_control_btn_date_name"),
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_date_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_date_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_date", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "win_block_control_btn_date_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_date_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_win_block_control_btn_name_name"),
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_name_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_name_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_name", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "win_block_control_btn_name_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_name_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_win_block_control_btn_close_name"),
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_close_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_close", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "win_block_control_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_close_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_win_block_control_btn_collapse_name"),
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_collapse_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_collapse_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_collapse", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "win_block_control_btn_collapse_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_collapse_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_win_block_control_btn_expand_name"),
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_expand_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_expand_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_expand", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "win_block_control_btn_expand_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_expand_icon_path", cmb_data="icon", input_box_width=-1),
            
            self._title("app_sett_style_win_block_header_buttons_name", title_center=True),
            self._title("app_sett_style_header_btn_diary_name"),
            self._checkbox("app_sett_style_button_flat_style", "header_btn_diary_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "header_btn_diary_stylesheet", affected_keys=self._standard_affected_keys("header_btn_diary", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "header_btn_diary_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "header_btn_diary_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_header_btn_tag_name"),
            self._checkbox("app_sett_style_button_flat_style", "header_btn_tag_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "header_btn_tag_stylesheet", affected_keys=self._standard_affected_keys("header_btn_tag", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "header_btn_tag_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "header_btn_tag_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_header_btn_user_name"),
            self._checkbox("app_sett_style_button_flat_style", "header_btn_user_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "header_btn_user_stylesheet", affected_keys=self._standard_affected_keys("header_btn_user", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "header_btn_user_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "header_btn_user_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_header_btn_add_name"),
            self._checkbox("app_sett_style_button_flat_style", "header_btn_add_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "header_btn_add_stylesheet", affected_keys=self._standard_affected_keys("header_btn_add", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "header_btn_add_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "header_btn_add_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_win_block_footer_buttons_name", title_center=True),
            self._title("app_sett_style_footer_btn_save_name"),
            self._checkbox("app_sett_style_button_flat_style", "footer_btn_save_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "footer_btn_save_stylesheet", affected_keys=self._standard_affected_keys("footer_btn_save", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "footer_btn_save_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "footer_btn_save_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_footer_btn_saved_name"),
            self._checkbox("app_sett_style_footer_btn_saved_visible_style", "footer_btn_saved_visible", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_button_flat_style", "footer_btn_saved_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "footer_btn_saved_stylesheet", affected_keys=self._standard_affected_keys("footer_btn_saved", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "footer_btn_saved_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "footer_btn_saved_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_footer_btn_add_new_name"),
            self._checkbox("app_sett_style_footer_btn_add_new_visible_style", "footer_btn_add_new_visible", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_button_flat_style", "footer_btn_add_new_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "footer_btn_add_new_stylesheet", affected_keys=self._standard_affected_keys("footer_btn_add_new", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "footer_btn_add_new_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "footer_btn_add_new_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_footer_btn_delete_name"),
            self._checkbox("app_sett_style_button_flat_style", "footer_btn_delete_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "footer_btn_delete_stylesheet", affected_keys=self._standard_affected_keys("footer_btn_delete", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "footer_btn_delete_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "footer_btn_delete_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_footer_btn_add_new_image_name"),
            self._checkbox("app_sett_style_button_flat_style", "footer_btn_add_new_image_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "footer_btn_add_new_image_stylesheet", affected_keys=self._standard_affected_keys("footer_btn_add_new_image", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "footer_btn_add_new_image_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "footer_btn_add_new_image_icon_path", cmb_data="image", input_box_width=-1),
            self._title("app_sett_style_footer_btn_detection_name"),
            self._checkbox("app_sett_style_button_flat_style", "footer_btn_detection_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "footer_btn_detection_stylesheet", affected_keys=self._standard_affected_keys("footer_btn_detection", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "footer_btn_detection_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "footer_btn_detection_icon_path", cmb_data="icon", input_box_width=-1)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_buttons_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Text Editor
        item_to_add = [
            self._title("app_sett_style_block_text_editor_general_name"),
            self._checkbox("app_sett_style_block_editor_smart_parenthesis_enabled_style", "block_editor_smart_parenthesis_enabled", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_body_txt_box_tab_changes_focus_style", "body_txt_box_tab_changes_focus", desc_getl="body_txt_box_tab_changes_focus_desc", recomm_getl="body_txt_box_tab_changes_focus_recomm"),
            self._combobox("app_sett_style_body_txt_box_line_wrap_mode_style", "body_txt_box_line_wrap_mode", cmb_data="line_wrap_mode", desc_getl="body_txt_box_line_wrap_mode_desc", recomm_getl="body_txt_box_line_wrap_mode_recomm"),
            self._input("app_sett_style_body_txt_box_line_wrap_column_or_width_style", "body_txt_box_line_wrap_column_or_width", desc_getl="body_txt_box_line_wrap_column_or_width_desc"),
            self._checkbox("app_sett_style_body_txt_box_accept_rich_text_style", "body_txt_box_accept_rich_text", desc_getl="body_txt_box_accept_rich_text_desc"),
            self._input("app_sett_style_body_txt_box_cursor_width_style", "body_txt_box_cursor_width", desc_getl="body_txt_box_cursor_width_desc", recomm_getl="body_txt_box_cursor_width_recomm"),
            self._input("app_sett_style_body_txt_box_number_of_visible_lines_style", "body_txt_box_number_of_visible_lines", desc_getl="body_txt_box_number_of_visible_lines_desc", recomm_getl="body_txt_box_number_of_visible_lines_recomm"),
            
            self._title("app_sett_style_lists_in_block_name"),
            self._input("app_sett_style_text_handler_list_string_style", "text_handler_list_string"),

            self._title("app_sett_style_block_text_editor_apperance_name"),
            self._combobox("app_sett_style_frame_shape_style", "body_txt_box_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "body_txt_box_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "body_txt_box_line_width"),
            self._style("app_sett_style_text_editor_stylesheet_style", "body_txt_box_stylesheet", affected_keys=self._standard_affected_keys("body_txt_box", "qtextedit"))
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_text_editor_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Autosave
        item_to_add = [
            self._checkbox("app_sett_style_block_autosave_enabled_style", "block_autosave_enabled", recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_block_autosave_on_lost_focus_style", "block_autosave_on_lost_focus", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_block_autosave_check_every_style", "block_autosave_check_every"),
            self._input("app_sett_style_block_autosave_timeout_style", "block_autosave_timeout"),
            
            self._title("app_sett_style_autosave_message_name", title_center=True),
            self._checkbox("app_sett_style_block_autosave_show_msg_style", "block_autosave_show_msg", recomm_getl="widget_setting_true_recomm"),
            self._input("app_sett_style_block_autosave_msg_duration_style", "block_autosave_msg_duration"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_autosave_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Information Message (Autosave etc.)
        item_to_add = [
            self._checkbox("app_sett_style_button_flat_style", "win_block_control_btn_msg_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "win_block_control_btn_msg_stylesheet", affected_keys=self._standard_affected_keys("win_block_control_btn_msg_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "win_block_control_btn_msg_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_widget_visible_style", "win_block_control_btn_msg_visible"),

            self._title("app_sett_style_block_calc_mode_titlebar_msg_name", title_center=True),
            self._checkbox("app_sett_style_block_calc_mode_titlebar_msg_enabled_style", "block_calc_mode_titlebar_msg_enabled"),
            self._input("app_sett_style_block_calc_mode_titlebar_msg_duration_style", "block_calc_mode_titlebar_msg_duration"),

            self._title("app_sett_style_block_definition_mode_titlebar_msg_name", title_center=True),
            self._checkbox("app_sett_style_block_definition_titlebar_msg_enabled_style", "block_definition_titlebar_msg_enabled"),
            self._input("app_sett_style_block_calc_mode_titlebar_msg_duration_style", "block_definition_titlebar_msg_duration"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_information_message_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Auto_add images
        item_to_add = [
            self._input("app_sett_style_auto_add_image_frame_lbl_pic_style", "auto_add_image_frame_lbl_pic_file_path", validator_type="icon", input_box_width=-1),
            self._combobox("app_sett_style_block_body_auto_added_image_sound_style", "block_body_auto_added_image_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_block_body_auto_added_image_error_sound_style", "block_body_auto_added_image_error_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_auto_add_images_frame_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Highlighted text
        item_to_add = [
            self._checkbox("app_sett_style_show_word_highlight_style", "show_word_highlight"),
            self._checkbox("app_sett_style_block_body_highlighted_font_italic_style", "block_body_highlighted_font_italic"),
            self._input("app_sett_style_block_body_highlighted_color_style", "block_body_highlighted_color", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_body_highlighted_background_style", "block_body_highlighted_background", validator_type="color", input_box_width=80)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_highlighted_text_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Hyperlinks
        item_to_add = [
            self._checkbox("app_sett_style_http_hyperlink_text_detection_enabled_style", "http_hyperlink_text_detection_enabled"),
            self._checkbox("app_sett_style_hyperlink_mark_enabled_style", "hyperlink_mark_enabled"),
            self._checkbox("app_sett_style_hyperlink_mouse_action_enabled_style", "hyperlink_mouse_action_enabled"),
            self._checkbox("app_sett_style_hyperlink_mouse_hover_show_tooltip_enabled_style", "hyperlink_mouse_hover_show_tooltip_enabled"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_hyperlinks_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Numbers Marking
        item_to_add = [
            self._checkbox("app_sett_style_numbers_in_block_text_mark_enabled_style", "numbers_in_block_text_mark_enabled"),
            self._input("app_sett_style_numbers_in_block_content_mark_forecolor_style", "numbers_in_block_content_mark_forecolor", validator_type="color", input_box_width=80)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_numbers_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Block Definition Hint
        item_to_add = [
            self._checkbox("app_sett_style_definition_hint_enabled_style", "definition_hint_enabled"),
            self._def_hint_edit(),
            self._combobox("app_sett_style_definition_hint_icon_path_style", "definition_hint_icon_path", cmb_data="icon", input_box_width=-1),
            self._input("app_sett_style_definition_hint_minimum_word_lenght_style", "definition_hint_minimum_word_lenght"),
            self._combobox("app_sett_style_definition_hint_sound_pop_up_style", "definition_hint_sound_pop_up", cmb_data="sound", input_box_width=-1),
            self._input("app_sett_style_definition_hint_typing_delay_style", "definition_hint_typing_delay"),
            self._combobox("app_sett_style_definition_hint_btn_close_icon_path_style", "definition_hint_btn_close_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_definition_hint_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

    def show_widget_settings(self, filter: dict = None, populate_archive: bool = False):
        section = self.getl("app_settings_lbl_menu_widget_title_text")

        # All dialogs general settings
        item_to_add = [
            self._style("app_sett_style_dialog_stylesheet_style", "", affected_keys=self.win_dialogs_style_affected_keys(), desc_getl="stylesheet_win_desc")
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_all_dialogs_general_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Dialog Title
        item_to_add = [
            self._combobox("app_sett_style_frame_shape_style", "", cmb_data="frame_shape", affected_keys=self.win_dialogs_title_frame_shape_affected_keys()),
            self._combobox("app_sett_style_frame_shadow_style", "", cmb_data="frame_shadow", affected_keys=self.win_dialogs_title_frame_shadow_affected_keys()),
            self._input("app_sett_style_line_width_style", "", affected_keys=self.win_dialogs_title_line_width_affected_keys()),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "", affected_keys=self.win_dialogs_title_style_affected_keys(), desc_getl="stylesheet_desc")
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_all_dialogs_title_label_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Dialog Cancel button
        item_to_add = [
            self._checkbox("app_sett_style_button_flat_style", "", desc_getl="app_sett_style_button_flat_desc", affected_keys=self.btn_cancel_flat_affected_keys()),
            self._style("app_sett_style_button_stylesheet_style", "", affected_keys=self.btn_cancel_style_affected_keys(), desc_getl="stylesheet_desc"),
            self._combobox("app_sett_style_select_icon_image_style", "", cmb_data="icon", input_box_width=-1, affected_keys=self.btn_cancel_icon_path_affected_keys(), desc_getl="app_sett_icon_path_desc")
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_all_dialogs_btn_cancel_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Dialog Confirm button
        item_to_add = [
            self._checkbox("app_sett_style_button_flat_style", "", desc_getl="app_sett_style_button_flat_desc", affected_keys=self.btn_confirm_flat_affected_keys()),
            self._style("app_sett_style_button_stylesheet_style", "", affected_keys=self.btn_confirm_style_affected_keys(), desc_getl="stylesheet_desc"),
            self._combobox("app_sett_style_select_icon_image_style", "", cmb_data="icon", input_box_width=-1, affected_keys=self.btn_confirm_icon_path_affected_keys(), desc_getl="app_sett_icon_path_desc")
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_all_dialogs_btn_confirm_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Dialog Delete button
        item_to_add = [
            self._checkbox("app_sett_style_button_flat_style", "", desc_getl="app_sett_style_button_flat_desc", affected_keys=self.btn_delete_flat_affected_keys()),
            self._style("app_sett_style_button_stylesheet_style", "", affected_keys=self.btn_delete_style_affected_keys(), desc_getl="stylesheet_desc"),
            self._combobox("app_sett_style_select_icon_image_style", "", cmb_data="icon", input_box_width=-1, affected_keys=self.btn_delete_icon_path_affected_keys(), desc_getl="app_sett_icon_path_desc")
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_all_dialogs_btn_delete_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Menu
        item_to_add = [
            self._title("app_sett_style_menu_main_name", title_center=True, font_size=18),
            self._style("app_sett_style_main_menu_stylesheet_style", "", affected_keys=self.menu_main_style_affected_keys(), desc_getl="stylesheet_desc"),
            self._checkbox("app_sett_style_menu_tooltip_visible_style", "", desc_getl="app_sett_style_menu_tooltip_visible_desc", affected_keys=self.menu_main_tooltip_visible_affected_keys(), recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_enabled_style", "", desc_getl="app_sett_style_menu_enabled_desc", affected_keys=self.menu_main_enabled_affected_keys(), recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "", desc_getl="app_sett_style_menu_visible_desc", affected_keys=self.menu_main_visible_affected_keys(), recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_menu_item_name", title_center=True, font_size=18),
            self._checkbox("app_sett_style_menu_enabled_style", "", desc_getl="app_sett_style_menu_enabled_desc", affected_keys=self.menu_item_enabled_affected_keys(), recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_visible_style", "", desc_getl="app_sett_style_menu_visible_desc", affected_keys=self.menu_item_visible_affected_keys(), recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_shortcut_visible_style", "", desc_getl="app_sett_style_menu_shortcut_visible_desc", affected_keys=self.menu_item_shortcut_visible_affected_keys(), recomm_getl="widget_setting_true_recomm"),
            self._checkbox("app_sett_style_menu_icon_visible_style", "", desc_getl="app_sett_style_menu_icon_visible_desc", affected_keys=self.menu_item_icon_visible_affected_keys(), recomm_getl="widget_setting_true_recomm"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_all_menus_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        bg_section_color = "#4c3200"
        bg_color_main_section = "#000000"
        fg_color_main_section = "#ffff00"
        hover_color_main_section = "#55ffff"
        # GLOBAL WIDGETS PROPERTIES
        # Pushbuttons
        item_to_add = [
            self._title("app_sett_style_gwp_buttons_click_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_cursor_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_allow_cursor_change_style", "gwp_qpushbutton_allow_cursor_change", desc_getl="gwp_qpushbutton_allow_cursor_change_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_cursor_style", "gwp_qpushbutton_cursor", cmb_data="cursor", input_box_width=-1),
            self._input("app_sett_style_gwp_qpushbutton_cursor_width_style", "gwp_qpushbutton_cursor_width", desc_getl="gwp_qpushbutton_cursor_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_height_style", "gwp_qpushbutton_cursor_height", desc_getl="gwp_qpushbutton_cursor_height_desc"),
            self._checkbox("app_sett_style_gwp_qpushbutton_cursor_keep_aspect_ratio_style", "gwp_qpushbutton_cursor_keep_aspect_ratio", desc_getl="gwp_qpushbutton_cursor_keep_aspect_ratio_desc"),

            self._title("app_sett_style_gwp_buttons_click_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_qpushbutton_tap_event_show_animation_enabled"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_qpushbutton_tap_event_show_animation_file_path", cmb_data="animation", input_box_width=-1),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_qpushbutton_tap_event_show_animation_width"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_qpushbutton_tap_event_show_animation_height"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_qpushbutton_tap_event_show_animation_background_color", validator_type="color"),

            self._title("app_sett_style_gwp_buttons_click_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qpushbutton_tap_event_play_sound_enabled"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qpushbutton_tap_event_play_sound_file_path", cmb_data="sound", input_box_width=-1),

            self._title("app_sett_style_gwp_buttons_click_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_qpushbutton_tap_event_change_stylesheet_enabled"),
            self._style("app_sett_style_button_stylesheet_style", "gwp_qpushbutton_tap_event_change_qss_stylesheet", affected_keys=[["gwp_qpushbutton_tap_event_change_qss_stylesheet", "qpushbutton"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qpushbutton_tap_event_change_stylesheet_duration_ms"),

            self._title("app_sett_style_gwp_buttons_click_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_qpushbutton_tap_event_change_size_enabled"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qpushbutton_tap_event_change_size_percent"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qpushbutton_tap_event_change_size_duration_ms"),

            self._title("app_sett_style_gwp_buttons_enter_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_enter_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_qpushbutton_enter_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_qpushbutton_enter_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_qpushbutton_enter_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_qpushbutton_enter_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_qpushbutton_enter_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_qpushbutton_enter_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_enter_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qpushbutton_enter_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qpushbutton_enter_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_enter_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_qpushbutton_enter_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_button_stylesheet_style", "gwp_qpushbutton_enter_event_change_qss_stylesheet", affected_keys=[["gwp_qpushbutton_enter_event_change_qss_stylesheet", "qpushbutton"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qpushbutton_enter_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_enter_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_qpushbutton_enter_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qpushbutton_enter_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qpushbutton_enter_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_leave_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_qpushbutton_leave_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_qpushbutton_leave_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_qpushbutton_leave_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_qpushbutton_leave_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_qpushbutton_leave_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_qpushbutton_leave_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_leave_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qpushbutton_leave_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qpushbutton_leave_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_leave_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_qpushbutton_leave_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_button_stylesheet_style", "gwp_qpushbutton_leave_event_change_qss_stylesheet", affected_keys=[["gwp_qpushbutton_leave_event_change_qss_stylesheet", "qpushbutton"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qpushbutton_leave_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_qpushbutton_leave_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qpushbutton_leave_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qpushbutton_leave_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_buttons_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # GLOBAL WIDGETS PROPERTIES
        # Action Frames (Large menu buttons on Dialog)
        item_to_add = [
            self._title("app_sett_style_gwp_buttons_click_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_cursor_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_allow_cursor_change_style", "gwp_actionframe_allow_cursor_change", desc_getl="gwp_qpushbutton_allow_cursor_change_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_cursor_style", "gwp_actionframe_cursor", cmb_data="cursor", input_box_width=-1, desc_getl="gwp_qpushbutton_cursor_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_width_style", "gwp_actionframe_cursor_width", desc_getl="gwp_qpushbutton_cursor_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_height_style", "gwp_actionframe_cursor_height", desc_getl="gwp_qpushbutton_cursor_height_desc"),
            self._checkbox("app_sett_style_gwp_qpushbutton_cursor_keep_aspect_ratio_style", "gwp_actionframe_cursor_keep_aspect_ratio", desc_getl="gwp_qpushbutton_cursor_keep_aspect_ratio_desc"),

            self._title("app_sett_style_gwp_buttons_click_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_actionframe_tap_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_actionframe_tap_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_actionframe_tap_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_actionframe_tap_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_actionframe_tap_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_actionframe_tap_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_click_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_actionframe_tap_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_actionframe_tap_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_click_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_actionframe_tap_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_button_stylesheet_style", "gwp_actionframe_tap_event_change_qss_stylesheet", affected_keys=[["gwp_actionframe_tap_event_change_qss_stylesheet", "qframe"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_actionframe_tap_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_click_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_actionframe_tap_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_actionframe_tap_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_actionframe_tap_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_enter_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_enter_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_actionframe_enter_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_actionframe_enter_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_actionframe_enter_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_actionframe_enter_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_actionframe_enter_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_actionframe_enter_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_enter_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_actionframe_enter_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_actionframe_enter_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_enter_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_actionframe_enter_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_button_stylesheet_style", "gwp_actionframe_enter_event_change_qss_stylesheet", affected_keys=[["gwp_actionframe_enter_event_change_qss_stylesheet", "qframe"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_actionframe_enter_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_enter_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_actionframe_enter_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_actionframe_enter_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_actionframe_enter_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_leave_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_actionframe_leave_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_actionframe_leave_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_actionframe_leave_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_actionframe_leave_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_actionframe_leave_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_actionframe_leave_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_leave_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_actionframe_leave_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_actionframe_leave_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_leave_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_actionframe_leave_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_button_stylesheet_style", "gwp_actionframe_leave_event_change_qss_stylesheet", affected_keys=[["gwp_actionframe_leave_event_change_qss_stylesheet", "qframe"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_actionframe_leave_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_actionframe_leave_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_actionframe_leave_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_actionframe_leave_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_actionframe_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # GLOBAL WIDGETS PROPERTIES
        # Selectable Widgets (CheckBox, ComboBox, RadioButton...)
        item_to_add = [
            self._title("app_sett_style_gwp_selection_click_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_cursor_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_allow_cursor_change_style", "gwp_selection_allow_cursor_change", desc_getl="gwp_qpushbutton_allow_cursor_change_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_cursor_style", "gwp_selection_cursor", cmb_data="cursor", input_box_width=-1),
            self._input("app_sett_style_gwp_qpushbutton_cursor_width_style", "gwp_selection_cursor_width", desc_getl="gwp_qpushbutton_cursor_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_height_style", "gwp_selection_cursor_height", desc_getl="gwp_qpushbutton_cursor_height_desc"),
            self._checkbox("app_sett_style_gwp_qpushbutton_cursor_keep_aspect_ratio_style", "gwp_selection_cursor_keep_aspect_ratio", desc_getl="gwp_qpushbutton_cursor_keep_aspect_ratio_desc"),

            self._title("app_sett_style_gwp_selection_click_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_selection_tap_event_show_animation_enabled"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_selection_tap_event_show_animation_file_path", cmb_data="animation", input_box_width=-1),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_selection_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_selection_tap_event_show_animation_width"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_selection_tap_event_show_animation_height"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_selection_tap_event_show_animation_background_color", validator_type="color"),

            self._title("app_sett_style_gwp_selection_click_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_selection_tap_event_play_sound_enabled"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_selection_tap_event_play_sound_file_path", cmb_data="sound", input_box_width=-1),

            self._title("app_sett_style_gwp_selection_click_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_selection_tap_event_change_stylesheet_enabled"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_selection_tap_event_change_qss_stylesheet", affected_keys=[["gwp_selection_tap_event_change_qss_stylesheet", "qcheckbox"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_selection_tap_event_change_stylesheet_duration_ms"),

            self._title("app_sett_style_gwp_selection_click_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_selection_tap_event_change_size_enabled"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_selection_tap_event_change_size_percent"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_selection_tap_event_change_size_duration_ms"),

            self._title("app_sett_style_gwp_buttons_enter_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_enter_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_selection_enter_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_selection_enter_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_selection_enter_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_selection_enter_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_selection_enter_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_selection_enter_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_enter_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_selection_enter_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_selection_enter_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_enter_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_selection_enter_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_selection_enter_event_change_qss_stylesheet", affected_keys=[["gwp_selection_enter_event_change_qss_stylesheet", "qcheckbox"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_selection_enter_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_enter_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_selection_enter_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_selection_enter_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_selection_enter_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_leave_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_selection_leave_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_selection_leave_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_selection_leave_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_selection_leave_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_selection_leave_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_selection_leave_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_leave_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_selection_leave_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_selection_leave_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_leave_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_selection_leave_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_selection_leave_event_change_qss_stylesheet", affected_keys=[["gwp_selection_leave_event_change_qss_stylesheet", "qcheckbox"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_selection_leave_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_selection_leave_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_selection_leave_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_selection_leave_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_selection_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # GLOBAL WIDGETS PROPERTIES
        # Item Based Widgets (QListWidget, QTableWidget, QTreeWidget...)
        item_to_add = [
            self._title("app_sett_style_gwp_selection_click_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_cursor_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_allow_cursor_change_style", "gwp_item_based_allow_cursor_change", desc_getl="gwp_qpushbutton_allow_cursor_change_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_cursor_style", "gwp_item_based_cursor", cmb_data="cursor", input_box_width=-1),
            self._input("app_sett_style_gwp_qpushbutton_cursor_width_style", "gwp_item_based_cursor_width", desc_getl="gwp_qpushbutton_cursor_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_height_style", "gwp_item_based_cursor_height", desc_getl="gwp_qpushbutton_cursor_height_desc"),
            self._checkbox("app_sett_style_gwp_qpushbutton_cursor_keep_aspect_ratio_style", "gwp_item_based_cursor_keep_aspect_ratio", desc_getl="gwp_qpushbutton_cursor_keep_aspect_ratio_desc"),

            self._title("app_sett_style_gwp_selection_click_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_item_based_tap_event_show_animation_enabled"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_item_based_tap_event_show_animation_file_path", cmb_data="animation", input_box_width=-1),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_item_based_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_item_based_tap_event_show_animation_width"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_item_based_tap_event_show_animation_height"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_item_based_tap_event_show_animation_background_color", validator_type="color"),

            self._title("app_sett_style_gwp_selection_click_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_item_based_tap_event_play_sound_enabled"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_item_based_tap_event_play_sound_file_path", cmb_data="sound", input_box_width=-1),

            self._title("app_sett_style_gwp_selection_click_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_item_based_tap_event_change_stylesheet_enabled"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_item_based_tap_event_change_qss_stylesheet", affected_keys=[["gwp_item_based_tap_event_change_qss_stylesheet", "qlistwidget"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_item_based_tap_event_change_stylesheet_duration_ms"),

            self._title("app_sett_style_gwp_selection_click_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_item_based_tap_event_change_size_enabled"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_item_based_tap_event_change_size_percent"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_item_based_tap_event_change_size_duration_ms"),

            self._title("app_sett_style_gwp_buttons_enter_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_enter_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_item_based_enter_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_item_based_enter_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_item_based_enter_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_item_based_enter_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_item_based_enter_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_item_based_enter_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_enter_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_item_based_enter_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_item_based_enter_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_enter_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_item_based_enter_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_item_based_enter_event_change_qss_stylesheet", affected_keys=[["gwp_item_based_enter_event_change_qss_stylesheet", "qlistwidget"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_item_based_enter_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_enter_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_item_based_enter_event_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_item_based_enter_event_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_item_based_enter_event_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_name", title_center=True, font_size=16, bg_color=bg_section_color),

            self._title("app_sett_style_gwp_buttons_leave_animation_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_enabled_style", "gwp_item_based_leave_event_show_animation_enabled", desc_getl="gwp_qpushbutton_tap_event_show_animation_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_show_animation_file_path_style", "gwp_item_based_leave_event_show_animation_file_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_show_animation_file_path_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_duration_ms_style", "gwp_item_based_leave_event_show_animation_duration_ms", desc_getl="gwp_qpushbutton_tap_event_show_animation_duration_ms"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_width_style", "gwp_item_based_leave_event_show_animation_width", desc_getl="gwp_qpushbutton_tap_event_show_animation_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_height_style", "gwp_item_based_leave_event_show_animation_height", desc_getl="gwp_qpushbutton_tap_event_show_animation_height_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_show_animation_background_color_style", "gwp_item_based_leave_event_show_animation_background_color", validator_type="color", desc_getl="gwp_qpushbutton_tap_event_show_animation_background_color_desc"),

            self._title("app_sett_style_gwp_buttons_leave_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_item_based_leave_event_play_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_item_based_leave_event_play_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),

            self._title("app_sett_style_gwp_buttons_leave_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_enabled_style", "gwp_item_based_leave_event_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_item_based_leave_event_change_qss_stylesheet", affected_keys=[["gwp_item_based_leave_event_change_qss_stylesheet", "qlistwidget"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_item_based_leave_event_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),

            self._title("app_sett_style_gwp_buttons_leave_size_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_change_size_enabled_style", "gwp_selection_leave_event_change_size_enabled", desc_getl="gwp_item_based_leave_event_change_size_enabled"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_selection_leave_event_change_size_percent", desc_getl="gwp_item_based_leave_event_change_size_percent"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_selection_leave_event_change_size_duration_ms", desc_getl="gwp_item_based_leave_event_change_size_duration_ms"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_item_based_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # GLOBAL WIDGETS PROPERTIES
        # Dialog
        item_to_add = [
            self._title("app_sett_style_gwp_dialog_drag_name", title_center=True, font_size=16, bg_color=bg_section_color),
            
            self._checkbox("app_sett_style_gwp_qdialog_window_drag_enabled_style", "gwp_qdialog_window_drag_enabled", desc_getl="gwp_qdialog_window_drag_enabled_desc"),
            self._checkbox("app_sett_style_gwp_qdialog_drag_dialog_with_body_style", "gwp_qdialog_window_drag_enabled_with_body", desc_getl="gwp_qdialog_dialog_drag_with_body_desc"),

            self._title("app_sett_style_gwp_dialog_drag_cursor_name"),
            self._checkbox("app_sett_style_gwp_qdialog_allow_drag_widgets_cursor_change_style", "gwp_qdialog_allow_drag_widgets_cursor_change", desc_getl="gwp_qdialog_allow_drag_widgets_cursor_change_desc"),
            self._combobox("app_sett_style_gwp_qdialog_start_drag_cursor_style", "gwp_qdialog_start_drag_cursor", cmb_data="cursor", input_box_width=-1, desc_getl="gwp_qdialog_start_drag_cursor_desc"),
            self._combobox("app_sett_style_gwp_qdialog_end_drag_cursor_style", "gwp_qdialog_end_drag_cursor", cmb_data="cursor", input_box_width=-1, desc_getl="gwp_qdialog_end_drag_cursor_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_width_style", "gwp_qdialog_cursor_width", desc_getl="gwp_qpushbutton_cursor_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_height_style", "gwp_qdialog_cursor_height", desc_getl="gwp_qpushbutton_cursor_height_desc"),
            self._checkbox("app_sett_style_gwp_qpushbutton_cursor_keep_aspect_ratio_style", "gwp_qdialog_cursor_keep_aspect_ratio", desc_getl="gwp_qpushbutton_cursor_keep_aspect_ratio_desc"),
            # Mask label while dragging
            self._title("app_sett_style_gwp_frame_mask_label_name"),
            self._checkbox("app_sett_style_gwp_qframe_dragged_window_mask_label_enabled_style", "gwp_qdialog_dragged_window_mask_label_enabled", desc_getl="gwp_qframe_dragged_window_mask_label_enabled_desc"),
            self._style("app_sett_style_label_mask_stylesheet_style", "gwp_qdialog_dragged_window_mask_label_stylesheet", affected_keys=[["gwp_qframe_dragged_window_mask_label_stylesheet", "qlabel"]], desc_getl="gwp_qframe_dragged_window_mask_label_stylesheet_desc"),
            self._combobox("app_sett_style_gwp_qframe_dragged_window_mask_label_image_path_style", "gwp_qdialog_dragged_window_mask_label_image_path", cmb_data="icon", input_box_width=-1, desc_getl="gwp_qframe_dragged_window_mask_label_image_path_desc"),
            self._combobox("app_sett_style_gwp_qframe_dragged_window_mask_label_animation_path_style", "gwp_qdialog_dragged_window_mask_label_animation_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qframe_dragged_window_mask_label_animation_path_desc"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # GLOBAL WIDGETS PROPERTIES
        # Frame
        item_to_add = [
            self._title("app_sett_style_gwp_frame_drag_name", title_center=True, font_size=16, bg_color=bg_section_color),
            
            self._checkbox("app_sett_style_gwp_qdialog_window_drag_enabled_style", "gwp_qframe_window_drag_enabled", desc_getl="gwp_qdialog_window_drag_enabled_desc"),
            self._checkbox("app_sett_style_gwp_qdialog_drag_frame_with_body_style", "gwp_qframe_window_drag_enabled_with_body", desc_getl="gwp_qdialog_frame_drag_with_body_desc"),

            self._title("app_sett_style_gwp_frame_drag_cursor_name"),
            self._checkbox("app_sett_style_gwp_qdialog_allow_drag_widgets_cursor_change_style", "gwp_qframe_allow_drag_widgets_cursor_change", desc_getl="gwp_qdialog_allow_drag_widgets_cursor_change_desc"),
            self._combobox("app_sett_style_gwp_qdialog_start_drag_cursor_style", "gwp_qframe_start_drag_cursor", cmb_data="cursor", input_box_width=-1, desc_getl="gwp_qdialog_start_drag_cursor_desc"),
            self._combobox("app_sett_style_gwp_qdialog_end_drag_cursor_style", "gwp_qframe_end_drag_cursor", cmb_data="cursor", input_box_width=-1, desc_getl="gwp_qdialog_end_drag_cursor_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_width_style", "gwp_qframe_cursor_width", desc_getl="gwp_qpushbutton_cursor_width_desc"),
            self._input("app_sett_style_gwp_qpushbutton_cursor_height_style", "gwp_qframe_cursor_height", desc_getl="gwp_qpushbutton_cursor_height_desc"),
            self._checkbox("app_sett_style_gwp_qpushbutton_cursor_keep_aspect_ratio_style", "gwp_qframe_cursor_keep_aspect_ratio", desc_getl="gwp_qpushbutton_cursor_keep_aspect_ratio_desc"),

            # Frame stylesheet while dragging
            self._title("app_sett_style_gwp_frame_change_stylesheet_name"),
            self._checkbox("app_sett_style_gwp_qframe_dragged_window_change_stylesheet_enabled_style", "gwp_qframe_dragged_window_change_stylesheet_enabled", desc_getl="gwp_qframe_dragged_window_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_qframe_dragged_window_stylesheet", affected_keys=[["gwp_qframe_dragged_window_stylesheet", "qframe"]]),
            # Mask label while dragging
            self._title("app_sett_style_gwp_frame_mask_label_name"),
            self._checkbox("app_sett_style_gwp_qframe_dragged_window_mask_label_enabled_style", "gwp_qframe_dragged_window_mask_label_enabled", desc_getl="gwp_qframe_dragged_window_mask_label_enabled_desc"),
            self._style("app_sett_style_label_mask_stylesheet_style", "gwp_qframe_dragged_window_mask_label_stylesheet", affected_keys=[["gwp_qframe_dragged_window_mask_label_stylesheet", "qlabel"]], desc_getl="gwp_qframe_dragged_window_mask_label_stylesheet_desc"),
            self._combobox("app_sett_style_gwp_qframe_dragged_window_mask_label_image_path_style", "gwp_qframe_dragged_window_mask_label_image_path", cmb_data="icon", input_box_width=-1, desc_getl="gwp_qframe_dragged_window_mask_label_image_path_desc"),
            self._combobox("app_sett_style_gwp_qframe_dragged_window_mask_label_animation_path_style", "gwp_qframe_dragged_window_mask_label_animation_path", cmb_data="animation", input_box_width=-1, desc_getl="gwp_qframe_dragged_window_mask_label_animation_path_desc"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_frame_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # GLOBAL WIDGETS PROPERTIES
        # TextBox
        item_to_add = [
            self._title("app_sett_style_gwp_key_press_name", title_center=True, font_size=16, bg_color=bg_section_color),
            
            # Key Pressed - Sound
            self._title("app_sett_style_gwp_qtextedit_key_pressed_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qtextedit_key_pressed_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qtextedit_key_pressed_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),
            # Key Pressed - Change Stylesheet
            self._title("app_sett_style_gwp_qtextedit_key_pressed_change_stylesheet_name"),
            self._checkbox("app_sett_style_textbox_stylesheet_enabled_style", "gwp_qtextedit_key_pressed_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_qtextedit_key_pressed_change_qss_stylesheet", affected_keys=[["gwp_qtextedit_key_pressed_change_qss_stylesheet", "qlineedit"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qtextedit_key_pressed_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),
            # Key Pressed - Change Size
            self._title("app_sett_style_gwp_qtextedit_key_pressed_change_size_name"),
            self._checkbox("app_sett_style_textbox_change_size_enabled_style", "gwp_qtextedit_key_pressed_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qtextedit_key_pressed_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qtextedit_key_pressed_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_return_press_name", title_center=True, font_size=16, bg_color=bg_section_color),
            
            # ENTER Pressed - Sound
            self._title("app_sett_style_gwp_qtextedit_return_pressed_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qtextedit_return_pressed_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qtextedit_return_pressed_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),
            # ENTER Pressed - Change Stylesheet
            self._title("app_sett_style_gwp_qtextedit_return_pressed_change_stylesheet_name"),
            self._checkbox("app_sett_style_textbox_stylesheet_enabled_style", "gwp_qtextedit_return_pressed_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_qtextedit_return_pressed_change_qss_stylesheet", affected_keys=[["gwp_qtextedit_return_pressed_change_qss_stylesheet", "qlineedit"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qtextedit_return_pressed_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),
            # ENTER Pressed - Change Size
            self._title("app_sett_style_gwp_qtextedit_return_pressed_change_size_name"),
            self._checkbox("app_sett_style_textbox_change_size_enabled_style", "gwp_qtextedit_return_pressed_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qtextedit_return_pressed_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qtextedit_return_pressed_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_esc_press_name", title_center=True, font_size=16, bg_color=bg_section_color),
            
            # ESC Pressed - Sound
            self._title("app_sett_style_gwp_qtextedit_escape_pressed_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qtextedit_escape_pressed_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qtextedit_escape_pressed_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),
            # ESC Pressed - Change Stylesheet
            self._title("app_sett_style_gwp_qtextedit_escape_pressed_change_stylesheet_name"),
            self._checkbox("app_sett_style_textbox_stylesheet_enabled_style", "gwp_qtextedit_escape_pressed_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_qtextedit_escape_pressed_change_qss_stylesheet", affected_keys=[["gwp_qtextedit_escape_pressed_change_qss_stylesheet", "qlineedit"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qtextedit_escape_pressed_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),
            # ESC Pressed - Change Size
            self._title("app_sett_style_gwp_qtextedit_escape_pressed_change_size_name"),
            self._checkbox("app_sett_style_textbox_change_size_enabled_style", "gwp_qtextedit_escape_pressed_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qtextedit_escape_pressed_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qtextedit_escape_pressed_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_gwp_smart_parenthesis_name", title_center=True, font_size=16, bg_color=bg_section_color),
            self._title("app_sett_style_gwp_smart_parenthesis_desc_name"),
            self._checkbox("app_sett_style_gwp_qtextedit_smart_parenthesis_enabled_style", "gwp_qtextedit_smart_parenthesis_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),

            # Smart Parenthesis - Sound
            self._title("app_sett_style_gwp_qtextedit_smart_parenthesis_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qtextedit_smart_parenthesis_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qtextedit_smart_parenthesis_success_sound_file_path_style", "gwp_qtextedit_smart_parenthesis_success_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),
            self._combobox("app_sett_style_gwp_qtextedit_smart_parenthesis_fail_sound_file_path_style", "gwp_qtextedit_smart_parenthesis_fail_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),
            # Smart Parenthesis - Change Stylesheet
            self._title("app_sett_style_gwp_qtextedit_smart_parenthesis_change_stylesheet_name"),
            self._checkbox("app_sett_style_textbox_stylesheet_enabled_style", "gwp_qtextedit_smart_parenthesis_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_qtextedit_smart_parenthesis_change_qss_stylesheet", affected_keys=[["gwp_qtextedit_smart_parenthesis_change_qss_stylesheet", "qlineedit"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qtextedit_smart_parenthesis_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),
            # Smart Parenthesis - Change Size
            self._title("app_sett_style_gwp_qtextedit_smart_parenthesis_change_size_name"),
            self._checkbox("app_sett_style_textbox_change_size_enabled_style", "gwp_qtextedit_smart_parenthesis_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qtextedit_smart_parenthesis_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qtextedit_smart_parenthesis_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),

            self._title("app_sett_style_illegal_entry_name", title_center=True, font_size=16, bg_color=bg_section_color),

            # ESC Pressed - Sound
            self._title("app_sett_style_gwp_qtextedit_illegal_entry_sound_name"),
            self._checkbox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_enabled_style", "gwp_qtextedit_illegal_entry_sound_enabled", desc_getl="gwp_qpushbutton_tap_event_play_sound_enabled_desc"),
            self._combobox("app_sett_style_gwp_qpushbutton_tap_event_play_sound_file_path_style", "gwp_qtextedit_illegal_entry_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="gwp_qpushbutton_tap_event_play_sound_file_path_desc"),
            # ESC Pressed - Change Stylesheet
            self._title("app_sett_style_gwp_qtextedit_illegal_entry_change_stylesheet_name"),
            self._checkbox("app_sett_style_textbox_stylesheet_enabled_style", "gwp_qtextedit_illegal_entry_change_stylesheet_enabled", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_enabled_desc"),
            self._style("app_sett_style_widget_stylesheet_style", "gwp_qtextedit_illegal_entry_change_qss_stylesheet", affected_keys=[["gwp_qtextedit_illegal_entry_change_qss_stylesheet", "qlineedit"]]),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_style", "gwp_qtextedit_illegal_entry_change_stylesheet_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_stylesheet_duration_ms_desc"),
            # ESC Pressed - Change Size
            self._title("app_sett_style_gwp_qtextedit_illegal_entry_change_size_name"),
            self._checkbox("app_sett_style_textbox_change_size_enabled_style", "gwp_qtextedit_illegal_entry_change_size_enabled", desc_getl="gwp_qpushbutton_tap_event_change_size_enabled_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_percent_style", "gwp_qtextedit_illegal_entry_change_size_percent", desc_getl="gwp_qpushbutton_tap_event_change_size_percent_desc"),
            self._input("app_sett_style_gwp_qpushbutton_tap_event_change_size_duration_ms_style", "gwp_qtextedit_illegal_entry_change_size_duration_ms", desc_getl="gwp_qpushbutton_tap_event_change_size_duration_ms_desc"),
        ]
        
        item_group_data = self.item_group_empty_dictionary()
        item_group_data["bg_color"] = bg_color_main_section
        item_group_data["fg_color"] = fg_color_main_section
        item_group_data["hover_color"] = hover_color_main_section
        item_group_data["name"] = self.getl("app_sett_style_gwp_textbox_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

    def show_dialog_settings(self, filter: dict = None, populate_archive: bool = False):
        section = self.getl("app_settings_lbl_menu_window_title_text")

        # MainWindow Title
        item_to_add = [
            self._style("app_sett_style_general_win_style", "main_win_stylesheet", affected_keys= "qmainwindow"),
            self._title("app_sett_style_toolBar_name"),
            self._style("app_sett_style_toolBar_stylesheet_style", "toolBar_stylesheet", affected_keys="qtoolbar"),
            self._checkbox("app_sett_style_toolBar_movable_style", "toolBar_movable"),
            self._checkbox("app_sett_style_toolBar_floatable_style", "toolBar_floatable"),
            self._checkbox("app_sett_style_toolBat_enabled_style", "toolBat_enabled"),
            self._checkbox("app_sett_style_toolBar_visible_style", "toolBar_visible"),
            self._title("app_sett_style_toolbar_buttons_name"),
            self._combobox("app_sett_style_toolBar_tool_button_style_style", "toolBar_tool_button_style", cmb_data="toolbar_button_style", input_box_width=200),
            self._style("app_sett_style_button_stylesheet_style", "toolbar_buttons_stylesheet", affected_keys=self._standard_affected_keys("toolbar_buttons_stylesheet", "qtoolbutton")),
            self._title("app_sett_style_statusbar_name"),
            self._style("app_sett_style_sts_bar_stylesheet_style", "sts_bar_stylesheet", affected_keys="qstatusbar"),
            self._input("app_sett_style_sts_bar_fixed_width_style", "sts_bar_fixed_width", input_box_width=60),
            self._input("app_sett_style_sts_bar_fixed_height_style", "sts_bar_fixed_height", input_box_width=60),
            self._checkbox("app_sett_style_sts_bar_visible_style", "sts_bar_visible", recomm_getl="widget_setting_true_recomm")
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_mainwindow_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Selection Dialog
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "selection_win_stylesheet", affected_keys="qdialog"),
            self._input("app_sett_style_widget_margins_style", "selection_win_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_layout_margins_style", "selection_win_layout_contents_margins", validator_type="margins", desc_getl="app_sett_style_margins_style_desc"),
            self._input("app_sett_style_spacing_style", "selection_win_layout_spacing", desc_getl="app_sett_style_spacing_desc"),
            self._checkbox("app_sett_style_selection_show_item_tooltip_style", "selection_show_item_tooltip", desc_getl="selection_show_item_tooltip_desc", recomm_getl="widget_setting_true_recomm"),
            self._combobox("app_sett_style_selection_list_item_alignment_style", "selection_list_item_alignment", cmb_data="align"),
            self._input("app_sett_style_selection_spacer_title-body_height_style", "selection_spacer_title-body_height", desc_getl="selection_spacer_title-body_height_desc", recomm_getl="selection_spacer_title-body_height_recomm"),
            self._input("app_sett_style_selection_spacer_body-footer_height_style", "selection_spacer_body-footer_height", desc_getl="selection_spacer_body-footer_height_desc"),
            self._checkbox("app_sett_style_show_titlebar_style", "selection_win_show_titlebar", desc_getl="app_sett_style_win_show_titlebar_desc", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "selection_lbl_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "selection_lbl_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "selection_lbl_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "selection_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("selection_lbl_title", "qlabel")),

            self._title("app_sett_style_selection_lbl_count_name"),
            self._combobox("app_sett_style_frame_shape_style", "selection_lbl_count_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "selection_lbl_count_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "selection_lbl_count_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "selection_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("selection_lbl_count", "qlabel")),

            self._title("app_sett_style_selection_lst_name"),
            self._combobox("app_sett_style_frame_shape_style", "selection_lst_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "selection_lst_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "selection_lst_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "selection_lst_stylesheet", affected_keys=self._standard_affected_keys("selection_lst", "qlistwidget")),

            self._title("app_sett_style_selection_btn_select_all_name"),
            self._checkbox("app_sett_style_button_flat_style", "selection_btn_select_all_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "selection_btn_select_all_stylesheet", affected_keys=self._standard_affected_keys("selection_btn_select_all_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "selection_btn_select_all_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "selection_btn_select_all_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_button_visible_style", "selection_btn_select_all_visible", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_selection_btn_clear_all_name"),
            self._checkbox("app_sett_style_button_flat_style", "selection_btn_clear_all_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "selection_btn_clear_all_stylesheet", affected_keys=self._standard_affected_keys("selection_btn_clear_all_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "selection_btn_clear_all_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "selection_btn_clear_all_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_button_visible_style", "selection_btn_clear_all_visible", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_btn_confirm_name"),
            self._checkbox("app_sett_style_button_flat_style", "selection_btn_select_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "selection_btn_select_stylesheet", affected_keys=self._standard_affected_keys("selection_btn_select_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "selection_btn_select_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "selection_btn_select_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "selection_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "selection_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("selection_btn_cancel", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "selection_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "selection_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_selection_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Definition Add
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "definition_add_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "definition_add_win_icon_path", cmb_data="icon", input_box_width=-1),
            self._input("app_sett_style_definition_image_thumb_size_style", "definition_image_thumb_size"),
            self._checkbox("app_sett_style_definition_add_remove_wiki_style", "definition_add_remove_wiki_[]_from_description", recomm_getl="widget_setting_true_recomm"),
            
            self._title("app_sett_style_def_add_sounds_name"),
            self._combobox("app_sett_style_def_add_auto_added_image_sound_style", "def_add_auto_added_image_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_def_add_auto_added_image_error_sound_style", "def_add_auto_added_image_error_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_def_add_auto_added_image_on_sound_style", "def_add_auto_added_image_on_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_def_add_auto_added_image_off_sound_style", "def_add_auto_added_image_off_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_def_add_auto_added_image_maximum_sound_style", "def_add_auto_added_image_maximum_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_completed_sound_file_path_style", "completed_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),
            self._combobox("app_sett_style_select_sound_file_path_style", "select_sound_file_path", cmb_data="sound", input_box_width=-1, desc_getl="app_sett_style_sound_desc"),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "definition_add_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "definition_add_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "definition_add_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "definition_add_title_stylesheet", affected_keys=self._standard_affected_keys("definition_add_title_stylesheet", "qlabel")),

            self._title("app_sett_style_definition_add_lbl_loading_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_add_lbl_loading_stylesheet", affected_keys=self._standard_affected_keys("definition_add_lbl_loading_stylesheet", "qlabel")),

            self._title("app_sett_style_definition_txt_expr_name"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_txt_expr_stylesheet", affected_keys=self._standard_affected_keys("definition_txt_expr_stylesheet", "qlineedit")),
            self._style("app_sett_style_definition_txt_expr_exist_stylesheet_style", "definition_txt_expr_exist_stylesheet", affected_keys=self._standard_affected_keys("definition_txt_expr_exist_stylesheet", "qlineedit")),
            self._style("app_sett_style_definition_txt_expr_illegal_stylesheet_style", "definition_txt_expr_illegal_stylesheet", affected_keys=self._standard_affected_keys("definition_txt_expr_illegal_stylesheet", "qlineedit")),
            self._style("app_sett_style_definition_txt_expr_part_of_other_def_stylesheet_style", "definition_txt_expr_part_of_other_def_stylesheet", affected_keys=self._standard_affected_keys("definition_txt_expr_part_of_other_def_stylesheet", "qlineedit")),

            self._title("app_sett_style_definition_add_lbl_syn_name"),
            self._combobox("app_sett_style_frame_shape_style", "definition_txt_syn_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "definition_txt_syn_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "definition_txt_syn_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_txt_syn_stylesheet", affected_keys=self._standard_affected_keys("definition_txt_syn_stylesheet", "qtextedit")),

            self._title("app_sett_style_ddefinition_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "definition_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "definition_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "definition_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("definition_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_definition_add_btn_format_desc_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_add_btn_format_desc_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_add_btn_format_desc_stylesheet", affected_keys=self._standard_affected_keys("definition_add_btn_format_desc_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_add_btn_format_desc_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_add_btn_format_desc_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_add_btn_editor_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_add_btn_editor_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_add_btn_editor_stylesheet", affected_keys=self._standard_affected_keys("definition_add_btn_editor_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_add_btn_editor_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_add_btn_editor_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_add_chk_auto_add_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_add_chk_auto_add_stylesheet", affected_keys=self._standard_affected_keys("definition_add_chk_auto_add_stylesheet", "qcheckbox")),

            self._title("app_sett_style_definition_add_btn_media_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_add_btn_media_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_add_btn_media_stylesheet", affected_keys=self._standard_affected_keys("definition_add_btn_media_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_add_btn_media_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_add_btn_media_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_add_btn_save_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_add_btn_save_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_add_btn_save_stylesheet", affected_keys=self._standard_affected_keys("definition_add_btn_save_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_add_btn_save_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_add_btn_save_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_add_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_add_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_add_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("definition_add_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_add_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_add_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_add_def_finder_name", title_center=True),

            self._title("app_sett_style_definition_add_def_finder_prefix_and_suffix_name"),
            self._input("app_sett_style_definition_add_def_finder_prefix_style", "definition_data_find_search_prefix"),
            self._input("app_sett_style_definition_add_def_finder_suffix_style", "definition_data_find_search_suffix"),

            self._title("app_sett_style_definition_finder_logo_animation_path_name"),
            self._combobox("app_sett_style_definition_finder_logo_animation_path_style", "definition_finder_logo_animation_path", cmb_data="animation", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_definition_add_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Definition Editor
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "definition_editor_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "definition_editor_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "def_editor_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_description_labels_name"),
            self._style("app_sett_style_def_editor_lbl_base_stylesheet_style", "def_editor_lbl_base_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_base_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_output_stylesheet_style", "def_editor_lbl_output_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_output_stylesheet", "qlabel")),


            self._title("app_sett_style_def_editor_txt_base_name"),
            self._style("app_sett_style_widget_stylesheet_style", "def_editor_txt_base_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_base_stylesheet", "qlineedit")),

            self._title("app_sett_style_def_editor_btn_first_letter_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_first_letter_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_first_letter_stylesheet", "qpushbutton")),

            self._title("app_sett_style_def_editor_txt_output_name"),
            self._style("app_sett_style_widget_stylesheet_style", "def_editor_txt_output_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_output_stylesheet", "qtextedit")),

            self._title("app_sett_style_def_editor_btn_switch_words_order_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_switch_words_order_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_switch_words_order_stylesheet", "qpushbutton")),

            self._title("app_sett_style_def_editor_txt_end_name"),
            self._style("app_sett_style_widget_stylesheet_style", "def_editor_txt_end_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_end_stylesheet", "qtextedit")),

            self._title("app_sett_style_def_editor_txt_beggining_name"),
            self._style("app_sett_style_widget_stylesheet_style", "def_editor_txt_beggining_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_beggining_stylesheet", "qtextedit")),

            self._title("app_sett_style_def_editor_checkboxes_name"),
            self._style("app_sett_style_widget_stylesheet_style", "def_editor_checkboxes_stylesheet", affected_keys=self._standard_affected_keys("def_editor_checkboxes_stylesheet", "qcheckbox")),

            self._title("app_sett_style_def_editor_btn_edit_output_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_edit_output_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_output_stylesheet", "qpushbutton")),

            self._title("app_sett_style_def_editor_btn_generate_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_generate_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_generate_stylesheet", "qpushbutton")),

            self._title("app_sett_style_def_editor_btn_copy_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_copy_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_copy_stylesheet", "qpushbutton")),

            self._title("app_sett_style_def_editor_btn_clear_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_clear_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_clear_stylesheet", "qpushbutton")),

            self._title("app_sett_style_picture_browse_btn_close_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_editor_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_cancel_stylesheet", "qpushbutton")),

            self._title("app_sett_style_edit_output_labels_name", title_center=True, font_size=14, font_shrink=2),
            self._style("app_sett_style_def_editor_lbl_edit_replace_stylesheet_style", "def_editor_lbl_edit_replace_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_edit_replace_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_edit_with_stylesheet_style", "def_editor_lbl_edit_with_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_edit_with_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_edit_in_string_stylesheet_style", "def_editor_lbl_edit_in_string_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_edit_in_string_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_edit_add_beg_stylesheet_style", "def_editor_lbl_edit_add_beg_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_edit_add_beg_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_edit_add_end_stylesheet_style", "def_editor_lbl_edit_add_end_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_edit_add_end_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_edit_msg_stylesheet_style", "def_editor_lbl_edit_msg_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_edit_msg_stylesheet", "qlabel")),
            self._style("app_sett_style_def_editor_lbl_msg_spaces_stylesheet_style", "def_editor_lbl_msg_spaces_stylesheet", affected_keys=self._standard_affected_keys("def_editor_lbl_msg_spaces_stylesheet", "qlabel")),

            self._title("app_sett_style_edit_output_buttons_name", title_center=True, font_size=14, font_shrink=2),
            self._style("app_sett_style_def_editor_btn_edit_replace_stylesheet_style", "def_editor_btn_edit_replace_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_replace_stylesheet", "qpushbutton")),
            self._style("app_sett_style_def_editor_btn_edit_replace_add_stylesheet_style", "def_editor_btn_edit_replace_add_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_replace_add_stylesheet", "qpushbutton")),
            self._style("app_sett_style_def_editor_btn_edit_case_stylesheet_style", "def_editor_btn_edit_case_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_case_stylesheet", "qpushbutton")),
            self._style("app_sett_style_def_editor_btn_edit_add_beg_stylesheet_style", "def_editor_btn_edit_add_beg_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_add_beg_stylesheet", "qpushbutton")),
            self._style("app_sett_style_def_editor_btn_edit_add_end_stylesheet_style", "def_editor_btn_edit_add_end_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_add_end_stylesheet", "qpushbutton")),
            self._style("app_sett_style_def_editor_btn_edit_spaces_stylesheet_style", "def_editor_btn_edit_spaces_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_spaces_stylesheet", "qpushbutton")),
            self._style("app_sett_style_def_editor_btn_edit_close_stylesheet_style", "def_editor_btn_edit_close_stylesheet", affected_keys=self._standard_affected_keys("def_editor_btn_edit_close_stylesheet", "qpushbutton")),

            self._title("app_sett_style_edit_output_checkboxes_name", title_center=True, font_size=14, font_shrink=2),
            self._style("app_sett_style_def_editor_chk_edit_case_stylesheet_style", "def_editor_chk_edit_case_stylesheet", affected_keys=self._standard_affected_keys("def_editor_chk_edit_case_stylesheet", "qcheckbox")),

            self._title("app_sett_style_edit_output_textboxes_name", title_center=True, font_size=14, font_shrink=2),
            self._style("app_sett_style_def_editor_lbl_edit_replace_stylesheet_style", "def_editor_txt_edit_replace_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_edit_replace_stylesheet", "qlineedit")),
            self._style("app_sett_style_def_editor_lbl_edit_with_stylesheet_style", "def_editor_txt_edit_with_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_edit_with_stylesheet", "qlineedit")),
            self._style("app_sett_style_def_editor_lbl_edit_in_string_stylesheet_style", "def_editor_txt_edit_in_string_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_edit_in_string_stylesheet", "qlineedit")),
            self._style("app_sett_style_def_editor_lbl_edit_add_beg_stylesheet_style", "def_editor_txt_edit_add_beg_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_edit_add_beg_stylesheet", "qlineedit")),
            self._style("app_sett_style_def_editor_lbl_edit_add_end_stylesheet_style", "def_editor_txt_edit_add_end_stylesheet", affected_keys=self._standard_affected_keys("def_editor_txt_edit_add_end_stylesheet", "qlineedit")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_definition_editor_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Definition view
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "definition_view_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "definition_view_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_view_name_name"),
            self._combobox("app_sett_style_frame_shape_style", "definition_view_name_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "definition_view_name_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "definition_view_name_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_view_name_stylesheet", affected_keys=self._standard_affected_keys("definition_view_name_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "definition_view_name_visible"),

            self._title("app_sett_style_definition_view_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "definition_view_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "definition_view_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "definition_view_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "definition_view_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("definition_view_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_definition_view_btn_edit_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_view_btn_edit_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_view_btn_edit_stylesheet", affected_keys=self._standard_affected_keys("definition_view_btn_edit_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_view_btn_edit_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_view_btn_edit_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_view_btn_size_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_view_btn_size_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_view_btn_size_stylesheet", affected_keys=self._standard_affected_keys("definition_view_btn_size_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "definition_view_btn_size_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_definition_view_btn_ok_name"),
            self._checkbox("app_sett_style_button_flat_style", "definition_view_btn_ok_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "definition_view_btn_ok_stylesheet", affected_keys=self._standard_affected_keys("definition_view_btn_ok_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "definition_view_btn_ok_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "definition_view_btn_ok_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_definition_view_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Definition Browse
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "browse_def_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "browse_def_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "browse_def_lbl_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "browse_def_lbl_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "browse_def_lbl_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "browse_def_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("browse_def_lbl_title_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "browse_def_lbl_title_visible"),

            self._title("app_sett_style_browse_def_lbl_count_name"),
            self._combobox("app_sett_style_frame_shape_style", "browse_def_lbl_count_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "browse_def_lbl_count_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "browse_def_lbl_count_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "browse_def_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("browse_def_lbl_count_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "browse_def_lbl_count_visible"),

            self._title("app_sett_style_browse_def_lst_def_name"),
            self._style("app_sett_style_widget_stylesheet_style", "browse_def_lst_def_stylesheet", affected_keys=self._standard_affected_keys("tag_view_lst_tags_stylesheet", "qlistwidget")),

            self._title("app_sett_style_browse_def_txt_find_name"),
            self._style("app_sett_style_widget_stylesheet_style", "browse_def_txt_find_stylesheet", affected_keys=self._standard_affected_keys("browse_def_txt_find_stylesheet", "qlineedit")),

            self._title("app_sett_style_browse_def_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "browse_def_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "browse_def_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "browse_def_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "browse_def_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("browse_def_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_browse_def_lbl_name_name"),
            self._combobox("app_sett_style_frame_shape_style", "browse_def_lbl_name_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "browse_def_lbl_name_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "browse_def_lbl_name_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "browse_def_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("browse_def_lbl_name_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "browse_def_lbl_name_visible"),

            self._title("app_sett_style_browse_def_btn_add_name"),
            self._checkbox("app_sett_style_button_flat_style", "browse_def_btn_add_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "browse_def_btn_add_stylesheet", affected_keys=self._standard_affected_keys("browse_def_btn_add_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "browse_def_btn_add_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "browse_def_btn_add_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_browse_def_btn_edit_name"),
            self._checkbox("app_sett_style_button_flat_style", "browse_def_btn_edit_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "browse_def_btn_edit_stylesheet", affected_keys=self._standard_affected_keys("browse_def_btn_edit_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "browse_def_btn_edit_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "browse_def_btn_edit_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_browse_def_btn_delete_name"),
            self._checkbox("app_sett_style_button_flat_style", "browse_def_btn_delete_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "browse_def_btn_delete_stylesheet", affected_keys=self._standard_affected_keys("browse_def_btn_delete_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "browse_def_btn_delete_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "browse_def_btn_delete_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_browse_def_btn_close_name"),
            self._checkbox("app_sett_style_button_flat_style", "browse_def_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "browse_def_btn_close_stylesheet", affected_keys=self._standard_affected_keys("browse_def_btn_close_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "browse_def_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "browse_def_btn_close_icon_path", cmb_data="icon", input_box_width=-1)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_browse_def_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Find Definition online from selected text in block
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "find_def_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "find_def_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "find_def_lbl_name_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "find_def_lbl_name_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "find_def_lbl_name_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "find_def_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_name_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "find_def_lbl_name_visible"),

            self._title("app_sett_style_find_def_lbl_pic_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_def_lbl_pic_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_pic_stylesheet", "qlabel")),
            self._combobox("app_sett_style_find_def_lbl_pic_icon_style", "find_def_lbl_pic_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_find_def_lbl_pic2_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_def_lbl_pic2_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_pic2_stylesheet", "qlabel")),

            self._title("app_sett_style_find_def_lbl_pic3_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_def_lbl_pic3_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_pic3_stylesheet", "qlabel")),

            self._title("app_sett_style_find_def_lst_pages_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_def_lst_pages_stylesheet", affected_keys=self._standard_affected_keys("find_def_lst_pages_stylesheet", "qlistwidget")),

            self._title("app_sett_style_find_def_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "find_def_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "find_def_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "find_def_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "find_def_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("find_def_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_find_def_lbl_load_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_def_lbl_load_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_load_stylesheet", "qlabel")),

            self._title("app_sett_style_find_def_btn_edit_name"),
            self._checkbox("app_sett_style_button_flat_style", "find_def_btn_edit_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "find_def_btn_edit_stylesheet", affected_keys=self._standard_affected_keys("find_def_btn_edit_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "find_def_btn_edit_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "find_def_btn_edit_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "find_def_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "find_def_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("find_def_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "find_def_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "find_def_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_find_def_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Synonims Manager
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "synonyms_manager_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "synonyms_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "synonyms_manager_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_synonyms_manager_lbl_shema_name_stylesheet_style", "synonyms_manager_lbl_shema_name_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_lbl_shema_name_stylesheet", "qlabel")),
            self._style("app_sett_style_synonyms_manager_lbl_suff_stylesheet_style", "synonyms_manager_lbl_suff_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_lbl_suff_stylesheet", "qlabel")),
            self._style("app_sett_style_synonyms_manager_lbl_count_stylesheet_style", "synonyms_manager_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_lbl_count_stylesheet", "qlabel")),
            self._style("app_sett_style_synonyms_manager_lbl_additional_stylesheet_style", "synonyms_manager_lbl_additional_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_lbl_additional_stylesheet", "qlabel")),

            self._title("app_sett_style_synonyms_manager_lst_shema_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "synonyms_manager_lst_shema_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_lst_shema_stylesheet", "qlistwidget")),

            self._title("app_sett_style_synonyms_manager_txt_find_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "synonyms_manager_txt_find_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_txt_find_stylesheet", "qlineedit")),

            self._title("app_sett_style_synonyms_manager_txt_name_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "synonyms_manager_txt_name_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_txt_name_stylesheet", "qlineedit")),

            self._title("app_sett_style_synonyms_manager_txt_suff_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "synonyms_manager_txt_suff_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_txt_suff_stylesheet", "qtextedit")),

            self._title("app_sett_style_synonyms_manager_txt_additional_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "synonyms_manager_txt_additional_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_txt_additional_stylesheet", "qtextedit")),

            self._title("app_sett_style_synonyms_manager_btn_additional_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "synonyms_manager_btn_additional_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_btn_additional_stylesheet", "qpushbutton")),

            self._title("app_sett_style_synonyms_manager_btn_update_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "synonyms_manager_btn_update_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_btn_update_stylesheet", "qpushbutton")),

            self._title("app_sett_style_synonyms_manager_btn_add_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "synonyms_manager_btn_add_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_btn_add_stylesheet", "qpushbutton")),

            self._title("app_sett_style_synonyms_manager_btn_copy_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "synonyms_manager_btn_copy_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_btn_copy_stylesheet", "qpushbutton")),

            self._title("app_sett_style_synonyms_manager_btn_delete_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "synonyms_manager_btn_delete_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_btn_delete_stylesheet", "qpushbutton")),

            self._title("app_sett_style_btn_cancel_name"),
            self._style("app_sett_style_button_stylesheet_style", "synonyms_manager_btn_close_stylesheet", affected_keys=self._standard_affected_keys("synonyms_manager_btn_close_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_synonyms_manager_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Definition Hint Manager
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "def_hint_manager_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "def_hint_manager_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "def_hint_manager_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("def_hint_manager_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_def_hint_manager_cmb_sort_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "def_hint_manager_cmb_sort_stylesheet", affected_keys=self._standard_affected_keys("def_hint_manager_cmb_sort_stylesheet", "qcombobox")),

            self._title("app_sett_style_def_hint_manager_txt_expressions_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_hint_manager_txt_expressions_stylesheet", affected_keys=self._standard_affected_keys("def_hint_manager_txt_expressions_stylesheet", "qtextedit")),

            self._title("app_sett_style_def_hint_manager_lbl_count_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_hint_manager_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("def_hint_manager_lbl_count_stylesheet", "qlabel")),

            self._title("app_sett_style_def_hint_manager_btn_save_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_hint_manager_btn_save_stylesheet", affected_keys=self._standard_affected_keys("def_hint_manager_btn_save_stylesheet", "qpushbutton")),

            self._title("app_sett_style_btn_cancel_name"),
            self._style("app_sett_style_button_stylesheet_style", "def_hint_manager_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("def_hint_manager_btn_cancel_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_def_hint_manager_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Picture add
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "picture_add_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "picture_add_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "picture_add_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "picture_add_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "picture_add_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "picture_add_title_stylesheet", affected_keys=self._standard_affected_keys("picture_add_title_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_add_chk_auto_load_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_add_chk_auto_load_stylesheet", affected_keys=self._standard_affected_keys("picture_add_chk_auto_load_stylesheet", "qcheckbox")),

            self._title("app_sett_style_picture_add_txt_file_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_add_txt_file_stylesheet", affected_keys=self._standard_affected_keys("picture_add_txt_file_stylesheet", "qlineedit")),

            self._title("app_sett_style_picture_add_lbl_file_name"),
            self._combobox("app_sett_style_frame_shape_style", "picture_add_lbl_file_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "picture_add_lbl_file_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "picture_add_lbl_file_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_add_lbl_file_stylesheet", affected_keys=self._standard_affected_keys("picture_add_lbl_file_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "picture_add_lbl_file_visible"),

            self._title("app_sett_style_picture_add_btn_file_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_add_btn_file_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_add_btn_file_stylesheet", affected_keys=self._standard_affected_keys("picture_add_btn_file_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_add_btn_file_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_add_btn_file_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_add_btn_show_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_add_btn_show_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_add_btn_show_stylesheet", affected_keys=self._standard_affected_keys("picture_add_btn_show_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_add_btn_show_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_add_btn_show_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_add_btn_add_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_add_btn_add_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_add_btn_add_stylesheet", affected_keys=self._standard_affected_keys("picture_add_btn_add_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_add_btn_add_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_add_btn_add_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_add_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_add_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_add_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("picture_add_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_add_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_add_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_picture_add_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Picture view
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "picture_view_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "picture_view_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_view_lbl_name_name"),
            self._combobox("app_sett_style_frame_shape_style", "picture_view_lbl_name_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "picture_view_lbl_name_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "picture_view_lbl_name_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_view_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("picture_view_lbl_name_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "picture_view_lbl_name_visible"),

            self._title("app_sett_style_picture_view_txt_name_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_view_txt_name_stylesheet", affected_keys=self._standard_affected_keys("picture_view_txt_name_stylesheet", "qlineedit")),

            self._title("app_sett_style_picture_view_lbl_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "picture_view_lbl_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "picture_view_lbl_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "picture_view_lbl_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_view_lbl_desc_stylesheet", affected_keys=self._standard_affected_keys("picture_view_lbl_desc_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "picture_view_lbl_desc_visible"),

            self._title("app_sett_style_picture_view_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "picture_view_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "picture_view_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "picture_view_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_view_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("picture_view_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_picture_view_btn_next_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_view_btn_next_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_view_btn_next_stylesheet", affected_keys=self._standard_affected_keys("picture_view_btn_next_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_view_btn_next_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_view_btn_next_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_view_btn_save_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_view_btn_save_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_view_btn_save_stylesheet", affected_keys=self._standard_affected_keys("picture_view_btn_save_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_view_btn_save_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_view_btn_save_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_add_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_view_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_view_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("picture_view_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_view_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_view_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_picture_view_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Picture Browse
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "picture_browse_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "picture_browse_win_icon_path", cmb_data="icon", input_box_width=-1),
            self._input("app_sett_style_picture_browse_item_size_style", "picture_browse_item_size"),
            self._input("app_sett_style_picture_browse_items_in_row_style", "picture_browse_items_in_row"),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "picture_browse_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_area_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_area_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_area_stylesheet", "qscrollarea")),
            
            self._title("app_sett_style_picture_browse_lbl_name_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_name_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_txt_name_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_txt_name_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_txt_name_stylesheet", "qlineedit")),

            self._title("app_sett_style_picture_browse_lbl_desc_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_desc_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_desc_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "picture_browse_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "picture_browse_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "picture_browse_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_picture_browse_lbl_file_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_file_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_file_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_lbl_file_val_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_file_val_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_file_val_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_lbl_src_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_src_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_src_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_lbl_src_val_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_src_val_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_src_val_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_lbl_count_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_browse_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_lbl_count_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_browse_btn_delete_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_browse_btn_delete_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_browse_btn_delete_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_btn_delete_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_browse_btn_delete_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_browse_btn_delete_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_browse_btn_update_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_browse_btn_update_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_browse_btn_update_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_btn_update_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_browse_btn_update_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_browse_btn_update_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_browse_btn_close_name"),
            self._checkbox("app_sett_style_button_flat_style", "picture_browse_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "picture_browse_btn_close_stylesheet", affected_keys=self._standard_affected_keys("picture_browse_btn_close_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "picture_browse_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "picture_browse_btn_close_icon_path", cmb_data="icon", input_box_width=-1)
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_picture_browse_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Image Information
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "picture_info_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "picture_info_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_picture_info_lbl_pic_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_info_lbl_pic_stylesheet", affected_keys=self._standard_affected_keys("picture_info_lbl_pic_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_info_lbl_used_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_info_lbl_used_stylesheet", affected_keys=self._standard_affected_keys("picture_info_lbl_used_stylesheet", "qlabel")),

            self._title("app_sett_style_picture_info_lst_used_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "picture_info_lst_used_stylesheet", affected_keys=self._standard_affected_keys("picture_info_lst_used_stylesheet", "qlistwidget")),

            self._title("app_sett_style_pic_info_lbl_created_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "pic_info_lbl_created_stylesheet", affected_keys=self._standard_affected_keys("pic_info_lbl_created_stylesheet", "qlabel")),
            self._input("app_sett_style_pic_info_lbl_created_date_color_style", "pic_info_lbl_created_date_color", validator_type="color"),
       ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_picture_info_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Add File in block
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "file_add_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "file_add_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "file_add_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("file_add_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_file_add_lbl_file_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_add_lbl_file_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_pic_stylesheet", "qlabel")),

            self._title("app_sett_style_file_add_txt_file_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_add_txt_file_stylesheet", affected_keys=self._standard_affected_keys("file_add_txt_file_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_add_lbl_select_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_add_lbl_select_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_pic_stylesheet", "qlabel")),

            self._title("app_sett_style_file_add_lst_select_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_add_lst_select_stylesheet", affected_keys=self._standard_affected_keys("file_add_lst_select_stylesheet", "qlistwidget")),

            self._title("app_sett_style_file_add_lbl_count_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_add_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("find_def_lbl_pic_stylesheet", "qlabel")),
            
            self._title("app_sett_style_file_add_btn_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_add_btn_file_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_add_btn_file_stylesheet", affected_keys=self._standard_affected_keys("file_add_btn_file_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_add_btn_file_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_add_btn_file_icon_path", cmb_data="icon", input_box_width=-1),
            
            self._title("app_sett_style_file_add_btn_add_to_list_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_add_btn_add_to_list_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_add_btn_add_to_list_stylesheet", affected_keys=self._standard_affected_keys("file_add_btn_add_to_list_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_add_btn_add_to_list_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_add_btn_add_to_list_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_file_add_btn_add_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_add_btn_add_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_add_btn_add_stylesheet", affected_keys=self._standard_affected_keys("file_add_btn_add_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_add_btn_add_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_add_btn_add_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_add_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_add_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("file_add_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_add_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_add_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_file_add_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # File Information
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "file_info_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "file_info_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "file_info_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_file_info_lbl_title_desc_stylesheet_style", "file_info_lbl_title_desc_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_title_desc_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_name_stylesheet_style", "file_info_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_name_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_desc_stylesheet_style", "file_info_lbl_desc_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_desc_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_icon_stylesheet_style", "file_info_lbl_icon_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_icon_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_ext_stylesheet_style", "file_info_lbl_ext_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_ext_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_file_type_stylesheet_style", "file_info_lbl_file_type_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_file_type_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_file_path_stylesheet_style", "file_info_lbl_file_path_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_file_path_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_def_app_stylesheet_style", "file_info_lbl_def_app_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_def_app_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_file_src_stylesheet_style", "file_info_lbl_file_src_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_file_src_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_size_stylesheet_style", "file_info_lbl_size_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_size_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_created_stylesheet_style", "file_info_lbl_created_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_created_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_modified_stylesheet_style", "file_info_lbl_modified_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_modified_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_accessed_stylesheet_style", "file_info_lbl_accessed_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_accessed_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_size_val_stylesheet_style", "file_info_lbl_size_val_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_size_val_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_created_val_stylesheet_style", "file_info_lbl_created_val_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_created_val_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_modified_val_stylesheet_style", "file_info_lbl_modified_val_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_modified_val_stylesheet", "qlabel")),
            self._style("app_sett_style_file_info_lbl_accessed_val_stylesheet_style", "file_info_lbl_accessed_val_stylesheet", affected_keys=self._standard_affected_keys("file_info_lbl_accessed_val_stylesheet", "qlabel")),

            self._title("app_sett_style_file_info_txt_name_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_info_txt_name_stylesheet", affected_keys=self._standard_affected_keys("file_info_txt_name_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_info_txt_desc_name"),
            self._combobox("app_sett_style_frame_shape_style", "file_info_txt_desc_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "file_info_txt_desc_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "file_info_txt_desc_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "file_info_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("file_info_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_file_info_txt_file_type_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_info_txt_file_type_stylesheet", affected_keys=self._standard_affected_keys("file_info_txt_file_type_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_info_txt_def_app_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_info_txt_def_app_stylesheet", affected_keys=self._standard_affected_keys("file_info_txt_def_app_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_info_txt_file_path_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_info_txt_file_path_stylesheet", affected_keys=self._standard_affected_keys("file_info_txt_file_path_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_info_txt_file_src_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "file_info_txt_file_src_stylesheet", affected_keys=self._standard_affected_keys("file_info_txt_file_src_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_info_btn_update_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_info_btn_update_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_info_btn_update_stylesheet", affected_keys=self._standard_affected_keys("file_info_btn_update_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_info_btn_update_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_info_btn_update_icon_path", cmb_data="icon", input_box_width=-1),
            
            self._title("app_sett_style_file_info_btn_save_as_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_info_btn_save_as_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_info_btn_save_as_stylesheet", affected_keys=self._standard_affected_keys("file_info_btn_save_as_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_info_btn_save_as_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_info_btn_save_as_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_file_info_btn_open_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_info_btn_open_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_info_btn_open_stylesheet", affected_keys=self._standard_affected_keys("file_info_btn_open_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_info_btn_open_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_info_btn_open_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "file_info_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "file_info_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("file_info_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "file_info_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "file_info_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_file_info_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Tag view
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "tag_view_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "tag_view_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "tag_view_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("tag_view_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_tag_view_frm_info_name"),
            self._combobox("app_sett_style_frame_shape_style", "tag_view_frm_info_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "tag_view_frm_info_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "tag_view_frm_info_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_frm_info_stylesheet", affected_keys=self._standard_affected_keys("tag_view_frm_info_stylesheet", "qframe")),

            self._title("app_sett_style_tag_view_lbl_info_name"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_lbl_info_stylesheet", affected_keys=self._standard_affected_keys("tag_view_lbl_info_stylesheet", "qlabel")),

            self._title("app_sett_style_tag_view_lbl_name_name"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("tag_view_lbl_name_stylesheet", "qlabel")),

            self._title("app_sett_style_tag_view_lbl_desc_name"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_lbl_desc_stylesheet", affected_keys=self._standard_affected_keys("tag_view_lbl_desc_stylesheet", "qlabel")),

            self._title("app_sett_style_tag_view_btn_apply_name"),
            self._style("app_sett_style_button_stylesheet_style", "tag_view_btn_apply_stylesheet", affected_keys=self._standard_affected_keys("tag_view_btn_apply_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "tag_view_btn_apply_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_tag_view_btn_delete_name"),
            self._style("app_sett_style_button_stylesheet_style", "tag_view_btn_delete_stylesheet", affected_keys=self._standard_affected_keys("tag_view_btn_delete_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "tag_view_btn_delete_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_tag_view_btn_add_name"),
            self._style("app_sett_style_button_stylesheet_style", "tag_view_btn_add_stylesheet", affected_keys=self._standard_affected_keys("tag_view_btn_add_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "tag_view_btn_add_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_tag_view_btn_cancel_name"),
            self._style("app_sett_style_button_stylesheet_style", "tag_view_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("tag_view_btn_cancel_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "tag_view_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_tag_view_txt_name_name"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_txt_name_stylesheet", affected_keys=self._standard_affected_keys("tag_view_txt_name_stylesheet", "qlineedit")),

            self._title("app_sett_style_tag_view_txt_desc_name"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_txt_desc_stylesheet", affected_keys=self._standard_affected_keys("tag_view_txt_desc_stylesheet", "qtextedit")),

            self._title("app_sett_style_tag_view_lst_tags_name"),
            self._style("app_sett_style_widget_stylesheet_style", "tag_view_lst_tags_stylesheet", affected_keys=self._standard_affected_keys("tag_view_lst_tags_stylesheet", "qlistwidget")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_tag_view_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Translator dialog
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "translate_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "translate_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "translate_lbl_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "translate_lbl_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "translate_lbl_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "translate_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("translate_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_translate_lbl_from_to_name"),
            self._combobox("app_sett_style_frame_shape_style", "translate_lbl_from_to_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "translate_lbl_from_to_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "translate_lbl_from_to_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "translate_lbl_from_to_stylesheet", affected_keys=self._standard_affected_keys("translate_lbl_from_to_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "translate_lbl_from_to_visible"),

            self._title("app_sett_style_translate_lbl_detected_name"),
            self._combobox("app_sett_style_frame_shape_style", "translate_lbl_detected_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "translate_lbl_detected_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "translate_lbl_detected_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "translate_lbl_detected_stylesheet", affected_keys=self._standard_affected_keys("translate_lbl_detected_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "translate_lbl_detected_visible"),

            self._title("app_sett_style_translate_btn_trans_name"),
            self._checkbox("app_sett_style_button_flat_style", "translate_btn_trans_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "translate_btn_trans_stylesheet", affected_keys=self._standard_affected_keys("translate_btn_trans_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "translate_btn_trans_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "translate_btn_trans_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_translate_btn_switch_name"),
            self._checkbox("app_sett_style_button_flat_style", "translate_btn_switch_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "translate_btn_switch_stylesheet", affected_keys=self._standard_affected_keys("translate_btn_switch_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "translate_btn_switch_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "translate_btn_switch_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_translate_btn_detect_name"),
            self._checkbox("app_sett_style_button_flat_style", "translate_btn_detect_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "translate_btn_detect_stylesheet", affected_keys=self._standard_affected_keys("translate_btn_detect_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "translate_btn_detect_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "translate_btn_detect_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_translate_txt_from_to_name"),
            self._combobox("app_sett_style_frame_shape_style", "translate_txt_from_to_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "translate_txt_from_to_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "translate_txt_from_to_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "translate_txt_from_to_stylesheet", affected_keys=self._standard_affected_keys("translate_txt_from_to_stylesheet", "qtextedit")),

            self._title("app_sett_style_translate_cmb_from_to_name"),
            self._style("app_sett_style_widget_stylesheet_style", "translate_cmb_from_to_stylesheet", affected_keys=self._standard_affected_keys("translate_cmb_from_to_stylesheet", "qcombobox")),

            self._title("app_sett_style_translate_chk_latin_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "translate_chk_latin_stylesheet", affected_keys=self._standard_affected_keys("translate_chk_latin_stylesheet", "qcheckbox")),

            self._title("app_sett_style_translate_translate_chk_auto_paste_and_copy_stylesheet_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "translate_chk_auto_paste_and_copy_stylesheet", affected_keys=self._standard_affected_keys("translate_chk_auto_paste_and_copy_stylesheet", "qcheckbox")),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "translate_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "translate_btn_close_stylesheet", affected_keys=self._standard_affected_keys("translate_btn_close_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "translate_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "translate_btn_close_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_translate_dialog_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Blocks Browser
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "block_view_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "block_view_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_block_view_list_show_name"),
            self._checkbox("app_sett_style_block_view_list_show_date_style", "block_view_list_show_date"),
            self._checkbox("app_sett_style_block_view_list_show_tags_style", "block_view_list_show_tags"),
            self._checkbox("app_sett_style_block_view_list_show_name_style", "block_view_list_show_name"),
            self._checkbox("app_sett_style_block_view_list_show_body_style", "block_view_list_show_body"),
            self._checkbox("app_sett_style_block_view_list_show_body_in_tooltip_style", "block_view_list_show_body_in_tooltip"),

            self._title("app_sett_style_block_view_list_item_image_icon_path_name"),
            self._combobox("app_sett_style_select_icon_image_style", "block_view_list_item_image_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_block_mark_colors_name"),
            self._input("app_sett_style_block_view_fore_color_main_win_style", "block_view_fore_color_main_win", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_back_color_main_win_style", "block_view_back_color_main_win", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_fore_color_view_win_style", "block_view_fore_color_view_win", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_back_color_view_win_style", "block_view_back_color_view_win", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_fore_color_checked_style", "block_view_fore_color_checked", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_back_color_checked_style", "block_view_back_color_checked", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_fore_color_unchecked_style", "block_view_fore_color_unchecked", validator_type="color", input_box_width=80),
            self._input("app_sett_style_block_view_back_color_unchecked_style", "block_view_back_color_unchecked", validator_type="color", input_box_width=80),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "block_view_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "block_view_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "block_view_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "block_view_title_stylesheet", affected_keys=self._standard_affected_keys("block_view_title_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "block_view_title_visible"),

            self._title("app_sett_style_block_view_txt_filter_name"),
            self._style("app_sett_style_widget_stylesheet_style", "block_view_txt_filter_stylesheet", affected_keys=self._standard_affected_keys("block_view_txt_filter_stylesheet", "qlineedit")),
            
            self._title("app_sett_style_block_view_btn_clear_filter_name"),
            self._style("app_sett_style_button_stylesheet_style", "block_view_btn_clear_filter_stylesheet", affected_keys=self._standard_affected_keys("block_view_btn_clear_filter_stylesheet", "qpushbutton")),
            
            self._title("app_sett_style_block_view_lbl_count_name"),
            self._combobox("app_sett_style_frame_shape_style", "block_view_lbl_count_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "block_view_lbl_count_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "block_view_lbl_count_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "block_view_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("block_view_lbl_count_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "block_view_lbl_count_visible"),

            self._title("app_sett_style_block_view_ln_delim_name"),
            self._style("app_sett_style_widget_stylesheet_style", "block_view_ln_delim_stylesheet", affected_keys=self._standard_affected_keys("block_view_ln_delim_stylesheet", "qframe")),

            self._title("app_sett_style_block_view_btn_view_diary_name"),
            self._checkbox("app_sett_style_button_flat_style", "block_view_btn_view_diary_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "block_view_btn_view_diary_stylesheet", affected_keys=self._standard_affected_keys("block_view_btn_view_diary_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "block_view_btn_view_diary_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "block_view_btn_view_diary_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_block_view_btn_tags_name"),
            self._checkbox("app_sett_style_button_flat_style", "block_view_btn_tags_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "block_view_btn_tags_stylesheet", affected_keys=self._standard_affected_keys("block_view_btn_tags_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "block_view_btn_tags_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "block_view_btn_tags_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_block_view_btn_close_all_name"),
            self._checkbox("app_sett_style_button_flat_style", "block_view_btn_close_all_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "block_view_btn_close_all_stylesheet", affected_keys=self._standard_affected_keys("block_view_btn_close_all_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "block_view_btn_close_all_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "block_view_btn_close_all_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "block_view_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "block_view_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("block_view_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "block_view_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "block_view_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),
            
            self._title("app_sett_style_frm_tags_frame_name", title_center=True),

            self._title("app_sett_style_frm_tags_frame_general_name"),
            self._combobox("app_sett_style_frame_shape_style", "frm_tags_frame_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "frm_tags_frame_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "frm_tags_frame_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "frm_tags_frame_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_frame_stylesheet", "qframe")),

            self._title("app_sett_style_frame_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "frm_tags_lbl_tag_title_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_lbl_tag_title_stylesheet", "qlabel")),

            self._title("app_sett_style_frm_tags_lbl_tag_tags_name"),
            self._style("app_sett_style_widget_stylesheet_style", "frm_tags_lbl_tag_tags_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_lbl_tag_tags_stylesheet", "qlabel")),

            self._title("app_sett_style_frm_tags_btn_tag_close_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "frm_tags_btn_tag_close_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_btn_tag_close_stylesheet", "qpushbutton")),

            self._title("app_sett_style_frm_tags_btn_tag_reset_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "frm_tags_btn_tag_reset_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_btn_tag_reset_stylesheet", "qpushbutton")),

            self._title("app_sett_style_frm_tags_btn_tag_invert_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "frm_tags_btn_tag_invert_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_btn_tag_invert_stylesheet", "qpushbutton")),

            self._title("app_sett_style_frm_tags_btn_tag_ok_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "frm_tags_btn_tag_ok_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_btn_tag_ok_stylesheet", "qpushbutton")),

            self._title("app_sett_style_frm_tags_btn_tag_cancel_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "frm_tags_btn_tag_cancel_stylesheet", affected_keys=self._standard_affected_keys("frm_tags_btn_tag_cancel_stylesheet", "qpushbutton")),

            self._title("app_sett_style_block_view_chk_tag_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "block_view_chk_tag_stylesheet", affected_keys=self._standard_affected_keys("block_view_chk_tag_stylesheet", "qcheckbox")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_block_view_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Diary view (old style)
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "diary_view_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "diary_view_win_icon_path", cmb_data="icon", input_box_width=-1),
            
            self._title("app_sett_style_diary_view_search_string_name"),
            self._checkbox("app_sett_style_diary_view_mark_search_string_style", "diary_view_mark_search_string"),
            self._input("app_sett_style_diary_view_mark_search_string_fore_color_style", "diary_view_mark_search_string_fore_color", validator_type="color"),
            self._input("app_sett_style_diary_view_mark_search_string_back_color_style", "diary_view_mark_search_string_back_color", validator_type="color"),

            self._title("app_sett_style_title_label_name"),
            self._combobox("app_sett_style_frame_shape_style", "diary_view_title_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "diary_view_title_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "diary_view_title_line_width"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "diary_view_title_stylesheet", affected_keys=self._standard_affected_keys("diary_view_title_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "diary_view_title_visible"),

            self._title("app_sett_style_diary_view_lbl_count_name"),
            self._combobox("app_sett_style_frame_shape_style", "diary_view_lbl_count_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "diary_view_lbl_count_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "diary_view_lbl_count_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("diary_view_lbl_count_stylesheet", "qlabel")),
            self._checkbox("app_sett_style_widget_visible_style", "diary_view_lbl_count_visible"),

            self._title("app_sett_style_diary_view_btn_apply_filter_name"),
            self._checkbox("app_sett_style_button_flat_style", "diary_view_btn_apply_filter_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_apply_filter_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_apply_filter_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "diary_view_btn_apply_filter_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "diary_view_btn_apply_filter_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_block_view_btn_tags_name"),
            self._checkbox("app_sett_style_button_flat_style", "diary_view_btn_tags_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_tags_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_tags_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "diary_view_btn_tags_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "diary_view_btn_tags_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_diary_view_btn_view_blocks_name"),
            self._checkbox("app_sett_style_button_flat_style", "diary_view_btn_view_blocks_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_view_blocks_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_view_blocks_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "diary_view_btn_view_blocks_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "diary_view_btn_view_blocks_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_diary_view_btn_view_name"),
            self._checkbox("app_sett_style_button_flat_style", "diary_view_btn_view_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_view_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_view_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "diary_view_btn_view_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "diary_view_btn_view_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "diary_view_btn_cancel_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_cancel_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "diary_view_btn_cancel_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "diary_view_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_diary_view_data_filter_section_name", title_center=True),

            self._title("app_sett_style_diary_view_txt_from_date_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_txt_from_date_stylesheet", affected_keys=self._standard_affected_keys("diary_view_txt_from_date_stylesheet", "qlineedit")),

            self._title("app_sett_style_diary_view_btn_clear_from_date_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_clear_from_date_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_clear_from_date_stylesheet", "qpushbutton")),

            self._title("app_sett_style_diary_view_txt_to_date_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_txt_to_date_stylesheet", affected_keys=self._standard_affected_keys("diary_view_txt_to_date_stylesheet", "qlineedit")),

            self._title("app_sett_style_diary_view_btn_clear_to_date_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_clear_to_date_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_clear_to_date_stylesheet", "qpushbutton")),

            self._title("app_sett_style_diary_view_txt_filter_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_txt_filter_stylesheet", affected_keys=self._standard_affected_keys("diary_view_txt_filter_stylesheet", "qlineedit")),

            self._title("app_sett_style_diary_view_btn_clear_filter_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_clear_filter_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_clear_filter_stylesheet", "qpushbutton")),

            self._title("app_sett_style_diary_view_chk_case_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_chk_case_stylesheet", affected_keys=self._standard_affected_keys("diary_view_chk_case_stylesheet", "qcheckbox")),

            self._title("app_sett_style_diary_view_item_name", title_center=True),

            self._title("app_sett_style_diary_item_general_name"),
            self._input("app_sett_style_diary_view_area_spacing_style", "diary_view_area_spacing"),
            self._input("app_sett_style_diary_view_item_text_image_spacer_style", "diary_view_item_text_image_spacer"),
            self._style("app_sett_style_diary_item_area_stylesheet_style", "diary_item_area_stylesheet", affected_keys=self._standard_affected_keys("diary_item_area_stylesheet", "qscrollarea")),
            self._style("app_sett_style_diary_item_area_widget_stylesheet_style", "diary_item_area_widget_stylesheet", affected_keys=self._standard_affected_keys("diary_item_area_widget_stylesheet", "qwidget")),

            self._title("app_sett_style_diary_item_lbl_day_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_item_lbl_day_stylesheet", affected_keys=self._standard_affected_keys("diary_item_lbl_day_stylesheet", "qlabel")),

            self._title("app_sett_style_diary_item_lbl_date_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_item_lbl_date_stylesheet", affected_keys=self._standard_affected_keys("diary_item_lbl_date_stylesheet", "qlabel")),

            self._title("app_sett_style_diary_item_lbl_tag_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_item_lbl_tag_stylesheet", affected_keys=self._standard_affected_keys("diary_item_lbl_tag_stylesheet", "qlabel")),

            self._title("app_sett_style_diary_item_text_box_name"),
            self._combobox("app_sett_style_frame_shape_style", "diary_item_text_box_frame_shape", cmb_data="frame_shape"),
            self._combobox("app_sett_style_frame_shadow_style", "diary_item_text_box_frame_shadow", cmb_data="frame_shadow"),
            self._input("app_sett_style_line_width_style", "diary_item_text_box_line_width"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_item_text_box_stylesheet", affected_keys=self._standard_affected_keys("diary_item_text_box_stylesheet", "qtextedit")),

            self._title("app_sett_style_diary_view_item_label_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_item_label_stylesheet", affected_keys=self._standard_affected_keys("diary_view_item_label_stylesheet", "qlabel")),

            self._title("app_sett_style_diary_view_loading_name", title_center=True),

            self._title("app_sett_style_diary_item_general_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_frm_loading_stylesheet", affected_keys=self._standard_affected_keys("diary_view_frm_loading_stylesheet", "qframe")),

            self._title("app_sett_style_diary_view_btn_loading_stop_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "diary_view_btn_loading_stop_stylesheet", affected_keys=self._standard_affected_keys("diary_view_btn_loading_stop_stylesheet", "qpushbutton")),

            self._title("app_sett_style_diary_view_lbl_loading_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_lbl_loading_stylesheet", affected_keys=self._standard_affected_keys("diary_view_lbl_loading_stylesheet", "qlabel")),

            self._title("app_sett_style_diary_view_prg_loading_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "diary_view_prg_loading_stylesheet", affected_keys=self._standard_affected_keys("diary_view_prg_loading_stylesheet", "qprogressbar")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_diary_view_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Fun Fact
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "fun_fact_show_win_stylesheet", affected_keys="qdialog"),
            self._input("app_sett_style_fun_fact_show_normal_content_font_size_style", "fun_fact_show_normal_content_font_size"),
            self._input("app_sett_style_fun_fact_show_normal_content_color_style", "fun_fact_show_normal_content_color", validator_type="color"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "fun_fact_show_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "fun_fact_show_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_sub_title_label_name"),
            self._input("app_sett_style_fun_fact_show_subtitle_font_size_style", "fun_fact_show_subtitle_font_size"),
            self._input("app_sett_style_fun_fact_show_subtitle_color_style", "fun_fact_show_subtitle_color", validator_type="color"),

            self._title("app_sett_style_fun_fact_show_txt_id_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "fun_fact_show_txt_id_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_txt_id_stylesheet", "qlineedit")),

            self._title("app_sett_style_fun_fact_show_txt_id_error_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "fun_fact_show_txt_id_error_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_txt_id_error_stylesheet", "qlineedit")),

            self._title("app_sett_style_fun_fact_content_name"),
            self._style("app_sett_style_fun_fact_show_lbl_content_stylesheet_style", "fun_fact_show_lbl_content_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_lbl_content_stylesheet", "qlabel")),
            self._style("app_sett_style_fun_fact_show_txt_content_stylesheet_style", "fun_fact_show_txt_content_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_txt_content_stylesheet", "qtextedit")),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_fun_fact_show_lbl_rec_stylesheet_style", "fun_fact_show_lbl_rec_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_lbl_rec_stylesheet", "qlabel")),
            self._style("app_sett_style_fun_fact_show_lbl_next_stylesheet_style", "fun_fact_show_lbl_next_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_lbl_next_stylesheet", "qlabel")),
            self._style("app_sett_style_fun_fact_show_lbl_next_val_stylesheet_style", "fun_fact_show_lbl_next_val_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_lbl_next_val_stylesheet", "qlabel")),
            self._style("app_sett_style_fun_fact_show_lbl_name_stylesheet_style", "fun_fact_show_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_lbl_name_stylesheet", "qlabel")),
            
            self._title("app_sett_style_fun_fact_show_cmb_lang_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "fun_fact_show_cmb_lang_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_cmb_lang_stylesheet", "qcombobox")),

            self._title("app_sett_style_fun_fact_show_chk_translate_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "fun_fact_show_chk_translate_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_chk_translate_stylesheet", "qcheckbox")),

            self._title("app_sett_style_fun_fact_show_chk_show_on_start_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "fun_fact_show_chk_show_on_start_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_chk_show_on_start_stylesheet", "qcheckbox")),

            self._title("app_sett_style_fun_fact_show_btn_next_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "fun_fact_show_btn_next_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_btn_next_stylesheet", "qpushbutton")),

            self._title("app_sett_style_btn_cancel_name"),
            self._style("app_sett_style_button_stylesheet_style", "fun_fact_show_btn_close_stylesheet", affected_keys=self._standard_affected_keys("fun_fact_show_btn_close_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_fun_fact_show_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Clipboard view
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "clipboard_view_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "clipboard_view_win_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_delete_clipboard_on_app_exit_style", "delete_clipboard_on_app_exit", recomm_getl="widget_setting_false_recomm"),
            self._checkbox("app_sett_style_delete_clipboard_on_paste_style", "delete_clipboard_on_paste", recomm_getl="widget_setting_false_recomm"),
            self._checkbox("app_sett_style_delete_temp_folder_on_app_exit_style", "delete_temp_folder_on_app_exit", recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "clipboard_view_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_clipboard_view_tree_clip_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "clipboard_view_tree_clip_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_tree_clip_stylesheet", "qtreewidget")),

            self._title("app_sett_style_clipboard_view_chk_del_close_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "clipboard_view_chk_del_close_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_chk_del_close_stylesheet", "qcheckbox"), recomm_getl="widget_setting_false_recomm"),

            self._title("app_sett_style_clipboard_view_chk_del_paste_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "clipboard_view_chk_del_paste_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_chk_del_paste_stylesheet", "qcheckbox"), recomm_getl="widget_setting_false_recomm"),

            self._title("app_sett_style_clipboard_view_chk_del_tmp_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "clipboard_view_chk_del_tmp_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_chk_del_tmp_stylesheet", "qcheckbox"), recomm_getl="widget_setting_true_recomm"),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_clipboard_view_lbl_clip_stylesheet_style", "clipboard_view_lbl_clip_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_clip_stylesheet", "qlabel"), desc_getl="app_sett_label_desc"),
            self._style("app_sett_style_clipboard_view_lbl_clip_title_stylesheet_style", "clipboard_view_lbl_clip_title_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_clip_title_stylesheet", "qlabel")),
            self._style("app_sett_style_clipboard_view_lbl_size_stylesheet_style", "clipboard_view_lbl_size_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_size_stylesheet", "qlabel"), desc_getl="app_sett_label_desc"),
            self._style("app_sett_style_clipboard_view_lbl_size_val_stylesheet_style", "clipboard_view_lbl_size_val_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_size_val_stylesheet", "qlabel"), desc_getl="app_sett_label_desc"),
            self._style("app_sett_style_clipboard_view_lbl_file_stylesheet_style", "clipboard_view_lbl_file_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_file_stylesheet", "qlabel"), desc_getl="app_sett_label_desc"),
            self._style("app_sett_style_clipboard_view_lbl_file_val_stylesheet_style", "clipboard_view_lbl_file_val_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_file_val_stylesheet", "qlabel"), desc_getl="app_sett_label_desc"),
            self._style("app_sett_style_clipboard_view_lbl_pic_stylesheet_style", "clipboard_view_lbl_pic_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_lbl_pic_stylesheet", "qlabel"), desc_getl="app_sett_label_desc"),

            self._title("app_sett_style_clipboard_view_btn_del_tmp_stylesheet_name"),
            self._checkbox("app_sett_style_button_flat_style", "clipboard_view_btn_del_tmp_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "clipboard_view_btn_del_tmp_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_btn_del_tmp_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "clipboard_view_btn_del_tmp_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "clipboard_view_btn_del_tmp_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_clipboard_view_btn_clear_stylesheet_name"),
            self._checkbox("app_sett_style_button_flat_style", "clipboard_view_btn_clear_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "clipboard_view_btn_clear_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_btn_clear_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "clipboard_view_btn_clear_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "clipboard_view_btn_clear_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_clipboard_view_btn_refresh_stylesheet_name"),
            self._checkbox("app_sett_style_button_flat_style", "clipboard_view_btn_refresh_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "clipboard_view_btn_refresh_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_btn_refresh_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "clipboard_view_btn_refresh_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "clipboard_view_btn_refresh_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "clipboard_view_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "clipboard_view_btn_close_stylesheet", affected_keys=self._standard_affected_keys("clipboard_view_btn_close_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "clipboard_view_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "clipboard_view_btn_close_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_clipboard_view_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Media Explorer
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "media_explorer_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "media_explorer_win_icon_path", cmb_data="icon", input_box_width=-1),
            self._checkbox("app_sett_style_when_deleting_copy_images_to_temp_folder_style", "when_deleting_copy_images_to_temp_folder"),
            self._checkbox("app_sett_style_when_deleting_copy_files_to_temp_folder_style", "when_deleting_copy_files_to_temp_folder"),

            self._title("app_sett_style_item_colors_name"),
            self._input("app_sett_style_media_explorer_image_item_list_color_style", "media_explorer_image_item_list_color", validator_type="color"),
            self._input("app_sett_style_media_explorer_file_item_list_color_style", "media_explorer_file_item_list_color", validator_type="color"),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "media_explorer_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_media_explorer_frm_controls_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_frm_controls_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_frm_controls_stylesheet", "qframe")),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_media_explorer_lbl_type_stylesheet_style", "media_explorer_lbl_type_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lbl_type_stylesheet", "qlabel")),
            self._style("app_sett_style_media_explorer_lbl_pic_stylesheet_style", "media_explorer_lbl_pic_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lbl_pic_stylesheet", "qlabel")),
            self._style("app_sett_style_media_explorer_lbl_used_stylesheet_style", "media_explorer_lbl_used_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lbl_used_stylesheet", "qlabel")),
            self._style("app_sett_style_media_explorer_lbl_count_stylesheet_style", "media_explorer_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lbl_count_stylesheet", "qlabel")),

            self._title("app_sett_style_media_explorer_txt_find_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_txt_find_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_txt_find_stylesheet", "qlineedit")),

            self._title("app_sett_style_media_explorer_lst_items_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_lst_items_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lst_items_stylesheet", "qlistwidget")),

            self._title("app_sett_style_media_explorer_tree_duplicates_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_tree_duplicates_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_tree_duplicates_stylesheet", "qtreewidget")),

            self._title("app_sett_style_media_explorer_lst_used_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_lst_used_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lst_used_stylesheet", "qlistwidget")),

            self._title("app_sett_style_media_explorer_rbt_all_radio_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_rbt_all_radio_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_rbt_all_radio_stylesheet", "qradiobutton")),

            self._title("app_sett_style_media_explorer_chk_not_used_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "media_explorer_chk_not_used_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_chk_not_used_stylesheet", "qcheckbox")),

            self._title("app_sett_style_media_explorer_btn_find_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_find_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_find_stylesheet", "qpushbutton")),

            self._title("app_sett_style_media_explorer_btn_delete_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_delete_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_delete_stylesheet", "qpushbutton")),

            self._title("app_sett_style_media_explorer_btn_delete_all_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_delete_all_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_delete_all_stylesheet", "qpushbutton")),

            self._title("app_sett_style_media_explorer_btn_duplicates_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_duplicates_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_duplicates_stylesheet", "qpushbutton")),

            self._title("app_sett_style_media_explorer_btn_delete_duplicates_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_delete_duplicates_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_delete_duplicates_stylesheet", "qpushbutton")),

            self._title("app_sett_style_media_explorer_btn_refresh_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_refresh_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_refresh_stylesheet", "qpushbutton")),

            self._title("app_sett_style_btn_cancel_name"),
            self._style("app_sett_style_button_stylesheet_style", "media_explorer_btn_close_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_close_stylesheet", "qpushbutton")),

            self._title("app_sett_style_media_explorer_progress_name", title_center=True),
            self._style("app_sett_style_media_explorer_frm_progress_stylesheet_style", "media_explorer_frm_progress_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_frm_progress_stylesheet", "qframe")),
            self._style("app_sett_style_media_explorer_lbl_progress_stylesheet_style", "media_explorer_lbl_progress_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_lbl_progress_stylesheet", "qlabel")),
            self._style("app_sett_style_media_explorer_prg_progress_stylesheet_style", "media_explorer_prg_progress_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_prg_progress_stylesheet", "qprogressbar")),
            self._style("app_sett_style_media_explorer_btn_progress_abort_stylesheet_style", "media_explorer_btn_progress_abort_stylesheet", affected_keys=self._standard_affected_keys("media_explorer_btn_progress_abort_stylesheet", "qpushbutton")),
            self._combobox("app_sett_media_explorer_msg_aborted_icon_path", "media_explorer_msg_aborted_icon_path", input_box_width=-1, cmb_data="icon")
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_media_explorer_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Find in App
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "find_in_app_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "find_in_app_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_search_result_colors_name"),
            self._input("app_sett_style_find_in_app_image_item_list_color_style", "find_in_app_image_item_list_color", validator_type="color"),
            self._input("app_sett_style_find_in_app_file_item_list_color_style", "find_in_app_file_item_list_color", validator_type="color"),
            self._input("app_sett_style_find_in_app_block_item_list_color_style", "find_in_app_block_item_list_color", validator_type="color"),
            self._input("app_sett_style_find_in_app_definition_item_list_color_style", "find_in_app_definition_item_list_color", validator_type="color"),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "find_in_app_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_find_in_app_lbl_result_stylesheet_style", "find_in_app_lbl_result_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_result_stylesheet", "qlabel")),
            self._style("app_sett_style_find_in_app_lbl_count_stylesheet_style", "find_in_app_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_count_stylesheet", "qlabel")),
            self._style("app_sett_style_find_in_app_lbl_blocks_stylesheet_style", "find_in_app_lbl_blocks_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_blocks_stylesheet", "qlabel")),
            self._style("app_sett_style_find_in_app_lbl_defs_stylesheet_style", "find_in_app_lbl_defs_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_defs_stylesheet", "qlabel")),
            self._style("app_sett_style_find_in_app_lbl_images_stylesheet_style", "find_in_app_lbl_images_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_images_stylesheet", "qlabel")),
            self._style("app_sett_style_find_in_app_lbl_files_stylesheet_style", "find_in_app_lbl_files_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_files_stylesheet", "qlabel")),

            self._title("app_sett_style_find_in_app_txt_find_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_in_app_txt_find_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_txt_find_stylesheet", "qlineedit")),
            self._style("app_sett_style_find_in_app_txt_find_illegal_entry_stylesheet_style", "find_in_app_txt_find_illegal_entry_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_txt_find_illegal_entry_stylesheet", "qlineedit")),

            self._title("app_sett_style_find_in_app_btn_find_stylesheet_name"),
            self._checkbox("app_sett_style_button_flat_style", "find_in_app_btn_find_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "find_in_app_btn_find_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_btn_find_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "find_in_app_btn_find_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "find_in_app_btn_find_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_find_in_app_under_search_field_name"),
            self._style("app_sett_style_find_in_app_chk_case_stylesheet_style", "find_in_app_chk_case_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_case_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_words_stylesheet_style", "find_in_app_chk_words_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_words_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_auto_search_stylesheet_style", "find_in_app_chk_auto_search_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_auto_search_stylesheet", "qcheckbox")),

            self._title("app_sett_style_find_in_app_grp_search_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_in_app_grp_search_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_grp_search_stylesheet", "qgroupbox")),

            self._title("app_sett_style_find_in_app_in_groupbox_name"),
            self._style("app_sett_style_find_in_app_chk_block_date_stylesheet_style", "find_in_app_chk_block_date_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_block_date_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_block_name_stylesheet_style", "find_in_app_chk_block_name_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_block_name_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_block_tags_stylesheet_style", "find_in_app_chk_block_tags_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_block_tags_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_block_text_stylesheet_style", "find_in_app_chk_block_text_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_block_text_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_block_def_syn_stylesheet_style", "find_in_app_chk_block_def_syn_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_block_def_syn_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_def_name_stylesheet_style", "find_in_app_chk_def_name_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_def_name_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_def_syn_stylesheet_style", "find_in_app_chk_def_syn_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_def_syn_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_def_desc_stylesheet_style", "find_in_app_chk_def_desc_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_def_desc_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_img_name_stylesheet_style", "find_in_app_chk_img_name_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_img_name_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_img_desc_stylesheet_style", "find_in_app_chk_img_desc_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_img_desc_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_img_file_stylesheet_style", "find_in_app_chk_img_file_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_img_file_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_img_src_stylesheet_style", "find_in_app_chk_img_src_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_img_src_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_file_name_stylesheet_style", "find_in_app_chk_file_name_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_file_name_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_file_desc_stylesheet_style", "find_in_app_chk_file_desc_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_file_desc_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_file_file_stylesheet_style", "find_in_app_chk_file_file_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_file_file_stylesheet", "qcheckbox")),
            self._style("app_sett_style_find_in_app_chk_file_src_stylesheet_style", "find_in_app_chk_file_src_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_chk_file_src_stylesheet", "qcheckbox")),

            self._title("app_sett_style_find_in_app_btn_search_all_stylesheet_name"),
            self._checkbox("app_sett_style_button_flat_style", "find_in_app_btn_search_all_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "find_in_app_btn_search_all_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_btn_search_all_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "find_in_app_btn_search_all_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "find_in_app_btn_search_all_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_find_in_app_lst_result_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "find_in_app_lst_result_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lst_result_stylesheet", "qlistwidget")),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "find_in_app_btn_close_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "find_in_app_btn_close_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_btn_close_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "find_in_app_btn_close_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "find_in_app_btn_close_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_find_in_app_searching_frame_name", title_center=True),
            self._style("app_sett_style_find_in_app_frm_searching_stylesheet_style", "find_in_app_frm_searching_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_frm_searching_stylesheet", "qframe")),
            self._style("app_sett_style_find_in_app_lbl_searching_stylesheet_style", "find_in_app_lbl_searching_stylesheet", affected_keys=self._standard_affected_keys("find_in_app_lbl_searching_stylesheet", "qlabel")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_find_in_app_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Application Settings
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "app_settings_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "app_settings_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "app_settings_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_resize_animation_name"),
            self._checkbox("app_sett_style_app_setting_animate_item_resize_style", "app_setting_animate_item_resize"),
            self._input("app_sett_style_app_setting_item_animation_duration_style", "app_setting_item_animation_duration"),
            self._input("app_sett_style_app_setting_item_animation_steps_style", "app_setting_item_animation_steps"),

            self._title("app_sett_style_app_settings_frm_menu_item_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_frm_menu_item_stylesheet", affected_keys=self._standard_affected_keys("app_settings_frm_menu_item_stylesheet", "qframe")),
            self._style("app_sett_style_labels_stylesheet_style", "app_settings_lbl_menu_item_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_menu_item_stylesheet", "qlabel")),

            self._title("app_sett_style_app_settings_lbl_counter_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_lbl_counter_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_counter_stylesheet", "qlabel")),

            self._title("app_sett_style_aapp_settings_lst_changes_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_lst_changes_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lst_changes_stylesheet", "qlistwidget")),

            self._title("app_sett_style_app_settings_btn_save_name"),
            self._checkbox("app_sett_style_button_flat_style", "app_settings_btn_save_text_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "app_settings_btn_save_text_stylesheet", affected_keys=self._standard_affected_keys("app_settings_btn_save_text_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "app_settings_btn_save_text_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "app_settings_btn_save_text_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_app_settings_btn_apply_name"),
            self._checkbox("app_sett_style_button_flat_style", "app_settings_btn_apply_text_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "app_settings_btn_apply_text_stylesheet", affected_keys=self._standard_affected_keys("app_settings_btn_apply_text_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "app_settings_btn_apply_text_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "app_settings_btn_apply_text_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_btn_cancel_name"),
            self._checkbox("app_sett_style_button_flat_style", "app_settings_btn_cancel_text_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "app_settings_btn_cancel_text_stylesheet", affected_keys=self._standard_affected_keys("app_settings_btn_cancel_text_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "app_settings_btn_cancel_text_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "app_settings_btn_cancel_text_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_app_settings_btn_export_name"),
            self._checkbox("app_sett_style_button_flat_style", "app_settings_btn_export_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "app_settings_btn_export_stylesheet", affected_keys=self._standard_affected_keys("app_settings_btn_export_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "app_settings_btn_export_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "app_settings_btn_export_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_app_settings_btn_import_name"),
            self._checkbox("app_sett_style_button_flat_style", "app_settings_btn_import_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "app_settings_btn_import_stylesheet", affected_keys=self._standard_affected_keys("app_settings_btn_import_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "app_settings_btn_import_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "app_settings_btn_import_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_app_settings_import_options_name", title_center=True, font_size=16),

            self._title("app_sett_style_app_settings_frm_import_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_frm_import_stylesheet", affected_keys=self._standard_affected_keys("app_settings_frm_import_stylesheet", "qframe")),
            
            self._title("app_sett_style_frame_title_label_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_lbl_import_title_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_import_title_stylesheet", "qlabel")),

            self._title("app_sett_style_app_settings_lbl_import_close_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_lbl_import_close_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_import_close_stylesheet", "qlabel")),

            self._title("app_sett_style_app_settings_rbt_import_radio_buttons_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_rbt_import_radio_buttons_stylesheet", affected_keys=self._standard_affected_keys("app_settings_rbt_import_radio_buttons_stylesheet", "qradiobutton")),

            self._title("app_sett_style_app_settings_grp_import_groupboxes_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_grp_import_groupboxes_stylesheet", affected_keys=self._standard_affected_keys("app_settings_grp_import_groupboxes_stylesheet", "qgroupbox")),

            self._title("app_sett_style_app_settings_chk_import_checkboxes_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_chk_import_checkboxes_stylesheet", affected_keys=self._standard_affected_keys("app_settings_chk_import_checkboxes_stylesheet", "qcheckbox")),

            self._title("app_sett_style_app_settings_lbl_import_desc_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_lbl_import_desc_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_import_desc_stylesheet", "qlabel")),

            self._title("app_sett_style_app_settings_btn_import_from_file_name"),
            self._checkbox("app_sett_style_button_flat_style", "app_settings_btn_import_from_file_flat", desc_getl="app_sett_style_button_flat_desc"),
            self._style("app_sett_style_button_stylesheet_style", "app_settings_btn_import_from_file_stylesheet", affected_keys=self._standard_affected_keys("app_settings_btn_import_from_file_stylesheet", "qpushbutton")),
            self._input("app_sett_style_select_shortcut_style", "app_settings_btn_import_from_file_shortcut", validator_type="shortcut"),
            self._combobox("app_sett_style_select_icon_image_style", "app_settings_btn_import_from_file_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_app_settings_working_name", title_center=True, font_size=16),

            self._title("app_sett_style_app_settings_frm_working_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_frm_working_stylesheet", affected_keys=self._standard_affected_keys("app_settings_frm_working_stylesheet", "qframe")),

            self._title("app_sett_style_app_settings_frm_working_info_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_frm_working_info_stylesheet", affected_keys=self._standard_affected_keys("app_settings_frm_working_info_stylesheet", "qframe")),

            self._title("app_sett_style_app_settings_lbl_working_title_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_lbl_working_title_stylesheet", affected_keys=self._standard_affected_keys("app_settings_lbl_working_title_stylesheet", "qlabel")),

            self._title("app_sett_style_app_settings_prg_working_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "app_settings_prg_working_stylesheet", affected_keys=self._standard_affected_keys("app_settings_prg_working_stylesheet", "qprogressbar")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_app_settings_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Dictionary Frame
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._input("app_sett_style_dict_online_search_cash_style", "dict_online_search_cash"),
            self._combobox("app_sett_style_dict_online_image_search_engine_style", "dict_online_image_search_engine", cmb_data="dict_search_engine"),
            self._combobox("app_sett_style_search_engine_logo_YAHOO_style", "search_engine_logo_YAHOO", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_search_engine_logo_AOL_style", "search_engine_logo_AOL", cmb_data="icon", input_box_width=-1),
            self._input("app_sett_style_dict_frame_max_number_of_saved_words_style", "dict_frame_max_number_of_saved_words"),

            self._title("app_sett_style_dict_frame_txt_find_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "dict_frame_txt_find_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_txt_find_stylesheet", "qlineedit")),

            self._title("app_sett_style_dict_frame_btn_find_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_find_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_find_stylesheet", "qpushbutton")),

            self._title("app_sett_style_dict_frame_btn_find_deep_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_find_deep_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_find_deep_stylesheet", "qpushbutton")),

            self._title("app_sett_style_dict_frame_txt_item_find_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "dict_frame_txt_item_find_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_txt_item_find_stylesheet", "qlineedit")),

            self._title("app_sett_style_file_info_labels_name"),
            self._style("app_sett_style_dict_frame_lbl_find_stylesheet_style", "dict_frame_lbl_find_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_find_stylesheet", "qlabel")),
            self._style("app_sett_style_dict_frame_lbl_result_stylesheet_style", "dict_frame_lbl_result_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_result_stylesheet", "qlabel")),
            self._style("app_sett_style_dict_frame_lbl_count_stylesheet_style", "dict_frame_lbl_count_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_count_stylesheet", "qlabel")),
            self._style("app_sett_style_dict_frame_lbl_dict_name_stylesheet_style", "dict_frame_lbl_dict_name_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_dict_name_stylesheet", "qlabel")),
            self._style("app_sett_style_dict_frame_lbl_item_name_stylesheet_style", "dict_frame_lbl_item_name_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_item_name_stylesheet", "qlabel")),
            self._style("app_sett_style_dict_frame_lbl_items_stylesheet_style", "dict_frame_lbl_items_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_items_stylesheet", "qlabel")),
            self._style("app_sett_style_dict_frame_lbl_searching_stylesheet_style", "dict_frame_lbl_searching_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lbl_searching_stylesheet", "qlabel")),

            self._title("app_sett_style_dict_frame_area_dict_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "dict_frame_area_dict_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_area_dict_stylesheet", "qlistwidget")),

            self._title("app_sett_style_dict_frame_lst_items_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "dict_frame_lst_items_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_lst_items_stylesheet", "qlistwidget")),

            self._title("app_sett_style_dict_frame_txt_item_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "dict_frame_txt_item_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_txt_item_stylesheet", "qtextedit")),

            self._title("app_sett_style_dict_icons_name"),
            self._combobox("app_sett_style_dict_mit_icon_path_style", "dict_mit_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_vujaklija_icon_path_style", "dict_vujaklija_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_san_icon_path_style", "dict_san_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_zargon_icon_path_style", "dict_zargon_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_bos_icon_path_style", "dict_bos_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_en-sr_icon_path_style", "dict_en-sr_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_dict_psiho_icon_path_style", "dict_psiho_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_stari_izrazi_icon_path_style", "dict_stari_izrazi_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_filoz_icon_path_style", "dict_filoz_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_emo_icon_path_style", "dict_emo_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_biljke_icon_path_style", "dict_biljke_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_it_icon_path_style", "dict_it_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_google&ms_icon_path_style", "dict_google&ms_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_bank_icon_path_style", "dict_bank_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_bokeljski_icon_path_style", "dict_bokeljski_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_fraze_icon_path_style", "dict_fraze_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_ekonom_icon_path_style", "dict_ekonom_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_ekonom2_icon_path_style", "dict_ekonom2_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_proces_icon_path_style", "dict_proces_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_filoz2_icon_path_style", "dict_filoz2_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_srp_srednji_vek_icon_path_style", "dict_srp_srednji_vek_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_sind_icon_path_style", "dict_sind_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_religije_icon_path_style", "dict_religije_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_svet_mit_icon_path_style", "dict_svet_mit_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_arvacki_icon_path_style", "dict_arvacki_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_frajer_icon_path_style", "dict_frajer_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_astroloski_icon_path_style", "dict_astroloski_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_biblija_stari_zavet_icon_path_style", "dict_biblija_stari_zavet_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_biblija_novi_zavet_icon_path_style", "dict_biblija_novi_zavet_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_bibl_leksikon_icon_path_style", "dict_bibl_leksikon_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_tis_mit_icon_path_style", "dict_tis_mit_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_dz_pravni_icon_path_style", "dict_dz_pravni_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_eponim_icon_path_style", "dict_eponim_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_jung_icon_path_style", "dict_jung_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_hrt_icon_path_style", "dict_hrt_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_imena_icon_path_style", "dict_imena_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_kosarka_icon_path_style", "dict_kosarka_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_jez_nedoum_icon_path_style", "dict_jez_nedoum_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_bibliotek_icon_path_style", "dict_bibliotek_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_leksikon_hji_icon_path_style", "dict_leksikon_hji_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_lov_icon_path_style", "dict_lov_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_polemologija_icon_path_style", "dict_polemologija_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_crven_ban_icon_path_style", "dict_crven_ban_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_medicina_icon_path_style", "dict_medicina_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_medicina_rogic_icon_path_style", "dict_medicina_rogic_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_narat_icon_path_style", "dict_narat_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_latin_icon_path_style", "dict_latin_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_anglicizmi_icon_path_style", "dict_anglicizmi_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_onkoloski_icon_path_style", "dict_onkoloski_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_pravoslavni_pojmovnik_icon_path_style", "dict_pravoslavni_pojmovnik_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_kuran_icon_path_style", "dict_kuran_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_arhitekt_icon_path_style", "dict_arhitekt_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_latin2_icon_path_style", "dict_latin2_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_pirot_icon_path_style", "dict_pirot_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_pravni_novinar_icon_path_style", "dict_pravni_novinar_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_poslovice_icon_path_style", "dict_poslovice_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_turcizmi_icon_path_style", "dict_turcizmi_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_urbani_icon_path_style", "dict_urbani_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_geografija_icon_path_style", "dict_geografija_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_biologija_icon_path_style", "dict_biologija_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_slo_mit_encikl_icon_path_style", "dict_slo_mit_encikl_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_tehnicki_icon_path_style", "dict_tehnicki_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_tolkin_icon_path_style", "dict_tolkin_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_istorijski_icon_path_style", "dict_istorijski_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_vlaski_icon_path_style", "dict_vlaski_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_zakon_krivicni_zakonik_icon_path_style", "dict_zakon_krivicni_zakonik_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_zakon_krivicni_postupak_icon_path_style", "dict_zakon_krivicni_postupak_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_zakon_o_radu_icon_path_style", "dict_zakon_o_radu_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_dusan_icon_path_style", "dict_dusan_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_zakon_upravni_icon_path_style", "dict_zakon_upravni_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_zakon_razni_icon_path_style", "dict_zakon_razni_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_dict_ustav_icon_path_style", "dict_ustav_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_dict_frame_btn_back_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_back_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_back_stylesheet", "qpushbutton")),

            self._title("app_sett_style_dict_frame_btn_forward_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_forward_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_forward_stylesheet", "qpushbutton")),

            self._title("app_sett_style_dict_frame_btn_item_back_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_item_back_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_item_back_stylesheet", "qpushbutton")),

            self._title("app_sett_style_dict_frame_btn_lock_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_lock_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_lock_stylesheet", "qpushbutton")),

            self._title("app_sett_style_btn_cancel_name"),
            self._style("app_sett_style_button_stylesheet_style", "dict_frame_btn_close_stylesheet", affected_keys=self._standard_affected_keys("dict_frame_btn_close_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_dict_frame_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Online Content
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "online_content_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "online_content_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_text_stylesheet_style", "online_content_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("online_content_lbl_title_stylesheet", "qlabel")),
            self._style("app_sett_style_dialog_title_pic_stylesheet_style", "online_content_lbl_title_pic_stylesheet", affected_keys=self._standard_affected_keys("online_content_lbl_title_pic_stylesheet", "qlabel")),

            self._title("app_sett_style_online_content_lst_topics_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "online_content_lst_topics_stylesheet", affected_keys=self._standard_affected_keys("online_content_lst_topics_stylesheet", "qlistwidget")),

            self._title("app_sett_style_online_content_btn_topics_show_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "online_content_btn_topics_show_stylesheet", affected_keys=self._standard_affected_keys("online_content_btn_topics_show_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_online_content_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Wikipedia
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "wiki_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "wiki_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_wikipedia_central_label_animation_path_name"),
            self._combobox("app_sett_style_wikipedia_central_label_animation_path_style", "wikipedia_central_label_animation_path", cmb_data="animation", input_box_width=-1),

            self._title("app_sett_style_wiki_frm_search_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "wiki_frm_search_stylesheet", affected_keys=self._standard_affected_keys("wiki_frm_search_stylesheet", "qframe")),

            self._title("app_sett_style_wiki_txt_search_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "wiki_txt_search_stylesheet", affected_keys=self._standard_affected_keys("wiki_txt_search_stylesheet", "qlineedit")),

            self._title("app_sett_style_wiki_btn_search_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "wiki_btn_search_stylesheet", affected_keys=self._standard_affected_keys("wiki_btn_search_stylesheet", "qpushbutton")),

            self._title("app_sett_style_wiki_lbl_search_icon_path_name"),
            self._combobox("app_sett_style_select_icon_image_style", "wiki_lbl_search_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_wiki_lbl_content_icon_path_name"),
            self._combobox("app_sett_style_select_icon_image_style", "wiki_lbl_content_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_wiki_btn_refresh_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "wiki_btn_refresh_stylesheet", affected_keys=self._standard_affected_keys("wiki_btn_refresh_stylesheet", "qpushbutton")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_wiki_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Filter results
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "filter_results_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "filter_results_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_filter_results_labels_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_labels_stylesheet", affected_keys=self._standard_affected_keys("filter_results_labels_stylesheet", "qlabel")),

            self._title("app_sett_style_filter_results_cmb_item_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_cmb_item_stylesheet", affected_keys=self._standard_affected_keys("filter_results_cmb_item_stylesheet", "qcombobox")),

            self._title("app_sett_style_filter_results_lbl_filter_text_val_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_lbl_filter_text_val_stylesheet", affected_keys=self._standard_affected_keys("filter_results_lbl_filter_text_val_stylesheet", "qlabel")),

            self._title("app_sett_style_filter_results_txt_doc_text_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_txt_doc_text_stylesheet", affected_keys=self._standard_affected_keys("filter_results_txt_doc_text_stylesheet", "qtextedit")),

            self._title("app_sett_style_filter_results_btn_show_setup_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "filter_results_btn_show_setup_stylesheet", affected_keys=self._standard_affected_keys("filter_results_btn_show_setup_stylesheet", "qpushbutton")),

            self._title("app_sett_style_filter_results_setup_frame_name", title_center=True),

            self._title("app_sett_style_filter_results_frm_setup_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_frm_setup_stylesheet", affected_keys=self._standard_affected_keys("filter_results_frm_setup_stylesheet", "qframe")),

            self._title("app_sett_style_filter_results_lbl_setup_title_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_lbl_setup_title_stylesheet", affected_keys=self._standard_affected_keys("filter_results_lbl_setup_title_stylesheet", "qlabel")),

            self._title("app_sett_style_filter_results_grp_setup_operators_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_grp_setup_operators_stylesheet", affected_keys=self._standard_affected_keys("filter_results_grp_setup_operators_stylesheet", "qgroupbox")),

            self._title("app_sett_style_filter_results_property_labels_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "filter_results_property_labels_stylesheet", affected_keys=self._standard_affected_keys("filter_results_property_labels_stylesheet", "qlabel")),

            self._title("app_sett_style_filter_results_lbl_setup_close_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "filter_results_lbl_setup_close_stylesheet", affected_keys=self._standard_affected_keys("filter_results_lbl_setup_close_stylesheet", "qlabel")),

            self._title("app_sett_style_filter_results_colors_in_textbox_name", title_center=True),
            
            self._title("app_sett_style_filter_results_valid_apperance_name"),
            self._input("app_sett_style_filter_fg_color_style", "filter_results_doc_textbox_color_valid_fg", validator_type="color", desc_getl="app_sett_style_filter_results_fg_color_desc"),
            self._input("app_sett_style_filter_bg_color_style", "filter_results_doc_textbox_color_valid_bg", validator_type="color", desc_getl="app_sett_style_filter_results_bg_color_desc"),
            self._checkbox("app_sett_style_filter_font_bold_style", "filter_results_doc_textbox_valid_font_bold", desc_getl="app_sett_style_filter_font_bold_desc"),

            self._title("app_sett_style_filter_results_invalid_whole_word_apperance_name"),
            self._input("app_sett_style_filter_fg_color_style", "filter_results_doc_textbox_color_invalid_whole_word_fg", validator_type="color", desc_getl="app_sett_style_filter_results_fg_color_desc"),
            self._input("app_sett_style_filter_bg_color_style", "filter_results_doc_textbox_color_invalid_whole_word_bg", validator_type="color", desc_getl="app_sett_style_filter_results_bg_color_desc"),
            self._checkbox("app_sett_style_filter_font_bold_style", "filter_results_doc_textbox_invalid_whole_word_font_bold", desc_getl="app_sett_style_filter_font_bold_desc"),

            self._title("app_sett_style_filter_results_invalid_matchcase_apperance_name"),
            self._input("app_sett_style_filter_fg_color_style", "filter_results_doc_textbox_color_invalid_matchcase_fg", validator_type="color", desc_getl="app_sett_style_filter_results_fg_color_desc"),
            self._input("app_sett_style_filter_bg_color_style", "filter_results_doc_textbox_color_invalid_matchcase_bg", validator_type="color", desc_getl="app_sett_style_filter_results_bg_color_desc"),
            self._checkbox("app_sett_style_filter_font_bold_style", "filter_results_doc_textbox_invalid_matchcase_font_bold", desc_getl="app_sett_style_filter_font_bold_desc"),

            self._title("app_sett_style_filter_results_invalid_all_apperance_name"),
            self._input("app_sett_style_filter_fg_color_style", "filter_results_doc_textbox_color_invalid_all_fg", validator_type="color", desc_getl="app_sett_style_filter_results_fg_color_desc"),
            self._input("app_sett_style_filter_bg_color_style", "filter_results_doc_textbox_color_invalid_all_bg", validator_type="color", desc_getl="app_sett_style_filter_results_bg_color_desc"),
            self._checkbox("app_sett_style_filter_font_bold_style", "filter_results_doc_textbox_invalid_all_font_bold", desc_getl="app_sett_style_filter_font_bold_desc"),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_filter_results_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Export - Import Dialog
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "export_import_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_export_icon_path_style", "export_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_import_icon_path_style", "import_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "export_import_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_tab_action_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_tab_action_stylesheet", affected_keys=self._standard_affected_keys("export_import_tab_action_stylesheet", "qtabwidget")),

            self._title("app_sett_style_export_import_btn_exec_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_exec_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_exec_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_exec_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_btn_cancel_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_cancel_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_cancel_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_cancel_icon_path", cmb_data="icon", input_box_width=-1),

            # Export blocks
            self._title("app_sett_style_export_import_tab_export_block_name", title_center=True),

            self._title("app_sett_style_export_import_tab_card_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_frm_export_block_stylesheet", affected_keys=self._standard_affected_keys("export_import_frm_export_block_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_button_clear_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_export_block_clear_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_export_block_clear_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_export_block_clear_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_button_paste_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_export_block_paste_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_export_block_paste_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_export_block_paste_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_info_label_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_export_block_info_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_export_block_info_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_items_list_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lst_export_block_stylesheet", affected_keys=self._standard_affected_keys("export_import_lst_export_block_stylesheet", "qlistwidget")),

            # Import blocks
            self._title("app_sett_style_export_import_tab_import_block_name", title_center=True),

            self._title("app_sett_style_export_import_tab_card_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_frm_import_block_stylesheet", affected_keys=self._standard_affected_keys("export_import_frm_import_block_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_button_clear_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_import_block_clear_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_import_block_clear_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_import_block_clear_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_button_add_file_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_import_block_add_file_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_import_block_add_file_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_import_block_add_file_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_info_label_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_import_block_info_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_import_block_info_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_items_list_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lst_import_block_stylesheet", affected_keys=self._standard_affected_keys("export_import_lst_import_block_stylesheet", "qlistwidget")),

            # Export defs
            self._title("app_sett_style_export_import_tab_export_def_name", title_center=True),

            self._title("app_sett_style_export_import_tab_card_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_frm_export_def_stylesheet", affected_keys=self._standard_affected_keys("export_import_frm_export_def_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_button_clear_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_export_def_clear_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_export_def_clear_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_export_def_clear_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_button_paste_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_export_def_paste_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_export_def_paste_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_export_def_paste_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_info_label_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_export_def_info_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_export_def_info_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_items_list_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lst_export_def_stylesheet", affected_keys=self._standard_affected_keys("export_import_lst_export_def_stylesheet", "qlistwidget")),

            # Import defs
            self._title("app_sett_style_export_import_tab_import_def_name", title_center=True),

            self._title("app_sett_style_export_import_tab_card_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_frm_import_def_stylesheet", affected_keys=self._standard_affected_keys("export_import_frm_import_def_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_button_clear_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_import_def_clear_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_import_def_clear_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_import_def_clear_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_button_add_file_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_import_def_add_file_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_import_def_add_file_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_import_def_add_file_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_info_label_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_import_def_info_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_import_def_info_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_items_list_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lst_import_def_stylesheet", affected_keys=self._standard_affected_keys("export_import_lst_import_def_stylesheet", "qlistwidget")),

            # Item Enabled
            self._title("app_sett_style_export_import_list_item_enabled_name", title_center=True),

            self._title("app_sett_style_export_import_item_card_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_enabled_frame_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_enabled_frame_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_enabled_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_enabled_lbl_enabled_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_enabled_lbl_enabled_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_id_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_enabled_lbl_id_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_enabled_lbl_id_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_name_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_enabled_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_enabled_lbl_name_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_src_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_enabled_lbl_src_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_enabled_lbl_src_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_text_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_enabled_lbl_text_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_enabled_lbl_text_stylesheet", "qlabel")),

            # Item Disabled
            self._title("app_sett_style_export_import_list_item_disabled_name", title_center=True),

            self._title("app_sett_style_export_import_item_card_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_disabled_frame_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_disabled_frame_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_enabled_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_disabled_lbl_enabled_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_disabled_lbl_enabled_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_id_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_disabled_lbl_id_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_disabled_lbl_id_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_name_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_disabled_lbl_name_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_disabled_lbl_name_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_src_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_disabled_lbl_src_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_disabled_lbl_src_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_list_item_enabled_lbl_text_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_list_item_disabled_lbl_text_stylesheet", affected_keys=self._standard_affected_keys("export_import_list_item_disabled_lbl_text_stylesheet", "qlabel")),

            # Execute Frame
            self._title("app_sett_style_export_import_list_execute_name", title_center=True),

            self._title("app_sett_style_export_import_frm_execute_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_frm_execute_stylesheet", affected_keys=self._standard_affected_keys("export_import_frm_execute_stylesheet", "qframe")),

            self._title("app_sett_style_export_import_lbl_execute_title_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_execute_title_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_execute_title_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_txt_execute_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_txt_execute_stylesheet", affected_keys=self._standard_affected_keys("export_import_txt_execute_stylesheet", "qtextedit")),

            self._title("app_sett_style_export_import_lst_execute_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lst_execute_stylesheet", affected_keys=self._standard_affected_keys("export_import_lst_execute_stylesheet", "qlistwidget")),

            self._title("app_sett_style_export_import_btn_execute_confirm_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_execute_confirm_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_execute_confirm_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_execute_confirm_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_btn_execute_done_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_execute_done_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_execute_done_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_execute_done_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_btn_execute_cancel_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_execute_cancel_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_execute_cancel_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_execute_cancel_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_btn_execute_details_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_execute_details_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_execute_details_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_execute_details_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_btn_execute_actions_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "export_import_btn_execute_actions_stylesheet", affected_keys=self._standard_affected_keys("export_import_btn_execute_actions_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "export_import_btn_execute_actions_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_export_import_lbl_execute_info_correct_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_execute_info_correct_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_execute_info_correct_stylesheet", "qlabel")),

            self._title("app_sett_style_export_import_lbl_execute_info_incorrect_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "export_import_lbl_execute_info_incorrect_stylesheet", affected_keys=self._standard_affected_keys("export_import_lbl_execute_info_incorrect_stylesheet", "qlabel")),

        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_ei_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Compare (export-import)
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_sett_style_compare_frm_tag_stylesheet_style", "compare_frm_tag_stylesheet", affected_keys=self._standard_affected_keys("compare_frm_tag_stylesheet", "qframe")),
            self._combobox("app_sett_compare_win_icon_path_style", "compare_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "compare_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("compare_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_ccompare_lbl_desc_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "compare_lbl_desc_stylesheet", affected_keys=self._standard_affected_keys("compare_lbl_desc_stylesheet", "qlabel")),

            self._title("app_sett_style_compare_btn_abort_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "compare_btn_abort_stylesheet", affected_keys=self._standard_affected_keys("compare_btn_abort_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "compare_btn_abort_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_compare_chk_boxes_unchecked_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "compare_chk_boxes_unchecked_stylesheet", affected_keys=self._standard_affected_keys("compare_chk_boxes_unchecked_stylesheet", "qcheckbox")),

            self._title("app_sett_style_compare_chk_boxes_checked_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "compare_chk_boxes_checked_stylesheet", affected_keys=self._standard_affected_keys("compare_chk_boxes_checked_stylesheet", "qcheckbox")),

            # New data
            self._title("app_sett_style_compare_new_data_name", title_center=True),

            self._title("app_sett_style_compare_lbl_tag_new_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "compare_lbl_tag_new_stylesheet", affected_keys=self._standard_affected_keys("compare_lbl_tag_new_stylesheet", "qlabel")),

            self._title("app_sett_style_compare_btn_tag_new_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "compare_btn_tag_new_stylesheet", affected_keys=self._standard_affected_keys("compare_btn_tag_new_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "compare_btn_tag_new_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_compare_txt_rename_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "compare_txt_rename_stylesheet", affected_keys=self._standard_affected_keys("compare_txt_rename_stylesheet", "qlineedit")),

            # Old data
            self._title("app_sett_style_compare_old_data_name", title_center=True),

            self._title("app_sett_style_compare_lbl_tag_old_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "compare_lbl_tag_old_stylesheet", affected_keys=self._standard_affected_keys("compare_lbl_tag_old_stylesheet", "qlabel")),

            self._title("app_sett_style_compare_btn_tag_old_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "compare_btn_tag_old_stylesheet", affected_keys=self._standard_affected_keys("compare_btn_tag_old_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_select_icon_image_style", "compare_btn_tag_old_icon_path", cmb_data="icon", input_box_width=-1),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_compare_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

        # Statistic
        item_to_add = [
            self._title("app_sett_style_selection_win_name"),
            self._style("app_settings_grp_style_gen_title", "statistic_win_stylesheet", affected_keys="qdialog"),
            self._combobox("app_sett_style_definition_add_win_icon_path_style", "statistic_win_icon_path", cmb_data="icon", input_box_width=-1),

            self._title("app_sett_style_title_label_name"),
            self._style("app_sett_style_dialog_title_label_stylesheet_style", "statistic_lbl_title_stylesheet", affected_keys=self._standard_affected_keys("statistic_lbl_title_stylesheet", "qlabel")),

            self._title("app_sett_style_statistic_area_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_area_stylesheet", affected_keys=self._standard_affected_keys("statistic_area_stylesheet", "qscrollarea")),

            self._title("app_sett_style_statistic_section_icons_name"),
            self._combobox("app_sett_style_statistic_btn_app_icon_path_style", "statistic_btn_app_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_statistic_btn_block_icon_path_style", "statistic_btn_block_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_statistic_btn_def_icon_path_style", "statistic_btn_def_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_statistic_btn_tag_icon_path_style", "statistic_btn_tag_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_statistic_btn_img_icon_path_style", "statistic_btn_img_icon_path", cmb_data="icon", input_box_width=-1),
            self._combobox("app_sett_style_statistic_btn_file_icon_path_style", "statistic_btn_file_icon_path", cmb_data="icon", input_box_width=-1),

            # Sections
            self._title("app_sett_style_statistic_sections_name", title_center=True, font_size=16),

            self._title("app_sett_style_statistic_section_general_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_section_frm_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_frm_stylesheet", "qframe")),
            self._title("app_sett_style_statistic_section_general_collapsed_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_section_frm_collapsed_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_frm_collapsed_stylesheet", "qframe")),
            self._title("app_sett_style_statistic_section_main_button_name"),
            self._style("app_sett_style_button_stylesheet_style", "statistic_section_btn_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_btn_stylesheet", "qpushbutton")),
            self._title("app_sett_style_statistic_section_lbl_info_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_section_lbl_info_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_lbl_info_stylesheet", "qlabel")),
            self._title("app_sett_style_statistic_section_search_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_section_frm_kw_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_frm_kw_stylesheet", "qframe")),
            self._title("app_sett_style_statistic_section_txt_kw_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_section_txt_kw_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_txt_kw_stylesheet", "qlineedit")),
            self._title("app_sett_style_statistic_section_btn_kw_stylesheet_name"),
            self._style("app_sett_style_button_stylesheet_style", "statistic_section_btn_kw_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_btn_kw_stylesheet", "qpushbutton")),
            self._title("app_sett_style_statistic_section_lbl_info_kw_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_section_lbl_info_kw_stylesheet", affected_keys=self._standard_affected_keys("statistic_section_lbl_info_kw_stylesheet", "qlabel")),

            # Log frame
            self._title("app_sett_style_statistic_log_name", title_center=True, font_size=16),

            self._title("app_sett_style_statistic_log_frame_general_name"),
            self._checkbox("app_sett_style_statistic_log_frame_enabled_style", "statistic_log_frame_enabled"),
            self._input("app_sett_style_statistic_log_frame_duration_style", "statistic_log_frame_duration", desc_getl="statistic_log_frame_duration_desc"),
            self._input("app_sett_style_statistic_log_frame_delay_style", "statistic_log_frame_delay", desc_getl="statistic_log_frame_delay_desc"),

            self._title("app_sett_style_statistic_log_appearance_name"),
            self._style("app_sett_style_statistic_log_working_stylesheet_style", "statistic_frm_log_stylesheet", affected_keys=self._standard_affected_keys("statistic_frm_log_stylesheet", "qframe")),
            self._style("app_sett_style_statistic_log_success_stylesheet_style", "statistic_frm_log_success_stylesheet", affected_keys=self._standard_affected_keys("statistic_frm_log_success_stylesheet", "qframe")),
            self._style("app_sett_style_statistic_log_error_stylesheet_style", "statistic_frm_log_error_stylesheet", affected_keys=self._standard_affected_keys("statistic_frm_log_error_stylesheet", "qframe")),
            self._title("app_sett_style_statistic_log_close_button_name"),
            self._style("app_sett_style_button_stylesheet_style", "statistic_btn_log_stylesheet", affected_keys=self._standard_affected_keys("statistic_btn_log_stylesheet", "qpushbutton")),
            self._combobox("app_sett_style_statistic_btn_log_icon_path_style", "statistic_btn_log_icon_path", cmb_data="icon", input_box_width=-1),
            self._title("app_sett_style_statistic_lbl_log_stylesheet_name"),
            self._style("app_sett_style_widget_stylesheet_style", "statistic_lbl_log_stylesheet", affected_keys=self._standard_affected_keys("statistic_lbl_log_stylesheet", "qlabel")),
        ]

        item_group_data = self.item_group_empty_dictionary()
        item_group_data["name"] = self.getl("app_sett_style_statistic_name")
        if populate_archive:
            self._add_to_archive(section, item_group_data["name"], item_to_add)
        else:
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

    def _standard_affected_keys(self, base_key: str, widget_type: str) -> list:
        if base_key.endswith("_stylesheet"):
            base_key = base_key[:-11]

        result = []
        if self._stt.is_setting_key_exist(base_key + "_stylesheet"):
            result.append([base_key + "_stylesheet", widget_type])
        if self._stt.is_setting_key_exist(base_key + "_font_name"):
            result.append([base_key + "_font_name", widget_type])
        if self._stt.is_setting_key_exist(base_key + "_font_size"):
            result.append([base_key + "_font_size", widget_type])
        if self._stt.is_setting_key_exist(base_key + "_font_weight"):
            result.append([base_key + "_font_weight", widget_type])
        if self._stt.is_setting_key_exist(base_key + "_font_italic"):
            result.append([base_key + "_font_italic", widget_type])
        if self._stt.is_setting_key_exist(base_key + "_font_underline"):
            result.append([base_key + "_font_underline", widget_type])
        if self._stt.is_setting_key_exist(base_key + "_font_strikeout"):
            result.append([base_key + "_font_strikeout", widget_type])

        return result

    def _menu_main_list(self) -> list:
        result = [
            "menu_file",
            "menu_edit",
            "menu_view",
            "menu_user",
            "menu_help"
        ]

        return result
    
    def _menu_item_list(self) -> list:
        result = [
            # File
            "mnu_file_app_settings",
            "mnu_export_blocks",
            "mnu_import_blocks",
            "mnu_export_def",
            "mnu_import_def",
            "mnu_open",
            "mnu_save_as",
            "mnu_file_save_active_block",
            # Edit
            "mnu_add_block",
            "mnu_expand_all",
            "mnu_collapse_all",
            "mnu_unfinished_show",
            "mnu_edit_tags",
            "mnu_edit_definitions",
            "mnu_translation",
            # View
            "mnu_diary",
            "mnu_view_blocks",
            "mnu_view_tags",
            "mnu_view_definitions",
            "mnu_view_images",
            "mnu_view_fun_fact",
            "mnu_view_clipboard",
            "mnu_view_media_explorer",
            "mnu_view_dicts",
            "mnu_view_wiki",
            "mnu_view_online_content",
            "mnu_view_find_in_app",
            # Help
            "mnu_help_log_messages",
            "mnu_help_statistic"
        ]

        return result

    def _btn_delete_list(self) -> list:
        result = [
            "tag_view_btn_delete",
            "browse_def_btn_delete",
            "picture_browse_btn_delete",
            "clipboard_view_btn_del_tmp",
            "clipboard_view_btn_clear",
            "media_explorer_btn_delete",
            "media_explorer_btn_delete_all",
            "media_explorer_btn_delete_duplicates",
            "synonyms_manager_btn_delete"
        ]

        return result

    def _btn_cancel_list(self) -> list:
        result = [
            "selection_btn_cancel",
            "calendar_btn_cancel",
            "definition_add_btn_cancel",
            "picture_add_btn_cancel",
            "picture_view_btn_cancel",
            "translate_btn_close",
            "tag_view_btn_cancel",
            "browse_def_btn_close",
            "picture_browse_btn_close",
            "def_editor_btn_cancel",
            "block_view_btn_cancel",
            "frm_tags_btn_tag_cancel",
            "find_def_btn_cancel",
            "diary_view_btn_cancel",
            "file_add_btn_cancel",
            "file_info_btn_cancel",
            "fun_fact_show_btn_close",
            "clipboard_view_btn_close",
            "media_explorer_btn_close",
            "app_settings_btn_cancel_text",
            "synonyms_manager_btn_close",
            "def_hint_manager_btn_cancel",
            "find_in_app_btn_close",
            "export_import_btn_cancel",
            "export_import_btn_execute_cancel"
        ]

        return result

    def _btn_confirm_list(self) -> list:
        result = [
            "selection_btn_select",
            "input_box_btn_ok",
            "calendar_btn_select",
            "msg_box_btn_ok",
            "definition_add_btn_save",
            "definition_view_btn_edit",
            "picture_add_btn_add",
            "picture_view_btn_save",
            "picture_view_btn_next",
            "translate_btn_trans"
            "definition_view_btn_ok",
            "tag_view_btn_apply",
            "tag_view_btn_add",
            "browse_def_btn_edit",
            "picture_browse_btn_update",
            "frm_tags_btn_tag_ok",
            "find_def_btn_edit",
            "diary_view_btn_apply_filter",
            "diary_view_btn_view_blocks",
            "diary_view_btn_view",
            "file_add_btn_add_to_list",
            "file_add_btn_add",
            "file_info_btn_update",
            "file_info_btn_save_as",
            "file_info_btn_open",
            "fun_fact_show_btn_next",
            "clipboard_view_btn_refresh",
            "media_explorer_btn_refresh",
            "app_settings_btn_save_text",
            "app_settings_btn_apply_text",
            "synonyms_manager_btn_update",
            "synonyms_manager_btn_add",
            "synonyms_manager_btn_copy",
            "definition_add_btn_format_desc",
            "def_hint_manager_btn_save",
            "find_in_app_btn_find",
            "browse_def_btn_add",
            "export_import_btn_exec",
            "export_import_btn_execute_confirm",
            "export_import_btn_execute_done"
        ]

        return result

    def _win_dialogs_list(self) -> list:
        result = [
            "selection_win",
            "definition_add_win",
            "picture_add_win",
            "picture_view_win",
            "definition_view_win",
            "translate_win",
            "tag_view_win",
            "browse_def_win",
            "picture_browse_win",
            "definition_editor_win",
            "block_view_win",
            "find_def_win",
            "diary_view_win",
            "file_add_win",
            "file_info_win",
            "fun_fact_show_win",
            "clipboard_view_win",
            "media_explorer_win",
            "find_in_app_win",
            "app_settings_win",
            "synonyms_manager_win",
            "online_content_win",
            "wiki_win",
            "def_hint_manager_win",
            "filter_results_win",
            "export_import_win",
            "statistic_win"
        ]

        return result

    def _win_dialogs_title_list(self) -> list:
        result = [
            "selection_lbl_title",
            "definition_add_title",
            "picture_add_title",
            "translate_lbl_title",
            "tag_view_lbl_title",
            "browse_def_lbl_title",
            "picture_browse_lbl_title",
            "def_editor_lbl_title",
            "block_view_title",
            "find_def_lbl_name",
            "diary_view_title",
            "file_add_lbl_title",
            "file_info_lbl_title",
            "fun_fact_show_lbl_title",
            "clipboard_view_lbl_title",
            "media_explorer_lbl_title",
            "find_in_app_lbl_title",
            "app_settings_lbl_title",
            "synonyms_manager_lbl_title",
            "def_hint_manager_lbl_title",
            "export_import_lbl_title",
            "compare_lbl_title",
            "statistic_lbl_title"
        ]

        return result

    def menu_item_enabled_affected_keys(self) -> list:
        result = []

        for item in self._menu_item_list():
            item = f"{item}_enabled"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])
        
        return result
    
    def menu_item_visible_affected_keys(self) -> list:
        result = []

        for item in self._menu_item_list():
            item = f"{item}_visible"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])
        
        return result
    
    def menu_item_shortcut_visible_affected_keys(self) -> list:
        result = []

        for item in self._menu_item_list():
            item = f"{item}_shortcut_visible_in_menu"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])
            item = f"{item}_shortcut_visible"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])

        return result
    
    def menu_item_icon_visible_affected_keys(self) -> list:
        result = []

        for item in self._menu_item_list():
            item = f"{item}_icon_visible"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])
        
        return result

    def menu_main_style_affected_keys(self) -> list:
        result = []

        for item in self._menu_main_list():
            item = f"{item}_stylesheet"
            if self._stt.is_setting_key_exist(item):
                result += self._standard_affected_keys(item, "qmenu")
        
        return result
    
    def menu_main_tooltip_visible_affected_keys(self) -> list:
        result = []

        for item in self._menu_main_list():
            item = f"{item}_tooltip_visible"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])
        
        return result
    
    def menu_main_enabled_affected_keys(self) -> list:
        result = []

        for item in self._menu_main_list():
            item = f"{item}_enabled"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])
        
        return result
    
    def menu_main_visible_affected_keys(self) -> list:
        result = []

        for item in self._menu_main_list():
            item = f"{item}_visible"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qmenu"])

        return result

    def win_dialogs_title_style_affected_keys(self) -> list:
        result = []

        for item in self._win_dialogs_title_list():
            item = f"{item}_stylesheet"
            if self._stt.is_setting_key_exist(item):
                result += self._standard_affected_keys(item, "qlabel")

        return result
    
    def win_dialogs_title_frame_shape_affected_keys(self) -> list:
        result = []
        for item in self._win_dialogs_title_list():
            item = f"{item}_frame_shape"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qlabel"])
        
        return result

    def win_dialogs_title_frame_shadow_affected_keys(self) -> list:
        result = []
        for item in self._win_dialogs_title_list():
            item = f"{item}_frame_shadow"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qlabel"])
        
        return result
    
    def win_dialogs_title_line_width_affected_keys(self) -> list:
        result = []
        for item in self._win_dialogs_title_list():
            item = f"{item}_line_width"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qlabel"])
        
        return result

    def win_dialogs_style_affected_keys(self) -> list:
        result = []

        for item in self._win_dialogs_list():
            item = f"{item}_stylesheet"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qdialog"])
        
        return result

    def btn_cancel_style_affected_keys(self) -> list:
        result = []

        for item in self._btn_cancel_list():
            result += self._standard_affected_keys(item, "qpushbutton")

        return result

    def btn_cancel_flat_affected_keys(self) -> list:
        result = []

        for item in self._btn_cancel_list():
            item = f"{item}_flat"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qpushbutton"])
        
        return result

    def btn_cancel_icon_path_affected_keys(self) -> list:
        result = []

        for item in self._btn_cancel_list():
            item = f"{item}_icon_path"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qpushbutton"])
        
        return result

    def btn_delete_style_affected_keys(self) -> list:
        result = []

        for item in self._btn_delete_list():
            result += self._standard_affected_keys(item, "qpushbutton")

        return result

    def btn_delete_flat_affected_keys(self) -> list:
        result = []

        for item in self._btn_delete_list():
            item = f"{item}_flat"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qpushbutton"])
        
        return result

    def btn_delete_icon_path_affected_keys(self) -> list:
        result = []

        for item in self._btn_delete_list():
            item = f"{item}_icon_path"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qpushbutton"])
        
        return result

    def btn_confirm_style_affected_keys(self) -> list:
        result = []

        for item in self._btn_confirm_list():
            result += self._standard_affected_keys(item, "qpushbutton")

        return result

    def btn_confirm_flat_affected_keys(self) -> list:
        result = []

        for item in self._btn_confirm_list():
            item = f"{item}_flat"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qpushbutton"])
        
        return result

    def btn_confirm_icon_path_affected_keys(self) -> list:
        result = []

        for item in self._btn_confirm_list():
            item = f"{item}_icon_path"
            if self._stt.is_setting_key_exist(item):
                result.append([item, "qpushbutton"])
        
        return result

    def _title(self, name_getl: str, name_str: str = None, title_center: bool = False, font_size: int = None, font_shrink: int = None, fg_color: str = None, bg_color: str = None, hover_color: str = None) -> dict:
        if name_str is not None:
            result = {
                "item_type": "title",
                "name": name_str,
                "title_center": title_center
            }
        else:
            result = {
                "item_type": "title",
                "name": self.getl(name_getl),
                "title_center": title_center
            }

        if font_size is not None:
            result["font_size"] = font_size
        if font_shrink is not None:
            result["font_shrink"] = font_shrink
        if result["title_center"]:
            result["bg_color"] = "#1e879f"
            result["fg_color"] = "#d3fffc"
            result["hover_color"] = "#ffffff"
        
        if bg_color is not None:
            result["bg_color"] = bg_color
        if fg_color is not None:
            result["fg_color"] = fg_color
        if hover_color is not None:
            result["hover_color"] = hover_color

        return result

    def _style(self,
               name_getl: str,
               key: str,
               affected_keys: list = None,
               desc_getl: str = None,
               recomm_getl: str = None
               ) -> dict:

        result = {
            "item_type": "style",
            "name": self.getl(name_getl),
            "key": key,
            "font_size": self.ITEM_FONT_SIZE,
            "main_win": self.data.get("main_win")
        }
        if affected_keys is not None:
            if isinstance(affected_keys, str):
                result["affected_keys"] = [[key, affected_keys]]
            else:
                result["affected_keys"] = affected_keys
        if desc_getl is not None:
            result["desc"] = self.getl(desc_getl)
        if recomm_getl is not None:
            result["recomm"] = self.getl(recomm_getl)
        
        return result

    def _def_hint_edit(self) -> dict:

        result = {
            "item_type": "style",
            "name": self.getl("app_sett_def_hint_edit_name"),
            "key": "",
            "font_size": self.ITEM_FONT_SIZE,
            "validator_type": "def_hint_edit",
            "desc": self.getl("app_sett_def_hint_edit_desc"),
            "recomm": "",
            "affected_keys": []
        }
        
        return result

    def _combobox(self, name_getl: str, key: str, cmb_data: str = None, input_box_width: int = None, desc_getl: str = None, recomm_getl: str = None, affected_keys: list = None) -> dict:
        result = {
            "item_type": "combobox",
            "name": self.getl(name_getl),
            "key": key,
            "font_size": self.ITEM_FONT_SIZE,
            "main_win": self.data.get("main_win")
        }
        if cmb_data is not None:
            result["cmb_data"] = cmb_data
        if input_box_width is not None:
            result["input_box_width"] = input_box_width
        if desc_getl is not None:
            result["desc"] = self.getl(desc_getl)
        if recomm_getl is not None:
            result["recomm"] = self.getl(recomm_getl)
        if affected_keys is not None:
            result["affected_keys"] = affected_keys
        
        return result

    def _checkbox(self, name_getl: str, key: str, desc_getl: str = None, recomm_getl: str = None, affected_keys: list = None) -> dict:
        result = {
            "item_type": "checkbox",
            "name": self.getl(name_getl),
            "key": key,
            "font_size": self.ITEM_FONT_SIZE,
            "main_win": self.data.get("main_win")
        }
        if desc_getl is not None:
            result["desc"] = self.getl(desc_getl)
        if recomm_getl is not None:
            result["recomm"] = self.getl(recomm_getl)
        if affected_keys is not None:
            result["affected_keys"] = affected_keys
        
        return result

    def _input(self, name_getl: str, key: str, input_box_width: int = None, validator_type: str = None, validator_data = None, desc_getl: str = None, desc_str: str = None, recomm_getl: str = None, affected_keys: list = None) -> dict:
        result = {
            "item_type": "input",
            "name": self.getl(name_getl),
            "key": key,
            "font_size": self.ITEM_FONT_SIZE,
            "main_win": self.data.get("main_win")
        }
        if input_box_width is not None:
            result["input_box_width"] = input_box_width
        if validator_type is not None:
            result["validator_type"] = validator_type
            if validator_type == "shortcut":
                validator_data = self.get_shortcut_list()
        if validator_data is not None:
            result["validator_data"] = validator_data
        if desc_str is not None:
            result["desc"] = desc_str
        else:
            if desc_getl is not None:
                result["desc"] = self.getl(desc_getl)
        if recomm_getl is not None:
            result["recomm"] = self.getl(recomm_getl)
        if affected_keys is not None:
            result["affected_keys"] = affected_keys
        
        return result

    def get_shortcut_list(self) -> list:
        result = []

        for shortcut in self._stt.get_keys_list():
            if shortcut.endswith("_shortcut"):
                result.append([self.getv(shortcut), shortcut])
        
        result = [x for x in result if x[0] != ""]

        return result

    def populate_archive(self):
        self.show_general_settings(populate_archive=True)
        self.show_block_settings(populate_archive=True)
        self.show_widget_settings(populate_archive=True)
        self.show_dialog_settings(populate_archive=True)

    def _add_to_archive(self, section: str, group_name: str, group_items: list):
        if section not in self.archive:
            self.archive[section] = []
        
        sub_title = ""
        for item in group_items:
            if item["item_type"] == "title":
                sub_title = item["name"]
                continue
            if item.get("affected_keys"):
                affected_keys = [x[0] for x in item["affected_keys"]]
            else:
                affected_keys = [item["key"]]

            search_text = f" {section} {group_name} {sub_title} {item['name']} {item['key']} "
            search_text = search_text.replace("_", " ")

            for i in affected_keys:
                search_text += f"{i} "
            
            # search_text += "\n" + self.clear_serbian_chars(search_text)

            item["section"] = section
            item["group_name"] = group_name
            item["sub_title"] = sub_title

            archive_item = {
                "item": item,
                "search_text": search_text
            }

            self.archive[section].append(archive_item)

    def clear_serbian_chars(self, text: str = None) -> str:
        if text is None:
            return None
        
        replace_table = [
            ["ć", "c"],
            ["č", "c"],
            ["š", "s"],
            ["ž", "z"],
            ["đ", "dj"],
            ["Ć", "c"],
            ["Č", "c"],
            ["Š", "S"],
            ["Ž", "Z"],
            ["Đ", "Dj"]
        ]
        for i in replace_table:
            text = text.replace(i[0], i[1])
        return text

    def create_search_items(self, filter_text: str, wholewords: bool = False, matchcase: bool = False) -> list:
        result = {}

        self._text_filter.MatchCase = matchcase
        self._text_filter.SearchWholeWordsOnly = wholewords
        self._text_filter.clear_search_history()

        count = 0
        for section in self.archive:
            sub_title = ""
            for item in self.archive[section]:
                if self._text_filter.is_filter_in_document(filter_text, item["search_text"]):
                    group_name = f"{section}\n{item['item']['group_name']}"
                    if group_name not in result:
                        sub_title = ""
                        result[group_name] = []
                    if sub_title != item["item"]["sub_title"]:
                        result[group_name].append(self._title(None, name_str=item["item"]["sub_title"]))
                        sub_title = item["item"]["sub_title"]
                    result[group_name].append(item["item"])
                    count += 1
                    self._text_filter.save_search_history(f"{count} | {item['item'].get('key', '')} |{item['item'].get('name', '')}")

        self.search_items = result
        
        return count

    def show_search_items(self):
        for group_name in self.search_items:
            item_to_add = []
            for item in self.search_items[group_name]:
                item_to_add.append(item)

            item_group_data = self.item_group_empty_dictionary()
            item_group_data["name"] = group_name
            group_item = ItemsGroup(self._stt, self.area_settings_widget, item_group_data)
            for item_data in item_to_add:
                group_item.add_item(info_data=item_data)
            self._add_area_setting_item(group_item)
            group_item.show()

    def _add_area_setting_item(self, item: QWidget):
        idx = self.area_settings_widget.layout().count() - 1
        self.area_settings_widget.layout().insertWidget(idx, item)

    def _get_tags_and_desc_for_block_tag_at_start(self):
        tags_db = db_tag_cls.Tag(self._stt)
        tag_list = tags_db.get_all_tags()

        text = self.getl("block_tag_added_at_start_desc")
        for tag in tag_list:
            if tag[1].strip().startswith("{") and tag[1].strip().endswith("}"):
                tag_name = self.getl(tag[1].strip(" {}"))
            else:
                tag_name = tag[1]
            tag_id = tag[0]
            text += f"\nID: {tag_id} - {tag_name}"
        return (tag_list, text)

    def close_me(self):
        QCoreApplication.processEvents()
        for i in range(self.area_settings_widget.layout().count(), 0, -1):
            if self.area_settings_widget.layout().itemAt(i - 1).widget():
                self.area_settings_widget.layout().itemAt(i - 1).widget().close_me()

        # while self.area_settings_widget.layout().count():
        #     if self.area_settings_widget.layout().itemAt(0).widget():
        #         self.area_settings_widget.layout().itemAt(0).widget().close_me()


class ChangedSettingsItem(QFrame):
    STYLE_FRAME_DEFAULT = "QFrame {	background-color: rgb(0, 59, 0); border: 0px solid #ffff00;} QFrame:hover {	background-color: rgb(0, 83, 0);}"
    STYLE_FRAME_UNCHECKED = "QFrame {	background-color: #8a8a8a; border: 0px solid #ffff00;} QFrame:hover {background-color: #9d9d9d;}"
    STYLE_FRAME_INVALID = "QFrame {	background-color: #8b0000; border: 0px solid #ffff00;} QFrame:hover {background-color: #a10000;}"
    STYLE_NEW_VALUE_DEFAULT = "QLabel {color: #00ff00; background-color: transparent; border: 1px solid #00aaff;}"
    STYLE_NEW_VALUE_UNCHECKED = "QLabel {color: #00ffff; background-color: transparent; border: 1px solid #00aaff;}"
    STYLE_NEW_VALUE_INVALID = "QLabel {color: #ff0000; background-color: transparent; border: 1px solid #00aaff;}"
    STYLE_KEY_DEFAULT = "QLabel {color: #ffff00; background-color: #0000ff; border: 1px solid #00aa00;}"
    STYLE_KEY_UNCHECKED = "QLabel {color: #ffffff; background-color: #b3b3b3; border: 0px;}"
    STYLE_KEY_INVALID = "QLabel {color: #ffffff; background-color: #ff0000; border: 0px;}"
    STYLE_BUTTON_CHECKED_DEFAULT = "QPushButton {color: #ffff00; background-color: transparent; border: 1px solid rgb(85, 170, 127); border-radius: 8px;} QPushButton:hover {background-color: #009f75;}"
    STYLE_BUTTON_CHECKED_UNCHECKED = "QPushButton {color: #ffff00; background-color: transparent; border: 1px solid rgb(85, 170, 127); border-radius: 8px;} QPushButton:hover {background-color: #b9b9b9;}"
    STYLE_BUTTON_CHECKED_INVALID = "QPushButton {color: #ffff00; background-color: transparent; border: 1px solid rgb(85, 170, 127); border-radius: 8px;} QPushButton:hover {background-color: #cc0000;}"
    ITEM_SPACER_HEIGHT = 10

    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, item_data: dict, widget_handler: qwidgets_util_cls.WidgetHandler):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("app_settings_changed_settings_item_ui_file_path"), self)

        # Define variables
        self._parent_widget = parent_widget
        self.widget_handler = widget_handler
        self.main_win: Settings = item_data["main_win"]
        self.me_key: str = item_data["key"]
        self.me_old_value = item_data["old_value"]
        self.me_new_value = item_data["new_value"]
        self.me_checked: bool = item_data["is_checked"]
        self.me_valid: bool = item_data["is_valid"]
        self.me_collapsed: bool = item_data.get("is_collapsed", False)
        self.me_width = item_data.get("width", 320)
        self.update_changed_settings_list_function = item_data["update_changed_settings_list_function"]
        self.size_changed_function = item_data["size_changed_function"]
        self.list_item = item_data["list_item"]

        self._define_widgets()
        self._set_widgets_text()
        self._set_item_apperance()
        self.update_item_apperance(is_checked=self.me_checked, is_valid=self.me_valid)

        self._setup_widget_handler()

        # Connect events with slots
        self.btn_checked.clicked.connect(self._btn_checked_clicked)
        self.lbl_shrink.mousePressEvent = self._lbl_shrink_mousePressEvent
        self.lbl_key.mousePressEvent = self._lbl_key_mousePressEvent
        self.lbl_old_value.mousePressEvent = self._lbl_old_value_mousePressEvent
        self.lbl_new_value.mousePressEvent = self._lbl_new_value_mousePressEvent

    def _setup_widget_handler(self):
        widget = self.widget_handler.add_QPushButton(self.btn_checked)
        widget.activate()
        widget = self.widget_handler.add_QPushButton(self.lbl_shrink, widget_properties_dict={"allow_bypass_mouse_press_event": False})
        widget.activate()

    def _lbl_key_mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            has_data = True if self.me_key else False

            result = self._show_context_menu(
                self.getl("app_settings_item_cm_copy_key_text"),
                self.getl("app_settings_item_cm_copy_key_tt").replace("#1", self.me_key),
                has_data,
                self.getv("key_icon_path")
            )

            if result:
                self.get_appv("clipboard").setText(self.me_key)
        elif e.button() == Qt.LeftButton:
            drag = QDrag(self.lbl_key)
            mime = QMimeData()
            mime.setText(self.lbl_key.text())
            drag.setMimeData(mime)
            drag.exec_()

    def _lbl_old_value_mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            has_data = True if self.me_old_value is not None else False

            result = self._show_context_menu(
                self.getl("app_settings_item_cm_copy_old_value_text"),
                self.getl("app_settings_item_cm_copy_old_value_tt").replace("#1", str(self.me_old_value)),
                has_data,
                self.getv("value_icon_path")
            )

            if result:
                self.get_appv("clipboard").setText(str(self.me_old_value))
        elif e.button() == Qt.LeftButton:
            drag = QDrag(self.lbl_old_value)
            mime = QMimeData()
            mime.setText(self.lbl_old_value.text())
            drag.setMimeData(mime)
            drag.exec_()
    
    def _lbl_new_value_mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            has_data = True if self.me_new_value is not None else False

            result = self._show_context_menu(
                self.getl("app_settings_item_cm_copy_new_value_text"),
                self.getl("app_settings_item_cm_copy_new_value_tt").replace("#1", str(self.me_new_value)),
                has_data,
                self.getv("value_icon_path")
            )

            if result:
                self.get_appv("clipboard").setText(str(self.me_new_value))
        elif e.button() == Qt.LeftButton:
            drag = QDrag(self.lbl_new_value)
            mime = QMimeData()
            mime.setText(self.lbl_new_value.text())
            drag.setMimeData(mime)
            drag.exec_()

    def _show_context_menu(self, item_name: str, item_tt: str, has_data: bool, icon: str) -> int:
        disab = [] if has_data else [10]
        
        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "items": [
                [10, item_name, item_tt, True, [], icon]
            ]
        }

        self.main_win._dont_clear_menu = True
        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self.main_win)

        return self.get_appv("menu")["result"]

    def set_check_state(self, checked: bool):
        self.me_checked = checked
        self.update_item_apperance(is_checked=self.me_checked)
        self.update_changed_settings_list_function(self)
    
    def set_valid_state(self, valid: bool):
        self.me_valid = valid
        self.update_item_apperance(is_valid=self.me_valid)
    
    def set_new_value(self, new_value):
        self.me_new_value = new_value
        self._set_widgets_text()
        self.resize_me()

    def _btn_checked_clicked(self):
        if self.me_checked:
            self.me_checked = False
        else:
            self.me_checked = True
        
        self.update_item_apperance(is_checked=self.me_checked)
        self.update_changed_settings_list_function(self)

    def _lbl_shrink_mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_shrink).EVENT_mouse_press_event(e)
            if self.frm_item.size().height() > self.lbl_old_value.pos().y():
                self.collapse_me()
            else:
                self.expand_me()
        
            self.size_changed_function(self.list_item)

    def collapse_me(self):
        self.frm_item.resize(self.size().width(), 50)
        self.resize(self.frm_item.width(), self.frm_item.height() + self.ITEM_SPACER_HEIGHT)
        self.lbl_shrink.setPixmap(QPixmap(self.getv("down_expand_icon_path")))
        self.me_collapsed = True

    def expand_me(self):
        self.frm_item.resize(self.size().width(), self.lbl_new_value.pos().y() + self.lbl_new_value.height() + 5)
        self.resize(self.frm_item.width(), self.frm_item.height() + self.ITEM_SPACER_HEIGHT)
        self.lbl_shrink.setPixmap(QPixmap(self.getv("up_collapse_icon_path")))
        self.me_collapsed = False

    def update_item_apperance(self, is_checked: bool = None, is_valid: bool = None):
        if is_checked is None:
            is_checked = self.me_checked
        if is_valid is None:
            is_valid = self.me_valid

        if is_checked:
            self.btn_checked.setIcon(QIcon(QPixmap(self.getv("checked_icon_path"))))
            if is_valid:
                self.frm_item.setStyleSheet(self.STYLE_FRAME_DEFAULT)
                self.lbl_new_value.setStyleSheet(self.STYLE_NEW_VALUE_DEFAULT)
                self.lbl_key.setStyleSheet(self.STYLE_KEY_DEFAULT)
                self.btn_checked.setStyleSheet(self.STYLE_BUTTON_CHECKED_DEFAULT)
            else:
                self.frm_item.setStyleSheet(self.STYLE_FRAME_INVALID)
                self.lbl_new_value.setStyleSheet(self.STYLE_NEW_VALUE_INVALID)
                self.lbl_key.setStyleSheet(self.STYLE_KEY_INVALID)
                self.btn_checked.setStyleSheet(self.STYLE_BUTTON_CHECKED_INVALID)
        else:
            self.btn_checked.setIcon(QIcon(QPixmap(self.getv("not_checked_icon_path"))))
            self.frm_item.setStyleSheet(self.STYLE_FRAME_UNCHECKED)
            self.lbl_new_value.setStyleSheet(self.STYLE_NEW_VALUE_UNCHECKED)
            self.lbl_key.setStyleSheet(self.STYLE_KEY_UNCHECKED)
            self.btn_checked.setStyleSheet(self.STYLE_BUTTON_CHECKED_UNCHECKED)

    def _define_widgets(self):
        self.btn_checked: QPushButton = self.findChild(QPushButton, "btn_checked")
        self.lbl_key_label: QLabel = self.findChild(QLabel, "lbl_key_label")
        self.lbl_type: QLabel = self.findChild(QLabel, "lbl_type")
        self.lbl_shrink: QLabel = self.findChild(QLabel, "lbl_shrink")
        self.lbl_key: QLabel = self.findChild(QLabel, "lbl_key")
        self.lbl_old_label: QLabel = self.findChild(QLabel, "lbl_old_label")
        self.lbl_old_value: QLabel = self.findChild(QLabel, "lbl_old_value")
        self.lbl_new_label: QLabel = self.findChild(QLabel, "lbl_new_label")
        self.lbl_new_value: QLabel = self.findChild(QLabel, "lbl_new_value")
        self.frm_item: QFrame = self.findChild(QFrame, "frm_item")

    def _set_widgets_text(self):
        self.lbl_key_label.setText(self.getl("app_setting_changed_settings_item_lbl_key_label_text"))
        self.lbl_old_label.setText(self.getl("app_setting_changed_settings_item_lbl_old_label_text"))
        self.lbl_new_label.setText(self.getl("app_setting_changed_settings_item_lbl_new_label_text"))
        
        self.lbl_key.setText(str(self.me_key))
        self.lbl_old_value.setText(str(self.me_old_value))
        self.lbl_new_value.setText(str(self.me_new_value))

        if isinstance(self.me_old_value, str):
            self.lbl_type.setText("STRING")
        elif isinstance(self.me_old_value, int) and not isinstance(self.me_old_value, bool):
            self.lbl_type.setText("INTEGER")
        elif isinstance(self.me_old_value, bool):
            self.lbl_type.setText("BOOLEAN")
        elif isinstance(self.me_old_value, float):
            self.lbl_type.setText("FLOAT")
        else:
            self.lbl_type.setText("UNKNOWN")

    def _set_item_apperance(self):
        self.lbl_key.adjustSize()
        key_w = self.lbl_key.width()
        if key_w <= self.me_width - 55:
            key_w = self.me_width - 55
        self.resize_me(key_w + 55)

    def resize_me(self, width: int = None):
        if width is None:
            width = self.size().width()

        h = self.lbl_old_value.pos().y()

        self.lbl_old_value.setFixedWidth(width - 10)
        self.lbl_old_value.adjustSize()

        h += self.lbl_old_value.height() + 4
        self.lbl_new_label.move(5, h)

        h += self.lbl_new_label.height()
        self.lbl_new_value.move(5, h)
        self.lbl_new_value.setFixedWidth(width - 10)
        self.lbl_new_value.adjustSize()

        h += self.lbl_new_value.height() + 5

        self.lbl_shrink.move(width - 25, 3)
        self.lbl_type.move(width - 110, 5)
        self.lbl_key.resize(width - 55, self.lbl_key.height())

        self.frm_item.resize(width, h)
        self.resize(self.frm_item.width(), self.frm_item.height() + self.ITEM_SPACER_HEIGHT)
        if self.me_collapsed:
            self.collapse_me()
        else:
            self.expand_me()

    def close_me(self):
        self.widget_handler.remove_child(self.btn_checked)
        self.widget_handler.remove_child(self.lbl_shrink)


class Settings(QDialog):
    COLOR_CHANGED_ITEM_DEFAULT = QColor("#00ff00")
    COLOR_CHANGED_ITEM_INVALID = QColor("#ff0000")
    COLOR_CHANGED_ITEM_INACTIVE = QColor("#bdbdbd")
    AUTO_SHOW_SEARCH_BELLOW = 100
    COMPATIBILITY_VERSION = "1.0"

    def __init__(self, settings: settings_cls.Settings, parent_widget, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self._dont_clear_menu = False

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

        # Define variables
        self._parent_widget = parent_widget
        self.changed_settings = []
        self.ignore_lst_changes_item_change = False
        self.ignore_txt_style_stylesheet_text_changes = False
        self.frm_style_affected_list = []
        self.clipboard_stylesheet = None
        self.abort_operation = False

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self.item_group_manager = None
        self.reset_area_settings()
        self.item_group_manager = ItemsGroupManager(
            self._stt,
            self.area_settings_widget,
            {"item_group_empty_dictionary": self.item_group_empty_dictionary, "main_win": self, "loading_function": self._show_loading_label}
            )

        # Widgets handler
        self.load_widgets_handler()

        self._load_win_position()

        self.show_general_settings()
        self.item_group_manager._text_filter.MatchCase = self.chk_menu_search_matchcase.isChecked()
        self.item_group_manager._text_filter.SearchWholeWordsOnly = self.chk_menu_search_whole_words.isChecked()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.keyPressEvent = self._key_press_event
        self.lbl_title.mouseDoubleClickEvent = self.lbl_title_double_click_event
        self.btn_save.clicked.connect(self.btn_save_click)
        self.btn_apply.clicked.connect(self.btn_apply_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_export.clicked.connect(self.btn_export_click)
        self.btn_import.clicked.connect(self.btn_import_click)
        self.btn_import_from_file.clicked.connect(self.btn_import_from_file_click)
        
        # Stylesheet Frame widgets
        self.rbt_style_enabled.clicked.connect(self.rbt_style_enabled_click)
        self.rbt_style_disabled.clicked.connect(self.rbt_style_disabled_click)

        self.btn_style_gen_fg.clicked.connect(self.btn_style_gen_fg_click)
        self.btn_style_gen_bg.clicked.connect(self.btn_style_gen_bg_click)
        self.btn_style_gen_border_color.clicked.connect(self.btn_style_gen_border_color_click)
        self.spin_style_gen_border_size.valueChanged.connect(self.spin_style_gen_border_size_changed)
        self.spin_style_gen_border_radius.valueChanged.connect(self.spin_style_gen_border_radius_changed)
        self.cmb_style_gen_font.currentTextChanged.connect(self.cmb_style_gen_font_changed)
        self.chk_style_gen_font_bold.stateChanged.connect(self.chk_style_gen_font_bold_changed)
        self.chk_style_gen_font_italic.stateChanged.connect(self.chk_style_gen_font_italic_changed)
        self.chk_style_gen_font_underline.stateChanged.connect(self.chk_style_gen_font_underline_changed)
        self.chk_style_gen_font_strikeout.stateChanged.connect(self.chk_style_gen_font_strikeout_changed)
        self.spin_style_gen_font_size.valueChanged.connect(self.spin_style_gen_font_size_changed)
        self.btn_style_gen_font.clicked.connect(self.btn_style_gen_font_click)
        self.lbl_style_close.mousePressEvent = self.lbl_style_close_click
        self.btn_style_cancel.clicked.connect(self.lbl_style_close_click)
        self.lbl_style_gen_fg.mouseDoubleClickEvent = self.lbl_style_gen_fg_double_click
        self.lbl_style_gen_bg.mouseDoubleClickEvent = self.lbl_style_gen_bg_double_click
        self.lbl_style_gen_border_color.mouseDoubleClickEvent = self.lbl_style_gen_border_color_double_click
        self.lbl_style_gen_fg.mousePressEvent = self.lbl_style_gen_fg_click
        self.lbl_style_gen_bg.mousePressEvent = self.lbl_style_gen_bg_click
        self.lbl_style_gen_border_color.mousePressEvent = self.lbl_style_gen_border_color_click

        self.spin_style_hov_border_size.valueChanged.connect(self.spin_style_hov_border_size_changed)
        self.spin_style_hov_border_radius.valueChanged.connect(self.spin_style_hov_border_radius_changed)
        self.btn_style_hov_fg.clicked.connect(self.btn_style_hov_fg_click)
        self.btn_style_hov_bg.clicked.connect(self.btn_style_hov_bg_click)
        self.lbl_style_hov_fg.mouseDoubleClickEvent = self.lbl_style_hov_fg_double_click
        self.lbl_style_hov_bg.mouseDoubleClickEvent = self.lbl_style_hov_bg_double_click
        self.btn_style_hov_border_color.clicked.connect(self.btn_style_hov_border_color_click)
        self.lbl_style_hov_border_color.mouseDoubleClickEvent = self.lbl_style_hov_border_color_double_click
        self.lbl_style_hov_fg.mousePressEvent = self.lbl_style_hov_fg_click
        self.lbl_style_hov_bg.mousePressEvent = self.lbl_style_hov_bg_click
        self.lbl_style_hov_border_color.mousePressEvent = self.lbl_style_hov_border_color_click

        self.btn_style_dis_fg.clicked.connect(self.btn_style_dis_fg_click)
        self.btn_style_dis_bg.clicked.connect(self.btn_style_dis_bg_click)
        self.btn_style_dis_border_color.clicked.connect(self.btn_style_dis_border_color_click)
        self.lbl_style_dis_fg.mouseDoubleClickEvent = self.lbl_style_dis_fg_double_click
        self.lbl_style_dis_bg.mouseDoubleClickEvent = self.lbl_style_dis_bg_double_click
        self.lbl_style_dis_border_color.mouseDoubleClickEvent = self.lbl_style_dis_border_color_double_click
        self.spin_style_dis_border_size.valueChanged.connect(self.spin_style_dis_border_size_changed)
        self.spin_style_dis_border_radius.valueChanged.connect(self.spin_style_dis_border_radius_changed)
        self.lbl_style_dis_fg.mousePressEvent = self.lbl_style_dis_fg_click
        self.lbl_style_dis_bg.mousePressEvent = self.lbl_style_dis_bg_click
        self.lbl_style_dis_border_color.mousePressEvent = self.lbl_style_dis_border_color_click

        self.btn_style_apply.clicked.connect(self.btn_style_apply_click)
        self.txt_style_stylesheet.textChanged.connect(self.txt_style_stylesheet_changed)
        self.btn_style_copy.clicked.connect(self.btn_style_copy_click)
        self.btn_style_paste.clicked.connect(self.btn_style_paste_click)
        # General settings
        self.frm_menu_general.mousePressEvent = self.show_general_settings
        self.lbl_menu_general_icon.mousePressEvent = self.show_general_settings
        self.lbl_menu_general_title.mousePressEvent = self.show_general_settings
        # Startup settings
        self.frm_menu_startup.mousePressEvent = self.show_startup_settings
        self.lbl_menu_startup_icon.mousePressEvent = self.show_startup_settings
        self.lbl_menu_startup_title.mousePressEvent = self.show_startup_settings
        # Widget settings
        self.frm_menu_widget.mousePressEvent = self.show_widget_settings
        self.lbl_menu_widget_icon.mousePressEvent = self.show_widget_settings
        self.lbl_menu_widget_title.mousePressEvent = self.show_widget_settings
        # Window settings
        self.frm_menu_window.mousePressEvent = self.show_window_settings
        self.lbl_menu_window_icon.mousePressEvent = self.show_window_settings
        self.lbl_menu_window_title.mousePressEvent = self.show_window_settings
        # Search settings
        self.frm_menu_search.mousePressEvent = lambda e: self.show_search_settings(e, "frame")
        self.lbl_menu_search_icon.mousePressEvent = lambda e: self.show_search_settings(e, "icon")
        self.lbl_menu_search_title.mousePressEvent = lambda e: self.show_search_settings(e, "title")
        self.txt_menu_search.textChanged.connect(self.txt_menu_search_changed)
        self.txt_menu_search.returnPressed.connect(self.show_search_settings)
        self.txt_menu_search.contextMenuEvent = self.txt_menu_search_context_menu
        self.txt_menu_search.dropEvent = self.txt_menu_search_drop_event
        self.lbl_menu_search_icon.mouseDoubleClickEvent = self.txt_menu_search_mouse_double_click
        self.chk_menu_search_whole_words.stateChanged.connect(self.txt_menu_search_changed)
        self.chk_menu_search_matchcase.stateChanged.connect(self.txt_menu_search_changed)

        # Import Options
        self.rbt_import_custom.clicked.connect(self.rbt_clicked)
        self.rbt_import_all.clicked.connect(self.rbt_clicked)
        self.lbl_import_close.mousePressEvent = self.lbl_import_close_click

        # Advanced settings
        self.lbl_adv_close.mousePressEvent = self.lbl_adv_close_click
        self.txt_adv_find.textChanged.connect(self.txt_adv_find_changed)
        self.lst_adv.itemChanged.connect(self.lst_adv_item_changed)
        self.lst_adv.currentItemChanged.connect(self.lst_adv_current_item_changed)
        self.btn_adv_select_all.clicked.connect(self.btn_adv_select_all_click)
        self.btn_adv_select_none.clicked.connect(self.btn_adv_select_none_click)
        self.btn_adv_swap_selection.clicked.connect(self.btn_adv_swap_selection_click)
        self.btn_adv_show_checked.clicked.connect(self.btn_adv_show_checked_click)
        self.btn_adv_apply.clicked.connect(self.btn_adv_apply_click)
        self.btn_adv_abort.clicked.connect(self.btn_adv_abort_click)
        self.btn_adv_clear_filter.clicked.connect(self.btn_adv_clear_filter_click)
        self.btn_adv_show.clicked.connect(self.btn_adv_show_click)

        self.show()
        UTILS.LogHandler.add_log_record("#1 dialog started.\nDialog displayed.", ["Application settings"])
        self.txt_menu_search.setFocus()

    def txt_menu_search_drop_event(self, a0: QDropEvent):
        if a0.mimeData().hasText():
            self.txt_menu_search.setText(a0.mimeData().text())
            a0.accept()
        else:
            a0.ignore()

    def _show_loading_label(self, value: bool):
        if value:
            self.frm_loading.raise_()
            self.frm_loading.show()
            self.lbl_loading.movie().start()
            QCoreApplication.processEvents()
        else:
            self.frm_loading.hide()
            self.lbl_loading.movie().stop()

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])

        # Add frames
        frm_import = self.widget_handler.add_QFrame(self.frm_import, main_win=self)
        frm_import.add_window_drag_widgets([self.lbl_import_title, self.frm_import])

        frm_adv = self.widget_handler.add_QFrame(self.frm_adv, main_win=self)
        frm_adv.add_window_drag_widgets([self.lbl_adv_title, self.frm_adv])

        frm_style = self.widget_handler.add_QFrame(self.frm_style, main_win=self)
        frm_style.add_window_drag_widgets([self.lbl_style_title, self.frm_style])

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)
        self.widget_handler.find_child(self.btn_import_from_file).properties.allow_bypass_leave_event = False
        self.widget_handler.find_child(self.btn_export).properties.allow_bypass_leave_event = False

        # Add Labels as PushButtons
        self.widget_handler.add_child(self.lbl_style_close, widget_properties_dict={"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_adv_close, widget_properties_dict={"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")
        self.widget_handler.add_child(self.lbl_import_close, widget_properties_dict={"allow_bypass_mouse_press_event": False}, force_widget_type="qpushbutton")

        # Add Action Frames
        self.widget_handler.add_ActionFrame(self.frm_menu_general, widget_properties_dict={"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_ActionFrame(self.frm_menu_startup, widget_properties_dict={"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_ActionFrame(self.frm_menu_widget, widget_properties_dict={"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_ActionFrame(self.frm_menu_window, widget_properties_dict={"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_ActionFrame(self.frm_menu_search, widget_properties_dict={"allow_bypass_mouse_press_event": False})

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_menu_search, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_adv_find, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets(starting_widget=self)

        # Add Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_adv)
        self.widget_handler.add_ItemBased_Widget(self.lst_changes)

        self.widget_handler.activate()

    def lbl_style_gen_fg_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_gen_fg, self.btn_style_gen_fg_click)

    def lbl_style_gen_bg_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_gen_bg, self.btn_style_gen_bg_click)

    def lbl_style_gen_border_color_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_gen_border_color, self.btn_style_gen_border_color_click)
    
    def lbl_style_dis_fg_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_dis_fg, self.btn_style_dis_fg_click)
    
    def lbl_style_dis_bg_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_dis_bg, self.btn_style_dis_bg_click)

    def lbl_style_dis_border_color_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_dis_border_color, self.btn_style_dis_border_color_click)
    
    def lbl_style_hov_fg_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_hov_fg, self.btn_style_hov_fg_click)
    
    def lbl_style_hov_bg_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_hov_bg, self.btn_style_hov_bg_click)
    
    def lbl_style_hov_border_color_click(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.contex_menu_color(self.lbl_style_hov_border_color, self.btn_style_hov_border_color_click)

    def contex_menu_color(self, color_label: QLabel, action_function):
        disab = []
        style = StyleSheet()

        label_text = color_label.text()

        if not label_text or label_text.strip() == "-" or not style._is_valid_color(color_value_string=label_text):
            disab.append(10)
        
        clip_text = self.get_appv("clipboard").text()

        if clip_text and len(clip_text) in [6, 8] and "#" not in clip_text and "rgb" not in clip_text.lower():
            clip_text = "#" + clip_text

        if not clip_text or not style._is_valid_color(color_value_string=clip_text):
            disab.append(20)
        
        if not label_text or label_text.strip() == "-":
            disab.append(30)

        menu_dict = {
            "position": QCursor().pos(),
            "disabled": disab,
            "separator": [20],
            "items": [
                [10, self.getl("app_settings_color_context_menu_copy_text"), label_text, True, [], self.getv("copy_icon_path")],
                [20, self.getl("app_settings_color_context_menu_paste_text"), clip_text, True, [], self.getv("paste_icon_path")],
                [30, self.getl("app_settings_color_context_menu_remove_text"), "", True, [], self.getv("remove_icon_path")]
            ]
        }

        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True

        label_style = color_label.styleSheet()
        color_label.setStyleSheet(label_style + "border: 3px dotted #aaff00;")
        utility_cls.ContextMenu(self._stt, self)
        color_label.setStyleSheet(label_style)

        if menu_dict["result"] == 10:
            self.get_appv("clipboard").setText(label_text)
        elif menu_dict["result"] == 20:
            action_function({"type": "add", "value": clip_text})
        elif menu_dict["result"] == 30:
            action_function({"type": "remove", "value": label_text})

    def btn_adv_show_click(self):
        self.frm_adv.setVisible(not self.frm_adv.isVisible())
        self.update_lst_adv()

    def lbl_title_double_click_event(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.btn_adv_show.setVisible(not self.btn_adv_show.isVisible())

    def btn_adv_clear_filter_click(self):
        if self.txt_adv_find.text():
            self.txt_adv_find.setText("")
        else:
            self.update_lst_adv(preserve_check_state=True)

    def btn_adv_abort_click(self):
        self.abort_operation = True

    def btn_adv_apply_click(self):
        self.btn_adv_apply.setDisabled(True)
        self.frm_adv_progress.setVisible(True)
        self.abort_operation = False

        text_to_html = utility_cls.TextToHTML("Working...\n\n\nPlease Wait")
        text_to_html.general_rule.font_size = 22
        text_to_html.general_rule.fg_color = "#ffffff"
        self.lbl_adv_info.setText(text_to_html.get_html())
        QCoreApplication.processEvents()

        items_to_update = []
        for index in range(self.lst_adv.count()):
            item = self.lst_adv.item(index)
            if item.checkState() == Qt.Checked:
                items_to_update.append(item.text())

        text_to_html = utility_cls.TextToHTML()
        text_to_html.general_rule.font_size = 12
        text_to_html.general_rule.fg_color = "#00ff00"
        text = "Updating #--1 item(s):\n\n"

        if not items_to_update:
            text_to_html.general_rule.font_size = 14
            text_to_html.general_rule.fg_color = "#ff0000"
            text_to_html.set_text("You did not select any items.\n\nPlease select some items.")
            self.lbl_adv_info.setText(text_to_html.get_html())
            self.lbl_adv_info.setToolTip(text_to_html.get_html())
            self.btn_adv_apply.setDisabled(False)
            self.frm_adv_progress.setVisible(False)
            self.abort_operation = False
            return
        
        new_val_string = self.txt_adv_new_value.toPlainText()
        
        try:
            new_val_int = int(new_val_string)
        except:
            new_val_int = None
        
        try:
            new_val_float = float(new_val_string)
        except:
            new_val_float = None
        
        if new_val_string.strip().lower() in ["true", "yes", "1"]:
            new_val_bool = True
        elif new_val_string.strip().lower() in ["false", "no", "0"]:
            new_val_bool = False
        else:
            new_val_bool = None
        
        text += "New value type:\n\nString: #-10\nInteger: #-11\nFloat: #-12\nBoolean: #-13\n\n"

        rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(len(items_to_update)), fg_color="#55ffff", font_bold=True)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#-10", replace_with=new_val_string, fg_color="#55ffff", font_bold=True)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#-11", replace_with=str(new_val_int), fg_color="#55ffff", font_bold=True)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#-12", replace_with=str(new_val_float), fg_color="#55ffff", font_bold=True)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#-13", replace_with=str(new_val_bool), fg_color="#55ffff", font_bold=True)
        text_to_html.add_rule(rule)

        droped_items = []

        count = 0
        for item in items_to_update:
            value = None
            if value is None:
                value = new_val_string if isinstance(self.getv(item), str) else None
            if value is None:
                value = new_val_int if new_val_int is not None and isinstance(self.getv(item), int) and not isinstance(self.getv(item), bool) else None
            if value is None:
                value = new_val_float if new_val_float is not None and isinstance(self.getv(item), float) else None
            if value is None:
                value = new_val_bool if new_val_bool is not None and isinstance(self.getv(item), bool) else None
            
            if value is None:
                droped_items.append(item)
                continue

            self.update_lst_changed_settings(item, value, True)

            # Update Progress
            count += 1
            self.lbl_adv_progress.setText(f"Updating {count} of {len(items_to_update)}\n{item}")
            self.prg_adv_progress.setValue(int(count * 100 / len(items_to_update)))
            QCoreApplication.processEvents()

            # Check if user aborted operation
            if self.abort_operation:
                QMessageBox.warning(self, "Aborted", f"Operation aborted.\nItems processed: {count}\nItems updated: {count - len(droped_items)}\nItems dropped: {len(droped_items)}\n\nNot completed: {len(items_to_update) - count}")
                break
        
        text += "#-20\n\n"
        rule = utility_cls.TextToHtmlRule(text="#-20", replace_with="Result:", fg_color="#ffff00", font_bold=True, font_size=14, font_italic=True)
        text_to_html.add_rule(rule)

        if self.abort_operation:
            text += "#--25\nUnable to update #-26 item(s) due to aborted operation.\n\n"
            rule = utility_cls.TextToHtmlRule(text="#--25", replace_with="Aborted !", fg_color="#ff0000", font_bold=True, font_size=24)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-26", replace_with=str(len(items_to_update) - count), fg_color="#55ffff", font_bold=True)
            text_to_html.add_rule(rule)
        
        if droped_items:
            text += "#-30\n\n#-80 item(s) updated out of #-81\n"
            text += "Dropped #-82 item(s) due to data type conflict:\n#-90"

            rule = utility_cls.TextToHtmlRule(text="#-30", replace_with="Completed with errors.", fg_color="#ff0000", font_bold=True, font_size=20)
            text_to_html.add_rule(rule)
            
            rule = utility_cls.TextToHtmlRule(text="#-80", replace_with=str(len(items_to_update) - len(droped_items)), fg_color="#55ffff", font_bold=True)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-81", replace_with=str(len(items_to_update)), fg_color="#55ffff", font_bold=True)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-82", replace_with=str(len(droped_items)), fg_color="#55ffff", font_bold=True)
            text_to_html.add_rule(rule)

            droped_items_text = "\n".join(droped_items)
            rule = utility_cls.TextToHtmlRule(text="#-90", replace_with=droped_items_text, fg_color="#ff0000", font_bold=True)
            text_to_html.add_rule(rule)
        else:
            text += "No items dropped.\n#-50 item(s) updated.\n\n#30"
            rule = utility_cls.TextToHtmlRule(text="#-50", replace_with=str(len(items_to_update)), fg_color="#55ffff", font_bold=True)
            text_to_html.add_rule(rule)

            if self.abort_operation:
                rule = utility_cls.TextToHtmlRule(text="#30", replace_with="Not Completed. User Abort.", fg_color="#ff0000", font_bold=True, font_size=20)
            else:
                rule = utility_cls.TextToHtmlRule(text="#30", replace_with="Completed successfully.", fg_color="#ffffff", font_bold=True, font_size=22)
            text_to_html.add_rule(rule)
        
        text_to_html.set_text(text)
        self.lbl_adv_info.setText(text_to_html.get_html())
        text_to_html.general_rule.font_size = 14
        self.lbl_adv_info.setToolTip(text_to_html.get_html())

        self.btn_adv_apply.setDisabled(False)
        self.frm_adv_progress.setVisible(False)
        self.abort_operation = False

    def btn_adv_show_checked_click(self):
        self.update_lst_adv(show_checked_only=True, preserve_check_state=True)

    def btn_adv_select_none_click(self):
        old_val = self.ignore_lst_changes_item_change
        self.ignore_lst_changes_item_change = True
        for index in range(self.lst_adv.count()):
            item = self.lst_adv.item(index)
            item.setCheckState(Qt.Unchecked)
        self.ignore_lst_changes_item_change = old_val
        self.update_adv_info_and_counter()

    def btn_adv_select_all_click(self):
        old_val = self.ignore_lst_changes_item_change
        self.ignore_lst_changes_item_change = True
        for index in range(self.lst_adv.count()):
            item = self.lst_adv.item(index)
            item.setCheckState(Qt.Checked)
        self.ignore_lst_changes_item_change = old_val
        self.update_adv_info_and_counter()

    def btn_adv_swap_selection_click(self):
        old_val = self.ignore_lst_changes_item_change
        self.ignore_lst_changes_item_change = True
        for index in range(self.lst_adv.count()):
            item = self.lst_adv.item(index)
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
        self.ignore_lst_changes_item_change = old_val
        self.update_adv_info_and_counter()

    def lst_adv_item_changed(self, item: QListWidgetItem):
        if not self.ignore_lst_changes_item_change:
            if item:
                self.lst_adv.setCurrentItem(item)
            self.update_adv_info_and_counter()
    
    def lst_adv_current_item_changed(self, item: QListWidgetItem):
        self.update_adv_info_and_counter()

    def txt_adv_find_changed(self):
        self.update_lst_adv(preserve_check_state=True)
        if not self.lst_adv.count():
            self.widget_handler.find_child(self.txt_adv_find).text_validation(False)

    def lbl_adv_close_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            obj = self.widget_handler.find_child(self.lbl_adv_close)
            if obj:
                obj.EVENT_mouse_press_event(e, False)
            self.frm_adv.setVisible(False)

    def update_lst_adv(self, preserve_check_state: bool = False, show_checked_only: bool = False):
        old_list_state = {}
        if preserve_check_state:
            for index in range(self.lst_adv.count()):
                item = self.lst_adv.item(index)
                old_list_state[item.text()] = item.checkState()
        else:
            old_list_state = {x: False for x in self._stt.get_keys_list()}

        old_current_item_text = None
        if self.lst_adv.currentItem():
            old_current_item_text = self.lst_adv.currentItem().text()

        self.lst_adv.clear()

        filter_text = self.txt_adv_find.text().strip().lower()
        
        self.item_group_manager._text_filter.MatchCase = False
        self.item_group_manager._text_filter.SearchWholeWordsOnly = False

        for key in self._stt.get_keys_list():
            if filter_text != "" and not self.item_group_manager._text_filter.is_filter_in_document(filter_text, key):
                continue

            item = QListWidgetItem(key)
            # Make item checkable
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if old_list_state.get(key, 0):
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            
            if show_checked_only:
                if item.checkState() == QtCore.Qt.Checked:
                    self.lst_adv.addItem(item)
            else:
                self.lst_adv.addItem(item)
        
        if old_current_item_text:
            for index in range(self.lst_adv.count()):
                item = self.lst_adv.item(index)
                if item.text() == old_current_item_text:
                    self.lst_adv.setCurrentItem(item)
                    break
        else:
            if self.lst_adv.count():
                self.lst_adv.setCurrentItem(self.lst_adv.item(0))

        self.update_adv_info_and_counter()

    def update_adv_info_and_counter(self):
        general_font_size = 12
        text_color = "#00ff00"
        value_color = "#55ffff"
        value_bold = True
        title_color = "#ffff00"
        title_bold = True
        desc_recomm_color = "#c5c5c5"

        # Update counter
        checked_items = 0
        for index in range(self.lst_adv.count()):
            item = self.lst_adv.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checked_items += 1
        self.lbl_adv_counter.setText(f"Checked {checked_items} out of {self.lst_adv.count()} items in total.")

        # Update Info label
        if not self.lst_adv.count():
            self.lbl_adv_info.setText("No items.")
            return
        
        # Find data types used        
        count = 0
        type_string = 0
        type_integer = 0
        type_float = 0
        type_bool = 0

        for index in range(self.lst_adv.count()):
            item = self.lst_adv.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                count += 1
                type_string += 1 if isinstance(self.getv(item.text()), str) else 0
                type_integer += 1 if isinstance(self.getv(item.text()), int) and not isinstance(self.getv(item.text()), bool) else 0
                type_float += 1 if isinstance(self.getv(item.text()), float) else 0
                type_bool += 1 if isinstance(self.getv(item.text()), bool) else 0

        text = "Affected #--1 items.\n\n#t-1\n"
        text += "Type string: #--2 items.\n" if type_string else ""
        text += "Type integer: #--3 items.\n" if type_integer else ""
        text += "Type float: #--4 items.\n" if type_float else ""
        text += "Type bool: #--5 items.\n" if type_bool else ""

        # Add data type info
        text_to_html = utility_cls.TextToHTML()
        text_to_html.general_rule.fg_color = text_color
        text_to_html.general_rule.font_size = general_font_size

        rule = utility_cls.TextToHtmlRule(text="#t-1", replace_with="Selected items data type:", fg_color=title_color, font_bold=title_bold)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(count), fg_color=value_color, font_bold=value_bold)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#--2", replace_with=str(type_string), fg_color=value_color, font_bold=value_bold)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#--3", replace_with=str(type_integer), fg_color=value_color, font_bold=value_bold)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#--4", replace_with=str(type_float), fg_color=value_color, font_bold=value_bold)
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(text="#--5", replace_with=str(type_bool), fg_color=value_color, font_bold=value_bold)
        text_to_html.add_rule(rule)

        # Add Item info
        item_dict = None
        if self.lst_adv.currentItem():
            item_dict = self._stt.get_setting_dict(self.lst_adv.currentItem().text())

        if item_dict:
            text += "\n\n#t-2\n"
            rule = utility_cls.TextToHtmlRule(text="#t-2", replace_with="Current Item info:", fg_color=title_color, font_bold=title_bold)
            text_to_html.add_rule(rule)

            text += "Key:\n#-10\n\nData type: #-11\n\nValue: #-12\nDefault Value: #-13\nMinimum: #-14\nMaximum: #-15\n"

            data_type_text = "None"
            if data_type_text == "None":
                data_type_text = "String" if isinstance(item_dict["value"], str) else "None"
            if data_type_text == "None":
                data_type_text = "Integer" if isinstance(item_dict["value"], int) and not isinstance(item_dict["value"], bool) else "None"
            if data_type_text == "None":
                data_type_text = "Float" if isinstance(item_dict["value"], float) else "None"
            if data_type_text == "None":
                data_type_text = "Boolean" if isinstance(item_dict["value"], bool) else "None"

            rule = utility_cls.TextToHtmlRule(text="#-10", replace_with=self.lst_adv.currentItem().text(), fg_color=value_color, font_bold=value_bold)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-11", replace_with=data_type_text, fg_color=value_color, font_bold=value_bold)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-12", replace_with=str(item_dict["value"]), fg_color=value_color, font_bold=value_bold)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-13", replace_with=str(item_dict["default_value"]), fg_color=value_color, font_bold=value_bold)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-14", replace_with=str(item_dict["min_value"]), fg_color=value_color, font_bold=value_bold)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-15", replace_with=str(item_dict["max_value"]), fg_color=value_color, font_bold=value_bold)
            text_to_html.add_rule(rule)

            text += "\nDescription:\n#-20\nRecommended Value:\n#-21"

            rule = utility_cls.TextToHtmlRule(text="#-20", replace_with=item_dict["description"], fg_color=desc_recomm_color, font_size=general_font_size-2)
            text_to_html.add_rule(rule)
            rule = utility_cls.TextToHtmlRule(text="#-21", replace_with=item_dict["recommended"], fg_color=desc_recomm_color, font_size=general_font_size-2)
            text_to_html.add_rule(rule)

        text_to_html.set_text(text)
        self.lbl_adv_info.setText(text_to_html.get_html())
        text_to_html.general_rule.font_size = general_font_size + 6
        self.lbl_adv_info.setToolTip(text_to_html.get_html())

    def txt_menu_search_mouse_double_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.frm_adv.setVisible(not self.frm_adv.isVisible())
            self.update_lst_adv()

    def btn_import_from_file_click(self):
        UTILS.LogHandler.add_log_record("#1: About to import settings from file.", ["AppSettings"])
        result = self._ask_user_for_filename()
        if result:
            sections = self._get_sections_to_import()
            imported_settings = self._get_settings_from_file(result, sections_to_import=sections)
            if not imported_settings:
                UTILS.LogHandler.add_log_record("#1: User selected file has no valid #2 settings to import.\nFile: #3\nImport canceled.", ["AppSettings", "MyJournal", result])
                self._notiffy_import_error(result)
                return
            count_settings = self._merge_imported_settings(imported_settings)
            if count_settings is None:
                UTILS.LogHandler.add_log_record("#1: An error occurred while importing #2 settings.\nFile: #3\nImport canceled.", ["AppSettings", "MyJournal", result], warning_raised=True)
                QMessageBox.warning(self, self.getl("app_settings_notif_import_error_title"), self.getl("app_settings_notif_import_merge_error_text").replace("#1", result))
                return

            UTILS.LogHandler.add_log_record("#1: Found and imported #2 settings from file: #3.", ["AppSettings", count_settings, result])
            QCoreApplication.processEvents()
            self._notiffy_successfull_import(result, count_settings, imported_settings)

    def _get_sections_to_import(self) -> list:
        if self.rbt_import_all.isChecked():
            return None
        
        sections = []

        if self.chk_import_all_style.isChecked():
            sections.append("all_stylesheet")
        if self.chk_import_button_style.isChecked():
            sections.append("button_stylesheet")
        if self.chk_import_icon.isChecked():
            sections.append("icon_path")
        if self.chk_import_font.isChecked():
            sections.append("font")
        if self.chk_import_sound.isChecked():
            sections.append("sound_file_path")
        
        return sections

    def _merge_imported_settings(self, imported_settings):
        if not isinstance(imported_settings, dict):
            return None
        
        if imported_settings.get("items") is None:
            return None

        self.frm_working.setVisible(True)
        self.frm_working.raise_()
        self.changed_settings = []
        self.lst_changes.clear()
        count_settings = 0
        count = 0
        total_items = len(imported_settings["items"])
        processed_keys = []
        max_item_width = 337
        for item in imported_settings["items"]:
            count += 1
            key = item["key"]
            value = item["value"]

            if key in processed_keys:
                continue
            else:
                processed_keys.append(key)

            if self._stt.is_setting_key_exist(key):
                value = self._convert_data_type(value, self.getv(key))
                try:
                    if self._stt.get_setting_dict(key)["min_value"] is not None and value < self._stt.get_setting_dict(key)["min_value"]:
                        UTILS.LogHandler.add_log_record("#1: Setting #2 value (#3) is below min value: #4.", ["AppSettings", key, value, self._stt.get_setting_dict(key)["min_value"]])
                        continue
                    if self._stt.get_setting_dict(key)["max_value"] is not None and value > self._stt.get_setting_dict(key)["max_value"]:
                        UTILS.LogHandler.add_log_record("#1: Setting #2 value (#3) is above max value: #4.", ["AppSettings", key, value, self._stt.get_setting_dict(key)["max_value"]])
                        continue
                except Exception as e:
                    UTILS.LogHandler.add_log_record("#1: Error while checking setting #2\nSetting value cannot be imported. Value: #3. ValueType: #4\n#5", ["AppSettings", key, value, type(value), str(e)])
                    continue

                result = self.fast_update_lst_changed_setting_no_existing_check(key, value)
                max_item_width = max(max_item_width, result)
                count_settings += 1

                # Progress
                percent = int((count / total_items) * 100)
                if percent != self.prg_working.value():
                    self.prg_working.setValue(percent)
                    QCoreApplication.processEvents()

        # Determine new self.lst_changes items width
        for i in range(self.lst_changes.count()):
            widget_item: ChangedSettingsItem = self.lst_changes.itemWidget(self.lst_changes.item(i))
            widget_item.resize_me(max_item_width)
            self.lst_changes.item(i).setSizeHint(widget_item.size())

        # Update save button
        self.update_save_button_apperance()
        # Update counter
        count_active_settings = len([x for x in self.changed_settings if x["is_checked"]])
        self.lbl_counter.setText(self.getl("app_settings_lbl_counter").replace("#1", str(len(self.changed_settings))).replace("#2", str(count_active_settings)))

        self.frm_working.setVisible(False)
        return count_settings

    def _convert_data_type(self, new_val, old_val):
        if old_val is None:
            UTILS.TerminalUtility.WarningMessage("You must specify old value. Old value is None.\nnew_val = #1\nold_val = #2", [new_val, old_val], exception_raised=True)
            raise TypeError("old_val is None")
        
        try:
            if isinstance(old_val, int) and not isinstance(old_val, bool):
                return int(new_val)
            elif isinstance(old_val, float):
                return float(new_val)
            elif isinstance(old_val, bool):
                if isinstance(new_val, bool):
                    return new_val
                elif isinstance(new_val, int):
                    if new_val == 0:
                        return False
                    elif new_val == 1:
                        return True
                    else:
                        UTILS.TerminalUtility.WarningMessage("Invalid value. New value is in #1 format and can not be converted to bool.\nnew_val = #2\nold_val = #3", ["integer", new_val, old_val], exception_raised=True)
                        raise TypeError("Invalid value. New value is in int format and can not be converted to bool.")
                elif isinstance(new_val, str):
                    if new_val.lower() in ["true", "1"]:
                        return True
                    elif new_val.lower() in ["false", "0"]:
                        return False
                    else:
                        UTILS.TerminalUtility.WarningMessage("Invalid value. New value is in #1 format and can not be converted to bool.\nnew_val = #2\nold_val = #3", ["string", new_val, old_val], exception_raised=True)
                        raise TypeError("Invalid value. New value is in string format and can not be converted to bool.")
                else:
                    UTILS.TerminalUtility.WarningMessage("Invalid value. New value is in #1 format and can not be converted to bool.\nnew_val = #2\nold_val = #3", [type(new_val), new_val, old_val], exception_raised=True)
                    raise TypeError(f"Invalid value. New value is in {type(new_val)} format and can not be converted to bool.")
            elif isinstance(old_val, str):
                return str(new_val)
            else:
                UTILS.TerminalUtility.WarningMessage("Invalid value. Old value is in #1 format and can not be converted to new type #2.\nnew_val = #3\nold_val = #4", [type(old_val), type(new_val), new_val, old_val], exception_raised=True)
                raise TypeError(f"Invalid value. Old value is in {type(old_val)} format and can not be converted to new type ({type(new_val)}).")
        except:
            UTILS.TerminalUtility.WarningMessage("Invalid value. New value is in #1 format and can not be converted to old type #2.\nnew_val = #3\nold_val = #4", [type(new_val), type(old_val), new_val, old_val], exception_raised=True)
            raise TypeError(f"Invalid value. New value is in {type(new_val)} format and can not be converted to old type ({type(old_val)}).")

    def _get_settings_from_file(self, file_name: str, sections_to_import: list = None) -> dict:
        success = False
        with open(file_name, 'r', encoding="utf-8") as file:
            file_content = None
            try:
                file_content = json.load(file)
                success = True
            except:
                success = False

        if not success:
            with open(file_name, 'r', encoding="utf-8") as file:
                try:
                    file_content = file.read()
                    if file_content:
                        success = True
                except:
                    success = False

        if not success:
            return False    
            
        if not isinstance(file_content, dict):
            if sections_to_import is not None:
                return False
            
            return self.try_to_extract_settings(file_content)
        
        try:
            file_ver = float(file_content.get("compatibility_version"))
        except:
            return False

        if file_ver > float(self.COMPATIBILITY_VERSION):
            QMessageBox.warning(self, self.getl("app_settings_btn_import_from_file_version_error_title"), self.getl("app_settings_btn_import_from_file_version_error_text").replace("#1", str(file_ver)).replace("#2", str(self.COMPATIBILITY_VERSION)))
            return False

        if file_content.get("items") is None:
            return False
        
        if sections_to_import is None:
            return file_content
        
        filtered_settings_list = []
        for item in file_content["items"]:
            key: str = item["key"]
            defined_section = False
            if key.endswith(("_font_name", "_font_size", "_font_weight", "_font_italic", "_font_underline", "_font_strikeout")):
                defined_section = True
                if "font" in sections_to_import:
                    filtered_settings_list.append(item)
                    continue
                elif "button_stylesheet" in sections_to_import and "btn_" in key:
                    filtered_settings_list.append(item)
                    continue
            if key.endswith("_stylesheet"):
                defined_section = True
                if "all_stylesheet" in sections_to_import:
                    filtered_settings_list.append(item)
                    continue
                if "button_stylesheet" in sections_to_import and "btn_" in key:
                    filtered_settings_list.append(item)
                    continue
            if key.endswith("_icon_path"):
                defined_section = True
                if "icon_path" in sections_to_import:
                    filtered_settings_list.append(item)
                    continue
            if key.endswith("_sound_file_path"):
                defined_section = True
                if "sound_file_path" in sections_to_import:
                    filtered_settings_list.append(item)
                    continue
            if not sections_to_import and not defined_section:
                filtered_settings_list.append(item)

        file_content["items"] = filtered_settings_list
        
        return file_content

    def try_to_extract_settings(self, file_content):
        if not isinstance(file_content, str):
            return False
        
        if not file_content.strip():
            return False
        
        # Remove comments
        text_list = file_content.splitlines()
        text = ""
        in_comment = False
        for line in text_list:
            line = line.strip()
            if not line:
                continue
            if line.startswith(("#", "//")):
                continue
            if line.startswith("/*"):
                in_comment = True
            if line.endswith("*/"):
                in_comment = False
                continue
            if in_comment:
                continue
            text += line + "\n"
        
        text_segments = text.split("}")
        if not text_segments:
            return False
        
        # Get all stylesheet settings
        # stylesheet_settings Structure: [key_name, widget_type, old_value, new_value]
        stylesheet_settings = []
        for section in self.item_group_manager.archive:
            for item in self.item_group_manager.archive[section]:
                for aff_key in item["item"].get("affected_keys", []):
                    if self._stt.is_setting_key_exist(aff_key[0]):
                        stylesheet_settings.append(aff_key + [self.getv(aff_key[0]), ""])

        if not stylesheet_settings:
            return False

        # Populate new values
        for segment in text_segments:
            segment = segment.strip() + "}"
            segment_list = segment.splitlines()
            widget_type = segment_list[0].split(":")[0].strip().lower()
            for idx, item in enumerate(stylesheet_settings):
                if item[1].lower() == widget_type and item[0].endswith("_stylesheet") and item[2] != segment:
                    stylesheet_settings[idx][3] += segment + "\n"
        
        stylesheet_settings = [item for item in stylesheet_settings if item[3]]

        if not stylesheet_settings:
            return False
        
        final_list = []
        for item in stylesheet_settings:
            final_list.append({
                "key": item[0],
                "value": item[3]
            })

        result = {
            "items": final_list
        }

        # Ask user if he want to import settings from this file
        UTILS.LogHandler.add_log_record("#1: Found #2 valid settings to import from text file, waiting for user confirmation.", ["AppSettings", len(stylesheet_settings)])
        question = QMessageBox.question(self, self.getl("app_settings_msg_import_from_string_file_title"), self.getl("app_settings_msg_import_from_string_file_text").replace("#1", str(len(stylesheet_settings))), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if question != QMessageBox.Yes:
            UTILS.LogHandler.add_log_record("#1: User cancelled the import process.", ["AppSettings"])
            return False
        else:
            UTILS.LogHandler.add_log_record("#1: User confirmed the import process.", ["AppSettings"])
        
        return result

    def _ask_user_for_filename(self) -> str:
        file_dialog = utility_cls.FileDialog(self._stt)
        result = file_dialog.show_dialog(title=self.getl("app_settings_btn_import_from_file_text"), parent_widget=self)
        
        return result

    def lbl_import_close_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            obj = self.widget_handler.find_child(self.lbl_import_close)
            if obj:
                obj.EVENT_mouse_press_event(e, False)
            self.frm_import.setVisible(False)

    def rbt_clicked(self):
        if self.rbt_import_custom.isChecked():
            self.grp_import_all.setDisabled(True)
            self.grp_import_custom.setDisabled(False)
        else:
            self.grp_import_all.setDisabled(False)
            self.grp_import_custom.setDisabled(True)

    def btn_export_click(self):
        UTILS.LogHandler.add_log_record("#1: About to export settings to file.", ["AppSettings"])
        result = self._ask_for_export_filename()
        if result:
            self._export_settings_to_file(result)
            UTILS.LogHandler.add_log_record("#1: Settings exported to file: #2", ["AppSettings", result])
            self._notiffy_successfull_export(result)
        else:
            UTILS.LogHandler.add_log_record("#1: Export cancelled.", ["AppSettings"])

    def btn_import_click(self):
        UTILS.LogHandler.add_log_record("#1: Import settings options displayed.", ["AppSettings"])
        self.frm_import.setVisible(not self.frm_import.isVisible())

    def _ask_for_export_filename(self):
        def check_file_extension(file_name):
            if not file_name.endswith('.json'):
                file_name += '.json'
            return file_name

        file_dialog = utility_cls.FileDialog(self._stt)
        title = self.getl("app_settings_export_dialog_title")
        result = file_dialog.show_save_file_dialog(title=title, parent_widget=self)
        # Check if file extension is .json, if not add .json
        if result:
            result = check_file_extension(result)
        return result

    def _export_settings_to_file(self, file_name: str):
        if not self.item_group_manager:
            return
        
        # Create list of keys
        self.frm_working.setVisible(True)
        self.frm_working.raise_()
        keys_processed = []
        items_to_export = []
        total_items = 0
        for section in self.item_group_manager.archive:
            total_items += len(self.item_group_manager.archive[section])
        count = 0

        for section in self.item_group_manager.archive:
            for item in self.item_group_manager.archive[section]:
                item_to_add = {}
                if item["item"].get("affected_keys"):
                    for aff_key_item in item["item"]["affected_keys"]:
                        if isinstance(aff_key_item, list):
                            aff_key = aff_key_item[0]
                        else:
                            aff_key = aff_key_item

                        if aff_key not in keys_processed and self._stt.is_setting_key_exist(aff_key):
                            keys_processed.append(aff_key)
                            item_to_add = {
                                "key": aff_key,
                                "value": self.getv(aff_key)
                            }
                            items_to_export.append(item_to_add)

                if item["item"]["key"] not in keys_processed:
                    aff_key = item["item"]["key"]
                    if self._stt.is_setting_key_exist(aff_key):
                        keys_processed.append(aff_key)
                        item_to_add = {
                            "key": aff_key,
                            "value": self.getv(aff_key)
                        }
                        items_to_export.append(item_to_add)

                # Progress
                count += 1
                percent = int((count / total_items) * 100)
                if percent != self.prg_working.value():
                    self.prg_working.setValue(percent)
                    QCoreApplication.processEvents()

        date_obj = utility_cls.DateTime(self._stt)
        
        export_dict = {
            "items": items_to_export,
            "hello": "MyJournal 1.0",
            "compatibility_version": "1.0",
            "date": date_obj.get_today_date(),
            "time": date_obj.get_current_time(),
            "user": self.get_appv("user").username,
            "language": self.get_appv("user").language_name
        }

        try:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(export_dict, file, indent=2)
            self.frm_working.setVisible(False)
            return True
        except:
            self.frm_working.setVisible(False)
            return False

    def _notiffy_successfull_export(self, file_name: str):
        data = {
            "title": self.getl("app_settings_notif_export_successfull"),
            "text": self.getl("app_settings_notif_export_successfull_text").replace("#1", file_name),
            "icon": self.getv("app_settings_win_icon_path"),
            "show_close": True,
            "show_ok": True,
            "position": "bottom left",
            "timer": 60000
        }
        utility_cls.Notification(self._stt, self, data)

    def _notiffy_import_error(self, file_name: str):
        data = {
            "title": self.getl("app_settings_notif_import_error_title"),
            "text": self.getl("app_settings_notif_import_error_text").replace("#1", file_name),
            "icon": self.getv("cancel_icon_path"),
            "show_close": True,
            "show_ok": True,
            "position": "bottom left",
            "timer": 60000
        }
        utility_cls.Notification(self._stt, self, data)

    def _notiffy_successfull_import(self, file_name: str, items_count: int, imported_settings: dict):
        title = self.getl("app_settings_notif_import_successfull_title")
        text = self.getl("app_settings_notif_import_successfull_text")
        if file_name:
            text += "\n" + self.getl("app_settings_notif_import_successfull_file_name").replace("#1", file_name)
        if imported_settings.get("compatibility_version"):
            text += "\n" + self.getl("app_settings_notif_import_successfull_version").replace("#1", imported_settings["compatibility_version"])
            if imported_settings.get("hello"):
                text += f"  ({imported_settings['hello']})"
        if imported_settings.get("date"):
            text += "\n" + self.getl("app_settings_notif_import_successfull_time").replace("#1", imported_settings["date"]).replace("#2", imported_settings.get("time", " - "))
        if imported_settings.get("user"):
            text += "\n" + self.getl("app_settings_notif_import_successfull_author").replace("#1", imported_settings["user"])
        if imported_settings.get("language"):
            text += "\n" + self.getl("app_settings_notif_import_successfull_language").replace("#1", imported_settings["language"])
        
        text += "\n" + self.getl("app_settings_notif_import_successfull_items_count").replace("#1", str(items_count))

        data = {
            "title": title,
            "text": text,
            "icon": self.getv("app_settings_win_icon_path"),
            "show_close": True,
            "show_ok": True,
            "position": "bottom left",
            "timer": 60000
        }
        utility_cls.Notification(self._stt, self, data)

    def _key_press_event(self, btn: QtGui.QKeyEvent):
        if btn.key() == Qt.Key_Escape:
            if self.frm_adv.isVisible():
                btn.accept()
                self.frm_adv.setVisible(False)
                return None
            if self.frm_style.isVisible():
                btn.accept()
                self.frm_style.setVisible(False)
                return None
            if self.frm_import.isVisible():
                btn.accept()
                self.frm_import.setVisible(False)
                return None
            else:
                self.close()

    def show_search_settings(self, e: QMouseEvent = None, sender_info: str = None):
        if e is not None and e.button() != Qt.LeftButton:
            return

        filter_text = self.txt_menu_search.text()
        if not filter_text:
            self.reset_area_settings()
            self._update_lbl_menu_search_info_apperance(0)
            self.update_widgets_apperance(active_settings_group="search_settings")
            if e:
                self.widget_handler.find_child(self.frm_menu_search).EVENT_mouse_press_event(e, False)
            return

        item_count = self.item_group_manager.create_search_items(filter_text, wholewords=self.chk_menu_search_whole_words.isChecked(), matchcase=self.chk_menu_search_matchcase.isChecked())

        self._update_lbl_menu_search_info_apperance(item_count)

        self.frm_style.setVisible(False)
        self.update_widgets_apperance(active_settings_group="search_settings")
        if e:
            self.widget_handler.find_child(self.frm_menu_search).EVENT_mouse_press_event(e, False)
        self.reset_area_settings()
        self.item_group_manager.show_search_items()

        if sender_info == "icon":
            QLabel.mousePressEvent(self.lbl_menu_search_icon, e)
        
    def txt_menu_search_context_menu(self, event):
        disab = []
        if not self.txt_menu_search.isUndoAvailable():
            disab.append(10)
        if not self.txt_menu_search.isRedoAvailable():
            disab.append(20)
        selected_text = ""
        if self.txt_menu_search.selectedText():
            selected_text = self.txt_menu_search.selectedText()
        else:
            disab.append(30)
            disab.append(60)
        if self.txt_menu_search.text():
            if not selected_text:
                selected_text = self.txt_menu_search.text()
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

        filter_menu = text_filter_cls.FilterMenu(self._stt, self.item_group_manager._text_filter)
        
        menu_dict = filter_menu.create_menu_dict(show_item_search_history=False, existing_menu_dict=menu_dict)

        self._dont_clear_menu = True

        result = filter_menu.show_menu(self, menu_dict=menu_dict)
        self.chk_menu_search_matchcase.setChecked(self.item_group_manager._text_filter.MatchCase)
        self.chk_menu_search_whole_words.setChecked(self.item_group_manager._text_filter.SearchWholeWordsOnly)
        if result in range(filter_menu.item_range_filter_setup[0], filter_menu.item_range_filter_setup[1]):
            self.txt_menu_search_changed()
        elif result == 10:
            self.txt_menu_search.undo()
        elif result == 20:
            self.txt_menu_search.redo()
        elif result == 30:
            self.txt_menu_search.cut()
        elif result == 40:
            if self.txt_menu_search.selectedText():
                self.txt_menu_search.copy()
            else:
                self.get_appv("clipboard").setText(self.txt_menu_search.text())
        elif result == 50:
            self.txt_menu_search.paste()
        elif result == 60:
            if self.txt_menu_search.selectedText():
                self.txt_menu_search.setText(f"{self.txt_menu_search.text()[:self.txt_menu_search.selectionStart()]}{self.txt_menu_search.text()[self.txt_menu_search.selectionEnd():]}")

    def txt_menu_search_changed(self):
        filter_text = self.txt_menu_search.text()

        if not filter_text:
            self.reset_area_settings()
            self._update_lbl_menu_search_info_apperance(0)
            self.update_widgets_apperance(active_settings_group="search_settings")
            return

        item_count = self.item_group_manager.create_search_items(filter_text, wholewords=self.chk_menu_search_whole_words.isChecked(), matchcase=self.chk_menu_search_matchcase.isChecked())

        if item_count == 0:
            textbox_object: qwidgets_util_cls.Widget_TextBox = self.widget_handler.find_child(self.txt_menu_search)
            textbox_object.text_validation(False)

        self._update_lbl_menu_search_info_apperance(item_count)

        if item_count > self.AUTO_SHOW_SEARCH_BELLOW:
            self.reset_area_settings()
            self.update_widgets_apperance(active_settings_group="search_settings")
            return
        
        self.frm_style.setVisible(False)
        self.update_widgets_apperance(active_settings_group="search_settings")
        self.reset_area_settings()
        self.item_group_manager.show_search_items()

    def _update_lbl_menu_search_info_apperance(self, item_count: int):
        if not self.txt_menu_search.text().strip():
            self.lbl_menu_search_info.setText("")
            return
        
        lbl_info_text = f'{item_count} {self.getl("app_settings_lbl_menu_search_info_text")}'
        if item_count == 1:
            lbl_info_text = lbl_info_text.replace("podešavanja", "podešavanje")

        self.lbl_menu_search_info.setText(lbl_info_text)

    def btn_style_copy_click(self):
        self.clipboard_stylesheet = StyleSheet()
        self.clipboard_stylesheet.merge_stylesheet(self.frm_style_stylesheet, force_new_value=True)
        self.btn_style_paste.setEnabled(True)

    def btn_style_paste_click(self):
        self.frm_style_stylesheet.merge_stylesheet(self.clipboard_stylesheet, force_new_value=True)
        self.txt_style_stylesheet.setText(self.frm_style_stylesheet.stylesheet)

    def rbt_style_enabled_click(self):
        if self.lbl_style_sample.isVisible():
            self.lbl_style_sample.setEnabled(True)
        if self.btn_style_sample.isVisible():
            self.btn_style_sample.setEnabled(True)
    
    def rbt_style_disabled_click(self):
        if self.lbl_style_sample.isVisible():
            self.lbl_style_sample.setEnabled(False)
        if self.btn_style_sample.isVisible():
            self.btn_style_sample.setEnabled(False)

    def txt_style_stylesheet_changed(self):
        if self.ignore_txt_style_stylesheet_text_changes:
            return
        
        self.frm_style_stylesheet.stylesheet = self.txt_style_stylesheet.toPlainText()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_gen_bg_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.bg_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def lbl_style_gen_border_color_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.border_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def lbl_style_hov_fg_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.fg_hover_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_dis_fg_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.fg_disabled_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_dis_bg_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.bg_disabled_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_dis_border_color_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.border_disabled_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_hov_bg_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.bg_hover_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def lbl_style_hov_border_color_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.border_hover_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_gen_fg_double_click(self, e: QMouseEvent):
        self.frm_style_stylesheet.fg_color = None
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def lbl_style_close_click(self, e: QMouseEvent = None):
        if e and e.button() != Qt.LeftButton:
            return
        if e:
            obj = self.widget_handler.find_child(self.lbl_style_close)
            if obj:
                obj.EVENT_mouse_press_event(e, False)

        self.frm_style.setVisible(False)

    def _set_custom_colors_to_qcolordialog(self, color_dialog: QColorDialog):
        if not self.frm_style_stylesheet:
            return
        
        for i in range(16):
            color_dialog.setCustomColor(i, QColor("white"))
        # color_dialog.setCustomColor(3, QColor("white"))
        # color_dialog.setCustomColor(5, QColor("white"))
        # color_dialog.setCustomColor(6, QColor("white"))
        # color_dialog.setCustomColor(8, QColor("white"))
        # color_dialog.setCustomColor(13, QColor("white"))
        # color_dialog.setCustomColor(15, QColor("white"))

        if self.frm_style_stylesheet.fg_color:
            color_dialog.setCustomColor(0, QColor(self.frm_style_stylesheet.fg_color))
        if self.frm_style_stylesheet.bg_color:
            color_dialog.setCustomColor(2, QColor(self.frm_style_stylesheet.bg_color))
        if self.frm_style_stylesheet.border_color:
            color_dialog.setCustomColor(4, QColor(self.frm_style_stylesheet.border_color))
        
        if self.frm_style_stylesheet.fg_hover_color:
            color_dialog.setCustomColor(10, QColor(self.frm_style_stylesheet.fg_hover_color))
        if self.frm_style_stylesheet.bg_hover_color:
            color_dialog.setCustomColor(12, QColor(self.frm_style_stylesheet.bg_hover_color))
        if self.frm_style_stylesheet.border_hover_color:
            color_dialog.setCustomColor(14, QColor(self.frm_style_stylesheet.border_hover_color))
        
        if self.frm_style_stylesheet.fg_disabled_color:
            color_dialog.setCustomColor(7, QColor(self.frm_style_stylesheet.fg_disabled_color))
        if self.frm_style_stylesheet.bg_disabled_color:
            color_dialog.setCustomColor(9, QColor(self.frm_style_stylesheet.bg_disabled_color))
        if self.frm_style_stylesheet.border_disabled_color:
            color_dialog.setCustomColor(11, QColor(self.frm_style_stylesheet.border_disabled_color))

    def btn_style_hov_fg_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.fg_hover_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def btn_style_dis_fg_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.fg_disabled_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def btn_style_dis_bg_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.bg_disabled_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def btn_style_hov_bg_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.bg_hover_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()
    
    def btn_style_hov_border_color_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.border_hover_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def btn_style_dis_border_color_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.border_disabled_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def spin_style_hov_border_size_changed(self):
        self.frm_style_stylesheet.border_hover_size = self.spin_style_hov_border_size.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def spin_style_hov_border_radius_changed(self):
        self.frm_style_stylesheet.border_hover_radius = self.spin_style_hov_border_radius.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def spin_style_dis_border_size_changed(self):
        self.frm_style_stylesheet.border_disabled_size = self.spin_style_dis_border_size.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def spin_style_dis_border_radius_changed(self):
        self.frm_style_stylesheet.border_disabled_radius = self.spin_style_dis_border_radius.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def spin_style_gen_font_size_changed(self):
        self.frm_style_stylesheet.font_size = self.spin_style_gen_font_size.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def btn_style_gen_font_click(self):
        result: QFont = self.pick_a_font()
        if result:
            self.frm_style_stylesheet.font_name = result.family()
            self.cmb_style_gen_font.setCurrentText(self.frm_style_stylesheet.font_name)
            self.frm_style_stylesheet.font_size = result.pointSize()
            self.spin_style_gen_font_size.setValue(self.frm_style_stylesheet.font_size)
            self.frm_style_stylesheet.font_bold = result.bold()
            self.chk_style_gen_font_bold.setChecked(self.frm_style_stylesheet.font_bold)
            self.frm_style_stylesheet.font_italic = result.italic()
            self.chk_style_gen_font_italic.setChecked(self.frm_style_stylesheet.font_italic)
            self.frm_style_stylesheet.font_underline = result.underline()
            self.chk_style_gen_font_underline.setChecked(self.frm_style_stylesheet.font_underline)
            self.frm_style_stylesheet.font_strikeout = result.strikeOut()
            self.chk_style_gen_font_strikeout.setChecked(self.frm_style_stylesheet.font_strikeout)

            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def chk_style_gen_font_bold_changed(self):
        self.frm_style_stylesheet.font_bold = self.chk_style_gen_font_bold.isChecked()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def chk_style_gen_font_italic_changed(self):
        self.frm_style_stylesheet.font_italic = self.chk_style_gen_font_italic.isChecked()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def chk_style_gen_font_underline_changed(self):
        self.frm_style_stylesheet.font_underline = self.chk_style_gen_font_underline.isChecked()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def chk_style_gen_font_strikeout_changed(self):
        self.frm_style_stylesheet.font_strikeout = self.chk_style_gen_font_strikeout.isChecked()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def cmb_style_gen_font_changed(self):
        self.frm_style_stylesheet.font_name = self.cmb_style_gen_font.currentText()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def spin_style_gen_border_size_changed(self):
        self.frm_style_stylesheet.border_size = self.spin_style_gen_border_size.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()
    
    def spin_style_gen_border_radius_changed(self):
        self.frm_style_stylesheet.border_radius = self.spin_style_gen_border_radius.value()
        self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
        self._update_frm_style_sample()

    def btn_style_gen_border_color_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.border_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()
    
    def btn_style_gen_fg_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.fg_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def btn_style_gen_bg_click(self, action: dict = None):
        if action:
            if action.get("type") == "add":
                color = action.get("value")
            elif action.get("type") == "remove":
                color = None
        else:
            color = self.pick_a_color(self.frm_style_stylesheet.fg_color)

        if color is not None or action:
            self.frm_style_stylesheet.bg_color = color
            self._set_stylesheet_to_style_frame(self.frm_style_stylesheet)
            self._update_frm_style_sample()

    def btn_style_apply_click(self):
        self._apply_frm_style_data()
        self.frm_style.setVisible(False)

    def pick_a_color(self, initial_color: str) -> str:
        color_dialog = QColorDialog(self)
        color_dialog.setOption(QColorDialog.ShowAlphaChannel)
        
        self._set_custom_colors_to_qcolordialog(color_dialog)
        if initial_color:
            color_dialog.setCurrentColor(QColor(initial_color))
        if color_dialog.exec_() == QColorDialog.Accepted:
            result = color_dialog.selectedColor()
            if result.alpha() != 255:
                return f"rgba({result.getRgb()[0]}, {result.getRgb()[1]}, {result.getRgb()[2]}, {result.getRgb()[3]})"
            else:
                return result.name()
        return None

    def pick_a_font(self) -> QFont:
        start_font_name = self.cmb_style_gen_font.currentText()
        start_font_size = self.spin_style_gen_font_size.value()
        start_font_bold = self.chk_style_gen_font_bold.isChecked()
        start_font_italic = self.chk_style_gen_font_italic.isChecked()
        start_font_underline = self.chk_style_gen_font_underline.isChecked()
        start_font_strikeout = self.chk_style_gen_font_strikeout.isChecked()

        font = QFont(start_font_name, start_font_size)
        font.setBold(start_font_bold)
        font.setItalic(start_font_italic)
        font.setUnderline(start_font_underline)
        font.setStrikeOut(start_font_strikeout)

        font_dialog = QFontDialog()
        font_dialog.setCurrentFont(font)

        if font_dialog.exec_():
            selected_font = font_dialog.currentFont()
            return selected_font
        return None

    def lst_changes_item_changed(self, item: ChangedSettingsItem):
        for i in self.changed_settings:
            if i["key"] == item.me_key:
                i["is_checked"] = item.me_checked
                break
        self.update_save_button_apperance()
        self.update_counter()

    def _apply_frm_style_data(self):
        for item in self.frm_style_affected_list:
            if item["key"].endswith("_stylesheet"):
                if item["value"] != self.frm_style_stylesheet.stylesheet and self.frm_style_stylesheet.stylesheet is not None:
                    self.update_lst_changed_settings(key=item["key"], value=self.frm_style_stylesheet.stylesheet, is_valid=True)
            elif item["key"].endswith("_font_name"):
                if item["value"] != self.frm_style_stylesheet.font_name and self.frm_style_stylesheet.font_name is not None:
                    self.update_lst_changed_settings(key=item["key"], value=self.frm_style_stylesheet.font_name, is_valid=True)
            elif item["key"].endswith("_font_size"):
                if item["value"] != self.frm_style_stylesheet.font_size and self.frm_style_stylesheet.font_size is not None:
                    self.update_lst_changed_settings(key=item["key"], value=self.frm_style_stylesheet.font_size, is_valid=True)
            elif item["key"].endswith("_font_weight"):
                value_for_font_weight = 50
                if self.frm_style_stylesheet.font_bold is True:
                    value_for_font_weight = 75
                if item["value"] != value_for_font_weight:
                    self.update_lst_changed_settings(key=item["key"], value=value_for_font_weight, is_valid=True)
            elif item["key"].endswith("_font_italic"):
                if item["value"] != self.frm_style_stylesheet.font_italic and self.frm_style_stylesheet.font_italic is not None:
                    self.update_lst_changed_settings(key=item["key"], value=self.frm_style_stylesheet.font_italic, is_valid=True)
            elif item["key"].endswith("_font_underline"):
                if item["value"] != self.frm_style_stylesheet.font_underline and self.frm_style_stylesheet.font_underline is not None:
                    self.update_lst_changed_settings(key=item["key"], value=self.frm_style_stylesheet.font_underline, is_valid=True)
            elif item["key"].endswith("_font_strikeout"):
                if item["value"] != self.frm_style_stylesheet.font_strikeout and self.frm_style_stylesheet.font_strikeout is not None:
                    self.update_lst_changed_settings(key=item["key"], value=self.frm_style_stylesheet.font_strikeout, is_valid=True)
            
            for record in self.changed_settings:
                if record["key"] == item["key"]:
                    item["value"] = record["value"]
                    break
                    
    def _populate_frm_style(self):
        self.rbt_style_enabled.setChecked(True)
        self.lbl_style_sample.setEnabled(True)

        style_final = self._if_multi_style_return_stylesheet_object(self.frm_style_affected_list)

        if style_final is None:
            style_final = StyleSheet()

            for item in self.frm_style_affected_list:
                style = None
                if item["key"].endswith("_stylesheet"):
                    style = StyleSheet(widget_name=item["type"])
                    style.stylesheet = item["value"]
                    style_final.merge_stylesheet(style, merge_widget_name=True)
                    style = None
                elif item["key"].endswith("_font_name"):
                    style = StyleSheet()
                    style.font_name = item["value"]
                elif item["key"].endswith("_font_size"):
                    style = StyleSheet()
                    style.font_size = item["value"]
                elif item["key"].endswith("_font_weight"):
                    style = StyleSheet()
                    if item["value"] == 75:
                        style.font_bold = True
                    else:
                        style.font_bold = False
                elif item["key"].endswith("_font_italic"):
                    style = StyleSheet()
                    style.font_italic = item["value"]
                elif item["key"].endswith("_font_underline"):
                    style = StyleSheet()
                    style.font_underline = item["value"]
                elif item["key"].endswith("_font_strikeout"):
                    style = StyleSheet()
                    style.font_strikeout = item["value"]
                
                if style:
                    style_final.merge_stylesheet(style)

        self.frm_style_stylesheet = style_final
        
        if self.frm_style_stylesheet.widget_name == "QPushButton":
            self.btn_style_sample.setVisible(True)
            self.lbl_style_sample.setVisible(False)
        else:
            self.btn_style_sample.setVisible(False)
            self.lbl_style_sample.setVisible(True)

        self._set_stylesheet_to_style_frame(style_final)
        self._update_frm_style_sample()

    def _if_multi_style_return_stylesheet_object(self, affected_list: list) -> StyleSheet:
        count = 0
        result = None
        style_list = []
        for item in affected_list:
            if item["key"].endswith("_stylesheet"):
                if result is None:
                    result = StyleSheet()
                    result.widget_name = item["type"]
                    result.stylesheet = item["value"]
                else:
                    item_style_obj = StyleSheet()
                    item_style_obj.widget_name = item["type"]
                    item_style_obj.stylesheet = item["value"]
                    style_list.append(item_style_obj)

                count += 1
        
        if count < 2:
            return None

        result.normalize_stylesheet_values(style_list)

        return result

    def _update_frm_style_sample(self):
        if self.lbl_style_sample.isVisible():
            self.lbl_style_sample.setStyleSheet(self.frm_style_stylesheet.get_stylesheet("QLabel"))
        if self.btn_style_sample.isVisible():
            self.btn_style_sample.setStyleSheet(self.frm_style_stylesheet.get_stylesheet("QPushButton"))

    def _set_stylesheet_to_style_frame(self, style: StyleSheet):
        fg_color = style.fg_color if style.fg_color is not None else ""
        bg_color = style.bg_color if style.bg_color is not None else ""
        border_size = style.border_size if style.border_size is not None else 0
        border_color = style.border_color if style.border_color is not None else ""
        border_radius = style.border_radius if style.border_radius is not None else 0
        font_name = style.font_name if style.font_name is not None else "Arial"
        font_size = style.font_size if style.font_size is not None else 12
        font_bold = style.font_bold if style.font_bold is not None else False
        font_italic = style.font_italic if style.font_italic is not None else False
        font_underline = style.font_underline if style.font_underline is not None else False
        font_strikeout = style.font_strikeout if style.font_strikeout is not None else False
        fg_hover_color = style.fg_hover_color if style.fg_hover_color is not None else ""
        bg_hover_color = style.bg_hover_color if style.bg_hover_color is not None else ""
        border_hover_size = style.border_hover_size if style.border_hover_size is not None else 0
        border_hover_color = style.border_hover_color if style.border_hover_color is not None else ""
        border_hover_radius = style.border_hover_radius if style.border_hover_radius is not None else 0
        fg_disabled_color = style.fg_disabled_color if style.fg_disabled_color is not None else ""
        bg_disabled_color = style.bg_disabled_color if style.bg_disabled_color is not None else ""
        border_disabled_size = style.border_disabled_size if style.border_disabled_size is not None else 0
        border_disabled_color = style.border_disabled_color if style.border_disabled_color is not None else ""
        border_disabled_radius = style.border_disabled_radius if style.border_disabled_radius is not None else 0

        if fg_color:
            self.lbl_style_gen_fg.setStyleSheet(f"background-color: {fg_color};")
            self.lbl_style_gen_fg.setText(fg_color)
        else:
            self.lbl_style_gen_fg.setStyleSheet("")
            self.lbl_style_gen_fg.setText("-")
        if bg_color:
            self.lbl_style_gen_bg.setStyleSheet(f"background-color: {bg_color};")
            self.lbl_style_gen_bg.setText(bg_color)
        else:
            self.lbl_style_gen_bg.setStyleSheet("")
            self.lbl_style_gen_bg.setText("-")
        if border_size < 0:
            border_size = 0
        elif border_size > self.spin_style_gen_border_size.maximum():
            border_size = self.spin_style_gen_border_size.maximum()
        self.spin_style_gen_border_size.setValue(border_size)
        if border_color:
            self.lbl_style_gen_border_color.setStyleSheet(f"background-color: {border_color};")
            self.lbl_style_gen_border_color.setText(border_color)
        else:
            self.lbl_style_gen_border_color.setStyleSheet("")
            self.lbl_style_gen_border_color.setText("-")
        if border_radius < 0:
            border_radius = 0
        elif border_radius > self.spin_style_gen_border_radius.maximum():
            border_radius = self.spin_style_gen_border_radius.maximum()
        self.spin_style_gen_border_radius.setValue(border_radius)
        self.cmb_style_gen_font.setCurrentText(font_name)
        if font_size < 0:
            font_size = 0
        elif font_size > self.spin_style_gen_font_size.maximum():
            font_size = self.spin_style_gen_font_size.maximum()
        self.spin_style_gen_font_size.setValue(font_size)
        self.chk_style_gen_font_bold.setChecked(font_bold)
        self.chk_style_gen_font_italic.setChecked(font_italic)
        self.chk_style_gen_font_underline.setChecked(font_underline)
        self.chk_style_gen_font_strikeout.setChecked(font_strikeout)
        
        if fg_hover_color:
            self.lbl_style_hov_fg.setStyleSheet(f"background-color: {fg_hover_color};")
            self.lbl_style_hov_fg.setText(fg_hover_color)
        else:
            self.lbl_style_hov_fg.setStyleSheet("")
            self.lbl_style_hov_fg.setText("-")
        if bg_hover_color:
            self.lbl_style_hov_bg.setStyleSheet(f"background-color: {bg_hover_color};")
            self.lbl_style_hov_bg.setText(bg_hover_color)
        else:
            self.lbl_style_hov_bg.setStyleSheet("")
            self.lbl_style_hov_bg.setText("-")
        if border_hover_size < 0:
            border_hover_size = 0
        elif border_hover_size > self.spin_style_hov_border_size.maximum():
            border_hover_size = self.spin_style_hov_border_size.maximum()
        self.spin_style_hov_border_size.setValue(border_hover_size)
        if border_hover_color:
            self.lbl_style_hov_border_color.setStyleSheet(f"background-color: {border_hover_color};")
            self.lbl_style_hov_border_color.setText(border_hover_color)
        else:
            self.lbl_style_hov_border_color.setStyleSheet("")
            self.lbl_style_hov_border_color.setText("-")
        if border_hover_radius < 0:
            border_hover_radius = 0
        elif border_hover_radius > self.spin_style_hov_border_radius.maximum():
            border_hover_radius = self.spin_style_hov_border_radius.maximum()
        self.spin_style_hov_border_radius.setValue(border_hover_radius)

        if fg_disabled_color:
            self.lbl_style_dis_fg.setStyleSheet(f"background-color: {fg_disabled_color};")
            self.lbl_style_dis_fg.setText(fg_disabled_color)
        else:
            self.lbl_style_dis_fg.setStyleSheet("")
            self.lbl_style_dis_fg.setText("-")
        if bg_disabled_color:
            self.lbl_style_dis_bg.setStyleSheet(f"background-color: {bg_disabled_color};")
            self.lbl_style_dis_bg.setText(bg_disabled_color)
        else:
            self.lbl_style_dis_bg.setStyleSheet("")
            self.lbl_style_dis_bg.setText("-")
        if border_disabled_size < 0:
            border_disabled_size = 0
        elif border_disabled_size > self.spin_style_dis_border_size.maximum():
            border_disabled_size = self.spin_style_dis_border_size.maximum()
        self.spin_style_dis_border_size.setValue(border_disabled_size)
        if border_disabled_color:
            self.lbl_style_dis_border_color.setStyleSheet(f"background-color: {border_disabled_color};")
            self.lbl_style_dis_border_color.setText(border_disabled_color)
        else:
            self.lbl_style_dis_border_color.setStyleSheet("")
            self.lbl_style_dis_border_color.setText("-")
        if border_disabled_radius < 0:
            border_disabled_radius = 0
        elif border_disabled_radius > self.spin_style_dis_border_radius.maximum():
            border_disabled_radius = self.spin_style_dis_border_radius.maximum()
        self.spin_style_dis_border_radius.setValue(border_disabled_radius)

        self.ignore_txt_style_stylesheet_text_changes = True
        self.txt_style_stylesheet.setText(style.stylesheet)
        self.ignore_txt_style_stylesheet_text_changes = False

    def feedback_function(self, data: dict, action: str = None):
        if action == "set_style":
            self.frm_style_affected_list = data["affected_keys"]
            self.frm_style.setVisible(True)
            self._populate_frm_style()
            return
        elif action == "set_style_default":
            for item in data["affected_keys"]:
                self.update_lst_changed_settings(item["key"], self._stt.get_setting_dict(item["key"])["default_value"], True)
            return
        elif action == "def_hint_edit":
            utility_cls.DefHintManager(self._stt, self)

        for item in data["affected_keys"]:
            self.update_lst_changed_settings(item["key"], data["value"], data["is_valid"])

    def show_widget_settings(self, e: QMouseEvent = None):
        if e is not None and e.button() != Qt.LeftButton:
            return

        self.frm_style.setVisible(False)
        self.update_widgets_apperance(active_settings_group="widget_settings")
        if e:
            self.widget_handler.find_child(self.frm_menu_widget).EVENT_mouse_press_event(e, False)
        self.reset_area_settings()

        self.item_group_manager.show_widget_settings()

    def show_window_settings(self, e: QMouseEvent = None):
        if e is not None and e.button() != Qt.LeftButton:
            return

        self.frm_style.setVisible(False)
        self.update_widgets_apperance(active_settings_group="window_settings")
        if e:
            self.widget_handler.find_child(self.frm_menu_window).EVENT_mouse_press_event(e, False)
        self.reset_area_settings()

        self.item_group_manager.show_dialog_settings()

    def show_startup_settings(self, e: QMouseEvent = None):
        if e is not None and e.button() != Qt.LeftButton:
            return

        self.frm_style.setVisible(False)
        self.update_widgets_apperance(active_settings_group="startup_settings")
        if e:
            self.widget_handler.find_child(self.frm_menu_startup).EVENT_mouse_press_event(e, False)
        self.reset_area_settings()

        self.item_group_manager.show_block_settings()

    def show_general_settings(self, e: QMouseEvent = None):
        if e is not None and e.button() != Qt.LeftButton:
            return

        self.frm_style.setVisible(False)
        self.update_widgets_apperance(active_settings_group="general_settings")
        if e:
            self.widget_handler.find_child(self.frm_menu_general).EVENT_mouse_press_event(e, False)
        self.reset_area_settings()

        self.item_group_manager.show_general_settings()

    def _make_affected_keys_list(self, item_data: list) -> list:
        affected_keys = []
        for item in item_data:
            item_set_dict = self._stt.get_setting_dict(item[0])

            value = ""
            for changed_item in self.changed_settings:
                if changed_item["key"] == item[0]:
                    value = changed_item["value"]
                    break
            else:
                value = item_set_dict["value"]

            aff_dict = self.item_affected_keys_empty_dictionary()
            aff_dict["key"] = item[0]
            aff_dict["type"] = item[1]
            aff_dict["value"] = value
            aff_dict["min"] = item_set_dict["min_value"]
            aff_dict["max"] = item_set_dict["max_value"]
            affected_keys.append(aff_dict)
            
        return affected_keys

    def fast_update_lst_changed_setting_no_existing_check(self, key: str, value):
        # Update item in self.changed_settings
        item = self.item_changed_empty_dictionary()
        item["key"] = key
        item["value"] = value
        item["is_valid"] = True
        if str(self.getv(key)) == str(value):
            item["is_checked"] = False
        else:
            item["is_checked"] = True
        
        # Update List item apperance
        widget_item_width = 337
        list_item = QListWidgetItem()
        self.lst_changes.addItem(list_item)
        
        item_data = {
            "key": key,
            "new_value": value,
            "old_value": self.getv(key),
            "is_valid": item["is_valid"],
            "update_changed_settings_list_function": self.lst_changes_item_changed,
            "size_changed_function": self.update_change_settings_item_height,
            "main_win": self,
            "width": widget_item_width,
            "list_item": list_item
        }
        item_data["is_checked"] = item["is_checked"]

        item_widget = ChangedSettingsItem(self.lst_changes, self._stt, item_data, widget_handler=self.widget_handler)
        new_widget_width = item_widget.size().width()
        self.lst_changes.setItemWidget(list_item, item_widget)
        list_item.setSizeHint(item_widget.size())

        self.changed_settings.append(item)

        self.lst_changes.addItem(list_item)

        return new_widget_width
    
    def update_lst_changed_settings(self, key: str, value, is_valid: bool):
        # Update item in self.changed_settings
        has_data = False
        for item in self.changed_settings:
            if item["key"] == key:
                if str(self.getv(key)) == str(value) or not is_valid:
                    item["is_checked"] = False
                else:
                    item["is_checked"] = True
                item["value"] = value
                item["is_valid"] = is_valid
                has_data = True
                break
        else:
            item = self.item_changed_empty_dictionary()
            item["key"] = key
            item["value"] = value
            item["is_valid"] = is_valid
            if is_valid:
                item["is_checked"] = True
            else:
                item["is_checked"] = False
            self.changed_settings.append(item)
        
        # Find max widget item width
        widget_item_width = 337
        for i in range(self.lst_changes.count()):
            widget_item_width = max(widget_item_width, self.lst_changes.itemWidget(self.lst_changes.item(i)).size().width())

        # Update List item apperance
        new_widget_width = 0
        if has_data:
            for i in range(self.lst_changes.count()):
                widget_item: ChangedSettingsItem = self.lst_changes.itemWidget(self.lst_changes.item(i))
                if widget_item.me_key == key:
                    widget_item.set_new_value(value)
                    widget_item.set_valid_state(is_valid)
                    widget_item.set_check_state(item["is_checked"])
                    break
        else:
            list_item = QListWidgetItem()
            self.lst_changes.addItem(list_item)
            
            item_data = {
                "key": key,
                "new_value": value,
                "old_value": self.getv(key),
                "is_valid": is_valid,
                "update_changed_settings_list_function": self.lst_changes_item_changed,
                "size_changed_function": self.update_change_settings_item_height,
                "main_win": self,
                "width": widget_item_width,
                "list_item": list_item
            }
            item_data["is_checked"] = item["is_checked"]

            item_widget = ChangedSettingsItem(self.lst_changes, self._stt, item_data, widget_handler=self.widget_handler)
            new_widget_width = item_widget.size().width()
            self.lst_changes.setItemWidget(list_item, item_widget)
            list_item.setSizeHint(item_widget.size())


        # Determine new self.lst_changes items width
        if new_widget_width > widget_item_width:
            for i in range(self.lst_changes.count()):
                widget_item: ChangedSettingsItem = self.lst_changes.itemWidget(self.lst_changes.item(i))
                widget_item.resize_me(new_widget_width)
                self.lst_changes.item(i).setSizeHint(widget_item.size())

        # Update save button
        self.update_save_button_apperance()
        self.update_counter()

    def update_change_settings_item_height(self, list_item: QListWidgetItem):
        widget_item: ChangedSettingsItem = self.lst_changes.itemWidget(list_item)
        list_item.setSizeHint(widget_item.size())

    def update_counter(self):
        # Update counter
        count_active_settings = len([x for x in self.changed_settings if x["is_checked"]])
        self.lbl_counter.setText(self.getl("app_settings_lbl_counter").replace("#1", str(len(self.changed_settings))).replace("#2", str(count_active_settings)))

    def update_save_button_apperance(self):
        for item in self.changed_settings:
            if item["is_checked"]:
                self.btn_save.setEnabled(True)
                self.btn_apply.setEnabled(True)
                self.btn_export.setEnabled(False)
                self.btn_import.setEnabled(False)
                self.btn_import_from_file.setEnabled(False)
                break
        else:
            self.btn_save.setEnabled(False)
            self.btn_apply.setEnabled(False)
            self.btn_export.setEnabled(True)
            self.btn_import.setEnabled(True)
            self.btn_import_from_file.setEnabled(True)

    def populate_item_value_default_desc_recomm_min_max(self, data: dict) -> None:
        key = data["key"]
        
        if not key:
            text = ""
            top_counted_value = []
            for i in data["affected_keys"]:
                if data["value"] is None:
                    value_to_append = ""
                    for item in self.changed_settings:
                        if item["key"] == i["key"]:
                            value_to_append = str(item["value"])
                            break
                    else:
                        value_to_append = str(self.getv(i["key"]))

                    top_counted_value.append(value_to_append)

                text += f"{i['key']}, "

            text = "\n" + text.strip(" ,")
            if data["value"] is None:
                if top_counted_value:
                    most_common_value = Counter(top_counted_value).most_common(1)[0][0]
                    if most_common_value is None:
                        most_common_value = ""
                    data["value"] = most_common_value
                else:
                    data["value"] = ""
            data["desc"] = self.getl("app_settings_desc_list_of_affected_keys") + text
            data["recomm"] = self.getl("app_settings_no_recommended_value")
            data["default"] = None
            data["min"] = None
            data["max"] = None
            return

        for item in self.changed_settings:
            if item["key"] == key:
                data["value"] = str(item["value"])
                break
        else:
            data["value"] = str(self.getv(key))
        
        if data["value"] is None:
            data["value"] = ""

        desc_text = self.getl(f"{key}_desc")
        if not desc_text:
            if data["key"].endswith("_stylesheet"):
                if "_win_" in data["key"]:
                    desc_text = self.getl("stylesheet_win_desc")
                else:
                    desc_text = self.getl("stylesheet_desc")
            elif data["key"].endswith("_enabled"):
                desc_text = self.getl("app_sett_enabled_desc")
            elif data["key"].endswith("_visible"):
                desc_text = self.getl("app_sett_visible_desc")
            elif data["key"].endswith("_icon_path"):
                desc_text = self.getl("app_sett_icon_path_desc")
            elif data["key"].endswith("_animation_path"):
                desc_text = self.getl("app_sett_animation_path_desc")
            elif data["key"].endswith("_shortcut"):
                desc_text = self.getl("app_sett_shortcut_desc")
            elif data["key"].endswith("_frame_shape"):
                desc_text = self.getl("app_sett_style_frame_shape_desc")
            elif data["key"].endswith("_frame_shadow"):
                desc_text = self.getl("app_sett_style_frame_shadow_desc")
            elif data["key"].endswith("_line_width"):
                desc_text = self.getl("app_sett_style_line_width_desc")

        recomm_text = self.getl(f"{key}_recomm") or self.getl("app_settings_no_recommended_value")

        data["desc"] = desc_text
        data["recomm"] = recomm_text
        data["default"] = str(self._stt.get_setting_dict(key)["default_value"])
        data["min"] = self._stt.get_setting_dict(key)["min_value"]
        data["max"] = self._stt.get_setting_dict(key)["max_value"]

    def item_changed_empty_dictionary(self) -> dict:
        result = {
            "key": "",
            "value": None,
            "is_valid": False,
            "is_checked": False
        }
        return result
    
    def item_group_empty_dictionary(self) -> dict:
        result = {
            "width": self.area_settings.contentsRect().width() - 20,
            "name": "",
            "main_win": self,
            "empty_dict_function": self.item_data_empty_dictionary,
            "make_affected_keys_list_function": self._make_affected_keys_list,
            "populate_item_value_default_desc_recomm_min_max_function": self.populate_item_value_default_desc_recomm_min_max,
            "loading_function": self._show_loading_label
        }
        return result

    def item_data_empty_dictionary(self) -> dict:
        result = {
            "width": self.area_settings.contentsRect().width() - 20,
            "input_box_width": None,
            "name": "",
            "key": "",
            "value": None,
            "default": None,
            "desc": "",
            "recomm": "",
            "min": None,
            "max": None,
            "has_font_settings": False,
            "affected_keys": [],
            "feedback_function": self.feedback_function,
            "input_center": True
        }
        return result

    def item_affected_keys_empty_dictionary(self) -> dict:
        result = {
            "key": "",
            "type": "",
            "value": None,
            "max": None,
            "min": None,
            "is_valid": False
        }
        return result

    def reset_area_settings(self):
        self.area_settings_widget = QWidget(self.area_settings)
        self.area_settings_widget_layout = QVBoxLayout(self.area_settings_widget)
        self.area_settings.setWidget(self.area_settings_widget)
        self.area_settings_widget.setLayout(self.area_settings_widget_layout)
        self.area_settings.setWidgetResizable(True)
        self.area_settings_widget_layout.setContentsMargins(0, 0, 0, 0)
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.area_settings_widget_layout.addItem(spacer)
        if self.item_group_manager:
            self.item_group_manager.area_settings_widget = self.area_settings_widget

    def update_widgets_apperance(self, active_settings_group: str):
        bg_inactive_color = "#000000"
        bg_active_color = "#00006c"
        label_stylesheet = "QLabel:hover {border: 0px;}"

        inactive_stylesheet = f"QFrame {{color: #c3c3c3; background-color: {bg_inactive_color};}} "
        active_stylesheet = f"QFrame {{color: #ffff00; background-color: {bg_active_color};}} "
        hover_stylesheet = "QFrame:hover {border: 1px solid #ffffff;}"

        active = active_stylesheet + hover_stylesheet
        inactive = inactive_stylesheet + hover_stylesheet

        # Set all settings groups to inactive
        self.frm_menu_general.setStyleSheet(inactive)
        self.lbl_menu_general_icon.setStyleSheet(label_stylesheet)
        self.lbl_menu_general_title.setStyleSheet(label_stylesheet)
        
        self.frm_menu_startup.setStyleSheet(inactive)
        self.lbl_menu_startup_icon.setStyleSheet(label_stylesheet)
        self.lbl_menu_startup_title.setStyleSheet(label_stylesheet)

        self.frm_menu_widget.setStyleSheet(inactive)
        self.lbl_menu_widget_icon.setStyleSheet(label_stylesheet)
        self.lbl_menu_widget_title.setStyleSheet(label_stylesheet)

        self.frm_menu_window.setStyleSheet(inactive)
        self.lbl_menu_window_icon.setStyleSheet(label_stylesheet)
        self.lbl_menu_window_title.setStyleSheet(label_stylesheet)

        self.frm_menu_search.setStyleSheet(inactive)
        self.lbl_menu_search_icon.setStyleSheet(label_stylesheet)
        self.lbl_menu_search_title.setStyleSheet(label_stylesheet)

        # Set active settings group
        if active_settings_group == "general_settings":
            self.frm_menu_general.setStyleSheet(active)
            self.lbl_menu_general_icon.setStyleSheet(label_stylesheet)
            self.lbl_menu_general_title.setStyleSheet(label_stylesheet)
        elif active_settings_group == "startup_settings":
            self.frm_menu_startup.setStyleSheet(active)
            self.lbl_menu_startup_icon.setStyleSheet(label_stylesheet)
            self.lbl_menu_startup_title.setStyleSheet(label_stylesheet)
        elif active_settings_group == "widget_settings":
            self.frm_menu_widget.setStyleSheet(active)
            self.lbl_menu_widget_icon.setStyleSheet(label_stylesheet)
            self.lbl_menu_widget_title.setStyleSheet(label_stylesheet)
        elif active_settings_group == "window_settings":
            self.frm_menu_window.setStyleSheet(active)
            self.lbl_menu_window_icon.setStyleSheet(label_stylesheet)
            self.lbl_menu_window_title.setStyleSheet(label_stylesheet)
        elif active_settings_group == "search_settings":
            self.frm_menu_search.setStyleSheet(active)
            self.lbl_menu_search_icon.setStyleSheet(label_stylesheet)
            self.lbl_menu_search_title.setStyleSheet(label_stylesheet)
        
        return active

    def _load_win_position(self):
        if "app_settings_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("app_settings_win_geometry")
            x = g.setdefault("pos_x", self.pos().x())
            y = g.setdefault("pos_y", self.pos().y())
            self.move(x, y)
            self.chk_menu_search_whole_words.setChecked(g.get("chk_menu_search_whole_words", False))
            self.chk_menu_search_matchcase.setChecked(g.get("chk_menu_search_matchcase", False))
            self.txt_menu_search.setText(g.get("txt_menu_search", ""))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not self._can_exit():
            a0.ignore()
            return None

        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "app_settings_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("app_settings_win_geometry", {}, save_to_file=True)

        g = self.get_appv("app_settings_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["chk_menu_search_whole_words"] = self.chk_menu_search_whole_words.isChecked()
        g["chk_menu_search_matchcase"] = self.chk_menu_search_matchcase.isChecked()
        g["txt_menu_search"] = self.txt_menu_search.text()

        self.get_appv("cm").remove_all_context_menu()
        
        if self.item_group_manager:
            self.item_group_manager.close_me()
            self.item_group_manager = None

        for child in self.children():
            if isinstance(child, utility_cls.Notification):
                child.close_me()

        UTILS.LogHandler.add_log_record("#1 dialog closed", ["Application settings"])
        UTILS.DialogUtility.on_closeEvent(self, close_children=False)
        
    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _can_exit(self) -> bool:
        data_changed = False
        for item in self.changed_settings:
            if item["is_checked"]:
                data_changed = True
                break

        if data_changed:
            msg_dict = {
                "title": self.getl("app_settings_exit_msg_save_title"),
                "text": self.getl("app_settings_exit_msg_save_text"),
                "position": "center",
                "pos_center": False,
                "buttons": [
                    [10, self.getl("btn_yes"), "", None, True],
                    [20, self.getl("btn_no"), "", None, True],
                    [30, self.getl("btn_cancel"), "", None, True],
                ]
            }
            utility_cls.MessageQuestion(self._stt, self, msg_dict)
            if msg_dict["result"] == 10:
                self.btn_save_click(close_dialog=False)
                return True
            elif msg_dict["result"] == 20:
                return True
            else:
                return False
        return True

    def btn_cancel_click(self):
        self.close()
    
    def btn_save_click(self, e = None, close_dialog: bool = True):
        self.setDisabled(True)
        result, errors = self.save_settings()

        if close_dialog:
            self.hide()
            
        self._save_settings_message(result, errors=errors)

        if close_dialog:
            self.close()

    def _save_settings_message(self, text_replacement: str, source_function: str = None, errors: int = None):
        if errors:
            error_text = self.getl("app_settings_save_error_msg_text").replace("#1", str(errors))
            msg_dict = {
                "title": self.getl("warning_text"),
                "text": error_text,
                "icon_path": self.getv("warning_icon_path")
            }
            self._dont_clear_menu = True
            utility_cls.MessageInformation(self._stt, self, msg_dict, app_modal=True)

        # Notification
        notif_data1 = {
            "title": self.getl("app_settings_save_notiffication_title"),
            "text": self.getl("app_settings_save_notiffication_text")
        }
        notif_data2 = {
            "title": self.getl("app_settings_save_notiffication_title"),
            "text": self.getl("app_settings_save_notiffication_please_restart_app_text"),
            "timer": 15000,
            "show_ok": True

        }
        if source_function == "btn_apply_click":
            notif_data1["timer"] = 5000
            notif_data1["position"] = "bottom left"
            utility_cls.Notification(self._stt, self, notif_data1)
            notif_data2["position"] = "top left"
            utility_cls.Notification(self._stt, self, notif_data2)
            return
        else:
            notif_data1["timer"] = 3000
            notif_data1["position"] = "bottom right"
            utility_cls.Notification(self._stt, self._parent_widget, notif_data1)
            notif_data2["position"] = "top right"
            utility_cls.Notification(self._stt, self._parent_widget, notif_data2)

        # Message
        msg_dict = {
            "title": self.getl("app_settings_save_msg_save_title"),
            "text": self.getl("app_settings_save_msg_save_text").replace("#1", str(text_replacement)),
            "icon_path": self.getv("app_settings_win_icon_path")
        }
        utility_cls.MessageInformation(self._stt, self, msg_dict, app_modal=False)

    def btn_apply_click(self):
        self.setDisabled(True)
        result, errors = self.save_settings()
        self._save_settings_message(result, source_function="btn_apply_click", errors=errors)
        self.update_save_button_apperance()

        self.reset_area_settings()
        if self.item_group_manager:
            self.item_group_manager.close_me()
        self.item_group_manager = ItemsGroupManager(
            self._stt,
            self.area_settings_widget,
            {"item_group_empty_dictionary": self.item_group_empty_dictionary, "main_win": self, "loading_function": self._show_loading_label}
            )

        if self.widget_handler:
            self.widget_handler.close_me()
        self.load_widgets_handler()

        self.show_general_settings()
        QCoreApplication.processEvents()
        self.setDisabled(False)

    def save_settings(self) -> int:
        self.frm_working.setVisible(True)
        self.prg_working.setMaximum(100)
        self.prg_working.raise_()
        QCoreApplication.processEvents()

        updated_settings = {}
        updated_settings["keys_list"] = []

        count = 0
        value_error = 0
        for idx, item in enumerate(self.changed_settings):
            prg_value = int((idx + 1) / len(self.changed_settings) * 100)
            self.prg_working.setValue(prg_value)
            QCoreApplication.processEvents()

            if not item["is_checked"]:
                continue

            key = item["key"]
            value = item["value"]

            if type(self.getv(key)) == int:
                value = int(value)
            elif type(self.getv(key)) == float:
                value = float(value)
            elif type(self.getv(key)) == bool:
                value = bool(value)
            elif type(self.getv(key)) == str:
                value = str(value)
            else:
                UTILS.TerminalUtility.WarningMessage("Error. Unknown settings value type. Key: #1", [key], variables=[["key", key], ["value", value], ["'old setting value'", self.getv(key)]])
                continue

            try:
                old_s_val = self.getv(key)
                result = self._stt.set_setting_value(key, value)
                if result:
                    UTILS.LogHandler.add_log_record("Changed setting #1\nOld value: #2\nNew value: #3", [key, old_s_val, value])
            except ValueError:
                UTILS.TerminalUtility.WarningMessage("Value error. Unable to update setting with key #1", [key], variables=[["key", key], ["value", value]])
                value_error += 1
                continue

            if not result:
                UTILS.TerminalUtility.WarningMessage("Error: Can't save settings. Key: #1", [key], variables=[["key", key], ["value", value], ["'old setting value'", self.getv(key)]])
                continue
            
            updated_settings["keys_list"].append(key)

            count += 1
        
        UTILS.LogHandler.add_log_record("Application settings updated #1 settings changed", [count])
        self.changed_settings = []
        
        for i in range(self.lst_changes.count()):
            item_widget: ChangedSettingsItem = self.lst_changes.itemWidget(self.lst_changes.item(i))
            item_widget.close_me()

        self.lst_changes.clear()
        self.lbl_counter.setText("")

        # Save Settings
        result = self._stt.save_settings()
        if result:
            UTILS.TerminalUtility.WarningMessage("Error. Can't save settings. Reason: #1", [result])
            QMessageBox.information(self, self.getl("app_settings_save_error_msg_save_title"), self.getl("app_settings_save_error_msg_save_text") + f"\n{result}")
            self.get_appv("log").write_log("Error. Saving settings. : " + result)
        else:
            UTILS.LogHandler.add_log_record("Application settings saved in file")
            self.get_appv("log").write_log("AppSettings. Settings updated.")

        self.get_appv("signal").send_app_settings_updated(updated_settings)

        self.frm_working.setVisible(False)
        QCoreApplication.processEvents()

        return count, value_error

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.btn_export: QPushButton = self.findChild(QPushButton, "btn_export")
        self.btn_import: QPushButton = self.findChild(QPushButton, "btn_import")
        self.lbl_counter: QLabel = self.findChild(QLabel, "lbl_counter")

        self.area_settings: QScrollArea = self.findChild(QScrollArea, "area_settings")
        self.lst_changes: QListWidget = self.findChild(QListWidget, "lst_changes")

        self.btn_save: QPushButton = self.findChild(QPushButton, "btn_save")
        self.btn_apply: QPushButton = self.findChild(QPushButton, "btn_apply")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")

        self.frm_menu: QFrame = self.findChild(QFrame, "frm_menu")

        # Working frame
        self.frm_working: QFrame = self.findChild(QFrame, "frm_working")
        self.frm_working_info: QFrame = self.findChild(QFrame, "frm_working_info")
        self.lbl_working_title: QLabel = self.findChild(QLabel, "lbl_working_title")
        self.prg_working: QProgressBar = self.findChild(QProgressBar, "prg_working")

        # Loading label
        self.lbl_loading: QLabel = self.findChild(QLabel, "lbl_loading")
        self.frm_loading: QFrame = self.findChild(QFrame, "frm_loading")

        # Advanced settings
        self.btn_adv_show: QPushButton = self.findChild(QPushButton, "btn_adv_show")
        self.frm_adv: QFrame = self.findChild(QFrame, "frm_adv")
        self.lbl_adv_title: QLabel = self.findChild(QLabel, "lbl_adv_title")
        self.txt_adv_find: QLineEdit = self.findChild(QLineEdit, "txt_adv_find")
        self.btn_adv_clear_filter: QPushButton = self.findChild(QPushButton, "btn_adv_clear_filter")
        self.lbl_adv_counter: QLabel = self.findChild(QLabel, "lbl_adv_counter")
        self.lst_adv: QListWidget = self.findChild(QListWidget, "lst_adv")
        self.btn_adv_select_all: QPushButton = self.findChild(QPushButton, "btn_adv_select_all")
        self.btn_adv_select_none: QPushButton = self.findChild(QPushButton, "btn_adv_select_none")
        self.btn_adv_swap_selection: QPushButton = self.findChild(QPushButton, "btn_adv_swap_selection")
        self.btn_adv_show_checked: QPushButton = self.findChild(QPushButton, "btn_adv_show_checked")
        self.lbl_adv_close: QLabel = self.findChild(QLabel, "lbl_adv_close")
        self.lbl_adv_info: QLabel = self.findChild(QLabel, "lbl_adv_info")
        self.txt_adv_new_value: QTextEdit = self.findChild(QTextEdit, "txt_adv_new_value")
        self.btn_adv_apply: QPushButton = self.findChild(QPushButton, "btn_adv_apply")
        self.lbl_adv_animated_gif: QLabel = self.findChild(QLabel, "lbl_adv_animated_gif")
        # Advanced settings  -  Progress frame
        self.frm_adv_progress: QFrame = self.findChild(QFrame, "frm_adv_progress")
        self.lbl_adv_progress: QLabel = self.findChild(QLabel, "lbl_adv_progress")
        self.prg_adv_progress: QProgressBar = self.findChild(QProgressBar, "prg_adv_progress")
        self.btn_adv_abort: QPushButton = self.findChild(QPushButton, "btn_adv_abort")

        # Import options
        self.frm_import: QFrame = self.findChild(QFrame, "frm_import")
        self.lbl_import_title: QLabel = self.findChild(QLabel, "lbl_import_title")
        self.lbl_import_close: QLabel = self.findChild(QLabel, "lbl_import_close")
        self.rbt_import_custom: QRadioButton = self.findChild(QRadioButton, "rbt_import_custom")
        self.rbt_import_all: QRadioButton = self.findChild(QRadioButton, "rbt_import_all")
        self.grp_import_custom: QGroupBox = self.findChild(QGroupBox, "grp_import_custom")
        self.grp_import_all: QGroupBox = self.findChild(QGroupBox, "grp_import_all")
        self.chk_import_all_style: QCheckBox = self.findChild(QCheckBox, "chk_import_all_style")
        self.chk_import_button_style: QCheckBox = self.findChild(QCheckBox, "chk_import_button_style")
        self.chk_import_font: QCheckBox = self.findChild(QCheckBox, "chk_import_font")
        self.chk_import_icon: QCheckBox = self.findChild(QCheckBox, "chk_import_icon")
        self.chk_import_sound: QCheckBox = self.findChild(QCheckBox, "chk_import_sound")
        self.lbl_import_all_desc: QLabel = self.findChild(QLabel, "lbl_import_all_desc")
        self.btn_import_from_file: QPushButton = self.findChild(QPushButton, "btn_import_from_file")

        # Style frame
        self.frm_style: QFrame = self.findChild(QFrame, "frm_style")
        self.lbl_style_title: QLabel = self.findChild(QLabel, "lbl_style_title")
        self.lbl_style_close: QLabel = self.findChild(QLabel, "lbl_style_close")
        self.frm_style_sample: QFrame = self.findChild(QFrame, "frm_style_sample")
        self.lbl_style_sample: QLabel = self.findChild(QLabel, "lbl_style_sample")
        self.btn_style_sample: QPushButton = self.findChild(QPushButton, "btn_style_sample")
        self.rbt_style_enabled: QRadioButton = self.findChild(QRadioButton, "rbt_style_enabled")
        self.rbt_style_disabled: QRadioButton = self.findChild(QRadioButton, "rbt_style_disabled")
        
        self.grp_style_gen: QGroupBox = self.findChild(QGroupBox, "grp_style_gen")
        self.btn_style_gen_fg: QPushButton = self.findChild(QPushButton, "btn_style_gen_fg")
        self.lbl_style_gen_fg: QLabel = self.findChild(QLabel, "lbl_style_gen_fg")
        self.btn_style_gen_bg: QPushButton = self.findChild(QPushButton, "btn_style_gen_bg")
        self.lbl_style_gen_bg: QLabel = self.findChild(QLabel, "lbl_style_gen_bg")
        self.lbl_style_gen_border_size: QLabel = self.findChild(QLabel, "lbl_style_gen_border_size")
        self.lbl_style_gen_border_radius: QLabel = self.findChild(QLabel, "lbl_style_gen_border_radius")
        self.spin_style_gen_border_size: QSpinBox = self.findChild(QSpinBox, "spin_style_gen_border_size")
        self.spin_style_gen_border_radius: QSpinBox = self.findChild(QSpinBox, "spin_style_gen_border_radius")
        self.btn_style_gen_border_color: QPushButton = self.findChild(QPushButton, "btn_style_gen_border_color")
        self.lbl_style_gen_border_color: QLabel = self.findChild(QLabel, "lbl_style_gen_border_color")
        self.btn_style_gen_font: QPushButton = self.findChild(QPushButton, "btn_style_gen_font")
        self.cmb_style_gen_font: QComboBox = self.findChild(QComboBox, "cmb_style_gen_font")
        self.spin_style_gen_font_size: QSpinBox = self.findChild(QSpinBox, "spin_style_gen_font_size")
        self.chk_style_gen_font_bold: QCheckBox = self.findChild(QCheckBox, "chk_style_gen_font_bold")
        self.chk_style_gen_font_italic: QCheckBox = self.findChild(QCheckBox, "chk_style_gen_font_italic")
        self.chk_style_gen_font_underline: QCheckBox = self.findChild(QCheckBox, "chk_style_gen_font_underline")
        self.chk_style_gen_font_strikeout: QCheckBox = self.findChild(QCheckBox, "chk_style_gen_font_strikeout")

        self.grp_style_hov: QGroupBox = self.findChild(QGroupBox, "grp_style_hov")
        self.btn_style_hov_fg: QPushButton = self.findChild(QPushButton, "btn_style_hov_fg")
        self.lbl_style_hov_fg: QLabel = self.findChild(QLabel, "lbl_style_hov_fg")
        self.btn_style_hov_bg: QPushButton = self.findChild(QPushButton, "btn_style_hov_bg")
        self.lbl_style_hov_bg: QLabel = self.findChild(QLabel, "lbl_style_hov_bg")
        self.btn_style_hov_border_color: QPushButton = self.findChild(QPushButton, "btn_style_hov_border_color")
        self.lbl_style_hov_border_color: QLabel = self.findChild(QLabel, "lbl_style_hov_border_color")
        self.lbl_style_hov_border_size: QLabel = self.findChild(QLabel, "lbl_style_hov_border_size")
        self.lbl_style_hov_border_radius: QLabel = self.findChild(QLabel, "lbl_style_hov_border_radius")
        self.spin_style_hov_border_size: QSpinBox = self.findChild(QSpinBox, "spin_style_hov_border_size")
        self.spin_style_hov_border_radius: QSpinBox = self.findChild(QSpinBox, "spin_style_hov_border_radius")

        self.grp_style_dis: QGroupBox = self.findChild(QGroupBox, "grp_style_dis")
        self.btn_style_dis_fg: QPushButton = self.findChild(QPushButton, "btn_style_dis_fg")
        self.lbl_style_dis_fg: QLabel = self.findChild(QLabel, "lbl_style_dis_fg")
        self.btn_style_dis_bg: QPushButton = self.findChild(QPushButton, "btn_style_dis_bg")
        self.lbl_style_dis_bg: QLabel = self.findChild(QLabel, "lbl_style_dis_bg")
        self.btn_style_dis_border_color: QPushButton = self.findChild(QPushButton, "btn_style_dis_border_color")
        self.lbl_style_dis_border_color: QLabel = self.findChild(QLabel, "lbl_style_dis_border_color")
        self.lbl_style_dis_border_size: QLabel = self.findChild(QLabel, "lbl_style_dis_border_size")
        self.lbl_style_dis_border_radius: QLabel = self.findChild(QLabel, "lbl_style_dis_border_radius")
        self.spin_style_dis_border_size: QSpinBox = self.findChild(QSpinBox, "spin_style_dis_border_size")
        self.spin_style_dis_border_radius: QSpinBox = self.findChild(QSpinBox, "spin_style_dis_border_radius")
        
        self.lbl_style_stylesheet: QLabel = self.findChild(QLabel, "lbl_style_stylesheet")
        self.txt_style_stylesheet: QTextEdit = self.findChild(QTextEdit, "txt_style_stylesheet")
        self.btn_style_apply: QPushButton = self.findChild(QPushButton, "btn_style_apply")
        self.btn_style_cancel: QPushButton = self.findChild(QPushButton, "btn_style_cancel")
        self.btn_style_copy: QPushButton = self.findChild(QPushButton, "btn_style_copy")
        self.btn_style_paste: QPushButton = self.findChild(QPushButton, "btn_style_paste")

        # Menu item: General Settings
        self.frm_menu_general: QFrame = self.findChild(QFrame, "frm_menu_general")
        self.lbl_menu_general_icon: QLabel = self.findChild(QLabel, "lbl_menu_general_icon")
        self.lbl_menu_general_title: QLabel = self.findChild(QLabel, "lbl_menu_general_title")

        # Menu item: StartUp
        self.frm_menu_startup: QFrame = self.findChild(QFrame, "frm_menu_startup")
        self.lbl_menu_startup_icon: QLabel = self.findChild(QLabel, "lbl_menu_startup_icon")
        self.lbl_menu_startup_title: QLabel = self.findChild(QLabel, "lbl_menu_startup_title")

        # Menu item: Widget
        self.frm_menu_widget: QFrame = self.findChild(QFrame, "frm_menu_widget")
        self.lbl_menu_widget_icon: QLabel = self.findChild(QLabel, "lbl_menu_widget_icon")
        self.lbl_menu_widget_title: QLabel = self.findChild(QLabel, "lbl_menu_widget_title")

        # Menu item: Windows
        self.frm_menu_window: QFrame = self.findChild(QFrame, "frm_menu_window")
        self.lbl_menu_window_icon: QLabel = self.findChild(QLabel, "lbl_menu_window_icon")
        self.lbl_menu_window_title: QLabel = self.findChild(QLabel, "lbl_menu_window_title")

        # Menu item: Search
        self.frm_menu_search: QFrame = self.findChild(QFrame, "frm_menu_search")
        self.lbl_menu_search_icon: QLabel = self.findChild(QLabel, "lbl_menu_search_icon")
        self.lbl_menu_search_title: QLabel = self.findChild(QLabel, "lbl_menu_search_title")
        self.txt_menu_search: QLineEdit = self.findChild(QLineEdit, "txt_menu_search")
        self.lbl_menu_search_info: QLabel = self.findChild(QLabel, "lbl_menu_search_info")
        self.chk_menu_search_whole_words: QCheckBox = self.findChild(QCheckBox, "chk_menu_search_whole_words")
        self.chk_menu_search_matchcase: QCheckBox = self.findChild(QCheckBox, "chk_menu_search_matchcase")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("app_settings_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("app_settings_lbl_title_tt"))

        self.btn_export.setText(self.getl("app_settings_btn_export_text"))
        self.btn_export.setToolTip(self.getl("app_settings_btn_export_tt"))

        self.btn_import.setText(self.getl("app_settings_btn_import_text"))
        self.btn_import.setToolTip(self.getl("app_settings_btn_import_tt"))

        self.btn_save.setText(self.getl("app_settings_btn_save_text"))
        self.btn_apply.setText(self.getl("app_settings_btn_apply_text"))
        self.btn_save.setToolTip(self.getl("app_settings_btn_save_tt"))

        self.btn_cancel.setText(self.getl("btn_cancel"))

        # Working frame
        self.lbl_working_title.setText(self.getl("please_wait"))

        # Import options
        self.lbl_import_title.setText(self.getl("app_settings_lbl_import_title_text"))
        self.rbt_import_custom.setText(self.getl("app_settings_rbt_import_custom_text"))
        self.rbt_import_all.setText(self.getl("app_settings_rbt_import_all_text"))
        self.grp_import_custom.setTitle(self.getl("app_settings_grp_import_custom_text"))
        self.grp_import_all.setTitle(self.getl("app_settings_grp_import_all_text"))
        self.chk_import_all_style.setText(self.getl("app_settings_chk_import_all_style_text"))
        self.chk_import_button_style.setText(self.getl("app_settings_chk_import_button_style_text"))
        self.chk_import_font.setText(self.getl("app_settings_chk_import_font_text"))
        self.chk_import_icon.setText(self.getl("app_settings_chk_import_icon_text"))
        self.chk_import_sound.setText(self.getl("app_settings_chk_import_sound_text"))
        self.lbl_import_all_desc.setText(self.getl("app_settings_lbl_import_all_desc_text"))
        self.btn_import_from_file.setText(self.getl("app_settings_btn_import_from_file_text"))


        # Style Frame
        self.lbl_style_title.setText(self.getl("app_settings_lbl_style_title_text"))
        self.lbl_style_sample.setText(self.getl("app_settings_lbl_style_sample_text"))
        self.btn_style_sample.setText(self.getl("app_settings_btn_style_sample_text"))
        self.rbt_style_enabled.setText(self.getl("app_settings_rbt_style_enabled_text"))
        self.rbt_style_disabled.setText(self.getl("app_settings_rbt_style_disabled_text"))

        self.grp_style_gen.setTitle(self.getl("app_settings_grp_style_gen_title"))
        self.btn_style_gen_fg.setText(self.getl("app_settings_btn_style_gen_fg_text"))
        self.btn_style_gen_bg.setText(self.getl("app_settings_btn_style_gen_bg_text"))
        self.lbl_style_gen_border_size.setText(self.getl("app_settings_lbl_style_gen_border_size_text"))
        self.lbl_style_gen_border_radius.setText(self.getl("app_settings_lbl_style_gen_border_radius_text"))
        self.btn_style_gen_border_color.setText(self.getl("app_settings_btn_style_gen_border_color_text"))
        self.btn_style_gen_font.setText(self.getl("app_settings_btn_style_gen_font_text"))
        self.chk_style_gen_font_bold.setText(self.getl("app_settings_chk_style_gen_font_bold_text"))
        self.chk_style_gen_font_italic.setText(self.getl("app_settings_chk_style_gen_font_italic_text"))
        self.chk_style_gen_font_underline.setText(self.getl("app_settings_chk_style_gen_font_underline_text"))
        self.chk_style_gen_font_strikeout.setText(self.getl("app_settings_chk_style_gen_font_strikeout_text"))
        
        self.grp_style_hov.setTitle(self.getl("app_settings_grp_style_hov_title"))
        self.btn_style_hov_fg.setText(self.getl("app_settings_btn_style_gen_fg_text"))
        self.btn_style_hov_bg.setText(self.getl("app_settings_btn_style_gen_bg_text"))
        self.lbl_style_hov_border_size.setText(self.getl("app_settings_lbl_style_gen_border_size_text"))
        self.lbl_style_hov_border_radius.setText(self.getl("app_settings_lbl_style_gen_border_radius_text"))
        self.btn_style_hov_border_color.setText(self.getl("app_settings_btn_style_gen_border_color_text"))

        self.grp_style_dis.setTitle(self.getl("app_settings_grp_style_dis_title"))
        self.btn_style_dis_fg.setText(self.getl("app_settings_btn_style_gen_fg_text"))
        self.btn_style_dis_bg.setText(self.getl("app_settings_btn_style_gen_bg_text"))
        self.lbl_style_dis_border_size.setText(self.getl("app_settings_lbl_style_gen_border_size_text"))
        self.lbl_style_dis_border_radius.setText(self.getl("app_settings_lbl_style_gen_border_radius_text"))
        self.btn_style_dis_border_color.setText(self.getl("app_settings_btn_style_gen_border_color_text"))
        
        self.lbl_style_stylesheet.setText(self.getl("app_settings_lbl_style_stylesheet_text"))
        self.btn_style_apply.setText(self.getl("app_settings_btn_style_apply_text"))
        self.btn_style_cancel.setText(self.getl("app_settings_btn_style_cancel_text"))
        self.btn_style_copy.setText(self.getl("app_settings_btn_style_copy_text"))
        self.btn_style_copy.setToolTip(self.getl("app_settings_btn_style_copy_tt"))
        self.btn_style_paste.setText(self.getl("app_settings_btn_style_paste_text"))
        self.btn_style_paste.setToolTip(self.getl("app_settings_btn_style_paste_tt"))

        # Menu item: General Settings
        item = "lbl_menu_general_title"
        title = self.getl(f"app_settings_{item}_text")
        tt = self.getl(f"app_settings_{item}_tt")
        self.lbl_menu_general_title.setText(title)
        self.lbl_menu_general_title.setToolTip(tt)
        self.frm_menu_general.setToolTip(tt)
        self.lbl_menu_general_icon.setToolTip(tt)
        # Menu item: StartUp
        item = "lbl_menu_startup_title"
        title = self.getl(f"app_settings_{item}_text")
        tt = self.getl(f"app_settings_{item}_tt")
        self.lbl_menu_startup_title.setText(title)
        self.lbl_menu_startup_title.setToolTip(tt)
        self.frm_menu_startup.setToolTip(tt)
        self.lbl_menu_startup_icon.setToolTip(tt)
        # Menu item: Widget
        item = "lbl_menu_widget_title"
        title = self.getl(f"app_settings_{item}_text")
        tt = self.getl(f"app_settings_{item}_tt")
        self.lbl_menu_widget_title.setText(title)
        self.lbl_menu_widget_title.setToolTip(tt)
        self.frm_menu_widget.setToolTip(tt)
        self.lbl_menu_widget_icon.setToolTip(tt)
        # Menu item: Window
        item = "lbl_menu_window_title"
        title = self.getl(f"app_settings_{item}_text")
        tt = self.getl(f"app_settings_{item}_tt")
        self.lbl_menu_window_title.setText(title)
        self.lbl_menu_window_title.setToolTip(tt)
        self.frm_menu_window.setToolTip(tt)
        self.lbl_menu_window_icon.setToolTip(tt)
        # Menu item: Search
        item = "lbl_menu_search_title"
        title = self.getl(f"app_settings_{item}_text")
        tt = self.getl(f"app_settings_{item}_tt")
        self.lbl_menu_search_title.setText(title)
        self.lbl_menu_search_title.setToolTip(tt)
        self.lbl_menu_search_icon.setToolTip(tt)
        self.lbl_menu_search_info.setText("")
        self.chk_menu_search_whole_words.setText(self.getl("app_settings_chk_menu_search_whole_words_text"))
        self.chk_menu_search_matchcase.setText(self.getl("app_settings_chk_menu_search_matchcase_text"))

    def app_setting_updated(self, data: dict):
        self.widget_handler.close_me()
        self.load_widgets_handler()
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        if not settings_updated:
            self.btn_save.setDisabled(True)
            self.btn_apply.setDisabled(True)

            self.frm_style.setVisible(False)
            self.btn_style_sample.setVisible(False)
            self.btn_style_paste.setEnabled(False)

            self.frm_adv.setVisible(False)
            self.frm_adv_progress.setVisible(False)
            self.btn_adv_show.setVisible(False)

            self.lst_changes.verticalScrollBar().setSingleStep(10)

            if self.getv("anim_settings_wheels_animation_path") and os.path.isfile(self.getv("anim_settings_wheels_animation_path")):
                movie_lbl_adv_animated_gif = QMovie(self.getv("anim_settings_wheels_animation_path"))
                movie_lbl_adv_animated_gif.setScaledSize(self.lbl_adv_animated_gif.size())
                self.lbl_adv_animated_gif.setMovie(movie_lbl_adv_animated_gif)
                movie_lbl_adv_animated_gif.start()

            # Populate self.cmb_style_gen_font with fonts
            self.cmb_style_gen_font.clear()
            font_list = QtGui.QFontDatabase().families()
            self.cmb_style_gen_font.addItems(font_list)

            self.frm_import.setVisible(False)
            
            self.frm_working.move(0, 0)
            self.frm_working.resize(self.width(), self.height())
            x = int(self.frm_working.width() / 2 - self.frm_working_info.width() / 2)
            if x < 0:
                x = 0
            y = int(self.frm_working.height() / 2 - self.frm_working_info.height() / 2)
            if y < 0:
                y = 0
            self.frm_working_info.move(x, y)
            self.frm_working.setVisible(False)
            self.grp_import_custom.setDisabled(True)

            self.frm_loading.setVisible(False)
            loading_movie = QMovie(self.getv("loading_animation_path"))
            self.lbl_loading.setScaledContents(True)
            self.lbl_loading.setMovie(loading_movie)


        # Working frame
        self.frm_working.setStyleSheet(self.getv("app_settings_frm_working_stylesheet"))
        self.frm_working_info.setStyleSheet(self.getv("app_settings_frm_working_info_stylesheet"))
        self._define_labels_apperance(self.lbl_working_title, "app_settings_lbl_working_title")
        self.prg_working.setStyleSheet(self.getv("app_settings_prg_working_stylesheet"))

        # Import options
        self.frm_import.setStyleSheet(self.getv("app_settings_frm_import_stylesheet"))
        self._define_labels_apperance(self.lbl_import_title, "app_settings_lbl_import_title")
        self.lbl_import_close.setStyleSheet(self.getv("app_settings_lbl_import_close_stylesheet"))
        self.rbt_import_custom.setStyleSheet(self.getv("app_settings_rbt_import_radio_buttons_stylesheet"))
        self.rbt_import_all.setStyleSheet(self.getv("app_settings_rbt_import_radio_buttons_stylesheet"))
        self.grp_import_custom.setStyleSheet(self.getv("app_settings_grp_import_groupboxes_stylesheet"))
        self.grp_import_all.setStyleSheet(self.getv("app_settings_grp_import_groupboxes_stylesheet"))
        self.chk_import_all_style.setStyleSheet(self.getv("app_settings_chk_import_checkboxes_stylesheet"))
        self.chk_import_button_style.setStyleSheet(self.getv("app_settings_chk_import_checkboxes_stylesheet"))
        self.chk_import_font.setStyleSheet(self.getv("app_settings_chk_import_checkboxes_stylesheet"))
        self.chk_import_icon.setStyleSheet(self.getv("app_settings_chk_import_checkboxes_stylesheet"))
        self.chk_import_sound.setStyleSheet(self.getv("app_settings_chk_import_checkboxes_stylesheet"))
        self._define_labels_apperance(self.lbl_import_all_desc, "app_settings_lbl_import_desc")
        self._define_buttons_apperance(self.btn_import_from_file, "app_settings_btn_import_from_file")

        # Stylesheet settings for widgets
        self._define_user_settings_win_apperance()

        self._define_buttons_apperance(self.btn_save, "app_settings_btn_save_text")
        self._define_buttons_apperance(self.btn_apply, "app_settings_btn_apply_text")
        self._define_buttons_apperance(self.btn_cancel, "app_settings_btn_cancel_text")
        self._define_buttons_apperance(self.btn_export, "app_settings_btn_export")
        self._define_buttons_apperance(self.btn_import, "app_settings_btn_import")

        self._define_labels_apperance(self.lbl_title, "app_settings_lbl_title")
        self._define_labels_apperance(self.lbl_counter, "app_settings_lbl_counter")
        self.lst_changes.setStyleSheet(self.getv("app_settings_lst_changes_stylesheet"))

        # Menu item: General Settings
        self.frm_menu_general.setStyleSheet(self.getv("app_settings_frm_menu_item_stylesheet"))
        self.frm_menu_general.setCursor(Qt.PointingHandCursor)
        self._define_labels_apperance(self.lbl_menu_general_title, "app_settings_lbl_menu_item")
        self._define_labels_apperance(self.lbl_menu_general_icon, "app_settings_lbl_menu_item")
        # Menu item: StartUp
        self.frm_menu_startup.setStyleSheet(self.getv("app_settings_frm_menu_item_stylesheet"))
        self.frm_menu_startup.setCursor(Qt.PointingHandCursor)
        self._define_labels_apperance(self.lbl_menu_startup_title, "app_settings_lbl_menu_item")
        self._define_labels_apperance(self.lbl_menu_startup_icon, "app_settings_lbl_menu_item")
        # Menu item: Widget
        self.frm_menu_widget.setStyleSheet(self.getv("app_settings_frm_menu_item_stylesheet"))
        self.frm_menu_widget.setCursor(Qt.PointingHandCursor)
        self._define_labels_apperance(self.lbl_menu_widget_title, "app_settings_lbl_menu_item")
        self._define_labels_apperance(self.lbl_menu_widget_icon, "app_settings_lbl_menu_item")
        # Menu item: Window
        self.frm_menu_window.setStyleSheet(self.getv("app_settings_frm_menu_item_stylesheet"))
        self.frm_menu_window.setCursor(Qt.PointingHandCursor)
        self._define_labels_apperance(self.lbl_menu_window_title, "app_settings_lbl_menu_item")
        self._define_labels_apperance(self.lbl_menu_window_icon, "app_settings_lbl_menu_item")
        # Menu item: Search
        self.frm_menu_search.setStyleSheet(self.getv("app_settings_frm_menu_item_stylesheet"))
        self.frm_menu_search.setCursor(Qt.PointingHandCursor)
        self._define_labels_apperance(self.lbl_menu_window_title, "app_settings_lbl_menu_item")
        self._define_labels_apperance(self.lbl_menu_window_icon, "app_settings_lbl_menu_item")

    def _define_user_settings_win_apperance(self):
        self.setStyleSheet(self.getv("app_settings_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("app_settings_win_icon_path")))
        self.setWindowTitle(self.getl("app_settings_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(1120, 745)

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
            btn.setIcon(QIcon(QPixmap(self.getv(f"{name}_icon_path"))))
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))


