from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QTreeWidget, QLabel,
                             QTreeWidgetItem, QItemDelegate, QStyleOptionViewItem,
                             QPushButton, QFrame, QTextEdit, QDesktopWidget)

from PyQt5.QtCore import QModelIndex, Qt, QRect, QSize
from PyQt5.QtGui import (QCloseEvent, QIcon, QKeyEvent, QPainter, QPixmap, QResizeEvent,
                         QMouseEvent, QCursor, QColor, QTextOption)

from typing import Union, Any

import UTILS


class STYLE_widget:
    def __init__(
            self,
            widget_type: str,
            # Widget Text
            text: str = None,
            title: str = None,
            # Widget Position
            x: Union[str, int] = None,
            y: Union[str, int] = None,
            width: Union[str, int] = None,
            height: Union[str, int] = None,
            # Widget base stylesheet
            fg_color: str = None,
            bg_color: str = None,
            border_width: str = None,
            border_color: str = None,
            # Widget hover stylesheet
            hover_fg_color: str = None,
            hover_bg_color: str = None,
            hover_border_width: str = None,
            hover_border_color: str = None,
            # Widget disabled stylesheet
            disabled_fg_color: str = None,
            disabled_bg_color: str = None,
            disabled_border_width: str = None,
            disabled_border_color: str = None,
            selected_fg_color: str = None,
            selected_bg_color: str = None,
            # Other
            frameless: bool = None,
            icon_path: str = None,
            close_icon_path: str = None,
            **kwargs
    ):
        
        if kwargs:
            UTILS.TerminalUtility.WarningMessage("Unexpected settings for widget: #1\n#2", [widget_type, kwargs])
        
        self.__widget_type = widget_type

        self.__text = text
        self.__title = title

        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height

        self.__fg_color = fg_color
        self.__bg_color = bg_color
        self.__border_width = border_width
        self.__border_color = border_color
        self.__hover_fg_color = hover_fg_color
        self.__hover_bg_color = hover_bg_color
        self.__hover_border_width = hover_border_width
        self.__hover_border_color = hover_border_color
        self.__disabled_fg_color = disabled_fg_color
        self.__disabled_bg_color = disabled_bg_color
        self.__disabled_border_width = disabled_border_width
        self.__disabled_border_color = disabled_border_color
        self.__selected_fg_color = selected_fg_color
        self.__selected_bg_color = selected_bg_color

        self.__frameless = frameless
        self.__icon_path = icon_path
        self.__close_icon_path = close_icon_path

    def get_stylesheet_property(self, property_name: str) -> str:
        match property_name.lower():
            case "fg_color":
                return self.__fg_color
            case "bg_color":
                return self.__bg_color
            case "border_width":
                return self.__border_width
            case "border_color":
                return self.__border_color
            case "hover_fg_color":
                return self.__hover_fg_color
            case "hover_bg_color":
                return self.__hover_bg_color
            case "hover_border_width":
                return self.__hover_border_width
            case "hover_border_color":
                return self.__hover_border_color
            case "disabled_fg_color":
                return self.__disabled_fg_color
            case "disabled_bg_color":
                return self.__disabled_bg_color
            case "disabled_border_width":
                return self.__disabled_border_width
            case "disabled_border_color":
                return self.__disabled_border_color
            case "selected_fg_color":
                return self.__selected_fg_color
            case "selected_bg_color":
                return self.__selected_bg_color
        return ""

    @property
    def text(self) -> str:
        if self.__text:
            return self.__text
        else:
            return ""
    
    @property
    def stylesheet(self) -> str:
        stylesheet_base = f"{self.__widget_type} {{#--1 #--2 #--3 #--4}}" if self.__fg_color or self.__bg_color or self.__border_width or self.__border_color else ""
        stylesheet_hover = f"{self.__widget_type}:hover {{#--1 #--2 #--3 #--4}}" if self.__hover_fg_color or self.__hover_bg_color or self.__hover_border_width or self.__hover_border_color else ""
        stylesheet_disabled = f"{self.__widget_type}:disabled {{#--1 #--2 #--3 #--4}}" if self.__disabled_fg_color or self.__disabled_bg_color or self.__disabled_border_width or self.__disabled_border_color else ""
        stylesheet_selected = f"{self.__widget_type}:item:selected {{#--1 #--2}}" if self.__selected_fg_color or self.__selected_bg_color else ""
        
        # Base
        if self.__fg_color:
            stylesheet_base = stylesheet_base.replace("#--1", f"color: {self.__fg_color};")
        else:
            stylesheet_base = stylesheet_base.replace("#--1", "")

        if self.__bg_color:
            stylesheet_base = stylesheet_base.replace("#--2", f"background-color: {self.__bg_color};")
        else:
            stylesheet_base = stylesheet_base.replace("#--2", "")

        if self.__border_width:
            stylesheet_base = stylesheet_base.replace("#--3", f"border: {self.__border_width}px;")
        else:
            stylesheet_base = stylesheet_base.replace("#--3", "")

        if self.__border_color:
            stylesheet_base = stylesheet_base.replace("#--4", f"border-color: {self.__border_color};")
        else:
            stylesheet_base = stylesheet_base.replace("#--4", "")

        # Hover
        if self.__hover_fg_color:
            stylesheet_hover = stylesheet_hover.replace("#--1", f"color: {self.__hover_fg_color};")
        else:
            stylesheet_hover = stylesheet_hover.replace("#--1", "")

        if self.__hover_bg_color:
            stylesheet_hover = stylesheet_hover.replace("#--2", f"background-color: {self.__hover_bg_color};")
        else:
            stylesheet_hover = stylesheet_hover.replace("#--2", "")

        if self.__hover_border_width:
            stylesheet_hover = stylesheet_hover.replace("#--3", f"border: {self.__hover_border_width}px;")
        else:
            stylesheet_hover = stylesheet_hover.replace("#--3", "")

        if self.__hover_border_color:
            stylesheet_hover = stylesheet_hover.replace("#--4", f"border-color: {self.__hover_border_color};")
        else:
            stylesheet_hover = stylesheet_hover.replace("#--4", "")

        # Disabled
        if self.__disabled_fg_color:
            stylesheet_disabled = stylesheet_disabled.replace("#--1", f"color: {self.__disabled_fg_color};")
        else:
            stylesheet_disabled = stylesheet_disabled.replace("#--1", "")

        if self.__disabled_bg_color:
            stylesheet_disabled = stylesheet_disabled.replace("#--2", f"background-color: {self.__disabled_bg_color};")
        else:
            stylesheet_disabled = stylesheet_disabled.replace("#--2", "")

        if self.__disabled_border_width:
            stylesheet_disabled = stylesheet_disabled.replace("#--3", f"border: {self.__disabled_border_width}px;")
        else:
            stylesheet_disabled = stylesheet_disabled.replace("#--3", "")

        if self.__disabled_border_color:
            stylesheet_disabled = stylesheet_disabled.replace("#--4", f"border-color: {self.__disabled_border_color};")
        else:
            stylesheet_disabled = stylesheet_disabled.replace("#--4", "")

        # Selected
        if self.__selected_fg_color:
            stylesheet_selected = stylesheet_selected.replace("#--1", f"color: {self.__selected_fg_color};")
        else:
            stylesheet_selected = stylesheet_selected.replace("#--1", "")

        if self.__selected_bg_color:
            stylesheet_selected = stylesheet_selected.replace("#--2", f"background-color: {self.__selected_bg_color};")
        else:
            stylesheet_selected = stylesheet_selected.replace("#--2", "")

        # Create stylesheet string
        stylesheet = f"{stylesheet_base} {stylesheet_hover} {stylesheet_disabled} {stylesheet_selected}"

        return stylesheet.strip()

    @property
    def title(self) -> str:
        if self.__title:
            return self.__title
        else:
            return ""

    @property
    def icon_path(self) -> str:
        return self.__icon_path
    
    @property
    def close_icon_path(self) -> str:
        return self.__close_icon_path

    @property
    def x(self) -> int:
        return UTILS.TextUtility.get_integer(self.__x)

    @property
    def y(self) -> int:
        return UTILS.TextUtility.get_integer(self.__y)

    @property
    def width(self) -> int:
        return UTILS.TextUtility.get_integer(self.__width)

    @property
    def height(self) -> int:
        return UTILS.TextUtility.get_integer(self.__height)
    
    @property
    def frameless(self) -> bool:
        return self.__frameless


