from src.game_components.action_data import ActionData
from src.game_components.chip import Chip


class ImprovedAgentActionData(ActionData):
    def __init__(self, row, col, chip_value, has_taking=False, combination=None):
        super().__init__(row, col, chip_value, has_taking, combination)

        # Estimate
        self.q_value = 0.0

        # Counters
        self.times_used = 0
        self.win_counter = 0
        self.lose_counter = 0
        self.draw_counter = 0

        self.from_closed_state = False
        self.to_closed_state = False

    def copy(self):
        combination_copy = []
        for chip in self.combination:
            chip_copy = Chip(chip.value)
            chip_copy.row = chip.row
            chip_copy.col = chip.col
            combination_copy.append(chip_copy)

        improved_agent_action_data_copy = ImprovedAgentActionData(
            row=self.row,
            col=self.col,
            chip_value=self.chip_value,
            has_taking=self.has_taking,
            combination=combination_copy
        )
        improved_agent_action_data_copy.q_value = self.q_value
        improved_agent_action_data_copy.times_used = self.times_used
        improved_agent_action_data_copy.win_counter = self.win_counter
        improved_agent_action_data_copy.lose_counter = self.lose_counter
        improved_agent_action_data_copy.draw_counter = self.draw_counter
        improved_agent_action_data_copy.from_closed_state = self.from_closed_state
        improved_agent_action_data_copy.to_closed_state = self.to_closed_state
        return improved_agent_action_data_copy
