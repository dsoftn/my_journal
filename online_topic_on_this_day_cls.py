from PyQt5.QtWidgets import QFrame, QPushButton, QWidget, QListWidget, QLabel, QListWidgetItem, QProgressBar
from PyQt5.QtGui import QFont, QPixmap, QCursor, QMouseEvent
from PyQt5.QtCore import Qt, QCoreApplication, QPoint
from PyQt5 import uic, QtGui

import webbrowser

import settings_cls
from online_abstract_topic import AbstractTopic
import html_parser_cls
from utility_cls import Calendar
from utility_cls import TextToHTML
from utility_cls import TextToHtmlRule
from utility_cls import DateTime
import UTILS


class EventItem(QFrame):
    FONT_SIZE = 18

    def __init__(self, settings: settings_cls.Settings, parent_widget: QWidget, html_code: str, position: QPoint, item_index: int) -> None:
        super().__init__(parent_widget)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.html_code = html_code
        self.position = position
        self.item_index = item_index
        self.has_image = None

        # Define widgets
        self.lbl_pic: QLabel = QLabel(self)
        self.lbl_pic.setFixedSize(250, 250)
        self.lbl_pic.setCursor(QCursor(Qt.PointingHandCursor))
        
        self.lbl_description: QLabel = QLabel(self)
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setTextInteractionFlags(self.lbl_description.textInteractionFlags() | Qt.TextSelectableByMouse)
        self.lbl_description.setFont(QFont("Arial", EventItem.FONT_SIZE))

        self.btn_pic = QPushButton(self)
        self.btn_pic.resize(250, 30)
        self.btn_pic.setStyleSheet("QPushButton {color: #0fb3ff;} QPushButton::hover {color: #c0edff}")
        font = self.btn_pic.font()
        font.setPointSize(12)
        font.setUnderline(True)
        self.btn_pic.setFont(font)
        self.btn_pic.setFlat(True)
        self.btn_pic.setCursor(QCursor(Qt.PointingHandCursor))

        # Connect events with slots
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.btn_pic.clicked.connect(self.btn_pic_click)
        
        self.create_me()

    def lbl_pic_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.parent_widget.lbl_pic.move(self.pos().x() + 260, self.pos().y() - 200)
            self.parent_widget.lbl_pic.resize(600, 600)
            self.parent_widget.set_image_to_label(self.lbl_pic.objectName(), self.parent_widget.lbl_pic)
            self.parent_widget.lbl_pic.raise_()
            self.parent_widget.lbl_pic.setVisible(True)
        elif e.button() == Qt.RightButton:
            self.parent_widget.show_additional_images(self)

    def btn_pic_click(self):
        self.parent_widget.show_additional_images(self)

    def resize_me(self):
        w = self.parent_widget.size().width() - 20

        if w < 470:
            w = 470

        self.move(self.position)
        
        if self.has_image:
            self.btn_pic.setText(self.getl("topic_on_this_day_item_btn_pic_has_image_text"))
            self.btn_pic.setToolTip(self.getl("topic_on_this_day_item_btn_pic_has_image_tt"))
            self.setFixedSize(w, 280)
            self.lbl_pic.move(0, 0)
            self.lbl_pic.resize(250, 250)
            self.lbl_pic.setVisible(True)
            self.lbl_description.move(260, 0)
            self.lbl_description.setFixedWidth(self.width() - 260)
            self.lbl_description.adjustSize()
            
            self.btn_pic.move(0, 250)
            if self.lbl_description.height() < 280:
                self.lbl_description.setFixedHeight(280)

            if self.lbl_description.height() > 280:
                self.setFixedHeight(self.lbl_description.height())
        else:
            self.btn_pic.setText(self.getl("topic_on_this_day_item_btn_pic_no_image_text"))
            self.btn_pic.setToolTip(self.getl("topic_on_this_day_item_btn_pic_no_image_tt"))
            self.setFixedWidth(w)
            self.lbl_pic.setVisible(False)
            self.lbl_description.move(20, 0)
            self.lbl_description.setFixedWidth(self.width() - 20)
            self.lbl_description.adjustSize()
            self.btn_pic.move(20, self.lbl_description.height())
            self.setFixedSize(w, self.btn_pic.pos().y() + self.btn_pic.height())

    def create_me(self, html_code: str = None):
        if html_code is None:
            html_code = self.html_code

        parser = html_parser_cls.HtmlParser()
        parser.load_html_code(html_code)

        text_slices = parser.get_all_text_slices()
        images = parser.get_all_images()

        if images:
            for image in images:
                if image.img_class == "Slika":
                    result = self.parent_widget.set_image_to_label(image, self.lbl_pic)
                    self.lbl_pic.setObjectName(image.img_src)
                    self.lbl_pic.setToolTip(image.img_title)
                    self.has_image = result
                    break
        
        if text_slices:
            tt: str = text_slices[0].txt_title + "\n"
            date: str = text_slices[0].txt_value
            if date:
                txt = "#1 "
            else:
                txt = ""
            
            for txt_slice in range(1, len(text_slices)):
                txt += text_slices[txt_slice].txt_value + " "
                tt += text_slices[txt_slice].txt_title + "\n"
            
            txt = txt.strip()
            tt = tt.strip()
        
            text_to_html_obj = TextToHTML(txt)
            
            if self.has_image:
                text_to_html_obj.general_rule.fg_color = "#aaff00"
                date_rule = TextToHtmlRule("#1", date, fg_color="#55ff00", font_bold=True)
                font = self.lbl_description.font()
                font.setPointSize(EventItem.FONT_SIZE + 2)
                self.lbl_description.setFont(font)
            else:
                text_to_html_obj.general_rule.fg_color = "#aaff7f"
                date_rule = TextToHtmlRule("#1", date, fg_color="#55ff00", font_bold=True)

            text_to_html_obj.add_rule(date_rule)
            desc = text_to_html_obj.get_html()

            self.lbl_description.setText(desc)
            self.lbl_description.setToolTip(tt)

        self.resize_me()


