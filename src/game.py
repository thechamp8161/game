import sys
from map import Map
from player import Player
from game_object import GameObject
from weapon import Weapon
from enemy import Enemy
from mission import Mission
from item import Item
from medkit import Medkit
from key import Key
from door import Door

class Game:
    def __init__(self, map_filepath):
        self.map = Map(map_filepath)
        self.game_over = False
        self._load_objects_from_map()
        self.mission = Mission("Clear the Area", "Eliminate all hostiles.")

    def _load_objects_from_map(self):
        player_pos = None
        for y, row in enumerate(self.map.map_data):
            for x, tile in enumerate(row):
                obj = None
                if tile == 'P':
                    player_pos = (x, y)
                elif tile == 'S': # Shotgun
                    obj = Weapon(x, y, "Shotgun", "A powerful pump-action shotgun.", damage=30, max_ammo=8, ammo=8)
                elif tile == 'K': # Key
                    obj = Key(x, y, "Key", "A small metal key.", key_id=1)
                elif tile == 'M': # Medkit
                    obj = Medkit(x, y, "Medkit", "A first-aid kit.", healing_amount=50)
                elif tile == 'D': # Door
                    obj = Door(x, y, key_id=1)
                elif tile == 'E': # Guard
                    obj = Enemy(x, y, "Guard", "A watchful guard.", health=30, damage=10)
                elif tile == 'H': # Heavy Guard
                    obj = Enemy(x, y, "Heavy Guard", "A heavily armored guard.", health=60, damage=20)

                if obj:
                    self.map.add_game_object(obj)
                    self.map.map_data[y][x] = '.'

        if not player_pos:
            print("Error: Player start position 'P' not found on the map.")
            sys.exit(1)

        self.player = Player(player_pos[0], player_pos[1])
        self.map.add_game_object(self.player)
        self.map.map_data[self.player.y][self.player.x] = '.'

    def get_description(self, x, y):
        obj = self.map.get_object_at(x, y)
        if obj and obj is not self.player:
            if isinstance(obj, Door):
                return f"a door that is {'locked' if obj.locked else 'unlocked'}"
            return f"a {obj.name}"

        tile = self.map.get_tile(x, y)
        if tile == '#': return "a solid wall"
        if tile == '.': return "an open path"
        return "the void"

    def look_around(self):
        x, y = self.player.x, self.player.y

        nearby_enemies = self.get_nearby_enemies()
        if nearby_enemies:
            print("\n!!! COMBAT INITIATED !!!")
            for enemy in nearby_enemies:
                print(f"A hostile {enemy.name} is nearby!")
            return

        descriptions = {
            "front": self.get_description(x, y - 1), "back": self.get_description(x, y + 1),
            "left": self.get_description(x - 1, y), "right": self.get_description(x + 1, y),
        }

        print("\nYou are standing in a room.")
        print(f"In front of you is {descriptions['front']}.")
        print(f"Behind you is {descriptions['back']}.")
        print(f"To your left is {descriptions['left']}.")
        print(f"To your right is {descriptions['right']}.")

        current_tile_obj = self.map.get_object_at(x,y)
        if current_tile_obj and current_tile_obj is not self.player:
             print(f"You see a {current_tile_obj.name} on the ground here.")

    def move_player(self, dx, dy):
        new_x, new_y = self.player.x + dx, self.player.y + dy

        if self.map.get_tile(new_x, new_y) == '#':
            print("You can't move there.")
            return

        dest_obj = self.map.get_object_at(new_x, new_y)
        if isinstance(dest_obj, Door) and dest_obj.locked:
            print(f"The {dest_obj.name} is locked.")
            return

        del self.map.game_objects[(self.player.x, self.player.y)]
        self.player.x, self.player.y = new_x, new_y
        self.map.add_game_object(self.player)
        print("You move.")
        self.look_around()

    def take_item(self):
        item = self.map.get_object_at(self.player.x, self.player.y)
        if item and isinstance(item, Item):
            self.player.add_to_inventory(item)
            del self.map.game_objects[(item.x, item.y)]
        else:
            print("There is nothing to take here.")

    def use_item(self, item_name):
        item_to_use = next((item for item in self.player.inventory if item.name.lower() == item_name.lower()), None)

        if not item_to_use:
            print(f"You don't have a '{item_name}'.")
            return

        if isinstance(item_to_use, Medkit):
            if self.player.health == self.player.max_health:
                print("You are already at full health.")
                return
            self.player.heal(item_to_use.healing_amount)
            self.player.inventory.remove(item_to_use)
            if self.get_nearby_enemies(): self.enemy_turn()
        else:
            print(f"You can't use the {item_to_use.name} right now.")

    def equip_weapon(self, weapon_name):
        weapon_to_equip = next((item for item in self.player.inventory if isinstance(item, Weapon) and item.name.lower() == weapon_name.lower()), None)

        if weapon_to_equip:
            self.player.equip_weapon(weapon_to_equip)
        else:
            print(f"You don't have a weapon called '{weapon_name}'.")

    def unlock_door(self):
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            door = self.map.get_object_at(self.player.x + dx, self.player.y + dy)
            if isinstance(door, Door):
                if not door.locked:
                    print("The door is already unlocked.")
                    return
                player_key = next((item for item in self.player.inventory if isinstance(item, Key) and item.key_id == door.key_id), None)
                if player_key:
                    door.unlock()
                    return
                else:
                    print("You don't have the key for this door.")
                    return
        print("There is no door here to unlock.")

    def get_nearby_enemies(self):
        return [obj for obj in self.map.game_objects.values() if isinstance(obj, Enemy) and abs(obj.x - self.player.x) <= 1 and abs(obj.y - self.player.y) <= 1 and obj is not self.player]

    def shoot_enemy(self):
        weapon = self.player.equipped_weapon
        if not weapon:
            print("You have no weapon equipped!"); return
        if weapon.ammo <= 0:
            print(f"Your {weapon.name} is out of ammo!"); return
        enemies = self.get_nearby_enemies()
        if not enemies:
            print("There are no enemies to shoot at."); return

        target = enemies[0]
        print(f"You shoot at the {target.name} with your {weapon.name}.")
        weapon.ammo -= 1

        if target.take_damage(weapon.damage):
            print(f"The {target.name} has been defeated!")
            del self.map.game_objects[(target.x, target.y)]

        self.enemy_turn()

    def enemy_turn(self):
        enemies = self.get_nearby_enemies()
        if not enemies: return

        print("\n--- Enemy Turn ---")
        for enemy in enemies:
            if enemy.health > 0:
                print(f"The {enemy.name} attacks you!")
                if self.player.take_damage(enemy.damage):
                    print("You have died. Game Over."); self.game_over = True; break
        print("--- Player Turn ---")

    def run(self):
        print("Welcome to the FPS Adventure!")
        self.look_around()

        while not self.game_over:
            if self.mission.check_completion(self):
                print("You have won the game!"); break

            print(f"\n{self.player.display_status()}\n{self.mission.display_status()}")

            nearby_enemies = self.get_nearby_enemies()
            if nearby_enemies:
                 print(f"In combat with: {[enemy.name for enemy in nearby_enemies]}")

            command = input("> ").lower().strip().split()
            if not command: continue
            action = command[0]
            args = " ".join(command[1:])

            if action == "quit": print("Thanks for playing!"); break

            if nearby_enemies:
                if action == "shoot": self.shoot_enemy()
                elif action == "use":
                    if args: self.use_item(args)
                    else: print("Use what?")
                else: print("In combat, you can 'shoot', 'use', or 'quit'.")
                continue

            if action == "look": self.look_around()
            elif action == "move":
                if args:
                    direction = args.split()[0]
                    if direction == 'w': self.move_player(0, -1)
                    elif direction == 's': self.move_player(0, 1)
                    elif direction == 'a': self.move_player(-1, 0)
                    elif direction == 'd': self.move_player(1, 0)
                    else: print("Unknown direction. Use w, a, s, or d.")
                else: print("Move where? (e.g., 'move w')")
            elif action == "take": self.take_item()
            elif action == "use":
                if args: self.use_item(args)
                else: print("Use what?")
            elif action == "equip":
                if args: self.equip_weapon(args)
                else: print("Equip what?")
            elif action == "unlock":
                self.unlock_door()
            elif action.startswith("debug"): self.map.display()
            else: print("Unknown command. Try 'look', 'move', 'take', 'use', 'equip', 'unlock', or 'quit'.")

if __name__ == "__main__":
    sys.path.insert(0, '.')
    from src.game import Game

    game = Game("maps/map.txt")
    game.run()