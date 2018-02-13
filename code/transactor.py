import socket
import threading
import json
import sys, time
from PyQt5.QtWidgets import QScrollBar, QSplitter, QTableWidgetItem, QTableWidget, QComboBox, QVBoxLayout, QGridLayout, \
    QDialog, QWidget, QPushButton, QApplication, QMainWindow, QAction, QMessageBox, QLabel, QTextEdit, QProgressBar, \
    QLineEdit
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi
import cheese



socketToTracker = []
socketToMembers = []
tracker_port = 9999
member_address = 'localhost'
name = "Transactor"
memberList = []

def MemberToTracker(addr, port, window):
    def sendMsg(sock):
        while True:
            sock.send(bytes(input(""), 'utf-8'))

    def handle(address, port, window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))
        send_server_port(sock)
        socketToTracker.append(sock)
        iThread = threading.Thread(target=sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()
        while True:
            header = sock.recv(1)

            if not header:
                break
            if header == b'\x01':
                size = int.from_bytes(sock.recv(2), byteorder='big')
                data = sock.recv(size)
                window.chat.appendPlainText(data.decode("utf-8"))
            if header == b'\x02':
                size = int.from_bytes(sock.recv(2), byteorder='big')
                data = sock.recv(size)
                for el in json.loads(data):
                    memberList.append(el)
                print(memberList)
                window.chat.appendPlainText("Members List: " + str(memberList))

    def send_server_port(sock):
        sock.send(b'\x03')

    t = threading.Thread(target=handle, args=(addr, port, window,))
    return t

def MemberToMemberClient(addr, port, window):
    def handle(address, port, window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))
        socketToMembers.append(sock)
        while True:
            header = sock.recv(1)
            if not header:
                break

            if header == b'\x04':
                size = sock.recv(2)
                size_int = int.from_bytes(size, byteorder='big')
                msg = sock.recv(size_int)
                print(str(msg, 'utf-8'))
                window.chat.appendPlainText(str(msg, 'utf-8'))

    t = threading.Thread(target=handle, args=(addr, port, window,))
    return t

# Auto create trans after 10secs
# Transactions list contains dict objects of random transactions
def auto_trans():
    def handle():
        pass
    t = threading.Thread(target=handle, args=(addr, port, window,))
    return t

class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("transactor.ui", self)
        self.setWindowTitle(name)
     # buttons
        self.btnGetMemList.clicked.connect(self.reqMemList)
        self.btnConTracker.clicked.connect(self.connectToTracker)
        self.btnConClients.clicked.connect(self.connectToClients)
        self.btnStart.clicked.connect(self.startSending)

    @pyqtSlot()
    def reqMemList(self):
        socketToTracker[0].send(b'\x02')

    @pyqtSlot()
    def connectToClients(self):
        for mem in memberList:
                addr = mem.split(":")
                MemberToMemberClient(addr[0], int(addr[1]), window).start()

    @pyqtSlot()
    def connectToTracker(self):
        MemberToTracker(member_address, tracker_port, window).start()

    @pyqtSlot()
    def startSending(self):
        auto_trans().start()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.exec()
    sys.exit(app.exec_())