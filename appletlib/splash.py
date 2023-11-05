import subprocess

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import QWidget


class Splash(QWidget):
    triggerClick = pyqtSignal(QMouseEvent)
    triggerDoubleClick = pyqtSignal(QMouseEvent)
    triggerResize = pyqtSignal(QResizeEvent)

    def __init__(self):
        super(Splash, self).__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.BypassWindowManagerHint
            | Qt.WindowType.FramelessWindowHint
        )
        self.setGeometry(0, 0, 1, 1)
        self.setWindowOpacity(0.75)
        self.font = QFont("Dejavu Sans", 8)

    def showEvent(self, ev):
        subprocess.call(
            [
                "xprop",
                "-id",
                "0x%x" % int(self.effectiveWinId()),
                "-f",
                "_NET_WM_DESKTOP",
                "32c",
                "-set",
                "_NET_WM_DESKTOP",
                "0xFFFFFFFF",
            ]
        )

    def resizeEvent(self, ev):
        self.triggerResize.emit(ev)

    def mouseReleaseEvent(self, ev):
        self.triggerClick.emit(ev)

    def mouseDoubleClickEvent(self, ev):
        self.triggerDoubleClick.emit(ev)
