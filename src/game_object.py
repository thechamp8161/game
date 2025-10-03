class GameObject:
    def __init__(self, x, y, name, description):
        self.x = x
        self.y = y
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"