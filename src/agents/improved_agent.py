import src.agents.agent as ag


# TODO need to define game routine for this agent
class ImprovedAgent(ag.Agent):
    # @param nickname               --> agent's id
    # @param graph                  --> neoj4 graph

    def __init__(self, nickname, graph):
        # Init Agent superclass
        super().__init__(nickname)

        # Graph stored in Neo4j
        self.graph = graph
