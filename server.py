#Skeleton code taken and modified from http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php

import sys
import socket
import select
from utils import *

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = MESSAGE_LENGTH
CHANNELS = []
PORT = None
CLIENTNAMES = {}
CLIENTCHANNELS = {}
SOCKETNAMES = {}
SOCKETETC = {}

def server(argv):
    PORT = int(argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", PORT))
    server_socket.listen(10)
    SOCKET_LIST.append(server_socket)

    while 1:
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
             
            # a message from a client, not a new connection
            else:
                name = sock
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER*2)
                    if data:
                        # there is something in the socket
                        if name not in CLIENTNAMES:
                            if name not in SOCKETNAMES:
                                SOCKETNAMES[name] = data
                            else:
                                SOCKETNAMES[name] = SOCKETNAMES[name] + data
                            if len(SOCKETNAMES[name]) >= 200:
                                CLIENTNAMES[name] = SOCKETNAMES[name].rstrip()
                                SOCKETNAMES.pop(name)
                        else:
                            if data[0] == '/' or name in SOCKETETC:
                                if name not in SOCKETETC:
                                    SOCKETETC[name] = data
                                else:
                                    SOCKETETC[name] = SOCKETETC[name] + data
                                if len(SOCKETETC[name]) >= 200:
                                    data = SOCKETETC[name]
                                    SOCKETETC.pop(name)
                                    if data[:8] == '/create ':
                                        if data[8:].rstrip() == '':
                                            sendbuff(sock, "\r" + SERVER_CREATE_REQUIRES_ARGUMENT + '\n')
                                        elif data[8:].rstrip() in CHANNELS:
                                            sendbuff(sock, "\r" + SERVER_CHANNEL_EXISTS.format(data[8:].rstrip()) + '\n')
                                        else:
                                            if name in CLIENTCHANNELS:
                                                try:
                                                    broadcast(server_socket, sock, "\r" + SERVER_CLIENT_LEFT_CHANNEL.format(CLIENTNAMES[name]) + '\n', CLIENTCHANNELS[name])
                                                except:
                                                    pass
                                            CHANNELS.append(data[8:].rstrip())
                                            CLIENTCHANNELS[name] = data[8:].rstrip()
                                            broadcast(server_socket, sock, "\r" + SERVER_CLIENT_JOINED_CHANNEL.format(CLIENTNAMES[name])+ '\n', CLIENTCHANNELS[name])
                                    elif data[:7] == '/create':
                                        sendbuff(sock, "\r" + SERVER_CREATE_REQUIRES_ARGUMENT + '\n')
                                    elif data.rstrip() == '/list':
                                        if CHANNELS:
                                            #sendbuff(sock, CLIENT_WIPE_ME)
                                            sock.send(CLIENT_WIPE_ME)
                                        for channel in CHANNELS:
                                            temp = ''
                                            for i in range(3000):
                                                temp = temp + ' '
                                            sock.send(CLIENT_WIPE_ME)
                                            sendbuff(sock, "\r" + channel)
                                    elif data.rstrip() == '/join':
                                        sendbuff(sock, "\r" + SERVER_JOIN_REQUIRES_ARGUMENT + '\n')
                                    elif data[0:6] == '/join ':
                                        if data[6:].rstrip() in CHANNELS:
                                            if not (name in CLIENTCHANNELS and CLIENTCHANNELS[name] == data[6:].rstrip()):
                                                if name in CLIENTCHANNELS:
                                                    broadcast(server_socket, sock, "\r" + SERVER_CLIENT_LEFT_CHANNEL.format(CLIENTNAMES[name]) + '\n', CLIENTCHANNELS[name])
                                                CLIENTCHANNELS[name] = data[6:].rstrip()
                                                broadcast(server_socket, sock, "\r" + SERVER_CLIENT_JOINED_CHANNEL.format(CLIENTNAMES[name])+ '\n', CLIENTCHANNELS[name])
                                        else:
                                            sendbuff(sock, "\r" + SERVER_NO_CHANNEL_EXISTS.format(data[6:].rstrip()) + '\n')
                                    else:
                                        sendbuff(sock, "\r" + SERVER_INVALID_CONTROL_MESSAGE.format(data.rstrip()) + '\n')
                            else:
                                if name in CLIENTCHANNELS:
                                    temp = ''
                                    for i in range(3000):
                                        temp = temp + ' '
                                    broadcastMessage(server_socket, sock, "\r" + '[' + CLIENTNAMES[name] + ']' + data, CLIENTCHANNELS[name])
                                else:
                                    sendbuff(sock, "\r" + SERVER_CLIENT_NOT_IN_CHANNEL + '\n')
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "\r" + SERVER_CLIENT_LEFT_CHANNEL.format(CLIENTNAMES[name]), CLIENTCHANNELS[name])
                        CLIENTNAMES.pop(name)
                        CLIENTCHANNELS.pop(name)

                # exception 
                except:
                    continue

    server_socket.close()

def broadcastMessage (server_socket, sock, message, channel):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock and CLIENTCHANNELS[socket] == channel :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

def broadcast (server_socket, sock, message, channel):
    x = 200 - len(message)
    for i in range(x):
        message = message + ' '
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock and CLIENTCHANNELS[socket] == channel :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
def sendbuff(sock, message):
    x = 200 - len(message)
    for i in range(x):
        message = message + ' '
    sock.send(message)


if __name__ == "__main__":
    server(sys.argv)