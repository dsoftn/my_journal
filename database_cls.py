import sqlite3
import os
import UTILS


class DBInfo():
    """Contains information about the database.
    It is used to pass information about the base between various classes.
    Database path, type, username, password...
    """
    def __init__(self, db_path: str, db_type: str, db_username: str = None, db_password: str = None):
        self._db_path = db_path
        self._db_type = db_type
        self._db_username = db_username
        self._db_password = db_password

    @property
    def DBPath(self) -> str:
        return self._db_path
    
    @property
    def DBType(self) -> str:
        return self._db_type.lower()

    @property
    def DBUserName(self) -> str:
        return self._db_username
    
    @property
    def DBPassword(self) -> str:
        return self._db_password
    

class DataBase():
    """Database connection.
    The connection for each type of database is programmed separately.
    The 'execute' method is used to send queries to the database.
    """
    def __init__(self, database_info: DBInfo):
        self.db_path = database_info.DBPath
        self.db_type = database_info.DBType
        self.db_username = database_info.DBUserName
        self.db_password = database_info.DBPassword
        self._make_connection()

    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, value, traceback):
        self.close_db()

    def _make_connection(self):
        if self.db_type == "sqlite" and self.db_path:
            if not os.path.isfile(self.db_path):
                UTILS.TerminalUtility.WarningMessage(f"Connection to #1 database failed.\nMissing file: #2", ["sqlite", self.db_path])
                raise FileNotFoundError(f"Connection to database failed. Missing file: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path)
            self.cur = self.conn.cursor()

    def execute(self, query: str, param: tuple = None, commit: bool = False, execute_many: bool = False) -> list:
        if not isinstance(self.conn, sqlite3.Connection):
            UTILS.TerminalUtility.WarningMessage("Database #1 object does not exist. Connection is not possible.\ntype(self.conn) = #2\nself.conn = #3", ["conn", type(self.conn), self.conn])
            raise ValueError("Database 'conn' object does not exist. Connection is not possible.")
        
        if self.db_type == "sqlite":
            if execute_many:
                if param is not None:
                    if not isinstance(param, list):
                        UTILS.TerminalUtility.WarningMessage("Parameter must be a list for execute_many.\ntype(param) = #1\nparam = #2", [type(param), param])
                        raise ValueError("Parameter must be a list for execute_many")
                if not commit:
                    UTILS.TerminalUtility.WarningMessage("Commit must be set to #1 for execute_many.\ncommit = #2", ["True", commit])
                    raise ValueError("Commit must be set to TRUE for execute_many")
                
                query_list = self._create_sql_list(query, param)
                if query_list:
                    for q in query_list:
                        if param:
                            self.cur.execute(q[0], q[1])
                        else:
                            self.cur.execute(q)
                    self.conn.commit()
                    return self.cur.lastrowid
                return None
            else:
                if param is not None:
                    if not isinstance(param, tuple):
                        self.cur.execute(query, (param,))
                    else:
                        self.cur.execute(query, param)
                else:
                    self.cur.execute(query)
                if commit:
                    self.conn.commit()
                    return self.cur.lastrowid
                return self.cur.fetchall()
        UTILS.TerminalUtility.WarningMessage("Database type not recognized. Connection is not possible.\nself.db_type = #1", [self.db_type])
        raise ValueError("Database type not recognized. Connection is not possible.")

    def _create_sql_list(self, query: str, param: list) -> list:
        query_list = []
        if not param:
            if isinstance(query, list):
                return query
            if isinstance(query, str):
                query_list = [x for x in query.splitlines() if x.strip()]
                return query_list
            return None
        
        if not isinstance(query, str):
            return None
        
        query_list = []
        for par in param:
            if isinstance(par, str):
                par = (par, )
            elif isinstance(par, list):
                if len (par) == 1:
                    par = (par[0], )
                else:
                    par = tuple(par)
            else:
                UTILS.TerminalUtility.WarningMessage("Param must be a tuple or list of tuples.\ntype(param) = #1\nparam = #2", [type(param), param])
                raise TypeError("Param must be a tuple or list of tuples")
            
            par_list = [x for x in par if x is not None]
            if len(par_list) != query.count("?"):
                UTILS.TerminalUtility.WarningMessage("Number of items in parameter tuple does not match number of question marks in query.\ntype(param) = #1\nparam = #2\nquery = #3\nlen(param) = #4\nNumber of question marks in query = #5", [type(param), param, query, len(par_list), query.count("?")])
                raise ValueError("Number of items in parameter tuple does not match number of question marks in query")
            
            query_list.append([query, par])
        return query_list

    def create_new_database(self, database_info: DBInfo, creation_sql: str):
        db_path = database_info.DBPath
        db_type = database_info.DBType
        db_username = database_info.DBUserName
        db_password = database_info.DBPassword

        if db_type.lower() == "sqlite":
            """Creates a new, empty database.
            Note: This method will delete the old database with the same name !!!
            """
            self.db_path = db_path
            self.db_type = db_type.lower()
            self.db_username = db_username
            self.db_password = db_password
            self._create_directory_structure(self.db_path)
            self._make_connection()
            if creation_sql:
                for q in creation_sql.split("\n"):
                    self.cur.execute(q)
                self.conn.commit()

    def _create_directory_structure(self, path: str, create_file: bool = True) -> bool:
        path_split = os.path.split(path)
        path_dir = path_split[0]
        path_file = path_split[1]
        if path_dir:
            if not os.path.isdir(path_dir):
                os.mkdir(path_dir)
        if create_file:
            if path_file:
                file = open (path, "w", encoding="utf-8")
                file.close()
                return True
            else:
                return False
        return True

    def close_db(self):
        if self.db_type == "sqlite":
            self.conn.close()







    