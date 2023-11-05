import syslog

from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QColorConstants,
    QHelpEvent,
    QIcon,
    QPainter,
    QPixmap,
)
from PyQt6.QtWidgets import QSystemTrayIcon

from appletlib.app import Application

class SystemTrayIcon(QSystemTrayIcon):
    triggerToolTip = pyqtSignal(QHelpEvent)
    triggerUpdate = pyqtSignal()
    triggerWheel  = pyqtSignal(int)
    
    def __init__(self,name,interval=1000):
        super(SystemTrayIcon,self).__init__()
        self.fgColor = QColor(
            Application.settingsValue("fgColor", QColor("#33b0dc")))
        self.bgColor = QColor(
            Application.settingsValue("bgColor", QColor("#144556")))
        self.interval = int(Application.settingsValue(
            f"{name}/interval", interval))
        
        pix = QPixmap(22,22)
        p = QPainter(pix)
        p.fillRect(pix.rect(), QColorConstants.Black)
        p.end()
        self.setIcon(QIcon(pix))
        self.startTimer(self.interval)

    def timerEvent(self,ev):
        self.triggerUpdate.emit()

    def event(self,ev):
        if ev.type() == QEvent.Type.Wheel:
            ev.accept()
            self.triggerWheel.emit(ev.angleDelta().y())
            return True
        elif ev.type() == QEvent.Type.Timer:
            pass
        elif ev.type() == QEvent.Type.ToolTip:
            ev.accept()
            self.triggerToolTip.emit(ev)
            return True
        else:
            syslog.syslog(
                syslog.LOG_DEBUG, f"DEBUG  systray event type '{ev.type().name}'"
            )

        return super(SystemTrayIcon,self).event(ev)
