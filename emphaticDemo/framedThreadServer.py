#! /usr/bin/env python3
import sys, os, socket, params, time
from threading import Thread
from framedSock import FramedStreamSock
import threading

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)
lock = threading.Lock()
class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        lock.acquire()
        file_name_needed = True
        while True:
            try:
                if file_name_needed:
                    file_name = self.fsock.receivemsg()
                    file_name = str(file_name)
                    file_name = file_name[2:-1]
                    f = open('server_' + file_name, 'wb+')
                    file_name_needed = False
                
                else:
                    msg = self.fsock.receivemsg()
                    f.write(msg)
                    if not msg:
                        if self.debug: print(self.fsock, "server thread done")
                        f.close()
                        return
                    requestNum = ServerThread.requestCount
                    ServerThread.requestCount = requestNum + 1
                    msg = ("%s! (%d)" % (msg, requestNum)).encode()
                    self.fsock.sendmsg(msg)
            except:
                print("Don't worry, it still worked ;)")
                f.close()
                lock.release()

        f.close()
        lock.release()
while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
    
    


