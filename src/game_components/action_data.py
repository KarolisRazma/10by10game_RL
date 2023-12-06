from src.game_components.chip import Chip


class ActionData:
    def __init__(self, row, col, chip_value, has_taking=False, combination=None):
        # Placing
        if combination is None:
            combination = []
        self.row = row
        self.col = col
        self.chip_value = chip_value

        # Taking
        self.has_taking = has_taking
        self.combination: list[Chip] = combination
