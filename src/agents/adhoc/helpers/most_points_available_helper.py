from src.agents.actions.placing_action import PlaceChipAction
from src.agents.adhoc.adhoc_helper import AdhocHelper


class MostPointsAvailableHelper(AdhocHelper):

    def __init__(self):
        self.top_left = 0
        self.top_left_row = 0
        self.top_left_col = 0

        self.top_center = 1
        self.top_center_row = 0
        self.top_center_col = 1

        self.top_right = 2
        self.top_right_row = 0
        self.top_right_col = 2

        self.center_left = 3
        self.center_left_row = 1
        self.center_left_col = 0

        self.center = 4
        self.center_row = 1
        self.center_col = 1

        self.center_right = 5
        self.center_right_row = 1
        self.center_right_col = 2

        self.bottom_left = 6
        self.bottom_left_row = 2
        self.bottom_left_col = 0

        self.bottom_center = 7
        self.bottom_center_row = 2
        self.bottom_center_col = 1

        self.bottom_right = 8
        self.bottom_right_row = 2
        self.bottom_right_col = 2

    def give_helper_result(self, game_board, hand_chips, ignore_blue=False):
        return self.get_most_points_available(game_board, hand_chips, ignore_blue)

    def get_most_points_available(self, game_board, hand_chips, ignore_blue):
        four_points_place_action = self.process_four_points_placements(game_board, hand_chips)
        if four_points_place_action is not None:
            return 4
        three_points_place_action = self.process_three_points_placements(game_board, hand_chips)
        if three_points_place_action is not None:
            return 3
        two_points_place_action = self.process_two_points_placements(game_board, hand_chips, ignore_blue)
        if two_points_place_action is not None:
            return 2
        one_point_place_action = self.process_one_point_placements(game_board, hand_chips, ignore_blue)
        if one_point_place_action is not None:
            return 1
        return 0

    def process_four_points_placements(self, game_board, hand_chips):
        if game_board.is_tile_empty(self.center) and not game_board.is_tile_empty(self.top_left) \
                and not game_board.is_tile_empty(self.bottom_right):
            first_chip_value = game_board.chips[self.top_left].value
            second_chip_value = game_board.chips[self.bottom_right].value

            return self.involves_both_tiles(hand_chips, first_chip_value, second_chip_value, self.center_row,
                                            self.center_col)
        return None

    def process_three_points_placements(self, game_board, hand_chips):
        # Clockwise start here (top 1/right 5/bottom 7/left 3)
        result = self.check_line(target=self.top_center, target_row=self.top_center_row,
                                 target_col=self.top_center_col, first=self.top_left, second=self.top_right,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        result = self.check_line(target=self.center_right, target_row=self.center_right_row,
                                 target_col=self.center_right_col, first=self.top_right, second=self.bottom_right,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        result = self.check_line(target=self.bottom_center, target_row=self.bottom_center_row,
                                 target_col=self.bottom_center_col, first=self.bottom_left,
                                 second=self.bottom_right,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        result = self.check_line(target=self.center_left, target_row=self.center_left_row,
                                 target_col=self.center_left_col, first=self.top_left, second=self.bottom_left,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        # Clockwise ends here

        # Repeating lines starts here
        # Pair 1
        result = self.check_line(target=self.top_right, target_row=self.top_right_row,
                                 target_col=self.top_right_col, first=self.top_left, second=self.top_center,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.top_right, target_row=self.top_right_row,
                                 target_col=self.top_right_col, first=self.bottom_right, second=self.center_right,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        # Pair 2
        result = self.check_line(target=self.bottom_left, target_row=self.bottom_left_row,
                                 target_col=self.bottom_left_col, first=self.top_left, second=self.center_left,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.bottom_left, target_row=self.bottom_left_row,
                                 target_col=self.bottom_left_col, first=self.bottom_right,
                                 second=self.bottom_center,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        return None

    def process_two_points_placements(self, game_board, hand_chips, ignore_blue):
        # Center
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.top_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.bottom_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.top_center, second=self.bottom_center,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.center_left, second=self.center_right,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.top_right, second=self.bottom_left,
                                 game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        if not ignore_blue:
            # Top Left
            result = self.check_line(target=self.top_left, target_row=self.top_left_row,
                                     target_col=self.top_left_col, first=self.top_center, second=self.top_right,
                                     game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result
            result = self.check_line(target=self.top_left, target_row=self.top_left_row,
                                     target_col=self.top_left_col, first=self.center, second=self.bottom_right,
                                     game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result
            result = self.check_line(target=self.top_left, target_row=self.top_left_row,
                                     target_col=self.top_left_col, first=self.center_left, second=self.bottom_left,
                                     game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result

            # Bottom Right
            result = self.check_line(target=self.bottom_right, target_row=self.bottom_right_row,
                                     target_col=self.bottom_right_col, first=self.center_right, second=self.top_right,
                                     game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result
            result = self.check_line(target=self.bottom_right, target_row=self.bottom_right_row,
                                     target_col=self.bottom_right_col, first=self.center, second=self.top_left,
                                     game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result
            result = self.check_line(target=self.bottom_right, target_row=self.bottom_right_row,
                                     target_col=self.bottom_right_col, first=self.bottom_center,
                                     second=self.bottom_left,
                                     game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result

        # Clockwise
        result = self.check_tile(target=self.top_center, target_row=self.top_center_row, target_col=self.top_center_col,
                                 first=self.top_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center_right, target_row=self.center_right_row,
                                 target_col=self.center_right_col,
                                 first=self.bottom_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.bottom_center, target_row=self.bottom_center_row,
                                 target_col=self.bottom_center_col,
                                 first=self.bottom_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center_left, target_row=self.center_left_row,
                                 target_col=self.center_left_col,
                                 first=self.top_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        return None

    def process_one_point_placements(self, game_board, hand_chips, ignore_blue):
        # Center
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.top_center, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.top_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.center_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.bottom_center, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.bottom_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center, target_row=self.center_row, target_col=self.center_col,
                                 first=self.center_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result

        if not ignore_blue:
            # Top Left
            result = self.check_tile(target=self.top_left, target_row=self.top_left_row, target_col=self.top_left_col,
                                     first=self.top_center, game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result
            result = self.check_tile(target=self.top_left, target_row=self.top_left_row, target_col=self.top_left_col,
                                     first=self.center_left, game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result

            # Bottom Right
            result = self.check_tile(target=self.bottom_right, target_row=self.bottom_right_row,
                                     target_col=self.bottom_right_col,
                                     first=self.center_right, game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result
            result = self.check_tile(target=self.bottom_right, target_row=self.bottom_right_row,
                                     target_col=self.bottom_right_col,
                                     first=self.bottom_center, game_board=game_board, hand_chips=hand_chips)
            if result is not None:
                return result

        # Clockwise
        result = self.check_tile(target=self.top_center, target_row=self.top_center_row,
                                 target_col=self.top_center_col,
                                 first=self.top_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.top_center, target_row=self.top_center_row, target_col=self.top_center_col,
                                 first=self.center, second=self.bottom_center, game_board=game_board,
                                 hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center_right, target_row=self.center_right_row,
                                 target_col=self.center_right_col,
                                 first=self.top_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.center_right, target_row=self.center_right_row,
                                 target_col=self.center_right_col,
                                 first=self.center, second=self.center_left, game_board=game_board,
                                 hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.bottom_center, target_row=self.bottom_center_row,
                                 target_col=self.bottom_center_col,
                                 first=self.bottom_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.bottom_center, target_row=self.bottom_center_row,
                                 target_col=self.bottom_center_col,
                                 first=self.center, second=self.top_center, game_board=game_board,
                                 hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.center_left, target_row=self.center_left_row,
                                 target_col=self.center_left_col,
                                 first=self.bottom_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.center_left, target_row=self.center_left_row,
                                 target_col=self.center_left_col,
                                 first=self.center, second=self.center_right, game_board=game_board,
                                 hand_chips=hand_chips)
        if result is not None:
            return result

        # Top Right
        result = self.check_tile(target=self.top_right, target_row=self.top_right_row,
                                 target_col=self.top_right_col,
                                 first=self.top_center, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.top_right, target_row=self.top_right_row,
                                 target_col=self.top_right_col,
                                 first=self.center_right, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.top_right, target_row=self.top_right_row,
                                 target_col=self.top_right_col,
                                 first=self.center, second=self.bottom_left, game_board=game_board,
                                 hand_chips=hand_chips)
        if result is not None:
            return result

        # Bottom Left
        result = self.check_tile(target=self.bottom_left, target_row=self.bottom_left_row,
                                 target_col=self.bottom_left_col,
                                 first=self.center_left, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_tile(target=self.bottom_left, target_row=self.bottom_left_row,
                                 target_col=self.bottom_left_col,
                                 first=self.bottom_center, game_board=game_board, hand_chips=hand_chips)
        if result is not None:
            return result
        result = self.check_line(target=self.bottom_left, target_row=self.bottom_left_row,
                                 target_col=self.bottom_left_col,
                                 first=self.center, second=self.top_right, game_board=game_board,
                                 hand_chips=hand_chips)
        if result is not None:
            return result

        return None

    def check_line(self, target, target_row, target_col, first, second, game_board, hand_chips):
        if game_board.is_tile_empty(target) and not game_board.is_tile_empty(first) \
                and not game_board.is_tile_empty(second):
            first_chip_value = game_board.chips[first].value
            second_chip_value = game_board.chips[second].value
            result = self.involves_both_tiles(hand_chips, first_chip_value, second_chip_value, target_row,
                                              target_col)
            if result is not None:
                return result
        return None

    def check_tile(self, target, target_row, target_col, first, game_board, hand_chips):
        if game_board.is_tile_empty(target) and not game_board.is_tile_empty(first):
            first_chip_value = game_board.chips[first].value
            result = self.involves_tile(hand_chips, first_chip_value, target_row, target_col)
            if result is not None:
                return result
        return None

    @staticmethod
    def involves_both_tiles(hand_chips, first_chip_value, second_chip_value, row, col):
        for chip in hand_chips:
            if chip.value + first_chip_value + second_chip_value == 4:
                return PlaceChipAction(row, col, chip.value)
        return None

    @staticmethod
    def involves_tile(hand_chips, first_chip_value, row, col):
        for chip in hand_chips:
            if chip.value + first_chip_value == 4:
                return PlaceChipAction(row, col, chip.value)
        return None
