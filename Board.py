import Tile as t
import Color as c

class Board:
    def __init__(self):
        self.tiles = []
        self.chips = [None] * 25
        self.createTiles()

    def createTiles(self):
        for i in range(25):
            if i == 0 or i == 4 or i == 12 or i == 20 or i == 24:
                tile = t.Tile(c.Color.BLUE)
                self.tiles.append(tile)
                continue
            if i == 6 or i == 8 or i == 16 or i == 18:
                tile = t.Tile(c.Color.RED)
                self.tiles.append(tile)
                continue
            tile = t.Tile(c.Color.WHITE)
            self.tiles.append(tile)

    # expected to get row and column already configured to be an index (row-- and column--)
    def isTileEmpty(self, row, column):
        if self.chips[row * 5 + column] is None:
            return True
        else:
            return False
    # same but parameter is index
    def isTileEmpty(self, index):
        if self.chips[index] is None:
            return True
        else:
            return False

    # get chip
    def getChipAtIndex(self, index):
        if not self.isTileEmpty(index):
            return self.chips[index]
    # get tile
    def getTileAtIndex(self, index):
        return self.tiles[index]
    
    # cli interface display (clunky)
    def display(self):
        for (i, chip) in zip(range(25), self.chips):
            if i % 5 == 4:
                if chip is None:
                    print(0)
                    continue
                print(chip.getValue())
                continue
            if chip is None:
                print(0, end = " ")
                continue
            print("{}".format(chip.getValue()), end = " ")