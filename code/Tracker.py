import socket
import threading
import json

class Tracker:
    connections = []
    client_peers = []
    server_peers = []
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 9999))
        sock.listen(1)
        print("Tracker running ...")
        while True:
            c, a = sock.accept() #get connection and address from clients
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.client_peers.append(str(a[0]) + ':' + str(a[1]))
            print(str(a[0]) + ':' + str(a[1]), "connected")
            print("peers: ", self.client_peers)
            self.reply_to_member(c)

    def handler(self, c, a):
        while True:
            data = c.recv(1024)
            if (data[0:1] == b'\x01'):
                server_member_port = str(data[1:], 'utf-8')
                self.server_peers.append(str(a[0]) + ':' + server_member_port)
            if (str(data, 'utf-8') == "REQ_MEM_LIST"):
                # c.send(bytes(str(self.peers), "utf-8"))
                peers_to_send = []
                index = []
                for peer in self.client_peers:
                    p = peer.split(":")
                    if p[0] != str(a[0]) or p[1] != str(a[1]):
                        index.append(self.client_peers.index(peer))
                # print("peer to send", peers_to_send)
                for i in index:
                    peers_to_send.append(self.server_peers[i])
                data_string = json.dumps(peers_to_send)
                c.send(b'\x02' + bytes(data_string, "utf-8"))

            # for connection in self.connections:
            #     connection.send(data)
            if not data:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break

    def reply_to_member(self, c):
        msg = "Connect to Tracker successfully!"
        c.send(b'\x01' + bytes(msg, "utf-8"))


tracker = Tracker()