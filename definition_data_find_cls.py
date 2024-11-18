from PyQt5.QtWidgets import (QFrame, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QRadioButton,
                             QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QDialog, QCheckBox,
                             QGroupBox, QTextEdit)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QMouseEvent, QResizeEvent, QCursor, QMovie
from PyQt5.QtCore import Qt, QCoreApplication, QPoint
from PyQt5 import QtCore, QtGui, uic

import time
from unidecode import unidecode
import requests
import urllib.request
from cyrtranslit import to_latin
from cyrtranslit import to_cyrillic

import settings_cls
import utility_cls
import html_parser_cls
import wikipedia_card_cls
import wikipedia_cls
import qwidgets_util_cls
import UTILS


class ImageItem(QLabel):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, img_src: str):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.img_src = img_src
        self.is_active = True

        self._define_widget()
        self.load_image(self.img_src)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.set_active(not self.is_active)
        return super().mousePressEvent(ev)

    def set_active(self, value: bool):
        self.is_active = value
        if value:
            self.setStyleSheet("QLabel {color: rgba(255, 255, 255, 255);}")
            self.lbl_status.setPixmap(QPixmap(self.getv("ok_icon_path")))
            self.lbl_disabled.setVisible(False)
        else:
            self.setStyleSheet("QLabel {color: rgba(255, 255, 255, 55);}")
            self.lbl_status.setPixmap(QPixmap(self.getv("cancel_icon_path")))
            self.lbl_disabled.setVisible(True)

    def load_image(self, image_url: str):
        response = urllib.request.urlopen(image_url, timeout=2).read()
        img = QPixmap()
        has_image = img.loadFromData(response)
        if not has_image:
            response = requests.get(image_url, timeout=2)
            has_image = img.loadFromData(response.content)

        if not has_image:
            return
        
        scale = int((img.width() / img.height()) * 190)
        self.setFixedSize(scale, 190)
        self.setScaledContents(True)
        self.setPixmap(img)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.lbl_status.move(self.width() - 30, 0)
        self.lbl_disabled.resize(self.width(), self.height())
        return super().resizeEvent(a0)

    def _define_widget(self):
        self.setAlignment(Qt.AlignCenter)

        self.lbl_disabled = QLabel(self)
        self.lbl_disabled.setStyleSheet("QLabel {color: #ffffff; background-color: rgba(0,0,0,200);}")
        self.lbl_disabled.move(0, 0)
        self.lbl_disabled.setVisible(False)

        self.lbl_status = QLabel(self)
        self.lbl_status.setFixedSize(30, 30)
        self.lbl_status.setScaledContents(True)
        self.lbl_status.setStyleSheet("QLabel {color: #ffffff; background-color: rgba(0,0,0,80);}")
        self.lbl_status.setPixmap(QPixmap(self.getv("ok_icon_path")))


class SynHead:
    def __init__(self,
                 name: str = "",
                 source: str = "",
                 is_enabled: bool = True,
                 syn_items: list = [],
                 sub_heads: list = [],
                 downloaded: bool = False):
        
        self.name = name
        self.source = source
        self.is_enabled = is_enabled
        self.items = syn_items
        self.sub_heads = sub_heads
        self.downloaded = downloaded

    def copy_from_headitem(self, item: "SynHead"):
        self.name = item.name
        self.source = item.source
        self.is_enabled = item.is_enabled
        self.items = item.items
        self.sub_heads = item.sub_heads
        self.downloaded = item.downloaded


class SynItem:
    def __init__(self,
                 name: str = "",
                 head: str = "",
                 is_enabled: bool = True):
        
        self.name = name
        self.head = head
        self.is_enabled = is_enabled


