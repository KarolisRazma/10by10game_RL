from enum import Enum

import src.agents.agent as ag
import src.agents.improved_agent_learning.path as ph

import src.agents.improved_agent_learning.path_evaluator as pe
import numpy as np
import random

from src.agents.actions.placing_action import PlaceChipAction
from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData
from src.game_components.action_data import ActionData
from src.game_components.state_data import StateData


class Behaviour(Enum):
    EXPLORE = 1
    EXPLOIT = 2


class ImprovedAgent(ag.Agent):
    # @param nickname               --> agent's id
    # @param graph                  --> neoj4 graph
    # @param learning_algorithm     --> class RLearning object

    def __init__(self, name, graph, learning_algorithm, exploit_growth, explore_minimum,
                 is_improved_exploitation_on=False, state_closure_depth=1, exploit_to_closed_state_rate=0.0):
        # Init Agent superclass
        super().__init__(name)

        # Graph stored in Neo4j
        self.graph: Graph = graph

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
        # This parameter sets the rate at which the relationship with the 'to_closed_state' property is used.
        self.exploit_to_closed_state_rate = exploit_to_closed_state_rate

        # List for agent behaviour selection
        self.behaviour = [Behaviour.EXPLOIT, Behaviour.EXPLORE]
        self.is_improved_exploitation_on = is_improved_exploitation_on

        self.this_turn_behaviour = None
        self.exploit_combination_in_this_turn = None

    def observe_state(self, state_data: StateData, action_data: ActionData = None):
        improved_agent_state_data = ImprovedAgentStateData(
            board_values=state_data.board_values,
            my_turn=state_data.my_turn,
            my_score=state_data.my_score,
            enemy_score=state_data.enemy_score,
            chips_left=state_data.chips_left,
            last_placed_chip_list=state_data.last_placed_chip_list,
            hand_chips_values_list=state_data.hand_chips_values_list,
            enemy_hand_chips_values_list=state_data.enemy_hand_chips_values_list,
            container_chips_values_list=state_data.container_chips_values_list,
            is_initial=state_data.is_initial,
            is_final=state_data.is_final
        )
        if state_data.is_final:
            improved_agent_state_data.game_result = self.last_game_result

        self.last_episode_path.state_data_list.append(improved_agent_state_data)
        self.current_state_info = improved_agent_state_data
        if action_data is not None:
            improved_agent_action_data = ImprovedAgentActionData(
                row=action_data.row,
                col=action_data.col,
                chip_value=action_data.chip_value,
                has_taking=action_data.has_taking,
                combination=action_data.combination,
            )
            self.last_episode_path.relation_data_list.append(improved_agent_action_data)

    def select_placing_action(self, game_board):
        return self.select_action(game_board)

    def select_taking_action(self, game_board, combinations):
        # I think, I need to clarify this one:
        # If behaviour is EXPLORE, it means that we didn't have combination yet,
        # But if behaviour is EXPLOIT and the game let us choose combination,
        # Then it means, that we already know what combination we want to exploit.
        if self.this_turn_behaviour == Behaviour.EXPLORE:
            return self.do_explore_taking(combinations)
        else:
            return self.exploit_combination_in_this_turn

    def reset(self):
        super().reset()
        self.last_episode_path.reset()
        self.current_state_info = None

    def eval_path_after_episode(self, state_closure_depth):
        self.path_evaluator.set_path(self.last_episode_path)
        self.path_evaluator.eval_path(self.graph, self.last_game_result, state_closure_depth)

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
        return [relation for relation in relations if relation.q_value > 0.0]

    def select_action(self, game_board):
        relations = self.graph.find_game_state_next_relations(self.current_state_info)

        # Closed state 'select_action' execution
        if self.is_state_closed(relations):
            return self.do_exploit_closed_state(relations[0])

        # Check if any relations leads to closed state
        relations_to_closed_state = self.filter_relations_by_to_closed_state(relations)
        if relations_to_closed_state:
            standart_exploit_explore_rate = float(1 - self.exploit_to_closed_state_rate)
            is_using_to_closed_relation =\
                np.random.choice([0, 1], 1, p=[standart_exploit_explore_rate, self.exploit_to_closed_state_rate])
            if is_using_to_closed_relation:
                return self.do_exploit_pre_closed_state(relations_to_closed_state)

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
        self.this_turn_behaviour = self.get_agent_behaviour()

        if self.this_turn_behaviour == Behaviour.EXPLORE:
            return self.do_explore_placing(game_board)
        elif self.this_turn_behaviour == Behaviour.EXPLOIT:
            return self.do_exploit(game_board, relations)

    def do_explore_placing(self, game_board):
        # Choose one action randomly
        return self.get_random_action_for_placing(game_board)

    @staticmethod
    def do_explore_taking(combinations):
        # Choose one combination randomly
        return combinations[random.randint(0, len(combinations) - 1)]

    def do_exploit(self, game_board, relations):
        # Sort list by q_value in decending order
        relations.sort(key=lambda x: x.q_value, reverse=True)

        positive_relations = self.filter_negative_relation_q_values(relations)

        # if 'positive_relations' is empty
        if not positive_relations:
            self.this_turn_behaviour = Behaviour.EXPLORE
            return self.do_explore_placing(game_board)

        # Set relation which holds highest q_value
        best_relation = positive_relations[0]

        # (Can be skipped) Optimization for better exploitation results
        if self.is_improved_exploitation_on:
            best_relation = self.get_best_relation(relations, best_relation)

        # Can be an empty array, if relation only has placing action
        self.exploit_combination_in_this_turn = best_relation.combination

        return PlaceChipAction(best_relation.row, best_relation.col, best_relation.chip_value)

    @staticmethod
    def is_state_closed(relations):
        if relations:
            # Check if relation is from closed state
            if relations[0].from_closed_state:
                return True
            return False

    def do_exploit_closed_state(self, relation):
        # Set current state to be closed = True
        self.last_episode_path.state_data_list[-1].is_closed = True
        # Set behaviour to EXPLOIT (there's no exploring to do in closed state)
        self.this_turn_behaviour = Behaviour.EXPLOIT
        # Can be an empty array, if relation only has placing action
        self.exploit_combination_in_this_turn = relation.combination
        return PlaceChipAction(relation.row, relation.col, relation.chip_value)

    @staticmethod
    def filter_relations_by_to_closed_state(relations):
        return [relation for relation in relations if relation.to_closed_state]

    # This method exploits relation with property 'to_closed_state' == True
    def do_exploit_pre_closed_state(self, relations):
        self.this_turn_behaviour = Behaviour.EXPLOIT

        chosen_relation = self.get_best_relation(relations, relations[0])

        self.exploit_combination_in_this_turn = chosen_relation.combination

        return PlaceChipAction(chosen_relation.row, chosen_relation.col, chosen_relation.chip_value)