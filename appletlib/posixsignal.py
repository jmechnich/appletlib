import signal
import socket
import syslog

from PyQt5.QtCore import QObject, QSocketNotifier, pyqtSignal

class Signal(QObject):
    signal = pyqtSignal(int)
    fds = {}
    
    def __init__(self, signum, parent):
        super(Signal,self).__init__(parent)
        self.signum = signum
        self.sn = None
        self.fd = [None,None]
        if self.setupHandler() < 0:
            return

        self.sn = QSocketNotifier(
            self.fd[1].fileno(), QSocketNotifier.Read, parent)
        self.sn.activated.connect(self.handleSignal)

    def __del__(self):
        #signal.signal( self.signum, signal.SIG_DFL)
        if self.signum in Signal.fds:
            Signal.fds.pop(self.signum)
        if self.fd[0] is not None:
            self.fd[0].close()
        if self.fd[1] is not None:
            self.fd[1].close()
        #super(Signal,self).__del__()

    @staticmethod
    def create(signum, parent):
        syslog.syslog(
            syslog.LOG_DEBUG, "DEBUG  creating Signal instance for %d" % signum)
        if signum in Signal.fds:
            if Signal.fds[signum].sn:
                Signal.fds[signum].sn.deleteLater()
            del(Signal.fds[signum])
        return Signal(signum,parent)
    
    def handleSignal(self):
        syslog.syslog(
            syslog.LOG_DEBUG, "DEBUG  handling signal %d" % self.signum)
        self.sn.setEnabled(False)
        self.fd[1].recv(1)
        self.signal.emit(self.signum)
        self.sn.setEnabled(True)

    def setupHandler(self):
        syslog.syslog(syslog.LOG_DEBUG,
                      "DEBUG  setting up handler for signal %d" % self.signum)
        self.fd = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        if not self.fd:
            return -1
        Signal.fds[self.signum] = self
        signal.signal(self.signum, self.handler)
        signal.siginterrupt(self.signum, False)
        return 0

    @staticmethod
    def handler(signum, frame):
        syslog.syslog(syslog.LOG_DEBUG, "DEBUG  handling signal %d" % signum)
        Signal.fds[signum].fd[0].send(bytes([1]))
