import math
import random

from src.agents.actions.placing_action import PlaceChipAction
from src.game_components.board import Board
from src.game_components.chip import Chip
from src.game_components.color import Color
import src.utilities.constants3x3 as c3x3


class ReusableFunctions:

    def get_combinations_by_board_values(self, chip_placed, chips_values_list):
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
        updated_combinations = []
        for combination in combinations:
            if chip_placed in combination:
                updated_combinations.append(combination)
        return updated_combinations

    @staticmethod
    def get_random_action_for_placing(game_board: Board, hand_chips):
        while True:
            random_tile_index = random.randint(0, len(game_board.tiles) - 1)
            if game_board.is_tile_empty(random_tile_index):
                tile_row = math.floor(random_tile_index / game_board.border_length)
                tile_col = random_tile_index % game_board.border_length
                hand_chip_index = random.randint(0, 1)
                return PlaceChipAction(tile_row, tile_col, hand_chips[hand_chip_index].value)

    @staticmethod
    def get_points_by_combination(game_board: Board, combination, last_placed_chip: Chip):
        total_points = 0
        for chip in combination:
            if last_placed_chip.row == chip.row and last_placed_chip.col == chip.col:
                continue
            tile = game_board.get_tile_at_index(chip.row * game_board.border_length + chip.col)
            if tile.color == Color.BLUE:
                total_points += 2
            if tile.color == Color.WHITE:
                total_points += 1
        return total_points

    @staticmethod
    def update_board_by_combination(board: Board, combination, last_placed_chip: Chip):
        for chip in combination:
            if last_placed_chip.row == chip.row and last_placed_chip.col == chip.col:
                continue
            board.remove_chip(chip.row * board.border_length + chip.col)

    @staticmethod
    def find_collectable_chips(indexes_start, indexes_end, index_growth, chips_values_list):
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
                if sum_of_chips_values == c3x3.scoring_parameter:
                    temp = chips_in_line.copy()
                    combinations.append(temp)
                    sum_of_chips_values -= chips_in_line[0].value
                    del chips_in_line[0]
                # if scoring parameter is stepped over
                if sum_of_chips_values > c3x3.scoring_parameter:
                    # remove first chip in a line while sum is larger than parameter
                    while sum_of_chips_values > c3x3.scoring_parameter:
                        sum_of_chips_values -= chips_in_line[0].value
                        del chips_in_line[0]
                    # prevent situations like this: 1 1 3 3 4
                    if sum_of_chips_values == c3x3.scoring_parameter and index_start == index_end:
                        temp = chips_in_line.copy()
                        combinations.append(temp)
                index_start += index_growth
        return combinations

    @staticmethod
    def update_board_by_placing_action(board: Board, hand_chips, placing_action: PlaceChipAction):
        row, col, value = placing_action.row, placing_action.col, placing_action.value

        chip_index = 0 if hand_chips[0].value == value else 1

        selected_chip = hand_chips[chip_index]
        selected_chip.row = row
        selected_chip.col = col

        board.chips[row * 3 + col] = selected_chip

