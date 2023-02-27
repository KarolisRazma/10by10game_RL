import Tile
import Color


class Board:
    def __init__(self):
        self.tiles = []
        self.chips = [None] * 25
        self.create_tiles()

    def create_tiles(self):
        for i in range(25):
            if i == 0 or i == 4 or i == 12 or i == 20 or i == 24:
                tile = Tile.Tile(Color.Color.BLUE)
                self.tiles.append(tile)
                continue
            if i == 6 or i == 8 or i == 16 or i == 18:
                tile = Tile.Tile(Color.Color.RED)
                self.tiles.append(tile)
                continue
            tile = Tile.Tile(Color.Color.WHITE)
            self.tiles.append(tile)

    def is_tile_empty(self, index):
        if self.chips[index] is None:
            return True
        else:
            return False

    # get chip
    def get_chip_at_index(self, index):
        if not self.is_tile_empty(index):
            return self.chips[index]

    # get tile
    def get_tile_at_index(self, index):
        return self.tiles[index]

    # cli interface display (clunky)
    def display(self):
        for (i, chip) in zip(range(25), self.chips):
            if i % 5 == 4:
                if chip is None:
                    print(0)
                    continue
                print(chip.get_value())
                continue
            if chip is None:
                print(0, end=" ")
                continue
            print("{}".format(chip.get_value()), end=" ")
