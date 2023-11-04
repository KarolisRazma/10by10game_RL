import copy
import math
import time

import src.agents.agent as ag
import src.agents.improved_agent_learning.path as ph

import src.agents.improved_agent_learning.path_evaluator as pe
import numpy as np
import random

from src.agents.actions.placing_action import PlaceChipAction
from src.game_components.color import Color
from src.utilities.state_changes import StateChangeType, StateChangeData, InitialStateData
from src.agents.improved_agent_learning.state_info import StateInfo

from src.game_components.chip import Chip


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

        self.bench1 = []  # Placing Explore
        self.bench2 = []  # Gets PlacingRelationInfo objects list
        self.bench3 = []  # Gets TakingRelationInfo objects list
        self.bench4 = []  # Placing exploit optimization
        self.bench5 = []  # Taking exploit optimization
        self.bench6 = []  # Placing exploit optimization method get_states_by_placing_actions
        self.bench7 = []  # Placing exploit optimization method get_best_placing_relation
        self.bench8 = []  # Taking exploit optimization method get_states_by_taking_actions
        self.bench9 = []  # Taking exploit optimization method get_best_taking_relation
        self.bench10 = []  # After Placing processing
        self.bench11 = []  # After Taking processing
        self.bench12 = []  # Initial state processing
        self.bench13 = []  # All placing exploitation time
        self.bench14 = []  # Exploit placing sort
        self.bench15 = []  # Exploit placing filter
        self.bench16 = []  # All taking exploitation time
        self.bench17 = []  # Exploit taking sort
        self.bench18 = []  # Exploit taking filter

    def select_placing_action(self, game_data):
        return self.get_placing_action(game_data)

    def select_taking_action(self, game_data, combinations, last_placed_chip):
        return self.get_taking_action(game_data)

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

        start_timer = time.time()
        # Update agent's graph with next board state and placing relation
        updated_next_state_info, placing_relation_info = \
            self.graph.create_next_node_and_make_placing_relation(self.current_state_info,
                                                                  next_state_info, placing_action)
        end_timer = time.time()
        self.bench10.append(end_timer - start_timer)

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

        start_timer = time.time()
        # Update agent's graph with next board state and taking relation
        updated_next_state_info, taking_relation_info = \
            self.graph.create_next_node_and_make_taking_relation(self.current_state_info, next_state_info,
                                                                 taking_combination, last_placed_chip)
        end_timer = time.time()
        self.bench11.append(end_timer - start_timer)

        # Append taking relation and next state to path
        self.last_episode_path.relation_info_list.append(taking_relation_info)
        self.last_episode_path.state_info_list.append(updated_next_state_info)

        # Update current state
        self.current_state_info = updated_next_state_info

    # def get_random_action_for_placing(self, game_board):
    #     # Loop while action is not selected
    #     # fixme can cause problems if board is full
    #     start_timer = time.time()
    #     while True:
    #         random_tile_index = random.randint(0, len(game_board.tiles) - 1)
    #         if game_board.is_tile_empty(random_tile_index):
    #             tile_row = math.floor(random_tile_index / game_board.border_length)
    #             tile_col = random_tile_index % game_board.border_length
    #             hand_chip_index = random.randint(0, 1)
    #
    #             end_timer = time.time()
    #             self.bench1.append(end_timer - start_timer)
    #
    #             return PlaceChipAction(tile_row, tile_col, self.hand_chips[hand_chip_index].value)

    def more_states(self, game_board, game_data):
        actions = []  # first, clear action list
        for tile in range(len(game_board.tiles)):
            if game_board.is_tile_empty(tile):
                tile_row = math.floor(tile / game_board.border_length)
                tile_col = tile % game_board.border_length
                actions.append(PlaceChipAction(tile_row, tile_col, 1))
                actions.append(PlaceChipAction(tile_row, tile_col, 2))
                actions.append(PlaceChipAction(tile_row, tile_col, 3))
        for action in actions:
            board_values = self.make_next_board_value_after_placing(game_board, action)
            next_state_info = StateInfo(board_values=board_values,
                                        my_turn=game_data["my_turn"],
                                        my_score=self.score,
                                        enemy_score=game_data["enemy_score"],
                                        chips_left=game_data["chips_left"])
            self.graph.create_next_node_and_make_placing_relation(self.current_state_info, next_state_info, action)

    def get_random_action_for_placing(self, game_data):
        game_board = game_data["game_board"]
        self.more_states(game_board, game_data)
        actions = []  # first, clear action list
        next_state_infos = []
        # loop over all tiles

        if game_data["my_turn"]:
            for tile in range(len(game_board.tiles)):
                if game_board.is_tile_empty(tile):
                    tile_row = math.floor(tile / game_board.border_length)
                    tile_col = tile % game_board.border_length
                    actions.append(PlaceChipAction(tile_row, tile_col, self.hand_chips[0].value))
                    actions.append(PlaceChipAction(tile_row, tile_col, self.hand_chips[1].value))
        else:
            for tile in range(len(game_board.tiles)):
                if game_board.is_tile_empty(tile):
                    tile_row = math.floor(tile / game_board.border_length)
                    tile_col = tile % game_board.border_length
                    actions.append(PlaceChipAction(tile_row, tile_col, game_data["agent_chips"][0].value))
                    actions.append(PlaceChipAction(tile_row, tile_col, game_data["agent_chips"][1].value))
        # Next states (to DB)
        for action in actions:
            board_values = self.make_next_board_value_after_placing(game_board, action)
            next_state_info = StateInfo(board_values=board_values,
                                        my_turn=game_data["my_turn"],
                                        my_score=self.score,
                                        enemy_score=game_data["enemy_score"],
                                        chips_left=game_data["chips_left"])
            next_state_infos.append(next_state_info)
            self.graph.create_next_node_and_make_placing_relation(self.current_state_info, next_state_info, action)

        relations = self.graph.find_game_state_next_relations(self.current_state_info)

        if game_data["my_turn"]:
            game_data["file"].write(f'{len(relations)},')

        index = random.randint(0, len(actions) - 1)
        return actions[index], next_state_infos[index]

    @staticmethod
    def make_next_board_value_after_placing(game_board, action):
        board_copy = copy.deepcopy(game_board)
        board_copy.add_chip_rowcol(action.row, action.col, Chip(action.value))
        return board_copy.board_to_chip_values()

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

        start_timer = time.time()
        # Add to db
        initial_state_updated = self.graph.add_game_state(initial_state, is_initial_state=True)
        end_timer = time.time()
        self.bench12.append(end_timer - start_timer)

        self.current_state_info = initial_state_updated
        self.last_episode_path.state_info_list.append(initial_state_updated)

    def get_placing_action(self, game_data):
        # Gets PlacingRelationInfo objects list

        # TODO parodyti relations kieki


        return self.do_explore_placing(game_data)

        # # If 'relations' is empty, then agent explore 100%
        # if not relations:
        #     self.explore_rate = float(1)
        #     self.exploit_rate = float(0)
        # # Else, change exploration rate accordingly to nodes_length
        # else:
        #     relations_length = len(relations)
        #
        #     explore_rate = float(1 - self.exploit_growth * relations_length)
        #     exploit_rate = float(1 - explore_rate)
        #     # If explore rate is negative
        #     if explore_rate < 0:
        #         explore_rate = float(self.explore_minimum)
        #         exploit_rate = float(1 - explore_rate)
        #
        #     self.explore_rate = explore_rate
        #     self.exploit_rate = exploit_rate
        #
        # # Getting agent's behaviour for this round
        # current_behaviour = self.get_agent_behaviour()

        # # TODO change to int EXPLORE/EXPLOIT 0/1
        # if current_behaviour == "EXPLORE":
        #
        # elif current_behaviour == "EXPLOIT":
        #     return self.do_exploit_placing(game_data, relations)

    def get_agent_behaviour(self):
        # Do random choice(not so random, because according to probabilities) for behaviour
        return np.random.choice(self.behaviour, 1, p=[self.exploit_rate, self.explore_rate])

    def do_explore_placing(self, game_data):
        # Choose one action randomly
        return self.get_random_action_for_placing(game_data)

    def do_exploit_placing(self, game_board, relations):
        exploit_start_timer = time.time()

        start_timer = time.time()
        # Sort list by q_value in decending order
        relations.sort(key=lambda x: x.q_value, reverse=True)
        end_timer = time.time()
        self.bench14.append(end_timer - start_timer)

        start_timer = time.time()
        # Filter irrelevant relations(the ones, which cannot be executed)
        filtered_relations = self.filter_placing_relations(relations)
        end_timer = time.time()
        self.bench15.append(end_timer - start_timer)

        # if 'filtered_relations' is empty
        if not filtered_relations:
            return self.do_explore_placing(game_board)

        # Set relation which holds highest q_value
        best_relation = filtered_relations[0]

        # (Can be skipped) Optimization for better exploitation results
        if self.is_improved_exploitation_on:
            start_timer = time.time()
            next_states_info = self.get_states_by_placing_actions(filtered_relations)
            best_relation = self.get_best_placing_relation(next_states_info, best_relation)
            end_timer = time.time()
            self.bench4.append(end_timer - start_timer)

        exploit_end_timer = time.time()
        self.bench13.append(exploit_end_timer - exploit_start_timer)

        return PlaceChipAction(best_relation.row, best_relation.col, best_relation.chip_value)

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_states_by_placing_actions(self, relations):
        start_timer = time.time()
        next_states_info = []
        for relation in relations:
            info = self.graph.find_next_state_by_placing_relation(self.current_state_info, relation)
            next_states_info.append(info)
        end_timer = time.time()
        self.bench6.append(end_timer - start_timer)
        return next_states_info

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_best_placing_relation(self, next_states_info, best_relation):
        start_timer = time.time()
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
            end_timer = time.time()
            self.bench7.append(end_timer - start_timer)
            return best_relation
        else:
            end_timer = time.time()
            self.bench7.append(end_timer - start_timer)
            return best_relation

    def get_taking_action(self, game_data):
        # Gets TakingRelationInfo objects list
        return self.do_explore_taking(game_data)

        # If 'nodes' is empty, then agent explore 100%
        # if not relations:
        #     self.explore_rate = float(1)
        #     self.exploit_rate = float(0)
        # # Else, change exploration rate accordingly to nodes_length
        # else:
        #     relations_length = len(relations)
        #
        #     explore_rate = float(1 - self.exploit_growth * relations_length)
        #     exploit_rate = float(1 - explore_rate)
        #     # If explore rate is negative
        #     if explore_rate < 0:
        #         explore_rate = float(self.explore_minimum)
        #         exploit_rate = float(1 - explore_rate)
        #
        #     self.explore_rate = explore_rate
        #     self.exploit_rate = exploit_rate

        # # Getting agent's behaviour for this round
        # current_behaviour = self.get_agent_behaviour()
        #
        # if current_behaviour == "EXPLORE":

        # elif current_behaviour == "EXPLOIT":
        #     return self.do_exploit_taking(combinations, last_placed_chip, relations)

    def do_explore_taking(self, game_data):
        next_state_infos = []
        for combination in game_data["combinations"]:
            board_values, score, chips_left = self.make_next_board_value_after_taking(game_data["game_board"],
                                                                                      combination,
                                                                                      game_data["last_placed_chip"],
                                                                                      game_data["chips_left"],
                                                                                      game_data["my_turn"],
                                                                                      game_data["enemy_score"])
            if game_data["my_turn"]:
                next_state_info = StateInfo(board_values=board_values,
                                            my_turn=game_data["my_turn"],
                                            my_score=score,
                                            enemy_score=game_data["enemy_score"],
                                            chips_left=chips_left)
            else:
                next_state_info = StateInfo(board_values=board_values,
                                            my_turn=game_data["my_turn"],
                                            my_score=self.score,
                                            enemy_score=score,
                                            chips_left=chips_left)
            next_state_infos.append(next_state_info)
            last_placed_chip = [game_data["last_placed_chip"].row, game_data["last_placed_chip"].col,
                                game_data["last_placed_chip"].value]

            self.graph.create_next_node_and_make_taking_relation(self.current_state_info, next_state_info, combination,
                                                                 last_placed_chip)

        # Choose one combination randomly
        relations = self.graph.find_game_state_next_relations(self.current_state_info)

        if game_data["my_turn"]:
            game_data["file"].write(f'{len(relations)},')

        index = random.randint(0, len(game_data["combinations"]) - 1)
        return game_data["combinations"][index], next_state_infos[index]

    def make_next_board_value_after_taking(self, game_board, combination, last_placed_chip, chips_left, my_turn,
                                           enemy_score):
        board_copy = copy.deepcopy(game_board)

        if my_turn:
            score_copy = self.score
        else:
            score_copy = enemy_score

        chips_left_copy = chips_left
        for chip in combination:
            if chip.row == last_placed_chip.row and chip.col == last_placed_chip.col:
                continue
            tile = board_copy.get_tile_at_index(chip.row * board_copy.border_length + chip.col)
            if tile.color == Color.RED:
                board_copy.remove_chip(chip.row * board_copy.border_length + chip.col)
                chips_left_copy += 1
                continue
            if tile.color == Color.BLUE:
                board_copy.remove_chip(chip.row * board_copy.border_length + chip.col)
                if chips_left_copy > 0:
                    chips_left_copy -= 1
                score_copy += 2
                continue
            if tile.color == Color.WHITE:
                board_copy.remove_chip(chip.row * board_copy.border_length + chip.col)
                score_copy += 1
        return board_copy.board_to_chip_values(), score_copy, chips_left_copy

    def do_exploit_taking(self, combinations, last_placed_chip, relations):
        exploit_start_timer = time.time()

        start_timer = time.time()
        # Sort list by q_value in decending order
        relations.sort(key=lambda x: x.q_value, reverse=True)
        end_timer = time.time()
        self.bench17.append(end_timer - start_timer)

        # Before filtering irrelevant relations, reorganize Chip object into row/col/value list
        last_placed_chip = [last_placed_chip.row, last_placed_chip.col, last_placed_chip.value]

        start_timer = time.time()
        # Filter irrelevant relations(the ones, which cannot be executed)
        filtered_relations = self.filter_taking_relations(relations, combinations, last_placed_chip)
        end_timer = time.time()
        self.bench18.append(end_timer - start_timer)

        # if 'filtered_relations' is empty
        if not filtered_relations:
            return self.do_explore_taking(combinations)

        # Set relation which holds highest q_value
        best_relation = filtered_relations[0]

        # (Can be skipped) Optimization for better exploitation results

        if self.is_improved_exploitation_on:
            start_timer = time.time()
            next_states_info = self.get_states_by_taking_actions(filtered_relations)
            best_relation = self.get_best_taking_relation(next_states_info, best_relation, last_placed_chip)
            end_timer = time.time()
            self.bench5.append(end_timer - start_timer)

        exploit_end_timer = time.time()
        self.bench16.append(exploit_end_timer - exploit_start_timer)

        return best_relation.combination

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_states_by_taking_actions(self, relations):
        start_timer = time.time()
        next_states_info = []
        for relation in relations:
            info = self.graph.find_next_state_by_taking_relation(self.current_state_info, relation)
            next_states_info.append(info)
        end_timer = time.time()
        self.bench8.append(end_timer - start_timer)
        return next_states_info

    def get_best_taking_relation(self, next_states_info, best_relation, last_placed_chip):
        start_timer = time.time()
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
            end_timer = time.time()
            self.bench9.append(end_timer - start_timer)
            return best_relation
        else:
            end_timer = time.time()
            self.bench9.append(end_timer - start_timer)
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
