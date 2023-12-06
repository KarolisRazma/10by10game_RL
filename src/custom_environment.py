# fixme refactor this

# import copy
#
# from src.agents.improved_agent_learning.path import Path
# from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData
# from src.agents.random_walker_agent import RandomWalkerAgent
# from src.environment import Environment
# from src.game_components.chip import Chip
# from src.game_components.game_result import GameResult
# from src.game_components.state_data import StateData
#
#
# class CustomEnvironment(Environment):
#     def __init__(self, scoring_parameter, score_to_win, board=None, container=None, agents=None):
#         super().__init__(scoring_parameter, score_to_win, board, container, agents, game_logger=None,
#                          is_logger_silent=True)
#
#         # This can be changed later on
#         self.set_agent_2(RandomWalkerAgent("CustomEnvRandomAgent"))
#
#         # noinspection PyTypeChecker
#         self.starting_state_info: ImprovedAgentStateData = None
#
#     def prepare_custom_game(self, starting_state_info: ImprovedAgentStateData, agent):
#         # Assume that the board is already created
#         self.starting_state_info = starting_state_info
#         self.board.from_board_values_to_board(starting_state_info.board_values)
#         self.container = copy.deepcopy(starting_state_info.container)
#         self.set_agent_1(agent)
#         self.set_agents_list()
#
#         # Prepare agents
#         self.agent_1.score = starting_state_info.my_score
#         self.agent_2.score = starting_state_info.enemy_score
#
#         self.agent_1.hand_chips = [Chip(starting_state_info.hand_chips_values[0]),
#                                    Chip(starting_state_info.hand_chips_values[1])]
#         self.agent_2.hand_chips = [Chip(starting_state_info.enemy_hand_chips_values[0]),
#                                    Chip(starting_state_info.enemy_hand_chips_values[1])]
#
#         self.agent_1.last_episode_path = Path()
#         self.agent_1.last_episode_path.state_data_list.append(starting_state_info)
#         self.agent_1.current_state_info = starting_state_info
#
#     def get_first_and_second_turn_agents(self):
#         first_turn_agent = self.agent_1 if not self.starting_state_info.my_turn else self.agent_2
#         second_turn_agent = self.agent_1 if self.starting_state_info.my_turn else self.agent_2
#         return first_turn_agent, second_turn_agent
#
#     # Additional setup for second turn agent (Game states are representing the end of the turn, but before drawing chip)
#     # TODO: Think about it. It will bring some randomness. You can't be sure, that agent will draw the same chip as he
#     # TODO: drawn in previous game.
#     def setup_second_turn_agent(self, second_turn_agent):
#         if second_turn_agent.hand_chips[0].value == self.starting_state_info.last_placed_chip_list[2]:
#             del second_turn_agent.hand_chips[0]
#         else:
#             del second_turn_agent.hand_chips[1]
#         self.from_container_to_agent(second_turn_agent)
#
#     def start_custom_game(self):
#         turn = 0
#         first_turn_agent, second_turn_agent = self.get_first_and_second_turn_agents()
#         self.setup_second_turn_agent(second_turn_agent)
#         while True:
#             # Get agent and enemy_agent (2.1)
#             agent = first_turn_agent if turn == 0 else second_turn_agent
#             enemy_agent = second_turn_agent if turn == 0 else first_turn_agent
#
#             # Agent selects placing action (2.2)
#             placing_action = agent.select_placing_action(game_board=self.board)
#
#             # Execute selected placing action (2.3)
#             self.make_placing_action(agent, placing_action)
#
#             # Agents processing state changes after a chip placement (2.4)
#             agent.process_state_changes(changes_type=StateChangeType.PLACING,
#                                         changes_data=StateData(is_my_turn=True,
#                                                                game_board=self.board,
#                                                                enemy_score=enemy_agent.score,
#                                                                container_chips_count=len(self.container.chips),
#                                                                placing_action=placing_action,
#                                                                last_placed_chip=self.last_placed_chip,
#                                                                container=copy.deepcopy(self.container),
#                                                                enemy_hand_chips_values=
#                                                                      enemy_agent.get_hand_chips_values_list()
#                                                                ))
#             enemy_agent.process_state_changes(changes_type=StateChangeType.PLACING,
#                                               changes_data=StateData(is_my_turn=False,
#                                                                      game_board=self.board,
#                                                                      enemy_score=agent.score,
#                                                                      container_chips_count=len(
#                                                                                self.container.chips),
#                                                                      placing_action=placing_action,
#                                                                      last_placed_chip=self.last_placed_chip,
#                                                                      container=copy.deepcopy(self.container),
#                                                                      enemy_hand_chips_values=
#                                                                            agent.get_hand_chips_values_list()
#                                                                      ))
#
#             # Everything related to combinations happens here
#             self.process_combinations(agent, enemy_agent)
#
#             # End round and check for ending flag
#             ending_flag = self.round_ending(agent)
#
#             if ending_flag:
#                 break
#
#             # Next agent's turn
#             turn = 0 if turn == 1 else 1
#
#     # Overriden method
#     def round_ending(self, agent):
#         if len(self.container.chips) > 0:
#             # Method from parent
#             self.from_container_to_agent(agent)
#
#         # Method from parent
#         end_game_flag = self.is_endgame()
#         if end_game_flag > 0:
#             # Overriden method
#             self.deal_with_endgame(end_game_flag)
#             return True
#         return False
#
#     def deal_with_endgame(self, end_game_flag):
#         if end_game_flag == 1:
#             self.agents[0].last_game_result = GameResult.WON
#             self.agents[1].last_game_result = GameResult.LOST
#             return
#         if end_game_flag == 2:
#             self.agents[0].last_game_result = GameResult.LOST
#             self.agents[1].last_game_result = GameResult.WON
#             return
#         if end_game_flag == 3:
#             if self.agents[0].score < self.agents[1].score:
#                 self.agents[0].last_game_result = GameResult.WON
#                 self.agents[1].last_game_result = GameResult.LOST
#                 return
#             elif self.agents[0].score > self.agents[1].score:
#                 self.agents[0].last_game_result = GameResult.LOST
#                 self.agents[1].last_game_result = GameResult.WON
#                 return
#             else:
#                 self.agents[0].last_game_result = GameResult.DRAW
#                 self.agents[1].last_game_result = GameResult.DRAW
#                 return
