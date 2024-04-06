from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.agents.improved_agent_learning.learning import RLearning
from src.agents.improved_agent_learning.path import Path
from src.game_components.game_result import GameResult
from src.utilities.relation_cutting_parameters import RelationCuttingParameters


class PathEvaluator:

    def __init__(self, learning: RLearning):
        # noinspection PyTypeChecker
        self.path: Path = None
        self.learning = learning
        self.cut_counter = 1

    def set_path(self, path: Path):
        self.path = path

    def eval_path(self, graph: Graph, last_game_result: GameResult, is_exploration_phase: bool):

        # Process final state
        graph.find_or_create_final_state(self.path.state_data_list[-1])

        # Remove final state from the list
        current_state_data = self.path.state_data_list.pop()

        # Reverse path (states and relations)
        self.path.state_data_list.reverse()
        self.path.relation_data_list.reverse()

        # Get relations count, set first step flag to True
        relations_left = len(self.path.relation_data_list)
        is_first_step = True

        for (previous_state_data, relation_data) in zip(self.path.state_data_list, self.path.relation_data_list):
            # Handle first step
            if is_first_step:
                # Immediate reward
                relation_data.q_value = self.learning.final_state_reward(last_game_result)
                is_first_step = False
            else:
                relation_data.q_value = self.learning.calc_new_q_value(graph, current_state_data, relation_data)

            graph.find_or_create_previous_state_and_make_next_relation(previous_state_data, relation_data,
                                                                       current_state_data)
            # relation_data.is_cut = self.cut_needed(relation_data, last_game_result, relations_left,
            # is_exploration_phase)
            relations_left -= 1
            graph.update_relation_properties(previous_state_data, relation_data, last_game_result)
            current_state_data = previous_state_data

    def cut_needed(self, relation: ImprovedAgentActionData, last_game_result: GameResult,
                   relations_left: int, is_exploration_phase: bool):
        if is_exploration_phase:
            return False

        times_used = relation.times_used
        win_counter = relation.win_counter
        lose_counter = relation.lose_counter
        draw_counter = relation.draw_counter
        if last_game_result == GameResult.WON:
            win_counter += 1
        elif last_game_result == GameResult.LOST:
            lose_counter += 1
        elif last_game_result == GameResult.DRAW:
            draw_counter += 1
        times_used += 1

        if relations_left == 1:
            criteria = RelationCuttingParameters.ON_FIRST_RELATION_TIMES_USED
        elif relations_left == len(self.path.relation_data_list):
            criteria = RelationCuttingParameters.ON_LAST_RELATION_TIMES_USED
        else:
            criteria = \
                RelationCuttingParameters.GROWTH_TIMES_USED * (len(self.path.relation_data_list) - relations_left + 1)

        if times_used >= criteria:
            lose_rate = lose_counter / times_used
            return lose_rate >= RelationCuttingParameters.LOSE_RATE_BOUND
        return False
