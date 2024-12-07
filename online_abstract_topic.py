from PyQt5 import QtGui
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, pyqtSignal, QSize, Qt

import os
from cyrtranslit import to_latin

import settings_cls
import urllib.request
import requests
from rashomon_cls import Rashomon
import html_parser_cls
from urllib.parse import urlparse
import utility_cls
import UTILS


class AbstractTopic(QFrame):
    signal_topic_info = pyqtSignal(str, dict)

    def __init__(self, parent_widget, settings: settings_cls.Settings = None):
        super().__init__(parent_widget)
        self._stt = settings
        if settings:
            # Define settings object and methods
            self.getv = self._stt.get_setting_value
            self.setv = self._stt.set_setting_value
            self.getl = self._stt.lang
            self.get_appv = self._stt.app_setting_get_value
            self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.name = "Abstract Topic"
        self.title: str = None
        self.change_title = True
        self.link: str = None
        self.icon_path: str = None
        self.icon_pixmap: QPixmap = None
        self.topic_info_dict = {
            "name": None,
            "title": None,
            "working": False,
            "msg": ""
        }

        self.stop_loading = False
        self.rashomon = Rashomon()
        self.html_parser = html_parser_cls.HtmlParser()
        self.slider_frm_image_slide = None
        self.base_url = ""

        # Events

    def _load_slider_widgets(self):
        # Image slide
        self.slider_frm_image_slide: QFrame = QFrame(self)
        self.slider_frm_image_slide.setFrameShape(QFrame.NoFrame)
        self.slider_frm_image_slide.setFrameShadow(QFrame.Plain)
        self.slider_frm_image_slide.setVisible(False)
        self.slider_frm_image_slide.setStyleSheet("background-color: #00007f;")
        
        self.slider_lbl_image = QLabel(self.slider_frm_image_slide)
        self.slider_lbl_image.setAlignment(Qt.AlignCenter)
        
        self.slider_lbl_left = QLabel(self.slider_frm_image_slide)
        self.slider_lbl_left.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.slider_lbl_left.setCursor(Qt.PointingHandCursor)
        self.slider_lbl_left.setAlignment(Qt.AlignCenter)
        self.slider_lbl_left.setPixmap(QPixmap(self.getv("left_roll_icon_path")))
        self.slider_lbl_left.setScaledContents(True)
        
        self.slider_lbl_right = QLabel(self.slider_frm_image_slide)
        self.slider_lbl_right.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.slider_lbl_right.setCursor(Qt.PointingHandCursor)
        self.slider_lbl_right.setAlignment(Qt.AlignCenter)
        self.slider_lbl_right.setPixmap(QPixmap(self.getv("right_roll_icon_path")))
        self.slider_lbl_right.setScaledContents(True)

        self.slider_lbl_close = QLabel(self.slider_frm_image_slide)
        self.slider_lbl_close.setStyleSheet("background-color: rgba(0,0,0,0);")
        self.slider_lbl_close.setCursor(Qt.PointingHandCursor)
        self.slider_lbl_close.setAlignment(Qt.AlignCenter)
        self.slider_lbl_close.setPixmap(QPixmap(self.getv("close_icon_path")))
        self.slider_lbl_close.setScaledContents(True)

        self.slider_lbl_count = QLabel(self.slider_frm_image_slide)
        font = self.slider_lbl_count.font()
        font.setPointSize(26)
        font.setBold(True)
        self.slider_lbl_count.setFont(font)
        self.slider_lbl_count.setStyleSheet("color: #ffffff; background-color: rgba(0,0,0,0);")
        self.slider_lbl_count.setAlignment(Qt.AlignCenter)

        self._slider_current_image_index = None
        self._slider_image_list = []

        self.slider_lbl_left.mousePressEvent = self._slider_go_left
        self.slider_lbl_right.mousePressEvent = self._slider_go_right
        self.slider_lbl_close.mousePressEvent = self._slider_close_show
        self.slider_lbl_image.mousePressEvent = self._slider_image_mouse_press

    def _slider_close_show(self, e):
        self.slider_frm_image_slide.setVisible(False)

    def _slider_image_mouse_press(self, e):
        if e.button() == Qt.RightButton:
            self.slider_frm_image_slide.setVisible(False)

    def _slider_go_left(self, e):
        if len(self._slider_image_list) > 1:
            self._slider_current_image_index -= 1
            if self._slider_current_image_index < 0:
                self._slider_current_image_index = len(self._slider_image_list) - 1
            self.set_image_to_label(self._slider_image_list[self._slider_current_image_index], self.slider_lbl_image)
            self.slider_lbl_count.setText(f"{self._slider_current_image_index + 1} / {len(self._slider_image_list)}")

    def _slider_go_right(self, e):
        if len(self._slider_image_list) > 1:
            self._slider_current_image_index += 1
            if self._slider_current_image_index >= len(self._slider_image_list):
                self._slider_current_image_index = 0
            self.set_image_to_label(self._slider_image_list[self._slider_current_image_index], self.slider_lbl_image)
            self.slider_lbl_count.setText(f"{self._slider_current_image_index + 1} / {len(self._slider_image_list)}")
    
    def key_press_handler(self, event) -> bool:
        if self.slider_frm_image_slide is None:
            return None
        
        if event.key() == Qt.Key_Escape:
            if self.slider_frm_image_slide.isVisible():
                self.slider_frm_image_slide.setVisible(False)
                return True
            self.close_me()
        elif event.key() == Qt.Key_Left:
            if self.slider_frm_image_slide.isVisible():
                self._slider_go_left(event)
                return True
        elif event.key() == Qt.Key_Right:
            if self.slider_frm_image_slide.isVisible():
                self._slider_go_right(event)
                return True

    def signal_topic_info_emit(self, topic_name: str, info: dict):
        self.signal_topic_info.emit(topic_name, info)
        
    def load_topic(self):
        self.stop_loading = False
        self.topic_info_dict["msg"] = ""
        self.topic_info_dict["working"] = False
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

    def close_me(self):
        UTILS.LogHandler.add_log_record("#1: Topic closed.", [self.name])
        self.stop_loading_topic()

    def stop_loading_topic(self):
        self.stop_loading = True

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result

    def _get_float(self, text: str) -> float:
        result = None
        try:
            result = float(text)
        except:
            result = None
        return result

    def area_changed(self, area_object: QScrollArea):
        pass

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.resize_me()
        return super().resizeEvent(a0)
    
    def resize_me(self, size: QSize = None):
        pass

    def set_image_to_label(self, image_data: str, label: QLabel, strech_to_label: bool = False, use_cashe: bool = True, resize_label: bool = False, resize_label_fixed_w: bool = False, resize_label_fixed_h: bool = False) -> bool:
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
            if use_cashe:
                img = self._get_image_from_cashe(image_url)
                if img:
                    has_image = True
            if not has_image:
                if os.path.isfile(image_url):
                    img = QPixmap()
                    has_image = img.load(os.path.abspath(image_url))
                    # print (img.width(), img.height())
                    # rrr = img.scaledToHeight(50, img.KeepAspectRatio)
                    # print (rrr.width(), rrr.height())
                    # print ()
                else:
                    response = requests.get(image_url, timeout=2)
                    img = QPixmap()
                    has_image = img.loadFromData(response.content)
        except:
            img = None
        
        if tt:
            label.setToolTip(tt)

        if not has_image:
            return False
        
        if use_cashe:
            self._set_image_to_cashe(image_url=image_url, image_pixmap=img)
        
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

    def _get_image_from_cashe(self, image_url: str) -> QPixmap:
        if not self._stt:
            return None
        
        if "images_cashe" in self._stt.app_setting_get_list_of_keys():
            images_cashe = self.get_appv("images_cashe")
        else:
            return None

        for image in images_cashe:
            if image[0] == image_url:
                img = QPixmap()
                result = img.load(image[1])
                if result:
                    return img
                else:
                    return None
        return None

    def _set_image_to_cashe(self, image_url: str, image_pixmap: QPixmap):
        if not self._stt:
            return None
        
        images_cashe = []
        if "images_cashe" in self._stt.app_setting_get_list_of_keys():
            images_cashe = self.get_appv("images_cashe")
        else:
            self._stt.app_setting_add("images_cashe", images_cashe)
        
        new_id = str(len(images_cashe))
        
        parsed_url = urlparse(image_url)
        url_file_name = parsed_url.path.split("/")[-1]

        file_name = f'{self.getv("temp_folder_path")}{new_id}_{url_file_name}'
        file_name = os.path.abspath(file_name)

        if not file_name:
            return
        
        image_pixmap.save(file_name)
        images_cashe.append([image_url, file_name])

    def get_images_from_search_engine(self, query_string: str, project_file: str) -> dict:
        result = {}
        
        self.rashomon.errors(clear_errors=True)
        q = self._clean_search_string(search_string=query_string)
        url = f"https://images.search.yahoo.com/search/images;?p={q}"
        self.rashomon.load_project(project_filename=project_file, change_source=url)
        if self.rashomon.errors():
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = "Abstract Topic, Unexpected error: " + i
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return result
        self.rashomon.set_compatible_mode(True)
        recreate_result = self.rashomon.recreate_segment_tree()
        if self.rashomon.errors() or not recreate_result:
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = "Abstract Topic, Unexpected error: " + i
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return result

        page_code = self.rashomon.get_segment_selection("images")
        images_code = self.html_parser.get_tags(html_code=page_code, tag="ul", custom_tag_property=[["id", "sres"]], multiline=True)
        if images_code:
            segments = self.html_parser.get_tags(html_code=images_code[0], tag="li", tag_class_contains="ld", multiline=True)

        count = 0
        for html_code in segments:
            if "<ul>" in html_code:
                continue

            result[str(count)] = {}
            self.html_parser.load_html_code(html_code)
            
            result[str(count)]["img_tag"] = ""
            images = self.html_parser.get_all_images()
            for image in images:
                if not image.img_class:
                    result[str(count)]["img_tag"] = image
                    break
            
            text_code = self.rashomon.get_tags(html_code=html_code, tag="div", tag_class_contains="img-desc", multiline=True)
            desc = ""
            if text_code:
                text_code = text_code[0]
                title = ""
                source = ""
                source_code = self.html_parser.get_tags(html_code=text_code, tag="span", tag_class_contains="source", multiline=True)
                if source_code:
                    self.html_parser.load_html_code(source_code[0])
                    source = self.html_parser.get_raw_text()
                
                title = ""
                in_tag = False
                for i in text_code.splitlines():
                    if i.startswith('<span class="source"'):
                        in_tag = True
                        continue
                    if i.startswith("</span>") and in_tag:
                        in_tag = False
                        continue
                    if in_tag:
                        continue
                    if i.startswith("<span"):
                        title += "\n"
                    if not i.startswith("<"):
                        title += i
                title = title.strip()
                
                desc = title + "\n" + source
                if title and source:
                    desc_text = title + "\n" + source
                    text_to_html = utility_cls.TextToHTML(text=desc_text)
                    text_to_html.general_rule.font_size = 12
                    text_to_html.general_rule.font_bold = True
                    text_to_html.general_rule.fg_color = "#aaff7f"
                    source_rule = utility_cls.TextToHtmlRule(text=source, fg_color="#aaffff", font_size=10, link_href=source)
                    text_to_html.add_rule(source_rule)
                    desc = text_to_html.get_html()

            result[str(count)]["desc"] = desc
            count += 1
        
        return result

    def get_search_results(self, query_string: str) -> list:
        result = self._get_search_results_duckduckgo(query_string=query_string)
        if not result:
            result = self._get_search_results_yahoo(query_string=query_string)
            if not result:
                result = self._get_search_results_brave(query_string=query_string)

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

        data = self.html_parser.get_tags(html_code=html, tag="tr")
        link = ""
        desc = ""
        title = ""
        link_list = []
        for row in data:
            if 'class="nav_button"' in row:
                continue
            links = self.html_parser.get_all_links(load_html_code=row)
            if links:
                title = links[0].a_text.strip()
                continue

            desc_code = self.html_parser.get_tags(html_code=row, tag="td", tag_class_contains="result-snippet")
            if desc_code:
                desc = self.html_parser.get_raw_text(load_html_code=desc_code[0]).strip()
            
            link = ""
            link_code = self.html_parser.get_tags(html_code=row, tag="span", tag_class_contains="link-text")
            if link_code:
                link = self.html_parser.get_raw_text(load_html_code=link_code[0]).strip()
                if not link.startswith("http"):
                    link = "https://" + link.lstrip("/")

            if link and link not in link_list:
                link_list.append(link)
                item = {}
                item["title"] = "🌐 " + title
                item["link"] = link
                item["description"] = desc
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
            title_code = self.html_parser.get_tags(html_code=row, tag="div", tag_class_contains="heading")
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
                result.append(item)
        
        return result

    def _load_url(self, source_http: str) -> str:
        try:
            result_page = urllib.request.urlopen(source_http, timeout=3)
            html = result_page.read().decode("utf-8")
        except:
            try:
                result_page = requests.get(source_http, timeout=3)
                html = result_page.content.decode("utf-8")
                print ("Used REQUESTS !")
            except:
                return None
        return html

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

    def show_image_slide(self, images: list = None):
        if self.slider_frm_image_slide is None:
            self._load_slider_widgets()

        if images is None:
            if self.data and self.data.active_page:
                page = self.data.get_page(self.data.active_page)
                if page:
                    images = page["images"]

        img_to_show = []
        if isinstance(images, str):
            img_to_show.append(images)
        elif isinstance(images, list) or isinstance(images, tuple):
            for image_data in images:
                if isinstance(image_data, str):
                    img_to_show.append(image_data)
                elif isinstance(image_data, html_parser_cls.ImageObject):
                    img_to_show.append(image_data.img_src)
                else:
                    return False
        else:
            return False
        
        if not img_to_show:
            return False
        
        slide_rect: QRect = self.parent_widget.area_content.visibleRegion().boundingRect()
        y = self.parent_widget.area_content.verticalScrollBar().value()

        self.slider_frm_image_slide.move(30, y + 30)
        w = slide_rect.width() - 60
        if w < 100:
            return False
        h = slide_rect.height() - 60
        if h < 100:
            return False
        
        self.slider_frm_image_slide.resize(w, h)
        self.slider_frm_image_slide.show()
        
        self.slider_lbl_image.move(0, 0)
        self.slider_lbl_image.resize(w, h)

        control_y = int((self.slider_frm_image_slide.height() / 8) * 3)
        control_h = int((self.slider_frm_image_slide.height() / 8) * 2)
        self.slider_lbl_left.move(0, control_y)
        self.slider_lbl_left.resize(50, control_h)
        self.slider_lbl_right.move(w-50, control_y)
        self.slider_lbl_right.resize(50, control_h)

        self.slider_lbl_close.move(int(self.slider_frm_image_slide.width() / 2) - 25, self.slider_frm_image_slide.height() - 50)
        self.slider_lbl_close.resize(50, 50)
        
        self.slider_lbl_count.move(0, 0)
        self.slider_lbl_count.resize(self.slider_frm_image_slide.width(), 70)

        self._slider_current_image_index = 0
        self._slider_image_list = img_to_show
        self.slider_lbl_count.setText(f"{self._slider_current_image_index + 1} / {len(self._slider_image_list)}")

        self.set_image_to_label(img_to_show[0], self.slider_lbl_image)

    def fix_url(self, url: str) -> str:
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = self.base_url.strip(" /") + "/" + url.strip(" /")
        return url
    
    def cirilica_u_latinicu(self, text: str) -> str:
        latinica_text = to_latin(text)
        return latinica_text





                






        


            