import src.learning_algorithm_parts.learning as lg


class PathEvaluator:
    # field path stores Path object
    def __init__(self):
        self.path = None
        self.learning = lg.RLearning()

    # argument path is Path object
    def set_path(self, path):
        self.path = path

    # argument graph is Graph object
    # argument is_game_won is boolean type value
    def eval_path(self, graph, is_game_won):
        # Store path length and create step counter from the end
        path_length = len(self.path.state_info_list)
        step_counter = 1

        # From Path END -> To Path START
        while path_length != 0:
            state_info = self.path.state_info_list[path_length - 1]
            node = graph.find_game_state(state_info)

            # Store current state value in a var
            current_node_value = node['state_value']

            # Calculate new value
            new_node_value = self.learning.calc_new_state_value(graph=graph, is_game_won=is_game_won,
                                                                current_state_info=state_info,
                                                                current_state_value=current_node_value,
                                                                step_counter=step_counter)

            # Update Graph
            graph.update_state_value(new_node_value, state_info)

            # Decrease path len and increase step counter
            path_length -= 1
            step_counter += 1
