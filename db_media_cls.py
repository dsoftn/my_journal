import os
import shutil

import database_cls
import settings_cls
import UTILS


class Media():
    """
    media_dict:
        name (str): Def=""
        description (str): Def=""
        file (str): Def=""
        http (str): Def=""
        default (str): Def=0
    """

    def __init__(self, settings: settings_cls.Settings, media_id: int = None) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.db_info = self._stt.app_setting_get_value("db_info")
        self._active_media_id = media_id

        if self._active_media_id:
            self._populate_properties()

    def is_safe_to_delete(self, media_id: int) -> bool:
        q_def = f"SELECT id FROM def_data WHERE media_id = {media_id} ;"
        q_rec = f"SELECT id FROM data WHERE media_id = {media_id} ;"
        
        with database_cls.DataBase(self.db_info) as db:
            q_def_result = db.execute(q_def)
            q_rec_result = db.execute(q_rec)
        
        if q_def_result:
            return False
        if q_rec_result:
            return False
        
        return True

    def delete_media(self, media_id: int = None) -> int | None:
        if media_id is None:
            media_id = self._active_media_id
        if media_id is None:
            return None
        
        if not self.is_safe_to_delete(media_id):
            UTILS.TerminalUtility.WarningMessage("Media cannot be deleted.\nFunction self.is_safe_to_delete(media_id) returned #1.\nmedia_id = #2", ["False", media_id], exception_raised=True)
            raise ValueError("Media cannot be deleted.")
        
        self._populate_properties(media_id)

        q = f"DELETE FROM media WHERE id = {media_id} AND is_default < 99 ;"

        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, commit=True)

        UTILS.LogHandler.add_log_record("#1: Image deleted. (ID=#2)", ["Media", media_id])
        
        file_path = os.path.abspath(self._file)
        destination = self.getv("temp_folder_path") + os.path.split(file_path)[1]
        if os.path.isfile(file_path):
            if self.getv("when_deleting_copy_images_to_temp_folder"):
                if not os.path.isfile(destination):
                    shutil.copy(file_path, destination)
                    UTILS.LogHandler.add_log_record("#1: Image backup copied to #2. (ID=#3)\nCopy from: #4\nto #5", ["Media", "Temp folder", media_id, file_path, destination])
            os.remove(file_path)

        return result

    def _populate_properties(self, media_id: int = None) -> list:
        if not media_id:
            media_id = self._active_media_id
        if not media_id:
            UTILS.TerminalUtility.WarningMessage("Media ID is not defined !\nmedia_id = #1", [media_id], exception_raised=True)
            raise ValueError("Media ID is not defined !")

        q = f"SELECT * FROM media WHERE id = {media_id} AND is_default < 99 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)

        self._active_media_id = result[0][0]
        self._name = result[0][1]
        self._description = result[0][2]
        self._file = result[0][3]
        self._http = result[0][4]
        self._default = result[0][5]

        return result

    def get_media(self, media_id: int) -> list:
        result = self._populate_properties(media_id=media_id)
        return result

    def load_media(self, media_id: int) -> bool:
        if self.is_media_exist(media_id=media_id):
            result = self._populate_properties(media_id=media_id)
            return result
        else:
            return None

    def is_media_exist(self, media_id: int) -> bool:
        q = f"SELECT * FROM media WHERE id = {media_id} AND is_default < 99 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        if result:
            return True
        else:
            return False

    def check_is_all_ids_images(self, media_ids: list) -> list:
        image_ids = self.get_all_media()
        image_ids = [x[0] for x in image_ids]
        result = [x for x in media_ids if x in image_ids]
        return result

    def update_media(self, media_id: int, media_dict: dict) -> int:
        if media_id != self._active_media_id:
            self._populate_properties(media_id)
        
        if "name" in media_dict:
            self._name = media_dict["name"]
        if "description" in media_dict:
            self._description = media_dict["description"]
        if "file" in media_dict:
            self._file = media_dict["file"]
        if "http" in media_dict:
            self._http = media_dict["http"]
        if "default" in media_dict:
            self._default = media_dict["default"]

        q = f"""
            UPDATE media
            SET 
                name = ?,
                description = ?,
                file = ?,
                http = ?,
                is_default = {self._default}
            WHERE id = {media_id} ;
            """
        param = (self._name, self._description, self._file, self._http)
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, param=param, commit=True)
        
        self._populate_properties(result)
        UTILS.LogHandler.add_log_record("#1: Image Updated. (ID=#2)", ["Media", media_id], variables=[["Name", self._name], ["Description", self._description], ["File_path", self._file], ["Source", self._http]])
        self.get_appv("log").write_log(f"Media. Media updated. Media ID: {self._active_media_id}")
        return result
    
    def add_media(self, media_dict: dict, add_if_not_exist: bool = True) -> int:
        """ Returns ID for new media
        media_dict:
            name (str): Def=""
            description (str): Def=""
            file (str): Def=""
            http (str): Def=""
            default (str): Def=0
        """
        if "name" in media_dict:
            self._name = media_dict["name"]
        else:
            self._name = ""
        if "description" in media_dict:
            self._description = media_dict["description"]
        else:
            self._description = ""
        if "file" in media_dict:
            self._file = media_dict["file"]
        else:
            self._file = ""
        if "http" in media_dict:
            self._http = media_dict["http"]
        else:
            self._http = ""
        if "default" in media_dict:
            self._default = media_dict["default"]
        else:
            self._default = 0

        # Check if image exist
        if add_if_not_exist:
            result = self.get_all_media()
            media_exist = None
            for i in result:
                if (i[3] == self._file and i[3] != "") or (i[4] == self._http and i[4] != ""):
                    media_exist = i[0]
            if media_exist:
                self._populate_properties(media_exist)
                UTILS.LogHandler.add_log_record("#1: New image not added. Image already exist. (ID=#2)", ["Media", media_exist], variables=[["Name", self._name], ["Description", self._description], ["File_path", self._file], ["Source", self._http]])
                return media_exist

        # Add new media
        q = f"""
            INSERT INTO 
                media(name, description, file, http, is_default)
            VALUES
                (?, ?, ?, ?, {self._default})
            ;
        """
        param = (self._name, self._description, self._file, self._http)
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, param=param, commit=True)

        self._populate_properties(result)
        UTILS.LogHandler.add_log_record("#1: New image added. (ID=#2)", ["Media", result], variables=[["Name", self._name], ["Description", self._description], ["File_path", self._file], ["Source", self._http]])
        self.get_appv("log").write_log(f"Media. New media added. Media ID: {self._active_media_id}")
        return result

    def get_block_ids_that_use_media(self, media_id: int = None) -> list:
        if media_id is None:
            media_id = self._active_media_id
        
        q = f"SELECT record_id FROM data WHERE media_id = {media_id} GROUP BY record_id ORDER BY record_id ;"
        
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        block_ids = [x[0] for x in result]

        return block_ids

    def get_definition_ids_that_use_media(self, media_id: int = None) -> list:
        if media_id is None:
            media_id = self._active_media_id
        
        q = f"SELECT definition_id FROM def_data WHERE media_id = {media_id} GROUP BY definition_id ORDER BY definition_id ;"
        
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        def_ids = [x[0] for x in result]

        return def_ids

    def get_all_media(self) -> list:
        q = "SELECT * FROM media WHERE is_default < 99 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    @property
    def media_id(self) -> int:
        return self._active_media_id
    
    @property
    def media_name(self) -> str:
        return self._name
    
    @property
    def media_description(self) -> str:
        return self._description

    @property
    def media_file(self) -> str:
        return self._file

    @property
    def media_http(self) -> str:
        return self._http

    @property
    def media_default(self) -> int:
        return self._default


