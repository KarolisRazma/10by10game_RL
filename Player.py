class Player:

    # id = nickname of the player
    def __init__(self, id):
        self.id = id 
        self.score = 0
        self.chips = [] # current chips in hand
        self.capturedChips = [] # chips captured = score
        self.wins = 0 # this games is should be bo2 (still not implemented)

    # returns used chip and deletes it from player's inventory 
    def useChip(self, chipIndex):
        chip = self.chips[chipIndex]
        del self.chips[chipIndex]
        return chip