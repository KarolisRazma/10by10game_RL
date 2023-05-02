# defining short class PlaceChipAction for the Agent class
# its purpose is to represent agent's action to place chip on the board
class PlaceChipAction:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value


