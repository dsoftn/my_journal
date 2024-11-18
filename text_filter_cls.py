from PyQt5.QtWidgets import QFrame, QPushButton, QTextEdit, QWidget, QDialog, QLabel, QComboBox, QGroupBox
from PyQt5.QtGui import QIcon, QFont, QResizeEvent, QColor, QMouseEvent, QTextCharFormat, QBrush, QCursor
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import uic, QtGui

from cyrtranslit import to_latin

import settings_cls
import utility_cls
import UTILS
import qwidgets_util_cls


class FilterResults(QDialog):
    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget, data: list, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("filter_results_ui_file_path"), self)

        # Define variables
        self._parent_widget = parent_widget
        self.data = data
        self.textbox_color_map = []

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()

        self._populate_widgets()
        self._load_win_position()

        self.load_widgets_handler()

        # Connect events with slots
        self.get_appv("signal").signal_app_settings_updated.connect(self.setting_updated)

        self.btn_show_setup.clicked.connect(self.show_setup)
        self.lbl_setup_close.mousePressEvent = self.show_setup
        self.cmb_item.currentIndexChanged.connect(self.update_data)

        self.show()
        self._resize_me()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["FilterResults"])

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_item, self.lbl_filter_text, self.lbl_doc_text, self.lbl_filter_text_val])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_QPushButton(self.btn_show_setup)
        # Add Labels as PushButtons
        self.widget_handler.add_QPushButton(self.lbl_setup_close)

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_doc_text)

        # Add Selection Widgets
        self.widget_handler.add_Selection_Widget(self.cmb_item)

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def show_setup(self, e: QMouseEvent = None):
        if e and e.button() != Qt.LeftButton:
            return

        self.frm_setup.setVisible(not self.frm_setup.isVisible())
        self._resize_me()

    def _populate_widgets(self):
        self.cmb_item.clear()

        for idx, item in enumerate(self.data):
            self.cmb_item.addItem(f"ID: {item['id']} | FILTER: {item['filter_text']}", idx)
        
        if self.data:
            # Set last item as current
            self.cmb_item.setCurrentIndex(len(self.data) - 1)
        self.update_data()

    def update_data(self):
        if not self.cmb_item.currentText():
            return
        
        search_result_item = self.data[self.cmb_item.currentData()]

        self.lbl_filter_text_val.setText(search_result_item["filter_text"])
        
        self.lbl_setup_matchcase.setText(self._colorize_property(self.getl("filter_results_lbl_setup_matchcase_text"), search_result_item["match_case"]))
        self.lbl_setup_whole_words.setText(self._colorize_property(self.getl("filter_results_lbl_setup_whole_words_text"), search_result_item["whole_words"]))
        self.lbl_setup_serbian_chars.setText(self._colorize_property(self.getl("filter_results_lbl_setup_serbian_chars_text"), search_result_item["serbian_chars"]))
        self.lbl_setup_cyr_to_latin.setText(self._colorize_property(self.getl("filter_results_lbl_setup_cyr_to_latin_text"), search_result_item["translate_cyrillic"]))
        self.lbl_setup_parenthesis.setText(self._colorize_property(self.getl("filter_results_lbl_setup_parenthesis_text"), search_result_item["parenthesis"]))
        self.lbl_setup_exact_string.setText(self._colorize_property(self.getl("filter_results_lbl_setup_exact_string_text"), search_result_item["exact_string"]))
        self.lbl_setup_and_operator.setText(self._colorize_property(self.getl("filter_results_lbl_setup_and_operator_text"), search_result_item["and_operators"]))
        self.lbl_setup_or_operator.setText(self._colorize_property(self.getl("filter_results_lbl_setup_or_operator_text"), search_result_item["or_operators"]))
        self.lbl_setup_not_operator.setText(self._colorize_property(self.getl("filter_results_lbl_setup_not_operator_text"), search_result_item["not_operators"]))
        self.lbl_setup_space_as_and.setText(self._colorize_property(self.getl("filter_results_lbl_setup_space_as_and_text"), search_result_item["space_as_and_operator"]))

        # Document textbox
        self.txt_doc_text.setPlainText(search_result_item["document_text"])

        bg_color_valid = self.getv("filter_results_doc_textbox_color_valid_bg")
        fg_color_valid = self.getv("filter_results_doc_textbox_color_valid_fg")
        font_bold_valid = self.getv("filter_results_doc_textbox_valid_font_bold")
        
        bg_color_invalid_whole_word = self.getv("filter_results_doc_textbox_color_invalid_whole_word_bg")
        fg_color_invalid_whole_word = self.getv("filter_results_doc_textbox_color_invalid_whole_word_fg")
        font_bold_invalid_whole_word = self.getv("filter_results_doc_textbox_invalid_whole_word_font_bold")

        bg_color_invalid_matchcase = self.getv("filter_results_doc_textbox_color_invalid_matchcase_bg")
        fg_color_invalid_matchcase = self.getv("filter_results_doc_textbox_color_invalid_matchcase_fg")
        font_bold_invalid_matchcase = self.getv("filter_results_doc_textbox_invalid_matchcase_font_bold")

        bg_color_invalid_all = self.getv("filter_results_doc_textbox_color_invalid_all_bg")
        fg_color_invalid_all = self.getv("filter_results_doc_textbox_color_invalid_all_fg")
        font_bold_invalid_all = self.getv("filter_results_doc_textbox_invalid_all_font_bold")

        filter_text_tt = ""
        self.textbox_color_map = []

        for item in search_result_item["document_map"]:
            text = item["text"]
            if not item["map_normal"]:
                item["desc"] = self._colorize_property(self.getl("filter_results_item_tooltip_not_found"), text, color="#00ffff")
                filter_text_tt += item["desc"] + "<br><br>"
                continue
            
            added_to_filter_text_tt = [False, False, False, False]
            for element in item["map_normal"]:
                if element not in item["map_whole_words"] and element not in item["map_matchcase"]:
                    self.textbox_color_map.append({
                        "pos": element,
                        "text": text,
                        "document": item["document"],
                        "desc": self._colorize_property(self.getl("filter_results_item_tooltip_invalid_all"), text, color="#00ffff")
                    })
                    if not added_to_filter_text_tt[0]:
                        filter_text_tt += self.textbox_color_map[-1]["desc"] + "<br><br>"
                        added_to_filter_text_tt[0] = True
                    self._colorize_textbox(self.textbox_color_map[-1], font_bold=font_bold_invalid_all, bg_color=bg_color_invalid_all, fg_color=fg_color_invalid_all)
                elif element not in item["map_whole_words"]:
                    self.textbox_color_map.append({
                        "pos": element,
                        "text": text,
                        "document": item["document"],
                        "desc": self._colorize_property(self.getl("filter_results_item_tooltip_invalid_whole_word"), text, color="#00ffff")
                    })
                    if not added_to_filter_text_tt[1]:
                        filter_text_tt += self.textbox_color_map[-1]["desc"] + "<br><br>"
                        added_to_filter_text_tt[1] = True
                    self._colorize_textbox(self.textbox_color_map[-1], font_bold=font_bold_invalid_whole_word, bg_color=bg_color_invalid_whole_word, fg_color=fg_color_invalid_whole_word)

                elif element not in item["map_matchcase"]:
                    self.textbox_color_map.append({
                        "pos": element,
                        "text": text,
                        "document": item["document"],
                        "desc": self._colorize_property(self.getl("filter_results_item_tooltip_invalid_matchcase"), text, color="#00ffff")
                    })
                    if not added_to_filter_text_tt[2]:
                        filter_text_tt += self.textbox_color_map[-1]["desc"] + "<br><br>"
                        added_to_filter_text_tt[2] = True
                    self._colorize_textbox(self.textbox_color_map[-1], font_bold=font_bold_invalid_matchcase, bg_color=bg_color_invalid_matchcase, fg_color=fg_color_invalid_matchcase)
                else:
                    self.textbox_color_map.append({
                        "pos": element,
                        "text": text,
                        "document": item["document"],
                        "desc": self._colorize_property(self.getl("filter_results_item_tooltip_valid"), search_result_item["filter_text"], color="#55ff00", extra_property=[["#2", text, "#00ffff", True]])
                    })
                    if not added_to_filter_text_tt[3]:
                        filter_text_tt += self.textbox_color_map[-1]["desc"] + "<br><br>"
                        added_to_filter_text_tt[3] = True
                    self._colorize_textbox(self.textbox_color_map[-1], font_bold=font_bold_valid, bg_color=bg_color_valid, fg_color=fg_color_valid)
        
        self.lbl_filter_text_val.setToolTip(filter_text_tt)

    def _colorize_textbox(self, data: dict, textbox: QTextEdit = None, fg_color: str = "#ffffff", bg_color: str = "#000000", font_bold: bool = True):
        if not textbox:
            textbox = self.txt_doc_text
        
        pos = data["pos"]
        text = data["document"][pos:pos + len(data["text"])]

        # Get cursor and mark text
        cur = textbox.textCursor()
        cur.setPosition(pos)
        cur.movePosition(cur.Right, cur.KeepAnchor, len(text))

        cur.insertHtml(f"<span 'title'='{data['desc']}'>{text}</span>")
        textbox.setTextCursor(cur)

        cur = textbox.textCursor()
        cur.setPosition(pos)
        cur.movePosition(cur.Right, cur.KeepAnchor, len(text))

        # Set bg and fg color and font bold
        format = QTextCharFormat()
        format.setBackground(QBrush(QColor(bg_color)))
        format.setForeground(QBrush(QColor(fg_color)))
        format.setFontWeight(QFont.Bold if font_bold else QFont.Normal)

        cur.mergeCharFormat(format)

        # Move cursor at beginning of text
        cur.setPosition(0)

        # Set cursor
        textbox.setTextCursor(cur)

    def _colorize_property(self, text: str, value, color: str = "#00ffff", font_bold: bool = True, extra_property: list = None):
        if isinstance(value, (list, tuple)):
            value = ", ".join(value)

        text_to_html = utility_cls.TextToHTML(text)
        rule = utility_cls.TextToHtmlRule(text="#1", replace_with=str(value), fg_color=color, font_bold=font_bold)
        text_to_html.add_rule(rule)

        if extra_property:
            for prop in extra_property:
                rule = utility_cls.TextToHtmlRule(text=prop[0], replace_with=prop[1], fg_color=prop[2], font_bold=prop[3])
                text_to_html.add_rule(rule)

        return text_to_html.get_html()

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self._resize_me()

        return super().resizeEvent(a0)

    def _resize_me(self):
        w = self.contentsRect().width() - (self.frm_setup.width() + 10) if self.frm_setup.isVisible() else self.contentsRect().width()
        h = self.contentsRect().height()
        
        self.lbl_filter_text_val.resize(w - 20, self.lbl_filter_text_val.height())
        self.txt_doc_text.resize(w - 20, h - self.txt_doc_text.pos().y() - 10)

        self.frm_setup.move(self.contentsRect().width() - self.frm_setup.width() - 10, 60)
        self.btn_show_setup.move(self.contentsRect().width() - self.btn_show_setup.width() - 10, 30)

    def _load_win_position(self):
        if "filter_results_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("filter_results_win_geometry")
            x = g.setdefault("pos_x", self.pos().x())
            y = g.setdefault("pos_y", self.pos().y())
            width = g.setdefault("width", 1010)
            height = g.setdefault("height", 460)
            self.move(x, y)
            self.resize(width, height)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "filter_results_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("filter_results_win_geometry", {}, save_to_file=True)

        g = self.get_appv("filter_results_win_geometry")
        g["pos_x"] = self.pos().x()
        g["pos_y"] = self.pos().y()
        g["width"] = self.width()
        g["height"] = self.height()

        self.get_appv("cm").remove_all_context_menu()
        UTILS.DialogUtility.on_closeEvent(self)
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["FilterResults"])

    def setting_updated(self, data: dict):
        self._setup_widgets_apperance(settings_updated=True)

    def _setup_widgets(self):
        self.lbl_item: QLabel = self.findChild(QLabel, "lbl_item")
        self.cmb_item: QComboBox = self.findChild(QComboBox, "cmb_item")
        self.lbl_filter_text: QLabel = self.findChild(QLabel, "lbl_filter_text")
        self.lbl_filter_text_val: QLabel = self.findChild(QLabel, "lbl_filter_text_val")
        self.lbl_doc_text: QLabel = self.findChild(QLabel, "lbl_doc_text")
        self.txt_doc_text: QTextEdit = self.findChild(QTextEdit, "txt_doc_text")
        self.btn_show_setup: QPushButton = self.findChild(QPushButton, "btn_show_setup")

        self.frm_setup: QFrame = self.findChild(QFrame, "frm_setup")
        self.lbl_setup_title: QLabel = self.findChild(QLabel, "lbl_setup_title")
        self.lbl_setup_matchcase: QLabel = self.findChild(QLabel, "lbl_setup_matchcase")
        self.lbl_setup_whole_words: QLabel = self.findChild(QLabel, "lbl_setup_whole_words")
        self.lbl_setup_serbian_chars: QLabel = self.findChild(QLabel, "lbl_setup_serbian_chars")
        self.lbl_setup_cyr_to_latin: QLabel = self.findChild(QLabel, "lbl_setup_cyr_to_latin")
        self.grp_setup_operators: QGroupBox = self.findChild(QGroupBox, "grp_setup_operators")
        self.lbl_setup_parenthesis: QLabel = self.findChild(QLabel, "lbl_setup_parenthesis")
        self.lbl_setup_exact_string: QLabel = self.findChild(QLabel, "lbl_setup_exact_string")
        self.lbl_setup_and_operator: QLabel = self.findChild(QLabel, "lbl_setup_and_operator")
        self.lbl_setup_or_operator: QLabel = self.findChild(QLabel, "lbl_setup_or_operator")
        self.lbl_setup_not_operator: QLabel = self.findChild(QLabel, "lbl_setup_not_operator")
        self.lbl_setup_space_as_and: QLabel = self.findChild(QLabel, "lbl_setup_space_as_and")
        self.lbl_setup_close: QLabel = self.findChild(QLabel, "lbl_setup_close")

    def _setup_widgets_text(self):
        self.lbl_item.setText(self.getl("filter_results_lbl_item_text"))
        self.lbl_filter_text.setText(self.getl("filter_results_lbl_filter_text_text"))
        self.lbl_doc_text.setText(self.getl("filter_results_lbl_doc_text_text"))
        self.btn_show_setup.setText(self.getl("filter_results_btn_show_setup_text"))

        self.lbl_setup_title.setText(self.getl("filter_results_lbl_setup_title_text"))
        self.grp_setup_operators.setTitle(self.getl("filter_results_grp_setup_operators_title"))

        self.lbl_setup_matchcase.setText(self.getl("filter_results_lbl_setup_matchcase_text"))
        self.lbl_setup_matchcase.setToolTip(self.getl("filter_results_lbl_setup_matchcase_tt"))
        self.lbl_setup_whole_words.setText(self.getl("filter_results_lbl_setup_whole_words_text"))
        self.lbl_setup_whole_words.setToolTip(self.getl("filter_results_lbl_setup_whole_words_tt"))
        self.lbl_setup_serbian_chars.setText(self.getl("filter_results_lbl_setup_serbian_chars_text"))
        self.lbl_setup_serbian_chars.setToolTip(self.getl("filter_results_lbl_setup_serbian_chars_tt"))
        self.lbl_setup_cyr_to_latin.setText(self.getl("filter_results_lbl_setup_cyr_to_latin_text"))
        self.lbl_setup_cyr_to_latin.setToolTip(self.getl("filter_results_lbl_setup_cyr_to_latin_tt"))
        self.lbl_setup_parenthesis.setText(self.getl("filter_results_lbl_setup_parenthesis_text"))
        self.lbl_setup_parenthesis.setToolTip(self.getl("filter_results_lbl_setup_parenthesis_tt"))
        self.lbl_setup_exact_string.setText(self.getl("filter_results_lbl_setup_exact_string_text"))
        self.lbl_setup_exact_string.setToolTip(self.getl("filter_results_lbl_setup_exact_string_tt"))
        self.lbl_setup_and_operator.setText(self.getl("filter_results_lbl_setup_and_operator_text"))
        self.lbl_setup_and_operator.setToolTip(self.getl("filter_results_lbl_setup_and_operator_tt"))
        self.lbl_setup_or_operator.setText(self.getl("filter_results_lbl_setup_or_operator_text"))
        self.lbl_setup_or_operator.setToolTip(self.getl("filter_results_lbl_setup_or_operator_tt"))
        self.lbl_setup_not_operator.setText(self.getl("filter_results_lbl_setup_not_operator_text"))
        self.lbl_setup_not_operator.setToolTip(self.getl("filter_results_lbl_setup_not_operator_tt"))
        self.lbl_setup_space_as_and.setText(self.getl("filter_results_lbl_setup_space_as_and_text"))
        self.lbl_setup_space_as_and.setToolTip(self.getl("filter_results_lbl_setup_space_as_and_tt"))

    def _setup_widgets_apperance(self, settings_updated: bool = False):
        self.setStyleSheet(self.getv("filter_results_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("filter_results_win_icon_path")))
        self.setWindowTitle(self.getl("filter_results_win_title_text"))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.lbl_item.setStyleSheet(self.getv("filter_results_labels_stylesheet"))
        self.lbl_filter_text.setStyleSheet(self.getv("filter_results_labels_stylesheet"))
        self.lbl_doc_text.setStyleSheet(self.getv("filter_results_labels_stylesheet"))

        self.cmb_item.setStyleSheet(self.getv("filter_results_cmb_item_stylesheet"))
        self.lbl_filter_text_val.setStyleSheet(self.getv("filter_results_lbl_filter_text_val_stylesheet"))
        self.txt_doc_text.setStyleSheet(self.getv("filter_results_txt_doc_text_stylesheet"))
        self.btn_show_setup.setStyleSheet(self.getv("filter_results_btn_show_setup_stylesheet"))

        self.frm_setup.setStyleSheet(self.getv("filter_results_frm_setup_stylesheet"))
        self.grp_setup_operators.setStyleSheet(self.getv("filter_results_grp_setup_operators_stylesheet"))
        self.lbl_setup_title.setStyleSheet(self.getv("filter_results_lbl_setup_title_stylesheet"))
        self.lbl_setup_matchcase.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_whole_words.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_parenthesis.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_exact_string.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_and_operator.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_or_operator.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_not_operator.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))
        self.lbl_setup_space_as_and.setStyleSheet(self.getv("filter_results_property_labels_stylesheet"))

        self.lbl_setup_close.setStyleSheet(self.getv("filter_results_lbl_setup_close_stylesheet"))

        if not settings_updated:
            self.setMinimumSize(400, 200)


