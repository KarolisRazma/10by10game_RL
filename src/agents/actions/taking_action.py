# defining short class TakeChipsAction for the Agent class
# its purpose is to represent agent's action to take chips from the board
class TakeChipsAction:
    def __init__(self, combination_index):
        self.combination_index = combination_index
