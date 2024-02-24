import time
import functools
from PyQt5.QtCore import QEvent


def time_func(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}\n Arguments: {args, kwargs}\n Execution time: {(end - start) * 1000:.2f} ms")
    return wrapper

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@time_func
@log
def counter(scope: int) -> None:
    for i in range(1, scope + 1):
        print(i)
        time.sleep(0.3)
        

# counter(1)



from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QLineEdit, QTextEdit, QDialog
from PyQt5.QtGui import QCursor, QPixmap, QDrag, QDropEvent
from PyQt5.QtCore import Qt, QMimeData


class Proba(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)

        self.drag_mode = False

        self.lbl = QLabel(self)
        self.lbl.resize(200,200)
        sty = "QLabel {color: #00ff00; background-color: transparent; border: 1px solid #00aaff;}"
        self.lbl.setStyleSheet(sty)
        self.lbl.setText("Dado")
        


        self.btn = QPushButton(self)
        self.btn.move(210, 10)
        self.btn.setText("Press me")

        self.txt_text = QTextEdit(self)
        self.txt_text.setPlaceholderText("QTextEdit")
        self.txt_text.move(10,210)
        self.txt_text.resize(300, 200)
        self.txt_text.setAcceptDrops(True)

        print (type(self.txt_text))
        



        self.txt_line = QLineEdit(self)
        self.txt_line.setPlaceholderText("QLineEdit")
        self.txt_line.move(210, 100)
        self.txt_line.resize(150, 23)





        self.btn.clicked.connect(self.btn_clicked)
        self.lbl.mousePressEvent = self.lbl_mousePressEvent
        self.txt_text.dragEnterEvent = self.txt_text_dragEnterEvent
        self.txt_text.dropEvent = self.txt_text_dropEvent

        self.txt_line.mousePressEvent = self.txt_line_mousePressEvent
        self.txt_line.mouseReleaseEvent = self.txt_line_mouseReleaseEvent
        self.txt_line.dropEvent = self.txt_line_dropEvent

        self.show()


    def txt_line_dropEvent(self, a0):
        print ("Drop event")
        if self.drag_mode:
            self.drag_mode = False
            print ("drop canceled")
            return
        QLineEdit.dropEvent(self.txt_line, a0)

    def txt_line_mouseReleaseEvent(self, a0):
        print (self.txt_line.children())
        self.drag_mode = False
        print ("Mouse released")
        
        if self.drag_mode:
            return
        QLineEdit.mouseReleaseEvent(self.txt_line, a0)
        


    def txt_line_mousePressEvent(self, a0):
        if self.txt_line.selectedText():
            print ("Selected text: " + self.txt_line.selectedText())
            self.drag_mode = True
            drag = QDrag(self.txt_line)
            drag.setObjectName("drag_obj")
            mime = QMimeData()
            mime.setText(self.txt_line.selectedText())
            drag.setMimeData(mime)
            drag.exec_()
        else:
            print ("No text selected")
            QLineEdit.mousePressEvent(self.txt_line, a0)

    def txt_text_dragEnterEvent(self, a0):
        if a0.mimeData().hasText():
            print ("Enter with text")
            a0.accept()
        else:
            a0.ignore()

    def txt_text_dropEvent(self, a0: QDropEvent) -> None:
        if a0.mimeData().hasText():
            print ("Dropped text: " + a0.mimeData().text())
            self.txt_text.setText(a0.mimeData().text())
            a0.accept()
        else:
            a0.ignore()


    def btn_clicked(self):
        self.txt_line.setClearButtonEnabled(True)


    def enterEvent(self, a0: QEvent | None) -> None:
        return super().enterEvent(a0)

    def lbl_mousePressEvent(self, a0) -> None:
        drag = QDrag(self.lbl)

        mime = QMimeData()
        mime.setText(self.lbl.text())

        drag.setMimeData(mime)

        drag.exec()



app = QApplication([])

a = Proba()

app.exec_()
