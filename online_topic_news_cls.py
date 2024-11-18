from PyQt5.QtWidgets import (QFrame, QPushButton, QScrollArea, QWidget, QLabel, QLineEdit, QProgressBar, QTableWidget,
                             QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout, QSpacerItem)
from PyQt5.QtGui import QPixmap, QMouseEvent, QFont, QFontMetrics
from PyQt5.QtCore import QSize, Qt, QCoreApplication, QEvent, QUrl
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView
import webbrowser

import settings_cls
import utility_cls
from rashomon_cls import Rashomon
import html_parser_cls
from online_abstract_topic import AbstractTopic
from media_player_cls import MediaPlayer
import UTILS


class NewsData:
    def __init__(self,
                 name: str = None,
                 project_file_path: str = None,
                 source_url: str = None,
                 categories: dict = None,
                 headlines: dict = None,
                 pages:dict = {}) -> None:
        self.name = name
        self.project_file_path = project_file_path
        self.source_url = source_url
        self.categories = categories
        self.headlines = headlines
        self.pages = pages
        
        self.active_headline_url: str = None
        self.active_page: str = None
        self.prev_pages: list = []
        self._current_navigation_page = None

    def set_active_page(self, page_url: str, navigation_click: bool = False):
        self.active_page = page_url
        if navigation_click:
            for idx, i in enumerate(self.prev_pages):
                if i == page_url:
                    self._current_navigation_page = idx
                    return
        # Delete previous page url from prev_page list
        if self.prev_pages and self._current_navigation_page is not None:
            while len(self.prev_pages) > self._current_navigation_page+1:
                self.prev_pages.pop(-1)

        clean_pages = []
        for i in self.prev_pages:
            if i not in clean_pages and i != self.active_page:
                clean_pages.append(i)
        self.prev_pages = clean_pages

        # Add new page
        self.prev_pages.append(page_url)
        self._current_navigation_page = len(self.prev_pages) - 1

    def failed_to_load(self, page_url: str):
        clean_pages = []
        for i in self.prev_pages:
            if i not in clean_pages and i != page_url:
                clean_pages.append(i)
        self.prev_pages = clean_pages

    def get_prev_page(self):
        if not self.prev_pages or not self._current_navigation_page:
            return None
        prev_page_idx = None
        for idx, i in enumerate(self.prev_pages):
            if i == self.active_page:
                if idx:
                    prev_page_idx = idx - 1
                    break
        if prev_page_idx is not None:
            return self.prev_pages[prev_page_idx]
        else:
            return None
                
    def get_next_page(self):
        if not self.prev_pages:
            return None
        next_page_idx = None
        for idx, i in enumerate(self.prev_pages):
            if i == self.active_page:
                if idx < len(self.prev_pages)-1:
                    next_page_idx = idx + 1
                    break
        if next_page_idx is not None:
            return self.prev_pages[next_page_idx]
        else:
            return None

    def add_page(self, page: dict):
        page_id = str(len(self.pages))
        while True:
            if page_id in self.pages:
                page_id = str(int(page_id) + 1)
            else:
                break
        self.pages[page_id] = page

    def get_page(self, page_url_or_id: str) -> dict:
        if page_url_or_id is None:
            return None
        
        page_id: str = None
        if page_url_or_id in self.pages:
            page_id = page_url_or_id
        else:
            for page in self.pages:
                if self.pages[page]["url"] == page_url_or_id:
                    page_id = page
                    break
        if page_id:
            return self.pages[page_id]
        else:
            return None

    def get_category_url(self, category_id: str) -> str:
        category_id = str(category_id)
        category_id_list = [x.strip() for x in category_id.split(",") if x.strip()]
        if len(category_id_list) == 1:
            if category_id_list[0] in self.categories:
                return self.categories[category_id_list[0]]["url"]
        elif len(category_id_list) == 2:
            cat_id = category_id_list[0]
            subcat_id = category_id_list[1]
            if cat_id in self.categories and subcat_id in self.categories[cat_id]["sub"]:
                return self.categories[cat_id]["sub"][subcat_id]["url"]

        return None
            

class AbstractNewsSource:
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, news_data_object: NewsData) -> None:
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.parent_widget = parent_widget
        self.project_loaded = False
        self.data: NewsData = news_data_object
        self.rashomon = Rashomon()
        self.html_parser = html_parser_cls.HtmlParser()
        self.base_site_url = ""
        self.base_default_image_path = ""
        self.search_available = False

    def load_project(self) -> bool:
        pass

    def load_categories(self) -> bool:
        pass

    def load_headlines(self, load_subcategories_for_id: str = None) -> bool:
        pass

    def load_page(self) -> bool:
        pass

    def _load_source(self) -> bool:
        pass

    def is_source_loaded(self) -> bool:
        if self.data.source_url:
            return True
        return False

    def _fix_url(self, url: str):
        if url.startswith("//"):
            url = "https:" + url
            return url
        elif url.startswith("/"):
            url = self.base_site_url + url
            return url
        return url


