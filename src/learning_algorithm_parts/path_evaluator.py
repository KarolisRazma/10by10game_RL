class PathEvaluator:
    # field path stores Path object
    def __init__(self):
        self.path = None

    # argument path is Path object
    def set_path(self, path):
        self.path = path

    # argument graph is Graph object
    def eval_path(self, graph):
        path_length = len(self.path.state_info_list)

        # From Path END -> To Path START
        while path_length != 0:
            state_info = self.path.state_info_list[path_length - 1]
            node = graph.find_game_state(state_info)

            # Store current state value in a var
            curr_node_value = node['state_value']

            # Calculate new value
            updated_node_value = curr_node_value + 0.5

            # Update Graph
            graph.update_state_value(updated_node_value, state_info)

            # Decrease path len
            path_length -= 1

