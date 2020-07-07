import syslog

from appletlib.systray import SystemTrayIcon

from PyQt5.Qt import QApplication, QPixmap, QTimer, QRect, QIcon

class Indicator(object):
    indicators = []

    def __init__(self,name,interval=1000):
        if self not in self.indicators:
            self.indicators += [self]
        self.name = name
        self.interval = interval
        self.initSystray()
        self.splash = None
        QApplication.desktop().resized.connect(self.screenSizeChanged)
    
    def __del__(self):
        if self in self.indicators:
            self.indicators.remove(self)

    def initSystray(self):
        self.systray = SystemTrayIcon(self.name, self.interval)
        p = QPixmap(22,22)
        p.fill(self.systray.bgColor)
        self.systray.setIcon(QIcon(p))
        self.systray.show()

    def reset(self):
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG  indicator reset")
        self.systray.deleteLater()
        self.initSystray()
        for i in self.indicators:
            QTimer.singleShot(0, i.updateSplashGeometry)
        
    def boundingBox(self):
        r = QRect()
        for i in self.indicators:
            r = r.united(i.systray.geometry())
        return r
    
    def screenSizeChanged( self, screen):
        QTimer.singleShot(1000, self.updateSplashGeometry)
  
    def updateSplashGeometry(self, hide=False):
        syslog.syslog(syslog.LOG_DEBUG,
                      "DEBUG  indicator updateSplashGeometry")
        if not self.splash: return
        if hide: self.hideAllSplashes()
        r = self.systray.geometry()
        sr = QApplication.desktop().availableGeometry()
        left = sr.width() - self.splash.width - r.left()
        if left > 0: left = 0
        top = r.height()+3
        r.translate(left, top)
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG   topLeft: %d, %d" %
                      (r.left(), r.top()))
        self.splash.move(r.topLeft())

    def hideAllSplashes(self):
        for i in self.indicators:
            if i.splash:
                i.splash.hide()
