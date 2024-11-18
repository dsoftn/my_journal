from PyQt5.QtWidgets import QMainWindow, QStatusBar, QFrame, QVBoxLayout, QLabel, QSlider, QApplication, QSpacerItem, QSizePolicy, QWidget
from PyQt5.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the main window
        self.setWindowTitle("Volume Control Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Create a custom widget for volume controls
        volume_frame = QFrame(self)
        volume_layout = QVBoxLayout()
        volume_label = QLabel("Volume", self)
        volume_slider = QSlider(Qt.Horizontal, self)
        volume_slider.setRange(0, 100)  # Set the range for volume control
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_frame.setLayout(volume_layout)

        # Add the custom volume frame to the status bar
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.statusBar.addPermanentWidget(spacer)
        self.statusBar.addPermanentWidget(volume_frame)

        # Connect volume slider signal to a slot to handle volume changes
        volume_slider.valueChanged.connect(self.handle_volume_change)

    def handle_volume_change(self, volume):
        # Logic to handle volume change
        print("Volume changed to:", volume)


# Create and show the main window
app = QApplication([])
main_window = MainWindow()
main_window.show()
sys.exit(app.exec_())