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
import random


socketToTracker = []
socketToMembers = []
tracker_port = 9999
tracker_address = 'localhost'#'172.18.250.18'
name = "Transactor"
memberList = []

class flag():
    def __init__(self):
        self.sending = False


def MemberToTracker(addr, port, window):
    def sendMsg(sock):
        while True:
            sock.sendall(bytes(input(""), 'utf-8'))

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
                window.chat.append(data.decode("utf-8"))
            if header == b'\x02':
                size = int.from_bytes(sock.recv(2), byteorder='big')
                data = sock.recv(size)
                for el in json.loads(data):
                    if el not in memberList:
                        memberList.append(el)
                print(memberList)
                window.chat.append("Members List: " + str(memberList))

    def send_server_port(sock):
        sock.sendall(b'\x03')

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
                window.chat.append(str(msg, 'utf-8'))

    t = threading.Thread(target=handle, args=(addr, port, window,))
    return t


# Auto create trans after 10secs
# Transactions will be created automatically based on the number of transaction provided until it is 0
# Sender remains the same, receiver will be randomly selected among the list of receiver (public keys list)
def auto_trans(number_of_transaction, window):
    def handle(number_of_transaction, window, delay=5):
        while True:
            if fg.sending:
                i = 0
                while i <= number_of_transaction - 1:
                    if fg.sending == False:
                        break
                    keys_sender = cheese.key_generator()
                    private_key_sender = keys_sender[0]
                    public_key_sender = keys_sender[1]

                    keys_receiver = cheese.key_generator()
                    public_key_receiver = keys_receiver[1]

                    random_amount = random.randint(1, 10)
                    new_tran = cheese.new_trans(private_key_sender, public_key_sender, public_key_receiver, random_amount)
                    new_tran_str = json.dumps(new_tran)
                    window.chat.append(new_tran_str)
                    encode_trans = bytes(new_tran_str, 'utf-8')
                    size_data = len(encode_trans).to_bytes(2, byteorder='big')
                    for sock in socketToMembers:
                        sock.sendall(b'\x08' + size_data + encode_trans)

                    time.sleep(delay)
                    i += 1
    t = threading.Thread(target=handle, args=(number_of_transaction, window))
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
        self.btnStop.clicked.connect(self.stopSending)
    @pyqtSlot()
    def reqMemList(self):
        socketToTracker[0].sendall(b'\x02')

    @pyqtSlot()
    def connectToClients(self):
        for mem in memberList:
                addr = mem.split(":")
                MemberToMemberClient(addr[0], int(addr[1]), window).start()

    @pyqtSlot()
    def connectToTracker(self):
        MemberToTracker(tracker_address, tracker_port, window).start()

    @pyqtSlot()
    def startSending(self):
        fg.sending = True
        print("start sending transactions")

    @pyqtSlot()
    def stopSending(self):
        fg.sending = False
        print("stop sending transactions")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    fg = flag()
    auto_trans(100, window).start()
    window.exec()
    sys.exit(app.exec_())