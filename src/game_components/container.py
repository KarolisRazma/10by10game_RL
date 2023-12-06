import src.game_components.chip as c


class Container:
    # @param chips_types = list of chips values
    # @param chips_per_type = quantity of one type chips
    def __init__(self, chips_types, chips_per_type):
        self.chips = []
        self.chips_types = chips_types
        self.chips_per_type = chips_per_type
        self.capacity = (len(chips_types) * chips_per_type)

    def fill_container(self):
        # loop to fill container
        for chip_value in range(len(self.chips_types)):
            chip_index = 0
            # loop to add specific value 
            while chip_index < self.chips_per_type:
                self.chips.append(c.Chip(chip_value + 1))
                chip_index += 1
    
    def draw_chip(self, index):
        if index < len(self.chips):     # if given index is less than chips left in container
            chip = self.chips[index]    # get chip from container
            del self.chips[index]       # then remove it from container
            return chip                 # return the removed chip

    def get_chips_values_list(self):
        return sorted([chip.value for chip in self.chips])

    def custom_fill_container(self, chips_values):
        self.chips = []
        for value in chips_values:
            self.chips.append(c.Chip(value))

    def clear(self):
        self.chips = []

