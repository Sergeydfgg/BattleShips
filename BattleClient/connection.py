import socket
from threading import Thread
from datetime import datetime
from Player import *
import re

SERVER_HOST = "127.0.0.1" #127.0.0.1
SERVER_PORT = 5002
separator_token = "<SEP>"

s = socket.socket()

new_player = Player()


def func_215(message: str):
    print(message)


def func_230(message: str):
    new_player.enemy_id = message.split(':')[1]
    new_player.status = 'prepare'
    new_player.show_planes()
    new_player.place_ship()
    new_player.show_planes()
    s.send(f"240:{new_player.player_id}".encode())


def func_245(message: str):
    print('Ожидайте...')
    new_player.status = 'in_game:wait'


def func_250(message: str):
    print('Игра началась')
    if new_player.status != 'in_game:wait':
        new_player.status = 'in_game'
    else:
        pass


def func_310(message: str):
    cur_move = message.split(':')[1]
    if len(cur_move) > 2:
        cur_col = int(cur_move[1] + cur_move[2])
    else:
        cur_col = int(cur_move[1])
    letter_change = {let.strip(): ind + 1 for ind, let in enumerate(new_player.player_plane[0][2:])}
    if tuple((letter_change[cur_move[0]], int(cur_col))) in new_player.ship_cells:
        s.send(f"320:{cur_move}:{new_player.player_id}".encode())
        print('Противник сделал ход')
        move_pair = tuple((letter_change[cur_move[0]], int(cur_col)))
        print(move_pair)
        new_player.dead_cells.append(move_pair)
        new_player.ship_cells.remove(move_pair)
        if not new_player.ship_cells:
            print('Вы прогирали')
        else:
            new_player.show_planes()
            new_player.status = 'in_game'
    else:
        s.send(f"330:{cur_move}:{new_player.player_id}".encode())
        print('Противник сделал ход')
        move_pair = tuple((letter_change[cur_move[0]], int(cur_col)))
        if move_pair[1] < 10 and move_pair[0] == 1:
            new_player.player_plane[cur_col][move_pair[0]] = ' [O]'
        else:
            new_player.player_plane[cur_col][move_pair[0]] = '[O]'
        new_player.show_planes()
        new_player.status = 'in_game'


def func_340(message: str):
    print('Ранил')
    cur_move = message.split(':')[1]
    if len(cur_move) > 2:
        cur_col = int(cur_move[1] + cur_move[2])
    else:
        cur_col = int(cur_move[1])
    letter_change = {let.strip(): ind + 1 for ind, let in enumerate(new_player.player_plane[0][2:])}
    move_pair = tuple((letter_change[cur_move[0]], int(cur_col)))
    if move_pair[1] < 10 and move_pair[0] == 1:
        new_player.enemy_plane[cur_col][move_pair[0]] = ' [X]'
    else:
        new_player.enemy_plane[cur_col][move_pair[0]] = '[X]'
    new_player.show_planes()
    new_player.status = 'in_game:wait'


def func_350(message: str):
    print('Мимо')
    cur_move = message.split(':')[1]
    if len(cur_move) > 2:
        cur_col = int(cur_move[1] + cur_move[2])
    else:
        cur_col = int(cur_move[1])
    letter_change = {let.strip(): ind + 1 for ind, let in enumerate(new_player.player_plane[0][2:])}
    move_pair = tuple((letter_change[cur_move[0]], int(cur_col)))
    if move_pair[1] < 10 and move_pair[0] == 1:
        new_player.enemy_plane[cur_col][move_pair[0]] = ' [O]'
    else:
        new_player.enemy_plane[cur_col][move_pair[0]] = '[O]'
    new_player.show_planes()
    new_player.status = 'in_game:wait'


code_dict = {
    "215": func_215,
    "230": func_230,
    "245": func_245,
    "250": func_250,
    "310": func_310,
    "340": func_340,
    "350": func_350,
}


def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        code_dict[message.split(':')[0]](message)


def connect_to_battle_server():
    print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
    try:
        s.connect((SERVER_HOST, SERVER_PORT))
        print("[+] Connected.")
        new_player.status = 'connected'
        t = Thread(target=listen_for_messages)
        t.daemon = True
        t.start()
        player_id = f"200:{new_player.player_id}"
        s.send(player_id.encode())
    except socket.error:
        print("[+] Error.")


def connect_to_player(enemy_id):
    message = f"220:{new_player.player_id}:{enemy_id}"
    s.send(message.encode())


def send_move():
    assert new_player.status == 'in_game'
    print('Выберите цель')
    move = input()
    if re.fullmatch(r'[a-j][0-9]', move) or re.fullmatch(r'[a-j]10', move):
        s.send(f'300:{move}:{new_player.player_id}'.encode())
    else:
        raise ValueError


def get_players_list():
    msg = f"210:{new_player.player_id}"
    s.send(msg.encode())


def connect_to_battle():
    get_id = input('Id противника: ')
    connect_to_player(get_id)


def make_move():
    if new_player.status != 'in_game:wait':
        try:
            send_move()
        except ValueError:
            print('Некорректное значение')
        except AssertionError:
            print('Игрок еще не в игре')
    else:
        print('Сейчас не ваш ход')


if __name__ == "__main__":
    while True:
        to_send = input()
        if to_send.lower() == 'q':
            break
        elif to_send == '/join server':
            connect_to_battle_server()
        elif to_send == '/ap':
            get_players_list()
        elif to_send == '/connect battle':
            connect_to_battle()
        elif to_send == '/mm':
            make_move()
        else:
            pass

    s.send(f"900:{new_player.player_id}".encode())
    s.close()
