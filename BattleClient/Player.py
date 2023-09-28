import re
from random import randint
import os


class Player:
    def __init__(self):
        self.player_id = randint(1000, 10000)
        self.enemy_id = 0
        self.status = 'free'
        self.available_ships = {'Авианосец': [(0, 3), (3, 0)],
                                'Крейсер': [(0, 2), (2, 0)],
                                'Эсминец': [(0, 1), (1, 0)],
                                'Катер': [(0, 0)],
                                }
        self.ships_on_plane = {'Авианосец': [tuple()],
                               'Крейсер': [tuple(), tuple()],
                               'Эсминец': [tuple(), tuple(), tuple()],
                               'Катер': [tuple(), tuple(), tuple(), tuple()],
                               }
        self.free_cells = list()
        self.dead_cells = list()
        self._prepare_free_cells()
        self.ship_cells = list()
        self.player_plane = [[] for _ in range(11)]
        self.player_plane[0] = [0, ' ', ' a ', ' b ', ' c ', ' d ', ' e ', ' f ', ' g ', ' h ', ' i ', ' j ']
        self._prepare_player_plane()
        self.enemy_plane = [[] for _ in range(11)]
        self.enemy_plane[0] = [0, ' ', ' a ', ' b ', ' c ', ' d ', ' e ', ' f ', ' g ', ' h ', ' i ', ' j ']
        self._prepare_enemy_plane()

    def _prepare_free_cells(self):
        for i in range(1, 11):
            for j in range(1, 11):
                self.free_cells.append((i, j))

    def _prepare_player_plane(self):
        for ind, row in enumerate(self.player_plane):
            if len(row) == 0:
                row.append(ind)
                if ind < 10:
                    row.append(' [ ]')
                    for _ in range(9):
                        row.append('[ ]')
                else:
                    for _ in range(10):
                        row.append('[ ]')

    def _prepare_enemy_plane(self):
        for ind, row in enumerate(self.enemy_plane):
            if len(row) == 0:
                row.append(ind)
                if ind < 10:
                    row.append(' [ ]')
                    for _ in range(9):
                        row.append('[ ]')
                else:
                    for _ in range(10):
                        row.append('[ ]')

    def show_planes(self):
        try:
            assert self.status in ['prepare', 'in_game', 'in_game:wait']
            print(f'Ваше поле {self.player_id}' + '\t\t\t\t\t' + f'Поле соперника {self.enemy_id}')
            for pair in self.ship_cells:
                if pair[1] < 10 and pair[0] == 1:
                    self.player_plane[pair[1]][pair[0]] = ' [X]'
                else:
                    self.player_plane[pair[1]][pair[0]] = '[X]'
            for pair in self.dead_cells:
                if pair[1] < 10 and pair[0] == 1:
                    self.player_plane[pair[1]][pair[0]] = ' [F]'
                else:
                    self.player_plane[pair[1]][pair[0]] = '[F]'
            for row_p, row_en in zip(self.player_plane, self.enemy_plane):
                print(*row_p, end='\t')
                print(*row_en)
            print('\n')
            #print(f'Поле соперника {self.enemy_id}')
        except AssertionError:
            print('Игрок вне игры')
            exit()

    def place_ship(self):
        print('Необходимо расставить корабли')
        letter_change = {let.strip(): ind + 1 for ind, let in enumerate(self.player_plane[0][2:])}
        for ship_key in self.available_ships.keys():
            cur_len = len(self.ships_on_plane[ship_key])
            for ship_num in range(cur_len):
                while True:
                    ship_pos = input(f'Выберите место для {ship_key}: ')
                    ship_pos = ship_pos.replace(' ', '')
                    if re.fullmatch(r'[a-j][0-9][a-j][0-9]', ship_pos) or re.fullmatch(r'[a-j]10[a-j]10', ship_pos):
                        if len(ship_pos) == 4:
                            pos_list = [int(pos) if pos.isdigit() else letter_change[pos] for pos in ship_pos]
                        elif len(ship_pos) == 6:
                            pos_list = [int(letter_change[ship_pos[0]]), int(ship_pos[1] + ship_pos[2]),
                                        int(letter_change[ship_pos[3]]), int(ship_pos[4] + ship_pos[5])]
                        else:
                            print('Ошибка ввода')
                            continue
                        if (lambda x1, y1, x2, y2: (abs(x1 - x2), abs(y1 - y2)))(*pos_list) \
                                in self.available_ships[ship_key]:
                            if all([(pos_list[0], pos_list[1]) not in self.ship_cells,
                                    (pos_list[2], pos_list[3]) not in self.ship_cells]):
                                self.ships_on_plane[ship_key][ship_num] = (tuple(pos_list))
                                ship_end = max(abs(pos_list[1] - pos_list[3]), abs(pos_list[0] - pos_list[2]))
                                if ship_end == abs(pos_list[1] - pos_list[3]):
                                    ship_begin = pos_list[0]
                                    for i in range(1, ship_end + 2):
                                        self.free_cells.remove((ship_begin, max(pos_list[1], pos_list[3]) + 1 - i))
                                        self.ship_cells.append((ship_begin, max(pos_list[1], pos_list[3]) + 1 - i))
                                else:
                                    ship_begin = pos_list[1]
                                    for i in range(1, ship_end + 2):
                                        self.free_cells.remove((max(pos_list[0], pos_list[2]) + 1 - i, ship_begin))
                                        self.ship_cells.append((max(pos_list[0], pos_list[2]) + 1 - i, ship_begin))
                                break
                            else:
                                print('Место уже занято')
                        else:
                            print('Ошибка. Повторите')
                    else:
                        print('Неверный ввод. Повторите')

            self.show_planes()
