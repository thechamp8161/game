class Map:
    def __init__(self, map_filepath):
        self.map_data = self._load_map(map_filepath)
        self.height = len(self.map_data)
        self.width = len(self.map_data[0]) if self.height > 0 else 0
        self.game_objects = {}

    def _load_map(self, map_filepath):
        with open(map_filepath, 'r') as f:
            return [list(line.strip()) for line in f.readlines()]

    def get_tile(self, x, y):
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.map_data[y][x]
        return None

    def add_game_object(self, obj):
        self.game_objects[(obj.x, obj.y)] = obj

    def get_object_at(self, x, y):
        return self.game_objects.get((x,y))

    def display(self):
        # This is a debug display and not the first-person view
        display_map = [row[:] for row in self.map_data]
        for (x,y), obj in self.game_objects.items():
            if 0 <= y < self.height and 0 <= x < self.width:
                # For now, just use the first letter of the object's name
                display_map[y][x] = obj.name[0]

        for row in display_map:
            print("".join(row))