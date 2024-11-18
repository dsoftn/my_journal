from PyQt5.QtWidgets import QFrame, QWidget, QLabel, QComboBox, QTableWidget, QToolTip, QDialog
from PyQt5.QtGui import QIcon, QPixmap, QMouseEvent, QFont, QFontMetrics, QResizeEvent, QCursor, QCloseEvent
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QPoint, pyqtSignal, QRect

import webbrowser
import os
import requests
import urllib.request
import html as HtmlLib

import settings_cls
import utility_cls
import html_parser_cls
from media_player_cls import MediaPlayer
import UTILS


class WikiFrameSettings:
    def __init__(self, settings_dict: dict = None):
        if settings_dict:
            self.settings = settings_dict
        else:
            self.settings = {}
        
        self.load_settings_dictionary(self.settings)
        
    def load_settings_dictionary(self, settings_dict: dict):
        """Load settings dictionary"""
        self.wiki_width = settings_dict.get("width", 800)
        self.wiki_height = settings_dict.get("height", 600)
        self.wiki_has_border = settings_dict.get("has_border", False)
        self.wiki_fg_color = settings_dict.get("fg_color", "#aaff7f")
        self.wiki_bg_color = settings_dict.get("bg_color", "#2a4155")
        self.wiki_feedback = settings_dict.get("feedback", None)
        self.wiki_ignore_feedback = settings_dict.get("ignore_feedback", True)
        self.wiki_size_changed_feedback = settings_dict.get("size_changed_feedback", None)
        self.wiki_loading_text = settings_dict.get("loading_text", "Loading...")

        self.wiki_title_fg_color = settings_dict.get("title_fg_color", "#c8ffa6")
        self.wiki_title_bg_color = settings_dict.get("title_bg_color", "#d60000")
        self.wiki_title_font_size = settings_dict.get("title_font_size", 26)
        self.wiki_title_font_bold = settings_dict.get("title_font_bold", True)
        
        self.wiki_info_bg_color = settings_dict.get("info_bg_color", "#395773")
        self.wiki_info_width = settings_dict.get("info_width", 360)
        self.wiki_info_has_border = settings_dict.get("info_has_border", False)
        self.wiki_info_category_value_ratio = settings_dict.get("info_category_value_ratio", 0.62)
        self.wiki_info_spacing_hor = settings_dict.get("info_spacing_hor", 4)
        self.wiki_info_spacing_ver = settings_dict.get("info_spacing_ver", 10)
        self.wiki_info_padding_hor = settings_dict.get("info_padding_hor", 10)
        self.wiki_info_padding_ver = settings_dict.get("info_padding_ver", 10)

        self.wiki_info_indent_fg_color = settings_dict.get("info_indent_fg_color", "#975aff")
        
        self.wiki_figure_bg_color = settings_dict.get("figure_bg_color", "#4c3673")
        self.wiki_figure_width = settings_dict.get("figure_width", 270)

        self.wiki_image_desc_fg_color = settings_dict.get("image_desc_fg_color", "#cfcfcf")
        self.wiki_image_desc_font_size = settings_dict.get("image_desc_font_size", 12)

        self.wiki_label_name_fg_color = settings_dict.get("label_name_fg_color", "#00ff00")
        self.wiki_label_name_font_size = settings_dict.get("label_name_font_size", 14)
        self.wiki_label_name_font_bold = settings_dict.get("label_name_font_bold", True)

        self.wiki_label_header_fg_color = settings_dict.get("label_header_fg_color", "#ffffff")
        self.wiki_label_header_bg_color = settings_dict.get("label_header_bg_color", "#cf0000")
        self.wiki_label_section_title_bg_color = settings_dict.get("label_section_title_bg_color", "#003100")
        self.wiki_label_header_font_size = settings_dict.get("label_header_font_size", 16)
        self.wiki_label_header_font_bold = settings_dict.get("label_header_font_bold", True)

        self.wiki_label_title_fg_color = settings_dict.get("label_title_fg_color", "#ffff00")
        self.wiki_label_title_font_size = settings_dict.get("label_title_font_size", 18)
        self.wiki_label_title_font_bold = settings_dict.get("label_title_font_bold", True)

        self.wiki_label_value_fg_color = settings_dict.get("label_value_fg_color", "#aaff00")
        self.wiki_label_value_font_size = settings_dict.get("label_value_font_size", 14)

        self.wiki_content_text_fg_color = settings_dict.get("content_text_fg_color", "#d5d5d5")
        self.wiki_content_text_title_fg_color = settings_dict.get("content_text_title_fg_color", "#ebebeb")
        self.wiki_content_text_bg_color = settings_dict.get("content_text_bg_color", "#141431")
        self.wiki_content_text_font_size = settings_dict.get("content_text_font_size", 22)

        self.wiki_content_code_fg_color = settings_dict.get("content_code_fg_color", "#dadada")
        self.wiki_content_code_bg_color = settings_dict.get("content_code_bg_color", "#000000")
        self.wiki_content_code_font_size = settings_dict.get("content_code_font_size", 14)
        self.wiki_content_code_title_fg_color = settings_dict.get("content_code_title_fg_color", "#eaea74")
        self.wiki_content_code_title_bg_color = settings_dict.get("content_code_title_bg_color", "#555555")
        self.wiki_content_code_title_font_size = settings_dict.get("content_code_title_font_size", 16)

        self.wiki_content_dd_fg_color = settings_dict.get("content_dd_fg_color", "#bfbfbf")
        self.wiki_content_dd_font_size = settings_dict.get("content_dd_font_size", 20)

        self.wiki_content_list_fg_color = settings_dict.get("content_list_fg_color", "#c8d4ba")
        self.wiki_content_list_dl_bg_color = settings_dict.get("content_list_dl_bg_color", "#e3e0b4")
        self.wiki_content_list_font_size = settings_dict.get("content_list_font_size", 22)

        self.wiki_content_warning_fg_color = settings_dict.get("content_list_fg_color", "#aa5500")
        self.wiki_content_warning_font_size = settings_dict.get("content_list_font_size", 14)

        self.wiki_content_toc_fg_color = settings_dict.get("content_toc_fg_color", "#ffff00")
        self.wiki_content_toc_bg_color = settings_dict.get("content_toc_bg_color", "#3e8c90")
        self.wiki_content_toc_has_border = settings_dict.get("content_top_has_border", True)
        self.wiki_content_toc_hover_color = settings_dict.get("content_toc_hover_color", "#914800")
        self.wiki_content_toc_selected_color = settings_dict.get("content_toc_selected_color", "#777d00")
        self.wiki_content_toc_font_size = settings_dict.get("content_toc_font_size", 16)
        self.wiki_content_toc_font_bold = settings_dict.get("content_toc_font_bold", False)

        self.settings = settings_dict
    
    def get_settings_dictionary(self) -> dict:
        return self.settings


