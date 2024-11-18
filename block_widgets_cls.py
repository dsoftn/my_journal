from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QGridLayout, QWidget,
                             QSpacerItem, QSizePolicy, QLabel, QHBoxLayout, QApplication)
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QMouseEvent, QCursor, QPixmap, QPainter, QColor, QDrag
from PyQt5.QtCore import QSize, Qt, QTimer, QCoreApplication, QRect, QMimeData
from PyQt5 import QtGui

import os
import time

import settings_cls
import log_cls
import users_cls
import db_record_cls
import utility_cls
import db_tag_cls
import text_handler_cls
import db_media_cls
import tag_cls
import qwidgets_util_cls
import timer_cls
from timer_cls import SingleShotTimer
import UTILS


class Frame(QFrame):
    def __init__(self, parent_widget: QFrame, settings: settings_cls.Settings, record_id: int, my_name: str, data_dict: dict, main_win = None, *args, **kwargs) -> None:
        super().__init__(parent_widget, *args, **kwargs)
        # Define variables
        self._parent_widget = parent_widget
        self._active_record_id = record_id
        self._my_name = my_name
        self._data_dict = data_dict
        self.tags = data_dict["tag"]
        # Define user object
        self._user: users_cls.User = settings.app_setting_get_value("user")
        # Define log object
        self._log: log_cls.Log = settings.app_setting_get_value("log")
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value
        
        self.auto_add_images_frame = None  # The variable must be set before the txtbox is created
        
        # Main_win 
        self._main_win = main_win
        # Set margins for frame
        self._set_margins(self, self._my_name)
        # Define layout and set margins for layout
        self.setLayout(QGridLayout(self))
        self._set_margins(self.layout(), f"{self._my_name}_layout")
        # Define apperance
        self._define_apperance()
        # Add this frame to parent layout
        self._parent_widget.layout().addWidget(self)
        # Internal clipboard
        self._clip: utility_cls.Clipboard = self.get_appv("cb")

        # Add frame content
        if self._my_name == "win_block_controls":
            self._win_block_controls_content()
        elif self._my_name == "header":
            self._header_content()
        elif self._my_name == "footer":
            self._footer_content()
        elif self._my_name == "body":
            self._body_content(main_win)

        # If Frame is 'body' then load AutoAddImages class
        if self._my_name == "body":
            self._auto_add_images_active = False
            self.auto_add_images_frame = utility_cls.AutoAddImageFrame(self._stt, self.body_text_box)
            self.sound_image_added = UTILS.SoundUtility(self.getv("block_body_auto_added_image_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
            self.sound_image_add_error = UTILS.SoundUtility(self.getv("block_body_auto_added_image_error_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
            self.sound_pop_up = UTILS.SoundUtility(self.getv("notification_pop_up_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))

        # Connect Signals with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        if self._my_name == "body":
            self.get_appv("clipboard").changed.connect(self._clipboard_changed)

        if self._my_name == "footer":
            self.setMouseTracking(True)
            self.mouseMoveEvent = self.mouse_move_event
    
    def mouse_move_event(self, e):
        self.block_event(self._my_name, "set_pointer_to_arrow")

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.get_appv("cm").remove_all_context_menu()

        if a0.button() == Qt.LeftButton:
            # text = f'{self.getl("cursor_drag_block")}: {self._active_record_id}'
            # font = QFont("Arial", 12)
            # fm = QFontMetrics(font)
            # text_width = fm.width(text)
            # text_height = fm.height()
            # cursor_image = QPixmap(text_width, text_height)
            # cursor_image.fill(Qt.transparent)
            # painter = QPainter(cursor_image)
            # painter.setPen(QColor("#55ffff"))
            # painter.setFont(font)
            # painter.drawText(QRect(0, 0, text_width, text_height), Qt.AlignCenter, text)
            # painter.end()
            # cursor = QCursor(cursor_image, hotX=int(text_width / 2), hotY=int(text_height / 2))
            # QApplication.setOverrideCursor(cursor)

            self.get_appv("cb").set_drag_data(self._active_record_id, "block")
            
            mime_data = QMimeData()
            mime_data.setText(str(self._active_record_id))
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)

            self._parent_widget.block_event(self._my_name, "mouse_press_left")
        elif a0.button() == Qt.RightButton:
            self._parent_widget.block_event(self._my_name, "mouse_press_right")
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        # QApplication.restoreOverrideCursor()

        return super().mouseReleaseEvent(a0)

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._parent_widget.block_event(self._my_name, "mouse_double_clicked")
        return super().mouseDoubleClickEvent(a0)

    def block_event(self, name: str, action: str, detail: dict = None):
        self._parent_widget.block_event(name, action, detail)
        
        if name == "data_block":
            if action == "txt_box_height":
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if widget is not None:
                        if widget._my_name == "body_txt_box":
                            detail["height"] = widget.height()
                            detail["frame_height"] = self.height()
            if action == "set_txt_box_height":
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if widget is not None:
                        if widget._my_name == "body_txt_box":
                            self.setFixedHeight(detail["set_frame_height"])
                            widget.setFixedHeight(detail["set_height"])
            if action == "txt_editor_command":
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if widget is not None:
                        if widget._my_name == "body_txt_box":
                            widget.detection_btn_command(detail)
            if action == "add_image":
                self._add_image()
            if action == "add_files":
                self._add_files()
            if action == "auto_add_images":
                self._auto_add_images_mode()
            if action == "calc_stop":
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if widget is not None:
                        if widget._my_name == "body_txt_box":
                            widget.stop_calculator()
        if name == "auto_add_images_frame":
            if action == "close":
                self._auto_add_images_mode_exit()
        if name == "body_txt_box":
            if action == "auto_add_images":
                self._auto_add_images_mode()
        if name == "win_block":
            if action == "titlebar_msg":
                self._titlebar_msg(detail)

    def _titlebar_msg(self, detail: dict):
        for i in range(self.layout().count()):
            button = self.layout().itemAt(i).widget()
            if button is not None:
                if button._my_name == "win_block_control_btn_msg":
                    button.update_msg(detail)
                    break

    def _clipboard_changed(self):
        if not self._auto_add_images_active:
            return

        # Try to add single image        
        result = self._auto_image_add()

        if result == "":
            UTILS.LogHandler.add_log_record("#1 record ID: #2. #3 added single image.", ["WinBlock", self._active_record_id, "AutoImageAdd"])
            return

        # Try to load multiple images
        self.auto_add_images_frame.update_me(None, self.getl("auto_add_image_frame_lbl_info_starting_multi_add_text"), is_error=False)
        self._auto_multi_image_add()
        self.auto_add_images_frame.update_me(None, self.getl("auto_add_image_frame_lbl_info_start_text"), is_error=False)

    def _auto_multi_image_add(self):
        # Check is there multiple images to add
        file_util = utility_cls.FileDialog()

        # Search for urls in text
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

        if not urls:
            return

        # Show the user a selection dialog to select the images they want to add
        UTILS.LogHandler.add_log_record("#1 record ID: #2. #3 triggered multiple image selection dialog.", ["WinBlock", self._active_record_id, "AutoImageAdd"])
        select_dict = {
            "title": self.getl("multi_urls_selection_title"),
            "multi-select": False,
            "checkable": True,
            "items": []
        }
        for url in urls:
            desc = f'<img src="{url}" alt="Image" width="300">'
            select_dict["items"].append([url, url, desc, False, False, []])
        
        self.sound_pop_up.play()
        utility_cls.Selection(self._stt, self, selection_dict=select_dict)
        urls = self.get_appv("selection")["result"]

        # If the user has not selected any image, return
        if not urls:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. #3: Image selection aborted.\nUser did not select any image.", ["WinBlock", self._active_record_id, "AutoImageAdd"])
            return

        not_added = []

        for idx, url in enumerate(urls):
            # Notify the user of progress
            msg = self.getl("multi_urls_user_msg_text").replace("#1", str(idx + 1)).replace("#2", str(len(urls)))
            self.auto_add_images_frame.update_progress(msg)
            
            # If the user has stopped adding images, exit the loop
            if not self._auto_add_images_active:
                break

            result = self._auto_image_add(img_source=url)
            if result:
                not_added.append(result)

        # Remove the progress message
        self.auto_add_images_frame.update_progress()

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
        UTILS.LogHandler.add_log_record("#1 record ID: #2. #3 added #4 images.\nFor #5 images url cannot be resolved.", ["WinBlock", self._active_record_id, "AutoImageAdd", len(urls) - len(not_added), len(not_added)])

    def _auto_image_add(self, img_source: str = None) -> str:
        self.auto_add_images_frame.update_me(None, self.getl("auto_add_image_frame_lbl_info_working_text"), is_error=False)

        silent_load = utility_cls.SilentPictureAdd(self._stt)
        if img_source is None:
            result = silent_load.add_image()
        else:
            result = silent_load.add_image(source=img_source)

        if result is None:
            self.sound_image_add_error.play()
            self.auto_add_images_frame.update_me(result, self.getl("auto_add_image_frame_lbl_info_error_text"), is_error=False)
            if img_source:
                txt = f'{img_source}  {self.getl("auto_adding_images_not_added_reason_text")}: {self.getl("auto_adding_images_not_added_reason_load_error_text")}'
                return txt
            else:
                return "Error"
        
        # Add Image
        for j in range(self.horizontal_grid.count()):
            if self.horizontal_grid.itemAt(j).widget()._media_id == result:
                self.sound_image_add_error.play()
                self.auto_add_images_frame.update_me(result, self.getl("auto_add_image_frame_lbl_info_exists_text"), is_error=True)
                return ""

        self.horizontal_grid.parent().setFixedWidth(self.horizontal_grid.parent().width() + (self.getv("block_image_thumb_size") + 10))
        self.horizontal_grid.addWidget(ImageItem(self._stt, self, result))
        self._data_dict["media"].append(result)
        self.block_event("body", "image_added")
        self.sound_image_added.play()
        self.auto_add_images_frame.update_me(result, self.getl("auto_add_image_frame_lbl_info_loaded_text"), is_error=False)

        return ""

    def _auto_add_images_mode(self):
        if self._auto_add_images_active == True:
            self.auto_add_images_frame.setVisible(False)
            self._auto_add_images_active = False
            UTILS.LogHandler.add_log_record("#1 record ID: #2. #3 deactivated.", ["WinBlock", self._active_record_id, "AutoImageAdd"])
        else:
            self.auto_add_images_frame.setVisible(True)
            self.auto_add_images_frame.update_me()
            self._auto_add_images_active = True
            UTILS.LogHandler.add_log_record("#1 record ID: #2. #3 activated.", ["WinBlock", self._active_record_id, "AutoImageAdd"])

    def _auto_add_images_mode_exit(self):
        if self.auto_add_images_frame is None:
            return
        self.auto_add_images_frame.setVisible(False)
        self._auto_add_images_active = False

    def _add_files(self, file_ids: list = None):
        UTILS.LogHandler.add_log_record("#1 record ID: #2. About to add files in block.", ["WinBlock", self._active_record_id])
        if file_ids is None:
            utility_cls.FileAdd(self._stt, self._main_win)
            result = self.get_appv("file_add")
        else:
            result = file_ids

        # Add Files
        db_media = db_media_cls.Files(self._stt)
        if result:
            for i in result:
                db_media.load_file(file_id=i)
                for j in range(self.horizontal_grid.count()):
                    if self.horizontal_grid.itemAt(j).widget()._media_id == i:
                        msg_dict = {
                            "title": self.getl("block_add_file_already_exist_title"),
                            "text": self.getl("block_add_file_already_exist") + f"\n{db_media.file_name}\n{db_media.file_file}",
                            "icon_path": self.getv("file_add_win_icon_path")
                        }
                        utility_cls.MessageInformation(self._stt, self._main_win, msg_dict, app_modal=True)
                        break
                else:
                    self.horizontal_grid.parent().setFixedWidth(self.horizontal_grid.parent().width() + (self.getv("block_image_thumb_size") + 10))
                    self.horizontal_grid.addWidget(ImageItem(self._stt, self, i))
                    self._data_dict["files"].append(i)
                    self.block_event("body", "file_added")
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Files added in block.", ["WinBlock", self._active_record_id])
        else:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. No files selected.", ["WinBlock", self._active_record_id])

    def _add_image(self, image_ids: list = None):
        UTILS.LogHandler.add_log_record("#1 record ID: #2. About to add image in block.", ["WinBlock", self._active_record_id])
        # Select image to add
        if image_ids is None:
            result = []
            utility_cls.PictureAdd(self._stt, self, result)
        else:
            result = image_ids
        # Add Image
        if result:
            for i in result:
                for j in range(self.horizontal_grid.count()):
                    if self.horizontal_grid.itemAt(j).widget()._media_id == i:
                        ntf_dict = {
                            "title": self.getl("block_add_image_already_exist_title"),
                            "text": self.getl("block_add_image_already_exist"),
                            "icon": self.getv("picture_add_win_icon_path"),
                            "timer": 6000,
                            "show_close": True
                        }
                        utility_cls.Notification(self._stt, self, ntf_dict)
                        break
                else:
                    self.horizontal_grid.parent().setFixedWidth(self.horizontal_grid.parent().width() + (self.getv("block_image_thumb_size") + 10))
                    self.horizontal_grid.addWidget(ImageItem(self._stt, self, i))
                    self._data_dict["media"].append(i)
                    self.block_event("body", "image_added")
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Image added in block.", ["WinBlock", self._active_record_id])
        else:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. No image selected.", ["WinBlock", self._active_record_id])

    def _set_user_defined_height(self, diff: int):
        self.setFixedHeight(self.height() + diff)
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                if widget._my_name == "body_txt_box":
                    widget.setFixedHeight(widget.height() + diff)

    def btn_clicked(self, button_name, action):
        self._parent_widget.btn_clicked(button_name, action)

    def header_update_button_list(self):
        self.tags = self._data_dict["tag"]
        self._header_content()

    def _body_content(self, main_win):
        # Add TextBox
        self.body_text_box = TextBox(self, self._stt, self._active_record_id, "body_txt_box", self._data_dict, main_win)
        self.layout().addWidget(self.body_text_box, 0, 0)
        body_height = 0
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                if body_height < widget.height():
                    body_height = widget.height()
        body_height += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
        body_height += self.contentsMargins().top() + self.contentsMargins().bottom()
        body_height += 15

        # Add area with images and files
        area = ScrollAreaItem(self)
        widget = QWidget(self)
        self.horizontal_grid = QHBoxLayout(widget)
        widget.setLayout(self.horizontal_grid)
        area.setWidget(widget)
        self.layout().addWidget(area, 1, 0)
        
        for media_id in self._data_dict["media"]:
            self.horizontal_grid.addWidget(ImageItem(self._stt, self, media_id))

        for media_id in self._data_dict["files"]:
            self.horizontal_grid.addWidget(ImageItem(self._stt, self, media_id))

        number_of_items = len(self._data_dict["media"]) + len(self._data_dict["files"])

        widget.setFixedHeight(self.getv("block_image_thumb_size") + 10)
        if number_of_items > 1:
            block_image_widget_width = (number_of_items - 1) * self.getv("block_image_widget_layout_spacing")
        else:
            block_image_widget_width = 0
        block_image_widget_width += number_of_items * (self.getv("block_image_thumb_size") + 10)
        widget.setFixedWidth(block_image_widget_width)
        area.setFixedHeight(widget.height() + 25)
        body_height += area.height()

        # Set area apperance
        area.setStyleSheet(self.getv("block_image_area_stylesheet"))
        self._set_margins(area, "block_image_area")
        widget.setStyleSheet(self.getv("block_image_area_widget_stylesheet"))
        self._set_margins(widget, "block_image_area_widget")
        self._set_margins(self.horizontal_grid, "block_image_widget_layout")
        self.horizontal_grid.setSpacing(self.getv("block_image_widget_layout_spacing"))
        
        self.setFixedHeight(body_height)

    def _footer_content(self):
        grid_pos_count = 0

        btn_name = "footer_btn_save"
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos_count)
        grid_pos_count += 1

        btn_name = "footer_btn_saved"
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos_count)
        grid_pos_count += 1

        btn_name = "footer_btn_delete"
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos_count)
        grid_pos_count += 1

        btn_name = "footer_btn_add_new_image"
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos_count)
        grid_pos_count += 1

        btn_name = "footer_btn_add_new"
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos_count)
        grid_pos_count += 1

        btn_name = "footer_btn_detection"
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos_count)
        grid_pos_count += 1

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().addItem(spacer, 0, grid_pos_count)
        grid_pos_count += 1
        footer_height = 0
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                if footer_height < widget.height():
                    footer_height = widget.height()
        footer_height += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
        footer_height += self.contentsMargins().top() + self.contentsMargins().bottom()
        self.setFixedHeight(footer_height)

    def _header_content(self):
        for i in range(self.layout().count()):
            item = self.layout().takeAt(0).widget()
            if item is not None:
                item.close()

        self.tags.sort()
        tag = db_tag_cls.Tag(self._stt)
        grid_pos = 0
        for tag_id in self.tags:
            tag.populate_values(tag_id)
            if tag.TagUserDefinded == 0:
                if tag_id == 1:
                    btn_name = "header_btn_diary"
                else:
                    btn_name = "header_btn_tag"
            else:
                btn_name = "header_btn_user"
            self.layout().addWidget(Button(self, self._stt, self._active_record_id, btn_name, tag_id=tag_id, data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos, alignment=Qt.AlignLeft|Qt.AlignVCenter)
            grid_pos += 1
        # Button ADD
        self.layout().addWidget(Button(self, self._stt, self._active_record_id, "header_btn_add", data_dict=self._data_dict, main_win=self._main_win), 0, grid_pos, alignment=Qt.AlignLeft|Qt.AlignVCenter)
        grid_pos += 1

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().addItem(spacer, 0, grid_pos)
        header_height = 0
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                if header_height < widget.height():
                    header_height = widget.height()
        header_height += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
        header_height += self.contentsMargins().top() + self.contentsMargins().bottom()
        self.setFixedHeight(header_height)

    def _win_block_controls_content(self):
        # Add buttons
        button_count = 0
        btn_day: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_day", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_day, 0, button_count, alignment=Qt.AlignLeft|Qt.AlignVCenter)
        button_count += 1
        btn_date: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_date", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_date, 0, button_count, alignment=Qt.AlignLeft|Qt.AlignVCenter)
        button_count += 1
        btn_name: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_name", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_name, 0, button_count, alignment=Qt.AlignLeft|Qt.AlignVCenter)
        button_count += 1
        btn_msg: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_msg", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_msg, 0, button_count, alignment=Qt.AlignLeft|Qt.AlignVCenter)
        button_count += 1
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().addItem(spacer, 0, button_count)

        button_count += 1
        btn_close: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_collapse", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_close, 0, button_count, alignment=Qt.AlignRight|Qt.AlignVCenter)
        button_count += 1
        btn_close: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_expand", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_close, 0, button_count, alignment=Qt.AlignRight|Qt.AlignVCenter)
        button_count += 1
        btn_close: QPushButton = Button(self, self._stt, self._active_record_id, "win_block_control_btn_close", data_dict=self._data_dict, main_win=self._main_win)
        self.layout().addWidget(btn_close, 0, button_count, alignment=Qt.AlignRight|Qt.AlignVCenter)

        # Adjust frame height with height of buttons
        win_block_height = 0
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                if win_block_height < widget.height():
                    win_block_height = widget.height()
        win_block_height += self.layout().contentsMargins().top() + self.layout().contentsMargins().bottom()
        win_block_height += self.contentsMargins().top() + self.contentsMargins().bottom()
        self.setFixedHeight(win_block_height)

    def image_item_double_click(self, media_id: int, image_item):
        if image_item._i_am_image_item:
            media_ids = []
            for i in range(self.horizontal_grid.count()):
                media_ids.append(self.horizontal_grid.itemAt(i).widget()._media_id)

            UTILS.LogHandler.add_log_record("#1 record ID: #2. Image item in block double clicked.", ["WinBlock", self._active_record_id])
            utility_cls.PictureView(self._stt, self, media_ids=media_ids, start_with_media_id=media_id)
        else:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. File item in block double clicked.", ["WinBlock", self._active_record_id])
            utility_cls.FileInfo(self._stt, self, media_id)

    def scroll_area_item_right_click(self):
        UTILS.LogHandler.add_log_record("#1 record ID: #2. Image/File area in block right mouse click.\nContext menu triggered.", ["WinBlock", self._active_record_id])
        disab = []
        if not self._data_dict["media"]:
            disab.append(10)
            disab.append(20)
        if not self._clip.number_of_files_in_clip:
            disab.append(55)
        if not self._clip.number_of_images_in_clip:
            disab.append(50)
        if self._clip.is_clip_empty():
            disab.append(60)

        menu_dict = {
            "position": QCursor().pos(),
            "disabled": disab,
            "separator": [45],
            "items": [
                [
                    10,
                    self.getl("block_area_item_menu_view_image_text"),
                    self.getl("block_area_item_menu_view_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    20,
                    self.getl("block_area_item_menu_view_all_images_text"),
                    self.getl("block_area_item_menu_view_all_images_tt"),
                    True,
                    [],
                    None
                ],
                [
                    30,
                    self.getl("block_image_item_menu_add_new_image_text"),
                    self.getl("block_image_item_menu_add_new_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    40,
                    self.getl("block_txt_box_menu_add_file_text"),
                    self.getl("block_txt_box_menu_add_file_tt"),
                    True,
                    [],
                    None
                ],
                [
                    45,
                    self.getl("block_image_item_menu_start_auto_add_image_text"),
                    self.getl("block_image_item_menu_start_auto_add_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    50,
                    self.getl("image_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_images(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    55,
                    self.getl("file_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_files(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    60,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]
        
        if not result:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser canceled. Menu closed with no selection.", ["WinBlock", self._active_record_id])
            return
        
        media_ids = []
        for i in range(self.horizontal_grid.count()):
            media_ids.append(self.horizontal_grid.itemAt(i).widget()._media_id)
        
        if result == 10:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Show single image"])
            utility_cls.PictureView(self._stt, self, media_ids=media_ids)
        elif result == 20:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Browse all block images"])
            utility_cls.PictureBrowse(self._stt, self, self._data_dict["media"])
        elif result == 30:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add image to block"])
            self._add_image()
        elif result == 40:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add file to block"])
            self._add_files()
        elif result == 45:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Auto add images"])
            self.block_event(self._my_name, "auto_add_images", None)
            self.get_appv("signal").block_text_give_focus(self._active_record_id)
        elif result == 50:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add images from clipboard"])
            self._add_image(image_ids=self._clip.get_paste_images_ids())
        elif result == 55:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add files from clipboard"])
            self._add_files(file_ids=self._clip.get_paste_files_ids())
        elif result == 60:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image/file area context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Clear clipboard"])
            self._clip.clear_clip()

    def image_item_left_click(self, media_id: int):
        for i in range(self.horizontal_grid.count()):
            widget = self.horizontal_grid.itemAt(i).widget()
            if widget._media_id == media_id:
                widget.you_are_marked(True)
            else:
                widget.you_are_marked(False)

    def image_item_right_click(self, media_id: int, image_item):
        if image_item._i_am_image_item:
            self._image_item_right_click_media_item(media_id, image_item)
        else:
            self._image_item_right_click_file_item(media_id, image_item)

    def _image_item_right_click_file_item(self, media_id: int, image_item):
        UTILS.LogHandler.add_log_record("#1 record ID: #2. File item in block right mouse click.\nContext menu triggered.", ["WinBlock", self._active_record_id])
        db_media = db_media_cls.Files(self._stt, media_id)
        file_util = utility_cls.FileDialog(self._stt)
        file_info = file_util.FileInfo(self._stt, db_media.file_file)
        
        disab = []
        if not self._clip.number_of_files_in_clip:
            disab.append(55)
        if not self._clip.number_of_images_in_clip:
            disab.append(50)
        if self._clip.is_clip_empty():
            disab.append(80)

        menu_dict = {
            "position": QCursor().pos(),
            "separator": [30, 40, 55],
            "disabled": disab,
            "items": [
                [
                    10,
                    self.getl("block_image_item_menu_view_file_text"),
                    self.getl("block_image_item_menu_view_file_tt"),
                    True,
                    [],
                    self.getv("file_info_win_icon_path")
                ],
                [
                    20,
                    self.getl("block_image_item_menu_open_file_text"),
                    self.getl("block_image_item_menu_open_file_tt"),
                    True,
                    [],
                    file_info.icon()
                ],
                [
                    30,
                    self.getl("block_txt_box_menu_add_file_text"),
                    self.getl("block_txt_box_menu_add_file_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_add_file_icon_path")
                ],
                [
                    40,
                    self.getl("block_image_item_menu_remove_file_text"),
                    self.getl("block_image_item_menu_remove_file_tt"),
                    True,
                    [],
                    self.getv("block_image_item_menu_remove_file_icon_path")
                ],
                [
                    50,
                    self.getl("image_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_images(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    55,
                    self.getl("file_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_files(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    60,
                    self.getl("file_menu_copy_text"),
                    self.getl("file_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    70,
                    self.getl("file_menu_add_to_clip_text"),
                    self.getl("file_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    80,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]
        
        if result == 10:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Show file information"])
            utility_cls.FileInfo(self._stt, self, media_id)
        elif result == 20:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Show file with default app."])
            abs_file_path = file_info.absolute_path()
            try:
                os.startfile(abs_file_path)
            except Exception as e:
                msg_dict = {
                    "title": self.getl("block_image_item_menu_open_file_error_title"),
                    "text": self.getl("block_image_item_menu_open_file_error_text").replace("#1", db_media.file_file)
                }
                UTILS.LogHandler.add_log_record("#1 record ID: #2. Error in showing file with default app.\n#3", ["WinBlock", self._active_record_id, e], warning_raised=True)
                utility_cls.MessageInformation(self._stt, self, msg_dict, app_modal=True)
        elif result == 30:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add file(s)"])
            self._add_files()
        elif result == 40:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Remove file"])
            self.remove_image_item(media_id)
        elif result == 50:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add image(s) from clipboard"])
            self._add_image(image_ids=self._clip.get_paste_images_ids())
        elif result == 55:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add file(s) from clipboard"])
            self._add_files(file_ids=self._clip.get_paste_files_ids())
        elif result == 60:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Copy file to clipboard"])
            self._clip.copy_to_clip(media_id)
        elif result == 70:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add file to clipboard"])
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif result == 80:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block file context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Clear clipboard"])
            self._clip.clear_clip()

    def _image_item_right_click_media_item(self, media_id: int, image_item):
        UTILS.LogHandler.add_log_record("#1 record ID: #2. Image item in block right mouse click.\nContext menu triggered.", ["WinBlock", self._active_record_id])
        disab = []
        if not self._clip.number_of_files_in_clip:
            disab.append(55)
        if not self._clip.number_of_images_in_clip:
            disab.append(50)
        if self._clip.is_clip_empty():
            disab.append(80)

        menu_dict = {
            "position": QCursor().pos(),
            "separator": [15, 40, 55],
            "disabled": disab,
            "items": [
                [
                    10,
                    self.getl("block_image_item_menu_view_image_text"),
                    self.getl("block_image_item_menu_view_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    13,
                    self.getl("picture_view_menu_image_info_text"),
                    self.getl("picture_view_menu_image_info_tt"),
                    True,
                    [],
                    self.getv("picture_info_win_icon_path")
                ],
                [
                    15,
                    self.getl("block_image_item_menu_view_all_images_text"),
                    self.getl("block_image_item_menu_view_all_images_tt"),
                    True,
                    [],
                    None
                ],
                [
                    20,
                    self.getl("block_image_item_menu_remove_image_text"),
                    self.getl("block_image_item_menu_remove_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    30,
                    self.getl("block_image_item_menu_add_new_image_text"),
                    self.getl("block_image_item_menu_add_new_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    40,
                    self.getl("block_image_item_menu_start_auto_add_image_text"),
                    self.getl("block_image_item_menu_start_auto_add_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    50,
                    self.getl("image_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_images(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    55,
                    self.getl("file_menu_paste_clip_text"),
                    self._clip.get_tooltip_hint_for_files(),
                    True,
                    [],
                    self.getv("paste_icon_path")
                ],
                [
                    60,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    70,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    80,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]
        
        media_ids = []
        for i in range(self.horizontal_grid.count()):
            media_ids.append(self.horizontal_grid.itemAt(i).widget()._media_id)
        
        if result == 10:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Show image"])
            utility_cls.PictureView(self._stt, self, media_ids=media_ids, start_with_media_id=media_id)
        elif result == 13:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Show image information"])
            utility_cls.PictureInfo(self._stt, self, media_id=media_id)
        elif result == 15:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Browse all block images"])
            utility_cls.PictureBrowse(self._stt, self._main_win, self._data_dict["media"])
        elif result == 20:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Remove image"])
            self.remove_image_item(media_id)
        elif result == 30:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add image"])
            self._add_image()
        elif result == 40:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Auto add images"])
            self.block_event(self._my_name, "auto_add_images", None)
            self.get_appv("signal").block_text_give_focus(self._active_record_id)
        elif result == 50:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add image(s) from clipboard"])
            self._add_image(image_ids=self._clip.get_paste_images_ids())
        elif result == 55:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add file(s) from clipboard"])
            self._add_files(file_ids=self._clip.get_paste_files_ids())
        elif result == 60:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Copy image to clipboard"])
            self._clip.copy_to_clip(media_id)
        elif result == 70:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Add image to clipboard"])
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif result == 80:
            UTILS.LogHandler.add_log_record("#1 record ID: #2. Block image context menu.\nUser selected: #3.", ["WinBlock", self._active_record_id, "Clear clipboard"])
            self._clip.clear_clip()

    def scroll_area_action(self, action: str):
        if action == "delete":
            for i in range(self.horizontal_grid.count()):
                widget = self.horizontal_grid.itemAt(i).widget()
                if widget.are_you_marked():
                    self.remove_image_item(widget._media_id)
                    if i >= self.horizontal_grid.count():
                        i -= 1
                    if i >= 0:
                        widget = self.horizontal_grid.itemAt(i).widget()
                        widget.you_are_marked(True)
                    break
        elif action == "move_left" and self.horizontal_grid.count():
            pos = None
            for i in range(self.horizontal_grid.count()):
                widget = self.horizontal_grid.itemAt(i).widget()
                if widget.are_you_marked():
                    pos = i
                    break
            if pos is not None:
                pos -= 1
                if pos < 0:
                    pos = 0
                widget.you_are_marked(False)
                widget = self.horizontal_grid.itemAt(pos).widget()
                widget.you_are_marked(True)
        elif action == "move_right" and self.horizontal_grid.count():
            pos = None
            for i in range(self.horizontal_grid.count()):
                widget = self.horizontal_grid.itemAt(i).widget()
                if widget.are_you_marked():
                    pos = i
                    break
            if pos is not None:
                pos += 1
                if pos >= self.horizontal_grid.count():
                    pos = self.horizontal_grid.count() - 1
                widget.you_are_marked(False)
                widget = self.horizontal_grid.itemAt(pos).widget()
                widget.you_are_marked(True)
        elif action == "show_image" and self.horizontal_grid.count():
            pos = None
            for i in range(self.horizontal_grid.count()):
                widget = self.horizontal_grid.itemAt(i).widget()
                if widget.are_you_marked():
                    pos = i
                    break
            if pos is not None:
                if widget._i_am_image_item:
                    utility_cls.PictureView(self._stt, self, media_ids=self._data_dict["media"], start_with_media_id=widget._media_id)
                else:
                    utility_cls.FileInfo(self._stt, self, file_id=widget._media_id)

    def _send_msg_to_main_win(self):
        main_dict = {
            "name": self._my_name,
            "action": "cm"
        }
        if self._main_win is not None:
            self._main_win.events(main_dict)

    def remove_image_item(self, media_id: int):
        for i in range(self.horizontal_grid.count()):
            widget = self.horizontal_grid.itemAt(i).widget()
            if widget._media_id == media_id:
                this_is_image_item = widget._i_am_image_item
                self.horizontal_grid.removeWidget(widget)
                widget.close_me()
                break

        self.horizontal_grid.parent().setFixedWidth(self.getv("block_image_thumb_size") * self.horizontal_grid.count() + 10)

        if this_is_image_item:
            for idx, m_id in enumerate(self._data_dict["media"]):
                if m_id == media_id:
                    self._data_dict["media"].pop(idx)
                    break
            self.block_event("body", "image_removed")
        else:
            for idx, m_id in enumerate(self._data_dict["files"]):
                if m_id == media_id:
                    self._data_dict["files"].pop(idx)
                    break
            self.block_event("body", "file_removed")

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1 record ID: #2. Application settings updated", ["WinBlock", self._active_record_id])
        self._define_apperance()

    def _define_apperance(self):
        self.setFrameShape(self.getv(f"{self._my_name}_frame_shape"))
        self.setFrameShadow(self.getv(f"{self._my_name}_frame_shadow"))
        self.setLineWidth(self.getv(f"{self._my_name}_line_width"))
        self.setStyleSheet(self.getv(f"{self._my_name}_stylesheet"))
        self.setEnabled(self.getv(f"{self._my_name}_enabled"))
        self.setVisible(self.getv(f"{self._my_name}_visible"))
        self.layout().setSpacing(self.getv(f"{self._my_name}_layout_spacing"))

    def _set_margins(self, object: object, name: str) -> None:
        values = self.getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])

    def close_me(self):
        for child in self.children():
            if isinstance(child, utility_cls.Notification):
                child.close_me()

        if self._my_name in ["win_block_controls", "header", "footer"]:
            widgets = []
            for i in range(self.layout().count()):
                widget = self.layout().itemAt(i).widget()
                if isinstance(widget, Button):
                    widgets.append(widget)
            for widget in widgets:
                widget.close_me()
            widgets = None

        if self._my_name == "body" and self.body_text_box:
            widgets = []
            for i in range(self.horizontal_grid.count()):
                widget = self.horizontal_grid.itemAt(i).widget()
                if isinstance(widget, ImageItem):
                    widgets.append(widget)
            for widget in widgets:
                widget.close_me()
                self.horizontal_grid.removeWidget(widget)
            widgets = None

            self.body_text_box.close_me()
            self.auto_add_images_frame.close_me()
        
        self.hide()
        self.deleteLater()
        self.setParent(None)


class ScrollAreaItem(QScrollArea):
    def __init__(self, parent_widget, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        
        self._parent_widget = parent_widget
        self._my_name = "scroll_area"

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        if ev.key() == Qt.Key_Delete:
            self._parent_widget.scroll_area_action("delete")
        elif ev.key() == Qt.Key_Left:
            self._parent_widget.scroll_area_action("move_left")
        elif ev.key() == Qt.Key_Right:
            self._parent_widget.scroll_area_action("move_right")
        elif ev.key() == Qt.Key_Return:
            self._parent_widget.scroll_area_action("show_image")

        return super().keyPressEvent(ev)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self._parent_widget.get_appv("cm").remove_all_context_menu()

        if a0.button() == Qt.RightButton:
            self._parent_widget.scroll_area_item_right_click()
            a0.accept()
        return super().mousePressEvent(a0)


class ImageItem(QLabel):
    def __init__(self, settings: settings_cls.Settings, parent_widget, media_id: int, *args, **kwargs):
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
        self._i_am_marked = False

        db_media = db_media_cls.Media(self._stt)
        self._i_am_image_item = db_media.is_media_exist(self._media_id)

        self._set_tooltip()

        self.load_image()

    def _set_tooltip(self):
        if self._i_am_image_item:
            db_media = db_media_cls.Media(self._stt, self._media_id)
            txt = ""
            if db_media.media_name:
                txt = db_media.media_name + "\n"
            if db_media.media_description:
                txt += db_media.media_description
        else:
            db_media = db_media_cls.Files(self._stt, self._media_id)
            file_util = utility_cls.FileDialog(self._stt)
            txt = file_util.get_file_tooltip_text(db_media.file_file, self._stt)

        self.setToolTip(txt)

    def you_are_marked(self, value: bool):
        if value:
            self.setFrameShape(self.Box)
            self.setLineWidth(1)
            self._i_am_marked = True
        else:
            self.setFrameShape(self.NoFrame)
            self._i_am_marked = False

    def are_you_marked(self) -> bool:
        return self._i_am_marked
    
    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        self._parent_widget.image_item_double_click(self._media_id, self)
        a0.accept()
        return super().mouseDoubleClickEvent(a0)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.get_appv("cm").remove_all_context_menu()
        
        self._parent_widget.image_item_left_click(self._media_id)
        
        if ev.button() == Qt.RightButton:
            self._parent_widget.image_item_right_click(self._media_id, self)
            ev.accept()
        else:
            return super().mousePressEvent(ev)

    def load_image(self, media_id: int = None):
        if media_id is None:
            media_id = self._media_id
        
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setFixedSize(self.getv("block_image_thumb_size"), self.getv("block_image_thumb_size"))

        db_media = db_media_cls.Media(self._stt)
        if db_media.is_media_exist(self._media_id):
            db_media.load_media(self._media_id)
            img = QPixmap(db_media.media_file)
            size = self.maximumSize()
            if img.height() > size.height() or img.width() > size.width():
                img = img.scaled(size, Qt.KeepAspectRatio)
            self.setPixmap(img)
        else:
            db_media = db_media_cls.Files(self._stt)
            if db_media.is_file_exist(self._media_id):
                db_media.load_file(self._media_id)
                file_util = utility_cls.FileDialog(self._stt)

                img = file_util.get_file_type_image(self._media_id, self.size())

                if img:
                    self.setPixmap(img)
                else:
                    file_ext = file_util.FileInfo().file_extension(db_media.file_file)
                    file_ext = file_ext.strip(".")
                    
                    for i in range(16, 100):
                        font = QFont("Comic Sans MS", i)
                        fm = QFontMetrics(font)
                        if fm.width(file_ext) >= self.getv("block_image_thumb_size"):
                            font = QFont("Comic Sans MS", i - 1)
                            break
                    self.setFont(font)
                    self.setText(f'<span style="color: #00df00; font-size: 12px;">{self.getl("file_text")} </span><span style="color: #0aa5ec; font-size: {i-1}px;">{file_ext}</span>')
            else:
                self.setText("Error.")

    def close_me(self):
        self.deleteLater()
        self.setParent(None)


class TextBox(QTextEdit):
    def __init__(self, parent_widget: QFrame, settings: settings_cls.Settings, record_id: int, my_name: str, data_dict: dict, main_win, *args, **kwargs):
        super().__init__(parent_widget, *args, *kwargs)
        # Define variables
        self._parent_widget = parent_widget
        self._active_record_id = record_id
        self._my_name = my_name
        self._data_dict = data_dict

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define MainWin
        self._main_win = main_win
        
        # Define Auto Complete
        self.ac = text_handler_cls.AutoComplete(self._stt, self, main_win=self._main_win, widget_handler=self._data_dict["widget_handler"])
        self.txt_handler = text_handler_cls.TextHandler(self._stt, self, self._main_win, widget_handler=self._data_dict["widget_handler"])

        # Define signals object
        self.signals: utility_cls.Signals = self.get_appv("signal")
        
        self._create_text_box()

        # It is used to monitor whether the text was typed or pasted by the user
        self.text_len = len(self.toPlainText()) - 1
        
        # Determines whether the user pasted new text or selected it from the autocomplete list
        self.autocomplete_commited = False

        # Determines whether the mouse move should highlight the word
        self.highlight_mode = True

        # Prevents recursion when marking defined expressions
        self._definitions_working = False

        # Prevents recursion when selecting text
        self._selection_working = False

        # Determines whether the mouse key is pressed
        self.mouse_pressed = False

        # Time when text was last entered
        self._type_time = time.time()

        # Clipboard
        self._clipboard = self.get_appv("clipboard")

        # Autosave QTimer
        self._autosave_timer = None

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.textChanged.connect(self.txt_box_text_changed)
        self.cursorPositionChanged.connect(self.txt_box_cursor_position_changed)
        self.selectionChanged.connect(self.selection_changed)
        # Connect Signals with slots
        self.signals.signalBlockTextGiveFocus.connect(self.signalBlockTextGiveFocus)
        self.signals.signalAutoCompleteSelected.connect(self.signalAutoCompleteSelected)
        self.signals.signalNewDefinitionAdded.connect(self.signalNewDefinitionAdded)

        self.txt_box_text_changed()
        self._autosave(first_run=True)

    def detection_btn_command(self, detail: dict):
        UTILS.LogHandler.add_log_record("#1 -> #2 record ID: #3. Command detected #4", ["WinBlock", "TextBox", self._active_record_id, detail["command"]])
        if detail["command"] == "list":
            if self.toPlainText():
                if self.toPlainText()[-1:] == "@":
                    insert_text = "@list"
                    if len(self.toPlainText()) > 1:
                        if self.toPlainText()[-2] != "\n@":
                            insert_text = f"\n@list"

                    cur = self.textCursor()
                    cur.setPosition(len(self.toPlainText()) - 1)
                    cur.movePosition(cur.Right, cur.KeepAnchor, 1)
                    cur.insertText(insert_text)
                    self.setTextCursor(cur)
                    self.txt_handler.return_pressed()
                    self.setFocus()

        if detail["command"] in ["images", "calculator"]:
            comm = detail["command"]
            if self.toPlainText():
                insert_text = f"@{comm}"
                if len(self.toPlainText()) > 1:
                    if self.toPlainText()[-2] != "\n@":
                        insert_text = f"\n@{comm}"

                cur = self.textCursor()
                cur.setPosition(len(self.toPlainText()) - 1)
                cur.movePosition(cur.Right, cur.KeepAnchor, 1)
                cur.insertText(insert_text)
                self.setTextCursor(cur)
                self.txt_handler.return_pressed()
                self.setFocus()

    def stop_calculator(self):
        self.txt_handler._calc_stop()

    def add_image(self):
        self._parent_widget.block_event(self._my_name, "add_image")

    def add_files(self):
        self._parent_widget.block_event(self._my_name, "add_files")

    def txt_box_cursor_position_changed(self):
        if self._active_record_id not in self.get_appv("calculator"):
            return
        
        cur = self.textCursor()
        cur_pos = cur.position()

        txt = self.toPlainText()
        txt_list = txt.split("\n")
        if not txt_list:
            return
        last_line_len = len(txt_list[-1])
        if cur_pos < len(txt) - last_line_len:
            cur_pos = len(txt)
            cur.setPosition(cur_pos)
            self.setTextCursor(cur)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == Qt.Key_Up:
            if self.ac.isVisible():
                self.ac.move_up()
                e.accept()
                return None

        if e.key() == Qt.Key_Down:
            if self.ac.isVisible():
                self.ac.move_down()
                e.accept()
                return None
        
        if e.key() == Qt.Key_Left:
            if self.ac.isVisible():
                self.ac.hide_ac()
                e.accept()
                return None

        if e.key() == Qt.Key_Right:
            if self.ac.isVisible():
                self.ac.hide_ac()
                e.accept()
                return None

        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            if self.ac.isVisible():
                self.ac.select_item()
                e.accept()
                return None
            if self.txt_handler.return_pressed():
                e.accept()
                return None

        if e.key() == Qt.Key_Escape:
            if self.ac.isVisible():
                self.ac.hide_ac()
            else:
                self.txt_handler.escape_pressed()
    
            self.txt_handler.hide_definition_simple_view()
            self.txt_handler.highlight_toggle(False)
            self._parent_widget._auto_add_images_mode_exit()
            e.accept()
            return None

        if e.key() == Qt.Key_Delete:
            if self.ac.isVisible():
                self.ac.delete_item()
                e.accept()
                return None

        if e.key() == Qt.Key_Backspace:
            if self._active_record_id in self.get_appv("calculator"):
                cur = self.textCursor()
                if cur.position() == len(self.toPlainText()) - len(self.toPlainText().split("\n")[-1]):
                    e.accept()
                    return None

        if e.text() and e.text() in "([{<|'\"`*_/\\~-":
            if self.txt_handler.smart_parenthesis_selection(e):
                e.accept()
                return None
        
        # if e.key() == Qt.Key_S and e.modifiers() == Qt.ControlModifier:
        #     self.block_event(self._my_name, "save_block")
        
        return super().keyPressEvent(e)

    def txt_box_text_changed(self) -> None:
        # Parenthesis
        if self.txt_handler.smart_parenthesis_command():
            return

        show_ac = False
        if len(self.toPlainText()) - self.text_len > 0:
            if not self._definitions_working:
                self._definitions_working = True
                self.txt_handler.check_definitions()
                self._definitions_working = False
                show_ac = True
        if len(self.toPlainText()) - self.text_len < 2:
            if len(self.toPlainText()) - self.text_len == 0 and not show_ac:
                self.auto_complete_text(hide_ac=True)
            else:
                if self.toPlainText()[self.toPlainText().rfind("\n") + 1:].startswith("@@"):
                    self.auto_complete_text(hide_ac=True)
                else:
                    self.auto_complete_text()
        else:
            if not self.autocomplete_commited:
                self.ac.update_autocomplete_dictionary(self.toPlainText())
                
        self.autocomplete_commited = False
        self.text_len = len(self.toPlainText())
        if self._data_dict["body"] != self.toPlainText():
            self.block_event(self._my_name, "text_changed")
        
        if self._active_record_id in self.get_appv("calculator"):
            self.txt_handler._calc_start()
        else:
            if self.toPlainText():
                if self.toPlainText()[-1:] == "@":
                    self.signals.send_detected_object_to_button(is_visible=True)
                else:
                    self.signals.send_detected_object_to_button(is_visible=False)
            else:
                self.signals.send_detected_object_to_button(is_visible=False)

        if self._type_time:
            type_time = time.time() - self._type_time
            self.txt_handler.definition_hint(type_time, self._active_record_id)
        self._type_time = time.time()

        self._autosave()

    def _autosave(self, first_run: bool = False, force_update: bool = False):
        if first_run:
            self._autosave_timer = QTimer(self)
            self._autosave_timer.timeout.connect(self._autosave)
            self._autosave_timer.start(self.getv("block_autosave_check_every"))
            self._autosave_timer_prev_text = self.toPlainText()
            return

        if self._autosave_timer is None:
            return

        if self.txt_handler._calc_mode:
            return

        if force_update:
            if self._data_dict["need_update"] is False:
                return
        else:
            if time.time() - self._type_time < self.getv("block_autosave_timeout") or self._data_dict["need_update"] is False:
                return

        if self.getv("block_autosave_enabled"):
            self.block_event(self._my_name, "autosave")
            detail_dict = {
                "type": "show",
                "name": "autosave",
                "text": self.getl("block_autosave_msg"),
                "duration": self.getv("block_autosave_msg_duration"),
                "id": self._active_record_id
            }
            if self.getv("block_autosave_show_msg"):
                self.block_event(self._my_name, "titlebar_msg", detail=detail_dict)

    def auto_complete_text(self, hide_ac: bool = False):
        # Activate AutoComplete
        if hide_ac:
            self.ac.hide_ac()
        else:
            self.ac.show_ac()

    def signalNewDefinitionAdded(self):
        UTILS.LogHandler.add_log_record("#1 -> #2 record ID: #3. Definitions changed, block updated.", ["WinBlock", "TextBox", self._active_record_id])
        # self.txt_handler._populate_def_list()
        # self.txt_handler.check_definitions()
        self.text_len -= 1
        self.txt_box_text_changed()

    def signalAutoCompleteSelected(self, data_dict: dict):
        if data_dict["record_id"] == self._active_record_id:
            self.autocomplete_commited = True
            move = len(data_dict["word"]) - len(data_dict["ac"])
            if self.textCursor().position() >= move:
                cursor = self.textCursor()
                cursor.movePosition(cursor.Left, cursor.KeepAnchor, move)
                cursor.deleteChar()
                self.autocomplete_commited = True
                cursor.insertText(data_dict["word"])
                self.setTextCursor(cursor)

    # Here we handle all events
    def block_event(self, name: str, action: str, detail: dict = None) -> None:
        if action == "text_changed":
            self._data_dict["body"] = self.toPlainText()
            self._data_dict["body_html"] = self.toHtml()

        self._parent_widget.block_event(name, action, detail)
        self.signals.saved_button_check_status(self._active_record_id)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        self.get_appv("cm").remove_all_context_menu()

        if e.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.highlight_mode = False
            self.txt_handler.highlight_toggle(False)

        self.txt_handler.mouse_press_event(e)
        if e.button() == Qt.LeftButton:
            self.txt_handler.check_definitions(e)

        return super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.mouse_pressed = False
            if not self.textCursor().hasSelection():
                self.highlight_mode = True
                self.txt_handler.mouse_move(e)
        return super().mouseReleaseEvent(e)

    def selection_changed(self) -> None:
        if self._active_record_id in self.get_appv("calculator"):
            if not self._selection_working:
                self._check_is_calculator_selection_valid()
        
        if self.textCursor().hasSelection():
            self.highlight_mode = False
        else:
            if self.mouse_pressed:
                self.highlight_mode = False
            else:
                self.highlight_mode = True

    def _check_is_calculator_selection_valid(self):
        cur = self.textCursor()
        if not cur.hasSelection():
            return
        
        sel_start = cur.selectionStart()
        sel_end = cur.selectionEnd()

        txt = self.toPlainText()
        txt_list = txt.split("\n")
        if not txt_list:
            return
        last_line_len = len(txt_list[-1])

        if sel_start < len(txt) - last_line_len:
            sel_start = len(txt) - last_line_len

        self._selection_working = True

        cur.clearSelection()

        if sel_end < len(txt) - last_line_len:
            cur.setPosition(len(txt))
            self.setTextCursor(cur)
            self._selection_working = False
            return

        cur.setPosition(sel_start)
        cur.movePosition(cur.Right, cur.KeepAnchor, sel_end - sel_start)
        self.setTextCursor(cur)
        self._selection_working = False

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if self.highlight_mode:
            self.txt_handler.mouse_move(e)
        
        self.txt_handler.show_definition_on_mouse_hover(e)
        
        return super().mouseMoveEvent(e)

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent) -> None:
        e.accept()
        self.ac.hide_ac()
        self.undoAvailable.connect(self.txt_handler._can_undo)
        self.redoAvailable.connect(self.txt_handler._can_redo)

        self.send_dont_clear_c_menu_to_main_win()

        self.txt_handler.show_context_menu()

        if self.ac:
            self.ac.hide_ac()
        if self.txt_handler:
            self.txt_handler.check_definitions()

    def send_dont_clear_c_menu_to_main_win(self):
        main_dict = {
            "name": self._my_name,
            "action": "cm"
        }
        self._main_win.events(main_dict)

    def focusInEvent(self, e: QtGui.QFocusEvent) -> None:
        self._parent_widget.block_event(self._my_name, "focus_in")
        return super().focusInEvent(e)

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
        if self.ac:
            self.ac.hide_ac()
            if self.getv("block_autosave_on_lost_focus"):
                self._autosave(force_update=True)
        return super().focusOutEvent(e)

    def signalBlockTextGiveFocus(self, record_id):
        if self._active_record_id == record_id:
            self.setFocus()

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1 -> #2 record ID: #3. Application settings updated.", ["WinBlock", "TextBox", self._active_record_id])
        self._create_text_box(settings_updated=True)

    def _create_text_box(self, settings_updated: bool = False):
        if not settings_updated:
            self.setUndoRedoEnabled(True)
            
            if self._data_dict["body"]:
                self.setHtml(self._data_dict["body_html"])
                if not self._data_dict["body_html"]:
                    self.setText(self._data_dict["body"])
            else:
                self.setText(self.getl(f"{self._my_name}_text"))
            self.setToolTip(self.getl(f"{self._my_name}_tt"))
            self.setStatusTip(self.getl(f"{self._my_name}_sb_text"))
            self.setStatusTip(self.getl(f"{self._my_name}_placeholder_text"))

        self.setFrameShape(self.getv(f"{self._my_name}_frame_shape"))
        self.setFrameShadow(self.getv(f"{self._my_name}_frame_shadow"))
        self.setLineWidth(self.getv(f"{self._my_name}_line_width"))
        self.setTabChangesFocus(self.getv(f"{self._my_name}_tab_changes_focus"))
        self.setLineWrapMode(self.getv(f"{self._my_name}_line_wrap_mode"))
        if self.getv(f"{self._my_name}_line_wrap_mode") > 1:
            self.setLineWrapColumnOrWidth(self.getv(f"{self._my_name}_line_wrap_column_or_width"))
        self.setReadOnly(self.getv(f"{self._my_name}_read_only"))
        self.setTabStopWidth(self.getv(f"{self._my_name}_tab_stop_width"))
        self.setTabStopDistance(self.getv(f"{self._my_name}_tab_stop_distance"))
        self.setAcceptRichText(self.getv(f"{self._my_name}_accept_rich_text"))
        self.setCursorWidth(self.getv(f"{self._my_name}_cursor_width"))

        font = QFont(self.getv(f"{self._my_name}_font_name"), self.getv(f"{self._my_name}_font_size"))
        font.setWeight(self.getv(f"{self._my_name}_font_weight"))
        font.setItalic(self.getv(f"{self._my_name}_font_italic"))
        font.setUnderline(self.getv(f"{self._my_name}_font_underline"))
        font.setStrikeOut(self.getv(f"{self._my_name}_font_strikeout"))
        self.setFont(font)

        self.setStyleSheet(self.getv(f"{self._my_name}_stylesheet"))

        self.setEnabled(self.getv(f"{self._my_name}_enabled"))
        self.setVisible(self.getv(f"{self._my_name}_visible"))

        fm = QFontMetrics(self.font())
        height = fm.height()
        number_of_lines = self.getv(f"{self._my_name}_number_of_visible_lines")
        self.setFixedHeight(int(number_of_lines * height) + 10)
        self.setViewportMargins(0,0,0,10)

    def close_me(self):
        self.get_appv("cm").remove_all_context_menu()

        self.hide()
        QCoreApplication.processEvents()
        for child in self.children():
            if isinstance(child, utility_cls.Notification):
                child.close_me()

        if self._autosave_timer:
            self._autosave_timer.stop()
        self._autosave_timer = None
        if self.ac:
            self.ac.close_me()
        self.ac = None
        if self.txt_handler:
            self.txt_handler.close_me()
        self.txt_handler = None

        self.deleteLater()
        self.setParent(None)


class Button(QPushButton):
    """Creates Buttons
    data_dict:
        'area'
        'cash'
        'contact'
        'date'
        'location'
        'medical'
        'tag'
        'web_page'
        'youtube'
        'translation'

        'record_date' (str): Date of record
        'name' (str)
        'body' (str): Text in block
        'updated' (str): Updated time
        'draft' (int)
        'save' (bool)
    """
    def __init__(self, parent_widget: QFrame, settings: settings_cls.Settings, record_id: int, my_name: str, tag_id: int = 0, data_dict: dict = None, main_win = None,*args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._tag_id = tag_id
        self._data_dict = data_dict
        self._parent_widget = parent_widget
        self._active_record_id = record_id
        self._my_name = my_name
        self._main_win = main_win
        self._messages = []  # item: text, duration, QTimer
        self.widget_handler: qwidgets_util_cls.WidgetHandler = self._data_dict["widget_handler"]
        self.widget_handler.add_QPushButton(self, {"allow_bypass_mouse_press_event": False})
        self.timer = timer_cls.TimerHandler(self)

        # Define Signals class
        self._signals: utility_cls.Signals = self.get_appv("signal")
        
        self._create_button()
        self._define_if_saved_button_is_visible(self._active_record_id)

        # Connect events with slots
        self.setMouseTracking(True)
        self.clicked.connect(self.btn_clicked)
        self.mouseMoveEvent = self._mouse_move_event

        # Connect Signals with slots
        self._signals_connections()

    def update_msg(self, detail: dict):
        # detail_dict = {
        #     "type": "show",
        #     "name": "autosave",
        #     "text": self.getl("block_autosave_msg"),
        #     "duration": self.getv("block_autosave_msg_duration")
        #     "id": self._active_record_id
        # }
        if detail["id"] != self._active_record_id:
            return
        
        if detail["type"] == "show":
            self._update_msg_show(detail)
        elif detail["type"] == "hide":
            self._update_msg_hide(detail["name"])
    
    def _update_msg_show(self, detail: dict):
        name = detail["name"]
        dur = detail["duration"]
        text = detail["text"]
        
        existing_msg = None
        for msg in self._messages:
            if msg["name"] == name:
                existing_msg = msg
        
        if existing_msg:
            existing_msg["text"] = text
            existing_msg["duration"] = dur
            try:
                timer: SingleShotTimer = existing_msg["timer"]
                timer.stop()
                timer.set_duration(dur)
                timer.start()
            except AttributeError:
                new_timer = self.timer.add_timer(SingleShotTimer(
                    self.timer,
                    duration=dur,
                    function_on_finished=self._msg_timer_triggered,
                    data={"name": name}),
                    auto_start=True)
                existing_msg["timer"] = new_timer
        else:
            new_msg = {}
            new_msg["name"] = name
            new_msg["text"] = text
            new_msg["duration"] = dur
            new_timer = self.timer.add_timer(SingleShotTimer(
                self.timer,
                duration=dur,
                function_on_finished=self._msg_timer_triggered,
                data={"name": name}),
                auto_start=True)

            new_msg["timer"] = new_timer
            self._messages.append(new_msg)

        self._update_msg_text()
        self.setVisible(True)

    def _msg_timer_triggered(self, timer: SingleShotTimer):
        name = timer.data["name"]
        self._update_msg_hide(name)

    def _update_msg_text(self):
        text = "   ".join([x["text"] for x in self._messages])
        self.setText(text)
        self._set_geometry()

    def _update_msg_hide(self, name: str):
        delete_index_list = []
        for idx, msg in enumerate(self._messages):
            if msg["name"] == name:
                msg["timer"].stop()
                self.timer.remove_timer(msg["timer"])
                delete_index_list.append(idx)

        delete_index_list.reverse()
        for idx in delete_index_list:
            del self._messages[idx]

        self._update_msg_text()

        if not self._messages:
            self.setVisible(False)

    def _mouse_move_event(self, e):
        self._parent_widget.block_event("footer", "set_pointer_to_arrow")

    def _signals_connections(self):
        self._signals.signalSavedButtonCheckStatus.connect(self._define_if_saved_button_is_visible)
        self._signals.signalBlockDateFormatChanged.connect(self.signal_date_format_changed_event)
        self._signals.signalDetectedObject.connect(self.signal_detect_object)
        self._signals.signal_app_settings_updated.connect(self.app_setting_updated)

    def signal_date_format_changed_event(self):
        if self._my_name == "win_block_control_btn_date":
            self._win_block_control_btn_date_set_text()
            self._set_geometry()

    def signal_detect_object(self, is_visible: bool):
        if self._my_name == "footer_btn_detection":
            self.setVisible(is_visible)

    # Here we Handle Mouse Press events (Right Click)
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        """
        Call parent method 'block_event'
        Param:
            name: button name
            action: right_click ...
            detail (dict):
                record_id (int)
                ...
        """
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self).EVENT_mouse_press_event(e)
        elif e.button() == Qt.RightButton:
            e.accept()
            self.get_appv("cm").remove_all_context_menu()
            self._parent_widget.block_event(self._my_name, "mouse_press")

            if self._my_name == "win_block_control_btn_name":
                self.action_control_btn_name_mouse_press(e)

            if self._my_name == "win_block_control_btn_date":
                self.action_control_btn_date_mouse_press(e)

            if self._my_name == "header_btn_add":
                self.action_control_header_btn_add_left_click()

            if self._my_name == "header_btn_diary":
                self.action_control_header_btn_diary_mouse_press(e)

            if self._my_name == "header_btn_tag":
                self.action_control_header_btn_tag_mouse_press(e)

            if self._my_name == "header_btn_user":
                self.action_control_header_btn_user_mouse_press(e)

            if self._my_name == "footer_btn_save":
                self.action_control_footer_btn_save_mouse_press(e)

            if self._my_name == "footer_btn_delete":
                self.action_control_footer_btn_delete_mouse_press(e)

            if self._my_name == "footer_btn_add_new":
                self.action_control_footer_btn_add_new_mouse_press(e)

            if self._my_name == "footer_btn_detection":
                self.action_footer_btn_detection_left_click()

            self._signals.saved_button_check_status(self._active_record_id)
            return None

        self._signals.saved_button_check_status(self._active_record_id)
        return super().mousePressEvent(e)

    def action_control_footer_btn_add_new_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        menu_dict = {
            "position": QCursor().pos(),
            "items": [
                [10, self.getl("block_footer_btn_menu_add_new_text"), self.getl("block_footer_btn_menu_add_new_desc"), True, [], self.getv("footer_btn_add_new_icon_path")],
                [20, self.getl("block_footer_btn_menu_add_new_and_close_me_text"), self.getl("block_footer_btn_menu_add_new_and_close_me_tt"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        if menu_dict["result"] == 10:
            self._parent_widget.btn_clicked("footer_btn_add_new", "clicked")
        if menu_dict["result"] == 20:
            self._parent_widget.btn_clicked("footer_btn_add_new", "clicked")
            self._parent_widget.btn_clicked("win_block_control_btn_close", "clicked")

    def action_control_footer_btn_save_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        menu_dict = {
            "position": QCursor().pos(),
            "separator": [20],
            "items": [
                [10, self.getl("block_footer_btn_save_menu_save_text"), self.getl("block_footer_btn_save_menu_save_desc"), True, [], self.getv("footer_btn_save_icon_path")],
                [20, self.getl("block_footer_btn_save_menu_save&close_text"), self.getl("block_footer_btn_save_menu_save&close_desc"), True, [], None],
                [30, self.getl("block_footer_btn_save_menu_update_text"), self.getl("block_footer_btn_save_menu_update_tt"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        if menu_dict["result"] == 10:
            self._parent_widget.btn_clicked(self._my_name, "clicked")
            self.action_save_button_left_click()
        elif menu_dict["result"] == 20:
            self._parent_widget.btn_clicked(self._my_name, "clicked")
            self.action_save_button_left_click()
            self._parent_widget.btn_clicked("win_block_control_btn_close", "clicked")
        elif menu_dict["result"] == 30:
            self._parent_widget.block_event(self._my_name, "update_block")

    def action_control_footer_btn_delete_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        menu_dict = {
            "position": QCursor().pos(),
            "items": [
                [1, self.getl("block_footer_btn_delete_menu_delete_text"), self.getl("block_footer_btn_delete_menu_delete_desc"), True, [], self.getv("block_footer_btn_delete_msg_btn_yes_icon_path")],
                [2, self.getl("block_footer_btn_delete_menu_close_text"), self.getl("block_footer_btn_delete_menu_close_desc"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        if menu_dict["result"] == 1:
            self.action_control_footer_btn_delete_left_click()
        elif menu_dict["result"] == 2:
            self._parent_widget.btn_clicked("win_block_control_btn_close", "clicked")

    def action_control_header_btn_user_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        menu_dict = {
            "position": QCursor().pos(),
            "items": [
                [1, f'{self.getl("block_header_user_context_remove_text")}: {self.text()}', self.getl("block_header_user_context_remove_desc"), True, [], None],
                [11, self.getl("edit_tags_cm_text"), self.getl("edit_tags_cm_tt"), True, [], None]
                ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        result = self.get_appv("menu")["result"]
        if result:
            if result == 1:
                new_tag_list = []
                for tag in self._data_dict["tag"]:
                    if tag != self._tag_id:
                        new_tag_list.append(tag)
                result_dict = {
                    "old_tag_list": self._data_dict["tag"],
                    "new_tag_list": new_tag_list,
                    "tag_diff": self._tag_id
                }
                self._parent_widget.block_event(self._my_name, "tag_changed", result_dict)
            if result == 11:
                tag_cls.TagView(self._stt, self._parent_widget, self._tag_id)

    def action_control_header_btn_tag_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        menu_dict = {
            "position": QCursor().pos(),
            "items": [
                [1, f'{self.getl("block_header_tag_context_remove_text")}: {self.text()}', self.getl("block_header_tag_context_remove_desc"), True, None, None],
                [11, self.getl("edit_tags_cm_text"), self.getl("edit_tags_cm_tt"), True, [], None]
                ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        result = self.get_appv("menu")["result"]
        if result:
            if result == 1:
                new_tag_list = []
                for tag in self._data_dict["tag"]:
                    if tag != self._tag_id:
                        new_tag_list.append(tag)
                result_dict = {
                    "old_tag_list": self._data_dict["tag"],
                    "new_tag_list": new_tag_list,
                    "tag_diff": self._tag_id
                }
                self._parent_widget.block_event(self._my_name, "tag_changed", result_dict)
            if result == 11:
                tag_cls.TagView(self._stt, self._parent_widget, self._tag_id)

    def action_control_header_btn_diary_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        notif_dict = {
            "text": self.getl("block_header_diary_context_notification_text"),
            "icon": self.getv("notification_block_remove_diary_icon_path"),
            "show_ok": True,
            "animation": False,
            "position": "bottom_right"
        }
        notification = utility_cls.Notification(self._stt, self._parent_widget._parent_widget, notif_dict)
        menu_dict = {
            "position": QCursor().pos(),
            "items": [[1, self.getl("block_header_diary_context_remove_text"), self.getl("block_header_diary_context_remove_desc"), True, None, self.getv("notification_block_remove_diary_icon_path")]]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        result = self.get_appv("menu")["result"]
        if result:
            if result == 1:
                new_tag_list = []
                for tag in self._data_dict["tag"]:
                    if tag != self._tag_id:
                        new_tag_list.append(tag)
                result_dict = {
                    "old_tag_list": self._data_dict["tag"],
                    "new_tag_list": new_tag_list,
                    "tag_diff": self._tag_id
                }
                self._parent_widget.block_event(self._my_name, "tag_changed", result_dict)
        notification.close()

    def action_control_btn_date_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        dt = utility_cls.DateTime(self._stt)
        date_dict = dt.make_date_dict()
        exm_short = f'{date_dict["date"]}'
        exm_day = f'{date_dict["day_name"]}, {date_dict["date"]}'
        exm_month = f'{date_dict["day"]}. , {date_dict["month_name"]}, {date_dict["year"]}.'
        exm_day_month = f'{date_dict["day_name"]}, {date_dict["day"]}. , {date_dict["month_name"]}, {date_dict["year"]}.'
        selected = []
        for i in range(4):
            selected.append(None)
        if 0 <= self.getv("win_block_controls_show_long_date") <= 4:
            selected[self.getv("win_block_controls_show_long_date")] = self.getv("context_menu_item_marked_icon_path")
        menu_dict = {
            "result": None,
            "position": QCursor().pos(),
            "selected": [],
            "separator": [2],
            "items": [
                [
                    1,
                    self.getl("header_btn_date_context_set_date"),
                    self.getl("header_btn_date_context_set_date_desc"),
                    True,
                    [],
                    self.getv("context_menu_item_write_line_icon_path")
                ],
                [
                    2,
                    self.getl("header_btn_date_context_calendar_pick"),
                    self.getl("header_btn_date_context_calendar_pick_desc"),
                    True,
                    [],
                    self.getv("context_menu_item_calendar_icon_path")
                ],
                [
                    3,
                    self.getl("header_btn_date_context_set_display"),
                    self.getl("header_btn_date_context_set_display_desc"),
                    False,
                    [
                        [
                            301,
                            f'{self.getl("header_btn_date_context_format_short")} ... ({exm_short})',
                            self.getl("header_btn_date_context_format_short_desc"),
                            True,
                            [],
                            selected[0]
                        ],
                        [
                            302,
                            f'{self.getl("header_btn_date_context_format_day")} ... ({exm_day})',
                            self.getl("header_btn_date_context_format_day_desc"),
                            True,
                            [],
                            selected[1]
                        ],
                        [
                            303,
                            f'{self.getl("header_btn_date_context_format_month")} ... ({exm_month})',
                            self.getl("header_btn_date_context_format_month_desc"),
                            True,
                            [],
                            selected[2]
                        ],
                        [
                            304,
                            f'{self.getl("header_btn_date_context_format_daymonth")} ... ({exm_day_month})',
                            self.getl("header_btn_date_context_format_daymonth_desc"),
                            True,
                            [],
                            selected[3]
                        ],
                    ],
                    self.getv("context_menu_item_cm_single_choice_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        result = self.get_appv("menu")["result"]
        if result:
            
            if result == 1:
                self.action_control_btn_date_left_click()
            
            elif result == 2:
                cal_dict = {
                    "name": "block_title_date_calendar",
                    "position": QCursor().pos(),
                    "date": self._data_dict["record_date"],
                }
                self._send_msg_to_main_win()
                utility_cls.Calendar(self._stt, self, cal_dict)
                if cal_dict["result"]:
                    result_dict = {
                        "old_date": self._data_dict["record_date"],
                        "new_date": cal_dict["result"],
                        "record_id": self._active_record_id
                    }
                    self._parent_widget.block_event(self._my_name, "date_changed", result_dict)
                    self._win_block_control_btn_date_set_text()
                    self._set_geometry()

            elif result >= 301 and result <= 304:
                self.setv("win_block_controls_show_long_date", result - 301)
                self._signals.block_date_format_changed()
                notif_dict = {
                    "title": "",
                    "text": self.getl("notification_block_date_format_changed_text"),
                    "timer": 1800,
                    "position": "bottom right" }
                self._signals.block_text_give_focus(self._active_record_id)
                utility_cls.Notification(self._stt, self._parent_widget._parent_widget, notif_dict)

    def action_control_btn_name_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        menu_dict = {
            "result": None,
            "position": QCursor().pos(),
            "items": [
                [
                    1,
                    self.getl("header_btn_name_context_set_name"),
                    self.getl("header_btn_name_context_set_name_desc"),
                    True,
                    [],
                    self.getv("context_menu_item_write_line_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        result = self.get_appv("menu")["result"]
        if result:
            if result == 1:
                self.action_control_btn_name_left_click()

    # Here we Handle Click events
    def btn_clicked(self) -> None:
        self.get_appv("cm").remove_all_context_menu()
        self._parent_widget.btn_clicked(self._my_name, "clicked")

        if self._my_name == "win_block_control_btn_name":
            self.action_control_btn_name_left_click()
        elif self._my_name == "win_block_control_btn_date":
            self.action_control_btn_date_left_click()
        elif self._my_name == "win_block_control_btn_msg":
            self.ask_user_to_hide_definition_messages()

        elif self._my_name == "header_btn_add":
            self.action_control_header_btn_add_left_click()

        elif self._my_name == "footer_btn_save":
            self.action_save_button_left_click()
        elif self._my_name == "footer_btn_saved":
            self.action_saved_button_left_click()
        elif self._my_name == "footer_btn_delete":
            self.action_control_footer_btn_delete_left_click()
        elif self._my_name == "footer_btn_detection":
            self.action_footer_btn_detection_left_click()

        self._signals.saved_button_check_status(self._active_record_id)

    def ask_user_to_hide_definition_messages(self):
        selected = []

        if self.getv("block_calc_mode_titlebar_msg_enabled"):
            selected.append(110)
        else:
            selected.append(120)

        if self.getv("block_definition_titlebar_msg_enabled"):
            selected.append(210)
        else:
            selected.append(220)

        menu_dict = {
            "position": QCursor().pos(),
            "selected": selected,
            "items": [
                [100,
                 self.getl("block_titlebar_msg_calc_enable_text"),
                 self.getl("block_titlebar_msg_calc_enable_tt"),
                 False,
                 [
                     [110, self.getl("text_on"), "", True, [], None],
                     [120, self.getl("text_off"), "", True, [], None]
                 ],
                 self.getv("calculator_icon_path")
                 ],
                [200,
                 self.getl("block_titlebar_msg_definition_enable_text"),
                 self.getl("block_titlebar_msg_definition_enable_tt"),
                 False,
                 [
                     [210, self.getl("text_on"), "", True, [], None],
                     [220, self.getl("text_off"), "", True, [], None]
                 ],
                 self.getv("definition_icon_path")
                 ]
            ]
        }

        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self._main_win)

        result = self.get_appv("menu")["result"]

        msg_dict = {
            "id": self._active_record_id,
            "type": "show",
            "name": "system",
            "duration": 10000
        }

        if result == 110:
            self.setv("block_calc_mode_titlebar_msg_enabled", True)
            msg_dict["text"] = f"{self.getl('block_titlebar_msg_calc_enable_text')} - {self.getl('text_on')}"
            self.update_msg(msg_dict)
        elif result == 120:
            self.setv("block_calc_mode_titlebar_msg_enabled", False)
            msg_dict["text"] = f"{self.getl('block_titlebar_msg_calc_enable_text')} - {self.getl('text_off')}"
            self.update_msg(msg_dict)
        elif result == 210:
            self.setv("block_definition_titlebar_msg_enabled", True)
            msg_dict["text"] = f"{self.getl('block_titlebar_msg_definition_enable_text')} - {self.getl('text_on')}"
            self.update_msg(msg_dict)
        elif result == 220:
            self.setv("block_definition_titlebar_msg_enabled", False)
            msg_dict["text"] = f"{self.getl('block_titlebar_msg_definition_enable_text')} - {self.getl('text_off')}"
            self.update_msg(msg_dict)

    def action_footer_btn_detection_left_click(self):
        menu_dict = {
            "position": QCursor().pos(),
            "items": [
                [10, self.getl("block_text_editor_command_list_text"), self.getl("block_text_editor_command_list_tt"), True, [], self.getv("block_text_editor_command_list_icon_path")],
                [20, self.getl("block_text_editor_command_auto_images_text"), self.getl("block_text_editor_command_auto_images_tt"), True, [], self.getv("block_text_editor_command_auto_images_icon_path")],
                [30, self.getl("block_text_editor_command_calculator_text"), self.getl("block_text_editor_command_calculator_tt"), True, [], self.getv("block_text_editor_command_calculator_icon_path")]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        if menu_dict["result"] == 10:
            data_dict = {
                "command": "list"
            }
            self._parent_widget.block_event(self._my_name, "selected", detail=data_dict)
        elif menu_dict["result"] == 20:
            data_dict = {
                "command": "images"
            }
            self._parent_widget.block_event(self._my_name, "selected", detail=data_dict)
        elif menu_dict["result"] == 30:
            data_dict = {
                "command": "calculator"
            }
            self._parent_widget.block_event(self._my_name, "selected", detail=data_dict)

    def action_control_footer_btn_delete_left_click(self):
        # Ask the user to confirm the deletion
        data_dict = {
            "title": self.getl("block_footer_btn_delete_msg_title"),
            "text": self.getl("block_footer_btn_delete_msg_text"),
            "icon_path": self.getv("block_footer_btn_delete_msg_icon_path"),
            "position": "center screen",
            "buttons": [
                [1, self.getl("btn_yes"), "", self.getv("block_footer_btn_delete_msg_btn_yes_icon_path"), True],
                [2, self.getl("btn_no"), "", "", True],
                [3, self.getl("btn_cancel"), "", "", True]
            ]
        }
        utility_cls.MessageQuestion(self._stt, self, data_dict)
        if data_dict["result"] == 1:
            self._parent_widget.block_event(self._my_name, "block_delete")

    def action_control_header_btn_add_left_click(self):
        l = self.getl
        
        # Find all standard and user tags
        db_tag = db_tag_cls.Tag(self._stt)
        tags = db_tag.get_all_tags()
        standard_tags=  []
        user_tags = []
        for tag in tags:
            db_tag.populate_values(tag[0])
            if db_tag.TagUserDefinded == 0:
                standard_tags.append(
                    [
                        db_tag.TagID,
                        db_tag.TagNameTranslated,
                        "",
                        True,
                        [],
                        ""
                    ]
                )
            else:
                user_tags.append(
                    [
                        db_tag.TagID,
                        db_tag.TagName,
                        "",
                        True,
                        [],
                        ""
                    ]
                )
        
        # Create dictionary for menu
        menu_dict = {
            "position": QCursor().pos(),
            "disabled": self._data_dict["tag"],
            "separator": ["m2"],
            "items": [
                ["m1", l("block_header_btn_add_context_standard_text"), l("block_header_btn_add_context_standard_tt"), False, standard_tags, ""],
                ["m2", l("block_header_btn_add_context_user_text"), l("block_header_btn_add_context_user_tt"), False, user_tags, ""],
                ["t1", self.getl("edit_tags_cm_text"), self.getl("edit_tags_cm_tt"), True, [], None]
            ]
        }
        self.set_appv("menu", menu_dict)
        self._send_msg_to_main_win()
        utility_cls.ContextMenu(self._stt, self.parent())
        result = self.get_appv("menu")["result"]
        if result:
            if db_tag.is_valid_tag_id(result):
                new_tags = []
                for tag in self._data_dict["tag"]:
                    new_tags.append(tag)

                if isinstance(result, list):
                    if tag in result:
                        new_tags.append(tag)
                else:
                    new_tags.append(result)
                result_dict = {
                    "old_tag_list": self._data_dict["tag"],
                    "new_tag_list": new_tags,
                    "tag_diff": result
                }
                self._parent_widget.block_event(self._my_name, "tag_changed", result_dict)
            if result == "t1":
                tag_cls.TagView(self._stt, self._parent_widget)

    def action_control_btn_date_left_click(self):
        mouse_pos = QCursor()
        input_text = self._data_dict["record_date"]
        input_dict = {
            "id": self._active_record_id,
            "name": "block_input_box_name",
            "input_hint": self.getl("block_input_box_date_placeholder"),
            "text": input_text,
            "description": self.getl("block_input_box_date_description_text"),
            "position": mouse_pos.pos(),
            "one_line": True,
            "calendar_on_double_click": True,
            "auto_show_calendar": True,
            "auto_apply_calendar": True
        }
        self._send_msg_to_main_win()
        utility_cls.InputBoxSimple(self._stt, self, input_dict)
        if input_dict["result"]:
            dt = utility_cls.DateTime(self._stt)
            date_dict = dt.make_date_dict(input_dict["result"])
            if date_dict:
                result_dict = {
                    "old_date": self._data_dict["record_date"],
                    "new_date": date_dict["date"],
                    "record_id": self._active_record_id
                }
                self._parent_widget.block_event(self._my_name, "date_changed", result_dict)
                self._win_block_control_btn_date_set_text()
                self._set_geometry()
            else:
                msg_dict = {
                    "title": self.getl("msg_box_block_btn_date_invalid_date_title"),
                    "text": self.getl("msg_box_block_btn_date_invalid_date_text"),
                    "icon_path": self.getv("msg_box_wrong_entry_icon_path"),
                    "position": f"{self.mapToGlobal(self.pos()).x()}, {self.mapToGlobal(self.pos()).y()}"
                }
                utility_cls.MessageInformation(self._stt, self, msg_dict)

    def action_control_btn_name_left_click(self):
        mouse_pos = QCursor()
        if self.text() == self.getl("win_block_control_btn_name_empty"):
            input_text = ""
        else:
            input_text = self.text()
        input_dict = {
            "id": self._active_record_id,
            "name": "block_input_box_name",
            "text": input_text,
            "position": mouse_pos.pos(),
            "one_line": True,
            "description": self.getl("block_input_box_name_description_text")
        }
        self._send_msg_to_main_win()
        utility_cls.InputBoxSimple(self._stt, self, input_dict)
        if input_dict["result"] is not None:
            result_dict = {
                "old_name": self.text(),
                "new_name": input_dict["result"],
                "record_id": self._active_record_id
            }
            self._parent_widget.block_event(self._my_name, "name_changed", result_dict)
            name = input_dict["result"]
            if name == "":
                name = self.getl("win_block_control_btn_name_empty")
            self.setText(name)
            self._set_geometry()

    def action_saved_button_left_click(self):
            self._signals.saved_button_check_status(self._active_record_id)
            data = {
                "title": "",
                "text": self.getl("notification_block_data_already_saved"),
                "timer": 800,
                "position": "bottom right" }
            self._signals.block_text_give_focus(self._active_record_id)
            utility_cls.Notification(self._stt, self._parent_widget, data)
    
    def action_save_button_left_click(self):
        data = {
            "title": "",
            "text": self.getl("notification_block_data_saved"),
            "timer": 2000,
            "position": "bottom right" }
        self._signals.block_text_give_focus(self._active_record_id)
        utility_cls.Notification(self._stt, self._parent_widget, data)
    
    def _define_if_saved_button_is_visible(self, record_id: int):
        if self._my_name == "footer_btn_saved" and record_id == self._active_record_id:
            if self.getv("block_show_saved_btn_if_save_is_hidden"):
                if self._data_dict["save"]:
                    self.setVisible(True)
                else:
                    self.setVisible(False)
            else:
                self.setVisible(False)

        if self._my_name == "footer_btn_save":
            if self.getv("block_save_event_hide_save_btn"):
                if self._data_dict["save"]:
                    self.setVisible(False)
                else:
                    self.setVisible(True)
            else:
                self.setVisible(True)

    def _send_msg_to_main_win(self):
        main_dict = {
            "name": self._my_name,
            "action": "cm"
        }
        if self._main_win is not None:
            self._main_win.events(main_dict)

    def _create_button(self):
        self._set_text()
        self._set_apperance()
        self._set_geometry()

        if self._my_name == "footer_btn_detection":
            self.setVisible(False)

    def _set_geometry(self):
        fm = QFontMetrics(self.font())
        width = fm.width(self.text())
        height = fm.height()
        if width < height:
            width = height - self.getv("blocks_buttons_text_width_pad") + self.getv("blocks_buttons_with_no_text_width_pad")
            if width < 1:
                width = 1
        if self.text() != "" and self.getv(f"{self._my_name}_icon_path") != "":
            width += height * 2
        self.setFixedSize(width + self.getv("blocks_buttons_text_width_pad"), height + self.getv("blocks_buttons_text_height_pad"))
        if self.getv(f"{self._my_name}_width") > self.width():
            self.setFixedWidth(self.getv(f"{self._my_name}_width"))
        if self.getv(f"{self._my_name}_height") > self.height():
            self.setFixedHeight(self.getv(f"{self._my_name}_height"))
        icon_size = int(self.contentsRect().height() * self.getv(f"{self._my_name}_icon_height") / 100)
        self.setIconSize(QSize(icon_size, icon_size))

    def _win_block_control_btn_date_set_text(self):
        date_cls = utility_cls.DateTime(self._stt)
        date_dict = date_cls.make_date_dict(self._data_dict["record_date"])
        if self.getv("win_block_controls_show_long_date") == 1:
            date = f'{date_dict["day_name"]}, {date_dict["date"]}'
        elif self.getv("win_block_controls_show_long_date") == 2:
            date = f'{date_dict["day"]}, {date_dict["month_name"]}, {date_dict["year"]}.'
        elif self.getv("win_block_controls_show_long_date") == 3:
            date = f'{date_dict["day_name"]}, {date_dict["day"]}, {date_dict["month_name"]}, {date_dict["year"]}.'
        else:
            date = date_dict["date"]
        self.setText(date)

    def _set_text(self):
        # Text
        if self._tag_id:
            tag = db_tag_cls.Tag(self._stt)
            tag.populate_values(self._tag_id)
            if tag.TagUserDefinded == 0:
                if self._tag_id == 1:
                    self.setText(self.getl(tag.get_tag_name_cleaned()))
                else:
                    self.setText(self.getl(tag.get_tag_name_cleaned()))
            else:
                self.setText(tag.TagName)
        else:
            if self._my_name == "win_block_control_btn_day":
                record = db_record_cls.Record(self._stt, self._active_record_id)
                day1 = record.get_date_of_first_entry()
                days = UTILS.DateTime.DateTime.get_date_difference(UTILS.DateTime.DateTime.today(), day1).total_days
                self.setText(f"{self.getl('win_block_control_btn_day_text')}: {days}")
            elif self._my_name == "win_block_control_btn_date":
                self._win_block_control_btn_date_set_text()
            elif self._my_name == "win_block_control_btn_name":
                name = self._data_dict["name"]
                if name == "":
                    name = self.getl("win_block_control_btn_name_empty")
                self.setText(name)
            else:
                self.setText(self.getl(f"{self._my_name}_text"))

        self.setToolTip(self.getl(f"{self._my_name}_tt"))
        self.setStatusTip(self.getl(f"{self._my_name}_sb_text"))

    def app_setting_updated(self, data: dict):
        self._set_apperance(settings_updated=True)

    def _set_apperance(self, settings_updated: bool = False):
        # Apperance
        self.setAutoDefault(False)
        self.setDefault(False)
        self.setFlat(self.getv(f"{self._my_name}_flat"))
        self.setShortcut(self.getv(f"{self._my_name}_shortcut"))
        if self.getv(f"{self._my_name}_icon_path"):
            self.setIcon(QIcon(self.getv(f"{self._my_name}_icon_path")))
        font = QFont(self.getv(f"{self._my_name}_font_name"), self.getv(f"{self._my_name}_font_size"))
        font.setWeight(self.getv(f"{self._my_name}_font_weight"))
        font.setItalic(self.getv(f"{self._my_name}_font_italic"))
        font.setUnderline(self.getv(f"{self._my_name}_font_underline"))
        font.setStrikeOut(self.getv(f"{self._my_name}_font_strikeout"))
        self.setFont(font)
        self.setStyleSheet(self.getv(f"{self._my_name}_stylesheet"))
        self.setEnabled(self.getv(f"{self._my_name}_enabled"))
        self.setVisible(self.getv(f"{self._my_name}_visible"))
        if not settings_updated:
            if self.text() == "" and self._my_name == "footer_btn_detection":
                self.setVisible(False)

    def close_me(self):
        self.get_appv("cm").remove_all_context_menu()

        try:
            self.hide()

            for item in self._messages:
                if item.get("timer"):
                    item.get("timer").stop()
            self.timer.close_me()

            QCoreApplication.processEvents()
            self._messages = []
            self.widget_handler.close_me()
            self.deleteLater()
            self.setParent(None)

        except Exception as e:
            UTILS.LogHandler.add_log_record(f"#1: Failed to close block button in #2 method.\nException: #3", ["WinBlock:Button", "close_me", str(e)], warning_raised=True)




