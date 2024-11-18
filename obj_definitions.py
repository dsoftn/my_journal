from typing import Any, Union

from db_media_cls import Media as ImageDB
from db_definition_cls import Definition as DefDB
import UTILS
from obj_constants import *
from obj_definition import Definition
import settings_cls


class Definitions:
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

        self._data_dict = {}

        if auto_load_data:
            self.refresh()

    def refresh(self):
        self._data_dict = self._load_data()

    def _load_data(self) -> dict:
        raw_data = self.get_defs_raw_data()
        
        result = {}
        for idx, item in enumerate(raw_data):
            if idx % int(len(raw_data) / self._feedback_percent_function_steps) == 0:
                if self._feedback_percent_function:
                    self._feedback_percent_function(int((idx + 1) / len(raw_data) * 100))

            def_dict = {
                DEF_INDEX_ID[1]: item[0],
                DEF_INDEX_NAME[1]: item[1],
                DEF_INDEX_DESC[1]: item[2],
                DEF_INDEX_EXPRESSIONS[1]: item[3],
                DEF_INDEX_IMAGES[1]: item[4],
                DEF_INDEX_DEFAULT_IMAGE[1]: item[5]
            }

            def_obj = Definition(self._stt)
            if def_obj.load_def_from_dict(def_dict=def_dict):
                result[str(def_obj.DefID)] = def_obj
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Adding definitions failed.", ["Definitions", "_load_data"], exception_raised=True)
                raise ValueError("Adding definitions in 'Definitions' class failed.")
        
        return result

    def get_def_list(self, def_id_s: Union[list, int, str, Definition, None]) -> list[Definition]:
        """
        Creates list of Definition objects from input variable def_id_s

        :param:
            def_id_s: DefinitionID or list of DefinitionIDs (if None, returns all items)
        :returns:
            List of Definition objects
        """

        if def_id_s is None:
            return [x for x in self._data_dict.values()]
        
        if not def_id_s:
            return []
        
        def_id_s = self.convert_ids_to_integer(def_id_s)

        if def_id_s is None:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. DefID list cannot be converted to integers.\nFunction #3 returned #4.", ["Definitions", "get_def_list", "convert_ids_to_integer", "None"], exception_raised=True)
            raise TypeError("Unable to convert DefID list to integers")

        try:
            return [self._data_dict[str(x)] for x in def_id_s]
        except KeyError:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. DefID does not exist.\ntype(def_id_s) = #3\ndef_id_s = #4", ["Definitions", "get_def_list", type(def_id_s), def_id_s], exception_raised=True)
            raise ValueError("DefID does not exist.")

    def convert_ids_to_integer(self, obj: Union[Definition, list, str]) -> Union[list[int], None]:
        """
        Trying to convert values into integers. Does not checks if tag ID is valid.
        Param:
            Object like string, list or Definition
        Returns:
            list of integers
            if integer cannot be determined returns None 
        """
       
        if isinstance(obj, int):
            return [obj]

        if isinstance(obj, Definition):
            return [obj.DefID]

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
            if isinstance(item, Definition):
                item = item.DefID

            if isinstance(item, str):
                if UTILS.TextUtility.is_integer_possible(item):
                    item = UTILS.TextUtility.get_integer(item)
                else:
                    return None
            
            if not isinstance(item, int):
                return None
            
            result.append(item)

        return result

    def get_defs_raw_data(self) -> list:
        """
        Definitions default order by ID
        Returns (list):
            [0] (int): Definition ID
            [1] (str): Definition name
            [2] (str): Definition description
            [3] (list): Definition expressions
            [4] (list): Definition images
            [5] (list): Definition default image
        """

        def_db = DefDB(self._stt)
        result = def_db.get_complete_definitions_data()
        return result

    def signal_def_added(self, obj: Definition):
        if self._data_dict.get(str(obj.DefID), None):
            UTILS.TerminalUtility.WarningMessage("#1: Definition (ID=#2) already exists in Definitions class. Function: #3.", ["Definitions", obj.DefID, "signal_def_added"], exception_raised=True)
            raise ValueError(f"Definition (ID={obj.DefID}) already exists in Definitions class.")

        self._data_dict[str(obj.DefID)] = obj

    def signal_def_saved(self, obj: Definition):
        if self._data_dict.get(str(obj.DefID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Definition (ID=#2) not found in Definitions class. Function: #3.", ["Definitions", obj.DefID, "signal_def_saved"], exception_raised=True)
            raise ValueError(f"Definition (ID={obj.DefID}) not found in Definitions class.")
        
        self._data_dict[str(obj.DefID)] = obj

    def signal_def_deleted(self, obj: Definition):
        if self._data_dict.get(str(obj.DefID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Definition (ID=#2) not found in Definitions class. Function: #3.", ["Definitions", obj.DefID, "signal_def_deleted"], exception_raised=True)
            raise ValueError(f"Definition (ID={obj.DefID}) not found in Definitions class.")
        
        self._data_dict.pop(str(obj.DefID), None)




