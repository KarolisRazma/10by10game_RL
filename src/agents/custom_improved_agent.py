import random
from enum import Enum

from src.agents.actions.placing_action import PlaceChipAction
from src.agents.improved_agent import ImprovedAgent, Behaviour
from src.game_components.board import Board


class CustomImprovedAgent(ImprovedAgent):

    def __init__(self, name, graph, learning_algorithm, exploit_growth, explore_minimum,
                 is_improved_exploitation_on=False, exploit_to_closed_state_rate=0.0):
        super().__init__(name, graph, learning_algorithm, exploit_growth, explore_minimum,
                         is_improved_exploitation_on, exploit_to_closed_state_rate)
        self.is_strategy_applied = False

    # @Override
    def select_placing_action(self, game_board: Board):
        result_of_strategy = self.strategise_blue_tiles(game_board)

        if isinstance(result_of_strategy, PlaceChipAction):
            self.is_strategy_applied = True
            self.this_turn_behaviour = None
            return result_of_strategy
        else:
            self.is_strategy_applied = False
            return self.select_action(game_board)

    def select_taking_action(self, game_board, combinations):
        if not self.is_strategy_applied:
            # I think, I need to clarify this one:
            # If behaviour is EXPLORE, it means that we didn't have combination yet,
            # But if behaviour is EXPLOIT and the game let us choose combination,
            # Then it means, that we already know what combination we want to exploit.
            if self.this_turn_behaviour == Behaviour.EXPLORE:
                return self.do_explore_taking(combinations)
            else:
                return self.exploit_combination_in_this_turn
        else:
            return self.get_strategy_combination(combinations)

    @staticmethod
    def get_blue_tiles(game_board: Board):
        return [game_board.chips[0], game_board.chips[-1]]

    @staticmethod
    def is_blue_tiles_empty(game_board: Board):
        return game_board.is_tile_empty(0) and game_board.is_tile_empty(8)

    def strategise_blue_tiles(self, game_board: Board):
        if not self.is_blue_tiles_empty(game_board):
            blue_tiles = self.get_blue_tiles(game_board)
            if blue_tiles[0].value != 0 and blue_tiles[1].value != 0:
                if game_board.is_tile_empty(4):
                    for chip in self.hand_chips:
                        if blue_tiles[0].value + chip.value + blue_tiles[1].value == 4:
                            return PlaceChipAction(1, 1, chip.value)
            blue_tile = blue_tiles[0] if blue_tiles[0].value != 0 else blue_tiles[1]
            if blue_tile.row == 0:
                for chip in self.hand_chips:
                    if chip.value + blue_tile.value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
            elif blue_tile.row == 2:
                for chip in self.hand_chips:
                    if chip.value + blue_tile.value == 4:
                        if game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
        else:
            if not game_board.is_tile_empty(1):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[1].value == 4:
                        if game_board.is_tile_empty(2):
                            return PlaceChipAction(0, 2, chip.value)
                        elif game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
            if not game_board.is_tile_empty(2):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[2].value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
            if not game_board.is_tile_empty(3):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[3].value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(6):
                            return PlaceChipAction(2, 0, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
            if not game_board.is_tile_empty(5):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[5].value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(2):
                            return PlaceChipAction(0, 2, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
            if not game_board.is_tile_empty(6):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[6].value == 4:
                        if game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
            if not game_board.is_tile_empty(7):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[7].value == 4:
                        if game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
                        elif game_board.is_tile_empty(6):
                            return PlaceChipAction(2, 0, chip.value)

    @staticmethod
    def get_strategy_combination(combinations):
        for combination in combinations:
            for chip in combination:
                if (chip.row == 0 and chip.col == 0) or (chip.row == 2 or chip.col == 2):
                    return combination
        return combinations[random.randint(0, len(combinations) - 1)]


