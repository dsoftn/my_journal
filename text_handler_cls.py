from PyQt5.QtWidgets import QFrame, QPushButton, QTextEdit, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QPixmap, QCursor, QTextCharFormat, QColor, QDrag
from PyQt5.QtCore import Qt, QCoreApplication, QRect, QPoint, QTimer, QMimeData
from PyQt5 import uic, QtGui

import time
from math import *
import random
import difflib
import os

import settings_cls
import db_record_data_cls
import utility_cls
import definition_cls
import db_definition_cls
import db_media_cls
import webbrowser
import wikipedia_cls
import block_widgets_cls
import dict_cls
import qwidgets_util_cls
import UTILS
import obj_blocks
import obj_block


class AutoCompleteData:
    """ This class calculates the autocomplete data for the diary.
    It contains the following variables:
        self.complete_diary (list): List of tuples with count and text for autocomplete.
    """

    FAVORITE_BLOCK_AMOUNT = 0
    FAVORITE_POINTS_AMOUNT = 1_000_000

    def __init__(self, settings: settings_cls.Settings):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.complete_diary = self.calculate_data()

    def calculate_data(self) -> list:
        blocks: obj_blocks.Blocks = self.get_appv("blocks")
        text_diary = [block.RecBody for block in blocks.get_block_list(None)]
        
        complete_diary = []
        for idx_block, i in enumerate(text_diary):
            if idx_block >= len(text_diary) - self.FAVORITE_BLOCK_AMOUNT:
                start_count = self.FAVORITE_POINTS_AMOUNT
            else:
                start_count = 0

            for j in i.splitlines():
                if not j.strip():
                    continue
                if j in [k[1] for k in complete_diary]:
                    for idx, k in enumerate(complete_diary):
                        if k[1] == j:
                            complete_diary[idx][0] += 1
                            if complete_diary[idx][0] < start_count:
                                complete_diary[idx][0] += start_count
                else:
                    complete_diary.append([1, j])
                    if complete_diary[-1][0] < start_count:
                        complete_diary[-1][0] += start_count
        
        return complete_diary

    def update_data(self, text: str) -> None:
        new_data = [x for x in text.splitlines() if x.strip()]
        
        data_to_add = []
        for line in new_data:
            for idx, item in enumerate(self.complete_diary):
                if line == item[1]:
                    self.complete_diary[idx][0] += 1
                    if self.complete_diary[idx][0] < self.FAVORITE_POINTS_AMOUNT:
                        self.complete_diary[idx][0] += self.FAVORITE_POINTS_AMOUNT
                    break
            else:
                data_to_add.append([self.FAVORITE_POINTS_AMOUNT + 1, line])
        
        self.complete_diary.extend(data_to_add)
        UTILS.Signal.emit_auto_complete_data_updated()

    def get_data(self) -> list:
        return self.complete_diary


class AutoComplete(QFrame):
    """
    self._ac_list = [ rank, word ]
    """

    def __init__(self, settings: settings_cls.Settings, text_edit_object: QTextEdit, name: str = "autocomplete", main_win = None, widget_handler: qwidgets_util_cls.WidgetHandler = None, *args, **kwargs):
        if main_win is None:
            self._parent_widget = settings.app_setting_get_value("main_win")
        else:
            self._parent_widget = main_win

        super().__init__(self._parent_widget, *args, **kwargs)
        self.setParent(self._parent_widget)
        self.setVisible(False)

        self._my_name = name
        self.txt_box = text_edit_object
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self._signals: utility_cls.Signals = self.get_appv("signal")
        self._main_win = main_win
        self.widget_handler = widget_handler

        self.complete_diary: list = self.get_appv("ac_data").get_data()

        # AutoComplete list to show
        self._ac_list = []
        self.selected_item = None
        self.completed_part = None

        self._frame_apperance()

        # Check is there app setting 'ac'
        if "ac" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("ac", {}, save_to_file=True)
        self.ac_dict = self.get_appv("ac")

        # Make buttons
        self.btn_list = []
        for i in range(self.getv("autocomplete_items_number")):
            btn = QPushButton(self)
            self._define_buttons_apperance(btn, "autocomplete_btn")
            btn.setVisible(False)
            self.btn_list.append(btn)

        # Connect events with slots
        for button in self.btn_list:
            button.clicked.connect(self._button_click)
            if self.widget_handler:
                self.widget_handler.add_QPushButton(button, main_win=self)
        if self.widget_handler:
            self.widget_handler.activate()

        # Connect signals with slots
        UTILS.Signal.signalAutoCompleteDataUpdated.connect(self._autocomplete_data_updated)

        UTILS.LogHandler.add_log_record("#1: Engine started.", ["AutoComplete"])

    def _autocomplete_data_updated(self) -> None:
        self.complete_diary: list = self.get_appv("ac_data").get_data()

    def select_item(self):
        button = self.btn_list[self.selected_item]
        ac_text = button.text()
        ac_text = ac_text[len(self.completed_part):]
        data_dict = {
            "word": button.text(),
            "ac": ac_text,
            "record_id": self.txt_box._active_record_id
        }
        self.setVisible(False)
        self._signals.auto_complete_selected(data_dict)

    def _button_click(self):
        button = self.sender()
        ac_text = button.text()
        ac_text = ac_text[len(self.completed_part):]
        data_dict = {
            "word": button.text(),
            "ac": ac_text,
            "record_id": self.txt_box._active_record_id
        }
        self.setVisible(False)
        self._signals.auto_complete_selected(data_dict)
        self._signals.block_text_give_focus(self.txt_box._active_record_id)

    def move_up(self):
        if self.selected_item > 0:
            self.selected_item -= 1
        else:
            self.selected_item = len(self._ac_list) - 1
        self._mark_selected_item()
        
    def move_down(self):
        if self.selected_item < len(self._ac_list) - 1:
            self.selected_item += 1
        else:
            self.selected_item = 0
        self._mark_selected_item()

    def delete_item(self):
        # Changes for _make_ac_list2   !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.hide_ac()
        return

        item = self._ac_list[self.selected_item][1]
        idx = -1
        for index, i in enumerate(self.ac_dict[item[:2]]):
            if i[1] == item:
                idx = index
                break
        if idx >= 0:
            self.ac_dict[item[:2]].pop(idx)

        selected = self.selected_item
        if self.show_ac():
            if len(self._ac_list) <= selected:
                selected = len(self._ac_list) - 1
            self._mark_selected_item()

    def hide_ac(self):
        self.setVisible(False)
    
    def show_ac(self) -> bool:
        """
        Displays an auto complete list.
        Returns:
            True - if the list is displayed
            False - if there is no data to display
            None - if auto complete is turned off            
        """
        # If autocomplete is off, return None
        if not self.getv("show_autocomplete"):
            return None

        # If Calculator mode is True, return None
        if self.txt_box._active_record_id in self.get_appv("calculator"):
            return None

        # If cursor is not at end return None
        if self.txt_box.textCursor().position() < len(self.txt_box.toPlainText()):
            self.hide_ac()
            return None

        # Create list of items
        text = self.txt_box.toPlainText()
        text = text[:self.txt_box.textCursor().position()]

        # Changes for _make_ac_list2   !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # self._ac_list = self._make_ac_list(text)
        text = self.txt_box.toPlainText()
        text = text[:self.txt_box.textCursor().position()]
        if text.find("\n") != -1:
            text = text.split("\n")[-1]
        self._ac_list = self._make_ac_list2(text)


        # If there is no items dont show QFrame and return False
        if not self._ac_list:
            self.setVisible(False)
            self.selected_item = None
            return False
        
        self._create_frame_with_items()

        # Find Position
        cursor_pos = self.txt_box.mapToGlobal(self.txt_box.cursorRect().bottomRight())
        ac_pos = self._parent_widget.mapFromGlobal(cursor_pos)
        # Move QFrame bottom right if possible
        x = ac_pos.x()
        if x + self.width() > self._parent_widget.contentsRect().width():
            x = self._parent_widget.contentsRect().width() - self.width()
        if x < 0:
            x = 0
        y = ac_pos.y()
        if y + self.height() > self._parent_widget.contentsRect().height():
            cursor_pos = self.txt_box.mapToGlobal(self.txt_box.cursorRect().topRight())
            ac_pos = self._parent_widget.mapFromGlobal(cursor_pos)
            y = ac_pos.y() - self.height()
            if y < 0:
                y = 0

        self.move(x, y)
        self.setVisible(True)
        return True

    def _create_frame_with_items(self):
        # Define buttons size
        fm = QFontMetrics(self.btn_list[0].font())
        w = 0
        for item in self._ac_list:
            if fm.width(item[1]) > w:
                w = fm.width(item[1])
        w += self.getv("autocomplete_button_width_pad")
        h = fm.height() + self.getv("autocomplete_button_height_pad")
        
        # Set buttons position and size
        for button in self.btn_list:
            button.setVisible(False)
        for idx, item in enumerate(self._ac_list):
            self.btn_list[idx].setText(item[1])
            self.btn_list[idx].move(0, idx * h)
            self.btn_list[idx].resize(w, h)
            self.btn_list[idx].setVisible(True)

        # Set Frame size
        self.resize(w, h * (idx + 1))
        self.selected_item = 0
        self._mark_selected_item()

    def _mark_selected_item(self):
        for idx, button in enumerate(self.btn_list):
            if idx == self.selected_item:
                button.setStyleSheet(self.getv("autocomplete_selected_btn_stylesheet"))
            else:
                button.setStyleSheet(self.getv("autocomplete_btn_stylesheet"))

    def _make_ac_list2(self, txt: str) -> list:
        # Check is text valid
        if not len(txt):
            return None
        
        self.completed_part = txt

        key_list = []
        for line in self.complete_diary:
            if line[1].startswith(txt) and line[1] != txt:
                key_list.append(line)

        if key_list:
            key_list = sorted(key_list, key=lambda x: x[0], reverse=True)
            if len(key_list) > self.getv("autocomplete_items_number"):
                key_list = key_list[:self.getv("autocomplete_items_number")]
            return key_list
        else:
            return False

    def _make_ac_list(self, txt: str) -> list:
        # Check is text valid
        if len(txt) < 2:
            return None
        if UTILS.TextUtility.is_special_char(txt[-1]):
            self._add_word_to_dict(txt)
            return None
        word = self._find_last_word(txt)
        if len(word) < 2:
            return None
        key = word[:2]
        if " " in key:
            return None
        self.completed_part = word
        # If key is in dict, make autocomplete list
        if key in self.ac_dict:
            key_list = []
            for item in self.ac_dict[key]:
                if item[1][:len(word)] == word:
                    key_list.append(item)
                    if len(key_list) == self.getv("autocomplete_items_number"):
                        break
            if key_list:
                return key_list
            else:
                return False
        
        # If key is not in dict, add key to dict
        self.ac_dict[key] = []
        return False

    def _add_word_to_dict(self, txt: str):
        # Changes for _make_ac_list2   !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return
        
        # Find last word
        words = self._find_last_word(txt, self.getv("autocomplete_max_number_of_suggested_words"))
        for word in words:
            self._update_dictionary(word)

    def _update_dictionary(self, word: str):
        # If word is longer than 2 chars and not in list then add word to dict
        if len(word) < self.getv("autocomplete_minimum_word_lenght"):
            return
        # If word start with '@' dont add to dict
        if word[:1] == "@":
            return
        if word[:2] not in self.ac_dict:
            self.ac_dict[word[:2]] = []
        for i in self.ac_dict[word[:2]]:
            if i[1] == word:
                self._rank_word(word)
                return
        self.ac_dict[word[:2]].append([10, word])
        self.ac_dict[word[:2]].sort(reverse=True)
        if len(self.ac_dict[word[:2]]) > self.getv("autocomplete_items_in_memory"):
            self.ac_dict[word[:2]].pop(-1)

    def _rank_word(self, word: str):
        # Increase the rank of the selected word by 2 and decrease all words before by 1
        # Range: 0 - 20
        for idx, i in enumerate(self.ac_dict[word[:2]]):
            if i[1] == word:
                self.ac_dict[word[:2]][idx][0] += 2
                if self.ac_dict[word[:2]][idx][0] > 20:
                    self.ac_dict[word[:2]][idx][0] = 20
                self.ac_dict[word[:2]].sort(reverse=True)
                return
            else:
                self.ac_dict[word[:2]][idx][0] -= 1
                if self.ac_dict[word[:2]][idx][0] < 0:
                    self.ac_dict[word[:2]][idx][0] = 0

    def _find_last_word(self, txt: str, number_of_words: int = None) -> str:
        if not txt:
            return txt

        # Delete last characters that marks end of word
        delete_last_char = True
        while delete_last_char:
            if UTILS.TextUtility.is_special_char(txt[-1]):
                if len(txt) > 1:
                    txt = txt[:-1]
                else:
                    delete_last_char = False
            else:
                delete_last_char = False

        # Find beginning of sentence and work only with that part of text
        begin_of_sen = 0
        txt = ". " + txt
        for i in UTILS.TextUtility.END_OF_SENTENCE:
            if txt.rfind(i) > begin_of_sen:
                begin_of_sen = txt.rfind(i)
        txt = txt[begin_of_sen + 1:]
        txt = txt.lstrip()

        # In case that is this first word in text
        if number_of_words is None:        
            txt = UTILS.TextUtility.replace_special_chars(txt)

            txt = " " + txt
            txt = txt[txt.rfind(" ") + 1:]
            return txt

        # In case that we have many words
        word_list = [x for x in txt.split(" ") if x != ""]
        if len(word_list) < number_of_words:
            word_count = len(word_list)
        else:
            word_count = number_of_words
        
        words = []
        for i in range(len(word_list) - word_count, len(word_list)):
            add_word = ""
            for j in range(i, len(word_list)):
                add_word += word_list[j] + " "
            add_word = add_word[:-1]
            words.append(add_word)
        return words

    def update_autocomplete_dictionary(self, text: str) -> None:
        # Changes for _make_ac_list2   !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return
    
        """
        It analyzes the received text and inserts each word from the text into the
        autocomplete dictionary if it does not exist.
        The function is used when the user pastes a large amount of text into the text box.
        """
        # Show Notification
        data_dict = {
            "title": self.getl("ac_msg_title"),
            "text": self.getl("ac_msg_text"),
            "timer": None,
            "animation": False,
            "icon": self.getv("autocomplete_msg_update_icon")
        }
        if len(text) > 1200:
            has_notification = True
        else:
            has_notification = False
        
        if has_notification:
            notif = utility_cls.Notification(self._stt, self._parent_widget, data_dict)
        
        QCoreApplication.processEvents()
        text_list = [x for x in text.split(" ") if x != ""]
        
        txt = ""
        for i in text_list:
            txt += i + " "
            self._add_word_to_dict(txt)
        
        if has_notification:
            notif.close_me()

    def _define_widgets(self):
        self._frame_apperance()
    
    def _frame_apperance(self):
        self.setFrameShape(self.getv(f"{self._my_name}_frame_shape"))
        self.setFrameShadow(self.getv(f"{self._my_name}_frame_shadow"))
        self.setLineWidth(self.getv(f"{self._my_name}_line_width"))
        self.setStyleSheet(self.getv(f"{self._my_name}_stylesheet"))

    def _define_buttons_apperance(self, btn: QPushButton, name: str):
        # Apperance
        btn.setAutoDefault(False)
        btn.setDefault(False)
        btn.setFlat(self.getv(f"{name}_flat"))
        font = QFont(self.getv(f"{name}_font_name"), self.getv(f"{name}_font_size"))
        font.setWeight(self.getv(f"{name}_font_weight"))
        font.setItalic(self.getv(f"{name}_font_italic"))
        font.setUnderline(self.getv(f"{name}_font_underline"))
        font.setStrikeOut(self.getv(f"{name}_font_strikeout"))
        btn.setFont(font)
        btn.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def close_me(self):
        for button in self.btn_list:
            if self.widget_handler:
                self.widget_handler.remove_child(button)

        UTILS.LogHandler.add_log_record("#1: Engine stopped.", ["AutoComplete"])
        self.deleteLater()
        self.setParent(None)


