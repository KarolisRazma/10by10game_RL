import src.utilities.constants3x3 as c3x3
from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.agents.improved_agent_learning.path import Path
from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData
from src.agents.random_walker_agent import RandomWalkerAgent
from src.environment import Environment
from src.game_components.action_data import ActionData
from src.game_components.chip import Chip
from src.game_components.container import Container
from src.game_components.game_result import GameResult
from src.game_components.state_data import StateData


class CustomEnvironment(Environment):
    def __init__(self, scoring_parameter, score_to_win, board=None, container=None, agent_1=None, agent_2=None):
        super().__init__(scoring_parameter, score_to_win, board, container, agent_1, agent_2, game_logger=None,
                         is_logger_silent=True)

        # This can be changed later on
        self.set_agent_2(RandomWalkerAgent("CustomEnvRandomAgent"))

        # noinspection PyTypeChecker
        self.starting_state_info: ImprovedAgentStateData = None

    def prepare_custom_game(self, starting_state_info: ImprovedAgentStateData, agent):
        self.last_placed_chip = None
        self.last_combination = None
        self.has_taking_action = False

        self.starting_state_info = starting_state_info

        # Prepare board
        # Assume that the board is already created
        self.board.from_board_values_to_board(starting_state_info.board_values)

        # Prepare container
        custom_container = Container(c3x3.chips_types, c3x3.chips_per_type)
        custom_container.custom_fill_container(starting_state_info.container_chips_values_list)
        self.set_container(custom_container)
        self.container.shuffle_container()

        # Prepare agent_1 (agent_2 is already set)
        self.set_agent_1(agent)
        self.set_agents_list()

        # Prepare agents
        self.agent_1.score = starting_state_info.my_score
        self.agent_2.score = starting_state_info.enemy_score

        self.agent_1.hand_chips = [Chip(starting_state_info.hand_chips_values_list[0]),
                                   Chip(starting_state_info.hand_chips_values_list[1])]
        self.agent_2.hand_chips = [Chip(starting_state_info.enemy_hand_chips_values_list[0]),
                                   Chip(starting_state_info.enemy_hand_chips_values_list[1])]

        self.agent_1.last_episode_path = Path()
        self.agent_1.last_episode_path.state_data_list.append(starting_state_info)
        self.agent_1.current_state_info = starting_state_info

    def get_first_and_second_turn_agents(self):
        first_turn_agent = self.agent_1 if self.starting_state_info.my_turn else self.agent_2
        second_turn_agent = self.agent_2 if self.starting_state_info.my_turn else self.agent_1
        return first_turn_agent, second_turn_agent

    def start_custom_game(self):
        turn = 0
        first_turn_agent, second_turn_agent = self.get_first_and_second_turn_agents()
        while True:
            # Get agent and enemy_agent (2.1)
            agent = first_turn_agent if turn == 0 else second_turn_agent
            enemy_agent = second_turn_agent if turn == 0 else first_turn_agent

            # Agent selects placing action (2.2)
            placing_action = agent.select_placing_action(game_board=self.board)

            # Execute selected placing action (2.3)
            self.make_placing_action(agent, placing_action)

            # Everything related to combinations happens here
            self.process_combinations(agent)

            # End round and check for ending flag
            ending_flag = self.round_ending(agent, enemy_agent)

            if ending_flag:
                break

            # Next agent's turn
            turn = 0 if turn == 1 else 1

    def get_custom_game_result(self, starting_state_info, agent):
        self.prepare_custom_game(starting_state_info, agent)
        self.start_custom_game()
        return self.agent_1.last_game_result

    def get_next_action_states_pairs_by_placing_action(self, state_data: ImprovedAgentStateData, placing_action):
        self.prepare_custom_game(state_data, self.agent_1)
        if state_data.my_turn:
            playing_agent = self.agent_1
        else:
            playing_agent = self.agent_2
        self.make_placing_action(playing_agent, placing_action)

        # Changes after placing
        board_values_after_placing = self.board.board_to_chip_values()
        playing_agent_hand_chips_values_after_placing = playing_agent.get_hand_chips_values_list()

        # Format [ [action, [state1, state2, ...]], [action, [state1, state2, ...]], ...]
        action_state_data_pair_list = []

        combinations = self.get_combinations(self.last_placed_chip)
        if not combinations:
            action_state_data_pair_list.append(
                self.get_next_action_states_pair(state_data, playing_agent,
                                                 playing_agent_hand_chips_values_after_placing)
            )
            return action_state_data_pair_list

            # Every combination should be executed
        for combination in combinations:
            # Reset before executing combination
            self.board.from_board_values_to_board(board_values_after_placing)
            playing_agent.score = state_data.my_score if state_data.my_turn else state_data.enemy_score
            self.container.clear()
            self.container.custom_fill_container(state_data.container_chips_values_list)

            # Execute
            self.has_taking_action = True
            self.last_combination = combination
            self.exec_taking_loop(playing_agent)

            container_values_after_taking = self.container.get_chips_values_list()
            action_state_data_pair_list \
                .append(self.get_next_action_states_pair(state_data, playing_agent,
                                                         playing_agent_hand_chips_values_after_placing,
                                                         container_values_after_taking))
        return action_state_data_pair_list

    def get_next_action_states_pair(self, state_data: ImprovedAgentStateData, playing_agent,
                                    playing_agent_hand_chips_values_after_placing,
                                    container_values_after_taking=None):
        action_state_data_pair = []
        next_action_data = ImprovedAgentActionData(
            row=self.last_placed_chip.row,
            col=self.last_placed_chip.col,
            chip_value=self.last_placed_chip.value,
            has_taking=self.has_taking_action,
            combination=self.last_combination
        )
        action_state_data_pair.append(next_action_data)

        next_state_data_list = []
        unique_container_chip_values = set(self.container.get_chips_values_list())

        # That means container is empty
        if not unique_container_chip_values:
            self.deal_with_endgame(self.is_endgame())
            next_state_data = ImprovedAgentStateData(
                board_values=self.board.board_to_chip_values(),
                my_turn=not state_data.my_turn,
                my_score=self.agent_1.score,
                enemy_score=self.agent_2.score,
                chips_left=len(self.container.chips),
                last_placed_chip_list=[self.last_placed_chip.row, self.last_placed_chip.col,
                                       self.last_placed_chip.value],
                hand_chips_values_list=self.agent_1.get_hand_chips_values_list(),
                enemy_hand_chips_values_list=self.agent_2.get_hand_chips_values_list(),
                container_chips_values_list=self.container.get_chips_values_list(),
                is_initial=False,
                is_final=True,
                game_result=self.agent_1.last_game_result
            )
            next_state_data_list.append(next_state_data)

        for unique_chip_value in unique_container_chip_values:
            playing_agent.hand_chips = [Chip(chip_value)
                                        for chip_value in playing_agent_hand_chips_values_after_placing]
            self.container.clear()
            if container_values_after_taking is not None:
                self.container.custom_fill_container(container_values_after_taking)
            else:
                self.container.custom_fill_container(state_data.container_chips_values_list)

            chip = self.container.draw_chip_with_exact_value(unique_chip_value)
            playing_agent.hand_chips.append(chip)

            # Check if its final state
            end_game_flag = self.is_endgame()
            if end_game_flag:
                self.deal_with_endgame(end_game_flag)
                game_result = self.agent_1.last_game_result
                is_final = True
            else:
                game_result = None
                is_final = False

            next_state_data = ImprovedAgentStateData(
                board_values=self.board.board_to_chip_values(),
                my_turn=not state_data.my_turn,
                my_score=self.agent_1.score,
                enemy_score=self.agent_2.score,
                chips_left=len(self.container.chips),
                last_placed_chip_list=[self.last_placed_chip.row, self.last_placed_chip.col,
                                       self.last_placed_chip.value],
                hand_chips_values_list=self.agent_1.get_hand_chips_values_list(),
                enemy_hand_chips_values_list=self.agent_2.get_hand_chips_values_list(),
                container_chips_values_list=self.container.get_chips_values_list(),
                is_initial=False,
                is_final=is_final,
                game_result=game_result
            )
            next_state_data_list.append(next_state_data)
        action_state_data_pair.append(next_state_data_list)
        return action_state_data_pair

    # Overriden method
    def round_ending(self, agent, enemy_agent):
        if len(self.container.chips) > 0:
            # Method from parent
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
                is_final=is_final
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
                is_final=is_final
            ),
            action_data=action_data
        )

        # Reset has_taking after round
        self.has_taking_action = False

        return is_final

    def deal_with_endgame(self, end_game_flag):
        if end_game_flag == 1:
            self.agents[0].last_game_result = GameResult.WON
            self.agents[1].last_game_result = GameResult.LOST
            return
        if end_game_flag == 2:
            self.agents[0].last_game_result = GameResult.LOST
            self.agents[1].last_game_result = GameResult.WON
            return
        if end_game_flag == 3:
            if self.agents[0].score < self.agents[1].score:
                self.agents[0].last_game_result = GameResult.WON
                self.agents[1].last_game_result = GameResult.LOST
                return
            elif self.agents[0].score > self.agents[1].score:
                self.agents[0].last_game_result = GameResult.LOST
                self.agents[1].last_game_result = GameResult.WON
                return
            else:
                self.agents[0].last_game_result = GameResult.DRAW
                self.agents[1].last_game_result = GameResult.DRAW
                return
