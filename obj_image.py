from typing import Any, Union

from db_media_cls import Media as ImageDB
from obj_constants import *
import UTILS
from utils_file import FileInformation
import settings_cls


class Image:
    def __init__(self, settings: settings_cls.Settings, image_id: Union[int, str, 'Image'] = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Variables
        self.data = self.get_empty_image_dict()
        self._db_image = ImageDB(self._stt)

        if image_id is not None:
            self.load_image(image_id)

    def load_image(self, image_id: Union[int, str, 'Image']) -> bool:
        if isinstance(image_id, str):
            image_id = UTILS.TextUtility.get_integer(image_id)
        if isinstance(image_id, Image):
            image_id = image_id.ImageID
        if not self._db_image.is_media_exist(media_id=image_id):
            UTILS.LogHandler.add_log_record("#1: Image ID (#2) passed to method #3 does not exist!", ["Image", image_id, "load_image"], warning_raised=True)
            return False

        self.data = self.get_empty_image_dict()
        self._db_image.load_media(media_id=image_id)

        self.data[IMG_INDEX_ID[1]] = self._db_image.media_id
        self.data[IMG_INDEX_NAME[1]] = self._db_image.media_name
        self.data[IMG_INDEX_DESC[1]] = self._db_image.media_description
        self.data[IMG_INDEX_FILE[1]] = FileInformation(self._db_image.media_file)
        self.data[IMG_INDEX_HTTP[1]] = self._db_image.media_http
        self.data[IMG_INDEX_IS_DEFAULT[1]] = self._db_image.media_default
        
        return True

    def new(self):
        """
        Clears all Image object properties
        """
        self.data = self.get_empty_image_dict()

    def add_to_image_list(self) -> int | None:
        """
        Add new image to Images list.
        If image is successfully added returns image ID, else None
        """

        if self.data[IMG_INDEX_ID[1]] is None:
            UTILS.LogHandler.add_log_record("#1: Unable to add image. Reason: #2", ["Image", "Image not loaded"], warning_raised=True)
            return None

        if not self.ImageFile.is_file():
            UTILS.LogHandler.add_log_record("#1: Unable to add image. Reason: #2", ["Image", "Image file does not exist"], warning_raised=True)
            return None
        
        image_id = self.ImageID
        
        self.get_appv("images").signal_image_added(self)
        UTILS.Signal.emit_image_added(self.to_dict())
        return image_id

    def can_be_added(self) -> bool:
        """
        Checks if image can be added to database.
        """

        if self.data[IMG_INDEX_ID[1]] is None:
            return False

        if not self.ImageFile.is_file():
            return False

        return True

    def save(self) -> bool:
        """
        Save/Update image.
        Image object must have valid ID and valid ImageFile property.
        """

        if not self._db_image.is_media_exist(self.ImageID):
            UTILS.LogHandler.add_log_record("#1: Unable to save image. Image with ID #2 does not exist.", ["Image", self.ImageID], warning_raised=True)
            return False

        if not self.ImageFile.is_file():
            UTILS.LogHandler.add_log_record("#1: Unable to save image. Filepath #2 is not valid path.", ["Image", self.ImageFile], warning_raised=True)
            return False
        
        image_dict = {
            "name": self.ImageName,
            "description": self.ImageDescription,
            "file": self.ImageFile.file_path,
            "http": self.ImageHTTP,
            "default": self.ImageIsDefault
        }
        image_id = self._db_image.update_media(media_id=self.ImageID, media_dict=image_dict)
        if not image_id:
            UTILS.LogHandler.add_log_record("#1: Unable to save image. Reason: #2", ["Image", "Error occurred in db_media_cls->Media->update_media"], warning_raised=True, extract_to_variables=image_dict)
            return False
        
        self.data[SAVED_FLAG] = True
        self.get_appv("images").signal_image_saved(self)
        UTILS.Signal.emit_image_saved(self.to_dict())
        return True

    def can_be_saved(self) -> bool:
        """
        Checks if image can be Saved/Updated.
        """

        if not self._db_image.is_media_exist(self.ImageID):
            return False

        if not self.ImageFile.is_file():
            return False
        
        return True

    def delete(self) -> int | None:
        """
        Deletes image.
        Image object must have valid ID and not being used in any block or definition.
        """

        if not self._db_image.is_media_exist(self.ImageID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete image. Image with ID #2 does not exist.", ["Image", self.ImageID], warning_raised=True)
            return None
        
        if not self._db_image.is_safe_to_delete(self.ImageID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete image. Image is used in some blocks or definitions.", ["Image"], warning_raised=True)
            return None

        result = self._db_image.delete_media(self.ImageID)
        if not result:
            UTILS.LogHandler.add_log_record("#1: Unable to delete image. Reason: #2", ["Image", "Error occurred in db_media_cls->Media->delete_media"], warning_raised=True)
            return None
        
        self.data[SAVED_FLAG] = None
        self.get_appv("images").signal_image_deleted(self)
        UTILS.Signal.emit_image_deleted(self.to_dict())
        return result

    def can_be_deleted(self) -> bool:
        """
        Checks if image can be deleted.
        """

        if not self._db_image.is_media_exist(self.ImageID):
            return False
        
        if not self._db_image.is_safe_to_delete(self.ImageID):
            return False

        return True

    def is_exist_ImageID(self, image_id: int = None) -> bool:
        if image_id is None:
            image_id = self.ImageID
        return self._db_image.is_media_exist(image_id)
    
    def is_ImageFile_path_valid(self):
        return self.ImageFile.is_file()

    def load_image_from_dict(self, image_dict: dict) -> bool:
        required_fields = [
            IMG_INDEX_ID[1],
            IMG_INDEX_NAME[1],
            IMG_INDEX_DESC[1],
            IMG_INDEX_FILE[1],
            IMG_INDEX_HTTP[1]
        ]

        if any(x not in image_dict.keys() for x in required_fields):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Image dictionary is incomplete.\nRequired fields: #3\nimage_dict fields: #4", ["Image", "load_image_from_dict", required_fields, image_dict.keys()], exception_raised=True)
            raise ValueError("Image dictionary does not contain all required keys.")

        if 0 > image_dict.get(IMG_INDEX_IS_DEFAULT[1], 0) > 99:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. ImageDefault value must be between 0 and 99. passed #3", ["Image", "load_image_from_dict", image_dict.get(IMG_INDEX_IS_DEFAULT[1], 0)], exception_raised=True)
            raise ValueError("ImageDefault must be between 0 and 99.")

        self.data = self.get_empty_image_dict()
        self.data[IMG_INDEX_ID[1]] = image_dict[IMG_INDEX_ID[1]]
        self.data[IMG_INDEX_NAME[1]] = image_dict[IMG_INDEX_NAME[1]]
        self.data[IMG_INDEX_DESC[1]] = image_dict[IMG_INDEX_DESC[1]]
        self.data[IMG_INDEX_FILE[1]] = FileInformation(image_dict[IMG_INDEX_FILE[1]])
        self.data[IMG_INDEX_HTTP[1]] = image_dict[IMG_INDEX_HTTP[1]]
        self.data[IMG_INDEX_IS_DEFAULT[1]] = image_dict.get(IMG_INDEX_IS_DEFAULT[1], 0)
        return True

    def to_dict(self) -> dict:
        return self.data

    def to_dict_unpacked(self) -> dict:
        result = dict(self.data)
        result[IMG_INDEX_FILE[1]] = self.ImageFile.file_path
        return result

    def get_empty_image_dict(self) -> dict:
        return {
            IMG_INDEX_ID[1]: None,
            IMG_INDEX_NAME[1]: "",
            IMG_INDEX_DESC[1]: "",
            IMG_INDEX_FILE[1]: "",
            IMG_INDEX_HTTP[1]: "",
            IMG_INDEX_IS_DEFAULT[1]: 0,
            SAVED_FLAG: True
        }

    def _object_changed(self):
        self.data[SAVED_FLAG] = False

    def __str__(self) -> str:
        return f"Image ID: {self.data[IMG_INDEX_ID[1]]}"

    def __eq__(self, other):
        if isinstance(other, Image):
            if (self.data[IMG_INDEX_ID[1]] == other.data[IMG_INDEX_ID[1]]
                and self.data[IMG_INDEX_NAME[1]] == other.data[IMG_INDEX_NAME[1]]
                and self.data[IMG_INDEX_DESC[1]] == other.data[IMG_INDEX_DESC[1]]
                and self.data[IMG_INDEX_FILE[1]] == other.data[IMG_INDEX_FILE[1]]
                and self.data[IMG_INDEX_HTTP[1]] == other.data[IMG_INDEX_HTTP[1]]
                and self.data[IMG_INDEX_IS_DEFAULT[1]] == other.data[IMG_INDEX_IS_DEFAULT[1]]
                ):
                return True
            else:
                return False
        else:
            return False    

    @property
    def ImageID(self) -> int:
        return self.data[IMG_INDEX_ID[1]]
    
    @ImageID.setter
    def ImageID(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. ImageID property must be an integer.\ntype(value) = #3\nvalue = #4", ["Image", "ImageID.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The ImageID property must be a integer. Passed '{str(type(value))}', expected 'int'")
        
        if self.data[IMG_INDEX_ID[1]] != value:
            self.data[IMG_INDEX_ID[1]] = value
            self._object_changed()

    @property
    def ImageName(self) -> str:
        return self.data[IMG_INDEX_NAME[1]]
    
    @ImageName.setter
    def ImageName(self, value: str) -> None:
        if self.data[IMG_INDEX_NAME[1]] != str(value):
            self.data[IMG_INDEX_NAME[1]] = str(value)
            self._object_changed()
    
    @property
    def ImageDescription(self) -> str:
        return self.data[IMG_INDEX_DESC[1]]
    
    @ImageDescription.setter
    def ImageDescription(self, value: str) -> None:
        if self.data[IMG_INDEX_DESC[1]] != str(value):
            self.data[IMG_INDEX_DESC[1]] = str(value)
            self._object_changed()
    
    @property
    def ImageFile(self) -> FileInformation:
        return self.data[IMG_INDEX_FILE[1]]
    
    @ImageFile.setter
    def ImageFile(self, value: Union[str, FileInformation]) -> None:
        if not isinstance(value, (str, FileInformation)):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. ImageFile property must be a string or FileInformation object.\ntype(value) = #3\nvalue = #4", ["Image", "ImageFile.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The ImageFile property must be a string or FileInformation object. Passed '{str(type(value))}', expected 'FileInformation'")
        
        if self.data[IMG_INDEX_FILE[1]] != FileInformation(value):
            self.data[IMG_INDEX_FILE[1]] = FileInformation(value)
            self._object_changed()
    
    @property
    def ImageHTTP(self) -> str:
        return self.data[IMG_INDEX_HTTP[1]]
    
    @ImageHTTP.setter
    def ImageHTTP(self, value: str) -> None:
        if self.data[IMG_INDEX_HTTP[1]] != str(value):
            self.data[IMG_INDEX_HTTP[1]] = str(value)
            self._object_changed()
    
    @property
    def ImageIsDefault(self) -> int:
        return self.data[IMG_INDEX_IS_DEFAULT[1]]
    
    @ImageIsDefault.setter
    def ImageIsDefault(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. ImageIsDefault property must be an integer.\ntype(value) = #3\nvalue = #4", ["Image", "ImageIsDefault.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The ImageIsDefault property must be a integer. Passed '{str(type(value))}', expected 'int'")

        if not value in range(0, 100):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. ImageIsDefault property must be in range 0 - 99.\ntype(value) = #3\nvalue = #4", ["Image", "ImageIsDefault.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The ImageIsDefault property must be in range 0 - 99. Passed '{str(type(value))}'.")
        
        if self.data[IMG_INDEX_IS_DEFAULT[1]] != value:
            self.data[IMG_INDEX_IS_DEFAULT[1]] = value
            self._object_changed()








