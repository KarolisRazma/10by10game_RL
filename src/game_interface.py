# Database
from neo4j import GraphDatabase

from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.learning import RLearning

# Environment
from src.environment import Environment

# Constants
import src.utilities.constants3x3 as c3x3
import src.utilities.constants5x5 as c5x5
import src.utilities.gi_constants as GI_CONSTANTS

# Agents
from src.agents.brute_force_agent import RandomWalkerAgent
from src.agents.improved_agent import ImprovedAgent

# Misc
import time

from src.utilities import logger

# Database
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"
driver = GraphDatabase.driver(uri, auth=(username, password))
driver.verify_connectivity()

# Create Sessions for agents (for their databases)
# And get Graphs for agents
session_improved_agent_1 = driver.session(database="newtest1")
graph_improved_agent_1 = Graph(driver, session_improved_agent_1)

session_improved_agent_2 = driver.session(database="newtest2")
graph_improved_agent_2 = Graph(driver, session_improved_agent_2)


class GameInterface:

    def __init__(self, environment_type):
        # Game environment creation
        if environment_type == GI_CONSTANTS.ENVIRONMENT_3X3:
            self.environment = Environment(c3x3.board_border_len, c3x3.container_capacity,
                                           c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                                           c3x3.score_to_win)
        if environment_type == GI_CONSTANTS.ENVIRONMENT_5X5:
            self.environment = Environment(c5x5.board_border_len, c5x5.container_capacity,
                                           c5x5.chips_types, c5x5.chips_per_type, c5x5.scoring_parameter,
                                           c5x5.score_to_win)

        # Agents creation
        self.random_walker_agent_1 = RandomWalkerAgent(GI_CONSTANTS.RANDOM_WALKER_1)
        self.random_walker_agent_2 = RandomWalkerAgent(GI_CONSTANTS.RANDOM_WALKER_2)

        # TODO Create Improved Agents here

        self.improved_agent_1 = ImprovedAgent(name=GI_CONSTANTS.IMPROVED_1,
                                              graph=graph_improved_agent_1,
                                              learning_algorithm=RLearning(discount_rate=0.9, learning_rate=0.9),
                                              exploit_growth=0.06,
                                              explore_minimum=0.10
                                              )

        self.improved_agent_2 = ImprovedAgent(name=GI_CONSTANTS.IMPROVED_2,
                                              graph=graph_improved_agent_2,
                                              learning_algorithm=RLearning(discount_rate=0.9, learning_rate=0.9),
                                              exploit_growth=0.06,
                                              explore_minimum=0.10,
                                              is_improved_exploitation_on=True
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

    def show_initial_options(self):

        # logggg = logger.Logger("benchmark_logger3", "test.log")
        # while True:
        #     start_time = time.time()
        #     query = \
        #         f"""
        #         MATCH (:GameState {{
        #         board_values: [0, 0, 0, 0, 1, 0, 0, 0, 2],
        #         my_turn: false,
        #         my_score: 0,
        #         enemy_score: 0}})
        #         -[r:NEXT_PLACING]->(:GameState)
        #         RETURN r
        #         """
        #     graph_improved_agent_2.session.run(query)
        #     end_time = time.time()
        #     logggg.write("{0:.3f}".format(end_time - start_time))

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
                self.environment.clear_agents()
                self.environment.set_agent(self.random_walker_agent_1)
                self.environment.set_agent(self.random_walker_agent_2)
            elif choice == 2:
                self.environment.clear_agents()
                self.environment.set_agent(self.improved_agent_1)
                self.environment.set_agent(self.random_walker_agent_1)
            elif choice == 3:
                self.environment.clear_agents()
                self.environment.set_agent(self.improved_agent_2)
                self.environment.set_agent(self.random_walker_agent_1)
            elif choice == 4:
                self.environment.clear_agents()
                self.environment.set_agent(self.improved_agent_1)
                self.environment.set_agent(self.improved_agent_2)
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
            start = time.time()
            for i in range(episodes):

                # Play episode
                self.environment.benchmark_logger.write("\nEpisode playing time")
                timer_start = time.time()
                self.environment.start_episode()
                timer_end = time.time()
                self.environment.benchmark_logger.write(timer_end - timer_start)

                self.environment.benchmark_logger.write("\nEpisode evaluating time")
                timer_start = time.time()
                # Evaluate ImprovedAgent path
                if isinstance(self.environment.agents[0], ImprovedAgent):
                    agent = self.environment.agents[0]
                    agent.eval_path_after_episode()

                # Evaluate ImprovedAgent path
                if isinstance(self.environment.agents[1], ImprovedAgent):
                    agent = self.environment.agents[1]
                    agent.eval_path_after_episode()
                timer_end = time.time()
                self.environment.benchmark_logger.write(timer_end - timer_start)

                # Log wins/loses/draws
                self.environment.game_logger.write(f'Agent [{self.environment.agents[0].name}]'
                                                   f' won {self.environment.agents[0].wins}')
                self.environment.game_logger.write(f'Agent [{self.environment.agents[1].name}]'
                                                   f' won {self.environment.agents[1].wins}')
                self.environment.game_logger.write(f'Draws: {self.environment.agents[1].draws}')

            end = time.time()
            print(f'\n')
            self.environment.benchmark_logger.write("\nWhole Episode time")
            self.environment.benchmark_logger.write(end - start)
            print(f'Time elapsed: {end - start}')
            print(f'Agent [{self.environment.agents[0].name}] won {self.environment.agents[0].wins}')
            print(f'Agent [{self.environment.agents[1].name}] won {self.environment.agents[1].wins}')
            print(f'Draws: {self.environment.agents[1].draws}')

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
