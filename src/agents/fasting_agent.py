import random

from src.agents.actions.placing_action import PlaceChipAction
from src.agents.improved_agent import ImprovedAgent, Behaviour
from src.game_components.board import Board


class FastingAgent(ImprovedAgent):

    def __init__(self, name, graph, learning_algorithm, exploit_growth, explore_minimum,
                 is_improved_exploitation_on=False, exploit_to_closed_state_rate=0.0):
        super().__init__(name, graph, learning_algorithm, exploit_growth, explore_minimum,
                         is_improved_exploitation_on, exploit_to_closed_state_rate)
        self.is_strategy_applied = False

    # @Override
    def select_placing_action(self, game_board: Board):
        result_of_strategy = self.strategise(game_board)

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

    def strategise(self, game_board: Board):
        # 0 1 2    -4 -3 -2
        # 3 4 5    -1  *  +1
        # 6 7 8    +2  +3 +4
        for tile_index in range(len(game_board.tiles)):
            if game_board.is_tile_empty(tile_index):
                for chip in self.hand_chips:
                    is_scorable = False
                    if tile_index - 4 >= 0 and game_board.is_tile_empty(tile_index - 4) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index - 3 >= 0 and game_board.is_tile_empty(tile_index - 3) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index - 2 >= 0 and game_board.is_tile_empty(tile_index - 2) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index - 1 >= 0 and game_board.is_tile_empty(tile_index - 1) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index + 1 >= 0 and game_board.is_tile_empty(tile_index + 1) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index + 2 >= 0 and game_board.is_tile_empty(tile_index + 2) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index + 3 >= 0 and game_board.is_tile_empty(tile_index + 3) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if tile_index + 4 >= 0 and game_board.is_tile_empty(tile_index + 4) \
                            and chip.value + game_board.chips[tile_index].value == 4:
                        is_scorable = True
                    if not is_scorable:
                        return PlaceChipAction(int(tile_index / 3), tile_index % 3, chip.value)
        return False

    @staticmethod
    def get_strategy_combination(combinations):
        for combination in combinations:
            for chip in combination:
                if (chip.row == 0 and chip.col == 0) or (chip.row == 2 or chip.col == 2):
                    return combination
        return combinations[random.randint(0, len(combinations) - 1)]
