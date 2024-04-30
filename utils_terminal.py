from typing import Union, Any
import warnings
import inspect
from datetime import datetime

from utils_log import LogHandler


class TerminalColors:
    RESET_ALL = "\033[0m"

    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"
    _FG_GRAY = "\033[90m"
    _FG_BRIGHT_RED = "\033[91m"
    _FG_BRIGHT_GREEN = "\033[92m"
    _FG_BRIGHT_YELLOW = "\033[93m"
    _FG_BRIGHT_BLUE = "\033[94m"
    _FG_BRIGHT_MAGENTA = "\033[95m"
    _FG_BRIGHT_CYAN = "\033[96m"
    _FG_BRIGHT_WHITE = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    _BG_GRAY = "\033[100m"
    _BG_BRIGHT_RED = "\033[101m"
    _BG_BRIGHT_GREEN = "\033[102m"
    _BG_BRIGHT_YELLOW = "\033[103m"
    _BG_BRIGHT_BLUE = "\033[104m"
    _BG_BRIGHT_MAGENTA = "\033[105m"
    _BG_BRIGHT_CYAN = "\033[106m"
    _BG_BRIGHT_WHITE = "\033[107m"

    FG_BLACK_RESET_FIRST = f"{RESET_ALL}\033[30m"
    FG_RED_RESET_FIRST = f"{RESET_ALL}\033[31m"
    FG_GREEN_RESET_FIRST = f"{RESET_ALL}\033[32m"
    FG_YELLOW_RESET_FIRST = f"{RESET_ALL}\033[33m"
    FG_BLUE_RESET_FIRST = f"{RESET_ALL}\033[34m"
    FG_MAGENTA_RESET_FIRST = f"{RESET_ALL}\033[35m"
    FG_CYAN_RESET_FIRST = f"{RESET_ALL}\033[36m"
    FG_WHITE_RESET_FIRST = f"{RESET_ALL}\033[37m"
    _FG_GRAY_RESET_FIRST = f"{RESET_ALL}\033[90m"
    _FG_BRIGHT_RED_RESET_FIRST = f"{RESET_ALL}\033[91m"
    _FG_BRIGHT_GREEN_RESET_FIRST = f"{RESET_ALL}\033[92m"
    _FG_BRIGHT_YELLOW_RESET_FIRST = f"{RESET_ALL}\033[93m"
    _FG_BRIGHT_BLUE_RESET_FIRST = f"{RESET_ALL}\033[94m"
    _FG_BRIGHT_MAGENTA_RESET_FIRST = f"{RESET_ALL}\033[95m"
    _FG_BRIGHT_CYAN_RESET_FIRST = f"{RESET_ALL}\033[96m"
    _FG_BRIGHT_WHITE_RESET_FIRST = f"{RESET_ALL}\033[97m"

    BG_BLACK_RESET_FIRST = f"{RESET_ALL}\033[40m"
    BG_RED_RESET_FIRST = f"{RESET_ALL}\033[41m"
    BG_GREEN_RESET_FIRST = f"{RESET_ALL}\033[42m"
    BG_YELLOW_RESET_FIRST = f"{RESET_ALL}\033[43m"
    BG_BLUE_RESET_FIRST = f"{RESET_ALL}\033[44m"
    BG_MAGENTA_RESET_FIRST = f"{RESET_ALL}\033[45m"
    BG_CYAN_RESET_FIRST = f"{RESET_ALL}\033[46m"
    BG_WHITE_RESET_FIRST = f"{RESET_ALL}\033[47m"
    _BG_GRAY_RESET_FIRST = f"{RESET_ALL}\033[100m"
    _BG_BRIGHT_RED_RESET_FIRST = f"{RESET_ALL}\033[101m"
    _BG_BRIGHT_GREEN_RESET_FIRST = f"{RESET_ALL}\033[102m"
    _BG_BRIGHT_YELLOW_RESET_FIRST = f"{RESET_ALL}\033[103m"
    _BG_BRIGHT_BLUE_RESET_FIRST = f"{RESET_ALL}\033[104m"
    _BG_BRIGHT_MAGENTA_RESET_FIRST = f"{RESET_ALL}\033[105m"
    _BG_BRIGHT_CYAN_RESET_FIRST = f"{RESET_ALL}\033[106m"
    _BG_BRIGHT_WHITE_RESET_FIRST = f"{RESET_ALL}\033[107m"

    FG_DEFAULT_COLOR = "\033[39m"
    BG_DEFAULT_COLOR = "\033[49m"


