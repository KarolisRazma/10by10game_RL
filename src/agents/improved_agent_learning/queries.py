FIND_OR_CREATE_FINAL_STATE = \
    """
        MERGE (:GameState {
        board_values: $board_values,
        my_turn: $my_turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        last_placed_chip: $last_placed_chip,
        hand_chips_values: $hand_chips_values,
        my_captured: $my_captured,
        enemy_captured: $enemy_captured,
        is_initial: $is_initial,
        is_final: $is_final
        })
    """

FIND_OR_CREATE_PREVIOUS_STATE_AND_MAKE_NEXT_RELATION = \
    """
        MERGE (prev:GameState {
        board_values: $p_board_values,
        my_turn: $p_my_turn,
        my_score: $p_my_score,
        enemy_score: $p_enemy_score,
        chips_left: $p_chips_left,
        last_placed_chip: $p_last_placed_chip,
        hand_chips_values: $p_hand_chips_values,
        my_captured: $p_my_captured,
        enemy_captured: $p_enemy_captured,
        is_initial: $p_is_initial,
        is_final: $p_is_final
        })    
        WITH prev        
        MATCH (curr:GameState {
        board_values: $c_board_values,
        my_turn: $c_my_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        last_placed_chip: $c_last_placed_chip,
        hand_chips_values: $c_hand_chips_values,
        my_captured: $c_my_captured,
        enemy_captured: $c_enemy_captured,
        is_initial: $c_is_initial,
        is_final: $c_is_final
        })
        MERGE (prev)-
        [rel:NEXT {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}]
        ->(curr)
        SET rel.q_value = $q_value
        SET rel.times_used = $times_used
        SET rel.win_counter = $win_counter
        SET rel.lose_counter = $lose_counter
        SET rel.draw_counter = $draw_counter
    """

UPDATE_RELATION_PROPERTIES_WHEN_WIN = \
    """
        MATCH (prev:GameState {
        board_values: $p_board_values,
        my_turn: $p_my_turn,
        my_score: $p_my_score,
        enemy_score: $p_enemy_score,
        chips_left: $p_chips_left,
        last_placed_chip: $p_last_placed_chip,
        hand_chips_values: $p_hand_chips_values,
        my_captured: $p_my_captured,
        enemy_captured: $p_enemy_captured,        
        is_initial: $p_is_initial,
        is_final: $p_is_final
        })-[rel:NEXT 
        {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}
        ]->(:GameState)
        SET rel.q_value = $q_value
        SET rel.times_used = coalesce(rel.times_used, 0) + 1
        SET rel.win_counter = coalesce(rel.win_counter, 0) + 1
        SET rel.lose_counter = coalesce(rel.lose_counter, 0)
        SET rel.draw_counter = coalesce(rel.draw_counter, 0)
        SET rel.is_cut = $is_cut
    """

UPDATE_RELATION_PROPERTIES_WHEN_LOSE = \
    """
        MATCH (prev:GameState {
        board_values: $p_board_values,
        my_turn: $p_my_turn,
        my_score: $p_my_score,
        enemy_score: $p_enemy_score,
        chips_left: $p_chips_left,
        last_placed_chip: $p_last_placed_chip,
        hand_chips_values: $p_hand_chips_values,
        my_captured: $p_my_captured,
        enemy_captured: $p_enemy_captured,
        is_initial: $p_is_initial,
        is_final: $p_is_final
        })-[rel:NEXT 
        {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}
        ]->(:GameState)
        SET rel.q_value = $q_value
        SET rel.times_used = coalesce(rel.times_used, 0) + 1
        SET rel.win_counter = coalesce(rel.win_counter, 0) 
        SET rel.lose_counter = coalesce(rel.lose_counter, 0) + 1
        SET rel.draw_counter = coalesce(rel.draw_counter, 0)
        SET rel.is_cut = $is_cut
    """

UPDATE_RELATION_PROPERTIES_WHEN_DRAW = \
    """
    MATCH (prev:GameState {
    board_values: $p_board_values,
    my_turn: $p_my_turn,
    my_score: $p_my_score,
    enemy_score: $p_enemy_score,
    chips_left: $p_chips_left,
    last_placed_chip: $p_last_placed_chip,
    hand_chips_values: $p_hand_chips_values,
    my_captured: $p_my_captured,
    enemy_captured: $p_enemy_captured,
    is_initial: $p_is_initial,
    is_final: $p_is_final
    })-[rel:NEXT 
    {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}
    ]->(:GameState)
    SET rel.q_value = $q_value
    SET rel.times_used = coalesce(rel.times_used, 0) + 1
    SET rel.win_counter = coalesce(rel.win_counter, 0)
    SET rel.lose_counter = coalesce(rel.lose_counter, 0)
    SET rel.draw_counter = coalesce(rel.draw_counter, 0) + 1
    SET rel.is_cut = $is_cut
"""

