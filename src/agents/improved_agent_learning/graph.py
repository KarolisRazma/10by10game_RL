import src.agents.improved_agent_learning.state_info as sti
import src.agents.improved_agent_learning.placing_relation_info as pri
import src.agents.improved_agent_learning.taking_relation_info as tri
import src.agents.improved_agent_learning.queries as QUERIES
import src.game_components.chip as cp
import time


# Structure of the graph
#
# node GameState:
#   property: board_values
#   property: my_turn
#   property: my_score
#   property: enemy_score
#   property: chips_left
#   property: times_visited
#   property: win_counter
#   property: lose_counter
#   property: draw_counter
#   property: initial_state
#   property: is_closed
#   property: hand_chips_values
#   property: last_placed_chip [row, col, value]
#
# relation NEXT_PLACING:
#   property: row
#   property: col
#   property: chip_value
#   property: q-value
#
# relation NEXT_TAKING
#   property: combination [row, col, value]
#   property: q-value


class Graph:
    def __init__(self, session):
        self.session = session

        self.bench1 = []  # Add game state
        self.bench2 = []  # Create next node and make placing rel
        self.bench3 = []  # Create next node and make taking rel
        self.bench4 = []  # Update node counters
        self.bench5 = []  # Find next placing action
        self.bench6 = []  # Find next taking action
        self.bench7 = []  # Find game state
        self.bench8 = []  # Find next game states
        self.bench9 = []  # Update Q-Value
        self.bench10 = []  # Find placing relation info
        self.bench11 = []  # Find taking relation info
        self.bench12 = []  # Find game state next relations
        self.bench13 = []  # Find next state by placing relation
        self.bench14 = []  # Find next state by taking relation
        self.bench15 = []  # Find max next state q-value (All time)
        self.bench16 = []  # Find max next state q-value (Placing)
        self.bench17 = []  # Find max next state q-value (Taking)
        self.bench18 = []  # Find max next state q-value (max function)
        self.bench19 = []  # Make state info from record
        self.bench20 = []  # Make placing relation info from record
        self.bench21 = []  # Make taking relation info from record

    # Delete entire db
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)

    def add_initial_game_state(self, state_info: sti.StateInfo):
        params = {
            "b_v": state_info.board_values,
            "m_t": state_info.my_turn,
            "m_s": state_info.my_score,
            "e_s": state_info.enemy_score,
            "c_l": state_info.chips_left,
            "i_i_s": state_info.is_initial_state,
            "hand_chips_values": state_info.hand_chips_values,
            "last_placed_chip": state_info.last_placed_chip,
        }
        start_timer = time.time()
        result = self.session.run(QUERIES.ADD_INITIAL_GAME_STATE, **params)
        end_timer = time.time()
        self.bench1.append(end_timer - start_timer)

        # Simplify dict
        record = result.single(strict=True).data()['g']
        return self.make_state_info_from_record(record)

    # @argument current_state_info          --> StateInfo object
    # @argument next_state_info             --> StateInfo object
    # @argument action                      --> list of ints [row, col, chip_value]
    def create_next_node_and_make_placing_relation(self, current_state_info, next_state_info, action):
        start_timer = time.time()
        params = {
            "c_board_values": current_state_info.board_values,
            "c_turn": current_state_info.my_turn,
            "c_my_score": current_state_info.my_score,
            "c_enemy_score": current_state_info.enemy_score,
            "c_chips_left": current_state_info.chips_left,
            "c_hand_chips_values": current_state_info.hand_chips_values,
            "c_last_placed_chip": current_state_info.last_placed_chip,
            "n_board_values": next_state_info.board_values,
            "n_turn": next_state_info.my_turn,
            "n_my_score": next_state_info.my_score,
            "n_enemy_score": next_state_info.enemy_score,
            "n_chips_left": next_state_info.chips_left,
            "n_initial_state": next_state_info.is_initial_state,
            "n_hand_chips_values": next_state_info.hand_chips_values,
            "n_last_placed_chip": next_state_info.last_placed_chip,
            "row": action.row,
            "col": action.col,
            "value": action.value
        }
        result = self.session.run(QUERIES.CREATE_NEXT_NODE_AND_MAKE_PLACING_RELATION, **params)
        end_timer = time.time()
        self.bench2.append(end_timer - start_timer)

        record = next(result)
        next_node = record["next"]
        rel = record["rel"]
        next_node_properties = next_node._properties
        rel_properties = rel._properties

        state_info = self.make_state_info_from_record(next_node_properties)
        placing_relation_info = self.make_placing_relation_info_from_record(rel_properties)
        return state_info, placing_relation_info

    # @argument current_state_info          --> StateInfo object
    # @argument next_state_info             --> StateInfo object
    # @argument action                      --> list of Chip objects
    # @argument last_placed_chip            --> list of ints [row, col, value]
    def create_next_node_and_make_taking_relation(self, current_state_info, next_state_info, combination):
        start_timer = time.time()
        updated_action = []
        for chip in combination:
            updated_action.append(chip.row)
            updated_action.append(chip.col)
            updated_action.append(chip.value)
        params = {
            "c_board_values": current_state_info.board_values,
            "c_turn": current_state_info.my_turn,
            "c_my_score": current_state_info.my_score,
            "c_enemy_score": current_state_info.enemy_score,
            "c_chips_left": current_state_info.chips_left,
            "c_hand_chips_values": current_state_info.hand_chips_values,
            "c_last_placed_chip": current_state_info.last_placed_chip,
            "n_board_values": next_state_info.board_values,
            "n_turn": next_state_info.my_turn,
            "n_my_score": next_state_info.my_score,
            "n_enemy_score": next_state_info.enemy_score,
            "n_chips_left": next_state_info.chips_left,
            "n_initial_state": next_state_info.is_initial_state,
            "n_hand_chips_values": next_state_info.hand_chips_values,
            "n_last_placed_chip": next_state_info.last_placed_chip,
            "combination": updated_action
        }
        result = self.session.run(QUERIES.CREATE_NEXT_NODE_AND_MAKE_TAKING_RELATION, **params)
        end_timer = time.time()
        self.bench3.append(end_timer - start_timer)

        record = next(result)
        next_node = record["next"]
        rel = record["rel"]
        next_node_properties = next_node._properties
        rel_properties = rel._properties

        state_info = self.make_state_info_from_record(next_node_properties)
        taking_relation_info = self.make_taking_relation_info_from_record(rel_properties)
        return state_info, taking_relation_info

    # It updates counters
    def update_counters(self, state_info):
        start_timer = time.time()
        params = {
            "board_values": state_info.board_values,
            "turn": state_info.my_turn,
            "my_score": state_info.my_score,
            "enemy_score": state_info.enemy_score,
            "chips_left": state_info.chips_left,
            "hand_chips_values": state_info.hand_chips_values,
            "last_placed_chip": state_info.last_placed_chip,
            "times_visited": state_info.times_visited,
            "win_counter": state_info.win_counter,
            "lose_counter": state_info.lose_counter,
            "draw_counter": state_info.draw_counter
        }
        self.session.run(QUERIES.UPDATE_COUNTERS, **params)
        end_timer = time.time()
        self.bench4.append(end_timer - start_timer)

    def update_q_value_and_counters(self, relation_info, next_state_info):
        params = {
            "n_board_values": next_state_info.board_values,
            "n_turn": next_state_info.my_turn,
            "n_my_score": next_state_info.my_score,
            "n_enemy_score": next_state_info.enemy_score,
            "n_chips_left": next_state_info.chips_left,
            "n_hand_chips_values": next_state_info.hand_chips_values,
            "n_last_placed_chip": next_state_info.last_placed_chip,
            "qvalue": relation_info.q_value,
            "times_visited": next_state_info.times_visited,
            "win_counter": next_state_info.win_counter,
            "lose_counter": next_state_info.lose_counter,
            "draw_counter": next_state_info.draw_counter
        }
        if isinstance(relation_info, pri.PlacingRelationInfo):
            params["row"] = relation_info.row
            params["col"] = relation_info.col
            params["chip_value"] = relation_info.chip_value
            self.session.run(QUERIES.UPDATE_Q_VALUE_AND_COUNTERS_PLACING, **params)
        elif isinstance(relation_info, tri.TakingRelationInfo):
            converted_combination = []
            for chip in relation_info.combination:
                converted_combination.append(chip.row)
                converted_combination.append(chip.col)
                converted_combination.append(chip.value)
            params["combination"] = converted_combination
            self.session.run(QUERIES.UPDATE_Q_VALUE_AND_COUNTERS_TAKING, **params)

    def find_placing_relation_info(self, current_state_info, next_state_info):
        start_timer = time.time()
        params = {
            "c_board_values": current_state_info.board_values,
            "c_turn": current_state_info.my_turn,
            "c_my_score": current_state_info.my_score,
            "c_enemy_score": current_state_info.enemy_score,
            "c_chips_left": current_state_info.chips_left,
            "c_hand_chips_values": current_state_info.hand_chips_values,
            "c_last_placed_chip": current_state_info.last_placed_chip,
            "n_board_values": next_state_info.board_values,
            "n_turn": next_state_info.my_turn,
            "n_my_score": next_state_info.my_score,
            "n_enemy_score": next_state_info.enemy_score,
            "n_chips_left": next_state_info.chips_left,
            "n_hand_chips_values": next_state_info.hand_chips_values,
            "n_last_placed_chip": next_state_info.last_placed_chip
        }
        result = self.session.run(QUERIES.FIND_PLACING_RELATION_INFO, **params)
        end_timer = time.time()
        self.bench10.append(end_timer - start_timer)

        record = next(result)
        rel_properties = record["r"]._properties
        return self.make_placing_relation_info_from_record(rel_properties)

    def find_taking_relation_info(self, current_state_info, next_state_info):
        start_timer = time.time()
        params = {
            "c_board_values": current_state_info.board_values,
            "c_turn": current_state_info.my_turn,
            "c_my_score": current_state_info.my_score,
            "c_enemy_score": current_state_info.enemy_score,
            "c_chips_left": current_state_info.chips_left,
            "c_hand_chips_values": current_state_info.hand_chips_values,
            "c_last_placed_chip": current_state_info.last_placed_chip,
            "n_board_values": next_state_info.board_values,
            "n_turn": next_state_info.my_turn,
            "n_my_score": next_state_info.my_score,
            "n_enemy_score": next_state_info.enemy_score,
            "n_chips_left": next_state_info.chips_left,
            "n_hand_chips_values": next_state_info.hand_chips_values,
            "n_last_placed_chip": next_state_info.last_placed_chip
        }
        result = self.session.run(QUERIES.FIND_TAKING_RELATION_INFO, **params)
        end_timer = time.time()
        self.bench11.append(end_timer - start_timer)

        record = next(result)
        rel_properties = record["r"]._properties
        return self.make_taking_relation_info_from_record(rel_properties)

    def find_game_state_next_relations(self, state_info, rel_type):
        start_timer = time.time()
        if rel_type == 0:
            query = QUERIES.FIND_GAME_STATE_NEXT_RELATIONS_PLACING
        elif rel_type == 1:
            query = QUERIES.FIND_GAME_STATE_NEXT_RELATIONS_TAKING
        params = {
            "c_board_values": state_info.board_values,
            "c_turn": state_info.my_turn,
            "c_my_score": state_info.my_score,
            "c_enemy_score": state_info.enemy_score,
            "c_chips_left": state_info.chips_left,
            "c_hand_chips_values": state_info.hand_chips_values,
            "c_last_placed_chip": state_info.last_placed_chip,
        }
        result = self.session.run(query, **params)
        end_timer = time.time()
        self.bench12.append(end_timer - start_timer)

        records = list(result)
        updated_records = []
        for record in records:
            rel_properties = record["r"]._properties
            if rel_type == 0:
                updated_records.append(self.make_placing_relation_info_from_record(rel_properties))
            elif rel_type == 1:
                updated_records.append(self.make_taking_relation_info_from_record(rel_properties))
        return updated_records

    def find_next_state_by_placing_relation(self, current_state_info, relation_info):
        start_timer = time.time()
        params = {
            "c_board_values": current_state_info.board_values,
            "c_turn": current_state_info.my_turn,
            "c_my_score": current_state_info.my_score,
            "c_enemy_score": current_state_info.enemy_score,
            "c_chips_left": current_state_info.chips_left,
            "c_hand_chips_values": current_state_info.hand_chips_values,
            "c_last_placed_chip": current_state_info.last_placed_chip,
            "row": relation_info.row,
            "col": relation_info.col,
            "chip_value": relation_info.chip_value
        }
        result = self.session.run(QUERIES.FIND_NEXT_STATE_BY_PLACING_RELATION, **params)
        end_timer = time.time()
        self.bench13.append(end_timer - start_timer)

        # Simplify dict
        record = (result.single(strict=True)).data()['n']
        return self.make_state_info_from_record(record)

    def find_next_state_by_taking_relation(self, current_state_info, relation_info):
        start_timer = time.time()
        # Restructurize combination
        updated_combination = []
        for chip in relation_info.combination:
            updated_combination.append(chip.row)
            updated_combination.append(chip.col)
            updated_combination.append(chip.value)
        params = {
            "c_board_values": current_state_info.board_values,
            "c_turn": current_state_info.my_turn,
            "c_my_score": current_state_info.my_score,
            "c_enemy_score": current_state_info.enemy_score,
            "c_chips_left": current_state_info.chips_left,
            "c_hand_chips_values": current_state_info.hand_chips_values,
            "c_last_placed_chip": current_state_info.last_placed_chip,
            "combination": updated_combination,
        }
        result = self.session.run(QUERIES.FIND_NEXT_STATE_BY_TAKING_RELATION, **params)
        end_timer = time.time()
        self.bench14.append(end_timer - start_timer)

        # Simplify dict
        record = (result.single(strict=True)).data()['n']
        return self.make_state_info_from_record(record)

    def set_is_closed_on_state(self, state_info: sti.StateInfo):
        params = {
            "board_values": state_info.board_values,
            "turn": state_info.my_turn,
            "my_score": state_info.my_score,
            "enemy_score": state_info.enemy_score,
            "chips_left": state_info.chips_left,
            "hand_chips_values": state_info.hand_chips_values,
            "last_placed_chip": state_info.last_placed_chip,
            "is_closed": True,
        }
        self.session.run(QUERIES.SET_IS_CLOSED_ON_STATE, **params)

    def find_max_next_state_q_value(self, current_state_info):
        root_start_timer = time.time()
        placing_relations_info = self.find_game_state_next_relations(current_state_info, rel_type=0)
        end_timer = time.time()
        self.bench16.append(end_timer - root_start_timer)

        start_timer = time.time()
        taking_relations_info = self.find_game_state_next_relations(current_state_info, rel_type=1)
        end_timer = time.time()
        self.bench17.append(end_timer - start_timer)

        start_timer = time.time()
        relations_info = placing_relations_info + taking_relations_info
        result = (max(relations_info, key=lambda x: x.q_value)).q_value
        end_timer = time.time()
        self.bench18.append(end_timer - start_timer)

        root_end_timer = time.time()
        self.bench15.append(root_end_timer - root_start_timer)
        return result

    def make_state_info_from_record(self, node_properties):
        start_timer = time.time()
        board_values = node_properties['board_values']
        my_turn = node_properties['my_turn']
        my_score = node_properties['my_score']
        enemy_score = node_properties['enemy_score']
        chips_left = node_properties['chips_left']
        hand_chips_values = node_properties['hand_chips_values']
        last_placed_chip = node_properties['last_placed_chip']
        is_initial_state = node_properties['initial_state']
        state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score,
                                   chips_left, hand_chips_values, last_placed_chip, is_initial_state)

        if 'times_visited' in node_properties.keys():
            times_visited = int(node_properties['times_visited'])
            state_info.times_visited = times_visited

        if 'win_counter' in node_properties.keys():
            win_counter = int(node_properties['win_counter'])
            state_info.win_counter = win_counter

        if 'lose_counter' in node_properties.keys():
            lose_counter = int(node_properties['lose_counter'])
            state_info.lose_counter = lose_counter

        if 'draw_counter' in node_properties.keys():
            draw_counter = int(node_properties['draw_counter'])
            state_info.draw_counter = draw_counter

        if 'is_closed' in node_properties.keys():
            is_closed = bool(node_properties['is_closed'])
            state_info.is_closed = is_closed

        end_timer = time.time()
        self.bench19.append(end_timer - start_timer)
        return state_info

    def make_placing_relation_info_from_record(self, relation_properties):
        start_timer = time.time()
        row = int(relation_properties['row'])
        col = int(relation_properties['col'])
        chip_value = int(relation_properties['chip_value'])
        placing_relation_info = pri.PlacingRelationInfo(row, col, chip_value)

        if 'q_value' in relation_properties.keys():
            q_value = float(relation_properties['q_value'])
            placing_relation_info.q_value = q_value

        end_timer = time.time()
        self.bench20.append(end_timer - start_timer)
        return placing_relation_info

    def make_taking_relation_info_from_record(self, relation_properties):
        start_timer = time.time()
        # Prepare to create TakingRelationInfo
        combination = relation_properties['combination']

        # Convert to [chip1, chip2, ...]
        time_iterate = int(len(combination) / 3)
        updated_combination = []
        for i in range(time_iterate):
            com_chip = cp.Chip(combination[3 * i + 2])
            com_chip.row = combination[3 * i + 0]
            com_chip.col = combination[3 * i + 1]
            updated_combination.append(com_chip)

        # Finally create TakingRelationInfo
        taking_relation_info = tri.TakingRelationInfo(updated_combination)

        if 'q_value' in relation_properties.keys():
            q_value = float(relation_properties['q_value'])
            taking_relation_info.q_value = q_value

        end_timer = time.time()
        self.bench21.append(end_timer - start_timer)
        return taking_relation_info
