import syslog, sys, os, signal, atexit, socket

from PyQt4.Qt import QFile, QDir, QIODevice, QString, QIcon, QApplication
from PyQt4.Qt import QSettings, QTimer

class Application(QApplication):
    timer = QTimer()
    
    def __init__(self, orgname, appname):
        super(Application,self).__init__(sys.argv)
        self.setOrganizationName( orgname)
        self.setApplicationName( appname)
        self.setQuitOnLastWindowClosed( False)
       
    def init(self, argdict):
        Application.setLogLevel( argdict.get('verbosity',0),
                                 argdict.get('daemon', 0))
        Application.setup()
        Application.setThemeFromGtk()

    @staticmethod
    def setLogLevel( level, isDaemon):
        option = syslog.LOG_PID
        if not isDaemon:
            option |= syslog.LOG_PERROR
    
        syslog.openlog( str(QApplication.applicationName()),
                        option, syslog.LOG_USER)
        
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
    def setup():
        atexit.register(Application.cleanup)
        signal.signal( signal.SIGHUP,  Application.hupSignalHandler)
        signal.signal( signal.SIGTERM, Application.termSignalHandler)
        signal.signal( signal.SIGINT,  Application.intSignalHandler)
        Application.timer.start(200)
        Application.timer.timeout.connect(lambda: None)

    @staticmethod
    def setThemeFromGtk():
        f = QFile(QDir.homePath() + "/.gtkrc-2.0");
        if not f.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        while not f.atEnd():
            l = f.readLine().trimmed();
            if l.startsWith("gtk-icon-theme-name="):
                s = QString(l.split('=')[-1]);
                syslog.syslog( syslog.LOG_DEBUG,
                               "DEBUG  setting gtk theme %s" % str(s));
                QIcon.setThemeName(s.remove('"'));
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
                       (key, var.toString()))
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
        except OSError, e:
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
        except OSError, e:
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


    @staticmethod
    def hupSignalHandler( signal, stack):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  caught SIGHUP")
        
    @staticmethod
    def termSignalHandler( signal, stack):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  caught SIGTERM")
        QApplication.quit()
    
    @staticmethod
    def intSignalHandler( signal, stack):
        syslog.syslog( syslog.LOG_DEBUG, "DEBUG  caught SIGINT")
        QApplication.quit()
