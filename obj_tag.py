from typing import Any, Union

from db_tag_cls import Tag as TagDB
from obj_constants import *
import UTILS
import settings_cls


class Tag:
    def __init__(self, settings: settings_cls.Settings, tag_id: Union[int, str, 'Tag'] = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Variables
        self.data = self.get_empty_tag_dict()
        self._db_tag = TagDB(self._stt)

        if tag_id is not None:
            self.load_tag(tag_id)

    def load_tag(self, tag_id: Union[int, str, 'Tag']) -> bool:
        if isinstance(tag_id, str):
            tag_id = UTILS.TextUtility.get_integer(tag_id)
        if isinstance(tag_id, Tag):
            tag_id = tag_id.TagID
        if not self._db_tag.is_valid_tag_id(tag_id=tag_id):
            UTILS.LogHandler.add_log_record("#1: Tag ID (#2) passed to method #3 does not exist!", ["Tag", tag_id, "load_tag"], warning_raised=True)
            return False

        self.data = self.get_empty_tag_dict()
        self._db_tag.populate_values(tag_id=tag_id)

        self.data[TAG_INDEX_ID[1]] = self._db_tag.TagID
        self.data[TAG_INDEX_NAME[1]] = self._db_tag.TagNameTranslated
        self.data[TAG_INDEX_USER_DEF[1]] = self._db_tag.TagUserDefinded
        self.data[TAG_INDEX_DESC[1]] = self._db_tag.TagDescriptionTranslated
        
        return True

    def new(self):
        """
        Clears all Tag object properties
        """
        self.data = self.get_empty_tag_dict()

    def add(self) -> int | None:
        """
        Add new tag to database.
        Tag object must have ID set to None and unique tag name.
        Only user defined tags can be added so TagUserDefined will be set to 1
        If tag is successfully added returns tag ID, else None
        """

        if self.data[TAG_INDEX_ID[1]] is not None:
            UTILS.LogHandler.add_log_record("#1: Unable to add tag. Reason: #2", ["Tag", "In order to add tag, tag ID must be set to None"], warning_raised=True)
            return None

        if self._db_tag.is_valid_tag_name(self.TagName):
            UTILS.LogHandler.add_log_record("#1: Unable to add tag. Reason: #2", ["Tag", "Tag name already exist"], warning_raised=True)
            return None
        
        tag_dict = {
            "name": self.TagName,
            "description": self.TagDescription,
            "user_def": 1,
            "name_transl": "",
            "description_transl": ""
        }
        tag_id = self._db_tag.add_new_tag(tag_dict=tag_dict)
        if not tag_id:
            UTILS.LogHandler.add_log_record("#1: Unable to add tag. Reason: #2", ["Tag", "Error occurred in db_tag_cls->Tag->add_new_tag"], warning_raised=True, extract_to_variables=tag_dict)
            return None
        
        self.data[TAG_INDEX_ID[1]] = tag_id
        self.data[SAVED_FLAG] = True
        self.get_appv("tags").signal_tag_added(self)
        UTILS.Signal.emit_tag_added(self.to_dict())
        return tag_id

    def can_be_added(self) -> bool:
        """
        Checks if tag can be added to database.
        """

        if self.data[TAG_INDEX_ID[1]] is not None:
            return False

        if self._db_tag.is_valid_tag_name(self.TagName):
            return False

        return True

    def save(self) -> bool:
        """
        Save/Update tag.
        Tag object must have valid ID and unique name.
        """

        if not self._db_tag.is_valid_tag_id(self.TagID):
            UTILS.LogHandler.add_log_record("#1: Unable to save tag (ID=#2). Reason: #3", ["Tag", self.TagID, "TagID does not exist"], warning_raised=True)
            return False

        for item in self.get_appv("tags").data:
            if item.TagName == self.TagName and item.TagID != self.TagID:
                UTILS.LogHandler.add_log_record("#1: Unable to save tag with ID=#2, another tag with ID=#3 has same name (#4).", ["Tags", self.TagID, item.TagID, self.TagName], warning_raised=True)
                return False
                
        tag_dict = {
            "name": self.TagName,
            "description": self.TagDescription,
            "user_def": self.TagUserDefined
        }
        tag_id = self._db_tag.update_tag(self.TagID, tag_dict)
        if not tag_id:
            UTILS.LogHandler.add_log_record("#1: Unable to save tag. Reason: #2", ["Tag", "Error occurred in db_tag_cls->Tag->update_tag"], warning_raised=True, extract_to_variables=tag_dict)
            return False
        
        self.data[SAVED_FLAG] = True
        self.get_appv("tags").signal_tag_saved(self)
        UTILS.Signal.emit_tag_saved(self.to_dict())
        return True

    def can_be_saved(self) -> bool:
        """
        Checks if tag can be Saved/Updated.
        """

        if not self._db_tag.is_valid_tag_id(self.TagID):
            return False

        for item in self.get_appv("tags").data:
            if item.TagName == self.TagName and item.TagID != self.TagID:
                return False
        
        return True

    def delete(self) -> int | None:
        """
        Deletes tag.
        Tag object must have valid ID and not being used in any block.
        """

        if not self._db_tag.is_valid_tag_id(self.TagID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete tag. Tag with ID #2 does not exist.", ["Tag", self.TagID], warning_raised=True)
            return None
        
        used_count = self._db_tag.how_many_times_is_used(self.TagID)
        if used_count:
            UTILS.LogHandler.add_log_record("#1: Unable to delete tag. Tag is used in #2 blocks.", ["Tag", used_count], warning_raised=True)
            return None

        result = self._db_tag.delete_tag(self.TagID)
        if not result:
            UTILS.LogHandler.add_log_record("#1: Unable to delete tag. Reason: #2", ["Tag", "Error occurred in db_tag_cls->Tag->delete_tag"], warning_raised=True)
            return None
        
        self.data[SAVED_FLAG] = None
        self.get_appv("tags").signal_tag_deleted(self)
        UTILS.Signal.emit_tag_deleted(self.to_dict())
        return result

    def can_be_deleted(self) -> bool:
        """
        Checks if tag can be deleted.
        """

        if not self._db_tag.is_valid_tag_id(self.TagID):
            return False
        
        used_count = self._db_tag.how_many_times_is_used(self.TagID)
        if used_count:
            return False

        return True

    def is_exist_TagID(self, tag_id: int = None) -> bool:
        if tag_id is None:
            tag_id = self.TagID
        return self._db_tag.is_valid_tag_id(tag_id=tag_id)

    def is_exist_TagName(self, tag_name: str = None) -> bool:
        if tag_name is None:
            tag_name = self.TagName

        for item in self.get_appv("tags").data:
            if item.TagName == tag_name:
                return True
        return False

    def load_tag_from_dict(self, tag_dict: dict) -> bool:
        required_fields = [
            TAG_INDEX_ID[1],
            TAG_INDEX_NAME[1],
            TAG_INDEX_USER_DEF[1],
            TAG_INDEX_DESC[1]
        ]

        if any(x not in tag_dict.keys() for x in required_fields):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Tag dictionary is incomplete.\nRequired fields: #3\ntag_dict fields: #4", ["Tag", "load_tag_from_dict", required_fields, tag_dict.keys()], exception_raised=True)
            raise ValueError("Tag dictionary does not contain all required keys.")

        self.data = self.get_empty_tag_dict()
        self.data[TAG_INDEX_ID[1]] = tag_dict[TAG_INDEX_ID[1]]
        self.data[TAG_INDEX_NAME[1]] = tag_dict[TAG_INDEX_NAME[1]]
        self.data[TAG_INDEX_USER_DEF[1]] = tag_dict[TAG_INDEX_USER_DEF[1]]
        self.data[TAG_INDEX_DESC[1]] = tag_dict[TAG_INDEX_DESC[1]]
        return True

    def to_dict(self) -> dict:
        return self.data

    def to_dict_unpacked(self) -> dict:
        return self.data

    def get_empty_tag_dict(self) -> dict:
        return {
            TAG_INDEX_ID[1]: None,
            TAG_INDEX_NAME[1]: "",
            TAG_INDEX_USER_DEF[1]: None,
            TAG_INDEX_DESC[1]: "",
            SAVED_FLAG: True
        }

    def _object_changed(self):
        self.data[SAVED_FLAG] = False

    def __str__(self) -> str:
        return f"Tag ID: {self.data[TAG_INDEX_ID[1]]}"

    def __eq__(self, other):
        if isinstance(other, Tag):
            if (self.data[TAG_INDEX_ID[1]] == other.data[TAG_INDEX_ID[1]]
                and self.data[TAG_INDEX_NAME[1]] == other.data[TAG_INDEX_NAME[1]]
                and self.data[TAG_INDEX_DESC[1]] == other.data[TAG_INDEX_DESC[1]]
                and self.data[TAG_INDEX_USER_DEF[1]] == other.data[TAG_INDEX_USER_DEF[1]]):
                return True
            else:
                return False
        else:
            return False    

    @property
    def TagID(self) -> int:
        return self.data[TAG_INDEX_ID[1]]
    
    @TagID.setter
    def TagID(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#!: Error in function #2. TagID property must be an integer.\ntype(value) = #3\nvalue = #4", ["Tag", "TagID.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The TagID property must be a integer. Passed '{str(type(value))}', expected 'int'")
        
        if self.data[TAG_INDEX_ID[1]] != value:
            self.data[TAG_INDEX_ID[1]] = value
            self._object_changed()

    @property
    def TagName(self) -> str:
        return self.data[TAG_INDEX_NAME[1]]
    
    @TagName.setter
    def TagName(self, value: str) -> None:
        if self.data[TAG_INDEX_NAME[1]] != str(value):
            self.data[TAG_INDEX_NAME[1]] = str(value)
            self._object_changed()
    
    @property
    def TagUserDefined(self) -> int:
        return self.data[TAG_INDEX_USER_DEF[1]]

    @TagUserDefined.setter
    def TagUserDefined(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#1: Error in function #2. TagUserDefined property must be an integer.\ntype(value) = #3\nvalue = #4", ["Tag", "TagUserDefined.setter", type(value), value], exception_raised=True)
            raise ValueError(f"The TagUserDefined property must be a integer. Passed '{str(type(value))}', expected 'int'")

        if isinstance(value, bool):
            if value:
                value = 1
            else:
                value = 0

        if self.data[TAG_INDEX_USER_DEF[1]] != value:
            self.data[TAG_INDEX_USER_DEF[1]] = value
            self._object_changed()

    @property
    def TagDescription(self) -> str:
        return self.data[TAG_INDEX_DESC[1]]
    
    @TagDescription.setter
    def TagDescription(self, value: str) -> None:
        if self.data[TAG_INDEX_DESC[1]] != str(value):
            self.data[TAG_INDEX_DESC[1]] = str(value)
            self._object_changed()











