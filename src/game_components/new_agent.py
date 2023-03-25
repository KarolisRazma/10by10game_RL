import copy
import math
import random
import src.learning_algorithm_parts.vertex as vrt


class Agent:
    def __init__(self, nickname, board_len):
        # Agent's current vertex
        self.current_vertex = None

        # Board border length constant
        self.board_border_len = board_len

        # Agent's possible actions at given position
        self.actions = []

        self.next_board_values = []

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
                self.actions.append(PlaceChipAction(tile_row, tile_col, 0))
                self.actions.append(PlaceChipAction(tile_row, tile_col, 1))  # append another action for other chip

    # parameter combinations is list made in class GameManager
    def get_actions_for_taking(self, combinations):
        self.actions = []  # first, clear action list

        # loop over all combinations
        for combination in range(len(combinations)):
            self.actions.append(TakeChipsAction(combination))

    # Returns true if vertex is already in the graph
    def is_selected_action_in_current_vertex(self, game_board):
        new_position = game_board.board_to_chip_values()
        vertex_new_position = vrt.Vertex(new_position)
        return self.current_vertex.is_linked_already(vertex_new_position)

    # Returns random action from actions list
    def select_action_randomly(self):
        random_index = random.randint(0, len(self.actions) - 1)
        return self.actions[random_index]

    # # PLACING ACTION
    # # Returns true if vertex is already in the graph
    # def is_selected_placing_action_in_current_vertex(self, action, game_board):
    #     new_position = self.convert_placing_action_to_new_position(action, game_board)
    #     vertex_new_position = vrt.Vertex(new_position)
    #     return self.current_vertex.is_linked_already(vertex_new_position)
    #
    # # Returns list of chips values
    # def convert_placing_action_to_new_position(self, action, game_board):
    #     game_board_copy = copy.deepcopy(game_board)
    #     game_board_copy.add_chip_rowcol(action.row, action.col, self.chips[action.chip_index])
    #     return game_board_copy.board_to_chip_values()

    # def append_actions_for_placing_to_graph(self, game_board):
    #     self.next_board_values = []
    #     self.get_actions_for_placing(game_board)
    #
    #     for action in self.actions:
    #         # Making action
    #         game_board_copy = copy.deepcopy(game_board)
    #         index = action.row * self.board_border_len + action.col
    #         game_board_copy.add_chip(index, self.chips[action.chip_index])
    #         # Convert board to chip values
    #         parent_board_values = game_board.board_to_chip_values()
    #         child_board_values = game_board_copy.board_to_chip_values()
    #         # Try to append to the graph
    #         self.graph.append_vertex(parent_board_values, child_board_values)
    #         self.next_board_values.append(child_board_values)
    #
    # def append_actions_for_taking_to_graph(self, combinations, game_board):
    #     self.next_board_values = []
    #     self.get_actions_for_taking(combinations)
    #
    #     for combination in self.actions:
    #         # Make copy of the board
    #         game_board_copy = copy.deepcopy(game_board)
    #
    #         # Collect indexes that involves chips in combination
    #         indexes = []
    #         for chip in combination:
    #             indexes.append(chip.row * self.board_border_len + chip.col)
    #
    #         # Remove all of those chips
    #         for index in indexes:
    #             game_board_copy.remove_chip(index)
    #
    #         # Convert board to chip values
    #         parent_board_values = game_board.board_to_chip_values()
    #         child_board_values = game_board_copy.board_to_chip_values()
    #
    #         # Try to append to the graph
    #         self.graph.append_vertex(parent_board_values, child_board_values)
    #         self.next_board_values.append(child_board_values)

    # TODO this function

    # def select_placing_action(self, game_board):
    #     # Convert to game board values (chip values)
    #     game_board_values = game_board.board_to_chip_values()
    #     # Find current state vertex
    #     parent_vertex = self.graph.find_vertex(game_board_values)
    #     # Copy its next vertexes
    #     parent_vertex_next_vertexes = copy.deepcopy(parent_vertex.next_vertexes)
    #
    #     # Filter irrelevant next vertexes
    #     for parent_next_vertex in parent_vertex_next_vertexes:
    #
    #
    #         # Convert board to chip values
    #         child_board_values = game_board_copy.board_to_chip_values()
    #             for child_ parent_vertex_next_vertexes
    #
    #
    #         next_vertexes_amount = len(parent_vertex.next_vertexes) - 1
    #
    #         random_index = random.randint(0, action_space)


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
