# src/modules/world.py
import pygame
import random
import pytmx
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT, \
    AREA_0_BACKGROUND, AREA_1_BACKGROUND, AREA_2_BACKGROUND, AREA_3_BACKGROUND, AREA_4_BACKGROUND, AREA_5_BACKGROUND, \
    AREA_0_MAP, AREA_1_MAP, AREA_2_MAP, AREA_3_MAP, AREA_4_MAP, AREA_5_MAP, HUD_HEIGHT
from src.modules.enemies import Sapa, SplitterSapa, ProjectileSapa, ChaserSapa, DiagonalSapa, BossArea1, BossArea2, \
    BossArea3, BossArea4, BossArea5, Skuld
from collections import deque

class Maze:
    def __init__(self, num_crosses=8, cross_size_range=(1, 3), shape_weights=None, min_cross_distance=2, min_path_length=15):
        print("Entering Maze.__init__...")
        try:
            self.width = MAZE_WIDTH
            self.height = MAZE_HEIGHT
            self.grid = self.create_arena()
            self.entry, self.exit = self.add_entry_exit()
            self.grid = self.place_cross_walls(
                entry=self.entry,
                exit_=self.exit,
                num_crosses=num_crosses,
                cross_size_range=cross_size_range,
                shape_weights=shape_weights,
                min_cross_distance=min_cross_distance,
                min_path_length=min_path_length
            )
            if not self.is_connected(self.entry, self.exit):
                print("Connectivity broken, carving fallback path...")
                x, y = self.entry
                gx, gy = self.exit
                while (x, y) != (gx, gy):
                    if x < gx:
                        x += 1
                    elif x > gx:
                        x -= 1
                    if y < gy:
                        y += 1
                    elif y > gy:
                        y -= 1
                    self.grid[y][x] = 0
            print("Maze initialized successfully.")
        except Exception as e:
            print(f"Error in Maze.__init__: {e}")
            raise

    def create_arena(self):
        arena = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for x in range(self.width):
            arena[0][x] = 1  # Top border
            arena[self.height - 1][x] = 1  # Bottom border
        for y in range(self.height):
            arena[y][0] = 1  # Left border
            arena[y][self.width - 1] = 1  # Right border
        return arena

    def add_entry_exit(self):
        height = len(self.grid)
        width = len(self.grid[0])
        sides = ["top", "bottom", "left", "right"]
        opposite_sides = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}

        def pick_opening(side):
            if side == "top":
                x = random.randrange(1, width - 3)
                y = 0
                for i in range(x, x + 2):
                    self.grid[y][i] = 0
                return (x + 1, y)
            elif side == "bottom":
                x = random.randrange(1, width - 3)
                y = height - 1
                for i in range(x, x + 2):
                    self.grid[y][i] = 0
                return (x + 1, y)
            elif side == "left":
                x = 0
                y = random.randrange(1, height - 3)
                for i in range(y, y + 2):
                    self.grid[i][x] = 0
                return (x, y + 1)
            else:  # "right"
                x = width - 1
                y = random.randrange(1, height - 3)
                for i in range(y, y + 2):
                    self.grid[i][x] = 0
                return (x, y + 1)

        entry_side = random.choice(sides)
        exit_side = opposite_sides[entry_side]
        entry = pick_opening(entry_side)
        exit_ = pick_opening(exit_side)
        return entry, exit_

    def is_connected(self, start, goal):
        height = len(self.grid)
        width = len(self.grid[0])
        visited = [[False] * width for _ in range(height)]
        queue = deque([start])
        visited[start[1]][start[0]] = True

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                return True
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if self.grid[ny][nx] == 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((nx, ny))
        return False

    def bfs_distance(self, start, goal):
        height = len(self.grid)
        width = len(self.grid[0])
        visited = [[False] * width for _ in range(height)]
        queue = deque([(start, 0)])
        visited[start[1]][start[0]] = True

        while queue:
            (x, y), dist = queue.popleft()
            if (x, y) == goal:
                return dist
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if self.grid[ny][nx] == 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append(((nx, ny), dist + 1))
        return None

    def generate_shape_cells(self, center, cross_size, shape_type):
        cx, cy = center
        cells = set()
        cells.add((cx, cy))

        if shape_type == "plus":
            for dist in range(1, cross_size + 1):
                cells.add((cx, cy - dist))
                cells.add((cx, cy + dist))
                cells.add((cx - dist, cy))
                cells.add((cx + dist, cy))
        elif shape_type == "T":
            temp = set()
            for dist in range(1, cross_size + 1):
                temp.add((cx, cy - dist))
                temp.add((cx, cy + dist))
                temp.add((cx - dist, cy))
                temp.add((cx + dist, cy))
            arm_options = [
                {(cx, cy - d) for d in range(1, cross_size + 1)},
                {(cx, cy + d) for d in range(1, cross_size + 1)},
                {(cx - d, cy) for d in range(1, cross_size + 1)},
                {(cx + d, cy) for d in range(1, cross_size + 1)}
            ]
            remove_arm = random.choice(arm_options)
            temp = temp - remove_arm
            cells = cells.union(temp)
        elif shape_type == "L":
            orientations = [
                [(1, 0), (0, 1)],
                [(-1, 0), (0, 1)],
                [(1, 0), (0, -1)],
                [(-1, 0), (0, -1)]
            ]
            arms = random.choice(orientations)
            for dx, dy in arms:
                for dist in range(1, cross_size + 1):
                    cells.add((cx + dx * dist, cy + dy * dist))
        elif shape_type == "arc":
            quadrants = {
                "up_left": [(-1, 0), (0, -1)],
                "up_right": [(1, 0), (0, -1)],
                "down_left": [(-1, 0), (0, 1)],
                "down_right": [(1, 0), (0, 1)]
            }
            quadrant = random.choice(list(quadrants.keys()))
            for dx, dy in quadrants[quadrant]:
                for dist in range(1, cross_size + 1):
                    cells.add((cx + dx * dist, cy + dy * dist))
        else:
            for dist in range(1, cross_size + 1):
                cells.add((cx, cy - dist))
                cells.add((cx, cy + dist))
                cells.add((cx - dist, cy))
                cells.add((cx + dist, cy))

        valid_cells = {(x, y) for (x, y) in cells if 0 < x < self.width - 1 and 0 < y < self.height - 1}
        return valid_cells

    def place_cross_walls(self, entry, exit_, num_crosses, cross_size_range, shape_weights, min_cross_distance,
                          min_path_length):
        height = len(self.grid)
        width = len(self.grid[0])
        placed = 0
        attempts = 0
        max_attempts = num_crosses * 100
        placed_centers = []

        if shape_weights is None:
            shape_weights = {"plus": 1, "T": 1, "L": 1, "arc": 1}

        shape_types = list(shape_weights.keys())
        weights = list(shape_weights.values())

        while placed < num_crosses and attempts < max_attempts:
            attempts += 1
            cx = random.randint(1, width - 2)
            cy = random.randint(1, height - 2)
            center = (cx, cy)

            if any(abs(cx - pcx) + abs(cy - pcy) < min_cross_distance for (pcx, pcy) in placed_centers):
                continue

            shape_type = random.choices(shape_types, weights=weights, k=1)[0]
            cross_size = random.randint(cross_size_range[0], cross_size_range[1])
            candidate_cells = self.generate_shape_cells(center, cross_size, shape_type)

            if any(self.grid[y][x] != 0 for (x, y) in candidate_cells):
                continue

            for (x, y) in candidate_cells:
                self.grid[y][x] = 1

            if not self.is_connected(entry, exit_):
                for (x, y) in candidate_cells:
                    self.grid[y][x] = 0
                continue

            if min_path_length is not None:
                path_length = self.bfs_distance(entry, exit_)
                if path_length is None or path_length < min_path_length:
                    for (x, y) in candidate_cells:
                        self.grid[y][x] = 0
                    continue

            placed_centers.append(center)
            placed += 1
            print(f"Placed obstacle {placed}/{num_crosses}: Shape {shape_type} at ({cx}, {cy})")

        if placed < num_crosses:
            print(f"Warning: Only placed {placed}/{num_crosses} obstacles after {attempts} attempts.")
        return self.grid

    def collides(self, rect):
        try:
            top_left_x = rect.x // TILE_SIZE
            top_left_y = (rect.y - HUD_HEIGHT) // TILE_SIZE
            bottom_right_x = (rect.x + rect.width - 1) // TILE_SIZE
            bottom_right_y = (rect.y + rect.height - 1 - HUD_HEIGHT) // TILE_SIZE

            for y in range(max(0, top_left_y), min(self.height, bottom_right_y + 1)):
                for x in range(max(0, top_left_x), min(self.width, bottom_right_x + 1)):
                    if self.grid[y][x] == 1:
                        return True
            return False
        except Exception as e:
            print(f"Error in Maze.collides: {e}")
            raise

    def find_open_start_position(self):
        print("Finding open start position near entry...")
        try:
            entry_x, entry_y = self.entry
            max_attempts = 100
            attempt = 0
            radius = 3
            while attempt < max_attempts:
                x = random.randint(max(1, entry_x - radius), min(self.width - 2, entry_x + radius))
                y = random.randint(max(1, entry_y - radius), min(self.height - 2, entry_y + radius))
                if self.grid[y][x] == 0:
                    screen_x = x * TILE_SIZE
                    screen_y = y * TILE_SIZE + HUD_HEIGHT
                    return screen_x, screen_y
                attempt += 1
            print("Warning: Failed to find open start position near entry after maximum attempts. Using entry position.")
            return entry_x * TILE_SIZE, entry_y * TILE_SIZE + HUD_HEIGHT
        except Exception as e:
            print(f"Error in Maze.find_open_start_position: {e}")
            raise

    def find_open_position(self):
        print("Finding open position...")
        try:
            max_attempts = 100
            attempt = 0
            while attempt < max_attempts:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                if self.grid[y][x] == 0:
                    entry_distance = ((x - self.entry[0]) ** 2 + (y - self.entry[1]) ** 2) ** 0.5
                    exit_distance = ((x - self.exit[0]) ** 2 + (y - self.exit[1]) ** 2) ** 0.5
                    if entry_distance > 5 and exit_distance > 5:
                        screen_x = x * TILE_SIZE
                        screen_y = y * TILE_SIZE + HUD_HEIGHT
                        return screen_x, screen_y
                attempt += 1
            print("Warning: Failed to find open position after maximum attempts. Using default (1, 1).")
            return TILE_SIZE, TILE_SIZE + HUD_HEIGHT
        except Exception as e:
            print(f"Error in Maze.find_open_position: {e}")
            raise

