# -*- coding: utf-8 -*- 

from flask import Flask, g
from flask import request as req
import chat_util 
from chat_util import Hall, Room, Player
import socket, threading, select

app = Flask(__name__)

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
                if msg :
                    msg = msg.decode()
                    hall.handle_msg(player, msg, conn_list)
                else:
                    player.socket.close()
                    conn_list.remove(player)

@app.route("/")
def index():
    return "Server running at 2323 port \n TCP Server running at 3115 port"

@app.route("/join", methods=["POST"])
def join():
    token = req.form['token']
    return "success"

@app.route("/send", methods=["POST"])
def send():
    msg = req.form['msg']
    g.server_conn.sendAll(msg.encode())
    return msg

if __name__ == "__main__":
    t = threading.Thread(target=launchTCPServer)
    t.daemon = True
    t.start()
    app.run(host=HOST, port=PORT)

