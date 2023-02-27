class Chip:
    def __init__(self, value):
        self.value = value
        # define chip position on the board
        # when chip is not placed, it's position is -1
        self.row = -1
        self.col = -1

    # setters
    def set_row(self, row):
        self.row = row

    def set_col(self, col):
        self.col = col

    # getters
    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def get_value(self):
        return self.value
