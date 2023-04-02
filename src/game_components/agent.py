import copy
import math
import random
import src.learning_algorithm_parts.graph as gh
import src.game_components.actions.placing_action as pan
import src.game_components.actions.taking_action as tan
import src.game_components.chip as cp


class Agent:
    # game_board = instance of class Board
    # nickname = agent's id
    # driver, session = neoj4 driver/session
    def __init__(self, game_board, nickname, driver, session):

        # Parameters
        self.discount_rate = 0.75   # gamma in math
        self.learning_rate = 0.9    # alpha in math

        # Game board parameters
        self.board = game_board
        self.border_length = self.board.border_length
        self.board_size = self.board.board_size

        # Graph stored in Neo4j
        self.graph = gh.Graph(driver, session)
        # DELETE
        # self.graph.delete_everything()

        # Agent's possible actions at given position
        self.actions = []

        # Agent stuff
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
                tile_row = math.floor(tile / self.border_length)
                tile_col = tile % self.border_length
                self.actions.append(pan.PlaceChipAction(tile_row, tile_col, self.chips[0].value))
                self.actions.append(pan.PlaceChipAction(tile_row, tile_col, self.chips[1].value))

    # parameter combinations is list made in class GameManager
    def get_actions_for_taking(self, combinations):
        self.actions = []  # first, clear action list

        # loop over all combinations
        for combination in range(len(combinations)):
            self.actions.append(tan.TakeChipsAction(combination))

    def convert_placing_actions_to_board_states(self, game_board):
        board_states = []
        for action in self.actions:
            game_board_copy = copy.deepcopy(game_board)
            game_board_copy.add_chip_rowcol(action.row, action.col, cp.Chip(action.value))
            board_states.append(game_board_copy.board_to_chip_values())
        return board_states

    @staticmethod
    def convert_taking_actions_to_board_states(game_board, combinations, chip_placed_row, chip_placed_col):
        board_states = []
        for combination in combinations:
            game_board_copy = copy.deepcopy(game_board)
            for chip in combination:
                # If it's the same chip that was placed this round, agent can't take it
                if chip_placed_row == chip.row and chip_placed_col == chip.col:
                    continue
                game_board_copy.remove_chip(chip.row * game_board_copy.border_length + chip.col)
            board_states.append(game_board_copy.board_to_chip_values())
        return board_states

    # Returns random action from actions list
    def select_action_randomly(self):
        random_index = random.randint(0, len(self.actions) - 1)
        return self.actions[random_index]
