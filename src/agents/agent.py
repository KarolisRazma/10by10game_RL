import math
import random
from abc import ABC, abstractmethod
from src.agents.actions.placing_action import PlaceChipAction
from src.game_components.action_data import ActionData
from src.game_components.state_data import StateData


class Agent(ABC):

    def __init__(self, name):
        # Agent name
        self.name = name

        # Episode details
        self.score = 0
        self.hand_chips = []
        self.captured_chips = []

        # Episodes results counters
        self.wins = 0
        self.draws = 0

        # Endgame result flags: None at init
        self.last_game_result = None

    # Resets episode details
    def reset(self):
        self.score = 0
        self.hand_chips = []
        self.captured_chips = []

    # Returns used chip and deletes it from agent's hand
    def use_chip(self, chip_index):
        chip = self.hand_chips[chip_index]
        del self.hand_chips[chip_index]
        return chip

    def get_hand_chips_values_list(self):
        return sorted([chip.value for chip in self.hand_chips])

    def get_random_action_for_placing(self, game_board):
        # Loop while action is not selected
        # fixme can cause problems if board is full
        while True:
            random_tile_index = random.randint(0, len(game_board.tiles) - 1)
            if game_board.is_tile_empty(random_tile_index):
                tile_row = math.floor(random_tile_index / game_board.border_length)
                tile_col = random_tile_index % game_board.border_length
                hand_chip_index = random.randint(0, 1)
                return PlaceChipAction(tile_row, tile_col, self.hand_chips[hand_chip_index].value)

    @abstractmethod
    def observe_state(self, state_data: StateData, action_data: ActionData =None):
        pass

    @abstractmethod
    def select_placing_action(self, game_board):
        pass

    @abstractmethod
    def select_taking_action(self, game_board, combinations):
        pass
