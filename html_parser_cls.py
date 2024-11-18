import urllib.request
import requests
import html as HtmlLib

import UTILS


class Utility:
    ONE_LINE_TAGS = ["img", "/img", "link", "/link", "meta", "/meta", "t", "/t", "br", "/br"]

    def __init__(self, html_code: str = None) -> None:
        self.special_case_rules = ""
        self.html_code = self._quick_format_html(html_code)

    def load_html_code(self, html_code: str, dont_split_into_lines: bool = False):
        if not isinstance(html_code, str):
            UTILS.TerminalUtility.WarningMessage("HTML Code must be in string format !\ntype(html_code): #1\nhtml_code = #2", [str(type(html_code)), html_code], exception_raised=True)
            raise TypeError("HTML Code must be in string format !")
        if self.html_code == html_code:
            return
        if not dont_split_into_lines:
            html_code = self._quick_format_html(html_code)
        self.html_code = html_code
    
    def _quick_format_html(self, html: str) -> str:
        if not html:
            return html
        
        html = html.replace("<", "\n<")
        html = html.replace(">", ">\n")
        
        if self.special_case_rules == "wikipedia":
            html_clean = html
        else:
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

    def remove_tags(self,
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
                 multiline: bool = None,
                 return_line_numbers: bool = False,
                 return_line_numbers_with_links: bool = False) -> str:

        html_code = self._quick_format_html(html_code)

        if not tag or not html_code:
            return ""
        
        if multiline is None:
            if tag in self.ONE_LINE_TAGS:
                multiline = False
            else:
                multiline = True
        
        tag_rules = [
            ["id", tag_id_contains], 
            ["class", tag_class_contains],
            ["title", tag_title_contains],
            ["property", tag_property_contains],
            ["content", tag_content_contains],
            ["type", tag_type_contains],
            ["name", tag_name_contains]
        ]
        remove_from_rules = []
        for idx, rule in enumerate(tag_rules):
            if rule[1] is None:
                remove_from_rules.append(idx)
        remove_from_rules.sort(reverse=True)
        for idx in remove_from_rules:
            tag_rules.pop(idx)
            
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
        counter = 0
        for line in html_list:
            if line.startswith(tag):
                if in_main_tag:
                    in_tag += 1
                elif self._is_tag_mark_valid(line, tag_rules):
                    in_main_tag = True
                    in_tag += 1
                    
            if not in_main_tag:
                tag_code += line + "\n"

            if line.endswith(end_tag) and in_tag:
                if in_main_tag:
                    in_tag -= 1
                    if not in_tag:
                        in_main_tag = False
            
            counter += 1

        return tag_code

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
                 multiline: bool = None,
                 return_line_numbers: bool = False,
                 return_line_numbers_with_links: bool = False,
                 return_exact_code: bool = False) -> list:
        
        html_code = self._quick_format_html(html_code)

        if not tag or not html_code:
            return ""
        
        if multiline is None:
            if tag in self.ONE_LINE_TAGS:
                multiline = False
            else:
                multiline = True
        
        tag_rules = [
            ["id", tag_id_contains], 
            ["class", tag_class_contains],
            ["title", tag_title_contains],
            ["property", tag_property_contains],
            ["content", tag_content_contains],
            ["type", tag_type_contains],
            ["name", tag_name_contains]
        ]
        remove_from_rules = []
        for idx, rule in enumerate(tag_rules):
            if rule[1] is None:
                remove_from_rules.append(idx)
        remove_from_rules.sort(reverse=True)
        for idx in remove_from_rules:
            tag_rules.pop(idx)
            
        if custom_tag_property:
            try:
                for tag_property in custom_tag_property:
                    tag_rules.append([tag_property[0], tag_property[1]])
            except Exception as e:
                print (f"Invalid custom_tag_property: {e}")

        if return_exact_code:
            html_list = [x for x in html_code.split("\n")]
        else:
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
        counter = 0
        start_line_number = 0
        link = ""
        for line in html_list:
            if return_line_numbers_with_links:
                if line.startswith("<a "):
                    link = self.get_tag_property_value(html_code=line, tag_property="href")
                if line.startswith("</a"):
                    link = ""

            if line.startswith(tag):
                if in_main_tag:
                    in_tag += 1
                elif self._is_tag_mark_valid(line, tag_rules):
                    in_main_tag = True
                    in_tag += 1
                    start_line_number = counter
                    if line.endswith("/>"):
                        in_tag -= 1
                        in_main_tag = False
                        tag_code += line + "\n"
                        
                        if not return_exact_code:
                            tag_code = tag_code.strip()

                        if return_line_numbers:
                            result.append([tag_code, start_line_number, counter])
                            start_line_number = counter
                        elif return_line_numbers_with_links:
                            result.append([tag_code, start_line_number, counter, link])
                            start_line_number = counter
                        else:
                            result.append(tag_code)
                        tag_code = ""
                    
            if line.endswith(end_tag) and in_tag:
                if in_main_tag:
                    in_tag -= 1
                    if not in_tag:
                        tag_code += line + "\n"
                        
                        if not return_exact_code:
                            tag_code = tag_code.strip()

                        if return_line_numbers:
                            result.append([tag_code, start_line_number, counter])
                            start_line_number = counter
                        elif return_line_numbers_with_links:
                            result.append([tag_code, start_line_number, counter, link])
                            start_line_number = counter
                        else:
                            result.append(tag_code)
                        tag_code = ""
                        in_main_tag = False
            
            if in_main_tag:
                tag_code += line + "\n"
            
            counter += 1

        return result
    
    def _is_tag_mark_valid(self, tag_code: str, rules: list, matchcase: bool = True) -> bool:
        tag_prop = self._get_tag_properties(tag_code, return_none_if_data_not_valid=False)
        for rule in rules:
            if not matchcase:
                if rule[0]:
                    rule[0] = rule[0].lower()
                if rule[1]:
                    rule[1] = rule[1].lower()

            is_valid = False
            if rule[1] is None or (rule[1].startswith(("'", '"')) and rule[1].endswith(("'", '"'))):
                for i in tag_prop:
                    if not matchcase:
                        if i[0]:
                            i[0] = i[0].lower()
                        if i[1]:
                            i[1] = i[1].lower()
                    if rule[0] == i[0] and rule[1].strip("'\"") == i[1].strip("'\""):
                        is_valid = True
                        break
                if is_valid:
                    continue
                else:
                    return False
            
            for i in tag_prop:
                if not matchcase:
                    if i[0]:
                        i[0] = i[0].lower()
                    if i[1]:
                        i[1] = i[1].lower()
                if rule[0] == i[0] and self._contains(i[1], rule[1]):
                    is_valid = True
                    break
            if is_valid:
                continue
            else:
                return False
        
        return True
            
    def _contains(self, text: str, contain_string: str) -> bool:
        if text is None and contain_string is None:
            return True
        if text is None and contain_string is not None:
            return False
        if text is not None and contain_string is None:
            return False
        if text and not contain_string:
            return True

        if contain_string in text:
            return True
        else:
            return False

    def _get_tag_properties(self, tag_line: str, return_none_if_data_not_valid: bool = True, skip_comments: bool = True) -> list:
        if return_none_if_data_not_valid:
            data_not_found = None
        else:
            data_not_found = []

        result = []
        
        if not tag_line:
            return data_not_found
        tag_lines = tag_line.splitlines()
        for tag_string in tag_lines:
            if tag_string.startswith("<!") and skip_comments:
                continue
            if tag_string.strip():
                tag_line = tag_string
                break
        else:
            return data_not_found
        
        tag_line = tag_line.strip()
        if not tag_line.startswith("<") or not tag_line.endswith(">"):
            return data_not_found
        
        pos = tag_line.find(" ")
        if pos == -1:
            return result
        tag_line = tag_line[pos+1:]
        
        pos = 0
        pos_end = len(tag_line) - 1
        while pos < pos_end:
            val_delim = [pos_end]

            start_pos = pos

            pos_space = tag_line.find(" ", pos)
            if pos_space != -1:
                val_delim.append(pos_space)

            pos_equal = tag_line.find("=", pos)
            if pos_equal != -1:
                val_delim.append(pos_equal)

            pos = min(val_delim)
            value_mark = tag_line[pos]
            tag_property = tag_line[start_pos:pos].strip()

            if value_mark == ">":
                if tag_property:
                    result.append([tag_property, None])
                pos = pos_end
            elif value_mark == " ":
                if tag_property:
                    result.append([tag_property, None])
                pos = pos_space + 1
            elif value_mark == "=":
                pos = pos_equal + 1
                while True:
                    if tag_line[pos] == " ":
                        pos += 1
                    else:
                        break
                value_container = " "
                if tag_line[pos] in "'\"":
                    value_container = tag_line[pos]
                    pos += 1
                end = tag_line.find(value_container, pos)
                if end == -1:
                    end = pos_end
                value = tag_line[pos:end]
                end += 1
                pos = end
                result.append([tag_property, value])

        return result

    def remove_specific_tag(self, html_code: str, tag: str, multiline: bool = None) -> str:
        if multiline is None:
            if tag in self.ONE_LINE_TAGS:
                multiline = False
            else:
                multiline = True

        html_code = self._quick_format_html(html_code)

        if not tag:
            return html_code
        
        if multiline:
            end_tag = "</" + tag.strip(" ><") + ">"
        else:
            end_tag = ">"

        tag = ("<" + tag.strip(" ><") + " ", "<" + tag.strip(" ><") + ">")

        result = ""
        in_tag = 0
        for line in html_code.splitlines():
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
                UTILS.TerminalUtility.WarningMessage("Variable #1 must be a string, list, tuple or set.\ntype(only_remove_double): #2\nonly_remove_double = #3", ["only_remove_double", type(only_remove_double), only_remove_double], exception_raised=True)
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

    def get_tag_property_value(self, html_code: str, tag: str = None, tag_property: str = None, return_first: bool = True):
        if not html_code:
            return None
        
        if not tag_property:
            UTILS.TerminalUtility.WarningMessage("Tag property must be defined !\ntag_property = #1", [tag_property], exception_raised=True)
            raise ValueError("Tag property must be defined !")
        
        if tag is None:
            tag = ""
        if tag_property is None:
            tag_property = ""
        
        html_code = self._quick_format_html(html_code)

        prop_values = []
        for line in html_code.splitlines():
            if line.startswith("<" + tag):
                prop_values += self._get_tag_property_value(line, tag_property)
        
        if return_first:
            if prop_values:
                return prop_values[0]
            else:
                return ""
        else:
            return prop_values
    
    def _get_tag_property_value(self, code_line: str, tag_property: str) -> list:
        prop_values = []

        start = code_line.find(tag_property + "=")
        if start != -1:
            bound_char = " "
            if code_line[start+len(tag_property)+1] in "\"'":
                bound_char = code_line[start+len(tag_property)+1]
            end = code_line.find(bound_char, start + len(tag_property) + 2)
            if end == -1:
                end = code_line.find(">", start + len(tag_property))
            if end != -1:
                value = code_line[start+len(tag_property)+2:end].strip(" '\"")
                prop_values.append(value)
        return prop_values
        

