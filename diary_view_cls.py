from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout, QWidget, QSpacerItem,
                             QSizePolicy, QListWidget, QDialog, QLabel, QListWidgetItem, QLineEdit, QHBoxLayout,
                             QCheckBox, QProgressBar)
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QPixmap, QCursor, QTextCharFormat, QColor
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QEvent
from PyQt5 import uic, QtGui

import os

import settings_cls
import db_record_cls
import db_record_data_cls
import utility_cls
import db_tag_cls
import text_handler_cls
import db_media_cls
import block_cls


class BlockView(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_obj, block_ids: list = None, auto_open_ids: list = None, *args, **kwargs):
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
        self._dont_clear_menu = False
        self._drag_mode = None
        self._tags_list = []
        self._painting_mode = None
        
        self._block_ids = block_ids
        if block_ids is not None:
            if isinstance(block_ids, int):
                self._block_ids = [block_ids]
            else:
                self._block_ids = block_ids
        
        self._auto_open_ids = auto_open_ids
        if auto_open_ids is not None:
            if isinstance(auto_open_ids, int):
                self._auto_open_ids = [auto_open_ids]
            else:
                self._auto_open_ids = auto_open_ids

        db_data = db_record_data_cls.RecordData(self._stt)
        self._records_with_images = db_data.get_record_ids_with_images()
        self._tags_map = db_data.get_tags_and_media_for_all_records()

        # Load GUI
        uic.loadUi(self.getv("block_view_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._define_tags_frame()

        self._populate_widgets(self._block_ids)
        self._load_win_position()
        self._paint_items()

        # Connect events with slots
        self.lst_blocks.itemDoubleClicked.connect(self.lst_blocks_item_double_clicked)
        self.lst_blocks.itemChanged.connect(self.lst_blocks_item_changed)
        self.lst_blocks.mouseReleaseEvent = self.lst_blocks_mouse_release
        
        self.ln_delim.mousePressEvent = self._ln_delim_mouse_click
        self.ln_delim.mouseReleaseEvent = self._ln_delim_mouse_release
        self.ln_delim.mouseMoveEvent = self._ln_delim_mouse_move

        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_clear_filter.clicked.connect(self.btn_clear_filter_click)
        self.btn_close_all.clicked.connect(self.btn_close_all_click)
        self.btn_tags.clicked.connect(self.btn_tags_click)
        self.btn_view_diary.clicked.connect(self.btn_view_diary_click)

        self.txt_filter.textChanged.connect(self.txt_filter_text_changed)

        self.get_appv("signal").signalCloseAllBlocks.connect(self._signal_close_all_blocks)

        self.show()
        QCoreApplication.processEvents()
        self._auto_open_blocks(blocks_ids=self._auto_open_ids)

    def _signal_close_all_blocks(self):
        while self.area.widget().layout().count():
            self.area.widget().layout().itemAt(0).widget()._close_block(fast_close=True)
        self.btn_cancel_click()

    def _auto_open_blocks(self, blocks_ids: list = None):
        if blocks_ids is None:
            return
        
        for i in blocks_ids:
            self._show_block(i)

    def btn_view_diary_click(self):
        block_list = []
        for item in self.lst_blocks.findItems("", Qt.MatchFlag.MatchContains):
            if not item.isHidden():
                block_list.append(item.data(Qt.UserRole))

        DiaryView(self._stt, self, block_list=block_list)

    def btn_close_all_click(self):
        while self.area.widget().layout().count():
            self.area.widget().layout().itemAt(0).widget()._close_block()

    def tags_are_selected(self, tag_list: list):
        self._tags_list = tag_list
        if tag_list:
            self.btn_tags.setText(self.getl("block_view_btn_tags_text").replace("#1", str(len(tag_list))))
        else:
            self.btn_tags.setText(self.getl("block_view_btn_tags_text").replace("#1", self.getl("block_view_btn_tags_#1")))

        self.filter_items()

    def btn_tags_click(self):
        if self.frm_tags.isVisible():
            self._frm_tags_hide_me()
        else:
            self._frm_tags_show_me()

    def btn_clear_filter_click(self):
        self.txt_filter.setText("")

    def btn_cancel_click(self):
        self.close()

    def lst_blocks_item_double_clicked(self):
        self._show_block(self.lst_blocks.currentItem().data(Qt.UserRole))

    def _show_block(self, block_id: int):
        data_dict = {
            "name": "block_view",
            "action": "block_ids"
        }
        result = self.get_appv("main_win").events(data_dict)
        if block_id in result:
            data_dict = {
                "title": self.getl("block_view_msg_block_exist_title"),
                "text": self.getl("block_view_msg_block_exist_text")
            }
            self._dont_clear_menu = True
            utility_cls.MessageInformation(self._stt, self, data_dict)
            return

        self._populate_data(block_id=block_id)

    def lst_blocks_item_changed(self, e: QListWidgetItem):
        if self._painting_mode:
            return
        rec_id = e.data(Qt.UserRole)
        db_rec = db_record_cls.Record(self._stt, record_id=rec_id)
        if e.checkState() == Qt.Checked:
            if db_rec.RecordDraft != 0:
                db_rec.RecordDraft = 0
                db_rec.save_record()
        else:
            if db_rec.RecordDraft == 0:
                db_rec.RecordDraft = 1
                db_rec.save_record()
        self._paint_items()

    def txt_filter_text_changed(self):
        if self.txt_filter.text():
            self.btn_clear_filter.setVisible(True)
        else:
            self.btn_clear_filter.setVisible(False)

        fm = QFontMetrics(self.txt_filter.font())
        if fm.width(self.txt_filter.text()) > 170:
            self.btn_clear_filter.move(210, self.btn_clear_filter.pos().y())
        else:
            self.btn_clear_filter.move(185, self.btn_clear_filter.pos().y())
        
        self.filter_items()
        
    def filter_items(self, block_ids: list = None):
        if block_ids:
            for item in self.lst_blocks.findItems("", Qt.MatchFlag.MatchContains):
                if item.data(Qt.UserRole) in block_ids:
                    item.setHidden(False)
                else:
                    item.setHidden(True)

            txt = self.getl("block_view_lbl_count_text").replace("#1", str(len(block_ids))).replace("#2", str(self.lst_blocks.count()))
            self.lbl_count.setText(txt)
            return

        count = 0
        for item in self.lst_blocks.findItems("", Qt.MatchFlag.MatchContains):
            item.setHidden(False)
            count += 1
            
            for i in self._tags_map:
                if i[0] == item.data(Qt.UserRole):
                    has_tag = True
                    if self.chk_tag.isChecked():
                        for j in self._tags_list:
                            if j in i[1]:
                                has_tag = False
                                break
                    else:
                        for j in self._tags_list:
                            if j not in i[1]:
                                has_tag = False
                                break
                    if has_tag:
                        item.setHidden(False)
                    else:
                        count -= 1
                        item.setHidden(True)
                    break

            if not item.isHidden():
                txt = item.text() + "\n" + item.toolTip()
                if self.txt_filter.text():
                    if self._filter_apply(self.txt_filter.text().lower(), txt.lower()):
                        item.setHidden(False)
                    else:
                        count -= 1
                        item.setHidden(True)

        txt = self.getl("block_view_lbl_count_text").replace("#1", str(count)).replace("#2", str(self.lst_blocks.count()))
        self.lbl_count.setText(txt)

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

    def _paint_items(self):

        # Find blocks opened in main win
        data_dict = {
            "name": "block_view",
            "action": "block_ids"
        }
        main_win_blocks = self.get_appv("main_win").events(data_dict)

        # Fins blocks opened in View win
        view_win_blocks = []
        for i in range(self.area.widget().layout().count()):
            view_win_blocks.append(self.area.widget().layout().itemAt(i).widget()._active_record_id)
        
        # Get background and foreground colors for blocks
        cf_main_win = self.getv("block_view_fore_color_main_win")
        cf_main_win_c = QColor(cf_main_win)
        cb_main_win = self.getv("block_view_back_color_main_win")
        cb_main_win_c = QColor(cb_main_win)

        cf_view_win = self.getv("block_view_fore_color_view_win")
        cf_view_win_c = QColor(cf_view_win)
        cb_view_win = self.getv("block_view_back_color_view_win")
        cb_view_win_c = QColor(cb_view_win)

        cf_checked = self.getv("block_view_fore_color_checked")
        cf_checked_c = QColor(cf_checked)
        cb_checked = self.getv("block_view_back_color_checked")
        cb_checked_c = QColor(cb_checked)

        cf_unchecked = self.getv("block_view_fore_color_unchecked")
        cf_unchecked_c = QColor(cf_unchecked)
        cb_unchecked = self.getv("block_view_back_color_unchecked")
        cb_unchecked_c = QColor(cb_unchecked)

        last_current_item = self.lst_blocks.currentItem()
        # Paint items
        self._painting_mode = True
        for i in range(self.lst_blocks.count()):
            item = self.lst_blocks.item(i)

            if item.checkState() == Qt.Checked:
                if cf_checked:
                    item.setForeground(cf_checked_c)
                if cb_checked:
                    item.setBackground(cb_checked_c)
            else:
                if cf_unchecked:
                    item.setForeground(cf_unchecked_c)
                if cb_unchecked:
                    item.setBackground(cb_unchecked_c)

            if item.data(Qt.UserRole) in view_win_blocks:
                if cf_view_win:
                    item.setForeground(cf_view_win_c)
                if cb_view_win:
                    item.setBackground(cb_view_win_c)
            
            if item.data(Qt.UserRole) in main_win_blocks:
                if cf_main_win:
                    item.setForeground(cf_main_win_c)
                if cb_main_win:
                    item.setBackground(cb_main_win_c)

        self._painting_mode = False
        if last_current_item is not None:
            self.lst_blocks.setCurrentItem(last_current_item)

    def _populate_data(self, block_id: int = None):
        if block_id is None:
            if self.lst_blocks.currentItem() is None:
                return
            else:
                block_id = self.lst_blocks.currentItem().data(Qt.UserRole)

        # Check if block exist
        for i in range(self.area.widget().layout().count()):
            if self.area.widget().layout().itemAt(i).widget()._active_record_id == block_id:
                self.area.widget().layout().itemAt(i).widget()._close_block()
                self._paint_items()
                return

        block_cls.WinBlock(self._stt, self.area.widget(), block_id, collapsed=False, main_window=self)
        self._paint_items()

    def events(self, event_dict: dict):
        if event_dict["name"] == "win_block":
            if event_dict["action"] == "open_new_block":
                msg_dict = {
                    "title": self.getl("block_view_add_new_msg_title"),
                    "text": self.getl("block_view_add_new_msg_text")
                }
                self._dont_clear_menu = True
                utility_cls.MessageInformation(self._stt, self, msg_dict, app_modal=True)
            
            if event_dict["action"] == "block_saved":
                self._list_update_block(event_dict["id"], event_dict["closed"])
            
            if event_dict["action"] == "block_deleted":
                self._list_delete_block(event_dict["id"])

        if event_dict["action"] == "cm":
            self._dont_clear_menu = True

    def _list_delete_block(self, rec_id: int):
        self._frm_tags_update_list()
        for item in self.lst_blocks.findItems("", Qt.MatchFlag.MatchContains):
            if item.data(Qt.UserRole) == rec_id:
                self.lst_blocks.takeItem(self.lst_blocks.row(item))
                self._paint_items()
                break

    def _list_update_block(self, rec_id: int, checked: bool):
        db_data = db_record_data_cls.RecordData(self._stt)
        self._records_with_images = db_data.get_record_ids_with_images()
        self._tags_map = db_data.get_tags_and_media_for_all_records()
        
        self._frm_tags_update_list()
        db_data = db_record_data_cls.RecordData(self._stt)
        self._records_with_images = db_data.get_record_ids_with_images()

        db_rec = db_record_cls.Record(self._stt)
        if not db_rec.is_valid_record_id(rec_id):
            return

        for item in self.lst_blocks.findItems("", Qt.MatchFlag.MatchContains):
            if item.data(Qt.UserRole) == rec_id:
                item.setText(self._set_list_item_text(db_rec.get_all_records(record_id=rec_id)[0]))
                if self.getv("block_view_list_show_body_in_tooltip"):
                    item.setToolTip(db_rec.get_all_records(record_id=rec_id)[0][4])

                if checked:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                
                if item.data(Qt.UserRole) in self._records_with_images:
                    ico = QIcon(self.getv("block_view_list_item_image_icon_path"))
                    item.setIcon(ico)
                else:
                    ico = QIcon()
                    item.setIcon(ico)

                self._paint_items()
                break

    def _populate_widgets(self, blocks_ids: list = None):
        self.lst_blocks.clear()

        db_rec = db_record_cls.Record(self._stt)
        records = db_rec.get_all_records()

        tags_dict = self._get_tags_dict()

        for record in records:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, record[0])
            item.setText(self._set_list_item_text(record, tags_dict=tags_dict))
            if self.getv("block_view_list_show_body_in_tooltip"):
                item.setToolTip(record[4])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if record[5]:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

            if item.data(Qt.UserRole) in self._records_with_images:
                ico = QIcon(self.getv("block_view_list_item_image_icon_path"))
                item.setIcon(ico)
            else:
                ico = QIcon()
                item.setIcon(ico)

            self.lst_blocks.addItem(item)

        self.filter_items(block_ids=blocks_ids)
        if self.lst_blocks.count():
            self.lst_blocks.setCurrentRow(self.lst_blocks.count() - 1)
        
    def _set_list_item_text(self, record_item: tuple, tags_dict: dict = None) -> str:
        if tags_dict is None:
            tags_dict = self._get_tags_dict()
        
        txt = ""

        if self.getv("block_view_list_show_date"):
            txt = record_item[2]

        if self.getv("block_view_list_show_tags"):
            if record_item[0] in tags_dict:
                txt += " ["
                for tag in tags_dict[record_item[0]]:
                    txt += f"{tag},"
                if txt[-1] == ",":
                    txt = txt.rstrip(",")
                txt += "]"

        if self.getv("block_view_list_show_name"):
            if record_item[1]:
                txt += " - " + record_item[1]
        
        if self.getv("block_view_list_show_body"):
            body =  record_item[4].split("\n")
            if body:
                txt += f" - {body[0]}"
        
        return txt

    def _get_tags_dict(self) -> dict:
        db_data = db_record_data_cls.RecordData(self._stt)
        db_tags = db_tag_cls.Tag(self._stt)
        data = db_data.get_tags_and_media_for_all_records()
        tags = db_tags.get_all_tags_translated()

        rec_dict = {}

        for item in data:
            if item[0] not in rec_dict:
                rec_dict[item[0]] = []
            
            for tag_id in item[1]:
                for tag in tags:
                    if tag[0] == tag_id:
                        rec_dict[item[0]].append(tag[1])
                        break
        return rec_dict

    def lst_blocks_mouse_release(self, e):
        if e.button() == Qt.RightButton:
            self._show_list_menu()
        QListWidget.mouseReleaseEvent(self.lst_blocks, e)

    def _show_list_menu(self):
        selected = []
        if self.lst_blocks.currentItem().checkState() == Qt.Checked:
            selected.append(30020)
        else:
            selected.append(30010)

        disabled = []
        for i in range(self.area.widget().layout().count()):
            if self.area.widget().layout().itemAt(i).widget()._active_record_id == self.lst_blocks.currentItem().data(Qt.UserRole):
                disabled = [10, 40]

        db_data = db_record_data_cls.RecordData(self._stt, self.lst_blocks.currentItem().data(Qt.UserRole))
        result = db_data.get_record_data_field_values("media_id")
        
        media_list = [x[3] for x in result]
        # Check are all media IDs images
        db_media = db_media_cls.Media(self._stt)
        media_list = db_media.check_is_all_ids_images(media_ids=media_list)

        if not media_list:
            disabled.append(15)

        if self.getv("block_view_list_show_date"):
            selected.append(20010)
        if self.getv("block_view_list_show_tags"):
            selected.append(20020)
        if self.getv("block_view_list_show_name"):
            selected.append(20030)
        if self.getv("block_view_list_show_body"):
            selected.append(20040)
        if self.getv("block_view_list_show_body_in_tooltip"):
            selected.append(20050)

        menu_dict = {
            "position": QCursor.pos(),
            "selected": selected,
            "disabled": disabled,
            "separator": [30, 20040],
            "items": [
                [
                    10,
                    self.getl("block_view_list_menu_show_block_text"),
                    self.getl("block_view_list_menu_show_block_tt"),
                    True, [], self.getv("block_view_menu_show_block_icon_path")
                ],
                [
                    15,
                    self.getl("block_view_list_menu_show_block_images_text"),
                    self.getl("block_view_list_menu_show_block_images_tt"),
                    True, [], self.getv("block_view_menu_show_block_images_icon_path")
                ],
                [
                    20,
                    self.getl("block_view_list_menu_setup_view_text"),
                    self.getl("block_view_list_menu_setup_view_tt"),
                    False,
                    [
                        [
                            20010,
                            self.getl("block_view_menu_setup_view_date_text"),
                            self.getl("block_view_menu_setup_view_date_tt"),
                            True, [], None
                        ],
                        [
                            20020,
                            self.getl("block_view_menu_setup_view_tags_text"),
                            self.getl("block_view_menu_setup_view_tags_tt"),
                            True, [], None
                        ],
                        [
                            20030,
                            self.getl("block_view_menu_setup_view_name_text"),
                            self.getl("block_view_menu_setup_view_name_tt"),
                            True, [], None
                        ],
                        [
                            20040,
                            self.getl("block_view_menu_setup_view_body_text"),
                            self.getl("block_view_menu_setup_view_body_tt"),
                            True, [], None
                        ],
                        [
                            20050,
                            self.getl("block_view_menu_setup_view_body_tooltip_text"),
                            self.getl("block_view_menu_setup_view_body_tooltip_tt"),
                            True, [], None
                        ]
                    ],
                    None
                ],
                [
                    30,
                    self.getl("block_view_list_menu_state_text"),
                    self.getl("block_view_list_menu_state_tt"),
                    False, [
                        [
                            30010,
                            self.getl("block_view_menu_state_opened_text"),
                            self.getl("block_view_menu_state_opened_tt"),
                            True, [], None
                        ],
                        [
                            30020,
                            self.getl("block_view_menu_state_closed_text"),
                            self.getl("block_view_menu_state_closed_tt"),
                            True, [], None
                        ]
                    ], None
                ],
                [
                    40,
                    self.getl("block_view_list_menu_delete_text"),
                    self.getl("block_view_list_menu_delete_tt"),
                    True, [], None
                ]
            ]

        }
        self.set_appv("menu", menu_dict)
        self._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]
        if result == 10:
            self.lst_blocks_item_double_clicked()
        elif result == 15:
            utility_cls.PictureBrowse(self._stt, self, media_list=media_list)
        elif result == 20010:
            self.setv("block_view_list_show_date", not self.getv("block_view_list_show_date"))
            self._refresh_list()
        elif result == 20020:
            self.setv("block_view_list_show_tags", not self.getv("block_view_list_show_tags"))
            self._refresh_list()
        elif result == 20030:
            self.setv("block_view_list_show_name", not self.getv("block_view_list_show_name"))
            self._refresh_list()
        elif result == 20040:
            self.setv("block_view_list_show_body", not self.getv("block_view_list_show_body"))
            self._refresh_list()
        elif result == 20050:
            self.setv("block_view_list_show_body_in_tooltip", not self.getv("block_view_list_show_body_in_tooltip"))
            self._refresh_list()
        elif result == 30010:
            self.lst_blocks.currentItem().setCheckState(Qt.Unchecked)
        elif result == 30020:
            self.lst_blocks.currentItem().setCheckState(Qt.Checked)
        elif result == 40:
            self._confirm_and_delete_block()
        
    def _refresh_list(self):
        last_current_item = self.lst_blocks.currentItem()
        self._painting_mode = True
        db_rec = db_record_cls.Record(self._stt)
        all_rec = db_rec.get_all_records()
        tags_dict = self._get_tags_dict()

        for item in self.lst_blocks.findItems("", Qt.MatchFlag.MatchContains):
            for rec in all_rec:
                if rec[0] == item.data(Qt.UserRole):
                    item.setText(self._set_list_item_text(rec, tags_dict=tags_dict))
                    if self.getv("block_view_list_show_body_in_tooltip"):
                        item.setToolTip(rec[4])
                    else:
                        item.setToolTip("")

                    if item.data(Qt.UserRole) in self._records_with_images:
                        ico = QIcon(self.getv("block_view_list_item_image_icon_path"))
                        item.setIcon(ico)
                    else:
                        ico = QIcon()
                        item.setIcon(ico)

        self._painting_mode = False

        if last_current_item is not None:
            self.lst_blocks.setCurrentItem(last_current_item)

    def _confirm_and_delete_block(self):
        # Ask the user to confirm the deletion
        rec_id = self.lst_blocks.currentItem().data(Qt.UserRole)
        txt = self.getl("block_footer_btn_delete_msg_text") + "\n\n"
        if len(self.lst_blocks.currentItem().text()) > 150:
            txt += self.lst_blocks.currentItem().text()[:147] + "..."
        else:
            txt += self.lst_blocks.currentItem().text()

        data_dict = {
            "title": self.getl("block_footer_btn_delete_msg_title"),
            "text": txt,
            "icon_path": self.getv("block_footer_btn_delete_msg_icon_path"),
            "position": "center screen",
            "buttons": [
                [1, self.getl("btn_yes"), "", self.getv("block_footer_btn_delete_msg_btn_yes_icon_path"), True],
                [2, self.getl("btn_no"), "", "", True],
                [3, self.getl("btn_cancel"), "", "", True]
            ]
        }
        self._dont_clear_menu = True
        utility_cls.MessageQuestion(self._stt, self, data_dict)
        if data_dict["result"] == 1:

            db_record = db_record_cls.Record(self._stt, rec_id)
            db_rec_data = db_record_data_cls.RecordData(self._stt, rec_id)
            db_record.delete_record()
            db_rec_data.delete_record_data()
            notif_dict = {
                "title": self.getl("win_block_notification_block_deleted_title"),
                "text": self.getl("win_block_notification_block_deleted_text"),
                "icon": self.getv("block_footer_btn_delete_msg_btn_yes_icon_path"),
                "timer": 1500,
                "position": "bottom right"
            }
            utility_cls.Notification(self._stt, self, notif_dict)
            self.get_appv("log").write_log(f"BlockView. Block Deleted. Record ID: {rec_id}")
            main_dict = {
                "name": "win_block",
                "action": "block_deleted",
                "id": rec_id
            }
            self.events(main_dict)

        self._dont_clear_menu = False

    def _load_win_position(self):
        if "block_view_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("block_view_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self.ln_delim.move(10, g["delimiter"])
            self._set_areas_size()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if "block_view_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("block_view_win_geometry", {}, save_to_file=True)

        g = self.get_appv("block_view_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["delimiter"] = self.ln_delim.pos().y()

        return super().closeEvent(a0)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w, self.lbl_title.height())
        self.btn_view_diary.move(w - 320, self.btn_view_diary.pos().y())
        self.btn_tags.move(w - 140, self.btn_tags.pos().y())

        self.ln_delim.resize(w - 20, self.ln_delim.height())
        self._set_areas_size()

        self.btn_close_all.move(w - 170, h - 70)
        self.btn_cancel.move(w - 90, h - 30)

        self.line.move(10, h - 40)
        self.line.resize(w - 20, self.line.height())

        self.frm_tags.move(w - 450, 90)

        return super().resizeEvent(a0)

    def _set_areas_size(self):
        y = self.ln_delim.pos().y()
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        if h - y < 130:
            y = h - 130
        if y < 140:
            y = 140

        self.ln_delim.move(10, y)
        self.ln_delim.resize(w - 20, 5)
        
        self.lst_blocks.resize(w - 20, y - 90)
        
        self.area.move(10, y + 5)
        self.area.resize(w - 20, h - y - 80)

    def changeEvent(self, a0: QEvent) -> None:
        if not self._dont_clear_menu:
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _ln_delim_mouse_click(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_mode = [self.ln_delim.pos().y(), QCursor.pos().y()]

    def _ln_delim_mouse_release(self, e):
        self._drag_mode = None

    def _ln_delim_mouse_move(self, e):
        if self._drag_mode:
            new_y = QCursor.pos().y() - self._drag_mode[1]
            self.ln_delim.move(10, self._drag_mode[0] + new_y)
            self._set_areas_size()

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.txt_filter: QLineEdit = self.findChild(QLineEdit, "txt_filter")

        self.btn_clear_filter: QPushButton = self.findChild(QPushButton, "btn_clear_filter")
        self.btn_view_diary: QPushButton = self.findChild(QPushButton, "btn_view_diary")
        self.btn_tags: QPushButton = self.findChild(QPushButton, "btn_tags")
        self.btn_close_all: QPushButton = self.findChild(QPushButton, "btn_close_all")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")

        self.line: QFrame = self.findChild(QFrame, "line")
        self.ln_delim: QFrame = self.findChild(QFrame, "ln_delim")
        self.lst_blocks: QListWidget = self.findChild(QListWidget, "lst_blocks")
        self.chk_tag: QCheckBox = self.findChild(QCheckBox, "chk_tag")
        
        self.area: QScrollArea = self.findChild(QScrollArea, "area")
        self.vert_lay: QVBoxLayout = QVBoxLayout()
        self._widget: QWidget = QWidget()
        self._widget.setLayout(self.vert_lay)
        self.area.setWidget(self._widget)

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("block_view_win_title"))

        self.lbl_count.setToolTip(self.getl("block_view_lbl_count_tt"))
        self.lbl_title.setText(self.getl("block_view_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("block_view_lbl_title_tt"))

        self.chk_tag.setText(self.getl("block_view_chk_tag_text"))
        self.chk_tag.setToolTip(self.getl("block_view_chk_tag_tt"))
        
        self.btn_view_diary.setText(self.getl("block_view_btn_view_diary_text"))
        self.btn_view_diary.setToolTip(self.getl("block_view_btn_view_diary_tt"))
        self.btn_tags.setText(self.getl("block_view_btn_tags_text").replace("#1", self.getl("block_view_btn_tags_#1")))
        self.btn_tags.setToolTip(self.getl("block_view_btn_tags_tt"))
        self.btn_close_all.setText(self.getl("block_view_btn_close_all_text"))
        self.btn_close_all.setToolTip(self.getl("block_view_btn_close_all_tt"))
        self.btn_cancel.setText(self.getl("btn_cancel"))

    def _setup_widgets_apperance(self):
        self._define_block_view_win_apperance()
        
        self._define_labels_apperance(self.lbl_title, "block_view_title")
        self._define_labels_apperance(self.lbl_count, "block_view_lbl_count")
        
        self._define_buttons_apperance(self.btn_tags, "block_view_btn_tags")
        self._define_buttons_apperance(self.btn_view_diary, "block_view_btn_view_diary")
        if isinstance(self._parent_obj, DiaryView):
            self.btn_view_diary.setEnabled(False)
        self._define_buttons_apperance(self.btn_cancel, "block_view_btn_cancel")
        self._define_buttons_apperance(self.btn_close_all, "block_view_btn_close_all")
        
        self.btn_clear_filter.setStyleSheet(self.getl("block_view_btn_clear_filter_stylesheet"))
        self.ln_delim.setStyleSheet(self.getl("block_view_ln_delim_stylesheet"))
        
        self._define_text_box_apperance(self.txt_filter, "block_view_txt_filter")

        self.chk_tag.setStyleSheet(self.getv("block_view_chk_tag_stylesheet"))

    def _define_block_view_win_apperance(self):
        self.setStyleSheet(self.getv("block_view_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("block_view_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(530, 300)

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

    def _define_tags_frame(self):
        self._define_tags_widgets()
        self._define_tags_text()
        self._define_tags_apperance()

        self._frm_tags_tags_list = []

        self._frm_tags_populate_widgets()

        self.btn_tag_cancel.clicked.connect(self._btn_tag_cancel_click)
        self.btn_tag_close.clicked.connect(self._btn_tag_close_click)
        self.lst_tag_tags.itemClicked.connect(self._lst_tag_tags_item_changed)
        self.btn_tag_invert.clicked.connect(self._btn_tag_invert_click)
        self.btn_tag_reset.clicked.connect(self._btn_tag_reset_click)
        self.btn_tag_ok.clicked.connect(self._btn_tag_ok_click)

    def _btn_tag_ok_click(self):
        self.tags_are_selected(list(self._frm_tags_tags_list))

    def _btn_tag_reset_click(self):
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
                item.setSelected(False)
        self._frm_tags_populate_data()

    def _btn_tag_invert_click(self):
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
            if item.isSelected():
                item.setSelected(False)
            else:
                item.setSelected(True)
        self._frm_tags_populate_data()

    def _lst_tag_tags_item_changed(self):
        self._frm_tags_populate_data()

    def _frm_tags_update_list(self):
        db_tags = db_tag_cls.Tag(self._stt)
        tags = db_tags.get_all_tags_translated()
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
            for tag in tags:
                if tag[0] == item.data(Qt.UserRole):
                    txt = f"{tag[1]} ({db_tags.how_many_times_is_used(tag[0])})"
                    item.setText(txt)
                    if tag[0] in self._frm_tags_tags_list:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
        self._frm_tags_populate_data()

    def _frm_tags_populate_widgets(self):
        self.lst_tag_tags.clear()
        db_tags = db_tag_cls.Tag(self._stt)
        tags = db_tags.get_all_tags_translated()
        for tag in tags:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, tag[0])
            txt = f"{tag[1]} ({db_tags.how_many_times_is_used(tag[0])})"
            item.setText(txt)
            if tag[0] in self._frm_tags_tags_list:
                item.setSelected(True)
            else:
                item.setSelected(False)
                
            self.lst_tag_tags.addItem(item)
        self._frm_tags_populate_data()
        
    def _frm_tags_populate_data(self):
        self._frm_tags_tags_list = []
        item_lst = []
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
            if item.isSelected():
                item_lst.append(item.text())
                self._frm_tags_tags_list.append(item.data(Qt.UserRole))

        if item_lst:
            self.lbl_tag_tags.setText(", ".join(item_lst))
        else:
            self.lbl_tag_tags.setText(self.getl("frm_tags_lbl_tag_tags_no_data_text"))

    def _btn_tag_close_click(self):
        self._frm_tags_hide_me()

    def _btn_tag_cancel_click(self):
        self._frm_tags_hide_me()

    def _frm_tags_hide_me(self):
        self.frm_tags.setVisible(False)
    
    def _frm_tags_show_me(self, tags_list: list = None) -> None:
        self._frm_tags_populate_data()
        self.frm_tags.setVisible(True)

    def _define_tags_widgets(self):
        self.frm_tags: QFrame = self.findChild(QFrame, "frm_tags")
        
        self.lbl_tag_title: QLabel = self.findChild(QLabel, "lbl_tag_title")
        self.lbl_tag_tags: QLabel = self.findChild(QLabel, "lbl_tag_tags")
        
        self.lst_tag_tags: QListWidget = self.findChild(QListWidget, "lst_tag_tags")

        self.btn_tag_invert: QPushButton = self.findChild(QPushButton, "btn_tag_invert")
        self.btn_tag_close: QPushButton = self.findChild(QPushButton, "btn_tag_close")
        self.btn_tag_reset: QPushButton = self.findChild(QPushButton, "btn_tag_reset")
        self.btn_tag_ok: QPushButton = self.findChild(QPushButton, "btn_tag_ok")
        self.btn_tag_cancel: QPushButton = self.findChild(QPushButton, "btn_tag_cancel")

    def _define_tags_text(self):
        self.lbl_tag_title.setText(self.getl("frm_tags_lbl_title_text"))
        self.lbl_tag_title.setToolTip(self.getl("frm_tags_lbl_title_tt"))

        self.btn_tag_invert.setText(self.getl("frm_tags_btn_tag_invert_text"))
        self.btn_tag_invert.setToolTip(self.getl("frm_tags_btn_tag_invert_tt"))

        self.btn_tag_reset.setText(self.getl("frm_tags_btn_tag_reset_text"))
        self.btn_tag_reset.setToolTip(self.getl("frm_tags_btn_tag_reset_tt"))

        self.btn_tag_ok.setText(self.getl("frm_tags_btn_tag_ok_text"))
        self.btn_tag_ok.setToolTip(self.getl("frm_tags_btn_tag_ok_tt"))

        self.btn_tag_cancel.setText(self.getl("frm_tags_btn_tag_cancel_text"))
        self.btn_tag_cancel.setToolTip(self.getl("frm_tags_btn_tag_cancel_tt"))

    def _define_tags_apperance(self):
        self.frm_tags.setFrameShape(self.getv("frm_tags_frame_frame_shape"))  # Value 1
        self.frm_tags.setFrameShadow(self.getv("frm_tags_frame_frame_shadow"))  # Value 32
        self.frm_tags.setLineWidth(self.getv("frm_tags_frame_line_width"))
        self.frm_tags.setStyleSheet(self.getv("frm_tags_frame_stylesheet"))
        self.frm_tags.setVisible(False)

        self.lst_tag_tags.setStyleSheet(self.getv("frm_tags_lst_tag_stylesheet"))

        self.lbl_tag_title.setStyleSheet(self.getv("frm_tags_lbl_tag_title_stylesheet"))
        self.lbl_tag_tags.setStyleSheet(self.getv("frm_tags_lbl_tag_tags_stylesheet"))

        self.btn_tag_invert.setStyleSheet(self.getv("frm_tags_btn_tag_invert_stylesheet"))
        self.btn_tag_close.setStyleSheet(self.getv("frm_tags_btn_tag_close_stylesheet"))
        self.btn_tag_reset.setStyleSheet(self.getv("frm_tags_btn_tag_reset_stylesheet"))
        self.btn_tag_ok.setStyleSheet(self.getv("frm_tags_btn_tag_ok_stylesheet"))
        self.btn_tag_cancel.setStyleSheet(self.getv("frm_tags_btn_tag_cancel_stylesheet"))


class DiaryViewItemText(QTextEdit):
    def __init__(self, settings: settings_cls.Settings, parent_obj, text: str, main_win, force_show_content:bool = False, *args, **kwargs):
        super().__init__(parent_obj, *args, **kwargs)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._show_content = force_show_content
        self._main_win = main_win
        self._parent_widget = parent_obj
        self.setText(text)
        self._text_handler = text_handler_cls.TextHandler(self._stt, self, self._main_win)

        self._define_apperance()
        # self.show()
        if self._show_content:
            self._show_definitions()

        # Connect events with slots


    def show_content(self):
        self._show_content = True
        self._show_definitions()

    def mark_search_string(self, find_string: str, match_case: bool = False):
        if not find_string:
            return
        
        if not self.getv("diary_view_mark_search_string"):
            return
        
        f_color = self.getv("diary_view_mark_search_string_fore_color")
        b_color = self.getv("diary_view_mark_search_string_back_color")

        if match_case:
            txt = self.toPlainText()
        else:
            txt = self.toPlainText().lower()
            find_string = find_string.lower()
        
        find_string = find_string.replace("/", " ")

        find_list = [x for x in find_string.split(" ") if x != ""]

        for find_txt in find_list:
            pos = 0
            while pos >= 0:
                pos = txt.find(find_txt, pos)
                if pos >= 0:
                    cur = self.textCursor()
                    cur.setPosition(pos)
                    cur.movePosition(cur.Right, cur.KeepAnchor, len(find_txt))

                    cf = QTextCharFormat()
                    if f_color:
                        color = QColor()
                        color.setNamedColor(f_color)
                        cf.setForeground(color)
                    if b_color:
                        color = QColor()
                        color.setNamedColor(b_color)
                        cf.setBackground(color)
                    
                    cur.setCharFormat(cf)
                    cur.setPosition(0)
                    self.setTextCursor(cur)
                    
                    pos = pos + len(find_txt)

    def _show_definitions(self):
        self._text_handler._populate_def_list()
        self._text_handler.check_definitions()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self._text_handler.mouse_press_event(e)    

        return super().mousePressEvent(e)

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        self._text_handler.show_definition_on_mouse_hover(e)
        return super().mouseMoveEvent(e)

    def _resize_me(self):
        fm = QFontMetrics(self.font())
        font_h = fm.height()

        h = 0
        document = self.document()
        block = document.begin()
        count = 1
        while block.isValid():
            blockRect = self.document().documentLayout().blockBoundingRect(block)
            if blockRect.height() > font_h:
                h += font_h * 2
            else:
                h += blockRect.height()
            block = block.next()
            count += 1
        
        h = int(h + 10)

        if h < 60:
            h = 60
        self.setFixedHeight(h)

    def _define_apperance(self):
        self.setFrameShape(self.getv("diary_item_text_box_frame_shape"))
        self.setFrameShadow(self.getv("diary_item_text_box_frame_shadow"))
        self.setLineWidth(self.getv("diary_item_text_box_line_width"))
        self.setAcceptRichText(False)

        font = QFont(self.getv("diary_item_text_box_font_name"), self.getv("diary_item_text_box_font_size"))
        font.setWeight(self.getv("diary_item_text_box_font_weight"))
        font.setItalic(self.getv("diary_item_text_box_font_italic"))
        font.setUnderline(self.getv("diary_item_text_box_font_underline"))
        font.setStrikeOut(self.getv("diary_item_text_box_font_strikeout"))
        self.setFont(font)

        self.setReadOnly(True)

        self.setStyleSheet(self.getv("diary_item_text_box_stylesheet"))


class DiaryViewItemImage(QLabel):
    def __init__(self, settings: settings_cls.Settings, parent_obj, media_id: int, main_win, force_show_content: bool = False, *args, **kwargs):
        super().__init__(parent_obj, *args, **kwargs)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._show_content = force_show_content
        self._main_win = main_win
        self._parent_widget = parent_obj
        self._media_id = media_id

        media = db_media_cls.Media(self._stt)
        if media.is_media_exist(self._media_id):
            self._i_am_image = True
        else:
            self._i_am_image = False            

        if self._show_content:
            if media.is_media_exist(self._media_id):
                media.load_media(self._media_id)
                self._media_file = media.media_file
            else:
                media = db_media_cls.Files(self._stt, self._media_id)
                self._media_file = media.file_file
        else:
            self._media_file = None

        self._define_apperance()

        if self._show_content:
            self._load_data()

        # Connect events with slots

    def show_content(self):
        self._show_content = True
        if self._media_file is None:
            media = db_media_cls.Media(self._stt)
            if media.is_media_exist(self._media_id):
                media.load_media(self._media_id)
                self._media_file = media.media_file
            else:
                media = db_media_cls.Files(self._stt, self._media_id)
                self._media_file = media.file_file

        self._load_data()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.RightButton:
            data = {
                "item": "image",
                "type": "right_click",
                "data": self._media_id,
                "is_image": self._i_am_image
            }
            self._parent_widget.item_event(data)
        return super().mousePressEvent(ev)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        data = {
            "item": "image",
            "type": "double_click",
            "data": self._media_id,
            "is_image": self._i_am_image
        }
        self._parent_widget.item_event(data)
        return super().mouseDoubleClickEvent(a0)

    def _resize_me(self):
        size = self._parent_widget.area.contentsRect().height()
        w = int(self._parent_widget.area.contentsRect().width() / 2)

        if size > w:
            size = w

        self.setFixedSize(size, size)

        if self._show_content:
            self._load_data()

    def _load_data(self):
        if self._i_am_image:
            img = QPixmap()
            result = img.load(self._media_file)
            
            size = self.size()
            
            if result:
                if img.height() > size.height() or img.width() > size.width():
                    img = img.scaled(size, Qt.KeepAspectRatio)
                self.setPixmap(img)
        else:
            db_media = db_media_cls.Files(self._stt)
            if db_media.is_file_exist(self._media_id):
                db_media.load_file(self._media_id)
                file_util = utility_cls.FileDialog(self._stt)
                file_ext = file_util.FileInfo().file_extension(db_media.file_file)
                file_ext = file_ext.strip(".")
                
                for i in range(16, 100):
                    font = QFont("Comic Sans MS", i)
                    fm = QFontMetrics(font)
                    if fm.width(file_ext) >= self.width():
                        break
                if i < 16:
                    i = 17
                font = QFont("Comic Sans MS", i - 1)
                self.setFont(font)
                self.setText(file_ext)
            else:
                self.setText("Error.")
    
    def _define_apperance(self):
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setStyleSheet(self.getv("diary_view_item_label_stylesheet"))


class DiaryViewItem(QFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, record_list: list, main_win, force_show_content: bool = False, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._show_content = force_show_content
        self._main_win = main_win
        self._record_list = record_list
        self._record_id = record_list[0]
        self._media_items = []
        self._clip: utility_cls.Clipboard = self.get_appv("cb")

        # Load GUI
        uic.loadUi(self.getv("diary_view_item_ui_file_path"), self)

        self._define_widgets()
        self._define_widgets_apperance()
        self._define_text_box()

        for media_id in self._record_list[10]:
            item = DiaryViewItemImage(self._stt, self, media_id, self._main_win, force_show_content=self._show_content)
            self._media_items.append(item)
            self.h_layout.addWidget(item)

        self.show()

        # Connect events with slots

    def show_content(self):
        if self._show_content:
            return

        self._show_content = True

        # Show Text formating
        self.txt_box.show_content()

        # Show images
        for i in range(self.h_layout.count()):
            item = self.h_layout.itemAt(i).widget()
            if isinstance(item, DiaryViewItemImage):
                item.show_content()

    def is_content_shown(self) -> bool:
        return self._show_content

    def mark_search_string(self, find_txt: str, match_case: bool = False):
        self.txt_box.mark_search_string(find_txt, match_case=match_case)

    def item_event(self, event_dict: dict):
        if event_dict["item"] == "image":
            if event_dict["type"] == "double_click":
                media_id = event_dict["data"]
                if event_dict["is_image"]:
                    utility_cls.PictureView(self._stt, self._main_win, self._record_list[10], start_with_media_id=media_id)
                else:
                    utility_cls.FileInfo(self._stt, self._main_win, media_id)

            if event_dict["type"] == "right_click":
                if event_dict["is_image"]:
                    self._item_menu_if_image(event_dict=event_dict)
                else:
                    self._item_menu_if_file(event_dict=event_dict)

    def _item_menu_if_file(self, event_dict: dict):
        db_media = db_media_cls.Files(self._stt, event_dict["data"])
        file_util = utility_cls.FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt, db_media.file_file)

        disab = []
        if self._clip.is_clip_empty():
            disab.append(50)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [20, 40],
            "items": [
                [
                    10, self.getl("diary_view_item_image_menu_file_info_text"), self.getl("diary_view_item_image_menu_file_info_tt"), True, [], self.getv("file_info_win_icon_path")
                ],
                [
                    20, self.getl("diary_view_item_image_menu_file_open_text"), self.getl("diary_view_item_image_menu_file_open_tt"), True, [], file_info.icon()
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
        self.set_appv("menu", menu_dict)
        self._main_win._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self._main_win)

        result = self.get_appv("menu")["result"]
        media_id = event_dict["data"]
        if result == 10:
            utility_cls.FileInfo(self._stt, self._main_win, media_id)
        elif result == 20:
            abs_file_path = file_info.absolute_path()
            try:
                os.startfile(abs_file_path)
            except Exception as e:
                msg_dict = {
                    "title": self.getl("block_image_item_menu_open_file_error_title"),
                    "text": self.getl("block_image_item_menu_open_file_error_text").replace("#1", db_media.file_file)
                }
                self._main_win._dont_clear_menu = True
                utility_cls.MessageInformation(self._stt, self, msg_dict, app_modal=True)
        elif result == 30:
            self._clip.copy_to_clip(media_id)
        elif result == 40:
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif result == 50:
            self._clip.clear_clip()

    def _item_menu_if_image(self, event_dict: dict):
        disab = []
        if self._clip.is_clip_empty():
            disab.append(50)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [20, 40],
            "items": [
                [
                    10, self.getl("diary_view_item_image_menu_show_text"), self.getl("diary_view_item_image_menu_show_tt"), True, [], self.getv("diary_view_item_image_menu_show_icon_path")
                ],
                [
                    20, self.getl("diary_view_item_image_menu_show_all_text"), self.getl("diary_view_item_image_menu_show_all_tt"), True, [], self.getv("diary_view_item_image_menu_show_icon_path")
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
        self.set_appv("menu", menu_dict)
        self._main_win._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self._main_win)

        result = self.get_appv("menu")["result"]
        media_id = event_dict["data"]
        if result == 10:
            utility_cls.PictureView(self._stt, self._main_win, self._record_list[10], start_with_media_id=media_id)
        elif result == 20:
            utility_cls.PictureBrowse(self._stt, self._main_win, self._record_list[10])
        elif result == 30:
            self._clip.copy_to_clip(media_id)
        elif result == 40:
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif result == 50:
            self._clip.clear_clip()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._resize_me
        return super().resizeEvent(a0)

    def _resize_me(self):
        if self._show_content:
            return

        spacer = self.getv("diary_view_item_text_image_spacer")

        txt_max_width = self._calculate_txt_box_width(self.txt_box)

        self.txt_box.move(125, 0)
        if self._record_list[10]:
            self.txt_box.setFixedWidth(txt_max_width)
        else:
            self.txt_box.setFixedWidth(self.width() - 125)

        self.txt_box._resize_me()
        self.setFixedHeight(self.txt_box.height())

        if self._record_list[10]:
            self.area.move(self.txt_box.width() + 125 + spacer, 0)
            self.area.setFixedSize(self.width() - 125 + spacer - txt_max_width, self.height())
            for item in self._media_items:
                item._resize_me()

    def _calculate_txt_box_width(self, txt_box: QTextEdit) -> int:
        txt_max_width = 0
        fm = QFontMetrics(txt_box.font())
        for i in txt_box.toPlainText().split("\n"):
            if fm.width(i) > txt_max_width:
                txt_max_width = fm.width(i)
        txt_max_width += 10
        
        txt_limit_width = self.width() - 125
        if self._record_list[10]:
            txt_limit_width -= 150
        if txt_limit_width < 30:
            txt_limit_width = 30

        if txt_max_width > txt_limit_width:
            txt_max_width = txt_limit_width

        return txt_max_width

    def _define_widgets(self):
        self.lbl_day: QLabel = self.findChild(QLabel, "lbl_day")
        self.lbl_date: QLabel = self.findChild(QLabel, "lbl_date")
        self.lbl_tag: QLabel = self.findChild(QLabel, "lbl_tag")
        self.area: QScrollArea = self.findChild(QScrollArea, "area")

        self.h_layout = QHBoxLayout()
        self.widget = QWidget()

        self.widget.setLayout(self.h_layout)
        self.area.setWidget(self.widget)

    def _define_widgets_apperance(self):
        self.lbl_day.setStyleSheet(self.getv("diary_item_lbl_day_stylesheet"))
        self.lbl_date.setStyleSheet(self.getv("diary_item_lbl_date_stylesheet"))
        self.lbl_tag.setStyleSheet(self.getv("diary_item_lbl_tag_stylesheet"))

        self.area.setContentsMargins(0,0,0,0)
        self.area.setViewportMargins(0,0,0,0)
        self.widget.setContentsMargins(0,0,0,0)
        self.h_layout.setContentsMargins(0,0,0,0)
        self.h_layout.setSpacing(5)

        self.area.setStyleSheet(self.getv("diary_item_area_stylesheet"))
        self.area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget.setStyleSheet(self.getv("diary_item_area_widget_stylesheet"))

        if not self._record_list[10]:
            self.area.setVisible(False)

        date_obj = utility_cls.DateTime(self._stt)
        date_dict = date_obj.make_date_dict(self._record_list[2])

        self.lbl_day.setText(date_dict["day_name"])
        self.lbl_date.setText(date_dict["date"])

        if self._record_list[9]:
            tags = ""
            tooltip = self.getl("diary_view_item_lbl_tag_tt")
            for i in self._record_list[9]:
                tags += i[1] + ", "
                tooltip += " "*10 + i[1] + "\n"
            tags = tags.rstrip().rstrip(",")
            self.lbl_tag.setText(tags)
            self.lbl_tag.setToolTip(tooltip)
        else:
            self.lbl_tag.setText("")
            self.lbl_tag.setToolTip("")

    def _define_text_box(self):
        self.txt_box = DiaryViewItemText(self._stt, self, self._record_list[4], self._main_win, force_show_content=self._show_content)
        self.txt_box.setFixedWidth(self._calculate_txt_box_width(self.txt_box))


class DiaryView(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_obj, block_list: list = None, *args, **kwargs):
        super().__init__(parent_obj, *args, **kwargs)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._block_list = block_list
        self._parent_obj = parent_obj
        self._dont_clear_menu = False
        self._tags_list = []
        self._record_data = self._calculate_data()
        self._abort = False
        self._window_loaded = False

        # Load GUI
        uic.loadUi(self.getv("diary_view_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._define_tags_frame()
        self.frm_tags.raise_()

        # self._populate_widgets()
        self._load_win_position()

        # Connect events with slots
        self.btn_clear_filter.clicked.connect(self.btn_clear_filter_click)
        self.btn_clear_from_date.clicked.connect(self.btn_clear_from_date_click)
        self.btn_clear_to_date.clicked.connect(self.btn_clear_to_date_click)
        self.btn_apply_filter.clicked.connect(self.btn_apply_filter_click)
        self.btn_tags.clicked.connect(self.btn_tags_click)
        self.btn_view_blocks.clicked.connect(self.btn_view_blocks_click)
        self.btn_view.clicked.connect(self.btn_view_click)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        
        self.txt_from_date.mouseDoubleClickEvent = self._txt_from_date_double_click
        self.txt_from_date.textChanged.connect(self._txt_from_date_text_changed)
        self.txt_to_date.mouseDoubleClickEvent = self._txt_to_date_double_click
        self.txt_to_date.textChanged.connect(self._txt_to_date_text_changed)
        self.txt_filter.textChanged.connect(self.txt_filter_text_changed)
        self.txt_filter.returnPressed.connect(self.txt_filter_return_pressed)

        self.btn_loading_stop.clicked.connect(self.btn_loading_stop_click)

        self.get_appv("signal").signalCloseAllBlocks.connect(self._signal_close_all_blocks)

        self.show()
        QCoreApplication.processEvents()
        if self._block_list:
            self._filter_data(filter_data=False)
        else:
            self._filter_data()
        QCoreApplication.processEvents()
        self._window_loaded = True
        self._show_data()
        self._resize_items()
        self.area.viewport().installEventFilter(self)

    def _signal_close_all_blocks(self):
        self.btn_cancel_click()

    def eventFilter(self, obj, event):
        if obj == self.area.viewport() and event.type() == event.Paint:
            visible_set = set(range(self.area.verticalScrollBar().value(), self.area.verticalScrollBar().value() + self.area.viewport().contentsRect().height() + 1))
            for i in range(self.vert_lay.count()):
                item = self.vert_lay.itemAt(i).widget()
                if item is not None:
                    item_size = set(range(item.pos().y(), item.pos().y() + item.height()))
                    if visible_set & item_size:
                        item.show_content()
        return super().eventFilter(obj, event)

    def events(self, event_dict: dict):
        if event_dict["action"] == "cm":
            self._dont_clear_menu = True

    def btn_loading_stop_click(self):
        self._abort = True

    def tags_are_selected(self, tag_list: list):
        if tag_list:
            txt = self.getl("diary_view_btn_tags_text").replace("#1", str(len(tag_list)))
            self.btn_tags.setText(txt)
            self._tags_list = tag_list
        else:
            txt = self.getl("diary_view_btn_tags_text").replace("#1", self.getl("diary_view_btn_tags_#1"))
            self.btn_tags.setText(txt)
            self._tags_list = []
        self._filter_data()

    def _get_date_string(self, date_str: str, tags: list) -> str:
        date_obj = utility_cls.DateTime(self._stt)
        date_dict = date_obj.make_date_dict(date_str)
        txt = f"{date_dict['day_name']}, {date_dict['day']}. {date_dict['month_name']} {date_dict['year']}.\n"

        if tags:
            txt = txt.rstrip()
            txt += " " * 10 + " ".join([f"[{x[1]}]" for x in tags]) + "\n"
        return txt

    def _show_data(self):
        if not self._window_loaded:
            return
        
        for i in range(self.vert_lay.count()):
            if self.vert_lay.itemAt(0).widget() is not None:
                item = self.vert_lay.itemAt(0).widget()
                self.vert_lay.removeWidget(item)
                item.close()

        QCoreApplication.processEvents()
        
        if not self.vert_lay.count():
            self.vert_lay.addSpacerItem(QSpacerItem(20, 2, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.frm_loading.setVisible(True)
        self.prg_loading.setMaximum(len(self._record_data))
        
        count = 0
        shown = 0
        self.txt_view.setText("")
        cf_normal = self.txt_view.textCursor().charFormat()
        cf_date = QTextCharFormat()
        cf_date.setForeground(QColor(self.getv("diary_view_txt_view_date_fore_color")))
        cf_date.setBackground(QColor(self.getv("diary_view_txt_view_date_back_color")))
        font_date = self.txt_view.font()
        font_date.setPointSize(self.getv("diary_view_txt_view_date_font_size"))
        cf_date.setFont(font_date)
        rec_date = ""
        date_map = []
        for record in self._record_data:
            if self._abort:
                break
            count += 1
            if record[11]:
                if rec_date != record[2]:
                    date_map.append([self.txt_view.textCursor().position(), self._get_date_string(record[2], tags=None)])
                    cur = self.txt_view.textCursor()
                    cur.setCharFormat(cf_date)
                    cur.insertText(self._get_date_string(record[2], tags=None))
                    self.txt_view.setTextCursor(cur)
                    rec_date = record[2]
                
                txt = record[4]
                if txt:
                    if txt[-1:] == "\n":
                        txt += "\n"
                    else:
                        txt += "\n\n"
                    
                    cur = self.txt_view.textCursor()
                    cur.setCharFormat(cf_normal)
                    cur.insertText(txt)
                    self.txt_view.setTextCursor(cur)

                item = DiaryViewItem(self._stt, self.area, record, self)
                self.vert_lay.insertWidget(self.vert_lay.count() - 1, item)
                item.mark_search_string(self.txt_filter.text(), match_case=self.chk_case.isChecked())
                self.prg_loading.setValue(count)
                # self._resize_items()
                QCoreApplication.processEvents()
                shown += 1
        
        self.txt_view._show_definitions()
        self.txt_view.mark_search_string(self.txt_filter.text(), self.chk_case.isChecked())
        
        self._resize_items()

        for i in date_map:
            cur = self.txt_view.textCursor()
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, len(i[1]))
            cur.setCharFormat(cf_date)
            self.txt_view.setTextCursor(cur)

        cur = self.txt_view.textCursor()
        cur.setPosition(len(self.txt_view.toPlainText()))
        self.txt_view.setTextCursor(cur)

        self._abort = False
        self.frm_loading.setVisible(False)
        self.lbl_count.setText(self.getl("diary_view_lbl_count_text").replace("#1", str(shown)).replace("#2", str(len(self._record_data))))

    def _filter_data(self, show_data: bool = True, filter_data: bool = True):
        date_obj = utility_cls.DateTime(self._stt)
        if self.txt_from_date.text():
            date_dict_from = date_obj.make_date_dict(self.txt_from_date.text())
        else:
            date_dict_from = None
        if self.txt_to_date.text():
            date_dict_to = date_obj.make_date_dict(self.txt_to_date.text())
        else:
            date_dict_to = None

        # Show only blocks passed in block_list
        count = 0
        for idx, record in enumerate(self._record_data):
            if self._block_list is None:
                count += 1
                self._record_data[idx][11] = True
            else:
                if record[0] in self._block_list:
                    count += 1
                    self._record_data[idx][11] = True
                else:
                    self._record_data[idx][11] = False

        if not filter_data:
            if show_data:
                self._show_data()
            return

        # Filter data
        count = 0
        for idx, record in enumerate(self._record_data):
            # Filter tags
            tag_list = [x[0] for x in record[9]]
            if self._tags_list:
                if self.chk_tag.isChecked():
                    visible = True
                    for tag in self._tags_list:
                        if tag in tag_list:
                            visible = False
                            break
                    self._record_data[idx][11] = visible
                else:
                    visible = True
                    for tag in self._tags_list:
                        if tag not in tag_list:
                            visible = False
                            break
                    self._record_data[idx][11] = visible
            
            # Filter dates
            if date_dict_from:
                if record[3] < date_dict_from["date_int"]:
                    self._record_data[idx][11] = False
            if date_dict_to:
                if record[3] > date_dict_to["date_int"]:
                    self._record_data[idx][11] = False

            # Filter user string
            txt = record[1] + record[2] + record[4]
            if self.txt_filter.text():
                if self.chk_case.isChecked():
                    if not self._filter_apply(self.txt_filter.text(), txt):
                        self._record_data[idx][11] = False
                else:
                    if not self._filter_apply(self.txt_filter.text().lower(), txt.lower()):
                        self._record_data[idx][11] = False

            # Count visible records
            if record[11]:
                count += 1

        if show_data:
            self._show_data()

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

    def _calculate_data(self):
        db_rec = db_record_cls.Record(self._stt)
        db_data = db_record_data_cls.RecordData(self._stt)
        db_tag = db_tag_cls.Tag(self._stt)
        
        # Get all tags dict
        tags_dict = {}
        all_tags = db_tag.get_all_tags_translated()
        for tag in all_tags:
            tags_dict[tag[0]] = tag[1]
        
        # Get block list with list of tags and media ids
        tag_media_map = db_data.get_tags_and_media_for_all_records()
        records = db_rec.get_all_records()

        record_data = []
        for record in records:
            rec_tags = []
            for tag in tag_media_map:
                if tag[0] == record[0]:
                    for i in tag[1]:
                        rec_tags.append([i, tags_dict[i]])
                    break
            
            rec_media = []
            for media in tag_media_map:
                if media[0] == record[0]:
                    for i in media[2]:
                        rec_media.append(i)
                    break
            
            record_data.append([
                record[0],
                record[1],
                record[2],
                record[3],
                record[4].rstrip("\n"),
                record[5],
                record[6],
                record[7],
                record[8],
                list(rec_tags),
                list(rec_media),
                True]
            )

        return record_data

    def btn_clear_filter_click(self):
        self.txt_filter.setText("")

    def btn_clear_from_date_click(self):
        self.txt_from_date.setText("")

    def btn_clear_to_date_click(self):
        self.txt_to_date.setText("")

    def btn_apply_filter_click(self):
        self.area.viewport().removeEventFilter(self)
        self._filter_data()
        self.area.viewport().installEventFilter(self)

    def btn_view_click(self):
        if self.txt_view.isVisible():
            self.txt_view.setVisible(False)
            self.btn_view.setText(self.getl("diary_view_btn_view_txt_text"))
            self.btn_view.setToolTip(self.getl("diary_view_btn_view_txt_tt"))
        else:
            self.txt_view.setVisible(True)
            self.btn_view.setText(self.getl("diary_view_btn_view_detail_text"))
            self.btn_view.setToolTip(self.getl("diary_view_btn_view_detail_tt"))

    def btn_cancel_click(self):
        self.close()

    def btn_tags_click(self):
        if self.frm_tags.isVisible():
            self.frm_tags.setVisible(False)
        else:
            self.frm_tags.setVisible(True)

    def btn_view_blocks_click(self):
        BlockView(self._stt, self)

    def _txt_from_date_double_click(self, e):
        date_obj = utility_cls.DateTime(self._stt)
        date_dict = date_obj.make_date_dict(self.txt_from_date.text())
        if date_dict is not None:
            start_date = date_dict["date"]
        else:
            start_date = date_obj.get_today_date()
        
        cal_dict = {
            "name": "diary_view_from_date_calendar",
            "position": QCursor().pos(),
            "date": start_date,
        }
        self._dont_clear_menu = True
        utility_cls.Calendar(self._stt, self, cal_dict)
        if cal_dict["result"]:
            self.txt_from_date.setText(cal_dict["result"])

    def _txt_from_date_text_changed(self):
        if self.txt_from_date.text():
            self.btn_clear_from_date.setVisible(True)
        else:
            self.btn_clear_from_date.setVisible(False)

    def _txt_to_date_double_click(self, e):
        date_obj = utility_cls.DateTime(self._stt)
        date_dict = date_obj.make_date_dict(self.txt_to_date.text())
        if date_dict is not None:
            start_date = date_dict["date"]
        else:
            start_date = date_obj.get_today_date()
        
        cal_dict = {
            "name": "diary_view_from_date_calendar",
            "position": QCursor().pos(),
            "date": start_date,
        }
        self._dont_clear_menu = True
        utility_cls.Calendar(self._stt, self, cal_dict)
        if cal_dict["result"]:
            self.txt_to_date.setText(cal_dict["result"])

    def _txt_to_date_text_changed(self):
        if self.txt_to_date.text():
            self.btn_clear_to_date.setVisible(True)
        else:
            self.btn_clear_to_date.setVisible(False)

    def txt_filter_text_changed(self):
        if self.txt_filter.text():
            self.btn_clear_filter.setVisible(True)
        else:
            self.btn_clear_filter.setVisible(False)

        fm = QFontMetrics(self.txt_filter.font())
        if fm.width(self.txt_filter.text()) > 170:
            self.btn_clear_filter.move(205, self.btn_clear_filter.pos().y())
        else:
            self.btn_clear_filter.move(180, self.btn_clear_filter.pos().y())

    def txt_filter_return_pressed(self):
        self.btn_apply_filter_click()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.resize(w - 420, self.lbl_title.height())
        self.frm_area.resize(w -20, h - 170)
        self.area.resize(self.frm_area.width(), self.frm_area.height())
        self.txt_view.resize(w -20, h - 170)

        self.btn_view_blocks.move(10, h -30)
        self.btn_view.move(150, h - 30)
        self.btn_cancel.move(w -85, h -30)

        self._resize_items()
        
        return super().resizeEvent(a0)    

    def _resize_items(self):
        for i in range(self.vert_lay.count()):
            if self.vert_lay.itemAt(i).widget():
                self.vert_lay.itemAt(i).widget().setFixedWidth(self.area.contentsRect().width() - 20)
                self.vert_lay.itemAt(i).widget()._resize_me()

    def _load_win_position(self):
        if "diary_view_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g = self.get_appv("diary_view_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self.txt_from_date.setText(g["from_date"])
            if self.txt_from_date.text():
                self.btn_clear_from_date.setVisible(True)
            self.txt_to_date.setText(g["to_date"])
            if self.txt_to_date.text():
                self.btn_clear_to_date.setVisible(True)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if "diary_view_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("diary_view_win_geometry", {}, save_to_file=True)

        g = self.get_appv("diary_view_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["from_date"] = self.txt_from_date.text()
        g["to_date"] = self.txt_to_date.text()

        return super().closeEvent(a0)

    def changeEvent(self, a0: QEvent) -> None:
        if not self._dont_clear_menu:
            dialog_queue = utility_cls.DialogsQueue()
            dialog_queue.remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.txt_filter: QLineEdit = self.findChild(QLineEdit, "txt_filter")
        self.txt_from_date: QLineEdit = self.findChild(QLineEdit, "txt_from_date")
        self.txt_to_date: QLineEdit = self.findChild(QLineEdit, "txt_to_date")

        self.chk_case: QCheckBox = self.findChild(QCheckBox, "chk_case")

        self.btn_clear_filter: QPushButton = self.findChild(QPushButton, "btn_clear_filter")
        self.btn_clear_from_date: QPushButton = self.findChild(QPushButton, "btn_clear_from_date")
        self.btn_clear_to_date: QPushButton = self.findChild(QPushButton, "btn_clear_to_date")
        self.btn_view_blocks: QPushButton = self.findChild(QPushButton, "btn_view_blocks")
        self.btn_tags: QPushButton = self.findChild(QPushButton, "btn_tags")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_apply_filter: QPushButton = self.findChild(QPushButton, "btn_apply_filter")
        self.btn_view: QPushButton = self.findChild(QPushButton, "btn_view")

        self.txt_view: DiaryViewItemText = DiaryViewItemText(self._stt, self, "", self)
        self.txt_view.move(10, 130)
        self.txt_view.setVisible(False)
        
        self.frm_area: QFrame = self.findChild(QFrame, "frm_area")
        
        # self.area = self.DiaryViewScrollArea(self.frm_area)
        self.area: QScrollArea = self.findChild(QScrollArea, "area")
        # self.area = QScrollArea()
        # self.area.setParent(self.frm_area)
        
        self.vert_lay: QVBoxLayout = QVBoxLayout()
        self._widget: QWidget = QWidget()
        self._widget.setLayout(self.vert_lay)
        self.area.setWidget(self._widget)

        self.frm_loading: QFrame = self.findChild(QFrame, "frm_loading")
        self.btn_loading_stop: QPushButton = self.findChild(QPushButton, "btn_loading_stop")
        self.lbl_loading: QLabel = self.findChild(QLabel, "lbl_loading")
        self.prg_loading: QProgressBar = self.findChild(QProgressBar, "prg_loading")

    def _setup_widgets_text(self):
        self.setWindowTitle(self.getl("diary_view_win_title"))

        self.lbl_count.setToolTip(self.getl("diary_view_lbl_count_tt"))
        self.lbl_title.setText(self.getl("diary_view_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("diary_view_lbl_title_tt"))

        self.chk_case.setText(self.getl("diary_view_chk_case_text"))
        self.chk_case.setToolTip(self.getl("diary_view_chk_case_tt"))

        self.btn_view_blocks.setText(self.getl("diary_view_btn_view_blocks_text"))
        self.btn_view_blocks.setToolTip(self.getl("diary_view_btn_view_blocks_tt"))
        self.btn_tags.setText(self.getl("diary_view_btn_tags_text").replace("#1", self.getl("diary_view_btn_tags_#1")))
        self.btn_tags.setToolTip(self.getl("diary_view_btn_tags_tt"))
        self.btn_apply_filter.setText(self.getl("diary_view_btn_apply_filter_text"))
        self.btn_apply_filter.setToolTip(self.getl("diary_view_btn_apply_filter_tt"))
        self.btn_view.setText(self.getl("diary_view_btn_view_txt_text"))
        self.btn_view.setToolTip(self.getl("diary_view_btn_view_txt_tt"))
        self.btn_cancel.setText(self.getl("btn_cancel"))

        self.lbl_loading.setText(self.getl("diary_view_lbl_loading_text"))
        self.lbl_loading.setToolTip(self.getl("diary_view_lbl_loading_tt"))
        self.prg_loading.setToolTip(self.getl("diary_view_lbl_loading_tt"))

    def _setup_widgets_apperance(self):
        self._define_diary_view_win_apperance()
        
        self._define_labels_apperance(self.lbl_title, "diary_view_title")
        self._define_labels_apperance(self.lbl_count, "diary_view_lbl_count")
        
        self._define_buttons_apperance(self.btn_tags, "diary_view_btn_tags")
        self._define_buttons_apperance(self.btn_apply_filter, "diary_view_btn_apply_filter")
        self._define_buttons_apperance(self.btn_cancel, "diary_view_btn_cancel")
        self._define_buttons_apperance(self.btn_view_blocks, "diary_view_btn_view_blocks")
        self._define_buttons_apperance(self.btn_view, "diary_view_btn_view")
        if isinstance(self._parent_obj, BlockView):
            self.btn_view_blocks.setEnabled(False)

        self.chk_case.setStyleSheet(self.getv("diary_view_chk_case_stylesheet"))
        
        self.btn_clear_filter.setStyleSheet(self.getv("diary_view_btn_clear_filter_stylesheet"))
        self.btn_clear_filter.setVisible(False)
        self.btn_clear_from_date.setStyleSheet(self.getv("diary_view_btn_clear_from_date_stylesheet"))
        self.btn_clear_from_date.setVisible(False)
        self.btn_clear_to_date.setStyleSheet(self.getv("diary_view_btn_clear_to_date_stylesheet"))
        self.btn_clear_to_date.setVisible(False)
        
        self._define_text_box_apperance(self.txt_filter, "diary_view_txt_filter")
        self._define_text_box_apperance(self.txt_from_date, "diary_view_txt_from_date")
        self._define_text_box_apperance(self.txt_to_date, "diary_view_txt_to_date")

        self.area.setContentsMargins(0,0,0,0)
        self.area.setViewportMargins(0,0,0,0)
        self.vert_lay.setContentsMargins(0,0,0,0)
        self.vert_lay.setSpacing(self.getv("diary_view_area_spacing"))
        self._widget.setContentsMargins(0,0,0,0)

        self.frm_loading.setStyleSheet(self.getv("diary_view_frm_loading_stylesheet"))
        self.btn_loading_stop.setStyleSheet(self.getv("diary_view_btn_loading_stop_stylesheet"))
        self.lbl_loading.setStyleSheet(self.getv("diary_view_lbl_loading_stylesheet"))
        self.prg_loading.setStyleSheet(self.getv("diary_view_prg_loading_stylesheet"))
        self.frm_loading.setVisible(False)
        self.frm_loading.move(360, 78)

    def _define_diary_view_win_apperance(self):
        self.setStyleSheet(self.getv("diary_view_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("diary_view_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(550, 250)

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

    # Tags Frame
    def _define_tags_frame(self):
        self._define_tags_widgets()
        self._define_tags_text()
        self._define_tags_apperance()

        self._frm_tags_tags_list = []

        self._frm_tags_populate_widgets()

        self.btn_tag_cancel.clicked.connect(self._btn_tag_cancel_click)
        self.btn_tag_close.clicked.connect(self._btn_tag_close_click)
        self.lst_tag_tags.itemClicked.connect(self._lst_tag_tags_item_changed)
        self.btn_tag_invert.clicked.connect(self._btn_tag_invert_click)
        self.btn_tag_reset.clicked.connect(self._btn_tag_reset_click)
        self.btn_tag_ok.clicked.connect(self._btn_tag_ok_click)

    def _btn_tag_ok_click(self):
        self.tags_are_selected(list(self._frm_tags_tags_list))

    def _btn_tag_reset_click(self):
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
                item.setSelected(False)
        self._frm_tags_populate_data()

    def _btn_tag_invert_click(self):
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
            if item.isSelected():
                item.setSelected(False)
            else:
                item.setSelected(True)
        self._frm_tags_populate_data()

    def _lst_tag_tags_item_changed(self):
        self._frm_tags_populate_data()

    def _frm_tags_update_list(self):
        db_tags = db_tag_cls.Tag(self._stt)
        tags = db_tags.get_all_tags_translated()
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
            for tag in tags:
                if tag[0] == item.data(Qt.UserRole):
                    txt = f"{tag[1]} ({db_tags.how_many_times_is_used(tag[0])})"
                    item.setText(txt)
                    if tag[0] in self._frm_tags_tags_list:
                        item.setSelected(True)
                    else:
                        item.setSelected(False)
        self._frm_tags_populate_data()

    def _frm_tags_populate_widgets(self):
        self.lst_tag_tags.clear()
        db_tags = db_tag_cls.Tag(self._stt)
        tags = db_tags.get_all_tags_translated()
        for tag in tags:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, tag[0])
            txt = f"{tag[1]} ({db_tags.how_many_times_is_used(tag[0])})"
            item.setText(txt)
            if tag[0] in self._frm_tags_tags_list:
                item.setSelected(True)
            else:
                item.setSelected(False)
                
            self.lst_tag_tags.addItem(item)
        self._frm_tags_populate_data()
        
    def _frm_tags_populate_data(self):
        self._frm_tags_tags_list = []
        item_lst = []
        for item in self.lst_tag_tags.findItems("", Qt.MatchFlag.MatchContains):
            if item.isSelected():
                item_lst.append(item.text())
                self._frm_tags_tags_list.append(item.data(Qt.UserRole))

        if item_lst:
            self.lbl_tag_tags.setText(", ".join(item_lst))
        else:
            self.lbl_tag_tags.setText(self.getl("frm_tags_lbl_tag_tags_no_data_text"))

    def _btn_tag_close_click(self):
        self._frm_tags_hide_me()

    def _btn_tag_cancel_click(self):
        self._frm_tags_hide_me()

    def _frm_tags_hide_me(self):
        self.frm_tags.setVisible(False)
    
    def _frm_tags_show_me(self, tags_list: list = None) -> None:
        self._frm_tags_populate_data()
        self.frm_tags.setVisible(True)

    def _define_tags_widgets(self):
        self.frm_tags: QFrame = self.findChild(QFrame, "frm_tags")
        
        self.lbl_tag_title: QLabel = self.findChild(QLabel, "lbl_tag_title")
        self.lbl_tag_tags: QLabel = self.findChild(QLabel, "lbl_tag_tags")
        
        self.lst_tag_tags: QListWidget = self.findChild(QListWidget, "lst_tag_tags")

        self.chk_tag: QCheckBox = self.findChild(QCheckBox, "chk_tag")

        self.btn_tag_invert: QPushButton = self.findChild(QPushButton, "btn_tag_invert")
        self.btn_tag_close: QPushButton = self.findChild(QPushButton, "btn_tag_close")
        self.btn_tag_reset: QPushButton = self.findChild(QPushButton, "btn_tag_reset")
        self.btn_tag_ok: QPushButton = self.findChild(QPushButton, "btn_tag_ok")
        self.btn_tag_cancel: QPushButton = self.findChild(QPushButton, "btn_tag_cancel")

    def _define_tags_text(self):
        self.lbl_tag_title.setText(self.getl("frm_tags_lbl_title_text"))
        self.lbl_tag_title.setToolTip(self.getl("frm_tags_lbl_title_tt"))

        self.btn_tag_invert.setText(self.getl("frm_tags_btn_tag_invert_text"))
        self.btn_tag_invert.setToolTip(self.getl("frm_tags_btn_tag_invert_tt"))

        self.btn_tag_reset.setText(self.getl("frm_tags_btn_tag_reset_text"))
        self.btn_tag_reset.setToolTip(self.getl("frm_tags_btn_tag_reset_tt"))

        self.btn_tag_ok.setText(self.getl("frm_tags_btn_tag_ok_text"))
        self.btn_tag_ok.setToolTip(self.getl("frm_tags_btn_tag_ok_tt"))

        self.btn_tag_cancel.setText(self.getl("frm_tags_btn_tag_cancel_text"))
        self.btn_tag_cancel.setToolTip(self.getl("frm_tags_btn_tag_cancel_tt"))

        self.chk_tag.setText(self.getl("block_view_chk_tag_text"))
        self.chk_tag.setToolTip(self.getl("block_view_chk_tag_tt"))

    def _define_tags_apperance(self):
        self.frm_tags.setFrameShape(self.getv("frm_tags_frame_frame_shape"))  # Value 1
        self.frm_tags.setFrameShadow(self.getv("frm_tags_frame_frame_shadow"))  # Value 32
        self.frm_tags.setLineWidth(self.getv("frm_tags_frame_line_width"))
        self.frm_tags.setStyleSheet(self.getv("frm_tags_frame_stylesheet"))
        self.frm_tags.setVisible(False)
        self.frm_tags.move(220, 125)

        self.lst_tag_tags.setStyleSheet(self.getv("frm_tags_lst_tag_stylesheet"))
        self.chk_tag.setStyleSheet(self.getv("block_view_chk_tag_stylesheet"))

        self.lbl_tag_title.setStyleSheet(self.getv("frm_tags_lbl_tag_title_stylesheet"))
        self.lbl_tag_tags.setStyleSheet(self.getv("frm_tags_lbl_tag_tags_stylesheet"))

        self.btn_tag_invert.setStyleSheet(self.getv("frm_tags_btn_tag_invert_stylesheet"))
        self.btn_tag_close.setStyleSheet(self.getv("frm_tags_btn_tag_close_stylesheet"))
        self.btn_tag_reset.setStyleSheet(self.getv("frm_tags_btn_tag_reset_stylesheet"))
        self.btn_tag_ok.setStyleSheet(self.getv("frm_tags_btn_tag_ok_stylesheet"))
        self.btn_tag_cancel.setStyleSheet(self.getv("frm_tags_btn_tag_cancel_stylesheet"))

    class DiaryViewScrollArea(QScrollArea):
        def __init__(self, parent_widget, *args, **kwargs):
            super().__init__(parent_widget, *args, **kwargs)

            self.show()

