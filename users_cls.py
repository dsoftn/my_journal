import os
import json
import copy

import settings_cls
import database_cls
import utility_cls
import UTILS


class User():
    """Manage users.
    This class provides all the information about users that other parts
    of the application may request.
    The 'settings_cls' module is used to store user data.
    Common usage:
        Set the active user using the 'set_active_user()' method
        Now you can request all data related to this user.
    User dictionary:
        id          (int): User ID
        username    (str): Username
        password    (str): Password
        language_id (int): The ID of the language the user is using
        language_name(str): The name of the language the user is using
        settings_path(str): Location of the 'settings.txt' file for the user
        db_path     (str): The location of the database where the data is stored
        db_type     (str): Database type
        db_username (str): Data required to access the database
        db_password (str): Data required to access the database
        firstname   (str): First Name
        lastname    (str): Last Name
        nickname    (str): Nick
        gender      (str): Gender
        phone       (str): Phone Number
        email       (str): E-mail address
        address     (str): Residential address
        description (str): Description
        created_at  (str): The date the user account was created
    """

    def __init__(self, settings: settings_cls.Settings, active_user_id: int = 0):
        # Set variables
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value

        self._users_json_file_path = self.getv("users_cls_file_path")
        self._create_file_path_and_file(self._users_json_file_path)
        self._users_dict = {}  # Dictionary of all users
        self._active_user_id = active_user_id  # Currently active user ID
        self.refresh_users_dict()
        UTILS.LogHandler.add_log_record("#1: Current user object created.", ["User"])

    def _create_file_path_and_file(self, file_path: str):
        """Create the directories and the file if they do not exist.
        """
        user_dir = os.path.split(file_path)
        user_dir = user_dir[0]
        if not os.path.isdir(user_dir):
            os.mkdir(user_dir)
        if not os.path.isfile(file_path):
            file = open(file_path, "w", encoding="utf-8")
            file.close()

    def refresh_users_dict(self) -> bool:
        """Reloads all user data.
        """
        self._users_dict = {}
        try:
            with open(self._users_json_file_path, "r", encoding="utf-8") as file:
                self._users_dict = json.load(file)
            UTILS.LogHandler.add_log_record("#1: Users data loaded.", ["User"])
            return True
        except Exception as e:
            UTILS.LogHandler.add_log_record("#1: Error. Loading users data.\n#2", ["User", str(e)], warning_raised=True)
            self._users_dict = {}
            return False

    def save_users_to_file(self):
        with open(self._users_json_file_path, "w", encoding="utf-8") as file:
            json.dump(self._users_dict, file)
        UTILS.LogHandler.add_log_record("#1: Users data saved.", ["User"])

    def get_user_info_all(self, user_id: int) -> dict:
        """Returns a dictionary with all information about the requested user.
        If the user ID is not specified, it returns information about the currently active user.
        """
        if self._active_user_id != 0:
            result = copy.deepcopy(self._users_dict[str(user_id)])
            return result
        else:
            return None
    
    def is_user_id(self, user_id: int) -> bool:
        """Checks if there is a user for this ID.
        """
        if str(user_id) in self._users_dict:
            return True
        return False

    def is_user_name(self, user_name: str) -> bool:
        """Checks if there is a user for this username.
        """
        for user in self._users_dict:
            if user_name == self._users_dict[user]["username"]:
                return True
        return False

    def get_user_id(self, username: str) -> int:
        for user in self._users_dict:
            if username == self._users_dict[user]["username"]:
                return self._users_dict[user]["id"]
        UTILS.TerminalUtility.WarningMessage("User with username #1 does not exist!", [username], exception_raised=True)
        raise ValueError(f"User with username '{username}' does not exist!")

    def get_user_name(self, user_id: int) -> str:
        for user in self._users_dict:
            if str(user_id) == user:
                return self._users_dict[user]["username"]
        UTILS.TerminalUtility.WarningMessage("User with user ID #1 does not exist!", [user_id], exception_raised=True)
        raise ValueError(f"User with user ID '{user_id}' does not exist!")

    def check_user_password(self, user_name: str, password: str) -> bool:
        if self._users_dict[str(self.get_user_id(user_name))]["password"] == self._encrypt_password(password, user_name):
            return True
        else:
            return False

    def get_user_language_id(self, user_id: int) -> int:
        """Returns the language ID for the requested user.
        If the language does not exist in the database, it returns 0, English.
        """
        if user_id == 0:
            return 0
        lang_id = self._users_dict[str(user_id)]["language_id"]
        lang_name = ""
        for lang in self.getl("languages:"):
            if lang[0] == lang_id:
                lang_name = lang[1]
                break
        if lang_name:
            return lang_id
        else:
            return 0

    def get_user_language_name(self, user_id: int) -> str:
        """Returns the language name for the requested user.
        """
        if user_id != 0:
            return self._users_dict[str(user_id)]["language_name"]
        return ""

    def add_new_user(self, user_name: str, user_password: str, language_id: int = 0) -> None:
        # Find ID for new user
        id_list = [int(x) for x in self._users_dict]
        if id_list:
            new_id = max(id_list) + 1
        else:
            new_id = 1
        if new_id <= self.getv("users_last_added_id"):
            new_id = self.getv("users_last_added_id") + 1
        self._stt.set_setting_value("users_last_added_id", new_id)
        new_id = str(new_id)
        # Set 'settings.json' file path for new user
        settings_file = self.getv("users_data_path").rstrip("/") +  "/"
        settings_file += str(new_id) + "_" + self._adjust_username_for_filename(user_name)
        settings_file += ".json"
        # Set database file path for new user
        db_file = self.getv("users_data_path").rstrip("/") +  "/"
        db_file += str(new_id) + "_" + self._adjust_username_for_filename(user_name)
        db_file += ".db"
        self._create_file_path_and_file(db_file)
        database_info = database_cls.DBInfo(db_file, "SQLite")
        database = database_cls.DataBase(database_info)
        database.create_new_database(database_info, self.getv("sqlite_database_creation_sql"))
        database.close_db()
        # Date
        date_cls = utility_cls.DateTime(self._stt)
        created = date_cls.get_today_date()
        # Find language name, if language does not exist switch to english
        lang_name = ""
        for lang in self._stt.GetListOfAllLanguages:
            if lang[0] == language_id:
                lang_name = lang[1]
                break
        if not lang_name:
            language_id = 0
            lang_name = "english"

        self._users_dict[new_id] = {
            "id": int(new_id),
            "username": user_name,
            "password": self._encrypt_password(user_password, user_name),
            "language_id": language_id,
            "language_name": lang_name,
            "settings_path": settings_file,
            "db_path": db_file,
            "db_type": "SQLite",
            "db_username": None,
            "db_password": None,
            "firstname": "",
            "lastname": "",
            "nickname": "",
            "gender": "",
            "phone": "",
            "email": "", 
            "address": "",
            "address": "",
            "created_at": created
        }
        self.save_users_to_file()
        UTILS.LogHandler.add_log_record("#1: New user added. (ID=#2, UserName=#3)", ["User", new_id, user_name])

    def _adjust_username_for_filename(self, user_name: str, max_chars: int = 10) -> str:
        allowed = "qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM0123456789_"
        result = ""
        for char in user_name:
            if char in allowed:
                result += char
        if len(result) > max_chars:
            result = result[:max_chars]
        return result

    def _encrypt_password(self, password: str, username: str) -> str:
        return password

    def _decrypt_password(self, password: str, username: str) -> str:
        return password

    @property
    def DBInfoObject(self) -> database_cls.DBInfo:
        db_info = database_cls.DBInfo(self.db_path, self.db_type, self.db_username, self.db_password)
        return db_info
    
    @property
    def ListOfAllUsers(self) -> list:
        """
        Returns:
            list: [user_id(int), username(str)]
        """
        result = []
        for user in self._users_dict:
            result.append([self._users_dict[user]["id"], self._users_dict[user]["username"]])
        return result

    @property
    def ActiveUserID(self) -> int:
        """Returns the ID of the currently active user.
        """
        return self._active_user_id

    @ActiveUserID.setter
    def ActiveUserID(self, user_id: int):
        """Sets the currently active user.
        """
        if str(user_id) in self._users_dict:
            self._active_user_id = user_id
        else:
            UTILS.TerminalUtility.WarningMessage("The user with ID #1 is not found", [user_id], exception_raised=True)
            raise ValueError("The user is not found")

    @property
    def id(self) -> int:
        return self._users_dict[str(self._active_user_id)]["id"]

    @property
    def username(self) -> str:
        return self._users_dict[str(self._active_user_id)]["username"]
    
    @property
    def password(self) -> str:
        result = self._users_dict[str(self._active_user_id)]["password"]
        return self._decrypt_password(result, self.username)
    
    @password.setter
    def password(self, password: str):
        result = self._encrypt_password(password, self.username)
        self._users_dict[str(self._active_user_id)]["password"] = result

    @property
    def language_id(self) -> int:
        return self._users_dict[str(self._active_user_id)]["language_id"]

    @language_id.setter
    def language_id(self, language_id: int):
        if language_id in self._stt.GetListOfAllLanguagesIDs:
            self._users_dict[str(self._active_user_id)]["language_id"] = language_id
            self._users_dict[str(self._active_user_id)]["language_name"] = self._stt.get_language_name(language_id)
        else:
            UTILS.TerminalUtility.WarningMessage("Language with ID #1 does not exist.", [language_id], exception_raised=True)
            raise ValueError("Language does not exist.")

    @property
    def language_name(self) -> str:
        return self._users_dict[str(self._active_user_id)]["language_name"]

    @language_name.setter
    def language_name(self, language_name: str):
        if language_name in self._stt.GetListOfAllLanguagesNames:
            self._users_dict[str(self._active_user_id)]["language_name"] = language_name
            self._users_dict[str(self._active_user_id)]["language_id"] = self._stt.get_language_id(language_name)
        else:
            UTILS.TerminalUtility.WarningMessage("Language with name #1 does not exist.", [language_name], exception_raised=True)
            raise ValueError("Language does not exist.")

    @property
    def settings_path(self) -> str:
        return self._users_dict[str(self._active_user_id)]["settings_path"]
    
    @settings_path.setter
    def settings_path(self, new_setting_file_path: str):
        self._users_dict[str(self._active_user_id)]["settings_path"] = new_setting_file_path

    @property
    def db_path(self) ->str:
        return self._users_dict[str(self._active_user_id)]["db_path"]
    
    @db_path.setter
    def db_path(self, new_database_file_path: str):
        self._users_dict[str(self._active_user_id)]["db_path"] = new_database_file_path

    @property
    def db_type(self) ->str:
        return self._users_dict[str(self._active_user_id)]["db_type"]
    
    @db_type.setter
    def db_type(self, new_database_type: str):
        self._users_dict[str(self._active_user_id)]["db_type"] = new_database_type

    @property
    def db_username(self) ->str:
        return self._users_dict[str(self._active_user_id)]["db_username"]
    
    @db_username.setter
    def db_username(self, new_database_username: str):
        password = self.db_password
        self._users_dict[str(self._active_user_id)]["db_username"] = new_database_username
        self.db_password = password

    @property
    def db_password(self) ->str:
        return self._decrypt_password(self._users_dict[str(self._active_user_id)]["db_password"], self.db_username)
    
    @db_password.setter
    def db_password(self, new_database_password: str):
        self._users_dict[str(self._active_user_id)]["db_password"] = self._encrypt_password(new_database_password, self.db_username)

    @property
    def firstname(self) ->str:
        return self._users_dict[str(self._active_user_id)]["firstname"]
    
    @firstname.setter
    def firstname(self, new_firstname: str):
        self._users_dict[str(self._active_user_id)]["firstname"] = new_firstname

    @property
    def lastname(self) ->str:
        return self._users_dict[str(self._active_user_id)]["lastname"]
    
    @lastname.setter
    def lastname(self, new_lastname: str):
        self._users_dict[str(self._active_user_id)]["lastname"] = new_lastname

    @property
    def nickname(self) ->str:
        return self._users_dict[str(self._active_user_id)]["nickname"]
    
    @nickname.setter
    def nickname(self, new_nickname: str):
        self._users_dict[str(self._active_user_id)]["nickname"] = new_nickname

    @property
    def gender(self) ->str:
        return self._users_dict[str(self._active_user_id)]["gender"]
    
    @gender.setter
    def gender(self, new_gender: str):
        self._users_dict[str(self._active_user_id)]["gender"] = new_gender

    @property
    def phone(self) ->str:
        return self._users_dict[str(self._active_user_id)]["phone"]
    
    @phone.setter
    def phone(self, new_phone: str):
        self._users_dict[str(self._active_user_id)]["phone"] = new_phone

    @property
    def email(self) ->str:
        return self._users_dict[str(self._active_user_id)]["email"]
    
    @email.setter
    def email(self, new_email: str):
        self._users_dict[str(self._active_user_id)]["email"] = new_email

    @property
    def address(self) ->str:
        return self._users_dict[str(self._active_user_id)]["address"]
    
    @address.setter
    def address(self, new_address: str):
        self._users_dict[str(self._active_user_id)]["address"] = new_address

    @property
    def description(self) ->str:
        return self._users_dict[str(self._active_user_id)]["description"]
    
    @description.setter
    def description(self, new_description: str):
        self._users_dict[str(self._active_user_id)]["description"] = new_description

    @property
    def created_at(self) ->str:
        return self._users_dict[str(self._active_user_id)]["created_at"]


