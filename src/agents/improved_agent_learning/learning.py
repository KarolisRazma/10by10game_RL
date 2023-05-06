class RLearning:
    def __init__(self):
        # Discount factor.
        # If the discount factor is zero, no regard is taken to what happens in the future.
        # Conversely, when the discount factor approaches one a long term high reward will be prioritized.

        # Learning rate.
        # A learning rate of zero would make the agent not learn anything new.
        # A learning rate of one would mean that only the most recent information is considered.

        self.discount_rate = 0.5  # gamma in math
        self.learning_rate = 0.5  # alpha in math

    def calc_new_state_value(self, graph, is_game_won, current_state_info, current_state_value, step_counter,
                             is_game_drawn):
        if step_counter == 1:
            reward = self.reward(is_game_won, is_game_drawn)
            new_state_value = reward
        else:
            max_next_state_value = graph.find_maximum_state_value(current_state_info)
            new_state_value = current_state_value + self.learning_rate * (0 + self.discount_rate * max_next_state_value
                                                                          - current_state_value)
        return new_state_value

    @staticmethod
    def reward(is_game_won, is_game_drawn):
        # Agent reached WIN
        if is_game_won:
            return 1000

        # Agent reached DRAW
        elif is_game_drawn:
            return 300

        # Agent reached LOSE
        if not is_game_won:
            return -1000
