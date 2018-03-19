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
import queue
from PyQt5.QtGui import QIcon, QPixmap

socketToTracker = []
socketToMembers = []
tracker_port = 9999
server_port = 10003
tracker_address = '172.20.10.8'  #'172.18.250.18'
member_address = '172.20.10.10'#'localhost' #'172.18.250.19'
member_name = "Member03"
memberList = []
my_cheeses_path = "../data/" + member_name + ".json"


class myCheeses:
    def __init__(self):
        self.stack = []
        self.received_trans_list = queue.Queue()
        self.flag = threading.Event()


def CheeseMining(window):
    def handle(window):
        trans_to_mine = []
        while True:
            while len(trans_to_mine) < 3:
                cheese.collect_trans(trans_to_mine, my_cheeses.received_trans_list.get(), member_name)
            val = cheese.cheese_mining(my_cheeses.stack, trans_to_mine, my_cheeses_path, my_cheeses.flag)
            if val is True:
                new_mined_block = json.dumps(my_cheeses.stack[-1])
                bytes_new_mined_block = bytes(new_mined_block, 'utf-8')
                size_data = len(bytes_new_mined_block).to_bytes(2, byteorder='big')
                for s in socketToMembers:
                    s.sendall(b'\x07' + size_data + bytes_new_mined_block)
                print("sent new mined cheese!", " size: ", len(bytes_new_mined_block), " data: ", bytes_new_mined_block)
                window.chat.append("sent new mined cheese!" )
            elif val is False:
                print("it's too late to add mined block to chain!")
            elif val == -1:
                print("cut down!")
            trans_to_mine = []
            my_cheeses.flag.clear()


    t = threading.Thread(target=handle, args=(window,), daemon=True)
    return t

