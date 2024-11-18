from PyQt5.QtWidgets import (QFrame, QPushButton, QScrollArea, QVBoxLayout, QWidget, QListWidget, QDialog,
                             QLabel, QListWidgetItem)
from PyQt5.QtGui import QIcon, QPixmap, QResizeEvent, QMouseEvent
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QCoreApplication
from PyQt5 import uic, QtGui, QtCore

import os
import time

import settings_cls
import utility_cls
import online_topic_handler_cls
import UTILS
import qwidgets_util_cls


class OnlineContentItem(QFrame):
    # signal_item_click = pyqtSignal(int, str)
    signal_link_click = pyqtSignal(int, str)

    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, index: int, name: str, title: str, link: str, topic_image: QPixmap, widget_handler: qwidgets_util_cls.WidgetHandler) -> None:
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        uic.loadUi(self.getv("news_item_ui_file_path"), self)
        
        self._dont_clear_menu = False
        self._index = index
        self._name = name
        self._title = title
        self._link = link

        self._define_widgets()
        self._define_widgets_apperance()

        self.widget_handler = widget_handler
        action_button = self.widget_handler.add_ActionFrame(self, widget_properties_dict={"allow_bypass_mouse_press_event": True})
        action_button.activate()

        if topic_image is not None:
            self.lbl_pic.setPixmap(topic_image)
        self.lbl_pic.setScaledContents(True)

        self.lbl_link.mousePressEvent = self.lbl_link_mouse_press
    
    def lbl_link_mouse_press(self, e: QMouseEvent):
        if self.lbl_link.text():
            self.signal_link_click.emit(self._index, self._name)
        QLabel.mousePressEvent(self.lbl_link, e)

    def set_active(self, value: bool):
        if value:
            self.setStyleSheet("QFrame {background-color: qconicalgradient(cx:0.00568182, cy:0, angle:159.1, stop:0.204545 rgba(0, 7, 255, 97), stop:0.289773 rgba(255, 255, 0, 69), stop:0.329545 rgba(0, 158, 255, 145), stop:0.375 rgba(3, 0, 255, 130), stop:0.4375 rgba(71, 177, 255, 130), stop:0.482955 rgba(0, 147, 255, 208), stop:0.518717 rgba(71, 115, 255, 130), stop:0.55 rgba(79, 0, 255, 255), stop:0.693182 rgba(133, 0, 255, 69), stop:1 rgba(255, 255, 0, 69));}")
            self.setLineWidth(2)
        else:
            self.setStyleSheet("QFrame {background-color: #001a27;}\nQFrame::hover {background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 14, 25, 255), stop:0.994318 rgba(0, 0, 172, 255));}")
            self.setLineWidth(0)
    
    def _define_widgets(self):
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_name: QLabel = self.findChild(QLabel, "lbl_name")
        self.lbl_link: QLabel = self.findChild(QLabel, "lbl_link")

    def _define_widgets_apperance(self):
        self.setStyleSheet("QFrame {background-color: #001a27;}\nQFrame::hover {background-color: #285079;}")
        self.setLineWidth(0)
        self.setCursor(Qt.PointingHandCursor)

        if self._title is not None:
            self.lbl_name.setText(self._title)
        else:
            self.lbl_name.setText("")
        if self._link is not None:
            self.lbl_link.setText(self._link)
        else:
            self.lbl_link.setText("")


