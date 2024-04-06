from src.agents.adhoc.adhoc_agent import AdhocAgent
from src.agents.adhoc.helpers.combination_order import CombinationOrder
from src.agents.adhoc.strategies.place_for_combination_strategy import PlaceForCombinationStrategy
from src.agents.adhoc.strategies.take_most_points_strategy import TakeMostPointsStrategy


class GreedyAgent(AdhocAgent):
    def __init__(self, name: str):
        super().__init__(name)

        # Strategies
        self.place_for_combination_strategy = PlaceForCombinationStrategy()
        self.take_most_points_strategy = TakeMostPointsStrategy()

    def select_placing_action(self, game_board):
        self.last_selected_placing_action = self.place_for_combination_strategy.give_strategy_result(
            game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.DESC
        )
        if self.last_selected_placing_action is not None:
            return self.last_selected_placing_action
        self.last_selected_placing_action = self.get_random_action_for_placing(game_board)
        return self.last_selected_placing_action

    def select_taking_action(self, game_board, combinations):
        return self.take_most_points_strategy.give_strategy_result(game_board=game_board, combinations=combinations,
                                                                   last_placed_chip=self.last_selected_placing_action)
