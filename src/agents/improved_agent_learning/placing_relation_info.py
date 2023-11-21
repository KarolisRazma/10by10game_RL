class PlacingRelationInfo:
    def __init__(self, row, col, chip_value):
        self.row = row
        self.col = col
        self.chip_value = chip_value

        self.q_value = 0.0