class NewsMondo(AbstractNewsSource):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, news_data_object: NewsData) -> None:
        super().__init__(parent_widget, settings, news_data_object)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.base_site_url = "http://mondo.rs"
        self.base_default_image_path = self.getv("online_news_mondo_page_def_img_path")

    def load_project(self, source: str = None, load_page_project: bool = False) -> bool:
        if load_page_project:
            project_file = self.getv("rashomon_folder_path") + "mondo_page.rpf"
        else:
            project_file = self.getv("rashomon_folder_path") + "mondo.rpf"
        
        if not source:
            source = "https://mondo.rs/"

        self.project_loaded = False
        
        self.rashomon.errors(clear_errors=True)
        result = self.rashomon.load_project(project_file, change_source=source)
        if self.rashomon.errors() or not result:
            return False

        self.rashomon.set_compatible_mode(True)
        if self.rashomon.errors():
            return False

        self.rashomon.recreate_segment_tree()
        if self.rashomon.errors():
            return False

        self.project_loaded = True
        return True

    def load_page(self) -> bool:
        if self.data.get_page(self.data.active_page):
            return True
        
        url = self.data.active_page

        if not url:
            return False
        
        self.rashomon.clear_errors()
        result = self.load_project(url, load_page_project=True)
        if not result or self.rashomon.errors():
            return False

        result = self._get_page_data()
        if not result:
            return False
        
        result["url"] = url
        self.data.add_page(result)
        return True

    def _get_page_data(self) -> bool:
        # Lead
        self.rashomon.clear_errors()
        page_lead = ""
        if self.rashomon.is_segment("lead_000"):
            page_lead = self.rashomon.get_segment_selection("lead_000", remove_tags=True, join_in_one_line=True)
        else:
            if self.rashomon.is_segment("lead1_000"):
                page_lead = self.rashomon.get_segment_selection("lead1_000", remove_tags=True, join_in_one_line=True)

        # Page Text
        result = self._get_page_text()
        if result is None:
            return False
        
        text_slices, page_text = result

        # Images
        result = self._get_page_images()

        if result:
            image_main, image_other = result
        else:
            image_main = ""
            image_other = []

        # Title
        self.rashomon.clear_errors()
        page_title = ""
        if self.rashomon.is_segment("title_000"):
            page_title = self.rashomon.get_segment_selection("title_000", remove_tags=True, join_in_one_line=True)
        else:
            page_title = self.rashomon.get_segment_selection("title1_000", remove_tags=True, join_in_one_line=True)
        
        # Date
        self.rashomon.clear_errors()
        page_date = ""
        if self.rashomon.is_segment("date_000"):
            page_date = self.rashomon.get_segment_selection("date_000", remove_tags=True, join_in_one_line=True)
        else:
            page_date = self.rashomon.get_segment_selection("date1_000", remove_tags=True, join_in_one_line=True)

        # Author name and page
        author_name = ""
        author_page = ""
        result = self._get_page_author()
        if result:
            author_name, author_page = result
        else:
            author_name = self.rashomon.get_segment_selection("author1_000", remove_tags=True, join_in_one_line=True)

        # Page tags
        page_tags = []
        result = self._get_page_tags()
        if result:
            page_tags = result
        
        # Related content
        related_content = {}
        result = self._get_page_related_content()
        if result:
            related_content = result

        # Videos
        videos = []
        result = self._get_page_videos()
        if result:
            videos = result

        # Audio
        audio = []
        audio_read_to_me = ""
        result = self._get_page_audio()
        if result:
            audio_read_to_me, audio = result

        # Tables
        tables = []
        result = self._get_page_tables()
        if result:
            tables = result

        page_dict = {
            "lead": page_lead,
            "text": page_text,
            "text_slices": text_slices,
            "main_image": image_main,
            "images": image_other,
            "date": page_date,
            "title": page_title,
            "author_name": author_name,
            "author_page": author_page,
            "tags": page_tags,
            "related": related_content,
            "videos": videos,
            "read_to_me": audio_read_to_me,
            "audios": audio,
            "tables": tables
        }
        return page_dict

    def _get_page_audio(self):
        pass

    def _get_page_videos(self) -> list:
        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("article_000")
        if self.rashomon.errors() or not html_code:
            html_code = self.rashomon.get_segment_selection("article1_001")
            if self.rashomon.errors() or not html_code:
                return None
        
        videos = []
        video_elements = self.html_parser.get_tags(html_code=html_code, tag="iframe", multiline=True)
        if video_elements:
            for element in video_elements:
                start = element.find('src="')
                end = element.find('"', start + 5)
                if start != -1 and end != -1:
                    url = element[start + 5:end]
                else:
                    continue

                start = element.find('class="')
                end = element.find('"', start + 7)
                video_class = ""
                if start != -1 and end != -1:
                    video_class = element[start + 7:end]
                videos.append([url, video_class])

        unable_to_show_html = """
        <html>
        <body>
                <h2><div>Unable to show some elements</div></h1>
                <h4>Please visit <a href="#1"><strong>source page</strong></a> for additional videos</h2>
        </body>
        </html>
        """
        unable_to_show_html = unable_to_show_html.replace("#1", self.data.active_page)

        video_elements = self.html_parser.get_tags(html_code=html_code, tag="blockquote", multiline=True)
        if video_elements:
            videos.append([unable_to_show_html, "page"])

        return videos

    def _get_page_related_content1(self) -> dict:
        self.rashomon.clear_errors()
        related_segments = self.rashomon.get_segment_children("related1")
        if not related_segments:
            return None
        
        related_content = {}
        count = 1
        for segment in related_segments:
            # Title
            title = ""
            title_code = self.html_parser.get_tags(html_code=segment, tag="div", tag_class_contains="card-title", multiline=True)
            if title_code:
                title = self.rashomon.remove_tags(title_code[0], join_in_one_line=True, delimiter="\n")
            # Time
            time = ""
            time_code = self.html_parser.get_tags(html_code=segment, tag="div", tag_class_contains="is-secondary-alt card", multiline=True)
            if time_code:
                time = self.rashomon.remove_tags(time_code[0], join_in_one_line=True, delimiter=" ")
            # Url
            url = ""
            url_code = self.html_parser.get_tags(html_code=segment, tag="a", tag_class_contains="card-link", multiline=False)
            if url_code:
                self.html_parser.load_html_code(url_code[0])
                urls = self.html_parser.get_all_links()
                if urls:
                    url = urls[0].a_href
            # Category
            category = ""
            category_code = self.html_parser.get_tags(html_code=segment, tag="div", tag_class_contains="is-secondary card", multiline=True)
            if category_code:
                category = self.rashomon.remove_tags(category_code[0], join_in_one_line=True, delimiter=" ")
            # Image
            image = ""
            image_code = self.html_parser.get_tags(html_code=segment, tag="picture", multiline=False)
            if image_code:
                image = self._get_image_url_from_picture_tag(image_code[0])
            
            if url:
                related_content[str(count)] = {}
                related_content[str(count)]["title"] = title
                related_content[str(count)]["time"] = time
                related_content[str(count)]["url"] = url
                related_content[str(count)]["category"] = category
                related_content[str(count)]["image"] = image
                count += 1

        return related_content

    def _get_page_related_content(self) -> dict:
        page_html = self.rashomon.get_source_text()
        page_related_code = self.html_parser.get_tags(html_code=page_html, tag="div", tag_class_contains="related-news__wrap", multiline=True)
        if not page_related_code:
            return None
        
        page_related_code = page_related_code[0]
        related_list = self.html_parser.get_tags(html_code=page_related_code, tag="a")
        if not related_list:
            return None
        
        related_content = {}
        count = 1
        for related in related_list:
            # Link
            rel_link = ""
            link_code = self.html_parser.get_all_links(related)
            if link_code:
                rel_link = link_code[0].a_href
            if not rel_link:
                continue

            # Title
            rel_title = ""
            title_code = self.html_parser.get_tags(html_code=related, tag="span", tag_class_contains="related-news__title", multiline=True)
            if title_code:
                rel_title = self.html_parser.get_raw_text(title_code[0]).strip('" ')
            
            # Time
            rel_time = ""

            # Category
            rel_cat = ""
            cat_code = self.html_parser.get_tags(html_code=related, tag="span", tag_class_contains="related-news__label")
            if cat_code:
                rel_cat = self.html_parser.get_raw_text(cat_code[0]).strip('" ')

            # Image
            rel_image = ""
            img_code = self.html_parser.get_tags(html_code=related, tag="div", tag_class_contains="card-image-container")
            if img_code:
                images = self.html_parser.get_all_images(img_code[0])
                if images:
                    rel_image = images[0].img_src

            if rel_link:
                related_content[str(count)] = {}
                related_content[str(count)]["title"] = rel_title
                related_content[str(count)]["time"] = rel_time
                related_content[str(count)]["url"] = rel_link
                related_content[str(count)]["category"] = rel_cat
                related_content[str(count)]["image"] = rel_image
                count += 1

        return related_content

    def DEPRECATED_get_page_related_content(self) -> dict:
        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("related_000")
        if self.rashomon.errors() or not html_code:
            return self._get_page_related_content1()
        
        related_content = {}

        li_segments = self.html_parser.get_tags(html_code=html_code, tag="li", multiline=True)
        if not li_segments:
            return None
        
        count = 1
        for li in li_segments:
            # Title
            title_code = self.html_parser.get_tags(html_code=li, tag="h2", tag_class_contains="title", multiline=True)
            if title_code:
                self.html_parser.load_html_code(title_code[0])
                title = self.html_parser.get_raw_text()
            else:
                continue
            # Time
            time_code = self.html_parser.get_tags(html_code=li, tag="p", tag_class_contains="time", multiline=True)
            time = ""
            if time_code:
                self.html_parser.load_html_code(time_code[0])
                time = self.html_parser.get_raw_text().strip(" |\n")
            # Url
            url_code = self.html_parser.get_tags(html_code=li, tag="a", tag_class_contains="title", multiline=True)
            if url_code:
                self.html_parser.load_html_code(url_code[0])
                url_list = self.html_parser.get_all_links()
                if url_list:
                    url = url_list[0].a_href
                else:
                    continue
            else:
                continue
            # Category
            category_code = self.html_parser.get_tags(html_code=li, tag="p", tag_class_contains="category-name", multiline=True)
            category = ""
            if category_code:
                self.html_parser.load_html_code(category_code[0])
                category = self.html_parser.get_raw_text()
            # Image
            image_code = self.html_parser.get_tags(html_code=li, tag="picture", multiline=True)
            if image_code:
                image = self._get_image_url_from_picture_tag(image_code[0])
            else:
                image = ""
            
            if url:
                related_content[str(count)] = {}
                related_content[str(count)]["title"] = title
                related_content[str(count)]["time"] = time
                related_content[str(count)]["url"] = url
                related_content[str(count)]["category"] = category
                related_content[str(count)]["image"] = image
                count += 1
        
        return related_content

    def _get_page_tags(self) -> list:
        tags_code = self.html_parser.get_tags(html_code=self.rashomon.get_source_text(), tag="div", tag_class_contains="article-tags")

        if not tags_code:
            return None
        
        tag_links = self.html_parser.get_all_links(tags_code[0])

        if not tag_links:
            return None

        page_tags = []
        for tag_link in tag_links:
            text = tag_link.a_text
            link = tag_link.a_href

            if link:
                page_tags.append([text, link])
        
        return page_tags

    def _get_page_author(self) -> str:
        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("article_000")
        if self.rashomon.errors() or not html_code:
            return None

        author_code_list = self.html_parser.get_tags(html_code=html_code, tag="a", tag_class_contains="author-name", multiline=True)
        if author_code_list:
            author_code = author_code_list[0]
            self.html_parser.load_html_code(author_code)
            result = self.html_parser.get_all_text_slices()
            if result:
                author_name = result[0].txt_value
                author_page = result[0].txt_link
                return author_name, author_page

    def _get_page_images1(self) -> tuple:
        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("article1_000")
        if self.rashomon.errors() or not html_code:
            return None
    
        picture_tags = self.html_parser.get_tags(html_code=html_code, tag="picture", multiline=True)
        image_main = ""
        image_other = []
        for pic_code in picture_tags:
            img_url = self._get_image_url_from_picture_tag(pic_code)
            if not img_url:
                continue

            if image_main:
                image_other.append(img_url)
            else:
                image_main = img_url

        return image_main, image_other
    
    def _get_page_images(self) -> tuple:
        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("article_000")
        if self.rashomon.errors() or not html_code:
            result = self._get_page_images1()
            if result:
                return result
            else:
                html_code = self.rashomon.get_segment_selection("live_000")
                if not html_code:
                    return None
        
        img_code = ""
        for line in html_code.splitlines():
            line = line.strip()
            if line.startswith(('BONUS VIDEO:', '<div class="story-related-news')):
                break
            img_code += line + "\n"

        picture_tags = self.html_parser.get_tags(html_code=img_code, tag="picture", multiline=True)
        image_main = ""
        image_other = []
        for pic_code in picture_tags:
            img_url = self._get_image_url_from_picture_tag(pic_code)
            if not img_url:
                continue

            if image_main:
                image_other.append(img_url)
            else:
                image_main = img_url

        return image_main, image_other

    def _get_image_url_from_picture_tag(self, picture_tag_code: str) -> str:
        start = picture_tag_code.find('src="')
        if start != -1:
            end = picture_tag_code.find('"', start + 5)
            if end != -1:
                return picture_tag_code[start+5:end]
        
        start = picture_tag_code.find('srcset="')
        if start == -1:
            return ""
        
        end = picture_tag_code.find('"', start + 8)
        if end == -1:
            return ""

        return picture_tag_code[start + 8:end]
    
    def _getpage_text1(self) -> tuple:
        if not self.rashomon.is_segment("article1_000"):
            return None

        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("article1_000")
        if self.rashomon.errors() or not html_code:
            return None

        self.html_parser.load_html_code(html_code)
        raw_text = self.html_parser.get_raw_text()

        text_paragraphs = self.html_parser.get_tags(html_code=html_code, tag="p", multiline=True)

        text_list = []
        for text_par in text_paragraphs:
            self.html_parser.load_html_code(text_par)
            text_list += self.html_parser.get_all_text_slices()
        
        return text_list, raw_text

    def _get_page_tables(self) -> list:
        segment_to_select = "article_000"
        if not self.rashomon.is_segment(segment_to_select):
            segment_to_select = "article1_000"
        if not self.rashomon.is_segment(segment_to_select):
            segment_to_select = "live_000"
        if not self.rashomon.is_segment(segment_to_select):
            return None
        
        self.html_parser.load_html_code(self.rashomon.get_segment_selection(segment_to_select))
        result = self.html_parser.get_all_tables()

        if result:
            return result
        else:
            return None

    def _get_page_text(self) -> tuple:
        segment_to_select = "article_000"
        if not self.rashomon.is_segment("article_000"):
            result = self.rashomon.is_segment("article1_000")
            if result:
                return self._getpage_text1()
            else:
                segment_to_select = "live_000"

        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection(segment_to_select)
        if self.rashomon.errors() or not html_code:
            return None
        
        # Find html code for text
        html_code = self.html_parser.remove_specific_tag(html_code, 'blockquote', multiline=True)
        html_code = self.html_parser.remove_specific_tag(html_code, 'section', multiline=True)
        html_code = self.html_parser.remove_specific_tag(html_code, 'figcaption', multiline=True)
        html_code = self.html_parser.remove_specific_tag(html_code, 'cite', multiline=True)
        html_code = self.html_parser.remove_specific_tag(html_code, 'script', multiline=True)
        html_code = self.html_parser.remove_specific_tag(html_code, 'style', multiline=True)
        text_code = ""
        if segment_to_select == "article_000":
            in_text = False
            for line in html_code.splitlines():
                line = line.strip()
                if line.startswith('<div class="first-letter'):
                    in_text = True
                    continue
                
                if line.strip().lower().startswith(('bonus  video', 'bonus video', '<div class="story-related-news')):
                    break

                if in_text:
                    text_code += line + "\n"
        else:
            text_code = html_code

        # Find all text and build text list
        text_list = []
        self.html_parser.load_html_code(text_code)
        text_slices = self.html_parser.get_all_text_slices()
        for slc in text_slices:
            if slc.txt_value:
                text_list.append(slc)
        
        return text_list, self.html_parser.get_raw_text()

    def load_headlines(self) -> bool:
        url = self.data.active_headline_url

        if not url:
            return False
        
        result = self.load_project(url)
        if not result:
            return False

        data = self.rashomon.get_source_text()

        # Check for main 3 headlines
        main3 = self.html_parser.get_tags(html_code=data, tag="div", tag_class_contains="main-3-news")
        main3_result = []
        if main3:
            main3_result = self._load_headline_new_main3(main3[0])

        other = self.html_parser.get_tags(html_code=data, tag="div", tag_class_contains="feed-list-item")
        other_result = []
        if other:
            other_result = self._load_headline_new_other(other)

        result = []
        if main3_result or other_result:
            result = True
        else:
            result = False

        return result

    def _load_headline_new_main3(self, html_code: str) -> bool:
        cards = self.html_parser.get_tags(html_code=html_code, tag="div", tag_class_contains="card-wrap type-news-card")
        if not cards:
            return False
        
        for card in cards:
            image = ""
            image_code = self.html_parser.get_tags(html_code=card, tag="div", tag_class_contains="card-image-container")
            if image_code:
                images = self.html_parser.get_all_images(image_code[0])
                if images:
                    image = images[0].img_src

            text = ""
            text_code = self.html_parser.get_tags(html_code=card, tag="div", tag_class_contains="card-title")
            if text_code:
                text = self.html_parser.get_raw_text(text_code[0]).strip('" ')
            
            news_cat = ""
            news_date = ""
            news_time = ""
            news_labels = self.html_parser.get_tags(html_code=card, tag="div", tag_class_contains="card-labels")
            if news_labels:
                news_categories = self.html_parser.get_tags(html_code=news_labels[0], tag="span")
                for category in news_categories:
                    label_text = self.html_parser.get_raw_text(category).strip()
                    if label_text.lower().startswith("pre"):
                        news_time = label_text
                        continue
                    if label_text and UTILS.TextUtility.is_integer_possible(label_text[0]):
                        news_date = label_text
                        continue
                    news_cat += label_text + ", "
                news_cat = news_cat.strip(", ")

            link = ""
            link_code = self.html_parser.get_tags(html_code=card, tag="a", tag_class_contains="card-link")
            if link_code:
                link = self._fix_url(self.html_parser.get_all_links(link_code[0])[0].a_href)
            
            self._add_headline(image, text, "", "", news_time, news_date, news_cat, link)
        
        return True

    def _load_headline_new_other(self, html_code_list: list) -> bool:
        if not html_code_list:
            return False

        has_data = False
        for card in html_code_list:
            image = ""
            image_code = self.html_parser.get_tags(html_code=card, tag="div", tag_class_contains="card-image-container")
            if image_code:
                images = self.html_parser.get_all_images(image_code[0])
                if images:
                    image = images[0].img_src

            text = ""
            text_code = self.html_parser.get_tags(html_code=card, tag="div", tag_class_contains="card-title")
            if text_code:
                text = self.html_parser.get_raw_text(text_code[0]).strip('" ')
            
            news_cat = ""
            news_date = ""
            news_time = ""
            news_labels = self.html_parser.get_tags(html_code=card, tag="div", tag_class_contains="card-labels")
            if news_labels:
                news_categories = self.html_parser.get_tags(html_code=news_labels[0], tag="span")
                for category in news_categories:
                    label_text = self.html_parser.get_raw_text(category).strip()
                    if label_text.lower().startswith("pre"):
                        news_time = label_text
                        continue
                    if label_text and UTILS.TextUtility.is_integer_possible(label_text[0]):
                        news_date = label_text
                        continue
                    news_cat += label_text + ", "
                news_cat = news_cat.strip(", ")

            link = ""
            link_code = self.html_parser.get_tags(html_code=card, tag="a", tag_class_contains="card-link")
            if link_code:
                link = self._fix_url(self.html_parser.get_all_links(link_code[0])[0].a_href)
            
            if self._add_headline(image, text, "", "", news_time, news_date, news_cat, link):
                has_data = True
        
        return has_data

    def _add_headline(self, image: str, text: str, desc: str, title: str, news_time: str, news_date: str, news_cat: str, news_link: str) -> bool:
        if not news_link:
            return False
        
        # Find next ID
        next_id = self._get_next_headline_id()
        
        # Add Headline
        self.data.headlines[next_id] = {}
        self.data.headlines[next_id]["image"] = image if image else ""
        self.data.headlines[next_id]["text"] = text if text else ""
        self.data.headlines[next_id]["desc"] = desc if desc else ""
        self.data.headlines[next_id]["title"] = title if title else ""
        self.data.headlines[next_id]["time"] = news_time if news_time else ""
        self.data.headlines[next_id]["date"] = news_date if news_date else ""
        self.data.headlines[next_id]["category"] = news_cat if news_cat else ""
        self.data.headlines[next_id]["link"] = news_link

        return True

    def DEPRECATED_load_headlines(self) -> bool:
        url = self.data.active_headline_url

        if not url:
            return False
        
        result = self.load_project(url)
        if not result:
            return False

        if self.rashomon.is_segment("main_head_000"):
            data = self.rashomon.get_segment_selection("main_head_000")
        else:
            data = ""
        if self.rashomon.errors():
            return False

        # if url.endswith(("mondo.rs", "mondo.rs/")):
        if data:
            result = self._load_headline_type1()
        else:
            result = self._load_headline_type2()
        
        return result

    def _load_headline_type2(self):
        result = True
        headlines = self.rashomon.get_segment_children("cat_article")
        for headline in headlines:
            html_code = self.rashomon.get_segment_selection(headline)
            is_ok = self._add_headline_type2(html_code)
            if not is_ok:
                result = False
        
        return result

    def _add_headline_type2(self, html_code: str) -> bool:
        title = ""
        # Find headline data
        image_code = self.html_parser.get_tags(html_code=html_code, tag="picture", multiline=True)
        image = ""
        if image_code:
            image_code = image_code[0]
            start = image_code.find('srcset="')
            if start != -1:
                end = image_code.find('"', start + 8)
                if end != -1:
                    image = image_code[start+8: end]
        if not image:
            self.html_parser.load_html_code(html_code)
            images = self.html_parser.get_all_images()
            if images:
                image = images[0].img_src

        text_code = self.html_parser.get_tags(html_code=html_code, tag="h2", multiline=True)
        if text_code:
            text_code = text_code[0]
        else:
            text_code = ""
        self.html_parser.load_html_code(text_code)
        text = self.html_parser.get_raw_text()
        for i in self.html_parser.get_all_text_slices():
            if i.txt_title:
                title += i.txt_title

        desc_code = self.html_parser.get_tags(html_code=html_code, tag="a", tag_class_contains="description", multiline=True)
        if desc_code:
            desc_code = desc_code[0]
        else:
            desc_code = ""
        self.html_parser.load_html_code(desc_code)
        desc = self.html_parser.get_raw_text()

        news_time_code = self.html_parser.get_tags(html_code=html_code, tag="span", tag_class_contains="time", multiline=True)
        if news_time_code:
            news_time_code = news_time_code[0]
        else:
            news_time_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="time", multiline=True)
            if news_time_code:
                news_time_code = news_time_code[0]
            else:
                news_time_code = ""
        self.html_parser.load_html_code(news_time_code)
        news_time = self.html_parser.get_raw_text().strip(" |")

        news_date_code = self.html_parser.get_tags(html_code=html_code, tag="span", tag_class_contains="date-text", multiline=True)
        if news_date_code:
            news_date_code = news_date_code[0]
        else:
            news_date_code = ""
        self.html_parser.load_html_code(news_date_code)
        news_date = self.html_parser.get_raw_text().strip(" |")

        news_cat_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="category-name", multiline=True)
        if news_cat_code:
            news_cat_code = news_cat_code[0]
        else:
            news_cat_code = ""
        self.html_parser.load_html_code(news_cat_code)
        news_cat = self.html_parser.get_raw_text()

        self.html_parser.load_html_code(html_code)
        news_links = self.html_parser.get_all_links()
        for i in news_links:
            if i.a_text:
                title += i.a_text
        if news_links:
            news_link = news_links[0].a_href
        else:
            return False
        
        title = title.strip()

        # Find next ID
        next_id = self._get_next_headline_id()
        
        # Add Headline
        self.data.headlines[next_id] = {}
        self.data.headlines[next_id]["image"] = image
        self.data.headlines[next_id]["text"] = text
        self.data.headlines[next_id]["desc"] = desc
        self.data.headlines[next_id]["title"] = title
        self.data.headlines[next_id]["time"] = news_time
        self.data.headlines[next_id]["date"] = news_date
        self.data.headlines[next_id]["category"] = news_cat
        self.data.headlines[next_id]["link"] = news_link
        return True

    def _load_headline_type1(self):
        top_headline = self.rashomon.get_segment_selection("main_head_000")
        result = self._add_headline_type1(top_headline)

        ignore_items = [
            "main_articles_000_000",
            "main_articles_000_001",
            "main_articles_000_002",
            "main_articles_000_003"
        ]

        if self.rashomon.is_segment("main_articles_000"):
            headlines = self.rashomon.get_segment_children("main_articles_000")
        else:
            return False

        for headline in headlines:
            if headline in ignore_items:
                continue
            html_code = self.rashomon.get_segment_selection(headline)
            is_ok = self._add_headline_type1(html_code)
            if not is_ok:
                result = False
        
        return result

    def _add_headline_type1(self, html_code: str) -> bool:
        title = ""
        # Find headline data
        self.html_parser.load_html_code(html_code)
        images = self.html_parser.get_all_images()
        for i in images:
            if i.img_title:
                title += i.img_title

        text_code = self.html_parser.get_tags(html_code=html_code, tag="h2", tag_class_contains="title", multiline=True)
        if text_code:
            text_code = text_code[0]
        else:
            text_code = ""
        self.html_parser.load_html_code(text_code)
        text = self.html_parser.get_raw_text()
        for i in self.html_parser.get_all_text_slices():
            if i.txt_title:
                title += i.txt_title

        news_time_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="time", multiline=True)
        if news_time_code:
            news_time_code = news_time_code[0]
        else:
            news_time_code = ""
        self.html_parser.load_html_code(news_time_code)
        news_time = self.html_parser.get_raw_text().strip(" |")

        news_cat_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="category-name", multiline=True)
        if news_cat_code:
            news_cat_code = news_cat_code[0]
        else:
            news_cat_code = ""
        self.html_parser.load_html_code(news_cat_code)
        news_cat = self.html_parser.get_raw_text()

        self.html_parser.load_html_code(html_code)
        news_links = self.html_parser.get_all_links()
        for i in news_links:
            if i.a_text:
                title += i.a_text
        if news_links:
            news_link = news_links[0].a_href
        else:
            return False
        
        title = title.strip()

        # Find next ID
        next_id = self._get_next_headline_id()
        
        # Add Headline
        self.data.headlines[next_id] = {}
        self.data.headlines[next_id]["image"] = images[0].img_src if images else ""
        self.data.headlines[next_id]["text"] = text
        self.data.headlines[next_id]["desc"] = ""
        self.data.headlines[next_id]["title"] = title
        self.data.headlines[next_id]["time"] = news_time
        self.data.headlines[next_id]["date"] = ""
        self.data.headlines[next_id]["category"] = news_cat
        self.data.headlines[next_id]["link"] = news_link
        return True

    def _get_next_headline_id(self) -> str:
        next_id = 1
        for i in self.data.headlines:
            if int(i) > next_id:
                next_id = int(i)
        
        next_id += 1
        return str(next_id)

    def load_categories(self) -> bool:
        if not self.project_loaded:
            if not self.load_project():
                return False
            
        self.rashomon.clear_errors()
        categories_html = self.rashomon.get_source_text()
        categories_html = self.html_parser.get_tags(self.rashomon.get_source_text(), tag="div", tag_class_contains="header-navigation__wrap")
        if not categories_html:
            return False
        categories_html = categories_html[0]
        
        self.html_parser.load_html_code(categories_html)

        lists = self.html_parser.get_all_lists()
        if not lists:
            return False
        
        remove_cat = [
            "galerija automobila",
            "lepa i srećna",
            "wanted",
            "sensa",
            "Ukrštene reči",
            "Sudoku"
        ]
        result = {}
        main_count = 1
        for main_cat in lists[0].sub_items:
            if not main_cat.get_link_url() or main_cat.text.lower().strip() in remove_cat:
                continue

            result[str(main_count)] = {}
            name = main_cat.text.strip()
            if name.lower().endswith("još"):
                name = name[:-3].strip() + "..."
            result[str(main_count)]["name"] = name
            result[str(main_count)]["title"] = main_cat.title.strip()
            result[str(main_count)]["url"] = self._fix_url(main_cat.get_link_url())
            
            result[str(main_count)]["sub"] = {}
            sub_count = 1
            for sub_cat in main_cat.sub_items:
                if not sub_cat.get_link_url() or sub_cat.text.lower().strip() in remove_cat:
                    continue
                name = sub_cat.text.strip()
                if name.lower().endswith("još"):
                    name = name[:-3].strip() + ":"
                result[str(main_count)]["sub"][str(sub_count)] = {}
                result[str(main_count)]["sub"][str(sub_count)]["name"] = name
                result[str(main_count)]["sub"][str(sub_count)]["title"] = sub_cat.title.strip()
                result[str(main_count)]["sub"][str(sub_count)]["url"] = self._fix_url(sub_cat.get_link_url())
                result[str(main_count)]["sub"][str(sub_count)]["sub"] = {}
                
                if sub_cat.sub_items:
                    for extra_sub_cat in sub_cat.sub_items:
                        if not extra_sub_cat.get_link_url() or extra_sub_cat.text.lower().strip() in remove_cat:
                            continue
                        sub_count += 1
                        name = extra_sub_cat.text.strip()
                        if name.lower().endswith("još"):
                            name = name[:-3].strip()
                        result[str(main_count)]["sub"][str(sub_count)] = {}
                        result[str(main_count)]["sub"][str(sub_count)]["name"] = name
                        result[str(main_count)]["sub"][str(sub_count)]["title"] = extra_sub_cat.title.strip()
                        result[str(main_count)]["sub"][str(sub_count)]["url"] = self._fix_url(extra_sub_cat.get_link_url())
                        result[str(main_count)]["sub"][str(sub_count)]["sub"] = {}

                sub_count += 1
            main_count += 1
        
        self.data.categories = result
        return True


