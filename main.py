from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, QAction, QStatusBar,
                             QToolBar, QScrollArea, QVBoxLayout, QWidget, QLabel)
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QTimer

import sys
import time
import os

import log_cls
import settings_cls
import login_cls
import users_cls
import block_cls
import utility_cls
import db_record_cls
import db_record_data_cls
import tag_cls
import definition_cls
import diary_view_cls
import app_settings_cls
import dict_cls
import online_content_cls
import wikipedia_cls
import definition_data_find_cls


theme_adaptic1 = """/*Copyright (c) DevSec Studio. All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/*-----QWidget-----*/
QWidget
{
	background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(102, 115, 140, 255),stop:1 rgba(56, 63, 77, 255));
	color: #ffffff;
	border-color: #051a39;

}


/*-----QLabel-----*/
QLabel
{
	background-color: transparent;
	color: #ffffff;
	font-weight: bold;

}


QLabel::disabled
{
	background-color: transparent;
	color: #898988;

}


/*-----QMenuBar-----*/
QMenuBar
{
	background-color: #484c58;
	color: #ffffff;
	border-color: #051a39;
	font-weight: bold;

}


QMenuBar::disabled
{
	background-color: #404040;
	color: #898988;
	border-color: #051a39;

}


QMenuBar::item
{
    background-color: transparent;

}


QMenuBar::item:selected
{
    background-color: #c4c5c3;
	color: #000000;
    border: 1px solid #000000;

}


QMenuBar::item:pressed
{
    background-color: #979796;
    border: 1px solid #000;
    margin-bottom: -1px;
    padding-bottom: 1px;

}


/*-----QMenu-----*/
QMenu
{
    background-color: #c4c5c3;
    border: 1px solid;
    color: #000000;
	font-weight: bold;

}


QMenu::separator
{
    height: 1px;
    background-color: #363942;
    color: #ffffff;
    padding-left: 4px;
    margin-left: 10px;
    margin-right: 5px;

}


QMenu::item
{
    min-width : 150px;
    padding: 3px 20px 3px 20px;

}


QMenu::item:selected
{
    background-color: #363942;
    color: #ffffff;

}


QMenu::item:disabled
{
    color: #898988;
}


/*-----QToolTip-----*/
QToolTip
{
	background-color: #bbbcba;
	color: #000000;
	border-color: #051a39;
	border : 1px solid #000000;
	border-radius: 2px;

}


/*-----QPushButton-----*/
QPushButton
{
	background-color: qlineargradient(spread:repeat, x1:0.486, y1:0, x2:0.505, y2:1, stop:0.00480769 rgba(170, 0, 0, 255),stop:1 rgba(122, 0, 0, 255));
	color: #ffffff;
	font-weight: bold;
	border-style: solid;
	border-width: 1px;
	border-radius: 3px;
	border-color: #051a39;
	padding: 5px;

}


QPushButton::disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


QPushButton::hover
{
	background-color: #9c0000;
	color: #ffffff;
	border-style: solid;
	border-width: 1px;
	border-radius: 3px;
	border-color: #051a39;
	padding: 5px;

}


QPushButton::pressed
{
	background-color: #880000;
	color: #ffffff;
	border-style: solid;
	border-width: 2px;
	border-radius: 3px;
	border-color: #000000;
	padding: 5px;

}


/*-----QToolButton-----*/
QToolButton 
{
	background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(177, 181, 193, 255),stop:1 rgba(159, 163, 174, 255));
	color: #ffffff;
	font-weight: bold;
	border-style: solid;
	border-width: 1px;
	border-radius: 3px;
	border-color: #051a39;
	padding: 5px;

}


QToolButton::disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


QToolButton::hover
{
	background-color: #9fa3ae;
	color: #ffffff;
	border-style: solid;
	border-width: 1px;
	border-radius: 3px;
	border-color: #051a39;
	padding: 5px;

}


QToolButton::pressed
{
	background-color: #7b7e86;
	color: #ffffff;
	border-style: solid;
	border-width: 2px;
	border-radius: 3px;
	border-color: #000000;
	padding: 5px;

}


/*-----QComboBox-----*/
QComboBox
{
    background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(118, 118, 118, 255),stop:1 rgba(70, 70, 70, 255));
    border: 1px solid #333333;
    border-radius: 3px;
    padding-left: 6px;
    color: lightgray;
	font-weight: bold;
    height: 20px;

}


QComboBox::disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


QComboBox:hover
{
    background-color: #646464;

}


QComboBox:on
{
    background-color: #979796;
	color: #000000;

}


QComboBox QAbstractItemView
{
    background-color: #c4c5c3;
    color: #000000;
    border: 1px solid black;
    selection-background-color: #363942;
    selection-color: #ffffff;
    outline: 0;

}


QComboBox::drop-down
{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 1px;
    border-left-color: darkgray;
    border-left-style: solid; 
    border-top-right-radius: 3px; 
    border-bottom-right-radius: 3px;

}


QComboBox::down-arrow
{
    image: url(://arrow-down.png);
    width: 8px;
    height: 8px;
}


/*-----QSpinBox & QDoubleSpinBox & QDateTimeEdit-----*/
QSpinBox, 
QDoubleSpinBox,
QDateTimeEdit
{
	background-color: #000000;
	color: #00ff00;
	font-weight: bold;
	border: 1px solid #333333;
	padding : 4px;

}


QSpinBox::disabled, 
QDoubleSpinBox::disabled,
QDateTimeEdit::disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


QSpinBox:hover, 
QDoubleSpinBox::hover,
QDateTimeEdit::hover
{
    border: 1px solid #00ff00;

}


QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QDateTimeEdit::up-button, QDateTimeEdit::down-button
{
	background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(118, 118, 118, 255),stop:1 rgba(70, 70, 70, 255));
    border: 0px solid #333333;

}


QSpinBox::disabled, 
QDoubleSpinBox::disabled,
QDateTimeEdit::disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover,
QDateTimeEdit::up-button:hover, QDateTimeEdit::down-button:hover
{
	background-color: #646464;
    border: 1px solid #333333;


}


QSpinBox::up-button:disabled, QSpinBox::down-button:disabled,
QDoubleSpinBox::up-button:disabled, QDoubleSpinBox::down-button:disabled,
QDateTimeEdit::up-button:disabled, QDateTimeEdit::down-button:disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


QSpinBox::up-button:pressed, QSpinBox::down-button:pressed,
QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button::pressed,
QDateTimeEdit::up-button:pressed, QDateTimeEdit::down-button::pressed
{
    background-color: #979796;
    border: 1px solid #444444;

}


QSpinBox::down-arrow,
QDoubleSpinBox::down-arrow,
QDateTimeEdit::down-arrow
{
    image: url(://arrow-down.png);
    width: 7px;

}


QSpinBox::up-arrow,
QDoubleSpinBox::up-arrow,
QDateTimeEdit::up-arrow
{
    image: url(://arrow-up.png);
    width: 7px;

}


/*-----QLineEdit-----*/
QLineEdit
{
	background-color: #000000;
	color: #00ff00;
	font-weight: bold;
    border: 1px solid #333333;
	padding: 4px;

}


QLineEdit:hover
{
    border: 1px solid #00ff00;

}


QLineEdit::disabled
{
	background-color: #404040;
	color: #656565;
	border-width: 1px;
	border-color: #051a39;
	padding: 2px;

}


/*-----QTextEdit-----*/
QTextEdit
{
	background-color: #808080;
	color: #fff;
	border: 1px groove #333333;

}


QTextEdit::disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;

}


/*-----QGroupBox-----*/
QGroupBox 
{
    border: 1px groove #333333;
	border-radius: 2px;
    margin-top: 20px;

}


QGroupBox 
{
	background-color: qlineargradient(spread:repeat, x1:0.486, y1:0, x2:0.505, y2:1, stop:0.00480769 rgba(170, 169, 169, 255),stop:1 rgba(122, 122, 122, 255));
	font-weight: bold;

}


QGroupBox::title  
{
    background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(71, 75, 87, 255),stop:1 rgba(35, 37, 43, 255));
    color: #ffffff;
    border: 2px groove #333333;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px;

}


QGroupBox::title::disabled
{
	background-color: #404040;
	color: #656565;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px;
	border-top-left-radius: 3px;
	border-top-right-radius: 3px;

}


/*-----QCheckBox-----*/
QCheckBox{
	background-color: transparent;
	font-weight: bold;
	color: #fff;

}


QCheckBox::indicator
{
    color: #b1b1b1;
    background-color: #323232;
    border: 2px solid #222222;
    width: 12px;
    height: 12px;

}


QCheckBox::indicator:checked
{
    image:url(://checkbox.png);
    border: 2px solid #00ff00;

}


QCheckBox::indicator:unchecked:hover
{
    border: 2px solid #00ff00;

}


QCheckBox::disabled
{
	color: #656565;

}


QCheckBox::indicator:disabled
{
	background-color: #656565;
	color: #656565;
    border: 1px solid #656565;

}


/*-----QRadioButton-----*/
QRadioButton{
	background-color: transparent;
	font-weight: bold;
	color: #fff;

}


QRadioButton::indicator::unchecked
{ 
	border: 2px inset #222222; 
	border-radius: 6px; 
	background-color:  #323232;
	width: 9px; 
	height: 9px; 

}


QRadioButton::indicator::unchecked:hover
{ 
	border: 2px solid #00ff00; 
	border-radius: 5px; 
	background-color:  #323232;
	width: 9px; 
	height: 9px; 

}


QRadioButton::indicator::checked
{ 
	border: 2px inset #222222; 
	border-radius: 5px; 
	background-color: #00ff00; 
	width: 9px; 
	height: 9px; 

}


QRadioButton::disabled
{
	color: #656565;

}


QRadioButton::indicator:disabled
{
	background-color: #656565;
	color: #656565;
    border: 2px solid #656565;

}


/*-----QTableView & QTableWidget-----*/
QTableView
{
    background-color: #808080;
    border: 1px groove #333333;
    color: #f0f0f0;
	font-weight: bold;
    gridline-color: #333333;
    outline : 0;

}


QTableView::disabled
{
    background-color: #242526;
    border: 1px solid #32414B;
    color: #656565;
    gridline-color: #656565;
    outline : 0;

}


QTableView::item:hover 
{
    background-color: #484c58;
    color: #f0f0f0;

}


QTableView::item:selected 
{
    background-color: #484c58;
    border: 2px groove #00ff00;
    color: #F0F0F0;

}


QTableView::item:selected:disabled
{
    background-color: #1a1b1c;
    border: 2px solid #525251;
    color: #656565;

}


QTableCornerButton::section
{
    background-color: #282830;

}


QHeaderView::section
{
    background-color: #282830;
    color: #fff;
	font-weight: bold;
    text-align: left;
	padding: 4px;
	
}


QHeaderView::section:disabled
{
    background-color: #525251;
    color: #656565;

}


QHeaderView::section:checked
{
    background-color: #00ff00;

}


QHeaderView::section:checked:disabled
{
    color: #656565;
    background-color: #525251;

}


QHeaderView::section::vertical::first,
QHeaderView::section::vertical::only-one
{
    border-top: 0px;

}


QHeaderView::section::vertical
{
    border-top: 0px;

}


QHeaderView::section::horizontal::first,
QHeaderView::section::horizontal::only-one
{
    border-left: 0px;

}


QHeaderView::section::horizontal
{
    border-left: 0px;

}


/*-----QTabWidget-----*/
QTabBar::tab
{
	background-color: transparent;
	color: #ffffff;
	font-weight: bold;
	width: 80px;
	height: 9px;
	
}


QTabBar::tab:disabled
{
	background-color: #656565;
	color: #656565;

}


QTabWidget::pane 
{
	background-color: transparent;
	color: #ffffff;
	border: 1px groove #333333;

}


QTabBar::tab:selected
{
    background-color: #484c58;
	color: #ffffff;
	border: 1px groove #333333;
	border-bottom: 0px;

}


QTabBar::tab:selected:disabled
{
	background-color: #404040;
	color: #656565;

}


QTabBar::tab:!selected 
{
    background-color: #a3a7b2;

}


QTabBar::tab:!selected:hover 
{
    background-color: #484c58;

}


QTabBar::tab:top:!selected 
{
    margin-top: 1px;

}


QTabBar::tab:bottom:!selected 
{
    margin-bottom: 3px;

}


QTabBar::tab:top, QTabBar::tab:bottom 
{
    min-width: 8ex;
    margin-right: -1px;
    padding: 5px 10px 5px 10px;

}


QTabBar::tab:top:selected 
{
    border-bottom-color: none;

}


QTabBar::tab:bottom:selected 
{
    border-top-color: none;

}


QTabBar::tab:top:last, QTabBar::tab:bottom:last,
QTabBar::tab:top:only-one, QTabBar::tab:bottom:only-one 
{
    margin-right: 0;

}


QTabBar::tab:left:!selected 
{
    margin-right: 2px;

}


QTabBar::tab:right:!selected
{
    margin-left: 2px;

}


QTabBar::tab:left, QTabBar::tab:right 
{
    min-height: 15ex;
    margin-bottom: -1px;
    padding: 10px 5px 10px 5px;

}


QTabBar::tab:left:selected 
{
    border-left-color: none;

}


QTabBar::tab:right:selected 
{
    border-right-color: none;

}


QTabBar::tab:left:last, QTabBar::tab:right:last,
QTabBar::tab:left:only-one, QTabBar::tab:right:only-one 
{
    margin-bottom: 0;

}


/*-----QSlider-----*/
QSlider{
	background-color: transparent;

}


QSlider::groove:horizontal 
{
	background-color: transparent;
	height: 6px;

}


QSlider::sub-page:horizontal 
{
	background-color: qlineargradient(spread:reflect, x1:1, y1:0, x2:1, y2:1, stop:0.00480769 rgba(201, 201, 201, 255),stop:1 rgba(72, 72, 72, 255));
	border: 1px solid #000;

}


QSlider::add-page:horizontal 
{
	background-color: #404040;
	border: 1px solid #000; 

}


QSlider::handle:horizontal 
{
	background-color: qlineargradient(spread:reflect, x1:1, y1:0, x2:1, y2:1, stop:0.00480769 rgba(201, 201, 201, 255),stop:1 rgba(72, 72, 72, 255));
	border: 1px solid #000; 
	width: 12px;
	margin-top: -6px;
	margin-bottom: -6px;

}


QSlider::handle:horizontal:hover 
{
	background-color: #808080;

}


QSlider::sub-page:horizontal:disabled 
{
	background-color: #bbb;
	border-color: #999;

}


QSlider::add-page:horizontal:disabled 
{
	background-color: #eee;
	border-color: #999;

}


QSlider::handle:horizontal:disabled 
{
	background-color: #eee;
	border: 1px solid #aaa;

}


QSlider::groove:vertical 
{
	background-color: transparent;
	width: 6px;

}


QSlider::sub-page:vertical 
{
	background-color: qlineargradient(spread:reflect, x1:0, y1:0.483, x2:1, y2:0.517, stop:0.00480769 rgba(201, 201, 201, 255),stop:1 rgba(72, 72, 72, 255));
	border: 1px solid #000;

}


QSlider::add-page:vertical 
{
	background-color: #404040;
	border: 1px solid #000;

}


QSlider::handle:vertical 
{
	background-color: qlineargradient(spread:reflect, x1:0, y1:0.483, x2:1, y2:0.517, stop:0.00480769 rgba(201, 201, 201, 255),stop:1 rgba(72, 72, 72, 255));
	border: 1px solid #000;
	height: 12px;
	margin-left: -6px;
	margin-right: -6px;

}


QSlider::handle:vertical:hover 
{
	background-color: #808080;

}


QSlider::sub-page:vertical:disabled 
{
	background-color: #bbb;
	border-color: #999;

}


QSlider::add-page:vertical:disabled 
{
	background-color: #eee;
	border-color: #999;

}


QSlider::handle:vertical:disabled 
{
	background-color: #eee;
	border: 1px solid #aaa;
	border-radius: 3px;

}


/*-----QDial-----*/
QDial
{
	background-color: #600000;

}


QDial::disabled
{
	background-color: #404040;

}


/*-----QScrollBar-----*/
QScrollBar:horizontal
{
    border: 1px solid #222222;
    background-color: #63676d;
    height: 18px;
    margin: 0px 18px 0 18px;

}


QScrollBar::handle:horizontal
{
    background-color: #a6acb3;
	border: 1px solid #656565;
	border-radius: 2px;
    min-height: 20px;

}


QScrollBar::add-line:horizontal
{
    border: 1px solid #1b1b19;
    background-color: #a6acb3;
    width: 18px;
    subcontrol-position: right;
    subcontrol-origin: margin;

}


QScrollBar::sub-line:horizontal
{
    border: 1px solid #1b1b19;
    background-color: #a6acb3;
    width: 18px;
    subcontrol-position: left;
    subcontrol-origin: margin;

}


QScrollBar::right-arrow:horizontal
{
    image: url(://arrow-right.png);
    width: 8px;
    height: 8px;

}


QScrollBar::left-arrow:horizontal
{
    image: url(://arrow-left.png);
    width: 8px;
    height: 8px;

}


QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
{
    background: none;

}


QScrollBar:vertical
{
    background-color: #63676d;
    width: 18px;
    margin: 18px 0 18px 0;
    border: 1px solid #222222;

}


QScrollBar::handle:vertical
{
    background-color: #a6acb3;
	border: 1px solid #656565;
	border-radius: 2px;
    min-height: 20px;

}


QScrollBar::add-line:vertical
{
    border: 1px solid #1b1b19;
    background-color: #a6acb3;
    height: 18px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;

}


QScrollBar::sub-line:vertical
{
    border: 1px solid #1b1b19;
    background-color: #a6acb3;
    height: 18px;
    subcontrol-position: top;
    subcontrol-origin: margin;

}


QScrollBar::up-arrow:vertical
{
    image: url(://arrow-up.png);
    width: 8px;
    height: 8px;

}


QScrollBar::down-arrow:vertical
{
    image: url(://arrow-down.png);
    width: 8px;
    height: 8px;

}


QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
{
    background: none;

}


/*-----QProgressBar-----*/
QProgressBar
{
	background-color: #000;
	color: #00ff00;
	font-weight: bold;
	border: 0px groove #000;
	border-radius: 10px;
	text-align: center;

}


QProgressBar:disabled
{
	background-color: #404040;
	color: #656565;
	border-color: #051a39;
	border: 1px solid #000;
	border-radius: 10px;
	text-align: center;

}


QProgressBar::chunk {
	background-color: #ffaf02;
	border: 0px;
	border-radius: 10px;
	color: #000;

}


QProgressBar::chunk:disabled {
	background-color: #333;
	border: 0px;
	border-radius: 10px;
	color: #656565;
}


/*-----QStatusBar-----*/
QStatusBar
{
	background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, stop:0 rgba(102, 115, 140, 255),stop:1 rgba(56, 63, 77, 255));
	color: #ffffff;
	border-color: #051a39;
	font-weight: bold;

}


"""


