from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QGridLayout, QWidget, 
                             QSizePolicy, QListWidget, QFileDialog, QDialog, QLabel, QListWidgetItem, 
                             QDesktopWidget, QLineEdit, QCalendarWidget, QHBoxLayout, QComboBox, 
                             QProgressBar, QCheckBox, QFileIconProvider, QTreeWidget, QTreeWidgetItem, 
                             QRadioButton, QGroupBox, QTabWidget, QAbstractItemView)
from PyQt5.QtGui import (QIcon, QFont, QFontMetrics, QPixmap, QCursor, QImage, QClipboard, QColor, QCloseEvent, QMouseEvent, QWheelEvent, QTextCursor)
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QObject, QCoreApplication, QRect,QPoint, QDate, QFileInfo, QMimeDatabase
from PyQt5 import uic, QtGui, QtCore

import json

import settings_cls
import utility_cls
import db_media_cls
import db_record_cls
import db_record_data_cls
import db_definition_cls
import db_tag_cls
import UTILS
import qwidgets_util_cls


class Compare(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget, data: dict, reset_compare_info_data_only: bool = False):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget)

        if reset_compare_info_data_only:
            self.create_compare_info_var(reset=True)
            return
        
        # Define other variables
        self._parent_widget = parent_widget
        self.data = data
        self.result = None
        self.update_checkboxes_info = False

        # Load GUI
        uic.loadUi(self.getv("compare_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_appearance()

        self._load_win_position()

        self.load_widgets_handler()

        self.populate_widgets()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.btn_abort.clicked.connect(self.btn_abort_click)
        self.btn_tag_new.clicked.connect(self.btn_tag_new_click)
        self.btn_tag_old.clicked.connect(self.btn_tag_old_click)
        self.txt_rename.textChanged.connect(self.txt_rename_text_changed)
        self.chk_item_default.stateChanged.connect(self.chk_item_default_state_changed)
        self.chk_session_default.stateChanged.connect(self.chk_session_default_state_changed)

        UTILS.LogHandler.add_log_record("#1: Dialog initialized. Action=#2", ["Compare", self.data.get("action")])

    def chk_item_default_state_changed(self, e):
        self._set_checkboxes_appearance()
        if self.update_checkboxes_info:
            if self.chk_item_default.checkState() == Qt.Checked:
                self.get_appv("compare_info")[self.data["action"]]["item_action"] = True
                if int(self.data["refer_id"]) not in self.get_appv("compare_info")[self.data["action"]]["items"]:
                    self.get_appv("compare_info")[self.data["action"]]["items"].append(int(self.data["refer_id"]))
            else:
                self.get_appv("compare_info")[self.data["action"]]["item_action"] = True
                if int(self.data["refer_id"]) in self.get_appv("compare_info")[self.data["action"]]["items"]:
                    self.get_appv("compare_info")[self.data["action"]]["items"].remove(int(self.data["refer_id"]))
    
    def chk_session_default_state_changed(self, e):
        self._set_checkboxes_appearance()
        if self.update_checkboxes_info:
            if self.chk_session_default.checkState() == Qt.Checked:
                self.get_appv("compare_info")[self.data["action"]]["session_action"] = True
            else:
                self.get_appv("compare_info")[self.data["action"]]["session_action"] = False

    def txt_rename_text_changed(self):
        if self.txt_rename.text().strip().lower() in self.data["validator"]:
            self.txt_rename.setStyleSheet("QLineEdit {color: #aa0000; background-color: #005500;} QLineEdit:hover {background-color: #007400;}")
            self.btn_tag_new.setDisabled(True)
        else:
            self.txt_rename.setStyleSheet("QLineEdit {color: #ffff00; background-color: #005500;} QLineEdit:hover {background-color: #007400;}")
            self.btn_tag_new.setDisabled(False)

    def btn_abort_click(self):
        self.result = None
        self.create_compare_info_var(reset=True)
        self.close()
    
    def btn_tag_new_click(self):
        if self.data["action"] == "definition":
            self.result = self.txt_rename.text()
            UTILS.LogHandler.add_log_record("#1: Definition renamed to #2.", ["Compare", self.txt_rename.text()])
        elif self.data["action"] == "append":
            self.result = False
        else:
            self.result = 0
        
        if self.get_appv("compare_info").get(self.data["action"]) is not None:
            self.get_appv("compare_info")[self.data["action"]]["action"] = "new"

        UTILS.LogHandler.add_log_record("#1: New data selected.", ["Compare"])
        self.close()
    
    def btn_tag_old_click(self):
        if self.data["action"] == "definition":
            self.result = self.data["old"]["name"]
        elif self.data["action"] == "append":
            self.result = True
        else:
            self.result = self.data["old"]["id"]
        
        if self.get_appv("compare_info").get(self.data["action"]) is not None:
            self.get_appv("compare_info")[self.data["action"]]["action"] = "old"

        UTILS.LogHandler.add_log_record("#1: Old data selected.", ["Compare"])
        self.close()

    def show_me(self) -> int | None:
        self.create_compare_info_var()
        if self.get_appv("compare_info").get(self.data["action"]) is not None:
            if self.get_appv("compare_info")[self.data["action"]]["item_action"] and int(self.data.get("refer_id")) in self.get_appv("compare_info")[self.data["action"]]["items"]:
                self.chk_item_default.setCheckState(Qt.Checked)
            else:
                self.chk_item_default.setCheckState(Qt.Unchecked)
            if self.get_appv("compare_info")[self.data["action"]]["session_action"]:
                self.chk_session_default.setCheckState(Qt.Checked)
            else:
                self.chk_session_default.setCheckState(Qt.Unchecked)
        
        run_result = self._run_default_action(self.data["action"])
        if run_result is not None:
            return self.result

        self.show()
        self._set_checkboxes_appearance()
        self._load_win_position()
        self.resize_me()
        self.update_checkboxes_info = True
        UTILS.LogHandler.add_log_record("#1: Dialog displayed.", ["Compare"])
        self.exec_()
        return self.result

    def _run_default_action(self, obj: str) -> str | None:
        if self.get_appv("compare_info").get(self.data["action"]) is None:
            return None
        
        if self.chk_item_default.checkState() == Qt.Checked:
            self.get_appv("compare_info")[obj]["item_action"] = True
        else:
            self.get_appv("compare_info")[obj]["item_action"] = False
        if self.chk_session_default.checkState() == Qt.Checked:
            self.get_appv("compare_info")[obj]["session_action"] = True
        else:
            self.get_appv("compare_info")[obj]["session_action"] = False

        if self.get_appv("compare_info")[obj]["action"] and self.get_appv("compare_info")[obj]["session_action"]:
            if self.get_appv("compare_info")[obj]["action"] == "new":
                self.btn_tag_new_click()
                return self.result
            if self.get_appv("compare_info")[obj]["action"] == "old":
                self.btn_tag_old_click()
                return self.result

        if self.get_appv("compare_info")[obj]["action"] and self.get_appv("compare_info")[obj]["item_action"] and int(self.data["refer_id"]) in self.get_appv("compare_info")[obj]["items"]:
            if self.get_appv("compare_info")[obj]["action"] == "new":
                self.btn_tag_new_click()
                return self.result
            if self.get_appv("compare_info")[obj]["action"] == "old":
                self.btn_tag_old_click()
                return self.result

        return None

    def create_compare_info_var(self, reset: bool = False):
        result = {
            "block": {
                "action": None,
                "item_action": None,
                "items": [],
                "session_action": None
            },
            "definition": {
                "action": None,
                "item_action": None,
                "items": [],
                "session_action": None
            },
            "file": {
                "action": None,
                "item_action": None,
                "items": [],
                "session_action": None
            },
            "image": {
                "action": None,
                "item_action": None,
                "items": [],
                "session_action": None
            },
            "tag": {
                "action": None,
                "item_action": None,
                "items": [],
                "session_action": None
            }
        }

        if "compare_info" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("compare_info", result, save_to_file=False)
        if reset:
            if "compare_info" in self._stt.app_setting_get_list_of_keys():
                self._stt.app_setting_delete("compare_info")
            self._stt.app_setting_add("compare_info", result, save_to_file=False)

    def populate_widgets(self):
        if self.data["action"] == "tag":
            text = self._populate_tag_label(self.data["new"])
            self.lbl_tag_new.setText(text)
            self.lbl_tag_new.setToolTip(text)
            text = self._populate_tag_label(self.data["old"])
            self.lbl_tag_old.setText(text)
            self.lbl_tag_old.setToolTip(text)
        elif self.data["action"] == "image":
            text = self._populate_image_label(self.data["new"])
            self.lbl_tag_new.setText("")
            self.lbl_tag_new.setToolTip(text)
            text = self._populate_image_label(self.data["old"])
            self.lbl_tag_old.setText("")
            self.lbl_tag_old.setToolTip(text)
        elif self.data["action"] == "file":
            text = self._populate_file_label(self.data["new"])
            self.lbl_tag_new.setText(text)
            self.lbl_tag_new.setToolTip(text)
            text = self._populate_file_label(self.data["old"])
            self.lbl_tag_old.setText(text)
            self.lbl_tag_old.setToolTip(text)
        elif self.data["action"] == "definition":
            text = self._populate_def_label(self.data["new"])
            self.lbl_tag_new.setText(text)
            self.lbl_tag_new.setToolTip(text)
            text = self._populate_def_label(self.data["old"])
            self.lbl_tag_old.setText(text)
            self.lbl_tag_old.setToolTip(text)
        elif self.data["action"] == "append":
            text = self._populate_append_label(None)
            self.lbl_tag_new.setText(text)
            self.lbl_tag_new.setToolTip(text)
            text = self._populate_append_label(self.data["old"])
            self.lbl_tag_old.setText(text)
            self.lbl_tag_old.setToolTip(text)
        elif self.data["action"] == "block":
            text = self._populate_block_label(self.data["new"])
            self.lbl_tag_new.setText(text)
            self.lbl_tag_new.setToolTip(text)
            text = self._populate_block_label(self.data["old"])
            self.lbl_tag_old.setText(text)
            self.lbl_tag_old.setToolTip(text)

    def _set_images(self):
        UTILS.WidgetUtility.set_image_to_label(self.data["new"]["file"], self.lbl_tag_new)
        UTILS.WidgetUtility.set_image_to_label(self.data["old"]["file"], self.lbl_tag_old)

    def _populate_append_label(self, data: str):
        text_to_html = UTILS.HTMLText.TextToHTML()
        text_to_html.general_rule.fg_color = "#ffca61"
        text_to_html.general_rule.font_size = 12

        if data is None:
            text = self.getl("compare_append_new")
            rule = UTILS.HTMLText.TextToHtmlRule(
                text = "#1",
                replace_with=self.getl("compare_append_new_delete"),
                fg_color="#9d0000"
            )
            text_to_html.add_rule(rule)
            text_to_html.set_text(text)
            return text_to_html.get_html()

        # Old archive text
        text_to_html.general_rule.fg_color = "#878787"
        text = "#----0\n"
        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#----0",
            replace_with=self.getl("compare_append_old"),
            fg_color="#ffca61"
        )
        text_to_html.add_rule(rule)
        
        count = 1
        if UTILS.FileUtility.ZIP_is_zipfile(data):
            zip_files = UTILS.FileUtility.ZIP_list_archive(data)

            if len(zip_files) == 0:
                file_id = "#" + "-" * (5 - len(str(count))) + str(count)
                text += file_id
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text=file_id,
                    replace_with=self.getl("compare_append_no_files"),
                    fg_color="#ffffff"
                )
                text_to_html.add_rule(rule)
                count += 1

            is_valid_archive = False
            for file in zip_files:
                file_id = "#" + "-" * (5 - len(str(count))) + str(count)
                
                text += f"[{file_id}], "

                if file == "tmp_export_data.json":
                    is_valid_archive = True
                    rule = UTILS.HTMLText.TextToHtmlRule(
                        text=file_id,
                        replace_with=file,
                        fg_color="#aaff00"
                    )
                else:
                    rule = UTILS.HTMLText.TextToHtmlRule(
                        text=file_id,
                        replace_with=file,
                        fg_color="#55ffff"
                    )
                text_to_html.add_rule(rule)

                count += 1
            
            if not is_valid_archive:
                file_id = "#" + "-" * (5 - len(str(count))) + str(count)
                text += file_id
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text=file_id,
                    replace_with=self.getl("compare_append_not_valid_archive"),
                    fg_color="#9d0000"
                )
                text_to_html.add_rule(rule)
                count += 1
                self.btn_tag_old.setDisabled(True)
        else:
            file_id = "#" + "-" * (5 - len(str(count))) + str(count)
            text += file_id
            rule = UTILS.HTMLText.TextToHtmlRule(
                text=file_id,
                replace_with=self.getl("compare_append_not_archive"),
                fg_color="#ffffff"
            )
            text_to_html.add_rule(rule)
            count += 1
            self.btn_tag_old.setDisabled(True)

        text = text.rstrip(" ,")
        text_to_html.set_text(text)
        
        return text_to_html.get_html()
          
    def _populate_def_label(self, data: dict):
        text = self.getl("compare_def_item_id")
        text += " = #---1\n"
        text += self.getl("compare_def_item_name") + ": #---2\n"
        text += self.getl("compare_def_item_syn") + ": \n#---3"

        text_to_html = UTILS.HTMLText.TextToHTML(text)
        text_to_html.general_rule.fg_color = "#ffca61"
        text_to_html.general_rule.font_size = 12

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---1",
            replace_with=str(data["id"]),
            fg_color="#aaffff",
            font_bold=True
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---2",
            replace_with=str(data["name"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---3",
            replace_with=str(data["synonyms"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def _populate_file_label(self, data: dict):
        text = self.getl("compare_file_item_id")
        text += " = #---1\n"
        text += self.getl("compare_file_item_name") + ": #---2\n"
        text += self.getl("compare_file_item_desc") + ": \n#---3\n"
        text += self.getl("compare_file_item_http") + ": \n#---4\n"
        text += self.getl("compare_file_item_file") + ": \n#---5\n"
        text += self.getl("compare_file_item_size") + ": #---6\n"
        text += self.getl("compare_file_item_created") + ": #---7\n"

        text_to_html = UTILS.HTMLText.TextToHTML(text)
        text_to_html.general_rule.fg_color = "#ffca61"
        text_to_html.general_rule.font_size = 12

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---1",
            replace_with=str(data["id"]),
            fg_color="#aaffff",
            font_bold=True
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---2",
            replace_with=str(data["name"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---3",
            replace_with=str(data["description"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---4",
            replace_with=str(data["http"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---5",
            replace_with=str(data["file"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        file_obj = UTILS.FileUtility.get_FileInformation_object(data["file"])

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---6",
            replace_with=file_obj.size(return_formatted_string=True) + f'  ({file_obj.size()} bytes)',
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---7",
            replace_with=str(file_obj.created_time()),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def _populate_image_label(self, data: dict):
        text = self.getl("compare_image_item_id")
        text += " = #---1\n"
        text += self.getl("compare_image_item_name") + ": #---2\n"
        text += self.getl("compare_image_item_desc") + ": \n#---3\n"
        text += self.getl("compare_image_item_http") + ": \n#---4\n"
        text += self.getl("compare_image_item_file") + ": \n#---5\n"

        text_to_html = UTILS.HTMLText.TextToHTML(text)
        text_to_html.general_rule.fg_color = "#ffca61"
        text_to_html.general_rule.font_size = 12

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---1",
            replace_with=str(data["id"]),
            fg_color="#aaffff",
            font_bold=True
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---2",
            replace_with=str(data["name"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---3",
            replace_with=str(data["description"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---4",
            replace_with=str(data["http"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---5",
            replace_with=str(data["file"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def _populate_tag_label(self, data: dict):
        text = "Tag ID = #---1\n"
        text += self.getl("compare_tag_item_name") + ": #---2\n"
        text += self.getl("compare_tag_item_desc") + ": \n#---3"

        text_to_html = UTILS.HTMLText.TextToHTML(text)
        text_to_html.general_rule.fg_color = "#ffca61"
        text_to_html.general_rule.font_size = 12

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---1",
            replace_with=str(data["id"]),
            fg_color="#aaffff",
            font_bold=True
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---2",
            replace_with=str(data["name"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---3",
            replace_with=str(data["description"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def _populate_block_label(self, data: dict):
        text = self.getl("compare_block_item_id")
        text += " = #---1\n"
        text += self.getl("compare_block_item_name") + ": #---2\n"
        text += self.getl("compare_block_item_desc") + ": \n#---3\n"

        text_to_html = UTILS.HTMLText.TextToHTML(text)
        text_to_html.general_rule.fg_color = "#ffca61"
        text_to_html.general_rule.font_size = 12

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---1",
            replace_with=str(data["id"]),
            fg_color="#aaffff",
            font_bold=True
        )
        text_to_html.add_rule(rule)

        name = str(data["date"])
        if data["name"]:
            name += f' - {data["name"]}'
        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---2",
            replace_with=name,
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        rule = UTILS.HTMLText.TextToHtmlRule(
            text="#---3",
            replace_with=str(data["body"]),
            fg_color="#aaffff"
        )
        text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def load_widgets_handler(self) -> None:
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
        self.widget_handler.add_QPushButton(self.btn_abort)
        self.widget_handler.add_QPushButton(self.btn_tag_new)
        self.widget_handler.add_QPushButton(self.btn_tag_old)
        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_rename)

        # Add Selection Widgets
        self.widget_handler.add_Selection_Widget(self.chk_item_default, {"tap_event_change_stylesheet_enabled": False})
        self.widget_handler.add_Selection_Widget(self.chk_session_default, {"tap_event_change_stylesheet_enabled": False})

        # Add Item Based Widgets

        self.widget_handler.activate()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.resize_me()
        return super().resizeEvent(a0)

    def resize_me(self):
        try:
            if self.data is None:
                return
        except:
            return
        
        chk_h = 0
        if self.chk_item_default.isVisible():
            chk_h += self.chk_item_default.height()
        if self.chk_session_default.isVisible():
            chk_h += self.chk_session_default.height()
        if self.chk_session_default.isVisible() and self.chk_session_default.isVisible():
            chk_h += 2
        if chk_h:
            chk_h += 10

        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w - 20, self.lbl_title.height())
        self.lbl_desc.resize(w - 20, self.lbl_desc.height())

        self.btn_abort.move(int((w - self.btn_abort.width()) / 2), h - 40)

        self.frm_tag.move(10, 160)
        self.frm_tag.resize(w - 20, h - 210)
        frm_w = self.frm_tag.width()
        frm_h = self.frm_tag.height()
        frm_h_without_chk = frm_h - chk_h
        lbl_w = int((frm_w - 20) / 2 - 20)
        self.lbl_tag_new.move(10, 10)
        self.lbl_tag_new.resize(lbl_w, frm_h_without_chk - 60)

        self.txt_rename.move(self.lbl_tag_new.pos().x(), self.lbl_tag_new.pos().y() + self.lbl_tag_new.height() - self.txt_rename.height())
        self.txt_rename.resize(lbl_w, self.txt_rename.height())

        self.lbl_tag_old.move(frm_w - (lbl_w + 10), 10)
        self.lbl_tag_old.resize(lbl_w, frm_h_without_chk - 60)

        if lbl_w < 200:
            self.btn_tag_new.resize(lbl_w, self.btn_tag_new.height())
            self.btn_tag_old.resize(lbl_w, self.btn_tag_old.height())
        else:
            self.btn_tag_new.resize(200, self.btn_tag_new.height())
            self.btn_tag_old.resize(200, self.btn_tag_old.height())
        
        self.btn_tag_new.move(10 + int((lbl_w - self.btn_tag_new.width()) / 2), frm_h_without_chk - (self.btn_tag_new.height() + 10))
        self.btn_tag_old.move(self.lbl_tag_old.pos().x() + int((lbl_w - self.btn_tag_old.width()) / 2), frm_h_without_chk - (self.btn_tag_old.height() + 10))

        chk_item_x = int(frm_w / 2 - self.chk_item_default.width() / 2)
        if chk_item_x < 0:
            chk_item_x = 0
        chk_session_x = int(frm_w / 2 - self.chk_session_default.width() / 2)
        if chk_session_x < 0:
            chk_session_x = 0
        if self.chk_item_default.isVisible() and self.chk_session_default.isVisible():
            self.chk_session_default.move(chk_session_x, frm_h - 5 - 24)
            self.chk_item_default.move(chk_item_x, frm_h - 5 - 24 - 2 - 24)
        else:
            if self.chk_item_default.isVisible():
                self.chk_item_default.move(chk_item_x, frm_h - 5 - 24)
            elif self.chk_session_default.isVisible():
                self.chk_session_default.move(chk_session_x, frm_h - 5 - 24)
        
        if self.data["action"] == "image":
            self._set_images()

    def _load_win_position(self):
        if "compare_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("compare_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self, save_geometry: bool = True):
        if save_geometry:
            if "compare_win_geometry" not in self._stt.app_setting_get_list_of_keys():
                self._stt.app_setting_add("compare_win_geometry", {}, save_to_file=True)

            g = self.get_appv("compare_win_geometry")
            g["pos_x"] = self.pos().x()
            g["pos_y"] = self.pos().y()
            g["width"] = self.width()
            g["height"] = self.height()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["Compare"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self) -> None:
        # General
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_desc: QLabel = self.findChild(QLabel, "lbl_desc")
        self.btn_abort: QPushButton = self.findChild(QPushButton, "btn_abort")

        # Tag
        self.frm_tag: QFrame = self.findChild(QFrame, "frm_tag")
        self.lbl_tag_new: QLabel = self.findChild(QLabel, "lbl_tag_new")
        self.lbl_tag_old: QLabel = self.findChild(QLabel, "lbl_tag_old")
        self.btn_tag_new: QPushButton = self.findChild(QPushButton, "btn_tag_new")
        self.btn_tag_old: QPushButton = self.findChild(QPushButton, "btn_tag_old")
        self.txt_rename: QLineEdit = self.findChild(QLineEdit, "txt_rename")

        self.chk_item_default: QCheckBox = self.findChild(QCheckBox, "chk_item_default")
        self.chk_session_default: QCheckBox = self.findChild(QCheckBox, "chk_session_default")

    def _setup_widgets_text(self) -> None:
        self.btn_abort.setText(self.getl("export_import_btn_working_abort_text"))

        self.lbl_tag_new.setText("")
        self.lbl_tag_old.setText("")

        if self.data["action"] == "tag":
            self.btn_tag_new.setText(self.getl("compare_btn_tag_new_text"))
            self.btn_tag_old.setText(self.getl("compare_btn_tag_old_text"))
            self.lbl_title.setText(self.getl("compare_tag_lbl_title_text"))
            self.lbl_desc.setText(self.getl("compare_tag_lbl_desc_text"))
            
            self.chk_item_default.setText(self.getl("compare_tag_chk_item_default_text"))
            self.chk_session_default.setText(self.getl("compare_tag_chk_session_default_text"))
        elif self.data["action"] == "image":
            self.btn_tag_new.setText(self.getl("compare_btn_tag_new_image_text"))
            self.btn_tag_old.setText(self.getl("compare_btn_tag_old_image_text"))
            self.lbl_title.setText(self.getl("compare_image_lbl_title_text"))
            self.lbl_desc.setText(self.getl("compare_image_lbl_desc_text"))
            
            item_text = self.getl("compare_img_chk_item_default_text")
            if self.data["refer_object"] == "definition":
                item_text += self._get_def_headline()
            elif self.data["refer_object"] == "block":
                item_text += self._get_block_headline()
            else:
                UTILS.LogHandler.add_log_record("#1: Undefined refer object for #2 in function #3.", ["Compare", "image", "_setup_widgets_text"], warning_raised=True)
            self.chk_item_default.setText(item_text)
            self.chk_session_default.setText(self.getl("compare_img_chk_session_default_text"))
        elif self.data["action"] == "file":
            self.btn_tag_new.setText(self.getl("compare_btn_tag_new_file_text"))
            self.btn_tag_old.setText(self.getl("compare_btn_tag_old_file_text"))
            self.lbl_title.setText(self.getl("compare_file_lbl_title_text"))
            self.lbl_desc.setText(self.getl("compare_file_lbl_desc_text"))

            item_text = self.getl("compare_file_chk_item_default_text")
            if self.data["refer_object"] == "block":
                item_text += self._get_block_headline()
            else:
                UTILS.LogHandler.add_log_record("#1: Undefined refer object for #2 in function #3.", ["Compare", "file", "_setup_widgets_text"], warning_raised=True)
            self.chk_item_default.setText(item_text)
            self.chk_session_default.setText(self.getl("compare_file_chk_session_default_text"))
        elif self.data["action"] == "definition":
            self.btn_tag_new.setText(self.getl("compare_btn_tag_new_rename_text"))
            self.btn_tag_old.setText(self.getl("compare_btn_tag_old_update_text"))
            self.lbl_title.setText(self.getl("compare_def_lbl_title_text"))
            self.lbl_desc.setText(self.getl("compare_def_lbl_desc_text"))

            self.chk_item_default.setText(self.getl("compare_def_chk_item_default_text"))
            self.chk_session_default.setText(self.getl("compare_def_chk_session_default_text"))
        elif self.data["action"] == "append":
            self.btn_tag_new.setText(self.getl("compare_btn_tag_new_append_text"))
            self.btn_tag_old.setText(self.getl("compare_btn_tag_old_append_text"))
            self.lbl_title.setText(self.getl("compare_append_lbl_title_text"))
            self.lbl_desc.setText(self.getl("compare_append_lbl_desc_text"))
        elif self.data["action"] == "block":
            self.btn_tag_new.setText(self.getl("compare_btn_tag_new_block_text"))
            self.btn_tag_old.setText(self.getl("compare_btn_tag_old_block_text"))
            self.lbl_title.setText(self.getl("compare_block_lbl_title_text"))
            self.lbl_desc.setText(self.getl("compare_block_lbl_desc_text"))

            self.chk_item_default.setText(self.getl("compare_block_chk_item_default_text"))
            self.chk_session_default.setText(self.getl("compare_block_chk_session_default_text"))

    def _get_def_headline(self) -> str:
        if not self.data["refer_id"]:
            UTILS.LogHandler.add_log_record("#1: Invalid definiton ID (#2) in function #3", ["Compare", self.data["refer_id"], "_get_def_headline"])
            return ""

        return self.data["refer_object_name"]

    def _get_block_headline(self) -> str:
        if not self.data["refer_id"]:
            UTILS.LogHandler.add_log_record("#1: Invalid definiton ID (#2) in function #3", ["Compare", self.data["refer_id"], "_get_block_headline"])
            return ""

        return self.data["refer_object_name"]

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["Compare"])
        self._setup_widgets_appearance()

    def _setup_widgets_appearance(self) -> None:
        self.setWindowIcon(QIcon(QPixmap(self.getv("compare_win_icon_path"))))
        self.setWindowTitle(self.getl("compare_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(300, 360)

        if self.data["action"] == "image":
            self.lbl_tag_new.setAlignment(Qt.AlignCenter)
            self.lbl_tag_old.setAlignment(Qt.AlignCenter)

        self.lbl_title.setStyleSheet(self.getv("compare_lbl_title_stylesheet"))
        self.lbl_desc.setStyleSheet(self.getv("compare_lbl_desc_stylesheet"))
        self.btn_abort.setStyleSheet(self.getv("compare_btn_abort_stylesheet"))
        self.btn_abort.setIcon(QIcon(QPixmap(self.getv("compare_btn_abort_icon_path"))))
        
        self.frm_tag.setStyleSheet(self.getv("compare_frm_tag_stylesheet"))
        self.lbl_tag_new.setStyleSheet(self.getv("compare_lbl_tag_new_stylesheet"))
        self.lbl_tag_old.setStyleSheet(self.getv("compare_lbl_tag_old_stylesheet"))
        self.btn_tag_new.setStyleSheet(self.getv("compare_btn_tag_new_stylesheet"))
        if self.data["action"] == "definition":
            self.btn_tag_new.setIcon(QIcon(QPixmap(self.getv("rename_icon_path"))))
        else:
            self.btn_tag_new.setIcon(QIcon(QPixmap(self.getv("compare_btn_tag_new_icon_path"))))
        self.btn_tag_old.setStyleSheet(self.getv("compare_btn_tag_old_stylesheet"))
        self.btn_tag_old.setIcon(QIcon(QPixmap(self.getv("compare_btn_tag_old_icon_path"))))
        self.txt_rename.setStyleSheet(self.getv("compare_txt_rename_stylesheet"))
        if self.data["action"] != "definition":
            self.txt_rename.setVisible(False)
        else:
            self.txt_rename.setVisible(True)
            self.btn_tag_new.setDisabled(True)
            self.txt_rename.setText(self.data["new"]["name"])

        self._set_checkboxes_appearance()
        self.chk_item_default.adjustSize()
        self.chk_item_default.resize(self.chk_item_default.width() + 10, 24)
        self.chk_session_default.adjustSize()
        self.chk_session_default.resize(self.chk_session_default.width() + 10, 24)
        self.chk_session_default.setVisible(False)
        self.chk_item_default.setVisible(False)
        if self.data["action"] in ["block", "definition", "tag"]:
            self.chk_session_default.setVisible(True)
        elif self.data["action"] in ["image", "file"]:
            self.chk_item_default.setVisible(True)
            self.chk_session_default.setVisible(True)

    def _set_checkboxes_appearance(self) -> None:
        if self.chk_item_default.checkState() == Qt.Checked:
            self.chk_item_default.setStyleSheet(self.getv("compare_chk_boxes_checked_stylesheet"))
        else:
            self.chk_item_default.setStyleSheet(self.getv("compare_chk_boxes_unchecked_stylesheet"))
        
        if self.chk_session_default.checkState() == Qt.Checked:
            self.chk_session_default.setStyleSheet(self.getv("compare_chk_boxes_checked_stylesheet"))
        else:
            self.chk_session_default.setStyleSheet(self.getv("compare_chk_boxes_unchecked_stylesheet"))

        


