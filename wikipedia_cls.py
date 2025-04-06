from PyQt5.QtWidgets import (QFrame, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QSizePolicy, QVBoxLayout,
                             QSpacerItem, QDialog, QCheckBox)
from PyQt5.QtGui import QIcon, QPixmap, QMouseEvent, QResizeEvent, QMovie
from PyQt5.QtCore import QSize, Qt, QCoreApplication
from PyQt5 import QtGui

from cyrtranslit import to_latin
import webbrowser
import requests
import urllib.request

import settings_cls
import utility_cls
import html_parser_cls
import wikipedia_card_cls
import qwidgets_util_cls
import UTILS


class SearchCard(QFrame):
    def __init__(self, parent_widget, settings: settings_cls.Settings, search_data: str, card_setting: dict = None):
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.search_data = self.sort_data(search_data)
        self.card_setting = card_setting
        self.parent_widget = parent_widget
        self.html_parser = html_parser_cls.HtmlParser()

        self._create_find_card()

    def refresh_card(self):
        self._create_find_card()
        self.parent_widget.resize(self.width(), self.height() + 20)

    def sort_data(self, data: list) -> list:
        rules = []
        if self.get_appv("user").language_name in ["serbian", "croatian", "bosnian"]:
            rules = ["sh", "sr", "hr", "bs", "en"]
        else:
            rules.append(self.get_appv("user").language_id)
            rules.append("en")

        result = []
        for rule in rules:
            for item in data:
                if item["link"].startswith(f"https://{rule}.wikipedia.org") and item not in result:
                    result.append(item)
        for item in data:
            if item not in result:
                item["title"] = item["title"].strip("🌐 ")
                result.append(item)
        return result

    def fix_url(self, url: str) -> str:
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = "https://wikipedia.org/" + url.strip(" /")
        return url

    def _create_find_card(self):
        w = self.card_setting.get("width", 600)
        y = 0
        x = 0

        # Title
        lbl_title = QLabel(self)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_title.setAlignment(Qt.AlignCenter)
        title_text = self.card_setting.get("title", self.getl("wiki_search_title_text"))
        text_to_html = utility_cls.TextToHTML(text=title_text + "\n(#--1)")
        text_to_html.general_rule.font_size = 22
        text_to_html.general_rule.font_bold = True
        text_to_html.general_rule.fg_color = "#65cc97"
        rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=self.card_setting["search_string"], fg_color="#b5b588", font_size=12, font_bold=False)
        text_to_html.add_rule(rule)
        lbl_title.setText(text_to_html.get_html())
        lbl_title.move(x, y)
        lbl_title.resize(w, 80)
        y += lbl_title.height()

        # Supported sites
        lbl_sup = QLabel(self)
        lbl_sup.setTextInteractionFlags(lbl_sup.textInteractionFlags()|Qt.TextSelectableByMouse)
        sup_text = self.getl("wikipedia_pages_text") + " (#--1)"
        sup_text_to_html = utility_cls.TextToHTML(text=sup_text)
        sup_text_to_html.general_rule.font_size = 18
        sup_text_to_html.general_rule.fg_color = "#00ff00"
        lbl_sup.move(x, y)
        lbl_sup.resize(w, 35)
        y += lbl_sup.height()

        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.move(0, y)
        line1.resize(w, 3)
        y += line1.height() + 5

        # Supported Body
        frm_sup, sup_items_no = self._create_find_card_supported_frame()
        frm_sup.move(x, y)
        y += frm_sup.height() + 20

        if not self.card_setting.get("only_valid_links", False):
            # All search results
            lbl_all = QLabel(self)
            lbl_all.setTextInteractionFlags(lbl_all.textInteractionFlags()|Qt.TextSelectableByMouse)
            all_text = self.getl("wikipedia_all_search_results_text") + " (#--1)"
            all_text_to_html = utility_cls.TextToHTML(text=all_text)
            all_text_to_html.general_rule.font_size = 18
            all_text_to_html.general_rule.fg_color = "#00ff00"
            lbl_all.move(x, y)
            lbl_all.resize(w, 35)
            y += lbl_all.height()
            
            line2 = QFrame(self)
            line2.setFrameShape(QFrame.HLine)
            line2.setFrameShadow(QFrame.Sunken)
            line2.move(0, y)
            line2.resize(w, 3)
            y += line2.height() + 5

            # All Body
            frm_all, all_items_no = self._create_find_card_all_frame()
            frm_all.move(x, y)
            y += frm_all.height()

        # Set item count text
        rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(sup_items_no), fg_color="#ffffff")
        sup_text_to_html.add_rule(rule)
        lbl_sup.setText(sup_text_to_html.get_html())

        if not self.card_setting.get("only_valid_links", False):
            rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(all_items_no), fg_color="#ffffff")
            all_text_to_html.add_rule(rule)
            lbl_all.setText(all_text_to_html.get_html())

        self.resize(w, y)

    def _create_find_card_supported_frame(self, spacing: int = 15):
        w = self.card_setting.get("width", 600)
        frm = QFrame(self)
        self._define_frame(frm)
        frm.resize(w, 0)

        items = []
        for item in self.search_data:
            is_supported = False
            for i in self.card_setting["supported"]:
                if i in item["link"]:
                    is_supported = True
            if is_supported:
                items.append(item)
        
        feedback = self.card_setting["feedback"]
        y = 0
        x = 0
        for item in items:
            # Title
            btn_title = QPushButton(frm)
            font = btn_title.font()
            font.setPointSize(14)
            font.setBold(True)
            btn_title.setFont(font)
            btn_title.setStyleSheet("QPushButton {color: rgb(255, 255, 0); background-color: rgb(0, 0, 115);} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
            btn_title.setText(item["title"])
            link = item["link"]
            btn_title.clicked.connect(lambda _, link_val=link: feedback(link_val))
            btn_title.adjustSize()
            btn_title.move(x, y)
            y += btn_title.height()

            # Description
            lbl_desc = self._create_find_card_item_desc_label(frm, item["description"])
            lbl_desc.move(x, y)
            y += lbl_desc.height()

            # Link
            lbl_link = self._create_find_card_item_link_label(frm, item["link"], external=True)
            lbl_link.move(x, y)
            y += lbl_link.height() + spacing

        frm.resize(w, y)
        return (frm, len(items))

    def _create_find_card_all_frame(self, spacing: int = 15):
        w = self.card_setting.get("width", 600)
        frm = QFrame(self)
        self._define_frame(frm)
        frm.resize(w, 0)

        items = []
        for item in self.search_data:
            is_supported = False
            for i in self.card_setting["supported"]:
                if i in item["link"]:
                    is_supported = True
            if not is_supported:
                items.append(item)
        
        y = 0
        x = 0
        for item in items:
            # Title
            lbl_title = QLabel(frm)
            lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
            font = lbl_title.font()
            font.setPointSize(12)
            font.setBold(True)
            lbl_title.setFont(font)
            lbl_title.setStyleSheet("QLabel {color: #ffff00;} QLabel:hover {color: #aaffff;}")
            lbl_title.setText(item["title"])
            link = item["link"]
            lbl_title.mousePressEvent = lambda _, link_val=link: self.external_link(link_val)
            lbl_title.adjustSize()
            lbl_title.move(x, y)
            y += lbl_title.height()

            # Description
            lbl_desc = self._create_find_card_item_desc_label(frm, item["description"])
            lbl_desc.move(x, y)
            y += lbl_desc.height()

            # Link
            lbl_link = self._create_find_card_item_link_label(frm, item["link"], external=True)
            lbl_link.move(x, y)
            y += lbl_link.height() + spacing

        frm.resize(w, y)
        return (frm, len(items))

    def _create_find_card_item_desc_label(self, parent_widget: QFrame, text: str) -> QLabel:
        lbl = QLabel(parent_widget)
        lbl.setTextInteractionFlags(lbl.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl.setWordWrap(True)
        font = lbl.font()
        font.setPointSize(10)
        lbl.setFont(font)
        lbl.setStyleSheet("color: #c7c7c7;")
        lbl.setText(text)
        lbl.setFixedWidth(parent_widget.width())
        lbl.adjustSize()
        return lbl

    def _create_find_card_item_link_label(self, parent_widget: QFrame, text: str, external: bool = True) -> QLabel:
        lbl = QLabel(parent_widget)
        lbl.setTextInteractionFlags(lbl.textInteractionFlags()|Qt.TextSelectableByMouse)
        font = lbl.font()
        font.setPointSize(10)
        lbl.setFont(font)
        lbl.setStyleSheet("QLabel {color: #aaff7f;} QLabel:hover {color: #aaffff;}")
        lbl.setText(text)
        lbl.resize(parent_widget.width(), 10)
        lbl.adjustSize()
        feedback = self.card_setting["feedback"]
        if external:
            lbl.mousePressEvent = lambda _, link_val=text: self.external_link(link_val)
        else:
            lbl.mousePressEvent = lambda _, link_val=text: feedback(link_val)
        return lbl

    def _define_frame(self, frame: QFrame = None):
        if frame is None:
            frame = self

        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(0)

    def external_link(self, url: str):
        webbrowser.open_new_tab(url)


class Wikipedia(QDialog):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, search_string: str = None, wiki_settings: dict = None, auto_show_dialog: bool = True):
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.wiki_card = None
        self.auto_show_dialog = auto_show_dialog
        self.html_parser = html_parser_cls.HtmlParser()
        self.ignore_checkbox_status_change = False

        if wiki_settings is None:
            wiki_settings = {}
        self.wiki_settings = wiki_settings

        self._define_widgets()
        self._load_win_position()
        self._check_engine_selection_status()

        self.load_widgets_handler()

        # Connect events with slots
        self.chk_any.stateChanged.connect(self.chk_any_state_changed)
        self.chk_duckduckgo.stateChanged.connect(self.chk_duckduckgo_state_changed)
        self.chk_yahoo.stateChanged.connect(self.chk_yahoo_state_changed)
        self.chk_brave.stateChanged.connect(self.chk_brave_state_changed)
        self.btn_search.clicked.connect(self.btn_search_click)
        self.txt_search.returnPressed.connect(self.btn_search_click)
        self.btn_refresh.clicked.connect(self.btn_refresh_click)
        self.lbl_search_pic.mousePressEvent = self.lbl_search_pic_mouse_press
        self.lbl_content_pic.mousePressEvent = self.lbl_content_pic_mouse_press
        self.lbl_wiki_logo.mousePressEvent = self.lbl_wiki_logo_mouse_press

        if self.auto_show_dialog:
            self.show()
            UTILS.LogHandler.add_log_record("#1: Dialog started. (Display dialog = #2)", ["Wikipedia", "True"])
            QCoreApplication.processEvents()
        else:
            UTILS.LogHandler.add_log_record("#1: Dialog started. (Display dialog = #2)", ["Wikipedia", "False"])
        if search_string:
            self.txt_search.setText(search_string)
            self.btn_search_click()

    def load_widgets_handler(self):
        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.frm_search, self.lbl_search_title])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons()

        # Add Labels as PushButtons
        self.widget_handler.add_QPushButton(self.lbl_content_pic, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_search_pic, {"allow_bypass_mouse_press_event": False})

        # Add Action Frames

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_search, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # ADD Item Based Widgets

        self.widget_handler.activate()

    def lbl_wiki_logo_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.wiki_logo_movie.stop()
        elif self.lbl_wiki_logo.isVisible():
            self.wiki_logo_movie.start()

    def btn_refresh_click(self):
        self.loading(True)
        QCoreApplication.processEvents()
        if self.search_area_widget_layout.count():
            if self.search_area_widget_layout.itemAt(0).widget():
                self.search_area_widget_layout.itemAt(0).widget().card_setting["width"] = self.search_area.contentsRect().width() - 20
                self.search_area_widget_layout.itemAt(0).widget().refresh_card()
        if self.content_area_widget_layout.count():
            if self.content_area_widget_layout.itemAt(0).widget():
                self.content_area_widget_layout.itemAt(0).widget().wiki_frame_settings.wiki_width = self.content_area.contentsRect().width() - 20
                self.content_area_widget_layout.itemAt(0).widget().refresh_card()
        self.loading(False)

    def lbl_search_pic_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_search_pic).EVENT_mouse_press_event(e)
            self.content_area.setVisible(False)
            self.search_area.setVisible(True)
            self._check_engine_selection_status()

    def lbl_content_pic_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_content_pic).EVENT_mouse_press_event(e)
            self.content_area.setVisible(True)
            self.search_area.setVisible(False)
            self._check_engine_selection_status()

    def btn_search_click(self):
        self.wiki_logo_movie.stop()
        self.lbl_wiki_logo.setVisible(False)
        self.show_search_results(self.txt_search.text())
        UTILS.LogHandler.add_log_record("#1: Search performed. (#2)", ["Wikipedia", self.txt_search.text()])

    def chk_duckduckgo_state_changed(self):
        self._check_engine_selection_status()
    
    def chk_yahoo_state_changed(self):
        self._check_engine_selection_status()

    def chk_brave_state_changed(self):
        self._check_engine_selection_status()

    def chk_any_state_changed(self):
        if not self.ignore_checkbox_status_change:
            if self.chk_any.isChecked():
                self.chk_duckduckgo.setChecked(True)
                self.chk_yahoo.setChecked(True)
                self.chk_brave.setChecked(True)
            else:
                self.chk_duckduckgo.setChecked(False)
                self.chk_yahoo.setChecked(False)
                self.chk_brave.setChecked(False)
        
            self._check_engine_selection_status()
    
    def _check_engine_selection_status(self):
        all_engines_status = None
        if self.chk_duckduckgo.isChecked() == self.chk_yahoo.isChecked() == self.chk_brave.isChecked():
            all_engines_status = self.chk_duckduckgo.isChecked()

        if all_engines_status is not None:
            self.lbl_warning.setVisible(not all_engines_status)
            self.ignore_checkbox_status_change = True
            self.chk_any.setChecked(all_engines_status)
            self.ignore_checkbox_status_change = False
        else:
            self.lbl_warning.setVisible(False)
            self.ignore_checkbox_status_change = True
            self.chk_any.setChecked(False)
            self.ignore_checkbox_status_change = False
        
        if self.search_area.isVisible():
            self.lbl_search_pic.setStyleSheet("QLabel {border-bottom: 3px solid; border-bottom-color: #00ffff;} QLabel:hover {background-color: #00007f;}")
        else:
            self.lbl_search_pic.setStyleSheet("QLabel {border-bottom: 0px solid; border-bottom-color: #00ffff;} QLabel:hover {background-color: #00007f;}")

        if self.content_area.isVisible():
            self.lbl_content_pic.setStyleSheet("QLabel {border-bottom: 3px solid; border-bottom-color: #00ffff;} QLabel:hover {background-color: #00007f;}")
        else:
            self.lbl_content_pic.setStyleSheet("QLabel {border-bottom: 0px solid; border-bottom-color: #00ffff;} QLabel:hover {background-color: #00007f;}")

    def loading(self, value: bool):
        if value:
            self.lbl_loading.setVisible(True)
            self.search_area.setEnabled(False)
            self.content_area.setEnabled(False)
        else:
            self.lbl_loading.setVisible(False)
            self.search_area.setEnabled(True)
            self.content_area.setEnabled(True)

    def search_result_clicked(self, url: str):
        self.loading(True)

        # Set new widget in QScrollArea
        self.content_area_widget = QWidget()
        self.content_area_widget_layout = QVBoxLayout()
        # self.search_area_widget_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.content_area_widget.setLayout(self.content_area_widget_layout)
        self.content_area.setWidget(self.content_area_widget)
        # Set all margins to 0 for are, widget and layout
        self.content_area.setContentsMargins(0,0,0,0)
        self.content_area_widget.setContentsMargins(0,0,0,0)
        self.search_area.setVisible(False)
        self.content_area.setVisible(True)
        self._check_engine_selection_status()
        QCoreApplication.processEvents()

        # Get WikiCard
        card_settings = self.wiki_settings
        card_settings["width"] = self.wiki_settings.get("width", self.content_area.contentsRect().width() - 20)
        card_settings["size_changed_feedback"] = self.wiki_card_size_changed

        self.wiki_card = wikipedia_card_cls.WikipediaCard(self.content_area, self._stt, url=url, card_setting=card_settings)
        self.content_area_widget_layout.insertWidget(0, self.wiki_card)
        self.content_area_widget.resize(self.wiki_card.width(), self.wiki_card.height() + 20)
        self.wiki_card.show()
        self.loading(False)

    def wiki_card_size_changed(self, size: QSize):
        if self.wiki_card:
            self.content_area_widget.resize(self.content_area.width(), size.height() + 20)

    def show_search_results(self, query_string: str):
        # Select search engine
        engine = []
        if self.chk_duckduckgo.isChecked():
            engine.append("duckduckgo")
        if self.chk_yahoo.isChecked():
            engine.append("yahoo")
        if self.chk_brave.isChecked():
            engine.append("brave")
        if not engine:
            return

        self.loading(True)
        QCoreApplication.processEvents()

        # Get search data
        query_string = "wikipedia " + query_string
        data = self.get_search_results(query_string=query_string, engines=engine)

        # Set new widget in QScrollArea
        self.search_area_widget = QWidget()
        self.search_area_widget_layout = QVBoxLayout()
        # self.search_area_widget_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.search_area_widget.setLayout(self.search_area_widget_layout)
        self.search_area.setWidget(self.search_area_widget)
        # Set all margins to 0 for are, widget and layout
        self.search_area.setContentsMargins(0,0,0,0)
        self.search_area_widget.setContentsMargins(0,0,0,0)
        self.content_area.setVisible(False)
        self.search_area.setVisible(True)
        self._check_engine_selection_status()

        # Get SearchCard frame
        search_card_settings = {
            "width": self.search_area.contentsRect().width() - 20,
            "search_string": query_string,
            "feedback": self.search_result_clicked,
            "supported": ["wikipedia.org"]
        }
        search_card = SearchCard(self.search_area_widget, self._stt, data, search_card_settings)
        self.search_area_widget.resize(search_card.width(), search_card.height() + 20)

        # Insert SearchCard in area widget layout
        self.search_area_widget_layout.insertWidget(0, search_card)
        search_card.show()
        self.loading(False)

    def get_search_results(self, query_string: str, engines: list = None) -> list:
        if "duckduckgo" in engines or "duck" in engines:
            result = self._get_search_results_duckduckgo(query_string=query_string)
            if result:
                return result
        if "yahoo" in engines:
            result = self._get_search_results_yahoo(query_string=query_string)
            if result:
                return result
        if "brave" in engines:
            result = self._get_search_results_brave(query_string=query_string)
            if result:
                return result
        
        return result

    def _get_search_results_yahoo(self, query_string: str) -> list:
        result = []

        source_http = "https://search.yahoo.com/search?p=" + self._clean_search_string(query_string)
        try:
            result_page = urllib.request.urlopen(source_http, timeout=3)
            html = result_page.read().decode("utf-8")
        except:
            try:
                result_page = requests.get(source_http, timeout=3)
                html = result_page.content
            except:
                return result
        
        if not result_page:
            return result
        if not html:
            return result

        html = html.replace("<b>", "")
        html = html.replace("</b>", "")
        html = self.html_parser._quick_format_html(html)

        search_code = self.html_parser.get_tags(html_code=html, tag="ol", tag_class_contains="reg searchCenterMiddle")
        if search_code:
            data = self.html_parser.get_tags(html_code=search_code[0], tag="li")
        else:
            return result
        
        link = ""
        desc = ""
        title = ""
        link_list = []
        for row in data:
            # Title
            title_code = self.html_parser.get_tags(html_code=row, tag="div", tag_class_contains="compTitle")
            link = ""
            title = ""
            if title_code:
                links = self.html_parser.get_all_links(load_html_code=title_code[0])
                if links:
                    link = links[0].a_href
                    if not link.startswith("http"):
                        link = "https://" + link.lstrip("/")

                title_txt_slices = self.html_parser.get_all_text_slices(load_html_code=title_code[0])
                title = ""
                for txt_slice in title_txt_slices:
                    txt_slice: html_parser_cls.TextObject
                    if "span" not in txt_slice.get_tag():
                        title = txt_slice.txt_value
                if not title:
                    title = self.html_parser.get_raw_text(load_html_code=title_code[0])
            if not link:
                continue

            # Description
            desc_code = self.html_parser.get_tags(html_code=row, tag="div", tag_class_contains="compText")
            if desc_code:
                desc = self.html_parser.get_raw_text(load_html_code=desc_code[0])
    
            # Add result
            if link and link not in link_list:
                link_list.append(link)
                item = {}
                item["title"] = "🌐 " + title
                item["link"] = link
                item["description"] = desc
                item["important"] = None
                result.append(item)
                title = ""
                desc = ""
        
        return result

    def _get_search_results_duckduckgo(self, query_string: str) -> list:
        result = []

        source_http = "https://lite.duckduckgo.com/lite/search?q=" + self._clean_search_string(query_string)

        try:
            result_page = urllib.request.urlopen(source_http, timeout=3)
            html = result_page.read().decode("utf-8")
        except:
            try:
                result_page = requests.get(source_http, timeout=3)
                html = result_page.content
            except:
                return result
        
        if not result_page:
            return result
        if not html:
            return result

        html = html.replace("<b>", "")
        html = html.replace("</b>", "")
        html = self.html_parser._quick_format_html(html)

        data = self.html_parser.get_tags(html_code=html, tag="tr")
        link = ""
        desc = ""
        title = ""
        link_list = []
        for idx, row in enumerate(data):
            if 'class="next_form"' in row:
                break
            links = self.html_parser.get_all_links(load_html_code=row)
            if not links:
                continue

            link = links[0].a_href.strip()
            link = link[link.find("http"):]
            if (link.find("&amp;rut") != -1):
                link = link[:link.find("&amp;rut")]

            link = urllib.parse.unquote(link)
            title = links[0].a_text.strip()

            if idx + 1 >= len(data):
                continue

            desc = ""
            desc = self.html_parser.get_raw_text(load_html_code=data[idx + 1]).strip()
            
            if link and link not in link_list:
                link_list.append(link)
                item = {}
                item["title"] = "🌐 " + title
                item["link"] = link
                item["description"] = desc
                item["important"] = None
                result.append(item)
                title = ""
                desc = ""
        
        return result

    def _get_search_results_brave(self, query_string: str) -> list:
        result = []

        source_http = "https://search.brave.com/search?q=" + self._clean_search_string(query_string) + "&source=web"

        try:
            result_page = urllib.request.urlopen(source_http, timeout=3)
            html = result_page.read().decode("utf-8")
        except:
            try:
                result_page = requests.get(source_http, timeout=3)
                html = result_page.content.decode("utf-8")
            except:
                return result
        
        if not result_page:
            return result
        if not html:
            return result

        html = html.replace("<b>", "")
        html = html.replace("</b>", "")
        html = self.html_parser._quick_format_html(html)

        data = self.html_parser.get_tags(html_code=html, tag="div", custom_tag_property=[["class", "snippet"], ["data-type", "web"]])
        link = ""
        desc = ""
        title = ""
        link_list = []
        for row in data:
            title = ""
            title_code = self.html_parser.get_tags(html_code=row, tag="div", tag_class_contains="title")
            if title_code:
                title = self.html_parser.get_raw_text(load_html_code=title_code[0])

            link = ""
            link_code = self.html_parser.get_all_links(load_html_code=row)
            if link_code:
                link = link_code[0].a_href
            
            desc = ""
            desc_code = self.html_parser.get_tags(html_code=row, tag="div", tag_class_contains="description")
            if desc_code:
                desc = self.html_parser.get_raw_text(load_html_code=desc_code[0])
            
            if not link.startswith("http"):
                link = "https://" + link.lstrip("/")

            if link and link not in link_list:
                link_list.append(link)
                item = {}
                item["title"] = "🌐 " + title
                item["link"] = link
                item["description"] = desc
                item["important"] = None
                result.append(item)
        
        return result

    def _clean_search_string(self, search_string: str, remove_serbian_chars: bool = True) -> str:
        if remove_serbian_chars:
            search_string = self.clear_serbian_chars(search_string)

        search_string = search_string.replace(">", ">\n")
        search_string = search_string.replace("<", "\n<")
        search_string_list = [x.strip() for x in search_string.split("\n") if not x.startswith("<")]
        search_string = " ".join(search_string_list)

        search_string = search_string.strip()

        allowed_chars = "abcdefghijklmnopqrstuvwxyzčćžšđČĆŽŠĐ ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        cleaned_string = ""
        for char in search_string:
            if char in allowed_chars:
                cleaned_string += char
        search_string = cleaned_string

        while True:
            search_string = search_string.replace("  ", " ")
            if search_string.find("  ") == -1:
                break
        search_string = search_string.replace(" ", "+")
        return search_string.strip(" +")

    def clear_serbian_chars(self, text: str = None) -> str:
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

    def fix_url(self, url: str) -> str:
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = "https://wikipedia.org/" + url.strip(" /")
        return url
    
    def cirilica_u_latinicu(self, text: str) -> str:
        latinica_text = to_latin(text)
        return latinica_text

    def _load_win_position(self):
        if "wiki_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("wiki_win_geometry")
            if g.get("pos_x") is not None and g.get("pos_y") is not None:
                self.move(g["pos_x"], g["pos_y"])
            if g.get("width") is not None and g.get("height") is not None:
                self.resize(g["width"], g["height"])
            self.chk_duckduckgo.setChecked(g.get("engine_duckduckgo", True))
            self.chk_yahoo.setChecked(g.get("engine_yahoo", True))
            self.chk_brave.setChecked(g.get("engine_brave", True))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "wiki_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("wiki_win_geometry", {}, save_to_file=True)

        g = self.get_appv("wiki_win_geometry")
        if not self.isMinimized() and not self.isMaximized():
            g["pos_x"] = self.pos().x()
            g["pos_y"] = self.pos().y()
            g["width"] = self.width()
            g["height"] = self.height()
        g["engine_duckduckgo"] = self.chk_duckduckgo.isChecked()
        g["engine_yahoo"] = self.chk_yahoo.isChecked()
        g["engine_brave"] = self.chk_brave.isChecked()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["Wikipedia"])
        UTILS.DialogUtility.on_closeEvent(self)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        # Search bar
        self.frm_search.move(0, 0)
        self.frm_search.resize(w, self.frm_search.height())
        self.lbl_loading.resize(self.frm_search.width() - 4, self.frm_search.height() - 4)
        self.btn_search.move(self.frm_search.contentsRect().width() - self.btn_search.width() - 20, self.btn_search.pos().y())
        self.btn_refresh.move(self.frm_search.contentsRect().width() - self.btn_refresh.width() - 20, self.btn_refresh.pos().y())
        self.txt_search.resize((self.btn_search.pos().x() - 10) - (self.lbl_search_title.pos().x() + self.lbl_search_title.width() + 10), self.txt_search.height())
        self.lbl_warning.resize(self.txt_search.width(), self.txt_search.height())

        # Wiki logo 
        wiki_scale = 1
        wiki_shrink = 1
        wiki_logo_size_y = int((self.contentsRect().height() - (self.frm_search.pos().y() + self.frm_search.height())) / wiki_shrink)
        if wiki_logo_size_y * wiki_scale > self.contentsRect().width() / wiki_shrink:
            wiki_logo_size_x = int((self.contentsRect().width() / wiki_shrink))
            wiki_logo_size_y = int(wiki_logo_size_x / wiki_scale)
        else:
            wiki_logo_size_x = int(wiki_logo_size_y * wiki_scale)

        wiki_logo_x = int((self.contentsRect().width() - wiki_logo_size_x) / 2)
        wiki_logo_y = int((self.contentsRect().height() - (self.frm_search.pos().y() + self.frm_search.height()) - wiki_logo_size_y) / 2 + (self.frm_search.pos().y() + self.frm_search.height()))

        if wiki_logo_size_x < 20 or wiki_logo_size_y < 20:
            self.lbl_wiki_logo.setVisible(False)
        else:
            self.lbl_wiki_logo.setVisible(True)
            self.lbl_wiki_logo.move(wiki_logo_x, wiki_logo_y)
            self.lbl_wiki_logo.resize(wiki_logo_size_x, wiki_logo_size_y)

        # Search Area
        self.search_area.move(0, self.frm_search.pos().y() + self.frm_search.height())
        self.search_area.resize(w, h - self.search_area.pos().y())

        # Content Area
        self.content_area.move(0, self.frm_search.pos().y() + self.frm_search.height())
        self.content_area.resize(w, h - self.content_area.pos().y())

        if self.wiki_card:
            self.wiki_card.wiki_frame_settings.wiki_width = self.content_area.width() - 20

        return super().resizeEvent(a0)

    def _define_widgets(self):
        search_text_y = 5
        search_text_h = 25
        engines_y = 35
        engines_h = 30

        self.setStyleSheet(self.getv("wiki_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("wiki_win_icon_path")))
        self.setWindowTitle(self.getl("wiki_win_title_text"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(800, 600)

        # Search bar
        self.frm_search = QFrame(self)
        self.frm_search.resize(10, 70)
        self.frm_search.setFrameShape(QFrame.Box)
        self.frm_search.setFrameShadow(QFrame.Plain)
        self.frm_search.setLineWidth(2)
        self.frm_search.setStyleSheet(self.getv("wiki_frm_search_stylesheet"))
        font = self.frm_search.font()
        font.setPointSize(10)

        self.lbl_search_pic = QLabel(self.frm_search)
        self.lbl_search_pic.move(10, 10)
        self.lbl_search_pic.resize(50, 50)
        self.lbl_search_pic.setScaledContents(True)
        self.lbl_search_pic.setAlignment(Qt.AlignCenter)
        self.lbl_search_pic.setPixmap(QPixmap(self.getv("wiki_lbl_search_icon_path")))
        self.lbl_search_pic.setStyleSheet("QLabel:hover {background-color: #0000ff}")
        self.lbl_search_pic.setToolTip(self.getl("wiki_lbl_search_pic_tt"))

        self.lbl_content_pic = QLabel(self.frm_search)
        self.lbl_content_pic.move(70, 10)
        self.lbl_content_pic.resize(50, 50)
        self.lbl_content_pic.setScaledContents(True)
        self.lbl_content_pic.setAlignment(Qt.AlignCenter)
        self.lbl_content_pic.setPixmap(QPixmap(self.getv("wiki_lbl_content_icon_path")))
        self.lbl_content_pic.setStyleSheet("QLabel:hover {background-color: #0000ff}")
        self.lbl_content_pic.setToolTip(self.getl("wiki_lbl_content_pic_tt"))

        self.lbl_search_title = QLabel(self.frm_search)
        self.lbl_search_title.move(self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() + 20, search_text_y)
        self.lbl_search_title.setFont(font)
        self.lbl_search_title.setText(self.getl("wiki_lbl_search_title_text"))
        self.lbl_search_title.adjustSize()
        self.lbl_search_title.resize(self.lbl_search_title.width(), search_text_h)
        
        self.txt_search = QLineEdit(self.frm_search)
        self.txt_search.move(self.lbl_search_title.pos().x() + self.lbl_search_title.width() + 10, search_text_y)
        self.txt_search.resize(10, search_text_h)
        font.setPointSize(12)
        self.txt_search.setFont(font)
        self.txt_search.setStyleSheet(self.getv("wiki_txt_search_stylesheet"))

        self.btn_search = QPushButton(self.frm_search)
        self.btn_search.move(10, search_text_y)
        self.btn_search.resize(100, search_text_h)
        self.btn_search.setText(self.getl("wiki_btn_search_text"))
        font.setPointSize(10)
        self.btn_search.setFont(font)
        self.btn_search.setStyleSheet(self.getv("wiki_btn_search_stylesheet"))
        self.btn_search.setDefault(False)

        self.btn_refresh = QPushButton(self.frm_search)
        self.btn_refresh.move(10, search_text_y + search_text_h + 5)
        self.btn_refresh.resize(100, search_text_h)
        self.btn_refresh.setText(self.getl("wiki_btn_refresh_text"))
        font.setPointSize(10)
        self.btn_refresh.setFont(font)
        self.btn_refresh.setStyleSheet(self.getv("wiki_btn_refresh_stylesheet"))
        self.btn_refresh.setDefault(False)

        # Engines
        self.chk_any = QCheckBox(self.frm_search)
        self.chk_any.setStyleSheet("QCheckBox:hover {background-color: #0000ff;}")
        self.chk_any.move(self.txt_search.pos().x(), engines_y)
        engine_icon = QPixmap(self.getv("engine_any"))
        engine_w = int((engine_icon.width() / engine_icon.height()) * engines_h)
        self.chk_any.setIcon(QIcon(engine_icon))
        self.chk_any.setIconSize(QSize(engine_w, engines_h))
        self.chk_any.setFixedHeight(engines_h)
        self.chk_any.adjustSize()
        self.chk_any.setToolTip(self.getl("wiki_chk_any_tt"))

        self.chk_duckduckgo = QCheckBox(self.frm_search)
        self.chk_duckduckgo.setStyleSheet("QCheckBox:hover {background-color: #0000ff;}")
        self.chk_duckduckgo.move(self.chk_any.pos().x() + self.chk_any.width() + 40, engines_y)
        engine_icon = QPixmap(self.getv("engine_duckduckgo"))
        engine_w = int((engine_icon.width() / engine_icon.height()) * engines_h)
        self.chk_duckduckgo.setIcon(QIcon(engine_icon))
        self.chk_duckduckgo.setIconSize(QSize(engine_w, engines_h))
        self.chk_duckduckgo.setFixedHeight(engines_h)
        self.chk_duckduckgo.adjustSize()
        self.chk_duckduckgo.setToolTip(self.getl("wiki_chk_duckduckgo_tt"))

        self.chk_yahoo = QCheckBox(self.frm_search)
        self.chk_yahoo.setStyleSheet("QCheckBox:hover {background-color: #0000ff;}")
        self.chk_yahoo.move(self.chk_duckduckgo.pos().x() + self.chk_duckduckgo.width() + 20, engines_y)
        engine_icon = QPixmap(self.getv("engine_yahoo"))
        engine_w = int((engine_icon.width() / engine_icon.height()) * engines_h)
        self.chk_yahoo.setIcon(QIcon(engine_icon))
        self.chk_yahoo.setIconSize(QSize(engine_w, engines_h))
        self.chk_yahoo.setFixedHeight(engines_h)
        self.chk_yahoo.adjustSize()
        self.chk_yahoo.setToolTip(self.getl("wiki_chk_yahoo_tt"))

        self.chk_brave = QCheckBox(self.frm_search)
        self.chk_brave.setStyleSheet("QCheckBox:hover {background-color: #0000ff;}")
        self.chk_brave.move(self.chk_yahoo.pos().x() + self.chk_yahoo.width() + 20, engines_y)
        engine_icon = QPixmap(self.getv("engine_brave"))
        engine_w = int((engine_icon.width() / engine_icon.height()) * engines_h)
        self.chk_brave.setIcon(QIcon(engine_icon))
        self.chk_brave.setIconSize(QSize(engine_w, engines_h))
        self.chk_brave.setFixedHeight(engines_h)
        self.chk_brave.adjustSize()
        self.chk_brave.setToolTip(self.getl("wiki_chk_brave_tt"))

        # Wikipedia logo label
        self.lbl_wiki_logo = QLabel(self)
        self.lbl_wiki_logo.setScaledContents(True)
        self.lbl_wiki_logo.setAlignment(Qt.AlignCenter)
        self.wiki_logo_movie = QMovie(self.getv("wikipedia_central_label_animation_path"))
        self.lbl_wiki_logo.setMovie(self.wiki_logo_movie)
        self.wiki_logo_movie.start()
        
        # Loading label
        self.lbl_loading = QLabel(self.frm_search)
        self.lbl_loading.move(2, 2)
        self.lbl_loading.setAlignment(Qt.AlignCenter)
        font.setPointSize(32)
        font.setBold(True)
        self.lbl_loading.setFont(font)
        font.setBold(False)
        self.lbl_loading.setStyleSheet("color: red;")
        self.lbl_loading.setText(self.getl("loading_text"))
        self.lbl_loading.setVisible(False)

        # Warning label
        self.lbl_warning = QLabel(self.frm_search)
        self.lbl_warning.setAlignment(Qt.AlignCenter)
        font.setPointSize(10)
        self.lbl_warning.setFont(font)
        self.lbl_warning.setStyleSheet("color: yellow; background-color: red;")
        self.lbl_warning.setText(self.getl("wiki_lbl_warning_text"))
        self.lbl_warning.move(self.txt_search.pos().x(), self.txt_search.pos().y())
        self.lbl_warning.setVisible(False)

        # Search Area
        self.search_area = QScrollArea(self)
        self.search_area_widget = QWidget(self.search_area)
        self.search_area_widget_layout = QVBoxLayout(self.search_area_widget)
        self.search_area_widget_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.search_area_widget.setLayout(self.search_area_widget_layout)
        self.search_area.setWidget(self.search_area_widget)
        self.search_area.setVisible(False)
        self.search_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        # Content Area
        self.content_area = QScrollArea(self)
        self.content_area_widget = QWidget(self.content_area)
        self.content_area_widget_layout = QVBoxLayout(self.content_area_widget)
        self.content_area_widget_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.content_area_widget.setLayout(self.content_area_widget_layout)
        self.content_area.setWidget(self.content_area_widget)
        self.content_area.setVisible(False)
        self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)






