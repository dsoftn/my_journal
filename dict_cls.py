from PyQt5.QtWidgets import (QFrame, QPushButton, QTextEdit, QScrollArea, QWidget, QListWidget, QLabel,
                             QListWidgetItem, QLineEdit, QHBoxLayout, QCheckBox, QRadioButton, QGraphicsOpacityEffect,
                             QSpinBox)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor, QColor, QTextCharFormat
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QTimer, QEvent
from PyQt5 import uic, QtGui

import time
import os
import random
import sqlite3

import settings_cls
import text_handler_cls
import text_handler_cls
import utility_cls
import net_cls
import qwidgets_util_cls
import UTILS


class ImageItem(QFrame):
    def __init__(self, settings: settings_cls.Settings, parent_widget, filename: str, item_id: str, source: str, label: str, online_images: net_cls.Images, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self._online_images = online_images
        self.filename = filename
        self.item_id = item_id
        self.source = source
        self.label = label
        self.parent_widget = parent_widget

        self._define_widgets()

        # Connect events with slots
        self.lbl_pic.mouseDoubleClickEvent = self.lbl_pic_mouse_double_click

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._clear_cm()
        if a0.button() == Qt.RightButton:
            self._show_context_menu()

    def _clear_cm(self) -> None:
        self.get_appv("cm").remove_all_context_menu()

    def _show_context_menu(self):
        clip: utility_cls.Clipboard = self.get_appv("cb")

        disab = []
        if clip.is_clip_empty():
            disab.append(50)

        menu_dict = {
            "position": QCursor.pos(),
            "disabled": disab,
            "separator": [10, 20, 40],
            "items": [
                [
                    10,
                    self.getl("dict_frame_image_menu_open_image_text"),
                    self.getl("dict_frame_image_menu_open_image_tt"),
                    True,
                    [],
                    None
                ],
                [
                    20,
                    self.getl("dict_frame_image_menu_change_image_text"),
                    self.getl("dict_frame_image_menu_change_image_tt"),
                    True,
                    [],
                    self.getv("replace_icon_path")
                ],
                [
                    30,
                    self.getl("picture_view_menu_copy_image_text"),
                    self.getl("picture_view_menu_copy_image_tt"),
                    True,
                    [],
                    self.getv("picture_view_menu_copy_icon_path")
                ],
                [
                    40,
                    self.getl("picture_view_menu_add_to_clip_image_text"),
                    self.getl("picture_view_menu_add_to_clip_image_tt"),
                    True,
                    [],
                    self.getv("picture_view_menu_copy_icon_path")
                ],
                [
                    50,
                    self.getl("image_menu_clear_clipboard_text"),
                    clip.get_tooltip_hint_for_clear_clipboard(),
                    True,
                    [],
                    self.getv("clear_clipboard_icon_path")
                ]
            ]
        }
        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self)
        result = self.get_appv("menu")["result"]
        if result == 10:
            self._open_image()
        elif result == 20:
            self._set_new_image()
        elif result == 30:
            clip.copy_to_clip(self.filename, add_to_clip=False)
        elif result == 40:
            clip.copy_to_clip(self.filename, add_to_clip=True)
        elif result == 50:
            clip.clear_clip()

    def _set_new_image(self):
        count = 1
        count_limit = len(self._online_images.get_image_ids())
        while True:
            self.lbl_pic.setText(self.getl("dict_frame_image_item_loading_text").replace("#1", str(count)).replace("#2", str(count_limit)))
            QCoreApplication.processEvents()
            new_image_id = self._online_images.get_next_image_id_to_show()
            self.item_id = new_image_id
            self.source = self._online_images.get_image_source(new_image_id)
            self.label = self._online_images.get_image_label(new_image_id)
            self.filename = self._online_images.get_image_filename(new_image_id)
            self.lbl_pic.setText("")
            result = self._set_image()
            if result is not None and self.filename is not None:
                break
            if count >= count_limit:
                break
            count += 1

    def _open_image(self):
        try:
            os.startfile(self.filename)
        except:
            print ("Cannot open image !")

    def lbl_pic_mouse_double_click(self, a0: QtGui.QMouseEvent) -> None:
        self._open_image()
        QLabel.mouseDoubleClickEvent(self.lbl_pic, a0)

    def resize_me(self):
        h = self.parent_widget.contentsRect().height()
        self.setFixedSize(h, h)
        self.lbl_pic.resize(self.contentsRect().width(), self.contentsRect().height())

    def refresh_me(self):
        self._set_image()
    
    def _set_image(self):
        img = QPixmap()
        result = img.load(self.filename)
        img = img.scaled(self.lbl_pic.width(), self.lbl_pic.height(), Qt.KeepAspectRatio)
        self.lbl_pic.setPixmap(img)
        self.lbl_pic.setToolTip(f"{self.label}\n\n{self.source}")
        return result

    def _define_widgets(self):
        self.setFixedSize(self.parent_widget.height(), self.parent_widget.height())
        self.lbl_pic: QLabel = QLabel(self)
        self.lbl_pic.resize(self.contentsRect().width(), self.contentsRect().height())
        self.lbl_pic.setScaledContents(False)
        self.lbl_pic.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.lbl_pic.setWordWrap(True)
        self.lbl_pic.setFont(QFont("Comic Sans MS", 18))
        self._set_image()


