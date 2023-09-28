import socket
from threading import Thread

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002

client_sockets = dict()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

connected_players = dict()
players_in_game = list()
players_ready_to_battle = list()
players_in_battle = dict()


def func_200(msg: str, cs=None):
    print(type(cs))
    client_sockets[cs] = msg.split(':')[1]
    connected_players[msg.split(':')[1]] = cs


def func_210(msg: str, cs=None):
    text = "215:Достпуные игркои:\n"
    for player in connected_players:
        if player != msg.split(':')[1]:
            text += player
            text += '\n'
    connected_players[msg.split(':')[1]].send(text.encode())


def func_220(msg: str, cs=None):
    player_1_socket = connected_players[msg.split(':')[1]]
    player_2_socket = connected_players[msg.split(':')[2]]
    battle_pair = {msg.split(':')[1]: player_1_socket, msg.split(':')[2]: player_2_socket}
    players_in_game.append(battle_pair)
    for player in battle_pair.keys():
        if player == msg.split(':')[1]:
            connected_players[player].send(f"230:{msg.split(':')[2]}".encode())
        else:
            connected_players[player].send(f"230:{msg.split(':')[1]}".encode())


def func_240(msg: str, cs=None):
    players_ready_to_battle.append(msg.split(':')[1])
    for cur_pair in players_in_game:
        if msg.split(':')[1] in cur_pair.keys():
            pair_keys = list(cur_pair.keys())
            if all([pair_keys[0] in players_ready_to_battle,
                    pair_keys[1] in players_ready_to_battle]):
                players_in_battle[pair_keys[0]] = cur_pair
                players_in_battle[pair_keys[1]] = cur_pair
                connected_players[pair_keys[0]].send(f"250:{pair_keys[1]}".encode())
                connected_players[pair_keys[1]].send(f"250:{pair_keys[0]}".encode())
            else:
                connected_players[msg.split(':')[1]].send(f"245:".encode())


def func_300(msg: str, cs=None):
    player_id = msg.split(':')[2]
    print(players_in_battle[player_id])
    cur_pair = players_in_battle[player_id]
    for player_enemy in cur_pair.keys():
        if player_enemy != player_id:
            connected_players[player_enemy].send(
                f"310:{msg.split(':')[1]}".encode())


def func_320(msg: str, cs=None):
    player_id = msg.split(':')[2]
    cur_pair = players_in_battle[player_id]
    for player_enemy in cur_pair.keys():
        if player_enemy != player_id:
            connected_players[player_enemy].send(f"340:{msg.split(':')[1]}".encode())


def func_330(msg: str, cs=None):
    player_id = msg.split(':')[2]
    cur_pair = players_in_battle[player_id]
    for player_enemy in cur_pair.keys():
        if player_enemy != player_id:
            connected_players[player_enemy].send(f"350:{msg.split(':')[1]}".encode())


code_dict = {
    "200": func_200,
    "210": func_210,
    "220": func_220,
    "240": func_240,
    "300": func_300,
    "320": func_320,
    "330": func_330,
}


def listen_for_client(cs):
    while True:
        try:
            msg = cs.recv(1024).decode()
            print(msg)
        except Exception as e:
            print(f"[!] Error: {e}")
            cl_id = client_sockets[cs]
            del connected_players[cl_id]
            return
        else:
            try:
                code_dict[msg.split(':')[0]](msg, cs=cs)
            except KeyError:
                pass


while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    t = Thread(target=listen_for_client, args=(client_socket,))
    t.daemon = True
    t.start()
