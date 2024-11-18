from typing import Union, Any
import urllib.request
import requests
import mimetypes
from urllib.parse import urlparse


from utils_terminal import TerminalUtility


class InternetUtility:

    @staticmethod
    def get_internet_status() -> Union[bool, str]:
        try:
            urllib.request.urlopen('https://www.google.com', timeout=1)
            return True
        except Exception as e:
            return e
    
    @staticmethod
    def get_internet_status_with_request() -> Union[bool, str]:
        try:
            requests.get("https://www.google.com", timeout=1)
            return True
        except requests.ConnectionError as e:
            return e
    
    @staticmethod
    def download_file_from_internet_with_urllib(url: str, file_path: str) -> bool:
        try:
            urllib.request.urlretrieve(url, file_path)
            return True
        except Exception as e:
            TerminalUtility.WarningMessage("Exception in #1\n#2", ["download_file_from_internet_with_urllib", str(e)])
            return False
        
    @staticmethod
    def download_file_from_internet_with_requests(url: str, file_path: str) -> bool:
        try:
            r = requests.get(url, allow_redirects=True)
            open(file_path, 'wb').write(r.content)
            return True
        except Exception as e:
            TerminalUtility.WarningMessage("Exception in #1\n#2", ["download_file_from_internet_with_requests", str(e)])
            return False
        
    @staticmethod
    def get_web_file_name(url: str) -> str:
        parsed_url = urlparse(url)
        file_name = parsed_url.path.split("/")[-1]
        return file_name
    
    @staticmethod
    def get_web_file_extension(url: str) -> str:
        try:
            response = urllib.request.urlopen(url)
            content_type = response.headers['Content-Type']
            file_extension = mimetypes.guess_extension(content_type)
        except Exception as e:
            file_extension = None
        
        return file_extension







