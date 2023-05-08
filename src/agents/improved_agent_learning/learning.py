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

    def calc_new_q_value(self, graph, state_info, relation_info, is_final_state, is_game_won, is_game_drawn):
        current_q_value = relation_info.q_value

        if is_final_state:
            reward = self.reward(is_game_won, is_game_drawn)
            new_q_value = reward
        else:
            # max_next_state_value = graph.find_maximum_state_value(state_info)
            max_next_state_q_value = graph.find_max_next_state_q_value(state_info)
            new_q_value = current_q_value + self.learning_rate * (self.discount_rate * max_next_state_q_value
                                                                  - current_q_value)
        return new_q_value

    @staticmethod
    def reward(is_game_won, is_game_drawn):
        # Agent reached WIN
        if is_game_won:
            return 100000

        # Agent reached DRAW
        elif is_game_drawn:
            return 30000

        # Agent reached LOSE
        if not is_game_won:
            return -100000
