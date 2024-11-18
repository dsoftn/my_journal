from PyQt5.QtWidgets import (QApplication, QTabWidget, QLabel, QPushButton, QTextEdit,
                             QLineEdit, QFrame, QListWidget, QDialog, QScrollArea,
                             QComboBox, QCheckBox, QMessageBox, QWidget, QListWidgetItem,
                             QGridLayout, QProgressBar)
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QFont, QKeyEvent, QTextCharFormat, QColor
from googletrans import Translator
import googletrans
import copy
import time

import default_settings
import settings_cls


"""
The default googletrans package has not been updated in years and currently
has a bug in it. You can fix this by installing the alpha release:
pip install googletrans==3.1.0a0
"""

DESIGNER_UI_FILE = "settings_gui/default_edit.ui"


class SettingsHandler(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(DESIGNER_UI_FILE, self)
        # Load default dictionaries
        self._load_dictionaries()
        self.languages = copy.deepcopy(self.lang["languages:"])
        self._active_lang = self.lang["active_lang:"]
        # Setup widgets
        self._define_widgets()
        # Define illegal characters for key name
        self.illegal_chars = ":'\"\\~`="
        # Init Google Translator
        self.trans = Translator()
        # List od widgets in scroll area
        self.lang_txt_box = []
        # Layout for widgets in ScrollArea
        self.layout = QGridLayout()
        self.layout.setSpacing(10)

    def start_gui(self):
        # Populate Author
        self.lbl_caption.setText("The default setting handler creates a 'default_settings.py' file that contains all settings and languages. This file is used by 'settings_cls.py' module to make initial settings on first run.")
        self.lbl_e_mail.setText(self.stt["author:e_mail"])
        # Pop not needed items in settings and languages
        self.stt.pop("author:")
        self.stt.pop("author:name")
        self.stt.pop("author:e_mail")
        self.lang.pop("active_lang:")
        self.lang.pop("languages:")
        # Populate key lists
        self._populate_stt_keys_list()
        self.lbl_stt_count.setText(str(len(self.stt)) + " Records.")        
        self._populate_lang_keys_list()
        self.lbl_lang_count.setText(str(len(self.lang)) + " Records.")
        self._populate_new_lang_list()
        self._populate_languages_combo_box()
        self._populate_translator_combo_boxes()
        # Default language section
        current_lang = ""
        for language in self.languages:
            self.cmb_default_lang.addItem(language[1], language[0])
            if self._active_lang == language[0]:
                current_lang = language[1]
        self.cmb_default_lang.setCurrentText(current_lang)
        self._update_default_lang_selection()
        # Populate Scroll Area with language QTextEdit widgets
        self._populate_scroll_area()
        # Connect events with slots
        #   Events for settings tab
        self.lst_stt_keys.currentItemChanged.connect(self._lst_stt_current_changed)
        self.lst_stt_keys.doubleClicked.connect(self._lst_stt_current_changed)
        self.txt_stt_key.textChanged.connect(self.txt_key_text_changed)
        self.txt_val.textChanged.connect(self.txt_val_text_changed)
        self.txt_def.textChanged.connect(self.txt_def_text_changed)
        self.txt_min.textChanged.connect(self.txt_min_text_changed)
        self.txt_max.textChanged.connect(self.txt_max_text_changed)
        self.txt_des.textChanged.connect(self.txt_des_text_changed)
        self.txt_rec.textChanged.connect(self.txt_rec_text_changed)
        self.txt_stt_key.returnPressed.connect(self.txt_stt_key_return_press)
        self.txt_val.returnPressed.connect(self.txt_val_return_press)
        self.txt_def.returnPressed.connect(self.txt_def_return_press)
        self.txt_min.returnPressed.connect(self.txt_min_return_press)
        self.txt_max.returnPressed.connect(self.txt_max_return_press)
        self.btn_stt_delete.clicked.connect(self.btn_stt_delete_click)
        self.txt_stt_filter.textChanged.connect(self.txt_stt_filter_text_changed)
        self.txt_stt_filter.returnPressed.connect(self.txt_stt_filter_text_changed)
        self.btn_stt_clear_filter.clicked.connect(self.btn_stt_clear_filter_click)
        self.btn_stt_apply.clicked.connect(self.btn_stt_apply_click)
        # Language Edit
        self.lst_lang_keys.currentItemChanged.connect(self._lst_lang_current_changed)
        self.lst_lang_keys.doubleClicked.connect(self._lst_lang_current_changed)
        self.txt_lang_filter.textChanged.connect(self.txt_lang_filter_text_changed)
        self.txt_lang_filter.returnPressed.connect(self.txt_lang_filter_text_changed)
        self.btn_lang_clear_filter.clicked.connect(self.btn_lang_filter_click)
        self.txt_lang_key.textChanged.connect(self.txt_lang_key_text_changed)
        self.btn_lang_delete.clicked.connect(self.btn_lang_delete_click)
        self.btn_lang_apply.clicked.connect(self.btn_lang_apply_click)
        self.txt_lang_key.returnPressed.connect(self.txt_lang_key_return_press)
        # Add new language events
        self.btn_delete_lang.clicked.connect(self.btn_delete_lang_click)
        self.btn_add_lang.clicked.connect(self.btn_add_lang_click)
        self.cmb_default_lang.currentTextChanged.connect(self.cmb_default_lang_text_changed)
        self.btn_fix_translations.clicked.connect(self.btn_fix_translations_click)
        # Translator events
        self.btn_trans_paste_from.clicked.connect(self.btn_trans_paste_from_click)
        self.btn_trans_copy_to.clicked.connect(self.btn_trans_copy_to_click)
        self.btn_trans_translate.clicked.connect(self.btn_trans_translate_click)
        self.txt_trans_to.textChanged.connect(self.txt_trans_to_text_changed)
        self.btn_switch.clicked.connect(self.btn_switch_click)
        # Update missing translations
        self.btn_update_lang_cancel.clicked.connect(self.btn_update_lang_cancel_click)
        self.btn_update_lang_update.clicked.connect(self.btn_update_lang_update_click)
        self.btn_update_lang_txt_expand.clicked.connect(self.btn_update_lang_txt_expand_click)
        self.btn_update_lang_txt_plus.clicked.connect(self.btn_update_lang_txt_plus_click)
        self.btn_update_lang_txt_minus.clicked.connect(self.btn_update_lang_txt_minus_click)
        self.btn_update_lang_txt_clear.clicked.connect(self.btn_update_lang_txt_clear_click)
        # Other Events
        self.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.btn_save_all.clicked.connect(self.btn_save_click)
        self.closeEvent = self.dialog_close_event
        
        # Set focus to translate from textbox
        self.txt_trans_from.setFocus()
        self.show()

    def btn_update_lang_txt_clear_click(self):
        self.txt_update_lang.setText("")

    def btn_update_lang_txt_expand_click(self):
        if self.btn_update_lang_txt_expand.text() == "><":
            self.btn_update_lang_txt_expand.setText("<>")
            self.txt_update_lang.move(10, 70)
            self.txt_update_lang.resize(891, 361)
            self.txt_update_lang.setStyleSheet('background-color: rgb(74, 74, 74); font: 16pt "Comic Sans MS";')
            self.btn_update_lang_txt_expand.move(860, 70)
            self.btn_update_lang_txt_plus.move(self.btn_update_lang_txt_expand.pos().x() - 90, self.btn_update_lang_txt_expand.pos().y())
            self.btn_update_lang_txt_minus.move(self.btn_update_lang_txt_expand.pos().x() - 50, self.btn_update_lang_txt_expand.pos().y())
            self.btn_update_lang_txt_clear.move(self.btn_update_lang_txt_clear.pos().x(), self.btn_update_lang_txt_expand.pos().y())
            self.lbl_update_lang_affected.setVisible(False)
        elif self.btn_update_lang_txt_expand.text() == "<>":
            self.btn_update_lang_txt_expand.setText("><")
            self.txt_update_lang.move(280, 240)
            self.txt_update_lang.resize(621, 191)
            self.txt_update_lang.setStyleSheet('background-color: rgb(74, 74, 74); font: 9pt "Comic Sans MS";')
            self.btn_update_lang_txt_expand.move(860, 240)
            self.btn_update_lang_txt_plus.move(self.btn_update_lang_txt_expand.pos().x() - 90, self.btn_update_lang_txt_expand.pos().y())
            self.btn_update_lang_txt_minus.move(self.btn_update_lang_txt_expand.pos().x() - 50, self.btn_update_lang_txt_expand.pos().y())
            self.btn_update_lang_txt_clear.move(self.btn_update_lang_txt_clear.pos().x(), self.btn_update_lang_txt_expand.pos().y())
            self.lbl_update_lang_affected.setVisible(True)

    def btn_update_lang_txt_plus_click(self):
        if self.txt_update_lang.font().pointSize() > 140:
            return
        stylesheet = f'background-color: rgb(74, 74, 74); font: {self.txt_update_lang.font().pointSize() + 1}pt "Comic Sans MS";'
        self.txt_update_lang.setStyleSheet(stylesheet)

    def btn_update_lang_txt_minus_click(self):
        if self.txt_update_lang.font().pointSize() < 5:
            return
        stylesheet = f'background-color: rgb(74, 74, 74); font: {self.txt_update_lang.font().pointSize() - 1}pt "Comic Sans MS";'
        self.txt_update_lang.setStyleSheet(stylesheet)

    def btn_fix_translations_click(self):
        self.frm_update_lang_border.setVisible(True)
        self._show_frame_for_update()

    def btn_update_lang_cancel_click(self):
        self.frm_update_lang_border.setVisible(False)
        self._lst_lang_current_changed()

    def btn_switch_click(self):
        tmp = self.cmb_trans_from.currentText()
        self.cmb_trans_from.setCurrentText(self.cmb_trans_to.currentText())
        self.cmb_trans_to.setCurrentText(tmp)

    def dialog_close_event(self, a0):
        if self.btn_save_all.isEnabled():
            result = QMessageBox.question(self, "Save data", "Do you want to save the data before closing the application?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if result == QMessageBox.Yes:
                self.btn_save_click(confirm_save=True)
        app.quit()

    def cmb_default_lang_text_changed(self):
        self._active_lang = self.cmb_default_lang.currentData()
        self.lbl_default_lang.setText(f"[{self._active_lang}, {self.cmb_default_lang.currentText()}]")
        self.btn_save_all.setEnabled(True)
    
    def _update_default_lang_selection(self):
        old_lang = self.cmb_default_lang.currentText()
        self.cmb_default_lang.clear()
        # Check if old language is still in new list
        has_old_lang = False
        for language in self.languages:
            self.cmb_default_lang.addItem(language[1], language[0])
            if language[1] == old_lang:
                has_old_lang = True
        # Define current default lang
        if has_old_lang:
            self.cmb_default_lang.setCurrentText(old_lang)
        else:
            self.cmb_default_lang.setCurrentIndex(0)
        # Show info about default lang
        self._active_lang = self.cmb_default_lang.currentData()
        self.lbl_default_lang.setText(f"[{self._active_lang}, {self.cmb_default_lang.currentText()}]")

    def txt_trans_to_text_changed(self):
        self.btn_trans_copy_to.setEnabled(True)
        self.btn_trans_copy_to.setText("Copy")

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key_Return and a0.modifiers() == QtCore.Qt.ControlModifier:
            self.btn_trans_translate_click()
            self.btn_trans_copy_to_click()
            self.txt_trans_from.selectAll()
        if a0.key() == QtCore.Qt.Key_Escape:
            if self.txt_stt_filter.hasFocus():
                self.txt_stt_filter.setText("")
            elif self.txt_lang_filter.hasFocus():
                self.txt_lang_filter.setText("")
            elif self.txt_stt_key.hasFocus():
                self.txt_stt_key.selectAll()
            elif self.txt_val.hasFocus():
                self.txt_val.setText("")
            elif self.txt_def.hasFocus():
                self.txt_def.setText(self.txt_val.text())
            elif self.txt_min.hasFocus():
                self.txt_min.setText("None")
            elif self.txt_max.hasFocus():
                self.txt_max.setText("None")
            elif self.txt_des.hasFocus():
                self.txt_des.setText("")
            elif self.txt_rec.hasFocus():
                self.txt_rec.setText("")
            elif self.txt_lang_key.hasFocus():
                self.txt_lang_key.selectAll()
            elif self.txt_trans_from.hasFocus() or self.txt_trans_to.hasFocus() or self.cmb_trans_from.hasFocus() or self.cmb_trans_to.hasFocus() or self.btn_trans_paste_from.hasFocus() or self.btn_trans_copy_to.hasFocus() or self.btn_trans_translate.hasFocus():
                self.txt_trans_from.selectAll()
                self.txt_trans_from.setFocus()
            for item in self.lang_txt_box:
                if item[1].hasFocus():
                    item[1].setText("")
            return
            # self.dialog_close_event(0)
        return super().keyPressEvent(a0)

    def btn_trans_translate_click(self):
        txt_from = self.txt_trans_from.toPlainText()
        if txt_from.strip() == "":
            return
        code_from = googletrans.LANGCODES[self.cmb_trans_from.currentText()]
        code_to = googletrans.LANGCODES[self.cmb_trans_to.currentText()]
        trans = Translator()
        translated_text = trans.translate(txt_from, dest=code_to, src=code_from).text
        self.txt_trans_to.setPlainText(translated_text)

    def btn_trans_paste_from_click(self):
        text = QApplication.clipboard().text()
        self.txt_trans_from.setPlainText(text)

    def btn_trans_copy_to_click(self):
        text = self.txt_trans_to.toPlainText()
        QApplication.clipboard().setText(text)
        self.btn_trans_copy_to.setDisabled(True)
        self.btn_trans_copy_to.setText("Copied!")

    def _fix_last_char_quota(self, variable_any_type):
        result = variable_any_type
        if isinstance(variable_any_type, str):
            if len(variable_any_type) > 0:
                if variable_any_type[-1] == '"':
                    result = variable_any_type + " "
            result = result.replace('"""', '"*3')
        return result

    def btn_save_click(self, confirm_save: bool = False):
        if not confirm_save:
            result = QMessageBox.question(self, "Save data", "Are you sure you want to save all the changes made?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
            if result != QMessageBox.Yes:
                return
        # Fix characteres """ and " on last position
        for key in self.stt:
            self.stt[key]["value"] = self._fix_last_char_quota(self.stt[key]["value"])
            self.stt[key]["default_value"] = self._fix_last_char_quota(self.stt[key]["default_value"])
            self.stt[key]["min_value"] = self._fix_last_char_quota(self.stt[key]["min_value"])
            self.stt[key]["max_value"] = self._fix_last_char_quota(self.stt[key]["max_value"])
            self.stt[key]["description"] = self._fix_last_char_quota(self.stt[key]["description"])
            self.stt[key]["recommended"] = self._fix_last_char_quota(self.stt[key]["recommended"])
        for key in self.lang:
            for idx in range(len(self.lang[key])):
                self.lang[key][idx][1] = self._fix_last_char_quota(self.lang[key][idx][1])
        # Get headers anf footers
        func_lang_head, func_lang_foot, func_stt_head, func_stt_foot = self._functions_head_foot()
        # Get languages list
        func_lang_body = '        "languages:": [\n'
        line_to_add = ""
        for data in self.languages:
            line_to_add += f'                        [{str(data[0])}, "{data[1]}"],\n'
        func_lang_body += line_to_add.rstrip(" \n,") + " ],\n\n"
        # Get languages keys
        key = ""
        for data in self.lang.keys():
            key += f'        "{data}": [\n'
            for values in self.lang[data]:
                key += f'            [{str(values[0])}, """{values[1]}"""],\n'
            key = key.rstrip(" \n,")
            key += " ],\n"
        func_lang_body += key.rstrip(" \n,") + "\n"
        if len(self.lang) == 0:
            func_lang_body = func_lang_body.rstrip(" \n,") + "\n"
        # Get settings keys
        func_stt_body = ""
        for key in self.stt.keys():
            func_stt_body += f'        "{key}": ' + '{\n'
            val_val = self._convert_value_to_string(self.stt[key]["value"])
            val_def = self._convert_value_to_string(self.stt[key]["default_value"])
            val_min = self._convert_value_to_string(self.stt[key]["min_value"])
            val_max = self._convert_value_to_string(self.stt[key]["max_value"])
            val_rec = self._convert_value_to_string(self.stt[key]["recommended"])
            val_des = self._convert_value_to_string(self.stt[key]["description"])
            key_values = f"""            "value": {val_val},
            "default_value": {val_def},
            "min_value": {val_min},
            "max_value": {val_max},
            "recommended": {val_rec},
            "description": {val_des}
"""
            func_stt_body += key_values + "            },\n"
        func_stt_body = func_stt_body.rstrip(" \n,") + "\n"
        if len(self.stt) == 0:
            func_stt_head = func_stt_head.rstrip(" \n,") + "\n"
        code = func_lang_head + func_lang_body + func_lang_foot + "\n"
        code += func_stt_head + func_stt_body + func_stt_foot + "\n"
        with open("default_settings.py", "w", encoding="utf-8") as file:
            file.write(code)
        self.btn_save_all.setDisabled(True)
        result = QMessageBox.question(self, "Data Saved", "All data has been validated and file 'default_settings.py' was succesfully created.\n\nDo you want to update the data in the 'settings.json' file as well?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        # Save settings to file
        if result == QMessageBox.Yes:
            stt = settings_cls.Settings()
            stt.save_settings()
            result = QMessageBox.information(self, "Data Saved", "File 'settings.json' was succesfully updated.", QMessageBox.Ok)

    def _convert_value_to_string(self, value) -> str:
        if type(value) == str:
            return f'"""{value}"""'
        if value is None:
            return "None"
        if type(value) == int:
            return str(value)
        elif type(value) == float:
            return str(value)
        elif type(value) == bool:
            if value:
                return "True"
            else:
                return "False"
        return '""'

    def btn_cancel_click(self):
        self.close()

    def btn_update_lang_update_click(self):
        languages_list = []
        languages_complete_list = []
        for lang in self.languages:
            languages_complete_list.append(lang[1])
        for idx in range(self.lst_update_lang.count()):
            if self.lst_update_lang.item(idx).checkState() == QtCore.Qt.Checked:
                languages_list.append(self.lst_update_lang.item(idx).text())
        if not languages_list:
            QMessageBox.information(self, "Update Missing Translations", "You have not checkd any language.", QMessageBox.Ok)
            return
        time_start = time.perf_counter()
        self._update_progres(1, 1, True)
        self._update_report("\nIn progress...\n\n")
        # Translate from other to english
        if "english" in languages_list:
            self._update_report("Translating from other languages to english.\n", "light blue")
            for lang in languages_complete_list:
                if lang != "english":
                    self._update_report(f">> Translate started ... from {lang} to english ...\n")
                    result = self._translate_language(lang, "english", False)
                    if result:
                        self._update_report(f"{lang} to english done succesfuly !\n\n\n\n")
                    else:
                        self._update_report(f"Error. {lang} to english failed !\n\n\n\n")
        self._update_report("---------------------------------------------------------\n")
        # Translate from english to other
        self._update_report("Translating from english to other languages.\n", "light blue")
        for lang in languages_list:
            if lang != "english":
                self._update_report(f">>> Translate started ... from english to {lang} ...\n")
                result = self._translate_language("english", lang, False)
                if result:
                    self._update_report(f"English to {lang} done succesfuly !\n\n\n")
                else:
                    self._update_report(f"Error. English to {lang} failed !\n\n\n")
        self._update_report("---------------------------------------------------------\n")
        time_elaps = time.perf_counter() - time_start
        self._update_report(f"Translation completed in {time_elaps: .2f} sec !\n\n\n")
        self._check_translation_health()
        self.prb_update_lang.setVisible(False)
        self.btn_save_all.setEnabled(True)

    def _show_frame_for_add_new_lang(self, selected_language: str):
        self.frm_update_lang_border.setVisible(True)
        self.lst_update_lang.setDisabled(True)
        self.lbl_update_lang_title.setText("New Language")
        self.lbl_update_lang_description.setText("")
        self.btn_update_lang_update.setDisabled(True)
        self.btn_update_lang_update.setText("New language")
        self.txt_update_lang.setText("")
        self.lbl_update_lang_affected.setText(f"Adding {selected_language} report:")
        self.txt_update_lang.move(10, 100)
        self.txt_update_lang.resize(891, 332)
        self.txt_update_lang.setStyleSheet('background-color: rgb(74, 74, 74); font: 16pt "Comic Sans MS";')
        self.btn_update_lang_cancel.setText("Close")
        self.btn_update_lang_update.setVisible(False)
        self.btn_update_lang_txt_expand.setVisible(False)
        self.btn_update_lang_txt_plus.move(self.btn_update_lang_txt_plus.pos().x(), 100)
        self.btn_update_lang_txt_minus.move(self.btn_update_lang_txt_minus.pos().x(), 100)
        self.btn_update_lang_txt_clear.move(self.btn_update_lang_txt_clear.pos().x(), 100)
        app.processEvents()

    def _show_frame_for_update(self):
        self.prb_update_lang.setVisible(False)
        self.frm_update_lang_border.setVisible(True)
        self.lst_update_lang.setDisabled(False)
        self.lbl_update_lang_title.setText("Update Missing Translations")
        self.lbl_update_lang_description.setText("Each checked language, if not already translated, will be translated from English.\n\nIf you also check the English language, the application will search all languages ​​and English will be updated if data in another language is found.\n\nAfter the translation is complete, please review the data before saving.")
        self.btn_update_lang_update.setDisabled(False)
        self.btn_update_lang_update.setText("Update Translations")
        self.txt_update_lang.setText("")
        self.lbl_update_lang_affected.setText("Affected Languages:")
        self.txt_update_lang.move(280, 240)
        self.txt_update_lang.resize(621, 191)
        self.txt_update_lang.setStyleSheet('background-color: rgb(74, 74, 74); font: 9pt "Comic Sans MS";')
        self.btn_update_lang_cancel.setText("Cancel")
        self.btn_update_lang_update.setVisible(True)
        self.btn_update_lang_txt_expand.setVisible(True)
        self.lbl_update_lang_affected.setVisible(True)
        self.btn_update_lang_txt_expand.move(860, 240)
        self.btn_update_lang_txt_expand.setText("><")
        self.btn_update_lang_txt_plus.move(self.btn_update_lang_txt_expand.pos().x() - 90, self.btn_update_lang_txt_expand.pos().y())
        self.btn_update_lang_txt_minus.move(self.btn_update_lang_txt_expand.pos().x() - 50, self.btn_update_lang_txt_expand.pos().y())
        self.btn_update_lang_txt_clear.move(self.btn_update_lang_txt_clear.pos().x(), self.btn_update_lang_txt_expand.pos().y())
        self._populate_update_lang_lst()
        result = self._check_translation_health()
        if result:
            self._update_report(f"Total of {result} items are not translated.\n\n", "light red")
        else:
            self._update_report(f"All items are translated.\n\n", "light green")
        app.processEvents()

    def _check_translation_health(self) -> int:
        total = 0        
        for idx, lang in enumerate(self.languages):
            not_translated = 0
            for key in self.lang:
                if not self.lang[key][idx][1]:
                    other_has_translate = False
                    for other in self.lang[key]:
                        if other[1]:
                            other_has_translate = True
                            break
                    if other_has_translate:
                        not_translated += 1
            if not_translated:
                self._update_report(f"Language {lang[1]} has {not_translated} untranslated items.\n", "orange")
            else:
                self._update_report(f"Language {lang[1]} has no untranslated items.\n", "light green")
            total += not_translated
        return total

    def _populate_update_lang_lst(self, selected_lang: str = ""):
        self.lst_update_lang.clear()
        for lang in self.languages:
            item = QListWidgetItem()
            item.setText(lang[1])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if selected_lang:
                if lang[1] == selected_lang:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
            else:
                if lang[1] == "serbian" or lang[1] == "english":
                    item.setCheckState(QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.Checked)
            self.lst_update_lang.addItem(item)

    def btn_add_lang_click(self):
        lang_list = [lang[1] for lang in self.languages]
        # Check is any language selected
        if self.cmb_languages.currentText() in ["", None]:
            QMessageBox.information(self, "Add language", "No item has been selected.", QMessageBox.Ok)
            return
        selected_lang = self.cmb_languages.currentText()
        # Check if language already exist
        if selected_lang in lang_list:
            QMessageBox.information(self, "Add language", "Selected language is already in list !", QMessageBox.Ok)
            return

        # Add Translated Language
        if self.chk_auto_translate.isChecked() and len(self.lang) > 0:
            # Find index for english
            index = -1
            for idx, i in enumerate(self.languages):
                if i[1].lower() == "english":
                    index = idx
                    break
            if index == -1:
                QMessageBox.information(self, "Add language", "In order for the automatic translation to the selected language to work properly, you need to have the English language in the database.\nPlease add English language or uncheck the automatic translation option.", QMessageBox.Ok)
                return
            # Show Frame and translate new language
            self._show_frame_for_add_new_lang(selected_lang)
            app.processEvents()
            result = self._translate_language("english", selected_lang, True)
            if result:
                self._populate_new_lang_list()
                self._populate_scroll_area()
                self._populate_lang_keys_list()
                self._lst_lang_current_changed()
                self._update_default_lang_selection()
                QMessageBox.information(self, "Add language", f"The language '{selected_lang}' has been successfully added to the database.", QMessageBox.Ok)
                self.btn_save_all.setEnabled(True)
                return

        # Add new language without translation
        #   First find ID for new language
        id = 0
        for i in self.languages:
            if id < i[0]:
                id = i[0]
        id += 1
        #   Add language to self.languages list
        self.languages.append([id, selected_lang])
        #   Add language to dictionary
        for idx, key in enumerate(self.lang.keys()):
            self.lang[key].append([id, ""])

        self._populate_new_lang_list()
        self._populate_scroll_area()
        self._populate_lang_keys_list()
        self._lst_lang_current_changed()
        self._update_default_lang_selection()
        self._populate_update_lang_lst(selected_lang)
        QMessageBox.information(self, "Add language", f"The language '{selected_lang}' has been successfully added to the database.", QMessageBox.Ok)
        self.btn_save_all.setEnabled(True)

    def _translate_language(self, language_name_from: str, language_name_to: str, add_new_language: bool) -> bool:
        text_lang_from_list = []
        translated_list = []
        # Find index for language from and language to
        index_lang_from = -1
        index_lang_to = -1
        for idx, i in enumerate(self.languages):
            if i[1].lower() == language_name_from:
                index_lang_from = idx
            elif i[1].lower() == language_name_to:
                index_lang_to = idx

        if add_new_language:
            # Find ID for new language
            id = 0
            for i in self.languages:
                if id < i[0]:
                    id = i[0]
            id += 1
            index_lang_to = id

        if index_lang_from == -1:
            self._update_report(f"Fatal Error. Language {language_name_from} not found.\n")
            return False
        elif index_lang_to == -1:
            self._update_report(f"Fatal Error. Language {language_name_to} not found.\n")
            return False

        # Find all missing translations
        for key in self.lang.keys():
            if self.lang[key][index_lang_from][1]:
                if add_new_language:
                    text_lang_from_list.append([key, index_lang_from, self.lang[key][index_lang_from][1]])
                else:
                    if not self.lang[key][index_lang_to][1].strip():
                        text_lang_from_list.append([key, index_lang_from, self.lang[key][index_lang_from][1]])

        if text_lang_from_list:
            # Try to translate many records at once
            self._update_report("Trying to translate many keys at once:\n")
            try_delimiters = ["^", "&", "|", "\n|", "#", "@", "$", "_", "`", "{"]
            attempt = 0
            for delimiter in try_delimiters:
                attempt += 1
                self._update_report(f"Attempt {attempt}/{len(try_delimiters)} ... ")
                self._update_progres(1, len(try_delimiters), True)
                app.processEvents()
                translated_list = self._translate_many(text_lang_from_list, index_lang_to, delimiter, language_name_from, language_name_to)
                if translated_list is None:
                    self._update_report("Failed !\n")
                else:
                    self._update_report("Successs !\n")
                    break
            self._update_progres(1, 1, False)
            app.processEvents()
            
            # Translate records one by one
            if not translated_list:
                self._update_report("\nTranslating key one by one:\n")
                self._update_progres(1, 1, True)
                app.processEvents()
                translated_list = self._translate_one_by_one(text_lang_from_list, index_lang_to, language_name_from, language_name_to)
                if not translated_list:
                    self._update_report("\nFatal Error. Unable to translate language.\n")
                    self._update_progres(1, 1, False)
                    return False
                self._update_progres(1, 1, False)
                app.processEvents()
        else:
            self._update_report("All items are already translated !\n", "light blue")        
        if add_new_language:
            self._update_report("Adding new language ... ")
            app.processEvents()

        #   Add language to self.languages list if new language
        if add_new_language:
            self.languages.append([index_lang_to, language_name_to])
            # Add language to dictionary
            for key in self.lang:
                self.lang[key].append([index_lang_to, ""])
            self._update_report("Done.\n")
            app.processEvents()

        # Add translated data
        self._update_report("Updating keys with translated data ... ")
        app.processEvents()
        for translated_item in translated_list:
            key = translated_item[0]
            for idx, lang_item in enumerate(self.lang[key]):
                if lang_item[0] == translated_item[1]:
                    self.lang[key][idx][1] = translated_item[2]
        self._update_report("Done.\nTranslation finished successfuly !")
        app.processEvents()
        if len(translated_list):
            self._update_report(f"\n{len(translated_list)} records affected.\n")
        else:
            self._update_report("\nNo records affected.\n")
        return True

    def _translate_one_by_one(self, text_from_list: list, index_lang_to: int, language_from: str, language_to: str) -> list:
        text_to_list = []
        trans_from = googletrans.LANGCODES[language_from]
        trans_to = googletrans.LANGCODES[language_to]
        for idx, item in enumerate(text_from_list):
            self._update_progres(idx + 1, len(text_from_list))
            app.processEvents()
            text = item[2]
            try:
                text_translated = self.trans.translate(text, dest=trans_to, src=trans_from).text
            except:
                return None
            text_to_list.append([item[0], index_lang_to, text_translated])
        return text_to_list

    def _translate_many(self, text_from_list: list, index_lang_to: int, delimiter: str, language_from: str, language_to: str) -> list:
        text_block_max = 1500
        text_blocks = []
        text_to_list = []
        text_from = ""
        for key in text_from_list:
            if key[2].find(delimiter) >= 0:
                return None
            text_from += key[2] + delimiter
            if len(text_from) > text_block_max:
                text_from = text_from.rstrip(delimiter)
                text_blocks.append(text_from)
                text_from = ""
        
        text_from = text_from.rstrip(delimiter)
        if text_from:
            text_blocks.append(text_from)

    
        trans_from = googletrans.LANGCODES[language_from]
        trans_to = googletrans.LANGCODES[language_to]
        text_translated = ""
        total_blocks = len(text_blocks)
        idx = 0
        for block_num, block in enumerate(text_blocks):
            try:
                text_translated = self.trans.translate(block, dest=trans_to, src=trans_from).text
            except:
                return None
            text_split = text_translated.split(delimiter)
            for text_split_item in text_split:
                text_to_list.append([text_from_list[idx][0], index_lang_to, text_split_item])
                idx += 1
            text_translated = ""
            if len(block.split(delimiter)) != len(text_split):
                return None
            self._update_progres(block_num + 1, total_blocks)
            app.processEvents()
        return text_to_list
    
    def _update_report(self, text: str, color: str = ""):
        cursor = self.txt_update_lang.textCursor()
        cf = QTextCharFormat()
        clr = QColor()
        clr_lang = QColor()
        clr_lang.setNamedColor("#ff34de")
        if color:
            clr.setNamedColor(color)
        else:
            if text.lower().find("error") >= 0:
                clr.setNamedColor("light red")
            elif text.lower().find("failed") >= 0:
                clr.setNamedColor("orange")
            elif text.lower().find("done") >= 0 or text.lower().find("success") >= 0:
                clr.setNamedColor("light green")
            elif text.lower().find(">>>") >= 0:
                clr.setNamedColor("#81ff0b")
            elif text.lower().find("records affected") >= 0:
                clr.setNamedColor("#ffc2f1")
            else:
                clr.setNamedColor("yellow")
        lang_list = [x[1] for x in self.languages]
        print_list = []
        for lang in lang_list:
            if text.lower().find(lang) >= 0:
                print_list.append([text.lower().find(lang), len(lang)])
        print_list.sort()
        pos = 0
        pos_relative = 0
        for item in print_list:
            cf.setForeground(clr)
            cursor.setCharFormat(cf)
            cursor.insertText(text[:item[0]-pos_relative])
            text = text[item[0]-pos_relative:]
            cf.setForeground(clr_lang)
            cursor.setCharFormat(cf)
            cursor.insertText(text[:item[1]])
            text = text[item[1]:]
            pos_relative += item[0] + item[1]

        if text.lower().find("records affected") >= 0:
            clr_lang.setNamedColor("dark blue")
            cf.setBackground(clr_lang)
        cf.setForeground(clr)
        cursor.setCharFormat(cf)
        cursor.insertText(text)
        self.txt_update_lang.ensureCursorVisible()

    def _update_progres(self, progress_val: int, progress_max: int, show_progress: bool = None):
        if show_progress is not None:
            self.prb_update_lang.setVisible(show_progress)
        self.prb_update_lang.setMaximum(progress_max)
        self.prb_update_lang.setValue(progress_val)
        app.processEvents()

    def btn_delete_lang_click(self):
        # Check i f any item is selected
        if self.lst_new_lang.currentItem() is None:
            QMessageBox.information(self, "Delete language", "No item has been selected.", QMessageBox.Ok)
            return
        lang = self.lst_new_lang.currentItem().text().lower()
        # If language is english or serbian, cancel delete
        if lang == "english" or lang == "serbian":
            QMessageBox.information(self, "Delete language", f"The '{lang}' language is a protected language and cannot be deleted!", QMessageBox.Ok)
            return
        # Delete selected language
        result = QMessageBox.question(self, "Delete language", f"Are you sure you want to delete the '{lang}' language?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
        if result != QMessageBox.Yes:
            return
        for idx in range(len(self.languages)):
            if self.languages[idx][1] == lang:
                id = self.languages[idx][0]
                self.languages.pop(idx)
        # keys = []
        # for key in self.lang.keys():
        #     keys.append(key)
        for key in self.lang.keys():
            for idx in range(len(self.lang[key])):
                if self.lang[key][idx][0] == id:
                    self.lang[key].pop(idx)
                    break
        self._populate_new_lang_list()
        self._populate_scroll_area()
        self._populate_lang_keys_list()
        self._lst_lang_current_changed()
        self.btn_save_all.setEnabled(True)
        self._update_default_lang_selection()
        QMessageBox.information(self, "Delete language", f"The '{lang}' language has been deleted!", QMessageBox.Ok)

    def txt_lang_key_return_press(self):
        self.lang_txt_box[0][1].setFocus()

    def btn_lang_apply_click(self):
        key = self.txt_lang_key.text()
        if key == "":
            QMessageBox.information(self, "Add language key error", "Enter a key name for the new record !", QMessageBox.Ok)
            return
        self.btn_save_all.setEnabled(True)
        if key in self.lang.keys():
            for i in range(len(self.lang_txt_box)):
                box: QTextEdit = self.lang_txt_box[i][1]
                id = self.lang_txt_box[i][0].text()
                id = int(id[id.find("=")+1:id.find(",")])
                if id == self.lang[key][i][0]:
                    self.lang[key][i][1] = box.toPlainText()
                else:
                    print ("Error: def btn_lang_apply_click(self):")
            self.btn_lang_apply.setDisabled(True)
            self.btn_lang_apply.setText("Language key Updated !")
        else:
            self.lang[key] = []
            for i in range(len(self.lang_txt_box)):
                box: QTextEdit = self.lang_txt_box[i][1]
                id = self.lang_txt_box[i][3]
                self.lang[key].append([id, box.toPlainText()])
            self.lst_lang_keys.addItem(key)
            self.lst_lang_keys.setCurrentItem(self.lst_lang_keys.item(self.lst_lang_keys.count()-1))
            key = self.lst_lang_keys.currentItem().text()
            if key is not None:
                self._show_lang_key_data(key)
            self.btn_lang_apply.setDisabled(True)
            self.btn_lang_apply.setText("Language key Added !")

    def btn_lang_delete_click(self):
        lst_row = self.lst_lang_keys.currentRow()
        key = self.txt_lang_key.text()
        if key in self.lang.keys():
            result = QMessageBox.question(self, "Delete language key", "Are you sure you want to delete this language key:\n"+key, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
            if result != QMessageBox.Yes:
                return
            self.lang.pop(key)
            self._populate_lang_keys_list(self.txt_lang_filter.text())
            if self.lst_lang_keys.count() > 0:
                if lst_row < self.lst_lang_keys.count():
                    self.lst_lang_keys.setCurrentRow(lst_row)
                else:
                    self.lst_lang_keys.setCurrentItem(self.lst_lang_keys.item(self.lst_lang_keys.count()-1))
            if self.lst_lang_keys.currentItem() is not None:
                self._show_lang_key_data(self.lst_lang_keys.currentItem().text())
            else:
                self.txt_lang_key.setText("")
                for box_list in self.lang_txt_box:
                    box_list[1].setText("")
            self.btn_save_all.setEnabled(True)

    def translate_button_click(self, index):
        if not self.lang_txt_box[index][2].hasFocus():
            return
        if len(self.languages) < 2:
            QMessageBox.information(self, "Translate", "You must have more than one language in the database to be able to use the translator.", QMessageBox.Ok)
            return
        try:
            if index == 0:
                # Translate from serbian to english
                trans_from = googletrans.LANGCODES["serbian"]
                trans_to = googletrans.LANGCODES["english"]
                text_to_translate = self.lang_txt_box[1][1].toPlainText()
                if self.languages[1][1].lower() == "serbian":
                    trans = self.trans.translate(text_to_translate, dest=trans_to, src=trans_from).text
                    self.lang_txt_box[0][1].setText(trans)
                return
            # Translate from english to any language
            trans_from = googletrans.LANGCODES[self.languages[0][1].lower()]
            trans_to = googletrans.LANGCODES[self.languages[index][1].lower()]
            text_to_translate = self.lang_txt_box[0][1].toPlainText()
            if text_to_translate.strip() == "":
                QMessageBox.information(self, "Translator", "You do not have any text in the English field.\nThe translator can only translate from English to other languages.", QMessageBox.Ok)
                trans = ""
            else:
                trans = self.trans.translate(text_to_translate, dest=trans_to, src=trans_from).text
            self.lang_txt_box[index][1].setText(trans)
        except Exception as e:
            QMessageBox.critical(self, "Translate", str(e), QMessageBox.Ok)
            return

    def txt_lang_key_text_changed(self):
        key = self.txt_lang_key.text()
        self.btn_lang_apply.setEnabled(True)
        if key in self.lang.keys():
            for index, value in enumerate(self.lang[key]):
                self.lang_txt_box[index][1].setText(value[1])
            self.btn_lang_delete.setEnabled(True)
            self.btn_lang_apply.setText("Update language key")
        else:
            if key == "":
                for index in range(len(self.languages)):
                    self.lang_txt_box[index][1].setText("")
            self.btn_lang_delete.setEnabled(False)
            self.btn_lang_apply.setText("Add language key")

    def txt_language_box_text_changed(self):
        if self.btn_lang_apply.text() == "Language key Updated !" or self.btn_lang_apply.text() == "Language key Added !":
            self.btn_lang_apply.setText("Update language key")
        self.btn_lang_apply.setEnabled(True)
    
    def btn_lang_filter_click(self):
        self.txt_lang_filter.setText("")

    def txt_lang_filter_text_changed(self):
        self._populate_lang_keys_list(self.txt_lang_filter.text())
        self._lst_lang_current_changed(None, None)

    def _lst_lang_current_changed(self, x=None, y=None):
        self.lbl_lang_count.setText(str(len(self.lang)) + " Records.")
        if self.lst_lang_keys.currentItem() is not None:
            self._show_lang_key_data(self.lst_lang_keys.currentItem().text())
            self.btn_lang_delete.setEnabled(True)

    def _show_lang_key_data(self, key: str):
        self.txt_lang_key.setText(key)
        for index, value in enumerate(self.lang[key]):
            self.lang_txt_box[index][1].setText(value[1])
        self.btn_lang_apply.setDisabled(True)

    def _populate_scroll_area(self):
        # Clear ScrollArea
        if self.lang_txt_box:
            for item in self.lang_txt_box:
                self.layout.removeWidget(item[0])
                self.layout.removeWidget(item[1])
                self.layout.removeWidget(item[2])
            for item in self.lang_txt_box:
                item[0].deleteLater()
                item[1].deleteLater()
                item[2].deleteLater()

        # Add widgets
        widget = QWidget()
        self.lang_txt_box = []
        for i in range(len(self.languages)):
            self.lang_txt_box.append([])

            self.lang_txt_box[i].append(QLabel())
            self.lang_txt_box[i].append(QTextEdit())
            if self.languages[i][1].lower() == "english":
                button = QPushButton("Translate from serbian")
                button.setDefault(False)
                self.lang_txt_box[i].append(button)
            else:
                button = QPushButton("Translate from english")
                button.setDefault(False)
                self.lang_txt_box[i].append(button)
            self.lang_txt_box[i].append(self.languages[i][0])
            
            self.lang_txt_box[i][0].setFont(QFont("Arial", 10))
            self.lang_txt_box[i][0].setText("ID=" + str(self.languages[i][0]) + ", " + self.languages[i][1])
            self.lang_txt_box[i][1].setStyleSheet("background-color: rgb(0, 170, 0);color: rgb(0, 0, 127);")
            self.lang_txt_box[i][1].setFont(QFont("Comic Sans MS", 12))
            self.lang_txt_box[i][1].setTabChangesFocus(True)
            self.layout.addWidget(self.lang_txt_box[i][0], 2*i, 0)
            self.layout.addWidget(self.lang_txt_box[i][2], 2*i, 1)
            self.layout.addWidget(self.lang_txt_box[i][1], 2*i+1, 0, QtCore.Qt.AlignmentFlag.AlignLeft, 2)
        widget.setLayout(self.layout)
        self.scroll_lang.setWidget(widget)
        # Connect widget events with slots
        for txt_box in self.lang_txt_box:
            txt_box[1].setAcceptRichText(False)
            txt_box[1].textChanged.connect(self.txt_language_box_text_changed)
            txt_box[2].clicked.connect(lambda checked, arg=txt_box[3]: self.translate_button_click(arg))

    def btn_stt_apply_click(self):
        if self.txt_val.text() == "":
            self.txt_val.setText("None")
        if self.txt_def.text() == "":
            self.txt_def.setText("None")
        if self.txt_min.text() == "":
            self.txt_min.setText("None")
        if self.txt_max.text() == "":
            self.txt_max.setText("None")

        self.txt_val_text_changed(self.txt_val.text())
        self.txt_def_text_changed(self.txt_def.text())
        self.txt_min_text_changed(self.txt_min.text())
        self.txt_max_text_changed(self.txt_max.text())
        # If the key is not entered, report an error
        if self.txt_stt_key.text() == "":
            QMessageBox.information(self, "Add setting error", "Enter a key name for the new setting !", QMessageBox.Ok)
            return
        # Enable Save button
        self.btn_save_all.setEnabled(True)
        # Conversion of a string to the appropriate data type
        def convert(value: str):
            val_type = value[:value.find(":=")]
            val_value = value[value.find(":=")+2:]
            if "none" in val_type.lower():
                return None
            elif "integer" in val_type:
                try:
                    return int(val_value)
                except ValueError:
                    return str(val_value)
            elif "float" in val_type:
                try:
                    return float(val_value)
                except ValueError:
                    return str(val_value)
            elif "boolean" in val_type:
                if val_value == "True":
                    return True
                elif val_value == "False":
                    return False
            if len(val_value) > 0:
                if val_value[:1] == "@":
                    val_value = val_value[1:]
            return str(val_value)
        # Convert all setting values
        new_key = self.txt_stt_key.text()
        new_val = convert(self.txt_val.text())
        new_def = convert(self.txt_def.text())
        new_min = convert(self.txt_min.text())
        new_max = convert(self.txt_max.text())
        new_des = self.txt_des.toPlainText()
        new_rec = self.txt_rec.toPlainText()
        # If it is a new key, we first create a dictionary for it
        new_data = False
        if new_key not in self.stt.keys():
            new_data = True
            self.stt[new_key] = {}
        # Record all new data
        self.stt[new_key]["value"] = new_val
        self.stt[new_key]["default_value"] = new_def
        self.stt[new_key]["min_value"] = new_min
        self.stt[new_key]["max_value"] = new_max
        self.stt[new_key]["description"] = new_des
        self.stt[new_key]["recommended"] = new_rec
        # If new_data, update list and clear filter if any, then go to last key in list
        if new_data:
            if self.txt_stt_filter.text():
                self.lst_stt_keys.addItem(new_key)
            else:
                self._populate_stt_keys_list()
            self.lst_stt_keys.setCurrentItem(self.lst_stt_keys.item(self.lst_stt_keys.count()-1))
        self._show_stt_key_data(new_key)
        # Change Apply button        
        if new_data:
            self.btn_stt_apply.setText("Data Added !")    
        else:
            self.btn_stt_apply.setText("Data Updated !")
        self.btn_stt_apply.setDisabled(True)
        self.txt_stt_key.selectAll()
        self.txt_stt_key.setFocus()

    def btn_stt_clear_filter_click(self):
        self.txt_stt_filter.setText("")

    def txt_stt_filter_text_changed(self, a0 = ""):
        self._populate_stt_keys_list(self.txt_stt_filter.text())
        self._lst_stt_current_changed()

    def btn_stt_delete_click(self):
        result = QMessageBox.question(self, "Delete setting key", "Are you sure you want to delete the setting under the key:\n" + self.txt_stt_key.text(), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
        if result == QMessageBox.Yes:
            stt_lst_row = self.lst_stt_keys.currentRow()
            self.stt.pop(self.txt_stt_key.text())
            self._populate_stt_keys_list(self.txt_stt_filter.text())
            if self.lst_stt_keys.count() > 0:
                if stt_lst_row < self.lst_stt_keys.count():
                    self.lst_stt_keys.setCurrentRow(stt_lst_row)
                else:
                    self.lst_stt_keys.setCurrentItem(self.lst_stt_keys.item(self.lst_stt_keys.count()-1))
            if self.lst_stt_keys.currentItem() is None:
                self._show_stt_key_data(key="")
            else:
                self._show_stt_key_data(self.lst_stt_keys.currentItem().text()) 
            # Enable Save button
            self.btn_save_all.setEnabled(True)

    def txt_max_return_press(self):
        self.txt_des.setFocus()

    def txt_min_return_press(self):
        self.txt_max.setFocus()

    def txt_def_return_press(self):
        self.txt_min.setFocus()

    def txt_val_return_press(self):
        def_text = self.txt_def.text()
        delim_pos = def_text.find(":=")
        if delim_pos >= 0:
            def_text = def_text[delim_pos+2:]
        if def_text == "" and self.txt_val.text() != "":
            self.txt_def.setText(self.txt_val.text())
        self.txt_def.setFocus()
    
    def txt_stt_key_return_press(self):
        self.txt_val.setFocus()

    def txt_val_text_changed(self, a0):
        self.btn_stt_apply.setEnabled(True)
        if self.txt_stt_key.text() in self.stt:
            self.btn_stt_apply.setText("Update key")
        else:
            self.btn_stt_apply.setText("Add setting key")
        delim = a0.find(":")
        if delim > 3:
            val_text = a0[delim + 1:]
            if val_text == "":
                a0 = ""
        if self.txt_stt_key.text() in self.stt.keys():
            old_val = self.stt[self.txt_stt_key.text()]["value"]
        else:
            old_val = None
        string_with_type = self._string_for_txt_box(a0, old_val)
        if string_with_type != a0:
            self.txt_val.setText(string_with_type)
        
    def txt_def_text_changed(self, a0):
        self.btn_stt_apply.setEnabled(True)
        if self.txt_stt_key.text() in self.stt:
            self.btn_stt_apply.setText("Update key")
        else:
            self.btn_stt_apply.setText("Add setting key")
        delim = a0.find(":")
        if delim > 3:
            val_text = a0[delim + 1:]
            if val_text == "":
                a0 = ""
        if self.txt_stt_key.text() in self.stt.keys():
            old_val = self.stt[self.txt_stt_key.text()]["default_value"]
        else:
            old_val = None
        string_with_type = self._string_for_txt_box(a0, old_val)
        if string_with_type != a0:
            self.txt_def.setText(string_with_type)

    def txt_min_text_changed(self, a0):
        self.btn_stt_apply.setEnabled(True)
        if self.txt_stt_key.text() in self.stt:
            self.btn_stt_apply.setText("Update key")
        else:
            self.btn_stt_apply.setText("Add setting key")
        delim = a0.find(":")
        if delim > 3:
            val_text = a0[delim + 1:]
            if val_text == "":
                a0 = ""
        if self.txt_stt_key.text() in self.stt.keys():
            old_val = self.stt[self.txt_stt_key.text()]["min_value"]
        else:
            old_val = None
        string_with_type = self._string_for_txt_box(a0, old_val)
        if string_with_type != a0:
            self.txt_min.setText(string_with_type)

    def txt_max_text_changed(self, a0):
        self.btn_stt_apply.setEnabled(True)
        if self.txt_stt_key.text() in self.stt:
            self.btn_stt_apply.setText("Update key")
        else:
            self.btn_stt_apply.setText("Add setting key")
        delim = a0.find(":")
        if delim > 3:
            val_text = a0[delim + 1:]
            if val_text == "":
                a0 = ""
        if self.txt_stt_key.text() in self.stt.keys():
            old_val = self.stt[self.txt_stt_key.text()]["max_value"]
        else:
            old_val = None
        string_with_type = self._string_for_txt_box(a0, old_val)
        if string_with_type != a0:
            self.txt_max.setText(string_with_type)

    def txt_des_text_changed(self):
        self.btn_stt_apply.setEnabled(True)
        if self.txt_stt_key.text() in self.stt:
            self.btn_stt_apply.setText("Update key")
        else:
            self.btn_stt_apply.setText("Add setting key")

    def txt_rec_text_changed(self):
        self.btn_stt_apply.setEnabled(True)
        if self.txt_stt_key.text() in self.stt:
            self.btn_stt_apply.setText("Update key")
        else:
            self.btn_stt_apply.setText("Add setting key")

    def txt_key_text_changed(self):
        self.btn_stt_apply.setDisabled(False)
        if self.txt_stt_key.text() in self.stt.keys():
            self.btn_stt_apply.setText("Update key")
            self.btn_stt_delete.setEnabled(True)
        else:
            self.btn_stt_apply.setText("Add setting key")
            self.btn_stt_delete.setEnabled(False)
            if self.txt_stt_key.text() == "":
                self.txt_val.setText("")
                self.txt_def.setText("")
                self.txt_min.setText("None")
                self.txt_max.setText("None")
                self.txt_rec.setText("")
                self.txt_des.setText("")

    def _lst_stt_current_changed(self, x=None, y=None):
        self.lbl_stt_count.setText(str(len(self.stt)) + " Records.")
        if self.lst_stt_keys.currentItem() is not None:
            self._show_stt_key_data(self.lst_stt_keys.currentItem().text())

    def _show_stt_key_data(self, key: str):
        if key not in self.stt:
            self.txt_stt_key.setText("")
            self.txt_val.setText("")
            self.txt_def.setText("")
            self.txt_min.setText("")
            self.txt_max.setText("")
            self.txt_rec.setText("")
            self.txt_des.setText("")
            return
        # Check if key is in dictionary
        try:
            key_dict = self.stt[key]
        except KeyError:
            self.txt_stt_key.setText("KeyError")
            return
        # Populate widgets
        self.txt_stt_key.setText(key)
        self.txt_des.setText(key_dict["description"])
        self.txt_rec.setText(key_dict["recommended"])

        text = self._string_for_txt_box(str(key_dict["value"]))
        self.txt_val.setText(text)
        text = self._string_for_txt_box(str(key_dict["default_value"]))
        self.txt_def.setText(text)
        text = self._string_for_txt_box(str(key_dict["min_value"]))
        self.txt_min.setText(text)
        text = self._string_for_txt_box(str(key_dict["max_value"]))
        self.txt_max.setText(text)
        # Disable apply button
        self.btn_stt_apply.setDisabled(True)

    def _string_for_txt_box(self, new_value: str, old_value = None) -> str:
        # Extract only value if data type mark exist
        delimiter = new_value.find(":=")
        if delimiter >= 0:
            if len(new_value) == delimiter + 2:
                new_value = ""
            else:
                new_value = new_value[delimiter + 2:]
        
        val_type = self._return_value_type(new_value)
        if val_type == "integer" and type(old_value) == float:
            val_type = "float"
        error = ""
        if val_type != "None":
            if type(old_value) == str and val_type != "string":
                error = "<old=string type mismatch>"
            elif type(old_value) == int and val_type != "integer":
                error = "<old=integer type mismatch>"
            elif type(old_value) == float and val_type != "float":
                error = "<old=float type mismatch>"
            elif type(old_value) == bool and val_type != "boolean":
                error = "<old=boolean type mismatch>"
        result = f"{val_type}{error}:={new_value}"
        return result

    def _return_value_type(self, new_value: str) -> str:
        """Checks the new value data type.
        Args:
            new_value (str): Value in string format
        Returns:
            string: Value type as string "string", "integer", "float", "boolean", "None"
        """
        if new_value is None:
            return "None"
        if new_value == "True" or new_value == "False":
            return "boolean"
        if new_value == "None":
            return "None"
        if new_value.lstrip("-").replace(".", "").isdigit():
            tmp_float = float(new_value)
            tmp_int = int(tmp_float)
            if tmp_float == tmp_int and new_value.find(".") == -1:
                result = "integer"
            else:
                result = "float"
        else:
            result = "string"
        return result

    def _populate_languages_combo_box(self):
        self.cmb_languages.addItems(googletrans.LANGCODES.keys())

    def _populate_translator_combo_boxes(self):
        self.cmb_trans_from.addItems(googletrans.LANGCODES.keys())
        self.cmb_trans_from.setCurrentText("serbian")
        self.cmb_trans_to.addItems(googletrans.LANGCODES.keys())
        self.cmb_trans_to.setCurrentText("english")

    def _populate_stt_keys_list(self, filter: str = ""):
        """Use the 'filter' argument if you want to display in the list only those keys
        that meet a certain criteria.
        When a filter is passed, the filter string is looked for in the key name,
        description, and recommended value description.
        """
        # Setting keys
        self.lst_stt_keys.clear()
        for key in self.stt.keys():
            filter_search_in = f"{key} {self.stt[key]['description']} {self.stt[key]['recommended']}"
            if self._filter_apply(filter=filter, text=filter_search_in):
                self.lst_stt_keys.addItem(key)
        if self.lst_stt_keys.count() > 0:
            self.lst_stt_keys.setCurrentItem(self.lst_stt_keys.item(0))

    def _filter_apply(self, filter: str, text: str) -> bool:
        """Checking whether the text meets the filter criteria.
        SPACE = AND operator
        / = OR operator
        """
        if filter.find("/") >= 0:
            filter_items = [x.strip() for x in filter.split("/") if x.strip() != ""]
            filter_true = False
            for item in filter_items:
                if text.find(item) >= 0:
                    filter_true = True
                    break
            return filter_true
        elif filter.strip().find(" ") >= 0:
            filter_items = [x.strip() for x in filter.split(" ") if x.strip() != ""]
            filter_true = True
            for item in filter_items:
                if text.find(item) == -1:
                    filter_true = False
                    break
            return filter_true
        else:
            if text.find(filter) == -1:
                return False
            else:
                return True

    def _populate_lang_keys_list(self, filter: str = ""):
        """Use the 'filter' argument if you want to display in the list only those keys
        that meet a certain criteria.
        When a filter is passed, the filter string is looked for in the key name,
        and all languages. 
        """
        # Language keys
        self.lst_lang_keys.clear()
        for key in self.lang.keys():
            filter_search_in = key + " "
            for lang_text in self.lang[key]:
                filter_search_in += lang_text[1] + " "
            if self._filter_apply(filter=filter, text=filter_search_in):
                self.lst_lang_keys.addItem(key)
        if self.lst_lang_keys.count() > 0:
            self.lst_lang_keys.setCurrentItem(self.lst_lang_keys.item(0))

    def _populate_new_lang_list(self):
        self.lst_new_lang.clear()
        for language in self.languages:
            self.lst_new_lang.addItem(language[1])
        if self.lst_new_lang.count() > 0:
            self.lst_new_lang.setCurrentItem(self.lst_new_lang.item(0))

    def _load_dictionaries(self):
        self.stt = default_settings.default_settings_dictionary()
        self.lang = default_settings.default_language_dictionary()

    def _define_widgets(self):
        # Frame Missing Translations
        self.frm_update_lang_border: QFrame = self.findChild(QFrame, "frm_update_lang_border")
        self.frm_update_lang: QFrame = self.findChild(QFrame, "frm_update_lang")
        self.lbl_update_lang_affected: QLabel = self.findChild(QLabel, "lbl_update_lang_affected")
        self.lbl_update_lang_title: QLabel = self.findChild(QLabel, "lbl_update_lang_title")
        self.lbl_update_lang_description: QLabel = self.findChild(QLabel, "lbl_update_lang_description")
        self.txt_update_lang: QTextEdit = self.findChild(QTextEdit, "txt_update_lang")
        self.btn_update_lang_update: QPushButton = self.findChild(QPushButton, "btn_update_lang_update")
        self.btn_update_lang_cancel: QPushButton = self.findChild(QPushButton, "btn_update_lang_cancel")
        self.lst_update_lang: QListWidget = self.findChild(QListWidget, "lst_update_lang")
        self.prb_update_lang: QProgressBar = self.findChild(QProgressBar, "prb_update_lang")
        self.btn_update_lang_txt_expand: QPushButton = self.findChild(QPushButton, "btn_update_lang_txt_expand")
        self.btn_update_lang_txt_plus: QPushButton = self.findChild(QPushButton, "btn_update_lang_txt_plus")
        self.btn_update_lang_txt_minus: QPushButton = self.findChild(QPushButton, "btn_update_lang_txt_minus")
        self.btn_update_lang_txt_clear: QPushButton = self.findChild(QPushButton, "btn_update_lang_txt_clear")
        self.frm_update_lang_border.setVisible(False)
        self.frm_update_lang_border.move(0, 0)
        self.frm_update_lang_border.resize(self.contentsRect().width(), self.contentsRect().height())
        self.frm_update_lang.move(150, 83)        
        # Tab Widget
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tabWidget")
        # Scroll Area
        self.scroll_lang: QScrollArea = self.findChild(QScrollArea, "scroll_lang")
        # Labels
        self.lbl_caption: QLabel = self.findChild(QLabel, "lbl_caption")
        self.lbl_e_mail: QLabel = self.findChild(QLabel, "lbl_e_mail")
        self.lbl_default_lang: QLabel = self.findChild(QLabel, "lbl_default_lang")
        self.lbl_stt_count: QLabel = self.findChild(QLabel, "lbl_stt_count")
        self.lbl_lang_count: QLabel = self.findChild(QLabel, "lbl_lang_count")
        # Lists with keys
        self.lst_stt_keys: QListWidget = self.findChild(QListWidget, "lst_stt_keys")
        self.lst_lang_keys: QListWidget = self.findChild(QListWidget, "lst_lang_keys")
        self.lst_new_lang: QListWidget = self.findChild(QListWidget, "lst_new_lang")
        # Input widgets
        #    Line Edit
        self.txt_stt_key: QLineEdit = self.findChild(QLineEdit, "txt_stt_key")
        self.txt_lang_key: QLineEdit = self.findChild(QLineEdit, "txt_lang_key")
        self.txt_val: QLineEdit = self.findChild(QLineEdit, "txt_val")
        self.txt_def: QLineEdit = self.findChild(QLineEdit, "txt_def")
        self.txt_min: QLineEdit = self.findChild(QLineEdit, "txt_min")
        self.txt_max: QLineEdit = self.findChild(QLineEdit, "txt_max")
        self.txt_stt_filter: QLineEdit = self.findChild(QLineEdit, "txt_stt_filter")
        self.txt_lang_filter: QLineEdit = self.findChild(QLineEdit, "txt_lang_filter")
        #    Text Edit
        self.txt_des: QTextEdit = self.findChild(QTextEdit, "txt_des")
        self.txt_rec: QTextEdit = self.findChild(QTextEdit, "txt_rec")
        self.txt_trans_from: QTextEdit = self.findChild(QTextEdit, "txt_trans_from")
        self.txt_trans_to: QTextEdit = self.findChild(QTextEdit, "txt_trans_to")
        # Combo Box
        self.cmb_languages: QComboBox = self.findChild(QComboBox, "cmb_languages")
        self.cmb_trans_from: QComboBox = self.findChild(QComboBox, "cmb_trans_lang_from")
        self.cmb_trans_to: QComboBox = self.findChild(QComboBox, "cmb_trans_lang_to")
        self.cmb_default_lang: QComboBox = self.findChild(QComboBox, "cmb_default_lang")
        # Check Box
        self.chk_auto_translate: QCheckBox = self.findChild(QCheckBox, "chk_auto_translate")
        # Buttons
        self.btn_stt_delete: QPushButton = self.findChild(QPushButton, "btn_stt_delete")
        self.btn_stt_apply: QPushButton = self.findChild(QPushButton, "btn_stt_apply")
        self.btn_lang_delete: QPushButton = self.findChild(QPushButton, "btn_lang_delete")
        self.btn_lang_apply: QPushButton = self.findChild(QPushButton, "btn_lang_apply")
        self.btn_save_all: QPushButton = self.findChild(QPushButton, "btn_save_all")
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_stt_clear_filter: QPushButton = self.findChild(QPushButton, "btn_stt_clear_filter")
        self.btn_lang_clear_filter: QPushButton = self.findChild(QPushButton, "btn_lang_clear_filter")
        self.btn_delete_lang: QPushButton = self.findChild(QPushButton, "btn_delete_lang")
        self.btn_add_lang:QPushButton = self.findChild(QPushButton, "btn_add_lang")
        self.btn_trans_paste_from:QPushButton = self.findChild(QPushButton, "btn_paste_from")
        self.btn_trans_copy_to:QPushButton = self.findChild(QPushButton, "btn_copy_to")
        self.btn_trans_translate:QPushButton = self.findChild(QPushButton, "btn_translate")
        self.btn_switch: QPushButton = self.findChild(QPushButton, "btn_switch")
        self.btn_fix_translations: QPushButton = self.findChild(QPushButton, "btn_fix_translations")
        # Disabled buttons
        self.btn_lang_apply.setDisabled(True)
        self.btn_stt_apply.setDisabled(True)
        self.btn_save_all.setDisabled(True)
        self.btn_stt_delete.setDisabled(True)
        self.btn_lang_delete.setDisabled(True)
        self.btn_trans_copy_to.setDisabled(True)

    def _functions_head_foot(self):
        func_lang_head = """# Generic file made by Default Editor ('default_edit.py')

def default_language_dictionary(key_name: str = "") -> dict:
    lang = {
        """
        active_lang = f'''"active_lang:": {self._active_lang},

'''
        func_lang_head += active_lang

        func_lang_foot = """    }
    if key_name in lang.keys():
        return lang[key_name]
    else:
        return lang

"""        
        func_stt_head = """
def default_settings_dictionary(key_name: str = "") -> dict:
    stt = {
        "author:": "DsoftN",
        "author:name": "Danijel Nisevic",
        "author:e_mail": "dsoftn@gmail.com",

"""
        func_stt_foot = """    }

    if key_name in stt.keys():
        return stt[key_name]
    else:
        return stt

"""
        return func_lang_head, func_lang_foot, func_stt_head, func_stt_foot


if __name__ == "__main__":
    app = QApplication([])
    handler = SettingsHandler()
    handler.start_gui()

    app.exec_()
