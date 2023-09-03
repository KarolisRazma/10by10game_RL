from abc import ABC, abstractmethod


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
        self.is_game_won = None
        self.is_game_drawn = None

    # Resets episode details
    def reset(self):
        self.score = 0
        self.hand_chips = []
        self.captured_chips = []
        self.is_game_won = None
        self.is_game_drawn = None

    # Returns used chip and deletes it from agent's hand
    def use_chip(self, chip_index):
        chip = self.hand_chips[chip_index]
        del self.hand_chips[chip_index]
        return chip

    @abstractmethod
    def process_initial_state(self, initial_data):
        pass

    @abstractmethod
    def process_state_changes(self, changes_type, changes_data):
        pass

    @abstractmethod
    def select_placing_action(self, game_board):
        pass

    @abstractmethod
    def select_taking_action(self, game_board, combinations, last_placed_chip):
        pass