class MyJournal(QMainWindow):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Load GUI
        uic.loadUi(getv("main_ui_file_path"), self)
        # 'blocks' has key = record_ID
        #       key = text, key = tag_id list
        stt.app_setting_add("blocks", {})
        # Define database information object and save it in app settings
        stt.app_setting_add("db_info", user.DBInfoObject)
        # Define LOG object and save it in app settings
        stt.app_setting_add("log", log)
        # Define USER object and save it in app settings
        stt.app_setting_add("user", user)
        # Define Signals class
        signals = utility_cls.Signals()
        stt.app_setting_add("signal", signals)
        self.send_signal: utility_cls.Signals = get_appv("signal")
        # Define ContextMenu and Selection information dictionary
        stt.app_setting_add("selection", {})
        stt.app_setting_add("menu", {})
        # Add main windows to app settings
        stt.app_setting_add("main_win", self)
        # Add clipboard to app settings
        stt.app_setting_add("clipboard", app.clipboard())
        # Add internal clipboard dict {type['file', 'image'], id}
        stt.app_setting_add("cb", utility_cls.Clipboard(stt))
        # Calculator variable
        stt.app_setting_add("calculator", [])
        # Add file add variable
        stt.app_setting_add("file_add", None)
        # Set Calculator mode variable
        setv("calculator_mode", False)
        # Variable used for Definition Extra Images (List of shown images)
        stt.app_setting_add("extra_images", [])
        stt.app_setting_add("extra_images_pool", [])
        stt.app_setting_add("extra_images_around_def", [])
        # Crash variable if something goes wrong
        crash_file = getv("crash_file_path")
        if os.path.isfile(crash_file):
            self.crash_dict = stt.custom_dict_load(crash_file)
        else:
            self.crash_dict = {}

    def start_gui(self):    
        # Define widgets, setup language and apperance
        self._define_widgets()
        self._setup_widgets_language()
        self._setup_widgets_apperance()
        self._animate_window_title()
        # Load user settings, Window pos, size, toolbar pos...
        self._load_user_widget_settings()
        # Add QLabel in QScrollArea
        self.area_widget.layout().addWidget(self.area_label)
        if not getv("scroll_area_show_label_widget"):
            self.area_label.setText("")

        self.show()
        # Show Fun Facts
        if getv("fun_fact_show_on_start"):
            utility_cls.FunFactShow(stt, self)
        # Check is there draft records and ask user to show them
        self.ask_to_open_drafts_on_start()
        # Check crash dictionary:
        if user.username in self.crash_dict:
            if "def" in self.crash_dict[user.username]:
                log.write_log("Warning. Last session crashed...: Definition Add/Edit resuming...")
                definition_cls.AddDefinition(stt, self, crash_dict=self.crash_dict)
        # Connect events with slots
        self.closeEvent = self._close_event
        self.area_label.mousePressEvent = self.area_label_mouse_press
        # Menu / ToolBar events
        self.toolBar.orientationChanged.connect(self._toolbar_areas_changed)
        self.toolBar.actionTriggered.connect(self._close_context_dialogs)
        self.menu_file.aboutToShow.connect(self._close_context_dialogs)
        self.menu_edit.aboutToShow.connect(self._close_context_dialogs)
        self.menu_view.aboutToShow.connect(self._close_context_dialogs)
        self.menu_user.aboutToShow.connect(self._close_context_dialogs)
        self.menu_tags.aboutToShow.connect(self._close_context_dialogs)
        self.menu_help.aboutToShow.connect(self._close_context_dialogs)

        # File menu
        self.mnu_file_save_active_block.triggered.connect(self.mnu_file_save_active_block_triggered)
        # Edit menu
        self.mnu_add_block.triggered.connect(self.mnu_add_block_triggered)
        self.mnu_expand_all.triggered.connect(self.mnu_expand_all_triggered)
        self.mnu_collapse_all.triggered.connect(self.mnu_collapse_all_triggered)
        self.mnu_edit_tags.triggered.connect(self.mnu_edit_tags_triggered)
        self.mnu_edit_definitions.triggered.connect(self.mnu_edit_definitions_triggered)
        self.mnu_unfinished_show.triggered.connect(self.mnu_unfinished_show_triggered)
        self.mnu_translation.triggered.connect(self.mnu_translation_triggered)
        # View menu
        self.mnu_diary.triggered.connect(self.mnu_diary_triggered)
        self.mnu_view_blocks.triggered.connect(self.mnu_view_blocks_triggered)
        self.mnu_view_tags.triggered.connect(self.mnu_view_tags_triggered)
        self.mnu_view_definitions.triggered.connect(self.mnu_view_definitions_triggered)
        self.mnu_view_images.triggered.connect(self.mnu_view_images_triggered)
        self.mnu_view_fun_fact.triggered.connect(self.mnu_view_fun_fact_triggered)
        self.mnu_view_media_explorer.triggered.connect(self.mnu_view_media_explorer_triggered)
        self.mnu_view_dicts.triggered.connect(self.mnu_view_dicts_triggered)
        self.mnu_view_wiki.triggered.connect(self.mnu_view_wiki_triggered)
        self.mnu_view_online_content.triggered.connect(self.mnu_view_online_content_triggered)
        self.mnu_view_find_in_app.triggered.connect(self.mnu_view_find_in_app_triggered)
        self.mnu_view_clipboard.triggered.connect(self.mnu_view_clipboard_triggered)
        # TMP
        self.mnu_open.triggered.connect(self.mnu_open_click)

        self.show()
        self.show_welcome_notification()

    # Here we recive info from WinBlock...
    def events(self, event_dict: dict):
        if event_dict["name"] == "win_block":
            if event_dict["action"] == "open_new_block":
                self.add_block()

        if event_dict["name"] == "block_view":
            if event_dict["action"] == "block_ids":
                id_list = []
                for i in range(self.area_widget.layout().count()):
                    if isinstance(self.area_widget.layout().itemAt(i).widget(), block_cls.WinBlock):
                        id_list.append(self.area_widget.layout().itemAt(i).widget()._active_record_id)
                return id_list
        
        if event_dict["name"] == "pic_info":
            if event_dict["action"] == "open_block":
                diary_view_cls.BlockView(stt, self, block_ids=event_dict["id"], auto_open_ids=event_dict["id"])
            if event_dict["action"] == "open_def":
                definition_cls.ViewDefinition(stt, self, event_dict["id"])

        if event_dict["name"] == "find_in_app":
            if event_dict["action"] == "open_block":
                diary_view_cls.BlockView(stt, self, auto_open_ids=event_dict["id"])
            if event_dict["action"] == "open_all_blocks":
                diary_view_cls.BlockView(stt, self, block_ids=event_dict["ids"])
            if event_dict["action"] == "open_all_diary":
                diary_view_cls.DiaryView(stt, self, block_list=event_dict["ids"])
            if event_dict["action"] == "open_definition":
                definition_cls.BrowseDefinitions(stt, self, definition_id=event_dict["id"])
            if event_dict["action"] == "open_image":
                utility_cls.PictureView(stt, self, [event_dict["id"]], start_with_media_id=event_dict["id"], application_modal=False)
            if event_dict["action"] == "image_info":
                utility_cls.PictureInfo(stt, self, event_dict["id"])
            if event_dict["action"] == "file_info":
                utility_cls.FileInfo(stt, self, event_dict["id"])

    def toolBar_mouse_press_event(self):
        self._close_context_dialogs()

    def area_label_mouse_press(self, ev: QtGui.QMouseEvent):
        dialog_queue = utility_cls.DialogsQueue()
        dialog_queue.remove_all_context_menu()
        if ev.button() == Qt.RightButton:
            self._show_area_label_menu()

    def _show_area_label_menu(self):
        menu_dict = {
            "position": QCursor().pos(),
            "separator": [30],
            "items": [
                [
                    10,
                    getl("main_area_lbl_menu_add_new_text"),
                    getl("main_area_lbl_menu_add_new_tt"),
                    True,
                    [],
                    getv("mnu_add_block_icon_path")
                ],
                [
                    20,
                    getl("main_area_lbl_menu_unfinnished_text"),
                    getl("main_area_lbl_menu_unfinnished_tt"),
                    True,
                    [],
                    getv("select_icon_path")
                ],
                [
                    30,
                    getl("main_area_lbl_menu_block_view_text"),
                    getl("main_area_lbl_menu_block_view_tt"),
                    True,
                    [],
                    getv("block_view_win_icon_path")
                ],
                [
                    40,
                    getl("block_txt_box_menu_find_in_app_text"),
                    getl("block_txt_box_menu_find_in_app_tt"),
                    True,
                    [],
                    getv("find_in_app_win_icon_path")
                ],
            ]
        }
        set_appv("menu", menu_dict)
        utility_cls.ContextMenu(stt, self)
        get_appv("log").write_log("MainWin. Area Label context menu show")
        if get_appv("menu")["result"] == 10:
            self.add_block()
        elif get_appv("menu")["result"] == 20:
            self.mnu_unfinished_show_triggered()
        elif get_appv("menu")["result"] == 30:
            diary_view_cls.BlockView(stt, self)
        elif get_appv("menu")["result"] == 40:
            utility_cls.FindInApp(stt, self)

    def _close_context_dialogs(self):
        dialog_queue = utility_cls.DialogsQueue()
        dialog_queue.remove_all_context_menu()

    def _animate_window_title(self):
        if getv("main_win_title_animate"):
            self.timer = QTimer(self)
            spaces = " " * getv("main_win_title_animate_spaces")
            title = spaces.join([x for x in self.windowTitle()])
            self.setWindowTitle(title)
            self.timer.singleShot(getv("main_win_title_animate_step_duration"), self._animate_window_title_loop)
            get_appv("log").write_log("MainWin. Window title animation started.")
    
    def _animate_window_title_loop(self):
        i = self.windowTitle().find(" ")
        text = self.windowTitle()
        if i >= 0:
            self.setWindowTitle(text[:i] + text[i+1:])
            self.timer.singleShot(getv("main_win_title_animate_step_duration"), self._animate_window_title_loop)
        else:
            self.timer = None

    def show_welcome_notification(self):
        if getv("show_welcome_notification"):
            date_cls = utility_cls.DateTime(stt)
            date_dict = date_cls.make_date_dict()
            text = f'{date_dict["day_name"]}, {date_dict["day"]}, {date_dict["month_name"]}, {date_dict["year"]}.'

            data = {
                "title": getl("welcome_notification_title"),
                "show_close": True,
                "text": text,
                "timer": 10000,
                "position": "bottom right" }
            utility_cls.Notification(stt, self, data, play_sound=False)
            get_appv("log").write_log("MainWin. Welcome notification show.")

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        dialog_queue = utility_cls.DialogsQueue()
        dialog_queue.remove_all_context_menu()
        return super().mousePressEvent(a0)

    def mnu_open_click(self):
        definition_data_find_cls.DefinitionFinder(self, stt)
        # app_settings_cls.Settings(stt, self)

    def mnu_file_save_active_block_triggered(self) -> None:
        self.save_active_block()

    def mnu_add_block_triggered(self):
        self.add_block()

    def mnu_edit_definitions_triggered(self):
        definition_cls.AddDefinition(stt, self)

    def mnu_edit_tags_triggered(self):
        tag_cls.TagView(stt, self)

    def mnu_unfinished_show_triggered(self):
        result = self._show_all_drafts(animate_block_open=getv("mnu_unfinished_show_block_animation"))
        if not result:
            msg_dict = {
                "text": getl("mnu_unfinished_msg_no_data_text"),
                "position": "center",
                "pos_center": True
            }
            utility_cls.MessageInformation(stt, self, msg_dict)

    def mnu_translation_triggered(self) -> None:
        trans = utility_cls.Translate(stt, self)
        trans.show_gui()

    def mnu_diary_triggered(self):
        diary_view_cls.DiaryView(stt, self)

    def mnu_view_blocks_triggered(self) -> None:
        diary_view_cls.BlockView(stt, self)

    def mnu_view_tags_triggered(self):
        tag_cls.TagView(stt, self)

    def mnu_view_images_triggered(self):
        utility_cls.PictureBrowse(stt, self)

    def mnu_view_definitions_triggered(self) -> None:
        definition_cls.BrowseDefinitions(stt, self)

    def mnu_view_fun_fact_triggered(self) -> None:
        utility_cls.FunFactShow(stt, self)

    def mnu_view_clipboard_triggered(self) -> None:
        utility_cls.ClipboardView(stt, self)

    def mnu_view_media_explorer_triggered(self):
        utility_cls.MediaExplorer(stt, self)

    def mnu_view_dicts_triggered(self) -> None:
        dict_view = dict_cls.DictFrame(stt, self)
        dict_view.show_word()

    def mnu_view_wiki_triggered(self) -> None:
        wikipedia_cls.Wikipedia(self, stt)

    def mnu_view_online_content_triggered(self) -> None:
        online_content_cls.OnlineContent(self, stt)

    def mnu_view_find_in_app_triggered(self):
        utility_cls.FindInApp(stt, self)

    def save_active_block(self):
        for i in range(self.area_widget.layout().count()):
            if isinstance(self.area_widget.layout().itemAt(i).widget(), block_cls.WinBlock):
                if self.area_widget.layout().itemAt(i).widget().block_is_active:
                    self.area_widget.layout().itemAt(i).widget()._update_block(silent_update=False)
                else:
                    self.area_widget.layout().itemAt(i).widget()._update_block(silent_update=True)
        ntf_dict = {
            "title": "",
            "text": getl("main_win_notif_blocks_updated_text"),
            "icon": getv("win_block_notif_block_updated_icon_path"),
            "animation": False,
            "timer": 2500
        }
        utility_cls.Notification(stt, self, ntf_dict, play_sound=False)

    def ask_to_open_drafts_on_start(self):
        if getv("auto_show_drafts_on_start"):
            self._show_all_drafts(collapsed=getv("show_draft_blocks_collapsed_on_start"), animate_block_open=getv("animate_adding_empty_blocks_at_start"))
        # Create block on start
        if getv("add_block_at_start"):
            db_record = db_record_cls.Record(stt)
            draft_rec = db_record.get_draft_records()
            if draft_rec:
                add_new = True
                for record in draft_rec:
                    if record[4] == "":
                        add_new = False
                        break
                if add_new:
                    self.add_block()
            else:
                self.add_block()

    def _show_all_drafts(self, collapsed: bool = False, animate_block_open: bool = None) -> bool:
        selection = get_appv("selection")
        opened_items = []
        for idx in range(self.area_widget.layout().count()):
            if isinstance(self.area_widget.layout().itemAt(idx).widget(), block_cls.WinBlock):
                opened_items.append(self.area_widget.layout().itemAt(idx).widget()._active_record_id)
        selection["title"] = getl("open_drafts_at_start_menu_title")
        selection["multi-select"] = False
        selection["checkable"] = True
        selection["result"] = None
        selection["items"] = []
        db_record = db_record_cls.Record(stt)
        empty_rec = db_record.get_draft_records()
        app.processEvents()
        if empty_rec:
            has_records = False
            for record in empty_rec:
                name = record[2] + " "
                if record[1]:
                    name += record[1]
                else:
                    name += getl("open_records_on_start_no_name")
                if record[0] not in opened_items:
                    selection["items"].append([record[0], name, record[4], False, True, []])
                    has_records = True
            if has_records:
                menu = utility_cls.Selection(stt, self)
                if selection["result"]:
                    for record_id in selection["result"]:
                        if animate_block_open is not None:
                            animate = animate_block_open
                        else:
                            animate = True
                        self.add_block(record_id, collapsed=collapsed, animate=animate)
                return True
            else:
                return False
        else:
            return False

    def add_block(self, record_id: int = 0, collapsed: bool = False, animate: bool = True):
        if record_id == 0:
            # Find record ID for new block
            #   Save new empty record
            record = db_record_cls.Record(stt)
            record_id = record.add_new_record("", "")
            record_data = db_record_data_cls.RecordData(stt, record_id)
            data_dict = record_data._empty_record_data_dict()
            data_dict["tag"] = [x for x in getv("block_tag_added_at_start").split(",") if x != ""]
            record_data.update_record_data(data_dict, record_id=record_id)
            get_appv("log").write_log(f"MainWin. New block added. Record ID: {record_id}")
        
        # Check if block exist
        for i in range(self.area_widget.layout().count()):
            if isinstance(self.area_widget.layout().itemAt(i).widget(), block_cls.WinBlock):
                if self.area_widget.layout().itemAt(i).widget()._active_record_id == record_id:
                    return
        # Create new win block            
        block_cls.WinBlock(stt, self.area_widget, record_id, collapsed=collapsed, animate_block=animate, main_window=self)

    def mnu_expand_all_triggered(self):
        value = getv("block_animation_on_expand")
        setv("block_animation_on_expand", False)
        self.send_signal.send_expand_all_signal()
        app.processEvents()
        setv("block_animation_on_expand", value)

    def mnu_collapse_all_triggered(self):
        value = getv("block_animation_on_collapse")
        setv("block_animation_on_collapse", False)
        self.send_signal.send_collapse_all_signal()
        app.processEvents()
        setv("block_animation_on_collapse", value)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if getv("resize_area_with_mainwindow"):
            w = self.contentsRect().width()
            h = self.contentsRect().height() - self.sts_bar.height() - self.menubar.height()
            if self.toolBarArea(self.toolBar) == Qt.TopToolBarArea or self.toolBarArea(self.toolBar) == Qt.BottomToolBarArea:
                h -= self.toolBar.height()
            elif self.toolBarArea(self.toolBar) == Qt.LeftToolBarArea or self.toolBarArea(self.toolBar) == Qt.RightToolBarArea:
                w -= self.toolBar.width()
            
            self.area.resize(w, h)
        return super().resizeEvent(a0)

    def _close_event(self, a0):
        # Show exit notification
        if getv("show_closing_notification"):
            data_dict = {"text": getl("closing_notification_text")}
            data_dict["title"] = getl("closing_notification_title")
            data_dict["fade"] = False
            data_dict["animation"] = False
            data_dict["timer"] = None
            data_dict["position"] = "top right"
            utility_cls.Notification(stt, self, data_dict, play_sound=False)
            app.processEvents()
            get_appv("log").write_log("MainWin. Close notification show.")

        # Save clipboard content
        if getv("delete_clipboard_on_app_exit"):
            get_appv("cb").clear_clip()
        get_appv("cb")._save_clipboard_to_file()

        # Delete temp folder
        if getv("delete_temp_folder_on_app_exit"):
            file_util = utility_cls.FileDialog(stt)
            file_util.delete_temp_folder()

        # Close all blocks
        for idx in range(self.area_widget.layout().count()):
            if isinstance(self.area_widget.layout().itemAt(idx).widget(), block_cls.WinBlock):
                get_appv("log").write_log(f"MainWin. Close block on exit. Record ID: {self.area_widget.layout().itemAt(idx).widget()._active_record_id}")
                self.area_widget.layout().itemAt(idx).widget().close()

        # Remove any context menu, notification, input dialog ...
        dialog_queue = utility_cls.DialogsQueue()
        dialog_queue.remove_all()

        if self.isMaximized():
            setv("main_win_is_fullscreen", True)
        else:
            setv("main_win_is_fullscreen", False)
            setv("main_win_pos_x", self.pos().x())
            setv("main_win_pos_y", self.pos().y())
            setv("main_win_width", self.width())
            setv("main_win_height", self.height())
        setv("main_toolbar_position", self.toolBarArea(self.toolBar))

        stt.save_settings()
        get_appv("log").write_log("MainWin. Settings saved.")
        
        # Remove main window from app_setting
        stt.app_setting_delete("main_win")
        orac = 1
        while orac > 0:
            self.setWindowOpacity(orac)
            time.sleep(0.03)
            orac -= 0.05
        get_appv("log").write_log("MainWin. Window closed.")

    def _load_user_widget_settings(self):
        # MainWindow
        self.move(getv("main_win_pos_x"), getv("main_win_pos_y"))
        self.resize(getv("main_win_width"), getv("main_win_height"))
        if getv("main_win_is_fullscreen"):
            self.showMaximized()
        # Toolbar
        self.addToolBar(getv("main_toolbar_position"), self.toolBar)
        get_appv("log").write_log("MainWin. Settings loaded.")

    def _toolbar_areas_changed(self, areas):
        if getv("resize_area_with_mainwindow"):
            w = self.contentsRect().width()
            h = self.contentsRect().height() - self.sts_bar.height() - self.menubar.height()
            if self.toolBar.width() < self.toolBar.height():
                h -= self.toolBar.width()
            else:
                w -= self.toolBar.height() - self.sts_bar.height()
            self.area.resize(w, h)

    def _setup_widgets_apperance(self):
        # MainWindow
        self.setWindowIcon(QIcon(getv("main_win_icon_path")))
        self.setStyleSheet(getv("main_win_stylesheet"))
        # Toolbar
        self.toolBar.setStyleSheet(getv("toolBar_stylesheet"))
        self.toolBar.setMovable(getv("toolBar_movable"))
        self.toolBar.setFloatable(getv("toolBar_floatable"))
        self.toolBar.setToolButtonStyle(getv("toolBar_tool_button_style"))
        if getv("toolBar_fixed_width") >= 0:
            self.toolBar.setFixedWidth(getv("toolBar_fixed_width"))
        if getv("toolBar_fixed_height") >= 0:
            self.toolBar.setFixedHeight(getv("toolBar_fixed_height"))
        self.toolBar.setEnabled(getv("toolBat_enabled"))
        self.toolBar.setVisible(getv("toolBar_visible"))
        # StatusBar
        self.sts_bar.setStyleSheet(getv("sts_bar_stylesheet"))
        if getv("sts_bar_fixed_width") >= 0:
            self.sts_bar.setFixedWidth(getv("sts_bar_fixed_width"))
        if getv("sts_bar_fixed_height") >= 0:
            self.sts_bar.setFixedHeight(getv("sts_bar_fixed_height"))
        self.sts_bar.setEnabled(getv("sts_bar_enabled"))
        self.sts_bar.setVisible(getv("sts_bar_visible"))
        # ScrollArea
        self.area.setFrameShape(getv("scroll_area_frame_shape"))
        self.area.setFrameShadow(getv("scroll_area_frame_shadow"))
        self.area.setLineWidth(getv("scroll_area_line_width"))
        self.area.setStyleSheet(getv("scroll_area_stylesheet"))
        self.area.setEnabled(getv("scroll_area_enabled"))
        self.area.setVisible(getv("scroll_area_visible"))
        #   Label widget in ScrollArea
        self.area_label.setFrameShape(getv("area_label_widget_frame_shape"))
        self.area_label.setFrameShadow(getv("area_label_widget_frame_shadow"))
        self.area_label.setLineWidth(getv("area_label_widget_line_width"))
        self.area_label.setStyleSheet(getv("area_label_widget_stylesheet"))
        self.area_label.setVisible(getv("area_label_widget_visible"))
        align = getv("area_label_widget_alignment")
        if isinstance(align, str):
            align_vals = [int(x) for x in align.split(",") if x != ""]
            align = sum(align_vals)
        self.area_label.setAlignment(Qt.Alignment(align))
        # Main Menu
        self._define_main_menu_items(self.menu_file, "menu_file")
        self._define_main_menu_items(self.menu_edit, "menu_edit")
        self._define_main_menu_items(self.menu_view, "menu_view")
        self._define_main_menu_items(self.menu_user, "menu_user")
        self._define_main_menu_items(self.menu_tags, "menu_tags")
        self._define_main_menu_items(self.menu_help, "menu_help")

        # Menu Items
        #       File
        self._define_menu_item(self.mnu_open, "mnu_open")
        self._define_menu_item(self.mnu_save_as, "mnu_save_as")
        self._define_menu_item(self.mnu_file_save_active_block, "mnu_file_save_active_block")
        #       Edit
        self._define_menu_item(self.mnu_add_block, "mnu_add_block")
        self._define_menu_item(self.mnu_expand_all, "mnu_expand_all")
        self._define_menu_item(self.mnu_collapse_all, "mnu_collapse_all")
        self._define_menu_item(self.mnu_unfinished_show, "mnu_unfinished_show")
        self._define_menu_item(self.mnu_edit_tags, "mnu_edit_tags")
        self._define_menu_item(self.mnu_edit_definitions, "mnu_edit_definitions")
        self._define_menu_item(self.mnu_translation, "mnu_translation")
        #       View
        self._define_menu_item(self.mnu_diary, "mnu_diary")
        self._define_menu_item(self.mnu_view_blocks, "mnu_view_blocks")
        self._define_menu_item(self.mnu_view_tags, "mnu_view_tags")
        self._define_menu_item(self.mnu_view_definitions, "mnu_view_definitions")
        self._define_menu_item(self.mnu_view_images, "mnu_view_images")
        self._define_menu_item(self.mnu_view_fun_fact, "mnu_view_fun_fact")
        self._define_menu_item(self.mnu_view_clipboard, "mnu_view_clipboard")
        self._define_menu_item(self.mnu_view_media_explorer, "mnu_view_media_explorer")
        self._define_menu_item(self.mnu_view_dicts, "mnu_view_dicts")
        self._define_menu_item(self.mnu_view_wiki, "mnu_view_wiki")
        self._define_menu_item(self.mnu_view_online_content, "mnu_view_online_content")
        self._define_menu_item(self.mnu_view_find_in_app, "mnu_view_find_in_app")
        self._define_menu_item(self.mnu_schedule, "mnu_schedule")
        #       User
        self._define_menu_item(self.mnu_user_settings, "mnu_user_settings")
        self._define_menu_item(self.mnu_personal_info, "mnu_personal_info")
        self._define_menu_item(self.mnu_contacts, "mnu_contacts")
        #       Tags
        self._define_menu_item(self.mnu_expenses, "mnu_expenses")
        self._define_menu_item(self.mnu_incomes, "mnu_incomes")
        self._define_menu_item(self.mnu_web_pages, "mnu_web_pages")
        self._define_menu_item(self.mnu_youtube, "mnu_youtube")
        self._define_menu_item(self.mnu_important_dates, "mnu_important_dates")

    def _define_main_menu_items(self, menu_item: QMenu, name: str):
        menu_item.setStyleSheet(getv(f"{name}_stylesheet"))
        if getv("menu_file_icon_path"):
            menu_item.setIcon(QIcon(getv(f"{name}_icon_path")))
        menu_item.setToolTipsVisible(getv(f"{name}_tooltip_visible"))
        menu_item.setEnabled(getv(f"{name}_enabled"))
        menu_item.setVisible(getv(f"{name}_visible"))

    def _define_menu_item(self, menu_item: QAction, name: str):
        if getv(f"{name}_icon_path"):
            menu_item.setIcon(QIcon(getv(f"{name}_icon_path")))
        menu_item.setEnabled(getv(f"{name}_enabled"))
        menu_item.setVisible(getv(f"{name}_visible"))
        menu_item.setIconVisibleInMenu(getv(f"{name}_icon_visible"))
        menu_item.setShortcut(getv(f"{name}_shortcut"))
        menu_item.setShortcutVisibleInContextMenu(getv(f"{name}_shortcut_visible_in_menu"))

    def _setup_widgets_language(self):
        # Main Window
        self.setWindowTitle(getl("main_win_title") + f"...---...{user.username}")
        # ScrollArea
        self.area.setToolTip(getl("scroll_area_tt"))
        self.area.setStatusTip(getl("scroll_area_sb_text"))
        # ScrollArea QLabel widget
        self.area_label.setText(getl("area_label_widget_text"))
        self.area_label.setToolTip(getl("area_label_widget_tt"))
        self.area_label.setStatusTip(getl("area_label_widget_sb_text"))
        # Status Bar
        self.sts_bar.setToolTip(getl("stb_bar_tt"))
        # ToolBar
        self.toolBar.setToolTip(getl("toolBar_tt"))
        # Main menu items
        self.menu_file.setTitle(getl("menu_file_title"))
        self.menu_file.setToolTip(getl("menu_file_tt"))
        self.menu_file.setStatusTip(getl("menu_file_sb_text"))
        self.menu_edit.setTitle(getl("menu_edit_title"))
        self.menu_edit.setToolTip(getl("menu_edit_tt"))
        self.menu_edit.setStatusTip(getl("menu_edit_sb_text"))
        self.menu_view.setTitle(getl("menu_view_title"))
        self.menu_view.setToolTip(getl("menu_view_tt"))
        self.menu_view.setStatusTip(getl("menu_view_sb_text"))
        self.menu_user.setTitle(getl("menu_user_title"))
        self.menu_user.setToolTip(getl("menu_user_tt"))
        self.menu_user.setStatusTip(getl("menu_user_sb_text"))
        self.menu_tags.setTitle(getl("menu_tags_title"))
        self.menu_tags.setToolTip(getl("menu_tags_tt"))
        self.menu_tags.setStatusTip(getl("menu_tags_sb_text"))
        self.menu_help.setTitle(getl("menu_help_title"))
        self.menu_help.setToolTip(getl("menu_help_tt"))
        self.menu_help.setStatusTip(getl("menu_help_sb_text"))
        # File
        self.mnu_open.setText(getl("mnu_open_text"))
        self.mnu_open.setToolTip(getl("mnu_open_tt"))
        self.mnu_open.setStatusTip(getl("mnu_open_sb_text"))
        self.mnu_save_as.setText(getl("mnu_save_as_text"))
        self.mnu_save_as.setToolTip(getl("mnu_save_as_tt"))
        self.mnu_save_as.setStatusTip(getl("mnu_save_as_sb_text"))
        self.mnu_file_save_active_block.setText(getl("mnu_file_save_active_block_text"))
        self.mnu_file_save_active_block.setToolTip(getl("mnu_file_save_active_block_tt"))
        self.mnu_file_save_active_block.setStatusTip(getl("mnu_file_save_active_block_sb_text"))
        # Edit
        self.mnu_add_block.setText(getl("mnu_add_block_text"))
        self.mnu_add_block.setToolTip(getl("mnu_add_block_tt"))
        self.mnu_add_block.setStatusTip(getl("mnu_add_block_sb_text"))
        self.mnu_expand_all.setText(getl("mnu_expand_all_text"))
        self.mnu_expand_all.setToolTip(getl("mnu_expand_all_tt"))
        self.mnu_expand_all.setStatusTip(getl("mnu_expand_all_sb_text"))
        self.mnu_collapse_all.setText(getl("mnu_collapse_all_text"))
        self.mnu_collapse_all.setToolTip(getl("mnu_collapse_all_tt"))
        self.mnu_collapse_all.setStatusTip(getl("mnu_collapse_all_sb_text"))
        self.mnu_unfinished_show.setText(getl("mnu_unfinished_show_text"))
        self.mnu_unfinished_show.setToolTip(getl("mnu_unfinished_show_tt"))
        self.mnu_unfinished_show.setStatusTip(getl("mnu_unfinished_show_sb_text"))
        self.mnu_edit_tags.setText(getl("mnu_edit_tags_text"))
        self.mnu_edit_tags.setToolTip(getl("mnu_edit_tags_tt"))
        self.mnu_edit_tags.setStatusTip(getl("mnu_edit_tags_sb_text"))
        self.mnu_edit_definitions.setText(getl("mnu_edit_definitions_text"))
        self.mnu_edit_definitions.setToolTip(getl("mnu_edit_definitions_tt"))
        self.mnu_edit_definitions.setStatusTip(getl("mnu_edit_definitions_sb_text"))
        self.mnu_translation.setText(getl("mnu_translation_text"))
        self.mnu_translation.setToolTip(getl("mnu_translation_tt"))
        self.mnu_translation.setStatusTip(getl("mnu_translation_sb_text"))
        # View
        self.mnu_diary.setText(getl("mnu_diary_text"))
        self.mnu_diary.setToolTip(getl("mnu_diary_tt"))
        self.mnu_diary.setStatusTip(getl("mnu_diary_sb_text"))
        self.mnu_view_blocks.setText(getl("mnu_view_blocks_text"))
        self.mnu_view_blocks.setToolTip(getl("mnu_view_blocks_tt"))
        self.mnu_view_blocks.setStatusTip(getl("mnu_view_blocks_sb_text"))
        self.mnu_view_tags.setText(getl("mnu_view_tags_text"))
        self.mnu_view_tags.setToolTip(getl("mnu_view_tags_tt"))
        self.mnu_view_tags.setStatusTip(getl("mnu_view_tags_sb_text"))
        self.mnu_view_definitions.setText(getl("mnu_view_definitions_text"))
        self.mnu_view_definitions.setToolTip(getl("mnu_view_definitions_tt"))
        self.mnu_view_definitions.setStatusTip(getl("mnu_view_definitions_sb_text"))
        self.mnu_view_images.setText(getl("mnu_view_images_text"))
        self.mnu_view_images.setToolTip(getl("mnu_view_images_tt"))
        self.mnu_view_images.setStatusTip(getl("mnu_view_images_sb_text"))
        self.mnu_view_fun_fact.setText(getl("mnu_view_fun_fact_text"))
        self.mnu_view_fun_fact.setToolTip(getl("mnu_view_fun_fact_tt"))
        self.mnu_view_fun_fact.setStatusTip(getl("mnu_view_fun_fact_sb_text"))
        self.mnu_view_clipboard.setText(getl("mnu_view_clipboard_text"))
        self.mnu_view_clipboard.setToolTip(getl("mnu_view_clipboard_tt"))
        self.mnu_view_clipboard.setStatusTip(getl("mnu_view_clipboard_sb_text"))
        self.mnu_view_media_explorer.setText(getl("mnu_view_media_explorer_text"))
        self.mnu_view_media_explorer.setToolTip(getl("mnu_view_media_explorer_tt"))
        self.mnu_view_media_explorer.setStatusTip(getl("mnu_view_media_explorer_sb_text"))
        self.mnu_view_dicts.setText(getl("mnu_view_dicts_text"))
        self.mnu_view_dicts.setToolTip(getl("mnu_view_dicts_tt"))
        self.mnu_view_dicts.setStatusTip(getl("mnu_view_dicts_sb_text"))
        self.mnu_view_wiki.setText(getl("mnu_view_wiki_text"))
        self.mnu_view_wiki.setToolTip(getl("mnu_view_wiki_tt"))
        self.mnu_view_wiki.setStatusTip(getl("mnu_view_wiki_sb_text"))
        self.mnu_view_online_content.setText(getl("mnu_view_online_content_text"))
        self.mnu_view_online_content.setToolTip(getl("mnu_view_online_content_tt"))
        self.mnu_view_online_content.setStatusTip(getl("mnu_view_online_content_sb_text"))
        self.mnu_view_find_in_app.setText(getl("mnu_view_find_in_app_text"))
        self.mnu_view_find_in_app.setToolTip(getl("mnu_view_find_in_app_tt"))
        self.mnu_view_find_in_app.setStatusTip(getl("mnu_view_find_in_app_sb_text"))
        self.mnu_schedule.setText(getl("mnu_schedule_text"))
        self.mnu_schedule.setToolTip(getl("mnu_schedule_tt"))
        self.mnu_schedule.setStatusTip(getl("mnu_schedule_sb_text"))
        # User
        self.mnu_user_settings.setText(getl("mnu_user_settings_text"))
        self.mnu_user_settings.setToolTip(getl("mnu_user_settings_tt"))
        self.mnu_user_settings.setStatusTip(getl("mnu_user_settings_sb_text"))
        self.mnu_personal_info.setText(getl("mnu_personal_info_text"))
        self.mnu_personal_info.setToolTip(getl("mnu_personal_info_tt"))
        self.mnu_personal_info.setStatusTip(getl("mnu_personal_info_sb_text"))
        self.mnu_contacts.setText(getl("mnu_contacts_text"))
        self.mnu_contacts.setToolTip(getl("mnu_contacts_tt"))
        self.mnu_contacts.setStatusTip(getl("mnu_contacts_sb_text"))
        # Tags
        self.mnu_expenses.setText(getl("mnu_expenses_text"))
        self.mnu_expenses.setToolTip(getl("mnu_expenses_tt"))
        self.mnu_expenses.setStatusTip(getl("mnu_expenses_sb_text"))
        self.mnu_incomes.setText(getl("mnu_incomes_text"))
        self.mnu_incomes.setToolTip(getl("mnu_incomes_tt"))
        self.mnu_incomes.setStatusTip(getl("mnu_incomes_sb_text"))
        self.mnu_web_pages.setText(getl("mnu_web_pages_text"))
        self.mnu_web_pages.setToolTip(getl("mnu_web_pages_tt"))
        self.mnu_web_pages.setStatusTip(getl("mnu_web_pages_sb_text"))
        self.mnu_youtube.setText(getl("mnu_youtube_text"))
        self.mnu_youtube.setToolTip(getl("mnu_youtube_tt"))
        self.mnu_youtube.setStatusTip(getl("mnu_youtube_sb_text"))
        self.mnu_important_dates.setText(getl("mnu_important_dates_text"))
        self.mnu_important_dates.setToolTip(getl("mnu_important_dates_tt"))
        self.mnu_important_dates.setStatusTip(getl("mnu_important_dates_sb_text"))

    def _define_widgets(self):
        # Main menu
        self.menubar: QMenuBar = self.findChild(QMenuBar, "menubar")
        self.menu_file: QMenu = self.findChild(QMenu, "menuFile")
        self.menu_edit: QMenu = self.findChild(QMenu, "menuEdit")
        self.menu_view: QMenu = self.findChild(QMenu, "menuView")
        self.menu_user: QMenu = self.findChild(QMenu, "menuUser")
        self.menu_tags: QMenu = self.findChild(QMenu, "menuTags")
        self.menu_help: QMenu = self.findChild(QMenu, "menuHelp")
        # Menu Items
        #       File
        self.mnu_open: QAction = self.findChild(QAction, "mnu_open")
        self.mnu_save_as: QAction = self.findChild(QAction, "mnu_save_as")
        self.mnu_file_save_active_block: QAction = self.findChild(QAction, "mnu_file_save_active_block")
        #       Edit
        self.mnu_add_block: QAction = self.findChild(QAction, "mnu_add_block")
        self.mnu_expand_all: QAction = self.findChild(QAction, "mnu_expand_all")
        self.mnu_collapse_all: QAction = self.findChild(QAction, "mnu_collapse_all")
        self.mnu_unfinished_show: QAction = self.findChild(QAction, "mnu_unfinished_show")
        self.mnu_edit_tags:QAction = self.findChild(QAction, "mnu_edit_tags")
        self.mnu_edit_definitions: QAction = self.findChild(QAction, "mnu_edit_definitions")
        self.mnu_translation: QAction = self.findChild(QAction, "mnu_translation")
        #       View
        self.mnu_diary: QAction = self.findChild(QAction, "mnu_diary")
        self.mnu_view_blocks: QAction = self.findChild(QAction, "mnu_view_blocks")
        self.mnu_view_tags: QAction = self.findChild(QAction, "mnu_view_tags")
        self.mnu_view_definitions: QAction = self.findChild(QAction, "mnu_view_definitions")
        self.mnu_view_images: QAction = self.findChild(QAction, "mnu_view_images")
        self.mnu_view_fun_fact: QAction = self.findChild(QAction, "mnu_view_fun_fact")
        self.mnu_view_clipboard: QAction = self.findChild(QAction, "mnu_view_clipboard")
        self.mnu_view_media_explorer: QAction = self.findChild(QAction, "mnu_view_media_explorer")
        self.mnu_view_dicts: QAction = self.findChild(QAction, "mnu_view_dicts")
        self.mnu_view_wiki: QAction = self.findChild(QAction, "mnu_view_wiki")
        self.mnu_view_online_content: QAction = self.findChild(QAction, "mnu_view_online_content")
        self.mnu_view_find_in_app: QAction = self.findChild(QAction, "mnu_view_find_in_app")
        self.mnu_schedule: QAction = self.findChild(QAction, "mnu_schedule")
        #       User
        self.mnu_user_settings: QAction = self.findChild(QAction, "mnu_user_settings")
        self.mnu_personal_info: QAction = self.findChild(QAction, "mnu_personal_info")
        self.mnu_contacts: QAction = self.findChild(QAction, "mnu_contacts")
        #       Tags
        self.mnu_expenses: QAction = self.findChild(QAction, "mnu_expenses")
        self.mnu_incomes: QAction = self.findChild(QAction, "mnu_incomes")
        self.mnu_web_pages: QAction = self.findChild(QAction, "mnu_web_pages")
        self.mnu_youtube: QAction = self.findChild(QAction, "mnu_youtube")
        self.mnu_important_dates: QAction = self.findChild(QAction, "mnu_important_dates")
        # Status bar, Toolbar
        self.sts_bar: QStatusBar = self.findChild(QStatusBar, "sts_bar")
        self.toolBar: QToolBar = self.findChild(QToolBar, "toolBar")
        # ScrollArea
        self.area: QScrollArea = self.findChild(QScrollArea, "area")
        self._set_margins(self.area, "scroll_area")
        self.area_widget: QWidget = QWidget(self.area)
        self._set_margins(self.area_widget, "scroll_area_widget")
        self.area_widget.setLayout(QVBoxLayout(self.area_widget))
        self.area_widget.layout().setSpacing(getv("scroll_area_widget_layout_spacing"))
        self._set_margins(self.area_widget.layout(), "scroll_area_widget_layout")
        self.area.setWidget(self.area_widget)
        #   Label as last widget in scrollarea
        self.area_label: QLabel = QLabel(self.area_widget)

    def _set_margins(self, object: object, name: str) -> None:
        values = getv(name + "_contents_margins")
        margins = [int(x) for x in values.split(",") if x != ""]
        if len(margins) != 4:
            margins = [0, 0, 0, 0]
        object.setContentsMargins(margins[0], margins[1], margins[2], margins[3])


