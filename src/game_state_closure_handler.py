# fixme refactor this

# from copy import deepcopy
#
# from src.agents.improved_agent import ImprovedAgent
# from src.agents.improved_agent_learning.path import Path
# from src.agents.improved_agent_learning.taking_relation_info import TakingRelationInfo
# from src.custom_environment import CustomEnvironment
# import src.utilities.constants3x3 as c3x3
# from src.game_components.board import Board
#
#
# class GameStateClosureHandler:
#     def __init__(self, target_agent=None, game_path=None):
#         self.custom_environment = CustomEnvironment(scoring_parameter=c3x3.scoring_parameter,
#                                                     score_to_win=c3x3.score_to_win,
#                                                     board=Board(c3x3.board_border_len)
#                                                     )
#         self.target_agent: ImprovedAgent = target_agent
#         self.game_path: Path = game_path
#
#         # Depth only counts for the moves that agents did (NOT THE ENEMY AGENT)
#         self.depth = 2
#
#     def set_target_agent(self, target_agent: ImprovedAgent):
#         self.target_agent = target_agent
#
#     def set_game_path(self, game_path: Path):
#         self.game_path = game_path
#
#     def run_custom_env(self):
#         self.custom_environment.prepare_custom_game(self.get_state_info_by_depth(self.depth), self.target_agent)
#         self.custom_environment.start_custom_game()
#
#     def get_state_info_by_depth(self, depth):
#         if isinstance(self.game_path.relation_data_list[depth - 1], TakingRelationInfo):
#             return self.game_path.state_data_list[depth + 1]
#         return self.game_path.state_data_list[depth]
#
#
#
#
#
#
#
#
#
#
#