class LogViewerStyle:
    def __init__(self, theme_: str, **kwargs):
        self.__theme = theme_.lower() if theme_.lower() in ["light", "dark"] else "light"

        self.dialog = self.__create_dialog(self.__theme, **kwargs)
        self.lbl_title = self.__create_lbl_title(self.__theme, **kwargs)
        self.tree_msg = self.__create_tree_msg(self.__theme, **kwargs)
        self.menu_label = self.__create_menu_label(self.__theme, **kwargs)

    def __create_menu_label(self, theme_: str, **kwargs) -> STYLE_widget:
        settings = {key.replace("menu_label_", ""):value for key, value in kwargs.items() if key.startswith("menu_label_")}

        if theme_ == "dark":
            settings["fg_color"] = "#aaffff" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "transparent" if settings.get("bg_color") is None else settings.get("bg_color")
            settings["hover_fg_color"] = "#aaff00" if settings.get("hover_fg_color") is None else settings.get("hover_fg_color")
            settings["hover_bg_color"] = "#204161" if settings.get("hover_bg_color") is None else settings.get("hover_bg_color")
            settings["disabled_fg_color"] = "#989898" if settings.get("disabled_fg_color") is None else settings.get("disabled_fg_color")
        else:
            settings["fg_color"] = "#00007f" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "transparent" if settings.get("bg_color") is None else settings.get("bg_color")
            settings["hover_fg_color"] = "#aaff00" if settings.get("hover_fg_color") is None else settings.get("hover_fg_color")
            settings["hover_bg_color"] = "#00004f" if settings.get("hover_bg_color") is None else settings.get("hover_bg_color")
            settings["disabled_fg_color"] = "#939393" if settings.get("disabled_fg_color") is None else settings.get("disabled_fg_color")

        return STYLE_widget(widget_type="QLabel", **settings)

    def __create_tree_msg(self, theme_: str, **kwargs) -> STYLE_widget:
        settings = {key.replace("tree_msg_", ""):value for key, value in kwargs.items() if key.startswith("tree_msg_")}

        if theme_ == "dark":
            settings["fg_color"] = "#ffff00" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "transparent" if settings.get("bg_color") is None else settings.get("bg_color")
            settings["selected_fg_color"] = "#ffff00" if settings.get("selected_fg_color") is None else settings.get("selected_fg_color")
            settings["selected_bg_color"] = "#00007f" if settings.get("selected_bg_color") is None else settings.get("selected_bg_color")
        else:
            settings["fg_color"] = "#000000" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "#c2c2c2" if settings.get("bg_color") is None else settings.get("bg_color")
            settings["selected_fg_color"] = "#ffff00" if settings.get("selected_fg_color") is None else settings.get("selected_fg_color")
            settings["selected_bg_color"] = "#005500" if settings.get("selected_bg_color") is None else settings.get("selected_bg_color")

        return STYLE_widget(widget_type="QTreeWidget", **settings)

    def __create_dialog(self, theme_: str, **kwargs) -> STYLE_widget:
        settings = {key.replace("dialog_", ""):value for key, value in kwargs.items() if key.startswith("dialog_")}

        settings["title"] = "Log Viewer" if settings.get("title") is None else settings.get("title")
        settings["icon_path"] = settings.get("icon_path")
        settings["close_icon_path"] = settings.get("close_icon_path")
        settings["frameless"] = True if settings.get("frameless") is None else settings.get("frameless")
        settings["x"] = UTILS.TextUtility.get_integer(settings.get("x"))
        settings["y"] = UTILS.TextUtility.get_integer(settings.get("y"))
        settings["width"] = UTILS.TextUtility.get_integer(settings.get("width"))
        settings["height"] = UTILS.TextUtility.get_integer(settings.get("height"))

        if theme_ == "dark":
            settings["fg_color"] = "#ffff00" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "#003550" if settings.get("bg_color") is None else settings.get("bg_color")
        else:
            settings["fg_color"] = "#000000" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "#d4d4d4" if settings.get("bg_color") is None else settings.get("bg_color")

        return STYLE_widget(widget_type="QDialog", **settings)

    def __create_lbl_title(self, theme_: str, **kwargs) -> STYLE_widget:
        settings = {key.replace("lbl_title_", ""):value for key, value in kwargs.items() if key.startswith("lbl_title_")}

        settings["text"] = "Log Viewer:" if settings.get("text") is None else settings.get("text")
        
        if theme_ == "dark":
            settings["fg_color"] = "#00ffff" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "transparent" if settings.get("bg_color") is None else settings.get("bg_color")
        else:
            settings["fg_color"] = "#00007f" if settings.get("fg_color") is None else settings.get("fg_color")
            settings["bg_color"] = "transparent" if settings.get("bg_color") is None else settings.get("bg_color")

        return STYLE_widget(widget_type="QLabel", **settings)

    @property
    def theme(self) -> str:
        return self.__theme


