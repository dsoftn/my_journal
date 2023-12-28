from PyQt5.QtWidgets import (QFrame, QPushButton, QWidget, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QSpinBox, QTextEdit)
from PyQt5.QtGui import QPixmap, QMouseEvent, QResizeEvent, QIcon, QFontMetrics
from PyQt5.QtCore import QSize, Qt, QCoreApplication
from PyQt5 import uic
from PyQt5.QtMultimedia import QSound

import webbrowser
import random

import settings_cls
import utility_cls
import html_parser_cls
from online_abstract_topic import AbstractTopic


class Numbers(QFrame):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, data: dict) -> None:
        """
        data["border] = boolean
        data["hor_padding"] = int
        data["ver_padding"] = int
        data["hor_spacing"] = int
        data["ver_spacing"] = int
        data["numbers"] = list of numbers
        data["number_width"] = int
        data["number_height"] = int
        data["number_image_path"] = string
        data["feedback_click_function"] = function
        """
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
        self.data = self._populate_data(data)

        self._create_frame()
        self.update_numbers(self.data["numbers"])

    def update_numbers(self, numbers: list):
        # Delete old widgets
        for item in self.children():
            item.deleteLater()

        x = self.data["hor_padding"]
        y = self.data["ver_padding"]

        # Find font size
        font = self.font()
        for i in range(8, 72):
            font.setPointSize(i)
            fm = QFontMetrics(font)
            if fm.height() > self.data["number_height"] / 1.5:
                break

        # Create new widgets
        for number in numbers:
            lbl_pic = QLabel(self)
            lbl_pic.setPixmap(QPixmap(self.data["number_image_path"]))
            lbl_pic.resize(self.data["number_width"], self.data["number_height"])
            lbl_pic.setScaledContents(True)
            lbl_pic.move(x, y)

            lbl_value = QLabel(self)
            lbl_value.setText(str(number))
            lbl_value.setAlignment(Qt.AlignCenter)
            lbl_value.setFont(font)
            lbl_value.move(x, y)
            lbl_value.resize(self.data["number_width"] - 2, self.data["number_height"] - 2)
            lbl_value.setStyleSheet("QLabel {color: rgb(255, 255, 0); background-color: rgba(255, 255, 255, 0);} QLabel:hover {color: rgb(230, 255, 0);}")
            lbl_value.setCursor(Qt.PointingHandCursor)
            lbl_value.mousePressEvent = lambda event, number=number: self._on_number_clicked(event, number)

            x += self.data["number_width"] + self.data["hor_spacing"]
        
        lbl_remove = QLabel(self)
        lbl_remove.setPixmap(QPixmap(self.getv("cancel_icon_path")))
        lbl_remove.resize(self.data["number_width"], self.data["number_height"])
        lbl_remove.setScaledContents(True)
        lbl_remove.move(x, y)
        lbl_remove.setStyleSheet("QLabel:hover {background-color: #5ad9ff;}")
        lbl_remove.setToolTip("Obriši ovu kombinaciju !")
        x += self.data["number_width"] + self.data["hor_spacing"]
        lbl_remove.mousePressEvent = lambda event, number=numbers: self._on_number_clicked(event, number)

        self.resize(x - self.data["hor_spacing"] + self.data["hor_padding"], y + self.data["number_height"] + self.data["ver_padding"])

    def _on_number_clicked(self, event: QMouseEvent, number: int):
        if event.button() == Qt.LeftButton:
            if self.data["feedback_click_function"] is not None:
                self.data["feedback_click_function"](number)

    def _populate_data(self, data: dict) -> dict:
        result = {
            "border": data.get("border", True),
            "hor_padding": data.get("hor_padding", 0),
            "ver_padding": data.get("ver_padding", 0),
            "hor_spacing": data.get("hor_spacing", 0),
            "ver_spacing": data.get("ver_spacing", 0),
            "numbers": data.get("numbers", []),
            "number_width": data.get("number_width", 0),
            "number_height": data.get("number_height", 0),
            "number_image_path": data.get("number_image_path", self.getv("ball_red_icon_path")),
            "feedback_click_function": data.get("feedback_click_function", None)
        }
        return result

    def _create_frame(self):
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.Box)
        if self.data["border"]:
            self.setLineWidth(1)
        else:
            self.setLineWidth(0)


