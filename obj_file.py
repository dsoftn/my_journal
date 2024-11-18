from typing import Any, Union

from db_media_cls import Files as FilesDB
from obj_constants import *
import UTILS
from utils_file import FileInformation
import settings_cls


class File:
    """
    File object that contain user added file.
    """
    def __init__(self, settings: settings_cls.Settings, file_id: Union[int, str, 'File'] = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Variables
        self.data = self.get_empty_file_dict()
        self._db_file = FilesDB(self._stt)

        if file_id is not None:
            self.load_file(file_id)

    def load_file(self, file_id: Union[int, str, 'File']) -> bool:
        """
        Populates File object properties that match file_id passed.
        """
        if isinstance(file_id, str):
            file_id = UTILS.TextUtility.get_integer(file_id)
        if isinstance(file_id, File):
            file_id = file_id.FileID
        if not self._db_file.is_file_exist(file_id=file_id):
            UTILS.LogHandler.add_log_record("#1: File ID (#2) passed to method #3 does not exist!", ["File", file_id, "load_file"], warning_raised=True)
            return False

        self.data = self.get_empty_file_dict()
        self._db_file.load_file(file_id=file_id)

        self.data[FILE_INDEX_ID[1]] = self._db_file.file_id
        self.data[FILE_INDEX_NAME[1]] = self._db_file.file_name
        self.data[FILE_INDEX_DESC[1]] = self._db_file.file_description
        self.data[FILE_INDEX_FILE[1]] = FileInformation(self._db_file.file_file)
        self.data[FILE_INDEX_HTTP[1]] = self._db_file.file_http
        self.data[FILE_INDEX_IS_DEFAULT[1]] = self._db_file.file_default
        
        return True

    def new(self):
        """
        Clears all File object properties
        """
        self.data = self.get_empty_file_dict()

    def add_to_file_list(self) -> int | None:
        """
        Add new file to Files list.
        If file is successfully added returns file ID, else None
        """

        if self.data[FILE_INDEX_ID[1]] is None:
            UTILS.LogHandler.add_log_record("#1: Unable to add file. Reason: #2", ["File", "No file loaded"], warning_raised=True)
            return None

        if not self.FileFile.is_file():
            UTILS.LogHandler.add_log_record("#1: Unable to add file. Reason: #2", ["File", "File does not exist"], warning_raised=True)
            return None
        
        file_id = self.FileID
        
        self.get_appv("files").signal_file_added(self)
        UTILS.Signal.emit_file_added(self.to_dict())
        return file_id

    def can_be_added(self) -> bool:
        """
        Checks if file can be added to database.
        """

        if self.data[FILE_INDEX_ID[1]] is None:
            return False

        if not self.FileFile.is_file():
            return False

        return True

    def save(self) -> bool:
        """
        Save/Update file.
        File object must have valid ID and valid FileFile property.
        """

        if not self._db_file.is_file_exist(self.FileID):
            UTILS.LogHandler.add_log_record("#1: Unable to save file. File with ID #2 does not exist.", ["File", self.FileID], warning_raised=True)
            return False

        if not self.FileFile.is_file():
            UTILS.LogHandler.add_log_record("#1: Unable to save file. Filepath #2 is not valid path.", ["File", self.FileFile], warning_raised=True)
            return False
        
        file_dict = {
            "name": self.FileName,
            "description": self.FileDescription,
            "file": self.FileFile.file_path,
            "http": self.FileHTTP,
            "default": self.FileIsDefault
        }
        file_id = self._db_file.update_file(file_id=self.FileID, file_dict=file_dict)
        if not file_id:
            UTILS.LogHandler.add_log_record("#1: Unable to save file. Reason: #2", ["File", "Error occurred in db_media_cls->Files->update_file"], warning_raised=True, extract_to_variables=file_dict)
            return False
        
        self.data[SAVED_FLAG] = True
        self.get_appv("files").signal_file_saved(self)
        UTILS.Signal.emit_file_saved(self.to_dict())
        return True

    def can_be_saved(self) -> bool:
        """
        Checks if file can be Saved/Updated.
        """

        if not self._db_file.is_file_exist(self.FileID):
            return False

        if not self.FileFile.is_file():
            return False
        
        return True

    def delete(self) -> int | None:
        """
        Deletes file.
        File object must have valid ID and not being used in any block or definition.
        """

        if not self._db_file.is_file_exist(self.FileID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete file. File with ID #2 does not exist.", ["File", self.FileID], warning_raised=True)
            return None
        
        if not self._db_file.is_safe_to_delete(self.FileID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete file. File is used in some blocks.", ["File"], warning_raised=True)
            return None

        result = self._db_file.delete_file(self.FileID)
        if not result:
            UTILS.LogHandler.add_log_record("#1: Unable to delete file. Reason: #2", ["File", "Error occurred in db_media_cls->Files->delete_file"], warning_raised=True)
            return None
        
        self.data[SAVED_FLAG] = None
        self.get_appv("files").signal_file_deleted(self)
        UTILS.Signal.emit_file_deleted(self.to_dict())
        return result

    def can_be_deleted(self) -> bool:
        """
        Checks if file can be deleted.
        """

        if not self._db_file.is_file_exist(self.FileID):
            return False
        
        if not self._db_file.is_safe_to_delete(self.FileID):
            return False

        return True

    def is_exist_FileID(self, file_id: int = None) -> bool:
        if file_id is None:
            file_id = self.FileID
        return self._db_file.is_file_exist(file_id)
    
    def is_FileFile_path_valid(self):
        return self.FileFile.is_file()

    def load_file_from_dict(self, file_dict: dict) -> bool:
        required_fields = [
            FILE_INDEX_ID[1],
            FILE_INDEX_NAME[1],
            FILE_INDEX_DESC[1],
            FILE_INDEX_FILE[1],
            FILE_INDEX_HTTP[1]
        ]

        if any(x not in file_dict.keys() for x in required_fields):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. File dictionary is incomplete.\nRequired fields: #3\nfile_dict fields: #4", ["File", "load_file_from_dict", required_fields, file_dict.keys()], exception_raised=True)
            raise ValueError("File dictionary does not contain all required keys.")

        if file_dict.get(FILE_INDEX_IS_DEFAULT[1], 100) < 100:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. FileDefault value must be greater than 99. passed #3", ["File", "load_file_from_dict", file_dict.get(FILE_INDEX_IS_DEFAULT[1], 100)], exception_raised=True)
            raise ValueError("FileDefault must be greater than 99.")

        self.data = self.get_empty_file_dict()
        self.data[FILE_INDEX_ID[1]] = file_dict[FILE_INDEX_ID[1]]
        self.data[FILE_INDEX_NAME[1]] = file_dict[FILE_INDEX_NAME[1]]
        self.data[FILE_INDEX_DESC[1]] = file_dict[FILE_INDEX_DESC[1]]
        self.data[FILE_INDEX_FILE[1]] = FileInformation(file_dict[FILE_INDEX_FILE[1]])
        self.data[FILE_INDEX_HTTP[1]] = file_dict[FILE_INDEX_HTTP[1]]
        self.data[FILE_INDEX_IS_DEFAULT[1]] = file_dict.get(FILE_INDEX_IS_DEFAULT[1], 100)
        return True

    def to_dict(self) -> dict:
        return self.data

    def to_dict_unpacked(self) -> dict:
        result = dict(self.data)
        result[FILE_INDEX_FILE[1]] = self.FileFile.file_path
        return result

    def get_empty_file_dict(self) -> dict:
        return {
            FILE_INDEX_ID[1]: None,
            FILE_INDEX_NAME[1]: "",
            FILE_INDEX_DESC[1]: "",
            FILE_INDEX_FILE[1]: "",
            FILE_INDEX_HTTP[1]: "",
            FILE_INDEX_IS_DEFAULT[1]: 100,
            SAVED_FLAG: True
        }

    def _object_changed(self):
        self.data[SAVED_FLAG] = False

    def __str__(self) -> str:
        return f"File ID: {self.data[FILE_INDEX_ID[1]]}"

    def __eq__(self, other):
        if isinstance(other, File):
            if (self.data[FILE_INDEX_ID[1]] == other.data[FILE_INDEX_ID[1]]
                and self.data[FILE_INDEX_NAME[1]] == other.data[FILE_INDEX_NAME[1]]
                and self.data[FILE_INDEX_DESC[1]] == other.data[FILE_INDEX_DESC[1]]
                and self.data[FILE_INDEX_FILE[1]] == other.data[FILE_INDEX_FILE[1]]
                and self.data[FILE_INDEX_HTTP[1]] == other.data[FILE_INDEX_HTTP[1]]
                and self.data[FILE_INDEX_IS_DEFAULT[1]] == other.data[FILE_INDEX_IS_DEFAULT[1]]
                ):
                return True
            else:
                return False
        else:
            return False    

    @property
    def FileID(self) -> int:
        return self.data[FILE_INDEX_ID[1]]
    
    @FileID.setter
    def FileID(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. FileID property must be an integer.\ntype(value) = #3\nvalue = #4", ["File", "FileID.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The FileID property must be a integer. Passed '{str(type(value))}', expected 'int'")
        
        if self.data[FILE_INDEX_ID[1]] != value:
            self.data[FILE_INDEX_ID[1]] = value
            self._object_changed()

    @property
    def FileName(self) -> str:
        return self.data[FILE_INDEX_NAME[1]]
    
    @FileName.setter
    def FileName(self, value: str) -> None:
        if self.data[FILE_INDEX_NAME[1]] != str(value):
            self.data[FILE_INDEX_NAME[1]] = str(value)
            self._object_changed()
    
    @property
    def FileDescription(self) -> str:
        return self.data[FILE_INDEX_DESC[1]]
    
    @FileDescription.setter
    def FileDescription(self, value: str) -> None:
        if self.data[FILE_INDEX_DESC[1]] != str(value):
            self.data[FILE_INDEX_DESC[1]] = str(value)
            self._object_changed()
    
    @property
    def FileFile(self) -> FileInformation:
        return self.data[FILE_INDEX_FILE[1]]
    
    @FileFile.setter
    def FileFile(self, value: Union[str, FileInformation]) -> None:
        if not isinstance(value, (str, FileInformation)):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. FileFile property must be a string or FileInformation.\ntype(value) = #3\nvalue = #4", ["File", "FileFile.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The FileFile property must be a string or FileInformation. Passed '{str(type(value))}', expected 'str' or 'FileInformation'")
        
        if self.data[FILE_INDEX_FILE[1]] != FileInformation(value):
            self.data[FILE_INDEX_FILE[1]] = FileInformation(value)
            self._object_changed()
    
    @property
    def FileHTTP(self) -> str:
        return self.data[FILE_INDEX_HTTP[1]]
    
    @FileHTTP.setter
    def FileHTTP(self, value: str) -> None:
        if self.data[FILE_INDEX_HTTP[1]] != str(value):
            self.data[FILE_INDEX_HTTP[1]] = str(value)
            self._object_changed()
    
    @property
    def FileIsDefault(self) -> int:
        return self.data[FILE_INDEX_IS_DEFAULT[1]]
    
    @FileIsDefault.setter
    def FileIsDefault(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. FileIsDefault property must be an integer.\ntype(value) = #3\nvalue = #4", ["File", "FileIsDefault.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The FileIsDefault property must be a integer. Passed '{str(type(value))}', expected 'int'")

        if not value < 100:
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. FileIsDefault property must be in greater than 99.\ntype(value) = #3\nvalue = #4", ["File", "FileIsDefault.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The FileIsDefault property must be greater than 99. Passed '{str(type(value))}'.")
        
        if self.data[FILE_INDEX_IS_DEFAULT[1]] != value:
            self.data[FILE_INDEX_IS_DEFAULT[1]] = value
            self._object_changed()








