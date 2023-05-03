class StateInfo:
    def __init__(self, board_values, my_turn, my_score, enemy_score, chips_left,
                 times_visited, win_counter, lose_counter, draw_counter):
        self.board_values = board_values
        self.my_turn = my_turn
        self.my_score = my_score
        self.enemy_score = enemy_score
        self.chips_left = chips_left

        # Do not need to assign any value on object creation
        self.state_value = None
        # Assign this value after drawing new chip, when everything is done in a round
        self.chips_in_hand = None

        # Counters
        self.times_visited = times_visited
        self.win_counter = win_counter
        self.lose_counter = lose_counter
        self.draw_counter = draw_counter
