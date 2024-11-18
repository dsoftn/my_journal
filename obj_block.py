from typing import Any, Union

from db_record_cls import Record
from db_record_data_cls import RecordData
from obj_constants import *
from obj_tags import Tags
from obj_tag import Tag
from obj_images import Images
from obj_image import Image
from obj_files import Files
from obj_file import File
import UTILS
import settings_cls


class Block:
    def __init__(self, settings: settings_cls.Settings, record_id: Union[int, str, 'Block'] = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Variables
        self._db_rec = Record(self._stt)
        self._db_rec_data = RecordData(self._stt)
        self.data = self.get_empty_block_dict()

        self._tags_obj: Tags = self.get_appv("tags")
        self._images_obj: Images = self.get_appv("images")
        self._files_obj: Files = self.get_appv("files")

        if record_id is not None:
            self.load_block(record_id=record_id)

    def load_block(self, record_id: Union[int, str, 'Block']) -> bool:
        if isinstance(record_id, str):
            record_id = UTILS.TextUtility.get_integer(record_id)
        if isinstance(record_id, Block):
            record_id = record_id.RecID
        if not self._db_rec.is_valid_record_id(rec_id=record_id):
            UTILS.LogHandler.add_log_record("#1: Block ID (#2) passed to method #3 does not exist!", ["Block", record_id, "load_block"], warning_raised=True)
            return False

        self._db_rec.load_record(record_id=record_id)
        rec_data = self._db_rec_data.get_record_data_dict(record_id=record_id)

        # Populate data
        self.data = self.get_empty_block_dict()
        self.data[REC_INDEX_ID[1]] = self._db_rec.RecordID
        self.data[REC_INDEX_NAME[1]] = self._db_rec.RecordName
        self.data[REC_INDEX_DATE[1]] = UTILS.DateTime.DateTimeObject(self._db_rec.RecordDate)
        self.data[REC_INDEX_DATE_INT[1]] = self._db_rec.RecordDateINT
        self.data[REC_INDEX_BODY[1]] = self._db_rec.RecordBody
        self.data[REC_INDEX_DRAFT[1]] = True if self._db_rec.RecordDraft else False
        self.data[REC_INDEX_CREATED_AT[1]] = UTILS.DateTime.DateTimeObject(self._db_rec.RecordCreatedAt)
        self.data[REC_INDEX_UPDATED_AT[1]] = UTILS.DateTime.DateTimeObject(self._db_rec.RecordUpdatedAt)
        self.data[REC_INDEX_BODY_HTML[1]] = self._db_rec.RecordBodyHTML
        self.data[REC_INDEX_TAGS[1]] = self._tags_obj.get_tag_list(rec_data["tag"])
        self.data[REC_INDEX_IMAGES[1]] = self._images_obj.get_image_list(rec_data["media"])
        self.data[REC_INDEX_FILES[1]] = self._files_obj.get_file_list(rec_data["files"])
        
        return True

    def new(self):
        """
        Clears all Block object properties
        """
        self.data = self.get_empty_block_dict()

    def add(self) -> int | None:
        """
        Add new block to database.
        Block object must have ID set to None.
        If block is successfully added returns block ID, else None
        """

        if self.data[REC_INDEX_ID[1]] is not None:
            UTILS.LogHandler.add_log_record("#1: Unable to add block. Reason: #2", ["Block", "In order to add block, block ID must be set to None"], warning_raised=True)
            return None
        
        if not self.RecDate:
            self.RecDate = UTILS.DateTime.DateTimeObject(UTILS.DateTime.DateTime.today())

        self.data[REC_INDEX_CREATED_AT[1]] = UTILS.DateTime.DateTime.now().DATE_TIME_formatted_string
        self.data[REC_INDEX_UPDATED_AT[1]] = UTILS.DateTime.DateTime.now().DATE_TIME_formatted_string
        self.RecDraft = True

        # Add Record
        rec_id = self._db_rec.add_new_record(
            body=self.RecBody,
            body_html=self.RecBodyHTML,
            date=self.RecDate.DATE_formatted_string,
            draft=int(self.RecDraft),
            name=self.RecName
        )

        if not rec_id:
            UTILS.LogHandler.add_log_record("#1: Unable to add block. Reason: #2", ["Block", "Error occurred in db_record_cls->Record->add_new_record"], warning_raised=True)
            return None
        
        # Add RecordData
        unpacked = self.to_dict_unpacked()
        rec_data_dict = {
            "tag": unpacked[REC_INDEX_TAGS[1]],
            "media": unpacked[REC_INDEX_IMAGES[1]],
            "files": unpacked[REC_INDEX_FILES[1]]
        }
        self._db_rec_data.update_record_data(
            data_dict=rec_data_dict,
            record_id=rec_id
        )

        self.load_block(rec_id)

        self.get_appv("blocks").signal_block_added(self)
        UTILS.Signal.emit_block_added(self.to_dict())
        return rec_id

    def can_be_added(self) -> bool:
        """
        Checks if block can be added to database.
        """

        if self.data[REC_INDEX_ID[1]] is not None:
            return False

        return True

    def save(self) -> bool:
        """
        Save/Update block.
        Block object must have valid ID.
        """

        if not self._db_rec.is_valid_record_id(self.RecID):
            UTILS.LogHandler.add_log_record("#1: Unable to save block. Block with ID=#2 does not exist.", ["Block", self.RecID], warning_raised=True)
            return None

        # Save Record
        self._db_rec.load_record(self.RecID)

        self._db_rec.RecordName = self.RecName
        self._db_rec.RecordDate = self.RecDate.DATE_formatted_string
        self._db_rec.RecordBody = self.RecBody
        self._db_rec.RecordBodyHTML = self.RecBodyHTML
        self._db_rec.RecordDraft = int(self.RecDraft)
        self._db_rec.RecordUpdatedAt = UTILS.DateTime.DateTime.now().DATE_TIME_formatted_string
        
        self._db_rec.save_record()

        # Save RecordData
        unpacked = self.to_dict_unpacked()
        rec_data_dict = {
            "tag": unpacked[REC_INDEX_TAGS[1]],
            "media": unpacked[REC_INDEX_IMAGES[1]],
            "files": unpacked[REC_INDEX_FILES[1]]
        }
        self._db_rec_data.update_record_data(
            data_dict=rec_data_dict,
            record_id=self.RecID
        )

        self.data[SAVED_FLAG] = True
        self.get_appv("blocks").signal_block_saved(self)
        UTILS.Signal.emit_block_saved(self.to_dict())
        return True

    def can_be_saved(self) -> bool:
        """
        Checks if block can be Saved/Updated.
        """

        if not self._db_rec.is_valid_record_id(self.RecID):
            return False
        
        return True

    def delete(self) -> int | None:
        """
        Deletes block.
        Block object must have valid ID.
        """

        if not self._db_rec.is_valid_record_id(self.RecID):
            UTILS.LogHandler.add_log_record("#1: Unable to delete block. Block with ID #2 does not exist.", ["Block", self.RecID], warning_raised=True)
            return None
        
        self._db_rec.delete_record(self.RecID)
        self._db_rec_data.delete_record_data(self.RecID)
        
        self.data[SAVED_FLAG] = None
        self.get_appv("blocks").signal_block_deleted(self)
        UTILS.Signal.emit_block_deleted(self.to_dict())
        return self.RecID

    def can_be_deleted(self) -> bool:
        """
        Checks if block can be deleted.
        """

        if not self._db_rec.is_valid_record_id(self.RecID):
            return False

        return True

    def is_exist_RecordID(self, rec_id: int = None) -> bool:
        if rec_id is None:
            rec_id = self.RecID
        return self._db_rec.is_valid_record_id(rec_id)

    def append_images_to_block(self, image_s: Union[int, str, Image, list, tuple, set]) -> bool:
        result = self.get_appv("images").get_image_list(image_s)
        if not result:
            UTILS.LogHandler.add_log_record("#1: No images found in function #2\nimage_s = #3", ["Block", "append_images_to_block", image_s], warning_raised=True)
            return False

        for item in result:
            if item.ImageID in [x.ImageID for x in self.RecImages]:
                UTILS.LogHandler.add_log_record("#1: Image with id #2 already exist in block.", ["Block", item.ImageID], warning_raised=True)
            else:
                self.data[REC_INDEX_IMAGES[1]].append(item)
        
        return True

    def append_files_to_block(self, file_s: Union[int, str, File, list, tuple, set]) -> bool:
        result = self.get_appv("files").get_file_list(file_s)
        if not result:
            UTILS.LogHandler.add_log_record("#1: No files found in function #2\nfile_s = #3", ["Block", "append_files_to_block", file_s], warning_raised=True)
            return False

        for item in result:
            if item.FileID in [x.FileID for x in self.RecFiles]:
                UTILS.LogHandler.add_log_record("#1: File with id #2 already exist in block.", ["Block", item.FileID], warning_raised=True)
            else:
                self.data[REC_INDEX_FILES[1]].append(item)

        return True

    def append_tags_to_block(self, tag_s: Union[int, str, Tag, list, tuple, set]) -> bool:
        result = self.get_appv("tags").get_tag_list(tag_s)
        if not result:
            UTILS.LogHandler.add_log_record("#1: No tags found in function #2\ntag_s = #3", ["Block", "append_tags_to_block", tag_s], warning_raised=True)
            return False

        for item in result:
            if item.TagID in [x.TagID for x in self.RecTags]:
                UTILS.LogHandler.add_log_record("#1: Tag with id #2 already exist in block.", ["Block", item.TagID], warning_raised=True)
            else:
                self.data[REC_INDEX_TAGS[1]].append(item)

        return True

    def load_block_from_dict(self, block_dict: dict) -> bool:
        def fix_list_field(field: Any, field_type: str, tags: Tags, images: Images, files: Files) -> list:
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
                    UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Cannot resolve block field #3\ntype(field) = #4\nfield = #5", ["Block", "load_block_from_dict->fix_list_field", field_type, type(field), field], exception_raised=True)
                    raise TypeError(f"Unable to resolve block field {field_type}.")
            
            if field_type == "tag" and isinstance(field, Tag):
                field = [field]
            elif field_type == "image" and isinstance(field, Image):
                field = [field]
            elif field_type == "file" and isinstance(field, File):
                field = [field]

            if not isinstance(field, list):
                UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Block field #3 must be a list.\ntype(field) = #4\nfield = #5", ["Block", "load_block_from_dict->fix_list_field", field_type, type(field), field], exception_raised=True)
                raise TypeError(f"Block field {field_type} must be a list.")
            
            result = []
            for item in field:
                if isinstance(item, str):
                    if UTILS.TextUtility.is_integer_possible(item):
                        item = [UTILS.TextUtility.get_integer(item)]
                    else:
                        UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Cannot resolve element in block field #3\ntype(item) = #4\nitem = #5", ["Block", "load_block_from_dict->fix_list_field", field_type, type(item), item], exception_raised=True)
                        raise TypeError(f"Unable to resolve element in block field {field_type}. Element: {item}")
                
                passed = False
                if field_type == "tag" and isinstance(item, Tag):
                    passed = True
                elif field_type == "image" and isinstance(item, Image):
                    passed = True
                elif field_type == "file" and isinstance(item, File):
                    passed = True
                
                if not isinstance(item, int) and not passed:
                    UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Cannot resolve element in block field #3\ntype(item) = #4\nitem = #5", ["Block", "load_block_from_dict->fix_list_field", field_type, type(item), item], exception_raised=True)
                    raise TypeError(f"Unable to resolve element in block field {field_type}. Element: {item}")
                
                result.append(item)
            
            if field_type == "tag":
                result = tags.get_tag_list(result)
            elif field_type == "image":
                result = images.get_image_list(result)
            elif field_type == "file":
                result = files.get_file_list(result)
            
            return result
            
        required_fields = [
            REC_INDEX_ID[1],
            REC_INDEX_NAME[1],
            REC_INDEX_DATE[1],
            REC_INDEX_BODY[1],
            REC_INDEX_DRAFT[1]
        ]

        if any(x not in block_dict.keys() for x in required_fields):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Block dictionary is incomplete.\nRequired fields: #3\nblock_dict fields: #4", ["Block", "load_block_from_dict", required_fields, block_dict.keys()], exception_raised=True)
            raise ValueError("Block dictionary does not contain all required keys.")

        tags: Tags = self.get_appv("tags")
        images: Images = self.get_appv("images")
        files: Files = self.get_appv("files")

        # Populate data
        self.data = self.get_empty_block_dict()
        self.data[REC_INDEX_ID[1]] = UTILS.TextUtility.get_integer(block_dict[REC_INDEX_ID[1]])
        self.data[REC_INDEX_NAME[1]] = str(block_dict[REC_INDEX_NAME[1]])
        self.data[REC_INDEX_DATE[1]] = UTILS.DateTime.DateTimeObject(block_dict[REC_INDEX_DATE[1]])
        self.data[REC_INDEX_DATE_INT[1]] = block_dict.get(REC_INDEX_DATE_INT[1], self.data[REC_INDEX_DATE[1]].DateToInteger)
        self.data[REC_INDEX_BODY[1]] = str(block_dict[REC_INDEX_BODY[1]])
        self.data[REC_INDEX_DRAFT[1]] = True if block_dict[REC_INDEX_DRAFT[1]] else False
        self.data[REC_INDEX_CREATED_AT[1]] = UTILS.DateTime.DateTimeObject(block_dict[REC_INDEX_CREATED_AT[1]]) if block_dict.get(REC_INDEX_CREATED_AT[1]) else UTILS.DateTime.DateTime.now()
        self.data[REC_INDEX_UPDATED_AT[1]] = UTILS.DateTime.DateTimeObject(block_dict[REC_INDEX_UPDATED_AT[1]]) if block_dict.get(REC_INDEX_UPDATED_AT[1]) else UTILS.DateTime.DateTime.now()
        self.data[REC_INDEX_BODY_HTML[1]] = str(block_dict.get(REC_INDEX_BODY_HTML[1], ""))
        self.data[REC_INDEX_TAGS[1]] = fix_list_field(block_dict.get(REC_INDEX_TAGS[1]), "tag", tags, images, files)
        self.data[REC_INDEX_IMAGES[1]] = fix_list_field(block_dict.get(REC_INDEX_IMAGES[1]), "image", tags, images, files)
        self.data[REC_INDEX_FILES[1]] = fix_list_field(block_dict.get(REC_INDEX_FILES[1]), "file", tags, images, files)
        
        return True

    def to_dict(self) -> dict:
        return self.data

    def to_dict_unpacked(self) -> dict:
        result = dict(self.data)
        result[REC_INDEX_DATE[1]] = self.RecDate.DATE_formatted_string
        result[REC_INDEX_DRAFT[1]] = 1 if self.RecDraft else 0
        result[REC_INDEX_CREATED_AT[1]] = self.RecCreatedAt.DATE_formatted_string
        result[REC_INDEX_UPDATED_AT[1]] = self.RecUpdatedAt.DATE_formatted_string
        result[REC_INDEX_TAGS[1]] = [x.TagID for x in self.RecTags]
        result[REC_INDEX_IMAGES[1]] = [x.ImageID for x in self.RecImages]
        result[REC_INDEX_FILES[1]] = [x.FileID for x in self.RecFiles]
        return result

    def get_empty_block_dict(self) -> dict:
        return {
            REC_INDEX_ID[1]: None,
            REC_INDEX_NAME[1]: "",
            REC_INDEX_DATE[1]: None,
            REC_INDEX_DATE_INT[1]: 0,
            REC_INDEX_BODY[1]: "",
            REC_INDEX_DRAFT[1]: None,
            REC_INDEX_CREATED_AT[1]: "",
            REC_INDEX_UPDATED_AT[1]: "",
            REC_INDEX_BODY_HTML[1]: "",
            REC_INDEX_TAGS[1]: [],
            REC_INDEX_IMAGES[1]: [],
            REC_INDEX_FILES[1]: [],
            SAVED_FLAG: True
        }

    def _object_changed(self):
        self.data[SAVED_FLAG] = False
        self.data[REC_INDEX_DRAFT[1]] = False

    def __str__(self) -> str:
        return f"Block ID: {self.data[REC_INDEX_ID[1]]}"

    def __eq__(self, other):
        if isinstance(other, Block):
            if (self.data[REC_INDEX_ID[1]] == other.data[REC_INDEX_ID[1]]
                and self.data[REC_INDEX_NAME[1]] == other.data[REC_INDEX_NAME[1]]
                and self.data[REC_INDEX_DATE[1]] == other.data[REC_INDEX_DATE[1]]
                and self.data[REC_INDEX_DATE_INT[1]] == other.data[REC_INDEX_DATE_INT[1]]
                and self.data[REC_INDEX_BODY[1]] == other.data[REC_INDEX_BODY[1]]
                and self.data[REC_INDEX_DRAFT[1]] == other.data[REC_INDEX_DRAFT[1]]
                and self.data[REC_INDEX_CREATED_AT[1]] == other.data[REC_INDEX_CREATED_AT[1]]
                and self.data[REC_INDEX_UPDATED_AT[1]] == other.data[REC_INDEX_UPDATED_AT[1]]
                and self.data[REC_INDEX_BODY_HTML[1]] == other.data[REC_INDEX_BODY_HTML[1]]
                and all(x in other[REC_INDEX_TAGS[1]] for x in self.data[REC_INDEX_TAGS[1]])
                and len(self.data[REC_INDEX_TAGS[1]]) == len(other.data[REC_INDEX_TAGS[1]])
                and all(x in self.data[REC_INDEX_IMAGES[1]] for x in other[REC_INDEX_IMAGES[1]])
                and len(self.data[REC_INDEX_IMAGES[1]]) == len(other.data[REC_INDEX_IMAGES[1]])
                and all(x in other[REC_INDEX_FILES[1]] for x in self.data[REC_INDEX_FILES[1]])
                and len(self.data[REC_INDEX_FILES[1]]) == len(other.data[REC_INDEX_FILES[1]])
            ):
                return True
            else:
                return False
        else:
            return False    

    @property
    def RecID(self) -> int:
        return self.data[REC_INDEX_ID[1]]
    
    @RecID.setter
    def RecID(self, value: int) -> None:
        if isinstance(value, str):
            if UTILS.TextUtility.is_integer_possible(value):
                value = UTILS.TextUtility.get_integer(value)
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. RecordID must be #3 or #4.\ntype(value) = #5\nvalue = #6", ["Block", "RecordID.setter", "integer", "None", type(value), value], exception_raised=True)
            raise TypeError("RecordID must me integer or none")
            
        if self.data[REC_INDEX_ID[1]] != value:
            self.data[REC_INDEX_ID[1]] = value
            self._object_changed()

    @property
    def RecName(self) -> str:
        return self.data[REC_INDEX_NAME[1]]

    @RecName.setter
    def RecName(self, value: str) -> None:
        if self.data[REC_INDEX_NAME[1]] != str(value):
            self.data[REC_INDEX_NAME[1]] = str(value)
            self._object_changed()

    @property
    def RecDate(self) -> UTILS.DateTime.DateTimeObject:
        return self.data[REC_INDEX_DATE[1]]
    
    @RecDate.setter
    def RecDate(self, value: str) -> None:
        if not UTILS.DateTime.DateTime.is_valid(value):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Not valid date.\ntype(value) = #3\nvalue = #4", ["Block", "RecordDate.setter", type(value), value], exception_raised=True)
            raise ValueError("Invalid date")

        result = UTILS.DateTime.DateTimeObject(value)

        if self.data[REC_INDEX_DATE[1]] != result:
            self.data[REC_INDEX_DATE[1]] = result
            self.data[REC_INDEX_DATE_INT[1]] = result.DateToInteger
            self._object_changed()
    
    @property
    def RecDateINT(self) -> int:
        return self.data[REC_INDEX_DATE_INT[1]]
    
    @property
    def RecBody(self) -> str:
        return self.data[REC_INDEX_BODY[1]]
    
    @RecBody.setter
    def RecBody(self, value: str) -> None:
        if value is None:
            value = ""

        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Body must be a string.\ntype(value) = #3\nvalue = #4", ["Block", "RecordBody.setter", type(value), value], exception_raised=True)
            raise ValueError("Block Body must be a string")
        
        if self.data[REC_INDEX_BODY[1]] != value:
            self.data[REC_INDEX_BODY[1]] = value
            self._object_changed()

    @property
    def RecDraft(self) -> bool:
        return self.data[REC_INDEX_DRAFT[1]]
    
    @RecDraft.setter
    def RecDraft(self, value: bool) -> None:
        if not isinstance(value, (bool, int)):
            UTILS.TerminalUtility.WarningMessage("#1: Exception in function #2. Draft must be a boolean.\ntype(value) = #3\nvalue = #4", ["Block", "RecordDraft.setter", type(value), value], exception_raised=True)
            raise ValueError("Block Draft must be a boolean")
        
        if self.data[REC_INDEX_DRAFT[1]] != bool(value):
            self._object_changed()
            self.data[REC_INDEX_DRAFT[1]] = bool(value)

    @property
    def RecCreatedAt(self) -> UTILS.DateTime.DateTimeObject | None:
        if self.data[REC_INDEX_CREATED_AT[1]]:
            return UTILS.DateTime.DateTimeObject(self.data[REC_INDEX_CREATED_AT[1]])
        else:
            return None

    @property
    def RecUpdatedAt(self) -> UTILS.DateTime.DateTimeObject | None:
        if self.data[REC_INDEX_UPDATED_AT[1]]:
            return UTILS.DateTime.DateTimeObject(self.data[REC_INDEX_UPDATED_AT[1]])
        else:
            return None

    @property
    def RecBodyHTML(self) -> str:
        return self.data[REC_INDEX_BODY_HTML[1]]

    @RecBodyHTML.setter
    def RecBodyHTML(self, value: str) -> None:
        if self.data[REC_INDEX_BODY_HTML[1]] != str(value):
            self.data[REC_INDEX_BODY_HTML[1]] = str(value)
            self._object_changed()

    @property
    def RecTags(self) -> list[Tag]:
        return self.data[REC_INDEX_TAGS[1]]
    
    @RecTags.setter
    def RecTags(self, tag_list: list) -> None:
        if isinstance(tag_list, str):
            tag_list = [tag_list]
        
        if self.data[REC_INDEX_TAGS[1]] != self._tags_obj.get_tag_list(tag_list):
            self.data[REC_INDEX_TAGS[1]] = self._tags_obj.get_tag_list(tag_list)
            self._object_changed()

    @property
    def RecImages(self) -> list[Image]:
        return self.data[REC_INDEX_IMAGES[1]]
    
    @RecImages.setter
    def RecImages(self, image_list: list) -> None:
        if isinstance(image_list, str):
            image_list = [image_list]

        if self.data[REC_INDEX_IMAGES[1]] != self._images_obj.get_image_list(image_list):
            self.data[REC_INDEX_IMAGES[1]] = self._images_obj.get_image_list(image_list)
            self._object_changed()

    @property
    def RecFiles(self) -> list[File]:
        return self.data[REC_INDEX_FILES[1]]
    
    @RecFiles.setter
    def RecFiles(self, file_list: list):
        if isinstance(file_list, str):
            file_list = [file_list]
        
        if self.data[REC_INDEX_FILES[1]] != self._files_obj.get_file_list(file_list):
            self.data[REC_INDEX_FILES[1]] = self._files_obj.get_file_list(file_list)
            self._object_changed()

