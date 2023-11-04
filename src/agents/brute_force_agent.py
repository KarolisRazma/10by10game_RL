import math
import random
from src.agents.agent import Agent
from src.agents.actions.placing_action import PlaceChipAction


# TODO change class name to RandomWalker
class RandomWalkerAgent(Agent):

    def __init__(self, name):
        super().__init__(name)

    def select_placing_action(self, game_data):
        return self.get_action_for_placing(game_data.game_board)

    def select_taking_action(self, game_data, combinations, last_placed_chip):
        random_combination_index = random.randint(0, len(combinations) - 1)
        return combinations[random_combination_index]

    def get_action_for_placing(self, game_board):
        # Loop while action is not selected
        # fixme can cause problems if board is full
        while True:
            random_tile_index = random.randint(0, len(game_board.tiles) - 1)
            if game_board.is_tile_empty(random_tile_index):
                tile_row = math.floor(random_tile_index / game_board.border_length)
                tile_col = random_tile_index % game_board.border_length
                hand_chip_index = random.randint(0, 1)
                return PlaceChipAction(tile_row, tile_col, self.hand_chips[hand_chip_index].value)

    def process_initial_state(self, initial_data):
        pass

    def process_state_changes(self, changes_type, changes_data):
        pass
