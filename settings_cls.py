from PyQt5.QtWidgets import QApplication, QListWidget, QLineEdit, QDialog, QLabel, QPushButton, QMessageBox, QFileDialog
from PyQt5 import uic
import json
import os
import copy
import warnings
import shutil

import default_settings
import UTILS


# File location where all settings will be saved
SETTING_FILE = "data/app/settings/settings.json"
# File location where all language data will be saved
LANGUAGES_FILE = "data/app/settings/languages.json"
# Choose whether you want the 'language.json' file data to be saved when saving the settings
SAVE_LANGUAGE_FILE = True

# ui file location for SettingViewer
DESIGNER_UI_FILE = "settings_gui/settings.ui"


class Settings():
    """Application settings
    There are two files on the disk where the settings are stored.
    
    (1) settings.json
        All settings for the application are stored in this file.
        Settings loaded from a file are kept as a dictionary (self.setting = {}).
        The key in the dictionary is the setting name.
            ["setting_name"] = {}
        Each setting contains its own additional dictionary that has several keys:
            ["value"] = Setting value (any data type)
            ["default_value"] = Default value for setting
            ["min_value"] = The minimum value that can be set
            ["max_value"] = The maximum value that can be set
            ["recommended] = Recommended value description (string)
            ["description"] = Description for setting (string)

    (2) language.json
        If the application supports several languages, the translations into
        the supported languages ​​are saved here.
        Languages ​​are also kept as a dictionary.
        In the dictionary key called 'languages' contains a list of all supported languages.
            ["languages"] = [[ID1, LANG_NAME], [ID2, LANG_name]...]
        The key named 'active_language' indicates the language currently in use.
            ["active_language] = ID
        Each text that appears in the application has its own identifier 
        (usually some descriptive name) and its own value for each of the supported languages.
            ["text_name"] = {
                "ID1" : Value (string),
                "ID2" : Value (string),
                ...
            }
    """

    def __init__(self, settings_json_file_path: str = "", languages_json_file_path: str = ""):
        # Define location of 'settings.json' and 'languages.json' files.
        if settings_json_file_path:
            self._settings_json_file_path = settings_json_file_path
        else:
            self._settings_json_file_path = SETTING_FILE
        if languages_json_file_path:
            self._languages_json_file_path = languages_json_file_path
        else:
            self._languages_json_file_path = LANGUAGES_FILE
        # Define location of 'app_var.json' file
        # This file contains all application variables, lists, dicts...
        settings_dir_name, settings_file_name = os.path.split(self._settings_json_file_path)
        if settings_dir_name:
            self._app_var_json_file_path = f"{settings_dir_name}/app_var_{settings_file_name}"
        else:
            self._app_var_json_file_path = f"app_var_{settings_file_name}"
        # Define dictionary with all settings
        self._settings = {}
        # Define dictionary with languages
        self._lang = {}
        # Define dictionary with application variables
        self._app_var = {}
        # Create directory structure for settings.json and languages.json if not exists
        self._create_directory_structure()
        # Load dict from file 'settings.json'
        self._load_settings()
        # Load languages from file 'languages.json'
        self._load_languages()
        # Load application variables from 'app_var.json'
        self._load_app_var()
        # Debug mode saves info about used settings in file 'settings_cls_debug.txt'
        self.debug_mode = False
        self.debug_settings = []
        self.debug_language = []

        UTILS.LogHandler.add_log_record("#1: Settings loaded.", ["Settings"])

    def __del__(self):
        if self.debug_mode:
            setting_used = "USED SETTINGS KEYS:\n"
            lang_used = "\n\n\nUSED LANGUAGE KEYS:\n\n"
            setting_not_used = "\n\n\nNOT USED SETTINGS KEYS:\n\n"
            lang_not_used = "\n\n\nNOT USED LANGUAGE KEYS:\n\n"
            for key in self._settings:
                if key in self.debug_settings:
                    setting_used += key + ", "
                else:
                    setting_not_used += key + "\n"
            for key in self._lang:
                if key in self.debug_language:
                    lang_used += key + ", "
                else:
                    lang_not_used += key + "\n"
            text = setting_used.strip(",") + lang_used.strip(",") + setting_not_used + lang_not_used
            file = open("settings_cls_debug.txt", "w", encoding="utf-8")
            file.write(text)
            file.close()

    def change_settings_file(self, new_settings_file_path: str):
        self.save_settings()
        self._settings_json_file_path = new_settings_file_path

        settings_dir_name, settings_file_name = os.path.split(self._settings_json_file_path)
        if settings_dir_name:
            self._app_var_json_file_path = f"{settings_dir_name}/app_var_{settings_file_name}"
        else:
            self._app_var_json_file_path = f"app_var_{settings_file_name}"

        self._create_directory_structure()
        self._settings = {}
        self._app_var = {}
        self._load_settings()
        self._load_app_var()
        self.save_settings()

    def _create_directory_structure(self):
        stt_dir = os.path.split(self._settings_json_file_path)
        stt_dir = stt_dir[0]
        lang_dir = os.path.split(self._languages_json_file_path)
        lang_dir = lang_dir[0]
    
        if not os.path.isdir(stt_dir):
            create_dirs = ""
            for path in stt_dir.split("/"):
                if path:
                    create_dirs += f"{path}/"
                    if not os.path.isdir(create_dirs):
                        os.mkdir(create_dirs)
        if not os.path.isdir(lang_dir):
            create_dirs = ""
            for path in lang_dir.split("/"):
                if path:
                    create_dirs += f"{path}/"
                    if not os.path.isdir(create_dirs):
                        os.mkdir(create_dirs)

    def _add_to_dict_new_keys(self, dict_add_to: dict, dict_add_from: dict):
        for key, value in dict_add_from.items():
            if key not in dict_add_to:
                dict_add_to[key] = value
    
    def custom_dict_load(self, file_name: str) -> dict:
        if os.path.isfile(file_name):
            # If file is found, try to load data
            try:
                with open(file_name, "r", encoding="utf-8") as file:
                    result = json.load(file)
                return result
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage("Error in custom_dict_load(). File is corrupted.\n#1\nNew, empty file will be created.", [str(e)])
                with open(file_name, "w", encoding="utf-8") as file:
                    result = {}
                    json.dump(result, file)
                return result
        else:
            return None

    def custom_dict_save(self, file_name: str, data_dict: dict) -> bool:
        # Try to save data to file
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(data_dict, file, indent=2)
            return True
        except Exception as e:
            return False

    def _load_app_var(self):
        if os.path.isfile(self._app_var_json_file_path):
            # If file is found, try to load data
            try:
                with open(self._app_var_json_file_path, "r", encoding="utf-8") as file:
                    self._app_var = json.load(file)
                for key in self._app_var:
                    self._app_var[key]["save"] = True
                # Make backup copy
                shutil.copy(os.path.abspath(self._app_var_json_file_path), os.path.abspath(self._app_var_json_file_path) + ".bak")
                return True
            except Exception as e:
                UTILS.TerminalUtility.WarningMessage("Error while loading '#1'\n#2\nYou can find backup file in:\n#3", [self._app_var_json_file_path, str(e), os.path.abspath(self._app_var_json_file_path) + ".bak"], exception_raised=True)
                raise e
        else:
            # If not return false
            return False

    def _load_languages(self) -> bool:
        # Try to load languages from file
        if os.path.isfile(self._languages_json_file_path):
            # If file is found, load data
            with open(self._languages_json_file_path, "r", encoding="utf-8") as file:
                self._lang = json.load(file)
            self._add_to_dict_new_keys(self._lang, default_settings.default_language_dictionary())
            # Make backup copy
            shutil.copy(os.path.abspath(self._languages_json_file_path), os.path.abspath(self._languages_json_file_path) + ".bak")
            return True
        else:
            UTILS.TerminalUtility.WarningMessage("Language file not found: #1\nYou can find backup file in:\n#2", [self._languages_json_file_path, os.path.abspath(self._languages_json_file_path) + ".bak"], exception_raised=True)
            # If not load default data
            self._lang = default_settings.default_language_dictionary()
            return False

    def _load_settings(self) -> bool:
        # Try to load data from file
        if os.path.isfile(self._settings_json_file_path):
            # If file is found, load data
            with open(self._settings_json_file_path, "r", encoding="utf-8") as file:
                self._settings = json.load(file)
            self._add_to_dict_new_keys(self._settings, default_settings.default_settings_dictionary())
            # Make backup copy
            shutil.copy(os.path.abspath(self._settings_json_file_path), os.path.abspath(self._settings_json_file_path) + ".bak")
            return True
        else:
            UTILS.TerminalUtility.WarningMessage("Settings file not found: #1\nYou can find backup file in:\n#2", [self._settings_json_file_path, os.path.abspath(self._settings_json_file_path) + ".bak"], exception_raised=True)
            # If not, load default data
            self._settings = default_settings.default_settings_dictionary()
            return False

    def save_settings(self) -> str:
        # Try to save data to file
        try:
            # Save settings
            with open(self._settings_json_file_path, "w", encoding="utf-8") as file:
                json.dump(self._settings, file, indent=2)
            # Save application variables
            new_app_var = {}
            for key in self._app_var:
                if self._app_var[key]["save"] == True:
                    new_app_var[key] = self._app_var[key]
            with open(self._app_var_json_file_path, "w", encoding="utf-8") as file:
                json.dump(new_app_var, file, indent=2)
            # Save languages
            if SAVE_LANGUAGE_FILE:
                with open(self._languages_json_file_path, "w", encoding="utf-8") as file:
                    json.dump(self._lang, file, indent=2)
            UTILS.LogHandler.add_log_record("#1: Settings saved.", ["Settings"])
            return ""
        except Exception as e:
            UTILS.TerminalUtility.WarningMessage("Error while saving settings.\nPlease check following files:\n'#1'\n'#2'\nError:\n#3", [self._settings_json_file_path, self._app_var_json_file_path, str(e)], exception_raised=True)
            raise e
    
    def add_setting(self, key_name: str, value, min_value=None, max_value=None, description: str = "", recommended: str = "") -> bool:
        """Adds a new setting to the database.
        If a setting with this key already exists, it will be overwritten.
        """
        try:
            if min_value is not None and max_value is not None:
                if not (min_value <= value <= max_value):
                    UTILS.TerminalUtility.WarningMessage("Value out of range.\nValue must be between #1 and #2\nvalue = #3", [min_value, max_value, value], exception_raised=True)
                    raise ValueError("Value out of range.")
        except TypeError:
            UTILS.TerminalUtility.WarningMessage("Variables: #1, #2 or #3 are not numeric type.\ntype(value): #4\nvalue = #5\ntype(min_value): #6\nmin_value = #7\ntype(max_value): #8\nmax_value = #9", ["value", "min_value", "max_value", type(value), value, type(min_value), min_value, type(max_value), max_value], exception_raised=True)
            raise TypeError("value, min_value or max_value are not numeric type.")
        self._settings[key_name]["value"] = value
        self._settings[key_name]["min_value"] = min_value
        self._settings[key_name]["max_value"] = max_value
        self._settings[key_name]["description"] = description
        self._settings[key_name]["recommended"] = recommended
        return True

    def delete_setting(self, key_name: str) -> None:
        """Deletes setting from the database.
        If a setting with this key does not exists, returns exception.
        """
        if key_name in self._settings:
            self._settings.pop(key_name)
        else:
            UTILS.TerminalUtility.WarningMessage("Setting '#1' does not exist and cannot be deleted.", [key_name], exception_raised=True)
            raise ValueError(f"Setting '{key_name}' does not exist and cannot be deleted.")

    def app_setting_add(self, key_name: str, value=None, save_to_file = False) -> None:
        self._app_var[key_name] = {}
        self._app_var[key_name]["value"] = value
        self._app_var[key_name]["save"] = save_to_file

    def app_setting_delete(self, key_name: str) -> bool:
        if key_name in self._app_var:
            self._app_var.pop(key_name)
            return True
        else:
            return False

    def app_setting_get_value(self, key_name: str) -> object:
        return self._app_var[key_name]["value"]

    def app_setting_set_value(self, key_name: str, value) -> None:
        self._app_var[key_name]["value"] = value

    def app_setting_is_save_to_file(self, key_name: str) -> bool:
        return self._app_var[key_name]["save"]

    def app_setting_set_save_to_file(self, key_name: str, save_to_file: bool) -> None:
        self._app_var[key_name]["save"] = save_to_file

    def app_setting_get_list_of_keys(self, filter: str = "") -> list:
        if filter:
            result = [x for x in self._app_var if x.find(filter) >= 0]
        else:
            result = [x for x in self._app_var]
        return result

    def get_setting_dict(self, key_name: str) -> dict:
        """ Dictionary with all properties of the setting.
        result["value"] - value of the setting
        result["min_value"] - minimal value of the setting
        result["max_value"] - maximal value of the setting
        result["description"] - description of the setting
        result["recommended"] - recommended value of the setting
        """
        if key_name not in self._settings.keys():
            UTILS.TerminalUtility.WarningMessage("Setting with name #1 does not exist.", [key_name], exception_raised=True)
            raise ValueError(f"Setting with name '{key_name}' does not exist.")
        return copy.deepcopy(self._settings[key_name])

    def set_setting_dict(self, key_name: str, new_key_dict: dict) -> bool:
        # Check is new_key_dict is valid
        if "value" not in new_key_dict.keys() or "min_value" not in new_key_dict.keys() or "max_value" not in new_key_dict.keys():
            UTILS.TerminalUtility.WarningMessage("Setting with name #1 does not have valid properties.\nexist in new_key_dict (#2): #3\nexist in new_key_dict (#4): #5\nexist in new_key_dict (#6): #7", [key_name, "value", "value" in new_key_dict.keys(), "min_value", "min_value" in new_key_dict.keys(), "max_value", "max_value" in new_key_dict.keys()], exception_raised=True)
            raise ValueError(f"Setting with name '{key_name}' does not have valid properties.")
        # We must check that value type is correct
        old_dict = self.get_setting_dict(key_name)
        is_valid = True
        value = self._check_is_value_type_valid(old_dict["value"], new_key_dict["value"])
        if value is None and new_key_dict["value"] is not None:
            is_valid = False
        # Check is value out of range
        if not self._is_value_in_range(key_name, value):
            UTILS.TerminalUtility.WarningMessage("Value out of range for setting #1.\n Function #2 returned #3", [key_name, "self._is_value_in_range", "False"], exception_raised=True)
            raise ValueError(f"Value out of range for setting '{key_name}'.")
        max_value = self._check_is_value_type_valid(old_dict["max_value"], new_key_dict["max_value"])
        if max_value is None and new_key_dict["max_value"] is not None:
            is_valid = False
        min_value = self._check_is_value_type_valid(old_dict["min_value"], new_key_dict["min_value"])
        if min_value is None and new_key_dict["min_value"] is not None:
            is_valid = False
        # Check if min or max is not number or None
        if type(min_value) not in [int, float] and min_value is not None:
            is_valid = False
        if type(max_value) not in [int, float] and max_value is not None:
            is_valid = False
        # Check if value is non digit, and min or max are set
        if min_value is not None or max_value is not None:
            if type(value) not in [int, float]:
                is_valid = False
        # If all values are ok, write to dictionary
        if is_valid:
            self._settings[key_name]["value"] = value
            self._settings[key_name]["max_value"] = max_value
            self._settings[key_name]["min_value"] = min_value
            return True
        UTILS.TerminalUtility.WarningMessage("Value error for setting #1.", [key_name], exception_raised=True)
        raise ValueError(f"Value error for setting '{key_name}'.")

    def is_setting_key_exist(self, key_name: str) -> bool:
        return key_name in self._settings

    def get_setting_value(self, key_name: str):
        if key_name in self._settings:
            setting_dict = self.get_setting_dict(key_name)
            if "value" in setting_dict.keys():
                if self.debug_mode:
                    self.debug_settings.append(key_name)
                return setting_dict["value"]
            else:
                UTILS.TerminalUtility.WarningMessage("Setting with name #1 does not have #2 property.", [key_name, "value"], exception_raised=True)
                raise ValueError(f"Setting with name '{key_name}' does not have 'value' property.")
        else:
            UTILS.TerminalUtility.WarningMessage("Setting with name #1 does not exist.", [key_name], exception_raised=True)
            raise ValueError(f"Setting with name '{key_name}' does not exist.")

    def set_setting_value(self, key_name: str, new_value) -> bool:
        """Sets a new setting value under key 'key_name'
        Args:
            key_name (str): The name of the key whose value you want to change
            new_value (any): New value to be set
        Returns:
            bool: If true, the value was set successfully
        """
        if key_name not in self._settings:
            UTILS.TerminalUtility.WarningMessage("Setting with name #1 does not exist.", [key_name], exception_raised=True)
            raise ValueError(f"Setting with name '{key_name}' does not exist.")
        if new_value is None:
            self._settings[key_name]["value"] = new_value
            return True
        # We must check that value type is correct
        old_dict = self.get_setting_dict(key_name)
        result = self._check_is_value_type_valid(old_dict["value"], new_value)
        # Check if value is non digit, and min or max are set
        if old_dict["min_value"] is not None or old_dict["max_value"] is not None:
            if type(result) not in [int, float]:
                UTILS.TerminalUtility.WarningMessage("Setting:#1.\nUnable to set non-numeric data as a setting value that has defined minimum and maximum values.\ntype(new_value): #2\nnew_value = #3, Settings minimum = #4, Settings maximum = #5", [key_name, type(result), result, old_dict["min_value"], old_dict["max_value"]], exception_raised=True)
                raise ValueError(f"Setting:'{key_name}'. Unable to set non-numeric data as a setting value that has defined minimum and maximum values.")
        # Check is value in range min-max
        if not self._is_value_in_range(key_name, result):
            UTILS.TerminalUtility.WarningMessage("Value out of range for setting #1.\n Function #2 returned #3", [key_name, "self._is_value_in_range", "False"], exception_raised=True)
            raise ValueError(f"Setting with name '{key_name}' out of range.")
        if result is not None:
            self._settings[key_name]["value"] = result
            return True
        else:
            if new_value is None:
                self._settings[key_name]["value"] = result
                return True
            else:
                UTILS.TerminalUtility.WarningMessage("Value error for setting #1.", [key_name], exception_raised=True)
                raise ValueError(f"Setting with name '{key_name}' is not valid data type.")

    def get_keys_list(self, filter: str = "") -> list:
        """Returns a list of keys according to the specified criteria.
        Example:
            If you create settings '@user.name.John', '@user.name.Mike', '@user.name.Homer'
            then you can call:
                Settings.get_keys_list(filter = '@user.name')
        """
        result = []
        for key in self._settings:
            if isinstance(self._settings[key], dict):
                if filter in key:
                    result.append(key)
        return result

    def _is_value_in_range(self, key_name: str, value) -> bool:
        result = True
        if type(value) == int or type(value) == float:
            key_dict = self.get_setting_dict(key_name)
            if type(key_dict["min_value"]) == int or type(key_dict["min_value"]) == float:
                if value < key_dict["min_value"]:
                    result = False
            if type(key_dict["max_value"]) == int or type(key_dict["max_value"]) == float:
                if value > key_dict["max_value"]:
                    result = False
        return result

    def _check_is_value_type_valid(self, old_value, new_value):
        """Checks if the new value is of the same type as the old one.
        If not, it tries to convert the new value to the type of the old value.
        If successful, it returns a new value that has the same data type as
        the old one, otherwise it returns None.
        """
        if type(old_value) == type(new_value):
            return new_value
        if new_value is None:
            return None
        if old_value is None:
            return new_value
        result = None
        try:
            if type(old_value) == int:
                result = int(new_value)
            elif type(old_value) == float:
                result = float(new_value)
            elif type(old_value) == str:
                result = str(new_value)
            elif type(old_value) == bool:
                result = bool(new_value)
            elif old_value is None:
                if type(new_value) == str:
                    if new_value.lstrip("-").replace(".", "").isdigit():
                        tmp_float = float(new_value)
                        tmp_int = int(tmp_float)
                        if tmp_float == tmp_int:
                            result = int(new_value)
                        else:
                            result = float(new_value)
                    else:
                        result = new_value
                else:
                    result = new_value
            return result
        except ValueError:
            return None

    def get_language_name(self, language_id: int) -> str:
        lang_name = ""
        for language in self._lang["languages:"]:
            if language[0] == language_id:
                lang_name = language[1]
                break
        return lang_name

    def get_language_id(self, language_name: str) -> int:
        lang_id = ""
        for language in self._lang["languages:"]:
            if language[1] == language_name:
                lang_id = language[0]
                break
        return lang_id

    def lang(self, key_name: str) -> str:
        """Returns text from language dict for key_name and current language
        """
        result = None
        active_lang = self._lang["active_lang:"]
        if key_name in self._lang.keys():
            for language in self._lang[key_name]:
                if language[0] == active_lang:
                    result = language[1]
        # else:
           # NOTE: AppSettings often contains keys that are not in the language dictionary. It is normal behavior.
        #    print (f"Language key not found: {key_name}")
        #    UTILS.TerminalUtility.WarningMessage("Language key with name #1 does not exist.", [key_name])

        if self.debug_mode:
            self.debug_language.append(key_name)
        return result

    def _is_valid_color(self, color_value_string: str) -> str:
        """Checks if color string is valid.
        Args:
            color_value_string (str): Color in HEX or RGB format (#000000 or rgb(0,0,0))
        Returns: valid color in hex form
            str: HEX color name or empty string if color is not valid
        """
        color = ""
        is_valid = False
        c_str = color_value_string.strip()
        if color_value_string.strip().lower() == "transparent":
            return color_value_string.strip().lower()
        
        # Case when a hex value is passed
        if "#" in c_str:
            c_str = c_str.strip(" #;")
            if len(c_str) < 9:
                is_valid = True
                for i in c_str:
                    if i.lower() not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]:
                        is_valid = False
                        break
                if is_valid:
                    color = f"#{c_str}"

        # Case when an rgb value is passed
        if "(" in c_str and ")" in c_str:
            start_pos = c_str.find("(")
            end_pos = c_str.find(")")
            # There must be at least two characters between the brackets (,,) = (0,0,0)
            if (end_pos - start_pos) < 3:
                is_valid = False
            else:
                # c_str = content between brackets
                c_str = c_str[start_pos + 1:end_pos]
                # Separate each number between the brackets separated by a comma, if there is no number, put 0
                values = [x.strip() if x.strip() != "" else "0" for x in c_str.split(",")]
                # There must be exactly 3 values ​​between the brackets
                if len(values) == 3 or len(values) == 4:
                    # Check if all values ​​are numbers
                    if all([x.isdigit() for x in values]):
                        red = int(values[0])
                        green = int(values[1])
                        blue = int(values[2])
                        alpha_hex = ""
                        if len(values) == 4:
                            alpha = int(values[3])
                            if alpha in range(0, 256):
                                alpha_hex = hex(alpha)[2:].zfill(2)
                            else:
                                alpha_hex = None
                        
                        # Check that all values ​​are in the range 0-255
                        if red in range(0, 256) and green in range(0, 256) and blue in range(0, 256):
                            # Convert each value to a HEX number and pad the left side with zeros to make the number of characters exactly 2
                            red_hex = hex(red)[2:].zfill(2)
                            green_hex = hex(green)[2:].zfill(2)
                            blue_hex = hex(blue)[2:].zfill(2)
                            # Finally, concatenate all HEX values ​​and add # to the beginning
                            if alpha_hex is not None:
                                color = "#" + red_hex + green_hex + blue_hex + alpha_hex
                                is_valid = True
        if is_valid:
            return color
        else:
            return ""

    @property
    def GetListOfAllLanguages(self) -> list:
        return self._lang["languages:"]

    @property
    def GetListOfAllLanguagesIDs(self) -> list:
        result = []
        for language in self._lang["languages:"]:
            result.append(language[0])
        return result

    @property
    def GetListOfAllLanguagesNames(self) -> list:
        result = []
        for language in self._lang["languages:"]:
            result.append(language[1])
        return result

    @property
    def ActiveLanguageID(self) -> int:
        return self._lang["active_lang:"]
    
    @ActiveLanguageID.setter
    def ActiveLanguageID(self, active_lang: int):
        lang_ids = [id[0] for id in self._lang["languages:"]]
        if active_lang in lang_ids:
            self._lang["active_lang:"] = active_lang
        else:
            UTILS.TerminalUtility.WarningMessage("The requested active language ID (#1) does not exist.", [active_lang], exception_raised=True)
            raise ValueError("The requested active language ID does not exist.")


