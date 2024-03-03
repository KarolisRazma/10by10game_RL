# This python code file defines parameters for agents (discount/learning rates and so on...)

# Improved Agent 1
class ImprovedAgent1Parameters:
    name = "ImprovedAgent1"
    database = "ba-sandbox"
    discount_rate = 0.9
    learning_rate = 0.9
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0


# Improved Agent 2
class ImprovedAgent2Parameters:
    name = "ImprovedAgent2"
    database = "test-time-2"
    discount_rate = 0.9
    learning_rate = 0.9
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0


# Improved Agent 2
class CustomImprovedAgentParameters:
    name = "CustomAgent"
    database = "ba-sandbox"
    discount_rate = 0.9
    learning_rate = 0.9
    exploit_growth = 0.06
    explore_minimum = 0.10
    is_improved_exploitation_on = True
    exploit_to_closed_state_rate = 1.0
