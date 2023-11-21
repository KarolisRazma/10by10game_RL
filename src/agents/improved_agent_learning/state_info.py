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

    def print(self):
        print("StateInfo data")
        print(f'Board values: {self.board_values}')
        print(f'Is my turn: {self.my_turn}')
        print(f'My score: {self.my_score}')
        print(f'Enemy score: {self.enemy_score}')
        print(f'Chips left: {self.chips_left}')
        print(f'Times visited: {self.times_visited}')
        print(f'Win: {self.win_counter}')
        print(f'Lose: {self.lose_counter}')
        print(f'Draw: {self.draw_counter}')

    def to_string(self):
        return f'\nStateInfo data\n' + \
               f'Board values: {self.board_values}\n' + \
               f'Is my turn: {self.my_turn}\n' + \
               f'My score: {self.my_score}\n' + \
               f'Enemy score: {self.enemy_score}\n' + \
               f'Chips left: {self.chips_left}\n' + \
               f'Times visited: {self.times_visited}\n' + \
               f'Win: {self.win_counter}\n' + \
               f'Lose: {self.lose_counter}\n' + \
               f'Draw: {self.draw_counter}\n'
