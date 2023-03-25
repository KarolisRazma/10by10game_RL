import src.learning_algorithm_parts.vertex as vrt
import src.utilities.util_funcs as util


class Graph:
    def __init__(self, board_size, chips_types):
        self.root = None
        self.create_root(board_size, chips_types)

    def create_root(self, board_size, chips_types):
        self.root = vrt.Vertex([0] * board_size)
        # for chip_value in chips_types:
        #     chips_values_list = [0] * board_size
        #     chips_values_list[int((board_size-1) / 2)] = chip_value
        #     self.root.next_vertexes.append(vrt.Vertex(chips_values_list))

    # @param filename => filename that holds graph data
    def store_to_file(self, filename):
        with open(filename, 'w') as f:
            visited = []  # List for visited vertex.
            queue = []  # Initialize a queue
            visited.append(self.root)
            queue.append(self.root)

            while queue:  # Creating loop to visit each vertex
                vertex_popped = queue.pop(0)
                vertex_board_values = util.vertex_values_to_string(vertex_popped.board_values)
                next_vertexes_board_values = []
                for neighbour in vertex_popped.next_vertexes:
                    next_vertexes_board_values.append(util.vertex_values_to_string(neighbour.board_values))
                    if neighbour not in visited:
                        visited.append(neighbour)
                        queue.append(neighbour)

                # Writing vertex and it's children to file
                f.write(vertex_board_values)
                for child_value in next_vertexes_board_values:
                    f.write(child_value)
                f.write('---\n')

    # @param filename => filename that holds graph data
    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            # Read root and assign to self.root
            root_values = util.string_to_vertex_values(f.readline())
            self.root = vrt.Vertex(root_values)

            # Flag to identify when it's time to pick up next vertex
            take_next_vertex = False
            current_vertex = self.root
            for line in f:
                if line == "---\n":
                    take_next_vertex = True
                    continue
                if take_next_vertex:
                    current_vertex = self.find_vertex(util.string_to_vertex_values(line))
                    take_next_vertex = False
                    continue
                self.append_vertex_optimized(current_vertex, None, util.string_to_vertex_values(line))

    def find_vertex(self, vertex_values, is_silent=False):  # function for BFS
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
        return None

    def append_vertex(self, parent_vertex_values, child_vertex_values):
        parent_vertex = self.find_vertex(parent_vertex_values, is_silent=True)
        child_vertex = self.find_vertex(child_vertex_values, is_silent=True)

        if parent_vertex is not None:
            if child_vertex is None:
                # create new vertex and append it
                parent_vertex.next_vertexes.append(vrt.Vertex(child_vertex_values))
            else:
                # append existing vertex to parent vertexes list
                # if it's not already appended
                if not parent_vertex.is_linked_already(child_vertex):
                    parent_vertex.next_vertexes.append(child_vertex)

    # TODO optimize appending to graph? (How to optimize it?)
    def append_vertex_optimized(self, parent_vertex, child_vertex, child_vertex_values):
        # If child vertex is not given
        if child_vertex is None:
            child_vertex = self.find_vertex(child_vertex_values, is_silent=True)
            if child_vertex is None:
                # Create new child vertex
                child_vertex = vrt.Vertex(child_vertex_values)

        # append existing child vertex to parent vertexes list
        # if it's not already appended
        if not parent_vertex.is_linked_already(child_vertex):
            parent_vertex.next_vertexes.append(child_vertex)

