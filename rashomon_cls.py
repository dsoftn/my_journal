import os
import json
import urllib.request
import requests
import html as HtmlLib

import UTILS


class Data():
    COLOR_COMMENT = "#aaff7f"
    COLOR_BLOCK = "#007e00"
    COLOR_KEYWORD = "#d4ff82"
    COLOR_CONDITION = "#66ce99"
    COLOR_OPERATOR = "#ff557f"
    COLOR_CONTAINER = "#aa5500"
    COLOR_STRING = "#bdb7ff"

    EXTRA_COLOR_RULES = [
        ["If", "#c8c896"],
        ["EndIf", "#c8c896"],
        ["BeginSegment", "#0055ff"],
        ["EndSegment", "#0055ff"]
    ]

    def __init__(self) -> None:
        self.CommandLineText = None
        self.CommandLineNumber = None
        self.Code = None

        self.Command = None
        self.Description = None
        self.Example = None
        self.Not = None
        self.CommandType = None
        self.Argument = None
        self.Conditions = None

        self.Valid = None
        self.Value = None
        self.Segment = None
        self.Text = None
        self.Selection = None

        self.AutoCompleteLine = None
        self.AutoCompleteCursorPosition = None
        self.ColorMap = None

class AbstractCommand():
    CONTAINERS = [
        ['"', '"', '"'],
        ["'", "'", "'"],
        ["|", "|", "|"],
        ["`", "`", "`"]
    ]
    BLOCK = 0
    KEYWORD = 1
    COMMENT = 2
    CONDITION = 3
    OPERATOR = 4

    COMMANDS_CONDITIONS = [
        "StartString",
        "EndString",
        "ContainsString",
        "If"
        ]
    COMMANDS_OPERATOR = [
        "And",
        "Or",
        "Not"
    ]
    COMMANDS_BLOCK = [
        "BeginSegment",
        "EndSegment",
        "DefineStartString",
        "EndDefineStartString",
        "DefineEndString",
        "EndDefineEndString",
        "If",
        "EndIf"
    ]
    COMMANDS_KEYWORD = [
        "Parent",
        "Index",
        "MatchCase",
        "IsEqual",
        "StartsWith",
        "EndsWith"
    ]

    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self._command_line: str = code.split("\n")[line_number]
        self._code = code
        self._line_number = line_number
        self._text = text
        self._selection = selection

        self.data = Data()

    def is_valid(self):
        UTILS.TerminalUtility.WarningMessage("Error. Function has not been implemented yet.", exception_raised=True)
        raise NotImplementedError("Error. Function has not been implemented yet.")
    
    def value(self):
        UTILS.TerminalUtility.WarningMessage("Error. Function has not been implemented yet.", exception_raised=True)
        raise NotImplementedError("Error. Function has not been implemented yet.")

    def selection(self):
        UTILS.TerminalUtility.WarningMessage("Error. Function has not been implemented yet.", exception_raised=True)
        raise NotImplementedError("Error. Function has not been implemented yet.")

    def execute(self):
        UTILS.TerminalUtility.WarningMessage("Error. Function has not been implemented yet.", exception_raised=True)
        raise NotImplementedError("Error. Function has not been implemented yet.")
    
    def _has_container(self, command_text: str) -> bool:
        txt = command_text
        delimiters = self.CONTAINERS
        
        in_container = False
        found_container = False
        start_delim = [x[0] for x in delimiters]
        end_delim = [x[1] for x in delimiters]
        container_type = None
        for char in txt:
            if char in start_delim and not in_container:
                container_type = start_delim.index(char)
                in_container = True
                continue
            
            if not in_container:
                continue

            if char == end_delim[container_type]:
                found_container = True
                break
            
        if found_container:
            return True
        else:
            return False

    def _get_simple_value(self, txt: str) -> str:
        pos = txt.find("=")
        if pos == -1:
            return None
        
        result = txt[pos:].strip()
        return result
    
    def _text_in_container(self, txt: str, delimiter: str = None) -> str:
        if delimiter:
            if isinstance(delimiter, str):
                for i in self.CONTAINERS:
                    if i[2] == delimiter:
                        delimiters = [i]
                        break
                else:
                    delimiters_list = ", ".join([x[2] for x in self.CONTAINERS])
                    raise ValueError(f"Unknown delimiter: {delimiter}   Allowed delimiters are : {delimiters_list}")
            elif isinstance(delimiter, list) or isinstance(delimiter, tuple):
                delimiters = delimiter
            else:
                UTILS.TerminalUtility.WarningMessage("Error. Unknown delimiter: #1\nCustom delimiter must be list or tuple. [#2, #3, #4]\ntype(delimiter): #5\ndelimiter = #6", [delimiter, "start", "end", "name", type(delimiter), delimiter], exception_raised=True)
                raise ValueError(f"Unknown delimiter: {delimiter}   Custom delimiter must be list or tuple. ['start', 'end', 'name']")
        else:
            delimiters = self.CONTAINERS
        
        result = ""
        in_container = False
        found_container = False
        start_delim = [x[0] for x in delimiters]
        end_delim = [x[1] for x in delimiters]
        container_type = None
        for char in txt:
            if char in start_delim and not in_container:
                container_type = start_delim.index(char)
                in_container = True
                continue
            
            if not in_container:
                continue

            if char == end_delim[container_type]:
                found_container = True
                break
            
            if in_container:
                result += char

        if found_container:
            return result
        else:
            return None

    def _get_if_conditions(self, if_command: str) -> dict:
        if_command = if_command.lstrip()
        if_resolved = {
            "valid": False,
            "command_line": if_command,
            "conditions": None,
            "eval_text": None
        }
        if not if_command.startswith("If"):
            return if_resolved
        
        delimiters = self.CONTAINERS
        start_delim = [x[0] for x in delimiters]
        end_delim = [x[1] for x in delimiters]
        container_type = None
        
        conditions = []
        txt = f" {if_command[3:]} "
        txt_con = ""
        container_content = ""
        command = ""
        pos = 0
        is_if_valid = True
        negative_command = False
        in_container = False
        prev_command = None
        while True:
            if pos >= len(txt):
                break

            i = txt[pos]

            if i in start_delim and not in_container:
                container_type = start_delim.index(i)
                in_container = True
                pos += 1
                continue
            if in_container:
                if i == end_delim[container_type]:
                    in_container = False
                    if not command:
                        if prev_command:
                            command = prev_command
                        else:
                            is_if_valid = False
                            break
                    else:
                        prev_command = command

                    conditions.append([command, container_content, negative_command])
                    negative_command = False
                    container_content = ""
                    command = ""
                    txt_con += f" CON[{len(conditions)-1}] "
                    pos += 1
                    continue
                else:
                    container_content += i
                    pos += 1
                    continue

            if i in " =":
                if not command:
                    pos += 1
                    continue

                if command.capitalize() in self.COMMANDS_OPERATOR:
                    if command.lower() == "not":
                        negative_command = True
                    txt_con += f" {command.lower()} "
                    pos += 1
                    command = ""
                    continue

            if i in "() ":
                txt_con += i
                pos += 1
                continue

            command += i
            command = command.strip(" =")
            pos += 1

        if in_container:
            is_if_valid = False
        
        for i in self.COMMANDS_CONDITIONS:
            txt_con = txt_con.replace(i, " ")
        
        if_resolved["valid"] = is_if_valid
        if_resolved["command_line"] = if_command
        if_resolved["conditions"] = conditions
        if_resolved["eval_text"] = txt_con

        return if_resolved

    def _is_if_condition_syntax_valid(self, if_command: str) -> bool:
        if_command = if_command.lstrip()
        result = self._get_if_conditions(if_command=if_command)
        if result["valid"]:
            return True
        else:
            return False

    def _get_segment_name(self) -> str:
        txt_list = self._code.split("\n")
        pos = self._line_number
        if pos >= len(txt_list):
            return None
        
        while pos >= 0:
            if txt_list[pos].startswith("BeginSegment"):
                if self._has_container(txt_list[pos]):
                    return self._text_in_container(txt_list[pos])
                else:
                    return None
            pos -= 1
        return None

    def _get_color_map_for_simple_command(self) -> list:
        delimiters = self.CONTAINERS
        
        result = []
        in_container = False
        found_container = None
        start_delim = [x[0] for x in delimiters]
        end_delim = [x[1] for x in delimiters]
        container_type = None
        pos = 0
        old_pos = 0
        txt = self._command_line + " "
        command = ""
        invalid_command_color = "#b4b4b4"
        found_command = False
        operators_lower = [x.lower() for x in self.COMMANDS_OPERATOR]
        commands_list = [
            [self.COMMANDS_CONDITIONS, self.data.COLOR_CONDITION],
            [self.COMMANDS_KEYWORD, self.data.COLOR_KEYWORD],
            [self.COMMANDS_BLOCK, self.data.COLOR_BLOCK],
            [self.COMMANDS_OPERATOR, self.data.COLOR_OPERATOR],
            [operators_lower, self.data.COLOR_OPERATOR]
        ]
        
        while True:
            if pos >= len(txt):
                break

            char = txt[pos]

            if char in start_delim and not in_container:
                container_type = start_delim.index(char)
                found_container = pos
                in_container = True
                pos += 1
                continue
            
            if in_container and char == end_delim[container_type]:
                result.append([found_container, found_container+1, self.data.COLOR_CONTAINER])
                result.append([found_container+1, pos, self.data.COLOR_STRING])
                result.append([pos, pos+1, self.data.COLOR_CONTAINER])
                found_container = None
                in_container = False
                pos += 1
                old_pos = pos
                continue

            if in_container:
                pos += 1
                continue

            if char in "()= \n\t" and command.strip():
                for item in self.data.EXTRA_COLOR_RULES:
                    if command.strip() == item[0]:
                        result.append([old_pos, pos, item[1]])
                        old_pos = pos
                        found_command = True
                        break

                if not found_command:
                    for item in commands_list:
                        for i in item[0]:
                            if command.strip() == i:
                                result.append([old_pos, pos, item[1]])
                                found_command = True
                                old_pos = pos
                if not found_command:
                    result.append([old_pos, pos, invalid_command_color])
                    old_pos = pos
                else:
                    found_command = False
                command = ""

            if char in "()=":
                result.append([old_pos, pos + 1, self.data.COLOR_CONTAINER])
                pos += 1
                old_pos = pos
                continue

            command += char
            pos += 1

        return result

    def _keyword_is_equal_to(self):
        txt = self._command_line.lstrip()
        pos = txt.find("=")
        if pos == -1:
            if len(txt) > len(self.data.Command):
                txt = " " + txt[len(self.data.Command):]
                pos = 0
        
        txt = txt[pos+1:].strip()
        if txt:
            for i in self.CONTAINERS:
                if txt[0] == i[0]:
                    txt = txt.strip(i[0])
                    break
        
        return txt


