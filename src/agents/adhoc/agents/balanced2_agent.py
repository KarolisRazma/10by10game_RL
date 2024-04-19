from src.agents.adhoc.adhoc_agent import AdhocAgent
from src.agents.adhoc.commons.combination_order import CombinationOrder
from src.agents.adhoc.helpers.most_points_available_helper import MostPointsAvailableHelper
from src.agents.adhoc.strategies.minimize_enemy_points_strategy import MinimizeEnemyPointsStrategy
from src.agents.adhoc.strategies.never_place_on_blue_strategy import NeverPlaceOnBlueStrategy
from src.agents.adhoc.strategies.place_for_combination_strategy import PlaceForCombinationStrategy
from src.agents.adhoc.strategies.take_most_points_strategy import TakeMostPointsStrategy


class BalancedAgent2(AdhocAgent):
    def __init__(self, name: str):
        super().__init__(name)

        self.minimize_enemy_points_strategy = MinimizeEnemyPointsStrategy()
        self.never_place_on_blue_strategy = NeverPlaceOnBlueStrategy()
        self.take_most_points_strategy = TakeMostPointsStrategy()
        self.place_for_combination_strategy = PlaceForCombinationStrategy()

        self.most_points_available_helper = MostPointsAvailableHelper()

    def select_placing_action(self, game_board):
        if self.most_points_available_helper.give_helper_result(game_board, self.hand_chips) \
                + self.current_state_data.my_score == 4:
            self.last_selected_placing_action = self.place_for_combination_strategy.give_strategy_result(
                game_board, self.hand_chips, CombinationOrder.DESC)
            return self.last_selected_placing_action

        if self.most_points_available_helper.give_helper_result(game_board, self.hand_chips, ignore_blue=True) >= 1:
            self.last_selected_placing_action = self.never_place_on_blue_strategy.give_strategy_result(
                game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.DESC
            )
        else:
            self.last_selected_placing_action = self.minimize_enemy_points_strategy.give_strategy_result(
                game_board=game_board, hand_chips=self.hand_chips, current_state_data=self.current_state_data
            )
        return self.last_selected_placing_action

    def select_taking_action(self, game_board, combinations):
        return self.take_most_points_strategy.give_strategy_result(game_board=game_board, combinations=combinations,
                                                                   last_placed_chip=self.last_selected_placing_action)
