import src.learning_algorithm_parts.vertex as vrt


class Graph:
    def __init__(self, board_size):
        self.root = None
        self.create_root(board_size)

    def create_root(self, board_size):
        self.root = vrt.Vertex([0] * board_size)

    def is_vertex_found(self, vertex_values, is_silent=False):  # function for BFS
        visited = []  # List for visited vertex.
        queue = []  # Initialize a queue
        visited.append(self.root)
        queue.append(self.root)

        while queue:  # Creating loop to visit each vertex
            vertex_popped = queue.pop(0)
            if not is_silent:
                print(vertex_popped.board_values)

            # if [board_values] == [board_values]
            if vertex_values == vertex_popped.board_values:
                return vertex_popped

            for neighbour in vertex_popped.next_vertexes:
                if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append(neighbour)
        return False

    def append_vertex(self, parent_vertex_values, child_vertex_values):
        parent_vertex = self.is_vertex_found(parent_vertex_values, is_silent=True)
        parent_vertex.next_vertexes.append(vrt.Vertex(child_vertex_values))

