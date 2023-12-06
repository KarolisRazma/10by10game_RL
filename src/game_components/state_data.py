class StateData:
    def __init__(self, board_values, my_turn, my_score, enemy_score, chips_left, last_placed_chip_list,
                 hand_chips_values_list, enemy_hand_chips_values_list, container_chips_values_list,
                 is_initial_state=False):
        self.board_values = board_values
        self.my_turn = my_turn
        self.my_score = my_score
        self.enemy_score = enemy_score
        self.chips_left = chips_left
        self.last_placed_chip_list = last_placed_chip_list
        self.hand_chips_values_list = hand_chips_values_list
        self.enemy_hand_chips_values_list = enemy_hand_chips_values_list
        self.container_chips_values_list = container_chips_values_list
        self.is_initial_state = is_initial_state