class SimpleDefinitionExtraImage(QLabel):
    def __init__(self, settings: settings_cls.Settings, parent_widget):
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
        self._timer_fade_out = QTimer(self)
        self._timer_delay = QTimer(self)
        self._timer_start_fade_out = QTimer(self)
        self._is_active = False
        # self._is_running = False
        self._extra_image_id = None
        self._call_log = []
        self._definitions_q = []

        self._data = self._stt.custom_dict_load(self.getv("def_extra_images_settings_file_path"))
        self.effects = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effects)
        self._delay_data = None
        self._definition_id = None

        # Connect events with slots
        self._timer_fade_out.timeout.connect(self._fade_out)
        self._timer_start_fade_out.timeout.connect(self._start_fade_out)
        self.mousePressEvent = self.mouse_press_event
        

        self._define_label()

    def mouse_press_event(self, e: QtGui.QMouseEvent):
        self.hide_me()

    def change_definition_geometry(self, def_frame_position_from_parent: QPoint = None, def_frame_rect_map_parent: QRect = None, def_id: int = None):
        if def_id != self._definition_id:
            return
        
        if def_frame_position_from_parent:
            self._def_frame_pos = def_frame_position_from_parent
        if def_frame_rect_map_parent:
            self._def_frame_rect = def_frame_rect_map_parent

    def show_me(self, cursor_pos_map_parent: QPoint = None, def_frame_position_from_parent: QPoint = None, def_frame_rect_map_parent: QRect = None, extra_image_id: int = None, delay: int = None, definition_id: str = None, caller: str = None):
        self._is_active = False
        if definition_id:
            if self._definition_id != definition_id:
                self.set_appv("extra_images_pool", [])
            self._definition_id = definition_id
        
        if caller == "SimpleDef":
            self._definitions_q.append(definition_id)
            self._extra_image_id = None

        if caller == "self":
            if len(self._call_log) > 0:
                return
            
            if not self._definitions_q:
                if isinstance(self._timer_start_fade_out, QTimer):
                    self._timer_start_fade_out.stop()
                return

            self._is_active = True

            self._extra_image_id = extra_image_id
            self._cursor_pos: QPoint = cursor_pos_map_parent
            self._def_frame_rect: QRect = def_frame_rect_map_parent
            self._def_frame_pos: QPoint = def_frame_position_from_parent
            self.setVisible(True)
            self.effects.setOpacity(1)
            self.load_random_image(caller="show_me")
            if self._extra_image_id:
                self.setVisible(True)
                self.raise_()
                if self.getv("def_extra_image_auto_hide"):
                    self._timer_start_fade_out.start(self.getv("def_extra_image_auto_hide"))
            else:
                self.setVisible(False)
                self._is_active = False
            return


        if delay is not None:
            self._call_log.append(definition_id)
            if delay == 0:
                delay = 1
            self._delay_data = [cursor_pos_map_parent, def_frame_position_from_parent, def_frame_rect_map_parent, extra_image_id, definition_id]
            self._timer_delay.singleShot(delay, self.show_me)
            return
        else:
            self._call_log.pop(0)
            if self._delay_data is None:
                return

            cursor_pos_map_parent = self._delay_data[0]
            def_frame_position_from_parent = self._delay_data[1]
            def_frame_rect_map_parent = self._delay_data[2]
            extra_image_id = self._delay_data[3]
            def_id = self._delay_data[4]

            if len(self._call_log) == 0:
                self._delay_data = None

            self.show_me(
                cursor_pos_map_parent=cursor_pos_map_parent,
                def_frame_position_from_parent=def_frame_position_from_parent,
                def_frame_rect_map_parent=def_frame_rect_map_parent,
                extra_image_id=extra_image_id,
                delay=None,
                definition_id=def_id,
                caller="self"
            )
            return

    def _start_fade_out(self):
        if not self._is_active:
            self._timer_start_fade_out.stop()
            return

        if self.getv("def_extra_image_auto_hide_fade_out_duration") > 80:
            duration = int(self.getv("def_extra_image_auto_hide_fade_out_duration") / 40)
            if not self._timer_fade_out.isActive():
                self._timer_fade_out.start(duration)
            else:
                self._timer_fade_out.stop()
                self.hide_me()
        else:
            self.hide_me(continue_next=True)

    def _fade_out(self):
        if not self._is_active:
            return

        self.effects.setOpacity(self.effects.opacity() - 0.05)
        
        if self.effects.opacity() < 0.025:
            self._timer_fade_out.stop()
            self.hide_me(continue_next=True)

    def hide_me(self, continue_next: bool = False, definition_id: int = None):
        if definition_id:
            if definition_id not in self._definitions_q:
                return
        self.effects.setOpacity(1)

        for idx, i in enumerate(self.get_appv("extra_images")):
            if i == self._extra_image_id:
                self.get_appv("extra_images").pop(idx)
                break
    
        if continue_next and self.getv("def_extra_image_show_next_after_hide") and self._is_active:
            for idx, i in enumerate(self.get_appv("extra_images_around_def")):
                if i[1] == self._extra_image_id:
                    self.get_appv("extra_images_around_def").pop(idx)
                    break
            self._extra_image_id = None
            self.load_random_image(caller="hide_me (With continue_next)")
            return
        
        if self._definitions_q:
            self._definitions_q.pop(0)

        self.setVisible(False)
        self.set_appv("extra_images", [])
        self.set_appv("extra_images_around_def", [])
        self._extra_image_id = None
        self._is_active = False
        self._definition_id = None

    def select_random_image(self):
        match self.getv("def_extra_image_source"):
            case 1:
                self._select_random_image_toon()
            case 2:
                self._select_random_image_media("def")
            case 3:
                self._select_random_image_media("blocks")
            case 4:
                self._select_random_image_media("app")
            case 5:
                self._select_random_image_custom()
                
    def _select_random_image_custom(self):
        if not self.getv("def_extra_image_custom_source_folder_path"):
            return
        if not os.path.isdir(self.getv("def_extra_image_custom_source_folder_path")):
            return
        
        # Get media pool
        media_pool = self._custom_folder_image_pool(self.getv("def_extra_image_custom_source_folder_path"))

        self._extra_image_id = self._get_next_image(media_pool)
        
    def _custom_folder_image_pool(self, base_path: str = ""):
        image_pool = []
        abs_path = os.path.abspath(base_path)
        file_list = os.listdir(abs_path)
        for file in file_list:
            file_path = os.path.join(abs_path, file)
            if os.path.isfile(file_path) and file.lower().endswith((".jpg", ".jpeg", ".svg", ".png", ".webp", ".gif")):
                image_pool.append(file_path)
            if os.path.isdir(file_path) and self.getv("def_extra_image_custom_source_add_subfolders"):
                image_pool += self._custom_folder_image_pool(file_path)

        return image_pool            

    def _select_random_image_media(self, src: str):
        media_pool = []
        media_cls = db_media_cls.Media(self._stt)

        match src:
            case "def":
                if self._definition_id:
                    def_cls = db_definition_cls.Definition(self._stt, self._definition_id)
                    media_pool = def_cls.definition_media_ids
            case "blocks":
                rec_data = db_record_data_cls.RecordData(self._stt)
                rec_data_items = [x[3] for x in rec_data.get_all_record_data()]

                all_media_ids = [x[0] for x in media_cls.get_all_media()]

                media_pool = [x for x in rec_data_items if x in all_media_ids]
            case "app":
                media_pool = [x[0] for x in media_cls.get_all_media()]
        
        if media_pool:
            self._extra_image_id = self._get_next_image(media_pool)
        else:
            self._extra_image_id = None

    def _get_next_image(self, image_list: list) -> int:
        """
        The "extra_images" variable contains the currently displayed images.
        This function adds the image it finds to that variable.
        If this function finds an image that for some reason cannot be displayed later because,
        for example, it does not fit in the frame of the parent window,
        then "extra_images" should be updated and the image removed from that list.
        Updating the "extra_images" variable mainly refers to the situation when the display mode is set "around the definition"
        The "extra_images_pool" variable should be updated in a similar way.
        """
        random.shuffle(image_list)
        old_images = [x for x in self.get_appv("extra_images_pool")]
        old_images_frq = [(old_images.count(x), x) for x in image_list]
        old_images_frq.sort(key=lambda x: x[0])
        image_list = [x[1] for x in old_images_frq]
        
        if len(self.get_appv("extra_images")) >= self.getv("def_extra_image_max_number_of_images") and len(self.get_appv("extra_images")) > 0:
            self.get_appv("extra_images").pop(0)
        for i in image_list:
            if i not in self.get_appv("extra_images"):
                self.get_appv("extra_images").append(i)
                self.get_appv("extra_images_pool").append(i)
                return i
        
        return None 

    def _select_random_image_toon(self):
        valid_images = [x for x in self._data if self._data[x]["defined"] and not self._data[x]["rejected"]]
        if len(valid_images) > 0:
            random_index = random.randint(0, len(valid_images)-1)
        else:
            self._extra_image_id = None
            return
        self._extra_image_id = valid_images[random_index]

    def load_random_image(self, caller: str = None):
        if self._extra_image_id is None:
            self.select_random_image()

        if self.getv("def_extra_image_source") == 1:
            if self.getv("def_extra_image_layout") == 1:
                for i in range(50):
                    if self.is_image_valid():
                        break
                    self.select_random_image()
                else:
                    self._extra_image_id = None
                self.load_image_toon()
                self._animate_me_in()
            elif self.getv("def_extra_image_layout") == 2:
                self.load_label_around_def()
            
        elif self.getv("def_extra_image_source") in [2, 3, 4, 5]:
            if self.getv("def_extra_image_layout") == 1:
                self.load_image_media()
            elif self.getv("def_extra_image_layout") == 2:
                self.load_label_around_def()

    def load_label_around_def(self):
        if not self._extra_image_id:
            self.select_random_image()
        img = None
        if self.getv("def_extra_image_source") == 1:
            img = QPixmap()
            img.load(self.getv("def_extra_images_folder_path") + self._extra_image_id)
            self.set_label_to_available_pos_around_def(img)
        elif self.getv("def_extra_image_source") in [2, 3, 4, 5]:
            if self._extra_image_id:
                if self.getv("def_extra_image_source") == 5:
                    img = QPixmap()
                    result = img.load(self._extra_image_id)
                    if not result:
                        return None
                else:
                    db_media = db_media_cls.Media(self._stt)
                    if db_media.is_media_exist(self._extra_image_id):
                        db_media.load_media(self._extra_image_id)
                        img = QPixmap()
                        img.load(db_media.media_file)
            self.set_label_to_available_pos_around_def(img)

    def set_label_to_available_pos_around_def(self, pixmap_obj: QPixmap) -> bool:
        around_pos = None
        pos = None
        for i in range(1, 11):
            is_free = True
            for item in self.get_appv("extra_images_around_def"):
                if item[0] == i:
                    is_free = False
                    
            if is_free:
                pos = self._can_label_fit_in_pos_around_def(i, pixmap_obj)
                if pos:
                    around_pos = i
                    break

        if not pos:
            # Since the image is not currently suitable for display here, we will
            # update the variables "extra_images" and "extra_images_pool" to maintain the accuracy
            # of the information about the displayed images.
            for idx, i in enumerate(self.get_appv("extra_images")):
                if i == self._extra_image_id:
                    self.get_appv("extra_images").pop(idx)
                    break
            for idx, i in enumerate(self.get_appv("extra_images_pool")):
                if i == self._extra_image_id:
                    self.get_appv("extra_images_pool").pop(idx)
                    break
            self._extra_image_id = None

            img = QPixmap()
            self.setPixmap(img)
            return False
        
        self.move(pos[0], pos[1])
        self.resize(pos[2], pos[3])
        self.setPixmap(pixmap_obj)
        self.setScaledContents(True)
        self.get_appv("extra_images_around_def").append([around_pos, self._extra_image_id])
        self._animate_me_in()
        return True
        
    def _can_label_fit_in_pos_around_def(self, position: int, pixmap_obj: QPixmap) -> tuple:
        if pixmap_obj is None or not pixmap_obj.width() or not pixmap_obj.height():
            return False
        
        scale_x = pixmap_obj.width() / pixmap_obj.height()

        result = None

        match position:
            case 1:
                h = self._def_frame_rect.height()
                w = int(h * scale_x)
                x = self._def_frame_pos.x() - w
                y = self._def_frame_pos.y()
                result = (x, y, w, h)
            case 2:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() + self._def_frame_rect.height()
                x = self._def_frame_pos.x() - w
                result = (x, y, w, h)
            case 3:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() + self._def_frame_rect.height()
                x = self._def_frame_pos.x()
                result = (x, y, w, h)
            case 4:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() + self._def_frame_rect.height()
                x = self._def_frame_pos.x() + w
                result = (x, y, w, h)
            case 5:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() + self._def_frame_rect.height()
                x = self._def_frame_pos.x() + w * 2
                result = (x, y, w, h)
            case 6:
                h = self._def_frame_rect.height()
                w = int(h * scale_x)
                x = self._def_frame_pos.x() + self._def_frame_rect.width()
                y = self._def_frame_pos.y()
                result = (x, y, w, h)
            case 7:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() - h
                x = self._def_frame_pos.x() + w * 2
                result = (x, y, w, h)
            case 8:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() - h
                x = self._def_frame_pos.x() + w
                result = (x, y, w, h)
            case 9:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() - h
                x = self._def_frame_pos.x()
                result = (x, y, w, h)
            case 10:
                w = int(self._def_frame_rect.width() / 2)
                h = int(w / scale_x)
                y = self._def_frame_pos.y() - h
                x = self._def_frame_pos.x() - w
                result = (x, y, w, h)

        if self._check_is_label_has_valid_position(x, y, w, h):
            result = (x, y, w, h)
            return result
        return None

    def _check_is_label_has_valid_position(self, x: int, y: int, w: int, h: int) -> bool:
        if x < 0 or x + w > self._parent_widget.contentsRect().width():
            return False
        if y < 0 or y + h > self._parent_widget.contentsRect().height():
            return False
        if self._cursor_pos.x() in range(x, x + w) and self._cursor_pos.y() in range(y, y + h):
            return False
        return True

    def load_image_media(self):
        if not self._extra_image_id:
            return

        if self.getv("def_extra_image_source") == 5:
            img = QPixmap(self._extra_image_id)
        else:
            media = db_media_cls.Media(self._stt, self._extra_image_id)
            img = QPixmap(media.media_file)
        
        for i in range(500):
            pos = self.get_position(img)
            if pos:
                break
        
        if pos:
            self.move(pos[0], pos[1])
            self.resize(pos[2], pos[3])
            self.setPixmap(img)
            self.setScaledContents(True)
            self._animate_me_in()

    def _animate_me_in(self):
        sleep_time = self.getv("def_extra_image_animate_show")
        if not sleep_time:
            return
        
        step_scale = int(9 + (sleep_time - 100) / 14)
        if step_scale < 1:
            step_scale = 1
        if step_scale > 50:
            step_scale = 50

        sleep_time = sleep_time / 1000

        x = self.pos().x()
        y = self.pos().y()
        w = self.width()
        h = self.height()

        s = w / h
        
        step_x = w / 2 / step_scale
        step_y = h / 2 / step_scale

        animate_mode_pool = [
            "grove",
            "from_left_up",
            "from_right_up",
            "from_left_down",
            "from_right_down"
            ]

        animate_mode = animate_mode_pool[random.randint(0, len(animate_mode_pool) - 1)]

        match self.getv("def_extra_image_animate_style"):
            case 1:
                return
            case 2:
                animate_mode = "grove"
            case 3:
                animate_mode = "from_left_up"
            case 4:
                animate_mode = "from_right_up"
            case 5:
                animate_mode = "from_left_down"
            case 6:
                animate_mode = "from_right_down"

        from_left_up_step_x = x / step_scale
        from_left_up_step_y = y / step_scale
        from_right_up_step_x = (self._parent_widget.contentsRect().width() - x) / step_scale
        from_right_up_step_y = (self._parent_widget.contentsRect().height() - y) / step_scale

        if self.pixmap() is None:
            step_scale = 0

        for i in range(step_scale):
            if animate_mode == "grove":
                new_x = int((x + w / 2) - step_x * i)
                new_y = int((y + h / 2) - step_y * i)
                new_w = int(w / step_scale * i)
                new_h = int(h / step_scale * i)
            elif animate_mode == "from_left_up":
                new_x = int(from_left_up_step_x * i)
                new_y = int(from_left_up_step_y * i)
                new_w = int(w / step_scale * i)
                new_h = int(h / step_scale * i)
            elif animate_mode == "from_right_up":
                new_x = int(self._parent_widget.contentsRect().width() - from_right_up_step_x * i)
                new_y = int(from_left_up_step_y * i)
                new_w = int(w / step_scale * i)
                new_h = int(h / step_scale * i)
            elif animate_mode == "from_left_down":
                new_x = int(from_left_up_step_x * i)
                new_y = int(self._parent_widget.contentsRect().height() - from_right_up_step_y * i)
                new_w = int(w / step_scale * i)
                new_h = int(h / step_scale * i)
            elif animate_mode == "from_right_down":
                new_x = int(self._parent_widget.contentsRect().width() - from_right_up_step_x * i)
                new_y = int(self._parent_widget.contentsRect().height() - from_right_up_step_y * i)
                new_w = int(w / step_scale * i)
                new_h = int(h / step_scale * i)

            self.move(new_x, new_y)
            self.resize(new_w, new_h)
            # QCoreApplication.processEvents()
            self.repaint()
            time.sleep(sleep_time / step_scale)
        
        self.move(x, y)
        self.resize(w, h)

    def get_position(self, image: QPixmap) -> tuple:
        x = random.randint(0, self._parent_widget.contentsRect().width())
        y = random.randint(0, self._parent_widget.contentsRect().height())

        limit = int(min([self._parent_widget.contentsRect().width(), self._parent_widget.contentsRect().height()]))

        size = random.randint(int(limit * 0.4), int(limit * 0.75))

        scale = image.width() / image.height()

        if scale < 1:
            h = size
            w = int(h * scale)
        else:
            w = size
            h = int(w / scale)
        
        if x + w > self._parent_widget.contentsRect().width() or y + h > self._parent_widget.contentsRect().height():
            return None

        if self._cursor_pos.x() in range(x, x + w) and self._cursor_pos.y() in range(y, y + h):
            return None
        else:
            return (x, y, w, h)

    def load_image_toon(self):
        if not self._extra_image_id:
            return

        img = QPixmap()

        if self._extra_image_id:
            file = f"{self.getv('def_extra_images_folder_path')}{self._extra_image_id}"
            img.load(file)
        
        self.setPixmap(img)
        self.setScaledContents(True)

    def is_image_valid(self, dont_draw_image: bool = False) -> bool:
        if not self._extra_image_id:
            return False
        
        item = self._extra_image_id

        x = None
        y = None
        w = None
        h = None

        if self._data[item]["y_rel"] == "up":
            y = self._def_frame_pos.y() + self._data[item]["y"]
        else:
            y = self._def_frame_pos.y() + self._def_frame_rect.height() + self._data[item]["y"]
        
        if self._data[item]["x_rel"] == "left":
            x = self._def_frame_pos.x() + self._data[item]["x"]
        else:
            x = self._def_frame_pos.x() + self._def_frame_rect.width() + self._data[item]["x"]
        
        w = self._data[item]["w"]
        h = self._data[item]["h"]

        if x is None or y is None or w is None or h is None:
            return False
        
        cur_x = self._cursor_pos.x()
        cur_y = self._cursor_pos.y()

        if cur_x in range(x, x + w) and cur_y in range(y, y + h):
            return False
        
        if x < 0 or y < 0 or x + w * self.getv("def_extra_image_min_visible_width") / 100 > self._parent_widget.contentsRect().width() or y + h * self.getv("def_extra_image_min_visible_height") / 100 > self._parent_widget.contentsRect().height():
            return False
        
        if not dont_draw_image:
            self.move(x, y)
            self.resize(w, h)
            
        return True

    def _define_label(self):
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.setVisible(False)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def close_me(self):
        if self._timer_fade_out:
            self._timer_fade_out.stop()
            self._timer_fade_out.deleteLater()
        if self._timer_delay:
            self._timer_delay.stop()
            self._timer_delay.deleteLater()
        if self._timer_start_fade_out:
            self._timer_start_fade_out.stop()
            self._timer_start_fade_out.deleteLater()
        self._timer_fade_out = None
        self._timer_delay = None
        self._timer_start_fade_out = None
        self.hide()
        self.deleteLater()
        self.setParent(None)


class ShowSimpleDefinitions():
    def __init__(self, settings: settings_cls.Settings, parent_widget, definition_ids: list = None, cursor_pos: QPoint = None, *args, **kwargs):

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self.signal: utility_cls.Signals = self.get_appv("signal")
        self._parent_widget = parent_widget
        self._definition_ids = self._remove_duplicate_defs(definition_ids)
        self._extra_image = []
        if self._definition_ids is None:
            self._definition_ids = []
        self._cursor_pos = cursor_pos
        if self._cursor_pos:
            self._cursor_loc_pos = self._parent_widget.mapFromGlobal(self._cursor_pos)
        else:
            self._cursor_loc_pos = None
        self._definitions = []

        # Connect signals with slots
        self.signal.signalSimpleDefinitionGeometryChanged.connect(self.signal_definition_geometry_changed)

        UTILS.LogHandler.add_log_record("#1: Engine started.", ["ShowSimpleDefinitions"])

    def show_me(self, definition_ids: list = None, cursor_pos: QPoint = None):
        definition_ids = self._remove_duplicate_defs(definition_ids)
        UTILS.LogHandler.add_log_record("#1: Show frame requested for ID(s) #2.", ["ShowSimpleDefinitions", str(definition_ids)])
        if cursor_pos is not None:
            self._cursor_pos = cursor_pos
            self._cursor_loc_pos = self._parent_widget.mapFromGlobal(self._cursor_pos)
        
        while len(self._definitions) > 0:
            self.hide_me(self._definitions[0][0])
        
        if definition_ids is not None:
            self._definition_ids = list(definition_ids)

        self._definitions = []

        pos_x = self._cursor_loc_pos.x()
        pos_y = self._cursor_loc_pos.y()

        for i in self._definition_ids:
            cur_pos = QPoint(pos_x, pos_y)
            def_obj = ShowSimpleDefinition(self._stt, self._parent_widget, i, self._parent_widget.mapToGlobal(cur_pos))
            def_obj.show_me(i, self._parent_widget.mapToGlobal(cur_pos))
            self._definitions.append([i, def_obj])
            
            pos_y += def_obj.height() + 10
            pos_x += int(def_obj.width() / 4)
            if pos_y >= self._parent_widget.contentsRect().height():
                pos_y = 0
            if pos_x >= self._parent_widget.contentsRect().width():
                pos_x -= def_obj.width()
                if pos_x < 0:
                    pos_x = 0
        self._display_extra_images()

    def _remove_duplicate_defs(self, definition_ids: list) -> list:
        if definition_ids is None:
            return None
        defs = []
        for i in definition_ids:
            if i not in defs:
                defs.append(i)
        return defs

    def _display_extra_images(self):
        if not self.getv("show_definition_extra_image"):
            return
        
        max_images = self.getv("def_extra_image_max_number_of_images")
        if max_images < len(self._extra_image):
            while len(self._extra_image) > max_images:
                self._extra_image[0].close()
                self._extra_image[0].deleteLater()
                self._extra_image.pop(0)

        for _ in range(len(self._extra_image), self.getv("def_extra_image_max_number_of_images")):
            self._extra_image.append(SimpleDefinitionExtraImage(self._stt, self._parent_widget))

        if not self._definitions:
            return

        cur_pos = self._parent_widget.mapFromGlobal(QCursor.pos())
        frm_pos = self._definitions[-1][1].mapToGlobal(QPoint(0,0))
        frm_pos = self._parent_widget.mapFromGlobal(frm_pos)
        frm_rect = self._definitions[-1][1].rect()
        def_id = self._definitions[-1][1]._definition_id

        if self.getv("def_extra_image_total_display_period"):
            delay_range = self.getv("def_extra_image_total_display_period")
        else:
            delay_range = self.getv("def_extra_image_auto_hide")
            if delay_range > 10000:
                delay_range = 10000

        for i in range(len(self._extra_image)):
            if i == 0:
                delay = self.getv("def_extra_image_start_delay")
            else:
                delay = random.randint(0, delay_range) + self.getv("def_extra_image_start_delay")
            self._extra_image[i].show_me(cur_pos, frm_pos, frm_rect, delay=delay, definition_id=def_id, caller="SimpleDef")

    def signal_definition_geometry_changed(self, simple_def: QFrame):
        frm_pos = simple_def.mapToGlobal(QPoint(0,0))
        frm_pos = self._parent_widget.mapFromGlobal(frm_pos)
        frm_rect = simple_def.rect()
        def_id = simple_def._definition_id
        for i in self._extra_image:
            i.change_definition_geometry(frm_pos, frm_rect, def_id)

    def get_width(self, definition_id: int):
        for i in self._definitions:
            if i[0] == definition_id:
                return i[1].width()
        return 0

    def get_height(self, definition_id: int):
        for i in self._definitions:
            if i[0] == definition_id:
                return i[1].height()
        return 0

    def get_mapToGlobal(self, definition_id: int):
        for i in self._definitions:
            if i[0] == definition_id:
                return i[1].mapToGlobal(QPoint(0,0))
        return QPoint(0,0)

    def hide_me(self, definition_id: int = None):
        if self._extra_image:
            for item in self._extra_image:
                item.hide_me(definition_id=definition_id)

        if definition_id:
            self._hide_def(definition_id)
            return
        
        while len(self._definitions) > 0:
            self._hide_def(self._definitions[0][0])
        
    def _hide_def(self, definition_id: int):
        try:
            for idx, item in enumerate(self._definitions):
                if item[0] == definition_id:
                    item[1].hide_me()
                    item[1].close_me()
                    self._definitions.pop(idx)
                    break
            for idx, item in enumerate(self._definition_ids):
                if item == definition_id:
                    self._definition_ids.pop(idx)
                    break
        except Exception as e:
            UTILS.LogHandler.add_log_record("#1: Error occurred while trying to hide definition #2 in method #3.\nException: #4", ["ShowSimpleDefinitions", str(definition_id), "_hide_def", str(e)], warning_raised=True)

    def close_me(self):
        if self._definitions:
            for item in self._definitions:
                item[1].close_me()
        
        if self._extra_image:
            for item in self._extra_image:
                item.close_me()
        UTILS.LogHandler.add_log_record("#1: Engine stopped.", ["ShowSimpleDefinitions"])
        
    @property
    def drag_mode(self) -> bool:
        for i in self._definitions:
            if i[1].drag_mode:
                return True
        return False


