from typing import Any, Union

from db_media_cls import Files as FilesDB
import UTILS
from obj_constants import *
from obj_file import File
import settings_cls


class Files:
    def __init__(self, settings: settings_cls.Settings, auto_load_data: bool = True, feedback_percent_function: callable = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Variables
        if feedback_percent_function and isinstance(feedback_percent_function, tuple):
            self._feedback_percent_function = feedback_percent_function[0]
            self._feedback_percent_function_steps = feedback_percent_function[1]
        else:
            self._feedback_percent_function = feedback_percent_function
            self._feedback_percent_function_steps = PERCENT_FEEDBACK_STEP

        self._db_file = FilesDB(self._stt)
        self._data_dict = {}

        if auto_load_data:
            self.refresh()

    def refresh(self):
        self._data_dict = self._load_data()

    def get_file_list(self, file_id_s: Union[list, int, str, File, None]) -> list[File]:
        """
        Creates list of File objects from input variable file_id_s

        :param:
            file_id_s: FileID or list of FileIDs (if None, returns all items)
        :returns:
            List of File objects
        """
        
        if file_id_s is None:
            return [x for x in self._data_dict.values()]

        if not file_id_s:
            return []

        file_id_s = self.convert_ids_to_integer(file_id_s)

        if file_id_s is None:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. FileID list cannot be converted to integers.\nFunction #3 returned #4.", ["Files", "get_file_list", "convert_ids_to_integer", "None"], exception_raised=True)
            raise TypeError("Unable to convert FileID list to integers")

        try:
            return [self._data_dict[str(x)] for x in file_id_s]
        except KeyError:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. FileID does not exist.\ntype(file_id_s) = #3\nfile_id_s = #4", ["Files", "get_file_list", type(file_id_s), file_id_s], exception_raised=True)
            raise ValueError("FileID does not exist.")

    def convert_ids_to_integer(self, obj: Union[File, list, str]) -> Union[list[int], None]:
        """
        Trying to convert values into integers. Does not checks if ID is valid.
        Param:
            Object like string, list or File
        Returns:
            list of integers
            if integer cannot be determined returns None 
        """
       
        if isinstance(obj, int):
            return [obj]

        if isinstance(obj, File):
            return [obj.FileID]

        if isinstance(obj, str):
            if UTILS.TextUtility.is_integer_possible(obj):
                return [UTILS.TextUtility.get_integer(obj)]
            else:
                return None
        
        if isinstance(obj, (tuple, set)):
            obj = list(obj)
        
        if not isinstance(obj, list):
            return None
        
        result = []
        for item in obj:
            if isinstance(item, File):
                item = item.FileID

            if isinstance(item, str):
                if UTILS.TextUtility.is_integer_possible(item):
                    item = UTILS.TextUtility.get_integer(item)
                else:
                    return None
            
            if not isinstance(item, int):
                return None
            
            result.append(item)

        return result

    def _load_data(self) -> dict:
        raw_data = self.get_files_raw_data()
        
        result = {}
        for idx, file in enumerate(raw_data):
            if idx % int(len(raw_data) / self._feedback_percent_function_steps) == 0:
                if self._feedback_percent_function:
                    self._feedback_percent_function(int((idx + 1) / len(raw_data) * 100))

            file_dict = {
                FILE_INDEX_ID[1]: file[0],
                FILE_INDEX_NAME[1]: file[1],
                FILE_INDEX_DESC[1]: file[2],
                FILE_INDEX_FILE[1]: file[3],
                FILE_INDEX_HTTP[1]: file[4],
                FILE_INDEX_IS_DEFAULT[1]: file[5]
            }

            file_obj = File(self._stt)
            if file_obj.load_file_from_dict(file_dict=file_dict):
                result[str(file_obj.FileID)] = file_obj
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Adding files failed.", ["Files", "_load_data"])
                raise ValueError("Adding files in 'Files' class failed.")
        
        return result

    def get_files_raw_data(self) -> list:
        """
        Returns a list of all files.
        Returns (list):
            [0] (int): File ID
            [1] (str): File name
            [2] (str): File description
            [3] (str): File file path
            [4] (str): File source (HTTP)
            [5] (str): File is_default (if greater than 99 it is file, else is image)
        """

        file_list = self._db_file.get_all_file()
        return file_list

    def signal_file_added(self, obj: File):
        if self._data_dict.get(str(obj.FileID), None):
            UTILS.LogHandler.add_log_record("#1: File (ID=#2) already exists in Files class. Function: #3.", ["Files", obj.FileID, "signal_file_added"])

        self._data_dict[str(obj.FileID)] = obj

    def signal_file_saved(self, obj: File):
        if self._data_dict.get(str(obj.ImageID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Saved file (ID=#2) not found in Files class. Function: #3.", ["Files", obj.ImageID, "signal_file_saved"], exception_raised=True)
            raise ValueError(f"Saved file (ID={obj.ImageID}) not found in Files class.")

        self._data_dict[str(obj.FileID)] = obj

    def signal_file_deleted(self, obj: File):
        if self._data_dict.get(str(obj.ImageID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Deleted file (ID=#2) not found in Files class. Function: #3.", ["Files", obj.ImageID, "signal_file_deleted"], exception_raised=True)
            raise ValueError(f"Deleted file (ID={obj.ImageID}) not found in Files class.")
        
        self._data_dict.pop(str(obj.FileID), None)




