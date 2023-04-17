import src.game_components.actions.placing_action as pan
import src.learning_algorithm_parts.state_info as sti


# Structure of the graph
#
# node GameState:
#   property: board_values
#   property: state_value
#   property: my_turn
#   property: my_score
#   property: enemy_score
#   property: chips_left
#
# relation NEXT_PLACING:
#   property: row
#   property: col
#   property: value
#
# relation NEXT_TAKING
#   property: combination [row, col, value]
#   property: last_placed_chip [row, col, value]

class Graph:
    def __init__(self, driver, session):
        self.driver = driver
        self.session = session

    def add_root(self, board_values, game_info):
        # Check if node exists
        if self.is_vertex_found(game_info):
            return

        self.session.run(
            """
            MERGE (:GameState {
            board_values: $values,
            state_value: 0.0,
            my_turn: $my_turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            """,
            values=board_values, my_turn=game_info.my_turn, my_score=game_info.my_score,
            enemy_score=game_info.enemy_score, chips_left=game_info.chips_left
        )

    # Parameters
    # current_state_values --> list of ints
    # next_states_values --> list of list of ints
    # action_type --> taking or placing action
    # actions --> actions list, combinations list
    # last_placed_chip --> if action is taking, specify which chips was placed in the same round
    # current_state_game_info --> StateInfo instance, holding current information about the game
    # next_states_game_info --> list of StateInfo instances, holding new possible information about the game
    def add_n_game_states(self, current_state_values, next_states_values,
                          action_type, actions, last_placed_chip,
                          current_state_game_info, next_states_game_info):
        for (n_state_values, action, n_state_game_info) in zip(next_states_values, actions, next_states_game_info):
            self.add_game_state(current_state_values, n_state_values, action_type,
                                action, last_placed_chip, current_state_game_info, n_state_game_info)

    # Parameters
    # current_state_values --> list of ints
    # next_state_values --> list of ints
    # action_type --> taking or placing action
    # action --> action or combination
    # last_placed_chip --> if action is taking, specify which chips was placed in the same round
    # current_state_game_info --> StateInfo instance, holding current information about the game
    # next_state_game_info --> StateInfo instance, holding new possible information about the game
    def add_game_state(self, current_state_values, next_state_values,
                       action_type, action, last_placed_chip, current_state_game_info, next_state_game_info):
        # Check if node exists
        if self.is_vertex_found(next_state_game_info):
            return

        # Create new game state
        self.session.run(
            """
            MERGE (:GameState {
            board_values: $board_values,
            state_value: 0.0,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            """,
            board_values=next_state_values, turn=next_state_game_info.my_turn, my_score=next_state_game_info.my_score,
            enemy_score=next_state_game_info.enemy_score, chips_left=next_state_game_info.chips_left
        )
        # Create relation for placing action
        if action_type == "placing":
            self.make_placing_rel(current_state_values, next_state_values,
                                  action, current_state_game_info, next_state_game_info)
            return
        # Create relation for taking action
        if action_type == "taking":
            self.make_taking_rel(current_state_values, next_state_values, action, last_placed_chip,
                                 current_state_game_info, next_state_game_info)

    def make_placing_rel(self, current_state_values, next_state_values, action,
                         current_state_game_info, next_state_game_info):
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
            MERGE (curr)-[:NEXT_PLACING {row: $row, col: $col, value: $value}]->(next) 
            """,
            c_board_values=current_state_values, c_turn=current_state_game_info.my_turn,
            c_my_score=current_state_game_info.my_score, c_enemy_score=current_state_game_info.enemy_score,
            c_chips_left=current_state_game_info.chips_left,
            n_board_values=next_state_values, n_turn=next_state_game_info.my_turn,
            n_my_score=next_state_game_info.my_score, n_enemy_score=next_state_game_info.enemy_score,
            n_chips_left=next_state_game_info.chips_left,
            row=action.row, col=action.col, value=action.value
        )

    def make_taking_rel(self, current_state_values, next_state_values, action, last_placed_chip,
                        current_state_game_info, next_state_game_info):
        updated_action = []
        for chip in action:
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
            c_board_values=current_state_values, c_turn=current_state_game_info.my_turn,
            c_my_score=current_state_game_info.my_score, c_enemy_score=current_state_game_info.enemy_score,
            c_chips_left=current_state_game_info.chips_left,
            n_board_values=next_state_values, n_turn=next_state_game_info.my_turn,
            n_my_score=next_state_game_info.my_score, n_enemy_score=next_state_game_info.enemy_score,
            n_chips_left=next_state_game_info.chips_left,
            combination=updated_action, last_placed_chip=last_placed_chip
        )

    # Returns dict with node's info
    def find_game_state(self, game_info):
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
            board_values=game_info.board_values, turn=game_info.my_turn, my_score=game_info.my_score,
            enemy_score=game_info.enemy_score, chips_left=game_info.chips_left,
        )
        record = result.single(strict=True)
        return record.data()['g']

    # GET GIVEN VERTEX NEXT VERTICES
    # Returns StateInfo object
    def find_game_state_next_vertices(self, action_type, current_state_values, game_info):
        if action_type == 'placing':
            result = self.session.run(
                """ 
                MATCH (:GameState {
                board_values: $board_values,
                my_turn: $turn,
                my_score: $my_score,
                enemy_score: $enemy_score,
                chips_left: $chips_left})-[:NEXT_PLACING]->(c:GameState)
                RETURN c
                """,
                board_values=current_state_values, turn=game_info.my_turn, my_score=game_info.my_score,
                enemy_score=game_info.enemy_score, chips_left=game_info.chips_left,
            )
        if action_type == 'taking':
            result = self.session.run(
                """ 
                MATCH (:GameState {
                board_values: $board_values,
                my_turn: $turn,
                my_score: $my_score,
                enemy_score: $enemy_score,
                chips_left: $chips_left})-[:NEXT_TAKING]->(c:GameState)
                RETURN c
                """,
                board_values=current_state_values, turn=game_info.my_turn, my_score=game_info.my_score,
                enemy_score=game_info.enemy_score, chips_left=game_info.chips_left,
            )
        if action_type == 'any':
            result = self.session.run(
                """ 
                MATCH (:GameState {
                board_values: $board_values,
                my_turn: $turn,
                my_score: $my_score,
                enemy_score: $enemy_score,
                chips_left: $chips_left})-->(c:GameState)
                RETURN c
                """,
                board_values=current_state_values, turn=game_info.my_turn, my_score=game_info.my_score,
                enemy_score=game_info.enemy_score, chips_left=game_info.chips_left,
            )
        records = list(result)
        updated_records = []
        for record in records:
            board_values = record.data()['c']['board_values']
            my_turn = record.data()['c']['my_turn']
            my_score = record.data()['c']['my_score']
            enemy_score = record.data()['c']['enemy_score']
            chips_left = record.data()['c']['chips_left']
            state_value = record.data()['c']['state_value']
            state_info = sti.StateInfo(board_values, my_turn, my_score, enemy_score, chips_left)
            state_info.state_value = state_value
            updated_records.append(state_info)
        return updated_records

    # GET ACTION FROM PARENT TO CHILD VERTEX
    def find_next_action(self, current_state_values, next_state_values, action_type,
                         board, last_placed_chip, current_state_game_info, next_state_game_info):
        if action_type == "placing":
            result = self.session.run(
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
                RETURN r.row, r.col, r.value
                """,
                c_board_values=current_state_values, c_turn=current_state_game_info.my_turn,
                c_my_score=current_state_game_info.my_score, c_enemy_score=current_state_game_info.enemy_score,
                c_chips_left=current_state_game_info.chips_left,
                n_board_values=next_state_values, n_turn=next_state_game_info.my_turn,
                n_my_score=next_state_game_info.my_score, n_enemy_score=next_state_game_info.enemy_score,
                n_chips_left=next_state_game_info.chips_left,
            )
            record = result.single(strict=True).data()
            row = int(record['r.row'])
            col = int(record['r.col'])
            value = int(record['r.value'])
            return pan.PlaceChipAction(row, col, value)
        if action_type == "taking":
            result = self.session.run(
                """
                MATCH (:GameState {
                board_values: $c_board_values,
                my_turn: $c_turn,
                my_score: $c_my_score,
                enemy_score: $c_enemy_score,
                chips_left: $c_chips_left})
                -[r {last_placed_chip: $last_placed_chip}]->(:GameState {
                board_values: $n_board_values,
                my_turn: $n_turn,
                my_score: $n_my_score,
                enemy_score: $n_enemy_score,
                chips_left: $n_chips_left})
                RETURN r.combination
                """,
                last_placed_chip=last_placed_chip,
                c_board_values=current_state_values, c_turn=current_state_game_info.my_turn,
                c_my_score=current_state_game_info.my_score, c_enemy_score=current_state_game_info.enemy_score,
                c_chips_left=current_state_game_info.chips_left,
                n_board_values=next_state_values, n_turn=next_state_game_info.my_turn,
                n_my_score=next_state_game_info.my_score, n_enemy_score=next_state_game_info.enemy_score,
                n_chips_left=next_state_game_info.chips_left,
            )
            record = result.single(strict=True).data()
            combination = record['r.combination']

            # RETURNS list of chips row/col/value to remove
            return combination

    # RETURNS BOARD VALUES OF ALL VERTICES
    def get_everything(self):
        result = self.session.run("MATCH (g:GameState) RETURN g.board_values AS board_values")
        records = list(result)  # a list of Record objects
        return records

    # RETURNS TRUE IF VERTEX IS FOUND
    def is_vertex_found(self, game_info):
        result = self.session.run(
            """ 
            MATCH (g:GameState {
            board_values: $board_values,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})    
            WITH COUNT(g) > 0  as node_exists
            RETURN node_exists
            """,
            board_values = game_info.board_values, turn = game_info.my_turn, my_score = game_info.my_score,
            enemy_score = game_info.enemy_score, chips_left = game_info.chips_left
        )
        return result.single(strict=True).data()['node_exists']

    # DELETE ENTIRE DB
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)

    # Updates state value with new value given
    def update_state_value(self, state_value, state_info):
        self.session.run(
            """
            MATCH (g:GameState {
            board_values: $board_values,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            SET g.state_value = $state_value
            """,
            board_values=state_info.board_values, turn=state_info.my_turn,
            my_score=state_info.my_score, enemy_score=state_info.enemy_score,
            chips_left=state_info.chips_left, state_value=state_value
        )

    # Finds maximum value of next states for given current state
    # argument current_state_info is StateInfo object
    def find_maximum_state_value(self, current_state_info):
        next_vertices_info = self.find_game_state_next_vertices(action_type='any',
                                                                current_state_values=current_state_info.board_values,
                                                                game_info=current_state_info)
        # Find max out of these next vertices
        return (max(next_vertices_info, key=lambda x: x.state_value)).state_value


