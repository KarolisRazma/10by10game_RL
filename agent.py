import math
import random


class Agent:
    def __init__(self, nickname):
        # there's two ways to implement:
        # 1) give Agent class reference to Board
        # 2) pass board as argument in the function

        # (1) here, but sticking to (2) way, implemented below
        # self.board = game_board  # same instance as in GameManager

        # (2) way fields
        # maybe, I need to store actions as a field ?
        self.actions = []

        # also copy-paste stuff from Player class
        self.id = nickname
        self.score = 0
        self.chips = []  # current chips in hand
        self.captured_chips = []  # len(chips_captured) = score
        self.wins = 0
        self.draws = 0

    # reset score/chips/captured_chips after episode is complete
    def reset(self):
        self.score = 0
        self.chips = []
        self.captured_chips = []

    # same function from class Player
    # returns used chip and deletes it from agent's inventory
    def use_chip(self, chip_index):
        chip = self.chips[chip_index]
        del self.chips[chip_index]
        return chip

    # parameter game_board is object from class Board
    def get_actions_for_placing(self, game_board):
        self.actions = []  # first, clear action list

        # loop over all tiles
        for tile in range(len(game_board.tiles)):
            if game_board.is_tile_empty(tile):
                tile_row = math.floor(tile / 5)
                tile_col = tile % 5
                self.actions.append(PlaceChipAction(tile_row, tile_col, 0))
                self.actions.append(PlaceChipAction(tile_row, tile_col, 1))  # append another action for other chip

    # parameter combinations is list made in class GameManager
    def get_actions_for_taking(self, combinations):
        self.actions = []  # first, clear action list

        # loop over all combinations
        for combination in range(len(combinations)):
            self.actions.append(TakeChipsAction(combination))

    def select_action_randomly(self):
        random_index = random.randint(0, len(self.actions)-1)
        return self.actions[random_index]


# defining short class PlaceChipAction for the Agent class
# its purpose is to represent agent's action to place chip on the board
class PlaceChipAction:
    def __init__(self, row, col, chip_index):
        self.row = row
        self.col = col
        self.chip_index = chip_index

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


# defining short class TakeChipsAction for the Agent class
# its purpose is to represent agent's action to take chips from the board
class TakeChipsAction:
    def __init__(self, combination_index):
        self.combination_index = combination_index

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
