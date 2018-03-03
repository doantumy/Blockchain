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

tracker_port = 9999
tracker_address = '172.20.10.8'

def Tracker(window):
    connections = []
    client_peers = []
    server_peers = []
    def handle(window):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((tracker_address, tracker_port))
        sock.listen(1)
        print("Tracker running ...")
        while True:
            c, a = sock.accept() #get connection and address from clients
            cThread = threading.Thread(target=handler, args=(c,a, window))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            client_peers.append(str(a[0]) + ':' + str(a[1]))
            window.chat.append(str(a[0]) + ':' + str(a[1]) + " connected")
            print(str(a[0]) + ':' + str(a[1]), "connected")
            print("peers: ", client_peers)
            reply_to_member(c)

    def handler(c, a, window):
        while True:
            header = c.recv(1)

            if (header == b'\x01'):
                size = int.from_bytes(c.recv(2), byteorder='big')
                data = c.recv(size)
                server_member_port = str(data, 'utf-8')
                server_peers.append(str(a[0]) + ':' + server_member_port)
            elif(header == b'\x02'):
                print("received a request about member list")
                peers_to_send = []
                index = []
                for peer in client_peers:
                    p = peer.split(":")
                    if p[0] != str(a[0]) or p[1] != str(a[1]):
                        index.append(client_peers.index(peer))
                # print("peer to send", peers_to_send)
                for i in index:
                    peers_to_send.append(server_peers[i])
                data_string = json.dumps(peers_to_send)
                encode_data = bytes(data_string, "utf-8")
                size = len(encode_data).to_bytes(2, byteorder='big')
                c.sendall(b'\x02' + size + encode_data)
            elif (header == b'\x03'):
                for peer in client_peers:
                    p = peer.split(":")
                    if p[0] == str(a[0]) and p[1] == str(a[1]):
                        client_peers.remove(peer)
                print("peers after removing transactor: ", str(client_peers))
            # for connection in self.connections:
            #     connection.send(data)
            if not header:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                connections.remove(c)
                client_peers.remove(str(a[0]) + ':' + str(a[1]))
                c.close()
                break

    def reply_to_member(c):
        msg = "Connect to Tracker successfully!"
        encode_msg = bytes(msg, "utf-8")
        len_msg = len(encode_msg)
        size = len_msg.to_bytes(2, byteorder='big')
        c.sendall(b'\x01' + size + encode_msg )

    t = threading.Thread(target=handle, args=(window,))
    return t


class Window(QDialog):
    def __init__(self):
        super(Window, self).__init__()
        loadUi("trackerapp.ui", self)
        self.setWindowTitle("Tracker")
    #     self.ReqMemList.clicked.connect(self.reqMemList)
    # @pyqtSlot()
    # def reqMemList(self):
    #     req = "REQ_MEM_LIST"
    #     sockets[0].send(b'\x02'+bytes(req, 'utf-8'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    Tracker(window).start()
    window.exec()
    sys.exit(app.exec_())