class Tile:
    # color is enum Color field
    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

