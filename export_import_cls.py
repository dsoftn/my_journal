from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QWidget, QListWidget, QDialog, QLabel,
                             QListWidgetItem, QProgressBar, QTabWidget, QAbstractItemView)
from PyQt5.QtGui import (QIcon, QPixmap, QClipboard, QColor, QCloseEvent, QMouseEvent,
                         QTextCursor, QDropEvent)
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5 import uic, QtGui, QtCore

from typing import Union
import os

import settings_cls
import utility_cls
import db_media_cls
import db_record_cls
import db_record_data_cls
import db_definition_cls
import db_tag_cls
import UTILS
import qwidgets_util_cls
from compare_cls import Compare
import obj_tags
import obj_files
import obj_images
import obj_blocks
import obj_definitions


class ListItem(QFrame):
    PAD_X = 5
    PAD_Y = 5
    SPACER_X = 5
    SPACER_Y = 5

    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget, data: dict):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget)

        # Define variables
        self.parent_widget = parent_widget
        self.data = data
        self.is_enabled: bool = self.data.get("enabled", True)
        self.widget_handler: qwidgets_util_cls.WidgetHandler = self.data["widget_handler"]

        self._create_item()
        self.update_appearance()

        # Connect events with slots
        self.lbl_enabled.mousePressEvent = self.lbl_enabled_mouse_press

    def get_id(self) -> int:
        return self.data["id"]

    def get_name(self) -> str:
        return self.data["name"]

    def get_src(self) -> str:
        return self.data["src"]
    
    def get_text(self) -> str:
        return self.data["text"]
    
    def set_enabled(self, value: bool) -> None:
        self.data["enabled"] = value
        self.is_enabled = value

        self.update_appearance()

    def lbl_enabled_mouse_press(self, e: QMouseEvent) -> None:
        if not e.button() == Qt.LeftButton:
            return
        
        lbl_enabled_widget: qwidgets_util_cls.Widget_PushButton = self.widget_handler.find_child(self.lbl_enabled)
        lbl_enabled_widget.EVENT_mouse_press_event(e)
        
        self.set_enabled(not self.is_enabled)
        self.update_appearance()
        self.data["update_function"]()

    def update_appearance(self):
        if self.is_enabled:
            frame_stylesheet = self.getv("export_import_list_item_enabled_frame_stylesheet")
            lbl_enabled_stylesheet = self.getv("export_import_list_item_enabled_lbl_enabled_stylesheet")
            lbl_enabled_icon_path = self.getv("checked_icon_path")
            lbl_id_stylesheet = self.getv("export_import_list_item_enabled_lbl_id_stylesheet")
            lbl_name_stylesheet = self.getv("export_import_list_item_enabled_lbl_name_stylesheet")
            lbl_src_stylesheet = self.getv("export_import_list_item_enabled_lbl_src_stylesheet")
            lbl_text_stylesheet = self.getv("export_import_list_item_enabled_lbl_text_stylesheet")
        else:
            frame_stylesheet = self.getv("export_import_list_item_disabled_frame_stylesheet")
            lbl_enabled_stylesheet = self.getv("export_import_list_item_disabled_lbl_enabled_stylesheet")
            lbl_enabled_icon_path = self.getv("not_checked_icon_path")
            lbl_id_stylesheet = self.getv("export_import_list_item_disabled_lbl_id_stylesheet")
            lbl_name_stylesheet = self.getv("export_import_list_item_disabled_lbl_name_stylesheet")
            lbl_src_stylesheet = self.getv("export_import_list_item_disabled_lbl_src_stylesheet")
            lbl_text_stylesheet = self.getv("export_import_list_item_disabled_lbl_text_stylesheet")
        
        self.setStyleSheet(frame_stylesheet)
        self.lbl_enabled.setStyleSheet(lbl_enabled_stylesheet)
        self.lbl_enabled.setPixmap(QPixmap(lbl_enabled_icon_path))
        self.lbl_enabled.setScaledContents(True)
        self.lbl_id.setStyleSheet(lbl_id_stylesheet)
        self.lbl_name.setStyleSheet(lbl_name_stylesheet)
        self.lbl_src.setStyleSheet(lbl_src_stylesheet)
        self.lbl_text.setStyleSheet(lbl_text_stylesheet)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self) -> None:
        self.widget_handler.remove_child(self.lbl_enabled)
        self.deleteLater()

    def resize_me(self, new_width: int) -> None:
        w = new_width
        top_h = 25

        lbl_name_w = w - self.lbl_name.pos().x() - 10
        if lbl_name_w < 0:
            lbl_name_w = 0
        self.lbl_name.resize(lbl_name_w, top_h)
        self.lbl_src.resize(w - 20, 17)
        self.lbl_text.resize(w - 20, 68)

        self.setFixedSize(w, self.height())

    def _create_item(self) -> None:
        w = self.data["width"]
        top_h = 25
        
        # Frame
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.Box)

        # Check label
        self.lbl_enabled = QLabel(self)
        self.lbl_enabled.move(self.PAD_X, self.PAD_Y)
        self.lbl_enabled.resize(top_h, top_h)
        self.lbl_enabled.setCursor(Qt.PointingHandCursor)
        lbl_enabled_widget = self.widget_handler.add_QPushButton(self.lbl_enabled)
        lbl_enabled_widget.properties.allow_bypass_mouse_press_event = False

        # ID Label
        self.lbl_id = QLabel(self)
        self.lbl_id.move(self.lbl_enabled.pos().x() + self.lbl_enabled.width() + self.SPACER_X, self.PAD_Y)
        id_value = self.data["id"].split(":")[0]
        self.lbl_id.setText(f'ID: {id_value}')
        self.lbl_id.setStyleSheet(self.getv("export_import_list_item_enabled_lbl_id_stylesheet"))
        self.lbl_id.adjustSize()
        self.lbl_id.resize(self.lbl_id.width(), top_h)

        # Name Label
        self.lbl_name = QLabel(self)
        self.lbl_name.move(self.lbl_id.pos().x() + self.lbl_id.width() + self.SPACER_X, self.PAD_Y)
        self.lbl_name.setText(self.data["name"])
        self.lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name_w = w - self.lbl_name.pos().x() - 10
        if lbl_name_w < 0:
            lbl_name_w = 0
        self.lbl_name.resize(lbl_name_w, top_h)
        
        y = top_h + self.SPACER_Y
        # Source Label
        self.lbl_src = QLabel(self)
        self.lbl_src.setAlignment(Qt.AlignCenter)
        self.lbl_src.move(self.PAD_X, y)
        self.lbl_src.setText(f'{self.getl("export_import_list_item_source_text")}: {self.data["src"]}')
        self.lbl_src.resize(w - 20, 17)

        y += 17 + self.SPACER_Y
        # Text Label
        self.lbl_text = QLabel(self)
        self.lbl_text.move(self.PAD_X, y)
        self.lbl_text.setText(self.data["text"])
        self.lbl_text.resize(w - 20, 68)
        self.lbl_text.setWordWrap(True)

        # Resize Frame
        y += self.lbl_text.height() + self.PAD_Y
        self.setFixedSize(w, y)


