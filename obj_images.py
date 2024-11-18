from typing import Any, Union

from db_media_cls import Media as ImageDB
import UTILS
from obj_constants import *
from obj_image import Image
import settings_cls


class Images:
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

        self._db_image = ImageDB(self._stt)
        self._data_dict = {}

        if auto_load_data:
            self.refresh()

    def refresh(self):
        self._data_dict = self._load_data()

    def get_image_list(self, image_id_s: Union[list, int, str, Image, None]) -> list[Image]:
        """
        Creates list of Image objects from input variable image_id_s

        :param:
            image_id_s: ImageID or list of ImageIDs (if None, returns all items)
        :returns:
            List of Image objects
        """
        
        if image_id_s is None:
            return [x for x in self._data_dict.values()]
        
        if not image_id_s:
            return []
        
        image_id_s = self.convert_ids_to_integer(image_id_s)

        if image_id_s is None:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. ImageID list cannot be converted to integers.\nFunction #3 returned #4.", ["Images", "get_image_list", "convert_ids_to_integer", "None"], exception_raised=True)
            raise TypeError("Unable to convert ImageID list to integers")

        try:
            return [self._data_dict[str(x)] for x in image_id_s]
        except KeyError:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. ImageID does not exist.\ntype(image_id_s) = #3\nimage_id_s = #4", ["Images", "get_image_list", type(image_id_s), image_id_s], exception_raised=True)
            raise ValueError("ImageID does not exist.")
        
    def convert_ids_to_integer(self, obj: Union[Image, list, str]) -> Union[list[int], None]:
        """
        Trying to convert values into integers. Does not checks if ID is valid.
        Param:
            Object like string, list or Image
        Returns:
            list of integers
            if integer cannot be determined returns None 
        """
       
        if isinstance(obj, int):
            return [obj]

        if isinstance(obj, Image):
            return [obj.ImageID]

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
            if isinstance(item, Image):
                item = item.ImageID

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
        raw_data = self.get_images_raw_data()
        
        result = {}
        for idx, img in enumerate(raw_data):
            if idx % int(len(raw_data) / self._feedback_percent_function_steps) == 0:
                if self._feedback_percent_function:
                    self._feedback_percent_function(int((idx + 1) / len(raw_data) * 100))

            img_dict = {
                IMG_INDEX_ID[1]: img[0],
                IMG_INDEX_NAME[1]: img[1],
                IMG_INDEX_DESC[1]: img[2],
                IMG_INDEX_FILE[1]: img[3],
                IMG_INDEX_HTTP[1]: img[4],
                IMG_INDEX_IS_DEFAULT[1]: img[5]
            }

            img_obj = Image(self._stt)
            if img_obj.load_image_from_dict(image_dict=img_dict):
                result[str(img_obj.ImageID)] = img_obj
            else:
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Adding images failed.", ["Images", "_load_data"])
                raise ValueError("Adding images in 'Images' class failed.")
        
        return result

    def get_images_raw_data(self) -> list:
        """
        Returns a list of all images.
        Returns (list):
            [0] (int): Image ID
            [1] (str): Image name
            [2] (str): Image description
            [3] (str): Image file path
            [4] (str): Image source (HTTP)
            [5] (str): Image is_default (if under 100 it is image, else is file)
        """

        img_list = self._db_image.get_all_media()
        return img_list

    def signal_image_added(self, obj: Image):
        if self._data_dict.get(str(obj.ImageID), None):
            UTILS.LogHandler.add_log_record("#1: Image (ID=#2) already exists in Images class. Function: #3.", ["Images", obj.ImageID, "signal_image_added"])
            print (f"Image {obj.ImageID} already exist!")
        
        self._data_dict[str(obj.ImageID)] = obj

    def signal_image_saved(self, obj: Image):
        if self._data_dict.get(str(obj.ImageID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Image (ID=#2) not found in Images class. Function: #3.", ["Images", obj.ImageID, "signal_image_saved"], exception_raised=True)
            raise ValueError(f"Image (ID={obj.ImageID}) not found in Images class.")

        self._data_dict[str(obj.ImageID)] = obj

    def signal_image_deleted(self, obj: Image):
        if self._data_dict.get(str(obj.ImageID), None) is None:
            UTILS.TerminalUtility.WarningMessage("#1: Image (ID=#2) not found in Images class. Function: #3.", ["Images", obj.ImageID, "signal_image_deleted"], exception_raised=True)
            raise ValueError(f"Image (ID={obj.ImageID}) not found in Images class.")

        self._data_dict.pop(str(obj.ImageID), None)



