import copy
import random
import numpy as np
import src.agents.simple_agent_learning.path as ph
import src.agents.simple_agent_learning.path_evaluator as pe
import src.agents.simple_agent_learning.state_info as sti
import src.game_components.color as clr
import src.game_components.chip as cp
import src.agents.agent as ag


class SimpleAgent(ag.Agent):
    # @param nickname               --> agent's id
    # @param graph                  --> neoj4 graph
    # @param learning_algorithm     --> class RLearning object
    # @param explore_rate           --> probability of doing random action

    def __init__(self, nickname, graph, learning_algorithm, explore_rate):
        # Init Agent superclass
        super().__init__(nickname)

        # Graph stored in Neo4j
        self.graph = graph

        # Path evaluation field
        self.path_evaluator = pe.PathEvaluator(learning_algorithm)

        # Every move which happened in last episode stored here
        self.last_episode_path = ph.Path()

        # Flag to store last game result
        self.is_last_game_won = None

        # Fields for (current/next) (state info/board values), and store it into database
        self.next_states_board_values = None
        self.current_state_info = None
        self.next_state_info = None

        # Between 0 and 1 (float value) --> rate of choosing random/best next node
        # Random next node selection rate
        self.explore_rate = explore_rate
        # Best nexr node selection rate
        self.exploit_rate = float(1 - self.explore_rate)

        # List for agent behaviour selection
        self.behaviour = ["EXPLOIT", "EXPLORE"]

    # OVERRIDE
    # reset score/chips/captured_chips after episode is complete
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
        self.path_evaluator.eval_path(self.graph, self.is_last_game_won)

    # arguments:
    # initial_board_values --> list of chip values(int)
    # agent_number --> 0 if agent starts first, 1 if agent starts second
    # chips_left --> chips left in the container
    def set_initial_state_in_db(self, initial_board_values, chips_left):
        self.current_state_info = sti.StateInfo(board_values=initial_board_values, my_turn=self.agent_number,
                                                my_score=0, enemy_score=0, chips_left=chips_left)
        self.graph.add_root(initial_board_values, self.current_state_info)
        # With state_value property if is exists
        full_state_info = self.graph.find_game_state(self.current_state_info)
        self.current_state_info = full_state_info
        self.last_episode_path.state_info_list.append(full_state_info)

    # Process every possible new next state from current state (try to add it to database)
    def process_new_placing_actions(self, current_board_values, enemy_agent_score,
                                    chips_left_in_the_container, board):
        # Get agent's placing actions
        self.get_actions_for_placing(board)

        # Get next board states from agent's placing actions
        self.next_states_board_values = self.convert_placing_actions_to_board_states(board)

        # Try to add them to the database
        self.add_next_states_into_db(current_board_values, enemy_agent_score, chips_left_in_the_container,
                                     self.next_states_board_values, self.actions)

    def add_next_states_into_db(self, current_board_values, enemy_agent_score, chips_left_in_the_container,
                                next_states_board_values, actions):
        for (action, next_state_board_values) in zip(actions, next_states_board_values):
            # Construct game state info (board_values, my_turn, my_score, enemy_score, chips_left)
            self.next_state_info = sti.StateInfo(board_values=next_state_board_values, my_turn=1,
                                                 my_score=self.score, enemy_score=enemy_agent_score,
                                                 chips_left=chips_left_in_the_container - 1)
            # Update the agent's graph with next board states
            self.graph.add_game_state(current_state_values=current_board_values,
                                      next_state_values=next_state_board_values,
                                      action_type='placing', action=action,
                                      last_placed_chip=None,
                                      current_state_game_info=self.current_state_info,
                                      next_state_game_info=self.next_state_info)

    def select_placing_action(self, board, board_values):
        nodes = self.graph.find_game_state_next_vertices(action_type='placing',
                                                         current_state_values=board_values,
                                                         game_info=self.current_state_info)

        # Filter nodes (StateInfo objects) which agent can't do at this stage
        nodes = self.filter_nodes(nodes)

        # Do next node (StateInfo object) selection
        selected_node = self.select_next_node(nodes)

        # Store next state game info
        self.next_state_info = copy.deepcopy(selected_node)

        # Append it to the agent's path
        self.last_episode_path.state_info_list.append(self.next_state_info)

        # Get action which leads to selected node
        return self.get_action_from_next_node(board=board, board_values=board_values, selected_node=selected_node,
                                              action_type='placing', last_placed_chip=None)

    def filter_nodes(self, nodes):
        updated_nodes = []
        for node in nodes:
            if node.board_values in self.next_states_board_values:
                updated_nodes.append(node)
        return updated_nodes

    def select_next_node(self, nodes):
        # Do random choice for behaviour
        current_behaviour = np.random.choice(self.behaviour, 1, p=[self.exploit_rate, self.explore_rate])

        if current_behaviour == "EXPLORE":
            # VERY PRIMITIVE EXPLORING [BASELINE]
            random_index = random.randint(0, len(nodes) - 1)
            return nodes[random_index]

        if current_behaviour == "EXPLOIT":
            return self.find_max_value_node(nodes)

    @staticmethod
    def find_max_value_node(nodes):
        for node in nodes:
            if node.state_value is None:
                node.state_value = 0.0
        return max(nodes, key=lambda x: x.state_value)

    def get_action_from_next_node(self, board, board_values, selected_node, action_type, last_placed_chip):
        # Get action from this vertex
        return self.graph.find_next_action(current_state_values=board_values,
                                           next_state_values=selected_node.board_values, action_type=action_type,
                                           board=board, last_placed_chip=last_placed_chip,
                                           current_state_game_info=self.current_state_info,
                                           next_state_game_info=self.next_state_info)

    def add_enemy_made_action_to_agent_path(self, enemy_next_state_info):
        # Configure my next_state_info
        my_next_state_info = copy.deepcopy(enemy_next_state_info)
        my_next_state_info.my_turn = 0
        my_next_state_info.my_score, my_next_state_info.enemy_score = \
            enemy_next_state_info.enemy_score, enemy_next_state_info.my_score

        # Update next state info
        self.next_state_info = my_next_state_info
        # Append next state info to path
        self.last_episode_path.state_info_list.append(self.next_state_info)

    def set_current_state_info(self):
        self.current_state_info = copy.deepcopy(self.next_state_info)

    def process_new_taking_actions(self, board, board_values, last_played_chip, enemy_score, combinations, chips_left):
        # Get next board states from agent's taking actions
        self.next_states_board_values = self.convert_taking_actions_to_board_states(board, combinations,
                                                                                    last_played_chip[0],
                                                                                    last_played_chip[1])
        # Try to add them to the database
        self.add_next_taking_states_into_db(board, board_values, last_played_chip, chips_left, enemy_score,
                                            combinations, self.next_states_board_values)

    def add_next_taking_states_into_db(self, board, board_values, last_played_chip, chips_left, enemy_score,
                                       combinations, next_states_board_values):
        # Do taking actions on agent's instance copies
        # And update graph with next board states
        for (combination, next_state_board_values) in zip(combinations, next_states_board_values):
            agent_score = self.get_next_state_score_after_taking(board, combination, last_played_chip[0],
                                                                 last_played_chip[1])
            c_left = self.get_next_state_chips_left_after_taking(board, chips_left - 1,
                                                                 combination, last_played_chip[0],
                                                                 last_played_chip[1])
            # Construct game info (board_values, my_turn, my_score, enemy_score, chips_left)
            self.next_state_info = sti.StateInfo(board_values=next_state_board_values,
                                                 my_turn=1, my_score=agent_score,
                                                 enemy_score=enemy_score,
                                                 chips_left=c_left)

            self.graph.add_game_state(current_state_values=board_values,
                                      next_state_values=next_state_board_values,
                                      action_type='taking', action=combination,
                                      last_placed_chip=last_played_chip,
                                      current_state_game_info=self.current_state_info,
                                      next_state_game_info=self.next_state_info)

    def select_taking_action(self, board, board_values, last_played_chip):
        # Get nodes from database
        nodes = self.graph.find_game_state_next_vertices(action_type='taking',
                                                         current_state_values=board_values,
                                                         game_info=self.current_state_info)

        # Filter nodes (StateInfo objects) which agent can't do at this stage
        nodes = self.filter_nodes(nodes)

        # Do next node (StateInfo object) selection
        selected_node = self.select_next_node(nodes)

        # Store next state game info
        self.next_state_info = copy.deepcopy(selected_node)

        # Append it to the agent's path
        self.last_episode_path.state_info_list.append(self.next_state_info)

        # Get action which leads to selected node
        return self.get_action_from_next_node(board=board, board_values=board_values, selected_node=selected_node,
                                              action_type='taking', last_placed_chip=last_played_chip)

    # Placing action
    def convert_placing_actions_to_board_states(self, game_board):
        board_states = []
        for action in self.actions:
            game_board_copy = copy.deepcopy(game_board)
            game_board_copy.add_chip_rowcol(action.row, action.col, cp.Chip(action.value))
            board_states.append(game_board_copy.board_to_chip_values())
        return board_states

    # -------------------------------
    # Taking action related func
    # -------------------------------
    @staticmethod
    def convert_taking_actions_to_board_states(game_board, combinations, chip_placed_row, chip_placed_col):
        board_states = []
        for combination in combinations:
            game_board_copy = copy.deepcopy(game_board)
            for chip in combination:
                # If it's the same chip that was placed this round, agent can't take it
                if chip_placed_row == chip.row and chip_placed_col == chip.col:
                    continue
                game_board_copy.remove_chip(chip.row * game_board_copy.border_length + chip.col)
            board_states.append(game_board_copy.board_to_chip_values())
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
