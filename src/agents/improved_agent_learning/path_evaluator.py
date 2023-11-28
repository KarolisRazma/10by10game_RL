from src.game_components.game_result import GameResult


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

    def eval_path(self, graph, last_game_result):
        # Reverse path (states and relations)
        self.path.state_info_list.reverse()
        self.path.relation_info_list.reverse()

        # Make relations the same length as states list
        self.path.relation_info_list.append(None)

        is_first_step = True
        for (state_info, relation_info) in zip(self.path.state_info_list, self.path.relation_info_list):
            # Only evaluate if state is not closed (already decided win)
            if not state_info.is_closed:
                # Increment counters
                state_info.times_visited += 1
                if last_game_result == GameResult.WON:
                    state_info.win_counter += 1
                elif last_game_result == GameResult.LOST:
                    state_info.lose_counter += 1
                elif last_game_result == GameResult.DRAW:
                    state_info.draw_counter += 1

                if relation_info is not None:
                    relation_info.q_value = self.learning.calc_new_q_value(graph=graph, state_info=state_info,
                                                                           relation_info=relation_info,
                                                                           is_final_state=is_first_step,
                                                                           last_game_result=last_game_result)
                    graph.update_q_value_and_counters(relation_info, state_info)
                else:
                    graph.update_counters(state_info)

                # Set flag to false
                if is_first_step:
                    is_first_step = False