class LogViewerData:
    def __init__(self, source_messages: dict):
        self.__src = source_messages.get("messages") if source_messages.get("messages") else []
        self.__data_map = source_messages.get("data_map") if source_messages.get("messages") else []

    def get_last_id(self) -> str:
        ids = [x.get("id") for x in self.__src]
        if ids:
            return ids[-1]
        else:
            return None

    def get_list_dates(self) -> list:
        result = []
        for item in self.__src:
            date = item.get("date")
            if date and date not in result:
                result.append(date)

        return result
    
    def get_list_log_names_for_date(self, date: str) -> list:
        if not date:
            UTILS.TerminalUtility.WarningMessage("Invalid date in #1\ntype(date): #2\ndate = #3", ["get_list_log_names_for_date", type(date), date])
            return []
        
        result = []
        for item in self.__src:
            if item.get("date") == date and item.get("log_name"):
                if item["log_name"] not in result:
                    result.append(item["log_name"])
        
        return result
    
    def get_list_ids(self, date: str = None, log_name: str = None) -> list:
        result = []
        if date and not log_name:
            for item in self.__src:
                if item.get("date") == date and item.get("id"):
                    if item["id"] not in result:
                        result.append(item["id"])
        elif log_name and not date:
            for item in self.__src:
                if item.get("log_name") == log_name and item.get("id"):
                    if item["id"] not in result:
                        result.append(item["id"])
        elif date and log_name:
            for item in self.__src:
                if item.get("date") == date and item.get("log_name") == log_name and item.get("id"):
                    if item["id"] not in result:
                        result.append(item["id"])

        return result
    
    def get_record(self, record_id: str) -> dict:
        for item in self.__src:
            if item.get("id") == record_id:
                for call_stack_item in item["message"]["call_stack"]:
                    if isinstance(call_stack_item["function_code"], int):
                        call_stack_item["function_code"] = self._get_data_map_value(data_map_id=call_stack_item["function_code"], default_value="UNDEFINED FUNCTION CODE !!!")
                    if isinstance(call_stack_item["locals"], int):
                        call_stack_item["locals"] = self._get_data_map_value(data_map_id=call_stack_item["locals"], default_value=[["UNDEFINED LOCAL VARIABLE !!!", "", ""]])
                    if isinstance(call_stack_item["globals"], int):
                        call_stack_item["globals"] = self._get_data_map_value(data_map_id=call_stack_item["globals"], default_value=[["UNDEFINED GLOBAL VARIABLE !!!", "", ""]])
                    if isinstance(call_stack_item["builtins"], int):
                        call_stack_item["builtins"] = self._get_data_map_value(data_map_id=call_stack_item["builtins"], default_value=[["UNDEFINED BUILTINS VARIABLE !!!", "", ""]])

                return item

    def get_top_function_name(self, record_id: str) -> str:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("call_stack"):
                if item["message"]["call_stack"]:
                    return str(item["message"]["call_stack"][0]["function_name"])
        return "N/A"

    def get_top_function_class(self, record_id: str) -> str:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("call_stack"):
                if item["message"]["call_stack"]:
                    return str(item["message"]["call_stack"][0]["class"])
        return "N/A"

    def get_top_function_module(self, record_id: str) -> str:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("call_stack"):
                if item["message"]["call_stack"]:
                    return str(item["message"]["call_stack"][0]["module"])
        return "N/A"

    def _get_data_map_value(self, data_map_id: int, default_value: Any = None) -> Any:
        for data_map in self.__data_map:
            if data_map.get("id") == data_map_id:
                return data_map.get("value", default_value)
        return default_value

    def get_arguments(self, record_id: str) -> list:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("arguments"):
                return item["message"]["arguments"]

    def get_variables(self, record_id: str) -> list:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("variables"):
                return item["message"]["variables"]
        return []

    def get_function_code(self, record_id: str) -> str:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("call_stack"):
                if item["message"]["call_stack"]:
                    return item["message"]["call_stack"][0]["function_code"]
        return "N/A"

    def get_call_stack(self, record_id: str) -> list:
        item = self.get_record(record_id=record_id)
        if item.get("message"):
            if item["message"].get("call_stack"):
                return item["message"]["call_stack"]
        return []

    def has_data(self) -> bool:
        return len(self.__src) > 0

    def is_exception(self, record_id: str) -> bool:
        return self.get_record(record_id=record_id)["message"]["is_exception"]

    def is_warning(self, record_id: str) -> bool:
        return self.get_record(record_id=record_id)["message"]["is_warning"]

    def get_log_date(self, record_id: str) -> str:
        if rec_data:= self.get_record(record_id=record_id):
            return rec_data.get("date")

    def get_msg_date(self, record_id: str) -> str:
        if rec_data:= self.get_record(record_id=record_id):
            if rec_data.get("message"):
                return rec_data["message"].get("date")

    def get_log_time(self, record_id: str) -> str:
        if rec_data:= self.get_record(record_id=record_id):
            return rec_data.get("time")

    def get_msg_time(self, record_id: str) -> str:
        if rec_data:= self.get_record(record_id=record_id):
            if rec_data.get("message"):
                return rec_data["message"].get("time")

    def get_log_name(self, record_id: str) -> str:
        if rec_data:= self.get_record(record_id=record_id):
            return rec_data.get("log_name")

    def get_msg_text(self, record_id: str) -> str:
        if rec_data:= self.get_record(record_id=record_id):
            msg = rec_data.get("message")
            if msg:
                return msg.get("text")

    def get_msg_counter_in_log(self, record_id: str) -> int:
        date = self.get_log_date(record_id=record_id)
        log_name = self.get_log_name(record_id=record_id)
        msg_counter = 1
        for record in self.__src:
            if record.get("id") == record_id:
                break
            if record.get("date") == date and record.get("log_name") == log_name:
                msg_counter += 1
        else:
            return 0
        return msg_counter

    def get_msg_count(self, record_id: str = None, date: str = None, log_name: str = None) -> int:
        if record_id is not None:
            date = self.get_log_date(record_id=record_id)
            log_name = self.get_log_name(record_id=record_id)
        msg_counter = 0
        for record in self.__src:
            if (date is None or record.get("date") == date) and (log_name is None or record.get("log_name") == log_name):
                msg_counter += 1

        return msg_counter


