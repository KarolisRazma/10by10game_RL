from src.agents.improved_agent_learning.improved_agent_action_data import ImprovedAgentActionData
from src.agents.improved_agent_learning.improved_agent_state_data import ImprovedAgentStateData


class Path:
    def __init__(self):
        self.state_data_list: list[ImprovedAgentStateData] = []
        self.relation_data_list: list[ImprovedAgentActionData] = []

    def reset(self):
        self.state_data_list = []
        self.relation_data_list = []
