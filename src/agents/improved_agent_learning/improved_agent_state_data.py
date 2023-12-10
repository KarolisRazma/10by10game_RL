from src.game_components.state_data import StateData


class ImprovedAgentStateData(StateData):
    def __init__(self, board_values, my_turn, my_score, enemy_score, chips_left, last_placed_chip_list,
                 hand_chips_values_list, enemy_hand_chips_values_list, container_chips_values_list,
                 is_initial=False, is_final=False, is_closed=False, game_result=None):
        super().__init__(board_values, my_turn, my_score, enemy_score, chips_left, last_placed_chip_list,
                         hand_chips_values_list, enemy_hand_chips_values_list, container_chips_values_list,
                         is_initial, is_final)
        self.is_closed = is_closed

        # Not in database
        # Only set on is_final=True
        self.game_result = game_result

    def copy(self):
        return ImprovedAgentStateData(
            board_values=self.board_values.copy(),
            my_turn=self.my_turn,
            my_score=self.my_score,
            enemy_score=self.enemy_score,
            chips_left=self.chips_left,
            last_placed_chip_list=self.last_placed_chip_list.copy(),
            hand_chips_values_list=self.hand_chips_values_list.copy(),
            enemy_hand_chips_values_list=self.enemy_hand_chips_values_list.copy(),
            container_chips_values_list=self.container_chips_values_list.copy(),
            is_initial=self.is_initial,
            is_final=self.is_final,
            is_closed=self.is_closed,
            game_result=self.game_result
        )
