import random
from src.agents.agent import Agent
from src.game_components.action_data import ActionData
from src.game_components.state_data import StateData


class RandomWalkerAgent(Agent):

    def __init__(self, name):
        super().__init__(name)

    def select_placing_action(self, game_board):
        return self.get_random_action_for_placing(game_board)

    def select_taking_action(self, game_board, combinations):
        random_combination_index = random.randint(0, len(combinations) - 1)
        return combinations[random_combination_index]

    def observe_state(self, state_data: StateData, action_data: ActionData = None):
        pass
