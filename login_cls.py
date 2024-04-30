from PyQt5.QtWidgets import (QFrame, QComboBox, QLineEdit, QPushButton, QLabel,
                             QDialog, QMessageBox)
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtCore import Qt

import settings_cls
import users_cls
import log_cls
import UTILS


class UserLogin(QDialog):
    """User login:
    - Registration of an existing user
        Checks if username and passwod match
        Sets the 'ActiveUserID' and 'language_name' variables and completes the login
    - Adding a new user
        It checks whether the entered data is valid and if so adds a new user to the database.
        Then goes back to 'Login' and sets checkbox to the newly added user.
    """

    def __init__(self, settings: settings_cls.Settings, user: users_cls.User, log: log_cls.Log, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Set variables
        self._log = log
        self._user = user
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.getl = self._stt.lang
        # Load GUI
        uic.loadUi(self.getv("login_ui_file_path"), self)

    def start_gui(self) -> str:
        # Define widgets
        self._define_widgets()
        # Adjust the appearance and behavior of the widget
        self._setup_widgets_appearance()
        self._setup_widgets_language(overwrite_user_data=True)
        self._setup_open_settings()
        # Connect events with slots
        #   User Login events
        self.keyPressEvent = self.key_press_event
        self.btn_new.clicked.connect(self.btn_new_click)
        self.txt_password.textChanged.connect(self.txt_password_text_changed)
        self.cmb_user.currentTextChanged.connect(self.cmb_user_text_changed)
        self.cmb_lang.currentTextChanged.connect(self.cmb_lang_text_changed)
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_login.clicked.connect(self.btn_login_click)
        self.txt_password.returnPressed.connect(self.btn_login_click)
        #   New user events
        self.btn_new_cancel.clicked.connect(self.btn_new_cancel_click)
        self.txt_new_username.textChanged.connect(self.txt_new_username_text_changed)
        self.txt_new_password.textChanged.connect(self.txt_new_password_text_changed)
        self.txt_new_password_confirm.textChanged.connect(self.txt_new_password_confirm_text_changed)
        self.btn_new_ok.clicked.connect(self.btn_new_ok_click)
        
        self._log.write_log("Login started...")
        UTILS.LogHandler.add_log_record("#1: Login started...", ["UserLogin"])
        self.show()

    def btn_login_click(self):
        # Checking if the username and password match
        user_name = self.cmb_user.currentText()
        if not self._user.is_user_name(user_name):
            UTILS.TerminalUtility.WarningMessage("#1: Login Error. Username not found. User: #2", ["UserLogin", user_name], call_stack_show=False)
            QMessageBox.critical(self, self.getl("login_msg_invalid_username_title"), self.getl("login_msg_invalid_username_text"), QMessageBox.Ok)
            self._log.write_log(f"Login Error. Username not found. User: '{user_name}'")
            return
        passsword = self.txt_password.text()
        if self._user.check_user_password(user_name, passsword):
            self._user.ActiveUserID = self._user.get_user_id(user_name)
            self._user.language_name = self.cmb_lang.currentText()
            self._stt.ActiveLanguageID = self._user.language_id
            self._user.save_users_to_file()
            self._stt.set_setting_value("last_user_id", self.cmb_user.currentData())
            self._stt.set_setting_value("last_user_username", user_name)
            self._log.write_log(f"User is logged in: {user_name}")
            self._log.write_log("Login window closed.")
            UTILS.LogHandler.add_log_record("#1: User #2 is logged in. Language: #3", ["UserLogin", user_name, self._user.language_name])
            self.close()
        else:
            UTILS.TerminalUtility.WarningMessage("#1: Login Error. Invalid password. User: #2", ["UserLogin", user_name], call_stack_show=False)
            QMessageBox.critical(self, self.getl("login_incorrect_password_title"), self.getl("login_incorrect_password_text"), QMessageBox.Ok)
            self._log.write_log(f"Warning. Attempted login with incorrect password: {user_name}")
            self.txt_password.setText("")
            self.txt_password.setFocus()

    def cmb_user_text_changed(self):
        self.txt_password.setText("")
        if self.cmb_user.currentText():
            self.cmb_lang.setCurrentText(self._user.get_user_language_name(self.cmb_user.currentData()))

    def btn_new_ok_click(self):
        if self.txt_new_username.text().strip() == "":
            self.txt_new_username.setText("")
            return
        # Check password match
        if self.txt_new_password.text() != self.txt_new_password_confirm.text():
            UTILS.LogHandler.add_log_record("#1: Adding new user: Password confirm mismatch.", ["UserLogin"])
            QMessageBox.information(self, self.getl("login_msg_new_pass_mismatch_title"), self.getl("login_msg_new_pass_mismatch_text"), QMessageBox.Ok)
            return
        # Check if the user already exists
        if self._user.is_user_name(self.txt_new_username.text()):
            UTILS.LogHandler.add_log_record("#1: Adding new user. User #2 already exist.", ["UserLogin", self.txt_new_username.text()])
            QMessageBox.information(self, self.getl("login_msg_new_user_exist_title"), self.getl("login_msg_new_user_exist_text"), QMessageBox.Ok)
            return
        # Add new user
        self._user.add_new_user(self.txt_new_username.text(), self.txt_new_password.text(), self.cmb_lang.currentData())
        self.cmb_user.addItem(self.txt_new_username.text(), self._user.get_user_id(self.txt_new_username.text()))
        self.cmb_user.setCurrentText(self.txt_new_username.text())
        self.cmb_user_text_changed()
        self._user.save_users_to_file()
        UTILS.LogHandler.add_log_record("#1: New user added. Username: #2", ["UserLogin", self.txt_new_username.text()])
        QMessageBox.information(self, self.getl("login_msg_new_user_added_title"), self.getl("login_msg_new_user_added_text"), QMessageBox.Ok)
        # Show login screen, and clear new user text boxes
        self.frm_new.setVisible(False)
        self.txt_new_password.setText("")
        self.txt_new_password_confirm.setText("")
        self.txt_new_username.setText("")
        self._log.write_log(f"New user added : {self.txt_new_username.text()}")
        
    def key_press_event(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key_Escape:
            UTILS.LogHandler.add_log_record("#1: User login canceled. Login window #2.", ["UserLogin", "closed"])
            self.close()

        return super().keyPressEvent(a0)

    def btn_cancel_click(self):
        UTILS.LogHandler.add_log_record("#1: User login canceled. Login window #2.", ["UserLogin", "closed"])
        self.close()

    def cmb_lang_text_changed(self):
        if self.cmb_lang.currentText():
            self._stt.ActiveLanguageID = self.cmb_lang.currentData()
            UTILS.LogHandler.add_log_record("#1: Login dialog. Current language changed to #2", ["UserLogin", self.cmb_lang.currentText()])
        self._setup_widgets_language()

    def txt_new_username_text_changed(self):
        # Check for illegal characters
        self.txt_new_username.setText(self._username_text_check(self.txt_new_username.text()))
        # Enable/Disable OK button
        if self.txt_new_username.text():
            self.btn_new_ok.setEnabled(True)
        else:
            self.btn_new_ok.setEnabled(False)

    def txt_new_password_text_changed(self):
        self.txt_new_password.setText(self._password_text_check(self.txt_new_password.text()))

    def txt_new_password_confirm_text_changed(self):
        self.txt_new_password_confirm.setText(self._password_text_check(self.txt_new_password_confirm.text()))

    def txt_password_text_changed(self):
        self.txt_password.setText(self._password_text_check(self.txt_password.text()))

    def _password_text_check(self, text: str) -> str:
        allowed = self.getv("allowed_chars_for_user_password")
        result = ""
        for char in text:
            if char in allowed:
                result += char
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Login Error. Invalid password character.\nInvalid character: #2", ["UserLogin", char], call_stack_show=False)
                QMessageBox.warning(self, self.getl("login_msg_pass_char_title"), self.getl("login_msg_pass_char_text"), QMessageBox.Ok)
                return ""
        return result

    def _username_text_check(self, text: str) -> str:
        allowed = self.getv("allowed_chars_for_user_name")
        result = ""
        for char in text:
            if char in allowed:
                result += char
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Login Error. Invalid username character.\nInvalid character: #2", ["UserLogin", char])
                QMessageBox.warning(self, self.getl("login_msg_username_char_title"), self.getl("login_msg_username_char_text"), QMessageBox.Ok)
                return ""
        return result

    def btn_new_click(self):
        UTILS.LogHandler.add_log_record("#1: Login: Stated #2 dialog.", ["UserLogin", "add new user"])
        self.frm_new.setVisible(True)

    def btn_new_cancel_click(self):
        UTILS.LogHandler.add_log_record("#1: Login: New user add dialog closed.", ["UserLogin"])
        self.frm_new.setVisible(False)

    def _setup_open_settings(self):
        # Set the new user input frame as invisible.
        self.frm_new.setVisible(False)
        # Set buttons as disabled
        self.btn_new_ok.setEnabled(False)
        # Populate users combo box
        self.cmb_user.clear()
        for user in self._user.ListOfAllUsers:
            self.cmb_user.addItem(user[1], user[0])
        self.cmb_user.setCurrentText(self.getv("last_user_username"))
        # Populate languages combo box
        self.cmb_lang.clear()
        for language in self._stt.GetListOfAllLanguages:
            self.cmb_lang.addItem(language[1], language[0])
        if self.cmb_user.currentText():
            self.cmb_lang.setCurrentText(self._user.get_user_language_name(self.cmb_user.currentData()))
        self.cmb_lang_text_changed()
        # Set focus to password entry
        self.txt_password.setFocus()

    def _define_widgets(self) -> None:
        # User login screen
        self.lbl_caption: QLabel = self.findChild(QLabel, "lbl_caption")
        self.cmb_user: QComboBox = self.findChild(QComboBox, "cmb_user")
        self.txt_password: QLineEdit = self.findChild(QLineEdit, "txt_password")
        self.lbl_lang: QLabel = self.findChild(QLabel, "lbl_lang")
        self.cmb_lang: QComboBox = self.findChild(QComboBox, "cmb_lang")
        self.btn_login: QPushButton = self.findChild(QPushButton, "btn_login")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_new: QPushButton = self.findChild(QPushButton, "btn_new")
        # New user screen
        self.frm_new: QFrame = self.findChild(QFrame, "frm_new")
        self.lbl_new_caption: QLabel = self.findChild(QLabel, "lbl_new_caption")
        self.txt_new_username: QLineEdit = self.findChild(QLineEdit, "txt_new_username")
        self.txt_new_password: QLineEdit = self.findChild(QLineEdit, "txt_new_password")
        self.txt_new_password_confirm: QLineEdit = self.findChild(QLineEdit, "txt_new_password_confirm")
        self.btn_new_ok: QPushButton = self.findChild(QPushButton, "btn_new_ok")
        self.btn_new_cancel: QPushButton = self.findChild(QPushButton, "btn_new_cancel")

    def _setup_widgets_appearance(self):
        # Window
        if self.getv("login_is_fixed_size"):
            self.setFixedSize(self.getv("login_win_fixed_width"), self.getv("login_win_fixed_height"))
        self.setStyleSheet(self.getv("login_win_stylesheet"))
        if self.getv("login_win_icon"):
            self.setWindowIcon(QIcon(self.getv("login_win_icon")))
        # Widgets: User login
        self.lbl_caption.setStyleSheet(self.getv("login_lbl_caption_stylesheet"))
        self.cmb_user.setStyleSheet(self.getv("login_cmb_user_stylesheet"))
        self.txt_password.setStyleSheet(self.getv("login_txt_password_stylesheet"))
        self.lbl_lang.setStyleSheet(self.getv("login_lbl_lang_stylesheet"))
        self.cmb_lang.setStyleSheet(self.getv("login_cmb_lang_stylesheet"))
        self.btn_login.setStyleSheet(self.getv("login_btn_login.stylesheet"))
        if self.getv("login_btn_login_icon"):
            self.btn_login.setIcon(QIcon(self.getv("login_btn_login_icon")))
        self.btn_cancel.setStyleSheet(self.getv("login_btn_cancel_stylesheet"))
        if self.getv("login_btn_cancel_icon"):
            self.btn_cancel.setIcon(QIcon(self.getv("login_btn_cancel_icon")))
        self.btn_new.setStyleSheet(self.getv("login_btn_new_stylesheet"))
        if self.getv("login_btn_new_icon"):
            self.btn_new.setIcon(QIcon(self.getv("login_btn_new_icon")))
        # Widgets: Add new user
        self.lbl_new_caption.setStyleSheet(self.getv("login_lbl_new_caption_stylesheet"))
        self.txt_new_username.setStyleSheet(self.getv("login_txt_new_username_stylesheet"))
        self.txt_new_password.setStyleSheet(self.getv("login_txt_new_password_stylesheet"))
        self.txt_new_password_confirm.setStyleSheet(self.getv("login_txt_new_password_confirm_stylesheet"))
        self.btn_new_ok.setStyleSheet(self.getv("login_btn_new_ok_stylesheet"))
        if self.getv("login_btn_new_ok_icon"):
            self.btn_new_ok.setIcon(QIcon(self.getv("login_btn_new_ok_icon")))
        self.btn_new_cancel.setStyleSheet(self.getv("login_btn_new_cancel_stylesheet"))
        if self.getv("login_btn_new_cancel_icon"):
            self.btn_new_cancel.setIcon(QIcon(self.getv("login_btn_new_cancel_icon")))
        
    def _setup_widgets_language(self, overwrite_user_data=False):
        # Window
        self.setWindowTitle(self.getl("login_win_title"))
        # Widgets: User login
        self.lbl_caption.setText(self.getl("login_lbl_caption_text"))
        self.lbl_caption.setToolTip(self.getl("login_lbl_caption_tt"))
        self.cmb_user.setToolTip(self.getl("login_cmb_user_tt"))
        if overwrite_user_data:
            self.txt_password.setText(self.getl("login_txt_password_text"))
        self.txt_password.setPlaceholderText(self.getl("login_txt_password_placeholder"))
        self.txt_password.setToolTip(self.getl("login_txt_password_text_tt"))
        self.lbl_lang.setText(self.getl("login_lbl_lang_text"))
        self.lbl_lang.setToolTip(self.getl("login_lbl_lang_tt"))
        self.cmb_lang.setToolTip(self.getl("login_cmb_lang_tt"))
        self.btn_login.setText(self.getl("login_btn_login_text"))
        self.btn_login.setToolTip(self.getl("login_btn_login_tt"))
        self.btn_cancel.setText(self.getl("login_btn_cancel_text"))
        self.btn_cancel.setToolTip(self.getl("login_btn_cancel_tt"))
        self.btn_new.setText(self.getl("login_btn_new_text"))
        self.btn_new.setToolTip(self.getl("login_btn_new_tt"))
        # Widgets: Add new user
        self.lbl_new_caption.setText(self.getl("login_lbl_new_caption_text"))
        self.lbl_new_caption.setToolTip(self.getl("login_lbl_new_caption_tt"))
        if overwrite_user_data:
            self.txt_new_username.setText(self.getl("login_txt_new_username_text"))
        self.txt_new_username.setPlaceholderText(self.getl("login_txt_new_username_placeholder"))
        self.txt_new_username.setToolTip(self.getl("login_txt_new_username_tt"))
        if overwrite_user_data:
            self.txt_new_password.setText(self.getl("login_txt_new_password_text"))
        self.txt_new_password.setPlaceholderText(self.getl("login_txt_new_password_placeholder"))
        self.txt_new_password.setToolTip(self.getl("login_txt_new_password_tt"))
        if overwrite_user_data:
            self.txt_new_password_confirm.setText(self.getl("login_txt_new_password_confirm_text"))
        self.txt_new_password_confirm.setPlaceholderText(self.getl("login_txt_new_password_confirm_placeholder"))
        self.txt_new_password_confirm.setToolTip(self.getl("login_txt_new_password_confirm_tt"))
        self.btn_new_ok.setText(self.getl("login_btn_new_ok_text"))
        self.btn_new_ok.setToolTip(self.getl("login_btn_new_ok_tt"))
        self.btn_new_cancel.setText(self.getl("login_btn_new_cancel_text"))
        self.btn_new_cancel.setToolTip(self.getl("login_btn_new_cancel_tt"))


