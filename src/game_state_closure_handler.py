from src.agents.improved_agent import ImprovedAgent
from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData
from src.agents.improved_agent_learning.path import Path
from src.custom_environment import CustomEnvironment
import src.utilities.constants3x3 as c3x3
from src.game_components.board import Board
from src.game_components.game_result import GameResult


class GameStateClosureHandler:
    def __init__(self, lowest_path_len_to_start_closure: int,
                 depth_in_interval_from_7_to_8: int, depth_in_interval_from_9_to_9: int, depth_in_interval_from_10: int,
                 target_agent=None, game_path=None):
        self.custom_environment = CustomEnvironment(scoring_parameter=c3x3.scoring_parameter,
                                                    score_to_win=c3x3.score_to_win,
                                                    board=Board(c3x3.board_border_len),
                                                    )
        self.target_agent: ImprovedAgent = target_agent
        self.game_path: Path = game_path
        self.depth = 1

        self.lowest_path_len_to_start_closure = lowest_path_len_to_start_closure

        # 'Interval' means game path len between some values
        # And according to interval, closure handler will use dynamic depth.
        self.depth_in_interval_from_7_to_8 = depth_in_interval_from_7_to_8
        self.depth_in_interval_from_9_to_9 = depth_in_interval_from_9_to_9
        self.depth_in_interval_from_10 = depth_in_interval_from_10

    def set_target_agent(self, target_agent: ImprovedAgent):
        self.target_agent = target_agent

    def set_game_path(self, game_path: Path):
        # Set game_path
        self.game_path = game_path
        self.game_path.state_data_list = game_path.state_data_list[-self.depth:]
        if self.depth > 1:
            self.game_path.relation_data_list = game_path.relation_data_list[-(self.depth-1):]
        else:
            self.game_path.relation_data_list = []

    def get_starting_state_data(self):
        return self.game_path.state_data_list[0]

    def get_starting_action_data(self):
        return self.game_path.relation_data_list[0]

    def start_closure(self):
        starting_state_data = self.get_starting_state_data()

        # Check if is_closed == True (on starting state)
        if starting_state_data.is_closed:
            return

        # Check if is_final == True (on starting state)
        if starting_state_data.is_final:
            starting_state_data.is_closed = True
            self.target_agent.graph.close_game_state(starting_state_data)
            return

        self.close_state_recursively(starting_state_data)

    def close_state_recursively(self, current_state_data: ImprovedAgentStateData):
        pairs = self.get_next_action_states_pairs(current_state_data)

        # If it is an enemy agent's move, then add action-states pairs to graph
        if not current_state_data.my_turn:
            pairs_is_closed_list = self.add_pairs_to_graph(current_state_data, pairs)

            for pair, is_closed_list in zip(pairs, pairs_is_closed_list):
                # pair[0] contains ActionData, pair[1] contains list of StateData
                for next_state_data, is_closed in zip(pair[1], is_closed_list):
                    # If state is closed, then continue to next iteration
                    if is_closed:
                        continue
                    # If not final, then go deeper recursively
                    if not next_state_data.is_final:
                        self.close_state_recursively(next_state_data)
                    next_state_data.is_closed = True
                    self.target_agent.graph.close_game_state(next_state_data)

            # Eventually, close the current state data
            current_state_data.is_closed = True
            self.target_agent.graph.close_game_state(current_state_data)

        # Otherwise, check where every action-state pair leads
        else:
            chosen_pair = self.get_highest_score_pair(pairs)

            # Check if current state does not contain any old relations
            old_relations = self.target_agent.graph.find_game_state_next_relations(current_state_data)
            if old_relations:
                # Remove old relations from the graph
                for relation in old_relations:
                    self.target_agent.graph.remove_relation(current_state_data, relation)

            # The chosen pair need to be added to db
            is_closed_list = self.add_pair_to_graph(current_state_data, chosen_pair)

            for next_state_data, is_closed in zip(chosen_pair[1], is_closed_list):
                # If state is closed, then continue to next iteration
                if is_closed:
                    continue
                # If not final, then go deeper recursively
                if not next_state_data.is_final:
                    self.close_state_recursively(next_state_data)
                next_state_data.is_closed = True
                self.target_agent.graph.close_game_state(next_state_data)

            # Eventually, close the current state data
            current_state_data.is_closed = True
            self.target_agent.graph.close_game_state(current_state_data)

    def get_next_action_states_pairs(self, state_data):
        # Prepare environment for moves generation
        self.custom_environment.prepare_custom_game(state_data, self.target_agent)

        # Get agent, whose turn is it in given state data
        playing_agent = self.custom_environment.agent_1 if state_data.my_turn else self.custom_environment.agent_2

        # Generate placing moves
        placing_moves = playing_agent.generate_actions_from_position(self.custom_environment.board)

        # Iterate through every placing move and collect all pairs
        next_action_state_pairs_list = []
        for move in placing_moves:
            next_action_state_pairs_list.extend(
                self.custom_environment.get_next_action_states_pairs_by_placing_action(state_data, move)
            )
        return next_action_state_pairs_list

    def add_pairs_to_graph(self, current_state_data, pairs):
        pairs_states_is_closed_flag_values = []
        for pair in pairs:
            pairs_states_is_closed_flag_values.append(self.add_pair_to_graph(current_state_data, pair))
        return pairs_states_is_closed_flag_values

    def add_pair_to_graph(self, current_state_data, pair):
        pair_states_is_closed_flag_values = []
        for state in pair[1]:
            is_closed = \
                self.target_agent.graph.find_or_create_next_game_state_and_make_rel(current_state_data, pair[0], state)
            pair_states_is_closed_flag_values.append(is_closed)
        return pair_states_is_closed_flag_values

    def get_highest_score_pair(self, pairs):
        pairs_score_list = []
        for pair in pairs:
            for next_state_data in pair[1]:
                game_results_list = []
                if next_state_data.is_final:
                    game_results_list.append(next_state_data.game_result)
                else:
                    game_results_list.append(
                        self.custom_environment.get_custom_game_result(next_state_data, self.target_agent)
                    )
            pair_score = 0
            for game_result in game_results_list:
                if game_result == GameResult.WON:
                    pair_score += 2
                if game_result == GameResult.DRAW:
                    pair_score += 1
                if game_result == GameResult.LOST:
                    pair_score += 0
            pairs_score_list.append(pair_score)
        highest_score_pair_index = pairs_score_list.index(max(pairs_score_list))
        return pairs[highest_score_pair_index]

    def calculate_depth(self, path_len):
        if path_len >= self.lowest_path_len_to_start_closure:
            if path_len < 9:
                self.depth = self.depth_in_interval_from_7_to_8
            if path_len == 9:
                self.depth = self.depth_in_interval_from_9_to_9
            if path_len > 9:
                self.depth = self.depth_in_interval_from_10
        else:
            self.depth = 1
        # print(f'Depth this episode: {self.depth}')
        return self.depth
