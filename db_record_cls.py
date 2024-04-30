import database_cls
import settings_cls
import utility_cls
import UTILS


class Record():
    """It contains all the information about the record in the 'record' table.
    """
    def __init__(self, settings: settings_cls.Settings, record_id: int = 0):
        self._active_id = record_id
        self._stt = settings
        self.get_appv = self._stt.app_setting_get_value
        self.db_info = self._stt.app_setting_get_value("db_info")
        self.getv = self._stt.get_setting_value
        self.load_record()

    def get_date_of_first_entry(self) -> str:
        q = "SELECT date, MIN(date_int) FROM record ;"
        db = database_cls.DataBase(self.db_info)
        result = db.execute(q)
        db.close_db()
        return result[0][0]

    def get_empty_body_records(self) -> list:
        q = "SELECT * FROM record WHERE body = '' ;"
        db = database_cls.DataBase(self.db_info)
        result = db.execute(q)
        db.close_db()
        return result

    def get_draft_records(self) -> list:
        q = "SELECT * FROM record WHERE draft > 0 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    def is_valid_record_id(self, rec_id: int) -> bool:
        q = f"SELECT * FROM record WHERE id = {rec_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        if result:
            return True
        else:
            return False

    def get_all_records(self, record_id: int = None, sort_by_date: bool = True, sort_by_id: bool = False) -> list:
        if record_id is None:
            condition = ""
        else:
            condition = f" WHERE id = {record_id}"

        if sort_by_date:
            q = f"SELECT * FROM record{condition} ORDER BY date_int ;"
        if sort_by_id:
            q = f"SELECT * FROM record{condition} ORDER BY id ;"
        else:
            q = f"SELECT * FROM record{condition} ;"
        
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    def _populate_variables(self, record_fetched: list) -> bool:
        if len(record_fetched) != 1:
            return False
        self._active_id = record_fetched[0][0]
        self._record_name = record_fetched[0][1]
        self._record_date = record_fetched[0][2]
        self._record_date_int = record_fetched[0][3]
        self._record_body = record_fetched[0][4]
        self._record_draft = record_fetched[0][5]
        self._record_created_at = record_fetched[0][6]
        self._record_updated_at = record_fetched[0][7]
        self._record_body_html = record_fetched[0][8]

        self.get_appv("log").write_log(f"DB Record. Record opened. Record ID: {self._active_id}")

    def load_record(self, record_id: int = 0):
        # If 'record_id' is not specified, try loading 'self._active_id'
        if record_id == 0:
            if self._active_id == 0:
                return
            else:
                record_id = self._active_id
        self._active_id = record_id
        # Load record and set activeID to that record
        q = f"SELECT * FROM record WHERE id = {record_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        self._populate_variables(result)
    
    def save_record(self):
        q = f"""
        UPDATE
            record
        SET
            name = ?,
            date = '{self._record_date}',
            date_int = {self._record_date_int},
            body = ?,
            draft = {self._record_draft},
            updated_at = '{self._record_updated_at}',
            body_html = ?
        WHERE
            id = {self._active_id}
        ;
        """
        with database_cls.DataBase(self.db_info) as db:
            db.execute(q, param=(self._record_name, self._record_body, self._record_body_html), commit=True)
        UTILS.LogHandler.add_log_record("#1: Block record updated. (ID=#2)", ["Record", self._active_id], variables=[["Name", self._record_name], ["Date", self._record_date], ["Body", self._record_body], ["Draft", self._record_draft], ["Updated_at", self._record_updated_at], ["Body_HTML", self._record_body_html]])
        self.get_appv("log").write_log(f"DB Record. Record saved. Record ID: {self._active_id}")

    def delete_record(self, record_id: int = None) -> None:
        if not record_id:
            record_id = self._active_id
        if not record_id:
            self.get_appv("log").write_log(f"Error. DB Record. delete_record. Record ID: {self._active_id}")
            UTILS.TerminalUtility.WarningMessage("Error. Record ID not defined. Cannot delete record.\nrecord_id = #1\nself._active_id = #2", [record_id, self._active_id], exception_raised=True)
            raise ValueError("An attempt was made to delete an undefined recordID.")

        q = f"DELETE FROM record WHERE id = {record_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            db.execute(q, commit=True)
        UTILS.LogHandler.add_log_record("#1: Block record deleted. (ID=#2)", ["Record", self._active_id])
        self.get_appv("log").write_log(f"DB Record. Record deleted. Record ID: {self._active_id}")

    def add_new_record(self, body: str, body_html: str, date: str = "", draft: int = 1, name: str = "") -> int:
        dt = utility_cls.DateTime(self._stt)
        date_dict = dt.make_date_dict(date)
        rec_name = name
        rec_date = date_dict["date"]
        rec_date_int = date_dict["date_int"]
        rec_body = body
        rec_body_html = body_html
        rec_draft = draft
        rec_created_at = dt.get_current_date_and_time(with_long_names=False)
        rec_updated_at = rec_created_at

        q = f"""INSERT INTO record (
                    name,
                    date,
                    date_int,
                    body, 
                    draft,
                    created_at,
                    updated_at,
                    body_html  )
                VALUES
                    (
                    ?,
                    '{rec_date}',
                    {rec_date_int},
                    ?,
                    {rec_draft},
                    '{rec_created_at}',
                    '{rec_updated_at}',
                    ? )
                    ;
                """
        db = database_cls.DataBase(self.db_info)
        last_row_id = db.execute(q, (rec_name, rec_body, rec_body_html), commit=True)
        self.load_record(last_row_id)
        db.close_db()
        UTILS.LogHandler.add_log_record("#1: Block record added. (ID=#2)", ["Record", last_row_id], variables=[["Name", self._record_name], ["Date", self._record_date], ["Body", self._record_body], ["Draft", self._record_draft], ["Updated_at", self._record_updated_at], ["Body_HTML", self._record_body_html]])
        self.get_appv("log").write_log(f"DB Record. Record added. Record ID: {last_row_id}")
        return last_row_id

    def count_chars(self) -> int:
        return len(self._record_body)

    def count_words(self) -> int:
        words = [x for x in self._record_body.split(" ") if x != ""]
        return len(words)

    @property
    def RecordID(self) -> int:
        return self._active_id
    
    @property
    def RecordName(self) -> str:
        return self._record_name

    @RecordName.setter
    def RecordName(self, value: str) -> None:
        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("Error. RecordName property must be a string.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordName property must be a string. Passed '{str(type(value))}', expected 'str'")
        self._record_name = value

    @property
    def RecordDate(self) -> str:
        return self._record_date

    @RecordDate.setter
    def RecordDate(self, value: str) -> None:
        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("Error. RecordDate property must be a string.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordDate property must be a string. Passed '{str(type(value))}', expected 'str'")
        dt = utility_cls.DateTime(self._stt)
        date_dict = dt.make_date_dict(value)
        self._record_date = date_dict["date"]
        self._record_date_int = date_dict["date_int"]
    
    @property
    def RecordDateINT(self) -> int:
        return self._record_date_int
    
    @property
    def RecordBody(self) -> str:
        return self._record_body

    @RecordBody.setter
    def RecordBody(self, value: str) -> None:
        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("Error. RecordBody property must be a string.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordBody property must be a string. Passed '{str(type(value))}', expected 'str'")
        self._record_body = value

    @property
    def RecordBodyHTML(self) -> str:
        return self._record_body_html

    @RecordBodyHTML.setter
    def RecordBodyHTML(self, value: str) -> None:
        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("Error. RecordBodyHTML property must be a string.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordBodyHTML property must be a string. Passed '{str(type(value))}', expected 'str'")
        self._record_body_html = value

    @property
    def RecordDraft(self) -> int:
        return self._record_draft

    @RecordDraft.setter
    def RecordDraft(self, value: int) -> None:
        if not isinstance(value, int):
            UTILS.TerminalUtility.WarningMessage("Error. RecordDraft property must be an integer.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordDraft property must be a integer. Passed '{str(type(value))}', expected 'int'")
        self._record_draft = value

    @property
    def RecordCreatedAt(self) -> str:
        return self._record_created_at

    @RecordCreatedAt.setter
    def RecordCreatedAt(self, value: str) -> None:
        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("Error. RecordCreatedAt property must be a string.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordCreatedAt property must be a string. Passed '{str(type(value))}', expected 'str'")
        self._record_created_at = value

    @property
    def RecordUpdatedAt(self) -> str:
        return self._record_updated_at

    @RecordUpdatedAt.setter
    def RecordUpdatedAt(self, value: str) -> None:
        if not isinstance(value, str):
            UTILS.TerminalUtility.WarningMessage("Error. RecordUpdatedAt property must be a string.\ntype(value) = #1\nvalue = #2", [type(value), value], exception_raised=True)
            raise ValueError(f"The RecordUpdatedAt property must be a string. Passed '{str(type(value))}', expected 'str'")
        self._record_updated_at = value
