from src.agents.actions.placing_action import PlaceChipAction
from src.agents.adhoc.adhoc_strategy import AdhocStrategy
from src.game_components.board import Board


class BringBackToContainerStrategy(AdhocStrategy):

    def __init__(self):
        self.center_index = 4

    def give_strategy_result(self, game_board: Board, hand_chips):
        if not game_board.is_tile_empty(self.center_index):
            center_value = game_board.chips[self.center_index].value

            for chip in hand_chips:
                if chip.value + center_value == 4:
                    for tile_index in range(len(game_board.tiles)):
                        if game_board.is_tile_empty(tile_index):
                            return PlaceChipAction(row=int(tile_index / 3), col=tile_index % 3, value=chip.value)
        return None
