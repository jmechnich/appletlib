import re, syslog, sys, os, signal, atexit, socket, argparse

from appletlib.posixsignal import Signal

from PyQt4.Qt import QFile, QDir, QIODevice, QIcon, QApplication
from PyQt4.Qt import QSettings, QTimer, pyqtSignal

class Application(QApplication):
    timer = QTimer()
    sigusr1 = pyqtSignal()
    sigusr2 = pyqtSignal()
    
    def __init__(self, orgname, appname):
        super(Application,self).__init__(sys.argv)
        self.setOrganizationName( orgname)
        self.setApplicationName( appname)
        self.setQuitOnLastWindowClosed( False)
       
    def init(self, argdict):
        Application.setLogLevel( argdict.get('verbosity',0),
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
        parser.add_argument( '-d', '--daemon',
                             help='run as daemon', action="store_true")
        parser.add_argument( '-v', '--verbosity', type=int, default=0,
                             help='select verbosity (default: 0)')
        args = parser.parse_args()
        return args

    @staticmethod
    def setLogLevel( level, isDaemon):
        option = syslog.LOG_PID
        if not isDaemon:
            option |= syslog.LOG_PERROR
    
        syslog.openlog( str(QApplication.applicationName()),
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
        syslog.syslog( syslog.LOG_INFO, "INFO   logging to syslog")

    @staticmethod
    def cleanup():
        syslog.syslog( syslog.LOG_INFO, "INFO   shutting down");
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
                syslog.syslog( syslog.LOG_DEBUG,
                               "DEBUG  setting gtk theme %s" % str(s));
                QIcon.setThemeName(s.remove('"'))
                break

    @staticmethod
    def settingsValue( key, default):
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  settingsValue %s, default: %s" %
                       (key, str(default)))
        s = QSettings()
        var = s.value(key, default)
        if not s.contains(key): s.setValue( key, var)
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  settingsValue %s, value:   %s" %
                       (key, var)
        )
        return var

    @staticmethod
    def setSettingsValue( key, val):
        syslog.syslog( syslog.LOG_DEBUG,
                       "DEBUG  setSettingsValue %s, value: %s" %
                       (key, str(val)))
        s = QSettings()
        s.setValue( key, val)

    @staticmethod
    def detach():
        stdin  = '/dev/null'
        stdout = '/dev/null'
        stderr = '/dev/null'
        
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(stdin, 'r')
        so = file(stdout, 'a+')
        se = file(stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    sigmap = { v:k for k,v in signal.__dict__.items() if re.match(r'^SIG[A-Z12]+$',k)}
    def initSignalHandlers(self):
        sigs = [ signal.SIGINT, signal.SIGTERM, signal.SIGUSR1, signal.SIGUSR2 ]
        for s in sigs:
            syslog.syslog( syslog.LOG_DEBUG, "DEBUG  Registering handler for "+
                           self.sigmap[s])
            sig = Signal.create(s,self)
            sig.signal.connect(self.handleSignal)

    def handleSignal(self,signum):
        syslog.syslog( syslog.LOG_INFO, "INFO   Received "+self.sigmap[signum])
        if signum == signal.SIGINT or \
           signum == signal.SIGTERM:
            self.quit()
        elif signum == signal.SIGUSR1:
            self.sigusr1.emit()
        elif signum == signal.SIGUSR2:
            self.sigusr2.emit()
