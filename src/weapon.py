from item import Item

class Weapon(Item):
    def __init__(self, x, y, name, description, damage, max_ammo, ammo):
        super().__init__(x, y, name, description)
        self.damage = damage
        self.max_ammo = max_ammo
        self.ammo = ammo

    def __str__(self):
        return f"{self.name} (Dmg: {self.damage}, Ammo: {self.ammo}/{self.max_ammo})"