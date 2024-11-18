from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, QAction, QStatusBar, QFrame, QPushButton,
                             QToolBar, QScrollArea, QVBoxLayout, QWidget, QLabel, QSizePolicy, QToolButton, QSlider,
                             QStyle, QDesktopWidget)
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QMovie, QMouseEvent
from PyQt5.QtCore import Qt, QTimer, QSize

import sys
import time
import os
from typing import Union, Any

import settings_cls
import log_cls
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
import export_import_cls
import statistic_cls
import qwidgets_util_cls
import timer_cls
import UTILS
from utils_settings import UTILS_Settings
import obj_tags
import obj_images
import obj_files
import obj_blocks
import obj_block
import obj_definitions
from text_handler_cls import AutoCompleteData
from text_handler_cls import TextHandlerData


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


def update_utils_settings(**kwargs) -> None:
    """
    Update the settings of the utils module.
    :param kwargs:
        DATE_FORMAT: Date format like "%d.%m.%Y."
        TIME_FORMAT: Time format like "%H:%M:%S"
        DATE_TIME_FORMAT_DELIMITER: String to separate date from time
        
        LOG_WINDOW_PARENT_WIDGET (QWidget): Widget to be set as parent of LogMessageViewer dialog
        POPUP_LOG_WINDOW_WHEN_EXCEPTION_IS_RAISED (bool): Show LogMessageViewer on exception
        POPUP_LOG_WINDOW_WHEN_WARNING_IS_RAISED (bool): Show LogMessageViewer on warning
        KEEP_LOG_WINDOW_ON_TOP (bool): Keep LogMessageViewer above other windows
        LOG_MAX_RECORDS (int): Maximum number of recorded log messages
        RECORD_NORMAL_LOGS (bool): Save all messages
        RECORD_WARNING_LOGS (bool): Save warning messages
        RECORD_EXCEPTION_LOGS (bool): Save exception messages
        LOG_SAVE_LOCALS (bool): Save local variables
        LOG_SAVE_GLOBALS (bool): Save global variables
        LOG_SAVE_BUILTINS (bool): Save built-in variables
        LOG_SAVE_MODULE_CODE (bool): Save <module> code
        LOG_SAVE_FUNCTION_CODE (bool): Save <function> code

    """

    if kwargs.get("DATE_FORMAT"):
        UTILS_Settings.DATE_FORMAT = kwargs["DATE_FORMAT"]
    if kwargs.get("TIME_FORMAT"):
        UTILS_Settings.TIME_FORMAT = kwargs["TIME_FORMAT"]
    if kwargs.get("DATE_TIME_FORMAT_DELIMITER"):
        UTILS_Settings.DATE_TIME_FORMAT_DELIMITER = kwargs["DATE_TIME_FORMAT_DELIMITER"]

    if kwargs.get("LOG_WINDOW_PARENT_WIDGET"):
        UTILS_Settings.LOG_WINDOW_PARENT_WIDGET = kwargs["LOG_WINDOW_PARENT_WIDGET"]
    if kwargs.get("POPUP_LOG_WINDOW_WHEN_EXCEPTION_IS_RAISED"):
        UTILS_Settings.POPUP_LOG_WINDOW_WHEN_EXCEPTION_IS_RAISED = kwargs["POPUP_LOG_WINDOW_WHEN_EXCEPTION_IS_RAISED"]
    if kwargs.get("POPUP_LOG_WINDOW_WHEN_WARNING_IS_RAISED"):
        UTILS_Settings.POPUP_LOG_WINDOW_WHEN_WARNING_IS_RAISED = kwargs["POPUP_LOG_WINDOW_WHEN_WARNING_IS_RAISED"]
    if kwargs.get("KEEP_LOG_WINDOW_ON_TOP"):
        UTILS_Settings.KEEP_LOG_WINDOW_ON_TOP = kwargs["KEEP_LOG_WINDOW_ON_TOP"]
    if kwargs.get("LOG_MAX_RECORDS"):
        UTILS_Settings.LOG_MAX_RECORDS = kwargs["LOG_MAX_RECORDS"]
    if kwargs.get("RECORD_NORMAL_LOGS"):
        UTILS_Settings.RECORD_NORMAL_LOGS = kwargs["RECORD_NORMAL_LOGS"]
    if kwargs.get("RECORD_WARNING_LOGS"):
        UTILS_Settings.RECORD_WARNING_LOGS = kwargs["RECORD_WARNING_LOGS"]
    if kwargs.get("RECORD_EXCEPTION_LOGS"):
        UTILS_Settings.RECORD_EXCEPTION_LOGS = kwargs["RECORD_EXCEPTION_LOGS"]
    if kwargs.get("LOG_SAVE_LOCALS"):
        UTILS_Settings.LOG_SAVE_LOCALS = kwargs["LOG_SAVE_LOCALS"]
    if kwargs.get("LOG_SAVE_GLOBALS"):
        UTILS_Settings.LOG_SAVE_GLOBALS = kwargs["LOG_SAVE_GLOBALS"]
    if kwargs.get("LOG_SAVE_BUILTINS"):
        UTILS_Settings.LOG_SAVE_BUILTINS = kwargs["LOG_SAVE_BUILTINS"]
    if kwargs.get("LOG_SAVE_MODULE_CODE"):
        UTILS_Settings.LOG_SAVE_MODULE_CODE = kwargs["LOG_SAVE_MODULE_CODE"]
    if kwargs.get("LOG_SAVE_FUNCTION_CODE"):
        UTILS_Settings.LOG_SAVE_FUNCTION_CODE = kwargs["LOG_SAVE_FUNCTION_CODE"]
    
    if kwargs.get("load_from"):
        stt_obj = kwargs["load_from"]
        UTILS_Settings.DATE_FORMAT = stt_obj.get_setting_value("date_format")
        UTILS_Settings.TIME_FORMAT = stt_obj.get_setting_value("time_format")
        UTILS_Settings.DATE_TIME_FORMAT_DELIMITER = stt_obj.get_setting_value("date_time_delimiter")

        UTILS_Settings.POPUP_LOG_WINDOW_WHEN_EXCEPTION_IS_RAISED = stt_obj.get_setting_value("pop_log_dialog_on_exception")
        UTILS_Settings.POPUP_LOG_WINDOW_WHEN_WARNING_IS_RAISED = stt_obj.get_setting_value("pop_log_dialog_on_warning")
        UTILS_Settings.KEEP_LOG_WINDOW_ON_TOP = stt_obj.get_setting_value("keep_log_window_on_top")
        UTILS_Settings.LOG_MAX_RECORDS = stt_obj.get_setting_value("number_of_saved_logs")
        UTILS_Settings.RECORD_NORMAL_LOGS = stt_obj.get_setting_value("record_normal_logs")
        UTILS_Settings.RECORD_WARNING_LOGS = stt_obj.get_setting_value("record_warning_logs")
        UTILS_Settings.RECORD_EXCEPTION_LOGS = stt_obj.get_setting_value("record_exception_logs")
        UTILS_Settings.LOG_SAVE_LOCALS = stt_obj.get_setting_value("log_save_locals")
        UTILS_Settings.LOG_SAVE_GLOBALS = stt_obj.get_setting_value("log_save_globals")
        UTILS_Settings.LOG_SAVE_BUILTINS = stt_obj.get_setting_value("log_save_builtins")
        UTILS_Settings.LOG_SAVE_MODULE_CODE = stt_obj.get_setting_value("log_save_module_code")
        UTILS_Settings.LOG_SAVE_FUNCTION_CODE = stt_obj.get_setting_value("log_save_function_code")

        # Update general settings
        stt_general = settings_cls.Settings(SETTING_FILE, LANGUAGES_FILE)
        stt_general.set_setting_value("date_format", stt_obj.get_setting_value("date_format"))
        stt_general.set_setting_value("time_format", stt_obj.get_setting_value("time_format"))
        stt_general.set_setting_value("date_time_delimiter", stt_obj.get_setting_value("date_time_delimiter"))

        stt_general.set_setting_value("pop_log_dialog_on_exception", stt_obj.get_setting_value("pop_log_dialog_on_exception"))
        stt_general.set_setting_value("pop_log_dialog_on_warning", stt_obj.get_setting_value("pop_log_dialog_on_warning"))
        stt_general.set_setting_value("keep_log_window_on_top", stt_obj.get_setting_value("keep_log_window_on_top"))
        stt_general.set_setting_value("number_of_saved_logs", stt_obj.get_setting_value("number_of_saved_logs"))
        stt_general.set_setting_value("record_normal_logs", stt_obj.get_setting_value("record_normal_logs"))
        stt_general.set_setting_value("record_warning_logs", stt_obj.get_setting_value("record_warning_logs"))
        stt_general.set_setting_value("record_exception_logs", stt_obj.get_setting_value("record_exception_logs"))
        stt_general.set_setting_value("log_save_locals", stt_obj.get_setting_value("log_save_locals"))
        stt_general.set_setting_value("log_save_globals", stt_obj.get_setting_value("log_save_globals"))
        stt_general.set_setting_value("log_save_builtins", stt_obj.get_setting_value("log_save_builtins"))
        stt_general.set_setting_value("log_save_module_code", stt_obj.get_setting_value("log_save_module_code"))
        stt_general.set_setting_value("log_save_function_code", stt_obj.get_setting_value("log_save_function_code"))
        if error_msg:= stt_general.save_settings():
            UTILS.TerminalUtility.WarningMessage("Unable to update general settings file.\n#1", [error_msg], variables=[["SETTING_FILE", SETTING_FILE], ["LANGUAGES_FILE", LANGUAGES_FILE]])
        else:
            UTILS.LogHandler.add_log_record("General settings file updated.")


class SplashScreen(QFrame):
    def __init__(self, **kwargs) -> None:
        """
        kwargs:
            size (QSize, tuple): Window size
            background_image (str): Window background image
            splash_image (str): Small image on left side of window
            title (str): Big text right top
            detail (str): Small text right bottom (Can be updated)
        """
        super().__init__(None)

        # Variables
        size = kwargs.get("size") if kwargs.get("size") else QSize(400, 200)
        if isinstance(size, tuple):
            size = QSize(*size)
        background_image = kwargs.get("background_image")
        splash_image = kwargs.get("splash_image")
        title = kwargs.get("title", "Loading...")
        detail = kwargs.get("detail", "Please wait...")

        self._msg_counter = 0
        self._msg_text = ""

        # Frame setup
        self.setWindowFlags(Qt.SplashScreen)
        desktop_w = QDesktopWidget()
        self.move(int(desktop_w.width() / 2 - size.width() / 2), int(desktop_w.height() / 2 - size.height() / 2))
        self.resize(size)
        self.setStyleSheet("QFrame {background-color: transparent; color: #ffff00; font-size: 20pt; border: 2px solid #ffff00; border-radius: 8;}")

        # Background image label
        self.lbl_bg = QLabel(self)
        self.lbl_bg.move(2, 2)
        self.lbl_bg.resize(size.width() - 4, size.height() - 4)
        self.lbl_bg.setScaledContents(True)
        self.lbl_bg.setStyleSheet("QLabel {background-color: #0000ff; border: 1px solid #000000; border-radius: 8;}")
        if background_image:
            self.lbl_bg.setPixmap(QPixmap(background_image))
        
        # Image label
        self.lbl_pic = QLabel(self)
        self.lbl_pic.move(5, 5)
        self.lbl_pic.resize(size.height() - 10, size.height() - 10)
        self.lbl_pic.setAlignment(Qt.AlignCenter)
        self.lbl_pic.setScaledContents(True)
        self.lbl_pic.setStyleSheet("QLabel {background-color: transparent; border: 0px;}")
        if splash_image:
            self.lbl_pic.setPixmap(QPixmap(splash_image))

        scale_h = (self.height() - 10) / 4
        title_h = int(scale_h)
        detail_h = int(scale_h * 2.4)
        # Title label
        self.lbl_title = QLabel(self)
        self.lbl_title.move(self.lbl_pic.width() + 10, 5)
        self.lbl_title.resize((size.width() - 5) - self.lbl_title.pos().x(), title_h)
        self.lbl_title.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("QLabel {background-color: transparent; color: #ffff00; border: 0px; font-size: 20pt;}")
        self.lbl_title.setText(title)

        # Detail label
        self.lbl_detail = QLabel(self)
        self.lbl_detail.move(self.lbl_pic.width() + 10, int(self.lbl_title.height() + 5))
        self.lbl_detail.resize((size.width() - 5) - self.lbl_detail.pos().x(), detail_h)
        self.lbl_detail.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.lbl_detail.setWordWrap(True)
        self.lbl_detail.setStyleSheet("QLabel {background-color: transparent; color: #ffffff; border: 0px; font-size: 12pt;}")
        self.update(detail)

        self.show()

    def update(self, text: str):
        if not text:
            return
        if self._msg_text:
            if self._msg_text.endswith("%"):
                self._msg_text = self._msg_text.rstrip(" 7894561230%")

            if text.find("%") != -1:
                self._msg_text += " " + text
            else:
                self._msg_text += "\n" + text
        else:
            self._msg_text = text

        step = int(190 / len(self._msg_text.splitlines()))
        
        text_to_html = UTILS.HTMLText.TextToHTML()

        count = 0
        html_text = ""
        for line in self._msg_text.splitlines():
            color_fix = 50 + (step * count)
            if color_fix < 50:
                color_fix = 50

            color_fix = f"rgb({color_fix},{color_fix},{color_fix})"

            rule_id = "#" + "-" * (5 - len(str(count))) + str(count)

            html_text += f"{rule_id}\n"

            if count == len(self._msg_text.splitlines()) - 1:
                font_bold = True
                color_fix = "#ffff00"
            else:
                font_bold = False

            text_to_html.add_rule(
                UTILS.HTMLText.TextToHtmlRule(
                    text=rule_id,
                    replace_with=line,
                    fg_color=color_fix,
                    font_bold=font_bold
                )
            )
            count += 1
        
        html_text = html_text.strip()
        text_to_html.set_text(html_text)

        self.lbl_detail.setText(text_to_html.get_html())
        self.repaint()

    def close_me(self):
        self.hide()
        self.deleteLater()


