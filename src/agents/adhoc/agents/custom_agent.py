from src.agents.adhoc.adhoc_agent import AdhocAgent
from src.agents.adhoc.commons.combination_order import CombinationOrder
from src.agents.adhoc.commons.playstyle import Playstyle
from src.agents.adhoc.helpers.most_points_available_helper import MostPointsAvailableHelper
from src.agents.adhoc.strategies.adaptive_strategy import AdaptiveStrategy
from src.agents.adhoc.strategies.avoid_and_minimize_strategy import AvoidAndMinimize
from src.agents.adhoc.strategies.avoid_combinations_strategy import AvoidCombinationsStrategy
from src.agents.adhoc.strategies.bring_back_to_container_strategy import BringBackToContainerStrategy
from src.agents.adhoc.strategies.never_place_on_blue_strategy import NeverPlaceOnBlueStrategy
from src.agents.adhoc.strategies.place_for_combination_strategy import PlaceForCombinationStrategy
from src.agents.adhoc.strategies.take_least_points_strategy import TakeLeastPointsStrategy
from src.agents.adhoc.strategies.take_most_points_strategy import TakeMostPointsStrategy


class CustomAgent(AdhocAgent):
    def __init__(self, name: str):
        super().__init__(name)

        self.current_playstyle: Playstyle = None

        # Strategies
        self.adaptive_strategy = AdaptiveStrategy()

        self.place_for_combination_strategy = PlaceForCombinationStrategy()
        self.avoid_combinations_strategy = AvoidCombinationsStrategy()
        self.never_place_on_blue_strategy = NeverPlaceOnBlueStrategy()

        self.take_most_points_strategy = TakeMostPointsStrategy()
        self.take_least_points_strategy = TakeLeastPointsStrategy()

        self.most_points_available_helper = MostPointsAvailableHelper()
        self.bring_back_to_container_strategy = BringBackToContainerStrategy()

        self.avoid_and_minimize = AvoidAndMinimize()

    def select_placing_action(self, game_board):
        chips_left = self.current_state_data.chips_left
        my_score = self.current_state_data.my_score
        enemy_score = self.current_state_data.enemy_score
        most_points_available = self.most_points_available_helper.give_helper_result(game_board, self.hand_chips)

        # Focus red if conditions are met
        if most_points_available == 0:
            self.last_selected_placing_action = self.bring_back_to_container_strategy.give_strategy_result(
                game_board, self.hand_chips)
            if self.last_selected_placing_action is not None:
                return self.last_selected_placing_action

        # Otherwise depending on playstyle
        self.current_playstyle: Playstyle = self.adaptive_strategy.give_strategy_result(self.current_state_data)

        if most_points_available + my_score >= 4:
            self.current_playstyle = Playstyle.LOOK_FOR_COMBINATION

        if self.current_playstyle is Playstyle.AVOID_COMBINATION:
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
        else:
            self.last_selected_placing_action = self.place_for_combination_strategy.give_strategy_result(
                game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.DESC
            )
            if self.last_selected_placing_action is not None:
                return self.last_selected_placing_action

        self.last_selected_placing_action = self.get_random_action_for_placing(game_board)
        return self.last_selected_placing_action

    def select_taking_action(self, game_board, combinations):
        if self.current_playstyle is Playstyle.AVOID_COMBINATION:
            return self.take_least_points_strategy.give_strategy_result(game_board=game_board,
                                                                        combinations=combinations,
                                                                        last_placed_chip=
                                                                        self.last_selected_placing_action)
        else:
            return self.take_most_points_strategy.give_strategy_result(game_board=game_board,
                                                                       combinations=combinations,
                                                                       last_placed_chip=
                                                                       self.last_selected_placing_action)
