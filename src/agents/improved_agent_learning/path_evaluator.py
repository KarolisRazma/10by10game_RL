from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.learning import RLearning
from src.agents.improved_agent_learning.path import Path
from src.game_components.game_result import GameResult


class PathEvaluator:

    def __init__(self, learning: RLearning):
        # noinspection PyTypeChecker
        self.path: Path = None
        self.learning = learning

    # argument path is Path object
    def set_path(self, path):
        self.path = path

    def eval_path(self, graph: Graph, last_game_result: GameResult, state_closure_depth: int):

        # Trim path according to state_closure_depth
        to = len(self.path.state_data_list) + 1 - state_closure_depth
        self.path.state_data_list = self.path.state_data_list[:to]
        self.path.relation_data_list = self.path.relation_data_list[:(to-1)]

        # Process final state (if state is closed, then it should be already in the graph)
        if not self.path.state_data_list[-1].is_closed:
            graph.find_or_create_final_state(self.path.state_data_list[-1])

        # Remove final state from the list
        current_state_data = self.path.state_data_list.pop()

        # Reverse path (states and relations)
        self.path.state_data_list.reverse()
        self.path.relation_data_list.reverse()

        is_first_step = True
        for (previous_state_data, relation_data) in zip(self.path.state_data_list, self.path.relation_data_list):
            # Only evaluate if states is not closed
            if not previous_state_data.is_closed:
                if is_first_step:
                    relation_data.q_value = self.learning.final_state_reward(last_game_result)
                    graph.find_or_create_previous_state_and_make_next_relation(previous_state_data, relation_data,
                                                                               current_state_data, last_game_result,
                                                                               to_closed_state=True)
                    is_first_step = False
                else:
                    # Handle remaining states
                    relation_data.q_value = self.learning.calc_new_q_value(graph, current_state_data, relation_data)
                    graph.find_or_create_previous_state_and_make_next_relation(previous_state_data, relation_data,
                                                                               current_state_data, last_game_result)
            current_state_data = previous_state_data
