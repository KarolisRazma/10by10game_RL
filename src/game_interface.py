import time
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

            file = open("/home/karolisr/Desktop/results20240303.txt", "w")

            start = time.time()
            for i in range(episodes):

                if i != 0 and i % 100 == 0:
                    print(f'Reached {int(i / 100)}')
                    if i % 10000 == 0:
                        file.write(
                            f'{i + 750000}: {float(self.improved_agent_1.wins / i) * 100} '
                            f'{float((i - self.improved_agent_1.wins - self.improved_agent_1.draws) / i) * 100} '
                            f'{float(self.improved_agent_1.draws / i) * 100}\n')

                # Play episode
                self.environment.start_episode()

                # Do game_path copy
                game_path_copy = self.improved_agent_1.last_episode_path.copy()

                # Calculate depth for closure handler
                dynamic_state_closure_depth = self.game_state_closure_handler.calculate_depth(
                    len(game_path_copy.state_data_list)
                )

                # Evaluate ImprovedAgent path
                if isinstance(self.environment.agents[0], ImprovedAgent):
                    agent = self.environment.agents[0]
                    agent.eval_path_after_episode(dynamic_state_closure_depth)

                # Evaluate ImprovedAgent path
                if isinstance(self.environment.agents[1], ImprovedAgent):
                    agent = self.environment.agents[1]
                    agent.eval_path_after_episode(dynamic_state_closure_depth)

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
            print(f'\n')
            print(f'Time elapsed: {end - start}')
            print(f'Agent [{self.environment.agents[0].name}] won {self.environment.agents[0].wins}')
            print(f'Agent [{self.environment.agents[1].name}] won {self.environment.agents[1].wins}')
            print(f'Draws: {self.environment.agents[1].draws}')

            file.write(
                f'{episodes + 750000}: {float(self.improved_agent_1.wins / episodes) * 100} '
                f'{float((episodes - self.improved_agent_1.wins - self.improved_agent_1.draws) / episodes) * 100} '
                f'{float(self.improved_agent_1.draws / episodes) * 100}\n')
            file.close()

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
