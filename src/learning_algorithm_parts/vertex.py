class Vertex:
    # @param board_values => list of chips values, that are on the board,
    # e.g. [1,0,2,3,1,2,1,0,0]
    # @field next_vertexes => list of references to next vertex
    def __init__(self, board_values):
        self.board_values = board_values
        self.next_vertexes = []

    def add_next_vertex(self, vertex):
        self.next_vertexes.append(vertex)

    def is_linked_already(self, vertex):
        for vx in self.next_vertexes:
            if vx == vertex:
                return True
        return False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)