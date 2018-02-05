import socket
import threading
import json

tracker_port = 9999
server_port = 10002
member_address = 'localhost'


def MemberToTracker(addr, port):
    def sendMsg(sock):
        while True:
            sock.send(bytes(input(""), 'utf-8'))

    def handle(address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))
        send_server_port(sock)
        iThread = threading.Thread(target=sendMsg, args=(sock,))
        iThread.daemon = True
        iThread.start()
        while True:
            data = sock.recv(1024)
            if not data:
                break
            if data[0:1] == b'\x01':
                print(str(data[1:], 'utf-8'))
            if data[0:1] == b'\x02':
                # print(str(data,'utf-8'))
                data_arr = json.loads(data[1:])
                print(data_arr)
                for element in data_arr:
                    addr = element.split(":")
                    MemberToMemberClient(addr[0], int(addr[1])).start()

    def send_server_port(sock):
        sock.send(b'\x01' + bytes(str(server_port), 'utf-8'))

    t = threading.Thread(target=handle, args=(addr, port,))
    return t

def MemberToMemberServer(address, port):
    connections = []
    peers = []

    def handle(address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((address, port))
        sock.listen(1)
        print("Member Server running ...")
        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            peers.append(str(a[0]) + ':' + str(a[1]))
            print(str(a[0]) + ':' + str(a[1]), "connected")
            print("peers: ", peers)
            reply_to_member(c)

    def handler(c, a):
        while True:
            data = c.recv(1024)
            if (str(data, 'utf-8') == "REQ_MEM_LIST"):
                # c.send(bytes(str(self.peers), "utf-8"))
                data_string = json.dumps(peers)
                c.send(b'\x02' + bytes(data_string, "utf-8"))

            # for connection in self.connections:
            #     connection.send(data)
            if not data:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                connections.remove(c)
                peers.remove(a[0])
                c.close()
                break

    def reply_to_member(c):
        msg = "Connect to Member02 successfully!"
        c.send(b'\x03' + bytes(msg, "utf-8"))

    t = threading.Thread(target=handle, args=(address, port))
    return t



def MemberToMemberClient(addr, port):

    def handle(address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address, port))

        while True:
            data = sock.recv(1024)
            if not data:
                break

            if data[0:1] == b'\x03':
                print(str(data[1:], 'utf-8'))

            if data[0:1] == b'\x01':
                # print(str(data,'utf-8'))
                data_arr = json.loads(data[1:])
                print(data_arr)
    t = threading.Thread(target=handle, args=(addr, port,))
    return t

# member_to_tracker = MemberToTracker('localhost')
MemberToTracker(member_address, tracker_port).start()
MemberToMemberServer(member_address, server_port).start()