from typing import Any, Union

from db_definition_cls import Definition as DefDB
from obj_constants import *
from obj_images import Images
from obj_image import Image
import UTILS
import settings_cls


class Definition:
    def __init__(self, settings: settings_cls.Settings, def_id: Union[int, str, 'Definition'] = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Variables
        self._db_def = DefDB(self._stt)
        self.data = self.get_empty_def_dict()

        self._images_obj: Images = self.get_appv("images")

        if def_id is not None:
            self.load_def(def_id=def_id)

    def load_def(self, def_id: Union[int, str, 'Definition']) -> bool:
        if isinstance(def_id, str):
            def_id = UTILS.TextUtility.get_integer(def_id)
        if isinstance(def_id, Definition):
            def_id = def_id.DefID
        if not self._db_def.is_definition_valid(def_id=def_id):
            UTILS.LogHandler.add_log_record("#1: Definition ID (#2) passed to method #3 does not exist!", ["Definition", def_id, "load_def"], warning_raised=True)
            return False

        self._db_def.load_definition(definition_id=def_id)

        # Populate data
        self.data = self.get_empty_def_dict()
        self.data[DEF_INDEX_ID[1]] = self._db_def.definition_id
        self.data[DEF_INDEX_NAME[1]] = self._db_def.definition_name
        self.data[DEF_INDEX_DESC[1]] = self._db_def.definition_description
        self.data[DEF_INDEX_EXPRESSIONS[1]] = self._db_def.definition_synonyms
        self.data[DEF_INDEX_IMAGES[1]] = self._images_obj.get_image_list(self._db_def.definition_media_ids)
        def_img = self._images_obj.get_image_list(self._db_def.default_media_id) if self._db_def.default_media_id else None
        self.data[DEF_INDEX_DEFAULT_IMAGE[1]] = def_img[0] if def_img else None
        
        return True

    def new(self):
        """
        Clears all Definition object properties
        """
        self.data = self.get_empty_def_dict()

    def add(self) -> int | None:
        """
        Add new definition to database.
        Definition object must have ID set to None and unique name.
        If definition is successfully added returns definition ID, else None
        """

        if self.data[DEF_INDEX_ID[1]] is not None:
            UTILS.LogHandler.add_log_record("#1: Unable to add definition. Reason: #2", ["Definition", "In order to add definition, definition ID must be set to None"], warning_raised=True)
            return None

        found_same_name = self._db_def.find_definition_by_name(self.DefName, populate_properties=False)
        if found_same_name:
            UTILS.LogHandler.add_log_record("#1: Unable to add definition. Definition ID=#2 already have same name (#3).", ["Definition", found_same_name, self.DefName], warning_raised=True)
            return None
        
        def_dict = {
            "name": self.DefName,
            "description": self.DefDescription,
            "media_ids": [x.ImageID for x in self.DefImages],
            "synonyms": self.DefSynonyms,
            "show": 1
        }
        if self.DefDefaultImage:
            def_dict["default"] = self.DefDefaultImage.ImageID

        def_id = self._db_def.add_new_definition(def_dict)
        if not def_id:
            UTILS.LogHandler.add_log_record("#1: Unable to add definition. Reason: #2", ["Definition", "Error occurred in db_definition_cls->Definition->add_new_definition"], warning_raised=True, extract_to_variables=def_dict)
            return None
        
        self.data[DEF_INDEX_ID[1]] = def_id
        self.data[SAVED_FLAG] = True
        self.get_appv("defs").signal_def_added(self)
        UTILS.Signal.emit_def_added(self.to_dict())
        return def_id

    def can_be_added(self) -> bool:
        """
        Checks if definition can be added to database.
        """

        if self.data[DEF_INDEX_ID[1]] is not None:
            return False

        found_same_name = self._db_def.find_definition_by_name(self.DefName, populate_properties=False)
        if found_same_name:
            return False

        return True

    def save(self) -> bool:
        """
        Save/Update definition.
        Definition object must have valid ID and unique name.
        """

        if not self._db_def.is_definition_valid(self.DefID):
            UTILS.LogHandler.add_log_record("#1: Unable to save definition. Definition with ID=#2 does not exist.", ["Definition", self.DefID], warning_raised=True)
            return None

        found_same_name = self._db_def.find_definition_by_name(self.DefName, populate_properties=False)
        if found_same_name and found_same_name != self.DefID:
            UTILS.LogHandler.add_log_record("#1: Unable to save definition. Definition ID=#2 already have same name (#3).", ["Definition", found_same_name, self.DefName], warning_raised=True)
            return None
        
        def_dict = {
            "name": self.DefName,
            "description": self.DefDescription,
            "media_ids": [x.ImageID for x in self.DefImages],
            "synonyms": self.DefSynonyms,
            "show": 1
        }

        if self.DefDefaultImage:
            def_dict["default"] = self.DefDefaultImage.ImageID

        def_id = self._db_def.update_definition(self.DefID, def_dict)
        if def_id is None:
            UTILS.LogHandler.add_log_record("#1: Unable to save definition. Reason: #2", ["Definition", "Error occurred in db_definition_cls->Definition->update_definition"], warning_raised=True, extract_to_variables=def_dict)
            return False
        
        self.data[SAVED_FLAG] = True
        self.get_appv("defs").signal_def_saved(self)
        UTILS.Signal.emit_def_saved(self.to_dict())
        return True

    def can_be_saved(self) -> bool:
        """
        Checks if definition can be Saved/Updated.
        """

        if not self._db_def.is_definition_valid(self.DefID):
            return False

        found_same_name = self._db_def.find_definition_by_name(self.DefName, populate_properties=False)
        if found_same_name and found_same_name != self.DefID:
            return False
        
        return True

    def delete(self) -> int | None:
        """
        Deletes definition.
        Definition object must have valid ID.
        """

        if not self._db_def.is_definition_valid(self.DefID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete definition. Definition with ID #2 does not exist.", ["Definition", self.DefID], warning_raised=True)
            return None
        
        result = self._db_def.delete_definition(self.DefID)
        if not result:
            UTILS.LogHandler.add_log_record("#1: Unable to delete definition. Reason: #2", ["Definition", "Error occurred in db_definition_cls->Definition->delete_definition"], warning_raised=True)
            return None
        
        self.data[SAVED_FLAG] = None
        self.get_appv("defs").signal_def_deleted(self)
        UTILS.Signal.emit_def_deleted(self.to_dict())
        return result

    def can_be_deleted(self) -> bool:
        """
        Checks if definition can be deleted.
        """

        if not self._db_def.is_definition_valid(self.DefID):
            return False

        return True

    def is_exist_DefID(self, def_id: int = None) -> bool:
        if def_id is None:
            def_id = self.DefID
        return self._db_def.is_definition_valid(def_id)

    def append_images_to_definition(self, def_s: Union[int, str, Image, list, tuple, set]) -> bool:
        result = self.get_appv("images").get_image_list(def_s)
        if not result:
            UTILS.LogHandler.add_log_record("#1: No images found in function #2\nimage_s = #3", ["Definition", "append_images_to_definition", def_s], warning_raised=True)
            return False

        for item in result:
            if item.ImageID in [x.ImageID for x in self.DefImages]:
                UTILS.LogHandler.add_log_record("#1: Image with id #2 already exist in definition.", ["Definition", item.ImageID], warning_raised=True)
            else:
                self.data[DEF_INDEX_IMAGES[1]].append(item)
        
        return True

    def load_def_from_dict(self, def_dict: dict) -> bool:
        def fix_list_field(field: Any, images: Images) -> list:
            if field is None:
                return []
            
            if isinstance(field, (tuple, set)):
                field = list(field)
            
            if isinstance(field, int):
                field = [field]
            
            if isinstance(field, str):
                if UTILS.TextUtility.is_integer_possible(field):
                    field = [UTILS.TextUtility.get_integer(field)]
                else:
                    UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Cannot resolve definition field #3\ntype(field) = #4\nfield = #5", ["Definition", "load_def_from_dict->fix_list_field", "image", type(field), field], exception_raised=True)
                    raise TypeError("Unable to resolve definition field 'image'.")
            
            if isinstance(field, Image):
                field = [field]

            if not isinstance(field, list):
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Definition field #3 must be a list.\ntype(field) = #4\nfield = #5", ["Definition", "load_def_from_dict->fix_list_field", "image", type(field), field], exception_raised=True)
                raise TypeError("Definition field 'image' must be a list.")
            
            result = []
            for item in field:
                if isinstance(item, str):
                    if UTILS.TextUtility.is_integer_possible(item):
                        item = [UTILS.TextUtility.get_integer(item)]
                    else:
                        UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Cannot resolve element in definition field #3\ntype(item) = #4\nitem = #5", ["Definition", "load_def_from_dict->fix_list_field", "image", type(item), item], exception_raised=True)
                        raise TypeError(f"Unable to resolve element in definition field 'image'. Element: {item}")
                
                passed = False
                if isinstance(item, Image):
                    passed = True
                
                if not isinstance(item, int) and not passed:
                    UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Cannot resolve element in definition field #3\ntype(item) = #4\nitem = #5", ["Definition", "load_def_from_dict->fix_list_field", "image", type(item), item], exception_raised=True)
                    raise TypeError(f"Unable to resolve element in definition field 'image'. Element: {item}")
                
                result.append(item)
            
            result = images.get_image_list(result)
            
            return result

        required_fields = [
            DEF_INDEX_ID[1],
            DEF_INDEX_NAME[1],
            DEF_INDEX_DESC[1],
            DEF_INDEX_EXPRESSIONS[1],
            DEF_INDEX_IMAGES[1],
            DEF_INDEX_DEFAULT_IMAGE[1]
        ]

        if any(x not in def_dict.keys() for x in required_fields):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Definition dictionary is incomplete.\nRequired fields: #3\ndef_dict fields: #4", ["Definition", "load_def_from_dict", required_fields, def_dict.keys()], exception_raised=True)
            raise ValueError("Definition dictionary does not contain all required keys.")

        images: Images = self.get_appv("images")

        # Populate data
        self.data = self.get_empty_def_dict()
        self.data[DEF_INDEX_ID[1]] = UTILS.TextUtility.get_integer(def_dict[DEF_INDEX_ID[1]])
        self.data[DEF_INDEX_NAME[1]] = str(def_dict[DEF_INDEX_NAME[1]])
        self.data[DEF_INDEX_DESC[1]] = str(def_dict[DEF_INDEX_DESC[1]])
        self.data[DEF_INDEX_EXPRESSIONS[1]] = list(def_dict[DEF_INDEX_EXPRESSIONS[1]])
        self.data[DEF_INDEX_IMAGES[1]] = fix_list_field(def_dict.get(DEF_INDEX_IMAGES[1]), images=images)
        def_img = fix_list_field(def_dict.get(DEF_INDEX_DEFAULT_IMAGE[1]), images=images) if def_dict.get(DEF_INDEX_DEFAULT_IMAGE[1]) else None
        self.data[DEF_INDEX_DEFAULT_IMAGE[1]] = def_img[0] if def_img else None
        
        return True

    def to_dict(self) -> dict:
        return self.data

    def to_dict_unpacked(self) -> dict:
        result = dict(self.data)
        result[DEF_INDEX_IMAGES[1]] = [x.ImageID for x in self.DefImages]
        if self.DefDefaultImage:
            result[DEF_INDEX_DEFAULT_IMAGE[1]] = self.DefDefaultImage.ImageID
        else:
            result[DEF_INDEX_DEFAULT_IMAGE[1]] = None
        return result

    def get_empty_def_dict(self) -> dict:
        return {
            DEF_INDEX_ID[1]: None,
            DEF_INDEX_NAME[1]: "",
            DEF_INDEX_DESC[1]: "",
            DEF_INDEX_EXPRESSIONS[1]: [],
            DEF_INDEX_IMAGES[1]: [],
            DEF_INDEX_DEFAULT_IMAGE[1]: None,
            SAVED_FLAG: True
        }

    def _object_changed(self):
        self.data[SAVED_FLAG] = False

    def __str__(self) -> str:
        return f"Definition ID: {self.data[DEF_INDEX_ID[1]]}"

    def __eq__(self, other):
        if isinstance(other, Definition):
            if (self.data[DEF_INDEX_ID[1]] == other.data[DEF_INDEX_ID[1]]
                and self.data[DEF_INDEX_NAME[1]] == other.data[DEF_INDEX_NAME[1]]
                and self.data[DEF_INDEX_DESC[1]] == other.data[DEF_INDEX_DESC[1]]
                and all(x in other[DEF_INDEX_EXPRESSIONS[1]] for x in self.data[DEF_INDEX_EXPRESSIONS[1]])
                and len(self.data[DEF_INDEX_EXPRESSIONS[1]]) == len(other.data[DEF_INDEX_EXPRESSIONS[1]])
                and all(x in other[DEF_INDEX_IMAGES[1]] for x in self.data[DEF_INDEX_IMAGES[1]])
                and len(self.data[DEF_INDEX_IMAGES[1]]) == len(other.data[DEF_INDEX_IMAGES[1]])
                and self.data[DEF_INDEX_DEFAULT_IMAGE[1]] == other.data[DEF_INDEX_DEFAULT_IMAGE[1]]):
                return True
            else:
                return False
        else:
            return False    

    @property
    def DefID(self) -> int:
        return self.data[DEF_INDEX_ID[1]]
    
    @DefID.setter
    def DefID(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. DefinitionID must be #3 or #4.\ntype(value) = #5\nvalue = #6", ["Definition", "DefID.setter", "integer", "None", type(value), value], exception_raised=True)
            raise TypeError("DefinitionID must me integer or None")
            
        if self.data[DEF_INDEX_ID[1]] != value:
            self.data[DEF_INDEX_ID[1]] = value
            self._object_changed()

    @property
    def DefName(self) -> str:
        return self.data[DEF_INDEX_NAME[1]]

    @DefName.setter
    def DefName(self, value: str) -> None:
        if self.data[DEF_INDEX_NAME[1]] != str(value):
            self.data[DEF_INDEX_NAME[1]] = str(value)
            self._object_changed()

    @property
    def DefDescription(self) -> str:
        return self.data[DEF_INDEX_DESC[1]]

    @DefDescription.setter
    def DefDescription(self, value: str) -> None:
        if self.data[DEF_INDEX_DESC[1]] != str(value):
            self.data[DEF_INDEX_DESC[1]] = str(value)
            self._object_changed()

    @property
    def DefSynonyms(self) -> list:
        return self.data[DEF_INDEX_EXPRESSIONS[1]]
    
    @DefSynonyms.setter
    def DefSynonyms(self, value: list) -> None:
        if isinstance(value, int):
            value = [value]

        if not isinstance(value, list):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Synonyms must be a list.\ntype(value) = #3\nvalue = #4", ["Definition", "DefSynonyms.setter", type(value), value], exception_raised=True)
            raise TypeError("Synonyms must be a list")

        if self.data[DEF_INDEX_EXPRESSIONS[1]] != value:
            self.data[DEF_INDEX_EXPRESSIONS[1]] = value
            self._object_changed()

    @property
    def DefImages(self) -> list[Image]:
        return self.data[DEF_INDEX_IMAGES[1]]
    
    @DefImages.setter
    def DefImages(self, image_list: list) -> None:
        if isinstance(image_list, str):
            image_list = [image_list]
        
        if self.data[DEF_INDEX_IMAGES[1]] != self._images_obj.get_image_list(image_list):
            self.data[DEF_INDEX_IMAGES[1]] = self._images_obj.get_image_list(image_list)
            self._object_changed()

    @property
    def DefDefaultImage(self) -> Image:
        return self.data[DEF_INDEX_DEFAULT_IMAGE[1]]
    
    @DefDefaultImage.setter
    def DefDefaultImage(self, image_id_or_obj: Union[Image, str, int]) -> None:
        if isinstance(image_id_or_obj, str):
            image_id_or_obj = [image_id_or_obj]
        
        result = self._images_obj.get_image_list(image_id_or_obj)
        if result:
            if not self.DefDefaultImage or self.DefDefaultImage.ImageID != result[0].ImageID:
                if result[0].ImageID in [x.ImageID for x in self.DefImages]:
                    self.data[DEF_INDEX_DEFAULT_IMAGE[1]] = result[0]
                    self._object_changed()
                else:
                    UTILS.LogHandler.add_log_record("#1: Unable to set default image because this image is not added to definition images.\nDefault image is not set.", ["Definition"])
        else:
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Default image not found.\ntype(image_id_or_obj) = #3\nimage_id_or_obj = #4", ["Definition", "DefDefaultImage.setter", type(image_id_or_obj), image_id_or_obj], exception_raised=True)
            raise ValueError(f"Default image not found. Type: {type(image_id_or_obj)} Value: {image_id_or_obj}")

