import random
import src.learning_algorithm_parts.vertex as vrt


def get_random_index(list_len):
    return random.randint(0, list_len - 1)


# Vertex board values to string (list to string)
def vertex_values_to_string(value_list):
    string = ''
    for item in value_list:
        string += str(item)
    return string + '\n'


# String to vertex board values (string to list)
def string_to_vertex_values(string):
    value_list = []
    for index in range(len(string) - 1):
        value_list.append(int(string[index]))
    return value_list


# PATH CREATION FUNCTIONS
def create_path_from_values(path_values):
    root = vrt.Vertex(path_values[0])
    path_values.pop(0)
    add_next_vertex(root, path_values)
    return root


def add_next_vertex(root, path_values):
    # if path_values not empty
    if path_values:
        next_vertex = vrt.Vertex(path_values[0])
        path_values.pop(0)
        root.next_vertexes.append(next_vertex)
        add_next_vertex(next_vertex, path_values)


def print_path(root):
    print(root.board_values)
    if root.next_vertexes:
        print_path(root.next_vertexes[0])
