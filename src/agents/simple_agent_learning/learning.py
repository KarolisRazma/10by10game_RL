class RLearning:
    def __init__(self):
        # Parameters
        self.discount_rate = 0.5  # gamma in math
        self.learning_rate = 0.5  # alpha in math

        # Probability distributions
        self.take_best_node = 0.75
        self.take_random_node = 0.25

    def calc_new_state_value(self, graph, is_game_won, current_state_info, current_state_value, step_counter):
        # TODO what value should I assign if it's top of the path?
        if step_counter > 1:
            max_next_state_value = graph.find_maximum_state_value(current_state_info)
        else:
            # TODO, temporary solution
            max_next_state_value = 1 if is_game_won else -1

        # Q learning
        new_state_value = current_state_value + self.learning_rate * (self.reward(is_game_won, step_counter) +
                          self.discount_rate * max_next_state_value - current_state_value)
        return new_state_value


    @staticmethod
    def reward(is_game_won, step_counter):
        # TODO improve reward func
        if is_game_won:
            return 1.0 / float(step_counter)
        return -1.0 / float(step_counter)

