from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QVBoxLayout, QWidget, QSpacerItem,
                             QSizePolicy, QListWidget, QFileDialog, QDialog, QLabel, QListWidgetItem,  QLineEdit,
                             QMessageBox, QComboBox,  QProgressBar, QCheckBox, QKeySequenceEdit, QRadioButton,
                             QGroupBox, QGraphicsOpacityEffect, QSpinBox, QColorDialog, QFontDialog, QToolTip)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor, QColor, QMouseEvent, QMovie, QFontMetrics, QPalette
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5 import uic, QtGui, QtCore

from typing import Union, Any
from collections import Counter
import time
import os
import json

import settings_cls
from timer_cls import ContinuousTimer
from timer_cls import SingleShotTimer
import utility_cls
import db_tag_cls
import db_definition_cls
import db_record_cls
import db_record_data_cls
import db_media_cls
import qwidgets_util_cls
import definition_cls
import diary_view_cls
import UTILS
from utils_file import FileInformation
from utils_datetime import Period
from UTILS import TextUtility


class StatisticCommand:
    COMMON_ITEMS_COUNT = 5
    MAX_ITEMS_COUNT = 100

    def __init__(self, settings: settings_cls.Settings, expression: str, data: list, data_type: str = "def") -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.expression = expression
        self.data_type = data_type
        self.data = self._create_data(data)
        self.commands = self._define_commands()

    def _create_data(self, data) -> list:
        result = []
        if self.data_type == "def":
            for item in data:
                item_dict = {
                    "id": item[0],
                    "name": item[1].lower().replace('"', "'"),
                    "desc": item[2].lower().replace('"', "'"),
                    "syn": [x.lower().replace('"', "'") for x in item[3]],
                    "image": item[4]
                }
                result.append(item_dict)
        elif self.data_type == "block":
            pos = 0
            db_data = db_record_data_cls.RecordData(self._stt)
            block_data_list = db_data.get_all_record_data()
            db_files = db_media_cls.Files(self._stt)
            file_ids = [x[0] for x in db_files.get_all_file()]
            db_tag = db_tag_cls.Tag(self._stt)
            tag_ids_and_names = [[x[0], x[1]] for x in db_tag.get_all_tags_translated()]
            for item in data:
                images = []
                files = []
                tags = []

                for data_idx in range(pos, len(block_data_list)):
                    data_item = block_data_list[data_idx]
                    if item[0] == data_item[1]:
                        if data_item[2]:
                            tag_to_append = ""
                            for tag_item in tag_ids_and_names:
                                if tag_item[0] == data_item[2]:
                                    tag_to_append = tag_item[1]
                                    break
                            tags.append(tag_to_append)
                        if data_item[3]:
                            if data_item[3] in file_ids:
                                files.append(data_item[3])
                            else:
                                images.append(data_item[3])
                    else:
                        pos = data_idx
                        break

                item_dict = {
                    "id": item[0],
                    "name": item[1].lower().replace('"', "'"),
                    "date": item[2],
                    "date_int": item[3],
                    "body": item[4].lower().replace('"', "'"),
                    "tag": tags,
                    "image": images,
                    "file": files
                }
                result.append(item_dict)

        return result

    def _add_show_details(self, items: list, field: str) -> list:
        result = []
        for item in items:
            if field == "None":
                text = ""
                if self.data_type == "def":
                    text = f'ID={item["id"]} , {item["name"]}'
                elif self.data_type == "block":
                    text = f'ID={item["id"]} - {item["date"]}'
                    if item["name"]:
                        text += f' - {item["name"]}'
                item["show"] = text
                item["show_extra"] = ""
                result.append(item)
                continue
            if item.get(field) is None:
                item["show"] = ""
                item["show_extra"] = ""
                continue
            if self.data_type == "def":
                text = f'ID={item["id"]} , {item["name"]}'
                item["show"] = text
                text = ""
                if field == "name":
                    text = f'Name LEN={UTILS.TextUtility.number_to_string_formatted(len(item["name"]))} chars'
                elif field == "desc":
                    text = f'Description LEN={UTILS.TextUtility.number_to_string_formatted(len(item["desc"]))} chars'
                elif field == "syn":
                    text = f'Contain {UTILS.TextUtility.number_to_string_formatted(len(item["syn"]))} synonyms'
                elif field == "image":
                    text = f'Contain {UTILS.TextUtility.number_to_string_formatted(len(item["image"]))} images'
                item["show_extra"] = text
            elif self.data_type == "block":
                text = f'ID={item["id"]} - {item["date"]}'
                if item["name"]:
                    text += f' - {item["name"]}'
                item["show"] = text
                text = ""
                if field == "name":
                    text = f'Name LEN={UTILS.TextUtility.number_to_string_formatted(len(item["name"]))} chars'
                elif field == "body":
                    text = f'Body LEN={UTILS.TextUtility.number_to_string_formatted(len(item["body"]))} chars'
                elif field == "tag":
                    text = f'Contain {UTILS.TextUtility.number_to_string_formatted(len(item["tag"]))} tags'
                elif field == "image":
                    text = f'Contain {UTILS.TextUtility.number_to_string_formatted(len(item["image"]))} images'
                elif field == "file":
                    text = f'Contain {UTILS.TextUtility.number_to_string_formatted(len(item["file"]))} files'
                item["show_extra"] = text

            result.append(item)

        return result

    def get_result_dict(self) -> list | None:
        expression = self.expression.lower()

        if not self.expression.strip():
            return None
        
        self._split_if(expression)
        self._find_commands()
        fields_list = self._get_fields()
        
        available_items = []
        for item in self.data:
            eval_result = self._is_if_expression_true(item)
            if isinstance(eval_result, str):
                return eval_result
            if self._is_if_expression_true(item):
                available_items.append(item)
        
        found_count = len(available_items)
        result = []
        # No sorting
        if not fields_list:
            if available_items:
                if self.commands["has_first"]:
                    items = available_items[:self.commands["size"]]
                    items = self._add_show_details(items, "None")
                    result_item = {
                        "title": f"First {self.commands['size']} unsorted items (Found {found_count}):",
                        "items": items
                    }
                    result.append(result_item)

                if self.commands["has_last"]:
                    items = available_items[-self.commands["size"]:][::-1]
                    items = self._add_show_details(items, "None")
                    result_item = {
                        "title": f"Last {self.commands['size']} unsorted items (Found {found_count}):",
                        "items": items
                    }
                    result.append(result_item)
        
        # Name
        if any(x in fields_list for x in self.commands["field_name"]):
            if available_items:
                if available_items[0].get("name") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("name")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "name")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by name length ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("name")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "name")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by name length descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # Date
        if any(x in fields_list for x in self.commands["field_date"]):
            if available_items:
                if available_items[0].get("date") is not None and available_items[0].get("date_int") is not None:
                    field_items = sorted(available_items, key=lambda x: x.get("date_int"))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "date")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by date length ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: x.get("date_int"), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "date")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by date length descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # Body
        if any(x in fields_list for x in self.commands["field_body"]):
            if available_items:
                if available_items[0].get("body") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("body")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "body")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by body length ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("body")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "body")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by body length descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # Description
        if any(x in fields_list for x in self.commands["field_desc"]):
            if available_items:
                if available_items[0].get("desc") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("desc")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "desc")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by description length ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("desc")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "desc")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by description length descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

        # Image
        if any(x in fields_list for x in self.commands["field_image"]):
            if available_items:
                if available_items[0].get("image") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("image")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "image")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by number of images ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("image")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "image")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by number of images descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # File
        if any(x in fields_list for x in self.commands["field_file"]):
            if available_items:
                if available_items[0].get("file") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("file")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "file")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by number of files ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("file")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "file")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by number of files descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # Tag
        if any(x in fields_list for x in self.commands["field_tag"]):
            if available_items:
                if available_items[0].get("tag") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("tag")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "tag")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by number of tags ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("tag")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "tag")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by number of tags descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # ID
        if any(x in fields_list for x in self.commands["field_id"]):
            if available_items:
                if available_items[0].get("id") is not None:
                    field_items = sorted(available_items, key=lambda x: x.get("id"))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "id")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by ID ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: x.get("id"), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "id")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by ID descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)
        
        # Syn
        if any(x in fields_list for x in self.commands["field_syn"]):
            if available_items:
                if available_items[0].get("syn") is not None:
                    field_items = sorted(available_items, key=lambda x: len(x.get("syn")))
                    if self.commands["has_first"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "syn")
                        result_item = {
                            "title": f"First {self.commands['size']} items sorted by number of synonyms ascending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

                    field_items = sorted(available_items, key=lambda x: len(x.get("syn")), reverse=True)
                    if self.commands["has_last"]:
                        items = field_items[:self.commands["size"]]
                        items = self._add_show_details(items, "syn")
                        result_item = {
                            "title": f"Last {self.commands['size']} items sorted by number of synonyms descending (Found {found_count}):",
                            "items": items
                        }
                        result.append(result_item)

        return result

    def _is_if_expression_true(self, item: dict) -> bool | str:
        if not self.commands.get("if_part"):
            return True
        
        if_list = self.parse_expression(self.commands["if_part"])

        for idx, command in enumerate(if_list):
            if command.startswith('"'):
                continue

            original_command = command
            
            # Check parenthesis
            command_split = command.split("(")
            if len(command_split) > 1:
                command_split = command_split[1].split(")")[0]
                if command_split.strip() in self.commands["all_fields"]:
                    command = command_split.strip()

            # Check dot
            command_split = command.split(".")
            if len(command_split) > 1:
                for c in command_split:
                    if c.strip() in self.commands["all_fields"]:
                        command = c.strip()
                        break
            
            # Check bracket
            command_split = command.split("[")
            if len(command_split) > 1:
                for c in command_split:
                    if c.strip() in self.commands["all_fields"]:
                        command = c.strip()
                        break

            if command in self.commands["field_name"]:
                if_list[idx] = original_command.replace(command, f'"""{item.get("name", "")}"""')
                continue

            if command in self.commands["field_date"]:
                if_list[idx] = original_command.replace(command, f'{item.get("date_int", "")}')
                continue

            if command in self.commands["field_body"]:
                if_list[idx] = original_command.replace(command, f'"""{item.get("body", "")}"""')
                continue

            if command in self.commands["field_desc"]:
                if_list[idx] = original_command.replace(command, f'"""{item.get("desc", "")}"""')
                continue

            if command in self.commands["field_image"]:
                if_list[idx] = f'{len(item.get("image", []))}'
                continue

            if command in self.commands["field_file"]:
                if_list[idx] = f'{len(item.get("file", []))}'
                continue

            if command in self.commands["field_syn"]:
                if original_command.startswith("len"):
                    if_list[idx] = f'{len(item.get("syn", []))}'
                else:
                    if_list[idx] = original_command.replace(command, f'"""{" ".join(item.get("syn", ""))}"""')
            
            if command in self.commands["field_tag"]:
                if original_command.startswith("len"):
                    if_list[idx] = f'{len(item.get("tag", []))}'
                else:
                    if_list[idx] = original_command.replace(command, f'"""{" ".join(item.get("tag", ""))}"""')
            
            if original_command in self.commands["field_id"]:
                if_list[idx] = f'{item.get("id", "")}'

        # Check if user entered date
        for idx, expression in enumerate(if_list):
            if expression.startswith('"'):
                # Check if variable is date
                expression = expression.strip('"\'')
                if UTILS.DateTime.DateTime.is_valid(expression):
                    command = UTILS.DateTime.DateTimeObject(expression).DateToInteger
                    if_list[idx] = str(command)

        if_expression = " ".join(if_list)
        if_expression = repr(if_expression)[1:-1]
        
        try:
            result = eval(if_expression)
        except Exception as e:
            result = str(e)

        return result

    def _get_fields(self) -> list:
        commands_list = self.parse_expression(self.commands["head_part"])
        result = []
        for item in commands_list:
            if item in self.commands["field_name"]:
                result.append("name")
            if item in self.commands["field_date"]:
                result.append("date")
            if item in self.commands["field_body"]:
                result.append("body")
            if item in self.commands["field_desc"]:
                result.append("desc")
            if item in self.commands["field_image"]:
                result.append("image")
            if item in self.commands["field_file"]:
                result.append("file")
            if item in self.commands["field_syn"]:
                result.append("syn")
            if item in self.commands["field_tag"]:
                result.append("tag")
            if item in self.commands["field_id"]:
                result.append("id")
        
        return result

    def _find_commands(self) -> None:
        commands_list = self.parse_expression(self.commands["head_part"])

        if not commands_list:
            return None
        
        # First command
        if any(command in self.commands["first"] for command in commands_list):
            self.commands["has_first"] = True
        
        # Last command
        if any(command in self.commands["last"] for command in commands_list):
            self.commands["has_last"] = True

        # Size command
        for command in commands_list:
            size = UTILS.TextUtility.get_integer(command)
            if size:
                if size < 0:
                    size = self.COMMON_ITEMS_COUNT
                if size > self.MAX_ITEMS_COUNT:
                    size = self.MAX_ITEMS_COUNT
                self.commands["size"] = size
        
    def parse_expression(self, expression: str) -> list:
        expression += " "

        result = []
        command = ""
        for idx, char in enumerate(expression):
            if char == " " and expression[:idx].count('"') % 2 == 0:
                if command:
                    result.append(command)
                command = ""
                continue

            command += char

        result = [x.strip() for x in result if x.strip()]
        return result

    def _split_if(self, expression: str) -> None:
        if_part = None
        head_part = None
        for if_kw in self.commands["if"]:
            pos = expression.find(if_kw)
            if pos != -1 and expression[:pos].count('"') % 2 == 0:
                if_part = expression[pos + len(if_kw):].strip()
                head_part = expression[:pos].strip()
                break
        
        if if_part is None:
            self.commands["head_part"] = expression
            return None

        self.commands["has_if"] = True
        self.commands["if_part"] = if_part
        self.commands["head_part"] = head_part

    def _define_commands(self) -> dict:
        result = {
            "first": ["top", "first", "beginning", "begin", "start", "most", "head", "upper"],
            "has_first": None,
            "last": ["bottom", "last", "end", "finish", "tail", "lower"],
            "has_last": None,
            "if": ["if", "while", "where", "for", "case", "with"],
            "has_if": None,
            "size": self.COMMON_ITEMS_COUNT,
            "field_name": ["names", "name", "titles", "title"],
            "field_date": ["dates", "date", "times", "time"],
            "field_body": ["bodies", "body", "contents", "content", "texts", "text"],
            "field_desc": ["descriptions", "description", "desc"],
            "field_image": ["images", "image", "pics", "pic"],
            "field_file": ["files", "file"],
            "field_syn": ["synonyms", "synonym", "syn"],
            "field_tag": ["tags", "tag", "markers", "marker", "mark"],
            "field_id": ["ids", "id"]
        }

        fields = []
        for item in result:
            if item.startswith("field_"):
                fields.append(item)
        result["all_fields"] = []
        for field in fields:
            result["all_fields"].extend(result[field])

        return result


class Statistic(QDialog):
    COLLAPSED_HEIGHT = 50
    WAITING_FOR_DATA = "..."

    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget):
        self._dont_clear_menu = False
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("statistic_ui_file_path"), self)

        # Define variables
        self.parent_widget = parent_widget
        self.is_working = 0
        self.abort_action = False
        self.sound_busy = UTILS.SoundUtility(self.getv("statistic_busy_sound_file_path"), volume=self.getv("volume_value"), muted=self.getv("volume_muted"))
        
        self.log_timer = ContinuousTimer(
            parent=None,
            name="Log Timer",
            interval=1000,
            duration=self.getv("statistic_log_frame_duration"),
            delay=self.getv("statistic_log_frame_delay"),
            function_on_timeout=self.log_timer_timeout,
            function_on_finished=self.log_timer_finished
        )
        
        self.busy_timer = SingleShotTimer(
            parent=None,
            name="Busy Timer",
            duration=1000,
            function_on_finished=self.busy_timer_finished
        )

        self.data = self._get_empty_data_dict()

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_appearance()

        self._load_win_position()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)

        self.keyPressEvent = self._key_press_event

        self.btn_log_close.clicked.connect(self.btn_log_close_clicked)
        self.frm_log.enterEvent = self.frm_log_enter_event
        self.frm_log.leaveEvent = self.frm_log_leave_event

        self.btn_app.clicked.connect(self.btn_app_clicked)
        self.btn_app_kw.clicked.connect(self.btn_app_kw_clicked)
        self.txt_app_kw.returnPressed.connect(self.btn_app_kw_clicked)

        self.btn_img.clicked.connect(self.btn_img_clicked)

        self.btn_file.clicked.connect(self.btn_file_clicked)

        self.btn_block.clicked.connect(self.btn_block_clicked)
        self.btn_block_kw.clicked.connect(self.btn_block_kw_clicked)
        self.txt_block_kw.returnPressed.connect(self.btn_block_kw_clicked)
        self.lbl_block_info_kw.linkActivated.connect(self.lbl_block_info_kw_link_activated)
        self.lbl_block_info_kw.linkHovered.connect(self.lbl_block_info_kw_link_hovered)

        self.btn_def.clicked.connect(self.btn_def_clicked)
        self.btn_def_kw.clicked.connect(self.btn_def_kw_clicked)
        self.txt_def_kw.returnPressed.connect(self.btn_def_kw_clicked)
        self.lbl_def_info_kw.linkActivated.connect(self.lbl_def_info_kw_link_activated)
        self.lbl_def_info_kw.linkHovered.connect(self.lbl_def_info_kw_link_hovered)
        self.lbl_def_info.linkActivated.connect(self.lbl_def_info_kw_link_activated)
        self.lbl_def_info.linkHovered.connect(self.lbl_def_info_kw_link_hovered)

        self.btn_tag.clicked.connect(self.btn_tag_clicked)

        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["Statistic"])

    def log_frame_finished_working(self, success: bool):
        if success:
            self.frm_log.setStyleSheet(self.getv("statistic_frm_log_success_stylesheet"))
        else:
            self.frm_log.setStyleSheet(self.getv("statistic_frm_log_error_stylesheet"))
            self.data = self._get_empty_data_dict()

    def lbl_block_info_kw_link_activated(self, link):
        if link.find(",") != -1:
            ids = link.split(",")
            diary_view_cls.BlockView(self._stt, self.get_appv("main_win"), ids)
            return

        block_id = UTILS.TextUtility.get_integer(link[2:])
        db_block = db_record_cls.Record(self._stt)
        if not db_block.is_valid_record_id(block_id):
            QMessageBox.information(self, self.getl("error_text"), self.getl("statistic_block_info_kw_link_hovered_error"))
            return
        diary_view_cls.BlockView(self._stt, self.get_appv("main_win"), [block_id], auto_open_ids=[block_id])

    def lbl_block_info_kw_link_hovered(self, link):
        if link.find(",") != -1:
            tt_text = "ID:\n" + link
            QToolTip.showText(QCursor.pos(), tt_text)
            return

        block_id = UTILS.TextUtility.get_integer(link[2:])
        if block_id:
            db_block = db_record_cls.Record(self._stt)
            if db_block.is_valid_record_id(block_id):
                db_block.load_record(block_id)
                block_date = db_block.RecordDate
                block_name = db_block.RecordName
                block_body = db_block.RecordBody
                text = self.getl("statistic_block_info_kw_link_hovered").replace("#1", str(block_id)).replace("#2", block_date).replace("#3", block_name).replace("#4", block_body)
            else:
                text = self.getl("statistic_block_info_kw_link_hovered_error")
            QToolTip.showText(QCursor.pos(), text)
    
    def lbl_def_info_kw_link_activated(self, link):
        if link.find(",") != -1:
            ids = link.split(",")
            definition_cls.BrowseDefinitions(self._stt, self.get_appv("main_win"), ids)
            return

        def_id = UTILS.TextUtility.get_integer(link[2:])
        db_def = db_definition_cls.Definition(self._stt)
        if not db_def.load_definition(def_id):
            QMessageBox.information(self, self.getl("error_text"), self.getl("statistic_def_info_kw_link_hovered_error"))
            return
        definition_cls.BrowseDefinitions(self._stt, self.get_appv("main_win"), [def_id])

    def lbl_def_info_kw_link_hovered(self, link):
        if link.find(",") != -1:
            tt_text = "ID:\n" + link
            QToolTip.showText(QCursor.pos(), tt_text)
            return

        def_id = UTILS.TextUtility.get_integer(link[2:])
        if def_id:
            db_def = db_definition_cls.Definition(self._stt)
            if db_def.load_definition(def_id):
                def_name = db_def.definition_name
                db_image_id = db_def.default_media_id
                image_path = None
                if db_image_id:
                    db_image = db_media_cls.Media(self._stt, db_image_id)
                    image_path = UTILS.FileUtility.get_absolute_path(db_image.media_file)
                
                text = self.getl("statistic_def_info_kw_link_hovered").replace("#1", str(def_id))
                text_html = UTILS.HTMLText.TextToHTML(text)
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text="#2",
                    replace_with=def_name,
                    fg_color="#ffffff",
                    bg_color="#ff0000",
                    font_size=14
                )

                text_html.add_rule(rule)
                tt_text = text_html.get_html()

                if image_path:
                    tt_text += f'<br><img src="{image_path}" width=200>'
            else:
                tt_text = self.getl("statistic_def_info_kw_link_hovered_error")

            QToolTip.showText(QCursor.pos(), tt_text)

    def btn_log_close_clicked(self):
        self.log_timer.stop()
        self.frm_log.setVisible(False)

    def frm_log_enter_event(self, event: QMouseEvent):
        self.log_timer.stop()
        self.btn_log_close.setText(self.getl("close"))

    def frm_log_leave_event(self, event: QMouseEvent):
        if not self.is_working:
            self.log_timer.start()

    def log_timer_timeout(self, timer: ContinuousTimer):
        remaining_time = round(timer.get_total_remaining_time() / 1000)
        self.btn_log_close.setText(self.getl("close") + f"({remaining_time})")
    
    def log_timer_finished(self, timer: ContinuousTimer):
        self.hide_log_messages()

    def show_log_messages(self):
        if not self.getv("statistic_log_frame_enabled"):
            return
        self.frm_log.setVisible(True)
        self.btn_log_close.setText(self.getl("close"))
        self.frm_log.raise_()
        self.frm_log.setStyleSheet(self.getv("statistic_frm_log_stylesheet"))

    def hide_log_messages(self):
        self.log_timer.stop()
        self.frm_log.setVisible(False)

    def update_log_frame(self, message: str, arguments: Union[str, list] = None, fg_color: str = "#a4d3ff", update_log_text: bool = True, start_new_line: bool = True, reset_log_text: bool = False):
        if reset_log_text:
            self.data["log"]["text"] = ""

        if isinstance(arguments, str):
            arguments = [arguments]

        if not arguments:
            arguments = []
        
        text = ""
        if start_new_line:
            text += "\n"
        
        text_html = UTILS.HTMLText.TextToHTML()
        text_html.general_rule.fg_color = fg_color
        text_html.general_rule.font_family = "Comic Sans MS"
        text_html.general_rule.font_size = 11

        text += message

        for index, argument in enumerate(arguments):
            argument = str(argument)
            rule = UTILS.HTMLText.TextToHtmlRule(
                text=f"#{index + 1}",
                replace_with=argument,
                fg_color="#00ffff"
            )

            text_html.add_rule(rule)

        text_html.set_text(text)

        self.lbl_log.setText(self.data["log"]["text"] + text_html.get_html())
        
        if update_log_text:
            self.data["log"]["text"] += text_html.get_html()
        
        line_width = 0
        fm = QFontMetrics(QFont(text_html.general_rule.font_family, text_html.general_rule.font_size))

        for line in self.lbl_log.text().split("<br>"):
            line = UTILS.TextUtility.get_raw_text_from_html(line)
            line_width = max(line_width, fm.width(line))
        
        line_width += 10
        line_width = max(line_width, self.btn_log_close.width() + 20)

        self.lbl_log.setFixedWidth(max(self.lbl_log.width(), line_width))
        self.lbl_log.adjustSize()

        self.frm_log.resize(self.lbl_log.width() + 20, self.lbl_log.height() + 50)
        self.btn_log_close.move(self.frm_log.width() - (self.btn_log_close.width() + 10), 10)

        x = self.contentsRect().width() - (self.frm_log.width() + 10)
        y = self.contentsRect().height() - (self.frm_log.height() + 10)
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        self.frm_log.move(x, y)
        QCoreApplication.processEvents()

    def update_info_label(self, info_label: QLabel, message: str, arguments: Union[str, list] = None, fg_color: str = "#00ff00", start_new_line: bool = True, reset_label_text: bool = False, link_message: str = None):
        if reset_label_text:
            self.data["info"][info_label.objectName()] = ""
            info_label.setText("")

        if isinstance(arguments, str) or isinstance(arguments, int) or isinstance(arguments, float):
            arguments = [arguments]
        
        if not arguments:
            arguments = []
        
        text = ""
        if start_new_line:
            text += "\n"
        
        text_html = UTILS.HTMLText.TextToHTML()
        text_html.general_rule.fg_color = fg_color
        if link_message:
            text_html.general_rule.link_href = link_message

        text += message

        # Find link in message
        if info_label.objectName() in ["lbl_def_info_kw", "lbl_block_info_kw", "lbl_def_info", "lbl_block_info"]:
            link = None
            if message.find("ID=") != -1:
                link = message.split("ID=")
                if len(link) > 1:
                    link = link[1].split(" ")
                    if len(link) > 0:
                        link = link[0]
                    else:
                        link = None
                else:
                    link = None
                if link and UTILS.TextUtility.is_integer_possible(link):
                    if info_label.objectName() in ["lbl_def_info_kw", "lbl_def_info"]:
                        db_def = db_definition_cls.Definition(self._stt)
                        if db_def.load_definition(UTILS.TextUtility.get_integer(link)):
                            link = "D:" + str(UTILS.TextUtility.get_integer(link))
                    elif info_label.objectName() in ["lbl_block_info_kw", "lbl_block_info"]:
                        db_block = db_record_cls.Record(self._stt)
                        if db_block.is_valid_record_id(UTILS.TextUtility.get_integer(link)):
                            link = "B:" + str(UTILS.TextUtility.get_integer(link))
                    else:
                        link = None
                else:
                    link = None
                if link:
                    text_html.general_rule.link_href = link

        for index, argument in enumerate(arguments):
            argument = str(argument)
            rule = UTILS.HTMLText.TextToHtmlRule(
                text=f"#{index + 1}",
                replace_with=argument,
                fg_color="#00ffff"
            )

            # Find link in arguments
            if info_label.objectName() in ["lbl_def_info_kw", "lbl_block_info_kw", "lbl_def_info", "lbl_block_info"]:
                link = None
                if argument.find("ID=") != -1:
                    link = argument.split("ID=")
                    if len(link) > 1:
                        link = link[1].split(" ")
                        if len(link) > 0:
                            link = link[0]
                        else:
                            link = None
                    else:
                        link = None
                    if link and UTILS.TextUtility.is_integer_possible(link):
                        if info_label.objectName() in ["lbl_def_info_kw", "lbl_def_info"]:
                            db_def = db_definition_cls.Definition(self._stt)
                            if db_def.load_definition(UTILS.TextUtility.get_integer(link)):
                                link = "D:" + str(UTILS.TextUtility.get_integer(link))
                        elif info_label.objectName() in ["lbl_block_info_kw", "lbl_block_info"]:
                            db_block = db_record_cls.Record(self._stt)
                            if db_block.is_valid_record_id(UTILS.TextUtility.get_integer(link)):
                                link = "B:" + str(UTILS.TextUtility.get_integer(link))
                        else:
                            link = None
                    else:
                        link = None
                    if link:
                        rule.link_href = link

            text_html.add_rule(rule)

        text_html.set_text(text)

        self.data["info"][info_label.objectName()] += text_html.get_html()

        info_label.setText(self.data["info"][info_label.objectName()])

        for index in range(self.area_widget_layout.count()):
            item = self.area_widget_layout.itemAt(index).widget()
            
            frame_name = info_label.objectName().replace("lbl_", "frm_").replace("_info", "")

            if isinstance(item, QFrame):
                if item.objectName() == frame_name or item.objectName() + "_kw" == frame_name:
                    self.resize_section_frame(item)
                    break
        else:
            UTILS.LogHandler.add_log_record("#1: Frame for label #2 was not found!", ["Statistic", info_label.objectName()], exception_raised=True)
        
        # QCoreApplication.processEvents()

    def btn_app_kw_clicked(self):
        expression = self.txt_app_kw.text()

        if not expression or self.data["app"]["files"] is None:
            self.update_info_label(self.lbl_app_info_kw, "", start_new_line=False, reset_label_text=True)
            return
        
        UTILS.LogHandler.add_log_record("#1: About to search #2 statistics.\nExpression: #3", ["Statistic", "application", expression])
        if not expression:
            UTILS.LogHandler.add_log_record("#1: Search #2 statistics canceled, expression is empty", ["Statistic", "application"])

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_app.setCursor(Qt.BusyCursor)
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), expression, fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_app_kw_label()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), expression, fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Search for #2 statistics on expression #3 displayed.", ["Statistic", "application", expression])
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_app.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_app_kw_label(self):
        # Collecting data
        self.update_log_frame(self.getl("statistic_log_app_search_collecting_data"))
        
        expression = self.txt_app_kw.text().lower()
        data = {
            "files": [],
            "file_contents": []
        }

        count = 0
        step = int(len(self.data["app"]["files"]) / 20) if int(len(self.data["app"]["files"]) / 20) > 0 else 1
        for count, file in enumerate(self.data["app"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            
            if expression in file.get_base_filename().lower():
                data["files"].append(file)
            
            if expression in file.get_file_content().lower():
                data["file_contents"].append(file)

            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)

        if len(self.data['app']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        
        self.update_log_frame(self.getl("statistic_log_search_preparing_data"))

        # Displaying data
        if data["files"]:
            self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_files_title"), fg_color="#ffff00", start_new_line=False, reset_label_text=True)
            count = 1
            remaining_files = 0
            for file in data["files"]:
                if self.abort_action:
                    return False
                
                if count == 4 and len(data["files"]) > 4:
                    remaining_files = len(data["files"]) - 3
                    break
                
                file_name = file.get_base_filename()
                file_size = file.size(return_formatted_string=True)
                file_created_dt = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f" {self.getl('at')} ")
                file_created = self.getl(f"week_day{file_created_dt.DayOfWeek + 1}")
                file_created += f", {file_created_dt.DATE_TIME_formatted_string}"
                file_created_before = self._period_before_formatted_string(file.created_before_period())
                file_lines = TextUtility.number_to_string_formatted(file.file_content_count_lines(), decimals=0)
                file_words = TextUtility.number_to_string_formatted(file.file_content_count_words(), decimals=0)
                file_chars = TextUtility.number_to_string_formatted(file.file_content_count_chars(), decimals=0)
                self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_files"), [count, file_name, file_size, file_created, file_created_before, file_lines, file_words, file_chars])
                count += 1

            if remaining_files > 0:
                self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_files_remaining"), [remaining_files])

        expression_count = []
        for file in data["file_contents"]:
            if self.abort_action:
                return False
            
            file_content = file.get_file_content()
            expression_count.append([file.get_base_filename(), file.size(return_formatted_string=True), TextUtility.count_expressions(file_content, expression)])
        
        expression_count = sorted(expression_count, key=lambda x: x[2], reverse=True)

        if expression_count:
            if data["files"]:
                self.update_info_label(self.lbl_app_info_kw, "\n" + self.getl("statistic_log_app_search_content_title"), fg_color="#ffff00")
            else:
                self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_content_title"), fg_color="#ffff00", start_new_line=False, reset_label_text=True)

            self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_top_content"))

            for count, item in enumerate(expression_count):
                if self.abort_action:
                    return False
                self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_top_content_item"), [count + 1, item[0], item[1], TextUtility.number_to_string_formatted(item[2], decimals=0)])

                if count == 9:
                    break
        
        if not expression_count and not data["files"]:
            self.update_info_label(self.lbl_app_info_kw, self.getl("statistic_log_app_search_no_content"), [expression], fg_color="#ff5500", start_new_line=False, reset_label_text=True)
        
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)

        return True

    def btn_block_kw_clicked(self):
        expression = self.txt_block_kw.text()

        if not expression or self.data["block"]["blocks"] is None:
            self.update_info_label(self.lbl_block_info_kw, "", start_new_line=False, reset_label_text=True)
            return
        
        UTILS.LogHandler.add_log_record("#1: About to search #2 statistics.\nExpression: #3", ["Statistic", "block", expression])
        if not expression:
            UTILS.LogHandler.add_log_record("#1: Search #2 statistics canceled, expression is empty", ["Statistic", "block"])

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_block.setCursor(Qt.BusyCursor)
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), expression, fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_block_kw_label()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), expression, fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Search for #2 statistics on expression #3 displayed.", ["Statistic", "block", expression])
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_block.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_block_kw_label(self):
        if not self.data["block"]["blocks"]:
            self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_no_data_text"), start_new_line=False, reset_label_text=True)
            return True
        # Collecting data
        self.update_log_frame(self.getl("statistic_log_block_search_collecting_data"))

        self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_search_collecting_data"), fg_color="#ff0000", start_new_line=False, reset_label_text=True)
        QCoreApplication.processEvents()
        commands = StatisticCommand(self._stt, expression=self.txt_block_kw.text(), data=self.data["block"]["blocks"], data_type="block")
        command_list = commands.get_result_dict()

        first_entry = True
        if isinstance(command_list, str):
            text = "Error: " + command_list
            self.update_info_label(self.lbl_block_info_kw, text, fg_color="#ff0000", reset_label_text=True, start_new_line=False)
            return True
        
        if command_list:
            for item in command_list:
                if first_entry:
                    self.update_info_label(self.lbl_block_info_kw, item["title"], fg_color="#ffff00", reset_label_text=True, start_new_line=False)
                    first_entry = False
                else:
                    self.update_info_label(self.lbl_block_info_kw, "\n" + item["title"], fg_color="#ffff00")

                link_message = ""
                for idx, rec in enumerate(item["items"]):
                    self.update_info_label(self.lbl_block_info_kw, f"{idx + 1}.) ", fg_color="#949494")
                    self.update_info_label(self.lbl_block_info_kw, "#1 " + rec.get("show_extra", ""), arguments=rec.get("show", ""), fg_color="#55aa7f", start_new_line=False)
                    link_message += f'{rec.get("id")},'
                
                link_message = link_message.strip(",")
                if link_message.find(",") != -1:
                    self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_search_show_all_blocks"), fg_color="#aaffff", link_message=link_message)

            return True
        
        expression = self.txt_block_kw.text().lower()

        data = {
            "blocks": 0,
            "count": 0,
            "dates": []
        }

        count = 0
        step = int(len(self.data["block"]["blocks"]) / 20) if int(len(self.data["block"]["blocks"]) / 20) > 0 else 1
        for count, block_data in enumerate(self.data["block"]["blocks"]):
            if expression.startswith("!"):
                search_expression = expression[1:]
                if search_expression not in block_data[4].lower():
                    data["blocks"] += 1
                    data["count"] += block_data[4].lower().count(search_expression)
                    if block_data[1]:
                        data["dates"].append([block_data[0], f'ID={block_data[0]} ... {self.getl("date")}: {block_data[2]} - {block_data[1]}'])
                    else:
                        data["dates"].append([block_data[0], f'ID={block_data[0]} ... {self.getl("date")}: {block_data[2]}'])
            else:
                search_expression = expression
                if search_expression in block_data[4].lower():
                    data["blocks"] += 1
                    data["count"] += block_data[4].lower().count(search_expression)
                    if block_data[1]:
                        data["dates"].append([block_data[0], f'ID={block_data[0]} ... {self.getl("date")}: {block_data[2]} - {block_data[1]}'])
                    else:
                        data["dates"].append([block_data[0], f'ID={block_data[0]} ... {self.getl("date")}: {block_data[2]}'])

            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['block']['blocks'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)

        if len(self.data['block']['blocks']):
            self.update_log_frame(f"{count+1}/{len(self.data['block']['blocks'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        
        self.update_log_frame(self.getl("statistic_log_search_preparing_data"))

        # Displaying data
        if data["blocks"]:
            self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_log_block_search_title"), expression, fg_color="#ffff00", start_new_line=False, reset_label_text=True)
            block_count_percent = UTILS.TextUtility.number_to_string_formatted((data["blocks"] / len(self.data["block"]["blocks"])) * 100, decimals=4)
            expression_avg = UTILS.TextUtility.number_to_string_formatted((data["count"] / data["blocks"]), decimals=2)
            if expression.startswith("!"):
                self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_log_block_search_result_not"), [block_count_percent, UTILS.TextUtility.number_to_string_formatted(data["blocks"], decimals=0)])
                self.update_info_label(self.lbl_block_info_kw, "\n" + self.getl("statistic_log_block_search_block_list_title_not"), expression, fg_color="#ffff00")
            else:
                self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_log_block_search_result"), [block_count_percent, UTILS.TextUtility.number_to_string_formatted(data["blocks"], decimals=0), UTILS.TextUtility.number_to_string_formatted(data["count"], decimals=0), expression_avg])
                self.update_info_label(self.lbl_block_info_kw, "\n" + self.getl("statistic_log_block_search_block_list_title"), expression, fg_color="#ffff00")

            for count, item_in_dates in enumerate(data["dates"]):
                item = item_in_dates[1]
                text = f"{count+1}.)  {item}"
                block_tags = 0
                block_media = 0
                if self.data["block"]["media"]:
                    for block in self.data["block"]["media"]:
                        if block[0] == item_in_dates[0]:
                            block_tags += block[1]
                            block_media += block[2]

                    add_info = ""
                    if block_tags:
                        add_info += self.getl("statistic_log_block_search_block_tags").replace("#1", UTILS.TextUtility.number_to_string_formatted(block_tags, decimals=0))
                    if block_media:
                        if add_info:
                            add_info += ", "
                        add_info += self.getl("statistic_log_block_search_block_media").replace("#1", UTILS.TextUtility.number_to_string_formatted(block_media, decimals=0))

                    if add_info:
                        add_info = f" ({add_info})"

                    text += add_info

                self.update_info_label(self.lbl_block_info_kw, text, fg_color="#c4e1ff")
                if count >= 9:
                    break
            if len(data["dates"]) > 10:
                self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_log_block_search_block_more"), len(data["dates"]) - 10, fg_color="#c4e1ff")

        else:
            self.update_info_label(self.lbl_block_info_kw, self.getl("statistic_log_block_search_no_content"), [expression], fg_color="#ff5500", start_new_line=False, reset_label_text=True)
        
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)

        return True

    def btn_def_kw_clicked(self):
        expression = self.txt_def_kw.text()

        if not expression or self.data["def"]["defs"] is None:
            self.update_info_label(self.lbl_def_info_kw, "", start_new_line=False, reset_label_text=True)
            return
        
        UTILS.LogHandler.add_log_record("#1: About to search #2 statistics.\nExpression: #3", ["Statistic", "definition", expression])
        if not expression:
            UTILS.LogHandler.add_log_record("#1: Search #2 statistics canceled, expression is empty", ["Statistic", "definition"])

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_def.setCursor(Qt.BusyCursor)
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), expression, fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_def_kw_label()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), expression, fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Search for #2 statistics on expression #3 displayed.", ["Statistic", "definition", expression])
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_def.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_def_kw_label(self):
        if not self.data["def"]["defs"]:
            self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_no_data_text"), start_new_line=False, reset_label_text=True)
            return True
        # Collecting data
        self.update_log_frame(self.getl("statistic_log_def_search_collecting_data"))

        self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_search_collecting_data"), fg_color="#ff0000", start_new_line=False, reset_label_text=True)
        QCoreApplication.processEvents()
        commands = StatisticCommand(self._stt, expression=self.txt_def_kw.text(), data=self.data["def"]["defs"], data_type="def")
        command_list = commands.get_result_dict()

        first_entry = True
        if isinstance(command_list, str):
            text = "Error: " + command_list
            self.update_info_label(self.lbl_def_info_kw, text, fg_color="#ff0000", reset_label_text=True, start_new_line=False)
            return True
        
        if command_list:
            for item in command_list:
                if first_entry:
                    self.update_info_label(self.lbl_def_info_kw, item["title"], fg_color="#ffff00", reset_label_text=True, start_new_line=False)
                    first_entry = False
                else:
                    self.update_info_label(self.lbl_def_info_kw, "\n" + item["title"], fg_color="#ffff00")

                link_message = ""
                for idx, rec in enumerate(item["items"]):
                    self.update_info_label(self.lbl_def_info_kw, f"{idx + 1}.) ", fg_color="#949494")
                    self.update_info_label(self.lbl_def_info_kw, "#1 " + rec.get("show_extra", ""), arguments=rec.get("show", ""), fg_color="#55aa7f", start_new_line=False)
                    link_message += f'{rec.get("id")},'

                link_message = link_message.strip(",")
                if link_message.find(",") != -1:
                    self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_search_show_all_defs"), fg_color="#aaffff", link_message=link_message)

            return True
        
        expression = self.txt_def_kw.text().lower()

        data = {
            "syn": [],
            "desc": [],
            "desc_count_total": 0,
            "count_syn": 0,
            "count_desc": 0,
            "whole_syn": []
        }

        if not self.data["def"]["defs"]:
            return False
        
        count = 0
        step = int(len(self.data["def"]["defs"]) / 20) if int(len(self.data["def"]["defs"]) / 20) > 0 else 1
        for def_item in self.data["def"]["defs"]:
            syn_string = " ".join(def_item[3]) if def_item[3] else ""
            syn_string = syn_string.lower()

            if expression.startswith("!"):
                search_expression = expression[1:]
                if search_expression not in syn_string.lower():
                    data["syn"].append([def_item[0], def_item[1], def_item[3], def_item[4]])
                    data["count_syn"] += syn_string.count(search_expression)
                else:
                    if search_expression not in def_item[2].lower():
                        data["desc"].append([def_item[0], def_item[1], def_item[3], def_item[4]])
                        data["count_desc"] += def_item[2].lower().count(search_expression)
                if search_expression not in def_item[2].lower():
                    data["desc_count_total"] += 1
            else:
                search_expression = expression
                if search_expression in syn_string.lower():
                    data["syn"].append([def_item[0], def_item[1], def_item[3], def_item[4]])
                    data["count_syn"] += syn_string.count(search_expression)
                else:
                    if search_expression in def_item[2].lower():
                        data["desc"].append([def_item[0], def_item[1], def_item[3], def_item[4]])
                        data["count_desc"] += def_item[2].lower().count(search_expression)
                if search_expression in def_item[2].lower():
                    data["desc_count_total"] += 1
                
                if f" {expression} " in f" {syn_string} ":
                    data["whole_syn"].append([def_item[0], def_item[1], def_item[3], def_item[4]])

            count += 1
            
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['def']['defs'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)

        if len(self.data['def']['defs']):
            self.update_log_frame(f"{count+1}/{len(self.data['def']['defs'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        
        self.update_log_frame(self.getl("statistic_log_search_preparing_data"))

        # Displaying data
        if data["syn"]:
            self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_title"), [UTILS.TextUtility.number_to_string_formatted(len(data["syn"])), len(self.data["def"]["defs"])], fg_color="#ffff00", start_new_line=False, reset_label_text=True)
            def_count_percent = UTILS.TextUtility.number_to_string_formatted((len(data["syn"]) / len(self.data["def"]["defs"])) * 100, decimals=4)
            expression_avg = UTILS.TextUtility.number_to_string_formatted((data["count_syn"] / len(data["syn"])), decimals=2)
            if expression.startswith("!"):
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_result_not"), [def_count_percent, UTILS.TextUtility.number_to_string_formatted(data["syn"], decimals=0)])
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_block_list_title_not"), fg_color="#9ca9ff")
            else:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_result"), [def_count_percent, UTILS.TextUtility.number_to_string_formatted(data["syn"], decimals=0), UTILS.TextUtility.number_to_string_formatted(data["count_syn"], decimals=0), expression_avg])
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_block_list_title"), fg_color="#9ca9ff")

            for count, item_in_syn in enumerate(data["syn"]):
                text = f"{count+1}.)  ID={item_in_syn[0]} - {item_in_syn[1]}"
                text1 = f' ({len(item_in_syn[2])} {self.getl("statistic_log_def_syn")}, {len(item_in_syn[3])} {self.getl("statistic_log_def_img")})'
                self.update_info_label(self.lbl_def_info_kw, text, fg_color="#c4e1ff")
                self.update_info_label(self.lbl_def_info_kw, text1, fg_color="#55aa7f", start_new_line=False)
                if count >= 4:
                    break
            if len(data["syn"]) > 5:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_def_default_img_more"), len(data["syn"]) - 5, fg_color="#c4e1ff")

        if data["desc"]:
            if data["syn"]:
                self.update_info_label(self.lbl_def_info_kw, "\n" + self.getl("statistic_log_def_search_desc_title"), [UTILS.TextUtility.number_to_string_formatted(data["desc_count_total"]), len(self.data["def"]["defs"])], fg_color="#ffff00")
            else:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_desc_title"), [UTILS.TextUtility.number_to_string_formatted(data["desc_count_total"]), len(self.data["def"]["defs"])], fg_color="#ffff00", start_new_line=False, reset_label_text=True)

            def_count_percent = UTILS.TextUtility.number_to_string_formatted((data["desc_count_total"] / len(self.data["def"]["defs"])) * 100, decimals=4)
            expression_avg = UTILS.TextUtility.number_to_string_formatted((data["count_desc"] / data["desc_count_total"]), decimals=2)
            if expression.startswith("!"):
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_result_not"), [def_count_percent, UTILS.TextUtility.number_to_string_formatted(data["desc_count_total"], decimals=0)])
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_block_list_title_not"), fg_color="#9ca9ff")
            else:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_desc_result"), [def_count_percent, UTILS.TextUtility.number_to_string_formatted(data["desc_count_total"], decimals=0), UTILS.TextUtility.number_to_string_formatted(data["count_desc"], decimals=0), expression_avg])
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_block_list_title"), fg_color="#9ca9ff")

            for count, item_in_syn in enumerate(data["desc"]):
                text = f"{count+1}.)  ID={item_in_syn[0]} - {item_in_syn[1]}"
                text1 = f' ({len(item_in_syn[2])} {self.getl("statistic_log_def_syn")}, {len(item_in_syn[3])} {self.getl("statistic_log_def_img")})'
                self.update_info_label(self.lbl_def_info_kw, text, fg_color="#c4e1ff")
                self.update_info_label(self.lbl_def_info_kw, text1, fg_color="#55aa7f", start_new_line=False)
                if count >= 4:
                    break
            if len(data["desc"]) > 5:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_def_default_img_more"), len(data["desc"]) - 5, fg_color="#c4e1ff")

        if data["whole_syn"]:
            if data["syn"] or data["desc"]:
                self.update_info_label(self.lbl_def_info_kw, "\n" + self.getl("statistic_log_def_search_whole_title"), UTILS.TextUtility.number_to_string_formatted(len(data["whole_syn"])), fg_color="#ffff00")
            else:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_whole_title"), UTILS.TextUtility.number_to_string_formatted(len(data["whole_syn"])), fg_color="#ffff00", start_new_line=False, reset_label_text=True)

            for count, item_in_syn in enumerate(data["whole_syn"]):
                text = f"{count+1}.)  ID={item_in_syn[0]} - {item_in_syn[1]}"
                text1 = f' ({len(item_in_syn[2])} {self.getl("statistic_log_def_syn")}, {len(item_in_syn[3])} {self.getl("statistic_log_def_img")})'
                self.update_info_label(self.lbl_def_info_kw, text, fg_color="#c4e1ff")
                self.update_info_label(self.lbl_def_info_kw, text1, fg_color="#55aa7f", start_new_line=False)
                if count >= 9:
                    break
            if len(data["whole_syn"]) > 10:
                self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_def_default_img_more"), len(data["whole_syn"]) - 10, fg_color="#c4e1ff")

        if not data["syn"] and not data["desc"] and not data["whole_syn"]:
            self.update_info_label(self.lbl_def_info_kw, self.getl("statistic_log_def_search_no_content"), [expression], fg_color="#ff5500", start_new_line=False, reset_label_text=True)
        
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)

        return True

    def btn_app_clicked(self):
        if self.is_working:
            self._still_busy()
            return
        
        UTILS.LogHandler.add_log_record("#1: About to show #2 statistics.", ["Statistic", "application"])
        self.hide_log_messages()

        self._frame_title_clicked(self.frm_app)

        if self.frm_app.height() == self.COLLAPSED_HEIGHT:
            return

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_app.setCursor(Qt.BusyCursor)
        self.frm_log.setFixedWidth = 120
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), self.getl("statistic_log_about_app"), fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_app_data()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), self.getl("statistic_log_about_app"), fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Displayed #2 statistics.", ["Statistic", "application"])
            self.btn_app.setText(self.getl("statistic_btn_app_text") + f" ({len(self.data['app']['files'])})")
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_app.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_app_data(self) -> bool:
        source_files = UTILS.FileUtility.FOLDER_list_files("")
        
        app_folder = UTILS.FileUtility.get_absolute_path("")
        self.data["app"]["path"] = app_folder
        self._populate_app_info_label()

        # File list
        self.update_log_frame(self.getl("statistic_log_app_get_file_list"))
        self.data["app"]["files"] = []

        for file in source_files:
            if file.endswith((".py", ".pyw")):
                if self.abort_action:
                    return False
                self.data["app"]["files"].append(UTILS.FileUtility.get_FileInformation_object(file))
                self.update_log_frame(self.getl("statistic_log_app_count_files").replace("#1", str(len(self.data["app"]["files"]))), fg_color="#00ffff", start_new_line=False, update_log_text=False)
        self.update_log_frame(self.getl("statistic_log_app_count_files").replace("#1", str(len(self.data["app"]["files"]))), fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_app_info_label()

        # File sizes
        self.update_log_frame(self.getl("statistic_log_app_get_file_sizes"))
        self.data["app"]["sizes"] = []
        count = 0
        step = int(len(self.data["app"]["files"]) / 20) if int(len(self.data["app"]["files"]) / 20) > 0 else 1
        for count, file in enumerate(self.data["app"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            self.data["app"]["sizes"].append([file.get_base_filename(), file.size()])
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)

        if len(self.data['app']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self.data["app"]["sizes"].sort(key=lambda x: x[1], reverse=True)
        self._populate_app_info_label()

        # Oldest / Newest creation time
        self.update_log_frame(self.getl("statistic_log_app_get_creation_times"))
        self.data["app"]["oldest_file"] = None
        self.data["app"]["newest_file"] = None
        count = 0
        step = int(len(self.data["app"]["files"]) / 20) if int(len(self.data["app"]["files"]) / 20) > 0 else 1
        for count, file in enumerate(self.data["app"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["app"]["oldest_file"] or file.created_time(return_DateTimeObject=True) < self.data["app"]["oldest_file"].created_time(return_DateTimeObject=True):
                self.data["app"]["oldest_file"] = file
            if not self.data["app"]["newest_file"] or file.created_time(return_DateTimeObject=True) > self.data["app"]["newest_file"].created_time(return_DateTimeObject=True):
                self.data["app"]["newest_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['app']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_app_info_label()

        # Oldest / Newest modification time
        self.update_log_frame(self.getl("statistic_log_app_get_modification_times"))
        self.data["app"]["oldest_modified_file"] = None
        self.data["app"]["newest_modified_file"] = None
        count = 0
        step = int(len(self.data["app"]["files"]) / 20) if int(len(self.data["app"]["files"]) / 20) > 0 else 1
        for count, file in enumerate(self.data["app"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["app"]["oldest_modified_file"] or file.modification_time(return_DateTimeObject=True) < self.data["app"]["oldest_modified_file"].modification_time(return_DateTimeObject=True):
                self.data["app"]["oldest_modified_file"] = file
            if not self.data["app"]["newest_modified_file"] or file.modification_time(return_DateTimeObject=True) > self.data["app"]["newest_modified_file"].modification_time(return_DateTimeObject=True):
                self.data["app"]["newest_modified_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['app']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_app_info_label()

        # Oldest / Newest accessed time
        self.update_log_frame(self.getl("statistic_log_app_get_access_times"))
        self.data["app"]["oldest_accessed_file"] = None
        self.data["app"]["newest_accessed_file"] = None
        count = 0
        step = int(len(self.data["app"]["files"]) / 20) if int(len(self.data["app"]["files"]) / 20) > 0 else 1
        for count, file in enumerate(self.data["app"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["app"]["oldest_accessed_file"] or file.access_time(return_DateTimeObject=True) < self.data["app"]["oldest_accessed_file"].access_time(return_DateTimeObject=True):
                self.data["app"]["oldest_accessed_file"] = file
            if not self.data["app"]["newest_accessed_file"] or file.access_time(return_DateTimeObject=True) > self.data["app"]["newest_accessed_file"].access_time(return_DateTimeObject=True):
                self.data["app"]["newest_accessed_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['app']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_app_info_label()

        # File content
        self.update_log_frame(self.getl("statistic_log_app_get_file_content"))
        self.data["app"]["file_content"] = []
        count = 0
        step = int(len(self.data["app"]["files"]) / 20) if int(len(self.data["app"]["files"]) / 20) > 0 else 1
        for count, file in enumerate(self.data["app"]["files"]):
            if self.abort_action:
                return False
            self.data["app"]["file_content"].append([file.get_base_filename(), file.file_content_count_lines(), file.file_content_count_words(), file.file_content_count_chars()])
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['app']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['app']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_app_info_label()

        return True

    def _populate_app_info_label(self):
        # Path
        value = self.data["app"]["path"] if self.data["app"]["path"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_folder_path"), value, reset_label_text=True)
        # Files count and total size
        self.update_info_label(self.lbl_app_info, "\n" + self.getl("statistic_app_info_files_count_and_total_size_title"), fg_color="#ffff00")
        value1 = str(len(self.data["app"]["files"])) if self.data["app"]["files"] is not None else self.WAITING_FOR_DATA
        value2 = FileInformation.get_size_formatted_string(sum([x[1] for x in self.data["app"]["sizes"]])) if self.data["app"]["sizes"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_files_count_and_total_size"), [value1, value2])
        if self.data["app"]["sizes"]:
            average_size = FileInformation.get_size_formatted_string(sum([x[1] for x in self.data["app"]["sizes"]]) / len(self.data["app"]["sizes"]))
            self.update_info_label(self.lbl_app_info, " " + self.getl("statistic_app_info_min_max_file_sizes"), [average_size, f'{self.data["app"]["sizes"][0][0]} ({FileInformation.get_size_formatted_string(self.data["app"]["sizes"][0][1])})', f'{self.data["app"]["sizes"][-1][0]} ({FileInformation.get_size_formatted_string(self.data["app"]["sizes"][-1][1])})'], start_new_line=False)
        # Top 5 file sizes
        if self.data["app"]["sizes"]:
            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_top5_file_sizes"))
            top5 = self.data["app"]["sizes"][:5] if len(self.data["app"]["sizes"]) >= 5 else self.data["app"]["sizes"]
            for index, item in enumerate(top5):
                self.update_info_label(self.lbl_app_info, f"{index+1}.) #1 (#2)", [item[0], FileInformation.get_size_formatted_string(item[1])])
        # File created time, modified time and accessed time
        self.update_info_label(self.lbl_app_info, "\n" + self.getl("statistic_app_file_times_title"), fg_color="#ffff00")
        # Created time oldest file
        file: FileInformation = self.data["app"]["oldest_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.created_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_oldest_file"), [value1, value2, value3])
        # Created time newest file
        file: FileInformation = self.data["app"]["newest_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.created_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_newest_file"), [value1, value2, value3])
        # Modification time oldest file
        file: FileInformation = self.data["app"]["oldest_modified_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.modified_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.modification_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_oldest_modified_file"), [value1, value2, value3])
        # Modification time newest file
        file: FileInformation = self.data["app"]["newest_modified_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.modified_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.modification_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_newest_modified_file"), [value1, value2, value3])
        # Access time oldest file
        file: FileInformation = self.data["app"]["oldest_accessed_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.accessed_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.access_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_oldest_accessed_file"), [value1, value2, value3])
        # Access time newest file
        file: FileInformation = self.data["app"]["newest_accessed_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.accessed_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.access_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_newest_accessed_file"), [value1, value2, value3])
        # File content
        if self.data["app"]["file_content"] is not None:
            self.update_info_label(self.lbl_app_info, "\n" + self.getl("statistic_app_file_content_title"), fg_color="#ffff00")
            max_lines = ["", 0, 0]
            min_lines = ["", 0, 0]
            max_words = ["", 0, 0]
            min_words = ["", 0, 0]
            total_lines = 0
            total_words = 0
            total_chars = 0
            for content_info in self.data["app"]["file_content"]:
                total_lines += content_info[1]
                total_words += content_info[2]
                total_chars += content_info[3]
                if content_info[1] > max_lines[1]:
                    max_lines = content_info
                if min_lines[1] == 0:
                    min_lines = content_info
                if content_info[1] < min_lines[1] and content_info[1] != 0:
                    min_lines = content_info
                if content_info[2] > max_words[2]:
                    max_words = content_info
                if min_words[2] == 0:
                    min_words = content_info
                if content_info[2] < min_words[2] and content_info[2] != 0:
                    min_words = content_info

            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_total_lines"), [len(self.data["app"]["file_content"]), TextUtility.number_to_string_formatted(total_lines, decimals=0)])
            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_max_lines"), [max_lines[0], TextUtility.number_to_string_formatted(max_lines[1], decimals=0)])
            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_min_lines"), [min_lines[0], TextUtility.number_to_string_formatted(min_lines[1], decimals=0)])
            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_total_words"), [len(self.data["app"]["file_content"]), TextUtility.number_to_string_formatted(total_words, decimals=0), TextUtility.number_to_string_formatted(total_chars, decimals=0)])
            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_max_words"), [max_words[0], TextUtility.number_to_string_formatted(max_words[2], decimals=0)])
            self.update_info_label(self.lbl_app_info, self.getl("statistic_app_info_min_words"), [min_words[0], TextUtility.number_to_string_formatted(min_words[2], decimals=0)])

        QCoreApplication.processEvents()

    def btn_img_clicked(self):
        if self.is_working:
            self._still_busy()
            return

        UTILS.LogHandler.add_log_record("#1: About to show #2 statistics.", ["Statistic", "image"])
        self.hide_log_messages()

        self._frame_title_clicked(self.frm_img)

        if self.frm_img.height() == self.COLLAPSED_HEIGHT:
            return

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_img.setCursor(Qt.BusyCursor)
        self.frm_log.setFixedWidth = 120
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), self.getl("statistic_log_about_img"), fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_img_data()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), self.getl("statistic_log_about_img"), fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Displayed #2 statistics.", ["Statistic", "image"])
            self.btn_img.setText(self.getl("statistic_btn_img_text") + f" ({len(self.data['img']['files'])})")
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_img.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_img_data(self) -> bool:
        user_db_file_information = UTILS.FileUtility.get_FileInformation_object(self.get_appv("user").db_path)
        user_image_folder = user_db_file_information.get_dir_name() + str(self.get_appv("user").id) + "images/"
        db_media = db_media_cls.Media(self._stt)
        if not db_media.get_all_media() or not UTILS.FileUtility.FOLDER_is_exist(user_image_folder):
            self.update_info_label(self.lbl_img_info, self.getl("statistic_no_data_text"), reset_label_text=True, start_new_line=False)
            self.data["img"]["files"] = []
            return True
        
        source_files = UTILS.FileUtility.FOLDER_list_files(user_image_folder)
        
        img_folder = UTILS.FileUtility.get_absolute_path(user_image_folder)
        self.data["img"]["path"] = img_folder
        self._populate_img_info_label()

        # File list
        self.update_log_frame(self.getl("statistic_log_app_get_file_list"))
        self.data["img"]["files"] = []

        for file in source_files:
            if self.abort_action:
                return False
            self.data["img"]["files"].append(UTILS.FileUtility.get_FileInformation_object(file))
            self.update_log_frame(self.getl("statistic_log_app_count_files").replace("#1", str(len(self.data["img"]["files"]))), fg_color="#00ffff", start_new_line=False, update_log_text=False)
        self.update_log_frame(self.getl("statistic_log_app_count_files").replace("#1", str(len(self.data["img"]["files"]))), fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_img_info_label()

        # File sizes
        self.update_log_frame(self.getl("statistic_log_app_get_file_sizes"))
        self.data["img"]["sizes"] = []
        count = 0
        step = int(len(self.data["img"]["files"]) / 100) if int(len(self.data["img"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["img"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            self.data["img"]["sizes"].append([file.get_base_filename(), file.size()])
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)

        if len(self.data['img']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self.data["img"]["sizes"].sort(key=lambda x: x[1], reverse=True)
        self._populate_img_info_label()

        # Oldest / Newest creation time
        self.update_log_frame(self.getl("statistic_log_app_get_creation_times"))
        self.data["img"]["oldest_file"] = None
        self.data["img"]["newest_file"] = None
        count = 0
        step = int(len(self.data["img"]["files"]) / 100) if int(len(self.data["img"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["img"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["img"]["oldest_file"] or file.created_time(return_DateTimeObject=True) < self.data["img"]["oldest_file"].created_time(return_DateTimeObject=True):
                self.data["img"]["oldest_file"] = file
            if not self.data["img"]["newest_file"] or file.created_time(return_DateTimeObject=True) > self.data["img"]["newest_file"].created_time(return_DateTimeObject=True):
                self.data["img"]["newest_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['img']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_img_info_label()

        # Oldest / Newest modification time
        self.update_log_frame(self.getl("statistic_log_app_get_modification_times"))
        self.data["img"]["oldest_modified_file"] = None
        self.data["img"]["newest_modified_file"] = None
        count = 0
        step = int(len(self.data["img"]["files"]) / 100) if int(len(self.data["img"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["img"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["img"]["oldest_modified_file"] or file.modification_time(return_DateTimeObject=True) < self.data["img"]["oldest_modified_file"].modification_time(return_DateTimeObject=True):
                self.data["img"]["oldest_modified_file"] = file
            if not self.data["img"]["newest_modified_file"] or file.modification_time(return_DateTimeObject=True) > self.data["img"]["newest_modified_file"].modification_time(return_DateTimeObject=True):
                self.data["img"]["newest_modified_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['img']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_img_info_label()

        # Oldest / Newest accessed time
        self.update_log_frame(self.getl("statistic_log_app_get_access_times"))
        self.data["img"]["oldest_accessed_file"] = None
        self.data["img"]["newest_accessed_file"] = None
        count = 0
        step = int(len(self.data["img"]["files"]) / 100) if int(len(self.data["img"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["img"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["img"]["oldest_accessed_file"] or file.access_time(return_DateTimeObject=True) < self.data["img"]["oldest_accessed_file"].access_time(return_DateTimeObject=True):
                self.data["img"]["oldest_accessed_file"] = file
            if not self.data["img"]["newest_accessed_file"] or file.access_time(return_DateTimeObject=True) > self.data["img"]["newest_accessed_file"].access_time(return_DateTimeObject=True):
                self.data["img"]["newest_accessed_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['img']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_img_info_label()

        # File types
        self.update_log_frame(self.getl("statistic_log_img_get_file_types"))
        self.data["img"]["file_types"] = {}
        count = 0
        step = int(len(self.data["img"]["files"]) / 100) if int(len(self.data["img"]["files"]) / 100) > 0 else 1
        if self.data["img"]["files"]:
            self.data["img"]["file_types"] = {}

        for count, file in enumerate(self.data["img"]["files"]):
            if self.abort_action:
                return False
            extension = file.extension().lower()
            if extension in self.data["img"]["file_types"]:
                self.data["img"]["file_types"][extension][0] += 1
                self.data["img"]["file_types"][extension][1] += file.size()
            else:
                self.data["img"]["file_types"][extension] = [1, file.size()]

            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['img']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['img']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_img_info_label()

        return True

    def _populate_img_info_label(self):
        # Path
        value = self.data["img"]["path"] if self.data["img"]["path"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_folder_path"), value, reset_label_text=True)
        # Files count and total size
        self.update_info_label(self.lbl_img_info, "\n" + self.getl("statistic_app_info_files_count_and_total_size_title"), fg_color="#ffff00")
        value1 = str(len(self.data["img"]["files"])) if self.data["img"]["files"] is not None else self.WAITING_FOR_DATA
        value2 = FileInformation.get_size_formatted_string(sum([x[1] for x in self.data["img"]["sizes"]])) if self.data["img"]["sizes"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_files_count_and_total_size"), [value1, value2])
        if self.data["img"]["sizes"]:
            average_size = FileInformation.get_size_formatted_string(sum([x[1] for x in self.data["img"]["sizes"]]) / len(self.data["img"]["sizes"]))
            self.update_info_label(self.lbl_img_info, " " + self.getl("statistic_app_info_min_max_file_sizes"), [average_size, f'{self.data["img"]["sizes"][0][0]} ({FileInformation.get_size_formatted_string(self.data["img"]["sizes"][0][1])})', f'{self.data["img"]["sizes"][-1][0]} ({FileInformation.get_size_formatted_string(self.data["img"]["sizes"][-1][1])})'], start_new_line=False)
        # Top 5 file sizes
        if self.data["img"]["sizes"]:
            self.update_info_label(self.lbl_img_info, self.getl("statistic_app_info_top5_file_sizes"))
            top5 = self.data["img"]["sizes"][:10] if len(self.data["img"]["sizes"]) >= 10 else self.data["img"]["sizes"]
            for index, item in enumerate(top5):
                self.update_info_label(self.lbl_img_info, f"{index+1}.) #1 (#2)", [item[0], FileInformation.get_size_formatted_string(item[1])])
        # File created time, modified time and accessed time
        self.update_info_label(self.lbl_img_info, "\n" + self.getl("statistic_app_file_times_title"), fg_color="#ffff00")
        # Created time oldest file
        file: FileInformation = self.data["img"]["oldest_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.created_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_oldest_file"), [value1, value2, value3])
        # Created time newest file
        file: FileInformation = self.data["img"]["newest_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.created_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_newest_file"), [value1, value2, value3])
        # Modification time oldest file
        file: FileInformation = self.data["img"]["oldest_modified_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.modified_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.modification_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_oldest_modified_file"), [value1, value2, value3])
        # Modification time newest file
        file: FileInformation = self.data["img"]["newest_modified_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.modified_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.modification_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_newest_modified_file"), [value1, value2, value3])
        # Access time oldest file
        file: FileInformation = self.data["img"]["oldest_accessed_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.accessed_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.access_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_oldest_accessed_file"), [value1, value2, value3])
        # Access time newest file
        file: FileInformation = self.data["img"]["newest_accessed_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.accessed_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.access_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_img_info, self.getl("statistic_img_info_newest_accessed_file"), [value1, value2, value3])
        # File types
        if self.data["img"]["file_types"] is not None:
            self.update_info_label(self.lbl_img_info, "\n" + self.getl("statistic_img_file_type_title"), fg_color="#ffff00")

            count = 1
            for key, item in self.data["img"]["file_types"].items():
                self.update_info_label(self.lbl_img_info, self.getl("statistic_img_file_type_item"), [count, key.upper(), TextUtility.number_to_string_formatted(item[0], decimals=0), FileInformation.get_size_formatted_string(item[1])])
                count += 1

        QCoreApplication.processEvents()

    def btn_file_clicked(self):
        if self.is_working:
            self._still_busy()
            return

        UTILS.LogHandler.add_log_record("#1: About to show #2 statistics.", ["Statistic", "file"])
        self.hide_log_messages()

        self._frame_title_clicked(self.frm_file)

        if self.frm_file.height() == self.COLLAPSED_HEIGHT:
            return

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_file.setCursor(Qt.BusyCursor)
        self.frm_log.setFixedWidth = 120
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), self.getl("statistic_log_about_file"), fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_file_data()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), self.getl("statistic_log_about_file"), fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Displayed #2 statistics.", ["Statistic", "file"])
            self.btn_file.setText(self.getl("statistic_btn_file_text") + f" ({len(self.data['file']['files'])})")
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_file.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_file_data(self) -> bool:
        user_db_file_information = UTILS.FileUtility.get_FileInformation_object(self.get_appv("user").db_path)
        user_file_folder = user_db_file_information.get_dir_name() + str(self.get_appv("user").id) + "files/"
        db_media = db_media_cls.Files(self._stt)
        if not db_media.get_all_file() or not UTILS.FileUtility.FOLDER_is_exist(user_file_folder):
            self.update_info_label(self.lbl_file_info, self.getl("statistic_no_data_text"), reset_label_text=True, start_new_line=False)
            self.data["file"]["files"] = []
            return True

        source_files = UTILS.FileUtility.FOLDER_list_files(user_file_folder)
        
        file_folder = UTILS.FileUtility.get_absolute_path(user_file_folder)
        self.data["file"]["path"] = file_folder
        self._populate_file_info_label()

        # File list
        self.update_log_frame(self.getl("statistic_log_app_get_file_list"))
        self.data["file"]["files"] = []

        for file in source_files:
            if self.abort_action:
                return False
            self.data["file"]["files"].append(UTILS.FileUtility.get_FileInformation_object(file))
            self.update_log_frame(self.getl("statistic_log_app_count_files").replace("#1", str(len(self.data["file"]["files"]))), fg_color="#00ffff", start_new_line=False, update_log_text=False)
        self.update_log_frame(self.getl("statistic_log_app_count_files").replace("#1", str(len(self.data["file"]["files"]))), fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_file_info_label()

        # File sizes
        self.update_log_frame(self.getl("statistic_log_app_get_file_sizes"))
        self.data["file"]["sizes"] = []
        count = 0
        step = int(len(self.data["file"]["files"]) / 100) if int(len(self.data["file"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["file"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            self.data["file"]["sizes"].append([file.get_base_filename(), file.size()])
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)

        if len(self.data['file']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self.data["file"]["sizes"].sort(key=lambda x: x[1], reverse=True)
        self._populate_file_info_label()

        # Oldest / Newest creation time
        self.update_log_frame(self.getl("statistic_log_app_get_creation_times"))
        self.data["file"]["oldest_file"] = None
        self.data["file"]["newest_file"] = None
        count = 0
        step = int(len(self.data["file"]["files"]) / 100) if int(len(self.data["file"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["file"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["file"]["oldest_file"] or file.created_time(return_DateTimeObject=True) < self.data["file"]["oldest_file"].created_time(return_DateTimeObject=True):
                self.data["file"]["oldest_file"] = file
            if not self.data["file"]["newest_file"] or file.created_time(return_DateTimeObject=True) > self.data["file"]["newest_file"].created_time(return_DateTimeObject=True):
                self.data["file"]["newest_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['file']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_file_info_label()

        # Oldest / Newest modification time
        self.update_log_frame(self.getl("statistic_log_app_get_modification_times"))
        self.data["file"]["oldest_modified_file"] = None
        self.data["file"]["newest_modified_file"] = None
        count = 0
        step = int(len(self.data["file"]["files"]) / 100) if int(len(self.data["file"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["file"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["file"]["oldest_modified_file"] or file.modification_time(return_DateTimeObject=True) < self.data["file"]["oldest_modified_file"].modification_time(return_DateTimeObject=True):
                self.data["file"]["oldest_modified_file"] = file
            if not self.data["file"]["newest_modified_file"] or file.modification_time(return_DateTimeObject=True) > self.data["file"]["newest_modified_file"].modification_time(return_DateTimeObject=True):
                self.data["file"]["newest_modified_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['file']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_file_info_label()

        # Oldest / Newest accessed time
        self.update_log_frame(self.getl("statistic_log_app_get_access_times"))
        self.data["file"]["oldest_accessed_file"] = None
        self.data["file"]["newest_accessed_file"] = None
        count = 0
        step = int(len(self.data["file"]["files"]) / 100) if int(len(self.data["file"]["files"]) / 100) > 0 else 1
        for count, file in enumerate(self.data["file"]["files"]):
            file: FileInformation
            if self.abort_action:
                return False
            if not self.data["file"]["oldest_accessed_file"] or file.access_time(return_DateTimeObject=True) < self.data["file"]["oldest_accessed_file"].access_time(return_DateTimeObject=True):
                self.data["file"]["oldest_accessed_file"] = file
            if not self.data["file"]["newest_accessed_file"] or file.access_time(return_DateTimeObject=True) > self.data["file"]["newest_accessed_file"].access_time(return_DateTimeObject=True):
                self.data["file"]["newest_accessed_file"] = file
            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['file']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_file_info_label()

        # File types
        self.update_log_frame(self.getl("statistic_log_img_get_file_types"))
        self.data["file"]["file_types"] = {}
        count = 0
        step = int(len(self.data["file"]["files"]) / 100) if int(len(self.data["file"]["files"]) / 100) > 0 else 1
        if self.data["file"]["files"]:
            self.data["file"]["file_types"] = {}

        for count, file in enumerate(self.data["file"]["files"]):
            if self.abort_action:
                return False
            extension = file.extension().lower()
            if extension in self.data["file"]["file_types"]:
                self.data["file"]["file_types"][extension][0] += 1
                self.data["file"]["file_types"][extension][1] += file.size()
            else:
                self.data["file"]["file_types"][extension] = [1, file.size()]

            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if len(self.data['file']['files']):
            self.update_log_frame(f"{count+1}/{len(self.data['file']['files'])}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_file_info_label()

        return True

    def _populate_file_info_label(self):
        # Path
        value = self.data["file"]["path"] if self.data["file"]["path"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_folder_path"), value, reset_label_text=True)
        # Files count and total size
        self.update_info_label(self.lbl_file_info, "\n" + self.getl("statistic_app_info_files_count_and_total_size_title"), fg_color="#ffff00")
        value1 = str(len(self.data["file"]["files"])) if self.data["file"]["files"] is not None else self.WAITING_FOR_DATA
        value2 = FileInformation.get_size_formatted_string(sum([x[1] for x in self.data["file"]["sizes"]])) if self.data["file"]["sizes"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_files_count_and_total_size"), [value1, value2])
        if self.data["file"]["sizes"]:
            average_size = FileInformation.get_size_formatted_string(sum([x[1] for x in self.data["file"]["sizes"]]) / len(self.data["file"]["sizes"]))
            self.update_info_label(self.lbl_file_info, " " + self.getl("statistic_app_info_min_max_file_sizes"), [average_size, f'{self.data["file"]["sizes"][0][0]} ({FileInformation.get_size_formatted_string(self.data["file"]["sizes"][0][1])})', f'{self.data["file"]["sizes"][-1][0]} ({FileInformation.get_size_formatted_string(self.data["file"]["sizes"][-1][1])})'], start_new_line=False)
        # Top 5 file sizes
        if self.data["file"]["sizes"]:
            self.update_info_label(self.lbl_file_info, self.getl("statistic_app_info_top5_file_sizes"))
            top5 = self.data["file"]["sizes"][:10] if len(self.data["file"]["sizes"]) >= 10 else self.data["file"]["sizes"]
            for index, item in enumerate(top5):
                self.update_info_label(self.lbl_file_info, f"{index+1}.) #1 (#2)", [item[0], FileInformation.get_size_formatted_string(item[1])])
        # File created time, modified time and accessed time
        self.update_info_label(self.lbl_file_info, "\n" + self.getl("statistic_app_file_times_title"), fg_color="#ffff00")
        # Created time oldest file
        file: FileInformation = self.data["file"]["oldest_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.created_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_oldest_file"), [value1, value2, value3])
        # Created time newest file
        file: FileInformation = self.data["file"]["newest_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.created_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.created_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_newest_file"), [value1, value2, value3])
        # Modification time oldest file
        file: FileInformation = self.data["file"]["oldest_modified_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.modified_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.modification_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_oldest_modified_file"), [value1, value2, value3])
        # Modification time newest file
        file: FileInformation = self.data["file"]["newest_modified_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.modified_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.modification_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_newest_modified_file"), [value1, value2, value3])
        # Access time oldest file
        file: FileInformation = self.data["file"]["oldest_accessed_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.accessed_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.access_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_oldest_accessed_file"), [value1, value2, value3])
        # Access time newest file
        file: FileInformation = self.data["file"]["newest_accessed_file"]
        value1 = file.get_base_filename() if file is not None else self.WAITING_FOR_DATA
        value2 = self._period_before_formatted_string(file.accessed_before_period()) if file is not None else self.WAITING_FOR_DATA
        value3 = file.access_time(return_DateTimeObject=True, datetime_format_delimiter=f' {self.getl("at")} ').DATE_TIME_formatted_string if file is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_file_info, self.getl("statistic_file_info_newest_accessed_file"), [value1, value2, value3])
        # File types
        if self.data["file"]["file_types"] is not None:
            self.update_info_label(self.lbl_file_info, "\n" + self.getl("statistic_img_file_type_title"), fg_color="#ffff00")

            count = 1
            for key, item in self.data["file"]["file_types"].items():
                self.update_info_label(self.lbl_file_info, self.getl("statistic_img_file_type_item"), [count, key.upper(), TextUtility.number_to_string_formatted(item[0], decimals=0), FileInformation.get_size_formatted_string(item[1])])
                count += 1

        QCoreApplication.processEvents()

    def btn_block_clicked(self):
        if self.is_working:
            self._still_busy()
            return

        UTILS.LogHandler.add_log_record("#1: About to show #2 statistics.", ["Statistic", "block"])
        self.hide_log_messages()

        self._frame_title_clicked(self.frm_block)

        if self.frm_block.height() == self.COLLAPSED_HEIGHT:
            return

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_block.setCursor(Qt.BusyCursor)
        self.frm_log.setFixedWidth = 120
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), self.getl("statistic_log_about_block"), fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_block_data()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), self.getl("statistic_log_about_block"), fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Displayed #2 statistics.", ["Statistic", "block"])
            self.btn_block.setText(self.getl("statistic_btn_block_text") + f" ({len(self.data['block']['blocks'])})")
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_block.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_block_data(self) -> bool:
        # Database information
        self.update_log_frame(self.getl("statistic_log_block_db"))
        user_db_file_information = UTILS.FileUtility.get_FileInformation_object(self.get_appv("user").db_path)
        self.data["block"]["db_path"] = self.get_appv("user").db_path
        self.data["block"]["db"] = user_db_file_information
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_block_info_label()

        # Block count
        self.update_log_frame(self.getl("statistic_log_block_count"))

        db_block = db_record_cls.Record(self._stt)
        db_data = db_record_data_cls.RecordData(self._stt)
        block_list = db_block.get_all_records(sort_by_id=True)
        block_data_list = db_data.get_all_record_data()

        self.data["block"]["blocks"] = block_list
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_block_info_label()

        # Block dates and content
        self.update_log_frame(self.getl("statistic_log_block_content"))
        self.data["block"]["dates"] = {}
        count = 0
        step = int(len(block_list) / 100) if int(len(block_list) / 100) > 0 else 1
        for block in block_list:
            if self.abort_action:
                return False
            
            # Update dates field
            block_item = {
                "block_id": block[0],
                "block_name": block[1],
                "block_date": block[2],
                "sentences": UTILS.TextUtility.count_sentences(block[4]),
                "words": UTILS.TextUtility.count_words(block[4]),
                "characters": len(block[4]),
                "created_at": block[6],
                "updated_at": block[7]
            }
            if self.data["block"]["dates"].get(block[2]) is None:
                self.data["block"]["dates"][block[2]] = [block_item]
            else:
                self.data["block"]["dates"][block[2]].append(block_item)
            
            count += 1

            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(block_list)}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if block_list:
            self.update_log_frame(f"{count+1}/{len(block_list)}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_block_info_label()

        # Block tags and media
        self.update_log_frame(self.getl("statistic_log_block_media"))
        block_id = None
        self.data["block"]["media"] = []
        count = 0
        step = int(len(block_data_list) / 10) if int(len(block_data_list) / 10) > 0 else 1
        for item in block_data_list:
            if self.abort_action:
                return False
            
            add_tag = 1 if item[2] else 0
            add_media = 1 if item[3] else 0
            
            if item[1] != block_id:
                self.data["block"]["media"].append([item[1], 0, 0])
            
            self.data["block"]["media"][-1][1] += add_tag
            self.data["block"]["media"][-1][2] += add_media

            count += 1

            if count % step == 0:
                self.update_log_frame(f"{count+1}/{len(block_data_list)}", fg_color="#00ffff", start_new_line=False, update_log_text=False)
        
        if block_data_list:
            self.update_log_frame(f"{count+1}/{len(block_data_list)}", fg_color="#00ffff", start_new_line=False)
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_block_info_label()

        if self.abort_action:
            return False

        return True

    def _populate_block_info_label(self):
        # Path
        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_db_title"), fg_color="#ffff00", reset_label_text=True, start_new_line=False)
        value = self.data["block"]["db_path"] if self.data["block"]["db_path"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_db_folder_path"), value)

        # Database information
        if self.data["block"]["db"] is not None:
            db_file: FileInformation = self.data["block"]["db"]
            db_size = db_file.size(return_formatted_string=True)
            db_created = db_file.created_time()
            db_created_before = self._period_before_formatted_string(db_file.created_before_period())
            db_modified = db_file.modification_time()
            db_modified_before = self._period_before_formatted_string(db_file.modified_before_period())
            db_accessed = db_file.access_time()
            db_accessed_before = self._period_before_formatted_string(db_file.accessed_before_period())
            self.update_info_label(self.lbl_block_info, self.getl("statistic_block_db_info"), [db_size, db_created, db_created_before, db_modified, db_modified_before, db_accessed, db_accessed_before])

        if not self.data["block"]["dates"] or not self.data["block"]["blocks"]:
            QCoreApplication.processEvents()
            return

        # First and last block
        self.update_info_label(self.lbl_block_info, "\n" + self.getl("statistic_block_title"), fg_color="#ffff00")

        now = UTILS.DateTime.DateTime.now()
        first_date = UTILS.DateTime.DateTimeObject(self.data["block"]["blocks"][0][2]) if len(self.data["block"]["blocks"]) > 0 else "???"
        first_created = UTILS.DateTime.DateTimeObject(self.data["block"]["blocks"][0][6], datetime_format_delimiter=f' {self.getl("at")} ') if len(self.data["block"]["blocks"]) > 0 else "???"
        first_created_before = self._period_before_formatted_string(now - first_created) if isinstance(first_created, UTILS.DateTime.DateTimeObject) else "???"
        first_updated = UTILS.DateTime.DateTimeObject(self.data["block"]["blocks"][0][7], datetime_format_delimiter=f' {self.getl("at")} ') if len(self.data["block"]["blocks"]) > 0 else "???"
        first_updated_before = self._period_before_formatted_string(now - first_updated) if first_updated != "???" else "???"

        last_date = UTILS.DateTime.DateTimeObject(self.data["block"]["blocks"][-1][2]) if len(self.data["block"]["blocks"]) > 0 else "???"
        last_created = UTILS.DateTime.DateTimeObject(self.data["block"]["blocks"][-1][6], datetime_format_delimiter=f' {self.getl("at")} ') if len(self.data["block"]["blocks"]) > 0 else "???"
        last_created_before = self._period_before_formatted_string(now - last_created) if last_created != "???" else "???"
        last_updated = UTILS.DateTime.DateTimeObject(self.data["block"]["blocks"][-1][7], datetime_format_delimiter=f' {self.getl("at")} ') if len(self.data["block"]["blocks"]) > 0 else "???"
        last_updated_before = self._period_before_formatted_string(now - last_updated) if last_updated != "???" else "???"

        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_count"), [UTILS.TextUtility.number_to_string_formatted(len(self.data["block"]["blocks"]), decimals=0)])
        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_first_date"), [first_date.DATE_formatted_string, first_created.DATE_TIME_formatted_string, first_created_before, first_updated.DATE_TIME_formatted_string, first_updated_before])
        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_last_date"), [last_date.DATE_formatted_string, last_created.DATE_TIME_formatted_string, last_created_before, last_updated.DATE_TIME_formatted_string, last_updated_before])
    
        # Biggest and smallest block
        self.update_info_label(self.lbl_block_info, "\n" + self.getl("statistic_block_content_title"), fg_color="#ffff00")

        biggest_block = None
        smallest_block = None

        for block in self.data["block"]["blocks"]:
            if biggest_block is None:
                biggest_block = block
            if len(block[4]) > len(biggest_block[4]):
                biggest_block = block
            if smallest_block is None:
                smallest_block = block
            if len(block[4]) < len(smallest_block[4]):
                smallest_block = block
        
        if biggest_block is not None:
            biggest_block_content = biggest_block[4]
            biggest_block_date = UTILS.DateTime.DateTimeObject(biggest_block[2]).DATE_formatted_string
            biggest_block_date_before = self._period_before_formatted_string(UTILS.DateTime.DateTime.now() - UTILS.DateTime.DateTimeObject(biggest_block[2]))
            biggest_block_words = UTILS.TextUtility.count_words(biggest_block_content)
            self.update_info_label(self.lbl_block_info, self.getl("statistic_block_biggest_block"), [biggest_block_date, biggest_block_date_before, UTILS.TextUtility.number_to_string_formatted(biggest_block_words, decimals=0), UTILS.TextUtility.number_to_string_formatted(len(biggest_block_content), decimals=0)])
        
        if smallest_block is not None:
            smallest_block_content = smallest_block[4]
            smallest_block_date = UTILS.DateTime.DateTimeObject(smallest_block[2]).DATE_formatted_string
            smallest_block_date_before = self._period_before_formatted_string(UTILS.DateTime.DateTime.now() - UTILS.DateTime.DateTimeObject(smallest_block[2]))
            smallest_block_words = UTILS.TextUtility.count_words(smallest_block_content)
            self.update_info_label(self.lbl_block_info, self.getl("statistic_block_smallest_block"), [smallest_block_date, smallest_block_date_before, UTILS.TextUtility.number_to_string_formatted(smallest_block_words, decimals=0), UTILS.TextUtility.number_to_string_formatted(len(smallest_block_content), decimals=0)])
        
        # Blocks with names and content info
        total_sentences = 0
        total_words = 0
        total_characters = 0
        blocks_with_names = 0
        block_count = len(self.data["block"]["blocks"])
        most_content_date = None
        most_block_per_date = None
        for date in self.data["block"]["dates"]:
            b_char = 0
            for block in self.data["block"]["dates"][date]:
                total_sentences += block["sentences"]
                total_words += block["words"]
                total_characters += block["characters"]
                b_char += block["characters"]
                if block["block_name"]:
                    blocks_with_names += 1
            if most_content_date is None:
                most_content_date = {
                    "date": date,
                    "blocks": self.data["block"]["dates"][date]
                }
            if sum([x["characters"] for x in self.data["block"]["dates"][date]]) > sum([x["characters"] for x in most_content_date["blocks"]]):
                most_content_date = {
                    "date": date,
                    "blocks": self.data["block"]["dates"][date]
                }
            
            if most_block_per_date is None or len(self.data["block"]["dates"][date]) > most_block_per_date["blocks"]:
                most_block_per_date = {
                    "date": date,
                    "blocks": len(self.data["block"]["dates"][date]),
                    "sentences": sum([x["sentences"] for x in self.data["block"]["dates"][date]]),
                    "words": sum([x["words"] for x in self.data["block"]["dates"][date]]),
                    "characters": sum([x["characters"] for x in self.data["block"]["dates"][date]])
                }

        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_content"), [UTILS.TextUtility.number_to_string_formatted(block_count, decimals=0), UTILS.TextUtility.number_to_string_formatted(total_sentences, decimals=0), UTILS.TextUtility.number_to_string_formatted(total_words, decimals=0), UTILS.TextUtility.number_to_string_formatted(total_characters, decimals=0)])

        if most_content_date is not None:
            mcd_date = UTILS.DateTime.DateTimeObject(most_content_date["date"]).DATE_formatted_string
            mcd_before = self._period_before_formatted_string(UTILS.DateTime.DateTime.now() - UTILS.DateTime.DateTimeObject(most_content_date["date"]))
            mcd_sentences = sum([x["sentences"] for x in most_content_date["blocks"]])
            mcd_words = sum([x["words"] for x in most_content_date["blocks"]])
            mcd_characters = sum([x["characters"] for x in most_content_date["blocks"]])
            mcd_blocks = len(most_content_date["blocks"])
            self.update_info_label(self.lbl_block_info, self.getl("statistic_block_most_content"), [mcd_before, mcd_date, UTILS.TextUtility.number_to_string_formatted(mcd_sentences, decimals=0), UTILS.TextUtility.number_to_string_formatted(mcd_words, decimals=0), UTILS.TextUtility.number_to_string_formatted(mcd_characters, decimals=0), UTILS.TextUtility.number_to_string_formatted(mcd_blocks, decimals=0)])

        self.update_info_label(self.lbl_block_info, "\n" + self.getl("statistic_block_avg_title"), fg_color="#ffff00")

        blocks_with_names_percent = UTILS.TextUtility.number_to_string_formatted((blocks_with_names / block_count) * 100, decimals=2)

        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_avg_names"), [blocks_with_names_percent, UTILS.TextUtility.number_to_string_formatted(blocks_with_names, decimals=0)])
        
        total_sentences_avg = UTILS.TextUtility.number_to_string_formatted(total_sentences / block_count, decimals=2)
        total_words_avg = UTILS.TextUtility.number_to_string_formatted(total_words / block_count, decimals=2)
        total_characters_avg = UTILS.TextUtility.number_to_string_formatted(total_characters / block_count, decimals=2)

        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_avg_content"), [total_sentences_avg, total_words_avg, total_characters_avg])

        # Average block per day
        bpd_elapsed_total = UTILS.DateTime.DateTime.today() - first_date
        bpd_total_entry_days = len(self.data["block"]["dates"])
        bpd_total_entry_days_percent = UTILS.TextUtility.number_to_string_formatted((bpd_total_entry_days / bpd_elapsed_total.total_days) * 100, decimals=2) if bpd_elapsed_total.total_days else "0"

        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_day_title"), [UTILS.TextUtility.number_to_string_formatted(bpd_elapsed_total.total_days), UTILS.TextUtility.number_to_string_formatted(bpd_total_entry_days), bpd_total_entry_days_percent])

        bpd_blocks_per_day = UTILS.TextUtility.number_to_string_formatted(block_count / bpd_total_entry_days, decimals=2) if bpd_total_entry_days else "0"
        sentences_per_day = UTILS.TextUtility.number_to_string_formatted(total_sentences / bpd_total_entry_days, decimals=2) if bpd_total_entry_days else "0"
        words_per_day = UTILS.TextUtility.number_to_string_formatted(total_words / bpd_total_entry_days, decimals=2) if bpd_total_entry_days else "0"
        characters_per_day = UTILS.TextUtility.number_to_string_formatted(total_characters / bpd_total_entry_days, decimals=2) if bpd_total_entry_days else "0"

        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_day_avg_title"), [bpd_blocks_per_day, sentences_per_day, words_per_day, characters_per_day])

        if most_block_per_date is not None:
            most_day_entry_date = UTILS.DateTime.DateTimeObject(most_block_per_date["date"])
            most_day_entry_date_string = self.getl("week_day" + str(most_day_entry_date.DayOfWeek + 1)) + ", " + most_day_entry_date.DATE_formatted_string
            most_day_entry_before = self._period_before_formatted_string(UTILS.DateTime.DateTime.now() - most_day_entry_date)
            most_day_entry_blocks = UTILS.TextUtility.number_to_string_formatted(most_block_per_date["blocks"])
            most_day_entry_sentences = UTILS.TextUtility.number_to_string_formatted(most_block_per_date["sentences"])
            most_day_entry_words = UTILS.TextUtility.number_to_string_formatted(most_block_per_date["words"])
            most_day_entry_characters = UTILS.TextUtility.number_to_string_formatted(most_block_per_date["characters"])

            self.update_info_label(self.lbl_block_info, self.getl("statistic_block_day_avg_most_title"), [most_day_entry_date_string, most_day_entry_before, most_day_entry_blocks, most_day_entry_sentences, most_day_entry_words, most_day_entry_characters])


        # Tags, images and files in blocks
        if self.data["block"]["media"] is None:
            return
        
        self.update_info_label(self.lbl_block_info, "\n" + self.getl("statistic_block_tif_title"), fg_color="#ffff00")
        total_tags = 0
        blocks_with_tags = set()
        total_media = 0
        blocks_with_media = set()
        for item in self.data["block"]["media"]:
            if item[1]:
                total_tags += item[1]
                blocks_with_tags.add(item[0])
            if item[2]:
                total_media += item[2]
                blocks_with_media.add(item[0])
        blocks_with_tags_percent = UTILS.TextUtility.number_to_string_formatted((len(blocks_with_tags) / block_count) * 100, decimals=2) if block_count else "0"
        tags_avg_all = UTILS.TextUtility.number_to_string_formatted(total_tags / block_count, decimals=2) if block_count else "0"
        tags_avg = UTILS.TextUtility.number_to_string_formatted(total_tags / len(blocks_with_tags), decimals=2) if len(blocks_with_tags) else "0"
        blocks_with_media_percent = UTILS.TextUtility.number_to_string_formatted((len(blocks_with_media) / block_count) * 100, decimals=2) if block_count else "0"
        media_avg_all = UTILS.TextUtility.number_to_string_formatted(total_media / block_count, decimals=2) if block_count else "0"
        media_avg = UTILS.TextUtility.number_to_string_formatted(total_media / len(blocks_with_media), decimals=2) if len(blocks_with_media) else "0"
        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_tif_total_tags"), [UTILS.TextUtility.number_to_string_formatted(total_tags), tags_avg_all, UTILS.TextUtility.number_to_string_formatted(len(blocks_with_tags)), blocks_with_tags_percent, tags_avg])
        self.update_info_label(self.lbl_block_info, self.getl("statistic_block_tif_total_media"), [UTILS.TextUtility.number_to_string_formatted(total_media), media_avg_all, UTILS.TextUtility.number_to_string_formatted(len(blocks_with_media)), blocks_with_media_percent, media_avg])

        QCoreApplication.processEvents()

    def btn_def_clicked(self):
        if self.is_working:
            self._still_busy()
            return

        UTILS.LogHandler.add_log_record("#1: About to show #2 statistics.", ["Statistic", "definition"])
        self.hide_log_messages()

        self._frame_title_clicked(self.frm_def)

        if self.frm_def.height() == self.COLLAPSED_HEIGHT:
            return

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_def.setCursor(Qt.BusyCursor)
        self.frm_log.setFixedWidth = 120
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), self.getl("statistic_log_about_def"), fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_def_data()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), self.getl("statistic_log_about_def"), fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Displayed #2 statistics.", ["Statistic", "definition"])
            self.btn_def.setText(self.getl("statistic_btn_def_text") + f" ({len(self.data['def']['defs'])})")
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_def.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_def_data(self):
        # Database information
        self.update_log_frame(self.getl("statistic_log_block_db"))
        user_db_file_information = UTILS.FileUtility.get_FileInformation_object(self.get_appv("user").db_path)
        self.data["block"]["db_path"] = self.get_appv("user").db_path
        self.data["block"]["db"] = user_db_file_information
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_def_info_label()

        # Definition count
        self.update_log_frame(self.getl("statistic_log_def_count"))

        db_def = db_definition_cls.Definition(self._stt)
        def_list = db_def.get_complete_definitions_data()
        self.data["def"]["defs"] = def_list
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)

        self.update_log_frame(self.getl("statistic_log_def_update"))
        count = 0
        step = int(len(self.data["def"]["defs"]) / 20) if int(len(self.data["def"]["defs"]) / 20) > 0 else 1
        for def_item in self.data["def"]["defs"]:
            desc_sentences = UTILS.TextUtility.count_sentences(def_item[2])
            desc_words = UTILS.TextUtility.count_words(def_item[2])
            desc_chars = UTILS.TextUtility.count_chars(def_item[2])
            self.data["def"]["defs"][count].extend([desc_sentences, desc_words, desc_chars])

            if count % step == 0:
                self.update_log_frame(f'{count+1}/{len(self.data["def"]["defs"])}', fg_color="#00ffff", start_new_line=False, update_log_text=False)
            count += 1
        
        if self.data["def"]["defs"]:
            self.update_log_frame(f'{count+1}/{len(self.data["def"]["defs"])}', fg_color="#00ffff", start_new_line=False)

        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_def_info_label()

        return True

    def _populate_def_info_label(self):
        # Path
        self.update_info_label(self.lbl_def_info, self.getl("statistic_block_db_title"), fg_color="#ffff00", reset_label_text=True, start_new_line=False)
        value = self.data["block"]["db_path"] if self.data["block"]["db_path"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_def_info, self.getl("statistic_block_db_folder_path"), value)

        # Database information
        if self.data["block"]["db"] is not None:
            db_file: FileInformation = self.data["block"]["db"]
            db_size = db_file.size(return_formatted_string=True)
            db_created = db_file.created_time()
            db_created_before = self._period_before_formatted_string(db_file.created_before_period())
            db_modified = db_file.modification_time()
            db_modified_before = self._period_before_formatted_string(db_file.modified_before_period())
            db_accessed = db_file.access_time()
            db_accessed_before = self._period_before_formatted_string(db_file.accessed_before_period())
            self.update_info_label(self.lbl_def_info, self.getl("statistic_block_db_info"), [db_size, db_created, db_created_before, db_modified, db_modified_before, db_accessed, db_accessed_before])

        if self.data["def"]["defs"] is None:
            QCoreApplication.processEvents()
            return

        # Totals
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_title"), fg_color="#ffff00")

        total_defs = len(self.data["def"]["defs"])
        total_syn = 0
        total_img = 0
        most_syn = 0
        most_syn_string = ""
        most_img = 0
        most_img_string = ""
        defs_without_default_image = []

        defs_without_syn = 0
        defs_without_img = 0
        unique_syn = set()
        unique_img = set()

        total_desc_sentences = 0
        total_desc_words = 0
        total_desc_chars = 0
        most_desc_size = None
        defs_without_desc = []

        for definition in self.data["def"]["defs"]:
            total_syn += len(definition[3])
            if len(definition[3]) > most_syn:
                most_syn = len(definition[3])
                most_syn_string = f"(ID:{definition[0]}) {definition[1]}"

            total_img += len(definition[4])
            if len(definition[4]) > most_img:
                most_img = len(definition[4])
                most_img_string = f"(ID:{definition[0]}) {definition[1]}"
            
            if not definition[5] and len(definition[4]):
                defs_without_default_image.append([definition[0], definition[1]])
            
            if len(definition[3]) <= 1:
                defs_without_syn += 1

            if not len(definition[4]):
                defs_without_img += 1

            unique_syn.update(definition[3])
            unique_img.update(definition[4])

            desc_sentences = definition[6]
            desc_words = definition[7]
            desc_chars = definition[8]
            total_desc_sentences += desc_sentences
            total_desc_words += desc_words
            total_desc_chars += desc_chars
            if most_desc_size is None or desc_chars > most_desc_size["chars"]:
                most_desc_size  = {
                    "id": definition[0],
                    "name": definition[1],
                    "sentences": desc_sentences,
                    "words": desc_words,
                    "chars": desc_chars
                }
            if desc_words == 0:
                defs_without_desc.append([definition[0], definition[1]])

        avg_desc_chars = total_desc_chars / total_defs if total_defs > 0 else 0
        if most_desc_size is not None:
            most_desc_size["sentences_str"] = UTILS.TextUtility.number_to_string_formatted(most_desc_size["sentences"])
            most_desc_size["words_str"] = UTILS.TextUtility.number_to_string_formatted(most_desc_size["words"])
            most_desc_size["chars_str"] = UTILS.TextUtility.number_to_string_formatted(most_desc_size["chars"])
            most_desc_size["more_str"] = UTILS.TextUtility.percent_more_than_average_formatted_string(most_desc_size["chars"], avg_desc_chars, decimals=0)
        
        avg_syn = total_syn / total_defs if total_defs > 0 else 0
        avg_img = total_img / total_defs if total_defs > 0 else 0
        most_syn_avg_more = UTILS.TextUtility.percent_more_than_average_formatted_string(most_syn, avg_syn)
        most_img_avg_more = UTILS.TextUtility.percent_more_than_average_formatted_string(most_img, avg_img)
        repeated_syn = total_syn - len(unique_syn)
        repeated_img = total_img - len(unique_img)

        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_totals"), [UTILS.TextUtility.number_to_string_formatted(total_defs), UTILS.TextUtility.number_to_string_formatted(total_syn), UTILS.TextUtility.number_to_string_formatted(total_img)])
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_most_syn"), [most_syn_string, UTILS.TextUtility.number_to_string_formatted(most_syn), UTILS.TextUtility.number_to_string_formatted(most_syn_avg_more)])
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_most_img"), [most_img_string, UTILS.TextUtility.number_to_string_formatted(most_img), UTILS.TextUtility.number_to_string_formatted(most_img_avg_more)])

        # Average
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_avg_title"), fg_color="#ffff00")

        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_avg"), [UTILS.TextUtility.number_to_string_formatted(avg_syn, decimals=2), UTILS.TextUtility.number_to_string_formatted(avg_img, decimals=2)])

        # Synonyms
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_syn_title"), fg_color="#ffff00")

        defs_without_syn_percent_z = defs_without_syn / total_defs if total_defs else 0
        repeated_syn_percent_z = repeated_syn / total_syn if total_syn else 0
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn"), [UTILS.TextUtility.number_to_string_formatted(defs_without_syn), UTILS.TextUtility.number_to_string_formatted((defs_without_syn_percent_z) * 100, decimals=2)])
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_avg"), [UTILS.TextUtility.number_to_string_formatted(avg_syn, decimals=2)])
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_repeated"), [UTILS.TextUtility.number_to_string_formatted(repeated_syn), UTILS.TextUtility.number_to_string_formatted((repeated_syn_percent_z) * 100, decimals=2)])

        # Descriptions
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_desc_title"), fg_color="#ffff00")

        if defs_without_desc:
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_desc"), [UTILS.TextUtility.number_to_string_formatted(len(defs_without_desc)), UTILS.TextUtility.number_to_string_formatted((len(defs_without_desc) / total_defs) * 100, decimals=2)])
        else:
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_desc_no_without_desc"))
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_desc_total"), [UTILS.TextUtility.number_to_string_formatted(total_desc_sentences), UTILS.TextUtility.number_to_string_formatted(total_desc_words), UTILS.TextUtility.number_to_string_formatted(total_desc_chars)])
        total_desc_sentences_z = total_desc_sentences / total_defs if total_defs else 0
        total_desc_words_z = total_desc_words / total_defs if total_defs else 0
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_desc_avg"), [UTILS.TextUtility.number_to_string_formatted(total_desc_sentences_z), UTILS.TextUtility.number_to_string_formatted(total_desc_words_z), UTILS.TextUtility.number_to_string_formatted(avg_desc_chars)])
        if most_desc_size:
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_desc_avg_most"), [most_desc_size["id"], most_desc_size["name"], most_desc_size["sentences_str"], most_desc_size["words_str"], most_desc_size["chars_str"], most_desc_size["more_str"]])

        # Images
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_img_title"), fg_color="#ffff00")

        defs_without_img_z = defs_without_img / total_defs if total_defs else 0
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_img"), [UTILS.TextUtility.number_to_string_formatted(defs_without_img), UTILS.TextUtility.number_to_string_formatted((defs_without_img_z) * 100, decimals=2)])
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_img_avg"), [UTILS.TextUtility.number_to_string_formatted(avg_img, decimals=2)])
        repeated_img_z = repeated_img / total_img if total_img else 0
        self.update_info_label(self.lbl_def_info, self.getl("statistic_def_img_repeated"), [UTILS.TextUtility.number_to_string_formatted(repeated_img), UTILS.TextUtility.number_to_string_formatted((repeated_img_z) * 100, decimals=2)])

        # Default image in definitions
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_default_img_title"), fg_color="#ffff00")

        if defs_without_default_image:
            defs_without_default_image_z = len(defs_without_default_image) / total_defs if total_defs else 0
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_default_img"), [UTILS.TextUtility.number_to_string_formatted(len(defs_without_default_image)), UTILS.TextUtility.number_to_string_formatted((defs_without_default_image_z) * 100, decimals=2)])
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_default_img_list"))
            count = 0
            for image in defs_without_default_image:
                self.update_info_label(self.lbl_def_info, "#1", [f"ID={image[0]}"], fg_color="#ff5500")
                self.update_info_label(self.lbl_def_info, f" - {image[1]}", fg_color="#ff5500", start_new_line=False)
                if count >= 4 and len(defs_without_default_image) > 5:
                    break
                count += 1
            if len(defs_without_default_image) > 5:
                self.update_info_label(self.lbl_def_info, self.getl("statistic_def_default_img_more"), [UTILS.TextUtility.number_to_string_formatted(len(defs_without_default_image) - 5)])
        else:
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_default_img_none"))

        # Serbian characters in synonyms
        self.update_info_label(self.lbl_def_info, "\n" + self.getl("statistic_def_syn_sr_title"), fg_color="#ffff00")
        self.update_log_frame(self.getl("statistic_log_def_syn_sr"))

        total_sr_syn = 0
        total_sr_def = 0
        most_sr_syn = {"count": 0}
        most_miss_sr_syn = {"count": 0}
        miss_sr_syn = []
        for definition in self.data["def"]["defs"]:
            synonyms = definition[3]
            sr_syn_count = 0
            missed_syn = []
            synonyms_with_sr = []
            for synonym in synonyms:
                syn_cleared = UTILS.TextUtility.clear_serbian_chars(synonym)
                if syn_cleared != synonym and definition[1].lower() != synonym:
                    sr_syn_count += 1
                    synonyms_with_sr.append(synonym)
                    if syn_cleared not in synonyms:
                        missed_syn.append(synonym)

            if sr_syn_count > 0:
                total_sr_syn += sr_syn_count
                total_sr_def += 1
                if sr_syn_count > most_sr_syn["count"]:
                    most_sr_syn = {
                        "count": sr_syn_count,
                        "id": definition[0],
                        "name": definition[1],
                        "synonyms": synonyms_with_sr,
                        "miss": missed_syn
                    }

                if missed_syn:
                    if most_miss_sr_syn["count"] < len(missed_syn):
                        most_miss_sr_syn = {
                            "count": len(missed_syn),
                            "id": definition[0],
                            "name": definition[1],
                            "synonyms": synonyms_with_sr,
                            "miss": missed_syn
                        }

                    miss_sr_syn.append({
                        "id": definition[0],
                        "count": sr_syn_count,
                        "name": definition[1],
                        "synonyms": synonyms_with_sr,
                        "miss": missed_syn
                    })

        miss_sr_syn = sorted(miss_sr_syn, key=lambda x: len(x["miss"]), reverse=True)

        if total_sr_def:
            total_sr_syn_str = UTILS.TextUtility.number_to_string_formatted(total_sr_syn)
            total_sr_def_str = UTILS.TextUtility.number_to_string_formatted(total_sr_def)
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_sr"), [total_sr_def_str, total_sr_syn_str, UTILS.TextUtility.percent_formatted_string(total_defs, total_sr_def, decimals=1), UTILS.TextUtility.number_to_string_formatted(total_syn), total_sr_syn_str, UTILS.TextUtility.percent_formatted_string(total_syn, total_sr_syn, decimals=1)])
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_sr_most"), [f'ID={most_sr_syn["id"]}', most_sr_syn["name"], UTILS.TextUtility.number_to_string_formatted(most_sr_syn["count"])])

            if miss_sr_syn:
                self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_sr_miss"), [
                    UTILS.TextUtility.number_to_string_formatted(len(miss_sr_syn)),
                    UTILS.TextUtility.number_to_string_formatted(sum([len(x["miss"]) for x in miss_sr_syn])),
                    f'ID={most_miss_sr_syn["id"]}',
                    most_miss_sr_syn["name"],
                    UTILS.TextUtility.number_to_string_formatted(len(most_miss_sr_syn["miss"]))
                ])

                self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_sr_miss_list_title"), fg_color="#ff5500")

                count = 0
                step = int(len(miss_sr_syn) / 100) if int(len(miss_sr_syn) / 100) > 0 else 1
                for miss in miss_sr_syn:
                    self.update_info_label(self.lbl_def_info, "#1", [f"ID={miss['id']}"], fg_color="#d8a0ff")
                    self.update_info_label(self.lbl_def_info, f" - {miss['name']}", fg_color="#d8a0ff", start_new_line=False)
                    self.update_info_label(self.lbl_def_info, " (#1) #2", [UTILS.TextUtility.number_to_string_formatted(len(miss["miss"])), str(miss["miss"])], start_new_line=False)
                    if count % step == 0:
                        self.update_log_frame(f'{count+1}/{len(miss_sr_syn)}', fg_color="#00ffff", start_new_line=False, update_log_text=False)
                    count += 1
            else:
                self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_sr_miss_none"))
        else:
            self.update_info_label(self.lbl_def_info, self.getl("statistic_def_syn_sr_none"))

        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)

        QCoreApplication.processEvents()

    def btn_tag_clicked(self):
        if self.is_working:
            self._still_busy()
            return

        UTILS.LogHandler.add_log_record("#1: About to show #2 statistics.", ["Statistic", "tag"])
        self.hide_log_messages()

        self._frame_title_clicked(self.frm_tag)

        if self.frm_tag.height() == self.COLLAPSED_HEIGHT:
            return

        self.is_working += 1
        # Change cursor arrow with hourglass
        self.frm_tag.setCursor(Qt.BusyCursor)
        self.frm_log.setFixedWidth = 120
        self.show_log_messages()

        self.update_log_frame(self.getl("statistic_log_started"), self.getl("statistic_log_about_tag"), fg_color="#ffff00", start_new_line=False, reset_log_text=True)
        result = self._populate_tag_data()
        self.is_working -= 1
        self.abort_action = False
        if result:
            self.update_log_frame(self.getl("statistic_log_finished"), self.getl("statistic_log_about_tag"), fg_color="#ffff00")
            UTILS.LogHandler.add_log_record("#1: Displayed #2 statistics.", ["Statistic", "tag"])
            self.btn_tag.setText(self.getl("statistic_btn_tag_text") + f" ({len(self.data['tag']['tags'])})")
            self.log_timer.start()
            self.log_frame_finished_working(success=True)
        else:
            self.update_log_frame(self.getl("statistic_log_aborted"), fg_color="#ff0000")
            UTILS.LogHandler.add_log_record("#1: User aborted calculation.", ["Statistic"])
            self.log_frame_finished_working(success=False)
        
        self.frm_tag.setCursor(QCursor(Qt.ArrowCursor))

    def _populate_tag_data(self):
        # Database information
        self.update_log_frame(self.getl("statistic_log_block_db"))
        user_db_file_information = UTILS.FileUtility.get_FileInformation_object(self.get_appv("user").db_path)
        self.data["block"]["db_path"] = self.get_appv("user").db_path
        self.data["block"]["db"] = user_db_file_information
        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_tag_info_label()

        # Tag count
        self.update_log_frame(self.getl("statistic_log_tag_count"))

        db_tag = db_tag_cls.Tag(self._stt)
        tag_list = db_tag.get_all_tags_translated()

        self.data["tag"]["tags"] = []

        for tag in tag_list:
            item = {
                "id": tag[0],
                "name": tag[1],
                "desc": tag[3],
                "user": False if tag[2] == 0 else True,
                "used": db_tag.how_many_times_is_used(tag[0])
            }

            self.data["tag"]["tags"].append(item)

        db_block = db_record_cls.Record(self._stt)
        block_count = len(db_block.get_all_records())

        self.data["tag"]["block_count"] = block_count

        self.update_log_frame(self.getl("statistic_log_done"), fg_color="#aaff7f", start_new_line=False)
        self._populate_tag_info_label()

        return True

    def _populate_tag_info_label(self):
        # Path
        self.update_info_label(self.lbl_tag_info, self.getl("statistic_block_db_title"), fg_color="#ffff00", reset_label_text=True, start_new_line=False)
        value = self.data["block"]["db_path"] if self.data["block"]["db_path"] is not None else self.WAITING_FOR_DATA
        self.update_info_label(self.lbl_tag_info, self.getl("statistic_block_db_folder_path"), value)

        # Database information
        if self.data["block"]["db"] is not None:
            db_file: FileInformation = self.data["block"]["db"]
            db_size = db_file.size(return_formatted_string=True)
            db_created = db_file.created_time()
            db_created_before = self._period_before_formatted_string(db_file.created_before_period())
            db_modified = db_file.modification_time()
            db_modified_before = self._period_before_formatted_string(db_file.modified_before_period())
            db_accessed = db_file.access_time()
            db_accessed_before = self._period_before_formatted_string(db_file.accessed_before_period())
            self.update_info_label(self.lbl_tag_info, self.getl("statistic_block_db_info"), [db_size, db_created, db_created_before, db_modified, db_modified_before, db_accessed, db_accessed_before])

        if self.data["tag"]["tags"] is None:
            QCoreApplication.processEvents()
            return

        # Totals
        self.update_info_label(self.lbl_tag_info, "\n" + self.getl("statistic_tag_title"), fg_color="#ffff00")

        total_tags = len(self.data["tag"]["tags"])
        app_tags = 0

        for tag in self.data["tag"]["tags"]:
            if not tag["user"]:
                app_tags += 1
        
        user_tags = total_tags - app_tags
        block_count = self.data["tag"]["block_count"] if self.data["tag"]["block_count"] else 1
        user_tags_percent = (user_tags / total_tags) * 100
        user_tags_percent_str = UTILS.TextUtility.number_to_string_formatted(user_tags_percent, decimals=2)

        self.update_info_label(self.lbl_tag_info, self.getl("statistic_tag_info"), [UTILS.TextUtility.number_to_string_formatted(total_tags), UTILS.TextUtility.number_to_string_formatted(app_tags), UTILS.TextUtility.number_to_string_formatted(user_tags), user_tags_percent_str])

        self.update_info_label(self.lbl_tag_info, "\n" + self.getl("statistic_tag_in_blocks_title"), fg_color="#ffff00")

        self.update_info_label(self.lbl_tag_info, self.getl("statistic_tag_in_blocks_app"))

        count = 1
        for tag in self.data["tag"]["tags"]:
            if tag["user"]:
                continue

            tag_id_str = str(tag["id"])
            tag_name = tag["name"]
            tag_user = self.getl("statistic_tag_user_mark") if tag["user"] else self.getl("statistic_tag_app_mark")
            tag_used = UTILS.TextUtility.number_to_string_formatted(tag["used"])
            tag_used_block_percent_str = UTILS.TextUtility.number_to_string_formatted((tag["used"] / block_count) * 100, decimals=2)

            self.update_info_label(self.lbl_tag_info, self.getl("statistic_tag_in_blocks_info"), [count, tag_id_str, tag_name, tag_user, tag_used, tag_used_block_percent_str])

            count += 1

        self.update_info_label(self.lbl_tag_info, self.getl("statistic_tag_in_blocks_user"))

        count = 1
        for tag in self.data["tag"]["tags"]:
            if not tag["user"]:
                continue
            
            tag_id_str = str(tag["id"])
            tag_name = tag["name"]
            tag_user = self.getl("statistic_tag_user_mark") if tag["user"] else self.getl("statistic_tag_app_mark")
            tag_used = UTILS.TextUtility.number_to_string_formatted(tag["used"])
            tag_used_block_percent_str = UTILS.TextUtility.number_to_string_formatted((tag["used"] / block_count) * 100, decimals=2)

            self.update_info_label(self.lbl_tag_info, self.getl("statistic_tag_in_blocks_info"), [count, tag_id_str, tag_name, tag_user, tag_used, tag_used_block_percent_str])

            count += 1

        QCoreApplication.processEvents()

    def _still_busy(self) -> None:
        self.frm_log.setVisible(True)
        self.frm_log.raise_()
        self.frm_log.setStyleSheet(self.getv("statistic_frm_log_busy_stylesheet"))
        self.busy_timer.start()
        self.sound_busy.play()

    def busy_timer_finished(self, timer: SingleShotTimer) -> None:
        self.frm_log.setStyleSheet(self.getv("statistic_frm_log_stylesheet"))
        self.busy_timer.stop()

    def _get_empty_data_dict(self):
        return {
            "app": {
                "path": None,
                "files": None,
                "sizes": None,
                "oldest_file": None,
                "newest_file": None,
                "oldest_modified_file": None,
                "newest_modified_file": None,
                "oldest_accessed_file": None,
                "newest_accessed_file": None,
                "file_content": None
            },
            "block": {
                "db_path": None,
                "db": None,
                "blocks": None,
                "dates": None,
                "media": None
            },
            "def": {
                "db_path": None,
                "db": None,
                "defs": None
            },
            "tag": {
                "tags": None
            },
            "img": {
                "path": None,
                "files": None,
                "sizes": None,
                "oldest_file": None,
                "newest_file": None,
                "oldest_modified_file": None,
                "newest_modified_file": None,
                "oldest_accessed_file": None,
                "newest_accessed_file": None,
                "file_types": {}
            },
            "file": {
                "path": None,
                "files": None,
                "sizes": None,
                "oldest_file": None,
                "newest_file": None,
                "oldest_modified_file": None,
                "newest_modified_file": None,
                "oldest_accessed_file": None,
                "newest_accessed_file": None,
                "file_types": {}
            },
            "log": {
                "text": ""
            },
            "info": {
                self.lbl_app_info.objectName(): ""
            }
        }

    def _period_before_formatted_string(self, period: Period) -> str:
        text = ""

        text_years = ""
        if period.years > 0:
            if period.years > 1:
                text_years = f"{period.years} {self.getl('years')}"
            else:
                text_years = f"{period.years} {self.getl('year')}"
        
        text_months = ""
        if period.months > 0:
            if period.months > 1:
                text_months = f"{period.months} {self.getl('months')}"
            else:
                text_months = f"{period.months} {self.getl('month')}"
        
        text_days = ""
        if period.days > 0:
            if period.days > 1:
                text_days = f"{period.days} {self.getl('days')}"
            else:
                text_days = f"{period.days} {self.getl('day')}"
        
        if text_years or text_months or text_days:
            if text_years and text_months and text_days:
                text = f"{text_years}, {text_months} {self.getl('and')} {text_days}"
                return text
            if text_years:
                text = text_years
            if text_months:
                if text:
                    text += f" {self.getl('and')} {text_months}"
                else:
                    text = text_months
            if text_days:
                if text:
                    text += f" {self.getl('and')} {text_days}"
                else:
                    text = text_days
            
            return text
        
        text_hour = ""
        if period.hours > 0:
            if period.hours > 1:
                text_hour = f"{period.hours} {self.getl('hours')}"
            else:
                text_hour = f"{period.hours} {self.getl('hour')}"

        text_minute = ""
        if period.minutes > 0:
            if period.minutes > 1:
                text_minute = f"{period.minutes} {self.getl('minutes')}"
            else:
                text_minute = f"{period.minutes} {self.getl('minute')}"

        text_second = ""
        if period.seconds > 0:
            if period.seconds > 1:
                text_second = f"{period.seconds} {self.getl('seconds')}"
            else:
                text_second = f"{period.seconds} {self.getl('second')}"

        if text_hour or text_minute or text_second:
            if text_hour and text_minute and text_second:
                text = f"{text_hour}, {text_minute} {self.getl('and')} {text_second}"
                return text
            if text_hour:
                text = text_hour
            if text_minute:
                if text:
                    text += f" {self.getl('and')} {text_minute}"
                else:
                    text = text_minute
            if text_second:
                if text:
                    text += f" {self.getl('and')} {text_second}"
                else:
                    text = text_second
            
            return text
        
        return "???"

    def _frame_title_clicked(self, section_frame: QFrame):
        if section_frame.height() != self.COLLAPSED_HEIGHT:
            section_frame.setFixedHeight(self.COLLAPSED_HEIGHT)
            self.resize_section_frame(section_frame)
            return
        section_frame.setFixedHeight(self.COLLAPSED_HEIGHT + 1)
        self.resize_section_frame(section_frame)

    def _key_press_event(self, btn: QtGui.QKeyEvent):
        if btn.key() == Qt.Key_Escape:
            if self.is_working:
                btn.accept()
                self.abort_action = True
                return None
            if self.frm_log.isVisible():
                btn.accept()
                self.btn_log_close_clicked()
                return None
            else:
                self.close()

    def resize_section_frame(self, section_frame: QFrame) -> int:
        area_widget_width = self.area_widget.width()

        if section_frame.objectName().endswith("_kw"):
            section_frame = self.findChild(QFrame, section_frame.objectName()[:-3])
        
        section_frame.setFixedWidth(area_widget_width)

        w = section_frame.width()
        h = self.COLLAPSED_HEIGHT

        # Section title button
        for child in section_frame.children():
            if isinstance(child, QPushButton):
                section_title_button = child
                break
        else:
            UTILS.LogHandler.add_log_record("#1: Exception in #2. Section title button not found.", ["Statistic", "resize_section_frame"], exception_raised=True)
            raise Exception("Section title button not found")
        
        section_title_button.setFixedWidth(w - 20)

        # If frame is collapsed, return collapsed height
        if section_frame.height() == self.COLLAPSED_HEIGHT:
            section_frame.setStyleSheet(self.getv("statistic_section_frm_collapsed_stylesheet"))
            section_frame.setFixedHeight(self.COLLAPSED_HEIGHT)
            return self.COLLAPSED_HEIGHT
        
        section_frame.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))

        # Info label
        for child in section_frame.children():
            if "QLabel" in str(type(child)):
                section_info_label = child
                break
        else:
            UTILS.LogHandler.add_log_record("#1: Exception in #2. Info label not found.", ["Statistic", "resize_section_frame"], exception_raised=True)
            raise Exception("Info label not found")
        
        section_info_label.setFixedWidth(w - 20)
        section_info_label.adjustSize()
        h += section_info_label.height()
        h += 10

        # Section search frame
        for child in section_frame.children():
            if "QFrame" in str(type(child)):
                section_search_frame = child
                break
        else:
            section_frame.setFixedHeight(h)
            return h
        
        section_search_frame.move(10, h)
        section_search_frame.setFixedWidth(section_frame.width() - 20)

        # Search textbox
        for child in section_search_frame.children():
            if "QLineEdit" in str(type(child)):
                search_line_edit = child
                break
        else:
            section_frame.setFixedHeight(h)
            UTILS.LogHandler.add_log_record("#1: Warning in #2. Search textbox not found.", ["Statistic", "resize_section_frame"], warning_raised=True)
            return h
        
        search_line_edit.setFixedWidth(section_search_frame.width() - 50)

        # Search button
        for child in section_search_frame.children():
            if "QPushButton" in str(type(child)):
                search_button = child
                break
        else:
            section_frame.setFixedHeight(h)
            UTILS.LogHandler.add_log_record("#1: Warning in #2. Search button not found.", ["Statistic", "resize_section_frame"], warning_raised=True)
            return h
        
        search_button.move(search_line_edit.pos().x() + search_line_edit.width() + 10, 10)

        # Search info label
        for child in section_search_frame.children():
            if "QLabel" in str(type(child)):
                search_info_label = child
                break
        else:
            section_frame.setFixedHeight(h)
            UTILS.LogHandler.add_log_record("#1: Warning in #2. Search info label not found.", ["Statistic", "resize_section_frame"], warning_raised=True)
            return h
        
        search_info_label.setFixedWidth(section_search_frame.width() - 20)
        search_info_label.adjustSize()

        section_search_frame.setFixedHeight(search_info_label.pos().y() + search_info_label.height() + 10)

        h += section_search_frame.height()
        h += 10
        section_frame.setFixedHeight(h)

        return h

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
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_app_kw)
        self.widget_handler.add_TextBox(self.txt_block_kw)
        self.widget_handler.add_TextBox(self.txt_def_kw)

        # Add Selection Widgets

        # Add Item Based Widgets

        self.widget_handler.activate()

    def resizeEvent(self, a0: QtGui.QResizeEvent | None) -> None:
        self.resize_me()
        return super().resizeEvent(a0)

    def resize_me(self):
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        
        self.lbl_title.resize(w - 20, self.lbl_title.height())

        self.area.move(10, 90)
        self.area.resize(w - 20, h - 100)
        self.area_widget.setFixedWidth(self.area.width())

        self.resize_section_frame(self.frm_app)
        self.resize_section_frame(self.frm_block)
        self.resize_section_frame(self.frm_def)
        self.resize_section_frame(self.frm_tag)
        self.resize_section_frame(self.frm_img)
        self.resize_section_frame(self.frm_file)

    def _load_win_position(self):
        if "statistic_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("statistic_win_geometry")
            self.move(g["pos_x"], g["pos_y"])
            self.resize(g["width"], g["height"])

            self.txt_app_kw.setText(g.get("app_kw", ""))
            self.txt_block_kw.setText(g.get("block_kw", ""))
            self.txt_def_kw.setText(g.get("def_kw", ""))

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.is_working:
            self.abort_action = True
            a0.ignore()
            return
        
        if self.frm_log.isVisible():
            self.log_timer.stop()
            self.frm_log.setVisible(False)
            a0.ignore()
            return

        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "statistic_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("statistic_win_geometry", {}, save_to_file=True)

        g = self.get_appv("statistic_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        g["app_kw"] = self.txt_app_kw.text()
        g["block_kw"] = self.txt_block_kw.text()
        g["def_kw"] = self.txt_def_kw.text()

        self.get_appv("cm").remove_all_context_menu()

        self.log_timer.stop()
        self.log_timer.close_me()
        self.busy_timer.stop()
        self.busy_timer.close_me()
        self.sound_busy = None
        
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["Statistic"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _setup_widgets(self):
        # Area
        self.area = QScrollArea(self)
        self.area.setWidgetResizable(True)
        self.area_widget = QWidget()
        self.area_widget_layout = QVBoxLayout()
        self.area_widget.setLayout(self.area_widget_layout)
        self.area.setWidget(self.area_widget)

        self.area.setContentsMargins(0, 0, 0, 0)
        self.area.setViewportMargins(0, 0, 0, 0)
        self.area_widget.setContentsMargins(0, 0, 0, 0)
        self.area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.area_widget_layout.setSpacing(10)

        # Set area policy to no vertical scroll bar and no horizontal scroll bar
        self.area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Title
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")

        # Application
        self.frm_app: QFrame = self.findChild(QFrame, "frm_app")
        self.frm_app.setParent(self.area_widget)
        self.btn_app: QPushButton = self.findChild(QPushButton, "btn_app")
        self.lbl_app_info: QLabel = self.findChild(QLabel, "lbl_app_info")
        self.frm_app_kw: QFrame = self.findChild(QFrame, "frm_app_kw")
        self.txt_app_kw: QLineEdit = self.findChild(QLineEdit, "txt_app_kw")
        self.btn_app_kw: QPushButton = self.findChild(QPushButton, "btn_app_kw")
        self.lbl_app_info_kw: QLabel = self.findChild(QLabel, "lbl_app_info_kw")
        # Block
        self.frm_block: QFrame = self.findChild(QFrame, "frm_block")
        self.frm_block.setParent(self.area_widget)
        self.btn_block: QPushButton = self.findChild(QPushButton, "btn_block")
        self.lbl_block_info: QLabel = self.findChild(QLabel, "lbl_block_info")
        self.frm_block_kw: QFrame = self.findChild(QFrame, "frm_block_kw")
        self.txt_block_kw: QLineEdit = self.findChild(QLineEdit, "txt_block_kw")
        self.btn_block_kw: QPushButton = self.findChild(QPushButton, "btn_block_kw")
        self.lbl_block_info_kw: QLabel = self.findChild(QLabel, "lbl_block_info_kw")
        # Definition
        self.frm_def: QFrame = self.findChild(QFrame, "frm_def")
        self.frm_def.setParent(self.area_widget)
        self.btn_def: QPushButton = self.findChild(QPushButton, "btn_def")
        self.lbl_def_info: QLabel = self.findChild(QLabel, "lbl_def_info")
        self.frm_def_kw: QFrame = self.findChild(QFrame, "frm_def_kw")
        self.txt_def_kw: QLineEdit = self.findChild(QLineEdit, "txt_def_kw")
        self.btn_def_kw: QPushButton = self.findChild(QPushButton, "btn_def_kw")
        self.lbl_def_info_kw: QLabel = self.findChild(QLabel, "lbl_def_info_kw")
        # Image
        self.frm_img: QFrame = self.findChild(QFrame, "frm_img")
        self.frm_img.setParent(self.area_widget)
        self.btn_img: QPushButton = self.findChild(QPushButton, "btn_img")
        self.lbl_img_info: QLabel = self.findChild(QLabel, "lbl_img_info")
        # File
        self.frm_file: QFrame = self.findChild(QFrame, "frm_file")
        self.frm_file.setParent(self.area_widget)
        self.btn_file: QPushButton = self.findChild(QPushButton, "btn_file")
        self.lbl_file_info: QLabel = self.findChild(QLabel, "lbl_file_info")
        # Tag
        self.frm_tag: QFrame = self.findChild(QFrame, "frm_tag")
        self.frm_tag.setParent(self.area_widget)
        self.btn_tag: QPushButton = self.findChild(QPushButton, "btn_tag")
        self.lbl_tag_info: QLabel = self.findChild(QLabel, "lbl_tag_info")

        # Log
        self.frm_log: QFrame = self.findChild(QFrame, "frm_log")
        self.lbl_log: QLabel = self.findChild(QLabel, "lbl_log")
        self.btn_log_close: QPushButton = self.findChild(QPushButton, "btn_log_close")

    def _setup_widgets_text(self):
        # Title
        self.lbl_title.setText(self.getl("statistic_lbl_title_text"))
        # Application
        self.btn_app.setText(self.getl("statistic_btn_app_text"))
        self.btn_app.setToolTip(self.getl("statistic_btn_app_tt"))
        self.lbl_app_info.setText(self.getl("statistic_lbl_app_info_text"))
        self.txt_app_kw.setPlaceholderText(self.getl("statistic_txt_app_kw_ph"))
        self.btn_app_kw.setToolTip(self.getl("statistic_btn_app_kw_tt"))
        self.lbl_app_info_kw.setText(self.getl("statistic_lbl_app_info_kw_text"))
        # Block
        self.btn_block.setText(self.getl("statistic_btn_block_text"))
        self.btn_block.setToolTip(self.getl("statistic_btn_block_tt"))
        self.lbl_block_info.setText(self.getl("statistic_lbl_block_info_text"))
        self.txt_block_kw.setPlaceholderText(self.getl("statistic_txt_block_kw_ph"))
        self.btn_block_kw.setToolTip(self._format_tooltip(self.getl("statistic_btn_block_kw_tt")))
        self.lbl_block_info_kw.setText(self.getl("statistic_lbl_block_info_kw_text"))
        # Definition
        self.btn_def.setText(self.getl("statistic_btn_def_text"))
        self.btn_def.setToolTip(self.getl("statistic_btn_def_tt"))
        self.lbl_def_info.setText(self.getl("statistic_lbl_def_info_text"))
        self.txt_def_kw.setPlaceholderText(self.getl("statistic_txt_def_kw_ph"))
        self.btn_def_kw.setToolTip(self._format_tooltip(self.getl("statistic_btn_def_kw_tt")))
        self.lbl_def_info_kw.setText(self.getl("statistic_lbl_def_info_kw_text"))
        # Image
        self.btn_img.setText(self.getl("statistic_btn_img_text"))
        self.btn_img.setToolTip(self.getl("statistic_btn_img_tt"))
        self.lbl_img_info.setText(self.getl("statistic_lbl_img_info_text"))
        # File
        self.btn_file.setText(self.getl("statistic_btn_file_text"))
        self.btn_file.setToolTip(self.getl("statistic_btn_file_tt"))
        self.lbl_file_info.setText(self.getl("statistic_lbl_file_info_text"))
        # Tag
        self.btn_tag.setText(self.getl("statistic_btn_tag_text"))
        self.btn_tag.setToolTip(self.getl("statistic_btn_tag_tt"))
        self.lbl_tag_info.setText(self.getl("statistic_lbl_tag_info_text"))
        # Log
        self.lbl_log.setText("")
        self.btn_log_close.setText(self.getl("close"))

    def _format_tooltip(self, text: str) -> str:
        HEAD_COLOR = "#ffffff"
        SECTION_COLOR = "#ffff00"
        EXAMPLE_COLOR = "#55ffff"
        SUB_SECTION_COLOR = "#ffaa7f"
        NORMAL_COLOR = "#55ff00"
        TITLE_FONT_SIZE = 16
        SECTION_TITLE_FONT_SIZE = 18
        NORMAL_FONT_SIZE = 14
        EXAMPLE_FONT_SIZE = 16

        html_text = UTILS.HTMLText.TextToHTML()
        html_text.general_rule.fg_color = NORMAL_COLOR
        html_text.general_rule.font_size = NORMAL_FONT_SIZE
        
        text_to_format = ""
        is_title = True
        count = 1
        for line in text.split("\n"):
            if is_title:
                rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text=rule_id,
                    replace_with=line,
                    fg_color=HEAD_COLOR,
                    font_size=TITLE_FONT_SIZE
                )
                html_text.add_rule(rule)
                is_title = False
                count += 1
                text_to_format += rule_id + "\n"
                continue

            if line.startswith('"') and line.endswith('"'):
                rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text=rule_id,
                    replace_with=line,
                    fg_color=EXAMPLE_COLOR,
                    font_size=EXAMPLE_FONT_SIZE
                )
                html_text.add_rule(rule)
                count += 1
                text_to_format += rule_id + "\n"
                continue

            if line.startswith("(") and line.endswith(")"):
                rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text=rule_id,
                    replace_with=line,
                    fg_color=SUB_SECTION_COLOR
                )
                html_text.add_rule(rule)
                count += 1
                text_to_format += rule_id + "\n"
                continue

            if line == line.upper():
                rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
                rule = UTILS.HTMLText.TextToHtmlRule(
                    text=rule_id,
                    replace_with=line,
                    fg_color=SECTION_COLOR,
                    font_size=SECTION_TITLE_FONT_SIZE,
                    font_bold=True
                )
                html_text.add_rule(rule)
                count += 1
                text_to_format += rule_id + "\n"
                continue

            text_to_format += line + "\n"

        html_text.set_text(text_to_format)

        return html_text.get_html()

    def app_setting_updated(self, data: dict):
        UTILS.LogHandler.add_log_record("#1: Application settings updated.", ["ExportImport"])
        self._setup_widgets_appearance(updating=True)

    def _setup_widgets_appearance(self, updating: bool = False):
        # Dialog
        self.setStyleSheet(self.getv("statistic_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("statistic_win_icon_path")))
        self.setWindowTitle(self.getl("statistic_lbl_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setMinimumSize(250, 150)

        # Area
        self.area.setStyleSheet(self.getv("statistic_area_stylesheet"))
        self.area_widget.setStyleSheet(self.getv("statistic_area_widget_stylesheet"))
        if not updating:
            spacer = QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.area_widget_layout.addWidget(self.frm_app)
            self.area_widget_layout.addWidget(self.frm_block)
            self.area_widget_layout.addWidget(self.frm_tag)
            self.area_widget_layout.addWidget(self.frm_def)
            self.area_widget_layout.addWidget(self.frm_img)
            self.area_widget_layout.addWidget(self.frm_file)
            self.area_widget_layout.addSpacerItem(spacer)

        # Title
        self.lbl_title.setStyleSheet(self.getv("statistic_lbl_title_stylesheet"))

        # Application
        self.frm_app.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))
        self.btn_app.setStyleSheet(self.getv("statistic_section_btn_stylesheet"))
        self.btn_app.setIcon(QIcon(QPixmap(self.getv("statistic_btn_app_icon_path"))))
        self.lbl_app_info.setStyleSheet(self.getv("statistic_section_lbl_info_stylesheet"))
        self.frm_app_kw.setStyleSheet(self.getv("statistic_section_frm_kw_stylesheet"))
        self.txt_app_kw.setStyleSheet(self.getv("statistic_section_txt_kw_stylesheet"))
        self.btn_app_kw.setStyleSheet(self.getv("statistic_section_btn_kw_stylesheet"))
        self.lbl_app_info_kw.setStyleSheet(self.getv("statistic_section_lbl_info_kw_stylesheet"))
        self.frm_app.setFixedHeight(self.COLLAPSED_HEIGHT)

        # Block
        self.frm_block.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))
        self.btn_block.setStyleSheet(self.getv("statistic_section_btn_stylesheet"))
        self.btn_block.setIcon(QIcon(QPixmap(self.getv("statistic_btn_block_icon_path"))))
        self.lbl_block_info.setStyleSheet(self.getv("statistic_section_lbl_info_stylesheet"))
        self.frm_block_kw.setStyleSheet(self.getv("statistic_section_frm_kw_stylesheet"))
        self.txt_block_kw.setStyleSheet(self.getv("statistic_section_txt_kw_stylesheet"))
        self.btn_block_kw.setStyleSheet(self.getv("statistic_section_btn_kw_stylesheet"))
        self.lbl_block_info_kw.setStyleSheet(self.getv("statistic_section_lbl_info_kw_stylesheet"))
        self.frm_block.setFixedHeight(self.COLLAPSED_HEIGHT)

        # Definition
        self.frm_def.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))
        self.btn_def.setStyleSheet(self.getv("statistic_section_btn_stylesheet"))
        self.btn_def.setIcon(QIcon(QPixmap(self.getv("statistic_btn_def_icon_path"))))
        self.lbl_def_info.setStyleSheet(self.getv("statistic_section_lbl_info_stylesheet"))
        self.frm_def_kw.setStyleSheet(self.getv("statistic_section_frm_kw_stylesheet"))
        self.txt_def_kw.setStyleSheet(self.getv("statistic_section_txt_kw_stylesheet"))
        self.btn_def_kw.setStyleSheet(self.getv("statistic_section_btn_kw_stylesheet"))
        self.lbl_def_info_kw.setStyleSheet(self.getv("statistic_section_lbl_info_kw_stylesheet"))
        self.frm_def.setFixedHeight(self.COLLAPSED_HEIGHT)

        # Image
        self.frm_img.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))
        self.btn_img.setStyleSheet(self.getv("statistic_section_btn_stylesheet"))
        self.btn_img.setIcon(QIcon(QPixmap(self.getv("statistic_btn_img_icon_path"))))
        self.lbl_img_info.setStyleSheet(self.getv("statistic_section_lbl_info_stylesheet"))
        self.frm_img.setFixedHeight(self.COLLAPSED_HEIGHT)

        # File
        self.frm_file.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))
        self.btn_file.setStyleSheet(self.getv("statistic_section_btn_stylesheet"))
        self.btn_file.setIcon(QIcon(QPixmap(self.getv("statistic_btn_file_icon_path"))))
        self.lbl_file_info.setStyleSheet(self.getv("statistic_section_lbl_info_stylesheet"))
        self.frm_file.setFixedHeight(self.COLLAPSED_HEIGHT)

        # Tag
        self.frm_tag.setStyleSheet(self.getv("statistic_section_frm_stylesheet"))
        self.btn_tag.setStyleSheet(self.getv("statistic_section_btn_stylesheet"))
        self.btn_tag.setIcon(QIcon(QPixmap(self.getv("statistic_btn_tag_icon_path"))))
        self.lbl_tag_info.setStyleSheet(self.getv("statistic_section_lbl_info_stylesheet"))
        self.frm_tag.setFixedHeight(self.COLLAPSED_HEIGHT)

        # Log
        self.frm_log.setStyleSheet(self.getv("statistic_frm_log_stylesheet"))
        self.btn_log_close.setStyleSheet(self.getv("statistic_btn_log_stylesheet"))
        self.btn_log_close.setIcon(QIcon(QPixmap(self.getv("statistic_btn_log_icon_path"))))
        self.lbl_log.setStyleSheet(self.getv("statistic_lbl_log_stylesheet"))
        self.frm_log.setVisible(False)
        



        


