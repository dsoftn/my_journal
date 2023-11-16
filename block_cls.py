from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout,
    QGridLayout, QWidget, QSpacerItem, QSizePolicy, QMainWindow)
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QStaticText, QCursor
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtGui

import copy

import settings_cls
import log_cls
import users_cls
import database_cls
import db_record_cls
import db_record_data_cls
import utility_cls
import db_tag_cls
import block_widgets_cls


class WinBlock(QFrame):

    """ This class is a block Frame, this QFrame contains all block elements.
    It contains the following variables:
        self._active_record_id (int): RecordID
        self._parent_widget (obj)
        self.collapsed (bool): Indicator whether the block is collapsed or expanded
        self.signals (obj): Signals class 'utility_cls.Signals' which manages user defined signals
        self._data_dict (dict):
            This dictionary contains information about the relationships of the current
            RecordID with data in other database tables.
            The dictionary is obtained using the class 'db_record_data_cls.RecordData'
            Each key of the dictionary contains a list of IDs of the corresponding
            table in the database.
            The original dictionary is extended with several keys.
            This dictionary now represents all the information about the block and every
            element of the block such as button, text box and so on can update this dictionary.
            Recording of the block is done using the information from this dictionary.
                data_dict:
                    ORIGINAL DICTIONARY:
                        'tag'
                        'media'
                    EXTENDED KEYS:
                        'record_date' (str): Date of record
                        'name' (str): Record name
                        'body' (str): Text in block
                        'updated' (str): Updated time
                        'draft' (int)
                        'save' (bool)
    """

    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget, record_id: int, collapsed: bool = False, animate_block: bool = True, main_window: QMainWindow = None, *args, **kwargs):
        super().__init__(parent_widget, *args, *kwargs)
        
        self.setMouseTracking(True)
        self.setFixedHeight(1)
        
        # Define settings variables:
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables:
        self._parent_widget = parent_widget
        self.block_is_active = False
        
        if main_window:
            self._main_window = main_window
        else:
            self._main_window = self.get_appv("main_win")

        self._active_record_id = record_id
        self.collapsed = collapsed
        self.animate_block = animate_block
        self.drag_mode = []
        self._dont_save_on_close_event = False

        self.signals: utility_cls.Signals = self.get_appv("signal")

        # Get record data dictionary
        record_data = db_record_data_cls.RecordData(self._stt, self._active_record_id)
        self._data_dict = record_data.get_record_data_dict()
        
        # Extend data_dict
        record = db_record_cls.Record(self._stt, self._active_record_id)
        self._data_dict["record_date"] = record.RecordDate
        self._data_dict["name"] = record.RecordName
        self._data_dict["body"] = record.RecordBody
        self._data_dict["body_html"] = record.RecordBodyHTML
        self._data_dict["updated"] = record.RecordUpdatedAt
        self._data_dict["draft"] = record.RecordDraft
        self._data_dict["need_update"] = False
        if record.RecordDraft == 0:
            self._data_dict["save"] = True
        else:
            self._data_dict["save"] = False
        
        # Set margins for win block
        self._set_margins(self, "win_block")
        # Add to win block Vertical Box Layout
        self.setLayout(QVBoxLayout(self))
        self._set_margins(self.layout(), "win_block_layout")
        # Make controls frame  date, name_of_block, close_btn
        self.win_block_controls = block_widgets_cls.Frame(self, self._stt, self._active_record_id, "win_block_controls", self._data_dict, main_win=self._main_window)
        # Define apperance
        self._define_apperance()
        # Get data block
        self.data_block = DataBlock(self, self._stt, self._active_record_id, self._data_dict, main_win=self._main_window)
        # Add WinBlock to Parent Widget (ScrollArea)
        layout_pos = self._parent_widget.layout().count()
        if layout_pos > 0:
            self._parent_widget.layout().insertWidget(layout_pos-1, self)
        else:
            self._parent_widget.layout().addWidget(self)
        self._set_win_block_height()

        # Connect events with slots

        # Connect signals with slots
        self._connect_signals()
    
    def _connect_signals(self):
        """
        Connects user-defined signals to slots
        """
        # Signal to close block
        self.signals.signalCloseAllBlocks.connect(self._signal_close_block)
        # Signal to display all blocks as collapsed
        self.signals.signalCollapseAll.connect(self._collapse_block)
        # Signal to display all blocks as extended
        self.signals.signalExpandAll.connect(self._expand_block)
        # Signal that sets all block titlebars ('self.win_block_controls') to inactive.
        # Later, one block will be determined which will have an active titlebar
        self.signals.signalBlockControlBarInactive.connect(self.block_control_bar_inactive)

    def _signal_close_block(self):
        db_rec = db_record_cls.Record(self._stt)
        if db_rec.is_valid_record_id(self._active_record_id):
            self._close_block(save_data=False, fast_close=True)

    def _set_win_block_height(self):
        """
        Determines the height of the WinBlock depending on whether it is expanded or collapsed.
        """
        # Set height
        if self.collapsed:
            h = self.win_block_controls.height() + 3
            self.data_block.setVisible(False)
        else:
            h = self.win_block_controls.height() + self.data_block.height()
            h += self.contentsMargins().top() + self.contentsMargins().bottom()
            h += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
            h += self.getv("win_block_plus_height_to_ensure_visibility")
            self.data_block.setVisible(True)
        # Animate WinBlock if needed
        info = utility_cls.BlockAnimationInformation(self._stt, load_mode="open", animate_object=self.animate_block, start_height=self.height(), stop_height=h)
        utility_cls.BlockAnimation(info, self)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            if a0.pos().y() in range(self.height() - 4, self.height() + 1):
                if "user_resize_block" not in self._stt.app_setting_get_list_of_keys():
                    self._stt.app_setting_add("user_resize_block", {}, save_to_file=True)
                if not self.collapsed:
                    a0.accept()
                    detail = {}
                    self.data_block.block_event("win_block", "txt_box_height", detail)
                    self.drag_mode = [a0.pos().y(), self.height(), detail["frame_height"], detail["height"], self.data_block.height()]
                    if str(self._active_record_id) not in self.get_appv("user_resize_block"):
                        self.get_appv("user_resize_block")[str(self._active_record_id)] = 0
                    self.setCursor(Qt.SizeVerCursor)
                    return None
        return super().mousePressEvent(a0)
    
    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            if self.drag_mode:
                a0.accept()
                diff = a0.pos().y() - self.drag_mode[0]
                self.drag_mode = []
                self.setCursor(Qt.ArrowCursor)
                self.get_appv("user_resize_block")[str(self._active_record_id)] += diff
                return None
        return super().mouseReleaseEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self.collapsed:
            if a0.pos().y() in range(self.height() - 3, self.height() + 1):
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        if self.drag_mode:
            diff = a0.pos().y() - self.drag_mode[0]
            if self.drag_mode[2] + diff > 60 + self.getv("block_image_thumb_size"):
                a0.accept()
                self.setFixedHeight(self.drag_mode[1] + diff)
                self.data_block.setFixedHeight(self.drag_mode[4] + diff)
                detail = {
                    "set_frame_height": self.drag_mode[2] + diff,
                    "set_height": self.drag_mode[3] + diff
                }
                self.data_block.block_event("win_block", "set_txt_box_height", detail)
                return None
        return super().mouseMoveEvent(a0)

    # Signal SLOT
    def block_control_bar_inactive(self, set_inactive: bool = True, record_id: int = None):
        """
        This is the slot connected to the signal 'signalBlockControlBarInactive'
        """
        if not record_id:
            if set_inactive:
                self.block_is_active = False
                self.win_block_controls.setStyleSheet(self.getv("win_block_controls_stylesheet"))
            else:
                self.block_is_active = True
                self.win_block_controls.setStyleSheet(self.getv("win_block_controls_active_stylesheet"))
        else:
            if self._active_record_id == record_id:
                if set_inactive:
                    self.block_is_active = False
                    self.win_block_controls.setStyleSheet(self.getv("win_block_controls_stylesheet"))
                else:
                    self.block_is_active = True
                    self.win_block_controls.setStyleSheet(self.getv("win_block_controls_active_stylesheet"))

    # Block Event SLOT
    def block_event(self, name, action, detail: dict = None):
        """
        All block elements send information to this method.
        Here, some action is taken if necessary depending on the information received
        from the particular block element
        """
        if action != "text_changed" and action != "set_pointer_to_arrow":
            self.get_appv("log").write_log(f"WinBlock. Event. Widget name, action: {name}, {action}")
        
        self.signals.block_control_bar_inactive(True, 0)
        self.win_block_controls.setStyleSheet(self.getv("win_block_controls_active_stylesheet"))
        self.block_is_active = True
        
        if name == "win_block_controls":
            if action == "mouse_double_clicked":
                if self.collapsed:
                    self._expand_block()
                else:
                    self._collapse_block()
            if action == "mouse_press_right":
                self.action_win_block_controls_frame_right_click()
        
        if name == "win_block_control_btn_name":
            if action == "name_changed":
                self._data_dict["name"] = detail["new_name"]
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
        if name == "win_block_control_btn_date":
            if action == "date_changed":
                self._data_dict["record_date"] = detail["new_date"]
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
        if name == "header_btn_add":
            if action == "tag_changed":
                self._data_dict["tag"] = detail["new_tag_list"]
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
                self.data_block.block_event("win_block", "header_update_buttons")
        if name == "header_btn_diary":
            if action == "tag_changed":
                self._data_dict["tag"] = detail["new_tag_list"]
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
                self.data_block.block_event("win_block", "header_update_buttons")
        if name == "header_btn_tag":
            if action == "tag_changed":
                self._data_dict["tag"] = detail["new_tag_list"]
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
                self.data_block.block_event("win_block", "header_update_buttons")
        if name == "header_btn_user":
            if action == "tag_changed":
                self._data_dict["tag"] = detail["new_tag_list"]
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
                self.data_block.block_event("win_block", "header_update_buttons")
        if name == "body_txt_box":
            if action == "text_changed":
                self._data_dict["save"] = False
                self._data_dict["need_update"] = True
                self._data_dict["draft"] = 1
            if action == "add_image":
                self.data_block.block_event("win_block", "add_image")
            if action == "add_files":
                self.data_block.block_event("win_block", "add_files", detail=detail)
            if action == "save_block":
                self._update_block()
            if action == "autosave":
                self._data_dict["save"] = False
                self._data_dict["draft"] = 1
                self._update_block(silent_update=True)
        if name == "body":
            if action == "image_added":
                self._data_dict["save"] = False
                self._data_dict["draft"] = 1
                self._update_block(silent_update=True)
            if action == "file_added":
                self._data_dict["save"] = False
                self._data_dict["draft"] = 1
                self._update_block(silent_update=True)
            if action == "image_removed":
                self._data_dict["save"] = False
                self._data_dict["draft"] = 1
                self._update_block(silent_update=True)
            if action == "file_removed":
                self._data_dict["save"] = False
                self._data_dict["draft"] = 1
                self._update_block(silent_update=True)
            if action == "auto_add_images":
                self.data_block.block_event("win_block", "auto_add_images")
        if name == "footer":
            if action == "set_pointer_to_arrow":
                self.setCursor(Qt.ArrowCursor)
        if name == "footer_btn_save":
            if action == "update_block":
                self._update_block()
        if name == "footer_btn_delete":
            if action == "block_delete":
                self._delete_block()
        if name == "footer_btn_detection":
            if action == "selected":
                self.data_block.block_event("win_block", "txt_editor_command", detail=detail)
        if name == "save_func":
            if action == "calc_stop":
                self.data_block.block_event("win_block", "calc_stop", detail=detail)
        if name != "win_block" and action == "titlebar_msg":
            self.win_block_controls.block_event("win_block", "titlebar_msg", detail=detail)

        self.signals.saved_button_check_status(self._active_record_id)

    def _delete_block(self):
        db_record = db_record_cls.Record(self._stt, self._active_record_id)
        db_rec_data = db_record_data_cls.RecordData(self._stt, self._active_record_id)
        db_record.delete_record()
        db_rec_data.delete_record_data()
        notif_dict = {
            "title": self.getl("win_block_notification_block_deleted_title"),
            "text": self.getl("win_block_notification_block_deleted_text"),
            "icon": self.getv("block_footer_btn_delete_msg_btn_yes_icon_path"),
            "timer": 1500,
            "position": "bottom right"
        }
        utility_cls.Notification(self._stt, self.get_appv("main_win"), notif_dict)
        self._dont_save_on_close_event = True
        self.get_appv("log").write_log(f"WinBlock. Block Deleted. Record ID: {self._active_record_id}")
        main_dict = {
            "name": "win_block",
            "action": "block_deleted",
            "id": self._active_record_id
        }
        self._main_window.events(main_dict)
        self._close_block(save_data=False)

    def _update_block(self, silent_update: bool = False):
        self._save_record_and_data()
        main_dict = {
            "name": "win_block",
            "action": "block_saved",
            "id": self._active_record_id,
            "closed": self._data_dict["save"]
        }
        self._main_window.events(main_dict)
        ntf_dict = {
            "title": "",
            "text": self.getl("win_block_notif_block_updated_text"),
            "icon": self.getv("win_block_notif_block_updated_icon_path"),
            "timer": 1000
        }
        if not silent_update:
            utility_cls.Notification(self._stt, self, ntf_dict)

    # Button Clicked event
    def btn_clicked(self, button_name, action):
        self.get_appv("log").write_log(f"WinBlock. Button clicked. Button name, action: {button_name}, {action}")
        self.block_event(button_name, action)
        if button_name == "win_block_control_btn_close":
            if action == "clicked":
                self._close_block()
        elif button_name == "win_block_control_btn_expand":
            if action == "clicked":
                self._expand_block()
        elif button_name == "win_block_control_btn_collapse":
            if action == "clicked":
                self._collapse_block()
        elif button_name == "footer_btn_save":
            if action == "clicked":
                self._data_dict["save"] = True
                self._save_record_and_data()
                main_dict = {
                    "name": "win_block",
                    "action": "block_saved",
                    "id": self._active_record_id,
                    "closed": self._data_dict["save"]
                }
                self._main_window.events(main_dict)
        elif button_name == "footer_btn_add_new":
            if action == "clicked":
                main_dict = {
                    "name": "win_block",
                    "action": "open_new_block"
                }
                self._main_window.events(main_dict)
        elif button_name == "footer_btn_add_new_image":
            if action == "clicked":
                self.data_block.block_event("win_block", "add_image")

    def _close_block(self, save_data: bool = True, fast_close: bool = False):
        if not fast_close:
            info = utility_cls.BlockAnimationInformation(self._stt, load_mode="close", start_height=self.height(), stop_height=0)
            animation = utility_cls.BlockAnimation(info, self)

        self._parent_widget.layout().removeWidget(self)
        # Save data
        if save_data:
            self._save_record_and_data()
        # Send message to main win
        main_dict = {
            "name": "win_block",
            "action": "block_saved",
            "id": self._active_record_id,
            "closed": self._data_dict["save"]
        }
        self._main_window.events(main_dict)
        # Remove block
        self._dont_save_on_close_event = True
        
        self.close()

    def action_win_block_controls_frame_right_click(self):
        if self.collapsed:
            disable = 3
        else:
            disable = 2

        menu_dict = {
            "position": QCursor().pos(),
            "disabled": [disable],
            "separator": [3],
            "items":[
                [
                    1,
                    self.getl("block_titlebar_context_info_text"),
                    self.getl("block_titlebar_context_info_desc"),
                    True,
                    [],
                    self.getv("messagebox_information_icon_path")
                ],
                [
                    2,
                    self.getl("block_titlebar_context_expand_text"),
                    self.getl("block_titlebar_context_expand_desc"),
                    True,
                    [],
                    self.getv("win_block_control_btn_expand_icon_path")
                ],
                [
                    3,
                    self.getl("block_titlebar_context_collapse_text"),
                    self.getl("block_titlebar_context_collapse_desc"),
                    True,
                    [],
                    self.getv("win_block_control_btn_collapse_icon_path")
                ],
                [
                    4,
                    self.getl("block_titlebar_context_close_text"),
                    self.getl("block_titlebar_context_close_desc"),
                    True,
                    [],
                    self.getv("win_block_control_btn_close_icon_path")
                ]
           ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self)
        self.get_appv("log").write_log("WinBlock. Title Frame. Mouse right click. Context menu show.")
        result = self.get_appv("menu")["result"]
        if result == 1:
            self._send_msg_to_main_win()
            self.show_block_info_message_box()
        elif result == 2:
            self._expand_block()
        elif result == 3:
            self._collapse_block()
        elif result == 4:
            self._close_block()

    def show_block_info_message_box(self):
        db_record = db_record_cls.Record(self._stt, self._active_record_id)
        text = self.getl("block_titlebar_msgbox_text")
        text = text.replace("#0", f"( {str(self._active_record_id)} )")
        text = text.replace("#1", self._data_dict["record_date"])
        if self._data_dict["name"]:
            text = text.replace("#2", self._data_dict["name"])
        else:
            text = text.replace("#2", "---")
        text = text.replace("#3", db_record.RecordCreatedAt)
        text = text.replace("#4", db_record.RecordUpdatedAt)
        
        tag_text = ""
        db_tag = db_tag_cls.Tag(self._stt)
        for tag in self._data_dict["tag"]:
            tag_info = db_tag.populate_values(tag)
            tag_text += db_tag.TagNameTranslated + ", "
        tag_text = tag_text.strip().strip(",")
        if tag_text:
            text = text.replace("#5", tag_text)
        else:
            text = text.replace("#5", "---")
        text = text.replace("#6", str(len(self._data_dict["body"])))
        body_text = self._data_dict["body"]
        replace_char = ["!", "?", ".", "\n", ",", ":", ";"]
        for i in replace_char:
            body_text = body_text.replace(i, " ")
        body_words = [x for x in body_text.split(" ") if x != ""]
        text = text.replace("#7", str(len(body_words)))
        
        msg_dict = {
            "title": self.getl("block_titlebar_msgbox_title"),
            "text": text,
            "icon_path": self.getv("main_win_icon_path"),
            "btn_ok_text": self.getl("close"),
            "position": QCursor().pos(),
            "pos_center": True
        }
        utility_cls.MessageInformation(self._stt, self, msg_dict)
        self.get_appv("log").write_log(f"WinBlock. Info message show. Record ID: {self._active_record_id}")

    def _send_msg_to_main_win(self):
        main_dict = {
            "name": "win_block",
            "action": "cm"
        }
        if self._main_window is not None:
            self._main_window.events(main_dict)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not self._dont_save_on_close_event:
            self._save_record_and_data()
        return super().closeEvent(a0)

    def _save_record_and_data(self):
        if self._active_record_id in self.get_appv("calculator"):
            self.block_event("save_func", "calc_stop")
        
        record = db_record_cls.Record(self._stt, self._active_record_id)
        record_data = db_record_data_cls.RecordData(self._stt, self._active_record_id)
        time_cls = utility_cls.DateTime(self._stt)
        time_now = time_cls.get_current_date_and_time(with_long_names=False)
        
        # Populate data and save record
        record.RecordDate = self._data_dict["record_date"]
        record.RecordName = self._data_dict["name"]
        record.RecordBody = self._data_dict["body"]
        record.RecordBodyHTML = self._data_dict["body_html"]
        record.RecordUpdatedAt = time_now
        if self._data_dict["save"]:
            record.RecordDraft = 0
            self._data_dict["draft"] = 0
        else:
            record.RecordDraft = 1
            self._data_dict["draft"] = 1
        self._data_dict["need_update"] = False
        record.save_record()

        # Save record data
        # First we need to remove the extra fields from the dictionary
        dict_for_record_data = copy.deepcopy(self._data_dict)
        dict_for_record_data.pop("record_date")
        dict_for_record_data.pop("name")
        dict_for_record_data.pop("body")
        dict_for_record_data.pop("body_html")
        dict_for_record_data.pop("updated")
        dict_for_record_data.pop("draft")
        dict_for_record_data.pop("save")
        dict_for_record_data.pop("need_update")
        # Update record data
        record_data.update_record_data(dict_for_record_data)

    def _collapse_block(self):
        if not self.collapsed:
            h = self.win_block_controls.height() + 3
            self.collapsed = True
            info = utility_cls.BlockAnimationInformation(self._stt, load_mode="collapse", start_height=self.height(), stop_height=h)
            utility_cls.BlockAnimation(info, self)
            self.data_block.setVisible(False)

    def _expand_block(self):
        if self.collapsed:
            h = self.win_block_controls.height() + self.data_block.height()
            h += self.contentsMargins().top() + self.contentsMargins().bottom()
            h += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
            h += self.getv("win_block_plus_height_to_ensure_visibility")
            self.collapsed = False
            self.data_block.setVisible(True)
            info = utility_cls.BlockAnimationInformation(self._stt, load_mode="expand", start_height=self.height(), stop_height=h)
            utility_cls.BlockAnimation(info, self)

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])

    def _define_apperance(self):
        # Win Block
        self.setFrameShape(self.getv("win_block_frame_shape"))
        self.setFrameShadow(self.getv("win_block_frame_shadow"))
        self.setLineWidth(self.getv("win_block_line_width"))
        self.setStyleSheet(self.getv("win_block_stylesheet"))
        self.setEnabled(self.getv("win_block_enabled"))
        self.layout().setSpacing(self.getv("win_block_layout_spacing"))