def loadCheeses():
    my_cheeses.stack = cheese.load_cheese_stack(my_cheeses_path)
    print(my_cheeses.stack)


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
        encode_msg = bytes(str(server_port), 'utf-8')
        size = len(encode_msg).to_bytes(2, byteorder='big')
        sock.sendall(b'\x01' + size + encode_msg)

    t = threading.Thread(target=handle, args=(addr, port, window,))
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

    def recvall(sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = sock.recv(1)
            if not packet:
                return None
            data += packet
        return data

    def handler(c, a, window):
        while True:
            header = c.recv(1)
            # window.chat.append(data.decode('utf-8'))
            if (header == b'\x07'):
                size = c.recv(2)
                buf = int.from_bytes(size, byteorder='big')
                ch = recvall(c, buf)#c.recv(buf)
                new_cheese = json.loads(ch)
                if cheese.add_mined_cheese(my_cheeses.stack, new_cheese, my_cheeses_path):
                    my_cheeses.flag.set()
                    print("added new mined cheese: ", new_cheese)
                    window.chat.append("added new mined cheese! " )
                else:
                    print("new mined cheese is not valid")
                    window.chat.append("new mined cheese is not valid")

            if header == b'\x05':
                window.chat.append("received request for CS from " + str(a[0]) + ':' + str(a[1]))
                header2 = c.recv(1)
                if header2 == b'\x01':
                    cheese_stack_length = my_cheeses.stack[-1]["index"].to_bytes(2, byteorder='big')
                    c.sendall(b'\x05' + b'\x01' + cheese_stack_length)
                    print("sent index!")
                elif header2 == b'\x02':
                    cheese_stack_length = c.recv(2)
                    index = int.from_bytes(cheese_stack_length, byteorder='big')
                    cheeses_to_send = []
                    while index <= my_cheeses.stack[-1]["index"]:
                        cheeses_to_send.append(my_cheeses.stack[index])
                        index += 1
                    cheeses_string = json.dumps(cheeses_to_send)
                    bytes_cheese_string = bytes(cheeses_string, 'utf-8')
                    size_data = len(bytes_cheese_string)
                    size_data_bytes = size_data.to_bytes(2, byteorder='big')
                    c.sendall(b'\x05' + b'\x02' + size_data_bytes + bytes_cheese_string)
                    print("sent cheeses!")

            if header == b'\x08':
                size = c.recv(2)
                buf = int.from_bytes(size, byteorder='big')
                data = c.recv(buf)
                transaction = json.loads(data)
                print("received transaction: ", transaction)
                my_cheeses.received_trans_list.put(transaction)
                window.chat.append("received a new transaction")

            if not header:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                connections.remove(c)
                peers.remove(a[0])
                c.close()
                break

    def reply_to_member(c):
        msg = "Connect to " + member_name + " successfully!"
        encode_msg = bytes(msg, "utf-8")
        size = len(encode_msg)
        size_bytes = size.to_bytes(2, byteorder='big')
        c.sendall(b'\x04' + size_bytes + encode_msg)

    t = threading.Thread(target=handle, args=(address, port, window))
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

            if header == b'\x05':  # receive Cheese stack information
                header2 = sock.recv(1)
                if header2 == b'\x01':  # receive index
                    length = sock.recv(2)
                    length_int = int.from_bytes(length, byteorder='big')
                    if cheese.update_cheese_stack(my_cheeses.stack, length_int):
                        next_index = my_cheeses.stack[-1]["index"] + 1
                        next_index_bytes = next_index.to_bytes(2, byteorder='big')
                        sock.sendall(b'\x05' + b'\x02' + next_index_bytes)
                        window.chat.append("need to update from " + str(address) + ":" + str(port))
                    else:
                        window.chat.append("don't need to update from " + str(address) + ":" + str(port))
                if header2 == b'\x02':  # receive cheese stack
                    size = sock.recv(2)
                    size_data = int.from_bytes(size, byteorder='big')
                    data = sock.recv(size_data)
                    cheeses_received = json.loads(data)
                    print(cheeses_received)
                    cheese.add_cheeses(my_cheeses.stack, cheeses_received, my_cheeses_path)
                    window.chat.append("my new CS: " + json.dumps(my_cheeses.stack))

    t = threading.Thread(target=handle, args=(addr, port, window,))
    return t


class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("clientapp.ui", self)
        self.setWindowTitle(member_name)
        # Label
        self.desToSend.hide()
        # combobox
        self.destination.addItem("Tracker")
        self.destination.addItem("Client")
        self.destination.addItem("AllClients")
        self.destination.activated[str].connect(self.onActivated)
        # buttons
        self.ReqMemList.clicked.connect(self.reqMemList)
        self.btnConnect.clicked.connect(self.connectTo)
        self.showMemList.clicked.connect(self.show)
        self.btnSendCheese.clicked.connect(self.sendCheese)
        self.btnShowCS.clicked.connect(self.showCS)
        self.btnReqCS.clicked.connect(self.reqCS)

        # Create backfround
        pixmap = QPixmap('../img/bg.png')
        self.background.setPixmap(pixmap)


    @pyqtSlot()
    def reqMemList(self):
        # req = "REQ_MEM_LIST"
        socketToTracker[0].sendall(b'\x02')

    @pyqtSlot(str)
    def onActivated(self, text):
        self.desToSend.setText(text)

    @pyqtSlot()
    def connectTo(self):
        if self.desToSend.text() == "destination":
            window.chat.append("Select destination pls!")
        elif self.desToSend.text() == "Tracker":
            MemberToTracker(tracker_address, tracker_port, window).start()
        elif self.desToSend.text() == "AllClients":
            for mem in memberList:
                addr = mem.split(":")
                MemberToMemberClient(addr[0], int(addr[1]), window).start()

    @pyqtSlot()
    def show(self):
        window.chat.append(str(memberList))

    @pyqtSlot()
    def sendCheese(self):
        if self.desToSend.text() == "destination":
            window.chat.append("Select destination pls!")
        elif self.desToSend.text() == "AllClients":
            new_mined_block = json.dumps(my_cheeses.stack[-1])
            window.chat.append("sent cheese: " + new_mined_block)
            bytes_new_mined_block = bytes(new_mined_block, 'utf-8')
            size_data = len(bytes_new_mined_block)
            size_data_bytes = size_data.to_bytes(2, byteorder='big')
            for s in socketToMembers:
                s.send(b'\x07' + size_data_bytes + bytes_new_mined_block)

    @pyqtSlot()
    def showCS(self):
        window.chat.append("my new CS: " + json.dumps(my_cheeses.stack))

    @pyqtSlot()
    def reqCS(self):
        if self.desToSend.text() == "destination":
            window.chat.append("Select destination pls!")
        elif self.desToSend.text() == "AllClients":
            for s in socketToMembers:
                s.sendall(b'\x05' + b'\x01')
        window.chat.append("sent a query for Cheese Stack")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    MemberToMemberServer(member_address, server_port, window).start()
    my_cheeses = myCheeses()
    loadCheeses()
    CheeseMining(window).start()
    window.exec()
    sys.exit(app.exec_())
