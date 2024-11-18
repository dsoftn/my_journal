from PyQt5.QtWidgets import (QFrame, QPushButton, QWidget, QLabel, QLineEdit, QComboBox, QProgressBar,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QMouseEvent
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView

import webbrowser
import folium

import settings_cls
from online_abstract_topic import AbstractTopic
import UTILS


class Main(AbstractTopic):
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
        uic.loadUi(self.getv("online_topic_main_ui_file_path"), self)

        # Define variables
        self.name = "main"
        self.topic_info_dict["name"] = self.name
        self.parent_widget = parent_widget
        self.title = self.getl("online_topic_main_title")
        self.topic_info_dict["title"] = self.title
        self.link = None
        self.icon_path = self.getv("online_topic_main_icon_path")
        self.icon_pixmap = QPixmap(self.icon_path)

        self.settings: dict = self._get_user_settings()
        self.cashe: dict = self._get_cashe_struct()
        self.ignore_combobox_changes = False

        self._define_widgets()
        self.set_mouse_pointer_to_pointing_hand()

        # Connect events with slots
        self.cmb_exc_from.currentTextChanged.connect(self.cmb_exc_from_current_changed)
        self.cmb_exc_to.currentTextChanged.connect(self.cmb_exc_to_current_changed)
        self.cmb_exc_from.wheelEvent = self.cmb_wheel_event
        self.cmb_exc_to.wheelEvent = self.cmb_wheel_event
        self.txt_exc_amount1.returnPressed.connect(self.txt_exc_amount1_return_press)
        self.txt_exc_amount1.textChanged.connect(self.txt_exc_amount1_return_press)
        self.btn_exc_switch.clicked.connect(self.btn_exc_switch_click)
        self.lbl_site_oanda.mouseDoubleClickEvent = self.lbl_site_oanda_double_click
        self.lbl_site_xe.mouseDoubleClickEvent = self.lbl_site_xe_double_click
        self.lbl_site_mylocation.mouseDoubleClickEvent = self.lbl_site_mylocation_double_click
        self.lbl_site_timeanddate.mouseDoubleClickEvent = self.lbl_site_timeanddate_double_click
        self.btn_loc_map.clicked.connect(self.btn_loc_map_click)

        self.btn_we_city_go.clicked.connect(self.btn_we_city_go_click)
        self.txt_we_city.returnPressed.connect(self.txt_we_city_return_press)
        self.txt_we_city.textChanged.connect(self.txt_we_city_text_changed)

        UTILS.LogHandler.add_log_record("#1: Topic frame loaded.", ["OnlineTopic Main"])

    def cmb_wheel_event(self, e: QMouseEvent):
        return

    def set_mouse_pointer_to_pointing_hand(self):
        self.btn_loc_map.setCursor(Qt.PointingHandCursor)
        self.btn_we_city_go.setCursor(Qt.PointingHandCursor)
        self.cmb_exc_from.setCursor(Qt.PointingHandCursor)
        self.cmb_exc_to.setCursor(Qt.PointingHandCursor)

    def btn_we_city_go_click(self):
        if self.txt_we_city.text().strip() or self.txt_we_city.objectName():
            self._update_user_settings()
            self.update_weather()

    def txt_we_city_text_changed(self):
        self.txt_we_city.setObjectName("")

    def txt_we_city_return_press(self):
        if self.txt_we_city.text().strip() or self.txt_we_city.objectName():
            self._update_user_settings()
            self.update_weather()

    def btn_loc_map_click(self):
        if not self.lbl_loc_lat_val.text() or not self.lbl_loc_lon_val.text():
            return
        
        latitude = self.lbl_loc_lat_val.text()
        longitude = self.lbl_loc_lon_val.text()
        if self._get_float(latitude) is None or self._get_float(longitude) is None:
            return

        if self.web_engine.isVisible():
            self.web_engine.setVisible(False)
            self.btn_loc_map.setText(self.getl("topic_main_btn_loc_map_show"))
            return
        
        self.btn_loc_map.setText(self.getl("topic_main_btn_loc_map_hide"))
        
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        folium.Marker([latitude, longitude], popup="Vasa lokacija").add_to(m)
        tmp_folder = self.getv("temp_folder_path")
        map_file = tmp_folder + "location.html"
        m.save(map_file)
        with open(map_file, "r", encoding="utf-8") as file:
            map_html = file.read()
        
        self.web_engine.setHtml(map_html)

        self.web_engine.move(10, 220)
        self.web_engine.resize(self.width() - 20, self.height() - 230)
        self.web_engine.raise_()
        self.web_engine.setVisible(True)

    def lbl_site_mylocation_double_click(self, e: QMouseEvent):
        site = self.lbl_site_mylocation.toolTip()
        webbrowser.open_new_tab(site)
        QLabel.mouseDoubleClickEvent(self.lbl_site_mylocation, e)
    
    def lbl_site_timeanddate_double_click(self, e: QMouseEvent):
        site = self.lbl_site_timeanddate.toolTip()
        webbrowser.open_new_tab(site)
        QLabel.mouseDoubleClickEvent(self.lbl_site_timeanddate, e)

    def lbl_site_oanda_double_click(self, e: QMouseEvent):
        site = self.lbl_site_oanda.toolTip()
        webbrowser.open_new_tab(site)
        QLabel.mouseDoubleClickEvent(self.lbl_site_oanda, e)

    def lbl_site_xe_double_click(self, e: QMouseEvent):
        site = self.lbl_site_xe.toolTip()
        webbrowser.open_new_tab(site)
        QLabel.mouseDoubleClickEvent(self.lbl_site_xe, e)

    def btn_exc_switch_click(self):
        self.ignore_combobox_changes = True
        tmp = self.cmb_exc_from.currentText()
        self.cmb_exc_from.setCurrentText(self.cmb_exc_to.currentText())
        self.cmb_exc_to.setCurrentText(tmp)
        self.txt_exc_amount2.setText("")
        self.ignore_combobox_changes = False
        self.update_exchange_rate()
        self._update_user_settings()
        self.stop_loading = False
    
    def txt_exc_amount1_return_press(self):
        pos = self.txt_exc_amount1.cursorPosition()
        self.update_exchange_rate()
        self.txt_exc_amount1.setFocus()
        self.txt_exc_amount1.setCursorPosition(pos)
        self.stop_loading = False

    def cmb_exc_from_current_changed(self):
        self.update_exchange_rate()
        self._update_user_settings()
        self.stop_loading = False

    def cmb_exc_to_current_changed(self):
        self.update_exchange_rate()
        self._update_user_settings()
        self.stop_loading = False

    def load_topic(self):
        UTILS.LogHandler.add_log_record("#1: About to load topic.", ["OnlineTopic Main"])
        self.topic_info_dict["working"] = True
        self.stop_loading = False
        self._load_location()
        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            UTILS.LogHandler.add_log_record("#1: User stopped loading.", ["OnlineTopic Main"])
            return

        self._load_exchange_rate()
        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            UTILS.LogHandler.add_log_record("#1: User stopped loading.", ["OnlineTopic Main"])
            return

        self.load_weather()
        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            UTILS.LogHandler.add_log_record("#1: User stopped loading.", ["OnlineTopic Main"])
            return

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False
        UTILS.LogHandler.add_log_record("#1: Topic loading completed.", ["OnlineTopic Main"])
        return super().load_topic()

    def load_weather(self):
        self.txt_we_city.setText(self.settings["weather"]["city"])
        self.txt_we_city.setObjectName(self.settings["weather"]["city_url"])

        self.txt_we_city.setDisabled(True)
        self.btn_we_city_go.setDisabled(True)
        self._load_weather()
        self.txt_we_city.setDisabled(False)
        self.btn_we_city_go.setDisabled(False)
    
    def update_weather(self):
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.txt_we_city.setDisabled(True)
        self.btn_we_city_go.setDisabled(True)
        self._load_weather()
        self.txt_we_city.setDisabled(False)
        self.btn_we_city_go.setDisabled(False)

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.settings["weather"]["city"] = self.txt_we_city.text()

    def _load_weather(self):
        search_string = self._we_search_string()
        if not search_string and not self.txt_we_city.objectName():
            return
        
        working_val = self.topic_info_dict["working"]
        self.topic_info_dict["working"] = True

        self.topic_info_dict["msg"] = self.getl("topic_msg_weather") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        QCoreApplication.processEvents()

        self.frm_we_result.setVisible(False)
        self.lbl_we_map.setVisible(False)
        self.lbl_we_map_loc.setVisible(False)
        self.lbl_we_no_data.setVisible(False)
        self.lbl_we_search_title.setVisible(False)
        self.lbl_5h_title.setVisible(False)
        self.lbl_48h_title.setVisible(False)
        self.lbl_14d_title.setVisible(False)
        self.frm_near.setVisible(False)

        self._we_hide_all_tables()

        if self.txt_we_city.objectName():
            source = self.txt_we_city.objectName()
        else:
            source = f"https://www.timeanddate.com/weather/?query={search_string}"
        
        self.rashomon.errors(clear_errors=True)
        self.rashomon.load_project(self.getv("rashomon_folder_path") + "weather.rpf", change_source=source)

        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        self.rashomon.set_compatible_mode(True)

        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        result = self.rashomon.recreate_segment_tree()

        if not result or self.rashomon.errors():
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl("topic_msg_weather") + ", " + i
                self.signal_topic_info_emit(self.name, self.topic_info_dict)
            QCoreApplication.processEvents()
            return

        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        # loaded_url = self.rashomon.get_segment_selection("page_url_000")
        loaded_url = self.rashomon.get_source()

        if not loaded_url:
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl("topic_msg_weather") + ", " + i
                self.signal_topic_info_emit(self.name, self.topic_info_dict)
            QCoreApplication.processEvents()
            return

        if not self.rashomon.get_segment_selection("main_look_000"):
            result = self._we_show_search_results()
        elif loaded_url.find("@") == -1:
            self._we_show_country_weather()
        else:
            self._we_show_country_weather()




        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

    def _we_show_country_weather(self) -> bool:
        if self.rashomon.get_segment_children("no_data"):
            self.lbl_we_no_data.setVisible(True)
            return True
        
        self._we_hide_all_tables()
        self.frm_we_result.setVisible(True)

        self._we_city_main_panel()
        if self.stop_loading:
            return
        self._we_city_info()
        if self.stop_loading:
            return
        self._we_city_map()
        if self.stop_loading:
            return
        self._we_city_5h()
        if self.stop_loading:
            return
        self._we_city_48h()
        if self.stop_loading:
            return
        self._we_city_14d()
        if self.stop_loading:
            return
        self._we_near()
    
    def _get_last_pos(self) -> int:
        pos = []
        pos.append(self.frm_we_result.pos().y() + self.frm_we_result.height())
        if self.lbl_we_map.isVisible():
            pos.append(self.lbl_we_map.pos().y() + self.lbl_we_map.height())
        if self.tbl_info.isVisible():
            pos.append(self.tbl_info.pos().y() + self.tbl_info.height())
        if self.tbl_5h.isVisible():
            pos.append(self.tbl_5h.pos().y() + self.tbl_5h.height())
        if self.tbl_48h.isVisible():
            pos.append(self.tbl_48h.pos().y() + self.tbl_48h.height())
        if self.tbl_14d.isVisible():
            pos.append(self.tbl_14d.pos().y() + self.tbl_14d.height())

        return max(pos)        

    def _is_start_with_integer(self, txt: str) -> bool:
        txt = txt.strip()
        pos = txt.find(" ")
        if pos > 0:
            txt = txt[:pos]
        try:
            _ = int(txt)
            result = True
        except:
            result = False
        return result
    
    def _we_city_main_panel(self):
        # Populate contry widgets
        self.rashomon.errors(clear_errors=True)
        result = self.rashomon.get_segment_selection("title_000")
        if not self.rashomon.errors():
            self.lbl_we_title.setText(self.rashomon.remove_tags(result, join_in_one_line=True, delimiter=" "))
            self.html_parser.load_html_code(result)
            images = self.html_parser.get_all_images()
            if images:
                self.set_image_to_label(images[0], self.lbl_we_result_flag)
        if self.stop_loading:
            return False
        
        self.rashomon.errors(clear_errors=True)
        result = self.rashomon.get_segment_selection("main_look_000", remove_tags=True)
        if not self.rashomon.errors():
            city = ""
            temp = ""
            result_list = result.split("\n")
            if len(result_list) > 2:
                start = 3
                if self._is_start_with_integer(result_list[1]):
                    city = result_list[0]
                    temp = temp = result_list[1]
                    start = 2
                elif self._is_start_with_integer(result_list[2]):
                    city = result_list[0] + "\n" + result_list[1]
                    temp = result_list[2]
                else:
                    city = result_list[0] + ", " + result_list[1] + "\n" + result_list[2]
                    if len(result_list) > 3:
                        temp = result_list[3]
                    start = 4

                other_info = ""
                for i in range(start, len(result_list)):
                    other_info += result_list[i] + "\n"
                other_info = other_info.strip()
            else:
                other_info = ""
                for i in range(len(result_list)):
                    other_info += result_list[i] + "\n"
                other_info = other_info.strip()
            self.lbl_we_result_city.setText(city)
            self.lbl_we_result_temp.setText(temp)
            self.lbl_we_result_desc.setText(other_info)

            result = self.rashomon.get_segment_selection("main_look_000")
            self.html_parser.load_html_code(result)
            images = self.html_parser.get_all_images()
            if images:
                self.set_image_to_label(images[0], self.lbl_we_result_pic)
        return True
        
    def _we_city_info(self):
        # Show Info table
        self.rashomon.errors(clear_errors=True)
        table_code = self.rashomon.get_segment_selection("main_info_000_000", remove_double_lf=False)
        if self.rashomon.errors():
            return False
        
        self.html_parser.load_html_code(table_code)
        tables = self.html_parser.get_all_tables()
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False

        if not tables:
            self.topic_info_dict["msg"] = self.getl("topic_msg_weather") + ", " + self.getl("topic_msg_data_error")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            QCoreApplication.processEvents()
            return False

        self.tbl_info = self.html_parser.get_PYQT5_table_widget(tables[0], parent_widget=self)
        self.tbl_info.setVisible(True)
        
        self.tbl_info.move(10, self.frm_we_result.pos().y() + self.frm_we_result.height() + 10)
        bg_color = self.palette().color(self.backgroundRole())
        header_stylesheet = "QHeaderView::section {background-color:#1; color: #aaffff}"
        header_stylesheet = header_stylesheet.replace("#1", bg_color.name())
        self.tbl_info.verticalHeader().setStyleSheet(header_stylesheet)

        self.tbl_info.horizontalHeader().setStyleSheet(header_stylesheet)

        self.tbl_info.setStyleSheet("color: #aaff7f")
        self.tbl_info.show()
        return True
        
    def _we_city_map(self):
        # Show map
        self.rashomon.errors(clear_errors=True)
        table_code = self.rashomon.get_segment_selection("main_map_000_000", remove_double_lf=False)
        if self.rashomon.errors():
            return False

        if not table_code:
            return False
        
        self.html_parser.load_html_code(table_code)
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False
        
        images = self.html_parser.get_all_images()

        if not images:
            return False
        
        scale = 1.8

        images[0].img_width = images[0].img_width if images[0].img_width is not None else 320
        images[0].img_height = images[0].img_height if images[0].img_height is not None else 160

        self.lbl_we_map.resize(int(images[0].img_width * scale), int(images[0].img_height * scale))
        self.set_image_to_label(images[0], self.lbl_we_map, strech_to_label=True)
        self.lbl_we_map.setVisible(True)

        if len(images) > 1:
            images[1].img_x = images[1].img_x if images[1].img_x is not None else 0
            images[1].img_y = images[1].img_y if images[1].img_y is not None else 0
            images[1].img_width = images[1].img_width if images[1].img_width is not None else 10
            images[1].img_height = images[1].img_height if images[1].img_height is not None else 10

            self.set_image_to_label(images[1], self.lbl_we_map_loc)
            loc_x = self.lbl_we_map.pos().x() + (images[1].img_x * scale + (images[1].img_width * scale - images[1].img_width) / 2)
            loc_y = self.lbl_we_map.pos().y() + images[1].img_y * scale + (images[1].img_height * scale - images[1].img_height)
            self.lbl_we_map_loc.move(int(loc_x), int(loc_y))
            self.lbl_we_map_loc.setVisible(True)

        return True

    def _we_city_5h(self):
        self.rashomon.errors(clear_errors=True)
        table_code = self.rashomon.get_segment_selection("5h_000", remove_double_lf=False)
        if self.rashomon.errors():
            return False

        if not table_code:
            return False
        
        self.html_parser.load_html_code(table_code)
        tables = self.html_parser.get_all_tables()
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False
        if not tables:
            return False

        pos_y = self._get_last_pos() + 5

        title = self.rashomon.get_segment_selection("5h_title_000", remove_tags=True, join_in_one_line=True)
        if not self.rashomon.errors():
            self.lbl_5h_title.setText(title)
            self.lbl_5h_title.move(10, pos_y)
            pos_y += 30
            self.lbl_5h_title.setVisible(True)

        self.prg_we.setVisible(True)

        self.tbl_5h = self.html_parser.get_PYQT5_table_widget(tables[0], parent_widget=self, feedback_function=self.feedback_function)
        self.tbl_5h.setVisible(True)
        
        self.tbl_5h.move(10, pos_y)
        
        bg_color = self.palette().color(self.backgroundRole())
        header_stylesheet = "QHeaderView::section {background-color:#1; color: #aaffff}"
        header_stylesheet = header_stylesheet.replace("#1", bg_color.name())

        self.tbl_5h.verticalHeader().setStyleSheet(header_stylesheet)
        self.tbl_5h.horizontalHeader().setStyleSheet(header_stylesheet)

        self.tbl_5h.setStyleSheet("color: #aaff7f")
        self.tbl_5h.show()
        self.prg_we.setVisible(False)
        return True

    def _we_city_48h(self):
        self.rashomon.errors(clear_errors=True)
        table_code = self.rashomon.get_segment_selection("48h_000", remove_double_lf=False)
        if self.rashomon.errors():
            return False

        if not table_code:
            return False
        
        self.html_parser.load_html_code(table_code)
        tables = self.html_parser.get_all_tables()
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False
        if not tables:
            return False

        pos_y = self._get_last_pos() + 40

        title = self.rashomon.get_segment_selection("48h_14d_title_000", remove_tags=True)
        if not self.rashomon.errors() and title:
            self.lbl_48h_title.setText(title)
            self.lbl_48h_title.move(10, pos_y)
            pos_y += 30
            self.lbl_48h_title.setVisible(True)

        self.prg_we.setVisible(True)

        self.tbl_48h = self.html_parser.get_PYQT5_table_widget(tables[0], parent_widget=self, feedback_function=self.feedback_function)
        self.tbl_48h.setVisible(True)
        
        self.tbl_48h.setVerticalHeaderItem(self.tbl_48h.rowCount() - 1, QTableWidgetItem(""))
        txt = self.rashomon.get_segment_selection("48h_000", remove_tags=True)
        self.tbl_48h.item(self.tbl_48h.rowCount() - 1, 0).setText(txt.split("\n")[-1])
        self.tbl_48h.item(self.tbl_48h.rowCount() - 1, 0).setForeground(QColor("#c5bdff"))
        self.tbl_48h.setSpan(self.tbl_48h.rowCount() - 1, 0, 1, self.tbl_48h.columnCount())

        self.tbl_48h.move(10, pos_y)
        
        bg_color = self.palette().color(self.backgroundRole())
        header_stylesheet = "QHeaderView::section {background-color:#1; color: #aaffff}"
        header_stylesheet = header_stylesheet.replace("#1", bg_color.name())

        self.tbl_48h.verticalHeader().setStyleSheet(header_stylesheet)
        self.tbl_48h.horizontalHeader().setStyleSheet(header_stylesheet)

        self.tbl_48h.setStyleSheet("color: #aaff7f")
        self.tbl_48h.show()
        self.prg_we.setVisible(False)
        return True

    def _we_city_14d(self):
        self.rashomon.errors(clear_errors=True)
        table_code = self.rashomon.get_segment_selection("14d_000", remove_double_lf=False)
        if self.rashomon.errors():
            return False

        if not table_code:
            return False
        
        self.html_parser.load_html_code(table_code)
        tables = self.html_parser.get_all_tables()
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False
        if not tables:
            return False

        pos_y = self._get_last_pos() + 10

        title = self.rashomon.get_segment_selection("48h_14d_title_001", remove_tags=True)
        if not self.rashomon.errors() and title:
            self.lbl_14d_title.setText(title)
            self.lbl_14d_title.move(10, pos_y)
            pos_y += 30
            self.lbl_14d_title.setVisible(True)

        self.prg_we.setVisible(True)

        self.tbl_14d = self.html_parser.get_PYQT5_table_widget(tables[0], 
                                                               parent_widget=self,
                                                               feedback_function=self.feedback_function,
                                                               split_text_slices_into_lines=True)
        self.tbl_14d.setVisible(True)
        
        self.tbl_14d.move(10, pos_y)
        
        bg_color = self.palette().color(self.backgroundRole())
        header_stylesheet = "QHeaderView::section {background-color:#1; color: #aaffff}"
        header_stylesheet = header_stylesheet.replace("#1", bg_color.name())

        self.tbl_14d.verticalHeader().setStyleSheet(header_stylesheet)
        self.tbl_14d.horizontalHeader().setStyleSheet(header_stylesheet)

        self.tbl_14d.setStyleSheet("color: #aaff7f")
        self.tbl_14d.show()
        self.prg_we.setVisible(False)
        self.setFixedSize(max(self.tbl_14d.pos().x() + self.tbl_14d.width() + 10, self.width()), self.tbl_14d.pos().y() + self.tbl_14d.height() + 10)
        return True

    def _we_near(self):
        self.rashomon.errors(clear_errors=True)
        near_code = self.rashomon.get_segment_selection("near_001", remove_double_lf=False)
        if self.rashomon.errors():
            return False

        if not near_code:
            return False
        
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False
        
        near_city = self.html_parser.get_tags(html_code=near_code, tag="div", tag_class_contains="clear", multiline=True)
        if len(near_city) < 3:
            return False
        
        # Title
        title = self.html_parser.get_tags(html_code=near_code, tag="h3", tag_class_contains="mgt0 tc", multiline=True)
        if title:
            self.html_parser.load_html_code(title[0])
            title = self.html_parser.get_raw_text()
        else:
            title = ""
        self.lbl_near_title.setText(title)

        # City 1
        city_code = near_city[0]

        text1 = self.html_parser.get_tags(html_code=city_code, tag="h3", tag_class_contains="mgb0", multiline=True)
        if text1:
            self.html_parser.load_html_code(text1[0])
            text1 = self.html_parser.get_raw_text()
        else:
            text1 = ""

        text2 = self.html_parser.get_tags(html_code=city_code, tag="p", multiline=True)
        if text2:
            self.html_parser.load_html_code(text2[0])
            text2 = self.html_parser.get_raw_text()
        else:
            text2 = ""

        desc = text1 + "\n" + text2

        temp = self.html_parser.get_tags(html_code=city_code, tag="span", tag_class_contains="block", multiline=True)
        if temp:
            self.html_parser.load_html_code(temp[0])
            temp = self.html_parser.get_raw_text()
        else:
            temp = ""

        self.html_parser.load_html_code(city_code)
        img_obj = self.html_parser.get_all_images()
        if img_obj:
            self.set_image_to_label(img_obj[0].img_src, self.lbl_near_pic1)
            self.lbl_near_pic1.setVisible(True)
        else:
            self.lbl_near_pic1.setVisible(False)

        self.lbl_near_desc1.setText(desc)
        self.lbl_near_temp1.setText(temp)

        # City 2
        city_code = near_city[1]

        text1 = self.html_parser.get_tags(html_code=city_code, tag="h3", tag_class_contains="mgb0", multiline=True)
        if text1:
            self.html_parser.load_html_code(text1[0])
            text1 = self.html_parser.get_raw_text()
        else:
            text1 = ""

        text2 = self.html_parser.get_tags(html_code=city_code, tag="p", multiline=True)
        if text2:
            self.html_parser.load_html_code(text2[0])
            text2 = self.html_parser.get_raw_text()
        else:
            text2 = ""

        desc = text1 + "\n" + text2

        temp = self.html_parser.get_tags(html_code=city_code, tag="span", tag_class_contains="block", multiline=True)
        if temp:
            self.html_parser.load_html_code(temp[0])
            temp = self.html_parser.get_raw_text()
        else:
            temp = ""

        self.html_parser.load_html_code(city_code)
        img_obj = self.html_parser.get_all_images()
        if img_obj:
            self.set_image_to_label(img_obj[0].img_src, self.lbl_near_pic2)
            self.lbl_near_pic2.setVisible(True)
        else:
            self.lbl_near_pic2.setVisible(False)

        self.lbl_near_desc2.setText(desc)
        self.lbl_near_temp2.setText(temp)

        # City 3
        city_code = near_city[2]

        text1 = self.html_parser.get_tags(html_code=city_code, tag="h3", tag_class_contains="mgb0", multiline=True)
        if text1:
            self.html_parser.load_html_code(text1[0])
            text1 = self.html_parser.get_raw_text()
        else:
            text1 = ""

        text2 = self.html_parser.get_tags(html_code=city_code, tag="p", multiline=True)
        if text2:
            self.html_parser.load_html_code(text2[0])
            text2 = self.html_parser.get_raw_text()
        else:
            text2 = ""

        desc = text1 + "\n" + text2

        temp = self.html_parser.get_tags(html_code=city_code, tag="span", tag_class_contains="block", multiline=True)
        if temp:
            self.html_parser.load_html_code(temp[0])
            temp = self.html_parser.get_raw_text()
        else:
            temp = ""

        self.html_parser.load_html_code(city_code)
        img_obj = self.html_parser.get_all_images()
        if img_obj:
            self.set_image_to_label(img_obj[0].img_src, self.lbl_near_pic3)
            self.lbl_near_pic3.setVisible(True)
        else:
            self.lbl_near_pic3.setVisible(False)

        self.lbl_near_desc3.setText(desc)
        self.lbl_near_temp3.setText(temp)

        # Set frame
        self.frm_near.move(self.tbl_5h.width() + 20, self.lbl_we_map.pos().y() + self.lbl_we_map.height() + 10)
        self.frm_near.setVisible(True)

        return True
    
    def _we_show_search_results(self) -> bool:
        if self.rashomon.get_segment_children("no_data"):
            self.lbl_we_no_data.setVisible(True)
            return True
        
        self._we_hide_all_tables()

        self.rashomon.errors(clear_errors=True)
        table_code = self.rashomon.get_segment_selection("search_000", remove_double_lf=False)
        if self.rashomon.errors():
            self.lbl_we_no_data.setVisible(True)
            return False

        self.html_parser.load_html_code(table_code)
        tables = self.html_parser.get_all_tables()
        QCoreApplication.processEvents()

        if self.stop_loading:
            return False

        if not tables:
            self.topic_info_dict["msg"] = self.getl("topic_msg_weather") + ", " + self.getl("topic_msg_data_error")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            QCoreApplication.processEvents()
            return False

        self.lbl_we_search_title.setVisible(True)
        self.lbl_we_search_title.setStyleSheet("color: rgb(85, 255, 255);")
        self.lbl_we_search_title.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.lbl_we_search_title.setText("Searching...\nPlease wait")
        QCoreApplication.processEvents()
        
        self.prg_we.setVisible(True)
        self.tbl_search = self.html_parser.get_PYQT5_table_widget(tables[0], parent_widget=self, table_height=400, feedback_function=self.feedback_function)
        self.prg_we.setVisible(False)
        self.tbl_search.setStyleSheet("background-color: #303000; color: #aaff7f")
        self.tbl_search.setVisible(True)
        self.tbl_search.itemClicked.connect(self.tbl_search_item_clicked)
        self.tbl_search.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.lbl_we_search_title.setVisible(True)
        self.lbl_we_search_title.setStyleSheet("color: #aaff00;")
        self.lbl_we_search_title.setAlignment(Qt.AlignLeft|Qt.AlignBottom)
        self.lbl_we_search_title.setText(f"Search results for\n{self.txt_we_city.text()}")

        self.tbl_search.move(10, 560)
        self.tbl_search.show()
        return True

    def _we_hide_all_tables(self):
        self.tbl_info.setVisible(False)
        self.tbl_5h.setVisible(False)
        self.tbl_48h.setVisible(False)
        self.tbl_14d.setVisible(False)
        self.tbl_search.setVisible(False)

    def feedback_function(self, progress: tuple) -> bool:
        if self.stop_loading:
            return False
        
        percent = 0
        if progress[1] != 0:
            percent = int((progress[0] / progress[1]) * 100)
        
        if percent % 4 == 0 and percent != self.prg_we.value():
            self.prg_we.setValue(percent)
            QCoreApplication.processEvents()
        return True

    def tbl_search_item_clicked(self):
        row = self.tbl_search.currentRow()
        col = 0
        city = self.tbl_search.item(row, col).text()
        city_url: str = self.tbl_search.item(row, col).data(Qt.UserRole)

        if city_url:
            if city_url.startswith("//"):
                city_url = "https:" + city_url
            elif city_url.startswith("/"):
                city_url = "https://www.timeanddate.com" + city_url

            self.txt_we_city.setText(city)
            self.txt_we_city.setObjectName(city_url)

    def _we_search_string(self) -> str:
        txt = self.txt_we_city.text()
        for i in "~!@#$%^&*()_+=-[}{];:'\"|\\/?.,><`":
            txt = txt.replace(i, " ")
        while True:
            txt = txt.replace("  ", " ")
            if txt.find("  ") == -1:
                break
        
        txt = txt.strip().replace(" ", "+")
        return txt

    def _load_exchange_rate(self):
        self.topic_info_dict["msg"] = self.getl("topic_msg_exchange_rate") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        # Populate ComboBoxes
        currencies = self._currency_list()
        self.ignore_combobox_changes = True
        for i in currencies:
            txt = "  " + currencies[i]["name"] + "  " + currencies[i]["desc"]
            icon = icon=QIcon(QPixmap(currencies[i]["image"]))
            self.cmb_exc_from.addItem(txt, i)
            self.cmb_exc_from.setItemIcon(self.cmb_exc_from.count() - 1, icon)
            self.cmb_exc_to.addItem(txt, i)
            self.cmb_exc_to.setItemIcon(self.cmb_exc_to.count() - 1, icon)
        
        # Set ComboBoxes selection
        for i in range(self.cmb_exc_from.count()):
            if self.cmb_exc_from.itemData(i) == self.settings["exchange"]["from"]:
                self.cmb_exc_from.setCurrentIndex(i)
            if self.cmb_exc_to.itemData(i) == self.settings["exchange"]["to"]:
                self.cmb_exc_to.setCurrentIndex(i)
        
        QCoreApplication.processEvents()
        self.ignore_combobox_changes = False
        if self.stop_loading:
            return
        self.update_exchange_rate()
        if self.stop_loading:
            return

    def update_exchange_rate(self):
        value = True
        self.cmb_exc_from.setDisabled(value)
        self.cmb_exc_to.setDisabled(value)
        self.txt_exc_amount1.setDisabled(value)
        self.txt_exc_amount2.setDisabled(value)
        self._update_exchange_rate()
        value = False
        self.cmb_exc_from.setDisabled(value)
        self.cmb_exc_to.setDisabled(value)
        self.txt_exc_amount1.setDisabled(value)
        self.txt_exc_amount2.setDisabled(value)

    def _update_exchange_rate(self):
        QCoreApplication.processEvents()
        if self.ignore_combobox_changes:
            return
        if self.stop_loading:
            return

        working_val = self.topic_info_dict["working"]
        self.topic_info_dict["working"] = True

        self.topic_info_dict["msg"] = self.getl("topic_msg_exchange_rate") + ", " + self.getl("topic_msg_getting_data")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        QCoreApplication.processEvents()

        current_valutes = self.cmb_exc_from.currentData() + self.cmb_exc_to.currentData()
        if self.cashe["exchange"]["from_to"] == current_valutes:
            amount = self._get_number(self.txt_exc_amount1.text()) * self.cashe["exchange"]["rate"]
            self.txt_exc_amount2.setText(f"{amount: ,.2f}")
            self.lbl_exc_cur1_desc.setText(self.cashe["exchange"]["desc1"])
            self.lbl_exc_cur2_desc.setText(self.cashe["exchange"]["desc2"])
            self.topic_info_dict["msg"] = ""
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return
        
        # Load site for exchange rate
        source = "https://www.xe.com/currencyconverter/convert/?Amount=#1&From=#2&To=#3"
        amount = self._get_number(self.txt_exc_amount1.text())
        if amount == 0:
            amount = 1
        source = source.replace("#1", str(amount))
        source = source.replace("#2", self.cmb_exc_from.currentData())
        source = source.replace("#3", self.cmb_exc_to.currentData())

        self.rashomon.errors(clear_errors=True)
        self.rashomon.load_project(self.getv("rashomon_folder_path") + "exchange.rpf", change_source=source)
        self.rashomon.set_compatible_mode(True)
        if self.rashomon.errors():
            self.txt_exc_amount1.setText("")
            self.txt_exc_amount2.setText("")
            self.lbl_exc_cur1.setText("---")
            self.lbl_exc_cur2.setText("---")
            self.lbl_exc_other_rates.setText(self.getl("topic_main_exchange_no_data"))
            self.topic_info_dict["msg"] = ""
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        QCoreApplication.processEvents()
        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        # Get data for exchange rate
        self.topic_info_dict["msg"] = self.getl("topic_msg_exchange_rate") + ", " + self.getl("topic_msg_getting_data")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        exc_amount_list = self.rashomon.get_segment_selection("Result", remove_tags=True)
        if self.rashomon.errors():
            for error in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl(error)
                self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.rashomon.errors(clear_errors=True)
            self.topic_info_dict["msg"] = ""
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return
        exc_amount_list = exc_amount_list.split("\n")
        exc_amount_list = list(exc_amount_list)

        if len(exc_amount_list) > 1:
            exc_amount_list.pop(-1)
        exc_amount = "".join(exc_amount_list)
        exc_amount = exc_amount.replace(" ", "")
        exc_amount = exc_amount.replace(",", "")
        exc_amount = exc_amount.strip()
        amount2 = self._get_number(exc_amount)

        self.txt_exc_amount2.setText(f"{amount2: ,.2f}")
        if not self.txt_exc_amount1.text():
            self.txt_exc_amount1.setText("1")

        other_units = self.rashomon.get_segment_selection("OtherUnits", remove_tags=True)
        self.lbl_exc_other_rates.setText(other_units)

        self.lbl_exc_cur1.setText(self.cmb_exc_from.currentData())
        self.lbl_exc_cur2.setText(self.cmb_exc_to.currentData())
        
        self.cashe["exchange"]["from_to"] = self.cmb_exc_from.currentData()+ self.cmb_exc_to.currentData()
        self.cashe["exchange"]["rate"] = amount2 / amount
        
        QCoreApplication.processEvents()
        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        self.topic_info_dict["msg"] = self.getl("topic_msg_exchange_rate") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        
        # Load site for description
        source = "https://www.oanda.com/currency-converter/en/?from=#1&to=#2&amount=1"
        source = source.replace("#1", self.cmb_exc_from.currentData())
        source = source.replace("#2", self.cmb_exc_to.currentData())

        self.rashomon.errors(clear_errors=True)
        self.rashomon.load_project(self.getv("rashomon_folder_path") + "exchange_desc.rpf", change_source=source)
        self.rashomon.set_compatible_mode(True)

        QCoreApplication.processEvents()
        if self.stop_loading:
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return
        
        self.topic_info_dict["msg"] = self.getl("topic_msg_exchange_rate") + ", " + self.getl("topic_msg_getting_data")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        # Get description data
        desc1 = self.rashomon.get_segment_selection("Valute1_Desc", remove_tags=True)
        desc2 = self.rashomon.get_segment_selection("Valute2_Desc", remove_tags=True)

        if self.rashomon.errors():
            for error in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl(error)
                self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.rashomon.errors(clear_errors=True)
            self.topic_info_dict["msg"] = ""
            self.topic_info_dict["working"] = working_val
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        self.lbl_exc_cur1_desc.setText(desc1)
        self.lbl_exc_cur2_desc.setText(desc2)
        self.cashe["exchange"]["desc1"] = desc1
        self.cashe["exchange"]["desc2"] = desc2

        self.topic_info_dict["msg"] = ""
        self.topic_info_dict["working"] = working_val
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

    def _get_number(self, value: str) -> float:
        try:
            result = float(value)
        except:
            result = 0
        return result

    def _load_location(self):
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_location") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        file = self.getv("rashomon_folder_path") + "location_topic.rpf"
        self.rashomon.errors(clear_errors=True)
        self.rashomon.load_project(file)
        self.rashomon.set_compatible_mode(True)

        if self.rashomon.errors():
            for i in self.rashomon.errors():
                self.topic_info_dict["msg"] = self.getl("topic_msg_location") + ", Error: " + i
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            return

        QCoreApplication.processEvents()
        if self.stop_loading:
            return
        
        self.topic_info_dict["msg"] = self.getl("topic_msg_location") + ", " + self.getl("topic_msg_getting_data")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.lbl_loc_city_val.setText(self.rashomon.get_segment_selection("city_000", remove_tags=True))
        self.lbl_loc_country_val.setText(self.rashomon.get_segment_selection("contry_000", remove_tags=True))
        self.lbl_loc_region_val.setText(self.rashomon.get_segment_selection("region_000", remove_tags=True))
        self.lbl_loc_lon_val.setText(self.rashomon.get_segment_selection("lon_000", remove_tags=True))
        self.lbl_loc_lat_val.setText(self.rashomon.get_segment_selection("lat_000", remove_tags=True))
        ip_txt = self.rashomon.get_segment_selection("ip_adress_000", remove_tags=True) + " "*5 + self.rashomon.get_segment_selection("org_000", remove_tags=True)
        self.lbl_loc_ip_val.setText(ip_txt)

    def _get_cashe_struct(self) -> dict:
        result = {
            "exchange": {
                "from_to": None,
                "rate": None,
                "desc1": None,
                "desc2": None
            }
        }
        return result

    def _get_user_settings(self) -> dict:
        result = {
            "exchange": {
                "from": "EUR",
                "to": "RSD"
            },
            "weather": {
                "city": "",
                "city_url": ""
            }
        }
        if "online_topic_main_settings" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("online_topic_main_settings")
            result["exchange"]["from"] = g["exchange"]["from"]
            result["exchange"]["to"] = g["exchange"]["to"]
            if "weather" in g and "city" in g["weather"]:
                result["weather"]["city"] = g["weather"]["city"]
                result["weather"]["city_url"] = g["weather"].get("city_url", "")
        
        return result

    def _update_user_settings(self) -> None:
        if self.ignore_combobox_changes:
            return
        
        self.settings["exchange"]["from"] = self.cmb_exc_from.currentData()
        self.settings["exchange"]["to"] = self.cmb_exc_to.currentData()
        self.settings["weather"]["city"] = self.txt_we_city.text()
        self.settings["weather"]["city_url"] = self.txt_we_city.objectName()

        if "online_topic_main_settings" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("online_topic_main_settings", self.settings, save_to_file=True)
        else:
            self.set_appv("online_topic_main_settings", self.settings)

    def _currency_list(self) -> dict:
        result = {
            "1INCH": {
                "name": "1INCH", 
                "desc": "1INCH",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "AAVE": {
                "name": "AAVE", 
                "desc": "AAVE",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ADA": {
                "name": "ADA", 
                "desc": "Cardano",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ada.svg"
            },
            "AED": {
                "name": "AED", 
                "desc": "Utd. Arab Emir. Dirham",
                "image": self.getv("online_topics_exc_flags_folder_path") + "aed.svg"
            },
            "AFN": {
                "name": "AFN", 
                "desc": "Afghan Afghani",
                "image": self.getv("online_topics_exc_flags_folder_path") + "afn.svg"
            },
            "ALGO": {
                "name": "ALGO", 
                "desc": "Algorand",
                "image": self.getv("online_topics_exc_flags_folder_path") + "algo.svg"
            },
            "ALL": {
                "name": "ALL", 
                "desc": "Albanian Lek",
                "image": self.getv("online_topics_exc_flags_folder_path") + "all.svg"
            },
            "AMM": {
                "name": "AMM", 
                "desc": "Armenian Dram",
                "image": self.getv("online_topics_exc_flags_folder_path") + "amm.svg"
            },
            "AMP": {
                "name": "AMP", 
                "desc": "Amp",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ANG": {
                "name": "ANG", 
                "desc": "NL Antillian Guilder",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ang.svg"
            },
            "ANKR": {
                "name": "ANKR", 
                "desc": "Ankr Network",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "AOA": {
                "name": "AOA", 
                "desc": "Angolan Kwanza",
                "image": self.getv("online_topics_exc_flags_folder_path") + "aoa.svg"
            },
            "APE": {
                "name": "APE", 
                "desc": "ApeCoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "AR": {
                "name": "AR", 
                "desc": "Arweave",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "AMP": {
                "name": "AMP", 
                "desc": "Amp",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ARS": {
                "name": "ARS", 
                "desc": "Argentine Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ars.svg"
            },
            "ATOM": {
                "name": "ATOM", 
                "desc": "Cosmos",
                "image": self.getv("online_topics_exc_flags_folder_path") + "atom.svg"
            },
            "AUD": {
                "name": "AUD", 
                "desc": "Australian Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "aud.svg"
            },
            "AVAX": {
                "name": "AVAX", 
                "desc": "Avalanche",
                "image": self.getv("online_topics_exc_flags_folder_path") + "avax.svg"
            },
            "AWG": {
                "name": "AWG", 
                "desc": "Aruban Florin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "awg.svg"
            },
            "AXS": {
                "name": "AXS", 
                "desc": "Axie Infinity",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "AZN": {
                "name": "AZN", 
                "desc": "Azerbaijan New Manat",
                "image": self.getv("online_topics_exc_flags_folder_path") + "azn.svg"
            },
            "BAL": {
                "name": "BAL", 
                "desc": "Balancer",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BAM": {
                "name": "BAM", 
                "desc": "Bosnian Mark",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bam.svg"
            },
            "BAND": {
                "name": "BAND", 
                "desc": "Band Protocol",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BAT": {
                "name": "BAT", 
                "desc": "Basic Attention Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BBD": {
                "name": "BBD", 
                "desc": "Barbados Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bbd.svg"
            },
            "BCH": {
                "name": "BCH", 
                "desc": "Bitcoin Cash",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bch.svg"
            },
            "BCHSV": {
                "name": "BCHSV", 
                "desc": "Bitcoin Cash SV",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BDT": {
                "name": "BDT", 
                "desc": "Bangladeshi Taka",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bdt.svg"
            },
            "BGN": {
                "name": "BGN", 
                "desc": "Bulgarian Lev",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bgn.svg"
            },
            "BHD": {
                "name": "BHD", 
                "desc": "Bahraini Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bhd.svg"
            },
            "BIF": {
                "name": "BIF", 
                "desc": "Burundi Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bif.svg"
            },
            "BIT": {
                "name": "BIT", 
                "desc": "BitDAO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BMD": {
                "name": "BMD", 
                "desc": "Bermudian Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bmd.svg"
            },
            "BNB": {
                "name": "BNB", 
                "desc": "Binance Coin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BND": {
                "name": "BND", 
                "desc": "Brunei Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bnd.svg"
            },
            "BOB": {
                "name": "BOB", 
                "desc": "Bolivian Boliviano",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bob.svg"
            },
            "BONE": {
                "name": "BONE", 
                "desc": "Bone",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BRL": {
                "name": "BRL", 
                "desc": "Brazilian Real",
                "image": self.getv("online_topics_exc_flags_folder_path") + "brl.svg"
            },
            "BSD": {
                "name": "BSD", 
                "desc": "Bahamian Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bsd.svg"
            },
            "BSV": {
                "name": "BSV", 
                "desc": "Bitcoin SV",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BTC": {
                "name": "BTC", 
                "desc": "Bitcoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bch.svg"
            },
            "BTCST": {
                "name": "BTCST", 
                "desc": "BTC Standard Hashrate Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BTG": {
                "name": "BTG", 
                "desc": "Bitcoin Gold",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BTN": {
                "name": "BTN", 
                "desc": "Bhutan Ngultrum",
                "image": self.getv("online_topics_exc_flags_folder_path") + "btn.svg"
            },
            "BTT": {
                "name": "BTT", 
                "desc": "BitTorrent",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BUSD": {
                "name": "BUSD", 
                "desc": "Binance USD",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "BWP": {
                "name": "BWP", 
                "desc": "Botswana Pula",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bwp.svg"
            },
            "BYN": {
                "name": "BYN", 
                "desc": "Belarusian Ruble",
                "image": self.getv("online_topics_exc_flags_folder_path") + "byn.svg"
            },
            "BZD": {
                "name": "BZD", 
                "desc": "Belize Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bzd.svg"
            },
            "CAD": {
                "name": "CAD", 
                "desc": "Canadian Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cad.svg"
            },
            "CAKE": {
                "name": "CAKE", 
                "desc": "PancakeSwap",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CDF": {
                "name": "CDF", 
                "desc": "Congolese Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cdf.svg"
            },
            "CEL": {
                "name": "CEL", 
                "desc": "Celsius Network",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CELO": {
                "name": "CELO", 
                "desc": "Celo",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CHF": {
                "name": "CHF", 
                "desc": "Swiss Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "chf.svg"
            },
            "CHZ": {
                "name": "CHZ", 
                "desc": "Chiliz",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CLP": {
                "name": "CLP", 
                "desc": "Chilean Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "clp.svg"
            },
            "CNH": {
                "name": "CNH", 
                "desc": "Chinese Yuan Renminbi (offshore)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cnh.svg"
            },
            "CNY": {
                "name": "CNY", 
                "desc": "Chinese Yuan Renminbi",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cnh.svg"
            },
            "COMP": {
                "name": "COMP", 
                "desc": "Compound Coin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "COP": {
                "name": "COP", 
                "desc": "Colombian Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cop.svg"
            },
            "CRC": {
                "name": "CRC", 
                "desc": "Costa Rican Colon",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crc.svg"
            },
            "CRO": {
                "name": "CRO", 
                "desc": "Crypto.com Chain",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CRV": {
                "name": "CRV", 
                "desc": "Curve DAO Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CUC": {
                "name": "CUC", 
                "desc": "Cuban Convertible Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cuc.svg"
            },
            "CUP": {
                "name": "CUP", 
                "desc": "Cuban Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cuc.svg"
            },
            "CVE": {
                "name": "CVE", 
                "desc": "Cape Verde Escudo",
                "image": self.getv("online_topics_exc_flags_folder_path") + "cve.svg"
            },
            "CVX": {
                "name": "CVX", 
                "desc": "Convex Finance",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "CZK": {
                "name": "CZK", 
                "desc": "Czech Koruna",
                "image": self.getv("online_topics_exc_flags_folder_path") + "czk.svg"
            },
            "DAI": {
                "name": "DAI", 
                "desc": "Dai",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DAR": {
                "name": "DAR", 
                "desc": "Mines of Dalarnia",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DASH": {
                "name": "DASH", 
                "desc": "Dash",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DC": {
                "name": "DC", 
                "desc": "Demon",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DCR": {
                "name": "DCR", 
                "desc": "Decred",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DJF": {
                "name": "DJF", 
                "desc": "Djibouti Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "djf.svg"
            },
            "DKA": {
                "name": "DKA", 
                "desc": "dKargo",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DKK": {
                "name": "DKK", 
                "desc": "Danish Krone",
                "image": self.getv("online_topics_exc_flags_folder_path") + "dkk.svg"
            },
            "DODO": {
                "name": "DODO", 
                "desc": "DODO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DOGE": {
                "name": "DOGE", 
                "desc": "Dogecoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "doge.svg"
            },
            "DOP": {
                "name": "DOP", 
                "desc": "Dominican Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "dop.svg"
            },
            "DOT": {
                "name": "DOT", 
                "desc": "Polkadot",
                "image": self.getv("online_topics_exc_flags_folder_path") + "dot.svg"
            },
            "DYDX": {
                "name": "DYDX", 
                "desc": "dYdX",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "DZD": {
                "name": "DZD", 
                "desc": "Algerian Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "dzd.svg"
            },
            "ECS": {
                "name": "ECS", 
                "desc": "Ecuador Sucre",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ecs.svg"
            },
            "EGLD": {
                "name": "EGLD", 
                "desc": "Elrond Mainnet",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "EGP": {
                "name": "EGP", 
                "desc": "Egyptian Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "egp.svg"
            },
            "ENJ": {
                "name": "ENJ", 
                "desc": "Enjin Coin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ENS": {
                "name": "ENS", 
                "desc": "Ethereum Name Service (ENS)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "EOS": {
                "name": "EOS", 
                "desc": "Eos",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ERN": {
                "name": "ERN", 
                "desc": "Eritrean Nakfa",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ern.svg"
            },
            "ETB": {
                "name": "ETB", 
                "desc": "Ethiopian Birr",
                "image": self.getv("online_topics_exc_flags_folder_path") + "etb.svg"
            },
            "ETC": {
                "name": "ETC", 
                "desc": "Ethereum Classic",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ETH": {
                "name": "ETH", 
                "desc": "Ethereum",
                "image": self.getv("online_topics_exc_flags_folder_path") + "eth.svg"
            },
            "EUR": {
                "name": "EUR", 
                "desc": "Euro",
                "image": self.getv("online_topics_exc_flags_folder_path") + "eur.svg"
            },
            "FEI": {
                "name": "FEI", 
                "desc": "Fei Protocol",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "FIDA": {
                "name": "FIDA", 
                "desc": "Bonfida",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "FIL": {
                "name": "FIL", 
                "desc": "Filecoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "fil.svg"
            },
            "FJD": {
                "name": "FJD", 
                "desc": "Fiji Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "fjd.svg"
            },
            "FKP": {
                "name": "FKP", 
                "desc": "Falkland Islands Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "fkp.svg"
            },
            "FLOW": {
                "name": "FLOW", 
                "desc": "Flow - Dapper Labs",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "FLUX": {
                "name": "FLUX", 
                "desc": "Flux",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "FTM": {
                "name": "FTM", 
                "desc": "Fantom",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "FTT": {
                "name": "FTT", 
                "desc": "FTX Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GAL": {
                "name": "GAL", 
                "desc": "Project Galaxy",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GALA": {
                "name": "GALA", 
                "desc": "Gala",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GEL": {
                "name": "GEL", 
                "desc": "Georgian Lari",
                "image": self.getv("online_topics_exc_flags_folder_path") + "gel.svg"
            },
            "GHS": {
                "name": "GHS", 
                "desc": "Ghanaian New Cedi",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ghs.svg"
            },
            "GIP": {
                "name": "GIP", 
                "desc": "Gibraltar Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "gip.svg"
            },
            "GMD": {
                "name": "GMD", 
                "desc": "Gambian Dalasi",
                "image": self.getv("online_topics_exc_flags_folder_path") + "gmd.svg"
            },
            "GMT": {
                "name": "GMT", 
                "desc": "STEPN",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GNF": {
                "name": "GNF", 
                "desc": "Guinea Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "gnf.svg"
            },
            "GNO": {
                "name": "GNO", 
                "desc": "Gnosis",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GNS": {
                "name": "GNS", 
                "desc": "GNS",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GRT": {
                "name": "GRT", 
                "desc": "The Graph",
                "image": self.getv("online_topics_exc_flags_folder_path") + "grt.svg"
            },
            "GT": {
                "name": "GT", 
                "desc": "GT",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "GTQ": {
                "name": "GTQ", 
                "desc": "Guatemalan Quetzal",
                "image": self.getv("online_topics_exc_flags_folder_path") + "gtq.svg"
            },
            "GYD": {
                "name": "GYD", 
                "desc": "Guyanese Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "gyd.svg"
            },
            "HBAR": {
                "name": "HBAR", 
                "desc": "Hedera Hashgraph",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "HKD": {
                "name": "HKD", 
                "desc": "Hong Kong Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "hkd.svg"
            },
            "HNL": {
                "name": "HNL", 
                "desc": "Honduran Lempira",
                "image": self.getv("online_topics_exc_flags_folder_path") + "hnl.svg"
            },
            "HNT": {
                "name": "HNT", 
                "desc": "Helium",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "HOLY": {
                "name": "HOLY", 
                "desc": "Holy Trinity",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "HOT": {
                "name": "HOT", 
                "desc": "Holo",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "HRK": {
                "name": "HRK", 
                "desc": "Croatian Kuna",
                "image": self.getv("online_topics_exc_flags_folder_path") + "hrk.svg"
            },
            "HT": {
                "name": "HT", 
                "desc": "Huobi Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "HTG": {
                "name": "HTG", 
                "desc": "Haitian Gourde",
                "image": self.getv("online_topics_exc_flags_folder_path") + "htg.svg"
            },
            "HUF": {
                "name": "HUF", 
                "desc": "Hungarian Forint",
                "image": self.getv("online_topics_exc_flags_folder_path") + "huf.svg"
            },
            "ICP": {
                "name": "ICP", 
                "desc": "Internet Computer",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "IDR": {
                "name": "IDR", 
                "desc": "Indonesian Rupiah",
                "image": self.getv("online_topics_exc_flags_folder_path") + "idr.svg"
            },
            "ILS": {
                "name": "ILS", 
                "desc": "Israeli New Shekel",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ils.svg"
            },
            "INR": {
                "name": "INR", 
                "desc": "Indian Rupee",
                "image": self.getv("online_topics_exc_flags_folder_path") + "inr.svg"
            },
            "IOST": {
                "name": "IOST", 
                "desc": "IOST",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "IOTA": {
                "name": "IOTA", 
                "desc": "IOTA",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "IQD": {
                "name": "IQD", 
                "desc": "Iraqi Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "iqd.svg"
            },
            "IRR": {
                "name": "IRR", 
                "desc": "Iranian Rial",
                "image": self.getv("online_topics_exc_flags_folder_path") + "irr.svg"
            },
            "ISK": {
                "name": "ISK", 
                "desc": "Iceland Krona",
                "image": self.getv("online_topics_exc_flags_folder_path") + "isk.svg"
            },
            "JASMY": {
                "name": "JASMY", 
                "desc": "Jasmy",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "JMD": {
                "name": "JMD", 
                "desc": "Jamaican Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "jmd.svg"
            },
            "JOD": {
                "name": "JOD", 
                "desc": "Jordanian Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "jod.svg"
            },
            "KAVA": {
                "name": "KAVA", 
                "desc": "Kava",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KCS": {
                "name": "KCS", 
                "desc": "KuCoin Shares",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KES": {
                "name": "KES", 
                "desc": "Kenyan Shilling",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kes.svg"
            },
            "KGS": {
                "name": "KGS", 
                "desc": "Kyrgyzstanian Som",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kgs.svg"
            },
            "KHR": {
                "name": "KHR", 
                "desc": "Cambodian Riel",
                "image": self.getv("online_topics_exc_flags_folder_path") + "khr.svg"
            },
            "KLAY": {
                "name": "KLAY", 
                "desc": "Klaytn",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KMD": {
                "name": "KMD", 
                "desc": "Komodo",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KMF": {
                "name": "KMF", 
                "desc": "Comoros Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kmf.svg"
            },
            "KNC": {
                "name": "KNC", 
                "desc": "Kyber Network",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KPW": {
                "name": "KPW", 
                "desc": "North Korean Won",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kpw.svg"
            },
            "KRW": {
                "name": "KRW", 
                "desc": "Korean Won",
                "image": self.getv("online_topics_exc_flags_folder_path") + "krw.svg"
            },
            "KSM": {
                "name": "KSM", 
                "desc": "Kusama",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KSOS": {
                "name": "KSOS", 
                "desc": "Kilo OpenDAO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "KWD": {
                "name": "KWD", 
                "desc": "Kuwaiti Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kwd.svg"
            },
            "KYD": {
                "name": "KYD", 
                "desc": "Cayman Islands Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kyd.svg"
            },
            "KZT": {
                "name": "KZT", 
                "desc": "Kazakhstan Tenge",
                "image": self.getv("online_topics_exc_flags_folder_path") + "kzt.svg"
            },
            "LAK": {
                "name": "LAK", 
                "desc": "Lao Kip",
                "image": self.getv("online_topics_exc_flags_folder_path") + "lak.svg"
            },
            "LAZIO": {
                "name": "LAZIO", 
                "desc": "Lazio Fan Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LBP": {
                "name": "LBP", 
                "desc": "Lebanese Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "lbp.svg"
            },
            "LDO": {
                "name": "LDO", 
                "desc": "Lido DAO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LEO": {
                "name": "LEO", 
                "desc": "LEO Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LINK": {
                "name": "LINK", 
                "desc": "ChainLink",
                "image": self.getv("online_topics_exc_flags_folder_path") + "link.svg"
            },
            "LKR": {
                "name": "LKR", 
                "desc": "Sri Lanka Rupee",
                "image": self.getv("online_topics_exc_flags_folder_path") + "lkr.svg"
            },
            "LOKA": {
                "name": "LOKA", 
                "desc": "League of Kingdoms",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LOOKS": {
                "name": "LOOKS", 
                "desc": "LooksRare Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LOOM": {
                "name": "LOOM", 
                "desc": "Loom Network",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LRC": {
                "name": "LRC", 
                "desc": "Loopring",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LRD": {
                "name": "LRD", 
                "desc": "Liberian Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "lrd.svg"
            },
            "LSL": {
                "name": "LSL", 
                "desc": "Lesotho Loti",
                "image": self.getv("online_topics_exc_flags_folder_path") + "lsl.svg"
            },
            "LTC": {
                "name": "LTC", 
                "desc": "Litecoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ltc.svg"
            },
            "LUNA": {
                "name": "LUNA", 
                "desc": "Terra Luna Classic",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LUNC": {
                "name": "LUNC", 
                "desc": "Terra Luna Classic (relisted)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "LYD": {
                "name": "LYD", 
                "desc": "Libyan Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "lyd.svg"
            },
            "MAD": {
                "name": "MAD", 
                "desc": "Moroccan Dirham",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mad.svg"
            },
            "MANA": {
                "name": "MANA", 
                "desc": "Decentraland",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mana.svg"
            },
            "MATIC": {
                "name": "MATIC", 
                "desc": "Matic Network",
                "image": self.getv("online_topics_exc_flags_folder_path") + "matic.svg"
            },
            "MDL": {
                "name": "MDL", 
                "desc": "Moldovan Leu",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mdl.svg"
            },
            "MGA": {
                "name": "MGA", 
                "desc": "Malagasy Ariary",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mga.svg"
            },
            "MINA": {
                "name": "MINA", 
                "desc": "Mina",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "MIOTA": {
                "name": "MIOTA", 
                "desc": "IOTA",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "MKD": {
                "name": "MKD", 
                "desc": "Macedonian Denar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mkd.svg"
            },
            "MKR": {
                "name": "MKR", 
                "desc": "Maker",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "MMK": {
                "name": "MMK", 
                "desc": "Myanmar Kyat",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mmk.svg"
            },
            "MNT": {
                "name": "MNT", 
                "desc": "Mongolian Tugrik",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mnt.svg"
            },
            "MOP": {
                "name": "MOP", 
                "desc": "Macau Pataca",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mop.svg"
            },
            "MRU": {
                "name": "MRU", 
                "desc": "Mauritania Ouguiya",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mru.svg"
            },
            "MUR": {
                "name": "MUR", 
                "desc": "Mauritius Rupee",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mur.svg"
            },
            "MVR": {
                "name": "MVR", 
                "desc": "Maldive Rufiyaa",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mvr.svg"
            },
            "MWK": {
                "name": "MWK", 
                "desc": "Malawi Kwacha",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mwk.svg"
            },
            "MXN": {
                "name": "MXN", 
                "desc": "Mexican Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mxn.svg"
            },
            "MYR": {
                "name": "MYR", 
                "desc": "Malaysian Ringgit",
                "image": self.getv("online_topics_exc_flags_folder_path") + "myr.svg"
            },
            "MZN": {
                "name": "MZN", 
                "desc": "Mozambique New Metical",
                "image": self.getv("online_topics_exc_flags_folder_path") + "mzn.svg"
            },
            "NAD": {
                "name": "NAD", 
                "desc": "Namibia Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "nad.svg"
            },
            "NEAR": {
                "name": "NEAR", 
                "desc": "Near",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "NEO": {
                "name": "NEO", 
                "desc": "NEO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "NEXO": {
                "name": "NEXO", 
                "desc": "Nexo",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "NFTN": {
                "name": "NFTN", 
                "desc": "NFTN",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "NGN": {
                "name": "NGN", 
                "desc": "Nigerian Naira",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ngn.svg"
            },
            "NIO": {
                "name": "NIO", 
                "desc": "Nicaraguan Cordoba Oro",
                "image": self.getv("online_topics_exc_flags_folder_path") + "nio.svg"
            },
            "NOK": {
                "name": "NOK", 
                "desc": "Norwegian Kroner",
                "image": self.getv("online_topics_exc_flags_folder_path") + "nok.svg"
            },
            "NPR": {
                "name": "NPR", 
                "desc": "Nepalese Rupee",
                "image": self.getv("online_topics_exc_flags_folder_path") + "npr.svg"
            },
            "NZD": {
                "name": "NZD", 
                "desc": "New Zealand Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "nzd.svg"
            },
            "OKB": {
                "name": "OKB", 
                "desc": "OKB",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "OMG": {
                "name": "OMG", 
                "desc": "OmiseGO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "OMR": {
                "name": "OMR", 
                "desc": "Omani Rial",
                "image": self.getv("online_topics_exc_flags_folder_path") + "omr.svg"
            },
            "ONE": {
                "name": "ONE", 
                "desc": "Harmony",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "OP": {
                "name": "OP", 
                "desc": "Optimism",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "OXY": {
                "name": "OXY", 
                "desc": "Oxygen",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "PAB": {
                "name": "PAB", 
                "desc": "Panamanian Balboa",
                "image": self.getv("online_topics_exc_flags_folder_path") + "pab.svg"
            },
            "PAXG": {
                "name": "PAXG", 
                "desc": "PAX Gold",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "PEN": {
                "name": "PEN", 
                "desc": "Peruvian Nuevo Sol",
                "image": self.getv("online_topics_exc_flags_folder_path") + "pen.svg"
            },
            "PEOPLE": {
                "name": "PEOPLE", 
                "desc": "ConstitutionDAO",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "PGK": {
                "name": "PGK", 
                "desc": "Papua New Guinea Kina",
                "image": self.getv("online_topics_exc_flags_folder_path") + "pgk.svg"
            },
            "PHP": {
                "name": "PHP", 
                "desc": "Philippine Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "php.svg"
            },
            "PKR": {
                "name": "PKR", 
                "desc": "Pakistan Rupee",
                "image": self.getv("online_topics_exc_flags_folder_path") + "pkr.svg"
            },
            "PLA": {
                "name": "PLA", 
                "desc": "PlayDapp Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "PLN": {
                "name": "PLN", 
                "desc": "Polish Zloty",
                "image": self.getv("online_topics_exc_flags_folder_path") + "pln.svg"
            },
            "PYG": {
                "name": "PYG", 
                "desc": "Paraguay Guarani",
                "image": self.getv("online_topics_exc_flags_folder_path") + "pyg.svg"
            },
            "QAR": {
                "name": "QAR", 
                "desc": "Qatari Rial",
                "image": self.getv("online_topics_exc_flags_folder_path") + "qar.svg"
            },
            "QNT": {
                "name": "QNT", 
                "desc": "Quant",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "QTUM": {
                "name": "QTUM", 
                "desc": "Qtum",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "RAY": {
                "name": "RAY", 
                "desc": "Raydium",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "REN": {
                "name": "REN", 
                "desc": "Ren",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "RON": {
                "name": "RON", 
                "desc": "Romanian New Leu",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ron.svg"
            },
            "ROSE": {
                "name": "ROSE", 
                "desc": "Oasis Network",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "RSD": {
                "name": "RSD", 
                "desc": "Serbian Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "rsd.svg"
            },
            "RSR": {
                "name": "RSR", 
                "desc": "Reserve Rights",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "RUB": {
                "name": "RUB", 
                "desc": "Russian Rouble",
                "image": self.getv("online_topics_exc_flags_folder_path") + "rub.svg"
            },
            "RUNE": {
                "name": "RUNE", 
                "desc": "Thorchain",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "RWF": {
                "name": "RWF", 
                "desc": "Rwandan Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "rwf.svg"
            },
            "SAND": {
                "name": "SAND", 
                "desc": "SAND",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sand.svg"
            },
            "SANTOS": {
                "name": "SANTOS", 
                "desc": "Santos FC Fan Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SAR": {
                "name": "SAR", 
                "desc": "Saudi Riyal",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sar.svg"
            },
            "SBD": {
                "name": "SBD", 
                "desc": "Solomon Islands Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sbd.svg"
            },
            "SCR": {
                "name": "SCR", 
                "desc": "Seychelles Rupee",
                "image": self.getv("online_topics_exc_flags_folder_path") + "scr.svg"
            },
            "SDG": {
                "name": "SDG", 
                "desc": "Sudanese Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sdg.svg"
            },
            "SEK": {
                "name": "SEK", 
                "desc": "Swedish Krona",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sek.svg"
            },
            "SGD": {
                "name": "SGD", 
                "desc": "Singapore Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sgd.svg"
            },
            "SHIB": {
                "name": "SHIB", 
                "desc": "Shiba Inu",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SHP": {
                "name": "SHP", 
                "desc": "St. Helena Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "shp.svg"
            },
            "SLL": {
                "name": "SLL", 
                "desc": "Sierra Leone Leone",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sll.svg"
            },
            "SLP": {
                "name": "SLP", 
                "desc": "Smooth Love Potion",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SNX": {
                "name": "SNX", 
                "desc": "Synthetix Network Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SOL": {
                "name": "SOL", 
                "desc": "Solana",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sol.svg"
            },
            "SOS": {
                "name": "SOS", 
                "desc": "Somali Shilling",
                "image": self.getv("online_topics_exc_flags_folder_path") + "sos.svg"
            },
            "SPELL": {
                "name": "SPELL", 
                "desc": "Spell Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SRD": {
                "name": "SRD", 
                "desc": "Suriname Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "srd.svg"
            },
            "SRM": {
                "name": "SRM", 
                "desc": "Serum",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "STG": {
                "name": "STG", 
                "desc": "Stargate Finance",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "STN": {
                "name": "STN", 
                "desc": "Sao Tome/Principe Dobra",
                "image": self.getv("online_topics_exc_flags_folder_path") + "stn.svg"
            },
            "STORJ": {
                "name": "STORJ", 
                "desc": "Storj",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "STX": {
                "name": "STX", 
                "desc": "Stacks",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SUSHI": {
                "name": "SUSHI", 
                "desc": "Sushi",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "SVC": {
                "name": "SVC", 
                "desc": "El Salvador Colon",
                "image": self.getv("online_topics_exc_flags_folder_path") + "svc.svg"
            },
            "SYP": {
                "name": "SYP", 
                "desc": "Syrian Pound",
                "image": self.getv("online_topics_exc_flags_folder_path") + "syp.svg"
            },
            "SZL": {
                "name": "SZL", 
                "desc": "Swaziland Lilangeni",
                "image": self.getv("online_topics_exc_flags_folder_path") + "szl.svg"
            },
            "THB": {
                "name": "THB", 
                "desc": "Thai Baht",
                "image": self.getv("online_topics_exc_flags_folder_path") + "thb.svg"
            },
            "THETA": {
                "name": "THETA", 
                "desc": "Theta Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TJS": {
                "name": "TJS", 
                "desc": "Tajikistan Somoni",
                "image": self.getv("online_topics_exc_flags_folder_path") + "tjs.svg"
            },
            "TKING": {
                "name": "TKING", 
                "desc": "Tiger King",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TMT": {
                "name": "TMT", 
                "desc": "Turkmenistan New Manat",
                "image": self.getv("online_topics_exc_flags_folder_path") + "tmt.svg"
            },
            "TND": {
                "name": "TND", 
                "desc": "Tunisian Dinar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "tnd.svg"
            },
            "TOP": {
                "name": "TOP", 
                "desc": "Tongan Pa'anga",
                "image": self.getv("online_topics_exc_flags_folder_path") + "top.svg"
            },
            "TRU": {
                "name": "TRU", 
                "desc": "TrueFi",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TRX": {
                "name": "TRX", 
                "desc": "TRON",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TRY": {
                "name": "TRY", 
                "desc": "TRON",
                "image": self.getv("online_topics_exc_flags_folder_path") + "try.svg"
            },
            "TRYB": {
                "name": "TRYB", 
                "desc": "BiLira",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TTD": {
                "name": "TTD", 
                "desc": "Trinidad/Tobago Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ttd.svg"
            },
            "TUSD": {
                "name": "TUSD", 
                "desc": "TrueUSD",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TWD": {
                "name": "TWD", 
                "desc": "Taiwan Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "twd.svg"
            },
            "TWT": {
                "name": "TWT", 
                "desc": "Trust Wallet Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "TZS": {
                "name": "TZS", 
                "desc": "Tanzanian Shilling",
                "image": self.getv("online_topics_exc_flags_folder_path") + "tzs.svg"
            },
            "UAH": {
                "name": "UAH", 
                "desc": "Ukraine Hryvnia",
                "image": self.getv("online_topics_exc_flags_folder_path") + "uah.svg"
            },
            "UGX": {
                "name": "UGX", 
                "desc": "Uganda Shilling",
                "image": self.getv("online_topics_exc_flags_folder_path") + "ugx.svg"
            },
            "UMA": {
                "name": "UMA", 
                "desc": "UMA",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "UNI": {
                "name": "UNI", 
                "desc": "Uniswap",
                "image": self.getv("online_topics_exc_flags_folder_path") + "uni.svg"
            },
            "USD": {
                "name": "USD", 
                "desc": "US Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "usd.svg"
            },
            "USDC": {
                "name": "USDC", 
                "desc": "USD Coin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "USDD": {
                "name": "USDD", 
                "desc": "USDD",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "USDN": {
                "name": "USDN", 
                "desc": "Neutrino USD",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "USDP": {
                "name": "USDP", 
                "desc": "Pax Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "USDT": {
                "name": "USDT", 
                "desc": "Tether",
                "image": self.getv("online_topics_exc_flags_folder_path") + "usdt.svg"
            },
            "UYU": {
                "name": "UYU", 
                "desc": "Uruguayan Peso",
                "image": self.getv("online_topics_exc_flags_folder_path") + "uyu.svg"
            },
            "UZS": {
                "name": "UZS", 
                "desc": "Uzbekistan Som",
                "image": self.getv("online_topics_exc_flags_folder_path") + "uzs.svg"
            },
            "VEF": {
                "name": "VEF", 
                "desc": "Venezuelan Bolivar Fuerte",
                "image": self.getv("online_topics_exc_flags_folder_path") + "vef.svg"
            },
            "VES": {
                "name": "VES", 
                "desc": "Venezuelan Bolivar Soberano",
                "image": self.getv("online_topics_exc_flags_folder_path") + "vef.svg"
            },
            "VET": {
                "name": "VET", 
                "desc": "VeChain Thor Blockchain",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "VGX": {
                "name": "VGX", 
                "desc": "Voyager Token",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "VND": {
                "name": "VND", 
                "desc": "Vietnamese Dong",
                "image": self.getv("online_topics_exc_flags_folder_path") + "vnd.svg"
            },
            "VUV": {
                "name": "VUV", 
                "desc": "Vanuatu Vatu",
                "image": self.getv("online_topics_exc_flags_folder_path") + "vuv.svg"
            },
            "WAVES": {
                "name": "WAVES", 
                "desc": "Waves",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "WBNB": {
                "name": "WBNB", 
                "desc": "Wrapped BNB",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "WBTC": {
                "name": "WBTC", 
                "desc": "Wrapped Bitcoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "WBTC.svg"
            },
            "WETH": {
                "name": "WETH", 
                "desc": "Wrapped ETH",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "WST": {
                "name": "WST", 
                "desc": "Samoan Tala",
                "image": self.getv("online_topics_exc_flags_folder_path") + "wst.svg"
            },
            "XAG": {
                "name": "XAG", 
                "desc": "Silver (oz.)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xag.svg"
            },
            "XAU": {
                "name": "XAU", 
                "desc": "Gold (oz.)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xau.svg"
            },
            "XBT": {
                "name": "XBT", 
                "desc": "1INCH",
                "image": self.getv("online_topics_exc_flags_folder_path") + "bch.svg"
            },
            "XCD": {
                "name": "XCD", 
                "desc": "East Caribbean Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xcd.svg"
            },
            "XEC": {
                "name": "XEC", 
                "desc": "eCash",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "XEM": {
                "name": "XEM", 
                "desc": "New Economy Movement",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "XLM": {
                "name": "XLM", 
                "desc": "Stellar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xlm.svg"
            },
            "XMR": {
                "name": "XMR", 
                "desc": "Monero",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "XOF": {
                "name": "XOF", 
                "desc": "West African CFA Franc",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xof.svg"
            },
            "XPD": {
                "name": "XPD", 
                "desc": "Palladium (oz.)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xpd.svg"
            },
            "XPF": {
                "name": "XPF", 
                "desc": "Pacific Franc Exchange",
                "image": self.getv("online_topics_exc_flags_folder_path") + "no_flag.svg"
            },
            "XPT": {
                "name": "XPT", 
                "desc": "Platinum (oz.)",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xpt.svg"
            },
            "XRP": {
                "name": "XRP", 
                "desc": "Ripple",
                "image": self.getv("online_topics_exc_flags_folder_path") + "xrp.svg"
            },
            "XT": {
                "name": "XT", 
                "desc": "ExtremeCoin",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "XTZ": {
                "name": "XTZ", 
                "desc": "Tezos",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "YER": {
                "name": "YER", 
                "desc": "Yemen Rial",
                "image": self.getv("online_topics_exc_flags_folder_path") + "yer.svg"
            },
            "YFI": {
                "name": "YFI", 
                "desc": "yearn.finance",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "YFII": {
                "name": "YFII", 
                "desc": "DFI.money",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ZAR": {
                "name": "ZAR", 
                "desc": "South African Rand",
                "image": self.getv("online_topics_exc_flags_folder_path") + "zar.svg"
            },
            "ZEC": {
                "name": "ZEC", 
                "desc": "Zcash",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ZIL": {
                "name": "ZIL", 
                "desc": "Zilliqa",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ZMW": {
                "name": "ZMW", 
                "desc": "Zambian Kwacha",
                "image": self.getv("online_topics_exc_flags_folder_path") + "zmw.svg"
            },
            "ZRX": {
                "name": "ZRX", 
                "desc": "0x",
                "image": self.getv("online_topics_exc_flags_folder_path") + "crypto_generic.svg"
            },
            "ZWL": {
                "name": "ZWL", 
                "desc": "Zimbabwe Dollar",
                "image": self.getv("online_topics_exc_flags_folder_path") + "zwl.svg"
            }
        }
        return result        
    
    def _define_widgets(self):
        # Location
        self.lbl_location: QLabel = self.findChild(QLabel, "lbl_location")
        self.lbl_loc_city: QLabel = self.findChild(QLabel, "lbl_loc_city")
        self.lbl_loc_region: QLabel = self.findChild(QLabel, "lbl_loc_region")
        self.lbl_loc_contry: QLabel = self.findChild(QLabel, "lbl_loc_contry")
        self.lbl_loc_ip: QLabel = self.findChild(QLabel, "lbl_loc_ip")
        self.lbl_loc_lon: QLabel = self.findChild(QLabel, "lbl_loc_lon")
        self.lbl_loc_lat: QLabel = self.findChild(QLabel, "lbl_loc_lat")

        self.lbl_loc_city_val: QLabel = self.findChild(QLabel, "lbl_loc_city_val")
        self.lbl_loc_region_val: QLabel = self.findChild(QLabel, "lbl_loc_region_val")
        self.lbl_loc_country_val: QLabel = self.findChild(QLabel, "lbl_loc_country_val")
        self.lbl_loc_ip_val: QLabel = self.findChild(QLabel, "lbl_loc_ip_val")
        self.lbl_loc_lon_val: QLabel = self.findChild(QLabel, "lbl_loc_lon_val")
        self.lbl_loc_lat_val: QLabel = self.findChild(QLabel, "lbl_loc_lat_val")

        self.lbl_site_mylocation: QLabel = self.findChild(QLabel, "lbl_site_mylocation")
        self.btn_loc_map: QPushButton = self.findChild(QPushButton, "btn_loc_map")

        self.web_engine: QWebEngineView = QWebEngineView(self)
        self.web_engine.setVisible(False)

        # Exchange rate
        self.lbl_exc: QLabel = self.findChild(QLabel, "lbl_exc")
        self.lbl_exc_from: QLabel = self.findChild(QLabel, "lbl_exc_from")
        self.lbl_exc_to: QLabel = self.findChild(QLabel, "lbl_exc_to")
        self.cmb_exc_from: QComboBox = self.findChild(QComboBox, "cmb_exc_from")
        self.cmb_exc_to: QComboBox = self.findChild(QComboBox, "cmb_exc_to")
        self.txt_exc_amount1: QLineEdit = self.findChild(QLineEdit, "txt_exc_amount1")
        self.txt_exc_amount2: QLineEdit = self.findChild(QLineEdit, "txt_exc_amount2")
        self.lbl_exc_cur1: QLabel = self.findChild(QLabel, "lbl_exc_cur1")
        self.lbl_exc_cur2: QLabel = self.findChild(QLabel, "lbl_exc_cur2")
        self.lbl_exc_cur1_desc: QLabel = self.findChild(QLabel, "lbl_exc_cur1_desc")
        self.lbl_exc_cur2_desc: QLabel = self.findChild(QLabel, "lbl_exc_cur2_desc")
        self.btn_exc_switch: QPushButton = self.findChild(QPushButton, "btn_exc_switch")
        self.lbl_exc_other_rates: QLabel = self.findChild(QLabel, "lbl_exc_other_rates")
        self.lbl_site_oanda: QLabel = self.findChild(QLabel, "lbl_site_oanda")
        self.lbl_site_xe: QLabel = self.findChild(QLabel, "lbl_site_xe")

        # Weather
        self.lbl_weather: QLabel = self.findChild(QLabel, "lbl_weather")
        self.lbl_we_city: QLabel = self.findChild(QLabel, "lbl_we_city")
        self.lbl_site_timeanddate: QLabel = self.findChild(QLabel, "lbl_site_timeanddate")
        self.txt_we_city: QLineEdit = self.findChild(QLineEdit, "txt_we_city")
        self.btn_we_city_go: QPushButton = self.findChild(QPushButton, "btn_we_city_go")

        self.frm_we_result: QFrame = self.findChild(QFrame, "frm_we_result")
        self.lbl_we_title: QLabel = self.findChild(QLabel, "lbl_we_title")
        self.lbl_we_result_city: QLabel = self.findChild(QLabel, "lbl_we_result_city")
        self.lbl_we_result_temp: QLabel = self.findChild(QLabel, "lbl_we_result_temp")
        self.lbl_we_result_desc: QLabel = self.findChild(QLabel, "lbl_we_result_desc")
        self.lbl_we_result_flag: QLabel = self.findChild(QLabel, "lbl_we_result_flag")
        self.lbl_we_result_pic: QLabel = self.findChild(QLabel, "lbl_we_result_pic")
        self.lbl_we_map: QLabel = self.findChild(QLabel, "lbl_we_map")
        self.lbl_we_map_loc: QLabel = self.findChild(QLabel, "lbl_we_map_loc")
        self.lbl_we_no_data: QLabel = self.findChild(QLabel, "lbl_we_no_data")
        self.lbl_we_search_title: QLabel = self.findChild(QLabel, "lbl_we_search_title")
        self.prg_we: QProgressBar = self.findChild(QProgressBar, "prg_we")
        self.lbl_5h_title: QLabel = self.findChild(QLabel, "lbl_5h_title")
        self.lbl_48h_title: QLabel = self.findChild(QLabel, "lbl_48h_title")
        self.lbl_14d_title: QLabel = self.findChild(QLabel, "lbl_14d_title")

        self.frm_near: QFrame = self.findChild(QFrame, "frm_near")
        self.lbl_near_desc1: QLabel = self.findChild(QLabel, "lbl_near_desc1")
        self.lbl_near_desc2: QLabel = self.findChild(QLabel, "lbl_near_desc2")
        self.lbl_near_desc3: QLabel = self.findChild(QLabel, "lbl_near_desc3")
        self.lbl_near_pic1: QLabel = self.findChild(QLabel, "lbl_near_pic1")
        self.lbl_near_pic2: QLabel = self.findChild(QLabel, "lbl_near_pic2")
        self.lbl_near_pic3: QLabel = self.findChild(QLabel, "lbl_near_pic3")
        self.lbl_near_temp1: QLabel = self.findChild(QLabel, "lbl_near_temp1")
        self.lbl_near_temp2: QLabel = self.findChild(QLabel, "lbl_near_temp2")
        self.lbl_near_temp3: QLabel = self.findChild(QLabel, "lbl_near_temp3")
        self.lbl_near_title: QLabel = self.findChild(QLabel, "lbl_near_title")


        self._define_widgets_text()
        self._define_widgets_apperance()

    def _define_widgets_text(self):
        # Location
        self.lbl_location.setText(self.getl("topic_main_lbl_location_text"))
        self.lbl_location.setToolTip(self.getl("topic_main_lbl_location_tt"))
        self.lbl_loc_city.setText(self.getl("topic_main_lbl_loc_city_text"))
        self.lbl_loc_city.setToolTip(self.getl("topic_main_lbl_loc_city_tt"))
        self.lbl_loc_region.setText(self.getl("topic_main_lbl_loc_region_text"))
        self.lbl_loc_region.setToolTip(self.getl("topic_main_lbl_loc_region_tt"))
        self.lbl_loc_contry.setText(self.getl("topic_main_lbl_loc_contry_text"))
        self.lbl_loc_contry.setToolTip(self.getl("topic_main_lbl_loc_contry_tt"))
        self.lbl_loc_ip.setText(self.getl("topic_main_lbl_loc_ip_text"))
        self.lbl_loc_ip.setToolTip(self.getl("topic_main_lbl_loc_ip_tt"))
        self.lbl_loc_lon.setText(self.getl("topic_main_lbl_loc_lon_text"))
        self.lbl_loc_lon.setToolTip(self.getl("topic_main_lbl_loc_lon_tt"))
        self.lbl_loc_lat.setText(self.getl("topic_main_lbl_loc_lat_text"))
        self.lbl_loc_lat.setToolTip(self.getl("topic_main_lbl_loc_lat_tt"))
        # Set default text
        self.lbl_loc_city_val.setText("-")
        self.lbl_loc_region_val.setText("-")
        self.lbl_loc_country_val.setText("-")
        self.lbl_loc_ip_val.setText("-")
        self.lbl_loc_lon_val.setText("-")
        self.lbl_loc_lat_val.setText("-")

        # Exchange rate
        self.lbl_exc.setText(self.getl("topic_main_lbl_exc_text"))
        self.lbl_exc.setToolTip(self.getl("topic_main_lbl_exc_tt"))
        self.lbl_exc_from.setText(self.getl("topic_main_lbl_exc_from_text"))
        self.lbl_exc_from.setToolTip(self.getl("topic_main_lbl_exc_from_tt"))
        self.lbl_exc_to.setText(self.getl("topic_main_lbl_exc_to_text"))
        self.lbl_exc_to.setToolTip(self.getl("topic_main_lbl_exc_to_tt"))
        self.btn_exc_switch.setToolTip(self.getl("topic_main_btn_exc_switch_tt"))

        # Site urls
        self.lbl_site_mylocation.setToolTip("https://my-location.org/")
        self.lbl_site_oanda.setToolTip("https://www.oanda.com/currency-converter/en/")
        self.lbl_site_xe.setToolTip("https://www.xe.com/currencyconverter/convert/")
        self.lbl_site_timeanddate.setToolTip("https://www.timeanddate.com/weather/")

    def _define_widgets_apperance(self):
        self.setFixedSize(1400, 1400)
        
        self.frm_we_result.setVisible(False)
        self.lbl_we_map.setVisible(False)
        self.lbl_we_map_loc.setVisible(False)
        self.lbl_we_no_data.setVisible(False)
        self.lbl_we_search_title.setVisible(False)
        self.prg_we.setVisible(False)

        self.tbl_info = QTableWidget(self)
        self.tbl_5h = QTableWidget(self)
        self.tbl_48h = QTableWidget(self)
        self.tbl_14d = QTableWidget(self)
        self.tbl_search = QTableWidget(self)
        self.tbl_info.setVisible(False)
        self.tbl_5h.setVisible(False)
        self.tbl_48h.setVisible(False)
        self.tbl_14d.setVisible(False)
        self.tbl_search.setVisible(False)
        self.lbl_5h_title.setVisible(False)
        self.lbl_48h_title.setVisible(False)
        self.lbl_14d_title.setVisible(False)
        self.frm_near.setVisible(False)

        self.txt_we_city.setObjectName("")


