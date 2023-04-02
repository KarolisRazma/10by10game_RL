import time
import random

import src.game_components.environment as e
import src.utilities.constants3x3 as c3x3
import src.learning_algorithm_parts.graph as gh
import utilities.util_funcs as util

# 100 episodes -> 38.22 seconds
# nodes generated 5320

# 10000 episodes -> 2778.58 seconds -> 46.3 min
# nodes generated 61755
# agents win rate 40%
# agents lose rate 40%
# agents draw rate 20%


# constants
episodes = 100

if __name__ == "__main__":

    env = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
                        c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                        c3x3.score_to_win, "agent1", "agent2")

    start = time.time()
    for i in range(episodes):
        env.start_episode_with_graph_db()
    end = time.time()

    # Time taken on playing n episodes
    print(f'Time elapsed: {end - start}')

    print(f'Agent [0] won {env.agents[0].wins}')
    print(f'Agent [1] won {env.agents[1].wins}')
