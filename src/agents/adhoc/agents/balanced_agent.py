from src.agents.adhoc.adhoc_agent import AdhocAgent
from src.agents.adhoc.helpers.combination_order import CombinationOrder
from src.agents.adhoc.helpers.playstyle import Playstyle
from src.agents.adhoc.strategies.adaptive_strategy import AdaptiveStrategy
from src.agents.adhoc.strategies.advanced_first_move_strategy import AdvancedFirstMoveStrategy
from src.agents.adhoc.strategies.avoid_combinations_strategy import AvoidCombinationsStrategy
from src.agents.adhoc.strategies.never_place_on_blue_strategy import NeverPlaceOnBlueStrategy
from src.agents.adhoc.strategies.place_for_combination_strategy import PlaceForCombinationStrategy
from src.agents.adhoc.strategies.take_least_points_strategy import TakeLeastPointsStrategy
from src.agents.adhoc.strategies.take_most_points_strategy import TakeMostPointsStrategy


class BalancedAgent(AdhocAgent):
    def __init__(self, name: str):
        super().__init__(name)

        self.is_first_move = True

        # Default value (doesn't matter)
        self.current_playstyle: Playstyle = Playstyle.AVOID_COMBINATION

        # Strategies
        self.avoid_combinations_strategy = AvoidCombinationsStrategy()
        self.take_least_points_strategy = TakeLeastPointsStrategy()
        self.place_for_combination_strategy = PlaceForCombinationStrategy()
        self.take_most_points_strategy = TakeMostPointsStrategy()
        self.adaptive_strategy = AdaptiveStrategy()

        self.advanced_first_move_strategy = AdvancedFirstMoveStrategy()
        self.never_place_on_blue_strategy = NeverPlaceOnBlueStrategy()

    def reset(self):
        super().reset()
        self.is_first_move = True

    def select_placing_action(self, game_board):
        # self.current_playstyle: Playstyle = self.adaptive_strategy.give_strategy_result(self.current_state_data)
        #
        # if self.current_playstyle is Playstyle.AVOID_COMBINATION:
        #     self.last_selected_placing_action = self.avoid_combinations_strategy.give_strategy_result(
        #         game_board=game_board, hand_chips=self.hand_chips
        #     )
        #     if self.last_selected_placing_action is not None:
        #         return self.last_selected_placing_action
        #     self.last_selected_placing_action = self.place_for_combination_strategy.give_strategy_result(
        #         game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.ASC
        #     )
        #     if self.last_selected_placing_action is not None:
        #         return self.last_selected_placing_action
        # else:
        #     self.last_selected_placing_action = self.place_for_combination_strategy.give_strategy_result(
        #         game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.DESC
        #     )
        #     if self.last_selected_placing_action is not None:
        #         return self.last_selected_placing_action
        #
        # # Shouldn't be reached, but just in case
        # self.last_selected_placing_action = self.get_random_action_for_placing(game_board)

        self.last_selected_placing_action = self.never_place_on_blue_strategy.give_strategy_result(
            game_board=game_board, hand_chips=self.hand_chips, order=CombinationOrder.DESC
        )
        if self.last_selected_placing_action is not None:
            return self.last_selected_placing_action

        self.last_selected_placing_action = self.get_random_action_for_placing(game_board)
        return self.last_selected_placing_action

    def select_taking_action(self, game_board, combinations):
        return self.take_most_points_strategy.give_strategy_result(game_board=game_board,
                                                                   combinations=combinations,
                                                                   last_placed_chip=
                                                                   self.last_selected_placing_action)
    # if self.current_playstyle is Playstyle.AVOID_COMBINATION:
    #     return self.take_least_points_strategy.give_strategy_result(game_board=game_board,
    #                                                                 combinations=combinations,
    #                                                                 last_placed_chip=
    #                                                                 self.last_selected_placing_action)
    # else:
    #     return self.take_most_points_strategy.give_strategy_result(game_board=game_board,
    #                                                                combinations=combinations,
    #                                                                last_placed_chip=
    #                                                                self.last_selected_placing_action)
