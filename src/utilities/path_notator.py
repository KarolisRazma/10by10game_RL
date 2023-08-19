import copy
import src.agents.improved_agent_learning.placing_relation_info as ipri
import src.agents.improved_agent_learning.taking_relation_info as itri

FILENAME_SIMPLE_AGENT_1 = "simpleagent1.log"
FILENAME_SIMPLE_AGENT_2 = "simpleagent2.log"
FILENAME_IMPROVED_AGENT_1 = "improvedagent1.log"
FILENAME_IMPROVED_AGENT_2 = "improvedagent2.log"
FILENAME_IMPROVED_AGENT_3 = "improvedagent3.log"
FILENAME_IMPROVED_AGENT_33 = "improvedagent33.log"
FILENAME_IMPROVED_AGENT_333 = "improvedagent333.log"
FILENAME_IMPROVED_AGENT_3333 = "improvedagent3333.log"

FILENAME_IMPROVED_AGENT_0303 = "ia0303.log"
FILENAME_IMPROVED_AGENT_0603 = "ia0603.log"
FILENAME_IMPROVED_AGENT_0903 = "ia0903.log"

FILENAME_IMPROVED_AGENT_0306 = "ia0306.log"
FILENAME_IMPROVED_AGENT_0606 = "ia0606.log"
FILENAME_IMPROVED_AGENT_0906 = "ia0906.log"

FILENAME_IMPROVED_AGENT_0309 = "ia0309.log"
FILENAME_IMPROVED_AGENT_0609 = "ia0609.log"
FILENAME_IMPROVED_AGENT_0909 = "ia0909.log"


SEPARATOR = "/"
NEXT_TAKING = "T"
NEXT_PLACING = "P"


def notate_path_simple(path):
    states = copy.deepcopy(path.state_info_list)
    # TODO collect relations

    state_counter = 1
    path_to_string = ""
    for state in states:
        board_values = ''.join(str(i) for i in state.board_values)
        my_turn = str(state.my_turn)
        my_score = str(state.my_score)
        enemy_score = str(state.enemy_score)
        chips_left = str(state.chips_left)
        state_value = str(format(state.state_value, '.4f'))

        state_to_string = str(state_counter) + "." + SEPARATOR + board_values + SEPARATOR + my_turn + SEPARATOR + \
                          my_score + SEPARATOR + enemy_score + SEPARATOR + chips_left + SEPARATOR + state_value + " "
        state_counter += 1
        path_to_string += state_to_string
    return path_to_string + '\n'


def notate_path_improved(path):
    # Take initial state
    state = path.state_info_list[0]

    # Do initial state
    board_values = ''.join(str(i) for i in state.board_values)
    my_turn = str(state.my_turn)
    my_score = str(state.my_score)
    enemy_score = str(state.enemy_score)
    chips_left = str(state.chips_left)

    times_visited = str(state.times_visited)
    win_counter = str(state.win_counter)
    lose_counter = str(state.lose_counter)
    draw_counter = str(state.draw_counter)
    is_initial_state = str(1) if state.is_initial_state else str(0)

    state_counter = 1
    state_to_string = str(state_counter) + "." + SEPARATOR + board_values + SEPARATOR + my_turn + SEPARATOR + \
                      my_score + SEPARATOR + enemy_score + SEPARATOR + chips_left + SEPARATOR + \
                      times_visited + SEPARATOR + win_counter + \
                      SEPARATOR + lose_counter + SEPARATOR + draw_counter + SEPARATOR + is_initial_state + " "

    state_counter += 1
    path_to_string = state_to_string

    # Remove initial state
    del path.state_info_list[0]

    states = copy.deepcopy(path.state_info_list)
    relations = copy.deepcopy(path.relation_info_list)
    for (state, relation) in zip(states, relations):
        # Do relation
        if isinstance(relation, ipri.PlacingRelationInfo):
            row = str(relation.row)
            col = str(relation.col)
            chip_value = str(relation.chip_value)
            q_value = str(format(relation.q_value, '.8f'))
            relation_to_string = NEXT_PLACING + SEPARATOR + row + SEPARATOR + col + SEPARATOR + chip_value + SEPARATOR \
                                 + q_value + " "
        elif isinstance(relation, itri.TakingRelationInfo):
            combination = ''.join(str(i) for i in relation.combination)
            last_placed_chip = ''.join(str(i) for i in relation.last_placed_chip)
            q_value = str(format(relation.q_value, '.8f'))
            relation_to_string = NEXT_TAKING + SEPARATOR + combination + SEPARATOR + last_placed_chip + SEPARATOR \
                                 + q_value + " "

        path_to_string += relation_to_string

        # Do state
        board_values = ''.join(str(i) for i in state.board_values)
        my_turn = str(state.my_turn)
        my_score = str(state.my_score)
        enemy_score = str(state.enemy_score)
        chips_left = str(state.chips_left)

        times_visited = str(state.times_visited)
        win_counter = str(state.win_counter)
        lose_counter = str(state.lose_counter)
        draw_counter = str(state.draw_counter)

        state_to_string = str(state_counter) + "." + SEPARATOR + board_values + SEPARATOR + my_turn + SEPARATOR + \
                          my_score + SEPARATOR + enemy_score + SEPARATOR + chips_left + SEPARATOR + \
                          times_visited + SEPARATOR + win_counter + \
                          SEPARATOR + lose_counter + SEPARATOR + draw_counter + " "
        state_counter += 1
        path_to_string += state_to_string
    return path_to_string + '\n'


def dump_pathstring_into_log(pathstring, filename):
    with open(filename, 'a') as file:
        # Dump pathstring into file
        file.writelines(pathstring)
