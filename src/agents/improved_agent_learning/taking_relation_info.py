class TakingRelationInfo:
    def __init__(self, combination, last_placed_chip):

        # [chip1, chip2, chip3, ...]
        self.combination = combination

        # [row, col, value]
        self.last_placed_chip = last_placed_chip

        self.q_value = None

    def to_string(self):
        return f'\nTaking Rel Info\nCombination: {self.combination}\nLast placed chip: {self.last_placed_chip}\nQValue: {self.q_value}\n'
