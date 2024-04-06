from enum import Enum

import src.agents.agent as ag
import src.agents.improved_agent_learning.path as ph

import src.agents.improved_agent_learning.path_evaluator as pe
import numpy as np
import random

from src.agents.actions.placing_action import PlaceChipAction
from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.game_components.action_data import ActionData
from src.game_components.board import Board
from src.game_components.state_data import StateData


class Behaviour(Enum):
    EXPLORE = 1
    EXPLOIT = 2


class ImprovedAgent(ag.Agent):
    # @param nickname               --> agent's id
    # @param graph                  --> neoj4 graph
    # @param learning_algorithm     --> class RLearning object

    def __init__(self, name, graph, learning_algorithm, exploit_growth, explore_minimum, exploit_growth_by_depth,
                 exploration_phase_is_applied, exploration_phase_duration, is_improved_exploitation_on=False):
        # Init Agent superclass
        super().__init__(name)

        # Graph stored in Neo4j
        self.graph: Graph = graph

        # Path evaluation field
        self.path_evaluator = pe.PathEvaluator(learning_algorithm)

        # Every move which happened in last episode stored here
        self.last_episode_path = ph.Path()

        # Current game state info
        self.current_state_data = None

        # Random next node selection rate
        self.explore_rate = float(1)
        # Best next node selection rate
        self.exploit_rate = float(1 - self.explore_rate)
        self.explore_minimum = explore_minimum
        self.exploit_growth = exploit_growth
        self.exploit_growth_by_depth = exploit_growth_by_depth
        self.current_depth = 1
        self.is_initial_state_observed = False

        # List for agent behaviour selection
        self.behaviour = [Behaviour.EXPLOIT, Behaviour.EXPLORE]
        self.is_improved_exploitation_on = is_improved_exploitation_on

        # Current turn fields
        self.this_turn_behaviour = None
        self.exploit_combination_in_this_turn = None
        self.exploited_relation = None
        # List of current turn relations from graph
        self.relations = None

        self.exploration_phase_is_applied = exploration_phase_is_applied
        self.exploration_phase_duration = exploration_phase_duration
        self.episodes_played = 0

        self.is_strategy_applied = False

    def observe_state(self, state_data: StateData, action_data: ActionData = None):
        self.current_state_data = state_data
        # Last move is done by the agent and its not initial state
        if not state_data.my_turn and self.is_initial_state_observed:
            self.current_depth += 1
            if self.this_turn_behaviour == Behaviour.EXPLOIT:
                self.last_episode_path.relation_data_list.append(self.exploited_relation)
            else:
                updated_relation_data = self.find_relation_in_relations_list(
                    target_relation=action_data,
                    source_relations=self.relations
                )
                if updated_relation_data:
                    self.last_episode_path.relation_data_list.append(updated_relation_data)
                else:
                    improved_agent_action_data = ImprovedAgentActionData(
                        row=action_data.row,
                        col=action_data.col,
                        chip_value=action_data.chip_value,
                        has_taking=action_data.has_taking,
                        combination=action_data.combination,
                    )
                    self.last_episode_path.relation_data_list.append(improved_agent_action_data)

        # Last move is done by enemy agent, or state is final
        if state_data.my_turn or state_data.is_final:
            if not self.is_initial_state_observed:
                # For environment, it could be not initial state
                # But for agent, it can be initial state
                state_data.is_initial = True
                self.is_initial_state_observed = True
            if state_data.is_final:
                self.episodes_played += 1
            self.last_episode_path.state_data_list.append(state_data)

    def select_placing_action(self, game_board):
        return self.select_action(game_board)

    #
    # def select_taking_action(self, game_board, combinations):
    #     # I think, I need to clarify this one:
    #     # If behaviour is EXPLORE, it means that we didn't have combination yet,
    #     # But if behaviour is EXPLOIT and the game let us choose combination,
    #     # Then it means, that we already know what combination we want to exploit.
    #     if self.this_turn_behaviour == Behaviour.EXPLORE:
    #         return self.do_explore_taking(combinations)
    #     else:
    #         return self.exploit_combination_in_this_turn

    def select_taking_action(self, game_board, combinations):
        if not self.is_strategy_applied:
            # I think, I need to clarify this one:
            # If behaviour is EXPLORE, it means that we didn't have combination yet,
            # But if behaviour is EXPLOIT and the game let us choose combination,
            # Then it means, that we already know what combination we want to exploit.
            if self.this_turn_behaviour == Behaviour.EXPLORE:
                return self.do_explore_taking(combinations)
            else:
                return self.exploit_combination_in_this_turn
        else:
            return self.get_strategy_combination(combinations)

    def reset(self):
        super().reset()
        self.last_episode_path.reset()
        self.current_state_data = None
        self.current_depth = 1
        self.is_initial_state_observed = False

    def eval_path_after_episode(self):
        self.path_evaluator.set_path(self.last_episode_path)
        self.path_evaluator.eval_path(self.graph, self.last_game_result, self.is_exploration_phase())

    def get_agent_behaviour(self):
        # Do random choice(not so random, because according to probabilities) for behaviour
        return np.random.choice(self.behaviour, 1, p=[self.exploit_rate, self.explore_rate])

    @staticmethod
    def get_best_relation(relations, best_relation):
        # Get max times_used in 'relations' list
        get_max_times_used = (max(relations, key=lambda x: x.times_used)).times_used

        # Visited/winrate criteria parameters
        times_used_criteria = int(get_max_times_used / 3) if int(get_max_times_used / 3) > 0 else 1
        win_rate_criteria = 0.40

        best_relations = []
        for relation in relations:
            relation_win_rate = relation.win_counter / relation.times_used
            # Check if relation meets the criteria
            if relation_win_rate >= win_rate_criteria and relation.times_used >= times_used_criteria:
                best_relations.append(relation)
        # At least one relation met the criteria
        if best_relations:
            return max(best_relations, key=lambda x: float(x.win_counter / x.times_used))
        return best_relation

    @staticmethod
    def filter_negative_relation_q_values(relations):
        return [relation for relation in relations if relation.q_value >= 0.0]

    def select_action(self, game_board):
        self.relations = self.graph.find_game_state_next_relations(self.current_state_data)
        self.relations = self.remove_relations_duplicates()

        if self.current_depth > 2:
            result_of_strategy = self.strategise_blue_tiles(game_board)

            if isinstance(result_of_strategy, PlaceChipAction):
                self.is_strategy_applied = True
                self.this_turn_behaviour = None
                return result_of_strategy
            else:
                self.is_strategy_applied = False

        # If an exploratory phase is applied, then explore a set number of episodes
        if self.is_exploration_phase():
            self.this_turn_behaviour = Behaviour.EXPLORE
            return self.do_explore_placing(game_board)

        # If 'relations' is empty, then agent explore 100%
        if not self.relations:
            self.explore_rate = float(1)
            self.exploit_rate = float(0)
        # Else, change exploration rate accordingly to nodes_length
        else:
            relations_length = len(self.relations)
            explore_rate = float(1 - (self.exploit_growth_by_depth * self.current_depth) * relations_length)
            exploit_rate = float(1 - explore_rate)

            # If explore rate is negative
            if explore_rate < 0:
                explore_rate = float(self.explore_minimum)
                exploit_rate = float(1 - explore_rate)

            self.explore_rate = explore_rate
            self.exploit_rate = exploit_rate

        # Getting agent's behaviour for this round
        self.this_turn_behaviour = self.get_agent_behaviour()

        print(f'\nExplore rate: {self.explore_rate}')
        print(f'Exploit rate: {self.exploit_rate}')
        print(f'Behaviour: {self.this_turn_behaviour}')

        if self.this_turn_behaviour == Behaviour.EXPLORE:
            return self.do_explore_placing(game_board)
        elif self.this_turn_behaviour == Behaviour.EXPLOIT:
            return self.do_exploit(game_board)

    def do_explore_placing(self, game_board):
        # Choose one action randomly
        return self.get_random_action_for_placing(game_board)

    @staticmethod
    def do_explore_taking(combinations):
        # Choose one combination randomly
        return combinations[random.randint(0, len(combinations) - 1)]

    def do_exploit(self, game_board):
        # Sort list by q_value in decending order
        self.relations.sort(key=lambda x: x.q_value, reverse=True)

        # TODO Update filter later
        # Filter cut relations and negative relations
        # filtered_relations = self.filter_cut_relations(
        #     self.filter_negative_relation_q_values(self.relations)
        # )
        # if 'filtered_relations' is empty
        # if not filtered_relations:
        #     if self.explore_rate == self.explore_minimum:
        #         filtered_relations = [self.relations[0]]
        #     else:
        #         self.this_turn_behaviour = Behaviour.EXPLORE
        #         return self.do_explore_placing(game_board)

        # Set relation which holds highest q_value
        best_relation = self.relations[0]

        # (Can be skipped) Optimization for better exploitation results
        if self.is_improved_exploitation_on:
            best_relation = self.get_best_relation(self.relations, best_relation)

        # Can be an empty array, if relation only has placing action
        self.exploit_combination_in_this_turn = best_relation.combination

        self.exploited_relation = best_relation

        return PlaceChipAction(best_relation.row, best_relation.col, best_relation.chip_value)

    def remove_relations_duplicates(self, key=lambda x: (x.row, x.col, x.chip_value,
                                                         x.has_taking, tuple(x.combination))):
        seen = set()
        return [relation for relation in self.relations if (k := key(relation)) not in seen and not seen.add(k)]

    @staticmethod
    def filter_cut_relations(relations):
        return [relation for relation in relations if not relation.is_cut]

    @staticmethod
    def is_combinations_equal(comb1, comb2):
        if len(comb1) != len(comb2):
            return False
        for chip1, chip2 in zip(comb1, comb2):
            if chip1.row != chip2.row or chip1.col != chip2.col or chip1.value != chip2.value:
                return False
        return True

    def find_relation_in_relations_list(self, target_relation, source_relations):
        for relation in source_relations:
            if relation.row == target_relation.row and \
                    relation.col == target_relation.col and \
                    relation.chip_value == target_relation.chip_value and \
                    relation.has_taking == target_relation.has_taking and \
                    self.is_combinations_equal(relation.combination, target_relation.combination):
                return relation
        return None

    def is_exploration_phase(self):
        return self.exploration_phase_is_applied and self.episodes_played < self.exploration_phase_duration

    @staticmethod
    def get_blue_tiles(game_board: Board):
        return [game_board.chips[0], game_board.chips[-1]]

    @staticmethod
    def is_blue_tiles_empty(game_board: Board):
        return game_board.is_tile_empty(0) and game_board.is_tile_empty(8)

    def strategise_blue_tiles(self, game_board: Board):
        if not self.is_blue_tiles_empty(game_board):
            blue_tiles = self.get_blue_tiles(game_board)
            if blue_tiles[0].value != 0 and blue_tiles[1].value != 0:
                if game_board.is_tile_empty(4):
                    for chip in self.hand_chips:
                        if blue_tiles[0].value + chip.value + blue_tiles[1].value == 4:
                            return PlaceChipAction(1, 1, chip.value)
            blue_tile = blue_tiles[0] if blue_tiles[0].value != 0 else blue_tiles[1]
            if blue_tile.row == 0:
                for chip in self.hand_chips:
                    if chip.value + blue_tile.value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
            elif blue_tile.row == 2:
                for chip in self.hand_chips:
                    if chip.value + blue_tile.value == 4:
                        if game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
        else:
            if not game_board.is_tile_empty(1):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[1].value == 4:
                        if game_board.is_tile_empty(2):
                            return PlaceChipAction(0, 2, chip.value)
                        elif game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
            if not game_board.is_tile_empty(2):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[2].value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
            if not game_board.is_tile_empty(3):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[3].value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(6):
                            return PlaceChipAction(2, 0, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
            if not game_board.is_tile_empty(5):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[5].value == 4:
                        if game_board.is_tile_empty(1):
                            return PlaceChipAction(0, 1, chip.value)
                        elif game_board.is_tile_empty(2):
                            return PlaceChipAction(0, 2, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
            if not game_board.is_tile_empty(6):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[6].value == 4:
                        if game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(7):
                            return PlaceChipAction(2, 1, chip.value)
            if not game_board.is_tile_empty(7):
                for chip in self.hand_chips:
                    if chip.value + game_board.chips[7].value == 4:
                        if game_board.is_tile_empty(3):
                            return PlaceChipAction(1, 0, chip.value)
                        elif game_board.is_tile_empty(4):
                            return PlaceChipAction(1, 1, chip.value)
                        elif game_board.is_tile_empty(5):
                            return PlaceChipAction(1, 2, chip.value)
                        elif game_board.is_tile_empty(6):
                            return PlaceChipAction(2, 0, chip.value)
        return False

    @staticmethod
    def get_strategy_combination(combinations):
        for combination in combinations:
            for chip in combination:
                if (chip.row == 0 and chip.col == 0) or (chip.row == 2 or chip.col == 2):
                    return combination
        return combinations[random.randint(0, len(combinations) - 1)]
