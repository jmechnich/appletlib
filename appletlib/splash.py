import subprocess

from PyQt4.Qt import *

class Splash(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.SplashScreen|Qt.WindowStaysOnTopHint);
        self.setGeometry(0,0,1,1)
        self.setWindowOpacity(0.75)
        self.font = QFont("Dejavu Sans", 8)
    
    def show(self):
        QWidget.show(self)
        subprocess.call( ['xprop', '-id', "0x%x" % self.winId(),
                          '-f', '_NET_WM_DESKTOP', '32c',
                          '-set', '_NET_WM_DESKTOP', '0xFFFFFFFF'] )
        
