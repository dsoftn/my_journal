import urllib.request


class Utility:
    def __init__(self, html_code: str = None) -> None:
        self.html_code = self._quick_format_html(html_code)

    def load_html_code(self, html_code: str, dont_split_into_lines: bool = False):
        if not isinstance(html_code, str):
            raise TypeError("HTML Code must be in string format !")
        if not dont_split_into_lines:
            html_code = self._quick_format_html(html_code)
        self.html_code = html_code
    
    def _quick_format_html(self, html: str) -> str:
        if not html:
            return html
        
        html = html.replace("<", "\n<")
        html = html.replace(">", ">\n")
        
        html_clean = ""
        in_tag = False
        for line in html.splitlines():
            if line.startswith("<"):
                in_tag = True
            if line.endswith(">"):
                in_tag = False
            html_clean += line
            if not in_tag:
                html_clean += "\n"

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
                mark = rule[0] + '="'
                if mark not in tag_code:
                    return False
                else:
                    start = tag_code.find(mark)
                    end = tag_code.find('"', start + len(mark))
                    if end == -1:
                        return None
                    value = tag_code[start+len(mark):end]
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
        
        remove = [" ", "n"]
        if only_remove_double:
            if isinstance(only_remove_double, str):
                remove = [only_remove_double]
            elif isinstance(only_remove_double, list) or isinstance(only_remove_double, tuple) or isinstance(only_remove_double, set):
                remove = [x for x in only_remove_double]
            else:
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

    def crop_html_code(self, html_code: str, starting_lines: int = 1, ending_lines: int = 1) -> str:
        if not html_code:
            return ""
        
        html_code = self._quick_format_html(html_code)
        html_code_list = html_code.splitlines()

        start = starting_lines
        end = len(html_code_list) - ending_lines

        result = ""
        for line_idx in range(start, end):
            result += html_code_list[line_idx] + "\n"
        
        return result.strip()

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result

    def _get_float(self, text: str) -> float:
        result = None
        try:
            result = float(text)
        except:
            result = None
        return result


class AObject:
    def __init__(self,
                 a_href: str = None,
                 a_text: str = None,
                 a_class: str = None) -> None:
        
        self.a_href = a_href
        self.a_text = a_text
        self.a_class = a_class


