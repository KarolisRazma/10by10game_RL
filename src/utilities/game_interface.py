# Database
from neo4j import GraphDatabase
import src.agents.simple_agent_learning.graph as gh
import src.agents.simple_agent_learning.learning as lg

# Environment
import src.environment as e

# Constants
import src.utilities.constants3x3 as c3x3
import src.utilities.constants5x5 as c5x5
import src.utilities.game_interface_constants as int_c

# Agents
import src.agents.brute_force_agent as bfag
import src.agents.simple_agent as sag

# Misc
import time
import src.utilities.path_notator as notator


# Database
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"
driver = GraphDatabase.driver(uri, auth=(username, password))
driver.verify_connectivity()

# Create Sessions for agents (for their databases)
# And get Graphs for agents
session_simple_agent_1 = driver.session(database="simpleagent1")
session_simple_agent_2 = driver.session(database="simpleagent2")
graph_simple_agent_1 = gh.Graph(driver, session_simple_agent_1)
graph_simple_agent_2 = gh.Graph(driver, session_simple_agent_2)


class GameInterface:
    def __init__(self, environment_type):
        # Game environment creation
        if environment_type == int_c.ENVIRONMENT_3X3:
            self.environment = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
                                             c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                                             c3x3.score_to_win)
        if environment_type == int_c.ENVIRONMENT_5X5:
            self.environment = e.Environment(c5x5.board_border_len, c5x5.container_capacity,
                                             c5x5.chips_types, c5x5.chips_per_type, c5x5.scoring_parameter,
                                             c5x5.score_to_win)

        # Agents creation
        self.brute_force_agent_1 = bfag.BruteForceAgent("Brute Force Agent 1")
        self.brute_force_agent_2 = bfag.BruteForceAgent("Brute Force Agent 2")
        self.simple_agent_1 = sag.SimpleAgent("Simple Agent 1", graph_simple_agent_1, learning_algorithm=lg.RLearning(),
                                              explore_rate=0.5)
        self.simple_agent_2 = sag.SimpleAgent("Simple Agent 2", graph_simple_agent_2, learning_algorithm=lg.RLearning(),
                                              explore_rate=0.5)

        # Initial options list
        self.initial_options = [int_c.SET_AGENTS, int_c.RUN_EPISODES, int_c.DELETE_AGENT_GRAPHS, int_c.EXIT]

        # Agent vs Agent pairs list
        self.agents_pairs_options = [int_c.BRUTE_VS_BRUTE, int_c.SIMPLE_AGENT_1_VS_BRUTE, int_c.SIMPLE_AGENT_2_VS_BRUTE,
                                     int_c.SIMPLE_AGENT_1_VS_SIMPLE_AGENT_2, int_c.RETURN]

        # Start episode options list
        self.start_episode_options = [int_c.START_1, int_c.START_10, int_c.START_100, int_c.START_N, int_c.RETURN]

        # Delete agent's graphs options list
        self.graphs_deletion_options = [int_c.DELETE_SIMPLE_AGENT_1_GRAPH, int_c.DELETE_SIMPLE_AGENT_2_GRAPH,
                                        int_c.DELETE_SIMPLE_AGENT_GRAPHS, int_c.RETURN]

    @staticmethod
    def display_options(options):
        option_counter = 1
        for option in options:
            print(f'[{option_counter}] {option}')
            option_counter += 1

    def show_initial_options(self):
        while True:
            print(f'\n')
            self.display_options(self.initial_options)
            choice = int(input("> "))
            if choice == 1:
                self.process_set_agents_option()
            elif choice == 2:
                self.process_start_episode_option()
            elif choice == 3:
                self.process_graph_deletion_option()
            elif choice == 4:
                break
            else:
                print(int_c.INVALID_OPTION)
                continue

    def process_set_agents_option(self):
        while True:
            print(f'\n')
            self.display_options(self.agents_pairs_options)
            choice = int(input("> "))
            if choice == 1:
                self.environment.clear_agents()
                self.environment.set_agent(self.brute_force_agent_1)
                self.environment.set_agent(self.brute_force_agent_2)
            elif choice == 2:
                self.environment.clear_agents()
                self.environment.set_agent(self.simple_agent_1)
                self.environment.set_agent(self.brute_force_agent_1)
            elif choice == 3:
                self.environment.clear_agents()
                self.environment.set_agent(self.simple_agent_2)
                self.environment.set_agent(self.brute_force_agent_1)
            elif choice == 4:
                self.environment.clear_agents()
                self.environment.set_agent(self.simple_agent_1)
                self.environment.set_agent(self.simple_agent_2)
            elif choice == 5:
                break
            else:
                print(int_c.INVALID_OPTION)
                continue

    def process_start_episode_option(self):
        while True:
            print(f'\n')
            self.display_options(self.start_episode_options)
            choice = int(input("> "))
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
                print(int_c.INVALID_OPTION)
                continue
            start = time.time()
            for i in range(episodes):
                # Play episode
                self.environment.start_episode()

                # Evaluate SimpleAgent paths
                if isinstance(self.environment.agents[0], sag.SimpleAgent):
                    agent = self.environment.agents[0]
                    agent.eval_path_after_episode()
                    pathstring = notator.notate_path_simple(agent.last_episode_path)
                    filename = notator.FILENAME_SIMPLE_AGENT_1 if agent.id == "Simple Agent 1" else notator.FILENAME_SIMPLE_AGENT_2
                    notator.dump_pathstring_into_log(pathstring, filename)

                if isinstance(self.environment.agents[1], sag.SimpleAgent):
                    agent = self.environment.agents[1]
                    agent.eval_path_after_episode()
                    pathstring = notator.notate_path_simple(agent.last_episode_path)
                    filename = notator.FILENAME_SIMPLE_AGENT_2 if agent.id == "Simple Agent 2" else notator.FILENAME_SIMPLE_AGENT_1
                    notator.dump_pathstring_into_log(pathstring, filename)
            end = time.time()
            print(f'\n')
            print(f'Time elapsed: {end - start}')
            print(f'Agent [{self.environment.agents[0].id}] won {self.environment.agents[0].wins}')
            print(f'Agent [{self.environment.agents[1].id}] won {self.environment.agents[1].wins}')
            print(f'Draws: {self.environment.agents[1].draws}')

    def process_graph_deletion_option(self):
        while True:
            print(f'\n')
            self.display_options(self.graphs_deletion_options)
            choice = int(input("> "))
            if choice == 1:
                self.simple_agent_1.graph.delete_everything()
            elif choice == 2:
                self.simple_agent_2.graph.delete_everything()
            elif choice == 3:
                self.simple_agent_1.graph.delete_everything()
                self.simple_agent_2.graph.delete_everything()
            elif choice == 4:
                break
            else:
                print(int_c.INVALID_OPTION)
                continue