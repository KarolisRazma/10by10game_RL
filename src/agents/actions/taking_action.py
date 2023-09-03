# defining short class TakeChipsAction for the Agent class
# its purpose is to represent agent's action to take chips from the board
class TakeChipsAction:
    def __init__(self, combination_index):
        self.combination_index = combination_index


# IMPORTANT NOTE:
# This class is not used, the taking action itself is construct of chip type objects (chips list)
# It should be deleted at some time
