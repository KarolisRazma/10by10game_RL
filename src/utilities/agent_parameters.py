# This python code file defines parameters for agents (discount/learning rates and so on...)

class ImprovedAgent1Parameters:
    name = "ImprovedAgent1"
    database = "ba-sandbox"
    discount_rate = 0.8
    learning_rate = 0.2
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0


class ImprovedAgent2Parameters:
    name = "ImprovedAgent2"
    database = "test-time-2"
    discount_rate = 0.9
    learning_rate = 0.9
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0


class GreedyAgentParameters:
    name = "GreedyAgent"
    database = "ba-greedy"
    discount_rate = 0.9
    learning_rate = 0.9
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0


class FastingAgentParameters:
    name = "FastingAgent"
    database = "ba-fasting"
    discount_rate = 0.9
    learning_rate = 0.9
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0
