import urllib.request
from urllib.parse import quote as Quote
import requests

from PyQt5.QtGui import QPixmap

import os
import time

import settings_cls


class EnginesData():
    YAHOO = 1
    YAHOO_IMAGES_PATTERN = "https://images.search.yahoo.com/search/images;_ylt=AwrErrFSCQZlQGEexWJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?p=@@@&fr2=piv-web&fr=yfp-t"
    BING = 2
    BING_IMAGES_PATTERN = "https://search.aol.com/aol/image;_ylt=AwrE_E89gAdl0jkxMLRpCWVH;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?q=@@@&s_it=searchtabs&v_t=na"


class Engine():
    def __init__(self, engine_type: EnginesData):
        self.engine_type = engine_type
    
    def get_images_list(self, criteria: str) -> list:
        if self.engine_type == EnginesData.YAHOO:
            return self._get_images_list_yahoo(criteria=criteria)
        elif self.engine_type == EnginesData.BING:
            return self._get_images_list_bing(criteria=criteria)

    def _get_images_list_bing(self, criteria: str) -> list:
        criteria = self._prepare_search_term_for_yahoo(criteria)
        
        url = EnginesData.BING_IMAGES_PATTERN.replace("@@@", criteria)

        try:
            result_page = urllib.request.urlopen(url)
            html = result_page.read().decode("utf-8")
        except Exception as e:
            print (f"Error. {e}")
            return None

        html = html.replace('"', "'")

        images = []
        pos = 0
        while True:
            pos = html.find("<img data-src='", pos)
            if pos == -1:
                break
            pos = html.find("'", pos)
            end = html.find("'", pos + 1)
            if end == -1:
                break

            link = html[pos+1:end]
            link = self._remove_image_size(link)
            images.append([link, "", ""])

        return images

    def _get_link_list_for_bing(self, txt: str) -> list:
        link_mark = "http"
        bing_image = "https://tse1.mm.bing.net"

        txt = txt.replace("&quot;", "'")

        link_validation_strings = self._web_image_extensions()
        link_validation_strings.append(bing_image)

        pos = 0
        link_list = []
        while True:
            pos = txt.find(link_mark, pos)
            if pos == -1:
                break
            end = txt.find("'", pos)
            if end == -1:
                break

            link = txt[pos:end]
            if any(s in link for s in link_validation_strings):
                link_list.append(link)
            pos = end

        for idx, i in enumerate(link_list):
            if bing_image in i and idx != 0:
                link_list.insert(0, link_list.pop(idx))
                break
        
        return link_list
    
    def _get_label_for_bing(self, txt: str) -> str:
        start_string = "aria-label="

        txt = txt.replace("&quot;", "'")
        start = txt.find(start_string)
        if start == -1:
            return ""
        start = txt.find("'", start)
        if start == -1:
            return ""
        end = txt.find("'", start + 1)
        if end == -1:
            return ""
        
        return txt[start + 1:end]

    def _get_images_list_yahoo(self, criteria: str) -> list:
        keywords = []
        if criteria.find(":::") != -1:
            keywords = [x for x in self._prepare_search_term_for_yahoo(criteria[criteria.find(":::"):]).split("+")]

        criteria = self._prepare_search_term_for_yahoo(criteria)
        
        url = EnginesData.YAHOO_IMAGES_PATTERN.replace("@@@", criteria)

        try:
            result_page = urllib.request.urlopen(url)
            html = result_page.read().decode("utf-8")
        except Exception as e:
            print (f"Error. {e}")
            return None

        html = html.replace('"', "'")

        pos = 0
        images = []
        while True:
            pos = html.find("<img src='https:", pos)
            pos = html.find("'", pos)
            if pos == -1:
                break
            end = html.find("'", pos + 1)
            if end == -1:
                break

            image = html[pos + 1:end]
            image = self._remove_image_size(image)

            label = ""
            label_start = html[:pos].rfind("label")
            if label_start != -1:
                label_start = html.find("'", label_start)
                if label_start != -1 and label_start != pos:
                    label = html[label_start + 1:html.find("'", label_start + 1)]

            file_name = ""

            images.append([image, label, file_name])

        idx = 0
        for i in range(len(images)):
            image = images[idx]
            contain_all = True
            for keyword in keywords:
                if keyword.lower() not in image[1].lower() and keyword.lower() not in image[0].lower():
                    contain_all = False
                    break
            if not contain_all:
                images.append(images.pop(idx))
            else:
                idx += 1

        return images

    def _remove_image_size(self, image: str) -> str:
        parts = image.split("&")
        result = ""
        for part in parts:
            if part.lower().startswith("w=") or part.lower().startswith("h="):
                continue
            result += f"&{part}"
        result = result.lstrip("&")
        return result

    def _prepare_search_term_for_yahoo(self, term: str) -> str:
        if term is None:
            return ""
        
        if term.find(":::") != -1:
            if term[:term.find(":::")].startswith(":"):
                term = term[term.find(":::"):] + term[:term.find(":::")]
        
        repl = "!@#$%^&*()_+=-{}[];:'\'\\<>/?.,\t\n"

        for i in repl:
            term = term.replace(i, " ")

        repl = [
            ["ć", "c"],
            ["č", "c"],
            ["Ć", "C"],
            ["Č", "C"],
            ["ž", "z"],
            ["Ž", "Z"],
            ["š", "s"],
            ["Š", "S"],
            ["đ", "dj"],
            ["Đ", "DJ"]
        ]
        for i in repl:
            term = term.replace(i[0], i[1])

        while term.find("  ") != -1:
            term = term.replace("  ", " ")
        
        term = "+".join(term.split(" "))
        return term

    def _web_image_extensions(self) -> list:
        extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif"
        ]
        return extensions