class ExportImport(QDialog):
    EXPORT_BLOCKS_INDEX = 0
    IMPORT_BLOCKS_INDEX = 1
    EXPORT_DEFINITIONS_INDEX = 2
    IMPORT_DEFINITIONS_INDEX = 3
    SCROLL_BY_PIXEL = 7

    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget, action: str = "export_blocks"):
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget)

        # Define other variables
        self._parent_widget = parent_widget
        self._os_clip: QClipboard = self.get_appv("clipboard")
        self._app_clip: utility_cls.Clipboard = self.get_appv("cb")
        self.abort_action = False
        self.last_export_folder = ""
        self.last_import_folder = ""

        self.export_blocks_id_list = []
        self.import_blocks_id_list = []
        self.export_definitions_id_list = []
        self.import_definitions_id_list = []

        # Load GUI
        uic.loadUi(self.getv("export_import_ui_file_path"), self)

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_appearance()

        self._load_win_position()

        self.load_widgets_handler()

        if action == "export_blocks":
            self.tab_action.setCurrentIndex(self.EXPORT_BLOCKS_INDEX)
        elif action == "import_blocks":
            self.tab_action.setCurrentIndex(self.IMPORT_BLOCKS_INDEX)
        elif action == "export_defs":
            self.tab_action.setCurrentIndex(self.EXPORT_DEFINITIONS_INDEX)
            self.populate_export_blocks_list()
        elif action == "import_defs":
            self.tab_action.setCurrentIndex(self.IMPORT_DEFINITIONS_INDEX)

        self.populate_list()
        self.update_widgets_appearance()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)
        self._os_clip.dataChanged.connect(self._clipboard_changed)
        
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_exec.clicked.connect(self.btn_exec_click)
        
        self.btn_export_block_paste.clicked.connect(self.btn_export_block_paste_click)
        self.btn_export_block_clear.clicked.connect(self.btn_export_block_clear_click)
        self.btn_export_def_paste.clicked.connect(self.btn_export_def_paste_click)
        self.btn_export_def_clear.clicked.connect(self.btn_export_def_clear_click)

        self.btn_import_block_clear.clicked.connect(self.btn_import_block_clear_click)
        self.btn_import_def_clear.clicked.connect(self.btn_import_def_clear_click)
        self.btn_import_block_add_file.clicked.connect(self.btn_import_block_add_file_click)
        self.btn_import_def_add_file.clicked.connect(self.btn_import_def_add_file_click)

        self.tab_action.currentChanged.connect(self.tab_action_current_changed)
        self.btn_working_abort.clicked.connect(self.btn_working_abort_click)

        self.btn_execute_abort.clicked.connect(self.btn_execute_abort_click)
        self.btn_execute_details.clicked.connect(self.btn_execute_details_click)
        self.btn_execute_cancel.clicked.connect(self.btn_execute_cancel_click)
        self.btn_execute_actions.clicked.connect(self.btn_execute_actions_click)
        self.btn_execute_confirm.clicked.connect(self.btn_execute_confirm_click)
        self.btn_execute_done.clicked.connect(self.btn_execute_done_click)

        self.lst_export_block.dropEvent = self._on_drop_event
        self.lst_export_block.dragEnterEvent = self.lst_export_block_drag_enter
        self.lst_export_block.dragLeaveEvent = self.lst_export_block_drag_leave
        self.lst_export_def.dropEvent = self._on_drop_event
        self.lst_export_def.dragEnterEvent = self.lst_export_def_drag_enter
        self.lst_export_def.dragLeaveEvent = self.lst_export_def_drag_leave


        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["ImportExport"])

    def lst_export_block_drag_enter(self, e):
        self.raise_()
        self.lst_export_block.setStyleSheet(self.lst_export_block.styleSheet() + "QListWidget {border: 3px solid #ffff00}")
        self.lbl_drop_block.setVisible(True)
        self.lbl_drop_block.move(self.btn_export_block_paste.pos().x() + self.btn_export_block_paste.width() + 10, self.btn_export_block_paste.pos().y())
        self.lbl_drop_block.resize(self.btn_export_block_paste.size())
        e.accept()

    def lst_export_block_drag_leave(self, e):
        self.lst_export_block.setStyleSheet(self.getv("export_import_lst_export_block_stylesheet"))
        self.lbl_drop_block.setVisible(False)
        e.accept()

    def lst_export_def_drag_enter(self, e):
        self.raise_()
        self.lst_export_def.setStyleSheet(self.lst_export_block.styleSheet() + "QListWidget {border: 3px solid #ffff00}")
        self.lbl_drop_def.setVisible(True)
        self.lbl_drop_def.move(self.btn_export_def_paste.pos().x() + self.btn_export_def_paste.width() + 10, self.btn_export_def_paste.pos().y())
        self.lbl_drop_def.resize(self.btn_export_def_paste.size())
        e.accept()

    def lst_export_def_drag_leave(self, e):
        self.lst_export_def.setStyleSheet(self.getv("export_import_lst_export_def_stylesheet"))
        self.lbl_drop_def.setVisible(False)
        e.accept()

    def _on_drop_event(self, e: QDropEvent):
        self.lbl_drop_block.setVisible(False)
        self.lbl_drop_def.setVisible(False)
        self.lst_export_block.setStyleSheet(self.getv("export_import_lst_export_block_stylesheet"))
        self.lst_export_def.setStyleSheet(self.getv("export_import_lst_export_def_stylesheet"))

        data = self.get_appv("cb").get_drag_data()

        UTILS.LogHandler.add_log_record("#1: Drag&Drop data : #2 function triggered.", ["ExportImport", "_on_drop_event"])

        if data is None:
            UTILS.LogHandler.add_log_record("#1: Drag&Drop data : No data in #2 clipboard.", ["ExportImport", "drag"])
        else:
            UTILS.LogHandler.add_log_record("#1: Drag&Drop data : Received data = #2.", ["ExportImport", data])
            self.send_to(data.get("data"), data.get("type"))
        
        e.ignore()

    def btn_execute_done_click(self):
        self.btn_execute_done.setVisible(False)
        self.frm_execute.setVisible(False)

    def btn_execute_confirm_click(self):
        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Started executing #2 actions.", ["ExportImport", "block export"])
            result = self._execute_confirm_export()
            if result:
                self.get_appv("main_win").events({"name": "export_import", "action": "block_exported", "title": self.getl("export_import_main_win_msg_block_exported_title"), "text": self.getl("export_import_main_win_msg_block_exported_text"), "icon": self.getv("export_icon_path")})
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Started executing #2 actions.", ["ExportImport", "block import"])
            result = self._execute_confirm_import()
            if result:
                self.get_appv("main_win").events({"name": "export_import", "action": "block_exported", "title": self.getl("export_import_main_win_msg_block_imported_title"), "text": self.getl("export_import_main_win_msg_block_imported_text"), "icon": self.getv("import_icon_path")})
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Started executing #2 actions.", ["ExportImport", "definition export"])
            result = self._execute_confirm_export()
            if result:
                self.get_appv("main_win").events({"name": "export_import", "action": "block_exported", "title": self.getl("export_import_main_win_msg_def_exported_title"), "text": self.getl("export_import_main_win_msg_def_exported_text"), "icon": self.getv("export_icon_path")})
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Started executing #2 actions.", ["ExportImport", "definition import"])
            result = self._execute_confirm_import()
            if result:
                self.get_appv("main_win").events({"name": "export_import", "action": "block_exported", "title": self.getl("export_import_main_win_msg_def_imported_title"), "text": self.getl("export_import_main_win_msg_def_imported_text"), "icon": self.getv("import_icon_path")})

        self.abort_action = False

    def _execute_confirm_export(self) -> bool:
        # Get filename
        file_path = self._ask_for_export_file_name()
        if not file_path:
            return None
        
        append_to_archive = None
        if UTILS.FileUtility.FILE_is_exist(file_path):
            compare_archive = Compare(self._stt, self, {"action": "append", "old": file_path})
            compare_result = compare_archive.show_me()
            if compare_result is None:
                return None
            elif compare_result is False:
                UTILS.FileUtility.FILE_delete(file_path)
            elif compare_result is True:
                append_to_archive = self.getv("temp_folder_path") + "append_arch.zip"
                info_text = self.lbl_execute_info.text()
                self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_copy_archive"))
                QCoreApplication.processEvents()
                UTILS.FileUtility.FILE_copy(file_path, append_to_archive)
                UTILS.FileUtility.FILE_delete(file_path)
                self.lbl_execute_info.setText(info_text)

        # Disable buttons
        self.btn_execute_confirm.setDisabled(True)
        self.btn_execute_cancel.setDisabled(True)
        self.btn_execute_details.setDisabled(True)
        self.btn_execute_actions.setDisabled(True)
        
        # Process actions
        result = self._process_export_action_list(file_path, self.getl("export_import_lbl_execute_info_process_actions"))

        if append_to_archive and result:
            self.merge_archives(file_path, append_to_archive, file_path)
            UTILS.FileUtility.FILE_delete(append_to_archive)

        # Enable buttons
        if result:
            UTILS.LogHandler.add_log_record("#1: Processing actions completed successfully.", ["ExportImport"])
            self.btn_execute_done.setVisible(True)
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_done_success"))
        else:
            UTILS.LogHandler.add_log_record("#1: Processing actions failed.", ["ExportImport"])
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_incorrect_stylesheet"))
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_done_fail"))
            self.btn_execute_cancel.setDisabled(False)

            file_to_delete = self.getv("temp_folder_path") + "tmp_export_data.json"
            if UTILS.FileUtility.FILE_is_exist(file_to_delete):
                UTILS.FileUtility.FILE_delete(file_to_delete)

            file_to_delete = file_path
            if UTILS.FileUtility.FILE_is_exist(file_to_delete):
                UTILS.FileUtility.FILE_delete(file_to_delete)

        self.btn_execute_details.setDisabled(False)
        self.btn_execute_actions.setDisabled(False)
        self.btn_execute_details_click()
        return result

    def merge_archives(self, new_archive: str, old_archive: str, result_archive: str) -> bool:
        if not result_archive:
            result_archive = new_archive

        info_text = self.lbl_execute_info.text()
        self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_merge_archives"))
        QCoreApplication.processEvents()

        extract_new_path = self.getv("temp_folder_path") + "merge/new/"
        extract_old_path = self.getv("temp_folder_path") + "merge/old/"

        # Clear folders
        if UTILS.FileUtility.FOLDER_is_exist(extract_new_path):
            UTILS.FileUtility.FOLDER_delete_all_files(extract_new_path)
        else:
            UTILS.FileUtility.FOLDER_create(extract_new_path)
        
        if UTILS.FileUtility.FOLDER_is_exist(extract_old_path):
            UTILS.FileUtility.FOLDER_delete_all_files(extract_old_path)
        else:
            UTILS.FileUtility.FOLDER_create(extract_old_path)

        # Extract both archive
        UTILS.FileUtility.ZIP_extract_all_files_from_archive(new_archive, extract_new_path)
        UTILS.FileUtility.ZIP_extract_all_files_from_archive(old_archive, extract_old_path)

        data_file_name = "tmp_export_data.json"

        self.lbl_execute_info.setText(info_text)

        # Load data from archives
        if data_file_name in UTILS.FileUtility.FOLDER_list_files(extract_new_path, return_base_name_only=True):
            new_data = UTILS.FileUtility.JSON_load(extract_new_path + data_file_name)
        else:
            UTILS.LogHandler.add_log_record("#1: Unable to find #2 file in archive.\nArchive: #3\nMerge operation in function #4 is aborted.", ["ExportImport", "tmp_export_data.json", new_archive, "merge_archives"], warning_raised=True)
            return False
        
        if data_file_name in UTILS.FileUtility.FOLDER_list_files(extract_old_path, return_base_name_only=True):
            old_data = UTILS.FileUtility.JSON_load(extract_old_path + data_file_name)
        else:
            UTILS.LogHandler.add_log_record("#1: Unable to find #2 file in archive.\nArchive: #3\nMerge operation in function #4 is aborted.", ["ExportImport", "tmp_export_data.json", old_archive, "merge_archives"], warning_raised=True)
            return False
        
        # Update tags
        if new_data.get("tags") is None:
            new_data["tags"] = []
        new_items = [x["id"] for x in new_data.get("tags", [])]
        for item in old_data.get("tags", []):
            if item["id"] not in new_items:
                new_data["tags"].append(item)
                new_items.append(item["id"])
        # Update images
        if new_data.get("images") is None:
            new_data["images"] = []
        new_items = [x["id"] for x in new_data.get("images", [])]
        for item in old_data.get("images", []):
            if item["id"] not in new_items:
                new_data["images"].append(item)
                new_items.append(item["id"])
        # Update files
        if new_data.get("files") is None:
            new_data["files"] = []
        new_items = [x["id"] for x in new_data.get("files", [])]
        for item in old_data.get("files", []):
            if item["id"] not in new_items:
                new_data["files"].append(item)
                new_items.append(item["id"])
        # Update blocks
        if new_data.get("blocks") is None:
            new_data["blocks"] = []
        new_items = [x["id"] for x in new_data.get("blocks", [])]
        failed_blocks = 0
        for item in old_data.get("blocks", []):
            if item["id"] not in new_items:
                new_data["blocks"].append(item)
                new_items.append(item["id"])
            else:
                failed_blocks += 1
        # Update definitions
        if new_data.get("definitions") is None:
            new_data["definitions"] = []
        new_items = [x["id"] for x in new_data.get("definitions", [])]
        failed_defs = 0
        for item in old_data.get("definitions", []):
            if item["id"] not in new_items:
                new_data["definitions"].append(item)
                new_items.append(item["id"])
            else:
                failed_defs += 1

        # Save data
        UTILS.FileUtility.FILE_delete(extract_new_path + data_file_name)

        UTILS.FileUtility.JSON_dump(extract_new_path + data_file_name, new_data)
        
        for file in UTILS.FileUtility.FOLDER_list_files(extract_old_path, return_base_name_only=True):
            if file not in UTILS.FileUtility.FOLDER_list_files(extract_new_path, return_base_name_only=True):
                UTILS.FileUtility.FILE_copy(extract_old_path + file, extract_new_path + file)

        if UTILS.FileUtility.FILE_is_exist(result_archive):
            UTILS.FileUtility.FILE_delete(result_archive)
        
        UTILS.FileUtility.ZIP_create_new_archive(result_archive)

        for file in UTILS.FileUtility.FOLDER_list_files(extract_new_path):
            UTILS.FileUtility.ZIP_add_file_to_archive(result_archive, file)
        
        # UTILS.FileUtility.FOLDER_delete_all_files(extract_new_path)
        # UTILS.FileUtility.FOLDER_delete_all_files(extract_old_path)

        UTILS.LogHandler.add_log_record("#1: Merge operation completed successfully.\nNew Archive: #2\nOld Archive: #3\nResult archive: #4", ["ExportImport", new_archive, old_archive, result_archive])

        if failed_blocks or failed_defs:
            self._msg_failed_blocks_and_defs(failed_blocks, failed_defs)

        return True

    def _msg_failed_blocks_and_defs(self, blocks: int, defs: int):
        text = ""
        if blocks:
            text += self.getl("export_import_msg_failed_blocks").replace("#1", str(blocks))
        
        if defs:
            if text:
                text += "\n"
            text += self.getl("export_import_msg_failed_defs").replace("#1", str(defs))

        msg_dict = {
            "title": self.getl("export_import_failed_title"),
            "text": text
        }

        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_dict, app_modal=True)

    def _execute_confirm_import(self) -> bool:
        # Disable buttons
        self.btn_execute_confirm.setDisabled(True)
        self.btn_execute_cancel.setDisabled(True)
        self.btn_execute_details.setDisabled(True)
        self.btn_execute_actions.setDisabled(True)
        
        # Process actions
        result = self._process_import_action_list(self.getl("export_import_lbl_execute_info_process_actions"))

        # Enable buttons
        if result:
            UTILS.LogHandler.add_log_record("#1: Processing actions completed successfully.", ["ExportImport"])
            self.btn_execute_done.setVisible(True)
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_done_success"))
        else:
            UTILS.LogHandler.add_log_record("#1: Processing actions failed.", ["ExportImport"])
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_incorrect_stylesheet"))
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_done_fail"))
            self.btn_execute_cancel.setDisabled(False)

        self.btn_execute_details.setDisabled(False)
        self.btn_execute_actions.setDisabled(False)
        self.btn_execute_details_click()
        return result

    def _process_import_action_list(self, info_text: str) -> bool:
        # Switch to action list
        self.btn_execute_actions_click()

        # Set title
        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_exporting_blocks"))
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_importing_blocks"))
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_exporting_defs"))
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_importing_defs"))
        self.txt_execute.clear()
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_import_started"), font_size=16, fg_color="#ffff00", start_new_line=False)

        unpacked_archive_name = None
        archive_content_path = None
        self.prg_import_export.setVisible(True)
        imported_objects = {
            "blocks": [],
            "definitions": []
        }
        # Process actions
        for index in range(self.lst_execute.count()):
            self.update_progress(index + 1, self.lst_execute.count(), prg_widget=self.prg_import_export)
            item: QListWidgetItem = self.lst_execute.item(index)
            data: dict = item.data(Qt.UserRole)

            item.setForeground(QColor("#000000"))
            item.setBackground(QColor("#ffff00"))
            font = item.font()
            font.setBold(True)
            font_size = font.pointSize()
            font.setPointSize(font_size + 4)
            item.setFont(font)
            item.setText(f"-> {item.text()}")

            self.lst_execute.scrollToItem(item)

            self.lbl_execute_info.setText(f"{info_text}\n{index + 1} / {self.lst_execute.count()}")

            QCoreApplication.processEvents()

            # Unpack archive
            if data["archive_path"] != unpacked_archive_name:
                unpacked_archive_name = data["archive_path"]
                archive_content_path = self._unpack_archive(data["archive_path"])
            
            # Block
            if data["object"] == "block":
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_importing_block"), font_size=12, fg_color="#aaff00")
                self._frm_execute_write_detail(str(data["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                result = self._add_imported_block(data)
                if not result:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=16, fg_color="#ff0000")
                    return False
                imported_objects["blocks"].append(UTILS.TextUtility.get_integer(result))
                self._frm_execute_write_detail(self.getl("export_import_btn_execute_done_text"), font_size=12, fg_color="#aaff7f", start_new_line=False)
            # Definition
            elif data["object"] == "definition":
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_importing_def"), font_size=12, fg_color="#aaff00")
                self._frm_execute_write_detail(str(data["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                result = self._add_imported_def(data)
                if not result:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=16, fg_color="#ff0000")
                    return False
                imported_objects["definitions"].append(UTILS.TextUtility.get_integer(result))
                self._frm_execute_write_detail(self.getl("export_import_btn_execute_done_text"), font_size=12, fg_color="#aaff7f", start_new_line=False)
            # Tag
            elif data["object"] == "tag":
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_importing_tag"), font_size=12, fg_color="#aaff00")
                self._frm_execute_write_detail(str(data["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                result = self._add_imported_tag(data)
                if not result:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=16, fg_color="#ff0000")
                    return False
                self._frm_execute_write_detail(self.getl("export_import_btn_execute_done_text"), font_size=12, fg_color="#aaff7f", start_new_line=False)
            # Image
            elif data["object"] == "image":
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_importing_image"), font_size=12, fg_color="#aaff00")
                self._frm_execute_write_detail(str(data["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                result = self._add_imported_image(data, archive_content_path)
                if not result:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=16, fg_color="#ff0000")
                    return False
                self._frm_execute_write_detail(self.getl("export_import_btn_execute_done_text"), font_size=12, fg_color="#aaff7f", start_new_line=False)
            # File
            elif data["object"] == "file":
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_importing_file"), font_size=12, fg_color="#aaff00")
                self._frm_execute_write_detail(str(data["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                result = self._add_imported_file(data, archive_content_path)
                if not result:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=16, fg_color="#ff0000")
                    return False
                self._frm_execute_write_detail(self.getl("export_import_btn_execute_done_text"), font_size=12, fg_color="#aaff7f", start_new_line=False)
            else:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_unknown_object"), font_size=12, fg_color="#ff85ff")
                self._frm_execute_write_detail(str(data["object"]), font_size=12, fg_color="#00ffff", start_new_line=False)
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
                return False

            item.setForeground(QColor("#818181"))
            item.setBackground(QColor("#2b2b2b"))
            font = item.font()
            font.setBold(False)
            font.setPointSize(font_size)
            item.setFont(font)
            item.setText(item.text()[3:])

        self.prg_import_export.setVisible(False)
        # Clean tmp folder
        tmp_folder_path = self.getv("temp_folder_path")
        archive_folder = tmp_folder_path + "import/"

        # Clear archive folder
        if UTILS.FileUtility.FOLDER_is_exist(archive_folder):
            UTILS.FileUtility.FOLDER_delete_all_files(archive_folder)
        if UTILS.FileUtility.FILE_is_exist(archive_folder):
            UTILS.FileUtility.FILE_delete(archive_folder)

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_archive_success_import"), font_size=16, fg_color="#00ff00")

        self._update_shared_objects()

        if imported_objects["blocks"]:
            events_dict = {
                "name": "start_dialog",
                "action": "BlockView",
                "ids": imported_objects["blocks"]
            }
            self.get_appv("main_win").events(events_dict)
        elif imported_objects["definitions"]:
            events_dict = {
                "name": "start_dialog",
                "action": "BrowseDefinitions",
                "ids": imported_objects["definitions"]
            }
            self.get_appv("main_win").events(events_dict)
        
        return True

    def _update_shared_objects(self):
        """
        Updates Tags, Files, Images, Blocks, Definitions, AutoComplete and TextHandler
        """

        # Show frame
        self.frm_updating.move(int(self.width() / 2 - self.frm_updating.width() / 2), int(self.height() / 2 - self.frm_updating.height() / 2))
        content = ""
        content += self.getl("splash_loading_tags") + "...> " + "\n"
        content += self.getl("splash_loading_images") + "...> " + "\n"
        content += self.getl("splash_loading_files") + "...> " + "\n"
        content += self.getl("splash_loading_blocks") + "...> " + "\n"
        content += self.getl("splash_loading_defs") + "...> " + "\n"
        content += self.getl("splash_loading_ac_data") + "...> " + "\n"
        content += self.getl("splash_loading_text_handler_data") + "...> "
        self.lbl_updating_content.setText(content)

        self.frm_updating.setVisible(True)

        content = self._refresh_updating_frame_content(content)

        # Tags
        obj: obj_tags.Tags = self.get_appv("tags")
        obj.refresh()
        content = self._refresh_updating_frame_content(content)

        # Images
        obj: obj_images.Images = self.get_appv("images")
        obj.refresh()
        content = self._refresh_updating_frame_content(content)

        # Files
        obj: obj_files.Files = self.get_appv("files")
        obj.refresh()
        content = self._refresh_updating_frame_content(content)

        # Blocks
        obj: obj_blocks.Blocks = self.get_appv("blocks")
        obj.refresh()
        content = self._refresh_updating_frame_content(content)

        # Definitions
        obj: obj_definitions.Definitions = self.get_appv("defs")
        obj.refresh()
        content = self._refresh_updating_frame_content(content)

        # AutoComplete
        self.get_appv("ac_data").complete_diary = self.get_appv("ac_data").calculate_data()
        content = self._refresh_updating_frame_content(content)

        # TextHandler
        self.get_appv("text_handler_data")._def_list = self.get_appv("text_handler_data").calculate_data()
        content = self._refresh_updating_frame_content(content)

        self.frm_updating.setVisible(False)

    def _refresh_updating_frame_content(self, text: str) -> str:
        if text.find(">>>") != -1:
            start = text.find(">>>")
            end = text.find("\n", start)
            if end == -1:
                end = len(text)

            text = text[:start] + "...#1" + text[end:]

        if text.find("...>") != -1:
            start = text.find("...>")
            end = text.find("\n", start)
            if end == -1:
                end = len(text)

            text = text[:start] + ">>>#2" + text[end:]
        
        new_content = text

        html_to_text = UTILS.HTMLText.TextToHTML(text)
        rule_done = UTILS.HTMLText.TextToHtmlRule(
            text="#1",
            replace_with=self.getl("export_import_execute_msg_done"),
            fg_color="#00aa00",
            font_italic=True
        )
        rule_working = UTILS.HTMLText.TextToHtmlRule(
            text="#2",
            replace_with=self.getl("working"),
            fg_color="#900000"
        )
        html_to_text.add_rule(rule_done)
        html_to_text.add_rule(rule_working)
        self.lbl_updating_content.setText(html_to_text.get_html())

        self.lbl_updating_content.repaint()

        return new_content

    def _add_imported_def(self, data: dict) -> int | None:
        db_def = db_definition_cls.Definition(self._stt)

        # Find images
        images_to_add = []
        for image in [x["id"] for x in data["data"]["images"]]:
            for index in range(self.lst_execute.count()):
                item = self.lst_execute.item(index)
                widget_data = item.data(Qt.UserRole)
                if widget_data["object"] == "image" and widget_data["id"] == image:
                    images_to_add.append(widget_data["new_id"])
                    break

        default_media_id = None
        for image in [x["id"] for x in data["data"]["images"]]:
            for index in range(self.lst_execute.count()):
                item = self.lst_execute.item(index)
                widget_data = item.data(Qt.UserRole)
                if widget_data["object"] == "image" and widget_data["id"] == data["data"]["default"]:
                    default_media_id = widget_data["new_id"]
                    break

        def_dict = {
            "name": data["data"]["name"],
            "description": data["data"]["description"],
            "media_ids": images_to_add,
            "synonyms": data["data"]["synonyms"],
            "show": 1
        }
        if default_media_id is not None:
            def_dict["default"] = default_media_id

        if data["new_id"] == 0:
            result = db_def.add_new_definition(def_dict=def_dict)
            return result
        
        db_def.load_definition(data["new_id"])
        extra_images_to_add = db_def.definition_media_ids
        for image in images_to_add:
            if image not in extra_images_to_add:
                extra_images_to_add.append(image)

        
        def_dict = {
            "media_ids": extra_images_to_add,
            "synonyms": data["data"]["synonyms"]
        }
        db_def.update_definition(data["new_id"], def_dict)
        
        return data["new_id"]

    def _add_imported_block(self, data: dict) -> int | None:
        db_rec = db_record_cls.Record(self._stt)
        closed_block = False

        if data["new_id"] == 0:
            last_row_id = db_rec.add_new_record(
                body=data["data"]["body"],
                body_html=data["data"]["body_html"],
                date=data["data"]["date"],
                name=data["data"]["name"]
            )
        else:
            closed_block = self.get_appv("main_win").events({"name": "close_block", "id": data["id"]})
            last_row_id = data["new_id"]
            if not db_rec.is_valid_record_id(last_row_id):
                UTILS.LogHandler.add_log_record("#1: Exception in function #2. Block ID=#3 not found, cannot update blocks.", ["ExportImport", "_add_imported_block", last_row_id], exception_raised=True)
                return None
            
            db_rec.load_record(last_row_id)
            db_rec.RecordDate = data["data"]["date"]
            db_rec.RecordName = data["data"]["name"]
            db_rec.RecordBody = data["data"]["body"]
            db_rec.RecordBodyHTML = data["data"]["body_html"]
            db_rec.RecordDraft = 1

            db_rec.save_record()

        # Find tags
        tags_to_add = []
        for tag in [x["id"] for x in data["data"]["tags"]]:
            for index in range(self.lst_execute.count()):
                item = self.lst_execute.item(index)
                widget_data = item.data(Qt.UserRole)
                if widget_data["object"] == "tag" and widget_data["id"] == tag:
                    tags_to_add.append(widget_data["new_id"])
                    break

        # Find images
        images_to_add = []
        for image in [x["id"] for x in data["data"]["images"]]:
            for index in range(self.lst_execute.count()):
                item = self.lst_execute.item(index)
                widget_data = item.data(Qt.UserRole)
                if widget_data["object"] == "image" and widget_data["id"] == image:
                    images_to_add.append(widget_data["new_id"])
                    break

        # Find files
        files_to_add = []
        for file in [x["id"] for x in data["data"]["files"]]:
            for index in range(self.lst_execute.count()):
                item = self.lst_execute.item(index)
                widget_data = item.data(Qt.UserRole)
                if widget_data["object"] == "file" and widget_data["id"] == file:
                    files_to_add.append(widget_data["new_id"])
                    break

        # Add data
        db_rec_data = db_record_data_cls.RecordData(self._stt)
        rec_data_dict = {
            "tag": tags_to_add,
            "media": images_to_add,
            "files": files_to_add
        }

        db_rec_data.update_record_data(
            data_dict=rec_data_dict,
            record_id=last_row_id
        )

        if closed_block:
            self.get_appv("main_win").events({"name": "open_block", "id": data["id"]})

        return last_row_id

    def _add_imported_file(self, data: dict, archive_content_path: str) -> bool:
        if data["new_id"] != 0:
            return True
        
        # Find unpacked image path
        unpacked_image_path = UTILS.FileUtility.join_folder_and_file_name(archive_content_path, os.path.basename(data["data"]["file"]))
        if not UTILS.FileUtility.FILE_is_exist(unpacked_image_path):
            return False
        unpacked_image_obj = UTILS.FileUtility.get_FileInformation_object(unpacked_image_path)
        
        # Create new image
        file_dict = {
            "name": data["data"]["name"],
            "description": data["data"]["description"],
            "http": data["data"]["http"]
        }
        db_file = db_media_cls.Files(self._stt)
        last_row_id = db_file.add_file(file_dict, add_if_not_exist=False)
        data["new_id"] = last_row_id

        user_set = self.get_appv("user").settings_path
        file_name, _ = os.path.split(user_set)
        if file_name:
            file_name = file_name + "/"
        file_name = file_name + str(self.get_appv("user").ActiveUserID)
        file_name = file_name + "files/"

        fixed_filename = unpacked_image_obj.get_base_filename()
        if fixed_filename.rfind(".") != -1:
            fixed_filename = fixed_filename[:fixed_filename.rfind(".")]
        if fixed_filename.find("_") != -1:
            fixed_filename = fixed_filename[fixed_filename.find("_") + 1:]
        if fixed_filename:
            fixed_filename = "_" + fixed_filename

        file_name = file_name + str(last_row_id) + fixed_filename + "."
        file_name += unpacked_image_obj.extension()

        if UTILS.FileUtility.FILE_is_exist(file_name):
            if db_file.is_safe_to_delete(last_row_id):
                db_file.delete_file(last_row_id)
            return False

        UTILS.FileUtility.FILE_copy(unpacked_image_obj, file_name)

        file_dict = {
            "file": file_name
        }
        db_file.update_file(last_row_id, file_dict=file_dict)

        data["new_id"] = last_row_id
        self._update_list_data("file", data["data"]["id"], last_row_id)
        return True

    def _add_imported_image(self, data: dict, archive_content_path: str) -> bool:
        if data["new_id"] != 0:
            return True
        
        # Find unpacked image path
        unpacked_image_path = UTILS.FileUtility.join_folder_and_file_name(archive_content_path, os.path.basename(data["data"]["file"]))
        if not UTILS.FileUtility.FILE_is_exist(unpacked_image_path):
            return False
        unpacked_image_obj = UTILS.FileUtility.get_FileInformation_object(unpacked_image_path)
        
        # Create new image
        image_dict = {
            "name": data["data"]["name"],
            "description": data["data"]["description"],
            "http": data["data"]["http"]
        }
        db_image = db_media_cls.Media(self._stt)
        last_row_id = db_image.add_media(image_dict, add_if_not_exist=False)
        data["new_id"] = last_row_id

        user_set = self.get_appv("user").settings_path
        file_name, _ = os.path.split(user_set)
        if file_name:
            file_name = file_name + "/"
        file_name = file_name + str(self.get_appv("user").ActiveUserID)
        file_name = file_name + "images/"

        file_name = file_name + str(last_row_id) + "."
        file_name += unpacked_image_obj.extension()

        if UTILS.FileUtility.FILE_is_exist(file_name):
            if db_image.is_safe_to_delete(last_row_id):
                db_image.delete_media(last_row_id)
            return False

        UTILS.FileUtility.FILE_copy(unpacked_image_obj, file_name)

        image_dict = {
            "file": file_name
        }
        db_image.update_media(last_row_id, media_dict=image_dict)

        data["new_id"] = last_row_id

        self._update_list_data("image", data["data"]["id"], last_row_id)

        return True

    def _add_imported_tag(self, data: dict) -> bool:
        if data["new_id"] != 0:
            return True
        
        # Create new tag
        tag_dict = {
            "name": data["data"]["name"],
            "description": data["data"]["description"]
        }
        db_tag = db_tag_cls.Tag(self._stt)
        result = db_tag.add_new_tag(tag_dict)
        data["new_id"] = result
        self._update_list_data("tag", data["data"]["id"], result)
        return True

    def _update_list_data(self, object_name: str, data_id: int, new_id: int):
        for index in range(self.lst_execute.count()):
            item = self.lst_execute.item(index)
            widget_data = item.data(Qt.UserRole)
            if widget_data["object"] == object_name and widget_data["data"]["id"] == data_id:
                widget_data["new_id"] = new_id
                item.setData(Qt.UserRole, widget_data)
                break

    def _unpack_archive(self, archive_path: str) -> str:
        # Define Archive folder
        tmp_folder_path = self.getv("temp_folder_path")
        archive_folder = tmp_folder_path + "import/"

        info_text = self.lbl_execute_info.text()
        self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_unpacking_archive"))

        # Clear archive folder
        if UTILS.FileUtility.FOLDER_is_exist(archive_folder):
            UTILS.FileUtility.FOLDER_delete_all_files(archive_folder)
        else:
            UTILS.FileUtility.FOLDER_create(archive_folder)

        if UTILS.FileUtility.FILE_is_exist(archive_folder):
            UTILS.FileUtility.FILE_delete(archive_folder)
        
        UTILS.FileUtility.ZIP_extract_all_files_from_archive(archive_path, archive_folder)

        self.lbl_execute_info.setText(info_text)

        return archive_folder

    def _process_export_action_list(self, file_name: str, info_text: str) -> bool:
        # Switch to action list
        self.btn_execute_actions_click()

        # Set title
        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_exporting_blocks"))
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_importing_blocks"))
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_exporting_defs"))
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_importing_defs"))
        self.txt_execute.clear()
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_create_archive"), font_size=16, fg_color="#ffff00", start_new_line=False)
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_name"), font_size=12, fg_color="#b1ff87")

        data_final = {}

        # Define Temp Folder
        tmp_folder_path = self.getv("temp_folder_path")
        if not UTILS.FileUtility.FOLDER_is_exist(tmp_folder_path):
            UTILS.FileUtility.FOLDER_create(tmp_folder_path)
        
        # Define temp data file, file will be added to archive later
        tmp_data_file_path = "tmp_export_data.json"
        tmp_data_file_path = UTILS.FileUtility.join_folder_and_file_name(tmp_folder_path, tmp_data_file_path)

        if UTILS.FileUtility.FILE_is_exist(tmp_data_file_path):
            UTILS.FileUtility.FILE_delete(tmp_data_file_path)

        # Define Archive file
        archive_file_path = file_name
        if UTILS.FileUtility.FILE_is_exist(archive_file_path):
            UTILS.FileUtility.FILE_delete(archive_file_path)
        result = UTILS.FileUtility.ZIP_create_new_archive(archive_file_path)
        if not result:
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_archive_not_created"), font_size=12, fg_color="#ffffff")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
            return False

        self._frm_execute_write_detail(archive_file_path, font_size=12, fg_color="#00ffff", start_new_line=False)

        self.prg_import_export.setVisible(True)
        # Process actions
        for index in range(self.lst_execute.count()):
            self.update_progress(index + 1, self.lst_execute.count(), prg_widget=self.prg_import_export)
            item: QListWidgetItem = self.lst_execute.item(index)
            data: dict = item.data(Qt.UserRole)

            item.setForeground(QColor("#000000"))
            item.setBackground(QColor("#ffff00"))
            font = item.font()
            font.setBold(True)
            font_size = font.pointSize()
            font.setPointSize(font_size + 4)
            item.setFont(font)
            item.setText(f"-> {item.text()}")

            self.lst_execute.scrollToItem(item)

            self.lbl_execute_info.setText(f"{info_text}\n{index + 1} / {self.lst_execute.count()}")

            QCoreApplication.processEvents()

            # Block
            if data["object"] == "block":
                if data_final.get("blocks") is None:
                    data_final["blocks"] = []
                
                if data["data"]["id"] in [x["id"] for x in data_final["blocks"]]:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_duplicate_block1"), font_size=12, fg_color="#ffffff")
                    self._frm_execute_write_detail(str(data["data"]["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_duplicate_block2"), font_size=12, fg_color="#ffffff", start_new_line=False)
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
                    if UTILS.FileUtility.FILE_is_exist(archive_file_path):
                        UTILS.FileUtility.FILE_delete(archive_file_path)
                    return False

                data_final["blocks"].append(data["data"])
            # Definition
            elif data["object"] == "definition":
                if data_final.get("definitions") is None:
                    data_final["definitions"] = []
                
                if data["data"]["id"] in [x["id"] for x in data_final["definitions"]]:
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_duplicate_def1"), font_size=12, fg_color="#ffffff")
                    self._frm_execute_write_detail(str(data["data"]["id"]), font_size=12, fg_color="#aaffff", start_new_line=False)
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_duplicate_def2"), font_size=12, fg_color="#ffffff", start_new_line=False)
                    self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
                    if UTILS.FileUtility.FILE_is_exist(archive_file_path):
                        UTILS.FileUtility.FILE_delete(archive_file_path)
                    return False

                data_final["definitions"].append(data["data"])
            # Tag
            elif data["object"] == "tag":
                if data_final.get("tags") is None:
                    data_final["tags"] = []
                
                if data["data"]["id"] not in [x["id"] for x in data_final["tags"]]:
                    data_final["tags"].append(data["data"])
            # Image
            elif data["object"] == "image":
                if data_final.get("images") is None:
                    data_final["images"] = []
                
                if data["data"]["id"] not in [x["id"] for x in data_final["images"]]:
                    image_file_path = data["data"]["file"]
                    if not UTILS.FileUtility.FILE_is_exist(image_file_path):
                        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
                        self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_image_not_found"), font_size=12, fg_color="#ffffff")
                        self._frm_execute_write_detail(f'ID={data["data"]["id"]}', font_size=12, fg_color="#00ffff", start_new_line=False)
                        self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
                        return False

                    data["data"]["archive_filename"] = UTILS.FileUtility.get_FileInformation_object(image_file_path).get_base_filename()
                    data_final["images"].append(data["data"])
                    UTILS.FileUtility.ZIP_add_file_to_archive(archive_file_path, image_file_path)
            # File
            elif data["object"] == "file":
                if data_final.get("files") is None:
                    data_final["files"] = []
                
                if data["data"]["id"] not in [x["id"] for x in data_final["files"]]:
                    file_file_path = data["data"]["file"]
                    if not UTILS.FileUtility.FILE_is_exist(file_file_path):
                        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
                        self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_file_not_found"), font_size=12, fg_color="#ffffff")
                        self._frm_execute_write_detail(f'ID={data["data"]["id"]}', font_size=12, fg_color="#00ffff", start_new_line=False)
                        self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
                        return False

                    data["data"]["archive_filename"] = UTILS.FileUtility.get_FileInformation_object(file_file_path).get_base_filename()
                    data_final["images"].append(data["data"])
                    UTILS.FileUtility.ZIP_add_file_to_archive(archive_file_path, file_file_path)
            else:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_unknown_object"), font_size=12, fg_color="#ff85ff")
                self._frm_execute_write_detail(str(data["object"]), font_size=12, fg_color="#00ffff", start_new_line=False)
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
                return False

            item.setForeground(QColor("#818181"))
            item.setBackground(QColor("#2b2b2b"))
            font = item.font()
            font.setBold(False)
            font.setPointSize(font_size)
            item.setFont(font)
            item.setText(item.text()[3:])

        self.prg_import_export.setVisible(False)
        # Add data json to archive
        result = UTILS.FileUtility.JSON_dump(tmp_data_file_path, data_final)
        if not result:
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_json_write"), font_size=12, fg_color="#ffffff")
            self._frm_execute_write_detail("JSON: ", font_size=12, fg_color="#ffffff")
            self._frm_execute_write_detail(tmp_data_file_path, font_size=12, fg_color="#00ffff", start_new_line=False)
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
            return False

        result = UTILS.FileUtility.ZIP_add_file_to_archive(archive_file_path, tmp_data_file_path)
        if not result:
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_archive_error"), font_size=12, fg_color="#ff0000")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_error_json_write"), font_size=12, fg_color="#ffffff")
            self._frm_execute_write_detail("JSON: ", font_size=12, fg_color="#ffffff")
            self._frm_execute_write_detail(tmp_data_file_path, font_size=12, fg_color="#00ffff", start_new_line=False)
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_operation_aborted"), font_size=14, fg_color="#aa0000")
            return False
        
        UTILS.FileUtility.FILE_delete(tmp_data_file_path)

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_archive_success"), font_size=16, fg_color="#00ff00")

        return True

    def _ask_for_export_file_name(self) -> str | None:
        today = UTILS.DateTime.DateTimeObject(UTILS.DateTime.DateTime.today())
        recommended_filename = today.DATE_formatted_string.strip(" .").replace(".", "_").replace(" ", "") + ".zip"
        if self.last_export_folder:
            last_file_name = UTILS.FileUtility.get_FileInformation_object(self.last_export_folder)
            recommended_filename = last_file_name.get_dir_name() + recommended_filename

        filename = UTILS.FileUtility.show_save_file_PyQt5(
            parent_widget=self,
            title=self.getl("export_import_save_archive_dialog_title"),
            default_filename=recommended_filename,
            filters="ZIP Archive (*.zip);;All Files (*.*)"
        )
        if filename:
            if not filename.lower().endswith(".zip"):
                filename = filename + ".zip"
            self.last_export_folder = filename
            return filename
        return None

    def btn_execute_cancel_click(self):
        self.frm_execute.setVisible(False)

    def btn_execute_details_click(self):
        self.txt_execute.setVisible(True)
        self.lst_execute.setVisible(False)

        self.btn_execute_details.setEnabled(False)
        self.btn_execute_actions.setEnabled(True)

        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_details_export_blocks_text"))
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_details_import_blocks_text"))
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_details_export_defs_text"))
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_details_import_defs_text"))

    def btn_execute_actions_click(self):
        self.txt_execute.setVisible(False)
        self.lst_execute.setVisible(True)

        self.btn_execute_details.setEnabled(True)
        self.btn_execute_actions.setEnabled(False)

        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_actions_export_blocks_text"))
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_actions_import_blocks_text"))
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_actions_export_defs_text"))
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            self.lbl_execute_title.setText(self.getl("export_import_lbl_execute_title_actions_import_defs_text"))

    def btn_execute_abort_click(self):
        self.abort_action = True

    def btn_exec_click(self):
        self.btn_execute_done.setVisible(False)
        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Block export - creating actions started.", ["ExportImport"])
            self._export_blocks()
            UTILS.LogHandler.add_log_record("#1: Block export - creating actions completed.", ["ExportImport"])
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Block import - creating actions started.", ["ExportImport"])
            compare = Compare(self._stt, self, {}, reset_compare_info_data_only=True)
            compare.close_me(save_geometry=False)
            self._import_blocks()
            UTILS.LogHandler.add_log_record("#1: Block import - creating actions completed.", ["ExportImport"])
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Definitions export - creating actions started.", ["ExportImport"])
            self._export_definitions()
            UTILS.LogHandler.add_log_record("#1: Definitions export - creating actions completed.", ["ExportImport"])
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Definitions import - creating actions started.", ["ExportImport"])
            compare = Compare(self._stt, self, {}, reset_compare_info_data_only=True)
            compare.close_me(save_geometry=False)
            self._import_definitions()
            UTILS.LogHandler.add_log_record("#1: Definitions import - creating actions completed.", ["ExportImport"])

    def _import_blocks(self):
        self.abort_action = False
        # Setup Execute Frame
        self.btn_execute_details_click()
        self.btn_execute_confirm.setText(self.getl("export_import_btn_execute_confirm_import_blocks_text"))
        self.txt_execute.clear()
        self.lst_execute.clear()
        self.btn_execute_abort.setVisible(True)
        self.btn_execute_confirm.setEnabled(False)
        self.btn_execute_cancel.setEnabled(False)
        self.btn_execute_details.setEnabled(False)
        self.btn_execute_actions.setEnabled(False)
        
        self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_collecting_data_text"))
        self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))

        # Show frame
        self.frm_execute.setVisible(True)
        QCoreApplication.processEvents()

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data"), font_size=20, fg_color="#00ffff")

        self.prg_import_export.setVisible(True)

        # Collect data
        for index in range(self.lst_import_block.count()):
            self.update_progress(index, self.lst_import_block.count(), prg_widget=self.prg_import_export)

            self._frm_execute_write_detail(" ")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_block"), font_size=16, fg_color="#ffffff")
            self._frm_execute_write_detail("  ID: ", font_size=16, fg_color="#ffff00", start_new_line=False)
            item_widget: ListItem = self.lst_import_block.itemWidget(self.lst_import_block.item(index))

            data: dict = dict(item_widget.data)
            data["id"] = data["id"].split(":")[0]

            self._frm_execute_write_detail(str(data.get("id")), font_size=16, fg_color="#00ffff", start_new_line=False)

            if not item_widget.is_enabled:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_item_disabled"), font_size=12, fg_color="#aa55ff")
                continue

            # Block name for Compare
            refer_object_name = data["block"]["date"]
            if data["block"]["name"]:
                refer_object_name += f' - {data["block"]["name"]}'
            if data["block"]["body"]:
                refer_object_name += " - " + UTILS.TextUtility.shrink_text(data["block"]["body"], 100, ratio_start_end=(100, 0), replace_chars_map=[("\n", ";")])

            self._frm_execute_import_block_write_tags(data["block"]["tags"], refers_to_id=data["id"], refers_to_object="block", refer_object_name=refer_object_name, archive_path=data["src"])
            if self.abort_action:
                break
            self._frm_execute_import_write_images(data["block"]["images"], refers_to_id=data["id"], refers_to_object="block", refer_object_name=refer_object_name, archive_path=data["src"])
            if self.abort_action:
                break
            self._frm_execute_import_write_files(data["block"]["files"], refers_to_id=data["id"], refers_to_object="block", refer_object_name=refer_object_name, archive_path=data["src"])
            if self.abort_action:
                break
            self._frm_execute_import_block_write_metadata(data["block"], refers_to_id=None, refers_to_object=None, archive_path=data["src"])

            self._frm_execute_write_detail(self.getl("export_import_execute_msg_done"), font_size=16, fg_color="#55ff00")

            QCoreApplication.processEvents()

            if self.abort_action:
                break

        self.prg_import_export.setVisible(False)

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data_done"), font_size=20, fg_color="#00ffff")
            
        # Setup Execute Frame
        self.btn_execute_actions_click()
        self.btn_execute_cancel.setEnabled(True)
        self.btn_execute_abort.setVisible(False)
        self.btn_execute_details.setEnabled(True)
        self.btn_execute_actions.setEnabled(True)
        if self.abort_action:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_user_aborted"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_incorrect_stylesheet"))
        else:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_data_collected"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
            self.txt_execute.setVisible(False)
            self.lst_execute.setVisible(True)
            self.btn_execute_confirm.setEnabled(True)
        
        self.abort_action = False
        
    def _export_definitions(self):
        self.abort_action = False
        # Setup Execute Frame
        self.btn_execute_details_click()
        self.btn_execute_confirm.setText(self.getl("export_import_btn_execute_confirm_export_blocks_text"))
        self.txt_execute.clear()
        self.lst_execute.clear()
        self.btn_execute_abort.setVisible(True)
        self.btn_execute_confirm.setEnabled(False)
        self.btn_execute_cancel.setEnabled(False)
        self.btn_execute_details.setEnabled(False)
        self.btn_execute_actions.setEnabled(False)
        
        self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_collecting_data_text"))
        self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))

        # Show frame
        self.frm_execute.setVisible(True)
        QCoreApplication.processEvents()

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data"), font_size=20, fg_color="#00ffff")

        self.prg_import_export.setVisible(True)
        # Collect data
        for index in range(self.lst_export_def.count()):
            self.update_progress(index, self.lst_export_def.count(), prg_widget=self.prg_import_export)

            self._frm_execute_write_detail(" ")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_def"), font_size=16, fg_color="#ffffff")
            self._frm_execute_write_detail("  ID: ", font_size=16, fg_color="#ffff00", start_new_line=False)
            item_widget: ListItem = self.lst_export_def.itemWidget(self.lst_export_def.item(index))

            data: dict = item_widget.data

            self._frm_execute_write_detail(str(data.get("id")), font_size=16, fg_color="#00ffff", start_new_line=False)

            if not item_widget.is_enabled:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_item_disabled"), font_size=12, fg_color="#aa55ff")
                continue

            self._frm_execute_export_write_images(data["definition"]["images"], refers_to_id=data["id"], refers_to_object="definition")
            self._frm_execute_export_def_write_metadata(data["definition"], refers_to_id=None, refers_to_object=None)

            self._frm_execute_write_detail(self.getl("export_import_execute_msg_done"), font_size=16, fg_color="#55ff00")

            QCoreApplication.processEvents()

            if self.abort_action:
                break

        self.prg_import_export.setVisible(False)

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data_done"), font_size=20, fg_color="#00ffff")
            
        # Setup Execute Frame
        self.btn_execute_actions_click()
        self.btn_execute_cancel.setEnabled(True)
        self.btn_execute_abort.setVisible(False)
        self.btn_execute_details.setEnabled(True)
        self.btn_execute_actions.setEnabled(True)
        if self.abort_action:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_user_aborted"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_incorrect_stylesheet"))
        else:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_data_collected"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
            self.txt_execute.setVisible(False)
            self.lst_execute.setVisible(True)
            self.btn_execute_confirm.setEnabled(True)

        self.abort_action = False

    def _import_definitions(self):
        self.abort_action = False
        # Setup Execute Frame
        self.btn_execute_details_click()
        self.btn_execute_confirm.setText(self.getl("export_import_btn_execute_confirm_import_blocks_text"))
        self.txt_execute.clear()
        self.lst_execute.clear()
        self.btn_execute_abort.setVisible(True)
        self.btn_execute_confirm.setEnabled(False)
        self.btn_execute_cancel.setEnabled(False)
        self.btn_execute_details.setEnabled(False)
        self.btn_execute_actions.setEnabled(False)
        
        self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_collecting_data_text"))
        self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))

        # Show frame
        self.frm_execute.setVisible(True)
        QCoreApplication.processEvents()

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data"), font_size=20, fg_color="#00ffff")

        self.prg_import_export.setVisible(True)

        # Collect data
        for index in range(self.lst_import_def.count()):
            self.update_progress(index, self.lst_import_def.count(), prg_widget=self.prg_import_export)

            self._frm_execute_write_detail(" ")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_def"), font_size=16, fg_color="#ffffff")
            self._frm_execute_write_detail("  ID: ", font_size=16, fg_color="#ffff00", start_new_line=False)
            item_widget: ListItem = self.lst_import_def.itemWidget(self.lst_import_def.item(index))

            data: dict = dict(item_widget.data)
            data["id"] = data["id"].split(":")[0]

            self._frm_execute_write_detail(str(data.get("id")), font_size=16, fg_color="#00ffff", start_new_line=False)

            if not item_widget.is_enabled:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_item_disabled"), font_size=12, fg_color="#aa55ff")
                continue

            # Definition name for Compare
            refer_object_name = data["definition"]["name"]

            self._frm_execute_import_write_images(data["definition"]["images"], refers_to_id=data["id"], refers_to_object="definition", refer_object_name=refer_object_name, archive_path=data["src"])
            if self.abort_action:
                break
            self._frm_execute_import_def_write_metadata(data["definition"], refers_to_id=None, refers_to_object=None, archive_path=data["src"])

            self._frm_execute_write_detail(self.getl("export_import_execute_msg_done"), font_size=16, fg_color="#55ff00")

            QCoreApplication.processEvents()

            if self.abort_action:
                break

        self.prg_import_export.setVisible(False)

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data_done"), font_size=20, fg_color="#00ffff")
            
        # Setup Execute Frame
        self.btn_execute_actions_click()
        self.btn_execute_cancel.setEnabled(True)
        self.btn_execute_abort.setVisible(False)
        self.btn_execute_details.setEnabled(True)
        self.btn_execute_actions.setEnabled(True)
        if self.abort_action:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_user_aborted"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_incorrect_stylesheet"))
        else:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_data_collected"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
            self.txt_execute.setVisible(False)
            self.lst_execute.setVisible(True)
            self.btn_execute_confirm.setEnabled(True)

        self.abort_action = False

    def _export_blocks(self):
        self.abort_action = False
        # Setup Execute Frame
        self.btn_execute_details_click()
        self.btn_execute_confirm.setText(self.getl("export_import_btn_execute_confirm_export_blocks_text"))
        self.txt_execute.clear()
        self.lst_execute.clear()
        self.btn_execute_abort.setVisible(True)
        self.btn_execute_confirm.setEnabled(False)
        self.btn_execute_cancel.setEnabled(False)
        self.btn_execute_details.setEnabled(False)
        self.btn_execute_actions.setEnabled(False)
        
        self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_collecting_data_text"))
        self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))

        # Show frame
        self.frm_execute.setVisible(True)
        QCoreApplication.processEvents()

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data"), font_size=20, fg_color="#00ffff")

        self.prg_import_export.setVisible(True)
        # Collect data
        for index in range(self.lst_export_block.count()):
            self.update_progress(index, self.lst_export_block.count(), prg_widget=self.prg_import_export)

            self._frm_execute_write_detail(" ")
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_block"), font_size=16, fg_color="#ffffff")
            self._frm_execute_write_detail("  ID: ", font_size=16, fg_color="#ffff00", start_new_line=False)
            item_widget: ListItem = self.lst_export_block.itemWidget(self.lst_export_block.item(index))

            data: dict = item_widget.data

            self._frm_execute_write_detail(str(data.get("id")), font_size=16, fg_color="#00ffff", start_new_line=False)

            if not item_widget.is_enabled:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_item_disabled"), font_size=12, fg_color="#aa55ff")
                continue

            self._frm_execute_export_block_write_tags(data["block"]["tags"], refers_to_id=data["id"], refers_to_object="block")
            self._frm_execute_export_write_images(data["block"]["images"], refers_to_id=data["id"], refers_to_object="block")
            self._frm_execute_export_write_files(data["block"]["files"], refers_to_id=data["id"], refers_to_object="block")
            self._frm_execute_export_block_write_metadata(data["block"], refers_to_id=None, refers_to_object=None)

            self._frm_execute_write_detail(self.getl("export_import_execute_msg_done"), font_size=16, fg_color="#55ff00")

            QCoreApplication.processEvents()

            if self.abort_action:
                break

        self.prg_import_export.setVisible(False)

        self._frm_execute_write_detail(self.getl("export_import_execute_msg_processing_data_done"), font_size=20, fg_color="#00ffff")
            
        # Setup Execute Frame
        self.btn_execute_actions_click()
        self.btn_execute_cancel.setEnabled(True)
        self.btn_execute_abort.setVisible(False)
        self.btn_execute_details.setEnabled(True)
        self.btn_execute_actions.setEnabled(True)
        if self.abort_action:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_user_aborted"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_incorrect_stylesheet"))
        else:
            self.lbl_execute_info.setText(self.getl("export_import_lbl_execute_info_data_collected"))
            self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
            self.txt_execute.setVisible(False)
            self.lst_execute.setVisible(True)
            self.btn_execute_confirm.setEnabled(True)
        
        self.abort_action = False

    def _frm_execute_import_block_write_tags(self, tag_data_list: list, refers_to_id: int, refers_to_object: str, refer_object_name: str, archive_path: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_tags"), font_size=12, fg_color="#aaffff")
        
        db_tag_object = db_tag_cls.Tag(self._stt)
        db_tag_list = db_tag_object.get_all_tags()
        
        for item in tag_data_list:
            # Write init details message
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_tag"), font_size=12, fg_color="#ffff7f")
            self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
            self._frm_execute_write_detail(str(item["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_object), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_id), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)


            # Set data
            action_data = {
                "id": item["id"],
                "object": "tag",
                "archive_path": archive_path,
                "enabled": True,
                "refer_id": refers_to_id,
                "refer_object": refers_to_object,
                "refer_object_name": refer_object_name,
                "data": item
            }
            
            # Check if tag exist
            new_id = 0
            process_success = False
            for db_tag in db_tag_list:
                if db_tag[1] == action_data["data"]["name"]:
                    if db_tag[3] == action_data["data"]["description"]:
                        new_id = db_tag[0]
                        process_success = True
                        break
                    else:
                        compare_data = {
                            "action": "tag",
                            "refer_id": action_data["refer_id"],
                            "refer_object": action_data["refer_object"],
                            "refer_object_name": refer_object_name,
                            "new": {
                                "id": action_data["data"]["id"],
                                "name": action_data["data"]["name"],
                                "description": action_data["data"]["description"]
                            },
                            "old": {
                                "id": db_tag[0],
                                "name": db_tag[1],
                                "description": db_tag[3]
                            }
                        }
                        compare_tags = Compare(self._stt, self, compare_data)
                        q_result = compare_tags.show_me()
                        compare_tags = None

                        if q_result is None:
                            process_success = False
                        else:
                            new_id = q_result
                            process_success = True
                        break
            else:
                process_success = True
            
            if not process_success:
                self.abort_action = True
                break

            action_data["new_id"] = new_id

            # Write detail message

            if new_id == 0:
                msg = self.getl("export_import_execute_msg_use_new_tag")
                self._frm_execute_write_detail(msg, fg_color="#ffaa00")
            else:
                msg = self.getl("export_import_execute_msg_use_old_tag")
                self._frm_execute_write_detail(msg, fg_color="#ffaa00")
            
            # ID
            msg = self.getl("export_import_execute_msg_define_tag_id")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["id"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Name
            msg = self.getl("export_import_execute_msg_define_tag_name")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["name"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Description
            msg = self.getl("export_import_execute_msg_define_tag_description")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Write action
            msg = self.getl("export_import_execute_msg_define_tag_import_action").replace("#1", str(action_data["data"]["id"]))
            self._frm_execute_write_action(msg, action_data)

            QCoreApplication.processEvents()

    def _frm_execute_export_block_write_tags(self, tag_data_list: list, refers_to_id: int, refers_to_object: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_tags"), font_size=12, fg_color="#aaffff")
        
        for item in tag_data_list:
            # Write init details message
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_tag"), font_size=12, fg_color="#ffff7f")
            self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
            self._frm_execute_write_detail(str(item["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_object), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_id), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)


            # Set data
            action_data = {
                "id": item["id"],
                "object": "tag",
                "refer_id": refers_to_id,
                "refer_object": refers_to_object,
                "data": item
            }
            
            # Write detail message

            # ID
            msg = self.getl("export_import_execute_msg_define_tag_id")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["id"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Name
            msg = self.getl("export_import_execute_msg_define_tag_name")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["name"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Description
            msg = self.getl("export_import_execute_msg_define_tag_description")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Write action
            msg = self.getl("export_import_execute_msg_define_tag_export_action").replace("#1", str(action_data["data"]["id"]))
            self._frm_execute_write_action(msg, action_data)

            QCoreApplication.processEvents()

    def _frm_execute_import_write_images(self, image_data_list: list, refers_to_id: int, refers_to_object: str, refer_object_name: str, archive_path: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_images"), font_size=12, fg_color="#aaffff")

        db_image = db_media_cls.Media(self._stt)
        images_db_list = db_image.get_all_media()
        images_list_with_sizes = []
        for i in images_db_list:
            image_db_item = list(i)
            image_db_item.append(UTILS.FileUtility.FILE_get_size(i[3]))
            images_list_with_sizes.append(image_db_item)

        # IMAGES
        for item in image_data_list:
            # Write init details message
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_image"), font_size=12, fg_color="#ffff7f")
            self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
            self._frm_execute_write_detail(str(item["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_object), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_id), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

            # Set data
            action_data = {
                "id": item["id"],
                "object": "image",
                "archive_path": archive_path,
                "refer_id": refers_to_id,
                "refer_object": refers_to_object,
                "data": item
            }

            # Check image
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_image"), font_size=12, fg_color="#5fbe8d")
            new_id = self._check_image(action_data, archive_path, images_list_with_sizes=images_list_with_sizes, refer_object_name=refer_object_name)
            if new_id:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_image_old"), font_size=12, fg_color="#5dbe65", start_new_line=False)
            else:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_image_new"), font_size=12, fg_color="#5dbe65", start_new_line=False)
            
            if new_id is None:
                self.abort_action = True
                break
            
            action_data["new_id"] = new_id

            # Write detail message
            if new_id == 0:
                msg = self.getl("export_import_execute_msg_use_new_image")
                self._frm_execute_write_detail(msg, fg_color="#ffaa00")
            else:
                msg = self.getl("export_import_execute_msg_use_old_image")
                self._frm_execute_write_detail(msg, fg_color="#ffaa00")

            # ID
            msg = self.getl("export_import_execute_msg_define_image_id")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["id"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Name
            msg = self.getl("export_import_execute_msg_define_image_name")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["name"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Description
            msg = self.getl("export_import_execute_msg_define_image_description")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Source (http)
            msg = self.getl("export_import_execute_msg_define_image_source")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["http"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # File location
            msg = self.getl("export_import_execute_msg_define_image_file")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["file"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Write action
            msg = self.getl("export_import_execute_msg_define_image_import_action").replace("#1", str(action_data["data"]["id"]))
            self._frm_execute_write_action(msg, action_data)

            QCoreApplication.processEvents()
            if self.abort_action:
                break

    def _check_image(self, data: dict, archive_path: str, images_list_with_sizes: list = None, refer_object_name: str = "???"):
        archive_filename = os.path.basename(data["data"]["file"])
        temp_folder = self.getv("temp_folder_path")
        tmp_image = temp_folder + archive_filename

        if UTILS.FileUtility.FILE_is_exist(tmp_image):
            UTILS.FileUtility.FILE_delete(tmp_image)
        
        UTILS.FileUtility.ZIP_extract_file_from_archive(archive_path, archive_filename, temp_folder)

        temp_file_hash = UTILS.FileUtility.FILE_get_hash(tmp_image)
        temp_file_size = UTILS.FileUtility.get_FileInformation_object(tmp_image).size()

        if images_list_with_sizes is None:
            db_image = db_media_cls.Media(self._stt)
            images = db_image.get_all_media()
        else:
            images = images_list_with_sizes

        found_image = None
        self.prg_find_match.setVisible(True)
        for index, image in enumerate(images):
            if images_list_with_sizes is None:
                self.update_progress(index + 1, len(images), prg_widget=self.prg_find_match)
                c_image_obj = UTILS.FileUtility.get_FileInformation_object(image[3])
                c_image_obj_size = c_image_obj.size()
            else:
                c_image_obj_size = image[-1]
            
            if temp_file_size == c_image_obj_size:
                result = UTILS.FileUtility.FILE_is_files_content_equal(temp_file_hash, image[3])
            else:
                result = False
            if result:
                found_image = image
                break
        
        self.prg_find_match.setVisible(False)

        if found_image is None:
            UTILS.FileUtility.FILE_delete(tmp_image)
            return 0

        compare_data = {
            "action": "image",
            "refer_id": data["refer_id"],
            "refer_object": data["refer_object"],
            "refer_object_name": refer_object_name,
            "new": {
                "id": data["data"]["id"],
                "name": data["data"]["name"],
                "description": data["data"]["description"],
                "http": data["data"]["http"],
                "file": tmp_image
            },
            "old": {
                "id": found_image[0],
                "name": found_image[1],
                "description": found_image[2],
                "http": found_image[4],
                "file": found_image[3]
            }
        }
        compare = Compare(self._stt, self, compare_data)

        result = compare.show_me()
        UTILS.FileUtility.FILE_delete(tmp_image)

        return result

    def _frm_execute_export_write_images(self, image_data_list: list, refers_to_id: int, refers_to_object: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_images"), font_size=12, fg_color="#aaffff")

        # IMAGES
        for item in image_data_list:
            # Write init details message
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_image"), font_size=12, fg_color="#ffff7f")
            self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
            self._frm_execute_write_detail(str(item["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_object), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_id), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

            # Set data
            action_data = {
                "id": item["id"],
                "object": "image",
                "refer_id": refers_to_id,
                "refer_object": refers_to_object,
                "data": item
            }

            # Write detail message

            # ID
            msg = self.getl("export_import_execute_msg_define_image_id")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["id"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Name
            msg = self.getl("export_import_execute_msg_define_image_name")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["name"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Description
            msg = self.getl("export_import_execute_msg_define_image_description")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Source (http)
            msg = self.getl("export_import_execute_msg_define_image_source")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["http"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # File location
            msg = self.getl("export_import_execute_msg_define_image_file")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["file"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Write action
            msg = self.getl("export_import_execute_msg_define_image_export_action").replace("#1", str(action_data["data"]["id"]))
            self._frm_execute_write_action(msg, action_data)

            QCoreApplication.processEvents()
            if self.abort_action:
                break

    def _frm_execute_import_write_files(self, file_data_list: list, refers_to_id: int, refers_to_object: str, refer_object_name: str, archive_path: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_files"), font_size=12, fg_color="#aaffff")

        # FILES
        for item in file_data_list:
            # Write init details message
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_file"), font_size=12, fg_color="#ffff7f")
            self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
            self._frm_execute_write_detail(str(item["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_object), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_id), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

            # Set data
            action_data = {
                "id": item["id"],
                "object": "file",
                "archive_path": archive_path,
                "refer_id": refers_to_id,
                "refer_object": refers_to_object,
                "data": item
            }

            # Check image
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_file"), font_size=12, fg_color="#5fbe8d")
            new_id = self._check_file(action_data, archive_path, refer_object_name=refer_object_name)
            if new_id:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_image_old"), font_size=12, fg_color="#5dbe65", start_new_line=False)
            else:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_image_new"), font_size=12, fg_color="#5dbe65", start_new_line=False)
            
            if new_id is None:
                self.abort_action = True
                break
            
            action_data["new_id"] = new_id

            # Write detail message
            if new_id == 0:
                msg = self.getl("export_import_execute_msg_use_new_file")
                self._frm_execute_write_detail(msg, fg_color="#ffaa00")
            else:
                msg = self.getl("export_import_execute_msg_use_old_file")
                self._frm_execute_write_detail(msg, fg_color="#ffaa00")

            # ID
            msg = self.getl("export_import_execute_msg_define_file_id")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["id"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Name
            msg = self.getl("export_import_execute_msg_define_file_name")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["name"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Description
            msg = self.getl("export_import_execute_msg_define_file_description")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Source (http)
            msg = self.getl("export_import_execute_msg_define_file_source")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["http"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # File location
            msg = self.getl("export_import_execute_msg_define_file_file")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["file"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Write action
            msg = self.getl("export_import_execute_msg_define_file_import_action").replace("#1", str(action_data["data"]["id"]))
            self._frm_execute_write_action(msg, action_data)

            QCoreApplication.processEvents()
            if self.abort_action:
                break

    def _check_file(self, data: dict, archive_path: str, refer_object_name: str):
        archive_filename = os.path.basename(data["data"]["file"])
        temp_folder = self.getv("temp_folder_path")
        tmp_file = temp_folder + archive_filename

        if UTILS.FileUtility.FILE_is_exist(tmp_file):
            UTILS.FileUtility.FILE_delete(tmp_file)
        
        UTILS.FileUtility.ZIP_extract_file_from_archive(archive_path, archive_filename, temp_folder)

        temp_file_hash = UTILS.FileUtility.FILE_get_hash(tmp_file)

        db_file = db_media_cls.Files(self._stt)
        files = db_file.get_all_file()

        found_file = None
        self.prg_find_match.setVisible(True)
        for index, image in enumerate(files):
            self.update_progress(index + 1, len(files), prg_widget=self.prg_find_match)
            result = UTILS.FileUtility.FILE_is_files_content_equal(temp_file_hash, image[3])
            if result:
                found_file = image
                break
        
        self.prg_find_match.setVisible(False)

        if found_file is None:
            UTILS.FileUtility.FILE_delete(tmp_file)
            return 0

        compare_data = {
            "action": "file",
            "refer_id": data["refer_id"],
            "refer_object": data["refer_object"],
            "refer_object_name": refer_object_name,
            "new": {
                "id": data["data"]["id"],
                "name": data["data"]["name"],
                "description": data["data"]["description"],
                "http": data["data"]["http"],
                "file": tmp_file
            },
            "old": {
                "id": found_file[0],
                "name": found_file[1],
                "description": found_file[2],
                "http": found_file[4],
                "file": found_file[3]
            }
        }
        compare = Compare(self._stt, self, compare_data)

        result = compare.show_me()
        UTILS.FileUtility.FILE_delete(tmp_file)

        return result

    def _frm_execute_export_write_files(self, file_data_list: list, refers_to_id: int, refers_to_object: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_files"), font_size=12, fg_color="#aaffff")

        # FILES
        for item in file_data_list:
            # Write init details message
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_file"), font_size=12, fg_color="#ffff7f")
            self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
            self._frm_execute_write_detail(str(item["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_object), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
            self._frm_execute_write_detail(str(refers_to_id), font_size=12, fg_color="#55ffff", start_new_line=False)
            self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

            # Set data
            action_data = {
                "id": item["id"],
                "object": "file",
                "refer_id": refers_to_id,
                "refer_object": refers_to_object,
                "data": item
            }

            # Write detail message

            # ID
            msg = self.getl("export_import_execute_msg_define_file_id")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["id"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Name
            msg = self.getl("export_import_execute_msg_define_file_name")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["name"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Description
            msg = self.getl("export_import_execute_msg_define_file_description")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Source (http)
            msg = self.getl("export_import_execute_msg_define_file_source")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["http"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # File location
            msg = self.getl("export_import_execute_msg_define_file_file")
            self._frm_execute_write_detail(msg, fg_color="#00aaff")
            msg = action_data["data"]["file"]
            self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

            # Write action
            msg = self.getl("export_import_execute_msg_define_file_export_action").replace("#1", str(action_data["data"]["id"]))
            self._frm_execute_write_action(msg, action_data)

            QCoreApplication.processEvents()
            if self.abort_action:
                break

    def _frm_execute_import_block_write_metadata(self, block_data: dict, refers_to_id: int, refers_to_object: str, archive_path: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_metadata"), font_size=12, fg_color="#aaffff")

        # Write init details message
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_block"), font_size=12, fg_color="#ffff7f")
        self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
        self._frm_execute_write_detail(str(block_data["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_object, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_id, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

        # Set data
        action_data = {
            "id": block_data["id"],
            "new_id": 0,
            "object": "block",
            "archive_path": archive_path,
            "refer_id": refers_to_id,
            "refer_object": refers_to_object,
            "data": block_data
        }

        # Find existing block
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_block"), font_size=12, fg_color="#5fbe8d")
        new_id = self._check_block(action_data)
        if new_id:
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_block_old"), font_size=12, fg_color="#5dbe65", start_new_line=False)
        else:
            self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_block_new"), font_size=12, fg_color="#5dbe65", start_new_line=False)
        
        if new_id is None:
            self.abort_action = True
        
        action_data["new_id"] = new_id


        # Write detail message

        # ID
        msg = self.getl("export_import_execute_msg_define_block_id")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["id"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Name
        msg = self.getl("export_import_execute_msg_define_block_name")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["name"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Date
        msg = self.getl("export_import_execute_msg_define_block_date")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["date"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Body
        msg = self.getl("export_import_execute_msg_define_block_body")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["body"]), 80, replace_chars_map=[["\n", ";"]])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Body HTML
        msg = self.getl("export_import_execute_msg_define_block_body_html")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = "..."
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Draft
        msg = self.getl("export_import_execute_msg_define_block_draft")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["draft"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Tags
        msg = self.getl("export_import_execute_msg_define_block_tags")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["tags"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["tags"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Images
        msg = self.getl("export_import_execute_msg_define_block_images")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["images"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["images"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Files
        msg = self.getl("export_import_execute_msg_define_block_files")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["files"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["files"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Write action
        msg = self.getl("export_import_execute_msg_define_block_import_action").replace("#1", str(action_data["data"]["id"]))
        self._frm_execute_write_action(msg, action_data)

        QCoreApplication.processEvents()

    def _check_block(self, data: dict) -> int | None:
        db_rec = db_record_cls.Record(self._stt)
        similar_record_id = None
        for record in db_rec.get_all_records():
            if record[2] == data["data"]["date"]:
                if UTILS.TextUtility.similarity_ratio(record[4], data["data"]["body"]) > 0.7:
                    similar_record_id = record[0]
                    break
        if not similar_record_id:
            return 0
            
        db_rec.load_record(similar_record_id)
        
        compare_data = {
            "action": "block",
            "new": {
                "id": data["data"]["id"],
                "date": data["data"]["date"],
                "name": data["data"]["name"],
                "body": data["data"]["body"]
            },
            "old": {
                "id": db_rec.RecordID,
                "date": db_rec.RecordDate,
                "name": db_rec.RecordName,
                "body": db_rec.RecordBody
            }
        }
        compare = Compare(self._stt, self, compare_data)

        result = compare.show_me()

        return result

    def _frm_execute_export_block_write_metadata(self, block_data: dict, refers_to_id: int, refers_to_object: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_metadata"), font_size=12, fg_color="#aaffff")

        # Write init details message
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_block"), font_size=12, fg_color="#ffff7f")
        self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
        self._frm_execute_write_detail(str(block_data["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_object, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_id, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

        # Set data
        action_data = {
            "id": block_data["id"],
            "object": "block",
            "refer_id": refers_to_id,
            "refer_object": refers_to_object,
            "data": block_data
        }

        # Write detail message

        # ID
        msg = self.getl("export_import_execute_msg_define_block_id")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["id"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Name
        msg = self.getl("export_import_execute_msg_define_block_name")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["name"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Date
        msg = self.getl("export_import_execute_msg_define_block_date")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["date"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Body
        msg = self.getl("export_import_execute_msg_define_block_body")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["body"]), 80, replace_chars_map=[["\n", ";"]])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Body HTML
        msg = self.getl("export_import_execute_msg_define_block_body_html")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = "..."
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Draft
        msg = self.getl("export_import_execute_msg_define_block_draft")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["draft"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Tags
        msg = self.getl("export_import_execute_msg_define_block_tags")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["tags"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["tags"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Images
        msg = self.getl("export_import_execute_msg_define_block_images")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["images"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["images"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Files
        msg = self.getl("export_import_execute_msg_define_block_files")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["files"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["files"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Write action
        msg = self.getl("export_import_execute_msg_define_block_export_action").replace("#1", str(action_data["data"]["id"]))
        self._frm_execute_write_action(msg, action_data)

        QCoreApplication.processEvents()

    def _frm_execute_import_def_write_metadata(self, def_data: dict, refers_to_id: int, refers_to_object: str, archive_path: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_metadata_defs"), font_size=12, fg_color="#aaffff")

        # Write init details message
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_def"), font_size=12, fg_color="#ffff7f")
        self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
        self._frm_execute_write_detail(str(def_data["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_object, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_id, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

        # Set data
        action_data = {
            "id": def_data["id"],
            "object": "definition",
            "archive_path": archive_path,
            "refer_id": refers_to_id,
            "refer_object": refers_to_object,
            "data": def_data
        }

        # Check Definition
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_def"), font_size=12, fg_color="#5fbe8d")
        new_name, new_id = self._check_definition(action_data)
        if new_name:
            if new_name == action_data["data"]["name"] and not new_id:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_def_new_def"), font_size=12, fg_color="#5dbe65", start_new_line=False)
                action_data["new_id"] = 0
            elif new_name == action_data["data"]["name"] and new_id:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_def_update"), font_size=12, fg_color="#5dbe65", start_new_line=False)
                action_data["new_id"] = new_id
            elif new_name != action_data["data"]["name"]:
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_def_renamed"), font_size=12, fg_color="#5dbe65", start_new_line=False)
                self._frm_execute_write_detail(self.getl("export_import_execute_msg_check_def_new_name"), font_size=12, fg_color="#5fbe8d")
                self._frm_execute_write_detail(new_name, font_size=12, fg_color="#5dbe65", start_new_line=False)
                action_data["new_id"] = 0
                action_data["data"]["name"] = new_name
        
        if new_name is None:
            self.abort_action = True

        # Write detail message

        # ID
        msg = self.getl("export_import_execute_msg_define_block_id")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["id"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Name
        msg = self.getl("export_import_execute_msg_define_block_name")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["name"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Description
        msg = self.getl("export_import_execute_msg_define_def_description")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Synonyms
        msg = self.getl("export_import_execute_msg_define_def_synonyms")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["synonyms"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + UTILS.TextUtility.shrink_text(str(action_data["data"]["synonyms"]), 80, replace_chars_map=[["\n", ";"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Images
        msg = self.getl("export_import_execute_msg_define_block_images")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["images"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["images"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Write action
        msg = self.getl("export_import_execute_msg_define_def_import_action").replace("#1", str(action_data["data"]["id"]))
        self._frm_execute_write_action(msg, action_data)

        QCoreApplication.processEvents()

    def _check_definition(self, data: dict) -> tuple:
        db_def = db_definition_cls.Definition(self._stt)

        all_defs = db_def.get_list_of_all_definitions()

        old_def_name = data["data"]["name"]

        new_id = 0
        
        for def_item in all_defs:
            if old_def_name.lower() == def_item[1].lower():
                new_id = def_item[0]
                db_def.load_definition(new_id)
                break
        
        if not new_id:
            return old_def_name, 0
        
        compare_dict = {
            "action": "definition",
            "validator": [x[0] for x in db_def.get_list_of_all_expressions()],
            "old": {
                "id": db_def.definition_id,
                "name": db_def.definition_name,
                "description": db_def.definition_description,
                "synonyms": db_def.definition_synonyms,
                "images": db_def.definition_media_ids
            },
            "new": {
                "id": data["data"]["id"],
                "name": data["data"]["name"],
                "description": data["data"]["description"],
                "synonyms": data["data"]["synonyms"],
                "images": data["data"]["images"]
            }
        }
        compare = Compare(self._stt, self, compare_dict)

        result = compare.show_me()

        if result == old_def_name:
            return result, new_id
        else:
            return result, 0

    def _frm_execute_export_def_write_metadata(self, def_data: dict, refers_to_id: int, refers_to_object: str):
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_start_metadata_defs"), font_size=12, fg_color="#aaffff")

        # Write init details message
        self._frm_execute_write_detail(self.getl("export_import_execute_msg_def"), font_size=12, fg_color="#ffff7f")
        self._frm_execute_write_detail("  ID = ", font_size=12, fg_color="#ffff00", start_new_line=False)
        self._frm_execute_write_detail(str(def_data["id"]), font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail("    " + self.getl("export_import_execute_msg_refer_to"), font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_object, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(" (", font_size=12, fg_color="#ffff7f", start_new_line=False)
        self._frm_execute_write_detail(refers_to_id, font_size=12, fg_color="#55ffff", start_new_line=False)
        self._frm_execute_write_detail(")", font_size=12, fg_color="#ffff7f", start_new_line=False)

        # Set data
        action_data = {
            "id": def_data["id"],
            "object": "definition",
            "refer_id": refers_to_id,
            "refer_object": refers_to_object,
            "data": def_data
        }

        # Write detail message

        # ID
        msg = self.getl("export_import_execute_msg_define_block_id")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["id"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Name
        msg = self.getl("export_import_execute_msg_define_block_name")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = action_data["data"]["name"]
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Description
        msg = self.getl("export_import_execute_msg_define_def_description")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = UTILS.TextUtility.shrink_text(str(action_data["data"]["description"]), 80, replace_chars_map=[["\n", ";"]])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)

        # Synonyms
        msg = self.getl("export_import_execute_msg_define_def_synonyms")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["synonyms"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + UTILS.TextUtility.shrink_text(str(action_data["data"]["synonyms"]), 80, replace_chars_map=[["\n", ";"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Images
        msg = self.getl("export_import_execute_msg_define_block_images")
        self._frm_execute_write_detail(msg, fg_color="#00aaff")
        msg = len(action_data["data"]["images"])
        self._frm_execute_write_detail(msg, fg_color="#00ffff", start_new_line=False)
        msg = "  " + str([x["id"] for x in action_data["data"]["images"]])
        self._frm_execute_write_detail(msg, fg_color="#7a7a7a", start_new_line=False)

        # Write action
        msg = self.getl("export_import_execute_msg_define_def_export_action").replace("#1", str(action_data["data"]["id"]))
        self._frm_execute_write_action(msg, action_data)

        QCoreApplication.processEvents()

    def _frm_execute_write_detail(self, msg: str, start_new_line: bool = True, font_size: int = 11, fg_color: str = "#ffff00"):
        msg = str(msg)
        if start_new_line:
            msg = "\n" + msg
        
        cur = self.txt_execute.textCursor()
        cur.movePosition(QTextCursor.End)
        cf = cur.charFormat()
        cf.setFontPointSize(font_size)
        cf.setForeground(QColor(fg_color))
        cur.setCharFormat(cf)
        cur.insertText(msg)
        self.txt_execute.setTextCursor(cur)
        # self.txt_execute.ensureCursorVisible()
        QCoreApplication.processEvents()

    def _frm_execute_write_action(self, msg: str, data: dict):
        # Send message to details
        detail_msg1 = self.getl("export_import_execute_msg_adding_action") + " ("
        detail_msg2 = msg
        detail_msg3 = ")"
        detail_msg4 = " ... "
        detail_msg5 = f' {self.getl("export_import_execute_msg_done")}'
        detail_msg6 = "."
        self._frm_execute_write_detail(detail_msg1, fg_color="#6f6046")
        self._frm_execute_write_detail(detail_msg2, fg_color="#a69069", start_new_line=False)
        self._frm_execute_write_detail(detail_msg3, fg_color="#6f6046", start_new_line=False)
        self._frm_execute_write_detail(detail_msg4, fg_color="#bababa", start_new_line=False)

        # Add action to list
        item = QListWidgetItem(self.lst_execute)
        item.setText(msg)
        item.setData(Qt.UserRole, data)

        font = item.font()
        if data.get("object") in ["block", "definition"]:
            item.setForeground(QColor("#ffff00"))
            font.setBold(True)
            item.setFont(font)
        else:
            item.setForeground(QColor("#8d8dd4"))

        self.lst_execute.addItem(item)

        self._frm_execute_write_detail(detail_msg5, fg_color="#aaff00", start_new_line=False)
        self._frm_execute_write_detail(detail_msg6, fg_color="#6f6046", start_new_line=False)

    def btn_cancel_click(self):
        self.close()

    def btn_export_block_clear_click(self) -> None:
        self._clear_list(self.lst_export_block)
        self.export_blocks_id_list = []
        self.update_widgets_appearance()

    def btn_import_block_clear_click(self) -> None:
        self._clear_list(self.lst_import_block)
        self.import_blocks_id_list = []
        self.update_widgets_appearance()

    def btn_import_def_clear_click(self) -> None:
        self._clear_list(self.lst_import_def)
        self.import_definitions_id_list = []
        self.update_widgets_appearance()

    def btn_export_def_clear_click(self) -> None:
        self._clear_list(self.lst_export_def)
        self.export_definitions_id_list = []
        self.update_widgets_appearance()

    def btn_working_abort_click(self):
        self.abort_action = True

    def btn_export_block_paste_click(self):
        items_to_paste = self._app_clip.block_clip_items()

        items_added = 0
        for item in items_to_paste:
            if item not in self.export_blocks_id_list:
                self.export_blocks_id_list.append(item)
                items_added += 1

        if items_added:
            UTILS.LogHandler.add_log_record("#1: Paste blocks triggered. Items added = #2", ["ExportImport", items_added])
        
        self.populate_list()
        self.update_widgets_appearance()

    def btn_export_def_paste_click(self):
        items_to_paste = self._app_clip.def_clip_items()
        items_added = 0
        for item in items_to_paste:
            if item not in self.export_definitions_id_list:
                self.export_definitions_id_list.append(item)
                items_added += 1

        if items_added:
            UTILS.LogHandler.add_log_record("#1: Paste definitions triggered. Items added = #2", ["ExportImport", items_added])
        
        self.populate_list()
        self.update_widgets_appearance()

    def send_to(self, objects: Union[str, int, list, tuple], object_type: str) -> None:
        if objects is None or object_type not in ["block", "def", "definition"]:
            return
        
        if isinstance(objects, int):
            objects = [objects]

        if isinstance(objects, str):
            objects = [objects]

        added_objects = 0
        for obj in objects:
            if isinstance(obj, str):
                if obj.find(":") != -1:
                    obj = obj.split(":")[1]
            if not isinstance(obj, int):
                obj = UTILS.TextUtility.get_integer(obj)
                if obj is None:
                    continue
            
            obj = str(obj)
            
            if obj not in self.export_blocks_id_list and object_type == "block":
                self.export_blocks_id_list.append(obj)
                self.tab_action.setCurrentIndex(self.EXPORT_BLOCKS_INDEX)
                added_objects += 1
            if obj not in self.export_definitions_id_list and object_type in ["def", "definition"]:
                self.export_definitions_id_list.append(obj)
                self.tab_action.setCurrentIndex(self.EXPORT_DEFINITIONS_INDEX)
                added_objects += 1

        self.populate_list()
        self.update_widgets_appearance()

        UTILS.LogHandler.add_log_record("#1: Objects received successfully. Source: #2", ["ExportImport", "SendTo"])

        if not added_objects:
            return

        notif_dict = {
            "title": self.getl("export_import_send_to_msg_title"),
            "text": self.getl("export_import_send_to_msg_text").replace("#1", str(len(objects))),
            "icon": self.getv("send_to_icon_path"),
            "timer": 2500,
            "position": "bottom left"
        }
        
        if object_type == "block":
            notif_dict["text"] = self.getl("export_import_send_to_msg_block_text").replace("#1", str(len(objects)))
        elif object_type in ["def", "definition"]:
            notif_dict["text"] = self.getl("export_import_send_to_msg_def_text").replace("#1", str(len(objects)))

        utility_cls.Notification(self._stt, self, notif_dict)

    def _clipboard_changed(self) -> None:
        self.update_widgets_appearance()
    
    def tab_action_current_changed(self, index: int):
        if index == self.EXPORT_BLOCKS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Tab changed to #2.", ["ExportImport", "Block Export"])
        elif index == self.IMPORT_BLOCKS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Tab changed to #2.", ["ExportImport", "Block Import"])
        elif index == self.EXPORT_DEFINITIONS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Tab changed to #2.", ["ExportImport", "Definition Export"])
        elif index == self.IMPORT_DEFINITIONS_INDEX:
            UTILS.LogHandler.add_log_record("#1: Tab changed to #2.", ["ExportImport", "Definition Import"])
    
        self.populate_list()
        self.update_widgets_appearance()

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
        self.widget_handler.add_QPushButton(self.btn_cancel)
        self.widget_handler.add_QPushButton(self.btn_exec)
        self.widget_handler.add_QPushButton(self.btn_export_block_clear)
        self.widget_handler.add_QPushButton(self.btn_export_block_paste)
        self.widget_handler.add_QPushButton(self.btn_import_block_clear)
        self.widget_handler.add_QPushButton(self.btn_import_block_add_file)
        self.widget_handler.add_QPushButton(self.btn_export_def_clear)
        self.widget_handler.add_QPushButton(self.btn_export_def_paste)
        self.widget_handler.add_QPushButton(self.btn_import_def_clear)
        self.widget_handler.add_QPushButton(self.btn_import_def_add_file)
        
        self.widget_handler.add_QPushButton(self.btn_execute_confirm)
        self.widget_handler.find_child(self.btn_execute_confirm).properties.allow_bypass_leave_event = False
        self.widget_handler.add_QPushButton(self.btn_execute_cancel)
        self.widget_handler.add_QPushButton(self.btn_execute_details)
        self.widget_handler.add_QPushButton(self.btn_execute_actions)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # Add Item Based Widgets

        self.widget_handler.activate()

    def populate_list(self) -> None:
        self.toggle_working_screen(True)

        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            self.populate_export_blocks_list()
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            self.btn_working_abort.setVisible(False)
            self.populate_import_blocks_list()
            self.btn_working_abort.setVisible(True)
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            self.populate_export_defs_list()
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            self.btn_working_abort.setVisible(False)
            self.populate_import_defs_list()
            self.btn_working_abort.setVisible(True)

        self.abort_action = False
        self.toggle_working_screen(False)

    def toggle_working_screen(self, show_screen: bool) -> None:
        if not show_screen:
            self.frm_working.setVisible(False)
            return
        
        self.frm_working.move(0, 0)
        self.frm_working.resize(self.width(), self.height())

        y = int(self.height() / 2) - 50
        if y < 0:
            y = 0
        
        self.lbl_working_title.move(0, y)
        self.lbl_working_title.resize(self.width(), self.lbl_working_title.height())

        y += self.lbl_working_title.height() + 10

        x = int((self.width() - self.prg_working.width()) / 2)
        if x < 0:
            x = 0
        if self.width() < 300:
            self.prg_working.resize(self.width() - 10, self.prg_working.height())
        else:
            self.prg_working.resize(300, self.prg_working.height())
        self.prg_working.move(x, y)
        self.prg_working.setValue(0)

        y += self.prg_working.height() + 10
        x = int((self.width() - self.btn_working_abort.width()) / 2)
        if x < 0:
            x = 0

        self.btn_working_abort.move(x, y)

        self.frm_working.setVisible(True)
        QCoreApplication.processEvents()

    def populate_export_blocks_list(self) -> None:
        self._populate_export_list(self.lst_export_block, self.export_blocks_id_list, self._fill_block_id_data)

    def populate_import_blocks_list(self) -> None:
        self._populate_import_list(self.lst_import_block, self.import_blocks_id_list)
    
    def populate_import_defs_list(self) -> None:
        self._populate_import_list(self.lst_import_def, self.import_definitions_id_list)

    def _populate_import_list(self, list_to_populate: QListWidget, data_var: list):
        disabled_ids = self._get_all_disabled_ids(list_to_populate)
        self._clear_list(list_to_populate)

        for count, item_in_list in enumerate(data_var):
            data = item_in_list
            list_item = QListWidgetItem(list_to_populate)
            list_to_populate.addItem(list_item)

            id_item = item_in_list["id"]

            if id_item in disabled_ids:
                data["enabled"] = False
            else:
                data["enabled"] = True
            
            data["width"] = list_to_populate.width() - 20
            
            widget_item = ListItem(self._stt, list_to_populate, item_in_list)
            list_to_populate.setItemWidget(list_item, widget_item)
            list_item.setSizeHint(widget_item.size())

            self.update_progress(count, len(data_var))
        
        self._resize_list_items()

    def btn_import_block_add_file_click(self) -> None:
        archive_path = self._ask_for_archive_filename()
        if not archive_path:
            return
        
        archive_blocks = self._get_objects_from_archive(archive_path, "blocks")
        if archive_blocks is None:
            return
        
        self._import_new_objects(archive_blocks, "blocks", archive_path)

        UTILS.LogHandler.add_log_record("#1: Added blocks from archive file.\nArchive path = #2", ["ExportImport", archive_path])

        self.populate_import_blocks_list()
        self.update_widgets_appearance()

    def btn_import_def_add_file_click(self) -> None:
        archive_path = self._ask_for_archive_filename()
        if not archive_path:
            return

        archive_blocks = self._get_objects_from_archive(archive_path, "definitions")
        if archive_blocks is None:
            return
        
        self._import_new_objects(archive_blocks, "definitions", archive_path)

        UTILS.LogHandler.add_log_record("#1: Added definitions from archive file.\nArchive path = #2", ["ExportImport", archive_path])

        self.populate_import_defs_list()
        self.update_widgets_appearance()

    def _import_new_objects(self, objects: list, object_type: str, archive_path):
        if object_type == "blocks":
            list_to_use = self.lst_import_block
            ids_list = self.import_blocks_id_list
        elif object_type == "definitions":
            list_to_use = self.lst_import_def
            ids_list = self.import_definitions_id_list

        count_added = 0
        for obj in objects:
            data = self.empty_list_item_dictionary()
            data["id"] = f'{obj["id"]}:{archive_path}'

            ids_in_list = [x["id"] for x in ids_list]
            if f'{obj["id"]}:{archive_path}' in ids_in_list:
                continue

            data["src"] = archive_path

            if object_type == "blocks":
                name = obj["date"]
                if obj["name"]:
                    name += f' - {obj["name"]}'
                data["name"] = name
                data["text"] = obj["body"]
                data["block"] = obj
            elif object_type == "definitions":
                data["name"] = obj["name"]
                data["text"] = obj["description"]
                data["definition"] = obj
            
            data["width"] = list_to_use.width() - 20

            ids_list.append(data)
            count_added += 1

    def _get_objects_from_archive(self, archive_path: str, object_type: str) -> list | None:
        if object_type not in ["blocks", "definitions"]:
            return []
        
        # Define Temp Folder
        tmp_folder_path = self.getv("temp_folder_path")
        if not UTILS.FileUtility.FOLDER_is_exist(tmp_folder_path):
            UTILS.FileUtility.FOLDER_create(tmp_folder_path)
        
        # Define temp data file, file will be added to archive later
        tmp_data_file_name = "tmp_export_data.json"
        tmp_data_file_path = "tmp_export_data.json"
        tmp_data_file_path = UTILS.FileUtility.join_folder_and_file_name(tmp_folder_path, tmp_data_file_path)

        if UTILS.FileUtility.FILE_is_exist(tmp_data_file_path):
            UTILS.FileUtility.FILE_delete(tmp_data_file_path)
        
        
        archive_content = UTILS.FileUtility.ZIP_list_archive(archive_path)

        if tmp_data_file_name not in archive_content:
            self._msg_bad_archive(archive_path)
            return None

        result = UTILS.FileUtility.ZIP_extract_file_from_archive(archive_path, tmp_data_file_name, tmp_folder_path)
        if not result:
            self._msg_extract_archive_error(archive_path)
            return None
        
        objects_data = UTILS.FileUtility.JSON_load(tmp_data_file_path)

        UTILS.FileUtility.FILE_delete(tmp_data_file_path)

        if not objects_data.get(object_type):
            self._msg_extract_archive_no_data(archive_path, objects_data.get("blocks"), objects_data.get("definitions"))
            return None
        
        return objects_data[object_type]

    def _msg_bad_archive(self, archive_path: str) -> None:
        msg_data = {
            "title": self.getl("export_import_msg_bad_archive_title"),
            "text": self.getl("export_import_msg_bad_archive_text") + f"\n{archive_path}"
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_data, app_modal=True)

    def _msg_extract_archive_no_data(self, archive_path: str, block_list: list, def_list: list) -> None:
        msg_data = {
            "title": self.getl("export_import_msg_archive_no_data_title")
        }

        if block_list and not def_list:
            msg_data["text"] = self.getl("export_import_msg_archive_has_block_no_def_text").replace("#1", str(len(block_list))) + f"\n{archive_path}"
        elif def_list and not block_list:
            msg_data["text"] = self.getl("export_import_msg_archive_no_block_has_def_text").replace("#1", str(len(def_list))) + f"\n{archive_path}"
        elif not def_list and not block_list:
            msg_data["text"] = self.getl("export_import_msg_archive_no_block_no_def_text") + f"\n{archive_path}"
        else:
            msg_data["text"] = archive_path

        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_data, app_modal=True)

    def _msg_extract_archive_error(self, archive_path: str) -> None:
        msg_data = {
            "title": self.getl("export_import_msg_extract_archive_error_title"),
            "text": self.getl("export_import_msg_extract_archive_error_text") + f"\n{archive_path}"
        }

        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, msg_data, app_modal=True)

    def _ask_for_archive_filename(self) -> str | None:
        result = UTILS.FileUtility.show_open_file_PyQt5(
            parent_widget=self,
            title=self.getl("export_import_open_archive_dialog_title"),
            initial_dir=self.last_import_folder,
            filters="Archive Files (*.zip);;All Files (*.*)"
        )

        if result and UTILS.FileUtility.ZIP_is_zipfile(result):
            self.last_import_folder = result
            return result
        
        return None

    def populate_export_defs_list(self) -> None:
        self._populate_export_list(self.lst_export_def, self.export_definitions_id_list, self._fill_definition_id_data)

    def _fill_block_id_data(self, data: dict) -> dict:
        db_rec = db_record_cls.Record(self._stt)
        db_rec.load_record(data["id"])
        name = db_rec.RecordDate
        if db_rec.RecordName:
            name += f" - {db_rec.RecordName}"
        data["name"] = name
        data["src"] = f'{self.get_appv("user").username} - DataBase'
        data["text"] = db_rec.RecordBody
        
        # Fill Block data
        data["block"] = {
            "id": data["id"],
            "name": db_rec.RecordName,
            "date": db_rec.RecordDate,
            "body": db_rec.RecordBody,
            "body_html": db_rec.RecordBodyHTML,
            "draft": 1,
            "tags": [],
            "images": [],
            "files": []
        }

        db_rec_data = db_record_data_cls.RecordData(self._stt)
        record_data = db_rec_data.get_record_data(data["id"])
        
        # Fill Tags, Images and Files data
        db_images = db_media_cls.Media(self._stt)
        db_files = db_media_cls.Files(self._stt)
        db_tags = db_tag_cls.Tag(self._stt)
        
        for item in record_data:
            if item[2]:
                db_tags.populate_values(item[2])
                tag_dict = {
                    "id": db_tags.TagID,
                    "name": db_tags.TagName,
                    "description": db_tags.TagDescription
                }
                data["block"]["tags"].append(tag_dict)
            if item[3]:
                if db_images.is_media_exist(item[3]):
                    db_images.load_media(item[3])
                    image_dict = {
                        "id": db_images.media_id,
                        "name": db_images.media_name,
                        "description": db_images.media_description,
                        "http": db_images.media_http,
                        "file": db_images.media_file
                    }
                    data["block"]["images"].append(image_dict)
                if db_files.is_file_exist(item[3]):
                    db_files.load_file(item[3])
                    file_dict = {
                        "id": db_files.file_id,
                        "name": db_files.file_name,
                        "description": db_files.file_description,
                        "http": db_files.file_http,
                        "file": db_files.file_file
                    }
                    data["block"]["files"].append(file_dict)

    def _fill_definition_id_data(self, data: dict) -> dict:
        db_def = db_definition_cls.Definition(self._stt)
        db_def.load_definition(data["id"])
        data["name"] = db_def.definition_name
        data["src"] = f'{self.get_appv("user").username} - DataBase'
        data["text"] = db_def.definition_description

        # Fill Definition data
        data["definition"] = {
            "id": data["id"],
            "name": db_def.definition_name,
            "description": db_def.definition_description,
            "synonyms": db_def.definition_synonyms,
            "images": [],
            "default": db_def.default_media_id
        }

        # Fill images data
        db_images = db_media_cls.Media(self._stt)
        for image_id in db_def.definition_media_ids:
            db_images.load_media(image_id)
            image_dict = {
                "id": db_images.media_id,
                "name": db_images.media_name,
                "description": db_images.media_description,
                "http": db_images.media_http,
                "file": db_images.media_file
            }
            data["definition"]["images"].append(image_dict)

    def update_progress(self, current_item_number: int, total_items: int, prg_widget: QProgressBar = None) -> bool:
        if self.abort_action:
            return False

        if total_items == 0:
            return True
        
        if prg_widget is None:
            prg_widget = self.prg_working

        value = int((current_item_number / total_items) * 100)
        if value > prg_widget.maximum():
            value = prg_widget.maximum()

        prg_widget.setValue(value)

        QCoreApplication.processEvents()

        return True

    def _populate_export_list(self, list_obj: QListWidget, ids: list, id_info_function) -> None:
        disabled_ids = self._get_all_disabled_ids(list_obj)

        self._clear_list(list_obj)

        for count, id_item in enumerate(ids):
            # Create QListWidgetItem and add it to list
            list_item = QListWidgetItem(list_obj)
            list_obj.addItem(list_item)
            # Populate data dictionary
            data = self.empty_list_item_dictionary()
            data["id"] = id_item
            
            # Populate block/definition data
            id_info_function(data)
            
            if id_item in disabled_ids:
                data["enabled"] = False
            else:
                data["enabled"] = True
            data["width"] = list_obj.width() - 20
            # Create widget and assign it to list item
            widget_item = ListItem(self._stt, list_obj, data)
            list_obj.setItemWidget(list_item, widget_item)
            list_item.setSizeHint(widget_item.size())
            
            if not self.update_progress(count, len(ids)):
                break
        
        self._resize_list_items()

    def _clear_list(self, list_obj: QListWidget) -> None:
        for i in range(list_obj.count()):
            list_item: ListItem = list_obj.itemWidget(list_obj.item(i))
            list_item.close_me()
        list_obj.clear()            

    def _get_all_disabled_ids(self, list_obj: QListWidget) -> list:
        result = []
        for i in range(list_obj.count()):
            list_item: ListItem = list_obj.itemWidget(list_obj.item(i))
            if not list_item.is_enabled:
                result.append(list_item.get_id())
        return result

    def empty_list_item_dictionary(self) -> dict:
        result = {
            "id": "",
            "name": "",
            "src": "",
            "text": "",
            "enabled": True,
            "width": self.lst_export_block.width() - 20,
            "widget_handler": self.widget_handler,
            "update_function": self.update_widgets_appearance
        }
        return result

    def update_widgets_appearance(self) -> None:
        text = self.tab_action.tabText(self.tab_action.currentIndex())
        self.lbl_title.setText(text)
        self.btn_exec.setText(text)
        self.setWindowTitle(text)
        self.setWindowIcon(self.tab_action.tabIcon(self.tab_action.currentIndex()))

        if self.tab_action.currentIndex() == self.EXPORT_BLOCKS_INDEX:
            # Export Blocks
            lst = self.lst_export_block
            no_items_in_clip = self._app_clip.block_clip_number_of_items()
            new_items_in_clip = no_items_in_clip - len(self._app_clip.block_clip_ids_that_are_in_clipboard(self.get_item_ids_in_list(lst)))
            if lst.count():
                self.btn_export_block_clear.setEnabled(True)
                self.btn_export_block_clear.setText(f'{self.getl("export_import_btn_export_block_clear_text")} ({lst.count()})')
            else:
                self.btn_export_block_clear.setEnabled(False)
                self.btn_export_block_clear.setText(self.getl("export_import_btn_export_block_clear_text"))
            if new_items_in_clip:
                self.btn_export_block_paste.setEnabled(True)
                self.btn_export_block_paste.setText(f'{self.getl("export_import_btn_export_block_paste_text")} ({new_items_in_clip}/{no_items_in_clip})')
            else:
                self.btn_export_block_paste.setEnabled(False)
                self.btn_export_block_paste.setText(self.getl("export_import_btn_export_block_paste_text"))
            
            selected = 0
            for i in range(lst.count()):
                if lst.itemWidget(lst.item(i)).is_enabled:
                    selected += 1

            if selected:
                self.btn_exec.setEnabled(True)
            else:
                self.btn_exec.setEnabled(False)

            if lst.count():
                self.lbl_export_block_info.setText(self.getl("export_import_lbl_export_block_info_text").replace("#1", str(selected)).replace("#2", str(lst.count())))
            else:
                self.lbl_export_block_info.setText(self.getl("export_import_lbl_export_block_info_no_data_text"))
        elif self.tab_action.currentIndex() == self.IMPORT_BLOCKS_INDEX:
            # Import Blocks
            lst = self.lst_import_block
            if lst.count():
                self.btn_import_block_clear.setEnabled(True)
                self.btn_import_block_clear.setText(f'{self.getl("export_import_btn_import_block_clear_text")} ({lst.count()})')
            else:
                self.btn_import_block_clear.setEnabled(False)
                self.btn_import_block_clear.setText(self.getl("export_import_btn_import_block_clear_text"))
            
            selected = 0
            for i in range(lst.count()):
                if lst.itemWidget(lst.item(i)).is_enabled:
                    selected += 1

            if selected:
                self.btn_exec.setEnabled(True)
            else:
                self.btn_exec.setEnabled(False)

            if lst.count():
                self.lbl_import_block_info.setText(self.getl("export_import_lbl_export_block_info_text").replace("#1", str(selected)).replace("#2", str(lst.count())))
            else:
                self.lbl_import_block_info.setText(self.getl("export_import_lbl_export_block_info_no_data_text"))
        elif self.tab_action.currentIndex() == self.EXPORT_DEFINITIONS_INDEX:
            # Export Definitions
            lst = self.lst_export_def
            no_items_in_clip = self._app_clip.def_clip_number_of_items()
            new_items_in_clip = no_items_in_clip - len(self._app_clip.def_clip_ids_that_are_in_clipboard(self.get_item_ids_in_list(lst)))
            if lst.count():
                self.btn_export_def_clear.setEnabled(True)
                self.btn_export_def_clear.setText(f'{self.getl("export_import_btn_export_def_clear_text")} ({lst.count()})')
            else:
                self.btn_export_def_clear.setEnabled(False)
                self.btn_export_def_clear.setText(self.getl("export_import_btn_export_def_clear_text"))
            if new_items_in_clip:
                self.btn_export_def_paste.setEnabled(True)
                self.btn_export_def_paste.setText(f'{self.getl("export_import_btn_export_def_paste_text")} ({new_items_in_clip}/{no_items_in_clip})')
            else:
                self.btn_export_def_paste.setEnabled(False)
                self.btn_export_def_paste.setText(self.getl("export_import_btn_export_def_paste_text"))
            
            selected = 0
            for i in range(lst.count()):
                if lst.itemWidget(lst.item(i)).is_enabled:
                    selected += 1

            if selected:
                self.btn_exec.setEnabled(True)
            else:
                self.btn_exec.setEnabled(False)

            if lst.count():
                self.lbl_export_def_info.setText(self.getl("export_import_lbl_export_def_info_text").replace("#1", str(selected)).replace("#2", str(lst.count())))
            else:
                self.lbl_export_def_info.setText(self.getl("export_import_lbl_export_def_info_no_data_text"))
        elif self.tab_action.currentIndex() == self.IMPORT_DEFINITIONS_INDEX:
            # Import Definitions
            lst = self.lst_import_def
            if lst.count():
                self.btn_import_def_clear.setEnabled(True)
                self.btn_import_def_clear.setText(f'{self.getl("export_import_btn_import_def_clear_text")} ({lst.count()})')
            else:
                self.btn_import_def_clear.setEnabled(False)
                self.btn_import_def_clear.setText(self.getl("export_import_btn_import_def_clear_text"))
            
            selected = 0
            for i in range(lst.count()):
                if lst.itemWidget(lst.item(i)).is_enabled:
                    selected += 1

            if selected:
                self.btn_exec.setEnabled(True)
            else:
                self.btn_exec.setEnabled(False)

            if lst.count():
                self.lbl_import_def_info.setText(self.getl("export_import_lbl_export_def_info_text").replace("#1", str(selected)).replace("#2", str(lst.count())))
            else:
                self.lbl_import_def_info.setText(self.getl("export_import_lbl_export_def_info_no_data_text"))

    def get_item_ids_in_list(self, list_object: QListWidget) -> list:
        result = []
        for index in range(list_object.count()):
            item: ListItem = list_object.itemWidget(list_object.item(index))
            result.append(item.get_id())
        
        return result

    def _load_win_position(self):
        if "export_import_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("export_import_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])
            self.last_export_folder = g.get("last_export_folder", "")
            self.last_import_folder = g.get("last_import_folder", "")

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.frm_working.isVisible():
            self.abort_action = True
            a0.ignore()
            return

        if self.frm_execute.isVisible():
            a0.ignore()

            if self.btn_execute_done.isVisible() and self.btn_execute_done.isEnabled():
               self.btn_execute_done_click()
               return
            
            if self.btn_execute_cancel.isVisible() and self.btn_execute_cancel.isEnabled():
                self.btn_execute_cancel_click()
                return
        
            self.abort_action = True
            return

        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "export_import_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("export_import_win_geometry", {}, save_to_file=True)

        g = self.get_appv("export_import_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()
        g["last_export_folder"] = UTILS.FileUtility.get_FileInformation_object(self.last_export_folder).get_dir_name().rstrip("/")
        g["last_import_folder"] = UTILS.FileUtility.get_FileInformation_object(self.last_import_folder).get_dir_name().rstrip("/")

        self.get_appv("cm").remove_all_context_menu()
        
        # Close all list items
        self._clear_list(self.lst_export_block)
        self._clear_list(self.lst_import_block)
        self._clear_list(self.lst_export_def)
        self._clear_list(self.lst_import_def)

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["ExportImport"])
        UTILS.DialogUtility.on_closeEvent(self)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._resize_widgets()
        return super().resizeEvent(a0)

    def _resize_widgets(self) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        
        self.lbl_title.resize(w, self.lbl_title.height())

        self.tab_action.resize(w - 20, h - 140)

        self.btn_cancel.move(w - 100, h - 40)
        self.btn_exec.move(w - 320, h - 40)

        tab_w = self.tab_action.contentsRect().width() - 20
        if tab_w < 20:
            tab_w = 20
        tab_h = self.tab_action.contentsRect().height() - 20 - self.tab_action.tabBar().height()
        if tab_h < 60:
            tab_h = 60
        # Export Blocks
        self.frm_export_block.resize(tab_w, tab_h)
        lbl_w = tab_w - self.lbl_export_block_info.pos().x() - 10
        if lbl_w < 0:
            lbl_w = 0
        self.lbl_export_block_info.resize(lbl_w, self.lbl_export_block_info.height())
        self.lst_export_block.resize(tab_w - 20, tab_h - 60)
        # Import Blocks
        self.frm_import_block.resize(tab_w, tab_h)
        lbl_w = tab_w - self.lbl_import_block_info.pos().x() - 10
        if lbl_w < 0:
            lbl_w = 0
        self.lbl_import_block_info.resize(lbl_w, self.lbl_import_block_info.height())
        self.lst_import_block.resize(tab_w - 20, tab_h - 60)
        # Export Definitions
        self.frm_export_def.resize(tab_w, tab_h)
        lbl_w = tab_w - self.lbl_export_def_info.pos().x() - 10
        if lbl_w < 0:
            lbl_w = 0
        self.lbl_export_def_info.resize(lbl_w, self.lbl_export_def_info.height())
        self.lst_export_def.resize(tab_w - 20, tab_h - 60)
        # Import Definitions
        self.frm_import_def.resize(tab_w, tab_h)
        lbl_w = tab_w - self.lbl_import_def_info.pos().x() - 10
        if lbl_w < 0:
            lbl_w = 0
        self.lbl_import_def_info.resize(lbl_w, self.lbl_import_def_info.height())
        self.lst_import_def.resize(tab_w - 20, tab_h - 60)

        self._resize_list_items()
        self._resize_execute_frame()

    def _resize_execute_frame(self):
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        btn_w = self.btn_execute_confirm.width()

        self.frm_execute.move(0, 0)
        self.frm_execute.resize(w, h)

        # Title
        self.lbl_execute_title.move(10, 10)
        self.lbl_execute_title.resize(w - (btn_w + 30), 30)

        # TextBox
        self.txt_execute.move(10, 50)
        self.txt_execute.resize(w - (btn_w + 30), h - 60)
        self.prg_find_match.move(self.txt_execute.pos().x() + 2, self.txt_execute.pos().y() + 2)
        self.prg_find_match.resize(self.txt_execute.width() - 4, self.prg_find_match.height())

        # List box
        self.lst_execute.move(self.txt_execute.pos())
        self.lst_execute.resize(self.txt_execute.size())

        # Buttons
        y = 10
        x = w - btn_w - 10

        self.btn_execute_confirm.move(x, y)
        self.btn_execute_done.move(x, y)
        y += self.btn_execute_confirm.height() + 10

        self.btn_execute_cancel.move(x, y)
        y += self.btn_execute_cancel.height() + 10

        self.btn_execute_details.move(x, y)
        y += self.btn_execute_details.height() + 10

        self.btn_execute_actions.move(x, y)
        y += self.btn_execute_actions.height() + 10

        self.lbl_execute_info.move(x, y)
        self.lbl_execute_info.resize(btn_w, (h - self.btn_execute_abort.height() - 20) - y)

        y = h - self.btn_execute_abort.height() - 10
        self.btn_execute_abort.move(x, y)
        self.prg_import_export.move(self.btn_execute_abort.pos().x(), self.btn_execute_abort.pos().y() - 20)

    def _resize_list_items(self):
        lst = self.lst_export_block
        if lst.verticalScrollBar().isVisible():
            v_scroll_bar_width = lst.verticalScrollBar().width()
        else:
            v_scroll_bar_width = 0
        for index in range(lst.count()):
            item: ListItem = lst.itemWidget(lst.item(index))
            item.resize_me(lst.contentsRect().width() - v_scroll_bar_width)
            lst.item(index).setSizeHint(item.size())
        lst = self.lst_import_block
        if lst.verticalScrollBar().isVisible():
            v_scroll_bar_width = lst.verticalScrollBar().width()
        else:
            v_scroll_bar_width = 0
        for index in range(lst.count()):
            item: ListItem = lst.itemWidget(lst.item(index))
            item.resize_me(lst.contentsRect().width() - v_scroll_bar_width)
            lst.item(index).setSizeHint(item.size())
        lst = self.lst_export_def
        if lst.verticalScrollBar().isVisible():
            v_scroll_bar_width = lst.verticalScrollBar().width()
        else:
            v_scroll_bar_width = 0
        for index in range(lst.count()):
            item: ListItem = lst.itemWidget(lst.item(index))
            item.resize_me(lst.contentsRect().width() - v_scroll_bar_width)
            lst.item(index).setSizeHint(item.size())
        lst = self.lst_import_def
        if lst.verticalScrollBar().isVisible():
            v_scroll_bar_width = lst.verticalScrollBar().width()
        else:
            v_scroll_bar_width = 0
        for index in range(lst.count()):
            item: ListItem = lst.itemWidget(lst.item(index))
            item.resize_me(lst.contentsRect().width() - v_scroll_bar_width)
            lst.item(index).setSizeHint(item.size())

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["ExportImport"])
        self._setup_widgets_appearance()

    def _setup_widgets(self) -> None:
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.tab_action: QTabWidget = self.findChild(QTabWidget, "tab_action")
        self.tab_item_export_block: QWidget = self.findChild(QWidget, "tab_item_export_block")
        self.tab_item_import_block: QWidget = self.findChild(QWidget, "tab_item_import_block")
        self.tab_item_export_def: QWidget = self.findChild(QWidget, "tab_item_export_def")
        self.tab_item_import_def: QWidget = self.findChild(QWidget, "tab_item_import_def")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_exec: QPushButton = self.findChild(QPushButton, "btn_exec")
        # Export Blocks
        self.frm_export_block: QFrame = self.findChild(QFrame, "frm_export_block")
        self.btn_export_block_clear: QPushButton = self.findChild(QPushButton, "btn_export_block_clear")
        self.btn_export_block_paste: QPushButton = self.findChild(QPushButton, "btn_export_block_paste")
        self.lbl_export_block_info: QLabel = self.findChild(QLabel, "lbl_export_block_info")
        self.lst_export_block: QListWidget = self.findChild(QListWidget, "lst_export_block")
        # Import Blocks
        self.frm_import_block: QFrame = self.findChild(QFrame, "frm_import_block")
        self.btn_import_block_clear: QPushButton = self.findChild(QPushButton, "btn_import_block_clear")
        self.btn_import_block_add_file: QPushButton = self.findChild(QPushButton, "btn_import_block_add_file")
        self.lbl_import_block_info: QLabel = self.findChild(QLabel, "lbl_import_block_info")
        self.lst_import_block: QListWidget = self.findChild(QListWidget, "lst_import_block")
        # Export Definitions
        self.frm_export_def: QFrame = self.findChild(QFrame, "frm_export_def")
        self.btn_export_def_clear: QPushButton = self.findChild(QPushButton, "btn_export_def_clear")
        self.btn_export_def_paste: QPushButton = self.findChild(QPushButton, "btn_export_def_paste")
        self.lbl_export_def_info: QLabel = self.findChild(QLabel, "lbl_export_def_info")
        self.lst_export_def: QListWidget = self.findChild(QListWidget, "lst_export_def")
        # Import Definitions
        self.frm_import_def: QFrame = self.findChild(QFrame, "frm_import_def")
        self.btn_import_def_clear: QPushButton = self.findChild(QPushButton, "btn_import_def_clear")
        self.btn_import_def_add_file: QPushButton = self.findChild(QPushButton, "btn_import_def_add_file")
        self.lbl_import_def_info: QLabel = self.findChild(QLabel, "lbl_import_def_info")
        self.lst_import_def: QListWidget = self.findChild(QListWidget, "lst_import_def")

        # Working Frame
        self.frm_working: QFrame = self.findChild(QFrame, "frm_working")
        self.lbl_working_title: QLabel = self.findChild(QLabel, "lbl_working_title")
        self.prg_working: QProgressBar = self.findChild(QProgressBar, "prg_working")
        self.btn_working_abort: QPushButton = self.findChild(QPushButton, "btn_working_abort")

        # Execute Frame
        self.frm_execute: QFrame = self.findChild(QFrame, "frm_execute")
        self.lbl_execute_title: QLabel = self.findChild(QLabel, "lbl_execute_title")
        self.txt_execute: QTextEdit = self.findChild(QTextEdit, "txt_execute")
        self.lst_execute: QListWidget = self.findChild(QListWidget, "lst_execute")
        self.btn_execute_confirm: QPushButton = self.findChild(QPushButton, "btn_execute_confirm")
        self.btn_execute_done: QPushButton = self.findChild(QPushButton, "btn_execute_done")
        self.btn_execute_cancel: QPushButton = self.findChild(QPushButton, "btn_execute_cancel")
        self.btn_execute_details: QPushButton = self.findChild(QPushButton, "btn_execute_details")
        self.btn_execute_actions: QPushButton = self.findChild(QPushButton, "btn_execute_actions")
        self.btn_execute_abort: QPushButton = self.findChild(QPushButton, "btn_execute_abort")
        self.lbl_execute_info: QLabel = self.findChild(QLabel, "lbl_execute_info")
        self.prg_import_export: QProgressBar = self.findChild(QProgressBar, "prg_import_export")
        self.prg_find_match: QProgressBar = self.findChild(QProgressBar, "prg_find_match")

        self.lbl_drop_block = QLabel(self.frm_export_block)
        self.lbl_drop_def = QLabel(self.frm_export_def)

        # Updating frame
        self.frm_updating: QFrame = self.findChild(QFrame, "frm_updating")
        self.lbl_updating_title: QLabel = self.findChild(QLabel, "lbl_updating_title")
        self.lbl_updating_content: QLabel = self.findChild(QLabel, "lbl_updating_content")

    def _setup_widgets_text(self) -> None:
        self.tab_action.setTabText(self.EXPORT_BLOCKS_INDEX, self.getl("export_import_tab_export_blocks_text"))
        self.tab_action.setTabText(self.IMPORT_BLOCKS_INDEX, self.getl("export_import_tab_import_blocks_text"))
        self.tab_action.setTabText(self.EXPORT_DEFINITIONS_INDEX, self.getl("export_import_tab_export_defs_text"))
        self.tab_action.setTabText(self.IMPORT_DEFINITIONS_INDEX, self.getl("export_import_tab_import_defs_text"))

        self.btn_cancel.setText(self.getl("btn_cancel"))

        # Export Blocks
        self.btn_export_block_clear.setText(self.getl("export_import_btn_export_block_clear_text"))
        self.btn_export_block_clear.setToolTip(self.getl("export_import_btn_export_block_clear_tt"))
        self.btn_export_block_paste.setText(self.getl("export_import_btn_export_block_paste_text"))
        self.btn_export_block_paste.setToolTip(self.getl("export_import_btn_export_block_paste_tt"))
        self.lbl_export_block_info.setText("")
        # Import Blocks
        self.btn_import_block_clear.setText(self.getl("export_import_btn_import_block_clear_text"))
        self.btn_import_block_clear.setToolTip(self.getl("export_import_btn_import_block_clear_tt"))
        self.btn_import_block_add_file.setText(self.getl("export_import_btn_import_block_add_file_text"))
        self.btn_import_block_add_file.setToolTip(self.getl("export_import_btn_import_block_add_file_tt"))
        self.lbl_import_block_info.setText("")
        # Export Definitions
        self.btn_export_def_clear.setText(self.getl("export_import_btn_export_def_clear_text"))
        self.btn_export_def_clear.setToolTip(self.getl("export_import_btn_export_def_clear_tt"))
        self.btn_export_def_paste.setText(self.getl("export_import_btn_export_def_paste_text"))
        self.btn_export_def_paste.setToolTip(self.getl("export_import_btn_export_def_paste_tt"))
        self.lbl_export_def_info.setText("")
        # Import Definitions
        self.btn_import_def_clear.setText(self.getl("export_import_btn_import_def_clear_text"))
        self.btn_import_def_clear.setToolTip(self.getl("export_import_btn_import_def_clear_tt"))
        self.btn_import_def_add_file.setText(self.getl("export_import_btn_import_def_add_file_text"))
        self.btn_import_def_add_file.setToolTip(self.getl("export_import_btn_import_def_add_file_tt"))
        self.lbl_import_def_info.setText("")

        # Working frame
        self.lbl_working_title.setText(self.getl("please_wait"))
        self.btn_working_abort.setText(self.getl("export_import_btn_working_abort_text"))

        # Execute frame
        self.btn_execute_cancel.setText(self.getl("btn_cancel"))
        self.btn_execute_done.setText(self.getl("export_import_btn_execute_done_text"))
        self.btn_execute_details.setText(self.getl("export_import_btn_execute_details_text"))
        self.btn_execute_actions.setText(self.getl("export_import_btn_execute_actions_text"))
        self.btn_execute_abort.setText(self.getl("export_import_btn_working_abort_text"))
        self.lbl_execute_info.setText("")

        # Updating frame
        self.lbl_updating_title.setText(self.getl("updating_data"))

    def _setup_widgets_appearance(self) -> None:
        self._setup_win_export_import()

        self.tab_action.setTabIcon(self.EXPORT_BLOCKS_INDEX, QIcon(QPixmap(self.getv("export_icon_path"))))
        self.tab_action.setTabIcon(self.IMPORT_BLOCKS_INDEX, QIcon(QPixmap(self.getv("import_icon_path"))))
        self.tab_action.setTabIcon(self.EXPORT_DEFINITIONS_INDEX, QIcon(QPixmap(self.getv("export_icon_path"))))
        self.tab_action.setTabIcon(self.IMPORT_DEFINITIONS_INDEX, QIcon(QPixmap(self.getv("import_icon_path"))))

        self.tab_action.setStyleSheet(self.getv("export_import_tab_action_stylesheet"))

        self.lbl_title.setStyleSheet(self.getv("export_import_lbl_title_stylesheet"))
        self.btn_cancel.setStyleSheet(self.getv("export_import_btn_cancel_stylesheet"))
        self.btn_cancel.setIcon(QIcon(QPixmap(self.getv("export_import_btn_cancel_icon_path"))))
        self.btn_exec.setStyleSheet(self.getv("export_import_btn_exec_stylesheet"))
        self.btn_exec.setIcon(QIcon(QPixmap(self.getv("export_import_btn_exec_icon_path"))))

        self.lbl_drop_block.setStyleSheet("QLabel {background-color: transparent;}")
        self.lbl_drop_block.setAlignment(Qt.AlignCenter)
        UTILS.WidgetUtility.set_image_to_label(self.getv("drop_icon_path"), self.lbl_drop_block)
        self.lbl_drop_block.setVisible(False)
        self.lbl_drop_def.setStyleSheet("QLabel {background-color: transparent;}")
        self.lbl_drop_def.setAlignment(Qt.AlignCenter)
        UTILS.WidgetUtility.set_image_to_label(self.getv("drop_icon_path"), self.lbl_drop_def)
        self.lbl_drop_def.setVisible(False)

        # Export Blocks
        self.frm_export_block.setStyleSheet(self.getv("export_import_frm_export_block_stylesheet"))
        self.btn_export_block_clear.setStyleSheet(self.getv("export_import_btn_export_block_clear_stylesheet"))
        self.btn_export_block_clear.setIcon(QIcon(QPixmap(self.getv("export_import_btn_export_block_clear_icon_path"))))
        self.btn_export_block_paste.setStyleSheet(self.getv("export_import_btn_export_block_paste_stylesheet"))
        self.btn_export_block_paste.setIcon(QIcon(QPixmap(self.getv("export_import_btn_export_block_paste_icon_path"))))
        self.lbl_export_block_info.setStyleSheet(self.getv("export_import_lbl_export_block_info_stylesheet"))
        
        self.lst_export_block.setStyleSheet(self.getv("export_import_lst_export_block_stylesheet"))
        self.lst_export_block.verticalScrollBar().setSingleStep(self.SCROLL_BY_PIXEL)
        self.lst_export_block.setAcceptDrops(True)
        self.lst_export_block.setDragEnabled(False)
        self.lst_export_block.setDragDropMode(QAbstractItemView.InternalMove)
        # Import Blocks
        self.frm_import_block.setStyleSheet(self.getv("export_import_frm_import_block_stylesheet"))
        self.btn_import_block_clear.setStyleSheet(self.getv("export_import_btn_import_block_clear_stylesheet"))
        self.btn_import_block_clear.setIcon(QIcon(QPixmap(self.getv("export_import_btn_import_block_clear_icon_path"))))
        self.btn_import_block_add_file.setStyleSheet(self.getv("export_import_btn_import_block_add_file_stylesheet"))
        self.btn_import_block_add_file.setIcon(QIcon(QPixmap(self.getv("export_import_btn_import_block_add_file_icon_path"))))
        self.lbl_import_block_info.setStyleSheet(self.getv("export_import_lbl_import_block_info_stylesheet"))
        self.lst_import_block.setStyleSheet(self.getv("export_import_lst_import_block_stylesheet"))
        self.lst_import_block.verticalScrollBar().setSingleStep(self.SCROLL_BY_PIXEL)
        # Export Definitions
        self.frm_export_def.setStyleSheet(self.getv("export_import_frm_export_def_stylesheet"))
        self.btn_export_def_clear.setStyleSheet(self.getv("export_import_btn_export_def_clear_stylesheet"))
        self.btn_export_def_clear.setIcon(QIcon(QPixmap(self.getv("export_import_btn_export_def_clear_icon_path"))))
        self.btn_export_def_paste.setStyleSheet(self.getv("export_import_btn_export_def_paste_stylesheet"))
        self.btn_export_def_paste.setIcon(QIcon(QPixmap(self.getv("export_import_btn_export_def_paste_icon_path"))))
        self.lbl_export_def_info.setStyleSheet(self.getv("export_import_lbl_export_def_info_stylesheet"))

        self.lst_export_def.setStyleSheet(self.getv("export_import_lst_export_def_stylesheet"))
        self.lst_export_def.verticalScrollBar().setSingleStep(self.SCROLL_BY_PIXEL)
        self.lst_export_def.setAcceptDrops(True)
        self.lst_export_def.setDragEnabled(False)
        self.lst_export_def.setDragDropMode(QAbstractItemView.InternalMove)
        # Import Definitions
        self.frm_import_def.setStyleSheet(self.getv("export_import_frm_import_def_stylesheet"))
        self.btn_import_def_clear.setStyleSheet(self.getv("export_import_btn_import_def_clear_stylesheet"))
        self.btn_import_def_clear.setIcon(QIcon(QPixmap(self.getv("export_import_btn_import_def_clear_icon_path"))))
        self.btn_import_def_add_file.setStyleSheet(self.getv("export_import_btn_import_def_add_file_stylesheet"))
        self.btn_import_def_add_file.setIcon(QIcon(QPixmap(self.getv("export_import_btn_import_def_add_file_icon_path"))))
        self.lbl_import_def_info.setStyleSheet(self.getv("export_import_lbl_import_def_info_stylesheet"))
        self.lst_import_def.setStyleSheet(self.getv("export_import_lst_import_def_stylesheet"))
        self.lst_import_def.verticalScrollBar().setSingleStep(self.SCROLL_BY_PIXEL)

        # Working frame
        self.frm_working.setVisible(False)

        # Execute frame
        self.frm_execute.setStyleSheet(self.getv("export_import_frm_execute_stylesheet"))
        self.lbl_execute_title.setStyleSheet(self.getv("export_import_lbl_execute_title_stylesheet"))
        self.txt_execute.setStyleSheet(self.getv("export_import_txt_execute_stylesheet"))
        self.lst_execute.setStyleSheet(self.getv("export_import_lst_execute_stylesheet"))
        self.btn_execute_abort.setStyleSheet(self.getv("export_import_btn_working_abort_stylesheet"))
        self.btn_execute_abort.setIcon(QIcon(QPixmap(self.getv("export_import_btn_working_abort_icon_path"))))
        self.btn_execute_confirm.setStyleSheet(self.getv("export_import_btn_execute_confirm_stylesheet"))
        self.btn_execute_confirm.setIcon(QIcon(QPixmap(self.getv("export_import_btn_execute_confirm_icon_path"))))
        self.btn_execute_done.setStyleSheet(self.getv("export_import_btn_execute_done_stylesheet"))
        self.btn_execute_done.setIcon(QIcon(QPixmap(self.getv("export_import_btn_execute_done_icon_path"))))
        self.btn_execute_cancel.setStyleSheet(self.getv("export_import_btn_execute_cancel_stylesheet"))
        self.btn_execute_cancel.setIcon(QIcon(QPixmap(self.getv("export_import_btn_execute_cancel_icon_path"))))
        self.btn_execute_details.setStyleSheet(self.getv("export_import_btn_execute_details_stylesheet"))
        self.btn_execute_details.setIcon(QIcon(QPixmap(self.getv("export_import_btn_execute_details_icon_path"))))
        self.btn_execute_actions.setStyleSheet(self.getv("export_import_btn_execute_actions_stylesheet"))
        self.btn_execute_actions.setIcon(QIcon(QPixmap(self.getv("export_import_btn_execute_actions_icon_path"))))
        self.lbl_execute_info.setStyleSheet(self.getv("export_import_lbl_execute_info_correct_stylesheet"))
        self.frm_execute.setVisible(False)
        self.prg_import_export.setVisible(False)
        self.prg_find_match.setVisible(False)
        self.frm_updating.setVisible(False)

    def _setup_win_export_import(self) -> None:
        self.setStyleSheet(self.getv("export_import_win_stylesheet"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(320, 250)


