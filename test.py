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
        

counter(1)



from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtCore import Qt


class Proba(QLabel):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)

        self.lbl = QLabel(self)
        self.lbl.resize(200,200)

        print ("Is QWidget: ", isinstance(self.lbl, QWidget))

        sty = "QLabel {color: #00ff00; background-color: transparent; border: 1px solid #00aaff;}"

        self.lbl.setStyleSheet(sty)
        app.processEvents()
        img = QPixmap("data/app/images/abort.png")
        img = img.scaled(20, 60, Qt.KeepAspectRatio)
        cur  = QCursor(img)
        self.lbl.setCursor(cur)
        print ("Cursor: ", Qt.SizeAllCursor)
        print (self.lbl.styleSheet())
        print ("Object Name: ", self.lbl.objectName())

        print (sty == self.lbl.styleSheet())

        self.lbl.mousePressEvent = self.lbl_mousePressEvent

        self.show()

    def enterEvent(self, a0: QEvent | None) -> None:
        return super().enterEvent(a0)

    def lbl_mousePressEvent(self, a0) -> None:
        # Set cursor to default
        cur = QCursor()
        self.lbl.setCursor(cur)
        QLabel.mousePressEvent(self.lbl, a0)

app = QApplication([])
a = Proba()
print ("Is QWidget: ", isinstance(a, QWidget))
app.exec_()
