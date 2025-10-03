class Mission:
    def __init__(self, name, description, goal_type='eliminate_all'):
        self.name = name
        self.description = description
        self.goal_type = goal_type
        self.is_complete = False

    def check_completion(self, game):
        if self.is_complete:
            return True

        if self.goal_type == 'eliminate_all':
            from enemy import Enemy  # Local import to avoid circular dependencies

            # Check if any Enemy objects remain in the game world
            enemies_left = any(isinstance(obj, Enemy) for obj in game.map.game_objects.values())

            if not enemies_left:
                self.is_complete = True
                print(f"\n*** MISSION COMPLETE: {self.name} ***")
                print(f"Objective: {self.description}")
                return True

        return False

    def display_status(self):
        status = "Complete" if self.is_complete else "In Progress"
        return f"Mission: {self.name} ({status})"