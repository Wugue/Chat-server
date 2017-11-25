#Skeleton code taken and modified from http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php

import sys
import socket
import select
from utils import *
 #TEST
def client(argv):
    buff = {}
    host = sys.argv[2]
    port = int(sys.argv[3])
    etc = ''
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
        msg = sys.argv[1]
        x = 200 - len(msg)
        for i in range(x):
            msg = msg + ' '
        s.send(msg)
    except :
        print CLIENT_CANNOT_CONNECT.format(host, port)
        sys.exit()
     
    sys.stdout.write('[Me] '); sys.stdout.flush()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [], 0)
        for sock in ready_to_read:             
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(MESSAGE_LENGTH*2)
                #print '\n' + data + '\n'
                if not data :
                    print '\n' + CLIENT_SERVER_DISCONNECTED.format(host, port)
                    sys.exit()
                else :
                    try:
                        #print data
                        #THIS IS BROKEN
                        i = 0
                        while not data[i] == ']':
                            i = i + 1
                        i = i + 1
                        name = data[:i]
                        content = data[i:]
                        if name in buff:
                            buff[name] = buff[name] + content
                        else:
                            buff[name] = content
                        #print 'rec' + str(len(buff[name])) + content + '\n'
                        if buff[name].rstrip() == '':
                            buff[name] == ''
                        if len(buff[name]) >= 200:
                            sys.stdout.write((name + ' ' + buff[name]).rstrip() + '\n')
                            buff[name] = ''
                            sys.stdout.write('[Me] '); sys.stdout.flush()
                    except:
                        if data == CLIENT_WIPE_ME:
                            sys.stdout.write(data)
                            #sys.stdout.write('[Me] '); sys.stdout.flush()
                        else:
                            etc = etc + data
                            #if etc.rstrip() == '':
                                #etc = ''
                            if len(etc) >= 200:
                                sys.stdout.write(etc.rstrip() + '\n')
                                etc = ''
                                sys.stdout.write('[Me] '); sys.stdout.flush()
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                msg = msg[:-1]
                x = 200 - len(msg)
                for i in range(x):
                    msg = msg + ' '
                #print 'sent' + str(len(msg)) + '\n'
                s.send(msg)
                sys.stdout.write('[Me] '); sys.stdout.flush() 

if __name__ == "__main__":
    client(sys.argv)