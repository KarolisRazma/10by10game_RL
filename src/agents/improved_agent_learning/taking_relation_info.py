class TakingRelationInfo:
    def __init__(self, combination, last_placed_chip):

        # [chip1, chip2, chip3, ...]
        self.combination = combination

        # [row, col, value]
        self.last_placed_chip = last_placed_chip

        self.q_value = 0.0
