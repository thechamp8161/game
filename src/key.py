from item import Item

class Key(Item):
    def __init__(self, x, y, name, description, key_id):
        super().__init__(x, y, name, description)
        self.key_id = key_id # To match with a specific door or set of doors