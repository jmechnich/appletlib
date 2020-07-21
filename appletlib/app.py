import argparse
import atexit
import os
import re
import signal
import socket
import sys
import syslog

from appletlib.posixsignal import Signal

from PyQt5.Qt import QFile, QDir, QIODevice, QIcon, QApplication, QObject
from PyQt5.Qt import QSettings, QTimer, QVariant, pyqtSignal

class Application(QApplication):
    timer = QTimer()
    sigusr1 = pyqtSignal()
    sigusr2 = pyqtSignal()

    def __init__(self, orgname, appname):
        super(Application,self).__init__(sys.argv)
        self.setOrganizationName(orgname)
        self.setApplicationName(appname)
        self.setQuitOnLastWindowClosed( False)

    def init(self, argdict):
        Application.setLogLevel(argdict.get('verbosity',0),
                                argdict.get('daemon', 0))
        self.initSignalHandlers()
        #Application.setThemeFromGtk()
        Application.startIdleTimer()

    @staticmethod
    def startIdleTimer():
        # switch to python interpreter context every 500ms to check if
        # POSIX signal was triggered
        Application.timer.start(500)
        Application.timer.timeout.connect(lambda:None)

    @staticmethod
    def parseCommandLine(desc):
        ret = {}
        parser = argparse.ArgumentParser(description=desc)
        parser.add_argument('-d', '--daemon',
                            help='run as daemon', action="store_true")
        parser.add_argument('-v', '--verbosity', type=int, default=0,
                            help='select verbosity (default: 0)')
        args = parser.parse_args()
        return args

    @staticmethod
    def setLogLevel(level, isDaemon):
        option = syslog.LOG_PID
        if not isDaemon:
            option |= syslog.LOG_PERROR

        syslog.openlog(str(QApplication.applicationName()),
                       option, syslog.LOG_USER)
        atexit.register(Application.cleanup)

        if level == 0:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_WARNING))
        elif level == 1:
            syslog.setlogmask(syslog.LOG_UPTO( syslog.LOG_NOTICE))
        elif level == 2:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_INFO))
        else:
            syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
        syslog.syslog(syslog.LOG_INFO, "INFO   logging to syslog")

    @staticmethod
    def cleanup():
        syslog.syslog(syslog.LOG_INFO, "INFO   shutting down");
        syslog.closelog()

    @staticmethod
    def setThemeFromGtk():
        f = QFile(QDir.homePath() + "/.gtkrc-2.0")
        if not f.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        while not f.atEnd():
            l = f.readLine().trimmed()
            if l.startsWith("gtk-icon-theme-name="):
                s = l.split('=')[-1]
                syslog.syslog(syslog.LOG_DEBUG,
                              "DEBUG  setting gtk theme %s" % str(s))
                QIcon.setThemeName(s.remove('"'))
                break

    @staticmethod
    def settingsValue( key, default, t=None):
        if t is None:
            t = type(default)
        syslog.syslog(syslog.LOG_DEBUG,
                      "DEBUG  settingsValue %s, default: %s, type: %s" %
                      (key, str(default), t))
        s = QSettings()
        var = s.value(key, default, t)
        if not s.contains(key): s.setValue( key, var)
        syslog.syslog(syslog.LOG_DEBUG,
                      "DEBUG  settingsValue %s, value: %s, type: %s" %
                      (key, var, str(t))
        )
        return var

    @staticmethod
    def setSettingsValue( key, val):
        syslog.syslog(syslog.LOG_DEBUG,
                      "DEBUG  setSettingsValue %s, value: %s" %
                      (key, str(val)))
        s = QSettings()
        s.setValue( key, val)

    sigmap = {
        v:k for k,v in signal.__dict__.items() if re.match(r'^SIG[A-Z12]+$',k)
    }
    def initSignalHandlers(self):
        sigs = [ signal.SIGINT, signal.SIGTERM, signal.SIGUSR1, signal.SIGUSR2 ]
        for s in sigs:
            syslog.syslog(syslog.LOG_DEBUG, "DEBUG  Registering handler for "+
                          self.sigmap[s])
            sig = Signal.create(s,self)
            sig.signal.connect(self.handleSignal)

    def handleSignal(self,signum):
        syslog.syslog(syslog.LOG_INFO, "INFO   Received "+self.sigmap[signum])
        if signum == signal.SIGINT or \
           signum == signal.SIGTERM:
            self.quit()
        elif signum == signal.SIGUSR1:
            self.sigusr1.emit()
        elif signum == signal.SIGUSR2:
            self.sigusr2.emit()

class SettingsValue(QObject):
    valueChanged = pyqtSignal(QVariant)

    def __init__(self, name, val, t, callback=None):
        super(SettingsValue,self).__init__()
        self.name  = name
        self.type = t
        self.val = Application.settingsValue(self.name, val, self.type)
        if callback:
            self.valueChanged.connect(callback)

    def value(self):
        return self.val

    def setValue(self, val):
        if self.val == val:
            return
        self.val = val
        Application.setSettingsValue(self.name, self.val)
        self.valueChanged.emit(self.val)