class AObject:
    def __init__(self,
                 a_href: str = None,
                 a_text: str = None,
                 a_class: str = None,
                 a_title: str = None) -> None:
        
        self.a_href = a_href
        self.a_text = a_text
        self.a_class = a_class
        self.a_title = a_title


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
                link = line[start+6:end]

                a_class = ""
                start = line.find('class="')
                if start != -1:
                    end = line.find('"', start+7)
                    if end != -1:
                        a_class = line[start+7:end]

                a_title = ""
                start = line.find('title="')
                if start != -1:
                    end = line.find('"', start+7)
                    if end != -1:
                        a_title = line[start+7:end]

            if not line.startswith("<"):
                txt += line

        if link.startswith(("http", "/", "ftp", ".")):
            result = AObject(a_href=link, a_text=txt, a_class=a_class, a_title=a_title)
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
                 img_width_ex: int = None,
                 img_height: int = None,
                 img_height_ex: int = None,
                 img_alt: str = None,
                 img_title: str = None,
                 img_id: str = None,
                 img_class: str = None,
                 img_link: str = None,
                 img_link_title: str = None,
                 img_link_class: str = None,
                 tag_list: str = None,
                 in_tag_pos: int = None) -> None:
        
        self.img_src = img_src
        self.img_x = img_x
        self.img_y = img_y
        self.img_width = img_width
        self.img_height = img_height
        self.img_width_ex = img_width_ex
        self.img_height_ex = img_height_ex
        self.img_alt = img_alt
        self.img_title = img_title
        self.img_id = img_id
        self.img_class = img_class
        self.img_link = img_link
        self.img_link_title = img_link_title
        self.img_link_class = img_link_class
        self.tag_list = tag_list
        self.in_tag_pos = in_tag_pos


