# Structure of the graph
#
# node GameState:
#   property: board_values
#   property: state_value
#   property: my_turn
#   property: my_score
#   property: chips_in_hand
#   property: enemy_score
#   property: chips_left
#   property: times_visited
#   property: win_counter:
#   property: lose_counter:
#   property: draw_counter:
#
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

    # Delete entire db
    def delete_everything(self):
        query_1 = """ MATCH (a) -[r] -> () DELETE a, r """
        query_2 = """ MATCH (a) DELETE a """
        self.session.run(query_1)
        self.session.run(query_2)

    # @argument state_info             --> StateInfo object
    def add_game_state(self, state_info):
        self.session(
            """
            MERGE (:GameState {
            board_values: $b_v,
            my_turn: $m_t,
            my_score: $m_s,
            enemy_score: $e_s,
            chips_left: $c_l})
            """,
            b_v=state_info.board_values, m_t=state_info.my_turn, m_s=state_info.my_score,
            e_s=state_info.enemy_score, c_l=state_info.chips_left
        )

    # @argument current_state_info          --> StateInfo object
    # @argument next_state_info             --> StateInfo object
    # @argument action                      --> list of ints [row, col, value]
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
            MERGE (curr)-[:NEXT_PLACING {row: $row, col: $col, value: $value}]->(next) 
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
    def make_taking_rel(self, current_state_info, next_state_info, action, last_placed_chip):
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
            c_board_values=current_state_info.board_values, c_turn=current_state_info.my_turn,
            c_my_score=current_state_info.my_score, c_enemy_score=current_state_info.enemy_score,
            c_chips_left=current_state_info.chips_left,
            n_board_values=next_state_info.board_values, n_turn=next_state_info.my_turn,
            n_my_score=next_state_info.my_score, n_enemy_score=next_state_info.enemy_score,
            n_chips_left=next_state_info.chips_left,
            combination=updated_action, last_placed_chip=last_placed_chip
        )

    # It updates state value and counters
    def update_node_after_episode(self, state_info, state_value, times_visited,
                                  win_counter, lose_counter, draw_counter):
        self.session.run(
            """
            MATCH (g:GameState {
            board_values: $board_values,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            SET g.state_value = $state_value
            SET g.times_visited = $times_visited
            SET g.win_counter = $win_counter
            SET g.lose_counter = $lose_counter
            SET g.draw_counter = $draw_counter
            """,
            board_values=state_info.board_values, turn=state_info.my_turn,
            my_score=state_info.my_score, enemy_score=state_info.enemy_score,
            chips_left=state_info.chips_left, state_value=state_value,
            times_visited=times_visited, win_counter=win_counter, lose_counter=lose_counter, draw_counter=draw_counter
        )

    def add_chips_in_hand_property(self, state_info, chips_values):
        self.session.run(
            """
            MATCH (g:GameState {
            board_values: $board_values,
            my_turn: $turn,
            my_score: $my_score,
            enemy_score: $enemy_score,
            chips_left: $chips_left})
            SET g.chips_in_hand = $chips_values
            """,
            board_values=state_info.board_values, turn=state_info.my_turn,
            my_score=state_info.my_score, enemy_score=state_info.enemy_score,
            chips_left=state_info.chips_left, chips=chips_values
        )

    def find_next_placing_action(self):
        pass

    def find_next_taking_action(self):
        pass