class NewsSputnik(AbstractNewsSource):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, news_data_object: NewsData) -> None:
        super().__init__(parent_widget, settings, news_data_object)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.base_site_url = "https://lat.sputnikportal.rs"
        self.base_default_image_path = self.getv("online_news_sputnik_page_def_img_path")

    def load_project(self, source: str = None) -> bool:
        project_file = self.getv("rashomon_folder_path") + "sputnik.rpf"
        if not source:
            source = "https://lat.sputnikportal.rs/"

        if self.project_loaded:
            if self.rashomon.get_source() == source:
                return True
            
        self.project_loaded = False
        
        self.rashomon.errors(clear_errors=True)
        result = self.rashomon.load_project(project_file, change_source=source)
        if self.rashomon.errors() or not result:
            return False

        self.rashomon.set_compatible_mode(True)
        if self.rashomon.errors():
            return False

        self.rashomon.recreate_segment_tree()
        if self.rashomon.errors():
            return False

        self.project_loaded = True
        return True

    def load_categories(self) -> bool:
        if not self.project_loaded:
            if not self.load_project():
                return False
            
        self.rashomon.clear_errors()
        if not self.rashomon.is_segment("menu_000"):
            return False

        result = self._get_category_list(add_pocetna=True)
        self.data.categories = result
        return True

    def _get_category_list(self, add_pocetna: bool = False) -> dict:
        remove_cat = [
        ]
        
        result = {}
        cat_code_list = self.rashomon.get_segment_children("menu")
        if not cat_code_list:
            return result
        
        count = 1
        if add_pocetna:
            result[str(count)] = {}
            result[str(count)]["name"] = "Početna"
            result[str(count)]["title"] = ""
            result[str(count)]["url"] = "https://lat.sputnikportal.rs/"
            result[str(count)]["sub"] = {}
            count += 1
            
        for cat_segment in cat_code_list:
            cat_code = self.rashomon.get_segment_selection(cat_segment)
            self.html_parser.load_html_code(cat_code)
            name = self.html_parser.get_raw_text()
            title = ""
            url_list = self.html_parser.get_all_links()
            if url_list:
                url = url_list[0].a_href
            else:
                continue
            if name in remove_cat:
                continue

            result[str(count)] = {}
            result[str(count)]["name"] = name
            result[str(count)]["title"] = title
            result[str(count)]["url"] = self._fix_url(url)
            result[str(count)]["sub"] = {}
            count += 1
        
        return result

    def load_headlines(self, load_subcategories_for_id: str = None) -> bool:
        url = self.data.active_headline_url

        if not url:
            return False
        
        load_cat = None
        if self.data.categories:
            for i in self.data.categories:
                if i == "1":
                    continue
                if self.data.categories[i]["url"] == url:
                    if not self.data.categories[i]["sub"]:
                        load_cat = i
                        break

        result = self.load_project(url)
        if not result:
            return False

        # Load SubCategory if any
        if load_cat is not None:
            sub_cat = self._get_category_list()
            if sub_cat:
                self.data.categories[load_cat]["sub"] = sub_cat

        # Load Headlines
        result = self._load_headlines()

        if self.rashomon.errors():
            return False

        return result

    def _load_headlines(self):
        result = True
        if self.rashomon.is_segment("head_000"):
            head_type = 1
            result = self.rashomon.get_segment_selection("head")
            headline_codes = self.html_parser.get_tags(html_code=result, tag="div", tag_class_contains="floor__cell-shape", multiline=True)
            if headline_codes:
                result = True
                for headline_code in headline_codes:
                    if '<div class="cell-extension' in headline_code:
                        continue
                    is_ok = self._add_headline(headline_code=headline_code, head_type=head_type)
                    if not is_ok:
                        result = False
                return result
            else:
                headline_segments = self.rashomon.get_segment_children("head")
        elif self.rashomon.is_segment("head1_000"):
            head_type = 2
            headline_segments = self.rashomon.get_segment_children("head1")
        else:
            return self._add_headline2()

        for headline in headline_segments:
            headline_code = self.rashomon.get_segment_selection(headline)
            is_ok = self._add_headline(headline_code=headline_code, head_type=head_type)
            if not is_ok:
                result = False
        
        return result

    def _add_headline2(self) -> bool:
        page_code = self.rashomon.get_segment_selection("head")
        segments_code = self.html_parser.get_tags(html_code=page_code, tag="div", tag_class_contains="cell cell-list m-title", multiline=True)
        if not segments_code:
            return False
        for segment_code in segments_code:
            cat_code = self.html_parser.get_tags(html_code=segment_code, tag="a", multiline=True)
            cat = ""
            if cat_code:
                self.html_parser.load_html_code(cat_code[0])
                cat = self.html_parser.get_raw_text()

            items_code = self.html_parser.get_tags(html_code=segment_code, tag="a", tag_class_contains="cell-list__item", multiline=True)
            if items_code:
                for item_code in items_code:
                    # Image and title
                    image = self.base_default_image_path
                    title = ""
                    result = self.html_parser.get_tags(html_code=item_code, tag="img", multiline=False)
                    if result:
                        self.html_parser.load_html_code(result[0])
                        result = self.html_parser.get_all_images()
                        if result:
                            image = result[0].img_src
                    # Link
                    link = ""
                    self.html_parser.load_html_code(item_code)
                    result  = self.html_parser.get_all_links()
                    if result:
                        link = self._fix_url(result[0].a_href)
                    # Text and description
                    text = ""
                    desc = ""
                    result = self.html_parser.get_tags(html_code=item_code, tag="span", tag_class_contains="cell-list__item-title", multiline=True)
                    if result:
                        self.html_parser.load_html_code(result[0])
                        text = self.html_parser.get_raw_text()
                    # Time and date
                    time = ""
                    date = ""
                    result = self.html_parser.get_tags(html_code=item_code, tag="span", tag_class_contains="cell__controls-date", multiline=True)
                    if result:
                        self.html_parser.load_html_code(result[0])
                        date = self.html_parser.get_raw_text()

                    # Find next ID
                    next_id = self._get_next_headline_id()
                    
                    # Add Headline
                    self.data.headlines[next_id] = {}
                    self.data.headlines[next_id]["image"] = image
                    self.data.headlines[next_id]["text"] = text
                    self.data.headlines[next_id]["desc"] = desc
                    self.data.headlines[next_id]["title"] = title
                    self.data.headlines[next_id]["time"] = time
                    self.data.headlines[next_id]["date"] = date
                    self.data.headlines[next_id]["category"] = cat
                    self.data.headlines[next_id]["link"] = link
        return True

    def _add_headline(self, headline_code: str, head_type: int) -> bool:
        self.html_parser.load_html_code(headline_code)
        # Image and Title
        image = ""
        title = ""
        images = self.html_parser.get_all_images()
        if images:
            image = self._fix_url(images[0].img_src)
            title = images[0].img_title
        if not image:
            image = self.base_default_image_path
        # Link
        link = ""
        links = self.html_parser.get_all_links()
        if links:
            for i in links:
                if i.a_class.find("supertag") != -1:
                    continue
                if not i.a_href.endswith("html"):
                    continue
                link = self._fix_url(i.a_href)
                break
        if not link:
            return True   
                
        # Text and Description
        if head_type == 1:
            text = ""
            desc = ""
            text_code = self.html_parser.get_tags(html_code=headline_code, tag="div", tag_class_contains="cell-main-photo__info", multiline=True)
            if text_code:
                self.html_parser.load_html_code(text_code[0])
                text = self.html_parser.get_raw_text()
            else:
                text_code = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="cell-video__title", multiline=True)
                if text_code:
                    self.html_parser.load_html_code(text_code[0])
                    text = self.html_parser.get_raw_text()
                else:
                    text_code = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="__item-title", multiline=True)
                    if text_code:
                        self.html_parser.load_html_code(text_code[0])
                        text = self.html_parser.get_raw_text()
                    else:
                        text_code = self.html_parser.get_tags(html_code=headline_code, tag="div", tag_class_contains="cell-supertag__content", multiline=True)
                        if text_code:
                            self.html_parser.load_html_code(text_code[0])
                            text = self.html_parser.get_raw_text()
                        else:
                            text_code = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="cell-photo__title", multiline=True)
                            if text_code:
                                self.html_parser.load_html_code(text_code[0])
                                text = self.html_parser.get_raw_text()
                            else:
                                text_code = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="cell-media-cover__title", multiline=True)
                                if text_code:
                                    self.html_parser.load_html_code(text_code[0])
                                    text = self.html_parser.get_raw_text()
                                else:
                                    text_code = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="title", multiline=True)
                                    if text_code:
                                        self.html_parser.load_html_code(text_code[0])
                                        text = self.html_parser.get_raw_text()
                                    else:
                                        text_code = self.html_parser.get_tags(html_code=headline_code, tag="div", tag_class_contains="title", multiline=True)
                                        if text_code:
                                            self.html_parser.load_html_code(text_code[0])
                                            text = self.html_parser.get_raw_text()

            if not text:
                text = title
        elif head_type == 2:
            text = ""
            desc = ""
            texts = self.html_parser.get_tags(html_code=headline_code, tag="a", tag_class_contains="list__title", multiline=True)
            if texts:
                self.html_parser.load_html_code(texts[0])
                text = self.html_parser.get_raw_text()
            descs = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="author", multiline=True)
            if descs:
                self.html_parser.load_html_code(descs[0])
                desc = self.html_parser.get_raw_text()
        # Time
        time = ""
        # Date
        date = ""
        times = self.html_parser.get_tags(html_code=headline_code, tag="span", tag_class_contains="date", multiline=True)
        if times:
            self.html_parser.load_html_code(times[0])
            date = self.html_parser.get_raw_text()
        # Category
        if head_type == 1:
            cat = ""
            cats = self.html_parser.get_tags(html_code=headline_code, tag="a", tag_class_contains="supertag", multiline=True)
            if cats:
                self.html_parser.load_html_code(cats[0])
                cat = self.html_parser.get_raw_text()
        elif head_type == 2:
            cat = ""
            cats = self.html_parser.get_tags(html_code=headline_code, tag="a", tag_class_contains="tag__text", multiline=True)
            if cats:
                self.html_parser.load_html_code(cats[0])
                cat = self.html_parser.get_raw_text()
        
        # Check if headline exist
        for i in self.data.headlines:
            if self.data.headlines[i]["link"] == link:
                if not self.data.headlines[i]["image"]:
                    self.data.headlines[i]["image"] = image
                if not self.data.headlines[i]["text"]:
                    self.data.headlines[i]["text"] = text
                if not self.data.headlines[i]["desc"]:
                    self.data.headlines[i]["desc"] = desc
                if not self.data.headlines[i]["title"]:
                    self.data.headlines[i]["title"] = title
                if not self.data.headlines[i]["time"]:
                    self.data.headlines[i]["time"] = time
                if not self.data.headlines[i]["date"]:
                    self.data.headlines[i]["date"] = date
                if not self.data.headlines[i]["category"]:
                    self.data.headlines[i]["category"] = cat
                return True

        # Find next ID
        next_id = self._get_next_headline_id()
        
        # Add Headline
        self.data.headlines[next_id] = {}
        self.data.headlines[next_id]["image"] = image
        self.data.headlines[next_id]["text"] = text
        self.data.headlines[next_id]["desc"] = desc
        self.data.headlines[next_id]["title"] = title
        self.data.headlines[next_id]["time"] = time
        self.data.headlines[next_id]["date"] = date
        self.data.headlines[next_id]["category"] = cat
        self.data.headlines[next_id]["link"] = link
        return True

    def _get_next_headline_id(self) -> str:
        next_id = 1
        for i in self.data.headlines:
            if int(i) > next_id:
                next_id = int(i)
        
        next_id += 1
        return str(next_id)

    def load_page(self) -> bool:
        if self.data.get_page(self.data.active_page):
            return True
        
        url = self.data.active_page

        if not url:
            return False
        
        self.rashomon.clear_errors()
        result = self.load_project(url)
        if not result or self.rashomon.errors():
            return False

        result = self._get_page_data(url)
        if not result:
            return False
        
        result["url"] = url
        self.data.add_page(result)
        return True

    def _get_page_data(self, page_url: str = None) -> bool:
        # Lead
        page_lead = ""

        # Page Text and tables
        text_slices = []
        page_tables = []
        if self.rashomon.is_segment("page_text_000"):
            # Text
            page_content_code_raw = self.rashomon.get_segment_selection("page_text_000")

            page_content_code_raw = self.html_parser.remove_specific_tag(page_content_code_raw, 'blockquote', multiline=True)
            page_content_code_raw = self.html_parser.remove_specific_tag(page_content_code_raw, 'section', multiline=True)
            page_content_code_raw = self.html_parser.remove_specific_tag(page_content_code_raw, 'figcaption', multiline=True)
            page_content_code_raw = self.html_parser.remove_specific_tag(page_content_code_raw, 'cite', multiline=True)
            page_content_code_raw = self.html_parser.remove_specific_tag(page_content_code_raw, 'script', multiline=True)
            page_content_code_raw = self.html_parser.remove_specific_tag(page_content_code_raw, 'style', multiline=True)
            
            page_content_code_raw = page_content_code_raw.replace('<div class="article__block"', '<br>\n<div class="article__block"')
            page_content_code_raw = page_content_code_raw.replace('</div>', '<br>\n</div>')

            page_text_code_raw1 = page_content_code_raw
            page_text_code_raw1 = self.html_parser.remove_specific_tag(html_code=page_text_code_raw1, tag="table", multiline=True)
            in_tag = False
            page_text_code_raw = ""
            for line in page_text_code_raw1.splitlines():
                if line.startswith(('<div class="online__caption-title">', '<div class="online__sort"', '<div class="photoview', '<div class="media')):
                    in_tag = True
                if not in_tag:
                    page_text_code_raw += line + "\n"
                if line.startswith("</div>"):
                    in_tag = False

            self.html_parser.load_html_code(page_text_code_raw)
            text_slices = self.html_parser.get_all_text_slices()
            page_text = self.html_parser.get_raw_text()

            for text_slice in text_slices:
                text_slice.txt_link = self._fix_url(text_slice.txt_link)
            # Tables
            self.html_parser.load_html_code(page_content_code_raw)
            page_tables = self.html_parser.get_all_tables()
        
        if not text_slices:
            return False

        # Images
        self.rashomon.clear_errors()
        image_main = ""
        image_other = []
        if self.rashomon.is_segment("page_main_image_000"):
            main_image_code = self.rashomon.get_segment_selection("page_main_image_000")

            self.html_parser.load_html_code(main_image_code)
            result = self.html_parser.get_all_images()
            if result:
                image_main = self._fix_url(result[0].img_src)
            else:
                image_main = self.base_default_image_path
        
        main_image_code_raw = self.rashomon.get_segment_selection("page_text_000")
        in_tag = False
        main_image_code = ""
        for line in main_image_code_raw.splitlines():
            if line.startswith(('<div class="footer__apps"', '<i class="footer__logo-icon"')):
                in_tag = True
            if not in_tag:
                main_image_code += line + "\n"
            if line.startswith(("</div>", "</i>")):
                in_tag = False
        self.html_parser.load_html_code(main_image_code)
        images_other = self.html_parser.get_all_images()
        if images_other:
            for image_obj in images_other:
                image_other.append(self._fix_url(image_obj.img_src))
        # Title
        self.rashomon.clear_errors()
        page_title = ""
        if self.rashomon.is_segment("page_title_000"):
            page_title = self.rashomon.get_segment_selection("page_title_000", remove_tags=True, join_in_one_line=True)
        
        # Date
        self.rashomon.clear_errors()
        page_date = ""
        if self.rashomon.is_segment("page_date_000"):
            page_date = self.rashomon.get_segment_selection("page_date_000", remove_tags=True, join_in_one_line=True).replace("&gt;", ">")
            while True:
                page_date = page_date.replace("    ", "   ")
                if page_date.find("    ") == -1:
                    break

        # Author name and page
        author_name = ""
        author_page = ""
        self.rashomon.clear_errors()
        author_code = self.rashomon.get_segment_selection("page_author_000")
        if author_code:
            author_name_code = self.html_parser.get_tags(html_code=author_code, tag="div", custom_tag_property=[["itemprop", "name"]], multiline=True)
            author_name = self.rashomon.remove_tags(author_name_code, join_in_one_line=True)
            self.html_parser.load_html_code(author_code)
            author_page_links = self.html_parser.get_all_links()
            if author_page_links:
                author_page = self._fix_url(author_page_links[0].a_href)

        # Page tags
        page_tags = []
        self.rashomon.clear_errors()
        if self.rashomon.is_segment("page_tags_000"):
            self.html_parser.load_html_code(self.rashomon.get_segment_selection("page_tags_000"))
            tags_obj = self.html_parser.get_all_links()
            for i in tags_obj:
                if i.a_href:
                    link = self._fix_url(i.a_href)
                    page_tags.append([i.a_text, link])

        # Related content
        related_content = {}

        # Videos
        videos = []
        video_code_raw = self.rashomon.get_segment_selection("page_text_000")
        video_code = self.html_parser.get_tags(html_code=video_code_raw, tag="iframe", multiline=True)
        if video_code:
            for iframe in video_code:
                video_url = ""
                video_id = ""
                start = iframe.find('src="')
                if start != -1:
                    end = iframe.find('"', start+5)
                    if end != -1:
                        video_url = iframe[start+5:end]
                start = iframe.find('id="')
                if start != -1:
                    end = iframe.find('"', start+4)
                    if end != -1:
                        video_id = iframe[start+4:end]
                if video_url:
                    videos.append([self._fix_url(video_url), video_id])
        video_code = self.html_parser.get_tags(html_code=video_code_raw, tag="blockquote", multiline=True)
        if video_code:
            for blockquote in video_code:
                self.html_parser.load_html_code(blockquote)
                result = self.html_parser.get_all_links()
                if result:
                    videos.append([self._fix_url(result[-1].a_href), ""])

        # Audio
        audio = []

        page_dict = {
            "lead": page_lead,
            "text": page_text,
            "text_slices": text_slices,
            "main_image": image_main,
            "images": image_other,
            "date": page_date,
            "title": page_title,
            "author_name": author_name,
            "author_page": author_page,
            "tags": page_tags,
            "related": related_content,
            "videos": videos,
            "audios": audio,
            "tables": page_tables
        }
        return page_dict


