from connection import *
import Player

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
