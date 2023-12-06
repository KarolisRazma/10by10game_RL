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

    def eval_path(self, graph: Graph, last_game_result: GameResult):

        # Process final state
        if not self.path.relation_data_list[-1].fully_explored:
            final_state_data = graph.find_or_create_final_state(self.path.state_data_list[-1])
            fixed_q_value = self.learning.final_state_reward(last_game_result)

        # Remove final state from the list
        self.path.state_data_list.pop()

        # Reverse path (states and relations)
        self.path.state_data_list.reverse()
        self.path.relation_data_list.reverse()

        is_first_step = True
        for (previous_state_data, relation_data) in zip(self.path.state_data_list, self.path.relation_data_list):
            # Only evaluate if states is not closed (or fully explored, just in other words)
            if not relation_data.fully_explored:
                # Handle previous->final state
                if is_first_step:
                    relation_data.q_value = fixed_q_value
                    graph.find_or_create_previous_state_and_make_next_relation(previous_state_data, relation_data,
                                                                               final_state_data, last_game_result)
                    current_state_data = previous_state_data
                    is_first_step = False
                    continue

                # Handle remaining states
                relation_data.q_value = self.learning.calc_new_q_value(graph, current_state_data, relation_data)
                graph.find_or_create_previous_state_and_make_next_relation(previous_state_data, relation_data,
                                                                           current_state_data, last_game_result)
                current_state_data = previous_state_data
