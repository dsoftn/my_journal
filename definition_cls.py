from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QGridLayout, QWidget, QListWidget, 
                             QDialog, QLabel, QListWidgetItem, QLineEdit, QHBoxLayout, QCheckBox, QAction,
                             QProgressBar , QComboBox, QMessageBox)
from PyQt5.QtGui import (QIcon, QFont, QPixmap, QCursor, QTextCharFormat, QColor, QImage, QClipboard,
                         QDrag, QMouseEvent, QTextCursor)
from PyQt5.QtCore import (QSize, Qt, QCoreApplication, QPoint, QMimeData)
from PyQt5 import uic, QtGui, QtCore

import time
import wikipedia
from googletrans import Translator
import googletrans
import asyncio
import aiohttp
import webbrowser
import os

import settings_cls
import utility_cls
import db_definition_cls
import db_media_cls
import text_handler_cls
import definition_data_find_cls
import text_filter_cls
import qwidgets_util_cls
import UTILS
from obj_definition import Definition


class SynonymManager(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, shema_name: str = None, suggested_words: list = None):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self.my_name = None
        self._parent_widget = parent_widget
        self.shemas = self.get_shemas()
        self._working = False
        
        if self._parent_widget is None:
            # Register dialog
            self.my_name = str(time.time_ns())
            self.get_appv("cm").dialog_method_add_dialog(self, self._my_name)

        # Load GUI
        uic.loadUi(self.getv("synonyms_manager_ui_file_path"), self)

        self._define_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()
        self._load_data(shema_name, suggested_words=suggested_words)
        self._load_win_position()
        self.load_widgets_handler()

        self.old_base_text = self.cmb_apply.currentText()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.lst_shema.currentItemChanged.connect(self.lst_shema_current_item_changed)
        self.txt_suff.textChanged.connect(self.txt_suff_text_changed)
        self.txt_name.textChanged.connect(self.txt_name_text_changed)
        self.btn_update.clicked.connect(self.btn_update_click)
        self.btn_add.clicked.connect(self.btn_add_click)
        self.btn_delete.clicked.connect(self.btn_delete_click)
        self.btn_copy.clicked.connect(self.btn_copy_click)
        self.btn_zoom_in.clicked.connect(self.btn_zoom_in_click)
        self.btn_zoom_out.clicked.connect(self.btn_zoom_out_click)
        self.btn_apply_refresh.clicked.connect(self.btn_apply_refresh_click)
        self.txt_find.textChanged.connect(self.txt_find_text_changed)
        self.cmb_apply.editTextChanged.connect(self.cmb_apply_edit_text_changed)
        self.btn_close.clicked.connect(self.btn_close_click)

        UTILS.LogHandler.add_log_record("#1: Dialog started.(Loaded #2 schemas)", ["SynonymManager", len(self.shemas)])
        self.show()

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title, self.lbl_shema_name])

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_find, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_name, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_suff, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_additional, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_Selection_Widget(self.cmb_apply)

        # Add Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_shema)

        self.widget_handler.activate()

    def btn_close_click(self):
        self.close()

    def btn_apply_refresh_click(self):
        txt = self.cmb_apply.currentText()
        self.cmb_apply.setCurrentText("")
        self.cmb_apply.setCurrentText(txt)

    def cmb_apply_edit_text_changed(self):
        if self._working:
            return
        
        if not self.txt_suff.toPlainText():
            return

        if self.txt_suff.toPlainText()[-1] == "\n":
            self.txt_suff.setText(self.txt_suff.toPlainText()[:-1])

        text = self.cmb_apply.currentText()
        new_text_list = []

        for i in self.txt_suff.toPlainText().split("\n"):
            if i == "":
                new_text_list.append(["", ""])
                continue
            
            if len(i) > len(self.old_base_text):
                if i[:len(self.old_base_text)] == self.old_base_text:
                    new_text_list.append([text, i[len(self.old_base_text):]])
                else:
                    new_text_list.append(["", i])
            else:
                new_text_list.append(["", i])
        
        self.old_base_text = text
        cur = self.txt_suff.textCursor()
        color_pref = QColor()
        color_pref.setNamedColor("#ffff00")
        color_suff = QColor()
        color_suff.setNamedColor("#ffff7f")
        self._working = True
        self.txt_suff.setText("")
        cf = QTextCharFormat()
        for i in new_text_list:
            cf.setForeground(color_pref)
            cur.setCharFormat(cf)
            cur.insertText(i[0])

            cf.setForeground(color_suff)
            cur.setCharFormat(cf)
            cur.insertText(i[1] + "\n")
        
        self.txt_suff.setTextCursor(cur)
        self._working = False

    def txt_find_text_changed(self):
        item = None
        if self.lst_shema.currentItem() is not None:
            item = self.lst_shema.currentItem().text()
        self._load_data(selected_shema=item)

    def btn_zoom_in_click(self):
        font = self.txt_suff.font()
        size = font.pointSize()
        if size < 30:
            size += 2
            font.setPointSize(size)
            self.txt_suff.setFont(font)

    def btn_zoom_out_click(self):
        font = self.txt_suff.font()
        size = font.pointSize()
        if size > 6:
            size -= 2
            font.setPointSize(size)
        self.txt_suff.setFont(font)

    def btn_copy_click(self):
        self.get_appv("clipboard").setText(self.txt_suff.toPlainText())
        UTILS.LogHandler.add_log_record("#1: Data copied to clipboard.", ["SynonymManager"], variables=[["Copied Data", self.txt_suff.toPlainText()]])
        self.btn_copy.setEnabled(False)

    def btn_update_click(self):
        item = self.txt_name.text()
        if item in self.shemas:
            self.shemas[item]["suffs"] = [x.strip() for x in self.txt_suff.toPlainText().split("\n") if x.strip() != ""]
        
        self._update_counter_and_buttons()

    def btn_add_click(self):
        UTILS.LogHandler.add_log_record("#1: About to add new schema.", ["SynonymManager"])
        if len(self.shemas) >= 50:
            UTILS.LogHandler.add_log_record("#1: Maximum items reached, adding canceled.", ["SynonymManager"])
            self._msg_maximum_shemas()
            return
        
        name = self.txt_name.text()
        suffs = [x.strip() for x in self.txt_suff.toPlainText().split("\n") if x.strip() != ""]
        
        if name in self.shemas:
            return
        
        self.shemas[name] = {"suffs": suffs}
        self._update_counter_and_buttons()
        UTILS.LogHandler.add_log_record("#1: New schema added.", ["SynonymManager"])
        self._load_data(selected_shema=name)

    def _msg_maximum_shemas(self):
        msg_data = {
            "title": self.getl("synonyms_manager_msg_max_shemas_title"),
            "text": self.getl("synonyms_manager_msg_max_shemas_text"),
            "icon_path": self.getv("synonyms_icon_path")
        }
        utility_cls.MessageInformation(self._stt, self, msg_data)

    def btn_delete_click(self):
        name = self.txt_name.text()
        if name in self.shemas:
            del self.shemas[name]
            UTILS.LogHandler.add_log_record("#1: Schema deleted.", ["SynonymManager"])
        
        self._load_data()

    def txt_suff_text_changed(self):
        self._update_counter_and_buttons()

    def txt_name_text_changed(self):
        self._update_counter_and_buttons()

    def lst_shema_current_item_changed(self, x = None, y = None):
        if self.lst_shema.currentItem() is None:
            return
        shema_name = self.lst_shema.currentItem().text()

        self._load_item(shema_name)

    def _load_item(self, item_name: str):
        if self.lst_shema.currentItem() is None:
            return
        
        shema = self.lst_shema.currentItem().text()

        self.lbl_shema_name.setText(shema)
        self.txt_name.setText(shema)
        
        suff_text = "\n".join(self.shemas[shema]["suffs"])
        self.txt_suff.setText(suff_text)
        self._update_counter_and_buttons()

    def _update_counter_and_buttons(self):
        self.lbl_count.setText(self.getl("synonyms_manager_lbl_count_text").replace("#1", str(self.lst_shema.currentRow() + 1)).replace("#2", str(self.lst_shema.count())))
        if self.lst_shema.currentItem() is None:
            shema = None
        else:
            shema = self.lst_shema.currentItem().text()
        
        if shema is not None:
            shema_suffs = "\n".join(self.shemas[shema]["suffs"])
        else:
            shema_suffs = ""
        
        # Buttton Update
        if shema == self.txt_name.text() and shema_suffs != self.txt_suff.toPlainText():
            self.btn_update.setEnabled(True)
        else:
            self.btn_update.setEnabled(False)
        # Button Add
        if self.txt_name.text() not in self.shemas and self.txt_name.text():
            self.btn_add.setEnabled(True)
        else:
            self.btn_add.setEnabled(False)
        # Button Delete
        if shema == self.txt_name.text():
            self.btn_delete.setEnabled(True)
        else:
            self.btn_delete.setEnabled(False)
        # Button Copy
        if self.txt_suff.toPlainText():
            self.btn_copy.setEnabled(True)
        else:
            self.btn_copy.setEnabled(False)

    def _load_data(self, selected_shema: str = None, suggested_words: list = None):
        replace_char = "(),[];:.<>/?'\"\n\t{}=+_-*&^%$#@!"
        if suggested_words:
            if isinstance(suggested_words, str):
                suggested_words = [suggested_words]
            for i in range(len(suggested_words)):
                txt = suggested_words[i]
                for j in replace_char:
                    txt = txt.replace(j, " ")
                sugg_list = [x for x in txt.split(" ") if x != ""]
                for j in sugg_list:
                    if j not in suggested_words:
                        suggested_words.append(j)
            for i in suggested_words:
                self.cmb_apply.addItem(i)
            self.cmb_apply.setEditText("")
    
        self.lst_shema.clear()

        row = None
        count = 0
        for item in self.shemas:
            if item == selected_shema:
                row = count
            lst_item = QListWidgetItem()
            lst_item.setText(item)
            if item.lower().find(self.txt_find.text().lower()) >= 0 and self.txt_find.text():
                color = QColor()
                color.setNamedColor("#316293")
                lst_item.setBackground(color)
            self.lst_shema.addItem(lst_item)
            count += 1
        self._update_counter_and_buttons()
        
        if row is not None:
            self.lst_shema.setCurrentRow(row)
        elif self.lst_shema.count():
            self.lst_shema.setCurrentRow(0)
        self.lst_shema_current_item_changed()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()        
        return super().closeEvent(a0)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        h = self.contentsRect().height()
        w = self.contentsRect().width()

        self.lbl_title.resize(w, self.lbl_title.height())
        self.lbl_shema_name.resize(w - 280, self.lbl_shema_name.height())
        self.txt_name.resize(w - 290, self.txt_name.height())
        self.cmb_apply.resize(w - 430, self.cmb_apply.height())

        self.lst_shema.resize(self.lst_shema.width(), h - 210)
        self.lbl_count.move(10, self.lst_shema.height() + 135)
        self.line.move(10, h - 55)
        self.line.resize(w - 20, self.line.height())
        self.btn_close.move(w - 110, h -35)

        self.txt_suff.resize(w - 620, h - 320)
        self.btn_zoom_in.move(w - 265, h - 75)
        self.btn_zoom_out.move(w - 230, h - 75)

        self.lbl_additional.move(w - 190, 250)
        self.txt_additional.move(w - 190, 280)
        self.txt_additional.resize(self.txt_additional.width(), h -360)
        self.btn_additional.move(w - 160, h - 80)

        return super().resizeEvent(a0)

    def _load_win_position(self):
        if "synonym_manager_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("synonym_manager_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            
            font = self.txt_suff.font()
            font.setPointSize(g.setdefault("font_size", 10))
            self.txt_suff.setFont(font)

    def close_me(self):
        if "synonym_manager_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("synonym_manager_win_geometry", {}, save_to_file=True)

        g = self.get_appv("synonym_manager_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["font_size"] = self.txt_suff.font().pointSize()

        # Unregister Dialog
        self.get_appv("cm").remove_all_context_menu()
        
        if self._parent_widget is None:
            self.get_appv("cm").dialog_method_remove_dialog(self.my_name)

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["SynonymManager"])
        UTILS.DialogUtility.on_closeEvent(self)

    def get_shemas(self) -> dict:
        if "def_syn_shemas" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("def_syn_shemas", {}, save_to_file=True)
        
        return self.get_appv("def_syn_shemas")

    def _define_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_shema_name: QLabel = self.findChild(QLabel, "lbl_shema_name")
        self.lbl_suff: QLabel = self.findChild(QLabel, "lbl_suff")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.txt_find: QLineEdit = self.findChild(QLineEdit, "txt_find")
        self.txt_name: QLineEdit = self.findChild(QLineEdit, "txt_name")
        self.cmb_apply: QComboBox = self.findChild(QComboBox, "cmb_apply")
        self.txt_suff: QTextEdit = self.findChild(QTextEdit, "txt_suff")
        self.lst_shema: QListWidget = self.findChild(QListWidget, "lst_shema")
        self.btn_update: QPushButton = self.findChild(QPushButton, "btn_update")
        self.btn_add: QPushButton = self.findChild(QPushButton, "btn_add")
        self.btn_copy: QPushButton = self.findChild(QPushButton, "btn_copy")
        self.btn_delete: QPushButton = self.findChild(QPushButton, "btn_delete")
        self.btn_zoom_in: QPushButton = self.findChild(QPushButton, "btn_zoom_in")
        self.btn_zoom_out: QPushButton = self.findChild(QPushButton, "btn_zoom_out")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_apply_refresh: QPushButton = self.findChild(QPushButton, "btn_apply_refresh")
        self.line: QFrame = self.findChild(QFrame, "line")
        self.lbl_additional: QLabel = self.findChild(QLabel, "lbl_additional")
        self.txt_additional: QTextEdit = self.findChild(QTextEdit, "txt_additional")
        self.btn_additional: QPushButton = self.findChild(QPushButton, "btn_additional")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("synonyms_manager_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("synonyms_manager_lbl_title_tt"))

        self.lbl_shema_name.setText("")
        self.lbl_shema_name.setToolTip(self.getl("synonyms_manager_lbl_shema_name_tt"))

        self.lbl_suff.setText(self.getl("synonyms_manager_lbl_suff_text"))
        self.lbl_suff.setToolTip(self.getl("synonyms_manager_lbl_suff_tt"))

        self.lbl_count.setText(self.getl("synonyms_manager_lbl_count_text"))
        self.lbl_count.setToolTip(self.getl("synonyms_manager_lbl_count_tt"))

        self.btn_update.setText(self.getl("synonyms_manager_btn_update_text"))
        self.btn_update.setToolTip(self.getl("synonyms_manager_btn_update_tt"))

        self.btn_add.setText(self.getl("synonyms_manager_btn_add_text"))
        self.btn_add.setToolTip(self.getl("synonyms_manager_btn_add_tt"))

        self.btn_copy.setText(self.getl("synonyms_manager_btn_copy_text"))
        self.btn_copy.setToolTip(self.getl("synonyms_manager_btn_copy_tt"))

        self.btn_delete.setText(self.getl("synonyms_manager_btn_delete_text"))
        self.btn_delete.setToolTip(self.getl("synonyms_manager_btn_delete_tt"))

        self.btn_close.setText(self.getl("synonyms_manager_btn_close_text"))
        self.btn_close.setToolTip(self.getl("synonyms_manager_btn_close_tt"))

        self.btn_zoom_in.setToolTip(self.getl("synonyms_manager_btn_zoom_in_tt"))

        self.btn_zoom_out.setToolTip(self.getl("synonyms_manager_btn_zoom_out_tt"))

        self.lbl_additional.setText(self.getl("synonyms_manager_lbl_additional_text").replace("#1", ""))
        self.lbl_additional.setToolTip(self.getl("synonyms_manager_lbl_additional_tt"))

        self.btn_additional.setText(self.getl("synonyms_manager_btn_additional_text"))
        self.btn_additional.setToolTip(self.getl("synonyms_manager_btn_additional_tt"))

    def app_setting_updated(self, data: dict):
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self.setStyleSheet(self.getv("synonyms_manager_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("synonyms_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumWidth(800)
        self.setMinimumHeight(530)

        self._define_labels_apperance(self.lbl_title, "synonyms_manager_lbl_title")
        self._define_labels_apperance(self.lbl_shema_name, "synonyms_manager_lbl_shema_name")
        self._define_labels_apperance(self.lbl_suff, "synonyms_manager_lbl_suff")
        self._define_labels_apperance(self.lbl_count, "synonyms_manager_lbl_count")
        self._define_labels_apperance(self.lbl_additional, "synonyms_manager_lbl_additional")

        self.lst_shema.setStyleSheet(self.getv("synonyms_manager_lst_shema_stylesheet"))
        self.txt_find.setStyleSheet(self.getv("synonyms_manager_txt_find_stylesheet"))
        self.cmb_apply.setStyleSheet(self.getv("synonyms_manager_txt_apply_stylesheet"))
        self.txt_name.setStyleSheet(self.getv("synonyms_manager_txt_name_stylesheet"))
        self.txt_suff.setStyleSheet(self.getv("synonyms_manager_txt_suff_stylesheet"))
        self.txt_additional.setStyleSheet(self.getv("synonyms_manager_txt_additional_stylesheet"))

        self.btn_update.setStyleSheet(self.getv("synonyms_manager_btn_update_stylesheet"))
        self.btn_add.setStyleSheet(self.getv("synonyms_manager_btn_add_stylesheet"))
        self.btn_copy.setStyleSheet(self.getv("synonyms_manager_btn_copy_stylesheet"))
        self.btn_delete.setStyleSheet(self.getv("synonyms_manager_btn_delete_stylesheet"))
        self.btn_close.setStyleSheet(self.getv("synonyms_manager_btn_close_stylesheet"))
        self.btn_additional.setStyleSheet(self.getv("synonyms_manager_btn_additional_stylesheet"))

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))


class SynonymHint():
    def __init__(self, settings: settings_cls.Settings, parent_widget, text_box: QTextEdit = None, base_string: str = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_widget = parent_widget
        self.txt_box = text_box
        self._base_string = base_string
        self.text_func = text_handler_cls.TextFunctions(self._stt, text_box=text_box)
        self.shemas: dict = self.get_shemas()
        self.clipboard: QClipboard = self.get_appv("clipboard")

    def show_contex_menu(self, menu_position: QPoint = None, show_raport: bool = True, text_box: QTextEdit = None, base_string: str = None):
        if base_string:
            self._base_string = base_string

        if menu_position is None:
            menu_position = QCursor.pos()

        if text_box is None:
            text_box = self.txt_box

        if text_box is None:
            return None

        result = self._show_contex_menu(text_box, menu_position, show_raport)
        
        if result:
            if result["text"]:
                return result
            
        return None
    
    def _add_copy_paste_manager_items(self, menu_items: list, paste_menu_text: str = None, paste_menu_tt: str = None) -> None:
        name = self.getl("syn_hint_menu_copy_text")
        tt = self.getl("syn_hint_menu_copy_tt")
        icon = self.getv("copy_icon_path")
        menu_item = self._create_menu_item(10010, name, tt, icon=icon)
        menu_items.append(menu_item)

        if paste_menu_text is None:
            name = self.getl("syn_hint_menu_paste_text")
        else:
            name = paste_menu_text
        if paste_menu_tt is None:
            tt = self.getl("syn_hint_menu_paste_tt")
        else:
            tt = paste_menu_tt
        icon = self.getv("paste_icon_path")
        menu_item = self._create_menu_item(10020, name, tt, icon=icon)
        menu_items.append(menu_item)

        name = self.getl("syn_hint_menu_start_manager_text")
        tt = self.getl("syn_hint_menu_start_manager_tt")
        icon = self.getv("synonyms_icon_path")
        menu_item = self._create_menu_item(10100, name, tt, icon=icon)
        menu_items.append(menu_item)

    def _add_replace_serbian_chars_items(self, menu_items: list) -> None:
        name = self.getl("syn_hint_menu_add_serbian_text")
        tt = self.getl("syn_hint_menu_add_serbian_tt")
        icon = self.getv("replace_icon_path")
        menu_item = self._create_menu_item(10050, name, tt, icon=icon)
        menu_items.append(menu_item)

        name = self.getl("syn_hint_menu_copy_serbian_text")
        tt = self.getl("syn_hint_menu_copy_serbian_tt")
        icon = self.getv("copy_icon_path")
        menu_item = self._create_menu_item(10060, name, tt, icon=icon)
        menu_items.append(menu_item)

        name = self.getl("syn_hint_menu_replace_serbian_text")
        tt = self.getl("syn_hint_menu_replace_serbian_tt")
        icon = self.getv("edit_icon_path")
        menu_item = self._create_menu_item(10070, name, tt, icon=icon)
        menu_items.append(menu_item)

    def _show_contex_menu(self, text_box: QTextEdit, menu_position: QPoint, show_raport: bool):
        disab = []
        separator = []
        menu_item_width = 400
        font = QFont(self.getv("context_menu_button_font_name"), self.getv("context_menu_button_font_size"))
        font.setWeight(self.getv("context_menu_button_font_weight"))
        font.setItalic(self.getv("context_menu_button_font_italic"))
        font.setUnderline(self.getv("context_menu_button_font_underline"))
        font.setStrikeOut(self.getv("context_menu_button_font_strikeout"))

        items = self.text_func.select_whole_lines_from_text_box(text_box)
        
        base_items_list = self.text_func.get_all_common_denominators(items, match_case=True)

        if base_items_list:
            while len(base_items_list) > 50:
                base_items_list.pop(len(base_items_list) - 1)
        else:
            base_items_list = []

        if self.shemas and base_items_list:
            separator.append(len(base_items_list) - 1)
        
        menu_items = []

        # Add copy and paste items
        paste_menu_text = self.getl("syn_hint_menu_paste_text")
        paste_menu_tt = self.getl("syn_hint_menu_paste_tt")
        syns_to_add_list = []
        if not self.clipboard.text():
            disab.append(10020)
        else:
            clip_items = [x.lower().strip() for x in self.clipboard.text().split("\n") if x.strip()]
            syn_txt_box_items = [x.lower() for x in self.txt_box.toPlainText().split("\n") if x]
            for item in clip_items:
                if item not in syn_txt_box_items and item not in syns_to_add_list:
                    syns_to_add_list.append(item)

            if syns_to_add_list:
                paste_menu_text += f" ({len(syns_to_add_list)})"
                paste_menu_tt += "\n" + "\n".join(syns_to_add_list)
                self.clipboard.setText("\n".join(syns_to_add_list))
            else:
                disab.append(10020)
                paste_menu_text = self.getl("syn_hint_menu_paste_already_present_text")
        
        self._add_copy_paste_manager_items(menu_items, paste_menu_text=paste_menu_text, paste_menu_tt=paste_menu_tt)

        cur = self.txt_box.textCursor()
        if cur.hasSelection():
            txt_box_selection = cur.selection().toPlainText()
        else:
            txt_box_selection = None
            disab.append(10010)
        separator.append(10020)
        separator.append(10100)

        # Add replace serbian chars items
        self._add_replace_serbian_chars_items(menu_items)
        if not UTILS.TextUtility.has_serbian_chars(self.txt_box.toPlainText()):
            disab.append(10050)
            disab.append(10060)
            disab.append(10070)
        else:
            if 10050 not in disab and not UTILS.TextUtility.get_text_lines_without_serbian_chars(self.txt_box.toPlainText(), if_data_exist_add_string_at_end="\n", ignore_if_line_already_exist=True).strip():
                disab.append(10050)
        separator.append(10070)

        html = utility_cls.TextToHTML()
        html.general_rule.font_size = 20
        html.general_rule.fg_color = "#d0d0d0"
        html.general_rule.white_space_wrap = False
        html_rule_base = utility_cls.TextToHtmlRule(text="#01", fg_color="#00ff00")
        html_new_word = utility_cls.TextToHtmlRule(text="#31", fg_color="#00cb00")
        html_rule_base_title =  utility_cls.TextToHtmlRule(text="#91", fg_color="#00ff00", font_size=28)
        html_rule_base_title.set_default_offset_shadow()
        html_rule_suff = utility_cls.TextToHtmlRule(text="#02", fg_color="#e7e773")

        html.add_rule([html_rule_base, html_rule_base_title, html_rule_suff, html_new_word])

        for idx, item in enumerate(base_items_list):
            # Options Menu Item
            name = self.getl("syn_hint_menu_options_text").replace("#01", item)
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            tooltip = self.getl("syn_hint_menu_options_tt")
            html_rule_base.replace_with = item
            tooltip = tooltip.replace("#10", self.getl("syn_hint_menu_create_text"))
            tooltip = tooltip.replace("#11", self.getl("syn_hint_menu_update_text"))
            tooltip = tooltip.replace("#12", self.getl("syn_hint_menu_delete_text"))
            html.set_text(tooltip)
            tooltip = html.get_html()

            item_icon = self.getv("options_icon_path")

            menu_item = self._create_menu_item(idx, name, tooltip=tooltip, clickable=False, icon=item_icon)

            html_rule_base_title.replace_with = item
            html_rule_base.replace_with = item

            # Create new shema Menu Item
            item_icon = self.getv("add_schema_icon_path")

            name = self.getl("syn_hint_menu_create_text").replace("#01", item)
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            tooltip = self.getl("syn_hint_menu_create_tt") + "\n\n"
            suffs = self.text_func.get_suffixes_for_base_string(item, match_case=True)
            suf_rules = []
            column = 0
            for suff_idx, suff in enumerate(suffs):
                if column == int(len(suffs) / 30):
                    delimiter = "\n"
                    column = 0
                else:
                    column += 1
                    delimiter = "     \t"
                tooltip += f'\t- #01(#S{suff_idx}#){delimiter}'
                suf_rules.append(utility_cls.TextToHtmlRule(text=f"#S{suff_idx}#", replace_with=suff, fg_color="#ffff00"))
            html.add_rule(suf_rules)
            html.set_text(tooltip)
            tooltip = html.get_html()
            html.delete_rule(suf_rules)
            shema_item = self._create_menu_item(idx + 1000, name, tooltip=tooltip, icon=item_icon)
            if item in self.shemas:
                disab.append(idx + 1000)
            menu_item[4].append(shema_item)

            # Update shema Menu Item
            item_icon = self.getv("update_schema_icon_path")
            old_suffs = ""
            if item in self.shemas:
                old_suffs = ", ".join(self.shemas[item]["suffs"])
            old_suffs = f"( {old_suffs} )"
            name = self.getl("syn_hint_menu_update_text").replace("#01", f"{item} {old_suffs}")
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            tooltip = self.getl("syn_hint_menu_update_tt") + "\n\n"
            
            old_suffs = "---"
            if item in self.shemas:
                if self.shemas[item]["suffs"]:
                    old_suffs = ", ".join(self.shemas[item]["suffs"])
                    old_suffs = f"( {old_suffs} )"

            html_rule_suff.replace_with = old_suffs

            suffs = self.text_func.get_suffixes_for_base_string(item, match_case=True)
            suf_rules = []
            column = 0
            for suff_idx, suff in enumerate(suffs):
                if column == int(len(suffs) / 30):
                    delimiter = "\n"
                    column = 0
                else:
                    column += 1
                    delimiter = "     \t"
                tooltip += f'\t- #01(#S{suff_idx}#){delimiter}'
                suf_rules.append(utility_cls.TextToHtmlRule(text=f"#S{suff_idx}#", replace_with=suff, fg_color="#ffff00"))
            html.add_rule(suf_rules)
            html.set_text(tooltip)
            tooltip = html.get_html()
            html.delete_rule(suf_rules)
            shema_item = self._create_menu_item(idx + 2000, name, tooltip=tooltip, icon=item_icon)
            if item not in self.shemas:
                disab.append(idx + 2000)
            menu_item[4].append(shema_item)

            # Delete shema Menu Item
            item_icon = self.getv("delete_schema_icon_path")
            old_suffs = ""
            if item in self.shemas:
                old_suffs = ", ".join(self.shemas[item]["suffs"])
            old_suffs = f"( {old_suffs} )"
            name = self.getl("syn_hint_menu_delete_text").replace("#01", f"{item} {old_suffs}")
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            tooltip = self.getl("syn_hint_menu_delete_tt")
            
            old_suffs = "---"
            if item in self.shemas:
                if self.shemas[item]["suffs"]:
                    old_suffs = ", ".join(self.shemas[item]["suffs"])
                    old_suffs = f"( {old_suffs} )"

            html_rule_suff.replace_with = old_suffs
            html.set_text(tooltip)
            tooltip = html.get_html()

            shema_item = self._create_menu_item(idx + 3000, name, tooltip=tooltip, icon=item_icon)
            if item not in self.shemas:
                disab.append(idx + 3000)
            menu_item[4].append(shema_item)


            menu_items.append(menu_item)
        
        # Add all other items from shema
        new_word = self.text_func.select_whole_lines_from_text_box(if_no_selection_select_all=False)
        new_word_list = [x for x in new_word.split("\n") if x != ""]
        new_word = new_word.replace("\n", ", ")
        
        for item in self.shemas:
            html_rule_base_title.replace_with = item
            html_rule_base.replace_with = item

            item_icon = None
            old_suffs = ""
            old_suffs = ", ".join(self.shemas[item]["suffs"])
            old_suffs = f"( {old_suffs} )"
            name = self.getl("syn_hint_menu_item_text").replace("#01", f"{item} {old_suffs}")
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            tooltip = self.getl("syn_hint_menu_item_tt") + "\n\n"
            
            suffs = self.shemas[item]["suffs"]
            suf_rules = []
            column = 0
            for suff_idx, suff in enumerate(suffs):
                if column == int(len(suffs) / 30):
                    delimiter = "\n"
                    column = 0
                else:
                    column += 1
                    delimiter = "     \t"
                tooltip += f'\t- #01(#S{suff_idx}#){delimiter}'
                suf_rules.append(utility_cls.TextToHtmlRule(text=f"#S{suff_idx}#", replace_with=suff, fg_color="#ffff00"))
            html.add_rule(suf_rules)
            html.set_text(tooltip)
            tooltip = html.get_html()
            html.delete_rule(suf_rules)
            shema_item = self._create_menu_item(f"SELECT:{item}", name, tooltip=tooltip, icon=item_icon)
            menu_items.append(shema_item)

            # Copy item suffixes
            name = self.getl("syn_hint_menu_item_copy_text").replace("#01", f"{item} {old_suffs}")
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            shema_item_copy = self._create_menu_item(f"C1:{item}", name, tooltip=tooltip, icon=item_icon)
            shema_item[4].append(shema_item_copy)

            # Copy item words
            name = self.getl("syn_hint_menu_item_copy_words_text").replace("#01", f"{item} --> {new_word}")
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)
            if not new_word:
                disab.append(f"C2:{item}")
            
            new_word_tt = self.getl("syn_hint_menu_item_word_tt") + "\n\n"
            suffs = self.shemas[item]["suffs"]
            suf_rules = []
            column = 0
            for suff_idx, suff in enumerate(suffs):
                if column == int(len(suffs) / 30):
                    delimiter = "\n"
                    column = 0
                else:
                    column += 1
                    delimiter = "     \t"
                new_word_tt += f'\t- #31(#S{suff_idx}#){delimiter}'
                suf_rules.append(utility_cls.TextToHtmlRule(text=f"#S{suff_idx}#", replace_with=suff, fg_color="#ffff00"))
            html.add_rule(suf_rules)
            html_new_word.replace_with = new_word
            html.set_text(new_word_tt)
            new_word_tt = html.get_html()
            html.delete_rule(suf_rules)

            shema_item_copy = self._create_menu_item(f"C2:{item}", name, tooltip=new_word_tt, icon=item_icon)
            shema_item[4].append(shema_item_copy)

            # Delete Item
            name = self.getl("syn_hint_menu_item_delete_text").replace("#01", f"{item} {old_suffs}")
            name = self.text_func.shrink_text(name, font=font, max_text_width=menu_item_width)

            shema_item_copy = self._create_menu_item(f"D0:{item}", name, tooltip=tooltip, icon=item_icon)
            shema_item[4].append(shema_item_copy)

            # Start Synonym Manager
            name = self.getl("syn_hint_menu_start_manager_text")
            tooltip = self.getl("syn_hint_menu_start_manager_tt")
            icon = self.getv("synonyms_icon_path")
            shema_item_copy = self._create_menu_item(f"M0:{item}", name, tooltip, icon=icon)
            shema_item[4].append(shema_item_copy)



        menu_dict = {
            "position": menu_position,
            "disabled": disab,
            "separator": separator,
            "items": menu_items
        }

        msg_dict = {
            "title": self.getl("syn_hin_msg_general_title"),
            "text": "",
            "icon_path": self.getv("synonyms_icon_path")
        }

        if not menu_items:
            msg_dict["text"] = self.getl("syn_hin_msg_no_data_text")
            return msg_dict
        
        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self.txt_box)
        menu_result = self.get_appv("menu")["result"]

        for idx, item in enumerate(base_items_list):
            if menu_result == idx + 1000:
                suffs = self.text_func.get_suffixes_for_base_string(item, match_case=True)
                self.shemas[item] = {}
                self.shemas[item]["suffs"] = suffs
                msg_dict["text"] = self.getl("syn_hin_msg_add_text").replace("#1", item)
            elif menu_result == idx + 2000:
                suffs = self.text_func.get_suffixes_for_base_string(item, match_case=True)
                self.shemas[item]["suffs"] = suffs
                msg_dict["text"] = self.getl("syn_hin_msg_update_text").replace("#1", item)
            elif menu_result == idx + 3000:
                self.shemas.pop(item)
                msg_dict["text"] = self.getl("syn_hin_msg_delete_text").replace("#1", item)
        if menu_result == 10010:
            self.clipboard.setText(txt_box_selection)
            msg_dict = None
        elif menu_result == 10020:
            text = self.txt_box.toPlainText()
            text = text.strip() + "\n" + self.clipboard.text() + "\n"
            self.txt_box.setText(text)
            # move cursor to end
            self.txt_box.moveCursor(QTextCursor.End)
            msg_dict = None
        elif menu_result == 10050:
            # Add no serbian letters items
            no_serbian_letters = UTILS.TextUtility.get_text_lines_without_serbian_chars(self.txt_box.toPlainText(), if_data_exist_add_string_at_end="\n", ignore_if_line_already_exist=True)
            if self.txt_box.toPlainText() and self.txt_box.toPlainText()[-1] != "\n":
                no_serbian_letters = "\n" + no_serbian_letters
            self.txt_box.setText(self.txt_box.toPlainText() + no_serbian_letters)
        elif menu_result == 10060:
            # Copy to clipboard no serbian letters items
            no_serbian_letters = UTILS.TextUtility.get_text_lines_without_serbian_chars(self.txt_box.toPlainText(), if_data_exist_add_string_at_end="\n")
            self.get_appv("clipboard").setText(no_serbian_letters)
        elif menu_result == 10070:
            # Replace no serbian letters in all items
            no_serbian_text = UTILS.TextUtility.clear_serbian_chars(self.txt_box.toPlainText())
            if self._ask_to_replace_serbian_chars():
                self.txt_box.setText(no_serbian_text)
        elif menu_result == 10100:
            msg_dict = None
            SynonymManager(self._stt, self._parent_widget, suggested_words=self._base_string)

        if isinstance(menu_result, str):
            if len(menu_result) > 2:
                if menu_result[:3] == "C1:":
                    item = menu_result[3:]
                    if item in self.shemas:
                        txt = "\n".join(self.shemas[item]["suffs"])
                        txt += "\n"
                        self.get_appv("clipboard").setText(txt)
                        msg_dict["text"] = self.getl("syn_hin_msg_item_copy_suffs_text").replace("#1", item)
                if menu_result[:3] == "C2:":
                    item = menu_result[3:]
                    if item in self.shemas:
                        txt = ""
                        for j in new_word_list:
                            for i in self.shemas[item]["suffs"]:
                                txt += f"{j}{i}\n"
                        self.get_appv("clipboard").setText(txt)
                        msg_dict["text"] = self.getl("syn_hin_msg_item_copy_word_text").replace("#1", item)
                if menu_result[:3] == "D0:":
                    item = menu_result[3:]
                    if item in self.shemas:
                        self.shemas.pop(item)
                        msg_dict["text"] = self.getl("syn_hin_msg_delete_text").replace("#1", item)
                if menu_result[:3] == "M0:":
                    item = menu_result[3:]
                    msg_dict = None
                    SynonymManager(self._stt, self._parent_widget, shema_name=item, suggested_words=self._base_string)

        if show_raport:
            return msg_dict

    def _create_menu_item(self, id, name: str, tooltip: str = "", clickable: bool = True, icon: str = None):
        result = [
            id,
            name,
            tooltip,
            clickable,
            [],
            icon
        ]
        return result

    def _ask_to_replace_serbian_chars(self) -> bool:
        msg_dict = {
            "title": self.getl("add_def_syn_hint_msg_replace_serbian_chars_title"),
            "text": self.getl("add_def_syn_hint_msg_replace_serbian_chars_text"),
            "position": "center",
            "pos_center": False,
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True],
            ]
        }
        utility_cls.MessageQuestion(self._stt, self._parent_widget, msg_dict)
        if msg_dict["result"] != 10:
            return False
        return True

    def get_shemas(self) -> dict:
        if "def_syn_shemas" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("def_syn_shemas", {}, save_to_file=True)
        
        return self.get_appv("def_syn_shemas")


class DefinitionEditor(QDialog):
    SAMOGLASNICI = ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"]
    PRIDEV_N = ["a", "e", "i", "o", "u", "im", "ima", "om", "ome", "ih", "og", "oga", "oj"]
    PRIDEV_IJ = ["a", "e", "i", "o", "u", "im", "ima", "om", "ome", "em", "emu", "ih", "eg", "ega", "oj"]

    def __init__(self, settings: settings_cls.Settings, parent_obj, expression: str = None, *args, **kwargs):
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_obj, *args, **kwargs)

        # Define other variables
        self._parent_widget = parent_obj
        self._padezi_image = None
        self._dont_clear_menu = False
        self.variant: dict = {}
        self.ignore_txt_output_text_changed = False

        # Load GUI
        uic.loadUi(self.getv("definition_editor_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()
        self._text_handler_output = text_handler_cls.TextHandler(self._stt, self.txt_output, self)

        self.txt_output_text_changed()
        
        self.load_widgets_handler()
        
        self._synonyms_hint = SynonymHint(self._stt, self, self.txt_output)

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_clear_base.clicked.connect(self.btn_clear_base_click)
        self.btn_clear_beggining.clicked.connect(self.btn_clear_beggining_click)
        self.btn_clear_end.clicked.connect(self.btn_clear_end_click)
        self.btn_clear_output.clicked.connect(self.btn_clear_output_click)
        self.btn_copy.clicked.connect(self.btn_copy_click)
        self.txt_output.textChanged.connect(self.txt_output_text_changed)
        self.txt_output.contextMenuEvent = self.txt_output_context_menu_triggered
        self.txt_output.mouseMoveEvent = self._txt_output_mouse_move
        self.btn_switch_words_order.clicked.connect(self.btn_switch_words_order_click)
        self.btn_generate.clicked.connect(self.btn_generate_click)
        self.txt_base.textChanged.connect(self.btn_base_text_changed)
        self.txt_beggining.keyPressEvent = self._txt_beggining_key_press
        self.txt_end.keyPressEvent = self._txt_end_key_press
        self.chk_add_end.mouseReleaseEvent = self._chk_end_mouse_release
        self.keyPressEvent = self._key_press_event
        self.btn_clip_content.clicked.connect(self.btn_clip_content_click)

        self.btn_edit_output.clicked.connect(self.btn_edit_output_click)
        self.txt_edit_replace.textChanged.connect(self.txt_edit_replace_text_changed)
        self.txt_edit_add_beg.textChanged.connect(self.txt_edit_add_beg_text_changed)
        self.txt_edit_add_end.textChanged.connect(self.txt_edit_add_end_text_changed)
        self.txt_edit_in_string.textChanged.connect(self.txt_edit_in_string_click)
        self.btn_edit_switch.clicked.connect(self.btn_edit_switch_click)
        self.btn_edit_replace.clicked.connect(self.btn_edit_replace_click)
        self.btn_edit_replace_add.clicked.connect(self.btn_edit_replace_add_click)
        self.chk_edit_case.stateChanged.connect(self.chk_edit_case_state_changed)
        self.btn_edit_add_beg.clicked.connect(self.btn_edit_add_beg_click)
        self.btn_edit_add_end.clicked.connect(self.btn_edit_add_end_click)
        self.btn_edit_spaces.clicked.connect(self.btn_edit_spaces_click)
        self.btn_edit_close.clicked.connect(self.btn_edit_close_click)
        self.btn_edit_case.clicked.connect(self.btn_edit_case_click)
        self.btn_edit_case.mouseReleaseEvent = self.btn_edit_case_mouse_release
        self.btn_first_letter.clicked.connect(self.btn_first_letter_click)
        
        self.btn_padezi_close.clicked.connect(self.btn_padezi_close_click)
        self.action_show_padezi.triggered.connect(self._show_padezi_frame)
        self.lbl_padezi_img.mouseDoubleClickEvent = self.lbl_padezi_img_double_click
        self.lbl_padezi_text.mouseDoubleClickEvent = self.lbl_padezi_text_double_click

        self.lbl_auto_show.mousePressEvent = self._lbl_auto_show_mouse_press

        self.get_appv("clipboard").changed.connect(self._clipboard_changed)

        # Variant
        self.btn_variant_close.clicked.connect(self.variant_hide)
        self.btn_variant_opt1.enterEvent = self.btn_variant_opt1_enter_event
        self.btn_variant_opt1.leaveEvent = self.btn_variant_opt1_leave_event
        self.btn_variant_opt1.clicked.connect(self.btn_variant_opt1_click)
        self.btn_variant_opt2.enterEvent = self.btn_variant_opt2_enter_event
        self.btn_variant_opt2.leaveEvent = self.btn_variant_opt2_leave_event
        self.btn_variant_opt2.clicked.connect(self.btn_variant_opt2_click)
        self.btn_variant_opt3.enterEvent = self.btn_variant_opt3_enter_event
        self.btn_variant_opt3.leaveEvent = self.btn_variant_opt3_leave_event
        self.btn_variant_opt3.clicked.connect(self.btn_variant_opt3_click)
        self.lst_variant.itemClicked.connect(self.lst_variant_item_clicked)
        self.lst_variant.mouseMoveEvent = self.lst_variant_mouse_move
        self.lst_variant.leaveEvent = self.lst_variant_mouse_leave
        self.lst_variant.itemSelectionChanged.connect(self.lst_variant_selection_changed)

        if expression:
            self.txt_base.setText(expression)

        self._load_win_position()
        self.show_menu_selection_result(self.lbl_auto_show.objectName())

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["DefinitionEditor"])
        self.txt_base.setFocus()
        if self.txt_edit_replace.text():
            self.btn_edit_replace.setEnabled(True)
            self.btn_edit_replace_add.setEnabled(True)

    def _txt_output_mouse_move(self, e: QtGui.QMouseEvent) -> None:
        if self._text_handler_output:
            self._text_handler_output.show_definition_on_mouse_hover(e)
        QTextEdit.mouseMoveEvent(self.txt_output, e)

    def btn_clip_content_click(self):
        self.txt_base.setText(self.get_valid_clipboard_text())
        self.btn_clip_content.setVisible(False)

    def get_valid_clipboard_text(self) -> str:
        text: str = self.get_appv("clipboard").text()
        if not text:
            return None
        
        text = text.strip()
        
        if text == self.txt_base.text():
            return None
        
        if len(text) < 3:
            return None
        
        if text.count("\n") > 0:
            return None
        
        if text.count(" ") > 3:
            return None
        
        return text.replace("\t", " ")

    def _clipboard_changed(self):
        if self.get_valid_clipboard_text():
            self.btn_clip_content.setText("Clipboard:\n" + self.get_valid_clipboard_text())
            self.btn_clip_content.setVisible(True)
        else:
            self.btn_clip_content.setVisible(False)

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
        frm_padezi = self.widget_handler.add_QFrame(self.frm_padezi)
        frm_padezi.add_window_drag_widgets([self, self.lbl_padezi_img, self.lbl_padezi_text])

        frm_edit = self.widget_handler.add_QFrame(self.frm_edit)
        frm_edit.add_window_drag_widgets([self])

        frm_variant = self.widget_handler.add_QFrame(self.frm_variant)
        frm_variant.add_window_drag_widgets([self.frm_variant, self.lbl_variant_title])

        frm_variant_pre = self.widget_handler.add_QFrame(self.frm_variant_pre)
        frm_variant_pre.add_window_drag_widgets([self.frm_variant_pre, self.lbl_variant_pre_title])

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)

        btn_variant_opt1: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(self.btn_variant_opt1, return_none_if_not_found=True)
        if btn_variant_opt1:
            btn_variant_opt1.properties.allow_bypass_enter_event = False
            btn_variant_opt1.properties.allow_bypass_leave_event = False

        btn_variant_opt2: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(self.btn_variant_opt2, return_none_if_not_found=True)
        if btn_variant_opt2:
            btn_variant_opt2.properties.allow_bypass_enter_event = False
            btn_variant_opt2.properties.allow_bypass_leave_event = False
        
        btn_variant_opt3: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(self.btn_variant_opt3, return_none_if_not_found=True)
        if btn_variant_opt3:
            btn_variant_opt3.properties.allow_bypass_enter_event = False
            btn_variant_opt3.properties.allow_bypass_leave_event = False

        for btn in self.btn_variant_extras:
            btn_variant: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(btn, return_none_if_not_found=True)
            if btn_variant:
                btn_variant.properties.allow_bypass_enter_event = False
                btn_variant.properties.allow_bypass_leave_event = False
                btn_variant.properties.tap_event_change_stylesheet_enabled = False

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_base, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_output, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_end, {"allow_bypass_key_press_event": False})
        self.widget_handler.add_TextBox(self.txt_beggining, {"allow_bypass_key_press_event": False})
        self.widget_handler.add_TextBox(self.txt_edit_replace, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_edit_with, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_edit_in_string, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_edit_add_beg, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_edit_add_end, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets(starting_widget=self)

        self.widget_handler.activate()

    def lst_variant_item_clicked(self, item: QListWidgetItem):
        if item is None:
            return
        self.txt_output.setText(self.variant[str(item.data(Qt.UserRole))]["content"])

    def lst_variant_selection_changed(self):
        item = self.lst_variant.currentItem()
        if item is None or not self.frm_variant.isVisible() or not self.lst_variant.isVisible():
            return
        self.txt_output.setText(self.variant[str(item.data(Qt.UserRole))]["content"])

    def lst_variant_mouse_move(self, event):
        if event is None:
            return
        item = self.lst_variant.itemAt(event.pos())
        if item is None:
            return

        self.lbl_variant_pre_content.setText(self.variant[str(item.data(Qt.UserRole))]["content"])
        self.frm_variant_pre.setVisible(True)

    def lst_variant_mouse_leave(self, event):
        self.frm_variant_pre.setVisible(False)

    def btn_variant_opt1_click(self):
        self.txt_output.setText(self.variant["1"]["content"])
        extra_buttons_text = self.variant["1"].get("extra", None)
        if extra_buttons_text:
            for idx, btn in enumerate(self.btn_variant_extras):
                btn: QPushButton
                text = extra_buttons_text[idx] if idx < len(extra_buttons_text) else ""
                btn.setText(text)

    def btn_variant_opt2_click(self):
        self.txt_output.setText(self.variant["2"]["content"])
        extra_buttons_text = self.variant["2"].get("extra", None)
        if extra_buttons_text:
            for idx, btn in enumerate(self.btn_variant_extras):
                btn: QPushButton
                text = extra_buttons_text[idx] if idx < len(extra_buttons_text) else ""
                btn.setText(text)

    def btn_variant_opt3_click(self):
        self.txt_output.setText(self.variant["3"]["content"])
        extra_buttons_text = self.variant["3"].get("extra", None)
        if extra_buttons_text:
            for idx, btn in enumerate(self.btn_variant_extras):
                btn: QPushButton
                text = extra_buttons_text[idx] if idx < len(extra_buttons_text) else ""
                btn.setText(text)

    def btn_variant_opt1_enter_event(self, event):
        try:
            self.lbl_variant_pre_content.setText(self.variant["1"]["content"])
            self.frm_variant_pre.setVisible(True)
        except KeyError:
            self.frm_variant_pre.setVisible(False)
    
    def btn_variant_opt1_leave_event(self, event):
        self.frm_variant_pre.setVisible(False)
    
    def btn_variant_opt2_enter_event(self, event):
        try:
            self.lbl_variant_pre_content.setText(self.variant["2"]["content"])
            self.frm_variant_pre.setVisible(True)
        except KeyError:
            self.frm_variant_pre.setVisible(False)
    
    def btn_variant_opt2_leave_event(self, event):
        self.frm_variant_pre.setVisible(False)
    
    def btn_variant_opt3_enter_event(self, event):
        try:
            self.lbl_variant_pre_content.setText(self.variant["3"]["content"])
            self.frm_variant_pre.setVisible(True)
        except KeyError:
            self.frm_variant_pre.setVisible(False)
    
    def btn_variant_opt3_leave_event(self, event):
        self.frm_variant_pre.setVisible(False)

    def colorize_variant_extra_buttons(self, text: str = None):
        added_stylesheet = "QPushButton {color: #ffff00; background-color: #00bd5b; border: 1px solid #3700a5;} QPushButton:hover {color: #aaffff; border: 1px solid #7ce7ff;}"
        not_added_stylesheet = "QPushButton {color: #f3f3f3; background-color: #414141; border: 1px solid #3700a5;} QPushButton:hover {color: #aaffff; border: 1px solid #7ce7ff;}"

        if text is None:
            text = self.txt_output.toPlainText()
        
        for btn in self.btn_variant_extras:
            btn: QPushButton
            if btn.text() in [x.strip() for x in text.split("\n") if x != ""]:
                btn.setStyleSheet(added_stylesheet)
            else:
                btn.setStyleSheet(not_added_stylesheet)

    def event_variant_extra_button_clicked(self, button: QPushButton = None):
        if button is None:
            return
        if button.text() not in [x.strip() for x in self.txt_output.toPlainText().split("\n") if x != ""]:
            text = self.txt_output.toPlainText().strip() + "\n" + button.text() + "\n"
            self.txt_output.setText(text)
            self.txt_output.moveCursor(QTextCursor.End)
            self.colorize_variant_extra_buttons(text)

    def event_variant_mouse_release(self, event, button: QPushButton = None):
        if event.button() == Qt.RightButton:
            if button is not None:
                if button.text() in [x.strip() for x in self.txt_output.toPlainText().split("\n") if x != ""]:
                    text = "\n".join([x for x in self.txt_output.toPlainText().split("\n") if x.strip() and x != button.text()]) + "\n"
                    self.txt_output.setText(text)
                    self.txt_output.moveCursor(QTextCursor.End)
                    self.colorize_variant_extra_buttons(text)
        
        QPushButton.mouseReleaseEvent(button, event)

    def variant_show(self, opt1: str = None, opt2: str = None, opt3: str = None, extra_plus: dict = None):
        if opt1 is None and opt2 is None and opt3 is None:
            self.variant_hide()
            return
        
        self.btn_variant_opt1.setVisible(False)
        self.btn_variant_opt2.setVisible(False)
        self.btn_variant_opt3.setVisible(False)
        self.lst_variant.clear()
        self.lst_variant.setVisible(False)

        self.variant = {}
        self.variant["1"] = {}
        self.variant["2"] = {}
        self.variant["3"] = {}

        if extra_plus:
            self.frm_variant.resize(440, self.frm_variant.height())
            self.variant["1"]["extra"] = extra_plus["opt1"]
            self.variant["2"]["extra"] = extra_plus["opt2"]
            self.variant["3"]["extra"] = extra_plus["opt3"]
            for idx, item in enumerate(self.variant["1"]["extra"]):
                self.btn_variant_extras[idx].setText(item)
        else:
            self.frm_variant.resize(195, self.frm_variant.height())

        if isinstance(opt1, list):
            for idx, opt in enumerate(opt1):
                if opt.find(";") == -1:
                    name = "Opcija"
                    content = [x.strip() for x in opt.split(",") if x.strip()]
                else:
                    name = opt.split(";")[0].strip()
                    content = [x.strip() for x in opt[opt.find(";") + 1:].split(",") if x.strip()]
                
                self.variant[str(idx)] = {}
                self.variant[str(idx)]["name"] = name
                self.variant[str(idx)]["content"] = "\n".join(content) if content else ""

                lst_item = QListWidgetItem()
                lst_item.setText(name)
                lst_item.setData(Qt.UserRole, idx)
                if "FIX" in name:
                    lst_item.setBackground(QColor("grey"))
                self.lst_variant.addItem(lst_item)

            self.lst_variant.setVisible(True)
            self.frm_variant.setVisible(True)
            if opt2 is not None:
                self.lst_variant.setCurrentRow(opt2)

            return

        if opt1:
            self.btn_variant_opt1.setVisible(True)

            if opt1.find(";") == -1:
                name = "Opcija 1"
                content = [x.strip() for x in opt1.split(",") if x.strip()]
            else:
                name = opt1.split(";")[0].strip()
                content = [x.strip() for x in opt1[opt1.find(";") + 1:].split(",") if x.strip()]
            
            self.variant["1"]["name"] = name
            self.variant["1"]["content"] = "\n".join(content) if content else ""

            self.btn_variant_opt1.setText(name)
        
        if opt2:
            self.btn_variant_opt2.setVisible(True)

            if opt2.find(";") == -1:
                name = "Opcija 2"
                content = [x.strip() for x in opt2.split(",") if x.strip()]
            else:
                name = opt2.split(";")[0].strip()
                content = [x.strip() for x in opt2[opt2.find(";") + 1:].split(",") if x.strip()]
            
            self.variant["2"]["name"] = name
            self.variant["2"]["content"] = "\n".join(content) if content else ""

            self.btn_variant_opt2.setText(name)
        
        if opt3:
            self.btn_variant_opt3.setVisible(True)

            if opt3.find(";") == -1:
                name = "Opcija 3"
                content = [x.strip() for x in opt3.split(",") if x.strip()]
            else:
                name = opt3.split(";")[0].strip()
                content = [x.strip() for x in opt3[opt3.find(";") + 1:].split(",") if x.strip()]
            
            self.variant["3"]["name"] = name
            self.variant["3"]["content"] = "\n".join(content) if content else ""

            self.btn_variant_opt3.setText(name)
        
        self.frm_variant.setVisible(True)

    def variant_hide(self):
        self.frm_variant_pre.setVisible(False)
        self.frm_variant.setVisible(False)
        self.variant = {}

    def btn_switch_words_order_click(self):
        text_list = self.txt_output.toPlainText().splitlines()

        result = []

        for line in text_list:
            words = line.split(" ")
            if len(words) > 1:
                new_line = " ".join(words[1:]) + f" {words[0]}"
            else:
                new_line = line
            
            result.append(new_line)

        self.txt_output.setText("\n".join(result))

    def txt_output_context_menu_triggered(self, e: QtGui.QContextMenuEvent):
        UTILS.LogHandler.add_log_record("#1: Output TextBox context menu triggered.", ["DefinitionEditor"])
        self._dont_clear_menu = True
        result = self._synonyms_hint.show_contex_menu(base_string=self.txt_base.text())
        if result:
            self._dont_clear_menu = True
            utility_cls.MessageInformation(self._stt, self, result)

    def txt_output_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            cursor = self.txt_output.cursorForPosition(e.pos())
            cur = self.txt_output.textCursor()
            if not cur.hasSelection():
                cur.setPosition(cursor.position())
                self.txt_output.setTextCursor(cur)
            self._dont_clear_menu = True
            result = self._synonyms_hint.show_contex_menu(base_string=self.txt_base.text())
            if result:
                self._dont_clear_menu = True
                utility_cls.MessageInformation(self._stt, self, result)
        QTextEdit.mouseReleaseEvent(self.txt_output, e)

    def btn_first_letter_click(self):
        if not self.txt_base.text():
            return
        
        txt = self.txt_base.text()
        if txt[0].isupper():
            txt = txt[0].lower() + txt[1:]
        else:
            txt = txt[0].upper() + txt[1:]
        self.txt_base.setText(txt)

    def btn_edit_case_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self._context_case_btn_menu()
        QPushButton.mouseReleaseEvent(self.btn_edit_case, e)

    def _context_case_btn_menu(self):
        if not self.txt_output.toPlainText().strip():
            return
        
        menu_dict = {
            "position": QCursor.pos(),
            "separator": [15, 30, 50],
            "items": [
                [10, self.getl("def_editor_btn_edit_case_menu_first_switch_text"), self.getl("def_editor_btn_edit_case_menu_first_switch_tt"), True, [], None],
                [15, self.getl("def_editor_btn_edit_case_menu_not_first_switch_low_text"), self.getl("def_editor_btn_edit_case_menu_not_first_switch_low_tt"), True, [], None],
                [20, self.getl("def_editor_btn_edit_case_menu_up_text"), self.getl("def_editor_btn_edit_case_menu_up_tt"), True, [], None],
                [30, self.getl("def_editor_btn_edit_case_menu_low_text"), self.getl("def_editor_btn_edit_case_menu_low_tt"), True, [], None],
                [40, self.getl("def_editor_btn_edit_case_menu_all_word_up_text"), self.getl("def_editor_btn_edit_case_menu_all_word_up_tt"), True, [], None],
                [50, self.getl("def_editor_btn_edit_case_menu_all_word_low_text"), self.getl("def_editor_btn_edit_case_menu_all_word_low_tt"), True, [], None],
                [60, self.getl("def_editor_btn_edit_case_menu_all_up_text"), self.getl("def_editor_btn_edit_case_menu_all_up_tt"), True, [], None],
                [70, self.getl("def_editor_btn_edit_case_menu_all_low_text"), self.getl("def_editor_btn_edit_case_menu_all_low_tt"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]

        if result == 10:
            self._change_list_letter_case()
        elif result == 15:
            self._change_list_letter_case(mode="all_low_but_first")
        elif result == 20:
            self._change_list_letter_case(mode="first_up")
        elif result == 30:
            self._change_list_letter_case(mode="first_low")
        elif result == 40:
            self._change_list_letter_case(mode="word_up")
        elif result == 50:
            self._change_list_letter_case(mode="word_low")
        elif result == 60:
            self._change_list_letter_case(mode="all_up")
        elif result == 70:
            self._change_list_letter_case(mode="all_low")

    def _change_list_letter_case(self, mode: str = "switch"):
        txt = self.txt_output.toPlainText().strip()
        if not txt:
            return
        
        txt_list = [x for x in txt.split("\n") if x != ""]
        
        match mode:
            case "switch":
                for i in range(len(txt_list)):
                    if txt_list[i][0].isupper():
                        txt_list[i] = txt_list[i][0].lower() + txt_list[i][1:]
                    else:
                        txt_list[i] = txt_list[i][0].upper() + txt_list[i][1:]
                txt = "\n".join(txt_list) + "\n"
            case "first_up":
                for i in range(len(txt_list)):
                    txt_list[i] = txt_list[i][0].upper() + txt_list[i][1:]
                txt = "\n".join(txt_list) + "\n"
            case "first_low":
                for i in range(len(txt_list)):
                    txt_list[i] = txt_list[i][0].lower() + txt_list[i][1:]
                txt = "\n".join(txt_list) + "\n"
            case "word_low":
                for i in range(len(txt_list)):
                    row = txt_list[i]
                    change = True
                    pos = 0
                    result = ""
                    while True:
                        write_letter = row[pos]
                        if change:
                            write_letter = write_letter.lower()
                            change = False
                        result += write_letter
                        if write_letter == " ":
                            change = True
                        
                        pos += 1
                        if pos == len(row):
                            break

                    txt_list[i] = result
                txt = "\n".join(txt_list) + "\n"
            case "word_up":
                for i in range(len(txt_list)):
                    row = txt_list[i]
                    change = True
                    pos = 0
                    result = ""
                    while True:
                        write_letter = row[pos]
                        if change:
                            write_letter = write_letter.upper()
                            change = False
                        result += write_letter
                        if write_letter == " ":
                            change = True
                        
                        pos += 1
                        if pos == len(row):
                            break

                    txt_list[i] = result
                txt = "\n".join(txt_list) + "\n"
            case "all_low":
                for i in range(len(txt_list)):
                    txt_list[i] = txt_list[i].lower()
                txt = "\n".join(txt_list) + "\n"
            case "all_up":
                for i in range(len(txt_list)):
                    txt_list[i] = txt_list[i].upper()
                txt = "\n".join(txt_list) + "\n"
            case "all_low_but_first":
                for i in range(len(txt_list)):
                    txt_list[i] = txt_list[i][0] + txt_list[i][1:].lower()
                txt = "\n".join(txt_list) + "\n"
            
        self.txt_output.setText(txt)

    def btn_edit_case_click(self):
        self._change_list_letter_case()

    def _txt_beggining_key_press(self, e: QtGui.QKeyEvent):
        txt_beginning: qwidgets_util_cls.Widget_TextBox = self.widget_handler.find_child(self.txt_beggining)
        if txt_beginning:
            txt_beginning.EVENT_key_press_event(e)

        if e.key() == Qt.Key_S and e.modifiers() == Qt.ControlModifier:
            text_list = self.txt_beggining.toPlainText().split("\n")
            if text_list:
                base_string = text_list[-1]
                text_list[-1] = base_string + "a"
                text_list.append(base_string + "e")
                text_list.append(base_string + "i")
                text_list.append(base_string + "o")
                text_list.append(base_string + "u")
                self.txt_beggining.setText("\n".join(text_list))
                cur = self.txt_beggining.textCursor()
                cur.setPosition(len(self.txt_beggining.toPlainText()))
                self.txt_beggining.setTextCursor(cur)
        if e.key() == Qt.Key_A and e.modifiers() == Qt.ControlModifier:
            self._context_menu_add_pref_suf(self.txt_beggining)

        QTextEdit.keyPressEvent(self.txt_beggining, e)

    def _chk_end_mouse_release(self, e: QtGui.QMouseEvent):
        self.variant_hide()
        if e.button() == Qt.RightButton:
            self._context_menu_add_pref_suf(self.txt_end)
        QCheckBox.mouseReleaseEvent(self.chk_add_end, e)

    def _txt_end_key_press(self, e: QtGui.QKeyEvent):
        txt_end: qwidgets_util_cls.Widget_TextBox = self.widget_handler.find_child(self.txt_end)
        if txt_end:
            txt_end.EVENT_key_press_event(e)

        if e.key() == Qt.Key_S and e.modifiers() == Qt.ControlModifier:
            text_list = self.txt_end.toPlainText().split("\n")
            if text_list:
                base_string = text_list[-1]
                text_list[-1] = base_string + "a"
                text_list.append(base_string + "e")
                text_list.append(base_string + "i")
                text_list.append(base_string + "o")
                text_list.append(base_string + "u")
                self.txt_end.setText("\n".join(text_list))
                cur = self.txt_end.textCursor()
                cur.setPosition(len(self.txt_end.toPlainText()))
                self.txt_end.setTextCursor(cur)
        if e.key() == Qt.Key_Space and e.modifiers() == Qt.ControlModifier:
            self._context_menu_add_pref_suf(self.txt_end)

        QTextEdit.keyPressEvent(self.txt_end, e)

    def _lbl_auto_show_mouse_press(self, e: QtGui.QMouseEvent):
        self.variant_hide()
        self._context_menu_add_pref_suf(self.lbl_auto_show)

        QLabel.mousePressEvent(self.lbl_auto_show, e)

    def _context_menu_add_pref_suf(self, text_box: QTextEdit):
        menu_dict = {
            "position": self.mapToGlobal(text_box.pos()),
            "separator": [50, 1010, 2000, 3010],
            "items": [
                [10, self.getl("def_editor_c_menu_pref_suf_imenica_text"), self.getl("def_editor_c_menu_pref_suf_imenica_tt"), True, [], None],
                [40, self.getl("def_editor_c_menu_pref_suf_imenica_strana_sa_crticom_text"), self.getl("def_editor_c_menu_pref_suf_imenica_strana_sa_crticom_tt"), True, [], None],
                [50, self.getl("def_editor_c_menu_pref_suf_imenica_strana_bez_crtica_text"), self.getl("def_editor_c_menu_pref_suf_imenica_strana_bez_crtica_tt"), True, [], None],

                [1000, self.getl("def_editor_c_menu_pref_suf_pridev_text"), self.getl("def_editor_c_menu_pref_suf_pridev_tt"), True, [], None],
                [1010, self.getl("def_editor_c_menu_pref_suf_pridev_komp_text"), self.getl("def_editor_c_menu_pref_suf_pridev_komp_tt"), True, [], None],

                [2000, self.getl("def_editor_c_menu_pref_suf_glagol_text"), self.getl("def_editor_c_menu_pref_suf_glagol_tt"), True, [], None],

                [3000, self.getl("def_editor_c_menu_pref_suf_ime_musko_text"), self.getl("def_editor_c_menu_pref_suf_ime_musko_tt"), True, [], None],
                [3010, self.getl("def_editor_c_menu_pref_suf_ime_zensko_text"), self.getl("def_editor_c_menu_pref_suf_ime_zensko_tt"), True, [], None],

                [4000, self.getl("def_editor_c_menu_pref_suf_vise_reci_text"), self.getl("def_editor_c_menu_pref_suf_vise_reci_tt"), True, [], None],
                [4010, self.getl("def_editor_c_menu_pref_suf_vise_reci_jednina_text"), self.getl("def_editor_c_menu_pref_suf_vise_reci_jednina_tt"), True, [], None],
            ]
        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]

        self.show_menu_selection_result(result)

    def show_menu_selection_result(self, result: int):
        if isinstance(result, str):
            result = UTILS.TextUtility.get_integer(result, on_error_return=0)

        self.lbl_auto_show.setObjectName(str(result))

        if result == 10:
            syn_list = self._imenica()
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_imenica_text"))
        elif result == 40:
            syn_list = self._imenica(sa_crticom=True)
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_imenica_strana_sa_crticom_text"))
        elif result == 50:
            syn_list = self._imenica(strana_bez_crtica=True)
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_imenica_strana_bez_crtica_text"))
        elif result == 1000:
            syn_list = self._pridev()
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_pridev_text"))
        elif result == 1010:
            syn_list = self._pridev(komparacija=True)
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_pridev_komp_text"))
        elif result == 2000:
            syn_list = self._glagol()
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.colorize_variant_extra_buttons()
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_glagol_text"))
        elif result == 3000:
            syn_list = self.vlastito_ime(musko_ime=True)
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_ime_musko_text"))
        elif result == 3010:
            syn_list = self.vlastito_ime(zensko_ime=True)
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_ime_zensko_text"))
        elif result == 4000:
            syn_list = self.vise_reci()
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_vise_reci_text"))
        elif result == 4010:
            syn_list = self.vise_reci(samo_jednina=True)
            self.txt_output.setText("\n".join(syn_list) + "\n")
            self.lbl_auto_show.setText(self.getl("def_editor_c_menu_pref_suf_vise_reci_jednina_text"))
        else:
            self.lbl_auto_show.setObjectName("0")
            self.lbl_auto_show.setText("- - -")

    def _make_suffs(self, *args) -> str:
        """
        Param: agrs: String delimited with ","
        <p>Return: String delimited with <b>new line</b></p>
        """
        result = ""

        if len(args) == 1:
            args = [x.strip() for x in args[0].split(",") if x.strip()]

        if not args:
            return ""

        for arg in args:
            arg = arg.strip()
            if not arg:
                continue

            result += f"{arg}\n"

        return result

    def sibilarizacija(self, char: str) -> str:
        """kgh -> czs"""
        if char.lower() == "k":
            return "c"
        elif char.lower() == "g":
            return "z"
        elif char.lower() == "h":
            return "s"
        
        return char
    
    def palatalizacija(self, char: str) -> str:
        """kgh -> čžš"""
        if char.lower() == "k":
            return "č"
        elif char.lower() == "g":
            return "ž"
        elif char.lower() == "h":
            return "š"
        
        return char

    def reverse_palatalizacija(self, char: str) -> str:
        """čžš -> kgh"""
        if char.lower() == "č":
            return "k"
        elif char.lower() == "ž":
            return "g"
        elif char.lower() == "š":
            return "h"
        
        return char

    def reverse_sibilarizacija(self, char: str) -> str:
        """čžš -> czs"""
        if char.lower() == "č":
            return "c"
        elif char.lower() == "ž":
            return "z"
        elif char.lower() == "š":
            return "s"
        
        return char

    def _imenica(self, sa_crticom: bool = False, strana_bez_crtica: bool = False, return_declination: bool = False, return_adjective: bool = False, declination_and_adjective_level: int = 1) -> list:
        base_str = self.txt_base.text().replace("\n", " ").strip()
        if not base_str:
            return []

        base_str_preff = ""
        base_str_suff = ""
        while True:
            if not base_str[-1].isalnum():
                base_str_suff += base_str[-1]
                base_str = base_str[:-1]

            if not base_str:
                return []

            if not base_str[0].isalnum():
                base_str_preff += base_str[0]
                base_str = base_str[1:]

            if not base_str:
                return []
            
            if base_str[-1].isalnum() and base_str[0].isalnum():
                break

        if len(base_str) < 3:
            return []

        suff = ""
        
        # decl - sadrzi deklinaciju 7 padeza jednine + 7 padeza mnozine
        decl = ""
        decl2 = ""
        decl3 = ""
        decl_p = ""
        decl_p2 = ""
        decl_p3 = ""

        if sa_crticom or strana_bez_crtica:
            if sa_crticom:
                crtica = "-"
            else:
                crtica = ""

            if base_str[-1].lower() in ["a"]:
                nastavak = base_str[-1]
                base_str = base_str[:-1]
                suff = self._make_suffs(f"{nastavak}, {nastavak}{crtica}e, {nastavak}{crtica}i, {nastavak}{crtica}u, {nastavak}{crtica}o, {nastavak}{crtica}om, {nastavak}{crtica}ama")
                suff += self._make_suffs(*[f"{nastavak}{crtica}in{x}" for x in self.PRIDEV_N])
                suff += self._make_suffs(f"{nastavak}{crtica}in")
            elif base_str[-1].lower() in ["e", "o", "u"]:
                nastavak = base_str[-1]
                base_str = base_str[:-1]
                suff = self._make_suffs(f"{nastavak}, {nastavak}{crtica}a, {nastavak}{crtica}u, {nastavak}{crtica}om, {nastavak}{crtica}em, {nastavak}{crtica}i, {nastavak}{crtica}ima, {nastavak}{crtica}e")
                suff += self._make_suffs(*[f"{nastavak}{crtica}ov{x}" for x in self.PRIDEV_N])
                suff += self._make_suffs(f"{nastavak}{crtica}ov")
            elif base_str[-1].lower() in ["i"]:
                nastavak = base_str[-1]
                base_str = base_str[:-1]
                suff = self._make_suffs(f"{nastavak}, {nastavak}{crtica}ja, {nastavak}{crtica}ju, {nastavak}{crtica}jem, {nastavak}{crtica}jom, {nastavak}{crtica}ji, {nastavak}{crtica}jima, {nastavak}{crtica}je")
                suff += self._make_suffs(*[f"{nastavak}{crtica}jev{x}" for x in self.PRIDEV_N])
                suff += self._make_suffs(f"{nastavak}{crtica}jev")
                suff += self._make_suffs(*[f"{nastavak}{crtica}ev{x}" for x in self.PRIDEV_N])
                suff += self._make_suffs(f"{nastavak}{crtica}ev")
            else:
                nastavak = base_str[-1]
                base_str = base_str[:-1]
                suff = self._make_suffs(f"{nastavak}, {nastavak}{crtica}a, {nastavak}{crtica}u, {nastavak}{crtica}om, {nastavak}{crtica}em, {nastavak}{crtica}i, {nastavak}{crtica}ima, {nastavak}{crtica}e, {nastavak}{crtica}ovi, {nastavak}{crtica}ova, {nastavak}{crtica}ovima, {nastavak}{crtica}ove")
                suff += self._make_suffs(*[f"{nastavak}{crtica}ov{x}" for x in self.PRIDEV_N])
                suff += self._make_suffs(f"{nastavak}{crtica}ov")
        else:
            if base_str[-1].lower() in ["a", "e"]:
                # Obicna imenica - SAMOGLASNIK "a" na kraju
                nastavak = base_str[-1].lower()
                base_str = base_str[:-1]
                slovo_pre = base_str[-1]
                if base_str[-2:].lower() == "nj" and nastavak == "a":
                    # Ako zavrsava na "nja"  Patnja-Patnje
                    base_str = base_str[:-2]
                    suff = self._make_suffs("nja, nje, nji, nju, njo, njom, njama")
                    suff2 = self._make_suffs("nje, nja, nju, njem, njima")
                    # Nase patnje
                    decl = self._join_pref_base_suff("", base_str, "nja, nje, nji, nju, njo, njom, nji, nje, nji, njama, nje, nje, njama, njama")
                    decl_p = self._join_pref_base_suff("", base_str, "nja, nje, nji, nju, njo, njom, nji, nje, nji, njama, nje, nje, njama, njama")
                    # Unutrasnja azija
                    decl2 = self._join_pref_base_suff("", base_str, "nja, nje, njoj, nju, nja, njom, njoj, nje, njih, njim, nje, nje, njim, njim")
                    decl_p2 = self._join_pref_base_suff("", base_str, "nja, nje, njoj, nju, nja, njom, njoj, nje, njih, njim, nje, nje, njim, njim")
                    self.variant_show(
                        opt1 = "Patnja-Patnjama;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Saznanje-Saznanjima;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                    )
                elif base_str[-2:].lower() == "nj" and nastavak == "e":
                    # Ako zavrsava na "nje"  Saznanje-Saznanja
                    base_str = base_str[:-2]
                    suff = self._make_suffs("nje, nja, nju, njem, njima")
                    suff2 = self._make_suffs("nja, nje, nji, nju, njo, njom, njama")
                    # Moje poslednje
                    decl = self._join_pref_base_suff("", base_str, "nje, njeg, njem, nje, nje, njim, njem, nja, njih, njim, nje, nje, njim, njim")
                    # poslednje jutro
                    decl_p = self._join_pref_base_suff("", base_str, "nje, njeg, njem, nje, nje, njim, njem, nja, njih, njim, nja, nja, njim, njim")
                    self.variant_show(
                        opt1 = "Saznanje-Saznanjima;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Patnja-Patnjama;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                    )
                elif base_str[-1] == "j":
                    if nastavak == "a":
                        # kuja - kuje
                        suff = self._make_suffs(f"{nastavak}, e, i, u, o, om, ama")
                        # Kuja Crna
                        decl = self._join_pref_base_suff("", base_str, "a,e,i,u,o,om,i,e,a,ama,e,e,ama,ama")
                        # Crna kuja
                        decl_p = self._join_pref_base_suff("", base_str, "a,e,i,u,o,om,i,e,a,ama,e,e,ama,ama")
                    elif nastavak == "e":
                        # Sutomore - Sutomora
                        suff = self._make_suffs(f"{nastavak}, a, u, em, ima")
                        # Imenice koje imaju samo mnozinu  pantalone, gaće
                        suff2 = self._make_suffs(f"{nastavak}, a, ama")
                        # Slavno Sutomore
                        decl = self._join_pref_base_suff("", base_str, "e,a,u,e,e,em,u,a,a,ima,a,a,ima,ima")
                        # Sutomore slavno
                        decl_p = self._join_pref_base_suff("", base_str, "e,a,u,e,e,em,u,a,a,ima,a,a,ima,ima")
                        # Moje pantalone
                        decl2 = self._join_pref_base_suff("", base_str, "e,a,ama,e,e,ama,ama,e,a,ama,e,e,ama,ama")
                        decl_p2 = self._join_pref_base_suff("", base_str, "e,a,ama,e,e,ama,ama,e,a,ama,e,e,ama,ama")
                        self.variant_show(
                            opt1 = "Sutomore-Sutomora;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                            opt2 = "Samo mnozina - pantalone;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                        )
                elif base_str[-2:].lower() in ["sk", "šk", "čk"]:
                    # Francuska-Francuske
                    suff = self._make_suffs("a, e, oj, u, o, om")
                    # Opaska - Opaske
                    suff2 = self._make_suffs(f"ka, ke, ki, {self.sibilarizacija(base_str[-1])}i, ku, ko, kom, aka, kama")
                    # Pljoska-Pljoske
                    suff3 = self._make_suffs(f"ka, ke, ki, {self.sibilarizacija(base_str[-1])}i, ku, ko, kom, aka, kama")
                    # Republika Francuska  Radnicka
                    decl = self._join_pref_base_suff("", base_str[:-1], f"ka, ke, koj, ku, ka, kom, koj, ke, kih, kim, ke, ke, kim, kim")
                    decl_p = self._join_pref_base_suff("", base_str[:-1], f"ka, ke, koj, ku, ka, kom, koj, ke, kih, kim, ke, ke, kim, kim")
                    # Mala opaska
                    decl2 = self._join_pref_base_suff("", base_str[:-1], f"ka, ke, {self.sibilarizacija(base_str[-1])}i, ku, ko, kom, {self.sibilarizacija(base_str[-1])}i, ke, aka, kama, ke, ke, kama, kama")
                    decl_p2 = self._join_pref_base_suff("", base_str[:-1], f"ka, ke, {self.sibilarizacija(base_str[-1])}i, ku, ko, kom, {self.sibilarizacija(base_str[-1])}i, ke, aka, kama, ke, ke, kama, kama")
                    # Limena Pljoska
                    decl3 = self._join_pref_base_suff("", base_str, "a, e, i, u, o, om, i, e, i, ama, e, e, ama, ama")
                    decl_p3 = self._join_pref_base_suff("", base_str, "a, e, i, u, o, om, i, e, i, ama, e, e, ama, ama")
                    self.variant_show(
                        opt1 = "Naziv jednina (Francuska);" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Naziv jed+mno (Opaska);" + ",".join([base_str[:-1] + x.strip() for x in suff2.split("\n") if x.strip()]),
                        opt3 = "Predmet (pljoska-pljoske);" + ",".join([base_str[:-1] + x.strip() for x in suff3.split("\n") if x.strip()])
                    )
                else:
                    # suff_mnozina za imenice koje imaju samo mnozinu - Leđa, Pantalone, Gaće
                    base_str = base_str[:-1]
                    if nastavak == "a":
                        # kuća - kuće - kućama
                        # scenarista - scenariste - scenaristima
                        suff = self._make_suffs(f"{slovo_pre}a,{slovo_pre}e,{self.sibilarizacija(slovo_pre)}i,{slovo_pre}i,{slovo_pre}u,{slovo_pre}o,{slovo_pre}om,{slovo_pre}ama")
                        suff2 = self._make_suffs(f"{slovo_pre}a,{slovo_pre}e,{self.sibilarizacija(slovo_pre)}i,{slovo_pre}i,{slovo_pre}u,{slovo_pre}o,{slovo_pre}om,{slovo_pre}ima")
                        suff_mnozina = self._make_suffs(f"{slovo_pre}{nastavak}, {slovo_pre}ima")
                        # nobelova - nobelovoj
                        decl = self._join_pref_base_suff("", base_str, f"{slovo_pre}a,{slovo_pre}e,{slovo_pre}oj,{slovo_pre}u,{slovo_pre}a,{slovo_pre}om,{slovo_pre}oj,{slovo_pre}e,{slovo_pre}ih,{slovo_pre}im,{slovo_pre}e,{slovo_pre}e,{slovo_pre}im,{slovo_pre}im")
                        decl_p = self._join_pref_base_suff("", base_str, f"{slovo_pre}a,{slovo_pre}e,{slovo_pre}oj,{slovo_pre}u,{slovo_pre}a,{slovo_pre}om,{slovo_pre}oj,{slovo_pre}e,{slovo_pre}ih,{slovo_pre}im,{slovo_pre}e,{slovo_pre}e,{slovo_pre}im,{slovo_pre}im")
                        # Scenarista
                        decl2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}a,{slovo_pre}e,{slovo_pre}i,{slovo_pre}u,{slovo_pre}o,{slovo_pre}om,{slovo_pre}i,{slovo_pre}e,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}e,{slovo_pre}i,{slovo_pre}ima,{slovo_pre}ima")
                        decl_p2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}a,{slovo_pre}e,{slovo_pre}i,{slovo_pre}u,{slovo_pre}o,{slovo_pre}om,{slovo_pre}i,{slovo_pre}e,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}e,{slovo_pre}i,{slovo_pre}ima,{slovo_pre}ima")
                        # Kuća
                        decl3 = self._join_pref_base_suff("", base_str, f"{slovo_pre}a,{slovo_pre}e,{self.sibilarizacija(slovo_pre)}i,{slovo_pre}u,{slovo_pre}o,{slovo_pre}om,{self.sibilarizacija(slovo_pre)}i,{slovo_pre}e,{slovo_pre}a,{slovo_pre}ama,{slovo_pre}e,{slovo_pre}e,{slovo_pre}ama,{slovo_pre}ama")
                        decl_p3 = self._join_pref_base_suff("", base_str, f"{slovo_pre}a,{slovo_pre}e,{self.sibilarizacija(slovo_pre)}i,{slovo_pre}u,{slovo_pre}o,{slovo_pre}om,{self.sibilarizacija(slovo_pre)}i,{slovo_pre}e,{slovo_pre}a,{slovo_pre}ama,{slovo_pre}e,{slovo_pre}e,{slovo_pre}ama,{slovo_pre}ama")
                        self.variant_show(
                            opt1 = "Kuća - Kućama;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                            opt2 = "Scenarista - Scenaristima;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()]),
                            opt3 = "Leđa - Leđima;" + ",".join([base_str + x.strip() for x in suff_mnozina.split("\n") if x.strip()])
                        )
                    elif nastavak == "e":
                        # Siže - Sižea
                        # Parče - Parčeta
                        suff = self._make_suffs(f"{slovo_pre}e,{slovo_pre}a,{slovo_pre}i,{slovo_pre}u,{slovo_pre}om,{slovo_pre}ima")
                        suff2 = self._make_suffs(f"{slovo_pre}e,{slovo_pre}eta,{slovo_pre}etu,{slovo_pre}etom,{slovo_pre}ad,{slovo_pre}adi,{slovo_pre}adima")
                        suff_mnozina = self._make_suffs(f"{slovo_pre}{nastavak}, {slovo_pre}a, {slovo_pre}ama")
                        # More jadransko
                        decl = self._join_pref_base_suff("", base_str, f"{slovo_pre}e,{slovo_pre}a,{slovo_pre}u,{slovo_pre}e,{slovo_pre}e,{slovo_pre}em,{slovo_pre}u,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}ima")
                        decl_p = self._join_pref_base_suff("", base_str, f"{slovo_pre}e,{slovo_pre}a,{slovo_pre}u,{slovo_pre}e,{slovo_pre}e,{slovo_pre}em,{slovo_pre}u,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}ima")
                        # Kratak Siže
                        decl2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}e,{slovo_pre}a,{slovo_pre}u,{slovo_pre}e,{slovo_pre}e,{slovo_pre}om,{slovo_pre}u,{slovo_pre}i,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}e,{slovo_pre}i,{slovo_pre}ima,{slovo_pre}ima")
                        decl_p2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}e,{slovo_pre}a,{slovo_pre}u,{slovo_pre}e,{slovo_pre}e,{slovo_pre}om,{slovo_pre}u,{slovo_pre}i,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}e,{slovo_pre}i,{slovo_pre}ima,{slovo_pre}ima")
                        if slovo_pre == "č":
                            # Dobro parče
                            decl3 = decl
                            decl_p3 = decl_p
                            decl = self._join_pref_base_suff("", base_str, f"{slovo_pre}e,{slovo_pre}eta,{slovo_pre}etu,{slovo_pre}e,{slovo_pre}e,{slovo_pre}etom,{slovo_pre}etu,{slovo_pre}ad,{slovo_pre}adi,{slovo_pre}adima,{slovo_pre}ad,{slovo_pre}adi,{slovo_pre}adima,{slovo_pre}adima")
                            # Lonče plavo
                            decl_p = self._join_pref_base_suff("", base_str, f"{slovo_pre}e,{slovo_pre}eta,{slovo_pre}etu,{slovo_pre}e,{slovo_pre}e,{slovo_pre}etom,{slovo_pre}etu,{slovo_pre}ad,{slovo_pre}adi,{slovo_pre}adima,{slovo_pre}ad,{slovo_pre}adi,{slovo_pre}adima,{slovo_pre}adima")
                        self.variant_show(
                            opt1 = "Siže - Sižea;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                            opt2 = "Parče - Parčeta;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()]),
                            opt3 = "Pantalone - Pantalonama;" + ",".join([base_str + x.strip() for x in suff_mnozina.split("\n") if x.strip()])
                        )

            elif base_str[-2:] in ["ci"]:
                # ganci - ganac
                base_str = base_str[:-2]
                suff = self._make_suffs("ac,ca,cu,če,com,cem,ci,aca,cima,ce")
                decl = self._join_pref_base_suff("", base_str, "ci,cija,ciju,cija,ci,cijem,ciju,ciji,cija,cijima,cije,ciji,cijima,cijima")
                decl_p = self._join_pref_base_suff("", base_str, "ci,cija,ciju,cija,ci,cijem,ciju,ciji,cija,cijima,cije,ciji,cijima,cijima")
            elif base_str[-1] in self.SAMOGLASNICI:
                # Obicna imenica - SAMOGLASNIK koji nije "a" ili "e" na kraju
                samoglasnik = base_str[-1].lower()
                base_str = base_str[:-1]
                slovo_pre = base_str[-1].lower()
                if base_str[-2:].lower() == "nj":
                    # Ako zavrsava na "nje"  potonji-potonjeg
                    suff = self._make_suffs(f"{samoglasnik},eg,em,im,ih,e,ima")
                    # Potonji kandidat
                    decl = self._join_pref_base_suff("", base_str, f"{samoglasnik},eg,em,eg,{samoglasnik},{samoglasnik}m,em,{samoglasnik},{samoglasnik}h,{samoglasnik}m,e,{samoglasnik},{samoglasnik}m,{samoglasnik}m")
                    decl_p = self._join_pref_base_suff("", base_str, f"{samoglasnik},eg,em,eg,{samoglasnik},{samoglasnik}m,em,{samoglasnik},{samoglasnik}h,{samoglasnik}m,e,{samoglasnik},{samoglasnik}m,{samoglasnik}m")
                else:
                    if samoglasnik == "i":
                        # grogi - grogija
                        # studeni - studenog
                        suff = self._make_suffs(f"i,ija,iju,ijem,iju,iji,ijima,ije")
                        suff2 = self._make_suffs(f"i,og,om,im,ih,ima,e")
                        decl = self._join_pref_base_suff("", base_str, f"i,eg,em,eg,i,im,em,i,ih,im,e,i,im,im")
                        decl_p = self._join_pref_base_suff("", base_str, f"i,eg,em,eg,i,im,em,i,ih,im,e,i,im,im")
                        decl2 = self._join_pref_base_suff("", base_str, f"i,og,om,i,i,im,om,i,ih,im,e,i,im,im")
                        decl_p2 = self._join_pref_base_suff("", base_str, f"i,og,om,i,i,im,om,i,ih,im,e,i,im,im")
                        if slovo_pre == "n":
                            # pakosni-pakosnog
                            decl = self._join_pref_base_suff("", base_str[:-1], f"ni,nog,nom,ni,ni,nim,nom,ni,nih,nim,ne,ni,nim,nim")
                            decl_p = self._join_pref_base_suff("", base_str[:-1], f"ni,nog,nom,ni,ni,nim,nom,ni,nih,nim,ne,ni,nim,nim")
                        elif slovo_pre == "v":
                            # šaljivi-šaljivog
                            decl = self._join_pref_base_suff("", base_str[:-1], f"v,vog,vom,vog,vi,vim,vom,vi,vih,vim,ve,vi,vim,vim")
                            decl_p = self._join_pref_base_suff("", base_str[:-1], f"v,vog,vom,vog,vi,vim,vom,vi,vih,vim,ve,vi,vim,vim")
                        elif base_str[-2:].lower() in ["sk", "šk", "čk"]:
                            # Lužički jezik - VIDIM Lužički jezik
                            decl = self._join_pref_base_suff("", base_str, f"i,og,om,i,i,im,om,i,ih,im,e,i,im,im")
                            decl_p = self._join_pref_base_suff("", base_str, f"i,og,om,i,i,im,om,i,ih,im,e,i,im,im")
                            # Lužički Srbin - VIDIM Lužičkog Srbina
                            decl2 = self._join_pref_base_suff("", base_str, f"i,og,om,og,i,im,om,i,ih,im,e,i,im,im")
                            decl_p2 = self._join_pref_base_suff("", base_str, f"i,og,om,og,i,im,om,i,ih,im,e,i,im,im")
                        elif base_str[-1:].lower() == "k":
                            decl2 = self._join_pref_base_suff("", base_str, f"i,og,om,i,i,im,om,i,ih,im,e,i,im,im")
                            decl_p2 = self._join_pref_base_suff("", base_str, f"i,og,om,i,i,im,om,i,ih,im,e,i,im,im")
                        elif base_str[-1:].lower() == "l":
                            # nas mali
                            decl = self._join_pref_base_suff("", base_str, f"i,og,om,og,i,im,om,i,ih,im,e,i,im,im")
                            # mali svet
                            decl_p = self._join_pref_base_suff("", base_str, f"i,og,om,og,i,im,om,i,ih,im,e,i,im,im")

                        self.variant_show(
                            opt1 = "Grogi - Grogija;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                            opt2 = "Studeni - Studenog;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                        )
                    elif samoglasnik == "o":
                        if slovo_pre == "a":
                            # Ugao - Ugla
                            base_str = base_str[:-1]
                            suff = self._make_suffs(f"ao,la,lu,le,lom,lovi,lova,lovima,love")
                            # Ugao merenja
                            decl = self._join_pref_base_suff("", base_str, f"ao,la,lu,ao,le,lom,lu,lovi,lova,lovima,love,lovi,lovima,lovima")
                            # Merni Ugao
                            decl_p = self._join_pref_base_suff("", base_str, f"ao,la,lu,ao,le,lom,lu,lovi,lova,lovima,love,lovi,lovima,lovima")
                        elif slovo_pre == "e":
                            # Predeo - Predela
                            # Deo - Dela
                            # Video - Videa
                            suff = self._make_suffs(f"{samoglasnik},la,lu,lom,li,lima,le")
                            suff2 = self._make_suffs(f"{samoglasnik},la,lu,lom,lovi,lova,lovima,love")
                            suff3 = self._make_suffs(f"{samoglasnik},a,u,om,l,ima,e")
                            # Predeo Srbije - Predeli Srbije
                            decl = self._join_pref_base_suff("", base_str, f"{samoglasnik},la,lu,{samoglasnik},{samoglasnik},lom,lu,li,la,lima,le,li,lima,lima")
                            decl_p = self._join_pref_base_suff("", base_str, f"{samoglasnik},la,lu,{samoglasnik},{samoglasnik},lom,lu,li,la,lima,le,li,lima,lima")
                            # Deo motora - Delovi motora
                            decl2 = self._join_pref_base_suff("", base_str, f"{samoglasnik},la,lu,{samoglasnik},{samoglasnik},lom,lu,lovi,lova,lovima,love,lovi,lovima,lovima")
                            decl_p2 = self._join_pref_base_suff("", base_str, f"{samoglasnik},la,lu,{samoglasnik},{samoglasnik},lom,lu,lovi,lova,lovima,love,lovi,lovima,lovima")
                            # Video
                            decl3 = self._join_pref_base_suff("", base_str, f"{samoglasnik},a,u,{samoglasnik},{samoglasnik},om,u,i,a,ima,e,i,ima,ima")
                            decl_p3 = self._join_pref_base_suff("", base_str, f"{samoglasnik},a,u,{samoglasnik},{samoglasnik},om,u,i,a,ima,e,i,ima,ima")
                            self.variant_show(
                                opt1 = "Predeo-Predela;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                                opt2 = "Deo-Dela;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()]),
                                opt3 = "Video-Videa;" + ",".join([base_str + x.strip() for x in suff3.split("\n") if x.strip()])
                            )
                        else:
                            # božanstvo-božanstva-božanstava
                            # Sečivo-Sečiva-Sečiva
                            base_str = base_str[:-1]
                            suff = self._make_suffs(f"{slovo_pre}o,{slovo_pre}a,{slovo_pre}u,{slovo_pre}om,a{slovo_pre}a,{slovo_pre}ima")
                            suff2 = self._make_suffs(f"{slovo_pre}o,{slovo_pre}a,{slovo_pre}u,{slovo_pre}om,{slovo_pre}ima")
                            if base_str[-1].lower() + slovo_pre == "tv":
                                # Bozanstvo
                                decl = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}a,{slovo_pre}u,{slovo_pre}o,{slovo_pre}o,{slovo_pre}om,{slovo_pre}u,{slovo_pre}a,a{slovo_pre}a,{slovo_pre}ima,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}ima")
                                decl_p = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}a,{slovo_pre}u,{slovo_pre}o,{slovo_pre}o,{slovo_pre}om,{slovo_pre}u,{slovo_pre}a,a{slovo_pre}a,{slovo_pre}ima,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}ima")
                                decl2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}og,{slovo_pre}om,{slovo_pre}o,{slovo_pre}o,{slovo_pre}im,{slovo_pre}om,{slovo_pre}a,{slovo_pre}ih,{slovo_pre}im,{slovo_pre}a,{slovo_pre}a,{slovo_pre}im,{slovo_pre}im")
                                decl_p2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}og,{slovo_pre}om,{slovo_pre}o,{slovo_pre}o,{slovo_pre}im,{slovo_pre}om,{slovo_pre}a,{slovo_pre}ih,{slovo_pre}im,{slovo_pre}a,{slovo_pre}a,{slovo_pre}im,{slovo_pre}im")
                            else:
                                # Agregatno - Agregatna
                                decl = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}og,{slovo_pre}om,{slovo_pre}o,{slovo_pre}o,{slovo_pre}im,{slovo_pre}om,{slovo_pre}a,{slovo_pre}ih,{slovo_pre}im,{slovo_pre}a,{slovo_pre}a,{slovo_pre}im,{slovo_pre}im")
                                decl_p = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}og,{slovo_pre}om,{slovo_pre}o,{slovo_pre}o,{slovo_pre}im,{slovo_pre}om,{slovo_pre}a,{slovo_pre}ih,{slovo_pre}im,{slovo_pre}a,{slovo_pre}a,{slovo_pre}im,{slovo_pre}im")
                                decl2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}a,{slovo_pre}u,{slovo_pre}o,{slovo_pre}o,{slovo_pre}om,{slovo_pre}u,{slovo_pre}a,a{slovo_pre}a,{slovo_pre}ima,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}ima")
                                decl_p2 = self._join_pref_base_suff("", base_str, f"{slovo_pre}o,{slovo_pre}a,{slovo_pre}u,{slovo_pre}o,{slovo_pre}o,{slovo_pre}om,{slovo_pre}u,{slovo_pre}a,a{slovo_pre}a,{slovo_pre}ima,{slovo_pre}a,{slovo_pre}a,{slovo_pre}ima,{slovo_pre}ima")
                            self.variant_show(
                                opt1 = "Božanstvo-...-Božanstava;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                                opt2 = "Sečivo-...-Sečiva;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                            )
                    else:
                        # Baku - Bakua (Kao glavni grad Azerbejdzana)
                        suff = self._make_suffs(f"{samoglasnik},{samoglasnik}a,{samoglasnik}u,{samoglasnik}om,{samoglasnik}i,{samoglasnik}ima, {samoglasnik}e")
                        decl = self._join_pref_base_suff("", base_str, f"{samoglasnik},{samoglasnik}a,{samoglasnik}u,{samoglasnik},{samoglasnik},{samoglasnik}om,{samoglasnik}u,{samoglasnik}i,{samoglasnik}a,{samoglasnik}ima,{samoglasnik}e,{samoglasnik}i,{samoglasnik}ima,{samoglasnik}ima")
                        decl_p = self._join_pref_base_suff("", base_str, f"{samoglasnik},{samoglasnik}a,{samoglasnik}u,{samoglasnik},{samoglasnik},{samoglasnik}om,{samoglasnik}u,{samoglasnik}i,{samoglasnik}a,{samoglasnik}ima,{samoglasnik}e,{samoglasnik}i,{samoglasnik}ima,{samoglasnik}ima")
                        decl2 = self._join_pref_base_suff("", base_str, f"{samoglasnik},{samoglasnik}a,{samoglasnik}u,{samoglasnik},{samoglasnik},{samoglasnik}om,{samoglasnik}u,{samoglasnik}ovi,{samoglasnik}ova,{samoglasnik}ovima,{samoglasnik}ove,{samoglasnik}ovi,{samoglasnik}ovima,{samoglasnik}ovima")
                        decl_p2 = self._join_pref_base_suff("", base_str, f"{samoglasnik},{samoglasnik}a,{samoglasnik}u,{samoglasnik},{samoglasnik},{samoglasnik}om,{samoglasnik}u,{samoglasnik}ovi,{samoglasnik}ova,{samoglasnik}ovima,{samoglasnik}ove,{samoglasnik}ovi,{samoglasnik}ovima,{samoglasnik}ovima")
            else:
                # Obicna imenica - SUGLASNIK na kraju
                if base_str[-2:].lower() == "ac":
                    # Ako zavrsava na "ac"
                    # suff = kukac - kukca
                    # suff2 = poverilac - poverioca
                    # suff3 = Poljubac - Poljupca
                    base_str = base_str[:-2]
                    slovo_pre = base_str[-1]
                    suff = self._make_suffs("ac, ca, cu, če, com, cem, ci, aca, cima, ce")
                    # Crni kukac - crnog kukca
                    decl = self._join_pref_base_suff("", base_str, "ac,ca,cu,ca,če,cem,cu,ci,aca,cima,ce,ci,cima,cima")
                    decl_p = self._join_pref_base_suff("", base_str, "ac,ca,cu,ca,če,cem,cu,ci,aca,cima,ce,ci,cima,cima")
                    suff2 = self._make_suffs(f"{slovo_pre}ac, oca, ocu, oče, ocom, ocem, oci, {slovo_pre}aca, ocima, oce")
                    # moj poverilac - moga poverioca
                    decl2 = self._join_pref_base_suff("", base_str[:-1], f"{slovo_pre}ac,oca,ocu,oca,oče,ocem,ocu,oci,{slovo_pre}aca,ocima,oce,oci,ocima,ocima")
                    decl_p2 = self._join_pref_base_suff("", base_str[:-1], f"{slovo_pre}ac,oca,ocu,oca,oče,ocem,ocu,oci,{slovo_pre}aca,ocima,oce,oci,ocima,ocima")
                    if base_str[-1].lower() in "bmp":
                        # Ako ispred "ac" ima "b", "m" ili "p"
                        suff += self._make_suffs("LJE, LJA, LJU, LJIMA")
                    
                    if base_str[-1].lower() == "b":
                        # suff3 = Poljubac - Poljupca
                        suff3 = self._make_suffs(f"{slovo_pre}ac, pca, pcu, pče, pcom, pcem, pci, {slovo_pre}aca, pcima, pce")
                        decl3 = self._join_pref_base_suff("", base_str[:-1], f"{slovo_pre}ac,pca,pcu,{slovo_pre}ac,pče,pcem,pcu,pci,{slovo_pre}aca,pcima,pce,pci,pcima,pcima")
                        decl_p3 = self._join_pref_base_suff("", base_str[:-1], f"{slovo_pre}ac,pca,pcu,{slovo_pre}ac,pče,pcem,pcu,pci,{slovo_pre}aca,pcima,pce,pci,pcima,pcima")
                        self.variant_show(
                            opt1 = "Kukac-Kukca;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                            opt2 = "Poverilac-Poverioca;" + ",".join([base_str[:-1] + x.strip() for x in suff2.split("\n") if x.strip()]),
                            opt3 = "Poljubac-Poljupca;" + ",".join([base_str[:-1] + x.strip() for x in suff3.split("\n") if x.strip()])
                        )
                    else:
                        self.variant_show(
                            opt1 = "Kukac-Kukca;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                            opt2 = "Poverilac-Poverioca;" + ",".join([base_str[:-1] + x.strip() for x in suff2.split("\n") if x.strip()])
                        )
                    
                elif base_str[-2:].lower() == "oc":
                    # Rukovodioc - rukovodilac
                    base_str = base_str[:-2]
                    suff = self._make_suffs("lac, oc, oca, ocu, oče, ocom, ocem, oci, laca, ocima, oce")
                    decl = self._join_pref_base_suff("", base_str, "oc,oca,ocu,oca,oče,ocem,ocu,oci,oca,ocima,oce,oci,ocima,ocima")
                    decl_p = self._join_pref_base_suff("", base_str, "oc,oca,ocu,oca,oče,ocem,ocu,oci,oca,ocima,oce,oci,ocima,ocima")

                elif base_str[-2:].lower() == "ar":
                    # Kalibar - Kalibra
                    # Putar - Putara
                    base_str = base_str[:-2]
                    suff = self._make_suffs("ar, ra, ru, re, rom, ri, ara, rima")
                    suff2 = self._make_suffs("ar, ara, aru, are, arom, ari, arima")
                    # Moj kalibar - mog kalibra
                    decl = self._join_pref_base_suff("", base_str, "ar,ra,ru,ar,re,rom,ru,ri,ara,rima,re,ri,rima,rima")
                    decl_p = self._join_pref_base_suff("", base_str, "ar,ra,ru,ar,re,rom,ru,ri,ara,rima,re,ri,rima,rima")
                    # srpski putar - srpskog putara
                    decl2 = self._join_pref_base_suff("", base_str, "ar,ara,aru,ara,are,arom,aru,ari,ara,arima,are,ari,arima,arima")
                    decl_p2 = self._join_pref_base_suff("", base_str, "ar,ara,aru,ara,are,arom,aru,ari,ara,arima,are,ari,arima,arima")
                    self.variant_show(
                        opt1 = "Kalibar-Kalibra;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Putar-Putara;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                    )

                elif base_str[-2:].lower() in ["ak", "ik", "ek"] and len(base_str) >= 3:
                    # Ako zavrsava na "ak"
                    # suff = bedak - bedaka
                    # suff2 = zamak - zamka
                    # Suff3 - Uzorak - Uzorci
                    # Sa ik je primer "Jezik"
                    # Sa ek je primer "Odsek"

                    slovo_s = base_str[-3:-2].lower()
                    slovo_s_changed = slovo_s
                    if slovo_s == "s":
                        slovo_s_changed = "š"
                    prvo_slovo = base_str[-2:-1].lower()
                    base_str = base_str[:-3]
                    suff = self._make_suffs(f"{slovo_s}{prvo_slovo}k, {slovo_s}{prvo_slovo}ka, {slovo_s}{prvo_slovo}ku, {slovo_s}{prvo_slovo}če, {slovo_s}{prvo_slovo}kom, {slovo_s}{prvo_slovo}kovi, {slovo_s}{prvo_slovo}kova, {slovo_s}{prvo_slovo}kovima, {slovo_s}{prvo_slovo}kove, {slovo_s}{prvo_slovo}ci, {slovo_s}{prvo_slovo}cima, {slovo_s}{prvo_slovo}ke")
                    # srpski bedak
                    decl = self._join_pref_base_suff("", base_str + slovo_s + prvo_slovo, "k,ka,ku,k,če,kom,ku,ci,ka,cima,ke,ci,cima,cima")
                    decl_p = self._join_pref_base_suff("", base_str + slovo_s + prvo_slovo, "k,ka,ku,k,če,kom,ku,ci,ka,cima,ke,ci,cima,cima")
                    suff2 = self._make_suffs(f"{slovo_s}{prvo_slovo}k, {slovo_s}ka, {slovo_s}ku, {slovo_s_changed}če, {slovo_s}kom, {slovo_s}kovi, {slovo_s}kova, {slovo_s}kovima, {slovo_s}kove, {slovo_s}ci, {slovo_s}cima, {slovo_s}ke")
                    # srpski zamak
                    decl2 = self._join_pref_base_suff("", base_str, f"{slovo_s}{prvo_slovo}k,{slovo_s}ka,{slovo_s}ku,{slovo_s}{prvo_slovo}k,{slovo_s_changed}če,{slovo_s}kom,{slovo_s}ku,{slovo_s}kovi,{slovo_s}kova,{slovo_s}kovima,{slovo_s}kove,{slovo_s}kovi,{slovo_s}kovima,{slovo_s}kovima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"{slovo_s}{prvo_slovo}k,{slovo_s}ka,{slovo_s}ku,{slovo_s}{prvo_slovo}k,{slovo_s_changed}če,{slovo_s}kom,{slovo_s}ku,{slovo_s}kovi,{slovo_s}kova,{slovo_s}kovima,{slovo_s}kove,{slovo_s}kovi,{slovo_s}kovima,{slovo_s}kovima")
                    suff3 = self._make_suffs(f"{slovo_s}{prvo_slovo}k, {slovo_s}ka, {slovo_s}ku, {slovo_s_changed}če, {slovo_s}kom, {slovo_s}ci, {slovo_s}{prvo_slovo}ka, {slovo_s}cima, {slovo_s}ke")
                    if prvo_slovo == "e":
                        # Prek - Prekog
                        decl3 = self._join_pref_base_suff("", base_str + slovo_s + prvo_slovo, f"k,kog,kom,kog,i,kim,kom,ki,kih,kim,ke,ki,kim,kim")
                        decl_p3 = self._join_pref_base_suff("", base_str + slovo_s + prvo_slovo, f"k,kog,kom,kog,i,kim,kom,ki,kih,kim,ke,ki,kim,kim")
                    else:
                        # srpski uzorak
                        decl3 = self._join_pref_base_suff("", base_str, f"{slovo_s}{prvo_slovo}k,{slovo_s}ka,{slovo_s}ku,{slovo_s}{prvo_slovo}k,{slovo_s_changed}če,{slovo_s}kom,{slovo_s}ku,{slovo_s}ci,{slovo_s}{prvo_slovo}ka,{slovo_s}cima,{slovo_s}ke,{slovo_s}ci,{slovo_s}cima,{slovo_s}cima")
                        decl_p3 = self._join_pref_base_suff("", base_str, f"{slovo_s}{prvo_slovo}k,{slovo_s}ka,{slovo_s}ku,{slovo_s}{prvo_slovo}k,{slovo_s_changed}če,{slovo_s}kom,{slovo_s}ku,{slovo_s}ci,{slovo_s}{prvo_slovo}ka,{slovo_s}cima,{slovo_s}ke,{slovo_s}ci,{slovo_s}cima,{slovo_s}cima")
                    # if slovo_s in "bmp":
                    #     # Ako ispred "ak" ima "b", "m" ili "p"
                    #     suff += self._make_suffs(f"{slovo_s}lje, {slovo_s}lja, {slovo_s}lju, {slovo_s}ljima")
                    self.variant_show(
                        opt1 = "Bedak-Bedaka;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Zamak-Zamka-Zamku;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()]),
                        opt3 = "Uzorak-Uzorci;" + ",".join([base_str + x.strip() for x in suff3.split("\n") if x.strip()])
                    )
                    
                elif base_str[-2:].lower() in ["ok"]:
                    # Visok - Visokog
                    # Prek - Prekog
                    # Blok - Bloka

                    prvo_slovo = base_str[-2:-1].lower()
                    base_str = base_str[:-2]
                    suff = self._make_suffs(f"{prvo_slovo}k, {prvo_slovo}kog, {prvo_slovo}kom, {prvo_slovo}ki, {prvo_slovo}kim, {prvo_slovo}ke")
                    suff2 = self._make_suffs(f"{prvo_slovo}k, {prvo_slovo}ka, {prvo_slovo}ku, {prvo_slovo}če, {prvo_slovo}kom, {prvo_slovo}kovi, {prvo_slovo}kova, {prvo_slovo}kovima, {prvo_slovo}kove, {prvo_slovo}kovi")
                    decl = self._join_pref_base_suff("", base_str + prvo_slovo, "k,kog,kom,ki,ki,kim,kom,ki,kih,kim,ke,ki,kim,kim")
                    decl_p = self._join_pref_base_suff("", base_str + prvo_slovo, "k,kog,kom,ki,ki,kim,kom,ki,kih,kim,ke,ki,kim,kim")
                    decl2 = self._join_pref_base_suff("", base_str + prvo_slovo, "k,ka,ku,k,če,kom,ku,kovi,kova,kovima,kove,kovi,kovima,kovima")
                    decl_p2 = self._join_pref_base_suff("", base_str + prvo_slovo, "k,ka,ku,k,če,kom,ku,kovi,kova,kovima,kove,kovi,kovima,kovima")
                    self.variant_show(
                        opt1 = "Visok - Visokog;" + ",".join([base_str + x for x in suff.split("\n") if x.strip()]),
                        opt2 = "Blok - Bloka;" + ",".join([base_str + x for x in suff2.split("\n") if x.strip()])
                    )

                elif base_str[-2:].lower() == "at":
                    # plagijat-plagijata
                    # fragmenat-fragmenta
                    base_str = base_str[:-2]
                    suff = self._make_suffs("at,ata,atu,ate,atom,ati,atima")
                    suff2 = self._make_suffs("t,at,ta,tu,te,tom,ti,ata,tima")
                    # dobar plagijat
                    decl = self._join_pref_base_suff("", base_str, "at,ata,atu,at,ate,atom,atu,ati,ata,atima,ate,ati,atima,atima")
                    decl_p = self._join_pref_base_suff("", base_str, "at,ata,atu,at,ate,atom,atu,ati,ata,atima,ate,ati,atima,atima")
                    # dobar fragmenat
                    decl2 = self._join_pref_base_suff("", base_str, "at,ta,tu,at,te,tom,tu,ti,ata,tima,te,ti,tima,tima")
                    decl_p2 = self._join_pref_base_suff("", base_str, "at,ta,tu,at,te,tom,tu,ti,ata,tima,te,ti,tima,tima")
                    if base_str[-1].lower() in "bmp":
                        # Ako ispred "at" ima "b", "m" ili "p"
                        suff += self._make_suffs("lje, lja, lju, ljima")
                    self.variant_show(
                        opt1 = "Plagijat-Plagijata;" + ",".join([base_str + x for x in suff.split("\n") if x.strip()]),
                        opt2 = "Fragmenat-Fragmenta;" + ",".join([base_str + x for x in suff2.split("\n") if x.strip()])
                    )

                elif base_str[-2:].lower() in ["nj", "št"]:
                    # Ako zavrsava na "nj"
                    # Ako zavrsava na "št"  rušt-rušta
                    nastavak = base_str[-2:].lower()
                    base_str = base_str[:-2]
                    suff = self._make_suffs(f"{nastavak}, {nastavak}a, {nastavak}u, {nastavak}e, {nastavak}om, {nastavak}em, {nastavak}evi, {nastavak}eva, {nastavak}evima, {nastavak}eve")
                    decl = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}a,{nastavak}u,{nastavak},{nastavak}e,{nastavak}em,{nastavak}u,{nastavak}evi,{nastavak}eva,{nastavak}evima,{nastavak}eve,{nastavak}evi,{nastavak}evima,{nastavak}evima")
                    decl_p = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}a,{nastavak}u,{nastavak},{nastavak}e,{nastavak}em,{nastavak}u,{nastavak}evi,{nastavak}eva,{nastavak}evima,{nastavak}eve,{nastavak}evi,{nastavak}evima,{nastavak}evima")
                    if base_str[-1].lower() in "bmp":
                        # Ako ispred "at" ima "b", "m" ili "p"
                        suff += self._make_suffs("lje, lja, lju, ljima")
                elif base_str[-2:].lower() == "in":
                    # Srbin - Srbi
                    # Mlin - Mlinovi
                    base_str = base_str[:-2]
                    suff = self._make_suffs("in, ina, inu, ine, inom, i, a, ima, e")
                    decl = self._join_pref_base_suff("", base_str, "in,ina,inu,ina,ine,inom,inu,i,a,ima,e,i,ima,ima")
                    decl_p = self._join_pref_base_suff("", base_str, "in,ina,inu,ina,ine,inom,inu,i,a,ima,e,i,ima,ima")
                    suff2 = self._make_suffs("in, ina, inu, ine, inom, inovi, inova, inovima, inove")
                    decl2 = self._join_pref_base_suff("", base_str, "in,ina,inu,in,ine,inom,inu,inovi,inova,inovima,inove,inovi,inovima,inovima")
                    decl_p2 = self._join_pref_base_suff("", base_str, "in,ina,inu,in,ine,inom,inu,inovi,inova,inovima,inove,inovi,inovima,inovima")
                    self.variant_show(
                        opt1 = "Srbin-Srbi;" + ",".join([base_str + x for x in suff.split("\n") if x.strip()]),
                        opt2 = "Mlin-Mlinovi;" + ",".join([base_str + x for x in suff2.split("\n") if x.strip()])
                    )
                elif base_str[-1:].lower() in ["n"]:
                    # Ako zavrsava na "n"  - tron, dron
                    # Šljivin - Šljivinog
                    # Tjedan - Tjedni
                    nastavak = base_str[-1:].lower()
                    base_str = base_str[:-1]
                    slovo_pre = base_str[-1].lower()
                    suff = self._make_suffs(f"{nastavak}, {nastavak}a, {nastavak}u, {nastavak}e, {nastavak}om, {nastavak}ovi, {nastavak}ova, {nastavak}ovima, {nastavak}ove")
                    # šljivin
                    decl = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}og,{nastavak}om,{nastavak},{nastavak},{nastavak}im,{nastavak}om,{nastavak}i,{nastavak}ih,{nastavak}im,{nastavak}e,{nastavak}i,{nastavak}im,{nastavak}im")
                    decl_p = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}og,{nastavak}om,{nastavak},{nastavak},{nastavak}im,{nastavak}om,{nastavak}i,{nastavak}ih,{nastavak}im,{nastavak}e,{nastavak}i,{nastavak}im,{nastavak}im")
                    # Tron
                    decl2 = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}a,{nastavak}u,{nastavak},{nastavak}e,{nastavak}om,{nastavak}u,{nastavak}ovi,{nastavak}ova,{nastavak}ovima,{nastavak}ove,{nastavak}ovi,{nastavak}ovima,{nastavak}ovima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}a,{nastavak}u,{nastavak},{nastavak}e,{nastavak}om,{nastavak}u,{nastavak}ovi,{nastavak}ova,{nastavak}ovima,{nastavak}ove,{nastavak}ovi,{nastavak}ovima,{nastavak}ovima")
                    # Tjedan
                    decl3 = self._join_pref_base_suff("", base_str[:-1], f"{slovo_pre}{nastavak},{nastavak}a,{nastavak}u,{slovo_pre}{nastavak},{nastavak}e,{nastavak}om,{nastavak}u,{nastavak}i,a{nastavak}a,{nastavak}ima,{nastavak}e,{nastavak}i,{nastavak}ima,{nastavak}ima")
                    decl_p3 = self._join_pref_base_suff("", base_str[:-1], f"{slovo_pre}{nastavak},{nastavak}a,{nastavak}u,{slovo_pre}{nastavak},{nastavak}e,{nastavak}om,{nastavak}u,{nastavak}i,a{nastavak}a,{nastavak}ima,{nastavak}e,{nastavak}i,{nastavak}ima,{nastavak}ima")
                    self.variant_show(
                        opt1 = "Bez -ovi, -ovima;" + ",".join([base_str + x for x in f"{nastavak},{nastavak}a,{nastavak}u,{nastavak}om,{nastavak}i,{nastavak}ima,{nastavak}e".split(",")]),
                        opt2 = "Bez -ovi - gubi se a;" + ",".join([base_str[:-1] + x for x in f"{slovo_pre}{nastavak},{nastavak}a,{nastavak}u,{nastavak}e,{nastavak}om,{nastavak}i,a{nastavak}a,{nastavak}ima".split(",")]),
                        opt3 = "Sa -ovi, -ovima;" + ",".join([base_str + x for x in f"{nastavak},{nastavak}a,{nastavak}u,{nastavak}om,{nastavak}ovi,{nastavak}ova,{nastavak}ovima,{nastavak}ove".split(",")])
                    )
                elif base_str[-2:].lower() == "st":
                    # vlast - vlasti
                    # terorist - teroriste
                    # test - testovi
                    nastavak = base_str[-2:].lower()
                    base_str = base_str[:-2]
                    suff = self._make_suffs(f"{nastavak}, {nastavak}i, šću, {nastavak}ima")
                    suff2 = self._make_suffs(f"{nastavak}, {nastavak}a, {nastavak}e, {nastavak}u, {nastavak}o, {nastavak}om, {nastavak}i, {nastavak}ima")
                    suff3 = self._make_suffs(f"{nastavak}, {nastavak}a, {nastavak}u, {nastavak}e, {nastavak}om, {nastavak}ovi, {nastavak}ova, {nastavak}ovima, {nastavak}ove")
                    # Narodna vlast
                    decl = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}i,{nastavak}i,{nastavak},{nastavak}i,šću,{nastavak}i,{nastavak}i,{nastavak}i,{nastavak}ima,{nastavak}i,{nastavak}i,{nastavak}ima,{nastavak}ima")
                    decl_p = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}i,{nastavak}i,{nastavak},{nastavak}i,šću,{nastavak}i,{nastavak}i,{nastavak}i,{nastavak}ima,{nastavak}i,{nastavak}i,{nastavak}ima,{nastavak}ima")
                    # Opasan terorista
                    decl2 = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}e,{nastavak}i,{nastavak}u,{nastavak}o,{nastavak}om,{nastavak}i,{nastavak}i,{nastavak}a,{nastavak}ima,{nastavak}e,{nastavak}i,{nastavak}ima,{nastavak}ima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}e,{nastavak}i,{nastavak}u,{nastavak}o,{nastavak}om,{nastavak}i,{nastavak}i,{nastavak}a,{nastavak}ima,{nastavak}e,{nastavak}i,{nastavak}ima,{nastavak}ima")
                    # Tezak test
                    decl3 = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}a,{nastavak}u,{nastavak},{nastavak}e,{nastavak}om,{nastavak}u,{nastavak}ovi,{nastavak}ova,{nastavak}ovima,{nastavak}ove,{nastavak}ovi,{nastavak}ovima,{nastavak}ovima")
                    decl_p3 = self._join_pref_base_suff("", base_str, f"{nastavak},{nastavak}a,{nastavak}u,{nastavak},{nastavak}e,{nastavak}om,{nastavak}u,{nastavak}ovi,{nastavak}ova,{nastavak}ovima,{nastavak}ove,{nastavak}ovi,{nastavak}ovima,{nastavak}ovima")
                    self.variant_show(
                        opt1 = "Radost - Radošću;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Dvanaest - Dvanaesti;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()]),
                        opt3 = "Test - Testovi;" + ",".join([base_str + x.strip() for x in suff3.split("\n") if x.strip()])
                    )

                elif base_str[-2:].lower() == "am":
                    # arhaizam - arhaizma
                    # pojam - pojmovi
                    # program - programa
                    nastavak = base_str[-2:].lower()
                    base_str = base_str[:-2]
                    suff = self._make_suffs("am,ma,mu,mom,mi,ama,mima,me")
                    suff2 = self._make_suffs("am,ma,mu,me,mom,movi,mova,movima,move")
                    suff3 = self._make_suffs("am,ama,amu,ame,amom,ami,amima")
                    # Stari arhaizam
                    decl = self._join_pref_base_suff("", base_str, f"am,ma,mu,am,me,mom,mu,mi,ama,mima,me,mi,mima,mima")
                    decl_p = self._join_pref_base_suff("", base_str, f"am,ma,mu,am,me,mom,mu,mi,ama,mima,me,mi,mima,mima")
                    # Lep pojam
                    decl2 = self._join_pref_base_suff("", base_str, f"am,ma,mu,am,me,mom,mu,movi,mova,movima,move,movi,movima,movima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"am,ma,mu,am,me,mom,mu,movi,mova,movima,move,movi,movima,movima")
                    # Dosadan program
                    decl3 = self._join_pref_base_suff("", base_str, f"am,ama,amu,am,ame,amom,amu,ami,ama,amima,ame,ami,amima,amima")
                    decl_p3 = self._join_pref_base_suff("", base_str, f"am,ama,amu,am,ame,amom,amu,ami,ama,amima,ame,ami,amima,amima")
                    self.variant_show(
                        opt1 = "Arhaizam - Arhaizma;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Pojam - Pojmova;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()]),
                        opt3 = "Program - Programa;" + ",".join([base_str + x.strip() for x in suff3.split("\n") if x.strip()])
                    )
                elif base_str[-1:].lower() == "v":
                    # carev-carevog
                    nastavak = base_str[-1:].lower()
                    base_str = base_str[:-1]
                    suff = self._make_suffs("v,va,ve,vi,vo,vom,vima")
                    # Carev dvor
                    decl = self._join_pref_base_suff("", base_str, f"v,vog,vom,v,vi,vim,vom,vi,vih,vim,ve,vi,vim,vim")
                    decl_p = self._join_pref_base_suff("", base_str, f"v,vog,vom,v,vi,vim,vom,vi,vih,vim,ve,vi,vim,vim")
                elif base_str[-2:].lower() == "kt":
                    # Trakt - Trakata
                    # kontrakt - kontrakata
                    base_str = base_str[:-2]
                    suff = self._make_suffs("kt,kta,ktu,kte,ktom,ktovi,ktova,ktovima,ktove")
                    suff2 = self._make_suffs("kt,kta,ktu,kte,ktom,kti,kata,ktima")
                    # Probavni trakt
                    decl = self._join_pref_base_suff("", base_str, f"kt,kta,ktu,kt,kte,ktom,ktu,ktovi,ktova,ktovima,ktove,ktovi,ktovima,ktovima")
                    decl_p = self._join_pref_base_suff("", base_str, f"kt,kta,ktu,kt,kte,ktom,ktu,ktovi,ktova,ktovima,ktove,ktovi,ktovima,ktovima")
                    # Vazan kontakt
                    decl2 = self._join_pref_base_suff("", base_str, f"kt,kta,ktu,kt,kte,ktom,ktu,kti,kta,ktima,kte,kti,ktima,ktima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"kt,kta,ktu,kt,kte,ktom,ktu,kti,kta,ktima,kte,kti,ktima,ktima")
                    self.variant_show(
                        opt1 = "Trakt - Trakata;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Kontrakt - Kontrakata;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                    )
                elif base_str[-2:].lower() == "nt":
                    # Element - Elemenata
                    base_str = base_str[:-2]
                    suff = self._make_suffs("nt,nta,ntu,nte,ntom,ntovi,ntova,ntovima,ntove")
                    suff2 = self._make_suffs("nt,nta,ntu,nte,ntom,nti,nata,ntima")
                    decl = self._join_pref_base_suff("", base_str, f"nt,nta,ntu,nt,nte,ntom,ntu,ntovi,ntova,ntovima,ntove,ntovi,ntovima,ntovima")
                    decl_p = self._join_pref_base_suff("", base_str, f"nt,nta,ntu,nt,nte,ntom,ntu,ntovi,ntova,ntovima,ntove,ntovi,ntovima,ntovima")
                    decl2 = self._join_pref_base_suff("", base_str, f"nt,nta,ntu,nt,nte,ntom,ntu,nti,nata,ntima,nte,nti,ntima,ntima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"nt,nta,ntu,nt,nte,ntom,ntu,nti,nata,ntima,nte,nti,ntima,ntima")
                    self.variant_show(
                        opt1 = "Sa ovi;" + ",".join([base_str + x.strip() for x in suff.split("\n") if x.strip()]),
                        opt2 = "Bez ovi;" + ",".join([base_str + x.strip() for x in suff2.split("\n") if x.strip()])
                    )
                else:
                    # Ostali slucajevi  pekmez-pekmeza
                    ll = base_str[-1]
                    base_str = base_str[:-1]
                    suff = self._make_suffs(f"{ll}, {ll}a, {ll}u, {self.palatalizacija(ll)}e, {ll}om")
                    if ll != self.sibilarizacija(ll):
                        suff += self._make_suffs(f"{self.sibilarizacija(ll)}i, {self.sibilarizacija(ll)}ima, {ll}e")
                        decl = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll},{self.palatalizacija(ll)}e,{ll}om,{ll}u,{self.sibilarizacija(ll)}i,{ll}a,{self.sibilarizacija(ll)}ima,{ll}e,{self.sibilarizacija(ll)}i,{self.sibilarizacija(ll)}ima,{self.sibilarizacija(ll)}ima")
                        decl_p = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll},{self.palatalizacija(ll)}e,{ll}om,{ll}u,{self.sibilarizacija(ll)}i,{ll}a,{self.sibilarizacija(ll)}ima,{ll}e,{self.sibilarizacija(ll)}i,{self.sibilarizacija(ll)}ima,{self.sibilarizacija(ll)}ima")
                    else:
                        suff += self._make_suffs(f"{ll}ovi, {ll}ova, {ll}ovima, {ll}ove, {ll}i, {ll}ima")
                        decl = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll},{self.palatalizacija(ll)}e,{ll}om,{ll}u,{ll}ovi,{ll}ova,{ll}ovima,{ll}ove,{ll}ovi,{ll}ovima,{ll}ovima")
                        decl_p = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll},{self.palatalizacija(ll)}e,{ll}om,{ll}u,{ll}ovi,{ll}ova,{ll}ovima,{ll}ove,{ll}ovi,{ll}ovima,{ll}ovima")
                    
                    # Puž - Puževi
                    decl2 = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll}a,{self.palatalizacija(ll)}e,{ll}om,{ll}u,{ll}evi,{ll}eva,{ll}evima,{ll}eve,{ll}evi,{ll}evima,{ll}evima")
                    decl_p2 = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll}a,{self.palatalizacija(ll)}e,{ll}om,{ll}u,{ll}evi,{ll}eva,{ll}evima,{ll}eve,{ll}evi,{ll}evima,{ll}evima")
                    # Golać - Golaći
                    decl3 = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll}a,{self.palatalizacija(ll)}u,{ll}om,{ll}u,{ll}i,{ll}a,{ll}ima,{ll}e,{ll}i,{ll}ima,{ll}ima")
                    decl_p3 = self._join_pref_base_suff("", base_str, f"{ll},{ll}a,{ll}u,{ll}a,{self.palatalizacija(ll)}u,{ll}om,{ll}u,{ll}i,{ll}a,{ll}ima,{ll}e,{ll}i,{ll}ima,{ll}ima")

                    if base_str[-1].lower() in "bmp":
                        # Ako zavrsava na "b", "m" ili "p"
                        suff += self._make_suffs("lje, lja, lju, ljima")

                    self.variant_show(
                        opt1 = "Bez -ovi, -ovima;" + ",".join([base_str + x for x in f"{ll},{ll}a,{ll}u,{self.palatalizacija(ll)}e,{ll}om,{self.sibilarizacija(ll)}i,{self.sibilarizacija(ll)}ima,{ll}e".split(",")]),
                        opt2 = "Sa -ovi, -ovima;" + ",".join([base_str + x for x in f"{ll},{ll}a,{ll}u,{self.palatalizacija(ll)}e,{ll}om,{ll}ovi,{ll}ova,{ll}ovima,{ll}ove,{ll}ovima".split(",")]),
                        opt3 = "Sa -evi, -evima;" + ",".join([base_str + x for x in f"{ll},{ll}a,{ll}u,{self.palatalizacija(ll)}e,{ll}om,{ll}evi,{ll}eva,{ll}evima,{ll}eve,{ll}evima".split(",")])
                    )
        
        suff = self._delete_duplicates_from_list(suff.splitlines())

        result = []

        for item in suff:
            result.append(base_str + item)

        decl = [x.strip() for x in decl.splitlines() if x.strip()]
        if decl and len(decl) != 14:
            UTILS.TerminalUtility.WarningMessage("#1: Deklinacija ne sadrži 14 redova. (LEN(#2)=#3)", ["DefinitionEditor", "decl", len(decl)], exception_raised=True)

        decl2 = [x.strip() for x in decl2.splitlines() if x.strip()]
        if decl2 and len(decl2) != 14:
            UTILS.TerminalUtility.WarningMessage("#1: Deklinacija ne sadrži 14 redova. (LEN(#2)=#3)", ["DefinitionEditor", "decl2", len(decl2)], exception_raised=True)

        decl3 = [x.strip() for x in decl3.splitlines() if x.strip()]
        if decl3 and len(decl3) != 14:
            UTILS.TerminalUtility.WarningMessage("#1: Deklinacija ne sadrži 14 redova. (LEN(#2)=#3)", ["DefinitionEditor", "decl3", len(decl3)], exception_raised=True)

        decl_p = [x.strip() for x in decl_p.splitlines() if x.strip()]
        if decl_p and len(decl_p) != 14:
            UTILS.TerminalUtility.WarningMessage("#1: Deklinacija ne sadrži 14 redova. (LEN(#2)=#3)", ["DefinitionEditor", "decl_p", len(decl_p)], exception_raised=True)

        decl_p2 = [x.strip() for x in decl_p2.splitlines() if x.strip()]
        if decl_p2 and len(decl_p2) != 14:
            UTILS.TerminalUtility.WarningMessage("#1: Deklinacija ne sadrži 14 redova. (LEN(#2)=#3)", ["DefinitionEditor", "decl_p2", len(decl_p2)], exception_raised=True)

        decl_p3 = [x.strip() for x in decl_p3.splitlines() if x.strip()]
        if decl_p3 and len(decl_p3) != 14:
            UTILS.TerminalUtility.WarningMessage("#1: Deklinacija ne sadrži 14 redova. (LEN(#2)=#3)", ["DefinitionEditor", "decl_p3", len(decl_p3)], exception_raised=True)

        # Add preff and seff to base string output
        for idx, item in enumerate(result):
            result[idx] = f"{base_str_preff}{item}{base_str_suff}"
        
        for idx, item in enumerate(decl):
            decl[idx] = f"{base_str_preff}{item}{base_str_suff}"
        
        for idx, item in enumerate(decl_p):
            decl_p[idx] = f"{base_str_preff}{item}{base_str_suff}"

        if return_declination:
            if declination_and_adjective_level == 2:
                return decl2
            elif declination_and_adjective_level == 3:
                return decl3
            else:
                return decl
        elif return_adjective:
            if not decl_p:
                decl_p = decl
            if declination_and_adjective_level == 2:
                return decl_p2
            elif declination_and_adjective_level == 3:
                return decl_p3
            else:
                return decl_p
            
        return result

    def vise_reci(self, samo_jednina = False) -> list:
        if samo_jednina:
            broj_padeza = 7
        else:
            broj_padeza = 14

        base_str = self.txt_base.text()
        base_str_cur_pos = self.txt_base.cursorPosition()
        if len(base_str) < 3:
            return []
        
        auto_show_switch = self.chk_auto_show.isChecked()
        self.chk_auto_show.setChecked(False)

        words = [x.strip() for x in base_str.split(" ") if x.strip()]

        expression_decl = {}

        # Make expression_decl 
        for word_idx, word in enumerate(words):
            self.txt_base.setText(word)

            expression_decl[str(word_idx)] = []
            expression_decl[str(word_idx)].append(
            {
                "name": "FIX",
                "data": [word for _ in range(broj_padeza)]
            })

            if self._imenica(return_declination=True, declination_and_adjective_level=1):
                expression_decl[str(word_idx)].append(
                {
                    "name": "LVL 1",
                    "data": self._imenica(return_declination=True, declination_and_adjective_level=1)
                })

            if self._imenica(return_declination=True, declination_and_adjective_level=2):
                expression_decl[str(word_idx)].append(
                {
                    "name": "LVL 2",
                    "data": self._imenica(return_declination=True, declination_and_adjective_level=2)
                })

            if self._imenica(return_declination=True, declination_and_adjective_level=3):
                expression_decl[str(word_idx)].append(
                {
                    "name": "LVL 3",
                    "data": self._imenica(return_declination=True, declination_and_adjective_level=3)
                })

        word_pool = []
        names = []
        for i in expression_decl["0"]:
            word_pool.append([i["data"]])
            names.append(i["name"] + " ")

        for process_idx in range(1, len(expression_decl)):
            temp = []
            names_tmp = []
            for next_word_dict in expression_decl[str(process_idx)]:
                for name_idx, word_in_pool in enumerate(word_pool):
                    temp.append(word_in_pool + [next_word_dict["data"]])
                    names_tmp.append(names[name_idx] + " - " + next_word_dict["name"] + " ")

            word_pool = temp
            names = names_tmp

        opt = []
        
        for idx, word_list in enumerate(word_pool):
            opt_entry = ""
            for word_idx in range(broj_padeza):
                word_tmp = ""
                for word in word_list:
                    word_tmp += word[word_idx] + " "
                opt_entry += word_tmp.strip() + "\n"
            
            opt_entry = opt_entry.strip()
            opt_entry = ",".join(self._delete_duplicates_from_list([x for x in opt_entry.splitlines() if x.strip()]))

            opt_entry = names[idx].strip(" -") + ";" + opt_entry.strip(",")

            opt.append(opt_entry)

        self.txt_base.setText(base_str)
        self.txt_base.setCursorPosition(base_str_cur_pos)
        self.chk_auto_show.setChecked(auto_show_switch)

        # Sort
        for idx, i in enumerate(names):
            names[idx] = [idx, names[idx]]

        names.sort(key=lambda x: x[1])

        names_result = []
        opt_result = []

        for i in names:
            idx = i[0]
            opt_result.append(opt[idx])
            names_result.append(i[1])


        recomm = None
        for idx, i in enumerate(names_result):
            if i.count("LVL 1") == len(i.split("-")):
                recomm = idx
                break

        self.variant_show(opt1=opt_result, opt2= recomm)

        if recomm:
            return opt_result[recomm][opt_result[recomm].find(";") + 1:].split(",")
        else:
            return opt_result[0][opt_result[0].find(";") + 1:].split(",")

    def _pridev(self, komparacija: bool = False) -> list:
        base_str = self.txt_base.text().strip()
        if len(base_str) < 3:
            return []
        
        suff = ""
        output = ""

        if base_str[-1].lower() in self.SAMOGLASNICI:
            base_str = base_str[:-1]

        if base_str[-2:].lower() in ["an", "ar"]:
            nastavak = base_str[-2:]
            base_str = base_str[:-2]
            suff = self._make_suffs(*[f"{nastavak[-1]}{x}" for x in self.PRIDEV_N])
            suff2 = self._make_suffs(*[f"{nastavak}{x}" for x in self.PRIDEV_N])
            suff += self._make_suffs(f"{nastavak}")
            suff2 += self._make_suffs(f"{nastavak}")
            output = self._join_pref_base_suff("", base_str, suff)
            output2 = self._join_pref_base_suff("", base_str, suff2)

            if komparacija:
                # Komparativ
                komp_suff = nastavak[-1] + "ij"
                komp_suff2 = nastavak + "ij"
                suff += self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ])
                suff2 += self._make_suffs(*[f"{komp_suff2}{x}" for x in self.PRIDEV_IJ])
                output += self._join_pref_base_suff("", base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(*[f"{komp_suff2}{x}" for x in self.PRIDEV_IJ]))
                # Superlativ
                komp_pref = "naj"
                output += self._join_pref_base_suff(komp_pref, base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                output2 += self._join_pref_base_suff(komp_pref, base_str, self._make_suffs(*[f"{komp_suff2}{x}" for x in self.PRIDEV_IJ]))
            
            self.variant_show(
                opt1 = "Unikatan-Unikatni;" + ",".join(output.splitlines()),
                opt2 = "Poderan-Poderani;" + ",".join(output2.splitlines())
            )

        elif base_str[-1:].lower() in ["d"]:
            nastavak = ""
            suff = self._make_suffs(*[x for x in self.PRIDEV_N])
            output = self._join_pref_base_suff("", base_str, suff)
            output += base_str + "\n"
            output2 = self._join_pref_base_suff("", base_str, suff)
            output2 += base_str + "\n"

            if komparacija:
                # Komparativ
                komp_suff = nastavak + "đ"
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))

                komp_suff2 = nastavak + "ij"
                suff += self._make_suffs(*[f"{komp_suff2}{x}" for x in self.PRIDEV_IJ])
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(*[f"{komp_suff2}{x}" for x in self.PRIDEV_IJ]))
                # Superlativ
                komp_pref = "naj"
                output += self._join_pref_base_suff(komp_pref, base_str[:-1], self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                output2 += self._join_pref_base_suff(komp_pref, base_str, self._make_suffs(*[f"{komp_suff2}{x}" for x in self.PRIDEV_IJ]))

                self.variant_show(
                    opt1 = "Promena u Đ;" + ",".join(output.splitlines()),
                    opt2 = "Bez promene u Đ;" + ",".join(output2.splitlines())
                )

        elif base_str[-1:].lower() in ["j"]:
            nastavak = ""
            suff = self._make_suffs(*[x for x in self.PRIDEV_IJ])
            output = self._join_pref_base_suff("", base_str, suff)

            if komparacija:
                # Komparativ
                komp_suff = nastavak + "ij"
                suff += self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ])
                output += self._join_pref_base_suff("", base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                # Superlativ
                komp_pref = "naj"
                output += self._join_pref_base_suff(komp_pref, base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
        else:
            nastavak = base_str[-1]
            base_str = base_str[:-1]
            suff = self._make_suffs(*[f"{nastavak}{x}" for x in self.PRIDEV_N])
            suff2 = self._make_suffs(*[f"{nastavak}{x}" for x in self.PRIDEV_IJ])
            if nastavak.lower() != "k":
                suff += self._make_suffs(f"{nastavak}")
            output = self._join_pref_base_suff("", base_str, suff)
            output2 = self._join_pref_base_suff("", base_str, suff2)

            if komparacija:
                # Komparativ
                komp_suff = nastavak + "ij"
                suff += self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ])
                suff2 += self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ])
                output += self._join_pref_base_suff("", base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                # Superlativ
                komp_pref = "naj"
                output += self._join_pref_base_suff(komp_pref, base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))
                output2 += self._join_pref_base_suff(komp_pref, base_str, self._make_suffs(*[f"{komp_suff}{x}" for x in self.PRIDEV_IJ]))

            self.variant_show(
                opt1 = "Sa (og);" + ",".join(output.splitlines()),
                opt2 = "Sa (eg);" + ",".join(output2.splitlines())
            )

        suff = self._delete_duplicates_from_list(suff.splitlines())

        output = self._delete_duplicates_from_list(output.splitlines())

        return output

    def _join_pref_base_suff(self, pref: str, base: str, suff: str) -> str:
        """Return: String delimited with <b>new line</b> + new line at end"""
        if suff.count(",") != 0 and suff.count("\n") == 0:
            suff = "\n".join([x.strip() for x in suff.split(",") if x.strip()])
        return "\n".join([f"{pref}{base}{x}" for x in suff.splitlines()]) + "\n"

    def _glagol(self):
        base_str = self.txt_base.text().strip()
        if len(base_str) < 3:
            return []

        # Provera da li je glagol validan
        nastavak = ""
        if base_str[-2:].lower() in ["im", "am", "om", "um", "em"]:
            nastavak = base_str[-2:-1].lower()
            base_str = base_str[:-2]
        elif base_str[-3:].lower() in ["iti", "ati", "oti", "uti", "eti"]:
            nastavak = base_str[-3:-2].lower()
            base_str = base_str[:-3]
        elif base_str[-1].lower() in self.SAMOGLASNICI:
            nastavak = base_str[-1].lower()
            base_str = base_str[:-1]
        if not nastavak:
            return []

        suff = ""
        output = ""
        base_str_extra = ""

        if nastavak == "a":
            # Present
            present = "am, aš, a, amo, ate, aju"
            suff = self._make_suffs(present)
            output = self._join_pref_base_suff("", base_str, self._make_suffs(present))
            # Perfekt
            base_str_extra = [base_str, base_str, base_str]
            perfekt = "ao, ati, ala, alo, ali, ale"
            suff += self._make_suffs(perfekt)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
            # Aorist
            aorist = "ah, aše, asmo, aste, ašte, ahu"
            suff += self._make_suffs(aorist)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
            # Futur
            futur = "aću, aćeš, aće, aćemo, aćete"
            suff += self._make_suffs(futur)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
            # Extra
            extra = "ajući,aj,ajte"

            extra_plus = None
            extra_suffs = ["avši","evši","ivši","ovši","uvši","avavši","evavši","ivavši","ovavši","uvavši"]
            if base_str_extra:
                extra_plus = {}
                if base_str_extra[0] and base_str_extra[0][-1] in self.SAMOGLASNICI:
                    base_str_extra[0] = base_str_extra[0][:-1]
                extra_plus["opt1"] = [base_str_extra[0] + x for x in extra_suffs]
                if base_str_extra[1] and base_str_extra[1][-1] in self.SAMOGLASNICI:
                    base_str_extra[1] = base_str_extra[1][:-1]
                extra_plus["opt2"] = [base_str_extra[1] + x for x in extra_suffs]
                if base_str_extra[2] and base_str_extra[2][-1] in self.SAMOGLASNICI:
                    base_str_extra[2] = base_str_extra[2][:-1]
                extra_plus["opt3"] = [base_str_extra[2] + x for x in extra_suffs]

            suff += self._make_suffs(extra)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
            self.variant_show(
                opt1="DEFAULT;" + ",".join(output.splitlines()),
                extra_plus=extra_plus
            )
        elif nastavak == "e":
            imperativ_output1 = ""
            imperativ_output2 = ""
            imperativ_output3 = ""
            # Present
            present = "em, eš, e, emo, ete, u"
            suff = self._make_suffs(present)
            output = self._join_pref_base_suff("", base_str, self._make_suffs(present))
            output_ev = self._join_pref_base_suff("", base_str, self._make_suffs(present)) # Bičujem - Bičevao
            if base_str[-1].lower() in "čžš":
                # Sečem  Seku
                slovo_pre = base_str[-1]
                # Rastačem Rastaču
                # Sečem Seku
                # Podtičem Podstiču
                # Srčem Srču
                # Obučem Obuku
                if len(base_str) > 1:
                    if base_str[-2:-1].lower() in "eu":
                        present = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {self.reverse_palatalizacija(slovo_pre)}u"
                        present2 = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {self.reverse_palatalizacija(slovo_pre)}u"
                        present3 = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {self.reverse_palatalizacija(slovo_pre)}u"
                    else:
                        present = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {slovo_pre}u"
                        present2 = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {slovo_pre}u"
                        present3 = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {slovo_pre}u"
                else:
                    present2 = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {slovo_pre}u"
                    present3 = f"{slovo_pre}em, {slovo_pre}eš, {slovo_pre}e, {slovo_pre}emo, {slovo_pre}ete, {slovo_pre}u"
                output = self._join_pref_base_suff("", base_str[:-1], self._make_suffs(present))
                output2 = self._join_pref_base_suff("", base_str[:-1], self._make_suffs(present2))
                output3 = self._join_pref_base_suff("", base_str[:-1], self._make_suffs(present3))
            else:
                output2 = self._join_pref_base_suff("", base_str, self._make_suffs(present))
                output3 = self._join_pref_base_suff("", base_str, self._make_suffs(present))
            
            # Perfekt
            if base_str[-2:].lower() in ["uj"]:
                # output = socijalizujem - socijalizovao  uj -> ov
                # output2 = okružujem - okruživao  uj -> iv
                base_str_extra = [base_str[:-2], base_str[:-2], base_str[:-2]]
                perfekt = "ao, ati, ala, alo, ali, ale"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-2] + "ov", self._make_suffs(perfekt))
                output_ev += self._join_pref_base_suff("", base_str[:-2] + "ev", self._make_suffs(perfekt))
                output2 += self._join_pref_base_suff("", base_str[:-2] + "iv", self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str},{base_str + 'te'}"
                imperativ_output2 = f"{base_str},{base_str + 'te'}"
                imperativ_output3 = f"{base_str},{base_str + 'te'}"
            elif base_str[-2:].lower() == "ij":
                # dobijam - dobijao - dobivao
                # izlijem - izlio - izlivao
                base_str_extra = [base_str[:-2], base_str[:-2], base_str[:-2]]
                perfekt = "ao, ati, ala, alo, ali, ale"
                perfekt2 = "o, ti, la, lo, li, le"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
                output += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str},{base_str + 'te'}"
                imperativ_output1 += f"{base_str + 'aj'},{base_str + 'ajte'}"
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt2))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(perfekt))
                imperativ_output2 = f"{base_str},{base_str + 'te'}"
                imperativ_output2 += f"{base_str[:-1] + 'vaj'},{base_str[:-1] + 'ajte'}"
            elif base_str[-2:].lower() == "aj":
                # saznajem - saznavao
                # postajem - postajao
                base_str_extra = [base_str, base_str[:-2], base_str[:-2]]
                perfekt = "ao, ati, ala, alo, ali, ale"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str},{base_str + 'te'}"
                output2 += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(perfekt))
                imperativ_output2 = f"{base_str},{base_str + 'te'}"
            elif base_str[-1:].lower() in "šžč":
                # manipulišem - manipulisao  š -> s
                # prikažem - prikazao ž -> z
                # podstičem - podsticao
                # Predlažem - Predlagao
                nastavak1 = self.reverse_sibilarizacija(base_str[-1].lower())
                if len(base_str) > 1:
                    if base_str[-2:-1].lower() in "eu":
                        nastavak1 = self.reverse_palatalizacija(base_str[-1].lower())
                        nastavak2 = self.reverse_sibilarizacija(base_str[-1].lower())
                        base_str_extra = [base_str[:-1] + nastavak1, base_str[:-1] + self.reverse_palatalizacija(base_str[-1]), base_str[:-1] + nastavak2]
                    else:
                        nastavak1 = self.reverse_sibilarizacija(base_str[-1].lower())
                        nastavak2 = self.reverse_palatalizacija(base_str[-1].lower())
                        base_str_extra = [base_str[:-1] + nastavak1, base_str[:-1] + self.reverse_sibilarizacija(base_str[-1]), base_str[:-1] + nastavak2]
                else:
                    nastavak1 = ""
                    nastavak2 = ""
                    base_str_extra = [base_str, base_str, base_str]
                perfekt = "ao, ati, ala, alo, ali, ale"
                slovo_pre = base_str[-1]
                # Sečem - Seko - Sekao - Seći
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output2 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output3 = f"{base_str + 'i'},{base_str + 'ite'}"
                if len(base_str) > 1:
                    if base_str[-2:-1].lower() in "eu":
                        perfekt2 = f"{nastavak1}o,{nastavak1}ao, ći, {nastavak1}la, {nastavak1}lo, {nastavak1}li, {nastavak1}le"
                        perfekt3 = f"{nastavak2}o,{nastavak2}ao, ći, {nastavak2}la, {nastavak2}lo, {nastavak2}li, {nastavak2}le"
                        if base_str[-1:].lower() == "č":
                            imperativ_output3 = f"{base_str[:-1] + 'ci'},{base_str[:-1] + 'cite'}"
                    else:
                        perfekt2 = f"{nastavak1}o,{nastavak1}ao, {nastavak1}ati,{nastavak1}ala, {nastavak1}alo, {nastavak1}ali, {nastavak1}ale"
                        perfekt3 = f"{nastavak2}o,{nastavak2}ao, {nastavak2}ati,{nastavak2}ala, {nastavak2}alo, {nastavak2}ali, {nastavak2}ale"
                else:
                    perfekt2 = perfekt
                    perfekt3 = perfekt
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt2))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt2))
                output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt3))
            elif base_str[-1:].lower() in "ć":
                # Obrćem - Obrtao
                base_str_extra = [base_str[:-1] + "t", base_str[:-1] + "t", base_str[:-1] + "t"]
                perfekt = "ao, ati, ala, alo, ali, ale"
                nastavak1 = "t"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-1] + nastavak1, self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
            elif base_str[-2:].lower() == "nj":
                # razapinjem - razapinjao
                base_str_extra = [base_str, base_str, base_str]
                perfekt = "ao, ati, ala, alo, ali, ale"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
            elif base_str[-1:].lower() == "n" and len(base_str) > 1:
                # Potisnem - Potisno - Potisnuo
                # Postignem - Postigo - Postignuo
                base_str_extra = [base_str, base_str[:-1], base_str]
                perfekt = "o, uo, uti, ula, ulo, uli, ule"
                perfekt2 = "go, gao, ći, gla, glo, gli, gle"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
                output2 += self._join_pref_base_suff("", base_str[:-2], self._make_suffs(perfekt2))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output2 = f"{base_str + 'i'},{base_str + 'ite'},{base_str[:-2] + 'ži'},{base_str[:-2] + 'žite'}"
            elif base_str[-1:].lower() == "s":
                # Donesem - Donesti
                # Donesem - Doneti
                base_str_extra = [base_str, base_str[:-1], base_str]
                perfekt = "o, ti, la, lo, li, le"
                perfekt2 = "o, ti, la, lo, li, le"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt2))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output2 = f"{base_str + 'i'},{base_str + 'ite'}"
            elif base_str[-4:].lower() == "šalj":
                # Šaljem - Slao
                base_str_extra = [base_str[:-4] + "sl", base_str, base_str[:-4] + "sl"]
                perfekt = "o, ti, la, lo, li, le"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-4] + "sla", self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
            elif base_str[-2:].lower() == "lj" and len(base_str) >= 3:
                # Šaljem - Slao  Meljem - Mleo  Koljem - Klao
                # Đeljem - Đeljao
                base_str_extra = [base_str[:-3] + "la", base_str[:-3] + "le", base_str]
                perfekt = "o, ti, la, lo, li, le"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-3] + "la", self._make_suffs(perfekt))
                output2 += self._join_pref_base_suff("", base_str[:-3] + "le", self._make_suffs(perfekt))
                output3 += self._join_pref_base_suff("", base_str + "a", self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output2 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output3 = f"{base_str + 'i'},{base_str + 'ite'}"
            elif base_str[-1:].lower() == "đ":
                # Nadiđem - Nadišao
                base_str_extra = [base_str[:-1] + "š", base_str[:-1] + "š", base_str[:-1] + "š"]
                perfekt = "šo, šao, ći, šla, šlo, šli, šle"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
            elif base_str[-2:].lower() == "ov":
                # Izazovem - Izazvao
                base_str_extra = [base_str[:-2] + "v", base_str[:-2] + "v", base_str[:-2] + "v"]
                perfekt = "o, ao, ala, alo, ali, ale"
                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str[:-2] + "v", self._make_suffs(perfekt))
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
            else:
                imperativ_output1 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output2 = f"{base_str + 'i'},{base_str + 'ite'}"
                imperativ_output3 = f"{base_str + 'i'},{base_str + 'ite'}"
                base_str_extra = [base_str, base_str, base_str]
                # planem - planuo
                perfekt = "uo, uti, ula, ulo, uli, ule"
                # razumem - razumeo
                perfekt2 = "eo, eti, ela, elo, eli, ele"
                # donesem - doneo
                perfekt3 = "o, ti, la, lo, li, le"

                suff += self._make_suffs(perfekt)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt2))
                if len(base_str) >= 2:
                    if base_str[-2:-1].lower() not in self.SAMOGLASNICI:
                        # razapnem - razapeo
                        output3 += self._join_pref_base_suff("", base_str[:-1] + "e", self._make_suffs(perfekt3))
                        # razapnem - razapnuo
                        output3 += self._join_pref_base_suff("", base_str + "u", self._make_suffs(perfekt3))
                    else:
                        output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt3))
                else:
                    output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(perfekt3))

            # Aorist
            if base_str[-2:].lower() == "uj":
                # socijalizujem - socijalizovah  uj -> ov
                aorist = "ah, aše, asmo, aste, ašte, ahu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str[:-2] + "ov", self._make_suffs(aorist))
                output_ev += self._join_pref_base_suff("", base_str[:-2] + "ev", self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str[:-2] + "iv", self._make_suffs(aorist))
            elif base_str[-2:].lower() == "ij":
                # dobijam - dobijah - dobivah
                # izlijem - izlih - izlivah
                aorist = "ah, aše, asmo, aste, ašte, ahu"
                aorist2 = "h, še, smo, ste, šte, hu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
                output += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(aorist2))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(aorist))
            elif base_str[-2:].lower() == "aj":
                # postajem - postajah
                # saznajem - saznavah
                aorist = "ah, aše, asmo, aste, ašte, ahu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(aorist))
            elif base_str[-1:].lower() in "šžč":
                # manipulišem - manipulisah  š -> s
                # prikažem - prikazah ž -> z
                # podstičem - podsticao
                if len(base_str) > 1:
                    if base_str[-2:-1].lower() in "eu":
                        nastavak1 = self.reverse_palatalizacija(base_str[-1].lower())
                        nastavak2 = self.reverse_sibilarizacija(base_str[-1].lower())
                    else:
                        nastavak1 = self.reverse_sibilarizacija(base_str[-1].lower())
                        nastavak2 = self.reverse_palatalizacija(base_str[-1].lower())
                else:
                    nastavak1 = ""
                    nastavak2 = ""
                
                # Aorist (ah) Plačem Plakah   Oblažem Oblagah   Režem Rezah
                # Aurist (oh) Obučem Obukoh   Sečem Sekoh
                aorist = f"{nastavak1}ah, {nastavak1}aše, {nastavak1}asmo, {nastavak1}aste, {nastavak1}ašte, {nastavak1}ahu"
                aorist2 = f"{nastavak1}oh, {nastavak1}oše, {nastavak1}osmo, {nastavak1}oste, {nastavak1}ošte, {nastavak1}ohu"
                aorist3 = f"{nastavak2}ah, {nastavak2}aše, {nastavak2}asmo, {nastavak2}aste, {nastavak2}ašte, {nastavak2}ahu"
                
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(aorist2))
                output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(aorist3))
            elif base_str[-1:].lower() in "ć":
                # Obrćem - Obrtah
                aorist = "ah, aše, asmo, aste, ašte, ahu"
                nastavak1 = "t"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str[:-1] + nastavak1, self._make_suffs(aorist))
            elif base_str[-2:].lower() == "nj":
                # razapinjem - razapinjah
                aorist = "ah, aše, asmo, aste, ašte, ahu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
            elif base_str[-1:].lower() == "n" and len(base_str) > 1:
                # Potisnem - Potisnuh
                # Postignem - Postigoh
                aorist = "uh, uše, usmo, uste, ušte,uhu"
                aorist2 = "oh, oše, osmo, oste, ošte,ohu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(aorist2))
            elif base_str[-1:].lower() == "s":
                # Donesem - Donesoh
                aorist = "oh, oše, osmo, oste, ošte,ohu"
                aorist2 = "oh, oše, osmo, oste, ošte,ohu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist2))
            elif base_str[-4:].lower() == "šalj":
                # Šaljem - Slao
                aorist = "h, še, smo, ste, šte,hu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str[:-4] + "sla", self._make_suffs(aorist))
            elif base_str[-2:].lower() == "lj" and len(base_str) >= 3:
                # Šaljem - Slah  Meljem - Mleh  Koljem - Klah
                # Đeljem - Đeljao
                aorist = "h, še, smo, ste, šte,hu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str[:-3] + "la", self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str[:-3] + "le", self._make_suffs(aorist))
                output3 += self._join_pref_base_suff("", base_str + "a", self._make_suffs(aorist))
            elif base_str[-1:].lower() == "đ":
                # Nadiđem - Nadiđoh
                aorist = "oh, oše, osmo, oste, ošte, ohu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
            elif base_str[-2:].lower() == "ov":
                # Izazovem - Izazvah
                aorist = "ah, aše, asmo, aste, ašte, ahu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str[:-2] + "v", self._make_suffs(aorist))
            else:
                # planem - planuh
                aorist = "uh, uše, usmo, uste, ušte,uhu"
                # razumem - razumeh
                aorist2 = "eh, eše, esmo, este, ešte,ehu"
                # donesem - donesoh
                aorist3 = "oh, oše, osmo, oste, ošte,ohu"
                # razapnem - razapeh
                aorist_razapeh = "eh,eše,esmo,este,ešte,ehu"
                # razapnem - razapnuh
                aorist_razapnuh = "uh,uše,usmo,uste,ušte,uhu"
                suff += self._make_suffs(aorist)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist2))
                if len(base_str) >= 2:
                    if base_str[-2:-1].lower() not in self.SAMOGLASNICI:
                        # razapnem - razapeh
                        output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(aorist_razapeh))
                        # razapnem - razapnuh
                        output3 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist_razapnuh))
                    else:
                        output3 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist3))
                else:
                    output3 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist3))

            # Futur
            if base_str[-2:].lower() == "uj":
                # socijalizujem - socijalizovaću  uj -> ov
                futur = "aću, aćeš, aće, aćemo, aćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-2] + "ov", self._make_suffs(futur))
                output_ev += self._join_pref_base_suff("", base_str[:-2] + "ev", self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-2] + "iv", self._make_suffs(futur))
            elif base_str[-2:].lower() == "ij":
                # dobijam - dobijaću - dobivaću
                # izlijem - izliću - izlivaću
                futur = "aću, aćeš, aće, aćemo, aćete"
                futur2 = "ću, ćeš, će, ćemo, ćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
                output += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur2))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(futur))
            elif base_str[-2:].lower() == "aj":
                # postajem - postajaću
                # saznajem - saznavaću
                futur = "aću, aćeš, aće, aćemo, aćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "v", self._make_suffs(futur))
            elif base_str[-1:].lower() in "šžč":
                # manipulišem - manipulisaću  š -> s
                # prikažem - prikazaću ž -> z
                # podstičem - podsticao
                if len(base_str) > 1:
                    if base_str[-2:-1].lower() in "eu":
                        nastavak1 = self.reverse_palatalizacija(base_str[-1].lower())
                        nastavak2 = self.reverse_sibilarizacija(base_str[-1].lower())
                    else:
                        nastavak1 = self.reverse_sibilarizacija(base_str[-1].lower())
                        nastavak2 = self.reverse_palatalizacija(base_str[-1].lower())
                else:
                    nastavak1 = ""
                    nastavak2 = ""
                
                futur = f"{nastavak1}aću, {nastavak1}aćeš, {nastavak1}aće, {nastavak1}aćemo, {nastavak1}aćete"
                futur2 = "ću, ćeš, će, ćemo, ćete"
                futur3 = f"{nastavak2}aću, {nastavak2}aćeš, {nastavak2}aće, {nastavak2}aćemo, {nastavak2}aćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur2))
                output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur3))
            elif base_str[-1:].lower() in "ć":
                # Obrćem - Obrtaću
                futur = "aću, aćeš, aće, aćemo, aćete"
                nastavak1 = "t"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-1] + nastavak1, self._make_suffs(futur))
            elif base_str[-2:].lower() == "nj":
                # razapinjem - razapinjaću
                futur = "aću, aćeš, aće, aćemo, aćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
            elif base_str[-1:].lower() == "n" and len(base_str) > 1:
                # Potisnem - Potisnuću
                # Postignem - Postiću
                futur = "uću, ućeš, uće, ućemo, ućete"
                futur2 = "ću, ćeš, će, ćemo, ćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-2], self._make_suffs(futur2))
            elif base_str[-1:].lower() == "s":
                # Donesem - Donešću
                # Donesem - Doneću
                futur = "šću, šćeš, šće, šćemo, šćete"
                futur2 = "ću, ćeš, će, ćemo, ćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur2))
            elif base_str[-4:].lower() == "šalj":
                # Šaljem - Slao
                futur = "ću, ćeš, će, ćemo, ćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-4] + "sla", self._make_suffs(futur))
            elif base_str[-2:].lower() == "lj" and len(base_str) >= 3:
                # Šaljem - Slaću  Meljem - Mleću  Koljem - Klaću
                # Đeljem - Đeljaću
                futur = "ću, ćeš, će, ćemo, ćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-3] + "la", self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str[:-3] + "le", self._make_suffs(futur))
                output3 += self._join_pref_base_suff("", base_str + "a", self._make_suffs(futur))
            elif base_str[-1:].lower() == "đ":
                # Nadiđem - Nadiću
                futur = "ću, ćeš, će, ćemo, ćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur))
            elif base_str[-2:].lower() == "ov":
                # Izazovem - Izazvaću
                futur = "aću, aćeš, aće, aćemo, aćete"
                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str[:-2] + "v", self._make_suffs(futur))
            else:
                # planem - planuću
                futur = "uću, ućeš, uće, ućemo, ućete"
                # razumem - razumeću
                futur2 = "eću, ećeš, eće, ećemo, ećete"
                # donesem - doneću
                futur3 = "ću, ćeš, će, ćemo, ćete"

                suff += self._make_suffs(futur)
                output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(futur2))
                if len(base_str) >= 2:
                    if base_str[-2:-1].lower() not in self.SAMOGLASNICI:
                        # razapnem - razapeću
                        output3 += self._join_pref_base_suff("", base_str[:-1] + "e", self._make_suffs(futur3))
                        # razapnem - razapnuću
                        output3 += self._join_pref_base_suff("", base_str + "u", self._make_suffs(futur3))
                    else:
                        output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur3))
                else:
                    output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(futur3))

            # Extra
            extra = "ući"

            # Add imperativ
            if imperativ_output1:
                output += "\n".join(x for x in imperativ_output1.split(",") if x.strip()) + "\n"
            if imperativ_output2:
                output2 += "\n".join(x for x in imperativ_output2.split(",") if x.strip()) + "\n"
            if imperativ_output3:
                output3 += "\n".join(x for x in imperativ_output3.split(",") if x.strip()) + "\n"
            
            extra_plus = None
            extra_suffs = ["avši","evši","ivši","ovši","uvši","avavši","evavši","ivavši","ovavši","uvavši"]
            if base_str_extra:
                extra_plus = {}
                if base_str_extra[0] and base_str_extra[0][-1] in self.SAMOGLASNICI:
                    base_str_extra[0] = base_str_extra[0][:-1]
                extra_plus["opt1"] = [base_str_extra[0] + x for x in extra_suffs]
                if base_str_extra[1] and base_str_extra[1][-1] in self.SAMOGLASNICI:
                    base_str_extra[1] = base_str_extra[1][:-1]
                extra_plus["opt2"] = [base_str_extra[1] + x for x in extra_suffs]
                if base_str_extra[2] and base_str_extra[2][-1] in self.SAMOGLASNICI:
                    base_str_extra[2] = base_str_extra[2][:-1]
                extra_plus["opt3"] = [base_str_extra[2] + x for x in extra_suffs]
            
            suff += self._make_suffs(extra)
            if base_str[-2:].lower() == "uj":
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output_ev += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="Socijalizujem-Socijalizovao;" + ",".join(output.splitlines()),
                    opt2="Bičujem-Bičevao;" + ",".join(output_ev.splitlines()),
                    opt3="Okružujem-Okruživao;" + ",".join(output2.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-2:].lower() == "ij":
                # Dobijam Dobijacu
                # Izlijem Izlicu
                output += self._join_pref_base_suff("", base_str[:-1] + "vaj", self._make_suffs(extra))
                output += self._join_pref_base_suff("", base_str + "aj", self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "vaj", self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "j", self._make_suffs(extra))
                self.variant_show(
                    opt1="Sa (j) Dobijam - Dobijao;" + ",".join(output.splitlines()),
                    opt2="Bez (j) Izlijem - Izlio;" + ",".join(output2.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-2:].lower() == "aj":
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str[:-1] + "vaj", self._make_suffs(extra))
                self.variant_show(
                    opt1="Postajem - Postajao;" + ",".join(output.splitlines()),
                    opt2="Sa (v) Saznajem-Saznavao;" + ",".join(output2.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-1:].lower() in "šžč":
                # podstičem - podsticao
                # Sečem - Sekao
                
                if len(base_str) > 1:
                    if base_str[-2:-1].lower() in "eu":
                        extra = f"{self.reverse_palatalizacija(base_str[-1:])}ući,{self.reverse_sibilarizacija(base_str[-1:])}i"
                    else:
                        extra = f"{base_str[-1:]}ući,{base_str[-1:]}i"

                    output += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(extra))
                    output2 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(extra))
                    output3 += self._join_pref_base_suff("", base_str[:-1], self._make_suffs(extra))
                else:
                    output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                    output2 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                    output3 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                
                self.variant_show(
                    opt1="Aorist AH Režem - Rezah;" + ",".join(output.splitlines()),
                    opt2="Aorist OH Sečem - Sekoh;" + ",".join(output2.splitlines()),
                    opt3="ČŽŠ -> KGH;" + ",".join(output3.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-2:].lower() == "nj":
                # Proklinjem
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="DEFAULT;" + ",".join(output.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-1:].lower() == "n" and len(base_str) > 1:
                # Potisnem - Potisnuću
                # Postignem - Postiću
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str[:-2] + "ž", self._make_suffs(extra))
                self.variant_show(
                    opt1="Potisnem - Potisnuću;" + ",".join(output.splitlines()),
                    opt2="Postignem - Postiću;" + ",".join(output2.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-1:].lower() == "s":
                # Donesem-Donesti-Donešću
                # Donesem-Doneti-Doneću
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="Donesem-Donesti-Donešću;" + ",".join(output.splitlines()),
                    opt2="Donesem-Doneti-Doneću;" + ",".join(output2.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-4:].lower() == "šalj":
                # Šaljem - Slao - Šaljući
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="DEFAULT;" + ",".join(output.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-2:].lower() == "lj" and len(base_str) >= 3:
                # Šaljem - Slaću  Meljem - Mleću  Koljem - Klaću
                # Đeljem - Đeljaću
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output3 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="Koljem - Klao;" + ",".join(output.splitlines()),
                    opt2="Meljem - Mleo;" + ",".join(output2.splitlines()),
                    opt3="Đeljem - Đeljao;" + ",".join(output3.splitlines()),
                    extra_plus=extra_plus
                )
            elif base_str[-1:].lower() == "đ":
                # Nadiđem - Nadiću
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="DEFAULT;" + ",".join([x.strip() for x in output.split("\n") if x.strip()]),
                    extra_plus=extra_plus
                )
            elif base_str[-2:].lower() == "ov":
                # Izazovem - Izazovući
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="DEFAULT;" + ",".join([x.strip() for x in output.split("\n") if x.strip()]),
                    extra_plus=extra_plus
                )
            else:
                output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                output2 += self._join_pref_base_suff("", base_str, self._make_suffs("eći"))
                output3 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
                self.variant_show(
                    opt1="Planem - Planuo;" + ",".join([x.strip() for x in output.split("\n") if x.strip()]),
                    opt2="Razumem - Razumeo;" + ",".join([x.strip() for x in output2.split("\n") if x.strip()]),
                    opt3="Donesem - Doneo;" + ",".join([x.strip() for x in output3.split("\n") if x.strip()]),
                    extra_plus=extra_plus
                )

        elif nastavak == "i":
            # suff = palim - paliti
            # suff2 = živim - živeti
            # suff3 = postojim - postojati

            # Present
            present = "im, iš, i, imo, ite, e"
            suff = self._make_suffs(present)
            suff2 = self._make_suffs(present)
            suff3 = self._make_suffs(present)
            output = self._join_pref_base_suff("", base_str, self._make_suffs(present))
            output2 = self._join_pref_base_suff("", base_str, self._make_suffs(present))
            output3 = self._join_pref_base_suff("", base_str, self._make_suffs(present))
            # Perfekt
            # pazim - pazio
            base_str_extra = [base_str, base_str, base_str, base_str]
            perfekt = "io, iti, ila, ilo, ili, ile"
            perfekt2 = "eo, eti, ela, elo, eli, ele"
            perfekt3 = "ao, ati, ala, alo, ali, ale"
            suff += self._make_suffs(perfekt)
            suff2 += self._make_suffs(perfekt2)
            suff3 += self._make_suffs(perfekt3)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt))
            output2 += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt2))
            output3 += self._join_pref_base_suff("", base_str, self._make_suffs(perfekt3))
            # Aorist
            # pazim - pazih
            aorist = "ih, iše, ismo, iste, ište, ihu"
            aorist2 = "eh, eše, esmo, este, ešte, ehu"
            aorist3 = "ah, aše, asmo, aste, ašte, ahu"
            suff += self._make_suffs(aorist)
            suff2 += self._make_suffs(aorist2)
            suff3 += self._make_suffs(aorist3)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(aorist))
            output2 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist2))
            output3 += self._join_pref_base_suff("", base_str, self._make_suffs(aorist3))
            # Futur
            # pazim - paziću
            # vredim - vredeću
            futur = "iću, ićeš, iće, ićemo, ićete"
            futur2 = "eću, ećeš, eće, ećemo, ećete"
            futur3 = "aću, aćeš, aće, aćemo, aćete"
            suff += self._make_suffs(futur)
            suff2 += self._make_suffs(futur2)
            suff3 += self._make_suffs(futur3)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(futur))
            output2 += self._join_pref_base_suff("", base_str, self._make_suffs(futur2))
            output3 += self._join_pref_base_suff("", base_str, self._make_suffs(futur3))

            # Imperativ
            output += self._join_pref_base_suff("", base_str, self._make_suffs("i,ite"))
            output2 += self._join_pref_base_suff("", base_str, self._make_suffs("i,ite"))
            output3 += self._join_pref_base_suff("", base_str, self._make_suffs("i,ite"))
            # Extra
            extra = "eći"

            extra_plus = None
            extra_suffs = ["avši","evši","ivši","ovši","uvši","avavši","evavši","ivavši","ovavši","uvavši"]
            if base_str_extra:
                extra_plus = {}
                if base_str_extra[0] and base_str_extra[0][-1] in self.SAMOGLASNICI:
                    base_str_extra[0] = base_str_extra[0][:-1]
                extra_plus["opt1"] = [base_str_extra[0] + x for x in extra_suffs]
                if base_str_extra[1] and base_str_extra[1][-1] in self.SAMOGLASNICI:
                    base_str_extra[1] = base_str_extra[1][:-1]
                extra_plus["opt2"] = [base_str_extra[1] + x for x in extra_suffs]
                if base_str_extra[2] and base_str_extra[2][-1] in self.SAMOGLASNICI:
                    base_str_extra[2] = base_str_extra[2][:-1]
                extra_plus["opt3"] = [base_str_extra[2] + x for x in extra_suffs]

            suff += self._make_suffs(extra)
            suff2 += self._make_suffs(extra)
            suff3 += self._make_suffs(extra)
            output += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
            output2 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
            output3 += self._join_pref_base_suff("", base_str, self._make_suffs(extra))
            self.variant_show(
                opt1="Sa i (palim-paliti);" + ",".join([x.strip() for x in output.split("\n") if x.strip()]),
                opt2="Sa e (živim-živeti);" + ",".join([x.strip() for x in output2.split("\n") if x.strip()]),
                opt3="Sa a (postojim-postojati);" + ",".join([x.strip() for x in output3.split("\n") if x.strip()]),
                extra_plus=extra_plus
            )

        else:
            return []
        
        suff = self._delete_duplicates_from_list(suff.splitlines())

        output = self._delete_duplicates_from_list(output.splitlines())

        return output

    def vlastito_ime(self, musko_ime: bool = False, zensko_ime: bool = False) -> list:
        base_str = self.txt_base.text().strip()
        if len(base_str) < 3:
            return []

        output = ""
        output2 = ""

        if zensko_ime:
            padezi = [x.strip() for x in "a, e, i, o, u, om".split(",")]
            imena = [x.strip() for x in base_str.split(" ")]
            for padez in padezi:
                result = ""
                has_changed = False
                for idx, ime in enumerate(imena):
                    if has_changed and idx == len(imena) - 1:
                        result += f" {ime}"
                        break

                    if ime.lower().endswith("a"):
                        result += f" {ime[:-1]}{padez}"
                        has_changed = True
                    else:
                        result += f" {ime}"
                output += result.strip() + "\n"
        elif musko_ime:
            imena = [x.strip() for x in base_str.split(" ") if x.strip()]
            padezi = 7

            for padez in range(padezi):
                result = ""
                result2 = ""
                for idx, ime in enumerate(imena):
                    if ime.endswith("."):
                        result += f" {ime}"
                        continue

                    result += " " + self._vlastito_ime_promena(ime, padez)[0]
                    result2 += " " + self._vlastito_ime_promena(ime, padez)[1]

                output += result.strip() + "\n"
                output2 += result2.strip() + "\n"

                output += self._vlastito_ime_promena(" ".join(imena), padez)[0] + "\n"
                output2 += self._vlastito_ime_promena(" ".join(imena), padez)[1] + "\n"
            
            if output == output2:
                output2 = ""

        output = self._delete_duplicates_from_list(output.splitlines())
        output2 = self._delete_duplicates_from_list(output2.splitlines())

        if output2:
            self.variant_show(
                opt1="Opcija 1;" + "\n".join(output),
                opt2="Opcija 2;" + "\n".join(output2)
            )

        return output

    def _vlastito_ime_promena(self, ime: str, padez: int) -> tuple[str]:
        if len(ime) < 1:
            return (ime, ime)

        if ime.endswith("."):
            return (ime, ime)

        if ime[-1].lower() == "a":
            padezi = "a,e,i,u,a,om,i".split(",")
            return (f"{ime[:-1]}{padezi[padez]}", f"{ime[:-1]}{padezi[padez]}")
        elif ime[-1].lower() == "e":
            padezi = "e,ea,eu,ea,e,eom,eu".split(",")
            padezi2 = "e,a,i,u,e,om,i".split(",")
            return (f"{ime[:-1]}{padezi[padez]}", f"{ime[:-1]}{padezi2[padez]}")
        elif ime[-1].lower() == "i":
            padezi = "i,ija,iju,ija,i,ijem,iju".split(",")
            return (f"{ime[:-1]}{padezi[padez]}", f"{ime[:-1]}{padezi[padez]}")
        elif ime[-1].lower() == "o":
            padezi = "o,oa,ou,oa,o,oom,ou".split(",")
            padezi2 = "o,a,u,a,o,om,u".split(",")
            return (f"{ime[:-1]}{padezi[padez]}", f"{ime[:-1]}{padezi2[padez]}")
        elif ime[-1].lower() == "u":
            padezi = "u,ua,uu,ua,u,uom,uu".split(",")
            padezi2 = "u,a,u,a,u,om,u".split(",")
            return (f"{ime[:-1]}{padezi[padez]}", f"{ime[:-1]}{padezi2[padez]}")
        else:
            # Kada se zavrsava na suglasnik
            if ime[-1].lower() in ["ć"]:
                padezi = ",a,u,a,u,em,u".split(",")
                padezi2 = ",a,u,a,,om,u".split(",")
                return (f"{ime}{padezi[padez]}", f"{ime}{padezi2[padez]}")
            elif len(ime) >= 4 and ime[-4:].lower() == "ndar":
                # Aleksandar - Aleksandru
                padezi = "ndar,ndra,ndru,ndra,ndre,ndrom,ndru".split(",")
                padezi2 = ",a,u,a,e,om,u".split(",")
                return (f"{ime[:-4]}{padezi[padez]}", f"{ime}{padezi2[padez]}")
            else:
                padezi = ",a,u,a,,om,u".split(",")
                return (f"{ime}{padezi[padez]}", f"{ime}{padezi[padez]}")
        
    def _delete_duplicates_from_list(self, some_list: list) -> list:
        result = []
        for i in some_list:
            if i not in result:
                result.append(i)
        return result

    def _translate(self, text: str, translate_to_croatian: bool = True) -> str:
        if translate_to_croatian:
            code_from = googletrans.LANGCODES["english"]
            code_to = googletrans.LANGCODES["croatian"]
        else:
            code_to = googletrans.LANGCODES["english"]
            code_from = googletrans.LANGCODES["croatian"]

        trans = Translator()
        try:
            translated_text = trans.translate(text, dest=code_to, src=code_from).text
        except:
            translated_text = "Error"
        return translated_text

    def _key_press_event(self, btn: QtGui.QKeyEvent):
        if btn.key() == Qt.Key_Escape:
            if self.frm_padezi.isVisible():
                btn.accept()
                self.frm_padezi.setVisible(False)
                return None
            elif self.frm_edit.isVisible():
                btn.accept()
                self.frm_edit.setVisible(False)
                return None
            else:
                self.close()

    def lbl_padezi_img_double_click(self, e):
        self._padezi_image = False
        self.lbl_padezi_img.setVisible(False)
        self.lbl_padezi_text.setVisible(True)

    def lbl_padezi_text_double_click(self, e):
        self._padezi_image = True
        self.lbl_padezi_text.setVisible(False)
        self.lbl_padezi_img.setVisible(True)

    def _show_padezi_frame(self):
        if self.frm_padezi.isVisible():
            self.frm_padezi.setVisible(False)
        else:
            self.frm_padezi.setVisible(True)
            self.frm_padezi.raise_()

    def btn_padezi_close_click(self):
        self.frm_padezi.setVisible(False)

    def btn_edit_close_click(self):
        self.frm_edit.setVisible(False)

    def btn_edit_spaces_click(self):
        txt = self.txt_output.toPlainText()
        
        replace_count = 0
        txt_list = [x for x in txt.split("\n") if x != ""]
        new_txt_list = []
        for i in txt_list:
            while i.find("  ") >= 0:
                i = i.replace("  ", " ", 1)
                replace_count += 1
            i = i.strip()
            new_txt_list.append(i)

        new_txt = "\n".join(new_txt_list)
        self.txt_output.setText(new_txt)

        if replace_count:
            self.lbl_msg_spaces.setText(self.getl("def_editor_lbl_msg_spaces_text").replace("#1", str(replace_count)))
        else:
            self.lbl_msg_spaces.setText(self.getl("def_editor_lbl_msg_no_spaces_text"))

    def btn_edit_add_end_click(self):
        result = self._add_to_items(self.txt_output.toPlainText(), self.txt_edit_add_end.text(), to_end=True)
        self.txt_output.setText(result)
        self.btn_edit_add_end.setEnabled(False)

    def btn_edit_add_beg_click(self):
        result = self._add_to_items(self.txt_output.toPlainText(), self.txt_edit_add_beg.text(), to_beginning=True)
        self.txt_output.setText(result)
        self.btn_edit_add_beg.setEnabled(False)

    def _add_to_items(self, txt: str, add_str: str, to_beginning: bool = None, to_end: bool = None) -> str:
        if not to_beginning and not to_end:
            return txt
        
        txt_list = [x for x in txt.split("\n") if x != ""]
        new_txt_list = []
        for i in txt_list:
            if to_beginning:
                new_txt_list.append(add_str + i)
            if to_end:
                new_txt_list.append(i + add_str)
        
        new_txt = "\n".join(new_txt_list)
        
        return new_txt

    def btn_edit_replace_add_click(self):
        result = self._replace_strings(
            self.txt_output.toPlainText(),
            self.txt_edit_replace.text(),
            self.txt_edit_with.text(),
            self.txt_edit_in_string.text(),
            self.chk_edit_case.isChecked()
        )
        
        output_text = self.txt_output.toPlainText()
        if output_text:
            if output_text[-1] != "\n":
                output_text += "\n"
        
        output_text += result[2]
        
        self.txt_output.setText(output_text)
        
        if result[1]:
            self.lbl_edit_msg.setText(self.getl("def_editor_msg_replaced_text").replace("#1", str(result[1])))
        else:
            self.lbl_edit_msg.setText(self.getl("def_editor_msg_no_replaced_text"))
        self.btn_edit_replace.setEnabled(False)
        self.btn_edit_replace_add.setEnabled(False)

    def btn_edit_replace_click(self):
        result = self._replace_strings(
            self.txt_output.toPlainText(),
            self.txt_edit_replace.text(),
            self.txt_edit_with.text(),
            self.txt_edit_in_string.text(),
            self.chk_edit_case.isChecked()
        )
        self.txt_output.setText(result[0])
        if result[1]:
            self.lbl_edit_msg.setText(self.getl("def_editor_msg_replaced_text").replace("#1", str(result[1])))
        else:
            self.lbl_edit_msg.setText(self.getl("def_editor_msg_no_replaced_text"))
        self.btn_edit_replace.setEnabled(False)
        self.btn_edit_replace_add.setEnabled(False)

    def _replace_strings(self, txt: str, replace_str: str, with_str: str, in_word: str, match_case: bool) -> list:
        """ Replaces string in text
        Return:
            [0] = all items 
            [1] = number of replacement
            [2] = only replaced items
        """
        
        if not replace_str:
            return txt, 0, ""
        # If in_word exist but does not contain replace_str, return passed values
        if in_word:
            if in_word.lower().find(replace_str.lower()) < 0:
                return txt, 0, ""
            if in_word.find(replace_str) < 0 and match_case:
                return txt, 0, ""
            
        txt_list = [x for x in txt.split("\n") if x != ""]

        if not match_case:
            in_word = in_word.lower()
            replace_str = replace_str.lower()

        counter = 0
        in_word_start_pos = in_word.find(replace_str)
        all_items = []
        changed_items = []

        for item in txt_list:
            is_changed = False
            if not match_case:
                output_item = item.lower()
            else:
                output_item = item

            if in_word:
                start_pos = 0
                while start_pos >= 0:
                    start_pos = output_item.find(in_word, start_pos)
                    if start_pos >= 0:
                        item = item[:start_pos + in_word_start_pos] + with_str + in_word[in_word_start_pos + len(replace_str):] + item[start_pos + len(in_word):]
                        start_pos += len(in_word) - len(replace_str) + len(with_str)
                        if not match_case:
                            output_item = item.lower()
                        else:
                            output_item = item
                        counter += 1
                        is_changed = True
            else:
                start_pos = 0
                while start_pos >= 0:
                    start_pos = output_item.find(replace_str, start_pos)
                    if start_pos >= 0:
                        item = item[:start_pos] + with_str + item[start_pos + len(replace_str):]
                        start_pos += len(with_str)
                        if not match_case:
                            output_item = item.lower()
                        else:
                            output_item = item
                        counter += 1
                        is_changed = True
            
            all_items.append(item)
            if is_changed:
                changed_items.append(item)

        all_text = "\n".join(all_items)
        changed_text = "\n".join(changed_items)
        
        return all_text, counter, changed_text

    def btn_edit_switch_click(self):
        tmp = self.txt_edit_replace.text()
        self.txt_edit_replace.setText(self.txt_edit_with.text())
        self.txt_edit_with.setText(tmp)

    def txt_edit_add_end_text_changed(self):
        self._set_buttons_for_replace()

    def txt_edit_add_beg_text_changed(self):
        self._set_buttons_for_replace()

    def txt_edit_replace_text_changed(self):
        self._set_buttons_for_replace()

    def txt_edit_in_string_click(self):
         self._set_buttons_for_replace()

    def chk_edit_case_state_changed(self):
        self._set_buttons_for_replace()

    def _set_buttons_for_replace(self):
        if not self.txt_edit_replace.text() or () or (self.txt_edit_replace.text() not in self.txt_output.toPlainText() and self.chk_edit_case.isChecked()):
            self.btn_edit_replace.setEnabled(False)
            self.btn_edit_replace_add.setEnabled(False)
        else:
            if (self.txt_edit_replace.text().lower() not in self.txt_output.toPlainText().lower() and not self.chk_edit_case.isChecked()) or (self.txt_edit_replace.text() not in self.txt_output.toPlainText() and self.chk_edit_case.isChecked()):
                self.btn_edit_replace.setEnabled(False)
                self.btn_edit_replace_add.setEnabled(False)
            else:
                self.btn_edit_replace.setEnabled(True)
                self.btn_edit_replace_add.setEnabled(True)

        if self.txt_edit_add_beg.text():
            self.btn_edit_add_beg.setEnabled(True)
        else:
            self.btn_edit_add_beg.setEnabled(False)

        if self.txt_edit_add_end.text():
            self.btn_edit_add_end.setEnabled(True)
        else:
            self.btn_edit_add_end.setEnabled(False)

    def btn_edit_output_click(self):
        if self.frm_edit.isVisible():
            self.frm_edit.setVisible(False)
        else:
            self.frm_edit.setVisible(True)
            self.frm_edit.raise_()

    def btn_generate_click(self):
        # Create lists if checkboxex are checked
        if self.chk_add_end.isChecked():
            lst_e = [x for x in self.txt_end.toPlainText().split("\n") if x != ""]
        else:
            lst_e = []
        if self.chk_add_beggining.isChecked():
            lst_b = [x for x in self.txt_beggining.toPlainText().split("\n") if x != ""]
        else:
            lst_b = []
        
        # Append base string
        if self.chk_add_base.isChecked():
            if " " not in lst_e:
                lst_e.append("")
        
        # Create Output list that already exist
        lst_o = [x for x in self.txt_output.toPlainText().split("\n") if x != ""]

        final = []
        base = self.txt_base.text()

        # Append at beginning
        if self.chk_add_base.isChecked():
            for i in lst_b:
                final.append(i + base)

        # Append at end
        for i in lst_e:
            final.append(base + i)

        # Combine beginning and end
        if self.chk_combo_add.isChecked():
            for i in lst_b:
                for j in lst_e:
                    final.append(i + base + j)
        
        # Make capital letter
        tmp = []
        if self.chk_first_up.isChecked():
            for i in final:
                tmp.append(i.capitalize())
        
        final += tmp

        # Combine with previous list
        if not self.chk_combo_prev.isChecked():
            output_string = "\n".join(final)
            if output_string:
                output_string += "\n"
            
            self.txt_output.setText(output_string)
            return

        output = []
        eol = [False, False]
        count = 0
        finish_loop = False
        while not finish_loop:
            apend_str = ""

            if len(lst_o) <= count:
                eol[0] = True
            else:
                apend_str += lst_o[count]

            if len(final) <= count:
                eol[1] = True
            else:
                if apend_str:
                    apend_str += " " + final[count]
                else:
                    apend_str += final[count]
            
            output.append(apend_str)
            count += 1
            if eol[0] and eol[1]:
                finish_loop = True
        
        output_string = "\n".join(output)
        if output_string:
            output_string += "\n"
        
        self.txt_output.setText(output_string)
        UTILS.LogHandler.add_log_record("#1: Data generated.", ["DefinitionEditor"])

    def btn_base_text_changed(self):
        if self.get_valid_clipboard_text():
            self.btn_clip_content.setText("Clipboard:\n" + self.get_valid_clipboard_text())
            self.btn_clip_content.setVisible(True)
        else:
            self.btn_clip_content.setVisible(False)

        if self.txt_base.text():
            self.btn_generate.setEnabled(True)
        else:
            self.btn_generate.setEnabled(False)
        
        self.variant_hide()

        if self.chk_auto_show.isChecked():
            self.show_menu_selection_result(self.lbl_auto_show.objectName())

    def txt_output_text_changed(self):
        if self.ignore_txt_output_text_changed:
            return
        
        if self.txt_output.toPlainText():
            if self.txt_output.toPlainText()[-1] != "\n":
                cur = self.txt_output.textCursor()
                position = cur.position()
                self.txt_output.setText(self.txt_output.toPlainText() + "\n")
                cur = self.txt_output.textCursor()
                cur.setPosition(position)
                self.txt_output.setTextCursor(cur)
            self.btn_copy.setEnabled(True)
            if " " in self.txt_output.toPlainText():
                self.btn_switch_words_order.setEnabled(True)
        else:
            self.btn_copy.setEnabled(False)
            self.btn_switch_words_order.setEnabled(False)
        
        self.lbl_output.setText(self.getl("def_editor_lbl_output_text") + " (" + str(len([x for x in self.txt_output.toPlainText().split("\n") if x.strip()])) + ")")
        self._set_buttons_for_replace()
        self.colorize_variant_extra_buttons()

        if self.getv("definition_text_mark_enabled_in_def_add_dialog"):
            self.ignore_txt_output_text_changed = True
            self._text_handler_output.check_definitions()
            self.ignore_txt_output_text_changed = False

    def btn_copy_click(self):
        self.get_appv("clipboard").setText(self.txt_output.toPlainText())
        self.btn_copy.setEnabled(False)
        UTILS.LogHandler.add_log_record("#1: Data copied.", ["DefinitionEditor"])

    def btn_clear_output_click(self):
        self.txt_output.setText("")

    def btn_clear_end_click(self):
        self.txt_end.setText("")

    def btn_clear_beggining_click(self):
        self.txt_beggining.setText("")

    def btn_clear_base_click(self):
        self.txt_base.setText("")
        self.variant_hide()

    def btn_cancel_click(self):
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "definition_editor_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("definition_editor_win_geometry", {}, save_to_file=True)

        g = self.get_appv("definition_editor_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["has_settings"] = self.chk_remember.isChecked()
        g["add_end"] = self.chk_add_end.isChecked()
        g["add_beggining"] = self.chk_add_beggining.isChecked()
        g["first_up"] = self.chk_first_up.isChecked()
        g["add_base"] = self.chk_add_base.isChecked()
        g["combo_add"] = self.chk_combo_add.isChecked()
        g["combo_prev"] = self.chk_combo_prev.isChecked()
        g["list_end"] = self._make_list(self.txt_end.toPlainText())
        g["list_beginning"] = self._make_list(self.txt_beggining.toPlainText())

        g["chk_edit_case"] = self.chk_edit_case.isChecked()
        g["txt_edit_replace"] = self.txt_edit_replace.text()
        g["txt_edit_with"] = self.txt_edit_with.text()
        g["txt_edit_in_string"] = self.txt_edit_in_string.text()
        g["txt_edit_add_beg"] = self.txt_edit_add_beg.text()
        g["txt_edit_add_end"] = self.txt_edit_add_end.text()

        g["show_padezi_img"] = self._padezi_image

        g["chk_auto_show"] = self.chk_auto_show.isChecked()
        g["lbl_auto_show_object_name"] = self.lbl_auto_show.objectName()

        self.get_appv("cm").remove_all_context_menu()

        if self._text_handler_output:
            self._text_handler_output.close_me()
            self._text_handler_output = None

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["DefinitionEditor"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _load_win_position(self):
        if "definition_editor_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("definition_editor_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            if g["has_settings"] is not None:
                self.chk_remember.setChecked(True)
                self.chk_add_end.setChecked(g["add_end"])
                self.chk_add_beggining.setChecked(g["add_beggining"])
                self.chk_first_up.setChecked(g["first_up"])
                self.chk_add_base.setChecked(g["add_base"])
                self.chk_combo_add.setChecked(g["combo_add"])
                self.chk_combo_prev.setChecked(g["combo_prev"])
                self.txt_end.setText(self._make_string(g["list_end"]))
                self.txt_beggining.setText(self._make_string(g["list_beginning"]))

                self.chk_edit_case.setChecked(g["chk_edit_case"])
                self.txt_edit_replace.setText(g["txt_edit_replace"])
                self.txt_edit_with.setText(g["txt_edit_with"])
                self.txt_edit_in_string.setText(g["txt_edit_in_string"])
                self.txt_edit_add_beg.setText(g["txt_edit_add_beg"])
                self.txt_edit_add_end.setText(g["txt_edit_add_end"])

                self._padezi_image = g["show_padezi_img"]
                if g["show_padezi_img"]:
                    self.lbl_padezi_img.setVisible(True)
                    self.lbl_padezi_text.setVisible(False)
                else:
                    self.lbl_padezi_img.setVisible(False)
                    self.lbl_padezi_text.setVisible(True)

                self.chk_auto_show.setChecked(g.get("chk_auto_show", False))
                self.lbl_auto_show.setObjectName(g.get("lbl_auto_show_object_name", "0"))

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _make_string(self, input_list: list) -> str:
        result = "\n".join(input_list)
        return result
    
    def _make_list(self, input_string: str) -> list:
        result = [x for x in input_string.split("\n") if x != ""]
        return result

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_base: QLabel = self.findChild(QLabel, "lbl_base")
        self.lbl_output: QLabel = self.findChild(QLabel, "lbl_output")

        self.chk_auto_show: QCheckBox = self.findChild(QCheckBox, "chk_auto_show")
        self.lbl_auto_show: QLabel = self.findChild(QLabel, "lbl_auto_show")

        self.btn_clear_base: QPushButton = self.findChild(QPushButton, "btn_clear_base")
        self.btn_clear_end: QPushButton = self.findChild(QPushButton, "btn_clear_end")
        self.btn_clear_beggining: QPushButton = self.findChild(QPushButton, "btn_clear_beggining")
        self.btn_clear_output: QPushButton = self.findChild(QPushButton, "btn_clear_output")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_generate: QPushButton = self.findChild(QPushButton, "btn_generate")
        self.btn_copy: QPushButton = self.findChild(QPushButton, "btn_copy")
        self.btn_first_letter: QPushButton = self.findChild(QPushButton, "btn_first_letter")
        self.btn_switch_words_order: QPushButton = self.findChild(QPushButton, "btn_switch_words_order")
        self.btn_clip_content: QPushButton = self.findChild(QPushButton, "btn_clip_content")

        self.chk_add_end: QCheckBox = self.findChild(QCheckBox, "chk_add_end")
        self.chk_add_beggining: QCheckBox = self.findChild(QCheckBox, "chk_add_beggining")
        self.chk_first_up: QCheckBox = self.findChild(QCheckBox, "chk_first_up")
        self.chk_add_base: QCheckBox = self.findChild(QCheckBox, "chk_add_base")
        self.chk_combo_add: QCheckBox = self.findChild(QCheckBox, "chk_combo_add")
        self.chk_combo_prev: QCheckBox = self.findChild(QCheckBox, "chk_combo_prev")
        self.chk_remember: QCheckBox = self.findChild(QCheckBox, "chk_remember")

        self.txt_base: QLineEdit = self.findChild(QLineEdit, "txt_base")
        self.txt_output: QTextEdit = self.findChild(QTextEdit, "txt_output")
        self.txt_end: QTextEdit = self.findChild(QTextEdit, "txt_end")
        self.txt_beggining: QTextEdit = self.findChild(QTextEdit, "txt_beggining")

        self.btn_edit_output:QPushButton = self.findChild(QPushButton, "btn_edit_output")
        self.frm_edit: QFrame = self.findChild(QFrame, "frm_edit")
        
        self.lbl_edit_replace: QLabel = self.findChild(QLabel, "lbl_edit_replace")
        self.lbl_edit_with: QLabel = self.findChild(QLabel, "lbl_edit_with")
        self.lbl_edit_in_string: QLabel = self.findChild(QLabel, "lbl_edit_in_string")
        self.lbl_edit_add_beg: QLabel = self.findChild(QLabel, "lbl_edit_add_beg")
        self.lbl_edit_add_end: QLabel = self.findChild(QLabel, "lbl_edit_add_end")
        self.lbl_edit_msg: QLabel = self.findChild(QLabel, "lbl_edit_msg")
        self.lbl_msg_spaces: QLabel = self.findChild(QLabel, "lbl_msg_spaces")

        self.btn_edit_switch: QPushButton = self.findChild(QPushButton, "btn_edit_switch")
        self.btn_edit_replace: QPushButton = self.findChild(QPushButton, "btn_edit_replace")
        self.btn_edit_replace_add: QPushButton = self.findChild(QPushButton, "btn_edit_replace_add")
        self.btn_edit_add_beg: QPushButton = self.findChild(QPushButton, "btn_edit_add_beg")
        self.btn_edit_add_end: QPushButton = self.findChild(QPushButton, "btn_edit_add_end")
        self.btn_edit_spaces: QPushButton = self.findChild(QPushButton, "btn_edit_spaces")
        self.btn_edit_close: QPushButton = self.findChild(QPushButton, "btn_edit_close")
        self.btn_edit_case: QPushButton = self.findChild(QPushButton, "btn_edit_case")

        self.chk_edit_case: QCheckBox = self.findChild(QCheckBox, "chk_edit_case")

        self.txt_edit_replace: QLineEdit = self.findChild(QLineEdit, "txt_edit_replace")
        self.txt_edit_with: QLineEdit = self.findChild(QLineEdit, "txt_edit_with")
        self.txt_edit_in_string: QLineEdit = self.findChild(QLineEdit, "txt_edit_in_string")
        self.txt_edit_add_beg: QLineEdit = self.findChild(QLineEdit, "txt_edit_add_beg")
        self.txt_edit_add_end: QLineEdit = self.findChild(QLineEdit, "txt_edit_add_end")

        self.lbl_padezi_text: QLabel = self.findChild(QLabel, "lbl_padezi_text")
        self.lbl_padezi_img: QLabel = self.findChild(QLabel, "lbl_padezi_img")
        self.frm_padezi: QFrame = self.findChild(QFrame, "frm_padezi")
        self.frm_padezi.move(10, 140)
        self.frm_padezi.setStyleSheet("background-color: #00007f; color: #ffff00;")
        self.btn_padezi_close: QPushButton = self.findChild(QPushButton, "btn_padezi_close")
        self.frm_padezi.setVisible(False)
        self.action_show_padezi: QAction = QAction(self)
        self.action_show_padezi.setShortcut("Ctrl+Return")
        self.addAction(self.action_show_padezi)

        # Frame Variant
        self.frm_variant: QFrame = self.findChild(QFrame, "frm_variant")
        self.lbl_variant_title: QLabel = self.findChild(QLabel, "lbl_variant_title")
        self.btn_variant_close: QPushButton = self.findChild(QPushButton, "btn_variant_close")
        self.btn_variant_opt1: QPushButton = self.findChild(QPushButton, "btn_variant_opt1")
        self.btn_variant_opt2: QPushButton = self.findChild(QPushButton, "btn_variant_opt2")
        self.btn_variant_opt3: QPushButton = self.findChild(QPushButton, "btn_variant_opt3")
        self.lst_variant: QListWidget = self.findChild(QListWidget, "lst_variant")
        # Variant extra buttons
        self.btn_variant_extras = []
        x = 200
        y = 3
        for i in range(10):
            btn = QPushButton(self.frm_variant)
            btn.setText("")
            btn.setObjectName("")
            btn.move(x, y)
            btn.resize(115, 24)
            font = btn.font()
            font.setPointSize(12)
            btn.setFont(font)
            # Connect buttons clicked event with "self.event_variant_extra_button_clicked" and send button object to it
            btn.clicked.connect(lambda x, y=btn: self.event_variant_extra_button_clicked(y))
            btn.mouseReleaseEvent = lambda x, y=btn: self.event_variant_mouse_release(x, y)
            
            self.btn_variant_extras.append(btn)
            y += 24 + 1
            if i == 4:
                x = 320
                y = 3

        self.frm_variant_pre: QFrame = self.findChild(QFrame, "frm_variant_pre")
        self.lbl_variant_pre_title: QLabel = self.findChild(QLabel, "lbl_variant_pre_title")
        self.lbl_variant_pre_content: QLabel = self.findChild(QLabel, "lbl_variant_pre_content")

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("def_editor_lbl_title_text"))
        self.lbl_base.setText(self.getl("def_editor_lbl_base_text"))
        self.lbl_output.setText(self.getl("def_editor_lbl_output_text"))

        self.chk_auto_show.setText(self.getl("def_editor_chk_auto_show_text"))
        self.chk_auto_show.setToolTip(self.getl("def_editor_chk_auto_show_tt"))
        self.lbl_auto_show.setText("- - -")
        self.lbl_auto_show.setObjectName("0")

        self.chk_add_end.setText(self.getl("def_editor_chk_add_end_text"))
        self.chk_add_end.setToolTip(self.getl("def_editor_chk_add_end_tt"))
        self.chk_add_beggining.setText(self.getl("def_editor_chk_add_beggining_text"))
        self.chk_add_beggining.setToolTip(self.getl("def_editor_chk_add_beggining_tt"))
        self.chk_first_up.setText(self.getl("def_editor_chk_first_up_text"))
        self.chk_first_up.setToolTip(self.getl("def_editor_chk_first_up_tt"))
        self.chk_add_base.setText(self.getl("def_editor_chk_add_base_text"))
        self.chk_add_base.setToolTip(self.getl("def_editor_chk_add_base_tt"))
        self.chk_combo_add.setText(self.getl("def_editor_chk_combo_add_text"))
        self.chk_combo_add.setToolTip(self.getl("def_editor_chk_combo_add_tt"))
        self.chk_combo_prev.setText(self.getl("def_editor_chk_combo_prev_text"))
        self.chk_combo_prev.setToolTip(self.getl("def_editor_chk_combo_prev_tt"))
        self.chk_remember.setText(self.getl("def_editor_chk_remember_text"))
        self.chk_remember.setToolTip(self.getl("def_editor_chk_remember_tt"))

        self.btn_generate.setText(self.getl("def_editor_btn_generate_text"))
        self.btn_generate.setToolTip(self.getl("def_editor_btn_generate_tt"))
        self.btn_copy.setText(self.getl("def_editor_btn_copy_text"))
        self.btn_copy.setToolTip(self.getl("def_editor_btn_copy_tt"))
        self.btn_cancel.setText(self.getl("def_editor_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("def_editor_btn_cancel_tt"))
        self.btn_first_letter.setText(self.getl("def_editor_btn_first_letter_text"))
        self.btn_first_letter.setToolTip(self.getl("def_editor_btn_first_letter_tt"))
        self.btn_switch_words_order.setText(self.getl("def_editor_btn_switch_words_order_text"))
        self.btn_switch_words_order.setToolTip(self.getl("def_editor_btn_switch_words_order_tt"))

        self.btn_clear_base.setText(self.getl("def_editor_btn_clear_text"))
        self.btn_clear_base.setToolTip(self.getl("def_editor_btn_clear_tt"))
        self.btn_clear_end.setText(self.getl("def_editor_btn_clear_text"))
        self.btn_clear_end.setToolTip(self.getl("def_editor_btn_clear_tt"))
        self.btn_clear_beggining.setText(self.getl("def_editor_btn_clear_text"))
        self.btn_clear_beggining.setToolTip(self.getl("def_editor_btn_clear_tt"))
        self.btn_clear_output.setText(self.getl("def_editor_btn_clear_text"))
        self.btn_clear_output.setToolTip(self.getl("def_editor_btn_clear_tt"))

        self.btn_edit_output.setText(self.getl("def_editor_btn_edit_output_text"))
        self.btn_edit_output.setToolTip(self.getl("def_editor_btn_edit_output_tt"))
        
        self.btn_edit_replace.setText(self.getl("def_editor_btn_edit_replace_text"))
        self.btn_edit_replace.setToolTip(self.getl("def_editor_btn_edit_replace_tt"))
        self.btn_edit_replace_add.setText(self.getl("def_editor_btn_edit_replace_add_text"))
        self.btn_edit_replace_add.setToolTip(self.getl("def_editor_btn_edit_replace_add_tt"))
        self.btn_edit_add_beg.setText(self.getl("def_editor_btn_edit_add_beg_text"))
        self.btn_edit_add_beg.setToolTip(self.getl("def_editor_btn_edit_add_beg_tt"))
        self.btn_edit_add_end.setText(self.getl("def_editor_btn_edit_add_end_text"))
        self.btn_edit_add_end.setToolTip(self.getl("def_editor_btn_edit_add_end_tt"))
        self.btn_edit_spaces.setText(self.getl("def_editor_btn_edit_spaces_text"))
        self.btn_edit_spaces.setToolTip(self.getl("def_editor_btn_edit_spaces_tt"))
        self.btn_edit_case.setText(self.getl("def_editor_btn_edit_case_text"))
        self.btn_edit_case.setToolTip(self.getl("def_editor_btn_edit_case_tt"))

        self.chk_edit_case.setText(self.getl("def_editor_chk_edit_case_text"))
        self.chk_edit_case.setToolTip(self.getl("def_editor_chk_edit_case_tt"))

        self.lbl_edit_replace.setText(self.getl("def_editor_lbl_edit_replace_text"))
        self.lbl_edit_replace.setToolTip(self.getl("def_editor_lbl_edit_replace_tt"))
        self.lbl_edit_with.setText(self.getl("def_editor_lbl_edit_with_text"))
        self.lbl_edit_with.setToolTip(self.getl("def_editor_lbl_edit_with_tt"))
        self.lbl_edit_in_string.setText(self.getl("def_editor_lbl_edit_in_string_text"))
        self.lbl_edit_in_string.setToolTip(self.getl("def_editor_lbl_edit_in_string_tt"))
        self.lbl_edit_add_beg.setText(self.getl("def_editor_lbl_edit_add_beg_text"))
        self.lbl_edit_add_beg.setToolTip(self.getl("def_editor_lbl_edit_add_beg_tt"))
        self.lbl_edit_add_end.setText(self.getl("def_editor_lbl_edit_add_end_text"))
        self.lbl_edit_add_end.setToolTip(self.getl("def_editor_lbl_edit_add_end_tt"))
        self.lbl_edit_msg.setText("")
        self.lbl_msg_spaces.setText("")

        self.txt_edit_replace.setToolTip(self.getl("def_editor_txt_edit_replace_tt"))
        self.txt_edit_with.setToolTip(self.getl("def_editor_txt_edit_with_tt"))
        self.txt_edit_in_string.setToolTip(self.getl("def_editor_txt_edit_in_string_tt"))
        self.txt_edit_add_beg.setToolTip(self.getl("def_editor_txt_edit_add_beg_tt"))
        self.txt_edit_add_end.setToolTip(self.getl("def_editor_txt_edit_add_end_tt"))

    def app_setting_updated(self, data: dict):
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()

        self.lbl_title.setStyleSheet(self.getv("def_editor_lbl_title_stylesheet"))
        self.lbl_base.setStyleSheet(self.getv("def_editor_lbl_base_stylesheet"))
        self.lbl_output.setStyleSheet(self.getv("def_editor_lbl_output_stylesheet"))

        self.txt_base.setStyleSheet(self.getv("def_editor_txt_base_stylesheet"))
        self.txt_end.setStyleSheet(self.getv("def_editor_txt_end_stylesheet"))
        self.txt_beggining.setStyleSheet(self.getv("def_editor_txt_beggining_stylesheet"))
        self.txt_output.setStyleSheet(self.getv("def_editor_txt_output_stylesheet"))

        self.btn_cancel.setStyleSheet(self.getv("def_editor_btn_cancel_stylesheet"))
        self.btn_clear_base.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_clear_end.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_clear_beggining.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_clear_output.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_first_letter.setStyleSheet(self.getv("def_editor_btn_first_letter_stylesheet"))
        self.btn_switch_words_order.setStyleSheet(self.getv("def_editor_btn_switch_words_order_stylesheet"))
        self.btn_generate.setStyleSheet(self.getv("def_editor_btn_generate_stylesheet"))
        self.btn_generate.setEnabled(False)
        self.btn_copy.setStyleSheet(self.getv("def_editor_btn_copy_stylesheet"))
        self.btn_copy.setEnabled(False)

        self.chk_add_end.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_add_beggining.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_first_up.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_add_base.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_combo_add.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_combo_prev.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_remember.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))
        self.chk_auto_show.setStyleSheet(self.getv("def_editor_checkboxes_stylesheet"))

        self.btn_edit_output.setStyleSheet(self.getv("def_editor_btn_edit_output_stylesheet"))
        
        self.btn_edit_replace.setStyleSheet(self.getv("def_editor_btn_edit_replace_stylesheet"))
        self.btn_edit_replace.setEnabled(False)
        self.btn_edit_replace_add.setStyleSheet(self.getv("def_editor_btn_edit_replace_add_stylesheet"))
        self.btn_edit_replace_add.setEnabled(False)
        self.btn_edit_add_beg.setStyleSheet(self.getv("def_editor_btn_edit_add_beg_stylesheet"))
        self.btn_edit_add_beg.setEnabled(False)
        self.btn_edit_add_end.setStyleSheet(self.getv("def_editor_btn_edit_add_end_stylesheet"))
        self.btn_edit_add_end.setEnabled(False)
        self.btn_edit_spaces.setStyleSheet(self.getv("def_editor_btn_edit_spaces_stylesheet"))
        self.btn_edit_close.setStyleSheet(self.getv("def_editor_btn_edit_close_stylesheet"))
        self.btn_edit_case.setStyleSheet(self.getv("def_editor_btn_edit_case_stylesheet"))

        self.chk_edit_case.setStyleSheet(self.getv("def_editor_chk_edit_case_stylesheet"))

        self.lbl_edit_replace.setStyleSheet(self.getv("def_editor_lbl_edit_replace_stylesheet"))
        self.lbl_edit_with.setStyleSheet(self.getv("def_editor_lbl_edit_with_stylesheet"))
        self.lbl_edit_in_string.setStyleSheet(self.getv("def_editor_lbl_edit_in_string_stylesheet"))
        self.lbl_edit_add_beg.setStyleSheet(self.getv("def_editor_lbl_edit_add_beg_stylesheet"))
        self.lbl_edit_add_end.setStyleSheet(self.getv("def_editor_lbl_edit_add_end_stylesheet"))
        self.lbl_edit_msg.setStyleSheet(self.getv("def_editor_lbl_edit_msg_stylesheet"))
        self.lbl_msg_spaces.setStyleSheet(self.getv("def_editor_lbl_msg_spaces_stylesheet"))

        self.txt_edit_replace.setStyleSheet(self.getv("def_editor_txt_edit_replace_stylesheet"))
        self.txt_edit_with.setStyleSheet(self.getv("def_editor_txt_edit_with_stylesheet"))
        self.txt_edit_in_string.setStyleSheet(self.getv("def_editor_txt_edit_in_string_stylesheet"))
        self.txt_edit_add_beg.setStyleSheet(self.getv("def_editor_txt_edit_add_beg_stylesheet"))
        self.txt_edit_add_end.setStyleSheet(self.getv("def_editor_txt_edit_add_end_stylesheet"))

        self.frm_edit.move(310, 140)
        self.frm_edit.setVisible(False)

        self.frm_variant.setVisible(False)
        self.frm_variant_pre.setVisible(False)
        self.lst_variant.setMouseTracking(True)

        if self.get_valid_clipboard_text():
            self.btn_clip_content.setText("Clipboard:\n" + self.get_valid_clipboard_text())
            self.btn_clip_content.setVisible(True)
        else:
            self.btn_clip_content.setVisible(False)

    def _define_definition_win_apperance(self):
        self.setStyleSheet(self.getv("definition_editor_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("definition_editor_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(self.getl("definition_editor_win_title_text"))
        self.setFixedSize(770, 470)


class ImageThumbItem(QLabel):
    def __init__(self, settings: settings_cls.Settings, parent_widget, media_id: int, definition_id: int, *args, **kwargs):
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
        self._definition_id =  definition_id
        self._is_default = self._am_i_default()
        self.img_src = None

        self._setup_label()

    def _am_i_default(self) -> bool:
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        if db_def.default_media_id is not None:
            if db_def.default_media_id == self._media_id:
                return True
            else:
                return False
        else:
            return False

    def you_are_default(self, is_this_true: bool = True) -> None:
        if is_this_true:
            self.setFrameShape(1)
            self.setFrameShadow(32)
            self.setLineWidth(2)
            self.setMidLineWidth(2)
        else:
            self.setFrameShape(0)
            self.setFrameShadow(16)
            self.setLineWidth(0)
            self.setMidLineWidth(0)

    def _setup_label(self):
        db_media = db_media_cls.Media(self._stt, self._media_id)
        self.img_src = db_media.media_http
        img = QPixmap(db_media.media_file)
        self.setFixedSize(self.getv("definition_image_thumb_size"), self.getv("definition_image_thumb_size"))
        size = self.maximumSize()
        if img.height() > size.height() or img.width() > size.width():
            img = img.scaled(size, Qt.KeepAspectRatio)
        self.setPixmap(img)
        self.setToolTip(f'<img src="{os.path.abspath(db_media.media_file)}" width=300>')

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._parent_widget.item_double_click_event(self._media_id, self._am_i_default(), self)
        return super().mouseDoubleClickEvent(a0)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.RightButton:
            self._parent_widget.item_right_click_event(self._media_id, self._am_i_default(), self)
        elif ev.button() == Qt.LeftButton:
            self._parent_widget.item_left_click_event(self._media_id, self._am_i_default(), self)
        return super().mousePressEvent(ev)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        self.setParent(None)
        self.deleteLater()


class AddDefinition(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_obj, expression: str = "", definition_id: int = 0, application_modal: bool = False, crash_dict: dict = None, *args, **kwargs):
        self._dont_clear_menu = False
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_obj, *args, **kwargs)
        
        UTILS.LogHandler.add_log_record("#1: Dialog is about to start.", ["AddDefinition"])

        if application_modal:
            self.setWindowModality(Qt.ApplicationModal)

        # Define other variables
        self._parent_obj = parent_obj
        self._expression = expression
        self._definition_id = definition_id
        self._data_changed = False
        # self._illegal_entry = False
        self._checking_in_progress = False
        self._syn_text = ""
        self._txt_desc_mark_mode = False
        self._txt_syn_mark_mode = False
        self._text_handler_working = False
        self._clip: utility_cls.Clipboard = self.get_appv("cb")
        self._menu_event_completed = False
        self._force_exit = False
        self._title_and_chk_box_text = []

        self.sound_image_added = UTILS.SoundUtility(self.getv("def_add_auto_added_image_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_image_add_error = UTILS.SoundUtility(self.getv("def_add_auto_added_image_error_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_auto_image_on = UTILS.SoundUtility(self.getv("def_add_auto_added_image_on_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_auto_image_off = UTILS.SoundUtility(self.getv("def_add_auto_added_image_off_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_auto_image_maximum = UTILS.SoundUtility(self.getv("def_add_auto_added_image_maximum_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_pop_up = UTILS.SoundUtility(self.getv("notification_pop_up_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_completed = UTILS.SoundUtility(self.getv("completed_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self.sound_select = UTILS.SoundUtility(self.getv("select_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))

        db_def = db_definition_cls.Definition(self._stt)
        self.exp_list = db_def.get_list_of_all_expressions()

        # Load GUI
        uic.loadUi(self.getv("definition_add_ui_file_path"), self)

        self.setEnabled(False)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self.show()
        QCoreApplication.processEvents()
        self.frm_loading.setVisible(True)
        self.horizontalLayout.addWidget(self.frm_loading)
        self.frm_loading.repaint()
        QCoreApplication.processEvents()

        self._char_format_syn = self.txt_syn.textCursor().charFormat()
        
        self._synonyms_hint = SynonymHint(self._stt, self, self.txt_syn)

        self._text_handler = text_handler_cls.TextHandler(self._stt, self.txt_desc, self, exec_when_check_def=("AddDefinition txt_desc", self))
        self._text_handler_syn = text_handler_cls.TextHandler(self._stt, self.txt_syn, self, exec_when_check_def=("AddDefinition txt_syn", self))

        self._desc_cf = self.txt_desc.textCursor().charFormat()

        self.load_widgets_handler()

        # self.show()
        # QCoreApplication.processEvents()

        # Check if multiple definitions for expression exist
        check_expression = self._definition_id_for_expression(self._expression)
        if check_expression:
            if len(check_expression) == 1:
                UTILS.LogHandler.add_log_record("#1: Found requested definition. (ID=#2)", ["AddDefinition", check_expression[0]])
                self._expression = self._get_definition_name(check_expression[0])
            else:
                UTILS.LogHandler.add_log_record("#1: Multiple definitons matched requested expression (Expression=#2).\nContext menu #3 is shown.", ["AddDefinition", self._expression, "User Select Definition"])
                result = self.user_select_definition(check_expression)
                if result:
                    UTILS.LogHandler.add_log_record("#1: User selected definition (#2).", ["AddDefinition", result])
                    self._expression = self._get_definition_name(result)
                else:
                    UTILS.LogHandler.add_log_record("#1: User canceled contex menu.\nAdding new definition is started", ["AddDefinition"])
                    self._expression = ""
        else:
            if self._expression and self._expression[0] != self._expression[0].upper():
                self._expression = self._expression.capitalize()


        # self.frm_loading.setVisible(True)
        # self.horizontalLayout.addWidget(self.frm_loading)
        # QCoreApplication.processEvents()
        self._populate_widgets()
        self._update_syn_img_counter()
        self._txt_syn_text_changed()
        self.frm_loading.setVisible(False)
        self._syn_text = self.txt_syn.toPlainText()
        self._define_labels_apperance(self.lbl_title, "definition_add_title")

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)
        self.keyPressEvent = self._key_press
        self.txt_expression.textChanged.connect(self._txt_expression_text_changed)
        self.txt_expression.returnPressed.connect(self._txt_expression_return_pressed)
        self.txt_desc.textChanged.connect(self._txt_desc_text_changed)
        self.txt_desc.mouseDoubleClickEvent = self._txt_desc_double_click
        self.txt_desc.mouseMoveEvent = self._txt_desc_mouse_move
        self.txt_syn.textChanged.connect(self._txt_syn_text_changed)
        self.txt_syn.mouseReleaseEvent = self.txt_syn_mouse_release
        self.txt_syn.mouseMoveEvent = self._txt_syn_mouse_move
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_add_media.clicked.connect(self._btn_add_media_click)
        self.btn_save.mouseReleaseEvent = self.btn_save_mouse_release
        self.btn_editor.clicked.connect(self._btn_editor_click)
        self.btn_format_desc.clicked.connect(self._btn_format_desc_click)
        self.chk_auto_add.stateChanged.connect(self.chk_auto_add_state_changed)
        self.btn_syn_find.clicked.connect(self._btn_syn_find_click)
        self.area.mousePressEvent = self.area_mouse_press
        self.btn_auto_add_stop.clicked.connect(self.btn_auto_add_stop_click)
        self.get_appv("clipboard").changed.connect(self._clipboard_changed)
        self.get_appv("signal").signalCloseAllDefinitions.connect(self._signal_close_all_definitions)
        self.get_appv("signal").signalNewDefinitionAdded.connect(self.signalNewDefinitionAdded_event)
        self.setEnabled(True)

        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["AddDefinition"])
        if crash_dict:
            UTILS.LogHandler.add_log_record("#1: Application #2 reports unfinished definition adding in last session.\nAttempting to restore entry from last session.", ["AddDefinition", "Crash service"], variables=[[crash_key, crash_item] for crash_key, crash_item in crash_dict.items()], warning_raised=True)
            self._load_crash_data(crash_dict)
            UTILS.LogHandler.add_log_record("#1: Loaded data from last session.", ["AddDefinition"])
        else:
            self.txt_expression.setFocus()
            self.exec_()

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

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        txt_expression = self.widget_handler.add_TextBox(self.txt_expression, {"allow_bypass_key_press_event": True})
        txt_expression.properties.key_pressed_change_stylesheet_enabled = False
        txt_expression.properties.smart_parenthesis_change_stylesheet_enabled = False
        txt_expression.properties.key_pressed_change_size_enabled = False
        txt_expression.properties.smart_parenthesis_change_size_enabled = False

        self.widget_handler.add_TextBox(self.txt_syn, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_Selection_Widget(self.chk_auto_add)

        self.widget_handler.activate()

    def _btn_syn_find_click(self):
        UTILS.LogHandler.add_log_record("#1: User triggered #2 for expression #3.", ["AddDefinition", "DefinitionFinder", self.txt_expression.text()])
        images = []
        for i in range(self.horizontalLayout.count()):
            img_src = self.horizontalLayout.itemAt(i).widget().img_src
            images.append(img_src)

        definition_data_find_cls.DefinitionFinder(parent_widget=self, 
                                                  settings=self._stt, 
                                                  search_string=self.txt_expression.text(), 
                                                  syn_list=self.txt_syn.toPlainText(),
                                                  image_list=images,
                                                  update_def_function=self.definition_update_function,
                                                  caller_class_id=id(self))

    def definition_update_function(self, data: dict):
        if data["caller_id"] != id(self):
            UTILS.TerminalUtility.WarningMessage("#1 returned invalid #2 (id(self)=#3)(ReturedID=#4)", ["DefinitionFinder", "caller_id", id(self), data.get("caller_id")])
            return
        
        # Text
        if data.get("update_text", None):
            if data["text"]:
                self.txt_desc.setPlainText(data["text"])
                UTILS.LogHandler.add_log_record("#1: Definition description is updated by #2.", ["AddDefinition", "DefinitionFinder"], variables=[["Text returned", data["text"]]])

        # Images
        if data.get("update_images", None):
            UTILS.LogHandler.add_log_record("#1: About to update images by #2.", ["AddDefinition", "DefinitionFinder"])
            if data["replace_images"]:
                # Delete existing images
                for _ in range(self.horizontalLayout.count()):
                    item = self.horizontalLayout.itemAt(0)
                    item.widget().close()
                    item.widget().deleteLater()
                    self.horizontalLayout.removeItem(item)
                UTILS.LogHandler.add_log_record("#1: Existing images cleared by #2.", ["AddDefinition", "DefinitionFinder"])

            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_working_text"))
            QCoreApplication.processEvents()
            silent_add = utility_cls.SilentPictureAdd(self._stt)

            not_added_images = ""

            for image in data["images"]:
                UTILS.LogHandler.add_log_record("#1: Attempting to add new image to definition by #2.\n#3", ["AddDefinition", "DefinitionFinder", image])
                result = silent_add.add_image(source=image)
                if result:
                    if self._is_media_already_added(result):
                        UTILS.LogHandler.add_log_record("#1: Image already exist in definition. Adding skipped.\n#3", ["AddDefinition", "DefinitionFinder", image])
                        self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                        continue

                    self._add_image_to_layout(result)
                    self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                    self.sound_image_added.play()
                    UTILS.LogHandler.add_log_record("#1: Image added to definition by #2.\n#3", ["AddDefinition", "DefinitionFinder", image])
                else:
                    self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                    not_added_images += f"{image}\n"
                    UTILS.LogHandler.add_log_record("#1: Unable to add image to definition by #2.\n#3", ["AddDefinition", "DefinitionFinder", image])

                if not_added_images:
                    UTILS.LogHandler.add_log_record("#1: Some images could not be added to definition.\n#2", ["AddDefinition", not_added_images])
                    QMessageBox.warning(self, self.getl("definition_add_error_online_img_add_title"), self.getl("definition_add_error_online_img_add_text") + f"\n{not_added_images}")
                
        # Synonyms
        if data.get("update_syn", None):
            text = ""
            if data["append_syn"]:
                text = self.txt_syn.toPlainText() + "\n\n"
            text += data["syn"]
            self.txt_syn.setPlainText(text)
            UTILS.LogHandler.add_log_record("#1: Definition synonyms updated by #2.", ["AddDefinition", "DefinitionFinder"], variables=[["Synonym list", text]])

        # Return data
        if data.get("return_data", None):
            images = []
            for i in range(self.horizontalLayout.count()):
                img_src = self.horizontalLayout.itemAt(i).widget().img_src
                images.append(img_src)
            UTILS.LogHandler.add_log_record("#1: Updated #2 data.", ["AddDefinition", "DefinitionFinder"])
            return self.txt_syn.toPlainText(), images

        self.sound_auto_image_on.play()

    def user_select_definition(self, def_list: list) -> int:
        items = []
        db_def = db_definition_cls.Definition(self._stt)
        for def_id in def_list:
            result =  db_def.load_definition(def_id)
            if result:
                item_text = f"{db_def.definition_id}, {db_def.definition_name}             "
                if len(db_def.definition_description) > 50:
                    item_desc = db_def.definition_description[:50].replace('\n', ' ')
                    item_text += f"[ {item_desc}... ]"
                else:
                    item_desc = db_def.definition_description.replace('\n', ' ')
                    item_text += f"[ {item_desc} ]"
                
                items.append([db_def.definition_id, item_text, "", True, [], None])

        menu_dict = {
            "position": self.mapToGlobal(QPoint(self.txt_expression.pos().x(), self.txt_expression.pos().y() + self.txt_expression.height())),
            "items": items
        }
        self.set_appv("menu", menu_dict)

        self._dont_clear_menu = True
        QCoreApplication.processEvents()
        self.sound_pop_up.play()
        utility_cls.ContextMenu(self._stt, self)
        if self.get_appv("menu")["result"]:
            return self.get_appv("menu")["result"]
        else:
            return None

    def txt_syn_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            cursor = self.txt_syn.cursorForPosition(e.pos())
            cur = self.txt_syn.textCursor()
            if not cur.hasSelection():
                cur.setPosition(cursor.position())
                self.txt_syn.setTextCursor(cur)
            UTILS.LogHandler.add_log_record("#1: Synonyms TextBox context menu triggered.", ["AddDefinition"])
            self._dont_clear_menu = True
            result = self._synonyms_hint.show_contex_menu(base_string=self.txt_expression.text())
            if result:
                self._dont_clear_menu = True
                utility_cls.MessageInformation(self._stt, self, result, app_modal=True)
        QTextEdit.mouseReleaseEvent(self.txt_syn, e)

    def signalNewDefinitionAdded_event(self):
        UTILS.LogHandler.add_log_record("#1: Signal #2 recieved.", ["AddDefinition", "NewDefinitionAdded"])
        
        # Comented code is handled by TextHandler !!!

        # db_def = db_definition_cls.Definition(self._stt)
        # self.exp_list = db_def.get_list_of_all_expressions()

        # self._change_widgets_if_illegal_entry()

        # if self.txt_desc.toPlainText():
        #     self._txt_desc_text_changed()
        UTILS.LogHandler.add_log_record("#1: Current definition data updated.", ["AddDefinition"])

    def _load_crash_data(self, crash_dict: dict):
        self._data_changed = True
        data_dict = {
            "title": self.getl("def_add_crash_msg_title"),
            "text": self.getl("def_add_crash_msg_text")
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, data_dict=data_dict, app_modal=False)
        QCoreApplication.processEvents()

        self.txt_expression.setText(crash_dict[self.get_appv("user").username]["def"]["name"])
        self.txt_syn.setText(crash_dict[self.get_appv("user").username]["def"]["syn"])
        self.txt_desc.setText(crash_dict[self.get_appv("user").username]["def"]["desc"])
        for i in crash_dict[self.get_appv("user").username]["def"]["media"]:
            self._add_image_to_layout(i)
        QCoreApplication.processEvents()
        UTILS.LogHandler.add_log_record("#1: Definition data from previous session are recovered.", ["AddDefinition"])

    def _signal_close_all_definitions(self):
        UTILS.LogHandler.add_log_record("#1: Signal #2 is recieved.", ["AddDefinition", "CloseAllDefinitions"])
        self._force_exit = True
        self.close()

    def area_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton and self._menu_event_completed == False:
            disabled = []
            if not self._clip.number_of_images_in_clip:
                disabled.append(10)
            if self._clip.is_clip_empty():
                disabled.append(20)

            menu_dict = {
                "position": QCursor().pos(),
                "disabled": disabled,
                "items": [
                    [
                        10,
                        self.getl("image_menu_paste_clip_text"),
                        self._clip.get_tooltip_hint_for_images(),
                        True,
                        [],
                        self.getv("paste_icon_path")
                    ],
                    [
                        20,
                        self.getl("image_menu_clear_clipboard_text"),
                        self._clip.get_tooltip_hint_for_clear_clipboard(),
                        True,
                        [],
                        self.getv("clear_clipboard_icon_path")
                    ]
                ]
            }

            UTILS.LogHandler.add_log_record("#1: Definition images context menu is triggered.", ["AddDefinition"])
            self.set_appv("menu", menu_dict)
            self._dont_clear_menu = True
            utility_cls.ContextMenu(self._stt, self)

            if self.get_appv("menu")["result"] == 10:
                self._paste_images()
            elif self.get_appv("menu")["result"] == 20:
                self._clip.clear_clip()
            
            if self.horizontalLayout.count() == 0 and self.txt_desc.toPlainText() == "" and self.txt_syn.toPlainText() == "":
                self._data_changed = False
        
        self._menu_event_completed = False
        QScrollArea.mousePressEvent(self.area, e)

    def events(self, event_dict: dict):
        UTILS.LogHandler.add_log_record("#1: Function #2 is not implemented.", ["AddDefinition", "events"], warning_raised=True)
        pass

    def btn_save_mouse_release(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            menu_dict = {
                "position": QCursor.pos(),
                "selected": [10],
                "items": [
                    [10, self.getl("def_add_btn_save_menu_save_and_exit_text"), self.getl("def_add_btn_save_menu_save_and_exit_tt"), True, [], None],
                    [20, self.getl("def_add_btn_save_menu_save_and_no_exit_text"), self.getl("def_add_btn_save_menu_save_and_no_exit_tt"), True, [], None],
                ]
            }
            UTILS.LogHandler.add_log_record("#1: Right click on button #2.\nContext menu is triggered", ["AddDefinition", "Save"])
            self.set_appv("menu", menu_dict)
            self._dont_clear_menu = True
            utility_cls.ContextMenu(self._stt, self)
            result = self.get_appv("menu")["result"]
            if result == 10:
                UTILS.LogHandler.add_log_record("#1: User selected #2.", ["AddDefinition", "Save & Exit"])
                self._btn_save_click(close_dialog=True)
            elif result == 20:
                UTILS.LogHandler.add_log_record("#1: User selected #2.", ["AddDefinition", "Save & Don't Exit"])
                self._btn_save_click(close_dialog=False)
            else:
                UTILS.LogHandler.add_log_record("#1: User canceled menu.", ["AddDefinition"])
            
        elif e.button() == Qt.LeftButton:
            self._btn_save_click()
        else:
            QPushButton.mouseReleaseEvent(self.btn_save, e)

    def btn_auto_add_stop_click(self):
        UTILS.LogHandler.add_log_record("#1: User aborted #2.", ["AddDefinition", "AutoAddImages"])
        self._stop_adding_images = True

    def chk_auto_add_state_changed(self):
        if self.chk_auto_add.isChecked():
            self.sound_auto_image_on.play()
            UTILS.LogHandler.add_log_record("#1: User started #2.", ["AddDefinition", "AutoAddImages"])
        else:
            self.sound_auto_image_off.play()
            UTILS.LogHandler.add_log_record("#1: User stoped #2.", ["AddDefinition", "AutoAddImages"])

    def _clipboard_changed(self):
        if not self.chk_auto_add.isChecked():
            return

        if not self.chk_auto_add.isEnabled():
            self.sound_image_add_error.play()
            return

        if self.horizontalLayout.count() > self.getv("max_number_of_images_in_definition"):
            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_full_text"))
            self.chk_auto_add.setEnabled(False)
            self.chk_auto_add.setChecked(False)
            self.sound_auto_image_maximum.play()
            UTILS.LogHandler.add_log_record("#1: Maximum number of images reached (#2).", ["AddDefinition", self.getv("max_number_of_images_in_definition")], warning_raised=True)
            self._message_too_many_images()
            return

        self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_working_text"))
        QCoreApplication.processEvents()
        silent_add = utility_cls.SilentPictureAdd(self._stt)
        UTILS.LogHandler.add_log_record("#1: About to add image by #2.\nImage source: #3", ["AddDefinition", "AutoAddImages", silent_add.clipboard_image_source])
        result = silent_add.add_image()
        if result:
            if self._is_media_already_added(result):
                self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                self.get_appv("log").write_log(f"DefinitionAdd. An attempt is made to add an image that has already been added to the definition. Media ID: {result}")
                self.sound_image_add_error.play()
                UTILS.LogHandler.add_log_record("#1: Image is already added to definition. Canceled adding #2\nImage source: #3", ["AddDefinition", result, silent_add.clipboard_image_source])
                return
            self._add_image_to_layout(result)
            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
            self.sound_image_added.play()
            UTILS.LogHandler.add_log_record("#1: Image is added to definition by #2.\nImage source: #3", ["AddDefinition", "AutoAddImages", silent_add.clipboard_image_source])
        else:
            UTILS.LogHandler.add_log_record("#1: Unable to add image by #2.\nImage source: #3", ["AddDefinition", "AutoAddImages", silent_add.clipboard_image_source])
            if not self._multi_urls_add():
                self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                self.sound_image_add_error.play()
            else:
                self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))

    def _multi_urls_add(self, urls_text: str = None) -> bool:
        file_util = utility_cls.FileDialog()
        urls = None

        # Search for urls in text
        if urls_text is None:
            if self.get_appv("clipboard").mimeData().hasText():
                urls_text = self.get_appv("clipboard").text()
                urls = file_util.return_valid_urls_from_text(urls_text)
                if len(urls) < 2:
                    urls = None
        
        # Search for files in clipboard
        if not urls:
            if self.get_appv("clipboard").mimeData().hasUrls():
                urls = [x.toLocalFile() for x in self.get_appv("clipboard").mimeData().urls()]
                urls = file_util.get_valid_local_files(urls)
        
        # If no urls found, return False
        if not urls:
            return False
        
        # Show the user a selection dialog to select the images they want to add
        select_dict = {
            "title": self.getl("multi_urls_selection_title"),
            "multi-select": False,
            "checkable": True,
            "items": []
        }
        for url in urls:
            desc = f'<img src="{url}" width=300>'
            select_dict["items"].append([url, url, desc, False, False, []])
        
        self.sound_pop_up.play()
        UTILS.LogHandler.add_log_record("#1: Multiple images add selection dialog displayed. (Urls=#2)", ["AddDefinition", len(urls)], variables=[["Image source", url] for url in urls])
        utility_cls.Selection(self._stt, self, selection_dict=select_dict)
        urls = self.get_appv("selection")["result"]

        # If the user has not selected any image, return false
        if not urls:
            UTILS.LogHandler.add_log_record("#1: User did not select any image.", ["AddDefinition"])
            return False
        
        # Start adding images
        silent_add = utility_cls.SilentPictureAdd(self._stt)

        not_added = []
        max_img_reached = False
        self._stop_adding_images = False
        UTILS.LogHandler.add_log_record("#1: Adding user selected images started...", ["AddDefinition"])

        for idx, url in enumerate(urls):
            # Notify the user of progress
            msg = self.getl("multi_urls_user_msg_text").replace("#1", str(idx + 1)).replace("#2", str(len(urls)))
            self._multi_urls_add_user_msg(msg)
            QCoreApplication.processEvents()
            
            # If the user has stopped adding images, exit the loop
            if self._stop_adding_images:
                UTILS.LogHandler.add_log_record("#1: User aborted adding images!", ["AddDefinition"])
                break
            
            # Check if the maximum number of images has been reached
            if self.horizontalLayout.count() > self.getv("max_number_of_images_in_definition"):
                max_img_reached = True
                txt = f'{url}  {self.getl("auto_adding_images_not_added_reason_text")}: {self.getl("auto_adding_images_not_added_reason_max_reached_text")}'
                not_added.append(txt)
                continue

            result = silent_add.add_image(source=url)

            if result:
                # If the image has already been added, continue with the next image
                if self._is_media_already_added(result):
                    UTILS.LogHandler.add_log_record("#1: Image already exists in definition #2.", ["AddDefinition", url])
                    continue
                # Add image
                self._add_image_to_layout(result)
                self.sound_image_added.play()
                UTILS.LogHandler.add_log_record("#1: Image added #2.", ["AddDefinition", url])
            else:
                # In case of error, inform the user with a sound signal and continue with the next image
                txt = f'{url}  {self.getl("auto_adding_images_not_added_reason_text")}: {self.getl("auto_adding_images_not_added_reason_load_error_text")}'
                not_added.append(txt)
                self.sound_image_add_error.play()
                UTILS.LogHandler.add_log_record("#1: Image not added due to #2.\nImage source: #3", ["AddDefinition", "Load Error", url])

        # If the maximum number of images is reached, notify the user with a message
        if max_img_reached:
            UTILS.LogHandler.add_log_record("#1: Maximum number of images reached #2.", ["AddDefinition", self.getv("max_number_of_images_in_definition")])
            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_full_text"))
            self.chk_auto_add.setEnabled(False)
            self.chk_auto_add.setChecked(False)
            self.sound_auto_image_maximum.play()
            self._message_too_many_images()

        # Remove the progress frame
        self._multi_urls_add_user_msg(None)

        # If there are images that could not be added, show the user a list of those images
        if not_added:
            select_dict = {
                "title": self.getl("multi_urls_selection_not_added_title"),
                "multi-select": False,
                "checkable": False,
                "items": []
            }
            for url in not_added:
                desc = f'<img src="{url}" width=300>'
                select_dict["items"].append([url, url, desc, False, False, []])
            
            UTILS.LogHandler.add_log_record("#1: Some images could not be added.\n#2", ["AddDefinition", "\n".join(not_added)])
            self.sound_pop_up.play()
            utility_cls.Selection(self._stt, self, selection_dict=select_dict)

        UTILS.LogHandler.add_log_record("#1: Adding user selected images completed.", ["AddDefinition"])
        return True

    def _multi_urls_add_user_msg(self, message: str):
        if message:
            if not self._title_and_chk_box_text:
                self._title_and_chk_box_text = [self.lbl_title.text(), self.chk_auto_add.text()]

            self.lbl_title.setText(message)

            y = self.area.pos().y()
            if y < 0:
                y = 0
            h = self.frm_auto_add.height()
            w = self.area.width()
            btn_x = int((self.area.width() - self.btn_auto_add_stop.width()) / 2)
            if btn_x < 0:
                btn_x = 0
            # self.frm_auto_add.move(0, y)
            # self.frm_auto_add.resize(w, h)
            self.frm_auto_add.setFixedSize(w, h)
            self.lbl_auto_add_msg.resize(self.frm_auto_add.width(), self.lbl_auto_add_msg.height())
            self.btn_auto_add_stop.move(btn_x, self.btn_auto_add_stop.pos().y())

            self.lbl_auto_add_msg.setText(message)
            self.frm_auto_add.setVisible(True)
        else:
            if self._title_and_chk_box_text:
                self.lbl_title.setText(self._title_and_chk_box_text[0])
                self.chk_auto_add.setText(self._title_and_chk_box_text[1])
                self._title_and_chk_box_text = []

            self.frm_auto_add.setVisible(False)

    def _key_press(self, e: QtGui.QKeyEvent):
        if e.key() == Qt.Key_Escape:
            if self._data_changed:
                self.close()
            else:                
                e.accept()
                self.close()

    def _btn_editor_click(self):
        UTILS.LogHandler.add_log_record("#1: User click triggered #2", ["AddDefinition", "DefinitionEditor"])
        DefinitionEditor(self._stt, self, self.txt_expression.text())

    def _txt_expression_return_pressed(self):
        if self.txt_expression.text():
            new_id = self._definition_id_for_expression(self.txt_expression.text().lower())
            if new_id:
                if len(new_id) > 1:
                    result = self.user_select_definition(new_id)
                    if not result:
                        result = 0
                else:
                    result = new_id[0]

                self._definition_id = result
                self._expression = ""
                self.sound_image_added.play()
                self._populate_widgets()

    def _definition_id_for_expression(self, expression: str = None) -> int:
        if expression is None:
            expression = self._expression
        exp_list = self.exp_list
        result = []
        for item in exp_list:
            if item[0] == expression.lower():
                result.append(item[1])
        return result

    def _get_definition_name(self, def_id: int) -> str:
        db_def = db_definition_cls.Definition(self._stt, def_id=def_id)
        return db_def.definition_name

    def check_for_serbian_chars(self) -> bool:
        if not UTILS.TextUtility.get_text_lines_without_serbian_chars(self.txt_syn.toPlainText(), if_data_exist_add_string_at_end="\n", ignore_if_line_already_exist=True).strip():
            UTILS.LogHandler.add_log_record("#1: No uncleaned serbian characters found", ["AddDefinition"])
            return True

        msg_dict = {
            "title": self.getl("add_def_exit_msg_clean_serbian_title"),
            "text": self.getl("add_def_exit_msg_clean_serbian_text"),
            "position": "center",
            "pos_center": False,
            "icon_path": self.getv("srpsko_slovo_c_icon_path"),
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True],
            ]
        }
        UTILS.LogHandler.add_log_record("#1: Question dialog shown\n#2", ["AddDefinition", "Uncleaned serbian characters"])
        utility_cls.MessageQuestion(self._stt, self, msg_dict)
        if msg_dict["result"] == 10:
            UTILS.LogHandler.add_log_record("#1: User selected to save definition without cleaning serbian characters", ["AddDefinition"])
            return True
        
        UTILS.LogHandler.add_log_record("#1: User cancelled saving definition", ["AddDefinition"])
        return False

    def _btn_save_click(self, close_dialog: bool = True):
        if self.txt_expression.text().strip() == "":
            return
        
        if not self.check_for_serbian_chars():
            return

        UTILS.LogHandler.add_log_record("#1: Saving data started...", ["AddDefinition"])

        self.lbl_auto_add_msg.setText(self.getl("add_def_lbl_auto_add_msg_saving_text"))
        self.lbl_auto_add_msg.resize(self.lbl_auto_add_msg.width(), self.frm_auto_add.height())
        self.btn_auto_add_stop.setVisible(False)
        self.frm_auto_add.setVisible(True)
        QCoreApplication.processEvents()

        self.txt_syn.setText(self.txt_syn.toPlainText() + "\n")
        self._change_widgets_if_illegal_entry()

        # Find media IDs
        media_ids = []
        default_item = None
        for i in range(self.horizontalLayout.count()):
            media_ids.append(self.horizontalLayout.itemAt(i).widget()._media_id)
            if self.horizontalLayout.itemAt(i).widget()._is_default:
                default_item = self.horizontalLayout.itemAt(i).widget()._media_id

        # Make similar expressions list
        syn_list = [x.strip() for x in self.txt_syn.toPlainText().split("\n") if x.strip() != ""]

        name = self.txt_expression.text()
        desc = self.txt_desc.toPlainText()

        # Create dictionary
        def_dict = {
            "name": name,
            "description": desc,
            "media_ids": media_ids,
            "synonyms": syn_list,
            "show": 1,
            "default": default_item
        }

        # Check if definition exist
        db_def = db_definition_cls.Definition(self._stt)
        definition_id = db_def.find_definition_by_name(name)

        # Save data
        if definition_id:
            definition = Definition(self._stt, def_id=definition_id)
            definition.DefName = name
            definition.DefDescription = desc
            definition.DefImages = media_ids
            definition.DefSynonyms = syn_list
            definition.DefDefaultImage = default_item
            if definition.can_be_saved():
                definition.save()
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2, cannot save definition ID = #3", ["AddDefinition", "_btn_save_click", definition_id], exception_raised=True)
                return
            UTILS.LogHandler.add_log_record("#1: Definition updated", ["AddDefinition"])
        else:
            definition = Definition(self._stt)
            definition.DefName = name
            definition.DefDescription = desc
            definition.DefImages = media_ids
            definition.DefSynonyms = syn_list
            definition.DefDefaultImage = default_item
            if definition.can_be_added():
                definition.add()
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2, cannot add definition.", ["AddDefinition", "_btn_save_click"], exception_raised=True)
                return
            UTILS.LogHandler.add_log_record("#1: Added new definition", ["AddDefinition"])

        self.get_appv("log").write_log(f"DefinitionAdd. Definition Saved. Definition ID: {def_dict['name']}")
        
        # Close dialog
        UTILS.LogHandler.add_log_record("#1: Sent signal #2", ["AddDefinition", "NewDefinitionAdded"])
        self.get_appv("text_handler_data").update_data()
        self.get_appv("signal").new_definition_added()
        self._data_changed = False

        self.lbl_auto_add_msg.resize(self.lbl_auto_add_msg.width(), 40)
        self.btn_auto_add_stop.setVisible(True)
        self.frm_auto_add.setVisible(False)

        UTILS.LogHandler.add_log_record("#1: Saving data completed.", ["AddDefinition"])
        if close_dialog:
            self._show_save_notification()
            self.close()
        else:
            self._show_save_notification(main_win=False)

    def _show_save_notification(self, main_win: bool = True):
        data_dict = {
            "title": self.getl("definition_add_save_notif_title"),
            "text": self.getl("definition_add_save_notif_text"),
            "timer": 3500
        }

        # self._dont_clear_menu = True
        if main_win:
            utility_cls.Notification(self._stt, self.get_appv("main_win"), data_dict)
        else:
            data_dict["position"] = "top_right"
            data_dict["animation"] = False
            utility_cls.Notification(self._stt, self, data_dict)
        # QCoreApplication.processEvents()

    def item_double_click_event(self, media_id: int, is_default: bool, item: QLabel):
        UTILS.LogHandler.add_log_record("#1: Image item #2", ["AddDefinition", "DoubleClicked"])
        self._show_images(item._media_id)

    def item_left_click_event(self, media_id: int, is_default: bool, item: QLabel):
        UTILS.LogHandler.add_log_record("#1: Image item #2 function #3", ["AddDefinition", "LeftClick", "NotImplemented"], warning_raised=True)
        pass

    def item_right_click_event(self, media_id: int, is_default: bool, item: QLabel):
        UTILS.LogHandler.add_log_record("#1: Image item #2, context menu showed.", ["AddDefinition", "RightClick"])
        if is_default:
            disabled = [10]
        else:
            disabled = []

        if not self._clip.number_of_images_in_clip:
            disabled.append(60)
        if self._clip.is_clip_empty():
            disabled.append(90)

        menu_dict = {
            "position": QCursor().pos(),
            "disabled": disabled,
            "separator": [10, 50],
            "items": [
                [
                    10,
                    self.getl("definition_media_item_menu_default_text"),
                    self.getl("definition_media_item_menu_default_tt"),
                    True,
                    [],
                    None
                ],
                [
                    20,
                    self.getl("definition_media_item_menu_remove_text"),
                    self.getl("definition_media_item_menu_remove_tt"),
                    True,
                    [],
                    None
                ],
                [
                    30,
                    self.getl("definition_media_item_menu_add_new_text"),
                    self.getl("definition_media_item_menu_add_new_tt"),
                    True,
                    [],
                    None
                ],
                [
                    40,
                    self.getl("definition_media_item_menu_view_text"),
                    self.getl("definition_media_item_menu_view_tt"),
                    True,
                    [],
                    None
                ],
                [
                    50,
                    self.getl("picture_view_menu_image_info_text"),
                    self.getl("picture_view_menu_image_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    60,
                    self.getl("image_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_images(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    70,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    80,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    90,
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
        utility_cls.ContextMenu(self._stt, self)
        self._menu_event_completed = True

        if self.get_appv("menu")["result"] == 10:
            for i in range(self.horizontalLayout.count()):
                self.horizontalLayout.itemAt(i).widget()._is_default = False
                self.horizontalLayout.itemAt(i).widget().you_are_default(False)
            item._is_default = True
            item.you_are_default()
            UTILS.LogHandler.add_log_record("#1: #2: Image with ID (#3) is set as default image.", ["AddDefinition", "User Selected", item._media_id])
        elif self.get_appv("menu")["result"] == 20:
            self.chk_auto_add.setEnabled(True)
            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
            for i in range(self.horizontalLayout.count()):
                if self.horizontalLayout.itemAt(i).widget()._media_id == item._media_id:
                    self.horizontalLayout.removeItem(self.horizontalLayout.itemAt(i))
                    break
            UTILS.LogHandler.add_log_record("#1: #2: Image with ID (#3) is removed from definition.", ["AddDefinition", "User Selected", item._media_id])
            item.close()
            self._update_syn_img_counter()
        elif self.get_appv("menu")["result"] == 30:
            UTILS.LogHandler.add_log_record("#1: #2: Add new image.", ["AddDefinition", "User Selected", item._media_id])
            self._btn_add_media_click()
        elif self.get_appv("menu")["result"] == 40:
            UTILS.LogHandler.add_log_record("#1: #2: Image with ID (#3) is displayed.", ["AddDefinition", "User Selected", item._media_id])
            self._show_images(item._media_id)
        elif self.get_appv("menu")["result"] == 50:
            UTILS.LogHandler.add_log_record("#1: #2: Image imformation for image with ID (#3) are displayed.", ["AddDefinition", "User Selected", item._media_id])
            utility_cls.PictureInfo(self._stt, self, item._media_id)
        elif self.get_appv("menu")["result"] == 60:
            UTILS.LogHandler.add_log_record("#1: #2: Paste images from clipboard.", ["AddDefinition", "User Selected"])
            self._paste_images()
        elif self.get_appv("menu")["result"] == 70:
            if self.chk_auto_add.isChecked():
                self.chk_auto_add.setChecked(False)
            self._clip.copy_to_clip(media_id)
            UTILS.LogHandler.add_log_record("#1: #2: Copy image to clipboard.", ["AddDefinition", "User Selected"])
        elif self.get_appv("menu")["result"] == 80:
            if self.chk_auto_add.isChecked():
                self.chk_auto_add.setChecked(False)
            self._clip.copy_to_clip(media_id, add_to_clip=True)
            UTILS.LogHandler.add_log_record("#1: #2: Add image to clipboard.", ["AddDefinition", "User Selected"])
        elif self.get_appv("menu")["result"] == 90:
            UTILS.LogHandler.add_log_record("#1: #2: Clear clipboard.", ["AddDefinition", "User Selected"])
            self._clip.clear_clip()
        else:
            UTILS.LogHandler.add_log_record("#1: #2: User canceled menu.", ["AddDefinition", "User Selected"])
        
        if self.horizontalLayout.count() == 0 and self.txt_desc.toPlainText() == "" and self.txt_syn.toPlainText() == "":
            self._data_changed = False

    def _paste_images(self):
        count = 0
        for i in self._clip.get_paste_images_ids():
            result = self._add_new_media(media_id=i)
            if result is True:
                count += 1
            if result == "limit":
                break
        ntf_dict = {
            "title": self.getl("paste_image_notification_title"),
            "text": self.getl("paste_image_notification_text").replace("#1", str(count)),
            "timer": 1000
        }
        self._dont_clear_menu = True
        utility_cls.Notification(self._stt, self, ntf_dict)

    def _show_images(self, media_id: int = None):
        media_ids = []
        for i in range(self.horizontalLayout.count()):
            media_ids.append(self.horizontalLayout.itemAt(i).widget()._media_id)
        if media_id:
            utility_cls.PictureView(self._stt, self, media_ids=media_ids, start_with_media_id=media_id)
        else:
            utility_cls.PictureView(self._stt, self, media_ids=media_ids)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _load_win_position(self):
        if "add_definition_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("add_definition_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def _btn_add_media_click(self):
        if self._clip.number_of_images_in_clip:
            menu_dict = {
                "position": QCursor().pos(),
                "items": [
                    [
                        10,
                        self.getl("definition_add_btn_add_media_text"),
                        self.getl("definition_add_btn_add_media_tt"),
                        True,
                        [],
                        self.getv("definition_add_btn_media_icon_path")
                    ],
                    [
                        20,
                        self.getl("image_menu_paste_clip_text"),
                        self._clip.get_tooltip_hint_for_images(),
                        True,
                        [],
                        self.getv("paste_icon_path")
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
            utility_cls.ContextMenu(self._stt, self)

            if self.get_appv("menu")["result"] == 10:
                self._add_new_media()
            elif self.get_appv("menu")["result"] == 20:
                self._paste_images()
            elif self.get_appv("menu")["result"] == 30:
                self._clip.clear_clip()
        else:
            self._add_new_media()

    def _add_new_media(self, media_id: int = None):
        if self.horizontalLayout.count() > self.getv("max_number_of_images_in_definition"):
            self._message_too_many_images()
            return "limit"
        if media_id:
            if self._is_media_already_added(media_id):
                return False
            self._add_image_to_layout(media_id)
            return True
        else:
            result = []
            utility_cls.PictureAdd(self._stt, self, result)
            if result:
                if self._is_media_already_added(result[0]):
                    self._message_image_exist()
                    return
                self._add_image_to_layout(result[0])

    def _is_media_already_added(self, media_id: int) -> bool:
        result = False
        for i in range(self.horizontalLayout.count()):
            if self.horizontalLayout.itemAt(i).widget()._media_id == media_id:
                result = True
                break
        return result

    def _add_image_to_layout(self, image_id: int):
        self._data_changed = True
        lbl_pic = ImageThumbItem(self._stt, self, image_id, self._definition_id)
        self.horizontalLayout.addWidget(lbl_pic)
        w = (self.getv("definition_image_thumb_size") + self.horizontalLayout.spacing()) * self.horizontalLayout.count() + 25
        self._widget.setFixedSize(w, self.getv("definition_image_thumb_size") + 10)
        self.area.setFixedHeight(self._widget.height() + 24)

        # Update crash dict
        media_ids = []
        for i in range(self.horizontalLayout.count()):
            media_ids.append(self.horizontalLayout.itemAt(i).widget()._media_id)

        crash_dict = self._stt.custom_dict_load(self.getv("crash_file_path"))
        if not crash_dict:
            crash_dict = {}
        if self.get_appv("user").username not in crash_dict:
            crash_dict[self.get_appv("user").username] = {}
        crash_dict[self.get_appv("user").username] = {
            "def": {
                "name": self.txt_expression.text(),
                "syn": self.txt_syn.toPlainText(),
                "desc": self.txt_desc.toPlainText(),
                "media": media_ids
            }
        }
        self._stt.custom_dict_save(self.getv("crash_file_path"), crash_dict)

        self._update_syn_img_counter()

    def _message_too_many_images(self):
        msg_dict = {
            "title": self.getl("definition_add_msg_img_limit_title"),
            "text": self.getl("definition_add_msg_img_limit_text")            
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_dict)

    def _message_image_exist(self):
        msg_dict = {
            "title": self.getl("definition_add_msg_img_exist_title"),
            "text": self.getl("definition_add_msg_img_exist_text")            
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_dict)

    def btn_cancel_click(self):
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not self._can_exit():
            a0.ignore()
            return None

        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "add_definition_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("add_definition_win_geometry", {}, save_to_file=True)

        g = self.get_appv("add_definition_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        self.chk_auto_add.setChecked(False)
        crash_dict = self._stt.custom_dict_load(self.getv("crash_file_path"))
        if not crash_dict:
            crash_dict = {}
        if self.get_appv("user").username in crash_dict:
            if "def" in crash_dict[self.get_appv("user").username]:
                crash_dict[self.get_appv("user").username].pop("def")
                self._stt.custom_dict_save(self.getv("crash_file_path"), crash_dict)

        self.get_appv("cm").remove_all_context_menu()

        if self._text_handler:
            self._text_handler.close_me()
            self._text_handler = None
        
        if self._text_handler_syn:
            self._text_handler_syn.close_me()
            self._text_handler_syn = None

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["AddDefinition"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _can_exit(self) -> bool:
        if self._force_exit:
            return True

        if self._data_changed:
            msg_dict = {
                "title": self.getl("add_def_exit_msg_save_title"),
                "text": self.getl("add_def_exit_msg_save_text"),
                "position": "center",
                "pos_center": False,
                "buttons": [
                    [10, self.getl("btn_yes"), "", None, True],
                    [20, self.getl("btn_no"), "", None, True],
                    [30, self.getl("btn_cancel"), "", None, True],
                ]
            }
            utility_cls.MessageQuestion(self._stt, self, msg_dict)
            if msg_dict["result"] != 10:
                return False
            return True
        return True

    def _txt_expression_text_changed(self):
        if self.txt_expression.text().find("\n") != -1:
            self.txt_expression.setText(self.txt_expression.text().replace("\n", ""))
            self.sound_image_add_error.play()

        self._change_widgets_if_def_exist()
        self._update_syn_img_counter()
            
        if not self._checking_in_progress:
            if self._change_widgets_if_illegal_entry():
                self.sound_auto_image_maximum.play()

    def _txt_syn_text_changed(self):
        if len(self.txt_syn.toPlainText()) - len(self._syn_text) != 0:
            self._data_changed = True
        if self.txt_desc.toPlainText() == "" and self.txt_syn.toPlainText() == "" and self.horizontalLayout.count() == 0:
            self._data_changed = False
        if not self._checking_in_progress:
            if self.txt_syn.toPlainText():
                title_text = self.lbl_title.text()
                title_stylesheet = self.lbl_title.styleSheet()
                self.lbl_title.setText(self.getl("definition_add_title_syn_update_text"))
                self.lbl_title.setStyleSheet(title_stylesheet + "background-color: rgb(255, 0, 0);")
                QCoreApplication.processEvents()

                if self.getv("definition_text_mark_enabled_in_def_add_dialog"):
                    self._checking_in_progress = True
                    self._text_handler_syn.check_definitions()
                    self._checking_in_progress = False

                # if self.txt_syn.toPlainText()[-1] == "\n":
                #     self._change_widgets_if_illegal_entry()
                # elif self.txt_syn.textCursor().position() != len(self.txt_syn.toPlainText()):
                #     self._change_widgets_if_illegal_entry()
                # elif abs(len(self.txt_syn.toPlainText()) - len(self._syn_text)) > 1:
                #     self._change_widgets_if_illegal_entry()
                
                self.lbl_title.setText(title_text)
                self.lbl_title.setStyleSheet(title_stylesheet)

                syn_count_before = len([x for x in self._syn_text.split("\n")])
                self._syn_text = self.txt_syn.toPlainText()
                syn_count_after = len([x for x in self._syn_text.split("\n")])

                self.syn_count_diff = syn_count_after - syn_count_before
                self._update_syn_img_counter(syn_count_added=self.syn_count_diff)

    def _update_syn_img_counter(self, syn_count_added: int = 0):
        syn_count = len([x for x in self.txt_syn.toPlainText().split("\n") if x.strip()])
        img_count = self.horizontalLayout.count()

        title = self.lbl_title.text()
        if title.find("[") != -1:
            if title.find("(") != -1 and syn_count_added == 0:
                syn_count_added = UTILS.TextUtility.get_integer(title[title.find("(") + 1: title.find(")")], on_error_return=0)
            title = title[:title.find("[")].strip() + " "
        else:
            title = title.strip() + " "

        title += f'[{self.getl("synonyms")} '
        if syn_count_added != 0:
            if syn_count_added > 0:
                title += f"(+{syn_count_added}) "
            else:
                title += f"({syn_count_added}) "
        title += f'= {syn_count}, {self.getl("images")} = {img_count})]'

        self.lbl_title.setText(title)
        self.lbl_title.repaint()

    def _change_widgets_if_illegal_entry(self) -> bool:
        self._checking_in_progress = True
        has_data_in_other_defs = False
        db_def = db_definition_cls.Definition(self._stt)
        def_id = db_def.find_definition_by_name(self.txt_expression.text(), populate_properties=True)
        expression_text = self.txt_expression.text().lower()
        if self.txt_expression.text():
            exp_lst = [x for x in self.exp_list if x[0] == expression_text]
            for item in exp_lst:
                if item[1] != def_id:
                    if item[0] == expression_text:
                        has_data_in_other_defs = True
                        self.txt_expression.setStyleSheet(self.getv("definition_txt_expr_part_of_other_def_stylesheet"))
                        break

        # if self.txt_syn.toPlainText():
        #     syn_list = [[x.strip(), x.strip().lower()] for x in self.txt_syn.toPlainText().split("\n") if len(x) != ""]
        #     ill_items = []
        #     for item in self.exp_list:
        #         if item[1] != def_id:
        #             for i in syn_list:
        #                 if i[1] == item[0]:
        #                     ill_items.append(i[0])
        #     cur_pos = self.txt_syn.textCursor().position()
        #     if ill_items:
        #         txt = self.txt_syn.toPlainText()
        #         for word in ill_items:
        #             start_pos = txt.find(word)
        #             while start_pos >= 0:
        #                 if txt[start_pos + len(word):start_pos + len(word) + 1] == "\n":
        #                     cur = self.txt_syn.textCursor()
        #                     cf = QTextCharFormat()
        #                     color = QColor()
        #                     # color.setNamedColor("red")
        #                     # cf.setBackground(color)
        #                     color.setNamedColor("#ff9c38")
        #                     cf.setForeground(color)
        #                     cur.setPosition(start_pos)
        #                     cur.movePosition(cur.Right, cur.KeepAnchor, len(word))
        #                     cur.setCharFormat(cf)
        #                     self.txt_syn.setTextCursor(cur)
        #                 start_pos = txt.find(word, start_pos + len(word))
        #     else:
        #         cur = self.txt_syn.textCursor()
        #         cur.setPosition(0)
        #         cur.movePosition(cur.Right, cur.KeepAnchor, len(self.txt_syn.toPlainText()))
        #         cur.setCharFormat(self._char_format_syn)
        #         self.txt_syn.setTextCursor(cur)

        #     cur = self.txt_syn.textCursor()
        #     cur.clearSelection()
        #     cur.setPosition(cur_pos)
        #     cur.setCharFormat(self._char_format_syn)
        #     self.txt_syn.setTextCursor(cur)

        if self.txt_expression.text():
            self.btn_add_media.setEnabled(True)
            self.btn_save.setEnabled(True)
        self._checking_in_progress = False

        return has_data_in_other_defs

    def _txt_desc_text_changed(self):
        if not self._text_handler:
            return
        
        if not self._txt_desc_mark_mode:
            if self.getv("definition_text_mark_enabled_in_def_add_dialog"):
                self._txt_desc_mark_mode = True
                data_changed = self._data_changed
                self._text_handler.check_definitions()
                self._data_changed = data_changed
                self._txt_desc_mark_mode = False

            self._mark_wiki_links(self.txt_desc.toPlainText())

        self._data_changed = True
        if self.txt_desc.toPlainText() == "" and self.txt_syn.toPlainText() == "" and self.horizontalLayout.count() == 0:
            self._data_changed = False

    def _txt_desc_mouse_move(self, e: QtGui.QMouseEvent) -> None:
        if self._text_handler:
            self._text_handler.show_definition_on_mouse_hover(e)
        QTextEdit.mouseMoveEvent(self.txt_desc, e)

    def _txt_syn_mouse_move(self, e: QtGui.QMouseEvent) -> None:
        if self._text_handler_syn:
            self._text_handler_syn.show_definition_on_mouse_hover(e)
        QTextEdit.mouseMoveEvent(self.txt_syn, e)

    def _btn_format_desc_click(self):
        UTILS.LogHandler.add_log_record("#1: User clicked #2.", ["AddDefinition", "Format Definition Description"])
        self.sound_select.play()
        QCoreApplication.processEvents()
        self.txt_desc.setText(self._clear_unnecessary_spaces(self.txt_desc.toPlainText()))
        self.txt_desc.setText(self._remove_wiki_from_text(self.txt_desc.toPlainText()))
        self.sound_completed.play()

    def _txt_desc_double_click(self, e):
        if self.getv("definition_add_remove_wiki_[]_from_description"):
            self.sound_select.play()
            QCoreApplication.processEvents()
            self.txt_desc.setText(self._clear_unnecessary_spaces(self.txt_desc.toPlainText()))
            self.txt_desc.setText(self._remove_wiki_from_text(self.txt_desc.toPlainText()))
            self.sound_completed.play()
        QTextEdit.mouseDoubleClickEvent(self.txt_desc, e)

    def _clear_unnecessary_spaces(self, txt: str) -> str:
        replace_map = [
            ["  ", " "],
            [" .", "."],
            [" ,", ","],
            [" ?", "?"],
            [" !", "!"],
            [" :", ":"],
            [" ;", ";"],
            [" )", ")"],
            ["( ", "("],
            ["\n ", "\n"],
            [" \n", "\n"],
            ["\n\n\n", "\n\n"],
            ["\t", " "]
        ]
        while True:
            can_exit = True
            for i in replace_map:
                if i[0] in txt:
                    txt = txt.replace(i[0], i[1])
                    can_exit = False
            if can_exit:
                break
        
        UTILS.LogHandler.add_log_record("#1: Unnecessary spaces cleared from definition description.", ["AddDefinition"])
        return txt

    def _remove_wiki_from_text(self, txt: str) -> str:
        items = self._find_wiki_links(txt)
        
        for i in items:
            txt = txt[:i[0]] + "`" * len(i[2]) + txt[i[1]:]
        
        txt = txt.replace("`", "")

        UTILS.LogHandler.add_log_record("#1: Wikipedia links removed from definition description.", ["AddDefinition"])
        return txt

    def _find_wiki_links(self, txt: str) -> list:
        start = 0
        result = []
        while start >= 0:
            start = txt.find("[", start)
            if start >= 0:
                end = txt.find("]", start)
                if end >= 0:
                    result.append((start, end + 1, txt[start:end + 1]))
                    start = end
                else:
                    start = -1
            
        return result

    def _mark_wiki_links(self, txt: str) -> None:
        self._txt_desc_mark_mode = True
        cf = QTextCharFormat()
        color = QColor(self.getv("diary_view_mark_search_string_fore_color"))
        cf.setForeground(color)
        color = QColor(self.getv("diary_view_mark_search_string_back_color"))
        cf.setBackground(color)
        pos = self.txt_desc.textCursor().position()
        # self.txt_desc.setText(txt)

        for i in self._find_wiki_links(txt):
            cur = self.txt_desc.textCursor()
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.setCharFormat(cf)
            self.txt_desc.setTextCursor(cur)
        cur = self.txt_desc.textCursor()
        cur.setPosition(pos)
        cur.setCharFormat(self._desc_cf)
        self.txt_desc.setTextCursor(cur)
        self._txt_desc_mark_mode = False

    def _populate_widgets(self):
        data_changed = self._data_changed
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        if self._definition_id:
            self.txt_expression.setText(db_def.definition_name)
            self.txt_desc.setText(db_def.definition_description)

            syn_list = db_def.get_definition_media_synonyms_names(self._definition_id)
            syn_text = ""
            if syn_list:
                syn_text = "\n".join(syn_list)
                syn_text = syn_text.strip() + "\n"
            self.txt_syn.setText(syn_text)

            self._populate_media(db_def.definition_media_ids)
        if self._expression:
            self.txt_expression.setText(self._expression)
            def_exist = db_def.find_definition_by_name(self._expression)
            if def_exist:
                if not self.txt_desc.toPlainText() and not self.txt_syn.toPlainText() and not self.horizontalLayout.count():
                    self._definition_id = def_exist
                    self.txt_desc.setText(db_def.definition_description)
                    
                    syn_list = db_def.get_definition_media_synonyms_names(self._definition_id)
                    syn_text = ""
                    if syn_list:
                        syn_text = "\n".join(syn_list)
                        syn_text = syn_text.strip() + "\n"
                    self.txt_syn.setText(syn_text)
                    
                    self._populate_media(db_def.definition_media_ids)

        self._change_widgets_if_def_exist()
        self._data_changed = data_changed
        self._txt_desc_text_changed()
        self._data_changed = False
        
    def _change_widgets_if_def_exist(self) -> int:
        data_changed = self._data_changed
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        def_exist = db_def.find_definition_by_name(self.txt_expression.text().lower())
        if def_exist:
            self.txt_expression.setStyleSheet(self.getv("definition_txt_expr_exist_stylesheet"))
            self.btn_save.setText(self.getl("definition_add_btn_update_text"))
            self.lbl_title.setText(self.getl("definition_edit_title_text"))
            self._definition_id = db_def.definition_id
            
            if self._data_changed:
                data_changed = False
            self.txt_desc.setText(db_def.definition_description)
            syn_list = db_def.get_definition_media_synonyms_names(self._definition_id)
            syn_text = ""
            if syn_list:
                syn_text = "\n".join(syn_list)
                syn_text = syn_text.strip() + "\n"
            self.txt_syn.setText(syn_text)
            self._populate_media(db_def.definition_media_ids)
        else:
            self.txt_expression.setStyleSheet(self.getv("definition_txt_expr_stylesheet"))
            self.btn_save.setText(self.getl("definition_add_btn_add_new_text"))
            self.lbl_title.setText(self.getl("definition_add_title_text"))
            self._definition_id = 0
            if not self._data_changed:
                self.txt_desc.setText("")
                self.txt_syn.setText("")
                self._populate_media([])
        if self._data_changed:
            self._data_changed = data_changed
        
        return def_exist
            
    def _populate_media(self, media_ids: list):
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        default_id = db_def.default_media_id

        for i in range(self.horizontalLayout.count()):
            widget = self.horizontalLayout.itemAt(0).widget()
            self.horizontalLayout.removeItem(self.horizontalLayout.itemAt(0))
            widget.close()

        if media_ids:
            for i in media_ids:
                lbl_pic = ImageThumbItem(self._stt, self, i, self._definition_id)
                self.horizontalLayout.addWidget(lbl_pic)
                if default_id == i:
                    lbl_pic.you_are_default()

        w = (self.getv("definition_image_thumb_size") + self.horizontalLayout.spacing()) * self.horizontalLayout.count() + 25
        self._widget.setFixedSize(w, self.getv("definition_image_thumb_size") + 10)
        self.area.setFixedHeight(self._widget.height() + 24)

        QCoreApplication.processEvents()

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.frm_syn: QFrame = self.findChild(QFrame, "frm_syn")
        self.btn_syn_find: QPushButton = self.findChild(QPushButton, "btn_syn_find")
        self.lbl_syn_pic: QLabel = self.findChild(QLabel, "lbl_syn_pic")
        self.txt_expression: QLineEdit = self.findChild(QLineEdit, "txt_expression")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.txt_syn: QTextEdit = self.findChild(QTextEdit, "txt_syn")
        self.btn_add_media: QPushButton = self.findChild(QPushButton, "btn_add_media")
        self.btn_save: QPushButton = self.findChild(QPushButton, "btn_save")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_editor: QPushButton = self.findChild(QPushButton, "btn_editor")
        self.btn_format_desc: QPushButton = self.findChild(QPushButton, "btn_format_desc")
        self.gridLayout: QGridLayout = self.findChild(QGridLayout, "gridLayout")
        self.frm_media: QFrame = self.findChild(QFrame, "frm_media")
        self.chk_auto_add: QCheckBox = self.findChild(QCheckBox, "chk_auto_add")

        self.frm_auto_add: QFrame = self.findChild(QFrame, "frm_auto_add")
        self.lbl_auto_add_msg: QLabel = self.findChild(QLabel, "lbl_auto_add_msg")
        self.btn_auto_add_stop: QPushButton = self.findChild(QPushButton, "btn_auto_add_stop")
        self.frm_auto_add.raise_()
        self.frm_auto_add.setVisible(False)

        self.frm_loading: QFrame = self.findChild(QFrame, "frm_loading")
        self.lbl_loading : QLabel = self.findChild(QLabel, "lbl_loading")

        self.setLayout(self.gridLayout)

        self.area: QScrollArea = self.findChild(QScrollArea, "area")
        self._widget: QWidget = QWidget()
        self.horizontalLayout: QHBoxLayout = QHBoxLayout()
        self._widget.setLayout(self.horizontalLayout)
        self.area.setWidget(self._widget)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.btn_syn_find.move(max(int((self.frm_syn.width() - self.btn_syn_find.width()) / 2), 5), max(5, self.frm_syn.height() - self.btn_syn_find.height() - 5))
        self.lbl_syn_pic.move(5, 5)
        self.lbl_syn_pic.resize(self.frm_syn.width() - 10, self.frm_syn.height() - 33)
        return super().resizeEvent(a0)

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("definition_add_win_title_text"))
        if self._definition_id:
            self.lbl_title.setText(self.getl("definition_edit_title_text"))
            self.lbl_title.setToolTip(self.getl("definition_edit_title_tt"))
        else:
            self.lbl_title.setText(self.getl("definition_add_title_text"))
            self.lbl_title.setToolTip(self.getl("definition_add_title_tt"))
        
        self.btn_syn_find.setText(self.getl("definition_add_btn_syn_find_text"))
        self.btn_syn_find.setToolTip(self.getl("definition_add_btn_syn_find_tt"))

        self.txt_expression.setPlaceholderText(self.getl("definition_add_expr_placeholder"))
        self.txt_expression.setToolTip(self.getl("definition_add_expr_tt"))

        self.txt_syn.setPlaceholderText(self.getl("definition_add_syn_placeholder"))
        self.txt_desc.setPlaceholderText(self.getl("definition_add_desc_placeholder"))

        self.btn_add_media.setText(self.getl("definition_add_btn_add_media_text"))
        self.btn_add_media.setToolTip(self.getl("definition_add_btn_add_media_tt"))
        self.btn_editor.setText(self.getl("definition_add_btn_editor_text"))
        self.btn_editor.setToolTip(self.getl("definition_add_btn_editor_tt"))
        self.btn_format_desc.setText(self.getl("definition_add_btn_format_desc_text"))
        self.btn_format_desc.setToolTip(self.getl("definition_add_btn_format_desc_tt"))
        self.btn_cancel.setText(self.getl("btn_cancel"))
        self.btn_save.setText(self.getl("btn_save"))

        self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
        self.chk_auto_add.setToolTip(self.getl("definition_add_chk_auto_add_tt"))

        self.lbl_loading.setText(self.getl("definition_add_lbl_loading_text"))
        self.lbl_loading.setToolTip(self.getl("definition_add_lbl_loading_tt"))

    def app_setting_updated(self, data: dict):
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()

        self.lbl_title.setText(self.getl("please_wait"))
        self.lbl_title.setStyleSheet("background-color: rgb(255, 0, 0);")
        # self._define_labels_apperance(self.lbl_title, "definition_add_title")
        
        self._define_buttons_apperance(self.btn_add_media, "definition_add_btn_media")
        self._define_buttons_apperance(self.btn_save, "definition_add_btn_save")
        self._define_buttons_apperance(self.btn_cancel, "definition_add_btn_cancel")
        self._define_buttons_apperance(self.btn_editor, "definition_add_btn_editor")
        self._define_buttons_apperance(self.btn_format_desc, "definition_add_btn_format_desc")
        
        self._define_text_box_apperance(self.txt_expression, "definition_txt_expr")
        self._define_text_box_apperance(self.txt_syn, "definition_txt_syn")
        self.txt_syn.setContextMenuPolicy(Qt.NoContextMenu)
        self._define_text_box_apperance(self.txt_desc, "definition_txt_desc")

        self.chk_auto_add.setStyleSheet(self.getv("definition_add_chk_auto_add_stylesheet"))

        self.lbl_loading.setStyleSheet(self.getv("definition_add_lbl_loading_stylesheet"))
        self.lbl_syn_pic.setScaledContents(True)

    def _define_definition_win_apperance(self):
        self.setStyleSheet(self.getv("definition_add_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("definition_add_win_icon_path")))
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


class ViewDefinition(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_obj, definition_id: int, *args, **kwargs):

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_obj, *args, **kwargs)

        # Define other variables
        self._parent_obj = parent_obj
        self._definition_id = definition_id
        self.drag_mode = None
        self.move_mode = None
        self._dont_clear_menu = False
        self._dont_show_menu = False
        self._media_id_displayed = None
        self._clip: utility_cls.Clipboard = self.get_appv("cb")

        self._db_def = db_definition_cls.Definition(self._stt, self._definition_id)

        # Load GUI
        uic.loadUi(self.getv("definition_view_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_size.mousePressEvent = self._btn_size_mouse_press
        self.btn_size.mouseReleaseEvent = self._btn_size_mouse_release
        self.btn_size.mouseMoveEvent = self._btn_size_mouse_move
        self.lbl_name.mousePressEvent = self.lbl_name_mouse_press
        self.lbl_name.mouseReleaseEvent = self.lbl_name_mouse_release
        self.lbl_name.mouseMoveEvent = self.lbl_name_mouse_move
        self.lbl_pic.mousePressEvent = self.lbl_name_mouse_press
        self.lbl_pic.mouseReleaseEvent = self.lbl_name_mouse_release
        self.lbl_pic.mouseMoveEvent = self.lbl_name_mouse_move
        self.lbl_pic.mouseDoubleClickEvent = self.lbl_pic_mouse_double_click

        self.btn_ok.clicked.connect(self._btn_ok_click)
        self.btn_edit.clicked.connect(self._btn_edit_click)
        self.btn_close.clicked.connect(self._btn_close_click)

        self.get_appv("signal").signalCloseAllDefinitions.connect(self._signal_close_all_definitions)

        self.show()
        self._populate_widgets()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["ViewDefinition"])
        self.exec_()

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_QPushButton(self.btn_close)
        self.widget_handler.add_QPushButton(self.btn_edit)
        self.widget_handler.add_QPushButton(self.btn_ok)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        self.widget_handler.activate()

    def _signal_close_all_definitions(self):
        UTILS.LogHandler.add_log_record("#1: Signal #2 recieved.", ["ViewDefinition", "CloseAllDefinitions"])
        self.close()

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _btn_close_click(self):
        self.close()

    def save_images(self):
        media_ids = []
        for i in range(self.horizontalLayout.count()):
            media_ids.append(self.horizontalLayout.itemAt(i).widget()._media_id)

        def_dict = {
            "media_ids": media_ids
        }

        self._db_def.update_definition(self._definition_id, def_dict=def_dict)
        UTILS.LogHandler.add_log_record("#1: Images Saved.", ["ViewDefinition"])

    def _btn_edit_click(self):
        UTILS.LogHandler.add_log_record("#1: Button #2 clicked.", ["ViewDefinition", "Edit Definitions"])
        AddDefinition(self._stt, self, definition_id=self._definition_id)
        self._db_def._populate_properties(self._definition_id)
        self._setup_widgets_text()
        self._populate_widgets()

    def _btn_ok_click(self):
        self.save_images()
        self.close()

    def lbl_name_mouse_press(self, x):
        if x.button() == Qt.LeftButton:
            self.move_mode = (QCursor().pos().x() - self.pos().x(), QCursor().pos().y() - self.pos().y())
        elif x.button() == Qt.RightButton:
            self.item_right_click_event(None, None, None, disabled_menu_items=[1,2,4,5])
    
    def lbl_name_mouse_release(self, x):
        self.move_mode = None

    def lbl_name_mouse_move(self, x):
        if self.move_mode:
            x = QCursor().pos().x() - self.move_mode[0]
            y = QCursor().pos().y() - self.move_mode[1]
            self.move(x, y)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self.move_mode = (QCursor().pos().x() - self.pos().x(), QCursor().pos().y() - self.pos().y())
        if a0.button() == Qt.RightButton:
            if not self.horizontalLayout.count():
                self.item_right_click_event(None, None, None, disabled_menu_items=[1,2,4,5])
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.move_mode = None
        return super().mouseReleaseEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.move_mode:
            x = QCursor().pos().x() - self.move_mode[0]
            y = QCursor().pos().y() - self.move_mode[1]
            self.move(x, y)
        return super().mouseMoveEvent(a0)

    def _btn_size_mouse_move(self, event):
        if self.drag_mode:
            self.drag_mode = [
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

    def _btn_size_mouse_press(self, event):
        self.drag_mode = [
            self.pos().x(),
            self.pos().y(),
            QCursor.pos().x(),
            QCursor.pos().y() ]
        
    def _btn_size_mouse_release(self, event):
        self.drag_mode = None

    def lbl_pic_mouse_double_click(self, e):
        if self._media_id_displayed:
            self._show_images(self._media_id_displayed)

    def item_double_click_event(self, media_id: int, is_default: bool, item: QLabel):
        self._show_images(item._media_id)

    def item_left_click_event(self, media_id: int, is_default: bool, item: QLabel):
        db_media = db_media_cls.Media(self._stt, media_id)
        self._media_id_displayed = media_id
        self._show_image_in_main_label(db_media.media_file)

    def item_right_click_event(self, media_id: int, is_default: bool, item: QLabel, disabled_menu_items: list = None):
        db_media = db_media_cls.Media(self._stt, media_id)
        if is_default:
            disabled = [1]
        else:
            disabled = []
        
        if disabled_menu_items:
            for i in disabled_menu_items:
                disabled.append(i)

        if not media_id:
            disabled.append(70)
            disabled.append(80)
        if self._clip.is_clip_empty():
            disabled.append(90)
            
        menu_dict = {
            "position": QCursor().pos(),
            "disabled": disabled,
            "separator": [1, 5],
            "items": [
                [
                    1,
                    self.getl("definition_media_item_menu_default_text"),
                    self.getl("definition_media_item_menu_default_tt"),
                    True,
                    [],
                    None
                ],
                [
                    2,
                    self.getl("definition_media_item_menu_remove_text"),
                    self.getl("definition_media_item_menu_remove_tt"),
                    True,
                    [],
                    None
                ],
                [
                    3,
                    self.getl("definition_media_item_menu_add_new_text"),
                    self.getl("definition_media_item_menu_add_new_tt"),
                    True,
                    [],
                    None
                ],
                [
                    4,
                    self.getl("definition_media_item_menu_view_text"),
                    self.getl("definition_media_item_menu_view_tt"),
                    True,
                    [],
                    None
                ],
                [
                    5,
                    self.getl("picture_view_menu_image_info_text"),
                    self.getl("picture_view_menu_image_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    70,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    80,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    90,
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
        utility_cls.ContextMenu(self._stt, self)

        if self.get_appv("menu")["result"] == 1:
            for i in range(self.horizontalLayout.count()):
                self.horizontalLayout.itemAt(i).widget()._is_default = False
                self.horizontalLayout.itemAt(i).widget().you_are_default(False)
            item._is_default = True
            item.you_are_default()
            self._db_def.set_new_default_media(item._media_id)
        elif self.get_appv("menu")["result"] == 2:
            for i in range(self.horizontalLayout.count()):
                if self.horizontalLayout.itemAt(i).widget()._media_id == item._media_id:
                    self.horizontalLayout.removeItem(self.horizontalLayout.itemAt(i))
                    w = (self.getv("definition_image_thumb_size") + self.horizontalLayout.spacing()) * self.horizontalLayout.count() + 25
                    self._widget.setFixedSize(w, self.getv("definition_image_thumb_size") + 10)
                    self.area.setFixedHeight(self._widget.height() + 24)
                    break
            item.close()
            if self.horizontalLayout.count():
                db_media = db_media_cls.Media(self._stt, self.horizontalLayout.itemAt(0).widget()._media_id)
                self._show_image_in_main_label(db_media.media_file)
            else:
                img = QPixmap()
                img.load(self.getv("definition_icon_path"))
                self.lbl_pic.setPixmap(img)

        elif self.get_appv("menu")["result"] == 3:
            self._add_media_cm()
        elif self.get_appv("menu")["result"] == 4:
            self._show_images(item._media_id)
        elif self.get_appv("menu")["result"] == 5:
            utility_cls.PictureInfo(self._stt, self, item._media_id)
        elif self.get_appv("menu")["result"] == 70:
            self._clip.copy_to_clip(media_id)
        elif self.get_appv("menu")["result"] == 80:
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif self.get_appv("menu")["result"] == 90:
            self._clip.clear_clip()

    def _add_media_cm(self):
        if self.horizontalLayout.count() > self.getv("max_number_of_images_in_definition"):
            UTILS.LogHandler.add_log_record("#1: Maximum number of images reached.", ["ViewDefinition"])
            self._message_too_many_images()
            return
        result = []
        UTILS.LogHandler.add_log_record("#1: Adding image...", ["ViewDefinition"])
        utility_cls.PictureAdd(self._stt, self, result)
        if result:
            for i in range(self.horizontalLayout.count()):
                if self.horizontalLayout.itemAt(i).widget()._media_id == result[0]:
                    self._message_image_exist()
                    UTILS.LogHandler.add_log_record("#1: Add Image canceled, image already exits in definition.", ["ViewDefinition"])
                    return
            self._data_changed = True
            lbl_pic = ImageThumbItem(self._stt, self, result[0], self._definition_id)
            self.horizontalLayout.addWidget(lbl_pic)

            w = (self.getv("definition_image_thumb_size") + self.horizontalLayout.spacing()) * self.horizontalLayout.count() + 25
            self._widget.setFixedSize(w, self.getv("definition_image_thumb_size") + 10)
            self.area.setFixedHeight(self._widget.height() + 24)
            
            db_media = db_media_cls.Media(self._stt, result[0])
            self._show_image_in_main_label(db_media.media_file)
            UTILS.LogHandler.add_log_record("#1: Image added.", ["ViewDefinition"])
        else:
            UTILS.LogHandler.add_log_record("#1: ImageAdd canceled.", ["ViewDefinition"])

    def _show_image_in_main_label(self, media_file: str = None):
            img = QPixmap()
            img.load(media_file)
            size = self.lbl_pic.maximumSize()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)

    def _message_too_many_images(self):
        msg_dict = {
            "title": self.getl("definition_add_msg_img_limit_title"),
            "text": self.getl("definition_add_msg_img_limit_text")            
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_dict)

    def _message_image_exist(self):
        msg_dict = {
            "title": self.getl("definition_add_msg_img_exist_title"),
            "text": self.getl("definition_add_msg_img_exist_text")            
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_dict)

    def _show_images(self, media_id: int = None):
        media_ids = []
        for i in range(self.horizontalLayout.count()):
            media_ids.append(self.horizontalLayout.itemAt(i).widget()._media_id)
        if media_id:
            utility_cls.PictureView(self._stt, self, media_ids=media_ids, start_with_media_id=media_id)
        else:
            utility_cls.PictureView(self._stt, self, media_ids=media_ids)

    def _populate_widgets(self, add_to_layout=True):
        if add_to_layout:
            for i in range(self.horizontalLayout.count()):
                widget = self.horizontalLayout.itemAt(0).widget()
                self.horizontalLayout.removeWidget(widget)
                widget.close()
        
        img = QPixmap()
        for i in self._db_def.definition_media_ids:
            lbl = ImageThumbItem(self._stt, self, i, self._definition_id)
            lbl.you_are_default(False)
            if self._db_def.default_media_id:
                if self._db_def.default_media_id == i:
                    db_media = db_media_cls.Media(self._stt, i)
                    img.load(db_media.media_file)
                    size = self.lbl_pic.maximumSize()
                    if img.height() > size.height() or img.width() > size.width():
                        img = img.scaled(size, Qt.KeepAspectRatio)
                    self.lbl_pic.setPixmap(img)
                    self._media_id_displayed = i
                    lbl.you_are_default()
            if add_to_layout:
                self.horizontalLayout.addWidget(lbl)

        if self._db_def.definition_media_ids and not self._db_def.default_media_id:
            default_id = self.horizontalLayout.itemAt(0).widget()._media_id
            db_media = db_media_cls.Media(self._stt, default_id)
            img.load(db_media.media_file)
            size = self.lbl_pic.maximumSize()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)

        w = (self.getv("definition_image_thumb_size") + self.horizontalLayout.spacing()) * self.horizontalLayout.count() + 25
        self._widget.setFixedSize(w, self.getv("definition_image_thumb_size") + 10)
        self.area.setFixedHeight(self._widget.height() + 24)
       
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.frame.setFixedSize(self.width(), self.height())
        self.lbl_pic.setFixedSize(int(self.contentsRect().width() * 0.45), int(self.contentsRect().width() * 0.45))
        if self.horizontalLayout.count() > 0:
            self._populate_widgets(add_to_layout=False)
        return super().resizeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["ViewDefinition"])
        self.get_appv("cm").remove_all_context_menu()

        for i in range(self.horizontalLayout.count()):
            widget = self.horizontalLayout.itemAt(0).widget()
            self.horizontalLayout.removeWidget(widget)
            widget.close_me()

        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.btn_ok: QPushButton = self.findChild(QPushButton, "btn_ok")
        self.btn_edit: QPushButton = self.findChild(QPushButton, "btn_edit")
        self.btn_size: QPushButton = self.findChild(QPushButton, "btn_size")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.gridLayout: QGridLayout = self.findChild(QGridLayout, "gridLayout")
        
        self.frame: QFrame = self.findChild(QFrame, "frame")

        self.frame.setLayout(self.gridLayout)

        self.area: QScrollArea = self.findChild(QScrollArea, "area")
        self._widget: QWidget = QWidget()
        self.horizontalLayout: QHBoxLayout = QHBoxLayout()
        self._widget.setLayout(self.horizontalLayout)
        self.area.setWidget(self._widget)

    def _setup_widgets_text(self):
        self.setWindowTitle(self._db_def.definition_name)
        self.lbl_name.setText(self._db_def.definition_name)
        self.txt_desc.setText(self._db_def.definition_description)

        self.btn_ok.setText(self.getl("definition_view_btn_ok_text"))
        self.btn_ok.setToolTip(self.getl("definition_view_btn_ok_tt"))
        self.btn_edit.setText(self.getl("definition_view_btn_edit_text"))
        self.btn_edit.setToolTip(self.getl("definition_view_btn_edit_tt"))

    def app_setting_updated(self, data: dict):
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()
        self._define_labels_apperance(self.lbl_name, "definition_view_name")

        self._define_buttons_apperance(self.btn_edit, "definition_view_btn_edit")
        self._define_buttons_apperance(self.btn_ok, "definition_view_btn_ok")
        self._define_buttons_apperance(self.btn_size, "definition_view_btn_size")
        self.btn_close.setStyleSheet(self.getv("definition_view_btn_close_stylesheet"))

        self._define_text_box_apperance(self.txt_desc, "definition_view_txt_desc")

    def _define_definition_win_apperance(self):
        self.setStyleSheet(self.getv("definition_view_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("definition_view_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setContentsMargins(10, 10, 10, 10)

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


class BrowseDefinitions(QDialog):
    MINIMUM_SEARCH_LEN = 5

    def __init__(self, settings: settings_cls.Settings, parent_widget, definition_id: int = None, *args, **kwargs):

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_obj = parent_widget
        if isinstance(definition_id, list):
            self._definition_id = None
        else:
            self._definition_id = definition_id
        self._def_dict = None
        self.def_list = None
        self._dont_clear_menu = False
        self._clip: utility_cls.Clipboard = self.get_appv("cb")
        self._text_filter = text_filter_cls.TextFilter()
        self._text_filter.MatchCase = False
        self._text_filter.SearchWholeWordsOnly = False

        # Load GUI
        uic.loadUi(self.getv("browse_def_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._populate_widgets()
        self._load_win_position()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.lst_def.currentItemChanged.connect(self._lst_def_current_item_changed)
        self.lst_def.contextMenuEvent = self.lst_def_context_menu
        self.lst_def.mouseDoubleClickEvent = self._lst_def_mouse_double_click
        self.lst_def.mousePressEvent = self.lst_def_start_drag
        
        self.btn_close.clicked.connect(self._btn_close_click)
        self.btn_edit.clicked.connect(self._btn_edit_click)
        self.btn_add.clicked.connect(self._btn_add_click)
        self.btn_delete.clicked.connect(self._btn_delete_click)
        self.lbl_pic.mouseDoubleClickEvent = self.lbl_pic_double_click
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.txt_find.textChanged.connect(self.txt_find_text_changed)
        self.txt_find.returnPressed.connect(self.txt_find_return_pressed)
        self.txt_find.contextMenuEvent = self.txt_find_context_menu
        self.txt_desc.mouseDoubleClickEvent = self.txt_desc_mouse_double_click

        self.get_appv("signal").signalCloseAllDefinitions.connect(self._signal_close_all_definitions)
        self.get_appv("signal").signalNewDefinitionAdded.connect(self.signal_new_definition_added)

        self.show()
        self._load_passed_definitions(definition_id)
        self.txt_find.setFocus()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["BrowseDefinitions"])

    def lst_def_start_drag(self, e: QMouseEvent):
        if not self.widget_handler:
            return
        
        lst_widget: qwidgets_util_cls.Widget_ItemBased = self.widget_handler.find_child(self.lst_def, return_none_if_not_found=True)
        if lst_widget is not None:
            lst_widget.EVENT_mouse_press_event(e)

        if e.button() == Qt.LeftButton:
            self.get_appv("cb").clear_drag_data()
            item = self.lst_def.currentItem()
            if item is not None:
                self.get_appv("cb").set_drag_data(item.data(Qt.UserRole), "def", self)
                self.lst_def.startDrag(Qt.CopyAction)
        QListWidget.mousePressEvent(self.lst_def, e)
        if self.lst_def.currentItem() is not None:
            self.lst_def.scrollToItem(self.lst_def.currentItem())

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

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_find, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_desc, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        
        # Add Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_def)
        lst_widget: qwidgets_util_cls.Widget_ItemBased = self.widget_handler.find_child(self.lst_def, return_none_if_not_found=True)
        if lst_widget is not None:
            lst_widget.properties.allow_bypass_mouse_press_event = False

        self.widget_handler.activate()

    def _signal_close_all_definitions(self):
        UTILS.LogHandler.add_log_record("#1: Signal #2 recieved.", ["BrowseDefinitions", "CloseAllDefinitions"])
        self.close()

    def _lst_def_mouse_double_click(self, e: QtGui.QMouseEvent):
        self._btn_edit_click()
        QListWidget.mouseDoubleClickEvent(self.lst_def, e)
        self.get_appv("cb").clear_drag_data()
        self.lst_def.setDragEnabled(False)
        self.lst_def.setDragEnabled(True)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def txt_desc_mouse_double_click(self, e):
        if self.lst_def.currentItem() is None:
            return
        
        db_def = db_definition_cls.Definition(self._stt, self.lst_def.currentItem().data(Qt.UserRole))
        def_desc = db_def.definition_description

        if self.txt_desc.toPlainText() == def_desc:
            self.txt_desc.setText(self._def_dict[self.lst_def.currentItem().data(Qt.UserRole)])
        else:
            self.txt_desc.setText(def_desc)

    def txt_find_context_menu(self, e):
        UTILS.LogHandler.add_log_record("#1: TextBox #2 context menu displayed.", ["BrowseDefinitions", "txt_find"])
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

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter)

        menu_dict = filter_menu.create_menu_dict(show_item_search_history=False, existing_menu_dict=menu_dict)

        self._dont_clear_menu = True

        result = filter_menu.show_menu(self, menu_dict=menu_dict)

        if result in range(filter_menu.item_range_filter_setup[0], filter_menu.item_range_filter_setup[1]):
            self.txt_find_text_changed()
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
        else:
            UTILS.LogHandler.add_log_record("#1: User canceled context menu.", ["BrowseDefinitions"])

    def txt_find_text_changed(self, ignore_small_entry: bool = True):
        txt = self.txt_find.text()
        
        if len(txt) < self.MINIMUM_SEARCH_LEN and ignore_small_entry:
            return
        
        txt = txt.lstrip()

        self._text_filter.clear_search_history()

        self.lst_def.clear()
        for item in self.def_list:
            if txt:
                if self._text_filter.is_filter_in_document(txt, self._def_dict[self.def_list[item]]):
                    lst_item = QListWidgetItem()
                    lst_item.setText(item)
                    lst_item.setData(Qt.UserRole, self.def_list[item])
                    self.lst_def.addItem(lst_item)
                    if len(txt) >= self.MINIMUM_SEARCH_LEN:
                        self._text_filter.save_search_history(f"{lst_item.data(Qt.UserRole)} | Name: {lst_item.text()}")
            else:
                lst_item = QListWidgetItem()
                lst_item.setText(item)
                lst_item.setData(Qt.UserRole, self.def_list[item])
                self.lst_def.addItem(lst_item)
        
        self._select_first_item_in_list()
        self._update_counter()

    def _load_passed_definitions(self, def_ids: list):
        if not isinstance(def_ids, list):
            return

        def_ids = [UTILS.TextUtility.get_integer(x) for x in def_ids if UTILS.TextUtility.is_integer_possible(x)]
        self.lst_def.clear()
        for item in self.def_list:
            if self.def_list[item] in def_ids:
                lst_item = QListWidgetItem()
                lst_item.setText(item)
                lst_item.setData(Qt.UserRole, self.def_list[item])
                self.lst_def.addItem(lst_item)
        
        # Select first item
        self._select_first_item_in_list()
        
        if def_ids:
            UTILS.LogHandler.add_log_record("#1: Loaded definition list to show.", ["BrowseDefinitions"], variables=[["Definition List", def_ids]])
        self._update_counter()

    def _select_first_item_in_list(self):
        current_set = False
        if self.lst_def.count() > 0:
            self.lst_def.setCurrentRow(0)
            current_set = True

        if current_set:
            self._populate_data(self.lst_def.currentItem().data(Qt.UserRole))
        else:
            self._populate_data(None)

    def txt_find_return_pressed(self):
        self.txt_find_text_changed(ignore_small_entry=False)

    def _get_def_dict(self) -> dict:
        db_def = db_definition_cls.Definition(self._stt)
        
        def_dict = {}
        for i in db_def.get_list_of_all_expressions():
            if i[1] in def_dict:
                def_dict[i[1]] = def_dict[i[1]] + f"[{i[0]}] "
            else:
                def_dict[i[1]] = f"[{i[0]}] "
        return def_dict

    def _get_def_list(self) -> dict:
        db_def = db_definition_cls.Definition(self._stt)

        def_list = {}
        for i in db_def.get_list_of_all_definitions(order_by_name=True):
            def_list[i[1]] = i[0]
        
        return def_list

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

    def lbl_pic_double_click(self, e):
        if self._definition_id is None:
            return
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        media_ids = [[x] for x in db_def.definition_media_ids]

        if media_ids:
            utility_cls.PictureBrowse(self._stt, self, media_list=media_ids)

    def lst_def_context_menu(self, e):
        self._show_context_menu()

    def lbl_pic_mouse_press(self, e):
        self.get_appv("cm").remove_all_context_menu()
        if e.button() == Qt.LeftButton:
            if self._definition_id is None:
                return

            self.get_appv("cb").set_drag_data(self._definition_id, "def")
            
            mime_data = QMimeData()
            mime_data.setText(str(self._definition_id))
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)
        elif e.button() == Qt.RightButton:
            self._show_context_menu()

    def _show_context_menu(self):
        if self._definition_id is None:
            return
        
        disab = []

        if self.lbl_pic.pixmap():
            show_cur_pic = self.lbl_pic.pixmap()
        else:
            show_cur_pic = None

        if not self.lbl_pic.objectName():
            disab.append(10)
            disab.append(15)
            disab.append(20)
        
        cur_item = self.getl("browse_def_menu_rename_def_text")
        if self.lst_def.currentItem() is not None:
            cur_item += f" ({self.lst_def.currentItem().text()})"
        else:
            disab.append(30)
        
        if self._clip.is_clip_empty():
            disab.append(90)

        list_item = self.lst_def.currentItem()
        if list_item is None:
            full_item_id = ""
        else:
            full_item_id = f"{list_item.data(Qt.UserRole)} | Name: {list_item.text()}"

        def_id = 0
        all_defs = []

        for i in range(self.lst_def.count()):
            if not self.lst_def.item(i).isHidden():
                all_defs.append(self.lst_def.item(i).data(Qt.UserRole))

        no_items_in_clip = self.get_appv("cb").def_clip_number_of_items()
        no_items_in_list = len(all_defs)
        no_items_found = len(self.get_appv("cb").def_clip_ids_that_are_in_clipboard(all_defs))

        if self.lst_def.currentItem() is None:
            for i in [110, 11010, 11020, 11030, 11040, 11050, 11060, 11070, 120, 12010, 130, 13010]:
                disab.append(i)
        else:
            def_id = self.lst_def.currentItem().data(Qt.UserRole)

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
            "selected": [20],
            "separator": [20, 40, 90, 130, 11030, 11060],
            "disabled": disab,
            "items": [
                [
                    10, self.getl("browse_def_menu_show_pic_text"), self.getl("browse_def_menu_show_pic_tt"), True, [], show_cur_pic
                ],
                [
                    15,
                    self.getl("picture_view_menu_image_info_text"),
                    self.getl("picture_view_menu_image_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    20, self.getl("browse_def_menu_show_all_pic_text"), self.getl("browse_def_menu_show_all_pic_tt"), True, [], self.getv("browse_def_menu_show_all_pic_icon_path")
                ],
                [
                    30, cur_item, self.getl("browse_def_menu_rename_def_tt"), True, [], self.getv("browse_def_menu_rename_def_icon_path")
                ],
                [
                    40, self.getl("browse_def_menu_edit_def_text") + f" ({self.lst_def.currentItem().text()})", self.getl("browse_def_menu_edit_def_tt"), True, [], self.getv("browse_def_menu_edit_def_icon_path")
                ],
                [
                    70,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    80,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    90,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
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

        filter_menu = text_filter_cls.FilterMenu(self._stt, self._text_filter)
        
        menu_dict = filter_menu.create_menu_dict(existing_menu_dict=menu_dict,
                                                 show_match_case=False,
                                                 show_whole_words=False,
                                                 show_ignore_serbian_characters=False,
                                                 show_translate_cyrillic_to_latin=False)

        filter_menu.show_menu(self, menu_dict=menu_dict, full_item_ID=full_item_id)

        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        media_ids = db_def.definition_media_ids

        result = self.get_appv("menu")["result"]

        if result == 10:
            if self.lbl_pic.objectName() and media_ids:
                utility_cls.PictureView(self._stt, self, media_ids, int(self.lbl_pic.objectName()))
        elif result == 15:
            if self.lbl_pic.objectName() and media_ids:
                utility_cls.PictureInfo(self._stt, self, media_id=int(self.lbl_pic.objectName()))
        elif result == 20:
            if media_ids:
                media_ids = [[x] for x in db_def.definition_media_ids]
                utility_cls.PictureBrowse(self._stt, self, media_list=media_ids)
        elif result == 30:
            self._rename_definition()
        elif result == 40:
            self._btn_edit_click()
        elif result == 70:
            self._clip.copy_to_clip(UTILS.TextUtility.get_integer(self.lbl_pic.objectName()))
        elif result == 80:
            self._clip.copy_to_clip(UTILS.TextUtility.get_integer(self.lbl_pic.objectName()), add_to_clip=True)
        elif result == 90:
            self._clip.clear_clip()
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

    def _rename_definition(self) -> bool:
        if self.lst_def.currentItem() is None:
            return False
        
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        
        desc = self.getl("browse_def_menu_rename_def_input_box_desc")
        desc = desc.replace("#1", str(db_def.definition_id))
        desc = desc.replace("#2", db_def.definition_name)
        desc = desc.replace("#3", str(len(db_def.definition_synonyms)))
        desc = desc.replace("#4", str(len(db_def.definition_media_ids)))

        input_dict = {
            "name": "block_input_box_name",
            "title": self.getl("browse_def_menu_rename_def_input_box_title"),
            "text": self.lst_def.currentItem().text(),
            "position": QCursor.pos(),
            "description": desc,
            "validator": {
                "type": "definition",
                "excluded": [x for x in self.def_list.keys()]
            }
        }
        self._dont_clear_menu = True
        utility_cls.InputBoxSimple(self._stt, self, input_dict)
        if not input_dict["result"]:
            return
        
        # Check if name already exists as definition name
        input_dict["result"] = input_dict["result"].strip()
        is_valid = True
        for item in self.def_list:
            if item.lower() == input_dict["result"].lower():
                is_valid = False
                break
        
        if not is_valid:
            notif_dict = {
                "title": self.getl("browse_def_menu_rename_def_notification_title"),
                "text": self.getl("browse_def_menu_rename_def_notification_name_exist_text"),
                "timer": 10000,
                "position": "bottom left",
                "show_close": True,
                "icon": self.getv("cancel_icon_path")
            }
            utility_cls.Notification(self._stt, self, notif_dict)
            return

        definition = Definition(self._stt, def_id=self._definition_id)
        definition.DefName = input_dict["result"]
        if definition.can_be_saved():
            definition.save()
        else:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2, cannot save definition ID = #3", ["BrowseDefinitions", "_rename_definition", self._definition_id], exception_raised=True)
            return

        self.lst_def.currentItem().setText(definition.DefName)
        self._populate_data(self._definition_id)
        
        self.get_appv("text_handler_data").update_data()
        self.get_appv("signal").new_definition_added()

        notif_dict = {
            "position": "bottom left",
            "title": self.getl("browse_def_menu_rename_def_notification_title"),
            "text": self.getl("browse_def_menu_rename_def_notification_text"),
            "timer": 2000
        }
        utility_cls.Notification(self._stt, self, notif_dict)

    def _btn_delete_click(self):
        if self.lst_def.currentItem() is not None:
            if self.lst_def.currentItem().data(Qt.UserRole) == self._definition_id:
                msg = {
                    "title": self.getl("browse_def_delete_conf_msg_title"),
                    "text": self.getl("browse_def_delete_conf_msg_text") + self.lbl_name.text(),
                    "icon_path": self.getv("browse_def_btn_delete_icon_path"),
                    "position": "center_parent",
                    "buttons": [
                        [1, self.getl("btn_yes"), "", None, True],
                        [2, self.getl("btn_no"), "", None, True],
                        [3, self.getl("btn_cancel"), "", None, True]
                    ]
                }
                utility_cls.MessageQuestion(self._stt, self, msg, app_modal=True)
                if msg["result"] != 1:
                    return
        else:
            msg = {
                "title": self.getl("browse_def_delete_no_item_msg_title"),
                "text": self.getl("browse_def_delete_no_item_msg_text") + self.lbl_name.text()
            }
            utility_cls.MessageInformation(self._stt, self, msg)
            return
        
        definition = Definition(self._stt, def_id=self._definition_id)
        if definition.can_be_deleted():
            definition.delete()
        else:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2, cannot delete definition ID = #3", ["BrowseDefinitions", "_btn_delete_click", self._definition_id], exception_raised=True)
            return
        
        def_name = definition.DefName
        self.get_appv("text_handler_data").update_data()

        row = self.lst_def.currentRow()
        
        item_row_deleted = row

        if row + 1 < self.lst_def.count():
            row += 1
        elif row + 1 == self.lst_def.count():
            row -= 1
        
        if row < 0:
            def_id = None
        else:
            def_id = self.lst_def.item(row).data(Qt.UserRole)
        self._definition_id = def_id
        
        self._def_dict = self._get_def_dict()
        self.def_list = self._get_def_list()
        if row is not None:
            self.lst_def.setCurrentRow(row)
        self.lst_def.takeItem(item_row_deleted)

        self._populate_data(def_id=self._definition_id)

        ntf_dict = {
            "title": "",
            "text": self.getl("browse_def_notiff_item_deleted_text").replace("#1", def_name),
            "timer": 2000
        }
        self.get_appv("signal").new_definition_added()
        utility_cls.Notification(self._stt, self, ntf_dict)

    def signal_new_definition_added(self):
        self._populate_data(def_id=self._definition_id)
        if self.def_list != self._get_def_list():
            self._populate_widgets(self._definition_id)
            self.txt_find_text_changed()

    def _btn_close_click(self):
        self.close()

    def _btn_edit_click(self):
        if self.lst_def.currentItem() is not None:
            self._definition_id = self.lst_def.currentItem().data(Qt.UserRole)
            AddDefinition(self._stt, self, definition_id=self._definition_id)
            # self._populate_widgets(self._definition_id)
            # self.txt_find_text_changed()
        else:
            AddDefinition(self._stt, self)
            # self._populate_widgets(self._definition_id)
            # self.txt_find_text_changed()

    def _btn_add_click(self):
        AddDefinition(self._stt, self, expression=self.txt_find.text())
        self._populate_widgets(self._definition_id)
        self.txt_find_text_changed()

    def _lst_def_current_item_changed(self, x, y):
        self._update_counter()
        if self.lst_def.currentItem() is not None:
            self._populate_data(self.lst_def.currentItem().data(Qt.UserRole))

    def _update_counter(self):
        total = len(self.def_list)
        active = self.lst_def.count()
        self.lbl_count.setText(self.getl("browse_def_lbl_count_text").replace("#1", str(active)).replace("#2", str(total)))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "browse_def_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("browse_def_win_geometry", {}, save_to_file=True)

        g = self.get_appv("browse_def_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        
        self.get_appv("cb").clear_drag_data()
        
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["BrowseDefinitions"])
        self.get_appv("cm").remove_all_context_menu()
        QCoreApplication.processEvents()
        UTILS.DialogUtility.on_closeEvent(self)

    def _load_win_position(self):
        if "browse_def_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("browse_def_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        scale_left = 0.4
        scale_right = 0.55
        # Title
        self.lbl_title.resize(w, self.lbl_title.height())
        # Buttons
        self.btn_close.move(w - 90, h - 30)
        self.btn_edit.move(w - 170, h - 30)
        self.btn_add.move(w - 270, h - 30)
        self.btn_delete.move(w - 350, h - 30)
        # List
        self.lst_def.resize(int(w * scale_left), h - 120)
        # Counter
        self.lbl_count.move(10, h - 30)
        self.lbl_count.resize(w - 360, self.lbl_count.height())
        # Picture
        self.lbl_pic.move(self.lst_def.width() + 20, self.lbl_pic.pos().y())
        self.lbl_pic.resize(w - self.lbl_pic.pos().x() - 10, h - 270)
        # Name
        self.lbl_name.move(self.lst_def.width() + 20, h - 210)
        self.lbl_name.resize(w - self.lbl_name.pos().x() - 10, self.lbl_name.height())
        # Description
        self.txt_desc.move(self.lst_def.width() + 20, h - 170)
        self.txt_desc.resize(w - self.txt_desc.pos().x() - 10, self.txt_desc.height())

        self._populate_data(self._definition_id)
        return super().resizeEvent(a0)

    def _populate_widgets(self, def_id: int = None):
        self._def_dict = self._get_def_dict()
        self.def_list = self._get_def_list()

        if def_id is None:
            def_id = self._definition_id

        try:
            self.lst_def.clear()
        except Exception as e:
            UTILS.LogHandler.add_log_record("#1: Error clearing list in function #2: #3", ["BrowseDefinitions", "_populate_widgets", e], exception_raised=True)
            return
        
        row = None
        count = 0
        for definition in self.def_list.keys():
            item = QListWidgetItem()
            item.setText(definition)
            item.setData(Qt.UserRole, self.def_list[definition])
            self.lst_def.addItem(item)
            if def_id == self.def_list[definition]:
                row = count
            count += 1

        if row is not None:
            self.lst_def.setCurrentRow(row)
            self._definition_id = self.lst_def.currentItem().data(Qt.UserRole)
        else:
            if self.lst_def.count():
                self.lst_def.setCurrentRow(0)
                self._definition_id = self.lst_def.currentItem().data(Qt.UserRole)

        self._populate_data(def_id=self._definition_id)

    def _populate_data(self, def_id: int = None) -> None:
        self._update_counter()
        if def_id is None:
            def_id = self._definition_id
            img = QPixmap()
            img.load(self.getv("no_icon_icon_path"))
            self.lbl_pic.setPixmap(img)
            self.lbl_name.setText("")
            self.txt_desc.setText("")
            self.lbl_pic.setDisabled(True)
            self.lbl_name.setDisabled(True)
            self.txt_desc.setDisabled(True)
            return
        else:
            self.lbl_pic.setDisabled(False)
            self.lbl_name.setDisabled(False)
            self.txt_desc.setDisabled(False)
            self._definition_id = def_id

        db_def = db_definition_cls.Definition(self._stt, def_id=def_id)
        
        self.lbl_name.setText(db_def.definition_name)
        self.txt_desc.setText(db_def.definition_description)
        
        default_media = db_def.default_media_id
        if not default_media:
            if db_def.definition_media_ids:
                default_media = db_def.definition_media_ids[0]
        if default_media:
            img = QPixmap()
            db_media = db_media_cls.Media(self._stt, default_media)
            img.load(db_media.media_file)
            size = self.lbl_pic.size()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)
            self.lbl_pic.setObjectName(str(default_media))
        else:
            img = QPixmap()
            img.load(self.getv("browse_def_win_icon_path"))
            self.lbl_pic.setPixmap(img)
            self.lbl_pic.setObjectName("")

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.txt_find: QLineEdit = self.findChild(QLineEdit, "txt_find")

        self.btn_edit: QPushButton = self.findChild(QPushButton, "btn_edit")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_delete: QPushButton = self.findChild(QPushButton, "btn_delete")
        self.btn_add: QPushButton = self.findChild(QPushButton, "btn_add")

        self.lst_def: QListWidget = self.findChild(QListWidget, "lst_def")

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("browse_def_win_title"))
        self.lbl_title.setText(self.getl("browse_def_win_title"))
        self.lbl_name.setText("")
        self.txt_desc.setText("")
        self.lbl_count.setText("")

        self.btn_edit.setText(self.getl("browse_def_btn_edit_text"))
        self.btn_edit.setToolTip(self.getl("browse_def_btn_edit_tt"))
        self.btn_close.setText(self.getl("browse_def_btn_close_text"))
        self.btn_close.setToolTip(self.getl("browse_def_btn_close_tt"))
        self.btn_delete.setText(self.getl("browse_def_btn_delete_text"))
        self.btn_delete.setToolTip(self.getl("browse_def_btn_delete_tt"))
        self.btn_add.setText(self.getl("browse_def_btn_add_text"))
        self.btn_add.setToolTip(self.getl("browse_def_btn_add_tt"))

    def app_setting_updated(self, data: dict):
        self._setup_widgets_apperance()

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()
        
        self._define_labels_apperance(self.lbl_title, "browse_def_lbl_title")
        self._define_labels_apperance(self.lbl_name, "browse_def_lbl_name")
        self._define_labels_apperance(self.lbl_count, "browse_def_lbl_count")

        self._define_buttons_apperance(self.btn_edit, "browse_def_btn_edit")
        self._define_buttons_apperance(self.btn_delete, "browse_def_btn_delete")
        self._define_buttons_apperance(self.btn_close, "browse_def_btn_close")
        self._define_buttons_apperance(self.btn_add, "browse_def_btn_add")

        self._define_text_box_apperance(self.txt_desc, "browse_def_txt_desc")
        self._define_text_box_apperance(self.txt_find, "browse_def_txt_find")
        self._define_list_apperance(self.lst_def, "browse_def_lst_def")
        self.lst_def.setDragEnabled(True)

    def _define_definition_win_apperance(self):
        self.setStyleSheet(self.getv("browse_def_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("browse_def_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(370, 330)

    def _define_list_apperance(self, list_obj: QListWidget, name: str) -> None:
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        list_obj.setFont(font)
        list_obj.setStyleSheet(self.getv(f"{name}_stylesheet"))

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


class FindDefinition(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, expression: str = None, *args, **kwargs):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Define other variables
        self._parent_obj = parent_widget
        self._expression = expression
        self._dont_clear_menu = False
        self._title = ""
        self._clip: utility_cls.Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("find_def_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self.load_widgets_handler()

        self._load_win_position()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.lst_pages.currentChanged = self._lst_pages_current_changed
        self.lbl_pic.mousePressEvent = self._lbl_pic_mouse_press
        self.lbl_pic2.mousePressEvent = self._lbl_pic2_mouse_press
        self.lbl_pic3.mousePressEvent = self._lbl_pic3_mouse_press
        self.btn_cancel.clicked.connect(self._btn_cancel_click)
        self.btn_open_images.clicked.connect(self._btn_open_images_click)

        self.show()

        self.frm_load.setVisible(True)
        QCoreApplication.processEvents()
        self._populate_widgets()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["FindDefinitions"])

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_name])

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_desc, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets

        # Add ItemBased Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_pages)

        self.widget_handler.activate()

    def _btn_cancel_click(self):
        self.close()

    def _btn_open_images_click(self):
        if self._title:
            title_list = [x for x in self._title.split(" ") if x != ""]
            title = "+".join(title_list)
            webbrowser.open_new_tab(f"https://duckduckgo.com/?va=v&t=ha&q={title}&iax=images&ia=images")

    def _open_transparent_images(self):
        if self._title:
            title_list = [x for x in self._title.split(" ") if x != ""]
            title = "+".join(title_list)
            webbrowser.open_new_tab(f"https://www.google.com/search?q={title}&tbm=isch&tbs=ic:trans")

    def _lbl_pic_mouse_press(self, e):
        self._show_image_menu(self.lbl_pic.pixmap(), self.lbl_pic.objectName())

    def _lbl_pic2_mouse_press(self, e):
        self._show_image_menu(self.lbl_pic2.pixmap(), self.lbl_pic2.objectName())

    def _lbl_pic3_mouse_press(self, e):
        self._show_image_menu(self.lbl_pic3.pixmap(), self.lbl_pic3.objectName())

    def _show_image_menu(self, img: QPixmap, url_text: str):
        if not self._title:
            disab = [20, 30]
        else:
            disab = []

        disab.append(15)
        if self._clip.is_clip_empty():
            disab.append(17)
        
        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [17],
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
                    15,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
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
                    self.getl("find_def_image_menu_show_images_text"),
                    self.getl("find_def_image_menu_show_images_tt"),
                    True,
                    [],
                    None
                ],
                [
                    30,
                    self.getl("find_def_image_menu_show_trans_images_text"),
                    self.getl("find_def_image_menu_show_trans_images_tt"),
                    True,
                    [],
                    None
                ],
            ]
        }
        self._dont_clear_menu = True
        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self)
        
        if self.get_appv("menu")["result"] == 10:
            image = QImage(img)
            self.get_appv("clipboard").setImage(image)
            self._clip.copy_to_clip(url_text, add_to_clip=False)
        elif self.get_appv("menu")["result"] == 15:
            image = QImage(img)
            self.get_appv("clipboard").setImage(image)
            self._clip.copy_to_clip(url_text, add_to_clip=True)
        elif self.get_appv("menu")["result"] == 17:
            self._clip.clear_clip()
        elif self.get_appv("menu")["result"] == 20:
            self._btn_open_images_click()
        elif self.get_appv("menu")["result"] == 30:
            self._open_transparent_images()

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _lst_pages_current_changed(self, x, y):
        self._populate_data()

    def _wiki_error(self):
        self.txt_desc.setText(self.getl("find_def_url_not_found_text"))
        self.lbl_name.setText(self.getl("find_def_url_not_found_text"))
        self.frm_load.setVisible(False)

    def _populate_widgets(self):
        self.lst_pages.clear()
        self.frm_load.setVisible(True)
        QCoreApplication.processEvents()

        lang = self.get_appv("user").language_name
        lang_code = googletrans.LANGCODES[lang]

        start_t = time.perf_counter()
        try:
            wikipedia.set_lang(lang_code)
            results = wikipedia.search(self._expression)
        except Exception as e:
            self.get_appv("log").write_log("Error: Wikipedia SEARCH: " + str(e))
            self._wiki_error()
            return
        end_t = time.perf_counter()
        self.get_appv("log").write_log(f"Wikipedia search finnished in {end_t - start_t}, Expression: {self._expression}")

        if not results:
            self._wiki_error()
            return
        
        for result in results:
            item = QListWidgetItem()
            item.setText(result)
            self.lst_pages.addItem(item)
        
        self.lst_pages.setCurrentRow(0)

    def _populate_data(self):
        title = self.lst_pages.currentItem().text()

        img = QPixmap(self.getl("find_def_lbl_pic_icon_path"))
        self.lbl_pic.setPixmap(img)
        self.lbl_pic2.setPixmap(img)
        self.lbl_pic3.setPixmap(img)
        
        self.frm_load.setVisible(True)
        self.prg_load.setValue(1)
        QCoreApplication.processEvents()

        start_t = time.perf_counter()
        try:
            page = wikipedia.page(title)
        except Exception as e:
            self.get_appv("log").write_log("Error: Wikipedia PAGE: " + str(e))
            self._wiki_error()
            return
        end_t = time.perf_counter()
        self.get_appv("log").write_log(f"Wikipedia page loaded in {end_t - start_t}")

        skip_images = [
            "-logo",
            "_icon",
            "lock-green",
        ]

        try:
            self.get_appv("log").write_log(f"All Images: {self._expression} ({len(page.images)} images)")
        except Exception as e:
            self.get_appv("log").write_log("Error: Wikipedia PAGE: " + str(e))
            self._wiki_error()
            return

        for image in page.images:
            self.get_appv("log").write_log(image)

        if page:
            self.get_appv("log").write_log("FindDefinition. Wikipedia PAGE: " + page.title)
            self.lbl_name.setText(page.title)
            self._title = page.title
            self.txt_desc.setText(page.content)
            self.prg_load.setValue(2)
            QCoreApplication.processEvents()

            if page.images:
                page_images = []
                jpg_images = []
                png_images = []
                other_images = []
                for image in page.images:
                    skip_image = False
                    for i in skip_images:
                        if i in image.lower():
                            skip_image = True
                    if not skip_image:
                        if image.find(".jpg") >= 0 or image.find(".jpeg") >= 0:
                            jpg_images.append(image)
                        elif image.find(".png") >= 0:
                            png_images.append(image)
                        else:
                            other_images.append(image)
                
                page_images = jpg_images + png_images + other_images
                if len(page_images) > 3:
                    page_images = page_images[:3]

                self.get_appv("log").write_log(f"Selected Images: {len(skip_images)} filters.")
                for image in page_images:
                    self.get_appv("log").write_log(image)

                s_time = time.perf_counter()
                image_data = asyncio.run(self.a_load_images(page_images))
                e_time = time.perf_counter()
                
                self.get_appv("log").write_log(f"FindDefinition. Finnished {len(image_data)} images in {e_time - s_time} : {page.title}")

                self.prg_load.setValue(3)
                QCoreApplication.processEvents()
                
                if image_data:

                    count = 1
                    for idx, image in enumerate(image_data):

                        img = QPixmap()
                        try:
                            img.loadFromData(image)
                        except Exception as e:
                            self.get_appv("log").write_log(f"Error. FindDefinition. LoadImage in QPixmap: {e}")
                            continue
                        
                        size = self.lbl_pic.size()
                        if img.height() > size.height() or img.width() > size.width():
                            img = img.scaled(size, Qt.KeepAspectRatio)
                        
                        if count == 1:
                            self.lbl_pic.setPixmap(img)
                            self.lbl_pic.setObjectName(page_images[idx])
                        elif count == 2:
                            self.lbl_pic2.setPixmap(img)
                            self.lbl_pic2.setObjectName(page_images[idx])
                        elif count == 3:
                            self.lbl_pic3.setPixmap(img)
                            self.lbl_pic3.setObjectName(page_images[idx])
                            break
                        
                        count += 1
        self.prg_load.setValue(0)
        self.frm_load.setVisible(False)

    async def a_load_images(self, image_list: list) -> list:
        img_data = []
        img_tasks = []

        timeout = aiohttp.ClientTimeout(total=3)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for image_name in image_list:
                img_tasks.append(session.get(image_name, ssl=False))

            responses = await asyncio.gather(*img_tasks)

            for response in responses:
                try:
                    web_image = await response.read()
                    img_data.append(web_image)
                except Exception as e:
                    self.get_appv("log").write_log(f"Error. FindDefinition. asyn_load_image: {e}")

        return img_data

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "find_def_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("find_def_win_geometry", {}, save_to_file=True)

        g = self.get_appv("find_def_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["FindDefinitions"])
        self.get_appv("cm").remove_all_context_menu()
        UTILS.DialogUtility.on_closeEvent(self)

    def _load_win_position(self):
        if "find_def_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("find_def_win_geometry")
            self.move(g["pos_x"], g["pos_y"])

    def _setup_widgets(self):
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_pic2: QLabel = self.findChild(QLabel, "lbl_pic2")
        self.lbl_pic3: QLabel = self.findChild(QLabel, "lbl_pic3")
        self.lst_pages: QListWidget = self.findChild(QListWidget, "lst_pages")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")
        self.btn_open_images: QPushButton = self.findChild(QPushButton, "btn_open_images")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")

        self.frm_load: QFrame = self.findChild(QFrame, "frm_load")
        self.lbl_load: QLabel = self.findChild(QLabel, "lbl_load")
        self.prg_load: QProgressBar = self.findChild(QProgressBar, "prg_load")

    def _setup_widgets_text(self):
        self.lbl_name.setText("")
        self.setWindowTitle(self.getl("find_def_win_title"))

        self.btn_open_images.setText(self.getl("find_def_btn_open_images_text"))
        self.btn_open_images.setToolTip(self.getl("find_btn_open_images_edit_tt"))

        self.btn_cancel.setText(self.getl("btn_cancel"))

        self.lbl_load.setText(self.getl("find_def_lbl_load_text"))
        self.lbl_load.setToolTip(self.getl("find_def_lbl_load_tt"))

    def app_setting_updated(self, data: dict):
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        if not settings_updated:
            self.frm_load.setVisible(False)
        self.lbl_load.setStyleSheet(self.getl("find_def_lbl_load_stylesheet"))

        self._define_find_definition_win_apperance()

        self._define_labels_apperance(self.lbl_name, "find_def_lbl_name")
        
        self.lbl_pic.setStyleSheet(self.getl("find_def_lbl_pic_stylesheet"))
        self.lbl_pic2.setStyleSheet(self.getl("find_def_lbl_pic2_stylesheet"))
        self.lbl_pic3.setStyleSheet(self.getl("find_def_lbl_pic3_stylesheet"))

        self.lst_pages.setStyleSheet(self.getl("find_def_lst_pages_stylesheet"))

        self._define_text_box_apperance(self.txt_desc, "find_def_txt_desc")
        self._define_buttons_apperance(self.btn_open_images, "find_def_btn_edit")
        self._define_buttons_apperance(self.btn_cancel, "find_def_btn_cancel")

    def _define_find_definition_win_apperance(self):
        self.setStyleSheet(self.getv("find_def_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("find_def_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(1390, 870)

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

