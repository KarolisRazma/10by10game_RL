import src.game_components.board as bd
import src.game_components.container as cr
import src.game_components.agent as at
import src.learning_algorithm_parts.graph as gh
import src.learning_algorithm_parts.vertex as vx
import src.utilities.util_funcs as util
import copy


class GraphGenerator:
    def __init__(self, board_length, container_cap, c_types, c_per_type):
        # Create initial board, container, agent, graph
        self.board = bd.Board(length=board_length)
        self.container = cr.Container(capacity=container_cap, chips_types=c_types, chips_per_type=c_per_type)
        self.agent = at.Agent(nickname="Generator", board_length=board_length)

        # TODO make graph more universal, atm its use is only for 3x3 board
        self.graph = gh.Graph(self.board.board_size)

    # simulate part of the environment
    # ------------------------------------
    # agent draws chips from container ->
    # snapshot (1) current board state ->
    # agent places chip on the board ->
    # snapshot (2) current board state ->
    # turn (2) board state into Vertex ->
    # check if graph contains recently made vertex ->
    # if true: add vertex to graph
    # if false: continue

    def simulate(self):
        self.setup_generator_env()
        while self.container.chips:
            if self.board.is_board_full():
                break

            # CAPTURE BOARD CURRENT LOOK
            parent_vertex_values = self.transform_board_to_vertex_values()

            # AGENT PLACES CHIP ON THE BOARD
            self.agent.get_actions_for_placing(self.board)  # get agent placing actions
            agent_action = self.agent.select_action_randomly()  # get which action agent wants to select
            row = agent_action.row
            col = agent_action.col
            chip_index = agent_action.chip_index
            selected_chip = self.agent.use_chip(chip_index)
            self.place_chip_on_board(selected_chip, row, col, self.board.border_length)

            # THE BOARD CHANGES
            child_vertex_values = self.transform_board_to_vertex_values()
            if not self.graph.is_vertex_found(vertex_values=child_vertex_values, is_silent=True):
                self.graph.append_vertex(parent_vertex_values=parent_vertex_values,
                                         child_vertex_values=child_vertex_values)

            # AGENT DRAWS CHIP FROM CONTAINER
            self.from_container_to_agent()

    def transform_board_to_vertex_values(self):
        board = copy.deepcopy(self.board)
        return [chip.value for chip in board.chips]

    def setup_generator_env(self):
        self.board.clear_chips()
        self.container.reset()
        self.agent.reset()
        self.from_container_to_agent()
        self.from_container_to_agent()

    # STANDARD WAY OF PLAYING
    # def place_first_chip(self):
    #     chip_index_in_container = util.get_random_index(list_len=len(self.container.chips))
    #     chip = self.container.draw_chip(index=chip_index_in_container)
    #     border_len = self.board.border_length
    #     self.place_chip_on_board(chip, int((border_len-1)/2), int((border_len-1)/2), border_len)

    def place_chip_on_board(self, chip, row, column, border_length):
        chip.row = row
        chip.col = column
        self.board.chips[row * border_length + column] = chip

    def from_container_to_agent(self):
        # get random index to drawing from container
        chip_index_in_container = util.get_random_index(list_len=len(self.container.chips))
        chip = self.container.draw_chip(index=chip_index_in_container)
        self.agent.chips.append(chip)