class TagIMG(Utility):
    def __init__(self, html_code: str = None):
        super().__init__(html_code=html_code)

    def get_all_images(self) -> list:
        if not self.html_code:
            return []

        img_objects = []
        for line in self._get_img_lines_from_code(self.html_code):
            img_objects.append(self._get_image_object(line[0], line[1], line[2], line[3], line[4], line[5]))
        
        return img_objects

    def _get_img_lines_from_code(self, html_code: str) -> list:
        result = []
        link = ""
        link_title = ""
        link_class = ""
        tags = []
        count = 0
        for line in html_code.split("\n"):
            if line.startswith("<"):
                if line.startswith("</"):
                    tag_to_pop = None
                    for idx, i in enumerate(tags):
                        tag = line.replace("/", "").rstrip(" >")
                        if i.startswith(tag):
                            tag_to_pop = idx
                    if tag_to_pop is not None:
                        tags.pop(tag_to_pop)
                else:
                    tags.append(line)

            if line.startswith("<a "):
                link = self.get_tag_property_value(html_code=line, tag_property="href")
                link_title = self.get_tag_property_value(html_code=line, tag_property="title")
                link_class = self.get_tag_property_value(html_code=line, tag_property="class")
            if line.startswith("</a"):
                link = ""
            if line.startswith("<img") and line.endswith(">"):
                result.append([line, link, link_title, link_class, "\n".join(tags), count])
            count += 1
        return result

    def _get_image_object(self, img_tag: str, link: str, link_title: str, link_class: str, tag_list: str, in_tag_pos: int) -> ImageObject:
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
                        number_txt = style[5:].replace("px", "").strip(" '\"")
                        number = self._get_integer(number_txt)
                        if number is not None:
                            img_obj.img_x = number
                    if style.startswith("top:"):
                        number_txt = style[4:].replace("px", "").strip(" '\"")
                        number = self._get_integer(number_txt)
                        if number is not None:
                            img_obj.img_y = number
                    if style.startswith("width:") and style.endswith("ex"):
                        number_txt = style[6:].replace("ex", "").strip(" '\"")
                        number = self._get_float(number_txt)
                        if number is not None:
                            img_obj.img_width_ex = number
                    if style.startswith("height:") and style.endswith("ex"):
                        number_txt = style[7:].replace("ex", "").strip(" '\"")
                        number = self._get_float(number_txt)
                        if number is not None:
                            img_obj.img_height_ex= number

        # width
        pos = img_tag.find('width=')
        if pos >= 0:
            end = img_tag.find(' ', pos + 6)
            if end == -1:
                end = img_tag.find('>', pos + 6)
            if end >= 0:
                number_txt = img_tag[pos+6:end].replace("px", "").strip(" '\"")
                number = self._get_integer(number_txt)
                if number is not None:
                    img_obj.img_width = number
        # height
        pos = img_tag.find('height=')
        if pos >= 0:
            end = img_tag.find(' ', pos + 7)
            if end == -1:
                end = img_tag.find('>', pos + 7)
            if end >= 0:
                number_txt = img_tag[pos+7:end].replace("px", "").strip(" '\"")
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

        img_obj.img_link = link
        img_obj.img_link_title = link_title
        img_obj.img_link_class = link_class
        img_obj.tag_list = tag_list
        img_obj.in_tag_pos = in_tag_pos
        return img_obj