class NewsRTS(AbstractNewsSource):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, news_data_object: NewsData) -> None:
        super().__init__(parent_widget, settings, news_data_object)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.base_site_url = "https://www.rts.rs"
        self.base_default_image_path = self.getv("online_news_rts_page_def_img_path")
        self.search_available = "https://www.rts.rs/pretraga.html?lang=sr&searchText="

    def load_project(self, source: str = None) -> bool:
        project_file = self.getv("rashomon_folder_path") + "rts_news.rpf"
        if not source:
            source = "https://www.rts.rs/sr/index.html"

        if self.rashomon.project_name == project_file and self.rashomon.get_source() == source:
            self.project_loaded = True
            return True
        
        self.project_loaded = False
        
        self.rashomon.errors(clear_errors=True)
        result = self.rashomon.load_project(project_file, change_source=source)
        if self.rashomon.errors() or not result:
            return False

        self.rashomon.set_compatible_mode(True)
        if self.rashomon.errors():
            return False

        self.rashomon.recreate_segment_tree()
        if self.rashomon.errors():
            return False

        self.project_loaded = True
        return True

    def load_categories(self) -> bool:
        if not self.project_loaded:
            if not self.load_project():
                return False
            
        self.rashomon.clear_errors()
        categories_html = self.rashomon.get_segment_selection("cat_000")
        if self.rashomon.errors():
            return False
        
        self.html_parser.load_html_code(categories_html)

        lists = self.html_parser.get_all_lists()
        if not lists:
            return False

        remove_cat = [
            "OKO",
            "ТВ",
            "Радио",
            "Емисије",
            "РТС",
            "Остало",
            "Видео дана",
            "Архива рубрика",
            "Гледаоци репортери"
        ]
        
        result = {}
        main_count = 1
        for main_cat in lists[0].sub_items:
            if not main_cat.get_link_url() or main_cat.text.strip() in remove_cat:
                continue

            result[str(main_count)] = {}
            name = main_cat.text.strip()
            result[str(main_count)]["name"] = name
            result[str(main_count)]["title"] = main_cat.title.strip()
            cat_url = self._fix_url(main_cat.get_link_url())
            result[str(main_count)]["url"] = cat_url
            
            result[str(main_count)]["sub"] = {}
            sub_count = 1
            for sub_cat in main_cat.sub_items:
                if not sub_cat.get_link_url() or sub_cat.text.strip() in remove_cat:
                    continue
                name = sub_cat.text.strip()
                result[str(main_count)]["sub"][str(sub_count)] = {}
                result[str(main_count)]["sub"][str(sub_count)]["name"] = name
                result[str(main_count)]["sub"][str(sub_count)]["title"] = sub_cat.title.strip()
                cat_url = self._fix_url(sub_cat.get_link_url())
                result[str(main_count)]["sub"][str(sub_count)]["url"] = cat_url
                result[str(main_count)]["sub"][str(sub_count)]["sub"] = {}
                
                if sub_cat.sub_items:
                    for extra_sub_cat in sub_cat.sub_items:
                        if not extra_sub_cat.get_link_url() or extra_sub_cat.text.strip() in remove_cat:
                            continue
                        sub_count += 1
                        name = extra_sub_cat.text.strip()
                        result[str(main_count)]["sub"][str(sub_count)] = {}
                        result[str(main_count)]["sub"][str(sub_count)]["name"] = name
                        result[str(main_count)]["sub"][str(sub_count)]["title"] = extra_sub_cat.title.strip()
                        cat_url = self._fix_url(extra_sub_cat.get_link_url())
                        result[str(main_count)]["sub"][str(sub_count)]["url"] = cat_url
                        result[str(main_count)]["sub"][str(sub_count)]["sub"] = {}

                sub_count += 1
            main_count += 1
        
        self.data.categories = result
        return True

    def load_headlines(self) -> bool:
        url = self.data.active_headline_url

        if not url:
            return False
        
        result = self.load_project(url)
        if not result:
            return False
        
        search_code = self.rashomon.get_segment_selection("content_final")
        search_results = self.html_parser.get_tags(html_code=search_code, tag="div", tag_class_contains="storyNav fix  searchStory", multiline=True)
        if self.rashomon.is_segment("head1_000"):
            segment_to_load = "head1_000"
            data = self.rashomon.get_segment_selection(segment_to_load)
        elif self.rashomon.is_segment("head2_000"):
            segment_to_load = "head2_000"
            data = self.rashomon.get_segment_selection(segment_to_load)
        elif self.rashomon.is_segment("content_final_000"):
            return self._load_headline_type2()
        elif search_results:
            return self._load_headline_type3(search_results)
        else:
            data = ""
        if self.rashomon.errors():
            return False

        result = False
        if data:
            result = self._load_headline_type1(segment_to_load)
        
        return result

    def _load_headline_type3(self, search_results: list) -> bool:
        for headline_code in search_results:
            self._add_headline_type1(headline_code)
        
        return True

    def _load_headline_type2(self) -> bool:
        headlines_segments = self.rashomon.get_segment_children("content_final")
        if not headlines_segments:
            return False
        
        for headline_segment in headlines_segments:
            headline_data = self.rashomon.get_segment_selection(headline_segment)
            if not headline_data:
                continue
            self._add_headline_type1(headline_data)
        
        return True
    
    def _load_headline_type1(self, head_segment: str):
        if not self.rashomon.is_segment(head_segment):
            return False

        html_code = self.rashomon.get_segment_selection(head_segment)
        self.html_parser.load_html_code(html_code)
        headlines = self.html_parser.get_tags(html_code=html_code, tag="div", tag_class_contains="element", multiline=True)
        
        result = True
        for headline in headlines:
            is_ok = self._add_headline_type1(headline)
            if not is_ok:
                result = False
        
        return result

    def _add_headline_type1(self, html_code: str) -> bool:
        # Image and Title
        image = ""
        title = ""
        image_code = self.html_parser.get_tags(html_code=html_code, tag="img", multiline=False)
        if image_code:
            self.html_parser.load_html_code(image_code[0])
            result = self.html_parser.get_all_images()
            if result:
                image = self._fix_url(result[0].img_src)
                title = result[0].img_title
        # Text and Link
        text = ""
        news_link = ""
        text_code = self.html_parser.get_tags(html_code=html_code, tag="h3", multiline=True)
        if text_code:
            self.html_parser.load_html_code(text_code[0])
            text = self.html_parser.get_raw_text()
            if self.html_parser.get_all_links():
                news_link = self._fix_url(self.html_parser.get_all_links()[0].a_href)
        else:
            text_code = self.html_parser.get_tags(html_code=html_code, tag="a", multiline=True)
            if len(text_code) > 1:
                self.html_parser.load_html_code(text_code[1])
                text = self.html_parser.get_raw_text()
                result = self.html_parser.get_all_links()
                if result:
                    news_link = self._fix_url(result[0].a_href)
        if not text:
            text_code = self.html_parser.get_tags(html_code=html_code, tag="h2", multiline=True)
            if text_code:
                self.html_parser.load_html_code(text_code[0])
                text = self.html_parser.get_raw_text().strip()
        if not news_link:
            self.html_parser.load_html_code(html_code)
            if self.html_parser.get_all_links():
                news_link = self._fix_url(self.html_parser.get_all_links()[0].a_href)
        # Description
        desc = ""
        desc_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="lead", multiline=True)
        if desc_code:
            self.html_parser.load_html_code(desc_code[0])
            if self.html_parser.get_raw_text():
                desc = self.html_parser.get_raw_text()
        else:
            desc_code = self.html_parser.get_tags(html_code=html_code, tag="div", tag_class_contains="newsText", multiline=True)
            if desc_code:
                self.html_parser.load_html_code(desc_code[0])
                desc = self.html_parser.get_raw_text()
        # Time
        news_time = ""
        # Date
        news_date = ""
        news_date_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="dateTime", multiline=True)
        if news_date_code:
            self.html_parser.load_html_code(news_date_code[0])
            news_date = self.html_parser.get_raw_text().replace("&gt;", ">")
        if not news_date:
            news_date_code = self.html_parser.get_tags(html_code=html_code, tag="p", tag_class_contains="date", multiline=True)
            if news_date_code:
                self.html_parser.load_html_code(news_date_code[0])
                news_date = self.html_parser.get_raw_text().replace("&gt;", ">")
        # Category
        news_cat = ""
        news_cat_code = self.html_parser.get_tags(html_code=html_code, tag="div", tag_class_contains="uptitleHolder", multiline=True)
        if news_cat_code:
            self.html_parser.load_html_code(news_cat_code[0])
            news_cat = self.html_parser.get_raw_text()

        # Find next ID
        next_id = self._get_next_headline_id()
        
        # Add Headline
        self.data.headlines[next_id] = {}
        self.data.headlines[next_id]["image"] = image
        self.data.headlines[next_id]["text"] = text
        self.data.headlines[next_id]["desc"] = desc
        self.data.headlines[next_id]["title"] = title
        self.data.headlines[next_id]["time"] = news_time
        self.data.headlines[next_id]["date"] = news_date
        self.data.headlines[next_id]["category"] = news_cat
        self.data.headlines[next_id]["link"] = news_link
        return True

    def _get_next_headline_id(self) -> str:
        next_id = 1
        for i in self.data.headlines:
            if int(i) > next_id:
                next_id = int(i)
        
        next_id += 1
        return str(next_id)

    def load_page(self) -> bool:
        if self.data.get_page(self.data.active_page):
            return True
        
        url = self.data.active_page

        if not url:
            return False
        
        self.rashomon.clear_errors()
        result = self.load_project(url)
        if not result or self.rashomon.errors():
            return False

        result = self._get_page_data(url)
        if not result:
            return False
        
        result["url"] = url
        self.data.add_page(result)
        return True

    def _get_page_data(self, page_url: str = None) -> bool:
        # Lead
        self.rashomon.clear_errors()
        page_lead = ""
        if self.rashomon.is_segment("page_subtitle_000"):
            page_lead = self.rashomon.get_segment_selection("page_subtitle_000", remove_tags=True, join_in_one_line=True)

        # Page Text and tables
        text_slices = []
        page_tables = []
        if self.rashomon.is_segment("page_content_000"):
            # Text
            page_content_code_raw = self.rashomon.get_segment_selection("page_content_000")
            page_text_code_raw = page_content_code_raw
            if "kursna-lista-za" in page_url.lower():
                page_text_code_raw = self.html_parser.remove_specific_tag(html_code=page_text_code_raw, tag="table", multiline=True)
            page_text_code = ""
            write = True
            for i in page_text_code_raw.splitlines():
                if i.strip().startswith('<a class="btn-socia'):
                    write = False
                if write:
                    page_text_code += i + "\n"
                if i.strip().startswith("</a>"):
                    write = True

            self.html_parser.load_html_code(page_text_code)
            text_slices = self.html_parser.get_all_text_slices()
            page_text = self.html_parser.get_raw_text()

            for text_slice in text_slices:
                text_slice.txt_link = self._fix_url(text_slice.txt_link)
            # Tables
            self.html_parser.load_html_code(page_content_code_raw)
            page_tables = self.html_parser.get_all_tables()
        
        if not text_slices:
            return False

        # Images
        self.rashomon.clear_errors()
        image_main = ""
        image_other = []
        if self.rashomon.is_segment("page_images_000"):
            images_code = self.rashomon.get_segment_selection("page_images_000")
            images = self.html_parser.get_tags(html_code=images_code, tag="img", multiline=False)
            if images:
                for i in range(0, len(images)):
                    self.html_parser.load_html_code(images[i])
                    result = self.html_parser.get_all_images()
                    if result and not image_main:
                        image_main = self._fix_url(result[0].img_src)
                        continue
                    if result:
                        image_other.append(self._fix_url(result[i].img_src))
        if not image_main:
            if self.rashomon.is_segment("cat"):
                images_code = self.rashomon.get_segment_selection("cat")
                images = self.html_parser.get_tags(html_code=images_code, tag="meta", custom_tag_property=[["property", "og:image"]], multiline=False)
                if images:
                    for i in images:
                        start = i.find('content="')
                        if start != -1:
                            end = i.find('"', start+9)
                            if end != -1:
                                img_url = i[start+9:end]
                                if not image_main:
                                    image_main = self._fix_url(img_url)
                                    continue
                                image_other.append(self._fix_url(img_url))

        # Title
        self.rashomon.clear_errors()
        page_title = ""
        if self.rashomon.is_segment("page_title_000"):
            page_title = self.rashomon.get_segment_selection("page_title_000", remove_tags=True, join_in_one_line=True)
        
        # Date
        self.rashomon.clear_errors()
        page_date = ""
        if self.rashomon.is_segment("page_date_000"):
            page_date = self.rashomon.get_segment_selection("page_date_000", remove_tags=True, join_in_one_line=True).replace("&gt;", ">")
            while True:
                page_date = page_date.replace("    ", "   ")
                if page_date.find("    ") == -1:
                    break

        # Author name and page
        author_name = ""
        author_page = ""
        self.rashomon.clear_errors()
        if self.rashomon.is_segment("page_author_000"):
            author_name = self.rashomon.get_segment_selection("page_author_000", remove_tags=True, join_in_one_line=True).replace("&gt;", ">")

        # Page tags
        page_tags = []
        self.rashomon.clear_errors()
        if self.rashomon.is_segment("page_tags_000"):
            self.html_parser.load_html_code(self.rashomon.get_segment_selection("page_tags_000"))
            tags_obj = self.html_parser.get_all_links()
            for i in tags_obj:
                if i.a_href:
                    link = self._fix_url(i.a_href)
                    page_tags.append([i.a_text, link])

        # Related content
        related_content = {}
        result = self._get_page_related_content()
        if result:
            related_content = result

        # Videos
        videos = []

        # Audio
        audio = []
        if self.rashomon.is_segment("page_read_000"):
            audio_code = self.rashomon.get_segment_selection("page_read_000")
            start = audio_code.find('src="')
            if start != -1:
                end = audio_code.find('"', start + 5)
                if end != -1:
                    audio.append(self._fix_url(audio_code[start+5:end]))

        page_dict = {
            "lead": page_lead,
            "text": page_text,
            "text_slices": text_slices,
            "main_image": image_main,
            "images": image_other,
            "date": page_date,
            "title": page_title,
            "author_name": author_name,
            "author_page": author_page,
            "tags": page_tags,
            "related": related_content,
            "videos": videos,
            "audios": audio,
            "tables": page_tables
        }
        return page_dict

    def _get_page_related_content(self) -> dict:
        self.rashomon.clear_errors()
        html_code = self.rashomon.get_segment_selection("page_date")
        if self.rashomon.errors() or not html_code:
            return None
        
        related_content = {}

        related_code = self.html_parser.get_tags(html_code=html_code, tag="div", tag_class_contains="item fix", multiline=True)
        if not related_code:
            return None
        
        count = 1
        for related_item_code in related_code:
            # Title
            title_code = self.html_parser.get_tags(html_code=related_item_code, tag="h5", multiline=True)
            self.html_parser.load_html_code(title_code[0])
            title = self.html_parser.get_raw_text()
            # Time
            time = ""
            time_code = self.html_parser.get_tags(html_code=related_item_code, tag="span", tag_class_contains="date", multiline=True)
            if time_code:
                self.html_parser.load_html_code(time_code[0])
                time = self.html_parser.get_raw_text()
            # Url
            url = ""
            self.html_parser.load_html_code(html_code=related_item_code)
            links = self.html_parser.get_all_links()
            if links:
                url = self._fix_url(links[0].a_href)
            if not url:
                continue
            # Category
            category = ""
            # Image
            image = ""
            image_code = self.html_parser.get_tags(html_code=related_item_code, tag="img", multiline=False)
            if image_code:
                self.html_parser.load_html_code(image_code[0])
                images = self.html_parser.get_all_images()
            if images:
                image = self._fix_url(images[0].img_src)
            
            if url:
                related_content[str(count)] = {}
                related_content[str(count)]["title"] = title
                related_content[str(count)]["time"] = time
                related_content[str(count)]["url"] = url
                related_content[str(count)]["category"] = category
                related_content[str(count)]["image"] = image
                count += 1

        return related_content


