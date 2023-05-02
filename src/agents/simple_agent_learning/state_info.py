class StateInfo:
    def __init__(self, board_values, my_turn, my_score, enemy_score, chips_left):
        self.board_values = board_values
        self.my_turn = my_turn
        self.my_score = my_score
        self.enemy_score = enemy_score
        self.chips_left = chips_left

        # Do not need to assign any value on object creation
        self.state_value = None
