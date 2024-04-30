from PyQt5.QtWidgets import (QFrame, QPushButton, QWidget, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QSpinBox, QTextEdit, QScrollArea, QVBoxLayout, QProgressBar)
from PyQt5.QtGui import QPixmap, QMouseEvent, QResizeEvent, QIcon, QFontMetrics, QColor, QFont
from PyQt5.QtCore import QSize, Qt, QCoreApplication
from PyQt5 import uic
from PyQt5.QtMultimedia import QSound

import webbrowser
import random

import settings_cls
import utility_cls
import html_parser_cls
from online_abstract_topic import AbstractTopic
import UTILS


class Numbers(QFrame):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, data: dict) -> None:
        """
        data["width] = int | None
        data["border] = boolean
        data["background"]: string
        data["foreground"]: string
        data["hor_padding"] = int
        data["ver_padding"] = int
        data["hor_spacing"] = int
        data["ver_spacing"] = int
        data["numbers"] = list of numbers
        data["number_width"] = int
        data["number_height"] = int
        data["number_image_path"] = string
        data["feedback_click_function"] = function
        data["has_cancel"] = boolean
        data["marked_numbers"] = list of marked numbers
        data["marked_numbers_icon_path"] = string
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

        # Prefix image
        if self.data["prefix_image"]:
            lbl_prefix = QLabel(self)
            lbl_prefix.setPixmap(QPixmap(self.data["prefix_image"]))
            lbl_prefix.resize(self.data["number_width"], self.data["number_height"])
            lbl_prefix.setScaledContents(True)
            lbl_prefix.move(x, y)
            lbl_prefix.setStyleSheet("QLabel {border: 0px;} QLabel:hover {background-color: #5ad9ff; border: 0px;}")
            x += self.data["number_width"] + self.data["hor_spacing"]

        # Create new widgets
        for number in numbers:
            lbl_pic = QLabel(self)
            lbl_pic.setStyleSheet("QLabel {border: 0px;}")
            if number in self.data["marked_numbers"]:
                lbl_pic.setPixmap(QPixmap(self.data["marked_numbers_icon_path"]))
            else:
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
            lbl_value_foreground_color = self.data["foreground"]
            lbl_value.setStyleSheet(f"QLabel {{color: {lbl_value_foreground_color}; background-color: rgba(255, 255, 255, 0); border: 0px;}} QLabel:hover {{color: rgb(230, 255, 0); border: 0px;}}")
            # lbl_value.setCursor(Qt.PointingHandCursor)
            lbl_value.mousePressEvent = lambda event, number=number: self._on_number_clicked(event, number)

            x += self.data["number_width"] + self.data["hor_spacing"]
            if self.data["width"]:
                if x + self.data["number_width"] + self.data["hor_spacing"] > self.data["width"]:
                    x = self.data["hor_padding"]
                    y += self.data["number_height"] + self.data["ver_spacing"]
        
        if self.data["has_cancel"]:
            lbl_remove = QLabel(self)
            lbl_remove.setPixmap(QPixmap(self.getv("cancel_icon_path")))
            lbl_remove.resize(self.data["number_width"], self.data["number_height"])
            lbl_remove.setScaledContents(True)
            lbl_remove.move(x, y)
            lbl_remove.setStyleSheet("QLabel {border: 0px;} QLabel:hover {background-color: #5ad9ff; border: 0px;}")
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
            "width": data.get("width", None),
            "border": data.get("border", True),
            "background": data.get("background", None),
            "foreground": data.get("foreground", "#ffff00"),
            "hor_padding": data.get("hor_padding", 5),
            "ver_padding": data.get("ver_padding", 5),
            "hor_spacing": data.get("hor_spacing", 5),
            "ver_spacing": data.get("ver_spacing", 10),
            "numbers": data.get("numbers", []),
            "number_width": data.get("number_width", 0),
            "number_height": data.get("number_height", 0),
            "number_image_path": data.get("number_image_path", self.getv("ball_red_icon_path")),
            "feedback_click_function": data.get("feedback_click_function", None),
            "has_cancel": data.get("has_cancel", True),
            "prefix_image": data.get("prefix_image", None),
            "marked_numbers": data.get("marked_numbers", []),
            "marked_numbers_icon_path": data.get("marked_numbers_icon_path", "")
        }
        return result

    def _create_frame(self):
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(0)

        if self.data["background"]:
            bg_stylesheet = f"background-color: {self.data['background']};"
        else:
            bg_stylesheet = ""

        if self.data["border"]:
            brd_stylesheet = "border-color: #d40000; border-style: solid; border-width: 1px;"
        else:
            brd_stylesheet = "border: 0px;"

        stylesheet = "QFrame {" + bg_stylesheet + brd_stylesheet + "}"
        self.setStyleSheet(stylesheet)


class WorkingFrame(QFrame):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, data: dict) -> None:
        """
        data["type"] = string (add_komb, add_sys, edit_komb, edit_sys, winnings)
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

        self.frm_list_kombs = None
        self.frm_list_kombs_joker = None
        
        self.max_numbers = 7
        self.max_numbers_pool = 39
        if self.data["item"]:
            self.max_numbers_pool = self.data["item"]["sys_numbers"]
        if self.data["item_type"] == "komb":
            self.max_numbers_pool = 39

        self.selected_kombs = []
        if self.data["item"]:
            self.selected_kombs_joker = self.data["item"].get("joker_numbers", [])
        else:
            self.selected_kombs_joker = []

        self.pick_numbers_update_function = None

        self.sound_max_numbers_reached = QSound(self.getv("def_add_auto_added_image_error_sound_file_path"))
        self.sound_loto6 = QSound(self.getv("loto6_sound_file_path"))
        self.sound_loto7 = QSound(self.getv("loto7_sound_file_path"))
        self.sound_loto5 = QSound(self.getv("loto5_sound_file_path"))


        if "view" in self.data["type"]:
            self._create_view_frame()
        elif "winnings" in self.data["type"]:
            self._create_winnings_frame()
        else:
            self._create_frame()

    def _create_winnings_frame(self):
        w = self.data["width"]
        self.area = QScrollArea(self)
        self.area_widget = QWidget(self.area)
        self.area_widget_layout = QVBoxLayout(self.area_widget)
        self.area_widget.setLayout(self.area_widget_layout)
        self.area.setWidget(self.area_widget)
        self.area.setWidgetResizable(True)
        self.area.move(0, 0)
        self.area.resize(w, self.data["height"])
        # Set margins to 0
        self.area_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.area_widget_layout.setSpacing(0)

        for loto_komb in self.data["kombs"]:
            if len(self.data["rounds"]) == 1:
                expanded = True
            else:
                expanded = False
            loto_winnning_frame = self._create_winning_komb_frame(loto_komb, self.data["rounds"], expanded=expanded)
            self.area_widget_layout.addWidget(loto_winnning_frame)
        
        h = 10
        for item in range(self.area_widget_layout.count()):
            h += self.area_widget_layout.itemAt(item).widget().height()

        if len(self.data["kombs"] * len(self.data["rounds"])) == 0:
            h = self.data["height"] - 10
            lbl = QLabel(self.area_widget)
            lbl.setText("Nema izabrane kombinacije ili sistema !\n\nMolim odaberite kombinaciju i sistem !")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont("Arial", 26))
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #ff0000; background-color: #000000;")
            lbl.setFixedSize(w - 10, h)
            self.area_widget_layout.addWidget(lbl)
            lbl.show()
            self.area_widget.resize(w-10, h)

        self.area_widget.setFixedHeight(h)
        self.area.show()

    def _create_winning_komb_frame(self, loto_komb: dict, rounds: list, expanded: bool):
        w = self.data["width"] - 20
        h = self.data["height"]

        # Frame
        frm = QFrame(self.area_widget)
        frm.setFrameShape(QFrame.NoFrame)
        frm.setFrameShadow(QFrame.Plain)
        frm.setLineWidth(0)
        # frm.setStyleSheet("border: 1px solid rgb(0, 255, 0);")
        frm.setFixedWidth(w)
        w = w - 20

        # Title
        lbl_title = QLabel(frm)
        if loto_komb["type"] == "sys":
            lbl_title.setText(f"Sistem {loto_komb['name']}")
        else:
            lbl_title.setText(f"Kombinacija {loto_komb['name']}")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl_title.setWordWrap(True)
        font = lbl_title.font()
        font.setPointSize(20)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("color: rgb(255, 255, 0); background-color: rgb(0, 61, 0);")
        lbl_title.move(10, 5)
        lbl_title.setFixedWidth(w - 20)
        lbl_title.adjustSize()
        y = lbl_title.height() + 10

        x = 10
        total_winings = 0
        total_cost = 0
        prg_data = {
            "title": "Molim sačekajte...",
            "max_value": len(rounds),
            "value": 0,
            "item_name": loto_komb["name"],
            "action": "show",
            "step": 4
        }
        self.data["feedback_function"](prg_data, "progress")
        prg_data["action"] = "update"
        for idx, round_item in enumerate(rounds):
            prg_data["value"] = idx
            self.data["feedback_function"](prg_data, "progress")

            winings = self._get_winning_data(loto_komb, round_item)
            if loto_komb["type"] == "sys":
                data = {
                    "width": w - 20,
                    "border": False,
                    "numbers": loto_komb["sys_selected_numbers"],
                    "number_width": 20,
                    "number_height": 20,
                    "number_image_path": self.getv("ball_white_icon_path"),
                    "has_cancel": False,
                    "marked_numbers": [int(x) for x in round_item["loto_numbers"]],
                    "marked_numbers_icon_path": self.getv("ball_red_icon_path")
                }
                frm_sys_numbers_loto = Numbers(frm, self._stt, data)
                frm_sys_numbers_loto.setParent(frm)
                frm_sys_numbers_loto.move(x, y)
                
                has_all_numbers = True
                count = 0
                for i in round_item["loto_numbers"]:
                    if int(i) not in loto_komb["sys_selected_numbers"]:
                        has_all_numbers = False
                    else:
                        count += 1
                        
                loto_sys_spacing = 50
                if has_all_numbers:
                    lbl_sedmica_loto = QLabel(frm)
                    lbl_sedmica_loto.setAlignment(Qt.AlignCenter)
                    lbl_sedmica_loto.setPixmap(QPixmap(self.getv("online_topic_dls_sedmica_icon_path")))
                    lbl_sedmica_loto.setScaledContents(True)
                    lbl_sedmica_loto.resize(108, 20)
                    lbl_sedmica_loto.move(x + frm_sys_numbers_loto.width() + 10, y)
                    loto_sys_spacing = 130
                else:
                    lbl_sedmica_loto = QLabel(frm)
                    lbl_sedmica_loto.setAlignment(Qt.AlignCenter)
                    lbl_sedmica_loto.setText(str(count))
                    font = lbl_sedmica_loto.font()
                    font.setPointSize(16)
                    font.setBold(True)
                    lbl_sedmica_loto.setFont(font)
                    if count == 6:
                        lbl_sedmica_loto.setStyleSheet("color: #00ff00; background-color: #ff0000;")
                    elif count == 5:
                        lbl_sedmica_loto.setStyleSheet("color: #00ff00;")
                    elif count == 4 or count == 3:
                        lbl_sedmica_loto.setStyleSheet("color: #ffffff;")
                    else:
                        lbl_sedmica_loto.setStyleSheet("color: #8b8b8b;")
                    lbl_sedmica_loto.setFixedSize(30, 20)
                    lbl_sedmica_loto.move(x + frm_sys_numbers_loto.width() + 10, y)

                y += frm_sys_numbers_loto.height() + 5
            
                data = {
                    "width": w - 20,
                    "border": False,
                    "numbers": loto_komb["sys_selected_numbers"],
                    "number_width": 20,
                    "number_height": 20,
                    "number_image_path": self.getv("ball_white_icon_path"),
                    "has_cancel": False,
                    "marked_numbers": [int(x) for x in round_item["loto_plus_numbers"]],
                    "marked_numbers_icon_path": self.getv("ball_blue_icon_path")
                }
                frm_sys_numbers_loto_plus = Numbers(frm, self._stt, data)
                frm_sys_numbers_loto_plus.setParent(frm)
                if frm_sys_numbers_loto.width() + loto_sys_spacing + frm_sys_numbers_loto_plus.width() < w:
                    y -= (frm_sys_numbers_loto.height() + 5)
                    x_loto_plus = x + frm_sys_numbers_loto.width() + loto_sys_spacing
                else:
                    x_loto_plus = x
                frm_sys_numbers_loto_plus.move(x_loto_plus, y)

                has_all_numbers = True
                count = 0
                for i in round_item["loto_plus_numbers"]:
                    if int(i) not in loto_komb["sys_selected_numbers"]:
                        has_all_numbers = False
                    else:
                        count += 1
                if has_all_numbers:
                    lbl_sedmica_loto_plus = QLabel(frm)
                    lbl_sedmica_loto_plus.setAlignment(Qt.AlignCenter)
                    lbl_sedmica_loto_plus.setPixmap(QPixmap(self.getv("online_topic_dls_sedmica_icon_path")))
                    lbl_sedmica_loto_plus.setScaledContents(True)
                    lbl_sedmica_loto_plus.resize(108, 20)
                    lbl_sedmica_loto_plus.move(x_loto_plus + frm_sys_numbers_loto_plus.width() + 10, y)
                else:
                    lbl_sedmica_loto_plus = QLabel(frm)
                    lbl_sedmica_loto_plus.setAlignment(Qt.AlignCenter)
                    lbl_sedmica_loto_plus.setText(str(count))
                    font = lbl_sedmica_loto_plus.font()
                    font.setPointSize(16)
                    font.setBold(True)
                    lbl_sedmica_loto_plus.setFont(font)
                    if count == 6:
                        lbl_sedmica_loto_plus.setStyleSheet("color: #00ff00; background-color: #ff0000;")
                    elif count == 5:
                        lbl_sedmica_loto_plus.setStyleSheet("color: #00ff00;")
                    elif count == 4 or count == 3:
                        lbl_sedmica_loto_plus.setStyleSheet("color: #ffffff;")
                    else:
                        lbl_sedmica_loto_plus.setStyleSheet("color: #8b8b8b;")
                    lbl_sedmica_loto_plus.setFixedSize(30, 20)
                    lbl_sedmica_loto_plus.move(x_loto_plus + frm_sys_numbers_loto_plus.width() + 10, y)

                y += frm_sys_numbers_loto_plus.height() + 5

            # Label Info
            if len(rounds) < 10:
                font_size = 16
                delim_char = "\n"
            else:
                font_size = 12
                delim_char = "      "

            lbl_info = QLabel(frm)
            lbl_info.setTextInteractionFlags(lbl_info.textInteractionFlags() | Qt.TextSelectableByMouse)
            lbl_info.setWordWrap(True)
            lbl_info.move(x, y)
            lbl_info.setFixedWidth(w - 20)

            text_to_html = utility_cls.TextToHTML()
            text_to_html.general_rule.fg_color = "rgb(170, 255, 127)"
            text_to_html.general_rule.font_size = font_size
            text = f'Kolo #--1  Godina #--2   Datum: #--3{delim_char}'
            rule = utility_cls.TextToHtmlRule(
                text="#--1",
                replace_with=round_item["round"],
                fg_color="rgb(255, 0, 0)",
                link_href="show_loto_round"
            )
            text_to_html.add_rule(rule)

            rule = utility_cls.TextToHtmlRule(
                text="#--2",
                replace_with=round_item["year"],
                fg_color="rgb(255, 0, 0)"
            )
            text_to_html.add_rule(rule)

            rule = utility_cls.TextToHtmlRule(
                text="#--3",
                replace_with=round_item["date"],
                fg_color="#aa007f"
            )
            text_to_html.add_rule(rule)

            text += "Loto dobici:  #--4"

            if winings["loto_win7"]["winnings"]:
                if len(rounds) == 1:
                    self.sound_loto7.play()
                rule = utility_cls.TextToHtmlRule(
                    text="#--4",
                    replace_with="Sedmica: " + str(winings["loto_win7"]["winnings"]),
                    fg_color="#ffff00",
                    bg_color="#ff0000",
                    font_size=50,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#--4",
                    replace_with="Sedmica: " + str(winings["loto_win7"]["winnings"]),
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += "   #--5"
            if winings["loto_win6"]["winnings"]:
                if len(rounds) == 1:
                    self.sound_loto6.play()
                rule = utility_cls.TextToHtmlRule(
                    text="#--5",
                    replace_with="Šestica: " + str(winings["loto_win6"]["winnings"]),
                    fg_color="#ffff00",
                    bg_color="#aa0000",
                    font_size=36,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#--5",
                    replace_with="Šestica: " + str(winings["loto_win6"]["winnings"]),
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += "   #--6"
            if winings["loto_win5"]["winnings"]:
                if len(rounds) == 1:
                    self.sound_loto5.play()
                rule = utility_cls.TextToHtmlRule(
                    text="#--6",
                    replace_with="Petica: " + str(winings["loto_win5"]["winnings"]),
                    fg_color="#ffff00",
                    bg_color="#9e6900",
                    font_size=26,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#--6",
                    replace_with="Petica: " + str(winings["loto_win5"]["winnings"]),
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += "   #--7"
            if winings["loto_win4"]["winnings"]:
                rule = utility_cls.TextToHtmlRule(
                    text="#--7",
                    replace_with="Četvorka: " + str(winings["loto_win4"]["winnings"]),
                    fg_color="#ffff00",
                    font_size=16,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#--7",
                    replace_with="Četvorka: " + str(winings["loto_win4"]["winnings"]),
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += "   #--8"
            if winings["loto_win3"]["winnings"]:
                rule = utility_cls.TextToHtmlRule(
                    text="#--8",
                    replace_with="Trojka: " + str(winings["loto_win3"]["winnings"]),
                    fg_color="#ffff00",
                    font_size=16,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#--8",
                    replace_with="Trojka: " + str(winings["loto_win3"]["winnings"]),
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += f"{delim_char}Loto Plus dobitak: #--9"
            if winings["loto_plus_win7"]["winnings"]:
                if len(rounds) == 1:
                    self.sound_loto7.play()
                rule = utility_cls.TextToHtmlRule(
                    text="#--9",
                    replace_with="Sedmica: " + str(winings["loto_plus_win7"]["winnings"]),
                    fg_color="#ffff00",
                    bg_color="#ff0000",
                    font_size=50,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#--9",
                    replace_with="Sedmica: " + str(winings["loto_plus_win7"]["winnings"]),
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += f"{delim_char}Džoker: #-10"
            if winings["joker"]["winnings"]:
                if len(rounds) == 1:
                    self.sound_loto6.play()
                rule = utility_cls.TextToHtmlRule(
                    text="#-10",
                    replace_with="Džoker dobitak",
                    fg_color="#ffff00",
                    bg_color="#ff0000",
                    font_size=50,
                    font_bold=True
                )
            else:
                rule = utility_cls.TextToHtmlRule(
                    text="#-10",
                    replace_with="Nema dobitka",
                    fg_color="#dcdcdc"
                )
            text_to_html.add_rule(rule)

            text += f"{delim_char}Prikaži detalje"
            rule = utility_cls.TextToHtmlRule(
                text="Prikaži detalje",
                font_size=14,
                fg_color="#aaffff",
                link_href="show_kombs"
            )
            text_to_html.add_rule(rule)

            text_to_html.set_text(text)

            lbl_info.setText(text_to_html.get_html())
            lbl_info.setFixedWidth(w - 20)

            lbl_info.adjustSize()
            y += lbl_info.height() + 10

            # Kombinacije
            frm_kombs = QFrame(frm)
            frm_kombs.setFrameShape(QFrame.NoFrame)
            frm_kombs.setFrameShadow(QFrame.Plain)
            frm_kombs.setLineWidth(0)
            frm_kombs.resize(w - 20, 1)
            frm_kombs.move(10, y)
            y += 1

            lbl_info.linkActivated.connect(lambda url, lbl_info=lbl_info, frm_kombs=frm_kombs, frm=frm, loto_komb=loto_komb, round_item=round_item, winings=winings: self._show_kombs(url, lbl_info, frm_kombs, frm, loto_komb, round_item, winings))

            total_winings += winings["loto_win7"]["total"] + winings["loto_win6"]["total"] + winings["loto_win5"]["total"] + winings["loto_win4"]["total"] + winings["loto_win3"]["total"] + winings["loto_plus_win7"]["total"] + winings["joker"]["total"]
            total_cost += winings["loto_cost"] + winings["loto_plus_cost"] + winings["joker_cost"]

        prg_data["action"] = "hide"
        self.data["feedback_function"](prg_data, "progress")
        # Summary label
        lbl_summ = QLabel(frm)
        lbl_summ.setObjectName("lbl_summ")
        lbl_summ.setTextInteractionFlags(lbl_summ.textInteractionFlags()|Qt.TextSelectableByMouse)
        text_to_html = utility_cls.TextToHTML()
        text_to_html.general_rule.fg_color = "#ffff00"
        text_to_html.general_rule.font_size = font_size + 6
        text = "Ukupan dobitak: #--1,  Potrošeno: #--2,   Profit: #--3"
        rule = utility_cls.TextToHtmlRule(
            text="#--1", 
            replace_with=f"{total_winings:,.2f}",
            fg_color="#ff0000")
        text_to_html.add_rule(rule)
        rule = utility_cls.TextToHtmlRule(
            text="#--2", 
            replace_with=f"{total_cost:,.2f}",
            fg_color="#ff0000")
        text_to_html.add_rule(rule)
        profit = total_winings - total_cost
        if total_winings - total_cost > 0:
            rule = utility_cls.TextToHtmlRule(
                text="#--3", 
                replace_with=f"{profit:,.2f}",
                fg_color="#00ff00",
                font_size=font_size + 14,
                font_bold=True)
        else:
            rule = utility_cls.TextToHtmlRule(
                text="#--3", 
                replace_with=f"{profit:,.2f}",
                fg_color="#ff0000")
            
        text_to_html.add_rule(rule)
        text_to_html.set_text(text)
        lbl_summ.setText(text_to_html.get_html())
        lbl_summ.move(10, y)
        lbl_summ.setFixedWidth(w - 20)
        lbl_summ.adjustSize()
        y += lbl_summ.height() + 5

        frm.setFixedSize(frm.width(), lbl_summ.pos().y() + lbl_summ.height() + 5)

        return frm

    def _show_kombs(self, url: str, lbl_info: QLabel, frm_kombs: QFrame, main_frame: QFrame, loto_komb: dict, round_item: dict, winings: dict):
        if url == "show_loto_round":
            data_dict = {
                "round": round_item["round"],
                "year": round_item["year"]
            }
            self.data["feedback_function"](data_dict, "show_loto_round")
            return
        
        frm_kombs_height = frm_kombs.height()

        for widget in main_frame.children():
            if widget.objectName() == "lbl_summ":
                lbl_summ: QLabel = widget

        if frm_kombs.height() > 1:
            lbl_info.setText(lbl_info.text().replace("Sakrij detalje", "Prikaži detalje"))
            frm_kombs.resize(frm_kombs.width(), 1)
            frm_kombs.setStyleSheet("QFrame {border: 0px;}")
        else:
            frm_kombs.setStyleSheet("QFrame {border: 1px solid #aaffff;}")
            lbl_info.setText(lbl_info.text().replace("Prikaži detalje", "Sakrij detalje"))
            x = 10
            y = 5
            for komb in loto_komb["numbers"]:
                marked_numbers = [int(x) for x in round_item["loto_numbers"]]
                count = 0
                for i in komb:
                    if i in marked_numbers:
                        count += 1
                frm_background = ""
                frm_border = False
                if count > 2:
                    frm_background = "#000000"
                    frm_border = True

                data = {
                    "width": main_frame.width() - 20,
                    "border": frm_border,
                    "background": frm_background,
                    "numbers": komb,
                    "number_width": 20,
                    "number_height": 20,
                    "number_image_path": self.getv("ball_white_icon_path"),
                    "has_cancel": False,
                    "marked_numbers": marked_numbers,
                    "marked_numbers_icon_path": self.getv("ball_red_icon_path")
                }
                frm_numbers = Numbers(frm_kombs, self._stt, data)
                frm_numbers.setParent(frm_kombs)
                frm_numbers.move(x, y)
                frm_numbers.show()

                x += frm_numbers.width() + 50
                if x + frm_numbers.width() > frm_kombs.width() - 10:
                    x = 10
                    y += frm_numbers.height() + 10
            
            y += frm_numbers.height() + 5

            # Recapitulation label
            lbl_recap = QLabel(frm_kombs)
            lbl_recap.setTextInteractionFlags(lbl_recap.textInteractionFlags()|Qt.TextSelectableByMouse)
            lbl_recap.setWordWrap(True)
            lbl_recap.setFixedWidth(frm_kombs.width() - 20)
            lbl_recap.move(10, y)

            text_to_html = utility_cls.TextToHTML()
            text_to_html.general_rule.fg_color = "#ffff00"
            text_to_html.general_rule.font_size = 14
            text = "Sedmica: #--1 * #--2 din = #--3\n"
            text += "Šestica: #--4 * #--5 din = #--6\n"
            text += "Petica: #--7 * #--8 din = #--9\n"
            text += "Četvorki: #-10 * #-11 din = #-12\n"
            text += "Trojki: #-13 * #-14 din = #-15\n"
            text += "Loto plus sedmica: #-16 * #-17 din = #-18\n"
            text += "Džoker: #-19 * #-20 din = #-21\n\n"
            text += f"Ukupan dobitak: #-22,  Potrošeno: #-23 + #-24 = #-25,   Profit: #-26\n\n"
            
            rule_has_wining_color = "#aaff00"
            rule_no_wining_color = "#aaaaaa"
            
            wining_data_for_rule = [
               [winings['loto_win7']['winnings'], winings['loto_win7']['amount'], winings['loto_win7']['total']],
               [winings['loto_win6']['winnings'], winings['loto_win6']['amount'], winings['loto_win6']['total']],
               [winings['loto_win5']['winnings'], winings['loto_win5']['amount'], winings['loto_win5']['total']],
               [winings['loto_win4']['winnings'], winings['loto_win4']['amount'], winings['loto_win4']['total']],
               [winings['loto_win3']['winnings'], winings['loto_win3']['amount'], winings['loto_win3']['total']],
               [winings['loto_plus_win7']['winnings'], winings['loto_plus_win7']['amount'], winings['loto_plus_win7']['total']],
               [winings['joker']['winnings'], winings['joker']['amount'], winings['joker']['total']]
            ]

            count = 1
            total_winings = 0
            for i in range(len(wining_data_for_rule)):
                item = wining_data_for_rule[i]
                total_winings += item[2]
                if item[0]:
                    color = rule_has_wining_color
                    color_amount = "#ff0000"
                    font_bold = True
                else:
                    color_amount = rule_no_wining_color
                    color = rule_no_wining_color
                    font_bold = False

                rule_id = "#" + "-"*(3-len(str(count))) + str(count)
                rule = utility_cls.TextToHtmlRule(
                    text=rule_id,
                    replace_with=f"{item[0]}",
                    fg_color=color_amount,
                    font_bold=font_bold)
                text_to_html.add_rule(rule)

                count += 1
                rule_id = "#" + "-"*(3-len(str(count))) + str(count)
                rule = utility_cls.TextToHtmlRule(
                    text=rule_id, 
                    replace_with=f"{item[1]:,.2f}",
                    fg_color="#ffffff",
                    font_bold=False)
                text_to_html.add_rule(rule)

                count += 1
                rule_id = "#" + "-"*(3-len(str(count))) + str(count)
                rule = utility_cls.TextToHtmlRule(
                    text=rule_id,
                    replace_with=f"{item[2]:,.2f}",
                    fg_color=color,
                    font_bold=font_bold)
                text_to_html.add_rule(rule)
                
                count += 1

            rule = utility_cls.TextToHtmlRule(
                text="#-22",
                replace_with=f"{total_winings:,.2f}",
                fg_color="#ff0000",
                font_bold=True
            )
            text_to_html.add_rule(rule)
            
            rule = utility_cls.TextToHtmlRule(
                text="#-23",
                replace_with=f"{winings['loto_cost']:,.2f}",
                fg_color="#ffffff",
                font_bold=False
            )
            text_to_html.add_rule(rule)

            rule = utility_cls.TextToHtmlRule(
                text="#-24",
                replace_with=f"{winings['loto_plus_cost']:,.2f}",
                fg_color="#ffffff",
                font_bold=False
            )
            text_to_html.add_rule(rule)

            rule = utility_cls.TextToHtmlRule(
                text="#-25",
                replace_with=f"{winings['loto_cost'] + winings['loto_plus_cost']:,.2f}",
                fg_color="#ff0000",
                font_bold=True
            )
            text_to_html.add_rule(rule)

            if total_winings >= winings['loto_cost'] + winings['loto_plus_cost'] + winings['joker_cost']:
                color = "#00ff00"
            else:
                color = "#ff0000"

            rule = utility_cls.TextToHtmlRule(
                text="#-26",
                replace_with=f"{total_winings - (winings['loto_cost'] + winings['loto_plus_cost']):,.2f}",
                fg_color=color,
                font_bold=True
            )
            if total_winings - (winings['loto_cost'] + winings['loto_plus_cost'] + winings['joker_cost']) < 0:
                rule.font_size = text_to_html.general_rule.font_size + 4
            else:
                rule.font_size = text_to_html.general_rule.font_size + 10

            text_to_html.add_rule(rule)

            text_to_html.set_text(text)
            lbl_recap.setText(text_to_html.get_html())
            lbl_recap.adjustSize()
            lbl_recap.show()

            y += lbl_recap.height() + 15

            frm_kombs.resize(frm_kombs.width(), y)
            frm_kombs.show()
        
        for widget in main_frame.children():
            if widget.pos().y() > frm_kombs.pos().y():
                widget.move(widget.pos().x(), widget.pos().y() + (frm_kombs.height() - frm_kombs_height))

        main_frame.setFixedSize(main_frame.width(), lbl_summ.pos().y() + lbl_summ.height() + 5)

        h = 10
        for item in range(self.area_widget_layout.count()):
            h += self.area_widget_layout.itemAt(item).widget().height()
        
        self.area_widget.setFixedHeight(h)

    def _get_winning_data(self, loto_komb: dict, round: dict):
        loto_win7 = 0
        loto_win6 = 0
        loto_win5 = 0
        loto_win4 = 0
        loto_win3 = 0
        loto_cost = 0
        loto_plus_cost = 0
        loto_plus_win7 = 0
        joker = 0
        joker_cost = 0

        for komb in loto_komb["numbers"]:
            numbers_hit = self._numbers_hit(komb, round["loto_numbers"])
            if len(numbers_hit) == 7:
                loto_win7 += 1
            elif len(numbers_hit) == 6:
                loto_win6 += 1
            elif len(numbers_hit) == 5:
                loto_win5 += 1
            elif len(numbers_hit) == 4:
                loto_win4 += 1
            elif len(numbers_hit) == 3:
                loto_win3 += 1
            
            loto_cost += self._get_amount(round["lbl_loto_price"])
            
            numbers_hit = self._numbers_hit(komb, round["loto_plus_numbers"])
            if len(numbers_hit) == 7:
                loto_plus_win7 += 1
            
            loto_plus_cost += self._get_amount(round["lbl_loto_plus_price"])

        if loto_komb.get("joker_numbers", None) is not None:
            for komb in loto_komb["joker_numbers"]:
                komb_joker_combination = "".join(komb)
                round_joker_combination = "".join(round["dzoker_numbers"])
                if komb_joker_combination == round_joker_combination:
                    joker = 1
                joker_cost += self._get_amount(round["lbl_dzoker_price"])

        result = {
            "loto_win7": {
                "winnings": loto_win7,
                "amount": self._get_amount(round["lbl_loto_prize_7_amount"]),
                "total": loto_win7 * self._get_amount(round["lbl_loto_prize_7_amount"])
            },
            "loto_win6": {
                "winnings": loto_win6,
                "amount": self._get_amount(round["lbl_loto_prize_6_amount"]),
                "total": loto_win6 * self._get_amount(round["lbl_loto_prize_6_amount"])
            },
            "loto_win5": {
                "winnings": loto_win5,
                "amount": self._get_amount(round["lbl_loto_prize_5_amount"]),
                "total": loto_win5 * self._get_amount(round["lbl_loto_prize_5_amount"])
            },
            "loto_win4": {
                "winnings": loto_win4,
                "amount": self._get_amount(round["lbl_loto_prize_4_amount"]),
                "total": loto_win4 * self._get_amount(round["lbl_loto_prize_4_amount"])
            },
            "loto_win3": {
                "winnings": loto_win3,
                "amount": self._get_amount(round["lbl_loto_prize_3_amount"]),
                "total": loto_win3 * self._get_amount(round["lbl_loto_prize_3_amount"])
            },
            "loto_cost": loto_cost,
            "loto_win_total": None,
            "loto_plus_win7": {
                "winnings": loto_plus_win7,
                "amount": self._get_amount(round["lbl_loto_plus_winers"]),
                "total": loto_plus_win7 * self._get_amount(round["lbl_loto_plus_winers"])
            },
            "loto_plus_cost": loto_plus_cost,
            "joker":{
                "winnings": joker,
                "amount": self._get_amount(round["lbl_dzoker_amount"]),
                "total": joker * self._get_amount(round["lbl_dzoker_amount"])
            },
            "joker_cost": joker_cost
        }

        return result

    def _numbers_hit(self, kombination: list, drawn_numbers: list):
        result = []
        for number in kombination:
            if str(number) in drawn_numbers:
                result.append(number)
        return result

    def _get_amount(self, text: str) -> float:
        html_parser = html_parser_cls.HtmlParser(text)
        text = html_parser.get_raw_text()
        text = text.lower()
        text = text.replace("дин", "")
        text = text.replace("din", "")
        text = text.replace(".", "")
        text = text.replace("цена комбинације", "")
        text = text.replace("cena kombinacije", "")
        text = text.replace("број добитака", "")
        text = text.replace("broj dobitaka", "")
        text = text.replace("iznos dobitka", "")
        text = text.replace("износ добитка", "")
        text = text.replace(",", ".")
        text = text.strip(" ,.")
        return self._get_float(text)

    def _get_float(self, text: str) -> float:
        result = None
        while True:
            if text.find(" ") == -1:
                break
            text = text.replace(" ", "")

        try:
            result = float(text)
        except:
            result = None
        return result

    def _create_view_frame(self):
        w = self.data["width"]
        item_type_text = "Kombinacija" if self.data["item_type"] == "komb" else "Sistemska kombinacija"

        lbl_title = QLabel(self)
        lbl_title.setText(item_type_text)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl_title.setWordWrap(True)
        font = lbl_title.font()
        font.setPointSize(20)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setStyleSheet("color: rgb(0, 255, 0);")
        lbl_title.move(10, 0)
        lbl_title.resize(w - 20, 31)

        lbl_name = QLabel(self)
        lbl_name.setText(self.data["item"]["name"])
        lbl_name.setAlignment(Qt.AlignCenter)
        lbl_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl_name.setWordWrap(True)
        font = lbl_name.font()
        font.setPointSize(14)
        font.setBold(True)
        lbl_name.setFont(font)
        lbl_name.setStyleSheet("color: rgb(170, 255, 255);")
        lbl_name.move(10, 40)
        lbl_name.resize(w - 20, 31)

        min_x = 0
        if self.data["item_type"] == "sys":
            btn_select_sys_numbers = QPushButton(self)
            btn_select_sys_numbers.setText("Izaberi sistemske brojeve")
            btn_select_sys_numbers.clicked.connect(self._on_select_sys_numbers_clicked)
            font = btn_select_sys_numbers.font()
            font.setPointSize(14)
            btn_select_sys_numbers.setFont(font)
            btn_select_sys_numbers.resize(270, 31)
            btn_select_sys_numbers.setStyleSheet("QPushButton {background-color: #140b98; color: white; border-radius: 10px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
            btn_select_sys_numbers.move(10, 80)
            min_x = btn_select_sys_numbers.width() + 20
        
        btn_check_current = QPushButton(self)
        btn_check_current.setText("Proveri za tekuće kolo")
        btn_check_current.clicked.connect(self._on_check_current_clicked)
        font = btn_check_current.font()
        font.setPointSize(14)
        btn_check_current.setFont(font)
        btn_check_current.resize(270, 31)
        btn_check_current.setStyleSheet("QPushButton {color: rgb(0, 0, 83); background-color: rgb(170, 255, 127); border-radius: 15px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(0, 67, 0), stop:1 rgb(0, 161, 0)); color: rgb(255, 255, 0)}")
        x = int(w / 2 - btn_check_current.width() - 10)
        if x < min_x:
            x = min_x
        btn_check_current.move(x, 80)

        btn_check_all = QPushButton(self)
        btn_check_all.setText("Proveri za sva kola")
        btn_check_all.clicked.connect(self._on_check_all_clicked)
        btn_check_all.move(btn_check_current.pos().x() + btn_check_current.width() + 20, btn_check_current.pos().y())
        btn_check_all.setFont(font)
        btn_check_all.resize(270, 31)
        btn_check_all.setStyleSheet("QPushButton {color: rgb(0, 0, 83); background-color: rgb(170, 255, 127); border-radius: 15px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(0, 67, 0), stop:1 rgb(0, 161, 0)); color: rgb(255, 255, 0)}")

        y = btn_check_all.pos().y() + btn_check_all.height() + 20

        if self.data["item_type"] == "sys":
            lbl_sys_numbers = QLabel(self)
            lbl_sys_numbers.setText("Sistemski brojevi:")
            lbl_sys_numbers.setTextInteractionFlags(Qt.TextSelectableByMouse)
            font = lbl_sys_numbers.font()
            font.setPointSize(14)
            lbl_sys_numbers.setFont(font)
            lbl_sys_numbers.setStyleSheet("color: rgb(203, 203, 203);")
            lbl_sys_numbers.move(10, y)
            lbl_sys_numbers.resize(w - 20, 31)

            y += 40
            data = {
                "width": w - 20,
                "border": False,
                "numbers": self.data["item"]["sys_selected_numbers"],
                "number_width": 35,
                "number_height": 35,
                "number_image_path": self.getv("ball_white_icon_path"),
                "has_cancel": False
            }
            frm_sys_numbers = Numbers(self, self._stt, data)
            frm_sys_numbers.move(10, y)
            y += frm_sys_numbers.height() + 10
        
        lbl_kombs = QLabel(self)
        lbl_kombs.setText("Kombinacije:")
        lbl_kombs.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = lbl_kombs.font()
        font.setPointSize(14)
        lbl_kombs.setFont(font)
        lbl_kombs.setStyleSheet("color: rgb(203, 203, 203);")
        lbl_kombs.move(10, y)
        lbl_kombs.resize(w - 20, 31)

        y += 40
        x = 10
        for item in self.data["item"]["numbers"]:
            data = {
                "width": w - 20,
                "border": False,
                "numbers": item,
                "number_width": 25,
                "number_height": 25,
                "number_image_path": self.getv("ball_red_icon_path"),
                "has_cancel": False
            }
            frm_sys_numbers = Numbers(self, self._stt, data)
            frm_sys_numbers.move(x, y)

            x += frm_sys_numbers.width() + 50
            if x + frm_sys_numbers.width() > w:
                x = 10
                y += frm_sys_numbers.height() + 10
        
        y += 30

        if self.data["item"].get("joker_numbers", None):
            x = 10
            for item in self.data["item"]["joker_numbers"]:
                data = {
                    "width": w - 20,
                    "border": False,
                    "numbers": item,
                    "number_width": 35,
                    "number_height": 35,
                    "number_image_path": self.getv("ball_black_icon_path"),
                    "prefix_image": self.getv("joker_logo_icon_path"),
                    "foreground": "#00ff00",
                    "has_cancel": False
                }
                frm_sys_numbers = Numbers(self, self._stt, data)
                frm_sys_numbers.move(x, y)

                x += frm_sys_numbers.width() + 50
                if x + frm_sys_numbers.width() > w:
                    x = 10
                    y += frm_sys_numbers.height() + 10
            
            y += 30

        self.resize(w, y + 10)

    def _on_check_current_clicked(self):
        self.data["feedback_function"](self.data["item"], "show_winnings_current")

    def _on_check_all_clicked(self):
        self.data["feedback_function"](self.data["item"], "show_winnings_all")

    def _on_select_sys_numbers_clicked(self):
        self.frm_numbers_pool = None
        self.max_numbers = self.data["item"]["sys_numbers"]
        self.max_numbers_pool = 39
        
        frm_select_numbers = QFrame(self)
        frm_select_numbers.setFrameShape(QFrame.Box)
        frm_select_numbers.setFrameShadow(QFrame.Plain)
        frm_select_numbers.setLineWidth(1)
        frm_select_numbers.setStyleSheet("border-color: #d40000; border-style: solid; border-width: 1px;")
        frm_select_numbers.move(10, 120)
        
        self.frm_number_pick = self._number_pick_frame()
        self.frm_number_pick.setParent(frm_select_numbers)
        self.frm_number_pick.move(10, 10)
        self.pick_numbers_update_function = self._update_pick_numbers_for_select_sys_numbers

        self.frm_numbers_pool = QFrame(frm_select_numbers)
        self.frm_numbers_pool.setFrameShape(QFrame.NoFrame)
        self.frm_numbers_pool.setFrameShadow(QFrame.Plain)
        self.frm_numbers_pool.setLineWidth(0)
        self.frm_numbers_pool.setStyleSheet("border-width: 0px;")
        self.frm_numbers_pool.move(self.frm_number_pick.width() + 20, 50)
        
        self.btn_update_sys_numbers = QPushButton(frm_select_numbers)
        self.btn_update_sys_numbers.setText("Ažuriraj")
        self.btn_update_sys_numbers.clicked.connect(lambda: self.pick_numbers_update_function("update"))
        font = self.btn_update_sys_numbers.font()
        font.setPointSize(14)
        self.btn_update_sys_numbers.setFont(font)
        self.btn_update_sys_numbers.setStyleSheet("QPushButton {background-color: #140b98; color: white; border-radius: 10px;} QPushButton:hover {background-color: qlineargradient(spread:pad, x1:0, y1:0.00568182, x2:0.98, y2:0.982955, stop:0 rgb(38, 19, 255), stop:1 rgb(150, 207, 207));}")
        self.btn_update_sys_numbers.move(self.frm_number_pick.width() + 20, self.frm_number_pick.pos().y())
        self.btn_update_sys_numbers.resize(150, 30)
        self.btn_update_sys_numbers.setDisabled(True)

        frm_select_numbers.resize(self.width() - 30, self.frm_number_pick.height() + 20)
        self.frm_numbers_pool.resize(frm_select_numbers.width() - (self.frm_number_pick.width() + 30), self.frm_number_pick.height() - (self.btn_update_sys_numbers.height() + 10) - 10)
        frm_select_numbers.show()
        self.resize(self.width(), max(self.height(), frm_select_numbers.height() + 130))
        self.parent_widget.parent().resize_me()

    def _update_pick_numbers_for_select_sys_numbers(self, action: str):
        if action == "update":
            self.selected_numbers.sort()
            self.data["item"]["sys_selected_numbers"] = self.selected_numbers
            self.data["feedback_function"](self.data["item"], "update_sys_numbers")
            return
        
        if not self.frm_numbers_pool:
            return
        
        data = {
            "width": self.frm_numbers_pool.width(),
            "border": False,
            "numbers": self.selected_numbers,
            "number_width": 35,
            "number_height": 35,
            "number_image_path": self.getv("ball_white_icon_path"),
            "has_cancel": False
        }
        frm_sys_numbers = Numbers(self, self._stt, data)
        frm_sys_numbers.setParent(self.frm_numbers_pool)
        frm_sys_numbers.move(0, 0)
        frm_sys_numbers.show()
        if len(self.selected_numbers) == self.max_numbers:
            self.btn_update_sys_numbers.setDisabled(False)
        else:
            self.btn_update_sys_numbers.setDisabled(True)

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
            
            frm_num.enterEvent = lambda event, obj=lbl_pic, image_path=self.getv("online_topic_dls_x_light_icon_path"): self._on_number_enter_event(event, obj, image_path)
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

    def _on_number_enter_event(self, event, lbl_pic: QLabel, image_path: str):
        QCoreApplication.processEvents()
        lbl_pic.setPixmap(QPixmap(image_path))
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

        if self.pick_numbers_update_function is not None:
            self.pick_numbers_update_function(number_list)
            return

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

    def _update_list_of_kombs(self, joker_kombs: bool = False):
        # Delete old widgets
        if joker_kombs:
            for widget in self.frm_list_kombs_joker.children():
                widget.deleteLater()
        else:
            for widget in self.frm_list_kombs.children():
                widget.deleteLater()

        # Populate frame with new widgets
        h_spacing = 50
        v_spacing = 10
        x = 0
        y = 0
        w = self.width() - 20 - self.frm_number_pick.width()
        frm = None
        if joker_kombs:
            self.frm_list_kombs_joker.resize(w, y)
            for komb in self.selected_kombs_joker:
                data = {
                    "border": False,
                    "hor_padding": 0,
                    "ver_padding": 0,
                    "hor_spacing": 10,
                    "ver_spacing": 0,
                    "numbers": komb,
                    "number_width": 35,
                    "number_height": 35,
                    "number_image_path": self.getv("ball_black_icon_path"),
                    "prefix_image": self.getv("joker_logo_icon_path"),
                    "foreground": "#00ff00",
                    "feedback_click_function": self._joker_number_komb_click
                }
                frm = Numbers(self.frm_list_kombs_joker, self._stt, data)
                frm.move(x, y)
                frm.show()
                x += frm.width()
                if x + frm.width() + h_spacing > self.frm_list_kombs_joker.width():
                    x = 0
                    y += frm.height() + v_spacing
                else:
                    x += h_spacing
            
            if x > 0 and frm:
                y += frm.height() + v_spacing

            w = self.width() - 20 - self.frm_number_pick.width()
            self.frm_list_kombs_joker.move(self.frm_number_pick.pos().x() + self.frm_number_pick.width() + 10, self.frm_list_kombs.pos().y() + self.frm_list_kombs.height() + 20)
            self.frm_list_kombs_joker.resize(w, y)
            self.frm_list_kombs_joker.show()
            self.resize(self.width(), max(self.width(), self.frm_list_kombs_joker.pos().y() + self.frm_list_kombs_joker.height() + 10))
            self.parent_widget.parent().resize_me()
        else:
            self.frm_list_kombs.resize(w, y)
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
            if self.frm_list_kombs_joker:
                self.resize(self.width(), max(self.width(), self.frm_list_kombs.pos().y() + self.frm_list_kombs.height() + 10, self.frm_list_kombs_joker.pos().y() + self.frm_list_kombs_joker.height() + 10))
            else:
                self.resize(self.width(), max(self.width(), self.frm_list_kombs.pos().y() + self.frm_list_kombs.height() + 10))
            self.parent_widget.parent().resize_me()

        if self.frm_list_kombs:
            self.frm_list_kombs.move(self.frm_number_pick.pos().x() + self.frm_number_pick.width() + 10, self.btn_save_komb.pos().y() + self.btn_save_komb.height() + 20)
        if self.frm_list_kombs_joker:
            self.frm_list_kombs_joker.move(self.frm_number_pick.pos().x() + self.frm_number_pick.width() + 10, self.frm_list_kombs.pos().y() + self.frm_list_kombs.height() + 20)

    def _number_komb_click(self, number):
        if number in self.selected_kombs:
            self.selected_kombs.remove(number)
        self._update_list_of_kombs()
        if self.selected_kombs:
            self.txt_count_sys_numbers.setDisabled(True)
        else:
            self.txt_count_sys_numbers.setDisabled(False)

    def _joker_number_komb_click(self, number):
        if number in self.selected_kombs_joker:
            self.selected_kombs_joker.remove(number)
        self._update_list_of_kombs(joker_kombs=True)

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
        if self.data["item_type"] == "komb":
            self.selected_kombs = item["numbers"]
        else:
            self.selected_kombs = item["sys_shema"]
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
        
        # Create Joker kombs frame
        self.frm_joker: QFrame = self._create_joker_frame()
        self.frm_joker.move(max(self.lbl_count_sys_numbers.pos().x() + self.lbl_count_sys_numbers.width() + 10, self.txt_count_sys_numbers.pos().x() + self.txt_count_sys_numbers.width() + 10), self.lbl_count_sys_numbers.pos().y())
        
        # Create frame for showing list of kombinations
        self.frm_list_kombs = QFrame(self)
        self.frm_list_kombs.setFrameShape(QFrame.NoFrame)
        self.frm_list_kombs.setFrameShadow(QFrame.Plain)
        self._update_list_of_kombs()

        # Create frame for showing list of joker kombinations
        self.frm_list_kombs_joker = QFrame(self)
        self.frm_list_kombs_joker.setFrameShape(QFrame.NoFrame)
        self.frm_list_kombs_joker.setFrameShadow(QFrame.Plain)
        self._update_list_of_kombs(joker_kombs=True)

        self.resize(self.width(), max(self.frm_number_pick.pos().y() + self.frm_number_pick.height() + 10, self.frm_list_kombs.pos().y() + self.frm_list_kombs.height() + 10))

    def _create_joker_frame(self) -> QFrame:
        frm = QFrame(self)
        frm.setFrameShape(QFrame.Box)
        frm.setFrameShadow(QFrame.Plain)
        frm.setLineWidth(1)

        lbl_title = QLabel(frm)
        lbl_title.setText(self.getl("online_dsl_joker_add_title"))
        lbl_title.setStyleSheet("QLabel {color: #dfdfdf; font-size: 14px;}")
        lbl_title.setTextInteractionFlags(lbl_title.textInteractionFlags() | Qt.TextSelectableByMouse)
        lbl_title.adjustSize()
        lbl_title.move(5, 5)
        y = lbl_title.height() + 10

        txt_joker = QLineEdit(frm)
        txt_joker.setStyleSheet("QLineEdit {font-size: 14px; background-color: rgb(0, 126, 0); color: rgb(255, 255, 0);} QLineEdit:hover {background-color: rgb(0, 163, 0);}")
        txt_joker.setAlignment(Qt.AlignCenter)
        txt_joker.move(5, y)
        txt_joker.resize(110, 25)
        txt_joker.textChanged.connect(lambda _: self._txt_joker_text_changed(text_widget=txt_joker))

        btn_add_joker = QPushButton(frm)
        btn_add_joker.setText(self.getl("online_dsl_joker_add_btn"))
        btn_add_joker.setCursor(Qt.PointingHandCursor)
        btn_add_joker.setStyleSheet("QPushButton {background-color: rgb(0, 126, 0); color: rgb(255, 255, 0);} QPushButton:hover {background-color: rgb(0, 163, 0);}")
        btn_add_joker.move(txt_joker.pos().x() + txt_joker.width() + 5, txt_joker.pos().y())
        btn_add_joker.clicked.connect(lambda _: self._add_joker_btn_add_joker_clicked(text_widget=txt_joker))

        frm.resize(btn_add_joker.pos().x() + btn_add_joker.width() + 5, y + btn_add_joker.height() + 5)
        return frm

    def _add_joker_btn_add_joker_clicked(self, text_widget: QLineEdit):
        numbers = self._joker_numbers_from_text(text_widget=text_widget)
        if numbers is None or numbers in self.selected_kombs_joker:
            return
        self.selected_kombs_joker.append(numbers)
        self._update_list_of_kombs(joker_kombs=True)
    
    def _txt_joker_text_changed(self, text_widget: QLineEdit):
        self._joker_numbers_from_text(text_widget=text_widget)

    def _joker_numbers_from_text(self, text_widget: QLineEdit) -> list:
        default_stylesheet = "QLineEdit {font-size: 14px; background-color: rgb(0, 126, 0); color: rgb(255, 255, 0);} QLineEdit:hover {background-color: rgb(0, 163, 0);}"
        invalid_stylesheet = "QLineEdit {font-size: 14px; background-color: #aa0000; color: rgb(255, 255, 0);} QLineEdit:hover {background-color: #df0000;}"
        komb_exists_stylesheet = "QLineEdit {font-size: 14px; background-color: #8400c6; color: rgb(255, 255, 0);} QLineEdit:hover {background-color: #9a00e7;}"
        text = text_widget.text()
        if text == "":
            text_widget.setStyleSheet(default_stylesheet)
            return None
        
        if "," in text:
            numbers = [x for x in text.split(",")]
        else:
            numbers = [x for x in text if x.isdigit()]

        if len(numbers) != 6:
            text_widget.setStyleSheet(invalid_stylesheet)
            return None
        
        for number in numbers:
            number = self._get_integer(number)
            if number is None or number < 0 or number > 9:
                text_widget.setStyleSheet(invalid_stylesheet)
                return None
        
        if numbers in self.selected_kombs_joker:
            text_widget.setStyleSheet(komb_exists_stylesheet)
        else:
            text_widget.setStyleSheet(default_stylesheet)
        return numbers

    def _txt_count_sys_numbers_text_changed(self):
        value = self._get_integer(self.txt_count_sys_numbers.text())
        if value is None or value < 7 or value > 39:
            if value is not None and value > 39:
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
        item["joker_numbers"] = self.selected_kombs_joker            
        item["sys_numbers"] = self.max_numbers_pool
        item["sys_selected_numbers"] = [x for x in range(1, self.max_numbers_pool + 1)]
        item["sys_shema"] = self.selected_kombs

        if self.data["item_type"] == "komb":
            self.data["feedback_function"](item)
        else:
            self.data["feedback_function"](item, "update_sys_numbers")

        self.hide()
        

class DLS(AbstractTopic):
    LOTO_ARCHIVE_COLOR_COMPLETE = QColor("#00ff00")
    LOTO_ARCHIVE_COLOR_INCOMPLETE = QColor("#ffff00")
    LOTO_ARCHIVE_COLOR_EMPTY = QColor("#f8f8f8")

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
        self.btn_loto_komb_check.clicked.connect(self.btn_loto_komb_check_clicked)

        UTILS.LogHandler.add_log_record("#1: Topic frame loaded.", ["DLS"])

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

    def btn_loto_komb_check_clicked(self):
        kombs = []
        for item in self.settings["loto"]["system"]:
            if item["is_enabled"]:
                kombs.append(item)

        data = {
            "width": self.contentsRect().width() - 320,
            "height": self.parent_widget.get_topic_area_size().height() - (150 + self.frm_loto_komb.pos().y()),
            "type": "winnings",
            "item": None,
            "item_type": None,
            "kombs": kombs,
            "rounds": [self.settings["current_loto"]],
            "feedback_function": self.frm_loto_komb_work_feedback_function
        }
        if self.frm_loto_komb_work:
            self.frm_loto_komb_work.deleteLater()
        self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data)
        self.frm_loto_komb_work.move(290, 140)
        self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
        self.frm_loto_komb_work.show()
        self.resize_me()
        return

    def frm_loto_komb_work_feedback_function(self, data: dict, action: str = None):
        if action == "show_loto_round":
            year = self._get_integer(data["year"])
            rnd = self._get_integer(data["round"])
            if not year or not rnd:
                return
            
            year_round = tuple([str(year), str(rnd)])

            self._load_loto_frame(year_round=year_round)
            return
            # self._update_loto_archive_label_text(self.txt_loto_archive_year.text())

        if action == "progress":
            if data["action"] == "hide":
                self.frm_progress_window.deleteLater()
                QCoreApplication.processEvents()
                return
            if data["action"] == "update":
                prg_progress = None
                for i in self.frm_progress_window.children():
                    if isinstance(i, QProgressBar):
                        prg_progress = i
                        break
                
                if prg_progress:
                    percent = int(data["value"] / data["max_value"] * 100)
                    if percent % data["step"] != 0 or percent == prg_progress.value():
                        return
                    if data["max_value"] != prg_progress.maximum():
                        prg_progress.setMaximum(data["max_value"])
                    prg_progress.setValue(data["value"])
                QCoreApplication.processEvents()
                return
            
            self.frm_progress_window = QFrame(self.frm_loto_komb)
            self.frm_progress_window.setStyleSheet("background-color: #000000; border: 2px solid #ff0000;")
            self.frm_progress_window.move(290, 140)
            self.frm_progress_window.resize(self.contentsRect().width() - 320, 200)
            lbl_title = QLabel(self.frm_progress_window)
            lbl_title.setStyleSheet("color: #ffff00; border: 0px;")
            lbl_title.setText(data["title"])
            font = lbl_title.font()
            font.setPointSize(18)
            lbl_title.setFont(font)
            lbl_title.setAlignment(Qt.AlignCenter)
            lbl_title.setWordWrap(True)
            lbl_title.move(10, 10)
            lbl_title.setFixedWidth(self.frm_progress_window.width() - 20)
            lbl_title.adjustSize()

            lbl_item_name = QLabel(self.frm_progress_window)
            lbl_item_name.setStyleSheet("color: #00ff00; border: 0px;")
            lbl_item_name.setText(data["item_name"])
            font.setPointSize(14)
            lbl_item_name.setFont(font)
            lbl_item_name.setAlignment(Qt.AlignCenter)
            lbl_item_name.setWordWrap(True)
            lbl_item_name.move(10, lbl_title.height() + 10)
            lbl_item_name.setFixedWidth(self.frm_progress_window.width() - 20)
            lbl_item_name.adjustSize()

            prg_progress = QProgressBar(self.frm_progress_window)
            prg_progress.setStyleSheet("border: 0px;")
            prg_progress.setFixedWidth(self.frm_progress_window.width() - 20)
            prg_progress.move(10, lbl_item_name.pos().y() + lbl_item_name.height() + 10)
            prg_progress.setFixedHeight(15)

            self.frm_progress_window.resize(self.frm_progress_window.width(), prg_progress.pos().y() + prg_progress.height() + 10)
            self.frm_progress_window.show()
            QCoreApplication.processEvents()
            return

        if action == "show_winnings_current":
            data_dict = {
                "width": self.contentsRect().width() - 320,
                "height": self.parent_widget.get_topic_area_size().height() - (150 + self.frm_loto_komb.pos().y()),
                "type": "winnings",
                "item": None,
                "item_type": None,
                "kombs": [data],
                "rounds": [self.settings["current_loto"]],
                "feedback_function": self.frm_loto_komb_work_feedback_function
            }
            if self.frm_loto_komb_work:
                self.frm_loto_komb_work.deleteLater()
            self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data_dict)
            self.frm_loto_komb_work.move(290, 140)
            self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
            self.frm_loto_komb_work.show()
            self.resize_me()
            return

        if action == "show_winnings_all":
            rounds = []
            for i in self.settings["loto"]["archive"]:
                rounds.append(i)
            rounds.sort(key=lambda x: x["year"] + " "*(3-len(x["round"])) + x["round"], reverse=True)

            data_dict = {
                "width": self.contentsRect().width() - 320,
                "height": self.parent_widget.get_topic_area_size().height() - (150 + self.frm_loto_komb.pos().y()),
                "type": "winnings",
                "item": None,
                "item_type": None,
                "kombs": [data],
                "rounds": rounds,
                "feedback_function": self.frm_loto_komb_work_feedback_function
            }
            if self.frm_loto_komb_work:
                self.frm_loto_komb_work.deleteLater()
            self.frm_loto_komb_work = WorkingFrame(self.frm_loto_komb, self._stt, data_dict)
            self.frm_loto_komb_work.move(290, 140)
            self.frm_loto_komb.resize(self.width(), max(self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10, self.height()))
            self.frm_loto_komb_work.show()
            self.resize_me()
            return

        if action == "update_sys_numbers":
            sys_num_dict = {str(key+1):value for key, value in enumerate(data["sys_selected_numbers"])}
            item_numbers = []
            for idx, item in enumerate(self.settings["loto"]["system"]):
                if item["name"] == data["name"]:
                    for i in item["sys_shema"]:
                        item_numbers.append([sys_num_dict[str(x)] for x in i])
                    data["numbers"] = item_numbers
        
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

        if action == "update_sys_numbers":
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
                        if self.frm_loto_komb_work.data.get("reserved_names", None) and data["name"] in self.frm_loto_komb_work.data["reserved_names"]:
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
            # if year in self.settings["completed_years"]:
            #     self.btn_loto_archive_search_download.setDisabled(True)
            # else:
            #     self.btn_loto_archive_search_download.setDisabled(False)
            self._update_loto_archive_label_text(year)
            self.frm_loto_archive_search.setVisible(True)

    def _update_loto_archive_label_text(self, year: str):
        list_item = None
        for i in range(self.lst_loto_archive_years.count()):
            if self.lst_loto_archive_years.item(i).text() == year:
                list_item = self.lst_loto_archive_years.item(i)
                break
        else:
            return

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
            list_item.setForeground(self.LOTO_ARCHIVE_COLOR_COMPLETE)
        else:
            text = "Preuzeto #--1 kola."
            text_to_html = utility_cls.TextToHTML(text)
            text_to_html.general_rule.fg_color = "#55ffff"
            rule = utility_cls.TextToHtmlRule(text="#--1", replace_with=str(total_rounds), fg_color="#aaffff")
            text_to_html.add_rule(rule)
            text = text_to_html.get_html()
            list_item.setForeground(self.LOTO_ARCHIVE_COLOR_INCOMPLETE)
        
        if not total_rounds:
            list_item.setForeground(self.LOTO_ARCHIVE_COLOR_EMPTY)

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
            
            has_data = False
            for i in self.settings["loto"]["archive"]:
                if i["year"] == str(year):
                    has_data = True
                    break
            if has_data:
                item.setForeground(self.LOTO_ARCHIVE_COLOR_INCOMPLETE)
            else:
                item.setForeground(self.LOTO_ARCHIVE_COLOR_EMPTY)
            if str(year) in self.settings["completed_years"]:
                item.setForeground(self.LOTO_ARCHIVE_COLOR_COMPLETE)

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
        self._update_loto_archive_label_text(self.txt_loto_archive_year.text())

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
        UTILS.LogHandler.add_log_record("#1: Topic loaded.", ["DLS"])
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
            self._update_loto_archive(data)
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
            "joker_numbers": [],
            "sys_selected_numbers": [],
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
            self.frm_loto_komb.resize(w - 20, max(self.frm_loto_komb.height(), self.frm_loto_komb_work.pos().y() + self.frm_loto_komb_work.height() + 10))

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





