from src.agents.actions.placing_action import PlaceChipAction
from src.agents.adhoc.adhoc_strategy import AdhocStrategy


class PlaceCenterStrategy(AdhocStrategy):
    def __init__(self):
        self.center_tile_index = 4
        self.center_row = 1
        self.center_col = 1

    def give_strategy_result(self, game_board, hand_chips):
        top_left_blue, bottom_right_blue = game_board.chips[0].value, game_board.chips[8].value

        if game_board.is_tile_empty(self.center_tile_index):
            both_blue_tiles = self.involves_both_tiles(hand_chips, top_left_blue, bottom_right_blue)
            if both_blue_tiles is not None:
                return both_blue_tiles
            any_blue_tile = self.involves_any_tile(hand_chips, top_left_blue, bottom_right_blue)
            if any_blue_tile is not None:
                return any_blue_tile
            both_white_tiles = self.process_both_white_tiles(game_board, hand_chips)
            if both_white_tiles is not None:
                return both_white_tiles
            any_white_tiles = self.process_any_white_tiles(game_board, hand_chips)
            if any_white_tiles is not None:
                return any_white_tiles
        return None

    def involves_both_tiles(self, hand_chips, first_chip_value, second_chip_value):
        for chip in hand_chips:
            if chip.value + first_chip_value + second_chip_value == 4:
                return PlaceChipAction(self.center_row, self.center_col, chip.value)
        return None

    def involves_any_tile(self, hand_chips, first_chip_value, second_chip_value):
        for chip in hand_chips:
            if chip.value + first_chip_value == 4:
                return PlaceChipAction(self.center_row, self.center_col, chip.value)
            elif chip.value + second_chip_value == 4:
                return PlaceChipAction(self.center_row, self.center_col, chip.value)
        return None

    def process_both_white_tiles(self, game_board, hand_chips):
        # [1] and [7]
        first_white_tile, second_white_tile = game_board.chips[1].value, game_board.chips[7].value
        both_white_tiles = self.involves_both_tiles(hand_chips, first_white_tile, second_white_tile)
        if both_white_tiles is not None:
            return both_white_tiles

        # [2] and [6]
        first_white_tile, second_white_tile = game_board.chips[2].value, game_board.chips[6].value
        both_white_tiles = self.involves_both_tiles(hand_chips, first_white_tile, second_white_tile)
        if both_white_tiles is not None:
            return both_white_tiles

        # [3] and [5]
        first_white_tile, second_white_tile = game_board.chips[3].value, game_board.chips[5].value
        both_white_tiles = self.involves_both_tiles(hand_chips, first_white_tile, second_white_tile)
        if both_white_tiles is not None:
            return both_white_tiles
        return None

    def process_any_white_tiles(self, game_board, hand_chips):
        # [1] and [7]
        first_white_tile, second_white_tile = game_board.chips[1].value, game_board.chips[7].value
        any_white_tiles = self.involves_any_tile(hand_chips, first_white_tile, second_white_tile)
        if any_white_tiles is not None:
            return any_white_tiles

        # [2] and [6]
        first_white_tile, second_white_tile = game_board.chips[2].value, game_board.chips[6].value
        any_white_tiles = self.involves_any_tile(hand_chips, first_white_tile, second_white_tile)
        if any_white_tiles is not None:
            return any_white_tiles

        # [3] and [5]
        first_white_tile, second_white_tile = game_board.chips[3].value, game_board.chips[5].value
        any_white_tiles = self.involves_any_tile(hand_chips, first_white_tile, second_white_tile)
        if any_white_tiles is not None:
            return any_white_tiles
        return None
