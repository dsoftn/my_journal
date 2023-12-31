from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QGridLayout, QWidget, QListWidget, 
                             QDialog, QLabel, QListWidgetItem, QLineEdit, QHBoxLayout, QCheckBox, QAction,
                             QProgressBar , QComboBox, QMessageBox)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor, QTextCharFormat, QColor, QImage, QClipboard
from PyQt5.QtCore import (QSize, Qt, QCoreApplication, QPoint)
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtMultimedia import QSound

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
            self.dialog_queue = utility_cls.DialogsQueue(self, self.my_name, add_dialog=True)

        # Load GUI
        uic.loadUi(self.getv("synonyms_manager_ui_file_path"), self)

        self._define_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()
        self._load_data(shema_name, suggested_words=suggested_words)
        self._load_win_position()

        self.old_base_text = self.cmb_apply.currentText()

        # Connect events with slots
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

        self.show()

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
        self.btn_copy.setEnabled(False)

    def btn_update_click(self):
        item = self.txt_name.text()
        if item in self.shemas:
            self.shemas[item]["suffs"] = [x.strip() for x in self.txt_suff.toPlainText().split("\n") if x.strip() != ""]
        
        self._update_counter_and_buttons()

    def btn_add_click(self):
        if len(self.shemas) >= 50:
            self._msg_maximum_shemas()
            return
        
        name = self.txt_name.text()
        suffs = [x.strip() for x in self.txt_suff.toPlainText().split("\n") if x.strip() != ""]
        
        if name in self.shemas:
            return
        
        self.shemas[name] = {"suffs": suffs}
        self._update_counter_and_buttons()
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
        if "synonym_manager_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("synonym_manager_win_geometry", {}, save_to_file=True)

        g = self.get_appv("synonym_manager_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["font_size"] = self.txt_suff.font().pointSize()

        # Unregister Dialog
        if self._parent_widget is None:
            self.dialog_queue.dialog_method_remove_dialog(self.my_name)
        
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
        # if not self._dont_close_me:
        self.close()

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
    
    def _add_copy_paste_manager_items(self, menu_items: list) -> None:
        name = self.getl("syn_hint_menu_copy_text")
        tt = self.getl("syn_hint_menu_copy_tt")
        icon = self.getv("copy_icon_path")
        menu_item = self._create_menu_item(10010, name, tt, icon=icon)
        menu_items.append(menu_item)

        name = self.getl("syn_hint_menu_paste_text")
        tt = self.getl("syn_hint_menu_paste_tt")
        icon = self.getv("paste_icon_path")
        menu_item = self._create_menu_item(10020, name, tt, icon=icon)
        menu_items.append(menu_item)

        name = self.getl("syn_hint_menu_start_manager_text")
        tt = self.getl("syn_hint_menu_start_manager_tt")
        icon = self.getv("synonyms_icon_path")
        menu_item = self._create_menu_item(10100, name, tt, icon=icon)
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

        self._add_copy_paste_manager_items(menu_items)
        if not self.clipboard.text():
            disab.append(10020)
        cur = self.txt_box.textCursor()
        if cur.hasSelection():
            txt_box_selection = cur.selection().toPlainText()
        else:
            txt_box_selection = None
            disab.append(10010)
        separator.append(10020)
        separator.append(10100)

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
            cur = self.txt_box.textCursor()
            cur.insertText(self.clipboard.text())
            self.txt_box.setTextCursor(cur)
            msg_dict = None
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
    
    def get_shemas(self) -> dict:
        if "def_syn_shemas" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("def_syn_shemas", {}, save_to_file=True)
        
        return self.get_appv("def_syn_shemas")


class DefinitionEditor(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_obj, expression: str = None, *args, **kwargs):
        super().__init__(parent_obj, *args, **kwargs)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_widget = parent_obj
        self._padezi_image = None
        self._dont_clear_menu = False

        # Load GUI
        uic.loadUi(self.getv("definition_editor_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()
        
        self._synonyms_hint = SynonymHint(self._stt, self, self.txt_output)

        # Connect events with slots

        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_clear_base.clicked.connect(self.btn_clear_base_click)
        self.btn_clear_beggining.clicked.connect(self.btn_clear_beggining_click)
        self.btn_clear_end.clicked.connect(self.btn_clear_end_click)
        self.btn_clear_output.clicked.connect(self.btn_clear_output_click)
        self.btn_copy.clicked.connect(self.btn_copy_click)
        self.txt_output.textChanged.connect(self.txt_output_text_changed)
        self.txt_output.mouseReleaseEvent = self.txt_output_mouse_release
        self.btn_generate.clicked.connect(self.btn_generate_click)
        self.txt_base.textChanged.connect(self.btn_base_text_changed)
        self.txt_beggining.keyPressEvent = self._txt_beggining_key_press
        self.txt_end.keyPressEvent = self._txt_end_key_press
        self.chk_add_end.mouseReleaseEvent = self._chk_end_mouse_release
        self.keyPressEvent = self._key_press_event

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

        if expression:
            self.txt_base.setText(expression)

        self._load_win_position()

        self.show()
        self.txt_base.setFocus()
        if self.txt_edit_replace.text():
            self.btn_edit_replace.setEnabled(True)
            self.btn_edit_replace_add.setEnabled(True)

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
        if e.button() == Qt.RightButton:
            self._context_menu_add_pref_suf(self.txt_end)
        QCheckBox.mouseReleaseEvent(self.chk_add_end, e)

    def _txt_end_key_press(self, e: QtGui.QKeyEvent):
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

    def _context_menu_add_pref_suf(self, text_box: QTextEdit):
        menu_dict = {
            "position": self.mapToGlobal(text_box.pos()),
            "separator": [30, 1000],
            "items": [
                [10, self.getl("def_editor_c_menu_pref_suf_imenica_text"), self.getl("def_editor_c_menu_pref_suf_imenica_tt"), True, [], None],
                [15, self.getl("def_editor_c_menu_pref_suf_imenica_default_text"), self.getl("def_editor_c_menu_pref_suf_imenica_default_tt"), True, [], None],
                [20, self.getl("def_editor_c_menu_pref_suf_imenica_naziv_sa_crticom_text"), self.getl("def_editor_c_menu_pref_suf_imenica_naziv_sa_crticom_tt"), True, [], None],
                [30, self.getl("def_editor_c_menu_pref_suf_imenica_naziv_bez_crtice_text"), self.getl("def_editor_c_menu_pref_suf_imenica_naziv_bez_crtice_tt"), True, [], None],

                [1000, self.getl("def_editor_c_menu_pref_suf_pridev_text"), self.getl("def_editor_c_menu_pref_suf_pridev_tt"), True, [], None],

                [2000, self.getl("def_editor_c_menu_pref_suf_glagol_text"), self.getl("def_editor_c_menu_pref_suf_glagol_tt"), True, [], None],
                [2010, self.getl("def_editor_c_menu_pref_suf_glagol_bez_buduc_proslo_text"), self.getl("def_editor_c_menu_pref_suf_glagol_bez_buduc_proslo_tt"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]

        if result == 10:
            self._imenica()
        elif result == 15:
            self._imenica(default=True)
        elif result == 20:
            self._imenica(vlastito_ime=True, sa_crticom=True)
        elif result == 30:
            self._imenica(vlastito_ime=True, sa_crticom=False)
        elif result == 1000:
            self._pridev()
        elif result == 2000:
            self._glagol()
        elif result == 2010:
            self._glagol(only_present=True)

    def _imenica(self, vlastito_ime: bool = False, sa_crticom: bool = False, default:bool = False):
        self._clear_text()
        base_str = self.txt_base.text().strip()
        if not base_str:
            return
        base = base_str

        if default:
            vlastito_ime = True

        if vlastito_ime:
            suff = ["a", "u", "e", "om", "ima", "i"]
            if not default:
                if base_str[-1] == "a":
                    suff = ["a", "e", "i", "u", "om", "ama"]
                    base_str = base_str[:-1]
                elif base_str[-1] == "e":
                    suff = ["e", "a", "ama"]
                    if base_str[-2:-1] in "g":
                        suff = ["e", "u", "ama"]
                    base_str = base_str[:-1]
                elif base_str[-1] == "i":
                    suff = ["i", "ija", "iju", "ijem", "ijom"]
                    if base_str[-2:-1] in "v":
                        suff = ["i", "a", "u", "e", "om", "ima"]
                    base_str = base_str[:-1]
                elif base_str[-1] == "o":
                    suff = ["o", "a", "u", "om"]
                    base_str = base_str[:-1]
                elif base_str[-1] == "u":
                    suff = ["u", "ua", "uu", "om"]
                    base_str = base_str[:-1]

            crtica = []
            if sa_crticom:
                for i in suff:
                    if i == base[-1]:
                        continue
                    if i:
                        if base[-1] in "aeiou":
                            crtica.append(base[-1] + "-" + i)
                        else:
                            crtica.append("-" + i)
            
            suff_text = "\n".join(suff) + "\n" + "\n".join(crtica)
            suff_text = suff_text.strip()

            self.txt_base.setText(base_str)
            self.txt_end.setText(suff_text)
            return

        pattern = """dogs
there is no dogs
I'm going toward the dogs
i see a dogs
hey dogs
with the dogs
about the dogs"""
        
        pattern2 = pattern.replace("dogs", self._translate(base_str, translate_to_croatian=False) + "s")
        pattern = pattern.replace("dogs", self._translate(base_str, translate_to_croatian=False))

        cro_pattern = self._translate(pattern)
        cro_pattern += self._translate(pattern2)
        pat_list = [x.strip() for x in cro_pattern.split("\n") if x.strip() != ""]

        word_list = [x.split(" ")[-1] for x in pat_list]

        word_list2 = list(word_list)
        word_list2.sort(key=len)

        new_base = word_list2[0]
        for i in word_list2:
            for j in range(len(new_base)):
                if new_base[j] != i[j]:
                    new_base = new_base[:j]
                    break
        
        word_list = [x[len(new_base):] for x in word_list if x[len(new_base):].strip() != ""]

        word_list = self._delete_duplicates_from_list(word_list)
        
        suff = "\n".join(word_list)

        if not new_base.strip():
            self._imenica(vlastito_ime=True, sa_crticom=False)
            return

        self.txt_base.setText(new_base.lower())
        self.txt_end.setText(suff)

        return

    def _pridev(self):
        self._clear_text()
        base_str = self.txt_base.text().strip()
        if not base_str:
            return
        
        pattern = """he is red
she is red
milk is red
there is no red man
there is no red woman
there is no red milk
I'm going toward the red man
I'm going toward the red woman
I'm going toward the red milk
i see a red man
i see a red woman
i see a red milk
hey red man
hey red woman
hey red milk
with the red man
with the red woman
with the red milk
about the red man
about the red woman
about the red milk"""
        
        pattern = pattern.replace("red", self._translate(base_str, translate_to_croatian=False))

        cro_pattern = self._translate(pattern)
        pat_list = [x.strip() for x in cro_pattern.split("\n") if x.strip() != ""]

        word_list2 = []
        word_list = []
        extr = ["žen", "mlijek", "čovje"]
        for i in pat_list:
            ii = [x for x in i.split(" ") if len(x) > 0]
            ii2 = ""
            for j in ii:
                add_item = True
                for k in extr:
                    if len(k) < len(j):
                        if j[:len(k)] == k:
                            add_item = False
                if add_item:
                    ii2 += j + " "
            ii2 = ii2.strip()
            word_list.append(ii2.split(" ")[-1])

        word_list2 = list(word_list)
        word_list2.sort(key=len)

        new_base = word_list2[0]
        for i in word_list2:
            for j in range(len(new_base)):
                if new_base[j] != i[j]:
                    new_base = new_base[:j]
                    break
        
        word_list = [x[len(new_base):] for x in word_list if x[len(new_base):].strip() != ""]

        word_list = self._delete_duplicates_from_list(word_list)

        suff = "\n".join(word_list)

        self.txt_base.setText(new_base.lower())
        self.txt_end.setText(suff)

        return

    def _glagol(self, only_present: bool = False):
        self._clear_text()
        base_str = self.txt_base.text().strip()
        if len(base_str) < 2:
            return

        suff_map = {
            "i": {
                "suff": ["im", "is", "iš", "i", "imo", "ite", "e"],
                "time": ["io", "iti", "ila", "ilo", "ile", "ili"]
            },
            "e": {
                "suff": ["em", "es", "eš", "e", "emo", "ete", "u"],
                "time": ["ao", "ati", "ala", "alo", "ale", "ali"]
            },
            "a": {
                "suff": ["am", "as", "aš", "a", "amo", "ate", "ju"],
                "time": ["ao", "ati", "ala", "alo", "ale", "ali"]
            }
        }

        # Ako je poslednje slovo l onda menjamo 'time' da pocinje sa e i dodajemo na postojeci
        if base_str[-1] == "i":
            if base_str[-2:-1] in "l":
                suff_add = ["e" + x[1:] for x in suff_map["i"]["time"]]
                for i in suff_add:
                    suff_map["i"]["time"].append(i)
            if base_str[-2:-1] in "cč":
                suff_add = ["a" + x[1:] for x in suff_map["i"]["time"]]
                suff_map["i"]["time"] = []
                for i in suff_add:
                    suff_map["i"]["time"].append(i)
        
                
        suff_key = base_str[-1]
        new_base = base_str[:-1]

        if only_present:
            for i in suff_map:
                suff_map[i]["time"] = []

        suff = ""
        if suff_key in suff_map:
            suff = "\n".join(suff_map[suff_key]["suff"]) + "\n" + "\n".join(suff_map[suff_key]["time"])
        
        self.txt_base.setText(new_base)
        self.txt_end.setText(suff.strip())

    def _clear_text(self):
        self.txt_end.setText("")

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
        if self.txt_edit_add_end.text():
            self.btn_edit_add_end.setEnabled(True)
        else:
            self.btn_edit_add_end.setEnabled(False)

    def txt_edit_add_beg_text_changed(self):
        if self.txt_edit_add_beg.text():
            self.btn_edit_add_beg.setEnabled(True)
        else:
            self.btn_edit_add_beg.setEnabled(False)

    def txt_edit_replace_text_changed(self):
        self._set_buttons_for_replace()

    def txt_edit_in_string_click(self):
         self._set_buttons_for_replace()

    def chk_edit_case_state_changed(self):
        self._set_buttons_for_replace()

    def _set_buttons_for_replace(self):
        if not self.txt_edit_replace.text():
            self.btn_edit_replace.setEnabled(False)
            self.btn_edit_replace_add.setEnabled(False)
            return
        
        if not self.txt_edit_in_string.text():
            if self.txt_edit_replace.text():
                self.btn_edit_replace.setEnabled(True)
                self.btn_edit_replace_add.setEnabled(True)
            else:
                self.btn_edit_replace.setEnabled(False)
                self.btn_edit_replace_add.setEnabled(False)
        else:
            if self.txt_edit_in_string.text().find(self.txt_edit_replace.text()) >= 0:
                self.btn_edit_replace.setEnabled(True)
                self.btn_edit_replace_add.setEnabled(True)
            else:
                self.btn_edit_replace.setEnabled(False)
                self.btn_edit_replace_add.setEnabled(False)

    def btn_edit_output_click(self):
        if self.frm_edit.isVisible():
            self.frm_edit.setVisible(False)
        else:
            self.frm_edit.setVisible(True)

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

    def btn_base_text_changed(self):
        if self.txt_base.text():
            self.btn_generate.setEnabled(True)
        else:
            self.btn_generate.setEnabled(False)

    def txt_output_text_changed(self):
        if self.txt_output.toPlainText():
            if self.txt_output.toPlainText()[-1] != "\n":
                self.txt_output.setText(self.txt_output.toPlainText() + "\n")
            self.btn_copy.setEnabled(True)
        else:
            self.btn_copy.setEnabled(False)

    def btn_copy_click(self):
        self.get_appv("clipboard").setText(self.txt_output.toPlainText())
        self.btn_copy.setEnabled(False)

    def btn_clear_output_click(self):
        self.txt_output.setText("")

    def btn_clear_end_click(self):
        self.txt_end.setText("")

    def btn_clear_beggining_click(self):
        self.txt_beggining.setText("")

    def btn_clear_base_click(self):
        self.txt_base.setText("")

    def btn_cancel_click(self):
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
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

        return super().closeEvent(a0)

    def _load_win_position(self):
        if "definition_editor_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("definition_editor_win_geometry")
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

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
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

        self.btn_clear_base: QPushButton = self.findChild(QPushButton, "btn_clear_base")
        self.btn_clear_end: QPushButton = self.findChild(QPushButton, "btn_clear_end")
        self.btn_clear_beggining: QPushButton = self.findChild(QPushButton, "btn_clear_beggining")
        self.btn_clear_output: QPushButton = self.findChild(QPushButton, "btn_clear_output")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_generate: QPushButton = self.findChild(QPushButton, "btn_generate")
        self.btn_copy: QPushButton = self.findChild(QPushButton, "btn_copy")
        self.btn_first_letter: QPushButton = self.findChild(QPushButton, "btn_first_letter")

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

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("def_editor_lbl_title_text"))
        self.lbl_base.setText(self.getl("def_editor_lbl_base_text"))
        self.lbl_output.setText(self.getl("def_editor_lbl_output_text"))

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

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()

        self.lbl_title.setStyleSheet(self.getv("def_editor_lbl_title_stylesheet"))
        self.lbl_base.setStyleSheet(self.getv("def_editor_lbl_base_stylesheet"))
        self.lbl_output.setStyleSheet(self.getv("def_editor_lbl_output_stylesheet"))

        self.txt_base.setStyleSheet(self.getv("def_editor_txt_base_stylesheet"))
        self.txt_end.setStyleSheet(self.getv("def_editor_txt_end_stylesheet"))
        self.txt_beggining.setStyleSheet(self.getv("def_editor_txt_beggining_stylesheet"))
        self.txt_output.setStyleSheet(self.getv("def_editor_txt_output_stylesheet"))
        self.txt_output.setContextMenuPolicy(Qt.NoContextMenu)

        self.btn_cancel.setStyleSheet(self.getv("def_editor_btn_cancel_stylesheet"))
        self.btn_clear_base.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_clear_end.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_clear_beggining.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_clear_output.setStyleSheet(self.getv("def_editor_btn_clear_stylesheet"))
        self.btn_first_letter.setStyleSheet(self.getv("def_editor_btn_first_letter_stylesheet"))
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


class AddDefinition(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_obj, expression: str = "", definition_id: int = 0, application_modal: bool = False, crash_dict: dict = None, *args, **kwargs):
        super().__init__(parent_obj, *args, **kwargs)
        
        if application_modal:
            self.setWindowModality(Qt.ApplicationModal)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_obj = parent_obj
        self._expression = expression
        self._definition_id = definition_id
        self._data_changed = False
        self._dont_clear_menu = False
        # self._illegal_entry = False
        self._checking_in_progress = False
        self._syn_text = ""
        self._txt_desc_mark_mode = False
        self._text_handler_working = False
        self._clip: utility_cls.Clipboard = self.get_appv("cb")
        self._menu_event_completed = False
        self._force_exit = False
        self._title_and_chk_box_text = []

        self.sound_image_added = QSound(self.getv("def_add_auto_added_image_sound_file_path"))
        self.sound_image_add_error = QSound(self.getv("def_add_auto_added_image_error_sound_file_path"))
        self.sound_auto_image_on = QSound(self.getv("def_add_auto_added_image_on_sound_file_path"))
        self.sound_auto_image_off = QSound(self.getv("def_add_auto_added_image_off_sound_file_path"))
        self.sound_auto_image_maximum = QSound(self.getv("def_add_auto_added_image_maximum_sound_file_path"))
        self.sound_pop_up = QSound(self.getv("notification_pop_up_sound_file_path"))
        self.sound_completed = QSound(self.getv("completed_sound_file_path"))
        self.sound_select = QSound(self.getv("select_sound_file_path"))

        db_def = db_definition_cls.Definition(self._stt)
        self.exp_list = db_def.get_list_of_all_expressions()

        # Load GUI
        uic.loadUi(self.getv("definition_add_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()
        self._char_format_syn = self.txt_syn.textCursor().charFormat()
        
        self._synonyms_hint = SynonymHint(self._stt, self, self.txt_syn)

        self._text_handler = text_handler_cls.TextHandler(self._stt, self.txt_desc, self)

        self._desc_cf = self.txt_desc.textCursor().charFormat()

        self._load_win_position()

        # Connect events with slots
        self.keyPressEvent = self._key_press

        self.txt_expression.textChanged.connect(self._txt_expression_text_changed)
        self.txt_expression.returnPressed.connect(self._txt_expression_return_pressed)
        self.txt_desc.textChanged.connect(self._txt_desc_text_changed)
        self.txt_desc.mouseDoubleClickEvent = self._txt_desc_double_click
        self.txt_desc.mouseMoveEvent = self._txt_desc_mouse_move
        self.txt_syn.textChanged.connect(self._txt_syn_text_changed)
        self.txt_syn.mouseReleaseEvent = self.txt_syn_mouse_release
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_add_media.clicked.connect(self._btn_add_media_click)
        # self.btn_save.clicked.connect(self._btn_save_click)
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
        
        self.show()

        QCoreApplication.processEvents()
        check_expression = self._definition_id_for_expression(self._expression)
        if check_expression:
            if len(check_expression) == 1:
                self._expression = self._get_definition_name(check_expression[0])
            else:
                result = self.user_select_definition(check_expression)
                if result:
                    self._expression = self._get_definition_name(result)
                else:
                    self._expression = ""
        else:
            if self._expression and self._expression[0] != self._expression[0].upper():
                self._expression = self._expression.capitalize()


        self.frm_loading.setVisible(True)
        self.horizontalLayout.addWidget(self.frm_loading)
        QCoreApplication.processEvents()
        self._populate_widgets()
        self.frm_loading.setVisible(False)

        if crash_dict:
            self._load_crash_data(crash_dict)
        else:
            self.txt_expression.setFocus()
            self.exec_()

    def _btn_syn_find_click(self):
        self.sound_select.play()
        images = []
        for i in range(self.horizontalLayout.count()):
            img_src = self.horizontalLayout.itemAt(i).widget().img_src
            images.append(img_src)

        definition_data_find_cls.DefinitionFinder(parent_widget=self, 
                                                  settings=self._stt, 
                                                  search_string=self.txt_expression.text(), 
                                                  syn_list=self.txt_syn.toPlainText(),
                                                  image_list=images,
                                                  update_def_function=self.definition_update_function)

    def definition_update_function(self, data: dict):
        # Text
        if data.get("update_text", None):
            if data["text"]:
                self.txt_desc.setPlainText(data["text"])

        # Images
        if data.get("update_images", None):
            if data["replace_images"]:
                # Delete existing images
                for _ in range(self.horizontalLayout.count()):
                    item = self.horizontalLayout.itemAt(0)
                    item.widget().close()
                    item.widget().deleteLater()
                    self.horizontalLayout.removeItem(item)

            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_working_text"))
            QCoreApplication.processEvents()
            silent_add = utility_cls.SilentPictureAdd(self._stt)

            not_added_images = ""

            for image in data["images"]:
                result = silent_add.add_image(source=image)
                if result:
                    if self._is_media_already_added(result):
                        self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                        continue

                    self._add_image_to_layout(result)
                    self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                    self.sound_image_added.play()
                else:
                    self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                    not_added_images += f"{image}\n"

                if not_added_images:
                    QMessageBox.warning(self, self.getl("definition_add_error_online_img_add_title"), self.getl("definition_add_error_online_img_add_text") + f"\n{not_added_images}")
                
        # Synonyms
        if data.get("update_syn", None):
            text = ""
            if data["append_syn"]:
                text = self.txt_syn.toPlainText() + "\n\n"
            text += data["syn"]
            self.txt_syn.setPlainText(text)

        # Return data
        if data.get("return_data", None):
            images = []
            for i in range(self.horizontalLayout.count()):
                img_src = self.horizontalLayout.itemAt(i).widget().img_src
                images.append(img_src)
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
            self._dont_clear_menu = True
            result = self._synonyms_hint.show_contex_menu(base_string=self.txt_expression.text())
            if result:
                self._dont_clear_menu = True
                utility_cls.MessageInformation(self._stt, self, result)
        QTextEdit.mouseReleaseEvent(self.txt_syn, e)

    def signalNewDefinitionAdded_event(self):
        db_def = db_definition_cls.Definition(self._stt)
        self.exp_list = db_def.get_list_of_all_expressions()

        self._change_widgets_if_illegal_entry()

        if self.txt_desc.toPlainText():
            self._txt_desc_text_changed()

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

    def _signal_close_all_definitions(self):
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
            self.set_appv("menu", menu_dict)
            self._dont_clear_menu = True
            utility_cls.ContextMenu(self._stt, self)
            result = self.get_appv("menu")["result"]
            if result == 10:
                self._btn_save_click(close_dialog=True)
            elif result == 20:
                self._btn_save_click(close_dialog=False)
        elif e.button() == Qt.LeftButton:
            self._btn_save_click()
        else:
            QPushButton.mouseReleaseEvent(self.btn_save, e)

    def btn_auto_add_stop_click(self):
        self._stop_adding_images = True

    def chk_auto_add_state_changed(self):
        if self.chk_auto_add.isChecked():
            self.sound_auto_image_on.play()
        else:
            self.sound_auto_image_off.play()

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
            self._message_too_many_images()
            return

        self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_working_text"))
        QCoreApplication.processEvents()
        silent_add = utility_cls.SilentPictureAdd(self._stt)
        result = silent_add.add_image()
        if result:
            if self._is_media_already_added(result):
                self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
                self.get_appv("log").write_log(f"DefinitionAdd. An attempt is made to add an image that has already been added to the definition. Media ID: {result}")
                self.sound_image_add_error.play()
                return
            self._add_image_to_layout(result)
            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
            self.sound_image_added.play()
        else:
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
        utility_cls.Selection(self._stt, self, selection_dict=select_dict)
        urls = self.get_appv("selection")["result"]

        # If the user has not selected any image, return false
        if not urls:
            return False
        
        # Start adding images
        silent_add = utility_cls.SilentPictureAdd(self._stt)

        not_added = []
        max_img_reached = False
        self._stop_adding_images = False

        for idx, url in enumerate(urls):
            # Notify the user of progress
            msg = self.getl("multi_urls_user_msg_text").replace("#1", str(idx + 1)).replace("#2", str(len(urls)))
            self._multi_urls_add_user_msg(msg)
            QCoreApplication.processEvents()
            
            # If the user has stopped adding images, exit the loop
            if self._stop_adding_images:
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
                    continue
                # Add image
                self._add_image_to_layout(result)
                self.sound_image_added.play()
            else:
                # In case of error, inform the user with a sound signal and continue with the next image
                txt = f'{url}  {self.getl("auto_adding_images_not_added_reason_text")}: {self.getl("auto_adding_images_not_added_reason_load_error_text")}'
                not_added.append(txt)
                self.sound_image_add_error.play()

        # If the maximum number of images is reached, notify the user with a message
        if max_img_reached:
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
            
            self.sound_pop_up.play()
            utility_cls.Selection(self._stt, self, selection_dict=select_dict)

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
        self.sound_select.play()
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

    def _btn_save_click(self, close_dialog: bool = True):
        if self.txt_expression.text().strip() == "":
            return
        
        self.lbl_auto_add_msg.setText(self.getl("add_def_lbl_auto_add_msg_saving_text"))
        self.lbl_auto_add_msg.resize(self.lbl_auto_add_msg.width(), self.frm_auto_add.height())
        self.btn_auto_add_stop.setVisible(False)
        self.frm_auto_add.setVisible(True)
        QCoreApplication.processEvents()

        self.txt_syn.setText(self.txt_syn.toPlainText() + "\n")
        self._change_widgets_if_illegal_entry()
        # if self._illegal_entry:
        #     data_dict = {
        #         "title": self.getl("definition_add_illegal_msg_title"),
        #         "text": self.getl("definition_add_illegal_msg_text")
        #     }
        #     self._dont_clear_menu = True
        #     utility_cls.MessageInformation(self._stt, self, data_dict)
        #     self.lbl_auto_add_msg.setText("Auto add")
        #     self.lbl_auto_add_msg.resize(self.lbl_auto_add_msg.width(), 40)
        #     self.btn_auto_add_stop.setVisible(True)
        #     self.frm_auto_add.setVisible(False)
        #     return

        # Find media IDs
        media_ids = []
        default_item = None
        for i in range(self.horizontalLayout.count()):
            media_ids.append(self.horizontalLayout.itemAt(i).widget()._media_id)
            if self.horizontalLayout.itemAt(i).widget()._is_default:
                default_item = self.horizontalLayout.itemAt(i).widget()._media_id

        # Make similar expressions list
        syn_list = [x.strip() for x in self.txt_syn.toPlainText().split("\n") if x != ""]

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
            db_def.update_definition(definition_id, def_dict=def_dict)
        else:
            db_def.add_new_definition(def_dict)
        self.get_appv("log").write_log(f"DefinitionAdd. Definition Saved. Definition ID: {def_dict['name']}")
        
        # Close dialog
        self.get_appv("signal").new_definition_added()
        self._data_changed = False

        self.lbl_auto_add_msg.resize(self.lbl_auto_add_msg.width(), 40)
        self.btn_auto_add_stop.setVisible(True)
        self.frm_auto_add.setVisible(False)

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
        self._show_images(item._media_id)

    def item_left_click_event(self, media_id: int, is_default: bool, item: QLabel):
        pass

    def item_right_click_event(self, media_id: int, is_default: bool, item: QLabel):
        db_media = db_media_cls.Media(self._stt, media_id)
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
        elif self.get_appv("menu")["result"] == 20:
            self.chk_auto_add.setEnabled(True)
            self.chk_auto_add.setText(self.getl("definition_add_chk_auto_add_text"))
            for i in range(self.horizontalLayout.count()):
                if self.horizontalLayout.itemAt(i).widget()._media_id == item._media_id:
                    self.horizontalLayout.removeItem(self.horizontalLayout.itemAt(i))
                    break
            item.close()
        elif self.get_appv("menu")["result"] == 30:
            self._btn_add_media_click()
        elif self.get_appv("menu")["result"] == 40:
            self._show_images(item._media_id)
        elif self.get_appv("menu")["result"] == 50:
            utility_cls.PictureInfo(self._stt, self, item._media_id)
        elif self.get_appv("menu")["result"] == 60:
            self._paste_images()
        elif self.get_appv("menu")["result"] == 70:
            if self.chk_auto_add.isChecked():
                self.chk_auto_add.setChecked(False)
            self._clip.copy_to_clip(media_id)
        elif self.get_appv("menu")["result"] == 80:
            if self.chk_auto_add.isChecked():
                self.chk_auto_add.setChecked(False)
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif self.get_appv("menu")["result"] == 90:
            self._clip.clear_clip()
        
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
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _load_win_position(self):
        if "add_definition_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("add_definition_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def _btn_add_media_click(self):
        self.sound_select.play()
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
        if "add_definition_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("add_definition_win_geometry", {}, save_to_file=True)

        g = self.get_appv("add_definition_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        if not self._can_exit():
            a0.ignore()
            return None

        self.chk_auto_add.setChecked(False)
        crash_dict = self._stt.custom_dict_load(self.getv("crash_file_path"))
        if self.get_appv("user").username in crash_dict:
            if "def" in crash_dict[self.get_appv("user").username]:
                crash_dict[self.get_appv("user").username].pop("def")
                self._stt.custom_dict_save(self.getv("crash_file_path"), crash_dict)
        return super().closeEvent(a0)

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
        self._change_widgets_if_def_exist()
            
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
                if self.txt_syn.toPlainText()[-1] == "\n":
                    self._change_widgets_if_illegal_entry()
                elif self.txt_syn.textCursor().position() != len(self.txt_syn.toPlainText()):
                    self._change_widgets_if_illegal_entry()
                elif abs(len(self.txt_syn.toPlainText()) - len(self._syn_text)) > 1:
                    self._change_widgets_if_illegal_entry()
        self._syn_text = self.txt_syn.toPlainText()

    def _change_widgets_if_illegal_entry(self) -> bool:
        self._checking_in_progress = True
        has_data_in_other_defs = False
        db_def = db_definition_cls.Definition(self._stt)
        def_id = db_def.find_definition_by_name(self.txt_expression.text(), populate_properties=True)
        expression_text = self.txt_expression.text().lower()
        if self.txt_expression.text():
            for item in self.exp_list:
                if item[1] != def_id:
                    if item[0] == expression_text:
                        has_data_in_other_defs = True
                        self.txt_expression.setStyleSheet(self.getv("definition_txt_expr_part_of_other_def_stylesheet"))
                        break

        if self.txt_syn.toPlainText():
            syn_list = [[x.strip(), x.strip().lower()] for x in self.txt_syn.toPlainText().split("\n") if len(x) != ""]
            ill_items = []
            for item in self.exp_list:
                if item[1] != def_id:
                    for i in syn_list:
                        if i[1] == item[0]:
                            ill_items.append(i[0])
            cur_pos = self.txt_syn.textCursor().position()
            if ill_items:
                txt = self.txt_syn.toPlainText()
                for word in ill_items:
                    start_pos = txt.find(word)
                    while start_pos >= 0:
                        if txt[start_pos + len(word):start_pos + len(word) + 1] == "\n":
                            cur = self.txt_syn.textCursor()
                            cf = QTextCharFormat()
                            color = QColor()
                            # color.setNamedColor("red")
                            # cf.setBackground(color)
                            color.setNamedColor("#ff9c38")
                            cf.setForeground(color)
                            cur.setPosition(start_pos)
                            cur.movePosition(cur.Right, cur.KeepAnchor, len(word))
                            cur.setCharFormat(cf)
                            self.txt_syn.setTextCursor(cur)
                        start_pos = txt.find(word, start_pos + len(word))
            else:
                cur = self.txt_syn.textCursor()
                cur.setPosition(0)
                cur.movePosition(cur.Right, cur.KeepAnchor, len(self.txt_syn.toPlainText()))
                cur.setCharFormat(self._char_format_syn)
                self.txt_syn.setTextCursor(cur)

            cur = self.txt_syn.textCursor()
            cur.clearSelection()
            cur.setPosition(cur_pos)
            cur.setCharFormat(self._char_format_syn)
            self.txt_syn.setTextCursor(cur)

        if self.txt_expression.text():
            self.btn_add_media.setEnabled(True)
            self.btn_save.setEnabled(True)
        self._checking_in_progress = False

        return has_data_in_other_defs

    def _txt_desc_text_changed(self):
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
        self._text_handler.show_definition_on_mouse_hover(e)
        QTextEdit.mouseMoveEvent(self.txt_desc, e)

    def _btn_format_desc_click(self):
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
        
        return txt

    def _remove_wiki_from_text(self, txt: str) -> str:
        items = self._find_wiki_links(txt)
        
        for i in items:
            txt = txt[:i[0]] + "`" * len(i[2]) + txt[i[1]:]
        
        txt = txt.replace("`", "")

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

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()
        self._define_labels_apperance(self.lbl_title, "definition_add_title")
        
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
        super().__init__(parent_obj, *args, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

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

        # Connect events with slots
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
        self.exec_()

    def _signal_close_all_definitions(self):
        self.close()

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
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

    def _btn_edit_click(self):
        edit_def = AddDefinition(self._stt, self, definition_id=self._definition_id)
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
            self._message_too_many_images()
            return
        result = []
        utility_cls.PictureAdd(self._stt, self, result)
        if result:
            for i in range(self.horizontalLayout.count()):
                if self.horizontalLayout.itemAt(i).widget()._media_id == result[0]:
                    self._message_image_exist()
                    return
            self._data_changed = True
            lbl_pic = ImageThumbItem(self._stt, self, result[0], self._definition_id)
            self.horizontalLayout.addWidget(lbl_pic)

            w = (self.getv("definition_image_thumb_size") + self.horizontalLayout.spacing()) * self.horizontalLayout.count() + 25
            self._widget.setFixedSize(w, self.getv("definition_image_thumb_size") + 10)
            self.area.setFixedHeight(self._widget.height() + 24)
            
            db_media = db_media_cls.Media(self._stt, result[0])
            self._show_image_in_main_label(db_media.media_file)

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

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()
        self._define_labels_apperance(self.lbl_name, "definition_view_name")

        self._define_buttons_apperance(self.btn_edit, "definition_view_btn_edit")
        self._define_buttons_apperance(self.btn_ok, "definition_view_btn_ok")
        self._define_buttons_apperance(self.btn_size, "definition_view_btn_size")

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
    def __init__(self, settings: settings_cls.Settings, parent_widget, definition_id: int = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_obj = parent_widget
        if isinstance(definition_id, list):
            self._definition_id = None
        else:
            self._definition_id = definition_id
        self._def_dict = self._get_def_dict()
        self._dont_clear_menu = False
        self._clip: utility_cls.Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("browse_def_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._populate_widgets()
        self._load_win_position()

        # Connect events with slots
        self.lst_def.currentItemChanged.connect(self._lst_def_current_item_changed)
        self.lst_def.contextMenuEvent = self.lst_def_context_menu
        self.lst_def.mouseDoubleClickEvent = self._lst_def_mouse_double_click
        self.btn_close.clicked.connect(self._btn_close_click)
        self.btn_edit.clicked.connect(self._btn_edit_click)
        self.btn_delete.clicked.connect(self._btn_delete_click)
        self.lbl_pic.mouseDoubleClickEvent = self.lbl_pic_double_click
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.txt_find.textChanged.connect(self.txt_find_text_changed)
        self.txt_find.returnPressed.connect(self.txt_find_return_pressed)
        self.txt_desc.mouseDoubleClickEvent = self.txt_desc_mouse_double_click

        self.get_appv("signal").signalCloseAllDefinitions.connect(self._signal_close_all_definitions)

        self.show()
        self._load_passed_definitions(definition_id)
        self.txt_find.setFocus()

    def _signal_close_all_definitions(self):
        self.close()

    def _lst_def_mouse_double_click(self, e: QtGui.QMouseEvent):
        self._btn_edit_click()
        QListWidget.mouseDoubleClickEvent(self.lst_def, e)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
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

    def txt_find_text_changed(self):
        txt = self.txt_find.text().lower()
        
        for item in self.lst_def.findItems("", Qt.MatchFlag.MatchContains):
            if txt:
                if self._filter_apply(txt, self._def_dict[item.data(Qt.UserRole)].lower()):
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            else:
                item.setHidden(False)
        
        self._update_counter()

    def _load_passed_definitions(self, def_ids: list):
        if not isinstance(def_ids, list):
            return
        for item in self.lst_def.findItems("", Qt.MatchFlag.MatchContains):
            if item.data(Qt.UserRole) in def_ids:
                item.setHidden(False)
            else:
                item.setHidden(True)
        
        self._update_counter()

    def txt_find_return_pressed(self):
        db_def = db_definition_cls.Definition(self._stt)
        defs = db_def.get_list_of_all_descriptions()

        txt = self.txt_find.text().lower()
        
        for item in self.lst_def.findItems("", Qt.MatchFlag.MatchContains):
            if txt:

                find_in = self._def_dict[item.data(Qt.UserRole)]
                for i in defs:
                    if i[0] == item.data(Qt.UserRole):
                        find_in += " " + i[1]
                
                if self._filter_apply(txt, find_in):
                    item.setHidden(False)
                else:
                    item.setHidden(True)
            else:
                item.setHidden(False)
        
        self._update_counter()

    def _get_def_dict(self) -> dict:
        db_def = db_definition_cls.Definition(self._stt)
        
        def_dict = {}
        for i in db_def.get_list_of_all_expressions():
            if i[1] in def_dict:
                def_dict[i[1]] = def_dict[i[1]] + f"[{i[0]}] "
            else:
                def_dict[i[1]] = f"[{i[0]}] "
        return def_dict

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
        if e.button() == Qt.RightButton:
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

        menu_dict = {
            "position": QCursor.pos(),
            "selected": [20],
            "separator": [20, 40],
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
                ]
            ]
        }
        self._dont_clear_menu = True
        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self)

        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        media_ids = db_def.definition_media_ids

        if self.get_appv("menu")["result"] == 10:
            if self.lbl_pic.objectName() and media_ids:
                utility_cls.PictureView(self._stt, self, media_ids, int(self.lbl_pic.objectName()))
        if self.get_appv("menu")["result"] == 15:
            if self.lbl_pic.objectName() and media_ids:
                utility_cls.PictureInfo(self._stt, self, media_id=int(self.lbl_pic.objectName()))
        if self.get_appv("menu")["result"] == 20:
            if media_ids:
                media_ids = [[x] for x in db_def.definition_media_ids]
                utility_cls.PictureBrowse(self._stt, self, media_list=media_ids)
        if self.get_appv("menu")["result"] == 30:
            self._rename_definition()
        if self.get_appv("menu")["result"] == 40:
            self._btn_edit_click()
        if self.get_appv("menu")["result"] == 70:
            self._clip.copy_to_clip(int(self.lbl_pic.objectName()))
        if self.get_appv("menu")["result"] == 80:
            self._clip.copy_to_clip(int(self.lbl_pic.objectName()), add_to_clip=True)
        if self.get_appv("menu")["result"] == 90:
            self._clip.clear_clip()

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
            "description": desc
        }
        self._dont_clear_menu = True
        utility_cls.InputBoxSimple(self._stt, self, input_dict)
        if not input_dict["result"]:
            return
        
        def_dict = {
            "name": input_dict["result"]
        }
        db_def.update_definition(self._definition_id, def_dict=def_dict)

        self.lst_def.currentItem().setText(db_def.definition_name)
        self._populate_data(self._definition_id)

        notif_dict = {
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
        
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)
        def_name = db_def.definition_name
        db_def.delete_definition(self._definition_id)
        row = self.lst_def.currentRow()
        
        if row + 1 < self.lst_def.count():
            row += 1
        elif row + 1 == self.lst_def.count():
            row -= 1
        
        if row < 0:
            def_id = None
        else:
            def_id = self.lst_def.item(row).data(Qt.UserRole)
        self._definition_id = def_id
        
        self._populate_widgets(def_id=def_id)
        ntf_dict = {
            "title": "",
            "text": self.getl("browse_def_notiff_item_deleted_text").replace("#1", def_name),
            "timer": 2000
        }
        self.get_appv("signal").new_definition_added()
        utility_cls.Notification(self._stt, self, ntf_dict)

    def _btn_close_click(self):
        self.close()

    def _btn_edit_click(self):
        if self.lst_def.currentItem() is not None:
            self._definition_id = self.lst_def.currentItem().data(Qt.UserRole)
            AddDefinition(self._stt, self, definition_id=self._definition_id)
            self._populate_widgets(self._definition_id)
            self.txt_find_text_changed()
        else:
            AddDefinition(self._stt, self)
            self._populate_widgets(self._definition_id)
            self.txt_find_text_changed()

    def _lst_def_current_item_changed(self, x, y):
        self._update_counter()
        if self.lst_def.currentItem() is not None:
            self._populate_data(self.lst_def.currentItem().data(Qt.UserRole))

    def _update_counter(self):
        total = 0
        active = 0
        for item in self.lst_def.findItems("", Qt.MatchFlag.MatchContains):
            total += 1
            if not item.isHidden():
                active += 1
        self.lbl_count.setText(self.getl("browse_def_lbl_count_text").replace("#1", str(active)).replace("#2", str(total)))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if "browse_def_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("browse_def_win_geometry", {}, save_to_file=True)

        g = self.get_appv("browse_def_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        
        return super().closeEvent(a0)

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
        self.btn_edit.move(w - 180, h - 30)
        self.btn_delete.move(w - 270, h - 30)
        # List
        self.lst_def.resize(int(w * scale_left), h - 120)
        # Counter
        self.lbl_count.move(10, h - 30)
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
        if def_id is None:
            def_id = self._definition_id

        db_def = db_definition_cls.Definition(self._stt, def_id=def_id)
        defs = list(db_def.get_list_of_all_definitions())
        defs.sort(key = lambda name: name[1].lower())

        self.lst_def.clear()
        row = None
        for idx, definition in enumerate(defs):
            item = QListWidgetItem()
            item.setText(definition[1])
            item.setData(Qt.UserRole, definition[0])
            self.lst_def.addItem(item)
            if def_id == definition[0]:
                row = idx
        if row:
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
            img.load(self.getv("browse_def_win_icon_path"))
            self.lbl_pic.setPixmap(img)
            self.lbl_name.setText("")
            self.txt_desc.setText("")
            return
        else:
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

    def _setup_widgets_apperance(self):
        self._define_definition_win_apperance()
        
        self._define_labels_apperance(self.lbl_name, "browse_def_lbl_title")
        self._define_labels_apperance(self.lbl_name, "browse_def_lbl_name")
        self._define_labels_apperance(self.lbl_count, "browse_def_lbl_count")

        self._define_buttons_apperance(self.btn_edit, "browse_def_btn_edit")
        self._define_buttons_apperance(self.btn_delete, "browse_def_btn_delete")
        self._define_buttons_apperance(self.btn_close, "browse_def_btn_close")

        self._define_text_box_apperance(self.txt_desc, "browse_def_txt_desc")
        self._define_text_box_apperance(self.txt_find, "browse_def_txt_find")
        self._define_list_apperance(self.lst_def, "browse_def_lst_def")

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
        super().__init__(parent_widget, *args, **kwargs)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

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

        self._load_win_position()

        # Connect events with slots
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
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
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

        self.get_appv("log").write_log(f"All Images: {self._expression} ({len(page.images)} images)")
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
        if "find_def_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("find_def_win_geometry", {}, save_to_file=True)

        g = self.get_appv("find_def_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        
        return super().closeEvent(a0)

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

    def _setup_widgets_apperance(self):
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

