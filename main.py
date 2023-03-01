import environment as e

# constants
episodes = 500

# init environment
env = e.Environment()

for i in range(episodes):
    env.start_episode()

print("Wins by {}: {}".format(env.agents[0].id, env.agents[0].wins))
print("Wins by {}: {}".format(env.agents[1].id, env.agents[1].wins))
print("Draws: {}".format(env.draws))


# after 1000 episodes, I got 22423 q-values
# print(len(env.qtable.q_values))
