from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect, pyqtSignal, QObject

import settings_cls
from online_abstract_topic import AbstractTopic
import online_topic_main_cls
import online_topic_on_this_day_cls
import online_topic_news_cls
import online_topic_aladin_we_cls
import online_topic_aladin_tv_cls
import online_topic_dls_cls


class OnLineTopicHandler(QObject):
    topic_signal = pyqtSignal(str, dict)

    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, topic_geometry: QRect = None) -> None:
        super().__init__(parent_widget)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.topics = {
            "main": {"object": online_topic_main_cls.Main},
            "on_this_day": {"object": online_topic_on_this_day_cls.OnThisDay},
            "news": {"object": online_topic_news_cls.News},
            "aladin_we": {"object": online_topic_aladin_we_cls.AladinWE},
            "aladin_tv": {"object": online_topic_aladin_tv_cls.AladinTV},
            "gambling": {"object": online_topic_dls_cls.DLS}
            }
        self.parent_widget = parent_widget
        self.current_topic: AbstractTopic = None

        self._populate_topic_dictionary()
        
    def set_current_topic(self, topic_name: str):
        if self.current_topic is not None:
            self.current_topic.signal_topic_info.disconnect()
            self.current_topic.setVisible(False)
            # self.current_topic.setParent(self.parent_widget)
        self.current_topic: AbstractTopic = self.topics[topic_name]["object"](self.parent_widget, self._stt)
        self.current_topic.signal_topic_info.connect(self._topic_info_sender)
        self.current_topic.setVisible(True)

    def _topic_info_sender(self, topic_name: str, info: dict):
        self.topic_signal.emit(topic_name, info)
    
    def set_topic_geometry(self, topic_rect: QRect):
        if self.current_topic is None:
            return
        self.current_topic.move(topic_rect.x(), topic_rect.y())
        self.current_topic.resize(topic_rect.width(), topic_rect.height())

    def get_topics_list(self) -> list:
        return self.topics
    
    def _populate_topic_dictionary(self):
        for topic in self.topics:
            topic_obj: AbstractTopic = self.topics[topic]["object"](self.parent_widget, self._stt)
            topic_obj.setVisible(False)
            
            self.topics[topic]["name"] = topic
            self.topics[topic]["title"] = topic_obj.title
            self.topics[topic]["icon_path"] = topic_obj.icon_path
            self.topics[topic]["icon_pixmap"] = topic_obj.icon_pixmap
            self.topics[topic]["link"] = topic_obj.link





