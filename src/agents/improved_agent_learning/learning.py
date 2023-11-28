import time

from src.game_components.game_result import GameResult


class RLearning:
    def __init__(self, discount_rate, learning_rate):
        # Discount factor.
        # If the discount factor is zero, no regard is taken to what happens in the future.
        # Conversely, when the discount factor approaches one a long term high reward will be prioritized.

        # Learning rate.
        # A learning rate of zero would make the agent not learn anything new.
        # A learning rate of one would mean that only the most recent information is considered.

        self.discount_rate = discount_rate  # gamma in math
        self.learning_rate = learning_rate  # alpha in math

        self.bench1 = []  # Execute find_max_next_state_q_value

    def calc_new_q_value(self, graph, state_info, relation_info, is_final_state, last_game_result):
        current_q_value = relation_info.q_value

        if is_final_state:
            reward = self.reward(last_game_result)
            new_q_value = reward
        else:
            start_timer = time.time()
            max_next_state_q_value = graph.find_max_next_state_q_value(state_info)
            new_q_value = current_q_value + self.learning_rate * (self.discount_rate * max_next_state_q_value
                                                                  - current_q_value)
            end_timer = time.time()
            self.bench1.append(end_timer - start_timer)

        return new_q_value

    @staticmethod
    def reward(last_game_result):
        if last_game_result == GameResult.WON:
            return 100000

        elif last_game_result == GameResult.LOST:
            return -100000

        elif last_game_result == GameResult.DRAW:
            return 5000
