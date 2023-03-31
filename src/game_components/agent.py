import copy
import math
import random
import src.learning_algorithm_parts.vertex as vrt
import src.game_components.actions.placing_action as pan
import src.game_components.actions.taking_action as tan
import src.game_components.chip as cp


class Agent:
    def __init__(self, nickname, board_len):
        # Agent's current vertex
        self.current_vertex = None

        # Board border length constant
        self.board_border_len = board_len

        # Agent's possible actions at given position
        self.actions = []

        # Next possible vertexes
        self.next_vertexes = []

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
                tile_row = math.floor(tile / self.board_border_len)
                tile_col = tile % self.board_border_len
                self.actions.append(pan.PlaceChipAction(tile_row, tile_col, self.chips[0].value))
                self.actions.append(pan.PlaceChipAction(tile_row, tile_col, self.chips[1].value))

    # parameter combinations is list made in class GameManager
    def get_actions_for_taking(self, combinations):
        self.actions = []  # first, clear action list

        # loop over all combinations
        for combination in range(len(combinations)):
            self.actions.append(tan.TakeChipsAction(combination))

    # Returns true if vertex is already in the graph
    def is_selected_action_in_current_vertex(self, game_board):
        new_position = game_board.board_to_chip_values()
        vertex_new_position = vrt.Vertex(new_position)
        return self.current_vertex.is_linked_already(vertex_new_position)

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

    # Returns next possible vertexes according to available actions
    # Updates self.actions according to next_vertexes
    def get_next_vertexes_placing(self, game_board):
        updated_actions = []
        self.next_vertexes = []
        for action in self.actions:
            game_board_copy = copy.deepcopy(game_board)
            game_board_copy.add_chip_rowcol(action.row, action.col, self.chips[action.chip_index])
            # What if null?
            next_vertex = self.current_vertex.find_next_vertex(game_board_copy.board_to_chip_values())
            if next_vertex is not None:
                self.next_vertexes.append(next_vertex)
                updated_actions.append(action)
        self.actions = updated_actions

    def get_next_vertexes_taking(self, game_board, combinations, chip_placed_row, chip_placed_col):
        updated_actions = []
        self.next_vertexes = []
        for (action, combination) in zip(self.actions, combinations):
            game_board_copy = copy.deepcopy(game_board)
            for chip in combination:
                # If it's the same chip that was placed this round, agent can't take it
                if chip_placed_row == chip.row and chip_placed_col == chip.col:
                    continue
                game_board_copy.remove_chip(chip.row * game_board_copy.border_length + chip.col)
            # What if null?
            next_vertex = self.current_vertex.find_next_vertex(game_board_copy.board_to_chip_values())
            if next_vertex is not None:
                self.next_vertexes.append(next_vertex)
                updated_actions.append(action)
        self.actions = updated_actions

    # Returns random next vertex board values
    @staticmethod
    def select_next_vertex_randomly(next_vertices):
        random_index = random.randint(0, len(next_vertices) - 1)
        return next_vertices[random_index]

    # Returns random action from actions list
    def select_action_randomly(self):
        random_index = random.randint(0, len(self.actions) - 1)
        return self.actions[random_index]

    # Returns random action from actions list
    # And random next vertex from next vertices list
    # In a list form [0] is action, [1] is next_vertex
    def select_action_and_next_vertex_randomly(self, next_vertices):
        random_index = random.randint(0, len(self.actions) - 1)
        return [self.actions[random_index], next_vertices[random_index]]