class Images():
    def __init__(self, settings: settings_cls.Settings, criteria: str = None) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Other variables
        self.last_image_shown = []
        self.cashe_limit = self.getv("dict_online_search_cash")
        self.data = self._load_cashe()
        
        if criteria:
            self.load_image_data(criteria=criteria)

    def clear_cashe(self):
        remove_items = [x for x in self.data]
        for item in remove_items:
            if item == "@@@active" or item == self.data["@@@active"]:
                continue
            self.data.pop(item)

    def _load_cashe(self) -> dict:
        cash_name = "online_images_cash"
        if cash_name not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add(cash_name, {"@@@active": None}, save_to_file=True)
        return self.get_appv(cash_name)

    def _valid_criteria(self, criteria: str) -> str:
        if criteria is None:
            criteria = self.data["@@@active"]
        if criteria in self.data:
            return criteria
        return None

    def get_image_ids(self, criteria: str = None) -> list:
        criteria = self._valid_criteria(criteria)
        if criteria is None:
            return None
        result = [x for x in self.data[criteria]]
        return result
    
    def get_image_source(self, image_id: str, criteria: str = None) -> str:
        criteria = self._valid_criteria(criteria)
        if criteria is None:
            return None
        if image_id is None:
            return None

        if isinstance(image_id, int):
            image_id = str(image_id)
        
        if not isinstance(image_id, str):
            return None

        if image_id in self.data[criteria]:
            return self.data[criteria][image_id]["src"]
        return None

    def get_image_label(self, image_id: str, criteria: str = None) -> str:
        criteria = self._valid_criteria(criteria)
        if criteria is None:
            return None
        if image_id is None:
            return None

        if isinstance(image_id, int):
            image_id = str(image_id)
        
        if not isinstance(image_id, str):
            return None

        if image_id in self.data[criteria]:
            return self.data[criteria][image_id]["label"]
        return None

    def get_image_filename(self, image_id: str, criteria: str = None, create_file_if_not_exist: bool = True, update_last_image_shown_indicator: bool = True) -> str:
        criteria = self._valid_criteria(criteria)
        if criteria is None:
            return None
        if image_id is None:
            return None

        if isinstance(image_id, int):
            image_id = str(image_id)
        
        if not isinstance(image_id, str):
            return None

        if image_id not in self.data[criteria]:
            return None
        
        filename = self.data[criteria][image_id]["file"]

        if filename is None:
            return None
        
        if filename and os.path.isfile(filename):
            self.last_image_shown = [criteria, int(image_id)]
            return filename
        
        if not create_file_if_not_exist:
            return None
        
        filename = self._create_file(self.get_image_source(image_id), criteria, self.get_image_label(image_id), image_id)
        
        if filename is None:
            self.data[criteria][image_id]["file"] = filename
            return None
        
        if os.path.isfile(filename):
            self.data[criteria][image_id]["file"] = filename
            self.last_image_shown = [criteria, int(image_id)]
            return filename
        
        return None

    def get_next_image_id_to_show(self) -> str:
        if not self.last_image_shown:
            if self.data["@@@active"]:
                self.last_image_shown = [self.data["@@@active"], 0]
            if not self.last_image_shown:
                return None
        
        if self.last_image_shown[0] not in self.data:
            if self.data["@@@active"]:
                self.last_image_shown = [self.data["@@@active"], 0]
            else:
                return None
        
        count = self.last_image_shown[1]
        
        if str(count) not in self.data[self.last_image_shown[0]]:
            count = -1
        else:
            count = int(self.last_image_shown[1])
        
        image_ids = [int(x) for x in self.data[self.last_image_shown[0]]]

        if not image_ids:
            return None
        
        if count >= max(image_ids):
            count = -1

        if count == -1:
            count = image_ids[0]
        else:
            for idx, i in enumerate(image_ids):
                if i == count:
                    if idx+1 < len(image_ids):
                        count = image_ids[idx+1]
                        break
                    else:
                        count = image_ids[0]
                        break
            else:
                count = image_ids[0]
        
        self.last_image_shown[1] = count

        return str(self.last_image_shown[1])

    def _create_file(self, source: str, criteria: str, label: str, id: str) -> str:
        path = self.getv("temp_folder_path")

        file = str(time.time_ns())
        criteria = self._prepare_search_term(criteria).replace("+", "_")
        if len(criteria) > 20:
            criteria = criteria[:20]
        label = self._prepare_search_term(label).replace("+", "_")
        if len(label) > 30:
            label = label[:20]
        
        file += criteria
        file += id
        file += label
        file = path + file

        file = os.path.abspath(file)

        img = QPixmap()
        try:
            web_image = urllib.request.urlopen(source, timeout=3).read()
            result = img.loadFromData(web_image)
        except Exception as e:
            result = None

        if not result:
            return None

        if img.hasAlpha() or img.hasAlphaChannel():
            file += ".png"
            img.save(file, "png")
        else:
            file += ".jpg"
            img.save(file, "jpg")

        if os.path.isfile(file):
            return file
        else:
            return None

    def load_image_data(self, criteria: str, engine_type: EnginesData = None) -> bool:
        criteria = criteria.strip()
        if not criteria or criteria == "@@@active":
            return False
        
        if criteria in self.data and self.data[criteria]:
            self.data["@@@active"] = criteria
            return True
        
        current_item = criteria
        self.data[current_item] = {}

        if engine_type is None:
            engine_type = EnginesData.YAHOO

        engine = Engine(engine_type=engine_type)
        images = engine.get_images_list(criteria=criteria)

        if images is None:
            return False

        for idx, item in enumerate(images):
            self.data[current_item][str(idx)] = {}
            self.data[current_item][str(idx)]["src"] = item[0]
            self.data[current_item][str(idx)]["label"] = item[1]
            self.data[current_item][str(idx)]["file"] = item[2]

        self.data["@@@active"] = current_item

        self._check_cashe_limit()

        return True

    def _check_cashe_limit(self):
        if self.cashe_limit < 1:
            self.cashe_limit = 1
        if len(self.data) > self.cashe_limit:
            remove_items = self.cashe_limit - len(self.data)
            remove_list = []
            count = 1
            for i in self.data:
                if i != "@@@active":
                    remove_list.append(i)
                if count >= remove_items:
                    break
                count += 1
            for i in remove_list:
                for j in self.data[i]:
                    if os.path.isfile(self.data[i][j]["file"]):
                        os.remove(self.data[i][j]["file"])
                self.data.pop(i)

    def _remove_image_size(self, image: str) -> str:
        parts = image.split("&")
        result = ""
        for part in parts:
            if part.lower().startswith("w=") or part.lower().startswith("h="):
                continue
            result += f"&{part}"
        result = result.lstrip("&")
        return result

    def _prepare_search_term(self, term: str) -> str:
        if term is None:
            return ""
        
        repl = "!@#$%^&*()_+=-{}[];:'\'\\<>/?.,"

        for i in repl:
            term = term.replace(i, " ")

        repl = [
            ["ć", "c"],
            ["č", "c"],
            ["Ć", "C"],
            ["Č", "C"],
            ["ž", "z"],
            ["Ž", "Z"],
            ["š", "s"],
            ["Š", "S"],
            ["đ", "dj"],
            ["Đ", "DJ"]
        ]
        for i in repl:
            term = term.replace(i[0], i[1])

        while term.find("  ") != -1:
            term = term.replace("  ", " ")
        
        term = "+".join(term.split(" "))
        return term


