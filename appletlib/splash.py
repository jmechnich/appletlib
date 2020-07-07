import subprocess

from PyQt5.Qt import *

class Splash(QWidget):
    triggerClick = pyqtSignal(QMouseEvent)
    triggerDoubleClick = pyqtSignal(QMouseEvent)

    def __init__(self):
        super(Splash,self).__init__()
        self.setWindowFlags(Qt.SplashScreen|Qt.WindowStaysOnTopHint);
        self.setGeometry(0,0,1,1)
        self.setWindowOpacity(0.75)
        self.font = QFont("Dejavu Sans", 8)

    def showEvent(self, ev):
        subprocess.call( ['xprop', '-id', "0x%x" % int(self.effectiveWinId()),
                          '-f', '_NET_WM_DESKTOP', '32c',
                          '-set', '_NET_WM_DESKTOP', '0xFFFFFFFF'] )

    def mouseReleaseEvent(self, ev):
        self.triggerClick.emit(ev)

    def mouseDoubleClickEvent(self, ev):
        self.triggerDoubleClick.emit(ev)
