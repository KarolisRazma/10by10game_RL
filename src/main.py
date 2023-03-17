import game_components.environment as e
import utilities.constants3x3 as c3x3
import utilities.constants5x5 as c5x5
import src.learning_algorithm_parts.graph_generator as gg

# constants
episodes = 100

g_generator = gg.GraphGenerator(c3x3.board_border_len, c3x3.container_capacity, c3x3.chips_types, c3x3.chips_per_type)
g_generator.simulate()

for i in range(episodes):
    g_generator.simulate()

g_generator.graph.is_vertex_found([0,0,0,0,1,0,0,0,0])


#
# # init environment
# env_3x3 = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
#                         c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
#                         c3x3.score_to_win)
#
# for i in range(episodes):
#     env_3x3.start_episode_without_graph()
#
# print("Wins by {}: {}".format(env_3x3.agents[0].id, env_3x3.agents[0].wins))
# print("Wins by {}: {}".format(env_3x3.agents[1].id, env_3x3.agents[1].wins))
# print("Draws: {}".format(env_3x3.agents[1].draws))
