import database_cls
import settings_cls
import UTILS


class Tag():
    """
    tag_dict = {}
        name (str):
        user_def (int):
        description (str):
        name_transl (str):
        description_transl (str):
    """
    
    def __init__(self, settings: settings_cls.Settings, tag_id: int = 0):
        self._stt = settings
        self.get_appv = self._stt.app_setting_get_value

        self.db_info = self._stt.app_setting_get_value("db_info")
        self.log = self._stt.app_setting_get_value("log")
        self._active_tag_id = tag_id
        if self._active_tag_id:
            self.populate_values()

    def get_tag_name_cleaned(self, tag_id: int = 0) -> str:
        if tag_id == 0:
            tag_id = self._active_tag_id
        with database_cls.DataBase(self.db_info) as db:
            q = f"SELECT name_transl FROM tag WHERE id = {tag_id} ;"
            result = db.execute(q)
        result = result[0][0].strip("{").strip("}")
        return result

    def get_all_tags(self, tag_id: int = 0) -> list:
        with database_cls.DataBase(self.db_info) as db:
            if tag_id != 0:
                q = f"SELECT * FROM tag WHERE id = {tag_id} ;"
            else:
                q = "SELECT * FROM tag ;"
            result = db.execute(q)
        return result

    def is_valid_tag_id(self, tag_id: int) -> bool:
        if not isinstance(tag_id, int):
            return False
        q = f"SELECT id FROM tag WHERE id = {tag_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        if result:
            return True
        else:
            return False
    
    def add_new_tag(self, tag_dict: dict) -> int:
        """
        tag_dict = {}
            name (str):
            user_def (int):
            description (str):
            name_transl (str):
            description_transl (str):
        """
        if self.is_valid_tag_name(tag_dict["name"]) is not None:
            UTILS.TerminalUtility.WarningMessage("Tag name already exist.\ntag_dict[name]: #1", [tag_dict.get("name")], exception_raised=True)
            raise ValueError("Tag name already exist.")
        
        if "user_def" not in tag_dict:
            tag_dict["user_def"] = 1
        if "description" not in tag_dict:
            tag_dict["description"] = ""
        if "name_transl" not in tag_dict:
            tag_dict["name_transl"] = ""
        if "description_transl" not in tag_dict:
            tag_dict["description_transl"] = ""

        q = f'INSERT INTO tag(name, user_def, description, name_transl, description_transl) VALUES (?, {tag_dict["user_def"]}, ?, ?, ?) ;'
        param = (tag_dict["name"], tag_dict["description"], tag_dict["name_transl"], tag_dict["description_transl"])

        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, param=param, commit=True)
        
        UTILS.LogHandler.add_log_record("#1: New tag added. (ID=#2)", ["Tag", result], variables=[["tag_dict[name]", tag_dict.get("name")], ["tag_dict[description]", tag_dict.get("description")], ["tag_dict[user_def]", tag_dict.get("user_def")], ["tag_dict[name_transl]", tag_dict.get("name_transl")], ["tag_dict[description_transl]", tag_dict.get("description_transl")]])
        self.log.write_log(f"DB Tag. Tag added. Tag ID: {result}")
        return result

    def delete_tag(self, tag_id: int) -> int:
        if not self.is_valid_tag_id(tag_id):
            UTILS.TerminalUtility.WarningMessage("Tag ID does not exist.\ntag_id: #1", [tag_id], exception_raised=True)
            raise ValueError("Tag ID does not exist.")
        q = f"DELETE FROM tag WHERE id = {tag_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, commit=True)

        UTILS.LogHandler.add_log_record("#1: Tag deleted. (ID=#2)", ["Tag", result])

        self.log.write_log(f"DB Tag. Tag deleted. Tag ID: {tag_id}")
        
        return result

    def update_tag(self, tag_id: int, tag_dict: dict) -> int:
        """
        tag_dict = {}
            name (str):
            user_def (int):
            description (str):
            name_transl (str):
            description_transl (str):
        """
        if not self.is_valid_tag_id(tag_id):
            UTILS.TerminalUtility.WarningMessage("Tag ID does not exist.\ntag_id: #1", [tag_id], exception_raised=True)
            raise ValueError("Tag ID does not exist.")
        if self.is_valid_tag_name(tag_dict["name"]) is None:
            UTILS.TerminalUtility.WarningMessage("Tag name does not exist.\ntag_dict[name]: #1", [tag_dict.get("name")], exception_raised=True)
            raise ValueError("Tag name does not exist.")
        if not tag_dict["name"]:
            UTILS.TerminalUtility.WarningMessage("Tag name not defined.\ntag_dict[name]: #1", [tag_dict.get("name")], exception_raised=True)
            raise ValueError("Tag name not defined.")

        if "user_def" not in tag_dict:
            tag_dict["user_def"] = 1
        if "description" not in tag_dict:
            tag_dict["description"] = ""
        if "name_transl" not in tag_dict:
            tag_dict["name_transl"] = ""
        if "description_transl" not in tag_dict:
            tag_dict["description_transl"] = ""

        q = f'UPDATE tag SET name = ?, user_def = {tag_dict["user_def"]}, description = ?, name_transl = ?, description_transl = ? WHERE id = {tag_id} ;'
        param = (tag_dict["name"], tag_dict["description"], tag_dict["name_transl"], tag_dict["description_transl"])

        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, param=param, commit=True)

        UTILS.LogHandler.add_log_record("#1: New tag added. (ID=#2)", ["Tag", tag_id], variables=[["tag_dict[name]", tag_dict.get("name")], ["tag_dict[description]", tag_dict.get("description")], ["tag_dict[user_def]", tag_dict.get("user_def")], ["tag_dict[name_transl]", tag_dict.get("name_transl")], ["tag_dict[description_transl]", tag_dict.get("description_transl")]])
        
        self.log.write_log(f"DB Tag. Tag updated. Tag ID: {tag_id}")
        return result

    def is_valid_tag_name(self, tag_name: str) -> int:
        tags = self.get_all_tags_translated()
        for tag in tags:
            if tag[1] == tag_name:
                return tag[0]
        return None

    def how_many_times_is_used(self, tag_id: int = None) -> int:
        if tag_id is None:
            tag_id = self._active_tag_id
        if tag_id is None:
            UTILS.TerminalUtility.WarningMessage("Missing tag ID !\ntag_id: #1\nself._active_tag_id: #2", [tag_id, self._active_tag_id], exception_raised=True)
            raise ValueError("Missing tag ID !")
        
        q = f"SELECT COUNT(tag_id) FROM data WHERE tag_id = {tag_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result[0][0]

    def get_all_tags_translated(self) -> list:
        with database_cls.DataBase(self.db_info) as db:
            q = "SELECT * FROM tag ;"
            result = db.execute(q)

        tags = []
        for tag in result:
            # Translated tag name
            tag_name_trans = tag[4].strip("{").strip("}")
            if tag_name_trans:
                tag_name_trans = self._stt.lang(tag_name_trans)
            else:
                tag_name_trans = tag[1]
            # Translated tag description
            tag_description_trans = tag[5].strip("{").strip("}")
            if tag_description_trans:
                tag_description_trans = self._stt.lang(tag_description_trans)
            else:
                tag_description_trans = tag[3]
            
            # Add to tags list
            tags.append([tag[0], tag_name_trans, tag[2], tag_description_trans])
        return tags

    def populate_values(self, tag_id: int = 0) -> None:
        if tag_id:
            self._active_tag_id = tag_id
        else:
            tag_id = self._active_tag_id
        if self._active_tag_id == 0:
            self.log.write_log("Error: Tag_ID not found. Module: tag_cls, Class: Tag, Method: populate_values")
            UTILS.TerminalUtility.WarningMessage("Error: Tag_ID not found.\ntag_id: #1\nself._active_tag_id: #2", [tag_id, self._active_tag_id], exception_raised=True)
            raise ValueError("Error: Tag_ID not found. Module: tag_cls, Class: Tag, Method: populate_values")
        tag = self.get_all_tags(self._active_tag_id)[0]
        self._tag_name = tag[1]
        self._tag_user_def = tag[2]
        self._tag_description = tag[3]
        # Translated tag name
        self._tag_name_trans = tag[4].strip("{").strip("}")
        if self._tag_name_trans:
            self._tag_name_trans = self._stt.lang(self._tag_name_trans)
        else:
            self._tag_name_trans = self._tag_name
        # Translated tag description
        self._tag_description_trans = tag[5].strip("{").strip("}")
        if self._tag_description_trans:
            self._tag_description_trans = self._stt.lang(self._tag_description_trans)
        else:
            self._tag_description_trans = self._tag_description
        self.log.write_log(f"DB Tag. Tag loaded. Tag ID: {self._active_tag_id}")

    @property
    def TagName(self):
        return self._tag_name

    @property
    def TagNameTranslated(self):
        return self._tag_name_trans
    
    @property
    def TagUserDefinded(self):
        return self._tag_user_def

    @property
    def TagDescription(self):
        return self._tag_description

    @property
    def TagDescriptionTranslated(self):
        return self._tag_description_trans

    @property
    def TagID(self):
        return self._active_tag_id
