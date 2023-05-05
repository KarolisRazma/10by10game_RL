import math
import src.agents.actions.placing_action as pan


class Agent:

    def __init__(self, nickname):
        # Agent stuff, game details
        self.id = nickname
        self.score = 0
        self.chips = []  # current chips in hand
        self.captured_chips = []  # len(chips_captured) = score
        self.wins = 0
        self.draws = 0

        self.is_last_game_won = None
        self.is_last_game_drawn = None

        # Agent's possible actions at given position
        self.actions = []

        # Assigned by environment
        self.agent_number = None

    # reset score/chips/captured_chips after episode is complete
    def reset(self):
        self.score = 0
        self.chips = []
        self.captured_chips = []

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
                tile_row = math.floor(tile / game_board.border_length)
                tile_col = tile % game_board.border_length
                self.actions.append(pan.PlaceChipAction(tile_row, tile_col, self.chips[0].value))
                self.actions.append(pan.PlaceChipAction(tile_row, tile_col, self.chips[1].value))