class NewsTEST(AbstractNewsSource):
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings, news_data_object: NewsData) -> None:
        super().__init__(parent_widget, settings, news_data_object)
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        self.data.name = "test"
        self.data.project_file_path = self.getv("rashomon_folder_path") + "test has no project !"

    def load_categories(self) -> bool:
        result = {
            "1": {
                "name": "Category1",
                "title": "This is first main category !",
                "url": "",
                "sub": {}
            },
            "2": {
                "name": "Category2",
                "title": "This is second main category !",
                "url": "",
                "sub": {
                    "1": {
                        "name": "SubCat1",
                        "title": "This is first SubCategory !",
                        "url": ""
                    },
                    "2": {
                        "name": "SubCatalogue on line 2",
                        "title": "This is first SubCategory !",
                        "url": ""
                    },
                    "3": {
                        "name": "SubCat3",
                        "title": "This is first SubCategory !",
                        "url": ""
                    }
                }
            }
        }
        self.data.categories = result
        return True


class CategoryItem(QFrame):
    SCALE = 1.1
    def __init__(self, 
                 parent_widget: QWidget, 
                 settings: settings_cls.Settings,
                 name: str,
                 title: str,
                 item_id: str,
                 url:str,
                 item_type: int,
                 click_function = None):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.name = name
        self.title = title
        self.item_id = item_id
        self.url = url
        self.item_type = item_type
        self.click_function = click_function
        
        self._active_item = False

        self.create_widget()

        # Connect events with slots

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if self.click_function:
            self.click_function(self)
        return super().mousePressEvent(a0)
    
    def enterEvent(self, a0: QEvent) -> None:
        if not self._active_item:
            if self.item_type == 1:
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_cat_item_main_hover_image_path")))
            elif self.item_type == 2:
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_subcat_item_main_hover_image_path")))
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        if not self._active_item:
            if self.item_type == 1:
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_cat_item_main_idle_image_path")))
            elif self.item_type == 2:
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_subcat_item_main_idle_image_path")))
        return super().leaveEvent(a0)

    def set_active(self, value: bool):
        self._active_item = value
        if value:
            font = self.lbl_txt.font()
            font.setBold(True)
            self.lbl_txt.setFont(font)
            if self.item_type == 1:
                self.lbl_txt.setStyleSheet("background-color: rgba(0,0,0,0); color: #ffff00")
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_cat_item_main_active_image_path")))
            elif self.item_type == 2:
                self.lbl_txt.setStyleSheet("background-color: rgba(0,0,0,0); color: #ffff00")
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_subcat_item_main_active_image_path")))
        else:
            font = self.lbl_txt.font()
            font.setBold(False)
            self.lbl_txt.setFont(font)
            if self.item_type == 1:
                self.lbl_txt.setStyleSheet("background-color: rgba(0,0,0,0); color: #00007f")
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_cat_item_main_idle_image_path")))  
            elif self.item_type == 2:
                self.lbl_txt.setStyleSheet("background-color: rgba(0,0,0,0); color: #00007f")
                self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_subcat_item_main_idle_image_path")))

    def is_active(self) -> bool:
        return self._active_item

    def create_widget(self):
        # Define Frame
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setToolTip(self.title)
        self.setCursor(Qt.PointingHandCursor)
        # Define Height
        h = self.parent_widget.height()
        h -= self.parent_widget.contentsMargins().top()
        h -= self.parent_widget.contentsMargins().bottom()
        # Define backgroung image label
        self.lbl_pic = QLabel(self)
        self.lbl_pic.setScaledContents(True)
        if self.item_type == 1:
            self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_cat_item_main_idle_image_path")))
        elif self.item_type == 2:
            self.lbl_pic.setPixmap(QPixmap(self.getv("online_news_subcat_item_main_idle_image_path")))
        # Define item text label
        self.lbl_txt = QLabel(self)
        self.lbl_txt.setStyleSheet("background-color: rgba(0,0,0,0); color: #00007f")
        self.lbl_txt.setText(f"   {self.name}   ")
        self.lbl_txt.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        font = self.parent_widget.font()
        self.lbl_txt.setFont(font)
        self.lbl_txt.adjustSize()
        # Set labels size and position
        w = int(self.lbl_txt.width() * self.SCALE)
        self.lbl_txt.move(0, 0)
        self.lbl_txt.resize(w, h)
        self.lbl_pic.move(0, 0)
        self.lbl_pic.resize(w, h)
        # Set Frame size
        self.setFixedWidth(w)
        self.setFixedHeight(h)


class HeadlineItem(QFrame):
    ITEM_HEIGHT = 150
    ITEM_WIDTH = 480
    def __init__(self, 
                 parent_widget: QWidget, 
                 settings: settings_cls.Settings,
                 item_id: str,
                 item_img_url: str,
                 text: str,
                 description: str,
                 title: str,
                 url:str,
                 item_category: str,
                 item_time: str,
                 item_date: str,
                 click_function = None):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.text = text
        self.desc = description
        self.title = title
        self.item_img_url = item_img_url
        self.item_id = item_id
        self.url = url
        self.item_category = item_category
        self.item_time = item_time
        self.item_date = item_date
        self.click_function = click_function
        
        self._active_item = False

        self.create_widget()

        # Connect events with slots

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if self.click_function:
            self.click_function(self)
        return super().mousePressEvent(a0)

    def create_widget(self):
        # Define Frame
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        # Define Frame width
        self.setFixedWidth(self.ITEM_WIDTH)
        # Define headline image label
        self.lbl_pic = QLabel(self)
        self.lbl_pic.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.lbl_pic.move(0, 0)
        self.lbl_pic.resize(self.ITEM_HEIGHT, self.ITEM_HEIGHT)
        self.lbl_pic.setCursor(Qt.PointingHandCursor)
        self.lbl_pic.setToolTip(self.title)
        # Define read more label
        self.lbl_read_more = QLabel(self)
        self.lbl_read_more.resize(self.ITEM_WIDTH - self.lbl_pic.width() - 10, 25)
        self.lbl_read_more.setText(self.getl("online_topic_news_headline_item_lbl_read_more_text"))
        self.lbl_read_more.setToolTip(self.getl("online_topic_news_headline_item_lbl_read_more_tt"))
        font = self.lbl_read_more.font()
        font.setPointSize(12)
        self.lbl_read_more.setFont(font)
        self.lbl_read_more.setStyleSheet("QLabel {color: #aaffff ;} QLabel::hover {color: #00ffff ;}")
        self.lbl_read_more.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.lbl_read_more.setCursor(Qt.PointingHandCursor)
        # Define headline text label
        self.lbl_text = QLabel(self)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        if self.desc:
            txt = f"{self.text}\n#2"
            text_to_html = utility_cls.TextToHTML(txt)
            text_to_html.general_rule.fg_color = "#00ff00"
            text_to_html.general_rule.font_size = 14
            desc_rule = utility_cls.TextToHtmlRule("#2", replace_with=self.desc, fg_color="#aaff00", font_size=12)
            text_to_html.add_rule(desc_rule)
            self.lbl_text.setText(text_to_html.get_html())
        else:
            self.lbl_text.setText(self.text)
            font = self.lbl_text.font()
            font.setPointSize(14)
            self.lbl_text.setFont(font)
            self.lbl_text.setStyleSheet("QLabel {color: #00ff00;}")
        self.lbl_text.setFixedWidth(self.ITEM_WIDTH - self.lbl_pic.width() - 10)
        self.lbl_text.adjustSize()
        # Set position and size of widgets
        if self.lbl_text.height() + 25 > self.ITEM_HEIGHT:
            self.setFixedHeight(self.lbl_text.height() + 25)
            self.lbl_text.move(self.lbl_pic.width() + 10, 0)
            self.lbl_read_more.move(self.lbl_text.pos().x(), self.lbl_text.height() + self.lbl_text.pos().y())
        else:
            y = int((self.ITEM_HEIGHT - self.lbl_text.height()) / 2)
            self.lbl_text.move(self.lbl_pic.width() + 10, y)
            self.lbl_read_more.move(self.lbl_text.pos().x(), self.lbl_text.height() + self.lbl_text.pos().y())
            self.setFixedHeight(max(self.ITEM_HEIGHT, self.lbl_read_more.height() + self.lbl_read_more.pos().y()))
        # Define category name label
        self.lbl_cat = QLabel(self)
        if not self.item_category.strip():
            self.lbl_cat.setVisible(False)
        self.lbl_cat.setText(f" {self.item_category}  ")
        self.lbl_cat.setStyleSheet("color: #ffffff; background-color: rgba(0, 170, 255, 100);")
        self.lbl_cat.adjustSize()
        self.lbl_cat.move(5, 5)
        # Define time label
        self.lbl_time = QLabel(self)
        if not self.item_time.strip():
            self.lbl_time.setVisible(False)
        self.lbl_time.setText(self.item_time)
        self.lbl_time.setStyleSheet("color: #ffff00; background-color: rgba(0, 0, 0, 70);")
        self.lbl_time.adjustSize()
        self.lbl_time.move(self.lbl_pic.width() - self.lbl_time.width() - 5, 5)
        # Define date label
        if self.item_date:
            self.lbl_date = QLabel(self)
            if not self.item_date.strip():
                self.lbl_date.setVisible(False)
            self.lbl_date.setText(f"  {self.item_date}")
            self.lbl_date.setStyleSheet("color: rgb(255, 255, 255); background-color: rgba(85, 0, 127, 125);")
            self.lbl_date.adjustSize()
            self.lbl_date.move(self.lbl_pic.width() - self.lbl_date.width() - 5, self.lbl_time.height() + 5)


