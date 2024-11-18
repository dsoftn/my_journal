from PyQt5.QtWidgets import QApplication, QComboBox, QTextEdit, QDialog
from PyQt5.QtGui import QTextCharFormat, QColor
from PyQt5 import uic
import os
import datetime

import settings_cls
import utility_cls


# QT Designer's ui file location for LogViewer
DESIGNER_UI_FILE = "data/app/designer/log.ui"
# Location of log file
LOG_FILE_PATH = "data/app/log/log.txt"
# DATE_FORMAT - variable is used by log_viewer
DATE_FORMAT = "%d.%m.%Y."


class Log():
    def __init__(self, settings_object: settings_cls.Settings):
        self._stt = settings_object
        self._date = utility_cls.DateTime(self._stt)
        self._log_file_path = self._stt.get_setting_value("log_file_path")
        if not self._check_is_log_exists():
            self._create_log_file_path()
        self._delete_old_logs()

    def _create_log_file_path(self):
        log_dir = os.path.split(self._log_file_path)
        log_dir = log_dir[0]
        if not os.path.isdir(log_dir):
            os.mkdir(log_dir)

    def _check_is_log_exists(self):
        if os.path.isfile(self._log_file_path):
            return True
        select_file = utility_cls.FileDialog()
        file_name = select_file.show_dialog(title="Select Log File:")
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as file:
                    content = file.read()
                    if content.find("### DsoftNs Log File") == -1 and content.strip() != "":
                        return False
            except Exception as e:
                return False
        else:
            return False
        return True

    def _delete_old_logs(self):
        # Load log file
        if os.path.isfile(self._log_file_path):
            with open(self._log_file_path, "r", encoding="utf-8") as log_file:
                log_content = log_file.read()
        else:
            log_content = ""
        # Split string to find all individual logs
        logs = log_content.split("### DsoftNs Log File")
        logs.pop(0)
        # Delete obsolete logs
        while len(logs) >= self._stt.get_setting_value("number_of_saved_logs"):
            logs.pop(0)
        # Update log file
        updated_log = ""
        logs_today = 1
        for log in logs:
            log = log.lstrip()
            updated_log += "### DsoftNs Log File\n" + log
            if len(log) > 11:
                if log[:11] == self._date.get_today_date():
                    logs_today += 1
        # Add new log header
        updated_log += "### DsoftNs Log File\n"
        updated_log += f"{self._date.get_today_date()}   Log #{len(logs) + 1}  >>> {self._stt.get_setting_value('   app')} <<<  (Log #{logs_today} of this date)\n"
        # Write file
        with open(self._log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write(updated_log)
        # Start log
        self.write_log("Log started ...")

    def write_log(self, text: str) -> bool:
        header = f"--- {self._date.get_today_date()} --- {self._date.get_current_time()} ---\n"
        if os.path.isfile(self._log_file_path):
            with open(self._log_file_path, "a", encoding="utf-8") as log_file:
                text = header + "    " + text + "\n"        
                log_file.write(text)
            return True
        else:
            return False


class LogViewer(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedSize(1100, 700)
        # Load log file
        if os.path.isfile(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
                log_content = log_file.read()
        else:
            log_content = ""
        self.logs = log_content.split("### DsoftNs Log File")
        self.logs.pop(0)
        # Load GUI made with QtDesigner
        uic.loadUi(DESIGNER_UI_FILE, self)
        # Define Widgets
        self.cmb_logs: QComboBox = self.findChild(QComboBox, "comboBox")
        self.txt_log: QTextEdit = self.findChild(QTextEdit, "textEdit")
        # Populate combo box
        self.populate_combo_box()

    def start_gui(self):
        self.cmb_logs.currentTextChanged.connect(self.cmb_text_changed)
        self.show()

    def cmb_text_changed(self):
        text = ""
        if self.cmb_logs.currentData() == -1:
            for log in self.logs:
                text += log.lstrip()
        else:
            text = self.logs[self.cmb_logs.currentData()].lstrip()
        self.txt_log.setPlainText("")
        text_lines = text.split("\n")
        cursor = self.txt_log.textCursor()
        cf = QTextCharFormat()
        font = self.txt_log.font()
        color_light = QColor("#8c8c8c")
        color_normal = QColor("#ffff00")
        color_head = QColor("#00ff00")
        color_head_date_diff = QColor("#aaff00")
        color_error = QColor("#ff0000")
        color_warning = QColor("#ff5500")
        color_user = QColor("#00ffff")
        for line in text_lines:
            line += "\n"
            font.setPointSize(12)
            cf.setForeground(color_normal)
            if len(line) > 3:
                if line[:3] == "---":
                    cf.setForeground(color_light)
                    font.setPointSize(8)
                elif line.lower().find("log #") >= 0:
                    cf.setForeground(color_head_date_diff)
                    font.setPointSize(16)
                    cf.setFont(font)
                    cursor.setCharFormat(cf)
                    part1 = self._get_date_difference(line[:11])
                    cursor.insertText(part1)
                    cf.setForeground(color_head)
                    font.setPointSize(16)
                elif line.lower().find("warning") >= 0 or line.lower().find("warnning") >= 0:
                    cf.setForeground(color_warning)
                elif line.lower().find("error") >= 0:
                    cf.setForeground(color_error)
                if line.find(": ") >= 0:
                    part1 = line[:line.find(": ")+1]
                    line = line[line.find(": ")+1:]
                    cf.setFont(font)
                    cursor.setCharFormat(cf)
                    cursor.insertText(part1)
                    cf.setForeground(color_user)
            cf.setFont(font)
            cursor.setCharFormat(cf)
            cursor.insertText(line)

    def _get_date_difference(self, date: str) -> str:
        try:
            date_log = datetime.datetime.strptime(date, DATE_FORMAT)
            today = datetime.datetime.today()
            diff = (today - date_log).days
        except ValueError:
            diff = "---"
        if diff == 0:
            result = "Today - "
        elif diff == 1:
            result = "Yesterday - "
        elif diff == 2:
            result = "Day before yesterday - "
        else:
            result = f"{diff} days ago - "
        return result

    def populate_combo_box(self):
        self.cmb_logs.addItem("All log records", -1)
        current_index = 0
        for index, log in enumerate(self.logs):
            current_index += 1
            title_start = log.find("\n") + 1
            title_end = log.find("\n", title_start)
            title = log[title_start:title_end]
            self.cmb_logs.addItem(title, index)
        self.cmb_logs.setCurrentIndex(current_index)
        self.cmb_text_changed()


if __name__ == "__main__":
    app = QApplication([])
    view_log = LogViewer()
    view_log.start_gui()
    app.exec_()

