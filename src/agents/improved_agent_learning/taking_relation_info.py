class TakingRelationInfo:
    def __init__(self, combination, last_placed_chip):

        # [row, col, value, ...] repeating pattern of list
        self.combination = combination

        # [row, col, value] non-repeating
        self.last_placed_chip = last_placed_chip

        self.q_value = None
