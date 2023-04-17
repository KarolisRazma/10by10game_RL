import random


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
