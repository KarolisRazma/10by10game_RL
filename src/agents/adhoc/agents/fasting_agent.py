from src.agents.adhoc.adhoc_agent import AdhocAgent
from src.agents.adhoc.helpers.combination_order import CombinationOrder
from src.agents.adhoc.strategies.avoid_combinations_strategy import AvoidCombinationsStrategy
from src.agents.adhoc.strategies.place_for_combination_strategy import PlaceForCombinationStrategy
from src.agents.adhoc.strategies.take_least_points_strategy import TakeLeastPointsStrategy


class FastingAgent(AdhocAgent):
    def __init__(self, name: str):
        super().__init__(name)

        # Strategies
        self.avoid_combinations_strategy = AvoidCombinationsStrategy()
        self.place_for_combination_strategy = PlaceForCombinationStrategy()
        self.take_least_points_strategy = TakeLeastPointsStrategy()

    def select_placing_action(self, game_board):
        self.last_selected_placing_action = self.avoid_combinations_strategy.give_strategy_result(
            game_board=game_board, hand_chips=self.hand_chips
        )
        if self.last_selected_placing_action is not None:
            return self.last_selected_placing_action

        self.last_selected_placing_action = self.place_for_combination_strategy.give_strategy_result(
            game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.ASC
        )
        if self.last_selected_placing_action is not None:
            return self.last_selected_placing_action

        self.last_selected_placing_action = self.get_random_action_for_placing(game_board)
        return self.last_selected_placing_action

    def select_taking_action(self, game_board, combinations):
        return self.take_least_points_strategy.give_strategy_result(game_board=game_board, combinations=combinations,
                                                                    last_placed_chip=self.last_selected_placing_action)
