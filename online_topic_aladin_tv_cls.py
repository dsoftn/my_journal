from PyQt5.QtWidgets import QFrame, QPushButton, QWidget, QLabel, QLineEdit, QComboBox, QProgressBar
from PyQt5.QtGui import QPixmap, QMouseEvent, QResizeEvent
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QUrl, QPoint
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView

import webbrowser
import os

import settings_cls
import utility_cls
import html_parser_cls
from online_abstract_topic import AbstractTopic
from wikipedia_card_cls import WikipediaCard
import UTILS


class ChannelMenuItem(QFrame):
    NAME_BG = "background-color: rgba(0, 0, 79, 0);"

    def __init__(self, parent_widget, settings: settings_cls.Settings, url: str, title: str):
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.url = url
        self.title = title
        self.parent_widget: AbstractTopic = parent_widget.parent()
        self.active = False

        self._create_item()
    
    def set_active(self, value: bool):
        style = "QPushButton {color: rgb(170, 255, 255); " + self.NAME_BG + "} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}"
        if value:
            if self.getv("online_topic_aladain_tv_channel_item_display") == 2:
                self.setFrameShape(QFrame.Box)
            style = "QPushButton {color: #ffff00; " + self.NAME_BG + "} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}"
            self.btn.setStyleSheet("QPushButton {color: #ffff00; background-color: #005500;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        else:
            if self.getv("online_topic_aladain_tv_channel_item_display") == 3:
                self.btn.setStyleSheet(style)
            else:
                self.setFrameShape(QFrame.NoFrame)
                self.btn.setStyleSheet(style)

    def is_active(self) -> bool:
        return self.active
    
    def recreate_item(self):
        self._set_widgets_apperance()
    
    def _create_item(self):
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.NoFrame)
        self.setObjectName(self.url)
        self.setStyleSheet("QFrame {background-color: rgba(255, 255, 255, 0);}")

        # Label
        self.lbl_pic = QLabel(self)
        self.lbl_pic.setAlignment(Qt.AlignCenter)
        self.lbl_pic.setStyleSheet("QLabel {background-color: rgba(255, 255, 255, 0);}")
        self.lbl_pic.move(0, 0)

        # Button
        self.btn = QPushButton(self)
        self.btn.setObjectName(self.url)
        font = self.btn.font()
        font.setPointSize(14)
        self.btn.setFont(font)
        self.btn.setText(self.title)
        self.btn.adjustSize()

        self._set_widgets_apperance()

    def _set_widgets_apperance(self):
        file_path_uncomplete = self.getv("online_topics_aladin_tv_channel_logo") + self.parent_widget._clean_search_string(self.title).replace("+", "_")
        item_type = self.getv("online_topic_aladain_tv_channel_item_display")

        if item_type == 2:
            self.lbl_pic.resize(30, 30)
        else:
            self.lbl_pic.resize(self.btn.height(), self.btn.height())
        
        # Set Image
        has_image = False
        image_extensions = [".png", ".svg", ".webp", ".jpg", ".jpeg", ".gif"]
        if item_type == 3:
            self.parent_widget.set_image_to_label(self.getv("item_icon_path"), self.lbl_pic, use_cashe=False)
            for i in image_extensions:
                file_path = file_path_uncomplete + i
                if os.path.isfile(file_path):
                    has_image = True
                    break
        else:
            for i in image_extensions:
                file_path = file_path_uncomplete + i
                if os.path.isfile(file_path):
                    result = self.parent_widget.set_image_to_label(file_path, self.lbl_pic, use_cashe=False, resize_label_fixed_h=True)
                    if result:
                        has_image = True
                        break
            else:
                self.parent_widget.set_image_to_label(self.getv("item_icon_path"), self.lbl_pic, use_cashe=False)

        # Set stylesheet
        tt = ""
        tt_file_name = file_path_uncomplete + ".txt"
        if os.path.isfile(tt_file_name):
            with open(tt_file_name, "r", encoding="utf-8") as file:
                tt = file.read()
            text_to_html = utility_cls.TextToHTML(text=tt)
            text_to_html.general_rule.fg_color = "yellow"
            text_to_html.general_rule.font_size = "12px"
            tt = text_to_html.get_html()

        if has_image:
            tt = f'<img src="{file_path}" width=300 /><br>' + tt

        self.lbl_pic.setToolTip(tt)
        self.btn.setToolTip(tt)

        style = "QPushButton {color: rgb(170, 255, 255); " + self.NAME_BG + "} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}"
        if item_type == 1:
            self.lbl_pic.setVisible(True)
            self.btn.setVisible(True)
            self.lbl_pic.setStyleSheet("")
            self.btn.setStyleSheet(style) 
        elif item_type == 2:
            self.lbl_pic.setVisible(True)
            self.btn.setVisible(False)
            if not has_image:
                self.lbl_pic.setText(self.title)
                self.lbl_pic.adjustSize()
            self.lbl_pic.setStyleSheet("QLabel {color: rgb(170, 255, 255);} QLabel:hover {background-color: rgb(0, 0, 79);}")
        elif item_type == 3:
            self.lbl_pic.setVisible(True)
            self.btn.setVisible(True)
            self.btn.setStyleSheet(style)

        if item_type == 1:
            self.lbl_pic.move(0, 0)
            self.btn.move(self.lbl_pic.width() + 3, 0)
            w = self.btn.pos().x() + self.btn.width()
            h = self.btn.height()
        elif item_type == 2:
            self.lbl_pic.move(1, 1)
            w = self.lbl_pic.width() + 2
            h = self.lbl_pic.height() + 2
        elif item_type == 3:
            self.lbl_pic.move(0, 0)
            self.btn.move(self.lbl_pic.width() + 3, 0)
            w = self.btn.pos().x() + self.btn.width()
            h = self.btn.height()

        self.resize(w, h)
        self.show()


