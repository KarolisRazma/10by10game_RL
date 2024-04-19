# This python code file defines parameters for agents (discount/learning rates and so on...)

class ImprovedAgent1Parameters:
    name = "ImprovedAgent1"
    database = "ba-fasting"

    discount_rate = 0.50
    learning_rate = 0.90

    exploit_growth = 0.15
    explore_minimum = 0.05
    exploit_growth_by_depth = 0.10

    is_improved_exploitation_on = False
    improved_exploitation_least_times_used = 10
    improved_exploitation_least_win_rate = 0.40

    exploit_to_closed_state_rate = 1.0

    exploration_phase_is_applied = False
    exploration_phase_duration = 250000


class ImprovedAgent2Parameters:
    name = "ImprovedAgent2"
    database = "test-time-2"

    discount_rate = 0.8
    learning_rate = 0.2

    exploit_growth = 0.10
    explore_minimum = 0.10
    exploit_growth_by_depth = 0.10

    is_improved_exploitation_on = False
    improved_exploitation_least_times_used = 10
    improved_exploitation_least_win_rate = 0.4

    exploit_to_closed_state_rate = 1.0

    exploration_phase_is_applied = True
    exploration_phase_duration = 250000


class GreedyAgentParameters:
    name = "GreedyAgent"
    database = "ba-fasting"

    discount_rate = 0.8
    learning_rate = 0.2

    exploit_growth = 0.10
    explore_minimum = 0.10
    exploit_growth_by_depth = 0.10

    is_improved_exploitation_on = False
    improved_exploitation_least_times_used = 10
    improved_exploitation_least_win_rate = 0.4

    exploit_to_closed_state_rate = 1.0

    exploration_phase_is_applied = True
    exploration_phase_duration = 250000


class FastingAgentParameters:
    name = "FastingAgent"
    database = "ba-fasting"

    discount_rate = 0.8
    learning_rate = 0.2

    exploit_growth = 0.10
    explore_minimum = 0.10
    exploit_growth_by_depth = 0.10

    is_improved_exploitation_on = False
    improved_exploitation_least_times_used = 10
    improved_exploitation_least_win_rate = 0.4

    exploit_to_closed_state_rate = 1.0

    exploration_phase_is_applied = True
    exploration_phase_duration = 250000
