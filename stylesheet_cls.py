from collections import Counter


class StyleSheet:
    def __init__(self, widget_name: str = "") -> None:
        self._fg_color: str = None
        self._bg_color: str = None
        self._fg_hover_color: str = None
        self._bg_hover_color: str = None
        self._fg_disabled_color: str = None
        self._bg_disabled_color: str = None
        self._border_size: int = None
        self._border_color: str = None
        self._border_radius: int = None
        self._border_hover_size: int = None
        self._border_hover_color: str = None
        self._border_hover_radius: int = None
        self._border_disabled_size: int = None
        self._border_disabled_color: str = None
        self._border_disabled_radius: int = None
        self._font_name: str = None
        self._font_size: int = None
        self._font_bold: bool = None
        self._font_italic: bool = None
        self._font_underline: bool = None
        self._font_strikeout: bool = None
        self._stylesheet = None

        self._widget_name = self.detect_widget_name(widget_name)
        self._unmanaged_selectors = ""

    def load_data(self,
                fg_color: str = None,
                bg_color: str = None,
                fg_hover_color: str = None,
                bg_hover_color: str = None,
                fg_disabled_color: str = None,
                bg_disabled_color: str = None,
                border_size: int = None,
                border_color: str = None,
                border_radius: int = None,
                border_hover_size: int = None,
                border_hover_color: str = None,
                border_hover_radius: int = None,
                border_disabled_size: int = None,
                border_disabled_color: str = None,
                border_disabled_radius: int = None,
                font_name: str = None,
                font_size: int = None,
                font_bold: bool = None,
                font_italic: bool = None,
                font_underline: bool = None,
                font_strikeout: bool = None,
                unmanaged_selectors = ""
                ) -> None:
        self._fg_color = fg_color
        self._bg_color = bg_color
        self._fg_hover_color = fg_hover_color
        self._bg_hover_color = bg_hover_color
        self._fg_disabled_color = fg_disabled_color
        self._bg_disabled_color = bg_disabled_color
        self._border_size = border_size
        self._border_color = border_color
        self._border_radius = border_radius
        self._border_hover_size = border_hover_size
        self._border_hover_color = border_hover_color
        self._border_hover_radius = border_hover_radius
        self._border_disabled_size = border_disabled_size
        self._border_disabled_color = border_disabled_color
        self._border_disabled_radius = border_disabled_radius
        self._font_name = font_name
        self._font_size = font_size
        self._font_bold = font_bold
        self._font_italic = font_italic
        self._font_underline = font_underline
        self._font_strikeout = font_strikeout
        self._unmanaged_selectors = unmanaged_selectors

        self._update_stylesheet()
        
    def _update_stylesheet(self) -> str:
        style_default = ""
        style_hover = ""
        style_disabled = ""

        if self._fg_color:
            style_default += f" color: {self._fg_color};"
        
        if self._bg_color:
            style_default += f" background-color: {self._bg_color};"
        
        if self._border_size is not None:
            style_default += f" border: {self._border_size}px solid;"
        
        if self._border_color:
            style_default += f" border-color: {self._border_color};"
        
        if self._border_radius is not None:
            style_default += f" border-radius: {self._border_radius}px;"

        if self._font_name:
            style_default += f" font-family: {self._font_name};"
        
        if self._font_size:
            style_default += f" font-size: {self._font_size}px;"
        
        if self._font_bold is not None and self._font_bold:
            style_default += " font-weight: bold;"
        
        if self._font_italic is not None and self._font_italic:
            style_default += " font-style: italic;"

        if self._font_underline is not None and self._font_underline:
            style_default += " text-decoration: underline;"
        
        if self._font_strikeout is not None and self._font_strikeout:
            style_default += " text-decoration: line-through;"
        
        if style_default:
            style_default = self._widget_name + " {" + style_default.strip() + "}"
        
        if self._fg_hover_color:
            style_hover += f" color: {self._fg_hover_color};"
        
        if self._bg_hover_color:
            style_hover += f" background-color: {self._bg_hover_color};"
        
        if self._border_hover_size is not None:
            style_hover += f" border: {self._border_hover_size}px solid;"
        
        if self._border_hover_color:
            style_hover += f" border-color: {self._border_hover_color};"
        
        if self._border_hover_radius is not None:
            style_hover += f" border-radius: {self._border_hover_radius}px;"
        
        if style_hover:
            style_hover = self._widget_name + ":hover {" + style_hover.strip() + "}"
        
        
        if self._fg_disabled_color:
            style_disabled += f" color: {self._fg_disabled_color};"
        
        if self._bg_disabled_color:
            style_disabled += f" background-color: {self._bg_disabled_color};"

        if self._border_disabled_size is not None:
            style_disabled += f" border: {self._border_disabled_size}px solid;"
        
        if self._border_disabled_color:
            style_disabled += f" border-color: {self._border_disabled_color};"
        
        if self._border_disabled_radius is not None:
            style_disabled += f" border-radius: {self._border_disabled_radius}px;"
        
        if style_disabled:
            style_disabled = self._widget_name + ":disabled {" + style_disabled.strip() + "}"
        
        self._stylesheet = style_default
        if style_hover:
            self._stylesheet += "\n" + style_hover
        if style_disabled:
            self._stylesheet += "\n" + style_disabled

    def _update_properties(self) -> str:
        style_default = ""
        style_hover = ""
        style_disabled = ""
        
        self.detect_unmanaged_selectors()
        
        if self._widget_name not in self._stylesheet:
            style_default = self._stylesheet
        else:
            self._stylesheet = self._stylesheet.replace(f"{self._widget_name}::hover", f"{self._widget_name}:hover")
            self._stylesheet = self._stylesheet.replace(f"{self._widget_name}::disabled", f"{self._widget_name}:disabled")

            splited_style_line = self._stylesheet.split(f"{self._widget_name}:hover")
            splited_style_line2 = self._stylesheet.split(f"{self._widget_name}:disabled")
            style_default = splited_style_line[0]
            
            if len(splited_style_line) > 1:
                style_hover = self._stylesheet.split(f"{self._widget_name}:hover")[1]
            if len(splited_style_line2) > 1:
                style_disabled = self._stylesheet.split(f"{self._widget_name}:disabled")[1]
            
            if "{" in style_default:
                style_default = style_default.split("{")[1]
                style_default = style_default.split("}")[0].strip(" \n}{")
                style_default = f" {style_default} "
                style_default = style_default.replace(";", "; ")
            
            if "{" in style_hover:
                style_hover = style_hover.split("{")[1]
                style_hover = style_hover.split("}")[0].strip(" \n}{")
                style_hover = f" {style_hover} "
                style_hover = style_hover.replace(";", "; ")
            else:
                style_hover = ""
            
            if "{" in style_disabled:
                style_disabled = style_disabled.split("{")[1]
                style_disabled = style_disabled.split("}")[0].strip(" \n}{")
                style_disabled = f" {style_disabled} "
                style_disabled = style_disabled.replace(";", "; ")
            else:
                style_disabled = ""
        
        # Default style
        try:
            result = style_default.split("background-color:")[1].split(";")[0].strip()
        except:
            result = None
        self._bg_color = self.return_hex_color(result)

        style_default = style_default.replace("background-color:", "")

        try:
            result = style_default.split("border-color:")[1].split(";")[0].strip()
        except:
            result = None
        self._border_color = self.return_hex_color(result)

        style_default = style_default.replace("border-color:", "")

        try:
            result = style_default.split("color:")[1].split(";")[0].strip()
        except:
            result = None
        self._fg_color = self.return_hex_color(result)

        try:
            result = self._get_integer(self._remove_alpha_chars(style_default.split("border:")[1].split(";")[0]))
        except:
            result = None
        self._border_size = result

        try:
            result = self._get_integer(self._remove_alpha_chars(style_default.split("border-radius:")[1].split(";")[0]))
        except:
            result = None
        self._border_radius = result

        
        # Default Font
        try:
            result = style_default.split("font-family:")[1].split(";")[0].strip()
        except:
            result = None
        self._font_name = result

        try:
            result = self._get_integer(self._remove_alpha_chars(style_default.split("font-size:")[1].split(";")[0]))
        except:
            result = None
        self._font_size = result

        try:
            result = style_default.split("font-weight:")[1].split(";")[0].strip() == "bold"
        except:
            result = None
        self._font_bold = result

        try:
            result = style_default.split("font-style:")[1].split(";")[0].strip() == "italic"
        except:
            result = None
        self._font_italic = result

        try:
            result = style_default.split("text-decoration:")[1].split(";")[0].strip() == "underline"
        except:
            result = None
        self._font_underline = result

        try:
            result = style_default.split("text-decoration:")[1].split(";")[0].strip() == "line-through"
        except:
            result = None
        self._font_strikeout = result

        
        # Hover style
        try:
            result = style_hover.split("background-color:")[1].split(";")[0].strip()
        except:
            result = None
        self._bg_hover_color = self.return_hex_color(result)

        style_hover = style_hover.replace("background-color:", "")

        try:
            result = style_hover.split("border-color:")[1].split(";")[0].strip()
        except:
            result = None
        self._border_hover_color = self.return_hex_color(result)

        style_hover = style_hover.replace("border-color:", "")

        try:
            result = style_hover.split("color:")[1].split(";")[0].strip()
        except:
            result = None
        self._fg_hover_color = self.return_hex_color(result)

        try:
            result = self._get_integer(self._remove_alpha_chars(style_hover.split("border:")[1].split(";")[0]))
        except:
            result = None
        self._border_hover_size = result

        try:
            result = self._get_integer(self._remove_alpha_chars(style_hover.split("border-radius:")[1].split(";")[0]))
        except:
            result = None
        self._border_hover_radius = result


        # Disabled style
        try:
            result = style_disabled.split("background-color:")[1].split(";")[0].strip()
        except:
            result = None
        self._bg_disabled_color = self.return_hex_color(result)

        style_disabled = style_disabled.replace("background-color:", "")

        try:
            result = style_disabled.split("border-color:")[1].split(";")[0].strip()
        except:
            result = None
        self._border_disabled_color = self.return_hex_color(result)

        style_disabled = style_disabled.replace("border-color:", "")

        try:
            result = style_disabled.split("color:")[1].split(";")[0].strip()
        except:
            result = None
        self._fg_disabled_color = self.return_hex_color(result)

        try:
            result = self._get_integer(self._remove_alpha_chars(style_disabled.split("border:")[1].split(";")[0]))
        except:
            result = None
        self._border_disabled_size = result

        try:
            result = self._get_integer(self._remove_alpha_chars(style_disabled.split("border-radius:")[1].split(";")[0]))
        except:
            result = None
        self._border_disabled_radius = result

    def merge_stylesheet(self, stylesheet: 'StyleSheet', merge_widget_name: bool = False, force_new_value: bool = False) -> None:
        if merge_widget_name and not self.widget_name:
            self.widget_name = stylesheet.widget_name

        if not self.unmanaged_selectors:
            self.unmanaged_selectors = stylesheet.unmanaged_selectors

        if self.fg_color is None or force_new_value:
            self.fg_color = stylesheet.fg_color

        if self.bg_color is None or force_new_value:
            self.bg_color = stylesheet.bg_color

        if self.border_size is None or force_new_value:
            self.border_size = stylesheet.border_size

        if self.border_color is None or force_new_value:
            self.border_color = stylesheet.border_color

        if self.border_radius is None or force_new_value:
            self.border_radius = stylesheet.border_radius

        if self.font_name is None or force_new_value:
            self.font_name = stylesheet.font_name
        
        if self.font_size is None or force_new_value:
            self.font_size = stylesheet.font_size

        if self.font_bold is None or force_new_value:
            self.font_bold = stylesheet.font_bold

        if self.font_italic is None or force_new_value:
            self.font_italic = stylesheet.font_italic

        if self.font_underline is None or force_new_value:
            self.font_underline = stylesheet.font_underline

        if self.font_strikeout is None or force_new_value:
            self.font_strikeout = stylesheet.font_strikeout

        if self.bg_hover_color is None or force_new_value:
            self.bg_hover_color = stylesheet.bg_hover_color
        
        if self.fg_hover_color is None or force_new_value:
            self.fg_hover_color = stylesheet.fg_hover_color

        if self.border_hover_size is None or force_new_value:
            self.border_hover_size = stylesheet.border_hover_size

        if self.border_hover_color is None or force_new_value:
            self.border_hover_color = stylesheet.border_hover_color
        
        if self.border_hover_radius is None or force_new_value:
            self.border_hover_radius = stylesheet.border_hover_radius
        
        if self.bg_disabled_color is None or force_new_value:
            self.bg_disabled_color = stylesheet.bg_disabled_color
        
        if self.fg_disabled_color is None or force_new_value:
            self.fg_disabled_color = stylesheet.fg_disabled_color
        
        if self.border_disabled_size is None or force_new_value:
            self.border_disabled_size = stylesheet.border_disabled_size
        
        if self.border_disabled_color is None or force_new_value:
            self.border_disabled_color = stylesheet.border_disabled_color
        
        if self.border_disabled_radius is None or force_new_value:
            self.border_disabled_radius = stylesheet.border_disabled_radius
    
    def get_stylesheet(self, widget_name: str = None) -> str:
        if widget_name is None:
            return self.stylesheet

        style = self.stylesheet
        return style.replace(self._widget_name, widget_name)

    def detect_widget_name(self, text: str = None) -> str:
        replace_list = [
            ["qmainwindow", "QMainWindow"],
            ["qwidget", "QWidget"],
            ["qdialog", "QDialog"],
            ["qpushbutton", "QPushButton"],
            ["qtoolbar", "QToolBar"],
            ["qtoolbarwidget", "QToolBarWidget"],
            ["qtoolbutton", "QToolButton"],
            ["qradiobutton", "QRadioButton"],
            ["qcheckbox", "QCheckBox"],
            ["qcommandlinkbutton", "QCommandLinkButton"],
            ["qdialogbuttonbox", "QDialogButtonBox"],
            ["qlistview", "QListView"],
            ["qtreeview", "QTreeView"],
            ["qtableview", "QTableView"],
            ["qcolumnview", "QColumnView"],
            ["qlistwidget", "QListWidget"],
            ["qtreewidget", "QTreeWidget"],
            ["qtablewidget", "QTableWidget"],
            ["qgroupbox", "QGroupBox"],
            ["qscrollarea", "QScrollArea"],
            ["qtoolbox", "QToolBox"],
            ["qtabwidget", "QTabWidget"],
            ["qstatusbar", "QStatusBar"],
            ["qstackwidget", "QStackWidget"],
            ["qframe", "QFrame"],
            ["qmdiarea", "QMdiArea"],
            ["qdockwidget", "QDockWidget"],
            ["qcombobox", "QComboBox"],
            ["qfontcombobox", "QFontComboBox"],
            ["qlineedit", "QLineEdit"],
            ["qtextedit", "QTextEdit"],
            ["qplaintextedit", "QPlainTextEdit"],
            ["qspinbox", "QSpinBox"],
            ["qdoubleSpinBox", "QDoubleSpinBox"],
            ["qtimeedit", "QTimeEdit"],
            ["qdateedit", "QDateEdit"],
            ["qdatetimeedit", "QDateTimeEdit"],
            ["qdial", "QDial"],
            ["qhorizontalscrollbar", "QScrollBar"],
            ["qverticalscrollbar", "QScrollBar"],
            ["qhorizontalslider", "QSlider"],
            ["qverticalslider", "QSlider"],
            ["qslider", "QSlider"],
            ["qkeysequenceedit", "QKeySequenceEdit"],
            ["qlabel", "QLabel"],
            ["qtextbrowser", "QTextBrowser"],
            ["qgraphicsview", "QGraphicsView"],
            ["qcalendarwidget", "QCalendarWidget"],
            ["qlcdnumber", "QLCDNumber"],
            ["qprogressbar", "QProgressBar"],
            ["qopenglwidget", "QOpenGLWidget"],
            ["qwebengineview", "QWebEngineView"],
            ["qmenubar", "QMenuBar"],
            ["qmenu", "QMenu"],
            ["qaction", "QAction"]
        ]

        for item in replace_list:
            if item[0] == text.lower():
                return item[1]

        if text is None:
            text = self._stylesheet

        result = ""

        if self._stylesheet and "{" in self._stylesheet:
            text = self.stylesheet.split("{")[0].strip(" \n}")
            if ":" in text:
                result = text.split(":")[0].strip(" \n}")
        
        text = text.lower().strip(" \n{}\t")

        for item in replace_list:
            if item[0] == text:
                result = item[1]
                break
        
        self._widget_name = result
        return result

    def detect_unmanaged_selectors(self) -> None:
        if not self._widget_name:
            self.detect_widget_name(self._stylesheet)
        if not self._widget_name:
            self._unmanaged_selectors = ""
            return
        
        managed_selectors = [
            "hover",
            "disabled"
        ]

        self._stylesheet = self._stylesheet.replace("::hover", ":hover")
        self._stylesheet = self._stylesheet.replace("::disabled", ":disabled")

        selectors = []
        text = self._stylesheet
        while True:
            pos = text.find(self._widget_name)
            if pos == -1:
                selectors.append(text.strip(" \t\n{}:#"))
                break

            end = text.find("}")
            if end == -1:
                selectors.append(text.strip(" \t\n{}:#"))
                break

            selector = text[pos:end+1]
            selectors.extend((selector, text[:pos].strip(" \t\n{}:#")))

            text = text[end+1:]
        
        self._unmanaged_selectors = ""
        
        unmanaged = ""
        managed = ""
        for selector in selectors:
            if not selector:
                continue

            if self._widget_name not in selector:
                managed += "\n" + selector
                continue

            pos = selector.find("{")
            if pos == -1:
                unmanaged += "\n" + selector
                continue

            widget_selector = selector[:pos].replace(self._widget_name, "").strip(" \t\n{}:#")

            if widget_selector in managed_selectors or not widget_selector:
                managed += "\n" + selector
            else:
                unmanaged += "\n" + selector
        
        unmanaged = unmanaged.strip(" \n")
        managed = managed.strip(" \n")

        self._unmanaged_selectors = unmanaged
        self._stylesheet = managed

    def normalize_stylesheet_values(self, stylesheet_list: list):
        if self not in stylesheet_list:
            stylesheet_list.append(self)

        if not self.widget_name:
            self.widget_name = self.get_most_common_value([x.widget_name for x in stylesheet_list])
        
        self.unmanaged_selectors = self.get_most_common_value([x.unmanaged_selectors for x in stylesheet_list])

        self.fg_color = self.get_most_common_value([x.fg_color for x in stylesheet_list])
        self.bg_color = self.get_most_common_value([x.bg_color for x in stylesheet_list])
        self.border_size = self.get_most_common_value([x.border_size for x in stylesheet_list])
        self.border_color = self.get_most_common_value([x.border_color for x in stylesheet_list])
        self.border_radius = self.get_most_common_value([x.border_radius for x in stylesheet_list])
        self.font_name = self.get_most_common_value([x.font_name for x in stylesheet_list])
        self.font_size = self.get_most_common_value([x.font_size for x in stylesheet_list])
        self.font_bold = self.get_most_common_value([x.font_bold for x in stylesheet_list])
        self.font_italic = self.get_most_common_value([x.font_italic for x in stylesheet_list])
        self.font_underline = self.get_most_common_value([x.font_underline for x in stylesheet_list])
        self.font_strikeout = self.get_most_common_value([x.font_strikeout for x in stylesheet_list])

        self.fg_hover_color = self.get_most_common_value([x.fg_hover_color for x in stylesheet_list])
        self.bg_hover_color = self.get_most_common_value([x.bg_hover_color for x in stylesheet_list])
        self.border_hover_size = self.get_most_common_value([x.border_hover_size for x in stylesheet_list])
        self.border_hover_color = self.get_most_common_value([x.border_hover_color for x in stylesheet_list])
        self.border_hover_radius = self.get_most_common_value([x.border_hover_radius for x in stylesheet_list])

        self.fg_disabled_color = self.get_most_common_value([x.fg_disabled_color for x in stylesheet_list])
        self.bg_disabled_color = self.get_most_common_value([x.bg_disabled_color for x in stylesheet_list])
        self.border_disabled_size = self.get_most_common_value([x.border_disabled_size for x in stylesheet_list])
        self.border_disabled_color = self.get_most_common_value([x.border_disabled_color for x in stylesheet_list])
        self.border_disabled_radius = self.get_most_common_value([x.border_disabled_radius for x in stylesheet_list])

    def get_most_common_value(self, value_list: list) -> str:
        if not value_list:
            return None

        most_common_value = Counter(value_list).most_common(None)
        result = most_common_value[0][0]

        if most_common_value := [x[0] for x in most_common_value if x[0]]:
            result = most_common_value[0]
        
        return result

    def _remove_alpha_chars(self, text: str) -> str:
        return "".join(char for char in text if not char.isalpha())

    def _get_integer(self, text: str) -> int:
        result = None
        try:
            result = int(text)
        except:
            result = None
        return result

    def return_hex_color(self, color_string: str) -> str:
        if color_string is None:
            return None

        return self._is_valid_color(color_value_string=color_string) or ""

    def _is_valid_color(self, color_value_string: str) -> str:
        """Checks if color string is valid.
        Args:
            color_value_string (str): Color in HEX or RGB format (#000000 or rgb(0,0,0))
        Returns: valid color in hex form
            str: HEX color name or empty string if color is not valid
        """
        color = ""
        is_valid = False
        c_str = color_value_string.strip()
        original_c_str = c_str

        # Case when a hex value is passed
        if "#" in c_str:
            is_valid = True
            color = original_c_str

        # Case when a color name is transparent
        if c_str == "transparent":
            is_valid = True
            color = original_c_str

        # Case when an rgb value is passed
        # Find all color strings in the format rgb(0,0,0) or rgba(0,0,0,0)
        color_string_map = []
        pos = 0
        while True:
            pos = c_str.find("rgb", pos)
            if pos == -1:
                break
            start_pos = pos
            end_pos = c_str.find(")", pos)
            if end_pos == -1:
                break
            color_string_map.append([c_str[start_pos:end_pos + 1], start_pos, end_pos])
            pos = end_pos + 1

        # Replace rgb with hex and rgba with hex
        if color_string_map:
            for idx, item in enumerate(color_string_map):
                c_str = item[0]

                color = ""
                is_valid = False
                if "(" in c_str and ")" in c_str:
                    start_pos = c_str.find("(")
                    end_pos = c_str.find(")")
                    # There must be at least two characters between the brackets (,,) = (0,0,0)
                    if (end_pos - start_pos) < 3:
                        is_valid = False
                    else:
                        # c_str = content between brackets
                        c_str = c_str[start_pos + 1:end_pos]
                        # Separate each number between the brackets separated by a comma, if there is no number, put 0
                        values = [x.strip() if x.strip() != "" else "0" for x in c_str.split(",")]
                        # There must be exactly 3 values ​​between the brackets
                        # Check if all values ​​are numbers
                        if len(values) in {3, 4} and all(x.isdigit() for x in values):
                            red = int(values[0])
                            green = int(values[1])
                            blue = int(values[2])
                            alpha_hex = ""
                            if len(values) == 4:
                                alpha = int(values[3])
                                alpha_hex = hex(alpha)[2:].zfill(2) if alpha in range(256) else None

                            # Check that all values ​​are in the range 0-255
                            if red in range(256) and green in range(256) and blue in range(256):
                                # Convert each value to a HEX number and pad the left side with zeros to make the number of characters exactly 2
                                red_hex = hex(red)[2:].zfill(2)
                                green_hex = hex(green)[2:].zfill(2)
                                blue_hex = hex(blue)[2:].zfill(2)
                                # Finally, concatenate all HEX values ​​and add # to the beginning
                                if alpha_hex is not None:
                                    color = f"#{red_hex}{green_hex}{blue_hex}{alpha_hex}"
                                    is_valid = True
                if is_valid:
                    color_string_map[idx][0] = color

            # Replace color strings in original_c_str
            color_string_map = sorted(color_string_map, key=lambda x: x[1], reverse=True)
            for item in color_string_map:
                original_c_str = original_c_str[:item[1]] + item[0] + original_c_str[item[2] + 1:]

            is_valid = True
            color = original_c_str

        return color_value_string.strip() if is_valid else ""

    @property
    def unmanaged_selectors(self) -> str:
        return self._unmanaged_selectors

    @unmanaged_selectors.setter
    def unmanaged_selectors(self, value: str) -> None:
        self._unmanaged_selectors = value
        self._update_stylesheet()

    @property
    def stylesheet(self) -> str:
        text = ""
        return (
            self._stylesheet + "\n" + self._unmanaged_selectors
            if self._unmanaged_selectors
            else self._stylesheet
        )
    
    @stylesheet.setter
    def stylesheet(self, value: str) -> None:
        self._stylesheet = value
        self._update_properties()

    @property
    def widget_name(self) -> str:
        return self._widget_name
    
    @widget_name.setter
    def widget_name(self, value: str) -> None:
        self._widget_name = self.detect_widget_name(value)
        self._update_stylesheet()
    
    @property
    def fg_color(self) -> str:
        return self._fg_color
    
    @fg_color.setter
    def fg_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._fg_color = value
        self._update_stylesheet()
    
    @property
    def bg_color(self) -> str:
        return self._bg_color
    
    @bg_color.setter
    def bg_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._bg_color = value
        self._update_stylesheet()
    
    @property
    def fg_hover_color(self) -> str:
        return self._fg_hover_color
    
    @fg_hover_color.setter
    def fg_hover_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._fg_hover_color = value
        self._update_stylesheet()

    @property
    def bg_hover_color(self) -> str:
        return self._bg_hover_color
    
    @bg_hover_color.setter
    def bg_hover_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._bg_hover_color = value
        self._update_stylesheet()

    @property
    def fg_disabled_color(self) -> str:
        return self._fg_disabled_color
    
    @fg_disabled_color.setter
    def fg_disabled_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._fg_disabled_color = value
        self._update_stylesheet()
    
    @property
    def bg_disabled_color(self) -> str:
        return self._bg_disabled_color

    @bg_disabled_color.setter
    def bg_disabled_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._bg_disabled_color = value
        self._update_stylesheet()

    @property
    def border_size(self) -> int:
        return self._border_size
    
    @border_size.setter
    def border_size(self, value: int) -> None:
        self._border_size = value
        self._update_stylesheet()
    
    @property
    def border_color(self) -> str:
        return self._border_color

    @border_color.setter
    def border_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._border_color = value
        self._update_stylesheet()
    
    @property
    def border_radius(self) -> int:
        return self._border_radius
    
    @border_radius.setter
    def border_radius(self, value: int) -> None:
        self._border_radius = value
        self._update_stylesheet()
    
    @property
    def border_hover_size(self) -> int:
        return self._border_hover_size

    @border_hover_size.setter
    def border_hover_size(self, value: int) -> None:
        self._border_hover_size = value
        self._update_stylesheet()
    
    @property
    def border_hover_color(self) -> str:
        return self._border_hover_color
    
    @border_hover_color.setter
    def border_hover_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._border_hover_color = value
        self._update_stylesheet()
    
    @property
    def border_hover_radius(self) -> int:
        return self._border_hover_radius

    @border_hover_radius.setter
    def border_hover_radius(self, value: int) -> None:
        self._border_hover_radius = value
        self._update_stylesheet()

    @property
    def border_disabled_size(self) -> int:
        return self._border_disabled_size
    
    @border_disabled_size.setter
    def border_disabled_size(self, value: int) -> None:
        self._border_disabled_size = value
        self._update_stylesheet()

    @property
    def border_disabled_color(self) -> str:
        return self._border_disabled_color
    
    @border_disabled_color.setter
    def border_disabled_color(self, value: str) -> None:
        value = self.return_hex_color(value)
        self._border_disabled_color = value
        self._update_stylesheet()

    @property
    def border_disabled_radius(self) -> int:
        return self._border_disabled_radius

    @border_disabled_radius.setter
    def border_disabled_radius(self, value: int) -> None:
        self._border_disabled_radius = value
        self._update_stylesheet()

    @property
    def font_name(self) -> str:
        return self._font_name
    
    @font_name.setter
    def font_name(self, value: str) -> None:
        self._font_name = value
        self._update_stylesheet()
    
    @property
    def font_size(self) -> int:
        return self._font_size
    
    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font_size = value
        self._update_stylesheet()
    
    @property
    def font_bold(self) -> bool:
        return self._font_bold
    
    @font_bold.setter
    def font_bold(self, value: bool) -> None:
        self._font_bold = value
        self._update_stylesheet()
    
    @property
    def font_italic(self) -> bool:
        return self._font_italic
    
    @font_italic.setter
    def font_italic(self, value: bool) -> None:
        self._font_italic = value
        self._update_stylesheet()

    @property
    def font_underline(self) -> bool:
        return self._font_underline
    
    @font_underline.setter
    def font_underline(self, value: bool) -> None:
        self._font_underline = value
        self._update_stylesheet()
    
    @property
    def font_strikeout(self) -> bool:
        return self._font_strikeout
    
    @font_strikeout.setter
    def font_strikeout(self, value: bool) -> None:
        self._font_strikeout = value
        self._update_stylesheet()