class ShowSimpleDefinition(QFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, definition_id: int = None, cursor_pos: QPoint = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.drag_mode = None

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self._parent_widget = parent_widget
        self._definition_id = definition_id
        self._cursor_pos =  cursor_pos
        self.move_mode = None
        self._clip: utility_cls.Clipboard = self.get_appv("cb")
        self.signal: utility_cls.Signals = self.get_appv("signal")
        
        self.setVisible(False)

        self._setup_widgets()
        self._setup_apperance()
        self._setup_position_size_and_populate_widgets()

        # Connect events with slots
        self.btn_resize.mousePressEvent = self._btn_resize_mouse_press
        self.btn_resize.mouseReleaseEvent = self._btn_resize_mouse_release
        self.btn_resize.mouseMoveEvent = self._btn_resize_mouse_move
        self.btn_close.clicked.connect(self._btn_close_click)
        self.lbl_desc.mousePressEvent = self._lbl_desc_mouse_press
        self.lbl_desc.mouseDoubleClickEvent = self._lbl_desc_double_click
        self.lbl_pic.mousePressEvent = self._lbl_pic_mouse_press
        self.lbl_pic.mouseDoubleClickEvent = self._lbl_pic_double_click
        self.mousePressEvent = self._self_mouse_press

        self.lbl_title.mousePressEvent = self.lbl_title_mouse_press
        self.lbl_title.mouseReleaseEvent = self.lbl_title_mouse_release
        self.lbl_title.mouseMoveEvent = self.lbl_title_mouse_move

        UTILS.LogHandler.add_log_record("#1: Frame loaded. (DefID=#2)", ["ShowSimpleDefinition", self._definition_id])

    def lbl_title_mouse_press(self, x):
        self.move_mode = (QCursor().pos().x() - self.pos().x(), QCursor().pos().y() - self.pos().y())

    def lbl_title_mouse_release(self, x):
        self.move_mode = None
        self.signal.simple_viev_geometry_changed(self)

    def lbl_title_mouse_move(self, e):
        if self.move_mode:
            x = QCursor().pos().x() - self.move_mode[0]
            y = QCursor().pos().y() - self.move_mode[1]
            self.move(x, y)

    def _btn_close_click(self):
        self._clear_cm()
        self.hide_me()

    def _lbl_desc_mouse_press(self, e: QtGui.QMouseEvent):
        self._clear_cm()
        if e.button() == Qt.RightButton:
            self._context_menu()

    def _lbl_desc_double_click(self, e: QtGui.QMouseEvent) -> None:
        definition_cls.BrowseDefinitions(self._stt, self, definition_id=self._definition_id)

    def _lbl_pic_mouse_press(self, e: QtGui.QMouseEvent):
        self._clear_cm()
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
            self._context_menu()

    def _lbl_pic_double_click(self, e: QtGui.QMouseEvent) -> None:
        definition_cls.BrowseDefinitions(self._stt, self, definition_id=self._definition_id)

    def _self_mouse_press(self, e):
        self._clear_cm()

    def show_me(self, definition_id: int = None, cursor_pos: QPoint = None):
        if definition_id is not None:
            self._definition_id = definition_id
        if cursor_pos is not None:
            self._cursor_pos = cursor_pos
        
        self._setup_position_size_and_populate_widgets()
        self.setVisible(True)
    
    def hide_me(self):
        self.setVisible(False)

    def _context_menu(self):
        db_def = db_definition_cls.Definition(self._stt, self._definition_id)

        disab = []
        
        media_id = None
        if db_def.definition_media_ids:
            if db_def.default_media_id:
                media_id = db_def.default_media_id
            else:
                media_id = db_def.definition_media_ids[0]
        else:
            disab.append(50)
            disab.append(60)

        if self._clip.is_clip_empty():
            disab.append(70)

        menu_dict = {
            "position": QCursor().pos(),
            "disabled": disab,
            "separator":[40, 60],
            "items": [
                [
                    10,
                    self.getl("definition_view_simple_cm_view_text"),
                    self.getl("definition_view_simple_cm_view_tt"),
                    True,
                    [],
                    self.getv("mnu_view_definitions_icon_path")
                ],
                [
                    20,
                    self.getl("definition_view_simple_cm_edit_text"),
                    self.getl("definition_view_simple_cm_edit_tt"),
                    True,
                    [],
                    self.getv("mnu_edit_definitions_icon_path")
                ],
                [
                    30,
                    self.getl("definition_view_simple_cm_browse_text"),
                    self.getl("definition_view_simple_cm_browse_tt"),
                    True,
                    [],
                    self.getv("mnu_browse_definitions_icon_path")
                ],
                [
                    40,
                    self.getl("definition_view_simple_cm_show_all_images_text").replace("#1", str(len(db_def.definition_media_ids))),
                    self.getl("definition_view_simple_cm_show_all_images_tt"),
                    True,
                    [],
                    self.getv("picture_browse_win_icon_path")
                ],
                [
                    50,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    60,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    70,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        
        main_dict = {
            "name": "TextHandler",
            "action": "cm"
        }
        self._parent_widget.events(main_dict)

        utility_cls.ContextMenu(self._stt, self._parent_widget)
        # self._clear_cm()
        if menu_dict["result"] == 10:
            definition_cls.ViewDefinition(self._stt, self.get_appv("main_win"), self._definition_id)
        elif menu_dict["result"] == 20:
            definition_cls.AddDefinition(self._stt, self.get_appv("main_win"), definition_id=self._definition_id)
        elif menu_dict["result"] == 30:
            definition_cls.BrowseDefinitions(self._stt, self.get_appv("main_win"), definition_id=self._definition_id)
        elif menu_dict["result"] == 40:
            utility_cls.PictureBrowse(self._stt, self.get_appv("main_win"), db_def.definition_media_ids)
        elif self.get_appv("menu")["result"] == 50:
            self._clip.copy_to_clip(media_id, add_to_clip=False)
        elif self.get_appv("menu")["result"] == 60:
            self._clip.copy_to_clip(media_id, add_to_clip=True)
        elif self.get_appv("menu")["result"] == 70:
            self._clip.clear_clip()

    def _clear_cm(self) -> None:
        self.get_appv("cm").remove_all_context_menu()

    def _setup_position_size_and_populate_widgets(self):
        if self._definition_id is None:
            return
        
        # Define size
        w = self.getv("definition_view_simple_width")
        h = self.getv("definition_view_simple_height")

        if w == 0:
            w = 300
        if h == 0:
            h = 200

        db_def = db_definition_cls.Definition(self._stt, self._definition_id)

        fm = QFontMetrics(self.lbl_title.font())        

        if fm.width(db_def.definition_name) + 20 > w:
            if fm.width(db_def.definition_name) + 20 < self._parent_widget.contentsRect().width():
                w = fm.width(db_def.definition_name) + 20

        if not self.drag_mode:
            self.resize(w, h)

        title_h = fm.height() + 18
        self.lbl_title.move(2, 2)
        self.lbl_title.resize(self.width() - 4, title_h)

        widget_h = self.height() - self.lbl_title.height() - 10
        if widget_h < 0:
            widget_h = 0
        widget_w = int((self.width() - 20) / 2)
        if widget_w < 0:
            widget_w = 0

        if db_def.definition_media_ids:
            self.lbl_pic.setVisible(True)
            img = QPixmap()
            if db_def.default_media_id:
                media_id = db_def.default_media_id
            else:
                media_id = db_def.definition_media_ids[0]

            self.lbl_pic.move(5, self.lbl_title.height())
            self.lbl_pic.resize(widget_w, widget_h)

            db_media = db_media_cls.Media(self._stt, media_id=media_id)
            img.load(db_media.media_file)
            img = img.scaled(self.lbl_pic.width(), self.lbl_pic.height(), Qt.KeepAspectRatio)
            self.lbl_pic.setPixmap(img)

            self.lbl_desc.move(widget_w + 15, self.lbl_title.height())
            self.lbl_desc.resize(widget_w, widget_h)
        else:
            self.lbl_pic.setVisible(False)
            self.lbl_desc.move(10, self.lbl_title.height())
            self.lbl_desc.resize(widget_w * 2, widget_h)

        self.lbl_title.setText(db_def.definition_name)
        self.lbl_desc.setText(db_def.definition_description)

        # Set Frame position
        if self._cursor_pos is None:
            return
        
        loc_pos = self._parent_widget.mapFromGlobal(self._cursor_pos)

        x = loc_pos.x() + 10
        if x + self.width() > self._parent_widget.contentsRect().width():
            x = self._parent_widget.contentsRect().width() - self.width()
            if x < 0:
                x = 0

        y = loc_pos.y() + 30
        if y + self.height() > self._parent_widget.contentsRect().height():
            y = loc_pos.y() - 30 - self.height()
            if y < 0:
                y = 0
        
        self.move(x, y)
        self.btn_resize.resize(20, 20)
        self.btn_resize.move(self.width() - 22, self.height() - 22)

        self.btn_close.move(self.width() - 24, 2)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._setup_position_size_and_populate_widgets()
        return super().resizeEvent(a0)

    def _setup_widgets(self):
        self.lbl_title: QLabel = QLabel(self)
        self.lbl_pic: QLabel = QLabel(self)
        self.lbl_desc: QLabel = QLabel(self)
        self.btn_resize: QPushButton = QPushButton(self)
        self.btn_close: QPushButton = QPushButton(self)

    def _setup_apperance(self):
        self._frame_apperance("definition_view_simple_frame")
        font = QFont("MS Shell Dlg 2", 14)
        self.lbl_title.setFont(font)
        self.lbl_title.setStyleSheet(self.getv("definition_view_simple_title_stylesheet"))
        self.lbl_title.setAlignment(Qt.AlignHCenter)
        font = QFont("MS Shell Dlg 2", 12)
        self.lbl_desc.setFont(font)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet(self.getv("definition_view_simple_desc_stylesheet"))
        self.lbl_pic.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        img = QPixmap()
        img.load(self.getv("definition_view_simple_btn_resize_icon_path"))
        img = img.scaled(15, 15, Qt.KeepAspectRatio)
        self.btn_resize.setIcon(QIcon(img))
        self.btn_resize.setStyleSheet(self.getv("definition_view_simple_btn_resize_stylesheet"))
        self.btn_resize.setFlat(True)
        self.btn_resize.setToolTip(self.getl("definition_view_simple_btn_resize_tt"))

        img = QPixmap()
        img.load(self.getv("definition_view_simple_btn_close_icon_path"))
        img = img.scaled(22, 22, Qt.KeepAspectRatio)
        self.btn_close.resize(22, 22)
        self.btn_close.setIcon(QIcon(img))
        self.btn_close.setStyleSheet(self.getv("definition_view_simple_btn_close_stylesheet"))
        self.btn_close.setFlat(True)
        self.btn_close.setToolTip(self.getl("definition_view_simple_btn_close_tt"))

    def _frame_apperance(self, name: str):
        self.setFrameShape(self.getv(f"{name}_frame_shape"))
        self.setFrameShadow(self.getv(f"{name}_frame_shadow"))
        self.setLineWidth(self.getv(f"{name}_line_width"))
        self.setStyleSheet(self.getv(f"{name}_stylesheet"))

    def _btn_resize_mouse_move(self, event):
        if self.drag_mode:
            my_pos = self._parent_widget.mapToGlobal(self.pos())
            self.drag_mode = [
                my_pos.x(),
                my_pos.y(),
                QCursor.pos().x(),
                QCursor.pos().y() ]
            w = self.drag_mode[2] - self.drag_mode[0]
            h = self.drag_mode[3] - self.drag_mode[1]
            if w < 200:
                w = 200
            if h < 100:
                h = 100
            if w > self._parent_widget.contentsRect().width():
                w = self._parent_widget.contentsRect().width()
            if h > self._parent_widget.contentsRect().height():
                h = self._parent_widget.contentsRect().height()
            self.resize(w, h)

    def _btn_resize_mouse_press(self, event):
        self._clear_cm()
        my_pos = self._parent_widget.mapToGlobal(self.pos())
        self.drag_mode = [
            my_pos.x(),
            my_pos.y(),
            QCursor.pos().x(),
            QCursor.pos().y() ]
        
    def _btn_resize_mouse_release(self, event):
        self.drag_mode = None
        self.signal.simple_viev_geometry_changed(self)

    def close_me(self):
        if self.btn_resize:
            self.btn_resize.deleteLater()
        if self.btn_close:
            self.btn_close.deleteLater()
        if self.lbl_desc:
            self.lbl_desc.deleteLater()
        if self.lbl_pic:
            self.lbl_pic.deleteLater()
        if self.lbl_title:
            self.lbl_title.deleteLater()
        UTILS.LogHandler.add_log_record("#1: Frame closed. (DefID=#2)", ["ShowSimpleDefinition", self._definition_id])
        try:
            self.deleteLater()
            self.setParent(None)
        except Exception as e:
            UTILS.LogHandler.add_log_record(f"#1: Failed to delete frame in #2 method.\nException: #3", ["ShowSimpleDefinition", "close_me", str(e)], warning_raised=True)
        

class TextHandlerData:
    def __init__(self, settings: settings_cls.Settings) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self._def_list = self.calculate_data()

    def calculate_data(self) -> list:
        db_def = db_definition_cls.Definition(self._stt)

        return db_def.get_list_of_all_expressions(order_by="LENGTH(expression)", return_text_handler_list=True)

    def update_data(self) -> None:
        self._def_list = self.calculate_data()


    def get_data(self) -> list:
        return self._def_list


class TextHandler():
    PARENTHESIS_KEY_MAP = [
        ["(", ")"],
        ["[", "]"],
        ["{", "}"],
        ["<", ">"],
        ["|", "|"],
        ["'", "'"],
        ["\"", "\""],
        ["`", "`"],
        ["*", "*"],
        ["_", "_"],
        ["/", "/"],
        ["\\", "\\"],
        ["~", "~"],
        ["-", "-"]
    ]

    def __init__(self, settings: settings_cls.Settings, txt_box: QTextEdit, main_win, widget_handler: qwidgets_util_cls.WidgetHandler = None, exec_when_check_def = (None, None)) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self._exec_when_check_def = exec_when_check_def
        self._main_win = main_win
        self._widget_handler = widget_handler
        self._signals: utility_cls.Signals = self.get_appv("signal")
        self.txt_box = txt_box
        self.char_for = self.txt_box.textCursor().charFormat()
        self._real_char_format = self.txt_box.textCursor().charFormat()
        self.dicts = None

        self.has_highlighted_word = False
        self._undo_available = False
        self._redo_available = False

        self._list_mode = False
        self._calculator_mode(False)
        self._calc_mode = False

        self._def_list = []
        self._text_def_map = []
        self._hyperlink_list = []
        self._simple_def_view = ShowSimpleDefinitions(self._stt, self._main_win)
        self._timer = QTimer()
        self._timer_to_hide = QTimer()
        self._definition_to_show_in_simple_view = []

        self._txt_box_normal_tooltip = self.txt_box.toolTip()

        self._definition_hint = DefinitonHint(self._stt, self._main_win, widget_handler=self._widget_handler)

        self._populate_def_list()

        self.data_dict = {}
        self._populate_data_dict()

        # Conect events with slots
        self.get_appv("signal").signalNewDefinitionAdded.connect(self.signalNewDefinitionAdded)

        UTILS.LogHandler.add_log_record("#1: Engine started.", ["TextHandler"])

    def signalNewDefinitionAdded(self):
        if self._exec_when_check_def[0] == "AddDefinition txt_syn":
            self._exec_when_check_def[1]._checking_in_progress = True
        elif self._exec_when_check_def[0] == "AddDefinition txt_desc":
            self._exec_when_check_def[1]._txt_desc_mark_mode = True
        
        self._populate_def_list()
        self.check_definitions()

        if self._exec_when_check_def[0] == "AddDefinition txt_syn":
            self._exec_when_check_def[1]._checking_in_progress = False
            self._exec_when_check_def[1]._txt_syn_text_changed()
        elif self._exec_when_check_def[0] == "AddDefinition txt_desc":
            self._exec_when_check_def[1]._txt_desc_mark_mode = False
            self._exec_when_check_def[1]._txt_desc_text_changed()
        
        if self._exec_when_check_def[0] and self._exec_when_check_def[0].startswith("AddDefinition"):
            db_def = db_definition_cls.Definition(self._stt)
            self._exec_when_check_def[1].exp_list = db_def.get_list_of_all_expressions()
            self._exec_when_check_def[1]._change_widgets_if_illegal_entry()


    def _populate_data_dict(self):
        if "marked" not in self.data_dict:
            self.data_dict["marked"] = []
        if "highlighted" not in self.data_dict:
            self.data_dict["highlighted"] = []
        
    def mouse_move(self, e: QtGui.QMouseEvent) -> None:
        if self.getv("show_word_highlight"):
            cursor = self.txt_box.cursorForPosition(e.pos())
            
            if self._find_word(self.txt_box.toPlainText(), cursor.position()):
                self.highlight_toggle(True)
        
    def _find_word(self, txt: str, pos: int) -> bool:
        if self._calc_mode:
            return

        if pos == 0 or pos == len(txt):
            return False

        if UTILS.TextUtility.is_special_char(txt[pos - 1:pos]) or UTILS.TextUtility.is_special_char(txt[pos + 1:pos + 2]) or UTILS.TextUtility.is_special_char(txt[pos:pos + 1]):
            return False

        txt = UTILS.TextUtility.replace_special_chars(txt)

        start_pos = txt.rfind(" ", 0, pos) + 1
        end_pos = txt.find(" ", pos)
        word = txt[start_pos:end_pos]
        if self.data_dict["highlighted"]:
            if start_pos != self.data_dict["highlighted"][0] or end_pos != self.data_dict["highlighted"][1]:
                self.highlight_toggle(highlight=False)
                cursor = self.txt_box.textCursor()
                cursor.setPosition(pos)
                self.char_for = cursor.charFormat()
        else:
            cursor = self.txt_box.textCursor()
            cursor.setPosition(pos)
            self.char_for = cursor.charFormat()

        self.data_dict["highlighted"] = [start_pos, end_pos, word]
        return True

    def _can_undo(self, value) -> None:
        self._undo_available = value

    def _can_redo(self, value) -> None:
        self._redo_available = value

    def highlight_toggle(self, highlight: bool):
        if self._calc_mode:
            return

        if not self.data_dict["highlighted"]:
            self.has_highlighted_word = False
            return
        cursor = self.txt_box.textCursor()
        start_pos = self.data_dict["highlighted"][0]
        end_pos = self.data_dict["highlighted"][1]

        cursor.setPosition(self.data_dict["highlighted"][0])
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, end_pos - start_pos)
        if highlight:
            cf = QTextCharFormat(self.char_for)
            cf.setFontItalic(self.getv("block_body_highlighted_font_italic"))
            color = QColor()
            if self.getv("block_body_highlighted_color"):
                color.setNamedColor(self.getv("block_body_highlighted_color"))
                cf.setForeground(color)
            if self.getv("block_body_highlighted_background"):
                color.setNamedColor(self.getv("block_body_highlighted_background"))
                cf.setBackground(color)
            cursor.setCharFormat(cf)
            self.txt_box.setTextCursor(cursor)
            cursor.clearSelection()
            self.txt_box.setTextCursor(cursor)
            self.has_highlighted_word = True
        else:
            cursor.setCharFormat(self.char_for)
            self.txt_box.setTextCursor(cursor)
            cursor.clearSelection()
            # cursor.setPosition(len(self.txt_box.toPlainText()))
            self.txt_box.setTextCursor(cursor)
            self.has_highlighted_word = False
            self.data_dict["highlighted"] = []

    def show_context_menu(self):
        if self._calc_mode:
            return

        UTILS.LogHandler.add_log_record("#1: Main Context menu displayed.", ["TextHandler"])

        # Set status for AutoComplete and Highlighter
        disab = []
        if self.getv("show_word_highlight"):
            hl_stat = 80010
            hl_txt = f' ({self.getl("text_on")})'
            disab.append(80010)
        else:
            hl_stat = 80020
            hl_txt = f' ({self.getl("text_off")})'
            disab.append(80020)
        if self.getv("show_autocomplete"):
            ac_stat = 70010
            ac_txt = f' ({self.getl("text_on")})'
            disab.append(70010)
        else:
            ac_stat = 70020
            ac_txt = f' ({self.getl("text_off")})'
            disab.append(70020)
        
        # Define is there highlighted word or selection
        hl_word = ""
        sel_text = ""
        cursor = self.txt_box.textCursor()
        if cursor.hasSelection():
            txt = self.txt_box.toPlainText()
            txt = UTILS.TextUtility.replace_special_chars(txt)
            cur_sel = self.txt_box.textCursor()
            start_sel = txt[:cur_sel.selectionStart()].rfind(" ")
            end_sel = txt[cur_sel.selectionEnd():].find(" ") + cursor.selectionEnd()
            if end_sel == -1:
                end_sel = len(txt)
            sel_text = txt[start_sel + 1:end_sel]

            if len(sel_text) > 25:
                sel_text = sel_text[0:17] + "..." + sel_text[-8:]
        else:
            if self.has_highlighted_word:
                self.highlight_toggle(False)
            pos_global = QCursor().pos()
            pos_local = self.txt_box.mapFromGlobal(pos_global)
            cursor = self.txt_box.cursorForPosition(pos_local)
            pos = cursor.position()
            if self._find_word(self.txt_box.toPlainText(), pos):
                self.highlight_toggle(True)
                if self.has_highlighted_word:
                    hl_word = self.data_dict["highlighted"][2]
                    if len(hl_word) > 25:
                        hl_word = hl_word[:17] + "..." + hl_word[-8:]
        if sel_text:
            define_selection_text = f'{self.getl("block_txt_box_menu_def_sel_text")} ({sel_text})'
        else:
            define_selection_text = self.getl("block_txt_box_menu_def_sel_text")
        if hl_word:
            define_higlighted_word = f'{self.getl("block_txt_box_menu_def_high_text")} ({hl_word})'
        else:            
            define_higlighted_word = self.getl("block_txt_box_menu_def_high_text")

        if self.getv("definition_text_mark_enabled"):
            def_mark = 110010
            def_mark_text = f' ({self.getl("block_txt_box_menu_def_mark_on_text")})'
        else:
            def_mark = 110020
            def_mark_text = f' ({self.getl("block_txt_box_menu_def_mark_off_text")})'
        definition_word = None
        definition_id = None
        for i in self._text_def_map:
            if self.txt_box.textCursor().position() in range(i[2], i[3]):
                definition_word = i[1]
                definition_id = i[0]
                break
        if definition_word is None:
            disab.append(130)

        if len(sel_text) < 3 and len(hl_word) < 3:
            disab.append(105)

        if self.getv("definition_show_on_mouse_hover"):
            def_show_simple = 120010
            def_show_simple_text = f' ({self.getl("block_txt_box_menu_def_view_simple_on_text")})'
        else:
            def_show_simple = 120020
            def_show_simple_text = f' ({self.getl("block_txt_box_menu_def_view_simple_off_text")})'
        
        if self.getv("http_hyperlink_text_detection_enabled"):
            if self.getv("hyperlink_mark_enabled"):
                hyperlink_text = f' ({self.getl("block_txt_box_menu_hyperlink_on_and_mark_text_add")})'
                hyperlink_selected = 83010
            else:
                hyperlink_text = f' ({self.getl("block_txt_box_menu_hyperlink_on_and_not_mark_text_add")})'
                hyperlink_selected = 83020
        else:
            hyperlink_text = f' ({self.getl("block_txt_box_menu_hyperlink_off_text_add")})'
            hyperlink_selected = 83030

        if self.getv("numbers_in_block_text_mark_enabled"):
            numbers_text = f' ({self.getl("text_on")})'
            numbers_selection = 86010
        else:
            numbers_text = f' ({self.getl("text_off")})'
            numbers_selection = 86020

        if not self.txt_box._data_dict["media"]:
            disab.append(139)

        selected_items = [hl_stat, ac_stat, def_mark, def_show_simple, hyperlink_selected, numbers_selection]
        separator_items = [20, 60, 86, 105, 133, 145, 150, 160]
        
        # Extra definition images setup
        if self.getv("show_definition_extra_image"):
            extra_state_text = f'  ( {self.getl("text_on")} )'
            selected_items.append(1250010)
        else:
            extra_state_text = f'  ( {self.getl("text_off")} )'
            selected_items.append(1250020)

        i = self.getv("def_extra_image_max_number_of_images")
        separator_items.append(1250101100)
        extra_num_text = f'  ( {str(i)} )'
        if i > 0 and i < 10:
            selected_items.append(1250101000 + i * 10)
        else:
            selected_items.append(1250101900)

        separator_items.append(1250201000)
        separator_items.append(1250201100)
        if self.getv("def_extra_image_start_delay") in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]:
            selected_items.append(1250201000 + self.getv("def_extra_image_start_delay") / 1000 * 10)
            extra_delay_text = f'  ( {str(self.getv("def_extra_image_start_delay") / 1000)} sec )'
        elif self.getv("def_extra_image_start_delay") == 0:
            selected_items.append(1250201000)
            extra_delay_text = f'  ( {self.getl("block_txt_box_menu_def_simple_delay_none_text")} )'
        else:
            selected_items.append(1250201900)
            extra_delay_text = f'  ( {self.getl("custom")}: {str(self.getv("def_extra_image_start_delay") / 1000)} sec )'

        separator_items.append(1250301000)
        separator_items.append(1250301100)
        if self.getv("def_extra_image_auto_hide") in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]:
            selected_items.append(1250301000 + self.getv("def_extra_image_auto_hide") / 1000 * 10)
            extra_duration_text = f'  ( {str(self.getv("def_extra_image_auto_hide") / 1000)} sec )'
        elif self.getv("def_extra_image_auto_hide") == 0:
            selected_items.append(1250301000)
            extra_duration_text = f'  ( {self.getl("block_txt_box_menu_def_simple_duration_forever_text")} )'
        else:
            selected_items.append(1250301900)
            extra_duration_text = f'  ( {self.getl("custom")}: {str(self.getv("def_extra_image_auto_hide") / 1000)} sec )'

        separator_items.append(1250401000)
        separator_items.append(1250401050)
        if self.getv("def_extra_image_auto_hide_fade_out_duration") in [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]:
            selected_items.append(1250401000 + int(self.getv("def_extra_image_auto_hide_fade_out_duration") / 1000 * 10))
            extra_fade_duration_text = f'  ( {str(self.getv("def_extra_image_auto_hide_fade_out_duration") / 1000)} sec )'
        elif self.getv("def_extra_image_auto_hide_fade_out_duration") == 0:
            selected_items.append(1250401000)
            extra_fade_duration_text = f'  ( {self.getl("block_txt_box_menu_def_simple_fade_none_text")} )'
        else:
            selected_items.append(1250401900)
            extra_fade_duration_text = f'  ( {self.getl("custom")}: {str(self.getv("def_extra_image_auto_hide_fade_out_duration") / 1000)} sec )'

        if self.getv("def_extra_image_show_next_after_hide"):
            selected_items.append(1250510)
            extra_next_text = f'  ( {self.getl("text_on")} )'
        else:
            selected_items.append(1250520)
            extra_next_text = f'  ( {self.getl("text_off")} )'

        extra_src = " ??? "
        match self.getv("def_extra_image_source"):
            case 1:
                selected_items.append(1250610)
                extra_src = f' ({self.getl("block_txt_box_menu_def_simple_img_source_toon_text")})'
            case 2:
                selected_items.append(1250620)
                extra_src = f' ({self.getl("block_txt_box_menu_def_simple_img_source_def_text")})'
            case 3:
                selected_items.append(1250630)
                extra_src = f' ({self.getl("block_txt_box_menu_def_simple_img_source_blocks_text")})'
            case 4:
                selected_items.append(1250640)
                extra_src = f' ({self.getl("block_txt_box_menu_def_simple_img_source_app_text")})'
            case 5:
                selected_items.append(1250650)
                extra_src = f' ({self.getl("block_txt_box_menu_def_simple_img_source_cus_text")})'

        if self.getv("def_extra_image_layout") == 1:
            selected_items.append(1250710)
            extra_layout_text = f'  ( {self.getl("text_random")} )'
        elif self.getv("def_extra_image_layout") == 2:
            selected_items.append(1250720)
            extra_layout_text = f'  ( {self.getl("text_around_def")} )'

        def_enum_count_word = f"  ( {len(set([x[0] for x in self._text_def_map]))} )"
        # definitions_list = self._get_def_list_for_context_menu(number_of_items_per_menu=20)
        definitions_list = []

        separator_items.append(12508070)
        extra_apperance_text = "( ??? )"
        extra_apperance_duration_text = f'  ( {self.getv("def_extra_image_animate_show") / 1000} sec. )'
        match self.getv("def_extra_image_animate_style"):
            case 0:
                selected_items.append(12508010)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_style_random_text")})'
            case 1:
                selected_items.append(12508020)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_style_instant_text")})'
            case 2:
                selected_items.append(12508030)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_style_grove_text")})'
            case 3:
                selected_items.append(12508040)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_style_left_up_text")})'
            case 4:
                selected_items.append(12508050)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_style_right_up_text")})'
            case 5:
                selected_items.append(12508060)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_style_bot_left_text")})'
            case 6:
                selected_items.append(12508070)
                extra_apperance_text = f'  ({self.getl("block_txt_box_menu_def_simple_img_apperance_stylebot_right_text")})'

        if self.getv("definition_hint_enabled"):
            hint_word = f'  ({self.getl("text_on")})'
            selected_items.append(8710)
        else:
            hint_word = f'  ({self.getl("text_off")})'
            selected_items.append(8720)

        # Dictionaries Notification
        separator_items.append(135)
        if sel_text:
            dict_search_term = f"({sel_text})"
        elif hl_word:
            dict_search_term = f"({hl_word})"
        else:
            dict_search_term = ""

        if self.getv("dictionaries_search_notification"):
            selected_items.append(134010)
        else:
            selected_items.append(134020)

        menu_dict = {
            "position": QCursor().pos(),
            "selected": selected_items,
            "separator": separator_items,
            "disabled": disab,
            "use_icon_for_selected": True,
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
                    self.getl("block_txt_box_menu_copy_text"),
                    self.getl("block_txt_box_menu_copy_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_copy_icon_path")
                ],
                [
                    50,
                    self.getl("block_txt_box_menu_paste_text"),
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
                ],
                [
                    70,
                    self.getl("block_txt_box_menu_autocomplete_text") + ac_txt,
                    self.getl("block_txt_box_menu_autocomplete_tt"),
                    False,
                    [
                        [
                            70010,
                            self.getl("block_txt_box_menu_autocomplete_on_text"),
                            self.getl("block_txt_box_menu_autocomplete_on_tt"),
                            True,
                            []
                        ],
                        [
                            70020,
                            self.getl("block_txt_box_menu_autocomplete_off_text"),
                            self.getl("block_txt_box_menu_autocomplete_off_tt"),
                            True,
                            []
                        ]
                    ],
                    self.getv("block_txt_box_menu_autocomplete_icon_path")
                ],
                [
                    80,
                    self.getl("block_txt_box_menu_highlight_text") + hl_txt,
                    self.getl("block_txt_box_menu_highlight_tt"),
                    False,
                    [
                        [
                            80010,
                            self.getl("block_txt_box_menu_highlight_on_text"),
                            self.getl("block_txt_box_menu_highlight_on_tt"),
                            True,
                            []
                        ],
                        [
                            80020,
                            self.getl("block_txt_box_menu_highlight_off_text"),
                            self.getl("block_txt_box_menu_highlight_off_tt"),
                            True,
                            []
                        ]
                    ],
                    self.getv("block_txt_box_menu_highlight_icon_path")
                ],
                [
                    83,
                    self.getl("block_txt_box_menu_hyperlink_text") + hyperlink_text,
                    self.getl("block_txt_box_menu_hyperlink_tt"),
                    False,
                    [
                        [
                            83010,
                            self.getl("block_txt_box_menu_hyperlink_on_and_mark_text"),
                            self.getl("block_txt_box_menu_hyperlink_on_and_mark_tt"),
                            True,
                            []
                        ],
                        [
                            83020,
                            self.getl("block_txt_box_menu_hyperlink_on_and_not_mark_text"),
                            self.getl("block_txt_box_menu_hyperlink_on_and_not_mark_tt"),
                            True,
                            []
                        ],
                        [
                            83030,
                            self.getl("block_txt_box_menu_hyperlink_off_text"),
                            self.getl("block_txt_box_menu_hyperlink_off_tt"),
                            True,
                            []
                        ]
                    ],
                    self.getv("block_txt_box_menu_hyperlink_icon_path")
                ],
                [
                    86,
                    self.getl("block_txt_box_menu_numbers_text") + numbers_text,
                    self.getl("block_txt_box_menu_numbers_tt"),
                    False,
                    [
                        [
                            86010,
                            self.getl("block_txt_box_menu_numbers_on_text"),
                            self.getl("block_txt_box_menu_numbers_on_tt"),
                            True,
                            []
                        ],
                        [
                            86020,
                            self.getl("block_txt_box_menu_numbers_off_text"),
                            self.getl("block_txt_box_menu_numbers_off_tt"),
                            True,
                            []
                        ]
                    ],
                    self.getv("block_txt_box_menu_numbers_icon_path")
                ],
                [
                    87,
                    self.getl("block_txt_box_menu_def_hint_text") + hint_word,
                    self.getl("block_txt_box_menu_def_hint_tt"),
                    False,
                    [
                        [
                            8710,
                            self.getl("text_on"),
                            "",
                            True,
                            []
                        ],
                        [
                            8720,
                            self.getl("text_off"),
                            "",
                            True,
                            []
                        ]
                    ],
                    self.getv("definition_hint_icon_path")
                ],
                [
                    90,
                    define_selection_text,
                    self.getl("block_txt_box_menu_def_sel_tt"),
                    True,
                    [],
                    self.getv("definition_add_win_icon_path")
                ],
                [
                    100,
                    define_higlighted_word,
                    self.getl("block_txt_box_menu_def_high_tt"),
                    True,
                    [],
                    self.getv("definition_add_win_icon_path")
                ],
                [
                    105,
                    self.getl("block_txt_box_menu_find_def_text"),
                    self.getl("block_txt_box_menu_find_def_tt"),
                    True,
                    [],
                    self.getv("find_def_on_internet_icon_path")
                ],
                [
                    110,
                    self.getl("block_txt_box_menu_def_mark_on_off_text") + def_mark_text,
                    self.getl("block_txt_box_menu_def_mark_on_off_tt"),
                    False,
                    [
                        [
                            110010,
                            self.getl("block_txt_box_menu_def_mark_on_text"),
                            self.getl("block_txt_box_menu_def_mark_on_tt"),
                            True,
                            [],
                            None
                        ],
                        [
                            110020,
                            self.getl("block_txt_box_menu_def_mark_off_text"),
                            self.getl("block_txt_box_menu_def_mark_off_tt"),
                            True,
                            [],
                            None
                        ]
                    ],
                    self.getv("mark_icon_path")
                ],
                [
                    120,
                    self.getl("block_txt_box_menu_def_view_simple_on_off_text") + def_show_simple_text,
                    self.getl("block_txt_box_menu_def_view_simple_on_off_tt"),
                    False,
                    [
                        [
                            120010,
                            self.getl("block_txt_box_menu_def_view_simple_on_text"),
                            self.getl("block_txt_box_menu_def_view_simple_on_tt"),
                            True,
                            [],
                            None
                        ],
                        [
                            120020,
                            self.getl("block_txt_box_menu_def_view_simple_off_text"),
                            self.getl("block_txt_box_menu_def_view_simple_off_tt"),
                            True,
                            [],
                            None
                        ]
                    ],
                    self.getv("pop_up_definition_icon_path")
                ],
                [
                    125,
                    self.getl("block_txt_box_menu_def_simple_extra_options_text"),
                    self.getl("block_txt_box_menu_def_simple_extra_options_tt"),
                    False,
                    [
                        [
                            125000,
                            self.getl("block_txt_box_menu_def_simple_img_state_text") + extra_state_text,
                            self.getl("block_txt_box_menu_def_simple_img_state_tt"),
                            False,
                            [
                                [1250010, self.getl("text_on"), "", True, [], None],
                                [1250020, self.getl("text_off"), "", True, [], None]
                            ],
                            self.getv("pop_up_definition_extra_images_icon_path")
                        ],
                        [
                            125010,
                            self.getl("block_txt_box_menu_def_simple_img_number_text") + extra_num_text,
                            self.getl("block_txt_box_menu_def_simple_img_number_tt"),
                            False,
                            [
                                [1250101010, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "1"), "", True, [], None],
                                [1250101020, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "2"), "", True, [], None],
                                [1250101030, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "3"), "", True, [], None],
                                [1250101040, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "4"), "", True, [], None],
                                [1250101050, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "5"), "", True, [], None],
                                [1250101060, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "6"), "", True, [], None],
                                [1250101070, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "7"), "", True, [], None],
                                [1250101080, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "8"), "", True, [], None],
                                [1250101090, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "9"), "", True, [], None],
                                [1250101100, self.getl("block_txt_box_menu_def_simple_img_number_1-5_text").replace("#1", "10"), "", True, [], None],
                                [1250101900, self.getl("block_txt_box_menu_def_simple_img_number_cus_text"), "", True, [], None]
                            ],
                            self.getv("continue_icon_path")
                        ],
                        [
                            125020,
                            self.getl("block_txt_box_menu_def_simple_delay_text") + extra_delay_text,
                            self.getl("block_txt_box_menu_def_simple_delay_tt"),
                            False,
                            [
                                [1250201000, self.getl("block_txt_box_menu_def_simple_delay_none_text"), "", True, [], None],
                                [1250201010, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "1 sec."), "", True, [], None],
                                [1250201020, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "2 sec."), "", True, [], None],
                                [1250201030, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "3 sec."), "", True, [], None],
                                [1250201040, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "4 sec."), "", True, [], None],
                                [1250201050, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "5 sec."), "", True, [], None],
                                [1250201060, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "6 sec."), "", True, [], None],
                                [1250201070, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "7 sec."), "", True, [], None],
                                [1250201080, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "8 sec."), "", True, [], None],
                                [1250201090, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "9 sec."), "", True, [], None],
                                [1250201100, self.getl("block_txt_box_menu_def_simple_delay_num_text").replace("#1", "10 sec."), "", True, [], None],
                                [1250201900, self.getl("block_txt_box_menu_def_simple_delay_cus_text"), "", True, [], None]
                            ],
                            self.getv("continue_icon_path")
                        ],
                        [
                            125030,
                            self.getl("block_txt_box_menu_def_simple_img_duration_text") + extra_duration_text,
                            self.getl("block_txt_box_menu_def_simple_img_duration_tt"),
                            False,
                            [
                                [1250301000, self.getl("block_txt_box_menu_def_simple_duration_forever_text"), "", True, [], None],
                                [1250301010, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "1 sec."), "", True, [], None],
                                [1250301020, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "2 sec."), "", True, [], None],
                                [1250301030, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "3 sec."), "", True, [], None],
                                [1250301040, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "4 sec."), "", True, [], None],
                                [1250301050, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "5 sec."), "", True, [], None],
                                [1250301060, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "6 sec."), "", True, [], None],
                                [1250301070, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "7 sec."), "", True, [], None],
                                [1250301080, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "8 sec."), "", True, [], None],
                                [1250301090, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "9 sec."), "", True, [], None],
                                [1250301100, self.getl("block_txt_box_menu_def_simple_duration_num_text").replace("#1", "10 sec."), "", True, [], None],
                                [1250301900, self.getl("block_txt_box_menu_def_simple_duration_cus_text"), "", True, [], None]
                            ],
                            self.getv("continue_icon_path")
                        ],
                        [
                            125040,
                            self.getl("block_txt_box_menu_def_simple_img_fade_duration_text") + extra_fade_duration_text,
                            self.getl("block_txt_box_menu_def_simple_img_fade_duration_tt"),
                            False,
                            [
                                [1250401000, self.getl("block_txt_box_menu_def_simple_fade_none_text"), "", True, [], None],
                                [1250401005, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "0.5 sec."), "", True, [], None],
                                [1250401010, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "1.0 sec."), "", True, [], None],
                                [1250401015, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "1.5 sec."), "", True, [], None],
                                [1250401020, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "2.0 sec."), "", True, [], None],
                                [1250401025, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "2.5 sec."), "", True, [], None],
                                [1250401030, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "3.0 sec."), "", True, [], None],
                                [1250401035, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "3.5 sec."), "", True, [], None],
                                [1250401040, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "4.0 sec."), "", True, [], None],
                                [1250401045, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "4.5 sec."), "", True, [], None],
                                [1250401050, self.getl("block_txt_box_menu_def_simple_fade_num_text").replace("#1", "5.0 sec."), "", True, [], None],
                                [1250401900, self.getl("block_txt_box_menu_def_simple_fade_cus_text"), "", True, [], None]
                            ],
                            self.getv("continue_icon_path")
                        ],
                        [
                            125050,
                            self.getl("block_txt_box_menu_def_simple_img_next_image_text") + extra_next_text,
                            self.getl("block_txt_box_menu_def_simple_img_next_image_tt"),
                            False,
                            [
                                [1250510, self.getl("text_on"), "", True, [], None],
                                [1250520, self.getl("text_off"), "", True, [], None]
                            ],
                            self.getv("repeat_icon_path")
                        ],
                        [
                            125060,
                            self.getl("block_txt_box_menu_def_simple_img_source_text") + extra_src,
                            self.getl("block_txt_box_menu_def_simple_img_source_tt"),
                            False,
                            [
                                [1250610, self.getl("block_txt_box_menu_def_simple_img_source_toon_text"), self.getl("block_txt_box_menu_def_simple_img_source_toon_tt"), True, [], None],
                                [1250620, self.getl("block_txt_box_menu_def_simple_img_source_def_text"), self.getl("block_txt_box_menu_def_simple_img_source_def_tt"), True, [], None],
                                [1250630, self.getl("block_txt_box_menu_def_simple_img_source_blocks_text"), self.getl("block_txt_box_menu_def_simple_img_source_blocks_tt"), True, [], None],
                                [1250640, self.getl("block_txt_box_menu_def_simple_img_source_app_text"), self.getl("block_txt_box_menu_def_simple_img_source_app_tt"), True, [], None],
                                [1250650, self.getl("block_txt_box_menu_def_simple_img_source_cus_text") + f' [...{self.getv("def_extra_image_custom_source_folder_path")[-30:]}]', self.getl("block_txt_box_menu_def_simple_img_source_cus_tt"), True, [], None]
                            ],
                            self.getv("source_icon_path")
                        ],
                        [
                            125070,
                            self.getl("block_txt_box_menu_def_simple_img_layout_text") + extra_layout_text,
                            self.getl("block_txt_box_menu_def_simple_img_layout_tt"),
                            False,
                            [
                                [1250710, self.getl("block_txt_box_menu_def_simple_img_layout_random_text"), self.getl("block_txt_box_menu_def_simple_img_layout_random_tt"), True, [], None],
                                [1250720, self.getl("block_txt_box_menu_def_simple_img_layout_tile_text"), self.getl("block_txt_box_menu_def_simple_img_layout_tile_tt"), True, [], None]
                            ],
                            self.getv("layout_icon_path")
                        ],
                        [
                            125080,
                            self.getl("block_txt_box_menu_def_simple_img_apperance_text") + extra_apperance_text,
                            self.getl("block_txt_box_menu_def_simple_img_apperance_tt"),
                            False,
                            [
                                [12508010, self.getl("block_txt_box_menu_def_simple_img_apperance_style_random_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_random_tt"), True, [], None],
                                [12508020, self.getl("block_txt_box_menu_def_simple_img_apperance_style_instant_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_instant_tt"), True, [], None],
                                [12508030, self.getl("block_txt_box_menu_def_simple_img_apperance_style_grove_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_grove_tt"), True, [], None],
                                [12508040, self.getl("block_txt_box_menu_def_simple_img_apperance_style_left_up_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_left_up_tt"), True, [], None],
                                [12508050, self.getl("block_txt_box_menu_def_simple_img_apperance_style_right_up_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_right_up_tt"), True, [], None],
                                [12508060, self.getl("block_txt_box_menu_def_simple_img_apperance_style_bot_left_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_bot_left_tt"), True, [], None],
                                [12508070, self.getl("block_txt_box_menu_def_simple_img_apperance_style_bot_right_text"), self.getl("block_txt_box_menu_def_simple_img_apperance_style_bot_right_tt"), True, [], None],
                                [12508500, self.getl("block_txt_box_menu_def_simple_img_apperance_duration_text") + extra_apperance_duration_text, self.getl("block_txt_box_menu_def_simple_img_apperance_duration_tt"), True, [], None]
                            ],
                            self.getv("apperance_icon_path")
                        ]
                    ],
                    self.getv("pop_up_definition_extra_images_icon_path")
                ],
                [
                    130,
                    self.getl("block_txt_box_menu_def_show_text") + f" ({definition_word})",
                    self.getl("block_txt_box_menu_def_show_tt"),
                    True,
                    [],
                    self.getv("definition_add_win_icon_path")
                ],
                [
                    133,
                    self.getl("block_txt_box_menu_def_enum_text") + def_enum_count_word,
                    self.getl("block_txt_box_menu_def_enum_tt"),
                    True,
                    definitions_list,
                    self.getv("list_icon_path")
                ],
                [
                    134,
                    self.getl("block_txt_box_menu_show_dicts_text").replace("#1", dict_search_term),
                    self.getl("block_txt_box_menu_show_dicts_tt"),
                    True,
                    [
                        [
                            134010,
                            self.getl("block_txt_box_menu_show_dicts_on_text"),
                            self.getl("block_txt_box_menu_show_dicts_on_tt"),
                            True,
                            [],
                            None
                        ],
                        [
                            134020,
                            self.getl("block_txt_box_menu_show_dicts_off_text"),
                            self.getl("block_txt_box_menu_show_dicts_off_tt"),
                            True,
                            [],
                            None
                        ]
                    ],
                    self.getv("dictionaries_icon_path")
                ],
                [
                    135,
                    self.getl("block_txt_box_menu_wiki_search_text").replace("#1", dict_search_term),
                    self.getl("block_txt_box_menu_wiki_search_tt"),
                    True,
                    [],
                    self.getv("wiki_logo_icon_path")
                ],
                [
                    139,
                    self.getl("block_txt_box_menu_browse_images_text"),
                    self.getl("block_txt_box_menu_browse_images_tt"),
                    True,
                    [],
                    self.getv("picture_view_win_icon_path")
                ],
                [
                    140,
                    self.getl("block_txt_box_menu_add_image_text"),
                    self.getl("block_txt_box_menu_add_image_tt"),
                    True,
                    [],
                    self.getv("picture_view_win_icon_path")
                ],
                [
                    145,
                    self.getl("block_txt_box_menu_auto_add_image_text"),
                    self.getl("block_txt_box_menu_auto_add_image_tt"),
                    True,
                    [],
                    self.getv("images_icon_path")
                ],
                [
                    150,
                    self.getl("block_txt_box_menu_add_file_text"),
                    self.getl("block_txt_box_menu_add_file_tt"),
                    True,
                    [],
                    self.getv("block_txt_box_menu_add_file_icon_path")
                ],
                [
                    160,
                    self.getl("block_txt_box_menu_find_in_app_text"),
                    self.getl("block_txt_box_menu_find_in_app_tt"),
                    True,
                    [],
                    self.getv("find_in_app_win_icon_path")
                ],
                [
                    170,
                    self.getl("block_txt_box_menu_translate_text"),
                    self.getl("block_txt_box_menu_translate_tt"),
                    True,
                    [],
                    self.getv("translate_win_icon_path")
                ]
            ]
        }

        # Disable define selected or highlighted if no data
        if not sel_text:
            menu_dict["disabled"].append(90)
        if not hl_word:
            menu_dict["disabled"].append(100)

        # Disable / Enable text operation items
        if not self._undo_available:
            menu_dict["disabled"].append(10)
        if not self._redo_available:
            menu_dict["disabled"].append(20)
        if not self.txt_box.canPaste():
            menu_dict["disabled"].append(50)
        if not self.txt_box.textCursor().hasSelection():
            menu_dict["disabled"].append(30)
            menu_dict["disabled"].append(40)
            menu_dict["disabled"].append(60)

        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self.txt_box)

        if self.get_appv("menu")["result"] == 10:
            self.txt_box.undo()
        elif self.get_appv("menu")["result"] == 20:
            self.txt_box.redo()
        elif self.get_appv("menu")["result"] == 30:
            self.txt_box.cut()
        elif self.get_appv("menu")["result"] == 40:
            self.txt_box.copy()
        elif self.get_appv("menu")["result"] == 50:
            self.txt_box.paste()
        elif self.get_appv("menu")["result"] == 60:
            cursor = self.txt_box.textCursor()
            cursor.removeSelectedText()
            self.txt_box.setTextCursor(cursor)
        elif self.get_appv("menu")["result"] == 70010:
            self.setv("show_autocomplete", True)
        elif self.get_appv("menu")["result"] == 70020:
            self.setv("show_autocomplete", False)
        elif self.get_appv("menu")["result"] == 80010:
            self.setv("show_word_highlight", True)
        elif self.get_appv("menu")["result"] == 80020:
            self.setv("show_word_highlight", False)
        elif self.get_appv("menu")["result"] == 83010:
            self.setv("http_hyperlink_text_detection_enabled", True)
            self.setv("hyperlink_mark_enabled", True)
            self.clear_definition_formating()
        elif self.get_appv("menu")["result"] == 83020:
            self.setv("http_hyperlink_text_detection_enabled", True)
            self.setv("hyperlink_mark_enabled", False)
            self.clear_definition_formating()
        elif self.get_appv("menu")["result"] == 83030:
            self.setv("http_hyperlink_text_detection_enabled", False)
            self.setv("hyperlink_mark_enabled", False)
            self.clear_definition_formating()
        elif self.get_appv("menu")["result"] == 86010:
            self.setv("numbers_in_block_text_mark_enabled", True)
            self.clear_definition_formating()
        elif self.get_appv("menu")["result"] == 86020:
            self.setv("numbers_in_block_text_mark_enabled", False)
            self.clear_definition_formating()
        elif self.get_appv("menu")["result"] == 8710:
            self.setv("definition_hint_enabled", True)
            self._definition_hint.refresh()
        elif self.get_appv("menu")["result"] == 8720:
            self.setv("definition_hint_enabled", False)
        elif self.get_appv("menu")["result"] == 90:
            if self._check_expression_lenght(self.txt_box.textCursor().selectedText()):
                txt = self.txt_box.toPlainText()
                txt = UTILS.TextUtility.replace_special_chars(txt)
                cursor = self.txt_box.textCursor()
                start_sel = txt[:cursor.selectionStart()].rfind(" ")
                end_sel = txt[cursor.selectionEnd():].find(" ") + cursor.selectionEnd()
                if end_sel == -1:
                    end_sel = len(txt)
                expression = self.txt_box.toPlainText()[start_sel + 1:end_sel]
                definition_cls.AddDefinition(self._stt, self._main_win, expression=expression)
                self._populate_def_list()
                self.check_definitions()
        elif self.get_appv("menu")["result"] == 100:
            if self._check_expression_lenght(hl_word):
                expression = hl_word
                definition_cls.AddDefinition(self._stt, self._main_win, expression=expression)
                try:
                    self._populate_def_list()
                    self.check_definitions()
                except Exception as e:
                    UTILS.LogHandler.add_log_record("#1: Exception in function #2.\nException: #3", ["TextHandler", "show_context_menu->add_definition", str(e)], warning_raised=True)
        elif self.get_appv("menu")["result"] == 105:
            if self.txt_box.textCursor().selectedText():
                txt = self.txt_box.toPlainText()
                txt = UTILS.TextUtility.replace_special_chars(txt)
                cursor = self.txt_box.textCursor()
                start_sel = txt[:cursor.selectionStart()].rfind(" ")
                end_sel = txt[cursor.selectionEnd():].find(" ") + cursor.selectionEnd()
                if end_sel == -1:
                    end_sel = len(txt)
                expression = txt[start_sel + 1:end_sel]
                definition_cls.FindDefinition(self._stt, self._main_win, expression=expression)
            else:
                if hl_word:
                    definition_cls.FindDefinition(self._stt, self._main_win, expression=hl_word)
        elif self.get_appv("menu")["result"] == 110010:
            self.setv("definition_text_mark_enabled", True)
            self._populate_def_list()
            self.check_definitions()
        elif self.get_appv("menu")["result"] == 110020:
            self.setv("definition_text_mark_enabled", False)
            self.clear_definition_formating()
        elif self.get_appv("menu")["result"] == 120010:
            self.setv("definition_show_on_mouse_hover", True)
        elif self.get_appv("menu")["result"] == 120020:
            self.setv("definition_show_on_mouse_hover", False)
        elif self.get_appv("menu")["result"] == 130:
            db_def = definition_cls.ViewDefinition(self._stt, self.txt_box, definition_id)
        elif self.get_appv("menu")["result"] == 139:
            if self.txt_box._data_dict["media"]:
                utility_cls.PictureBrowse(self._stt, self._main_win, self.txt_box._data_dict["media"])
        elif self.get_appv("menu")["result"] == 140:
            self.txt_box.add_image()
        elif self.get_appv("menu")["result"] == 145:
            self.txt_box.block_event("body_txt_box", "auto_add_images")
        elif self.get_appv("menu")["result"] == 150:
            self.txt_box.add_files()
        elif self.get_appv("menu")["result"] == 160:
            utility_cls.FindInApp(self._stt, self._main_win)
        elif self.get_appv("menu")["result"] == 170:
            trans = utility_cls.Translate(self._stt, self.txt_box)
            text = None
            if self.txt_box.textCursor().selectedText():
                text = self.txt_box.textCursor().selectedText()
            trans.show_gui(text)
        elif self.get_appv("menu")["result"] == 1250010:
            self.setv("show_definition_extra_image", True)
        elif self.get_appv("menu")["result"] == 1250020:
            self.setv("show_definition_extra_image", False)
        elif self.get_appv("menu")["result"] == 1250101010:
            self.setv("def_extra_image_max_number_of_images", 1)
        elif self.get_appv("menu")["result"] == 1250101020:
            self.setv("def_extra_image_max_number_of_images", 2)
        elif self.get_appv("menu")["result"] == 1250101030:
            self.setv("def_extra_image_max_number_of_images", 3)
        elif self.get_appv("menu")["result"] == 1250101040:
            self.setv("def_extra_image_max_number_of_images", 4)
        elif self.get_appv("menu")["result"] == 1250101050:
            self.setv("def_extra_image_max_number_of_images", 5)
        elif self.get_appv("menu")["result"] == 1250101060:
            self.setv("def_extra_image_max_number_of_images", 6)
        elif self.get_appv("menu")["result"] == 1250101070:
            self.setv("def_extra_image_max_number_of_images", 7)
        elif self.get_appv("menu")["result"] == 1250101080:
            self.setv("def_extra_image_max_number_of_images", 8)
        elif self.get_appv("menu")["result"] == 1250101090:
            self.setv("def_extra_image_max_number_of_images", 9)
        elif self.get_appv("menu")["result"] == 1250101100:
            self.setv("def_extra_image_max_number_of_images", 10)
        elif self.get_appv("menu")["result"] == 1250101900:
            data_dict = {
                "id": 0,
                "name": "block_input_box_name",
                "input_hint": self.getl("block_txt_box_menu_def_simple_img_number_text"),
                "text": str(self.getv("def_extra_image_max_number_of_images")),
                "description": self.getl("def_extra_image_max_number_of_images_info_box_desc"),
                "result": ""
            }
            utility_cls.InputBoxSimple(self._stt, self.txt_box, input_dict=data_dict)
            rslt = data_dict["result"]
            if self._is_user_input_valid(rslt, 0, 100):
                try:
                    rslt = int(data_dict["result"])
                except ValueError:
                    rslt = None
                if rslt:
                    self.setv("def_extra_image_max_number_of_images", rslt)
        elif self.get_appv("menu")["result"] == 1250201000:
            self.setv("def_extra_image_start_delay", 0)
        elif self.get_appv("menu")["result"] == 1250201010:
            self.setv("def_extra_image_start_delay", 1000)
        elif self.get_appv("menu")["result"] == 1250201020:
            self.setv("def_extra_image_start_delay", 2000)
        elif self.get_appv("menu")["result"] == 1250201030:
            self.setv("def_extra_image_start_delay", 3000)
        elif self.get_appv("menu")["result"] == 1250201040:
            self.setv("def_extra_image_start_delay", 4000)
        elif self.get_appv("menu")["result"] == 1250201050:
            self.setv("def_extra_image_start_delay", 5000)
        elif self.get_appv("menu")["result"] == 1250201060:
            self.setv("def_extra_image_start_delay", 6000)
        elif self.get_appv("menu")["result"] == 1250201070:
            self.setv("def_extra_image_start_delay", 7000)
        elif self.get_appv("menu")["result"] == 1250201080:
            self.setv("def_extra_image_start_delay", 8000)
        elif self.get_appv("menu")["result"] == 1250201090:
            self.setv("def_extra_image_start_delay", 9000)
        elif self.get_appv("menu")["result"] == 1250201100:
            self.setv("def_extra_image_start_delay", 10000)
        elif self.get_appv("menu")["result"] == 1250201900:
            data_dict = {
                "id": 0,
                "name": "block_input_box_name",
                "input_hint": self.getl("block_txt_box_menu_def_simple_delay_text"),
                "text": str(self.getv("def_extra_image_start_delay") / 1000),
                "description": self.getl("def_extra_image_delay_info_box_desc"),
                "result": ""
            }
            utility_cls.InputBoxSimple(self._stt, self.txt_box, input_dict=data_dict)
            rslt = data_dict["result"]
            if self._is_user_input_valid(rslt, 0, 60):
                try:
                    rslt = int(float(data_dict["result"]) * 1000)
                except ValueError:
                    rslt = None
                if rslt:
                    self.setv("def_extra_image_start_delay", rslt)
        elif self.get_appv("menu")["result"] == 1250301000:
            self.setv("def_extra_image_auto_hide", 0)
        elif self.get_appv("menu")["result"] == 1250301010:
            self.setv("def_extra_image_auto_hide", 1000)
        elif self.get_appv("menu")["result"] == 1250301020:
            self.setv("def_extra_image_auto_hide", 2000)
        elif self.get_appv("menu")["result"] == 1250301030:
            self.setv("def_extra_image_auto_hide", 3000)
        elif self.get_appv("menu")["result"] == 1250301040:
            self.setv("def_extra_image_auto_hide", 4000)
        elif self.get_appv("menu")["result"] == 1250301050:
            self.setv("def_extra_image_auto_hide", 5000)
        elif self.get_appv("menu")["result"] == 1250301060:
            self.setv("def_extra_image_auto_hide", 6000)
        elif self.get_appv("menu")["result"] == 1250301070:
            self.setv("def_extra_image_auto_hide", 7000)
        elif self.get_appv("menu")["result"] == 1250301080:
            self.setv("def_extra_image_auto_hide", 8000)
        elif self.get_appv("menu")["result"] == 1250301090:
            self.setv("def_extra_image_auto_hide", 9000)
        elif self.get_appv("menu")["result"] == 1250301100:
            self.setv("def_extra_image_auto_hide", 10000)
        elif self.get_appv("menu")["result"] == 1250301900:
            data_dict = {
                "id": 0,
                "name": "block_input_box_name",
                "input_hint": self.getl("block_txt_box_menu_def_simple_img_duration_text"),
                "text": str(self.getv("def_extra_image_auto_hide") / 1000),
                "description": self.getl("def_extra_image_duration_info_box_desc"),
                "result": ""
            }
            utility_cls.InputBoxSimple(self._stt, self.txt_box, input_dict=data_dict)
            rslt = data_dict["result"]
            if self._is_user_input_valid(rslt, 0, 3600):
                try:
                    rslt = int(float(data_dict["result"]) * 1000)
                except ValueError:
                    rslt = None
                if rslt:
                    self.setv("def_extra_image_auto_hide", rslt)
        elif self.get_appv("menu")["result"] == 1250401000:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 0)
        elif self.get_appv("menu")["result"] == 1250401005:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 500)
        elif self.get_appv("menu")["result"] == 1250401010:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 1000)
        elif self.get_appv("menu")["result"] == 1250401015:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 1500)
        elif self.get_appv("menu")["result"] == 1250401020:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 2000)
        elif self.get_appv("menu")["result"] == 1250401025:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 2500)
        elif self.get_appv("menu")["result"] == 1250401030:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 3000)
        elif self.get_appv("menu")["result"] == 1250401035:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 3500)
        elif self.get_appv("menu")["result"] == 1250401040:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 4000)
        elif self.get_appv("menu")["result"] == 1250401045:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 4500)
        elif self.get_appv("menu")["result"] == 1250401050:
            self.setv("def_extra_image_auto_hide_fade_out_duration", 5000)
        elif self.get_appv("menu")["result"] == 1250401900:
            data_dict = {
                "id": 0,
                "name": "block_input_box_name",
                "input_hint": self.getl("block_txt_box_menu_def_simple_img_fade_duration_text"),
                "text": str(self.getv("def_extra_image_auto_hide_fade_out_duration") / 1000),
                "description": self.getl("def_extra_image_fade_duration_info_box_desc"),
                "result": ""
            }
            utility_cls.InputBoxSimple(self._stt, self.txt_box, input_dict=data_dict)
            rslt = data_dict["result"]
            if self._is_user_input_valid(rslt, 0, 60):
                try:
                    rslt = int(float(data_dict["result"]) * 1000)
                except ValueError:
                    rslt = None
                if rslt:
                    self.setv("def_extra_image_auto_hide_fade_out_duration", rslt)
        elif self.get_appv("menu")["result"] == 1250510:
            self.setv("def_extra_image_show_next_after_hide", True)
        elif self.get_appv("menu")["result"] == 1250520:
            self.setv("def_extra_image_show_next_after_hide", False)
        elif self.get_appv("menu")["result"] == 1250610:
            self.setv("def_extra_image_source", 1)
        elif self.get_appv("menu")["result"] == 1250620:
            self.setv("def_extra_image_source", 2)
        elif self.get_appv("menu")["result"] == 1250630:
            self.setv("def_extra_image_source", 3)
        elif self.get_appv("menu")["result"] == 1250640:
            self.setv("def_extra_image_source", 4)
        elif self.get_appv("menu")["result"] == 1250650:
            self.setv("def_extra_image_source", 5)
            file_ut = utility_cls.FileDialog(self._stt)
            file_ut_result = file_ut.show_dialog_select_folder(directory=self.getv("def_extra_image_custom_source_folder_path"))
            if file_ut_result:
                self.setv("def_extra_image_custom_source_folder_path", file_ut_result)
        elif self.get_appv("menu")["result"] == 1250710:
            self.setv("def_extra_image_layout", 1)
        elif self.get_appv("menu")["result"] == 1250720:
            self.setv("def_extra_image_layout", 2)
        elif self.get_appv("menu")["result"] is not None and self.get_appv("menu")["result"] > 1330000000000 and self.get_appv("menu")["result"] < 1339000000000:
            definition_cls.BrowseDefinitions(self._stt, self._main_win, self.get_appv("menu")["result"] - 1330000000000)
        elif self.get_appv("menu")["result"] == 133:
            if self._get_unique_definition_ids_in_block():
                definition_cls.BrowseDefinitions(self._stt, self._main_win, list(self._get_unique_definition_ids_in_block().keys()))
        elif self.get_appv("menu")["result"] == 12508010:
            self.setv("def_extra_image_animate_style", 0)
        elif self.get_appv("menu")["result"] == 12508020:
            self.setv("def_extra_image_animate_style", 1)
        elif self.get_appv("menu")["result"] == 12508030:
            self.setv("def_extra_image_animate_style", 2)
        elif self.get_appv("menu")["result"] == 12508040:
            self.setv("def_extra_image_animate_style", 3)
        elif self.get_appv("menu")["result"] == 12508050:
            self.setv("def_extra_image_animate_style", 4)
        elif self.get_appv("menu")["result"] == 12508060:
            self.setv("def_extra_image_animate_style", 5)
        elif self.get_appv("menu")["result"] == 12508070:
            self.setv("def_extra_image_animate_style", 6)
        elif self.get_appv("menu")["result"] == 12508500:
            data_dict = {
                "id": 0,
                "name": "block_input_box_name",
                "input_hint": self.getl("block_txt_box_menu_def_simple_img_apperance_duration_text"),
                "text": str(self.getv("def_extra_image_animate_show") / 1000),
                "description": self.getl("def_extra_image_apperance_duration_info_box_desc"),
                "result": ""
            }
            utility_cls.InputBoxSimple(self._stt, self.txt_box, input_dict=data_dict)
            rslt = data_dict["result"]
            if self._is_user_input_valid(rslt, 0, 60):
                try:
                    rslt = int(float(data_dict["result"]) * 1000)
                except ValueError:
                    rslt = None
                if rslt:
                    self.setv("def_extra_image_animate_show", rslt)
        elif self.get_appv("menu")["result"] == 134:
            if not self.dicts:
                self.dicts = dict_cls.DictFrame(self._stt, self._main_win, self.txt_box)
            self.dicts.show_word(dict_search_term.strip("()"))
        elif self.get_appv("menu")["result"] == 135:
            search_string = sel_text
            if not search_string:
                search_string = dict_search_term.strip("()")
            wikipedia_cls.Wikipedia(self.txt_box, self._stt, search_string)
        elif self.get_appv("menu")["result"] == 134010:
            self.setv("dictionaries_search_notification", True)
        elif self.get_appv("menu")["result"] == 134020:
            self.setv("dictionaries_search_notification", False)

            # Add user defined folders selection from Settings

    def _get_def_list_for_context_menu(self, number_of_items_per_menu: int = 10) -> list:
        """
        Menu ID  1,330,000,000,000 - 1,339,000,000,000
        
        Generates a context menu with definitions used in the text.

        Parameters:
        - number_of_items_per_menu (int): The maximum number of items to show per submenu. Default 10.

        Returns:
        - list: A list of menu items to show in the context menu.

        This iterates through _text_def_map to get a unique list of definitions used. 
        It groups the definitions by ID.
        For each ID group, it creates a submenu up to the number_of_items_per_menu limit.
        Once the limit is reached, a "next" item is added to continue to the next submenu.
        The submenus are created by _create_menu_for_def_list.
        The menu items themselves are generated by _create_menu_item_for_def_list.
        """
        unique_defs = self._get_unique_definition_ids_in_block()
        
        if not unique_defs:
            return []
        
        db_def_obj = db_definition_cls.Definition(self._stt)
        
        menu_items = self._create_menu_for_def_list(unique_defs, self._text_def_map[0][0], number_of_items_per_menu=number_of_items_per_menu, db_def_obj=db_def_obj)

        return menu_items

    def _get_unique_definition_ids_in_block(self) -> dict:
        unique_defs = {}

        for i in self._text_def_map:
            if i[0] not in unique_defs:
                unique_defs[i[0]] = {}
                unique_defs[i[0]]["count"] = 0
                unique_defs[i[0]]["list"] = []
            
            unique_defs[i[0]]["count"] += 1
            if i[1].strip() not in unique_defs[i[0]]["list"]:
                unique_defs[i[0]]["list"].append(i[1].strip())

        return unique_defs

    def _create_menu_for_def_list(self, defs_dict: dict, start_from: str, number_of_items_per_menu: int = 10, db_def_obj: db_definition_cls.Definition = None):
        if db_def_obj is None:
            db_def_obj = db_definition_cls.Definition(self._stt)
        result = []
        active = False
        counter = 0
        for i in defs_dict:
            if i == start_from:
                active = True
            if active:
                if counter >= number_of_items_per_menu:
                    item = self._create_menu_item_for_def_list("", 0, create_next_item=True)
                    item[4] = self._create_menu_for_def_list(defs_dict=defs_dict, start_from=i, number_of_items_per_menu=number_of_items_per_menu, db_def_obj=db_def_obj)
                    result.append(item)
                    active = False
                if active:
                    db_def_obj.load_definition(int(i))
                    result.append(self._create_menu_item_for_def_list(
                        f'{db_def_obj.definition_name}  ({", ".join(defs_dict[i]["list"])})  ({defs_dict[i]["count"]})',
                        1330000000000 + int(i)
                    ))
                    counter += 1

        return result
    
    def _create_menu_item_for_def_list(self, text: str, id: int, clicable: bool = True, create_next_item: bool = False) -> list:
        if create_next_item:
            result = [
                1339000,
                self.getl("def_list_menu_item_next_text"),
                self.getl("def_list_menu_item_next_tt"),
                False,
                [],
                self.getv("continue_icon_path")
            ]
        else:
            result = [
                id,
                text,
                "",
                clicable,
                [],
                None
            ]
        return result

    def _is_user_input_valid(self, user_input: str, range_from: float = None, range_to: float = None, display_msg: bool = True) -> bool:
        if not user_input:
            return False
        
        try:
            result = float(user_input)
        except ValueError:
            result = None
        
        if result is None:
            if display_msg:
                data_dict = {
                    "title": self.getl("user_input_error_not_number_title"),
                    "text": self.getl("user_input_error_not_number_text"),
                    "icon_path": self.getv("warning_icon_path")
                }
                utility_cls.MessageInformation(self._stt, self._main_win, data_dict=data_dict)
            return False
        
        valid_range = True
        if range_from:
            if result < range_from:
                valid_range = False
        if range_to:
            if result > range_to:
                valid_range = False
        if not valid_range:
            if display_msg:
                data_dict = {
                    "title": self.getl("user_input_error_number_not_in_range_title"),
                    "text": self.getl("user_input_error_number_not_in_range_text").replace("#1", str(range_from)).replace("#2", str(range_to)),
                    "icon_path": self.getv("warning_icon_path")
                }
                utility_cls.MessageInformation(self._stt, self._main_win, data_dict=data_dict)
            return False

        return True

    def _check_expression_lenght(self, txt: str) -> bool:
        txt = UTILS.TextUtility.replace_special_chars(txt)
        
        if len(txt.strip()) < self.getv("definition_minimum_word_lenght"):
            msg_text = self.getl("def_msg_word_to_short_text").replace("#1", txt.strip()).replace("#2", str(self.getv("definition_minimum_word_lenght")))
            msg_dict = {
                "title": self.getl("def_msg_word_to_short_title"),
                "text": msg_text,
                "icon_path": self.getv("definition_icon_path")
            }
            utility_cls.MessageInformation(self._stt, self._main_win, msg_dict)
            return False
        
        if len(txt.strip()) > self.getv("definition_maximum_word_lenght"):
            msg_text = self.getl("def_msg_word_to_long_text").replace("#1", str(self.getv("definition_maximum_word_lenght")))
            msg_dict = {
                "title": self.getl("def_msg_word_to_long_title"),
                "text": msg_text,
                "icon_path": self.getv("definition_icon_path")
            }
            utility_cls.MessageInformation(self._stt, self._main_win, msg_dict)
            return False
        
        return True

    def _populate_def_list(self):
        self._def_list = self.get_appv("text_handler_data").get_data()

        # def_list = db_def.get_list_of_all_expressions()
        # self._def_list = [[x[0], x[1]] for x in def_list]
        # self._def_list.sort(key = lambda expression: len(expression[0]))

        self._definition_hint.refresh()

    def check_definitions(self, e: QtGui.QMouseEvent = None):
        """
        self._text_def_map:[]
            definition_id
            expression
            start_pos
            end_pos
        """
        if self._calc_mode:
            return

        v_scroll = None
        v_scroll = self.txt_box.verticalScrollBar().value()
        if e:
            v_scroll = self.txt_box.verticalScrollBar().value()
            cur = self.txt_box.cursorForPosition(e.pos())
        else:
            cur = self.txt_box.textCursor()

        old_cursor_pos = cur.position()

        self.clear_definition_formating()

        self._check_hyperlink()
        self._mark_numbers()

        cur = self.txt_box.textCursor()
        old_cf = cur.charFormat()

        if not self.getv("definition_text_mark_enabled"):
            if v_scroll is not None:
                self.txt_box.verticalScrollBar().setValue(v_scroll)
            cur.setPosition(old_cursor_pos)
            cur.setCharFormat(old_cf)
            self.txt_box.setTextCursor(cur)
            return

        self._text_def_map = []
        
        txt = self.txt_box.toPlainText().lower()

        # Search for expressions
        
        for expression in self._def_list:
            pos = 0
            while pos != -1:
                pos = txt.find(expression[0], pos)

                if pos != -1:
                    left_char = True if pos == 0 or UTILS.TextUtility.is_special_char(txt[pos - 1]) else False
                    right_char = True if pos + len(expression[0]) == len(txt) or UTILS.TextUtility.is_special_char(txt[pos + len(expression[0])]) else False
                    if left_char and right_char:
                        self._text_def_map.append([expression[1], expression[0], pos, pos + len(expression[0])])
                    pos += len(expression[0])

        # Mark expressions in text box
        cf = QTextCharFormat()
        color = QColor()
        color.setNamedColor(self.getv("definition_text_mark_color"))
        if self.getv("definition_text_mark_color"):
            cf.setForeground(color)
        color.setNamedColor(self.getv("definition_text_mark_background"))
        if self.getv("definition_text_mark_background"):
            cf.setBackground(color)

        for i in self._text_def_map:
            if self._get_hyperlink_for_position(i[2]):
                cf.setFontUnderline(True)
            else:
                cf.setFontUnderline(False)
            
            cur.setPosition(i[2])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[3] - i[2])
            cur.setCharFormat(cf)
            self.txt_box.setTextCursor(cur)
        
        if v_scroll is not None:
            self.txt_box.verticalScrollBar().setValue(v_scroll)
        cur.setPosition(old_cursor_pos)
        cur.setCharFormat(old_cf)
        self.txt_box.setTextCursor(cur)

    def _get_hyperlink_for_position(self, cursor_position: int) -> str:
        if not self.getv("hyperlink_mark_enabled"):
            return None

        for i in self._hyperlink_list:
            if cursor_position in range(i[0], i[1]):
                return i[2]
        return None

    def _mark_numbers(self):
        if self._calc_mode:
            return

        if not self.getv("numbers_in_block_text_mark_enabled"):
            return

        txt = self.txt_box.toPlainText()
        txt = UTILS.TextUtility.replace_special_chars(txt)
        
        txt_list = [x + " " for x in txt.split(" ")]
        
        # Mark numbers in text box
        cur = self.txt_box.textCursor()
        old_cursor_pos = cur.position()

        old_cf = cur.charFormat()
        cf = QTextCharFormat()
        color = QColor()
        color.setNamedColor(self.getv("numbers_in_block_content_mark_forecolor"))
        cf.setForeground(color)
        
        currency_list = [x.strip().lower() for x in self.getv("currency_list").split(",")]
        currency_list.sort(key=len, reverse=True)

        pos = 0
        for word in txt_list:
            try:
                _ = float(word)
            except ValueError:
                if word[0].isnumeric() or word[-2:-1].isnumeric():
                    # currency_list = self.getv("currency_list").split(",")
                    word = word.lower()
                    for currency in currency_list:
                        # currency = currency.lower().strip()
                        if word.find(currency) >= 0:
                            word = word.replace(currency, " " * len(currency))
                    try:
                        _ = float(word)
                    except ValueError:
                        pos += len(word)
                        continue
                else:
                    pos += len(word)
                    continue
            
            cur.setPosition(pos)
            cur.movePosition(cur.Right, cur.KeepAnchor, len(word) - 1)
            cur.setCharFormat(cf)
            
            self.txt_box.setTextCursor(cur)
            pos += len(word)
        
        cur.setPosition(old_cursor_pos)
        cur.setCharFormat(old_cf)
        self.txt_box.setTextCursor(cur)

    def _check_hyperlink(self):
        if self._calc_mode:
            return

        txt = self.txt_box.toPlainText().replace("\n", " ").replace("\t", " ")
        self._hyperlink_list = []

        if not self.getv("http_hyperlink_text_detection_enabled"):
            return

        # Search for HTTPS keyword
        pos = 0
        while pos >= 0:
            pos = txt.find("https://", pos)
            if pos >= 0:
                start = pos
                end = txt.find(" ", pos)
                if end == -1:
                    end = len(txt)
                http_text = txt[start:end]
                self._hyperlink_list.append([start, end, http_text])
                pos = end

        # Search for HTTP keyword
        pos = 0
        while pos >= 0:
            pos = txt.find("http://", pos)
            if pos >= 0:
                is_new = True
                for i in self._hyperlink_list:
                    if pos in range(i[0], i[1]):
                        is_new = False
                        pos = i[1]
                        break
                if is_new:
                    start = pos
                    end = txt.find(" ", pos)
                    if end == -1:
                        end = len(txt)
                    http_text = txt[start:end]
                    self._hyperlink_list.append([start, end, http_text])
                    pos = end

        # Search for WWW keyword
        pos = 0
        while pos >= 0:
            pos = txt.find("www.", pos)
            if pos >= 0:
                is_new = True
                for i in self._hyperlink_list:
                    if pos in range(i[0], i[1]):
                        is_new = False
                        pos = i[1]
                        break
                if is_new:
                    start = pos
                    end = txt.find(" ", pos)
                    if end == -1:
                        end = len(txt)
                    http_text = txt[start:end]
                    self._hyperlink_list.append([start, end, http_text])
                    pos = end

        if not self.getv("hyperlink_mark_enabled"):
            return
        
        # Mark hyperlink in text box
        cur = self.txt_box.textCursor()
        old_cursor_pos = cur.position()

        old_cf = cur.charFormat()
        cf = QTextCharFormat()
        cf.setFontUnderline(True)
        
        for i in self._hyperlink_list:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.setCharFormat(cf)
            
            self.txt_box.setTextCursor(cur)
        
        cur.setPosition(old_cursor_pos)
        cur.setCharFormat(old_cf)
        self.txt_box.setTextCursor(cur)

    def smart_parenthesis_selection(self, e: QtGui.QKeyEvent) -> bool:
        if self._calc_mode:
            return False
        
        if not self.getv("block_editor_smart_parenthesis_enabled"):
            return False

        txt = self.txt_box.toPlainText()

        if not txt:
            return False
        
        cur = self.txt_box.textCursor()

        if not cur.hasSelection():
            return False
        
        old_cursor_pos = cur.selectionEnd()

        if e.text() not in [x[0] for x in self.PARENTHESIS_KEY_MAP]:
            return False
        
        txt = f"{e.text()}{cur.selectedText()}{[x[1] for x in self.PARENTHESIS_KEY_MAP if x[0] == e.text()][0]}"

        cur.insertText(txt)

        cur.setPosition(old_cursor_pos + 2)
        self.txt_box.setTextCursor(cur)

        self.check_definitions()
        return True

    def smart_parenthesis_command(self) -> bool:
        cur = self.txt_box.textCursor()
        old_cur_pos = cur.position()

        txt = self.txt_box.toPlainText()
        txt_left = txt[:cur.position()]
        txt_right = txt[cur.position():]

        # Command for smart parenthesis is @(num_of_words)
        # If command is stick to right word then search for next word in right
        # If command is stick to left word or in middle of word then search for previous word in left

        # Define command
        comm_start = txt_left.rfind("@")
        if comm_start == -1 or not ((len(txt_left) - comm_start) > 2):
            return False

        left_par = None
        right_par = None
        for i in self.PARENTHESIS_KEY_MAP:
            if txt_left[comm_start + 1] == i[0]:
                left_par = i[0]
                right_par = i[1]
                break
        
        if not left_par or len(txt_left[comm_start:]) < 3 or txt_left[comm_start + 2:].find(right_par) == -1:
            return False

        # Define number of words
        num_of_words_str = txt_left[comm_start + 2:txt_left.rfind(right_par)]
        command_len = len(num_of_words_str) + 3
        if not num_of_words_str:
            num_of_words_str = "1"
        
        num_of_words = UTILS.TextUtility.get_integer(num_of_words_str)

        if num_of_words is None:
            return False
        
        # Determine side to stick
        side = None
        if txt_left[comm_start - 1] != " ":
            side = "left"
        elif txt_right[0] != " " and txt_right.strip():
            side = "right"
    
        if not side:
            return False

        # Select words
        txt_left = UTILS.TextUtility.replace_special_chars(txt_left)
        txt_right = UTILS.TextUtility.replace_special_chars(txt_right)

        new_text = self.txt_box.toPlainText()

        if side == "left":
            pos = comm_start
            in_word = False
            while num_of_words > 0 and pos > 0:
                pos -= 1
                char = txt_left[pos]
                if char == " ":
                    if in_word:
                        num_of_words -= 1
                    in_word = False
                else:
                    in_word = True
            if pos != 0:
                pos += 1

            new_text = f"{new_text[:pos]}{left_par}{new_text[pos:comm_start]}{right_par}{new_text[len(txt_left):]}"
            new_cur_pos = comm_start + 2
            
        else:
            pos = 0
            in_word = False
            while num_of_words > 0 and pos < len(txt_right):
                char = txt_right[pos]
                if char == " ":
                    if in_word:
                        num_of_words -= 1
                    in_word = False
                else:
                    in_word = True
                pos += 1
            
            right_start = len(txt_left)
            if num_of_words == 0:
                pos -= 1
            pos += len(txt_left)
            new_text = f"{new_text[:comm_start]}{left_par}{new_text[right_start:pos]}{right_par}{new_text[pos:]}"
            new_cur_pos = old_cur_pos - command_len

        self.txt_box.setPlainText(new_text)
        cur = self.txt_box.textCursor()
        cur.setPosition(new_cur_pos)
        self.txt_box.setTextCursor(cur)

        self.check_definitions()
        return True

    def clear_definition_formating(self):
        if self._calc_mode:
            return
        cur = self.txt_box.textCursor()
        old_cur_pos = cur.position()

        cur.setPosition(len(self.txt_box.toPlainText()))
        cur.movePosition(cur.Left, cur.KeepAnchor, len(self.txt_box.toPlainText()))
        cur.setCharFormat(self._real_char_format)
        cur.setPosition(len(self.txt_box.toPlainText()))
        self.txt_box.setTextCursor(cur)

        cur = self.txt_box.textCursor()
        cur.setPosition(old_cur_pos)
        self.txt_box.setTextCursor(cur)

    def mouse_press_event(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.LeftButton:
            if self.txt_box.viewport().cursor().shape() == Qt.PointingHandCursor:
                cursor = self.txt_box.cursorForPosition(e.pos())
                for i in self._hyperlink_list:
                    if cursor.position() in range(i[0], i[1]):
                        webbrowser.open_new_tab(i[2])
                        break

    def show_definition_on_mouse_hover(self, e: QtGui.QMouseEvent):
        if self.getv("hyperlink_mouse_hover_show_tooltip_enabled"):
            cursor = self.txt_box.cursorForPosition(e.pos())
            hyperlink_text = self._get_hyperlink_for_position(cursor.position())
            if hyperlink_text:
                styled_text = [f"<span>{x}</span><br>" if x != "#1" else "#1" for x in self.getl("block_body_txt_box_hyperlink_tooltip").split("\n")]
                styled_text = "".join(styled_text)
                styled_text = '<span style="color: #aaff7f;"' + styled_text[5:]
                tt_txt = styled_text.replace("#1", f'<span style="color: #aaffff; text-decoration: underline">{hyperlink_text}</span>')
                # Add definition image if web site is defined
                web_site_name = hyperlink_text
                if web_site_name.find("//") != -1:
                    web_site_name = web_site_name[web_site_name.find("//") + 2:]
                    if web_site_name.startswith(("www.", "ai.", "app.")) and web_site_name.find(".") != -1:
                        web_site_name = web_site_name[web_site_name.find(".") + 1:]
                    web_site_name = web_site_name.split(".")[0].lower()
                    db_def = db_definition_cls.Definition(self._stt)
                    for i in db_def.get_list_of_all_expressions():
                        if i[0] == web_site_name:
                            db_def.load_definition(i[1])
                            if i[0] in db_def.definition_name.lower().replace(" ", "") and db_def.default_media_id:
                                db_media = db_media_cls.Media(self._stt)
                                if db_media.is_media_exist(db_def.default_media_id):
                                    db_media.load_media(db_def.default_media_id)
                                    tt_txt += f'<br><br><img src="{db_media.media_file}" width="300" />'

            else:
                tt_txt = self._txt_box_normal_tooltip
            
            self.txt_box.setToolTip(tt_txt)
        
        if self.getv("hyperlink_mouse_action_enabled"):
            cursor = self.txt_box.cursorForPosition(e.pos())

            view_cur = self.txt_box.viewport().cursor()
            has_hyperlink = False
            for i in self._hyperlink_list:
                if cursor.position() in range(i[0], i[1]):
                    has_hyperlink = True
                    break

            if has_hyperlink:
                view_cur.setShape(Qt.PointingHandCursor)
            else:
                view_cur.setShape(Qt.ArrowCursor)

            self.txt_box.viewport().setCursor(view_cur)

        if self.getv("definition_show_on_mouse_hover"):
            if not self._is_cursor_at_valid_position(e):
                return

            if not self._definition_to_show_in_simple_view:
                cursor = self.txt_box.cursorForPosition(e.pos())
                self._definition_to_show_in_simple_view = []
                has_def_with_spaces = False
                for i in self._text_def_map:
                    if cursor.position() in range(i[2], i[3]):
                        self._definition_to_show_in_simple_view.append(i)
                        if " " in i[1].strip():
                            has_def_with_spaces = True
                if has_def_with_spaces:
                    self._definition_to_show_in_simple_view = [x[0] for x in self._definition_to_show_in_simple_view if " " in x[1].strip()]
                else:
                    self._definition_to_show_in_simple_view = [x[0] for x in self._definition_to_show_in_simple_view]
                
                if len(self._definition_to_show_in_simple_view) == 0:
                    self._check_to_hide_simple_view()
                    return
            
                self._timer.singleShot(self.getv("definition_view_simple_delay"), self._show_simple_def)
                self.show_definition_names_in_titlebar(self._definition_to_show_in_simple_view)

    def show_definition_names_in_titlebar(self, definition_ids: list):
        if not self.getv("block_definition_titlebar_msg_enabled") or not isinstance(self.txt_box, block_widgets_cls.TextBox) or not definition_ids:
            return
        
        db_def = db_definition_cls.Definition(self._stt)
        for def_id in definition_ids:
            db_def.load_definition(def_id)
            detail_dict = {
                "type": "show",
                "name": f"definition {def_id}",
                "text": db_def.definition_name,
                "duration": self.getv("block_definition_titlebar_msg_duration"),
                "id": self.txt_box._active_record_id
            }
            self.txt_box.block_event(self.txt_box._my_name, "titlebar_msg", detail=detail_dict)

    def _is_cursor_at_valid_position(self, e: QtGui.QMouseEvent) -> bool:
        cursor = self.txt_box.cursorForPosition(e.pos())
        pos = cursor.position()
        txt = self.txt_box.toPlainText()

        if not txt:
            return False
        
        if pos == 0 or pos == len(txt):
            return False
        
        if txt[pos-1:pos] == "\n":
            return False
        
        return True

    def hide_definition_simple_view(self, definition_id: int = None):
        self._timer.stop()
        self._simple_def_view.hide_me(definition_id)

    def _check_to_hide_simple_view(self):
        # If SimpleView is in drag mode, do nothing
        if self._simple_def_view.drag_mode:
            self._timer_to_hide.singleShot(1000, self._check_to_hide_simple_view)
            return
        
        # Define cursor position in text and cursor relative position in box
        cursor = self.txt_box.cursorForPosition(self.txt_box.mapFromGlobal(QCursor.pos()))
        c_pos = self.txt_box.mapFromGlobal(QCursor.pos())
        
        # If SimpleBox is not visble return        
        if not self._simple_def_view._definition_ids:
            return

        for shown_def in self._simple_def_view._definition_ids:
            # Set variable to determinate will SimpleBox be hidden
            def_hide = True

            # Check is cursor still on definition word
            for i in self._text_def_map:
                if cursor.position() in range(i[2], i[3]):
                    if i[0] == shown_def:
                        def_hide = False
                        break

            # Check is cursor outside of txtbox, if true set def_hide to True
            if not def_hide:
                if c_pos.x() < 1 or c_pos.x() > self.txt_box.width() -1 or c_pos.y() < 1 or c_pos.y() > self.txt_box.height() -1:
                    def_hide = True

            # Check is cursor on SimpleView window, if true dont hide
            if def_hide:
                simple_view_pos = self._simple_def_view.get_mapToGlobal(shown_def)
                x = simple_view_pos.x()
                y = simple_view_pos.y()
                x1 = x + self._simple_def_view.get_width(shown_def)
                y1 = y + self._simple_def_view.get_height(shown_def)
                if QCursor.pos().x() > x and QCursor.pos().x() < x1 and QCursor.pos().y() > y and QCursor.pos().y() < y1:
                    def_hide = False

            # Hide definition if def_hide is true
            if def_hide:
                self.hide_definition_simple_view(shown_def)
        
        if self._simple_def_view._definition_ids:
            self._timer_to_hide.singleShot(1000, self._check_to_hide_simple_view)

    def _show_simple_def(self):
        if not self._definition_to_show_in_simple_view:
            self._timer.stop()
            return
        glob_pos = QCursor().pos()
        e = self.txt_box.mapFromGlobal(glob_pos)
        cursor = self.txt_box.cursorForPosition(e)
        definition_id = []
        has_def_with_spaces = False
        for i in self._text_def_map:
            if cursor.position() in range(i[2], i[3]):
                definition_id.append(i)
                if " " in i[1].strip():
                    has_def_with_spaces = True
        
        # Try to reduce number of showed definitions
        if has_def_with_spaces:
            definition_id = [x[0] for x in definition_id if " " in x[1].strip()]
        else:
            definition_id = [x[0] for x in definition_id]

        if not definition_id:
            self._definition_to_show_in_simple_view = []
            self._timer.stop()
            return

        if self._definition_to_show_in_simple_view == definition_id and self.txt_box.toPlainText():
            self._simple_def_view.show_me(definition_id, glob_pos)
        else:
            self._check_to_hide_simple_view()

        self._definition_to_show_in_simple_view = []
        self._timer.stop()
        self._timer_to_hide.singleShot(1000, self._check_to_hide_simple_view)

    def return_pressed(self) -> bool:
        txt = self.txt_box.toPlainText()
        if self._list_mode:
            txt += "\n" + self.getv("text_handler_list_string")
            self._set_text_and_pos_at_end(txt)
            return True
            
        command = self._check_is_command_typed()
        if command == "list":
            self._list_mode = True
            return True
        if command == "calculator":
            self._calc_start(return_pressed=True)
            return True
        if self._calc_mode:
            self._calc_start(return_pressed=True)
            return True
        if command:
            return True

    def escape_pressed(self):
        txt = self.txt_box.toPlainText()
        pos = txt.rfind(self.getv("text_handler_list_string"))
        if pos >= 0 :
            if txt[pos + len(self.getv("text_handler_list_string")):].strip() == "":
                txt = txt[:pos + len(self.getv("text_handler_list_string"))]

        if self._list_mode:
            self._list_mode = False
            if len(txt) >= len(self.getv("text_handler_list_string")):
                if txt[0 - len(self.getv("text_handler_list_string")):] == self.getv("text_handler_list_string"):
                    txt = txt[:0 - len(self.getv("text_handler_list_string"))]
                    self._set_text_and_pos_at_end(txt)
        if self._calc_mode:
            self._calc_stop()

        self._definition_hint.setVisible(False)

    def definition_hint(self, duration: int, record_id: int):
        if not self.getv("definition_hint_enabled") or not self.getv("definition_text_mark_enabled"):
            return
        cur = self.txt_box.textCursor()
        cur_rect = self.txt_box.cursorRect(cur)
        cur_pos = cur_rect.topLeft()
        global_pos = self.txt_box.mapToGlobal(cur_pos)
        pos = self._main_win.mapFromGlobal(global_pos)
        self._definition_hint.handle_text_event(self.txt_box.toPlainText(), pos, self.txt_box.textCursor().position(), duration, record_id=record_id)
        self.txt_box.setFocus()

    def _calculator_mode(self, value: bool):
        if not isinstance(self.txt_box, block_widgets_cls.TextBox):
            return
        
        if value:
            if self.txt_box._active_record_id not in self.get_appv("calculator"):
                self.get_appv("calculator").append(self.txt_box._active_record_id)
        else:
            if self.txt_box._active_record_id in self.get_appv("calculator"):
                self.get_appv("calculator").pop(self.get_appv("calculator").index(self.txt_box._active_record_id))

    def _calc_start(self, return_pressed: bool = False):
        detail_dict = {
            "type": "show",
            "name": "calc_mode",
            "text": self.getl("block_calc_mode_msg"),
            "duration": self.getv("block_calc_mode_titlebar_msg_duration"),
            "id": self.txt_box._active_record_id
        }
        if self.getv("block_calc_mode_titlebar_msg_enabled"):
            self.txt_box.block_event("text_handler", "titlebar_msg", detail=detail_dict)

        if not self._calc_mode:
            self._calc_mode = True
            cur = self.txt_box.textCursor()
            cur.setPosition(len(self.txt_box.toPlainText()) - len(self.txt_box.toPlainText().split("\n")[-1]))
            cur.movePosition(cur.Right, cur.KeepAnchor, len(self.txt_box.toPlainText().split("\n")[-1]))
            cur.removeSelectedText()
            cf = QTextCharFormat()
            
            cf.setBackground(QColor("#00007f"))
            cf.setForeground(QColor("#aaff00"))
            cur.setCharFormat(cf)
            cur.insertText(self.getl("calculator_mode_title"))
            
            cf.setForeground(QColor("#c7c7c7"))
            cur.setCharFormat(cf)
            cur.insertText(f'   {self.getl("calculator_mode_text")}\n')
            
            cf.setBackground(self._real_char_format.background())
            cf.setForeground(QColor("#55ff7f"))
            font_size = cur.charFormat().font().pointSize()
            font = cur.charFormat().font()
            font.setPointSize(10)
            cf.setFont(font)
            cur.setCharFormat(cf)
            cur.insertText(self.getl("calculator_mode_help_text") + "\n")

            cur.setCharFormat(self._real_char_format)
            self.txt_box.setTextCursor(cur)
            self._calculator_mode(True)
            return
        
        txt = self.txt_box.toPlainText()
        if txt and txt[-1] == "=":
            return_pressed = True
        
        txt_list = txt.split("\n")
        last_line = txt_list[-1]
        
        allowed_chars = "1234567890.+-/*()%<> ="
        if not return_pressed:
            self._calculator_mode(False)
            cur = self.txt_box.textCursor()

            if last_line.find("=") == -1:
                if len(last_line) == 1:
                    cur_pos = cur.position()
                    cur.setPosition(len(txt) - len(txt_list[-1]))
                    cur.movePosition(cur.Right, cur.KeepAnchor, len(txt_list[-1]))
                    cur.setCharFormat(self._real_char_format)
                    cur.insertText(last_line)
                    cur.setPosition(cur_pos)
                    self.txt_box.setTextCursor(cur)
                self._calculator_mode(True)
                return
            
            cur_pos = cur.position()
            cur.setPosition(len(txt) - len(txt_list[-1]))
            cur.movePosition(cur.Right, cur.KeepAnchor, len(txt_list[-1]))
            new_last_line = last_line[:last_line.find("=")].rstrip()
            cur.setCharFormat(self._real_char_format)
            cur.insertText(new_last_line)
            if cur_pos > len(txt) - (len(last_line) - len(new_last_line)):
                cur_pos = len(txt) - (len(last_line) - len(new_last_line))
            cur.setPosition(cur_pos)
            self.txt_box.setTextCursor(cur)

            self._calculator_mode(True)
            self.txt_box.ac.hide_ac()
            return
        
        self._calculator_mode(False)
        
        if last_line.find("=") >= 0:
            last_line = last_line[:last_line.find("=")].strip()
        new_last_line = last_line
        # for i in last_line:
        #     if i in allowed_chars:
        #         new_last_line += i
        
        result = self._calc_result(new_last_line)
        
        self.get_appv("clipboard").setText(result)

        new_last_line += f"  = {result} "
        cur = self.txt_box.textCursor()
        cur.setPosition(len(txt) - len(txt_list[-1]))
        cur.movePosition(cur.Right, cur.KeepAnchor, len(txt_list[-1]))
        cur.setCharFormat(self._real_char_format)
        cur.insertText(new_last_line[:new_last_line.find("=") - 1])

        cf = QTextCharFormat()
        cf.setBackground(QColor("#005500"))
        cf.setForeground(QColor("#ffff00"))
        cur.setCharFormat(cf)
        cur.insertText(new_last_line[new_last_line.find("=") - 1:])

        cur.setCharFormat(self._real_char_format)

        self.txt_box.setTextCursor(cur)
        self._calculator_mode(True)
        self.txt_box.ac.hide_ac()
        
    def _calc_result(self, expression: str) -> str:
        result = ""
        try:
            result = str(eval(expression))
        except:
            result = self.getl("error_text")
        
        return result

    def _calc_stop(self):
        detail_dict = {
            "type": "show",
            "name": "calc_mode",
            "text": self.getl("block_calc_mode_exit_msg"),
            "duration": self.getv("block_calc_mode_titlebar_msg_duration"),
            "id": self.txt_box._active_record_id
        }
        if self.getv("block_calc_mode_titlebar_msg_enabled"):
            self.txt_box.block_event("text_handler", "titlebar_msg", detail=detail_dict)

        self._calc_mode = False
        self._calculator_mode(False)
        
        txt = self.txt_box.toPlainText()
        txt_list = txt.split("\n")
        new_txt = "\n".join(txt_list[:-3])

        self.txt_box.setText(new_txt)
        cur = self.txt_box.textCursor()
        cur.setPosition(len(new_txt))
        cur.insertText("\n")
        self.txt_box.setTextCursor(cur)

    def _check_is_command_typed(self) -> str:
        txt = self.txt_box.toPlainText()
        txt = txt.rstrip()
        txt_len = len(txt)

        if self.txt_box.textCursor().position() >= txt_len:
            # List (@l)
            if txt_len > 1:
                list_string = self.getv("text_handler_list_string")
                if txt_len == 2:
                    if txt[-2:].lower() == "@l":
                        txt = txt[:-2] + list_string
                        self._set_text_and_pos_at_end(txt)
                        return "list"
                else:
                    if txt[-3:].lower() == "\n@l":
                        txt = txt[:-2] + list_string
                        self._set_text_and_pos_at_end(txt)
                        return "list"
            # List (@list)
            if txt_len > 4:
                list_string = self.getv("text_handler_list_string")
                if txt_len == 5:
                    if txt[-5:].lower() == "@list":
                        txt = txt[:-5] + list_string
                        self._set_text_and_pos_at_end(txt)
                        return "list"
                else:
                    if txt[-6:].lower() == "\n@list":
                        txt = txt[:-5] + list_string
                        self._set_text_and_pos_at_end(txt)
                        return "list"
            # Auto add images
            comm_pool = ["@i", "@img", "@image", "@images", "@pic", "@picture", "@pictures"]
            for comm in comm_pool:
                comm_len = len(comm)
                if self._is_command_typed(comm):
                    txt = txt[:-comm_len]
                    self._set_text_and_pos_at_end(txt)
                    self.txt_box.block_event("body_txt_box", "auto_add_images")
                    return "auto_add_images"
            # Calculator 
            comm_pool = ["@c", "@calc", "@calculator"]
            for comm in comm_pool:
                comm_len = len(comm)
                if self._is_command_typed(comm):
                    txt = txt[:-comm_len]
                    self._set_text_and_pos_at_end(txt)
                    self.txt_box.block_event("body_txt_box", "calculator")
                    return "calculator"
            # Add tags
            tags = self._check_is_tags_add_command()
            if tags is True:
                return "tags_no_data"
            elif tags:
                self.txt_box.block_event("body_txt_box", "tag_hint", {"tag_hints": tags})
                return "tags"

            return False
    
    def _check_is_tags_add_command(self) -> list | None:
        txt = self.txt_box.toPlainText()
        txt = txt.rstrip()

        if not txt:
            return None
        
        last_line_break = txt.rfind("\n")

        last_line = txt[last_line_break + 1:]
        if not last_line.startswith("@@"):
            return None
        
        tags = last_line[2:].strip()

        txt = txt[:-len(last_line)]
        self._set_text_and_pos_at_end(txt)

        if not tags:
            return True

        if tags.find(",") != -1:
            tag_list = [x.strip() for x in tags.split(",")]
        else:
            tag_list = [x.strip() for x in tags.split(" ")]
        
        return tag_list

    def _is_command_typed(self, command: str) -> bool:
        txt = self.txt_box.toPlainText()
        txt = txt.rstrip()
        txt_len = len(txt)
        comm_len = len(command)

        if txt_len >= comm_len:
            if txt_len == comm_len:
                if txt[-comm_len:].lower() == command:
                    txt = txt[:-comm_len]
                    return True
            else:
                if txt[-comm_len - 1:].lower() == f"\n{command}":
                    txt = txt[:-comm_len]
                    return True
        return False

    def _set_text_and_pos_at_end(self, txt: str):
        self.txt_box.setText(txt)
        self.check_definitions()
        cur = self.txt_box.textCursor()
        cur.setPosition(len(self.txt_box.toPlainText()))
        self.txt_box.setTextCursor(cur)

    def close_me(self):
        self.get_appv("cm").remove_all_context_menu()

        if self._simple_def_view:
            self._simple_def_view.close_me()
        self._simple_def_view = None
        if self._timer:
            self._timer.stop()
        self._timer = None
        if self._timer_to_hide:
            self._timer_to_hide.stop()
        self._timer_to_hide = None
        if self._definition_hint:
            self._definition_hint.close_me()
        self._definition_hint = None

        UTILS.LogHandler.add_log_record("#1: Engine stopped.", ["TextHandler"])


class DefinitonHint(QFrame):
    ACCURACY_PERCENT = 80
    NUMBER_OF_DEFINITIONS = 6

    def __init__(self, settings: settings_cls.Settings, parent_widget, widget_handler: qwidgets_util_cls.WidgetHandler = None):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self._previous_text = None

        # Load GUI
        uic.loadUi(self.getv("definition_hint_ui_file_path"), self)

        # Define other variables
        self.widget_handler = widget_handler
        self._dont_close_me = False
        self._parent_widget = parent_widget
        self._active_record_id = None
        self.hint_result = {}
        self.sound_hint_pop_up = UTILS.SoundUtility(self.getv("definition_hint_sound_pop_up"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        self._language = None
        self.data_dict = {}
        self.word = None
        self.text_func = TextFunctions(self._stt)

        self._define_widgets()
        self._setup_widgets_text()
        if self.widget_handler:
            self._setup_widget_handler()

        # Connect events with slots
        self.btn_dont_show.clicked.connect(self.btn_dont_show_click)
        self.btn_open.clicked.connect(self.btn_open_click)
        self.btn_quick_add.clicked.connect(self.btn_quick_add_click)
        self.btn_close.clicked.connect(self.btn_btn_close_click)
        self.btn_settings.clicked.connect(self.btn_settings_click)
        self.get_appv("signal").signalNewDefinitionAdded.connect(self.refresh)

        self.refresh()
        self._load_data()

        UTILS.LogHandler.add_log_record("#1: Engine started.", ["DefinitionHint"])

    def _setup_widget_handler(self):
        this_frame: qwidgets_util_cls.Widget_Frame = self.widget_handler.add_QFrame(self)
        this_frame.main_win = self.get_appv("main_win")
        this_frame.properties.window_drag_widgets = [self, self.lbl_title, self.lbl_pic]

        self.widget_handler.add_QPushButton(self.btn_close)
        self.widget_handler.add_QPushButton(self.btn_dont_show)
        self.widget_handler.add_QPushButton(self.btn_open)
        self.widget_handler.add_QPushButton(self.btn_quick_add)
        self.widget_handler.add_QPushButton(self.btn_settings)

        self.widget_handler.activate()

    def btn_settings_click(self):
        utility_cls.DefHintManager(self._stt, self._parent_widget)

    def btn_quick_add_click(self):
        if len(self.hint_result) != 1 or self.word is None:
            return
        
        self.setVisible(False)
        for i in self.hint_result:
            def_id = self.hint_result[i]["id"]
            break
        self._add_expression_to_definition(self.word, def_id)
        self.get_appv("signal").new_definition_added()
        self.setVisible(False)

    def _add_expression_to_definition(self, expression: str, definition_id: int) -> bool:
        db_def = db_definition_cls.Definition(self._stt, definition_id)
        def_syns = db_def.definition_synonyms
        def_syns.append(expression)
        def_dict = {
            "synonyms": def_syns
        }
        result = db_def.update_definition(definition_id, def_dict)
        
        html = utility_cls.TextToHTML(self.getl("def_hint_notif_updated_text"))
        html_rule = utility_cls.TextToHtmlRule("#1", replace_with=db_def.definition_name, fg_color="#00ff00", font_bold=True)
        html.add_rule(html_rule)

        notif_dict = {
            "title": self.getl("def_hint_notif_updated_title"),
            "text": html.get_html(),
            "icon": self.getv("def_updated_icon_path"),
            "timer": 6000,
            "show_close": True
        }
        utility_cls.Notification(self._stt, self._parent_widget, notif_dict)
        if self._active_record_id is not None:
            self.get_appv("signal").block_text_give_focus(self._active_record_id)

    def btn_open_click(self):
        if not self.hint_result:
            return
        elif len(self.hint_result) == 1:
            self.setVisible(False)
            for i in self.hint_result:
                def_id = self.hint_result[i]["id"]
                break
            definition_cls.AddDefinition(self._stt, self._parent_widget, definition_id=def_id)
            return
        
        menu_dict = {
            "position": QCursor.pos(),
            "items": []
        }
        def_ids = []
        for i in self.hint_result:
            def_ids.append(self.hint_result[i]["id"])
        definition_cls.BrowseDefinitions(self._stt, self._parent_widget, definition_id=def_ids)

    def btn_dont_show_click(self):
        if not self.word:
            return
        
        if self.word not in self.data_dict["rejected"]:
            self.data_dict["rejected"].append(self.word)
            self.setVisible(False)
            if self._active_record_id is not None:
                self.get_appv("signal").block_text_give_focus(self._active_record_id)

    def btn_btn_close_click(self):
        self.setVisible(False)
        if self._active_record_id is not None:
            self.get_appv("signal").block_text_give_focus(self._active_record_id)

    def _load_data(self):
        self.data_dict = {}
        self.data_dict["rejected"] = []

        if "definition_hint_data" in self._stt.app_setting_get_list_of_keys():
            self.data_dict = self.get_appv("definition_hint_data")
        else:
            self._stt.app_setting_add("definition_hint_data", self.data_dict, save_to_file=True)

        self._contruct_pref_suff()

    def refresh(self):
        if not self.getv("definition_hint_enabled"):
            self.expressions_words = []
            self.expression_table = {}
            return

        method = self.getv("definition_hint_ratio_method")
        db_def = db_definition_cls.Definition(self._stt)
        defs = db_def.get_list_of_all_definitions()
        table = db_def.get_list_of_all_expressions()
        self.expressions_words = [x[0] for x in table]
        self.expression_table = {}
        pos = 0
        for item in defs:
            def_id = str(item[0])
            if def_id not in self.expression_table:
                self.expression_table[def_id] = {}
                self.expression_table[def_id]["expressions"] = set()
                self.expression_table[def_id]["name"] = item[1]

                if method == 5:
                    name_expr = self.text_func.clear_serbian_chars(item[1])
                    name_expr = name_expr.replace("(", ",").replace(")", ",")
                    self.expression_table[def_id]["expressions"] = [x.strip().lower() for x in name_expr.split(",") if x.strip()]
                    continue

                for i in range(pos, len(table)):
                    if table[i][1] == item[0]:
                        if len(table[i][0]) > 3 and table[i][0].find(" ") == -1:
                            self.expression_table[def_id]["expressions"].add(self.text_func.clear_serbian_chars(table[i][0]).lower())
                    else:
                        pos = i
                        break

    def handle_text_event(self, txt: str, position: QPoint, cursor_position: int, duration: int, record_id: int = None) -> bool:
        self._active_record_id = record_id
        if txt == self._previous_text:
            return
        
        self._previous_text = txt

        if duration > self.getv("definition_hint_typing_delay"):
            self.setVisible(False)
        
        last_word = self._get_last_word(txt, cursor_position)
        if not last_word:
            return False
        
        if len(last_word) < self.getv("definition_hint_minimum_word_lenght"):
            return False

        last_word = last_word.lower()
        
        if last_word in self.expressions_words:
            return False

        if last_word in self.data_dict["rejected"]:
            return False

        if self.get_appv("user").language_name in ["serbian", "croatian", "bosnian"]:
            self._language = "serbian"
        elif self.get_appv("user").language_name == "english":
            self._language = "english"
        else:
            self._language = "other"

        self._calculate_definition_similarity_for_word(last_word)

        if len(self.hint_result) > self.NUMBER_OF_DEFINITIONS:
            return False

        self._show_hint(last_word, position)
        return True

    def _show_hint(self, word: str, position: QPoint) -> None:
        if not self.hint_result:
            return

        for item in self.hint_result:
            self.hint_result[item]["name"] = self.hint_result[item]["name"].title()
        
        self.word = word
        
        def_name = ""

        for item in self.hint_result:
            def_name += f' {self.getl("or_word_text")} "###{self.hint_result[item]["name"]}###"'

        def_name = def_name[len(self.getl("or_word_text")) + 2:]

        txt_to_html = utility_cls.TextToHTML()
        html_rule_word = utility_cls.TextToHtmlRule(
            text="#1",
            replace_with=word,
            fg_color="#00ff00",
            font_bold=True
        )
        txt_to_html.add_rule(html_rule_word)
        for item in self.hint_result:
            rule = utility_cls.TextToHtmlRule(
                text=f'###{self.hint_result[item]["name"]}###',
                replace_with=self.hint_result[item]["name"],
                fg_color="#aaffff",
                font_bold=True
            )
            txt_to_html.add_rule(rule)

        txt_to_html.text = self.getl("definition_hint_lbl_text_text").replace("#2", def_name)

        self.lbl_text.setText(txt_to_html.get_html())

        txt_to_html.text = self.getl("definition_hint_lbl_text_tt").replace("#2", def_name)
        txt_to_html.general_rule.font_size = 20
        for i in txt_to_html.rules:
            i.font_size = 24

        self.lbl_text.setToolTip(txt_to_html.get_html())

        def_name = def_name.replace("###", "")
        if len(self.hint_result) > 1:
            def_name = ""
        btn_text = self.getl("definition_hint_btn_open_text").replace("#2", def_name)
        btn_text = self.text_func.shrink_text(btn_text, self.btn_open.font(), self.btn_open.width() - 40)
        self.btn_open.setText(btn_text)
        self.btn_dont_show.setText(self.getl("definition_hint_btn_dont_show_text").replace("#1", f'"{word}"'))

        if len(self.hint_result) == 1:
            btn_text = self.getl("definition_hint_btn_quick_add_text").replace("#2", def_name)
            btn_text = self.text_func.shrink_text(btn_text, self.btn_quick_add.font(), self.btn_quick_add.width() - 40)
            self.btn_quick_add.setText(btn_text)
            txt_to_html.text = self.getl("definition_hint_btn_quick_add_tt").replace("#2", "###" + def_name.strip('"') + "###")
            self.btn_quick_add.setToolTip(txt_to_html.get_html())
            self.btn_quick_add.setVisible(True)
        else:
            self.btn_quick_add.setVisible(False)

        x = position.x() - 200
        y = position.y() - 130

        if x + self.width() > self._parent_widget.contentsRect().width():
            x = self._parent_widget.contentsRect().width() - self.width()
        if x < 0:
            x = 0
        if y + self.height() > self._parent_widget.contentsRect().height():
            x = self._parent_widget.contentsRect().height() - self.height()
        if y < 0:
            y = 0
        
        self.move(x, y)
        self.setVisible(True)
        self.sound_hint_pop_up.play()
        UTILS.LogHandler.add_log_record("#1: Frame displayed.", ["DefinitionHint"])

    def _calculate_definition_similarity_for_word(self, word: str) -> int:
        accuracy = self.ACCURACY_PERCENT
        word = self.text_func.clear_serbian_chars(word).lower()
        striped_words = self._strip_pref_suff_from_word(word)
        
        time_perf = time.perf_counter()
        self.hint_result = {}
        hint_result_custom = {}
        hint_result_diff = {}
        count = 0
        for i in self.expression_table:
            hint_diff_found = False
            hint_cus_found = False
            for item in self.expression_table[i]["expressions"]:
                count += 1
                if not hint_diff_found:
                    ratio = difflib.SequenceMatcher(None, item, word).ratio() * 100

                    if ratio >= accuracy:
                        hint_diff_found = True
                        hint_result_diff[i] = {
                            "id": int(i),
                            "ratio": ratio,
                            "name": self.expression_table[i]["name"]
                            }
                        # print (f"Found: word: {word} = {item}  Ratio: {ratio}")

                if not hint_cus_found:
                    if self._language == "serbian":
                        ratio = self._get_similarity_ratio_serbian(word, item, striped_words=striped_words)
                    elif self._language == "english":
                        ratio = self._get_similarity_ratio_english(word, item)
                    else:
                        ratio = self._get_similarity_ratio(word, item)

                    if ratio >= accuracy:
                        hint_cus_found = True
                        hint_result_custom[i] = {
                            "id": int(i),
                            "ratio": ratio,
                            "name": self.expression_table[i]["name"]
                            }
                        # print (f"Found: word: {word} = {item}  Ratio: {ratio}")
                        
                
        self.hint_result = self._combine_results(hint_result_diff, hint_result_custom)

        # print (f"RESULTS: Custom: {len(hint_result_custom)}, Diff: {len(hint_result_diff)}  METOD: COMBINED    ", "Time: ", time.perf_counter() - time_perf, "   COUNT: ", count)
        # if time.perf_counter() - time_perf > self.getv("definition_hint_ratio_method_limit_time"):
        #     print (f"Method COMBINED too slow. Records: {count},  Execute time: {time.perf_counter() - time_perf}", end="")

    def _combine_results(self, result1: dict, result2: dict) -> dict:
        result = {}
        res1_list = [[result1[x]["id"], result1[x]["ratio"], result1[x]["name"]] for x in result1]
        res1_list.sort(key=lambda x: x[1], reverse=True)

        res2_list = [[result2[x]["id"], result2[x]["ratio"], result2[x]["name"]] for x in result2]

        if not result1:
            count = 1
            for item in res2_list:
                if str(item[0]) not in result:
                    result[str(item[0])] = {
                                "id": int(item[0]),
                                "ratio": item[1],
                                "name": item[2]
                                }
                    count += 1
                    if count > 5:
                        break
            return result
        if not result2:
            count = 1
            for item in res1_list:
                if str(item[0]) not in result and item[1] > 88:
                    result[str(item[0])] = {
                                "id": int(item[0]),
                                "ratio": item[1],
                                "name": item[2]
                                }
                    count += 1
                    if count > 5:
                        break
            return result

        intersection = [x for x in res1_list if x[1] in [x[1] for x in res2_list]]

        count = 1
        for item in intersection:
            result[str(item[0])] = {
                        "id": int(item[0]),
                        "ratio": item[1],
                        "name": item[2]
                        }
            count += 1
            if count > 5:
                break

        count = len(result)
        if count > 4:
            return result

        for item in res1_list:
            if item[1] > 90 and str(item[0]) not in result:
                result[str(item[0])] = {
                            "id": int(item[0]),
                            "ratio": item[1],
                            "name": item[2]
                            }
                count += 1
                if count > 5:
                    break

        count = len(result)
        if count > 4:
            return result

        for item in res2_list:
            if str(item[0]) not in result:
                result[str(item[0])] = {
                            "id": int(item[0]),
                            "ratio": item[1],
                            "name": item[2]
                            }
                count += 1
                if count > 5:
                    break

        count = len(result)
        if count > 4:
            return result

        return result

    def _strip_pref_suff_from_word(self, word: str) -> list:
        pref_list = self._construct_prefix_list_serbian()
        suff_list = self._construct_suffix_list_serbian()
        pref_list.sort(key=len, reverse=True)
        suff_list.sort(key=len, reverse=True)
        
        word = word.lower()
        striped_words = []

        for pref in pref_list:
            if len(word) <= len(pref):
                continue
            if word[:len(pref)] == pref:
                word = word[len(pref):]
                striped_words.append(word)
                
        for suff in suff_list:
            if len(word) <= len(suff):
                continue
            if word[len(word)-len(suff):] == suff:
                word = word[:len(word)-len(suff):]
                striped_words.append(word)

        return striped_words

    def _get_similarity_ratio(self, word1: str, word2: str) -> int:
        ratio = self._compare_words(word1, word2)
        if ratio:
            return ratio
        ratio = self._compare_words(word2, word1)
        return ratio

    def _get_similarity_ratio_english(self, word1: str, word2: str) -> int:
        suffix_list = [
            "s",
            "es",
            "'s",
            "'em"
        ]

        ratio = self._get_similarity_ratio(word1, word2)
        if ratio:
            return ratio

        for i in suffix_list:
            if word1[:-len(i)] == i:
                ratio = self._compare_words(word1[:-len(i)], word2, modified_word=True)
                if ratio:
                    return ratio

        return ratio

    def _get_similarity_ratio_serbian(self, word1: str, word2: str, striped_words: list) -> int:
        ratio = self._get_similarity_ratio(word1, word2)
        if ratio:
            return ratio
        
        for i in striped_words:
            if i != word1:
                ratio = self._get_similarity_ratio(i, word2)
                if ratio:
                    return ratio

        return ratio
    
    def _construct_prefix_list_serbian(self) -> list:
        return self._prefix_list

    def _construct_suffix_list_serbian(self) -> list:
        return self._suffix_list

    def _contruct_pref_suff(self):
        prefix = """
        bez, bes, za, medju, na, nad, ne, nus, o, po, pod, pra, pred, pri, protiv, protiv-
        raz, sa, su, van, do, za, medju, preko, pro, do, iz, o, pod, pot, pre, uz, auto, auto-,
        sve"""

        prefix_list = [x.strip() for x in prefix.split(",")]
        pref_set = set(prefix_list)
        # if len(prefix_list) != len(pref_set):
        #     print (f'Size diff for prefix: Entered: {len(prefix_list)},  Result: {len(pref_set)}  Difference: {len(prefix_list) - len(pref_set)}')
        
        suffix = """
        nik, r, ac, ak, ar, nik, onja, dzija, lija, kinja, inja, ka, ica, ic, cic,
        cica, nce, ina, cina, tina, urda, ura, iste, liste, ana, ara, nica, onica,
        arnica, injak, ik, etina, ovina, arina, ovaca, stvo, ost, ota, oca, ina, ilo,
        nja, ska, sko, sku, ski, ske, om, ome, ama, omu, omi, im, ima, imi, og, oga,
        ih, iji, ija, ije, ijo, ijom, ijim, ijima, ijem, iju, ijemu, etina, etine, etini,
        etinu, etino, etinom, etinama, icom, icama, tine, tina, tini, tinu, tinom, tinama,
        o, e, a, i, u, ce, ca, cu, cem, cima, ci, etom, etima, ljen, ljenom, ljenome, ljenim,
        ljenih, ljenog, ljenoga"""

        suffix_list = [x.strip() for x in suffix.split(",")]
        suff_set =set(suffix_list)
        # if len(suffix_list) != len(suff_set):
        #     print (f'Size diff for suffix: Entered: {len(suffix_list)},  Result: {len(suff_set)}  Difference: {len(suffix_list) - len(suff_set)}')

        self._prefix_list = list(pref_set)
        self._suffix_list = list(suff_set)

    def _compare_words(self, word1: str, word2: str) -> int:
        ratio = 0
        if len(word1) == 3:
            if word2.find(word1) >= 0:
                if len(word2) in [3, 4]:
                    ratio = 100
        elif len(word1) == 4:
            if word2.find(word1) >= 0:
                if len(word2) in [4, 5, 6]:
                    ratio = 100
        elif len(word1) == 5:
            if word2.find(word1) >= 0:
                if len(word2) in [5, 6, 7]:
                    ratio = 100
        elif len(word1) > 5:
            len_word1 = len(word1)
            if word2.find(word1) >= 0:
                if len(word2) in [len_word1, len_word1 + 1, len_word1 + 2, len_word1 + 3]:
                    ratio = 100
        return ratio

    def _get_last_word(self, txt: str, cursor_position: int = None) -> str:
        if cursor_position is not None:
            txt = txt[:cursor_position]

        if not txt.strip():
            return None
        
        txt = UTILS.TextUtility.replace_special_chars(txt)
        
        if txt[-1] != " ":
            return None
        
        txt = txt[:-1]
        
        words = txt.split(" ")
        last_word = words[-1]

        return last_word

    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     print ("DefHint Unregistred")
    #     # Unregister Dialog
    #     self.dialog_queue.dialog_method_remove_dialog(self.my_name)
    #     return super().closeEvent(a0)

    def close_me(self):
        if self.widget_handler:
            self.widget_handler.remove_child(self)
            self.widget_handler.remove_child(self.btn_close)
            self.widget_handler.remove_child(self.btn_settings)
            self.widget_handler.remove_child(self.btn_quick_add)
            self.widget_handler.remove_child(self.btn_dont_show)
            self.widget_handler.remove_child(self.btn_open)

        self.setVisible(False)
        UTILS.LogHandler.add_log_record("#1: Engine stopped.", ["DefinitionHint"])
        self.close()
        self.deleteLater()
        self.setParent(None)

    def _define_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_text: QLabel = self.findChild(QLabel, "lbl_text")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.btn_open: QPushButton = self.findChild(QPushButton, "btn_open")
        self.btn_dont_show: QPushButton = self.findChild(QPushButton, "btn_dont_show")
        self.btn_quick_add: QPushButton = self.findChild(QPushButton, "btn_quick_add")
        self.btn_settings: QPushButton = self.findChild(QPushButton, "btn_settings")
        
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_close.setAutoDefault(False)
        self.btn_close.setDefault(False)
        if self.getv(f"definition_hint_btn_close_icon_path"):
            self.btn_close.setIcon(QIcon(self.getv("definition_hint_btn_close_icon_path")))
        self.btn_close.setFlat(True)
        self.btn_close.setStyleSheet("QPushButton:hover {background-color: #008f8f; border: 1px solid;}")

        img = QPixmap()
        img.load(self.getv("definition_hint_icon_path"))
        self.lbl_pic.setPixmap(img)
        self.lbl_pic.setScaledContents(True)

        self.setVisible(False)

    def _setup_widgets_text(self):
        self.lbl_title.setText(self.getl("definition_hint_lbl_title_text"))
        self.lbl_title.setToolTip(self.getl("definition_hint_lbl_title_tt"))

        self.lbl_text.setText(self.getl("definition_hint_lbl_text_text"))
        self.lbl_text.setToolTip(self.getl("definition_hint_lbl_text_tt"))

        self.btn_open.setText(self.getl("definition_hint_btn_open_text"))
        self.btn_open.setToolTip(self.getl("definition_hint_btn_open_tt"))

        self.btn_dont_show.setText(self.getl("definition_hint_btn_dont_show_text"))
        self.btn_dont_show.setToolTip(self.getl("definition_hint_btn_dont_show_tt"))

        self.btn_quick_add.setText(self.getl("definition_hint_btn_quick_add_text"))
        self.btn_quick_add.setToolTip(self.getl("definition_hint_btn_quick_add_tt"))


class TextFunctions():
    def __init__(self, settings: settings_cls.Settings, text: str = None, text_box: QTextEdit = None) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define other variables
        self.txt_box = text_box
        self.text = text

    def clear_serbian_chars(self, text: str = None) -> str:
        """
        Replace Serbian-specific Latin characters with equivalent ASCII characters.

        Parameters:
            text (str): The input text to replace characters in. Defaults to 
                        class text attribute if not provided.
                        
        Returns: 
            str: The text with Serbian characters converted to ASCII equivalents.

        This converts the following:

        - ć -> c
        - č -> c  
        - š -> s
        - ž -> z
        - đ -> dj

        And the uppercase versions:

        - Ć -> C
        - Č -> C
        - Š -> S 
        - Ž -> Z
        - Đ -> Dj

        It loops through each replacement pair and uses str.replace() on the input 
        text. This allows texts with Serbian Latin characters to be converted to plain
        ASCII for compatibility.

        For example:

        text = "Pozdrav đaci!" 

        clear_serbian_chars(text)
        # Returns "Pozdrav djaci!"
        """
        if text is None:
            text = self.text
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

    def replace_from_to(self,
                        text: str,
                        from_string: str,
                        to_string: str,
                        replace_with: str = "",
                        affected_occurrences: list = None,
                        leave_borders: bool = True,
                        preserve_number_of_lines: bool = True) -> str:
        """
        Replace text between two delimiters.

        Parameters:

            text (str): The input text to perform replacements on.

            from_string (str): The starting delimiter string.

            to_string (str): The ending delimiter string.

            replace_with (str): The text to replace matches with. Default is empty string.

            affected_occurrences (list): A list of which matched occurrences (indexed from 1) to replace.
                                        If None, all occurrences are replaced.

            leave_borders (bool): Whether to leave the delimiter strings in the result or remove them.
                                Default True leaves delimiters.

            preserve_number_of_lines (bool): Whether to preserve the original line breaks. 
                                            Default True preserves line breaks.
                                            
        Returns:

            str: The text with replacements made.
            
        This performs a search and replace between two delimiter strings. It searches for from_string, 
        then looks for the next to_string, and replaces the text in between with replace_with.

        It can optionally:

        - Only replace specific numbered occurrences 
        - Remove the delimiter strings from the result
        - Preserve the original multiline structure

        For example:

        text = "Hello <b>world</b>!"

        replace_from_to(text, "<b>", "</b>", "planet")
        # Returns "Hello <b>planet</b>!"

        """

        if isinstance(affected_occurrences, str):
            try:
                affected_occurrences = [int(x) for x in affected_occurrences.split(",") if x != ""]
            except ValueError:
                return text
        
        if not preserve_number_of_lines:
            result = self._replace_from_to_line(
                text=text,
                from_string=from_string,
                to_string=to_string,
                replace_with=replace_with,
                affected_occurrences=affected_occurrences,
                leave_borders=leave_borders
            )
            return result
        
        text_lines = [x for x in text.split("\n")]
        for idx, line in enumerate(text_lines):
            result = self._replace_from_to_line(
                text=line,
                from_string=from_string,
                to_string=to_string,
                replace_with=replace_with,
                affected_occurrences=affected_occurrences,
                leave_borders=leave_borders
            )
            text_lines[idx] = result
        
        result = "\n".join(text_lines)
        return result

    def shrink_text(self,
                    text: str,
                    font: QFont,
                    max_text_width: int,
                    invisible_text: str = ".....",
                    process_line_no: int = None,
                    word_sensitive: bool = True,
                    protect_first_no_until_chars: str = "10",
                    protect_last_no_until_chars: str = "10",
                    if_error_return_none: bool = False) -> str:
        """Shrink text to fit within a max width based on a font.

        Parameters:

            text (str): The input text to shrink

            font (QFont): The font the text will be rendered in

            max_text_width (int): The maximum width in pixels the text can occupy

            invisible_text (str): The string to use to indicate truncated text.  
                                Default '....'
                                
            process_line_no (int): Optional line number to process. If None, all lines are processed.

            word_sensitive (bool): Whether to truncate at word boundaries or character boundaries.
                                Default True for word boundaries.
                                
            protect_first_no_until_chars (int/str): Number of first chars to protect from truncation, 
                                                    or a string to find and protect up to.
                                                    Default 10
                                                    
            protect_last_no_until_chars (int/str): Number of last chars to protect from truncation,
                                                or a string to find and protect from.
                                                Default 10
                                                
            if_error_return_none (bool): Whether to return None if error in processing a line.
                                        Default False continues processing other lines.
                                        
        Returns:
            
            str: The text shrunk to fit max_text_width
            
        This function processes each line of a multiline text to shrink it to fit within a max width.
        It uses QFontMetrics to determine the pixel width of each line rendered in the provided font.

        The protect_first_no_until_chars and protect_last_no_until_chars parameters can accept either
        an integer number of characters to protect, or a string value. If a string is passed:

        - For protect_first_no_until_chars, the first occurrence of the string will be found,
        and all characters from the start of the line up to that string will be protected.

        - For protect_last_no_until_chars, the last occurrence of the string will be found,
        and all characters from that string to the end of the line will be protected.

        This allows protecting text relative to key substrings rather than absolute character counts.

        The rest of the string will be truncated if needed according to the other parameters.

        Any errors processing a line will skip that line unless if_error_return_none is True.

        The shrunk lines are rejoined and returned as a single string.

        """

        text_list = [x for x in text.split("\n")]
        for idx, line in enumerate(text_list):
            if process_line_no is not None:
                if process_line_no != idx:
                    continue

            result = self._shrink_line(
                text=line,
                font=font,
                max_text_width=max_text_width,
                invisible_text=invisible_text,
                word_sensitive=word_sensitive,
                protect_first_no_until_chars=protect_first_no_until_chars,
                protect_last_no_until_chars=protect_last_no_until_chars,
                if_error_return_none=if_error_return_none
            )
            if result is None:
                text_list = None
                break

            text_list[idx] = result
        
        if text_list is None:
            return None
        
        text = "\n".join(text_list)
        return text

    def get_least_common_denominator(self, text: str, no_empty_inputs: bool = True, match_case: bool = False) -> str:
        """
        Get the least common denominator substring from a text.

        Parameters:

            text (str): The input text. Can be multiline.

            no_empty_inputs (bool): If True, empty lines will be ignored. Default is True.

            match_case (bool): If False, text will be converted to lowercase before processing. Default is False.

        Returns:

            str: The longest common substring found in all lines of the text.
                Returns None if no common substring found or text is empty.

        Logic:

        - Split text into lines 
        - Extract non-empty lines if no_empty_inputs is True
        - Convert to lowercase if match_case is False
        - Initialize result to first line 
        - Iterate over remaining lines
            - Find common denominator substring between result and current line
            - Update result with new common denominator
        - Return final result

        So this finds the longest substring that is common across all lines of the input text.
        """
        text_list = self._get_text_list(text, no_empty_items=no_empty_inputs, match_case=match_case)
        
        if not text_list:
            return None
        
        result = text_list[0]

        for item in text_list:
            result = self._get_common_denominator(result, item)
        
        return result

    def get_all_common_denominators(self, text: str, no_empty_inputs: bool = True, match_case: bool = False) -> list:
        """
        Get all common denominator substrings from a text.

        Parameters:

            text (str): The input text. Can be multiline.  

            no_empty_inputs (bool): If True, empty lines will be ignored. Default is True.

            match_case (bool): If False, text will be converted to lowercase before processing. Default is False.

        Returns:

            list: A list of all common substrings sorted alphabetically.
                Returns None if no common substrings found or text is empty.

        Logic:

        - Split text into lines
        - Extract non-empty lines if no_empty_inputs is True  
        - Convert to lowercase if match_case is False
        - Sort lines by length, shortest first
        - Iterate over lines
            - Check if current line is a common substring of remaining lines
            - Find longest common substring between current line and each remaining line
            - Update result set with longest common substring  
        - Return sorted result list

        Finds all common substrings across the text lines, from longest to shortest.
        """

        text_list = self._get_text_list(text, no_empty_items=no_empty_inputs, match_case=match_case)
        text_set = set(text_list)

        if not text_list:
            return None
        
        text_list.sort(key=len)

        for item1 in text_list:
            if item1 not in text_set:
                continue
            text_set.discard(item1)
            
            set_items_to_remove = []
            add_to_set = item1
            for item2 in text_set:
                result = self._get_common_denominator(add_to_set, item2)
                if result:
                    add_to_set = result
                    set_items_to_remove.append(item2)
            for item in set_items_to_remove:
                text_set.discard(item)
            text_set.add(add_to_set)

        result = list(text_set)
        result.sort()
        
        return result

    def get_suffixes_for_base_string(self, base_string: str, match_case: bool = True) -> list:
        text = self.select_whole_lines_from_text_box()
        text_list = [x.strip() for x in text.split("\n") if x.strip() != ""]

        suffs = []
        if not match_case:
            base_string = base_string.lower()
        
        for i in text_list:
            if not match_case:
                i = i.lower()
            if self._get_common_denominator(base_string, i, strict_items_order=True) == base_string:
                item_to_add =i.replace(base_string, "")
                if item_to_add:
                    suffs.append(item_to_add)

        return suffs

    def select_whole_lines_from_text_box(self, txt_box: QTextEdit = None, if_no_selection_select_all: bool = True) -> str:
        if txt_box is None:
            txt_box = self.txt_box
        if txt_box is None:
            return None

        if not txt_box.toPlainText():
            return ""

        txt = txt_box.toPlainText()

        cur = txt_box.textCursor()
        if cur.hasSelection():
            selection_from = cur.selectionStart()
            selection_to = cur.selectionEnd()
        else:
            if if_no_selection_select_all:
                selection_from = 0
                selection_to = len(txt)
            else:
                selection_from = cur.position()
                selection_to = cur.position()
        
        selection_from = self._get_selection_from(txt, selection_from)
        selection_to = self._get_selection_to(txt, selection_to)

        txt = txt[selection_from:selection_to]
        return txt
        
    def _get_selection_from(self, txt: str, cur_position: int) -> int:
        if cur_position == 0:
            return cur_position
        
        pos = txt[:cur_position].rfind("\n")
        if pos == -1:
            pos = 0
        else:
            pos += 1
        return pos

    def _get_selection_to(self, txt: str, cur_position: int) -> int:
        if cur_position == len(txt):
            return cur_position
        
        if txt[cur_position - 1:cur_position] == "\n":
            return cur_position
        
        pos = txt.find("\n", cur_position)
        
        if pos == -1:
            pos = len(txt)
        return pos

    def _get_text_list(self, text: str, no_empty_items: bool = True, strip_items: bool = True, match_case: bool = False) -> list:
        if isinstance(text, str):
            if not match_case:
                text = text.lower()
            if no_empty_items:
                if strip_items:
                    text_list = [x.strip() for x in text.split("\n") if x.strip() != ""]
                else:
                    text_list = [x for x in text.split("\n") if x.strip() != ""]
            else:
                if strip_items:
                    text_list = [x.strip() for x in text.split("\n")]
                else:
                    text_list = [x for x in text.split("\n")]
        elif isinstance(text, list) or isinstance(text, set) or isinstance(text, tuple):
            text_list = []
            for i in text:
                if strip_items:
                    i = i.strip()
                if not match_case:
                    i = i.lower()
                if no_empty_items:
                    if i:
                        text_list.append(i)
                else:
                    text_list.append(i)
        else:
            return None
        return text_list

    def _replace_from_to_line(self,
                        text: str,
                        from_string: str,
                        to_string: str,
                        replace_with: str = "",
                        affected_occurrences: list = None,
                        leave_borders: bool = True
                        ) -> str:

        if not text:
            return text
        
        count = 1
        result = ""
        pos = 0
        while True:
            from_pos = text.find(from_string, pos)
            if from_pos == -1:
                result += text[pos:]
                break
            
            if leave_borders:
                result += text[pos:from_pos + len(from_string)]
            else:
                result += text[pos:from_pos]

            to_pos = text.find(to_string, from_pos + len(from_string))
            if to_pos == -1:
                if leave_borders:
                    result += text[from_pos + len(from_string):]
                else:
                    result += text[from_pos:]
                break

            if affected_occurrences is None:
                result += replace_with
                if leave_borders:
                    result += to_string
            else:
                if count in affected_occurrences:
                    result += replace_with
                    if leave_borders:
                        result += to_string
                else:
                    if leave_borders:
                        result += text[from_pos + len(from_string):to_pos + len(to_string)]
                    else:
                        result += text[from_pos:to_pos + len(to_string)]

            count += 1

            pos = to_pos + len(to_string)
        
        return result

    def _get_common_denominator(self, expression1: str, expression2: str, strict_items_order: bool = False) -> str:
        if strict_items_order:
            base = expression1
            expr = expression2
        else:
            if len(expression1) > len(expression2):
                base = expression2
                expr = expression1
            else:
                base = expression1
                expr = expression2
        
        for i in range(len(base)):
            if base[:len(base) - i] == expr[:len(base) - i]:
                return base[:len(base) - i]

        return ""        

    def _shrink_line(self,
                    text: str,
                    font: QFont,
                    max_text_width: int,
                    invisible_text: str = ".....",
                    word_sensitive: bool = True,
                    protect_first_no_until_chars: str = "5",
                    protect_last_no_until_chars: str = "5",
                    if_error_return_none: bool = False) -> str:
        
        if not text or font is None or len(text) < 2:
            if if_error_return_none:
                return None
            else:
                return text
        
        # Find number of characters to protect from beginning
        if self._value_integer(protect_first_no_until_chars) is not None:
            protect_first_no_until_chars = self._value_integer(protect_first_no_until_chars)
        else:
            if text.find(protect_first_no_until_chars) >= 0:
                protect_first_no_until_chars = text.find(protect_first_no_until_chars) + 1
            else:
                protect_first_no_until_chars = 5

        # Find number of characters to protect from end
        if self._value_integer(protect_last_no_until_chars) is not None:
            protect_last_no_until_chars = self._value_integer(protect_last_no_until_chars)
        else:
            if text.rfind(protect_last_no_until_chars) >= 0:
                protect_last_no_until_chars = len(text) - text.rfind(protect_last_no_until_chars)
            else:
                protect_last_no_until_chars = 5
        
        if protect_first_no_until_chars + protect_last_no_until_chars + len(invisible_text) >= len(text):
            if if_error_return_none:
                return None
            else:
                return text

        text_clear = self._clear_word_end_chars(text)

        fm = QFontMetrics(font)

        # Check if minimum text fits to width
        protect_last_no_until_chars = len(text) - protect_last_no_until_chars
        if word_sensitive:
            protect_first_no_until_chars = text_clear.find(" ", protect_first_no_until_chars)
            protect_last_no_until_chars = text_clear[:protect_last_no_until_chars].rfind(" ")
        
        if protect_first_no_until_chars >= protect_last_no_until_chars or protect_first_no_until_chars == -1 or protect_last_no_until_chars == -1:
            if if_error_return_none:
                return None
            else:
                return text

        result = f"{text[:protect_first_no_until_chars]}{invisible_text}{text[protect_last_no_until_chars:]}"
        if fm.width(result) > max_text_width:
            if if_error_return_none:
                return None
            else:
                return text

        # Find text
        while True:
            try_result = f"{text[:protect_first_no_until_chars]}{invisible_text}{text[protect_last_no_until_chars:]}"
            if fm.width(try_result) > max_text_width:
                break
            if protect_first_no_until_chars == protect_last_no_until_chars:
                result = text
                break
            if word_sensitive:
                protect_first_no_until_chars = text_clear.find(" ", protect_first_no_until_chars + 1)
            else:
                protect_first_no_until_chars += 1
            result = try_result

        return result

    def _value_integer(self, expression: str) -> int:
        try:
            int_val = int(expression)
        except ValueError:
            int_val = None
        return int_val

    def _clear_word_end_chars(self, text: str, replace_with: str = " ") -> str:
        text = UTILS.TextUtility.replace_special_chars(text, replace_with=replace_with)
        return text

    def _prepare_for_whole_words(self, txt: str) -> str:
        repl = """.!?"'|;:></[]{}=-_=)(*&^%$#@~`\t\n\\"""
        for i in repl:
            txt = txt.replace(i, " ")
        txt = " " + txt + " "
        return txt

    def filter_apply(self,
                     filter: str,
                     text: str,
                     partial: bool = False,
                     whole_word: bool = False,
                     match_case: bool = False,
                     similar_percent: int = None,
                     clear_serbian = True) -> bool:
        """
        Checks if a text matches a filter criteria.

        Parameters:
        filter (str): The filter string to check against. Can contain AND/OR/NOT operators.
        text (str): The text to check. 
        partial (bool): Whether to do a partial or full match for AND operator.
        whole_word (bool): Match only complete words.
        match_case (bool): Whether to match case or ignore case.

        Returns: 
        bool: True if text matches filter, False otherwise.

        The filter can contain:
        - AND: Use space between words 
        - OR: Use / between words
        - NOT: Use ! before a word

        Processes filter into items based on operators.
        Checks text against each item with find(), supporting NOT, 
        whole words, partial matches, etc.

        Returns True if all criteria is matched, False otherwise.
        """
        if not match_case:
            filter = filter.lower()
            text = text.lower()
        
        if clear_serbian:
            filter = self.clear_serbian_chars(filter)
            text = self.clear_serbian_chars(text)

        if similar_percent and filter and text:
            ratio = difflib.SequenceMatcher(None, filter, text).ratio() * 100
            if ratio >= similar_percent:
                return True

        if whole_word:
            text = self._prepare_for_whole_words(text)
        filter = filter.strip()

        if filter.find("/") >= 0:
            filter_items = [x.strip() for x in filter.split("/") if x.strip() != ""]
            filter_true = False
            for item in filter_items:
                if item[:1] == "!":
                    if whole_word:
                        item = f" {item[1:]} "
                    else:
                        item = item[1:]
                    if text.find(item) < 0:
                        filter_true = True
                        break
                else:
                    if whole_word:
                        item = f" {item} "
                    if text.find(item) >= 0:
                        filter_true = True
                        break
            return filter_true
        elif filter.find(" ") >= 0:
            filter_items = [x.strip() for x in filter.split(" ") if x.strip() != ""]
            if not partial:
                filter_true = True
                for item in filter_items:
                    if item[:1] == "!":
                        if whole_word:
                            item = f" {item[1:]} "
                        else:
                            item = item[1:]
                        if text.find(item) >= 0:
                            filter_true = False
                            break
                    else:
                        if whole_word:
                            item = f" {item} "
                        if text.find(item) == -1:
                            filter_true = False
                            break
                return filter_true
            else:
                filter_true = False
                for item in filter_items:
                    if item[:1] == "!":
                        if whole_word:
                            item = f" {item[1:]} "
                        else:
                            item = item[1:]
                        if text.find(item) < 0:
                            filter_true = True
                            break
                    else:
                        if whole_word:
                            item = f" {item} "
                        if text.find(item) >= 0:
                            filter_true = True
                            break
                return filter_true
        else:
            if filter[:1] == "!":
                if whole_word:
                    filter = f" {filter[1:]} "
                else:
                    filter = filter[1:]
                if text.find(filter) == -1:
                    return True
                else:
                    return False
            else:
                if whole_word:
                    filter = f" {filter} "
                if text.find(filter) == -1:
                    return False
                else:
                    return True
