# -*- coding: utf-8 -*- 

import chat_util 
from chat_util import Hall, Room, Player
import socket, threading, select

HOST = ''
PORT = 2233
TCP_PORT = 3115

listen_sock = chat_util.create_socket(('', TCP_PORT))
hall = Hall()
conn_list = []
conn_list.append(listen_sock)

def launchTCPServer():
    while True:
        read_players, write_players, error_socket = select.select(conn_list, [], [])

        for player in read_players:
            #새로운 접속
            if player is listen_sock:
                new_socket, addr_info = player.accept()
                # print('[INFO]클라이언트(%s)가 새롭게 연결 되었습니다.' % (addr_info[0]))
                print('new client: %s' % addr_info[0])
                new_player = Player(new_socket)
                conn_list.append(new_player)
                new_player.socket.sendall(b'connection success\n')

            else:
                msg = player.socket.recv(1024)
                print('msg : ', msg)
                if msg :
                    msg = msg.decode('utf-8')
                    hall.handle_msg(player, msg, conn_list)
                else:
                    player.socket.close()
                    conn_list.remove(player)


if __name__ == "__main__":
    launchTCPServer()

