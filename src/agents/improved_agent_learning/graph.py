import src.agents.actions.placing_action as pan
import src.agents.improved_agent_learning.state_info as sti
import src.agents.improved_agent_learning.placing_relation_info as pri
import src.agents.improved_agent_learning.taking_relation_info as tri
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
#
# relation NEXT_PLACING:
#   property: row
#   property: col
#   property: chip_value
#   property: q-value
#
# relation NEXT_TAKING
#   property: combination [row, col, value]
#   property: last_placed_chip [row, col, value]
#   property: q-value


class Graph:
    def __init__(self, driver, session):
        self.driver = driver
        self.session = session

        self.bench1 = []    # Add game state
        self.bench2 = []    # Create next node and make placing rel
        self.bench3 = []    # Create next node and make taking rel
        self.bench4 = []    # Update node counters
        self.bench5 = []    # Find next placing action
        self.bench6 = []    # Find next taking action
        self.bench7 = []    # Find game state
        self.bench8 = []    # Find next game states
        self.bench9 = []    # Update Q-Value
        self.bench10 = []   # Find placing relation info
        self.bench11 = []   # Find taking relation info
        self.bench12 = []   # Find game state next relations
        self.bench13 = []   # Find next state by placing relation
        self.bench14 = []   # Find next state by taking relation
        self.bench15 = []   # Find max next state q-value (All time)
        self.bench16 = []   # Find max next state q-value (Placing)
        self.bench17 = []   # Find max next state q-value (Taking)
        self.bench18 = []   # Find max next state q-value (max function)
        self.bench19 = []   # Make state info from record
        self.bench20 = []   # Make placing relation info from record
        self.bench21 = []   # Make taking relation info from record

    # Delete entire db
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)

    # @argument state_info      --> StateInfo object
    def add_game_state(self, state_info, is_initial_state=False):
        start_timer = time.time()
        result = self.session.run(
            """
            MERGE (g:GameState {
            board_values: $b_v,
            my_turn: $m_t,
            my_score: $m_s,
            enemy_score: $e_s,
            chips_left: $c_l,
            initial_state: $i_i_s})
            RETURN g
            """,
            b_v=state_info.board_values, m_t=state_info.my_turn, m_s=state_info.my_score,
            e_s=state_info.enemy_score, c_l=state_info.chips_left, i_i_s=is_initial_state
        )
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
        result = self.session.run(
            """ 
            MATCH (curr:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})           
            MERGE (next:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left,
            initial_state: false})
            MERGE (curr)-[rel:NEXT_PLACING {row: $row, col: $col, chip_value: $value}]->(next) 
            RETURN next, rel
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            row=action.row, col=action.col, value=action.value
        )
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
    def create_next_node_and_make_taking_relation(self, current_state_info, next_state_info, combination,
                                                  last_placed_chip):
        updated_action = []
        for chip in combination:
            updated_action.append(chip.row)
            updated_action.append(chip.col)
            updated_action.append(chip.value)

        start_timer = time.time()
        result = self.session.run(
            """ 
            MATCH (curr:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            MERGE (next:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left,
            initial_state: false})
            MERGE (curr)-[rel:NEXT_TAKING {combination: $combination, last_placed_chip: $last_placed_chip}]->(next)
            RETURN next, rel
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            combination=updated_action, last_placed_chip=last_placed_chip
        )
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
    def update_node_after_episode(self, state_info):
        start_timer = time.time()
        self.session.run(
            """
            MATCH (g:GameState {
            board_values: $board_values,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            SET g.times_visited = $times_visited
            SET g.win_counter = $win_counter
            SET g.lose_counter = $lose_counter
            SET g.draw_counter = $draw_counter
            """,
            board_values=state_info.board_values, turn=state_info.my_turn,
            my_score=state_info.my_score, enemy_score=state_info.enemy_score,
            chips_left=state_info.chips_left,
            times_visited=state_info.times_visited, win_counter=state_info.win_counter,
            lose_counter=state_info.lose_counter, draw_counter=state_info.draw_counter
        )
        end_timer = time.time()
        self.bench4.append(end_timer - start_timer)

    # For returning an action (not relation info)
    # ---------------------------------------------------------------------
    def find_next_placing_action(self, current_state_info, next_state_info):
        start_timer = time.time()
        result = self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[r:NEXT_PLACING]->(:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left})
            RETURN r.row, r.col, r.chip_value
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
        )
        end_timer = time.time()
        self.bench5.append(end_timer - start_timer)

        record = result.single(strict=True).data()
        row = int(record['r.row'])
        col = int(record['r.col'])
        value = int(record['r.chip_value'])
        return pan.PlaceChipAction(row, col, value)

    # For returning an action (not relation info)
    # ---------------------------------------------------------------------
    def find_next_taking_action(self, current_state_info, next_state_info, last_placed_chip):
        start_timer = time.time()
        result = self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[r:NEXT_TAKING {last_placed_chip: $last_placed_chip}]->(:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left})
            RETURN r.combination
            """,
            last_placed_chip=last_placed_chip,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
        )
        end_timer = time.time()
        self.bench6.append(end_timer - start_timer)

        record = result.single(strict=True).data()
        combination = record['r.combination']

        # Convert to [chip1, chip2, ...]
        time_iterate = int(len(combination) / 3)
        updated_combination = []
        for i in range(time_iterate):
            com_chip = cp.Chip(combination[3 * i + 2])
            com_chip.row = combination[3 * i + 0]
            com_chip.col = combination[3 * i + 1]
            updated_combination.append(com_chip)

        # RETURNS list of chip objects to remove
        return updated_combination

    # Returns StateInfo object
    def find_game_state(self, state_info):
        start_timer = time.time()
        result = self.session.run(
            """ 
            MATCH (g:GameState {
            board_values: $board_values,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            RETURN g
            """,
            board_values=state_info.board_values, turn=state_info.my_turn, my_score=state_info.my_score,
            enemy_score=state_info.enemy_score, chips_left=state_info.chips_left,
        )
        end_timer = time.time()
        self.bench7.append(end_timer - start_timer)
        # Simplify dict
        record = (result.single(strict=True)).data()['g']
        return self.make_state_info_from_record(record)

    # Returns list of StateInfo objects
    def find_game_state_next_vertices(self, action_type, state_info):
        if action_type == "placing":
            rel_type = ":NEXT_PLACING"
        elif action_type == "taking":
            rel_type = ":NEXT_TAKING"
        elif action_type == "any":
            rel_type = ""

        query = f"""
                MATCH (:GameState {{
                board_values: $board_values,
                my_turn: $turn,
                my_score: $my_score,
                enemy_score: $enemy_score,
                chips_left: $chips_left}})-[{rel_type}]->(c:GameState)
                RETURN c
                """
        start_timer = time.time()
        result = self.session.run(query,
                                  board_values=state_info.board_values, turn=state_info.my_turn,
                                  my_score=state_info.my_score, enemy_score=state_info.enemy_score,
                                  chips_left=state_info.chips_left)
        end_timer = time.time()
        self.bench8.append(end_timer - start_timer)

        records = list(result)
        updated_records = []
        for record in records:
            # Simplify dict
            record = record.data()['c']
            updated_records.append(self.make_state_info_from_record(record))
        return updated_records

    def set_q_value(self, current_state_info, next_state_info, relation_info):
        start_timer = time.time()
        self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[r]->(:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left})
            SET r.q_value = $qvalue
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            qvalue=relation_info.q_value
        )
        end_timer = time.time()
        self.bench9.append(end_timer - start_timer)

    def find_placing_relation_info(self, current_state_info, next_state_info):
        start_timer = time.time()
        result = self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[r:NEXT_PLACING]->(:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left})
            RETURN r
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left
        )
        end_timer = time.time()
        self.bench10.append(end_timer - start_timer)

        record = next(result)
        rel_properties = record["r"]._properties
        return self.make_placing_relation_info_from_record(rel_properties)

    def find_taking_relation_info(self, current_state_info, next_state_info, last_placed_chip):
        start_timer = time.time()
        result = self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[r:NEXT_TAKING {last_placed_chip: $lpc}]->(:GameState {
            board_values: $n_board_values,
            my_turn: $n_turn,
            my_score: $n_my_score,
            enemy_score: $n_enemy_score,
            chips_left: $n_chips_left})
            RETURN r
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            lpc=last_placed_chip
        )
        end_timer = time.time()
        self.bench11.append(end_timer - start_timer)

        record = next(result)
        rel_properties = record["r"]._properties
        return self.make_taking_relation_info_from_record(rel_properties)

    def find_game_state_next_relations(self, state_info, rel_type):
        if rel_type == 'placing':
            relation_name = "NEXT_PLACING"
        elif rel_type == 'taking':
            relation_name = "NEXT_TAKING"
        query = \
            f"""
            MATCH (:GameState {{
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left}})
            -[r:{relation_name}]->(:GameState)
            RETURN r   
            """
        start_timer = time.time()
        result = self.session.run(query, c_board_values=state_info.board_values, c_turn=state_info.my_turn,
                                  c_my_score=state_info.my_score, c_enemy_score=state_info.enemy_score,
                                  c_chips_left=state_info.chips_left)
        end_timer = time.time()
        self.bench12.append(end_timer - start_timer)

        records = list(result)
        updated_records = []
        for record in records:
            rel_properties = record["r"]._properties
            if rel_type == 'placing':
                updated_records.append(self.make_placing_relation_info_from_record(rel_properties))
            elif rel_type == "taking":
                updated_records.append(self.make_taking_relation_info_from_record(rel_properties))
        return updated_records

    def find_next_state_by_placing_relation(self, current_state_info, relation_info):
        start_timer = time.time()
        result = self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[:NEXT_PLACING {
            row: $row,
            col: $col,
            chip_value: $chip_value
            }]->(n:GameState)
            RETURN n
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            row=relation_info.row, col=relation_info.col, chip_value=relation_info.chip_value
        )
        end_timer = time.time()
        self.bench13.append(end_timer - start_timer)

        # Simplify dict
        record = (result.single(strict=True)).data()['n']
        return self.make_state_info_from_record(record)

    def find_next_state_by_taking_relation(self, current_state_info, relation_info):
        # Restructurize combination
        updated_combination = []
        for chip in relation_info.combination:
            updated_combination.append(chip.row)
            updated_combination.append(chip.col)
            updated_combination.append(chip.value)
        start_timer = time.time()
        result = self.session.run(
            """
            MATCH (:GameState {
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left})
            -[:NEXT_TAKING {
            combination: $combination,
            last_placed_chip: $last_placed_chip
            }]->(n:GameState)
            RETURN n
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            combination=updated_combination, last_placed_chip=relation_info.last_placed_chip
        )
        end_timer = time.time()
        self.bench14.append(end_timer - start_timer)

        # Simplify dict
        record = (result.single(strict=True)).data()['n']
        return self.make_state_info_from_record(record)

    def find_max_next_state_q_value(self, current_state_info):
        root_start_timer = time.time()
        placing_relations_info = self.find_game_state_next_relations(current_state_info, rel_type='placing')
        end_timer = time.time()
        self.bench16.append(end_timer - root_start_timer)

        start_timer = time.time()
        taking_relations_info = self.find_game_state_next_relations(current_state_info, rel_type='taking')
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
        state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score, chips_left)

        if 'times_visited' in node_properties.keys():
            times_visited = int(node_properties['times_visited'])
        else:
            times_visited = None

        if 'win_counter' in node_properties.keys():
            win_counter = int(node_properties['win_counter'])
        else:
            win_counter = None

        if 'lose_counter' in node_properties.keys():
            lose_counter = int(node_properties['lose_counter'])
        else:
            lose_counter = None

        if 'draw_counter' in node_properties.keys():
            draw_counter = int(node_properties['draw_counter'])
        else:
            draw_counter = None

        # Set it to the StateInfo object
        state_info.times_visited = times_visited
        state_info.win_counter = win_counter
        state_info.lose_counter = lose_counter
        state_info.draw_counter = draw_counter
        state_info.is_initial_state = node_properties['initial_state']
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
        else:
            q_value = None

        placing_relation_info.q_value = q_value
        end_timer = time.time()
        self.bench20.append(end_timer - start_timer)
        return placing_relation_info

    def make_taking_relation_info_from_record(self, relation_properties):
        start_timer = time.time()
        # Prepare to create TakingRelationInfo
        combination = relation_properties['combination']
        last_placed_chip = relation_properties['last_placed_chip']

        # Convert to [chip1, chip2, ...]
        time_iterate = int(len(combination) / 3)
        updated_combination = []
        for i in range(time_iterate):
            com_chip = cp.Chip(combination[3 * i + 2])
            com_chip.row = combination[3 * i + 0]
            com_chip.col = combination[3 * i + 1]
            updated_combination.append(com_chip)

        # Finally create TakingRelationInfo
        taking_relation_info = tri.TakingRelationInfo(updated_combination, last_placed_chip)

        if 'q_value' in relation_properties.keys():
            q_value = float(relation_properties['q_value'])
        else:
            q_value = None

        taking_relation_info.q_value = q_value
        end_timer = time.time()
        self.bench21.append(end_timer - start_timer)
        return taking_relation_info
