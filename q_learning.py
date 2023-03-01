import Board

# constants
learning_rate = 0.01
discount_factor = 0.85


class QLearning:
    def __init__(self):
        self.qtable = QTable()
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor


class QTable:
    def __init__(self):
        self.q_values = []

    # def initialise_q_values(self, state, action):
    #     # check if state/action pair exists
    #     for item in self.q_values:
    #         if item.state == state:
    #             if item.action == action:
    #                 return
    #     # otherwise, init it
    #     self.q_values.append(QValue(state, action, 0))

    # returns value for Q(s,a) pair or otherwise zero if pair not found
    def get_q_value(self, state, action):
        for item in self.q_values:
            if item.state == state:
                if item.action == action:
                    return item.value
        self.q_values.append(QValue(state, action, 0))
        return 0


class QValue:
    def __init__(self, state, action, value):
        self.state = state
        self.action = action
        self.value = value


