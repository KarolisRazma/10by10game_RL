import src.agents.actions.placing_action as pan
import src.agents.improved_agent_learning.state_info as sti
import src.agents.improved_agent_learning.placing_relation_info as pri
import src.agents.improved_agent_learning.taking_relation_info as tri


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

    # Delete entire db
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)

    # @argument state_info      --> StateInfo object
    def add_game_state(self, state_info, is_initial_state=False):
        self.session.run(
            """
            MERGE (:GameState {
            board_values: $b_v,
            my_turn: $m_t,
            my_score: $m_s,
            enemy_score: $e_s,
            chips_left: $c_l,
            initial_state: $i_i_s})
            """,
            b_v=state_info.board_values, m_t=state_info.my_turn, m_s=state_info.my_score,
            e_s=state_info.enemy_score, c_l=state_info.chips_left, i_i_s=is_initial_state
        )

    # @argument current_state_info          --> StateInfo object
    # @argument next_state_info             --> StateInfo object
    # @argument action                      --> list of ints [row, col, chip_value]
    def make_placing_rel(self, current_state_info, next_state_info, action):
        self.session.run(
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
            chips_left: $n_chips_left})
            MERGE (curr)-[:NEXT_PLACING {row: $row, col: $col, chip_value: $value}]->(next) 
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            row=action.row, col=action.col, value=action.value
        )

    # @argument current_state_info          --> StateInfo object
    # @argument next_state_info             --> StateInfo object
    # @argument action                      --> list of Chip objects
    # @argument last_placed_chip            --> list of ints [row, col, value]
    def make_taking_rel(self, current_state_info, next_state_info, combination, last_placed_chip):
        updated_action = []
        for chip in combination:
            updated_action.append(chip.row)
            updated_action.append(chip.col)
            updated_action.append(chip.value)

        self.session.run(
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
            chips_left: $n_chips_left})
            MERGE (curr)-[:NEXT_TAKING {combination: $combination, last_placed_chip: $last_placed_chip}]->(next) 
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            combination=updated_action, last_placed_chip=last_placed_chip
        )

    # It updates counters
    def update_node_after_episode(self, state_info):
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

    # For returning an action (not relation info)
    # ---------------------------------------------------------------------
    def find_next_placing_action(self, current_state_info, next_state_info):
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
        record = result.single(strict=True).data()
        row = int(record['r.row'])
        col = int(record['r.col'])
        value = int(record['r.chip_value'])
        return pan.PlaceChipAction(row, col, value)

    # For returning an action (not relation info)
    # ---------------------------------------------------------------------
    def find_next_taking_action(self, current_state_info, next_state_info, last_placed_chip):
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
        record = result.single(strict=True).data()
        combination = record['r.combination']

        # RETURNS list of chips row/col/value to remove
        return combination

    # Returns StateInfo object
    def find_game_state(self, state_info):
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
        # Simplify dict
        record = (result.single(strict=True)).data()['g']

        # Create StateInfo
        board_values = record['board_values']
        my_turn = record['my_turn']
        my_score = record['my_score']
        enemy_score = record['enemy_score']
        chips_left = record['chips_left']
        state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score, chips_left)

        # Check if 'times_visited' is set in the database
        if 'times_visited' in record.keys():
            times_visited = int(record['times_visited'])
        else:
            times_visited = None

        # Check if 'win_counter' is set in the database
        if 'win_counter' in record.keys():
            win_counter = int(record['win_counter'])
        else:
            win_counter = None

        # Check if 'lose_counter' is set in the database
        if 'lose_counter' in record.keys():
            lose_counter = int(record['lose_counter'])
        else:
            lose_counter = None

        # Check if 'draw_counter' is set in the database
        if 'draw_counter' in record.keys():
            draw_counter = int(record['draw_counter'])
        else:
            draw_counter = None

        # Set it to the StateInfo object
        state_info.times_visited = times_visited
        state_info.win_counter = win_counter
        state_info.lose_counter = lose_counter
        state_info.draw_counter = draw_counter
        state_info.is_initial_state = record['initial_state']

        return state_info

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
        result = self.session.run(query,
                                  board_values=state_info.board_values, turn=state_info.my_turn,
                                  my_score=state_info.my_score, enemy_score=state_info.enemy_score,
                                  chips_left=state_info.chips_left)
        # if action_type == 'placing':
        #     result = self.session.run(
        #         """
        #         MATCH (:GameState {
        #         board_values: $board_values,
        #         my_turn: $turn,
        #         my_score: $my_score,
        #         enemy_score: $enemy_score,
        #         chips_left: $chips_left})-[:NEXT_PLACING]->(c:GameState)
        #         RETURN c
        #         """,
        #         board_values=state_info.board_values, turn=state_info.my_turn, my_score=state_info.my_score,
        #         enemy_score=state_info.enemy_score, chips_left=state_info.chips_left,
        #     )
        # if action_type == 'taking':
        #     result = self.session.run(
        #         """
        #         MATCH (:GameState {
        #         board_values: $board_values,
        #         my_turn: $turn,
        #         my_score: $my_score,
        #         enemy_score: $enemy_score,
        #         chips_left: $chips_left})-[:NEXT_TAKING]->(c:GameState)
        #         RETURN c
        #         """,
        #         board_values=state_info.board_values, turn=state_info.my_turn, my_score=state_info.my_score,
        #         enemy_score=state_info.enemy_score, chips_left=state_info.chips_left,
        #     )
        # if action_type == 'any':
        #     result = self.session.run(
        #         """
        #         MATCH (:GameState {
        #         board_values: $board_values,
        #         my_turn: $turn,
        #         my_score: $my_score,
        #         enemy_score: $enemy_score,
        #         chips_left: $chips_left})-->(c:GameState)
        #         RETURN c
        #         """,
        #         board_values=state_info.board_values, turn=state_info.my_turn, my_score=state_info.my_score,
        #         enemy_score=state_info.enemy_score, chips_left=state_info.chips_left,
        #     )

        records = list(result)
        updated_records = []
        for record in records:
            # Simplify dict
            record = record.data()['c']

            # Create StateInfo
            board_values = record['board_values']
            my_turn = record['my_turn']
            my_score = record['my_score']
            enemy_score = record['enemy_score']
            chips_left = record['chips_left']
            state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score, chips_left)

            # Check if 'times_visited' is set in the database
            if 'times_visited' in record.keys():
                times_visited = int(record['times_visited'])
            else:
                times_visited = None

            # Check if 'win_counter' is set in the database
            if 'win_counter' in record.keys():
                win_counter = int(record['win_counter'])
            else:
                win_counter = None

            # Check if 'lose_counter' is set in the database
            if 'lose_counter' in record.keys():
                lose_counter = int(record['lose_counter'])
            else:
                lose_counter = None

            # Check if 'draw_counter' is set in the database
            if 'draw_counter' in record.keys():
                draw_counter = int(record['draw_counter'])
            else:
                draw_counter = None

            # Set it to the StateInfo object
            state_info.times_visited = times_visited
            state_info.win_counter = win_counter
            state_info.lose_counter = lose_counter
            state_info.draw_counter = draw_counter
            state_info.is_initial_state = record['initial_state']

            updated_records.append(state_info)
        return updated_records

    def set_q_value(self, current_state_info, next_state_info, relation_info):
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

    def find_placing_relation_info(self, current_state_info, next_state_info):
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
            RETURN r.row, r.col, r.chip_value, r.q_value
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left
        )
        record = result.single(strict=True).data()

        # Create PlacingRelationInfo
        row = int(record['r.row'])
        col = int(record['r.col'])
        chip_value = int(record['r.chip_value'])
        placing_relation_info = pri.PlacingRelationInfo(row, col, chip_value)

        # Check if 'q_value' is set in the database
        if 'q_value' in record.keys():
            q_value = float(record['r.q_value'])
        else:
            q_value = None

        placing_relation_info.q_value = q_value
        return placing_relation_info

    def find_taking_relation_info(self, current_state_info, next_state_info, last_placed_chip):
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
            RETURN r.combination, r.last_placed_chip, r.q_value
            """,
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            lpc=last_placed_chip
        )
        # Simplify dict
        record = (result.single(strict=True)).data()

        # Create TakingRelationInfo
        combination = record['r.combination']
        last_placed_chip = record['r.last_placed_chip']
        taking_relation_info = tri.TakingRelationInfo(combination, last_placed_chip)

        # Check if 'q_value' is set in the database
        if 'q_value' in record.keys():
            q_value = float(record['r.q_value'])
        else:
            q_value = None

        taking_relation_info.q_value = q_value
        return taking_relation_info

    def find_game_state_next_relations(self, state_info, rel_type):
        if rel_type == 'placing':
            relation_name = "NEXT_PLACING"
            return_values = "r.row, r.col, r.chip_value, r.q_value"
        elif rel_type == 'taking':
            relation_name = "NEXT_TAKING"
            return_values = "r.combination, r.last_placed_chip, r.q_value"
        query = \
            f"""
            MATCH (:GameState {{
            board_values: $c_board_values,
            my_turn: $c_turn,
            my_score: $c_my_score,
            enemy_score: $c_enemy_score,
            chips_left: $c_chips_left}})
            -[r:{relation_name}]->(:GameState)
            RETURN {return_values}   
            """
        result = self.session.run(query, c_board_values=state_info.board_values, c_turn=state_info.my_turn,
                                  c_my_score=state_info.my_score, c_enemy_score=state_info.enemy_score,
                                  c_chips_left=state_info.chips_left)
        records = list(result)
        updated_records = []
        for record in records:
            # Simplify dict
            record = record.data()

            # Check if 'q_value' is set in the database
            if record['r.q_value'] is not None:
                q_value = float(record['r.q_value'])
            else:
                q_value = 0.0

            # Placing relation
            if relation_name == "NEXT_PLACING":
                # Create PlacingRelationInfo
                row = record['r.row']
                col = record['r.col']
                chip_value = record['r.chip_value']
                placing_relation_info = pri.PlacingRelationInfo(row, col, chip_value)
                placing_relation_info.q_value = q_value
                updated_records.append(placing_relation_info)
            # Taking relation
            else:
                # Create TakingRelationInfo
                combination = record['r.combination']
                last_placed_chip = record['r.last_placed_chip']
                taking_relation_info = tri.TakingRelationInfo(combination, last_placed_chip)
                taking_relation_info.q_value = q_value
                updated_records.append(taking_relation_info)

        return updated_records

    def find_next_state_by_placing_relation(self, current_state_info, relation_info):
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

        # Simplify dict
        record = (result.single(strict=True)).data()['n']

        # Create StateInfo
        board_values = record['board_values']
        my_turn = record['my_turn']
        my_score = record['my_score']
        enemy_score = record['enemy_score']
        chips_left = record['chips_left']
        state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score, chips_left)

        # Check if 'times_visited' is set in the database
        if 'times_visited' in record.keys():
            times_visited = int(record['times_visited'])
        else:
            times_visited = None

        # Check if 'win_counter' is set in the database
        if 'win_counter' in record.keys():
            win_counter = int(record['win_counter'])
        else:
            win_counter = None

        # Check if 'lose_counter' is set in the database
        if 'lose_counter' in record.keys():
            lose_counter = int(record['lose_counter'])
        else:
            lose_counter = None

        # Check if 'draw_counter' is set in the database
        if 'draw_counter' in record.keys():
            draw_counter = int(record['draw_counter'])
        else:
            draw_counter = None

        # Set it to the StateInfo object
        state_info.times_visited = times_visited
        state_info.win_counter = win_counter
        state_info.lose_counter = lose_counter
        state_info.draw_counter = draw_counter
        state_info.is_initial_state = record['initial_state']

        return state_info

    def find_next_state_by_taking_relation(self, current_state_info, relation_info):
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
            combination=relation_info.combination, last_placed_chip=relation_info.last_placed_chip
        )

        # Simplify dict
        record = (result.single(strict=True)).data()['n']

        # Create StateInfo
        board_values = record['board_values']
        my_turn = record['my_turn']
        my_score = record['my_score']
        enemy_score = record['enemy_score']
        chips_left = record['chips_left']
        state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score, chips_left)

        # Check if 'times_visited' is set in the database
        if 'times_visited' in record.keys():
            times_visited = int(record['times_visited'])
        else:
            times_visited = None

        # Check if 'win_counter' is set in the database
        if 'win_counter' in record.keys():
            win_counter = int(record['win_counter'])
        else:
            win_counter = None

        # Check if 'lose_counter' is set in the database
        if 'lose_counter' in record.keys():
            lose_counter = int(record['lose_counter'])
        else:
            lose_counter = None

        # Check if 'draw_counter' is set in the database
        if 'draw_counter' in record.keys():
            draw_counter = int(record['draw_counter'])
        else:
            draw_counter = None

        # Set it to the StateInfo object
        state_info.times_visited = times_visited
        state_info.win_counter = win_counter
        state_info.lose_counter = lose_counter
        state_info.draw_counter = draw_counter
        state_info.is_initial_state = record['initial_state']

        return state_info

    def find_max_next_state_q_value(self, current_state_info):
        placing_relations_info = self.find_game_state_next_relations(current_state_info, rel_type='placing')
        taking_relations_info = self.find_game_state_next_relations(current_state_info, rel_type='taking')
        relations_info = placing_relations_info + taking_relations_info
        return (max(relations_info, key=lambda x: x.q_value)).q_value
