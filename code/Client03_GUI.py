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
server_port = 10003
member_address = 'localhost'
member_name = "Member03"
memberList = []


class myCheeses:
    def __init__(self):
        self.stack = []
        self.processed_trans_list = []


def CheeseThread():
    def handle():
        my_blue_cheese = cheese.blue_cheese()
        my_cheeses.stack.append(my_blue_cheese)

        new_trans0 = cheese.new_trans('Member 1', 'Mem 2', 300)
        miner1 = member_name
        reward_amount = cheese.reward

        trans_col_list = cheese.collect_trans(my_cheeses.processed_trans_list, new_trans0, miner1, reward_amount)
        new_mined_json = cheese.cheese_mining(my_cheeses.stack, trans_col_list)
        my_cheeses.stack.append(new_mined_json)

        new_trans1 = cheese.new_trans('Member 2', 'Member 3', 150)
        miner2 = 'Miner 8'

        trans_col_list = cheese.collect_trans(my_cheeses.processed_trans_list, new_trans1, miner2, reward_amount)

        new_mined_json1 = cheese.cheese_mining(my_cheeses.stack, trans_col_list)
        my_cheeses.stack.append(new_mined_json1)

        # cheese.store_cheese_stack(my_cheese_stack, 'cheese_stack.json')
        # print(cheese.load_cheese_stack('cheese_stack.json'))
        print(my_cheeses.stack)

    t = threading.Thread(target=handle)
    return t


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
            data = sock.recv(4096)

            if not data:
                break
            if data[0:1] == b'\x01':
                print(str(data[1:], 'utf-8'))
                window.chat.append(data[1:].decode("utf-8"))
            if data[0:1] == b'\x02':
                # print(str(data,'utf-8'))
                for el in json.loads(data[1:]):
                    memberList.append(el)
                print(memberList)
                window.chat.append("Members List: " + str(memberList))

    def send_server_port(sock):
        sock.send(b'\x01' + bytes(str(server_port), 'utf-8'))

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

    def handler(c, a, window):
        while True:
            data = c.recv(1024)
            # window.chat.append(data.decode('utf-8'))
            if (data[0:1] == b'\x07'):
                new_cheese = json.loads(data[1:])
                window.chat.append(json.dumps(new_cheese))
            if data[0:1] == b'\x05':
                window.chat.append("received request for CS from " + str(a[0]) + ':' + str(a[1]))
                if data[1:].decode('utf-8') == "REQ_CS_LENGTH":
                    cheese_stack_length = str(my_cheeses.stack[-1]["index"])
                    c.send(b'\x05' + b'\x01' + bytes(cheese_stack_length, 'utf-8'))
                elif data[1:].decode('utf-8') == "REQ_CS":
                    cheese_stack_string = json.dumps(my_cheeses.stack)
                    c.send(b'\x05' + b'\x02' + bytes(cheese_stack_string, 'utf-8'))
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
        c.send(b'\x04' + bytes(msg, "utf-8"))

    t = threading.Thread(target=handle, args=(address, port, window))
    return t


def MemberToMemberClient(addr, port, window):
    def handle(address, port, window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))
        socketToMembers.append(sock)
        while True:
            data = sock.recv(4096)
            if not data:
                break

            if data[0:1] == b'\x04':
                print(str(data[1:], 'utf-8'))
                window.chat.append(str(data[1:], 'utf-8'))

            if data[0:1] == b'\x05':  # receive Cheese stack information
                if data[1:2] == b'\x01':  # receive index
                    # print("index received: ", data[2:].decode('utf-8'))
                    # print("current index: ", my_cheeses.stack[-1]["index"])
                    if (int(data[2:].decode('utf-8')) > int(my_cheeses.stack[-1]["index"])):
                        req = "REQ_CS"
                        sock.send(b'\x05' + bytes(req, 'utf-8'))
                        window.chat.append(str(data[2:].decode('utf-8') + "from" + str(address) + ":" + str(port)))
                    else:
                        window.chat.append("don't need to update!")
                if data[1:2] == b'\x02':  # receive cheese stack
                    # need to check if the CS is valid?
                    my_cheeses.stack = json.loads(data[2:])
                    window.chat.append("my new CS: " + json.dumps(my_cheeses.stack))

                pass

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
        self.btnAskCheese.clicked.connect(self.askCheese)
        self.btnReqCS.clicked.connect(self.reqCS)

    @pyqtSlot()
    def reqMemList(self):
        req = "REQ_MEM_LIST"
        socketToTracker[0].send(b'\x02' + bytes(req, 'utf-8'))

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

    @pyqtSlot()
    def sendCheese(self):
        if self.desToSend.text() == "destination":
            window.chat.append("Select destination pls!")
        elif self.desToSend.text() == "AllClients":
            new_mined_block = json.dumps(my_cheeses.stack[-1])
            window.chat.append("sent cheese: " + new_mined_block)
            for s in socketToMembers:
                s.send(b'\x07' + bytes(new_mined_block, 'utf-8'))

    @pyqtSlot()
    def askCheese(self):
        window.chat.append("need to ask for cheese")

    @pyqtSlot()
    def reqCS(self):
        if self.desToSend.text() == "destination":
            window.chat.append("Select destination pls!")
        elif self.desToSend.text() == "AllClients":
            req = "REQ_CS_LENGTH"
            for s in socketToMembers:
                s.send(b'\x05' + bytes(req, 'utf-8'))
        window.chat.append("sent a query for Cheese Stack")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    MemberToMemberServer(member_address, server_port, window).start()
    my_cheeses = myCheeses()
    CheeseThread().start()
    window.exec()
    sys.exit(app.exec_())



