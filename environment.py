import agent as ag
import board
import color as clr
import constants3x3 as c3x3
import constants5x5 as c5x5
import container
import random
import logger


class Environment:
    # @param board_length ==> one side length in number of tiles
    # @param container_capacity ==> how many chips container can contain at maximum
    # @param chips_types ==> list of chips values
    # @param chips_per_type ==> quantity of one type chips
    # @param scoring_parameter ==> sum of horizontally/vertically/diagonally arranged chips that enable agent to collect
    # @param score_to_win ==> total points to win a game for agent
    def __init__(self, board_length, container_capacity, chips_types, chips_per_type, scoring_parameter, score_to_win):
        # create board
        self.board = board.Board(board_length) 

        # create container
        self.container = container.Container(container_capacity, chips_types, chips_per_type)

        # create agents
        self.agents = [ag.Agent("[1] Brute Force Agent"), ag.Agent("[2] Brute Force Agent")]

        # draw initial chips, place initial chip on the board
        self.prepare_game()

        # create instance of logger
        self.log = logger.Logger()

        # count episodes played
        self.episodes = 0

        # parameters
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
        self.prepare_game()

    def prepare_game(self):
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

    def place_first_chip(self, is_default=True):
        if is_default:
            chip_index_in_container = self.get_random_index(len(self.container.chips))
            chip = self.container.draw_chip(chip_index_in_container)
            border_len = self.board.border_length
            self.place_chip_on_board(chip, int((border_len-1)/2), int((border_len-1)/2), border_len)
        else:
            # TODO add manual first chip placement on the board
            return

    def place_chip_on_board(self, chip, row, column, border_length):
        chip.row = row
        chip.col = column
        self.board.chips[row * border_length + column] = chip

    def get_combinations(self):
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
        return combinations

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
        if self.agents[0].score < self.score_to_win and self.agents[1].score < self.score_to_win\
                and not self.container.chips:
            return 3
        return 0

    def deal_with_endgame(self, end_game_flag):
        self.log.add_log("info", "game: {}".format(self.episodes))
        self.log.add_log("info", "agent: {} --- score: {}".format(self.agents[0].id, self.agents[0].score))
        self.log.add_log("info", "agent: {} --- score: {}".format(self.agents[1].id, self.agents[1].score))

        # increment episodes counter
        self.episodes += 1
        if end_game_flag == 1:
            self.agents[0].wins += 1
            return
        if end_game_flag == 2:
            self.agents[1].wins += 1
            return
        if end_game_flag == 3:
            if self.agents[0].score < self.agents[1].score:
                self.agents[0].wins += 1
                return
            if self.agents[0].score > self.agents[1].score:
                self.agents[1].wins += 1
                return
            else:
                self.agents[0].draws += 1
                self.agents[1].draws += 1
                return

    def start_episode(self):
        turn = 0
        self.reset()
        while True:
            # get index (of chip) and row/col
            # (brute force agent)
            agent = self.agents[turn]  # take agent whose turn it is
            agent.get_actions_for_placing(self.board)  # get agent placing actions
            agent_action = agent.select_action_randomly()  # get which action agent wants to select
            row = agent_action.row
            col = agent_action.col
            chip_index = agent_action.chip_index

            # take chip from player's/agent's hand
            selected_chip = agent.use_chip(chip_index)
            # player/agent place one chip on the board
            self.place_chip_on_board(selected_chip, row, col, self.board.border_length)

            combinations = self.get_combinations()  # check if somehow there is value of 10 on the board

            # player/agent takes these chips
            # except the one placed this round
            if combinations:
                agent.get_actions_for_taking(combinations)  # agent gets all actions for taking chips
                action = agent.select_action_randomly()  # selects randomly, returns index of action
                selected_combination = combinations[action.combination_index]

                for chip in selected_combination:
                    # tile where the chip belongs
                    tile = self.board.get_tile_at_index(chip.row * self.board.border_length + chip.col)

                    # if it's the same chip that was placed this round, player/agent can't take it
                    if row == chip.row and col == chip.col:
                        continue

                    # return to container
                    if tile.color == clr.Color.RED:
                        self.container.chips.append(chip)
                        self.board.remove_chip(chip.row * self.board.border_length + chip.col)

                    # take a chip from board
                    # and collect one more from the container
                    if tile.color == clr.Color.BLUE:
                        # from board
                        self.board.remove_chip(chip.row * self.board.border_length + chip.col)
                        self.agents[turn].captured_chips.append(chip)
                        self.agents[turn].score += 1
                        # from container, do not forget to check if container has chips!
                        # if container is not empty
                        self.from_container_to_agent(turn, True)
                        self.agents[turn].score += 1
                        # if container is empty
                        if len(self.container.chips) == 0:
                            end_game_flag = self.is_endgame()
                            if end_game_flag > 0:
                                self.deal_with_endgame(end_game_flag)
                                break

                        # collect chip normally
                        if tile.color == clr.Color.WHITE:
                            self.from_container_to_agent(turn, True)
                            self.agents[turn].score += 1

            # draw new chip from the container
            # this if is related to drawing after taking chip from blue tile
            if len(self.container.chips) != 0:
                self.from_container_to_agent(turn)
            else:
                break

            # in the end of the round
            # check for end game conditions
            end_game_flag = self.is_endgame()
            if end_game_flag > 0:
                self.deal_with_endgame(end_game_flag)
                break

            # next player's/agent's turn
            turn = 0 if turn == 1 else 1

    @staticmethod
    def get_random_index(list_len):
        return random.randint(0, list_len - 1)
