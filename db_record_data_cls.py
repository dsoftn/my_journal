import database_cls
import settings_cls
import db_media_cls
import UTILS


class RecordData():
    def __init__(self, settings: settings_cls.Settings, record_id: int = None):
        self._stt = settings
        self._active_record_id = record_id
        self.db_info = self._stt.app_setting_get_value("db_info")

    def get_record_data(self, record_id: int = None) -> list:
        if record_id is None:
            record_id = self._active_record_id
        with database_cls.DataBase(self.db_info) as db:
            q = f"SELECT * FROM data WHERE record_id = {record_id} ;"
            result = db.execute(q)
        return result

    def get_all_record_data(self) -> list:
        with database_cls.DataBase(self.db_info) as db:
            q = f"SELECT * FROM data ORDER BY record_id;"
            result = db.execute(q)
        return result

    def get_tags_and_media_for_all_records(self):
        """ [   record_id, 
                [list(tag_id)], 
                list[media_id] 
            ]
        """
        q = f"SELECT * FROM data ORDER BY record_id;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        output = []
        last_rec = None
        item = {
            "rec_id": None,
            "tags": [],
            "media": []
        }

        for data in result:
            if data[1] != last_rec:
                if item["rec_id"]:
                    output.append([item["rec_id"], item["tags"], item["media"]])
                    item = {
                        "rec_id": None,
                        "tags": [],
                        "media": []
                    }

            if item["rec_id"] is None:
                item["rec_id"] = data[1]

            if data[2]:
                item["tags"].append(data[2])
            if data[3]:
                item["media"].append(data[3])
            
            last_rec = data[1]
            
        if item["rec_id"]:
            output.append([item["rec_id"], item["tags"], item["media"]])
        
        return output

    def get_record_ids_with_images(self) -> set:
        q = f"SELECT * FROM data WHERE media_id > 0 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return set([x[1] for x in result])

    def get_record_data_field_values(self, field_name: str, record_id: int = 0) -> list:
        if record_id == 0:
            record_id = self._active_record_id
        db = database_cls.DataBase(self.db_info)
        q = f"SELECT * FROM data WHERE record_id = {record_id} AND {field_name} > 0 ;"
        result = db.execute(q)
        db.close_db()
        return result

    def get_record_data_dict(self, record_id: int = 0, merge_with_dict: dict = None) -> dict:
        if record_id == 0:
            record_id = self._active_record_id
        if merge_with_dict:
            rec_dict = merge_with_dict
        else:
            rec_dict = self._empty_record_data_dict()
        data = self.get_record_data(record_id)
        db_media = db_media_cls.Files(self._stt)
        files_id = [x[0] for x in db_media.get_all_file()]

        for item in data:
            if item[2]:
                rec_dict["tag"].append(item[2])

            if item[3]:
                if item[3] in files_id:
                    rec_dict["files"].append(item[3])
                else:
                    rec_dict["media"].append(item[3])

        # for key in rec_dict:
        #     rec_dict[key] = [x for x in rec_dict[key] if x != 0]
        return rec_dict

    def update_record_data(self, data_dict: dict, record_id: int = 0, overwrite_old_data: bool = True):
        if record_id == 0:
            record_id = self._active_record_id
        if overwrite_old_data:
            UTILS.LogHandler.add_log_record("#1: Overwriting old record data. (ID=#2)", ["RecordData", record_id])
            self.delete_record_data(record_id)
            rec_dict = self.get_record_data_dict(record_id, merge_with_dict=data_dict)
        else:
            rec_dict = data_dict
        
        with database_cls.DataBase(self._stt.app_setting_get_value("db_info")) as db:
            for i in range(len(rec_dict["tag"])):
                q = f"INSERT INTO data (record_id, tag_id) VALUES ({record_id},{rec_dict['tag'][i]}) ;"
                db.execute(q, commit=True)
            for i in range(len(rec_dict["media"])):
                q = f"INSERT INTO data (record_id, media_id) VALUES ({record_id},{rec_dict['media'][i]}) ;"
                db.execute(q, commit=True)
            for i in range(len(rec_dict["files"])):
                q = f"INSERT INTO data (record_id, media_id) VALUES ({record_id},{rec_dict['files'][i]}) ;"
                db.execute(q, commit=True)
        UTILS.LogHandler.add_log_record("#1: Block record data updated. (ID=#2)", ["RecordData", record_id])

    def delete_record_data(self, record_id: int = None) -> None:
        if not record_id:
            record_id = self._active_record_id
        if not record_id:
            UTILS.TerminalUtility.WarningMessage("An attempt was made to delete an undefined recordID.\nrecord_id = #1", [record_id], exception_raised=True)
            raise ValueError("An attempt was made to delete an undefined recordID.")
        q = f"DELETE FROM data WHERE record_id = {record_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            db.execute(q, commit=True)
        UTILS.LogHandler.add_log_record("#1: Block record data deleted. (ID=#2)", ["RecordData", record_id])
        
    def _empty_record_data_dict(self) -> dict:
        result = {}
        result["tag"] = []
        result["media"] = []
        result["files"] = []
        return result
