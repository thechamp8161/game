from game_object import GameObject

from game_object import GameObject
from weapon import Weapon # Import Weapon

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, "Player", "The protagonist of our story.")
        self.max_health = 100
        self.health = 100
        self.inventory = []
        self.equipped_weapon = None

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"You take {amount} damage. Your health is now {self.health}.")
        return self.health <= 0 # Return True if the player is dead

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        print(f"You feel your wounds closing. Your health is now {self.health}/{self.max_health}.")

    def add_to_inventory(self, item):
        self.inventory.append(item)
        print(f"You picked up the {item.name}.")
        # Automatically equip the first weapon picked up
        if isinstance(item, Weapon) and not self.equipped_weapon:
            self.equip_weapon(item)

    def equip_weapon(self, weapon):
        if weapon in self.inventory and isinstance(weapon, Weapon):
            self.equipped_weapon = weapon
            print(f"You have equipped the {weapon.name}.")
        else:
            print("You can't equip that.")

    def display_status(self):
        status = f"Health: {self.health}/{self.max_health}"

        inventory_names = [item.name for item in self.inventory]
        status += f"\nInventory: {inventory_names if inventory_names else 'Empty'}"

        if self.equipped_weapon:
            status += f"\nEquipped: {self.equipped_weapon}"
        else:
            status += f"\nEquipped: None"

        return status