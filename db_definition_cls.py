import database_cls
import settings_cls


class Definition():
    def __init__(self, settings: settings_cls.Settings, def_id: int = None):
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.db_info = self._stt.app_setting_get_value("db_info")
        self._active_def_id = def_id
        
        if self._active_def_id:
            self._populate_properties()

    def get_list_of_all_expressions(self) -> list:
        """
        Returns list: [expresion, def_id]
        """
        q = "SELECT expression, definition_id FROM def_data ORDER BY definition_id ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        result = [x for x in result if x[0] != ""]
        return result

    def get_list_of_all_media_ids(self) -> list:
        """
        Returns list: [media_id, def_id]
        """
        q = "SELECT media_id, definition_id FROM def_data ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        result = [x for x in result if x[0] > 0]
        return result

    def get_list_of_all_definitions(self) -> list:
        q = "SELECT id, name FROM definition ORDER BY id ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    def get_list_of_all_definitions_and_descriptions(self) -> list:
        q = "SELECT id, name, description FROM definition ORDER BY id ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    def get_list_of_all_descriptions(self) -> list:
        q = "SELECT id, description FROM definition ORDER BY id ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        return result

    def find_definition_by_name(self, name: str, populate_properties: bool = True) -> int:
        """
        Returns definition ID or None
        """

        if not name:
            self.get_appv("log").write_log(f"Warrning: DB Definition. find_definition_by_name: {name}")
            return None
        
        name = name.lower()

        q = f"SELECT * FROM definition ;"
        with database_cls.DataBase(self.db_info) as db:
            db_result = db.execute(q)

        result = []
        for i in db_result:
            if i[1].lower() == name:
                result.append(i)

        if result:
            if populate_properties:
                self._populate_properties(result[0][0])
            return result[0][0]
        else:
            return None

    def add_new_definition(self, def_dict: dict):
        """ Adds a new expression definition
        def_dict: {}
            name (str):
            description (str):
            media_ids (list):
            synonyms (list):
            show (int):
            default (int):
        """
        
        def_dict["synonyms"].append(def_dict["name"].lower())
        
        syn_set = [x.strip().lower() for x in def_dict["synonyms"] if x.strip()]
        syn_set = set(syn_set)
        def_dict["synonyms"] = list(syn_set)

        q = f'INSERT INTO definition(name, description, show) VALUES (?, ?, {def_dict["show"]}) ;'
        with database_cls.DataBase(self.db_info) as db:
            new_id = db.execute(q, (def_dict["name"], def_dict["description"]), commit=True)
            
            q = f"INSERT INTO def_data(definition_id, expression, media_id, show, is_default) VALUES ({new_id}, ?, 0, 1, 0) ;"
            db.execute(query=q, param=def_dict["synonyms"], commit=True, execute_many=True)

            q = ""
            for item in def_dict["media_ids"]:
                q += f"INSERT INTO def_data(definition_id, expression, media_id, show, is_default) VALUES ({new_id}, '', {item}, 1, 0) ;\n"
            db.execute(q, commit=True, execute_many=True)

        self._active_def_id = new_id
        self._populate_properties(new_id)
        if "default" in def_dict:
            self.set_new_default_media(def_dict["default"])
        self.get_appv("log").write_log(f"DB Definition. add_new_definition. ID & Name: {new_id}, {def_dict['name']}")

    def _fix_definitions(self):
        return
        defs = self.get_list_of_all_definitions()

        for idx, item in enumerate(defs):
            def_dict = {}
            self._populate_properties(item[0])
            for i in range(len(self._synonyms)):
                self._synonyms[i] = self._synonyms[i].lower()
            def_dict["synonyms"] = list(self._synonyms)
            self.update_definition(def_id=item[0], def_dict=def_dict)
            print (f"Definition fixed: {item[0]}, {item[1]}  ...  {idx+1}/{len(defs)}")
        print ("Complete!")
    
    def update_definition(self, def_id: int, def_dict: dict):
        """ Adds a new expression definition
        def_dict: {}
            name (str):
            description (str):
            media_ids (list):
            synonyms (list):
            show (int):
            default (int):
        """

        self._populate_properties(def_id)
        default_media_id = self.default_media_id
        if "name" in def_dict:
            if def_dict["name"].lower() not in self._synonyms:
                self._synonyms.append(def_dict["name"].lower())
            self._name = def_dict["name"]
        if "description" in def_dict:
            self._description = def_dict["description"]
        if "media_ids" in def_dict:
            self._media_ids = def_dict["media_ids"]
        if "synonyms" in def_dict:
            def_dict["synonyms"].append(self._name.lower())
            def_dict["synonyms"] = set([x.strip().lower() for x in def_dict["synonyms"] if x.strip()])
            self._synonyms = list(def_dict["synonyms"])
        if "show" in def_dict:
            self._show = def_dict["show"]
        if "default" in def_dict:
            default_media_id = def_dict["default"]
            
        if not self._synonyms:
            self._synonyms.append(self._name.lower())
        
        q = f"UPDATE definition SET name = ?, description = ?, show = {self._show} WHERE id = {def_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            db.execute(q, (self._name, self._description), commit=True)
            q = f"DELETE FROM def_data WHERE definition_id = {def_id} ;"
            db.execute(q, commit=True)

            q = f"INSERT INTO def_data(definition_id, expression, media_id, show, is_default) VALUES ({def_id}, ?, 0, {self._show}, 0) ;"
            if self._synonyms:
                db.execute(query=q, param=self._synonyms, commit=True, execute_many=True)
            
            q = ""
            for item in self._media_ids:
                q += f"INSERT INTO def_data(definition_id, expression, media_id, show, is_default) VALUES ({def_id}, '', {item}, {self._show}, 0) ;\n"
            if q:
                db.execute(q.strip(), commit=True, execute_many=True)

        self.set_new_default_media(default_media_id)
        self.get_appv("log").write_log(f"DB Definition. update_definition. Name: {self._name}")

    def delete_definition(self, def_id: int = None) -> int:
        if def_id is None:
            def_id = self._active_def_id
        if def_id is None:
            raise ValueError("Definition ID is not specified.")
        
        q = f"DELETE FROM definition WHERE id = {def_id} ;"
        q2 = f"DELETE FROM def_data WHERE definition_id = {def_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q, commit=True)
            result2 = db.execute(q2, commit=True)
        if result != result2:
            self.get_appv("log").write_log(f"Error. DB Definition. delete_definition failed. ID: {def_id}")
            return False
        self.get_appv("log").write_log(f"DB Definition. delete_definition. ID: {def_id}")
        return result

    def _populate_properties(self, def_id: int = None) -> bool:
        if not def_id:
            def_id = self._active_def_id
        if not def_id:
            self.get_appv("log").write_log(f"Error. DB Definition. Loading failed. Definition ID: {def_id}")
            raise ValueError("Definition ID is not defined !")
        
        q = f"SELECT * FROM definition WHERE id = {def_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        
        if not result:
            return False
        
        self._active_def_id = def_id
        self._name = result[0][1]
        self._description = result[0][2]
        self._synonyms = self._get_definition_synonym(def_id)
        self._media_ids = self._get_definition_media_ids(def_id)
        self._show = result[0][3]
        
        return True

    def load_definition(self, definition_id: int) -> bool:
        return self._populate_properties(def_id=definition_id)

    def _get_definition_synonym(self, def_id: int) -> list:
        q = f"SELECT * FROM def_data WHERE definition_id = {def_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        syn = [x[2] for x in result if x[2] != ""]
        return syn
    
    def get_definition_media_synonyms_names(self, def_id: int) -> list:
        with database_cls.DataBase(self.db_info) as db:
            q = f"SELECT * FROM def_data WHERE definition_id = {def_id} ORDER BY expression ;"
            syn_list = db.execute(q)
        
        syn_names = []
        for item in syn_list:
            if item[2]:
                syn_names.append(item[2])
        
        return syn_names

    def _get_definition_media_ids(self, def_id: int) -> list:
        q = f"SELECT * FROM def_data WHERE definition_id = {def_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
        media_ids = [x[3] for x in result if x[3] != 0]
        return media_ids

    def set_new_default_media(self, media_id) -> bool:
        if media_id is None:
            self.get_appv("log").write_log(f"Warrning. DB Definition. set_new_default_media not set. Media ID: {media_id}")
            return
        q = f"UPDATE def_data SET is_default = 0 WHERE definition_id = {self._active_def_id} ;"
        q1 = f"UPDATE def_data SET is_default = 1 WHERE definition_id = {self._active_def_id} AND media_id = {media_id} ;"
        with database_cls.DataBase(self.db_info) as db:
            db.execute(q, commit=True)
            result = db.execute(q1, commit=True)
        
        self.get_appv("log").write_log(f"DB Definition. set_new_default_media. Media ID: {media_id}")
        if result:
            return True
        else:
            return False

    @property
    def default_media_id(self):
        q = f"SELECT * FROM def_data WHERE definition_id = {self._active_def_id} AND is_default = 1 ;"
        with database_cls.DataBase(self.db_info) as db:
            result = db.execute(q)
            if result:
                return result[0][3]
            else:
                return None

    @property
    def definition_id(self) -> int:
        return self._active_def_id
    
    @property
    def definition_name(self) -> str:
        return self._name
    
    @property
    def definition_description(self) -> str:
        return self._description

    @property
    def definition_synonyms(self) -> list:
        return self._synonyms

    @property
    def definition_media_ids(self) -> list:
        return self._media_ids


