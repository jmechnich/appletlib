import syslog

from PyQt4.Qt import *

from app import Application

class SystemTrayIcon(QSystemTrayIcon):
    triggerUpdate = pyqtSignal()
    
    def __init__(self,name,interval=1000):
        QSystemTrayIcon.__init__(self)
        self.fgColor = QColor(
            Application.settingsValue("fgColor", QColor("#33b0dc")))
        self.bgColor = QColor(
            Application.settingsValue("bgColor", QColor("#144556")))
        self.interval = Application.settingsValue(
            "%s/interval" % name, interval).toInt()[0]
        
        pix = QPixmap(22,22)
        p = QPainter(pix)
        p.fillRect(pix.rect(), Qt.black)
        p.end()
        self.setIcon(QIcon(pix))
        self.startTimer( self.interval)

    def timerEvent(self,ev):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  systray timerEvent")
        self.triggerUpdate.emit()