class DataBlock(QFrame):
    def __init__(self, parent_widget: QFrame, settings: settings_cls.Settings, record_id: int, data_dict: dict, main_win = None, *args, **kwargs) -> None:
        super().__init__(parent_widget, *args, **kwargs)
        # Define record_id (database ID for record)
        self._active_record_id = record_id

        # Define Parent Widget
        self._parent_widget = parent_widget

        # Define record data dictionary (contains tags, location, contact...)
        self._data_dict = data_dict

        # Define user object
        # self._user: users_cls.User = settings.app_setting_get_value("user")
        # Define log object
        # self._log: log_cls.Log = settings.app_setting_get_value("log")
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define signals object
        self.signals: utility_cls.Signals = self.get_appv("signal")

        # Set margins
        self._set_margins(self, "data_block")
        self.setLayout(QVBoxLayout(self))
        self._set_margins(self.layout(), "data_block_layout")

        # Define Header, Body and Footer
        self.header = block_widgets_cls.Frame(self, self._stt, self._active_record_id, "header", self._data_dict, main_win=main_win)
        self.body = block_widgets_cls.Frame(self, self._stt, self._active_record_id, "body", self._data_dict, main_win=main_win)
        self.footer = block_widgets_cls.Frame(self, self._stt, self._active_record_id, "footer", self._data_dict, main_win=main_win)

        # Define apperance
        self._define_apperance()

        # Add this frame to parent layout
        self._parent_widget.layout().addWidget(self)

        # Set Height
        height = self.header.height() + self.body.height() + self.footer.height()
        height += self.contentsMargins().top() + self.contentsMargins().bottom()
        height += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
        self.setFixedHeight(height)
        self._check_user_height()

    def _check_user_height(self):
        # Check is there app setting 
        if "user_resize_block" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("user_resize_block", {}, save_to_file=True)
        
        # Remove not needed keys
        if not self.getv("remember_user_resize_block_info_for_all_blocks"):
            db_record = db_record_cls.Record(self._stt)
            drafts = db_record.get_draft_records()
            drafts_id_list = []
            for draft in drafts:
                drafts_id_list.append(str(draft[0]))
            keys_to_remove = []
            for record in self.get_appv("user_resize_block"):
                if record not in drafts_id_list:
                    keys_to_remove.append(record)
            for key in keys_to_remove:
                self.get_appv("user_resize_block").pop(key)
        
        # Set User Defined Size
        if str(self._active_record_id) not in self.get_appv("user_resize_block"):
            return
        
        diff = self.get_appv("user_resize_block")[str(self._active_record_id)]
        self.setFixedHeight(self.height() + diff)
        self.body._set_user_defined_height(diff)

    # Block Event Slot
    def block_event(self, name, event, detail: dict = None):
        if name == "win_block":
            if event == "header_update_buttons":
                self.header.header_update_button_list()
            if event == "txt_box_height":
                self.body.block_event("data_block", event, detail)
            if event == "set_txt_box_height":
                self.body.block_event("data_block", event, detail)
            if event == "add_image":
                self.body.block_event("data_block", event, detail)
            if event == "add_files":
                self.body.block_event("data_block", event, detail)
            if event == "txt_editor_command":
                self.body.block_event("data_block", event, detail)
            if event == "auto_add_images":
                self.body.block_event("data_block", event, detail)
            if event == "calc_stop":
                self.body.block_event("data_block", event, detail)
                
        self._parent_widget.block_event(name, event, detail)

    def btn_clicked(self, button_name, action):
        self._parent_widget.btn_clicked(button_name, action)

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])

    def _define_apperance(self):
        self.setFrameShape(self.getv("data_block_frame_shape"))
        self.setFrameShadow(self.getv("data_block_frame_shadow"))
        self.setLineWidth(self.getv("data_block_line_width"))
        self.setStyleSheet(self.getv("data_block_stylesheet"))
        self.setEnabled(self.getv("data_block_enabled"))
        self.setVisible(self.getv("data_block_visible"))
        self.layout().setSpacing(self.getv("data_block_layout_spacing"))
