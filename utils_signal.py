from PyQt5.QtCore import QObject, pyqtSignal


class ApplicationSignals(QObject):
    signalVolumeChanged = pyqtSignal(int, dict)
    signalLogUpdated = pyqtSignal(dict, dict)
    signalBlockChanged = pyqtSignal(dict)

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


class Signal:
    signalVolumeChanged = ApplicationSignals.instance().signalVolumeChanged
    signalLogUpdated = ApplicationSignals.instance().signalLogUpdated
    signalBlockChanged = ApplicationSignals.instance().signalBlockChanged

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