class ColoredTextDelegate(QItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        super().paint(painter, option, index)
        rect = QRect(option.rect.x(), option.rect.y(), option.rect.width(), option.rect.height())
        
        for text in index.data(Qt.UserRole)["text"]:
            painter.setPen(QColor(text[1]))
            painter.drawText(rect, Qt.AlignLeft, text[0])
            w = painter.fontMetrics().width(text[0])
            new_rect_x = rect.x() + w
            new_rect_w = rect.width() - w
            if new_rect_w < 0:
                new_rect_w = 0
            rect = QRect(new_rect_x, rect.y(), new_rect_w, rect.height())

        return            


class MessageDetails(QFrame):
    def __init__(self, parent_widget: "LogMessageViewer", msg_id: str, data: LogViewerData, **kwargs) -> None:
        super().__init__()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        if kwargs.get("run_on_top", False):
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.parent_widget = parent_widget
        self.selected_menu = "messages"

        self.msg_id = msg_id
        self.data = data

        self.padding = 5
        self.spacing = 5

        self.menu_item_stylesheet_normal = "QLabel {color: #aaffff;} QLabel:hover {background-color: #0000ff; color: #ffff00;}"
        self.menu_item_stylesheet_selected = "QLabel {background-color: #008700; color: #ffffff;} QLabel:hover {background-color: #0000ff; color: #ffff00;}"
 
        self._create_widgets()

        if kwargs.get("x") is not None and kwargs.get("y") is not None:
            self.move(kwargs["x"], kwargs["y"])
        elif kwargs.get("pos") is not None:
            self.move(kwargs["pos"][0], kwargs["pos"][1])

        if kwargs.get("width") is not None and kwargs.get("height") is not None:
            self.move(kwargs["width"], kwargs["height"])
        elif kwargs.get("size") is not None:
            self.move(kwargs["size"][0], kwargs["size"][1])
        else:
            self.resize(630, 400)

        if kwargs.get("show_win") is not None:
            if kwargs["show_win"]:
                self.show()
        else:
            self.show()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        
        # Message title
        self.lbl_title.move(self.padding, self.padding)

        # Message type
        frm_type_x = w - self.frm_type.width() - self.padding
        if frm_type_x < 0:
            frm_type_x = 0

        self.frm_type.move(frm_type_x, self.padding)

        # Menu
        self.frm_menu.move(self.padding, self.lbl_title.pos().y() + self.lbl_title.height() + self.spacing * 3)

        # Info TextBox
        self.txt_info.move(self.padding, self.frm_menu.pos().y() + self.frm_menu.height() + self.spacing)
        txt_info_h = h - (self.frm_menu.pos().y() + self.frm_menu.height() + self.padding + self.spacing)
        if txt_info_h < 0:
            txt_info_h = 0
        self.txt_info.resize(w - self.padding * 2, txt_info_h)

        return super().resizeEvent(a0)

    def _create_widgets(self):
        self.setStyleSheet("QFrame {background-color: #252538;}")
        self.setWindowTitle("Message details")
        self.setWindowIcon(self.parent_widget.windowIcon())

        # Message title
        self.lbl_title = QLabel(self)
        lbl_title_text = "On #1 at #2, LOG: #3, MsgID: #4"
        text_to_html = UTILS.HTMLText.TextToHTML(text=lbl_title_text)
        text_to_html.general_rule.fg_color = "#e2e2e2"
        date_rule = UTILS.HTMLText.TextToHtmlRule(
            text="#1",
            replace_with=self.data.get_log_date(self.msg_id),
            fg_color="#aaffff"
        )
        time_rule = UTILS.HTMLText.TextToHtmlRule(
            text="#2",
            replace_with=self.data.get_log_time(self.msg_id),
            fg_color="#aaffff"
        )
        log_rule = UTILS.HTMLText.TextToHtmlRule(
            text="#3",
            replace_with=self.data.get_log_name(self.msg_id),
            fg_color="#00bd8b"
        )
        msg_id_rule = UTILS.HTMLText.TextToHtmlRule(
            text="#4",
            replace_with=self.msg_id,
            fg_color="#00bd8b"
        )
        text_to_html.add_rule(date_rule)
        text_to_html.add_rule(time_rule)
        text_to_html.add_rule(log_rule)
        text_to_html.add_rule(msg_id_rule)

        self.lbl_title.setText(text_to_html.get_html())
        self.lbl_title.adjustSize()


        # Message type
        self.frm_type = QFrame(self)
        
        self.lbl_type_label = QLabel(self.frm_type)
        self.lbl_type_label.setText("Type:")
        self.lbl_type_label.setStyleSheet("QLabel {color: #00ff00;}")
        self.lbl_type_label.move(0, 0)
        self.lbl_type_label.adjustSize()

        self.lbl_type_value = QLabel(self.frm_type)
        self.lbl_type_value.setAlignment(Qt.AlignCenter)
        if self.data.is_exception(self.msg_id):
            self.lbl_type_value.setStyleSheet("QLabel {color: #ffff00; background-color: #aa0000;}")
            self.lbl_type_value.setText("Exception")
        elif self.data.is_warning(self.msg_id):
            self.lbl_type_value.setStyleSheet("QLabel {color: #ffff00; background-color: #6b4700;}")
            self.lbl_type_value.setText("Warning")
        else:
            self.lbl_type_value.setStyleSheet("QLabel {color: #ffff00; background-color: #008d00;}")
            self.lbl_type_value.setText("Normal")

        self.lbl_type_value.move(self.lbl_type_label.width() + 5, 0)
        self.lbl_type_value.adjustSize()
        self.lbl_type_value.resize(self.lbl_type_value.width() + 10, self.lbl_type_value.height())

        self.frm_type.resize(self.lbl_type_label.width() + self.lbl_type_value.width() + 5, max(self.lbl_type_value.height(), self.lbl_type_label.height()))


        # Menu
        self.frm_menu = QFrame(self)
        
        x = 0
        self.lbl_menu_message = QLabel(self.frm_menu)
        self.lbl_menu_message.setText("Message")
        self.lbl_menu_message.setStyleSheet(self.menu_item_stylesheet_selected)
        self.lbl_menu_message.adjustSize()
        self.lbl_menu_message.setAlignment(Qt.AlignCenter)
        self.lbl_menu_message.resize(self.lbl_menu_message.width() + 10, self.lbl_menu_message.height())
        self.lbl_menu_message.move(x, 0)
        self.lbl_menu_message.mousePressEvent = self.on_lbl_menu_message_mouse_press
        x += self.lbl_menu_message.width() + self.spacing

        self.lbl_menu_call_stack = QLabel(self.frm_menu)
        self.lbl_menu_call_stack.setText("Call Stack")
        self.lbl_menu_call_stack.setStyleSheet(self.menu_item_stylesheet_normal)
        self.lbl_menu_call_stack.adjustSize()
        self.lbl_menu_call_stack.setAlignment(Qt.AlignCenter)
        self.lbl_menu_call_stack.resize(self.lbl_menu_call_stack.width() + 10, self.lbl_menu_call_stack.height())
        self.lbl_menu_call_stack.move(x, 0)
        self.lbl_menu_call_stack.mousePressEvent = self.on_lbl_menu_call_stack_mouse_press
        x += self.lbl_menu_call_stack.width() + self.spacing

        self.lbl_menu_function_code = QLabel(self.frm_menu)
        self.lbl_menu_function_code.setText("Function Code")
        self.lbl_menu_function_code.setStyleSheet(self.menu_item_stylesheet_normal)
        self.lbl_menu_function_code.adjustSize()
        self.lbl_menu_function_code.setAlignment(Qt.AlignCenter)
        self.lbl_menu_function_code.resize(self.lbl_menu_function_code.width() + 10, self.lbl_menu_function_code.height())
        self.lbl_menu_function_code.move(x, 0)
        self.lbl_menu_function_code.mousePressEvent = self.on_lbl_menu_function_code_mouse_press
        x += self.lbl_menu_function_code.width() + self.spacing

        self.lbl_menu_variables = QLabel(self.frm_menu)
        self.lbl_menu_variables.setText("Variables")
        self.lbl_menu_variables.setStyleSheet(self.menu_item_stylesheet_normal)
        self.lbl_menu_variables.adjustSize()
        self.lbl_menu_variables.setAlignment(Qt.AlignCenter)
        self.lbl_menu_variables.resize(self.lbl_menu_variables.width() + 10, self.lbl_menu_variables.height())
        self.lbl_menu_variables.move(x, 0)
        self.lbl_menu_variables.mousePressEvent = self.on_lbl_menu_variables_mouse_press
        x += self.lbl_menu_variables.width() + self.spacing

        self.frm_menu.resize(x, max(self.lbl_menu_message.height(), self.lbl_menu_call_stack.height()))

        # Info
        self.txt_info = QTextEdit(self)
        self.txt_info.setReadOnly(True)
        self.txt_info.setLineWrapMode(QTextEdit.NoWrap)
        self.txt_info.setWordWrapMode(QTextOption.NoWrap)

        self.txt_info.setFrameShape(QFrame.Box)
        self.txt_info.setFrameShadow(QFrame.Plain)

        self.txt_info.setStyleSheet("QTextEdit {color: #ffff00; background-color: #252538; border: 1px solid #aaff7f;}")

        self.info_show_message()

    def update_menu_appearance(self):
        if self.selected_menu == "messages":
            self.lbl_menu_message.setStyleSheet(self.menu_item_stylesheet_selected)
            self.lbl_menu_call_stack.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_function_code.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_variables.setStyleSheet(self.menu_item_stylesheet_normal)
        elif self.selected_menu == "call_stack":
            self.lbl_menu_message.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_call_stack.setStyleSheet(self.menu_item_stylesheet_selected)
            self.lbl_menu_function_code.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_variables.setStyleSheet(self.menu_item_stylesheet_normal)
        elif self.selected_menu == "function_code":
            self.lbl_menu_message.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_call_stack.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_function_code.setStyleSheet(self.menu_item_stylesheet_selected)
            self.lbl_menu_variables.setStyleSheet(self.menu_item_stylesheet_normal)
        elif self.selected_menu == "variables":
            self.lbl_menu_message.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_call_stack.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_function_code.setStyleSheet(self.menu_item_stylesheet_normal)
            self.lbl_menu_variables.setStyleSheet(self.menu_item_stylesheet_selected)

    def on_lbl_menu_call_stack_mouse_press(self, e: QMouseEvent):
        self.selected_menu = "call_stack"
        self.update_menu_appearance()
        self.info_show_call_stack()

    def on_lbl_menu_function_code_mouse_press(self, e: QMouseEvent):
        self.selected_menu = "function_code"
        self.update_menu_appearance()
        self.info_show_function_code()

    def on_lbl_menu_variables_mouse_press(self, e: QMouseEvent):
        self.selected_menu = "variables"
        self.update_menu_appearance()
        self.info_show_variables()

    def on_lbl_menu_message_mouse_press(self, e: QMouseEvent):
        self.selected_menu = "messages"
        self.update_menu_appearance()
        self.info_show_message()

    def info_show_call_stack(self) -> None:
        self.txt_info.clear()
        call_stack = self.data.get_call_stack(self.msg_id)

        text = "#----1"
        text_to_html = UTILS.HTMLText.TextToHTML()
        text_to_html.general_rule.fg_color = "#65cb96"
        text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
            text="#----1",
            replace_with="Trace back, most recent call first:\n\n",
            fg_color="#ffaa7f"
        ))

        count = 2
        for stack in call_stack:
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"Function: {rule_id}"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=stack["function_name"],
                fg_color="#00ff00"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"  (Line: {rule_id})"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(stack["line_number"]),
                fg_color="#00ff7f"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"  (Class: {rule_id})"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=stack["class"],
                fg_color="#00ff00"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"  (Module: {rule_id})"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=stack["module"],
                fg_color="#00ff00"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"  File:  {rule_id}\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(stack["file_path"]),
                fg_color="#5555ff"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"{rule_id}\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(stack["line_content"]),
                fg_color="#c7c7c7"
            ))
            count += 1

        if not call_stack:
            text += "#99999"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text="#99999",
                replace_with="No call stack found!",
                fg_color="#840000"
            ))

        text_to_html.set_text(text)
        self.txt_info.setText(text_to_html.get_html())

    def info_show_function_code(self) -> None:
        self.txt_info.clear()

        call_stack = self.data.get_call_stack(self.msg_id)
        
        if not call_stack:
            self.txt_info.setText("No call stack found!\nUnable to show function code.")
            return
        
        text_to_html = UTILS.HTMLText.TextToHTML()
        text_to_html.general_rule.fg_color = "#ffff00"

        text = ""
        count = 1
        code_map = []
        for stack in call_stack:
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"Function: {rule_id}\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=stack["function_name"],
                fg_color="#000062",
                bg_color="#ffff00"
            ))
            count += 1

            function_code = stack["function_code"]
            function_first_line_no = stack.get("function_first_line_no")
            if function_first_line_no:
                function_first_line_no = stack["line_number"] - function_first_line_no + 1

            colorized_code = UTILS.HTMLText.ColorizeCode.ColorizeCode(function_code, hightlight_lines=function_first_line_no)
            if colorized_code == function_code:
                colorized_code = f"<pre>{function_code}</pre>"

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += rule_id
            colorized_code += "\n\n"
            code_map.append([rule_id, colorized_code])
            count += 1

        text_to_html.set_text(text)
        text = text_to_html.get_html()
        
        for item in code_map:
            text = text.replace(item[0], item[1])
        
        self.txt_info.setHtml(text)

    def info_show_variables(self) -> None:
        self.txt_info.clear()
        
        # Retrieve message variables
        variables = self.data.get_variables(self.msg_id)
        text = ""
        text_to_html = UTILS.HTMLText.TextToHTML()
        text_to_html.general_rule.fg_color = "#a6a6a6"
        var_number = 1
        count = 1
        for variable in variables:
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"{var_number}.) {rule_id}"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=variable[0],
                fg_color="#00bd8b"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f" = {rule_id}"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(variable[1]),
                fg_color="#00bd8b"
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"  VarType: {rule_id}\n"
            var_type = str(variable[2])

            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=var_type,
                fg_color="#82b2ff"
            ))
            count += 1
            var_number += 1

        if variables:
            text = "#99999\n\n" + text
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text="#99999",
                replace_with="Variables received from message:",
                fg_color="#a681a6",
                font_size=18
            ))
        else:
            text = "#99999"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text="#99999",
                replace_with="Message did not provide any variables.",
                fg_color="#7c7c7c",
                font_size=18
            ))

        text +="\n\n"
        text_to_html.set_text(text)

        message_variables_text = text_to_html.get_html()

        # Get function variables from call stack
        call_stack = self.data.get_call_stack(self.msg_id)
        
        text = "Functions variables:\n\n"
        text_to_html = UTILS.HTMLText.TextToHTML()
        text_to_html.general_rule.fg_color = "#ffff00"

        func_variables_text = ""

        if not call_stack:
            text += "#99999"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text="#99999",
                replace_with="No call stack found!\nUnable to show function variables.",
                fg_color="#6f0000"
            ))
            text_to_html.set_text(text)
            variables_text = message_variables_text + text_to_html.get_html()
            self.txt_info.setHtml(variables_text)
            return

        count = 1
        for stack in call_stack:
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"Function: {rule_id}\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=stack["function_name"],
                fg_color="#000062",
                bg_color="#ffff00"
            ))
            count += 1

            # Locals
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"{rule_id} "
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with="Local variables",
                fg_color="#75b1ff",
                font_italic=True
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"({rule_id}) :\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(len(stack["locals"])),
                fg_color="#aaaa7f",
            ))
            count += 1

            if stack["locals"]:
                for variable in stack["locals"]:
                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f"     {rule_id}"
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=str(variable[0]),
                        fg_color="#00ff00"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f" ({rule_id}) "
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=variable[1],
                        fg_color="#555500"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f" {rule_id} "
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with="=",
                        fg_color="#55aa7f"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f"{rule_id}\n"
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=variable[2],
                        fg_color="#aaff7f"
                    ))
                    count += 1

            # Globals
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"{rule_id} "
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with="Global variables",
                fg_color="#75b1ff",
                font_italic=True
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"({rule_id}) :\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(len(stack["globals"])),
                fg_color="#aaaa7f",
            ))
            count += 1

            if stack["globals"]:
                for variable in stack["globals"]:
                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f"     {rule_id}"
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=str(variable[0]),
                        fg_color="#00ff00"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f" ({rule_id}) "
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=variable[1],
                        fg_color="#555500"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f" {rule_id} "
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with="=",
                        fg_color="#55aa7f"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f"{rule_id}\n"
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=variable[2],
                        fg_color="#aaff7f"
                    ))
                    count += 1

            # Builtins
            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"{rule_id} "
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with="Builtins variables",
                fg_color="#75b1ff",
                font_italic=True
            ))
            count += 1

            rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
            text += f"({rule_id}) :\n"
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                text=rule_id,
                replace_with=str(len(stack["builtins"])),
                fg_color="#aaaa7f",
            ))
            count += 1

            if stack["builtins"]:
                for variable in stack["builtins"]:
                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f"     {rule_id}"
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=str(variable[0]),
                        fg_color="#00ff00"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f" ({rule_id}) "
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=variable[1],
                        fg_color="#555500"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f" {rule_id} "
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with="=",
                        fg_color="#55aa7f"
                    ))
                    count += 1

                    rule_id = "#" + "-" *(5 - len(str(count))) + str(count)
                    text += f"{rule_id}\n"
                    text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(
                        text=rule_id,
                        replace_with=variable[2],
                        fg_color="#aaff7f"
                    ))
                    count += 1

            text += "\n"

        text_to_html.set_text(text)
        func_variables_text = text_to_html.get_html()

        variables_text = message_variables_text + func_variables_text

        self.txt_info.setHtml(variables_text)

    def info_show_message(self) -> None:
        self.txt_info.clear()
        COLOR_MSG = "#55aa00"
        COLOR_HEADER = "#7c7c7c"
        SIZE_HEADER = 20
        SIZE_GENERAL = 16
        COLOR_ARGUMENTS = "#00ff00"
        COLOR_WARNING = "#ff5500"
        COLOR_EXCEPTION = "#ff0000"


        msg_text_raw = self.data.get_msg_text(self.msg_id)
        if self.data.is_exception(self.msg_id):
            msg_color = COLOR_EXCEPTION
        elif self.data.is_warning(self.msg_id):
            msg_color = COLOR_WARNING
        else:
            msg_color = COLOR_MSG

        msg_text_list = self.parent_widget.insert_arguments(msg_text_raw, msg_color, self.data.get_arguments(self.msg_id), COLOR_ARGUMENTS)

        text = ""
        text_to_html = UTILS.HTMLText.TextToHTML()
        text_to_html.general_rule.fg_color = msg_color
        text_to_html.general_rule.font_size = SIZE_GENERAL
        
        count = 1

        rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
        text += f"{rule_id}\n"
        text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(text=rule_id, replace_with="Message content:", fg_color=COLOR_HEADER, font_size=SIZE_HEADER))
        count += 1

        for item in msg_text_list:
            rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
            text += rule_id
            text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(text=rule_id, replace_with=item[0], fg_color=item[1]))
            count += 1
        
        rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
        text += f"\n\n{rule_id}\n"
        text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(text=rule_id, replace_with="Message source function:", fg_color=COLOR_HEADER, font_size=SIZE_HEADER))
        count += 1
        
        func_description = ""
        rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
        func_description += f"(Function) {rule_id}"
        text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(text=rule_id, replace_with=self.data.get_top_function_name(self.msg_id), fg_color=COLOR_ARGUMENTS))
        count += 1
        rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
        func_description += f" (Class) {rule_id}"
        text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(text=rule_id, replace_with=self.data.get_top_function_class(self.msg_id), fg_color=COLOR_ARGUMENTS))
        count += 1
        rule_id = "#" + "-" * (5 - len(str(count))) + str(count)
        func_description += f" (Module) {rule_id}\n"
        text_to_html.add_rule(UTILS.HTMLText.TextToHtmlRule(text=rule_id, replace_with=self.data.get_top_function_module(self.msg_id), fg_color=COLOR_ARGUMENTS))
        count += 1

        text += func_description
        
        text_to_html.set_text(text)
        self.txt_info.setHtml(text_to_html.get_html())

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.close()

        return super().keyPressEvent(a0)


