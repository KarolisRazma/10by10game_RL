import time
import random

import src.game_components.environment as e
import src.utilities.constants3x3 as c3x3
import src.learning_algorithm_parts.graph as gh
import utilities.util_funcs as util

# constants
episodes = 10

if __name__ == "__main__":
    g = gh.Graph()

    env = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
                        c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                        c3x3.score_to_win)

    start = time.time()
    for i in range(episodes):
        env.start_episode_with_graph_db()
    end = time.time()

    # Time taken on playing n episodes
    print(f'Time elapsed: {end - start}')

    # Print how many states are generated already
    states = g.get_everything()
    print(len(states))