FIND_GAME_STATE_NEXT_RELATIONS = \
    """
        MATCH (:GameState {
        board_values: $board_values,
        my_turn: $my_turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        last_placed_chip: $last_placed_chip,
        hand_chips_values: $hand_chips_values,
        my_captured: $my_captured,
        enemy_captured: $enemy_captured,
        is_initial: $is_initial,
        is_final: $is_final
        })
        -[r:NEXT]->(:GameState)
        RETURN r  
    """

FIND_OR_CREATE_NEXT_GAME_STATE_AND_MAKE_REL = \
    """
        MATCH (curr:GameState {
        board_values: $c_board_values,
        my_turn: $c_my_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        is_initial: $c_is_initial,
        is_final: $c_is_final,
        last_placed_chip: $c_last_placed_chip,
        hand_chips_values: $c_hand_chips_values,
        my_captured: $c_my_captured,
        enemy_captured: $c_enemy_captured
        })    
        MERGE (next:GameState {
        board_values: $n_board_values,
        my_turn: $n_my_turn,
        my_score: $n_my_score,
        enemy_score: $n_enemy_score,
        chips_left: $n_chips_left,
        is_initial: $n_is_initial,
        is_final: $n_is_final,
        last_placed_chip: $n_last_placed_chip,
        hand_chips_values: $n_hand_chips_values,
        my_captured: $n_my_captured,
        enemy_captured: $n_enemy_captured
        })
        MERGE (curr)-
        [rel:NEXT {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}]
        ->(next)
        SET rel.from_closed_state = $from_closed_state
        RETURN next.is_closed
    """

CLOSE_GAME_STATE = \
    """
        MATCH (g:GameState {
        board_values: $board_values,
        my_turn: $my_turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        is_initial: $is_initial,
        is_final: $is_final,
        last_placed_chip: $last_placed_chip,
        hand_chips_values: $hand_chips_values,
        my_captured: $my_captured,
        enemy_captured: $enemy_captured
        })
        SET g.is_closed = $is_closed
    """

REMOVE_RELATION = \
    """
        OPTIONAL MATCH (g:GameState {
        board_values: $board_values,
        my_turn: $my_turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        is_initial: $is_initial,
        is_final: $is_final,
        last_placed_chip: $last_placed_chip,
        hand_chips_values: $hand_chips_values,
        my_captured: $my_captured,
        enemy_captured: $enemy_captured
        })
        -[r:NEXT {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}]
        ->(:GameState)
        DELETE r
    """

FIND_IDENTICAL_RELATIONS_FROM_STATE = \
    """
        OPTIONAL MATCH (g:GameState {
        board_values: $board_values,
        my_turn: $my_turn,
        my_score: $my_score,
        enemy_score: $enemy_score,
        chips_left: $chips_left,
        is_initial: $is_initial,
        is_final: $is_final,
        last_placed_chip: $last_placed_chip,
        hand_chips_values: $hand_chips_values,
        my_captured: $my_captured,
        enemy_captured: $enemy_captured
        })-[rel:NEXT {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}]
        ->(:GameState)
        RETURN rel
    """

FIND_RELATION_DATA_BY_PREVIOUS_AND_CURRENT_STATE = \
    """
        OPTIONAL MATCH (prev:GameState {
        board_values: $p_board_values,
        my_turn: $p_my_turn,
        my_score: $p_my_score,
        enemy_score: $p_enemy_score,
        chips_left: $p_chips_left,
        is_initial: $p_is_initial,
        is_final: $p_is_final,
        last_placed_chip: $p_last_placed_chip,
        hand_chips_values: $p_hand_chips_values,
        my_captured: $p_my_captured,
        enemy_captured: $p_enemy_captured,
        })
        -[rel:NEXT {row: $row, col: $col, chip_value: $chip_value, has_taking: $has_taking, combination: $combination}]
        ->(curr:GameState {
        board_values: $c_board_values,
        my_turn: $c_my_turn,
        my_score: $c_my_score,
        enemy_score: $c_enemy_score,
        chips_left: $c_chips_left,
        is_initial: $c_is_initial,
        is_final: $c_is_final,
        last_placed_chip: $c_last_placed_chip,
        hand_chips_values: $c_hand_chips_values,
        my_captured: $c_my_captured,
        enemy_captured: $c_enemy_captured,
        })
        RETURN rel
    """