class MyJournal(QMainWindow):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.log_messages_window = None
        
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
        # Add Dialog Queue
        stt.app_setting_add("cm", utility_cls.DialogsQueue())
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
        # Global Widgets properties
        stt.app_setting_add("global_widgets_properties", qwidgets_util_cls.GlobalWidgetsProperties(self._get_global_widgets_properties()))
        # DataBase Objects
        splash.update(getl("splash_loading_tags"))
        stt.app_setting_add("tags", obj_tags.Tags(stt, feedback_percent_function=self._data_object_loaded_percent))
        splash.update(getl("splash_loading_images"))
        stt.app_setting_add("images", obj_images.Images(stt, feedback_percent_function=self._data_object_loaded_percent))
        splash.update(getl("splash_loading_files"))
        stt.app_setting_add("files", obj_files.Files(stt, feedback_percent_function=self._data_object_loaded_percent))
        splash.update(getl("splash_loading_blocks"))
        stt.app_setting_add("blocks", obj_blocks.Blocks(stt, feedback_percent_function=self._data_object_loaded_percent))
        splash.update(getl("splash_loading_defs"))
        stt.app_setting_add("defs", obj_definitions.Definitions(stt, feedback_percent_function=self._data_object_loaded_percent))
        splash.update(getl("splash_loading_ac_data"))
        stt.app_setting_add("ac_data", AutoCompleteData(stt))
        splash.update(getl("splash_loading_text_handler_data"))
        stt.app_setting_add("text_handler_data", TextHandlerData(stt))
        
        splash.update(getl("splash_loading_finish"))

        self.timers = timer_cls.TimerHandler(parent=self)

    def start_gui(self):
        # Define widgets, setup language and appearance
        self._define_widgets()
        self._setup_widgets_language()

        # Add QLabel in QScrollArea
        self.area_widget.layout().addWidget(self.area_label)
        if not getv("scroll_area_show_label_widget"):
            self.area_label.setText("")

        self._setup_widgets_appearance()

        # Setup Widgets Handler
        self.load_widgets_handler()
        
        # Define menu sound effects
        self.main_menu_sound = UTILS.SoundUtility(getv("main_menu_sound_file_path"), volume=getv("volume_value"), muted=getv("volume_muted"))
        self.menu_item_sound = UTILS.SoundUtility(getv("menu_item_sound_file_path"), volume=getv("volume_value"), muted=getv("volume_muted"))
        self.volume_muted_sound = UTILS.SoundUtility(getv("set_muted_sound_file_path"), force_sound=True)
        self.volume_unmuted_sound = UTILS.SoundUtility(getv("set_unmuted_sound_file_path"), force_sound=True)

        # Load user settings, Window pos, size, toolbar pos...
        self._load_user_widget_settings()

        self.show()

        self._animate_window_title()

        # Show Fun Facts
        if getv("fun_fact_show_on_start"):
            utility_cls.FunFactShow(stt, self)
        # Check is there draft records and ask user to show them
        self.ask_to_open_drafts_on_start()
        # Check crash dictionary:
        if self.crash_dict is None:
            self.crash_dict = {}
        if user.username in self.crash_dict:
            if "def" in self.crash_dict[user.username]:
                log.write_log("Warning. Last session crashed...: Definition Add/Edit resuming...")
                definition_cls.AddDefinition(stt, self, crash_dict=self.crash_dict)
        
        # Connect events with slots
        get_appv("signal").signal_app_settings_updated.connect(self.app_setting_updated)
        self.closeEvent = self._close_event
        self.area_label.mousePressEvent = self.area_label_mouse_press
        # Status bar Volume Control
        self.btn_volume.clicked.connect(self.btn_volume_clicked)
        self.sld_volume.valueChanged.connect(self.sld_volume_value_changed)
        self.sld_volume.mousePressEvent = self.sld_volume_mouse_press
        self.sld_volume.mouseReleaseEvent = self.sld_volume_mouse_release
        # Status bar Logs Button
        self.btn_logs.clicked.connect(self.btn_logs_click)
        UTILS.Signal.signalLogUpdated.connect(self.log_messages_updated)
        # Menu / ToolBar events
        self.toolBar.orientationChanged.connect(self._toolbar_areas_changed)
        self.toolBar.actionTriggered.connect(self._close_context_dialogs)
        self.menu_file.aboutToShow.connect(self.main_menu_about_to_show)
        self.menu_edit.aboutToShow.connect(self.main_menu_about_to_show)
        self.menu_view.aboutToShow.connect(self.main_menu_about_to_show)
        self.menu_user.aboutToShow.connect(self.main_menu_about_to_show)
        self.menu_tags.aboutToShow.connect(self.main_menu_about_to_show)
        self.menu_help.aboutToShow.connect(self.main_menu_about_to_show)

        # File menu
        self.mnu_file_app_settings.triggered.connect(self.mnu_file_app_settings_triggered)
        self.mnu_import_blocks.triggered.connect(self.mnu_import_blocks_triggered)
        self.mnu_export_blocks.triggered.connect(self.mnu_export_blocks_triggered)
        self.mnu_import_def.triggered.connect(self.mnu_import_def_triggered)
        self.mnu_export_def.triggered.connect(self.mnu_export_def_triggered)
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
        # Help menu
        self.mnu_help_log_messages.triggered.connect(self.mnu_help_log_messages_triggered)
        self.mnu_help_statistic.triggered.connect(self.mnu_help_statistic_triggered)
        # TMP
        self.mnu_open.triggered.connect(self.mnu_open_click)

        UTILS.LogHandler.add_log_record("Main class #1 started ... application is visible.", ["MyJournal"])
        self.show_welcome_notification()

    def _data_object_loaded_percent(self, percent: int):
        if splash is not None:
            splash.update(f"{percent} %")

    def getv(self, key_id: str):
        return getv(key_id)

    def btn_volume_clicked(self):
        self._close_context_dialogs()
        setv("volume_muted", not getv("volume_muted"))
        
        if getv("volume_muted"):
            if getv("allow_volume_muted_sound"):
                self.volume_muted_sound.play()
        else:
            if getv("allow_volume_unmuted_sound"):
                self.volume_unmuted_sound.play()

        self.update_volume_status()
        UTILS.LogHandler.add_log_record(
            message="Volume #1 button clicked.",
            arguments=["enable/disable"],
            variables=[
                ["Setting(volume_muted)", getv("volume_muted")]
            ]
        )

    # Here we receive info from WinBlock...
    def events(self, event_dict: dict):
        variables = [[f"event_dict[{detail_key}]", detail_value] for detail_key, detail_value in event_dict.items()]
        clip: utility_cls.Clipboard = get_appv("cb")
        variables.append(["Clipboard blocks & Definitions", clip.ID_DELIMITER.join(clip._clip_get_all_ids())])
        UTILS.LogHandler.add_log_record("#1 class custom event triggered. [#2 -> #3]", ["MyJournal", event_dict.get("name"), event_dict.get("action")], variables=variables)
        
        if event_dict["name"] == "block_clipboard":
            if event_dict["action"] == "copy":
                clip.block_clip_copy_blocks(event_dict.get("id"))
            elif event_dict["action"] == "copy_add":
                clip.block_clip_add_blocks(event_dict.get("id"))
            elif event_dict["action"] == "remove":
                clip.block_clip_remove_all_blocks(event_dict.get("id"))
            elif event_dict["action"] == "send_to_export":
                for widget in self.children():
                    if isinstance(widget, export_import_cls.ExportImport):
                        widget.send_to(event_dict.get("id"), "block")
                        break
                else:
                    widget = export_import_cls.ExportImport(stt, self, "export_blocks")
                    widget.send_to(event_dict.get("id"), "block")
        if event_dict["name"] == "definition_clipboard":
            if event_dict["action"] == "copy":
                clip.def_clip_copy_defs(event_dict.get("id"))
            elif event_dict["action"] == "copy_add":
                clip.def_clip_add_defs(event_dict.get("id"))
            elif event_dict["action"] == "remove":
                clip.def_clip_remove_all_defs(event_dict.get("id"))
            elif event_dict["action"] == "send_to_export":
                for widget in self.children():
                    if isinstance(widget, export_import_cls.ExportImport):
                        widget.send_to(event_dict.get("id"), "def")
                        break
                else:
                    widget = export_import_cls.ExportImport(stt, self, "export_defs")
                    widget.send_to(event_dict.get("id"), "def")
        if event_dict["name"] == "delayed_action":
            if event_dict["action"] == "try_to_close_me":
                try:
                    timer = timer_cls.ContinuousTimer(self.timers, interval=250, duration=event_dict.get("duration", 60000), function_on_timeout=self.dialog_try_to_close_me_later_timeout, function_on_finished=self.dialog_try_to_close_me_later_finished)
                    self.timers.add_timer(timer)
                    timer.set_data({"object": event_dict["self"], "issue": event_dict.get("issue"), "dialog_name": event_dict.get("dialog_name", "Unknown"), "validate_function": event_dict.get("validate_function"), "execute_function": event_dict.get("execute_function")})
                    timer.start()
                    timer = None
                except Exception as e:
                    UTILS.TerminalUtility.WarningMessage(message=f"#1: Error in #2 function.\n#3", arguments=["MainWin", "events", str(e)])
        if event_dict["name"] == "win_block":
            if event_dict["action"] == "open_new_block":
                self.add_block()
            elif event_dict["action"] == "block_closed":
                pass
            elif event_dict["action"] == "try_to_close_me":
                try:
                    timer = timer_cls.ContinuousTimer(self.timers, interval=250, duration=60000, function_on_timeout=self.block_timer_timeout, function_on_finished=self.block_timer_finished)
                    self.timers.add_timer(timer)
                    timer.set_data({"object": event_dict["object"], "id": event_dict["id"], "validation": event_dict["validation"], "object_type": "Block", "execute_function": event_dict.get("execute_function")})
                    timer.start()
                    timer = None
                except Exception as e:
                    UTILS.TerminalUtility.WarningMessage(message=f"#1: Error in #2 function.\n#3", arguments=["MainWin", "events", str(e)])
        if event_dict["name"] == "notification":
            if event_dict["action"] == "try_to_close_me":
                try:
                    timer = timer_cls.ContinuousTimer(self.timers, interval=250, duration=60000, function_on_timeout=self.block_timer_timeout, function_on_finished=self.block_timer_finished)
                    self.timers.add_timer(timer)
                    timer.set_data({"object": event_dict["object"], "id": event_dict.get("id"), "validation": event_dict["validation"], "object_type": "Notification", "execute_function": event_dict.get("execute_function")})
                    timer.start()
                    timer = None
                except Exception as e:
                    UTILS.TerminalUtility.WarningMessage(message=f"#1: Error in #2 function.\n#3", arguments=["MainWin", "events", str(e)])
        if event_dict["name"] == "block_view":
            if event_dict["action"] == "block_ids":
                return [
                    self.area_widget.layout().itemAt(i).widget()._active_record_id
                    for i in range(self.area_widget.layout().count())
                    if isinstance(
                        self.area_widget.layout().itemAt(i).widget(),
                        block_cls.WinBlock,
                    )
                ]
        if event_dict["name"] == "pic_info":
            if event_dict["action"] == "open_block":
                diary_view_cls.BlockView(stt, self, block_ids=event_dict["id"], auto_open_ids=event_dict["id"])
            if event_dict["action"] == "open_def":
                definition_cls.ViewDefinition(stt, self, event_dict["id"])

        if event_dict["name"] == "find_in_app":
            self._start_specific_dialog(event_dict)
        
        if event_dict["name"] == "export_import":
            notif_duration = 2500
            if event_dict["action"] == "block_exported":
                self._notification_export_import(event_dict.get("title", "Block Export"), event_dict.get("text", "Blocks have been exported."), event_dict.get("duration", notif_duration), event_dict.get("icon", None))
            elif event_dict["action"] == "def_exported":
                self._notification_export_import(event_dict.get("title", "Definition Export"), event_dict.get("text", "Definitions have been exported."), event_dict.get("duration", notif_duration), event_dict.get("icon", None))
            elif event_dict["action"] == "block_imported":
                self._notification_export_import(event_dict.get("title", "Block Import"), event_dict.get("text", "Blocks have been imported."), event_dict.get("duration", notif_duration), event_dict.get("icon", None))
            elif event_dict["action"] == "def_imported":
                self._notification_export_import(event_dict.get("title", "Definition Import"), event_dict.get("text", "Definitions have been imported."), event_dict.get("duration", notif_duration), event_dict.get("icon", None))
        
        if event_dict["name"] == "start_dialog":
            if event_dict["action"] == "BlockView":
                diary_view_cls.BlockView(stt, self, event_dict.get("ids"))
            if event_dict["action"] == "BrowseDefinitions":
                definition_cls.BrowseDefinitions(stt, self, event_dict.get("ids"))

        if event_dict["name"] == "open_block":
            block_id = event_dict.get("id")
            if isinstance(block_id, str):
                if block_id.find(":") != -1:
                    for i in block_id.split(":"):
                        if UTILS.TextUtility.get_integer(i):
                            block_id = UTILS.TextUtility.get_integer(i)
                            break
                block_id = UTILS.TextUtility.get_integer(block_id)

            block_collapsed = event_dict.get("collapsed", False)
            block_animate = event_dict.get("animate")
            db_rec = db_record_cls.Record(stt)
            if db_rec.is_valid_record_id(block_id) or block_id == 0:
                self.add_block(record_id=block_id, collapsed=block_collapsed, animate=block_animate)
                return True
            return False
        
        if event_dict["name"] == "close_block":
            success = False
            block_id = event_dict.get("id")
            if isinstance(block_id, str):
                if block_id.find(":") != -1:
                    for i in block_id.split(":"):
                        if UTILS.TextUtility.get_integer(i):
                            block_id = UTILS.TextUtility.get_integer(i)
                            break
                block_id = UTILS.TextUtility.get_integer(block_id)

            for idx in range(self.area_widget.layout().count()):
                if self.area_widget.layout().itemAt(idx) and isinstance(self.area_widget.layout().itemAt(idx).widget(), block_cls.WinBlock):
                    if self.area_widget.layout().itemAt(idx).widget()._active_record_id == block_id:
                        self.area_widget.layout().itemAt(idx).widget().close_me()
                        success = True
                        break
            app.processEvents()
            return success

    def _notification_export_import(self, title: str, text: str, duration: int = 2500, icon_path: str = None):
        notif_dict = {
            "title": title,
            "text": text,
            "timer": duration,
            "icon": icon_path
        }
        utility_cls.Notification(stt, self, notif_dict)

    def btn_logs_click(self):
        self._close_context_dialogs()
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()

        self.show_log_messages()

    def log_messages_updated(self, data: dict, log_data: dict):
        number_of_messages = data.get("number_of_messages_in_last_log")
        if not number_of_messages:
            number_of_messages = 0
        else:
            number_of_messages -= 1
        
        if number_of_messages:
            self.btn_logs.setText(f'{getl("btn_logs_text")} ({number_of_messages})')
        else:
            self.btn_logs.setText(getl("btn_logs_text"))

    def dialog_try_to_close_me_later_timeout(self, timer: timer_cls.ContinuousTimer):
        validate_function = timer.get_data().get("validate_function", None)
        if validate_function is None:
            result = True
        else:
            result = validate_function()

        if result:
            execute_function = timer.get_data().get("execute_function", None)
            if execute_function is not None:
                execute_function()

            UTILS.TerminalUtility.WarningMessage("#1 is preventing #2 from closing.\nResponded after #3 milliseconds.\nWindow is successfully closed.", [timer.get_data().get("issue", "Unknown"), timer.get_data().get("dialog_name", "Unknown"), f"{timer.get_elapsed_time():,.0f}"])
            timer.stop()
            self.timers.remove_timer(timer)

    def dialog_try_to_close_me_later_finished(self, timer: timer_cls.ContinuousTimer):
        UTILS.TerminalUtility.WarningMessage("#1 is preventing #2 from closing.\nDid not respond after #3 milliseconds.\n#4\nQDialog will be deleted once you exit the app.", [timer.get_data().get("issue", "Unknown"), timer.get_data().get("dialog_name", "Unknown"), f"{timer.get_duration():,.0f}", "Unable to delete QDialog object."])
        timer.stop()
        self.timers.remove_timer(timer)

    def block_timer_timeout(self, timer: timer_cls.ContinuousTimer):
        result = timer.data["validation"]()
        if result:
            timer.stop()
            variables = []
            if timer.data:
                variables = [[f"timer.data[{timer_key}]", timer_val] for timer_key, timer_val in timer.data.items()]
            if timer.data.get("terminal_output"):
                UTILS.TerminalUtility.WarningMessage("#1: Animation is preventing #2 from closing.\nResponded after #3 milliseconds.\n#2 is successfully closed.", ["MyJournal", timer.data['object_type'], f"{timer.get_elapsed_time():,.0f}"], variables=variables)
            else:
                variables.append([f"timer.get_duration", timer.get_duration()])
                variables.append([f"timer.get_elapsed_time", timer.get_elapsed_time()])
                variables.append([f"timer.get_total_remaining_time", timer.get_total_remaining_time()])
                UTILS.LogHandler.add_log_record(
                    "#1: Animation is preventing #2 from closing.\nResponded after #3 milliseconds.\n#2 is successfully closed.",
                    ["MyJournal", timer.data['object_type'], f"{timer.get_elapsed_time():,.0f}"],
                    variables=variables)
            if timer.data.get("execute_function"):
                try:
                    timer.data["execute_function"]()
                except Exception as e:
                    UTILS.TerminalUtility.WarningMessage("#1: Exception in #2 -> #3. Unable to execute #4\n#5", ["MyJournal", "block_timer_timeout", "execute_function", "timer.data['execute_function']", str(e)])
            self.timers.remove_timer(timer)

    def block_timer_finished(self, timer: timer_cls.ContinuousTimer):
        variables = []
        if timer.data:
            variables = [[f"timer.data[{timer_key}]", timer_val] for timer_key, timer_val in timer.data.items()]
        if timer.data.get("terminal_output"):
            UTILS.TerminalUtility.WarningMessage("Animation is preventing #1 from closing.\nDid not respond after #2 milliseconds.\n#3\nBlock will be deleted once you exit the app.", [timer.data['object_type'], f"{timer.get_duration():,.0f}", "Unable to delete Block object."], variables=variables)
        else:
            variables.append([f"timer.get_duration", timer.get_duration()])
            variables.append([f"timer.get_elapsed_time", timer.get_elapsed_time()])
            variables.append([f"timer.get_total_remaining_time", timer.get_total_remaining_time()])
            UTILS.LogHandler.add_log_record(
                "#1: Animation is preventing #2 from closing.\nDid not respond after #3 milliseconds.\n#4\nBlock will be deleted once you exit the app.",
                ["MyJournal", timer.data['object_type'], f"{timer.get_duration():,.0f}", "Unable to delete Block object."],
                variables=variables)
        timer.stop()
        self.timers.remove_timer(timer)

    def load_widgets_handler(self):
        global_properties = get_appv("global_widgets_properties")
        self.widget_handler = qwidgets_util_cls.WidgetHandler(
            main_win=self,
            global_widgets_properties=global_properties)
        
        # Add Dialog
        handle_dialog: qwidgets_util_cls.Widget_Dialog = self.widget_handler.add_QDialog(self)
        handle_dialog.properties.allow_drag_widgets_cursor_change = False
        handle_dialog.add_window_drag_widgets([self.area_label])
        handle_dialog.properties.allow_bypass_key_press_event = False

        # Add frames

        # Add all Pushbuttons
        for i in self.toolBar.children():
            if isinstance(i, QToolButton):
                self.widget_handler.add_QPushButton(i)

        # Add Labels as PushButtons

        # Add Action Frames

        # Add TextBox

        # Add Selection Widgets

        self.widget_handler.activate()

    def _get_global_widgets_properties(self) -> dict:
        result = {
            "Widget_PushButton_Properties": {
                # Pushbutton cursor
                "allow_cursor_change": getv("gwp_qpushbutton_allow_cursor_change"),
                "cursor": getv("gwp_qpushbutton_cursor"),
                "cursor_width": getv("gwp_qpushbutton_cursor_width"),
                "cursor_height": getv("gwp_qpushbutton_cursor_height"),
                "cursor_keep_aspect_ratio": getv("gwp_qpushbutton_cursor_keep_aspect_ratio"),
                # Allow bypass mouse press event
                "allow_bypass_mouse_press_event": True,
                # Tap event - animation
                "tap_event_show_animation_enabled": getv("gwp_qpushbutton_tap_event_show_animation_enabled"),
                "tap_event_show_animation_file_path": getv("gwp_qpushbutton_tap_event_show_animation_file_path"),
                "tap_event_show_animation_duration_ms": getv("gwp_qpushbutton_tap_event_show_animation_duration_ms"),
                "tap_event_show_animation_width": getv("gwp_qpushbutton_tap_event_show_animation_width"),
                "tap_event_show_animation_height": getv("gwp_qpushbutton_tap_event_show_animation_height"),
                "tap_event_show_animation_background_color": getv("gwp_qpushbutton_tap_event_show_animation_background_color"),
                # Tap event - play sound
                "tap_event_play_sound_enabled": getv("gwp_qpushbutton_tap_event_play_sound_enabled"),
                "tap_event_play_sound_file_path": getv("gwp_qpushbutton_tap_event_play_sound_file_path"),
                # Tap event - change stylesheet
                "tap_event_change_stylesheet_enabled": getv("gwp_qpushbutton_tap_event_change_stylesheet_enabled"),
                "tap_event_change_qss_stylesheet": getv("gwp_qpushbutton_tap_event_change_qss_stylesheet"),
                "tap_event_change_stylesheet_duration_ms": getv("gwp_qpushbutton_tap_event_change_stylesheet_duration_ms"),
                # Tap event - change size
                "tap_event_change_size_enabled": getv("gwp_qpushbutton_tap_event_change_size_enabled"),
                "tap_event_change_size_percent": getv("gwp_qpushbutton_tap_event_change_size_percent"),
                "tap_event_change_size_duration_ms": getv("gwp_qpushbutton_tap_event_change_size_duration_ms"),
                # Allow bypass enter event
                "allow_bypass_enter_event": True,
                # Enter event - animation
                "enter_event_show_animation_enabled": getv("gwp_qpushbutton_enter_event_show_animation_enabled"),
                "enter_event_show_animation_file_path": getv("gwp_qpushbutton_enter_event_show_animation_file_path"),
                "enter_event_show_animation_duration_ms": getv("gwp_qpushbutton_enter_event_show_animation_duration_ms"),
                "enter_event_show_animation_width": getv("gwp_qpushbutton_enter_event_show_animation_width"),
                "enter_event_show_animation_height": getv("gwp_qpushbutton_enter_event_show_animation_height"),
                "enter_event_show_animation_background_color": getv("gwp_qpushbutton_enter_event_show_animation_background_color"),
                # Enter event - play sound
                "enter_event_play_sound_enabled": getv("gwp_qpushbutton_enter_event_play_sound_enabled"),
                "enter_event_play_sound_file_path": getv("gwp_qpushbutton_enter_event_play_sound_file_path"),
                # Enter event - change stylesheet
                "enter_event_change_stylesheet_enabled": getv("gwp_qpushbutton_enter_event_change_stylesheet_enabled"),
                "enter_event_change_qss_stylesheet": getv("gwp_qpushbutton_enter_event_change_qss_stylesheet"),
                "enter_event_change_stylesheet_duration_ms": getv("gwp_qpushbutton_enter_event_change_stylesheet_duration_ms"),
                # Enter event - change size
                "enter_event_change_size_enabled": getv("gwp_qpushbutton_enter_event_change_size_enabled"),
                "enter_event_change_size_percent": getv("gwp_qpushbutton_enter_event_change_size_percent"),
                "enter_event_change_size_duration_ms": getv("gwp_qpushbutton_enter_event_change_size_duration_ms"),
                # Allow bypass leave event
                "allow_bypass_leave_event": True,
                # Leave event - animation
                "leave_event_show_animation_enabled": getv("gwp_qpushbutton_leave_event_show_animation_enabled"),
                "leave_event_show_animation_file_path": getv("gwp_qpushbutton_leave_event_show_animation_file_path"),
                "leave_event_show_animation_duration_ms": getv("gwp_qpushbutton_leave_event_show_animation_duration_ms"),
                "leave_event_show_animation_width": getv("gwp_qpushbutton_leave_event_show_animation_width"),
                "leave_event_show_animation_height": getv("gwp_qpushbutton_leave_event_show_animation_height"),
                "leave_event_show_animation_background_color": getv("gwp_qpushbutton_leave_event_show_animation_background_color"),
                # Leave event - play sound
                "leave_event_play_sound_enabled": getv("gwp_qpushbutton_leave_event_play_sound_enabled"),
                "leave_event_play_sound_file_path": getv("gwp_qpushbutton_leave_event_play_sound_file_path"),
                # Leave event - change stylesheet
                "leave_event_change_stylesheet_enabled": getv("gwp_qpushbutton_leave_event_change_stylesheet_enabled"),
                "leave_event_change_qss_stylesheet": getv("gwp_qpushbutton_leave_event_change_qss_stylesheet"),
                "leave_event_change_stylesheet_duration_ms": getv("gwp_qpushbutton_leave_event_change_stylesheet_duration_ms"),
                # Leave event - change size
                "leave_event_change_size_enabled": getv("gwp_qpushbutton_leave_event_change_size_enabled"),
                "leave_event_change_size_percent": getv("gwp_qpushbutton_leave_event_change_size_percent"),
                "leave_event_change_size_duration_ms": getv("gwp_qpushbutton_leave_event_change_size_duration_ms"),
            },
            "Widget_ActionFrame_Properties": {
                # Pushbutton cursor
                "allow_cursor_change": getv("gwp_actionframe_allow_cursor_change"),
                "cursor": getv("gwp_actionframe_cursor"),
                "cursor_width": getv("gwp_actionframe_cursor_width"),
                "cursor_height": getv("gwp_actionframe_cursor_height"),
                "cursor_keep_aspect_ratio": getv("gwp_actionframe_cursor_keep_aspect_ratio"),
                # Allow bypass mouse press event
                "allow_bypass_mouse_press_event": True,
                # Tap event - animation
                "tap_event_show_animation_enabled": getv("gwp_actionframe_tap_event_show_animation_enabled"),
                "tap_event_show_animation_file_path": getv("gwp_actionframe_tap_event_show_animation_file_path"),
                "tap_event_show_animation_duration_ms": getv("gwp_actionframe_tap_event_show_animation_duration_ms"),
                "tap_event_show_animation_width": getv("gwp_actionframe_tap_event_show_animation_width"),
                "tap_event_show_animation_height": getv("gwp_actionframe_tap_event_show_animation_height"),
                "tap_event_show_animation_background_color": getv("gwp_actionframe_tap_event_show_animation_background_color"),
                # Tap event - play sound
                "tap_event_play_sound_enabled": getv("gwp_actionframe_tap_event_play_sound_enabled"),
                "tap_event_play_sound_file_path": getv("gwp_actionframe_tap_event_play_sound_file_path"),
                # Tap event - change stylesheet
                "tap_event_change_stylesheet_enabled": getv("gwp_actionframe_tap_event_change_stylesheet_enabled"),
                "tap_event_change_qss_stylesheet": getv("gwp_actionframe_tap_event_change_qss_stylesheet"),
                "tap_event_change_stylesheet_duration_ms": getv("gwp_actionframe_tap_event_change_stylesheet_duration_ms"),
                # Tap event - change size
                "tap_event_change_size_enabled": getv("gwp_actionframe_tap_event_change_size_enabled"),
                "tap_event_change_size_percent": getv("gwp_actionframe_tap_event_change_size_percent"),
                "tap_event_change_size_duration_ms": getv("gwp_actionframe_tap_event_change_size_duration_ms"),
                # Allow bypass enter event
                "allow_bypass_enter_event": True,
                # Enter event - animation
                "enter_event_show_animation_enabled": getv("gwp_actionframe_enter_event_show_animation_enabled"),
                "enter_event_show_animation_file_path": getv("gwp_actionframe_enter_event_show_animation_file_path"),
                "enter_event_show_animation_duration_ms": getv("gwp_actionframe_enter_event_show_animation_duration_ms"),
                "enter_event_show_animation_width": getv("gwp_actionframe_enter_event_show_animation_width"),
                "enter_event_show_animation_height": getv("gwp_actionframe_enter_event_show_animation_height"),
                "enter_event_show_animation_background_color": getv("gwp_actionframe_enter_event_show_animation_background_color"),
                # Enter event - play sound
                "enter_event_play_sound_enabled": getv("gwp_actionframe_enter_event_play_sound_enabled"),
                "enter_event_play_sound_file_path": getv("gwp_actionframe_enter_event_play_sound_file_path"),
                # Enter event - change stylesheet
                "enter_event_change_stylesheet_enabled": getv("gwp_actionframe_enter_event_change_stylesheet_enabled"),
                "enter_event_change_qss_stylesheet": getv("gwp_actionframe_enter_event_change_qss_stylesheet"),
                "enter_event_change_stylesheet_duration_ms": getv("gwp_actionframe_enter_event_change_stylesheet_duration_ms"),
                # Enter event - change size
                "enter_event_change_size_enabled": getv("gwp_actionframe_enter_event_change_size_enabled"),
                "enter_event_change_size_percent": getv("gwp_actionframe_enter_event_change_size_percent"),
                "enter_event_change_size_duration_ms": getv("gwp_actionframe_enter_event_change_size_duration_ms"),
                # Allow bypass leave event
                "allow_bypass_leave_event": True,
                # Leave event - animation
                "leave_event_show_animation_enabled": getv("gwp_actionframe_leave_event_show_animation_enabled"),
                "leave_event_show_animation_file_path": getv("gwp_actionframe_leave_event_show_animation_file_path"),
                "leave_event_show_animation_duration_ms": getv("gwp_actionframe_leave_event_show_animation_duration_ms"),
                "leave_event_show_animation_width": getv("gwp_actionframe_leave_event_show_animation_width"),
                "leave_event_show_animation_height": getv("gwp_actionframe_leave_event_show_animation_height"),
                "leave_event_show_animation_background_color": getv("gwp_actionframe_leave_event_show_animation_background_color"),
                # Leave event - play sound
                "leave_event_play_sound_enabled": getv("gwp_actionframe_leave_event_play_sound_enabled"),
                "leave_event_play_sound_file_path": getv("gwp_actionframe_leave_event_play_sound_file_path"),
                # Leave event - change stylesheet
                "leave_event_change_stylesheet_enabled": getv("gwp_actionframe_leave_event_change_stylesheet_enabled"),
                "leave_event_change_qss_stylesheet": getv("gwp_actionframe_leave_event_change_qss_stylesheet"),
                "leave_event_change_stylesheet_duration_ms": getv("gwp_actionframe_leave_event_change_stylesheet_duration_ms"),
                # Leave event - change size
                "leave_event_change_size_enabled": getv("gwp_actionframe_leave_event_change_size_enabled"),
                "leave_event_change_size_percent": getv("gwp_actionframe_leave_event_change_size_percent"),
                "leave_event_change_size_duration_ms": getv("gwp_actionframe_leave_event_change_size_duration_ms"),
            },
            "Widget_Dialog_Properties": {
                # Window dragging
                "window_drag_enabled": getv("gwp_qdialog_window_drag_enabled"),
                "window_drag_enabled_with_body": getv("gwp_qdialog_window_drag_enabled_with_body"),
                # Window dragging cursor change
                "allow_drag_widgets_cursor_change": getv("gwp_qdialog_allow_drag_widgets_cursor_change"),
                "start_drag_cursor": getv("gwp_qdialog_start_drag_cursor"),
                "end_drag_cursor": getv("gwp_qdialog_end_drag_cursor"),
                "cursor_keep_aspect_ratio": getv("gwp_qdialog_cursor_keep_aspect_ratio"),
                "cursor_width": getv("gwp_qdialog_cursor_width"),
                "cursor_height": getv("gwp_qdialog_cursor_height"),
                # Mask label
                "dragged_window_mask_label_enabled": getv("gwp_qdialog_dragged_window_mask_label_enabled"),
                "dragged_window_mask_label_stylesheet": getv("gwp_qdialog_dragged_window_mask_label_stylesheet"),
                "dragged_window_mask_label_image_path": getv("gwp_qdialog_dragged_window_mask_label_image_path"),
                "dragged_window_mask_label_animation_path": getv("gwp_qdialog_dragged_window_mask_label_animation_path"),
                # Call Close_me on ESCAPE
                "allow_bypass_key_press_event": True,
                "call_close_me_on_escape": True,
                # Close on Lost Focus
                "close_on_lost_focus": False,
            },
            "Widget_Frame_Properties": {
                # Window dragging
                "window_drag_enabled": getv("gwp_qframe_window_drag_enabled"),
                "window_drag_enabled_with_body": getv("gwp_qframe_window_drag_enabled_with_body"),
                # Window dragging cursor change
                "allow_drag_widgets_cursor_change": getv("gwp_qframe_allow_drag_widgets_cursor_change"),
                "start_drag_cursor": getv("gwp_qframe_start_drag_cursor"),
                "end_drag_cursor": getv("gwp_qframe_end_drag_cursor"),
                "cursor_keep_aspect_ratio": getv("gwp_qframe_cursor_keep_aspect_ratio"),
                "cursor_width": getv("gwp_qframe_cursor_width"),
                "cursor_height": getv("gwp_qframe_cursor_height"),
                # Change style and add mask label
                "dragged_window_change_stylesheet_enabled": getv("gwp_qframe_dragged_window_change_stylesheet_enabled"),
                "dragged_window_stylesheet": getv("gwp_qframe_dragged_window_stylesheet"),
                "dragged_window_mask_label_enabled": getv("gwp_qframe_dragged_window_mask_label_enabled"),
                "dragged_window_mask_label_stylesheet": getv("gwp_qframe_dragged_window_mask_label_stylesheet"),
                "dragged_window_mask_label_image_path": getv("gwp_qframe_dragged_window_mask_label_image_path"),
                "dragged_window_mask_label_animation_path": getv("gwp_qframe_dragged_window_mask_label_animation_path"),
            },
            "Widget_TextBox_Properties": {
                # Key press event
                "allow_bypass_key_press_event": True,
                # Key Pressed - Play Sound
                "key_pressed_sound_enabled": getv("gwp_qtextedit_key_pressed_sound_enabled"),
                "key_pressed_sound_file_path": getv("gwp_qtextedit_key_pressed_sound_file_path"),
                # Key Pressed - change stylesheet
                "key_pressed_change_stylesheet_enabled": getv("gwp_qtextedit_key_pressed_change_stylesheet_enabled"),
                "key_pressed_change_qss_stylesheet": getv("gwp_qtextedit_key_pressed_change_qss_stylesheet"),
                "key_pressed_change_stylesheet_duration_ms": getv("gwp_qtextedit_key_pressed_change_stylesheet_duration_ms"),
                # Key Pressed - change size
                "key_pressed_change_size_enabled": getv("gwp_qtextedit_key_pressed_change_size_enabled"),
                "key_pressed_change_size_percent": getv("gwp_qtextedit_key_pressed_change_size_percent"),
                "key_pressed_change_size_duration_ms": getv("gwp_qtextedit_key_pressed_change_size_duration_ms"),
                # RETURN Pressed - Play Sound
                "return_pressed_sound_enabled": getv("gwp_qtextedit_return_pressed_sound_enabled"),
                "return_pressed_sound_file_path": getv("gwp_qtextedit_return_pressed_sound_file_path"),
                # RETURN Pressed - change stylesheet
                "return_pressed_change_stylesheet_enabled": getv("gwp_qtextedit_return_pressed_change_stylesheet_enabled"),
                "return_pressed_change_qss_stylesheet": getv("gwp_qtextedit_return_pressed_change_qss_stylesheet"),
                "return_pressed_change_stylesheet_duration_ms": getv("gwp_qtextedit_return_pressed_change_stylesheet_duration_ms"),
                # RETURN Pressed - change size
                "return_pressed_change_size_enabled": getv("gwp_qtextedit_return_pressed_change_size_enabled"),
                "return_pressed_change_size_percent": getv("gwp_qtextedit_return_pressed_change_size_percent"),
                "return_pressed_change_size_duration_ms": getv("gwp_qtextedit_return_pressed_change_size_duration_ms"),
                # ESCAPE Pressed - Play Sound
                "escape_pressed_sound_enabled": getv("gwp_qtextedit_escape_pressed_sound_enabled"),
                "escape_pressed_sound_file_path": getv("gwp_qtextedit_escape_pressed_sound_file_path"),
                # ESCAPE Pressed - change stylesheet
                "escape_pressed_change_stylesheet_enabled": getv("gwp_qtextedit_escape_pressed_change_stylesheet_enabled"),
                "escape_pressed_change_qss_stylesheet": getv("gwp_qtextedit_escape_pressed_change_qss_stylesheet"),
                "escape_pressed_change_stylesheet_duration_ms": getv("gwp_qtextedit_escape_pressed_change_stylesheet_duration_ms"),
                # ESCAPE Pressed - change size
                "escape_pressed_change_size_enabled": getv("gwp_qtextedit_escape_pressed_change_size_enabled"),
                "escape_pressed_change_size_percent": getv("gwp_qtextedit_escape_pressed_change_size_percent"),
                "escape_pressed_change_size_duration_ms": getv("gwp_qtextedit_escape_pressed_change_size_duration_ms"),
                # Smart parenthesis
                "smart_parenthesis_enabled": getv("gwp_qtextedit_smart_parenthesis_enabled"),
                "smart_parenthesis_list": getv("gwp_qtextedit_smart_parenthesis_list"),
                # Smart parenthesis - Play Sound
                "smart_parenthesis_sound_enabled": getv("gwp_qtextedit_smart_parenthesis_sound_enabled"),
                "smart_parenthesis_success_sound_file_path": getv("gwp_qtextedit_smart_parenthesis_success_sound_file_path"),
                "smart_parenthesis_fail_sound_file_path": getv("gwp_qtextedit_smart_parenthesis_fail_sound_file_path"),
                # Smart parenthesis - change stylesheet
                "smart_parenthesis_change_stylesheet_enabled": getv("gwp_qtextedit_smart_parenthesis_change_stylesheet_enabled"),
                "smart_parenthesis_change_qss_stylesheet": getv("gwp_qtextedit_smart_parenthesis_change_qss_stylesheet"),
                "smart_parenthesis_change_stylesheet_duration_ms": getv("gwp_qtextedit_smart_parenthesis_change_stylesheet_duration_ms"),
                # Smart parenthesis - change size
                "smart_parenthesis_change_size_enabled": getv("gwp_qtextedit_smart_parenthesis_change_size_enabled"),
                "smart_parenthesis_change_size_percent": getv("gwp_qtextedit_smart_parenthesis_change_size_percent"),
                "smart_parenthesis_change_size_duration_ms": getv("gwp_qtextedit_smart_parenthesis_change_size_duration_ms"),
                # Illegal Entry - Play Sound
                "illegal_entry_sound_enabled": getv("gwp_qtextedit_illegal_entry_sound_enabled"),
                "illegal_entry_sound_file_path": getv("gwp_qtextedit_illegal_entry_sound_file_path"),
                # Illegal Entry - change stylesheet
                "illegal_entry_change_stylesheet_enabled": getv("gwp_qtextedit_illegal_entry_change_stylesheet_enabled"),
                "illegal_entry_change_qss_stylesheet": getv("gwp_qtextedit_illegal_entry_change_qss_stylesheet"),
                "illegal_entry_change_stylesheet_duration_ms": getv("gwp_qtextedit_illegal_entry_change_stylesheet_duration_ms"),
                # Illegal Entry - change size
                "illegal_entry_change_size_enabled": getv("gwp_qtextedit_illegal_entry_change_size_enabled"),
                "illegal_entry_change_size_percent": getv("gwp_qtextedit_illegal_entry_change_size_percent"),
                "illegal_entry_change_size_duration_ms": getv("gwp_qtextedit_illegal_entry_change_size_duration_ms"),
            },
            "Widget_Selection_Properties": {
                # Selection cursor
                "allow_cursor_change": getv("gwp_selection_allow_cursor_change"),
                "cursor": getv("gwp_selection_cursor"),
                "cursor_width": getv("gwp_selection_cursor_width"),
                "cursor_height": getv("gwp_selection_cursor_height"),
                "cursor_keep_aspect_ratio": getv("gwp_selection_cursor_keep_aspect_ratio"),
                # Allow bypass mouse press event
                "allow_bypass_mouse_press_event": True,
                # Tap event - animation
                "tap_event_show_animation_enabled": getv("gwp_selection_tap_event_show_animation_enabled"),
                "tap_event_show_animation_file_path": getv("gwp_selection_tap_event_show_animation_file_path"),
                "tap_event_show_animation_duration_ms": getv("gwp_selection_tap_event_show_animation_duration_ms"),
                "tap_event_show_animation_width": getv("gwp_selection_tap_event_show_animation_width"),
                "tap_event_show_animation_height": getv("gwp_selection_tap_event_show_animation_height"),
                "tap_event_show_animation_background_color": getv("gwp_selection_tap_event_show_animation_background_color"),
                # Tap event - play sound
                "tap_event_play_sound_enabled": getv("gwp_selection_tap_event_play_sound_enabled"),
                "tap_event_play_sound_file_path": getv("gwp_selection_tap_event_play_sound_file_path"),
                # Tap event - change stylesheet
                "tap_event_change_stylesheet_enabled": getv("gwp_selection_tap_event_change_stylesheet_enabled"),
                "tap_event_change_qss_stylesheet": getv("gwp_selection_tap_event_change_qss_stylesheet"),
                "tap_event_change_stylesheet_duration_ms": getv("gwp_selection_tap_event_change_stylesheet_duration_ms"),
                # Tap event - change size
                "tap_event_change_size_enabled": getv("gwp_selection_tap_event_change_size_enabled"),
                "tap_event_change_size_percent": getv("gwp_selection_tap_event_change_size_percent"),
                "tap_event_change_size_duration_ms": getv("gwp_selection_tap_event_change_size_duration_ms"),
                # Allow bypass enter event
                "allow_bypass_enter_event": True,
                # Enter event - animation
                "enter_event_show_animation_enabled": getv("gwp_selection_enter_event_show_animation_enabled"),
                "enter_event_show_animation_file_path": getv("gwp_selection_enter_event_show_animation_file_path"),
                "enter_event_show_animation_duration_ms": getv("gwp_selection_enter_event_show_animation_duration_ms"),
                "enter_event_show_animation_width": getv("gwp_selection_enter_event_show_animation_width"),
                "enter_event_show_animation_height": getv("gwp_selection_enter_event_show_animation_height"),
                "enter_event_show_animation_background_color": getv("gwp_selection_enter_event_show_animation_background_color"),
                # Enter event - play sound
                "enter_event_play_sound_enabled": getv("gwp_selection_enter_event_play_sound_enabled"),
                "enter_event_play_sound_file_path": getv("gwp_selection_enter_event_play_sound_file_path"),
                # Enter event - change stylesheet
                "enter_event_change_stylesheet_enabled": getv("gwp_selection_enter_event_change_stylesheet_enabled"),
                "enter_event_change_qss_stylesheet": getv("gwp_selection_enter_event_change_qss_stylesheet"),
                "enter_event_change_stylesheet_duration_ms": getv("gwp_selection_enter_event_change_stylesheet_duration_ms"),
                # Enter event - change size
                "enter_event_change_size_enabled": getv("gwp_selection_enter_event_change_size_enabled"),
                "enter_event_change_size_percent": getv("gwp_selection_enter_event_change_size_percent"),
                "enter_event_change_size_duration_ms": getv("gwp_selection_enter_event_change_size_duration_ms"),
                # Allow bypass leave event
                "allow_bypass_leave_event": True,
                # Leave event - animation
                "leave_event_show_animation_enabled": getv("gwp_selection_leave_event_show_animation_enabled"),
                "leave_event_show_animation_file_path": getv("gwp_selection_leave_event_show_animation_file_path"),
                "leave_event_show_animation_duration_ms": getv("gwp_selection_leave_event_show_animation_duration_ms"),
                "leave_event_show_animation_width": getv("gwp_selection_leave_event_show_animation_width"),
                "leave_event_show_animation_height": getv("gwp_selection_leave_event_show_animation_height"),
                "leave_event_show_animation_background_color": getv("gwp_selection_leave_event_show_animation_background_color"),
                # Leave event - play sound
                "leave_event_play_sound_enabled": getv("gwp_selection_leave_event_play_sound_enabled"),
                "leave_event_play_sound_file_path": getv("gwp_selection_leave_event_play_sound_file_path"),
                # Leave event - change stylesheet
                "leave_event_change_stylesheet_enabled": getv("gwp_selection_leave_event_change_stylesheet_enabled"),
                "leave_event_change_qss_stylesheet": getv("gwp_selection_leave_event_change_qss_stylesheet"),
                "leave_event_change_stylesheet_duration_ms": getv("gwp_selection_leave_event_change_stylesheet_duration_ms"),
                # Leave event - change size
                "leave_event_change_size_enabled": getv("gwp_selection_leave_event_change_size_enabled"),
                "leave_event_change_size_percent": getv("gwp_selection_leave_event_change_size_percent"),
                "leave_event_change_size_duration_ms": getv("gwp_selection_leave_event_change_size_duration_ms"),
            },
            "Widget_ItemBased_Properties": {
                # Selection cursor
                "allow_cursor_change": getv("gwp_item_based_allow_cursor_change"),
                "cursor": getv("gwp_item_based_cursor"),
                "cursor_width": getv("gwp_item_based_cursor_width"),
                "cursor_height": getv("gwp_item_based_cursor_height"),
                "cursor_keep_aspect_ratio": getv("gwp_item_based_cursor_keep_aspect_ratio"),
                # Allow bypass mouse press event
                "allow_bypass_mouse_press_event": True,
                # Tap event - animation
                "tap_event_show_animation_enabled": getv("gwp_item_based_tap_event_show_animation_enabled"),
                "tap_event_show_animation_file_path": getv("gwp_item_based_tap_event_show_animation_file_path"),
                "tap_event_show_animation_duration_ms": getv("gwp_item_based_tap_event_show_animation_duration_ms"),
                "tap_event_show_animation_width": getv("gwp_item_based_tap_event_show_animation_width"),
                "tap_event_show_animation_height": getv("gwp_item_based_tap_event_show_animation_height"),
                "tap_event_show_animation_background_color": getv("gwp_item_based_tap_event_show_animation_background_color"),
                # Tap event - play sound
                "tap_event_play_sound_enabled": getv("gwp_item_based_tap_event_play_sound_enabled"),
                "tap_event_play_sound_file_path": getv("gwp_item_based_tap_event_play_sound_file_path"),
                # Tap event - change stylesheet
                "tap_event_change_stylesheet_enabled": getv("gwp_item_based_tap_event_change_stylesheet_enabled"),
                "tap_event_change_qss_stylesheet": getv("gwp_item_based_tap_event_change_qss_stylesheet"),
                "tap_event_change_stylesheet_duration_ms": getv("gwp_item_based_tap_event_change_stylesheet_duration_ms"),
                # Tap event - change size
                "tap_event_change_size_enabled": getv("gwp_item_based_tap_event_change_size_enabled"),
                "tap_event_change_size_percent": getv("gwp_item_based_tap_event_change_size_percent"),
                "tap_event_change_size_duration_ms": getv("gwp_item_based_tap_event_change_size_duration_ms"),
                # Allow bypass enter event
                "allow_bypass_enter_event": True,
                # Enter event - animation
                "enter_event_show_animation_enabled": getv("gwp_item_based_enter_event_show_animation_enabled"),
                "enter_event_show_animation_file_path": getv("gwp_item_based_enter_event_show_animation_file_path"),
                "enter_event_show_animation_duration_ms": getv("gwp_item_based_enter_event_show_animation_duration_ms"),
                "enter_event_show_animation_width": getv("gwp_item_based_enter_event_show_animation_width"),
                "enter_event_show_animation_height": getv("gwp_item_based_enter_event_show_animation_height"),
                "enter_event_show_animation_background_color": getv("gwp_item_based_enter_event_show_animation_background_color"),
                # Enter event - play sound
                "enter_event_play_sound_enabled": getv("gwp_item_based_enter_event_play_sound_enabled"),
                "enter_event_play_sound_file_path": getv("gwp_item_based_enter_event_play_sound_file_path"),
                # Enter event - change stylesheet
                "enter_event_change_stylesheet_enabled": getv("gwp_item_based_enter_event_change_stylesheet_enabled"),
                "enter_event_change_qss_stylesheet": getv("gwp_item_based_enter_event_change_qss_stylesheet"),
                "enter_event_change_stylesheet_duration_ms": getv("gwp_item_based_enter_event_change_stylesheet_duration_ms"),
                # Enter event - change size
                "enter_event_change_size_enabled": getv("gwp_item_based_enter_event_change_size_enabled"),
                "enter_event_change_size_percent": getv("gwp_item_based_enter_event_change_size_percent"),
                "enter_event_change_size_duration_ms": getv("gwp_item_based_enter_event_change_size_duration_ms"),
                # Allow bypass leave event
                "allow_bypass_leave_event": True,
                # Leave event - animation
                "leave_event_show_animation_enabled": getv("gwp_item_based_leave_event_show_animation_enabled"),
                "leave_event_show_animation_file_path": getv("gwp_item_based_leave_event_show_animation_file_path"),
                "leave_event_show_animation_duration_ms": getv("gwp_item_based_leave_event_show_animation_duration_ms"),
                "leave_event_show_animation_width": getv("gwp_item_based_leave_event_show_animation_width"),
                "leave_event_show_animation_height": getv("gwp_item_based_leave_event_show_animation_height"),
                "leave_event_show_animation_background_color": getv("gwp_item_based_leave_event_show_animation_background_color"),
                # Leave event - play sound
                "leave_event_play_sound_enabled": getv("gwp_item_based_leave_event_play_sound_enabled"),
                "leave_event_play_sound_file_path": getv("gwp_item_based_leave_event_play_sound_file_path"),
                # Leave event - change stylesheet
                "leave_event_change_stylesheet_enabled": getv("gwp_item_based_leave_event_change_stylesheet_enabled"),
                "leave_event_change_qss_stylesheet": getv("gwp_item_based_leave_event_change_qss_stylesheet"),
                "leave_event_change_stylesheet_duration_ms": getv("gwp_item_based_leave_event_change_stylesheet_duration_ms"),
                # Leave event - change size
                "leave_event_change_size_enabled": getv("gwp_item_based_leave_event_change_size_enabled"),
                "leave_event_change_size_percent": getv("gwp_item_based_leave_event_change_size_percent"),
                "leave_event_change_size_duration_ms": getv("gwp_item_based_leave_event_change_size_duration_ms"),
            },
        }

        return result

    def _start_specific_dialog(self, event_dict):
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
        get_appv("cm").remove_all_context_menu()
        if ev.button() == Qt.RightButton:
            self._show_area_label_menu()
        elif ev.button() == Qt.LeftButton:
            self_obj: qwidgets_util_cls.Widget_Dialog = self.widget_handler.find_child(self)
            self_obj.EVENT_drag_widget_mouse_press_event(ev)

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
        UTILS.LogHandler.add_log_record("#1: Area Label context menu show.", ["MainWin"])
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
        get_appv("cm").remove_all_context_menu()

    def _animate_window_title(self):
        if getv("main_win_title_animate"):
            self.timer = QTimer(self)
            spaces = " " * getv("main_win_title_animate_spaces")
            title = spaces.join(list(self.windowTitle()))
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
                "position": "bottom right",
                "fade": True,
                "font_size": 42}
            utility_cls.Notification(stt, self, data, play_sound=False)
            get_appv("log").write_log("MainWin. Welcome notification show.")
            UTILS.LogHandler.add_log_record("#1 welcome notification shown.", ["MyJournal"])

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        get_appv("cm").remove_all_context_menu()
        return super().mousePressEvent(a0)

    def main_menu_about_to_show(self):
        if getv("main_menu_sound_enabled"):
            self.main_menu_sound.play()
        
        self._close_context_dialogs()

    def mnu_open_click(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
    
        statistic_cls.Statistic(stt, self)


    def show_log_messages(self):
        if self.log_messages_window:
            self.log_messages_window.close()

        frameless_window = getv("frameless_log_window")
        if UTILS_Settings.KEEP_LOG_WINDOW_ON_TOP:
            self.log_messages_window = UTILS.LogHandler.show_log_viewer(parent_widget=None, position=(100, 100), dialog_icon_path=getv("log_win_icon_icon"), dialog_close_icon_path=getv("close_icon_path"), dialog_frameless=frameless_window, close_feedback_function=self.log_messages_dialog_closed)
        else:
            self.log_messages_window = UTILS.LogHandler.show_log_viewer(parent_widget=self, position=(100, 100), dialog_icon_path=getv("log_win_icon_icon"), dialog_close_icon_path=getv("close_icon_path"), dialog_frameless=frameless_window, close_feedback_function=self.log_messages_dialog_closed)

    def log_messages_dialog_closed(self):
        self.log_messages_window = None

    def mnu_file_app_settings_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Application settings"])
            
        app_settings_cls.Settings(stt, self)

    def mnu_import_blocks_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Import Blocks"])

        export_import_cls.ExportImport(stt, self, action="import_blocks")

    def mnu_export_blocks_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Export Blocks"])

        export_import_cls.ExportImport(stt, self, action="export_blocks")

    def mnu_import_def_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Import Definitions"])

        export_import_cls.ExportImport(stt, self, action="import_defs")

    def mnu_export_def_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Export Definitions"])

        export_import_cls.ExportImport(stt, self, action="export_defs")

    def mnu_file_save_active_block_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Save active block"])
            
        self.save_active_block()

    def mnu_add_block_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Add new block"])
            
        self.add_block()

    def mnu_edit_definitions_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Edit Definitions"])
            
        definition_cls.AddDefinition(stt, self)

    def mnu_edit_tags_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Edit tags"])
            
        tag_cls.TagView(stt, self)

    def mnu_unfinished_show_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
            
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Show unfinished blocks"])
        result = self._show_all_drafts(animate_block_open=getv("mnu_unfinished_show_block_animation"))
        if not result:
            UTILS.LogHandler.add_log_record("MessageBox: #1 shown.", ["No unfinished blocks"])
            msg_dict = {
                "text": getl("mnu_unfinished_msg_no_data_text"),
                "position": "center",
                "pos_center": True
            }
            utility_cls.MessageInformation(stt, self, msg_dict)

    def mnu_translation_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Translate text dialog"])
            
        trans = utility_cls.Translate(stt, self)
        trans.show_gui()

    def mnu_diary_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Show diary dialog"])
            
        diary_view_cls.DiaryView(stt, self)

    def mnu_view_blocks_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Show block browse dialog"])
            
        diary_view_cls.BlockView(stt, self)

    def mnu_view_tags_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["View tags"])
            
        tag_cls.TagView(stt, self)

    def mnu_view_images_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Image browser"])
            
        utility_cls.PictureBrowse(stt, self)

    def mnu_view_definitions_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Definition browser"])
            
        definition_cls.BrowseDefinitions(stt, self)

    def mnu_view_fun_fact_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Fun Fact dialog"])
            
        utility_cls.FunFactShow(stt, self)

    def mnu_view_clipboard_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Clipboard dialog"])
            
        utility_cls.ClipboardView(stt, self)

    def mnu_view_media_explorer_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Media explorer"])
            
        utility_cls.MediaExplorer(stt, self)

    def mnu_view_dicts_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Dictionaries dialog"])
            
        dict_view = dict_cls.DictFrame(stt, self)
        dict_view.show_word()

    def mnu_view_wiki_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Wikipedia search dialog"])
            
        wikipedia_cls.Wikipedia(self, stt)

    def mnu_view_online_content_triggered(self) -> None:
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["OnLine Content dialog"])
            
        online_content_cls.OnlineContent(self, stt)

    def mnu_view_find_in_app_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Find in application dialog"])
            
        utility_cls.FindInApp(stt, self)

    def mnu_help_log_messages_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Log Messages"])
        
        self.show_log_messages()

    def mnu_help_statistic_triggered(self):
        if getv("menu_item_sound_enabled"):
            self.menu_item_sound.play()
        UTILS.LogHandler.add_log_record("Main menu item selected: #1", ["Statistic"])
        
        statistic_cls.Statistic(stt, self)

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
        UTILS.LogHandler.add_log_record("Active blocks saved (#1)", [f"{self.area_widget.layout().count() - 1} affected"])

    def ask_to_open_drafts_on_start(self):
        if getv("auto_show_drafts_on_start"):
            self._show_all_drafts(collapsed=getv("show_draft_blocks_collapsed_on_start"), animate_block_open=getv("animate_adding_empty_blocks_at_start"))
        # Create block on start
        if getv("add_block_at_start"):
            db_record = db_record_cls.Record(stt)
            if draft_rec := db_record.get_draft_records():
                add_new = all(record[4] != "" for record in draft_rec)
                if add_new:
                    UTILS.LogHandler.add_log_record("AutoAddBlock feature triggered #1 function.", ["Add New Block"])
                    self.add_block()
            else:
                UTILS.LogHandler.add_log_record("AutoAddBlock feature triggered #1 function.", ["Add New Block"])
                self.add_block()

    def _show_all_drafts(self, collapsed: bool = False, animate_block_open: bool = None) -> bool:
        selection = get_appv("selection")
        opened_items = [
            self.area_widget.layout().itemAt(idx).widget()._active_record_id
            for idx in range(self.area_widget.layout().count())
            if isinstance(
                self.area_widget.layout().itemAt(idx).widget(), block_cls.WinBlock
            )
        ]
        selection["title"] = getl("open_drafts_at_start_menu_title")
        selection["multi-select"] = False
        selection["checkable"] = True
        selection["result"] = None
        selection["items"] = []
        db_record = db_record_cls.Record(stt)
        empty_rec = db_record.get_draft_records()
        app.processEvents()
        if not empty_rec:
            return False

        has_records = False
        for record in empty_rec:
            name = f"{record[2]} "
            name += record[1] if record[1] else getl("open_records_on_start_no_name")

            if record[0] not in opened_items:
                selection["items"].append([record[0], name, record[4], False, True, []])
                has_records = True
        if not has_records:
            return False

        utility_cls.Selection(stt, self)

        if selection["result"]:
            for record_id in selection["result"]:
                animate = animate_block_open if animate_block_open is not None else True
                self.add_block(record_id, collapsed=collapsed, animate=animate)
        return True

    def add_block(self, record_id: int = 0, collapsed: bool = False, animate: bool = None):
        if animate is None:
            animate = getv("block_animation_on_open")

        if record_id == 0:
            record_id = self._find_new_block_id_and_save_record()
            if record_id is None:
                return None
        
        # Check if block exist
        for i in range(self.area_widget.layout().count()):
            if isinstance(self.area_widget.layout().itemAt(i).widget(), block_cls.WinBlock):
                if self.area_widget.layout().itemAt(i).widget()._active_record_id == record_id:
                    return
        # Create new win block            
        block_cls.WinBlock(stt, self.area_widget, record_id, collapsed=collapsed, animate_block=animate, main_window=self)
        get_appv("signal").block_text_give_focus(record_id)
        UTILS.LogHandler.add_log_record("New block added.", variables=[["record_id", record_id], ["collapsed", collapsed], ["animate", animate]])

    def _find_new_block_id_and_save_record(self):
        # Find record ID for new block
        #   Save new empty record
        block = obj_block.Block(stt)
        block.RecTags = [x for x in getv("block_tag_added_at_start").split(",") if x != ""]
        if block.can_be_added():
            result = block.add()
        else:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2, cannot create new block.", ["MyJournal", "_find_new_block_id_and_save_record"], exception_raised=True)
            return None

        # record = db_record_cls.Record(stt)
        # result = record.add_new_record("", "")
        # record_data = db_record_data_cls.RecordData(stt, result)
        # data_dict = record_data._empty_record_data_dict()
        # data_dict["tag"] = [x for x in getv("block_tag_added_at_start").split(",") if x != ""]
        # record_data.update_record_data(data_dict, record_id=result)
        get_appv("log").write_log(f"MainWin. New block added. Record ID: {result}")

        return result

    def mnu_expand_all_triggered(self):
        UTILS.LogHandler.add_log_record("All opened blocks: #1 triggered.", ["Expand all blocks"])
        value = getv("block_animation_on_expand")
        setv("block_animation_on_expand", False)
        self.send_signal.send_expand_all_signal()
        app.processEvents()
        setv("block_animation_on_expand", value)

    def mnu_collapse_all_triggered(self):
        UTILS.LogHandler.add_log_record("All opened blocks: #1 triggered.", ["Collapse all blocks"])
        value = getv("block_animation_on_collapse")
        setv("block_animation_on_collapse", False)
        self.send_signal.send_collapse_all_signal()
        app.processEvents()
        setv("block_animation_on_collapse", value)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if getv("resize_area_with_mainwindow"):
            w = self.contentsRect().width()
            h = self.contentsRect().height() - self.sts_bar.height() - self.menubar.height()
            if self.toolBarArea(self.toolBar) in [Qt.TopToolBarArea, Qt.BottomToolBarArea]:
                h -= self.toolBar.height()
            elif self.toolBarArea(self.toolBar) in [Qt.LeftToolBarArea, Qt.RightToolBarArea]:
                w -= self.toolBar.width()
            
            self.area.resize(w, h)
        return super().resizeEvent(a0)

    def _close_event(self, a0):
        UTILS.LogHandler.add_log_record("Close Application Event: About to #1", ["Show exit notification"])
        # Show exit notification
        close_notification = "N/A"
        if getv("show_closing_notification"):
            close_notification = self._show_exit_app_notification()
            UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Exit notification displayed"])
        else:
            UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Exit notification Canceled"])
        
        app.processEvents()

        UTILS.LogHandler.add_log_record("Close Application Event: About to #1", ["Save clipboard content"])
        # Save clipboard content
        if getv("delete_clipboard_on_app_exit"):
            UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Clipboard content deleted before saving"])
            get_appv("cb").clear_clip()
        get_appv("cb")._save_clipboard_to_file()
        UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Clipboard content saved"])

        UTILS.LogHandler.add_log_record("Close Application Event: About to #1", ["Clear temp folder"])
        # Delete temp folder
        if getv("delete_temp_folder_on_app_exit"):
            file_util = utility_cls.FileDialog(stt)
            file_util.delete_temp_folder()
            UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Temp folder cleared"])
        else:
            UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Clear temp folder Canceled"])

        # Stop timers
        self.timers.stop_all_timers()
        self.timers.remove_all_timers()
        UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Timers stopped."], variables=[["active timer", x] for x in self.timers.get_all_timers()])
        self.timers.close_me()
        self.timers = None
        app.processEvents()
        
        # Close all blocks
        blocks_to_close = []
        for idx in range(self.area_widget.layout().count()):
            if self.area_widget.layout().itemAt(idx) and isinstance(self.area_widget.layout().itemAt(idx).widget(), block_cls.WinBlock):
                get_appv("log").write_log(f"MainWin. Close block on exit. Record ID: {self.area_widget.layout().itemAt(idx).widget()._active_record_id}")
                blocks_to_close.append(self.area_widget.layout().itemAt(idx).widget())
        for block in blocks_to_close:
            block.close_me()
            app.processEvents()
        UTILS.LogHandler.add_log_record("Close Application Event: #1, active blocks = #2", ["Close all blocks", len(blocks_to_close)])
        blocks_to_close = None

        # Remove any context menu, notification, input dialog ...
        get_appv("cm").remove_all()
        UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Removed context menus, notifications etc..."])

        if self.isMaximized():
            setv("main_win_is_fullscreen", True)
        else:
            x = self.pos().x() if self.pos().x() >= 0 else 0
            y = self.pos().y() if self.pos().y() >= 0 else 0
            setv("main_win_is_fullscreen", False)
            setv("main_win_pos_x", x)
            setv("main_win_pos_y", y)
            setv("main_win_width", self.width())
            setv("main_win_height", self.height())
        setv("main_toolbar_position", self.toolBarArea(self.toolBar))
        UTILS.LogHandler.add_log_record("Close Application Event: Updated settings: #1", ["MainWindow position and size"])

        stt.save_settings()
        UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Settings saved"])
        get_appv("log").write_log("MainWin. Settings saved.")

        # Remove main window from app_setting
        stt.app_setting_delete("main_win")
        UTILS.LogHandler.add_log_record("Close Application Event: #1", ["Removed MainWindow from AppSettings"])
        
        if self.widget_handler:
            self.widget_handler.close_me()
            self.widget_handler = None
            UTILS.LogHandler.add_log_record("Close Application Event: #1", ["WidgetHandler closed"])
        
        UTILS.LogHandler.add_log_record("Close Application Event: About to #1", ["Close objects that failed to AutoClose"])
        
        # Close log message window
        if self.log_messages_window:
            self.log_messages_window.close()
            UTILS.LogHandler.add_log_record("Close Application Event: #1 closed.", ["LogMessagesWindow"])

        # Close objects that failed to close
        objects_to_close = []
        for child in self.children():
            try:
                ignore_child = False
                if isinstance(child, timer_cls.TimerHandler):
                    if child._parent is self:
                        ignore_child = True
                if str(child) == close_notification:
                    ignore_child = True

                child.close_me()

                UTILS.LogHandler.add_log_record("Close Application Event: Closing object #1", [child])
                get_appv("log").write_log("MainWin. Object closed. : " + str(child))
                
                if not ignore_child:
                    objects_to_close.append(str(child))
                else:
                    UTILS.LogHandler.add_log_record("Close Application Event: Ignore object #1", [child])
            except AttributeError:
                pass
            except Exception as e:
                UTILS.LogHandler.add_log_record("Close Application Event: Error while closing object #1 in object #2 method.\nException: #3", [child, "close_me", e])
                
        # Show warning message about objects that failed to close
        warning_message = "Objects forced to close:\n"
        for count in range(len(objects_to_close)):
            i = str(count + 1)
            warning_message += f"#{i}\n"

        if objects_to_close:
            UTILS.TerminalUtility.WarningMessage(warning_message, objects_to_close)
        
        UTILS.LogHandler.add_log_record("Close Application Event: About to #1", ["Fade Out MainWindow"])
        # Fade out main window
        opacity = 1
        while opacity > 0:
            self.setWindowOpacity(opacity)
            time.sleep(0.03)
            opacity -= 0.05
        get_appv("log").write_log("MainWin. Window closed.")
        UTILS.LogHandler.add_log_record("Close Application Event: #1", ["MainWindow Closed"])

    def _show_exit_app_notification(self) -> str:
        data_dict = {"text": getl("closing_notification_text")}
        data_dict["title"] = getl("closing_notification_title")
        data_dict["fade"] = False
        data_dict["animation"] = False
        data_dict["timer"] = None
        data_dict["position"] = "top right"
        close_notification = utility_cls.Notification(stt, self, data_dict, play_sound=False)
        app.processEvents()
        get_appv("log").write_log("MainWin. Close notification show.")
        return str(close_notification)

    def _load_user_widget_settings(self):
        # MainWindow
        self.move(getv("main_win_pos_x"), getv("main_win_pos_y"))
        self.resize(getv("main_win_width"), getv("main_win_height"))
        if getv("main_win_is_fullscreen"):
            self.showMaximized()
        # Toolbar
        self.addToolBar(getv("main_toolbar_position"), self.toolBar)
        get_appv("log").write_log("MainWin. Settings loaded.")
        UTILS.LogHandler.add_log_record("Loaded #1 geometry and ToolBar position.\n#1 position (#2, #3)\n#1 size (#4, #5)", ["MainWin", getv("main_win_pos_x"), getv("main_win_pos_y"), getv("main_win_width"), getv("main_win_height")])

    def _toolbar_areas_changed(self, areas):
        if getv("resize_area_with_mainwindow"):
            w = self.contentsRect().width()
            h = self.contentsRect().height() - self.sts_bar.height() - self.menubar.height()
            if self.toolBar.width() < self.toolBar.height():
                h -= self.toolBar.width()
            else:
                w -= self.toolBar.height() - self.sts_bar.height()
            self.area.resize(w, h)

    def sld_volume_mouse_press(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.lbl_volume_value.setVisible(True)
        
        QSlider.mousePressEvent(self.sld_volume, e)
    
    def sld_volume_mouse_release(self, e: QMouseEvent):
        self.lbl_volume_value.setVisible(False)

        QSlider.mouseReleaseEvent(self.sld_volume, e)

    def update_volume_status(self):
        if getv("volume_muted"):
            self.btn_volume.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.btn_volume.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        
        UTILS.Signal.emit_volume_changed(getv("volume_value"), {"muted": getv("volume_muted")})
        self.sld_volume.setToolTip(f"{getl('sld_volume_tt')}  Volume: {getv('volume_value')} %")
        self.lbl_volume_value.setText(str(getv('volume_value')))

    def sld_volume_value_changed(self):
        setv("volume_value", self.sld_volume.value())
        self.update_volume_status()

    def app_setting_updated(self, data: dict):
        set_appv("global_widgets_properties", qwidgets_util_cls.GlobalWidgetsProperties(self._get_global_widgets_properties()))
        self._setup_widgets_appearance(settings_action=True)
        update_utils_settings(load_from=stt)
        UTILS.LogHandler.add_log_record("#1. Settings updated: Refreshing widgets appearance.", ["MainWin"])

    def _setup_widgets_appearance(self, settings_action: bool = False):
        if settings_action:
            self._set_margins(self.area, "scroll_area")
            self._set_margins(self.area_widget, "scroll_area_widget")
            self._set_margins(self.area_widget.layout(), "scroll_area_widget_layout")

            self.hide()
        
        # MainWindow
        self.setWindowIcon(QIcon(getv("main_win_icon_path")))
        self.setStyleSheet(getv("main_win_stylesheet"))
        # Toolbar
        self.toolBar.setStyleSheet(getv("toolBar_stylesheet"))
        
        for i in self.toolBar.children():
            if isinstance(i, QToolButton):
                i.setStyleSheet(getv("toolbar_buttons_stylesheet"))
        
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
        # Statusbar Volume Control
        self.frm_stb_volume.setEnabled(getv("frm_stb_volume_enabled"))
        self.frm_stb_volume.setVisible(getv("frm_stb_volume_visible"))
        self.frm_stb_volume.setStyleSheet(getv("frm_stb_volume_stylesheet"))
        self.btn_volume.setStyleSheet(getv("btn_volume_stylesheet"))
        self.btn_volume.setCursor(Qt.PointingHandCursor)
        self.sld_volume.setStyleSheet(getv("sld_volume_stylesheet"))
        self.sld_volume.setCursor(Qt.PointingHandCursor)
        self.lbl_volume_value.setStyleSheet(getv("lbl_volume_value_stylesheet"))
        # Statusbar Logs button
        self.btn_logs.setVisible(getv("btn_logs_visible"))
        self.btn_logs.setStyleSheet(getv("btn_logs_stylesheet"))
        self.btn_logs.setFixedHeight(self.frm_stb_volume.height())
        self.btn_logs.setCursor(Qt.PointingHandCursor)

        frm_stb_volume_width = getv("frm_stb_volume_fixed_width")
        if frm_stb_volume_width < 15:
            if frm_stb_volume_width == 0:
                frm_stb_volume_width = 80
            else:
                UTILS.TerminalUtility.WarningMessage("Invalid volume control width, must be greater than #1\nwidth = #2\nWidth is set to 15", [15, frm_stb_volume_width])
                frm_stb_volume_width = 15
        if frm_stb_volume_width > self.sts_bar.width():
            UTILS.TerminalUtility.WarningMessage("Invalid volume control width.\nVolume control width is greater than status bar width.\nvolume control width = #1\nStatus bar width = #2\nVolume control width is set to status bar width (#2)", [frm_stb_volume_width, self.sts_bar.width()])
            frm_stb_volume_width = self.sts_bar.width()
        self.frm_stb_volume.setFixedWidth(frm_stb_volume_width)
        sld_volume_width = frm_stb_volume_width - 17 if frm_stb_volume_width > 17 else 0
        self.sld_volume.resize(sld_volume_width, self.sld_volume.height())
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Add widgets to statusbar
        self.sts_bar.layout().setSpacing(10)
        self.sts_bar.addPermanentWidget(spacer)
        self.sts_bar.addPermanentWidget(self.btn_logs)
        self.sts_bar.addPermanentWidget(self.frm_stb_volume)
        
        self.sld_volume.setValue(getv("volume_value"))
        self.lbl_volume_value.setVisible(False)
        self.update_volume_status()
        # Menubar
        self.menubar.setStyleSheet(getv("menubar_stylesheet"))
        self.menubar.setEnabled(getv("menubar_enabled"))
        self.menubar.setVisible(getv("menubar_visible"))
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
        self.area_label.setScaledContents(True)
        self.area_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.area_label.setMinimumHeight(getv("area_label_widget_min_height"))
        align = getv("area_label_widget_alignment")
        if isinstance(align, str):
            align_vals = [int(x) for x in align.split(",") if x != ""]
            align = sum(align_vals)
        self.area_label.setAlignment(Qt.Alignment(align))
        if getv("area_label_content_type") == 0:
            self.area_label.setPixmap(QPixmap())
            self.area_label.setMovie(QMovie())
            self.area_label.setText(getl("area_label_widget_text"))
        elif getv("area_label_content_type") == 1:
            self.area_label.setText("")
            self.area_label.setMovie(QMovie())
            self.area_label.setPixmap(QPixmap(getv("area_label_widget_icon_path")))
        elif getv("area_label_content_type") == 2:
            self.area_label.setText("")
            self.area_label.setPixmap(QPixmap())
            area_movie = QMovie(getv("area_label_widget_animation_path"))
            self.area_label.setMovie(area_movie)
            area_movie.start()
        else:
            log.write_log("ERROR: Unknown label content type: " + str(getv("area_label_content_type")))

        # Main Menu
        self._define_main_menu_items(self.menu_file, "menu_file")
        self._define_main_menu_items(self.menu_edit, "menu_edit")
        self._define_main_menu_items(self.menu_view, "menu_view")
        self._define_main_menu_items(self.menu_user, "menu_user")
        self._define_main_menu_items(self.menu_tags, "menu_tags")
        self._define_main_menu_items(self.menu_help, "menu_help")

        # Menu Items
        #       File
        self._define_menu_item(self.mnu_file_app_settings, "mnu_file_app_settings")
        self._define_menu_item(self.mnu_import_blocks, "mnu_import_blocks")
        self._define_menu_item(self.mnu_export_blocks, "mnu_export_blocks")
        self._define_menu_item(self.mnu_import_def, "mnu_import_def")
        self._define_menu_item(self.mnu_export_def, "mnu_export_def")
        self._define_menu_item(self.mnu_open, "mnu_open")
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
        #       Help
        self._define_menu_item(self.mnu_help_log_messages, "mnu_help_log_messages")
        self._define_menu_item(self.mnu_help_statistic, "mnu_help_statistic")

        if settings_action:
            app.processEvents()
            self.show()

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
        # Status Bar Volume Control
        self.btn_volume.setToolTip(getl("btn_volume_tt"))
        self.btn_volume.setStatusTip(getl("btn_volume_sb_text"))
        self.sld_volume.setToolTip(getl("sld_volume_tt"))
        self.sld_volume.setStatusTip(getl("sld_volume_sb_text"))
        # Logs in statusbar
        self.btn_logs.setText(getl("btn_logs_text"))
        self.btn_logs.setToolTip(getl("btn_logs_tt"))
        self.btn_logs.setStatusTip(getl("btn_logs_sb_text"))        
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
        self.mnu_file_app_settings.setText(getl("mnu_file_app_settings_text"))
        self.mnu_file_app_settings.setToolTip(getl("mnu_file_app_settings_tt"))
        self.mnu_file_app_settings.setStatusTip(getl("mnu_file_app_settings_sb_text"))
        self.mnu_import_blocks.setText(getl("mnu_import_blocks_text"))
        self.mnu_import_blocks.setToolTip(getl("mnu_import_blocks_tt"))
        self.mnu_import_blocks.setStatusTip(getl("mnu_import_blocks_sb_text"))
        self.mnu_export_blocks.setText(getl("mnu_export_blocks_text"))
        self.mnu_export_blocks.setToolTip(getl("mnu_export_blocks_tt"))
        self.mnu_export_blocks.setStatusTip(getl("mnu_export_blocks_sb_text"))
        self.mnu_import_def.setText(getl("mnu_import_def_text"))
        self.mnu_import_def.setToolTip(getl("mnu_import_def_tt"))
        self.mnu_import_def.setStatusTip(getl("mnu_import_def_sb_text"))
        self.mnu_export_def.setText(getl("mnu_export_def_text"))
        self.mnu_export_def.setToolTip(getl("mnu_export_def_tt"))
        self.mnu_export_def.setStatusTip(getl("mnu_export_def_sb_text"))
        self.mnu_open.setText(getl("mnu_open_text"))
        self.mnu_open.setToolTip(getl("mnu_open_tt"))
        self.mnu_open.setStatusTip(getl("mnu_open_sb_text"))
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
        # Help
        self.mnu_help_log_messages.setText(getl("mnu_help_log_messages_text"))
        self.mnu_help_log_messages.setToolTip(getl("mnu_help_log_messages_tt"))
        self.mnu_help_log_messages.setStatusTip(getl("mnu_help_log_messages_sb_text"))
        self.mnu_help_statistic.setText(getl("mnu_help_statistic_text"))
        self.mnu_help_statistic.setToolTip(getl("mnu_help_statistic_tt"))
        self.mnu_help_statistic.setStatusTip(getl("mnu_help_statistic_sb_text"))

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
        self.mnu_file_app_settings: QAction = self.findChild(QAction, "mnu_file_app_settings")
        self.mnu_import_blocks: QAction = self.findChild(QAction, "mnu_import_blocks")
        self.mnu_export_blocks: QAction = self.findChild(QAction, "mnu_export_blocks")
        self.mnu_import_def: QAction = self.findChild(QAction, "mnu_import_def")
        self.mnu_export_def: QAction = self.findChild(QAction, "mnu_export_def")
        self.mnu_open: QAction = self.findChild(QAction, "mnu_open")
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
        #       Help
        self.mnu_help_log_messages: QAction = self.findChild(QAction, "mnu_help_log_messages")
        self.mnu_help_statistic: QAction = self.findChild(QAction, "mnu_help_statistic")

        # Status bar
        self.sts_bar: QStatusBar = self.findChild(QStatusBar, "sts_bar")
        # Volume Control Frame in Status Bar
        self.frm_stb_volume: QFrame = self.findChild(QFrame, "frm_stb_volume")
        self.frm_stb_volume.setParent(self.sts_bar)
        self.btn_volume: QPushButton = self.findChild(QPushButton, "btn_volume")
        self.sld_volume: QSlider = self.findChild(QSlider, "sld_volume")
        self.lbl_volume_value: QLabel = self.findChild(QLabel, "lbl_volume_value")
        # Logs button in Status Bar
        self.btn_logs = QPushButton(self.sts_bar)

        # Toolbar
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
        values = getv(f"{name}_contents_margins")
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

    # Add startup log
    UTILS.LogHandler.add_log_record(
        message="Application #1 created, new log started.",
        arguments=["MyJournal"],
        start_new_log=True
    )

    _app_style_sheet = """
    QToolTip {
        background-color: black;
        color: yellow;
        border: 1px solid gray;
        padding: 5px;
    }
    """
    app.setStyleSheet(_app_style_sheet)
    # 'stt' is a setting object that will be passed to various modules during application execution.
    stt = settings_cls.Settings(SETTING_FILE, LANGUAGES_FILE)
    # stt.debug_mode = True
    # Define settings methods
    getv = stt.get_setting_value
    setv = stt.set_setting_value
    getl = stt.lang
    get_appv = stt.app_setting_get_value
    set_appv = stt.app_setting_set_value
    # Update UTIL settings with general settings
    update_utils_settings(load_from=stt)
    # 'log' object is also passed to all modules when they are called.
    log = log_cls.Log(stt)
    # We create a users object that will contain all information about the currently active user.
    user = users_cls.User(stt)
    # Start login screen
    stt.set_setting_value("active_user", "")
    login =  login_cls.UserLogin(stt, user, log)
    login.start_gui()

    # Check for code function duplicates
    _duplicate_functions = UTILS.ApplicationSourceCode.get_class_functions_duplicates_message()
    if _duplicate_functions:
        UTILS.LogHandler.add_log_record(
            message=_duplicate_functions[0],
            arguments=_duplicate_functions[1],
            exception_raised=True
        )

    # Check for incorrect number of declinations in module definition_cls.py
    _incorrect_declinations = UTILS.ApplicationSourceCode.get_incorrect_declinations_in_imenica()
    if _incorrect_declinations:
        UTILS.LogHandler.add_log_record(
            message=_incorrect_declinations[0],
            arguments=_incorrect_declinations[1],
            exception_raised=True
        )

    app.exec_()
    # If there is an active user in the 'active_user' object, then we start the application.
    my_journal = None
    splash = None
    try:
        if user.ActiveUserID != 0:
            splash = SplashScreen(size=(600, 300), background_image="data/app/images/splash_bg.jpg", splash_image="data/app/images/splash_small.png", title=getl("splash_title"), detail=getl("splash_creating_mainwin"))
            app.processEvents()

            login.deleteLater()
            stt.change_settings_file(user.settings_path)
            log.write_log("User settings are loaded.")
            my_journal = MyJournal()

            # Updater UTIL settings with user app settings
            update_utils_settings(
                load_from=stt,
                LOG_WINDOW_PARENT_WIDGET=my_journal
            )

            my_journal.start_gui()
            my_journal._load_user_widget_settings()
            UTILS.LogHandler.add_log_record("#1 displayed on position (#2, #3) size (#4, #5)", ["MainWin", my_journal.pos().x(), my_journal.pos().y(), my_journal.width(), my_journal.height()])

            splash.close_me()
            splash = None
            app.processEvents()

            app.exec_()
    except Exception as e:
        if splash:
            splash.close_me()
            splash = None
        
        UTILS.TerminalUtility.WarningMessage(
            message="Application execution failed.\nError: #1",
            arguments=[str(e)],
            exception_raised=True
        )

    app.quit()







