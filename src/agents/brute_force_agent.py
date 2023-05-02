import random
import src.agents.agent as ag
import src.agents.actions.taking_action as tan


class BruteForceAgent(ag.Agent):

    def __init__(self, nickname):
        super().__init__(nickname)

    # Returns random action (Placing/Taking) from actions list
    def select_action(self):
        random_index = random.randint(0, len(self.actions) - 1)
        return self.actions[random_index]

    # Added old function from legacy code, but it should work
    # for brute force agent (TakingAction)
    def get_actions_for_taking(self, combinations):
        self.actions = []  # first, clear action list
        # loop over all combinations
        for combination in range(len(combinations)):
            self.actions.append(tan.TakeChipsAction(combination))