# File location where all settings will be saved
SETTING_FILE = "data/app/settings/settings.json"
# File location where all language data will be saved
LANGUAGES_FILE = "data/app/settings/languages.json"

if __name__ == "__main__":
    app = QApplication(sys.argv)   
    # app.setStyleSheet(theme_adaptic1)
    # 'stt' is a setting object that will be passed to various modules during application execution.
    stt = settings_cls.Settings(SETTING_FILE, LANGUAGES_FILE)
    # stt.debug_mode = True
    # Define settings methods
    getv = stt.get_setting_value
    setv = stt.set_setting_value
    getl = stt.lang
    get_appv = stt.app_setting_get_value
    set_appv = stt.app_setting_set_value
    # 'log' object is also passed to all modules when they are called.
    log = log_cls.Log(stt)
    # We create a users object that will contain all information about the currently active user.
    user = users_cls.User(stt)
    # Start login screen
    stt.set_setting_value("active_user", "")
    login =  login_cls.UserLogin(stt, user, log)
    login.start_gui()
    app.exec_()
    # If there is an active user in the 'active_user' object, then we start the application.
    if user.ActiveUserID != 0:
        login.deleteLater()
        stt.change_settings_file(user.settings_path)
        log.write_log("User settings are loaded.")
        my_journal = MyJournal()
        my_journal.start_gui()

        app.exec_()

    app.quit()