class TextFilter:
    """A class for filtering text based on specified criteria.

    Args:
        filter_text (str): The text to search for.
        document_text (str): The document to search within.
        search_whole_words_only (bool): Flag indicating whether to search for whole words only.
        match_case (bool): Flag indicating whether to match the case of the text.
        and_operators (list): List of operators to use for logical AND.
        space_as_and_operator (bool): Flag indicating whether to treat spaces as logical AND operators.
        or_operators (list): List of operators to use for logical OR.
        not_operators (list): List of operators to use for logical NOT.
        exact_string_boundaries (list): List of boundary strings for exact string matching.
        logic_parenthesis (list): List of parenthesis strings for logical grouping.

    Attributes:
        FilterText (str): The text to filter.
        DocumentText (str): The document to search within.
        SearchWholeWordsOnly (bool): Flag indicating whether to search for whole words only.
        MatchCase (bool): Flag indicating whether to match the case of the text.
        AndOperators (list): List of operators to use for logical AND.
        SpaceAsAndOperator (bool): Flag indicating whether to treat spaces as logical AND operators.
        OrOperators (list): List of operators to use for logical OR.
        NotOperators (list): List of operators to use for logical NOT.
        ExactStringBoundaries (list): List of boundary strings for exact string matching.
        LogicParenthesis (list): List of parenthesis strings for logical grouping.

    Methods:
        is_filter_in_document(filter_text: str = None, document_text: str = None) -> bool:
            Checks if the filter text is present in the document text.

        is_any_filter_word_in_document(filter_text: str = None, document_text: str = None) -> bool:
            Checks if any word from the filter text is present in the document text.

    """

    REMOVE_CHARS_FOR_WHOLE_WORDS = """.,/!?"'|;:></[]{}=+-_=)(*&^%$#@~`\t\n\\"""
    MAX_CASHE_SIZE = 20
    MAX_HISTORY_SIZE = 500

    def __init__(self,
                 filter_text: str = None,
                 document_text: str = None,
                 search_whole_words_only: bool = False,
                 match_case: bool = False,
                 ignore_serbian_characters: bool = False,
                 translate_cyrillic_to_latin: bool = False,
                 and_operators: list = ["and", "&"],
                 space_as_and_operator: bool = True,
                 or_operators: list = ["or", "/"],
                 not_operators: list = ["not", "!"],
                 exact_string_boundaries: list = ['""'],
                 logic_parenthesis: list = ["()"]) -> None:
        # sourcery skip: default-mutable-arg
        
        self.__filter_text: str = filter_text
        self.__document_text: str = document_text
        self.__search_whole_words_only: bool = search_whole_words_only
        self.__match_case: bool = match_case
        self.__ignore_serbian_characters: bool = ignore_serbian_characters
        self.__translate_cyrillic_to_latin: bool = translate_cyrillic_to_latin
        self.__operators = []
        self.__and_operators: list = self._validate_operators(and_operators)
        self.__space_as_and_operator: bool = space_as_and_operator
        self.__or_operators: list = self._validate_operators(or_operators)
        self.__not_operators: list = self._validate_operators(not_operators)
        self.__exact_string_boundaries: list = self._validate_operators(exact_string_boundaries, boundaries_and_parenthesis=True)
        self.__exact_string_boundaries_open_string = self._find_open_strings(self.__exact_string_boundaries)
        self.__exact_string_boundaries_close_string = self._find_close_strings(self.__exact_string_boundaries)
        self.__logic_parenthesis: list = self._validate_operators(logic_parenthesis, boundaries_and_parenthesis=True)
        self.__logic_parenthesis_open_string = self._find_open_strings(self.__logic_parenthesis)
        self.__logic_parenthesis_close_string = self._find_close_strings(self.__logic_parenthesis)

        self.__filter_cashe = None
        self.__search_history = []

    def is_filter_in_document(self, filter_text: str = None, document_text: str = None, ignore_cashe: bool = False) -> bool:
        if filter_text is not None:
            self.FilterText = filter_text
        if document_text is not None:
            self.DocumentText = document_text

        return self._filter_apply(ignore_cashe=ignore_cashe)
    
    def is_any_filter_word_in_document(self, filter_text: str = None, document_text: str = None) -> bool:
        if filter_text is not None:
            self.FilterText = filter_text
        if document_text is not None:
            self.DocumentText = document_text
            
        return self._filter_apply(partial=True)

    def clear_search_history(self, item_id: str = None):
        if item_id is None:
            self.__search_history = []
        else:
            remove_items = [
                idx
                for idx, item in enumerate(self.__search_history)
                if item.get("id") == item_id
            ]
            remove_items.reverse()
            for idx in remove_items:
                self.__search_history.pop(idx)

    def save_search_history(self, item_id: str):
        status_dict = self._get_status_dict()
        status_dict["id"] = item_id
        status_dict["filter_text"] = self.FilterText
        status_dict["document_text"] = self.DocumentText
        status_dict["document_map"] = self._map_filter_in_document()

        self.clear_search_history(item_id=item_id)
        self.__search_history.append(status_dict)

        if len(self.__search_history) > self.MAX_HISTORY_SIZE:
            self.__search_history.pop(0)

    def _map_filter_in_document(self) -> list:
        string_list = self._parse_filter(self.FilterText)

        filter_text_slices = []
        for item in string_list:
            if item[0] not in ["t", "b"]:
                continue

            item_text = item[1] if item[0] == "t" else item[1][item[3]:len(item[1]) - item[3]]
            filter_text_slices.append([item[0], item_text])

        doc_normal = self.clear_serbian_chars(self.DocumentText, keep_same_lenght=True) if self.__ignore_serbian_characters else self.DocumentText
        doc_whole_words = self.clear_serbian_chars(self._prepare_for_whole_words(self.DocumentText), keep_same_lenght=True) if self.__ignore_serbian_characters else self._prepare_for_whole_words(self.DocumentText)

        result = []
        for item in filter_text_slices:
            item_text = self.clear_serbian_chars(item[1], keep_same_lenght=True) if self.__ignore_serbian_characters else item[1]
            result.append(
                {
                    "type": item[0],
                    "text": item_text,
                    "document": self.DocumentText,
                    "map_normal": self._map_found_positions(item_text.lower(), doc_normal.lower()),
                    "map_whole_words": self._map_found_positions(f" {item_text.lower()} ", doc_whole_words.lower(), offset=0),
                    "map_matchcase": self._map_found_positions(item_text, doc_normal),
                    "map_matchcase_whole_words": self._map_found_positions(f" {item_text} ", doc_whole_words, offset=0)
                }
            )
        
        return result
        
    def _map_found_positions(self, text: str, document: str, offset: int = 0) -> list:
        result = []
        pos = 0
        while True:
            pos = document.find(text, pos)
            if pos == -1:
                break
            result.append(pos + offset)
            pos += len(text)
        
        return result

    def show_search_history(self, settings: settings_cls.Settings, qdialog_parent_widget: QWidget, item_id: str = None):
        if item_id is None:
            FilterResults(settings=settings, parent_widget=qdialog_parent_widget, data=self.__search_history)
            return
        
        result = [x for x in self.__search_history if x.get("id") == item_id]
        FilterResults(settings=settings, parent_widget=qdialog_parent_widget, data=result)

    def has_search_history(self, item_id: str = None) -> bool:
        if item_id is None:
            return len(self.__search_history) > 0
        else:
            return any(item.get("id") == item_id for item in self.__search_history)

    def _prepare_for_whole_words(self, txt: str) -> str:
        for i in self.REMOVE_CHARS_FOR_WHOLE_WORDS:
            txt = txt.replace(i, " ")
        return f" {txt} "

    def _filter_apply(self, partial: bool = False, ignore_cashe: bool = False) -> bool:
        # Check for MatchCase
        filter_text = self.FilterText if self.MatchCase else self.FilterText.lower()
        document_text = self.DocumentText if self.MatchCase else self.DocumentText.lower()

        # Check for serbian characters
        filter_text = self.clear_serbian_chars(filter_text) if self.IgnoreSerbianCharacters else filter_text
        document_text = self.clear_serbian_chars(document_text) if self.IgnoreSerbianCharacters else document_text

        # Check for translate cyrillic to latin
        filter_text = self.cirilica_u_latinicu(filter_text) if self.TranslateCyrillicToLatin else filter_text
        document_text = self.cirilica_u_latinicu(document_text) if self.TranslateCyrillicToLatin else document_text

        # Get filter elements (check for cashe)
        if cashe_data := self._get_cashe_data():
            if ignore_cashe:
                filter_elements = self._parse_filter(filter_text)
            else:
                filter_elements = cashe_data
        else:
            filter_elements = self._parse_filter(filter_text)
            if not ignore_cashe:
                self._update_cashe(filter_elements)

        # Validate filter
        if partial:
            return self._validate_partial_filter(filter_elements, document_text, self.SearchWholeWordsOnly)
        else:
            return self._validate_filter(filter_elements, document_text, self.SearchWholeWordsOnly)

    def _get_cashe_data(self):
        if self.__filter_cashe is None:
            return None
        
        for item in self.__filter_cashe:
            is_valid = True

            if self.__filter_text != item["filter_text"]:
                is_valid = False
            if self.__match_case != item["match_case"]:
                is_valid = False
            if self.__search_whole_words_only != item["whole_words"]:
                is_valid = False
            if self.__ignore_serbian_characters != item["serbian_chars"]:
                is_valid = False
            if self.__translate_cyrillic_to_latin != item["translate_cyrillic"]:
                is_valid = False
            if self.__or_operators != item["or_operators"]:
                is_valid = False
            if self.__and_operators != item["and_operators"]:
                is_valid = False
            if self.__not_operators != item["not_operators"]:
                is_valid = False
            if self.__exact_string_boundaries != item["exact_string"]:
                is_valid = False
            if self.__logic_parenthesis != item["parenthesis"]:
                is_valid = False
            if self.__space_as_and_operator != item["space_as_and_operator"]:
                is_valid = False
            
            if is_valid:
                return item.get("filter_elements")
        
        return None
    
    def _update_cashe(self, data: list):
        if data is None:
            return
        
        if self.__filter_cashe is None:
            self.__filter_cashe = []
            
        if self._get_cashe_size() > self.MAX_CASHE_SIZE:
            self.__filter_cashe.pop(0)
        
        self.__filter_cashe.append(self._get_status_dict(data))

    def _get_status_dict(self, data: list = None) -> dict:
        return {
            "filter_text": self.__filter_text,
            "document_text": self.__document_text,
            "match_case": self.__match_case,
            "whole_words": self.__search_whole_words_only,
            "serbian_chars": self.__ignore_serbian_characters,
            "translate_cyrillic": self.__translate_cyrillic_to_latin,
            "or_operators": self.__or_operators,
            "and_operators": self.__and_operators,
            "not_operators": self.__not_operators,
            "exact_string": self.__exact_string_boundaries,
            "parenthesis": self.__logic_parenthesis,
            "space_as_and_operator": self.__space_as_and_operator,
            "filter_elements": list(data) if data is not None else None,
        }

    def _get_cashe_size(self) -> int:
        return len(self.__filter_cashe) if self.__filter_cashe is not None else 0

    def _validate_partial_filter(self, filter_elements: list, document_text: str, search_whole_words_only: bool) -> bool:
        if filter_elements is None:
            return None
        
        for item in filter_elements:

            item_text = item[1].strip()

            # Remove boundaries if item is boundary
            if item[0] == "b":
                item_text = item_text[item[3]:len(item[1]) - item[3]]

            # Add spaces to item if whole words only
            if search_whole_words_only and item_text:
                if self._is_whole_word_in_document(item_text, document_text):
                    return True
            elif item[0] in ["t", "b"] and item_text in document_text:
                return True

        return False

    def _validate_filter(self, filter_elements: list, document_text: str, search_whole_words_only: bool) -> bool:
        if filter_elements is None:
            return None

        if not self.MatchCase:
            document_text = document_text.lower()

        validation_string = ""
        for item in filter_elements:

            item_text = item[1].strip()

            # Remove boundaries if item is boundary
            if item[0] == "b":
                item_text = item_text[item[3]:len(item[1]) - item[3]]

            # Add item to validation string
            if item[0].startswith("o_"):
                validation_string += f" {item[1]} "
            elif item[0] in ["t", "b"]:
                if search_whole_words_only:
                    is_in_document = self._is_whole_word_in_document(item_text, document_text)
                else:
                    is_in_document = item_text in document_text
                validation_string += f" {is_in_document} "
            elif item[0] == "po":
                validation_string += "("
            elif item[0] == "pc":
                validation_string += ")"

        # Remove AND operators from beginning and end
        while True:
            validation_string = validation_string.strip()
            can_break = True
            
            if validation_string.startswith("and "):
                validation_string = validation_string[4:]
                can_break = False
            if validation_string.endswith(" and"):
                validation_string = validation_string[:-4]
                can_break = False
            if validation_string.find("( ") != -1:
                validation_string = validation_string.replace("( ", "(")
                can_break = False
            if validation_string.find(" )") != -1:
                validation_string = validation_string.replace(" )", ")")
                can_break = False
            if validation_string.find("(and") != -1:
                validation_string = validation_string.replace("(and", "(")
                can_break = False
            if validation_string.find("and)") != -1:
                validation_string = validation_string.replace("and)", ")")
                can_break = False
            
            if can_break:
                break

        try:
            result = eval(validation_string)
        except Exception:
            result = None

        return result            

    def _is_whole_word_in_document(self, item_text: str, document_text: str) -> bool:
        if item_text not in document_text:
            return False
        
        word_bounds = self.REMOVE_CHARS_FOR_WHOLE_WORDS + " "

        result = False
        
        pos = 0
        while True:
            pos = document_text.find(item_text, pos)
            if pos == -1:
                break

            left_char = True if pos == 0 or document_text[pos - 1] in word_bounds else False
            right_char = True if pos + len(item_text) == len(document_text) or document_text[pos + len(item_text)] in word_bounds else False
            if left_char and right_char:
                result = True
                break
            pos += 1

        return result

    def _parse_filter(self, filter_text: str) -> list:
        string_list = self._parse_boundaries(filter_text, self.__exact_string_boundaries_open_string, self.__exact_string_boundaries_close_string, marker="b")
        string_list = self._parse_parenthesis(string_list)
        string_list = self._find_logic_operators(string_list)
        string_list = self._normalize_filter_list(string_list)
        
        return string_list
            
    def _normalize_filter_list(self, string_list: list) -> list:
        if string_list is None:
            return None
        
        result = []
        operators_in_row = []
        for item in string_list:
            if not item[1] and item[0] == "t":
                continue

            if item[0].startswith("o_"):
                operators_in_row.append(item)
                continue
            else:
                self._add_operators_from_pool(operators_in_row, result)
                operators_in_row = []
            
            result.append(item)
        
        if operators_in_row:
            self._add_operators_from_pool(operators_in_row, result)

        return result
            
    def _add_operators_from_pool(self, operators_in_row: list, result: list) -> list:
        if operators_in_row:
            if other_than_blank_operators := [x for x in operators_in_row if x[0] != "o_blank"]:
                result.extend(other_than_blank_operators)
            else:
                result.append(operators_in_row[0])

    def _split_text_items_in_list(self, string_list: list) -> list:
        result = []
        logic_operators = self.AndOperators + self.OrOperators + self.NotOperators

        for item in string_list:
            if item[0] != "t":
                result.append(item)
                continue

            pos = 0
            agr_text_slice = ""
            for text_slice in item[1].strip().split(" "):
                if self.__space_as_and_operator:
                    result.append(["t", f"{text_slice} ", item[2] + pos, len(text_slice) + 1])
                    pos += len(text_slice) + 1
                    continue
                
                if agr_text_slice and text_slice in logic_operators:
                    result.append(["t", agr_text_slice[:-1], item[2] + pos, len(agr_text_slice)])
                    pos += len(agr_text_slice) - 1
                    agr_text_slice = ""
                else:
                    agr_text_slice += f"{text_slice} "
            
            if agr_text_slice:
                result.append(["t", agr_text_slice[:-1], item[2] + pos, len(agr_text_slice)])

        return result

    def _find_logic_operators(self, string_list: list) -> list:
        if string_list is None:
            return None
        
        string_list = self._split_text_items_in_list(string_list)

        result = []
        for item in string_list:
            if item[0] != "t":
                result.append(item)
                continue

            # Add and operator for each space at the beginning of the string
            if self.__space_as_and_operator:
                result.extend(
                    ["o_blank", "and", item[2] + i, 3]
                    for i in range(len(item[1]) - len(item[1].lstrip()))
                )
            
            # Check if text in item[1] is operator
            if item[1].strip() in self.__and_operators:
                result.append(["o_and", "and", item[2] + len(item[1]) - len(item[1].lstrip()), 3])
            elif item[1].strip() in self.__or_operators:
                result.append(["o_or", "or", item[2] + len(item[1]) - len(item[1].lstrip()), 2])
            elif item[1].strip() in self.__not_operators:
                result.append(["o_not", "not", item[2] + len(item[1]) - len(item[1].lstrip()), 3])
            else:
                # Add striped string
                result.append(["t", item[1].strip(), item[2] + (len(item[1]) - len(item[1].lstrip())), len(item[1].strip())])

            # Add and operator for each space at the end of the string
            if self.__space_as_and_operator:
                result.extend(
                    ["o_blank", "and", item[2] + len(item[1].rstrip()) + i, 3]
                    for i in range(len(item[1]) - len(item[1].rstrip()))
                )
                

        return result

    def _parse_parenthesis(self, string_list: list) -> list:
        # sourcery skip: low-code-quality
        if string_list is None:
            return None

        string = "".join(
            string_item[1] if string_item[0] == "t" else "`" * len(string_item[1])
            for string_item in string_list
        )
        
        # Parse parenthesis
        pos = 0
        parenthesis_list = []
        opened_parenthesis_order = []
        while True:
            # Find all opened parenthesis
            found_opened = []
            for idx, item in enumerate(self.__logic_parenthesis_open_string):
                item_pos = string.find(item, pos)
                if item_pos != -1:
                    found_opened.append([item_pos, idx, "po", item])

            # Find next opened
            if found_opened:
                found_opened.sort(key=lambda x: x[0])
                next_opened: list = found_opened[0]
            else:
                next_opened = [-1]

            # Find all closed parenthesis
            found_closed = []
            for idx, item in enumerate(self.__logic_parenthesis_close_string):
                item_pos = string.find(item, pos)
                if item_pos != -1:
                    found_closed.append([item_pos, idx, "pc", item])

            # Find next closed
            if found_closed:
                found_closed.sort(key=lambda x: x[0])
                next_closed: list = found_closed[0]
            else:
                next_closed = [-1]

            if next_opened[0] == -1 and next_closed[0] == -1:
                if opened_parenthesis_order:
                    return None

                else:
                    break
            
            # Update opened_parenthesis_order with next found
            if next_opened[0] >= 0 and next_opened[0] < next_closed[0]:
                opened_parenthesis_order.append(next_opened)
                parenthesis_list.append(next_opened)
                pos = next_opened[0] + len(self.__logic_parenthesis_open_string[next_opened[1]])
            else:
                if not opened_parenthesis_order:
                    return None

                if opened_parenthesis_order[-1][1] != next_closed[1]:
                    return None

                opened_parenthesis_order.pop()
                parenthesis_list.append(next_closed)
                pos = next_closed[0] + len(self.__logic_parenthesis_close_string[next_closed[1]])
        
        # Check is there any parenthesis
        if not parenthesis_list:
            return string_list

        # Concatenate string lists
        concatenated_string_list = []
        for string_item in string_list:
            if string_item[0] == "t":
                string_list_item_parenthesis = []
                for parenthesis_string_item in parenthesis_list:
                    if parenthesis_string_item[0] in range(string_item[2], string_item[2] + len(string_item[1])):
                        if parenthesis_string_item[2] == "po":
                            string_list_item_parenthesis.append([parenthesis_string_item[2], "", parenthesis_string_item[0], len(self.__logic_parenthesis_open_string[parenthesis_string_item[1]])])
                        elif parenthesis_string_item[2] == "pc":
                            string_list_item_parenthesis.append([parenthesis_string_item[2], "", parenthesis_string_item[0], len(self.__logic_parenthesis_close_string[parenthesis_string_item[1]])])

                if string_list_item_parenthesis:
                    last_pos = 0
                    for string_list_item_parenthesis_item in string_list_item_parenthesis:
                        pos = string_list_item_parenthesis_item[2] - string_item[2]
                        if string_item[1][last_pos:pos]:
                            concatenated_string_list.append(["t", string_item[1][last_pos:pos], string_item[2] + last_pos, pos - last_pos])
                        concatenated_string_list.append(string_list_item_parenthesis_item)
                        last_pos = pos + string_list_item_parenthesis_item[3]

                    if string_item[1][last_pos:]:
                        concatenated_string_list.append(["t", string_item[1][last_pos:], string_item[2] + last_pos, len(string_item[1]) - last_pos])
                else:
                    concatenated_string_list.append(string_item)
            else:
                concatenated_string_list.append(string_item)

        return concatenated_string_list

    def _parse_boundaries(self, string: str, open_strings: list, close_strings: list, marker: str) -> list:
        pos = 0
        boundary_strings = []
        open_positions = []
        last_pos = 0
        while True:
            # Find start
            open_positions = [[string.find(i, pos), idx] for idx, i in enumerate(open_strings) if string.find(i, pos) != -1]
            
            # If no start positions found stop
            if not open_positions:
                if string[pos:]:
                    boundary_strings.append(["t", string[pos:], pos, len(string[pos:])])
                break
        
            # Sort start positions
            open_positions.sort(key=lambda x: x[0])

            # Find end
            for open_position in open_positions:
                close_position = string.find(close_strings[open_position[1]], open_position[0] + len(open_strings[open_position[1]]))
                if close_position != -1:
                    if string[last_pos:open_position[0]]:
                        boundary_strings.append(["t", string[last_pos:open_position[0]], pos, 0])
                    if string[open_position[0]:close_position + len(close_strings[open_position[1]])]:
                        boundary_strings.append([marker, string[open_position[0]:close_position + len(close_strings[open_position[1]])], open_position[0], len(open_strings[open_position[1]])])
                    pos = close_position + len(close_strings[open_position[1]])
                    last_pos = pos
                    break
            else:
                return None
        
        return boundary_strings

    def _find_open_strings(self, operators: list) -> list:
        return [x[:len(x)//2] for x in operators]
    
    def _find_close_strings(self, operators: list) -> list:
        return [x[len(x)//2:] for x in operators]

    def _validate_operators(self, operators: list, boundaries_and_parenthesis: bool = False) -> list:
        if not isinstance(operators, (list, tuple, set)):
            UTILS.TerminalUtility.WarningMessage("Operators or string boundaries must be a #1, #2 or #3\ntype(operators): #4 - Not Supported\noperators = #5", ["list", "tuple", "set", type(operators), operators], exception_raised=True)
            raise TypeError(f"Operators or string boundaries must be a list, tuple or set, type of '{type(operators)}' is not supported.")
        
        # Check if any operator is already in the list
        result = []
        for operator in operators:
            if not isinstance(operator, str):
                UTILS.TerminalUtility.WarningMessage("Element in operator or string boundaries list must be a #1\ntype(operator): #2 - Not Supported\noperator = #3", ["string", type(operator), operator], exception_raised=True)
                raise TypeError(f"Element in operator or string boundaries list must be a string, type of '{type(operator)}' is not supported.")

            if "`" in operator:
                UTILS.TerminalUtility.WarningMessage("String boundaries or operator must not contain the character #1\noperator = #2", ["`", operator], exception_raised=True)
                raise ValueError(f"String boundaries or operator '{operator}' must not contain the character '`'")
            
            if not operator:
                continue
            
            if boundaries_and_parenthesis:
                if len(operator) == 1:
                    operator = operator * 2
                if len(operator) % 2 != 0:
                    raise ValueError(f"String boundaries '{operator}' must contain an even number of characters.")

            if operator in self.__operators:
                UTILS.TerminalUtility.WarningMessage("Operator or string boundaries #1 is already in the list of operators.\nDuplicate operators are not allowed.", [operator], exception_raised=True)
                raise ValueError(f"Operator or string boundaries '{operator}' is already in the list of operators. Duplicate operators are not allowed.")

            self.__operators.append(operator)
            result.append(operator)
        
        return result
    
    def _remove_operators(self, operators: list):
        for operator in operators:
            if operator in self.__operators:
                self.__operators.remove(operator)
            else:
                print (f"Warning: Operator or string boundaries '{operator}' is not in the list of operators. It will not be removed.")

    def cirilica_u_latinicu(self, text: str) -> str:
        return to_latin(text)

    def clear_serbian_chars(self, text: str = None, keep_same_lenght: bool = False) -> str:
        if text is None:
            return None
        
        replace_table = [
            ["ć", "c"],
            ["č", "c"],
            ["š", "s"],
            ["ž", "z"],
            ["Ć", "c"],
            ["Č", "c"],
            ["Š", "S"],
            ["Ž", "Z"]
        ]
        if keep_same_lenght:
            replace_table.append(["đ", "d"])
            replace_table.append(["Đ", "D"])
        else:
            replace_table.append(["đ", "dj"])
            replace_table.append(["Đ", "Dj"])
        
        for i in replace_table:
            text = text.replace(i[0], i[1])
        return text

    def __str__(self) -> str:
        return self.FilterText
    
    def __repr__(self) -> str:
        return self.FilterText
    
    def __eq__(self, other: object) -> bool:
        return self.FilterText == other

    def __len__(self) -> int:
        return len(self.FilterText)
    
    def __contains__(self, item: str) -> bool:
        return item in self.FilterText
    
    def __iadd__(self, add_to_filter_text: str) -> str:
        self.FilterText += add_to_filter_text
        return self

    @property
    def FilterText(self) -> str:
        return self.__filter_text
    
    @FilterText.setter
    def FilterText(self, filter_text: str):
        if not isinstance(filter_text, str):
            UTILS.TerminalUtility.WarningMessage("Filter text must be a #1\ntype(filter_text): #2 - Not Supported\nfilter_text = #3", ["string", type(filter_text), filter_text], exception_raised=True)
            raise TypeError(f"Filter text must be a string, type of '{type(filter_text)}' is not supported.")
        self.__filter_text = filter_text

    @property
    def DocumentText(self) -> str:
        return self.__document_text
    
    @DocumentText.setter
    def DocumentText(self, document_text: str):
        if not isinstance(document_text, str):
            UTILS.TerminalUtility.WarningMessage("Document text must be a #1\ntype(document_text): #2 - Not Supported\ndocument_text = #3", ["string", type(document_text), document_text])
            raise TypeError(f"Document text must be a string, type of '{type(document_text)}' is not supported.")
        self.__document_text = document_text
    
    @property
    def SearchWholeWordsOnly(self) -> bool:
        return self.__search_whole_words_only
    
    @SearchWholeWordsOnly.setter
    def SearchWholeWordsOnly(self, search_whole_words_only: bool):
        if not isinstance(search_whole_words_only, bool):
            UTILS.TerminalUtility.WarningMessage("Search whole words only must be a #1\ntype(search_whole_words_only): #2 - Not Supported\nsearch_whole_words_only = #3", ["boolean", type(search_whole_words_only), search_whole_words_only], exception_raised=True)
            raise TypeError(f"Search whole words only must be a boolean, type of '{type(search_whole_words_only)}' is not supported.")
        self.__search_whole_words_only = search_whole_words_only
    
    @property
    def MatchCase(self) -> bool:
        return self.__match_case
    
    @MatchCase.setter
    def MatchCase(self, match_case: bool):
        if not isinstance(match_case, bool):
            UTILS.TerminalUtility.WarningMessage("Match case must be a #1\ntype(match_case): #2 - Not Supported\nmatch_case = #3", ["boolean", type(match_case), match_case], exception_raised=True)
            raise TypeError(f"Match case must be a boolean, type of '{type(match_case)}' is not supported.")
        self.__match_case = match_case

    @property
    def IgnoreSerbianCharacters(self) -> bool:
        return self.__ignore_serbian_characters
    
    @IgnoreSerbianCharacters.setter
    def IgnoreSerbianCharacters(self, ignore_serbian_characters: bool):
        if not isinstance(ignore_serbian_characters, bool):
            UTILS.TerminalUtility.WarningMessage("Ignore serbian characters must be a #1\ntype(ignore_serbian_characters): #2 - Not Supported\nignore_serbian_characters = #3", ["boolean", type(ignore_serbian_characters), ignore_serbian_characters], exception_raised=True)
            raise TypeError(f"Ignore serbian characters must be a boolean, type of '{type(ignore_serbian_characters)}' is not supported.")
        self.__ignore_serbian_characters = ignore_serbian_characters

    @property
    def TranslateCyrillicToLatin(self) -> bool:
        return self.__translate_cyrillic_to_latin
    
    @TranslateCyrillicToLatin.setter
    def TranslateCyrillicToLatin(self, translate_cyrillic_to_latin: bool):
        if not isinstance(translate_cyrillic_to_latin, bool):
            UTILS.TerminalUtility.WarningMessage("Translate cyrillic to latin must be a #1\ntype(translate_cyrillic_to_latin): #2 - Not Supported\ntranslate_cyrillic_to_latin = #3", ["boolean", type(translate_cyrillic_to_latin), translate_cyrillic_to_latin], exception_raised=True)
            raise TypeError(f"Translate cyrillic to latin must be a boolean, type of '{type(translate_cyrillic_to_latin)}' is not supported.")
        self.__translate_cyrillic_to_latin = translate_cyrillic_to_latin

    @property
    def AndOperators(self) -> list:
        return self.__and_operators
    
    @AndOperators.setter
    def AndOperators(self, list_of_operators: list):
        self.__and_operators = self._validate_operators(list_of_operators)

    @property
    def SpaceAsAndOperator(self) -> bool:
        return self.__space_as_and_operator

    @SpaceAsAndOperator.setter
    def SpaceAsAndOperator(self, space_as_and_operator: bool):
        if not isinstance(space_as_and_operator, bool):
            UTILS.TerminalUtility.WarningMessage("Space as and operator must be a #1\ntype(space_as_and_operator): #2 - Not Supported\space_as_and_operator = #3", ["boolean", type(space_as_and_operator), space_as_and_operator], exception_raised=True)
            raise TypeError(f"Space as and operator must be a boolean, type of '{type(space_as_and_operator)}' is not supported.")
        self.__space_as_and_operator = space_as_and_operator

    @property
    def OrOperators(self) -> list:
        return self.__or_operators

    @OrOperators.setter
    def OrOperators(self, list_of_operators: list):
        self.__or_operators = self._validate_operators(list_of_operators)
    
    @property
    def NotOperators(self) -> list:
        return self.__not_operators
    
    @NotOperators.setter
    def NotOperators(self, list_of_operators: list):
        self.__not_operators = self._validate_operators(list_of_operators)
    
    @property
    def ExactStringBoundaries(self) -> list:
        return self.__exact_string_boundaries
    
    @ExactStringBoundaries.setter
    def ExactStringBoundaries(self, list_of_pair_strings: list):
        self._remove_operators(self.__exact_string_boundaries)
        self.__exact_string_boundaries = self._validate_operators(list_of_pair_strings, boundaries_and_parenthesis=True)
        self.__exact_string_boundaries_open_string = self._find_open_strings(self.__exact_string_boundaries)
        self.__exact_string_boundaries_close_string = self._find_close_strings(self.__exact_string_boundaries)

    @property
    def LogicParenthesis(self) -> list:
        return self.__logic_parenthesis

    @LogicParenthesis.setter
    def LogicParenthesis(self, list_of_pair_strings: list):
        self._remove_operators(self.__logic_parenthesis)
        self.__logic_parenthesis = self._validate_operators(list_of_pair_strings, boundaries_and_parenthesis=True)
        self.__logic_parenthesis_open_string = self._find_open_strings(self.__logic_parenthesis)
        self.__logic_parenthesis_close_string = self._find_close_strings(self.__logic_parenthesis)
        for item in self.__logic_parenthesis_open_string:
            if item in self.__logic_parenthesis_close_string:
                print (f"Warning: '{item}' is both open and close parenthesis string. It will not be removed. Unexpected behaviour may occur.")

        
class FilterMenu:
    STARTING_ID: int = 999990

    def __init__(self, settings: settings_cls.Settings, text_filter_object: TextFilter):

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._text_filter = text_filter_object
        self._active_menu_dict = None

        self.__menu_id_matchcase = self.STARTING_ID + 10
        self.__menu_id_wholewords = self.STARTING_ID + 20
        self.__menu_id_ignore_serbian_characters = self.STARTING_ID + 30
        self.__menu_id_translate_cyrillic_to_latin = self.STARTING_ID + 40

        self.item_range_filter_setup = (self.STARTING_ID, self.STARTING_ID + 50)

        self.__menu_id_item_search_history = self.STARTING_ID + 50
        self.__menu_id_all_search_history = self.STARTING_ID + 60

    def create_menu_dict(self,
                       existing_menu_dict: dict = None,
                       menu_position: QPoint = None,
                       show_match_case: bool = True,
                       show_whole_words: bool = True,
                       show_ignore_serbian_characters: bool = True,
                       show_translate_cyrillic_to_latin: bool = True,
                       show_item_search_history: bool = True,
                       show_all_search_history: bool = True,
                       add_separator_at_end: bool = False) -> dict:

        disab = []
        # Disable menu search history if there is no search history
        if not self._text_filter.has_search_history():
            if show_all_search_history:
                disab.append(self.MenuID_AllSearchHistory)
            if show_item_search_history:
                disab.append(self.MenuID_ItemSearchHistory)

        # Set menu ON/OFF status text
        matchcase_status = self.getl("text_on") if self._text_filter.MatchCase else self.getl("text_off")
        whole_words_status = self.getl("text_on") if self._text_filter.SearchWholeWordsOnly else self.getl("text_off")
        ignore_serbian_characters_status = self.getl("text_on") if self._text_filter.IgnoreSerbianCharacters else self.getl("text_off")
        translate_cyrillic_to_latin_status = self.getl("text_on") if self._text_filter.TranslateCyrillicToLatin else self.getl("text_off")

        separator = []
        # Set menu separator
        menu_switch_items = []
        if show_match_case:
            menu_switch_items.append(self.MenuID_MatchCase)
        if show_whole_words:
            menu_switch_items.append(self.MenuID_WholeWords)
        if show_ignore_serbian_characters:
            menu_switch_items.append(self.MenuID_IgnoreSerbianCharacters)
        if show_translate_cyrillic_to_latin:
            menu_switch_items.append(self.MenuID_TranslateCyrillicToLatin)
        
        if menu_switch_items:
            separator.append(max(menu_switch_items))

        # Add last menu item in separator list i add_separator_at_end is True
        if add_separator_at_end:
            separator.append(self.MenuID_AllSearchHistory)
        
        selected_items = []
        # Set selected menu items
        if self._text_filter.MatchCase:
            selected_items.append(self.MenuID_MatchCase_ON)
        else:
            selected_items.append(self.MenuID_MatchCase_OFF)
        if self._text_filter.SearchWholeWordsOnly:
            selected_items.append(self.MenuID_WholeWords_ON)
        else:
            selected_items.append(self.MenuID_WholeWords_OFF)
        if self._text_filter.IgnoreSerbianCharacters:
            selected_items.append(self.MenuID_IgnoreSerbianCharacters_ON)
        else:
            selected_items.append(self.MenuID_IgnoreSerbianCharacters_OFF)
        if self._text_filter.TranslateCyrillicToLatin:
            selected_items.append(self.MenuID_TranslateCyrillicToLatin_ON)
        else:
            selected_items.append(self.MenuID_TranslateCyrillicToLatin_OFF)
        
        # Set menu
        menu_dict = {
            "position": menu_position if menu_position is not None else QCursor.pos(),
            "disabled": disab,
            "selected": selected_items,
            "separator": separator,
            "items": []
        }
        if show_match_case:
            menu_dict["items"].append(self._menu_item_matchcase(matchcase_status))
        if show_whole_words:
            menu_dict["items"].append(self._menu_item_whole_words(whole_words_status))
        if show_ignore_serbian_characters:
            menu_dict["items"].append(self._menu_item_ignore_serbian_characters(ignore_serbian_characters_status))
        if show_translate_cyrillic_to_latin:
            menu_dict["items"].append(self._menu_item_translate_cyrillic_to_latin(translate_cyrillic_to_latin_status))
        if show_item_search_history:
            menu_dict["items"].append(self._menu_item_show_item_search_history())
        if show_all_search_history:
            menu_dict["items"].append(self._menu_item_show_all_search_history())

        # Check if existing menu dict exists
        if existing_menu_dict:
            for key in existing_menu_dict:
                if key in ["disabled", "selected", "separator", "items"]:
                    menu_dict[key] = existing_menu_dict[key] + menu_dict[key]
                else:
                    menu_dict[key] = existing_menu_dict[key]
        
        return menu_dict

    def show_menu(self, parent_widget: QWidget, menu_dict: dict = None, full_item_ID: str = None, process_text_filter_items: bool = True) -> int:
        if not menu_dict:
            menu_dict = self._active_menu_dict
        if not menu_dict:
            menu_dict = self.create_menu_dict()

        if not full_item_ID:
            full_item_ID = ""
            if menu_dict.get("disabled") is None:
                menu_dict["disabled"] = [self.MenuID_ItemSearchHistory]
            else:
                menu_dict["disabled"].append(self.MenuID_ItemSearchHistory)

        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, parent_widget)
        
        result = self.get_appv("menu")["result"]

        if not process_text_filter_items:
            return result
        
        if result == self.MenuID_MatchCase_ON:
            self._text_filter.MatchCase = True
        elif result == self.MenuID_MatchCase_OFF:
            self._text_filter.MatchCase = False
        elif result == self.MenuID_WholeWords_ON:
            self._text_filter.SearchWholeWordsOnly = True
        elif result == self.MenuID_WholeWords_OFF:
            self._text_filter.SearchWholeWordsOnly = False
        elif result == self.MenuID_IgnoreSerbianCharacters_ON:
            self._text_filter.IgnoreSerbianCharacters = True
        elif result == self.MenuID_IgnoreSerbianCharacters_OFF:
            self._text_filter.IgnoreSerbianCharacters = False
        elif result == self.MenuID_TranslateCyrillicToLatin_ON:
            self._text_filter.TranslateCyrillicToLatin = True
        elif result == self.MenuID_TranslateCyrillicToLatin_OFF:
            self._text_filter.TranslateCyrillicToLatin = False
        elif result == self.MenuID_ItemSearchHistory and full_item_ID:
            self._text_filter.show_search_history(settings=self._stt, qdialog_parent_widget=parent_widget, item_id=full_item_ID)
        elif result == self.MenuID_AllSearchHistory:
            self._text_filter.show_search_history(settings=self._stt, qdialog_parent_widget=parent_widget)

        return result
    
    def _menu_item_matchcase(self, item_status_text: str) -> list:
        return [
            self.MenuID_MatchCase,
            f'{self.getl("find_in_app_menu_set_matchcase_text")} ({item_status_text})',
            self.getl("find_in_app_menu_set_matchcase_tt"),
            False,
            [
                [self.MenuID_MatchCase_ON, self.getl("text_on"), "", True, [], None],
                [self.MenuID_MatchCase_OFF, self.getl("text_off"), "", True, [], None]
            ],
            self.getv("matchcase_icon_path")
        ]

    def _menu_item_whole_words(self, item_status_text: str) -> list:
        return [
            self.MenuID_WholeWords,
            f'{self.getl("find_in_app_menu_set_whole_words_text")} ({item_status_text})',
            self.getl("find_in_app_menu_set_whole_words_tt"),
            False,
            [
                [self.MenuID_WholeWords_ON, self.getl("text_on"), "", True, [], None],
                [self.MenuID_WholeWords_OFF, self.getl("text_off"), "", True, [], None]
            ],
            self.getv("whole_words_icon_path")
        ]
    
    def _menu_item_ignore_serbian_characters(self, item_status_text: str) -> list:
        return [
            self.MenuID_IgnoreSerbianCharacters,
            f'{self.getl("find_in_app_menu_set_ignore_serbian_characters_text")} ({item_status_text})',
            self.getl("find_in_app_menu_set_ignore_serbian_characters_tt"),
            False,
            [
                [self.MenuID_IgnoreSerbianCharacters_ON, self.getl("text_on"), "", True, [], None],
                [self.MenuID_IgnoreSerbianCharacters_OFF, self.getl("text_off"), "", True, [], None]
            ],
            self.getv("serbia_flag_rounded_icon_path")
        ]

    def _menu_item_translate_cyrillic_to_latin(self, item_status_text: str) -> list:
        return [
            self.MenuID_TranslateCyrillicToLatin,
            f'{self.getl("find_in_app_menu_set_translate_cyrillic_to_latin_text")} ({item_status_text})',
            self.getl("find_in_app_menu_set_translate_cyrillic_to_latin_tt"),
            False,
            [
                [self.MenuID_TranslateCyrillicToLatin_ON, self.getl("text_on"), "", True, [], None],
                [self.MenuID_TranslateCyrillicToLatin_OFF, self.getl("text_off"), "", True, [], None]
            ],
            self.getv("alphabet_conversion_icon_path")
        ]
    
    def _menu_item_show_item_search_history(self) -> list:
        return [
            self.MenuID_ItemSearchHistory,
            self.getl("find_in_app_menu_show_item_search_history_text"),
            self.getl("find_in_app_menu_show_item_search_history_tt"),
            True,
            [],
            self.getv("find_icon_path")
        ]

    def _menu_item_show_all_search_history(self) -> list:
        return [
            self.MenuID_AllSearchHistory,
            self.getl("find_in_app_menu_show_all_search_history_text"),
            self.getl("find_in_app_menu_show_all_search_history_tt"),
            True,
            [],
            self.getv("find_icon_path")
        ]

    @property
    def MenuID_MatchCase(self):
        return self.__menu_id_matchcase
    
    @property
    def MenuID_MatchCase_ON(self):
        return self.__menu_id_matchcase + 1
    
    @property
    def MenuID_MatchCase_OFF(self):
        return self.__menu_id_matchcase + 2
    
    @property
    def MenuID_WholeWords(self):
        return self.__menu_id_wholewords
    
    @property
    def MenuID_WholeWords_ON(self):
        return self.__menu_id_wholewords + 1
    
    @property
    def MenuID_WholeWords_OFF(self):
        return self.__menu_id_wholewords + 2
    
    @property
    def MenuID_IgnoreSerbianCharacters(self):
        return self.__menu_id_ignore_serbian_characters
    
    @property
    def MenuID_IgnoreSerbianCharacters_ON(self):
        return self.__menu_id_ignore_serbian_characters + 1
    
    @property
    def MenuID_IgnoreSerbianCharacters_OFF(self):
        return self.__menu_id_ignore_serbian_characters + 2
    
    @property
    def MenuID_TranslateCyrillicToLatin(self):
        return self.__menu_id_translate_cyrillic_to_latin
    
    @property
    def MenuID_TranslateCyrillicToLatin_ON(self):
        return self.__menu_id_translate_cyrillic_to_latin + 1
    
    @property
    def MenuID_TranslateCyrillicToLatin_OFF(self):
        return self.__menu_id_translate_cyrillic_to_latin + 2
    
    @property
    def MenuID_ItemSearchHistory(self):
        return self.__menu_id_item_search_history
    
    @property
    def MenuID_AllSearchHistory(self):
        return self.__menu_id_all_search_history
    

