from typing import Any, Union
from PyQt5.QtCore import QObject, pyqtSignal


class ApplicationSignals(QObject):
    signalVolumeChanged = pyqtSignal(int, dict)
    signalLogUpdated = pyqtSignal(dict, dict)
    signalBlockChanged = pyqtSignal(dict)

    # File
    signalFileAdded = pyqtSignal(dict)
    signalFileSaved = pyqtSignal(dict)
    signalFileDeleted = pyqtSignal(dict)

    # Image
    signalImageAdded = pyqtSignal(dict)
    signalImageSaved = pyqtSignal(dict)
    signalImageDeleted = pyqtSignal(dict)

    # Tag
    signalTagAdded = pyqtSignal(dict)
    signalTagSaved = pyqtSignal(dict)
    signalTagDeleted = pyqtSignal(dict)

    # Def
    signalDefAdded = pyqtSignal(dict)
    signalDefSaved = pyqtSignal(dict)
    signalDefDeleted = pyqtSignal(dict)

    # Block
    signalBlockAdded = pyqtSignal(dict)
    signalBlockSaved = pyqtSignal(dict)
    signalBlockDeleted = pyqtSignal(dict)

    # AutoComplete
    signalAutoCompleteDataUpdated = pyqtSignal()


    @staticmethod
    def instance():
        if not hasattr(ApplicationSignals, "_instance"):
            ApplicationSignals._instance = ApplicationSignals()
        return ApplicationSignals._instance
    
    def emit_volume_changed(self, volume: int, data: dict = None):
        if data is None:
            data = {}
        self.signalVolumeChanged.emit(volume, data)

    def emit_log_updated(self, emitter_func_info: dict, log_data: dict):
        self.signalLogUpdated.emit(emitter_func_info, log_data)
    
    def emit_block_changed(self, block_info: dict):
        self.signalBlockChanged.emit(block_info)
    
    def emit_file_added(self, file_dict: dict):
        self.signalFileAdded.emit(file_dict)

    def emit_file_saved(self, file_dict: dict):
        self.signalFileSaved.emit(file_dict)
    
    def emit_file_deleted(self, file_dict: dict):
        self.signalFileDeleted.emit(file_dict)

    def emit_image_added(self, image_dict: dict):
        self.signalImageAdded.emit(image_dict)

    def emit_image_saved(self, image_dict: dict):
        self.signalImageSaved.emit(image_dict)
    
    def emit_image_deleted(self, image_dict: dict):
        self.signalImageDeleted.emit(image_dict)
    
    def emit_tag_added(self, tag_dict: dict):
        self.signalTagAdded.emit(tag_dict)
    
    def emit_tag_saved(self, tag_dict: dict):
        self.signalTagSaved.emit(tag_dict)
    
    def emit_tag_deleted(self, tag_dict: dict):
        self.signalTagDeleted.emit(tag_dict)

    def emit_def_added(self, def_dict: dict):
        self.signalDefAdded.emit(def_dict)
    
    def emit_def_saved(self, def_dict: dict):
        self.signalDefSaved.emit(def_dict)
    
    def emit_def_deleted(self, def_dict: dict):
        self.signalDefDeleted.emit(def_dict)
    
    def emit_block_added(self, block_dict: dict):
        self.signalBlockAdded.emit(block_dict)
    
    def emit_block_saved(self, block_dict: dict):
        self.signalBlockSaved.emit(block_dict)
    
    def emit_block_deleted(self, block_dict: dict):
        self.signalBlockDeleted.emit(block_dict)
    
    def emit_auto_complete_data_updated(self):
        self.signalAutoCompleteDataUpdated.emit()
    