class DictFrameItem(QFrame):
    INACTIVE_OPACITY = 0.35

    def __init__(self, settings: settings_cls.Settings, parent_widget, name: str, name_desc: str, obj_name: int = None, widget_handler: qwidgets_util_cls.WidgetHandler = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("dict_frame_item_ui_file_path"), self)

        # Define variables
        self.widget_handler = widget_handler
        self._parent_widget: QListWidget = parent_widget
        self._obj_name = obj_name
        self.name = name
        self.name_desc = name_desc
        self._is_active = False
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.signal: utility_cls.Signals = self.get_appv("signal")

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_apperance()

        # Connect events with slots
        self.signal.signal_change_active_dict.connect(self.signal_change_active_dict_event)
        self.lbl_pic.mousePressEvent = self.lbl_pic_mouse_press
        self.lbl_title.mousePressEvent = self.lbl_title_mouse_press

    def register_me_to_widget_handler(self):
        if self.widget_handler is not None:
            wh_setup = {
                "allow_bypass_mouse_press_event": False,
                "allow_bypass_enter_event": False,
                "allow_bypass_leave_event": False
            }
            if self.widget_handler.find_child(self, return_none_if_not_found=True) is None:
                self.widget_handler.add_ActionFrame(self, wh_setup)

    def lbl_pic_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if not self._is_active:
                self._activate_me()
                QCoreApplication.processEvents()
                self.widget_handler.find_child(self).EVENT_mouse_press_event(e)

    def lbl_title_mouse_press(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if not self._is_active:
                self._activate_me()
                QCoreApplication.processEvents()
                self.widget_handler.find_child(self).EVENT_mouse_press_event(e)

    def signal_change_active_dict_event(self, dict_data: dict):
        if dict_data["obj_name"] == self._obj_name:
            if self.name == dict_data["dict_name"]:
                self._is_active = True
                self.effect.setOpacity(1)
            else:
                self._is_active = False
                self.effect.setOpacity(self.INACTIVE_OPACITY)

    def is_active(self) -> bool:
        return self._is_active
    
    def set_active(self, value: bool = True):
        self._is_active = value
        if value:
            self._activate_me()

    def resize_me(self, my_width: int = None):
        if my_width:
            self.resize(my_width, self.height())
        else:
            w = self._parent_widget.contentsRect().width()
            if self._parent_widget.verticalScrollBar().isVisible():
                w -= (self._parent_widget.verticalScrollBar().width() + 5)
            self.setFixedSize(w, self.height())
        self.lbl_title.setFixedSize(self.width() - 80, self.lbl_title.height())

    def enterEvent(self, a0: QEvent) -> None:
        self.setLineWidth(1)
        QCoreApplication.processEvents()
        self.widget_handler.find_child(self).EVENT_enter_event(a0)
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.setLineWidth(0)
        QCoreApplication.processEvents()
        self.widget_handler.find_child(self).EVENT_leave_event(a0)
        return super().leaveEvent(a0)
    
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            if not self._is_active:
                self._activate_me()
                QCoreApplication.processEvents()
                self.widget_handler.find_child(self).EVENT_mouse_press_event(a0)
        return super().mousePressEvent(a0)

    def _activate_me(self):
        self.signal.send_change_active_dict({"dict_name": self.name, "obj_name": self._obj_name, "name_desc": self.name_desc})

    def _get_dict_icon(self, name: str = None) -> str:
        if name is None:
            name = self.name
        
        result = None
        match name:
            case "mit":
                result = self.getv("dict_mit_icon_path")
            case "vujaklija":
                result = self.getv("dict_vujaklija_icon_path")
            case "san":
                result = self.getv("dict_san_icon_path")
            case "zargon":
                result = self.getv("dict_zargon_icon_path")
            case "bos":
                result = self.getv("dict_bos_icon_path")
            case "en-sr":
                result = self.getv("dict_en-sr_icon_path")
            case "psiho":
                result = self.getv("dict_psiho_icon_path")
            case "stari_izrazi":
                result = self.getv("dict_stari_izrazi_icon_path")
            case "filoz":
                result = self.getv("dict_filoz_icon_path")
            case "filoz2":
                result = self.getv("dict_filoz2_icon_path")
            case "emo":
                result = self.getv("dict_emo_icon_path")
            case "biljke":
                result = self.getv("dict_biljke_icon_path")
            case "it":
                result = self.getv("dict_it_icon_path")
            case "bokeljski":
                result = self.getv("dict_bokeljski_icon_path")
            case "bank":
                result = self.getv("dict_bank_icon_path")
            case "google&ms":
                result = self.getv("dict_google&ms_icon_path")
            case "fraze":
                result = self.getv("dict_fraze_icon_path")
            case "ekonom":
                result = self.getv("dict_ekonom_icon_path")
            case "ekonom2":
                result = self.getv("dict_ekonom2_icon_path")
            case "proces":
                result = self.getv("dict_proces_icon_path")
            case "srp_srednji_vek":
                result = self.getv("dict_srp_srednji_vek_icon_path")
            case "sind":
                result = self.getv("dict_sind_icon_path")
            case "religije":
                result = self.getv("dict_religije_icon_path")
            case "svet_mit":
                result = self.getv("dict_svet_mit_icon_path")
            case "arvacki":
                result = self.getv("dict_arvacki_icon_path")
            case "frajer":
                result = self.getv("dict_frajer_icon_path")
            case "astroloski":
                result = self.getv("dict_astroloski_icon_path")
            case "biblija_stari_zavet":
                result = self.getv("dict_biblija_stari_zavet_icon_path")
            case "biblija_novi_zavet":
                result = self.getv("dict_biblija_novi_zavet_icon_path")
            case "bibl_leksikon":
                result = self.getv("dict_bibl_leksikon_icon_path")
            case "tis_mit":
                result = self.getv("dict_tis_mit_icon_path")
            case "dz_pravni":
                result = self.getv("dict_dz_pravni_icon_path")
            case "eponim":
                result = self.getv("dict_eponim_icon_path")
            case "jung":
                result = self.getv("dict_jung_icon_path")
            case "hrt":
                result = self.getv("dict_hrt_icon_path")
            case "imena":
                result = self.getv("dict_imena_icon_path")
            case "kosarka":
                result = self.getv("dict_kosarka_icon_path")
            case "jez_nedoum":
                result = self.getv("dict_jez_nedoum_icon_path")
            case "bibliotek":
                result = self.getv("dict_bibliotek_icon_path")
            case "leksikon_hji":
                result = self.getv("dict_leksikon_hji_icon_path")
            case "lov":
                result = self.getv("dict_lov_icon_path")
            case "polemologija":
                result = self.getv("dict_polemologija_icon_path")
            case "crven_ban":
                result = self.getv("dict_crven_ban_icon_path")
            case "medicina":
                result = self.getv("dict_medicina_icon_path")
            case "medicina_rogic":
                result = self.getv("dict_medicina_rogic_icon_path")
            case "narat":
                result = self.getv("dict_narat_icon_path")
            case "latin":
                result = self.getv("dict_latin_icon_path")
            case "anglicizmi":
                result = self.getv("dict_anglicizmi_icon_path")
            case "onkoloski":
                result = self.getv("dict_onkoloski_icon_path")
            case "pravoslavni_pojmovnik":
                result = self.getv("dict_pravoslavni_pojmovnik_icon_path")
            case "kuran":
                result = self.getv("dict_kuran_icon_path")
            case "arhitekt":
                result = self.getv("dict_arhitekt_icon_path")
            case "latin2":
                result = self.getv("dict_latin2_icon_path")
            case "pirot":
                result = self.getv("dict_pirot_icon_path")
            case "pravni_novinar":
                result = self.getv("dict_pravni_novinar_icon_path")
            case "poslovice":
                result = self.getv("dict_poslovice_icon_path")
            case "turcizmi":
                result = self.getv("dict_turcizmi_icon_path")
            case "urbani":
                result = self.getv("dict_urbani_icon_path")
            case "geografija":
                result = self.getv("dict_geografija_icon_path")
            case "biologija":
                result = self.getv("dict_biologija_icon_path")
            case "slo_mit_encikl":
                result = self.getv("dict_slo_mit_encikl_icon_path")
            case "tehnicki":
                result = self.getv("dict_tehnicki_icon_path")
            case "tolkin":
                result = self.getv("dict_tolkin_icon_path")
            case "istorijski":
                result = self.getv("dict_istorijski_icon_path")
            case "vlaski":
                result = self.getv("dict_vlaski_icon_path")
            case "zakon_krivicni_zakonik":
                result = self.getv("dict_zakon_krivicni_zakonik_icon_path")
            case "zakon_krivicni_postupak":
                result = self.getv("dict_zakon_krivicni_postupak_icon_path")
            case "zakon_o_radu":
                result = self.getv("dict_zakon_o_radu_icon_path")
            case "dusan":
                result = self.getv("dict_dusan_icon_path")
            case "zakon_upravni":
                result = self.getv("dict_zakon_upravni_icon_path")
            case "zakon_razni":
                result = self.getv("dict_zakon_razni_icon_path")
            case "ustav":
                result = self.getv("dict_ustav_icon_path")

        return result

    def _setup_widgets(self):
        self.lbl_pic: QLabel = self.findChild(QLabel, "lbl_pic")
        self.lbl_title: QLabel = self.findChild(QLabel, "lbl_title")

    def _setup_widgets_text(self):
        self.lbl_title.setText("")

    def _setup_apperance(self):
        img = QPixmap()
        img.load(self._get_dict_icon(self.name))
        self.lbl_pic.setPixmap(img)
        self.lbl_pic.setScaledContents(True)
        pic_tt: str = f'<img src="{os.path.abspath(self._get_dict_icon(self.name))}" width = 300>'
        self.lbl_pic.setToolTip(pic_tt)

        self.lbl_title.setText(self.name_desc)
        self.setFixedSize(self._parent_widget.contentsRect().width(), 80)

        self.effect.setOpacity(self.INACTIVE_OPACITY)

    def close_me(self):
        if self.widget_handler:
            self.widget_handler.remove_child(self)


class DictFrame(QFrame):
    BORDER_SIZE = 5
    MIN_VISIBLE_RECT = 100
    AREA_MIN_WIDTH = 100
    LIST_MIN_WIDTH = 50
    ITEM_MIN_WIDTH = 100

    OPTIONS_BUTTON_MIN_OPACITY = 0.1

    def __init__(self, settings: settings_cls.Settings, parent_widget, txt_box: QTextEdit = None, *args, **kwargs):
        super().__init__(parent_widget, *args, **kwargs)
        self.setMouseTracking(True)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("dict_frame_ui_file_path"), self)

        self.installEventFilter(self)

        # Define variables
        self.widget_handler = None
        self._lock_geometry = None
        self._adding_images = False
        self._adding_images_delay = None
        self._online_images = net_cls.Images(self._stt)
        self.images_timer = QTimer(self)
        
        self.stop_adding_images = False
        self._show_images_dict = {}
        self._geometry_change_mode = None
        self._parent_widget = parent_widget
        self.data = DictData(self._stt)
        self.txt_box = txt_box
        self.my_name = time.time_ns() - random.randint(0, 1000000)
        self.page_info = None
        if self.txt_box:
            self.pages = []
            self.current_page = None
        else:
            self.pages: list = self._load_pages()
            if self.pages:
                self.current_page = 0
            else:
                self.current_page = None
        self.current_dict = None
        self.signal: utility_cls.Signals = self.get_appv("signal")
        self.links = []

        self._setup_widgets()
        self._setup_widgets_text()
        self._setup_widgets_apperance()
        self._load_position()

        self.load_widgets_handler()

        cur = self.txt_item.textCursor()
        self.old_cf = cur.charFormat()

        # Connect events with slots
        self.lbl_find.mousePressEvent = self.labels_mouse_press
        self.lbl_result.mousePressEvent = self.labels_mouse_press
        self.lbl_dict_name.mousePressEvent = self.labels_mouse_press
        self.lbl_find.mouseReleaseEvent = self.labels_mouse_release
        self.lbl_result.mouseReleaseEvent = self.labels_mouse_release
        self.lbl_dict_name.mouseReleaseEvent = self.labels_mouse_release
        self.lbl_find.mouseMoveEvent = self.labels_mouse_move
        self.lbl_result.mouseMoveEvent = self.labels_mouse_move
        self.lbl_dict_name.mouseMoveEvent = self.labels_mouse_move
        self.sep_a_l.mousePressEvent = self.sep_a_l_mouse_press
        self.sep_a_l.mouseReleaseEvent = self.sep_a_l_mouse_release
        self.sep_a_l.mouseMoveEvent = self.sep_a_l_mouse_move
        self.sep_l_i.mousePressEvent = self.sep_l_i_mouse_press
        self.sep_l_i.mouseReleaseEvent = self.sep_l_i_mouse_release
        self.sep_l_i.mouseMoveEvent = self.sep_l_i_mouse_move

        self.keyPressEvent = self.key_press_event
        self.btn_close.clicked.connect(self.btn_close_click)
        self.btn_close.mouseMoveEvent = self.btn_close_mouse_move
        self.btn_find.clicked.connect(self.btn_find_click)
        self.btn_find_deep.clicked.connect(self.btn_find_deep_click)
        self.txt_find.returnPressed.connect(self.txt_find_return_pressed)
        self.lst_items.currentItemChanged.connect(self.lst_items_current_item_changed)
        self.lst_items.mousePressEvent = self.lst_items_mouse_press
        self.lst_items.enterEvent = self.lst_items_enter_event
        self.lst_dicts.enterEvent = self.lst_dicts_enter_event
        self.lst_dicts.leaveEvent = self.lst_dicts_leave_event
        self.btn_back.clicked.connect(self.btn_back_click)
        self.btn_back.mousePressEvent = self.btn_back_mouse_press
        self.btn_forward.clicked.connect(self.btn_forward_click)
        self.btn_forward.mousePressEvent = self.btn_forward_mouse_press
        self.txt_item.mouseReleaseEvent = self.txt_item_mouse_release
        self.txt_item_find.textChanged.connect(self.txt_item_find_text_changed)
        self.txt_item_find.keyPressEvent = self.txt_item_find_key_press
        self.txt_dict_find.textChanged.connect(self.txt_dict_find_text_changed)
        self.btn_item_back.clicked.connect(self.btn_item_back_click)
        self.btn_deep_abort.clicked.connect(self.btn_deep_abort_click)

        self.frm_item_opt.mouseMoveEvent = self.frm_item_opt_mouse_move
        self.frm_item_opt.leaveEvent = self.frm_item_opt_leave_event
        self.btn_item_opt_exp.enterEvent = self.btn_item_opt_exp_enter_event
        self.btn_item_opt_exp.leaveEvent = self.btn_item_opt_exp_leave_event
        self.btn_item_opt_exp.clicked.connect(self.btn_item_opt_exp_click)
        self.btn_item_opt_show_images.clicked.connect(self.btn_item_opt_show_images_click)
        self.sep_li_pic.mousePressEvent = self.sep_li_pic_mouse_press
        self.sep_li_pic.mouseReleaseEvent = self.sep_li_pic_mouse_release
        self.sep_li_pic.mouseMoveEvent = self.sep_li_pic_mouse_move
        self.sep_li_pic.enterEvent = self.sep_li_pic_enter_event
        self.sep_li_pic.leaveEvent = self.sep_li_pic_leave_event
        self.btn_item_opt_clear_cashe.clicked.connect(self.btn_item_opt_clear_cashe_click)
        self.btn_lock.clicked.connect(self.btn_lock_click)

        self.signal.signal_change_active_dict.connect(self.signal_change_active_dict_event)

        UTILS.LogHandler.add_log_record("#1: Dictionary frame started.", ["DictFrame"])

    def load_widgets_handler(self):
        self.get_appv("cm").remove_all_context_menu()

        global_properties = self.get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.properties.window_drag_enabled = False


        # Add frames

        # Add all Pushbuttons
        self.widget_handler.add_QPushButton(self.btn_back, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.btn_forward, {"allow_bypass_mouse_press_event": False})
        self.widget_handler.add_QPushButton(self.btn_find)
        self.widget_handler.add_QPushButton(self.btn_find_deep)
        self.widget_handler.add_QPushButton(self.btn_close)
        self.widget_handler.add_QPushButton(self.btn_item_back)
        self.widget_handler.add_QPushButton(self.btn_deep_abort)
        self.widget_handler.add_QPushButton(self.btn_item_opt_exp, {"allow_bypass_enter_event": False, "allow_bypass_leave_event": False})
        self.widget_handler.add_QPushButton(self.btn_item_opt_show_images)
        self.widget_handler.add_QPushButton(self.btn_item_opt_clear_cashe)
        self.widget_handler.add_QPushButton(self.btn_lock)

        # Add Labels as PushButtons

        # Add Action Frames
        # print(self.lst_dicts.count())
        # for index in range(self.lst_dicts.count()):
        #     widget = self.lst_dicts.itemWidget(self.lst_dicts.item(index))
        #     widget.widget_handler = self.widget_handler
        #     widget.register_me_to_widget_handler()

        # Add TextBox
        self.widget_handler.add_TextBox(self.txt_find, {"allow_bypass_key_press_event": True})
        self.widget_handler.add_TextBox(self.txt_item_find, {"allow_bypass_key_press_event": False})
        self.widget_handler.add_TextBox(self.txt_dict_find, {"allow_bypass_key_press_event": True})

        # Add Selection Widgets
        self.widget_handler.add_all_Selection_Widgets()

        # Add Item Based Widgets
        self.widget_handler.add_ItemBased_Widget(self.lst_dicts, {"allow_bypass_enter_event": False, "allow_bypass_leave_event": False})
        self.widget_handler.add_ItemBased_Widget(self.lst_items, {"allow_bypass_enter_event": False, "allow_bypass_mouse_press_event": False})

        self.widget_handler.activate()

    def lst_dicts_enter_event(self, e):
        self.widget_handler.find_child(self.lst_dicts).EVENT_enter_event(e)

        self.setCursor(Qt.PointingHandCursor)
        QListWidget.enterEvent(self.lst_dicts, e)

    def lst_dicts_leave_event(self, e):
        self.widget_handler.find_child(self.lst_dicts).EVENT_leave_event(e)

        self.setCursor(Qt.ArrowCursor)
        QListWidget.leaveEvent(self.lst_dicts, e)

    def lst_items_enter_event(self, e):
        self.widget_handler.find_child(self.lst_items).EVENT_enter_event(e)

        self.setCursor(Qt.ArrowCursor)
        QListWidget.enterEvent(self.lst_items, e)

    def btn_lock_click(self):
        if self._lock_geometry:
            self._lock_geometry = False
        else:
            self._lock_geometry = True
        self._update_lock_btn_style()

    def _update_lock_btn_style(self):
        if self._lock_geometry:
            self.btn_lock.setIcon(QIcon(QPixmap(self.getv("lock_bw_icon_path"))))
            self.btn_lock.setToolTip(self.getl("dict_frame_btn_lock_locked_tt"))
        else:
            self.btn_lock.setIcon(QIcon(QPixmap(self.getv("unlock_bw_icon_path"))))
            self.btn_lock.setToolTip(self.getl("dict_frame_btn_lock_unlocked_tt"))

    def lst_items_mouse_press(self, e: QtGui.QMouseEvent):
        self.widget_handler.find_child(self.lst_items).EVENT_mouse_press_event(e)

        self._clear_cm()
        QListWidget.mousePressEvent(self.lst_items, e)

    def btn_item_opt_clear_cashe_click(self):
        self._online_images.clear_cashe()
        self.btn_item_opt_clear_cashe.setDisabled(True)

    def sep_li_pic_enter_event(self, e):
        self.setCursor(Qt.SizeVerCursor)
        QFrame.enterEvent(self.sep_li_pic, e)

    def sep_li_pic_leave_event(self, e):
        self.setCursor(Qt.ArrowCursor)
        QFrame.leaveEvent(self.sep_li_pic, e)

    def _add_images(self, number_of_images: int = None):
        if number_of_images is None:
            number_of_images = self.spin_item_opt_pic_num.value()
        
        if self._adding_images:
            return
        
        if self._adding_images_delay is None:
            return
        
        self._delete_images_from_layer()

        if self._adding_images_delay > time.time():
            return
        
        self.btn_item_opt_clear_cashe.setDisabled(False)
        self._adding_images_delay = None
        self._adding_images = True

        self.lbl_searching.setVisible(True)
        self.lbl_searching.setText(self.getl("dict_frame_add_images_msg_starting"))
        
        img = QPixmap()
        if self.getv("dict_online_image_search_engine") == 1:
            img.load(self.getv("search_engine_logo_YAHOO"))
        elif self.getv("dict_online_image_search_engine") == 2:
            img.load(self.getv("search_engine_logo_AOL"))
        self.lbl_engine_logo.setPixmap(img)
        self.lbl_engine_logo.setScaledContents(True)
        self.lbl_engine_logo_effects.setOpacity(1)
        self.lbl_engine_logo.setVisible(True)
        self.lbl_internet.setVisible(True)
        
        QCoreApplication.processEvents()

        self.stop_adding_images = False

        if not self.current_dict or self.lst_items.currentItem() is None:
            self._adding_images = False
            return
        
        criteria = self.data.get_criteria_for_online_images(self.current_dict)
        criteria += "::: " + self.lst_items.currentItem().text()

        cur = self.txt_item.textCursor()
        if cur.hasSelection():
            criteria = cur.selection().toPlainText()

        self._online_images.load_image_data(criteria, self.getv("dict_online_image_search_engine"))
        count  = 1
        for item in self._online_images.get_image_ids():
            self.lbl_searching.setText(self.getl("dict_frame_add_images_msg_progress").replace("#1", str(count)).replace("#2", str(number_of_images)))
            self.lbl_engine_logo_effects.setOpacity(1 - (count/number_of_images)*0.9)
            QCoreApplication.processEvents()
            if self.stop_adding_images:
                break
            filename = self._online_images.get_image_filename(item)
            if filename is None:
                continue
            source = self._online_images.get_image_source(item)
            label = self._online_images.get_image_label(item)
            pic_item = ImageItem(self._stt, self.widget_pic, filename=filename, item_id=item, source=source, label=label, online_images=self._online_images)
            self.layout_pic.addWidget(pic_item)
            widget_h = self.area_pic.contentsRect().height()
            if self.area_pic.horizontalScrollBar().isVisible():
                widget_h -= self.area_pic.horizontalScrollBar().height()
            self.widget_pic.resize(self.layout_pic.count() * (self.layout_pic.spacing() + widget_h), widget_h)
            pic_item.resize_me()
            self._resize_me()
            if count >= number_of_images:
                break
            count += 1
        
        self._adding_images = False
        if self.stop_adding_images:
            self._delete_images_from_layer()
            self.stop_adding_images = False
        QCoreApplication.processEvents()
        self.lbl_searching.setVisible(False)
        self.lbl_engine_logo.setVisible(False)
        self.lbl_internet.setVisible(False)

    def _delete_images_from_layer(self):
        self.widget_pic = QWidget()
        self.area_pic.setWidget(self.widget_pic)
        self.layout_pic = QHBoxLayout()
        self.widget_pic.setLayout(self.layout_pic)

    def _refresh_online_images(self):
        for i in range(self.layout_pic.count()):
            self.layout_pic.itemAt(i).widget().refresh_me()

    def btn_item_opt_show_images_click(self):
        self._show_images_frame()
        self._adding_images_delay = 0

    def _show_images_frame(self, value: bool = True):
        if self._adding_images:
            self.stop_adding_images = True
        else:
            if not value:
                self._delete_images_from_layer()
        self.sep_li_pic.setVisible(value)
        self.frm_pic.setVisible(value)
        self._resize_me()

    def _show_images(self):
        if self._adding_images:
            self.stop_adding_images = True
        if self.chk_item_opt_show.isChecked():
            self._show_images_frame(True)
        else:
            self._show_images_frame(False)
            
    def btn_item_opt_exp_click(self):
        if self.frm_item_opt_cont.isVisible():
            self._show_options_frame(False)
            self.btn_item_opt_exp_effects.setOpacity(self.OPTIONS_BUTTON_MIN_OPACITY)
        else:
            self._show_options_frame(True)
            self.btn_item_opt_exp_effects.setOpacity(1)

    def _save_options(self):
        if self.current_dict not in self._show_images_dict:
            self._show_images_dict[self.current_dict] = {}
        
        self._show_images_dict[self.current_dict]["show"] = self.chk_item_opt_show.isChecked()

        if "delay" in self._show_images_dict[self.current_dict]:
            delay = self._show_images_dict[self.current_dict]["delay"]
        else:
            delay = 3
        if self.rbt_item_opt_now.isChecked():
            delay = 0
        elif self.rbt_item_opt_del2.isChecked():
            delay = 2
        elif self.rbt_item_opt_del5.isChecked():
            delay = 5
        elif self.rbt_item_opt_del30.isChecked():
            delay = 30
        elif self.rbt_item_opt_delx.isChecked():
            delay = self.spin_item_opt_delay.value()
        self._show_images_dict[self.current_dict]["delay"] = delay
        self._show_images_dict[self.current_dict]["count"] = self.spin_item_opt_pic_num.value()

    def _load_options(self):
        if self.current_dict not in self._show_images_dict:
            self.chk_item_opt_show.setChecked(False)
            self.rbt_item_opt_now.setChecked(False)
            self.rbt_item_opt_del2.setChecked(False)
            self.rbt_item_opt_del5.setChecked(False)
            self.rbt_item_opt_del30.setChecked(False)
            self.rbt_item_opt_delx.setChecked(True)
            self.spin_item_opt_delay.setValue(3)
            self.spin_item_opt_pic_num.setValue(1)
            return
        
        self.chk_item_opt_show.setChecked(self._show_images_dict[self.current_dict]["show"])
        self.sep_li_pic.setVisible(self._show_images_dict[self.current_dict]["show"])
        self._resize_me()
        if self._show_images_dict[self.current_dict]["delay"] == 0:
            self.rbt_item_opt_now.setChecked(True)
        elif self._show_images_dict[self.current_dict]["delay"] == 2:
            self.rbt_item_opt_del2.setChecked(True)
        elif self._show_images_dict[self.current_dict]["delay"] == 5:
            self.rbt_item_opt_del5.setChecked(True)
        elif self._show_images_dict[self.current_dict]["delay"] == 30:
            self.rbt_item_opt_del30.setChecked(True)
        else:
            self.rbt_item_opt_delx.setChecked(True)
            self.spin_item_opt_delay.setValue(self._show_images_dict[self.current_dict]["delay"])

        self.spin_item_opt_pic_num.setValue(self._show_images_dict[self.current_dict]["count"])

    def btn_item_opt_exp_enter_event(self, e):
        self.widget_handler.find_child(self.btn_item_opt_exp).EVENT_enter_event(e)

        img = QPixmap()
        img.load(self.getv("double_down_expand_icon_path"))
        self.btn_item_opt_exp.setIcon(QIcon(img))
        if not self.frm_item_opt_cont.isVisible():
            self.btn_item_opt_exp_effects.setOpacity(1)
        QPushButton.enterEvent(self.btn_item_opt_exp, e)

    def btn_item_opt_exp_leave_event(self, e):
        self.widget_handler.find_child(self.btn_item_opt_exp).EVENT_leave_event(e)

        img = QPixmap()
        img.load(self.getv("down_expand_icon_path"))
        self.btn_item_opt_exp.setIcon(QIcon(img))
        if not self.frm_item_opt_cont.isVisible():
            self.btn_item_opt_exp_effects.setOpacity(self.OPTIONS_BUTTON_MIN_OPACITY)
        QPushButton.leaveEvent(self.btn_item_opt_exp, e)

    def frm_item_opt_mouse_move(self, e: QtGui.QMouseEvent):
        if not self.frm_item_opt_cont.isVisible():
            w_dist = int(e.pos().x() / (self.frm_item_opt.width() - self.btn_item_opt_exp.width())* 100)
            h_dist = 100 - int((e.pos().y() - self.btn_item_opt_exp.height()) / (self.frm_item_opt.height() - self.btn_item_opt_exp.height())* 100)
            dist = max((w_dist, h_dist)) / 100
            if dist > 1:
                dist = 1
            if dist < self.OPTIONS_BUTTON_MIN_OPACITY:
                dist = self.OPTIONS_BUTTON_MIN_OPACITY
            self.btn_item_opt_exp_effects.setOpacity(dist)
        QFrame.mouseMoveEvent(self.frm_item_opt, e)

    def frm_item_opt_leave_event(self, e):
        self._show_options_frame(False)
        self.btn_item_opt_exp_effects.setOpacity(self.OPTIONS_BUTTON_MIN_OPACITY)
        QFrame.leaveEvent(self.frm_item_opt, e)

    def btn_deep_abort_click(self):
        self.data.abort_operation = True

    def btn_item_back_click(self):
        if self.btn_item_back.isVisible() and self.btn_item_back.objectName():
            goto_row = int(self.btn_item_back.objectName())
            if goto_row >=0 and goto_row <= self.lst_items.count() - 1:
                self.lst_items.setCurrentRow(goto_row)

    def txt_item_find_text_changed(self):
        for i in range(self.lst_items.count()):
            item = self.lst_items.item(i)
            
            item_text = item.text().lower()
            find_text = self.txt_item_find.text().lower()

            for j in [["č", "c"], ["ć", "c"], ["ž", "z"], ["š", "s"], ["đ", "dj"], ["Č", "C"], ["Ć", "C"], ["Ž", "Z"], ["Š", "S"], ["Đ", "DJ"]]:
                item_text = item_text.replace(j[0], j[1])
                find_text = find_text.replace(j[0], j[1])
            
            if item_text.find(find_text) >= 0 or find_text.strip() == "":
                item.setHidden(False)
            else:
                item.setHidden(True)

    def txt_item_find_key_press(self, e: QtGui.QKeyEvent):
        self._clear_cm()
        if (e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return) and e.modifiers() == Qt.ControlModifier:
            for i in range(self.lst_items.count()):
                item = self.lst_items.item(i)
                
                item_text = item.text().lower() + " "
                item_text += self.page_info[self.current_dict][item.text()]["text"]
                find_text = self.txt_item_find.text().lower()

                for j in [["č", "c"], ["ć", "c"], ["ž", "z"], ["š", "s"], ["đ", "dj"], ["Č", "C"], ["Ć", "C"], ["Ž", "Z"], ["Š", "S"], ["Đ", "DJ"]]:
                    item_text = item_text.replace(j[0], j[1])
                    find_text = find_text.replace(j[0], j[1])
                
                if item_text.find(find_text) >= 0 or find_text.strip() == "":
                    item.setHidden(False)
                else:
                    item.setHidden(True)
        else:
            self.widget_handler.find_child(self.txt_item_find).EVENT_key_press_event(e)

        QLineEdit.keyPressEvent(self.txt_item_find, e)

    def txt_dict_find_text_changed(self):
        for i in range(self.lst_dicts.count()):
            item = self.lst_dicts.item(i)
            
            item_text = self.lst_dicts.itemWidget(self.lst_dicts.item(i)).name_desc.lower()
            find_text = self.txt_dict_find.text().lower()

            for j in [["č", "c"], ["ć", "c"], ["ž", "z"], ["š", "s"], ["đ", "dj"], ["Č", "C"], ["Ć", "C"], ["Ž", "Z"], ["Š", "S"], ["Đ", "DJ"]]:
                item_text = item_text.replace(j[0], j[1])
                find_text = find_text.replace(j[0], j[1])
            
            if item_text.find(find_text) >= 0 or find_text.strip() == "":
                item.setHidden(False)
            else:
                item.setHidden(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self._clear_cm()
        return False       

    def txt_item_mouse_release(self, e: QtGui.QMouseEvent):
        self._clear_cm()
        if e.button() == Qt.LeftButton:
            position = self.txt_item.textCursor().position()
            link = None
            curr_item_row = self.lst_items.currentRow()
            for i in self.links:
                if position in range(i[1], i[2] + 1):
                    link = (i[0], i[3])
                    break
            cur = self.txt_item.textCursor()
            if not cur.hasSelection():
                if self._set_curr_list_item(link):
                    self.btn_item_back.setVisible(True)
                    self.btn_item_back.setObjectName(str(curr_item_row))
                    self.lbl_item_name.setText("     " + self.lbl_item_name.text())

        QTextEdit.mousePressEvent(self.txt_item, e)

    def _set_curr_list_item(self, item_text: tuple) -> bool:
        if not item_text:
            return False
        
        for i in range(len(self.lst_items)):
            if self.lst_items.item(i).text().lower() == item_text[1].lower():
                self.lst_items.item(i).setHidden(False)
                self.lst_items.setCurrentRow(i)
                return True
        
        new_item = self.data.get_item(self.current_dict, item_text[1])
        if new_item:
            self.page_info[self.current_dict][new_item["@name"]] = {}
            self.page_info[self.current_dict][new_item["@name"]]["text"] = new_item["text"]
            self.page_info[self.current_dict][new_item["@name"]]["links"] = new_item["links"]
            self.page_info[self.current_dict][new_item["@name"]]["@id"] = new_item["@id"]
            lst_item = QListWidgetItem()
            lst_item.setText(new_item["@name"])
            self.lst_items.addItem(lst_item)
            self.lst_items.setCurrentRow(self.lst_items.count() - 1)
            return True
        return False

    def btn_back_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self.show_context_menu(self.pages)
        elif e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.btn_back).EVENT_mouse_press_event(e)
        QPushButton.mousePressEvent(self.btn_back, e)

    def btn_forward_mouse_press(self, e: QtGui.QMouseEvent):
        if e.button() == Qt.RightButton:
            self.show_context_menu(self.pages)
        elif e.button() == Qt.LeftButton:
            self.widget_handler.find_child(self.btn_forward).EVENT_mouse_press_event(e)
        QPushButton.mousePressEvent(self.btn_forward, e)

    def btn_back_click(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.show_page(self.current_page)
        
    def btn_forward_click(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page(self.current_page)

    def key_press_event(self, e: QtGui.QKeyEvent):
        if e.key() == Qt.Key_Escape:
            if self.get_appv("cm").has_opened_context_menu():
                self.get_appv("cm").remove_all_context_menu()
            else:
                self.hide_me()
        QFrame.keyPressEvent(self, e)

    def btn_close_mouse_move(self, e: QtGui.QMouseEvent):
        self.setCursor(Qt.ArrowCursor)

    def btn_find_click(self):
        self.show_word(self.txt_find.text())

    def btn_find_deep_click(self):
        self.show_word(self.txt_find.text(), deep_search=True)

    def txt_find_return_pressed(self):
        self.show_word(self.txt_find.text())

    def labels_mouse_press(self, a0: QtGui.QMouseEvent) -> None:
        self.mousePressEvent(a0)

    def labels_mouse_release(self, a0: QtGui.QMouseEvent) -> None:
        self.mouseReleaseEvent(a0)

    def labels_mouse_move(self, a0: QtGui.QMouseEvent) -> None:
        self.mouseMoveEvent(a0)

    def sep_li_pic_mouse_press(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self.images_timer.blockSignals(True)
            self._set_change_geometry_mode("sep_li_pic")
            self.sep_a_l.setCursor(Qt.SizeVerCursor)

    def sep_li_pic_mouse_move(self, a0: QtGui.QMouseEvent) -> None:
        if not self._lock_geometry:
            if self._geometry_change_mode:
                new_y = self._geometry_change_mode["widget_y"] + (QCursor.pos().y() - self._geometry_change_mode["cur_y"])
                if new_y < self.txt_item.pos().y() + 50:
                    new_y = self.txt_item.pos().y() + 50
                if new_y > self.contentsRect().height() - 60:
                    new_y = self.contentsRect().height() - 60
                self.sep_li_pic.move(self.sep_li_pic.pos().x(), new_y)
                self._resize_me()

    def sep_li_pic_mouse_release(self, a0: QtGui.QMouseEvent) -> None:
        QCoreApplication.processEvents()
        self._geometry_change_mode = None
        self.images_timer.blockSignals(False)
        self._save_geometry()
        self.setCursor(Qt.ArrowCursor)
        self._refresh_online_images()

    def sep_a_l_mouse_press(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self.images_timer.blockSignals(True)
            self._set_change_geometry_mode("sep_a_l")
            self.sep_a_l.setCursor(Qt.SizeHorCursor)

    def sep_a_l_mouse_release(self, a0: QtGui.QMouseEvent) -> None:
        QCoreApplication.processEvents()
        self._geometry_change_mode = None
        self.images_timer.blockSignals(False)
        self._save_geometry()
        self.setCursor(Qt.ArrowCursor)
        self._refresh_online_images()

    def sep_a_l_mouse_move(self, a0: QtGui.QMouseEvent) -> None:
        if not self._lock_geometry:
            if self._geometry_change_mode:
                new_x = self._geometry_change_mode["widget_x"] + (QCursor.pos().x() - self._geometry_change_mode["cur_x"])
                if new_x < self.lst_dicts.pos().x() + self.AREA_MIN_WIDTH:
                    new_x = self.lst_dicts.pos().x() + self.AREA_MIN_WIDTH
                if new_x > self.sep_l_i.pos().x() - self.LIST_MIN_WIDTH:
                    new_x = self.sep_l_i.pos().x() - self.LIST_MIN_WIDTH
                self.sep_a_l.move(new_x, self.sep_a_l.pos().y())
                self._resize_me()

    def sep_l_i_mouse_press(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self.images_timer.blockSignals(True)
            self._set_change_geometry_mode("sep_l_i")
            self.sep_a_l.setCursor(Qt.SizeHorCursor)

    def sep_l_i_mouse_release(self, a0: QtGui.QMouseEvent) -> None:
        QCoreApplication.processEvents()
        self._geometry_change_mode = None
        self.images_timer.blockSignals(False)
        self._save_geometry()
        self.setCursor(Qt.ArrowCursor)
        self._refresh_online_images()

    def sep_l_i_mouse_move(self, a0: QtGui.QMouseEvent) -> None:
        if not self._lock_geometry:
            if self._geometry_change_mode:
                new_x = self._geometry_change_mode["widget_x"] + (QCursor.pos().x() - self._geometry_change_mode["cur_x"])
                if new_x < self.lst_items.pos().x() + self.LIST_MIN_WIDTH:
                    new_x = self.lst_items.pos().x() + self.LIST_MIN_WIDTH
                if new_x > self.width() - 10 - self.ITEM_MIN_WIDTH:
                    new_x = self.width() - 10 - self.ITEM_MIN_WIDTH
                self.sep_l_i.move(new_x, self.sep_l_i.pos().y())
                self._resize_me()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self.images_timer.blockSignals(True)
            self._set_change_geometry_mode("frame")

        return super().mousePressEvent(a0)

    def _set_change_geometry_mode(self, widget: str):
        loc_cur_pos = self.mapFromGlobal(QCursor.pos())

        self._geometry_change_mode = {"widget": widget, "mode": ""}

        if widget == "sep_a_l":
            self._geometry_change_mode["mode"] = "arange"
            self._geometry_change_mode["widget_x"] = self.sep_a_l.pos().x()
            self._geometry_change_mode["cur_x"] = QCursor.pos().x()
            return

        if widget == "sep_l_i":
            self._geometry_change_mode["mode"] = "arange"
            self._geometry_change_mode["widget_x"] = self.sep_l_i.pos().x()
            self._geometry_change_mode["cur_x"] = QCursor.pos().x()
            return

        if widget == "sep_li_pic":
            self._geometry_change_mode["mode"] = "arange"
            self._geometry_change_mode["widget_y"] = self.sep_li_pic.pos().y()
            self._geometry_change_mode["cur_y"] = QCursor.pos().y()
            return

        if loc_cur_pos.x() < self.BORDER_SIZE:
            self._geometry_change_mode["mode"] += "l"
        if loc_cur_pos.x() > self.width() - self.BORDER_SIZE:
            self._geometry_change_mode["mode"] += "r"
        if loc_cur_pos.y() < self.BORDER_SIZE:
            self._geometry_change_mode["mode"] += "u"
        if loc_cur_pos.y() > self.height() - self.BORDER_SIZE:
            self._geometry_change_mode["mode"] += "d"
        
        if self._geometry_change_mode["mode"]:
            self._geometry_change_mode["type"] = "resize"
        else:
            self._geometry_change_mode["type"] = "move"
        
        self._geometry_change_mode["widget_x"] = self.pos().x()
        self._geometry_change_mode["widget_y"] = self.pos().y()
        self._geometry_change_mode["widget_w"] = self.width()
        self._geometry_change_mode["widget_h"] = self.height()

        self._geometry_change_mode["cur_x"] = QCursor.pos().x()
        self._geometry_change_mode["cur_y"] = QCursor.pos().y()
        if self._geometry_change_mode["type"] == "move":
            self.setCursor(Qt.SizeAllCursor)
        
    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if not self._lock_geometry:
            QCoreApplication.processEvents()
            if not self._geometry_change_mode:
                self._set_cursor_shape()
            else:
                if self._geometry_change_mode["widget"] == "frame":
                    if self._geometry_change_mode["type"] == "move":
                        new_x = self._geometry_change_mode["widget_x"] + QCursor.pos().x() - self._geometry_change_mode["cur_x"]
                        new_y = self._geometry_change_mode["widget_y"] + QCursor.pos().y() - self._geometry_change_mode["cur_y"]
                        if new_x < 0:
                            new_x = 0
                        if new_x > self._parent_widget.contentsRect().width() - self.MIN_VISIBLE_RECT:
                            new_x = self._parent_widget.contentsRect().width() - self.MIN_VISIBLE_RECT
                        if new_y < 0:
                            new_y = 0
                        if new_y > self._parent_widget.contentsRect().height() - self.MIN_VISIBLE_RECT:
                            new_y = self._parent_widget.contentsRect().height() - self.MIN_VISIBLE_RECT
                        self.move(new_x, new_y)
                    elif self._geometry_change_mode["type"] == "resize":
                        if "l" in self._geometry_change_mode["mode"]:
                            new_w = self._geometry_change_mode["widget_w"] + self._geometry_change_mode["cur_x"] - QCursor.pos().x()
                            min_w = self.txt_item.pos().x() + 110
                            max_w = self._geometry_change_mode["widget_x"] + self._geometry_change_mode["widget_w"]
                            if new_w > max_w:
                                new_w = max_w
                            if new_w < min_w:
                                new_w = min_w
                            self.move(self._geometry_change_mode["widget_x"] - (new_w - self._geometry_change_mode["widget_w"]), self.pos().y())
                            self.resize(new_w, self.height())
                        elif "r" in self._geometry_change_mode["mode"]:
                            new_w = self._geometry_change_mode["widget_w"] + QCursor.pos().x() - self._geometry_change_mode["cur_x"]
                            min_w = self.txt_item.pos().x() + 110
                            max_w = self._parent_widget.contentsRect().width() - self._geometry_change_mode["widget_x"]
                            if new_w > max_w:
                                new_w = max_w
                            if new_w < min_w:
                                new_w = min_w
                            self.resize(new_w, self.height())
                        if "u" in self._geometry_change_mode["mode"]:
                            new_h = self._geometry_change_mode["widget_h"] + self._geometry_change_mode["cur_y"] - QCursor.pos().y()
                            min_h = self.txt_item.pos().y() + 110
                            max_h = self._geometry_change_mode["widget_y"] + self._geometry_change_mode["widget_h"]
                            if new_h > max_h:
                                new_h = max_h
                            if new_h < min_h:
                                new_h = min_h
                            self.move(self.pos().x(), self._geometry_change_mode["widget_y"] - (new_h - self._geometry_change_mode["widget_h"]))
                            self.resize(self.width(), new_h)
                        if "d" in self._geometry_change_mode["mode"]:
                            new_h = self._geometry_change_mode["widget_h"] + QCursor.pos().y() - self._geometry_change_mode["cur_y"]
                            min_h = self.txt_item.pos().y() + 110
                            max_h = self._parent_widget.contentsRect().height() - self._geometry_change_mode["widget_y"]
                            if new_h > max_h:
                                new_h = max_h
                            if new_h < min_h:
                                new_h = min_h
                            self.resize(self.width(), new_h)
        return super().mouseMoveEvent(a0)
    
    def _set_cursor_shape(self):
        loc_cur_pos = self.mapFromGlobal(QCursor.pos())
        move_mode = ""

        if loc_cur_pos.x() < self.BORDER_SIZE:
            move_mode += "l"
        if loc_cur_pos.x() > self.width() - self.BORDER_SIZE:
            move_mode += "r"
        if loc_cur_pos.y() < self.BORDER_SIZE:
            move_mode += "u"
        if loc_cur_pos.y() > self.height() - self.BORDER_SIZE:
            move_mode += "d"

        if move_mode == "l" or move_mode == "r":
            self.setCursor(Qt.SizeHorCursor)
        elif move_mode == "u" or move_mode == "d":
            self.setCursor(Qt.SizeVerCursor)
        elif "l" in move_mode and "u" in move_mode:
            self.setCursor(Qt.SizeFDiagCursor)
        elif "r" in move_mode and "d" in move_mode:
            self.setCursor(Qt.SizeFDiagCursor)
        elif "l" in move_mode and "d" in move_mode:
            self.setCursor(Qt.SizeBDiagCursor)
        elif "r" in move_mode and "u" in move_mode:
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        QCoreApplication.processEvents()
        self._geometry_change_mode = None
        self.images_timer.blockSignals(False)
        self.setCursor(Qt.ArrowCursor)
        self._save_geometry()
        self._refresh_online_images()
        return super().mouseReleaseEvent(a0)

    def btn_close_click(self):
        self.hide_me()

    def show_word(self, word: str = None, deep_search: bool = False) -> None:
        if word:
            self.txt_find.setText(word)
        self.lbl_searching.setVisible(True)
        self.lbl_searching.setText(self.getl("dict_frame_lbl_searching_text"))
        self.show_me()
        QCoreApplication.processEvents()
        self.add_page(word)
        QCoreApplication.processEvents()
        self._load_word(word, deep_search=deep_search)
        self._populate_page()
        self.lbl_searching.setVisible(False)
        self._resize_me()

    def _clear_cm(self) -> None:
        self.get_appv("cm").remove_all_context_menu()

    def _load_word(self, word: str, deep_search: bool = False):
        if word is None:
            word = ""
        
        if deep_search:
            UTILS.LogHandler.add_log_record("#1: Serching for expression #2 (DeepSearch=#3).", ["DictFrame", word, deep_search])
            self._show_deep_search_frame()
            self.page_info = self.data.get_dicts_data_deep_search(word)
            self.frm_deep.setVisible(False)
        else:
            UTILS.LogHandler.add_log_record("#1: Serching for expression #2 (DeepSearch=#3).", ["DictFrame", word, deep_search])
            self.page_info = self.data.get_dicts_data(word)

    def _show_deep_search_frame(self):
        self.frm_deep.raise_()
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        
        self.frm_deep.move(0, 0)
        self.frm_deep.resize(w, h)

        self.lbl_deep.move(0, 0)
        self.lbl_deep.resize(w, int(h / 2))

        self.btn_deep_abort.move(int(w / 2 - self.btn_deep_abort.width() / 2), int((h / 5) * 3))

        self.frm_deep.setVisible(True)

    def signal_change_active_dict_event(self, dict_data: str):
        if dict_data["obj_name"] == self.my_name:
            self.current_dict = dict_data["dict_name"]
            self.lbl_item_opt_dict_val.setText(dict_data["name_desc"])
            self._load_options()
            self._populate_dict_items()
            self._populate_list_item()
            self._setup_counters_and_wigets()

    def lst_items_current_item_changed(self):
        self._clear_cm()
        self._populate_list_item()
        self._setup_counters_and_wigets()

    def _populate_page(self, page_info: dict = None):
        if page_info is None:
            page_info = self.page_info
        
        self._populate_dicts(page_info)
        self._populate_dict_items()
        self._populate_list_item()
        self._setup_counters_and_wigets()

    def _populate_dicts(self, page_info: dict = None):
        if page_info is None:
            page_info = self.page_info
        
        for item in range(self.lst_dicts.count()):
            widget = self.lst_dicts.itemWidget(self.lst_dicts.item(item))
            widget.close_me()

        self.lst_dicts.clear()
        self.txt_dict_find.setText("")
        
        for dict_item in page_info:
            dict_widget = DictFrameItem(self._stt, self.lst_dicts, name=dict_item, name_desc=page_info[dict_item]["@name"], obj_name=self.my_name, widget_handler=self.widget_handler)
            dict_widget.register_me_to_widget_handler()
            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(self.lst_dicts.contentsRect().width(), 80))
            self.lst_dicts.addItem(list_item)
            self.lst_dicts.setItemWidget(list_item, dict_widget)

        if page_info:
            self.current_dict = self.lst_dicts.itemWidget(self.lst_dicts.item(0)).name
            self.lbl_item_opt_dict_val.setText(self.page_info[self.current_dict]["@name"])
            self._load_options()
            self.lst_dicts.itemWidget(self.lst_dicts.item(0)).set_active()
        else:
            self.current_dict = None
        self._resize_me()

    def _populate_dict_items(self, dict_name: str = None):
        self.lst_items.clear()
        self.txt_item_find.setText("")
        if self.page_info is None:
            return

        if dict_name is None:
            dict_name = self.current_dict

        if dict_name is None:
            if self.current_dict is None:
                return

        for i in self.page_info[dict_name]:
            if i == "@name" or i == "@desc":
                continue
            item = QListWidgetItem()
            item.setText(i)
            item.setData(Qt.UserRole, self.page_info[dict_name][i]["links"])
            self.lst_items.addItem(item)
        
        if self.lst_items.count():
            self.lst_items.setCurrentRow(0)

    def _populate_list_item(self, item: str = None):
        self.btn_item_back.setVisible(False)
        self.btn_item_back.setObjectName("")
        if item is None:
            if self.lst_items.currentItem() is not None:
                item = self.lst_items.currentItem().text()
            else:
                self.lbl_item_name.setText("")
                self.txt_item.setText("")
                return
        
        self.stop_adding_images = True

        self.lbl_item_name.setText(item)
        
        self.txt_item.selectAll()
        cur = self.txt_item.textCursor()
        cur.setCharFormat(self.old_cf)
        cur.insertText(self.page_info[self.current_dict][item]["text"])
        self.txt_item.setTextCursor(cur)

        self._mark_specific_formats()
        self._mark_links(item)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        self.txt_item.setTextCursor(cur)

        self._set_delay_adding_images()
        self._show_images()

    def _set_delay_adding_images(self):
        if not self.chk_item_opt_show.isChecked():
            self._adding_images_delay = None
            return
        if self.rbt_item_opt_now.isChecked():
            self._adding_images_delay = time.time()
        elif self.rbt_item_opt_del2.isChecked():
            self._adding_images_delay = time.time() + 2
        elif self.rbt_item_opt_del5.isChecked():
            self._adding_images_delay = time.time() + 5
        elif self.rbt_item_opt_del30.isChecked():
            self._adding_images_delay = time.time() + 30
        elif self.rbt_item_opt_delx.isChecked():
            self._adding_images_delay = time.time() + self.spin_item_opt_delay.value()

    def _mark_links(self, item: str):
        self.links = []
        if self.lst_items.currentItem() is None:
            return
        
        item = self.lst_items.currentItem().text()
        self.page_info[self.current_dict][item]["links"] = self.data.get_links_for_item(self.page_info[self.current_dict][item]["@id"])
        links: list = self.page_info[self.current_dict][item]["links"]
        txt: str = self.txt_item.toPlainText()
        if not links:
            return
        
        # end_of_word = [" ", ",", ":", ";", ".", "!", "?", "\n", "\t", "(", ")", "/", "@", "#"]

        txt = UTILS.TextUtility.replace_special_chars(txt)
        # for i in end_of_word:
        #     txt = txt.replace(i, " ")
        
        # Find Links
        txt += " "
        txt = txt.lower()
        for link in links:
            start = 0
            while txt.find(f" {link[0].lower()} ", start) >= 0:
                start = txt.find(f" {link[0].lower()} ", start)
                if start >= 0:
                    self.links.append([link[0], start+1, start+1+len(link[0]), link[1]])
                start += len(link[0]) + 2
        
        # Mark Links
        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        cf.setForeground(QColor("#55ffff"))
        cf.setFontItalic(True)

        for link in self.links:
            cur.setPosition(link[1])
            cur.movePosition(cur.Right, cur.KeepAnchor, len(link[0]))
            cur.setCharFormat(cf)
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _mark_specific_formats(self):
        # DICT biljke - inside parentheses
        if self.current_dict == "biljke":
            self._color_biljke()
        elif self.current_dict == "frajer":
            self._color_frajer()
        elif self.current_dict == "biblija_stari_zavet" or self.current_dict == "biblija_novi_zavet":
            self._color_biblija()
        elif self.current_dict == "imena":
            self._color_imena()
        elif self.current_dict == "anglicizmi":
            self._color_anglicizmi()
        elif self.current_dict == "pirot":
            self._color_pirot()
        elif self.current_dict == "poslovice":
            self._color_poslovice()
        elif self.current_dict == "urbani":
            self._color_urbani()
        elif self.current_dict == "biologija":
            self._color_biologija()
        elif self.current_dict == "slo_mit_encikl":
            self._color_slo_mit_encikl()
        else:
            self._color_generic()
        self._color_search_expression()

    def _color_slo_mit_encikl(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        # color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        # color_tilde.setNamedColor("#7676b0")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 14)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()

        color_map = {
            "italic": {
                "start": "@@@00",
                "end": "@@@00",
                "color": color_subtitle,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "literatura": {
                "start": "@@@01",
                "end": "@@@01",
                "color": color_subtitle_group,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "example": {
                "start": "@@@10",
                "end": "@@@10",
                "color": color_example,
                "container_color": None,
                "font": font_example,
                "map": []
            },
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            }
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            ["*", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["=", QColor("#ffaa00")]
            ]
        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)
        return delete_text

    def _color_biologija(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        # color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        # color_tilde.setNamedColor("#7676b0")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 14)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()

        color_map = {
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota2": {
                "start": "'",
                "end": "'",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "subtitle": {
                "start": "@@@00",
                "end": "@@@00",
                "color": color_subtitle,
                "container_color": None,
                "font": font_standard,
                "map": []
            }
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["=", QColor("#ffaa00")]
            ]
        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)
        return delete_text

    def _color_urbani(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        # color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        # color_tilde.setNamedColor("#7676b0")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 14)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()

        color_map = {
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "italic": {
                "start": "@@@01",
                "end": "@@@01",
                "color": color_slash,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "with_asterix": {
                "start": "@@@00",
                "end": "@@@00",
                "color": color_subtitle_group,
                "container_color": None,
                "font": font_standard,
                "map": []
            }
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["*", QColor("#ffaa00")],
            ["=", QColor("#ffaa00")]
            ]
        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)
        return delete_text

    def _color_poslovice(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        # color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        # color_tilde.setNamedColor("#7676b0")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 12)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()

        color_map = {
            "history_fact": {
                "start": "@@@00",
                "end": "@@@00",
                "color": color_slash,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "author": {
                "start": "@@@01",
                "end": "@@@01",
                "color": color_subtitle_group,
                "container_color": None,
                "font": font_example,
                "map": []
            },
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            }
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["=", QColor("#ffaa00")]
            ]
        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)
        return delete_text

    def _color_search_expression(self, expression: str = None):
        if expression is None:
            expression = self.txt_find.text()
        if not expression:
            return
        
        expression = expression.lower()
        txt = self.txt_item.toPlainText().lower()
        
        cur = self.txt_item.textCursor()
        start = 0
        while txt.find(expression, start) >= 0:
            start = txt.find(expression, start)
            if start >= 0:
                cur = self.txt_item.textCursor()
                cur.setPosition(start)
                cur.movePosition(cur.Right, cur.KeepAnchor, len(expression))
                cf = cur.charFormat()
                cf.setBackground(QColor("#006f00"))
                cur.setCharFormat(cf)
            start += len(expression) + 1
        
        self.txt_item.setTextCursor(cur)
        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _color_pirot(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        # color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        # color_tilde.setNamedColor("#7676b0")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 14)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()

        color_map = {
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "slash": {
                "start": "/",
                "end": "/",
                "color": color_slash,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            }
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["/", QColor("#aaaa7f")],
            ["=", QColor("#ffaa00")]
            ]
        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)
        return delete_text
    
    def _color_anglicizmi(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count("/") % 2 != 0:
                txt_split[idx] = txt_split[idx].replace("/", " ")
            if i.count("'") % 2 != 0:
                txt_split[idx] = txt_split[idx].replace("'", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        # color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        # color_tilde.setNamedColor("#7676b0")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 14)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()

        color_map = {
            "example": {
                "start": "@@@10",
                "end": "@@@10",
                "color": color_example,
                "container_color": None,
                "font": font_example,
                "map": []
            },
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "slash": {
                "start": "/",
                "end": "/",
                "color": color_slash,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota2": {
                "start": "'",
                "end": "'",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            # "tilde": {
            #     "start": "~ ",
            #     "end": " ",
            #     "color": color_tilde,
            #     "container_color": QColor("#54547f"),
            #     "map": []
            # },
            "subtitle_group": {
                "start": "@@@01",
                "end": "@@@01",
                "color": color_subtitle_group,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "subtitle": {
                "start": "@@@00",
                "end": "@@@00",
                "color": color_subtitle,
                "container_color": None,
                "font": font_standard,
                "map": []
            }
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["=", QColor("#ffaa00")]
            ]
        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)
        return delete_text

    def _color_imena(self):
        txt = self.txt_item.toPlainText()
        if not txt:
            return
        
        pos = txt.find("\nNumerolo")
        if pos == -1:
            return
        
        end = txt.find("\n", pos + 1)
        if end == -1:
            return

        cur = self.txt_item.textCursor()
        cur.setPosition(pos)
        cur.movePosition(cur.Right, cur.KeepAnchor, end - pos)
        cf = QTextCharFormat()
        cf.setForeground(QColor("#efef77"))
        cf.setFontPointSize(14)
        cur.setCharFormat(cf)

        cur.setPosition(end)
        cur.movePosition(cur.Right, cur.KeepAnchor, len(txt) - end)
        cf = QTextCharFormat()
        cf.setForeground(QColor("#00ff00"))
        cf.setFontPointSize(16)
        cur.setCharFormat(cf)

        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _color_biblija(self):
        txt = self.txt_item.toPlainText()
        if not txt:
            return
        
        pos = 0
        while True:
            pos = txt.find("*", pos)
            if pos < 1 or pos >= len(txt) - 1:
                break
            
            if txt[:pos].rstrip(" ")[-1] != "\n":
                pos_end = pos + 1
            else:
                pos_end = txt.find("\n", pos)
                if pos_end == -1:
                    pos_end = len(txt)

            cur = self.txt_item.textCursor()
            cur.setPosition(pos)
            cur.movePosition(cur.Right, cur.KeepAnchor, 1)
            cf = QTextCharFormat()
            cf.setForeground(QColor("#00ff00"))
            cf.setFontPointSize(16)
            cur.setCharFormat(cf)

            if pos_end - pos > 1:
                cur.setPosition(pos + 1)
                cur.movePosition(cur.Right, cur.KeepAnchor, pos_end - pos - 1)
                cf.setForeground(QColor("#00ffff"))
                cf.setFontPointSize(14)
                cur.setCharFormat(cf)

            self.txt_item.setTextCursor(cur)
            
            pos = pos_end

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _color_biljke(self):
        txt = self.txt_item.toPlainText()
        if not txt:
            return
        
        pos = 0
        while True:
            pos = txt.find("(", pos)
            if pos < 0 or pos >= len(txt) - 1:
                break
            end = txt.find(")", pos)
            if txt.find("(", pos+1) < end and txt.find("(", pos+1) >= 0:
                pos += 1
                continue
            
            if end < 0:
                break

            if not self._is_biljke_valid_for_coloring(txt[pos+1:end]):
                pos = end
                continue

            cur = self.txt_item.textCursor()
            cur.setPosition(pos+1)
            cur.movePosition(cur.Right, cur.KeepAnchor, end-pos - 1)
            cf = QTextCharFormat()
            cf.setForeground(QColor("#75753a"))
            cf.setFontPointSize(8)
            cur.setCharFormat(cf)
            self.txt_item.setTextCursor(cur)
            
            pos = end

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _color_frajer(self):
        txt = self.txt_item.toPlainText()
        if not txt:
            return
        
        pos = 0
        while True:
            pos = txt.find("/", pos)
            if pos < 0 or pos >= len(txt) - 2:
                break
            end = txt.find("/", pos+1)

            if end < 0:
                end = len(txt)
            
            # exceptions
            excep = [
                ["/ v", "no action", 0],
                ["/ isto", "no action", 0],
                ["/ anal", "no action", 0],
                ["/ u ", "no action", 0],
                ["/ u.", "no action", 0],
                ["/ as", "#aaff7f", 16],
                ["/ sk", "#cfcbff", 12],
                ["/ sl", "#cfcbff", 12],
                ["/ saz", "#44cccc", 12],
                ["/ saž", "#44cccc", 12],
                ["/ konv", "#7e840a", 12],
                ["/ hi", "#959595", 12],
                ["/ inv", "#ffaa7f", 14],
                ["/ od", "#00ff7f", 16],
                ["/ po", "#00ff7f", 16],
                ["/ iz ", "#00ff7f", 16],
                ["/ odgo ", "#75aa98", 16],
                ["/ šalji ", "#75aa98", 16],
                ["/ izraz", "#00d800", 14],
                ["/ aluzi", "#00d800", 14],
                ["/ stari", "#00d800", 14],
                ["/ nadima", "#00d800", 14],
                ["/ iron","#aaaaff", 14],
                ["/ sark", "#aaaaff", 14],
                ["/ pogr", "#ff6387", 14],
                ["/ izv", "#c9ffdf", 12],
                ["/ al", "#ecec75", 16],
                ["/ mn", "#00cb95", 16],

                ["/ nem", "#838383", 8],
                ["/ alb", "#838383", 8],
                ["/ mad", "#838383", 8],
                ["/ mađ", "#838383", 8],
                ["/ lat", "#838383", 8],
                ["/ ger", "#838383", 8],
                ["/ nem", "#838383", 8],
                ["/ ita", "#838383", 8],
                ["/ fr", "#838383", 8],
                ["/ tur", "#838383", 8],
                ["/ amer", "#838383", 8],
                ["/ roni", "#838383", 8],
                ["/ rom", "#838383", 8],
                ["/ eng", "#838383", 8],
                ["/ indo", "#838383", 8],
                ["/ grc", "#838383", 8],
                ["/ grč", "#838383", 8],
                ["/ rus", "#838383", 8]

            ]
            excep.sort(key=lambda x: len(x[0]), reverse=True)

            cf_col_val = "#c2c2c2"
            cf_font_size_val = 13

            can_procced = True
            for i in excep:
                if pos < len(txt) - len(i[0]) and txt[pos:pos+len(i[0])] == i[0]:
                    if i[1] == "no action":
                        pos = end + 1
                        can_procced = False
                        break
                    cf_col_val = i[1]
                    cf_font_size_val = i[2]
                    break
            if not can_procced:
                continue

            cf_col = QColor()
            cf_col.setNamedColor(cf_col_val)
            cf = QTextCharFormat()
            cf.setForeground(cf_col)
            cf.setFontPointSize(cf_font_size_val)

            cur = self.txt_item.textCursor()
            cur.setPosition(pos)
            cur.movePosition(cur.Right, cur.KeepAnchor, end-pos+1)
            cur.setCharFormat(cf)
            self.txt_item.setTextCursor(cur)
            
            pos = end + 1

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _color_generic(self):
        txt = self.txt_item.toPlainText()
        txt_split = [x for x in txt.split("\n")]
        for idx, i in enumerate(txt_split):
            if i.find("[") != -1:
                if i.find("]") == -1:
                    txt_split[idx] = txt_split[idx].replace("[", " ").replace("]", " ")
            if i.count('"') % 2 != 0:
                txt_split[idx] = txt_split[idx].replace('"', " ")
            if i.find(">") != -1:
                if i.find("<") == -1:
                    txt_split[idx] = txt_split[idx].replace(">", " ").replace("<", " ")
        txt = "\n".join(txt_split)

        color_brackets = QColor()
        color_square_brackets = QColor()
        color_slash = QColor()
        color_tilde = QColor()
        color_subtitle = QColor()
        color_subtitle_group = QColor()
        color_container = QColor()
        color_quota = QColor()
        color_example = QColor()
        
        color_brackets.setNamedColor("#ffd607")
        color_square_brackets.setNamedColor("#aaff7f")
        color_slash.setNamedColor("#ffe0ca")
        color_tilde.setNamedColor("#aaffff")
        color_subtitle_group.setNamedColor("#00956d")
        color_subtitle.setNamedColor("#78f100")
        color_container.setNamedColor("#ffffff")
        color_quota.setNamedColor("#bcb7ff")
        color_example.setNamedColor("#efffa4")
        font_example = QFont("Comics Sans MS", 14)
        font_example.setItalic(True)
        font_standard = self.old_cf.font()
        font_big = QFont("Comics Sans MS", 18)
        font_big.setBold(True)

        color_map = {
            "00": {
                "start": "@@@00",
                "end": "@@@00",
                "color": color_subtitle,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "01": {
                "start": "@@@01",
                "end": "@@@01",
                "color": color_slash,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "02": {
                "start": "@@@02",
                "end": "@@@02",
                "color": color_subtitle_group,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "04": {
                "start": "@@@04",
                "end": "@@@04",
                "color": color_container,
                "container_color": None,
                "font": font_standard,
                "map": []
            },
            "10": {
                "start": "@@@10",
                "end": "@@@10",
                "color": color_tilde,
                "container_color": None,
                "font": font_big,
                "map": []
            },
            "brackets": {
                "start": "(", 
                "end": ")",
                "color": color_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "square_brackets": {
                "start": "[", 
                "end": "]",
                "color": color_square_brackets,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota1": {
                "start": '"',
                "end": '"',
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "quota3": {
                "start": ">",
                "end": "<",
                "color": color_quota,
                "container_color": color_container,
                "font": font_standard,
                "map": []
            },
            "03": {
                "start": "@@@03",
                "end": "@@@03",
                "color": QColor("#aaff00"),
                "container_color": None,
                "font": font_standard,
                "map": []
            },
        }

        for i in color_map:
            item = color_map[i]
            pos = 0
            while True:
                pos = txt.find(item["start"], pos)
                if pos == -1:
                    break
                end = txt.find(item["end"], pos + len(item["start"]))
                if end == -1:
                    break

                if item["container_color"] != item["color"]:
                    item["map"].append([pos + len(item["start"]), end, item["color"], item["font"]])
                    item["map"].append([pos, pos + len(item["start"]), item["container_color"], item["font"]])
                    item["map"].append([end, end + len(item["end"]), item["container_color"], item["font"]])
                else:
                    item["map"].append([pos, end + len(item["end"]), item["color"], item["font"]])
                
                pos = end + len(item["end"])

        cur = self.txt_item.textCursor()
        cf = QTextCharFormat()
        delete_text = []
        for i in color_map:
            item = color_map[i]
            for j in item["map"]:
                cur.setPosition(j[0])
                cur.movePosition(cur.Right, cur.KeepAnchor, j[1] - j[0])
                if j[2] is None:
                    delete_text.append([j[0], j][1])
                    continue
                cf.setForeground(j[2])
                cf.setFont(j[3])
                cur.setCharFormat(cf)
        
        color_text = [
            [" v. ", QColor("#00b6b6")],
            [" V. ", QColor("#00b6b6")],
            ["~", QColor("#969600")],
            [";", QColor("#aaaa7f")],
            ["=", QColor("#ffaa00")]
            ]
        list_styles = [
            " # ",
            " #. ",
            " #.) ",
            " (#) ",
            " (#.) ",
            "\n# ",
            "\n#. ",
            "\n#.) ",
            "\n(#) ",
            "\n(#.) "
            ]
        for i in range(15):
            for j in list_styles:
                num_str = j.replace("#", str(i))
                color_text.append([num_str, QColor("#d7ffac")])

        changed_txt = f" {txt} "
        for i in color_text:
            item = i[0]
            pos = 0
            while True:
                if pos > len(changed_txt) - 2:
                    break
                pos = changed_txt.find(item, pos)
                if pos == -1:
                    break
                end = pos + len(item)
                if end > len(changed_txt) - 2:
                    end = len(changed_txt) - 2
                if pos == 0:
                    start = 0
                else:
                    start = pos - 1
                cur.setPosition(start)

                cur.movePosition(cur.Right, cur.KeepAnchor, len(item.rstrip()))
                cf.setForeground(i[1])
                cf.setFont(font_standard)
                cur.setCharFormat(cf)
                pos = pos + len(item)

        delete_text.sort(key=lambda x: x[0], reverse=True)

        for i in delete_text:
            cur.setPosition(i[0])
            cur.movePosition(cur.Right, cur.KeepAnchor, i[1] - i[0])
            cur.insertText("")
            for idx, j in enumerate(self.links):
                if j[1] >= i[0]:
                    self.links[idx][1] = self.links[idx][1] - (i[1] - i[0])
                    self.links[idx][2] = self.links[idx][2] - (i[1] - i[0])
        
        self.txt_item.setTextCursor(cur)

        cur = self.txt_item.textCursor()
        cur.setPosition(0)
        cur.setCharFormat(self.old_cf)
        self.txt_item.setTextCursor(cur)

    def _is_biljke_valid_for_coloring(self, txt) -> bool:
        if txt.find("čl.") >= 0:
            return False
        
        for i in ".,!":
            if txt.find(i) >=0:
                return True
        return False

    def _setup_counters_and_wigets(self):
        self.btn_item_back.setVisible(False)
        self.btn_item_back.setObjectName("")
        if self.page_info is None:
            return

        if self.current_page is not None:
            self.btn_forward.setEnabled(self.current_page > 0)
            self.btn_back.setEnabled(self.current_page < len(self.pages)-1)
        else:
            self.btn_forward.setEnabled(False)
            self.btn_back.setEnabled(False)

        count = 0
        for i in self.page_info:
            count += len(self.page_info[i]) - 2
        self.lbl_result.setText(self.getl("dict_frame_lbl_result_text").replace("#1", str(count)))
        self.lbl_count.setText(self.getl("dict_frame_lbl_count_text").replace("#1", str(self.lst_dicts.count())).replace("#2", str(self.data.count_all_dicts())))

        self.lbl_items.setText(self.getl("dict_frame_lbl_items_text").replace("#1", str(self.lst_items.count())))

        if self.current_dict:
            self.lbl_dict_name.setText(self.page_info[self.current_dict]["@name"])
            self.lbl_dict_name.setToolTip(self.page_info[self.current_dict]["@desc"])
        else:
            self.lbl_dict_name.setText("")
            self.lbl_dict_name.setToolTip("")

    def show_me(self):
        self.images_timer.timeout.connect(self._add_images)
        self.images_timer.start(300)
        self.setVisible(True)
        UTILS.LogHandler.add_log_record("#1: Dictionary frame is visible.", ["DictFrame"])

    def hide_me(self):
        self.images_timer.stop()
        self._save_options()
        self._clear_cm()
        self.setVisible(False)
        UTILS.LogHandler.add_log_record("#1: Dictionary frame is hidden.", ["DictFrame"])

    def add_page(self, text: str):
        if text is None:
            text = ""
        
        if text in self.pages:
            self.pages.pop(self.pages.index(text))

        self.pages.insert(0, text)
        self.current_page = 0
        while len(self.pages) > self.getv("dict_frame_max_number_of_saved_words"):
            if not self.pages:
                break
            self.pages.pop(len(self.pages) - 1)
    
    def show_page(self, page_to_show: int):
        word = self.pages[page_to_show]
        self.lbl_searching.setVisible(True)
        QCoreApplication.processEvents()
        self.txt_find.setText(word)
        self._load_word(word)
        self._populate_page()

        if self.current_page < len(self.pages) - 1:
            self.btn_back.setToolTip(self.getl("dict_frame_btn_back_tt").replace("#1", self.pages[self.current_page+1]))
        else:
            self.btn_back.setToolTip("")
        if self.current_page > 0:
            self.btn_forward.setToolTip(self.getl("dict_frame_btn_forward_tt").replace("#1", self.pages[self.current_page-1]))
        else:
            self.btn_forward.setToolTip("")

        self.lbl_searching.setVisible(False)

    def _load_pages(self) -> list:
        if "dict_frame_pages" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("dict_frame_pages", [], save_to_file=True)
        return self.get_appv("dict_frame_pages")

    def show_context_menu(self, word_list: list) -> dict:
        menu_dict = {
            "position": QCursor.pos(),
            "items": self._create_menu_items_for_word_list(word_list)
        }
        self.set_appv("menu", menu_dict)
        utility_cls.ContextMenu(self._stt, self._parent_widget)
        result = self.get_appv("menu")["result"]
        if result is not None:
            self.show_page(result)

    def _create_menu_items_for_word_list(self, word_list: list, start_from: int = 0, number_of_items_per_menu: int = 25):
        result = []
        active = False
        counter = 0
        for i in range(len(word_list)):
            if i == start_from:
                active = True
            if active:
                if counter >= number_of_items_per_menu:
                    item = self._create_menu_item_for_word_list("", -1, create_next_item=True)
                    item[4] = self._create_menu_items_for_word_list(word_list=word_list, start_from=i, number_of_items_per_menu=number_of_items_per_menu)
                    result.append(item)
                    active = False
                if active:
                    result.append(self._create_menu_item_for_word_list(f'{i+1}. - {word_list[i]}', i))
                    counter += 1

        return result
    
    def _create_menu_item_for_word_list(self, text: str, id: int, clicable: bool = True, create_next_item: bool = False) -> list:
        if create_next_item:
            result = [
                id,
                self.getl("dict_frame_menu_item_next_text"),
                self.getl("dict_frame_menu_item_next_tt"),
                False,
                [],
                self.getv("continue_icon_path")
            ]
        else:
            result = [
                id,
                text,
                "",
                clicable,
                [],
                None
            ]
        return result

    def _show_options_frame(self, value: bool = True):
        self.frm_item_opt_cont.setVisible(value)
        self.btn_item_opt_show_images.setVisible(value)
        
        if value:
            self.frm_item_opt.resize(self.frm_item_opt.width(), 300)
            self._load_options()
            self.frm_item_opt_effects.setOpacity(1)
        else:
            self.frm_item_opt.resize(self.frm_item_opt.width(), 60)
            self._save_options()
            self.frm_item_opt_effects.setOpacity(0)

    def _load_position(self) -> None:
        if "dict_frame_geometry" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("dict_frame_geometry", {}, save_to_file=True)
        
        x = self.get_appv("dict_frame_geometry").setdefault("x", 100)
        y = self.get_appv("dict_frame_geometry").setdefault("y", 100)
        w = self.get_appv("dict_frame_geometry").setdefault("width", 1030)
        h = self.get_appv("dict_frame_geometry").setdefault("height", 570)
        sep_a_l_x = self.get_appv("dict_frame_geometry").setdefault("sep_a_l_x", 307)
        sep_l_i_x = self.get_appv("dict_frame_geometry").setdefault("sep_l_i_x", 565)
        sep_li_pic = self.get_appv("dict_frame_geometry").setdefault("sep_li_pic", 350)
        self._show_images_dict = self.get_appv("dict_frame_geometry").setdefault("show_images_dict", {})
        self._lock_geometry = self.get_appv("dict_frame_geometry").setdefault("lock_geometry", False)
        self._update_lock_btn_style()

        self.move(x, y)
        self.resize(w, h)
        self.sep_a_l.move(sep_a_l_x, self.sep_a_l.pos().y())
        self.sep_l_i.move(sep_l_i_x, self.sep_l_i.pos().y())
        self.sep_li_pic.move(self.sep_li_pic.pos().x(), sep_li_pic)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_me()
        return super().closeEvent(a0)

    def close_me(self):
        self.hide_me()
        
        self._save_geometry()

        UTILS.LogHandler.add_log_record("#1: Dictionary frame closed.", ["DictFrame"])
        self.get_appv("cm").remove_all_context_menu()
        UTILS.DialogUtility.on_closeEvent(self)

    def _save_geometry(self):
        self.get_appv("dict_frame_geometry")["x"] = self.pos().x()
        self.get_appv("dict_frame_geometry")["y"] = self.pos().y()
        self.get_appv("dict_frame_geometry")["width"] = self.width()
        self.get_appv("dict_frame_geometry")["height"] = self.height()
        self.get_appv("dict_frame_geometry")["sep_a_l_x"] = self.sep_a_l.pos().x()
        self.get_appv("dict_frame_geometry")["sep_l_i_x"] = self.sep_l_i.pos().x()
        self.get_appv("dict_frame_geometry")["sep_li_pic"] = self.sep_li_pic.pos().y()
        self.get_appv("dict_frame_geometry")["show_images_dict"] = self._show_images_dict
        self.get_appv("dict_frame_geometry")["lock_geometry"] = self._lock_geometry

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._resize_me()
        return super().resizeEvent(a0)

    def _resize_me(self):
        w = self.contentsRect().width()
        h = self.contentsRect().height()
        sep_a_l_x = self.sep_a_l.pos().x() + 3
        sep_l_i_x = self.sep_l_i.pos().x()

        self.lst_dicts.resize(sep_a_l_x - 10, h - 130)
        self.txt_dict_find.resize(self.lst_dicts.width(), self.txt_dict_find.height())

        self.lst_items.move(sep_a_l_x, self.lst_items.pos().y())
        self.lst_items.resize(sep_l_i_x - sep_a_l_x, h - 130)

        self.lbl_items.move(self.lst_items.pos().x(), self.lbl_items.pos().y())
        self.lbl_items.resize(self.lst_items.width(), self.lbl_items.height())

        self.txt_item_find.move(self.lst_items.pos().x(), self.txt_item_find.pos().y())
        self.txt_item_find.resize(self.lst_items.width(), self.txt_item_find.height())

        self.line.resize(w - 20, self.line.height())

        self.lbl_dict_name.move(sep_l_i_x + 5, self.lbl_dict_name.pos().y())
        self.lbl_dict_name.resize(w - (sep_l_i_x + 5) - 10, self.lbl_dict_name.height())

        self.lbl_item_name.move(sep_l_i_x + 5, self.lbl_item_name.pos().y())
        self.lbl_item_name.resize(w - (sep_l_i_x + 5) - 10, self.lbl_item_name.height())

        self.btn_item_back.move(self.lbl_item_name.pos().x(), self.lbl_item_name.pos().y())

        self.sep_a_l.resize(self.sep_a_l.width(), h - 90)
        self.sep_l_i.resize(self.sep_l_i.width(), h - 160)

        self.btn_close.move(w - 40, 5)
        self.btn_lock.move(w - 90, 5)

        # Resize Images Frame and txt_item and Separator line img - item
        if self.sep_li_pic.pos().y() > h - 50:
            sep_li_pic_y = h - 50
        else:
            sep_li_pic_y = self.sep_li_pic.pos().y()
        self.sep_li_pic.move(self.lbl_dict_name.pos().x(), sep_li_pic_y)
        self.sep_li_pic.resize(self.lbl_dict_name.width(), self.sep_li_pic.height())

        self.txt_item.move(sep_l_i_x + 5, self.txt_item.pos().y())
        txt_item_h = h - 220
        if self.sep_li_pic.isVisible():
            txt_item_h = self.sep_li_pic.pos().y() - self.txt_item.pos().y()
        self.txt_item.resize(w - (sep_l_i_x + 5) - 10, txt_item_h)

        self.frm_pic.move(self.txt_item.pos().x(), self.sep_li_pic.pos().y() + self.sep_li_pic.height())
        self.frm_pic.resize(self.txt_item.width(), (h - (self.sep_li_pic.pos().y() + self.sep_li_pic.height())) - 10)
        self.area_pic.resize(self.frm_pic.contentsRect().width(), self.frm_pic.contentsRect().height())

        # Move options frame and button
        self.btn_item_opt_exp.move(self.txt_item.pos().x() + self.txt_item.width() - (self.btn_item_opt_exp.width() + 20), self.lbl_item_name.pos().y())
        self.frm_item_opt.move(self.txt_item.pos().x() + self.txt_item.width() - (self.frm_item_opt.width() + 20), self.lbl_item_name.pos().y())

        # Resize Dict Items
        # if self.lst_dicts.verticalScrollBar().isVisible():
        for i in range(self.lst_dicts.count()):
            self.lst_dicts.itemWidget(self.lst_dicts.item(i)).resize_me()

        # Resize Online Images
        if self.area_pic.horizontalScrollBar().isVisible():
            self.widget_pic.setFixedHeight(self.area_pic.contentsRect().height() - self.area_pic.horizontalScrollBar().height())
        else:
            self.widget_pic.setFixedHeight(self.area_pic.contentsRect().height())
        self.lbl_internet.move(self.frm_pic.pos().x() + 10, self.frm_pic.pos().y() + 10)
        QCoreApplication.processEvents()

        self.lbl_engine_logo.move(self.area_pic.pos().x() + self.area_pic.width() - self.lbl_engine_logo.width() - 10, self.area_pic.pos().y() + self.area_pic.height() - self.lbl_engine_logo.height() - 10)

        for i in range(self.layout_pic.count()):
            self.layout_pic.itemAt(i).widget().resize_me()

    def _setup_widgets(self):
        self.lbl_find: QLabel = self.findChild(QLabel, "lbl_find")
        self.lbl_result: QLabel = self.findChild(QLabel, "lbl_result")
        self.lbl_count: QLabel = self.findChild(QLabel, "lbl_count")
        self.lbl_dict_name: QLabel = self.findChild(QLabel, "lbl_dict_name")
        self.lbl_item_name: QLabel = self.findChild(QLabel, "lbl_item_name")
        self.lbl_items: QLabel = self.findChild(QLabel, "lbl_items")
        self.lbl_searching: QLabel = self.findChild(QLabel, "lbl_searching")

        self.txt_find: QLineEdit = self.findChild(QLineEdit, "txt_find")
        self.txt_item_find: QLineEdit = self.findChild(QLineEdit, "txt_item_find")
        self.txt_dict_find: QLineEdit = self.findChild(QLineEdit, "txt_dict_find")
        self.line: QFrame = self.findChild(QFrame, "line")
        self.sep_a_l: QFrame = self.findChild(QFrame, "sep_a_l")
        self.sep_l_i: QFrame = self.findChild(QFrame, "sep_l_i")
        self.lst_dicts: QListWidget = self.findChild(QListWidget, "lst_dicts")
        self.lst_items: QListWidget = self.findChild(QListWidget, "lst_items")
        self.txt_item: QTextEdit = self.findChild(QTextEdit, "txt_item")

        self.frm_deep: QFrame = self.findChild(QFrame, "frm_deep")
        self.lbl_deep: QLabel = self.findChild(QLabel, "lbl_deep")
        self.btn_deep_abort: QPushButton = self.findChild(QPushButton, "btn_deep_abort")

        self.btn_find: QPushButton = self.findChild(QPushButton, "btn_find")
        self.btn_find_deep: QPushButton = self.findChild(QPushButton, "btn_find_deep")
        self.btn_close: QPushButton = self.findChild(QPushButton, "btn_close")
        self.btn_back: QPushButton = self.findChild(QPushButton, "btn_back")
        self.btn_forward: QPushButton = self.findChild(QPushButton, "btn_forward")
        self.btn_item_back: QPushButton = self.findChild(QPushButton, "btn_item_back")

        self.sep_li_pic: QFrame = self.findChild(QFrame, "sep_li_pic")
        self.frm_pic: QFrame = self.findChild(QFrame, "frm_pic")
        self.frm_item_opt: QFrame = self.findChild(QFrame, "frm_item_opt")
        self.frm_item_opt_cont: QFrame = self.findChild(QFrame, "frm_item_opt_cont")

        self.btn_item_opt_show_images: QPushButton = self.findChild(QPushButton, "btn_item_opt_show_images")
        self.btn_item_opt_exp: QPushButton = self.findChild(QPushButton, "btn_item_opt_exp")
        self.lbl_item_opt_dict: QLabel = self.findChild(QLabel, "lbl_item_opt_dict")
        self.lbl_item_opt_dict_val: QLabel = self.findChild(QLabel, "lbl_item_opt_dict_val")
        self.lbl_item_opt_pic_num: QLabel = self.findChild(QLabel, "lbl_item_opt_pic_num")

        self.chk_item_opt_show: QCheckBox = self.findChild(QCheckBox, "chk_item_opt_show")
        self.rbt_item_opt_now: QRadioButton = self.findChild(QRadioButton, "rbt_item_opt_now")
        self.rbt_item_opt_del2: QRadioButton = self.findChild(QRadioButton, "rbt_item_opt_del2")
        self.rbt_item_opt_del5: QRadioButton = self.findChild(QRadioButton, "rbt_item_opt_del5")
        self.rbt_item_opt_del30: QRadioButton = self.findChild(QRadioButton, "rbt_item_opt_del30")
        self.rbt_item_opt_delx: QRadioButton = self.findChild(QRadioButton, "rbt_item_opt_delx")
        self.spin_item_opt_delay: QSpinBox = self.findChild(QSpinBox, "spin_item_opt_delay")
        self.lbl_item_opt_delay_sec: QLabel = self.findChild(QLabel, "lbl_item_opt_delay_sec")

        self.spin_item_opt_pic_num: QSpinBox = self.findChild(QSpinBox, "spin_item_opt_pic_num")

        self.area_pic: QScrollArea = self.findChild(QScrollArea, "area_pic")

        self.widget_pic = QWidget()
        self.layout_pic = QHBoxLayout()
        self.widget_pic.setLayout(self.layout_pic)
        self.area_pic.setWidget(self.widget_pic)

        self.lbl_engine_logo: QLabel = self.findChild(QLabel, "lbl_engine_logo")
        self.btn_item_opt_clear_cashe: QPushButton = self.findChild(QPushButton, "btn_item_opt_clear_cashe")
        self.lbl_internet: QLabel = self.findChild(QLabel, "lbl_internet")

        self.btn_lock: QPushButton = self.findChild(QPushButton, "btn_lock")

    def _setup_widgets_text(self):
        self.lbl_find.setText(self.getl("dict_frame_lbl_find_text"))
        self.lbl_find.setToolTip(self.getl("dict_frame_lbl_find_tt"))

        self.lbl_searching.setText(self.getl("dict_frame_lbl_searching_text"))
        self.lbl_searching.setToolTip(self.getl("dict_frame_lbl_searching_tt"))

        self.lbl_result.setText("")
        self.lbl_result.setToolTip(self.getl("dict_frame_lbl_result_tt"))

        self.lbl_items.setText(self.getl("dict_frame_lbl_items_text"))
        self.lbl_items.setToolTip(self.getl("dict_frame_lbl_items_tt"))

        self.lbl_deep.setText(self.getl("dict_frame_lbl_deep_text"))
        self.lbl_deep.setToolTip("")

        self.txt_dict_find.setPlaceholderText(self.getl("dict_frame_txt_dict_find_placeholder"))
        self.txt_dict_find.setToolTip(self.getl("dict_frame_txt_dict_find_tt"))

        self.txt_item_find.setPlaceholderText(self.getl("dict_frame_txt_item_find_placeholder"))
        self.txt_item_find.setToolTip(self.getl("dict_frame_txt_item_find_tt"))

        self.btn_deep_abort.setText(self.getl("dict_frame_btn_deep_abort_text"))

        self.btn_find.setText(self.getl("dict_frame_btn_find_text"))
        self.btn_find.setToolTip(self.getl("dict_frame_btn_find_tt"))

        self.btn_find_deep.setText(self.getl("dict_frame_btn_find_deep_text"))
        self.btn_find_deep.setToolTip(self.getl("dict_frame_btn_find_deep_tt"))
        
        self.btn_item_back.setToolTip(self.getl("dict_frame_btn_item_back_tt"))

        self.lbl_item_opt_dict.setText(self.getl("dict_frame_lbl_item_opt_dict_text"))
        self.lbl_item_opt_dict.setToolTip(self.getl("dict_frame_lbl_item_opt_dict_tt"))

        self.lbl_item_opt_dict_val.setText("")
        self.lbl_item_opt_dict_val.setToolTip("")

        self.lbl_item_opt_pic_num.setText(self.getl("dict_frame_lbl_item_opt_pic_num_text"))
        self.lbl_item_opt_pic_num.setToolTip(self.getl("dict_frame_lbl_item_opt_pic_num_tt"))

        self.btn_item_opt_show_images.setText(self.getl("dict_frame_btn_item_opt_show_images_text"))
        self.btn_item_opt_show_images.setToolTip(self.getl("dict_frame_btn_item_opt_show_images_tt"))

        self.btn_item_opt_exp.setText("")
        self.btn_item_opt_exp.setToolTip(self.getl("dict_frame_btn_item_opt_exp_tt"))

        self.chk_item_opt_show.setText(self.getl("dict_frame_chk_item_opt_show_text"))
        self.chk_item_opt_show.setToolTip(self.getl("dict_frame_chk_item_opt_show_tt"))

        self.rbt_item_opt_now.setText(self.getl("dict_frame_rbt_item_opt_now_text"))
        self.rbt_item_opt_now.setToolTip(self.getl("dict_frame_rbt_item_opt_now_tt"))

        self.rbt_item_opt_del2.setText(self.getl("dict_frame_rbt_item_opt_del2_text"))
        self.rbt_item_opt_del2.setToolTip(self.getl("dict_frame_rbt_item_opt_del2_tt"))

        self.rbt_item_opt_del5.setText(self.getl("dict_frame_rbt_item_opt_del5_text"))
        self.rbt_item_opt_del5.setToolTip(self.getl("dict_frame_rbt_item_opt_del5_tt"))

        self.rbt_item_opt_del30.setText(self.getl("dict_frame_rbt_item_opt_del30_text"))
        self.rbt_item_opt_del30.setToolTip(self.getl("dict_frame_rbt_item_opt_del30_tt"))

        self.rbt_item_opt_delx.setText(self.getl("dict_frame_rbt_item_opt_delx_text"))
        self.rbt_item_opt_delx.setToolTip(self.getl("dict_frame_rbt_item_opt_delx_tt"))

        self.spin_item_opt_delay.setToolTip(self.getl("dict_frame_spin_item_opt_delay_tt"))

        self.lbl_item_opt_delay_sec.setText(self.getl("dict_frame_lbl_item_opt_delay_sec_text"))
        self.lbl_item_opt_delay_sec.setToolTip(self.getl("dict_frame_lbl_item_opt_delay_sec_tt"))

        self.spin_item_opt_pic_num.setToolTip(self.getl("dict_frame_txt_item_opt_pic_num_tt"))

    def _setup_widgets_apperance(self):
        self._define_labels_apperance(self.lbl_find, "dict_frame_lbl_find")
        self._define_labels_apperance(self.lbl_result, "dict_frame_lbl_result")
        self._define_labels_apperance(self.lbl_count, "dict_frame_lbl_count")
        self._define_labels_apperance(self.lbl_dict_name, "dict_frame_lbl_dict_name")
        self._define_labels_apperance(self.lbl_item_name, "dict_frame_lbl_item_name")
        self._define_labels_apperance(self.lbl_items, "dict_frame_lbl_items")
        self._define_labels_apperance(self.lbl_searching, "dict_frame_lbl_searching")
        self.lbl_searching.setVisible(False)

        self.lst_dicts.setStyleSheet(self.getv("dict_frame_area_dict_stylesheet"))
        self.lst_items.setStyleSheet(self.getv("dict_frame_lst_items_stylesheet"))
        self.txt_item.setStyleSheet(self.getv("dict_frame_txt_item_stylesheet"))
        self.txt_item.setMouseTracking(True)
        self.txt_find.setStyleSheet(self.getv("dict_frame_txt_find_stylesheet"))
        self.txt_item_find.setStyleSheet(self.getv("dict_frame_txt_item_find_stylesheet"))
        self.txt_dict_find.setStyleSheet(self.getv("dict_frame_txt_item_find_stylesheet"))
        self.btn_find.setStyleSheet(self.getv("dict_frame_btn_find_stylesheet"))
        self.btn_find_deep.setStyleSheet(self.getv("dict_frame_btn_find_deep_stylesheet"))
        self.btn_close.setStyleSheet(self.getv("dict_frame_btn_close_stylesheet"))
        self.btn_close.setMouseTracking(True)
        self.btn_back.setStyleSheet(self.getv("dict_frame_btn_back_stylesheet"))
        self.btn_forward.setStyleSheet(self.getv("dict_frame_btn_forward_stylesheet"))
        self.btn_item_back.setStyleSheet(self.getv("dict_frame_btn_item_back_stylesheet"))
        self.btn_lock.setStyleSheet(self.getv("dict_frame_btn_lock_stylesheet"))
        self.btn_item_back.setVisible(False)
        self.btn_item_back.setObjectName("")

        self.sep_a_l.setMouseTracking(True)
        self.sep_l_i.setMouseTracking(True)
        self.sep_a_l.setCursor(Qt.SizeHorCursor)
        self.sep_l_i.setCursor(Qt.SizeHorCursor)

        self.frm_deep.setVisible(False)

        self.setVisible(False)

        self.frm_item_opt_effects = QGraphicsOpacityEffect()
        self.frm_item_opt.setGraphicsEffect(self.frm_item_opt_effects)
        self._show_options_frame(False)
        self.frm_item_opt.setMouseTracking(True)

        self.btn_item_opt_exp_effects = QGraphicsOpacityEffect()
        self.btn_item_opt_exp_effects.setOpacity(self.OPTIONS_BUTTON_MIN_OPACITY)
        self.btn_item_opt_exp.setGraphicsEffect(self.btn_item_opt_exp_effects)

        self.frm_pic.setVisible(False)
        self.sep_li_pic.setVisible(False)

        self.lbl_engine_logo_effects = QGraphicsOpacityEffect()
        self.lbl_engine_logo.setGraphicsEffect(self.lbl_engine_logo_effects)
        self.lbl_engine_logo.setVisible(False)
        self.lbl_engine_logo.setScaledContents(True)
        
        self.lbl_internet.setPixmap(QPixmap(self.getv("internet_icon_path")))
        self.lbl_internet.setScaledContents(True)
        self.lbl_internet.setVisible(False)

    def _define_labels_apperance(self, label: QLabel, name: str) -> None:
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setStyleSheet(self.getv(f"{name}_stylesheet"))


class Words():
    def __init__(self, settings: settings_cls.Settings):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value


class DictData():
    SIMILAR_PERCENT = 85

    """
    [serbian][latin][abc+] - serbian with special characters
    [serbian][latin][abc] - serbian without special characters
    [serbian][dicts][mit] - Kulisic, Srpski Mitoloski Recnik
    [serbian][dicts][vujaklija] - Vujaklija, Recnik Stranih Reci
    [serbian][dicts][san] - Sanovnik
    [serbian][dicts][zargon] - Recnik Zargona
    [serbian][dicts][bos] - Bosanski Recnik
    [serbian][dicts][en-sr] - Englesko-Srpski Recnik
    [serbian][dicts][psiho] - Recnih Psiholoskih Pojmova
    [serbian][dicts][stari_izrazi] - Recnik Starih Izraza
    [serbian][dicts][filoz] - Filozofski Recnik
    [serbian][dicts][emo] - Recnik Emocija
    [serbian][dicts][biljke] - Recnik Narodnih Verovanja o Biljkama
    [serbian][dicts][it] - IT Recnik
    """

    def __init__(self, settings: settings_cls.Settings):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables:
        self.db_name = self.getv("dictionaries_db_file_path")
        self.lang_id = 1
        self.abort_operation = False

    def get_item(self, dict_name: str, item_name: str):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        sql = f"SELECT id FROM dict WHERE name = '{dict_name}';"
        cur.execute(sql)
        result = cur.fetchall()
        dict_id = result[0][0]

        sql = f"SELECT * FROM item WHERE dict_id = {dict_id} AND name = ?;"
        cur.execute(sql, (item_name,))
        result = cur.fetchall()

        if result:
            item_data = {}
            item_data["@name"] = result[0][2]
            item_data["text"] = result[0][3]
            item_data["links"] = None
            item_data["@id"] = result[0][0]
        else:
            item_data = None

        conn.close()
        return item_data

    def get_links_for_item(self, item_id: int) -> list:
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        sql = f"SELECT * FROM link WHERE item_id = {item_id};"
        cur.execute(sql)
        links = cur.fetchall()
        result = [[x[2], x[3]] for x in links]

        conn.close()
        return result

    def get_dicts_data(self, word: str) -> dict:
        text_func = text_handler_cls.TextFunctions(self._stt)
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        sql = f"SELECT * FROM item;"
        cur.execute(sql)
        all_items = cur.fetchall()

        dicts = self.dicts_names()
        empty_dicts = []
        for dict_item in dicts:
            has_data = False

            result = True
            for item in all_items:
                if item[1] != dicts[dict_item]["@id"]:
                    continue

                if word:
                    result = text_func.filter_apply(word, item[2], similar_percent=self.SIMILAR_PERCENT)
                
                if result:
                    dicts[dict_item][item[2]] = {}
                    dicts[dict_item][item[2]]["text"] = item[3]
                    dicts[dict_item][item[2]]["links"] = None
                    dicts[dict_item][item[2]]["@id"] = item[0]
                    has_data = True
            
            if has_data:
                dicts[dict_item].pop("@id")
            else:
                empty_dicts.append(dict_item)
        
        for item in empty_dicts:
            dicts.pop(item)
        
        conn.close()
        return dicts

    def get_dicts_data_deep_search(self, word: str) -> dict:
        self.abort_operation = False
        text_func = text_handler_cls.TextFunctions(self._stt)
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        sql = f"SELECT * FROM item;"
        cur.execute(sql)
        all_items = cur.fetchall()

        dicts = self.dicts_names()
        empty_dicts = []
        count = 0
        prev_percent = 0
        for dict_item in dicts:
            has_data = False

            for item in all_items:
                if self.abort_operation:
                    break

                if item[1] != dicts[dict_item]["@id"]:
                    continue
                
                result = text_func.filter_apply(word, item[2], similar_percent=59)
                if not result:
                    item_text = f" {item[3]} "
                    for i in "!#@$%^&*(_+=-[{}]\"';:.,<>/?~)":
                        item_text = item_text.replace(i, " ")
                    result = text_func.filter_apply(f" {word} ", item_text)

                if result:
                    dicts[dict_item][item[2]] = {}
                    dicts[dict_item][item[2]]["text"] = item[3]
                    dicts[dict_item][item[2]]["links"] = None
                    dicts[dict_item][item[2]]["@id"] = item[0]
                    has_data = True

                count += 1
                if int(count / (len(all_items) + 1) * 100) != prev_percent:
                    prev_percent = int(count / (len(all_items) + 1) * 100)
                    QCoreApplication.processEvents()
                
            if has_data:
                dicts[dict_item].pop("@id")
            else:
                empty_dicts.append(dict_item)
        
        for item in empty_dicts:
            dicts.pop(item)
        
        conn.close()
        self.abort_operation = False
        return dicts

    def dicts_names(self) -> dict:
        shema = self._all_dicts()

        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        sql = f"SELECT name, name_desc, desc, id FROM dict WHERE lang_id = {self.lang_id};"
        cur.execute(sql)
        dicts = cur.fetchall()

        for item in dicts:
            shema[item[0]]["@name"] = item[1]
            shema[item[0]]["@desc"] = item[2]
            shema[item[0]]["@id"] = item[3]

        pop_items = []
        for item in shema:
            if not shema[item]:
                pop_items.append(item)
        for item in pop_items:
            shema.pop(item)

        conn.close()
        return shema

    def get_criteria_for_online_images(self, dict_name: str) -> str:
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        sql = f"SELECT search_string FROM dict WHERE name='{dict_name}';"
        cur.execute(sql)
        result = cur.fetchall()
        return result[0][0]

    def _all_dicts(self) -> dict:
        shema = {
            "vujaklija": {},
            "jez_nedoum": {},
            "anglicizmi": {},
            "pirot": {},
            "narat": {},
            "eponim": {},
            "bibliotek": {},
            "stari_izrazi": {},
            "biljke": {},

            "san": {},
            "imena": {},
            "astroloski": {},

            "medicina": {},
            "medicina_rogic": {},
            "psiho": {},
            "jung": {},
            "emo": {},
            "onkoloski": {},

            "filoz": {},
            "filoz2": {},

            "geografija": {},
            "arhitekt": {},

            "biologija": {},

            "istorijski": {},
            "srp_srednji_vek": {},
            "slo_mit_encikl": {},
            "mit": {},
            "svet_mit": {},
            "tis_mit": {},
            "leksikon_hji": {},
            "religije": {},
            "biblija_stari_zavet": {},
            "biblija_novi_zavet": {},
            "kuran": {},
            "bibl_leksikon": {},
            "pravoslavni_pojmovnik": {},

            "poslovice": {},
            "frajer": {},
            "urbani": {},
            "zargon": {},
            "fraze": {},
            "bos": {},
            "bokeljski": {},
            "arvacki": {},
            "turcizmi": {},
            "vlaski": {},

            "it": {},
            "google&ms": {},
            "tehnicki": {},

            "dz_pravni": {},
            "proces": {},
            "pravni_novinar": {},
            "sind": {},

            "ustav": {},
            "zakon_krivicni_zakonik": {},
            "zakon_krivicni_postupak": {},
            "zakon_upravni": {},
            "zakon_o_radu": {},
            "zakon_razni": {},
            "dusan": {},

            "bank": {},
            "ekonom": {},
            "ekonom2": {},
            "hrt": {},

            "kosarka": {},
            "lov": {},
            "polemologija": {},
            "crven_ban": {},
            "tolkin": {},

            "latin": {},
            "latin2": {},
            "en-sr": {}
        }
        return shema

    def count_all_dicts(self) -> int:
        return len(self._all_dicts())