class OnlineContent(QDialog):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, *args, **kwargs):
        self._dont_clear_menu = False
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        super().__init__(parent_widget, *args, **kwargs)

        # Load GUI
        uic.loadUi(self.getv("news_ui_file_path"), self)

        # Define variables
        self.topic_handler = online_topic_handler_cls.OnLineTopicHandler(self, self._stt)
        self.topic_handler.topic_signal.connect(self.signal_topic_info)
        self.parent_widget = parent_widget
        self.active_topic = None
        self.active_topic_working = False
        self.topics_list = self.topic_handler.get_topics_list()

        self.temp_folder_snapshot = self._get_temp_folder_files()

        self._define_widgets()
        self._load_win_position()

        self.load_widgets_handler()

        self.show()
        QCoreApplication.processEvents()
        UTILS.LogHandler.add_log_record("#1: Dialog displayed.", ["OnlineContent"])

        # Connect events with slots
        self.btn_stop.clicked.connect(self.btn_stop_click)
        self.btn_refresh.clicked.connect(self.btn_refresh_click)
        self.lst_topics.currentItemChanged.connect(self.lst_topics_curent_item_changed)
        self.btn_topics_show.clicked.connect(self.btn_topics_show_click)
        self.area_content.verticalScrollBar().valueChanged.connect(self.scroll_bar_value_changed)
        self.area_content.horizontalScrollBar().valueChanged.connect(self.scroll_bar_value_changed)

        self.keyPressEvent = self.key_press

        self._populate_widgets()
        self._resize_me()

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.add_window_drag_widgets([self, self.lbl_title, self.lbl_title_pic])
        handle_dialog.properties.window_drag_enabled_with_body = False

        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_QPushButton(self.btn_stop)
        self.widget_handler.add_QPushButton(self.btn_refresh)
        self.widget_handler.add_QPushButton(self.btn_topics_show)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        # ADD Item Based Widgets


        self.widget_handler.activate()

    def key_press(self, event):
        result = self.topic_handler.current_topic.key_press_handler(event)
        if result:
            event.ignore()
            return
        QDialog.keyPressEvent(self, event)
        if event.key() == Qt.Key_Escape:
            self.close()

    def scroll_bar_value_changed(self, value: int):
        if self.topic_handler and self.topic_handler.current_topic:
            self.topic_handler.current_topic.area_changed(self.area_content)

    def btn_topics_show_click(self):
        if self.btn_topics_show.pos().x():
            self.frm_topics.resize(15, self.frm_topics.height())
            self.btn_topics_show.move(0, self.btn_topics_show.pos().y())
            self.lst_topics.setVisible(False)
        else:
            self.frm_topics.resize(371, self.frm_topics.height())
            self.btn_topics_show.move(350, self.btn_topics_show.pos().y())
            self.lst_topics.setVisible(True)
        self._resize_me()

    def lst_topics_curent_item_changed(self, x, y):
        if self.lst_topics.currentItem() is None:
            return
        if self.active_topic_working:
            self.lst_topics.setDisabled(True)
            return
        
        self.lst_topics.setDisabled(True)
        idx = self.lst_topics.currentRow()

        for i in range(self.lst_topics.count()):
            topic: OnlineContentItem = self.lst_topics.itemWidget(self.lst_topics.item(i))
            if topic._index == idx:
                topic_name = topic._name
                break

        self.show_topic(topic_name)

    def btn_refresh_click(self):
        self.show_topic()

    def btn_stop_click(self):
        if self.active_topic:
            self.topic_handler.current_topic.stop_loading_topic()

    def signal_topic_info(self, name: str, info: dict):
        if info["msg"]:
            txt = info["title"] + " - " + info["msg"]
            self.lbl_info.setText(txt)
            self.lbl_info.setToolTip(self.lbl_info.toolTip() + txt + "\n")
            QCoreApplication.processEvents()
        else:
            self.lbl_info.setText("")
        if info["working"]:
            self.lst_topics.setDisabled(True)
            self.active_topic_working = True
            self.btn_refresh.setVisible(False)
            self.btn_stop.setVisible(True)
        else:
            self.active_topic_working = False
            self.lst_topics.setDisabled(False)
            self.btn_refresh.setVisible(True)
            self.btn_stop.setVisible(False)

    def _populate_widgets(self):
        self.lst_topics.setDisabled(True)
        self.active_topic_working = True
        count = 0
        self.widgets = []
        for topic in self.topics_list:
            item = QListWidgetItem()
            item.setSizeHint(QSize(330, 150))
            self.lst_topics.addItem(item)
            widget = OnlineContentItem(
                self.lst_topics,
                self._stt, 
                count,
                topic,
                self.topics_list[topic]["title"],
                self.topics_list[topic]["link"],
                self.topics_list[topic]["icon_pixmap"],
                self.widget_handler)
            self.lst_topics.setItemWidget(item, widget)
            count += 1
        if self.active_topic is None:
            self.active_topic = "main"
            self.lst_topics.setCurrentRow(0)
        else:
            for i in range(self.lst_topics.count()):
                topic: OnlineContentItem = self.lst_topics.itemWidget(self.lst_topics.item(i))
                if self.active_topic == topic._name:
                    topic.set_active(True)
                    self.lst_topics.setCurrentRow(topic._index)
                else:
                    topic.set_active(False)

        self.active_topic_working = False
        self.show_topic()
        self.lst_topics.setDisabled(False)

    def get_topic_area_size(self) -> QSize:
        w = self.area_content.width() - self.area_content.contentsMargins().left() - self.area_content.contentsMargins().right() - self.area_content.verticalScrollBar().width() - 5
        h = self.area_content.height() - self.area_content.contentsMargins().top() - self.area_content.contentsMargins().bottom()
        return QSize(w, h)

    def show_topic(self, topic_name: str = None):
        if topic_name is None:
            topic_name = self.active_topic
        else:
            self.active_topic = topic_name
        if topic_name is None:
            self.lst_topics.setDisabled(False)
            return
        
        UTILS.LogHandler.add_log_record("#1: About to show topic (#2).", ["OnlineContent", topic_name])

        self.active_topic_working = True
        self.lst_topics.setDisabled(True)

        self._set_active_topic(topic_name)

        self.lbl_info.setToolTip("")
        self.lbl_info.setText("")
        self.frm_control.setVisible(True)
        self.btn_refresh.setVisible(False)
        self.btn_stop.setVisible(True)
        QCoreApplication.processEvents()
        self.topic_handler.current_topic.load_topic()
        self.active_topic_working = False
        self.lst_topics.setDisabled(False)
    
    def _set_active_topic(self, active_topic_name: str = None):
        if active_topic_name is None:
            active_topic_name = self.active_topic
        else:
            self.active_topic = active_topic_name
        if active_topic_name is None:
            return
        
        for i in range(self.lst_topics.count()):
            topic: OnlineContentItem = self.lst_topics.itemWidget(self.lst_topics.item(i))
            if active_topic_name == topic._name:
                topic.set_active(True)
            else:
                topic.set_active(False)
        
        self.topic_handler.set_current_topic(self.topics_list[active_topic_name]["name"])

        # Set topic in scrollbar
        self.area_widget = QWidget()
        self.area_layout = QVBoxLayout()
        self.area_widget.setLayout(self.area_layout)
        self.area_content.setWidget(self.area_widget)

        self.area_widget.layout().addWidget(self.topic_handler.current_topic)

    def _clear_temp_folder(self):
        if self.get_appv("cb")._clip["os"]:
            clipboard_files = [x[1] for x in self.get_appv("cb")._clip["os"]]
        else:
            clipboard_files = []
        tmp_folder = self.getv("temp_folder_path").strip("/") + "/"
        for file in os.listdir(tmp_folder):
            if file not in self.temp_folder_snapshot and os.path.abspath(tmp_folder + file) not in clipboard_files:
                os.remove(os.path.abspath(tmp_folder + file))

    def _get_temp_folder_files(self):
        tmp_folder = self.getv("temp_folder_path").strip("/") + "/"
        files = os.listdir(tmp_folder)
        return files

    def _load_win_position(self):
        if "online_content_win_geometry" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("online_content_win_geometry")
            if g.get("pos_x") is not None and g.get("pos_y") is not None:
                self.move(g["pos_x"], g["pos_y"])
            if g.get("width") is not None and g.get("height") is not None:
                self.resize(g["width"], g["height"])
            self.active_topic = g.get("last_topic", None)

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if not self._dont_clear_menu:
            self.get_appv("cm").remove_all_context_menu()
        self._dont_clear_menu = False
        return super().changeEvent(a0)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        UTILS.LogHandler.add_log_record("#1: About to close dialog.", ["OnlineContent"])
        result = self.close_me()
        if result:
            return super().closeEvent(a0)
        
        event_dict = {
            "name": "delayed_action",
            "dialog_name": "OnlineContent",
            "action": "try_to_close_me",
            "self": self,
            "issue": self.topic_handler.current_topic.title,
            "validate_function": self.close_me
        }
        
        self.get_appv("main_win").events(event_dict)
        UTILS.TerminalUtility.WarningMessage("#1: Unable to close dialog.\nMyJournal class will try to close it later.", "OnlineContent")
        return super().closeEvent(a0)

    def close_me(self) -> bool:
        if self.widget_handler:
            self.widget_handler.close_me()
            self.widget_handler = None

        if self.topic_handler and self.topic_handler.current_topic:
            self.topic_handler.current_topic.stop_loading_topic()
            self.topic_handler.current_topic.close_me()
            QCoreApplication.processEvents()

        if "online_content_win_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("online_content_win_geometry", {}, save_to_file=True)

        g = self.get_appv("online_content_win_geometry")
        if not self.isMinimized() and not self.isMaximized():
            g["pos_x"] = self.pos().x()
            g["pos_y"] = self.pos().y()
            g["width"] = self.width()
            g["height"] = self.height()
        g["last_topic"] = self.active_topic

        self._clear_temp_folder()
        self.hide()

        if self.active_topic_working:
            UTILS.LogHandler.add_log_record("#1: Unable to close dialog, active topic still running.", ["OnlineContent"])
            return False

        self.topic_handler = None        
        UTILS.LogHandler.add_log_record("#1: Dialog closed.", ["OnlineContent"])
        UTILS.DialogUtility.on_closeEvent(self)
        return True

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self._resize_me()
        return super().resizeEvent(a0)
        
    def _resize_me(self):
        w = self.contentsRect().width()
        h = self.contentsRect().height()

        self.frm_title.resize(w - 20, self.frm_title.height())
        self.lbl_title.resize(self.frm_title.width() - self.lbl_title.pos().x(), self.lbl_title.height())
        
        self.frm_topics.resize(self.frm_topics.width(), h - 10 - self.frm_topics.pos().y())
        self.lst_topics.resize(self.frm_topics.width() - self.btn_topics_show.width(), self.frm_topics.height())
        self.btn_topics_show.move(self.frm_topics.width() - self.btn_topics_show.width(), self.btn_topics_show.pos().y())
        self.btn_topics_show.resize(self.btn_topics_show.width(), self.frm_topics.height())

        if self.frm_title.width() > 170:
            self.frm_control.resize(self.frm_title.width(), self.frm_control.height())
            self.btn_refresh.move(self.frm_control.width() - self.btn_refresh.width(), 0)
            self.btn_stop.move(self.frm_control.width() - self.btn_refresh.width(), 0)
            self.lbl_info.resize(self.frm_control.width() - self.btn_refresh.width() - 10, self.lbl_info.height())

        self.area_content.move(10 + self.frm_topics.width(), self.frm_topics.pos().y())
        self.area_content.resize(w - 20 - self.frm_topics.width(), self.frm_topics.height())
        
        if self.topic_handler and self.topic_handler.current_topic:
            self.topic_handler.current_topic.area_changed(self.area_content)

    def _define_widgets(self):
        self.frm_title: QFrame = self.findChild(QFrame, "frm_title")
        self.lbl_title_pic: QLabel = self.findChild(QLabel, "lbl_title_pic")
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")
        self.frm_topics: QFrame = self.findChild(QFrame, "frm_topics")
        self.lst_topics: QListWidget = self.findChild(QListWidget, "lst_topics")
        self.btn_topics_show: QPushButton = self.findChild(QPushButton, "btn_topics_show")

        self.frm_control: QFrame = self.findChild(QFrame, "frm_control")
        self.lbl_info: QLabel = self.findChild(QLabel, "lbl_info")
        self.btn_stop: QPushButton = self.findChild(QPushButton, "btn_stop")
        self.btn_refresh: QPushButton = self.findChild(QPushButton, "btn_refresh")

        self.area_content: QScrollArea = self.findChild(QScrollArea, "area_content")
        self.area_widget = QWidget()
        self.area_layout = QVBoxLayout()
        self.area_widget.setLayout(self.area_layout)
        self.area_content.setWidget(self.area_widget)

        self._define_widgets_text()
        self._define_online_content_win_apperance()
        self._define_widgets_apperance()

    def _define_widgets_text(self):
        dt = utility_cls.DateTime(self._stt)
        date = dt.get_long_date(dt.get_today_date())
        self.lbl_title.setText(date)

        self.btn_refresh.setText(self.getl("online_content_btn_refresh_text"))
        self.btn_refresh.setToolTip(self.getl("online_content_btn_refresh_tt"))
        self.btn_stop.setText(self.getl("online_content_btn_stop_text"))
        self.btn_stop.setToolTip(self.getl("online_content_btn_stop_tt"))

    def _define_widgets_apperance(self):
        self.setWindowTitle(self.getl("online_content_win_title"))
        self._define_labels_apperance(self.lbl_title, "online_content_lbl_title")
        self._define_labels_apperance(self.lbl_title_pic, "online_content_lbl_title_pic")

        self.lst_topics.setStyleSheet(self.getv("online_content_lst_topics_stylesheet"))
        self.btn_topics_show.setStyleSheet(self.getv("online_content_btn_topics_show_stylesheet"))
        
        self.btn_refresh.setVisible(False)
        self.btn_stop.setVisible(False)

    def _define_online_content_win_apperance(self):
        self.setStyleSheet(self.getv("online_content_win_stylesheet"))
        self.setWindowIcon(QIcon(self.getv("online_content_win_icon_path")))
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))