class PageRelatedItem(QFrame):
    ITEM_HEIGHT = 150
    TEXT_FONT = QFont("Arial", 16)
    def __init__(self, 
                 parent_widget: QWidget, 
                 settings: settings_cls.Settings,
                 item_index: int,
                 item_url: str,
                 item_text: str,
                 item_image: str,
                 item_category: str,
                 item_date: str):
        super().__init__(parent_widget)

        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Define variables
        self.parent_widget = parent_widget
        self.item_text = item_text
        self.item_url = item_url
        self.item_index = item_index
        self.item_category = item_category
        self.item_date = item_date
        self.item_image = item_image
        
        self.create_widget()

        # Connect events with slots

    def arange_widgets(self):
        self.lbl_pic.move(0, 0)

        x = self.lbl_pic.width() + 10
        y = 0
        w = self.contentsRect().width() - self.lbl_pic.width() - 15
        if w < 200:
            w = 200

        self.lbl_cat.move(x, y)

        self.lbl_date.move(x + self.lbl_cat.width() + 10, y)
        y += self.lbl_date.height()

        self.lbl_text.move(x, y)
        self.lbl_text.setFixedWidth(w)
        self.lbl_text.adjustSize()
        
        self.resize(self.width(), max(self.height(), self.lbl_text.height() + y + 5))
        text_available_heigh = self.contentsRect().height() - y
        if self.lbl_text.height() < text_available_heigh:
            self.lbl_text.resize(self.lbl_text.width(), text_available_heigh)
    
    def create_widget(self):
        font = self.font()
        font.setBold(True)
        font.setPointSize(14)

        self.resize(self.parent_widget.width(), self.ITEM_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        # self.setStyleSheet("QFrame {color: ##aaaaff;} QFrame::hover {color: #aaffff;}")
        
        # Image
        self.lbl_pic = QLabel(self)
        self.lbl_pic.setAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
        self.lbl_pic.resize(self.ITEM_HEIGHT, self.ITEM_HEIGHT)

        # Text
        self.lbl_text = QLabel(self)
        self.lbl_text.setStyleSheet("QLabel {color: #aaaaff;} QLabel::hover {color: #aaffff;}")
        self.lbl_text.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setText(self.item_text)
        self.lbl_text.setFont(self.TEXT_FONT)

        # Category
        self.lbl_cat = QLabel(self)
        self.lbl_cat.setText(self.item_category)
        self.lbl_cat.setFont(font)
        self.lbl_cat.adjustSize()
        self.lbl_cat.setStyleSheet("color: #ffff00; background-color: rgba(0, 154, 231, 100);")
        
        # Date
        self.lbl_date = QLabel(self)
        self.lbl_date.setStyleSheet("color: white; background-color: #7900b5;")
        self.lbl_date.setText(self.item_date)
        self.lbl_date.setFont(font)
        self.lbl_date.adjustSize()


class News(AbstractTopic):
    MIN_PAGE_SIDE_TEXT_WIDTH = 200
    PAGE_TEXT_FONT = QFont("Arial", 16)
    PAGE_TAG_FONT = QFont("Arial", 16)
    def __init__(self, parent_widget: QWidget, settings: settings_cls.Settings) -> None:
        super().__init__(parent_widget, settings=settings)
        
        # Define settings object and methods
        self._stt = settings
        self.getv = self._stt.get_setting_value
        self.setv = self._stt.set_setting_value
        self.getl = self._stt.lang
        self.get_appv = self._stt.app_setting_get_value
        self.set_appv = self._stt.app_setting_set_value

        # Load GUI
        uic.loadUi(self.getv("online_topic_news_file_path"), self)

        # Define variables
        self.name = "news"
        self.topic_info_dict["name"] = self.name
        self.parent_widget = parent_widget
        self.title = self.getl("online_topic_news_title")
        self.topic_info_dict["title"] = self.title
        self.link = None
        self.icon_path = self.getv("online_topic_news_icon_path")
        self.icon_pixmap = QPixmap(self.icon_path)

        self.settings: dict = self._get_user_settings()

        self.data: NewsData = None
        self.source_obj: AbstractNewsSource = None
        self.active_category = None
        self.active_page = None
        self.page_content_images = []
        self.page_content_videos = []
        self.page_tags = []
        self.page_related = []
        self.page_content_audios = []
        self.page_content_tables = []

        self._define_widgets()
        self._set_cursor_pointing_hand()
        self._set_source(self.settings["news_source"], update_topic=False)

        # Connect events with slots
        self.frm_mondo.mousePressEvent = self.frm_mondo_mouse_click
        self.frm_rts.mousePressEvent = self.frm_rts_mouse_click
        self.frm_sputnik.mousePressEvent = self.frm_sputnik_mouse_click
        
        self.lst_cat.currentItemChanged.connect(self.lst_cat_current_item_changed)
        self.lst_subcat.currentItemChanged.connect(self.lst_subcat_current_item_changed)

        self.txt_search.textChanged.connect(self.txt_search_text_changed)
        self.txt_search.returnPressed.connect(self.btn_search_click)
        self.btn_search.clicked.connect(self.btn_search_click)

        self.lbl_content_pic_open_in_browser.mousePressEvent = self.lbl_content_pic_open_in_browser_click
        self.frm_content_images.mousePressEvent = self.frm_content_images_click

        self.lbl_content_1.linkActivated.connect(self._page_link_activatet_from_content)
        self.lbl_content_2.linkActivated.connect(self._page_link_activatet_from_content)

        self.lbl_top.mousePressEvent = self.lbl_top_click
        self.lbl_prev.mousePressEvent = self.lbl_prev_click
        self.lbl_next.mousePressEvent = self.lbl_next_click

        UTILS.LogHandler.add_log_record("#1: Topic frame loaded.", ["News"])

    def btn_search_click(self):
        if not self.source_obj or not self.source_obj.search_available:
            return
        
        search_text = self.txt_search.text().strip()
        if not search_text:
            return
        
        search_string = self._clean_search_string(search_string=search_text)
        search_string = self.source_obj.search_available + search_string

        self.active_page = search_string
        result = self.update_topic(load_categories=False, load_headlines=False, load_page=True)
        if result is False:
            self.update_topic(load_categories=False, load_headlines=search_string, load_page=False)

    def txt_search_text_changed(self):
        if self.txt_search.text().strip():
            self.btn_search.setEnabled(True)
        else:
            self.btn_search.setDisabled(True)

    def lbl_top_click(self, e: QMouseEvent):
        if e.button() != Qt.LeftButton:
            return
        self.parent_widget.area_content.verticalScrollBar().setValue(0)

    def lbl_prev_click(self, e: QMouseEvent):
        if e.button() != Qt.LeftButton:
            return
        page = self.data.get_prev_page()
        if page:
            self.active_page = page
            self._set_navigation_visible_status()
            self.update_topic(load_categories=False, load_headlines=False, load_page=True, navigation_click=True)

    def lbl_next_click(self, e: QMouseEvent):
        if e.button() != Qt.LeftButton:
            return
        page = self.data.get_next_page()
        if page:
            self.active_page = page
            self._set_navigation_visible_status()
            self.update_topic(load_categories=False, load_headlines=False, load_page=True, navigation_click=True)

    def _page_link_activatet_from_content(self, url: str):
        self.active_page = self._fix_page_url(url)
        result = self.update_topic(load_categories=False, load_headlines=False, load_page=True)
        if result is False:
            self.update_topic(load_categories=False, load_headlines=url, load_page=False)

    def frm_content_images_click(self, e: QMouseEvent):
        self.show_image_slide()

    def lbl_content_pic_open_in_browser_click(self, e: QMouseEvent):
        if self.data and e.button() == Qt.LeftButton:
            if self.data.active_page:
                page = self.data.get_page(self.data.active_page)
                site = page["url"]
                webbrowser.open_new_tab(site)
        QLabel.mousePressEvent(self.lbl_content_pic_open_in_browser, e)

    def _get_source_object(self, source: str = None) -> AbstractNewsSource:
        if source is None:
            source = self.settings["news_source"]

        src_objects = [
            ["mondo", NewsMondo],
            ["rts", NewsRTS],
            ["sputnik", NewsSputnik],
            ["test", NewsTEST]
        ]
        for item in src_objects:
            if source == item[0]:
                return item[1]
        else:
            return None

    def lst_subcat_current_item_changed(self):
        if self.lst_subcat.currentItem() is None:
            return

        item_id = self.lst_subcat.itemWidget(self.lst_subcat.currentItem()).item_id
        self._set_active_category_item(item_id, self.lst_subcat)
    
    def lst_cat_current_item_changed(self):
        if self.lst_cat.currentItem() is None:
            return
        
        item_id = self.lst_cat.itemWidget(self.lst_cat.currentItem()).item_id
        self._set_active_category_item(item_id, self.lst_cat)
        self._populate_subcategories(item_id)

    def frm_mondo_mouse_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._set_source("mondo")

    def frm_rts_mouse_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._set_source("rts")

    def frm_sputnik_mouse_click(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._set_source("sputnik")

    def _set_source(self, source: str, update_topic: bool = True, force_set_object: bool = False):
        if self.settings["news_source"] != source or force_set_object:
            self.settings["news_source"] = source
            self._update_user_settings()
            self.data = NewsData()
            source_obj = self._get_source_object(source)
            if source_obj:
                self.source_obj = source_obj(self.parent_widget, self._stt, self.data)
                if self.source_obj.search_available:
                    self.frm_search.setVisible(True)
                else:
                    self.frm_search.setVisible(False)
            else:
                self.source_obj = None
            self.frm_content.setVisible(False)
            self.area_headlines.setVisible(False)
            self._set_navigation_visible_status()
            if update_topic:
                self.update_topic()

        self._colorize_source_selection()

    def _colorize_source_selection(self):
        stylesheet = "QFrame {color: rgb(0, 255, 0); background-color: rgba(255, 255, 255, 0);} QFrame::hover {background-color: rgb(85, 170, 255);}"
        
        if self.settings["news_source"] == "mondo":
            self.frm_mondo.setStyleSheet("background-color: #00004f;")
        else:
            self.frm_mondo.setStyleSheet(stylesheet)
        
        if self.settings["news_source"] == "rts":
            self.frm_rts.setStyleSheet("background-color: #00004f;")
        else:
            self.frm_rts.setStyleSheet(stylesheet)

        if self.settings["news_source"] == "sputnik":
            self.frm_sputnik.setStyleSheet("background-color: #00004f;")
        else:
            self.frm_sputnik.setStyleSheet(stylesheet)

    def _enable_all_controls(self, value: bool = True):
        self.setEnabled(value)
        return

    def category_item_clicked(self, item: CategoryItem):
        if isinstance(item, str):
            self.active_category = item
        elif isinstance(item, CategoryItem):
            self.active_category = item.item_id
        
        self.update_topic(load_categories=False, load_headlines=True, load_page=False)
    
    def load_topic(self):
        self._set_source(self.settings["news_source"], update_topic=False, force_set_object=True)
        self.update_topic()
        UTILS.LogHandler.add_log_record("#1: Topic loaded.", ["News"])
        return super().load_topic() 

    def update_topic(self, load_categories: bool = True, load_headlines: bool = True, load_page: bool = True, navigation_click: bool = False) -> bool:
        UTILS.LogHandler.add_log_record("#1: About to update topic.", ["News"])
        QCoreApplication.processEvents()
        self.resize_me()
        QCoreApplication.processEvents()

        no_errors = True

        if self.data is None or self.source_obj is None:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = ""
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            self.prg_event.setVisible(False)
            self._enable_all_controls(True)
            UTILS.LogHandler.add_log_record("#1: Updating canceled.", ["News"])
            return

        self.topic_info_dict["working"] = True
        self.topic_info_dict["msg"] = self.getl("topic_msg_news") + ", " + self.getl("topic_msg_dowloading")
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False

        self.prg_event.setVisible(True)
        self.prg_event.setValue(0)
        self._enable_all_controls(False)
        QCoreApplication.processEvents()

        # Load categories and sub categories
        if load_categories and no_errors:
            no_errors = self._load_categories()

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            self.prg_event.setVisible(False)
            self._enable_all_controls(True)
            UTILS.LogHandler.add_log_record("#1: Updating canceled.", ["News"])
            return

        # Load headlines for selected category
        if load_headlines and no_errors:
            no_errors = self._load_headlines(headline_url=load_headlines)

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            self.prg_event.setVisible(False)
            self._enable_all_controls(True)
            UTILS.LogHandler.add_log_record("#1: Updating canceled.", ["News"])
            return

        # Load selected news page
        if load_page and no_errors:
            no_errors = self._load_page(navigation_click)
            self._set_navigation_visible_status()
        
        self.prg_event.setVisible(False)
        self._enable_all_controls(True)

        if self.stop_loading:
            self.topic_info_dict["working"] = False
            self.topic_info_dict["msg"] = self.getl("topic_msg_interrupted_by_user")
            self.signal_topic_info_emit(self.name, self.topic_info_dict)
            self.stop_loading = False
            self.prg_event.setVisible(False)
            UTILS.LogHandler.add_log_record("#1: Updating canceled.", ["News"])
            return 

        self.topic_info_dict["working"] = False
        self.topic_info_dict["msg"] = ""
        self.signal_topic_info_emit(self.name, self.topic_info_dict)
        self.stop_loading = False
        UTILS.LogHandler.add_log_record("#1: Updating completed.", ["News"])
        return no_errors

    def _load_categories(self) -> bool:
        self.active_category = None
        result = self.source_obj.load_categories()
        if not result:
            return False
        
        if self.data.categories:
            result = self._populate_main_categories()
        else:
            return False
        
        if not result:
            return False

    def _populate_main_categories(self):
        self.lst_cat.clear()
        cat_height = 60
        self.lst_cat.resize(self.lst_cat.width(), cat_height)
        active_item = None
        for cat in self.data.categories:
            if not active_item:
                active_item = cat
            item_widget = CategoryItem(self.lst_cat, 
                                       self._stt,
                                       name=self.data.categories[cat]["name"],
                                       title=self.data.categories[cat]["title"],
                                       item_id=cat,
                                       url=self.data.categories[cat]["url"],
                                       item_type=1,
                                       click_function=self.category_item_clicked)
            
            item = QListWidgetItem()
            item.setData(Qt.UserRole, cat)
            item.setSizeHint(item_widget.size())
            self.lst_cat.addItem(item)
            self.lst_cat.setItemWidget(item, item_widget)
        
        if active_item:
            self._set_active_category_item(active_item, self.lst_cat)
            self.category_item_clicked(active_item)
        if self.lst_cat.horizontalScrollBar().isVisible() and self.lst_cat.verticalScrollBar().isVisible():
            self.lst_cat.resize(self.lst_cat.width(), cat_height + self.lst_cat.horizontalScrollBar().height())
        else:
            self.lst_cat.resize(self.lst_cat.width(), cat_height)
        self.resize_me()
            
        return True

    def _populate_subcategories(self, item_id: str) -> bool:
        if item_id not in self.data.categories:
            return False

        self.lst_subcat.clear()
        sub_cat_height = 40
        self.lst_subcat.resize(self.lst_subcat.width(), sub_cat_height)
        
        subcats = self.data.categories[item_id]["sub"]
        for cat in subcats:
            item_widget = CategoryItem(self.lst_subcat,
                                       self._stt,
                                       name=subcats[cat]["name"],
                                       title=subcats[cat]["title"],
                                       item_id=f"{item_id},{cat}",
                                       url=subcats[cat]["url"],
                                       item_type=2,
                                       click_function=self.category_item_clicked)
            
            item = QListWidgetItem()
            item.setData(Qt.UserRole, f"{item_id},{cat}")
            item.setSizeHint(item_widget.size())
            self.lst_subcat.addItem(item)
            self.lst_subcat.setItemWidget(item, item_widget)
        
        if self.lst_subcat.count():
            self.lst_subcat.setVisible(True)
        else:
            self.lst_subcat.setVisible(False)
        if self.lst_subcat.horizontalScrollBar().isVisible() and self.lst_subcat.verticalScrollBar().isVisible():
            self.lst_subcat.resize(self.lst_subcat.width(), sub_cat_height + self.lst_subcat.horizontalScrollBar().height())
        else:
            self.lst_subcat.resize(self.lst_subcat.width(), sub_cat_height)
        self.resize_me()

    def _set_active_category_item(self, item_id: str, list_obj: QListWidget):
        for i in range(list_obj.count()):
            item = list_obj.item(i)
            widget = list_obj.itemWidget(item)
            if widget.item_id == item_id:
                widget.set_active(True)
                list_obj.setCurrentItem(item)

            else:
                widget.set_active(False)

    def _load_headlines(self, add_to_list: bool = False, headline_url: str = None):
        if not self.data or not self.active_category:
            return False
        
        if not self.data.get_category_url(self.active_category):
            return False
        
        if isinstance(headline_url, str):
            self.data.active_headline_url = headline_url
        else:
            if self.data.get_category_url(self.active_category) == self.data.active_headline_url:
                return True
            self.data.active_headline_url = self.data.get_category_url(self.active_category)

        if not add_to_list:
            self.data.headlines = {}
        
        old_subcategory_count = len(self.data.categories[self.active_category.split(",")[0]]["sub"])
        result = self.source_obj.load_headlines()
        if len(self.data.categories[self.active_category.split(",")[0]]["sub"]) != old_subcategory_count:
            self._populate_subcategories(self.active_category)

        if not result:
            return False
        
        self.area_widget = QWidget()
        self.area_widget_layout = QVBoxLayout()
        self.area_widget.setLayout(self.area_widget_layout)
        self.area_headlines.setWidget(self.area_widget)
        spacer = QSpacerItem(20, 4, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.area_widget_layout.addItem(spacer)
        self.area_headlines.setVisible(True)

        headlines = self.data.headlines
        count = 0
        for headline in headlines:
            item_widget = HeadlineItem(
                self.area_headlines,
                self._stt,
                headline,
                headlines[headline]["image"],
                headlines[headline]["text"],
                headlines[headline]["desc"],
                headlines[headline]["title"],
                headlines[headline]["link"],
                headlines[headline]["category"],
                headlines[headline]["time"],
                headlines[headline]["date"],
                self.headline_click_function
            )
            self.set_image_to_label(headlines[headline]["image"], item_widget.lbl_pic)

            self.area_widget_layout.insertWidget(self.area_widget_layout.count() - 1, item_widget)

            count += 1
            progress = int(count / len(headlines) * 100)
            self.prg_event.setValue(progress)
            QCoreApplication.processEvents()
            
            if self.stop_loading:
                return False

        return True

    def headline_click_function(self, item: HeadlineItem):
        if item.url:
            self.active_page = self._fix_page_url(item.url)
            self.update_topic(load_categories=False, load_headlines=False, load_page=True)

    def _fix_page_url(self, url: str) -> str:
        if not url:
            return url
        if url.startswith("//"):
            url = "https:" + url
            return url
        if url.startswith("/"):
            if self.source_obj:
                url = self.source_obj.base_site_url + url
                return url
        return url

    def _load_page(self, navigation_click: bool):
        if not self.data or self.active_page is None:
            return False
        
        if not self.active_page:
            if self.data.active_page:
                self.active_page = self.data.active_page
            return True
                
        self.active_page = self._fix_page_url(self.active_page)
        if self.active_page == self.data.active_page:
            return True
        
        old_page = self.data.active_page
        self.data.set_active_page(self.active_page, navigation_click=navigation_click)

        result = self.source_obj.load_page()
        if not result:
            self.data.failed_to_load(self.active_page)
            if old_page:
                self.data.set_active_page(old_page, navigation_click=navigation_click)
            return False
        
        QCoreApplication.processEvents()
        if self.stop_loading:
            return False

        self.frm_content.setVisible(True)
        result = self._populate_page_content()
        return result

    def _populate_page_content(self) -> bool:
        page = self.data.get_page(self.data.active_page)
        if not page:
            return False
        
        self._page_hide_all_widgets()
        # Main image
        if not page["main_image"] and self.source_obj.base_default_image_path:
            page["main_image"] = self.source_obj.base_default_image_path
        if page["main_image"]:
            self.lbl_content_pic.setVisible(True)
            self.lbl_content_pic_headline.setVisible(True)
            self.lbl_content_pic_open_in_browser.setVisible(True)
            self.lbl_content_pic_time.setVisible(True)

            # Main image set
            self.lbl_content_pic.resize(400, 400)
            self.set_image_to_label(page["main_image"], self.lbl_content_pic, resize_label=True)
            # Page title
            self.lbl_content_pic_headline.setFixedWidth(self.lbl_content_pic.width())
            self.lbl_content_pic_headline.setText(page["title"])
            self.lbl_content_pic_headline.adjustSize()
            h = self.lbl_content_pic.pos().y() + self.lbl_content_pic.height() - self.lbl_content_pic_headline.height() - 5
            if h < 0:
                h = 0
            self.lbl_content_pic_headline.move(self.lbl_content_pic.pos().x(), h)
            # Page open in browser
            self.lbl_content_pic_open_in_browser.move(self.lbl_content_pic.pos().x() + 5, self.lbl_content_pic.pos().y() + 5)
            text_to_html = utility_cls.TextToHTML(self.getl("online_source_news_lbl_open_in_browser_tt") + "\n#1")
            http_rule = utility_cls.TextToHtmlRule(text="#1", replace_with=page["url"], fg_color="#aaffff", font_underline=True)
            text_to_html.add_rule(http_rule)
            self.lbl_content_pic_open_in_browser.setToolTip(text_to_html.get_html())
            # Page time
            self.lbl_content_pic_time.setText(" " + page["date"])
            self.lbl_content_pic_time.adjustSize()
            w = self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() - self.lbl_content_pic_time.width() - 5
            if w < 0:
                w = 0
            self.lbl_content_pic_time.move(w, self.lbl_content_pic.pos().y() + 5)

        w_from_pic_to_edge = self.frm_content.width() - self.lbl_content_pic.pos().x() - self.lbl_content_pic.width() - 10
        content1_x = self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() + 10
        if w_from_pic_to_edge < self.MIN_PAGE_SIDE_TEXT_WIDTH:
            w_from_pic_to_edge = None
        # Lead text
        if page["lead"] and w_from_pic_to_edge:
            self.lbl_lead.setVisible(True)
            self.lbl_lead.setFixedWidth(w_from_pic_to_edge)
            self.lbl_lead.setText(page["lead"])
            self.lbl_lead.adjustSize()
            self.lbl_lead.move(content1_x, self.lbl_content_pic.pos().y())
        # Set Audio Frame
        self._page_set_audio_frame(page)
        # Set tags
        self._page_set_tags(page)
        # Text
        self._page_set_text_contents(page)
        # Tables
        self._page_set_tables(page)
        # Video
        self._page_set_video_frame(page)
        # Images
        self._page_set_images_frame(page)
        if self.stop_loading:
            self._page_get_next_y()
            self.resize_me()
            return False
        # Related content
        self._page_set_related_content(page)


        
        self._page_get_next_y()
        self.resize_me()

    def btn_tag_open_link(self, url: str):
        self.active_page = self._fix_page_url(url)
        result = self.update_topic(load_categories=False, load_headlines=False, load_page=True)
        if result is False:
            self.update_topic(load_categories=False, load_headlines=url, load_page=False)

    def _page_set_tables(self, page: dict) -> bool:
        if not page["tables"]:
            return True
        
        # Delete old tables
        for table in self.page_content_tables:
            table.deleteLater()
        self.page_content_tables = []

        # Add new tables
        y = 0
        w = 0
        for table_data in page["tables"]:
            table: QTableWidget = self.html_parser.get_PYQT5_table_widget(table_object=table_data, parent_widget=self.frm_content_tables)
            if not table:
                return False
            table.move(0, y)
            table.show()
            self.page_content_tables.append(table)
            y += table.height() + 10
            w = max(w, table.width())
            self.frm_content_tables.resize(w, y)

        self.frm_content_tables.setVisible(True)

        return True        

    def _page_set_tags(self, page: dict) -> bool:
        if not page["tags"]:
            return True

        # Delete old tags
        for tag in self.page_tags:
            tag: QPushButton
            tag.setVisible(False)
            tag.clicked.disconnect()
            tag.deleteLater()
        self.page_tags = []
        QCoreApplication.processEvents()

        # Add new tags
        y = 0
        h = self.lbl_content_pic.height()
        if self.lbl_lead.isVisible():
            h = self.lbl_content_pic.height() - self.lbl_lead.height()
            y = self.lbl_lead.pos().y() + self.lbl_lead.height()
        if self.frm_content_audio.isVisible():
            h = self.lbl_content_pic.height() - (self.frm_content_audio.pos().y() + self.frm_content_audio.height())
            y = self.frm_content_audio.pos().y() + self.frm_content_audio.height()

        x = self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() + 10
        w = self.frm_content.width() - x

        tag_w = 0
        fm = QFontMetrics(self.PAGE_TAG_FONT)
        for tag in page["tags"]:
            tag_w = max(tag_w, fm.width(tag[0]))
        tag_w += 30

        if tag_w > w:
            return True

        self.frm_content_tags.setFixedWidth(w)
        self.frm_content_tags.move(x, y)
        self.frm_content_tags.setVisible(True)

        for tag in page["tags"]:
            btn = QPushButton(self.frm_content_tags)
            name = tag[0]
            link = tag[1]
            btn.setText(name)
            btn.setObjectName(link)
            btn.resize(fm.width(name) + 30, fm.height() + 10)
            btn.setFont(self.PAGE_TAG_FONT)
            btn.clicked.connect(lambda state, link=link: self.btn_tag_open_link(link))
            btn.setStyleSheet("QPushButton {color: #aaffff; background-color: #00002d; border:none; border-radius: 10px;} QPushButton::hover {background-color: #000064;}")
            self.page_tags.append(btn)
            btn.show()
        
        # Set Tags position
        tag_line_y = 5
        tag_line_w = 0
        tag_buffer = []
        for tag in self.page_tags:
            tag_line_w += tag.width() + 10
            tag_buffer.append(tag)
            if tag_line_w > w:
                tag_buffer.pop(-1)
                curr_tags_w = 0
                for i in tag_buffer:
                    curr_tags_w += i.width() + 10
                curr_tags_w -= 10
                x = int((w - curr_tags_w) / 2)
                x_for_tag = x
                for i in tag_buffer:
                    i.move(x_for_tag, tag_line_y)
                    x_for_tag += i.width() + 10
                tag_line_y += fm.height() + 20
                tag_buffer = []
                tag_buffer.append(tag)
                tag_line_w = tag.width() + 10
        if tag_buffer:
            curr_tags_w = 0
            for i in tag_buffer:
                curr_tags_w += i.width() + 10
            curr_tags_w -= 10
            x = int((w - curr_tags_w) / 2)
            x_for_tag = x
            for i in tag_buffer:
                i.move(x_for_tag, tag_line_y)
                x_for_tag += i.width() + 10
            tag_line_y += fm.height() + 20

        self.frm_content_tags.resize(self.frm_content_tags.width(), min(tag_line_y, h))
        return True

    def _page_set_related_content(self, page: dict) -> bool:
        related = page["related"]
        if not related:
            return True
        
        # Delete old related
        for item in self.page_related:
            item: QFrame
            item.setVisible(False)
            item.deleteLater()
        self.page_related = []
        QCoreApplication.processEvents()
        
        # Set new related content
        self.frm_content_related.move(0, self._page_get_next_y())
        self.frm_content_related.setVisible(True)
        y = 35
        self.frm_content_related.resize(self.frm_content.width(), y)

        count = 0
        for topic_key in related:
            topic = related[topic_key]
            topic: dict
            item = PageRelatedItem(
                parent_widget=self.frm_content_related,
                settings=self._stt,
                item_index=count,
                item_url=topic["url"],
                item_text=topic["title"],
                item_image=topic["image"],
                item_category=topic["category"],
                item_date=topic["time"]
            )
            self.set_image_to_label(item.item_image, item.lbl_pic, resize_label_fixed_h=True)
            item.arange_widgets()
            item.move(0, y)
            item.mousePressEvent = lambda event, link=item.item_url: self._page_related_content_click(event, link)
            y += item.height() + 5
            self.frm_content_related.resize(self.frm_content_related.width(), y)
            item.show()
            self.page_related.append(item)
            count += 1
        
        return True

    def _page_related_content_click(self, e:QMouseEvent, url: str):
        if not e.button() == Qt.LeftButton:
            return
        self.active_page = self._fix_page_url(url)
        result = self.update_topic(load_categories=False, load_headlines=False, load_page=True)
        if result is False:
            self.update_topic(load_categories=False, load_headlines=url, load_page=False)
    
    def _page_set_video_frame(self, page: dict) -> bool:
        self.frm_content_video.move(0, self._page_get_next_y())
        videos = page["videos"]

        # Delete old videos
        while len(self.page_content_videos) > 0:
            self.page_content_videos[0].deleteLater()
            self.page_content_videos.pop(0)

        # Set new videos in QFrame
        if not videos:
            return True

        # Show frame
        self.frm_content_video.setFixedWidth(self.frm_content.width())
        self.frm_content_video.setVisible(True)
        QCoreApplication.processEvents()

        y = 0
        has_warrning = False
        for video in videos:
            video_url: QUrl = QUrl(video[0])
            web_widget = QWebEngineView(self.frm_content_video)
            if video[0].startswith("http"):
                web_widget.setUrl(video_url)
            else:
                web_widget.setHtml(video[0])
            web_widget.move(0, y)
            web_widget.adjustSize()
            w = self.frm_content_video.width()
            if video[0].find("youtube") != -1 or video[1] == "odysee-iframe":
                web_widget_h = min(int(w * 0.6), 500)
            else:
                web_widget_h = w
            if not video[0].startswith("http"):
                if has_warrning:
                    continue
                has_warrning = True
                web_widget = QLabel(self.frm_content_video)
                web_widget.setText(video[0])
                web_widget.setStyleSheet("QLabel {background-color: #aa0000; color: #ffffff;} QLabel:hover {background-color: #d10000;}")
                web_widget.setAlignment(Qt.AlignCenter)
                web_widget.linkActivated.connect(self._open_link_in_browser)
                web_widget_h = 80
            web_widget.resize(w, web_widget_h)
            y += web_widget_h + 10
            self.page_content_videos.append(web_widget)
            self.frm_content_video.resize(self.frm_content_video.width(), y)
            web_widget.show()
            QCoreApplication.processEvents()
        
        return True

    def _open_link_in_browser(self, url):
        webbrowser.open_new_tab(url)

    def _page_hide_all_widgets(self):
        self.lbl_content_pic.setVisible(False)
        self.lbl_content_pic_headline.setVisible(False)
        self.lbl_content_pic_open_in_browser.setVisible(False)
        self.lbl_content_pic_time.setVisible(False)
        self.lbl_lead.setVisible(False)
        self.frm_content_audio.setVisible(False)
        self.lbl_content_1.setVisible(False)
        self.lbl_content_2.setVisible(False)
        self.frm_content_images.setVisible(False)
        self.frm_content_video.setVisible(False)
        self.frm_content_tags.setVisible(False)
        self.frm_content_related.setVisible(False)
        self.frm_content_tables.setVisible(False)

    def _page_set_audio_frame(self, page: dict):
        audios = page["audios"]
        if not audios:
            return True
        
        y = 0
        if self.lbl_lead.isVisible():
            y = self.lbl_lead.pos().y() + self.lbl_lead.height() + 10
        
        self.frm_content_audio.move(self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() + 10, y)
        w = self.frm_content.width() - (self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() + 10)
        if w < 220:
            w = 220
        self.frm_content_audio.resize(w, 100)
        self.frm_content_audio.setVisible(True)
        # Delete old audios
        while len(self.page_content_audios) > 0:
            self.page_content_audios[0].stop()
            self.page_content_audios[0].deleteLater()
            self.page_content_audios.pop(0)
        
        # Set new audios
        player_y = 0
        for audio in audios:
            player = MediaPlayer(self.frm_content_audio, audio)
            player.move(0, player_y)
            player.resize(w, 100)
            player_y += 110

            self.frm_content_audio.resize(w, player_y)
            player.show()
            
            self.page_content_audios.append(player)
        
        return True

    def _page_get_next_y(self) -> int:
        y = 0
        if self.lbl_content_pic.isVisible():
            y = self.lbl_content_pic.pos().y() + self.lbl_content_pic.height()
        if self.lbl_lead.isVisible():
            y = max(self.lbl_lead.pos().y() + self.lbl_lead.height(), y)
        if self.frm_content_audio.isVisible():
            y = max(self.frm_content_audio.pos().y() + self.frm_content_audio.height(), y)
        if self.frm_content_tags.isVisible():
            y = max(self.frm_content_tags.pos().y() + self.frm_content_tags.height(), y)
        if self.lbl_content_1.isVisible():
            y = max(self.lbl_content_1.pos().y() + self.lbl_content_1.height(), y)
        if self.lbl_content_2.isVisible():
            y = max(self.lbl_content_2.pos().y() + self.lbl_content_2.height(), y)
        if self.frm_content_tables.isVisible():
            y = max(self.frm_content_tables.pos().y() + self.frm_content_tables.height(), y)
        if self.frm_content_video.isVisible():
            y = max(self.frm_content_video.pos().y() + self.frm_content_video.height(), y)
        if self.frm_content_images.isVisible():
            y = max(self.frm_content_images.pos().y() + self.frm_content_images.height(), y)
        if self.frm_content_related.isVisible():
            y = max(self.frm_content_related.pos().y() + self.frm_content_related.height(), y)

        if y:
            self.frm_content.resize(self.frm_content.width(), y + 5)
        
        return y

    def _page_set_images_frame(self, page: dict):
        self.frm_content_images.move(0, self._page_get_next_y() + 10)
        self.frm_content_images.setFixedWidth(self.frm_content.width())
        if not page["images"]:
            return
        
        # Delete old images
        for i in range(len(self.page_content_images)):
            self.page_content_images[i].setVisible(False)
            self.page_content_images[i].deleteLater()
        self.page_content_images = []

        # Add new images
        self.frm_content_images.setVisible(True)

        y1 = 0
        y2 = 0
        img_w = int(self.frm_content_images.width() / 2) - 5
        
        for idx, img_url in enumerate(page["images"]):
            progress = (idx / len(page["images"])) * 100
            self.prg_event.setValue(int(progress))
            QCoreApplication.processEvents()
            if self.stop_loading:
                return

            lbl_img = QLabel(self.frm_content_images)
            if y1 <= y2:
                lbl_img.move(0, y1)
                lbl_img.resize(img_w, img_w)
                self.set_image_to_label(image_data=img_url, label=lbl_img, resize_label_fixed_w=True)
                self.frm_content_images.resize(self.frm_content_images.width(), y1 + lbl_img.height())
                y1 += lbl_img.height() + 5
                self.page_content_images.append(lbl_img)
            else:
                lbl_img.move(img_w + 10, y2)
                lbl_img.resize(img_w, img_w)
                self.set_image_to_label(image_data=img_url, label=lbl_img, resize_label_fixed_w=True)
                self.frm_content_images.resize(self.frm_content_images.width(), y2 + lbl_img.height())
                y2 += lbl_img.height() + 5
                self.page_content_images.append(lbl_img)
            lbl_img.show()
        
    def _page_set_text_contents(self, page: dict):
        # Tokenize page text
        tokenized_text = []
        for txt_slice in page["text_slices"]:
            txt_slice: html_parser_cls.TextObject
            txt_slice.txt_value = txt_slice.txt_value.replace("\n", "<br>")
            if txt_slice.txt_link or txt_slice.get_tag(["h1", "h2", "h3", "h4", "h5", "h6"]):
                txt_slice.txt_value += " "
                tokenized_text.append(txt_slice)
                continue
            tokenized_slice = txt_slice.tokenize(preferred_token_lenght=10)
            tokenized_text = tokenized_text + tokenized_slice

        w_from_pic_to_edge = self.frm_content.width() - self.lbl_content_pic.pos().x() - self.lbl_content_pic.width() - 10
        if w_from_pic_to_edge < self.MIN_PAGE_SIDE_TEXT_WIDTH:
            w_from_pic_to_edge = None

        text_index = 0
        has_part2 = True
        if w_from_pic_to_edge:
            self.lbl_content_1.setFixedWidth(w_from_pic_to_edge)

            h = self.lbl_content_pic.height()
            y = 0
            if self.lbl_lead.isVisible():
                h = self.lbl_content_pic.height() - self.lbl_lead.height() - 50
                y = self.lbl_lead.pos().y() + self.lbl_lead.height() + 50
            if self.frm_content_audio.isVisible():
                h = self.lbl_content_pic.height() - (self.frm_content_audio.pos().y() + self.frm_content_audio.height())
                y = self.frm_content_audio.pos().y() + self.frm_content_audio.height()
            if self.frm_content_tags.isVisible():
                h = self.lbl_content_pic.height() - (self.frm_content_tags.pos().y() + self.frm_content_tags.height())
                y = self.frm_content_tags.pos().y() + self.frm_content_tags.height()

            if h > 100:
                self.lbl_content_1.setVisible(True)
                self.lbl_content_1.move(self.lbl_content_pic.pos().x() + self.lbl_content_pic.width() + 10, y)
                has_part2 = False
                for text_index, text_slice in enumerate(tokenized_text):
                    result = self._try_to_fit_text(self.lbl_content_1, tokenized_text[0:text_index+1], h)
                    if not result:
                        if text_index > 0:
                            self._try_to_fit_text(self.lbl_content_1, tokenized_text[0:text_index], h)
                            has_part2 = True
                        break
                if text_index == 0:
                    self.lbl_content_1.setVisible(False)

        if not has_part2:
            return

        if "livestream" in self.data.active_page:
            self.lbl_content_1.setVisible(False)
            text_index = 0

        self.lbl_content_2.move(0, self._page_get_next_y())
        self.lbl_content_2.setVisible(True)
        self.lbl_content_2.setFixedWidth(self.frm_content.width())

        self._try_to_fit_text(self.lbl_content_2, tokenized_text[text_index:], 0)

    def _try_to_fit_text(self, label: QLabel, text_slices: list, desired_w: int) -> bool:
        text_to_html = utility_cls.TextToHTML()
        text_to_html.general_rule.fg_color = "#aaff7f"
        text = ""
        fact_tracker = False
        for idx, txt_slice in enumerate(text_slices):
            txt_slice: html_parser_cls.TextObject
            text_id = "#" + "-" * (6 - len(str(idx))) + str(idx) + ";"
            html_rule = utility_cls.TextToHtmlRule(text=text_id, replace_with=txt_slice.txt_value)
            if txt_slice.txt_link:
                html_rule.font_underline = True
                html_rule.fg_color = "#55ffff"
            if txt_slice.txt_strong:
                html_rule.fg_color = "#e2ffcb"
                html_rule.font_bold = True
            if txt_slice.get_tag(["h1", "h2", "h3", "h4", "h5", "h6"]):
                html_rule.fg_color = "#00ff7f"
                html_rule.bg_color = "#424263"
                html_rule.replace_with = "<br><br>" + html_rule.replace_with + "<br>"
                html_rule.font_size = 20
                html_rule.font_bold = True
            is_factbox = txt_slice.get_tag("div")
            if is_factbox:
                if is_factbox.lower().find("factbox") != -1 or is_factbox.lower().find("article__quote-text") != -1:
                    html_rule.fg_color = "#aaaaff"
                    if not fact_tracker:
                        html_rule.replace_with = "<br>" + html_rule.replace_with
                    fact_tracker = True
                else:
                    if fact_tracker :
                        html_rule.replace_with = "<br>" + html_rule.replace_with
                    fact_tracker = False
            else:
                if fact_tracker:
                    html_rule.replace_with = "<br>" + html_rule.replace_with

            if is_factbox.find('article__article-desc') != -1:
                html_rule.replace_with = "<br><br>" + html_rule.replace_with
            if is_factbox.find('article__article-title') != -1:
                html_rule.replace_with = "<br>" + html_rule.replace_with
            if is_factbox.find('article__article-info') != -1:
                html_rule.replace_with = "<br>" + html_rule.replace_with
            if is_factbox.find('online__item-time') != -1:
                html_rule.replace_with = "<br><br>" + html_rule.replace_with + "<br>"
                html_rule.fg_color = "#60c18f"
            
            if txt_slice.get_tag("em"):
                html_rule.font_italic = True
                html_rule.fg_color = "#ffcef9"
            if txt_slice.txt_link:
                html_rule.link_href = txt_slice.txt_link

            text_to_html.add_rule(html_rule)
            text += text_id

        text_to_html.set_text(text)
        label.setText(text_to_html.get_html())
        label.adjustSize()
        if desired_w and label.height() > desired_w:
            return False
        return True

    def _get_user_settings(self) -> dict:
        result = {
            "news_source": None
            }

        if "online_topic_news_settings" in self._stt.app_setting_get_list_of_keys():
            g: dict = self.get_appv("online_topic_news_settings")
            result["news_source"] = g["news_source"]
        
        if result["news_source"] is None:
            result["news_source"] = "mondo"
        return result

    def _update_user_settings(self) -> None:
        if "online_topic_news_settings" not in self._stt.app_setting_get_list_of_keys():
            self._stt.app_setting_add("online_topic_news_settings", self.settings, save_to_file=True)
        else:
            self.set_appv("online_topic_news_settings", self.settings)

    def _set_cursor_pointing_hand(self):
        self.frm_mondo.setCursor(Qt.PointingHandCursor)
        self.frm_rts.setCursor(Qt.PointingHandCursor)
        self.frm_sputnik.setCursor(Qt.PointingHandCursor)

    def area_changed(self, area_object: QScrollArea):
        if self.parent_widget.area_content.widget():
            self.parent_widget.area_content.widget().layout().setStretch(0, 1)
        # Show GoTop Label
        if area_object.verticalScrollBar().value():
            self.lbl_top.setVisible(True)
            # Move Label to bottom of visible area
            x = int((area_object.viewport().width() - self.lbl_top.width()) / 2)
            if x < 0:
                x = 0
            y = area_object.viewport().height() - self.lbl_top.height() + area_object.verticalScrollBar().value()
            if y < 0:
                y = 0
            self.lbl_top.move(x, y)
            x -= int(self.lbl_top.width()/2)
            if x < 0:
                x = 0
            self.lbl_prev.move(x, y)
            x = int((area_object.viewport().width() - self.lbl_top.width()) / 2)
            x += self.lbl_top.width()
            if x < 0:
                x = 0
            self.lbl_next.move(x, y)
            self._set_navigation_visible_status()
        else:
            self.lbl_top.setVisible(False)
            self.lbl_prev.setVisible(False)
            self.lbl_next.setVisible(False)
        return super().area_changed(area_object)

    def _set_navigation_visible_status(self):
        if self.data.get_prev_page() is not None:
            self.lbl_prev.setVisible(True)
        else:
            self.lbl_prev.setVisible(False)
        if self.data.get_next_page() is not None:
            self.lbl_next.setVisible(True)
        else:
            self.lbl_next.setVisible(False)

    def close_me(self):
        for item in self.page_content_videos:
            if not isinstance(item, QLabel):
                item.stop()
            QCoreApplication.processEvents()
            item.deleteLater()
        self.page_content_videos = []
        for item in self.page_content_audios:
            item.stop()
            QCoreApplication.processEvents()
            item.deleteLater()
        self.page_content_audios = []

    def resize_me(self, size: QSize = None):
        position = 0
        if self.parent_widget.area_content.verticalScrollBar().isVisible():
            position = self.parent_widget.area_content.verticalScrollBar().value()

        self.lst_cat.resize(self.width(), self.lst_cat.height())
        self.lst_subcat.move(self.lst_subcat.pos().x(), self.lst_cat.pos().y() + self.lst_cat.height())
        self.lst_subcat.resize(self.width(), self.lst_subcat.height())

        if self.lst_subcat.isVisible():
            h = self.lst_subcat.pos().y() + self.lst_subcat.height() + 10
        else:
            h = self.lst_cat.pos().y() + self.lst_cat.height() + 10

        if self.frm_search.isVisible():
            self.frm_search.move(self.area_headlines.pos().x(), h)
            h += self.frm_search.height()

        self.area_headlines.move(self.area_headlines.pos().x(), h)
        self.area_headlines.resize(self.area_headlines.width(), 1200)

        
        self.line_end_headlines.move(self.area_headlines.pos().x(), self.area_headlines.pos().y() + self.area_headlines.height() + 4)
        self.line_end_headlines.resize(self.area_headlines.width(), self.line_end_headlines.height())

        self.frm_content.move(self.area_headlines.pos().x() + self.area_headlines.width() + 10, h)
        if self.parent_widget.area_content.verticalScrollBar().isVisible():
            shrink_content = 0
        else:
            shrink_content = self.parent_widget.area_content.verticalScrollBar().width()
        self.frm_content.resize(self.width() - self.frm_content.pos().x() - 10 - shrink_content, self.frm_content.height())

        size_h = size.height() if size else 0
        size_content = self.frm_content.pos().y() + self.frm_content.height() + 10
        self.setFixedHeight(max(h + self.area_headlines.height() + 10, size_h, size_content))

        self.parent_widget.area_content.verticalScrollBar().setValue(position)

        return super().resize_me(size)

    def _define_widgets(self):
        # Mondo Item
        self.frm_mondo: QFrame = self.findChild(QFrame, "frm_mondo")
        self.lbl_mondo_pic: QLabel = self.findChild(QLabel, "lbl_mondo_pic")
        self.lbl_mondo_txt: QLabel = self.findChild(QLabel, "lbl_mondo_txt")
        # RTS Item
        self.frm_rts: QFrame = self.findChild(QFrame, "frm_rts")
        self.lbl_rts_pic: QLabel = self.findChild(QLabel, "lbl_rts_pic")
        self.lbl_rts_txt: QLabel = self.findChild(QLabel, "lbl_rts_txt")
        # Sputnik Item
        self.frm_sputnik: QFrame = self.findChild(QFrame, "frm_sputnik")
        self.lbl_sputnik_pic: QLabel = self.findChild(QLabel, "lbl_sputnik_pic")
        self.lbl_sputnik_txt: QLabel = self.findChild(QLabel, "lbl_sputnik_txt")
        # Progress Bar
        self.prg_event: QProgressBar = self.findChild(QProgressBar, "prg_event")
        # Category
        self.lst_cat: QListWidget = self.findChild(QListWidget, "lst_cat")
        self.lst_subcat: QListWidget = self.findChild(QListWidget, "lst_subcat")
        # Search
        self.frm_search: QFrame = self.findChild(QFrame, "frm_search")
        self.txt_search: QLineEdit = self.findChild(QLineEdit, "txt_search")
        self.btn_search: QPushButton = self.findChild(QPushButton, "btn_search")
        # Headlines list
        self.area_headlines: QScrollArea = self.findChild(QScrollArea, "area_headlines")
        self.line_end_headlines: QFrame = self.findChild(QFrame, "line_end_headlines")
        # Content
        self.frm_content: QFrame = self.findChild(QFrame, "frm_content")
        self.lbl_content_pic: QLabel = self.findChild(QLabel, "lbl_content_pic")
        self.lbl_content_pic_headline: QLabel = self.findChild(QLabel, "lbl_content_pic_headline")
        self.lbl_content_pic_open_in_browser: QLabel = self.findChild(QLabel, "lbl_content_pic_open_in_browser")
        self.lbl_content_pic_time: QLabel = self.findChild(QLabel, "lbl_content_pic_time")
        self.lbl_content_1: QLabel = self.findChild(QLabel, "lbl_content_1")
        self.lbl_content_2: QLabel = self.findChild(QLabel, "lbl_content_2")
        self.lbl_lead: QLabel = self.findChild(QLabel, "lbl_lead")
        self.frm_content_audio: QFrame = self.findChild(QFrame, "frm_content_audio")
        self.frm_content_images: QFrame = self.findChild(QFrame, "frm_content_images")
        self.frm_content_video: QFrame = self.findChild(QFrame, "frm_content_video")
        self.frm_content_tags: QFrame = self.findChild(QFrame, "frm_content_tags")
        self.frm_content_related: QFrame = self.findChild(QFrame, "frm_content_related")
        self.lbl_content_related_title: QLabel = self.findChild(QLabel, "lbl_content_related_title")
        self.frm_content_tables: QFrame = self.findChild(QFrame, "frm_content_tables")
        # Go Top Prev Next
        self.lbl_top: QLabel = self.findChild(QLabel, "lbl_top")
        self.lbl_prev: QLabel = self.findChild(QLabel, "lbl_prev")
        self.lbl_next: QLabel = self.findChild(QLabel, "lbl_next")

        self._setup_widget_apperance()

    def _setup_widget_apperance(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.lbl_top.setVisible(False)
        self.lbl_top.setToolTip(self.getl("online_news_mondo_lbl_top_tt"))
        self.lbl_prev.setVisible(False)
        self.lbl_prev.setToolTip(self.getl("online_news_mondo_lbl_prev_tt"))
        self.lbl_next.setVisible(False)
        self.lbl_next.setToolTip(self.getl("online_news_mondo_lbl_next_tt"))

        self.txt_search.setPlaceholderText(self.getl("online_news_txt_search_placeholder_text"))
        self.btn_search.setText(self.getl("online_news_btn_search_text"))
        self.btn_search.setToolTip(self.getl("online_news_btn_search_tt"))
        self.frm_search.setVisible(False)
        self.btn_search.setDisabled(True)
        
        self.area_widget = QWidget()
        self.area_widget_layout = QVBoxLayout()
        self.area_widget.setLayout(self.area_widget_layout)
        self.area_headlines.setWidget(self.area_widget)
        self.area_headlines.ensureVisible(0, 0, Qt.AlignLeft)
        
        self.lst_subcat.setVisible(False)
        self.frm_content.setVisible(False)
        self.prg_event.setVisible(False)

        self.lbl_content_pic_open_in_browser.setText(self.getl("online_source_news_lbl_open_in_browser_text") + " ")
        self.lbl_content_pic_open_in_browser.setToolTip(self.getl("online_source_news_lbl_open_in_browser_tt"))
        self.lbl_content_pic_open_in_browser.adjustSize()

        self.lbl_lead.setFont(self.PAGE_TEXT_FONT)
        self.lbl_content_pic_open_in_browser.setCursor(Qt.PointingHandCursor)
        self.frm_content_images.setCursor(Qt.PointingHandCursor)
        self.lbl_content_related_title.resize(400, 30)
        self.lbl_content_related_title.setText(self.getl("online_news_page_related_title_text"))
        self.lbl_content_related_title.setAlignment(Qt.AlignLeft|Qt.AlignTop)

