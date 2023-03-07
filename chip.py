class Chip:
    def __init__(self, value):
        self.value = value
        # define chip position on the board
        # when chip is not placed, it's position is -1
        self.row = -1
        self.col = -1

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
