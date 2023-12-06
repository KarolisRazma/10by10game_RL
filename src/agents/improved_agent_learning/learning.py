from src.game_components.game_result import GameResult


class RLearning:
    def __init__(self, discount_rate, learning_rate):
        # Discount factor.
        # If the discount factor is zero, no regard is taken to what happens in the future.
        # Conversely, when the discount factor approaches one a long term high reward will be prioritized.

        # Learning rate.
        # A learning rate of zero would make the agent not learn anything new.
        # A learning rate of one would mean that only the most recent information is considered.

        self.discount_rate: float = discount_rate  # gamma in math
        self.learning_rate: float = learning_rate  # alpha in math

    def calc_new_q_value(self, graph, state_data, relation_data):
        current_q_value = relation_data.q_value

        max_next_state_q_value = graph.find_max_next_state_q_value(state_data)
        new_q_value = current_q_value + self.learning_rate * (self.discount_rate * max_next_state_q_value
                                                              - current_q_value)
        return float(new_q_value)

    def final_state_reward(self, last_game_result):
        return self.reward(last_game_result)

    @staticmethod
    def reward(last_game_result):
        if last_game_result == GameResult.WON:
            return 100000.0

        elif last_game_result == GameResult.LOST:
            return -100000.0

        elif last_game_result == GameResult.DRAW:
            return 5000.0
