from PyQt5.QtWidgets import QDialog, QWidget, QApplication, QLabel
from PyQt5.QtCore import Qt, QObject, QCoreApplication, QEvent
from PyQt5.QtGui import QPixmap

from typing import Union, Any
import os

from utils_terminal import TerminalUtility


class DialogUtility:

    @staticmethod
    def on_closeEvent(widget: QDialog,
                      close_widget_handler: bool = True,
                      close_children: bool = True,
                      hide_widget: bool = True,
                      delete_widget: bool = True) -> bool:
        """
        Perform any necessary actions when the window is about to be closed.
        - Checks if the 'widget_handler' variable exists, if it does, closes the widget_handler object
        - Closes all child objects that have a 'close_me()' method        

        Args:
        widget (QWidget): Widget to be closed (usually the QDialog or QFrame).

        Returns:
        None
        """

        result = True
        try:
            can_be_deleted = widget.can_be_deleted
            if not can_be_deleted:
                close_widget_handler = False
                close_children = False
                delete_widget = False
                result = False
        except Exception as e:
            pass


        if close_widget_handler:
            try:
                if widget.widget_handler:
                    widget.widget_handler.close_me()
                    widget.widget_handler = None
            except AttributeError:
                pass
        
        if close_children:
            try:
                for child in widget.children():
                    try:
                        child.close_me()
                    except AttributeError:
                        pass
            except Exception as e:
                TerminalUtility.WarningMessage("Failed to close children.\n#1", [str(e)])

        if hide_widget:
            try:
                widget.hide()
            except Exception as e:
                TerminalUtility.WarningMessage("Failed to hide widget.\n#1", [str(e)])
        
        if delete_widget:
            try:
                widget.deleteLater()
            except Exception as e:
                TerminalUtility.WarningMessage("Failed to delete children.\n#1", [str(e)])
        
        return result
    

class WidgetUtility:

    @staticmethod
    def set_image_to_label(image_path: str, label: QLabel, stretch_to_label: bool = False, resize_label: bool = False, resize_label_fixed_w: bool = False, resize_label_fixed_h: bool = False) -> bool:
        if not os.path.isfile(image_path):
            return False

        img = QPixmap()
        has_image = img.load(os.path.abspath(image_path))
        if not has_image:
            return False

        if stretch_to_label:
            label.setScaledContents(True)
        else:
            label.setScaledContents(False)
            if resize_label:
                scale = img.width() / img.height()
                if scale >= 1:
                    label.resize(int(label.height() * scale), label.height())
                else:
                    label.resize(label.width(), int(label.width() / scale))
            if resize_label_fixed_w:
                scale = img.height() / img.width()
                label.resize(label.width(), int(label.width() * scale))
            if resize_label_fixed_h:
                scale = img.width() / img.height()
                label.resize(int(label.height() * scale), label.height())

            img = img.scaled(label.width(), label.height(), Qt.KeepAspectRatio)

        label.setPixmap(img)

        return True


