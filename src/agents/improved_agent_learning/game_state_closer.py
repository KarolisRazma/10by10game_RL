from src.agents.improved_agent_learning.graph import Graph
from src.agents.improved_agent_learning.path import Path
from src.agents.improved_agent_learning.taking_relation_info import TakingRelationInfo


class GameStateCloser:

    def __init__(self, graph: Graph, game_path: Path = None):
        # It is expected that game_path will be ordered in descending order
        # It means from final state to initial state
        self.game_path = game_path
        self.graph = graph

    # Only closeing pre-final state
    #   Important notes:
    #       1. Closing is only done, when winner agent did the last move
    #       2. If taking relation is last relation in the list, then also close pre-pre-final state
    #   The scenarios:
    #       1. (pre-final state) [-placing>] (final state)
    #       2. (pre-pre-final state) [-placing>] (pre-final state) [-taking>] (final state)
    # One final note:
    #   * In this case, there's no need to show how "valuable" is closed state,
    #       the agent can only get to it by enemy's move
    def do_state_closing(self):
        final_state = self.game_path.state_info_list[0]
        pre_final_state = self.game_path.state_info_list[1]
        final_relation = self.game_path.relation_info_list[0]

        if final_state.my_turn and final_state.is_closed is not True:
            # Close final state and pre-final state
            self.graph.set_is_closed_on_state(final_state)
            self.graph.set_is_closed_on_state(pre_final_state)

            # Check if it is taking relation, then close one more state
            if isinstance(final_relation, TakingRelationInfo):
                pre_pre_final_state = self.game_path.state_info_list[2]
                self.graph.set_is_closed_on_state(pre_pre_final_state)
