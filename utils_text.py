from typing import Union, Any
from cyrtranslit import to_latin
import html as HtmlLib
import difflib


class TextUtility:
    END_OF_WORD = [" ", ",", ":", ";", ".", "!", "?", "\n", "\t", "(", ")", "/", "@", "#", "\"", "'", "{", "}", "[", "]", "_", "-", "*", "&", "^", "$", "+", "=", "|", "<", ">"]
    END_OF_SENTENCE = [".", "!", "?", "\n"]

    @staticmethod
    def get_integer(text: Union[str, int, float], on_error_return: Any = None) -> int:
        try:
            if isinstance(text, str):
                text = text.replace(",", "")
            result = int(text)
        except:
            result = on_error_return
        return result

    @staticmethod
    def get_float(text: Union[str, int, float], on_error_return: Any = None) -> float:
        try:
            if isinstance(text, str):
                text = text.replace(",", "")
            result = float(text)
        except:
            result = on_error_return
        return result

    @staticmethod
    def is_integer_possible(text: Union[str, int, float]) -> bool:
        try:
            _ = int(text)
            result = True
        except:
            result = False
        return result

    @staticmethod
    def is_float_possible(text: Union[str, int, float]) -> bool:
        try:
            _ = float(text)
            result = True
        except:
            result = False
        return result

    @staticmethod
    def replace_special_chars(text: str, replace_with: str = " ") -> str:
        if not text:
            return ""
        
        return "".join([x if x.isalnum() else replace_with for x in text])

    @staticmethod
    def is_special_char(character: str) -> bool | None:
        if not character:
            return None

        return not character.isalnum()

    @staticmethod
    def shrink_text(text: str, shrink_to_len: int, ratio_start_end: tuple = (80, 20), non_visible_replace_with: str = ".....", replace_chars_map: list = None) -> str:
        """
        shrink_to_len (int): shrink text to this length
        ratio_start_end (tuple): (start ratio (0-100), end ratio (0-100)) portion of text to keep
        non_visible_replace_with (str): text to replace non visible characters
        replace_chars_map (list): list of tuples (replace_char, replace_with)
        """

        if replace_chars_map:
            for item in replace_chars_map:
                text = text.replace(item[0], item[1])
        
        if len(text) <= shrink_to_len:
            return text
        if len(text) <= len(non_visible_replace_with):
            return text

        start_len = int((ratio_start_end[0] * shrink_to_len) / 100)
        end_len = int((ratio_start_end[1] * shrink_to_len) / 100)

        start_text = text[:start_len]
        if end_len == 0:
            end_text = ""
        else:
            end_text = text[-end_len:]

        result = start_text + non_visible_replace_with + end_text

        while len(result) > shrink_to_len:
            if end_text:
                end_text = end_text[1:]
            elif start_text:
                start_text = start_text[:-1]
            else:
                from utils_terminal import TerminalUtility
                TerminalUtility.WarningMessage(
                    message="#1: Error in #1 function.\nCannot shrink text.",
                    arguments=["TextUtility", "shrink_text"],
                    variables=[
                        ["start_len", start_len],
                        ["start_text", start_text],
                        ["end_len", end_len],
                        ["end_text", end_text],
                        ["result", result],
                        ["shrink_to_len", shrink_to_len],
                        ["non_visible_replace_with", non_visible_replace_with]
                    ]
                )
                break
            
            result = start_text + non_visible_replace_with + end_text
        
        return result

    @staticmethod
    def cyrillic_to_latin(text: str) -> str:
        return to_latin(text)

    @staticmethod
    def clear_serbian_chars(text: str = None, keep_same_length: bool = False) -> str:
        if text is None:
            return None
        
        replace_table = [
            ["ć", "c"],
            ["č", "c"],
            ["š", "s"],
            ["ž", "z"],
            ["Ć", "c"],
            ["Č", "c"],
            ["Š", "S"],
            ["Ž", "Z"]
        ]
        if keep_same_length:
            replace_table.append(["đ", "d"])
            replace_table.append(["Đ", "D"])
        else:
            replace_table.append(["đ", "dj"])
            replace_table.append(["Đ", "Dj"])
        
        for i in replace_table:
            text = text.replace(i[0], i[1])
        return text

    @staticmethod
    def has_serbian_chars(text: str) -> bool:
        serbian_table = [
            ["ć", "c"],
            ["č", "c"],
            ["š", "s"],
            ["ž", "z"],
            ["Ć", "c"],
            ["Č", "c"],
            ["Š", "S"],
            ["Ž", "Z"],
            ["đ", "dj"],
            ["Đ", "Dj"]
        ]

        for i in serbian_table:
            if i[0] in text:
                return True
        return False

    @staticmethod
    def get_text_lines_without_serbian_chars(text: str, return_only_lines_that_contain_serbian_letters: bool = True, line_delimiter: str = "\n", if_data_exist_add_string_at_end: str = "", ignore_if_line_already_exist: bool = False) -> str:
        if not text:
            return ""

        lines = text.split(line_delimiter)
        result = []

        for line in lines:
            if not TextUtility.has_serbian_chars(line):
                if return_only_lines_that_contain_serbian_letters:
                    continue
            new_line = TextUtility.clear_serbian_chars(line)
            if ignore_if_line_already_exist and new_line in lines:
                continue
            
            result.append(new_line)

        if if_data_exist_add_string_at_end:
            result.append(if_data_exist_add_string_at_end)

        return line_delimiter.join(result)

    @staticmethod
    def get_raw_text_from_html(html: str) -> str:
        html = html.replace("<", "\n<")
        html = html.replace(">", ">\n")
        html = html.lstrip("\n")

        text = ""
        for line in html.splitlines():
            if line.startswith("<"):
                continue
            if line.startswith("<br>"):
                text += "\n"
                continue
            text += HtmlLib.unescape(line)
        
        return text

    @staticmethod
    def count_sentences(text: str) -> int:
        if text is None:
            return 0
        
        for char in TextUtility.END_OF_SENTENCE:
            text = text.replace(char, "\n")

        while True:
            text = text.replace("\n\n", "\n")
            if text.find("\n\n") == -1:
                break

        text = text.strip()

        return len([x for x in text.split("\n") if x.strip()])

    @staticmethod
    def count_words(text: str) -> int:
        if text is None:
            return 0

        for char in TextUtility.END_OF_WORD:
            text = text.replace(char, " ")

        while True:
            text = text.replace("  ", " ")
            if text.find("  ") == -1:
                break

        text = text.strip()
        
        return len([x for x in text.split(" ") if x.strip()])
    
    @staticmethod
    def count_chars(text: str) -> int:
        if text is None:
            return 0
        return len(text)

    @staticmethod
    def count_lines(text: str) -> int:
        if text is None:
            return 0
        return len(text.splitlines())

    @staticmethod
    def count_expressions(text: str, expressions: Union[list, str], match_case: bool = False) -> int:
        if text is None:
            return 0
        if not expressions:
            return 0
        if isinstance(expressions, str):
            expressions = [expressions]

        count = 0
        for expression in expressions:
            if match_case:
                count += text.count(expression)
            else:
                count += text.lower().count(expression.lower())

        return count

    @staticmethod
    def to_number(number: Union[int, float, str, list, tuple, set]) -> Union[int, float, None]:
        if isinstance(number, (list, tuple, set)):
            number = len(number)
        elif isinstance(number, str):
            number = TextUtility.get_float(number)
            if number is None:
                return None
            if TextUtility.is_integer_possible(number):
                if number == int(number):
                    number = int(number)
        elif isinstance(number, int):
            pass
        elif isinstance(number, float):
            if number == int(number):
                number = int(number)
        else:
            number = None

        return number

    @staticmethod
    def number_to_string_formatted(number: Union[int, float, list, tuple, str, set], decimals: int = 0, add_thousand_separator: bool = True, on_error_return: Any = "Undefined") -> str:
        number = TextUtility.to_number(number)

        if number is None:
            return on_error_return

        if add_thousand_separator:
            return f"{number:,.{decimals}f}"
        else:
            return f"{number:.{decimals}f}"

    @staticmethod
    def percent_formatted_string(total: Union[int, float], part: Union[int, float], decimals: int = 2, include_percent_sign: bool = False, on_error_return: Any = "Undefined") -> str:
        """
        Calculates in what percent 'total' contains 'part'
        """

        total = TextUtility.to_number(total)
        part = TextUtility.to_number(part)

        if total is None or part is None:
            return on_error_return
        
        result = part / total if total else 0
        if include_percent_sign:
            return f"{TextUtility.number_to_string_formatted(result * 100, decimals)}%"
        else:
            return f"{TextUtility.number_to_string_formatted(result * 100, decimals)}"

    @staticmethod
    def percent_more_than_average_formatted_string(value: Union[int, float], average: Union[int, float], decimals: int = 2, include_percent_sign: bool = False, on_error_return: Any = "Undefined") -> str:
        """
        Calculates by how many percent "part" is greater than "total"
        """

        value = TextUtility.to_number(value)
        average = TextUtility.to_number(average)

        if value is None or average is None:
            return on_error_return
        
        result = ((value - average) / average) * 100 if value else 0

        if include_percent_sign:
            return f"{TextUtility.number_to_string_formatted(result, decimals)}%"
        else:
            return f"{TextUtility.number_to_string_formatted(result, decimals)}"

    @staticmethod
    def similarity_ratio(string1: str, string2: str) -> float:
        return difflib.SequenceMatcher(None, string1, string2).ratio()


class HTMLText:
    from utils_html_text import TextToHTML
    from utils_html_text import TextToHtmlRule
    from utils_html_text import ColorizeCode


