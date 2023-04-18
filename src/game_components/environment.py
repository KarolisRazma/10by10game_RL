import copy
import random

from neo4j import GraphDatabase

import src.game_components.agent as ag
import src.game_components.board as board
import src.game_components.color as clr
import src.game_components.chip as cp
import src.game_components.container as container

import src.learning_algorithm_parts.state_info as sti

import src.utilities.constants3x3 as c3x3
import src.utilities.constants5x5 as c5x5
import src.utilities.logger as logger


class Environment:
    # @param board_length ==> one side length in number of tiles
    # @param container_capacity ==> how many chips container can contain at maximum
    # @param chips_types ==> list of chips values
    # @param chips_per_type ==> quantity of one type chips
    # @param scoring_parameter ==> sum of horizontally/vertically/diagonally arranged chips that enable agent to collect
    # @param score_to_win ==> total points to win a game for agent
    # @param db_name_1, db_name_2 ==> neoj4 database username, db for agents
    def __init__(self, board_length, container_capacity, chips_types, chips_per_type,
                 scoring_parameter, score_to_win, db_name_1, db_name_2):
        # Create board
        self.board = board.Board(length=board_length)

        # Current game state, same as board,
        # just converted into list of chip values
        self.environment_current_state = [0] * self.board.board_size

        # Create container
        self.container = container.Container(container_capacity, chips_types, chips_per_type)

        # Create agents
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "password"
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        session_agent_1 = driver.session(database=db_name_1)
        session_agent_2 = driver.session(database=db_name_2)

        agent1 = ag.Agent(game_board=self.board, nickname="[1] Brute Force Agent",
                          driver=driver, session=session_agent_1)
        agent2 = ag.Agent(game_board=self.board, nickname="[2] Brute Force Agent",
                          driver=driver, session=session_agent_2)
        self.agents = [agent1, agent2]

        # Draw initial chips, place initial chip on the board
        self.prepare_game()

        # Create instance of logger
        self.log = logger.Logger("logs.txt")

        # Count episodes played
        self.episodes = 0

        # Game state fields
        self.current_state_game_info = None
        self.current_state_game_info_agent_0 = None
        self.current_state_game_info_agent_1 = None
        self.next_state_game_info = None
        self.next_state_game_info_agent_0 = None
        self.next_state_game_info_agent_1 = None

        # Field to store next possible board states (board values, list of ints)
        self.next_states_board_values = None

        # Field to store last played chip in list [row, col, value]
        self.last_played_chip = None

        # Parameters
        self.scoring_parameter = scoring_parameter
        self.score_to_win = score_to_win
        if board_length == 3:
            self.diagonally_start_1 = c3x3.diagonally_start_1
            self.diagonally_end_1 = c3x3.diagonally_end_1
            self.diagonally_growth_1 = c3x3.diagonally_growth_1
            self.diagonally_start_2 = c3x3.diagonally_start_2
            self.diagonally_end_2 = c3x3.diagonally_end_2
            self.diagonally_growth_2 = c3x3.diagonally_growth_2
            self.vertically_start = c3x3.vertically_start
            self.vertically_end = c3x3.vertically_end
            self.vertically_growth = c3x3.vertically_growth
            self.horizontally_start = c3x3.horizontally_start
            self.horizontally_end = c3x3.horizontally_end
            self.horizontally_growth = c3x3.horizontally_growth
        if board_length == 5:
            self.diagonally_start_1 = c5x5.diagonally_start_1
            self.diagonally_end_1 = c5x5.diagonally_end_1
            self.diagonally_growth_1 = c5x5.diagonally_growth_1
            self.diagonally_start_2 = c5x5.diagonally_start_2
            self.diagonally_end_2 = c5x5.diagonally_end_2
            self.diagonally_growth_2 = c5x5.diagonally_growth_2
            self.vertically_start = c5x5.vertically_start
            self.vertically_end = c5x5.vertically_end
            self.vertically_growth = c5x5.vertically_growth
            self.horizontally_start = c5x5.horizontally_start
            self.horizontally_end = c5x5.horizontally_end
            self.horizontally_growth = c5x5.horizontally_growth

    def reset(self):
        self.board.clear_chips()  # remove all chips from the board
        self.container.reset()  # clear and refill the container
        self.agents[0].reset()  # agent 1 reset score/hand_chips/captured_chips
        self.agents[1].reset()  # agent 2 reset score/hand_chips/captured_chips
        self.prepare_game()  # game prep method (set initial chips, place first chip, etc)

    def prepare_game(self):
        # Set environment current state to root
        self.environment_current_state = [0] * self.board.board_size
        self.from_container_to_agent(0)
        self.from_container_to_agent(0)
        self.from_container_to_agent(1)
        self.from_container_to_agent(1)
        self.place_first_chip()
        # select starting player/agent randomly
        random.shuffle(self.agents)

    def from_container_to_agent(self, agent_index, is_captured=False):
        # get random index to drawing from container
        chip_index_in_container = self.get_random_index(len(self.container.chips))
        # append taken chip
        if not is_captured:
            self.agents[agent_index].chips.append(self.container.draw_chip(chip_index_in_container))
        else:
            self.agents[agent_index].captured_chips.append(self.container.draw_chip(chip_index_in_container))

    def place_first_chip(self):
        chip_index_in_container = self.get_random_index(len(self.container.chips))
        chip = self.container.draw_chip(chip_index_in_container)
        border_len = self.board.border_length
        self.place_chip_on_board(chip, int((border_len - 1) / 2), int((border_len - 1) / 2), border_len)

    def place_chip_on_board(self, chip, row, column, border_length):
        chip.row = row
        chip.col = column
        self.board.chips[row * border_length + column] = chip

    def get_combinations(self, chip_placed):
        combinations = []
        combinations += self.find_collectable_chips(self.diagonally_start_1,
                                                    self.diagonally_end_1,
                                                    self.diagonally_growth_1)
        combinations += self.find_collectable_chips(self.diagonally_start_2,
                                                    self.diagonally_end_2,
                                                    self.diagonally_growth_2)
        combinations += self.find_collectable_chips(self.vertically_start,
                                                    self.vertically_end,
                                                    self.vertically_growth)
        combinations += self.find_collectable_chips(self.horizontally_start,
                                                    self.horizontally_end,
                                                    self.horizontally_growth)

        # filter combinations (viable combinations are those, that contains placed chip)
        updated_combinations = []
        for combination in combinations:
            if chip_placed in combination:
                updated_combinations.append(combination)
        return updated_combinations

    def find_collectable_chips(self, indexes_start, indexes_end, index_growth):
        combinations = []
        for (index_start, index_end) in zip(indexes_start, indexes_end):
            chips_in_line = []
            sum_of_chips_values = 0
            while index_start <= index_end:
                # if tile is empty
                if self.board.is_tile_empty(index_start):
                    sum_of_chips_values = 0
                    chips_in_line = []
                    index_start += index_growth
                    continue
                # else: not empty
                else:
                    sum_of_chips_values += self.board.chips[index_start].value
                    chips_in_line.append(self.board.chips[index_start])
                # if sum reaches scoring parameter
                if sum_of_chips_values == self.scoring_parameter:
                    temp = chips_in_line.copy()
                    combinations.append(temp)
                    sum_of_chips_values -= chips_in_line[0].value
                    del chips_in_line[0]
                # if scoring parameter is stepped over
                if sum_of_chips_values > self.scoring_parameter:
                    # remove first chip in a line while sum is larger than parameter
                    while sum_of_chips_values > self.scoring_parameter:
                        sum_of_chips_values -= chips_in_line[0].value
                        del chips_in_line[0]
                    # prevent situations like this: 1 1 3 3 4
                    if sum_of_chips_values == self.scoring_parameter and index_start == index_end:
                        temp = chips_in_line.copy()
                        combinations.append(temp)
                index_start += index_growth
        return combinations

    def is_endgame(self):
        if self.agents[0].score >= self.score_to_win:
            return 1
        if self.agents[1].score >= self.score_to_win:
            return 2
        if self.agents[0].score < self.score_to_win and self.agents[1].score < self.score_to_win \
                and not self.container.chips:
            return 3
        return 0

    def deal_with_endgame(self, end_game_flag):
        self.log_endgame_info()
        # Increment episodes counter
        self.episodes += 1
        if end_game_flag == 1:
            self.agents[0].wins += 1
            self.agents[0].is_last_game_won = True
            self.agents[1].is_last_game_won = False
            return
        if end_game_flag == 2:
            self.agents[1].wins += 1
            self.agents[0].is_last_game_won = False
            self.agents[1].is_last_game_won = True
            return
        if end_game_flag == 3:
            if self.agents[0].score < self.agents[1].score:
                self.agents[0].wins += 1
                self.agents[0].is_last_game_won = True
                self.agents[1].is_last_game_won = False
                return
            if self.agents[0].score > self.agents[1].score:
                self.agents[1].wins += 1
                self.agents[0].is_last_game_won = False
                self.agents[1].is_last_game_won = True
                return
            else:
                self.agents[0].draws += 1
                self.agents[1].draws += 1
                self.agents[0].is_last_game_won = False
                self.agents[1].is_last_game_won = False
                return

    def log_after_taking(self):
        self.log.add_log("info", "--------------------------------------")
        self.log.add_log("info", "After taking chips from board:")
        self.log.add_log("info", self.board.board_to_string())
        self.log.add_log("info", "--------------------------------------")

    def log_after_placing(self):
        self.log.add_log("info", "--------------------------------------")
        self.log.add_log("info", "After placing chip:")
        self.log.add_log("info", self.board.board_to_string())
        self.log.add_log("info", "--------------------------------------")

    def log_turn_start(self, turn):
        self.log.add_log("info", "--------------------------------------")
        self.log.add_log("info", "Turn for agent" + self.agents[turn].id)
        self.log.add_log("info", self.board.board_to_string())
        self.log.add_log("info", "Chips left in container " + str(len(self.container.chips)))
        self.log.add_log("info", "--------------------------------------")

    def log_endgame_info(self):
        self.log.add_log("info", "game: {}".format(self.episodes))
        self.log.add_log("info", "agent: {} --- score: {}".format(self.agents[0].id, self.agents[0].score))
        self.log.add_log("info", "agent: {} --- score: {}".format(self.agents[1].id, self.agents[1].score))

    # -----------------------------------
    # All methods that are only used in main environment method

    def set_initial_state_in_db(self):
        # Set initial state (node in Neo4j)
        self.environment_current_state = self.board.board_to_chip_values()
        self.current_state_game_info_agent_0 = sti.StateInfo(board_values=self.environment_current_state,
                                                             my_turn=0, my_score=0, enemy_score=0,
                                                             chips_left=len(self.container.chips))
        self.current_state_game_info_agent_1 = sti.StateInfo(board_values=self.environment_current_state,
                                                             my_turn=1, my_score=0, enemy_score=0,
                                                             chips_left=len(self.container.chips))
        self.agents[0].graph.add_root(self.environment_current_state, self.current_state_game_info_agent_0)
        self.agents[1].graph.add_root(self.environment_current_state, self.current_state_game_info_agent_1)

        # Add state info to agent's paths
        self.agents[0].last_episode_path.state_info_list.append(self.current_state_game_info_agent_0)
        self.agents[1].last_episode_path.state_info_list.append(self.current_state_game_info_agent_1)

    def process_new_placing_actions(self, agent, turn):
        # Get agent's placing actions
        agent.get_actions_for_placing(self.board)

        # Get next board states from agent's placing actions
        self.next_states_board_values = agent.convert_placing_actions_to_board_states(self.board)

        # Try to add them to the database
        self.add_game_states_made_out_of_placing_actions_into_db(agent.actions, turn)

    def add_game_states_made_out_of_placing_actions_into_db(self, actions, turn):
        for (action, next_state_board_value) in zip(actions, self.next_states_board_values):
            # Construct game state info (board_values, my_turn, my_score, enemy_score, chips_left)
            if turn == 0:
                self.next_state_game_info_agent_0 = sti.StateInfo(board_values=next_state_board_value,
                                                                  my_turn=1, my_score=self.agents[0].score,
                                                                  enemy_score=self.agents[1].score,
                                                                  chips_left=len(self.container.chips) - 1)
                self.next_state_game_info_agent_1 = sti.StateInfo(board_values=next_state_board_value,
                                                                  my_turn=0, my_score=self.agents[1].score,
                                                                  enemy_score=self.agents[0].score,
                                                                  chips_left=len(self.container.chips) - 1)
            else:
                self.next_state_game_info_agent_0 = sti.StateInfo(board_values=next_state_board_value,
                                                                  my_turn=0, my_score=self.agents[0].score,
                                                                  enemy_score=self.agents[1].score,
                                                                  chips_left=len(self.container.chips) - 1)
                self.next_state_game_info_agent_1 = sti.StateInfo(board_values=next_state_board_value,
                                                                  my_turn=1, my_score=self.agents[1].score,
                                                                  enemy_score=self.agents[0].score,
                                                                  chips_left=len(self.container.chips) - 1)
            # Update every agent graph with next board states
            self.agents[0].graph.add_game_state(current_state_values=self.environment_current_state,
                                                next_state_values=next_state_board_value,
                                                action_type='placing', action=action,
                                                last_placed_chip=None,
                                                current_state_game_info=self.current_state_game_info_agent_0,
                                                next_state_game_info=self.next_state_game_info_agent_0)

            self.agents[1].graph.add_game_state(current_state_values=self.environment_current_state,
                                                next_state_values=next_state_board_value,
                                                action_type='placing', action=action,
                                                last_placed_chip=None,
                                                current_state_game_info=self.current_state_game_info_agent_1,
                                                next_state_game_info=self.next_state_game_info_agent_1)

    def get_placing_action(self, agent, turn):
        # Get current state of the game (StateInfo object)
        self.current_state_game_info = self.current_state_game_info_agent_0 if turn == 0 \
            else self.current_state_game_info_agent_1

        # Get nodes (StateInfo objects) from database accordingly to current state
        nodes = agent.graph.find_game_state_next_vertices(action_type='placing',
                                                          current_state_values=self.environment_current_state,
                                                          game_info=self.current_state_game_info)
        # Filter nodes (StateInfo objects) which agent can't do at this stage
        nodes = self.filter_nodes(nodes)

        # Do next node (StateInfo object) selection
        selected_node = self.select_next_node(nodes)

        # Store next state game info
        self.next_state_game_info = copy.deepcopy(selected_node)

        # Add next state info to agent's paths
        self.add_state_info_to_agents_paths(turn)

        # Get action which leads to selected node
        return self.get_action(agent, selected_node, action_type='placing', last_placed_chip=None)

    def filter_nodes(self, nodes):
        updated_nodes = []
        for node in nodes:
            # TODO not sure if this is the right way to filter
            if node.board_values in self.next_states_board_values:
                updated_nodes.append(node)
        return updated_nodes

    @staticmethod
    def select_next_node(nodes):
        # Select one node randomly (this selection should change in the future)
        random_index = random.randint(0, len(nodes) - 1)
        return nodes[random_index]

    def add_state_info_to_agents_paths(self, turn):
        # Add state info to agent's paths
        self.next_state_game_info_agent_0 = copy.deepcopy(self.next_state_game_info)
        self.next_state_game_info_agent_1 = copy.deepcopy(self.next_state_game_info)
        if turn == 0:
            self.next_state_game_info_agent_0.my_turn = 1
            self.next_state_game_info_agent_1.my_turn = 0
            self.next_state_game_info_agent_1.my_score, self.next_state_game_info_agent_1.enemy_score = \
                self.next_state_game_info_agent_1.enemy_score, self.next_state_game_info_agent_1.my_score
        else:
            self.next_state_game_info_agent_0.my_turn = 0
            self.next_state_game_info_agent_1.my_turn = 1
            self.next_state_game_info_agent_0.my_score, self.next_state_game_info_agent_0.enemy_score = \
                self.next_state_game_info_agent_0.enemy_score, self.next_state_game_info_agent_0.my_score
        self.agents[0].last_episode_path.state_info_list.append(self.next_state_game_info_agent_0)
        self.agents[1].last_episode_path.state_info_list.append(self.next_state_game_info_agent_1)

    def get_action(self, agent, selected_node, action_type, last_placed_chip):
        # Get action from this vertex
        return agent.graph.find_next_action(current_state_values=self.environment_current_state,
                                            next_state_values=selected_node.board_values, action_type=action_type,
                                            board=self.board, last_placed_chip=last_placed_chip,
                                            current_state_game_info=self.current_state_game_info,
                                            next_state_game_info=self.next_state_game_info)

    def make_placing_action(self, agent, placing_action):
        # Parse action into row/col/value
        row, col, value = self.parse_action(placing_action)

        # Updated last played chip by agent
        self.last_played_chip = [row, col, value]

        # Get which chip to use in agent hand
        chip_index = 0 if agent.chips[0].value == value else 1

        # Take chip from agent's hand
        selected_chip = agent.use_chip(chip_index)

        # Agent place one chip on the board
        self.place_chip_on_board(selected_chip, row, col, self.board.border_length)

        # Update environment state (board values)
        self.environment_current_state = self.board.board_to_chip_values()

    @staticmethod
    def parse_action(action):
        # Parse action into row/col/chip_index
        row = action.row
        col = action.col
        value = action.value
        return row, col, value

    def process_combinations(self, agent, turn):
        # Check if somehow there is value of constantsnxn.scoring_parameter on the board
        combinations = self.get_combinations(self.board.get_chip_at_index(self.last_played_chip[0]
                                                                          * self.board.border_length +
                                                                          self.last_played_chip[1]))
        # Agent takes these chips
        # Except the one placed this round
        if combinations:
            # If there's any combinations, update current state game info
            self.set_current_state_game_info(turn)

            # Process every possible new next state from current state (try to add it to database)
            self.process_new_taking_actions(agent, turn, combinations)

            # Get action for taking
            taking_action = self.get_taking_action(agent, turn)

            # Execute that action
            self.make_taking_action(taking_action, turn)

            # Log how changed the game after the action
            self.log_after_taking()

    def set_current_state_game_info(self, turn):
        self.current_state_game_info = copy.deepcopy(self.next_state_game_info)
        # Set individually for both agents
        self.current_state_game_info_agent_0 = copy.deepcopy(self.current_state_game_info)
        self.current_state_game_info_agent_1 = copy.deepcopy(self.current_state_game_info)
        if turn == 0:
            self.current_state_game_info_agent_0.my_turn = 1
            self.current_state_game_info_agent_1.my_turn = 0
            self.current_state_game_info_agent_1.my_score, self.current_state_game_info_agent_1.enemy_score = \
                self.current_state_game_info_agent_1.enemy_score, self.current_state_game_info_agent_1.my_score
        else:
            self.current_state_game_info_agent_0.my_turn = 0
            self.current_state_game_info_agent_1.my_turn = 1
            self.current_state_game_info_agent_0.my_score, self.current_state_game_info_agent_0.enemy_score = \
                self.current_state_game_info_agent_0.enemy_score, self.current_state_game_info_agent_0.my_score

    def process_new_taking_actions(self, agent, turn, combinations):
        # Get next board states from agent's taking actions
        self.next_states_board_values = agent.convert_taking_actions_to_board_states(self.board,
                                                                                     combinations,
                                                                                     self.last_played_chip[0],
                                                                                     self.last_played_chip[1])
        # Try to add them to the database
        self.add_game_states_made_out_of_taking_actions_into_db(agent, turn, combinations)

    def add_game_states_made_out_of_taking_actions_into_db(self, agent, turn, combinations):
        # Do taking actions on agent's instance copies
        # And update graph with next board states
        for (combination, next_state_board_values) in zip(combinations, self.next_states_board_values):
            agent_score = agent.get_next_state_score_after_taking(self.board, combination, self.last_played_chip[0],
                                                                  self.last_played_chip[1])
            chips_left = agent.get_next_state_chips_left_after_taking(self.board, len(self.container.chips) - 1,
                                                                      combination, self.last_played_chip[0],
                                                                      self.last_played_chip[1])
            # Construct game info (board_values, my_turn, my_score, enemy_score, chips_left)
            if turn == 0:
                self.next_state_game_info_agent_0 = sti.StateInfo(board_values=next_state_board_values,
                                                                  my_turn=1, my_score=agent_score,
                                                                  enemy_score=self.agents[1].score,
                                                                  chips_left=chips_left)
                self.next_state_game_info_agent_1 = sti.StateInfo(board_values=next_state_board_values,
                                                                  my_turn=0, my_score=self.agents[1].score,
                                                                  enemy_score=agent_score,
                                                                  chips_left=chips_left)
            else:
                self.next_state_game_info_agent_0 = sti.StateInfo(board_values=next_state_board_values,
                                                                  my_turn=0, my_score=self.agents[0].score,
                                                                  enemy_score=agent_score,
                                                                  chips_left=chips_left)
                self.next_state_game_info_agent_1 = sti.StateInfo(board_values=next_state_board_values,
                                                                  my_turn=1, my_score=agent_score,
                                                                  enemy_score=self.agents[0].score,
                                                                  chips_left=chips_left)

            self.agents[0].graph.add_game_state(current_state_values=self.environment_current_state,
                                                next_state_values=next_state_board_values,
                                                action_type='taking', action=combination,
                                                last_placed_chip=self.last_played_chip,
                                                current_state_game_info=self.current_state_game_info_agent_0,
                                                next_state_game_info=self.next_state_game_info_agent_0)

            self.agents[1].graph.add_game_state(current_state_values=self.environment_current_state,
                                                next_state_values=next_state_board_values,
                                                action_type='taking', action=combination,
                                                last_placed_chip=self.last_played_chip,
                                                current_state_game_info=self.current_state_game_info_agent_1,
                                                next_state_game_info=self.next_state_game_info_agent_1)

    def get_taking_action(self, agent, turn):
        # Get nodes from database
        nodes = agent.graph.find_game_state_next_vertices(action_type='taking',
                                                          current_state_values=self.environment_current_state,
                                                          game_info=self.current_state_game_info)
        # Filter nodes (StateInfo objects) which agent can't do at this stage
        nodes = self.filter_nodes(nodes)

        # Do next node (StateInfo object) selection
        selected_node = self.select_next_node(nodes)

        # Store next state game info
        self.next_state_game_info = copy.deepcopy(selected_node)

        # Add next state info to agent's paths
        self.add_state_info_to_agents_paths(turn)

        # Get action which leads to selected node
        return self.get_action(agent, selected_node, action_type='taking', last_placed_chip=self.last_played_chip)

    def make_taking_action(self, taking_action, turn):
        # Change value parameters_counter if more parametres are included in relationship NEXT_TAKING
        parameters_counter = 3
        time_iterate = int(len(taking_action) / parameters_counter)

        # Create combination from action
        selected_combination = []
        for i in range(time_iterate):
            com_chip = cp.Chip(taking_action[3 * i + 2])
            com_chip.row = taking_action[3 * i + 0]
            com_chip.col = taking_action[3 * i + 1]
            selected_combination.append(com_chip)

        self.exec_taking_loop(selected_combination, turn)

        # Update environment state (board values)
        self.environment_current_state = self.board.board_to_chip_values()

    def exec_taking_loop(self, selected_combination, turn):
        for chip in selected_combination:
            # Tile where the chip belongs
            tile = self.board.get_tile_at_index(chip.row * self.board.border_length + chip.col)

            # If it's the same chip that was placed this round, agent can't take it
            if self.last_played_chip[0] == chip.row and self.last_played_chip[1] == chip.col:
                continue

            # Return to container
            if tile.color == clr.Color.RED:
                self.container.chips.append(chip)
                self.board.remove_chip(chip.row * self.board.border_length + chip.col)

            # Take a chip from board
            # And collect one more from the container
            if tile.color == clr.Color.BLUE:
                # From board
                self.board.remove_chip(chip.row * self.board.border_length + chip.col)
                self.agents[turn].captured_chips.append(chip)
                self.agents[turn].score += 1
                # From container, do not forget to check if container has chips!
                # If container is not empty
                self.from_container_to_agent(turn, is_captured=True)
                self.agents[turn].score += 1
                # If container is empty
                if len(self.container.chips) == 0:
                    end_game_flag = self.is_endgame()
                    if end_game_flag > 0:
                        self.deal_with_endgame(end_game_flag)
                        break

            # Collect chip normally
            if tile.color == clr.Color.WHITE:
                # From board
                self.board.remove_chip(chip.row * self.board.border_length + chip.col)
                self.agents[turn].captured_chips.append(chip)
                self.agents[turn].score += 1

    def round_ending(self, turn):
        # Draw new chip from the container
        # This is related to drawing after taking chip from blue tile
        if len(self.container.chips) != 0:
            self.from_container_to_agent(turn)
        else:
            # Returning True --> it indicates, that game is ended and
            # Game ending method is already executed, so just break the game loop
            return True

        # In the end of the round
        # Check for end game conditions
        end_game_flag = self.is_endgame()
        if end_game_flag > 0:
            self.deal_with_endgame(end_game_flag)
            return True
        return False

    def start_episode(self):
        # Initial game settings
        turn = 0
        self.reset()

        # Sets initial state (node in Neo4j) and Adds state info to agent's paths
        self.set_initial_state_in_db()

        # Start game loop
        while True:
            # Log start of the turn
            self.log_turn_start(turn)

            # Take agent whose turn it is
            agent = self.agents[turn]

            # Process every possible new next state from current state (try to add it to database)
            self.process_new_placing_actions(agent, turn)

            # Get action for placing
            placing_action = self.get_placing_action(agent, turn)

            # Execute that action
            self.make_placing_action(agent, placing_action)

            # Log how changed the game after the action
            self.log_after_placing()

            # Process everything related with combination
            # (Finding new ones, selecting, executing combination)
            self.process_combinations(agent, turn)

            # Set new current state of the game
            self.set_current_state_game_info(turn)

            # End round and check for ending flag
            ending_flag = self.round_ending(turn)

            if ending_flag:
                break

            # Next agent's turn
            turn = 0 if turn == 1 else 1

    @staticmethod
    def get_random_index(list_len):
        return random.randint(0, list_len - 1)
