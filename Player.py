class Player:

    # id = nickname of the player
    def __init__(self, nickname):
        self.id = nickname
        self.score = 0
        self.chips = []  # current chips in hand
        self.captured_chips = []  # chips captured = score

    # returns used chip and deletes it from player's inventory 
    def use_chip(self, chip_index):
        chip = self.chips[chip_index]
        del self.chips[chip_index]
        return chip