class TagA(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

    def get_all_links(self) -> list:
        if not self.html_code:
            return []

        a_objects = []
        for code_segment in self._get_a_segments_from_code(self.html_code):
            a_obj = self._get_a_object(code_segment=code_segment)
            if a_obj:
                a_objects.append(a_obj)
        
        return a_objects

    def _get_a_object(self, code_segment: str) -> AObject:
        code_list = code_segment.split("\n")

        link = ""
        txt = ""

        for line in code_list:
            if line.startswith("<a "):
                start = line.find('href="')
                if start == -1:
                    continue
                end = line.find('"', start + 6)
                if end == -1:
                    continue
                
                a_class = ""
                link = line[start+6:end]
                start = line.find('class="')
                if start != -1:
                    end = line.find('"', start+7)
                    if end != -1:
                        a_class = line[start+7:end]
            
            if not line.startswith("<"):
                txt += line

        if link.startswith(("http", "/", "ftp", ".")):
            result = AObject(a_href=link, a_text=txt, a_class=a_class)
        else:
            result = None

        return result

    def _get_a_segments_from_code(self, html_code: str) -> list:
        result = []
        in_tag = False
        txt = ""
        for line in html_code.split("\n"):
            if line.startswith("<a ") and line.endswith(">"):
                in_tag = True
                txt += line + "\n"
                continue
                
            if line.startswith("</a>"):
                in_tag = False
                txt += line
                result.append(txt.strip())
                txt = ""
            
            if in_tag:
                txt += line + "\n"

        if txt:
            result.append(txt.strip())

        return result


class ImageObject:
    def __init__(self,
                 img_src: str = None,
                 img_x: int = None,
                 img_y: int = None,
                 img_width: int = None,
                 img_height: int = None,
                 img_alt: str = None,
                 img_title: str = None,
                 img_id: str = None,
                 img_class: str = None) -> None:
        
        self.img_src = img_src
        self.img_x = img_x
        self.img_y = img_y
        self.img_width = img_width
        self.img_height = img_height
        self.img_alt = img_alt
        self.img_title = img_title
        self.img_id = img_id
        self.img_class = img_class


class TagIMG(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

    def get_all_images(self) -> list:
        if not self.html_code:
            return []

        img_objects = []
        for line in self._get_img_lines_from_code(self.html_code):
            img_objects.append(self._get_image_object(line))
        
        return img_objects

    def _get_img_lines_from_code(self, html_code: str) -> list:
        result = []
        for line in html_code.split("\n"):
            if line.startswith("<img") and line.endswith(">"):
                result.append(line)
        return result

    def _get_image_object(self, img_tag: str) -> ImageObject:
        img_obj = ImageObject()
        # src
        pos = img_tag.find('src="')
        if pos >= 0:
            end = img_tag.find('"', pos + 5)
            if end >= 0:
                img_obj.img_src = img_tag[pos+5:end]
        # x, y
        pos = img_tag.find('style="')
        if pos >= 0:
            end = img_tag.find('"', pos + 7)
            if end >= 0:
                style_list = [x.strip() for x in img_tag[pos+7:end].split(";")]
                for style in style_list:
                    if style.startswith("left:"):
                        number_txt = style[5:].replace("px", "")
                        number = self._get_integer(number_txt)
                        if number is not None:
                            img_obj.img_x = number
                    if style.startswith("top:"):
                        number_txt = style[4:].replace("px", "")
                        number = self._get_integer(number_txt)
                        if number is not None:
                            img_obj.img_y = number
        # width
        pos = img_tag.find('width="')
        if pos >= 0:
            end = img_tag.find('"', pos + 7)
            if end >= 0:
                number_txt = img_tag[pos+7:end].replace("px", "")
                number = self._get_integer(number_txt)
                if number is not None:
                    img_obj.img_width = number
        # height
        pos = img_tag.find('height="')
        if pos >= 0:
            end = img_tag.find('"', pos + 8)
            if end >= 0:
                number_txt = img_tag[pos+8:end].replace("px", "")
                number = self._get_integer(number_txt)
                if number is not None:
                    img_obj.img_height = number
        # alt
        pos = img_tag.find('alt="')
        if pos >= 0:
            end = img_tag.find('"', pos + 5)
            if end >= 0:
                img_obj.img_alt = img_tag[pos+5:end]
        # title
        pos = img_tag.find('title="')
        if pos >= 0:
            end = img_tag.find('"', pos + 7)
            if end >= 0:
                img_obj.img_title = img_tag[pos+7:end]
        # id
        pos = img_tag.find('id="')
        if pos >= 0:
            end = img_tag.find('"', pos + 4)
            if end >= 0:
                img_obj.img_id = img_tag[pos+4:end]
        # class
        pos = img_tag.find('class="')
        if pos >= 0:
            end = img_tag.find('"', pos + 7)
            if end >= 0:
                img_obj.img_class = img_tag[pos+7:end]

        return img_obj


class TextObject:
    def __init__(self,
                 txt_value: str = "",
                 txt_title: str = "",
                 txt_link: str = "",
                 txt_strong: bool = False,
                 tags: list = [],
                 eop :bool = False) -> None:
        self.txt_value = txt_value
        self.txt_title = txt_title
        self.txt_link = txt_link
        self.txt_strong = txt_strong
        self.tags = tags
        self.eop = eop  # End of paragraph tag </p>

    def get_tag(self, tag: str) -> str:
        if isinstance(tag, str):
            tag = "<" + tag.strip(" <>")
            tag = (tag + " ", tag + ">")
        elif isinstance(tag, list) or isinstance(tag, tuple):
            tag_search = []
            for i in tag:
                formated_tag = "<" + i.strip(" <>")
                tag_search.append(formated_tag + " ")
                tag_search.append(formated_tag + ">")
            tag = tuple(tag_search)
        else:
            raise TypeError(f"Invalid parameter type: tag must be string or list or tuple, not {type(tag)}")

        result = ""
        for i in self.tags:
            if i.startswith(tag):
                result += i + "   "
        return result
    
    def tokenize(self, preferred_token_lenght: int = None, use_smart_token_lenght: bool = True) -> list:
        if not self.txt_value:
            token_obj = self._create_text_object("")
            return [token_obj]
        
        txt = self.txt_value + " "
        tokens = [x + " " for x in txt.split(" ")]
        tokens.pop(-1)

        tokenized_text = []
        if not preferred_token_lenght:
            for token in tokens:
                token_obj = self._create_text_object(token)
                tokenized_text.append(token_obj)
            return tokenized_text
        
        if not use_smart_token_lenght:
            for token_idx in range(0, len(self.txt_value), preferred_token_lenght):
                txt = self.txt_value[token_idx:token_idx + preferred_token_lenght]
                token_obj = self._create_text_object(txt)
                tokenized_text.append(token_obj)
            return tokenized_text
        
        current_token = ""
        for token in tokens:
            current_token += token
            if len(current_token) >= preferred_token_lenght:
                tokenized_text.append(self._create_text_object(current_token))
                current_token = ""
        
        if current_token:
            tokenized_text.append(self._create_text_object(current_token))
        
        return tokenized_text
    
    def _create_text_object(self, text: str):
        text_obj = TextObject(txt_value=text,
                              txt_title=self.txt_title,
                              txt_link=self.txt_link,
                              txt_strong=self.txt_strong,
                              tags=self.tags,
                              eop=self.eop)
        return text_obj

class TagTEXT(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

    def get_all_text_slices(self) -> list:
        span_title = ""
        text_link = ""
        text_strong = False
        txt = ""
        slices = []
        tags = []
        for line in self.html_code.split("\n"):
            if not line.startswith("<"):
                if txt:
                    txt += " " + line.strip()
                else:
                    txt += line.strip()
            elif line.startswith("<br"):
                txt += "\n"
            else:
                if line.startswith("</") and txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                tags = self._check_tags(tags, line)

            if line.startswith(("<strong ", "<strong>")):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                text_strong = True
            
            if line.startswith(("</strong ", "</strong>")):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                text_strong = False

            if line.startswith("<a "):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                text_link = self._get_link(line)
            
            if line.startswith(("</a ", "</a>")):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                text_link = ""

            if line.startswith(("<span", "<div")):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                span_title = self._span_title(line)

            if line.startswith(("</span", "</div")):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                span_title = ""

            if line.startswith(("<p>", "<p ", "</p>")):
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
                    txt = ""
                slices.append(TextObject(txt_value="\n", txt_title="", txt_link="", txt_strong=False, tags=[], eop=True))
            

        if txt.strip():
            slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False))
        
        return slices

    def _check_tags(self, tags_list: list, line: str) -> list:
        tags = list(tags_list)
        
        if not line.startswith("</"):
            tags.append(line)
            return tags
        
        tags.reverse()

        if line.count(" "):
            line = line[:line.find(" ")]
        line = line.strip("<>/ ")
        remove_tag = ("<" + line + " ", "<" + line + ">")
        remove_index = None
        for idx, tag in enumerate(tags):
            if tag.startswith(remove_tag):
                remove_index = idx
                break
        if remove_index is not None:
            tags.pop(remove_index)
        
        tags.reverse()
        return tags





    def _get_link(self, line: str) -> str:
        pos = line.find('href="')
        if pos == -1:
            return ""

        end = line.find('"', pos + 6)
        if end == -1:
            return ""
        
        return line[pos+6:end]

    def get_raw_text(self) -> str:
        txt = ""
        for line in self.html_code.split("\n"):
            if not line.startswith("<"):
                txt += line.strip()
            elif line.startswith("<br"):
                txt += "\n"
            else:
                txt += " "
        return txt
    
    def _span_title(self, code_line: str) -> str:
        result = ""
        pos = code_line.find('title="')
        if pos >= 0:
            end = code_line.find('"', pos + 7)
            if end >= 0:
                result = code_line[pos+7:end]
        return result


class TableObject:
    def __init__(self):
        self.table = {}
        self._last_row = None
        self._last_col = None
        self.cur_cell = None
    
    def add_rows(self, number_of_rows: int = 1) -> int:
        if number_of_rows < 1:
            return None
        if self._last_row is None:
            self.table["0"] = {"0": self._empty_cell()}
            self._last_col = 0
            self._last_row = 0
            number_of_rows -= 1
        
        for y in range(self._last_row + 1, self._last_row + number_of_rows + 1):
            self.table[str(y)] = {}
            for x in range(self._last_col + 1):
                self.table[str(y)][str(x)] = self._empty_cell()

        self._last_row += number_of_rows
        return self._last_row

    def add_cols(self, number_of_columns: int = 1) -> int:
        if number_of_columns < 1:
            return None
        if self._last_col is None:
            self.table["0"] = {"0": self._empty_cell()}
            self._last_col = 0
            self._last_row = 0
            number_of_columns -= 1
        
        for x in range(self._last_col + 1, self._last_col + number_of_columns + 1):
            for y in range(self._last_row + 1):
                self.table[str(y)][str(x)] = self._empty_cell()

        self._last_col += number_of_columns
        return self._last_col

    def _empty_cell(self) -> dict:
        result = {
            "value": "",
            "type": "text",
            "data": {
                "images": [],
                "text_slices": [],
                "links": [],
                "head": False,
                "row_span": 1,
                "col_span": 1
            }
        }
        return result

    def add_cell(self, x: int = None, y: int = None, value: str = "", cell_type: str = "text", cell_data = None, auto_extend_table: bool = True):
        if x is None or y is None:
            if self.cur_cell is None:
                raise ValueError("Current cell is not set, unable to add new cell. You must specify x and y coordinates.")
            else:
                x = self.cur_cell[0] + 1
                y = self.cur_cell[1]
                if x > self._last_col:
                    x = 0
                    y += 1
                if y > self._last_row and auto_extend_table:
                    y = self.add_rows()
                else:
                    raise ValueError("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.")
        if self._last_col is None or  x > self._last_col:
            if auto_extend_table:
                if self._last_col is None:
                    correction = -1
                else:
                    correction = self._last_col
                self.add_cols(x - correction)
            else:
                raise ValueError("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.")
        if self._last_row is None or y > self._last_row:
            if auto_extend_table:
                if self._last_row is None:
                    correction = -1
                else:
                    correction = self._last_row
                self.add_rows(y - correction)
            else:
                raise ValueError("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.")
        
        self.table[str(y)][str(x)] = {"value": value, "type": cell_type, "data": cell_data}
        self.cur_cell = (x, y)

    def get_current_cell(self) -> dict:
        return self.table[str(self.cur_cell[0])][str(self.cur_cell[1])]
    
    def get_current_cell_position(self) -> tuple:
        return self.cur_cell

    def cell(self, x: int = None, y: int = None) -> dict:
        if x is None:
            if self.cur_cell:
                x = self.cur_cell[0]
            else:
                raise ValueError(f"Cell position ({x}, {y}) outside of table bounds. You must specify x and y coordinates or extend the table first.")
        
        if y is None:
            if self.cur_cell:
                y = self.cur_cell[1]
            else:
                raise ValueError(f"Cell position ({x}, {y}) outside of table bounds. You must specify x and y coordinates or extend the table first.")
        
        return self.table[str(y)][str(x)]

    def set_current_cell(self, x: int, y: int):
        if str(y) in self.table and str(x) in self.table[str(y)]:
            self.cur_cell = (x, y)
        else:
            raise ValueError(f"Cell ({x}, {y}) does not exist in table")
        
    def normalize_table(self) -> tuple:
        if self._last_col is None or self._last_row is None:
            return None
        
        max_cols = 0
        max_rows = 0
        
        for row in self.table:
            row_has_data = False
            for col in self.table[row]:
                if self.table[row][col] is not None and (self.table[row][col]["value"] or self.table[row][col]["data"]["images"] or self.table[row][col]["data"]["text_slices"]):
                    row_has_data = True
                    max_cols = max(max_cols, int(col))
            
            if row_has_data:
                max_rows = max(max_rows, int(row))

        for i in range(max_rows + 1, len(self.table)):
            self.table.pop(str(i))
        for row in self.table:
            for i in range(max_cols + 1, len(self.table[row])):
                self.table[row].pop(str(i))

        return (max_cols, max_rows)
        
    def has_table(self) -> bool:
        return bool(self.table)


class TagTABLE(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

        self.tables = None

    def get_all_tables(self) -> list:
        if not self.html_code:
            return []
        
        self.tables = []

        table_code_segments = self._get_table_code_segments(self.html_code)

        for code_segment in table_code_segments:
            table_obj = self._get_table_object_from_code(code_segment)
            if table_obj.has_table():
                self.tables.append(table_obj)
        
        return self.tables

    def _get_table_object_from_code(self, html_code: str) -> TableObject:
        table_obj = TableObject()

        row = -1
        col = -1
        row_span = 0
        col_span = 0
        thead = False
        th = False
        cell_code = ""
        for line in html_code.split("\n"):
            if line.startswith("<tr"):
                cell_code = ""
                row += 1
                col = -1
                row_span = self._span_value(line)
                continue
            if line.startswith("<td"):
                cell_code = ""
                col += 1
                col_span = self._span_value(line)
                continue
            if line.startswith(("<th>", "<th ")):
                cell_code = ""
                col += 1
                col_span = self._span_value(line)
                th = True
                continue
            
            if line.startswith("</tr"):
                if row_span:
                    row += row_span - 1
                    if row > table_obj._last_row:
                        table_obj.add_rows(row - table_obj._last_row)
                row_span = 0

            if line.startswith("</td"):
                cell = self._cell_dict(cell_code)
                cell["data"]["head"] = th
                cell["data"]["row_span"] = row_span
                cell["data"]["col_span"] = col_span
                
                table_obj.add_cell(x=col,
                                    y=row,
                                    value=cell["value"],
                                    cell_type=cell["type"],
                                    cell_data=cell["data"])
                if col_span:
                    col += col_span - 1
                    if col > table_obj._last_col:
                        table_obj.add_cols(col - table_obj._last_col)
                col_span = 0

            if line.startswith("</th>", ):
                cell = self._cell_dict(cell_code)
                cell["data"]["head"] = th
                cell["data"]["row_span"] = row_span
                cell["data"]["col_span"] = col_span
                
                table_obj.add_cell(x=col,
                                    y=row,
                                    value=cell["value"],
                                    cell_type=cell["type"],
                                    cell_data=cell["data"])
                if col_span:
                    col += col_span - 1
                    if col > table_obj._last_col:
                        table_obj.add_cols(col - table_obj._last_col)
                col_span = 0
                th = False

            cell_code += line + "\n"

        return table_obj

    def _cell_dict(self, cell_code: str) -> dict:
        result = {
            "value": "",
            "type": "text",
            "data": {
                "images": [],
                "text_slices": [],
                "links": [],
                "head": False,
                "row_span": 1,
                "col_span": 1
            }
        }
        
        tag_images = TagIMG(cell_code)
        images = tag_images.get_all_images()

        tag_text = TagTEXT(cell_code)
        text_slices = tag_text.get_all_text_slices()
        text = tag_text.get_raw_text()

        a_tag = TagA(cell_code)
        links = a_tag.get_all_links()

        if images:
            result["data"]["images"] = images
            result["type"] = "img"
            if text:
                result["data"]["text_slices"] = text_slices
                result["type"] = "mix"
        
        result["value"] = text
        result["data"]["text_slices"] = text_slices
        result["data"]["links"] = links
        
        return result

    def _span_value(self, code_line: str, default_value: int = 1) -> int:
        result = 1
        pos = code_line.find('span="')
        if pos >=0:
            end = code_line.find('"', pos + 6)
            if end >=0:
                result = self._get_integer(code_line[pos+6:end])
        if result is None:
            return 1
        else:
            return result

    def _get_table_code_segments(self, html_code: str) -> list:
        """Parses HTML code and returns a list of table code segments"""
        
        table_code = ""
        table_segments = []
        
        in_table = True
        for line in html_code.split("\n"):
            if line.startswith("<table"):
                in_table = True
                table_code += line + "\n"
                continue

            if in_table:
                table_code += line + "\n"
                if line.startswith("</table>"):
                    table_segments.append(table_code)
                    table_code = ""
                    in_table = False
        if in_table:
            table_segments.append(table_code)

        return table_segments


class ListObject:
    def __init__(self,
                 text: str = "",
                 title: str = "",
                 sub_items = None,
                 text_slices: list = None,
                 images: list = None,
                 links: list = None) -> None:
        
        self.text = text
        self.title = title
        
        if sub_items is None:
            self.sub_items = []
        else:
            self.sub_items = sub_items
        
        if text_slices is None:
            self.text_slices = []
        else:
            self.text_slices = text_slices
        
        if images is None:
            self.images = []
        else:
            self.images = images

        if links is None:
            self.links = []
        else:
            self.links = links

    def get_image_url(self, img_object: ImageObject = None) -> str:
        if img_object:
            return img_object.img_src
        else:
            if self.images:
                return self.images[0].img_src
        return ""
        
    def get_link_url(self, link_object: AObject = None) -> str:
        if link_object:
            return link_object.a_href
        else:
            if self.links:
                return self.links[0].a_href
        return ""
        

class TagLIST(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

    def get_all_lists(self) -> list:
        code_segments = self._get_list_code_segments(self.html_code)

        result = []
        for segment in code_segments:
            result.append(self._get_segment_data(segment))
    
        return result

    def _get_segment_data(self, html_code: str, list_object: ListObject = None) -> ListObject:
        if not list_object:
            list_object = self._create_list_object(html_code)

        list_items_code = self._get_list_item_code_segments(html_code)

        for item_code in list_items_code:
            item = self._create_list_object(item_code)
            list_object.sub_items.append(item)
            item_code = self.crop_html_code(item_code)
            if self._get_list_code_segments(item_code) or self._get_list_item_code_segments(item_code):
                self._get_segment_data(item_code, item)
        
        return list_object

    def _create_list_object(self, html_code: str) -> ListObject:
        # Crop html
        html_code = self._crop_list_html_code(html_code)

        # Remove other segments from html
        html_code = self.remove_specific_tag(html_code, "li", multiline=True)
        html_code = self.remove_specific_tag(html_code, "ul", multiline=True)
        html_code = self.remove_specific_tag(html_code, "ol", multiline=True)

        obj = ListObject()
        title = ""

        # Text
        text_parser = TagTEXT(html_code)
        obj.text = text_parser.get_raw_text()
        obj.text_slices = text_parser.get_all_text_slices()
        for i in obj.text_slices:
            if i.txt_title:
                title += i.txt_title + "\n"

        # Images
        img_parser = TagIMG(html_code)
        obj.images = img_parser.get_all_images()
        for i in obj.images:
            if i.img_title:
                title += i.img_title + "\n"

        # Links
        link_parser = TagA(html_code)
        obj.links = link_parser.get_all_links()

        return obj

    def _crop_list_html_code(self, html_code: str) -> str:
        crop_start = 0
        crop_end = 0
        if html_code.startswith(("<li ", "<li>", "<ul ", "<ul>", "<ol ", "<ol>")):
            crop_start = 1
        if html_code.endswith(("</li>", "</ul>", "</ol>")):
            crop_end = 1
        
        html_code = self.crop_html_code(html_code=html_code, starting_lines=crop_start, ending_lines=crop_end)
        return html_code

    def _get_list_item_code_segments(self, html_code: str) -> list:
        list_start = ("<li ", "<li>")
        list_end = "</li>"
        return self._extract_code_segments(html_code, list_start, list_end)

    def _get_list_code_segments(self, html_code: str) -> list:
        list_start = ("<ul ", "<ul>", "<ol ", "<ol>")
        list_end = ("</ul>", "</ol>")
        return self._extract_code_segments(html_code, list_start, list_end)

    def _extract_code_segments(self, html_code: str, list_start, list_end) -> list:
        lists = []
        list_code = ""
        in_list = 0
        
        for line in html_code.split("\n"):
            if line.startswith(list_start):
                in_list += 1

            if in_list:
                list_code += line + "\n"
            
            if line.endswith(list_end) and in_list:
                in_list -= 1
                if not in_list:
                    lists.append(list_code.strip())
                    list_code = ""

        return lists


class HtmlParser(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

        # Define Tags
        self.tag_img = TagIMG()
        self.tables = TagTABLE()
        self.text = TagTEXT()
        self.alink = TagA()
        self.tag_list = TagLIST()

    def get_all_links(self) -> list:
        if not self.html_code:
            return []
        
        self.alink.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.alink.get_all_links()

    def get_all_images(self) -> list:
        if not self.html_code:
            return []
        
        self.tag_img.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.tag_img.get_all_images()

    def get_all_lists(self) -> list:
        if not self.html_code:
            return []
        
        self.tag_list.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.tag_list.get_all_lists()

    def get_all_tables(self) -> list:
        if not self.html_code:
            return []
        
        self.tables.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.tables.get_all_tables()
    
    def get_all_text_slices(self) -> list:
        if not self.html_code:
            return []

        self.text.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.text.get_all_text_slices()

    def get_raw_text(self) -> str:
        if not self.html_code:
            return ""

        self.text.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.text.get_raw_text()

    def get_PYQT5_table_widget(self, 
                               table_object: TableObject, 
                               parent_widget = None, 
                               font_size: int = 12, 
                               remove_cell_if_contains: list = None, 
                               images_website: str = None, 
                               table_width: int = None, 
                               table_height: int = None, 
                               scrollbars_on: bool = True, 
                               feedback_function = None, 
                               split_text_slices_into_lines: bool = False):

        if not table_object.has_table():
            return None
        
        table_object = table_object.table
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
        from PyQt5.QtGui import QPixmap, QFontMetrics, QIcon, QColor
        from PyQt5.QtCore import QSize, Qt

        def set_cell_item(tbl: QTableWidget, cell_data: dict, qtable_row: int, qtable_col: int, no_image_download: bool = False) -> QTableWidget:
            fm = QFontMetrics(tbl.font())
            fm_height = fm.height() + 5
            cell_w = 0
            cell_h = 0
            tt = ""
            
            if cell_data["data"]["images"] and not no_image_download:
                url: str = cell_data["data"]["images"][0].img_src
                if not url.startswith("https:"):
                    if url.startswith("//"):
                        if images_website:
                            url = images_website.rstrip("/") + "/" + url.lstrip("/")
                        else:
                            url = "https:" + url
                    else:
                        if images_website:
                            url = images_website + url
                img = None
                try:
                    response = urllib.request.urlopen(url, timeout=2)
                    mime_type = response.info().get_content_type()
                    if mime_type and mime_type.startswith("image/"):
                        img = QPixmap()
                        img.loadFromData(response.read())
                except:
                    img = None
                
                img_w = 50
                img_h = 50
                if cell_data["data"]["images"][0].img_width:
                    img_w = cell_data["data"]["images"][0].img_width
                if cell_data["data"]["images"][0].img_height:
                    img_w = cell_data["data"]["images"][0].img_height
                
                tt += cell_data["data"]["images"][0].img_title + "\n"
                for i in range(1, len(cell_data["data"]["text_slices"])):
                    tt += cell_data["data"]["text_slices"][i].txt_title + "\n"
                tt = tt.strip()

                cell_h = fm_height * (cell_data["value"].count("\n") + 1)
                cell_w = fm.width(cell_data["value"]) + 15
                
                cell_item = QTableWidgetItem()
                cell_item.setText(cell_data["value"])
                cell_item.setToolTip(tt)

                if img:
                    img = img.scaled(img_w, img_h, Qt.KeepAspectRatio)
                    cell_item.setIcon(QIcon(img))
                    cell_item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                    tbl.setIconSize(img.size())
                    cell_h = max(cell_h, img_h)
                    cell_w += img_w + 10
            else:
                for i in range(len(cell_data["data"]["text_slices"])):
                    tt += cell_data["data"]["text_slices"][i].txt_title + "\n"
                tt = tt.strip()

                cell_h = fm_height * (cell_data["value"].count("\n") + 1)
                cell_w = fm.width(cell_data["value"]) + 15
                cell_item = QTableWidgetItem()
                cell_item.setText(cell_data["value"])
                cell_item.setToolTip(tt)

            if cell_data["data"]["links"]:
                link_txt = ""
                for link in cell_data["data"]["links"]:
                    link_txt += link.a_href + "\n"
                cell_item.setData(Qt.UserRole, link_txt.strip())
            else:
                cell_item.setData(Qt.UserRole, "")

            tbl.setItem(qtable_row, qtable_col, cell_item)
            tbl.item(qtable_row, qtable_col).setSizeHint(QSize(cell_w, cell_h))

            tbl.setColumnWidth(qtable_col, max(tbl.columnWidth(qtable_col), cell_w))
            tbl.setRowHeight(qtable_row, max(tbl.rowHeight(qtable_row), cell_h))
        

        qtable = QTableWidget(parent_widget)

        palette = qtable.palette()
        qtable.verticalHeader().setPalette(palette)
        qtable.horizontalHeader().setPalette(palette)

        # Removes unwanted cells
        if remove_cell_if_contains:
            for item in remove_cell_if_contains:
                for row in table_object:
                    for col in table_object[row]:
                        if table_object[row][col]["value"].find(item) >= 0:
                            table_object[row][col]["value"] = ""
                            table_object[row][col]["data"]["images"] = []
                            table_object[row][col]["data"]["text_slices"] = []
                            table_object[row][col]["data"]["links"] = []

        # Set font
        font = qtable.font()
        font.setPointSize(font_size)
        qtable.setFont(font)
        fm = QFontMetrics(font)
        fm_height = fm.height() + 5

        # Get Headers
        row_headers = []
        has_row_header = False
        first_cell = True
        for row in table_object:
            if table_object[row]["0"]["data"]["head"]:
                if not first_cell:
                    has_row_header = True
                else:
                    if table_object[row]["0"]["data"]["row_span"] > 1:
                        has_row_header = True
                    first_cell = False
                row_headers.append([table_object[row]["0"]["value"], table_object[row]["0"]["data"]["row_span"]])

        col_headers = []
        has_col_header = False
        first_cell = True
        for col in table_object["0"]:
            if table_object["0"][col]["data"]["head"]:
                if not first_cell:
                    has_col_header = True
                else:
                    if table_object["0"][col]["data"]["col_span"] > 1:
                        has_col_header = True
                    first_cell = False
                col_headers.append([table_object["0"][col]["value"], table_object["0"][col]["data"]["col_span"]])

        # Set table size
        row_count = len(table_object)
        col_count = len(table_object["0"])
        if has_col_header:
            qtable.setRowCount(row_count - 1)
        else:
            qtable.setRowCount(row_count)
        if has_row_header:
            qtable.setColumnCount(col_count - 1)
        else:
            qtable.setColumnCount(col_count)

        # Set headers
        
        if has_row_header:
            for i in range(len(row_headers)):
                if row_headers[i][1] > 1:
                    qtable.verticalHeader().setVisible(False)
                    qtable.setColumnCount(col_count)
                    has_row_header = False
                    row_headers = []
                    break
        else:
            qtable.verticalHeader().setVisible(False)

        if has_col_header:
            for i in range(len(col_headers)):
                if col_headers[i][1] > 1:
                    qtable.horizontalHeader().setVisible(False)
                    qtable.setRowCount(row_count)
                    has_col_header = False
                    col_headers = []
                    break
            if has_col_header:
                if has_row_header:
                    col_headers.pop(0)
                qtable.setHorizontalHeaderLabels([x[0] for x in col_headers])
                qtable.horizontalHeader().setFont(font)
        else:
            qtable.horizontalHeader().setVisible(False)

        if has_row_header:
            if has_col_header:
                row_headers.pop(0)
            qtable.setVerticalHeaderLabels([x[0] for x in row_headers])
            qtable.verticalHeader().setFont(font)

        # Determine the size of rows and columns
        font.setBold(True)
        row_sizes = []
        for row in table_object:
            row_sizes.append(fm_height)
        col_sizes = []
        for col in table_object["0"]:
            col_sizes.append(fm.width("MM"))

        for row in table_object:
            r_size = [row_sizes[int(row)]]
            r_size.append(fm_height)
            for col in table_object[row]:
                r_size.append(fm_height * (table_object[row][col]["value"].count("\n") + 1))
                c_size = [col_sizes[int(col)]]
                for i in table_object[row][col]["value"].splitlines():
                    c_size.append(fm.width(i) + 10)
                for i in table_object[row][col]["data"]["images"]:
                    if i.img_width:
                        c_size.append(i.img_width)
                    if i.img_height:
                        r_size.append(i.img_height + (len(table_object[row][col]["data"]["text_slices"]) + table_object[row][col]["value"].count("\n")) * fm_height)
                col_sizes[int(col)] = max(c_size)
            row_sizes[int(row)] = max(r_size)
        # Set column and row sizes
        start = 0
        if has_col_header:
            start = 1
        for i in range(start, len(row_sizes)):
            qtable.setRowHeight(i, row_sizes[i])
        start = 0
        if has_row_header:
            start = 1
        for i in range(start, len(col_sizes)):
            qtable.setColumnWidth(i, col_sizes[i])

        # Fill with data
        start_row = 0
        start_col = 0
        if has_row_header:
            start_col = 1
        if has_col_header:
            start_row = 1
        
        count = 0
        total_count = row_count * col_count
        no_image_download = False
        for row in range(start_row, len(table_object)):
            qtable_row = row
            if has_col_header:
                qtable_row = row - 1
            for col in range(start_col, len(table_object["0"])):
                qtable_col = col
                if has_row_header:
                    qtable_col = col - 1
                
                if split_text_slices_into_lines:
                    txt = ""
                    for txt_slice in table_object[str(row)][str(col)]["data"]["text_slices"]:
                        txt += txt_slice.txt_value + "\n"
                    txt = txt.strip()
                    table_object[str(row)][str(col)]["value"] = txt

                item = set_cell_item(qtable, table_object[str(row)][str(col)], qtable_row, qtable_col, no_image_download=no_image_download)
                if feedback_function:
                    response = feedback_function((count, total_count))
                    count += 1
                    if not response:
                        no_image_download = True

        # Add span values
        for row in range(start_row, len(table_object)):
            qtable_row = row
            if has_col_header:
                qtable_row = row - 1
            for col in range(start_col, len(table_object["0"])):
                qtable_col = col
                if has_row_header:
                    qtable_col = col - 1
                if table_object[str(row)][str(col)]["data"]["row_span"] > 1 or table_object[str(row)][str(col)]["data"]["col_span"] > 1:
                    qtable.setSpan(qtable_row, qtable_col, table_object[str(row)][str(col)]["data"]["row_span"], table_object[str(row)][str(col)]["data"]["col_span"])
        
        # Set table size
        horizontal_spacing = qtable.frameWidth() * 2
        vertical_spacing = qtable.frameWidth() * 2

        width = sum(qtable.columnWidth(col) for col in range(qtable.columnCount())) + horizontal_spacing
        if has_row_header:
            width += max(qtable.verticalHeader().width(), col_sizes[0])
        height = sum(qtable.rowHeight(row) for row in range(qtable.rowCount())) + vertical_spacing
        if has_col_header:
            height += max(qtable.horizontalHeader().height(), row_sizes[0])
        qtable.resize(width, height)

        # Set ScrollBars visibility
        if not scrollbars_on:
            qtable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            qtable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set header stylesheet and table selection behavior
        qtable.setSelectionMode(QTableWidget.SingleSelection)
        header_stylesheet = "QHeaderView::section {color: yellow;background-color: green}"
        qtable.verticalHeader().setStyleSheet(header_stylesheet)
        qtable.horizontalHeader().setStyleSheet(header_stylesheet)

        return qtable






