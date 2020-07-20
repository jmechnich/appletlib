import syslog

from PyQt5.Qt import *

from appletlib.app import Application

class SystemTrayIcon(QSystemTrayIcon):
    triggerToolTip = pyqtSignal(QHelpEvent)
    triggerUpdate = pyqtSignal()
    triggerWheel  = pyqtSignal(int)
    eventDict = dict((v,k) for k,v in  QEvent.__dict__.items())
    
    def __init__(self,name,interval=1000):
        super(SystemTrayIcon,self).__init__()
        self.fgColor = QColor(
            Application.settingsValue("fgColor", QColor("#33b0dc")))
        self.bgColor = QColor(
            Application.settingsValue("bgColor", QColor("#144556")))
        self.interval = int(Application.settingsValue(
            "%s/interval" % name, interval))
        
        pix = QPixmap(22,22)
        p = QPainter(pix)
        p.fillRect(pix.rect(), Qt.black)
        p.end()
        self.setIcon(QIcon(pix))
        self.startTimer(self.interval)

    def timerEvent(self,ev):
        self.triggerUpdate.emit()

    def event(self,ev):
        if ev.type() == QEvent.Wheel:
            ev.accept()
            self.triggerWheel.emit(ev.angleDelta().y())
            return True
        elif ev.type() == QEvent.Timer:
            pass
        elif ev.type() == QEvent.ToolTip:
            ev.accept()
            self.triggerToolTip.emit(ev)
            return True
        else:
            syslog.syslog(
                syslog.LOG_DEBUG, "DEBUG  systray event type '%s'" % \
                self.eventDict[ev.type()])

        return super(SystemTrayIcon,self).event(ev)
