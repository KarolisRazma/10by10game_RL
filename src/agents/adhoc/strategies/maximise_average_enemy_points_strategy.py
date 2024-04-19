# import random
#
# from src.agents.adhoc.adhoc_strategy import AdhocStrategy
# from src.agents.adhoc.commons.reusable_functions import ReusableFunctions
# from src.agents.adhoc.strategies.minimize_enemy_points_strategy import MinimizeEnemyPointsStrategy
# from src.agents.adhoc.strategies.take_least_points_strategy import TakeLeastPointsStrategy
# from src.game_components.board import Board
# from src.game_components.state_data import StateData
# import src.utilities.constants3x3 as c3x3
#
#
# class MaximizeAverageEnemyPointsStrategy(AdhocStrategy):
#
#     def __init__(self):
#         self.minimize_enemy_points_strategy = MinimizeEnemyPointsStrategy()
#         self.reusable_functions = ReusableFunctions()
#         self.take_least_points_strategy = TakeLeastPointsStrategy()
#
#     def process_tile(self, game_board, tile_index, hand_chips, enemy_hand_chips_variations):
#         if game_board.is_tile_empty(tile_index):
#             for chip, chip_index in zip(hand_chips, range(len(hand_chips))):
#                 # Update board
#                 board_copy = self.copy_board(game_board)
#                 self.place_chip_on_board_tile(board_copy, tile_index, chip)
#                 last_placed_chip = board_copy.chips[tile_index]
#
#                 combinations = self.reusable_functions.get_combinations_by_board_values(
#                     last_placed_chip, board_copy.board_to_chip_values())
#
#                 agent_min_points = 0
#                 if combinations:
#                     combination = self.take_least_points_strategy.give_strategy_result(board_copy, combinations,
#                                                                                        last_placed_chip)
#                     agent_min_points = self.reusable_functions.get_points_by_combination(board_copy, combination,
#                                                                                          last_placed_chip)
#                     self.reusable_functions.update_board_by_combination(board_copy, combination, last_placed_chip)
#
#                 board_copy_for_enemy = self.copy_board(board_copy)
#                 for enemy_tile_index in range(len(board_copy_for_enemy.tiles)):
#                     if board_copy_for_enemy.is_tile_empty(tile_index):
#                         for enemy_hand_chips in enemy_hand_chips_variations:
#                             for enemy_chip in enemy_hand_chips:
#                                 board_second_copy_for_enemy = self.copy_board(board_copy_for_enemy)
#                                 self.place_chip_on_board_tile(board_second_copy_for_enemy, enemy_tile_index, enemy_chip)
#                                 enemy_last_placed_chip = board_second_copy_for_enemy.chips[enemy_tile_index]
#                                 enemy_combinations = self.reusable_functions.get_combinations_by_board_values(
#                                     enemy_last_placed_chip, board_second_copy_for_enemy.board_to_chip_values())
#
#                                 enemy_points = 0
#                                 if enemy_combinations:
#                                     enemy_combination = enemy_combinations[random.randint(0, len(enemy_combinations) - 1)]
#                                     enemy_points = self.reusable_functions.get_points_by_combination(
#                                         board_second_copy_for_enemy,
#                                         enemy_combination,
#                                         enemy_last_placed_chip)
#                                 enemy_points_sum += enemy_points
#
#                             if enemy_points > enemy_max_points:
#                                 enemy_max_points = enemy_points
#
#     def give_strategy_result(self, game_board: Board, hand_chips, current_state_data: StateData):
#         enemy_hand_chips_variations = self.minimize_enemy_points_strategy.get_enemy_hand_chips_variations(
#             current_state_data)
#
#         for tile_index in range(len(game_board.tiles)):
#             self.minimize_enemy_points_strategy.process_tile(game_board, tile_index, hand_chips,
#                                                              enemy_hand_chips_variations)
#
#     @staticmethod
#     def copy_board(board: Board):
#         board_copy = Board(c3x3.board_border_len)
#         board_copy.from_board_values_to_board(board.board_to_chip_values())
#         return board_copy
#
#     @staticmethod
#     def place_chip_on_board_tile(board: Board, tile_index: int, chip: Chip):
#         chip_copy = Chip(chip.value, row=tile_index / 3, col=tile_index % 3)
#         board.chips[tile_index] = chip_copy
