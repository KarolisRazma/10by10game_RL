from src.game_components.action_data import ActionData


class ImprovedAgentActionData(ActionData):
    def __init__(self, row, col, chip_value, has_taking=False, combination=None, fully_explored=False):
        super().__init__(row, col, chip_value, has_taking, combination)

        # Estimate
        self.q_value = 0.0

        # Counters
        self.times_used = 0
        self.win_counter = 0
        self.lose_counter = 0
        self.draw_counter = 0

        self.fully_explored = fully_explored
