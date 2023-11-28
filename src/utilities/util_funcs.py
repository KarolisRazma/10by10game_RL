import random

from src.agents.agent import Agent
from src.agents.improved_agent import ImprovedAgent
from src.agents.improved_agent_learning.learning import RLearning
from src.agents.random_walker_agent import RandomWalkerAgent


def get_random_index(list_len):
    return random.randint(0, list_len - 1)


# [WARNING] It's not a full copy, only relevant for particular optimization
def make_agent_copy(agent: Agent):
    if isinstance(agent, RandomWalkerAgent):
        random_walker_agent = RandomWalkerAgent(agent.name)
        random_walker_agent.wins = agent.wins
        random_walker_agent.draws = agent.draws
        return random_walker_agent

    elif isinstance(agent, ImprovedAgent):
        improved_agent = ImprovedAgent(name=agent.name,
                                       graph=agent.graph,
                                       learning_algorithm=RLearning(agent.path_evaluator.learning.discount_rate,
                                                                    agent.path_evaluator.learning.learning_rate),
                                       exploit_growth=agent.exploit_growth,
                                       explore_minimum=agent.explore_minimum,
                                       is_improved_exploitation_on=agent.is_improved_exploitation_on)
        improved_agent.wins = agent.wins
        improved_agent.draws = agent.draws
        return improved_agent
