from game_object import GameObject

class Door(GameObject):
    def __init__(self, x, y, name="Door", description="A standard door.", locked=True, key_id=None):
        super().__init__(x, y, name, description)
        self.locked = locked
        self.key_id = key_id

    def unlock(self):
        if self.locked:
            self.locked = False
            self.description = "An unlocked door."
            print("The door clicks open.")
        else:
            print("The door is already unlocked.")