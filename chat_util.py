# -*- coding: utf-8 -*- 

import socket, pdb, uuid
import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')


MAX_CLIENTS = 30
PORT = 3115
QUIT_STRING = '<$quit$>'


def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(('', PORT))
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

class Hall:
    def __init__(self):
        self.rooms = {} # {room_name: Room}
        self.room_player_map = {} # {playerName: roomName}

    def welcome_new(self, new_player):
        new_player.socket.sendall(b'Welcome to pychat.\nPlease tell us your name:\n')

    def list_rooms(self, player):
        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [<join> room_name] to create a room.\n'
            player.socket.sendall(msg.encode('utf-8'))
        else:
            msg = 'Listing current rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].players)) + " player(s)\n"
            player.socket.sendall(msg.encode('utf-8'))

    def handle_msg(self, player, msg, conn_list):
        
        print(player.name + " says: " + msg[:len(msg) - 1] + " in " + player.now_room)
        # set name
        # query: #name <name>
        if "#name" in msg:
            # msg = #init# <name>
            name = msg.split()[1]
            player.name = name.encode('utf-8')
            print("New connection from:", player.name)
            player.socket.sendall(b'hello ' + name.encode('utf-8') + b'\n')

        #make room
        #query: #make <room_id> <room_name>
        elif "#make" in msg:
            if len(msg.split()) >= 3:
                room_id = msg.split()[1]
                room_name = msg.split()[2]
                new_room = Room(room_id, room_name)
                self.rooms[new_room.id] = new_room
                msg = b'success '+b'make room id='+new_room.id.encode('utf-8')+b'\n'
                player.socket.sendall(msg)

            else:
                player.socket.sendall(b'error')
        # reg room
        # query: #reg <room_id>
        elif "#reg" in msg:
            if len(msg.split()) >= 2:
                room_id = msg.split()[1]
                self.rooms[room_id].players.append(player)
                msg = player.name.encode('utf-8') + b' regist in ' + room_id.encode('utf-8') + b'\n'
                print(player.name, 'regist in', room_id)
                self.rooms[room_id].broadcast(player, msg)

        # join room
        # query: #join <room_id>
        elif "#join" in msg:
            if len(msg.split()) >= 2:
                room_id = msg.split()[1]
                if player not in self.rooms[room_id].players:
                    self.rooms[room_id].players.append(player)
                player.now_room = room_id
                print("%s join %s" % (player.name, player.now_room))
                self.rooms[player.now_room].welcome_new(player)
            else:
                player.socket.sendall(b'please join romm')

        # return chating room list
        elif "#list" in msg:
            self.list_rooms(player) 

        # leave room but remain
        elif "#leave" in msg:
            player.now_room = "hall"

        # delete on current room
        elif "#del_room" in msg:
            self.rooms[player.now_room].remove_player(player)
            player.now_room = "hall"

        # disconnect socket
        elif "#quit" in msg:
            player.socket.sendall(QUIT_STRING.encode())
            self.remove_player(player)

        elif "#ai" in msg:
            now = datetime.datetime.now()
            pre = 'ai/' + now.strftime('%Y-%m-%d %H:%M:%S:') + '/'
            re = "두 분 모두 안드로이드 개발자시 군요? 혹시 Kotlin에 대해 아시나요??"
            self.rooms[player.now_room].broadcast(player, pre.encode('utf-8') + re.encode('utf-8'))

        else:
            # check if in a room or not first
            if player.now_room != "hall":
                now = datetime.datetime.now()
                pre = 'msg/'+now.strftime('%Y-%m-%d %H:%M:%S:')+'/'+player.name + '/'

                self.rooms[player.now_room].broadcast(player, pre.encode('utf-8') +  msg.encode())
            else:
                # msg = 'You are currently not in any room! \n' \
                #    + 'Use [<list>] to see available rooms! \n' \
                #    + 'Use [<join> room_name] to join a room! \n'
                player.socket.sendall(b'please join room\n')
    
    def remove_player(self, player):
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("Player: " + player.name + " has left\n")

    
class Room:
    def __init__(self, id, name):
        self.players = [] # a list of sockets
        self.name = name
        self.id = id

    def welcome_new(self, from_player):
        msg = self.id + " welcomes: " + from_player.name + '\n'
        for player in self.players:
            player.socket.sendall(msg.encode())
    
    def broadcast(self, from_player, msg):
        # msg = from_player.name.encode() + b":" + msg
        for player in self.players:
            player.socket.sendall(msg)

    def remove_player(self, player):
        self.players.remove(player)
        leave_msg = player.name.encode('utf-8') + b"has left the room\n"
        self.broadcast(player, leave_msg)

class Player:
    def __init__(self, socket, name = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.now_room = "hall"

    def fileno(self):
        return self.socket.fileno()
