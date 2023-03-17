import src.learning_algorithm_parts.vertex as vrt


class Graph:
    def __init__(self, board_size):
        self.root = None
        self.create_root(board_size)

    def create_root(self, board_size):
        self.root = vrt.Vertex([0] * board_size)

    #def store_to_file(self, filename):

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
        child_vertex = self.is_vertex_found(child_vertex_values, is_silent=True)

        if not child_vertex:
            # create new vertex, and append it
            parent_vertex.next_vertexes.append(vrt.Vertex(child_vertex_values))
        else:
            # append existing vertex to parent vertexes list
            # if it's not already appended
            if not parent_vertex.is_linked_already(child_vertex):
                parent_vertex.next_vertexes.append(child_vertex)




