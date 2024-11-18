from PyQt5.QtCore import QCoreApplication

from typing import Union, Any
import inspect
from datetime import datetime
import json
from datetime import datetime
import os

from utils_settings import UTILS_Settings
from log_viewer_cls import LogMessageViewer
from utils_text import TextUtility
from utils_signal import Signal


class LogHandler:
    """
    Log file contains list of dictionaries as log records.
    Each dictionary contains information about one log record.

    Each log record contains:
        id (str): Unique record identification
        date (str): Date of log record
        time (str): Time of log record
        log_name (str): Name of log file
        message (dict): Dictionary with information about message
            date (str): Date of message
            time (str): Time of message
            is_exception (bool): Is exception raised
            is_warning (bool): Is warning raised
            text (str): Text of message
            arguments (list): List of arguments
            call_stack (list): List of dictionaries with information functions call stack
                level (int): Function level in call stack
                function_name (str): Function name
                function_code (str): Function code
                file_name (str): File name
                line_number (int): Line number
                class_name (str): Class name


    """
    @staticmethod
    def show_log_viewer(parent_widget = None, **kwargs) -> LogMessageViewer:
        if parent_widget is not None:
            for child in parent_widget.children():
                if isinstance(child, LogMessageViewer):
                    return

        data = LogHandler.get_log_data()

        kwargs["theme"] = kwargs.get("theme", "dark")
        kwargs["size"] = kwargs.get("size", (630, 400))
        kwargs["position"] = kwargs.get("position", (100, 100))
        
        log_win = LogMessageViewer(
            parent_widget,
            source_messages=data,
            **kwargs
            )
        
        log_win.resize(kwargs["size"][0], kwargs["size"][1])

        position = kwargs.get("position")
        if position and len(position) == 2:
            log_win.move(position[0], position[1])
        
        if kwargs.get("run_exec", False):
            log_win.exec_()
        
        return log_win

    @staticmethod
    def get_log_file_path() -> str:
        return UTILS_Settings.LOG_FILE_PATH

    @staticmethod
    def get_log_max_records() -> int:
        return UTILS_Settings.LOG_MAX_RECORDS
    
    @staticmethod
    def get_log_data() -> dict:
        # Load log file
        if not os.path.isfile(LogHandler.get_log_file_path()):
            create_new_file = open(LogHandler.get_log_file_path(), "w", encoding="utf-8")
            data = {"messages": [], "data_map": []}
            json.dump(data, create_new_file, indent=2)
            create_new_file.close()
            return data

        try:
            with open(LogHandler.get_log_file_path(), "r", encoding="utf-8") as file:
                data = json.load(file)
        except:
            data = {"messages": [], "data_map": []}
        
        return data

    @staticmethod
    def add_log_record(message: str, arguments: list = None, exception_raised: bool = False, warning_raised: bool = False, start_new_log: bool = False, variables: list = None, extract_to_variables: dict = None) -> bool:
        if not start_new_log:
            if not UTILS_Settings.RECORD_NORMAL_LOGS and not warning_raised and not exception_raised:
                return False
            if not UTILS_Settings.RECORD_WARNING_LOGS and warning_raised:
                return False
            if not UTILS_Settings.RECORD_EXCEPTION_LOGS and exception_raised:
                return False

        record = {}
        # Load log file
        log_data = LogHandler.get_log_data()
        data = log_data.get("messages")
        data_map = log_data.get("data_map")
        
        def get_data_map_value(value: Any, data_map_data: list) -> int:
            for data_map_item in data_map_data:
                if data_map_item.get("value") == value:
                    return data_map_item.get("id", None)
            return None

        def add_to_data_map(value: Any, data_map_data: list) -> int:
            next_data_map_id: int = 0
            for data_map_item in data_map_data:
                next_data_map_id = max(next_data_map_id, data_map_item["id"])
            next_data_map_id += 1

            data_map_data.append({
                "id": next_data_map_id,
                "value": value
            })
            return next_data_map_id

        def fix_vars_memory_address(vars_list: list) -> list:
            replace_memory_address = " object in memory>"
            for idx, var_item in enumerate(vars_list):
                if len(var_item) == 3:
                    var = var_item[2]
                    pos = var.find(" object at ")
                    if pos != -1:
                        var = var[:pos] + replace_memory_address
                        vars_list[idx][2] = var
            
            return vars_list

        def get_extract_to_variable_item(extract_to_variable_item: Union[dict, list]) -> list:
            result = []
            if isinstance(extract_to_variable_item, list):
                if len(extract_to_variable_item) != 2 or not isinstance(extract_to_variable_item[1], dict):
                    return result
                extract_to_variable_prefix = extract_to_variable_item[0]
                extract_to_variable_item = extract_to_variable_item[1]
            else:
                extract_to_variable_prefix = ""
            
            if not isinstance(extract_to_variable_item, dict):
                return result
            
            for key, value in extract_to_variable_item.items():
                result.append([f"{extract_to_variable_prefix}[{key}]", TextUtility.shrink_text(str(value), 1000, replace_chars_map=[["\n", ";"]]), str(type(value))])
            
            return result

        # Find next ID and LogName and date
        next_log_id = 0
        current_log_name = ""
        active_date = datetime.now().strftime('%d.%m.%Y')
        current_date = datetime.now().strftime('%d.%m.%Y')
        active_time = datetime.now().strftime('%H:%M:%S')
        current_time = datetime.now().strftime('%H:%M:%S')
        for item in data:
            next_log_id = max(next_log_id, TextUtility.get_integer(item["id"], on_error_return=0))
            current_log_name = item["log_name"]
            active_date = item["date"]
            active_time = item["time"]
        next_log_id += 1

        record["id"] = str(next_log_id)

        if start_new_log:
            record["date"] = current_date
            record["time"] = current_time
            record["log_name"] = f"Log started at {current_time}"
        else:
            record["date"] = active_date
            record["time"] = active_time
            record["log_name"] = current_log_name
        
        record["message"] = {}

        record["message"]["date"] = current_date
        record["message"]["time"] = current_time
        record["message"]["is_exception"] = exception_raised
        record["message"]["is_warning"] = warning_raised
        record["message"]["text"] = message

        if not arguments:
            arguments = []
        if not isinstance(arguments, list):
            arguments = [arguments]
        for idx, argument in enumerate(arguments):
            arguments[idx] = str(argument)

        record["message"]["arguments"] = arguments

        func_frame = inspect.currentframe().f_back
        call_stack = []
        while func_frame:
            func_name = func_frame.f_code.co_name
            if func_name == "WarningMessage":
                func_frame = func_frame.f_back
                continue
            
            function_first_line_no = func_frame.f_code.co_firstlineno
            
            func_filename = func_frame.f_code.co_filename
            func_lineno = func_frame.f_lineno
            # Get content of line with line number func_lineno
            
            try:
                frame_source, _ = inspect.findsource(func_frame)
            except:
                frame_source = None
            
            if frame_source:
                func_content = frame_source
            else:
                func_content = []
            func_line_content = func_content[func_lineno - 1] if func_lineno > 1 and len(func_content) > func_lineno - 1 else "Cannot get content of line !"
            func_module = inspect.getmodule(func_frame).__name__ if inspect.getmodule(func_frame) else "None"
            func_class = func_frame.f_locals.get("self", None).__class__.__name__ if func_frame.f_locals.get("self", None) else "None"
            
            func_source_code, _ = inspect.getsourcelines(func_frame)
            func_source_code = "".join(func_source_code) if func_source_code else ""

            var_locals_raw = func_frame.f_locals if func_frame.f_locals else {}
            var_globals_raw = func_frame.f_globals if func_frame.f_globals else {}
            var_builtins_raw = func_frame.f_builtins if func_frame.f_builtins else {}

            var_locals = []
            var_globals = []
            var_builtins = []

            for key, item in var_locals_raw.items():
                var_locals.append([key, str(type(item)), TextUtility.shrink_text(str(item), 200, replace_chars_map=[["\n", ";"]])])
            for key, item in var_globals_raw.items():
                var_globals.append([key, str(type(item)), TextUtility.shrink_text(str(item), 200, replace_chars_map=[["\n", ";"]])])
            for key, item in var_builtins_raw.items():
                var_builtins.append([key, str(type(item)), TextUtility.shrink_text(str(item), 200, replace_chars_map=[["\n", ";"]])])
            
            var_locals = fix_vars_memory_address(var_locals)
            var_globals = fix_vars_memory_address(var_globals)
            var_builtins = fix_vars_memory_address(var_builtins)

            # Check save permissions
            if not UTILS_Settings.LOG_SAVE_LOCALS:
                var_locals = [["Local variables", "N/A", "Not saved"]]
            if not UTILS_Settings.LOG_SAVE_GLOBALS:
                var_globals = [["Global variables", "N/A", "Not saved"]]
            if not UTILS_Settings.LOG_SAVE_BUILTINS:
                var_builtins = [["Built-in variables", "N/A", "Not saved"]]
            if not UTILS_Settings.LOG_SAVE_MODULE_CODE:
                if not func_source_code.lower().strip().startswith(("def", "@", "async")):
                    func_source_code ="Code not saved"
                    # Dont show <module> variables
                    var_locals = [["Module local variables", "N/A", "Not saved"]]
                    var_globals = [["Module global variables", "N/A", "Not saved"]]
                    var_builtins = [["Module built-in variables", "N/A", "Not saved"]]
            if not UTILS_Settings.LOG_SAVE_FUNCTION_CODE:
                func_source_code ="Code not saved"

            # Retrieve data from data_map
            data_map_id = get_data_map_value(func_source_code, data_map)
            if data_map_id is None:
                func_source_code = add_to_data_map(func_source_code, data_map)
            else:
                func_source_code = data_map_id
            
            data_map_id = get_data_map_value(var_locals, data_map)
            if data_map_id is None:
                var_locals = add_to_data_map(var_locals, data_map)
            else:
                var_locals = data_map_id

            data_map_id = get_data_map_value(var_globals, data_map)
            if data_map_id is None:
                var_globals = add_to_data_map(var_globals, data_map)
            else:
                var_globals = data_map_id

            data_map_id = get_data_map_value(var_builtins, data_map)
            if data_map_id is None:
                var_builtins = add_to_data_map(var_builtins, data_map)
            else:
                var_builtins = data_map_id

            call_stack.append({
                "file_path": func_filename,
                "module": func_module,
                "class": func_class,
                "function_name": func_name,
                "function_code": func_source_code,
                "function_first_line_no": function_first_line_no,
                "line_content": func_line_content.strip(),
                "line_number": func_lineno,
                "locals": var_locals,
                "globals": var_globals,
                "builtins": var_builtins
            })
            func_frame = func_frame.f_back
        
        record["message"]["call_stack"] = call_stack
        
        variables_cleaned = []

        if not variables:
            variables = []

        for item in variables:
            if not isinstance(item, list) and not not isinstance(item, tuple):
                variables_cleaned.append(["Passed variable is not in expected (list, tuple) format.", str(type(item)), "N/A"])
            else:
                if len(item) == 0:
                    variables_cleaned.append(["Missing variable, passed empty list/tuple", "[]", "N/A"])
                elif len(item) == 1:
                    variables_cleaned.append(["Passed variable in wrong format LEN(list/tuple) = 1, expected 2" , str(item[0]), "N/A"])
                elif len(item) == 2:
                    variables_cleaned.append([str(item[0]), TextUtility.shrink_text(str(item[1]), 1000, replace_chars_map=[["\n", ";"]]), str(type(item[1]))])
                else:
                    variables_cleaned.append([f"Passed variable in wrong format LEN(list/tuple) = {len(item)}, expected 2", str(item[0], "N/A")])

        # Add extract_to_variables argument
        if extract_to_variables is not None:
            if isinstance(extract_to_variables, list) and isinstance(extract_to_variables[0], list):
                for item in extract_to_variables:
                    variables_cleaned.extend(get_extract_to_variable_item(item))
            else:
                variables_cleaned.extend(get_extract_to_variable_item(extract_to_variables))
        
        record["message"]["variables"] = variables_cleaned

        data.append(record)
        if len(log_data["messages"]) > LogHandler.get_log_max_records():
            log_data["messages"] = data[-LogHandler.get_log_max_records():]
        
        with open(LogHandler.get_log_file_path(), "w", encoding="utf-8") as file:
            json.dump(log_data, file, indent=2)
        
        if exception_raised and UTILS_Settings.POPUP_LOG_WINDOW_WHEN_EXCEPTION_IS_RAISED:
            LogHandler.show_log_viewer(parent_widget=None, run_exec=True)
        if warning_raised and UTILS_Settings.POPUP_LOG_WINDOW_WHEN_WARNING_IS_RAISED:
            can_show_log_window = True
            for i in UTILS_Settings.DONT_SHOW_LOG_WINDOW_WHEN_MESSAGE_STARTS_WITH:
                if message.startswith(i):
                    can_show_log_window = False
                    break
                if message.startswith("#1"):
                    if arguments and arguments[0] in UTILS_Settings.DONT_SHOW_LOG_WINDOW_WHEN_MESSAGE_STARTS_WITH:
                        can_show_log_window = False
                        break
            
            if can_show_log_window:
                LogHandler.show_log_viewer(parent_widget=None, run_exec=False)
        
        number_of_messages_for_last_log = 0
        for i in log_data["messages"]:
            if i["log_name"] == current_log_name:
                number_of_messages_for_last_log += 1

        Signal.emit_log_updated({"name": "LogHandler: add_log_record", "number_of_messages_in_last_log": number_of_messages_for_last_log}, log_data)
        QCoreApplication.processEvents()
        return True







