from src.agents.actions.placing_action import PlaceChipAction
from src.agents.adhoc.adhoc_strategy import AdhocStrategy
import src.utilities.constants3x3 as c3x3
from src.game_components.board import Board
from src.game_components.chip import Chip


class AvoidCombinationsStrategy(AdhocStrategy):
    def __init__(self):
        self.scoring_parameter = 4

    def give_strategy_result(self, game_board: Board, hand_chips):
        chips_values_list = game_board.board_to_chip_values()

        for index in range(len(chips_values_list)):
            if chips_values_list[index] == 0:
                for chip in hand_chips:
                    updated_chips_values_list = chips_values_list.copy()
                    updated_chips_values_list[index] = chip.value
                    if not self.has_combinations(Chip(value=chip.value, row=int(index / 3), col=index % 3),
                                                 updated_chips_values_list):
                        return PlaceChipAction(row=int(index / 3), col=index % 3, value=chip.value)
        return None

    def has_combinations(self, chip_placed, chips_values_list):
        combinations = []
        combinations += self.find_collectable_chips(c3x3.diagonally_start_1,
                                                    c3x3.diagonally_end_1,
                                                    c3x3.diagonally_growth_1,
                                                    chips_values_list)
        combinations += self.find_collectable_chips(c3x3.diagonally_start_2,
                                                    c3x3.diagonally_end_2,
                                                    c3x3.diagonally_growth_2,
                                                    chips_values_list)
        combinations += self.find_collectable_chips(c3x3.vertically_start,
                                                    c3x3.vertically_end,
                                                    c3x3.vertically_growth,
                                                    chips_values_list)
        combinations += self.find_collectable_chips(c3x3.horizontally_start,
                                                    c3x3.horizontally_end,
                                                    c3x3.horizontally_growth,
                                                    chips_values_list)
        # filter combinations (viable combinations are those, that contains placed chip)
        for combination in combinations:
            for chip in combination:
                if chip.value == chip_placed.value and chip.row == chip_placed.row and chip.col == chip_placed.col:
                    return True
        return False

    def find_collectable_chips(self, indexes_start, indexes_end, index_growth, chips_values_list):
        combinations = []
        for (index_start, index_end) in zip(indexes_start, indexes_end):
            chips_in_line = []
            sum_of_chips_values = 0
            while index_start <= index_end:
                # if tile is empty
                if chips_values_list[index_start] == 0:
                    sum_of_chips_values = 0
                    chips_in_line = []
                    index_start += index_growth
                    continue
                # else: not empty
                else:
                    sum_of_chips_values += chips_values_list[index_start]
                    chips_in_line.append(
                        Chip(value=chips_values_list[index_start], row=int(index_start / 3), col=index_start % 3))
                # if sum reaches scoring parameter
                if sum_of_chips_values == self.scoring_parameter:
                    temp = chips_in_line.copy()
                    combinations.append(temp)
                    sum_of_chips_values -= chips_in_line[0].value
                    del chips_in_line[0]
                # if scoring parameter is stepped over
                if sum_of_chips_values > self.scoring_parameter:
                    # remove first chip in a line while sum is larger than parameter
                    while sum_of_chips_values > self.scoring_parameter:
                        sum_of_chips_values -= chips_in_line[0].value
                        del chips_in_line[0]
                    # prevent situations like this: 1 1 3 3 4
                    if sum_of_chips_values == self.scoring_parameter and index_start == index_end:
                        temp = chips_in_line.copy()
                        combinations.append(temp)
                index_start += index_growth
        return combinations
