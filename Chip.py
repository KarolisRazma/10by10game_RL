class Chip:
    def __init__(self, value):
        self.value = value
        # define chip position on the board
        # when chip is not placed, it's position is -1
        self.row = -1
        self.col = -1
    
    # setters
    def setRow(self, row):
        self.row = row
    def setCol(self, col):
        self.col = col
    
    # getters
    def getRow(self):
        return self.row
    def getCol(self):
        return self.col
    
    def getValue(self):
        return self.value