class LogMessageViewer(QDialog):
    def __init__ (self, parent_widget: QWidget, source_messages: list, **kwargs):
        super().__init__(parent_widget)

        self.drag_mode = None
        self.resize_mode = None

        self.parent_widget = parent_widget
        self.source_messages = source_messages
        self.details_frames = []
        self.dialog_close_feedback = kwargs.get("close_feedback_function", None)

        self.data = LogViewerData(source_messages=source_messages)

        self.theme = kwargs.get("theme") if kwargs.get("theme") else "light"

        self._style = LogViewerStyle(theme_=self.theme, **kwargs)
        
        self._define_widgets()
        self._define_widgets_appearance()

        self.update_data()
        
        # Connect events with slots
        self.lbl_title.mousePressEvent = self.lbl_title_mouse_press
        self.lbl_title.mouseReleaseEvent = self.lbl_title_mouse_release
        self.lbl_title.mouseMoveEvent = self.lbl_title_mouse_move
        self.lbl_resize.mousePressEvent = self.lbl_resize_mouse_press
        self.lbl_resize.mouseReleaseEvent = self.lbl_resize_mouse_release
        self.lbl_resize.mouseMoveEvent = self.lbl_resize_mouse_move
        self.tree_msg.itemSelectionChanged.connect(self.on_current_item_changed)
        self.tree_msg.itemDoubleClicked.connect(self.on_item_double_click)
        UTILS.Signal.signalLogUpdated.connect(self.on_signal_log_updated)

        if kwargs.get("x") is not None and kwargs.get("y") is not None:
            self.move(kwargs["x"], kwargs["y"])
        elif kwargs.get("pos") is not None:
            self.move(kwargs["pos"][0], kwargs["pos"][1])

        if kwargs.get("width") is not None and kwargs.get("height") is not None:
            self.move(kwargs["width"], kwargs["height"])
        elif kwargs.get("size") is not None:
            self.move(kwargs["size"][0], kwargs["size"][1])
        else:
            self.resize(630, 400)
        
        self.show()

        if kwargs.get("run_exec") is True:
            self.exec_()

    def on_signal_log_updated(self, func_info: dict, data: list) -> None:
        self.update_data(source_messages=data)
        self._expand_dates()
        self._expand_logs()
        self._show_last_item()

    def on_current_item_changed(self) -> None:
        self.update_menu()

    def update_data(self, reset_data: bool = False, source_messages: dict = None) -> tuple:
        """
        Populates tree widget with data
        
        Args:
            reset_data (bool): If True, Tree Widget will be cleared and then populated
            source_messages (dict): New, updated message list if needed

        Return:
            Tuple (Number of added items, Number of removed items)
        """

        if self._style.theme == "dark":
            COLOR_DATE = "#ffff00"
            COLOR_LOG = "#00ffff"
            COLOR_MSG = "#55aa00"
            COLOR_ARGUMENTS = "#00ff00"
            COLOR_INFO_DATE = "#c2c2c2"
            COLOR_INFO_LOG = "#c2c2c2"
            COLOR_INFO_MSG = "#c2c2c2"
            COLOR_TIME = "#c2ff90"
            COLOR_WARNING = "#ff5500"
            COLOR_EXCEPTION = "#ff0000"
        else:
            COLOR_DATE = "#000000"
            COLOR_LOG = "#00007f"
            COLOR_MSG = "#005500"
            COLOR_ARGUMENTS = "#009800  "
            COLOR_INFO_DATE = "#5b5b5b"
            COLOR_INFO_LOG = "#5b5b5b"
            COLOR_INFO_MSG = "#5b5b5b"
            COLOR_TIME = "#444466"
            COLOR_WARNING = "#712600"
            COLOR_EXCEPTION = "#760000"

        if reset_data:
            self.tree_msg.clear()
        
        if source_messages:
            self.data = LogViewerData(source_messages=source_messages)
        
        # DATES
        dates_tree = [self.tree_msg.topLevelItem(x).data(0, Qt.UserRole)["data"] for x in range(self.tree_msg.topLevelItemCount())]
        dates_data = self.data.get_list_dates()
        # Add new dates
        for date in dates_data:
            if date not in dates_tree:
                tree_item = QTreeWidgetItem(self.tree_msg)
                tree_item.setText(0, "")
                tree_item_data = {
                    "data": date,
                    "type": "date",
                    "text": [
                        [f"{date}   ", COLOR_DATE],
                        [f"({len(self.data.get_list_log_names_for_date(date))} logs, {self.data.get_msg_count(date=date)} messages in total.)", COLOR_INFO_DATE]
                    ]
                }
                tree_item.setData(0, Qt.UserRole, tree_item_data)
                # self._colorize_tree_item(tree_item=tree_item, item_type="date")
                self.tree_msg.addTopLevelItem(tree_item)
                dates_tree.append(date)
        # Remove missing dates
        for date in dates_tree:
            if date not in dates_data:
                item_index = None
                for i in range(self.tree_msg.topLevelItemCount()):
                    if self.tree_msg.topLevelItem(i).data(0, Qt.UserRole)["data"] == date:
                        item_index = i
                        break
                if item_index is not None:
                    self.tree_msg.takeTopLevelItem(item_index)
        
        # LOGS
        for top_index in range(self.tree_msg.topLevelItemCount()):
            top_item = self.tree_msg.topLevelItem(top_index)
            date = top_item.data(0, Qt.UserRole)["data"]
            
            logs_data = self.data.get_list_log_names_for_date(date=date)
            logs_tree = [top_item.child(x).data(0, Qt.UserRole)["data"] for x in range(top_item.childCount())]

            # Add new logs
            for log in logs_data:
                if log not in logs_tree:
                    tree_item = QTreeWidgetItem()
                    tree_item.setText(0, "")
                    tree_item_data = {
                        "data": log,
                        "type": "log",
                        "text": [
                            [f"{log}   ", COLOR_LOG],
                            [f"({self.data.get_msg_count(log_name=log, date=date)} messages.)", COLOR_INFO_LOG]
                        ]
                    }
                    tree_item.setData(0, Qt.UserRole, tree_item_data)
                    # self._colorize_tree_item(tree_item=tree_item, item_type="log")
                    top_item.addChild(tree_item)
                    logs_tree.append(log)
            # Remove missing logs
            for log in logs_tree:
                if log not in logs_data:
                    item_index = None
                    for i in range(top_item.childCount()):
                        if top_item.child(i).data(0, Qt.UserRole)["data"] == log:
                            item_index = i
                            break
                    if item_index is not None:
                        top_item.takeChild(item_index)
        
        # MESSAGES
        count_added_messages = 0
        count_removed_messages = 0
        for top_index in range(self.tree_msg.topLevelItemCount()):
            top_item = self.tree_msg.topLevelItem(top_index)
            date = top_item.data(0, Qt.UserRole)["data"]
            for log_index in range(top_item.childCount()):
                log_item = top_item.child(log_index)
                log_name = log_item.data(0, Qt.UserRole)["data"]

                msg_data = self.data.get_list_ids(date=date, log_name=log_name)
                msg_tree = [log_item.child(x).data(0, Qt.UserRole)["data"] for x in range(log_item.childCount())]
                
                # Add new messages
                for msg in msg_data:
                    if msg not in msg_tree:
                        tree_item = QTreeWidgetItem()
    
                        tree_item.setText(0, "")

                        if self.data.is_exception(msg):
                            msg_color = COLOR_EXCEPTION
                        elif self.data.is_warning(msg):
                            msg_color = COLOR_WARNING
                        else:
                            msg_color = COLOR_MSG

                        msg_text = self.data.get_msg_text(msg)
                        if msg_text.count("\n"):
                            msg_text = msg_text.splitlines()[0]
                            has_lf = True
                        else:
                            has_lf = False

                        tree_item_data = {
                            "data": msg,
                            "type": "msg",
                            "text": [
                                [f"[#{self.data.get_msg_counter_in_log(msg)}] ", COLOR_INFO_MSG],
                                [f"{self.data.get_msg_time(msg)}  ", COLOR_TIME]
                            ]
                        }
                        tree_item_data["text"].extend(self.insert_arguments(
                            text=msg_text,
                            text_color=msg_color,
                            arguments=self.data.get_arguments(msg),
                            argument_color=COLOR_ARGUMENTS
                        ))
                        if has_lf:
                            tree_item_data["text"].append(["  ...click Details for whole message.", COLOR_INFO_MSG])

                        tree_item.setData(0, Qt.UserRole, tree_item_data)

                        # self._colorize_tree_item(tree_item=tree_item, item_type="msg")
                        log_item.addChild(tree_item)
                        msg_tree.append(msg)
                        count_added_messages += 1
                # Remove missing logs
                for msg in msg_tree:
                    if msg not in msg_data:
                        item_index = None
                        for i in range(log_item.childCount()):
                            if log_item.child(i).data(0, Qt.UserRole)["data"] == msg:
                                item_index = i
                                break
                        if item_index is not None:
                            log_item.takeChild(item_index)
                            count_removed_messages += 1
        
        self._update_tree_items_counters()
        self.update_menu()
        self._show_last_item()
        self.lbl_title.setText(f"{self._style.lbl_title.text} ({self.data.get_msg_count()} messages)")
        return (count_added_messages, count_removed_messages)

    def _update_tree_items_counters(self) -> None:
        # DATES
        for index in range(self.tree_msg.topLevelItemCount()):
            top_item = self.tree_msg.topLevelItem(index)
            date = top_item.data(0, Qt.UserRole)["data"]
            data = top_item.data(0, Qt.UserRole)
            data["text"][1][0] = f"({len(self.data.get_list_log_names_for_date(date))} logs, {self.data.get_msg_count(date=date)} messages in total.)"
            top_item.setData(0, Qt.UserRole, data)
        
        # LOGS
        for index in range(self.tree_msg.topLevelItemCount()):
            top_item = self.tree_msg.topLevelItem(index)
            date = top_item.data(0, Qt.UserRole)["data"]
            for log_index in range(top_item.childCount()):
                log_item = top_item.child(log_index)
                log_name = log_item.data(0, Qt.UserRole)["data"]
                data = log_item.data(0, Qt.UserRole)
                data["text"][1][0] = f"({self.data.get_msg_count(log_name=log_name, date=date)} messages.)"
                log_item.setData(0, Qt.UserRole, data)
        
        # MESSAGES
        for index in range(self.tree_msg.topLevelItemCount()):
            top_item = self.tree_msg.topLevelItem(index)
            date = top_item.data(0, Qt.UserRole)["data"]
            for log_index in range(top_item.childCount()):
                log_item = top_item.child(log_index)
                log_name = log_item.data(0, Qt.UserRole)["data"]
                for msg_index in range(log_item.childCount()):
                    msg_item = log_item.child(msg_index)
                    msg = msg_item.data(0, Qt.UserRole)["data"]
                    data = msg_item.data(0, Qt.UserRole)
                    data["text"][0][0] = f"[#{self.data.get_msg_counter_in_log(msg)}] "
                    msg_item.setData(0, Qt.UserRole, data)
        
    def insert_arguments(self, text: str, text_color: str, arguments: list, argument_color: str) -> list:
        if not arguments:
            arguments = []
        if not text:
            return []
        
        has_replacements = True
        args_map = []
        map_count = 1
        while has_replacements:
            has_replacements = False
            count = 1
            for argument in arguments:
                if len(arguments) < 10:
                    replace_string = "#" + str(count)
                else:
                    replace_string = "#" + "0" * len(str(count)) + str(count)
                    if text.find(replace_string) == -1:
                        replace_string = "#" + str(count)

                if text.find(replace_string) != -1:
                    has_replacements = True
                
                replace_with = "@~~~@@```@" + "-" * (5 - len(str(map_count))) + str(map_count)
                text = text.replace(replace_string, replace_with, 1)
                args_map.append([replace_with, argument])
                count += 1
                map_count += 1
        
        text_list = text.split("@~~~@")
        result = []
        for i in text_list:
            if i.startswith("@```@"):
                argument_id = "@~~~@@```@" + i[5:10]
                i = i[10:]
                argument_replace = ""
                for j in args_map:
                    if j[0] == argument_id:
                        argument_replace = j[1]
                        break

                result.append([argument_replace, argument_color])
            
            if i:
                result.append([i, text_color])
        
        return result

    def lbl_title_mouse_press(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.drag_mode = {
                "x": self.pos().x(),
                "y": self.pos().y(),
                "cur_x": QCursor.pos().x(),
                "cur_y": QCursor.pos().y()
            }
    
    def lbl_title_mouse_release(self, e: QMouseEvent) -> None:
        self.drag_mode = None

    def lbl_title_mouse_move(self, e: QMouseEvent) -> None:
        if self.drag_mode:
            x = self.drag_mode["x"] + (QCursor.pos().x() - self.drag_mode["cur_x"])
            y = self.drag_mode["y"] + (QCursor.pos().y() - self.drag_mode["cur_y"])
            self.move(x, y)

    def lbl_resize_mouse_press(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.resize_mode = {
                "x": self.width(),
                "y": self.height(),
                "cur_x": QCursor.pos().x(),
                "cur_y": QCursor.pos().y()
            }
    
    def lbl_resize_mouse_release(self, e: QMouseEvent) -> None:
        self.resize_mode = None
    
    def lbl_resize_mouse_move(self, e: QMouseEvent) -> None:
        if self.resize_mode:
            x = self.resize_mode["x"] + (QCursor.pos().x() - self.resize_mode["cur_x"])
            if x < 50:
                x = 50
            y = self.resize_mode["y"] + (QCursor.pos().y() - self.resize_mode["cur_y"])
            if y < 50:
                y = 50
            self.resize(x, y)

    def update_menu(self):
        if self.data.has_data():
            is_enabled = True
        else:
            is_enabled = False
        
        self.lbl_show_date.setEnabled(is_enabled)
        self.lbl_show_log.setEnabled(is_enabled)
        self.lbl_show_msg.setEnabled(is_enabled)

        current_item = self.tree_msg.currentItem()
        if current_item is not None and current_item.data(0, Qt.UserRole)["type"] == "msg":
            self.lbl_show_details.setEnabled(True)
        else:
            self.lbl_show_details.setEnabled(False)

    def on_menu_item_click(self, e: QMouseEvent, item_type: str) -> None:
        if e.button() != Qt.LeftButton:
            return
        
        if item_type.lower() == "dates":
            self._expand_dates(False)
        elif item_type.lower() == "logs":
            self._expand_dates(True)
            self._expand_logs(False)
        elif item_type.lower() == "messages":
            self._expand_dates(True)
            self._expand_logs(True)
        elif item_type.lower() == "details":
            self.show_details()
        self.update_menu()

    def _show_last_item(self):
        if self.tree_msg.topLevelItemCount() - 1 >= 0:
            log_idx = self.tree_msg.topLevelItem(self.tree_msg.topLevelItemCount() - 1).childCount() - 1
            if log_idx >= 0:
                log_item = self.tree_msg.topLevelItem(self.tree_msg.topLevelItemCount() - 1).child(log_idx)
                msg_idx = log_item.childCount() - 1
                if msg_idx >= 0:
                    msg_item = log_item.child(msg_idx)
                    self.tree_msg.setCurrentItem(msg_item)
                    self.tree_msg.scrollToItem(msg_item)
        self.update_menu()

    def _expand_dates(self, value: bool = True) -> None:
        for i in range(self.tree_msg.topLevelItemCount()):
            self.tree_msg.topLevelItem(i).setExpanded(value)

    def _expand_logs(self, value: bool = True) -> None:
        for i in range(self.tree_msg.topLevelItemCount()):
            item = self.tree_msg.topLevelItem(i)
            for j in range(item.childCount()):
                item.child(j).setExpanded(value)

    def on_item_double_click(self, e):
        item = self.tree_msg.currentItem()
        if item is None:
            return
        
        if item.data(0, Qt.UserRole)["type"] == "msg":
            self.show_details()

    def show_details(self, tree_item: QTreeWidgetItem = None) -> None:
        item = self.tree_msg.currentItem()
        if item is None:
            return
        
        msg_id = item.data(0, Qt.UserRole)["data"]
        if item.data(0, Qt.UserRole)["type"] != "msg":
            return

        w = 750
        h = 330
        
        for item in self.details_frames:
            if item.msg_id == msg_id:
                self.details_frames.remove(item)
                item.close()
                break

        # Set position
        desktop = QDesktopWidget()
        x = QCursor.pos().x() - int(w / 2)
        if x < 0:
            x = 0
        if x + w > desktop.width() - 10:
            x = desktop.width() - 10 - w

        y = QCursor.pos().y() + 20
        if y + h > desktop.height() - 30:
            y = QCursor.pos().y() - h - 40
            if y < 0:
                y = 0

        if UTILS.UTILS_Settings.KEEP_LOG_WINDOW_ON_TOP:
            run_detail_window_on_top = True

        msg_details_frame = MessageDetails(
                parent_widget=self,
                msg_id=msg_id,
                data=self.data,
                pos=(x, y),
                size=(w, h),
                show_win=False,
                run_on_top=run_detail_window_on_top
                )
        msg_details_frame.move(x, y)
        msg_details_frame.resize(w, h)
        msg_details_frame.show()

        self.details_frames.append(msg_details_frame)

    def _define_widgets(self) -> None:
        # Main
        self.tree_msg = QTreeWidget(self)
        self.lbl_title = QLabel(self)
        self.btn_close = QPushButton(self)
        self.lbl_resize = QLabel(self)
        # Menu
        self.lbl_show_date = QLabel(self)
        self.lbl_show_log = QLabel(self)
        self.lbl_show_msg = QLabel(self)
        self.lbl_show_details = QLabel(self)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            self.close()
        elif a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return:
            self.show_details()

        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        for item in self.details_frames:
            item.close()
        
        self.details_frames.clear()

        self.tree_msg.setItemDelegate(None)

        if self.dialog_close_feedback:
            self.dialog_close_feedback()

        self.deleteLater()
        return super().closeEvent(a0)

    def close_me(self):
        self.close()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        w = self.contentsRect().width() - 20
        h = self.contentsRect().height()
        
        # Main
        if w < 10:
            w = 10
        tree_h = self.contentsRect().height() - (self.tree_msg.pos().y() + 10)
        if tree_h < 10:
            tree_h = 10

        self.lbl_title.resize(w, self.lbl_title.height())
        self.tree_msg.resize(w, tree_h)

        # Menu
        spacer_from_tree = 5 + self.lbl_show_details.height()
        min_x = 10
        
        w += 20
        x_msg = w - (self.lbl_show_msg.width() + 10)
        x_log = x_msg - (self.lbl_show_log.width() + 10)
        x_date = x_log - (self.lbl_show_date.width() + 10)
        x_details = x_date - (self.lbl_show_details.width() + 10)

        if x_details >= min_x:
            self.lbl_show_details.move(x_details, self.tree_msg.pos().y() - spacer_from_tree)
            self.lbl_show_details.setVisible(True)
        else:
            self.lbl_show_details.setVisible(False)
        
        if x_date >= min_x:
            self.lbl_show_date.move(x_date, self.tree_msg.pos().y() - spacer_from_tree)
            self.lbl_show_date.setVisible(True)
        else:
            self.lbl_show_date.setVisible(False)
        
        if x_log >= min_x:
            self.lbl_show_log.move(x_log, self.tree_msg.pos().y() - spacer_from_tree)
            self.lbl_show_log.setVisible(True)
        else:
            self.lbl_show_log.setVisible(False)
        
        if x_msg >= min_x:
            self.lbl_show_msg.move(x_msg, self.tree_msg.pos().y() - spacer_from_tree)
            self.lbl_show_msg.setVisible(True)
        else:
            self.lbl_show_msg.setVisible(False)

        self.btn_close.move(w - (self.btn_close.width() + 5), 5)

        self.lbl_resize.move(w - self.lbl_resize.width(), h - self.lbl_resize.height())
        
        return super().resizeEvent(a0)

    def _define_widgets_appearance(self) -> None:
        # Dialog
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        if UTILS.UTILS_Settings.KEEP_LOG_WINDOW_ON_TOP:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        if self._style.dialog.frameless:
            self.setWindowFlag(Qt.FramelessWindowHint)

        if self._style.dialog.x is not None:
            self.move(self._style.dialog.x, self.pos().y())
        if self._style.dialog.y is not None:
            self.move(self.pos().x(), self._style.dialog.x)
        if self._style.dialog.width is not None:
            self.resize(self._style.dialog.width, self.height())
        if self._style.dialog.height:
            self.resize(self.width(), self._style.dialog.height)
        if self._style.dialog.title is not None:
            self.setWindowTitle(self._style.dialog.title)
        if self._style.dialog.icon_path:
           self.setWindowIcon(QIcon(QPixmap(self._style.dialog.icon_path)))
        self.setStyleSheet(self._style.dialog.stylesheet)
        
        # Title
        self.lbl_title.move(10, 10)
        self.lbl_title.resize(self.width() - 20, 31)
        font = self.lbl_title.font()
        font.setPointSize(12)
        self.lbl_title.setFont(font)
        self.lbl_title.setText(self._style.lbl_title.text)
        self.lbl_title.setStyleSheet(self._style.lbl_title.stylesheet)

        # Close Button
        if self._style.dialog.close_icon_path:
            self.btn_close.setIcon(QIcon(QPixmap(self._style.dialog.close_icon_path)))
        else:
            self.btn_close.setText("X")
        self.btn_close.setStyleSheet(f"QPushButton {{background-color: {self._style.dialog.get_stylesheet_property('bg_color')}; color: #ffff00;}} QPushButton:hover {{background-color: #aaaaff;}}")
        self.btn_close.resize(17, 17)
        self.btn_close.setIconSize(QSize(17, 17))
        self.btn_close.clicked.connect(self.close_me)

        # Resize Label
        self.lbl_resize.setStyleSheet("QLabel {background-color: #ff0000;} QLabel:hover {background-color: #00ff00;}")
        self.lbl_resize.resize(10, 10)
        self.lbl_resize.setCursor(Qt.SizeFDiagCursor)
        
        # Tree MSG
        self.tree_msg.move(10, self.lbl_title.pos().y() + self.lbl_title.height() + 10)
        self.tree_msg.setStyleSheet(self._style.tree_msg.stylesheet)
        self.tree_msg.setHeaderHidden(True)
        self.tree_msg.setItemDelegate(ColoredTextDelegate())

        # Menu
        menu_labels = [
            [self.lbl_show_details, "Details"],
            [self.lbl_show_date, "Dates"],
            [self.lbl_show_log, "Logs"],
            [self.lbl_show_msg, "Messages"]
        ]
        for label_item in menu_labels:
            item: QLabel = label_item[0]

            item.setText(label_item[1])

            item.setStyleSheet(self._style.menu_label.stylesheet)
            item.adjustSize()
            # Set cursor to pointing hand
            item.setCursor(QCursor(Qt.PointingHandCursor))
            item.mousePressEvent = lambda e, item_type=label_item[1]: self.on_menu_item_click(e, item_type)

        






if __name__ == "__main__":
    app = QApplication([])
    src_dict = [
        {
            "id": "1",
            "date": "29.09.1975.",
            "time": "14:22:33",
            "log_name": "Log #1",
            "message": {
                    "date": "29.09.1975",
                    "time": "14:22:55",
                    "is_exception": False,
                    "is_warning": False,
                    "important_level": "low",
                    "text": "Testing #1 application message",
                    "arguments": ["MyJournal"],
                    "variables": [["number", 100], ["text", "some string"]],
                    "call_stack": [
                        {
                            "function_name": "close_me(self)",
                            "function_code": "close_me(self):\n    self.widget_handler.close_me()\n    self.close()",
                            "filename": "some/file/name",
                            "module": "some_module",
                            "class": "some_class",
                            "line_number": 123,
                            "line_content": "print me code",
                            "file_path": "some/path/to/file"
                        },
                    ]
            }
        },
    ]
    viewer = LogMessageViewer(parent_widget=None, source_messages=src_dict, theme="dark")
    viewer.resize(viewer.width(), 400)

    app.exec_()