class Scene:
    def __init__(self, area_id, scene_id, player, vitalik_freed):
        print(f"Entering Scene.__init__ for Area {area_id}, Scene {scene_id}...")
        try:
            self.area_id = area_id
            self.scene_id = scene_id
            self.player = player
            self.tokens = []
            self.checkpoints = []
            self.sapas = []
            self.fragments = []
            self.npc = None
            self.minigame = None
            self.sword = None
            self.boss = None
            self.exits = {}
            self.vitalik_freed = vitalik_freed
            self.tmx_data = None

            # Load area-specific background
            background_paths = {
                0: AREA_0_BACKGROUND,
                1: AREA_1_BACKGROUND,
                2: AREA_2_BACKGROUND,
                3: AREA_3_BACKGROUND,
                4: AREA_4_BACKGROUND,
                5: AREA_5_BACKGROUND
            }
            background_path = background_paths.get(area_id, AREA_0_BACKGROUND)
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            try:
                print(f"Attempting to load area background from: {background_path}")
                if not os.path.exists(background_path):
                    raise FileNotFoundError(f"File not found: {background_path}")
                self.background = pygame.image.load(background_path).convert()
                self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load area background at {background_path}. Error: {e}. Using placeholder.")
                for y in range(SCREEN_HEIGHT):
                    r = 14 + (y / SCREEN_HEIGHT) * (50 - 14)
                    g = 39 + (y / SCREEN_HEIGHT) * (70 - 39)
                    b = 59 + (y / SCREEN_HEIGHT) * (100 - 59)
                    pygame.draw.line(self.background, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))

            # Generate random maze
            self.maze = Maze()
            self.grid = self.maze.grid
            self.width = self.maze.width
            self.height = self.maze.height

            # Load Tiled map for visuals
            map_paths = {
                0: AREA_0_MAP,
                1: AREA_1_MAP,
                2: AREA_2_MAP,
                3: AREA_3_MAP,
                4: AREA_4_MAP,
                5: AREA_5_MAP
            }
            map_path = map_paths.get(area_id, None)
            self.tmx_data = None
            try:
                print(f"Attempting to load Tiled map from: {map_path}")
                if map_path and os.path.exists(map_path):
                    self.tmx_data = pytmx.load_pygame(map_path)
                    # Validate Tiled map dimensions
                    if self.tmx_data.width != self.width or self.tmx_data.height != self.height:
                        raise ValueError(f"Tiled map dimensions ({self.tmx_data.width}x{self.tmx_data.height}) do not match maze dimensions ({self.width}x{self.height}).")
                else:
                    raise FileNotFoundError("Tiled map file not found.")
            except (pygame.error, FileNotFoundError, ValueError, Exception) as e:
                print(f"Failed to load Tiled map at {map_path}. Error: {e}. Will use procedural rendering.")

            # Select random entry and exit from possible points
            possible_entries = []
            possible_exits = []
            if self.tmx_data:
                for obj in self.tmx_data.objects:
                    if obj.name and "Entry" in obj.name:
                        possible_entries.append((int(obj.x // TILE_SIZE), int(obj.y // TILE_SIZE)))
                    elif obj.name and "Exit" in obj.name:
                        possible_exits.append((int(obj.x // TILE_SIZE), int(obj.y // TILE_SIZE)))
            if possible_entries and possible_exits:
                self.entry = random.choice(possible_entries)
                self.exit = random.choice([e for e in possible_exits if e != self.entry])
            else:
                self.entry = self.maze.entry
                self.exit = self.maze.exit
                # Ensure entry and exit are open
                self.grid[self.entry[1]][self.entry[0]] = 0
                self.grid[self.exit[1]][self.exit[0]] = 0

            self.setup_exits()
            self.place_elements()
            print(f"Scene initialized: Area {area_id}, Scene {scene_id}")
        except Exception as e:
            print(f"Error in Scene.__init__: {e}")
            raise

    def setup_exits(self):
        print("Setting up exits...")
        try:
            if self.scene_id > 0:
                self.exits["west"] = (self.area_id, self.scene_id - 1)
            if self.scene_id < 4:
                self.exits["east"] = (self.area_id, self.scene_id + 1)
            print(f"Exits set: {self.exits}")
        except Exception as e:
            print(f"Error in Scene.setup_exits: {e}")
            raise

    def place_elements(self):
        print("Placing elements in scene...")
        try:
            for _ in range(random.randint(1, 3)):
                x, y = self.find_open_position()
                token = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                self.tokens.append(token)

            if self.scene_id == 4:
                x, y = self.find_open_position()
                checkpoint = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                self.checkpoints.append(checkpoint)

            if self.area_id == 0 and self.scene_id == 2 and self.vitalik_freed:
                x, y = self.find_open_position()
                self.sword = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            if self.scene_id == 4:
                x, y = self.find_open_position()
                fragment = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                self.fragments.append(fragment)

                # Place a boss at fragment locations
                if self.area_id == 0:
                    self.boss = BossArea1(self)
                elif self.area_id == 1:
                    self.boss = BossArea2(self)
                elif self.area_id == 2:
                    self.boss = BossArea3(self)
                elif self.area_id == 3:
                    self.boss = BossArea4(self)
                elif self.area_id == 4:
                    self.boss = BossArea5(self)
                elif self.area_id == 5:
                    self.boss = Skuld(self)

            start = (self.player.rect.x // TILE_SIZE, (self.player.rect.y - HUD_HEIGHT) // TILE_SIZE)
            for token in self.tokens:
                goal = (token.x // TILE_SIZE, (token.y - HUD_HEIGHT) // TILE_SIZE)
                if not self.is_connected(start, goal):
                    print(f"Carving path to token at {goal}...")
                    self.carve_path(start, goal)
            for checkpoint in self.checkpoints:
                goal = (checkpoint.x // TILE_SIZE, (checkpoint.y - HUD_HEIGHT) // TILE_SIZE)
                if not self.is_connected(start, goal):
                    print(f"Carving path to checkpoint at {goal}...")
                    self.carve_path(start, goal)
            if self.sword:
                goal = (self.sword.x // TILE_SIZE, (self.sword.y - HUD_HEIGHT) // TILE_SIZE)
                if not self.is_connected(start, goal):
                    print(f"Carving path to sword at {goal}...")
                    self.carve_path(start, goal)
            for fragment in self.fragments:
                goal = (fragment.x // TILE_SIZE, (fragment.y - HUD_HEIGHT) // TILE_SIZE)
                if not self.is_connected(start, goal):
                    print(f"Carving path to fragment at {goal}...")
                    self.carve_path(start, goal)
            print("Elements placed successfully.")
        except Exception as e:
            print(f"Error in Scene.place_elements: {e}")
            raise

    def carve_path(self, start, goal):
        x, y = start
        gx, gy = goal
        while (x, y) != (gx, gy):
            if x < gx:
                x += 1
            elif x > gx:
                x -= 1
            if y < gy:
                y += 1
            elif y > gy:
                y -= 1
            self.grid[y][x] = 0

    def is_connected(self, start, goal):
        height = len(self.grid)
        width = len(self.grid[0])
        visited = [[False] * width for _ in range(height)]
        queue = deque([start])
        visited[start[1]][start[0]] = True

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                return True
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if self.grid[ny][nx] == 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((nx, ny))
        return False

    def find_open_position(self):
        print("Finding open position...")
        try:
            max_attempts = 100
            attempt = 0
            while attempt < max_attempts:
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                if self.grid[y][x] == 0:
                    entry_distance = ((x - self.entry[0]) ** 2 + (y - self.entry[1]) ** 2) ** 0.5
                    exit_distance = ((x - self.exit[0]) ** 2 + (y - self.exit[1]) ** 2) ** 0.5
                    if entry_distance > 5 and exit_distance > 5:
                        screen_x = x * TILE_SIZE
                        screen_y = y * TILE_SIZE + HUD_HEIGHT
                        return screen_x, screen_y
                attempt += 1
            print("Warning: Failed to find open position after maximum attempts. Using default (1, 1).")
            return TILE_SIZE, TILE_SIZE + HUD_HEIGHT
        except Exception as e:
            print(f"Error in Scene.find_open_position: {e}")
            raise

    def relocate_sword(self):
        print("Relocating sword...")
        try:
            x, y = self.find_open_position()
            self.sword = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            print("Sword relocated successfully.")
        except Exception as e:
            print(f"Error in Scene.relocate_sword: {e}")
            raise

    def draw(self, screen):
        print("Drawing scene...")
        try:
            # Draw the area-specific background
            screen.blit(self.background, (0, 0))

            if self.tmx_data:
                # Map procedural grid to Tiled tiles
                for y in range(self.height):
                    for x in range(self.width):
                        tile_id = 1 if self.grid[y][x] == 1 else 2  # 1 for wall, 2 for floor (adjust based on your tileset)
                        tile = self.tmx_data.get_tile_image_by_id(tile_id)
                        if tile:
                            screen.blit(tile, (x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT))
            else:
                # Fallback to procedural rendering
                for y in range(self.height):
                    for x in range(self.width):
                        if self.grid[y][x] == 1:
                            screen_y = HUD_HEIGHT + y * TILE_SIZE
                            pygame.draw.rect(screen, (100, 100, 100), (x * TILE_SIZE, screen_y, TILE_SIZE, TILE_SIZE))

            for token in self.tokens:
                pygame.draw.rect(screen, (0, 255, 255), (token.x, token.y, token.width, token.height))
            for checkpoint in self.checkpoints:
                pygame.draw.rect(screen, (0, 255, 0), (checkpoint.x, checkpoint.y, checkpoint.width, checkpoint.height))
            if self.sword:
                pygame.draw.rect(screen, (255, 255, 0), (self.sword.x, self.sword.y, self.sword.width, self.sword.height))
            for fragment in self.fragments:
                pygame.draw.rect(screen, (255, 165, 0), (fragment.x, fragment.y, fragment.width, fragment.height))
            print("Scene drawn successfully.")
        except Exception as e:
            print(f"Error in Scene.draw: {e}")
            raise

class Area:
    def __init__(self, area_id, player, vitalik_freed):
        print(f"Entering Area.__init__ for Area {area_id}...")
        try:
            self.area_id = area_id
            area_names = {
                0: "The Slums of Krypto",
                1: "Seisan Spires",
                2: "Ethereum Chain Ruins",
                3: "Optimism’s Echo",
                4: "MEV Gang Hideout",
                5: "Skuld’s Lair"
            }
            self.name = area_names.get(area_id, f"Unknown Region {area_id}")
            self.scenes = [Scene(area_id, scene_id, player, vitalik_freed) for scene_id in range(5)]
            print(f"Area {area_id} initialized with {len(self.scenes)} scenes.")
        except Exception as e:
            print(f"Error in Area.__init__: {e}")
            raise

class World:
    def __init__(self, player, vitalik_freed=False):
        print("Entering World.__init__...")
        try:
            self.current_area = 0
            self.current_scene = 0
            self.areas = [Area(area_id, player, vitalik_freed) for area_id in range(6)]
            print("World initialized successfully.")
        except Exception as e:
            print(f"Error in World.__init__: {e}")
            raise

    def get_current_scene(self):
        print(f"Getting current scene: Area {self.current_area}, Scene {self.current_scene}")
        try:
            return self.areas[self.current_area].scenes[self.current_scene]
        except Exception as e:
            print(f"Error in World.get_current_scene: {e}")
            raise

    def move_to_scene(self, direction):
        print(f"Moving to scene in direction: {direction}")
        try:
            current_scene = self.get_current_scene()
            if direction in current_scene.exits:
                new_area, new_scene = current_scene.exits[direction]
                self.current_area = new_area
                self.current_scene = new_scene
                print(f"Moved to Area {self.current_area}, Scene {self.current_scene}")
        except Exception as e:
            print(f"Error in World.move_to_scene: {e}")
            raise