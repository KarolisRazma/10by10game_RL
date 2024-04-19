from src.agents.actions.placing_action import PlaceChipAction
from src.agents.adhoc.adhoc_strategy import AdhocStrategy
from src.agents.adhoc.commons.combination_order import CombinationOrder
from src.agents.adhoc.commons.reusable_functions import ReusableFunctions
from src.agents.adhoc.helpers.most_points_available_helper import MostPointsAvailableHelper
from src.agents.adhoc.strategies.place_for_combination_strategy import PlaceForCombinationStrategy
from src.agents.adhoc.strategies.take_least_points_strategy import TakeLeastPointsStrategy
from src.agents.adhoc.strategies.take_most_points_strategy import TakeMostPointsStrategy
from src.game_components.board import Board
from src.game_components.chip import Chip

import src.utilities.constants3x3 as c3x3
from src.game_components.state_data import StateData


class AvoidAndMinimize(AdhocStrategy):

    def __init__(self):
        self.take_most_points_strategy = TakeMostPointsStrategy()
        self.take_least_points_strategy = TakeLeastPointsStrategy()
        self.place_for_combination_strategy = PlaceForCombinationStrategy()

        self.agent_min_points_map = [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1],
                                     [-1, -1], [-1, -1], [-1, -1], [-1, -1]]
        self.enemy_max_points_map = [[999, 999], [999, 999], [999, 999], [999, 999], [999, 999],
                                     [999, 999], [999, 999], [999, 999], [999, 999]]

        self.reusable_functions = ReusableFunctions()
        self.most_points_available_helper = MostPointsAvailableHelper()

    def process_tile(self, game_board: Board, tile_index, hand_chips, enemy_hand_chips_variations):
        if game_board.is_tile_empty(tile_index):
            for chip, chip_index in zip(hand_chips, range(len(hand_chips))):
                # Update board
                board_copy = self.copy_board(game_board)
                self.place_chip_on_board_tile(board_copy, tile_index, chip)
                last_placed_chip = board_copy.chips[tile_index]

                combinations = self.reusable_functions.get_combinations_by_board_values(
                    last_placed_chip, board_copy.board_to_chip_values())

                agent_min_points = 0
                if combinations:
                    combination = self.take_least_points_strategy.give_strategy_result(board_copy, combinations,
                                                                                       last_placed_chip)
                    agent_min_points = self.reusable_functions.get_points_by_combination(board_copy, combination,
                                                                                         last_placed_chip)
                    self.reusable_functions.update_board_by_combination(board_copy, combination, last_placed_chip)

                enemy_max_points = 0
                for enemy_hand_chips in enemy_hand_chips_variations:
                    board_copy_for_enemy = self.copy_board(board_copy)
                    enemy_points = self.most_points_available_helper.give_helper_result(board_copy_for_enemy,
                                                                                        enemy_hand_chips)
                    if enemy_points > enemy_max_points:
                        enemy_max_points = enemy_points

                self.agent_min_points_map[tile_index][chip_index] = agent_min_points
                self.enemy_max_points_map[tile_index][chip_index] = enemy_max_points

    def give_strategy_result(self, game_board: Board, hand_chips, current_state_data: StateData):
        enemy_hand_chips_variations = self.get_enemy_hand_chips_variations(current_state_data)

        for tile_index in range(len(game_board.tiles)):
            self.process_tile(game_board, tile_index, hand_chips, enemy_hand_chips_variations)

        tile_index, chip_index = self.find_biggest_difference()
        if tile_index != -1:
            return PlaceChipAction(row=int(tile_index / 3), col=tile_index % 3, value=hand_chips[chip_index].value)
        else:
            return None

    def find_biggest_difference(self):
        target_tile_index = -1
        target_chip_index = -1
        for tile_index, agent_points_pair in enumerate(self.agent_min_points_map):
            enemy_points_pair = self.enemy_max_points_map[tile_index]
            for chip_index, (agent_points, enemy_points) in enumerate(zip(agent_points_pair, enemy_points_pair)):
                if enemy_points - agent_points <= 1:
                    target_tile_index = tile_index
                    target_chip_index = chip_index

        return target_tile_index, target_chip_index

    @staticmethod
    def copy_board(board: Board):
        board_copy = Board(c3x3.board_border_len)
        board_copy.from_board_values_to_board(board.board_to_chip_values())
        return board_copy

    @staticmethod
    def place_chip_on_board_tile(board: Board, tile_index: int, chip: Chip):
        chip_copy = Chip(chip.value, row=tile_index / 3, col=tile_index % 3)
        board.chips[tile_index] = chip_copy

    def get_enemy_hand_chips_variations(self, current_state_data):
        possible_chip_values = self.get_possible_chips_values(current_state_data)

        previous_chip_value = 0
        enemy_hand_chips_variations = []
        for chip_value in possible_chip_values:
            if chip_value == previous_chip_value:
                continue
            previous_chip_value = chip_value

            copy_possible_chip_values = possible_chip_values.copy()
            copy_possible_chip_values.remove(chip_value)

            previous_child_chip_value = 0
            for child_chip_value in copy_possible_chip_values:
                if chip_value <= child_chip_value != previous_child_chip_value:
                    enemy_hand_chips_variations.append([Chip(chip_value), Chip(child_chip_value)])
                    previous_child_chip_value = child_chip_value

        return enemy_hand_chips_variations

    @staticmethod
    def get_possible_chips_values(current_state_data):
        all_chips_values = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]

        my_captured = current_state_data.my_captured
        enemy_captured = current_state_data.enemy_captured
        my_hand_chips = current_state_data.hand_chips_values_list
        board_values: list = current_state_data.board_values

        # Filter zero values
        updated_board_values = []
        for i in range(len(board_values)):
            if board_values[i] != 0:
                updated_board_values.append(board_values[i])

        for chip_value in my_captured:
            try:
                index = all_chips_values.index(chip_value)
                all_chips_values.pop(index)
            except ValueError:
                continue
        for chip_value in enemy_captured:
            try:
                index = all_chips_values.index(chip_value)
                all_chips_values.pop(index)
            except ValueError:
                continue
        for chip_value in my_hand_chips:
            try:
                index = all_chips_values.index(chip_value)
                all_chips_values.pop(index)
            except ValueError:
                continue
        for chip_value in updated_board_values:
            try:
                index = all_chips_values.index(chip_value)
                all_chips_values.pop(index)
            except ValueError:
                continue
        return all_chips_values
