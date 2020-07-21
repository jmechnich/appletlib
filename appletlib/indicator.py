import syslog

from appletlib.app import Application, SettingsValue
from appletlib.systray import SystemTrayIcon

from PyQt5.Qt import *

class Indicator(object):
    indicators = []
    # splashpos: 0, 1, 2, 3 for top, left, bottom, right systray position
    splashpos = SettingsValue(
        "splashpos", 0, int, lambda val: Indicator.updateAllSplashes())

    def __init__(self,name,interval=1000):
        if self not in self.indicators:
            self.indicators += [self]
        self.name = name
        self.interval = interval
        self.initSystray()
        self.splash = None
        self.prefs  = None
        qApp.desktop().resized.connect(self.screenSizeChanged)

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
            QTimer.singleShot(500, i.updateSplashGeometry)

    def boundingBox(self):
        r = QRect()
        for i in self.indicators:
            r = r.united(i.systray.geometry())
        return r

    def screenSizeChanged(self, screen):
        QTimer.singleShot(1000, self.updateSplashGeometry)

    def updateSplashGeometry(self, hide=False):
        syslog.syslog(syslog.LOG_DEBUG,
                      "DEBUG  indicator %s updateSplashGeometry" % self.name)
        if not self.splash: return
        if hide: Indicator.hideAllSplashes()

        r = self.systray.geometry()
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG   systray rect: %s" % str(r))
        screen = qApp.primaryScreen()
        sr = screen.availableVirtualGeometry()

        top = 0
        splashpos = Indicator.splashpos.value()
        if splashpos == 0:
            left = sr.width() - self.splash.w - r.left()
            if left > 0: left = 0
            top = r.height()+3
        elif splashpos == 1:
            left = r.width()+3
        elif splashpos == 2:
            left = sr.width() - self.splash.w - r.left()
            if left > 0: left = 0
            top = -self.splash.h-3
        elif splashpos == 3:
            left = -self.splash.w-3

        r.translate(left, top)
        self.splash.move(r.topLeft())
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG   splash rect: %s" %
                      str(self.splash.geometry()))

    def getPrefs(self):
        if self.prefs:
            return self.prefs

        self.prefs = QGroupBox("Interface")
        v = QGridLayout()

        row = 0
        v.addWidget(QLabel("Splash position"), row, 0)
        splashposWid = QSpinBox()
        splashposWid.setRange(0, 3)
        splashposWid.setValue(Indicator.splashpos.value())
        splashposWid.valueChanged.connect(Indicator.splashpos.setValue)
        Indicator.splashpos.valueChanged.connect(splashposWid.setValue)
        v.addWidget(splashposWid, row, 1)
        row +=1

        self.prefs.setLayout(v)
        return self.prefs

    @staticmethod
    def updateAllSplashes():
        for i in Indicator.indicators:
            i.updateSplashGeometry()

    @staticmethod
    def hideAllSplashes():
        for i in Indicator.indicators:
            if i.splash:
                i.splash.hide()
