from src.agents.adhoc.adhoc_strategy import AdhocStrategy
from src.agents.adhoc.commons.playstyle import Playstyle
from src.agents.adhoc.helpers.most_points_available_helper import MostPointsAvailableHelper
from src.agents.adhoc.strategies.bring_back_to_container_strategy import BringBackToContainerStrategy
from src.game_components.state_data import StateData


class AdaptiveStrategy(AdhocStrategy):

    def __init__(self):
        pass

    def give_strategy_result(self, state_data: StateData):
        my_score = state_data.my_score
        enemy_score = state_data.enemy_score
        chips_left = state_data.chips_left

        if chips_left <= 5 and my_score < 2:
            return Playstyle.AVOID_COMBINATION

        return Playstyle.LOOK_FOR_COMBINATION

    #
    #
    # Possible scores
    #
    # ----0--1--2--3
    # 0| 00 01 02 03
    # 1| 10 11 12 13
    # 2| 20 21 22 23
    # 3| 30 31 32 33
    #
    #
    # Chips left
    #
    #
    #
    #
    #
    # def __init__(self):
    #     self.chips_left_criteria = 4
    #
    #     self.winning_points = 4
    #     self.points_left_for_enemy_to_win = 1
    #
    #     self.locked_fasting_playstyle = False
    #     self.locked_greedy_playstyle = False
    #
    #
    #

    # def give_strategy_result(self, state_data: StateData):
    #     if self.locked_greedy_playstyle:
    #         return Playstyle.LOOK_FOR_COMBINATION
    #     elif self.locked_fasting_playstyle:
    #         return Playstyle.AVOID_COMBINATION
    #
    #     # Scores
    #     my_current_score = state_data.my_score
    #     enemy_current_score = state_data.enemy_score
    #     current_score_difference = my_current_score - enemy_current_score
    #
    #     chips_left = state_data.chips_left
    #
    #     if chips_left == self.chips_left_criteria and my_current_score == 0:
    #         self.locked_fasting_playstyle = True
    #         return Playstyle.AVOID_COMBINATION
    #
    #     if chips_left == self.chips_left_criteria and my_current_score == 2:
    #         self.locked_greedy_playstyle = True
    #         return Playstyle.LOOK_FOR_COMBINATION
    #
    #     if chips_left <= self.chips_left_criteria and \
    #             self.winning_points - enemy_current_score <= self.points_left_for_enemy_to_win:
    #         return Playstyle.LOOK_FOR_COMBINATION
    #     return Playstyle.AVOID_COMBINATION
    #
    #     # if chips_left < self.chips_left_criteria and current_score_difference == self.score_difference:
    #     #     return Playstyle.AVOID_COMBINATION
    #     # else:
    #     #     return Playstyle.LOOK_FOR_COMBINATION