class WorkingFrame(QFrame):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, data: dict) -> None:
        """
        data["type"] = string (add_komb, add_sys, edit_komb, edit_sys)
        data["item_type"] = string (komb, sys)
        data["width"] = int
        data["item"] = dict
        data["feedback_function"] = function,
        data["reserved_names"] = list of allready reserved names
        """
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
        self.selected_numbers = []
        
        self.max_numbers = 7
        self.max_numbers_pool = 39
        if self.data["item"]:
            self.max_numbers_pool = self.data["item"]["sys_numbers"]
        if self.data["item_type"] == "komb":
            self.max_numbers_pool = 39

        self.selected_kombs = []
        self.sound_max_numbers_reached = QSound(self.getv("def_add_auto_added_image_error_sound_file_path"))

        if "view" in self.data["type"]:
            self._create_frame()
        else:
            self._create_view_frame()

    def _create_view_frame(self):
        pass

    def _number_pick_frame(self, cell_size: QSize = None, font_size: int = None) -> QFrame:
        if cell_size is None:
            cell_size = QSize(35, 25)
        if font_size is None:
            font_size = 14

        frm = QFrame(self)
        frm.setFrameShape(QFrame.Box)
        frm.setFrameShadow(QFrame.Plain)
        frm.setLineWidth(1)
        frm.setStyleSheet("color: #d40000; background-color: #f0f0f0; border-color: #d40000; border-style: solid; border-width: 1px;")

        h_spacing = 3
        v_spacing = 3
        x = h_spacing
        y = v_spacing
        w = cell_size.width() * 3 + h_spacing * 4

        # Title bar
        # Shuffle numbers button
        btn_shuffle = QPushButton(frm)
        btn_shuffle.setIcon(QIcon(QPixmap(self.getv("online_topic_dls_shuffle_icon_path"))))
        btn_shuffle.setIconSize(QSize(20, 20))
        btn_shuffle.move(x, y)
        btn_shuffle.resize(cell_size.height(), cell_size.height())
        btn_shuffle.setStyleSheet("QPushButton {color: white; background-color: #00007f;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        btn_shuffle.clicked.connect(self._on_shuffle_clicked)
        # Clear numbers button
        btn_clear = QPushButton(frm)
        btn_clear.setIcon(QIcon(QPixmap(self.getv("online_topic_dls_clear_icon_path"))))
        btn_clear.setIconSize(QSize(20, 20))
        btn_clear.move(w - cell_size.height() - h_spacing, y)
        btn_clear.resize(cell_size.height(), cell_size.height())
        btn_clear.setStyleSheet("QPushButton {color: white; background-color: #00007f;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        btn_clear.clicked.connect(self._on_clear_clicked)
        # Selected numbers counter label
        lbl_selected = QLabel(frm)
        lbl_selected.setObjectName("info_label")
        lbl_selected.setText(f"{len(self.selected_numbers)}/{self.max_numbers}")
        lbl_selected.move(btn_shuffle.pos().x() + btn_shuffle.width() + h_spacing, y)
        lbl_selected.resize(w - btn_shuffle.width() - btn_clear.width() - h_spacing * 4, cell_size.height())
        lbl_selected.setAlignment(Qt.AlignCenter)
        font = lbl_selected.font()
        font.setPointSize(font_size)
        lbl_selected.setFont(font)
        lbl_selected.setStyleSheet("color: #ffff00; background-color: #004200;")

        y += cell_size.height() + v_spacing

        if self.max_numbers_pool < 7 or self.max_numbers_pool > 39:
            btn_clear.setEnabled(False)
            btn_shuffle.setEnabled(False)

        for i in range(1, 40):
            if self.max_numbers_pool < 7 or self.max_numbers_pool > 39:
                break
            if i > self.max_numbers_pool:
                continue

            frm_num = QFrame(frm)
            frm_num.setFrameShape(QFrame.NoFrame)
            frm_num.setFrameShadow(QFrame.Plain)
            frm_num.move(x, y)
            frm_num.resize(cell_size)

            lbl = QLabel(frm_num)
            lbl.setText(str(i))
            lbl.setAlignment(Qt.AlignCenter)
            font = lbl.font()
            font.setPointSize(font_size)
            lbl.setFont(font)
            lbl.resize(cell_size)
            lbl.setStyleSheet("color: #000000; background-color: #f0f0f0; border: 1px; border-style: solid; border-color: #d40000;")
            lbl.move(0, 0)

            lbl_pic = QLabel(frm_num)
            lbl_pic.setPixmap(QPixmap(self.getv("online_topic_dls_x_dark_icon_path")))
            lbl_pic.resize(cell_size.height()-2, cell_size.height()-2)
            lbl_pic.move(int(cell_size.width() / 2 - (cell_size.height() - 2) / 2) + 1,  1)
            lbl_pic.setScaledContents(True)
            lbl_pic.setStyleSheet("background-color: rgba(0,0,0,0); border: 0px;")
            lbl_pic.setVisible(False)
            lbl_pic.setObjectName(str(i))
            
            frm_num.enterEvent = lambda event, obj=lbl_pic: self._on_number_enter_event(event, obj)
            frm_num.leaveEvent = lambda event, obj=lbl_pic: self._on_number_leave_event(event, obj)
            frm_num.mousePressEvent = lambda event, obj=lbl_pic: self._on_number_clicked(event, obj)

            if i % 3 == 0:
                x = h_spacing
                y += cell_size.height() + v_spacing
            else:
                x += cell_size.width() + h_spacing
        
        frm.resize(w, cell_size.height() * 14 + v_spacing * 15)
        return frm
    
    def _on_clear_clicked(self):
        self.selected_numbers = []
        self._update_number_pick_apperance()

    def _on_shuffle_clicked(self):
        self.selected_numbers = random.sample(range(1, self.max_numbers_pool + 1), self.max_numbers)
        self._update_number_pick_apperance()

    def _on_number_clicked(self, event, lbl_pic: QLabel):
        if int(lbl_pic.objectName()) in self.selected_numbers:
            self.selected_numbers.remove(int(lbl_pic.objectName()))
            self._update_number_pick_apperance()
        else:
            if len(self.selected_numbers) < self.max_numbers:
                self.selected_numbers.append(int(lbl_pic.objectName()))
                self._update_number_pick_apperance()
            else:
                self.sound_max_numbers_reached.play()

    def _on_number_enter_event(self, event, lbl_pic: QLabel):
        QCoreApplication.processEvents()
        lbl_pic.setPixmap(QPixmap(self.getv("online_topic_dls_x_light_icon_path")))
        lbl_pic.setVisible(True)
    
    def _on_number_leave_event(self, event, lbl_pic: QLabel):
        self._update_number_pick_apperance()

    def _update_number_pick_apperance(self, number_list: list = None):
        if number_list is None:
            number_list = self.selected_numbers
        title_info = None
        for widget_main in self.frm_number_pick.children():
            if isinstance(widget_main, QLabel):
                if widget_main.objectName() == "info_label":
                    title_info = widget_main

            if isinstance(widget_main, QFrame):
                for widget in widget_main.children():
                    if not self._get_integer(widget.objectName()):
                        continue

                    if int(widget.objectName()) in number_list:
                        widget.setPixmap(QPixmap(self.getv("online_topic_dls_x_dark_icon_path")))
                        widget.setVisible(True)
                    else:
                        widget.setVisible(False)
        title_info.setText(f"{len(self.selected_numbers)}/{self.max_numbers}")

        if len(self.selected_numbers) == self.max_numbers:
            self.btn_add_komb.setEnabled(True)
        else:
            self.btn_add_komb.setEnabled(False)
        
        if len(self.selected_kombs) > 0:
            self.btn_save_komb.setEnabled(True)
        else:
            self.btn_save_komb.setEnabled(False)

        if len(self.selected_numbers) == 0:
            text = "Izaberi kombinaciju brojeva i klikni na dugme 'Dodaj...'."
        if len(self.selected_numbers) > 0:
            text = f"Izaberi još {self.max_numbers - len(self.selected_numbers)} brojeva i klikni na dugme 'Dodaj...'."
        if len(self.selected_numbers) == self.max_numbers:
            text = "Kombinacija je zavrsena. Klikni na dugme 'Dodaj...'."
        if len(self.selected_kombs) > 0:
            if len(self.selected_kombs) == 1:
                text = "Imate jednu izabranu kombinaciju. Klikni na dugme 'Snimi kombinaciju' ili na dugme 'Dodaj...' za dodavanje nove."
            elif len(self.selected_kombs) < 5:
                text = f"Imate {len(self.selected_kombs)} izabrane kombinacije. Klikni na dugme 'Snimi kombinaciju' ili na dugme 'Dodaj...' za dodavanje nove."
            else:
                text = f"Imate {len(self.selected_kombs)}. izabranih kombinacija. Klikni na dugme 'Snimi kombinaciju' ili na dugme 'Dodaj...' za dodavanje nove."
        
        self.lbl_info.setStyleSheet("color: rgb(170, 255, 127);")
        self.lbl_info.setText(text)

    def _update_list_of_kombs(self):
        # Delete old widgets
        for widget in self.frm_list_kombs.children():
            widget.deleteLater()

        # Populate frame with new widgets
        h_spacing = 50
        v_spacing = 10
        x = 0
        y = 0
        w = self.width() - 20 - self.frm_number_pick.width()
        self.frm_list_kombs.resize(w, y)
        frm = None
        for komb in self.selected_kombs:
            data = {
                "border": False,
                "hor_padding": 0,
                "ver_padding": 0,
                "hor_spacing": 10,
                "ver_spacing": 0,
                "numbers": komb,
                "number_width": 30,
                "number_height": 30,
                "feedback_click_function": self._number_komb_click
            }
            frm = Numbers(self.frm_list_kombs, self._stt, data)
            frm.move(x, y)
            frm.show()

            x += frm.width()
            if x + frm.width() + h_spacing > self.frm_list_kombs.width():
                x = 0
                y += frm.height() + v_spacing
            else:
                x += h_spacing
        
        if x > 0 and frm:
            y += frm.height() + v_spacing

        w = self.width() - 20 - self.frm_number_pick.width()
        self.frm_list_kombs.move(self.frm_number_pick.pos().x() + self.frm_number_pick.width() + 10, self.btn_save_komb.pos().y() + self.btn_save_komb.height() + 20)
        self.frm_list_kombs.resize(w, y)
        self.frm_list_kombs.show()

    def _number_komb_click(self, number):
        if number in self.selected_kombs:
            self.selected_kombs.remove(number)
        self._update_list_of_kombs()
        if self.selected_kombs:
            self.txt_count_sys_numbers.setDisabled(True)
        else:
            self.txt_count_sys_numbers.setDisabled(False)

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result

    def _create_frame(self):
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.NoFrame)
        self.resize(self.data["width"], self.height())

        if "add" in self.data["type"] or "edit" in self.data["type"]:
            self._create_add_frame_default()
            self._create_add_komb_frame()

            if "edit" in self.data["type"]:
                self._populate_item_data(self.data["item"])

        elif "view" in self.data["type"]:
            self._create_view_frame_default()

    def _create_view_frame_default(self):
        pass

    def _populate_item_data(self, item):
        self.txt_name.setText(item["name"])
        self.txt_desc.setText(item["desc"])
        self.selected_kombs = item["numbers"]
        self.txt_count_sys_numbers.setText(str(self.max_numbers_pool))
        self._update_number_pick_apperance()
        self._update_list_of_kombs()
        self.txt_count_sys_numbers.setDisabled(True)

    def _create_add_frame_default(self):
        # Frame Title
        self.lbl_title = QLabel(self)
        font = self.lbl_title.font()
        font.setPointSize(18)
        font.setBold(True)
        self.lbl_title.setFont(font)
        self.lbl_title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_title.setStyleSheet("color: rgb(0, 255, 0);")
        self.lbl_title.move(10, 10)
        self.lbl_title.resize(self.data["width"] - 20, 31)

        # Item name
        self.lbl_name = QLabel(self)
        font = self.lbl_name.font()
        font.setPointSize(14)
        self.lbl_name.setFont(font)
        self.lbl_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_name.setText("Naziv:")
        self.lbl_name.setStyleSheet("color: rgb(207, 207, 207);")
        self.lbl_name.setAlignment(Qt.AlignRight)
        self.lbl_name.resize(50, 22)
        self.lbl_name.move(10, 50)

        self.txt_name = QTextEdit(self)
        self.txt_name.setFont(font)
        self.txt_name.setPlaceholderText("Naziv...")
        self.txt_name.setStyleSheet("QTextEdit {background-color: rgb(0, 126, 0); color: rgb(255, 255, 0);} QTextEdit:hover {background-color: rgb(0, 163, 0);}")
        self.txt_name.move(60, 50)
        self.txt_name.resize(int((self.data["width"] - 150) / 2) , 70)

        # Item description
        self.lbl_desc = QLabel(self)
        font = self.lbl_desc.font()
        font.setPointSize(14)
        self.lbl_desc.setFont(font)
        self.lbl_desc.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_desc.setText("Opis:")
        self.lbl_desc.setStyleSheet("color: rgb(207, 207, 207);")
        self.lbl_desc.setAlignment(Qt.AlignRight)
        self.lbl_desc.resize(50, 22)
        self.lbl_desc.move(self.txt_name.pos().x() + self.txt_name.width() + 10, 50)

        self.txt_desc = QTextEdit(self)
        self.txt_desc.setFont(font)
        self.txt_desc.setPlaceholderText("Opis...")
        self.txt_desc.setStyleSheet("QTextEdit {background-color: rgb(0, 126, 0); color: rgb(255, 255, 0);} QTextEdit:hover {background-color: rgb(0, 163, 0);}")
        self.txt_desc.resize(int((self.data["width"] - 150) / 2) , 70)
        self.txt_desc.move(self.lbl_desc.pos().x() + self.lbl_desc.width() + 10, 50)


        # Info label
        self.lbl_info = QLabel(self)
        font = self.lbl_info.font()
        font.setPointSize(14)
        self.lbl_info.setFont(font)
        self.lbl_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_info.setStyleSheet("color: #aaff7f;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        self.lbl_info.resize(self.data["width"] - 20, 23)
        self.lbl_info.move(10, 130)

    def _create_add_komb_frame(self):
        # Set default labels text
        if "komb" in self.data["type"]:
            self.lbl_title.setText("LOTO kombinacija:")
        elif "sys" in self.data["type"]:
            self.lbl_title.setText("LOTO sistem:")

        self.lbl_info.setText("Izaberi kombinaciju brojeva i klikni na dugme 'Dodaj...'.")

        # Create number pick frame
        self.frm_number_pick = self._number_pick_frame()
        self.frm_number_pick.move(10, 165)
        self.frm_number_pick.show()

        # Create 'Dodaj kombinaciju' button
        self.btn_add_komb = QPushButton(self)
        self.btn_add_komb.setText("Dodaj kombinaciju")
        self.btn_add_komb.setStyleSheet("QPushButton {color: rgb(0, 0, 83); background-color: rgb(170, 255, 127); border-radius: 15px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(0, 67, 0), stop:1 rgb(0, 161, 0)); color: rgb(255, 255, 0)}")
        font = self.btn_add_komb.font()
        font.setPointSize(14)
        self.btn_add_komb.setFont(font)
        self.btn_add_komb.resize(250, 40)
        self.btn_add_komb.setIcon(QIcon(QPixmap(self.getv("add_icon_path"))))
        self.btn_add_komb.setIconSize(QSize(30, 30))
        self.btn_add_komb.move(self.frm_number_pick.pos().x() + self.frm_number_pick.width() + 10, self.frm_number_pick.pos().y())
        self.btn_add_komb.clicked.connect(self._add_komb_btn_add_komb_clicked)
        self.btn_add_komb.setDisabled(True)

        # Create 'Snimi kombinaciju' button
        self.btn_save_komb = QPushButton(self)
        if self.data["type"] == "add_komb":
            self.btn_save_komb.setText("Snimi kombinaciju")
        elif self.data["type"] == "add_sys":
            self.btn_save_komb.setText("Snimi sistem")
        elif self.data["type"] == "edit_komb":
            self.btn_save_komb.setText("Ažuriraj kombinaciju")
        elif self.data["type"] == "edit_sys":
            self.btn_save_komb.setText("Ažuriraj sistem")
        
        self.btn_save_komb.setStyleSheet("QPushButton {background-color: #140b98; color: white; border-radius: 10px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        self.btn_save_komb.setFont(font)
        self.btn_save_komb.resize(250, 40)
        self.btn_save_komb.setIcon(QIcon(QPixmap(self.getv("save_red_disk_icon_path"))))
        self.btn_save_komb.setIconSize(QSize(30, 30))
        self.btn_save_komb.move(self.btn_add_komb.pos().x(), self.btn_add_komb.pos().y() + self.btn_add_komb.height() + 10)
        self.btn_save_komb.clicked.connect(self._add_komb_btn_save_komb_clicked)
        self.btn_save_komb.setDisabled(True)

        self.lbl_count_sys_numbers = QLabel(self)
        self.lbl_count_sys_numbers.setFont(font)
        self.lbl_count_sys_numbers.setText("Brojeva u sistemu:")
        self.lbl_count_sys_numbers.setStyleSheet("color: #dfdfdf;")
        self.lbl_count_sys_numbers.adjustSize()
        self.lbl_count_sys_numbers.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_count_sys_numbers.move(self.btn_save_komb.pos().x() + self.btn_save_komb.width() + 10, self.frm_number_pick.pos().y())

        self.txt_count_sys_numbers = QLineEdit(self)
        font.setPointSize(40)
        font.setBold(True)
        self.txt_count_sys_numbers.setFont(font)
        self.txt_count_sys_numbers.setText("0")
        self.txt_count_sys_numbers.setStyleSheet("QLineEdit {background-color: rgb(0, 126, 0); color: rgb(255, 255, 0);} QLineEdit:hover {background-color: rgb(0, 163, 0);} QLineEdit:disabled {color: #aa0000;}")
        self.txt_count_sys_numbers.setAlignment(Qt.AlignCenter)
        self.txt_count_sys_numbers.move(self.lbl_count_sys_numbers.pos().x() + 50, self.lbl_count_sys_numbers.pos().y() + self.lbl_count_sys_numbers.height() + 5)
        self.txt_count_sys_numbers.resize(90, 70)
        self.txt_count_sys_numbers.textChanged.connect(self._txt_count_sys_numbers_text_changed)

        if self.data["item_type"] == "komb":
            self.lbl_count_sys_numbers.setVisible(False)
            self.txt_count_sys_numbers.setVisible(False)
        
        # Create frame for showing list of kombinations
        self.frm_list_kombs = QFrame(self)
        self.frm_list_kombs.setFrameShape(QFrame.NoFrame)
        self.frm_list_kombs.setFrameShadow(QFrame.Plain)
        self._update_list_of_kombs()


        self.resize(self.width(), max(self.frm_number_pick.pos().y() + self.frm_number_pick.height() + 10, self.frm_list_kombs.pos().y() + self.frm_list_kombs.height() + 10))

    def _txt_count_sys_numbers_text_changed(self):
        value = self._get_integer(self.txt_count_sys_numbers.text())
        if value is None or value < 7 or value > 39:
            if value > 39:
                value = 39
            else:
                value = 7

        pos = self.frm_number_pick.pos()
        self.frm_number_pick.deleteLater()
        self.max_numbers_pool = value
        self.frm_number_pick = self._number_pick_frame()
        self.frm_number_pick.move(pos)
        self.frm_number_pick.show()

    def _add_komb_btn_add_komb_clicked(self):
        if len(self.selected_numbers) < self.max_numbers:
            self.lbl_info.setStyleSheet("color: #aa0000;")
            self.lbl_info.setText(f"Izaberite još {self.max_numbers - len(self.selected_numbers)} brojeva i kliknite na dugme 'Dodaj...'.")
            self.sound_max_numbers_reached.play()
            return
        
        self.selected_numbers.sort()
        if self.selected_numbers in self.selected_kombs:
            self.lbl_info.setStyleSheet("color: #aa0000;")
            self.lbl_info.setText("Već ste izabrali ovu kombinaciju!")
            self.sound_max_numbers_reached.play()
            return
        
        self.selected_kombs.append(list(self.selected_numbers))
        self.selected_numbers = []
        self._update_number_pick_apperance()
        self._update_list_of_kombs()
        self.txt_count_sys_numbers.setDisabled(True)

    def _add_komb_btn_save_komb_clicked(self):
        name = self.txt_name.toPlainText().strip()
        if not self.selected_kombs:
            self.lbl_info.setStyleSheet("color: #aa0000;")
            self.lbl_info.setText("Nemate izabranih kombinacija!")
            self.sound_max_numbers_reached.play()
            return
        if not name:
            self.lbl_info.setStyleSheet("color: #aa0000;")
            self.lbl_info.setText("Unesite naziv kombinacije!")
            self.sound_max_numbers_reached.play()
            self.txt_name.setFocus()
            return
        if name in self.data["reserved_names"]:
            self.lbl_info.setStyleSheet("color: #aa0000;")
            self.lbl_info.setText(f"Kombinacija '{name}' je zauzeta!")
            self.sound_max_numbers_reached.play()
            self.txt_name.setFocus()
            self.txt_name.selectAll()
            return
    
        item = self.data["item"]
        item["name"] = name
        item["desc"] = self.txt_desc.toPlainText().strip()
        item["type"] = self.data["item_type"]
        item["is_enabled"] = False
        item["can_be_removed"] = True
        item["numbers"] = self.selected_kombs
        item["sys_numbers"] = self.max_numbers_pool
        item["sys_shema"] = self.selected_kombs

        self.data["feedback_function"](item)
        self.hide()
        

class DLS(AbstractTopic):
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
        uic.loadUi(self.getv("online_topic_dls_ui_file_path"), self)

        # Define variables
        self.name = "dls"
        self.topic_info_dict["name"] = self.name
        self.parent_widget = parent_widget
        self.title = self.getl("online_topic_dls_title")
        self.topic_info_dict["title"] = self.title
        self.icon_path = self.getv("online_topic_dls_icon_path")
        self.icon_pixmap = QPixmap(self.icon_path)

        self.settings: dict = self._get_user_settings()
        self.base_url = "https://www.lutrija.rs"

        self.frm_loto_komb_work = None

        self._define_widgets()

        self._populate_widgets()

        # Connect events with slots
        self.lbl_title_pic.mouseDoubleClickEvent = self.lbl_title_pic_mouseDoubleClickEvent
        self.lbl_loto_btn.mousePressEvent = self.lbl_loto_btn_clicked
        self.lbl_bingo_btn.mousePressEvent = self.lbl_bingo_btn_clicked
        self.lbl_loto_archive_btn.mousePressEvent = self.lbl_loto_archive_btn_clicked
        self.btn_loto_archive_show.clicked.connect(self.btn_loto_archive_show_clicked)
        self.lst_loto_archive_years.currentRowChanged.connect(self.lst_loto_archive_years_current_row_changed)
        self.btn_loto_archive_search_download.clicked.connect(self.btn_loto_archive_search_download_clicked)
        self.btn_bingo_show_numbers.clicked.connect(self.btn_bingo_show_numbers_clicked)
        self.btn_bingo_plus_show_numbers.clicked.connect(self.btn_bingo_plus_show_numbers_clicked)
        self.frm_bingo_numbers.leaveEvent = self.frm_bingo_numbers_leaveEvent
        self.frm_bingo_plus_numbers.leaveEvent = self.frm_bingo_plus_numbers_leaveEvent
        self.btn_bingo_archive.clicked.connect(self.btn_bingo_archive_clicked)
        self.btn_bingo_archive_show.clicked.connect(self.btn_bingo_archive_show_clicked)
        self.lbl_loto_komb_btn.mousePressEvent = self.lbl_loto_komb_btn_clicked
        self.btn_loto_komb_add_komb.clicked.connect(self.btn_loto_komb_add_komb_clicked)
        self.btn_loto_komb_add_sys.clicked.connect(self.btn_loto_komb_add_sys_clicked)

    def btn_loto_komb_add_sys_clicked(self):
        data = {
            "width": self.contentsRect().width() - 300,
            "type": "add_sys",
            "item_type": "sys",
            "item": self._empty_loto_system_dict(),
            "feedback_function": self.frm_loto_komb_work_feedback_function,
            "reserved_names": [x["name"] for x in self.settings["loto"]["system"]]
        }
        if self.frm_loto_komb_work:
            self.frm_loto_komb_work.deleteLater()
        self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data)
        self.frm_loto_komb_work.move(290, 140)
        self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
        self.frm_loto_komb_work.show()
        self.resize_me()

    def btn_loto_komb_add_komb_clicked(self):
        data = {
            "width": self.contentsRect().width() - 300,
            "type": "add_komb",
            "item_type": "komb",
            "item": self._empty_loto_system_dict(),
            "feedback_function": self.frm_loto_komb_work_feedback_function,
            "reserved_names": [x["name"] for x in self.settings["loto"]["system"]]
        }
        if self.frm_loto_komb_work:
            self.frm_loto_komb_work.deleteLater()
        self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data)
        self.frm_loto_komb_work.move(290, 140)
        self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
        self.frm_loto_komb_work.show()
        self.resize_me()

    def frm_loto_komb_work_feedback_function(self, data: dict):
        for idx, item in enumerate(self.settings["loto"]["system"]):
            if item["name"] == data["name"]:
                self.settings["loto"]["system"][idx] = data
                break
        else:
            self.settings["loto"]["system"].append(data)

        self.frm_loto_komb_work.deleteLater()
        self.frm_loto_komb_work = None
        self._update_user_settings()
        self._update_frm_loto_komb_apperance()

    def lbl_loto_komb_btn_clicked(self, e: QMouseEvent):
        self._hide_all_frames()
        self.frm_loto_komb.setVisible(True)
        self._update_frm_loto_komb_apperance()

    def _update_frm_loto_komb_apperance(self):
        # Delete old child frames
        protected_widgets = [
            self.lbl_loto_komb_komb_title_pic,
            self.lbl_loto_komb_komb_title,
            self.line_loto_komb_komb,
            self.lbl_loto_komb_sys_title_pic,
            self.lbl_loto_komb_sys_title,
            self.line_loto_komb_sys
        ]
        for item in self.frm_loto_komb_komb.children():
            if item not in protected_widgets:
                item.deleteLater()
        for item in self.frm_loto_komb_sys.children():
            if item not in protected_widgets:
                item.deleteLater()

        # Create new child frames for komb
        y = 200
        for item in self.settings["loto"]["system"]:
            if item["type"] == "komb":
                frm = self._create_komb_or_sys_frame(self.frm_loto_komb_komb, item)
                frm.move(0, y)
                frm.show()
                y += frm.height() + 10
        self.frm_loto_komb_komb.resize(250, y)

        # Create new child frames for sys
        y = 200
        for item in self.settings["loto"]["system"]:
            if item["type"] == "sys":
                frm = self._create_komb_or_sys_frame(self.frm_loto_komb_sys, item)
                frm.move(0, y)
                frm.show()
                y += frm.height() + 10
        self.frm_loto_komb_sys.resize(250, y)
        self.frm_loto_komb_sys.move(10, self.frm_loto_komb_komb.pos().y() + self.frm_loto_komb_komb.height() + 20)

        self._set_frm_loto_komb_sys_height()

    def _set_frm_loto_komb_sys_height(self):
        if self.frm_loto_komb_work:
            self.frm_loto_komb.resize(self.frm_loto_komb.width(), max(self.frm_loto_komb_work.height() + self.frm_loto_komb_work.pos().y() + 10, self.frm_loto_komb_sys.pos().y() + self.frm_loto_komb_sys.height() + 10))
        else:
            self.frm_loto_komb.resize(self.frm_loto_komb.width(), self.frm_loto_komb_sys.pos().y() + self.frm_loto_komb_sys.height() + 10)
        self.resize_me()

    def _create_komb_or_sys_frame(self, parent_widget: QWidget, data: dict) -> QFrame:
        w = 250
        # Frame
        frm = QFrame(parent_widget)
        frm.setFrameShape(QFrame.NoFrame)
        frm.setFrameShadow(QFrame.Plain)
        frm.setStyleSheet("QFrame {color: #000000; border-top: 1px solid; border-bottom: 1px solid;} QFrame:hover {background-color: #2f2f00;}")

        # Enabled
        lbl_enabled = QLabel(frm)
        lbl_enabled.setAlignment(Qt.AlignCenter)
        if data["is_enabled"]:
            lbl_enabled.setPixmap(QPixmap(self.getv("checked_icon_path")))
        else:
            lbl_enabled.setPixmap(QPixmap(self.getv("not_checked_icon_path")))
        lbl_enabled.setScaledContents(True)
        lbl_enabled.setCursor(Qt.PointingHandCursor)
        lbl_enabled.setStyleSheet("QLabel {background-color: rgba(0, 0, 0, 0); border: 0px;} QLabel:hover {background-color: rgb(101, 101, 152);}")
        lbl_enabled.resize(25, 25)
        lbl_enabled.move(5, 5)
        lbl_enabled.mousePressEvent = lambda e: self._on_komb_sys_item_click("enabled", data, lbl_enabled)
        
        # Title
        name = data["name"]
        lbl_title = QLabel(frm)
        lbl_title.setText(name)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet("QLabel {color: rgb(0, 255, 0); background-color: rgb(0, 0, 127); border-radius: 8px;} QLabel:hover {color: rgb(255, 255, 0); background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        font = lbl_title.font()
        font.setPointSize(14)
        lbl_title.setFont(font)
        lbl_title.setFixedWidth(w - (lbl_enabled.pos().x() + lbl_enabled.width() + 10))
        lbl_title.adjustSize()
        lbl_title.move(lbl_enabled.pos().x() + lbl_enabled.width() + 10, 5)
        lbl_title.setCursor(Qt.PointingHandCursor)
        lbl_title.mousePressEvent = lambda e: self._on_komb_sys_item_click("click", data, lbl_title)

        # Button remove
        btn_remove = QPushButton(frm)
        btn_remove.setText("Obriši")
        btn_remove.setStyleSheet("QPushButton {color: #ff0000; background-color: rgb(170, 255, 127);} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(0, 67, 0), stop:1 rgb(0, 161, 0)); color: rgb(255, 255, 0)}")
        btn_remove.setFixedSize(80, 20)
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setIcon(QIcon(QPixmap(self.getv("remove_icon_path"))))
        btn_remove.setIconSize(QSize(16, 16))
        btn_remove.move(w - btn_remove.width() - 5, lbl_title.pos().y() + lbl_title.height() + 5)
        btn_remove.clicked.connect(lambda: self._on_komb_sys_item_click("remove", data, btn_remove))
        if data["can_be_removed"]:
            btn_remove.setDisabled(False)
        else:
            btn_remove.setDisabled(True)

        # Button edit
        btn_edit = QPushButton(frm)
        btn_edit.setText("Izmeni")
        btn_edit.setStyleSheet("QPushButton {color: rgb(0, 0, 83); background-color: rgb(170, 255, 127);} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(0, 67, 0), stop:1 rgb(0, 161, 0)); color: rgb(255, 255, 0)}")
        btn_edit.setFixedSize(80, 20)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setIcon(QIcon(QPixmap(self.getv("edit_icon_path"))))
        btn_edit.setIconSize(QSize(16, 16))
        btn_edit.move(w - (btn_edit.width() + 5 + btn_remove.width() + 5), lbl_title.pos().y() + lbl_title.height() + 5)
        btn_edit.clicked.connect(lambda: self._on_komb_sys_item_click("edit", data, btn_edit))

        frm.resize(w, btn_edit.pos().y() + btn_edit.height() + 5)
        return frm

    def _on_komb_sys_item_click(self, action: str, data: dict, widget: QWidget):
        if action == "remove":
            if not self._ask_for_delete_confirmation(data):
                return
            for item in self.settings["loto"]["system"]:
                if item["name"] == data["name"]:
                    self.settings["loto"]["system"].remove(item)
                    if self.frm_loto_komb_work:
                        if data["name"] in self.frm_loto_komb_work.data["reserved_names"]:
                            self.frm_loto_komb_work.data["reserved_names"].remove(data["name"])
                    break
            self._update_frm_loto_komb_apperance()
        elif action == "edit":
            data = {
                "width": self.contentsRect().width() - 300,
                "type": f"edit_{data['type']}",
                "item_type": data["type"],
                "item": data,
                "feedback_function": self.frm_loto_komb_work_feedback_function,
                "reserved_names": [x["name"] for x in self.settings["loto"]["system"] if x["name"] != data["name"]]
            }
            if self.frm_loto_komb_work:
                self.frm_loto_komb_work.deleteLater()
            self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data)
            self.frm_loto_komb_work.move(290, 140)
            self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
            self.frm_loto_komb_work.show()
            self.resize_me()
        elif action == "click":
            data = {
                "width": self.contentsRect().width() - 300,
                "type": f"view_{data['type']}",
                "item_type": data["type"],
                "item": data,
                "feedback_function": self.frm_loto_komb_work_feedback_function,
                "reserved_names": [x["name"] for x in self.settings["loto"]["system"] if x["name"] != data["name"]]
            }
            if self.frm_loto_komb_work:
                self.frm_loto_komb_work.deleteLater()
            self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data)
            self.frm_loto_komb_work.move(290, 140)
            self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
            self.frm_loto_komb_work.show()
            self.resize_me()
        elif action == "enabled":
            data["is_enabled"] = not data["is_enabled"]
            if data["is_enabled"]:
                widget.setPixmap(QPixmap(self.getv("checked_icon_path")))
            else:
                widget.setPixmap(QPixmap(self.getv("not_checked_icon_path")))

    def _ask_for_delete_confirmation(self, item: dict) -> bool:
        item_title_type = "kombinacije" if item["type"] == "komb" else "sistema"
        item_text_type = "ovu kombinaciju" if item["type"] == "komb" else "ovaj sistem"
        data = {
            "title": f"Brisanje {item_title_type}",
            "text": f"Jeste li sigurni da želite obrisati {item_text_type} ?",
            "icon_path": self.getv("messagebox_question_icon_path"),
            "buttons": [
                [1, self.getl("btn_yes"), "", None, True],
                [2, self.getl("btn_no"), "", None, True],
                [3, self.getl("btn_cancel"), "", None, True]

            ]
        }
        utility_cls.MessageQuestion(self._stt, self, data, app_modal=True)
        result = data["result"]
        if result == 1:
            return True
        return False

    def frm_bingo_plus_numbers_leaveEvent(self, event):
        self.frm_bingo_plus_numbers.setVisible(False)

    def frm_bingo_numbers_leaveEvent(self, event):
        self.frm_bingo_numbers.setVisible(False)

    def btn_bingo_plus_show_numbers_clicked(self):
        self.frm_bingo_plus_numbers.setVisible(not self.frm_bingo_plus_numbers.isVisible())

    def btn_bingo_show_numbers_clicked(self):
        self.frm_bingo_numbers.setVisible(not self.frm_bingo_numbers.isVisible())

    def btn_loto_archive_search_download_clicked(self):
        self.stop_loading = False
        attempt = 0
        rnd = "1"
        year = self.lbl_loto_archive_search_year.text().strip()
        if not self._get_integer(year):
            return
        
        while True:
            if self.stop_loading:
                break
            
            if rnd in [x["round"] for x in self.settings["loto"]["archive"] if x["year"] == year]:
                rnd = str(int(rnd) + 1)
                continue

            print (year, rnd)
            result = self._load_loto_frame(year_round=(year, rnd), auto_show_frame=False)
            self._update_loto_archive_label_text(year)

            if result is None:
                attempt += 1
            else:
                attempt = 0
            if attempt >= 3:
                break

            rnd = str(int(rnd) + 1)
            self._update_user_settings()
        
        self.stop_loading = False
        if attempt >= 3:
            if year not in self.settings["completed_years"]:
                self.settings["completed_years"].append(year)
            self._update_loto_archive_label_text(year)
            self._update_user_settings()

    def lst_loto_archive_years_current_row_changed(self, row: int):
        if row >= 0:
            year = self.lst_loto_archive_years.item(row).text()
            self.lbl_loto_archive_search_year.setText(year)
            if year in self.settings["completed_years"]:
                self.btn_loto_archive_search_download.setDisabled(True)
            else:
                self.btn_loto_archive_search_download.setDisabled(False)
            self._update_loto_archive_label_text(year)
            self.frm_loto_archive_search.setVisible(True)

    def _update_loto_archive_label_text(self, year: str):
        total_rounds = 0
        for item in self.settings["loto"]["archive"]:
            if item["year"] == year:
                total_rounds += 1
        
        if year in self.settings["completed_years"]:
            text = "Završeno (Ukupno #--1 kola.)"
            text_to_html = utility_cls.TextToHTML(text)
            text_to_html.general_rule.fg_color = "#00c760"
            rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(total_rounds), fg_color="#00ff7f")
            text_to_html.add_rule(rule)
            text = text_to_html.get_html()
        else:
            text = "Preuzeto #--1 kola."
            text_to_html = utility_cls.TextToHTML(text)
            text_to_html.general_rule.fg_color = "#55ffff"
            rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(total_rounds), fg_color="#aaffff")
            text_to_html.add_rule(rule)
            text = text_to_html.get_html()

        self.lbl_loto_archive_search_completed.setText(text)

        text_to_html = utility_cls.TextToHTML()
        text = ""
        count = 1
        for item in self.settings["loto"]["archive"]:
            if item["year"] == year:
                text += "Izveštaj za "
                
                text_id = "#" + "-" * (6 - len(str(count))) + str(count)
                text += text_id
                rule = utility_cls.TextToHtmlRule(text=text_id, replace_with=item["round"], fg_color="#ff0000")
                text_to_html.add_rule(rule)
                count += 1

                text += " kolo - datum izvlačenja "
                
                text_id = "#" + "-" * (6 - len(str(count))) + str(count)
                rule = utility_cls.TextToHtmlRule(text=text_id, replace_with=item["date"], fg_color="#ff0000")
                text_to_html.add_rule(rule)
                text += text_id
                count += 1

                text_id = "#" + "-" * (6 - len(str(count))) + str(count)
                text += f"  ({text_id})\n"
                rule = utility_cls.TextToHtmlRule(text=text_id, replace_with="Prikaži", fg_color="#aaffff", link_href=f"{year},{item['round']},show")
                text_to_html.add_rule(rule)
                count += 1

        text_to_html.set_text(text)
        text = text_to_html.get_html()
        self.lbl_loto_archive_search_results.setText(text)
        self.lbl_loto_archive_search_results.setFixedWidth(self.frm_loto_archive_search.width() - 20)
        self.lbl_loto_archive_search_results.adjustSize()
        self.resize_me()

    def _on_loto_archive_search_results_link_activated(self, link: str):
        year, rnd, action = link.split(",")
        year_round = tuple([year, rnd])

        if action == "show":
            self._load_loto_frame(year_round=year_round)

    def lbl_title_pic_mouseDoubleClickEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            webbrowser.open_new_tab(self.base_url)

    def _populate_widgets(self):
        # Populate Loto Archive list
        self.lst_loto_archive_years.clear()
        if not self.settings["current_loto"]["is_loaded"]:
            data = self._get_loto_data()
            if data["is_loaded"]:
                self.settings["current_loto"] = data
            else:
                return
        
        for year in range(2012, int(self.settings["current_loto"]["year"]) + 1):
            item = QListWidgetItem()
            item.setText(f"{year}")
            item.setTextAlignment(Qt.AlignCenter)
            self.lst_loto_archive_years.insertItem(0, item)

        # Calculate height of lst_loto_archive_years
        h = 30
        if self.lst_loto_archive_years.count():
            h = self.lst_loto_archive_years.count() * self.lst_loto_archive_years.sizeHintForRow(0)
            h += self.lst_loto_archive_years.frameWidth() * 2

        self.lst_loto_archive_years.resize(180, h)
        self.frm_loto_archive.resize(self.frm_loto_archive.width(), self.lst_loto_archive_years.height() + 170)

    def btn_loto_archive_show_clicked(self):
        year = self._get_integer(self.txt_loto_archive_year.text().strip())
        rnd = self._get_integer(self.txt_loto_archive_round.text().strip())
        if not year or not rnd:
            return
        
        year_round = tuple([str(year), str(rnd)])

        self._load_loto_frame(year_round=year_round)
        self._update_user_settings()
        self._update_loto_archive_label_text(self.lbl_loto_archive_search_year.text())

    def lbl_loto_btn_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._load_loto_frame()

    def lbl_bingo_btn_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._hide_all_frames()
            self._populate_bingo_frame(self.settings["current_bingo"])
            self.frm_bingo.setVisible(True)

    def load_topic(self):
        self._load_loto_frame()
        return super().load_topic()

    def _hide_all_frames(self):
        self.frm_loto.setVisible(False)
        self.frm_bingo.setVisible(False)
        self.frm_loto_archive.setVisible(False)
        self.frm_bingo_archive.setVisible(False)
        self.frm_loto_komb.setVisible(False)

    def lbl_loto_archive_btn_clicked(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._load_loto_archive_frame()

    def _load_loto_archive_frame(self):
        self._hide_all_frames()
        self.frm_loto_archive.setVisible(True)
        self.frm_loto_archive.raise_()
        self.resize_me()

    def _load_loto_frame(self, year_round: tuple = None, auto_show_frame: bool = True) -> bool:
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_dls") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.setDisabled(True)

        QCoreApplication.processEvents()

        if auto_show_frame:
            self._hide_all_frames()

        if year_round:
            data = self._find_loto_archive(year_round)
            if not data or not data["is_loaded"]:
                data = self._get_loto_data(year_round=year_round)
            if not data["is_loaded"]:
                self.topic_info_dict["working"] = False
                self.topic_info_dict["msg"] = ""
                self.signal_topic_info_emit(self.name, self.topic_info_dict)
                self.setDisabled(False)
                return None
        else:
            if self.settings["current_loto"]["is_loaded"]:
                data = self.settings["current_loto"]
            else:
                data = self._get_loto_data()
                if not data["is_loaded"]:
                    self.topic_info_dict["working"] = False
                    self.topic_info_dict["msg"] = ""
                    self.signal_topic_info_emit(self.name, self.topic_info_dict)
                    self.setDisabled(False)
                    return False
        
        if year_round:
            self._update_loto_archive(data)
        else:
            self.lbl_loto_btn.setText(f'Loto - {data["date"]}')
            self.settings["current_loto"] = data
            
        if auto_show_frame:
            self._populate_loto_frame_widgets(data)

            self.frm_loto.setVisible(True)
            self.frm_loto.raise_()
            self.resize_me()

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.setDisabled(False)

        return True

    def _update_loto_archive(self, data: dict):
        for idx, item in enumerate(self.settings["loto"]["archive"]):
            if item["year"] == data["year"] and item["round"] == data["round"]:
                self.settings["loto"]["archive"][idx] = data
                break
        else:
            self.settings["loto"]["archive"].append(data)

        self.settings["loto"]["archive"] = sorted(self.settings["loto"]["archive"], key=lambda k: k["year"]+" "*(4-len(k["round"])) + k["round"])

    def _find_loto_archive(self, year_round: tuple) -> dict:
        for item in self.settings["loto"]["archive"]:
            if item["year"] == year_round[0] and item["round"] == year_round[1]:
                return item
        return None

    def _populate_loto_frame_widgets(self, data: dict):
        # Populate the Loto frame based on the dictionary data from the self._empty_loto_dict function
        self.lbl_loto_title_info.setText(data["lbl_loto_title_info"])
        if len(data["loto_numbers"]) == 7:
            self.lbl_loto_n1_num.setText(data["loto_numbers"][0])
            self.lbl_loto_n2_num.setText(data["loto_numbers"][1])
            self.lbl_loto_n3_num.setText(data["loto_numbers"][2])
            self.lbl_loto_n4_num.setText(data["loto_numbers"][3])
            self.lbl_loto_n5_num.setText(data["loto_numbers"][4])
            self.lbl_loto_n6_num.setText(data["loto_numbers"][5])
            self.lbl_loto_n7_num.setText(data["loto_numbers"][6])
        else:
            self.lbl_loto_n1_num.setText("X")
            self.lbl_loto_n2_num.setText("X")
            self.lbl_loto_n3_num.setText("X")
            self.lbl_loto_n4_num.setText("X")
            self.lbl_loto_n5_num.setText("X")
            self.lbl_loto_n6_num.setText("X")
            self.lbl_loto_n7_num.setText("X")
        self.lbl_loto_expected.setText(data["lbl_loto_expected"])
        self.lbl_loto_total.setText(data["lbl_loto_total"])
        self.lbl_loto_fond.setText(data["lbl_loto_fond"])
        self.lbl_loto_fond7.setText(data["lbl_loto_fond7"])
        self.lbl_loto_price.setText(data["lbl_loto_price"])
        self.lbl_loto_komb_num.setText(data["lbl_loto_komb_num"])
        self.lbl_loto_prize_7_num.setText(data["lbl_loto_prize_7_num"])
        self.lbl_loto_prize_6_num.setText(data["lbl_loto_prize_6_num"])
        self.lbl_loto_prize_5_num.setText(data["lbl_loto_prize_5_num"])
        self.lbl_loto_prize_4_num.setText(data["lbl_loto_prize_4_num"])
        self.lbl_loto_prize_3_num.setText(data["lbl_loto_prize_3_num"])
        self.lbl_loto_prize_7_amount.setText(data["lbl_loto_prize_7_amount"])
        self.lbl_loto_prize_6_amount.setText(data["lbl_loto_prize_6_amount"])
        self.lbl_loto_prize_5_amount.setText(data["lbl_loto_prize_5_amount"])
        self.lbl_loto_prize_4_amount.setText(data["lbl_loto_prize_4_amount"])
        self.lbl_loto_prize_3_amount.setText(data["lbl_loto_prize_3_amount"])

        if len(data["loto_plus_numbers"]) == 7:
            self.lbl_loto_plus_n1_num.setText(data["loto_plus_numbers"][0])
            self.lbl_loto_plus_n2_num.setText(data["loto_plus_numbers"][1])
            self.lbl_loto_plus_n3_num.setText(data["loto_plus_numbers"][2])
            self.lbl_loto_plus_n4_num.setText(data["loto_plus_numbers"][3])
            self.lbl_loto_plus_n5_num.setText(data["loto_plus_numbers"][4])
            self.lbl_loto_plus_n6_num.setText(data["loto_plus_numbers"][5])
            self.lbl_loto_plus_n7_num.setText(data["loto_plus_numbers"][6])
        else:
            self.lbl_loto_plus_n1_num.setText("X")
            self.lbl_loto_plus_n2_num.setText("X")
            self.lbl_loto_plus_n3_num.setText("X")
            self.lbl_loto_plus_n4_num.setText("X")
            self.lbl_loto_plus_n5_num.setText("X")
            self.lbl_loto_plus_n6_num.setText("X")
            self.lbl_loto_plus_n7_num.setText("X")
        self.lbl_loto_plus_expected.setText(data["lbl_loto_plus_expected"])
        self.lbl_loto_plus_total.setText(data["lbl_loto_plus_total"])
        self.lbl_loto_plus_fond.setText(data["lbl_loto_plus_fond"])
        self.lbl_loto_plus_price.setText(data["lbl_loto_plus_price"])
        self.lbl_loto_plus_winers.setText(data["lbl_loto_plus_winers"])
        self.lbl_loto_plus_amount.setText(data["lbl_loto_plus_amount"])

        if len(data["dzoker_numbers"]) == 6:
            self.lbl_dzoker_n1_num.setText(data["dzoker_numbers"][0])
            self.lbl_dzoker_n2_num.setText(data["dzoker_numbers"][1])
            self.lbl_dzoker_n3_num.setText(data["dzoker_numbers"][2])
            self.lbl_dzoker_n4_num.setText(data["dzoker_numbers"][3])
            self.lbl_dzoker_n5_num.setText(data["dzoker_numbers"][4])
            self.lbl_dzoker_n6_num.setText(data["dzoker_numbers"][5])
        else:
            self.lbl_dzoker_n1_num.setText("X")
            self.lbl_dzoker_n2_num.setText("X")
            self.lbl_dzoker_n3_num.setText("X")
            self.lbl_dzoker_n4_num.setText("X")
            self.lbl_dzoker_n5_num.setText("X")
            self.lbl_dzoker_n6_num.setText("X")
        self.lbl_dzoker_expected.setText(data["lbl_dzoker_expected"])
        self.lbl_dzoker_total.setText(data["lbl_dzoker_total"])
        self.lbl_dzoker_fond.setText(data["lbl_dzoker_fond"])
        self.lbl_dzoker_price.setText(data["lbl_dzoker_price"])
        self.lbl_dzoker_winers.setText(data["lbl_dzoker_winers"])
        self.lbl_dzoker_amount.setText(data["lbl_dzoker_amount"])

    def _get_loto_data(self, year_round: tuple = None) -> dict:
        result = self._empty_loto_dict()

        if year_round is None:
            url = "https://www.lutrija.rs/Results"
        else:
            url = f"https://www.lutrija.rs/Results?drawNo={year_round[1]}&gameNo=1&drawYear={year_round[0]}"
        
        html = self._load_url(url)
        if not html:
            return result
        
        html = self.html_parser._quick_format_html(html)
        
        # Find Loto TAB
        loto_tab = self.html_parser.get_tags(html_code=html, tag="div", custom_tag_property=[["id", "tabs-lotoResults"]])
        
        if not loto_tab:
            return result
        loto_tab = loto_tab[0]

        # Find Bingo TAB
        if year_round is None:
            bingo_tab = self.html_parser.get_tags(html_code=html, tag="div", custom_tag_property=[["id", "tabs-bingoResults"]])
            if bingo_tab:
                bingo_tab = bingo_tab[0]
            else:
                bingo_tab = ""
            self._update_current_bingo_results(html=bingo_tab)

        # Find Round, Date and Year
        rnd_date_text = self.html_parser.get_tags(html_code=loto_tab, tag="div", tag_class_contains="Rez_Txt_Title")
        if not rnd_date_text:
            return result
        rnd_date_text = self.html_parser.get_raw_text(load_html_code=rnd_date_text[0]).strip()
        date = ""
        rnd = ""
        pos = rnd_date_text.rfind(" ")
        if pos != -1:
            date = rnd_date_text[pos+1:]
            for i in rnd_date_text[:pos].split(" "):
                i_int = self._get_integer(i.strip(" ."))
                if i_int:
                    rnd = str(i_int)
                    break
        if not date or not rnd:
            return result
        result["round"] = rnd
        result["date"] = date
        if date:
            result["year"] = [x.strip() for x in date.split(".") if x.strip()][-1]

        # lbl_loto_title_info
        text = "Datum izvlačenja #--1, izveštaj za #--2. kolo."
        text_to_html = utility_cls.TextToHTML(text=text)
        rule1 = utility_cls.TextToHtmlRule(text="#--1", replace_with=date, font_bold=True, fg_color="#ff0000")
        rule2 = utility_cls.TextToHtmlRule(text="#--2", replace_with=rnd, font_bold=True, fg_color="#ff0000")
        text_to_html.add_rule(rule1)
        text_to_html.add_rule(rule2)
        result["lbl_loto_title_info"] = text_to_html.get_html()

        # Loto, Loto Plus and Joker numbers
        numbers = self.html_parser.get_tags(html_code=loto_tab, tag="div", tag_class_contains="Rez_Brojevi_Txt_Gray")
        loto_numbers = []
        loto_plus_numbers = []
        dzoker_numbers = []
        for idx, number in enumerate(numbers):
            number_value = str(self._get_integer(self.html_parser.get_raw_text(load_html_code=number)))
            if idx <= 6:
                loto_numbers.append(number_value)
            elif idx > 6 and idx <= 13:
                loto_plus_numbers.append(number_value)
            elif idx > 13 and idx <= 19:
                dzoker_numbers.append(number_value)
        result["loto_numbers"] = loto_numbers
        result["loto_plus_numbers"] = loto_plus_numbers
        result["dzoker_numbers"] = dzoker_numbers

        # lbl_loto_expected, lbl_loto_plus_expected, lbl_dzoker_expected
        side_labels = self.html_parser.get_tags(html_code=loto_tab, tag="div", tag_class_contains="DIV_Rez_Loto_Right")
        if side_labels:
            result["lbl_loto_expected"] = self._get_side_label_text(side_labels[0])
        if len(side_labels) > 1:
            result["lbl_loto_plus_expected"] = self._get_side_label_text(side_labels[1])
        if len(side_labels) > 2:
            result["lbl_dzoker_expected"] = self._get_side_label_text(side_labels[2])

        # lbl_loto_total, lbl_loto_fond, lbl_loto_fond7, lbl_loto_price, lbl_loto_komb_num
        data = self._get_summary_table_data(html_code=loto_tab, table_id="table-loto-payments")
        result["lbl_loto_total"] = data[0] if len(data) > 0 else ""
        result["lbl_loto_fond"] = data[1] if len(data) > 1 else ""
        result["lbl_loto_fond7"] = data[2] if len(data) > 2 else ""
        result["lbl_loto_price"] = data[3] if len(data) > 3 else ""
        result["lbl_loto_komb_num"] = data[4] if len(data) > 4 else ""

        # lbl_loto_prize_7_num, lbl_loto_prize_7_amount, lbl_loto_prize_6_num, lbl_loto_prize_6_amount, lbl_loto_prize_5_num, lbl_loto_prize_5_amount, lbl_loto_prize_4_num, lbl_loto_prize_4_amount, lbl_loto_prize_3_num, lbl_loto_prize_3_amount
        data = self._get_summary_table_data(html_code=loto_tab, table_id="table-prize-breakdown")
        result["lbl_loto_prize_7_num"] = data[0][1] if len(data) > 0 and len(data[0]) > 2 else ""
        result["lbl_loto_prize_7_amount"] = data[0][2] if len(data) > 0 and len(data[0]) > 2 else ""
        result["lbl_loto_prize_6_num"] = data[1][1] if len(data) > 1 and len(data[1]) > 2 else ""
        result["lbl_loto_prize_6_amount"] = data[1][2] if len(data) > 1 and len(data[1]) > 2 else ""
        result["lbl_loto_prize_5_num"] = data[2][1] if len(data) > 2 and len(data[2]) > 2 else ""
        result["lbl_loto_prize_5_amount"] = data[2][2] if len(data) > 2 and len(data[2]) > 2 else ""
        result["lbl_loto_prize_4_num"] = data[3][1] if len(data) > 3 and len(data[3]) > 2 else ""
        result["lbl_loto_prize_4_amount"] = data[3][2] if len(data) > 3 and len(data[3]) > 2 else ""
        result["lbl_loto_prize_3_num"] = data[4][1] if len(data) > 4 and len(data[4]) > 2 else ""
        result["lbl_loto_prize_3_amount"] = data[4][2] if len(data) > 4 and len(data[4]) > 2 else ""

        # lbl_loto_plus_total, lbl_loto_plus_fond, lbl_loto_plus_price, lbl_loto_plus_winers, lbl_loto_plus_amount
        data = self._get_summary_table_data(html_code=loto_tab, table_id="table-loto-plus")
        result["lbl_loto_plus_total"] = data[0] if len(data) > 0 else ""
        result["lbl_loto_plus_fond"] = data[1] if len(data) > 1 else ""
        result["lbl_loto_plus_price"] = data[2] if len(data) > 2 else ""
        result["lbl_loto_plus_winers"] = data[3] if len(data) > 3 else ""
        result["lbl_loto_plus_amount"] = data[4] if len(data) > 4 else ""

        # lbl_dzoker_total, lbl_dzoker_fond, lbl_dzoker_price, lbl_dzoker_winers, lbl_dzoker_amount
        data = self._get_summary_table_data(html_code=loto_tab, table_id="table-joker")
        result["lbl_dzoker_total"] = data[0] if len(data) > 0 else ""
        result["lbl_dzoker_fond"] = data[1] if len(data) > 1 else ""
        result["lbl_dzoker_price"] = data[2] if len(data) > 2 else ""
        result["lbl_dzoker_winers"] = data[3] if len(data) > 3 else ""
        result["lbl_dzoker_amount"] = data[4] if len(data) > 4 else ""

        result["is_loaded"] = True
        
        return result

    def btn_bingo_archive_clicked(self):
        if not self.frm_bingo_archive.isVisible():
            if not self.txt_bingo_archive_year.text():
                self.txt_bingo_archive_year.setText(self.settings["current_bingo"]["year"])
            if self.spn_bingo_archive_round.value() == 0:
                self.spn_bingo_archive_round.setMinimum(1)
                value = self._get_integer(self.settings["current_bingo"]["round"])
                if not value:
                    value = 1
                self.spn_bingo_archive_round.setValue(value)

        self.frm_bingo_archive.setVisible(not self.frm_bingo_archive.isVisible())
        self.frm_bingo_numbers.setVisible(False)
        self.frm_bingo_plus_numbers.setVisible(False)
    
    def btn_bingo_archive_show_clicked(self):
        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_dls") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.setDisabled(True)

        QCoreApplication.processEvents()

        year_round = tuple([self.txt_bingo_archive_year.text(), self.spn_bingo_archive_round.text()])
        self._show_archived_bingo_result(year_round=year_round)
        self.frm_bingo_numbers.setVisible(False)
        self.frm_bingo_plus_numbers.setVisible(False)

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)

        self.setDisabled(False)

    def _show_archived_bingo_result(self, year_round: tuple = None):
        if year_round is None:
            url = "https://www.lutrija.rs/Results"
        else:
            url = f"https://www.lutrija.rs/Results?drawNo={year_round[1]}&gameNo=5&drawYear={year_round[0]}"
        
        html = self._load_url(url)
        if not html:
            return
        
        html = self.html_parser._quick_format_html(html)
        
        # Find Bingo TAB
        bingo_tab = self.html_parser.get_tags(html_code=html, tag="div", custom_tag_property=[["id", "tabs-bingoResults"]])
        if bingo_tab:
            bingo_tab = bingo_tab[0]
        else:
            return
        
        data = self._get_bingo_results(html=bingo_tab)
        self._populate_bingo_frame(data=data, update_main_bingo_button=False)
        self.frm_bingo_archive.setVisible(False)
        self.frm_bingo_numbers.setVisible(False)
        self.frm_bingo_plus_numbers.setVisible(False)

    def _update_current_bingo_results(self, html: str):
        data = self._get_bingo_results(html=html)
        self.settings["current_bingo"] = data
        self._populate_bingo_frame(data=data)

    def _populate_bingo_frame(self, data: dict, update_main_bingo_button: bool = True):
        if update_main_bingo_button:
            self.lbl_bingo_btn.setText(f"Bingo - {data['date']}")

        self.lbl_bingo_title_info.setText(data["date"])
        self.lbl_bingo_title_report.setText(data["lbl_bingo_title_report"])
        self.lbl_bingo_total.setText(data["lbl_bingo_total"])
        self.lbl_bingo_price.setText(data["lbl_bingo_price"])
        self.lbl_bingo_tikets.setText(data["lbl_bingo_tikets"])
        self.lbl_bingo_bingo_num.setText(data["lbl_bingo_bingo_num"])
        self.lbl_bingo_1red.setText(data["lbl_bingo_1red"])
        self.lbl_bingo_replace_num.setText(data["lbl_bingo_replace_num"])

        self.lbl_bingo_prize_1_title.setText(data["lbl_bingo_prize_1_title"])
        self.lbl_bingo_prize_1_winers.setText(data["lbl_bingo_prize_1_winers"])
        self.lbl_bingo_prize_1_amount.setText(data["lbl_bingo_prize_1_amount"])
        self.lbl_bingo_prize_2_title.setText(data["lbl_bingo_prize_2_title"])
        self.lbl_bingo_prize_2_winers.setText(data["lbl_bingo_prize_2_winers"])
        self.lbl_bingo_prize_2_amount.setText(data["lbl_bingo_prize_2_amount"])
        self.lbl_bingo_prize_3_title.setText(data["lbl_bingo_prize_3_title"])
        self.lbl_bingo_prize_3_winers.setText(data["lbl_bingo_prize_3_winers"])
        self.lbl_bingo_prize_3_amount.setText(data["lbl_bingo_prize_3_amount"])
        self.lbl_bingo_prize_4_title.setText(data["lbl_bingo_prize_4_title"])
        self.lbl_bingo_prize_4_winers.setText(data["lbl_bingo_prize_4_winers"])
        self.lbl_bingo_prize_4_amount.setText(data["lbl_bingo_prize_4_amount"])

        self.lbl_bingo_plus_title_report.setText(data["lbl_bingo_plus_title_report"])
        self.lbl_bingo_plus_total.setText(data["lbl_bingo_plus_total"])
        self.lbl_bingo_plus_price.setText(data["lbl_bingo_plus_price"])
        self.lbl_bingo_plus_tikets.setText(data["lbl_bingo_plus_tikets"])
        self.lbl_bingo_plus_bingo_num.setText(data["lbl_bingo_plus_bingo_num"])
        self.lbl_bingo_plus_ring_num.setText(data["lbl_bingo_plus_ring_num"])
        self.lbl_bingo_plus_center_num.setText(data["lbl_bingo_plus_center_num"])
        self.lbl_bingo_plus_replace_num.setText(data["lbl_bingo_plus_replace_num"])

        self.lbl_bingo_plus_prize_1_title.setText(data["lbl_bingo_plus_prize_1_title"])
        self.lbl_bingo_plus_prize_1_winers.setText(data["lbl_bingo_plus_prize_1_winers"])
        self.lbl_bingo_plus_prize_1_amount.setText(data["lbl_bingo_plus_prize_1_amount"])
        self.lbl_bingo_plus_prize_2_title.setText(data["lbl_bingo_plus_prize_2_title"])
        self.lbl_bingo_plus_prize_2_winers.setText(data["lbl_bingo_plus_prize_2_winers"])
        self.lbl_bingo_plus_prize_2_amount.setText(data["lbl_bingo_plus_prize_2_amount"])
        self.lbl_bingo_plus_prize_3_title.setText(data["lbl_bingo_plus_prize_3_title"])
        self.lbl_bingo_plus_prize_3_winers.setText(data["lbl_bingo_plus_prize_3_winers"])
        self.lbl_bingo_plus_prize_3_amount.setText(data["lbl_bingo_plus_prize_3_amount"])
        self.lbl_bingo_plus_prize_4_title.setText(data["lbl_bingo_plus_prize_4_title"])
        self.lbl_bingo_plus_prize_4_winers.setText(data["lbl_bingo_plus_prize_4_winers"])
        self.lbl_bingo_plus_prize_4_amount.setText(data["lbl_bingo_plus_prize_4_amount"])
        self.lbl_bingo_plus_prize_5_title.setText(data["lbl_bingo_plus_prize_5_title"])
        self.lbl_bingo_plus_prize_5_winers.setText(data["lbl_bingo_plus_prize_5_winers"])
        self.lbl_bingo_plus_prize_5_amount.setText(data["lbl_bingo_plus_prize_5_amount"])
        self.lbl_bingo_plus_prize_6_title.setText(data["lbl_bingo_plus_prize_6_title"])
        self.lbl_bingo_plus_prize_6_winers.setText(data["lbl_bingo_plus_prize_6_winers"])
        self.lbl_bingo_plus_prize_6_amount.setText(data["lbl_bingo_plus_prize_6_amount"])

        # Create bingo numbers frame
        for child in self.frm_bingo_numbers.children():
            child.deleteLater()

        w = self.frm_bingo.width() - 20
        if w < 100:
            w = 100
        
        y = 10
        x = 10
        x_spacing = 10
        y_spacing = 10
        for number in data["bingo_numbers"]:
            lbl_pic = QLabel(self.frm_bingo_numbers)
            lbl_txt = QLabel(self.frm_bingo_numbers)
            
            lbl_pic.move(x, y)
            lbl_pic.resize(80, 80)
            lbl_pic.setPixmap(QPixmap(self.getv("ball_blue_icon_path")))
            lbl_pic.setScaledContents(True)
            
            lbl_txt.move(x, y - 3)
            lbl_txt.resize(80, 80)
            lbl_txt.setText(number)
            font = lbl_txt.font()
            font.setPointSize(32)
            font.setBold(True)
            lbl_txt.setFont(font)
            lbl_txt.setAlignment(Qt.AlignCenter)
            lbl_txt.setStyleSheet("QLabel {color: rgb(255, 255, 0); background-color: rgba(255, 255, 255, 0);} QLabel:hover {color: rgb(230, 255, 0);}")

            x += lbl_pic.width() + x_spacing
            if x + lbl_pic.width() + x_spacing > w:
                x = 10
                y += lbl_pic.height() + y_spacing
            
        if x != 10:
            y += lbl_pic.height() + y_spacing
        
        self.frm_bingo_numbers.resize(w, y)

        # Create bingo plus numbers frame
        for child in self.frm_bingo_plus_numbers.children():
            child.deleteLater()

        w = self.frm_bingo.width() - 20
        if w < 100:
            w = 100
        
        y = 10
        x = 10
        x_spacing = 10
        y_spacing = 10
        for number in data["bingo_plus_numbers"]:
            lbl_pic = QLabel(self.frm_bingo_plus_numbers)
            lbl_txt = QLabel(self.frm_bingo_plus_numbers)
            
            lbl_pic.move(x, y)
            lbl_pic.resize(80, 80)
            lbl_pic.setPixmap(QPixmap(self.getv("ball_red_icon_path")))
            lbl_pic.setScaledContents(True)
            
            lbl_txt.move(x, y - 3)
            lbl_txt.resize(80, 80)
            lbl_txt.setText(number)
            font = lbl_txt.font()
            font.setPointSize(32)
            font.setBold(True)
            lbl_txt.setFont(font)
            lbl_txt.setAlignment(Qt.AlignCenter)
            lbl_txt.setStyleSheet("QLabel {color: rgb(255, 255, 0); background-color: rgba(255, 255, 255, 0);} QLabel:hover {color: rgb(230, 255, 0);}")

            x += lbl_pic.width() + x_spacing
            if x + lbl_pic.width() + x_spacing > w:
                x = 10
                y += lbl_pic.height() + y_spacing
            
        if x != 10:
            y += lbl_pic.height() + y_spacing
        
        self.frm_bingo_plus_numbers.resize(w, y)

        if self.frm_bingo_numbers.height() + 10 > self.frm_bingo.height():
            self.frm_bingo.resize(self.frm_bingo.width(), self.frm_bingo_numbers.height() + 70)
        if self.frm_bingo_plus_numbers.height() + 10 > self.frm_bingo.height():
            self.frm_bingo.resize(self.frm_bingo.width(), self.frm_bingo_plus_numbers.height() + 520)

    def _get_bingo_results(self, html: str) -> dict:
        result = self._empty_bingo_dict()

        # year, round, date
        rnd_date_text = self.html_parser.get_tags(html_code=html, tag="div", tag_class_contains="Rez_Txt_Title")
        if not rnd_date_text:
            return result
        rnd_date_text = self.html_parser.get_raw_text(load_html_code=rnd_date_text[0]).strip()
        date = ""
        rnd = ""
        pos = rnd_date_text.rfind(" ")
        if pos != -1:
            date = rnd_date_text[pos+1:]
            for i in rnd_date_text[:pos].split(" "):
                i_int = self._get_integer(i.strip(" ."))
                if i_int:
                    rnd = str(i_int)
                    break
        if not date or not rnd:
            return result
        result["round"] = rnd
        result["date"] = date
        if date:
            result["year"] = [x.strip() for x in date.split(".") if x.strip()][-1]

        # lbl_bingo_title_report, lbl_bingo_plus_title_report
        text = "Datum izvlačenja #--1, izveštaj za #--2. kolo."
        text_to_html = utility_cls.TextToHTML(text=text)
        rule1 = utility_cls.TextToHtmlRule(text="#--1", replace_with=date, font_bold=True, fg_color="#ff0000")
        rule2 = utility_cls.TextToHtmlRule(text="#--2", replace_with=rnd, font_bold=True, fg_color="#ff0000")
        text_to_html.add_rule(rule1)
        text_to_html.add_rule(rule2)
        result["lbl_bingo_title_report"] = text_to_html.get_html()
        result["lbl_bingo_plus_title_report"] = text_to_html.get_html()

        # Numbers for Bingo and Bingo Plus
        stop_line = self.html_parser.get_tags(html_code=html, tag="table", custom_tag_property=[["id", "table-bingo-payments"]], return_line_numbers=True)
        if stop_line:
            stop_line = stop_line[0][1]
        else:
            return result
        bingo_numbers_code = self.html_parser.get_tags(html_code=html, tag="div", tag_class_contains="Rez_Brojevi_Txt_Gray", return_line_numbers=True)
        bingo_numbers = []
        bingo_plus_numbers = []
        for number in bingo_numbers_code:
            number_text = self.html_parser.get_raw_text(load_html_code=number[0]).strip()

            if number[1] < stop_line:
                bingo_numbers.append(number_text)
            else:
                bingo_plus_numbers.append(number_text)
        result["bingo_numbers"] = bingo_numbers
        result["bingo_plus_numbers"] = bingo_plus_numbers

        # Bingo payments
        payment_label_map = ["lbl_bingo_total", "lbl_bingo_price", "lbl_bingo_tikets", "lbl_bingo_bingo_num", "lbl_bingo_1red", "lbl_bingo_replace_num"]
        bingo_payment_table = self.html_parser.get_tags(html_code=html, tag="table", custom_tag_property=[["id", "table-bingo-payments"]])
        bingo_payments_rows = self.html_parser.get_tags(html_code=bingo_payment_table[0], tag="tr")
        idx = 0
        for row in bingo_payments_rows:
            cols = self.html_parser.get_tags(html_code=row, tag="td")
            if len(cols) == 2:
                cols[0] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[0]).strip())
                cols[1] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[1]).strip())
                text = cols[0] + " " + "#--1"
                text_to_html = utility_cls.TextToHTML(text=text)
                rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=cols[1], font_bold=True)
                text_to_html.add_rule(rule)
                result[payment_label_map[idx]] = text_to_html.get_html()
                idx += 1
        
        # Bingo prizes
        prize_label_map = [
            ["lbl_bingo_prize_1_title", "lbl_bingo_prize_1_winers", "lbl_bingo_prize_1_amount"],
            ["lbl_bingo_prize_2_title", "lbl_bingo_prize_2_winers", "lbl_bingo_prize_2_amount"],
            ["lbl_bingo_prize_3_title", "lbl_bingo_prize_3_winers", "lbl_bingo_prize_3_amount"],
            ["lbl_bingo_prize_4_title", "lbl_bingo_prize_4_winers", "lbl_bingo_prize_4_amount"]
        ]
        bingo_prize_table = self.html_parser.get_tags(html_code=html, tag="table", custom_tag_property=[["id", "table-bingo-prize-breakdown"]])
        bingo_prize_rows = self.html_parser.get_tags(html_code=bingo_prize_table[0], tag="tr")
        idx = 0
        for row in bingo_prize_rows:
            cols = self.html_parser.get_tags(html_code=row, tag="td")
            if len(cols) == 3:
                cols[0] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[0]).strip())
                cols[1] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[1]).strip())
                cols[2] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[2]).strip())
                result[prize_label_map[idx][0]] = cols[0]
                result[prize_label_map[idx][1]] = cols[1]
                result[prize_label_map[idx][2]] = cols[2]
                idx += 1
        
        # Bingo Plus payments
        payment_label_map = [
            "lbl_bingo_plus_total",
            "lbl_bingo_plus_price",
            "lbl_bingo_plus_tikets",
            "lbl_bingo_plus_bingo_num",
            "lbl_bingo_plus_ring_num",
            "lbl_bingo_plus_center_num",
            "lbl_bingo_plus_replace_num"
        ]
        bingo_payment_table = self.html_parser.get_tags(html_code=html, tag="table", custom_tag_property=[["id", "table-bingo-plus-payments"]])
        bingo_payment_rows = self.html_parser.get_tags(html_code=bingo_payment_table[0], tag="tr")
        idx = 0
        for row in bingo_payment_rows:
            cols = self.html_parser.get_tags(html_code=row, tag="td")
            if len(cols) == 2:
                cols[0] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[0]).strip())
                cols[1] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[1]).strip())
                text = cols[0] + " " + "#--1"
                text_to_html = utility_cls.TextToHTML(text=text)
                rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=cols[1], font_bold=True)
                text_to_html.add_rule(rule)
                result[payment_label_map[idx]] = text_to_html.get_html()
                idx += 1

        # Bingo Plus prizes
        prize_label_map = [
            ["lbl_bingo_plus_prize_1_title", "lbl_bingo_plus_prize_1_winers", "lbl_bingo_plus_prize_1_amount"],
            ["lbl_bingo_plus_prize_2_title", "lbl_bingo_plus_prize_2_winers", "lbl_bingo_plus_prize_2_amount"],
            ["lbl_bingo_plus_prize_3_title", "lbl_bingo_plus_prize_3_winers", "lbl_bingo_plus_prize_3_amount"],
            ["lbl_bingo_plus_prize_4_title", "lbl_bingo_plus_prize_4_winers", "lbl_bingo_plus_prize_4_amount"],
            ["lbl_bingo_plus_prize_5_title", "lbl_bingo_plus_prize_5_winers", "lbl_bingo_plus_prize_5_amount"],
            ["lbl_bingo_plus_prize_6_title", "lbl_bingo_plus_prize_6_winers", "lbl_bingo_plus_prize_6_amount"]
        ]
        bingo_prize_table = self.html_parser.get_tags(html_code=html, tag="table", custom_tag_property=[["id", "table-bingop-prize-breakdown"]])
        bingo_prize_rows = self.html_parser.get_tags(html_code=bingo_prize_table[0], tag="tr")
        idx = 0
        for row in bingo_prize_rows:
            cols = self.html_parser.get_tags(html_code=row, tag="td")
            if len(cols) == 3:
                cols[0] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[0]).strip())
                cols[1] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[1]).strip())
                cols[2] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[2]).strip())
                result[prize_label_map[idx][0]] = cols[0]
                result[prize_label_map[idx][1]] = cols[1]
                result[prize_label_map[idx][2]] = cols[2]
                idx += 1

        result["is_loaded"] = True
        return result

    def _get_summary_table_data(self, html_code: str, table_id: str) -> list:
        result = []
        table_code = self.html_parser.get_tags(html_code=html_code, tag="table", custom_tag_property=[["id", table_id]])
        if not table_code:
            return result
        table_code = table_code[0]
        rows = self.html_parser.get_tags(html_code=table_code, tag="tr")
        for row in rows:
            cols = self.html_parser.get_tags(html_code=row, tag="td")
            if len(cols) == 2:
                cols[0] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[0]).strip())
                cols[1] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[1]).strip())
                text = cols[0] + " " + "#--1"
                text_to_html = utility_cls.TextToHTML(text=text)
                rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=cols[1], font_bold=True)
                text_to_html.add_rule(rule)
                result.append(text_to_html.get_html())
            elif len(cols) == 3:
                cols[0] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[0]).strip())
                cols[1] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[1]).strip())
                cols[2] = self.cirilica_u_latinicu(self.html_parser.get_raw_text(load_html_code=cols[2]).strip())
                result.append([cols[0], cols[1], cols[2]])
                
        return result

    def _get_side_label_text(self, html: str) -> str:
        text_slices = self.html_parser.get_all_text_slices(load_html_code=html)
        text_to_html = utility_cls.TextToHTML()
        text = ""
        rules = []
        count = 0
        for text_slice in text_slices:
            count += 1
            text_slice: html_parser_cls.TextObject
            text_slice.txt_value = self.cirilica_u_latinicu(text_slice.txt_value)
            if '_Red"' in text_slice.get_tag():
                text_id = "#" + "-" * (6 - len(str(count))) + str(count)
                rules.append([text_id, text_slice.txt_value])
                text += text_id + " "
            else:
                text += text_slice.txt_value + " "
        text = text.strip()
        text_to_html.set_text(text)
        for rule in rules:
            text_to_html.add_rule(utility_cls.TextToHtmlRule(text=rule[0], replace_with=rule[1], font_bold=True, fg_color="#ff0000"))
        
        return text_to_html.get_html()

    def _empty_loto_dict(self) -> dict:
        result = {
            "is_loaded": False,
            "round": "",
            "year": "",
            "date": "",
            "loto_numbers": [],
            "lbl_loto_title_info": "",
            "lbl_loto_expected": "",
            "lbl_loto_total": "",
            "lbl_loto_fond": "",
            "lbl_loto_fond7": "",
            "lbl_loto_price": "",
            "lbl_loto_komb_num": "",
            "lbl_loto_prize_7_num": "",
            "lbl_loto_prize_7_amount": "",
            "lbl_loto_prize_6_num": "",
            "lbl_loto_prize_6_amount": "",
            "lbl_loto_prize_5_num": "",
            "lbl_loto_prize_5_amount": "",
            "lbl_loto_prize_4_num": "",
            "lbl_loto_prize_4_amount": "",
            "lbl_loto_prize_3_num": "",
            "lbl_loto_prize_3_amount": "",

            "loto_plus_numbers": [],
            "lbl_loto_plus_expected": "",
            "lbl_loto_plus_total": "",
            "lbl_loto_plus_fond": "",
            "lbl_loto_plus_price": "",
            "lbl_loto_plus_winers": "",
            "lbl_loto_plus_amount": "",

            "dzoker_numbers": [],
            "lbl_dzoker_expected": "",
            "lbl_dzoker_total": "",
            "lbl_dzoker_fond": "",
            "lbl_dzoker_price": "",
            "lbl_dzoker_winers": "",
            "lbl_dzoker_amount": ""
        }
        return result
    
    def _empty_bingo_dict(self) -> dict:
        result = {
            "is_loaded": False,
            "year": "",
            "round": "",
            "date": "",
            "bingo_numbers": [],
            "lbl_bingo_title_report": "",
            "lbl_bingo_prize_1_title": "",
            "lbl_bingo_prize_1_winers": "",
            "lbl_bingo_prize_1_amount": "",
            "lbl_bingo_prize_2_title": "",
            "lbl_bingo_prize_2_winers": "",
            "lbl_bingo_prize_2_amount": "",
            "lbl_bingo_prize_3_title": "",
            "lbl_bingo_prize_3_winers": "",
            "lbl_bingo_prize_3_amount": "",
            "lbl_bingo_prize_4_title": "",
            "lbl_bingo_prize_4_winers": "",
            "lbl_bingo_prize_4_amount": "",
            "lbl_bingo_total": "",
            "lbl_bingo_price": "",
            "lbl_bingo_tikets": "",
            "lbl_bingo_bingo_num": "",
            "lbl_bingo_1red": "",
            "lbl_bingo_replace_num": "",

            "bingo_plus_numbers": [],
            "lbl_bingo_plus_title_report": "",
            "lbl_bingo_plus_prize_1_title": "",
            "lbl_bingo_plus_prize_1_winers": "",
            "lbl_bingo_plus_prize_1_amount": "",
            "lbl_bingo_plus_prize_2_title": "",
            "lbl_bingo_plus_prize_2_winers": "",
            "lbl_bingo_plus_prize_2_amount": "",
            "lbl_bingo_plus_prize_3_title": "",
            "lbl_bingo_plus_prize_3_winers": "",
            "lbl_bingo_plus_prize_3_amount": "",
            "lbl_bingo_plus_prize_4_title": "",
            "lbl_bingo_plus_prize_4_winers": "",
            "lbl_bingo_plus_prize_4_amount": "",
            "lbl_bingo_plus_prize_5_title": "",
            "lbl_bingo_plus_prize_5_winers": "",
            "lbl_bingo_plus_prize_5_amount": "",
            "lbl_bingo_plus_prize_6_title": "",
            "lbl_bingo_plus_prize_6_winers": "",
            "lbl_bingo_plus_prize_6_amount": "",
            "lbl_bingo_plus_total": "",
            "lbl_bingo_plus_price": "",
            "lbl_bingo_plus_tikets": "",
            "lbl_bingo_plus_bingo_num": "",
            "lbl_bingo_plus_ring_num": "",
            "lbl_bingo_plus_center_num": "",
            "lbl_bingo_plus_replace_num": ""
        }
        return result
    
    def _empty_loto_system_dict(self) -> dict:
        result = {
            "type": "",
            "name": "",
            "desc": "",
            "is_enabled": False,
            "can_be_removed": False,
            "numbers": [],
            "sys_numbers": 0,
            "sys_shema": []
        }
        return result

    def _get_user_settings(self) -> dict:
        result = {
            "current_loto": self._empty_loto_dict(),
            "current_bingo": self._empty_bingo_dict(),
            "completed_years": [],
            "loto": {
                "archive": [],
                "system": []
            },
            "bingo": {
                "archive": [],
                "system": []
            }
            }

        if "online_topic_dls_settings" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("online_topic_dls_settings")
            
            result["loto"]["archive"] = list(g.get("loto_archive", []))
            result["loto"]["system"] = list(g.get("loto_system", []))
            result["bingo"]["archive"] = list(g.get("bingo_archive", []))
            result["bingo"]["system"] = list(g.get("bingo_system", []))
            result["completed_years"] = list(g.get("completed_years", []))
        
        return result

    def _update_user_settings(self) -> None:
        result = {}
        
        if "online_topic_dls_settings" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("online_topic_dls_settings", self.settings, save_to_file=True)

        result["loto_archive"] = list(self.settings["loto"]["archive"])
        result["loto_system"] = list(self.settings["loto"]["system"])
        result["bingo_archive"] = list(self.settings["bingo"]["archive"])
        result["bingo_system"] = list(self.settings["bingo"]["system"])
        result["completed_years"] = list(self.settings["completed_years"])

        self.set_appv("online_topic_dls_settings", result)

    def _get_my_height(self):
        h = 220
        if self.frm_loto.isVisible():
            h += self.frm_loto.height()
        elif self.frm_bingo.isVisible():
            h += self.frm_bingo.height()
        elif self.frm_loto_archive.isVisible():
            h += self.frm_loto_archive.height()
        elif self.frm_loto_komb.isVisible():
            h += self.frm_loto_komb.height()
        return h

    def resizeEvent(self, event: QResizeEvent):
        self.resize_me()
        return super().resizeEvent(event)
    
    def resize_me(self, size: QSize = None):
        w = self.contentsRect().width()

        self.frm_loto.move(10, 220)
        self.frm_loto.resize(w - 20, self.frm_loto.height())
        self.lbl_loto_title_info.resize(self.frm_loto.width() - self.lbl_loto_title_info.pos().x() - 10, self.lbl_loto_title_info.height())

        self.frm_bingo.move(10, 220)
        self.frm_bingo.resize(w - 20, self.frm_bingo.height())
        self.lbl_bingo_title_report.resize(self.frm_bingo.width() - 20, self.lbl_bingo_title_report.height())
        self.lbl_bingo_plus_title_report.resize(self.frm_bingo.width() - 20, self.lbl_bingo_plus_title_report.height())

        self.frm_loto_archive.move(10, 220)
        self.frm_loto_archive_search.resize(self.frm_loto_archive.width() - 240, self.lbl_loto_archive_search_results.height() + 130)
        self.frm_loto_archive.resize(w - 20, max(self.lst_loto_archive_years.height() + 170, self.frm_loto_archive_search.height() + 20))
        
        self.frm_loto_komb.move(10, 220)
        self.frm_loto_komb.resize(w - 20, self.frm_loto_komb.height())
        if self.frm_loto_komb_work:
            self.frm_loto_komb_work.resize(self.frm_loto_komb.width() - self.frm_loto_komb_work.pos().x() - 10, self.frm_loto_komb_work.height())

        self.setFixedHeight(max(self._get_my_height(), self.parent_widget.get_topic_area_size().height()))

    def _define_widgets(self):
        # Title
        self.lbl_title_pic: QLabel = self.findChild(QLabel, "lbl_title_pic")
        # Buttons
        self.lbl_loto_btn: QLabel = self.findChild(QLabel, "lbl_loto_btn")
        self.lbl_loto_archive_btn: QLabel = self.findChild(QLabel, "lbl_loto_archive_btn")
        self.lbl_loto_komb_btn: QLabel = self.findChild(QLabel, "lbl_loto_komb_btn")
        self.lbl_bingo_btn: QLabel = self.findChild(QLabel, "lbl_bingo_btn")
        self.lbl_bingo_archive_btn: QLabel = self.findChild(QLabel, "lbl_bingo_archive_btn")
        # Loto frame
        self.frm_loto: QFrame = self.findChild(QFrame, "frm_loto")
        self.lbl_loto_title_info: QLabel = self.findChild(QLabel, "lbl_loto_title_info")
        self.lbl_loto_n1_num: QLabel = self.findChild(QLabel, "lbl_loto_n1_num")
        self.lbl_loto_n2_num: QLabel = self.findChild(QLabel, "lbl_loto_n2_num")
        self.lbl_loto_n3_num: QLabel = self.findChild(QLabel, "lbl_loto_n3_num")
        self.lbl_loto_n4_num: QLabel = self.findChild(QLabel, "lbl_loto_n4_num")
        self.lbl_loto_n5_num: QLabel = self.findChild(QLabel, "lbl_loto_n5_num")
        self.lbl_loto_n6_num: QLabel = self.findChild(QLabel, "lbl_loto_n6_num")
        self.lbl_loto_n7_num: QLabel = self.findChild(QLabel, "lbl_loto_n7_num")
        self.lbl_loto_prize_7_num: QLabel = self.findChild(QLabel, "lbl_loto_prize_7_num")
        self.lbl_loto_prize_6_num: QLabel = self.findChild(QLabel, "lbl_loto_prize_6_num")
        self.lbl_loto_prize_5_num: QLabel = self.findChild(QLabel, "lbl_loto_prize_5_num")
        self.lbl_loto_prize_4_num: QLabel = self.findChild(QLabel, "lbl_loto_prize_4_num")
        self.lbl_loto_prize_3_num: QLabel = self.findChild(QLabel, "lbl_loto_prize_3_num")
        self.lbl_loto_prize_7_amount: QLabel = self.findChild(QLabel, "lbl_loto_prize_7_amount")
        self.lbl_loto_prize_6_amount: QLabel = self.findChild(QLabel, "lbl_loto_prize_6_amount")
        self.lbl_loto_prize_5_amount: QLabel = self.findChild(QLabel, "lbl_loto_prize_5_amount")
        self.lbl_loto_prize_4_amount: QLabel = self.findChild(QLabel, "lbl_loto_prize_4_amount")
        self.lbl_loto_prize_3_amount: QLabel = self.findChild(QLabel, "lbl_loto_prize_3_amount")
        self.lbl_loto_expected: QLabel = self.findChild(QLabel, "lbl_loto_expected")
        self.lbl_loto_total: QLabel = self.findChild(QLabel, "lbl_loto_total")
        self.lbl_loto_fond: QLabel = self.findChild(QLabel, "lbl_loto_fond")
        self.lbl_loto_fond7: QLabel = self.findChild(QLabel, "lbl_loto_fond7")
        self.lbl_loto_price: QLabel = self.findChild(QLabel, "lbl_loto_price")
        self.lbl_loto_komb_num: QLabel = self.findChild(QLabel, "lbl_loto_komb_num")
        
        self.lbl_loto_plus_n1_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n1_num")
        self.lbl_loto_plus_n2_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n2_num")
        self.lbl_loto_plus_n3_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n3_num")
        self.lbl_loto_plus_n4_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n4_num")
        self.lbl_loto_plus_n5_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n5_num")
        self.lbl_loto_plus_n6_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n6_num")
        self.lbl_loto_plus_n7_num: QLabel = self.findChild(QLabel, "lbl_loto_plus_n7_num")
        self.lbl_loto_plus_expected: QLabel = self.findChild(QLabel, "lbl_loto_plus_expected")
        self.lbl_loto_plus_total: QLabel = self.findChild(QLabel, "lbl_loto_plus_total")
        self.lbl_loto_plus_fond: QLabel = self.findChild(QLabel, "lbl_loto_plus_fond")
        self.lbl_loto_plus_price: QLabel = self.findChild(QLabel, "lbl_loto_plus_price")
        self.lbl_loto_plus_winers: QLabel = self.findChild(QLabel, "lbl_loto_plus_winers")
        self.lbl_loto_plus_amount: QLabel = self.findChild(QLabel, "lbl_loto_plus_amount")

        self.lbl_dzoker_n1_num: QLabel = self.findChild(QLabel, "lbl_dzoker_n1_num")
        self.lbl_dzoker_n2_num: QLabel = self.findChild(QLabel, "lbl_dzoker_n2_num")
        self.lbl_dzoker_n3_num: QLabel = self.findChild(QLabel, "lbl_dzoker_n3_num")
        self.lbl_dzoker_n4_num: QLabel = self.findChild(QLabel, "lbl_dzoker_n4_num")
        self.lbl_dzoker_n5_num: QLabel = self.findChild(QLabel, "lbl_dzoker_n5_num")
        self.lbl_dzoker_n6_num: QLabel = self.findChild(QLabel, "lbl_dzoker_n6_num")
        self.lbl_dzoker_expected: QLabel = self.findChild(QLabel, "lbl_dzoker_expected")
        self.lbl_dzoker_total: QLabel = self.findChild(QLabel, "lbl_dzoker_total")
        self.lbl_dzoker_fond: QLabel = self.findChild(QLabel, "lbl_dzoker_fond")
        self.lbl_dzoker_price: QLabel = self.findChild(QLabel, "lbl_dzoker_price")
        self.lbl_dzoker_winers: QLabel = self.findChild(QLabel, "lbl_dzoker_winers")
        self.lbl_dzoker_amount: QLabel = self.findChild(QLabel, "lbl_dzoker_amount")
        # Bingo frame
        self.frm_bingo: QFrame = self.findChild(QFrame, "frm_bingo")
        self.lbl_bingo_title_info: QLabel = self.findChild(QLabel, "lbl_bingo_title_info")
        self.lbl_bingo_prize_1_title: QLabel = self.findChild(QLabel, "lbl_bingo_prize_1_title")
        self.lbl_bingo_prize_1_winers: QLabel = self.findChild(QLabel, "lbl_bingo_prize_1_winers")
        self.lbl_bingo_prize_1_amount: QLabel = self.findChild(QLabel, "lbl_bingo_prize_1_amount")
        self.lbl_bingo_prize_2_title: QLabel = self.findChild(QLabel, "lbl_bingo_prize_2_title")
        self.lbl_bingo_prize_2_winers: QLabel = self.findChild(QLabel, "lbl_bingo_prize_2_winers")
        self.lbl_bingo_prize_2_amount: QLabel = self.findChild(QLabel, "lbl_bingo_prize_2_amount")
        self.lbl_bingo_prize_3_title: QLabel = self.findChild(QLabel, "lbl_bingo_prize_3_title")
        self.lbl_bingo_prize_3_winers: QLabel = self.findChild(QLabel, "lbl_bingo_prize_3_winers")
        self.lbl_bingo_prize_3_amount: QLabel = self.findChild(QLabel, "lbl_bingo_prize_3_amount")
        self.lbl_bingo_prize_4_title: QLabel = self.findChild(QLabel, "lbl_bingo_prize_4_title")
        self.lbl_bingo_prize_4_winers: QLabel = self.findChild(QLabel, "lbl_bingo_prize_4_winers")
        self.lbl_bingo_prize_4_amount: QLabel = self.findChild(QLabel, "lbl_bingo_prize_4_amount")
        self.lbl_bingo_total: QLabel = self.findChild(QLabel, "lbl_bingo_total")
        self.lbl_bingo_price: QLabel = self.findChild(QLabel, "lbl_bingo_price")
        self.lbl_bingo_tikets: QLabel = self.findChild(QLabel, "lbl_bingo_tikets")
        self.lbl_bingo_bingo_num: QLabel = self.findChild(QLabel, "lbl_bingo_bingo_num")
        self.lbl_bingo_1red: QLabel = self.findChild(QLabel, "lbl_bingo_1red")
        self.lbl_bingo_replace_num: QLabel = self.findChild(QLabel, "lbl_bingo_replace_num")
        self.btn_bingo_show_numbers: QPushButton = self.findChild(QPushButton, "btn_bingo_show_numbers")
        self.frm_bingo_numbers: QFrame = self.findChild(QFrame, "frm_bingo_numbers")
        self.lbl_bingo_title_report: QLabel = self.findChild(QLabel, "lbl_bingo_title_report")

        self.lbl_bingo_plus_prize_1_title: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_1_title")
        self.lbl_bingo_plus_prize_1_winers: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_1_winers")
        self.lbl_bingo_plus_prize_1_amount: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_1_amount")
        self.lbl_bingo_plus_prize_2_title: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_2_title")
        self.lbl_bingo_plus_prize_2_winers: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_2_winers")
        self.lbl_bingo_plus_prize_2_amount: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_2_amount")
        self.lbl_bingo_plus_prize_3_title: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_3_title")
        self.lbl_bingo_plus_prize_3_winers: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_3_winers")
        self.lbl_bingo_plus_prize_3_amount: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_3_amount")
        self.lbl_bingo_plus_prize_4_title: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_4_title")
        self.lbl_bingo_plus_prize_4_winers: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_4_winers")
        self.lbl_bingo_plus_prize_4_amount: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_4_amount")
        self.lbl_bingo_plus_prize_5_title: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_5_title")
        self.lbl_bingo_plus_prize_5_winers: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_5_winers")
        self.lbl_bingo_plus_prize_5_amount: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_5_amount")
        self.lbl_bingo_plus_prize_6_title: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_6_title")
        self.lbl_bingo_plus_prize_6_winers: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_6_winers")
        self.lbl_bingo_plus_prize_6_amount: QLabel = self.findChild(QLabel, "lbl_bingo_plus_prize_6_amount")
        self.lbl_bingo_plus_total: QLabel = self.findChild(QLabel, "lbl_bingo_plus_total")
        self.lbl_bingo_plus_price: QLabel = self.findChild(QLabel, "lbl_bingo_plus_price")
        self.lbl_bingo_plus_tikets: QLabel = self.findChild(QLabel, "lbl_bingo_plus_tikets")
        self.lbl_bingo_plus_bingo_num: QLabel = self.findChild(QLabel, "lbl_bingo_plus_bingo_num")
        self.lbl_bingo_plus_ring_num: QLabel = self.findChild(QLabel, "lbl_bingo_plus_ring_num")
        self.lbl_bingo_plus_center_num: QLabel = self.findChild(QLabel, "lbl_bingo_plus_center_num")
        self.lbl_bingo_plus_replace_num: QLabel = self.findChild(QLabel, "lbl_bingo_plus_replace_num")
        self.btn_bingo_plus_show_numbers: QPushButton = self.findChild(QPushButton, "btn_bingo_plus_show_numbers")
        self.frm_bingo_plus_numbers: QFrame = self.findChild(QFrame, "frm_bingo_plus_numbers")
        self.lbl_bingo_plus_title_report: QLabel = self.findChild(QLabel, "lbl_bingo_plus_title_report")
        # Loto archive frame
        self.frm_loto_archive: QFrame = self.findChild(QFrame, "frm_loto_archive")
        self.txt_loto_archive_year: QLineEdit = self.findChild(QLineEdit, "txt_loto_archive_year")
        self.txt_loto_archive_round: QLineEdit = self.findChild(QLineEdit, "txt_loto_archive_round")
        self.btn_loto_archive_show: QPushButton = self.findChild(QPushButton, "btn_loto_archive_show")
        self.lst_loto_archive_years: QListWidget = self.findChild(QListWidget, "lst_loto_archive_years")
        self.frm_loto_archive_search: QFrame = self.findChild(QFrame, "frm_loto_archive_search")
        self.lbl_loto_archive_search_year: QLabel = self.findChild(QLabel, "lbl_loto_archive_search_year")
        self.btn_loto_archive_search_download: QPushButton = self.findChild(QPushButton, "btn_loto_archive_search_download")
        self.lbl_loto_archive_search_completed: QLabel = self.findChild(QLabel, "lbl_loto_archive_search_completed")
        self.lbl_loto_archive_search_results: QLabel = self.findChild(QLabel, "lbl_loto_archive_search_results")
        # Bingo archive frame
        self.btn_bingo_archive: QPushButton = self.findChild(QPushButton, "btn_bingo_archive")
        self.frm_bingo_archive: QFrame = self.findChild(QFrame, "frm_bingo_archive")
        self.txt_bingo_archive_year: QLineEdit = self.findChild(QLineEdit, "txt_bingo_archive_year")
        self.spn_bingo_archive_round: QSpinBox = self.findChild(QSpinBox, "spn_bingo_archive_round")
        self.btn_bingo_archive_show: QPushButton = self.findChild(QPushButton, "btn_bingo_archive_show")
        # Loto combinations and systems frame
        self.frm_loto_komb: QFrame = self.findChild(QFrame, "frm_loto_komb")
        self.frm_loto_komb_komb: QFrame = self.findChild(QFrame, "frm_loto_komb_komb")
        self.frm_loto_komb_sys: QFrame = self.findChild(QFrame, "frm_loto_komb_sys")
        self.btn_loto_komb_check: QPushButton = self.findChild(QPushButton, "btn_loto_komb_check")
        self.btn_loto_komb_add_komb: QPushButton = self.findChild(QPushButton, "btn_loto_komb_add_komb")
        self.btn_loto_komb_add_sys: QPushButton = self.findChild(QPushButton, "btn_loto_komb_add_sys")
        self.lbl_loto_komb_komb_title_pic: QLabel = self.findChild(QLabel, "lbl_loto_komb_komb_title_pic")
        self.lbl_loto_komb_komb_title: QLabel = self.findChild(QLabel, "lbl_loto_komb_komb_title")
        self.line_loto_komb_komb: QFrame = self.findChild(QFrame, "line_loto_komb_komb")
        self.lbl_loto_komb_sys_title_pic: QLabel = self.findChild(QLabel, "lbl_loto_komb_sys_title_pic")
        self.lbl_loto_komb_sys_title: QLabel = self.findChild(QLabel, "lbl_loto_komb_sys_title")
        self.line_loto_komb_sys: QFrame = self.findChild(QFrame, "line_loto_komb_sys")

        self._define_widgets_apperance()

    def _define_widgets_apperance(self):
        self.frm_loto.setVisible(False)
        self.frm_bingo.setVisible(False)
        self.frm_loto_archive.setVisible(False)
        self.frm_bingo_archive.setVisible(False)
        self.frm_loto_komb.setVisible(False)
        self.frm_loto_archive_search.setVisible(False)
        self.frm_bingo_numbers.setVisible(False)
        self.frm_bingo_plus_numbers.setVisible(False)

        self.lbl_bingo_archive_btn.setVisible(False)

        self.lbl_loto_btn.setCursor(Qt.PointingHandCursor)
        self.lbl_loto_archive_btn.setCursor(Qt.PointingHandCursor)
        self.lbl_loto_komb_btn.setCursor(Qt.PointingHandCursor)
        self.lbl_bingo_btn.setCursor(Qt.PointingHandCursor)
        self.btn_loto_archive_show.setCursor(Qt.PointingHandCursor)
        self.lbl_loto_archive_search_results.linkActivated.connect(self._on_loto_archive_search_results_link_activated)





