import time
import statistics
import numpy as np
import datetime
from neo4j import GraphDatabase

from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.learning import RLearning
from src.environment import Environment
import src.utilities.constants3x3 as c3x3
import src.utilities.gi_constants as GI_CONSTANTS
from src.game_components.board import Board
from src.game_components.container import Container
from src.game_state_closure_handler import GameStateClosureHandler
from src.utilities.closure_handler_parameters import ClosureHandlerParameters
from src.utilities.logger import Logger
from src.utilities.agent_parameters import ImprovedAgent1Parameters, ImprovedAgent2Parameters
from src.agents.random_walker_agent import RandomWalkerAgent
from src.agents.improved_agent import ImprovedAgent


class GameInterface:

    def __init__(self):
        # Game environment creation
        self.environment = Environment(scoring_parameter=c3x3.scoring_parameter,
                                       score_to_win=c3x3.score_to_win,
                                       board=Board(c3x3.board_border_len),
                                       container=Container(c3x3.chips_types, c3x3.chips_per_type),
                                       game_logger=Logger("game_logger", "game_logs.log")
                                       )

        self.game_state_closure_handler = GameStateClosureHandler(
            lowest_path_len_to_start_closure=ClosureHandlerParameters.lowest_path_len_to_start_closure,
            depth_in_interval_from_7_to_8=ClosureHandlerParameters.depth_in_interval_from_7_to_8,
            depth_in_interval_from_9_to_9=ClosureHandlerParameters.depth_in_interval_from_9_to_9,
            depth_in_interval_from_10=ClosureHandlerParameters.depth_in_interval_from_10
        )

        # Agents creation
        self.random_walker_agent_1 = RandomWalkerAgent(GI_CONSTANTS.RANDOM_WALKER_1)
        self.random_walker_agent_2 = RandomWalkerAgent(GI_CONSTANTS.RANDOM_WALKER_2)

        self.database_driver, self.graph_improved_agent_1, self.graph_improved_agent_2 = self.initialize_database()
        self.improved_agent_1 = ImprovedAgent(name=ImprovedAgent1Parameters.name,
                                              graph=self.graph_improved_agent_1,
                                              learning_algorithm=RLearning(ImprovedAgent1Parameters.discount_rate,
                                                                           ImprovedAgent1Parameters.learning_rate),
                                              exploit_growth=ImprovedAgent1Parameters.exploit_growth,
                                              explore_minimum=ImprovedAgent1Parameters.explore_minimum,
                                              is_improved_exploitation_on=
                                              ImprovedAgent1Parameters.is_improved_exploitation_on,
                                              exploit_to_closed_state_rate=
                                              ImprovedAgent1Parameters.exploit_to_closed_state_rate,
                                              )

        self.improved_agent_2 = ImprovedAgent(name=ImprovedAgent2Parameters.name,
                                              graph=self.graph_improved_agent_2,
                                              learning_algorithm=RLearning(ImprovedAgent2Parameters.discount_rate,
                                                                           ImprovedAgent2Parameters.learning_rate),
                                              exploit_growth=ImprovedAgent2Parameters.exploit_growth,
                                              explore_minimum=ImprovedAgent2Parameters.explore_minimum,
                                              is_improved_exploitation_on=
                                              ImprovedAgent2Parameters.is_improved_exploitation_on,
                                              exploit_to_closed_state_rate=
                                              ImprovedAgent2Parameters.exploit_to_closed_state_rate,
                                              )

        # Initial options list
        self.initial_options = [GI_CONSTANTS.SET_AGENTS,
                                GI_CONSTANTS.RUN_EPISODES,
                                GI_CONSTANTS.DELETE_AGENT_GRAPHS,
                                GI_CONSTANTS.EXIT]

        # Agent vs Agent pairs list
        self.agents_pairs_options = [GI_CONSTANTS.RANDOM_WALKER_VS_RANDOM_WALKER,
                                     GI_CONSTANTS.IMPROVED_AGENT_1_VS_RANDOM_WALKER,
                                     GI_CONSTANTS.IMPROVED_AGENT_2_VS_RANDOM_WALKER,
                                     GI_CONSTANTS.IMPROVED_AGENT_1_VS_IMPROVED_AGENT_2,
                                     GI_CONSTANTS.RETURN]

        # Start episode options list
        self.start_episode_options = [GI_CONSTANTS.START_1,
                                      GI_CONSTANTS.START_10,
                                      GI_CONSTANTS.START_100,
                                      GI_CONSTANTS.START_N,
                                      GI_CONSTANTS.RETURN]

        # Delete agent's graphs options list
        self.graphs_deletion_options = [GI_CONSTANTS.DELETE_IMPROVED_AGENT_1_GRAPH,
                                        GI_CONSTANTS.DELETE_IMPROVED_AGENT_2_GRAPH,
                                        GI_CONSTANTS.DELETE_IMPROVED_AGENT_GRAPHS,
                                        GI_CONSTANTS.DELETE_EVERYTHING,
                                        GI_CONSTANTS.RETURN]

    @staticmethod
    def display_options(options):
        option_counter = 1
        for option in options:
            print(f'[{option_counter}] {option}')
            option_counter += 1

    @staticmethod
    def initialize_database():
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        driver.verify_connectivity()
        return driver, \
               Graph(driver.session(database=ImprovedAgent1Parameters.database)), \
               Graph(driver.session(database=ImprovedAgent2Parameters.database))

    def show_initial_options(self):
        while True:
            print(f'\n')
            self.display_options(self.initial_options)
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice == 1:
                self.process_set_agents_option()
            elif choice == 2:
                self.process_start_episode_option()
            elif choice == 3:
                self.process_graph_deletion_option()
            elif choice == 4:
                break
            else:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue

    def process_set_agents_option(self):
        while True:
            print(f'\n')
            self.display_options(self.agents_pairs_options)
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice == 1:
                self.environment.set_agent_1(self.random_walker_agent_1)
                self.environment.set_agent_2(self.random_walker_agent_2)
            elif choice == 2:
                self.environment.set_agent_1(self.improved_agent_1)
                self.environment.set_agent_2(self.random_walker_agent_1)
            elif choice == 3:
                self.environment.set_agent_1(self.improved_agent_2)
                self.environment.set_agent_2(self.random_walker_agent_1)
            elif choice == 4:
                self.environment.set_agent_1(self.improved_agent_1)
                self.environment.set_agent_2(self.improved_agent_2)
            elif choice == 5:
                break
            else:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue

    def process_start_episode_option(self):
        while True:
            print(f'\n')
            self.display_options(self.start_episode_options)
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice == 1:
                episodes = 1
            elif choice == 2:
                episodes = 10
            elif choice == 3:
                episodes = 100
            elif choice == 4:
                episodes = int(input("Enter episodes> "))
            elif choice == 5:
                break
            else:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue

            benchmarks_playing = []
            benchmarks_evaluation = []
            do_benchmarking_counter = 1
            start = time.time()
            for i in range(episodes):

                if i != 0 and i % 100 == 0:
                    print(f'Reached {do_benchmarking_counter}')
                    # self.do_benchmarking(benchmarks_playing, benchmarks_evaluation, do_benchmarking_counter)
                    do_benchmarking_counter += 1
                    benchmarks_playing = []
                    benchmarks_evaluation = []
                    # self.clear_benchmarks_arrays()

                # Play episode
                playing_timer_start = time.time()
                self.environment.start_episode()
                playing_timer_end = time.time()
                benchmarks_playing.append(playing_timer_end - playing_timer_start)

                # Do game_path copy
                game_path_copy = self.improved_agent_1.last_episode_path.copy()

                # Calculate depth for closure handler
                dynamic_state_closure_depth = self.game_state_closure_handler.calculate_depth(
                    len(game_path_copy.state_data_list)
                )

                evaluation_timer_start = time.time()
                # Evaluate ImprovedAgent path
                if isinstance(self.environment.agents[0], ImprovedAgent):
                    agent = self.environment.agents[0]
                    agent.eval_path_after_episode(dynamic_state_closure_depth)

                # Evaluate ImprovedAgent path
                if isinstance(self.environment.agents[1], ImprovedAgent):
                    agent = self.environment.agents[1]
                    agent.eval_path_after_episode(dynamic_state_closure_depth)
                evaluation_timer_end = time.time()
                benchmarks_evaluation.append(evaluation_timer_end - evaluation_timer_start)

                self.game_state_closure_handler.set_target_agent(self.improved_agent_1)
                self.game_state_closure_handler.set_game_path(game_path_copy)
                self.game_state_closure_handler.start_closure()

                # Log wins/loses/draws
                self.environment.game_logger.write(f'Agent [{self.environment.agents[0].name}]'
                                                   f' won {self.environment.agents[0].wins}')
                self.environment.game_logger.write(f'Agent [{self.environment.agents[1].name}]'
                                                   f' won {self.environment.agents[1].wins}')
                self.environment.game_logger.write(f'Draws: {self.environment.agents[1].draws}')
            end = time.time()

            print(f'whole time average {(end - start) / episodes}')
            print(f'playing episode average {statistics.mean(benchmarks_playing)}')
            print(f'evaluating episode average {statistics.mean(benchmarks_evaluation)}')
            print(f'\n')

            print(f'Time elapsed: {end - start}')
            print(f'Agent [{self.environment.agents[0].name}] won {self.environment.agents[0].wins}')
            print(f'Agent [{self.environment.agents[1].name}] won {self.environment.agents[1].wins}')
            print(f'Draws: {self.environment.agents[1].draws}')

            # self.do_benchmarking(benchmarks_playing, benchmarks_evaluation, do_benchmarking_counter)

    def process_graph_deletion_option(self):
        while True:
            print(f'\n')
            self.display_options(self.graphs_deletion_options)
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice == 1:
                self.improved_agent_1.graph.delete_everything()
            elif choice == 2:
                self.improved_agent_2.graph.delete_everything()
            elif choice == 3:
                self.improved_agent_1.graph.delete_everything()
                self.improved_agent_2.graph.delete_everything()
            elif choice == 4:
                self.improved_agent_1.graph.delete_everything()
                self.improved_agent_2.graph.delete_everything()
            elif choice == 5:
                break
            else:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue

    # def do_benchmarking(self, benchmarks_playing, benchmarks_evaluation, benchmarking_counter):
    #     # Dump to file
    #     current_datetime = datetime.datetime.now()
    #     timestamp = current_datetime.strftime("%H:%M:%S")
    #
    #     path = f'/home/karolisr/Studijos/2023-2024_RUDUO/kursinio_projektas/NAUJI_MATAVIMAI/20231129/benchmarks/'
    #     playing_file = f'{path}{timestamp}_playing_{benchmarking_counter}.txt'
    #     evaluation_file = f'{path}{timestamp}_evaluation_{benchmarking_counter}.txt'
    #
    #     playing_array = np.array(benchmarks_playing)
    #     evaluation_array = np.array(benchmarks_evaluation)
    #
    #     # env1   processing initial state
    #     # env2   placing
    #     # env3   processing after placing
    #     # env4   taking
    #     # env5   processing after taking
    #     # env6   log start round
    #     # env7   get combinations
    #
    #     env1_file = f'{path}{timestamp}_env1_{benchmarking_counter}.txt'
    #     env2_file = f'{path}{timestamp}_env2_{benchmarking_counter}.txt'
    #     env3_file = f'{path}{timestamp}_env3_{benchmarking_counter}.txt'
    #     env4_file = f'{path}{timestamp}_env4_{benchmarking_counter}.txt'
    #     env5_file = f'{path}{timestamp}_env5_{benchmarking_counter}.txt'
    #     env6_file = f'{path}{timestamp}_env6_{benchmarking_counter}.txt'
    #     env7_file = f'{path}{timestamp}_env7_{benchmarking_counter}.txt'
    #
    #     env1_array = np.array(self.environment.benchmarks_1)
    #     env2_array = np.array(self.environment.benchmarks_2)
    #     env3_array = np.array(self.environment.benchmarks_3)
    #     env4_array = np.array(self.environment.benchmarks_4)
    #     env5_array = np.array(self.environment.benchmarks_5)
    #     env6_array = np.array(self.environment.benchmarks_6)
    #     env7_array = np.array(self.environment.benchmarks_7)
    #
    #     # bench1    Placing Explore
    #     # bench2    Gets PlacingRelationInfo objects list
    #     # bench3    Gets TakingRelationInfo objects list
    #     # bench4    Placing exploit optimization
    #     # bench5    Taking exploit optimization
    #     # bench6    Placing exploit optimization method get_states_by_placing_actions
    #     # bench7    Placing exploit optimization method get_best_placing_relation
    #     # bench8    Taking exploit optimization method get_states_by_taking_actions
    #     # bench9    Taking exploit optimization method get_best_taking_relation
    #     # bench10   After Placing processing
    #     # bench11   After Taking processing
    #     # bench12   Initial state processing
    #     # bench13   All placing exploitation time
    #     # bench14   Exploit placing sort
    #     # bench15   Exploit placing filter
    #     # bench16   All taking exploitation time
    #     # bench17   Exploit taking sort
    #     # bench18   Exploit taking filter
    #
    #     agent1_bench_files = [f'{path}{timestamp}_agent1_bench{bench_num}_{benchmarking_counter}.txt'
    #                           for bench_num in range(1, 19)]
    #     # agent2_bench_files = [f'{path}{timestamp}_agent2_bench{bench_num}_{benchmarking_counter}.txt'
    #     #                       for bench_num in range(1, 19)]
    #
    #     agent1_bench_arrays = [np.array(getattr(self.improved_agent_1, f'bench{bench_num}')) for bench_num in
    #                            range(1, 19)]
    #     # agent2_bench_arrays = [np.array(getattr(self.improved_agent_2, f'bench{bench_num}')) for bench_num in
    #     #                        range(1, 19)]
    #
    #     # Learning
    #     # bench1    Execute find_max_next_state_q_value
    #
    #     learning_bench1_file = f'{path}{timestamp}_learning_bench1_{benchmarking_counter}.txt'
    #     learning_bench1_array = np.array(self.improved_agent_1.path_evaluator.learning.bench1)
    #
    #     # Evaluator
    #     # bench1    Update counters in DB
    #     # bench2    Calculate Q-Value
    #     # bench3    Update Q-Value in DB
    #
    #     evaluator_bench1_file = f'{path}{timestamp}_evaluator_bench1_{benchmarking_counter}.txt'
    #     evaluator_bench2_file = f'{path}{timestamp}_evaluator_bench2_{benchmarking_counter}.txt'
    #     evaluator_bench3_file = f'{path}{timestamp}_evaluator_bench3_{benchmarking_counter}.txt'
    #
    #     evaluator_bench1_array = np.array(self.improved_agent_1.path_evaluator.bench1)
    #     evaluator_bench2_array = np.array(self.improved_agent_1.path_evaluator.bench2)
    #     evaluator_bench3_array = np.array(self.improved_agent_1.path_evaluator.bench3)
    #
    #     # Graph
    #     # bench1    # Add game state
    #     # bench2    # Create next node and make placing rel
    #     # bench3    # Create next node and make taking rel
    #     # bench4    # Update node counters
    #     # bench5    # Find next placing action
    #     # bench6    # Find next taking action
    #     # bench7    # Find game state
    #     # bench8    # Find next game states
    #     # bench9    # Update Q-Value
    #     # bench10   # Find placing relation info
    #     # bench11   # Find taking relation info
    #     # bench12   # Find game state next relations
    #     # bench13   # Find next state by placing relation
    #     # bench14   # Find next state by taking relation
    #     # bench15   # Find max next state q-value (All time)
    #     # bench16   # Find max next state q-value (Placing)
    #     # bench17   # Find max next state q-value (Taking)
    #     # bench18   # Find max next state q-value (max function)
    #     # bench19   # Make state info from record
    #     # bench20   # Make placing relation info from record
    #     # bench21   # Make taking relation info from record
    #
    #     graph_agent1_bench_files = [f'{path}{timestamp}_graph_agent1_bench{bench_num}_{benchmarking_counter}.txt'
    #                                 for bench_num in range(1, 18)]
    #     # graph_agent2_bench_files = [f'{path}{timestamp}_graph_agent2_bench{bench_num}_{benchmarking_counter}.txt'
    #     #                             for bench_num in range(1, 18)]
    #
    #     graph_agent1_bench_arrays = [np.array(getattr(self.improved_agent_1.graph, f'bench{bench_num}')) for bench_num
    #                                  in range(1, 18)]
    #     # graph_agent2_bench_arrays = [np.array(getattr(self.improved_agent_2.graph, f'bench{bench_num}')) for bench_num
    #     #                              in range(1, 18)]
    #
    #     np.savetxt(playing_file, playing_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(evaluation_file, evaluation_array, delimiter=',', fmt="%.6f")
    #
    #     np.savetxt(env1_file, env1_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(env2_file, env2_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(env3_file, env3_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(env4_file, env4_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(env5_file, env5_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(env6_file, env6_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(env7_file, env7_array, delimiter=',', fmt="%.6f")
    #
    #     for i in range(len(agent1_bench_files)):
    #         np.savetxt(agent1_bench_files[i], agent1_bench_arrays[i], delimiter=',', fmt="%.6f")
    #         # np.savetxt(agent2_bench_files[i], agent2_bench_arrays[i], delimiter=',', fmt="%.6f")
    #
    #     for i in range(len(graph_agent1_bench_files)):
    #         np.savetxt(graph_agent1_bench_files[i], graph_agent1_bench_arrays[i], delimiter=',', fmt="%.6f")
    #         # np.savetxt(graph_agent2_bench_files[i], graph_agent2_bench_arrays[i], delimiter=',', fmt="%.6f")
    #
    #     np.savetxt(learning_bench1_file, learning_bench1_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(evaluator_bench1_file, evaluator_bench1_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(evaluator_bench2_file, evaluator_bench2_array, delimiter=',', fmt="%.6f")
    #     np.savetxt(evaluator_bench3_file, evaluator_bench3_array, delimiter=',', fmt="%.6f")
    #
    # def clear_benchmarks_arrays(self):
    #     for i in range(1, 8):
    #         setattr(self.environment, f'benchmarks_{i}', [])
    #     for i in range(1, 19):
    #         setattr(self.improved_agent_1, f'bench{i}', [])
    #         # setattr(self.improved_agent_2, f'bench{i}', [])
    #     for i in range(1, 18):
    #         setattr(self.improved_agent_1.graph, f'bench{i}', [])
    #         # setattr(self.improved_agent_2.graph, f'bench{i}', [])
    #     for i in range(1, 4):
    #         setattr(self.improved_agent_1.path_evaluator, f'bench{i}', [])
    #         # setattr(self.improved_agent_2.path_evaluator, f'bench{i}', [])
    #     self.improved_agent_1.path_evaluator.learning.bench1 = []
    #     # self.improved_agent_2.path_evaluator.learning.bench1 = []