class TextObject:
    def __init__(self,
                 txt_value: str = "",
                 txt_title: str = "",
                 txt_link: str = "",
                 txt_strong: bool = False,
                 tags: list = [],
                 position_map: list = [],
                 in_tag_pos: int = None,
                 eop :bool = False) -> None:
        self.txt_value = txt_value
        self.txt_title = txt_title
        self.txt_link = txt_link
        self.txt_strong = txt_strong
        self.tags = list(tags)
        self.position_map = list(position_map)
        self.in_tag_pos = in_tag_pos
        self.eop = eop  # End of paragraph tag </p>

    def get_tag(self, tag: str = "") -> str:
        if isinstance(tag, str):
            if tag == "":
                tag = "<"
            else:
                tag = "<" + tag.strip(" <>")
                tag = (tag + " ", tag + ">")
        elif isinstance(tag, list) or isinstance(tag, tuple):
            tag_search = []
            for i in tag:
                formated_tag = "<" + i.strip(" <>")
                tag_search.append(formated_tag + " ")
                tag_search.append(formated_tag + ">")
                if i == "":
                    tag_search.append(formated_tag)
            tag = tuple(tag_search)
        else:
            UTILS.TerminalUtility.WarningMessage("Invalid parameter type: Variable #1 must be string or list or tuple.\ntype(tag): #2\ntag = #3", ["tag", type(tag), tag], exception_raised=True)
            raise TypeError(f"Invalid parameter type: tag must be string or list or tuple, not {type(tag)}")

        result = ""
        for i in self.tags:
            if i.startswith(tag):
                result += i + "\n"
        return result

    def compare_are_objects_in_same_tag(self, tag: str, compare_with: 'TextObject', object_to_compare_with: 'TextObject' = None, ignore_scope: bool = False) -> bool:
        # Set maps
        map1 = compare_with.position_map
        if object_to_compare_with is None:
            map2 = self.position_map
        else:
            map2 = object_to_compare_with.position_map

        # Fix tag
        tag = tag.split(">")[0].strip("<").lower()
        tag = tag.split(" ")[0]

        # Create map list for tag
        compare1 = []
        compare2 = []

        in_tag = False
        for i in map1:
            if tag in i:
                in_tag = True
            if in_tag:
                if ignore_scope and i[0] != "root_tag":
                    compare1.append(i)
                else:
                    compare1.append(i)
        in_tag = False
        for i in map2:
            if tag in i:
                in_tag = True
            if in_tag:
                if ignore_scope and i[0] != "root_tag":
                    compare2.append(i)
                else:
                    compare2.append(i)

        # Compare maps
        if len(compare1) != len(compare2) and not ignore_scope:
            return False
        
        if not compare1 or not compare2:
            return None
        
        for i in zip(compare1, compare2):
            if i[0][0] != i[1][0]:
                return False
            else:
                if i[0][1] != i[1][1] and not ignore_scope:
                    return False

        return True

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
        position_map = [["root_tag", 0, 0, "This is root tag"]]
        count = 0
        for line in self.html_code.split("\n"):
            if not line.startswith("<"):
                if txt:
                    txt += " " + line.strip()
                else:
                    txt += line.strip()
            elif line.startswith("<br"):
                txt += "\n"
            else:
                if txt.strip():
                    slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map, in_tag_pos=count))
                    txt = ""
                tags = self._check_tags(tags, line)

            if line.startswith(("<strong ", "<strong>")):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                text_strong = True
            
            if line.startswith(("</strong ", "</strong>")):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                text_strong = False

            if line.startswith("<a "):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                text_link = self._get_link(line)
            
            if line.startswith(("</a ", "</a>")):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                text_link = ""

            if line.startswith(("<span", "<div")):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                span_title = self._span_title(line)

            if line.startswith(("</span", "</div")):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                span_title = ""

            if line.startswith(("<p>", "<p ", "</p>")):
                # if txt.strip():
                #     slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map))
                #     txt = ""
                slices.append(TextObject(txt_value="\n", txt_title="", txt_link="", txt_strong=False, tags=[], eop=True, position_map=position_map, in_tag_pos=count))
            
            self._update_position_map(line, position_map)
            count += 1

        if txt.strip():
            slices.append(TextObject(txt_value=txt.strip(), txt_title=span_title, txt_link=text_link, txt_strong=text_strong, tags=tags, eop=False, position_map=position_map, in_tag_pos=count))
        
        return slices

    def _update_position_map(self, line: str, position_map: list):
        """position map list structure:
            [0] = tag name
            [1] = self index
            [2] = children count
            [3] = full tag line
        """
        
        if not line.startswith("<"):
            return
        
        # Fix Tag
        tag = line.split(">")[0].strip("<").lower()
        tag = tag.split(" ")[0]

        # Check if tag is one line type
        if tag in self.ONE_LINE_TAGS:
            return
        
        # Case: Closing tag
        if tag.startswith("/"):
            tag = tag.strip("/")
            for idx, item in enumerate(position_map):
                if item[0] == tag:
                    position_map.pop(idx)
                    break
            return
        
        # Case: Opening tag
        if len(position_map):
            tag_item = [tag, position_map[0][2], 0, line]
            position_map[0][2] += 1
        else:
            tag_item = [tag, 0, 0, line]
        
        position_map.insert(0, tag_item)
        return

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
                UTILS.TerminalUtility.WarningMessage("Current cell is not set, unable to add new cell. You must specify x and y coordinates.\nx = #1\ny = #2\nself.cur_cell = #3", [x, y, self.cur_cell], exception_raised=True)
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
                    UTILS.TerminalUtility.WarningMessage("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.\nVariable #1 is set to #2, cannot add new row", ["auto_extend_table", auto_extend_table], exception_raised=True)
                    raise ValueError("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.")
        if self._last_col is None or  x > self._last_col:
            if auto_extend_table:
                if self._last_col is None:
                    correction = -1
                else:
                    correction = self._last_col
                self.add_cols(x - correction)
            else:
                UTILS.TerminalUtility.WarningMessage("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.\nVariable #1 is set to #2, cannot add new col", ["auto_extend_table", auto_extend_table], exception_raised=True)
                raise ValueError("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.")
        if self._last_row is None or y > self._last_row:
            if auto_extend_table:
                if self._last_row is None:
                    correction = -1
                else:
                    correction = self._last_row
                self.add_rows(y - correction)
            else:
                UTILS.TerminalUtility.WarningMessage("New cell position outside of table bounds. You must specify x and y coordinates or extend the table first.\nVariable #1 is set to #2, cannot add new cell", ["auto_extend_table", auto_extend_table], exception_raised=True)
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
                UTILS.TerminalUtility.WarningMessage("Cell position (#1, #2) outside of table bounds. You must specify x and y coordinates or extend the table first.", [x, y], exception_raised=True)
                raise ValueError(f"Cell position ({x}, {y}) outside of table bounds. You must specify x and y coordinates or extend the table first.")
        
        if y is None:
            if self.cur_cell:
                y = self.cur_cell[1]
            else:
                UTILS.TerminalUtility.WarningMessage("Cell position (#1, #2) outside of table bounds. You must specify x and y coordinates or extend the table first.", [x, y], exception_raised=True)
                raise ValueError(f"Cell position ({x}, {y}) outside of table bounds. You must specify x and y coordinates or extend the table first.")
        
        return self.table[str(y)][str(x)]

    def set_current_cell(self, x: int, y: int):
        if str(y) in self.table and str(x) in self.table[str(y)]:
            self.cur_cell = (x, y)
        else:
            UTILS.TerminalUtility.WarningMessage("Cell (#1, #2) does not exist in table", [x, y], exception_raised=True)
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
        pos = code_line.find('span=')
        if pos >=0:
            end = code_line.find(' ', pos + 5)
            if end == -1:
                end = code_line.find(">", pos + 5)
            if end >=0:
                result = self._get_integer(code_line[pos+5:end].strip(" '\""))
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

    def get_all_links(self, load_html_code: str = None) -> list:
        if load_html_code:
            self.load_html_code(load_html_code)
            
        if not self.html_code:
            return []
        
        self.alink.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.alink.get_all_links()

    def get_all_images(self, load_html_code: str = None) -> list:
        if load_html_code:
            self.load_html_code(load_html_code)
            
        if not self.html_code:
            return []
        
        self.tag_img.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.tag_img.get_all_images()

    def get_all_lists(self, load_html_code: str = None) -> list:
        if load_html_code:
            self.load_html_code(load_html_code)
            
        if not self.html_code:
            return []
        
        self.tag_list.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.tag_list.get_all_lists()

    def get_all_tables(self, load_html_code: str = None) -> list:
        if load_html_code:
            self.load_html_code(load_html_code)
            
        if not self.html_code:
            return []
        
        self.tables.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.tables.get_all_tables()
    
    def get_all_text_slices(self, load_html_code: str = None) -> list:
        if load_html_code:
            self.load_html_code(load_html_code)
            
        if not self.html_code:
            return []

        self.text.load_html_code(self.html_code, dont_split_into_lines=True)
        return self.text.get_all_text_slices()

    def get_raw_text(self, load_html_code: str = None) -> str:
        if load_html_code:
            self.load_html_code(load_html_code)
            
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
                               split_text_slices_into_lines: bool = False,
                               ignore_headers: bool = False,
                               smart_cell_width: bool = False):

        if not table_object.has_table():
            return None
        
        table_object = table_object.table
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
        from PyQt5.QtGui import QPixmap, QFontMetrics, QIcon
        from PyQt5.QtCore import QSize, Qt

        def set_cell_item(tbl: QTableWidget, cell_data: dict, qtable_row: int, qtable_col: int, no_image_download: bool = False, cell_max_width: int = None) -> QTableWidget:
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
                
                if cell_data["data"]["images"][0].img_title:
                    tt += cell_data["data"]["images"][0].img_title + "\n"
                for i in range(1, len(cell_data["data"]["text_slices"])):
                    tt += cell_data["data"]["text_slices"][i].txt_title + "\n"
                tt = tt.strip()

                cell_item = QTableWidgetItem()
                cell_val = cell_data["value"]
                if cell_max_width:
                    words = cell_val.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        candidate_line = current_line + " " + word if current_line else word
                        width = fm.boundingRect(candidate_line).width()

                        if width <= cell_max_width:
                            current_line = candidate_line
                        else:
                            lines.append(current_line.strip())
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    cell_val = "\n".join(lines)

                cell_h = fm_height * (cell_val.count("\n") + 1)
                if cell_val:
                    cell_w = min([fm.width(x) for x in cell_val.split("\n")]) + 15
                else:
                    cell_w = 15
                
                cell_item.setText(cell_val)
                if not tt:
                    tt = cell_data["value"]
                cell_item.setToolTip(tt)

                if img:
                    img = img.scaled(img_w, img_h, Qt.KeepAspectRatio)
                    cell_item.setIcon(QIcon(img))
                    cell_item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                    icon_size_w = max(img_w, tbl.iconSize().width())
                    icon_size_h = max(img_h, tbl.iconSize().height())
                    tbl.setIconSize(QSize(icon_size_w, icon_size_h))
                    
                    cell_h = max(cell_h, img_h)
                    cell_w += img_w + 10
            else:
                cell_val = cell_data["value"]
                if cell_max_width:
                    words = cell_val.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        candidate_line = current_line + " " + word if current_line else word
                        width = fm.boundingRect(candidate_line).width()

                        if width <= cell_max_width:
                            current_line = candidate_line
                        else:
                            lines.append(current_line.strip())
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    cell_val = "\n".join(lines)

                for i in range(len(cell_data["data"]["text_slices"])):
                    tt += cell_data["data"]["text_slices"][i].txt_title + "\n"
                tt = tt.strip()

                cell_h = fm_height * (cell_val.count("\n") + 1)
                if cell_val:
                    cell_w = min([fm.width(x) for x in cell_val.split("\n")]) + 15
                else:
                    cell_w = 15

                cell_item = QTableWidgetItem()
                cell_item.setText(cell_val)
                if not tt:
                    tt = cell_val
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
        if ignore_headers:
            row_headers = []
            has_row_header = False
            col_headers = []
            has_col_header = False
        else:
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

                if smart_cell_width:
                    max_cell_width = int(table_width / 3)
                    item = set_cell_item(qtable, table_object[str(row)][str(col)], qtable_row, qtable_col, no_image_download=no_image_download, cell_max_width=max_cell_width)
                else:
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
        
        if table_width:
            width = table_width

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

    def get_PYQT5_table_ver2(self,
                             html_code: str,
                             parent_widget,
                             max_table_width: int = 1000,
                             font_size: int = 12,
                             text_link_feedback = None,
                             image_link_feedback = None,
                             fix_url_function = None):

        from PyQt5.QtWidgets import QTableWidget
        from PyQt5.QtCore import Qt

        html_code = self._quick_format_html(html_code)

        qtable = QTableWidget(parent_widget)
        qtable.setContentsMargins(0,0,0,0)
        qtable.verticalHeader().setVisible(False)
        qtable.horizontalHeader().setVisible(False)
        qtable.setSelectionMode(QTableWidget.SingleSelection)
        qtable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        qtable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Get data
        data = self._qtable_v2_get_data(html=html_code, parent_widget=qtable, font_size=font_size, max_table_width=max_table_width)
        if not data:
            qtable.resize(0, 0)
            return qtable

        # Calculate table size
        col_count = max([len(x) for x in data])
        row_count = len(data)
        qtable.setRowCount(row_count)
        qtable.setColumnCount(col_count)

        # Populate table with data
        font = qtable.font()
        font.setPointSize(font_size)
        row_idx = 0
        for row in data:
            col_idx = 0
            for col in row:
                frame = self._qtable_v2_get_cell_frame(col, font=font, text_link_feedback=text_link_feedback, image_link_feedback=image_link_feedback, fix_url_function=fix_url_function, max_table_width=max_table_width)
                qtable.setCellWidget(row_idx, col_idx, frame)
                if col["row_span"] > 1 or col["col_span"] > 1:
                    qtable.setSpan(row_idx, col_idx, col["row_span"], col["col_span"])
                
                qtable.setRowHeight(row_idx, max(qtable.rowHeight(row_idx), frame.height()))
                qtable.setColumnWidth(col_idx, max(qtable.columnWidth(col_idx), frame.width()))

                col_idx += col["col_span"]
            row_idx += col["row_span"]

        w = 0
        h = 0
        for row in range(qtable.rowCount()):
            h += qtable.rowHeight(row)
        for col in range(qtable.columnCount()):
            w += qtable.columnWidth(col)
        if max_table_width and max_table_width < w:
            w = max_table_width
            qtable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            h += qtable.horizontalScrollBar().height()

        qtable.resize(w + 2, h + 2)
        return qtable

    def _qtable_v2_get_cell_frame(self, data: dict, font, text_link_feedback, image_link_feedback, fix_url_function, max_table_width: int):
        from PyQt5.QtWidgets import QLabel, QFrame
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtCore import Qt

        frame = QFrame()
        frame.setFont(font)
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Plain)
        frame.setLineWidth(0)

        # If data is table, just set table to frame and return frame
        if data["table_obj"]:
            data["table_obj"].setParent(frame)
            data["table_obj"].move(0, 0)
            frame.resize(data["table_obj"].width(), data["table_obj"].height())
            return frame
        
        # Find data type
        if data["type"] == "th":
            word_wrap = False
        else:
            word_wrap = True
        
        # Group data by type
        frame_items = []
        widget_type = None
        for item in data["data"]:
            if isinstance(item, TextObject):
                cur_type = "text"
            elif isinstance(item, ImageObject):
                cur_type = "image"

            if cur_type != widget_type:
                frame_items.append([cur_type, [item], data["type"], data["bg_color"]])
                widget_type = cur_type
            else:
                frame_items[len(frame_items) - 1][1].append(item)
        
        # Create frame widgets
        frame_widgets = []
        for widget_type, widget_list, data_type, bg_color in frame_items:
            if widget_type == "text":
                lbl = QLabel(frame)
                if data_type == "th":
                    lbl.setAlignment(Qt.AlignCenter)
                if bg_color:
                    if bg_color in ["#000000", " #000000", "#0", "rgb(0,0,0)"]:
                        bg_color = "#b2dcc4"
                    frame.setStyleSheet(f"color: {bg_color};")
                lbl.setFont(font)
                lbl.setText(self._qtable_v2_format_label_text(widget_list, font.pointSize(), fix_url_function=fix_url_function))
                lbl.adjustSize()
                fixed_w = int(max_table_width * 0.8)
                fixed_w = min(fixed_w, lbl.width())
                lbl.setFixedWidth(fixed_w)
                lbl.setWordWrap(word_wrap)
                lbl.adjustSize()
                if text_link_feedback:
                    lbl.linkActivated.connect(lambda url: text_link_feedback(url))
                frame_widgets.append(lbl)
            elif widget_type == "image":
                for image in widget_list:
                    image: ImageObject
                    lbl = QLabel(frame)
                    lbl.setAlignment(Qt.AlignCenter)
                    # lbl.setScaledContents(True)

                    if image.img_height and image.img_width:
                        lbl.resize(image.img_width, image.img_height)
                    else:
                        lbl.resize(200, 200)
                    
                    if fix_url_function:
                        image_url = fix_url_function(image.img_src)
                    else:
                        image_url = image.img_src
                    img = None
                    has_image = False
                    try:
                        img = None
                        response = urllib.request.urlopen(image_url, timeout=2).read()
                        img = QPixmap()
                        has_image = img.loadFromData(response)
                        if not has_image:
                            response = requests.get(image_url, timeout=2)
                            has_image = img.loadFromData(response.content)
                    except:
                        img = None

                    if img:
                        lbl.setPixmap(img)
                        lbl.resize(img.width(), img.height())
                        if image.img_link:
                            image_link = fix_url_function(image.img_link)
                            lbl.mousePressEvent = lambda _, url=image_link: image_link_feedback(url)
                        if '<span class="flagicon' in image.tag_list:
                            lbl.setObjectName("flagicon")
                    frame_widgets.append(lbl)

        # Find max width and arange widgets
        max_w = 0
        for widget in frame_widgets:
            max_w = max(max_w, widget.width())
        
        y = 0
        x = 0
        for widget in frame_widgets:
            if widget.text():
                widget.resize(max_w, widget.height())
                widget.setFixedWidth(max_w)
                widget.adjustSize()
                widget.resize(max_w, widget.height() + 3)
            widget.move(x, y)
            if x > 0:
                max_w = max(max_w, widget.width() + x)
            
            if widget.objectName() == "flagicon":
                x = widget.width() + 10
            else:
                x = 0
                y += widget.height()
        
        frame.resize(max_w + 15, y)
        return frame

    def _qtable_v2_format_label_text(self, text_slices: list, font_size, fix_url_function) -> str:
        from utility_cls import TextToHTML
        from utility_cls import TextToHtmlRule

        text_to_html = TextToHTML()
        text_to_html.general_rule.font_size = font_size
        text = ""
        count = 1
        for text_slice in text_slices:
            text_slice: TextObject
            rule_id = "#" + "-" * (6 - len(str(count))) + str(count)
            rule = TextToHtmlRule(
                text=rule_id,
                replace_with=text_slice.txt_value
            )
            if text_slice.txt_link:
                if fix_url_function:
                    rule.link_href = fix_url_function(text_slice.txt_link)
                else:
                    rule.link_href = text_slice.txt_link

                if "wikipedia.org" in rule.link_href:
                    rule.fg_color = "#aaffff"
                else:
                    rule.fg_color = "#eab8ff"

            text += rule_id + " "
            text_to_html.add_rule(rule)
            count += 1
        
        text_to_html.set_text(text.strip())
        return text_to_html.get_html()

    def _qtable_v2_get_data(self, html: str, parent_widget, font_size: int = 12, max_table_width: int = 400) -> dict:
        data = []

        tables = self.get_tags(html_code=html, tag="table")
        if not tables:
            return data
        
        table_code = tables[0]
        rows_code = self.get_tags(html_code=table_code, tag="tr")

        for row_code in rows_code:
            row_data = []
            data.append(row_data)
            bg_color = self._qtable_v2_get_style_property(row_code, style_property="background:")

            row_span = self.get_tag_property_value(html_code=row_code, tag="tr", tag_property="rowspan")
            if not row_span:
                row_span = 1

            cols_code = self._qtable_v2_sort_tags(row_code, tags=["th", "td"])
            for col_code in cols_code:
                col_span = self.get_tag_property_value(html_code=col_code, tag_property="colspan")
                if not col_span:
                    col_span = 1

                cell_objects = self._qtable_v2_sort_text_and_images(html=col_code)
                if not bg_color:
                    bg_color = self._qtable_v2_get_style_property(col_code, style_property="background:")
                
                cell_type = ""
                if col_code.startswith("<th"):
                    cell_type = "th"
                elif col_code.startswith("td"):
                    cell_type = "td"

                raw_text = ""
                for item in cell_objects:
                    if isinstance(item, TextObject):
                        raw_text += item.txt_value + " "
                raw_text = raw_text.strip()

                tables = self.get_tags(html_code=col_code, tag="table")
                table_obj = None
                if tables:
                    table_obj = self.get_PYQT5_table_ver2(html_code=tables[0], parent_widget=parent_widget, font_size=font_size, max_table_width=max_table_width)

                cell_data = {
                    "col_span": int(col_span),
                    "row_span": int(row_span),
                    "raw_text": raw_text,
                    "data": cell_objects,
                    "bg_color": bg_color,
                    "type": cell_type,
                    "table_obj": table_obj
                }
                row_data.append(cell_data)
        
        return data
                
    def _qtable_v2_get_style_property(self, code_line: str, style_property: str) -> str:
        code_line = code_line.splitlines()[0]
        style = self.get_tag_property_value(html_code=code_line, tag_property="style")
        result = ""
        if style:
            start = style.find(style_property)
            if start != -1:
                end = style.find(";", start)
                if end != -1:
                    result = style[start+len(style_property):end]
        return result

    def _qtable_v2_sort_tags(self, html: str, tags: list) -> list:
        tag_codes = []

        for tag in tags:
            tag_codes += self.get_tags(html_code=html, tag=tag, return_line_numbers=True)
        
        sorted_tag_codes = sorted(tag_codes, key=lambda x: x[1])
        return [x[0] for x in sorted_tag_codes]

    def _qtable_v2_sort_text_and_images(self, html: str) -> list:
        tag_codes = []

        text_slices = self.get_all_text_slices(load_html_code=html)
        for text_slice in text_slices:
            tag_codes.append([text_slice, text_slice.in_tag_pos])

        images_code = self.get_all_images(load_html_code=html)
        for image in images_code:
            tag_codes.append([image, image.in_tag_pos])
        
        sorted_tag_codes = sorted(tag_codes, key=lambda x: x[1])
        return [x[0] for x in sorted_tag_codes]


