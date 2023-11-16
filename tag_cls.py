from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout,
    QGridLayout, QWidget, QSpacerItem, QSizePolicy, QListWidget, QFileDialog, QDialog,
    QLabel, QListWidgetItem, QDesktopWidget, QLineEdit, QCalendarWidget, QHBoxLayout)
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QStaticText, QPixmap, QCursor
from PyQt5.QtCore import (QSize, Qt, pyqtSignal, QObject, QCoreApplication, QRect,
    QPoint, QTimer, QThread, QDate)
from PyQt5 import uic, QtGui, QtCore

import datetime
import time
import copy

import settings_cls
import db_tag_cls
import utility_cls


class TagView(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget, tag_id: int = None, *agrs, **kwargs):
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
        self._tag_id = tag_id
        self._db_tag = db_tag_cls.Tag(self._stt)

        # Load GUI
        uic.loadUi(self.getv("tag_view_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._load_win_position()

        self._populate_widgets()
        self._set_butttons_enabled()

        # Connect events with slots
        self.lst_tags.currentItemChanged.connect(self.lst_tags_current_item_changed)
        self.txt_name.textChanged.connect(self.txt_name_text_changed)
        self.txt_desc.textChanged.connect(self.txt_desc_text_changed)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_apply.clicked.connect(self.btn_apply_click)
        self.btn_add.clicked.connect(self.btn_add_click)
        self.btn_delete.clicked.connect(self.btn_delete_click)

        self.show()

    def btn_delete_click(self):
        tag_id = self._db_tag.is_valid_tag_name(self.txt_name.text())
        if tag_id == 1:
            data_dict = {
                "title": self.getl("tag_view_delete_msg_no_diary_title"),
                "text": self.getl("tag_view_delete_msg_no_diary_text"),
                "btn_ok_text": self.getl("tag_view_delete_msg_no_diary_btn_ok_text")
            }
            utility_cls.MessageInformation(self._stt, self, data_dict, app_modal=True)
            return
        if self._db_tag.how_many_times_is_used(tag_id) > 0:
            data_dict = {
                "title": self.getl("tag_view_delete_msg_in_use_title"),
                "text": self.getl("tag_view_delete_msg_in_use_text"),
            }
            utility_cls.MessageInformation(self._stt, self, data_dict, app_modal=True)
            return

        text = self.getl("tag_view_delete_question_text").replace("#1", self.txt_name.text())
        data_dict = {
            "title": self.getl("tag_view_delete_question_title"),
            "text": text,
            "buttons": [
                [
                    1,
                    self.getl("tag_view_delete_question_btn_yes"),
                    "",
                    None,
                    True
                ],
                [
                    2,
                    self.getl("tag_view_delete_question_btn_no"),
                    "",
                    None,
                    True
                ],
                [
                    3,
                    self.getl("tag_view_delete_question_btn_cancel"),
                    "",
                    None,
                    True
                ]
            ]
        }
        utility_cls.MessageQuestion(self._stt, self, data_dict)
        if data_dict["result"] != 1:
            return
        
        tag_id = self._db_tag.is_valid_tag_name(self.txt_name.text())
        if not tag_id:
            self._notif(self.getl("tag_view_notif_data_not_deleted"), 3000)
            return
        
        self._db_tag.delete_tag(tag_id)
        self._set_butttons_enabled()
        self._notif(self.getl("tag_view_notif_data_deleted"))
        self.get_appv("log").write_log(f"TagView. Tag deleted. Tag ID: {self._tag_id}")
        self._tag_id = None
        self._populate_widgets()
 
    def btn_apply_click(self):
        tag_dict = {
            "name": self.txt_name.text(),
            "description": self.txt_desc.toPlainText()
        }
        tag_id = self._db_tag.is_valid_tag_name(self.txt_name.text())
        if not tag_id:
            self._notif(self.getl("tag_view_notif_data_not_updated"), 3000)
            return
        self._db_tag.update_tag(tag_id, tag_dict)
        self._set_butttons_enabled()
        self._notif(self.getl("tag_view_notif_data_updated"))
        self.get_appv("log").write_log(f"TagView. Tag info updated. Tag ID: {self._tag_id}")
        
    def btn_add_click(self):
        tag_dict = {
            "name": self.txt_name.text(),
            "description": self.txt_desc.toPlainText()
        }
        tag_id = self._db_tag.is_valid_tag_name(self.txt_name.text())
        if tag_id:
            self._notif(self.getl("tag_view_notif_data_not_added"), 3000)
            return
        self._db_tag.add_new_tag(tag_dict)
        self._set_butttons_enabled()
        self._notif(self.getl("tag_view_notif_data_added"))
        self._tag_id = tag_id
        self._populate_widgets()
        self.get_appv("log").write_log(f"TagView. New tag added. Tag ID: {self._tag_id}")

    def _notif(self, text: str, timer: int = 2000):
        ntf_dict = {
            "title": "",
            "text": text,
            "timer": timer
        }
        utility_cls.Notification(self._stt, self, ntf_dict)
    
    def btn_cancel_click(self):
        self.close()

    def txt_name_text_changed(self):
        self._set_butttons_enabled()

    def txt_desc_text_changed(self):
        self._set_butttons_enabled()

    def _set_butttons_enabled(self):
        if not self.txt_name.text():
            self.btn_apply.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_add.setEnabled(False)
            return
        tag_id = self._db_tag.is_valid_tag_name(self.txt_name.text())
        if tag_id:
            self._db_tag.populate_values(tag_id)
            self.btn_add.setEnabled(False)
            self.btn_delete.setEnabled(True)
            if self.txt_desc.toPlainText() == self._db_tag.TagDescriptionTranslated:
                self.btn_apply.setEnabled(False)
            else:
                self.btn_apply.setEnabled(True)
        else:
            self.btn_add.setEnabled(True)
            self.btn_apply.setEnabled(False)
            self.btn_delete.setEnabled(False)

    def lst_tags_current_item_changed(self, x, y):
        self._show_tag_info()

    def _populate_widgets(self):
        tags = self._db_tag.get_all_tags_translated()
        self.lst_tags.clear()
        row = None
        for tag in tags:
            item = QListWidgetItem()
            item.setText(tag[1])
            item.setData(Qt.UserRole, tag[0])
            self.lst_tags.addItem(item)
            if self._tag_id is not None:
                if self._tag_id == tag[0]:
                    row = self.lst_tags.row(item)
        if row is not None:
            self.lst_tags.setCurrentRow(row)
        self._show_tag_info()

    def _show_tag_info(self, tag_id: int = None):
        self.txt_desc.setText("")
        self.txt_name.setText("")

        if tag_id is None:
            if self.lst_tags.currentItem() == None:
                return
            tag_id = self.lst_tags.currentItem().data(Qt.UserRole)
        
        self._db_tag.populate_values(tag_id)
        info_txt = self.getl("tag_view_lbl_info_text")
        info_txt = info_txt.replace("#1", str(tag_id))
        info_txt = info_txt.replace("#2", self._db_tag.TagNameTranslated)
        info_txt = info_txt.replace("#3", str(self._db_tag.how_many_times_is_used(tag_id)))
        
        self.lbl_info.setText(info_txt)
        self.txt_name.setText(self._db_tag.TagNameTranslated)
        self.txt_desc.setText(self._db_tag.TagDescriptionTranslated)

    def _load_win_position(self):
        if "view_tag_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("view_tag_win_geometry")
            self.move(g["pos_x"], g["pos_y"])

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if "view_tag_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("view_tag_win_geometry", {}, save_to_file=True)

        g = self.get_appv("view_tag_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        return super().closeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_info: QLabel = self.findChild(QLabel, "lbl_info")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_desc: QLabel = self.findChild(QLabel, "lbl_desc")

        self.txt_name: QLineEdit = self.findChild(QLineEdit, "txt_name")
        self.txt_desc: QTextEdit = self.findChild(QTextEdit, "txt_desc")

        self.btn_apply: QPushButton = self.findChild(QPushButton, "btn_apply")
        self.btn_delete: QPushButton = self.findChild(QPushButton, "btn_delete")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_add: QPushButton = self.findChild(QPushButton, "btn_add")

        self.lst_tags: QListWidget = self.findChild(QListWidget, "lst_tags")
        self.frm_info: QFrame = self.findChild(QFrame, "frm_info")

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("tag_view_win_title_text"))

        self.lbl_title.setText(self.getl("tag_view_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("tag_view_lbl_title_tt"))

        self.lbl_name.setText(self.getl("tag_view_lbl_name_text"))
        self.lbl_name.setToolTip(self.getl("tag_view_lbl_name_tt"))
        
        self.lbl_desc.setText(self.getl("tag_view_lbl_desc_text"))
        self.lbl_desc.setToolTip(self.getl("tag_view_lbl_desc_tt"))

        self.lbl_info.setText("")
        self.lbl_info.setToolTip(self.getl("tag_view_lbl_info_tt"))

        self.btn_apply.setText(self.getl("tag_view_btn_apply_text"))
        self.btn_apply.setToolTip(self.getl("tag_view_btn_apply_tt"))

        self.btn_delete.setText(self.getl("tag_view_btn_delete_text"))
        self.btn_delete.setToolTip(self.getl("tag_view_btn_delete_tt"))

        self.btn_cancel.setText(self.getl("tag_view_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("tag_view_btn_cancel_tt"))

        self.btn_add.setText(self.getl("tag_view_btn_add_text"))
        self.btn_add.setToolTip(self.getl("tag_view_btn_add_tt"))

    def _setup_widgets_apperance(self):
        # Win
        self.setStyleSheet(self.getv("tag_view_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("tag_view_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(618, 451)
        # Frame
        self.frm_info.setFrameShape(self.getv("tag_view_frm_info_frame_shape"))
        self.frm_info.setFrameShadow(self.getv("tag_view_frm_info_frame_shadow"))
        self.frm_info.setLineWidth(self.getv("tag_view_frm_info_line_width"))
        self.frm_info.setStyleSheet(self.getv("tag_view_frm_info_stylesheet"))
        # Widgets
        self.lbl_title.setStyleSheet(self.getv("tag_view_lbl_title_stylesheet"))
        self.lbl_info.setStyleSheet(self.getv("tag_view_lbl_info_stylesheet"))
        self.lbl_name.setStyleSheet(self.getv("tag_view_lbl_name_stylesheet"))
        self.lbl_desc.setStyleSheet(self.getv("tag_view_lbl_desc_stylesheet"))

        self.btn_apply.setStyleSheet(self.getv("tag_view_btn_apply_stylesheet"))
        self.btn_apply.setIcon(QIcon(self.getv("tag_view_btn_apply_icon_path")))
        self.btn_apply.setEnabled(False)
        self.btn_delete.setStyleSheet(self.getv("tag_view_btn_delete_stylesheet"))
        self.btn_delete.setIcon(QIcon(self.getv("tag_view_btn_delete_icon_path")))
        self.btn_delete.setEnabled(False)
        self.btn_cancel.setStyleSheet(self.getv("tag_view_btn_cancel_stylesheet"))
        self.btn_cancel.setIcon(QIcon(self.getv("tag_view_btn_cancel_icon_path")))
        self.btn_add.setStyleSheet(self.getv("tag_view_btn_add_stylesheet"))
        self.btn_add.setIcon(QIcon(self.getv("tag_view_btn_add_icon_path")))
        self.btn_add.setEnabled(False)

        self.txt_name.setStyleSheet(self.getv("tag_view_txt_name_stylesheet"))
        self.txt_desc.setStyleSheet(self.getv("tag_view_txt_desc_stylesheet"))

        self.lst_tags.setStyleSheet(self.getv("tag_view_lst_tags_stylesheet"))