class WikiImageView(QDialog):
    def __init__(self, parent_widget, settings: settings_cls.Settings):
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
        self.html_parser = html_parser_cls.HtmlParser()
        self._clip: utility_cls.Clipboard = self.get_appv("cb")
        self.image_url = None

        self.url = None
        self.html = None

        self._define_widgets()

        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.lbl_title.mousePressEvent = self.clear_context_menu

    def lbl_pic_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.clear_context_menu()
            self._show_context_menu()
        else:
            self.clear_context_menu()

        QLabel.mousePressEvent(self.lbl_pic, e)

    def clear_context_menu(self, e = None):
        self.get_appv("cm").remove_all_context_menu()

    def _show_context_menu(self):
        if not self.image_url:
            disab = [10, 20]
        else:
            disab = []

        if self._clip.is_clip_empty():
            disab.append(30)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [],
            "items": [
                [
                    10,
                    self.getl("image_menu_copy_text"),
                    self.getl("image_menu_copy_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    20,
                    self.getl("image_menu_add_to_clip_text"),
                    self.getl("image_menu_add_to_clip_tt"),
                    True,
                    [],
                    self.getv("copy_icon_path")
                ],
                [
                    30,
                    self.getl("image_menu_clear_clipboard_text"),
                    self._clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }

        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self)
        
        if self.get_appv("menu")["result"] == 10:
            self._clip.copy_to_clip(self.image_url, add_to_clip=False)
        elif self.get_appv("menu")["result"] == 20:
            self._clip.copy_to_clip(self.image_url, add_to_clip=True)
        elif self.get_appv("menu")["result"] == 30:
            self._clip.clear_clip()

    def show_image(self):
        if not self.html:
            self._show_error()
            return
        
        self._load_image()

    def _load_image(self):
        if not self.html:
            self._show_error()
            return
        
        images = self.html_parser.get_all_images(load_html_code=self.html)
        img_obj = None
        size = 0
        for image in images:
            image: html_parser_cls.ImageObject
            if image.img_width and image.img_height:
                image_size = image.img_height * image.img_width
                if image_size > size:
                    img_obj = image
                    size = image_size
        
        if not img_obj:
            self._show_error()
            return

        self._setup_labels(img_obj)
        result = self._set_image_to_label(img_obj)

        if not result:
            self._show_error()

    def _setup_labels(self, image_obj: html_parser_cls.ImageObject):
        w = image_obj.img_width
        title = image_obj.img_alt
        if not title:
            title = image_obj.img_title
        if not title:
            title = image_obj.img_link_title
        title = HtmlLib.unescape(title)

        font = self.lbl_title.font()
        font.setPointSize(int(12 + (w/100)*1.3))
        self.lbl_title.setFont(font)
        self.lbl_title.setText(title)
        self.lbl_title.setFixedWidth(w)
        self.lbl_title.adjustSize()

    def _set_image_to_label(self, img_obj: html_parser_cls.ImageObject) -> bool:
        if img_obj.img_src:
            image_url = img_obj.img_src
        else:
            return False
        
        if img_obj.img_title:
            tt = img_obj.img_title
        else:
            tt = ""

        if image_url.startswith("//"):
            image_url = "https:" + image_url

        img = None
        has_image = False
        try:
            img = None
            if not has_image:
                if os.path.isfile(image_url):
                    img = QPixmap()
                    has_image = img.load(os.path.abspath(image_url))
                else:
                    response = urllib.request.urlopen(image_url, timeout=2).read()
                    img = QPixmap()
                    has_image = img.loadFromData(response)
                    if not has_image:
                        response = requests.get(image_url, timeout=2)
                        has_image = img.loadFromData(response.content)
        except:
            img = None
        
        if tt:
            self.lbl_pic.setToolTip(tt)

        if not has_image:
            return False

        self.image_url = image_url        
        
        self.resize(img.width(), img.height() + self.lbl_title.height())
        self.lbl_pic.setScaledContents(True)
        self.lbl_pic.setPixmap(img)
        return True

    def _show_error(self):
        self.lbl_pic.setText("Error.")

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.clear_context_menu()
        return super().closeEvent(a0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.lbl_title.setFixedWidth(w)
        self.lbl_title.adjustSize()
        self.lbl_title.move(0, h - self.lbl_title.height())

        self.lbl_pic.resize(w, h - self.lbl_title.height())

        return super().resizeEvent(a0)

    def _define_widgets(self):
        self.setWindowIcon(QIcon(self.getv("online_content_win_icon_path")))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Wikipedia: Media")

        self.lbl_pic = QLabel(self)
        self.lbl_pic.setAlignment(Qt.AlignCenter)
        font = self.lbl_pic.font()
        font.setPointSize(64)
        font.setBold(True)
        self.lbl_pic.setFont(font)
        self.lbl_pic.setStyleSheet("color: red;")
        self.lbl_pic.setText("⌛")
        
        self.lbl_title = QLabel(self)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet(f"color: yellow; background-color: red;")
        self.lbl_title.setWordWrap(True)


class WikiData:
    def __init__(self, url: str, wiki_frame_settings: WikiFrameSettings = None):
        self.url = url
        self.base_url = self._get_base_url()
        self.has_page = None

        self.wiki_frame_settings = wiki_frame_settings
        if self.wiki_frame_settings is None:
            self.wiki_frame_settings = WikiFrameSettings()

        self.html = self._load_url(url)
        self.html = self._format_html(self.html)
        self.html_parser = html_parser_cls.HtmlParser()
        self.html_parser.special_case_rules = "wikipedia"
        self.html_parser.load_html_code(self.html)
        self.html = self.html_parser.html_code

        self._populate_data()

    def _format_html(self, html: str) -> str:
        pos = 0
        start = 0
        result = []
        while True:
            pos = html.find("<pre", pos)
            if pos != -1:
                end = html.find("</pre>", pos)
                if end != -1:
                    result.append(html[start:pos])
                    result.append(html[pos:end])
                    pos = end
                    start = end
                else:
                    result.append(html[start:pos])
                    result.append(html[pos:])
                    break
            else:
                result.append(html[start:])
                break

        text = ""
        for i in result:
            if i.startswith("<pre"):
                i = i.replace("\n", "<br>")
                i = i.replace("\t", "<t>")
                text += i
            else:
                text += i
        
        return text

    def _populate_data(self):
        # Fix html
        self.html = self.html_parser.remove_specific_tag(html_code=self.html, tag="style", multiline=True)
        pos = 0
        while True:
            pos = self.html.find('<span class="legend-color"', pos)
            if pos == -1:
                break
            pos = self.html.find("</span", pos)
            if pos == -1:
                break
            self.html = self.html[:pos] + "██\n" + self.html[pos:]

        # Title
        self.data_title = {}
        self.data_title["text"] = self._get_title()
        # Available languages
        self.data_languages = self._get_languages()
        # Alphabet
        self.data_alphabet = self._get_alphabet()
        # Labels
        self.data_labels = self._get_labels_data()
        if self.data_labels is None:
            self.data_labels = []
        # Content
        self.data_content = self._get_content_data()

        # Set has_page variable
        if self.data_labels or self.data_content or self.data_title:
            self.has_page = True
        else:
            self.has_page = False
        
    def _get_content_data(self) -> list:
        # Get all elements
        elements_dict = {}
        # Get all lists with images
        lists_with_images = self.html_parser.get_tags(html_code=self.html, tag="li", return_line_numbers=True)
        figure_list = []
        if lists_with_images:
            for li in lists_with_images:
                img = self.html_parser.get_all_images(load_html_code=li[0])
                if img:
                    img = img[0]
                    if img.img_width and img.img_height:
                        if img.img_width > 30 and img.img_height > 30:
                            figure_list.append(li)
        elements_dict["c_figure"] = figure_list

        elements_dict["c_table"] = self.html_parser.get_tags(html_code=self.html, tag="table", return_line_numbers=True)
        
        list_results = self.html_parser.get_tags(html_code=self.html, tag="li", return_line_numbers=True)
        elements_dict["c_list"] = []
        for list_result in list_results:
            if list_result not in figure_list:
                elements_dict["c_list"].append(list_result)

        div_add_to_list = self.html_parser.get_tags(html_code=self.html, tag="div", tag_class_contains="NavHead", return_line_numbers=True)
        for item in div_add_to_list:
            item_fixed = "<li>" + item[0] + "</li>"
            elements_dict["c_list"].append([item_fixed, item[1], item[2]])

        div_add_to_list = self.html_parser.get_tags(html_code=self.html, tag="div", custom_tag_property=[["style", "background:#EFFFFF"]], return_line_numbers=True)
        for item in div_add_to_list:
            item_fixed = "<li>" + item[0] + "</li>"
            elements_dict["c_list"].append([item_fixed, item[1], item[2]])
        
        for item in elements_dict["c_table"]:
            caption_code = self.html_parser.get_tags(html_code=item[0], tag="caption", return_line_numbers=True)
            for caption in caption_code:
                caption_text = "<li>" + self.html_parser.crop_html_code(caption[0]) + "</li>"
                caption_start = item[1] - 1
                caption_end = caption[2] + item[1]
                elements_dict["c_list"].append([caption_text, caption_start, caption_end])
        

        elements_dict["c_text"] = self.html_parser.get_tags(html_code=self.html, tag="p", return_line_numbers=True)
        elements_dict["c_text"] = self._remove_duplicate_CRLF(elements_dict["c_text"])
        # Add TD elements if not in table
        for item in self.html_parser.get_tags(html_code=self.html, tag="td", return_line_numbers=True):
            is_in_table = False
            for i in elements_dict['c_table']:
                if item[1] >= i[1] and item[2] <= i[2]:
                    is_in_table = True
                    break
            if not is_in_table:
                elements_dict["c_text"].append(item)

        elements_dict["c_figure"] += self.html_parser.get_tags(html_code=self.html, tag="figure", return_line_numbers=True)
        elements_dict["c_section"] = self.html_parser.get_tags(html_code=self.html, tag="div", tag_class_contains="mw-heading", return_line_numbers=True)
        elements_dict["c_dl"] = self.html_parser.get_tags(html_code=self.html, tag="dl", return_line_numbers=True)
        elements_dict["c_code"] = self.html_parser.get_tags(html_code=self.html, tag="div", tag_class_contains="mw-highlight", return_line_numbers=True)
        elements_dict["c_pre"] = self.html_parser.get_tags(html_code=self.html, tag="pre", return_line_numbers=True)

        elements_dict["c_table_presentation"] = []

        # Find content start line
        content_start = 0
        count = 0
        for i in self.html.splitlines():
            if i == "<p>":
                content_start = count
                break
            count += 1

        # Move all c_figure starts before text in first section
        for idx, i in enumerate(elements_dict["c_figure"]):
            if i[1] < content_start:
                elements_dict["c_figure"][idx][1] = content_start - 1
                elements_dict["c_figure"][idx][2] = content_start - 1

        # Add tables with warnings
        for table in elements_dict["c_table"]:
            if table[1] < content_start:
                if "presentation" in self.html_parser.get_tag_property_value(html_code=table[0], tag="table", tag_property="role"):
                    elements_dict["c_table_presentation"].append([table[0], content_start - 1, content_start - 1])
        
        # Check is there info label that is not detected
        not_detected_info_table = None
        remove_table_index = None
        for idx, table in enumerate(elements_dict["c_table"]):
            if "infobox" in self.html_parser.get_tag_property_value(html_code=table[0], tag="table", tag_property="class") and remove_table_index is None:
                remove_table_index = idx
            if table[1] < content_start:
                if "presentation" not in self.html_parser.get_tag_property_value(html_code=table[0], tag="table", tag_property="role"):
                    if "<figure" not in table[0]:
                        not_detected_info_table = table[0]
        
        if remove_table_index is not None:
            elements_dict["c_table"].pop(remove_table_index)

        if not_detected_info_table and not self.data_labels:
            self.data_labels = self._get_labels_data(not_detected_info_table)
            if self.data_labels is None:
                self.data_labels = []

        # Move presentation tables in c_table_presentation
        tables_to_move = []
        for idx, table in enumerate(elements_dict["c_table"]):
            if table[1] > content_start:
                if "presentation" in self.html_parser.get_tag_property_value(html_code=table[0], tag="table", tag_property="role"):
                    tables_to_move.append([idx, table])
        tables_to_move.sort(key=lambda x: x[0], reverse=True)
        for i in tables_to_move:
            elements_dict["c_table_presentation"].append(i[1])
            del elements_dict["c_table"][i[0]]
        
        # Add starting section
        introduction = self.data_title["text"]
        if not introduction:
            introduction = "Introduction..."
        elements_dict["c_section"].append([f'<span class="mw-headline">\n{introduction}\n</span>\n', content_start - 2, content_start -2])

        content_start -= 2

        # Arrange the elements chronologically
        all_elements = []
        for element_group in elements_dict:
            for element in elements_dict[element_group]:
                if element[1] >= content_start:
                    all_elements.append([element_group, element[0], element[1], element[2]])
        all_elements.sort(key=lambda x: x[2])

        # Make data list
        content_data = []
        section_data = {}
        for section in all_elements:
            # Fix section code
            section[1] = self.html_parser.remove_tags(html_code=section[1], tag="annotation")

            # Section
            if section[0] == "c_section":
                if section_data:
                    content_data.append(section_data)
                section_data = self._get_empty_section_dict()

                section_data["code"] = section[1]
                section_data["text"] = self.text_to_html(self.html_parser.get_all_text_slices(load_html_code=section[1]), shema="toc")

            if not section_data:
                continue

            # Text
            if section[0] == "c_text":
                if "math" in self.html_parser.get_tag_property_value(html_code=section[1], tag="span", tag_property="class") and "<img" in section[1]:
                    section[0] = "c_dl"
                else:
                    if "c_list" not in self._get_duplicates(position=section[2], sections_list=all_elements) and "c_figure" not in self._get_duplicates(position=section[2], sections_list=all_elements):
                        element = {
                            "type": section[0],
                            "code": section[1],
                            "text": self.text_to_html(self.html_parser.get_all_text_slices(load_html_code=section[1]), shema="section_text")
                        }
                        section_data["data"].append(element)

            # Pre tag
            if section[0] == "c_pre":
                if len(self._get_duplicates(position=section[2], sections_list=all_elements)) == 1:
                    element = {
                        "type": "c_list",
                        "code": section[1],
                        "text_list": []
                    }
                    list_items = self.html_parser.get_all_text_slices(load_html_code=section[1])
                    for item in list_items:
                        element["text_list"].append(f"<li>{item.txt_value}</li>")
                    section_data["data"].append(element)
            
            # Table
            if section[0] == "c_table":
                element = {
                    "type": section[0],
                    "code": section[1],
                    "role": "",
                    "class": "",
                    "table_obj": None,
                    "labels": []
                }
                tables = self.html_parser.get_all_tables(load_html_code=section[1])
                if tables:
                    element["table_obj"] = tables[0]
                element["role"] = self.html_parser.get_tag_property_value(html_code=section[1], tag="table", tag_property="role")
                
                element["class"] = self.html_parser.get_tag_property_value(html_code=section[1], tag="table", tag_property="class")
                if "infobox" in element["class"]:
                    element["labels"] = self._get_labels_data(section[1])
                
                section_data["data"].append(element)

            # Table Presentation
            if section[0] == "c_table_presentation":
                element = {
                    "type": section[0],
                    "code": section[1],
                    "text": "",
                    "image": "",
                    "image_w": 0,
                    "image_h": 0
                }
                images = self.html_parser.get_all_images(load_html_code=section[1])
                if images:
                    element["image"] = images[0].img_src
                    element["image_w"] = images[0].img_width
                    element["image_h"] = images[0].img_height
                element["text"] = self.text_to_html(text_slices=self.html_parser.get_all_text_slices(load_html_code=section[1]), shema="warning")
                section_data["data"].append(element)

            # List
            if section[0] == "c_list" and "c_table" not in self._get_duplicates(section[2], all_elements):
                element = {
                    "type": section[0],
                    "code": section[1],
                    "text_list": []
                }
                list_items = self.html_parser.get_tags(html_code=section[1], tag="li")
                if "gallery " in self.html_parser.get_tag_property_value(html_code=section[1], tag="ul", tag_property="class"):
                    for i in list_items:
                        element = self._get_content_figure_element(i)
                        section_data["data"].append(element)
                else:
                    for i in list_items:
                        element["text_list"].append(self.text_to_html(text_slices=self.html_parser.get_all_text_slices(load_html_code=i), shema="section_list"))
                    section_data["data"].append(element)

            # dl
            if section[0] == "c_dl":
                element = {
                    "type": section[0],
                    "code": section[1],
                    "text_list": [],
                    "image": {}
                }
                element["text_list"].append(self.text_to_html(text_slices=self.html_parser.get_all_text_slices(load_html_code=section[1]), shema="dl_text"))
                dl_images = self.html_parser.get_all_images(load_html_code=section[1])
                if dl_images:
                    element["image"]["src"] = self.fix_url(dl_images[0].img_src)
                    element["image"]["width"] = dl_images[0].img_width
                    element["image"]["height"] = dl_images[0].img_height
                    element["image"]["width_ex"] = dl_images[0].img_width_ex
                    element["image"]["height_ex"] = dl_images[0].img_height_ex
                    
                section_data["data"].append(element)
            
            # Code snippets
            if section[0] == "c_code":
                element = {
                    "type": section[0],
                    "code": section[1],
                    "text": "",
                    "title": ""
                }
                snippet = self._format_code_snippet(section[1])
                title = "Code"
                title_hint = self.html_parser.get_tag_property_value(html_code=section[1], tag="div", tag_property="class")
                if title_hint:
                    pos = title_hint.find("lang-")
                    if pos != -1:
                        end = title_hint.find(" ", pos)
                        if end == -1:
                            end = len(title_hint)
                        title = title_hint[pos+5:end].strip(" ><-")
                element["title"] = title
                element["text"] = snippet.strip()
                section_data["data"].append(element)

            # Figure
            if section[0] == "c_figure":
                element = self._get_content_figure_element(section[1])
                section_data["data"].append(element)
        if all_elements:
            content_data.append(section_data)
        
        return content_data

    def _remove_duplicate_CRLF(self, text_slices: list) -> list:
        cleaned_text = []
        
        for text in text_slices:
            has_text = False
            text_slices = self.html_parser.get_all_text_slices(load_html_code=text[0]if isinstance(text, list) else text)
            if text_slices:
                for text_slice in text_slices:
                    if text_slice.txt_value != "\n":
                        has_text = True
                        break
                
                if has_text:
                    text_clean = self.html_parser.crop_html_code(text[0], starting_lines=1, ending_lines=0)
                    cleaned_text.append([text_clean, text[1], text[2]])
        
        return cleaned_text

    def _format_code_snippet(self, code: str) -> str:
        return self.html_parser.get_raw_text(load_html_code=code)

    def _get_duplicates(self, position: int, sections_list: list) -> list:
        result = []
        for item in sections_list:
            item_start = item[2]
            item_end = item[3]
            if position >= item_start and position <= item_end:
                result.append(item[0])
        return result

    def _get_content_figure_element(self, section_code: str) -> dict:
        element = {
            "type": "c_figure",
            "code": section_code,
            "image": "",
            "image_w": 0,
            "image_h": 0,
            "title": "",
            "image_link": "",
            "image_ratio": None,
            "text": ""
        }
        images = self.html_parser.get_all_images(load_html_code=section_code)
        for i in images:
            if i.img_width and i.img_height:
                if i.img_width < 30 or i.img_height < 30:
                    continue
                element["image_ratio"] = i.img_width / i.img_height
            element["image"] = self.fix_url(i.img_src) if i.img_src else ""
            element["image_w"] = i.img_width if i.img_width else 0
            element["image_h"] = i.img_height if i.img_height else 0
            element["title"] = i.img_title if i.img_title else ""
            element["image_link"] = self.fix_url(i.img_link) if i.img_link else ""
        
        element["text"] = self.text_to_html(self.html_parser.get_all_text_slices(load_html_code=section_code), shema="image_desc")
        return element

    def _get_empty_section_dict(self) -> dict:
        result = {
            "code": "",
            "text": "",
            "data": []
        }
        return result

    def _get_labels_data(self, force_table: str = None) -> list:
        labels_var = []
        
        if force_table:
            label_code = force_table
        else:
            label_code = self.html_parser.get_tags(html_code=self.html, tag="table", tag_class_contains="infobox")
            if label_code:
                label_code = label_code[0]
        
        if not label_code:
            return
        
        label_rows_code = self.html_parser.get_tags(html_code=label_code, tag="tr")
        
        for row_code in label_rows_code:
            row_code = self.html_parser.remove_specific_tag(html_code=row_code, tag="style")

            label = {
                "raw_text": "",
                "name": "",
                "value": "",
                "image": [],
                "image_desc": "",
                "icon": "",
                "colspan": 1,
                "rowspan": 1,
                "type": "",
                "audio": []
            }

            label["raw_text"] = self.html_parser.get_raw_text(load_html_code=row_code)

            # Label codes
            row_code_th, row_code_td = self._get_label_name_and_value_code(row_code=row_code)
            text = ""
            for i in row_code_th:
                text += i + "\n"
            row_code_th = []
            if text:
                row_code_th.append(text)
            text = ""
            for i in row_code_td:
                text += i + "\n"
            row_code_td = []
            if text:
                row_code_td.append(text)

            # Label name
            if row_code_th:
                if "header" in self.html_parser.get_tag_property_value(html_code=row_code_th[0], tag_property="class"):
                    label_shema = "label_header"
                    label["type"] = "header"
                elif "above" in self.html_parser.get_tag_property_value(html_code=row_code_th[0], tag_property="class"):
                    label_shema = "label_title"
                    label["type"] = "title"
                else:
                    label_shema = "label_name"
                    label["type"] = "normal"
                label["name"] = self.text_to_html(self.html_parser.get_all_text_slices(load_html_code=row_code_th[0]), shema=label_shema)

            # Label value
            if row_code_td:
                if "header" in self.html_parser.get_tag_property_value(html_code=row_code_td[0], tag_property="class"):
                    label_shema = "label_header"
                    label["type"] = "header"
                elif "above" in self.html_parser.get_tag_property_value(html_code=row_code_td[0], tag_property="class"):
                    label_shema = "label_title"
                    label["type"] = "title"
                else:
                    label_shema = "label_value"
                label["value"] = self.text_to_html(self.html_parser.get_all_text_slices(load_html_code=row_code_td[0]), shema=label_shema)

            # Audio
            audios = self.html_parser.get_tags(html_code=row_code, tag="audio")
            if audios:
                label["audio"] = self._get_audios(audios[0])
            
            # Span
            if row_code_th:
                th_colspan = self._get_integer(self.html_parser.get_tag_property_value(html_code=row_code_th[0], tag_property="colspan"))
                if not th_colspan:
                    th_colspan = 1
                label["colspan"] = max(label["colspan"], th_colspan)
                
            if row_code_td:
                td_colspan = self._get_integer(self.html_parser.get_tag_property_value(html_code=row_code_td[0], tag_property="colspan"))
                if not td_colspan:
                    td_colspan = 1
                label["colspan"] = max(label["colspan"], td_colspan)

            row_span = self._get_integer(self.html_parser.get_tag_property_value(html_code=row_code, tag_property="rowspan"))
            if row_span:
                label["rowspan"] = row_span

            # Images
            image_objects = self.html_parser.get_all_images(load_html_code=row_code)
            image_marker_set = False
            for image_obj in image_objects:
                image_obj: html_parser_cls.ImageObject
                image_dict = {
                    "src": "",
                    "title": "",
                    "link": "",
                    "ratio": None,
                    "image_w": 0,
                    "image_h": 0,
                    "tt": "",
                    "marker_image": {}
                }

                if "mw-kartographer-map" in image_obj.img_link_class:
                    continue

                # Check is icon
                if 'span class="plainlinks"' in image_obj.tag_list:
                    image_dict["src"] = image_obj.img_src
                    image_dict["title"] = image_obj.img_title
                    image_dict["link"] = image_obj.img_link
                    image_dict["image_h"] = image_obj.img_height
                    image_dict["image_w"] = image_obj.img_width
                    label["icon"] = image_dict
                    continue

                if image_obj.img_width and image_obj.img_height:
                    if ((image_obj.img_width < 30 or image_obj.img_height < 30) and label["value"]) or image_marker_set:
                        continue
                    image_dict["ratio"] = image_obj.img_width / image_obj.img_height
                    image_dict["image_w"] = image_obj.img_width
                    image_dict["image_h"] = image_obj.img_height
                
                image_dict["src"] = self.fix_url(image_obj.img_src)
                image_dict["title"] = image_obj.img_title
                image_dict["link"] = self.fix_url(image_obj.img_link)
                image_dict["tt"] = image_obj.img_link_title + "\n" + image_dict["link"]

                label["image"].append(image_dict)
                label["image_desc"] = self.text_to_html(text_slices=self.html_parser.get_all_text_slices(load_html_code=row_code), shema="image_desc")
                label["name"] = ""
                label["value"] = ""

                if self._check_image_marker(image_dict=image_dict, row_code=row_code):
                    image_marker_set = True
            
            labels_var.append(label)
        
        return labels_var

    def _get_audios(self, audio_code: str) -> list:
        result = []
        sources = self.html_parser.get_tags(html_code=audio_code, tag="source")
        for source in sources:
            source_src = self.html_parser.get_tag_property_value(html_code=source, tag="source", tag_property="src")
            source_src = self.fix_url(source_src)
            source_type = self.html_parser.get_tag_property_value(html_code=source, tag="source", tag_property="type")
            if source_src:
                if "wav" in source_type:
                    source_type = "100 " + source_type
                elif "mp3" in source_type:
                    source_type = "200 " + source_type
                elif "mpeg" in source_type:
                    source_type = "300 " + source_type
                else:
                    source_type = "900 " + source_type
                
                result.append([source_src, source_type])
        
        if not result:
            return []
        
        result.sort(key= lambda x: x[1])
        return [x[0] for x in result]

    def _check_image_marker(self, image_dict: dict, row_code: str) -> bool:
        process_code = row_code
        divs = self.html_parser.get_tags(html_code=process_code, tag="div", custom_tag_property=[["style", "top"], ["style", "left"], ["style", "%"]])
        if not divs:
            return False

        for div in divs:
            style = self.html_parser.get_tag_property_value(html_code=div, tag="div", tag_property="style")
            if style and "top" in style and "left" in style and "%" in style:
                images = self.html_parser.get_all_images(load_html_code=div)
                if images:
                    if "Red_pog.svg" in images[0].img_src or "Red_triangle" in images[0].img_src or True:
                        start = style.find("top:")
                        if start != -1:
                            end = style.find("%", start)
                            if end != -1:
                                top_val = style[start+4:end]
                        start = style.find("left:")
                        if start != -1:
                            end = style.find("%", start)
                            if end != -1:
                                left_val = style[start+5:end]
                        top_val = self._get_float(top_val)
                        left_val = self._get_float(left_val)
                        if top_val and left_val and (images[0].img_width and images[0].img_width < 30) and (images[0].img_height and images[0].img_height < 30):
                            image_dict["marker_image"]["image_w"] = images[0].img_width
                            image_dict["marker_image"]["image_h"] = images[0].img_height
                            image_dict["marker_image"]["src"] = self.fix_url(images[0].img_src)
                            image_dict["marker_image"]["marker_top"] = top_val
                            image_dict["marker_image"]["marker_left"] = left_val
                            return True
            else:
                if self._check_image_marker(image_dict=image_dict, row_code=self.html_parser.crop_html_code(html_code=div)):
                    return True
        return False

    def _get_float(self, text: str) -> float:
        result = None
        try:
            result = float(text)
        except:
            result = None
        return result

    def _get_label_name_and_value_code(self, row_code: str) -> tuple:
        th_code = self.html_parser.get_tags(html_code=row_code, tag="th")
        if not th_code:
            th_code = []
        td_code = self.html_parser.get_tags(html_code=row_code, tag="td")
        if not td_code:
            td_code = []

        if len(th_code) < 2 and len(td_code) < 2:
            return (th_code, td_code)
        
        if len(th_code) == 0:
            th_code = [td_code[0]]
            td_code.pop(0)
        elif len(td_code) == 0:
            td_code = [th_code[0]]
            th_code.pop(0)

        return (th_code, td_code)

    def _remove_wiki_from_text(self, txt: str) -> str:
        items = self._find_wiki_links(txt)
        
        for i in items:
            txt = txt[:i[0]] + "`" * len(i[2]) + txt[i[1]:]
        
        txt = txt.replace("`", "")

        return txt

    def _find_wiki_links(self, txt: str) -> list:
        start = 0
        result = []
        while start >= 0:
            start = txt.find("[", start)
            if start >= 0:
                end = txt.find("]", start)
                if end >= 0:
                    result.append((start, end + 1, txt[start:end + 1]))
                    start = end
                else:
                    start = -1
            
        return result

    def _get_alphabet(self) -> dict:
        result = {
            "title": "",
            "selected": "",
            "list": []
        }

        code = self.html_parser.get_tags(html_code=self.html, tag="div", tag_id_contains="vector-variants", tag_class_contains="vector-dropdown")
        if code:
            # Title
            title_code = self.html_parser.get_tags(html_code=code[0], tag="span", tag_class_contains="vector-dropdown-label-text")
            if title_code:
                result["title"] = self.html_parser.get_raw_text(load_html_code=title_code[0]).strip()

            # Alphabets list
            alph_code = self.html_parser.get_tags(html_code=code[0], tag="li")
            for item in alph_code:
                alph = {
                    "text": "",
                    "link": ""
                }

                text_slices = self.html_parser.get_all_text_slices(load_html_code=item)
                alph_text = ""
                alph_link = ""
                for text_slice in text_slices:
                    text_slice: html_parser_cls.TextObject
                    alph_text += text_slice.txt_value + " "
                    if not alph_link:
                        alph_link = self.fix_url(text_slice.txt_link)
                alph_text = alph_text.strip()
                if "selected" in self.html_parser.get_tag_property_value(html_code=item, tag="li", tag_property="class"):
                    result["selected"] = alph_text
                
                alph["text"] = alph_text
                alph["link"] = alph_link
                
                result["list"].append(alph)
        return result

    def _get_languages(self) -> dict:
        result = {
            "title": "",
            "selected": "",
            "list": []
        }

        code = self.html_parser.get_tags(html_code=self.html, tag="div", tag_class_contains="vector-dropdown mw-portlet mw-portlet-lang")
        if code:
            # Title
            title_code = self.html_parser.get_tags(html_code=code[0], tag="span", tag_class_contains="vector-dropdown-label-text")
            if title_code:
                result["title"] = self.html_parser.get_raw_text(title_code[0]).strip()
            
            # Language list
            lang_code = self.html_parser.get_tags(html_code=code[0], tag="ul")
            if lang_code:
                lang_items = self.html_parser.get_tags(html_code=lang_code[0], tag="li")
                for item in lang_items:
                    lang = {
                        "text": "",
                        "link": ""
                    }

                    text_slices = self.html_parser.get_all_text_slices(load_html_code=item)
                    lang_text = ""
                    lang_link = ""
                    for text_slice in text_slices:
                        text_slice: html_parser_cls.TextObject
                        lang_text += text_slice.txt_value + " "
                        if not lang_link:
                            lang_link = text_slice.txt_link
                    lang_text = lang_text.strip()
                    if "selected" in self.html_parser.get_tag_property_value(html_code=item, tag="li", tag_property="class"):
                        result["selected"] = lang_text
                    
                    lang["text"] = lang_text
                    lang["link"] = lang_link

                    result["list"].append(lang)
        return result

    def _get_title(self) -> str:
        result = ""
        code = self.html_parser.get_tags(html_code=self.html, tag="h1")
        if code:
            result = self.html_parser.get_raw_text(load_html_code=code[0]).strip()
            # result = self._remove_wiki_from_text(result)

        return result

    def _load_url(self, url: str):
        try:
            response = requests.get(url)
            result = response.text
            if result:
                return result
            else:
                return ""
        except Exception as e:
            return ""

    def _get_base_url(self) -> str:
        pos = self.url.find(".org")
        if pos != -1:
            result = self.url[:pos+4]
        else:
            result = ""
        return result
    
    def fix_url(self, url: str) -> str:
        if "/index.php" in url or "#" in url:
            return ""
        
        result = url
        if url.startswith("//"):
            result = "https:" + url
        elif url.startswith("/"):
            result = self.base_url + url
        
        if result.startswith("https://sr."):
            result = result.replace("/wiki/", "/sr-el/")
        return result

    def text_to_html(self, text_slices: list, fg_color: str = None, bg_color: str = None, font_family: str = None, font_size: int = None, font_bold: bool = False, font_italic: bool = False, shema: str = None) -> str:
        formater = utility_cls.TextToHTML()

        if shema == "image_desc":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_image_desc_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_image_desc_font_size
        elif shema == "label_name":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_label_name_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_label_name_font_size
            formater.general_rule.font_bold = self.wiki_frame_settings.wiki_label_name_font_bold
        elif shema == "label_header":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_label_header_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_label_header_font_size
            formater.general_rule.font_bold = self.wiki_frame_settings.wiki_label_header_font_bold
        elif shema == "label_title":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_label_title_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_label_title_font_size
            formater.general_rule.font_bold = self.wiki_frame_settings.wiki_label_title_font_bold
        elif shema == "label_value":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_label_value_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_label_value_font_size
        elif shema == "toc":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_content_toc_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_content_toc_font_size
            formater.general_rule.font_bold = self.wiki_frame_settings.wiki_content_toc_font_bold
        elif shema == "section_text":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_content_text_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_content_text_font_size
        elif shema == "section_list":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_content_list_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_content_list_font_size
        elif shema == "dl_text":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_content_dd_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_content_dd_font_size
        elif shema == "warning":
            formater.general_rule.fg_color = self.wiki_frame_settings.wiki_content_warning_fg_color
            formater.general_rule.font_size = self.wiki_frame_settings.wiki_content_warning_font_size

        if fg_color:
            formater.general_rule.fg_color = fg_color
        if bg_color:
            formater.general_rule.bg_color = bg_color
        if font_family:
            formater.general_rule.font_family = font_family
        if font_size:
            formater.general_rule.font_size = font_size
        if font_bold:
            formater.general_rule.font_bold = font_bold
        if font_italic:
            formater.general_rule.font_italic = font_italic

        text = ""
        count = 1
        list_indent = "● "
        list_item_indent = "• "
        add_indent = ""
        for idx, txt_slice in enumerate(text_slices):
            txt_slice: html_parser_cls.TextObject
            text_id = "#" + "-" * (6 - len(str(count))) + str(count)
            # text_val = self._remove_wiki_from_text(txt_slice.txt_value.replace("&#91;", "[").replace("&#93;", "]")) + " "
            text_val = self._remove_wiki_from_text(HtmlLib.unescape(txt_slice.txt_value)) + " "

            # Indent list items
            add_indent = ""
            text_slice_tags = txt_slice.get_tag()
            if "<ul" in text_slice_tags or "<ol" in text_slice_tags:
                indent_string = list_indent * text_slice_tags.count("<ul") + list_indent * text_slice_tags.count("<ol") + list_item_indent * text_slice_tags.count("<li")
                if idx < len(text_slices) - 1:
                    next_txt_obj = text_slices[idx+1]
                    if not txt_slice.compare_are_objects_in_same_tag(tag="li", compare_with=next_txt_obj):
                        text_val = text_val + "\n"
                if idx > 0:
                    prev_txt_obj = text_slices[idx-1]
                    if not txt_slice.compare_are_objects_in_same_tag(tag="li", compare_with=prev_txt_obj):
                        add_indent = indent_string
                else:
                    add_indent = indent_string

            text_link = ""
            if txt_slice.txt_link:
                text_link = self.fix_url(txt_slice.txt_link)

            rule = utility_cls.TextToHtmlRule(
                text=text_id,
                replace_with=text_val
            )
            if text_link:
                rule.link_href = self.fix_url(text_link)
                if "wikipedia.org" in rule.link_href:
                    rule.fg_color = "#aaffff"
                else:
                    rule.fg_color = "#eab8ff"
            
            txt_slice_tags = txt_slice.get_tag()
            if "<strong" in txt_slice_tags or "<b>" in txt_slice_tags or "<dt>" in txt_slice_tags:
                rule.font_bold = True
            if "<i>" in txt_slice_tags:
                rule.font_italic = True
            
            if "<span" in txt_slice_tags:
                style = self.html_parser.get_tag_property_value(html_code=txt_slice_tags, tag="span", tag_property="style")
                if "font-style:italic" in style:
                    rule.font_italic = True
                if "background-color:" in style:
                    pos = style.find("background-color:")
                    color_start = style.find(":", pos) + 1
                    if color_start:
                        color_end = style.find(";", color_start)
                        color = style[color_start:color_end]
                        rule.fg_color = color
            
            formater.add_rule(rule)
            count += 1
            if add_indent:
                text_id_indent = "#I" + "-" * (6 - len(str(count))) + str(count)
                rule_indent = utility_cls.TextToHtmlRule(
                    text=text_id_indent,
                    replace_with=add_indent,
                    fg_color=self.wiki_frame_settings.wiki_info_indent_fg_color
                )
                formater.add_rule(rule_indent)

            text += text_id
        
        formater.set_text(text)
        return formater.get_html()

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result


class WikipediaCard(QFrame):
    signal_size_changed = pyqtSignal(QSize, str)

    def __init__(self, parent_widget, settings: settings_cls.Settings, url: str, card_setting: dict = None, card_id: str = None):
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
        self.url = url
        self.card_id = card_id
        self.card_setting = card_setting
        self.wiki_frame_settings = WikiFrameSettings(self.card_setting)

        self.external_feedback_click_function = None
        self._set_external_click_function(self.wiki_frame_settings)

        self.pages = []
        self.current_page_index = 0

        self.current_content_index = 0

        self.size_without_content_frame = 0

        # Define widgets
        self._define_widgets()

        self.add_page(self.url)

        # Connect events with slots
        self.lbl_prev_page.mousePressEvent = self.lbl_prev_page_click
        self.lbl_next_page.mousePressEvent = self.lbl_next_page_click
        self.lbl_pic.mousePressEvent = self.lbl_pic_click

        UTILS.LogHandler.add_log_record("#1: Card frame started.", ["WikipediaCard"])

    def lbl_pic_click(self, e: QMouseEvent):
        self.lbl_pic.setVisible(False)

    def lbl_prev_page_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.prev_page()
        QLabel.mousePressEvent(self.lbl_prev_page, e)

    def lbl_next_page_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.next_page()
        QLabel.mousePressEvent(self.lbl_next_page, e)

    def loading_page(self, value: bool):
        if value:
            self.lbl_loading.raise_()
            self.lbl_loading.setVisible(True)
            self.lbl_prev_page.setVisible(False)
            self.lbl_next_page.setVisible(False)
            QCoreApplication.processEvents()
        else:
            self.lbl_loading.setVisible(False)
            self.lbl_prev_page.setVisible(True)
            self.lbl_next_page.setVisible(True)
            self._setup_navigation_buttons_status()
            QCoreApplication.processEvents()
    
    def add_page(self, url: str):
        self.loading_page(True)
        for idx, item in enumerate(self.pages):
            item: WikiData
            if item.url == url:
                poped_item = self.pages.pop(idx)
                self.pages.append(poped_item)
                self.current_page_index = len(self.pages) - 1
                self.update_card()
                self.loading_page(False)
                return
        
        while len(self.pages) > self.current_page_index + 1:
            self.pages.pop()

        data = WikiData(url=url, wiki_frame_settings=self.wiki_frame_settings)
        if data.has_page:
            self.pages.append(data)
            self.current_page_index = len(self.pages) - 1
            self.update_card()
        self.loading_page(False)

    def size_changed(self):
        if self.wiki_frame_settings.wiki_size_changed_feedback:
            self.wiki_frame_settings.wiki_size_changed_feedback(self.size())
        self.signal_size_changed.emit(self.size(), self.card_id)

    def prev_page(self):
        if self.current_page_index <= 0:
            return
        
        self.current_page_index -= 1
        self.update_card()
    
    def next_page(self):
        if self.current_page_index >= len(self.pages) - 1:
            return
        
        self.current_page_index += 1
        self.update_card()

    def _setup_navigation_buttons_status(self):
        self.lbl_prev_page.setEnabled(self.current_page_index > 0)
        self.lbl_next_page.setEnabled(self.current_page_index < len(self.pages)-1)
        prev_tt = ""
        next_tt = ""
        for idx, item in enumerate(self.pages):
            item: WikiData
            if idx < self.current_page_index:
                if item.has_page:
                    prev_tt += item.data_title["text"] + "\n"
            elif idx > self.current_page_index:
                if item.has_page:
                    next_tt += item.data_title["text"] + "\n"
        self.lbl_prev_page.setToolTip(prev_tt.strip())
        self.lbl_next_page.setToolTip(next_tt.strip())

    def _reset_widgets(self):
        protected_widgets = [
            self.lbl_loading,
            self.lbl_prev_page,
            self.lbl_next_page,
            self.lbl_pic,
            self.frm_toc,
            self.frm_content
        ]
        for item in self.children():
            if item not in protected_widgets:
                item.deleteLater()
        QCoreApplication.processEvents()

    def refresh_card(self):
        self.add_page(self.pages[self.current_page_index].url)
        # self.parent_widget.resize(self.width(), self.height() + 20)

    def update_card(self):
        # Set main frame
        self.loading_page(True)
        self._reset_widgets()
        sett = self.wiki_frame_settings
        style = f'color: {sett.wiki_fg_color}; background-color: {sett.wiki_bg_color};'
        self.setStyleSheet(style)

        # Set variables
        data: WikiData = self.pages[self.current_page_index]
        self._define_frame(self, self.wiki_frame_settings.wiki_has_border)
        y = sett.wiki_info_padding_ver

        # Info frame
        frm_info: QFrame = self._get_info_frame(data)
        frm_info.move(sett.wiki_info_padding_hor, sett.wiki_info_padding_ver)
        if frm_info.width():
            frm_info.show()
        frm_info_h = frm_info.pos().y() + frm_info.height()

        # Title
        title_width = sett.wiki_width - (frm_info.pos().x() + frm_info.width() + sett.wiki_info_spacing_hor + sett.wiki_info_padding_hor)
        frm_title: QFrame = self._get_title_frame(data, w=title_width)
        frm_title.move(frm_info.pos().x() + frm_info.width() + sett.wiki_info_spacing_hor, y)
        self.frm_toc.move(frm_title.pos().x() + sett.wiki_info_padding_hor, frm_title.pos().y() + frm_title.height() - sett.wiki_info_padding_ver - self.frm_toc.height())
        frm_title.show()
        frm_title_h = frm_title.pos().y() + frm_title.height()
        y = frm_title_h + sett.wiki_info_spacing_ver

        # Content frame
        content_width = sett.wiki_width - (frm_info.pos().x() + frm_info.width() + sett.wiki_info_spacing_hor) - sett.wiki_info_padding_hor
        if data.data_content:
            content_data = data.data_content[0]
        else:
            content_data = {}
        self.frm_content.resize(content_width, self.frm_content.height())
        frm_content: QFrame = self._update_content_frame(content_data, w=content_width)
        frm_content.move(frm_info.pos().x() + frm_info.width() + sett.wiki_info_spacing_hor, y)
        frm_content.show()
        frm_content_h = frm_content.pos().y() + frm_content.height()

        w = sett.wiki_width
        h = max(frm_info_h, frm_title_h, self.frm_toc.pos().y() + int(self.frm_toc.objectName()) + sett.wiki_info_padding_ver)
        h += sett.wiki_info_padding_ver
        self.size_without_content_frame = h
        h = max(h, frm_content_h + sett.wiki_info_padding_ver)
        self.resize(w, h)
        for item in self.children():
            if isinstance(item, QLabel):
                item.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.size_changed()
        self.frm_toc.raise_()
        # Raise combobox widgets if content frame is to wide
        self.frm_content.raise_()
        self.lbl_prev_page.raise_()
        self.lbl_next_page.raise_()
        self.loading_page(False)

    def _get_title_frame(self, data: WikiData, w: int) -> QFrame:
        sett = self.wiki_frame_settings

        # Title Frame
        frm_title = QFrame(self)
        self._define_frame(frm_title)
        style = f"color: {sett.wiki_title_fg_color}; background-color: {sett.wiki_title_bg_color};"
        frm_title.setStyleSheet(style)
        
        y = sett.wiki_info_padding_ver
        x = sett.wiki_info_padding_hor

        # Label Title
        lbl_title = QLabel(frm_title)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        font = lbl_title.font()
        font.setPointSize(sett.wiki_title_font_size)
        font.setBold(sett.wiki_title_font_bold)
        lbl_title.setFont(font)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setText(data.data_title["text"])
        lbl_title.adjustSize()
        lbl_title.move(x, y)
        lbl_title.resize(w, lbl_title.height())
        y += lbl_title.height() + sett.wiki_info_spacing_ver

        # Link to wikipedia
        url = self.pages[self.current_page_index].url
        lbl_link = QLabel(frm_title)
        lbl_link.setTextInteractionFlags(lbl_link.textInteractionFlags()|Qt.TextSelectableByMouse)
        font = lbl_link.font()
        font.setPointSize(10)
        lbl_link.setFont(font)
        lbl_link.setAlignment(Qt.AlignCenter)
        lbl_link.setStyleSheet("QLabel {color: #ababab; background-color: rgba(0,0,0,0);} QLabel:hover {color: #aaffff;}")
        lbl_link.mousePressEvent = lambda _, link_val=url: self.open_external_link(link_val)
        lbl_link.setText(self.getl("wiki_title_open_in_browser_text"))
        lbl_link.setToolTip(url)
        lbl_link.adjustSize()
        lbl_link.move(x, sett.wiki_info_padding_ver)

        # Languages
        cmb_lang = self._get_combo_list(parent_widget=frm_title, data=data.data_languages)
        cmb_lang.setToolTip(self.getl("wiki_cmb_languages"))
        lang_x = w - sett.wiki_info_padding_hor - cmb_lang.width()
        if lang_x < 0:
            lang_x = 0

        # Alphabets
        cmb_alphabet = self._get_combo_list(parent_widget=frm_title, data=data.data_alphabet)
        cmb_alphabet.setToolTip(self.getl("wiki_cmb_alphabets"))
        alphabet_x = lang_x - sett.wiki_info_spacing_hor - cmb_alphabet.width()
        if alphabet_x < 0:
            alphabet_x = 0
        
        # TOC Frame
        frm_toc = self._get_toc_frame(data=data)

        y += frm_toc.height() + sett.wiki_info_padding_ver
        cmb_lang.move(lang_x, y - sett.wiki_info_padding_ver - cmb_lang.height())
        cmb_alphabet.move(alphabet_x, y - sett.wiki_info_padding_ver - cmb_alphabet.height())
        # Set frame size
        frm_title.resize(w, y)
        # Return title frame
        return frm_title

    def _get_combo_list(self, parent_widget: QFrame, data: list) -> QComboBox:
        cmb = QComboBox(parent_widget)
        cmb.setFrame(False)
        cmb.setFont(QFont("Arial", 12))
        for item in data["list"]:
            text = item["text"]
            link = item["link"]
            cmb.addItem(text, link)
        
        if data["selected"]:
            cmb.setCurrentText(data["selected"])
        else:
            if data["title"]:
                cmb.insertItem(0, data["title"], "")
                cmb.setCurrentText(data["title"])
        
        cmb.adjustSize()

        cmb.currentTextChanged.connect(lambda : self.link_clicked(cmb.currentData()))
        return cmb
            
    def _get_toc_frame(self, data: WikiData) -> QFrame:
        sett = self.wiki_frame_settings

        # Delete children to reset toc frame
        for child in self.frm_toc.children():
            child.deleteLater()
        QCoreApplication.processEvents()

        # Frame
        self.frm_toc.setLineWidth(0)
        style = f"color: {sett.wiki_content_toc_fg_color}; background-color: {sett.wiki_title_bg_color};"
        self.frm_toc.setStyleSheet(style)
        
        y = sett.wiki_info_padding_ver
        x = sett.wiki_info_padding_hor

        # Title
        lbl_title = QLabel(self.frm_toc)
        lbl_title.setCursor(Qt.PointingHandCursor)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        font = lbl_title.font()
        font.setPointSize(sett.wiki_content_toc_font_size)
        font.setBold(sett.wiki_content_toc_font_bold)
        font.setUnderline(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("QLabel:hover {color: #aaff00;}")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setText(self.getl("wiki_card_toc_text"))
        lbl_title.adjustSize()
        lbl_title.move(x, y)
        y += lbl_title.height() + 5

        small_frame_h = y

        # Line
        line = QFrame(self.frm_toc)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.move(x, y)
        y += line.height() + 5
        y += sett.wiki_info_padding_ver

        x += 15

        max_w = lbl_title.width()
        style = "QLabel:hover {" + f"background-color: {sett.wiki_content_toc_hover_color};" + "}"

        items_list = []

        for idx, item in enumerate(data.data_content):
            lbl = QLabel(self.frm_toc)
            lbl.setTextInteractionFlags(lbl.textInteractionFlags()|Qt.TextSelectableByMouse)
            if item["data"]:
                lbl.setCursor(Qt.PointingHandCursor)
                lbl.setStyleSheet(style)
                lbl.setText("‣ " + item["text"])
            else:
                lbl.setStyleSheet(f"color: {sett.wiki_label_header_fg_color}")
                lbl.setAlignment(Qt.AlignCenter)
                font = lbl.font()
                font.setItalic(True)
                lbl.setFont(font)
                lbl.setText("- " + item["text"] + " -")
            lbl.adjustSize()
            lbl.move(x, y)
            y += lbl.height() + sett.wiki_info_spacing_ver
            max_w = max(max_w, lbl.width())
            items_list.append([lbl, idx])
        
        lbl_title.show()
        line.show()
        for item in items_list:
            item[0].resize(max_w, item[0].height())
            item[0].show()

        max_w += x + sett.wiki_info_padding_hor
        y += sett.wiki_info_padding_ver
        line.resize(max_w - sett.wiki_info_padding_hor*2, line.height())
        self.frm_toc.resize(max_w, small_frame_h)

        toggle = (small_frame_h, y)
        lbl_title.mousePressEvent = lambda e, size_toggle=toggle: self._toc_frame_click(e, size_toggle)
        self.frm_toc.leaveEvent = lambda _, size=small_frame_h: self._toc_minimize_size(size)
        for item in items_list:
            idx = item[1]
            item[0].mousePressEvent = lambda e, idx=idx, toggle=toggle: self._toc_item_click(e, idx, toggle)

        self.frm_toc.setObjectName(str(y))

        return self.frm_toc

    def _toc_item_click(self, e: QMouseEvent = None, idx: int = None, size_toggle: tuple = None):
        if e and e.button() != Qt.LeftButton:
            return

        if isinstance(idx, str):
            idx = int(idx[:idx.find(" ")])
        
        data = self.pages[self.current_page_index].data_content[idx]
        if not data["data"]:
            return

        if size_toggle:
            self._toc_minimize_size(size_toggle[0])
        
        self._update_content_frame(data, data_index=idx)
    
    def _toc_minimize_size(self, size: int):
        sett = self.wiki_frame_settings
        self.frm_toc.resize(self.frm_toc.width(), size)
        self.frm_toc.setLineWidth(0)
        style = f"color: {sett.wiki_content_toc_fg_color}; background-color: {sett.wiki_title_bg_color};"
        self.frm_toc.setStyleSheet(style)

    def _toc_frame_click(self, e: QMouseEvent, size_toggle: tuple):
        sett = self.wiki_frame_settings
        self.frm_toc.raise_()
        if e.button() == Qt.LeftButton:
            if self.frm_toc.height() == size_toggle[0]:
                self.frm_toc.resize(self.frm_toc.width(), size_toggle[1])
                if sett.wiki_content_toc_has_border:
                    self.frm_toc.setLineWidth(1)
                style = f"color: {sett.wiki_content_toc_fg_color}; background-color: {sett.wiki_content_toc_bg_color};"
                self.frm_toc.setStyleSheet(style)
            else:
                self._toc_minimize_size(size_toggle[0])

    def _update_content_frame(self, data: dict, w: int = None, data_index: int = 0) -> QFrame:
        loading_status = self.lbl_loading.isVisible()
        self.loading_page(True)
        if w is None:
            w = self.frm_content.width()

        self.frm_content.resize(w, 0)
        if not data:
            return self.frm_content
        
        sett = self.wiki_frame_settings

        # Delete children to reset content frame
        for child in self.frm_content.children():
            child.deleteLater()
        QCoreApplication.processEvents()

        style = f"color: {sett.wiki_content_text_fg_color}; background-color: {sett.wiki_content_text_bg_color};"
        self.frm_content.setStyleSheet(style)
        font = self.frm_content.font()
        font.setPointSize(sett.wiki_content_text_font_size)
        self.frm_content.setFont(font)

        x = sett.wiki_info_padding_hor
        y = sett.wiki_info_padding_ver
        max_w = w - sett.wiki_info_padding_hor*2

        # Title
        lbl_title: QLabel = self._get_content_frame_lbl_title(data["text"], data_index=data_index, w=max_w)
        lbl_title.move(x, y)
        lbl_title.resize(max_w, lbl_title.height())
        lbl_title.show()
        y += lbl_title.height() + 3
        
        # Line
        line: QFrame = self._get_content_frame_title_line()
        line.move(x, y)
        line.resize(max_w, 3)
        line.show()
        y += line.height() + sett.wiki_info_spacing_ver

        l_rect = QRect(x, y, 0, 0)
        r_rect = QRect(x, y, 0, 0)
        max_h = 0

        for item in data["data"]:
            if item["type"] == "c_text":
                obj: QLabel = self._get_content_frame_text_item(item)
            
            if item["type"] == "c_table":
                obj: QTableWidget = self._get_content_frame_table_item(item)
            
            if item["type"] == "c_table_presentation":
                obj: QFrame = self._get_content_frame_table_presentation_item(item)

            if item["type"] == "c_list":
                obj: QFrame = self._get_content_frame_list_item(item)
            
            if item["type"] == "c_dl":
                obj: QFrame = self._get_content_frame_list_item(item)

            if item["type"] == "c_figure":
                obj: QFrame = self._get_content_frame_figure_item(item)

            if item["type"] == "c_code":
                obj: QFrame = self._get_content_frame_code_snippet_item(item)

            self._position_content_frame_item_to_next_position(l_rect=l_rect, r_rect=r_rect, obj=obj, max_w=max_w)
            max_h = max(max_h, obj.pos().y() + obj.height())
            obj.show()

        y = max(l_rect.bottom(), r_rect.bottom(), max_h)
        y += sett.wiki_info_padding_ver
        self.frm_content.resize(self.frm_content.width(), y)
        self.resize(self.width(), max(self.size_without_content_frame, self.frm_content.pos().y() + self.frm_content.height() + sett.wiki_info_padding_ver))
        self.size_changed()
        self.loading_page(loading_status)
        return self.frm_content

    def _position_content_frame_item_to_next_position(self, l_rect: QRect, r_rect: QRect, obj: QWidget, max_w: int) -> QPoint:
        space_hor = self.wiki_frame_settings.wiki_info_spacing_hor
        space_ver = self.wiki_frame_settings.wiki_info_spacing_ver
        min_w = 200
        tolerance = 200
        text_type = isinstance(obj, QLabel)

        if text_type:
            # Case: right is lower than left
            if r_rect.bottom() >= l_rect.bottom():
                l_rect.setBottom(r_rect.bottom() + space_ver)
                x = l_rect.left()
                y = r_rect.bottom()
                obj.setFixedWidth(max_w)
                obj.adjustSize()
                obj.move(x, y)
                l_rect.setBottom(r_rect.bottom() + obj.height())
                l_rect.setWidth(max_w)
                r_rect.setBottom(l_rect.bottom())
                return
            
            # Case: left is lower than right
            ava_w = max_w - l_rect.right()
            if ava_w > min_w:
                # Resize QLabel and try to fit on right side
                x = l_rect.right()
                y = r_rect.bottom()
                obj.setFixedWidth(ava_w)
                obj.adjustSize()
                
                if obj.height() < (l_rect.bottom() + tolerance) - r_rect.bottom():
                    r_rect.setBottom(r_rect.bottom() + space_ver)
                    obj.move(l_rect.right(), r_rect.bottom())
                    r_rect.setBottom(r_rect.bottom() + obj.height())
                    return

            # Resize QLabel and expand it on full width
            l_rect.setBottom(l_rect.bottom() + space_ver)
            obj.move(l_rect.left(), l_rect.bottom())
            obj.setFixedWidth(max_w)
            obj.adjustSize()
            l_rect.setBottom(l_rect.bottom() + obj.height())
            l_rect.setWidth(max_w)
            r_rect.setBottom(l_rect.bottom())
            return

        # Line up left side
        if l_rect.bottom() < r_rect.bottom():
            l_rect.setBottom(r_rect.bottom())
        
        if l_rect.right() + obj.width() <= max_w and r_rect.bottom() + obj.height() < l_rect.bottom() + tolerance:
            # Case: Object fits on right side
            obj.move(l_rect.right(), r_rect.bottom())
            l_rect.setRight(l_rect.right() + obj.width() + space_hor)
            l_rect.setBottom(max(r_rect.bottom() + obj.height(), l_rect.bottom()))
            return
        
        # Place object in new line at beginning
        l_rect.setBottom(l_rect.bottom() + space_ver)
        obj.move(l_rect.left(), l_rect.bottom())
        r_rect.setBottom(l_rect.bottom())
        l_rect.setWidth(obj.width() + space_hor)
        l_rect.setBottom(l_rect.bottom() + obj.height())
        return

    def _get_content_frame_text_item(self, data: dict) -> QLabel:
        lbl_text = QLabel(self.frm_content)
        lbl_text.setTextInteractionFlags(lbl_text.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_text.linkActivated.connect(lambda url: self.link_clicked(url))
        lbl_text.linkHovered.connect(lambda url: self.link_hovered(url))
        lbl_text.setWordWrap(True)
        font = lbl_text.font()
        font.setPointSize(self.wiki_frame_settings.wiki_content_text_font_size)
        lbl_text.setFont(font)
        lbl_text.setText(data["text"])
        return lbl_text

    def _get_content_frame_table_presentation_item(self, data: dict) -> QFrame:
        frm = QFrame(self.frm_content)
        self._define_frame(frm)
        x = self.wiki_frame_settings.wiki_info_spacing_hor
        y = 0
        w = self.frm_content.width() - self.wiki_frame_settings.wiki_info_padding_hor * 2 - x * 2
        font = frm.font()
        font.setPointSize(self.wiki_frame_settings.wiki_content_list_font_size)
        max_w = w

        lbl_pic = QLabel(frm)
        lbl_pic.setAlignment(Qt.AlignCenter)
        img_w = data["image_w"] if data["image_w"] else 30
        img_h = data["image_h"] if data["image_h"] else 30
        lbl_pic.resize(img_w, img_h)
        lbl_pic.move(x, y)
        self.set_image_to_label(image_data=data["image"], label=lbl_pic)
        x += lbl_pic.width() + self.wiki_frame_settings.wiki_info_spacing_hor
        max_w -= lbl_pic.width() + self.wiki_frame_settings.wiki_info_spacing_hor

        lbl_desc = QLabel(frm)
        lbl_desc.setFont(font)
        lbl_desc.setWordWrap(True)
        lbl_desc.setText(data["text"])
        lbl_desc.setFixedWidth(max_w)
        lbl_desc.adjustSize()
        lbl_desc.move(x, y)
        lbl_desc.setTextInteractionFlags(lbl_desc.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_desc.linkActivated.connect(lambda url: self.link_clicked(url))
        lbl_desc.linkHovered.connect(lambda url: self.link_hovered(url))

        y = max(lbl_pic.height(), lbl_desc.height())

        frm.resize(w, y)
        return frm

    def _get_content_frame_table_item(self, data: dict) -> QTableWidget:
        if data["labels"]:
            return self._get_figure_frame(data["labels"], parent_widget=self.frm_content)
        
        html_parser = html_parser_cls.HtmlParser()
        font_size = self.wiki_frame_settings.wiki_content_text_font_size - 8
        if font_size < 12:
            font_size = 12
        table_width = self.frm_content.width() - self.wiki_frame_settings.wiki_info_padding_hor * 2

        return html_parser.get_PYQT5_table_ver2(html_code=data["code"],
                                                parent_widget=self.frm_content,
                                                font_size=font_size,
                                                max_table_width=table_width,
                                                fix_url_function=self.fix_url,
                                                text_link_feedback=self.link_clicked,
                                                image_link_feedback=self.image_link_clicked)

    def _get_content_frame_list_item(self, data: dict) -> QFrame:
        frm = QFrame(self.frm_content)
        self._define_frame(frm)
        x = self.wiki_frame_settings.wiki_info_spacing_hor
        y = 0
        w = self.frm_content.width() - self.wiki_frame_settings.wiki_info_padding_hor * 2 - x * 2
        font = frm.font()
        font.setPointSize(self.wiki_frame_settings.wiki_content_list_font_size)
        max_w = w

        if data.get("image", None) and data["type"] == "c_dl":
            lbl = QLabel(frm)
            fm = QFontMetrics(font)
            font_h = fm.height() / 2
            img_w = data["image"]["width"]
            if not img_w:
                img_w = int(data["image"]["width_ex"] * font_h)
                if not img_w:
                    frm.resize(0, 0)
                    return frm
            img_h = data["image"]["height"]
            if not img_h:
                img_h = int(data["image"]["height_ex"] * font_h)
                if not img_h:
                    frm.resize(0, 0)
                    return frm
            if img_w > w:
                img_h = int(img_h * (w / img_w))
                img_w = w
            elif img_w < 30:
                img_h = int(img_h * (30 / img_w))
                img_w = 30
            lbl.resize(img_w, img_h)
            lbl.setStyleSheet(f"background-color: {self.wiki_frame_settings.wiki_content_list_dl_bg_color};")
            self.set_image_to_label(data["image"]["src"], lbl, strech_to_label=True)
            lbl.move(x, y)
            y += lbl.height()
            frm.resize(max_w + x, y)
            return frm

        for item in data["text_list"]:
            lbl = QLabel(frm)
            lbl.setTextInteractionFlags(lbl.textInteractionFlags()|Qt.TextSelectableByMouse)
            lbl.linkActivated.connect(lambda url: self.link_clicked(url))
            lbl.linkHovered.connect(lambda url: self.link_hovered(url))
            lbl.setWordWrap(True)
            lbl.setFont(font)
            lbl.setStyleSheet(f"color: {self.wiki_frame_settings.wiki_content_list_fg_color};")
            lbl.setText(item)
            lbl.move(x, y)
            lbl.setFixedWidth(max_w)
            lbl.adjustSize()
            y += lbl.height()
        
        frm.resize(max_w + x, y)
        return frm

    def _get_content_frame_figure_item(self, data: dict) -> QFrame:
        sett = self.wiki_frame_settings

        frm = QFrame(self.frm_content)
        self._define_frame(frm)
        if not data["image"] and not data["text"]:
            frm.resize(0, 0)
            return frm
        
        frm.setStyleSheet(f"background-color: {sett.wiki_figure_bg_color};")
        x = sett.wiki_info_spacing_hor
        y = sett.wiki_info_spacing_ver
        max_w = sett.wiki_figure_width - sett.wiki_info_spacing_hor * 2

        # Image
        lbl_pic = QLabel(frm)
        lbl_pic.setAlignment(Qt.AlignCenter)
        lbl_pic.resize(max_w, 0)
        if data["image"]:
            if data["image_w"] and data["image_h"]:
                max_w = int(data["image_w"])
                lbl_pic.resize(int(data["image_w"]), int(data["image_h"]))
                self.set_image_to_label(data["image"], lbl_pic)
            else:
                self.set_image_to_label(data["image"], lbl_pic, resize_label_fixed_w=True)
        lbl_pic.move(x, y)
        if data["image_link"]:
            lbl_pic.mousePressEvent = lambda _, link_val=data["image_link"]: self.image_link_clicked(link_val)
            lbl_pic.setCursor(Qt.PointingHandCursor)
        y += lbl_pic.height()
        
        # Description
        lbl_desc = QLabel(frm)
        lbl_desc.setTextInteractionFlags(lbl_desc.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_desc.linkActivated.connect(lambda url: self.link_clicked(url))
        lbl_desc.linkHovered.connect(lambda url: self.link_hovered(url))
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setText(data["text"])
        lbl_desc.move(x, y)
        lbl_desc.setFixedWidth(max_w)
        lbl_desc.adjustSize()
        y += lbl_desc.height()

        frm.resize(max_w + sett.wiki_info_spacing_hor * 2, y + sett.wiki_info_spacing_ver)

        return frm

    def _get_content_frame_code_snippet_item(self, data: dict) -> QFrame:
        sett = self.wiki_frame_settings
        w = self.frm_content.width() - sett.wiki_info_padding_hor * 2

        frm = QFrame(self.frm_content)
        self._define_frame(frm)
        frm.setStyleSheet(f"color: {sett.wiki_content_code_fg_color}; background-color: {sett.wiki_content_code_bg_color};")
        x = 0
        y = 0

        # Title
        lbl_title = QLabel(frm)
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_title.setText(data["title"].strip().capitalize() + ":")
        font = lbl_title.font()
        
        font.setFamily("Source Code Pro")
        font.setPointSize(sett.wiki_content_code_title_font_size)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet(f"color: {sett.wiki_content_code_title_fg_color}; background-color: {sett.wiki_content_code_title_bg_color};")
        lbl_title.adjustSize()
        lbl_title.move(x, y)
        lbl_title.resize(w, lbl_title.height())
        y += lbl_title.height()

        # Code
        lbl_code = QLabel(frm)
        lbl_code.setTextInteractionFlags(lbl_code.textInteractionFlags()|Qt.TextSelectableByMouse)
        lbl_code.setWordWrap(True)
        font.setPointSize(sett.wiki_content_code_font_size)
        lbl_code.setFont(font)
        lbl_code.setStyleSheet(f"color: {sett.wiki_content_code_fg_color}; background-color: {sett.wiki_content_code_bg_color};")
        lbl_code.setText(HtmlLib.unescape(data["text"]))
        lbl_code.move(x, y)
        lbl_code.setFixedWidth(w)
        lbl_code.adjustSize()
        y += lbl_code.height()

        frm.resize(w, y + sett.wiki_info_spacing_ver)
        return frm

    def _get_content_frame_lbl_title(self, text: str, data_index: int = 0, w: int = None) -> QLabel:
        lbl = QLabel(self.frm_content)
        font = lbl.font()
        font.setPointSize(self.wiki_frame_settings.wiki_content_text_font_size + 4)
        lbl.setFont(font)
        lbl.setStyleSheet(f"color: {self.wiki_frame_settings.wiki_content_text_title_fg_color};")
        label_text = "#--3  " + self.raw_text(text) + "      #--1 #--2"

        # Add navigation
        max_index = len(self.pages[self.current_page_index].data_content) - 1
        
        nav_left_index = None
        for i in range(data_index - 1, -1, -1):
            if self.pages[self.current_page_index].data_content[i]["data"]:
                nav_left_index = i
                break
        if nav_left_index is not None and nav_left_index < 0:
            nav_left_index = None

        nav_right_index = None
        for i in range(data_index + 1, max_index + 1):
            if self.pages[self.current_page_index].data_content[i]["data"]:
                nav_right_index = i
                break
        if nav_right_index is not None and nav_right_index > max_index:
            nav_right_index = None

        html_parser = html_parser_cls.HtmlParser()

        nav_left_text = "⇦"
        nav_right_text = "⇨"
        nav_left_link = f"{str(nav_left_index)} {html_parser.get_raw_text(load_html_code=self.pages[self.current_page_index].data_content[nav_left_index]['text'])}" if nav_left_index is not None else None
        nav_right_link = f"{str(nav_right_index)} {html_parser.get_raw_text(load_html_code=self.pages[self.current_page_index].data_content[nav_right_index]['text'])}" if nav_right_index is not None else None
        nav_left_fg_color = "#aaff00" if nav_left_index is not None else "#b1b1b1"
        nav_right_fg_color = "#aaff00" if nav_right_index is not None else "#b1b1b1"
        
        text_to_html = utility_cls.TextToHTML(text=label_text)
        text_to_html.general_rule.fg_color = self.wiki_frame_settings.wiki_content_text_title_fg_color
        text_to_html.general_rule.font_size = self.wiki_frame_settings.wiki_content_text_font_size + 4
        
        # Left
        rule_left = utility_cls.TextToHtmlRule(
            text="#--1",
            replace_with=nav_left_text,
            fg_color=nav_left_fg_color
        )
        if nav_left_link:
            rule_left.link_href = nav_left_link
        text_to_html.add_rule(rule_left)
        
        # Right
        rule_right = utility_cls.TextToHtmlRule(
            text="#--2",
            replace_with=nav_right_text,
            fg_color=nav_right_fg_color
        )
        if nav_right_link:
            rule_right.link_href = nav_right_link
        text_to_html.add_rule(rule_right)

        # Delimiter
        rule_delim = utility_cls.TextToHtmlRule(
            text="#--3",
            replace_with=" 🌟",
            fg_color="#ffff00"
        )
        text_to_html.add_rule(rule_delim)

        label_text = text_to_html.get_html()
        lbl.setText(label_text)

        if w:
            lbl.setFixedWidth(w)
        lbl.setWordWrap(True)
        lbl.adjustSize()

        lbl.linkActivated.connect(lambda url: self._toc_item_click(idx=url))
        lbl.linkHovered.connect(lambda url: self.link_hovered(url))

        
        
        return lbl

    def _get_content_frame_title_line(self) -> QFrame:
        line = QFrame(self.frm_content)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        return line

    def raw_text(self, text: str) -> str:
        parser = html_parser_cls.HtmlParser(text)
        return parser.get_raw_text().strip()

    def _get_info_frame(self, data: WikiData) -> QFrame:
        result = self._get_figure_frame(figure_data=data.data_labels)
        return result

    def _get_figure_frame(self, figure_data: list, parent_widget: QWidget = None) -> QFrame:
        sett = self.wiki_frame_settings
        # Info Frame
        if parent_widget:
            frm_info = QFrame(parent_widget)
        else:
            frm_info = QFrame(self)
        self._define_frame(frm_info, has_border=sett.wiki_info_has_border)
        if sett.wiki_info_bg_color:
            frm_info.setStyleSheet(f"background-color: {sett.wiki_info_bg_color};")
        frm_info.resize(sett.wiki_info_width, 20)

        if not figure_data:
            frm_info.resize(0, 0)
            return frm_info

        # Content
        y = sett.wiki_info_padding_ver
        w = sett.wiki_info_width - sett.wiki_info_padding_hor * 2

        if sett.wiki_info_category_value_ratio == 0:
            sett.wiki_info_category_value_ratio = 1
        if sett.wiki_info_category_value_ratio <= 1:
            w_half_value = int((w - sett.wiki_info_spacing_hor) * sett.wiki_info_category_value_ratio)
            w_half_name = int((w - sett.wiki_info_spacing_hor) - w_half_value)
        else:
            w_half_value = int((w - sett.wiki_info_spacing_hor) / sett.wiki_info_category_value_ratio)
            w_half_name = int((w - sett.wiki_info_spacing_hor) - w_half_value)
        
        x = sett.wiki_info_padding_hor
        x_val = sett.wiki_info_padding_hor + w_half_name + sett.wiki_info_spacing_hor
        for item in figure_data:
            if item["image"]:
                if len(item["image"]) > 1:
                    w_array = [x["image_w"] for x in item["image"]]
                    if 0 in w_array:
                        w_array = [int((w - sett.wiki_info_spacing_hor)/2) for x in item["image"]]
                    else:
                        has1 = None
                        for i in range(len(w_array)):
                            if has1:
                                w_array[i] = (w - sett.wiki_info_spacing_hor) - has1
                                has1 = None
                            else:
                                if i < len(w_array) - 1:
                                    total_w = w_array[i] + w_array[i+1]
                                    has1 = int((w_array[i] / total_w) * (w - sett.wiki_info_spacing_hor))
                                    w_array[i] = has1
                                else:
                                    w_array[i] = w - sett.wiki_info_spacing_hor

                    image_x = 0
                    max_image_height = 0
                    for idx, image_item in enumerate(item["image"]):
                        lbl_pic = QLabel(frm_info)
                        lbl_pic.setStyleSheet("background-color: rgba(0,0,0,0);")
                        if image_item["link"]:
                            lbl_pic.setCursor(Qt.PointingHandCursor)
                            lbl_pic.mousePressEvent = lambda _, link_val=image_item["link"]: self.image_link_clicked(link_val)
                            lbl_pic.setToolTip(image_item["tt"])
                        lbl_pic.setAlignment(Qt.AlignCenter)
                        lbl_pic.move(x + image_x, y)
                        lbl_pic.resize(w_array[idx], 0)
                        self.set_image_to_label(image_item["src"], lbl_pic, resize_label_fixed_w=True)
                        lbl_pic.show()
                        max_image_height = max(max_image_height, lbl_pic.height())
                        if image_x:
                            image_x = 0
                            y += max_image_height + sett.wiki_info_spacing_hor
                            max_image_height = 0
                        else:
                            image_x += lbl_pic.width() + sett.wiki_info_spacing_hor
                    if image_x:
                        y += max_image_height + sett.wiki_info_spacing_ver
                    else:
                        y = y - sett.wiki_info_spacing_hor + sett.wiki_info_spacing_ver
                else:
                    image_item = item["image"][0]
                    lbl_pic = QLabel(frm_info)
                    lbl_pic.setStyleSheet("background-color: rgba(0,0,0,0);")
                    if image_item["link"]:
                        lbl_pic.setCursor(Qt.PointingHandCursor)
                        lbl_pic.mousePressEvent = lambda _, link_val=image_item["link"]: self.image_link_clicked(link_val)
                        lbl_pic.setToolTip(image_item["tt"])
                    lbl_pic.setAlignment(Qt.AlignCenter)
                    lbl_pic.move(x, y)
                    lbl_pic.resize(w, 0)
                    self.set_image_to_label(image_item["src"], lbl_pic, resize_label_fixed_w=True)
                    lbl_pic.show()
                    
                    if image_item["marker_image"]:
                        image_marker_item = image_item["marker_image"]
                        lbl_marker_pic = QLabel(frm_info)
                        lbl_marker_pic.setStyleSheet("background-color: rgba(0,0,0,0);")
                        lbl_marker_pic.setAlignment(Qt.AlignCenter)
                        marker_x = int(lbl_pic.pos().x() + lbl_pic.width()*image_marker_item["marker_left"]/100)
                        marker_y = int(lbl_pic.pos().y() + lbl_pic.height()*image_marker_item["marker_top"]/100)
                        lbl_marker_pic.move(marker_x, marker_y)
                        lbl_marker_pic.resize(image_marker_item["image_w"], image_marker_item["image_h"])
                        self.set_image_to_label(image_marker_item["src"], lbl_marker_pic)
                        lbl_marker_pic.show()

                    y += lbl_pic.height() + sett.wiki_info_spacing_ver
            
            if item["image_desc"]:
                lbl_text = QLabel(frm_info)
                lbl_text.setTextInteractionFlags(lbl_text.textInteractionFlags()|Qt.TextSelectableByMouse)
                lbl_text.linkActivated.connect(lambda url: self.link_clicked(url))
                lbl_text.linkHovered.connect(lambda url: self.link_hovered(url))
                lbl_text.setWordWrap(True)
                lbl_text.setAlignment(Qt.AlignCenter)
                lbl_text.move(x, y)
                lbl_text.setText(item["image_desc"])
                lbl_text.setFixedWidth(w)
                lbl_text.adjustSize()
                lbl_text.show()
                y += lbl_text.height() + sett.wiki_info_spacing_ver
            
            if item["name"] or item["value"]:
                max_h = 0
                y_tmp = y
                if item["name"]:
                    lbl_name = QLabel(frm_info)
                    lbl_name.setTextInteractionFlags(lbl_name.textInteractionFlags()|Qt.TextSelectableByMouse)
                    lbl_name.linkActivated.connect(lambda url: self.link_clicked(url))
                    lbl_name.linkHovered.connect(lambda url: self.link_hovered(url))
                    if item["type"] == "title":
                        lbl_name.setAlignment(Qt.AlignCenter)
                    else:
                        lbl_name.setAlignment(Qt.AlignLeft|Qt.AlignTop)
                    lbl_name.move(x, y_tmp)
                    lbl_name.setText(item["name"])
                    if item["colspan"] == 1:
                        lbl_name.setWordWrap(True)
                        if item["value"]:
                            lbl_name.setFixedWidth(w_half_name)
                        else:
                            lbl_name.setFixedWidth(w)
                        lbl_name.adjustSize()
                    else:
                        lbl_name.setAlignment(Qt.AlignCenter)
                        if item["type"] == "header":
                            lbl_name.setStyleSheet(f"background-color: {sett.wiki_label_header_bg_color};")
                        else:
                            lbl_name.setStyleSheet(f"background-color: {sett.wiki_label_section_title_bg_color};")

                        lbl_name.resize(w, lbl_name.height())
                        lbl_name.adjustSize()
                        lbl_name_true_w = lbl_name.width()
                        lbl_name.setWordWrap(True)
                        lbl_name.setFixedWidth(w)
                        lbl_name.adjustSize()

                        if item["icon"]:
                            lbl_icon = QLabel(frm_info)
                            lbl_icon.setAlignment(Qt.AlignCenter)
                            if item["icon"]["image_h"] and item["icon"]["image_w"] and item["icon"]["image_h"] <= lbl_name.height():
                                lbl_icon.resize(item["icon"]["image_w"], item["icon"]["image_h"])
                            else:
                                lbl_icon.resize(lbl_name.height(), lbl_name.height())
                            lbl_icon_x = int((w - lbl_name_true_w) / 2 - sett.wiki_info_spacing_hor)
                            if lbl_icon_x < 0:
                                lbl_icon_x = 0
                            lbl_icon.move(lbl_icon_x, y_tmp + int((lbl_name.height() - lbl_icon.height()) / 2))
                            lbl_icon.setStyleSheet("background-color: rgba(0,0,0,0);")
                            self.set_image_to_label(item["icon"]["src"], lbl_icon)
                            lbl_icon.show()

                        y_tmp = y + lbl_name.height() + sett.wiki_info_spacing_ver
                    lbl_name.show()
                    max_h = max(max_h, lbl_name.height())

                if item["value"]:
                    lbl_value = QLabel(frm_info)
                    lbl_value.setTextInteractionFlags(lbl_value.textInteractionFlags()|Qt.TextSelectableByMouse)
                    lbl_value.linkActivated.connect(lambda url: self.link_clicked(url))
                    lbl_value.linkHovered.connect(lambda url: self.link_hovered(url))
                    lbl_value.setWordWrap(True)
                    if item["type"] == "title":
                        lbl_value.setAlignment(Qt.AlignCenter)
                    lbl_value.setText(item["value"])
                    if item["colspan"] == 1:
                        if item["name"]:
                            lbl_value.move(x_val, y_tmp)
                            lbl_value.setFixedWidth(w_half_value)
                        else:
                            lbl_value.move(x, y_tmp)
                            lbl_value.setFixedWidth(w)
                        lbl_value.adjustSize()
                    else:
                        if item["type"] == "header":
                            lbl_value.setAlignment(Qt.AlignCenter)
                            lbl_value.setStyleSheet(f"background-color: {sett.wiki_label_header_bg_color};")
                        lbl_value.move(x, y_tmp)
                        lbl_value.setFixedWidth(w)
                        lbl_value.adjustSize()
                    lbl_value.show()
                    max_h = max(max_h, lbl_value.height() + (y_tmp - y))
                
                max_h += sett.wiki_info_spacing_ver
                y += max_h

                if item["audio"]:
                    y += sett.wiki_info_spacing_ver
                    mp_audio = MediaPlayer(self, item["audio"][0])
                    mp_audio.move(x, y)
                    mp_audio.resize(w, mp_audio.height())
                    mp_audio.show()
                    y += mp_audio.height() + sett.wiki_info_spacing_ver

        frm_info.resize(sett.wiki_info_width, y + sett.wiki_info_padding_ver * 2)
        return frm_info

    def set_image_to_label(self, image_data: str, label: QLabel, strech_to_label: bool = False, resize_label: bool = False, resize_label_fixed_w: bool = False, resize_label_fixed_h: bool = False) -> bool:
        if isinstance(image_data, str):
            image_url = image_data
            tt = ""
        elif isinstance(image_data, html_parser_cls.ImageObject):
            image_url = image_data.img_src
            tt = image_data.img_title
        else:
            return False

        if image_url.startswith("//"):
            image_url = "https:" + image_url

        img = None
        has_image = False
        try:
            img = None
            if not has_image:
                if os.path.isfile(image_url):
                    img = QPixmap()
                    has_image = img.load(os.path.abspath(image_url))
                else:
                    response = urllib.request.urlopen(image_url, timeout=2).read()
                    img = QPixmap()
                    has_image = img.loadFromData(response)
                    if not has_image:
                        response = requests.get(image_url, timeout=2)
                        has_image = img.loadFromData(response.content)
        except:
            img = None
        
        if tt:
            label.setToolTip(tt)

        if not has_image:
            return False
        
        if strech_to_label:
            label.setScaledContents(True)
        else:
            label.setScaledContents(False)
            if resize_label:
                scale = img.width() / img.height()
                if scale >= 1:
                    label.resize(int(label.height() * scale), label.height())
                else:
                    label.resize(label.width(), int(label.width() / scale))
            if resize_label_fixed_w:
                scale = img.height() / img.width()
                label.resize(label.width(), int(label.width() * scale))
            if resize_label_fixed_h:
                scale = img.width() / img.height()
                label.resize(int(label.height() * scale), label.height())

            img = img.scaled(label.width(), label.height(), Qt.KeepAspectRatio)
        
        label.setPixmap(img)

        return True
        
    def _set_external_click_function(self, data: WikiFrameSettings):
        if not data.wiki_ignore_feedback:
            self.external_feedback_click_function = data.wiki_feedback
        else:
            self.external_feedback_click_function = None

    def image_link_clicked(self, url: str):
        self.loading_page(True)
        image_dialog = WikiImageView(self, self._stt)
        image_dialog.resize(500, 300)
        image_dialog.show()
        QCoreApplication.processEvents()

        html = self.pages[self.current_page_index]._load_url(url)
        self.loading_page(False)
        if not html:
            image_dialog.hide()
            image_dialog.deleteLater()
            QCoreApplication.processEvents()
            return

        image_dialog.url = url
        image_dialog.html = html

        image_dialog.show_image()

        return


        point = self.mapFromGlobal(QCursor.pos())
        
        result = self.set_image_to_label(url, self.lbl_pic, resize_label=True)
        if not result:
            self.link_clicked(url=url)
            return
        
        w = self.lbl_pic.width()
        h = self.lbl_pic.height()
        if w < self.width()/2:
            h = int(h * self.width() / w)
            w = int(self.width()/2)
            self.lbl_pic.resize(w, h)
            self.lbl_pic.setScaledContents(True)

        if self.lbl_pic.width() > self.width() * 0.8:
            scale = self.lbl_pic.height() / self.lbl_pic.width()
            w = int(self.width() * 0.8)
            h = int(w * scale)

            self.lbl_pic.resize(w, h)
            self.lbl_pic.setScaledContents(True)

        x = point.x()
        y = point.y() - 20

        if x + w > self.width():
            x = self.width() - w - 20
        if x < 0:
            x = 0
        if y + h > self.height():
            y = self.height() - h - 20
        if y < 0:
            y = 0

        self.lbl_pic.move(x, y)
        self.lbl_pic.raise_()
        self.lbl_pic.setVisible(True)
    
    def open_external_link(sefl, url: str):
        webbrowser.open_new_tab(url)

    def link_clicked(self, url: str):
        if not url:
            return
        
        if self.external_feedback_click_function:
            result = self.external_feedback_click_function(url)
            if not result:
                return
        if "wikipedia.org" in url:
            self.add_page(url)
        else:
            webbrowser.open_new_tab(url)

    def link_hovered(self, url: str):
        QToolTip.showText(QCursor.pos(), url)

    def fix_url(self, url: str) -> str:
        if "/index.php" in url or "#" in url:
            return ""
        
        result = url
        if url.startswith("//"):
            result = "https:" + url
        elif url.startswith("/"):
            result = "https://sr.wikipedia.org" + url
        
        if result.startswith("https://sr."):
            result = result.replace("/wiki/", "/sr-el/")
        return result

    def _define_frame(self, frame: QFrame = None, has_border: bool = False):
        if frame is None:
            frame = self

        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Plain)

        if has_border:
            frame.setLineWidth(1)
        else:
            frame.setLineWidth(0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.resize_me()
        return super().resizeEvent(a0)

    def resize_me(self):
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        
        self.lbl_loading.move(0, 0)
        self.lbl_loading.resize(w, h)

        x = w - self.lbl_next_page.width() - self.lbl_prev_page.width() - (self.wiki_frame_settings.wiki_info_padding_hor + 2)
        if x < 0:
            x = 0
        self.lbl_prev_page.move(x, self.wiki_frame_settings.wiki_info_padding_ver)
        self.lbl_next_page.move(x + self.lbl_prev_page.width() + 2, self.wiki_frame_settings.wiki_info_padding_ver)

    def close_me(self):
        UTILS.LogHandler.add_log_record("#1: Card frame closed.", ["WikipediaCard"])
        UTILS.DialogUtility.on_closeEvent(self)

    def _define_widgets(self):
        # Table of content frame
        self.frm_toc = QFrame(self)
        self._define_frame(self.frm_toc, has_border=self.wiki_frame_settings.wiki_content_toc_has_border)

        # Content frame
        self.frm_content = QFrame(self)
        self._define_frame(self.frm_content)

        # Loading label
        self.lbl_loading = QLabel(self)
        self.lbl_loading.setAlignment(Qt.AlignCenter)
        self.lbl_loading.setStyleSheet("color: #cb0000; background-color: rgba(54, 12, 68, 50);")
        font = self.lbl_loading.font()
        font.setPointSize(30)
        font.setBold(True)
        self.lbl_loading.setFont(font)
        self.lbl_loading.setText(self.wiki_frame_settings.wiki_loading_text)
        self.lbl_loading.setVisible(False)

        # Navigation labels
        self.lbl_prev_page = QLabel(self)
        self.lbl_prev_page.setAlignment(Qt.AlignCenter)
        self.lbl_prev_page.setText("⇦")
        self.lbl_prev_page.setFont(font)
        self.lbl_prev_page.setStyleSheet("QLabel {color: rgba(255, 255, 127, 150); background-color: rgba(0, 0, 255, 0); border-top-left-radius: 15px; border-bottom-left-radius: 15px; border-top-right-radius: 10px; border-bottom-right-radius: 10px;}\nQLabel::hover {color: rgba(255, 255, 127, 250); background-color: rgba(0, 0, 255, 250);}\nQLabel:disabled {color: rgba(255, 255, 127, 50); background-color: rgba(0, 0, 255, 0);}")
        self.lbl_prev_page.resize(50, 50)
        self.lbl_prev_page.setVisible(False)

        self.lbl_next_page = QLabel(self)
        self.lbl_next_page.setAlignment(Qt.AlignCenter)
        self.lbl_next_page.setText("⇨")
        self.lbl_next_page.setFont(font)
        self.lbl_next_page.setStyleSheet("QLabel {color: rgba(255, 255, 127, 150); background-color: rgba(0, 0, 255, 0); border-top-left-radius: 15px; border-bottom-left-radius: 15px; border-top-right-radius: 10px; border-bottom-right-radius: 10px;}\nQLabel::hover {color: rgba(255, 255, 127, 250); background-color: rgba(0, 0, 255, 250);}\nQLabel:disabled {color: rgba(255, 255, 127, 50); background-color: rgba(0, 0, 255, 0);}")
        self.lbl_next_page.resize(50, 50)
        self.lbl_next_page.setVisible(False)

        self.lbl_pic = QLabel(self)
        self.lbl_pic.setAlignment(Qt.AlignCenter)
        self.lbl_pic.setVisible(False)
        self.lbl_pic.setStyleSheet("border: 2px solid;")

        self.resize(self.wiki_frame_settings.wiki_width, 250)