class SettingViewer(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(DESIGNER_UI_FILE, self)
        self.stt = Settings()

    def start_gui(self):
        # Define widgets
        self._define_widgets()
        # Populate Author
        self.lbl_author.setText(f"Author:     {self.stt.get_setting_dict('author:')}, {self.stt.get_setting_dict('author:name')}")
        self.lbl_e_mail.setText(self.stt.get_setting_dict("author:e_mail"))
        self.lbl_file.setText(f"Editing file: {self.stt._settings_json_file_path}")
        # Populate Keys List
        self._populate_key_list()
        # Connect events with slots
        self.lst_keys.currentItemChanged.connect(self._lst_current_changed)
        self.txt_value.textChanged.connect(self._text_changed)
        self.txt_min.textChanged.connect(self._text_changed)
        self.txt_max.textChanged.connect(self._text_changed)
        self.btn_cancel.clicked.connect(self._cancel_clicked)
        self.btn_apply.clicked.connect(self._apply_clicked)
        self.btn_save_all.clicked.connect(self._btn_save_clicked)
        self.btn_file.clicked.connect(self.btn_file_click)
        self.txt_filter.textChanged.connect(self.txt_filter_text_changed)
        self.btn_filter.clicked.connect(self.btn_filter_click)
        self.lbl_description.mouseDoubleClickEvent = self.lbl_description_changed
        self.show()

    def lbl_description_changed(self, x):
        font = self.lbl_description.font()
        if font.pointSize() > 9:
            font.setPointSize(font.pointSize()-1)
        else:
            font.setPointSize(12)
        self.lbl_description.setFont(font)

    def txt_filter_text_changed(self):
        self._populate_key_list()

    def btn_filter_click(self):
        self.txt_filter.setText("")

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

    def btn_file_click(self):
        if self.btn_save_all.isEnabled():
            QMessageBox.information(self, "File not saved", "To open a new file, you must first save the changes!", QMessageBox.Ok)
            return
        result, _ = QFileDialog.getOpenFileName(None, "Select setting file.", filter="*.json")
        if result:
            self.stt.change_settings_file(result)
            self._populate_key_list()
            self._update_item_data()
            self.lbl_file.setText(f"Loaded File: {self.stt._settings_json_file_path}")

    def _btn_save_clicked(self):
        result = QMessageBox.question(self, "Save settings", "Are you sure you want to save all changes?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
        if result == QMessageBox.Yes:
            success = self.stt.save_settings()
            if success:
                self.lbl_error.setText(success)
            else:
                QMessageBox.information(self, "Save settings", "Data has been saved successfully!", QMessageBox.Ok)
                self.btn_save_all.setEnabled(False)

    def _apply_clicked(self):
        key_name = self.lbl_key.text()
        key_dict = self.stt.get_setting_dict(key_name)
        new_val = self._return_correct_value_type(self.txt_value.text())
        new_min = self._return_correct_value_type(self.txt_min.text())
        new_max = self._return_correct_value_type(self.txt_max.text())

        key_dict["value"] = new_val
        key_dict["max_value"] = new_max
        key_dict["min_value"] = new_min
        result = self.stt.set_setting_dict(key_name, copy.deepcopy(key_dict))
        if not result:
            if not self.stt._is_value_in_range(self.lbl_key.text(), self.stt._check_is_value_type_valid(None, self.txt_value.text())):
                self.lbl_error.setText("Error: Value out of range.")
            else:
                self.lbl_error.setText("Error: Value error.")
        else:
            self.lbl_error_2.setText("The data has been updated.\n'Confirm and Save' to save the updated data.")
            self.btn_apply.setEnabled(False)
            self.btn_save_all.setEnabled(True)

        self.lbl_value.setText(f"Value type: {str(type(self.stt.get_setting_value(self.lbl_key.text())))}")

    def _return_correct_value_type(self, new_value: str):
        """Checks the new value data type.
        Args:
            new_value (str): Value in string format
        Returns:
            any: Value
        """
        if new_value is None:
            return None
        if new_value == "None":
            return None
        if new_value == "True":
            return True
        elif new_value == "False":
            return False
        if new_value.lstrip("-").replace(".", "").isdigit():
            tmp_float = float(new_value)
            tmp_int = int(tmp_float)
            if tmp_float == tmp_int and new_value.find(".") == -1:
                result = tmp_int
            else:
                result = tmp_float
        else:
            result = new_value
        return result

    def _cancel_clicked(self):
        self.close()

    def _text_changed(self):
        self.btn_apply.setEnabled(True)
        self.lbl_error.setText("")
        self.lbl_error_2.setText("")

    def _lst_current_changed(self, x, y):
        if self.lst_keys.currentItem() is None:
            return
        key = self.lst_keys.currentItem().text()
        self._update_item_data(key)
        self.btn_apply.setEnabled(False)
        self.lbl_error.setText("")
        self.lbl_error_2.setText("")

    def _update_item_data(self, key: str = ""):
        if not key:
            self.lbl_key.setText("")
            self.lbl_description.setText("")
            self.lbl_recommended.setText("")
            self.lbl_value.setText("")
            self.txt_value.setText("")
            self.txt_max.setText("")
            self.txt_min.setText("")
            self.btn_apply.setEnabled(False)
            return
        self.lbl_key.setText(key)
        if len(key) > 30:
            font = self.lbl_key.font()
            font.setPointSize(12)
            self.lbl_key.setFont(font)
        else:
            font = self.lbl_key.font()
            font.setPointSize(16)
            self.lbl_key.setFont(font)
        item = self.stt.get_setting_dict(key)
        self.lbl_description.setText(item["description"])
        self.lbl_recommended.setText(item["recommended"])
        self.lbl_value.setText(f"Value type: {str(type(item['value']))}")
        self.txt_value.setText(str(item["value"]))
        self.txt_max.setText(str(item["max_value"]))
        self.txt_min.setText(str(item["min_value"]))
        self.btn_apply.setEnabled(False)

    def _populate_key_list(self):
        self.lst_keys.clear()
        for key in self.stt._settings:
            if key.find("author:") == -1:
                search_string = key + self.stt._settings[key]["description"] + self.stt._settings[key]["recommended"]
                if self._filter_apply(self.txt_filter.text(), search_string):
                    self.lst_keys.addItem(str(key))
        if self.lst_keys.count() == 0:
            return
        self.lst_keys.setCurrentItem(self.lst_keys.item(0))
        self._lst_current_changed(None, None)
    
    def _define_widgets(self):
        # Labels
        self.lbl_author: QLabel = self.findChild(QLabel, "lbl_author")
        self.lbl_e_mail: QLabel = self.findChild(QLabel, "lbl_e_mail")
        self.lbl_key: QLabel = self.findChild(QLabel, "lbl_key")
        self.lbl_description: QLabel = self.findChild(QLabel, "lbl_description")
        self.lbl_recommended: QLabel = self.findChild(QLabel, "lbl_recommended")
        self.lbl_value: QLabel = self.findChild(QLabel, "lbl_value")
        self.lbl_error: QLabel = self.findChild(QLabel, "lbl_error")
        self.lbl_error_2: QLabel = self.findChild(QLabel, "lbl_error_2")
        self.lbl_file: QLabel = self.findChild(QLabel, "lbl_file")
        # Line Edit
        self.txt_value: QLineEdit = self.findChild(QLineEdit, "txt_value")
        self.txt_max: QLineEdit = self.findChild(QLineEdit, "txt_max")
        self.txt_min: QLineEdit = self.findChild(QLineEdit, "txt_min")
        self.txt_filter: QLineEdit = self.findChild(QLineEdit, "txt_filter")
        # Buttons
        self.btn_apply: QPushButton = self.findChild(QPushButton, "btn_apply")
        self.btn_apply.setEnabled(False)
        self.btn_save_all: QPushButton = self.findChild(QPushButton, "btn_save_all")
        self.btn_save_all.setEnabled(False)
        self.btn_cancel: QPushButton = self.findChild(QPushButton, "btn_cancel")
        self.btn_file: QPushButton = self.findChild(QPushButton, "btn_file")
        self.btn_filter: QPushButton = self.findChild(QPushButton, "btn_filter")
        # List Widget
        self.lst_keys: QListWidget = self.findChild(QListWidget, "lst_keys")

        


if __name__ == "__main__":
    app = QApplication([])

    view = SettingViewer()
    view.start_gui()

    app.exec_()

