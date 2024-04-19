from src.agents.adhoc.adhoc_agent import AdhocAgent
from src.agents.adhoc.strategies.minimize_enemy_points_strategy import MinimizeEnemyPointsStrategy
from src.agents.adhoc.strategies.take_most_points_strategy import TakeMostPointsStrategy


class NonameAgent(AdhocAgent):

    def __init__(self, name):
        super().__init__(name)

        self.minimize_enemy_points_strategy = MinimizeEnemyPointsStrategy()
        self.take_most_points_strategy = TakeMostPointsStrategy()

    def select_placing_action(self, game_board):
        self.last_selected_placing_action = self.minimize_enemy_points_strategy.give_strategy_result(game_board,
                                                                                                     self.hand_chips,
                                                                                                     self.current_state_data)
        return self.last_selected_placing_action

    def select_taking_action(self, game_board, combinations):
        return self.take_most_points_strategy.give_strategy_result(game_board, combinations,
                                                                   self.last_selected_placing_action)