class Files():
    """
    files_dict:
        name (str): Def=""
        description (str): Def=""
        file (str): Def=""
        http (str): Def=""
        default (str): Def=100
    """

    def __init__(self, settings: settings_cls.Settings, file_id: int = None) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.db_info = self._stt.app_setting_get_value("db_info")
        self._active_file_id = file_id

        if self._active_file_id:
            self._populate_properties()

    def is_safe_to_delete(self, file_id: int) -> bool:
        q_def = f"SELECT id FROM def_data WHERE media_id = {file_id} ;"
        q_rec = f"SELECT id FROM data WHERE media_id = {file_id} ;"
        
        with database_cls.DataBase(self.db_info) as db:
            q_def_result = db.execute(q_def)
            q_rec_result = db.execute(q_rec)
        
        if q_def_result:
            return False
        if q_rec_result:
            return False
        
        return True

    def delete_file(self, file_id: int = None) -> int:
        if file_id is None:
            file_id = self._active_file_id
        if file_id is None:
            return None
        
        if not self.is_safe_to_delete(file_id):
            UTILS.TerminalUtility.WarningMessage("File in use cannot be deleted.\nFunction self.is_safe_to_delete() returned #1.\nfile_id = #2\nself._active_file_id = #3", ["False", file_id, self._active_file_id], exception_raised=True)
            raise ValueError("File in use cannot be deleted.")

        self._populate_properties(file_id)

        q = f"DELETE FROM media WHERE id = {file_id} AND is_default > 99 ;"

        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, commit=True)

        UTILS.LogHandler.add_log_record("#1: File deleted. (ID=#2)", ["Files", file_id])

        file_path = os.path.abspath(self._file)
        destination = self.getv("temp_folder_path") + os.path.split(file_path)[1]
        if os.path.isfile(file_path):
            if self.getv("when_deleting_copy_files_to_temp_folder"):
                if not os.path.isfile(destination):
                    shutil.copy(file_path, destination)
                    UTILS.LogHandler.add_log_record("#1: File backup copied to #2. (ID=#3)\nCopy from: #4\nto #5", ["Files", "Temp folder", file_id, file_path, destination])
            os.remove(file_path)

        return result

    def _populate_properties(self, file_id: int = None) -> list:
        if not file_id:
            file_id = self._active_file_id
        if not file_id:
            UTILS.TerminalUtility.WarningMessage("Media ID is not defined !\nfile_id = #1", [file_id], exception_raised=True)
            raise ValueError("Media ID is not defined !")

        q = f"SELECT * FROM media WHERE id = {file_id} AND is_default > 99 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)

        self._active_file_id = result[0][0]
        self._name = result[0][1]
        self._description = result[0][2]
        self._file = result[0][3]
        self._http = result[0][4]
        self._default = result[0][5]

        return result

    def get_file(self, file_id: int) -> list:
        result = self._populate_properties(file_id=file_id)
        return result

    def load_file(self, file_id: int) -> bool:
        if self.is_file_exist(file_id=file_id):
            result = self._populate_properties(file_id=file_id)
            return result
        else:
            return None

    def is_file_exist(self, file_id: int) -> bool:
        q = f"SELECT * FROM media WHERE id = {file_id} AND is_default > 99 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        if result:
            return True
        else:
            return False

    def update_file(self, file_id: int, file_dict: dict) -> int:
        if file_id != self._active_file_id:
            self._populate_properties(file_id)
        
        if "name" in file_dict:
            self._name = file_dict["name"]
        if "description" in file_dict:
            self._description = file_dict["description"]
        if "file" in file_dict:
            self._file = file_dict["file"]
        if "http" in file_dict:
            self._http = file_dict["http"]
        if "default" in file_dict:
            self._default = file_dict["default"]

        q = f"""
            UPDATE media
            SET 
                name = ?,
                description = ?,
                file = ?,
                http = ?,
                is_default = {self._default}
            WHERE id = {file_id} ;
            """
        param = (self._name, self._description, self._file, self._http)
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, param=param, commit=True)
        
        self._populate_properties(result)
        UTILS.LogHandler.add_log_record("#1: File Updated. (ID=#2)", ["Files", file_id], variables=[["Name", self._name], ["Description", self._description], ["File_path", self._file], ["Source", self._http]])
        return result
    
    def add_file(self, file_dict: dict, add_if_not_exist: bool = True) -> int:
        """ Returns ID for new file
        file_dict:
            name (str): Def=""
            description (str): Def=""
            file (str): Def=""
            http (str): Def=""
            default (str): Def=100
        """
        if "name" in file_dict:
            self._name = file_dict["name"]
        else:
            self._name = ""
        if "description" in file_dict:
            self._description = file_dict["description"]
        else:
            self._description = ""
        if "file" in file_dict:
            self._file = file_dict["file"]
        else:
            self._file = ""
        if "http" in file_dict:
            self._http = file_dict["http"]
        else:
            self._http = ""
        if "default" in file_dict:
            self._default = file_dict["default"]
        else:
            self._default = 100

        # Check if file exist
        if add_if_not_exist:
            result = self.get_all_file()
            file_exist = None
            for i in result:
                if (i[3] == self._file and i[3] != "") or (i[4] == self._http and i[4] != ""):
                    file_exist = i[0]
            if file_exist:
                self._populate_properties(file_exist)
                UTILS.LogHandler.add_log_record("#1: New file not added. FIle already exist. (ID=#2)", ["Files", file_exist], variables=[["Name", self._name], ["Description", self._description], ["File_path", self._file], ["Source", self._http]])
                return file_exist

        # Add new file
        q = f"""
            INSERT INTO 
                media(name, description, file, http, is_default)
            VALUES
                (?, ?, ?, ?, {self._default})
            ;
        """
        param = (self._name, self._description, self._file, self._http)
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, param=param, commit=True)

        self._populate_properties(result)
        UTILS.LogHandler.add_log_record("#1: New file added. (ID=#2)", ["Files", result], variables=[["Name", self._name], ["Description", self._description], ["File_path", self._file], ["Source", self._http]])
        return result

    def get_block_ids_that_use_file(self, file_id: int = None) -> list:
        if file_id is None:
            file_id = self._active_file_id
        
        q = f"SELECT record_id FROM data WHERE media_id = {file_id} GROUP BY record_id ORDER BY record_id ;"
        
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        block_ids = [x[0] for x in result]

        return block_ids

    def get_all_file(self) -> list:
        q = "SELECT * FROM media WHERE is_default > 99 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    @property
    def file_id(self) -> int:
        return self._active_file_id
    
    @property
    def file_name(self) -> str:
        return self._name
    
    @property
    def file_description(self) -> str:
        return self._description

    @property
    def file_file(self) -> str:
        return self._file

    @property
    def file_http(self) -> str:
        return self._http

    @property
    def file_default(self) -> int:
        return self._default
