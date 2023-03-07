import chip as c


class Container:
    # @param capacity = maximum of chips in the container 
    # @param chips_types = list of chips values
    # @param chips_per_type = quantity of one type chips
    def __init__(self, capacity, chips_types, chips_per_type):
        self.capacity = capacity
        self.chips = []
        self.chips_types = chips_types
        self.chips_per_type = chips_per_type
        self.fill_container(self.chips_types, self.chips_per_type)

    # @param chips_types = list of chips values
    # @param chips_per_type = quantity of one type chips
    def fill_container(self, chips_types, chips_per_type):
        # check if capacity is large enough
        if self.capacity < (len(chips_types) * chips_per_type):
            self.capacity = (len(chips_types) * chips_per_type)
            print("[LOG] Initial value of container capacity was increased.")
        
        # loop to fill container
        for chip_value in range(len(chips_types)):
            chip_index = 0
            # loop to add specific value 
            while chip_index < chips_per_type:
                self.chips.append(c.Chip(chip_value + 1))
                chip_index += 1
    
    def draw_chip(self, index):
        if index < len(self.chips):     # if given index is less than chips left in container
            chip = self.chips[index]    # get chip from container
            del self.chips[index]       # then remove it from container
            return chip                 # return the removed chip
    
    def reset(self):
        self.chips = []  # TODO check how to empty list correctly
        self.fill_container(self.chips_types, self.chips_per_type)
