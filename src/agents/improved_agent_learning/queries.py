ADD_INITIAL_GAME_STATE = \
    """
        MERGE (g:GameState {
        board_values: $b_v,
        my_turn: $m_t,
        my_score: $m_s,
        enemy_score: $e_s,
        chips_left: $c_l,
        initial_state: $i_i_s,
        hand_chips_values: $hand_chips_values,
        last_placed_chip: $last_placed_chip
        })
        RETURN g
    """

CREATE_NEXT_NODE_AND_MAKE_PLACING_RELATION = \
    """
        MATCH (curr:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip})           
        MERGE (next:GameState {
        board_values: $n_board_values,
        my_turn: $n_turn,
        my_score: $n_my_score,
        enemy_score: $n_enemy_score,
        chips_left: $n_chips_left,
        initial_state: $n_initial_state,
        hand_chips_values: $n_hand_chips_values,
        last_placed_chip: $n_last_placed_chip})
        MERGE (curr)-[rel:NEXT_PLACING {row: $row, col: $col, chip_value: $value}]->(next) 
        RETURN next, rel
    """

CREATE_NEXT_NODE_AND_MAKE_TAKING_RELATION = \
    """
        MATCH (curr:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip})           
        MERGE (next:GameState {
        board_values: $n_board_values,
        my_turn: $n_turn,
        my_score: $n_my_score,
        enemy_score: $n_enemy_score,
        chips_left: $n_chips_left,
        initial_state: $n_initial_state,
        hand_chips_values: $n_hand_chips_values,
        last_placed_chip: $n_last_placed_chip})
        MERGE (curr)-[rel:NEXT_TAKING {combination: $combination}]->(next)
        RETURN next, rel
    """
FIND_NEXT_STATE_BY_PLACING_RELATION = \
    """
        MATCH (:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip})
        -[:NEXT_PLACING { row: $row, col: $col, chip_value: $chip_value }]->(n:GameState)
        RETURN n
    """
FIND_NEXT_STATE_BY_TAKING_RELATION = \
    """
        MATCH (:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip})
        -[:NEXT_TAKING { combination: $combination }]->(n:GameState)
        RETURN n
    """

FIND_GAME_STATE_NEXT_RELATIONS_PLACING = \
    """
        MATCH (:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip
        })
        -[r:NEXT_PLACING]->(:GameState)
        RETURN r  
    """

FIND_GAME_STATE_NEXT_RELATIONS_TAKING = \
    """
        MATCH (:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip
        })
        -[r:NEXT_TAKING]->(:GameState)
        RETURN r  
    """

FIND_PLACING_RELATION_INFO = \
    """
        MATCH (:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip})
        -[r:NEXT_PLACING]->(:GameState {
        board_values: $n_board_values,
        my_turn: $n_turn,
        my_score: $n_my_score,
        enemy_score: $n_enemy_score,
        chips_left: $n_chips_left,
        hand_chips_values: $n_hand_chips_values,
        last_placed_chip: $n_last_placed_chip})
        RETURN r
    """

FIND_TAKING_RELATION_INFO = \
    """
        MATCH (:GameState {
        board_values: $c_board_values,
        my_turn: $c_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        hand_chips_values: $c_hand_chips_values,
        last_placed_chip: $c_last_placed_chip})
        -[r:NEXT_TAKING]->(:GameState {
        board_values: $n_board_values,
        my_turn: $n_turn,
        my_score: $n_my_score,
        enemy_score: $n_enemy_score,
        chips_left: $n_chips_left,
        hand_chips_values: $n_hand_chips_values,
        last_placed_chip: $n_last_placed_chip})
        RETURN r
    """

UPDATE_Q_VALUE_AND_COUNTERS_PLACING = \
    """
        MATCH (:GameState)-[r:NEXT_PLACING {row: $row, col: $col, chip_value: $chip_value}]->(n:GameState {
                board_values: $n_board_values,
                my_turn: $n_turn,
                my_score: $n_my_score,
                enemy_score: $n_enemy_score,
                chips_left: $n_chips_left,
                hand_chips_values: $n_hand_chips_values,
                last_placed_chip: $n_last_placed_chip})
        SET r.q_value = $qvalue
        SET n.times_visited = $times_visited
        SET n.win_counter = $win_counter
        SET n.lose_counter = $lose_counter
        SET n.draw_counter = $draw_counter 
    """

UPDATE_Q_VALUE_AND_COUNTERS_TAKING = \
    """
        MATCH (:GameState)-[r:NEXT_TAKING {combination: $combination}]->(n:GameState {
                board_values: $n_board_values,
                my_turn: $n_turn,
                my_score: $n_my_score,
                enemy_score: $n_enemy_score,
                chips_left: $n_chips_left,
                hand_chips_values: $n_hand_chips_values,
                last_placed_chip: $n_last_placed_chip})
        SET r.q_value = $qvalue
        SET n.times_visited = $times_visited
        SET n.win_counter = $win_counter
        SET n.lose_counter = $lose_counter
        SET n.draw_counter = $draw_counter 
    """

UPDATE_COUNTERS = \
    """
        MATCH (g:GameState {
        board_values: $board_values,
        my_turn: $turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        hand_chips_values: $hand_chips_values,
        last_placed_chip: $last_placed_chip
        })
        SET g.times_visited = $times_visited
        SET g.win_counter = $win_counter
        SET g.lose_counter = $lose_counter
        SET g.draw_counter = $draw_counter
    """

SET_IS_CLOSED_ON_STATE = \
    """
        MATCH (g:GameState {
        board_values: $board_values,
        my_turn: $turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        hand_chips_values: $hand_chips_values,
        last_placed_chip: $last_placed_chip
        })
        SET g.is_closed = $is_closed
    """