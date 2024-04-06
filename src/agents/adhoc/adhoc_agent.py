import random
from abc import ABC, abstractmethod

from src.agents.agent import Agent
from src.game_components.action_data import ActionData
from src.game_components.state_data import StateData


class AdhocAgent(Agent, ABC):
    def __init__(self, name: str):
        super().__init__(name)

        self.current_state_data = None
        self.last_selected_placing_action = None

    @abstractmethod
    def select_placing_action(self, game_board):
        pass

    @abstractmethod
    def select_taking_action(self, game_board, combinations):
        pass

    def observe_state(self, state_data: StateData, action_data: ActionData = None):
        self.current_state_data = state_data

    @staticmethod
    def get_random_combination(combinations):
        random_combination_index = random.randint(0, len(combinations) - 1)
        return combinations[random_combination_index]
