from src.agents.adhoc.adhoc_strategy import AdhocStrategy
from src.game_components.color import Color


class TakeMostPointsStrategy(AdhocStrategy):

    def give_strategy_result(self, game_board, combinations, last_placed_chip):
        total_points_per_combination = []
        for combination in combinations:
            points = self.calculate_points(game_board, combination, last_placed_chip)
            total_points_per_combination.append(points)

        maximum_points = max(total_points_per_combination)
        return combinations[total_points_per_combination.index(maximum_points)]

    @staticmethod
    def calculate_points(game_board, combination, last_placed_chip):
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
