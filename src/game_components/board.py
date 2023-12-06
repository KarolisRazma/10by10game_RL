import src.game_components.tile as t
import src.game_components.color as c
import src.game_components.chip as cp


class Board:
    def __init__(self, border_length):
        self.tiles = []
        # Chip(0) - chip which value - zero, is assumed to be viewed as empty space on the board
        self.chips = []
        self.border_length = border_length
        self.board_size = self.border_length * self.border_length
        self.create_board()

    def create_board(self):
        self.create_tiles()
        self.create_chips()

    def create_tiles(self):
        # 3x3 length board creation
        if self.border_length == 3:
            for i in range(self.board_size):
                if i == 0 or i == 8:
                    tile = t.Tile(c.Color.BLUE)
                    self.tiles.append(tile)
                    continue
                if i == 4:
                    tile = t.Tile(c.Color.RED)
                    self.tiles.append(tile)
                    continue
                tile = t.Tile(c.Color.WHITE)
                self.tiles.append(tile)
       
        # 5x5 length board creation
        if self.border_length == 5:
            for i in range(self.board_size):
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

    def create_chips(self):
        self.chips = [cp.Chip(0)] * self.board_size 

    def clear_chips(self):
        for i in range(self.board_size):
            if not self.is_tile_empty(i):
                self.chips[i] = cp.Chip(0)

    def remove_chip(self, index):
        if index < self.board_size:
            self.chips[index] = cp.Chip(0)

    def is_tile_empty(self, index):
        if index < self.board_size:
            if self.chips[index].value == 0:
                return True
            else:
                return False    

    def get_tile_at_index(self, index):
        if index < self.board_size:
            return self.tiles[index]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def board_to_string(self):
        board = ""
        for (i, chip) in zip(range(self.board_size), self.chips):
            if i % self.border_length == self.border_length - 1:
                board += str(chip.value) + "\n"
            else:
                board += str(chip.value) + " "
        return board

    def board_to_chip_values(self):
        return [chip.value for chip in self.chips]

    def from_board_values_to_board(self, board_values):
        for i in range(self.board_size):
            if board_values[i] == 0:
                chip = cp.Chip(0)
            elif board_values[i] == 1:
                chip = cp.Chip(1)
            elif board_values[i] == 2:
                chip = cp.Chip(2)
            elif board_values[i] == 3:
                chip = cp.Chip(3)
            chip.row = int(i / self.border_length)
            chip.col = i % self.border_length
            self.chips[i] = chip

