import math

import src.agents.agent as ag
import src.agents.improved_agent_learning.path as ph

import src.agents.improved_agent_learning.path_evaluator as pe
import numpy as np
import random

from src.agents.actions.placing_action import PlaceChipAction
from src.utilities.state_changes import StateChangeType, StateChangeData, InitialStateData
from src.agents.improved_agent_learning.state_info import StateInfo


class ImprovedAgent(ag.Agent):

    # @param nickname               --> agent's id
    # @param graph                  --> neoj4 graph
    # @param learning_algorithm     --> class RLearning object

    def __init__(self, name, graph, learning_algorithm, exploit_growth, explore_minimum,
                 is_improved_exploitation_on=False):
        # Init Agent superclass
        super().__init__(name)

        # Graph stored in Neo4j
        self.graph = graph

        # Path evaluation field
        self.path_evaluator = pe.PathEvaluator(learning_algorithm)

        # Every move which happened in last episode stored here
        self.last_episode_path = ph.Path()

        # Current game state info
        self.current_state_info = None

        # Random next node selection rate
        self.explore_rate = float(1)
        # Best next node selection rate
        self.exploit_rate = float(1 - self.explore_rate)
        self.explore_minimum = explore_minimum
        self.exploit_growth = exploit_growth

        # List for agent behaviour selection
        self.behaviour = ["EXPLOIT", "EXPLORE"]
        self.is_improved_exploitation_on = is_improved_exploitation_on

    def select_placing_action(self, game_board):
        return self.get_placing_action(game_board)

    def select_taking_action(self, game_board, combinations, last_placed_chip):
        return self.get_taking_action(combinations, last_placed_chip)

    def process_state_changes(self, changes_type, changes_data):
        if changes_type == StateChangeType.PLACING:
            self.process_state_changes_after_placing(changes_data)
        elif changes_type == StateChangeType.TAKING:
            self.process_state_changes_after_taking(changes_data)

    def process_state_changes_after_placing(self, changes_data: StateChangeData):
        board_values = changes_data.game_board.board_to_chip_values()
        my_turn = changes_data.is_my_turn
        my_score = self.score
        enemy_score = changes_data.enemy_score
        chips_left = changes_data.container_chips_count
        placing_action = changes_data.placing_action

        # Create StateInfo object with next state data
        next_state_info = StateInfo(board_values=board_values,
                                    my_turn=my_turn,
                                    my_score=my_score,
                                    enemy_score=enemy_score,
                                    chips_left=chips_left)

        # Update agent's graph with next board state and placing relation
        updated_next_state_info, placing_relation_info = \
            self.graph.create_next_node_and_make_placing_relation(self.current_state_info,
                                                                  next_state_info, placing_action)

        # Append placing relation and next state to path
        self.last_episode_path.relation_info_list.append(placing_relation_info)
        self.last_episode_path.state_info_list.append(updated_next_state_info)

        # Update current state
        self.current_state_info = updated_next_state_info

    def process_state_changes_after_taking(self, changes_data: StateChangeData):
        board_values = changes_data.game_board.board_to_chip_values()
        my_turn = changes_data.is_my_turn
        my_score = self.score
        enemy_score = changes_data.enemy_score
        chips_left = changes_data.container_chips_count
        taking_combination = changes_data.taking_combination
        last_placed_chip = [changes_data.last_placed_chip.row, changes_data.last_placed_chip.col,
                            changes_data.last_placed_chip.value]

        # Create StateInfo object with next state data
        next_state_info = StateInfo(board_values=board_values,
                                    my_turn=my_turn,
                                    my_score=my_score,
                                    enemy_score=enemy_score,
                                    chips_left=chips_left)

        # Update agent's graph with next board state and taking relation
        updated_next_state_info, taking_relation_info = \
            self.graph.create_next_node_and_make_taking_relation(self.current_state_info, next_state_info,
                                                                 taking_combination, last_placed_chip)

        # Append taking relation and next state to path
        self.last_episode_path.relation_info_list.append(taking_relation_info)
        self.last_episode_path.state_info_list.append(updated_next_state_info)

        # Update current state
        self.current_state_info = updated_next_state_info

    def get_random_action_for_placing(self, game_board):
        # Loop while action is not selected
        # fixme can cause problems if board is full
        while True:
            random_tile_index = random.randint(0, len(game_board.tiles) - 1)
            if game_board.is_tile_empty(random_tile_index):
                tile_row = math.floor(random_tile_index / game_board.border_length)
                tile_col = random_tile_index % game_board.border_length
                hand_chip_index = random.randint(0, 1)
                return PlaceChipAction(tile_row, tile_col, self.hand_chips[hand_chip_index].value)

    def reset(self):
        super().reset()
        self.last_episode_path.reset()
        self.current_state_info = None

    def eval_path_after_episode(self):
        self.path_evaluator.set_path(self.last_episode_path)
        self.path_evaluator.eval_path(self.graph, self.is_game_won, self.is_game_drawn)

    def process_initial_state(self, initial_data: InitialStateData):
        board_values = initial_data.game_board.board_to_chip_values()

        # There is some "maneuver" - if is_starting is True, then it means on Initial State it should be set on False.
        # This is done for correct moves structure (True -> False -> True ...)
        is_starting = False if initial_data.is_starting else True

        container_chips_count = initial_data.container_chips_count

        initial_state = StateInfo(
            board_values=board_values,
            my_turn=is_starting,
            my_score=0,
            enemy_score=0,
            chips_left=container_chips_count)

        # Add to db
        initial_state_updated = self.graph.add_game_state(initial_state, is_initial_state=True)
        self.current_state_info = initial_state_updated
        self.last_episode_path.state_info_list.append(initial_state_updated)

    def get_placing_action(self, game_board):
        # Gets PlacingRelationInfo objects list
        relations = self.graph.find_game_state_next_relations(self.current_state_info, rel_type='placing')

        # If 'relations' is empty, then agent explore 100%
        if not relations:
            self.explore_rate = float(1)
            self.exploit_rate = float(0)
        # Else, change exploration rate accordingly to nodes_length
        else:
            relations_length = len(relations)

            explore_rate = float(1 - self.exploit_growth * relations_length)
            exploit_rate = float(1 - explore_rate)
            # If explore rate is negative
            if explore_rate < 0:
                explore_rate = float(self.explore_minimum)
                exploit_rate = float(1 - explore_rate)

            self.explore_rate = explore_rate
            self.exploit_rate = exploit_rate

        # Getting agent's behaviour for this round
        current_behaviour = self.get_agent_behaviour()

        # TODO change to int EXPLORE/EXPLOIT 0/1
        if current_behaviour == "EXPLORE":
            return self.do_explore_placing(game_board)
        elif current_behaviour == "EXPLOIT":
            return self.do_exploit_placing(game_board, relations)

    def get_agent_behaviour(self):
        # Do random choice(not so random, because according to probabilities) for behaviour
        return np.random.choice(self.behaviour, 1, p=[self.exploit_rate, self.explore_rate])

    def do_explore_placing(self, game_board):
        # Choose one action randomly
        return self.get_random_action_for_placing(game_board)

    def do_exploit_placing(self, game_board, relations):
        # Sort list by q_value in decending order
        relations.sort(key=lambda x: x.q_value, reverse=True)

        # Filter irrelevant relations(the ones, which cannot be executed)
        filtered_relations = self.filter_placing_relations(relations)

        # if 'filtered_relations' is empty
        if not filtered_relations:
            return self.do_explore_placing(game_board)

        # Set relation which holds highest q_value
        best_relation = filtered_relations[0]

        # (Can be skipped) Optimization for better exploitation results
        if self.is_improved_exploitation_on:
            next_states_info = self.get_states_by_placing_actions(filtered_relations)
            best_relation = self.get_best_placing_relation(next_states_info, best_relation)

        # Get action for next state
        return PlaceChipAction(best_relation.row, best_relation.col, best_relation.chip_value)

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_states_by_placing_actions(self, relations):
        return [self.graph.find_next_state_by_placing_relation(self.current_state_info, relation)
                for relation in relations]

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_best_placing_relation(self, next_states_info, best_relation):
        get_max_visited_state = max(next_states_info, key=lambda x: x.times_visited)

        # Not the field 'times_visited', but win+lose counter
        get_max_visited = get_max_visited_state.win_counter + get_max_visited_state.lose_counter

        visited_criteria = int(get_max_visited / 3) if int(get_max_visited / 3) > 0 else 1
        win_rate_criteria = 0.50
        best_states = []
        for state in next_states_info:
            wins_plus_loses = state.win_counter + state.lose_counter
            if wins_plus_loses:
                state_win_rate = float(state.win_counter / wins_plus_loses)
                if state_win_rate >= win_rate_criteria and state.times_visited >= visited_criteria:
                    best_states.append(state)
        if best_states:
            next_state = max(best_states, key=lambda x: float(x.win_counter / (x.win_counter + x.lose_counter)))
            best_relation = self.graph.find_placing_relation_info(self.current_state_info, next_state)
            return best_relation
        else:
            return best_relation

    def get_taking_action(self, combinations, last_placed_chip):
        # Gets TakingRelationInfo objects list
        relations = self.graph.find_game_state_next_relations(self.current_state_info, rel_type='taking')

        # If 'nodes' is empty, then agent explore 100%
        if not relations:
            self.explore_rate = float(1)
            self.exploit_rate = float(0)
        # Else, change exploration rate accordingly to nodes_length
        else:
            relations_length = len(relations)

            explore_rate = float(1 - self.exploit_growth * relations_length)
            exploit_rate = float(1 - explore_rate)
            # If explore rate is negative
            if explore_rate < 0:
                explore_rate = float(self.explore_minimum)
                exploit_rate = float(1 - explore_rate)

            self.explore_rate = explore_rate
            self.exploit_rate = exploit_rate

        # Getting agent's behaviour for this round
        current_behaviour = self.get_agent_behaviour()

        if current_behaviour == "EXPLORE":
            return self.do_explore_taking(combinations)
        elif current_behaviour == "EXPLOIT":
            return self.do_exploit_taking(combinations, last_placed_chip, relations)

    @staticmethod
    def do_explore_taking(combinations):
        # Choose one combination randomly
        return combinations[random.randint(0, len(combinations) - 1)]

    def do_exploit_taking(self, combinations, last_placed_chip, relations):
        # Sort list by q_value in decending order
        relations.sort(key=lambda x: x.q_value, reverse=True)

        # Before filtering irrelevant relations, reorganize Chip object into row/col/value list
        last_placed_chip = [last_placed_chip.row, last_placed_chip.col, last_placed_chip.value]
        # Filter irrelevant relations(the ones, which cannot be executed)
        filtered_relations = self.filter_taking_relations(relations, combinations, last_placed_chip)

        # if 'filtered_relations' is empty
        if not filtered_relations:
            return self.do_explore_taking(combinations)

        # Set relation which holds highest q_value
        best_relation = filtered_relations[0]

        # (Can be skipped) Optimization for better exploitation results
        if self.is_improved_exploitation_on:
            next_states_info = self.get_states_by_taking_actions(filtered_relations)
            best_relation = self.get_best_taking_relation(next_states_info, best_relation, last_placed_chip)

        # Get combination for next state
        return best_relation.combination

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_states_by_taking_actions(self, relations):
        next_states_info = []
        for relation in relations:
            info = self.graph.find_next_state_by_taking_relation(self.current_state_info, relation)
            next_states_info.append(info)
        return next_states_info

    def get_best_taking_relation(self, next_states_info, best_relation, last_placed_chip):
        get_max_visited_state = max(next_states_info, key=lambda x: x.times_visited)

        # Not the field 'times_visited', but win+lose counter
        get_max_visited = get_max_visited_state.win_counter + get_max_visited_state.lose_counter

        visited_criteria = int(get_max_visited / 3) if int(get_max_visited / 3) > 0 else 1
        win_rate_criteria = 0.50
        best_states = []
        for state in next_states_info:
            wins_plus_loses = state.win_counter + state.lose_counter
            if wins_plus_loses:
                state_win_rate = float(state.win_counter / wins_plus_loses)
                if state_win_rate >= win_rate_criteria and wins_plus_loses >= visited_criteria:
                    best_states.append(state)
        if best_states:
            next_state = max(best_states, key=lambda x: float(x.win_counter / (x.win_counter + x.lose_counter)))
            best_relation = self.graph.find_taking_relation_info(self.current_state_info, next_state,
                                                                 last_placed_chip)
            return best_relation
        else:
            return best_relation

    def filter_placing_relations(self, relations):
        filtered_relations = []
        for relation in relations:
            # Return if relations starts to be negative q-value
            if relation.q_value < 0:
                return filtered_relations
            # Relation is viable if True
            if relation.chip_value == self.hand_chips[0].value or relation.chip_value == self.hand_chips[1].value:
                filtered_relations.append(relation)
        return filtered_relations

    def filter_taking_relations(self, relations, combinations, last_placed_chip):
        filtered_relations = []
        for relation in relations:
            # Return if relations starts to be negative q-value
            if relation.q_value < 0:
                return filtered_relations
            if tuple(last_placed_chip) == tuple(relation.last_placed_chip):
                for combination in combinations:
                    if self.is_combinations_equal(combination, relation.combination):
                        filtered_relations.append(relation)
                        break
        return filtered_relations

    @staticmethod
    def is_combinations_equal(comb_1, comb_2):
        if len(comb_1) != len(comb_2):
            return False

        for (chip_1, chip_2) in zip(comb_1, comb_2):
            if chip_1.row != chip_2.row or chip_1.col != chip_2.col or chip_1.value != chip_2.value:
                return False
        return True
