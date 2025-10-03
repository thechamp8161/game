from item import Item

class Medkit(Item):
    def __init__(self, x, y, name, description, healing_amount):
        super().__init__(x, y, name, description)
        self.healing_amount = healing_amount