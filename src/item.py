from game_object import GameObject

class Item(GameObject):
    def __init__(self, x, y, name, description):
        super().__init__(x, y, name, description)