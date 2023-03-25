import game_components.environment as e
import utilities.constants3x3 as c3x3
import utilities.constants5x5 as c5x5
import src.learning_algorithm_parts.graph_generator as gg
import src.learning_algorithm_parts.graph as gh
import utilities.util_funcs as util
import time

# constants
episodes = 10

env = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
                    c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                    c3x3.score_to_win)

start = time.time()
for i in range(episodes):
    env.start_episode_with_graph()
end = time.time()

print(f'Time elapsed: {end - start}')

env.graph.store_to_file('environment_created_graph3.txt')
