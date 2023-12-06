from src.game_components.state_data import StateData


class ImprovedAgentStateData(StateData):
    def __init__(self, board_values, my_turn, my_score, enemy_score, chips_left, last_placed_chip_list,
                 hand_chips_values_list, enemy_hand_chips_values_list, container_chips_values_list,
                 is_initial_state=False):
        super().__init__(board_values, my_turn, my_score, enemy_score, chips_left, last_placed_chip_list,
                         hand_chips_values_list, enemy_hand_chips_values_list, container_chips_values_list,
                         is_initial_state)
