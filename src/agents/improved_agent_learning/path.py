from src.agents.improved_agent_learning.state_info import StateInfo


class Path:
    def __init__(self):
        # List of StateInfo objects
        self.state_info_list: list[StateInfo] = []
        # List of Placing/Taking RelationInfo objects
        self.relation_info_list = []

    def reset(self):
        self.state_info_list = []
        self.relation_info_list = []
