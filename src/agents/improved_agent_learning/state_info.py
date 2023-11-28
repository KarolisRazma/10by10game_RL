class StateInfo:
    def __init__(self, board_values, my_turn, my_score, enemy_score,
                 chips_left, hand_chips_values, last_placed_chip, is_initial_state=False):
        self.board_values = board_values
        self.my_turn = my_turn
        self.my_score = my_score
        self.enemy_score = enemy_score
        self.chips_left = chips_left
        self.hand_chips_values = hand_chips_values
        self.last_placed_chip = last_placed_chip

        # Not in the agent's knowledge
        self.container = None

        # Counters
        self.times_visited = 0
        self.win_counter = 0
        self.lose_counter = 0
        self.draw_counter = 0

        # Flag
        self.is_initial_state = is_initial_state
        self.is_closed = False
