import copy

FILENAME_SIMPLE_AGENT_1 = "simpleagent1.log"
FILENAME_SIMPLE_AGENT_2 = "simpleagent2.log"
FILENAME_IMPROVED_AGENT_1 = "improvedagent1.log"
FILENAME_IMPROVED_AGENT_2 = "improvedagent2.log"

SEPARATOR = "/"


def notate_path_simple(path):
    states = copy.deepcopy(path.state_info_list)
    states.reverse()
    state_counter = 1
    path_to_string = ""
    for state in states:
        board_values = ''.join(str(i) for i in state.board_values)
        my_turn = str(state.my_turn)
        my_score = str(state.my_score)
        enemy_score = str(state.enemy_score)
        chips_left = str(state.chips_left)
        state_value = str(state.state_value)

        state_to_string = str(state_counter) + "." + SEPARATOR + board_values + SEPARATOR + my_turn + SEPARATOR + \
                          my_score + SEPARATOR + enemy_score + SEPARATOR + chips_left + SEPARATOR + state_value + " "
        state_counter += 1
        path_to_string += state_to_string
    return path_to_string


def notate_path_improved(path):
    states = copy.deepcopy(path.state_info_list)
    states.reverse()
    state_counter = 1
    path_to_string = ""
    for state in states:
        board_values = ''.join(str(i) for i in state.board_values)
        my_turn = str(state.my_turn)
        my_score = str(state.my_score)
        enemy_score = str(state.enemy_score)
        chips_left = str(state.chips_left)
        state_value = str(state.state_value)
        times_visited = str(state.times_visited)
        win_counter = str(state.win_counter)
        lose_counter = str(state.lose_counter)
        draw_counter = str(state.draw_counter)

        state_to_string = str(state_counter) + "." + SEPARATOR + board_values + SEPARATOR + my_turn + SEPARATOR + \
                          my_score + SEPARATOR + enemy_score + SEPARATOR + chips_left + SEPARATOR + state_value + \
                          SEPARATOR + times_visited + SEPARATOR + win_counter + \
                          SEPARATOR + lose_counter + SEPARATOR + draw_counter + " "
        state_counter += 1
        path_to_string += state_to_string
    return path_to_string


def dump_pathstring_into_log(pathstring, filename):
    with open(filename, 'a') as file:
        # Dump pathstring into file
        file.writelines(pathstring)
