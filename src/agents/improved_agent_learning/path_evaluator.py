import time


class PathEvaluator:
    # field path stores Path object
    def __init__(self, learning):
        self.path = None
        self.learning = learning

        self.bench1 = []    # Update counters in DB
        self.bench2 = []    # Calculate Q-Value
        self.bench3 = []    # Update Q-Value in DB

    # argument path is Path object
    def set_path(self, path):
        self.path = path

    def eval_path(self, graph, is_game_won, is_game_drawn):
        # Reverse path (states and relations)
        self.path.state_info_list.reverse()
        self.path.relation_info_list.reverse()

        # Make relations the same length as states list
        self.path.relation_info_list.append(None)

        is_first_step = True
        for (state_info, relation_info) in zip(self.path.state_info_list, self.path.relation_info_list):
            # Increment counters
            state_info.times_visited += 1
            if is_game_won:
                state_info.win_counter += 1
            else:
                if is_game_drawn:
                    state_info.draw_counter += 1
                else:
                    state_info.lose_counter += 1

            if relation_info is not None:
                relation_info.q_value = self.learning.calc_new_q_value(graph=graph, state_info=state_info,
                                                                       relation_info=relation_info,
                                                                       is_final_state=is_first_step,
                                                                       is_game_won=is_game_won,
                                                                       is_game_drawn=is_game_drawn)
                graph.update_all(relation_info, state_info)
            else:
                graph.update_node_after_episode(state_info)

            # Set flag to false
            if is_first_step:
                is_first_step = False
