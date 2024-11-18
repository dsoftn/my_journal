from PyQt5.QtWidgets import QFrame, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QSizePolicy, QGridLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QMouseEvent, QResizeEvent
from PyQt5.QtCore import QSize, Qt, QCoreApplication
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView

import webbrowser
import folium

import settings_cls
import utility_cls
import html_parser_cls
from online_abstract_topic import AbstractTopic
import UTILS


class Table(QFrame):
    def __init__(self, parent_widget: AbstractTopic, settings: settings_cls.Settings, table_data: dict):
        """
        table_data: [title]= "" - str: Table title
                    [max_width]= None - int: Max width of table
                    [max_height]=None - int: Max height of table
                    [border]= False - bool: Frame has border
                    [feedback_link_click_function]= None - function: Function to call on link click
                    [frame_obj]= self
                    [item_image_width]= None - int: Width of images in items
                    [item_image_height]= None = int: Height of images in items
                    [item_image_scale]= "h" = str (w, h) Fixed width, height 
                    [items] - dict: Dictionary of dicts with item data
                            [text] - str: Item text
                            [link] - str: Item link
                            [text_slices] - list: List of text slices to style differently
                            [image] - str: Item image
                            [frm_item]: QFrame
                            [lbl_item_text]: QLabel
                            [lbl_item_pic]: QLabel

        """
        super().__init__(parent_widget)
        self._stt = settings
        # Define settings object and methods
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.data = table_data
        self.html_parser = html_parser_cls.HtmlParser()

        if isinstance(table_data["items"], str):
            self._populate_items()

        self._create_table()

    def _populate_items(self):
        # Title
        html = self.data["items"]
        title_code = self.html_parser.get_tags(html_code=html, tag="h4", multiline=True)
        title = ""
        if title_code:
            self.html_parser.load_html_code(title_code[0])
            title = self.html_parser.get_raw_text()

        self.data["title"] = title

        # Items
        items_code_list = self.html_parser.get_tags(html_code=html, tag="li", multiline=True)

        count = 1
        self.data["items"] = {}
        for item_code in items_code_list:
            self.html_parser.load_html_code(item_code)
            images = self.html_parser.get_all_images()
            image = ""
            if images:
                image = images[0].img_src
            text = self.html_parser.get_raw_text()
            text_slices = self.html_parser.get_all_text_slices()
            for i in text_slices:
                i.txt_link = self.parent_widget.fix_url(i.txt_link)
            links = self.html_parser.get_all_links()
            link = ""
            if links:
                link = self.parent_widget.fix_url(links[0].a_href)
            
            self.data["items"][str(count)] = {}
            self.data["items"][str(count)]["text"] = text
            self.data["items"][str(count)]["text_slices"] = text_slices
            self.data["items"][str(count)]["image"] = self.parent_widget.fix_url(image)
            self.data["items"][str(count)]["link"] = self.parent_widget.fix_url(link)

            count += 1

    def empty_table_dict() -> dict:
        result = {
            "title": "",
            "max_width": 0,
            "max_height": 0,
            "border": False,
            "feedback_link_click_function": None,
            "frame_obj": None,
            "item_image_width": None,
            "item_image_height": None,
            "item_image_scale": "h",
            "items": {}
        }
        return result

    def _create_table(self):
        # Create frame with title and list of items
        self.setFrameShadow(QFrame.Plain)
        if self.data["border"]:
            self.setFrameShape(QFrame.Box)
        else:
            self.setFrameShape(QFrame.NoFrame)
        self.data["frame_obj"] = self

        # Title
        self.lbl_title = QLabel(self)
        self.lbl_title.setText(self.data["title"])
        self.lbl_title.setStyleSheet("color: #00ff00;")
        font = self.lbl_title.font()
        font.setPointSize(16)
        self.lbl_title.setFont(font)
        self.lbl_title.move(1, 1)
        self.lbl_title.adjustSize()
        y = self.lbl_title.height() + 10

        # QScrollArea for items
        self.area = QScrollArea(self)
        self.area.setFrameShadow(QFrame.Plain)
        self.area.setFrameShape(QFrame.NoFrame)
        self.area_widget = QWidget()
        self.area_widget_layout = QGridLayout()
        # spacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.area_widget_layout.addItem(spacer)
        self.area_widget.setLayout(self.area_widget_layout)
        self.area.setWidget(self.area_widget)
        self.area.setContentsMargins(0, 0, 0, 0)
        self.area.setViewportMargins(0, 0, 0, 0)
        self.area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.area_widget.setContentsMargins(0, 0, 0, 0)
        self.area_widget_layout.setSpacing(10)
        self.area.move(10, y)

        # Create list of items
        items_h = 0
        items_w = 0
        def_image = self.getv("item_icon_path")
        for item in self.data["items"]:
            frm_item = QFrame(self.area_widget)
            frm_item.setFrameShadow(QFrame.Plain)
            frm_item.setFrameShape(QFrame.NoFrame)
            
            lbl_item_pic = QLabel(frm_item)
            lbl_item_pic.setAlignment(Qt.AlignCenter)
            lbl_item_pic.move(0, 0)
            image = self.data["items"][item]["image"]
            if not image:
                image = def_image
            if self.data["item_image_width"]:
                lbl_pic_w = self.data["item_image_width"]
            else:
                lbl_pic_w = 30
            if self.data["item_image_height"]:
                lbl_pic_h = self.data["item_image_height"]
            else:
                lbl_pic_h = 30
            lbl_item_pic.resize(lbl_pic_w, lbl_pic_h)
            if self.data["item_image_scale"].lower() == "w":
                self.parent_widget.set_image_to_label(image, lbl_item_pic, resize_label_fixed_w=lbl_pic_w)
            else:
                self.parent_widget.set_image_to_label(image, lbl_item_pic, resize_label_fixed_h=lbl_pic_h)
            
            lbl_item_text = QLabel(frm_item)
            lbl_item_text.setStyleSheet("QLabel::hover {background-color: #0055ff}")
            lbl_item_text.resize(1000, 25)
            font = lbl_item_text.font()
            font.setPointSize(12)
            lbl_item_text.setFont(font)
            lbl_item_text.setFixedHeight(lbl_item_pic.height())
            # lbl_item_text.setWordWrap(True)
            lbl_item_text.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self._set_text_to_label(self.data["items"][item]["text_slices"], lbl_item_text)
            lbl_item_text.setObjectName(self.data["items"][item].get("link", ""))
            lbl_item_text.move(lbl_item_pic.width() + 5, 0)
            lbl_item_text.adjustSize()
            lbl_item_text.resize(lbl_item_text.width() + 5, lbl_item_text.height())
            items_h = max(items_h, lbl_item_text.height(), lbl_item_pic.height())
            items_w = max(items_w, lbl_item_pic.width() + lbl_item_text.width() + 10)
            
            self.data["items"][item]["frm_item"] = frm_item
            self.data["items"][item]["lbl_item_text"] = lbl_item_text
            self.data["items"][item]["lbl_item_pic"] = lbl_item_pic

        # Add items to layout
        if not self.data["max_width"]:
            max_width = items_w * 3 + 10 + self.area_widget_layout.spacing() * 2
        else:
            max_width = self.data["max_width"] - 10

        if max_width < 0:
            max_width = 100
        
        columns = int(max_width / (items_w + self.area_widget_layout.spacing()))
        if columns < 1:
            columns = 1
        
        col = 0
        row = 0
        for item_key in self.data["items"]:
            item = self.data["items"][item_key]
            item["frm_item"].setFixedSize(items_w, items_h)
            item["lbl_item_text"].linkActivated.connect(self._url_click)
            item["lbl_item_text"].mousePressEvent = self._item_text_click
            item["lbl_item_pic"].mousePressEvent = self._item_image_click
            self.area_widget_layout.addWidget(item["frm_item"], row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1
        if col == 0:
            row -= 1

        self.area_widget.resize(items_w * columns + self.area_widget_layout.spacing() * (columns-1), (row + 1) * items_h + self.area_widget_layout.spacing() * (row))
        if self.data["max_height"]:
            area_h = self.data["max_height"]
        else:
            area_h = self.area_widget.height()
        self.area.resize(max_width, area_h + 5)

        self.resize(max(self.lbl_title.width() + 2, self.area.width() + 12), self.lbl_title.height() + self.area.height() + 12)

    def _url_click(self, url: str):
        data = {
            "type": "link",
            "url": url
        }
        if self.data["feedback_link_click_function"]:
            self.data["feedback_link_click_function"](data)

    def _item_text_click(self, e: QMouseEvent):
        url = ""
        if self.sender():
            url = self.sender().objectName()
        data = {
            "type": "widget_text",
            "url": url,
            "event": e
        }
        if self.data["feedback_link_click_function"]:
            self.data["feedback_link_click_function"](data)

    def _item_image_click(self, e: QMouseEvent):
        data = {
            "type": "widget_pic",
            "event": e
        }
        if self.data["feedback_link_click_function"]:
            self.data["feedback_link_click_function"](data)

    def _set_text_to_label(self, text_slices: list, label: QLabel):
        text_to_html = utility_cls.TextToHTML()
        text_to_html.general_rule.fg_color = "#aaff7f"
        text = ""
        for idx, txt_slice in enumerate(text_slices):
            txt_slice: html_parser_cls.TextObject
            text_id = "#" + "-" * (6 - len(str(idx))) + str(idx) + ";"
            html_rule = utility_cls.TextToHtmlRule(text=text_id, replace_with=txt_slice.txt_value)
            if txt_slice.txt_link:
                html_rule.font_underline = True
                html_rule.fg_color = "#55ffff"
                html_rule.link_href = txt_slice.txt_link
            if txt_slice.txt_strong:
                html_rule.fg_color = "#e2ffcb"
                html_rule.font_bold = True

            text_to_html.add_rule(html_rule)
            text += text_id

        text_to_html.set_text(text)
        label.setText(text_to_html.get_html())
        return True


class Card(QFrame):
    def __init__(self, parent_widget: AbstractTopic, settings: settings_cls.Settings, card_html: str, card_type: str, frame_setting: dict = None):
        super().__init__(parent_widget)
        self._stt = settings
        # Define settings object and methods
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.card_html = card_html
        self.card_type = card_type
        if frame_setting:
            self.frame_setting = frame_setting
        else:
            self.frame_setting = {}

        self.html_parser = html_parser_cls.HtmlParser()

        if self.card_type == "info":
            self._create_card_type_info()
        elif self.card_type == "geo":
            self._create_card_type_geo()
        elif self.card_type == "climate":
            self._create_card_type_climate()

    def _create_frames_type_info(self) -> list:
        frames_list = []
        # Get Cards
        cards_code_list = self.html_parser.get_tags(html_code=self.card_html, tag="div", tag_class_contains="row px-3", multiline=True)
        if not cards_code_list:
            cards_code_list = [self.card_html]
        
        for card_code_html in cards_code_list:
            # Image
            self.html_parser.load_html_code(card_code_html)
            images = self.html_parser.get_all_images()
            image = ""
            if images:
                image = self.parent_widget.fix_url(images[0].img_src)
            # Left side text
            l_text = ""
            if len(cards_code_list) == 1:
                l_text_code = self.html_parser.get_tags(html_code=card_code_html, tag="div", tag_class_contains="mt-2 small", multiline=True)
                if l_text_code:
                    self.html_parser.load_html_code(l_text_code[0])
                    l_text_slices = self.html_parser.get_all_text_slices()
                    if len(l_text_slices) == 2:
                        if len(l_text_slices[1].txt_value.splitlines()) == 2:
                            time_mark = l_text_slices[1].txt_value.splitlines()[1]
                            l_text_slices[1].txt_value = l_text_slices[1].txt_value.splitlines()[0]

                        l_text = "Sunce izlazi\n"
                        l_text += "🌞 " + l_text_slices[0].txt_value + " " + time_mark + "\n"
                        l_text += "Sunce zalazi\n"
                        l_text += "🌓 " + l_text_slices[1].txt_value + " " + time_mark
                    else:
                        for i in l_text_slices:
                            l_text += i.txt_value + "\n"
                        l_text = l_text.strip()
            else:
                l_text_code = self.html_parser.get_tags(html_code=card_code_html, tag="div", tag_class_contains="col-4 text-sm-center lh-sm", multiline=True)
                if not l_text_code:
                    l_text_code = self.html_parser.get_tags(html_code=card_code_html, tag="span", tag_class_contains="d-block fw-bold", multiline=True)
                if l_text_code:
                    self.html_parser.load_html_code(l_text_code[0])
                    l_text = "🕑 " + self.html_parser.get_raw_text()
            # Middle text
            m_text_main = ""
            m_text_temp = ""
            m_text_feel = ""
            m_text_other = ""
            if len(cards_code_list) == 1:
                m_text_main_code = self.html_parser.get_tags(html_code=card_code_html, tag="span", tag_class_contains="fs-3 fw-bold", multiline=True)
                if m_text_main_code:
                    self.html_parser.load_html_code(m_text_main_code[0])
                    m_text_main = self.html_parser.get_raw_text()
                m_text_main_code = self.html_parser.get_tags(html_code=card_code_html, tag="div", tag_class_contains="col-sm-6", multiline=True)
                if m_text_main_code:
                    m_text_main_code = m_text_main_code[0]
                    if self.html_parser.get_tags(html_code=m_text_main_code, tag="ul", multiline=True):
                        for i in self.html_parser.get_tags(html_code=m_text_main_code, tag="li", multiline=True):
                            self.html_parser.load_html_code(i)
                            result = self.html_parser.get_raw_text()
                            if "°" in result and "Osećaj" in result:
                                m_text_feel += result
                            elif "°" in result and not "Osećaj" in result:
                                m_text_temp += result
                            else:
                                m_text_other += result
                    else:
                        self.html_parser.load_html_code(m_text_main_code)
                        result = self.html_parser.get_all_text_slices()
                        for i in result:
                            if m_text_feel:
                                m_text_feel += i.txt_value + " "
                            else:
                                m_text_temp += i.txt_value + " "
                        m_text_feel = m_text_feel.strip()
                        m_text_temp = m_text_temp.strip()
            else:
                result = self.html_parser.get_tags(html_code=card_code_html, tag="span", tag_class_contains="fs-4 fw-bold d-block", multiline=True)
                if result:
                    self.html_parser.load_html_code(result[0])
                    m_text_main = self.html_parser.get_raw_text()
                result = self.html_parser.get_tags(html_code=card_code_html, tag="div", tag_class_contains="col-4 text-center p-0", multiline=True)
                if result:
                    result = self.html_parser.get_tags(html_code=result[0], tag="li", multiline=True)
                    if result:
                        for i in result:
                            self.html_parser.load_html_code(i)
                            text_raw = self.html_parser.get_raw_text()
                            if "°" in text_raw and "Osećaj" in text_raw:
                                m_text_feel += text_raw + " "
                            elif "°" in text_raw and not "Osećaj" in text_raw:
                                m_text_temp += text_raw + " "
                            else:
                                m_text_other += text_raw + "\n"
                        m_text_feel = m_text_feel.strip()
                        m_text_temp = m_text_temp.strip()
                        m_text_other = m_text_other.strip()

            # Right side text
            r_text = ""
            if len(cards_code_list) == 1:
                result = self.html_parser.get_tags(html_code=card_code_html, tag="ul", tag_class_contains="list-unstyled lh-sm mb-0", multiline=True)
                if result:
                    result = self.html_parser.get_tags(html_code=result[0], tag="li", multiline=True)
                    for i in result:
                        self.html_parser.load_html_code(i)
                        r_text += self.html_parser.get_raw_text() + "\n"
                    r_text = r_text.strip()
            else:
                result = self.html_parser.get_tags(html_code=card_code_html, tag="ul", tag_class_contains="list-unstyled lh-sm mb-0", multiline=True)
                if result:
                    r_text_code = ""
                    for i in range(1, len(result)):
                        r_text_code += result[i].strip() + "\n"
                    r_text_code = r_text_code.strip()
                    result = self.html_parser.get_tags(html_code=r_text_code, tag="li", multiline=True)
                    if result:
                        for i in result:
                            self.html_parser.load_html_code(i)
                            r_text += self.html_parser.get_raw_text() + "\n"
                        r_text = r_text.strip()

            # Create QFrame
            border_size = self.frame_setting.get("border_size", 1)
            frame = QFrame(self)
            frame.setFrameShadow(QFrame.Plain)
            if self.frame_setting.get("border", True):
                frame.setFrameShape(QFrame.Box)
                frame.setLineWidth(self.frame_setting.get("border_size", 1))
            else:
                frame.setFrameShape(QFrame.NoFrame)
            
            if len(cards_code_list) == 1:
                l_text_size = 16
                m_text_main_size = 56
                r_text_size = 20
            else:
                l_text_size = 14
                m_text_main_size = 18
                r_text_size = 10

            r_text = self._style_text_list(r_text, r_text_size)

            # Left label
            lbl_l = QLabel(frame)
            lbl_l.setWordWrap(True)
            lbl_l.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            text_to_html = utility_cls.TextToHTML(l_text)
            text_to_html.general_rule.font_size = l_text_size + 4
            if len(cards_code_list) == 1:
                text_to_html.general_rule.fg_color = "#ffff00"
            else:
                text_to_html.general_rule.fg_color = "#ffaaff"
            rule1 = utility_cls.TextToHtmlRule(text="Sunce izlazi", fg_color="#fffcd5", font_size=l_text_size)
            rule2 = utility_cls.TextToHtmlRule(text="Sunce zalazi", fg_color="#cecece", font_size=l_text_size)
            text_to_html.add_rule(rule1)
            text_to_html.add_rule(rule2)
            lbl_l.setText(text_to_html.get_html())
            lbl_l.adjustSize()
            lbl_l.move(border_size, border_size)
            lbl_l.resize(lbl_l.width() + 20, lbl_l.height())

            # Image label
            lbl_img = QLabel(frame)
            
            # Mid label
            if not m_text_feel:
                m_text_feel = " "
            if not m_text_temp:
                m_text_temp = " "

            lbl_m = QLabel(frame)
            lbl_m.setWordWrap(True)
            m_text = "#1\n#2\n#3\n" + m_text_other
            text_to_html = utility_cls.TextToHTML(m_text)
            text_to_html.general_rule.font_size = 16
            text_to_html.general_rule.fg_color = "#ffffff"
            rule_main = utility_cls.TextToHtmlRule(text="#1", replace_with=m_text_main, fg_color="#cff7ff", font_bold=True, font_size=m_text_main_size)
            rule_temp = utility_cls.TextToHtmlRule(text="#2", replace_with=m_text_temp, fg_color="#ffff00", font_size=m_text_main_size)
            rule_feel = utility_cls.TextToHtmlRule(text="#3", replace_with=m_text_feel, fg_color="#00ff00", font_size=m_text_main_size - 6)
            text_to_html.add_rule(rule_main)
            text_to_html.add_rule(rule_temp)
            text_to_html.add_rule(rule_feel)
            lbl_m.setText(text_to_html.get_html())
            lbl_m.adjustSize()
            lbl_m.resize(lbl_m.width() + 20, lbl_m.height())

            # Right side label
            lbl_r = QLabel(frame)
            lbl_r.setWordWrap(True)
            font = lbl_r.font()
            font.setPointSize(r_text_size)
            lbl_r.setFont(font)
            lbl_r.setStyleSheet("color: #aaff7f;")
            lbl_r.setText(r_text)
            lbl_r.adjustSize()

            # Arrange widgets
            h = max(lbl_r.height(), lbl_l.height(), lbl_m.height())
            lbl_l.resize(lbl_l.width(), h)
            
            lbl_img.move(lbl_l.width(), border_size)
            lbl_img.resize(h, h)
            self.parent_widget.set_image_to_label(image, lbl_img, strech_to_label=True)

            lbl_m.move(lbl_img.pos().x() + lbl_img.width() + 20, border_size)
            lbl_m.resize(lbl_m.width(), h)

            lbl_r.move(lbl_m.pos().x() + lbl_m.width(), border_size)
            lbl_r.resize(lbl_r.width(), h)

            frame.resize(lbl_r.pos().x() + lbl_r.width() + border_size, h + border_size*2)

            frames_list.append(frame)
        
        return frames_list

    def _create_card_type_info(self):
        # Title
        title_code = self.html_parser.get_tags(html_code=self.card_html, tag="h2", multiline=True)
        title = ""
        if title_code:
            self.html_parser.load_html_code(title_code[0])
            title = self.html_parser.get_raw_text()
        
        # Setup QFrame
        self.setFrameShadow(QFrame.Plain)
        if self.frame_setting.get("border", True):
            self.setFrameShape(QFrame.Box)
            self.setLineWidth(self.frame_setting.get("border_size", 1))
        else:
            self.setFrameShape(QFrame.NoFrame)
        
        # Add Title label
        self.lbl_title = QLabel(self)
        pos = title.find(" - ")
        if pos != -1:
            title_add = title[pos + 3:]
            title = title[:pos+3] + "#--1"
            text_to_html = utility_cls.TextToHTML(title)
            text_to_html.general_rule.fg_color = "#00ff7f"
            text_to_html.general_rule.font_size = 24
            text_to_html.general_rule.font_bold = True
            title_addon_rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=title_add, fg_color="#00ff00")
            text_to_html.add_rule(title_addon_rule)
            self.lbl_title.setText(text_to_html.get_html())
        else:
            self.lbl_title.setText(title)

        self.lbl_title.adjustSize()
        self.lbl_title.move(self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1))
        y = self.lbl_title.height() + 6
        
        # Add line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        y += 14
                
        # Add Frames
        frames = self._create_frames_type_info()
        h = y
        w = self.lbl_title.width() + self.frame_setting["border_size"] * 2
        for frame in frames:
            w = max(w, frame.width() + self.frame_setting.get("border_size", 1) * 2)

        for frame in frames:
            frame: QFrame
            frame.move(self.lbl_title.pos().x(), y)
            frame.resize(w - self.frame_setting.get("border_size", 1) * 2, frame.height())
            y += frame.height()

            h = max(h, y + self.frame_setting.get("border_size", 1) * 2)
            if self.frame_setting.get("spacing", None):
                y += self.frame_setting["spacing"]

        # Resize self and line
        self.resize(w, h)
        self.line.move(self.lbl_title.pos().x() + 10, self.lbl_title.pos().y() + self.lbl_title.height() + 6)
        line_w = self.width() - self.lbl_title.pos().x() * 2 - 20
        if line_w < 0:
            line_w = 0
        self.line.resize(line_w, 3)

    def _create_card_type_geo(self):
        # Setup QFrame
        self.setFrameShadow(QFrame.Plain)
        if self.frame_setting.get("border", True):
            self.setFrameShape(QFrame.Box)
            self.setLineWidth(self.frame_setting.get("border_size", 1))
        else:
            self.setFrameShape(QFrame.NoFrame)

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1))

        # Title
        title_code = self.html_parser.get_tags(html_code=self.card_html, tag="h2", multiline=True)
        title = ""
        if title_code:
            self.html_parser.load_html_code(title_code[0])
            title = self.html_parser.get_raw_text()

        self.lbl_title = QLabel(self)
        font = self.lbl_title.font()
        font.setPointSize(20)
        self.lbl_title.setFont(font)
        self.lbl_title.setStyleSheet("color: #00ff00;")
        self.lbl_title.setText(title)
        
        self.layout.addWidget(self.lbl_title, 0, 0, 1, 2)
        self.lbl_title.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Add line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setFixedHeight(20)
        self.layout.addWidget(self.line, 1, 0, 1, 2)
        self.line.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        # Add WebBrowser
        self.web = QWebEngineView(self)
        self.layout.addWidget(self.web, 2, 0)
        self.web.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        html = self._get_geo_html()
        if html:
            self.web.setHtml(html)

        # Add label description
        self.lbl_desc = QLabel(self)
        self.lbl_desc.setTextInteractionFlags(self.lbl_desc.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.lbl_desc.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.layout.addWidget(self.lbl_desc, 2, 1)
        self.lbl_desc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        text = self._get_geo_description()
        self.lbl_desc.setText(text)
        self.lbl_desc.adjustSize()

        w = self.lbl_desc.width() + 250
        self.resize(self.frame_setting.get("max_width", w), int(self.frame_setting.get("max_width", w) / 7 * 4))

    def _create_card_type_climate(self):
        # Title
        title_code = self.html_parser.get_tags(html_code=self.card_html, tag="h2", multiline=True)
        title = ""
        if title_code:
            self.html_parser.load_html_code(title_code[0])
            title = self.html_parser.get_raw_text().strip()

        # Image
        self.html_parser.load_html_code(self.card_html)
        images = self.html_parser.get_all_images()
        image = ""
        if images:
            image = self.parent_widget.fix_url(images[0].img_src)
        
        # Info
        items_code = self.html_parser.get_tags(html_code=self.card_html, tag="li", multiline=True)
        items = ""
        if items_code:
            for item in items_code:
                self.html_parser.load_html_code(item)
                text = self.html_parser.get_raw_text().strip().replace("\n", "")
                items += text + "\n"

        # Description
        desc_code = self.html_parser.get_tags(html_code=self.card_html, tag="p", multiline=True)
        desc = ""
        if desc_code:
            for p in desc_code:
                self.html_parser.load_html_code(p)
                desc += self.html_parser.get_raw_text().strip() + "\n"
        desc = desc.strip()
        desc = self._style_text_desc(desc)

        # Create and set widgets apperance
        # Setup QFrame
        self.setFrameShadow(QFrame.Plain)
        if self.frame_setting.get("border", True):
            self.setFrameShape(QFrame.Box)
            self.setLineWidth(self.frame_setting.get("border_size", 1))
        else:
            self.setFrameShape(QFrame.NoFrame)

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1), self.frame_setting.get("border_size", 1))

        # Title
        self.lbl_title = QLabel(self)
        font = self.lbl_title.font()
        font.setPointSize(20)
        self.lbl_title.setFont(font)
        self.lbl_title.setStyleSheet("color: #00ff00;")
        self.lbl_title.setText(title)
        
        self.layout.addWidget(self.lbl_title, 0, 0, 1, 2)
        self.lbl_title.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Add line
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setFixedHeight(20)
        self.layout.addWidget(self.line, 1, 0, 1, 2)
        self.line.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        # Add Image label
        self.lbl_pic = QLabel(self)
        self.layout.addWidget(self.lbl_pic, 2, 0)
        self.lbl_pic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.parent_widget.set_image_to_label(image, self.lbl_pic, strech_to_label=True)

        # Add Info label
        self.lbl_info = QLabel(self)
        items = self._style_text_list(items, fontsize=14)
        self.lbl_info.setText(items)
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setTextInteractionFlags(self.lbl_info.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.lbl_info.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.layout.addWidget(self.lbl_info, 2, 1)
        self.lbl_info.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.lbl_info.adjustSize()

        # Add Desciption label
        self.lbl_desc = QLabel(self)
        font = self.lbl_desc.font()
        font.setPointSize(18)
        self.lbl_desc.setFont(font)
        self.lbl_desc.setStyleSheet("color: #c2d1d3;")
        self.lbl_desc.setText(desc)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setTextInteractionFlags(self.lbl_desc.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.layout.addWidget(self.lbl_desc, 3, 0, 1, 2)
        self.lbl_desc.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.lbl_desc.adjustSize()

        w = self.frame_setting.get("max_width", 400)
        img_w = w - self.lbl_info.width()
        if img_w < 0:
            img_w = 200
        h = self.lbl_title.height() + self.line.height() + self.lbl_desc.height() + img_w
        h = int(h / 4 * 3)
        h = max(h, self.lbl_title.height() + self.line.height() + self.lbl_info.height() + self.layout.spacing()*2 + 10)

        self.resize(w, h)

    def _get_geo_description(self) -> str:
        code_lists = self.html_parser.get_tags(html_code=self.card_html, tag="ul", multiline=True)
        if not code_lists:
            return ""
        
        # Get data
        desc = ""
        for list_code in code_lists:
            if "list-unstyled lh-sm mb-0" in self.html_parser.get_tag_property_value(html_code=list_code, tag="ul", tag_property="class"):
                continue

            item_codes = self.html_parser.get_tags(html_code=list_code, tag="li", multiline=True)
            for item_code in item_codes:
                self.html_parser.load_html_code(item_code)
                desc += self.html_parser.get_raw_text() + "\n"
            
            desc += "\n"
        
        desc = desc.strip()

        # Style data
        desc = self._style_text_list(desc)

        return desc

    def _style_text_desc(self, text: str, fontsize: int = 18) -> str:
        months = [
            "Januar",
            "Februar",
            "Mart",
            "April",
            "Maj",
            "Jun",
            "Jul",
            "Avgust",
            "August",
            "Septembar",
            "Oktobar",
            "Novembar",
            "Decembar"
        ]
        color_main = "#c2d1d3"
        color_in_par = "#ffaaff"
        color_temp = "#ff8383"
        color_month = "#aaaaff"
        color_par = "#ffff7f"

        # Find elements
        pos = 0
        count = 1
        rule_map = []
        replace_in_text = []
        while True:
            start = text.find("(", pos)
            if start == -1:
                break
            end = text.find(")", start)
            if end == -1:
                break
            
            mark = "#" + "-" * (5 - len(str(count))) + str(count)
            count += 1
            replace_in_text.append([start, start+1, mark])
            rule_map.append([mark, "(", color_par])

            mark = "#" + "-" * (5 - len(str(count))) + str(count)
            count += 1
            replace_in_text.append([start+1, end, mark])
            if "°" in text[start+1:end] or "%" in text[start+1:end]:
                rule_map.append([mark, text[start+1:end], color_temp])
            else:
                rule_map.append([mark, text[start+1:end], color_in_par])
            
            mark = "#" + "-" * (5 - len(str(count))) + str(count)
            count += 1
            replace_in_text.append([end, end+1, mark])
            rule_map.append([mark, ")", color_par])

            pos = end
        
        replace_in_text.sort(key=lambda x: x[0], reverse=True)

        for i in replace_in_text:
            text = f"{text[:i[0]]}{i[2]}{text[i[1]:]}"

        text_to_html = utility_cls.TextToHTML(text)
        text_to_html.general_rule.font_size = fontsize
        text_to_html.general_rule.fg_color = color_main

        for i in rule_map:
            rule = utility_cls.TextToHtmlRule(text=i[0], replace_with=i[1], fg_color=i[2])
            text_to_html.add_rule(rule)
        for i in months:
            rule = utility_cls.TextToHtmlRule(text=i, fg_color=color_month)
            text_to_html.add_rule(rule)

        result = text_to_html.get_html()
        return result

    def _style_text_list(self, text: str, fontsize: int = 12) -> str:
        # Style data
        themes = []
        values = []
        desc_raw = ""
        count = 1
        for line in text.splitlines():
            pos = line.find(":")
            if pos == -1:
                desc_raw += line + "\n"
                continue

            theme = line[:pos].strip()
            value = line[pos+1:].strip()

            if not theme or not value:
                desc_raw += line + "\n"
                continue

            mark = "#" + "-" * (5 - len(str(count))) + str(count)
            count += 1
            themes.append([theme, mark])
            desc_raw += mark + ": "

            mark = "#" + "-" * (5 - len(str(count))) + str(count)
            count += 1
            values.append([value, mark])
            desc_raw += mark + "\n"

        text_to_html = utility_cls.TextToHTML(text=desc_raw)
        text_to_html.general_rule.font_size = fontsize
        text_to_html.general_rule.fg_color = "#ffff00"

        for rule in themes:
            html_rule = utility_cls.TextToHtmlRule(text=rule[1], replace_with=rule[0], fg_color="#00ff7f")
            text_to_html.add_rule(html_rule)
        
        for rule in values:
            html_rule = utility_cls.TextToHtmlRule(text=rule[1], replace_with=rule[0], fg_color="#a4ffbb", font_size=fontsize+2)
            text_to_html.add_rule(html_rule)

        return text_to_html.get_html()

    def _get_geo_html(self) -> str:
        html_page_code = self.parent_widget.rashomon.get_segment_selection("page")
        lat = self.html_parser.get_tags(html_code=html_page_code, tag="meta", custom_tag_property=[["itemprop", "latitude"]], multiline=False)
        if lat:
            lat = self.html_parser.get_tag_property_value(html_code=lat[0], tag="meta", tag_property="content")
        lat = self.parent_widget._get_float(lat)
        if not lat:
            return None

        lon = self.html_parser.get_tags(html_code=html_page_code, tag="meta", custom_tag_property=[["itemprop", "longitude"]], multiline=False)
        if lon:
            lon = self.html_parser.get_tag_property_value(html_code=lon[0], tag="meta", tag_property="content")
        lon = self.parent_widget._get_float(lon)
        if not lon:
            return None
        
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=self.lbl_title.text()).add_to(m)
        html_code = m._repr_html_()
        return html_code


class AladinWE(AbstractTopic):
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
        uic.loadUi(self.getv("online_topic_aladin_we_ui_file_path"), self)

        # Define variables
        self.name = "aladin"
        self.topic_info_dict["name"] = self.name
        self.parent_widget = parent_widget
        self.title = self.getl("online_topic_aladin_we_title")
        self.topic_info_dict["title"] = self.title
        self.link = None
        self.icon_path = self.getv("online_topic_aladin_we_icon_path")
        self.icon_pixmap = QPixmap(self.icon_path)

        self.settings: dict = self._get_user_settings()
        self.active_page = None
        self.base_url = "https://www.aladin.info"
        self.menu_items = []
        self.menu_months = []
        self.cards = {}
        self.tables = []

        self._define_widgets()

        # Connect events with slots
        self.btn_search.clicked.connect(self.search_city)
        self.txt_search.returnPressed.connect(self.search_city)
        self.lbl_title_pic.mouseDoubleClickEvent = self.lbl_title_pic_mouse_double_click

        UTILS.LogHandler.add_log_record("#1: Topic frame loaded.", ["AladinWE"])

    def lbl_title_pic_mouse_double_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            site = self.lbl_title_pic.toolTip()
            webbrowser.open_new_tab(site)

    def search_city(self):
        # Search is forbidden
        search = self.txt_search.text().strip().lower()
        if len(search.split(",")) == 1:
            city = self._clean_search_string(search, remove_serbian_chars=True).replace("+", "-")
            self.active_page = f"https://www.aladin.info/sr/srbija/{city}"
            self.update_topic()
            return
        elif len(search.split(",")) == 2:
            country = self._clean_search_string(search.split(",")[0], remove_serbian_chars=True).replace("+", "-").strip()
            city = self._clean_search_string(search.split(",")[1], remove_serbian_chars=True).replace("+", "-").strip()
            if country in ["srbija", "srb", "sr", "s"]:
                country = "srbija"
            if country in ["cg", "mn", "me"]:
                country = "crna-gora"
            if country in ["hr", "hrv", "croatia", "cro", "h"]:
                country = "hrvatska"
            if country in ["bih", "bh", "ba", "b", "bosna"]:
                country = "bosna-i-hercegovina"
            self.active_page = f"https://www.aladin.info/sr/{country}/{city}"
            self.update_topic()
            return


        
        # ----------------------------------
        city = self.txt_search.text().strip()
        city = self._clean_search_string(city, remove_serbian_chars=False)

        if not city:
            return

        url = f"https://www.aladin.info/sr/search.php?q={city}"

        self.active_page = url

        self.update_topic()

    def cards_frame_button_click(self, card_key: str):
        for card_id in self.cards:
            item = self.cards[card_id]
            if card_id == card_key:
                item["active"] = True
            else:
                item["active"] = False
        self._colorize_frm_content_buttons()
        self.update_normal_page_content()

    def cards_frame_label_click(self, e: QMouseEvent, card_key: str):
        if e.button() == Qt.LeftButton:
            if self.cards[card_key]["active"]:
                self.cards[card_key]["active"] = False
            else:
                self.cards[card_key]["active"] = True
            self._colorize_frm_content_buttons()
            self.update_normal_page_content()

    def load_topic(self):
        UTILS.LogHandler.add_log_record("#1: Topic loaded.", ["AladinWE"])
        self.active_page = self.settings["start_page"]
        self.update_topic()
        return super().load_topic()
    
    def update_topic(self) -> bool:
        UTILS.LogHandler.add_log_record("#1: Updating topic.", ["AladinWE"])
        QCoreApplication.processEvents()
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_aladin_we") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

        self.setDisabled(True)
        QCoreApplication.processEvents()
        result = self._get_page_type()
        success = True
        
        if result == "loaded":
            success = True
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = ""
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            self.setDisabled(False)
            UTILS.LogHandler.add_log_record("#1: Topic updated.", ["AladinWE"])
            return success
        
        self._clear_all_tables()
        self._reset_cards_dict()

        if result is None:
            UTILS.LogHandler.add_log_record("#1: No page found.", ["AladinWE"])
            success = False
        elif result == "empty":
            success = self._load_empty_page()
        elif result == "search":
            success = self._load_search_page()
        elif result == "normal":
            success = self._load_normal_page()
        elif result == "klima":
            success = self._load_normal_page()

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False

        self._colorize_menu_items()
        self.setDisabled(False)

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False
        self.resize_me()

        if success:
            UTILS.LogHandler.add_log_record("#1: Topic updated.", ["AladinWE"])
        else:
            UTILS.LogHandler.add_log_record("#1: Topic update failed.", ["AladinWE"])

        return success

    def _colorize_menu_items(self):
        for item in self.menu_items:
            if item.objectName() == self.active_page:
                item.setStyleSheet("QPushButton {color: #ffff00; background-color: #005500;} QPushButton:hover {background-color: #0000ca;}")
            else:
                item.setStyleSheet("QPushButton {color: #ffff00; background-color: #000062;} QPushButton:hover {background-color: #0000ca;}")

        for item in self.menu_months:
            if item.objectName() == self.active_page:
                item.setStyleSheet("QPushButton {color: #00aa00; background-color: #005500;} QPushButton:hover {background-color: #0000ca;}")
            else:
                item.setStyleSheet("QPushButton {color: #ffff00; background-color: #48486c;} QPushButton:hover {background-color: #0000ca;}")

    def _set_title_text(self, base_text: str = None, line2_text: str = None, city_text: str = None):
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

            if city_text:
                if "#1" in line2_text:
                    text = f"{base_text}\n#1#2#3"
                    html_to_text.set_text(text)

                    pos = line2_text.find("#1")
                    part1 = line2_text[:pos]
                    part2 = city_text
                    part3 = line2_text[pos+2:]
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

        self.lbl_title.setText(result)

    def _load_normal_page(self) -> bool:
        result = self._load_project()
        if not result:
            return False
        
        # Set title text
        if self.rashomon.is_segment("page_title_000"):
            title_code = self.rashomon.get_segment_selection("page_title_000")
            self.html_parser.load_html_code(title_code)
            title = self.html_parser.get_raw_text()
            text_to_html = utility_cls.TextToHTML(text=title)
            text_to_html.general_rule.font_size = 25
            
            city_code = self.html_parser.get_tags(html_code=title_code, tag="span", custom_tag_property=[["itemprop", "addressLocality"]], multiline=True)
            if city_code:
                self.html_parser.load_html_code(city_code[0])
                city = self.html_parser.get_raw_text()
                if city:
                    city_text_rule = utility_cls.TextToHtmlRule(text=city, fg_color="#b2c0ff")
                    text_to_html.add_rule(city_text_rule)

            country_code = self.html_parser.get_tags(html_code=title_code, tag="span", custom_tag_property=[["itemprop", "addressCountry"]], multiline=True)
            if country_code:
                self.html_parser.load_html_code(country_code[0])
                country = self.html_parser.get_raw_text()
                if country:
                    country_text_rule = utility_cls.TextToHtmlRule(text=country, fg_color="#7a9394")
                    text_to_html.add_rule(country_text_rule)
            
            self.lbl_title.setText(text_to_html.get_html())
        
        # Set content
        self.line_menu.move(self.line_menu.pos().x(), self._get_next_y() - 5)
        self.line_menu.setVisible(True)

        self._create_menu_frame()
        self._create_months_frame()

        self.line_content.move(self.line_content.pos().x(), self._get_next_y())
        self.line_content.setVisible(True)

        QCoreApplication.processEvents()
        if self.stop_loading:
            return False

        # Get cards
        self._populate_cards_dict()
        self._setup_frm_content_buttons()
        self._colorize_frm_content_buttons()

        QCoreApplication.processEvents()
        if self.stop_loading:
            return False
        
        self._update_normal_page_content(delete_old_objects=True)
        QCoreApplication.processEvents()
        if self.stop_loading:
            return False
        
        self.settings["start_page"] = self.active_page
        self._update_user_settings()
        return True

    def update_normal_page_content(self, delete_old_objects: bool = False):
        QCoreApplication.processEvents()
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_aladin_we") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

        self.setDisabled(True)
        QCoreApplication.processEvents()

        self._update_normal_page_content(delete_old_objects=delete_old_objects)

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False

        self.setDisabled(False)

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

    def _update_normal_page_content(self, delete_old_objects: bool = False):
        for i in self.cards:
            if self.cards[i]["frame"]:
                self.cards[i]["frame"].setVisible(False)
                if delete_old_objects:
                    self.cards[i]["frame"].deleteLater()
                    self.cards[i]["frame"] = None

        for card_id in self.cards:
            if not self.cards[card_id]["enabled"] or not self.cards[card_id]["active"]:
                continue

            if self.cards[card_id]["frame"]:
                continue

            html = self.cards[card_id]["html"]
            if self.cards[card_id]["type"] == "table":
                page_info = Table.empty_table_dict()
                w = self.contentsRect().width() - self.frm_content_buttons.pos().x() - self.frm_content_buttons.width()
                if w < 150:
                    w = 150
                page_info["max_width"] = w
                page_info["items"] = html
                page_info["feedback_link_click_function"] = self.feedback_click_function
                
                self.cards[card_id]["frame"] = Table(self, self._stt, page_info)
            else:
                card_type = None
                card_setting = {
                    "border": False,
                    "border_size": 1,
                    "spacing": 10,
                    "max_width": self.width() - self.frm_content_buttons.pos().x() - self.frm_content_buttons.width() - 30
                }
                if card_id in ["today", "tomorrow", "saturday", "sunday", "now", "10", "hourly"]:
                    card_type = "info"
                elif card_id in ["geo"]:
                    card_type = "geo"
                elif card_id in ["temp", "hum", "rain", "rain_d", "snow", "snow_d", "daylight", "uv"]:
                    card_type = "climate"
                
                if card_type:
                    self.cards[card_id]["frame"] = Card(self, self._stt, card_html=html, card_type=card_type, frame_setting=card_setting)
        self._show_updated_normal_page()

    def _show_updated_normal_page(self):
        y = self._get_next_y() + 40
        for i in self.cards:
            if self.cards[i]["active"] and self.cards[i]["frame"]:
                self.cards[i]["frame"].move(self.frm_content_buttons.pos().x() + self.frm_content_buttons.width() + 30, y)
                y += self.cards[i]["frame"].height() + 30
                self.cards[i]["frame"].show()
            else:
                if self.cards[i]["frame"]:
                    self.cards[i]["frame"].setVisible(False)
        self.resize_me()

    def _populate_cards_dict(self, html: str = None):
        if not html:
            html = self.rashomon.get_segment_selection("page")

        cards_htmls = self.html_parser.get_tags(html_code=html, tag="div", tag_class_contains="card mb-3", multiline=True)
        for card_html in cards_htmls:
            card_key = self._get_card_dict_key(card_html)
            if not card_key:
                continue
            
            self.cards[card_key]["html"] = card_html
            self.cards[card_key]["enabled"] = True
            self.cards[card_key]["active"] = False

            if 'div class="card-body pb-0"' in card_html:
                self.cards[card_key]["type"] = "table"
            else:
                self.cards[card_key]["type"] = "card"
        
    def _setup_frm_content_buttons(self):
        y = 0
        frm_w = 0
        frm_h = 0
        for card in self.cards:
            card_item = self.cards[card]
            if not card_item["enabled"]:
                card_item["btn"].setVisible(False)
                card_item["lbl"].setVisible(False)
                continue
            
            card_item["lbl"].move(card_item["lbl"].pos().x(), y)
            card_item["btn"].move(card_item["btn"].pos().x(), y)
            card_item["btn"].setVisible(True)
            card_item["lbl"].setVisible(True)
            if card_item["active"]:
                card_item["lbl"].setPixmap(QPixmap(self.getv("checked_icon_path")))
            else:
                card_item["lbl"].setPixmap(QPixmap(self.getv("not_checked_icon_path")))
            y += card_item["btn"].height()

            frm_w = max(frm_w, card_item["btn"].pos().x() + card_item["btn"].width())
            frm_h = y
            y += 30
        
        self.frm_content_buttons.move(0, self._get_next_y() + 30)
        self.frm_content_buttons.resize(frm_w, frm_h)
        self.frm_content_buttons.setVisible(True)

    def _colorize_frm_content_buttons(self):
        for card in self.cards:
            card_item = self.cards[card]
            if card_item["active"]:
                card_item["lbl"].setPixmap(QPixmap(self.getv("checked_icon_path")))
                card_item["btn"].setStyleSheet("QPushButton {color: #ffff00; background-color: #005500;}  QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
            else:
                card_item["lbl"].setPixmap(QPixmap(self.getv("not_checked_icon_path")))
                card_item["btn"].setStyleSheet("QPushButton {color: rgb(170, 255, 255); background-color: rgb(0, 0, 79);} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
            
    def _get_card_dict_key(self, html: str) -> str:
        if 'span class="collapse collapse-text show float-end"' in html:
            return False

        h2 = self.html_parser.get_tags(html_code=html, tag="h2", multiline=True)
        if h2:
            h2 = h2[0]
        h4 = self.html_parser.get_tags(html_code=html, tag="h4", multiline=True)
        if h4:
            h4 = h4[0]
        if not h2:
            h2 = h4
        iframe = self.html_parser.get_tags(html_code=html, tag="iframe", multiline=True)
        if iframe:
            iframe = iframe[0]
        
        if "Prognoza i temperatura za danas" in h2:
            return "today"
        elif "Prognoza i temperatura za sutra" in h2:
            return "tomorrow"
        elif "Vremenska prognoza" in h2 and "Subota" in h2:
            return "saturday"
        elif "Vremenska prognoza" in h2 and "Nedelja" in h2:
            return "sunday"
        elif "Trenutno stanje i temperatura" in h2:
            return "now"
        elif "Vremenska prognoza za 10 dana" in h2:
            return "10"
        elif "Vremenska prognoza i temperatura po satima" in h2:
            return "hourly"
        elif "U blizini" in h4:
            return "near"
        elif 'id="most_visited"' in h4:
            return "most"
        elif 'https://www.google.com/maps/embed/' in iframe:
            return "geo"
        elif "Prosečna temperatura" in h2:
            return "temp"
        elif "Prosečna relativna vlažnost" in h2:
            return "hum"
        elif "Prosečne kišne padavine" in h2:
            return "rain"
        elif "Prosečno kišnih dana" in h2:
            return "rain_d"
        elif "Prosečne snežne padavine" in h2:
            return "snow"
        elif "Prosečno snežnih dana" in h2:
            return "snow_d"
        elif "Prosečna dnevna svetlost" in h2:
            return "daylight"
        elif "Prosečan UV indeks" in h2:
            return "uv"
        
        return None

    def _reset_cards_dict(self):
        for card in self.cards:
            self.cards[card]["btn"].setVisible(False)
            self.cards[card]["lbl"].setVisible(False)
            self.cards[card]["enabled"] = False
            self.cards[card]["active"] = False
            if self.cards[card]["frame"]:
                self.cards[card]["frame"].deleteLater()
            self.cards[card]["frame"] = None
            self.cards[card]["html"] = ""
    
    def _create_months_frame(self) -> bool:
        result = self._load_project()
        if not result:
            return False
        
        if not self.rashomon.is_segment("page_months_000"):
            return False
        
        # Delete old months items
        for item in self.menu_months:
            item.setVisible(False)
            item.deleteLater()
        self.menu_months = []

        # Create new menu items
        menu_items_segments = self.rashomon.get_segment_children("page_months")

        x = 0
        w = 0
        h = 0
        for menu_item_segment in menu_items_segments:
            menu_item_code = self.rashomon.get_segment_selection(menu_item_segment)
            menu_item_code = self.html_parser.remove_specific_tag(html_code=menu_item_code, tag="span", multiline=True)
            self.html_parser.load_html_code(menu_item_code)
            # Link
            links = self.html_parser.get_all_links()
            if links:
                link = self.fix_url(links[0].a_href)
            else:
                continue
            # Text
            text = self.html_parser.get_raw_text()
            # Create menu item
            btn_menu_item = QPushButton(self.frm_months)
            font = btn_menu_item.font()
            font.setPointSize(10)
            font.setBold(True)
            btn_menu_item.setFont(font)
            btn_menu_item.setStyleSheet("QPushButton {color: #ffff00; background-color: #004c00;} QPushButton:hover {background-color: #008f00;}")
            btn_menu_item.setText(text)
            btn_menu_item.clicked.connect(lambda _, link_val=link: self.feedback_click_function(link_val))
            btn_menu_item.adjustSize()
            btn_menu_item.move(x, 25)
            btn_menu_item.setObjectName(link)
            self.menu_items.append(btn_menu_item)
            x += btn_menu_item.width() + 10

            h = max(h, btn_menu_item.height() + 25)
            w = x - 10

        # Show menu frame
        self.frm_months.move(10, self._get_next_y())
        self.frm_months.resize(w, h)
        self.frm_months.setVisible(True)
        self.frm_months.show()
        return True

    def _create_menu_frame(self) -> bool:
        result = self._load_project()
        if not result:
            return False
        
        if not self.rashomon.is_segment("page_menu_000"):
            return False
        
        # Delete old menu items
        for item in self.menu_items:
            item.setVisible(False)
            item.deleteLater()
        self.menu_items = []

        # Create new menu items
        menu_items_segments = self.rashomon.get_segment_children("page_menu")

        x = 0
        w = 0
        h = 0
        for menu_item_segment in menu_items_segments:
            menu_item_code = self.rashomon.get_segment_selection(menu_item_segment)
            self.html_parser.load_html_code(menu_item_code)
            # Link
            links = self.html_parser.get_all_links()
            if links:
                link = self.fix_url(links[0].a_href)
            else:
                continue
            # Text
            text = self.html_parser.get_raw_text()
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
        return True

    def _load_search_page(self) -> bool:
        self.rashomon.clear_errors()
        result = self._load_project()
        
        self._set_title_text()

        if not result:
            if self.rashomon.errors():
                msg_error = "ERROR: \n\n"
                for i in self.rashomon.errors():
                    msg_error += f"{i}\n"
            else:
                msg_error = "No results found."

            QMessageBox.critical(self, "Error", msg_error)            
            return False
        
        self._set_title_text(line2_text=self.getl("online_aladin_we_lbl_title_search_results_text"))

        data = Table.empty_table_dict()
        data["max_width"] = self.contentsRect().width() - 20
        
        # Title
        title = ""
        self.rashomon.clear_errors()
        if self.rashomon.is_segment("search_title_000"):
            title = self.rashomon.get_segment_selection("search_title_000", remove_tags=True, join_in_one_line=True)
        
        if not title:
            if self.rashomon.errors():
                title = f"ERROR: {self.rashomon.errors()[0]}"
            else:
                title = "No results found."
        self.rashomon.clear_errors()

        data["title"] = title
        data["feedback_link_click_function"] = self.feedback_click_function

        # Items
        if self.rashomon.is_segment("search_no_result_000"):
            self.html_parser.load_html_code(self.rashomon.get_segment_selection("search_no_result_000"))
            text = self.html_parser.get_raw_text()
            text_slices = self.html_parser.get_all_text_slices()
            image = ""
            link = ""

            data["items"]["1"] = {}
            
            data["items"]["1"]["text"] = text
            data["items"]["1"]["text_slices"] = text_slices
            data["items"]["1"]["image"] = image
            data["items"]["1"]["link"] = link
        else:            
            items_code = self.rashomon.get_segment_selection("page")

            cards_code_list = self.html_parser.get_tags(html_code=items_code, tag="div", tag_class_contains="card-body pb-0", multiline=True)
            if cards_code_list:
                items_code_list = self.html_parser.get_tags(html_code=cards_code_list[0], tag="li", multiline=True)
            else:
                return False

            count = 1
            for item_code in items_code_list:
                self.html_parser.load_html_code(item_code)
                images = self.html_parser.get_all_images()
                image = ""
                if images:
                    image = images[0].img_src
                text = self.html_parser.get_raw_text()
                text_slices = self.html_parser.get_all_text_slices()
                for i in text_slices:
                    i.txt_link = self.fix_url(i.txt_link)
                links = self.html_parser.get_all_links()
                link = ""
                if links:
                    link = self.fix_url(links[0].a_href)
                
                data["items"][str(count)] = {}
                data["items"][str(count)]["text"] = text
                data["items"][str(count)]["text_slices"] = text_slices
                data["items"][str(count)]["image"] = self.fix_url(image)
                data["items"][str(count)]["link"] = self.fix_url(link)

                count += 1
            
        self.line_menu.setVisible(True)
        self.line_menu.move(self.line_menu.pos().x(), self._get_next_y() - 5)

        self.table_search = Table(self, self._stt, data)
        self.table_search.move(0, self._get_next_y())
        self.table_search.setVisible(True)
        self.table_search.show()

        QCoreApplication.processEvents()
        if self.stop_loading:
            return False
        
        self._load_country_table()
        self.txt_search.setFocus()
        self.settings["search_text"] = self.txt_search.text()
        self._update_user_settings()
        return True

    def _load_country_table(self):
        data = Table.empty_table_dict()
        data["max_width"] = self.contentsRect().width() - 20
        data["border"] = True

        # Title
        data["title"] = self.getl("online_aladin_we_country_table_title")
        data["feedback_link_click_function"] = self.feedback_click_function

        # Items
        if self.rashomon.is_segment("countries_000"):
            items_code = self.rashomon.get_segment_selection("countries_000")
        else:
            return False

        items_code_list = self.html_parser.get_tags(html_code=items_code, tag="li", multiline=True)

        count = 1
        for item_code in items_code_list:
            self.html_parser.load_html_code(item_code)
            images = self.html_parser.get_all_images()
            image = ""
            if images:
                image = images[0].img_src
            text = self.html_parser.get_raw_text()
            text_slices = self.html_parser.get_all_text_slices()
            for i in text_slices:
                i.txt_link = self.fix_url(i.txt_link)
            links = self.html_parser.get_all_links()
            link = ""
            if links:
                link = self.fix_url(links[0].a_href)
            
            data["items"][str(count)] = {}
            data["items"][str(count)]["text"] = text
            data["items"][str(count)]["text_slices"] = text_slices
            data["items"][str(count)]["image"] = self.fix_url(image)
            data["items"][str(count)]["link"] = self.fix_url(link)

            count += 1
        
        self.table_country = Table(self, self._stt, data)
        self.table_country.move(0, self._get_next_y())
        self.table_country.setVisible(True)
        self.table_country.show()
        return True

    def feedback_click_function(self, data: dict):
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
        
    def _get_next_y(self):
        y = self.frm_search.pos().y() + self.frm_search.height() + 20
        if self.line_menu.isVisible():
            y = self.line_menu.pos().y() + self.line_menu.height() + 5

        if self.frm_menu and self.frm_menu.isVisible():
            y = self.frm_menu.pos().y() + self.frm_menu.height() + 10

        if self.frm_months and self.frm_months.isVisible():
            y = self.frm_months.pos().y() + self.frm_months.height() + 10

        if self.line_content.isVisible():
            y = self.line_content.pos().y() + self.line_content.height() + 5

        if self.table_search and self.table_search.isVisible():
            y = self.table_search.pos().y() + self.table_search.height() + 10

        if self.table_country and self.table_country.isVisible():
            y = self.table_country.pos().y() + self.table_country.height() + 10
        
        for i in self.cards:
            if self.cards[i]["active"]:
                if self.cards[i]["frame"] and self.cards[i]["frame"].isVisible():
                    y = self.cards[i]["frame"].pos().y() + self.cards[i]["frame"].height() + 10

        return y
    
    def _load_empty_page(self):
        return True

    def _get_page_type(self, page_url: str = None) -> str:
        if not page_url:
            page_url = self.active_page
            
        if not page_url:
            return "empty"
        
        page_url = self.fix_url(page_url)
        if self.active_page == self.rashomon.get_source():
            return "loaded"

        page_type = None
        if "search.php?" in page_url:
            page_type = "search"
        elif "-klima" in page_url:
            page_type = "klima"
        elif "aladin.info" in page_url:
            page_type = "normal"

        return page_type

    def _load_project(self, url: str = None) -> bool:
        if url is None:
            url = self.active_page
        
        if not url:
            return False
        
        if self.rashomon.get_source() == url:
            return True
        
        self.rashomon.clear_errors()
        project_name = self.getv("rashomon_folder_path") + "aladin_we.rpf"
        result = self.rashomon.load_project(project_filename=project_name, change_source=url)
        if self.rashomon.errors() or not result:
            return False

        self.rashomon.set_compatible_mode(True)

        result = self.rashomon.recreate_segment_tree()
        if self.rashomon.errors() or not result:
            return False

        return result

    def _clear_all_tables(self):
        if self.table_search:
            self.table_search.setVisible(False)
            self.table_search.deleteLater()
            self.table_search: Table = None
        if self.table_country:
            self.table_country.setVisible(False)
            self.table_country.deleteLater()
            self.table_country: Table = None

        self.frm_menu.setVisible(False)
        self.frm_months.setVisible(False)
        self.line_content.setVisible(False)
        self.line_menu.setVisible(False)
        self.frm_content_buttons.setVisible(False)

    def _get_user_settings(self) -> dict:
        result = {
            "start_page": None
            }

        if "online_topic_aladin_we_settings" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("online_topic_aladin_we_settings")
            
            result["start_page"] = g.get("start_page", None)
            self.active_page = result["start_page"]

            result["search_text"] = g.get("search_text", "")
            self.txt_search.setText(result["search_text"])
        
        return result

    def _update_user_settings(self) -> None:
        if "online_topic_aladin_we_settings" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("online_topic_aladin_we_settings", self.settings, save_to_file=True)

        self.set_appv("online_topic_aladin_we_settings", self.settings)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resize_me()
        return super().resizeEvent(a0)
    
    def resize_me(self, size: QSize = None):
        w = self.contentsRect().width()
        w_title = w - self.lbl_title.pos().x() - 10
        if w_title < 100:
            w_title = 100
        self.lbl_title.resize(w_title, self.lbl_title.height())
        self.line_title.resize(w - 10 - self.line_title.pos().x(), self.line_title.height())
        self.line_menu.resize(w - 10 - self.line_menu.pos().x(), self.line_menu.height())
        self.line_content.resize(w - 10 - self.line_content.pos().x(), self.line_content.height())
        
        self.setFixedHeight(max(self._get_next_y(), self.parent_widget.get_topic_area_size().height(), self.frm_content_buttons.pos().y() + self.frm_content_buttons.height()))

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

        self.frm_menu: QFrame = self.findChild(QFrame, "frm_menu")
        self.frm_months: QFrame = self.findChild(QFrame, "frm_months")
        self.lbl_months_title: QLabel = self.findChild(QLabel, "lbl_months_title")

        self.frm_content_buttons: QFrame = self.findChild(QFrame, "frm_content_buttons")
        self.btn_cb_today: QPushButton = self.findChild(QPushButton, "btn_cb_today")
        self.lbl_cb_today: QLabel = self.findChild(QLabel, "lbl_cb_today")
        self.btn_cb_tomorrow: QPushButton = self.findChild(QPushButton, "btn_cb_tomorrow")
        self.lbl_cb_tomorrow: QLabel = self.findChild(QLabel, "lbl_cb_tomorrow")
        self.btn_cb_sat: QPushButton = self.findChild(QPushButton, "btn_cb_sat")
        self.lbl_cb_sat: QLabel = self.findChild(QLabel, "lbl_cb_sat")
        self.btn_cb_sun: QPushButton = self.findChild(QPushButton, "btn_cb_sun")
        self.lbl_cb_sun: QLabel = self.findChild(QLabel, "lbl_cb_sun")
        self.btn_cb_now: QPushButton = self.findChild(QPushButton, "btn_cb_now")
        self.lbl_cb_now: QLabel = self.findChild(QLabel, "lbl_cb_now")
        self.btn_cb_10: QPushButton = self.findChild(QPushButton, "btn_cb_10")
        self.lbl_cb_10: QLabel = self.findChild(QLabel, "lbl_cb_10")
        self.btn_cb_hourly: QPushButton = self.findChild(QPushButton, "btn_cb_hourly")
        self.lbl_cb_hourly: QLabel = self.findChild(QLabel, "lbl_cb_hourly")
        self.btn_cb_geo: QPushButton = self.findChild(QPushButton, "btn_cb_geo")
        self.lbl_cb_geo: QLabel = self.findChild(QLabel, "lbl_cb_geo")
        self.btn_cb_near: QPushButton = self.findChild(QPushButton, "btn_cb_near")
        self.lbl_cb_near: QLabel = self.findChild(QLabel, "lbl_cb_near")
        self.btn_cb_most: QPushButton = self.findChild(QPushButton, "btn_cb_most")
        self.lbl_cb_most: QLabel = self.findChild(QLabel, "lbl_cb_most")
        self.btn_cb_temp: QPushButton = self.findChild(QPushButton, "btn_cb_temp")
        self.lbl_cb_temp: QLabel = self.findChild(QLabel, "lbl_cb_temp")
        self.btn_cb_hum: QPushButton = self.findChild(QPushButton, "btn_cb_hum")
        self.lbl_cb_hum: QLabel = self.findChild(QLabel, "lbl_cb_hum")
        self.btn_cb_rain: QPushButton = self.findChild(QPushButton, "btn_cb_rain")
        self.lbl_cb_rain: QLabel = self.findChild(QLabel, "lbl_cb_rain")
        self.btn_cb_rain_d: QPushButton = self.findChild(QPushButton, "btn_cb_rain_d")
        self.lbl_cb_rain_d: QLabel = self.findChild(QLabel, "lbl_cb_rain_d")
        self.btn_cb_snow: QPushButton = self.findChild(QPushButton, "btn_cb_snow")
        self.lbl_cb_snow: QLabel = self.findChild(QLabel, "lbl_cb_snow")
        self.btn_cb_snow_d: QPushButton = self.findChild(QPushButton, "btn_cb_snow_d")
        self.lbl_cb_snow_d: QLabel = self.findChild(QLabel, "lbl_cb_snow_d")
        self.btn_cb_daylight: QPushButton = self.findChild(QPushButton, "btn_cb_daylight")
        self.lbl_cb_daylight: QLabel = self.findChild(QLabel, "lbl_cb_daylight")
        self.btn_cb_uv: QPushButton = self.findChild(QPushButton, "btn_cb_uv")
        self.lbl_cb_uv: QLabel = self.findChild(QLabel, "lbl_cb_uv")

        self.table_search: Table = None
        self.table_country: Table = None

        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        self.lbl_title.setText(self.getl("online_aladin_we_lbl_title_text"))
        self.line_menu.setVisible(False)
        self.line_content.setVisible(False)

        self.txt_search.setPlaceholderText("Država(srb-cg-bih-hrv), Grad")

        self.frm_menu.setVisible(False)
        self.frm_months.setVisible(False)
        self.lbl_months_title.setText(self.getl("online_aladin_we_lbl_months_title_text"))

        self.frm_content_buttons.setVisible(False)
        self._define_cards()

    def _define_cards(self):
        self.cards["today"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_today,
            "lbl": self.lbl_cb_today,
            "title": self.getl("online_aladin_we_btn_cb_today_text"),
            "html": "",
            "frame": None,
            "enabled": False
        }
        self.cards["tomorrow"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_tomorrow,
            "lbl": self.lbl_cb_tomorrow,
            "title": self.getl("online_aladin_we_btn_cb_tomorrow_text"),
            "html": "",
            "frame": None,
            "enabled": False
        }
        self.cards["saturday"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_sat,
            "lbl": self.lbl_cb_sat,
            "title": self.getl("online_aladin_we_btn_cb_sat_text"),
            "html": "",
            "frame": None,
            "enabled": False
        }
        self.cards["sunday"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_sun,
            "lbl": self.lbl_cb_sun,
            "title": self.getl("online_aladin_we_btn_cb_sun_text"),
            "html": "",
            "frame": None,
            "enabled": False
        }
        self.cards["now"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_now,
            "lbl": self.lbl_cb_now,
            "title": self.getl("online_aladin_we_btn_cb_now_text"),
            "html": "",
            "frame": None,
            "enabled": False
            }
        self.cards["10"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_10,
            "lbl": self.lbl_cb_10,
            "title": self.getl("online_aladin_we_btn_cb_10_text"),
            "html": "",
            "frame": None,
            "enabled": False
            }
        self.cards["hourly"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_hourly,
            "lbl": self.lbl_cb_hourly,
            "title": self.getl("online_aladin_we_btn_cb_hourly_text"),
            "html": "",
            "frame": None,
            "enabled": False
        }
        self.cards["geo"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_geo,
            "lbl": self.lbl_cb_geo,
            "title": self.getl("online_aladin_we_btn_cb_geo_text"),
            "html": "",
            "frame": None,
            "enabled": False
        }
        self.cards["near"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_near,
            "lbl": self.lbl_cb_near,
            "title": self.getl("online_aladin_we_btn_cb_near_text"),
            "html": "",
            "frame": None,
            "enabled": False
            }
        self.cards["most"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_most, 
            "lbl": self.lbl_cb_most,
            "title": self.getl("online_aladin_we_btn_cb_most_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["temp"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_temp, 
            "lbl": self.lbl_cb_temp,
            "title": self.getl("online_aladin_we_btn_cb_temp_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["hum"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_hum, 
            "lbl": self.lbl_cb_hum,
            "title": self.getl("online_aladin_we_btn_cb_hum_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["rain"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_rain, 
            "lbl": self.lbl_cb_rain,
            "title": self.getl("online_aladin_we_btn_cb_rain_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["rain_d"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_rain_d, 
            "lbl": self.lbl_cb_rain_d,
            "title": self.getl("online_aladin_we_btn_cb_rain_d_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["snow"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_snow, 
            "lbl": self.lbl_cb_snow,
            "title": self.getl("online_aladin_we_btn_cb_snow_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["snow_d"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_snow_d, 
            "lbl": self.lbl_cb_snow_d,
            "title": self.getl("online_aladin_we_btn_cb_snow_d_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["daylight"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_daylight, 
            "lbl": self.lbl_cb_daylight,
            "title": self.getl("online_aladin_we_btn_cb_daylight_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        self.cards["uv"] = {
            "active": False,
            "type": "",
            "btn": self.btn_cb_uv, 
            "lbl": self.lbl_cb_uv,
            "title": self.getl("online_aladin_we_btn_cb_uv_text"),
            "html": "", 
            "frame": None,
            "enabled": False
        }
        for k, v in self.cards.items():
            v["btn"].setText(v["title"])
            v["btn"].adjustSize()
            v["btn"].setVisible(v["enabled"])
            v["btn"].move(v["btn"].height() + 2, v["btn"].pos().y())
            v["btn"].clicked.connect(lambda _, card_key=k: self.cards_frame_button_click(card_key))
            
            v["lbl"].resize(v["btn"].height(), v["btn"].height())
            v["lbl"].setVisible(v["enabled"])
            v["lbl"].mousePressEvent = lambda e, card_key=k: self.cards_frame_label_click(e, card_key)

            

        
        
        


