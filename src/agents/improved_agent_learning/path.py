from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData


class Path:
    def __init__(self):
        self.state_data_list: list[ImprovedAgentStateData] = []
        self.relation_data_list: list[ImprovedAgentActionData] = []

    def reset(self):
        self.state_data_list = []
        self.relation_data_list = []

    def copy(self):
        path_copy = Path()
        for state_data in self.state_data_list:
            path_copy.state_data_list.append(state_data.copy())
        for relation_data in self.relation_data_list:
            path_copy.relation_data_list.append(relation_data.copy())
        return path_copy
