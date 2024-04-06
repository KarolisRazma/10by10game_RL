from src.agents.actions.placing_action import PlaceChipAction
from src.agents.adhoc.adhoc_strategy import AdhocStrategy
from src.game_components.board import Board
from src.game_components.state_data import StateData


class AdvancedFirstMoveStrategy(AdhocStrategy):
    def __init__(self):
        self.center_tile_index = 4

        # self.top_right = 2
        # self.top_right_row = 0
        # self.top_right_col = 2

        self.center_left_row = 1
        self.center_left_col = 0

        self.center_row = 1
        self.center_col = 1

        self.center_right_row = 1
        self.center_right_col = 2

    def give_strategy_result(self, game_board: Board, hand_chips, state_data: StateData):
        if state_data.is_initial:
            return self.play_as_first_player(game_board, hand_chips)
        else:
            return self.play_as_second_player(game_board, hand_chips)

    def play_as_first_player(self, game_board, hand_chips):
        center_value = game_board.chips[self.center_tile_index].value
        for chip in hand_chips:
            if chip.value + center_value != 4:
                return PlaceChipAction(row=self.center_right_row, col=self.center_right_col, value=chip.value)
        # If both chips make combination, there's no difference which one of the chips to place
        return PlaceChipAction(row=self.center_right_row, col=self.center_right_col, value=hand_chips[0].value)

    def play_as_second_player(self, game_board, hand_chips):
        if not game_board.is_tile_empty(0):
            chip_on_blue_value = game_board.chips[0].value
            for chip in hand_chips:
                if chip.value + chip_on_blue_value == 4:
                    if game_board.is_tile_empty(self.center_tile_index):
                        return PlaceChipAction(row=self.center_row, col=self.center_col, value=chip.value)
                    else:
                        return PlaceChipAction(row=self.center_left_row, col=self.center_left_col, value=chip.value)
            biggest_chip_value = (max(hand_chips, key=lambda x: x.value)).value
            return PlaceChipAction(row=self.center_left_row, col=self.center_left_col, value=biggest_chip_value)

        if not game_board.is_tile_empty(8):
            chip_on_blue_value = game_board.chips[8].value
            for chip in hand_chips:
                if chip.value + chip_on_blue_value == 4:
                    if game_board.is_tile_empty(self.center_tile_index):
                        return PlaceChipAction(row=self.center_row, col=self.center_col, value=chip.value)
                    else:
                        return PlaceChipAction(row=self.center_left_row, col=self.center_left_col, value=chip.value)
            biggest_chip_value = (max(hand_chips, key=lambda x: x.value)).value
            return PlaceChipAction(row=self.center_right_row, col=self.center_right_col, value=biggest_chip_value)

        if game_board.is_tile_empty(self.center_tile_index):
            for i in range(9):
                if not game_board.is_tile_empty(i):
                    chip_on_white_value = game_board.chips[i].value
                    for chip in hand_chips:
                        if chip.value + chip_on_white_value == 4:
                            return PlaceChipAction(row=self.center_row, col=self.center_col, value=chip.value)

        if game_board.is_tile_empty(3):
            return PlaceChipAction(row=self.center_left_row, col=self.center_left_col, value=hand_chips[0].value)
        if game_board.is_tile_empty(5):
            return PlaceChipAction(row=self.center_right_row, col=self.center_right_col, value=hand_chips[0].value)
