import src.learning_algorithm_parts.path_evaluator as pe
import src.game_components.environment as e
import src.utilities.constants3x3 as c3x3
import src.utilities.cli as cli

# CLI
options = ["[1] Start 1 episode", "[2] Start 10 episodes", "[3] Start 100 episodes", "[4] Start n episodes",
           "[5] Delete Agent 0 graph", "[6] Delete Agent 1 graph", "[7] Delete Agent's graphs", "[8] Exit"]

# Environment 3x3
env = e.Environment(c3x3.board_border_len, c3x3.container_capacity,
                    c3x3.chips_types, c3x3.chips_per_type, c3x3.scoring_parameter,
                    c3x3.score_to_win, "agent1", "agent2")

# Agents from Environment 3x3
agent_0 = env.agents[0]
agent_1 = env.agents[1]

# Path Evaluator instance
path_evaluator = pe.PathEvaluator()

if __name__ == "__main__":
    cli.use_cli(env, path_evaluator, agent_0, agent_1, options)