class Cmd_Comment(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "#"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'This is a comment. Anything in a line of code starting with "#" will be ignored.'
        self.data.Example = ""
        self.data.CommandType = self.COMMENT
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = self.is_valid()
        self.data.Value = self.value()
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = "# "
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = [0, len(self.command_line), self.data.COLOR_COMMENT]

    def is_valid(self):
        if self.command_line.lstrip().startswith(self.name):
            return True
        else:
            return False

    def value(self):
        return None

    def selection(self):
        return self.data.Selection

    def execute(self):
        return self.data


class Cmd_Parent(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "Parent"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Sets the parent segment.\nEach segment processes only the part of the text it receives from the parent.'
        self.data.Example = 'Parent = "Some_segment_name"'
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'Parent = ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            value = self._keyword_is_equal_to()

        self.data.Valid = is_valid
        self.data.Argument = value
        if value == "None":
            value = None
        self.data.Value = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_Index(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "Index"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'The text index that the segment will receive from the parent.\nWhen the parent segment executes its code, it often receives as a result several text selections.\nThis index indicates the sequence number of the selection.\nIndices start at 0.'
        self.data.Example = 'Index = 0'
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'Index = ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            value = self._keyword_is_equal_to()

        self.data.Valid = is_valid
        self.data.Argument = value
        try:
            value_int = int(value)
        except:
            value_int = None
        self.data.Value = value_int
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_BeginSegment(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "BeginSegment"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'It marks the beginning of the segment and determines its name.\nEverything between the "BeginSegment" and "EndSegment" commands is part of the segment.'
        self.data.Example = 'BeginSegment (Segment_Name)\nEndSegment'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'BeginSegment ()'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            containers = [x for x in self.CONTAINERS]
            containers.append(["(", ")", "()"])
            value = self._text_in_container(self.data.CommandLineText, containers)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_EndSegment(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "EndSegment"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'It marks the end of the segment and determines its name.\nEverything between the "BeginSegment" and "EndSegment" commands is part of the segment.'
        self.data.Example = 'BeginSegment (Segment_Name)\nEndSegment'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'EndSegment'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_DefineStartString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "DefineStartString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'It marks the beginning of the code block in which the string from which the text selection begins is defined.\nEach segment must contain the definition of the string from which the text selection begins,\nas well as the definition of the string up to which the text is selected.'
        self.data.Example = 'DefineStartString\nEndDefineStartString'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'DefineStartString'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_EndDefineStartString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "EndDefineStartString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'It marks the end of the code block in which the string from which the text selection begins is defined.\nEach segment must contain the definition of the string from which the text selection begins,\nas well as the definition of the string up to which the text is selected.'
        self.data.Example = 'DefineStartString\nEndDefineStartString'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'EndDefineStartString'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_DefineEndString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "DefineEndString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'It marks the beginning of the code block in which the string up to which the text will be selected is defined.\nEach segment must contain the definition of the string from which the text selection starts,\nalso the definition of the string up to which the text is selected.'
        self.data.Example = 'DefineEndString\nEndDefineEndString'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'DefineEndString'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_EndDefineEndString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "EndDefineEndString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'It marks the end of the code block in which the string up to which the text will be selected is defined.\nEach segment must contain the definition of the string from which the text selection starts,\nalso the definition of the string up to which the text is selected.'
        self.data.Example = 'DefineEndString\nEndDefineEndString'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'EndDefineEndString'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_MatchCase(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "MatchCase"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Indicates whether upper and lower case letters will be taken into account when defining the strings between which the selected text is located.\nIt can have the values ​​True or False.'
        self.data.Example = 'MatchCase = False'
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'MatchCase = '
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            value = self._keyword_is_equal_to()

        self.data.Valid = is_valid
        if value:
            if value.lower() == "true":
                self.data.Value = True
            elif value.lower() == "false":
                self.data.Value = False
        else:
            self.data.Value = None
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_IsEqual(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "IsEqual"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Defines the starting or ending string between which the selected text is located.\nThe string must be equal to the value of this command in order for the condition to be satisfied.'
        self.data.Example = 'IsEqual "Some_Expression"'
        if self.command_line.lstrip().startswith("Not"):
            self.data.Not = True
        else:
            self.data.Not = False
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'IsEqual ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            value = self._text_in_container(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_StartsWith(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "StartsWith"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Defines the starting or ending string between which the selected text is located.\nThe string must start with the value of this command in order for the condition to be satisfied.'
        self.data.Example = 'StartsWith "Some_Expression"'
        if self.command_line.lstrip().startswith("Not"):
            self.data.Not = True
        else:
            self.data.Not = False
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'StartsWith ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            value = self._text_in_container(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_EndsWith(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "EndsWith"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Defines the starting or ending string between which the selected text is located.\nThe string must end with the value of this command in order for the condition to be satisfied.'
        self.data.Example = 'EndsWith "Some_Expression"'
        if self.command_line.lstrip().startswith("Not"):
            self.data.Not = True
        else:
            self.data.Not = False
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'EndsWith ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True
            value = self._text_in_container(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_If(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "If"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Block "If" - "EndIf"\nThe conditions under which the start/end string will be accepted are defined within this block.'
        self.data.Example = 'If\nContainsString "Expression" or ContainsString "Expression2"\nEndIf'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'If '
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        self.data.Conditions = None
        is_valid = self._is_if_condition_syntax_valid(self.data.CommandLineText)
        value = None
        if is_valid:
            self.data.Conditions = self._get_if_conditions(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_EndIf(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "EndIf"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Block "If" - "EndIf"\nThe conditions under which the start/end string will be accepted are defined within this block.'
        self.data.Example = 'If\nContainsString "Expression" or ContainsString "Expression2"\nEndIf'
        self.data.CommandType = self.BLOCK
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'EndIf'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine)
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip().startswith(self.name):
            is_valid = True

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_StartString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "StartString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Defines the starting or ending string between which the selected text is located.\nThe string must start with the value of this command in order for the condition to be satisfied.\nYou can use multiple "StartString", "EndString" and "ContainsString" commands in one line of code.\nEach command must be separated by a logical operator "And" or "Or".\nThe "Not" operator is used if it is necessary that the command does not satisfy condition.'
        self.data.Example = 'StartString "Expression1" And EndString "Expression2" Or ContainsString "Expression3"'
        if self.command_line.lstrip().startswith("Not"):
            self.data.Not = True
        else:
            self.data.Not = False
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'StartString ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip(" Not").startswith(self.name):
            is_valid = True
            value = self._text_in_container(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_EndString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "EndString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Defines the starting or ending string between which the selected text is located.\nThe string must end with the value of this command in order for the condition to be satisfied.\nYou can use multiple "StartString", "EndString" and "ContainsString" commands in one line of code.\nEach command must be separated by a logical operator "And" or "Or".\nThe "Not" operator is used if it is necessary that the command does not satisfy condition.'
        self.data.Example = 'StartString "Expression1" And EndString "Expression2" Or ContainsString "Expression3"'
        if self.command_line.lstrip().startswith("Not"):
            self.data.Not = True
        else:
            self.data.Not = False
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'EndString ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip(" Not").startswith(self.name):
            is_valid = True
            value = self._text_in_container(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Cmd_ContainsString(AbstractCommand):
    def __init__(self, code: str, line_number: int, text: str, selection: str) -> None:
        self.name = "ContainsString"
        super().__init__(code, line_number, text, selection)

        self.command_line: str = code.split("\n")[line_number]

        self.data.CommandLineText = self.command_line
        self.data.CommandLineNumber = line_number
        self.data.Code = code

        self.data.Command = self.name
        self.data.Description = 'Defines the starting or ending string between which the selected text is located.\nThe string must contain value of this command in order for the condition to be satisfied.\nYou can use multiple "StartString", "EndString" and "ContainsString" commands in one line of code.\nEach command must be separated by a logical operator "And" or "Or".\nThe "Not" operator is used if it is necessary that the command does not satisfy condition.'
        self.data.Example = 'StartString "Expression1" And EndString "Expression2" Or ContainsString "Expression3"'
        if self.command_line.lstrip().startswith("Not"):
            self.data.Not = True
        else:
            self.data.Not = False
        self.data.CommandType = self.KEYWORD
        self.data.Argument = None
        self.data.Conditions = None
        
        self.data.Valid = None
        self.data.Value = None
        self.data.Segment = self._get_segment_name()
        self.data.Text = text
        self.data.Selection = selection

        self.data.AutoCompleteLine = 'ContainsString ""'
        self.data.AutoCompleteCursorPosition = len(self.data.AutoCompleteLine) - 1
        self.data.ColorMap = self._get_color_map_for_simple_command()

    def is_valid(self):
        self.execute()
        return self.data.Valid

    def value(self):
        self.execute()
        return self.data.Value

    def selection(self):
        self.execute()
        return self.data.Selection

    def execute(self):
        is_valid = False
        value = None
        if self.command_line.lstrip(" Not").startswith(self.name):
            is_valid = True
            value = self._text_in_container(self.data.CommandLineText)

        self.data.Valid = is_valid
        self.data.Value = value
        self.data.Argument = value
        self.data.Conditions = None
        # self.data.Selection = self.data.Selection
            
        return self.data


class Code():
    def __init__(self) -> None:
        # self.commands = [ command name, command class ]
        self.commands = [
            ["#", Cmd_Comment],
            ["Parent", Cmd_Parent],
            ["Index", Cmd_Index],
            ["BeginSegment", Cmd_BeginSegment],
            ["EndSegment", Cmd_EndSegment],
            ["DefineStartString", Cmd_DefineStartString],
            ["EndDefineStartString", Cmd_EndDefineStartString],
            ["DefineEndString", Cmd_DefineEndString],
            ["EndDefineEndString", Cmd_EndDefineEndString],
            ["MatchCase", Cmd_MatchCase],
            ["IsEqual", Cmd_IsEqual],
            ["StartsWith", Cmd_StartsWith],
            ["EndsWith", Cmd_EndsWith],
            ["If", Cmd_If],
            ["EndIf", Cmd_EndIf],
            ["StartString", Cmd_StartString],
            ["EndString", Cmd_EndString],
            ["ContainsString", Cmd_ContainsString]

        ]

    def is_string_meet_conditions(self, code: str, string: str, matchcase: bool = False) -> bool:
        abs_command_obj = AbstractCommand("", 0, "", "")
        error = []

        code_list_all = code.split("\n")
        code_list = []
        in_if_comm = False
        for line in code_list_all:
            line: str = line.lstrip()
            if line.startswith("If"):
                in_if_comm = True
            if in_if_comm:
                code_list.append(line)
            if line.startswith("EndIf"):
                in_if_comm = False
        if in_if_comm:
            error.append('Error. Missing "EndIf"')

        criteria_meet = True
        for line in code_list:
            line: str = line.lstrip()
            command_name = self.get_command_object_for_code_line(line, return_command_name_only=True)
            if command_name in abs_command_obj.COMMANDS_CONDITIONS:
                if not line.startswith("If"):
                    line = "If " + line
                command_obj: AbstractCommand = self.get_command_object_for_code_line(line)(line, 0, "", "")
                command_obj.execute()
                conditions = command_obj.data.Conditions
                if conditions is None:
                    continue
                if not conditions["valid"]:
                    error.append(f'Error in line "{line}"  ... Skipped.')
                    continue
                eval_text = conditions["eval_text"]
                for idx, item in enumerate(conditions["conditions"]):
                    condition_value = self._get_condition_value(item, string, matchcase=matchcase)
                    if condition_value is None:
                        error.append(f'Unrecognized condition "{item[0]}" = "{item[1]}" in line "{line}"  ... Set to "True" !')
                        condition_value = True
                    if condition_value:
                        eval_text = eval_text.replace(f"CON[{idx}]", "True")
                    else:
                        eval_text = eval_text.replace(f"CON[{idx}]", "False")
                eval_result = None
                if eval_text.strip():
                    try:
                        eval_result = eval(eval_text)
                    except Exception as e:
                        error.append(f'Command execute failed : "{line}"  ... Skipped !\nError: {e}')
                        continue
                else:
                    eval_result = True

                if eval_result is None or eval_result is False:
                    criteria_meet = False
                    break

        result = {
            "value": criteria_meet,
            "error": error
        }
        return result        

    def _get_condition_value(self, if_command_condition: list, text: str, matchcase: bool = False) -> bool:
        command: str = if_command_condition[0]
        argument: str = if_command_condition[1]
        if not matchcase:
            argument = argument.lower()
            text = text.lower()

        result = None
        if command.startswith("StartString"):
            result = text.startswith(argument)
        elif command.startswith("EndString"):
            result = text.endswith(argument)
        elif command.startswith("ContainsString"):
            if text.find(argument) == -1:
                result = False
            else:
                result = True

        return result
    
    def get_code_block(self, code: str, block_start: str, block_end: str) -> str:
        code_list = code.split("\n")
        block = ""
        in_block = False
        for line in code_list:
            if line.lstrip().startswith(block_start):
                in_block = True
            if in_block:
                block += line + "\n"
            if line.lstrip().startswith(block_end):
                in_block = False
        return block
    
    def is_command_syntax_valid(self, command_line: str) -> bool:
        command_line = command_line.lstrip()
        is_valid = None
        for command in self.commands:
            if command_line.startswith(command[0]):
                command_obj: AbstractCommand = command[1](command_line, 0, "", "")
                is_valid = command_obj.is_valid()
                break
        return is_valid
    
    def get_command_object_for_code_line(self, code_line: str, return_command_name_only: bool = False) -> str:
        code_line = code_line.strip()
        if code_line.startswith("Not"):
            code_line = code_line[3:].strip()

        for i in "()='\"":
            code_line = code_line.replace(i," ")
        pos = code_line.find(" ")
        if pos != -1:
            code_line = code_line[:pos]
        
        if code_line.startswith("Not"):
            code_line = code_line[3:].strip()
        
        for i in self.commands:
            if i[0] == code_line:
                if return_command_name_only:
                    return i[0]
                else:
                    return i[1]
        return None
    
    def get_command_value(self, command_line: str) -> str:
        result = None
        command_line = command_line.lstrip()

        for command in self.commands:
            if command_line.startswith(command[0]):
                command_obj: AbstractCommand = command[1](command_line, 0, "", "")
                result = command_obj.value()
                break
        return result

    def get_segment_command_value(self, segment_code: str, command: str, multi_results: bool = False) -> str:
        code_line = None
        command_values = []
        for idx, i in enumerate(segment_code.split("\n")):
            if i.lstrip().startswith(command):
                result = self._get_multi_values(i)
                for val in result:
                    command_values.append(val)

                code_line = idx

        if multi_results:
            return command_values

        if code_line is None:
            return None
        
        command_value = None
        command_obj: AbstractCommand = self._get_command_object(command)(segment_code, code_line, "", "")
        for i in segment_code.split("\n"):
            if command_obj.is_valid():
                command_value = command_obj.value()
        return command_value

    def _get_multi_values(self, command_line: str) -> list:
        result = []
        command_line = command_line.lstrip()
        in_container = False
        parameter = ""
        container_type = None
        abs_comm = AbstractCommand(command_line, 0, "", "")
        start_con = [x[0] for x in abs_comm.CONTAINERS]
        end_con = [x[1] for x in abs_comm.CONTAINERS]
        for i in command_line:
            if i in start_con and not in_container:
                in_container = True
                container_type = start_con.index(i)
                continue
            if i in end_con and in_container:
                if i == end_con[container_type]:
                    in_container = False
                    result.append(parameter)
                    parameter = ""
                    continue
            if in_container:
                parameter += i
        return result
    
    def _get_command_object(self, command_name: str) -> AbstractCommand:
        for command in self.commands:
            if command[0] == command_name:
                return command[1]
        return None


class Segment():
    def __init__(self, segment_script: str) -> None:
        self.segment_script = segment_script

        self.code_handler = Code()

    def get_list_of_rules_for_GUI(self):
        rules_commands = [
            ["StartString", "If "],
            ["EndString", "If "],
            ["ContainsString", "If "],
            ["IsEqual", ""],
            ["StartsWith", ""],
            ["EndsWith", ""]
        ]
        
        start_block = self.code_handler.get_code_block(self.segment_script, "DefineStartString", "EndDefineStartString")
        end_block = self.code_handler.get_code_block(self.segment_script, "DefineEndString", "EndDefineEndString")
        rules = []
        
        script_list = start_block.split("\n")
        for line in script_list:
            command_obj: AbstractCommand = self.code_handler.get_command_object_for_code_line(line)
            if command_obj is not None:
                command_obj = command_obj(line, 0, "", "")
                for i in rules_commands:
                    if command_obj.data.Command == i[0]:
                        line = line.lstrip()
                        if line.startswith("If "):
                            line = line[3:]
                            line = line.lstrip()
                        rule = i[1] + line
                        rules.append("START: " + rule)
        script_list = end_block.split("\n")
        for line in script_list:
            command_obj: AbstractCommand = self.code_handler.get_command_object_for_code_line(line)
            if command_obj is not None:
                command_obj = command_obj(line, 0, "", "")
                for i in rules_commands:
                    if command_obj.data.Command == i[0]:
                        line = line.lstrip()
                        if line.startswith("If "):
                            line = line[3:]
                            line = line.lstrip()
                        rule = i[1] + line
                        rules.append("END: " + rule)
        return rules
    
    def execute(self, text: str) -> dict:
        code_result = {
            "executed": False,
            "error": [],
            "start": {
                "DefineStartString": self.code_handler.get_code_block(self.segment_script, "DefineStartString", "EndDefineStartString"),
                "IsEqual": [],
                "StartsWith": [],
                "EndsWith": [],
                "conditions": []
            },
            "end": {
                "DefineEndString": self.code_handler.get_code_block(self.segment_script, "DefineEndString", "EndDefineEndString"),
                "IsEqual": [],
                "StartsWith": [],
                "EndsWith": [],
                "conditions": []
            },
            "selections": {}
        }
        
        code_result["start"]["IsEqual"] = self.code_handler.get_segment_command_value(code_result["start"]["DefineStartString"], "IsEqual", multi_results=True)
        code_result["start"]["StartsWith"] = self.code_handler.get_segment_command_value(code_result["start"]["DefineStartString"], "StartsWith", multi_results=True)
        code_result["start"]["EndsWith"] = self.code_handler.get_segment_command_value(code_result["start"]["DefineStartString"], "EndsWith", multi_results=True)

        code_result["end"]["IsEqual"] = self.code_handler.get_segment_command_value(code_result["end"]["DefineEndString"], "IsEqual", multi_results=True)
        code_result["end"]["StartsWith"] = self.code_handler.get_segment_command_value(code_result["end"]["DefineEndString"], "StartsWith", multi_results=True)
        code_result["end"]["EndsWith"] = self.code_handler.get_segment_command_value(code_result["end"]["DefineEndString"], "EndsWith", multi_results=True)

        # Check if main conditions are valid
        error_msg = "The START selection has the value 'IsEqual' set, but the string with which this value should start or end conflicts with this value."

        if code_result["start"]["DefineStartString"] and (not (code_result["start"]["IsEqual"] or (code_result["start"]["StartsWith"] and code_result["start"]["EndsWith"]))):
            error_msg = 'The start of the selection is not properly defined.\nYou must define the "IsEqual" field or the "StartsWith" and "EndsWith" fields.'
            code_result["error"].append(error_msg)

        if code_result["end"]["DefineEndString"] and (not (code_result["end"]["IsEqual"] or (code_result["end"]["StartsWith"] and code_result["end"]["EndsWith"]))):
            error_msg = 'The end of the selection is not properly defined.\nYou must define the "IsEqual" field or the "StartsWith" and "EndsWith" fields.'
            code_result["error"].append(error_msg)

        if code_result["error"]:
            code_result["error"].append("Code execution was interrupted due to an error.")
            return code_result
        
        # Check for case sensitivity
        match_case = self.code_handler.get_segment_command_value(self.segment_script, "MatchCase")
        if match_case is None:
            match_case = False
        if match_case:
            txt = text
        else:
            txt = text.lower()
            code_result["start"]["IsEqual"] = self._lower_list(code_result["start"]["IsEqual"])
            code_result["start"]["StartsWith"] = self._lower_list(code_result["start"]["StartsWith"])
            code_result["start"]["EndsWith"] = self._lower_list(code_result["start"]["EndsWith"])
            code_result["end"]["IsEqual"] = self._lower_list(code_result["end"]["IsEqual"])
            code_result["end"]["StartsWith"] = self._lower_list(code_result["end"]["StartsWith"])
            code_result["end"]["EndsWith"] = self._lower_list(code_result["end"]["EndsWith"])

        # Find all start strings
        occurrences = []
        pos = 0
        while code_result["start"]["DefineStartString"]:
            if code_result["start"]["IsEqual"]:
                pos, found_item = self._find_first_pos(code_result["start"]["IsEqual"], txt, pos)
                if pos == -1:
                    break
                occurrences.append([pos, pos + len(found_item), found_item])
                pos += len(found_item)
                continue

            pos, found_item_start = self._find_first_pos(code_result["start"]["StartsWith"], txt, pos)
            pos_end, found_item_end = self._find_first_pos(code_result["start"]["EndsWith"], txt, pos + len(found_item_start))
            if pos == -1 or pos_end == -1:
                break
            
            occurrences.append([pos, pos_end + len(found_item_end), txt[pos:pos_end + len(found_item_end)]])
            pos = pos_end + len(found_item_end)

        delete_occur = []
        for idx, item in enumerate(occurrences):
            is_valid = self.code_handler.is_string_meet_conditions(code_result["start"]["DefineStartString"], item[2], matchcase=match_case)
            
            for i in is_valid["error"]:
                code_result["error"].append(i)

            if not is_valid["value"]:
                delete_occur.insert(0, idx)

        for idx in delete_occur:
            occurrences.pop(idx)

        # Case when DefineStartString does not exist:
        if not code_result["start"]["DefineStartString"]:
            occurrences = [[0, 0, ""]]
        
        # Find all End Strings
        count = 0
        for occurrence in occurrences:
            pos = occurrence[1]
            
            found_end = False
            end_selection = None
            while code_result["end"]["DefineEndString"]:
                if code_result["end"]["IsEqual"]:
                    pos, found_item = self._find_first_pos(code_result["end"]["IsEqual"], txt, pos)
                    if pos == -1:
                        break
                    end_selection = [pos, pos + len(found_item), found_item]
                    pos += len(found_item)
                else:
                    pos, found_item_start = self._find_first_pos(code_result["end"]["StartsWith"], txt, pos)
                    pos_end, found_item_end = self._find_first_pos(code_result["end"]["EndsWith"], txt, pos + len(found_item_start))
                    if pos == -1 or pos_end == -1:
                        break
                    end_selection = [pos, pos_end + len(found_item_end), txt[pos:pos_end + len(found_item_end)]]
                    pos += len(found_item_start)
                
                is_valid = self.code_handler.is_string_meet_conditions(code_result["end"]["DefineEndString"], end_selection[2])
                
                for i in is_valid["error"]:
                    code_result["error"].append(i)

                if is_valid["value"]:
                    found_end = end_selection
                    break
            
            # Case when DefineEndString does not exist
            if not code_result["end"]["DefineEndString"]:
                found_end = [len(txt), len(txt), ""]

            if found_end:
                code_result["selections"][count] = {
                    "start": occurrence[1],
                    "end": found_end[0],
                    "selection": text[occurrence[1]:found_end[0]]
                }
                count += 1
            
        return code_result

    def _find_first_pos(self, items: list, text: str, from_pos: int) -> tuple:
        """Find the first position of any item in items in text from from_pos."""
        result = len(text) + 1
        found_item = ""
        for item in items:
            pos = text.find(item, from_pos)
            if pos != -1 and pos < result:
                result = pos
                found_item = item
                
        if result > len(text):
            result = -1
        return (result, found_item)

    def _lower_list(self, list_to_lower: list) -> list:
        result = []
        for i in range(len(list_to_lower)):
            result.append(list_to_lower[i].lower())
        return result

    @property
    def parent(self) -> str:
        return self.code_handler.get_segment_command_value(self.segment_script, "Parent")

    @property
    def name(self) -> str:
        return self.code_handler.get_segment_command_value(self.segment_script, "BeginSegment")

    @property
    def code(self) -> str:
        return self.segment_script

    @property
    def index(self) -> str:
        return self.code_handler.get_segment_command_value(self.segment_script, "Index")


class Script():
    def __init__(self, data_source: dict = None) -> None:
        if data_source is None:
            self.data_source = self._empty_data_source_dict()
        else:
            self.data_source = data_source

        self.code = Code()

    def _empty_data_source_dict(self) -> dict:
        result = {
            "project": None,
            "selected": None,
            "type": None,
            "source": None,
            "text": None,
            "formated_text": None,
            "code": None
        }
        return result

    def segment(self, segment_name: str) -> Segment:
        segment_script = self._get_segment_script(segment_name=segment_name)
        return Segment(segment_script=segment_script)

    def load_data_source(self, data_source: dict) -> None:
        self.data_source = data_source

    def get_top_segment_names(self) -> list:
        top_segments = []
        segments = self.get_all_segments()
        for segment in segments:
            if segment.parent == "None" or segment.parent is None:
                top_segments.append(segment.name)
        return top_segments

    def get_segment_children(self, segment_name: str, names_only: bool = False) -> list:
        if names_only:
            return self._children_names_for_parent(segment_name)
        
        segments = self.get_all_segments()
        result = []
        for segment in segments:
            if segment.parent == segment_name:
                result.append(segment)
        return result

    def _children_names_for_parent(self, parent_name: str) -> list:
        code_list = self.data_source["code"].split("\n")
        result = []
        in_segment = False
        segment_name = ""
        seg_parent = ""
        for line in code_list:
            if line.lstrip().startswith("BeginSegment"):
                seg_parent = ""
                segment_name = ""
                segment_name = self.code.get_command_value(line)
                in_segment = True
            
            if line.lstrip().startswith("Parent") and in_segment:
                seg_parent = self.code.get_command_value(line)
            
            if line.lstrip().startswith("EndSegment") and in_segment:
                if segment_name and seg_parent:
                    if seg_parent == parent_name:
                        result.append(segment_name)
                seg_parent = ""
                segment_name = ""
                in_segment = False

        return result

    def update_block_in_segment(self, segment_name: str, new_block: str, replace_in_all_siblings: bool = False, feedback_function = None) -> str:
        original_segment = Segment(self._get_segment_script(segment_name=segment_name))

        segments_map = self.get_segments_map_name_parent()
        errors = ""
        count_segments = 0
        count = 0
        original_segment_parent = original_segment.parent
        sibling_segments = [x[0] for x in segments_map if x[1] == original_segment_parent]

        if replace_in_all_siblings:
            for segment in sibling_segments:
                self.delete_segment_children(segment, segments_map)

            for segment in sibling_segments:
                result = self._update_block_in_segment(segment_name=segment, new_block=new_block)
                count_segments += len(result["selections"])
                if result["error"]:
                    errors += "SEGMENT: " + segment + "\n"
                    errors += "\n".join(result["error"])
                    errors += "\n"*3
                count += 1
                if feedback_function:
                    is_aborted = feedback_function({"current": count, "total": len(sibling_segments)})
                    if is_aborted:
                        errors += "Interupted by User !\n"
                        return {"errors": errors, "count": count_segments}

        else:
            self.delete_segment_children(segment_name, segments_map)
            result = self._update_block_in_segment(segment_name=segment_name, new_block=new_block)
            count_segments += len(result["selections"])
            if result["error"]:
                errors += "SEGMENT: " + segment_name + "\n"
                errors += "\n".join(result["error"])
                errors += "\n"*3
        return {"errors": errors, "count": count_segments}

    def _update_block_in_segment(self, segment_name: str, new_block: str) -> list:
        new_block_list = new_block.split("\n")
        block_start = new_block_list[0].lstrip()
        block_end = new_block_list[-1].lstrip()

        segment = Segment(self._get_segment_script(segment_name))
        segment_code_list = segment.code.split("\n")
        segment_code_list_clean = []
        in_block = False
        for line in segment_code_list:
            if line.lstrip().startswith(block_start):
                in_block = True

            if line.lstrip().startswith(block_end):
                in_block = False
                if not block_end.startswith("EndSegment"):
                    continue

            if in_block:
                continue
            
            if line.lstrip().startswith("EndSegment"):
                segment_code_list_clean.append(new_block)
                if block_end.startswith("EndSegment"):
                    continue

            segment_code_list_clean.append(line)
        
        segment_code = "\n".join(segment_code_list_clean) + "\n"

        code_list = self.data_source["code"].split("\n")
        new_code = ""
        in_segment = False
        for line in code_list:
            if line.lstrip().startswith("BeginSegment"):
                if self.code.get_command_value(line) == segment_name:
                    in_segment = True
                
            if line.lstrip().startswith("EndSegment") and in_segment:
                in_segment = False
                continue

            if in_segment:
                continue

            new_code += line + "\n"
        
        new_code += segment_code

        self.data_source["code"] = new_code

        if self.data_source["formated_text"]:
            txt = self.data_source["formated_text"]
        else:
            txt = self.data_source["text"]

        segment = Segment(self._get_segment_script(segment_name=segment_name))
        text_dict = self.get_segment_text(segment_name=segment_name)
        short_text = txt[text_dict["start"]:text_dict["end"]]

        result = segment.execute(short_text)
        for index in result["selections"]:
            if result["selections"][index]["end"] <= result["selections"][index]["start"]:
                continue

            new_name = segment.name + "_" + self._add_leading_zeros(index)
            new_segment_code = f"""
BeginSegment ({new_name})
    Parent = "{segment_name}"
    Index = {int(index)}
EndSegment
"""
            new_code += new_segment_code + "\n"
        
        while True:
            new_code = new_code.replace("\n\n\n", "\n\n")
            if new_code.find("\n\n\n") == -1:
                break

        self.data_source["code"] = new_code
        return result

    def _add_leading_zeros(self, number: int, string_len: int = 3) -> str:
        txt = str(number)
        if len(txt) < string_len:
            txt = "0" * (string_len - len(txt)) + txt
        return txt

    def delete_segment_children(self, segment_name: str, segments_map: list = None, delete_current_segment_also: bool = False):
        if segments_map is None:
            segments_map = self.get_segments_map_name_parent()

        code_list = self.data_source["code"].split("\n")

        segements_to_delete = []

        self._segment_tree(segment_name=segment_name, tree_list=segements_to_delete, segments_map=segments_map)
        if delete_current_segment_also:
            segements_to_delete.append(segment_name)

        new_code = ""
        in_segment = False
        for line in code_list:
            if line.lstrip().startswith("BeginSegment"):
                name = self.code.get_command_value(line)
                if name in segements_to_delete:
                    in_segment = True

            if line.lstrip().startswith("EndSegment") and in_segment:
                in_segment = False
                continue
            if in_segment:
                continue
            new_code += line + "\n"
        while True:
            new_code = new_code.replace("\n\n\n", "\n\n")
            if new_code.find("\n\n\n") == -1:
                break
        self.data_source["code"] = new_code
        
    def _segment_tree(self, segment_name: str, tree_list: list, segments_map: list):
        children = [x[0] for x in segments_map if x[1] == segment_name]
        if children:
            for child in children:
                tree_list.append(child)
                self._segment_tree(child, tree_list=tree_list, segments_map=segments_map)
        return tree_list
    
    def get_segment_text(self, segment_name: str) -> dict:
        if segment_name not in self.get_all_segments(names_only=True):
            return None
        
        if self.data_source["formated_text"]:
            txt = self.data_source["formated_text"]
        else:
            txt = self.data_source["text"]

        segment_hierarchy = []
        seg_name = segment_name
        seg_index = None
        while True:
            segment = Segment(self._get_segment_script(segment_name=seg_name))
            segment_hierarchy.insert(0, [segment, seg_index])

            seg_index = segment.index
            if segment.parent is None:
                break
            seg_name = segment.parent
        
        segment_hierarchy.pop(len(segment_hierarchy)-1)
        text_start = 0
        text_end = len(txt)
        for segment in segment_hierarchy:
            segment_obj: Segment = segment[0]
            segment_index: int = segment[1]

            selections = segment_obj.execute(txt[text_start:text_end])["selections"]
            new_text_start = None
            new_text_end = None
            for selection in selections:
                if int(selection) == int(segment_index):
                    new_text_start = selections[selection]["start"]
                    new_text_end = selections[selection]["end"]
                    break
            if new_text_start is None:
                new_text_start = 0
            if new_text_end is None:
                new_text_end = 0

            text_start += new_text_start
            text_end = text_start + (new_text_end - new_text_start)
        
        result = {
            "start": text_start,
            "end": text_end
        }
        return result

    def rename_segment(self, segment_to_rename: str, new_name: str) -> dict:
        code_list = [x for x in self.data_source["code"].split("\n")]
        
        result = {
            "renamed": 0,
            "parent_changed": 0,
            "error": None
        }

        if new_name in self.get_all_segments(names_only=True):
            result["error"] = f'Error.\nSegment name "{new_name}" already exist.\nName cannot be changed!'
            return result
        elif not new_name:
            result["error"] = 'Error.\nNew segment name is not defined.\nName cannot be changed!'
            return result
        elif not segment_to_rename:
            result["error"] = 'Error.\nCurrent segment is not defined.\nName cannot be changed!'
            return result

        for i, line in enumerate(code_list):
            if line.lstrip().startswith("BeginSegment"):
                segment_name = self.code.get_command_value(line)
                if segment_name == segment_to_rename:
                    code_list[i] = f"BeginSegment ({new_name})"
                    result["renamed"] += 1
            if line.lstrip().startswith("Parent"):
                parent_name = self.code.get_command_value(line)
                if parent_name == segment_to_rename:
                    code_list[i] = f'    Parent = "{new_name}"'
                    result["parent_changed"] += 1
        
        self.data_source["code"] = "\n".join(code_list) + "\n"

        return result
    
    def get_all_segments(self, names_only: bool = False) -> list:
        code_list = self.data_source["code"].split("\n")
        result = []
        segment_script = ""
        segment_name = ""
        for line in code_list:
            segment_script += line + "\n"
            if line.lstrip().startswith("BeginSegment"):
                segment_name = self.code.get_command_value(line)
                segment_script = line + "\n"
            if line.lstrip().startswith("EndSegment"):
                if segment_name:
                    if names_only:
                        result.append(segment_name)
                    else:
                        result.append(Segment(segment_script))
                    segment_name = ""

        return result

    def get_segments_map_name_parent(self, siblings_for: str = None) -> list:
        if siblings_for:
            segment = Segment(self._get_segment_script(siblings_for))
            search_for_parent = segment.parent

        code_list = self.data_source["code"].split("\n")
        result = []
        for line in code_list:
            if line.lstrip().startswith("BeginSegment"):
                segment_name = self.code.get_command_value(line)
            if line.lstrip().startswith("Parent"):
                parent = self.code.get_command_value(line)
                if segment_name:
                    if siblings_for:
                        if parent == search_for_parent:
                            result.append([segment_name, parent])
                    else:
                        result.append([segment_name, parent])
                    segment_name = ""
            if line.lstrip().startswith("EndSegment"):
                segment_name = ""

        return result

    def update_segment_code(self, segment_code_to_be_replaced: str, new_code_to_insert: str) -> str:
        replace_code_list = segment_code_to_be_replaced.split("\n")
        replace_with_list = new_code_to_insert.split("\n")

        old_code = ""
        for i in replace_code_list:
            if i.lstrip().startswith(("BeginSegment", "Parent", "Index")):
                old_code += i + "\n"

        new_code = ""
        for i in replace_with_list:
            if not i.lstrip().startswith(("BeginSegment", "Parent", "Index", "EndSegment")):
                new_code += i + "\n"
        
        result = old_code + new_code + "EndSegment"

        return result

    def _get_segment_script(self, segment_name: str) -> str:
        code_list = self.data_source["code"].split("\n")
        result = ""
        segment_code = False
        for line in code_list:
            if line.strip().startswith("BeginSegment"):
                if self.code.get_command_value(line) == segment_name:
                    segment_code = True
            
            if not segment_code:
                continue
            
            if line.strip().startswith("EndSegment"):
                segment_code = False
                result += line

            if segment_code:
                result += f"{line}\n"
        return result


class Rashomon():
    def __init__(self, project_filename: str = None) -> None:
        self._error_messages = []
        self.timeout_for_retriving_from_url = 3
        self._compatible_mode = False
        self.project_name = project_filename
        self._data_source = None
        self.script = Script()
        if project_filename:
            self.load_project(project_filename)

    def get_segment_selection(self, segment_name: str, remove_tags: bool = False, remove_double_lf: bool = True, join_in_one_line: bool = False, strip_spaces: bool = True, remove_comments: bool = True) -> str:
        if not self.project_name:
            self.errors(error_message="No project loaded.")
            return None
        
        if not self.is_segment(segment_name=segment_name):
            self.errors(error_message=f'Segment "{segment_name}" does not exist.')
            return ""

        text_dict = self.script.get_segment_text(segment_name=segment_name)
        if not text_dict:
            self.errors(error_message="Segment selection text could not be retrived.")
            return ""
        if self._data_source["formated_text"]:
            txt = self._data_source["formated_text"]
        else:
            txt = self._data_source["text"]
        
        txt = txt[text_dict["start"]:text_dict["end"]]

        if remove_tags:
            txt = self.remove_tags(txt, join_in_one_line=join_in_one_line)

        if strip_spaces:
            txt = txt.strip()
        
        if remove_comments:
            while True:
                start = txt.find("<!--")
                if start != -1:
                    one_line_comment = True
                    end = txt.find("-->", start)
                    if end != -1:
                        comment_text = txt[start:end+3]
                        if comment_text.count("\n") < 3:
                            txt = txt[:start] + txt[end+3:]
                            one_line_comment = False
                    if one_line_comment:
                        end = txt.find("\n", start)
                        if end == -1:
                            txt = txt[:start]
                        else:
                            txt = txt[:start] + txt[end+1:]
                else:
                    break

        if remove_double_lf:
            txt_list = [x.strip() for x in txt.split("\n") if x.strip()]
            txt = "\n".join(txt_list)

        return txt

    def get_segment_siblings(self, segment_name: str) -> list:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        result = self.script.get_segments_map_name_parent(siblings_for=segment_name)
        return result

    def sort_segments(self, segments: list) -> list:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        all_segments = self.script.get_all_segments(names_only=True)
        seg_data = []
        for segment in segments:
            if segment not in all_segments:
                return None
            segment_text = self.script.get_segment_text(segment)
            seg_data.append([segment, segment_text["start"]])
        
        seg_data.sort(key=lambda x: x[1])
        return [x[0] for x in seg_data]

    def recreate_segment_tree(self) -> bool:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        # Create dict with all top level segments and descendants
        code_tree = {}
        for i in self.script.get_top_segment_names():
            # Add top level segment code
            code_tree[i] = []

            # Find descendants code
            cur_segment = i
            while True:
                children = self.script.get_segment_children(cur_segment, names_only=True)
                if self._is_defined_segment(cur_segment):
                    code_tree[i].append(self.script._get_segment_script(cur_segment))

                if not children:
                    break
                cur_segment = children[0]

            if not code_tree[i]:
                code_tree[i].append(self.script._get_segment_script(i))

        self._data_source["code"] = ""

        success = True
        for top_level_segment in code_tree:
            descendants = code_tree[top_level_segment]
            self._data_source["code"] += descendants[0]
            
            cur_segment = top_level_segment
            for descendant in descendants:
                result = self._build_segment_tree(cur_segment, descendant)
                if not result:
                    break
                children = self.script.get_segment_children(cur_segment,names_only=True)
                if not children:
                    break
                cur_segment = children[0]

            if result is False:
                success = False
                break
        return success

    def _is_defined_segment(self, segment_name: str) -> bool:
        segment_code = self.script._get_segment_script(segment_name)
        result = False
        for i in segment_code.split("\n"):
            if i.strip().startswith(("DefineStartString", "DefineEndString")):
                result = True
                break
        return result

    def _build_segment_tree(self, segment_name, new_code: str):
        segment_code = self.script._get_segment_script(segment_name=segment_name)
        segment = Segment(segment_code)

        result = None
        siblings = []
        if segment.parent:
            siblings = self.script.get_segments_map_name_parent(siblings_for=segment_name)
        else:
            siblings.append([segment_name, None])
        
        for seg in siblings:
            segment = Segment(self.script._get_segment_script(seg[0]))
            updated_code = self.script.update_segment_code(segment.code, new_code)
            result = self.script.update_block_in_segment(seg[0], updated_code.strip(), replace_in_all_siblings=False)
            if result["errors"]:
                break
        
        if result and result["errors"]:
            for error in result["errors"]:
                self.errors(error)
            return False

        return result

    def is_segment(self, segment_name: str) -> bool:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        if segment_name in self.script.get_all_segments(names_only=True):
            return True
        else:
            return False

    def get_all_segments(self) -> list:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        return self.script.get_all_segments(names_only=True)

    def get_segment_children(self, segment_name: str = None) -> list:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        if segment_name is None:
            result = self.script.get_top_segment_names()
        else:
            result = self.script.get_segment_children(segment_name=segment_name, names_only=True)
        return result

    def remove_tags(self, text: str, join_in_one_line: bool = False, delimiter: str = "") -> str:
        result = ""
        in_tag = False
        pos = 0
        while pos < len(text):
            char = text[pos]
            if char == "<":
                in_tag = True
                pos += 1
                continue
            if char == ">":
                in_tag = False
                pos += 1
                continue
            if in_tag:
                pos += 1
                continue

            result += char
            pos += 1

        if join_in_one_line:
            result = delimiter.join(result.split("\n"))
        
        return result

    def _quick_format_html(self, html: str) -> str:
        if not html:
            return html
        
        html = html.replace("<", "\n<")
        html = html.replace(">", ">\n")
        
        html_clean = ""
        in_tag = False
        for line in html.splitlines():
            if line.startswith("<"):
                html_clean += line.replace("'", '"')
                in_tag = True
                if line.endswith(">"):
                    html_clean += "\n"
                    in_tag = False
                continue
            if in_tag:
                html_clean += " " + line.replace("'", '"')
            if line.endswith(">"):
                in_tag = False
                html_clean += "\n"
                continue

            if not in_tag:
                html_clean += HtmlLib.unescape(line) + "\n"

        html_clean = self.remove_extra_spaces(text=html_clean, only_remove_double="\n", remove_tabs=True)
        return html_clean

    def get_tags(self, 
                 html_code: str, 
                 tag: str, 
                 tag_id_contains: str = None, 
                 tag_class_contains: str = None, 
                 tag_title_contains: str = None, 
                 tag_property_contains: str = None, 
                 tag_content_contains: str = None,
                 tag_type_contains: str = None,
                 tag_name_contains: str = None,
                 custom_tag_property: list = None,
                 multiline: bool = False) -> list:
        
        html_code = self._quick_format_html(html_code)

        if not tag or not html_code:
            return ""
        
        tag_rules = [
            ["id", tag_id_contains], 
            ["class", tag_class_contains],
            ["title", tag_title_contains],
            ["property", tag_property_contains],
            ["content", tag_content_contains],
            ["type", tag_type_contains],
            ["name", tag_name_contains]
        ]
        if custom_tag_property:
            try:
                for tag_property in custom_tag_property:
                    tag_rules.append([tag_property[0], tag_property[1]])
            except Exception as e:
                print (f"Invalid custom_tag_property: {e}")

        html_list = [x.strip() for x in html_code.split("\n")]

        if multiline:
            end_tag = "</" + tag.strip(" ><") + ">"
        else:
            end_tag = ">"
        tag = ("<" + tag.strip(" ><") + " ", "<" + tag.strip(" ><") + ">")

        in_tag = 0
        in_main_tag = False
        tag_code = ""
        result = []
        for line in html_list:
            if line.startswith(tag):
                if in_main_tag:
                    in_tag += 1
                elif self._is_tag_mark_valid(line, tag_rules):
                    in_main_tag = True
                    in_tag += 1
                    
            if line.endswith(end_tag) and in_tag:
                if in_main_tag:
                    in_tag -= 1
                    if not in_tag:
                        tag_code += line + "\n"
                        result.append(tag_code.strip())
                        tag_code = ""
                        in_main_tag = False
            
            if in_main_tag:
                tag_code += line + "\n"

        return result
    
    def _is_tag_mark_valid(self, tag_code: str, rules: list) -> bool:
        for rule in rules:
            if rule[1]:
                mark = rule[0] + '='
                if mark not in tag_code:
                    return False
                else:
                    start = tag_code.find(mark)
                    bound_char = " "
                    if start != -1:
                        if tag_code[start+len(mark):start+len(mark)+1] in "\"'":
                            bound_char = tag_code[start+len(mark):start+len(mark)+1]
                    end = tag_code.find(bound_char, start + len(mark) + 1)
                    if end == -1:
                        end = tag_code.find('>', start + len(mark))
                    if end == -1:
                        return None
                    value = tag_code[start+len(mark):end].strip(" '\"")
                    if rule[1] not in value:
                        return False
        return True

    def remove_specific_tag(self, text: str, tag: str, multiline: bool = False) -> str:
        text = self._quick_format_html(text)

        if not tag:
            return text
        
        if multiline:
            end_tag = "</" + tag.strip(" ><") + ">"
        else:
            end_tag = ">"

        tag = ("<" + tag.strip(" ><") + " ", "<" + tag.strip(" ><") + ">")

        result = ""
        in_tag = 0
        for line in text.splitlines():
            if line.startswith(tag):
                in_tag += 1
            
            if line.endswith(end_tag) and in_tag:
                in_tag -= 1
                continue

            if not in_tag:
                result += line + "\n"

        return result.strip()

    def remove_extra_spaces(self, text: str, only_remove_double: list = None, remove_tabs: bool = True) -> str:
        if text is None:
            return None
        
        remove = [" ", "\n"]
        if only_remove_double:
            if isinstance(only_remove_double, str):
                remove = [only_remove_double]
            elif isinstance(only_remove_double, list) or isinstance(only_remove_double, tuple) or isinstance(only_remove_double, set):
                remove = [x for x in only_remove_double]
            else:
                UTILS.TerminalUtility.WarningMessage("Variable #1 must be a #2, #3, #4 or #5\ntype(only_remove_double): #6\nonly_remove_double = #7", ["only_remove_double", "string", "list", "tuple", "set", type(only_remove_double), only_remove_double], exception_raised=True)
                raise ValueError("only_remove_double must be a string, list, tuple or set")

        while True:
            for item in remove:
                item_to_remove = item * 2
                item_to_replace_with = item
                text = text.replace(item_to_remove, item_to_replace_with)

            has_completed = True

            if remove_tabs:
                text = text.replace("\t", " ")
                if text.find("\t") != -1:
                    has_completed = False

            for item in remove:
                item_to_remove = item * 2
                if text.find(item_to_remove) != -1:
                    has_completed = False
            
            if has_completed:
                break

        return text.strip()

    def loaded_project(self) -> str:
        return self.project_name

    def load_project(self, project_filename: str = None, change_source: str = None) -> bool:
        if not os.path.isfile(project_filename):
            self.errors(error_message="The file does not exist.")
            self._data_source = None
            self.project_name = None
            return False
        
        try:
            with open(project_filename, "r", encoding="utf-8") as file:
                self._data_source = json.load(file)
        except Exception as e:
            self.errors(str(e))
            self._data_source = None
            self.project_name = None
            return False
        
        if change_source:
            self._data_source["source"] = change_source

        result = self.download_text_from_source()
        if not result:
            self.errors(error_message="The text could not be retrieved from the source.")
            self._data_source = None
            self.project_name = None
            return False

        self.project_name = project_filename
        self.script.load_data_source(self._data_source)
        return True
    
    def get_source(self) -> str:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        return self._data_source["source"]
    
    def get_source_text(self) -> str:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None

        if self._compatible_mode:
            if self._data_source["formated_text"]:
                return self._data_source["formated_text"]
            else:
                return self._data_source["text"]
        else:
            return self._data_source["text"]
        
    def set_compatible_mode(self, value: bool):
        if not isinstance(value, bool):
            self.errors(error_message="Set Compatible Mode: Value must be boolean True/False")
            return None
        
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None
        
        self._compatible_mode = value
        if not value:
            self._data_source["formated_text"] = ""
            return
        
        formatted_text = self._quick_format_html(self._data_source["text"])
        self._data_source["formated_text"] = formatted_text
    
    def is_compatible_mode(self) -> bool:
        return self._compatible_mode

    def errors(self, error_message: str = None, clear_errors: bool = False) -> list:
        if not isinstance(error_message, str) and error_message is not None:
            try:
                error_message = str(error_message)
            except:
                error_message = "Unknown error."

        if clear_errors:
            self._error_messages = []
        
        if error_message:
            self._error_messages.append(error_message)
        
        return self._error_messages
    
    def clear_errors(self):
        self._error_messages = []

    def set_new_source(self, source: str, dowload_text_from_source: bool = True) -> bool:
        if not source:
            return False
        
        self._data_source["source"] = source
        result = True
        if dowload_text_from_source:
            result = self.download_text_from_source()
        
        if not result:
            self.errors(error_message="The text could not be retrieved from the source.")
            return False
        return result

    def download_text_from_source(self) -> bool:
        if self._data_source is None:
            self.errors(error_message="No project loaded.")
            return None
        txt = ""
        if self._data_source["selected"] == "file":
            txt = self._retrive_text_from_file(self._data_source["source"])
            if txt is None:
                return False
        elif self._data_source["selected"] == "web":
            txt = self._retrive_text_from_url(self._data_source["source"])
            if txt is None:
                return False
        self._data_source["text"] = txt
        return True
        
    def _retrive_text_from_file(self, filename: str) -> str:
        if not os.path.isfile(filename):
            return None
        
        result = ""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                result = file.read()
        except Exception as e:
            self.errors(error_message=e)
            return None
        
        return result
    
    def _retrive_text_from_url(self, url: str) -> str:
        result = ""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110'
        }
        try:
            result_page = requests.get(self._data_source["source"], headers=headers)
            result_page.raise_for_status()
            result = result_page.text
        except:
            try:
                result = urllib.request.urlopen(url, timeout=self.timeout_for_retriving_from_url).read().decode("utf-8")
            except Exception as e:
                self.errors(error_message=e)
                return None
        
        return result
