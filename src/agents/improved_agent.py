import src.game_components.chip as cp
import src.game_components.color as clr
import src.agents.agent as ag
import src.agents.improved_agent_learning.path as ph
import src.agents.improved_agent_learning.state_info as sti
import src.agents.improved_agent_learning.placing_relation_info as pri
import src.agents.improved_agent_learning.taking_relation_info as tri
import src.agents.improved_agent_learning.path_evaluator as pe
import numpy as np
import random
import copy


class ImprovedAgent(ag.Agent):
    # @param nickname               --> agent's id
    # @param graph                  --> neoj4 graph
    # @param learning_algorithm     --> class RLearning object

    def __init__(self, nickname, graph, learning_algorithm, exploit_growth, explore_minimum,
                 is_improved_exploitation_on=False):
        # Init Agent superclass
        super().__init__(nickname)

        # Graph stored in Neo4j
        self.graph = graph

        # Path evaluation field
        self.path_evaluator = pe.PathEvaluator(learning_algorithm)

        # Every move which happened in last episode stored here
        self.last_episode_path = ph.Path()

        # Game state info (current/next)
        self.next_states_board_values = None
        self.current_state_info = None
        self.next_state_info = None

        # Random next node selection rate
        self.explore_rate = float(1)
        # Best next node selection rate
        self.exploit_rate = float(1 - self.explore_rate)
        self.explore_minimum = explore_minimum
        self.exploit_growth = exploit_growth

        # List for agent behaviour selection
        self.behaviour = ["EXPLOIT", "EXPLORE"]
        self.is_improved_exploitation_on = is_improved_exploitation_on

    def reset(self):
        self.score = 0
        self.chips = []
        self.captured_chips = []
        self.last_episode_path.reset()
        self.next_states_board_values = None
        self.current_state_info = None
        self.next_state_info = None
        self.is_last_game_won = None
        self.is_last_game_drawn = None

    def eval_path_after_episode(self):
        self.path_evaluator.set_path(self.last_episode_path)
        self.path_evaluator.eval_path(self.graph, self.is_last_game_won, self.is_last_game_drawn)

    def process_initial_state(self, initial_board_values, chips_left):
        initial_state = sti.StateInfo(board_values=initial_board_values, my_turn=self.agent_number, my_score=0,
                                      enemy_score=0, chips_left=chips_left)
        # Add to db
        self.graph.add_game_state(initial_state, is_initial_state=True)
        initial_state_updated = self.graph.find_game_state(initial_state)
        self.current_state_info = initial_state_updated
        self.last_episode_path.state_info_list.append(initial_state_updated)

    def get_placing_action(self, game_board):
        nodes = self.graph.find_game_state_next_vertices(action_type='placing', state_info=self.current_state_info)

        # If 'nodes' is empty, then agent explore 100%
        if not nodes:
            self.explore_rate = float(1)
            self.exploit_rate = float(0)
        # Else, change exploration rate accordingly to nodes_length
        else:
            nodes_length = len(nodes)

            explore_rate = float(1 - self.exploit_growth * nodes_length)
            exploit_rate = float(1 - explore_rate)
            # If explore rate is negative
            if explore_rate < 0:
                explore_rate = float(self.explore_minimum)
                exploit_rate = float(1 - explore_rate)

            self.explore_rate = explore_rate
            self.exploit_rate = exploit_rate

        # Getting agent's behaviour for this round
        current_behaviour = self.get_agent_behaviour()

        # Get all actions from current position (in the field self.actions)
        self.get_actions_for_placing(game_board)

        if current_behaviour == "EXPLORE":
            return self.do_explore_placing(game_board)
        elif current_behaviour == "EXPLOIT":
            return self.do_exploit_placing(game_board)

    def get_agent_behaviour(self):
        # Do random choice(not so random, because according to probabilities) for behaviour
        return np.random.choice(self.behaviour, 1, p=[self.exploit_rate, self.explore_rate])

    def do_explore_placing(self, game_board):
        # Choose one action randomly
        random_index = random.randint(0, len(self.actions) - 1)
        selected_action = self.actions[random_index]

        # Get board values
        next_board_values = self.convert_placing_action_to_board_values(selected_action, game_board)

        # Make StateInfo object
        enemy_score = self.current_state_info.enemy_score
        chips_left = self.current_state_info.chips_left - 1
        self.next_state_info = sti.StateInfo(board_values=next_board_values, my_turn=1, my_score=self.score,
                                             enemy_score=enemy_score, chips_left=chips_left)

        # Try to add it to db
        self.graph.add_game_state(self.next_state_info)
        # Make placing rel
        self.graph.make_placing_rel(self.current_state_info, self.next_state_info, selected_action)

        # Update next_state_info
        self.next_state_info = self.graph.find_game_state(self.next_state_info)
        # Get placing_relation_info from db
        placing_relation_info = self.graph.find_placing_relation_info(self.current_state_info, self.next_state_info)

        # Add to the path
        self.last_episode_path.relation_info_list.append(placing_relation_info)
        self.last_episode_path.state_info_list.append(self.next_state_info)

        return selected_action

    def do_exploit_placing(self, game_board):
        # Get next board values (need for filtering)
        self.next_states_board_values = self.convert_placing_actions(game_board)

        # Get nodes to which agent could move
        nodes = self.filter_nodes(self.graph.find_game_state_next_vertices
                                  (action_type='placing', state_info=self.current_state_info))
        # if 'nodes' is empty
        if not nodes:
            return self.do_explore_placing(game_board)

        # Extra validation to check if agent can do best possible action
        if nodes:
            # Nodes which agent might can do
            # Get all relations from that node
            relations_info = self.graph.find_game_state_next_relations(self.current_state_info, rel_type='placing')
            while len(relations_info) != 0:
                # First element in the list will have the highest q-value
                relations_info.sort(key=lambda x: x.q_value, reverse=True)
                # Node is viable if True
                if self.chips[0].value == relations_info[0].chip_value or \
                        self.chips[1].value == relations_info[0].chip_value:
                    best_relation = relations_info[0]
                    break
                # If reached, then relation is not possible to be made
                # Remove that relation
                del relations_info[0]
            if len(relations_info) == 0:
                # Do explore
                return self.do_explore_placing(game_board)

        # TODO DO IMPROVED EXPLOITATION FOR PLACING
        if self.is_improved_exploitation_on:
            # Filter relations, and get the ones that are possible to do
            relations = self.filter_placing_exploitation(relations_info)
            if relations:
                next_states_info = self.get_states_by_placing_actions(relations)
                best_relation = self.get_best_placing_relation(next_states_info, relations_info[0])

        # Update next_state_info
        self.next_state_info = self.graph.find_next_state_by_placing_relation(self.current_state_info, best_relation)

        # Add to the path
        self.last_episode_path.relation_info_list.append(best_relation)
        self.last_episode_path.state_info_list.append(self.next_state_info)

        # Get action for next state
        return self.graph.find_next_placing_action(self.current_state_info, self.next_state_info)

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def filter_placing_exploitation(self, relations_info):
        filtered_relations = []
        for relation in relations_info:
            # Return if relations starts to be negative q-value
            if relation.q_value < 0:
                return filtered_relations
            # Relation is viable if True
            if self.chips[0].value == relation.chip_value or self.chips[1].value == relation.chip_value:
                filtered_relations.append(relation)
        return filtered_relations

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_states_by_placing_actions(self, relations):
        next_states_info = []
        for relation in relations:
            info = self.graph.find_next_state_by_placing_relation(self.current_state_info, relation)
            next_states_info.append(info)
        return next_states_info

    def get_best_placing_relation(self, next_states_info, best_relation):
        get_max_visited = (max(next_states_info, key=lambda x: x.times_visited)).times_visited
        visited_criteria = int(get_max_visited / 3) if int(get_max_visited / 3) > 0 else 1
        win_rate_criteria = 0.50
        best_states = []
        for state in next_states_info:
            state_win_rate = float(state.win_counter / state.times_visited)
            if state_win_rate >= win_rate_criteria and state.times_visited >= visited_criteria:
                best_states.append(state)
        if best_states:
            next_state = max(best_states, key=lambda x: float(x.win_counter / x.times_visited))
            best_relation = self.graph.find_placing_relation_info(self.current_state_info, next_state)
            return best_relation
        else:
            return best_relation

    def filter_nodes(self, nodes):
        updated_nodes = []
        for node in nodes:
            if node.board_values in self.next_states_board_values:
                updated_nodes.append(node)
        return updated_nodes

    def set_current_state_info(self):
        self.current_state_info = copy.deepcopy(self.next_state_info)

    def get_taking_action(self, game_board, combinations, last_placed_chip):
        nodes = self.graph.find_game_state_next_vertices(action_type='taking', state_info=self.current_state_info)

        # If 'nodes' is empty, then agent explore 100%
        if not nodes:
            self.explore_rate = float(1)
            self.exploit_rate = float(0)
        # Else, change exploration rate accordingly to nodes_length
        else:
            nodes_length = len(nodes)

            explore_rate = float(1 - self.exploit_growth * nodes_length)
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
            return self.do_explore_taking(game_board, combinations, last_placed_chip)
        elif current_behaviour == "EXPLOIT":
            return self.do_exploit_taking(game_board, combinations, last_placed_chip)

    def do_explore_taking(self, game_board, combinations, last_placed_chip):
        # Choose one combination randomly
        random_index = random.randint(0, len(combinations) - 1)
        selected_combination = combinations[random_index]

        # Get board values
        next_board_values = self.convert_taking_action_to_board_values(game_board, selected_combination,
                                                                       last_placed_chip[0], last_placed_chip[1])

        enemy_score = self.current_state_info.enemy_score
        my_score = self.get_next_state_score_after_taking(game_board, selected_combination,
                                                          last_placed_chip[0], last_placed_chip[1])
        chips_left = self.get_next_state_chips_left_after_taking(game_board, self.current_state_info.chips_left,
                                                                 selected_combination, last_placed_chip[0],
                                                                 last_placed_chip[1])
        self.next_state_info = sti.StateInfo(board_values=next_board_values, my_turn=1, my_score=my_score,
                                             enemy_score=enemy_score, chips_left=chips_left)

        # Try to add it to db
        self.graph.add_game_state(self.next_state_info)
        # Make taking rel
        self.graph.make_taking_rel(self.current_state_info, self.next_state_info,
                                   selected_combination, last_placed_chip)

        # Update next_state_info
        self.next_state_info = self.graph.find_game_state(self.next_state_info)

        # Get taking_relation_info from db
        taking_relation_info = self.graph.find_taking_relation_info(self.current_state_info, self.next_state_info,
                                                                    last_placed_chip)

        # Add to the path
        self.last_episode_path.relation_info_list.append(taking_relation_info)
        self.last_episode_path.state_info_list.append(self.next_state_info)

        return self.graph.find_next_taking_action(self.current_state_info, self.next_state_info, last_placed_chip)

    def do_exploit_taking(self, game_board, combinations, last_placed_chip):
        # Get next board values (need for filtering)
        self.next_states_board_values = self.convert_taking_actions(game_board, combinations, last_placed_chip[0],
                                                                    last_placed_chip[1])
        # Get nodes to which agent could move
        nodes = self.filter_nodes(self.graph.find_game_state_next_vertices
                                  (action_type='taking', state_info=self.current_state_info))
        # if 'nodes' is empty
        if not nodes:
            return self.do_explore_taking(game_board, combinations, last_placed_chip)

        # Extra validation to check if agent can do best possible action
        if nodes:
            # Nodes which agent might can do
            # Get all relations from that node
            relations_info = self.graph.find_game_state_next_relations(self.current_state_info, rel_type='taking')
            while len(relations_info) != 0:
                # First element in the list will have the highest q-value
                relations_info.sort(key=lambda x: x.q_value, reverse=True)

                is_relation_viable = False
                # Check if relation is viable
                # First last_placed_chip should be equal to relations.info[0].last_placed_chip
                if tuple(last_placed_chip) == tuple(relations_info[0].last_placed_chip):
                    for combination in combinations:
                        # Transform into list of ints [row, col, value]
                        transformed_combination = self.transform_combination(combination)

                        if tuple(transformed_combination) == tuple(relations_info[0].combination):
                            is_relation_viable = True
                            best_relation = relations_info[0]
                            break
                # Check flag value
                if not is_relation_viable:
                    # If reached, then relation is not possible to be made
                    # Remove that relation
                    del relations_info[0]
                else:
                    # Relation is viable
                    break
            if len(relations_info) == 0:
                # Do explore
                return self.do_explore_taking(game_board, combinations, last_placed_chip)

        # TODO DO IMPROVED EXPLOITATION FOR TAKING
        if self.is_improved_exploitation_on:
            # Filter relations, and get the ones that are possible to do
            relations = self.filter_taking_exploitation(relations_info, combinations, last_placed_chip)
            if relations:
                next_states_info = self.get_states_by_taking_actions(relations)
                best_relation = self.get_best_taking_relation(next_states_info, relations_info[0], last_placed_chip)

        # Update next_state_info
        self.next_state_info = self.graph.find_next_state_by_taking_relation(self.current_state_info, best_relation)

        # Add to the path
        self.last_episode_path.relation_info_list.append(best_relation)
        self.last_episode_path.state_info_list.append(self.next_state_info)

        # Get action for next state
        return self.graph.find_next_taking_action(self.current_state_info, self.next_state_info, last_placed_chip)

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def filter_taking_exploitation(self, relations_info, combinations, last_placed_chip):
        filtered_relations = []
        for relation in relations_info:
            # Return if relations starts to be negative q-value
            if relation.q_value < 0:
                return filtered_relations

            if tuple(last_placed_chip) == tuple(relation.last_placed_chip):
                for combination in combinations:
                    # Transform into list of ints [row, col, value]
                    transformed_combination = self.transform_combination(combination)
                    if tuple(transformed_combination) == tuple(relation.combination):
                        filtered_relations.append(relation)

        return filtered_relations

    # THIS IS ONLY FOR IMPROVED EXPLOITATION
    def get_states_by_taking_actions(self, relations):
        next_states_info = []
        for relation in relations:
            info = self.graph.find_next_state_by_taking_relation(self.current_state_info, relation)
            next_states_info.append(info)
        return next_states_info

    def get_best_taking_relation(self, next_states_info, best_relation, last_placed_chip):
        get_max_visited = (max(next_states_info, key=lambda x: x.times_visited)).times_visited
        visited_criteria = int(get_max_visited / 3) if int(get_max_visited / 3) > 0 else 1
        win_rate_criteria = 0.50
        best_states = []
        for state in next_states_info:
            state_win_rate = float(state.win_counter / state.times_visited)
            if state_win_rate >= win_rate_criteria and state.times_visited >= visited_criteria:
                best_states.append(state)
        if best_states:
            next_state = max(best_states, key=lambda x: float(x.win_counter / x.times_visited))
            best_relation = self.graph.find_taking_relation_info(self.current_state_info, next_state,
                                                                 last_placed_chip)
            return best_relation
        else:
            return best_relation

    @staticmethod
    def transform_combination(combination):
        transformed_combination = []
        for chip in combination:
            transformed_combination.append(chip.row)
            transformed_combination.append(chip.col)
            transformed_combination.append(chip.value)
        return transformed_combination

    # Placing action
    @staticmethod
    def convert_placing_action_to_board_values(action, game_board):
        game_board_copy = copy.deepcopy(game_board)
        game_board_copy.add_chip_rowcol(action.row, action.col, cp.Chip(action.value))
        return game_board_copy.board_to_chip_values()

    def convert_placing_actions(self, game_board):
        board_states = []
        for action in self.actions:
            values = self.convert_placing_action_to_board_values(action, game_board)
            board_states.append(values)
        return board_states

    # Taking action
    @staticmethod
    def convert_taking_action_to_board_values(game_board, combination, chip_placed_row, chip_placed_col):
        game_board_copy = copy.deepcopy(game_board)
        for chip in combination:
            # If it's the same chip that was placed this round, agent can't take it
            if chip_placed_row == chip.row and chip_placed_col == chip.col:
                continue
            game_board_copy.remove_chip(chip.row * game_board_copy.border_length + chip.col)
        return game_board_copy.board_to_chip_values()

    def convert_taking_actions(self, game_board, combinations, chip_placed_row, chip_placed_col):
        board_states = []
        for combination in combinations:
            values = self.convert_taking_action_to_board_values(game_board, combination,
                                                                chip_placed_row, chip_placed_col)
            board_states.append(values)
        return board_states

    def get_next_state_score_after_taking(self, game_board, combination, chip_placed_row, chip_placed_col):
        agent_score = self.score
        for chip in combination:
            game_board_copy = copy.deepcopy(game_board)
            # Tile where the chip belongs
            tile = game_board_copy.get_tile_at_index(chip.row * game_board_copy.border_length + chip.col)
            # if it's the same chip that was placed this round, player/agent can't take it
            if chip_placed_row == chip.row and chip_placed_col == chip.col:
                continue
            if tile.color == clr.Color.BLUE:
                agent_score += 2
            if tile.color == clr.Color.WHITE:
                agent_score += 1
        return agent_score

    @staticmethod
    def get_next_state_chips_left_after_taking(game_board, chips_counter, combination,
                                               chip_placed_row, chip_placed_col):
        chips_left = chips_counter
        for chip in combination:
            game_board_copy = copy.deepcopy(game_board)
            tile = game_board_copy.get_tile_at_index(chip.row * game_board_copy.border_length + chip.col)
            if chip_placed_row == chip.row and chip_placed_col == chip.col:
                continue
            if tile.color == clr.Color.RED:
                chips_left += 1
            if tile.color == clr.Color.BLUE:
                chips_left -= 1
        return chips_left
