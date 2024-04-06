import time
from collections import Counter

from neo4j import GraphDatabase

import src.utilities.constants3x3 as c3x3
import src.utilities.gi_constants as GI_CONSTANTS
from src.agents.adhoc.agents.balanced_agent import BalancedAgent
from src.agents.adhoc.agents.fasting_agent import FastingAgent
from src.agents.adhoc.agents.greedy_agent import GreedyAgent

from src.agents.agent import Agent

from src.agents.improved_agent import ImprovedAgent
from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.learning import RLearning
from src.agents.random_walker_agent import RandomWalkerAgent
from src.environment import Environment
from src.game_components.board import Board
from src.game_components.container import Container
from src.utilities.agent_parameters import ImprovedAgent1Parameters, ImprovedAgent2Parameters
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

            file = open("/home/karolisr/Desktop/ba-random.txt", "w")

            start = time.time()
            for i in range(episodes):

                if i != 0 and i % 100 == 0:
                    print(f'Reached {int(i / 100)}')
                    if i % 1000 == 0:
                        file.write(
                            f'{i}: {float(self.agent_1.wins / i) * 100} '
                            f'{float((i - self.agent_1.wins - self.agent_1.draws) / i) * 100} '
                            f'{float(self.agent_1.draws / i) * 100}\n')

                # Play episode
                self.environment.start_episode()

                # Evaluate
                if isinstance(self.agent_1, ImprovedAgent):
                    self.agent_1.eval_path_after_episode()
                if isinstance(self.agent_2, ImprovedAgent):
                    self.agent_2.eval_path_after_episode()

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

            if isinstance(self.agent_1, BalancedAgent):
                print(f'Lost because enemy scored more points: {Counter(self.agent_1.losing_cause)[1]}')
                print(
                    f'Lost because container is empty and agent has more points: {Counter(self.agent_1.losing_cause)[2]}')
                print(self.agent_1.points)

            file.write(
                f'{episodes}: {float(self.agent_1.wins / episodes) * 100} '
                f'{float((episodes - self.agent_1.wins - self.agent_1.draws) / episodes) * 100} '
                f'{float(self.agent_1.draws / episodes) * 100}\n')
            file.close()

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
                                         exploit_growth_by_depth=ImprovedAgent1Parameters.exploit_growth_by_depth,
                                         is_improved_exploitation_on=
                                         ImprovedAgent1Parameters.is_improved_exploitation_on,
                                         exploration_phase_is_applied=
                                         ImprovedAgent1Parameters.exploration_phase_is_applied,
                                         exploration_phase_duration=
                                         ImprovedAgent1Parameters.exploration_phase_duration,
                                         ))
        self.agents.append(ImprovedAgent(name=ImprovedAgent2Parameters.name,
                                         graph=self.get_database(ImprovedAgent2Parameters.database),
                                         learning_algorithm=RLearning(ImprovedAgent2Parameters.discount_rate,
                                                                      ImprovedAgent2Parameters.learning_rate),
                                         exploit_growth=ImprovedAgent2Parameters.exploit_growth,
                                         explore_minimum=ImprovedAgent2Parameters.explore_minimum,
                                         exploit_growth_by_depth=ImprovedAgent2Parameters.exploit_growth_by_depth,
                                         is_improved_exploitation_on=
                                         ImprovedAgent2Parameters.is_improved_exploitation_on,
                                         exploration_phase_is_applied=
                                         ImprovedAgent2Parameters.exploration_phase_is_applied,
                                         exploration_phase_duration=
                                         ImprovedAgent2Parameters.exploration_phase_duration,
                                         ))
        self.agents.append(GreedyAgent(name="GreedyAgent"))
        self.agents.append(FastingAgent(name="FastingAgent"))
        self.agents.append(BalancedAgent(name="BalancedAgent"))

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