class TerminalStyle:
    RESET_ALL = "\033[0m"

    FONT_BOLD = "\033[1m"
    FONT_BOLD_OFF = "\033[22m"
    FONT_UNDERLINE = "\033[4m"
    FONT_UNDERLINE_OFF = "\033[24m"
    FONT_LIGHT = "\033[2m"
    _FONT_ITALIC = "\033[3m"
    _FONT_ITALIC_OFF = "\033[23m"

    BLINKING_SLOW = "\033[5m"
    BLINKING_RAPID = "\033[6m"
    BLINKING_OFF = "\033[25m"

    FONT_BOLD_RESET_FIRST = f"{RESET_ALL}\033[1m"
    FONT_BOLD_OFF_RESET_FIRST = f"{RESET_ALL}\033[22m"
    FONT_UNDERLINE_RESET_FIRST = f"{RESET_ALL}\033[4m"
    FONT_UNDERLINE_OFF_RESET_FIRST = f"{RESET_ALL}\033[24m"
    FONT_LIGHT_RESET_FIRST = f"{RESET_ALL}\033[2m"
    _FONT_ITALIC_RESET_FIRST = f"{RESET_ALL}\033[3m"
    _FONT_ITALIC_OFF_RESET_FIRST = f"{RESET_ALL}\033[23m"

    BLINKING_SLOW_RESET_FIRST = f"{RESET_ALL}\033[5m"
    BLINKING_RAPID_RESET_FIRST = f"{RESET_ALL}\033[6m"
    BLINKING_OFF_RESET_FIRST = f"{RESET_ALL}\033[25m"

    REVERSED = "\033[7m"
    REVERSED_OFF = "\033[27m"


