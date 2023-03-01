import random
# import os
import Color
import Chip
import Board
import agent as a
import q_learning as q


class Environment:
    def __init__(self):
        self.qtable = q.QTable()

        # create board instance
        self.board = Board.Board()

        # create empty container
        self.container = []

        # brute force Agent
        self.agents = [a.Agent("[1] Brute Force Agent"), a.Agent("[2] Brute Force Agent")]
        self.draws = 0  # to count draws

        # set environment in initial position
        self.reset()

    def reset(self):
        self.board.clear_chips()
        self.container = []
        self.agents[0].reset()
        self.agents[1].reset()
        self.create_container()  # fill container
        self.initial_chips()  # players take 2 chips

        # place chip in the board's center
        index = self.select_randomly_from_container()
        self.place_chip_on_board(self.get_chip_from_container(index), 2, 2)
        self.remove_chip_from_container(index)

        # select starting player/agent randomly
        random.shuffle(self.agents)

    def start_episode(self):
        # define turn, 0 - player1, 1 - player2
        turn = 0
        self.reset()
        while True:
            # CLI display
            # os.system("clear")
            # print()
            # self.board.display()
            # self.display_score()
            # self.display_turn(turn)
            # self.display_user_chips(turn)
            # self.display_chips_left_in_container()

            # get index (of chip) and row/col

            # (brute force agent)
            agent = self.agents[turn]  # take agent whose turn it is
            agent.get_actions_for_placing(self.board)  # get agent placing actions
            agent_action = agent.select_action_randomly()  # get which action agent wants to select
            row = agent_action.row  # same as before in user interaction
            col = agent_action.col
            chip_index = agent_action.chip_index

            # self.qtable.initialise_q_values(self.board.make_copy(), agent_action)

            selected_chip = agent.use_chip(chip_index)  # take chip from player's/agent's hand

            self.place_chip_on_board(selected_chip, row, col)  # player/agent place one chip on the board

            combinations_of_ten = self.find_tens()  # check if somehow there is value of 10 on the board

            # player/agent takes these chips
            # except the one placed this round
            if combinations_of_ten:
                # CLI display
                # os.system("clear")
                # self.board.display()
                # self.display_combinations(combinations_of_ten)

                agent.get_actions_for_taking(combinations_of_ten)  # agent gets all actions for taking chips
                action = agent.select_action_randomly()             # selects randomly, returns index of action
                selected_combination = combinations_of_ten[action.combination_index]

                for chip in selected_combination:
                    # tile where the chip belongs
                    tile = self.board.get_tile_at_index(chip.get_row() * 5 + chip.get_col())

                    # if it's the same chip that was placed this round, player/agent can't take it
                    if row == chip.get_row() and col == chip.get_col():
                        continue

                    # return to container
                    if tile.get_color() == Color.Color.RED:
                        self.container.append(chip)
                        self.remove_chip_from_board(chip.get_row(), chip.get_col())

                    # take a chip from board
                    # and collect one more from the container
                    if tile.get_color() == Color.Color.BLUE:
                        # from board
                        self.remove_chip_from_board(chip.get_row(), chip.get_col())
                        self.agents[turn].captured_chips.append(chip)
                        self.agents[turn].score += 1
                        # from container, do not forget to check if container has chips!
                        # if container is not empty
                        random_index = self.select_randomly_from_container()
                        self.agents[turn].captured_chips.append(self.get_chip_from_container(random_index))
                        self.agents[turn].score += 1
                        self.remove_chip_from_container(random_index)
                        # if container is empty
                        if len(self.container) == 0:
                            # print("Container became empty while drawing after taking chip from blue tile")
                            end_game_flag = self.is_end_game()
                            if end_game_flag > 0:
                                self.deal_with_endgame(end_game_flag, turn)
                                break

                    # collect chip normally
                    if tile.get_color() == Color.Color.WHITE:
                        self.remove_chip_from_board(chip.get_row(), chip.get_col())
                        self.agents[turn].captured_chips.append(chip)
                        self.agents[turn].score += 1

            # draw new chip from the container
            # this if is related to drawing after taking chip from blue tile
            if len(self.container) != 0:
                index = self.select_randomly_from_container()
                self.draw_chip_from_container(index, turn)
                self.remove_chip_from_container(index)
            else:
                break

            # in the end of the round
            # check for end game conditions
            end_game_flag = self.is_end_game()
            if end_game_flag > 0:
                self.deal_with_endgame(end_game_flag, turn)
                break

            # next player's/agent's turn
            turn = 0 if turn == 1 else 1

    # game logic, finding rows of ten
    # find every possible line of value 10
    ##############################################
    def find_tens(self):
        combinations_of_ten = []

        # diagonally
        indexes_start = [0, 1, 2, 5, 10]
        indexes_end = [24, 19, 14, 23, 22]
        combinations_of_ten += self.find_chips_in_line(indexes_start, indexes_end, 6)

        indexes_start = [2, 3, 4, 9, 14]
        indexes_end = [10, 15, 20, 21, 22]
        combinations_of_ten += self.find_chips_in_line(indexes_start, indexes_end, 4)

        # vertically
        indexes_start = [0, 1, 2, 3, 4]
        indexes_end = [20, 21, 22, 23, 24]
        combinations_of_ten += self.find_chips_in_line(indexes_start, indexes_end, 5)

        # horizontally
        indexes_start = [0, 5, 10, 15, 20]
        indexes_end = [4, 9, 14, 19, 24]
        combinations_of_ten += self.find_chips_in_line(indexes_start, indexes_end, 1)
        return combinations_of_ten

    # find possible line of value 10 (diagonally or vertically or horizontally)
    def find_chips_in_line(self, indexes_start, indexes_end, index_growth):
        combinations_of_ten = []
        for (index_start, index_end) in zip(indexes_start, indexes_end):
            chips_in_line = []
            sum_of_chips_values = 0
            while index_start <= index_end:
                if self.board.is_tile_empty(index_start):
                    sum_of_chips_values = 0
                    chips_in_line = []
                    index_start += index_growth
                    continue
                else:
                    sum_of_chips_values += self.board.chips[index_start].get_value()
                    chips_in_line.append(self.board.chips[index_start])
                if sum_of_chips_values == 10:
                    temp = chips_in_line.copy()
                    combinations_of_ten.append(temp)
                    sum_of_chips_values -= chips_in_line[0].get_value()
                    del chips_in_line[0]
                if sum_of_chips_values > 10:
                    i = 0
                    while sum_of_chips_values > 10:
                        sum_of_chips_values -= chips_in_line[i].get_value()
                    # prevent situations like this: 1 1 3 3 4
                    if sum_of_chips_values == 10 and index_start == index_end:
                        temp = chips_in_line.copy()
                        combinations_of_ten.append(temp)
                    del chips_in_line[0]
                index_start += index_growth
        return combinations_of_ten

    ##############################################

    # testing methods (will be deleted later on)
    # user input, printing to screen methods
    ########################################

    @staticmethod
    def user_input():
        row_col_chip = input("Select row,col,chip: ")
        return row_col_chip

    def display_chips_left_in_container(self):
        print("Chips left in container: {}".format(len(self.container)))

    def display_user_chips(self, turn):
        chips = self.agents[turn].chips
        for (i, chip) in zip(range(len(chips)), chips):
            print("[{}]. Value: {}".format(i, chip.get_value()))

    def display_turn(self, turn):
        print("It's now {} turn".format(self.agents[turn].id))

    @staticmethod
    def display_combinations(combinations_of_ten):
        for (i, comb) in zip(range(len(combinations_of_ten)), combinations_of_ten):
            for chip in comb:
                print("[{}] Row: {}, Col: {}, Value: {}"
                      .format(i, chip.get_row() + 1, chip.get_col() + 1, chip.get_value()))

    def display_score(self):
        player1 = self.agents[0]
        player2 = self.agents[1]
        print("Player1: {} and score {}".format(player1.id, player1.score))
        print("Player2: {} and score {}".format(player2.id, player2.score))

    #############################

    # misc
    #############################
    def initial_chips(self):
        # player 1 picks 2 initial chips
        index = self.select_randomly_from_container()
        self.draw_chip_from_container(index, 0)
        self.remove_chip_from_container(index)
        index = self.select_randomly_from_container()
        self.draw_chip_from_container(index, 0)
        self.remove_chip_from_container(index)
        # player 2 picks 2 initial chips
        index = self.select_randomly_from_container()
        self.draw_chip_from_container(index, 1)
        self.remove_chip_from_container(index)
        index = self.select_randomly_from_container()
        self.draw_chip_from_container(index, 1)
        self.remove_chip_from_container(index)

    def is_end_game(self):
        if self.agents[0].score >= 10:
            return 1
        if self.agents[1].score >= 10:
            return 2
        if self.agents[0].score < 10 and self.agents[1].score < 10 and not self.container:
            return 3
        return 0

    def deal_with_endgame(self, end_game_flag, turn):
        # self.display_score()
        if end_game_flag == 1:
            # print("Player1: {} won".format(self.agents[turn].id))
            self.agents[turn].wins += 1
            return
        if end_game_flag == 2:
            # print("Player2: {} won".format(self.agents[turn].id))
            self.agents[turn].wins += 1
            return
        if end_game_flag == 3:
            if self.agents[0].score < self.agents[1].score:
                # print("Player1: {} won".format(self.agents[turn].id))
                self.agents[0].wins += 1
                return
            if self.agents[0].score > self.agents[1].score:
                # print("Player2: {} won".format(self.agents[turn].id))
                self.agents[1].wins += 1
                return
            else:
                # print("Draw")
                self.draws += 1
                return

    #############################

    # BOARD METHODS
    #############################
    # expected to get row and column already configured to be an index (row-- and column--)
    def place_chip_on_board(self, chip, row, column):
        chip.set_row(row)
        chip.set_col(column)
        self.board.chips[row * 5 + column] = chip

    # expected to get row and column already configured to be an index (row-- and column--)
    # removes chip from the board
    def remove_chip_from_board(self, row, column):
        self.board.chips[row * 5 + column] = None

    # expected to get row and column already configured to be an index (row-- and column--)
    def collect_chip_from_board(self, row, column, player_index):
        self.agents[player_index].captured_chips.append(self.board.chips[row * 5 + column])

    #############################

    # CONTAINER METHODS
    #############################
    def remove_chip_from_container(self, index):
        del self.container[index]

    # turn is current player's turn (to take chip from container or take actions)
    def draw_chip_from_container(self, index, turn):
        self.agents[turn].chips.append(self.container[index])

    # returns index
    def select_randomly_from_container(self):
        return random.randint(0, len(self.container) - 1)

    def get_chip_from_container(self, index):
        return self.container[index]

    def create_container(self):
        for i in range(28):
            if i < 7:
                self.container.append(Chip.Chip(1))
                continue
            if i < 14:
                self.container.append(Chip.Chip(2))
                continue
            if i < 21:
                self.container.append(Chip.Chip(3))
                continue
            self.container.append(Chip.Chip(4))
    #############################
