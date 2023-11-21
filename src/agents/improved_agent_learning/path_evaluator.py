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


    # # argument graph is Graph object
    # # argument is_game_won is boolean type value
    # def eval_path(self, graph, is_game_won, is_game_drawn):
    #     # Store states length (relation length is shorter by 1)
    #     # And create flag for first step
    #     states_length = len(self.path.state_info_list)
    #     relations_length = len(self.path.relation_info_list)
    #     is_first_step = True
    #
    #     while True:
    #         # From Path END -> To Path START
    #
    #         # End loop
    #         if states_length == 0:
    #             break
    #
    #         # States
    #         if states_length > 0:
    #             state_info = self.path.state_info_list[states_length - 1]
    #
    #             # times_visited
    #             if state_info.times_visited is None:
    #                 state_info.times_visited = 0
    #
    #             # win_counter
    #             if state_info.win_counter is None:
    #                 state_info.win_counter = 0
    #
    #             # lose_counter
    #             if state_info.lose_counter is None:
    #                 state_info.lose_counter = 0
    #
    #             # draw_counter
    #             if state_info.draw_counter is None:
    #                 state_info.draw_counter = 0
    #
    #             # Increment times_visited
    #             state_info.times_visited += 1
    #             # Increment win, lose or draw counter
    #             if is_game_won:
    #                 state_info.win_counter += 1
    #             else:
    #                 if is_game_drawn:
    #                     state_info.draw_counter += 1
    #                 else:
    #                     state_info.lose_counter += 1
    #
    #             # Update Graph
    #             start_timer = time.time()
    #             graph.update_node_after_episode(state_info)
    #             end_timer = time.time()
    #             self.bench1.append(end_timer - start_timer)
    #
    #         # Relations
    #         if relations_length > 0:
    #             relation_info = self.path.relation_info_list[relations_length - 1]
    #
    #             # q_value
    #             if relation_info.q_value is None:
    #                 relation_info.q_value = 0.0
    #
    #             start_timer = time.time()
    #             relation_info.q_value = self.learning.calc_new_q_value(graph=graph, state_info=state_info,
    #                                                                    relation_info=relation_info,
    #                                                                    is_final_state=is_first_step,
    #                                                                    is_game_won=is_game_won,
    #                                                                    is_game_drawn=is_game_drawn)
    #             end_timer = time.time()
    #             self.bench2.append(end_timer - start_timer)
    #
    #             # Update q-value
    #             start_timer = time.time()
    #             graph.set_q_value(self.path.state_info_list[states_length - 2], state_info, relation_info)
    #             end_timer = time.time()
    #             self.bench3.append(end_timer - start_timer)
    #
    #             # First step is over, set flag false
    #             if is_first_step:
    #                 is_first_step = False
    #
    #         # Decrease states/relation len and increase step counter
    #         states_length -= 1
    #         relations_length -= 1