class OnThisDay(AbstractTopic):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings) -> None:
        super().__init__(parent_widget)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("online_topic_on_this_day_ui_file_path"), self)

        # Define variables
        self.name = "on_this_day"
        self.topic_info_dict["name"] = self.name
        self.parent_widget = parent_widget
        self.title = self.getl("online_topic_on_this_day_title")
        self.topic_info_dict["title"] = self.title
        self.link = None
        self.icon_path = self.getv("online_topic_on_this_day_icon_path")
        self.icon_pixmap = QPixmap(self.icon_path)

        self.event_list = []

        self._define_widgets()
        self._set_cursor_pointing_hand()

        # Connect events with slots
        self.lbl_nav_prev.mousePressEvent = self.prev_date
        self.lbl_nav_prev_pic.mousePressEvent = self.prev_date
        self.lbl_nav_next.mousePressEvent = self.next_date
        self.lbl_nav_next_pic.mousePressEvent = self.next_date
        self.btn_nav_date.clicked.connect(self.btn_nav_date_click)
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.lbl_close.mousePressEvent = self.lbl_close_mouse_press
        self.lbl_site_nadanasnjidan.mouseDoubleClickEvent = self.lbl_site_nadanasnjidan_double_click

        UTILS.LogHandler.add_log_record("#1: Topic frame loaded.", ["OnThisDay"])

    def lbl_site_nadanasnjidan_double_click(self, e: QMouseEvent):
        site = self.lbl_site_nadanasnjidan.toolTip()
        webbrowser.open_new_tab(site)
        QLabel.mouseDoubleClickEvent(self.lbl_site_nadanasnjidan, e)

    def _set_cursor_pointing_hand(self):
        cursor = QCursor(Qt.PointingHandCursor)
        self.lbl_close.setCursor(cursor)
        self.lbl_nav_prev.setCursor(cursor)
        self.lbl_nav_prev_pic.setCursor(cursor)
        self.lbl_nav_next.setCursor(cursor)
        self.lbl_nav_next_pic.setCursor(cursor)
        self.lbl_pic.setCursor(cursor)
        self.btn_nav_date.setCursor(cursor)

    def lbl_close_mouse_press(self, e: QtGui.QMouseEvent):
        if self.topic_info_dict["working"] == True:
            self.stop_loading = True
        self.lst_pic.setVisible(False)
        self.lbl_close.setVisible(False)

    def _set_position_lst_pic(self, item: EventItem, list_heigth: int = 300):
        item_rect = item.rect()
        x = item_rect.x()
        y = item.pos().y() + item_rect.height() + 10
        w = item_rect.width()
        h = list_heigth + self.lst_pic.horizontalScrollBar().height() + self.lst_pic.contentsMargins().top() + self.lst_pic.contentsMargins().bottom() + self.lst_pic.viewportMargins().top() + self.lst_pic.viewportMargins().bottom()
        h += self.lst_pic.getContentsMargins()[1]
        h += self.lst_pic.getContentsMargins()[3]

        h = max(self.lst_pic.height(), h)

        if y + h > self.height():
            y -= h
            if y < 0:
                y = 0
        self.lst_pic.move(x, y)
        self.lst_pic.resize(w, h)
        self.lbl_close.move(self.lst_pic.pos().x() + 3, self.lst_pic.pos().y() + 3)

    def show_additional_images(self, item: EventItem):
        if self.topic_info_dict["working"] == True:
            return
        
        self.lst_pic.resize(self.lst_pic.width(), 300)
        self._set_position_lst_pic(item=item)
        self.lst_pic.setVisible(True)
        self.lbl_close.setVisible(True)
        self.lbl_close.move(self.lst_pic.pos().x()+3, self.lst_pic.pos().y()+3)
        self.lst_pic.raise_()
        self.lbl_close.raise_()

        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_na_danasnji_dan") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.stop_loading = False

        self.lst_pic.clear()

        self.prg_event.setVisible(True)
        self.prg_event.setValue(0)
        QCoreApplication.processEvents()

        self.frm_nav.setEnabled(False)

        file = self.getv("rashomon_folder_path") + "image_search.rpf"
        images = self.get_images_from_search_engine(query_string=item.lbl_description.text(), project_file=file)
        
        font = QFont()
        font.setPointSize(10)
        for image_idx in images:
            image = images[image_idx]
            
            lst_item_widget = QFrame(self.lst_pic)
            lst_item_widget.setFrameShape(QFrame.NoFrame)
            lst_item_widget.setFrameShadow(QFrame.Plain)

            lbl_pic = QLabel(lst_item_widget)
            lbl_pic.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            lbl_pic.move(0, 0)
            lbl_pic.resize(300, 300)
            self.set_image_to_label(image["img_tag"], lbl_pic)

            lbl_desc = QLabel(lst_item_widget)
            lbl_desc.setWordWrap(True)
            lbl_desc.setFont(font)
            lbl_desc.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
            lbl_desc.move(0, 310)
            lbl_desc.setFixedWidth(300)
            lbl_desc.setText(image["desc"])
            lbl_desc.setToolTip(image["desc"])
            lbl_desc.adjustSize()
            lbl_desc.linkActivated.connect(lambda url: webbrowser.open_new_tab(url))

            lst_item_widget.resize(300, 310 + lbl_desc.height())

            lst_item = QListWidgetItem()
            lst_item.setSizeHint(lst_item_widget.size())
            self.lst_pic.addItem(lst_item)
            self.lst_pic.setItemWidget(lst_item, lst_item_widget)
            self._set_position_lst_pic(item, lst_item_widget.height())

            self.prg_event.setValue(int(int(image_idx) / len(images) * 100))
            QCoreApplication.processEvents()
            if self.stop_loading:
                break

        self.frm_nav.setEnabled(True)

        self.prg_event.setVisible(False)

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            return

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

    def lbl_pic_mouse_press(self, e: QtGui.QMouseEvent):
        self.lbl_pic.setVisible(False)

    def btn_nav_date_click(self):
        cal_dict = {
            "position": QCursor.pos(),
            "show_buttons": True
        }
        self.parent_widget._dont_clear_menu = True
        Calendar(self._stt, self, calendar_dict=cal_dict)
        if cal_dict["result"]:
            self.load_topic(selected_date=cal_dict["result"])

    def prev_date(self, e: QtGui.QMouseEvent):
        if self.lbl_nav_prev.objectName():
            self.load_topic(source_url=self.lbl_nav_prev.objectName())

    def next_date(self, e: QtGui.QMouseEvent):
        if self.lbl_nav_next.objectName():
            self.load_topic(source_url=self.lbl_nav_next.objectName())

    def load_topic(self, source_url: str = None, selected_date: str = None):
        """Load topic data"""
        UTILS.LogHandler.add_log_record("#1: About to load topic.", ["OnThisDay"])
        self.topic_info_dict["working"] = True
        self.stop_loading = False

        self.prg_event.setVisible(True)
        self.prg_event.setValue(0)
        QCoreApplication.processEvents()

        self.frm_nav.setEnabled(False)
        self.load_events(source_url=source_url, selected_date=selected_date)
        self.frm_nav.setEnabled(True)

        self.prg_event.setVisible(False)

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            UTILS.LogHandler.add_log_record("#1: Topic loading canceled.", ["OnThisDay"])
            return

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False
        UTILS.LogHandler.add_log_record("#1: Topic loading completed.", ["OnThisDay"])
        return super().load_topic()

    def load_events(self, source_url: str = None, selected_date: str = None):
        for i in self.event_list:
            i.hide()
            i.deleteLater()
        self.event_list = []

        self.topic_info_dict["msg"] = self.getl("topic_msg_na_danasnji_dan") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        datetime_obj = DateTime(self._stt)
        
        if selected_date:
            today = datetime_obj.make_date_dict(selected_date)
        else:
            today = datetime_obj.make_date_dict(datetime_obj.get_today_date())
        
        source = f'https://www.nadanasnjidan.net/nadan/{today["day"]}.{today["month"]}'

        if source_url:
            source = source_url

        file = self.getv("rashomon_folder_path") + "na_danasnji_dan.rpf"
        self.rashomon.errors(clear_errors=True)
        self.rashomon.load_project(file, change_source=source)
        self.rashomon.set_compatible_mode(True)

        if self.rashomon.errors():
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl("topic_msg_na_danasnji_dan") + ", Error: " + i
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        QCoreApplication.processEvents()
        if self.stop_loading:
            return
        
        self.rashomon.recreate_segment_tree()

        if self.rashomon.errors():
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl("topic_msg_na_danasnji_dan") + ", Error: " + i
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        QCoreApplication.processEvents()
        if self.stop_loading:
            return
        
        self.topic_info_dict["msg"] = self.getl("topic_msg_na_danasnji_dan") + ", " + self.getl("topic_msg_getting_data")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        # Populate Header
        title = self.rashomon.get_segment_selection("title_000", remove_tags=True)
        self.lbl_title.setText(title)

        nav_html = self.rashomon.get_segment_selection("nav_000")
        self.html_parser.load_html_code(nav_html)
        nav_text_list = [x for x in self.html_parser.get_all_text_slices() if x.txt_value != "-"]
        nav_link_list = self.html_parser.get_all_links()

        self.lbl_nav_prev.setText("")
        self.lbl_nav_prev.setToolTip("")
        self.lbl_nav_prev.setObjectName("")
        self.lbl_nav_next.setText("")
        self.lbl_nav_next.setToolTip("")
        self.lbl_nav_next.setObjectName("")
        
        if len(nav_text_list) > 2 and len(nav_link_list) > 2:
            self.lbl_nav_prev.setText(nav_text_list[0].txt_value)
            self.lbl_nav_prev.setToolTip(nav_text_list[0].txt_title)
            self.lbl_nav_prev.setObjectName(nav_link_list[0].a_href)
            self.lbl_nav_next.setText(nav_text_list[2].txt_value)
            self.lbl_nav_next.setToolTip(nav_text_list[2].txt_title)
            self.lbl_nav_next.setObjectName(nav_link_list[2].a_href)
        
        # Populate events
        events = self.rashomon.get_segment_children("items")

        if self.rashomon.errors() or events is None:
            if events is None:
                self.topic_info_dict["msg"] = "Error. No Events."
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl("topic_msg_na_danasnji_dan") + ", Error: " + i
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return
        
        count = 0
        self.setFixedSize(self.parent_widget.get_topic_area_size())

        self.lbl_title.resize(self.width() - 110, self.lbl_title.height())
        x = int((self.width() - self.frm_nav.width()) / 2)
        if x < 0:
            x = 0
        self.frm_nav.move(x, self.frm_nav.pos().y())

        for idx, event in enumerate(events):
            html_code = self.rashomon.get_segment_selection(event)
            html_code = self.rashomon.remove_specific_tag(html_code, tag="script", multiline=True)
            next_pos_y = self.get_new_y_position()
            position = QPoint(10, next_pos_y)
            item = EventItem(self._stt, self, html_code=html_code, position=position, item_index=idx)
            item.show()
            self.event_list.append(item)

            self.setFixedSize(self.width(), self.get_new_y_position())

            count += 1
            percent = int(count / len(events) * 100)
            self.prg_event.setValue(percent)
            QCoreApplication.processEvents()
            if self.stop_loading:
                return

    def get_new_y_position(self) -> int:
        h = 190
        for item in self.event_list:
            h += item.height() + 20
        return h

    def _define_widgets(self):
        self.lbl_site_nadanasnjidan: QLabel = self.findChild(QLabel, "lbl_site_nadanasnjidan")
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.frm_nav: QFrame = self.findChild(QFrame, "frm_nav")
        self.lbl_nav_prev_pic: QLabel = self.findChild(QLabel, "lbl_nav_prev_pic")
        self.lbl_nav_prev: QLabel = self.findChild(QLabel, "lbl_nav_prev")
        self.lbl_nav_next: QLabel = self.findChild(QLabel, "lbl_nav_next")
        self.lbl_nav_next_pic: QLabel = self.findChild(QLabel, "lbl_nav_next_pic")
        self.btn_nav_date: QPushButton = self.findChild(QPushButton, "btn_nav_date")
        self.prg_event: QProgressBar = self.findChild(QProgressBar, "prg_event")
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lst_pic: QListWidget = self.findChild(QListWidget, "lst_pic")
        self.lbl_close: QLabel = self.findChild(QLabel, "lbl_close")
        self._setup_widgets_text()
        self._setup_widgets()
    
    def _setup_widgets_text(self):
        self.lbl_site_nadanasnjidan.setToolTip("https://www.nadanasnjidan.net/")
        self.btn_nav_date.setText(self.getl("topic_na_danasnji_dan_btn_nav_date_text"))
        self.btn_nav_date.setToolTip(self.getl("topic_na_danasnji_dan_btn_nav_date_tt"))

    def _setup_widgets(self):
        self.setFixedSize(self.parent_widget.get_topic_area_size())
        self.prg_event.setVisible(False)
        self.btn_nav_date.setObjectName("")
        self.lbl_nav_prev.setObjectName("")
        self.lbl_nav_next.setObjectName("")
        self.lbl_pic.setVisible(False)
        self.lst_pic.setVisible(False)
        self.lbl_close.setVisible(False)