class TerminalUtility:

    @staticmethod
    def WarningMessage(message: str, arguments: list = None, print_only: bool = True, warning_type: type = RuntimeWarning, call_stack_show: bool = False, exception_raised: bool = False, variables: list = None, **kwargs):
        """
        Prints a warning message to the terminal.
        If you want to highlight some part of the message, all #1, #2, #3... characters will be replaced with the corresponding string in the argument list.
        Arguments will be highlighted in red.

        Args:
            message (str): Warning message.
            arguments (list, optional): List of arguments to be included in the warning message. Defaults to None.
            print_only (bool, optional): If True, only prints the warning message to the terminal. Defaults to True.
            warning_type (type, optional): Type of warning to be raised. Defaults to RuntimeWarning. print_only must be False for this to work.
            **kwargs: Additional keyword arguments to be passed to the warning message.
                warning_message_color: (str, optional): Color of the warning message. Defaults to TerminalColors.FG_YELLOW.
                warning_arguments_color: (str, optional): Color of the warning arguments. Defaults to TerminalColors.FG_RED.
                warning_message_info_text: (str, optional): Additional text to be included in the warning message. Defaults to "Application message:".
                warning_message_info_color: (str, optional): Color of the warning message information. Defaults to TerminalColors.FG_BLUE.
                warning_header_body_color: (str, optional): Color of the warning header/body. Defaults to TerminalColors.FG_CYAN.
                warning_header_values_color: (str, optional): Color of the warning header values. Defaults to TerminalColors.FG_GREEN.
                warning_frame_color: (str, optional): Color of the warning frame. Defaults to TerminalColors.FG_BLUE.
                argument_quote: (str, optional): Quote character to be used for bounding warning arguments. Defaults to ['"', '"']
                warning_quote_color: (str, optional): Color of the warning arguments bounding quote. Defaults to TerminalColors.FG_GREEN.

                call_stack_title_text: (str, optional): Text to be included in the call stack title. Defaults to "Call stack:".
                call_stack_title_color: (str, optional): Color of the call stack title. Defaults to TerminalColors.FG_BLUE.
                call_stack_show_filename: (bool, optional): If True, the filename will be included in the call stack. Defaults to False.
                call_stack_filename_color: (str, optional): Color of the filename in the call stack. Defaults to TerminalColors._FG_GRAY.
                call_stack_module_color: (str, optional): Color of the module in the call stack. Defaults to TerminalColors.FG_CYAN.
                call_stack_class_color: (str, optional): Color of the class in the call stack. Defaults to TerminalColors.FG_CYAN.
                call_stack_function_color: (str, optional): Color of the function in the call stack. Defaults to TerminalColors.FG_CYAN.
                call_stack_last_function_color: (str, optional): Color of the last function in the call stack. Defaults to TerminalColors.FG_MAGENTA.
                call_stack_line_number_color: (str, optional): Color of the line number in the call stack. Defaults to TerminalColors.FG_YELLOW.
                call_stack_show_line_content: (bool, optional): If True, the line content will be included in the call stack. Defaults to True.
                call_stack_line_content_color: (str, optional): Color of the line content in the call stack. Defaults to TerminalColors.FG_GREEN.
                call_stack_line_content_indent: (int, optional): Indentation level of the line content in the call stack. Defaults to 0.
                call_stack_boundaries_color: (str, optional): Color of the boundaries in the call stack. Defaults to TerminalColors.FG_WHITE.

        Returns:
            None
        """

        i = True if not exception_raised else False
        LogHandler.add_log_record(message=message, arguments=arguments, exception_raised=exception_raised, warning_raised=i, variables=variables)

        def insert_arguments(text: str, default_text_color: str = None, arguments: list = None, highlight_color: str = None, boundaries: list = None, boundaries_highlight_color: str = None) -> str:
            if not arguments:
                return text
            if not default_text_color:
                default_text_color = ""
            if not highlight_color:
                highlight_color = ""
            if not boundaries:
                boundaries = ['', '']
            if not boundaries_highlight_color:
                boundaries_highlight_color = ""
            
            has_replacements = True
            while has_replacements:
                count = 1
                has_replacements = False
                for argument in arguments:
                    if len(arguments) < 10:
                        replace_string = "#" + str(count)
                    else:
                        replace_string = "#" + "0" * len(str(count)) + str(count)
                        if text.find(replace_string) == -1:
                            replace_string = "#" + str(count)

                    if text.find(replace_string) != -1:
                        has_replacements = True
                    
                    text = text.replace(replace_string, f'{boundaries_highlight_color}{boundaries[0]}{highlight_color}{argument}{boundaries_highlight_color}{boundaries[1]}{default_text_color}', 1)
                    count += 1
            
            return text

        def fix_message_width(message: str, max_width: int) -> str:
            msg_list = []
            for i in message.splitlines():
                if len(i) <= max_width:
                    msg_list.append(i)
                    continue

                while len(i) > max_width:
                    pos = i.rfind(" ", 0, max_width)
                    if pos == -1:
                        pos = i.rfind("#", 0, max_width)
                    if pos == -1:
                        pos = max_width
                    
                    msg_list.append(i[:pos])
                    i = i[pos:]
                
                msg_list.append(i)

            return "\n".join(msg_list)

        def get_call_stack(func_frame) -> list:
            call_stack = []
            while func_frame:
                func_name = func_frame.f_code.co_name
                func_filename = func_frame.f_code.co_filename
                func_lineno = func_frame.f_lineno
                # Get content of line with line number func_lineno
                
                frame_source, _ = inspect.findsource(func_frame)
                if frame_source:
                    func_content = frame_source
                else:
                    func_content = []
                # print (len(func_content))
                func_line_content = func_content[func_lineno - 1] if func_lineno > 1 and len(func_content) > func_lineno - 1 else "Cannot get content of line !"
                func_module = inspect.getmodule(func_frame).__name__ if inspect.getmodule(func_frame) else "None"
                func_class = func_frame.f_locals.get("self", None).__class__.__name__ if func_frame.f_locals.get("self", None) else "None"
                call_stack.append({
                    "filename": func_filename,
                    "module": func_module,
                    "class": func_class,
                    "function": func_name,
                    "line_content": func_line_content.strip(),
                    "line_number": func_lineno
                })
                func_frame = func_frame.f_back
            return call_stack


        
        call_stack_show = kwargs.get("call_stack_show") if kwargs.get("call_stack_show") else call_stack_show
        print_only = kwargs.get("print_only") if kwargs.get("print_only") else print_only
        warning_type = kwargs.get("warning_type") if kwargs.get("warning_type") else warning_type
        
        warning_message_color = kwargs.get("warning_message_color") if kwargs.get("warning_message_color") else TerminalColors.FG_YELLOW_RESET_FIRST
        warning_arguments_color = kwargs.get("warning_arguments_color") if kwargs.get("warning_arguments_color") else TerminalColors.FG_RED_RESET_FIRST
        warning_quote_color = kwargs.get("warning_quote_color") if kwargs.get("warning_quote_color") else TerminalColors.FG_GREEN_RESET_FIRST
        warning_message_info_text = kwargs.get("warning_message_info_text") if kwargs.get("warning_message_info_text") else "Application message:"
        warning_message_info_color = kwargs.get("warning_message_info_color") if kwargs.get("warning_message_info_color") else TerminalColors.FG_BLUE_RESET_FIRST
        warning_header_body_color = kwargs.get("warning_header_body_color") if kwargs.get("warning_header_body_color") else TerminalColors.FG_CYAN_RESET_FIRST
        warning_header_values_color = kwargs.get("warning_header_values_color") if kwargs.get("warning_header_values_color") else TerminalColors.FG_GREEN_RESET_FIRST
        warning_frame_color = kwargs.get("warning_header_frame_color") if kwargs.get("warning_header_frame_color") else TerminalColors.FG_BLUE_RESET_FIRST
        argument_quote = kwargs.get("argument_quote") if kwargs.get("argument_quote") else ['"', '"']
        max_message_width = kwargs.get("max_message_width") if kwargs.get("max_message_width") else 120
        call_stack_title_text = kwargs.get("call_stack_title_text") if kwargs.get("call_stack_title_text") else "Call stack:"
        call_stack_title_color = kwargs.get("call_stack_title_color") if kwargs.get("call_stack_title_color") else TerminalColors.FG_BLUE_RESET_FIRST
        call_stack_show_filename = kwargs.get("call_stack_show_filename") if kwargs.get("call_stack_show_filename") else True
        call_stack_filename_color = kwargs.get("call_stack_filename_color") if kwargs.get("call_stack_filename_color") else TerminalColors._FG_GRAY_RESET_FIRST
        call_stack_show_module = kwargs.get("call_stack_show_module") if kwargs.get("call_stack_show_module") else True
        call_stack_module_color = kwargs.get("call_stack_module_color") if kwargs.get("call_stack_module_color") else TerminalColors.FG_CYAN_RESET_FIRST
        call_stack_show_class = kwargs.get("call_stack_show_class") if kwargs.get("call_stack_show_class") else True
        call_stack_class_color = kwargs.get("call_stack_class_color") if kwargs.get("call_stack_class_color") else TerminalColors.FG_CYAN_RESET_FIRST
        call_stack_show_function = kwargs.get("call_stack_show_function") if kwargs.get("call_stack_show_function") else True
        call_stack_function_color = kwargs.get("call_stack_function_color") if kwargs.get("call_stack_function_color") else TerminalColors.FG_CYAN_RESET_FIRST
        call_stack_last_function_color = kwargs.get("call_stack_last_function_color") if kwargs.get("call_stack_last_function_color") else TerminalColors.FG_MAGENTA_RESET_FIRST
        call_stack_line_number_color = kwargs.get("call_stack_line_number_color") if kwargs.get("call_stack_line_number_color") else TerminalColors.FG_YELLOW_RESET_FIRST
        call_stack_show_line_content = kwargs.get("call_stack_show_line_content") if kwargs.get("call_stack_show_line_content") else True
        call_stack_line_content_color = kwargs.get("call_stack_line_content_color") if kwargs.get("call_stack_line_content_color") else TerminalColors.FG_GREEN_RESET_FIRST
        call_stack_line_content_indent = kwargs.get("call_stack_line_content_indent") if kwargs.get("call_stack_line_content_indent") else 0
        call_stack_boundaries_color = kwargs.get("call_stack_boundaries_color") if kwargs.get("call_stack_boundaries_color") else TerminalColors.FG_WHITE_RESET_FIRST

        if exception_raised:
            call_stack_show = True
            summary_frame_title = "Error source details"
        else:
            summary_frame_title = "Warning source details"

        # Resolve Quote
        left_boundary = '"'
        right_boundary = '"'
        if isinstance(argument_quote, str):
            if len(argument_quote) == 0:
                left_boundary = ""
                right_boundary = ""
            elif len(argument_quote) % 2 == 0:
                left_boundary = argument_quote[:int(len(argument_quote)/2)]
                right_boundary = argument_quote[int(len(argument_quote)/2):]
            else:
                left_boundary = argument_quote
                right_boundary = argument_quote
        elif isinstance(argument_quote, list) or isinstance(argument_quote, tuple):
            if len(argument_quote) == 1:
                left_boundary = argument_quote[0]
                right_boundary = argument_quote[0]
            elif len(argument_quote) == 2:
                left_boundary = argument_quote[0]
                right_boundary = argument_quote[1]

        message = fix_message_width(message, max_message_width)

        warning_message_info_text = "Application message:"
        message_info_delimiter_text = "-" * len(warning_message_info_text)
        # Detail frame horizontal offset
        offset = 6
        # Detail frame left padding
        left_padding = 2
        # Spacing between detail frame and message frame
        spacing = 5

        
        # CREATE DETAIL FRAME
        
        caller_module_text = "Undefined"
        caller_class = "Undefined"
        caller_function = "Undefined"
        caller_line_number = "Undefined"
        
        # Fill data from caller function
        try:
            caller_frame = inspect.currentframe().f_back
            caller_module = inspect.getmodule(caller_frame) if inspect.getmodule(caller_frame) else "None"
            caller_module_text = caller_module.__name__
            caller_class = caller_frame.f_locals.get('self').__class__.__name__ if 'self' in caller_frame.f_locals else "None"
            caller_function = caller_frame.f_code.co_name
            caller_line_number = str(caller_frame.f_lineno)
        except:
            pass

        # Define detail frame items
        caller_module_text = warning_header_body_color + "Caller Module: " + warning_header_values_color + caller_module_text
        caller_class = warning_header_body_color + "Caller Class: " + warning_header_values_color + caller_class
        caller_function = warning_header_body_color + "Caller Function: " + warning_header_values_color + caller_function
        caller_line_number = warning_header_body_color + "Caller Line Number: " + warning_header_values_color + caller_line_number

        # Define detail frame items text length
        len_caller_module_text = len(caller_module_text) - len(warning_header_body_color) - len(warning_header_values_color)
        len_caller_class = len(caller_class) - len(warning_header_body_color) - len(warning_header_values_color)
        len_caller_function = len(caller_function) - len(warning_header_body_color) - len(warning_header_values_color)
        len_caller_line_number = len(caller_line_number) - len(warning_header_body_color) - len(warning_header_values_color)

        # Find max length for detail frame
        detail_frame_width = max(len(summary_frame_title), len_caller_module_text, len_caller_class, len_caller_function, len_caller_line_number) + offset

        # Create detail frame
        detail_frame = f"""

{warning_frame_color}╔{"═" * detail_frame_width}╗
{warning_frame_color}║{summary_frame_title.center(detail_frame_width)}║
{warning_frame_color}║{"-" * detail_frame_width}║
{warning_frame_color}║{" " * left_padding}{caller_module_text}{warning_frame_color}{" " * (detail_frame_width - len_caller_module_text - left_padding)}║
{warning_frame_color}║{" " * left_padding}{caller_class}{warning_frame_color}{" " * (detail_frame_width - len_caller_class - left_padding)}║
{warning_frame_color}║{" " * left_padding}{caller_function}{warning_frame_color}{" " * (detail_frame_width - len_caller_function - left_padding)}║
{warning_frame_color}║{" " * left_padding}{caller_line_number}{warning_frame_color}{" " * (detail_frame_width - len_caller_line_number - left_padding)}║
{warning_frame_color}╚{"═" * detail_frame_width}╝

"""

        detail_frame = detail_frame.strip()

        # CREATE MESSAGE FRAME
        
        # Define message frame items and find max text length
        tmp_message = message
        if arguments:
            if isinstance(arguments, str):
                arguments = [arguments]
            
            tmp_message = insert_arguments(text=tmp_message, arguments=arguments, boundaries=[left_boundary, right_boundary])

            len_message = 0
            for i in tmp_message.splitlines():
                len_message = max(len_message, len(i))
        else:
            len_message = len(message)

        # Set Time/Date text
        time_text = f"Time: {datetime.now().strftime('%H:%M:%S')}    Date: {datetime.now().strftime('%d.%m.%Y')}"
        len_time_text = len(time_text)

        time_text = f"{warning_header_body_color}Time: {warning_header_values_color}{datetime.now().strftime('%H:%M:%S')}    {warning_header_body_color}Date: {warning_header_values_color}{datetime.now().strftime('%d.%m.%Y')}"

        # Find max length for message frame
        message_width = max(len_message, len_time_text, len(warning_message_info_text))

        # Add colors to message arguments
        if arguments:
            if isinstance(arguments, str):
                arguments = [arguments]
            
            message = insert_arguments(
                text=message,
                default_text_color=warning_message_color,
                arguments=arguments,
                highlight_color=warning_arguments_color,
                boundaries=[left_boundary, right_boundary],
                boundaries_highlight_color=warning_quote_color)
            
        # Create message text
        message_text = ""
        for count, message_line in enumerate(message.splitlines()):
            fill_string = " " * (message_width - len(tmp_message.splitlines()[count]))
            message_text += f"{warning_frame_color}│{warning_message_color}{message_line}{fill_string}{warning_frame_color}│\n"

        message_frame = f"""
{warning_frame_color}┌{"─" * message_width}┐
{warning_frame_color}│{time_text}{" " * (message_width - len_time_text)}{warning_frame_color}│
{warning_frame_color}├{"─" * message_width}┤
{warning_frame_color}│{warning_message_info_color}{warning_message_info_text.ljust(message_width)}{warning_frame_color}│
{warning_frame_color}│{warning_header_body_color}{message_info_delimiter_text.ljust(message_width)}{warning_frame_color}│
{message_text}{warning_frame_color}└{"─" * message_width}┘

"""
        
        message_frame = message_frame.strip()
        
        # Combine detail and message frames
        header_frame_lines = detail_frame.splitlines()
        message_frame_lines = message_frame.splitlines()

        count = 0
        final_message_text = ""
        while True:
            if count >= len(header_frame_lines) and count >= len(message_frame_lines):
                break

            if count >= len(header_frame_lines):
                header_frame_line = " " * (detail_frame_width + 2) + " " * spacing
            else:
                header_frame_line = header_frame_lines[count] + " " * spacing
            
            if count >= len(message_frame_lines):
                message_frame_line = ""
            else:
                message_frame_line = message_frame_lines[count]
            
            final_message_text += f"{header_frame_line}{message_frame_line}\n"

            count += 1

        # CREATE CALL STACK INFO
        call_stack_list = get_call_stack(inspect.currentframe().f_back)
        call_stack_text = ""
        call_stack_module_width = max([len(i["module"]) for i in call_stack_list]) if call_stack_list else 0
        call_stack_class_width = max([len(i["class"]) for i in call_stack_list]) if call_stack_list else 0
        call_stack_function_width = max([len(f"{i['function']}   in line {i['line_number']}") for i in call_stack_list]) if call_stack_list else 0
        
        call_stack_text = f"\n{call_stack_title_color}{call_stack_title_text} {call_stack_boundaries_color}({len(call_stack_list)})"

        if not call_stack_list:
            call_stack_text += TerminalColors.FG_RED_RESET_FIRST + "\nCall stack is empty."

        call_stack_is_first_line = True
        for i in call_stack_list:
            fill_string = " " * (call_stack_function_width - len(f"{i['function']} in line {i['line_number']}"))
            call_stack_line = ""
            if call_stack_show_module:
                call_stack_line += f"{call_stack_module_color}{i['module'].rjust(call_stack_module_width)}{call_stack_boundaries_color} :: "
            if call_stack_show_class:
                call_stack_line += f"{call_stack_class_color}{i['class'].rjust(call_stack_class_width)}{call_stack_boundaries_color} :: "
            if call_stack_show_function:
                if call_stack_is_first_line:
                    call_stack_line += f"{call_stack_last_function_color}{i['function']}{call_stack_boundaries_color} in line {call_stack_line_number_color}{i['line_number']}{fill_string}{call_stack_boundaries_color} :: "
                    call_stack_is_first_line = False
                else:
                    call_stack_line += f"{call_stack_function_color}{i['function']}{call_stack_boundaries_color} in line {call_stack_line_number_color}{i['line_number']}{fill_string}{call_stack_boundaries_color} :: "
            if call_stack_show_filename:
                call_stack_line += f"{call_stack_filename_color}{i['filename']}"
            if call_stack_show_line_content:
                call_stack_line += f"\n{' ' * call_stack_line_content_indent}{call_stack_line_content_color}{i['line_content']}"

            call_stack_text += "\n" + call_stack_line.strip() + "\n"

        if not call_stack_show:
            call_stack_text = ""
        
        # Add exception raised text if exception raised
        if exception_raised:
            exception_raised_text = TerminalColors.BG_RED_RESET_FIRST + TerminalStyle._FONT_ITALIC + "Exception occurred, application execution may not be possible!" + TerminalColors.RESET_ALL + "\n"
        else:
            exception_raised_text = ""

        # Finalize message text
        print ()
        final_message_text = final_message_text.strip() + call_stack_text + exception_raised_text + TerminalColors.RESET_ALL + "\n"
        
        if print_only:
            print(final_message_text.strip())
        else:
            try:
                warnings.warn(final_message_text, warning_type)
            except:
                final_message_text = f"{final_message_text}\n{TerminalColors.BG_RED_RESET_FIRST}NOTE: Failed to show warning message type:\n{TerminalColors.FG_RED_RESET_FIRST}{warning_type}{TerminalColors.RESET_ALL}\n"
                print(final_message_text)


