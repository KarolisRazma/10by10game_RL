import time

from neo4j import GraphDatabase

import src.utilities.constants3x3 as c3x3
import src.utilities.gi_constants as GI_CONSTANTS
from src.agents.agent import Agent
from src.agents.fasting_agent import FastingAgent
from src.agents.greedy_agent import GreedyAgent
from src.agents.improved_agent import ImprovedAgent
from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.learning import RLearning
from src.agents.random_walker_agent import RandomWalkerAgent
from src.environment import Environment
from src.game_components.board import Board
from src.game_components.container import Container
from src.game_state_closure_handler import GameStateClosureHandler
from src.utilities.agent_parameters import ImprovedAgent1Parameters, ImprovedAgent2Parameters, \
    GreedyAgentParameters, FastingAgentParameters
from src.utilities.closure_handler_parameters import ClosureHandlerParameters
from src.utilities.logger import Logger


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

        self.agent_1 = None
        self.agent_2 = None
        self.agents: [Agent] = []
        self.database_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        self.database_driver.verify_connectivity()
        self.initialize_agents()

        # Initial options list
        self.initial_options = [GI_CONSTANTS.SET_AGENTS,
                                GI_CONSTANTS.RUN_EPISODES,
                                GI_CONSTANTS.DELETE_AGENT_GRAPHS,
                                GI_CONSTANTS.EXIT]

        # Start episode options list
        self.start_episode_options = [GI_CONSTANTS.START_1,
                                      GI_CONSTANTS.START_10,
                                      GI_CONSTANTS.START_100,
                                      GI_CONSTANTS.START_N,
                                      GI_CONSTANTS.RETURN]

    @staticmethod
    def display_options(options):
        option_counter = 1
        for option in options:
            print(f'[{option_counter}] {option}')
            option_counter += 1

    def get_database(self, database_name):
        return Graph(self.database_driver.session(database=database_name))

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

        self.select_agent_1()
        self.select_agent_2()

        self.environment.set_agent_1(self.agent_1)
        self.environment.set_agent_2(self.agent_2)

    def process_start_episode_option(self):
        if self.agent_1 is None or self.agent_2 is None:
            print(f'Agents are not selected! Select agents first.')
            return
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

                if i != 0 and i % 100 == 0:
                    print(f'Reached {int(i / 100)}')

                # Play episode
                self.environment.start_episode()

                # Do game_path copy
                if isinstance(self.agent_1, ImprovedAgent):
                    game_path_copy_1 = self.agent_1.last_episode_path.copy()
                    dynamic_state_closure_depth = self.game_state_closure_handler.calculate_depth(
                        len(game_path_copy_1.state_data_list)
                    )
                    self.agent_1.eval_path_after_episode(dynamic_state_closure_depth)
                    # self.game_state_closure_handler.set_target_agent(self.agent_1)
                    # self.game_state_closure_handler.set_game_path(game_path_copy_1)
                    # self.game_state_closure_handler.start_closure()

                if isinstance(self.agent_2, ImprovedAgent):
                    game_path_copy_2 = self.agent_2.last_episode_path.copy()
                    dynamic_state_closure_depth = self.game_state_closure_handler.calculate_depth(
                        len(game_path_copy_2.state_data_list)
                    )
                    self.agent_2.eval_path_after_episode(dynamic_state_closure_depth)
                    # self.game_state_closure_handler.set_target_agent(self.agent_2)
                    # self.game_state_closure_handler.set_game_path(game_path_copy_2)
                    # self.game_state_closure_handler.start_closure()
        
                # Log wins/loses/draws
                self.environment.game_logger.write(f'Agent [{self.agent_1.name}]'
                                                   f' won {self.agent_1.wins}')
                self.environment.game_logger.write(f'Agent [{self.agent_2.name}]'
                                                   f' won {self.agent_2.wins}')
                self.environment.game_logger.write(f'Draws: {self.agent_2.draws}')
            end = time.time()

            print(f'whole time average {(end - start) / episodes}')
            print(f'\n')
            print(f'Time elapsed: {end - start}')
            print(f'Agent [{self.agent_1.name}] won {self.agent_1.wins}')
            print(f'Agent [{self.agent_2.name}] won {self.agent_2.wins}')
            print(f'Draws: {self.agent_2.draws}')

    def process_graph_deletion_option(self):
        if self.agent_1 is None or self.agent_2 is None:
            print(f'Agents are not selected! Select agents first.')
            return
        while True:
            print(f'\n')
            print(f'1. Delete {self.agent_1.name} graph')
            print(f'2. Delete {self.agent_2.name} graph')
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice == 1:
                if not isinstance(self.agent_1, ImprovedAgent):
                    print(f'This type of agent doesnt have graph!')
                    return
                self.agent_1.graph.delete_everything()
                break
            elif choice == 2:
                if not isinstance(self.agent_2, ImprovedAgent):
                    print(f'This type of agent doesnt have graph!')
                    return
                self.agent_2.graph.delete_everything()
                break
            else:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue

    def initialize_agents(self):
        self.agents.append(RandomWalkerAgent(GI_CONSTANTS.RANDOM_WALKER_1))
        self.agents.append(RandomWalkerAgent(GI_CONSTANTS.RANDOM_WALKER_2))
        self.agents.append(ImprovedAgent(name=ImprovedAgent1Parameters.name,
                                         graph=self.get_database(ImprovedAgent1Parameters.database),
                                         learning_algorithm=RLearning(ImprovedAgent1Parameters.discount_rate,
                                                                      ImprovedAgent1Parameters.learning_rate),
                                         exploit_growth=ImprovedAgent1Parameters.exploit_growth,
                                         explore_minimum=ImprovedAgent1Parameters.explore_minimum,
                                         is_improved_exploitation_on=
                                         ImprovedAgent1Parameters.is_improved_exploitation_on,
                                         exploit_to_closed_state_rate=
                                         ImprovedAgent1Parameters.exploit_to_closed_state_rate,
                                         ))
        self.agents.append(ImprovedAgent(name=ImprovedAgent2Parameters.name,
                                         graph=self.get_database(ImprovedAgent2Parameters.database),
                                         learning_algorithm=RLearning(ImprovedAgent2Parameters.discount_rate,
                                                                      ImprovedAgent2Parameters.learning_rate),
                                         exploit_growth=ImprovedAgent2Parameters.exploit_growth,
                                         explore_minimum=ImprovedAgent2Parameters.explore_minimum,
                                         is_improved_exploitation_on=
                                         ImprovedAgent2Parameters.is_improved_exploitation_on,
                                         exploit_to_closed_state_rate=
                                         ImprovedAgent2Parameters.exploit_to_closed_state_rate,
                                         ))
        self.agents.append(GreedyAgent(name=GreedyAgentParameters.name,
                                       graph=self.get_database(GreedyAgentParameters.database),
                                       learning_algorithm=RLearning(
                                           GreedyAgentParameters.discount_rate,
                                           GreedyAgentParameters.learning_rate),
                                       exploit_growth=GreedyAgentParameters.exploit_growth,
                                       explore_minimum=GreedyAgentParameters.explore_minimum,
                                       is_improved_exploitation_on=
                                       GreedyAgentParameters.is_improved_exploitation_on,
                                       exploit_to_closed_state_rate=
                                       GreedyAgentParameters.exploit_to_closed_state_rate,
                                       ))
        self.agents.append(FastingAgent(name=FastingAgentParameters.name,
                                        graph=self.get_database(FastingAgentParameters.database),
                                        learning_algorithm=RLearning(
                                            FastingAgentParameters.discount_rate,
                                            FastingAgentParameters.learning_rate),
                                        exploit_growth=FastingAgentParameters.exploit_growth,
                                        explore_minimum=FastingAgentParameters.explore_minimum,
                                        is_improved_exploitation_on=
                                        FastingAgentParameters.is_improved_exploitation_on,
                                        exploit_to_closed_state_rate=
                                        FastingAgentParameters.exploit_to_closed_state_rate,
                                        ))

    def select_agent_1(self):
        while True:
            # Display
            print(f'\n')
            print(f'Select Agent 1')
            for (i, agent) in zip(range(len(self.agents)), self.agents):
                print(f'{i + 1}. {agent.name}')
            # Select
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice - 1 >= len(self.agents) or choice - 1 < 0:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue
            else:
                self.agent_1 = self.agents[choice - 1]
                print(f'Agent1 set successfully to {self.agent_1.name}!')
                break

    def select_agent_2(self):
        while True:
            # Display
            print(f'\n')
            print(f'Select Agent 2')
            for (i, agent) in zip(range(len(self.agents)), self.agents):
                if agent.name == self.agent_1.name:
                    continue
                print(f'{i + 1}. {agent.name}')
            # Select
            try:
                choice = int(input("> "))
            except ValueError:
                print(GI_CONSTANTS.NOT_INT_INPUTED)
                continue
            if choice - 1 >= len(self.agents) or choice - 1 < 0 \
                    or self.agents[choice - 1].name == self.agent_1.name:
                print(GI_CONSTANTS.INVALID_OPTION)
                continue
            else:
                self.agent_2 = self.agents[choice - 1]
                print(f'Agent2 set successfully to {self.agent_2.name}!')
                break
