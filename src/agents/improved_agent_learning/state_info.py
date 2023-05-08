class StateInfo:
    def __init__(self, board_values, my_turn, my_score, enemy_score, chips_left):
        self.board_values = board_values
        self.my_turn = my_turn
        self.my_score = my_score
        self.enemy_score = enemy_score
        self.chips_left = chips_left

        # Counters
        self.times_visited = None
        self.win_counter = None
        self.lose_counter = None
        self.draw_counter = None

        # Flag
        self.is_initial_state = False

    def set_counters(self, times_visited, win_counter, lose_counter, draw_counter):
        self.times_visited = times_visited
        self.win_counter = win_counter
        self.lose_counter = lose_counter
        self.draw_counter = draw_counter
