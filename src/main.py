import time
import random

import src.learning_algorithm_parts.path_evaluator as pe
import src.game_components.environment as e
import src.utilities.constants3x3 as c3x3
import src.learning_algorithm_parts.graph as gh
import utilities.util_funcs as util

# NEW DATA
# 100 episodes -> 241.22 seconds
# after 120 games nodes generated 9009

# OLD DATA
# 10000 episodes -> 2778.58 seconds -> 46.3 min
# nodes generated 61755
# agents win rate 40%
# agents lose rate 40%
# agents draw rate 20%


# constants
episodes = 10

if __name__ == "__main__":

    # Environment 3x3
    env = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
                        c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                        c3x3.score_to_win, "agent1", "agent2")
    # Agents from Environment
    agent_0 = env.agents[0]
    agent_1 = env.agents[1]

    # Path Evaluator instance
    path_evaluator = pe.PathEvaluator()

    # Delete Graphs
    env.agents[0].graph.delete_everything()
    env.agents[1].graph.delete_everything()

    start = time.time()
    for i in range(episodes):
        # Play episode
        env.start_episode_with_graph_db()
        # Evaluate round
        # Some evaluation happens here

        # Evaluate agent 0 path
        path_evaluator.set_path(agent_0.last_episode_path)
        path_evaluator.eval_path(agent_0.graph, agent_0.is_last_game_won)

        # Evaluate agent 1 path
        path_evaluator.set_path(agent_1.last_episode_path)
        path_evaluator.eval_path(agent_1.graph, agent_1.is_last_game_won)

    end = time.time()

    # Time taken on playing n episodes
    print(f'Time elapsed: {end - start}')

    print(f'Agent [0] won {env.agents[0].wins}')
    print(f'Agent [1] won {env.agents[1].wins}')
