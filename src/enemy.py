from game_object import GameObject

class Enemy(GameObject):
    def __init__(self, x, y, name, description, health=50, damage=10):
        super().__init__(x, y, name, description)
        self.health = health
        self.damage = damage

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"The {self.name} takes {amount} damage. Current health: {self.health}")
        return self.health <= 0 # Return True if the enemy is dead

    def __str__(self):
        return super().__str__() + f" (Health: {self.health})"