class SynonymManager(QFrame):
    MAX_W = 646
    MAX_H = 526
    INDENT = 40
    SPACING = 10
    COLOR_ITEM_ENABLED = "#aaff00"
    COLOR_ITEM_DISABLED = "#afafaf"

    def __init__(self, 
                 parent_widget: QWidget, 
                 settings: settings_cls.Settings, 
                 data: list, 
                 default_synonym_key: str, 
                 expression: str, 
                 section: str,
                 update_parent_list_function = None):
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
        self.data = data
        self.DEFAULT_SYNONYMS_KEY = default_synonym_key
        self.update_parent_list_function = update_parent_list_function
        self.url = None
        self.expression = expression
        self.section = section
        self.has_data = False
        self.html_parser = html_parser_cls.HtmlParser()

        self._define_widgets()

        # Connect events with slots
        self.lst_info.itemChanged.connect(self.lst_info_item_changed)
        self.lst_info.mouseDoubleClickEvent = self.lst_info_mouse_double_click
        self.lbl_close_title.mousePressEvent = self.lbl_close_title_mouse_press
        self.lbl_select_all.mousePressEvent = self.lbl_select_all_click
        self.lbl_select_none.mousePressEvent = self.lbl_select_none_click

        if self.expression:
            self.has_data = self.load_data(self.expression)
        
        self.show()
        self.show_data()

    def lbl_select_all_click(self, e: QMouseEvent):
        for i in range(self.lst_info.count()):
            self.lst_info.item(i).setCheckState(Qt.Checked)

    def lbl_select_none_click(self, e: QMouseEvent):
        for i in range(self.lst_info.count()):
            self.lst_info.item(i).setCheckState(Qt.Unchecked)

    def lbl_close_title_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.frm_info.setVisible(False)

    def lst_info_mouse_double_click(self, e: QMouseEvent):
        item = self.lst_info.currentItem()
        if e.button() == Qt.LeftButton and item:
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

    def lst_info_item_changed(self, e: QListWidgetItem):
        if e:
            item = e.data(Qt.UserRole)
            if e.checkState() == Qt.Checked:
                item.is_enabled = True
            else:
                item.is_enabled = False
            self.update_parent_list_function(item)

    def show_data(self):
        self._clear_frame()
        self.frm_info.setVisible(False)

        x = 10
        y = 10
        max_w = 0
        for item in self.data["syn"]:
            x, y, w = self._recurs_show_data(item, x, y)
            max_w = max(max_w, x + w)
        
        for i in self.children():
            if i != self.frm_info:
                max_w = i.pos().x() + i.width()

        self.resize(max(self.MAX_W, max_w + 10), max(self.MAX_H, y))
        self.parent_widget.resize(self.width(), self.height())
        self.show()

    def update_item(self, item: SynItem):
        # Item
        for obj in self.children():
            if obj.objectName() == item.head:
                for item_obj in obj.children():
                    if item_obj.objectName() == "info":
                        headitem = self._get_head_item(item.head)
                        text = self._item_info_label_text(headitem)
                        item_obj.setText(text)

        # List
        for idx in range(self.lst_info.count()):
            lst_item = self.lst_info.item(idx)
            lst_item_data = self.lst_info.item(idx).data(Qt.UserRole)
            if lst_item_data.head == item.head and lst_item_data.name == item.name:
                if item.is_enabled:
                    lst_item.setCheckState(Qt.Checked)
                    lst_item.setForeground(QColor(self.COLOR_ITEM_ENABLED))
                else:
                    lst_item.setCheckState(Qt.Unchecked)
                    lst_item.setForeground(QColor(self.COLOR_ITEM_DISABLED))

    def _show_headitem_list(self, headitem: SynHead, pos: QPoint):
        if self.frm_info.isVisible() and self.frm_info.objectName() == headitem.name:
            self.frm_info.setVisible(False)
            return
        
        x = 10
        if pos.x() < 320:
            x = 325
        y = 10 + self.parent_widget.parent().parent().verticalScrollBar().value()

        self.frm_info.move(x, y)

        self._populate_headitem_list(headitem)
        self.frm_info.setObjectName(headitem.name)
        self.frm_info.raise_()
        self.lbl_info_title.setText(headitem.name)
        self.frm_info.setVisible(True)

    def _populate_headitem_list(self, headitem: SynHead):
        self.lst_info.clear()
        for item in headitem.items:
            lst_item = QListWidgetItem()
            lst_item.setFlags(lst_item.flags() | Qt.ItemIsUserCheckable)
            if item.is_enabled:
                lst_item.setCheckState(Qt.Checked)
                lst_item.setForeground(QColor(self.COLOR_ITEM_ENABLED))
            else:
                lst_item.setCheckState(Qt.Unchecked)
                lst_item.setForeground(QColor(self.COLOR_ITEM_DISABLED))
            lst_item.setText(item.name)
            lst_item.setData(Qt.UserRole, item)
            self.lst_info.addItem(lst_item)
    
    def _download_head_item(self, e: QMouseEvent, item: SynHead, enable_item: bool = False):
        if e is not None:
            if e.button() != Qt.LeftButton or item.downloaded:
                return
        else:
            if item.downloaded:
                return
        
        syn_data = self.get_synonyms(item.name, ignore_duplicate_names=True)
        if not syn_data:
            item.downloaded = True
            self.show_data()
            return
        
        item.copy_from_headitem(syn_data)

        item.is_enabled = enable_item

        self.show_data()

    def _recurs_show_data(self, headitem: SynHead, x: int, y: int) -> tuple:
        frm: QFrame = self._create_frame(headitem)
        frm.move(x, y)
        frm.show()
        QCoreApplication.processEvents()
        y += frm.height() + self.SPACING

        x1 = x + self.INDENT
        for item in headitem.sub_heads:
            x1, y, _ = self._recurs_show_data(item, x1, y)
            y += self.SPACING

        return (x, y, frm.width())

    def _item_enabled_press(self, e: QMouseEvent, label: QLabel, headitem: SynHead):
        if e.button() == Qt.LeftButton:
            if not headitem.downloaded:
                self._download_head_item(e, headitem, enable_item=True)
                self.update_parent_list_function()
                return

            if headitem.is_enabled:
                headitem.is_enabled = False
                label.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
            else:
                headitem.is_enabled = True
                label.setPixmap(QPixmap(self.getv("checked_icon_path")))
            self.update_parent_list_function()

    def _create_frame(self, headitem: SynHead) -> QFrame:
        frm = QFrame(self)
        frm.setObjectName(headitem.name)

        # Enabled label
        lbl_enabled = QLabel(frm)
        lbl_enabled.move(10, 10)
        lbl_enabled.resize(40, 40)
        if headitem.is_enabled:
            lbl_enabled.setPixmap(QPixmap(self.getv("checked_icon_path")))
        else:
            lbl_enabled.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
        lbl_enabled.setScaledContents(True)
        lbl_enabled.setStyleSheet("QLabel:hover {background-color: rgb(196, 196, 255);}")
        lbl_enabled.mousePressEvent = lambda e: self._item_enabled_press(e, lbl_enabled, headitem)

        # Item label
        lbl_item = QLabel(frm)
        lbl_item.setObjectName("item")
        lbl_item.move(70, 10)
        font = lbl_item.font()
        font.setPointSize(22)
        lbl_item.setFont(font)
        lbl_item.setText(headitem.name)
        lbl_item.adjustSize()
        if headitem.name == self.DEFAULT_SYNONYMS_KEY or headitem.downloaded:
            lbl_item.setStyleSheet("color: #000000;")
        else:
            lbl_item.setStyleSheet("QLabel {color: #fcc4ff;} QLabel:hover {color: #ffff00;}")
        lbl_item.mousePressEvent = lambda e: self._download_head_item(e, headitem)

        style_enabled = "QPushButton {color: #ffff00; background-color: #00007f;} QPushButton:hover {color: #ffff00; 	background-color: #0000cf;}"
        style_disabled = "QPushButton {color: #cfcfcf;}"

        # View List Button
        btn_list = QPushButton(frm)
        btn_list.setObjectName("list")
        btn_list.move(lbl_item.width() + 90, 10)
        btn_list.setText(self.getl("def_finder_syn_list_item_btn_list_text"))
        if headitem.items:
            btn_list.setStyleSheet(style_enabled)
            btn_list.setEnabled(True)
        else:
            btn_list.setStyleSheet(style_disabled)
            btn_list.setEnabled(False)
        if headitem.name == self.DEFAULT_SYNONYMS_KEY:
            btn_list.setStyleSheet(style_enabled)
            btn_list.setEnabled(True)
        btn_list.adjustSize()
        btn_list.resize(btn_list.width() + 20, btn_list.height())
        btn_list.clicked.connect(lambda _: self._show_headitem_list(headitem, btn_list.pos()))
        
        # Related Terms Button
        btn_more = QPushButton(frm)
        btn_more.setObjectName("more")
        btn_more.move(lbl_item.width() + 90 + btn_list.width() + 10, 10)
        btn_more.setText(self.getl("def_finder_syn_list_item_btn_more_text"))
        if headitem.downloaded or headitem.name == self.DEFAULT_SYNONYMS_KEY:
            btn_more.setStyleSheet(style_disabled)
            btn_more.setEnabled(False)
        else:
            btn_more.setStyleSheet(style_enabled)
            btn_more.setEnabled(True)
        btn_more.adjustSize()
        btn_more.resize(btn_more.width() + 20, btn_more.height())
        btn_more.clicked.connect(lambda _: self._download_head_item(None, headitem))

        # Info label
        lbl_info = QLabel(frm)
        lbl_info.setObjectName("info")
        lbl_info.setWordWrap(True)
        lbl_info.move(lbl_item.width() + 90, 35)
        lbl_info.resize(btn_list.width() + btn_more.width() + 10, 30)
        text = self._item_info_label_text(headitem)
        lbl_info.setText(text)
        lbl_info.setStyleSheet("color: #e1e1e1;")

        w = btn_more.pos().x() + btn_more.width() + 10
        h = 70

        frm.resize(w, h)
        return frm

    def _item_info_label_text(self, headitem: SynHead) -> str:
        enabled_items = 0
        for i in headitem.items:
            i: SynItem
            if i.is_enabled:
                enabled_items += 1

        text = ""
        if headitem.downloaded:
            if headitem.sub_heads:
                text += self.getl("def_finder_syn_list_item_info_related_text").replace("#1", str(len(headitem.sub_heads))) + "\n"
            else:
                text += self.getl("def_finder_syn_list_item_info_no_related_text") + "\n"
        text += self.getl("def_finder_syn_list_item_info_list_count_text").replace("#1", str(enabled_items)).replace("#2", str(len(headitem.items)))
        return text

    def _clear_frame(self):
        for item in self.children():
            if item != self.frm_info:
                item.setVisible(False)
                item.deleteLater()

    def load_data(self, expression: str) -> bool:
        syn_data = self.get_synonyms(expression)
        if not syn_data:
            return False
        
        syn_data.is_enabled = True

        self.data["syn"].append(syn_data)
        return True

    def _get_list_of_synitems(self, only_enabled: bool = False, only_disabled: bool = False, headitem: SynHead = None) -> list:
        if headitem:
            return self._recurs_syn_items(headitem=headitem, only_enabled=only_enabled, only_disabled=only_disabled)

        result = []
        for headitem in self.data["syn"]:
            result += self._recurs_syn_items(headitem=headitem, only_enabled=only_enabled, only_disabled=only_disabled)
        return result

    def _recurs_syn_items(self, headitem: SynHead, only_enabled: bool = False, only_disabled: bool = False) -> list:
        items = []
        for item in headitem.items:
            item: SynItem
            if only_enabled and item.is_enabled:
                items.append(item)
            elif only_disabled and not item.is_enabled:
                items.append(item)
            else:
                items.append(item)
        for hitem in headitem.sub_heads:
            items += self._recurs_syn_items(headitem=hitem, only_enabled=only_enabled, only_disabled=only_disabled)

        return items

    def _get_list_of_headitems(self) -> list:
        result = []
        for headitem in self.data["syn"]:
            result += [headitem]
            result += self._recurs_syn_headitems(headitem=headitem)
        return result

    def _recurs_syn_headitems(self, headitem: SynHead):
        headitems = []
        headitems += headitem.sub_heads
        for hitem in headitem.sub_heads:
            headitems += self._recurs_syn_headitems(headitem=hitem)
        return headitems

    def _get_head_item(self, name: str) -> SynHead:
        for item in self.data["syn"]:
            result = self._recur_get_head_item(name=name, headitem=item)
            if result:
                return result
        
        return None

    def _recur_get_head_item(self, name: str, headitem: SynHead) -> SynHead:
        if headitem.name == name:
            return headitem
        
        for subitem in headitem.sub_heads:
            result = self._recur_get_head_item(name=name, headitem=subitem)
            if result:
                return result
        
        return None

    def get_synonyms(self, expression: str, ignore_duplicate_names: bool = False, inflection_run: str = None) -> SynHead:
        if not inflection_run:
            expression = self._clean_search_string(expression, remove_serbian_chars=False, delimiter="_")

            if expression in [x.name for x in self._get_list_of_headitems()]:
                if not ignore_duplicate_names:
                    return None
            url = f"https://en.wiktionary.org/wiki/{expression}"
        else:
            url = inflection_run

        html = self._get_html_from_url(url)
        if not html:
            return None
        
        html = self.html_parser._quick_format_html(html)
        
        section = self._get_section(html)

        if not section:
            return None
        
        words = self._get_word_list(section)

        clean_words = self._clean_up_words(words)

        items_list = []
        list_of_syn_items = [x.name for x in self._get_list_of_synitems()]
        for item in clean_words:
            if item in list_of_syn_items:
                can_be_enabled = False
            else:
                can_be_enabled = True
            
            syn_item = SynItem(name=item, head=expression, is_enabled=can_be_enabled)
            items_list.append(syn_item)

        sub_headitems = self._get_subheaditems(section)

        if not sub_headitems and not items_list and not inflection_run:
            result = self._check_for_inflection(section)
            if result:
                inflection_result = self.get_synonyms(expression=expression, ignore_duplicate_names=ignore_duplicate_names, inflection_run=result)
                return inflection_result
        
        head_item = SynHead(name=expression,
                            source=url,
                            is_enabled=False,
                            syn_items=items_list,
                            downloaded=True,
                            sub_heads=sub_headitems)
        
        return head_item

    def _check_for_inflection(self, html: str) -> str:
        link = None
        inf_code = self.html_parser.get_tags(html_code=html, tag="span", tag_class_contains="form-of-definition-link")
        if inf_code:
            links = self.html_parser.get_all_links(load_html_code=inf_code[0])
            if links:
                link = self.fix_url(links[0].a_href)
        return link

    def _get_subheaditems(self, section: str) -> list:
        headitems = self._extract_subheaditems(section=section, name="Derived_terms")
        headitems += self._extract_subheaditems(section=section, name="Related_terms")
        return headitems

    def _extract_subheaditems(self, section: str, name: str) -> list:
        headitems = []

        derived_code = self.html_parser.get_tags(html_code=section, tag="span", custom_tag_property=[["id", name]], return_line_numbers=True)
        if derived_code:
            start = derived_code[0][1]
            derived_list = None
            lists = self.html_parser.get_tags(html_code=section, tag="ul", return_line_numbers=True)
            for i in lists:
                if i[1] > start:
                    derived_list = i[0]
                    break
            if derived_list:
                derived_list_items = self.html_parser.get_tags(html_code=derived_list, tag="li")
                for item in derived_list_items:
                    links = self.html_parser.get_all_links(load_html_code=item)
                    if links:
                        if "/wiki/" in links[0].a_href:
                            # text = self.html_parser.get_raw_text(load_html_code=item).strip()
                            text = links[0].a_text
                            if text.find("(") != -1:
                                p_start = text.find("(")
                                p_end = text.find(")", p_start)
                                if p_end != -1:
                                    text = text[:p_start] + text[p_end+1:]

                            text = self._save_serbian_chars(text)
                            text = unidecode(text)
                            text = self._retrive_serbian_chars(text).strip()
                            hitem_obj = SynHead(
                                name=text,
                                source=self.fix_url(links[0].a_href),
                                is_enabled=False,
                                syn_items=[],
                                sub_heads=[],
                                downloaded=False
                            )
                            if text not in [x.name for x in self._get_list_of_headitems()]:
                                headitems.append(hitem_obj)
        return headitems

    def _clean_up_words(self, words: list) -> list:
        # Need to clean special chars like in word "kȍplje" to become "koplje"

        clean_note = []
        
        for item_raw in words:
            item_raw = item_raw.replace("\t", "\n")
            for item in item_raw.splitlines():
                if item:
                    start_char = item.strip()[0]
                    if start_char in "¹²³⁴⁵⁶⁷⁸⁹—*1234567890":
                        continue
                for word in self._clear_parenthasis(item):
                    for i in "¹²³⁴⁵⁶⁷⁸⁹—*1234567890":
                        word = word.replace(i, "")
                    for i in word.split("/"):
                        i = self._save_serbian_chars(i.lower())
                        i = unidecode(i)
                        i = self._retrive_serbian_chars(i)
                        while True:
                            if i.find("  ") == -1:
                                break
                            i = i.replace("  ", " ")
                        clean_note.append(i.strip())
        
        remove_words = [
            "ću",
            "cu",
            "ćeš",
            "ces",
            "ćes",
            "ceš",
            "će",
            "ce",
            "ćemo",
            "cemo",
            "ćete",
            "cete",
            "sam",
            "si",
            "je",
            "smo",
            "ste",
            "su",
            "budem",
            "budeš",
            "budes",
            "bude",
            "budemo",
            "budete",
            "budu",
            "bio sam",
            "bio si",
            "bio je",
            "bili smo",
            "bili ste",
            "bili su",
            "bih",
            "bi",
            "bismo",
            "biste",
            "bio bih",
            "bio bi",
            "bili bismo",
            "bili biste",
            "bili bi",
            "m",
            "f",
            "n",
            "m/",
            "f/",
            "future i",
            "imperfect",
            "passive past participle",
            "aorist"
        ]
        remove_words.sort(key=len, reverse=True)

        for idx, word in enumerate(clean_note):
            word = f" {word} "
            for string in remove_words:
                string = f" {string} "
                if string in word:
                    word = word.replace(string, "")
            
            clean_note[idx] = word.strip()

        clean_set = set(clean_note)
        result = list(clean_set)
        result = [x for x in result if x.strip()]
        result.sort()
        return result

    def _save_serbian_chars(self, text: str) -> str:
        char_map = [
            ["č", "0cc10"],
            ["ć", "0cc20"],
            ["ž", "0zz10"],
            ["š", "0ss10"],
            ["đ", "0dj10"]
        ]
        for i in char_map:
            text = text.replace(i[0], i[1])
        
        return text

    def _retrive_serbian_chars(self, text: str) -> str:
        char_map = [
            ["č", "0cc10"],
            ["ć", "0cc20"],
            ["ž", "0zz10"],
            ["š", "0ss10"],
            ["đ", "0dj10"]
        ]
        for i in char_map:
            text = text.replace(i[1], i[0])
        
        result = ""
        for i in text:
            if i in "qwertyuioplkjhgfdsazxcvbnmšđčćž":
                result += i
            else:
                result += " "
        
        return result

    def _clear_parenthasis(self, item: str) -> list:
        if item.find("(") == -1:
            return [item]
        
        start = item.find("(")
        end = item.find(")")
        if start == -1 or end == -1:
            return [item]
        
        remove_words = [
            "poetic",
            "regional"
        ]
        has_remove_words = False
        for i in remove_words:
            if i in item[start+1:end]:
                has_remove_words = True
        if has_remove_words:
            return [item[:start].strip()]

        clean_words = []
        base_word = item[:start].strip()
        suffix_list = item[start+1:end].split("/")
        clean_words.append(base_word)
        for suffix in suffix_list:
            suffix = suffix.strip()
            clean_words.append(f"{base_word}{suffix}")
        
        return clean_words

    def _get_word_list(self, section: str) -> list:
        words = []

        tables = self.html_parser.get_tags(html_code=section, tag="table", tag_class_contains="inflection-table")
        if not tables:
            return words
        
        for table in tables:
            text_code = self.html_parser.get_tags(html_code=table, tag="td")
            for code in text_code:
                text = self.html_parser.get_raw_text(load_html_code=code).strip()
                if text:
                    words.append(text)
        
        for table in tables:
            text_code = self.html_parser.get_tags(html_code=table, tag="th")
            for code in text_code:
                text = self.html_parser.get_raw_text(load_html_code=code).strip()
                if ":" in text:
                    words.append(text[text.find(":") + 1:].strip())
        
        return words

    def _get_section(self, html: str) -> list:
        content_code = self.html_parser.get_tags(html_code=html, tag="div", tag_id_contains="mw-content-text")

        if not content_code:
            return ""
        
        content_code = content_code[0].split("\n")

        usable_section = False
        div_code = ""
        result = ""
        for idx, line in enumerate(content_code):
            if line.startswith('<div class="mw-heading mw-heading2"'):
                div_code = ""
                for i in range(idx, len(content_code)):
                    div_code += content_code[i] + "\n"
                    if content_code[i].startswith("</div>"):
                        break
                language = self.html_parser.get_tags(div_code, tag="h2", tag_id_contains=self.section)
                if language:
                    usable_section = True
                else:
                    usable_section = False

            if usable_section:
                result += line + "\n"

        return result

    def _clean_search_string(self, search_string: str, remove_serbian_chars: bool = True, delimiter: str = "+") -> str:
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

        # remove_chars = "~!@#$%^&*()_+`-=[]}{;'\\\":?><,./|\n\t"
        # for char in remove_chars:
        #     search_string = search_string.replace(char, " ")

        while True:
            search_string = search_string.replace("  ", " ")
            if search_string.find("  ") == -1:
                break
        search_string = search_string.replace(" ", delimiter)
        return search_string.strip(f" {delimiter}")

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

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.parent_widget.resize(self.size())
        return super().resizeEvent(a0)
    
    def _define_widgets(self):
        self.resize(self.MAX_W, self.MAX_H)
        
        self.frm_info = QFrame(self)
        self.frm_info.setStyleSheet("QFrame {background-color: #003b00;}")
        self.frm_info.move(10, 10)
        self.frm_info.resize(300, self.MAX_H - 40)
        self.frm_info.setVisible(False)

        # Title
        self.lbl_info_title = QLabel(self.frm_info)
        self.lbl_info_title.move(0, 0)
        self.lbl_info_title.resize(self.frm_info.width(), 30)
        self.lbl_info_title.setAlignment(Qt.AlignCenter)
        font = self.lbl_info_title.font()
        font.setPointSize(14)
        self.lbl_info_title.setFont(font)
        self.lbl_info_title.setStyleSheet("color: #00ff00; background-color: #005500;")
        self.lbl_info_title.setText(self.getl("def_finder_lbl_info_title_text"))

        # Close
        self.lbl_close_title = QLabel(self.frm_info)
        self.lbl_close_title.resize(30, 30)
        self.lbl_close_title.move(self.frm_info.width() - 31, 1)
        self.lbl_close_title.setPixmap(QPixmap(self.getv("close_icon_path")))
        self.lbl_close_title.setScaledContents(True)
        self.lbl_close_title.setAlignment(Qt.AlignCenter)
        self.lbl_close_title.setStyleSheet("QLabel {background-color: rgba(0,0,0,0);} QLabel:hover {background-color: #939349;}")

        # List
        self.lst_info = QListWidget(self.frm_info)
        self.lst_info.setFont(font)
        self.lst_info.move(0, 30)
        self.lst_info.resize(self.frm_info.width(), self.frm_info.height() - 50)

        # Select all
        self.lbl_select_all = QLabel(self.frm_info)
        self.lbl_select_all.resize(20, 20)
        self.lbl_select_all.move(5, self.frm_info.height() - 20)
        self.lbl_select_all.setPixmap(QPixmap(self.getv("checked_icon_path")))
        self.lbl_select_all.setScaledContents(True)
        self.lbl_select_all.setAlignment(Qt.AlignCenter)
        self.lbl_select_all.setStyleSheet("QLabel {background-color: rgba(0,0,0,0);} QLabel:hover {background-color: #939349;}")

        # Select none
        self.lbl_select_none = QLabel(self.frm_info)
        self.lbl_select_none.resize(20, 20)
        self.lbl_select_none.move(30, self.frm_info.height() - 20)
        self.lbl_select_none.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
        self.lbl_select_none.setScaledContents(True)
        self.lbl_select_none.setAlignment(Qt.AlignCenter)
        self.lbl_select_none.setStyleSheet("QLabel {background-color: rgba(0,0,0,0);} QLabel:hover {background-color: #939349;}")

    def _get_html_from_url(self, url: str):
        try:
            response = requests.get(url)
            result = response.text
            if result:
                return result
            else:
                response = urllib.request.urlopen(url, timeout=2).read()
                result = response.decode("utf-8")
                if result:
                    return result
                else:
                    return ""
        except Exception as e:
            return ""

    def fix_url(self, url: str) -> str:
        if not url:
            return url
        result = url
        if url.startswith("//"):
            result = "https:" + url
        elif url.startswith("/"):
            result = "https://en.wiktionary.org" + url
        return result


