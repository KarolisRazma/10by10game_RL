import time
import os


def display_options(options):
    for option in options:
        print(f'{option}')


def use_cli(env, path_evaluator, agent_0, agent_1, options):
    while True:
        # Only works in terminal
        os.system('clear')
        print(f'\n')

        display_options(options)
        choice = int(input("Enter option>  "))
        if 1 <= choice <= 4:
            if choice == 1:
                episodes = 1
            if choice == 2:
                episodes = 10
            if choice == 3:
                episodes = 100
            if choice == 4:
                episodes = int(input("Enter episodes: "))
            start = time.time()
            for i in range(episodes):
                # Play episode
                env.start_episode()
                # Evaluate round
                # Some evaluation happens here

                # Evaluate agent 0 path
                path_evaluator.set_path(agent_0.last_episode_path)
                path_evaluator.eval_path(agent_0.graph, agent_0.is_last_game_won)

                # Evaluate agent 1 path
                path_evaluator.set_path(agent_1.last_episode_path)
                path_evaluator.eval_path(agent_1.graph, agent_1.is_last_game_won)
            end = time.time()
            print(f'\n')
            print(f'Time elapsed: {end - start}')
            print(f'Agent [0] won {env.agents[0].wins}')
            print(f'Agent [1] won {env.agents[1].wins}')
        if choice == 5:
            env.agents[0].graph.delete_everything()
        if choice == 6:
            env.agents[1].graph.delete_everything()
        if choice == 7:
            env.agents[0].graph.delete_everything()
            env.agents[1].graph.delete_everything()
        if choice == 8:
            break
        if choice > 8:
            print(f'Invalid option')