class Signal:
    signalVolumeChanged = ApplicationSignals.instance().signalVolumeChanged
    signalLogUpdated = ApplicationSignals.instance().signalLogUpdated
    signalBlockChanged = ApplicationSignals.instance().signalBlockChanged

    # File
    signalFileAdded = ApplicationSignals.instance().signalFileAdded
    signalFileSaved = ApplicationSignals.instance().signalFileSaved
    signalFileDeleted = ApplicationSignals.instance().signalFileDeleted

    # Image
    signalImageAdded = ApplicationSignals.instance().signalImageAdded
    signalImageSaved = ApplicationSignals.instance().signalImageSaved
    signalImageDeleted = ApplicationSignals.instance().signalImageDeleted

    # Tag
    signalTagAdded = ApplicationSignals.instance().signalTagAdded
    signalTagSaved = ApplicationSignals.instance().signalTagSaved
    signalTagDeleted = ApplicationSignals.instance().signalTagDeleted

    # Def
    signalDefAdded = ApplicationSignals.instance().signalDefAdded
    signalDefSaved = ApplicationSignals.instance().signalDefSaved
    signalDefDeleted = ApplicationSignals.instance().signalDefDeleted

    # Block
    signalBlockAdded = ApplicationSignals.instance().signalBlockAdded
    signalBlockSaved = ApplicationSignals.instance().signalBlockSaved
    signalBlockDeleted = ApplicationSignals.instance().signalBlockDeleted

    # AutoComplete
    signalAutoCompleteDataUpdated = ApplicationSignals.instance().signalAutoCompleteDataUpdated

    @staticmethod
    def emit_volume_changed(volume: int, data: dict = None):
        ApplicationSignals.instance().emit_volume_changed(volume, data)

    @staticmethod
    def emit_log_updated(emitter_func_info: dict, log_data: dict):
        ApplicationSignals.instance().emit_log_updated(emitter_func_info, log_data)
    
    @staticmethod
    def emit_block_changed(block_info: dict):
        """
        Emits a signal that a block has been changed.
        block_info (dict):
            "id" (int): Block ID
            "action" (list): [updated, deleted, saved, closed...]
            "source" (str): Source of signal (name of class)
            "date" (str): Block date
            "name" (str): Block name
            "body" (str): Block body
            "draft" (int): 0=Closed, 1=Draft
        """
        ApplicationSignals.instance().emit_block_changed(block_info)

    @staticmethod
    def emit_file_added(file_dict: dict):
        ApplicationSignals.instance().emit_file_added(file_dict)
    
    @staticmethod
    def emit_file_saved(file_dict: dict):
        ApplicationSignals.instance().emit_file_saved(file_dict)
    
    @staticmethod
    def emit_file_deleted(file_dict: dict):
        ApplicationSignals.instance().emit_file_deleted(file_dict)

    @staticmethod
    def emit_image_added(image_dict: dict):
        ApplicationSignals.instance().emit_image_added(image_dict)
    
    @staticmethod
    def emit_image_saved(image_dict: dict):
        ApplicationSignals.instance().emit_image_saved(image_dict)
    
    @staticmethod
    def emit_image_deleted(image_dict: dict):
        ApplicationSignals.instance().emit_image_deleted(image_dict)

    @staticmethod
    def emit_tag_added(tag_dict: dict):
        ApplicationSignals.instance().emit_tag_added(tag_dict)

    @staticmethod
    def emit_tag_saved(tag_dict: dict):
        ApplicationSignals.instance().emit_tag_saved(tag_dict)

    @staticmethod
    def emit_tag_deleted(tag_dict: dict):
        ApplicationSignals.instance().emit_tag_deleted(tag_dict)
    
    @staticmethod
    def emit_def_added(def_dict: dict):
        ApplicationSignals.instance().emit_def_added(def_dict)
    
    @staticmethod
    def emit_def_saved(def_dict: dict):
        ApplicationSignals.instance().emit_def_saved(def_dict)
    
    @staticmethod
    def emit_def_deleted(def_dict: dict):
        ApplicationSignals.instance().emit_def_deleted(def_dict)
    
    @staticmethod
    def emit_block_added(block_dict: dict):
        ApplicationSignals.instance().emit_block_added(block_dict)
    
    @staticmethod
    def emit_block_saved(block_dict: dict):
        ApplicationSignals.instance().emit_block_saved(block_dict)
    
    @staticmethod
    def emit_block_deleted(block_dict: dict):
        ApplicationSignals.instance().emit_block_deleted(block_dict)
    
    @staticmethod
    def emit_auto_complete_data_updated():
        ApplicationSignals.instance().emit_auto_complete_data_updated()





