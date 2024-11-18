from typing import Union, Any
import shutil
import os
import hashlib
import zipfile
import json
import time

from utils_datetime import DateTime
from utils_datetime import Period
from utils_datetime import DateTimeObject
from utils_log import LogHandler
from utils_text import TextUtility


class FileInformation:
    def __init__(self, file_path: Union[str, 'FileInformation'] = None):
        if isinstance(file_path, str):
            self._file_path = file_path
        elif isinstance(file_path, FileInformation):
            self._file_path = file_path._file_path
        else:
            LogHandler.add_log_record("#1: Unexpected data type in #2 method for #3\n#3 is set to #4\ntype(file_path) = #5", ["FileInformation", "__init__", "file_path", "None", type(file_path)], warning_raised=True)
            self._file_path = None

    def _fix_file_path(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        if file_path is None:
            file_path = self._file_path
        
        if isinstance(file_path, FileInformation):
            file_path = file_path._file_path

        if file_path is None:
            from utils_log import LogHandler
            LogHandler.add_log_record("#1: File path not specified.\ntype(file_path) = #2\nfile_path = #3", ["FileStatistic", type(file_path), file_path], exception_raised=True)
            raise ValueError("File path not specified!")
        
        if not isinstance(file_path, str):
            from utils_log import LogHandler
            LogHandler.add_log_record("#1: File path must be a string.\ntype(file_path) = #2\nfile_path = #3", ["FileStatistic", type(file_path), file_path], exception_raised=True)
            raise TypeError("File path must be a string!")
        
        if not os.path.exists(file_path):
            from utils_log import LogHandler
            LogHandler.add_log_record("#1: File not found.\ntype(file_path) = #2\nfile_path = #3", ["FileStatistic", type(file_path), file_path])

        if os.path.isdir(file_path):
            if not file_path.endswith("/") and file_path:
                file_path = file_path + "/"

        return file_path

    def is_exist(self, file_path: Union[str, 'FileInformation'] = None) -> bool:
        file_path = self._fix_file_path(file_path)

        if isinstance(file_path, str):
            return os.path.exists(file_path)
        elif isinstance(file_path, FileInformation):
            return file_path.is_exist()

    def is_file(self, file_path: Union[str, 'FileInformation'] = None) -> bool:
        file_path = self._fix_file_path(file_path)
        
        return os.path.isfile(file_path)
    
    def is_directory(self, file_path: Union[str, 'FileInformation'] = None) -> bool:
        file_path = self._fix_file_path(file_path)
        
        return os.path.isdir(file_path)
    
    def is_folder(self, file_path: Union[str, 'FileInformation'] = None) -> bool:
        return self.is_directory(file_path)

    def get_type(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        """
        Returns (string) type of object:
            Types:
                "archive" : ZIP archive object
                "folder" : Object is folder
                "file" : Object is file of unknown type
                "" : Object type cannot be specified
        """
        file_path = self._fix_file_path(file_path)
        
        if self.is_directory(file_path):
            return "folder"
        
        if self.is_zip_archive(file_path):
            return "archive"
        
        if self.is_file(file_path):
            return "file"
        
        return ""

    def is_zip_archive(self, file_path: Union[str, 'FileInformation'] = None) -> bool:
        file_path = self._fix_file_path(file_path)
        
        return zipfile.is_zipfile(os.path.abspath(file_path))

    def absolute_path(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        file_path = self._fix_file_path(file_path)

        return os.path.abspath(file_path)

    def get_base_filename(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        """
        Returns base file name without path to file.
        if object is directory, returns None

        Example
        -------
            file_path = "path/to/your/file.txt"
            returns: file.txt
        """
        file_path = self._fix_file_path(file_path)
        
        if self.is_directory(file_path):
            return None
        
        return os.path.basename(file_path)

    def get_file_content(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        file_path = self._fix_file_path(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            LogHandler.add_log_record("#1: Error in #2\n#3", ["FileStatistic", "get_file_content", e], warning_raised=True)
            return None

    def file_content_count_lines(self, file_path: Union[str, 'FileInformation'] = None) -> int:
        return TextUtility.count_lines(self.get_file_content(file_path))

    def file_content_count_words(self, file_path: Union[str, 'FileInformation'] = None) -> int:
        return TextUtility.count_words(self.get_file_content(file_path))
    
    def file_content_count_chars(self, file_path: Union[str, 'FileInformation'] = None) -> int:
        return TextUtility.count_chars(self.get_file_content(file_path))

    def file_content_count_sentences(self, file_path: Union[str, 'FileInformation'] = None) -> int:
        return TextUtility.count_sentences(self.get_file_content(file_path))

    def file_content_count_expressions(self, file_path: Union[str, 'FileInformation'] = None, expressions: Union[list, str] = None, match_case: bool = False) -> int:
        return TextUtility.count_expressions(self.get_file_content(file_path), expressions, match_case)

    def get_dir_name(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        """
        Returns directory name without base name.

        Example
        -------
            file_path = "path/to/your/file.txt"
            returns: path/to/your/
        """
        file_path = self._fix_file_path(file_path)
        
        result = os.path.dirname(file_path)
        if not result.endswith("/"):
            result = result + "/"

        return result

    def _directory_size(self, folder_path: Union[str, 'FileInformation'], include_subfolders: bool = True) -> int:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path._file_path
        
        if not self.is_directory(folder_path):
            folder_path = self.get_dir_name(folder_path)

        total_size = 0

        if not include_subfolders:
            for filename in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, filename)):
                    total_size += os.path.getsize(os.path.join(folder_path, filename))
            return total_size
        
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    
    def list_files_and_folders(self, file_path: Union[str, 'FileInformation'] = None) -> list:
        file_path = self._fix_file_path(file_path)
        
        if self.is_directory(file_path):
            return os.listdir(file_path)
        
        if self.is_zip_archive(file_path):
            result = []
            with zipfile.ZipFile(file_path, "r") as zip_file:
                for info in zip_file.infolist():
                    result.append(info.filename)
            return result
        
        if self.is_file(file_path):
            return []
        
        return None

    def size(self, file_path: Union[str, 'FileInformation'] = None, return_formatted_string: bool = False) -> Union[int, str]:
        file_path = self._fix_file_path(file_path)

        if self.is_directory(file_path):
            size = self._directory_size(file_path)
            if return_formatted_string:
                return FileInformation.get_size_formatted_string(size)
            
            return size

        file_stat = os.stat(file_path)

        size = file_stat.st_size

        if not return_formatted_string:
            return size
        
        return FileInformation.get_size_formatted_string(size)

    @staticmethod
    def get_size_formatted_string(size: int) -> str:
        txt = f'{size} bytes'
        
        if size > 1024:
            txt = f"{size/1024: .2f} Kb"
        if size > 1024*1024:
            txt = f"{size/1024/1024: .2f} Mb"
        if size > 1024*1024*1024:
            txt = f"{size/1024/1024/1024: .2f} Gb"

        return txt.strip()

    def created_time(self, file_path: Union[str, 'FileInformation'] = None, return_DateTimeObject = False, **kwargs) -> Union[str, DateTimeObject]:
        file_path = self._fix_file_path(file_path)

        if self.is_directory(file_path):
            return None
        
        file_stat = os.stat(file_path)

        creation_time = file_stat.st_ctime
        
        if DateTime.is_valid(creation_time):
            date_obj = DateTime.get_DateTimeObject(creation_time, **kwargs)
            if return_DateTimeObject:
                result = date_obj
            else:
                result = date_obj.DATE_TIME_formatted_string
        else:
            LogHandler.add_log_record("#1: #2 object cannot be created from #3 (#4)", ["FileStatistic", "DateTimeObject", "timestamp", creation_time], warning_raised=True)
            if return_DateTimeObject:
                result = DateTime.now()
            else:
                result = DateTime.now().DATE_TIME_formatted_string
        
        return result

    def created_before_period(self, file_path: Union[str, 'FileInformation'] = None, date: str = None) -> Period:
        file_path = self._fix_file_path(file_path)
        creation_time = self.created_time(file_path, return_DateTimeObject=True)
        if date is None:
            date = DateTime.now()
        
        return date - creation_time

    def modification_time(self, file_path: Union[str, 'FileInformation'] = None, return_DateTimeObject = False, **kwargs) -> Union[str, DateTimeObject]:
        file_path = self._fix_file_path(file_path)

        if self.is_directory(file_path):
            return None
        
        file_stat = os.stat(file_path)

        modification_time = file_stat.st_mtime
        # modification_time = os.path.getmtime(file_path)
        
        if DateTime.is_valid(modification_time):
            date_obj = DateTime.get_DateTimeObject(modification_time, **kwargs)
            if return_DateTimeObject:
                result = date_obj
            else:
                result = date_obj.DATE_TIME_formatted_string
        else:
            LogHandler.add_log_record("#1: #2 object cannot be created from #3 (#4)", ["FileStatistic", "DateTimeObject", "timestamp", modification_time], warning_raised=True)
            if return_DateTimeObject:
                result = DateTime.now()
            else:
                result = DateTime.now().DATE_TIME_formatted_string
        
        return result

    def modified_before_period(self, file_path: Union[str, 'FileInformation'] = None, date: str = None) -> Period:
        file_path = self._fix_file_path(file_path)
        modification_time = self.modification_time(file_path, return_DateTimeObject=True)
        if date is None:
            date = DateTime.now()
        
        return date - modification_time

    def access_time(self, file_path: Union[str, 'FileInformation'] = None, return_DateTimeObject = False, **kwargs) -> Union[str, DateTimeObject]:
        file_path = self._fix_file_path(file_path)

        if self.is_directory(file_path):
            return None
        
        file_stat = os.stat(file_path)

        access_time = file_stat.st_atime
        
        if DateTime.is_valid(access_time):
            date_obj = DateTime.get_DateTimeObject(access_time, **kwargs)
            if return_DateTimeObject:
                result = date_obj
            else:
                result = date_obj.DATE_TIME_formatted_string
        else:
            LogHandler.add_log_record("#1: #2 object cannot be created from #3 (#4)", ["FileStatistic", "DateTimeObject", "timestamp", access_time], warning_raised=True)
            if return_DateTimeObject:
                result = DateTime.now()
            else:
                result = DateTime.now().DATE_TIME_formatted_string
        
        return result

    def accessed_before_period(self, file_path: Union[str, 'FileInformation'] = None, date: str = None) -> Period:
        file_path = self._fix_file_path(file_path)
        access_time = self.access_time(file_path, return_DateTimeObject=True)
        if date is None:
            date = DateTime.now()
        
        return date - access_time

    def extension(self, file_path: Union[str, 'FileInformation'] = None) -> str:
        """
        Returns file extension without leading dot
        """
        file_path = self._fix_file_path(file_path)

        if self.is_directory(file_path):
            return None
        
        return os.path.splitext(file_path)[1].lstrip(".")

    def __str__(self) -> str:
        return f"Filepath: {self._file_path}"

    def __eq__(self, other):
        if isinstance(other, FileInformation):
            return self._file_path == other._file_path
        else:
            return False    

    @property
    def file_path(self) -> str:
        return self._file_path
    
    @file_path.setter
    def file_path(self, value: Union[str, 'FileInformation']) -> None:
        self._file_path = self._fix_file_path(value)


class FileUtility:
    @staticmethod
    def get_FileInformation_object(file_path: Union[str, FileInformation]) -> FileInformation:
        if isinstance(file_path, FileInformation):
            result = file_path
        elif isinstance(file_path, str):
            result = FileInformation(file_path)
        else:
            result = None
            LogHandler.add_log_record("#1: Method: #2, FileInformation object cannot be created. Unexpected data type for #3.\ntype(file_path) = #4\nfile_path = #5", ["FileUtility", "get_FileInformation_object", "file_path", type(file_path), file_path], warning_raised=True)

        return result
    
    @staticmethod
    def show_save_dialog_tkinter(title: str = "Save file", initial_file: str = "", initial_dir: str = "", default_extension: str = "", file_types: list = []) -> str | None:
        """
        Opens a save dialog window using Tkinter library.

        Args:
            title (str): Title of the dialog window. Default is "Save file".
            initial_file (str): Initial file name to be pre-filled in the dialog window. Default is an empty string.
            initial_dir (str): Initial directory to be pre-filled in the dialog window. Default is an empty string.
            default_extension (str): Default file extension to be pre-filled in the dialog window. Default is an empty string.
            file_types (list[tuple]): List of file types to be displayed in the dialog window. Default is an empty list.
                [("Files ZIP", ".zip"), ("Files RAR", ".rar") ...]

        Returns:
            save_path (str): Path of the file selected by the user in the dialog window. If the user cancels the dialog, an empty string is returned.

        Raises:
            Exception: If the Tkinter library is not available.
        """

        from tkinter import filedialog, Tk

        # Create a minimal Tkinter window (can be hidden)
        root = Tk()
        root.withdraw()

        # Open save dialog with pre-filled filename and directory
        save_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            initialfile=initial_file,
            initialdir=initial_dir,
            filetypes=file_types,
            title=title
        )

        return save_path
    
    @staticmethod
    def show_open_file_dialog_tkinter(title: str = "Open File", initial_file: str = "", initial_dir: str = "", file_types: list = [("All Files", "*.*")]) -> str | None:
        """
        Opens a file dialog using Tkinter library.

        Args:
            title (str): Title of the dialog window. Default is "Open File".
            initial_file (str): Initial file path to be pre-filled in the dialog. Default is an empty string.
            initial_dir (str): Initial directory path to be pre-filled in the dialog. Default is an empty string.
            file_types (list): List of file types to be displayed in the dialog. Each element is a tuple containing a description and a file extension. Default is [("All Files", "*.*")]
                [("Files ZIP", ".zip"), ("Files RAR", ".rar") ...]

        Returns:
            str: Path of the selected file. If the user cancels the dialog, an empty string is returned.
        """

        from tkinter import filedialog, Tk

        # Create a minimal Tkinter window (can be hidden)
        root = Tk()
        root.withdraw()

        # Open open dialog with pre-defined filetypes
        open_path = filedialog.askopenfilename(
            title=title,
            initialfile=initial_file,
            initialdir=initial_dir,
            filetypes=file_types
        )

        return open_path

    @staticmethod
    def show_open_file_PyQt5(parent_widget = None, title: str = "Open File", initial_dir: Union[str, FileInformation] = ".", filters: str = None) -> str | None:
        """
        Opens a file selection dialog with specified parameters.

        Args:
            self (QtWidgets.QWidget): The parent widget for the dialog.
            title (str, optional): The title of the dialog window. Defaults to "Open File".
            initial_dir (str, optional): The initial directory to display in the dialog. Defaults to "." (current directory).
            filters (str, optional): A string representing file filters (e.g., "Text Files (*.txt)"). Defaults to None (all files).
                Example filters string:
                "Archive Files (*.zip *.rar);;Text Files (*.txt);;All Files (*.*)"
                NOTE: Extensions are delimited with space

        Returns:
            str: The selected file path (or None if cancelled).
        """

        from PyQt5.QtWidgets import QFileDialog

        if isinstance(initial_dir, FileInformation):
            initial_dir = initial_dir.absolute_path()

        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly if not filters else QFileDialog.DontUseNativeDialog
        dialog = QFileDialog.getOpenFileName(parent_widget, title, initial_dir, filters, options=options)
        
        if dialog:
            return dialog[0]
        else:
            return None

    @staticmethod
    def show_save_file_PyQt5(parent_widget = None, title: str = "Save File", default_filename: Union[str, FileInformation] = None, filters: str = None) -> str | None:
        """
        Opens a save file dialog with specified parameters.

        Args:
            self (QtWidgets.QWidget): The parent widget for the dialog.
            title (str, optional): The title of the dialog window. Defaults to "Save File".
            default_filename (str, optional): The default filename to pre-fill. Defaults to None.
            initial_dir (str, optional): The initial directory to display in the dialog. Defaults to "." (current directory).
            filters (str, optional): A string representing file filters (e.g., "Text Files (*.txt)"). Defaults to None (all files).
                Example filters string:
                "Archive Files (*.zip *.rar);;Text Files (*.txt);;All Files (*.*)"
                NOTE: Extensions are delimited with space

        Returns:
            str: The selected file path (or None if cancelled).
        """
        from PyQt5.QtWidgets import QFileDialog

        if isinstance(default_filename, FileInformation):
            default_filename = default_filename.absolute_path()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        dialog = QFileDialog.getSaveFileName(parent_widget, title, default_filename, filters, options=options)
        
        if dialog:
            return dialog[0]
        else:
            return None

    @staticmethod
    def show_select_folder_PyQt5(parent_widget = None, title: str = "Select Folder", initial_dir: str = ".") -> str | None:
        """
        Opens a folder selection dialog with specified parameters.

        Args:
            self (QtWidgets.QWidget): The parent widget for the dialog.
            title (str, optional): The title of the dialog window. Defaults to "Select Folder".
            initial_dir (str, optional): The initial directory to display in the dialog. Defaults to "." (current directory).

        Returns:
            str: The selected folder path (or None if cancelled).
        """
        from PyQt5.QtWidgets import QFileDialog

        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
        dialog = QFileDialog.getExistingDirectory(parent_widget, title, initial_dir, options=options)

        if dialog:
            return dialog
        else:
            return None

    @staticmethod
    def join_folder_and_file_name(folder_path: str, file_name: str, validate_paths: bool = False) -> str:
        if not validate_paths:
            if folder_path and folder_path[-1] != "/":
                folder_path += "/"
            
            return FileUtility.get_absolute_path(folder_path + file_name)

        folder_obj = FileInformation(folder_path)
        file_obj = FileInformation(file_name)

        if not folder_obj.is_directory():
            LogHandler.add_log_record("#1: Error in method #2. Folder not found!\nFolder #3 is not found.", ["FileUtility", "join_folder_and_file_name", folder_path], exception_raised=True)
            raise FileNotFoundError(f"{folder_path} is not a directory")

        if not file_obj.is_file():
            LogHandler.add_log_record("#1: Error in method #2. File not found!\nFile #3 is not found.", ["FileUtility", "join_folder_and_file_name", file_name], exception_raised=True)
            raise FileNotFoundError(f"{file_name} is not a file")
        
        result = folder_obj.get_dir_name() + file_obj.get_base_filename()

        return result

    @staticmethod
    def get_absolute_path(file_path: str) -> str:
        return os.path.abspath(file_path)

    @staticmethod
    def FILE_get_absolute_path(file_path: Union[str, FileInformation]) -> str:
        if isinstance(file_path, FileInformation):
            return file_path.absolute_path()
        else:
            return FileUtility.get_absolute_path(file_path)
    
    @staticmethod
    def FILE_is_files_content_equal(file_path1: Union[str, FileInformation, bytes], file_path2: Union[str, FileInformation, bytes]) -> bool:
        hash1 = None
        hash2 = None

        if isinstance(file_path1, FileInformation):
            file_path1 = file_path1.absolute_path()
        elif isinstance(file_path1, str):
            file_path1 = FileUtility.get_absolute_path(file_path1)
        elif isinstance(file_path1, bytes):
            hash1 = file_path1
        
        if isinstance(file_path2, FileInformation):
            file_path2 = file_path2.absolute_path()
        elif isinstance(file_path2, str):
            file_path2 = FileUtility.get_absolute_path(file_path2)
        elif isinstance(file_path2, bytes):
            hash2 = file_path2
            
        if hash1 is None:
            if not FileUtility.FILE_is_exist(file_path1):
                LogHandler.add_log_record("#1: File to compare content does not exist. (#2)", ["FileUtility", file_path1], warning_raised=True)
                return False
            with open(file_path1, "rb") as file:
                hash1 = hashlib.md5(file.read()).digest()
        
        if hash2 is None:
            if not FileUtility.FILE_is_exist(file_path2):
                LogHandler.add_log_record("#1: File to compare content does not exist. (#2)", ["FileUtility", file_path2], warning_raised=True)
                return False
            with open(file_path2, "rb") as file:
                hash2 = hashlib.md5(file.read()).digest()
        
        if hash1 == hash2:
            return True
        else:
            return False

    @staticmethod
    def FILE_get_hash(file_path: Union[str, FileInformation]) -> bytes:
        with open(file_path, "rb") as file:
            hash = hashlib.md5(file.read()).digest()
        
        return hash

    @staticmethod
    def FILE_is_exist(file_path: Union[str, FileInformation]) -> bool:
        if isinstance(file_path, FileInformation):
            return file_path.is_exist()
        
        if os.path.isfile(file_path):
            return True
        
        return False

    @staticmethod
    def FILE_copy(file_path: Union[str, FileInformation], destination_folder_or_file_path: Union[str, FileInformation]) -> Union[FileInformation, None]:
        """
        Copies file to new destination

        Args:
            file_path (string, FileInformation): File to be copied
            destination_folder_or_file_path (string, FileInformation):
                Destination folder or file to be replaced (Files must have same extension)
        
        Returns:
            FileInformation object of new file
        """
        if isinstance(file_path, FileInformation):
            file_path = file_path.absolute_path()
        else:
            file_path = FileUtility.get_absolute_path(file_path)
        
        if isinstance(destination_folder_or_file_path, FileInformation):
            destination_folder_or_file_path = destination_folder_or_file_path.absolute_path()
        else:
            destination_folder_or_file_path = FileUtility.get_absolute_path(destination_folder_or_file_path)
        
        if os.path.splitext(destination_folder_or_file_path)[1]:
            if os.path.splitext(destination_folder_or_file_path)[1] != os.path.splitext(file_path)[1]:
                LogHandler.add_log_record("#1: Original and destination file must have same extension in #2 method.\nOriginal file: #3\nDestination file: #4", ["FileUtility", "FILE_copy", file_path, destination_folder_or_file_path], exception_raised=True)
                raise ValueError("Original and destination file extension mismatch!")
        else:
            destination_folder_or_file_path = FileUtility.join_folder_and_file_name(destination_folder_or_file_path, os.path.basename(file_path))
            
        try:
            shutil.copy(file_path, destination_folder_or_file_path)
        except Exception as e:
            LogHandler.add_log_record("#1: Exception in method #2\nOriginal file: #3\nDestination file: #4\nException: #5", ["FileUtility", "FILE_copy", file_path, destination_folder_or_file_path, str(e)], exception_raised=True)
            raise e

        return FileInformation(destination_folder_or_file_path)

    @staticmethod
    def FILE_delete(file_path: Union[str, FileInformation]) -> bool:
        if isinstance(file_path, FileInformation):
            file_path = file_path.absolute_path()
        file_path = FileUtility.get_absolute_path(file_path)

        if not FileUtility.FILE_is_exist(file_path):
            LogHandler.add_log_record("#1: In function #2, attempting to delete file #3, but file does not exist.\nFile path (#3) does not exist!", ["FileUtility", "FILE_delete", file_path])
            return False

        # Delete file
        try:
            os.remove(file_path)
        except Exception as e:
            LogHandler.add_log_record("#1: Exception in method #2\nFile path (#3) cannot be deleted.\nException: #4", ["FileUtility", "FILE_delete", file_path, str(e)], exception_raised=True)
            raise e        
        
        return True

    @staticmethod
    def FILE_get_base_filename(file_path: Union[str, FileInformation]) -> str:
        if isinstance(file_path, FileInformation):
            file_path = file_path.absolute_path()
        else:
            file_path = FileUtility.get_absolute_path(file_path)
        
        return os.path.basename(file_path)

    @staticmethod
    def FILE_get_size(file_path: Union[str, FileInformation]) -> int:
        if isinstance(file_path, FileInformation):
            file_path = file_path.absolute_path()
        else:
            file_path = FileUtility.get_absolute_path(file_path)
        
        return os.path.getsize(file_path)

    @staticmethod
    def FOLDER_is_exist(folder_path: Union[str, FileInformation]) -> bool:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        if os.path.isdir(folder_path):
            return True
        
        return False
    
    @staticmethod
    def FOLDER_create(folder_path: Union[str, FileInformation]) -> bool:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nFolder path (#3) cannot be created.\nException: #4", ["FileUtility", "FOLDER_create", folder_path, str(e)], exception_raised=True)
                raise e
        else:
            LogHandler.add_log_record("#1: Warning in method #2.\nFolder path (#3) already exists!", ["FileUtility", "FOLDER_create", folder_path], warning_raised=True)
            return False
        
        return True

    @staticmethod
    def FOLDER_list_files(folder_path: Union[str, FileInformation], return_base_name_only: bool = False) -> list:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        result = []

        for item in os.listdir(folder_path):
            if return_base_name_only:
                result.append(item)
            else:
                item_path = FileUtility.join_folder_and_file_name(folder_path, item)
                if os.path.isfile(item_path):
                    result.append(item_path)
        
        return result

    @staticmethod
    def FOLDER_list_folders(folder_path: Union[str, FileInformation]) -> list:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        result = []

        for item in os.listdir(folder_path):
            item_path = FileUtility.join_folder_and_file_name(folder_path, item)
            if os.path.isdir(item_path):
                result.append(item_path)
        
        return result

    @staticmethod
    def FOLDER_delete_tree(folder_path: Union[str, FileInformation]) -> bool:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        if os.path.exists(folder_path):
            files = list(os.listdir(folder_path))
            for item in files:
                item_path = FileUtility.join_folder_and_file_name(folder_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    FileUtility.FOLDER_delete_tree(item_path)

            try:
                os.rmdir(folder_path)
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nFolder path (#3) cannot be deleted.\nException: #4", ["FileUtility", "FOLDER_delete_tree", folder_path, str(e)], exception_raised=True)
                raise e
        else:
            LogHandler.add_log_record("#1: Warning in method #2.\nFolder path (#3) does not exist!", ["FileUtility", "FOLDER_delete", folder_path], warning_raised=True)
            return False
        
        return True

    @staticmethod
    def FOLDER_delete_all_files(folder_path: Union[str, FileInformation]) -> bool:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        if os.path.exists(folder_path):
            try:
                folder_path = FileUtility.get_absolute_path(folder_path)
                for item in os.listdir(folder_path):
                    file_path = FileUtility.join_folder_and_file_name(folder_path, item)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nSome or all files in folder #3 cannot be deleted.\nException: #4", ["FileUtility", "FOLDER_delete_all_files", folder_path, str(e)], exception_raised=True)
                raise e
        else:
            LogHandler.add_log_record("#1: Warning in method #2.\nFolder path (#3) does not exist!", ["FileUtility", "FOLDER_delete_all_files", folder_path], warning_raised=True)
            return False
        
        return True

    @staticmethod
    def FOLDER_delete(folder_path: Union[str, FileInformation]) -> bool:
        if isinstance(folder_path, FileInformation):
            folder_path = folder_path.absolute_path()
        else:
            folder_path = FileUtility.get_absolute_path(folder_path)

        if os.path.exists(folder_path):
            FileUtility.FOLDER_delete_all_files(folder_path)
            try:
                os.rmdir(folder_path)
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nFolder path (#3) cannot be deleted.\nException: #4", ["FileUtility", "FOLDER_delete", folder_path, str(e)], exception_raised=True)
                raise e
        else:
            LogHandler.add_log_record("#1: Warning in method #2.\nFolder path (#3) does not exist!", ["FileUtility", "FOLDER_delete", folder_path], warning_raised=True)
            return False
        
        return True

    @staticmethod
    def ZIP_is_zipfile(archive_path: Union[str, FileInformation]) -> bool:
        if isinstance(archive_path, FileInformation):
            archive_path = archive_path.absolute_path()
        else:
            archive_path = FileUtility.get_absolute_path(archive_path)
        
        if zipfile.is_zipfile(archive_path):
            return True
        else:
            return False
    
    @staticmethod
    def ZIP_list_archive(archive_path: Union[str, FileInformation]) -> list:
        """
        Returns list of files and folders in archive
        If file is not ZIP archive raises exception
        """
        if isinstance(archive_path, FileInformation):
            archive_path = archive_path.absolute_path()
        else:
            archive_path = FileUtility.get_absolute_path(archive_path)
        
        if zipfile.is_zipfile(archive_path):
            result = []
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                for info in zip_file.infolist():
                    result.append(info.filename)
            return result
        else:
            LogHandler.add_log_record("#1: ZIP archive not found. Function: #2\nFile path: #3", ["FileUtility", "ZIP_list_archive", archive_path], exception_raised=True)
            raise ValueError("ZIP archive not found!")

    @staticmethod
    def ZIP_create_new_archive(archive_path: Union[str, FileInformation]) -> bool:
        """
        Creates new empty ZIP archive
        If file exist raises exception
        """
        if isinstance(archive_path, FileInformation):
            archive_path = archive_path.absolute_path()
        else:
            archive_path = FileUtility.get_absolute_path(archive_path)
        
        if zipfile.is_zipfile(archive_path):
            LogHandler.add_log_record("#1: ZIP archive already exists. Function: #2\nFile path: #3", ["FileUtility", "ZIP_create_new_archive", archive_path], exception_raised=True)
            raise ValueError("ZIP archive already exists!")
        else:
            try:
                zip_file = zipfile.ZipFile(archive_path, "w")
                zip_file.close()
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nFile path: #3\nException: #4", ["FileUtility", "ZIP_create_new_archive", archive_path, str(e)], exception_raised=True)
                raise e
            return True
        
    @staticmethod
    def ZIP_add_file_to_archive(archive_path: Union[str, FileInformation], file_path_to_add: Union[str, FileInformation], create_new_archive_if_not_exist: bool = False) -> bool:
        """
        Adds file to ZIP archive
        If file does not exist raises exception

        Args:
            archive_path (str, FileInformation): Path to ZIP archive
            file_path_to_add (str, FileInformation): Path to file to be added to ZIP archive
            create_new_archive_if_not_exist (bool): If ZIP archive does not exits, new archive will be created
        """
        if isinstance(archive_path, FileInformation):
            archive_path = archive_path.absolute_path()
        else:
            archive_path = FileUtility.get_absolute_path(archive_path)
        
        if isinstance(file_path_to_add, FileInformation):
            file_path_to_add = file_path_to_add.absolute_path()
        else:
            file_path_to_add = FileUtility.get_absolute_path(file_path_to_add)
        
        if create_new_archive_if_not_exist and not zipfile.is_zipfile(archive_path):
            FileUtility.ZIP_create_new_archive(archive_path)

        if not FileUtility.FILE_is_exist(file_path_to_add):
            LogHandler.add_log_record("#1: File to add not found. Function: #2\nFile path: #3", ["FileUtility", "ZIP_add_file_to_archive", file_path_to_add], exception_raised=True)
            raise ValueError("File to add to archive not found!")
        
        if zipfile.is_zipfile(archive_path):
            try:
                if os.path.basename(file_path_to_add) not in FileUtility.ZIP_list_archive(archive_path):
                    zip_file = zipfile.ZipFile(archive_path, "a")
                    zip_file.write(file_path_to_add, arcname=os.path.basename(file_path_to_add))
                    zip_file.close()
                else:
                    return False
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nArchive path: #3\nFile to add path: #4\nException: #5", ["FileUtility", "ZIP_add_file_to_archive", archive_path, file_path_to_add, str(e)], exception_raised=True)
                raise e
            return True
        else:
            LogHandler.add_log_record("#1: ZIP archive not found. Function: #2\nArchive path: #3", ["FileUtility", "ZIP_add_file_to_archive", archive_path], exception_raised=True)
            raise ValueError("ZIP archive not found!")

    @staticmethod
    def ZIP_extract_file_from_archive(archive_path: Union[str, FileInformation], filename_to_extract: str, destination_folder: str) -> bool:
        """
        Extracts file from ZIP archive
        If file does not exist raises exception
        """
        if isinstance(archive_path, FileInformation):
            archive_path = archive_path.absolute_path()
        else:
            archive_path = FileUtility.get_absolute_path(archive_path)
        
        if not destination_folder.endswith("/"):
            destination_folder = destination_folder + "/"

        if zipfile.is_zipfile(archive_path):
            try:
                zip_file = zipfile.ZipFile(archive_path, "r")
                zip_file.extract(filename_to_extract, destination_folder)
                zip_file.close()
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nArchive path: #3\nFilename to extract: #4\nDestination folder: #4\nException: #5", ["FileUtility", "ZIP_extract_file_from_archive", archive_path, filename_to_extract, destination_folder, str(e)], exception_raised=True)
                raise e
            return True
        else:
            LogHandler.add_log_record("#1: ZIP archive not found. Function: #2\nArchive path: #3", ["FileUtility", "ZIP_extract_file_from_archive", archive_path], exception_raised=True)
            raise ValueError("ZIP archive not found!")
        
    @staticmethod
    def ZIP_extract_all_files_from_archive(archive_path: Union[str, FileInformation], destination_folder: str) -> bool:
        """
        Extracts all files from ZIP archive
        """
        if isinstance(archive_path, FileInformation):
            archive_path = archive_path.absolute_path()
        else:
            archive_path = FileUtility.get_absolute_path(archive_path)
        
        if not destination_folder.endswith("/"):
            destination_folder = destination_folder + "/"
        
        if zipfile.is_zipfile(archive_path):
            try:
                zip_file = zipfile.ZipFile(archive_path, "r")
                zip_file.extractall(destination_folder)
                zip_file.close()
            except Exception as e:
                LogHandler.add_log_record("#1: Exception in method #2\nArchive path: #3\nDestination folder: #4\nException: #5", ["FileUtility", "ZIP_extract_all_files_from_archive", archive_path, destination_folder, str(e)], exception_raised=True)
                raise e
            return True

    @staticmethod
    def JSON_dump(file_path: Union[str, FileInformation], data: Union[dict, list]) -> bool:
        if isinstance(file_path, FileInformation):
            file_path = file_path.absolute_path()
        else:
            file_path = FileUtility.get_absolute_path(file_path)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            LogHandler.add_log_record("#1: Exception in method #2\nFile path: #3\nException: #4\ntype(data) = #5", ["FileUtility", "JSON_dump", file_path, str(e), type(data)], warning_raised=True)
            return False
        
        return True

    @staticmethod
    def JSON_load(file_path: Union[str, FileInformation]) -> Any:
        if isinstance(file_path, FileInformation):
            file_path = file_path.absolute_path()
        else:
            file_path = FileUtility.get_absolute_path(file_path)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            LogHandler.add_log_record("#1: Exception in method #2\nFile path: #3\nException: #4", ["FileUtility", "JSON_load", file_path, str(e)], exception_raised=True)
            raise e
        
        

