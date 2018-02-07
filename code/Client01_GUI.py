import socket
import threading
import json
import sys, time
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QScrollBar, QSplitter, QTableWidgetItem, QTableWidget, QComboBox, QVBoxLayout, QGridLayout, \
    QDialog, QWidget, QPushButton, QApplication, QMainWindow, QAction, QMessageBox, QLabel, QTextEdit, QProgressBar, \
    QLineEdit
from PyQt5.QtCore import QCoreApplication
from socketserver import ThreadingMixIn
from PyQt5.QtCore import  pyqtSlot
from PyQt5.uic import  loadUi

tcpClientA = None
sockets = []
tracker_port = 9999
server_port = 10001
member_address = 'localhost'
member_name = "Member01"
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
        sockets.append(sock)
        iThread = threading.Thread(target=sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()
        while True:
            data = sock.recv(1024)

            if not data:
                break
            if data[0:1] == b'\x01':
                print(str(data[1:],'utf-8'))
                window.chat.append(data[1:].decode("utf-8"))
            if data[0:1] == b'\x02':
                # print(str(data,'utf-8'))
                for el in json.loads(data[1:]):
                    memberList.append(el)
                print(memberList)
                window.chat.append("Members List: " + str(memberList))

    def send_server_port(sock):
        sock.send(b'\x01' + bytes(str(server_port), 'utf-8'))
    t = threading.Thread(target=handle, args=(addr, port, window, ))
    return t


def MemberToMemberServer(address, port, window):
    connections = []
    peers = []

    def handle(address, port, window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((address, port))
        sock.listen(1)
        print("Member Server running ...")
        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=handler, args=(c, a, window))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            peers.append(str(a[0]) + ':' + str(a[1]))
            window.chat.append(str(a[0]) + ':' + str(a[1]) + "connected")
            print(str(a[0]) + ':' + str(a[1]), "connected")
            print("peers: ", peers)
            reply_to_member(c)

    def handler(c, a, window):
        while True:
            data = c.recv(1024)
            window.chat.append(data.decode('utf-8'))

            # for connection in self.connections:
            #     connection.send(data)
            if not data:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                connections.remove(c)
                peers.remove(a[0])
                c.close()
                break

    def reply_to_member(c):
        msg = "Connect to " + member_name + " successfully!"
        c.send(b'\x03' + bytes(msg, "utf-8"))

    t = threading.Thread(target=handle, args=(address, port, window))
    return t

def MemberToMemberClient(addr, port, window):

    def handle(address, port, window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))

        while True:
            data = sock.recv(1024)
            if not data:
                break

            if data[0:1] == b'\x03':
                print(str(data[1:], 'utf-8'))
                window.chat.append(str(data[1:], 'utf-8'))

            if data[0:1] == b'\x01':
                # print(str(data,'utf-8'))
                data_arr = json.loads(data[1:])
                print(data_arr)
    t = threading.Thread(target=handle, args=(addr, port, window, ))
    return t

class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("clientapp.ui", self)
        self.setWindowTitle(member_name)

        self.ReqMemList.clicked.connect(self.reqMemList) #button

        self.destination.addItem("Tracker")          #combobox
        self.destination.addItem("Client")
        self.destination.addItem("AllClients")
        self.destination.activated[str].connect(self.onActivated)

        self.btnConnect.clicked.connect(self.connectTo)
        self.desToSend.hide()
        self.showMemList.clicked.connect(self.show)

    @pyqtSlot()
    def reqMemList(self):
        req = "REQ_MEM_LIST"
        sockets[0].send(b'\x02'+bytes(req, 'utf-8'))

    @pyqtSlot(str)
    def onActivated(self, text):
        self.desToSend.setText(text)


    @pyqtSlot()
    def connectTo(self):
        if self.desToSend.text() == "destination":
            window.chat.append("Select destination pls!")
        elif self.desToSend.text() == "Tracker":
            MemberToTracker(member_address, tracker_port, window).start()
        elif self.desToSend.text() == "AllClients":
            for mem in memberList:
                addr = mem.split(":")
                MemberToMemberClient(addr[0], int(addr[1]), window).start()

    @pyqtSlot()
    def show(self):
        window.chat.append(str(memberList))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    MemberToMemberServer(member_address, server_port, window).start()
    window.exec()
    sys.exit(app.exec_())



