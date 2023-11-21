class PlacingRelationInfo:
    def __init__(self, row, col, chip_value):
        self.row = row
        self.col = col
        self.chip_value = chip_value

        self.q_value = None

    def to_string(self):
        return f'\nPlacing Rel Info\nRow: {self.row}\nCol: {self.col}\nChip value: {self.chip_value}\nQValue: {self.q_value}\n'
