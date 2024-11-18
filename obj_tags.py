from typing import Any, Union

from db_tag_cls import Tag as TagDB
import UTILS
from obj_constants import *
from obj_tag import Tag
import settings_cls


class Tags:
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

        self._db_tag = TagDB(self._stt)
        self._data_dict = {}

        if auto_load_data:
            self.refresh()

    def refresh(self):
        self._data_dict = self._load_data()

    def get_tag_list(self, tag_id_s: Union[list, int, str, Tag, None]) -> list[Tag]:
        """
        Creates list of Tag objects from input variable tag_id_s

        :param:
            tag_id_s: TagID or list of TagIDs (if None, returns all items)
        :returns:
            List of Tag objects
        """

        if tag_id_s is None:
            return list(self.data)
        
        if not tag_id_s:
            return []
        
        tag_id_s = self.convert_ids_to_integer(tag_id_s)

        if tag_id_s is None:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. TagID list cannot be converted to integers.\nFunction #3 returned #4.", ["Tags", "get_tag_list", "convert_ids_to_integer", "None"], exception_raised=True)
            raise TypeError("Unable to convert TagID list to integers")

        try:
            return [self._data_dict[str(x)] for x in tag_id_s]
        except KeyError:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. TagID does not exist.\ntype(tag_id_s) = #3\ntag_id_s = #4", ["Tags", "get_tag_list", type(tag_id_s), tag_id_s], exception_raised=True)
            raise ValueError("TagID does not exist.")

    def convert_ids_to_integer(self, obj: Union[Tag, list, str]) -> Union[list[int], None]:
        """
        Trying to convert values into integers. Does not checks if tag ID is valid.
        Param:
            Object like string, list or Tag
        Returns:
            list of integers
            if integer cannot be determined returns None 
        """
       
        if isinstance(obj, int):
            return [obj]

        if isinstance(obj, Tag):
            return [obj.TagID]

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
            if isinstance(item, Tag):
                item = item.TagID

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
        raw_data = self.get_tags_raw_data()
        
        result = {}
        for idx, tag in enumerate(raw_data):
            if idx % int(len(raw_data) / self._feedback_percent_function_steps) == 0:
                if self._feedback_percent_function:
                    self._feedback_percent_function(int((idx + 1) / len(raw_data) * 100))
            
            tag_dict = {
                TAG_INDEX_ID[1]: tag[0],
                TAG_INDEX_NAME[1]: tag[1],
                TAG_INDEX_USER_DEF[1]: tag[2],
                TAG_INDEX_DESC[1]: tag[3]
            }

            tag_obj = Tag(self._stt)
            if tag_obj.load_tag_from_dict(tag_dict=tag_dict):
                result[str(tag_obj.TagID)] = tag_obj
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Tag ID #3 does not exist in the database.\nTag name = #4", ["Tags", "load_data", tag_obj.TagID, tag_obj.TagName], exception_raised=True)
                raise ValueError(f"Tag ID {tag_obj.TagID} does not exist in the database.")
        
        return result

    def get_tags_raw_data(self) -> list:
        """
        Returns a list of all tags.
        Returns (list):
            [0] (int): Tag ID
            [1] (str): Tag name
            [2] (int): Tag user_def (0=No, 1=Yes)
            [3] (str): Tag description
        """
        tag_list = self._db_tag.get_all_tags_translated()
        return tag_list

    def signal_tag_added(self, obj: Tag):
        if self._data_dict.get(str(obj.TagID), None):
            UTILS.TerminalUtility.WarningMessage("#1: Tag (ID=#2) already exists in Tags class. Function: #3.", ["Tags", obj.TagID, "signal_tag_added"], exception_raised=True)
            raise ValueError(f"Tag (ID={obj.TagID}) already exists in Tags class.")
        
        self._data_dict[str(obj.TagID)] = obj

    def signal_tag_saved(self, obj: Tag):
        if self._data_dict.get(str(obj.TagID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Tag (ID=#2) not found in Tags class. Function: #3.", ["Tags", obj.TagID, "signal_tag_saved"], exception_raised=True)
            raise ValueError(f"Tag (ID={obj.TagID}) not found in Tags class.")
        
        self._data_dict[str(obj.TagID)] = obj

    def signal_tag_deleted(self, obj: Tag):
        if self._data_dict.get(str(obj.TagID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Tag (ID=#2) not found in Tags class. Function: #3.", ["Tags", obj.TagID, "signal_tag_deleted"], exception_raised=True)
            raise ValueError(f"Tag (ID={obj.TagID}) not found in Tags class.")
        
        self._data_dict.pop(str(obj.TagID), None)
        


