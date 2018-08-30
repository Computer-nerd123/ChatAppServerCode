import _thread as thread
import time
from time import gmtime, strftime
import socket
import urllib.request as urllib

allServers = {}
allPasswords = {}
allmsg = {}

def init(conn):
    return conn.recv(10000).decode()

def createNewServer(serverName, serverPassword, username, conn, addr):
    global allPasswords
    
    allServers[str(serverName)] = [(username, conn, addr)]
    allPasswords[str(serverName)] = str(serverPassword)

def addToServer(serverName, username, conn, addr):
    allServers[str(serverName)] += [(username, conn, addr)]

def get(serverName, userName, conn):
    global allmsg
    global allServers
    
    while True:
        try:
            msg = conn.recv(10000).decode()
        except ConnectionResetError:
            print("Clearing old conn from server...")
            conn.close()
            break
            #TODO ^
            
        if msg.lower() == "all_msg":
            try:
                print(allmsg[str(serverName)])
                allTheMsgs = ""
                for x in allmsg[str(serverName)]:
                    allTheMsgs += "From: " + str(x[0]) + " at " + str(x[1]) + ": " + str(x[2]) + "\n"
                print(len(allTheMsgs))
                send(conn, "server|\n" + str(allTheMsgs))
            except KeyError:
                print("No messages yet")
        elif msg.lower() == "who_is_here":
            print(allServers[str(serverName)])
        else:
            #name, timestamp, msg
            try:
                allmsg[str(serverName)] += [(str(userName), str(strftime("%Y-%m-%d %H:%M:%S", gmtime())), str(msg))]
            except KeyError:
                allmsg[str(serverName)] = [(str(userName), str(strftime("%Y-%m-%d %H:%M:%S", gmtime())), str(msg))]
            #send(conn, "Message received!")
            handleGroupSend(serverName, userName, msg)
            print("From " + str(userName) + ": " + str(msg))

def send(conn, msg):
    conn.send(msg.encode())
    
def handleGroupSend(serverName, userName, msg):
    global allServers
    
    print("Sending to: " + str(serverName) + " from: " + str(userName) + "...")
    for x in allServers[str(serverName)]:
        if not (x[0] == userName):
            try:
                x[1].send(str(str(userName) + "|" + str(msg)).encode())
            except OSError:
                #not working yet
                #del allServers[str(serverName)][x]
                print("Remove failed connection")
                
def handleNewConn(serverName, userName, conn, addr):
    get(serverName, userName, conn)
    


pub_ip = urllib.urlopen("https://www.myglobalip.com").read().decode().split('<span class="ip">')[1].split("</span>")[0]
print(pub_ip)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostIP = socket.gethostbyname(socket.gethostname())
print(hostIP)
port = 12345

#s.bind((pub_ip,port))
s.bind((hostIP,port))

threadNum = 0

while True:
    s.listen(0)
    conn,addr = s.accept()
    print(str(addr))
    info = init(conn)
    
    try:
        username = info.split(" ")[0]
        serverInfo = info.split(" ")[1]
        serverName = serverInfo.split(",")[0]
        serverPassword = serverInfo.split(",")[1]
    except IndexError:
        username = "Thread " + str(threadNum)
        serverPassword = False
        
    if not (serverPassword == False):
        #make some sort of login auth
        try:
            if allPasswords[str(serverName)] == serverPassword:
                addToServer(serverName, username, conn, addr)
            else:
                send(conn, "Invalid Passowrd!")
                conn.close()
        except KeyError:
            createNewServer(serverName, serverPassword, username, conn, addr)
        thread.start_new_thread(handleNewConn, (serverName, username, conn, addr, ))
        
    else:
        print("Stranger?")
        
    threadNum += 1

conn.close()
s.close()


