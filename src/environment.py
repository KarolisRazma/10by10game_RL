import random

from src.game_components.action_data import ActionData
# Components
from src.game_components.board import Board
from src.game_components.container import Container
from src.game_components.color import Color
from src.game_components.chip import Chip

# Utils
import src.utilities.constants3x3 as c3x3
from src.utilities.logger import Logger

from src.game_components.game_result import GameResult
from src.game_components.state_data import StateData


class Environment:
    def __init__(self, scoring_parameter, score_to_win, board=None, container=None,
                 agent_1=None, agent_2=None, game_logger=None, is_logger_silent=False):

        self.scoring_parameter = scoring_parameter
        self.score_to_win = score_to_win
        self.board: Board = board
        self.container: Container = container
        self.game_logger: Logger = game_logger
        self.is_logger_silent = is_logger_silent

        # Agents
        self.agent_1 = agent_1
        self.agent_2 = agent_2
        self.agents = []

        # Field to store last placed chip (Chip object)
        # noinspection PyTypeChecker
        self.last_placed_chip: Chip = None
        # noinspection PyTypeChecker
        self.last_combination: list[Chip] = None
        self.has_taking_action = False

        # Count episodes played
        self.episodes = 0

        # Taking constants
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

    def set_board(self, board: Board):
        self.board = board

    def set_container(self, container: Container):
        self.container = container

    def set_game_logger(self, game_logger: Logger):
        self.game_logger = game_logger

    def set_agent_1(self, agent_1):
        self.agent_1 = agent_1

    def set_agent_2(self, agent_2):
        self.agent_2 = agent_2

    def set_agents_list(self):
        self.clear_agents_list()
        if self.agent_1 is not None:
            self.agents.append(self.agent_1)
        if self.agent_2 is not None:
            self.agents.append(self.agent_2)

    def clear_agents_list(self):
        self.agents = []

    def reset(self):
        self.board.clear_chips()  # remove all chips from the board

        self.container.clear()
        self.container.fill_container()  # refill the container

        self.set_agents_list()
        random.shuffle(self.agents)  # select starting player/agent randomly
        self.agents[0].reset()  # agent 1 reset score/hand_chips/captured_chips
        self.agents[1].reset()  # agent 2 reset score/hand_chips/captured_chips

        self.prepare_game()  # game prep method (set initial chips, place first chip, etc)

    def prepare_game(self):
        self.from_container_to_agent(self.agent_1)
        self.from_container_to_agent(self.agent_1)
        self.from_container_to_agent(self.agent_2)
        self.from_container_to_agent(self.agent_2)
        self.place_first_chip()

    @staticmethod
    def get_random_index(list_len):
        return random.randint(0, list_len - 1)

    def from_container_to_agent(self, agent, is_captured=False):
        # get random index to drawing from container
        chip_index_in_container = self.get_random_index(len(self.container.chips))
        # append taken chip
        if not is_captured:
            agent.hand_chips.append(self.container.draw_chip(chip_index_in_container))
        else:
            agent.captured_chips.append(self.container.draw_chip(chip_index_in_container))

    def place_first_chip(self):
        chip_index_in_container = self.get_random_index(len(self.container.chips))
        chip = self.container.draw_chip(chip_index_in_container)
        border_len = self.board.border_length
        self.place_chip_on_board(chip, int((border_len - 1) / 2), int((border_len - 1) / 2), border_len)
        self.last_placed_chip = Chip(chip.value, chip.row, chip.col)

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
                # Create new chip objects, if combination is valid
                combination_copy = []
                for chip in combination:
                    combination_copy.append(Chip(chip.value, chip.row, chip.col))
                updated_combinations.append(combination_copy)
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
        if not self.container.chips:
            return 3
        return 0

    def deal_with_endgame(self, end_game_flag):
        if not self.is_logger_silent:
            self.log_endgame_info()
        # Increment episodes counter
        self.episodes += 1
        if end_game_flag == 1:
            self.agents[0].wins += 1
            self.agents[0].last_game_result = GameResult.WON
            self.agents[1].last_game_result = GameResult.LOST
            return
        if end_game_flag == 2:
            self.agents[1].wins += 1
            self.agents[0].last_game_result = GameResult.LOST
            self.agents[1].last_game_result = GameResult.WON
            return
        if end_game_flag == 3:
            if self.agents[0].score < self.agents[1].score:
                self.agents[0].wins += 1
                self.agents[0].last_game_result = GameResult.WON
                self.agents[1].last_game_result = GameResult.LOST
                return
            elif self.agents[0].score > self.agents[1].score:
                self.agents[1].wins += 1
                self.agents[0].last_game_result = GameResult.LOST
                self.agents[1].last_game_result = GameResult.WON
                return
            else:
                self.agents[0].draws += 1
                self.agents[1].draws += 1
                self.agents[0].last_game_result = GameResult.DRAW
                self.agents[1].last_game_result = GameResult.DRAW
                return

    def log_after_taking(self):
        self.game_logger.write("--------------------------------------")
        self.game_logger.write("After taking chips from board:")
        self.game_logger.write(self.board.board_to_string())
        self.game_logger.write("--------------------------------------")

    def log_after_placing(self):
        self.game_logger.write("--------------------------------------")
        self.game_logger.write("After placing chip:")
        self.game_logger.write(self.board.board_to_string())
        self.game_logger.write("--------------------------------------")

    def log_turn_start(self, turn):
        self.game_logger.write("--------------------------------------")
        self.game_logger.write("Turn for agent" + self.agents[turn].name)
        self.game_logger.write(self.board.board_to_string())
        self.game_logger.write("Chips left in container " + str(len(self.container.chips)))
        self.game_logger.write("--------------------------------------")

    def log_endgame_info(self):
        self.game_logger.write(f'game: {self.episodes}')
        self.game_logger.write(f'agent: {self.agents[0].name} --- score: {self.agents[0].score}')
        self.game_logger.write(f'agent: {self.agents[1].name} --- score: {self.agents[1].score}')

    def make_placing_action(self, agent, placing_action):
        # Parse action into row/col/value
        row, col, value = self.parse_action(placing_action)

        # Updated last played chip by agent
        self.last_placed_chip = Chip(value, row, col)

        # Get which chip to use in agent hand
        chip_index = 0 if agent.hand_chips[0].value == value else 1

        # Take chip from agent's hand
        selected_chip = agent.use_chip(chip_index)

        # Agent place one chip on the board
        self.place_chip_on_board(selected_chip, row, col, self.board.border_length)

    @staticmethod
    def parse_action(action):
        # Parse action into row/col/value
        row = action.row
        col = action.col
        value = action.value
        return row, col, value

    def process_combinations(self, agent):
        combinations = self.get_combinations(self.last_placed_chip)

        # Agent takes these chips
        # Except the one placed this round
        if combinations:
            self.has_taking_action = True

            # Sets taking_combination to [chip_1, chip_2, ... chip_n]
            self.last_combination = agent.select_taking_action(game_board=self.board, combinations=combinations)

            # Execute selected taking action
            self.exec_taking_loop(agent)

            # Log how changed the game after the action
            if not self.is_logger_silent:
                self.log_after_taking()
        else:
            self.last_combination = []

    def exec_taking_loop(self, agent):
        for chip in self.last_combination:
            # Tile where the chip belongs
            tile = self.board.get_tile_at_index(chip.row * self.board.border_length + chip.col)

            # If it's the same chip that was placed this round, agent can't take it
            if self.last_placed_chip.row == chip.row and self.last_placed_chip.col == chip.col:
                continue

            # Return to container
            if tile.color == Color.RED:
                removed_chip = self.board.remove_chip(chip.row * self.board.border_length + chip.col)
                self.container.chips.append(removed_chip)

            # Take a chip from board
            # And collect one more from the container
            if tile.color == Color.BLUE:
                # From board
                removed_chip = self.board.remove_chip(chip.row * self.board.border_length + chip.col)
                agent.captured_chips.append(removed_chip)
                agent.score += 1

                # If container is not empty
                if len(self.container.chips) > 0:
                    self.from_container_to_agent(agent, is_captured=True)
                agent.score += 1

            # Collect chip normally
            if tile.color == Color.WHITE:
                # From board
                removed_chip = self.board.remove_chip(chip.row * self.board.border_length + chip.col)
                agent.captured_chips.append(removed_chip)
                agent.score += 1

    def round_ending(self, agent, enemy_agent):
        # Draw new chip from the container (check if container is not empty)
        if len(self.container.chips) > 0:
            self.from_container_to_agent(agent)

        # In the end of the round, check for end game conditions
        end_game_flag = self.is_endgame()
        if end_game_flag > 0:
            self.deal_with_endgame(end_game_flag)
            is_final = True
        else:
            is_final = False

        action_data = ActionData(
            row=self.last_placed_chip.row,
            col=self.last_placed_chip.col,
            chip_value=self.last_placed_chip.value,
            has_taking=self.has_taking_action,
            combination=self.last_combination
        )
        agent.observe_state(
            state_data=StateData(
                board_values=self.board.board_to_chip_values(),
                my_turn=False,
                my_score=agent.score,
                enemy_score=enemy_agent.score,
                chips_left=len(self.container.chips),
                last_placed_chip_list=[self.last_placed_chip.row, self.last_placed_chip.col,
                                       self.last_placed_chip.value],
                hand_chips_values_list=agent.get_hand_chips_values_list(),
                enemy_hand_chips_values_list=enemy_agent.get_hand_chips_values_list(),
                container_chips_values_list=self.container.get_chips_values_list(),
                is_final=is_final,
            ),
            action_data=action_data
        )
        enemy_agent.observe_state(
            state_data=StateData(
                board_values=self.board.board_to_chip_values(),
                my_turn=True,
                my_score=enemy_agent.score,
                enemy_score=agent.score,
                chips_left=len(self.container.chips),
                last_placed_chip_list=[self.last_placed_chip.row, self.last_placed_chip.col,
                                       self.last_placed_chip.value],
                hand_chips_values_list=enemy_agent.get_hand_chips_values_list(),
                enemy_hand_chips_values_list=agent.get_hand_chips_values_list(),
                container_chips_values_list=self.container.get_chips_values_list(),
                is_final=is_final,
            ),
            action_data=action_data
        )

        # Reset has_taking after round
        self.has_taking_action = False

        return is_final

    def handle_initial_state_observing(self, first_agent, second_agent):
        first_agent.observe_state(state_data=StateData(
            board_values=self.board.board_to_chip_values(),
            my_turn=True,
            my_score=0,
            enemy_score=0,
            chips_left=len(self.container.chips),
            last_placed_chip_list=[self.last_placed_chip.row, self.last_placed_chip.col, self.last_placed_chip.value],
            hand_chips_values_list=first_agent.get_hand_chips_values_list(),
            enemy_hand_chips_values_list=second_agent.get_hand_chips_values_list(),
            container_chips_values_list=self.container.get_chips_values_list(),
            is_initial=True,
            is_final=False
        ))
        second_agent.observe_state(state_data=StateData(
            board_values=self.board.board_to_chip_values(),
            my_turn=False,
            my_score=0,
            enemy_score=0,
            chips_left=len(self.container.chips),
            last_placed_chip_list=[self.last_placed_chip.row, self.last_placed_chip.col, self.last_placed_chip.value],
            hand_chips_values_list=second_agent.get_hand_chips_values_list(),
            enemy_hand_chips_values_list=first_agent.get_hand_chips_values_list(),
            container_chips_values_list=self.container.get_chips_values_list(),
            is_initial=True,
            is_final=False
        ))

    def start_episode(self):
        # Initial game settings (1.1)
        turn = 0
        self.reset()

        # Store agents seperately for episode (1.2)
        agent_0, agent_1 = self.agents[0], self.agents[1]

        self.handle_initial_state_observing(first_agent=agent_0, second_agent=agent_1)

        # Game loop starts here (2)
        while True:

            if not self.is_logger_silent:
                self.log_turn_start(turn)

            # Get agent and enemy_agent (2.1)
            agent = agent_0 if turn == 0 else agent_1
            enemy_agent = agent_1 if turn == 0 else agent_0

            # agent selects placing action (2.2)
            placing_action = agent.select_placing_action(game_board=self.board)

            # Execute selected placing action (2.3)
            self.make_placing_action(agent, placing_action)

            # Log how the game changed after the action
            if not self.is_logger_silent:
                self.log_after_placing()

            # Everything related to combinations happens here
            self.process_combinations(agent)

            # End round and check for ending flag
            ending_flag = self.round_ending(agent, enemy_agent)

            if ending_flag:
                break

            # Next agent's turn
            turn = 0 if turn == 1 else 1
