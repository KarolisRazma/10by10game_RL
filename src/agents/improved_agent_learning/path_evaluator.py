class PathEvaluator:
    # field path stores Path object
    def __init__(self, learning):
        self.path = None
        self.learning = learning

    # argument path is Path object
    def set_path(self, path):
        self.path = path

    # argument graph is Graph object
    # argument is_game_won is boolean type value
    def eval_path(self, graph, is_game_won, is_game_drawn):
        # Store path length and create step counter from the end
        path_length = len(self.path.state_info_list)
        step_counter = 1

        # From Path END -> To Path START
        while path_length != 0:
            state_info = self.path.state_info_list[path_length - 1]

            # Check fields that have varying value
            # state_value
            if state_info.state_value is None:
                state_info.state_value = 0.0

            # times_visited
            if state_info.times_visited is None:
                state_info.times_visited = 0

            # win_counter
            if state_info.win_counter is None:
                state_info.win_counter = 0

            # lose_counter
            if state_info.lose_counter is None:
                state_info.lose_counter = 0

            # draw_counter
            if state_info.draw_counter is None:
                state_info.draw_counter = 0

            # Calculate new value
            state_info.state_value = self.learning.calc_new_state_value(graph=graph, is_game_won=is_game_won,
                                                                        current_state_info=state_info,
                                                                        current_state_value=state_info.state_value,
                                                                        step_counter=step_counter,
                                                                        is_game_drawn=is_game_drawn)
            # Increment times_visited
            state_info.times_visited += 1
            # Increment win, lose or draw counter
            if is_game_won:
                state_info.win_counter += 1
            else:
                if is_game_drawn:
                    state_info.draw_counter += 1
                else:
                    state_info.lose_counter += 1

            # Update Graph
            graph.update_node_after_episode(state_info)

            # Decrease path len and increase step counter
            path_length -= 1
            step_counter += 1