class DefinitionFinder(QDialog):
    IGNORE_AFTER_MARKER = " ⇨"
    DEFAULT_SYNONYMS_KEY = "@@@"
    COLOR_EXIST = "#a7a7a7"
    COLOR_NEW_ENABLED = "#aaff00"
    COLOR_NEW_DISABLED = "#00994a"
    COLOR_DOUBLE = "#aa0000"
    LANG_SECTIONS = """
    English•
    中文 (Chinese) • Français (French) • Deutsch (German) • Ελληνικά (Greek) • Malagasy • Русский (Russian)
    •Հայերեն (Armenian) • Català (Catalan) • Čeština (Czech) • Nederlands (Dutch) • Suomi (Finnish) • Español (Spanish) • Esperanto • Eesti (Estonian) • हिन्दी (Hindi) • Magyar (Hungarian) • Ido • Bahasa Indonesia (Indonesian) • Italiano (Italian) • 日本語 (Japanese) • ಕನ್ನಡ (Kannada) • 한국어 (Korean) • Kurdî / كوردی (Kurdish) • Limburgs (Limburgish) • Lietuvių (Lithuanian) • മലയാളം (Malayalam) • မြန်မာဘာသာ (Burmese) • Norsk Bokmål (Norwegian) • ଓଡ଼ିଆ (Odia) • فارسى (Persian) • Polski (Polish) • Português (Portuguese) • Română (Romanian) • Srpskohrvatski (Serbo-Croatian) • Svenska (Swedish) • தமிழ் (Tamil) • తెలుగు (Telugu) • ไทย (Thai) • Türkçe (Turkish) • Tiếng Việt (Vietnamese) • Oʻzbekcha / Ўзбекча (Uzbek)
    •Afrikaans • Shqip (Albanian) • العربية (Arabic) • Asturianu (Asturian) • Azərbaycan (Azeri) • Bahasa Melayu (Malay) • Euskara (Basque) • বাংলা (Bengali) • Brezhoneg (Breton) • Български (Bulgarian) • Hrvatski (Croatian) • Dansk (Danish) • Frysk (West Frisian) • Galego (Galician) • ქართული (Georgian) • עברית (Hebrew) • Íslenska (Icelandic) • Basa Jawa (Javanese) • Кыргызча (Kyrgyz) • ລາວ (Lao) • Latina (Latin) • Latviešu (Latvian) • Lombard • Bân-lâm-gú (Min Nan) • ဘာသာမန် (Mon) • Nynorsk (Norwegian) • Occitan • Oromoo (Oromo) • پښتو (Pashto) • ਪੰਜਾਬੀ (Punjabi) • Српски (Serbian) • လိၵ်ႈတႆ (Shan) • Sicilianu (Sicilian) • Simple English • Slovenčina (Slovak) • Kiswahili (Swahili) • Tagalog • Тоҷикӣ (Tajik) • Українська (Ukrainian) • اردو (Urdu) • Volapük • Walon (Walloon) • Cymraeg (Welsh)
    •Armãneashce (Aromanian) • Aymara • Беларуская (Belarusian) • Bosanski (Bosnian) • Bikol • Corsu (Corsican) • Føroyskt (Faroese) • Fiji Hindi • Kalaallisut (Greenlandic) • Avañe'ẽ (Guaraní) • Interlingua • Interlingue • Gaeilge (Irish) • كٲشُر (Kashmiri) • Kaszëbsczi (Kashubian) • қазақша (Kazakh) • ភាសាខ្មែរ (Khmer) • Кыргызча (Kyrgyz) • Lëtzebuergesch (Luxembourgish) • Māori • Plattdüütsch (Low Saxon) • Македонски (Macedonian) • Malti (Maltese) • मराठी (Marathi) • Nahuatl • नेपाली (Nepali) • Li Niha (Nias) • Ænglisc (Old English) • Gàidhlig (Scottish Gaelic) • Tacawit (Shawiya) • سنڌي (Sindhi) • සිංහල (Sinhalese) • Slovenščina (Slovene) • Soomaaliga (Somali) • Hornjoserbsce (Upper Sorbian) • seSotho (Southern Sotho) • Basa Sunda (Sundanese) • Tatarça / Татарча (Tatar) • تركمن / Туркмен (Turkmen) • Uyghurche / ئۇيغۇرچە (Uyghur) • پنجابی (Western Punjabi) • Wollof (Wolof) • isiZulu (Zulu)
    •አማርኛ (Amharic) • Aragonés (Aragonese) • ᏣᎳᎩ (Cherokee) • Kernewek / Karnuack (Cornish) • ދިވެހިބަސް (Divehi) • ગુજરાતી (Gujarati) • Hausa / هَوُسَ (Hausa) • ʻŌlelo Hawaiʻi (Hawaiian) • ᐃᓄᒃᑎᑐᑦ (Inuktitut) • Ikinyarwanda (Kinyarwanda) • Lingala • Gaelg (Manx) • Монгол (Mongolian) • Runa Simi (Quechua) • Gagana Samoa (Samoan) • Sängö • Setswana • ትግርኛ (Tigrinya) • Tok Pisin • Xitsonga (Tsonga) • ייִדיש (Yiddish)
    """
    MINIMUM_CHARS_TO_BE_CYRILLIC = 20

    def __init__(self,
                 parent_widget: QWidget,
                 settings: settings_cls.Settings,
                 search_string: str = None,
                 syn_list: str = "",
                 image_list: list = None,
                 update_def_function = None,
                 caller_class_id: int = None):
        
        self._dont_clear_menu = False

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget)

        uic.loadUi(self.getv("def_finder_ui_file_path"), self)

        # Define variables
        self.parent_widget = parent_widget
        self.caller_class_id = caller_class_id
        self.search_string = search_string
        self.update_def_function = update_def_function
        self.include_syn = None
        self.include_img = None
        self.include_txt = None
        self.ignore_list = []

        self.existing_images = image_list if image_list else []
        self.data = {
            "syn": [],
            "text": "",
            "images": []
        }
        # Add existing synonyms as name = @@@
        self.data["syn"].append(SynHead(name=self.DEFAULT_SYNONYMS_KEY, source=self.getl("def_finder_syn_source_default"), is_enabled=True, syn_items=self._format_synonym_list(syn_list)))

        self.html_parser = html_parser_cls.HtmlParser()
        self.syn_manager = None

        self._define_widgets()
        self.load_widgets_handler()
        self._load_def_finder_settings()
        if self.search_string:
            self.txt_head_def.setText(self.search_string)

        self.update_widget_apperance()

        # Connect events with slots
        self.keyPressEvent = self._key_press_event
        self.frm_head_syn.mousePressEvent = self.frm_head_syn_click
        self.frm_head_img.mousePressEvent = self.frm_head_img_click
        self.frm_head_txt.mousePressEvent = self.frm_head_txt_click
        self.lbl_syn_enabled.mousePressEvent = self.frm_head_syn_click
        self.lbl_img_enabled.mousePressEvent = self.frm_head_img_click
        self.lbl_txt_enabled.mousePressEvent = self.frm_head_txt_click
        self.lbl_txt_alphabet_conversion.mousePressEvent = self.lbl_txt_alphabet_conversion_click
        
        self.lbl_settings.mousePressEvent = self.lbl_settings_click
        self.txt_head_def.textChanged.connect(self.txt_head_def_text_changed)
        self.btn_head_find.clicked.connect(self.btn_head_find_click)
        self.btn_head_find_syn.clicked.connect(self.btn_head_find_syn_click)
        self.txt_head_def.returnPressed.connect(self.txt_head_def_return_press)
        self.btn_head_update.clicked.connect(self.btn_head_update_click)

        self.btn_syn_more.clicked.connect(self.btn_syn_more_click)
        self.btn_syn_copy.clicked.connect(self.btn_syn_copy_click)
        self.lst_syn.itemChanged.connect(self.lst_syn_item_changed)
        self.lbl_lst_syn_all.mousePressEvent = lambda e: self._change_state_syn_list_items(Qt.Checked, e)
        self.lbl_lst_syn_none.mousePressEvent = lambda e: self._change_state_syn_list_items(Qt.Unchecked, e)
        self.lst_syn.mouseDoubleClickEvent = self.lst_syn_mouse_double_click

        # Settings
        self.btn_settings_txt_ignore_edit.clicked.connect(self.btn_settings_txt_ignore_edit_click)
        self.lbl_settings_txt_info_pic.mousePressEvent = self.lbl_settings_txt_info_pic_click

        # Ignore frame
        self.btn_txt_ignore_close.clicked.connect(self.btn_txt_ignore_close_click)
        self.btn_txt_ignore_add.clicked.connect(self.btn_txt_ignore_add_click)
        self.lst_txt_ignore.contextMenuEvent = self.lst_txt_ignore_context_menu
        self.txt_txt_ignore_section.textChanged.connect(self.txt_txt_ignore_section_text_changed)
        self.rbt_settings_txt_all.toggled.connect(self.rbt_settings_txt_all_toggled)
        self.rbt_settings_txt_ignore.toggled.connect(self.rbt_settings_txt_all_toggled)

        # Section frame
        self.btn_section_close.clicked.connect(self.btn_section_close_click)
        self.btn_section_select.clicked.connect(self._setting_section_set_cur_item)
        self.lst_section.mouseDoubleClickEvent = self._setting_section_set_cur_item

        # Expression frame
        self.btn_expression_close.clicked.connect(self.btn_expression_close_click)
        self.btn_expression_select.clicked.connect(self._expression_set_cur_item)
        self.txt_expression.returnPressed.connect(self._expression_set_cur_item)
        self.lst_expression.mouseDoubleClickEvent = self._expression_set_cur_item
        self.lst_expression.mousePressEvent = self._expression_select_cur_item
        
        self.show()
        UTILS.LogHandler.add_log_record("#1: Dialog started.", ["DefinitionFinder"])

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title])

        # Add frames
        frm_expression = self.widget_handler.add_QFrame(self.frm_expression)
        frm_expression.add_window_drag_widgets([self.frm_expression, self.lbl_expression_title])

        frm_settings = self.widget_handler.add_QFrame(self.frm_settings)
        frm_settings.add_window_drag_widgets([self.frm_settings, self.lbl_settings_title])

        frm_section = self.widget_handler.add_QFrame(self.frm_section)
        frm_section.add_window_drag_widgets([self.frm_section, self.lbl_section_title])

        frm_txt_ignore = self.widget_handler.add_QFrame(self.frm_txt_ignore)
        frm_txt_ignore.add_window_drag_widgets([self.frm_txt_ignore, self.lbl_txt_ignore_title])

        # Add all Pushbuttons
        self.widget_handler.add_all_QPushButtons(starting_widget=self)

        # Add Labels as PushButtons
        self.widget_handler.add_QPushButton(self.lbl_syn_enabled, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_img_enabled, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_txt_enabled, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_settings, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_lst_syn_all, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_lst_syn_none, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_settings_txt_info_pic, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.lbl_txt_alphabet_conversion, {"allow_bypass_mouse_press_event": False})

        # Add Action Frames
        self.widget_handler.add_ActionFrame(self.frm_head_syn, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_ActionFrame(self.frm_head_img, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_ActionFrame(self.frm_head_txt, {"allow_bypass_mouse_press_event": False})

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_head_def, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_expression, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_txt_ignore_section, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_txt, {"allow_bypass_mouse_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # Add Item Based Widgets
        self.widget_handler.add_all_ItemBased_Widgets()
        lst_expression: qwidgets_util_cls.Widget_ItemBased = self.widget_handler.find_child(self.lst_expression)
        lst_expression.properties.allow_bypass_mouse_press_event = False

        self.widget_handler.activate()

    def lbl_txt_alphabet_conversion_click(self, e: QMouseEvent):
        text = self.txt_txt.toPlainText()
        if not text.strip():
            return
    
        self.widget_handler.find_child(self.lbl_txt_alphabet_conversion).EVENT_mouse_press_event(e)

        if e.button() == Qt.LeftButton:
            if self.da_li_je_cirilica(text):
                self.txt_txt.setText(self.cirilica_u_latinicu(text))
            else:
                self.txt_txt.setText(self.latinica_u_cirilicu(text))
        elif e.button() == Qt.RightButton:
            self.txt_txt.setText(self.cirilica_u_latinicu(text))

    def btn_syn_copy_click(self):
        syns = self._get_syn_from_lst_syn()
        self.get_appv("clipboard").setText(syns)

    def _key_press_event(self, btn: QtGui.QKeyEvent):
        if btn.key() == Qt.Key_Escape:
            if self.frm_txt_ignore.isVisible():
                btn.accept()
                self.frm_txt_ignore.setVisible(False)
                return None
            elif self.frm_section.isVisible():
                btn.accept()
                self.frm_section.setVisible(False)
                return None
            elif self.frm_settings.isVisible():
                btn.accept()
                self.frm_settings.setVisible(False)
                return None
            elif self.frm_expression.isVisible():
                btn.accept()
                self.frm_expression.setVisible(False)
                return None
            else:
                self.close()

    def _expression_select_cur_item(self, e: QMouseEvent):
        QListWidget.mousePressEvent(self.lst_expression, e)
        self.widget_handler.find_child(self.lst_expression).EVENT_mouse_press_event(e)

        cur_item = self.lst_expression.currentItem()
        if not cur_item:
            return
        
        self.txt_expression.setText(cur_item.text())

    def btn_expression_close_click(self):
        self.frm_expression.setVisible(False)

    def _setting_section_set_cur_item(self, x = None):
        if not self.lst_section.currentItem():
            return
        text = self.lst_section.currentItem().data(Qt.UserRole)
        self.txt_settings_syn_section.setText(text)
        self.frm_section.setVisible(False)

    def btn_section_close_click(self):
        self.frm_section.setVisible(False)

    def lbl_settings_txt_info_pic_click(self, e: QMouseEvent):
        if not self.lst_section.count():
            self._populate_section_list()
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_settings_txt_info_pic).EVENT_mouse_press_event(e)

            self.frm_section.raise_()
            self.frm_section.setVisible(not self.frm_section.isVisible())

    def _populate_section_list(self):
        colors = [
            "#ffff00",
            "#00ff00",
            "#00ffff",
            "#9272b9",
            "#a63400",
            "#660000"
        ]

        self.lbl_section_legend1.setStyleSheet(f"background-color: {colors[0]}; color: rgb(0, 0, 0);")
        self.lbl_section_legend2.setStyleSheet(f"background-color: {colors[1]}; color: rgb(0, 0, 0);")
        self.lbl_section_legend3.setStyleSheet(f"background-color: {colors[2]}; color: rgb(0, 0, 0);")
        self.lbl_section_legend4.setStyleSheet(f"background-color: {colors[3]};")
        self.lbl_section_legend5.setStyleSheet(f"background-color: {colors[4]};")
        self.lbl_section_legend6.setStyleSheet(f"background-color: {colors[5]};")
        self.lbl_section_legend1.setToolTip(f'<font color=black>{self.getl("def_finder_lbl_section_legend1_text")}</font>')
        self.lbl_section_legend2.setToolTip(f'<font color=black>{self.getl("def_finder_lbl_section_legend2_text")}</font>')
        self.lbl_section_legend3.setToolTip(f'<font color=black>{self.getl("def_finder_lbl_section_legend3_text")}</font>')
        self.lbl_section_legend4.setToolTip(self.getl("def_finder_lbl_section_legend4_text"))
        self.lbl_section_legend5.setToolTip(self.getl("def_finder_lbl_section_legend5_text"))
        self.lbl_section_legend6.setToolTip(self.getl("def_finder_lbl_section_legend6_text"))

        sections = [x for x in self.LANG_SECTIONS.splitlines() if x.strip()]
        sec_data = []
        
        for idx, section in enumerate(sections):
            sec_data += [[x.strip(), idx] for x in section.split("•") if x.strip()]
        
        sec_list = []
        for section in sec_data:
            name = section[0]
            data = section[0]
            cat = section[1]
            start = section[0].find("(")
            if start != -1:
                end = section[0].find(")", start)
                if end == -1:
                    print (f"Invalid section data: {section}")
                    continue
                data = section[0][start+1:end].strip()
                name = data + " (" + section[0][:start].strip() + ")"
            sec_list.append([name, data, cat])

        sec_list.sort(key=lambda x: x[1])

        self.lst_section.clear()

        for section in sec_list:
            data = section[1]
            name = section[0]
            item = QListWidgetItem()
            item.setText(name)
            item.setData(Qt.UserRole, data)
            item.setForeground(QColor(colors[section[2]]))
            font = item.font()
            if section[2] < 2:
                font.setBold(True)
            font.setPointSize(12 + (6 - section[2]) * 2)
            item.setFont(font)

            self.lst_section.addItem(item)

    def btn_head_update_click(self):
        if not self.update_def_function:
            return
        
        if self.chk_settings_confirmation.isChecked():
            result = self._ask_update_confirmation()
            if not result:
                return
            
        images = []
        for i in range(self.area_images_widget_layout.count()):
            if self.area_images_widget_layout.itemAt(i).widget().is_active:
                images.append(self.area_images_widget_layout.itemAt(i).widget().img_src)

        syns = self._get_syn_from_lst_syn()

        data = {
            "update_text": self.include_txt,
            "update_images": self.include_img,
            "update_syn": self.include_syn,
            "text": self.txt_txt.toPlainText(),
            "images": images,
            "syn": syns,
            "replace_images": self.rbt_settings_img_replace.isChecked(),
            "append_syn": self.rbt_settings_syn_append.isChecked(),
            "caller_id": self.caller_class_id
        }
        
        self.frm_progress.raise_()
        self.frm_progress.setVisible(True)
        self.lbl_progress_info.setText(self.getl("def_finder_lbl_progress_updating_msg"))
        QCoreApplication.processEvents()

        self.update_def_function(data)
        
        UTILS.LogHandler.add_log_record("#1: Definition data updated.", ["DefinitionFinder"])

        self.frm_progress.setVisible(False)

        if self.chk_settings_auto_close.isChecked():
            self.close()
            return
        
        data = {"return_data": True, "caller_id": self.caller_class_id}
        result = self.update_def_function(data)
        if not result:
            self.close()
            return
        while len(self.data["syn"]) > 1:
            self.data["syn"].pop()

        self.data["syn"][0].items = self._format_synonym_list(result[0])
        self.data["syn"][0].is_enabled = True
        self.existing_images = result[1]
        self.syn_frame.setVisible(False)
        self._populate_syn_list()
        self.syn_manager = None
        UTILS.LogHandler.add_log_record("#1: The dialog has synchronized the data with the current definition.", ["DefinitionFinder"])

    def _get_syn_from_lst_syn(self) -> str:
        syns_list = []
        for i in range(self.lst_syn.count()):
            if self.lst_syn.item(i).checkState() == Qt.Checked:
                serbian = self.lst_syn.item(i).text()
                no_serbian = self.clear_serbian_chars(self.lst_syn.item(i).text())
                if serbian not in syns_list:
                    syns_list.append(serbian)
                if no_serbian not in syns_list and self.chk_settings_no_serbian.isChecked():
                    syns_list.append(no_serbian)
        if syns_list:
            syns_list.sort()
            syns = "\n".join(syns_list) + "\n"
        else:
            syns = ""

        return syns

    def _ask_update_confirmation(self) -> bool:
        data = {
            "title": self.getl("def_finder_update_msg_title"),
            "text": self.getl("def_finder_update_msg_text"),
            "icon_path": self.getv("messagebox_question_icon_path"),
            "buttons": [
                [10, self.getl("btn_yes"), "", None, True],
                [20, self.getl("btn_no"), "", None, True],
                [30, self.getl("btn_cancel"), "", None, True]
            ]
        }
        self._dont_clear_menu = True
        utility_cls.MessageQuestion(self._stt, self, data, True)
        if data["result"] == 10:
            return True
        return False

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

    def lst_syn_mouse_double_click(self, e: QMouseEvent):
        cur = self.lst_syn.currentItem()
        if not cur:
            return
        
        if cur.checkState() == Qt.Checked:
            cur.setCheckState(Qt.Unchecked)
        else:
            cur.setCheckState(Qt.Checked)

    def _change_state_syn_list_items(self, new_state: int, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            if new_state == Qt.Checked:
                self.widget_handler.find_child(self.lbl_lst_syn_all).EVENT_mouse_press_event(e)
            elif new_state == Qt.Unchecked:
                self.widget_handler.find_child(self.lbl_lst_syn_none).EVENT_mouse_press_event(e)

            for idx in range(self.lst_syn.count()):
                self.lst_syn.item(idx).setCheckState(new_state)

    def lst_syn_item_changed(self, item: QListWidgetItem):
        if self._dont_clear_menu:
            self._dont_clear_menu = False
            return
        
        if not item:
            return
        
        data: SynItem = item.data(Qt.UserRole)
        if item.checkState() == Qt.Checked:
            data.is_enabled = True
        else:
            data.is_enabled = False
        
        self._dont_clear_menu = True
        self._colorize_syn_item(item, data)
        self._dont_clear_menu = False
        if self.syn_manager:
            self.syn_manager.update_item(data)

    def update_syn_list_item(self, item: SynItem = None):
        if item is None:
            self._populate_syn_list()
            return
        
        for idx in range(self.lst_syn.count()):
            lst_item = self.lst_syn.item(idx)
            lst_item_data = self.lst_syn.item(idx).data(Qt.UserRole)
            if lst_item_data.head == item.head and lst_item_data.name == item.name:
                if item.is_enabled:
                    lst_item.setCheckState(Qt.Checked)
                else:
                    lst_item.setCheckState(Qt.Unchecked)
                self._colorize_syn_item(self.lst_syn.item(idx), lst_item_data)
    
    def btn_head_find_syn_click(self):
        self._show_expression_frame(self.txt_head_def.text())

    def txt_head_def_return_press(self):
        text = self.txt_head_def.text()
        if self.txt_head_def.selectedText():
            text = self.txt_head_def.selectedText()
        else:
            if text.startswith("https") and "wikipedia.org" in text:
                self.search_feedback(text)
                return

        self._show_expression_frame(text)

    def _show_expression_frame(self, text: str):
        color_def = "#ffff00"
        color_other = "#00ff00"

        def_text = self.txt_head_def.text().strip()
        replace_chars = "~!@#$%^&*()_+=-`{}[]:\"|\\';,./?><"
        for char in replace_chars:
            def_text = def_text.replace(char, " ")
        exp_list = [x.strip() for x in def_text.split(" ") if len(x) > 2]
        
        def_text = self.txt_head_def.text().strip()
        if len(exp_list) > 1:
            exp_list.insert(0, def_text)

        self.txt_expression.setText(text)

        self.lst_expression.clear()

        for expression in exp_list:
            item = QListWidgetItem()
            item.setText(expression)
            if expression == text:
                item.setForeground(QColor(color_def))
            else:
                item.setForeground(QColor(color_other))
            self.lst_expression.addItem(item)

        self.frm_expression.raise_()
        self.frm_expression.setVisible(True)
        self.btn_expression_select.setFocus()
        
    def _expression_set_cur_item(self, x = None):
        if x:
            QListWidget.mouseDoubleClickEvent(self.lst_expression, x)

        self.frm_expression.setDisabled(True)
        QCoreApplication.processEvents()
        result = self._load_synonyms_for_expression()
        self.frm_expression.setDisabled(False)
        UTILS.LogHandler.add_log_record("#1: Search synonyms for expression #2.", ["DefinitionFinder", self.txt_expression.text().strip()])
        if result:
            self.frm_expression.setVisible(False)
            UTILS.LogHandler.add_log_record("#1: Search for synonyms was successful.", ["DefinitionFinder"])
        else:
            self.frm_expression.setVisible(True)
            UTILS.LogHandler.add_log_record("#1: Search for synonyms failed.", ["DefinitionFinder"])
    
    def _load_synonyms_for_expression(self):
        text = self.txt_expression.text().strip()
        if not text:
            return
        
        result = self.load_synonyms_data(text=text)
        if not result:
            self._show_no_data_msg()
        else:
            self.frm_search_results.setVisible(False)
            self.syn_frame.raise_()
            self.syn_frame.setVisible(True)
        return result

    def btn_syn_more_click(self):
        if self.syn_manager:
            self.syn_frame.raise_()
            self.syn_frame.setVisible(not self.syn_frame.isVisible())

    def _format_synonym_list(self, syn_list: str) -> list:
        result_set = set([x.lower() for x in syn_list.splitlines() if x.strip()])
        result_list = list(result_set)
        result_list.sort()
        result = []
        for item in result_list:
            result.append(SynItem(name=item, is_enabled=True, head=self.DEFAULT_SYNONYMS_KEY))

        return result

    def rbt_settings_txt_all_toggled(self):
        self.update_widget_apperance()

    def txt_txt_ignore_section_text_changed(self):
        self.update_widget_apperance()

    def btn_txt_ignore_add_click(self):
        if not self.txt_txt_ignore_section.text().strip():
            return
        
        text = self.txt_txt_ignore_section.text()
        
        if self.chk_txt_ignore_after.isChecked():
            text += self.IGNORE_AFTER_MARKER

        self.txt_txt_ignore_section.setText("")
        
        if text in self.ignore_list:
            return

        self.ignore_list.append(text)
        
        self.update_widget_apperance()

    def lst_txt_ignore_context_menu(self, e):
        if not self.lst_txt_ignore.currentItem():
            return
        
        curr_item_text = self.lst_txt_ignore.currentItem().text()
        menu_data = {
            "position": QCursor.pos(),
            "items":[
                [
                    10,
                    self.getl("def_finder_lst_txt_ignore_menu_remove_item_text"),
                    "",
                    True,
                    [],
                    None
                ]
            ]
        }
        self.set_appv("menu", menu_data)
        self._dont_clear_menu = True
        utility_cls.ContextMenu(self._stt, self)
        result = menu_data["result"]
        if result == 10:
            for idx, i in enumerate(self.ignore_list):
                if i == curr_item_text:
                    self.ignore_list.pop(idx)
                    break
        self.update_widget_apperance()

    def btn_txt_ignore_close_click(self):
        self.frm_txt_ignore.setVisible(False)

    def btn_settings_txt_ignore_edit_click(self):
        self.frm_txt_ignore.raise_()
        self.frm_txt_ignore.setVisible(not self.frm_txt_ignore.isVisible())

    def btn_head_find_click(self):
        search_string = self.txt_head_def.text()
        if not search_string:
            return
        
        search_string = f"{self.getv('definition_data_find_search_prefix')} {search_string} {self.getv('definition_data_find_search_suffix')}"

        info_msg = self.getl("def_finder_progress_wiki_pages_search")
        self.lbl_progress_info.setText(info_msg)
        self.frm_progress.setVisible(True)
        self.frm_progress.raise_()
        QCoreApplication.processEvents()

        wiki = wikipedia_cls.Wikipedia(self, self._stt, auto_show_dialog=False)
        search_data = wiki.get_search_results(query_string=search_string, engines=["duck", "yahoo", "brave"])

        info_msg += "\n" + self.getl("def_finder_progress_preparing_search_results")
        self.lbl_progress_info.setText(info_msg)
        QCoreApplication.processEvents()

        card_settings = {
            "width": self.frm_search_results.width() - 20,
            "search_string": search_string,
            "supported": ["wikipedia.org"],
            "feedback": self.search_feedback,
            "title": self.getl("def_finder_search_title_text"),
            "only_valid_links": True
        }

        self.area_search_widget = QWidget()
        self.area_search_widget_layout = QVBoxLayout()
        self.area_search_widget.setLayout(self.area_search_widget_layout)
        self.area_search.setWidget(self.area_search_widget)
        # Set margins to 0
        self.area_search_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.area_search.setContentsMargins(0, 0, 0, 0)

        self.search_card = wikipedia_cls.SearchCard(self.area_search_widget, self._stt, search_data=search_data, card_setting=card_settings)
        self.area_search_widget_layout.addWidget(self.search_card)
        self.area_search_widget.resize(self.search_card.width(), self.search_card.height())

        self.frm_search_results.setVisible(True)
        self.syn_frame.setVisible(False)

        self.frm_progress.setVisible(False)
        UTILS.LogHandler.add_log_record("#1: Search expression on internet triggered.", ["DefinitionFinder"], variables=[["Search string", search_string]])

    def search_feedback(self, url: str):
        if "wikipedia.org" in url:
            has_data = self.load_definition_data(url)
            if has_data:
                self.frm_search_results.setVisible(False)
            else:
                self._show_no_data_msg()
    
    def load_synonyms_data(self, text: str = None) -> bool:
        self.frm_progress.setVisible(True)
        self.frm_progress.raise_()

        progress_text = self.getl("def_finder_progress_msg_loading_syn")
        self.lbl_progress_info.setText(progress_text)
        QCoreApplication.processEvents()

        # Get synonyms
        has_syn_data = self._get_synonyms_data(text=text)

        self.frm_progress.setVisible(False)
        if not has_syn_data:
            return False

        return True

    def load_definition_data(self, url: str) -> bool:
        self.frm_progress.setVisible(True)
        self.frm_progress.raise_()

        progress_text = self.getl("def_finder_progress_msg_loading_syn")
        self.lbl_progress_info.setText(progress_text)
        QCoreApplication.processEvents()

        # Get synonyms
        has_syn_data = self._get_synonyms_data()

        if has_syn_data:
            progress_text += f" {self.getl('def_finder_progress_msg_found')} ... {self.getl('def_finder_progress_msg_done')}."
        else:
            progress_text += f" {self.getl('def_finder_progress_msg_done')}."
        progress_text += "\n" + self.getl("def_finder_progress_msg_loading_wikidata")
        self.lbl_progress_info.setText(progress_text)
        QCoreApplication.processEvents()

        # Get wiki data
        data = wikipedia_card_cls.WikiData(url=url)

        progress_text += f" {self.getl('def_finder_progress_msg_done')}."
        progress_text += "\n" + self.getl("def_finder_progress_msg_loading_text")
        self.lbl_progress_info.setText(progress_text)
        QCoreApplication.processEvents()
        
        # Get Text
        def_text = self._get_def_text(data)

        progress_text += f" {self.getl('def_finder_progress_msg_done')}."
        progress_text += "\n" + self.getl("def_finder_progress_msg_loading_images")
        self.lbl_progress_info.setText(progress_text)
        QCoreApplication.processEvents()

        # Get Images
        def_images = self._get_def_images(data)

        progress_text += f" {self.getl('def_finder_progress_msg_done')}."
        progress_text += "\n" + self.getl("def_finder_progress_msg_loading_completed")
        self.lbl_progress_info.setText(progress_text)
        QCoreApplication.processEvents()
        time.sleep(2)

        self.frm_progress.setVisible(False)
        if not data.has_page and not has_syn_data:
            return False

        self.data["text"] = def_text
        self.data["images"] = def_images

        return True

    def _get_synonyms_data(self, text: str = None) -> bool:
        if not text:
            text = self.txt_head_def.text()

        text = text.lower()

        while len(self.data["syn"]) > 1:
            self.data["syn"].pop()

        self.syn_manager = SynonymManager(parent_widget=self.syn_area_widget, 
                                          settings=self._stt, 
                                          data=self.data, 
                                          default_synonym_key=self.DEFAULT_SYNONYMS_KEY,
                                           expression=text,
                                           section=self.txt_settings_syn_section.text(),
                                           update_parent_list_function=self.update_syn_list_item)
        self._populate_syn_list()
        return self.syn_manager.has_data

    def _populate_syn_list(self):
        if not self.syn_manager:
            return
        
        self.lst_syn.clear()

        head_list = self.syn_manager._get_list_of_headitems()

        total_count = 0
        enabled_count = 0

        for head in head_list:
            if not head.items or not head.is_enabled:
                continue

            for item in head.items:
                item: SynItem
                lst_item = QListWidgetItem()
                lst_item.setText(item.name)
                lst_item.setData(Qt.UserRole, item)
                self._colorize_syn_item(lst_item, item)
                lst_item.setFlags(lst_item.flags() | Qt.ItemIsUserCheckable)
                if item.is_enabled:
                    lst_item.setCheckState(Qt.Checked)
                    enabled_count += 1
                else:
                    lst_item.setCheckState(Qt.Unchecked)
                
                self.lst_syn.addItem(lst_item)
                total_count += 1

        # Set last item as current item
        if self.lst_syn.count() > 0:
            self.lst_syn.setCurrentRow(self.lst_syn.count() - 1)

        text = self.getl("def_finder_lbl_syn_info_text").replace("#1", str(enabled_count)).replace("#2", str(total_count))
        self.lbl_syn_info.setText(text)

    def _colorize_syn_item(self, lst_item: QListWidgetItem, syn_item: SynItem):
        """
        Colorizes a QListWidgetItem based on the properties of a SynItem.

        Args:
            lst_item (QListWidgetItem): The QListWidgetItem to be colorized.
            syn_item (SynItem): The SynItem containing the properties for colorization.

        Returns:
            None
        """

        # Check if the SynItem is enabled
        if syn_item.is_enabled:
            # Check if there are more than one enabled SynItems with the same properties
            if self._count_items(syn_item, only_enabled=True) > 1:
                # Set color to COLOR_DOUBLE if there are duplicates
                color = QColor(self.COLOR_DOUBLE)
            else:
                # Set color to COLOR_NEW_ENABLED if there are no duplicates
                color = QColor(self.COLOR_NEW_ENABLED)
        else:
            # Set color to COLOR_NEW_DISABLED if SynItem is not enabled
            color = QColor(self.COLOR_NEW_DISABLED)

        # Check if the head of the SynItem is the default key
        if syn_item.head == self.DEFAULT_SYNONYMS_KEY:
            # Set color to COLOR_EXIST if head is the default key
            color = QColor(self.COLOR_EXIST)

        # Set the foreground color of the QListWidgetItem
        lst_item.setForeground(color)

    def _count_items(self, item_object: SynItem, only_enabled: bool = True) -> int:
        count = 0
        head_list = self.syn_manager._get_list_of_headitems()
        for head in head_list:
            head: SynHead
            for item in head.items:
                if item_object.name == item.name:
                    if only_enabled:
                        if item.is_enabled and head.is_enabled:
                            count += 1
                    else:
                        count += 1
        return count

    def _get_def_text(self, data: wikipedia_card_cls.WikiData) -> str:
        text = ""
        stop_section = False
        for section_item in data.data_content:
            section_title = self.html_parser.get_raw_text(load_html_code=section_item["text"]).strip()
            
            if section_title in self.ignore_list or section_title + self.IGNORE_AFTER_MARKER in self.ignore_list:
                if section_title + self.IGNORE_AFTER_MARKER in self.ignore_list:
                    stop_section = True
                continue
            if stop_section:
                continue
            
            text += section_title + "\n"
            
            for section in section_item["data"]:
                if section["type"] == "c_text" or section["type"] == "c_code":
                    text += self.html_parser.get_raw_text(load_html_code=section["text"]) + "\n"
                elif section["type"] == "c_list":
                    for i in section["text_list"]:
                        text += self.html_parser.get_raw_text(load_html_code=i) + "\n"
        self.txt_txt.setText(text)
        info_txt = self.getl("def_finder_lbl_txt_info_text").replace("#1", str(len(text))).replace("#2", str(self._count_words(text)))
        self.lbl_txt_info.setText(info_txt)

        return text

    def _count_words(self, text: str) -> int:
        replace_map = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        for char in replace_map:
            text = text.replace(char, " ")
        while True:
            if text.find("  ") == -1:
                break
            text = text.replace("  ", " ")
        return len(text.strip().split(" "))

    def _get_def_images(self, data: wikipedia_card_cls.WikiData) -> list:
        images = []

        for section_item in data.data_labels:
            for section in section_item["image"]:
                if section["src"] and section["image_w"] > 30 and section["image_h"] > 30 and section["link"]:
                    images.append({"image": section["src"], "link": section["link"]})

        for section_item in data.data_content:
            for section in section_item["data"]:
                if section["type"] == "c_table_presentation":
                    if section["image"] and section["image_w"] > 30 and section["image_h"] > 30:
                        image = self.html_parser.get_all_images(load_html_code=section["code"])
                        for img in image:
                            if img.img_link:
                                images.append({"image": img, "link": img.img_link})
                if section["type"] == "c_figure":
                    if section["image"] and section["image_w"] > 30 and section["image_h"] > 30 and section["image_link"]:
                        images.append({
                            "image": section["image"], 
                            "link": section["image_link"]
                        })

        # Create new widget for area
        self.area_images_widget = QWidget()
        self.area_images_widget_layout = QHBoxLayout()
        self.area_images_widget_layout.setContentsMargins(0,0,0,0)
        self.area_images_widget_layout.setSpacing(5)
        self.area_images.setWidget(self.area_images_widget)
        self.area_images_widget.setLayout(self.area_images_widget_layout)
        self.area_images.setWidgetResizable(True)
        self.area_images.show()
        
        # Add images
        total_images = len(images)
        count = 1
        label_text = self.lbl_progress_info.text()
        image_list = []
        count_existing = 0
        for image in images:
            image_number_text = f"{count}/{total_images}   "
            self.lbl_progress_info.setText(label_text + image_number_text)
            QCoreApplication.processEvents()

            
            html = data._load_url(image["link"])
            images_code = self.html_parser.get_tags(html_code=html, tag="div", tag_class_contains="resolutioninfo")
            if images_code:
                image_links = self.html_parser.get_all_links(load_html_code=images_code[0])
                if image_links:
                    image_link = image_links[-1]
                    if self.fix_url(image_link.a_href) in self.existing_images:
                        count_existing += 1
                    if self.fix_url(image_link.a_href) not in image_list and self.fix_url(image_link.a_href) not in self.existing_images:
                        image_item = ImageItem(self.area_images_widget, self._stt, self.fix_url(image_link.a_href))
                        self.area_images_widget_layout.addWidget(image_item)
                        image_item.show()
                        image_list.append(self.fix_url(image_link.a_href))
                else:
                    largest_image = self._get_largest_image(html)
                    if largest_image:
                        image_link = largest_image
                        if self.fix_url(image_link.img_src) in self.existing_images:
                            count_existing += 1
                        if self.fix_url(image_link.img_src) not in image_list and self.fix_url(image_link.img_src) not in self.existing_images:
                            image_item = ImageItem(self.area_images_widget, self._stt, self.fix_url(image_link.img_src))
                            self.area_images_widget_layout.addWidget(image_item)
                            image_item.show()
                            image_list.append(self.fix_url(image_link.img_src))
            count += 1
        
        info_txt = self.getl("def_finder_lbl_img_info_text").replace("#1", str(len(image_list)))
        if count_existing:
            info_txt += " " + self.getl("def_finder_lbl_img_info2_text").replace("#1", str(count_existing))

        self.lbl_img_info.setText(info_txt)
        return image_list

    def _get_largest_image(self, html: str) -> html_parser_cls.ImageObject:
        images = self.html_parser.get_all_images(load_html_code=html)
        img_obj = None
        size = 0
        for image in images:
            image: html_parser_cls.ImageObject
            if image.img_width and image.img_height:
                image_size = image.img_height * image.img_width
                if image_size > size:
                    img_obj = image
                    size = image_size
        return img_obj

    def _show_no_data_msg(self):
        data = {
            "title": self.getl("def_finder_no_data_title"),
            "text": self.getl("def_finder_no_data_text")
        }
        self._dont_clear_menu = True
        utility_cls.MessageInformation(self._stt, self, data_dict=data, app_modal=True)

    def fix_url(self, url: str) -> str:
        result = url
        if url.startswith("//"):
            result = "https:" + url
        elif url.startswith("/"):
            result = "https://wikipedia.org" + url
        return result

    def txt_head_def_text_changed(self):
        self.update_widget_apperance()

    def lbl_settings_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.lbl_settings).EVENT_mouse_press_event(e)

            self.frm_settings.raise_()
            self.frm_settings.setVisible(not self.frm_settings.isVisible())
            if not self.frm_settings.isVisible():
                self.frm_txt_ignore.setVisible(False)

    def frm_head_txt_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.frm_head_txt).EVENT_mouse_press_event(e)
            self.widget_handler.find_child(self.lbl_txt_enabled).EVENT_mouse_press_event(e)

            self.include_txt = not self.include_txt
            self.update_widget_apperance()

    def frm_head_img_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.frm_head_img).EVENT_mouse_press_event(e)
            self.widget_handler.find_child(self.lbl_img_enabled).EVENT_mouse_press_event(e)

            self.include_img = not self.include_img
            self.update_widget_apperance()

    def frm_head_syn_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.frm_head_syn).EVENT_mouse_press_event(e)
            self.widget_handler.find_child(self.lbl_syn_enabled).EVENT_mouse_press_event(e)

            self.include_syn = not self.include_syn
            self.update_widget_apperance()

    def update_widget_apperance(self):
        has_action = False

        font = self.lbl_head_syn.font()
        if self.include_syn:
            has_action = True
            font.setBold(True)
            self.lbl_head_syn.setFont(font)
            self.lbl_head_syn_pic.setPixmap(QPixmap(self.getv("checked_icon_path")))
            self.lbl_syn_enabled.setPixmap(QPixmap(self.getv("thumb_up_icon_path")))
            self.frm_syn.setStyleSheet("background-color: rgb(0, 0, 108); color: rgb(209, 209, 209);")
        else:
            font.setBold(False)
            self.lbl_head_syn.setFont(font)
            self.lbl_head_syn_pic.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
            self.lbl_syn_enabled.setPixmap(QPixmap(self.getv("thumb_down_icon_path")))
            self.frm_syn.setStyleSheet("background-color: rgb(61, 61, 61); color: rgb(209, 209, 209);")
        
        font = self.lbl_head_img.font()
        if self.include_img:
            has_action = True
            font.setBold(True)
            self.lbl_head_img.setFont(font)
            self.lbl_head_img_pic.setPixmap(QPixmap(self.getv("checked_icon_path")))
            self.lbl_img_enabled.setPixmap(QPixmap(self.getv("thumb_up_icon_path")))
            self.frm_img.setStyleSheet("background-color: rgb(0, 0, 108); color: rgb(209, 209, 209);")
        else:
            font = self.lbl_head_img.font()
            font.setBold(False)
            self.lbl_head_img.setFont(font)
            self.lbl_head_img_pic.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
            self.lbl_img_enabled.setPixmap(QPixmap(self.getv("thumb_down_icon_path")))
            self.frm_img.setStyleSheet("background-color: rgb(61, 61, 61); color: rgb(209, 209, 209);")
        
        font = self.lbl_head_txt.font()
        if self.include_txt:
            has_action = True
            font.setBold(True)
            self.lbl_head_txt.setFont(font)
            self.lbl_head_txt_pic.setPixmap(QPixmap(self.getv("checked_icon_path")))
            self.lbl_txt_enabled.setPixmap(QPixmap(self.getv("thumb_up_icon_path")))
            self.frm_txt.setStyleSheet("background-color: rgb(0, 0, 108); color: rgb(209, 209, 209);")
        else:
            font.setBold(False)
            self.lbl_head_txt.setFont(font)
            self.lbl_head_txt_pic.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
            self.lbl_txt_enabled.setPixmap(QPixmap(self.getv("thumb_down_icon_path")))
            self.frm_txt.setStyleSheet("background-color: rgb(61, 61, 61); color: rgb(209, 209, 209);")

        self.btn_head_update.setEnabled(has_action)
        if has_action:
            self.btn_head_update.setStyleSheet("QPushButton {color: #00ff00; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        else:
            self.btn_head_update.setStyleSheet("QPushButton {color: #bdbdbd; background-color: #1e3c5b;}")

        if self.txt_head_def.text().strip():
            self.btn_head_find.setEnabled(True)
            self.btn_head_find.setStyleSheet("QPushButton {color: #00ff00; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
            self.btn_head_find_syn.setEnabled(True)
            self.btn_head_find_syn.setStyleSheet("QPushButton {color: #00ff00; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        else:
            self.btn_head_find.setEnabled(False)
            self.btn_head_find.setStyleSheet("QPushButton {color: #bdbdbd; background-color: #1e3c5b;}")
            self.btn_head_find_syn.setEnabled(False)
            self.btn_head_find_syn.setStyleSheet("QPushButton {color: #bdbdbd; background-color: #1e3c5b;}")
        
        # Edit Ignore list button
        if self.rbt_settings_txt_all.isChecked():
            self.btn_settings_txt_ignore_edit.setDisabled(True)
            self.btn_settings_txt_ignore_edit.setStyleSheet("QPushButton {color: #bdbdbd; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        else:
            self.btn_settings_txt_ignore_edit.setDisabled(False)
            self.btn_settings_txt_ignore_edit.setStyleSheet("QPushButton {color: #00ff00; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        
        # Add Ignore item button
        if self.txt_txt_ignore_section.text().strip():
            self.btn_txt_ignore_add.setDisabled(False)
            self.btn_txt_ignore_add.setStyleSheet("QPushButton {color: #00ff00; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        else:
            self.btn_txt_ignore_add.setDisabled(True)
            self.btn_txt_ignore_add.setStyleSheet("QPushButton {color: #bdbdbd; background-color: #1e3c5b;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")

        # Set ignore list to label
        ignore_text = ""
        text_to_html = utility_cls.TextToHTML()
        count = 1
        for i in self.ignore_list:
            rule_id = "#" + "-" * (5 - len(str(count)))  + str(count)
            if self.IGNORE_AFTER_MARKER in i:
                color = "#ff0000"
            else:
                color = "#c9c9ff"
            rule = utility_cls.TextToHtmlRule(
                text=rule_id,
                replace_with=i,
                fg_color=color
            )
            text_to_html.add_rule(rule)
            ignore_text += rule_id + ", "
            count += 1
        if self.ignore_list:
            ignore_text = ignore_text[:-2]
            text_to_html.set_text(ignore_text)
            ignore_text = text_to_html.get_html()

        self.lbl_settings_txt_ignored.setText(ignore_text)

        # Set ignore list to QListWidget
        self.lst_txt_ignore.clear()
        for i in self.ignore_list:
            item = QListWidgetItem()
            item.setText(i)
            if self.IGNORE_AFTER_MARKER in i:
                item.setToolTip(self.getl("def_finder_lst_txt_ignore_item_tt_after_on").replace("#1", i))
                item.setForeground(QColor("#ff0000"))
            else:
                item.setToolTip(self.getl("def_finder_lst_txt_ignore_item_tt_after_off").replace("#1", i))
                item.setForeground(QColor("#97ffeb"))
            self.lst_txt_ignore.addItem(item)

    def _load_def_finder_settings(self):
        if "def_finder_settings" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("def_finder_settings")
            self.move(g["pos_x"], g["pos_y"])
        else:
            g = {}
            g["pos_x"] = self.pos().x()
            g["pos_y"] = self.pos().y()

        self.include_syn = g.get("include_syn", True)
        self.include_img = g.get("include_img", True)
        self.include_txt = g.get("include_txt", True)

        self.rbt_settings_syn_append.setChecked(g.get("append_syn", True))
        self.rbt_settings_syn_replace.setChecked(not self.rbt_settings_syn_append.isChecked())
        self.txt_settings_syn_section.setText(g.get("syn_section", "Serbo-Croatian"))
        self.chk_settings_no_serbian.setChecked(g.get("add_no_serbian", False))

        self.rbt_settings_img_append.setChecked(g.get("append_img", True))
        self.rbt_settings_img_replace.setChecked(not self.rbt_settings_img_append.isChecked())

        self.chk_settings_confirmation.setChecked(g.get("confirmation", True))
        self.chk_settings_auto_close.setChecked(g.get("auto_close", True))

        self.rbt_settings_txt_all.setChecked(g.get("select_all_text", True))
        self.rbt_settings_txt_ignore.setChecked(not g.get("select_all_text", True))
        self.ignore_list = g.get("ignore_sections_list", [])
        self.chk_txt_ignore_after.setChecked(g.get("ignore_after_section", False))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        if "def_finder_settings" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("def_finder_settings", {}, save_to_file=True)

        g = self.get_appv("def_finder_settings")
        if not self.isMinimized() and not self.isMaximized():
            g["pos_x"] = self.pos().x()
            g["pos_y"] = self.pos().y()

            g["include_syn"] = self.include_syn
            g["include_img"] = self.include_img
            g["include_txt"] = self.include_txt

            g["append_syn"] = self.rbt_settings_syn_append.isChecked()
            g["append_img"] = self.rbt_settings_img_append.isChecked()
            g["syn_section"] = self.txt_settings_syn_section.text()
            g["add_no_serbian"] = self.chk_settings_no_serbian.isChecked()

            g["confirmation"] = self.chk_settings_confirmation.isChecked()
            g["auto_close"] = self.chk_settings_auto_close.isChecked()

            g["select_all_text"] = self.rbt_settings_txt_all.isChecked()
            g["ignore_sections_list"] = self.ignore_list
            g["ignore_after_section"] = self.chk_txt_ignore_after.isChecked()

        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["DefinitionFinder"])
        self.get_appv("cm").remove_all_context_menu()
        UTILS.DialogUtility.on_closeEvent(self)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def _define_widgets(self):
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.lbl_wiki_logo: QLabel = self.findChild(QLabel, "lbl_wiki_logo")
        self.lbl_wiki_logo.setAlignment(Qt.AlignRight)
        self.lbl_wiki_logo.setScaledContents(True)
        wiki_movie = QMovie(self.getv("definition_finder_logo_animation_path"))
        self.lbl_wiki_logo.setMovie(wiki_movie)
        wiki_movie.start()
        
        # Head frame
        self.frm_head: QFrame = self.findChild(QFrame, "frm_head")
        self.lbl_head_def: QLabel = self.findChild(QLabel, "lbl_head_def")
        self.txt_head_def: QLineEdit = self.findChild(QLineEdit, "txt_head_def")
        self.btn_head_find: QPushButton = self.findChild(QPushButton, "btn_head_find")
        self.btn_head_find_syn: QPushButton = self.findChild(QPushButton, "btn_head_find_syn")
        self.lbl_settings: QLabel = self.findChild(QLabel, "lbl_settings")
        self.btn_head_update: QPushButton = self.findChild(QPushButton, "btn_head_update")
        
        self.frm_head_syn: QFrame = self.findChild(QFrame, "frm_head_syn")
        self.lbl_head_syn: QLabel = self.findChild(QLabel, "lbl_head_syn")
        self.lbl_head_syn_pic: QLabel = self.findChild(QLabel, "lbl_head_syn_pic")

        self.frm_head_img: QFrame = self.findChild(QFrame, "frm_head_img")
        self.lbl_head_img: QLabel = self.findChild(QLabel, "lbl_head_img")
        self.lbl_head_img_pic: QLabel = self.findChild(QLabel, "lbl_head_img_pic")

        self.frm_head_txt: QFrame = self.findChild(QFrame, "frm_head_txt")
        self.lbl_head_txt: QLabel = self.findChild(QLabel, "lbl_head_txt")
        self.lbl_head_txt_pic: QLabel = self.findChild(QLabel, "lbl_head_txt_pic")

        # Synonyms
        self.frm_syn: QFrame = self.findChild(QFrame, "frm_syn")
        self.lbl_syn_syn: QLabel = self.findChild(QLabel, "lbl_syn_syn")
        self.lbl_syn_info: QLabel = self.findChild(QLabel, "lbl_syn_info")
        self.lbl_syn_enabled: QLabel = self.findChild(QLabel, "lbl_syn_enabled")
        self.lst_syn: QListWidget = self.findChild(QListWidget, "lst_syn")
        self.btn_syn_more: QPushButton = self.findChild(QPushButton, "btn_syn_more")
        self.lbl_lst_syn_all: QLabel = self.findChild(QLabel, "lbl_lst_syn_all")
        self.lbl_lst_syn_none: QLabel = self.findChild(QLabel, "lbl_lst_syn_none")
        self.btn_syn_copy: QPushButton = self.findChild(QPushButton, "btn_syn_copy")

        # Images
        self.frm_img: QFrame = self.findChild(QFrame, "frm_img")
        self.lbl_img_img: QLabel = self.findChild(QLabel, "lbl_img_img")
        self.lbl_img_info: QLabel = self.findChild(QLabel, "lbl_img_info")
        self.lbl_img_enabled: QLabel = self.findChild(QLabel, "lbl_img_enabled")
        self.frm_img_pics: QFrame = self.findChild(QFrame, "frm_img_pics")

        # Text
        self.frm_txt: QFrame = self.findChild(QFrame, "frm_txt")
        self.lbl_txt_txt: QLabel = self.findChild(QLabel, "lbl_txt_txt")
        self.lbl_txt_info: QLabel = self.findChild(QLabel, "lbl_txt_info")
        self.lbl_txt_enabled: QLabel = self.findChild(QLabel, "lbl_txt_enabled")
        self.lbl_txt_alphabet_conversion: QLabel = self.findChild(QLabel, "lbl_txt_alphabet_conversion")
        self.txt_txt: QTextEdit = self.findChild(QTextEdit, "txt_txt")
        
        # Progress
        self.frm_progress: QFrame = self.findChild(QFrame, "frm_progress")
        self.lbl_progress_title: QLabel = self.findChild(QLabel, "lbl_progress_title")
        self.lbl_progress_info: QLabel = self.findChild(QLabel, "lbl_progress_info")

        # Settings
        self.frm_settings: QFrame = self.findChild(QFrame, "frm_settings")
        self.lbl_settings_title: QLabel = self.findChild(QLabel, "lbl_settings_title")
        self.grp_settings_syn: QGroupBox = self.findChild(QGroupBox, "grp_settings_syn")
        self.rbt_settings_syn_append: QRadioButton = self.findChild(QRadioButton, "rbt_settings_syn_append")
        self.rbt_settings_syn_replace: QRadioButton = self.findChild(QRadioButton, "rbt_settings_syn_replace")
        self.grp_settings_img: QGroupBox = self.findChild(QGroupBox, "grp_settings_img")
        self.rbt_settings_img_append: QRadioButton = self.findChild(QRadioButton, "rbt_settings_img_append")
        self.rbt_settings_img_replace: QRadioButton = self.findChild(QRadioButton, "rbt_settings_img_replace")
        self.chk_settings_confirmation: QCheckBox = self.findChild(QCheckBox, "chk_settings_confirmation")
        self.chk_settings_auto_close: QCheckBox = self.findChild(QCheckBox, "chk_settings_auto_close")
        self.grp_settings_txt: QGroupBox = self.findChild(QGroupBox, "grp_settings_txt")
        self.rbt_settings_txt_all: QRadioButton = self.findChild(QRadioButton, "rbt_settings_txt_all")
        self.rbt_settings_txt_ignore: QRadioButton = self.findChild(QRadioButton, "rbt_settings_txt_ignore")
        self.lbl_settings_txt_ignored: QLabel = self.findChild(QLabel, "lbl_settings_txt_ignored")
        self.btn_settings_txt_ignore_edit: QPushButton = self.findChild(QPushButton, "btn_settings_txt_ignore_edit")
        self.lbl_settings_syn_section: QLabel = self.findChild(QLabel, "lbl_settings_syn_section")
        self.txt_settings_syn_section: QLineEdit = self.findChild(QLineEdit, "txt_settings_syn_section")
        self.chk_settings_no_serbian: QCheckBox = self.findChild(QCheckBox, "chk_settings_no_serbian")
        self.lbl_settings_txt_info_pic: QLabel = self.findChild(QLabel, "lbl_settings_txt_info_pic")

        # Ignore list frame
        self.frm_txt_ignore: QFrame = self.findChild(QFrame, "frm_txt_ignore")
        self.lbl_txt_ignore_title: QLabel = self.findChild(QLabel, "lbl_txt_ignore_title")
        self.lbl_txt_ignore_section: QLabel = self.findChild(QLabel, "lbl_txt_ignore_section")
        self.txt_txt_ignore_section: QLineEdit = self.findChild(QLineEdit, "txt_txt_ignore_section")
        self.chk_txt_ignore_after: QCheckBox = self.findChild(QCheckBox, "chk_txt_ignore_after")
        self.btn_txt_ignore_add: QPushButton = self.findChild(QPushButton, "btn_txt_ignore_add")
        self.lst_txt_ignore: QListWidget = self.findChild(QListWidget, "lst_txt_ignore")
        self.btn_txt_ignore_close: QPushButton = self.findChild(QPushButton, "btn_txt_ignore_close")

        # Section selection
        self.frm_section: QFrame = self.findChild(QFrame, "frm_section")
        self.lbl_section_title: QLabel = self.findChild(QLabel, "lbl_section_title")
        self.btn_section_close: QPushButton = self.findChild(QPushButton, "btn_section_close")
        self.lst_section: QListWidget = self.findChild(QListWidget, "lst_section")
        self.btn_section_select: QPushButton = self.findChild(QPushButton, "btn_section_select")
        self.lbl_section_legend1: QLabel = self.findChild(QLabel, "lbl_section_legend1")
        self.lbl_section_legend2: QLabel = self.findChild(QLabel, "lbl_section_legend2")
        self.lbl_section_legend3: QLabel = self.findChild(QLabel, "lbl_section_legend3")
        self.lbl_section_legend4: QLabel = self.findChild(QLabel, "lbl_section_legend4")
        self.lbl_section_legend5: QLabel = self.findChild(QLabel, "lbl_section_legend5")
        self.lbl_section_legend6: QLabel = self.findChild(QLabel, "lbl_section_legend6")

        # Section expression
        self.frm_expression: QFrame = self.findChild(QFrame, "frm_expression")
        self.lbl_expression_title: QLabel = self.findChild(QLabel, "lbl_expression_title")
        self.lbl_expression_expression: QLabel = self.findChild(QLabel, "lbl_expression_expression")
        self.btn_expression_close: QPushButton = self.findChild(QPushButton, "btn_expression_close")
        self.lst_expression: QListWidget = self.findChild(QListWidget, "lst_expression")
        self.btn_expression_select: QPushButton = self.findChild(QPushButton, "btn_expression_select")
        self.txt_expression: QLineEdit = self.findChild(QLineEdit, "txt_expression")

        self._define_widgets_text()
        self._define_widgets_apperance()

    def _define_widgets_text(self):
        self.lbl_title.setText(self.getl("def_finder_lbl_title_text"))
        self.lbl_head_def.setText(self.getl("def_finder_lbl_head_def_text"))
        self.btn_head_find.setText(self.getl("def_finder_btn_head_find_text"))
        self.btn_head_find.setToolTip(self.getl("def_finder_btn_head_find_tt"))
        self.btn_head_find_syn.setText(self.getl("def_finder_btn_head_find_syn_text"))
        self.btn_head_find_syn.setToolTip(self.getl("def_finder_btn_head_find_syn_tt"))
        self.lbl_head_syn.setText(self.getl("def_finder_lbl_head_syn_text"))
        self.lbl_head_img.setText(self.getl("def_finder_lbl_head_img_text"))
        self.lbl_head_txt.setText(self.getl("def_finder_lbl_head_txt_text"))
        self.btn_head_update.setText(self.getl("def_finder_btn_head_update_text"))
        self.lbl_syn_syn.setText(self.getl("def_finder_lbl_head_syn_text"))
        self.lbl_img_img.setText(self.getl("def_finder_lbl_head_img_text"))
        self.lbl_txt_txt.setText(self.getl("def_finder_lbl_head_txt_text"))
        self.lbl_syn_info.setText("")
        self.lbl_img_info.setText("")
        self.lbl_txt_info.setText("")
        self.lbl_progress_title.setText(self.getl("def_finder_lbl_progress_title_text"))
        self.lbl_settings_title.setText(self.getl("def_finder_lbl_settings_title_text"))
        self.grp_settings_syn.setTitle(self.getl("def_finder_lbl_head_syn_text"))
        self.grp_settings_img.setTitle(self.getl("def_finder_lbl_head_img_text"))
        self.grp_settings_txt.setTitle(self.getl("def_finder_lbl_head_txt_text"))
        self.rbt_settings_syn_append.setText(self.getl("def_finder_rbt_settings_syn_append_text"))
        self.rbt_settings_syn_append.setToolTip(self.getl("def_finder_rbt_settings_syn_append_tt"))
        self.rbt_settings_syn_replace.setText(self.getl("def_finder_rbt_settings_syn_replace_text"))
        self.lbl_settings_syn_section.setText(self.getl("def_finder_lbl_settings_syn_section_text"))
        self.rbt_settings_img_append.setText(self.getl("def_finder_rbt_settings_img_append_text"))
        self.rbt_settings_img_append.setToolTip(self.getl("def_finder_rbt_settings_img_append_tt"))
        self.rbt_settings_img_replace.setText(self.getl("def_finder_rbt_settings_img_replace_text"))
        self.rbt_settings_img_replace.setToolTip(self.getl("def_finder_rbt_settings_img_replace_tt"))
        self.rbt_settings_txt_all.setText(self.getl("def_finder_rbt_settings_txt_all_text"))
        self.rbt_settings_txt_all.setToolTip(self.getl("def_finder_rbt_settings_txt_all_tt"))
        self.rbt_settings_txt_ignore.setText(self.getl("def_finder_rbt_settings_txt_ignore_text"))
        self.rbt_settings_txt_ignore.setToolTip(self.getl("def_finder_rbt_settings_txt_ignore_tt"))
        self.btn_settings_txt_ignore_edit.setText(self.getl("def_finder_btn_settings_txt_ignore_edit_text"))
        self.chk_settings_confirmation.setText(self.getl("def_finder_chk_settings_confirmation_text"))
        self.chk_settings_confirmation.setToolTip(self.getl("def_finder_chk_settings_confirmation_tt"))
        self.chk_settings_auto_close.setText(self.getl("def_finder_chk_settings_auto_close_text"))
        self.chk_settings_auto_close.setToolTip(self.getl("def_finder_chk_settings_auto_close_tt"))
        self.lbl_txt_ignore_title.setText(self.getl("def_finder_lbl_txt_ignore_title_text"))
        self.lbl_txt_ignore_section.setText(self.getl("def_finder_lbl_txt_ignore_section_text"))
        self.chk_txt_ignore_after.setText(self.getl("def_finder_chk_txt_ignore_after_text"))
        self.chk_txt_ignore_after.setToolTip(self.getl("def_finder_chk_txt_ignore_after_tt"))
        self.btn_txt_ignore_add.setText(self.getl("def_finder_btn_txt_ignore_add_text"))
        self.btn_syn_more.setText(self.getl("def_finder_btn_syn_more_text"))
        self.lbl_lst_syn_all.setToolTip(self.getl("def_finder_lbl_lst_syn_all_tt"))
        self.lbl_lst_syn_none.setToolTip(self.getl("def_finder_lbl_lst_syn_none_tt"))
        self.chk_settings_no_serbian.setText(self.getl("def_finder_chk_settings_no_serbian_text"))
        self.chk_settings_no_serbian.setToolTip(self.getl("def_finder_chk_settings_no_serbian_tt"))
        self.lbl_section_title.setText(self.getl("def_finder_lbl_section_title_text"))
        self.btn_section_select.setText(self.getl("def_finder_btn_section_select_text"))
        self.lbl_expression_title.setText(self.getl("def_finder_lbl_expression_title_text"))
        self.lbl_expression_expression.setText(self.getl("def_finder_lbl_expression_expression_text"))
        self.btn_expression_select.setText(self.getl("def_finder_btn_expression_select_text"))
        self.btn_syn_copy.setText(self.getl("def_finder_btn_syn_copy_text"))
        self.btn_syn_copy.setToolTip(self.getl("def_finder_btn_syn_copy_tt"))
        self.lbl_txt_alphabet_conversion.setToolTip(self.getl("def_finder_lbl_txt_alphabet_conversion_tt"))

    def _define_widgets_apperance(self):
        self.setFixedSize(1100, 730)
        self.setWindowTitle(self.getl("def_finder_lbl_title_text"))
        self.setWindowIcon(QIcon(QPixmap(self.getv("definition_data_find_icon_path"))))
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.frm_progress.setVisible(False)
        self.frm_settings.setVisible(False)
        self.frm_txt_ignore.setVisible(False)
        self.frm_section.setVisible(False)
        self.frm_expression.setVisible(False)

        # Search Frame
        self.frm_search_results: QFrame = QFrame(self)
        self.frm_search_results.setStyleSheet("background-color: rgb(74, 74, 111);")
        self.frm_search_results.move(self.frm_syn.pos().x(), self.frm_syn.pos().y())
        self.frm_search_results.resize(self.width() - 20, self.height() - self.frm_syn.pos().y() - 10)
        self.frm_search_results.setVisible(False)

        self.area_search = QScrollArea(self.frm_search_results)
        self.area_search.move(0, 0)
        self.area_search.resize(self.frm_search_results.width(), self.frm_search_results.height())

        self.area_images = QScrollArea(self.frm_img_pics)
        self.area_images.move(0, 0)
        self.area_images.resize(self.frm_img_pics.width(), self.frm_img_pics.height())
        self.area_images_widget = QWidget()
        self.area_images_widget_layout = QHBoxLayout()
        self.area_images.setWidget(self.area_images_widget)
        self.area_images_widget.setLayout(self.area_images_widget_layout)

        self.syn_frame = QFrame(self)
        self.syn_frame.setStyleSheet("background-color: rgb(53, 80, 138); color: rgb(255, 255, 0);")
        self.syn_area = QScrollArea(self.syn_frame)
        self.syn_area_widget = QWidget(self.syn_area)
        self.syn_area_widget_layout = QVBoxLayout(self.syn_area_widget)
        self.syn_area.setWidget(self.syn_area_widget)
        self.syn_area_widget.setLayout(self.syn_area_widget_layout)
        self.syn_frame.move(440, 190)
        self.syn_frame.resize(self.width() - 450, self.height() - 200)
        self.syn_area.move(0, 0)
        self.syn_area.resize(self.syn_frame.width(), self.syn_frame.height())
        self.syn_frame.setVisible(False)

    def cirilica_u_latinicu(self, text):
        latinica_text = to_latin(text)
        return latinica_text

    def latinica_u_cirilicu(self, text):
        latinica_text = to_cyrillic(text)
        return latinica_text

    def da_li_je_cirilica(self, tekst):
        cirilicni_karakteri = set("бгдђжилљњпћфцчџш")
        
        broj_cirilicnih_karaktera = sum(1 for karakter in tekst if karakter.lower() in cirilicni_karakteri)
        
        if broj_cirilicnih_karaktera >= self.MINIMUM_CHARS_TO_BE_CYRILLIC:
            return True
        else:
            return False







