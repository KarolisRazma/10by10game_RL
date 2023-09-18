class Chip:
    def __init__(self, value, row=-1, col=-1):
        self.value = value
        # define chip position on the board
        # when chip is not placed, it's position is -1
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
