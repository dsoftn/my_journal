from typing import Any, Union

from db_record_cls import Record
from db_record_data_cls import RecordData
from db_media_cls import Files as FilesDB
import UTILS
from obj_constants import *
from obj_block import Block
import settings_cls


class Blocks:
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
        raw_data = self.get_records_raw_data()
        
        result = {}
        for idx, rec in enumerate(raw_data):
            if idx % int(len(raw_data) / self._feedback_percent_function_steps) == 0:
                if self._feedback_percent_function:
                    self._feedback_percent_function(int((idx + 1) / len(raw_data) * 100))
            
            block_dict = {
                REC_INDEX_ID[1]: rec[0],
                REC_INDEX_NAME[1]: rec[1],
                REC_INDEX_DATE[1]: rec[2],
                REC_INDEX_DATE_INT[1]: rec[3],
                REC_INDEX_BODY[1]: rec[4],
                REC_INDEX_DRAFT[1]: rec[5],
                REC_INDEX_CREATED_AT[1]: rec[6],
                REC_INDEX_UPDATED_AT[1]: rec[7],
                REC_INDEX_BODY_HTML[1]: rec[8],
                REC_INDEX_TAGS[1]: rec[9],
                REC_INDEX_IMAGES[1]: rec[10],
                REC_INDEX_FILES[1]: rec[11]
            }

            block_obj = Block(self._stt)
            if block_obj.load_block_from_dict(block_dict=block_dict):
                result[str(block_obj.RecID)] = block_obj
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Adding blocks failed.", ["Blocks", "_load_data"])
                raise ValueError("Adding blocks in 'Blocks' class failed.")
        
        return result

    def get_block_list(self, RecID: Union[list, int, str, Block, None]) -> list[Block]:
        """
        Creates list of Block objects from input variable RecID

        :param:
            RecID: RecID or list of RecIDs (if None, returns all items)
        :returns:
            List of Block objects
        """

        if RecID is None:
            return [x for x in self._data_dict.values()]
        
        if not RecID:
            return []
        
        RecID = self.convert_ids_to_integer(RecID)

        if RecID is None:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. RecID list cannot be converted to integers.\nFunction #3 returned #4.", ["Images", "get_block_list", "convert_ids_to_integer", "None"], exception_raised=True)
            raise TypeError("Unable to convert RecID list to integers")

        try:
            return [self._data_dict[str(x)] for x in RecID]
        except KeyError:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. RecID does not exist.\ntype(RecID) = #3\nRecID = #4", ["Blocks", "get_block_list", type(RecID), RecID], exception_raised=True)
            raise ValueError("RecID does not exist.")

    def convert_ids_to_integer(self, obj: Union[Block, list, str]) -> Union[list[int], None]:
        """
        Trying to convert values into integers. Does not checks if tag ID is valid.
        Param:
            Object like string, list or Block
        Returns:
            list of integers
            if integer cannot be determined returns None 
        """
       
        if isinstance(obj, int):
            return [obj]

        if isinstance(obj, Block):
            return [obj.RecID]

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
            if isinstance(item, Block):
                item = item.RecID

            if isinstance(item, str):
                if UTILS.TextUtility.is_integer_possible(item):
                    item = UTILS.TextUtility.get_integer(item)
                else:
                    return None
            
            if not isinstance(item, int):
                return None
            
            result.append(item)

        return result

    def get_records_raw_data(self) -> list:
        """
        Records default
        Returns (list):
            [0] (int): Record ID
            [1] (str): Record name
            [2] (str): Record date
            [3] (int): Record date as integer
            [4] (str): Record body
            [5] (int): Record draft
            [6] (str): Record created_at
            [7] (str): Record updated_at
            [8] (str): Record body_html
            [9] (list): Record tags
            [10] (list): Record images
            [11] (list): Record files
        """

        rec = Record(self._stt)
        result = list([list(x) for x in rec.get_all_records(sort_by_id=True)])
        rec_data = self.get_records_data_raw_data()
        files_obj = FilesDB(self._stt)
        files = [x[0] for x in files_obj.get_all_file()]

        pos = 0
        for result_index in range(len(result)):
            rec_index = result[result_index][REC_INDEX_ID[0]]
            result[result_index].append([])
            result[result_index].append([])
            result[result_index].append([])
            for rec_data_index in range(pos, len(rec_data)):
                if rec_data[rec_data_index][REC_DATA_INDEX_RECORD_ID[0]] == rec_index:
                    if rec_data[rec_data_index][REC_DATA_INDEX_TAG_ID[0]]:
                        result[result_index][REC_INDEX_TAGS[0]].append(rec_data[rec_data_index][REC_DATA_INDEX_TAG_ID[0]])
                    if rec_data[rec_data_index][REC_DATA_INDEX_MEDIA_ID[0]]:
                        if rec_data[rec_data_index][REC_DATA_INDEX_MEDIA_ID[0]] in files:
                            result[result_index][REC_INDEX_FILES[0]].append(rec_data[rec_data_index][REC_DATA_INDEX_MEDIA_ID[0]])
                        else:
                            result[result_index][REC_INDEX_IMAGES[0]].append(rec_data[rec_data_index][REC_DATA_INDEX_MEDIA_ID[0]])
                else:
                    pos = rec_data_index
                    break

        return result

    def get_records_data_raw_data(self) -> list:
        """
        RecordData default order by record_id
        Returns (list):
            [0] (int): RecordData ID
            [1] (int): RecordData record_id
            [2] (int): RecordData tag_id
            [3] (int): RecordData media_id
        """

        rec_data = RecordData(self._stt)
        result = rec_data.get_all_record_data()
        return result

    def signal_block_added(self, obj: Block):
        if self._data_dict.get(str(obj.RecID), None):
            UTILS.TerminalUtility.WarningMessage("#1: Block (ID=#2) already exists in Blocks class. Function: #3.", ["Blocks", obj.RecID, "signal_block_added"], exception_raised=True)
            raise ValueError(f"Block (ID={obj.RecID}) already exists in Blocks class.")
        
        self._data_dict[str(obj.RecID)] = obj

    def signal_block_saved(self, obj: Block):
        if self._data_dict.get(str(obj.RecID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Saved block (ID=#2) not found in Blocks class. Function: #3.", ["Blocks", obj.RecID, "signal_block_saved"], exception_raised=True)
            raise ValueError(f"Saved block (ID={obj.RecID}) not found in Blocks class.")
        
        self._data_dict[str(obj.RecID)] = obj

    def signal_block_deleted(self, obj: Block):
        if self._data_dict.get(str(obj.RecID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Deleted block (ID=#2) not found in Blocks class. Function: #3.", ["Blocks", obj.RecID, "signal_block_deleted"], exception_raised=True)
            raise ValueError(f"Deleted block (ID={obj.RecID}) not found in Blocks class.")
        
        self._data_dict.pop(str(obj.RecID), None)





