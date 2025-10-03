import sys
from map import Map
from player import Player
from game_object import GameObject
from weapon import Weapon
from enemy import Enemy
from mission import Mission

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
                if tile == 'P':
                    player_pos = (x, y)
                elif tile == 'W':
                    pistol = Weapon(x, y, "Pistol", "A standard issue pistol.", damage=10, max_ammo=12, ammo=12)
                    self.map.add_game_object(pistol)
                elif tile == 'E':
                    guard = Enemy(x, y, "Guard", "A watchful guard.", health=30)
                    self.map.add_game_object(guard)

        if not player_pos:
            print("Error: Player start position 'P' not found on the map.")
            sys.exit(1)

        self.player = Player(player_pos[0], player_pos[1])
        self.map.add_game_object(self.player)
        self.map.map_data[self.player.y][self.player.x] = '.'

    def get_description(self, x, y):
        obj = self.map.get_object_at(x, y)
        if obj and obj is not self.player:
            return f"a {obj.name}"

        tile = self.map.get_tile(x, y)
        if tile == '#': return "a solid wall"
        if tile == '.': return "an open path"
        if tile == 'D': return "a closed door"
        return "the void"

    def look_around(self):
        x, y = self.player.x, self.player.y

        # Check for enemies in adjacent squares to start combat
        nearby_enemies = self.get_nearby_enemies()
        if nearby_enemies:
            print("\n!!! COMBAT INITIATED !!!")
            for enemy in nearby_enemies:
                print(f"A hostile {enemy.name} is nearby!")
            return # Don't print normal look description during combat

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
        if self.map.get_tile(new_x, new_y) not in ['#', 'D']:
            del self.map.game_objects[(self.player.x, self.player.y)]
            self.player.x, self.player.y = new_x, new_y
            self.map.add_game_object(self.player)
            print("You move.")
            self.look_around()
        else:
            print("You can't move there.")

    def take_item(self):
        item = self.map.get_object_at(self.player.x, self.player.y)
        if item and isinstance(item, Weapon):
            self.player.add_to_inventory(item)
            del self.map.game_objects[(item.x, item.y)]
        else:
            print("There is nothing to take here.")

    def get_nearby_enemies(self):
        enemies = []
        x, y = self.player.x, self.player.y
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                obj = self.map.get_object_at(x + dx, y + dy)
                if isinstance(obj, Enemy):
                    enemies.append(obj)
        return enemies

    def shoot_enemy(self):
        weapon = self.player.equipped_weapon
        if not weapon:
            print("You have no weapon equipped!")
            return

        if weapon.ammo <= 0:
            print(f"Your {weapon.name} is out of ammo!")
            return

        enemies = self.get_nearby_enemies()
        if not enemies:
            print("There are no enemies to shoot at.")
            return

        target = enemies[0] # Simple: always target the first enemy found
        print(f"You shoot at the {target.name} with your {weapon.name}.")
        weapon.ammo -= 1

        is_dead = target.take_damage(weapon.damage)
        if is_dead:
            print(f"The {target.name} has been defeated!")
            del self.map.game_objects[(target.x, target.y)]

        self.enemy_turn()

    def enemy_turn(self):
        enemies = self.get_nearby_enemies()
        if not enemies:
            return # Combat is over

        print("\n--- Enemy Turn ---")
        for enemy in enemies:
            # Simple AI: The enemy always attacks the player
            print(f"The {enemy.name} attacks you!")
            is_player_dead = self.player.take_damage(10) # Fixed damage for now
            if is_player_dead:
                print("You have died. Game Over.")
                self.game_over = True
                break
        print("--- Player Turn ---")

    def run(self):
        print("Welcome to the FPS Adventure!")
        self.look_around()

        while not self.game_over:
            if self.mission.check_completion(self):
                print("You have won the game!")
                break

            print("\n" + self.player.display_status())
            print(self.mission.display_status())

            nearby_enemies = self.get_nearby_enemies()
            if nearby_enemies:
                 print(f"In combat with: {[enemy.name for enemy in nearby_enemies]}")

            command = input("> ").lower().strip().split()
            if not command: continue
            action = command[0]

            if action == "quit":
                print("Thanks for playing!")
                break

            # Combat commands take priority
            if nearby_enemies:
                if action == "shoot": self.shoot_enemy()
                elif action == "move": print("You can't move during combat!")
                elif action == "take": print("You can't pick up items during combat!")
                else: print("In combat, you can 'shoot' or 'quit'.")
                continue

            # Non-combat commands
            if action == "look": self.look_around()
            elif action == "move":
                if len(command) > 1:
                    direction = command[1]
                    if direction == 'w': self.move_player(0, -1)
                    elif direction == 's': self.move_player(0, 1)
                    elif direction == 'a': self.move_player(-1, 0)
                    elif direction == 'd': self.move_player(1, 0)
                    else: print("Unknown direction. Use w, a, s, or d.")
                else: print("Move where? (e.g., 'move w')")
            elif action == "take": self.take_item()
            elif action.startswith("debug"): self.map.display()
            else: print("Unknown command.")

if __name__ == "__main__":
    sys.path.insert(0, '.')
    from src.game import Game

    game = Game("maps/map.txt")
    game.run()