class Card(QFrame):
    def __init__(self, parent_widget, settings: settings_cls.Settings, html_code: str, card_type: str, card_setting: dict = None):
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.card_type = card_type
        self.html_code = html_code
        self.card_setting = card_setting
        self.parent_widget: AbstractTopic = parent_widget.parent()
        self.html_parser = html_parser_cls.HtmlParser()
        self.fix_url = self.parent_widget.fix_url

        self.create_card()

    def create_card(self):
        self._define_frame()

        if self.card_type == "small_poster":
            self._create_small_poster()
        elif self.card_type == "tv_small":
            self._create_tv_small_card()
        elif self.card_type == "tv-program":
            self._create_tv_program_card()
        elif self.card_type == "tv-film":
            self._create_tv_program_card()
        elif self.card_type == "movie":
            self._create_movie_card()
        elif self.card_type == "selector":
            self._create_movie_card()
        elif self.card_type == "https://tvprofil.com/film":
            self._create_movie_card()
        elif self.card_type == "https://tvprofil.com/serije":
            self._create_movie_card()
        elif self.card_type == "https://www.cineplexx.rs":
            self._create_movie_card()
        elif self.card_type == "wikipedia":
            self._create_wikipedia_card()
        elif self.card_type == "find":
            self._create_find_card()
        elif self.card_type == "search_movie":
            self._create_find_card()
        elif self.card_type == "search_title":
            self._create_find_card()

    def _create_wikipedia_card(self):
        card = WikipediaCard(self, self._stt, self.parent_widget.active_page, self.card_setting, card_id=self.parent_widget.active_page)
        card.move(0, 0)
        self.resize(card.width(), card.height())
        card.signal_size_changed.connect(self.wiki_signal_size_changed)
    
    def wiki_signal_size_changed(self, size: QSize, card_id):
        self.resize(size)
        if self.card_setting.get("size_changed_feedback", None):
            self.card_setting["size_changed_feedback"](size)

    def _create_find_card(self):
        w = self.card_setting.get("width", 600)
        y = 0
        x = 0

        # Title
        lbl_title = QLabel(self)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_title.setAlignment(Qt.AlignCenter)
        text_to_html = utility_cls.TextToHTML(text=self.getl("online_topic_aladin_tv_find_title_text") + "\n(#--1)")
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
        sup_text = self.getl("online_topic_aladin_tv_find_supported_text") + " (#--1)"
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

        # All search results
        lbl_all = QLabel(self)
        lbl_all.setTextInteractionFlags(lbl_all.textInteractionFlags()|Qt.TextSelectableByMouse)
        all_text = self.getl("online_topic_aladin_tv_find_unsupported_text") + " (#--1)"
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
        for item in self.html_code:
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
        for item in self.html_code:
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

    def _create_movie_card(self):
        if self.card_type == "movie":
            data = self._get_aladin_movie_data()
        elif self.card_type == "selector":
            data = self._get_aladin_selector_data()
        elif self.card_type == "https://tvprofil.com/film":
            data = self._get_tvprofil_film_data()
        elif self.card_type == "https://tvprofil.com/serije":
            data = self._get_tvprofil_film_data()
        elif self.card_type == "https://www.cineplexx.rs":
            data = self._get_cineplexx_film_data()

        self._create_movie_frame(data)

    def _get_cineplexx_film_data(self) -> dict:
        data = self._get_empty_movie_data_dictionary()

        # Title and Description
        title = ""
        description = ""
        title_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="span12")
        for title_code_segment in title_code:
            if "<h1>" in title_code_segment and not title:
                title = self.html_parser.get_raw_text(load_html_code=title_code_segment).strip()
            if "<h2>" in title_code_segment:
                tag_h2 = self.html_parser.get_tags(html_code=title_code_segment, tag="h2")
                if tag_h2:
                    text = self.html_parser.get_raw_text(load_html_code=tag_h2[0]).lower()
                    if "sadr" in text:
                        desc_code = self.html_parser.get_tags(html_code=title_code_segment, tag="p")
                        for desc_code_segment in desc_code:
                            description += self.html_parser.get_raw_text(load_html_code=desc_code_segment).strip() + "\n"
                        description = description.strip()

        # Image and Movie Info
        image = ""
        original_title = ""
        duration = ""
        year = ""
        genres = ""
        actors = []
        directors = []
        info_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="span8 filmdetails")
        if info_code:
            # Image
            images = self.html_parser.get_all_images(load_html_code=info_code[0])
            if images:
                image = images[0].img_src
                if image.startswith("/"):
                    image = "https://www.cineplexx.rs" + image
            
            movie_info_code = self.html_parser.get_tags(html_code=info_code[0], tag="tr")
            for info_segment in movie_info_code:
                text_slices = self.html_parser.get_all_text_slices(load_html_code=info_segment)
                if text_slices:
                    segment_title = text_slices[0].txt_value.lower()
                    segment_data = ""
                    for idx in range(1, len(text_slices)):
                        segment_data += text_slices[idx].txt_value + " "
                    segment_data = segment_data.strip()

                    if "originalni naslov" in segment_title:
                        original_title = segment_data
                    elif "trajanja filma" in segment_title:
                        duration = segment_data
                    elif "godina:" in segment_title:
                        year = segment_data
                    elif "anr:" in segment_title:
                        genres = "\n".join(segment_data.split(","))
                    elif "glumci:" in segment_title:
                        for i in segment_data.split(","):
                            actor = self._get_empty_actor_director_dictionary()
                            actor["name"] = i
                            actor["image"] = self.getv("online_topic_aladin_tv_no_image_icon_path")
                            actor["image_w"] = 60
                            actor["image_h"] = 92
                            actors.append(actor)
                    elif "iser:" in segment_title:
                        for i in segment_data.split(","):
                            director = self._get_empty_actor_director_dictionary()
                            director["name"] = i
                            director["image"] = self.getv("online_topic_aladin_tv_no_image_icon_path")
                            director["image_w"] = 60
                            director["image_h"] = 92
                            directors.append(director)

        data["title"] = title.encode('latin-1').decode('utf-8')
        data["original_title"] = original_title.encode('latin-1').decode('utf-8')
        data["description"] = description.encode('latin-1').decode('utf-8')
        data["image"] = image
        data["genres"] = genres.encode('latin-1').decode('utf-8')
        data["year"] = year.encode('latin-1').decode('utf-8')
        data["duration"] = duration.encode('latin-1').decode('utf-8')
        data["directors"] = directors
        data["actors_line"] = actors

        return data

    def _get_tvprofil_film_data(self) -> dict:
        data = self._get_empty_movie_data_dictionary()

        # Title
        title = ""
        title_code = self.html_parser.get_tags(html_code=self.html_code, tag="h1", custom_tag_property=[["itemprop", "name"]])
        if title_code:
            title = self.html_parser.get_raw_text(load_html_code=title_code[0]).strip()

        # Year
        year = ""
        year_code = self.html_parser.get_tags(html_code=self.html_code, tag="span", custom_tag_property=[["itemprop", "dateCreated"]])
        if year_code:
            year = self.html_parser.get_raw_text(load_html_code=year_code[0]).strip()
        
        # Duration
        duration = ""
        duration_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains='""')
        for i in duration_code:
            if "TRAJANJE:" in i:
                duration_code_clean = self.html_parser.remove_specific_tag(html_code=i, tag="strong", multiline=True)
                duration = self.html_parser.get_raw_text(load_html_code=duration_code_clean).strip()
                break

        # Image
        image = ""
        image_code = self.html_parser.get_tags(html_code=self.html_code, tag="img", custom_tag_property=[["itemprop", "image"], ["class", "poster"]])
        if image_code:
            images = self.html_parser.get_all_images(load_html_code=image_code[0])
            if images:
                image = images[0].img_src
        
        # Genres
        genres = ""
        genres_code = self.html_parser.get_tags(html_code=self.html_code, tag="span", custom_tag_property=[["itemprop", "genre"]])
        if genres_code:
            genres = self.html_parser.get_raw_text(load_html_code=genres_code[0]).strip().replace(" ", "\n")
        
        directors = []
        director_codes = self.html_parser.get_tags(html_code=self.html_code, tag="a", custom_tag_property=[["itemprop", "director"]])
        if director_codes:
            director_info = self._get_empty_actor_director_dictionary()
            director_info["name"] = self.html_parser.get_raw_text(load_html_code=director_codes[0]).strip().replace("\n", "  ")
            directors.append(director_info)
        
        # Trailer
        trailer = ""
        trailer_code = self.html_parser.get_tags(html_code=self.html_code, tag="iframe", tag_class_contains="embed-responsive-item")
        if trailer_code:
            trailer = self.html_parser.get_tag_property_value(html_code=trailer_code[0], tag="iframe", tag_property="src", return_first=True)

        # Description
        description = ""
        description_code = self.html_parser.get_tags(html_code=self.html_code, tag="p", custom_tag_property=[["itemprop", "description"], ["class", "description"]])
        if description_code:
            description = self.html_parser.get_raw_text(load_html_code=description_code[0]).strip()
        else:
            description_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="col-lg-8 col-md-9")
            if description_code:
                description_code = self.html_parser.get_tags(html_code=description_code[0], tag="p")
                if description_code:
                    description = self.html_parser.get_raw_text(load_html_code=description_code[0]).strip()
        
        # Actors
        actors_line = []
        actor_codes = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="col-md-5")
        if actor_codes:
            actor_list = self.html_parser.get_tags(html_code=actor_codes[0], tag="ul", tag_class_contains="results")
            if actor_list:
                actor_items = self.html_parser.get_tags(html_code=actor_list[0], tag="li")
                for actor_item in actor_items:
                    actor_info = self._get_empty_actor_director_dictionary()

                    actor_name = ""
                    actor_name_code = self.html_parser.get_tags(html_code=actor_item, tag="div", tag_class_contains="name")
                    if actor_name_code:
                        actor_name = self.html_parser.get_raw_text(load_html_code=actor_name_code[0]).strip().replace("\n", "  ")
                    
                    actor_role_code = self.html_parser.get_tags(html_code=actor_item, tag="div", tag_class_contains="charname")
                    if actor_role_code:
                        actor_name += "(" + self.html_parser.get_raw_text(load_html_code=actor_role_code[0]).strip().replace("\n", "  ") + ")"
                    
                    
                    actor_image = ""
                    actor_image_code = self.html_parser.get_tags(html_code=actor_item, tag="img")
                    if actor_image_code:
                        actor_image = self.html_parser.get_tag_property_value(html_code=actor_image_code[0], tag="img", tag_property="src", return_first=True)
                        actor_image_w = self.html_parser.get_tag_property_value(html_code=actor_image_code[0], tag="img", tag_property="width", return_first=True)
                        actor_image_h = self.html_parser.get_tag_property_value(html_code=actor_image_code[0], tag="img", tag_property="height", return_first=True)

                    actor_info["name"] = actor_name
                    actor_info["image"] = actor_image
                    if actor_image_w:
                        actor_info["image_w"] = actor_image_w
                    if actor_image_h:
                        actor_info["image_h"] = actor_image_h

                    actors_line.append(actor_info)

        data["title"] = title
        data["description"] = description
        data["image"] = image
        data["genres"] = genres
        data["year"] = year
        data["duration"] = duration
        data["directors"] = directors
        data["actors_line"] = actors_line
        data["trailer"] = trailer
        
        return data

    def _get_aladin_selector_data(self) -> dict:
        data = self._get_empty_movie_data_dictionary()
        self.html_code = self.html_code.replace('<span class="block mb10 strong">', '<br><span class="block mb10 strong">')
        self.html_code = self.html_code.replace('<div class="text-center">', '<br><div class="text-center">')

        # Title
        title = ""
        title_code = self.html_parser.get_tags(html_code=self.html_code, tag="h4", tag_class_contains="modal-title")
        if title_code:
            title = self.html_parser.get_raw_text(load_html_code=title_code[0]).strip()

        # Image
        image = ""
        image_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="text-center")
        if image_code:
            images = self.html_parser.get_all_images(load_html_code=image_code[0])
            if images:
                image = self.fix_url(images[0].img_src)
    
        # Description
        description = ""
        description_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="modal-body")
        if description_code:
            description = self.html_parser.get_raw_text(load_html_code=description_code[0]).strip()

        # Actors line
        actors_line = []
        actors_code = self.html_parser.get_tags(html_code=self.html_code, tag="table", tag_class_contains="table table-striped")
        if actors_code:
            actors_link_code = self.html_parser.get_tags(html_code=actors_code[0], tag="a")
            for actor_code in actors_link_code:
                links = self.html_parser.get_all_links(load_html_code=actor_code)
                if links:
                    actor_imdb = self.fix_url(links[0].a_href)
                    actor_name = links[0].a_title
                images = self.html_parser.get_all_images(load_html_code=actor_code)
                actor_image = ""
                if images:
                    actor_image = self.fix_url(images[0].img_src)

                actor = {
                    "name": actor_name,
                    "image": actor_image,
                    "imdb": actor_imdb,
                    "image_w": 60,
                    "image_h": 88
                }
                actors_line.append(actor)

        # Trailer
        trailer = ""
        trailer_code = self.html_parser.get_tags(html_code=self.html_code, tag="iframe")
        if trailer_code:
            trailer = self.fix_url(self.html_parser.get_tag_property_value(html_code=trailer_code[0], tag_property="src", return_first=True))
            if trailer is None:
                trailer = ""

        data["title"] = title
        data["description"] = description
        data["image"] = image
        data["actors_line"] = actors_line
        data["trailer"] = trailer
        
        return data

    def _create_movie_frame(self, movie_data: dict):
        self._define_frame(self)
        frame_w = self.card_setting.get("width", 400)

        # Banner
        lbl_banner = self._movie_frame_create_banner(movie_data=movie_data)
        # Movie Image
        frm_pic = self._movie_frame_create_movie_image(movie_data=movie_data)
        # Movie Info
        lbl_info = self._movie_frame_create_movie_info(movie_data=movie_data)
        # Movie content
        frm_content = self._movie_frame_create_content(movie_data=movie_data)
        # Director(s)
        frm_directors = self._movie_frame_create_directors(movie_data=movie_data)
        # Actors
        frm_actors = self._movie_frame_create_actors(movie_data=movie_data)
        # Actors Line
        frm_actors_line = self._movie_frame_create_actors_line(movie_data=movie_data)
        # Trailer
        web_trailer = self._movie_frame_create_movie_trailer(movie_data=movie_data)

        x = int((frame_w - lbl_banner.width()) / 2)
        if x < 0:
            x = 0
        lbl_banner.move(x, 0)
        y = lbl_banner.height() + 10

        frm_pic.move(0, y)
        lbl_info.move(frm_pic.width() + 20, y)
        y = max(frm_pic.height() + y, lbl_info.height() + y)
        y += 10

        frm_content.move(0, y)
        y += frm_content.height() + 10

        frm_directors.move(0, y)
        y += frm_directors.height() + 10

        frm_actors.move(0, y)
        y += frm_actors.height() + 10

        frm_actors_line.move(0, y)
        y += frm_actors_line.height() + 10

        if web_trailer.height() and lbl_info.pos().x() + lbl_info.width() + 20 + web_trailer.width() <= frame_w and lbl_banner.height() + 10 + web_trailer.height() <= max(frm_pic.height(), lbl_info.height()):
            web_trailer.move(lbl_info.pos().x() + lbl_info.width() + 20, lbl_banner.height() + 10)
        else:
            web_trailer.move(0, y)
            y += web_trailer.height()

        self.resize(frame_w, y)

    def _movie_frame_create_movie_trailer(self, movie_data: dict) -> QWebEngineView:
        if not movie_data["trailer"]:
            frm = QFrame(self)
            frm.resize(self.card_setting.get("width", 400), 0)
            return frm
        
        web = QWebEngineView(self)
        w = self.card_setting.get("width", 800)
        if w > 800:
            w = 800
        
        h = int(w/16*9)

        web.resize(w, h)
        url = movie_data["trailer"]
        web.setUrl(QUrl(url))
        return web

    def _movie_frame_create_actors_line(self, movie_data: dict) -> QFrame:
        frm = QFrame(self)
        self._define_frame(frm)

        lbl_w = self.card_setting.get("width", 400) - 20
        frm.resize(lbl_w, 0)

        actors_line = movie_data["actors_line"]
        x = 5
        y = 5
        item_h = 0
        for actor_line in actors_line:
            lbl_pic = QLabel(frm)
            lbl_pic.setAlignment(Qt.AlignCenter)
            lbl_pic.resize(int(actor_line.get("image_w", 60)), int(actor_line.get("image_h", 88)))
            self.parent_widget.set_image_to_label(actor_line["image"], lbl_pic)

            lbl_name = QLabel(frm)
            lbl_name.setTextInteractionFlags(lbl_name.textInteractionFlags()|Qt.TextSelectableByMouse)
            lbl_name.setWordWrap(True)
            text_to_html = utility_cls.TextToHTML()
            text_to_html.general_rule.fg_color = "#ffff00"
            text_to_html.general_rule.font_size = 12
            title = actor_line["name"]
            if "(" in title:
                pos = title.find("(")
                title1 = title[pos:]
                title = title[:pos] + "\n#--1"
                rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=title1, fg_color="#aaff7f")
                text_to_html.add_rule(rule)
            text_to_html.set_text(title)
            lbl_name.setStyleSheet("color: #ffff00; background-color: #000000;")
            lbl_name.setText(text_to_html.get_html())
            lbl_name.setAlignment(Qt.AlignCenter)
            lbl_name.adjustSize()

            lbl_imdb = QLabel(frm)
            link = actor_line["imdb"]
            if link:
                lbl_imdb.setAlignment(Qt.AlignCenter)
                text_to_html = utility_cls.TextToHTML(text="imdb")
                text_to_html.general_rule.fg_color = "#ffffff"
                text_to_html.general_rule.font_size = 8
                rule = utility_cls.TextToHtmlRule(text="imdb", link_href=link)
                text_to_html.add_rule(rule)
                lbl_imdb.setText(text_to_html.get_html())
                lbl_imdb.adjustSize()
                lbl_imdb.linkActivated.connect(lambda _, link_val=link: self.external_link(link_val))
            else:
                lbl_imdb.resize(0, 0)

            actor_w = max(lbl_pic.width(), lbl_name.width(), lbl_imdb.width())

            if actor_w + x > frm.width() - 10:
                x = 5
                y += item_h + 20

            lbl_pic.move(x + int((actor_w - lbl_pic.width())/2), y)
            lbl_name.move(x, lbl_pic.pos().y() + lbl_pic.height())
            lbl_name.resize(actor_w, lbl_name.height())
            lbl_imdb.move(x, lbl_name.pos().y() + lbl_name.height())
            lbl_imdb.resize(actor_w, lbl_imdb.height())

            item_h = max(item_h, lbl_imdb.pos().y() + lbl_imdb.height() - y)
            
            x += actor_w + 20

        if x > 5 or y > 5:
            y += item_h + 5
            frm.resize(frm.width(), y)
        return frm

    def _movie_frame_create_actors(self, movie_data: dict) -> QFrame:
        frm = QFrame(self)
        self._define_frame(frm)

        lbl_w = self.card_setting.get("width", 400)
        lbl_title = QLabel(frm)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_title.resize(lbl_w, 20)
        font = lbl_title.font()
        font.setPointSize(16)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("color: #ffff00;")
        lbl_title.setText("Uloge")
        lbl_title.adjustSize()
        lbl_title.move(0, 0)

        line = QFrame(frm)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.move(10, lbl_title.height() + 4)

        y = lbl_title.height() + 10
        w = lbl_title.width()
        for item in movie_data["actors"]:
            director = self._create_actor_director_item_frame(parent_widget=frm, item_data=item)
            director.move(0, y)
            y += director.height() + 5
            w = max(w, director.width())

        line.resize(w -20, 3)
        frm.resize(w, y)
        return frm

    def _movie_frame_create_directors(self, movie_data: dict) -> QFrame:
        frm = QFrame(self)
        self._define_frame(frm)

        lbl_w = self.card_setting.get("width", 400)
        lbl_title = QLabel(frm)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_title.resize(lbl_w, 20)
        font = lbl_title.font()
        font.setPointSize(16)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("color: #ffff00;")
        lbl_title.setText("Režija")
        lbl_title.adjustSize()
        lbl_title.move(0, 0)

        line = QFrame(frm)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.move(10, lbl_title.height() + 4)

        y = lbl_title.height() + 10
        w = lbl_title.width()
        for item in movie_data["directors"]:
            director = self._create_actor_director_item_frame(parent_widget=frm, item_data=item)
            director.move(0, y)
            y += director.height() + 5
            w = max(w, director.width())

        line.resize(w -20, 3)
        frm.resize(w, y)
        return frm

    def _create_actor_director_item_frame(self, parent_widget: QFrame, item_data: dict) -> QFrame:
        frm = QFrame(parent_widget)
        self._define_frame(frm)
        frm.setStyleSheet("background-color: #001800;")

        lbl_pic = QLabel(frm)
        lbl_pic.setAlignment(Qt.AlignCenter)
        lbl_pic.resize(100, lbl_pic.height())
        if item_data["image"]:
            self.parent_widget.set_image_to_label(item_data["image"], lbl_pic, resize_label_fixed_w=True)
        lbl_pic.move(5, 5)
        
        lbl_name = QLabel(frm)
        lbl_name.setTextInteractionFlags(lbl_name.textInteractionFlags()|Qt.TextSelectableByMouse)
        font = lbl_name.font()
        font.setPointSize(12)
        font.setBold(True)
        lbl_name.setFont(font)
        lbl_name.setStyleSheet("color: #00ff7f;")
        lbl_name.setText(item_data["name"])
        lbl_name.adjustSize()
        if lbl_name.width() <= lbl_pic.width():
            lbl_name.setAlignment(Qt.AlignCenter)
            lbl_name.resize(lbl_pic.width(), lbl_name.height())
        lbl_name.move(5, lbl_pic.pos().y() + lbl_pic.height())

        lbl_imdb = QLabel(frm)
        lbl_imdb.setAlignment(Qt.AlignCenter)
        text_to_html = utility_cls.TextToHTML(text="imdb.com")
        rule = utility_cls.TextToHtmlRule(text="imdb.com", link_href=item_data["imdb"], fg_color="#aaffff")
        text_to_html.add_rule(rule)
        lbl_imdb.setText(text_to_html.get_html())
        lbl_imdb.setToolTip(self.getl("imdb_link"))
        lbl_imdb.move(5, lbl_name.pos().y() + lbl_name.height())
        lbl_imdb.adjustSize()
        lbl_imdb.resize(lbl_name.width(), lbl_imdb.height())
        lbl_imdb.linkActivated.connect(self.external_link)

        frm_movies = QFrame(frm)
        self._define_frame(frm_movies)
        frm_movies.move(max(lbl_pic.width() + 20, lbl_name.width() + 20), 5)

        movie_images = []
        x = 0
        y = 0
        max_btn_h = 0
        max_x = self.card_setting.get("width", 400) - frm_movies.pos().x() - 5
        for movie in item_data["filmography"]:
            if movie["image"]:
                movie_images.append(movie)
            
            btn = QPushButton(frm_movies)
            btn.setStyleSheet("QPushButton {color: white; background-color: #000055;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
            link = movie["link"]
            btn.setText(movie["title"])
            btn.setCursor(Qt.PointingHandCursor)
            font = btn.font()
            font.setPointSize(12)
            btn.setFont(font)
            btn.adjustSize()
            feedback_function = self.card_setting["feedback"]
            btn.clicked.connect(lambda _, link_val=link: feedback_function(link_val))
            
            if x == 0:
                max_btn_h = max(max_btn_h, btn.height())
                btn.move(x, y)
                x += btn.width() + 10
                frm_movies.resize(max_x, btn.pos().y() + btn.height() + 5)
            else:
                if x + btn.width() > max_x:
                    x = 0
                    y += max_btn_h + 10
                    max_btn_h = 0
                    btn.move(0, y)
                    x = btn.width() + 10
                    frm_movies.resize(max_x, btn.pos().y() + btn.height() + 5)
                else:
                    btn.move(x, y)
                    x += btn.width() + 10
                    max_btn_h = max(max_btn_h, btn.height())
        
        frm_movie_img = QFrame(frm)
        if movie_images:
            frm_movie_img.resize(max_x, 105)
        else:
            frm_movie_img.resize(max_x, 0)
        self._define_frame(frm_movie_img)
        frm_movie_img.move(max(lbl_pic.width() + 20, lbl_name.width() + 10), frm_movies.pos().y() + frm_movies.height() + 10)

        x = 0
        for movie_image in movie_images:
            lbl_movie_pic = QLabel(frm_movie_img)
            lbl_movie_pic.setAlignment(Qt.AlignCenter)
            lbl_movie_pic.resize(70, 100)
            lbl_movie_pic.setCursor(Qt.PointingHandCursor)
            self.parent_widget.set_image_to_label(movie_image["image"], lbl_movie_pic)
            lbl_movie_pic.setToolTip(movie_image["title"])
            lbl_movie_pic.move(x, 0)
            feedback_function = self.card_setting["feedback"]
            link = movie_image["link"]
            lbl_movie_pic.mousePressEvent = lambda _, link_val=link: feedback_function(link_val)
            x += 80

        h = max(frm_movie_img.pos().y() + frm_movie_img.height() + 5, lbl_imdb.pos().y() + lbl_imdb.height() + 5)
        frm.resize(self.card_setting.get("width", 400), h)
        return frm

    def external_link(self, url: str):
        webbrowser.open_new_tab(url)

    def _movie_frame_create_content(self, movie_data: dict) -> QFrame:
        frm = QFrame(self)
        self._define_frame(frm)

        lbl_w = self.card_setting.get("width", 400)
        lbl_title = QLabel(frm)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_title.resize(lbl_w, 20)
        font = lbl_title.font()
        font.setPointSize(16)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("color: #ffff00;")
        lbl_title.setText("Sadržaj")
        lbl_title.adjustSize()

        line = QFrame(frm)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        lbl_content = QLabel(frm)
        lbl_content.setTextInteractionFlags(lbl_content.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_content.setFixedWidth(lbl_w)
        lbl_content.setWordWrap(True)
        font = lbl_content.font()
        font.setPointSize(12)
        lbl_content.setFont(font)
        lbl_content.setStyleSheet("color: #aaff7f;")
        lbl_content.setText(movie_data["description"])
        lbl_content.adjustSize()

        lbl_title.move(0, 0)
        line.move(10, lbl_title.height() + 4)
        line.resize(lbl_w - 20, 3)
        lbl_content.move(0, lbl_title.height() + 10)
        frm.resize(lbl_w, lbl_title.height() + lbl_content.height() + 10)

        return frm

    def _movie_frame_create_movie_info(self, movie_data: dict) -> QLabel:
        lbl = QLabel(self)
        lbl.setTextInteractionFlags(lbl.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_w =  self.card_setting.get("width", 400) - self.card_setting.get("image_width", 200) - 20
        lbl.resize(lbl_w, 20)
        lbl.setWordWrap(True)
        if movie_data["movie_info"]:
            lbl.setText(movie_data["movie_info"])
            lbl.adjustSize()
            return lbl
        
        text_to_html = utility_cls.TextToHTML()
        text_to_html.general_rule.font_size = 16
        text_to_html.general_rule.fg_color = "#00ff00"
        text = ""

        repl_text = movie_data["title"]
        if repl_text:
            text += "Naziv\n#1\n"
            rule = utility_cls.TextToHtmlRule(text="#1", replace_with=repl_text, fg_color="#aaff7f")
            text_to_html.add_rule(rule)

        repl_text = movie_data["original_title"]
        if repl_text:
            text += "\nOriginalni Naziv\n#2\n"
            rule = utility_cls.TextToHtmlRule(text="#2", replace_with=repl_text, fg_color="#aaff7f")
            text_to_html.add_rule(rule)
        
        repl_text = movie_data["genres"]
        if repl_text:
            text += "\nŽanr\n#3\n"
            rule = utility_cls.TextToHtmlRule(text="#3", replace_with=repl_text, fg_color="#aaff7f")
            text_to_html.add_rule(rule)

        repl_text = movie_data["year"]
        if repl_text:
            text += "\nGodina\n#4\n"
            rule = utility_cls.TextToHtmlRule(text="#4", replace_with=repl_text, fg_color="#aaff7f")
            text_to_html.add_rule(rule)

        repl_text = movie_data["duration"]
        if repl_text:
            text += "\nTrajanje\n#5\n"
            rule = utility_cls.TextToHtmlRule(text="#5", replace_with=repl_text, fg_color="#aaff7f")
            text_to_html.add_rule(rule)

        text_to_html.set_text(text)
        lbl.setText(text_to_html.get_html())
        lbl.adjustSize()
        return lbl

    def _movie_frame_create_movie_image(self, movie_data: dict) -> QFrame:
        frm = QFrame(self)
        self._define_frame(frm)

        if not movie_data["image"]:
            frm.resize(0, 0)
            return frm
        
        lbl_pic = QLabel(frm)
        lbl_pic.setAlignment(Qt.AlignCenter)
        lbl_pic.resize(self.card_setting.get("image_width", 200), 10)
        self.parent_widget.set_image_to_label(movie_data["image"], lbl_pic, resize_label_fixed_w=True)

        lbl_name = QLabel(frm)
        lbl_name.setTextInteractionFlags(lbl_name.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_name.setWordWrap(True)
        lbl_name.setAlignment(Qt.AlignCenter)
        text = movie_data["title"]
        if movie_data["year"] and movie_data["year"] not in text:
            text += f' ({movie_data["year"]})'
        lbl_name.setText(text)
        font = lbl_name.font()
        font.setPointSize(14)
        lbl_name.setFont(font)
        lbl_name.setStyleSheet("color: #00ff00; background-color: #000000;")
        lbl_name.setFixedWidth(lbl_pic.width())
        lbl_name.adjustSize()
        
        lbl_pic.move(0, 0)
        lbl_name.move(0, lbl_pic.height())
        frm.resize(lbl_pic.width(), lbl_pic.height() + lbl_name.height())

        return frm

    def _movie_frame_create_banner(self, movie_data: dict) -> QLabel:
        lbl = QLabel(self)
        if not movie_data["banner_image"]:
            lbl.resize(0, 0)
            return lbl
        
        lbl.setAlignment(Qt.AlignCenter)
        lbl.resize(10, self.card_setting.get("banner_height", 200))
        self.parent_widget.set_image_to_label(movie_data["banner_image"], lbl, resize_label_fixed_h=True)

        return lbl

    def _get_aladin_movie_data(self) -> dict:
        data = self._get_empty_movie_data_dictionary()
        
        title = ""
        title_code = self.html_parser.get_tags(html_code=self.html_code, tag="h1")
        if title_code:
            title = self.html_parser.get_raw_text(load_html_code=title_code[0])
        
        banner_image = ""
        banner_image_code = self.html_parser.get_tags(html_code=self.html_code, tag="img", tag_class_contains="img-responsive mb10")
        if banner_image_code:
            banner_image_code = self.html_parser.get_all_images(load_html_code=banner_image_code[0])
            if banner_image_code:
                banner_image = self.fix_url(banner_image_code[0].img_src)
        
        movie_info = ""
        movie_info_code = self.html_parser.get_tags(html_code=self.html_code, tag="ul", tag_class_contains="list-unstyled")
        if movie_info_code:
            text_slices = self.html_parser.get_all_text_slices(load_html_code=movie_info_code[0])
            if text_slices:
                text_to_html = utility_cls.TextToHTML()
                text = ""
                text_to_html.general_rule.fg_color = "#00ff00"
                text_to_html.general_rule.font_size = 16
                count = 1
                for text_slice in text_slices:
                    text_slice: html_parser_cls.TextObject
                    if "strong" in text_slice.get_tag():
                        color = "#00ff00"
                        if text:
                            replace_text = "\n" + text_slice.txt_value + "\n"
                        else:
                            replace_text = text_slice.txt_value + "\n"
                    else:
                        color = "#aaff7f"
                        replace_text = "    " + text_slice.txt_value + "\n"
                    
                    if not replace_text:
                        continue
                    
                    rule_text = "#" + "-" * (5 - len(str(count))) + str(count)
                    text_rule = utility_cls.TextToHtmlRule(text=rule_text, replace_with=replace_text, fg_color=color)
                    text_to_html.add_rule(text_rule)
                    text += rule_text
                    count += 1
                text_to_html.set_text(text)
                movie_info = text_to_html.get_html()
        
        description = ""
        description_code = self.html_parser.get_tags(html_code=self.html_code, tag="p", tag_class_contains="pl10 pr10")
        if description_code:
            description = self.html_parser.get_raw_text(load_html_code=description_code[0]).strip()
        
        image = ""
        image_code = self.html_parser.get_tags(html_code=self.html_code, tag="img", tag_class_contains="img-responsive img-thumbnail")
        if image_code:
            images = self.html_parser.get_all_images(load_html_code=image_code[0])
            if images:
                image = self.fix_url(images[0].img_src)
        
        actors = []
        directors = []
        actors_code = self.html_parser.get_tags(html_code=self.html_code, tag="table")
        if actors_code:
            table_type_htmls = self.html_parser.get_tags(html_code=self.html_code, tag="h4")
            for idx, html_code in enumerate(actors_code):
                if len(table_type_htmls) != len(actors_code):
                    break
                table_type = table_type_htmls[idx]
                if self.html_parser.get_raw_text(load_html_code=table_type).strip() == "Uloge":
                    result = self._aladin_movie_data_add_actor_director(html_code=html_code)
                    for i in result:
                        actors.append(i)
                elif self.html_parser.get_raw_text(load_html_code=table_type).strip() == "Režija":
                    result = self._aladin_movie_data_add_actor_director(html_code=html_code)
                    for i in result:
                        directors.append(i)

        trailer = ""
        trailer_code = self.html_parser.get_tags(html_code=self.html_code, tag="iframe")
        if trailer_code:
            trailer = self.fix_url(self.html_parser.get_tag_property_value(html_code=trailer_code[0], tag_property="src", return_first=True))
            if trailer is None:
                trailer = ""

        
        data["title"] = title
        data["banner_image"] = banner_image
        data["movie_info"] = movie_info
        data["description"] = description
        data["image"] = image
        data["actors"] = actors
        data["directors"] = directors
        data["trailer"] = trailer

        return data
    
    def _aladin_movie_data_add_actor_director(self, html_code: str) -> dict:
        actors = self.html_parser.get_tags(html_code=html_code, tag="tr")
        return_list = []
        
        for actor in actors:
            result = self._get_empty_actor_director_dictionary()
            data = self.html_parser.get_tags(html_code=actor, tag="td", tag_class_contains="text-center")
            imdb_link = ""
            image = ""
            if data:
                links = self.html_parser.get_all_links(load_html_code=data[0])
                if links:
                    imdb_link = self.fix_url(links[0].a_href)
                images = self.html_parser.get_all_images(load_html_code=data[0])
                if images:
                    image = self.fix_url(images[0].img_src)
            
            data = self.html_parser.get_tags(html_code=actor, tag="li")
            movies = []
            name = ""

            for item in data:
                links = self.html_parser.get_all_links(load_html_code=item)
                if not links:
                    continue
                if links[0].a_href.startswith("#"):
                    continue

                if "strong" in links[0].a_class and not name:
                    name = links[0].a_text
                    continue

                movie = self._get_empty_movie_data_dictionary()
                movie["title"] = links[0].a_text
                movie["link"] = self.fix_url(links[0].a_href)

                movies.append(movie)
            
            data = self.html_parser.get_tags(html_code=actor, tag="td", tag_class_contains="pt10 col-xs-7")
            if data:
                data1 = self.html_parser.get_tags(html_code=data[0], tag="a")
                for item in data1:
                    images = self.html_parser.get_all_images(load_html_code=item)
                    if images:
                        for movie in movies:
                            if movie["title"] == images[0].img_title:
                                movie["image"] = self.fix_url(images[0].img_src)
            
            result["imdb"] = imdb_link
            result["image"] = image
            result["name"] = name
            result["filmography"] = movies

            return_list.append(result)

        return return_list
    
    def _get_empty_movie_data_dictionary(self) -> dict:
        result = {
            "title": "",
            "original_title": "",
            "year": "",
            "duration": "",
            "genres": "",
            "movie_info": "",
            "description": "",
            "image": "",
            "banner_image": "",
            "actors": [],
            "directors": [],
            "link": "",
            "actors_line": [],
            "trailer": ""
        }
        return result
    
    def _get_empty_actor_director_dictionary(self) -> dict:
        result = {
            "name": "",
            "role": "",
            "image": "",
            "imdb": "",
            "filmography": []
            }
        return result

    def _create_tv_program_card(self):
        self.html_code = self.html_parser.remove_specific_tag(self.html_code, "thead", multiline=True)
        code = ""
        for line in self.html_code.splitlines():
            if line.startswith("<table"):
                code += '<ul class="list-group">\n'
                continue
            if line.startswith("</table"):
                code += '</ul>\n'
                continue
            code += line + "\n"
        self.html_code = code.strip()
        self.html_code = self.html_code.replace("<tr", "<li")
        self.html_code = self.html_code.replace("</tr", "</li")
        self._create_tv_small_card()

    def _create_tv_small_card(self):
        header = self._small_card_header()
        body = self._small_card_body()
        footer = self._small_card_footer()

        header.move(0, 0)
        body.move(0, header.height())
        footer.move(0, body.pos().y() + body.height())

        self.resize(self.card_setting.get("width", 300), footer.pos().y() + footer.height())

    def _small_card_header(self) -> QFrame:
        # Data
        title = ""
        link = ""
        image = ""
        table_title = self.card_setting.get("title", "")
        if table_title:
            title = " " + table_title
            pos = table_title.find(":")
            if pos != -1:
                image = self._get_tv_station_logo(table_title[pos:].strip(": "))
        else:
            title_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="panel-heading", multiline=True)
            if title_code:
                self.html_parser.load_html_code(title_code[0])
                title = " " + self.html_parser.get_raw_text().strip()
                links = self.html_parser.get_all_links()
                if links:
                    link = self.fix_url(links[0].a_href)

            image = self._get_tv_station_logo(title)
        
        # Widget
        self.header_frame = QFrame(self)
        self._define_frame(frame=self.header_frame)
        head_style = f'background-color: {self.card_setting.get("header_bg", "black")}; color: #ffff00;'
        self.header_frame.setStyleSheet(head_style)
        font = self.header_frame.font()
        self.header_frame.resize(self.card_setting.get("width", 300), self.card_setting.get("header_height", 40))

        self.lbl_head_title = QLabel(self.header_frame)
        self.lbl_head_title.setTextInteractionFlags(self.lbl_head_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        font.setPointSize(14)
        font.setBold(True)
        self.lbl_head_title.setFont(font)
        if link:
            self.lbl_head_title.setStyleSheet("QLabel {color: #ffff00;} QLabel:hover {color: #aaffff;}")
            feedback_function = self.card_setting["feedback"]
            self.lbl_head_title.mousePressEvent = lambda _, link_val=link: feedback_function(link_val)
            self.lbl_head_title.setCursor(Qt.PointingHandCursor)
        self.lbl_head_title.setText(title)
        self.lbl_head_title.move(0, 0)
        self.lbl_head_title.resize(self.header_frame.width(), self.header_frame.height())

        self.lbl_head_pic = QLabel(self.header_frame)
        self.lbl_head_pic.setAlignment(Qt.AlignCenter)
        self.lbl_head_pic.resize(self.lbl_head_pic.width(), self.header_frame.height() - 6)
        if image:
            self.parent_widget.set_image_to_label(image, self.lbl_head_pic, resize_label_fixed_h=True)
        self.lbl_head_pic.move(self.header_frame.width() - self.lbl_head_pic.width() - 3, 3)

        return self.header_frame

    def _get_tv_station_logo(self, station_name: str) -> str:
        station_name = self.parent_widget._clean_search_string(station_name).replace("+", "_")
        file_path_uncomplete = self.getv("online_topics_aladin_tv_channel_logo") + station_name
        
        image_extensions = [".png", ".svg", ".webp", ".jpg", ".jpeg", ".gif"]
        
        result = None
        for i in image_extensions:
            file_path = file_path_uncomplete + i
            if os.path.isfile(file_path):
                result = file_path
                break
        return result

    def _small_card_body(self) -> QFrame:
        self.body_frame = QFrame(self)
        self._define_frame(self.body_frame)
        body_style = f'background-color: {self.card_setting.get("body_bg", "black")}; color: #ffffff;'
        self.body_frame.setStyleSheet(body_style)
        font = self.body_frame.font()
        font.setPointSize(12)
        item_h = self.card_setting.get("item_height", 0)
        if not item_h:
            item_h = 30
        self.body_frame.resize(self.card_setting.get("width", 400), 20)

        items_code = self.html_parser.get_tags(html_code=self.html_code, tag="ul", tag_class_contains="list-group", multiline=True)
        self.body_items = []
        y = 0
        if items_code:
            items_code_list = self.html_parser.get_tags(html_code=items_code[0], tag="li", multiline=True)
            total_items = len(items_code_list)
            current_item = 0
            for item_code in items_code_list:
                time = ""
                title = ""
                title_ext = ""
                item_style = "QLabel {color: #83c3cf;"
                item_style2 = ""
                link = ""
                self.html_parser.load_html_code(item_code)
                item_text_slices = self.html_parser.get_all_text_slices()
                if item_text_slices:
                    if ('bg-warning' in self.html_parser.get_tag_property_value(html_code=item_code, tag="li", tag_property="class") and not self.card_setting.get("title", None)) or ('"bg-warning"' in item_code and self.card_setting.get("title", None)):
                        has_warning = True
                        time = " ⏰ " + item_text_slices[0].txt_value
                    else:
                        has_warning = False
                        time = " 🕒 " + item_text_slices[0].txt_value
                    for i in range(1, len(item_text_slices)):
                        if i == 1:
                            title += item_text_slices[i].txt_value + " "
                        else:
                            if self.card_type == "tv-film":
                                title_ext += item_text_slices[i].txt_value + " "
                            else:
                                title += item_text_slices[i].txt_value + " "
                    title = title.replace("\n", " ").strip()
                    title_ext = title_ext.replace("\n", " ").strip()
                    if 'span class="glyphicons film"' in item_code:
                        title = "🎬 " + title
                links = self.html_parser.get_all_links()
                if links:
                    item_style = "QLabel {color: #e4e7ff;"
                    link = self.fix_url(links[0].a_href)
                    item_style2 = " QLabel:hover {color: #aaffff;}"
                else:
                    if 'span class="glyphicons film"' in item_code:
                        link = f"#search_movie:opis filma {title.replace('🎬 ', '')}"
                        item_style2 = " QLabel:hover {color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0.261364 rgba(170, 255, 255, 255), stop:1 rgba(255, 187, 187, 255));}"
                    else:
                        if title != "No information":
                            link = f"#search_title:tv emisija {title}"
                            item_style2 = " QLabel:hover {color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0.261364 rgba(170, 255, 255, 255), stop:1 rgba(255, 187, 187, 255));}"
                
                if has_warning:
                    item_style = item_style + " background-color: " + self.card_setting["body_now_bg"] + ";} " + item_style2
                else:
                    item_style = item_style + "} " + item_style2
                
                lbl_title = QLabel(self.body_frame)
                lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
                lbl_title.setWordWrap(True)
                if link:
                    font.setBold(True)
                else:
                    font.setBold(False)
                lbl_title.setFont(font)
                lbl_title.setStyleSheet(item_style)
                lbl_title.setText(title)
                
                lbl_time = QLabel(self.body_frame)
                lbl_time.setTextInteractionFlags(lbl_time.textInteractionFlags()|Qt.TextSelectableByMouse)
                font.setBold(True)
                lbl_time.setFont(font)
                lbl_time.setText(time)
                item_style = item_style.replace("QLabel {color: #e4e7ff;", "QLabel {color: #ffffff;")
                item_style = item_style.replace("QLabel {color: #83c3cf;", "QLabel {color: #ffffff;")
                lbl_time.setStyleSheet(item_style)

                lbl_time.resize(90, item_h)
                lbl_time.move(0, y)
                lbl_title.move(lbl_time.width(), y)
                if self.card_type == "tv-film":
                    frm_item_ext = QFrame(self.body_frame)
                    frm_item_ext.resize(self.card_setting.get("item_ext_width", 300), item_h)
                    frm_item_ext.move(self.body_frame.width() - frm_item_ext.width(), y)
                    frm_item_ext = self._create_item_extension(frm_item_ext, text=title_ext)
                    lbl_title.setFixedWidth(self.body_frame.width() - lbl_title.pos().x() - frm_item_ext.width())
                    lbl_title.adjustSize()
                    if lbl_title.height() > item_h:
                        font_small = lbl_title.font()
                        font_small.setPointSize(10)
                        lbl_title.setFont(font_small)
                        lbl_title.adjustSize()
                    item_h = max(item_h, lbl_title.height())
                    lbl_title.resize(lbl_title.width(), item_h)
                else:
                    lbl_title.setFixedWidth(self.body_frame.width() - lbl_title.pos().x())
                    lbl_title.adjustSize()
                    if lbl_title.height() > item_h:
                        font_small = lbl_title.font()
                        font_small.setPointSize(10)
                        lbl_title.setFont(font_small)
                        lbl_title.adjustSize()
                    item_h = max(item_h, lbl_title.height())
                    lbl_title.resize(lbl_title.width(), item_h)
                
                y += item_h

                if link:
                    feedback_function = self.card_setting["feedback"]
                    lbl_title.mousePressEvent = lambda _, link_val=link: feedback_function(link_val)
                    lbl_title.setCursor(Qt.PointingHandCursor)

                if self.card_type == "tv-film":
                    self.body_items.append([lbl_time, lbl_title, frm_item_ext])
                else:
                    self.body_items.append([lbl_time, lbl_title])

                current_item += 1
                self.parent_widget.prg_progress.setValue(int(current_item*100/total_items))
                QCoreApplication.processEvents()
                if self.parent_widget.stop_loading:
                    break

        self.body_frame.resize(self.body_frame.width(), y)
        
        return self.body_frame

    def _create_item_extension(self, frame: QFrame, text: str):
        w = frame.width()
        h = frame.height()

        self._define_frame(frame)
        lbl_pic = QLabel(frame)
        lbl_pic.resize(h, h - 10)
        image = self._get_tv_station_logo(text)
        self.parent_widget.set_image_to_label(image, lbl_pic, resize_label_fixed_h=True)
        
        lbl_text = QLabel(frame)
        lbl_text.setTextInteractionFlags(lbl_text.textInteractionFlags()|Qt.TextSelectableByMouse)
        font = lbl_text.font()
        font.setPointSize(12)
        lbl_text.setFont(font)
        lbl_text.setText(text)
        lbl_text.setStyleSheet("color: #aaff00; background-color: rgba(0, 0, 0, 0);")
        
        lbl_pic.move(w - lbl_pic.width() - 3, 5)
        lbl_text.move(0, 0)
        lbl_text.resize(w, h)

        return frame

    def _small_card_footer(self) -> QFrame:
        self.footer_frame = QFrame(self)
        self._define_frame(frame=self.footer_frame)
        head_style = f'background-color: {self.card_setting.get("footer_bg", "black")}; color: #ffff00;'
        self.footer_frame.setStyleSheet(head_style)
        font = self.footer_frame.font()
        self.footer_frame.resize(self.card_setting.get("width", 300), self.card_setting.get("footer_height", 40))

        # Data
        text = ""
        link = ""
        if self.card_setting.get("title", ""):
            text = self.card_setting.get("footer_text", "")
        else:
            text_code = self.html_parser.get_tags(html_code=self.html_code, tag="div", tag_class_contains="panel-footer", multiline=True)
            if text_code:
                self.html_parser.load_html_code(text_code[0])
                text = self.html_parser.get_raw_text()
                links = self.html_parser.get_all_links()
                if links:
                    link = links[0].a_href
        
        # Label
        self.lbl_footer = QLabel(self.footer_frame)
        self.lbl_footer.setTextInteractionFlags(self.lbl_footer.textInteractionFlags()|Qt.TextSelectableByMouse)
        self.lbl_footer.setWordWrap(True)
        self.lbl_footer.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        font.setPointSize(12)
        self.lbl_footer.setFont(font)
        if link:
            self.lbl_footer.setStyleSheet("QLabel {color: #ffff00;} QLabel:hover {color: #aaffff;}")
            feedback_function = self.card_setting["feedback"]
            self.lbl_footer.mousePressEvent = lambda _, link_val=link: feedback_function(link_val)
            self.lbl_footer.setCursor(Qt.PointingHandCursor)
        self.lbl_footer.setText(text)
        self.lbl_footer.move(0, 0)
        self.lbl_footer.resize(self.footer_frame.width(), self.footer_frame.height())

        return self.footer_frame

    def _create_small_poster(self):
        # Get data
        # Link
        link = ""
        self.html_parser.load_html_code(self.html_code)
        links = self.html_parser.get_all_links()
        if links:
            link = self.fix_url(links[0].a_href)
        # Image
        image = ""
        self.html_parser.load_html_code(self.html_code)
        image_code = self.html_parser.get_all_images()
        if image_code:
            image = self.fix_url(image_code[0].img_src)
        # Time
        time = ""
        time_code = self.html_parser.get_tags(html_code=self.html_code, tag="span", tag_class_contains="pull-left", multiline=True)
        if time_code:
            self.html_parser.load_html_code(time_code[0])
            time = self.html_parser.get_raw_text().strip()
            time = " " + time
        # Channel
        channel = ""
        channel_code = self.html_parser.get_tags(html_code=self.html_code, tag="span", tag_class_contains="pull-right", multiline=True)
        if channel_code:
            self.html_parser.load_html_code(channel_code[0])
            channel = self.html_parser.get_raw_text().strip()
            channel = " " + channel + " "
        # Movie name
        name = ""
        name_code = self.html_parser.remove_specific_tag(self.html_parser.crop_html_code(self.html_code), tag="div", multiline=True)
        self.html_parser.load_html_code(name_code)
        name = self.html_parser.get_raw_text().strip()
        
        # Set Widgets
        # self.layout = QGridLayout(self)
        font = self.font()
        font.setPointSize(12)

        if self.card_setting["width"]:
            w = self.card_setting["width"]
        else:
            w = 200
        pic_h = int(w * (220/150))
        self.resize(w, self.height())
        self.setStyleSheet("background-color: #aa0000; color: #ffffff;")

        # Image
        self.lbl_pic = QLabel(self)
        self.lbl_pic.setAlignment(Qt.AlignCenter)
        self.lbl_pic.setCursor(Qt.PointingHandCursor)
        self.lbl_pic.move(0, 3)
        self.lbl_pic.resize(w, pic_h)
        self.parent_widget.set_image_to_label(image, self.lbl_pic)
        y = self.lbl_pic.pos().y() + self.lbl_pic.height() + 2
    
        # Time
        self.lbl_time = QLabel(self)
        self.lbl_time.setTextInteractionFlags(self.lbl_time.textInteractionFlags()|Qt.TextSelectableByMouse)
        font.setBold(True)
        self.lbl_time.setFont(font)
        font.setBold(False)
        self.lbl_time.move(0, y)
        self.lbl_time.setText(time)
        self.lbl_time.adjustSize()

        # Channel
        self.lbl_ch = QLabel(self)
        self.lbl_ch.setTextInteractionFlags(self.lbl_ch.textInteractionFlags()|Qt.TextSelectableByMouse)
        self.lbl_ch.setFont(font)
        self.lbl_ch.setStyleSheet("background-color: #ffffff; color: #000000")
        self.lbl_ch.setText(channel)
        self.lbl_ch.adjustSize()
        self.lbl_ch.move(max(0, w - self.lbl_ch.width() - 2), y)

        y += max(self.lbl_time.height() + 5, self.lbl_ch.height() + 5)
        # Name
        self.lbl_name = QLabel(self)
        self.lbl_name.setTextInteractionFlags(self.lbl_name.textInteractionFlags()|Qt.TextSelectableByMouse)
        self.lbl_name.setCursor(Qt.PointingHandCursor)
        self.lbl_name.setFont(font)
        self.lbl_name.setStyleSheet("QLabel {color: #ffffff;} QLabel:hover {color: #aaffff;}")
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setText(name)
        self.lbl_name.adjustSize()
        self.lbl_name.move(0, y)
        self.lbl_name.resize(w, self.lbl_name.height())
        y += self.lbl_name.height() + 5

        self.resize(w, y)

        feedback_function = self.card_setting["feedback"]
        self.lbl_pic.mousePressEvent = lambda _, link_val=link: feedback_function(link_val)
        self.lbl_name.mousePressEvent = lambda _, link_val=link: feedback_function(link_val)

    def _define_frame(self, frame: QFrame = None):
        if frame is None:
            frame = self

        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(0)


class AladinTV(AbstractTopic):
    SPACING_HOR = 20
    SPACING_VER = 20
    SUPPORTED_SITES = [
        "https://tv.aladin.info",
        "https://tvprofil.com/",
        "https://www.cineplexx.rs/",
        "wikipedia.org/"
    ]

    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings) -> None:
        super().__init__(parent_widget, settings=settings)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("online_topic_aladin_tv_ui_file_path"), self)

        # Define variables
        self.name = "aladin_tv"
        self.topic_info_dict["name"] = self.name
        self.parent_widget = parent_widget
        self.title = self.getl("online_topic_aladin_tv_title")
        self.topic_info_dict["title"] = self.title
        self.link = None
        self.icon_path = self.getv("online_topic_aladin_tv_icon_path")
        self.icon_pixmap = QPixmap(self.icon_path)

        self.settings: dict = self._get_user_settings()
        self.active_page = None
        self.base_url = "https://tv.aladin.info"
        self.menu_items = []
        self.channel_items = []
        self.cards = {}

        self._define_widgets()

        # Connect events with slots
        self.lbl_title_pic.mouseDoubleClickEvent = self.lbl_title_pic_mouse_double_click
        self.lbl_chan.mousePressEvent = self.lbl_chan_mouse_press
        self.cmb_channel_item_style.currentTextChanged.connect(self.cmb_channel_item_style_text_changed)
        self.btn_search.clicked.connect(self.btn_search_click)
        self.txt_search.returnPressed.connect(self.btn_search_click)

        UTILS.LogHandler.add_log_record("#1: Topic frame loaded.", ["AladinTV"])

    def btn_search_click(self):
        if not self.txt_search.text().strip():
            return
        
        self.txt_search.setText(self.cirilica_u_latinicu(self.txt_search.text()))

        self.active_page = f"find:{self.txt_search.text()}"
        self.update_topic()

    def cmb_channel_item_style_text_changed(self, x):
        if not self.cmb_channel_item_style.currentData():
            return
        self._stt.set_setting_value("online_topic_aladain_tv_channel_item_display", self.cmb_channel_item_style.currentData())
        self._update_channel_item_style()

    def lbl_chan_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.frm_chan.raise_()
            self._arrange_frm_chan(columns=10)
            if self.frm_chan.isVisible():
                self.frm_chan.setVisible(False)
                self.cmb_channel_item_style.setVisible(False)
            else:
                self.frm_chan.setVisible(True)
                self.cmb_channel_item_style.setVisible(True)
            self.resize_me()

    def lbl_title_pic_mouse_double_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            site = self.lbl_title_pic.toolTip()
            webbrowser.open_new_tab(site)

    def _set_title_text(self, base_text: str = None, line2_text: str = None, line2_2_text: str = None):
        if base_text is None:
            base_text = self.getl("online_aladin_we_lbl_title_text")
        
        html_to_text = utility_cls.TextToHTML(base_text)

        result = base_text

        if line2_text:
            text = base_text + "\n" + line2_text
            html_rule = utility_cls.TextToHtmlRule(
                text=line2_text,
                fg_color="#59b385",
                font_size=18
            )
            html_to_text.set_text(text)
            html_to_text.add_rule(html_rule)
            result = html_to_text.get_html()

            if line2_2_text:
                if line2_2_text in line2_text:
                    text = f"{base_text}\n#1#2#3"
                    html_to_text.set_text(text)

                    pos = line2_text.find(line2_2_text)
                    part1 = line2_text[:pos]
                    part2 = line2_2_text
                    part3 = line2_text[pos+len(line2_2_text):]
                    html_to_text.delete_rule()
                    
                    html_rule1 = utility_cls.TextToHtmlRule(
                        text="#1",
                        replace_with=part1,
                        fg_color="#59b385",
                        font_size=18
                    )

                    html_rule2 = utility_cls.TextToHtmlRule(
                        text="#2",
                        replace_with=part2,
                        fg_color="#ffaa00",
                        font_size=18
                    )

                    html_rule3 = utility_cls.TextToHtmlRule(
                        text="#3",
                        replace_with=part3,
                        fg_color="#59b385",
                        font_size=18
                    )

                    html_to_text.add_rule(html_rule1)
                    html_to_text.add_rule(html_rule2)
                    html_to_text.add_rule(html_rule3)
                    result = html_to_text.get_html()
                else:
                    text = f"{base_text}\n#1 #2"
                    html_to_text.set_text(text)

                    part1 = line2_text.strip()
                    part2 = line2_2_text.strip()

                    html_rule1 = utility_cls.TextToHtmlRule(
                        text="#1",
                        replace_with=part1,
                        fg_color="#59b385",
                        font_size=18
                    )

                    html_rule2 = utility_cls.TextToHtmlRule(
                        text="#2",
                        replace_with=part2,
                        fg_color="#ffaa00",
                        font_size=18
                    )

                    html_to_text.add_rule(html_rule1)
                    html_to_text.add_rule(html_rule2)
                    result = html_to_text.get_html()

        self.lbl_title.setText(result)

    def _colorize_menu_buttons(self):
        for item in self.menu_items:
            if item.objectName() == self.active_page:
                item.setStyleSheet("QPushButton {color: #ffff00; background-color: #005500;} QPushButton:hover {background-color: #0000ca;}")
            else:
                item.setStyleSheet("QPushButton {color: #ffff00; background-color: #000062;} QPushButton:hover {background-color: #0000ca;}")

        for item in self.channel_items:
            item: ChannelMenuItem
            if item.url == self.active_page:
                item.set_active(True)
            else:
                item.set_active(False)

    def load_topic(self):
        QCoreApplication.processEvents()
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_aladin_tv") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

        self.setDisabled(True)
        QCoreApplication.processEvents()

        self._create_main_menu_frame()

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            self.setDisabled(False)
            return

        self.active_page = self.settings["start_page"]
        self.update_topic()
        UTILS.LogHandler.add_log_record("#1: Topic loaded.", ["AladinTV"])
        return super().load_topic()

    def update_topic(self):
        UTILS.LogHandler.add_log_record("#1: Topic update started.", ["AladinTV"])
        QCoreApplication.processEvents()
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_aladin_tv") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

        self.setDisabled(True)
        QCoreApplication.processEvents()

        # Load page
        description_page = self.is_description_page()
        page_url = ""
        if description_page:
            page_type = description_page[0]
            page_url = description_page[1]
        else:
            page_type = self._get_page_type()
            self._reset_content()
        self.prg_progress.setValue(0)
        self.prg_progress.setVisible(True)
        
        if page_type in ["home_page", "sadrzaj_filmova", "live"]:
            self._load_home_page()
        elif page_type in ["tv-program", "tv-film"]:
            self._load_channel_page(page_type=page_type)
        elif page_type in self.is_description_page(return_page_types=True):
            self._load_description_page(page_type=page_type, page_url=page_url)
        elif page_type == "find":
            self._load_find_movie_show_page(page_type=page_type)



        self.prg_progress.setVisible(False)
        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False

        self._colorize_menu_buttons()
        self.setDisabled(False)

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False
        self.resize_me()

        UTILS.LogHandler.add_log_record("#1: Topic update completed.", ["AladinTV"])

        return True

    def _get_search_results_for_active_page(self) -> list:
        search_string = self.active_page[self.active_page.find(":") + 1:].strip()
        search_results = self.get_search_results(query_string=search_string)
        remove_items = []
        for idx, item in enumerate(search_results):
            if item["link"].endswith("-"):
                remove_items.append(idx)
        remove_items.sort(reverse=True)
        for idx in remove_items:
            search_results.pop(idx)
        return search_results

    def _load_find_movie_show_page(self, page_type: str) -> bool:
        if not page_type.startswith("find"):
            return False
        
        search_results = self._get_search_results_for_active_page()

        # Delete old cards
        self._reset_content()
        
        self.resize_me()
        self.frm_content.setVisible(True)

        # Define page settings
        card_settings = self.CARD_SETTINGS()
        card_settings["width"] = self.frm_content.contentsRect().width()
        card_settings["supported"] = self.SUPPORTED_SITES
        card_settings["search_string"] = self.active_page[self.active_page.find(":") + 1:].strip()

        # Create Card
        page_type = "find"
        item = Card(self.frm_content, self._stt, search_results, page_type, card_setting=card_settings)

        # Move Card to position
        card_id = self._get_next_card_id()
        item.move(0, 0)
        item.show()

        # Add card
        self.cards[card_id] = {}
        self.cards[card_id]["html"] = ""
        self.cards[card_id]["type"] = page_type
        self.cards[card_id]["obj"] = item
        self.cards[card_id]["settings"] = card_settings
        self.cards[card_id]["name"] = ""

        return True

    def _load_description_page(self, page_type: str, page_url: str) -> bool:
        if page_type not in ["search_movie", "search_title"]:
            result = self._load_project(url=page_url)
            if not result:
                return False

        # Delete old cards
        if len(self.cards) == 1:
            if "1" not in self.cards.keys() or self.cards["1"]["obj"].card_type == "find":
                self._reset_content()
            else:
                if self.cards["1"]["obj"].card_type not in ["tv-program", "tv-film"]:
                    self._reset_content()
        elif len(self.cards) == 2:
            if not self.cards["1"] or not self.cards["2"]:
                self._reset_content()
            else:
                self.cards["2"]["obj"].setVisible(False)
                self.cards["2"]["obj"].deleteLater()
                self.cards.pop("2")
        else:
            self._reset_content()

        self.resize_me()
        self.frm_content.setVisible(True)

        # Get page code
        if page_type in ["search_movie", "search_title"]:
            page_code = self._get_search_results_for_active_page()
        else:
            page_code = self.rashomon.get_segment_selection("page")

        # Define page settings
        card_settings = self.CARD_SETTINGS()
        if len(self.cards) == 1:
            w = self.frm_content.contentsRect().width() - self.cards["1"]["obj"].width() - 20
        else:
            w = self.frm_content.contentsRect().width() - 20
        if w < 400:
            w = 400
        if len(self.cards) == 1:
            card_settings["width"] = w
        else:
            card_settings["width"] = self.frm_content.contentsRect().width()
        card_settings["banner_height"] = 200
        if page_type == "selector":
            card_settings["image_width"] = 400
        else:
            card_settings["image_width"] = 300
        card_settings["supported"] = self.SUPPORTED_SITES
        card_settings["search_string"] = self.active_page[self.active_page.find(":") + 1:].strip()
        card_settings["size_changed_feedback"] = self.feedback_size_changed_function

        # Create Card
        card_id = self._get_next_card_id()
        item = Card(self.frm_content, self._stt, page_code, page_type, card_setting=card_settings)

        # Move Card to position
        x = 0
        if len(self.cards) == 1:
            self.cards["1"]["obj"].move(0, 0)
            x = self.cards["1"]["obj"].width() + 20
        item.move(x, 0)
        item.show()

        # Add card
        self.cards[card_id] = {}
        self.cards[card_id]["html"] = page_code
        self.cards[card_id]["type"] = page_type
        self.cards[card_id]["obj"] = item
        self.cards[card_id]["settings"] = card_settings
        self.cards[card_id]["name"] = ""

        return True
    
    def is_description_page(self, url: str = None, return_page_types: bool = False) -> str:
        if return_page_types:
            result = [
                "search_movie",
                "search_title",
                "selector",
                "movie",
                "https://tvprofil.com/film",
                "https://tvprofil.com/serije",
                "https://www.cineplexx.rs",
                "wikipedia"
            ]
            return result
        
        def is_movie(text: str) -> str:
            if not text.startswith('https://tv.aladin.info/'):
                return None
            text = text[len('https://tv.aladin.info/'):]
            pos = text.find("-")
            if pos == -1:
                return None
            text = text[:pos]
            if text:
                return text
            
        if not url:
            url = self.active_page
        if not url:
            return None
        
        result = None
        if url.startswith("#search_movie:"):
            return ("search_movie", url[url.find(":")+1:])
        elif url.startswith("#search_title:"):
            return ("search_title", url[url.find(":")+1:])
        elif "?selector=" in url:
            return ("selector", url)
        elif self._get_integer(is_movie(url)):
            return ("movie", url)
        elif url.startswith("https://tvprofil.com/") and "/film/" in url:
            return ("https://tvprofil.com/film", url)
        elif url.startswith("https://tvprofil.com/"):
            return ("https://tvprofil.com/serije", url)
        elif url.startswith("https://www.cineplexx.rs"):
            return ("https://www.cineplexx.rs", url)
        elif "wikipedia.org/" in url:
            return ("wikipedia", url)

    def _load_channel_page(self, page_type: str = "tv-program") -> bool:
        result = self._load_project()
        if not result:
            return False

        self.resize_me()
        self.frm_content.setVisible(True)

        tv_code = self.rashomon.get_segment_selection("page")
        
        tv_items_code = self.html_parser.get_tags(html_code=tv_code, tag="table", multiline=True)
        if not tv_items_code:
            return False

        footer_text = ""
        text_code = self.html_parser.get_tags(html_code=tv_code, tag="title", custom_tag_property=[["itemprop", "name"]], multiline=True)
        if text_code:
            self.html_parser.load_html_code(text_code[0])
            footer_text = self.html_parser.get_raw_text().strip()

        title = ""
        name_code = self.html_parser.get_tags(html_code=tv_code, tag="h1", multiline=True)
        if name_code:
            self.html_parser.load_html_code(name_code[0])
            title = self.html_parser.get_raw_text().strip()

        card_settings = self.CARD_SETTINGS()
        if page_type == "tv-program":
            card_settings["width"] = 600
        elif page_type == "tv-film":
            card_settings["width"] = 600
            card_settings["item_ext_width"] = 200
        card_settings["header_height"] = 40
        card_settings["footer_height"] = 35
        card_settings["item_height"] = 30
        card_settings["header_bg"] = "#764e3b"
        card_settings["body_bg"] = "#3b261d"
        card_settings["body_now_bg"] = "#593a2c"
        card_settings["footer_bg"] = "#3b261d"
        card_settings["title"] = title
        card_settings["footer_text"] = footer_text

        total_items = len(tv_items_code)
        current_item = 0
        for idx, item_code in enumerate(tv_items_code):
            item = Card(self.frm_content, self._stt, item_code, page_type, card_setting=card_settings)
            
            card_id = self._get_next_card_id()

            if idx == 0:
                item.move(self._get_next_card_position(item, force_next_row=True, center_hor=True))
            else:
                item.move(self._get_next_card_position(item, center_hor=True))
            
            self.cards[card_id] = {}
            self.cards[card_id]["html"] = item_code
            self.cards[card_id]["type"] = page_type
            self.cards[card_id]["obj"] = item
            self.cards[card_id]["settings"] = card_settings
            self.cards[card_id]["name"] = ""

            item.show()
            self.frm_content.resize(self.frm_content.width(), self._get_next_y(return_cards_y=True))
            current_item += 1
            self.prg_progress.setValue(int(current_item*100/total_items))
            QCoreApplication.processEvents()

            if self.stop_loading:
                return False

        return True

    def _load_home_page(self) -> bool:
        result = self._load_project()
        if not result:
            return False

        # Load posters
        posters_code = self.rashomon.get_segment_selection("page")
        posters_code = self.html_parser.get_tags(html_code=posters_code, tag="div", tag_class_contains="row pt10", multiline=True)
        if not posters_code:
            return False
        
        poster_items_code = self.html_parser.get_tags(html_code=posters_code[0], tag="div", tag_class_contains="pb10 tv_ads", multiline=True)
        card_settings = self.CARD_SETTINGS()
        card_settings["width"] = 200

        self.resize_me()
        self.frm_content.setVisible(True)

        if poster_items_code:
            total_items = len(poster_items_code)
            current_item = 0
            for item_code in poster_items_code:
                item = Card(self.frm_content, self._stt, item_code, "small_poster", card_setting=card_settings)
                
                card_id = self._get_next_card_id()

                item.move(self._get_next_card_position(item))
                
                self.cards[card_id] = {}
                self.cards[card_id]["html"] = item_code
                self.cards[card_id]["type"] = "small_poster"
                self.cards[card_id]["obj"] = item
                self.cards[card_id]["settings"] = card_settings
                self.cards[card_id]["name"] = ""

                item.show()
                self.frm_content.resize(self.frm_content.width(), self._get_next_y(return_cards_y=True))
                current_item += 1
                self.prg_progress.setValue(int(current_item*100/total_items))
                QCoreApplication.processEvents()

                if self.stop_loading:
                    return False

        # Currently on TV
        tv_code = self.rashomon.get_segment_selection("page")
        
        tv_items_code = self.html_parser.get_tags(html_code=tv_code, tag="div", tag_class_contains="panel panel-default", multiline=True)
        if not tv_items_code:
            return True

        card_settings = self.CARD_SETTINGS()
        card_settings["width"] = 400
        card_settings["header_height"] = 40
        card_settings["footer_height"] = 35
        card_settings["item_height"] = 30
        card_settings["header_bg"] = "#764e3b"
        card_settings["body_bg"] = "#3b261d"
        card_settings["body_now_bg"] = "#593a2c"
        card_settings["footer_bg"] = "#3b261d"

        total_items = len(tv_items_code)
        current_item = 0
        for idx, item_code in enumerate(tv_items_code):
            item = Card(self.frm_content, self._stt, item_code, "tv_small", card_setting=card_settings)
            
            card_id = self._get_next_card_id()

            if idx == 0:
                item.move(self._get_next_card_position(item, force_next_row=True))
            else:
                item.move(self._get_next_card_position(item))
            
            self.cards[card_id] = {}
            self.cards[card_id]["html"] = item_code
            self.cards[card_id]["type"] = "tv_small"
            self.cards[card_id]["obj"] = item
            self.cards[card_id]["settings"] = card_settings
            self.cards[card_id]["name"] = ""

            item.show()
            self.frm_content.resize(self.frm_content.width(), self._get_next_y(return_cards_y=True))
            current_item += 1
            self.prg_progress.setValue(int(current_item*100/total_items))
            QCoreApplication.processEvents()

            if self.stop_loading:
                return False

        return True
        
    def _get_next_card_position(self, card_obj: Card, force_next_row: bool = False, center_hor: bool = False) -> QPoint:
        if force_next_row:
            x = 0
            if center_hor:
                x = int((self.frm_content.width() - card_obj.width()) / 2)
            return QPoint(x, self._get_next_y(return_cards_y=True))
        
        x = 0
        y = 0
        last_item = None
        for item_id in self.cards:
            item: Card = self.cards[item_id]["obj"]

            if not item.isVisible():
                continue
            last_item = item

        if not last_item:
            return QPoint(x, y)
        
        next_x = last_item.pos().x() + last_item.width() + self.SPACING_HOR
        if next_x + card_obj.width() <= self.frm_content.contentsRect().width():
            x = next_x
            if center_hor:
                x = int(((self.frm_content.width() - next_x) - card_obj.width) / 2 + next_x)
            y = last_item.pos().y()
            return QPoint(x, y)
        else:
            x = 0
            if center_hor:
                x = int((self.frm_content.width() - card_obj.width()) / 2)
            y = self._get_next_y(return_cards_y=True)
            return QPoint(x, y)

    def _get_page_type(self, url: str = None) -> str:
        if not url:
            url = self.active_page
        
        if not url:
            return None
        
        if url.lower().strip(" /") == "https://tv.aladin.info":
            return "home_page"
        elif url.lower().strip(" /") == "https://tv.aladin.info/film":
            return "sadrzaj_filmova"
        elif url.lower().strip(" /") == "https://tv.aladin.info/live":
            return "live"
        elif url.lower().strip(" /").startswith("https://tv.aladin.info/tv-program"):
            return "tv-program"
        elif url.lower().strip(" /").startswith("https://tv.aladin.info/tv-film"):
            return "tv-film"
        elif url.lower().startswith("find:"):
            return "find"

    def _get_next_card_id(self) -> str:
        next_id = 0
        for i in self.cards:
            next_id = max(int(i), next_id)
        next_id += 1
        return str(next_id)

    def _reset_content(self):
        self.frm_chan.setVisible(False)
        self.frm_content.setVisible(False)
        
        for item in self.cards:
            self.cards[item]["obj"].setVisible(False)
            self.cards[item]["obj"].deleteLater()
        for i in [x for x in self.cards]:
            self.cards.pop(i)

    def _create_main_menu_frame(self) -> bool:
        source = self.fix_url("/")
        result = self._load_project(url=source)
        if not result:
            return False
        
        # Delete old menu items
        for item in self.menu_items:
            item.setVisible(False)
            item.deleteLater()
        self.menu_items = []
        self.channel_items = []

        # Create new menu items
        menu_code = self.rashomon.get_segment_selection("page")
        if menu_code:
            menu_code = self.html_parser.get_tags(html_code=menu_code, tag="div", custom_tag_property=[["class", "navbar-collapse collapse"], ["id", "inverse-navbar"]], multiline=True)
            if menu_code:
                menu_code = menu_code[0]
            else:
                return False
        else:
            return False
        
        channels_menu_code = self.html_parser.get_tags(html_code=menu_code, tag="ul", tag_class_contains="dropdown-menu", multiline=True)
        if channels_menu_code:
            channels_menu_code = channels_menu_code[0]
        else:
            return False

        menu_code = self.html_parser.crop_html_code(menu_code, starting_lines=2, ending_lines=2)
        menu_code = self.html_parser.remove_specific_tag(html_code=menu_code, tag="ul", multiline=True)
                
        menu_items_segments = self.html_parser.get_tags(html_code=menu_code, tag="li", multiline=True)

        x = 0
        w = 0
        h = 0
        for menu_item_code in menu_items_segments:
            # menu_item_code = self.rashomon.get_segment_selection(menu_item_segment)
            self.html_parser.load_html_code(menu_item_code)
            # Link
            links = self.html_parser.get_all_links()
            if links:
                if links[0].a_href == "#":
                    continue
                link = self.fix_url(links[0].a_href)
            else:
                continue
            # Text
            text = self.html_parser.get_raw_text().strip()
            # Create menu item
            btn_menu_item = QPushButton(self.frm_menu)
            font = btn_menu_item.font()
            font.setPointSize(14)
            font.setBold(True)
            btn_menu_item.setFont(font)
            btn_menu_item.setStyleSheet("QPushButton {color: #ffff00; background-color: #000062;} QPushButton:hover {background-color: #0000ca;}")
            btn_menu_item.setText(text)
            btn_menu_item.clicked.connect(lambda _, link_val=link: self.feedback_click_function(link_val))
            btn_menu_item.adjustSize()
            btn_menu_item.setObjectName(link)
            btn_menu_item.move(x, 0)
            self.menu_items.append(btn_menu_item)
            x += btn_menu_item.width() + 10

            h = max(h, btn_menu_item.height())
            w = x - 10

        # Show menu frame
        self.frm_menu.move(10, self._get_next_y())
        self.frm_menu.resize(w, h)
        self.frm_menu.setVisible(True)
        self.frm_menu.show()
        QCoreApplication.processEvents()

        self.frm_menu.setVisible(True)
        self.line_content.setVisible(True)

        result = self._create_channel_menu(ch_menu_code=channels_menu_code, columns=10)

        return result

    def _create_channel_menu(self, ch_menu_code: str, columns: int = 2) -> bool:
        ch_code_list = self.html_parser.get_tags(html_code=ch_menu_code, tag="li", multiline=True)

        # Add items to list
        for menu_item_code in ch_code_list:
            self.html_parser.load_html_code(menu_item_code)
            # Link
            links = self.html_parser.get_all_links()
            if links:
                if links[0].a_href == "#":
                    continue
                link = self.fix_url(links[0].a_href)
            else:
                continue
            # Text
            text = self.html_parser.get_raw_text().strip()
            
            item = ChannelMenuItem(self.frm_chan, self._stt, url=link, title=text)
            item.btn.clicked.connect(lambda _, link_val=link: self.feedback_click_function(link_val))
            item.lbl_pic.mousePressEvent = lambda _, link_val=link: self.feedback_click_function(link_val)
            self.channel_items.append(item)
        self._arrange_frm_chan(columns=columns)

    def _update_channel_item_style(self):
        for item in self.channel_items:
            item: ChannelMenuItem
            item.recreate_item()
        self._arrange_frm_chan(columns=10)
    
    def _arrange_frm_chan(self, columns: int):
        # Set items position
        x_spacing = 10
        y_spacing = 5
        max_w = 0
        max_h = 0
        for item in self.channel_items:
            item: ChannelMenuItem
            max_w = max(max_w, item.width())
            max_h = max(max_h, item.height())
        
        while True:
            if max_w * columns + (columns - 1) * x_spacing > self.contentsRect().width() - 20:
                columns -= 1
            else:
                break
            if columns < 1:
                columns = 1
                break    
            
        x = 0
        y = 0
        row = 1
        max_rows = int(len(self.channel_items) / columns)
        if max_rows < 1:
            max_rows = 1
        
        for item in self.channel_items:
            item: ChannelMenuItem
            item.move(x, y)
            
            y += max_h + y_spacing
            
            row += 1
            if row > max_rows:
                x += max_w + x_spacing
                y = 0
                row = 1
            
        w = max_w * columns + (columns - 1) * x_spacing
        h = max_h * max_rows + (max_rows - 1) * y_spacing
        self.frm_chan.resize(w, h)

    def _load_project(self, url: str = None) -> bool:
        if url is None:
            url = self.active_page
        
        if not url:
            return False
        
        if self.rashomon.get_source() == url:
            return True
        
        self.rashomon.clear_errors()
        project_name = self.getv("rashomon_folder_path") + "aladin_tv.rpf"
        result = self.rashomon.load_project(project_filename=project_name, change_source=url)
        if self.rashomon.errors() or not result:
            return False

        self.rashomon.set_compatible_mode(True)

        result = self.rashomon.recreate_segment_tree()
        if self.rashomon.errors() or not result:
            return False

        return result

    def _get_next_y(self, return_cards_y: bool = False):
        y = self.frm_search.pos().y() + self.frm_search.height() + 20
        if self.line_menu.isVisible():
            y = self.line_menu.pos().y() + self.line_menu.height() + 5

        if self.frm_menu and self.frm_menu.isVisible():
            y = self.frm_menu.pos().y() + self.frm_menu.height() + 10

        if self.line_content.isVisible():
            y = self.line_content.pos().y() + self.line_content.height() + 5

        if self.frm_chan.isVisible():
            y = self.frm_chan.pos().y() + self.frm_chan.height() + 5

        if return_cards_y:
            y = 0
            for i in self.cards:
                if self.cards[i]["obj"] and self.cards[i]["obj"].isVisible():
                    y = max(y, self.cards[i]["obj"].pos().y() + self.cards[i]["obj"].height() + self.SPACING_VER)
            return y

        return y

    def feedback_click_function(self, data: dict):
        self.frm_chan.setVisible(False)
        self.cmb_channel_item_style.setVisible(False)
        if isinstance(data, str):
            if not data:
                return
            self.active_page = data
            self.update_topic()
        else:
            if data["url"]:
                if not data["url"]:
                    return
                self.active_page = data["url"]
                self.update_topic()

    def feedback_size_changed_function(self, size: QSize):
        self.resize_me()

    def _get_user_settings(self) -> dict:
        result = {
            "start_page": None,
            "search_text": ""
            }

        if "online_topic_aladin_tv_settings" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("online_topic_aladin_tv_settings")
            
            result["start_page"] = g.get("start_page", None)
            self.active_page = result["start_page"]

            result["search_text"] = g.get("search_text", "")
            self.txt_search.setText(result["search_text"])
        
        return result

    def _update_user_settings(self) -> None:
        if "online_topic_aladin_tv_settings" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("online_topic_aladin_tv_settings", self.settings, save_to_file=True)

        self.settings["start_page"] = self.active_page
        self.settings["search_text"] = self.txt_search.text()

        self.set_appv("online_topic_aladin_tv_settings", self.settings)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resize_me()
        return super().resizeEvent(a0)
    
    def resize_me(self, size: QSize = None):
        w = self.contentsRect().width()
        w_title = max(w - self.lbl_title.pos().x() - 10, 100)

        self.lbl_title.resize(w_title, self.lbl_title.height())
        self.line_title.resize(w - 10 - self.line_title.pos().x(), self.line_title.height())
        self.line_menu.resize(w - 10 - self.line_menu.pos().x(), self.line_menu.height())
        self.line_content.resize(w - 10 - self.line_content.pos().x(), self.line_content.height())

        self.frm_content.move(10, self._get_next_y())
        self.frm_content.resize(w - 20, self._get_next_y(return_cards_y=True))
        
        self.setFixedHeight(max(self._get_next_y(), self.parent_widget.get_topic_area_size().height(), self.frm_chan.pos().y() + self.frm_chan.height(), self.frm_content.pos().y() + self.frm_content.height()))

    def _define_widgets(self):
        self.lbl_title_pic: QLabel = self.findChild(QLabel, "lbl_title_pic")
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.line_title: QFrame = self.findChild(QFrame, "line_title")
        self.line_menu: QFrame = self.findChild(QFrame, "line_menu")
        self.line_content: QFrame = self.findChild(QFrame, "line_content")
        
        self.frm_search: QFrame = self.findChild(QFrame, "frm_search")
        self.lbl_search: QLabel = self.findChild(QLabel, "lbl_search")
        self.txt_search: QLineEdit = self.findChild(QLineEdit, "txt_search")
        self.btn_search: QPushButton = self.findChild(QPushButton, "btn_search")
        self.cmb_channel_item_style: QComboBox = self.findChild(QComboBox, "cmb_channel_item_style")

        self.frm_menu: QFrame = self.findChild(QFrame, "frm_menu")

        self.frm_chan: QFrame = self.findChild(QFrame, "frm_chan")
        self.lbl_chan: QLabel = self.findChild(QLabel, "lbl_chan")

        self.frm_content: QFrame = self.findChild(QFrame, "frm_content")
        self.prg_progress: QProgressBar = self.findChild(QProgressBar, "prg_progress")

        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        self.lbl_title.setText(self.getl("online_aladin_tv_lbl_title_text"))
        self.lbl_search.setText(self.getl("online_aladin_tv_lbl_search_text"))
        self.lbl_chan.setText(self.getl("online_aladin_tv_lbl_chan_text"))

        self.frm_menu.setVisible(False)
        self.line_content.setVisible(False)
        self.frm_chan.setVisible(False)

        channel_style = [
            [self.getl("online_topic_aladin_tv_channel_style_1_text"), 1],
            [self.getl("online_topic_aladin_tv_channel_style_2_text"), 2],
            [self.getl("online_topic_aladin_tv_channel_style_3_text"), 3]
        ]
        for i in channel_style:
            self.cmb_channel_item_style.addItem(i[0], i[1])
        
        self.cmb_channel_item_style.setCurrentIndex(self.getv("online_topic_aladain_tv_channel_item_display") - 1)
        self.cmb_channel_item_style.setVisible(False)

        self.frm_content.setVisible(False)
        self.prg_progress.setVisible(False)

    def CARD_SETTINGS(self) -> dict:
        result = {
            "feedback": self.feedback_click_function,
            "width": 0,
            "height": 0,
            "has_border": False
        }
        return result



