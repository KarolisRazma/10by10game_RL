from enum import Enum


class StateChangeType(Enum):
    PLACING = 1
    TAKING = 2


class StateChangeData:
    def __init__(self, is_my_turn, game_board, enemy_score, container_chips_count, placing_action=None,
                 taking_combination=None, last_placed_chip=None):
        self.is_my_turn = is_my_turn
        self.game_board = game_board
        self.enemy_score = enemy_score
        self.container_chips_count = container_chips_count
        self.placing_action = placing_action
        self.taking_combination = taking_combination
        self.last_placed_chip = last_placed_chip


class InitialStateData:
    def __init__(self, game_board, container_chips_count, is_starting):
        self.game_board = game_board
        self.container_chips_count = container_chips_count
        self.is_starting = is_starting
