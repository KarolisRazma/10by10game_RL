import copy
import random

import src.game_components.board as board
import src.game_components.color as clr
import src.game_components.chip as cp
import src.game_components.container as container
import src.agents.brute_force_agent as bfag
import src.agents.simple_agent as sag

import src.agents.simple_agent_learning.state_info as sti

import src.utilities.constants3x3 as c3x3
import src.utilities.constants5x5 as c5x5
import src.utilities.logger as logger


class Environment:
    # @param board_length ==> one side length in number of tiles
    # @param container_capacity ==> how many chips container can contain at maximum
    # @param chips_types ==> list of chips values
    # @param chips_per_type ==> quantity of one type chips
    # @param scoring_parameter ==> sum of horizontally/vertically/diagonally arranged chips that enable agent to collect

    def __init__(self, board_length, container_capacity, chips_types, chips_per_type,
                 scoring_parameter, score_to_win):
        # Create board
        self.board = board.Board(length=board_length)

        # Current game state, same as board,
        # just converted into list of chip values
        self.environment_board_values = [0] * self.board.board_size

        # Create container
        self.container = container.Container(container_capacity, chips_types, chips_per_type)

        # Store agents in a list
        self.agents = []

        # Create instance of logger
        self.log = logger.Logger("logs.txt")

        # Count episodes played
        self.episodes = 0

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

    # Append agent to self.agents list
    def set_agent(self, agent):
        if len(self.agents) < 2:
            self.agents.append(agent)

    # Clears agents list
    def clear_agents(self):
        self.agents = []

    def reset(self):
        self.board.clear_chips()  # remove all chips from the board
        self.container.reset()  # clear and refill the container
        self.agents[0].reset()  # agent 1 reset score/hand_chips/captured_chips
        self.agents[1].reset()  # agent 2 reset score/hand_chips/captured_chips
        self.prepare_game()  # game prep method (set initial chips, place first chip, etc)

    def prepare_game(self):
        # Set environment current state to root
        self.environment_board_values = [0] * self.board.board_size
        self.from_container_to_agent(0)
        self.from_container_to_agent(0)
        self.from_container_to_agent(1)
        self.from_container_to_agent(1)
        self.place_first_chip()
        # select starting player/agent randomly
        random.shuffle(self.agents)

    @staticmethod
    def get_random_index(list_len):
        return random.randint(0, list_len - 1)

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
        self.environment_board_values = self.board.board_to_chip_values()

    @staticmethod
    def parse_action(action):
        # Parse action into row/col/chip_index
        row = action.row
        col = action.col
        value = action.value
        return row, col, value

    def process_combinations(self, agent, enemy_agent, turn):
        # Check if somehow there is value of constantsnxn.scoring_parameter on the board
        combinations = self.get_combinations(self.board.get_chip_at_index(self.last_played_chip[0]
                                                                          * self.board.border_length +
                                                                          self.last_played_chip[1]))
        # Agent takes these chips
        # Except the one placed this round
        if combinations:
            # If there's any combinations, update current state info for both agents
            if isinstance(agent, sag.SimpleAgent):
                agent.set_current_state_info()
            if isinstance(enemy_agent, sag.SimpleAgent):
                enemy_agent.set_current_state_info()

            # If agent, whose turn is right now, is SimpleAgent, update graph with new taking actions
            if isinstance(agent, sag.SimpleAgent):
                chips_left = len(self.container.chips)
                agent.process_new_taking_actions(self.board, self.environment_board_values,
                                                 self.last_played_chip, enemy_agent.score, combinations, chips_left)

            # Get placing action if agent is BruteForceAgent
            if isinstance(agent, bfag.BruteForceAgent):
                agent.get_actions_for_taking(combinations)
                # TODO mistakes here, works now, but care later
                combination = combinations[agent.select_action().combination_index]
                updated_action = []
                for chip in combination:
                    updated_action.append(chip.row)
                    updated_action.append(chip.col)
                    updated_action.append(chip.value)
                taking_action = updated_action

            # Get placing action if agent is SimpleAgent
            if isinstance(agent, sag.SimpleAgent):
                taking_action = agent.select_taking_action(self.board, self.environment_board_values,
                                                           self.last_played_chip)

            # Save before executing placing action [for later use]
            previuos_board_values = copy.deepcopy(self.environment_board_values)
            # Executed selected taking action
            self.make_taking_action(agent, taking_action, turn)

            # If enemy agent is SimpleAgent type
            # Update enemy agent next state info
            # Add next state info to agent's paths
            if isinstance(enemy_agent, sag.SimpleAgent):
                # Before adding state, we need to acquire full state info (with state value)
                next_state_info_for_enemy = sti.StateInfo(board_values=self.environment_board_values, my_turn=0,
                                                          my_score=enemy_agent.score, enemy_score=agent.score,
                                                          chips_left=len(self.container.chips) - 1)

                # Create combination from action
                time_iterate = int(len(taking_action) / 3)
                combination = []
                for i in range(time_iterate):
                    com_chip = cp.Chip(taking_action[3 * i + 2])
                    com_chip.row = taking_action[3 * i + 0]
                    com_chip.col = taking_action[3 * i + 1]
                    combination.append(com_chip)

                # Update the enemy agent's graph with next board states
                enemy_agent.graph.add_game_state(current_state_values=previuos_board_values,
                                                 next_state_values=self.environment_board_values,
                                                 action_type='taking', action=combination,
                                                 last_placed_chip=self.last_played_chip,
                                                 current_state_game_info=enemy_agent.current_state_info,
                                                 next_state_game_info=next_state_info_for_enemy)

                # Update next state value
                enemy_agent.next_state_info = enemy_agent.graph.find_game_state(next_state_info_for_enemy)
                # Update path
                enemy_agent.last_episode_path.state_info_list.append(enemy_agent.next_state_info)

            # Log how changed the game after the action
            self.log_after_taking()

    def make_taking_action(self, agent, taking_action, turn):
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

        self.exec_taking_loop(selected_combination, agent, turn)

        # Update environment state (board values)
        self.environment_board_values = self.board.board_to_chip_values()

    def exec_taking_loop(self, selected_combination, agent, turn):
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
                agent.captured_chips.append(chip)
                agent.score += 1
                # From container, do not forget to check if container has chips!
                # If container is not empty
                self.from_container_to_agent(turn, is_captured=True)
                agent.score += 1
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
                agent.captured_chips.append(chip)
                agent.score += 1

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

        # Set initial environment board values
        self.environment_board_values = self.board.board_to_chip_values()

        # Store agents seperately for episode
        # And assign agent_numbers
        agent_0, agent_1 = self.agents[0], self.agents[1]
        agent_0.agent_number, agent_1.agent_number = 0, 1

        # Agent's deal with initial state of the game
        # If they are type of SimpleAgent, otherwise do nothing
        if isinstance(agent_0, sag.SimpleAgent):
            agent_0.set_initial_state_in_db(self.environment_board_values, chips_left=len(self.container.chips))
        if isinstance(agent_1, sag.SimpleAgent):
            agent_1.set_initial_state_in_db(self.environment_board_values, chips_left=len(self.container.chips))

        # Game loop starts here
        while True:
            # Log start of the turn
            self.log_turn_start(turn)

            # Get agent whose turn it is
            # Also get enemy agent
            agent = agent_0 if turn == 0 else agent_1
            enemy_agent = agent_1 if turn == 0 else agent_0

            # If agent is SimpleAgent, then
            # Process every possible new next state from current state (try to add it to database)
            if isinstance(agent, sag.SimpleAgent):
                agent.process_new_placing_actions(current_board_values=self.environment_board_values,
                                                  enemy_agent_score=enemy_agent.score, board=self.board,
                                                  chips_left_in_the_container=len(self.container.chips))

            # Get placing action if agent is BruteForceAgent
            if isinstance(agent, bfag.BruteForceAgent):
                agent.get_actions_for_placing(self.board)
                placing_action = agent.select_action()

            # Get placing action if agent is SimpleAgent
            if isinstance(agent, sag.SimpleAgent):
                placing_action = agent.select_placing_action(self.board, self.environment_board_values)

            # Save before executing placing action [for later use]
            previuos_board_values = copy.deepcopy(self.environment_board_values)
            # Executed selected placing action
            self.make_placing_action(agent, placing_action)

            # If enemy agent is SimpleAgent type
            # Update enemy agent next state info
            # Add next state info to agent's paths
            if isinstance(enemy_agent, sag.SimpleAgent):
                # Before adding state, we need to acquire full state info (with state value)
                next_state_info_for_enemy = sti.StateInfo(board_values=self.environment_board_values, my_turn=0,
                                                          my_score=enemy_agent.score, enemy_score=agent.score,
                                                          chips_left=len(self.container.chips) - 1)

                # Update the enemy agent's graph with next board states
                enemy_agent.graph.add_game_state(current_state_values=previuos_board_values,
                                                 next_state_values=self.environment_board_values,
                                                 action_type='placing', action=placing_action,
                                                 last_placed_chip=None,
                                                 current_state_game_info=enemy_agent.current_state_info,
                                                 next_state_game_info=next_state_info_for_enemy)

                # Update next state value
                enemy_agent.next_state_info = enemy_agent.graph.find_game_state(next_state_info_for_enemy)
                # Update path
                enemy_agent.last_episode_path.state_info_list.append(enemy_agent.next_state_info)

            # Log how the game changed after the action
            self.log_after_placing()

            # Everything related to combinations happens here
            self.process_combinations(agent, enemy_agent, turn)

            # Update current state info for both agents if they are SimpleAgent type agents
            if isinstance(agent, sag.SimpleAgent):
                agent.set_current_state_info()
            if isinstance(enemy_agent, sag.SimpleAgent):
                enemy_agent.set_current_state_info()

            # End round and check for ending flag
            ending_flag = self.round_ending(turn)

            if ending_flag:
                break

            # Next agent's turn
            turn = 0 if turn == 1 else 1
