# src/modules/world.py
import pygame
import random
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT, \
    AREA_0_BACKGROUND, AREA_1_BACKGROUND, AREA_2_BACKGROUND, AREA_3_BACKGROUND, AREA_4_BACKGROUND, AREA_5_BACKGROUND, \
    HUD_HEIGHT, AREA_0_FLOOR, AREA_0_WALL, AREA_1_FLOOR, AREA_1_WALL, AREA_2_FLOOR, AREA_2_WALL, \
    AREA_3_FLOOR, AREA_3_WALL, AREA_4_FLOOR, AREA_4_WALL, AREA_5_FLOOR, AREA_5_WALL, \
    SWORD_SPRITE, TOKEN_SPRITE, CHECKPOINT_SPRITE, FRAGMENT_SPRITE
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

        # Ensure entry and exit are at least 10 tiles apart
        max_attempts = 100
        attempt = 0
        while attempt < max_attempts:
            distance = ((entry[0] - exit_[0]) ** 2 + (entry[1] - exit_[1]) ** 2) ** 0.5
            if distance >= 10:  # Minimum distance of 10 tiles
                break
            # If too close, re-pick the exit
            exit_side = random.choice([s for s in sides if s != entry_side])
            exit_ = pick_opening(exit_side)
            attempt += 1

        if attempt >= max_attempts:
            print("Warning: Could not place entry and exit 10 tiles apart after maximum attempts. Using last positions.")

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
            playable_height = SCREEN_HEIGHT - HUD_HEIGHT
            tile_height = playable_height / self.height
            top_left_x = rect.x // TILE_SIZE
            top_left_y = max(0, min((rect.y - HUD_HEIGHT) // tile_height, self.height - 1))
            bottom_right_x = (rect.x + rect.width - 1) // TILE_SIZE
            bottom_right_y = max(0, min((rect.y + rect.height - 1 - HUD_HEIGHT) // tile_height, self.height - 1))

            for y in range(max(0, int(top_left_y)), min(self.height, int(bottom_right_y) + 1)):
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
            self.sword_sprite = None
            self.token_sprite = None
            self.checkpoint_sprite = None
            self.fragment_sprite = None
            self.boss = None
            self.exits = {}
            self.vitalik_freed = vitalik_freed

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

            # Generate random maze with fewer obstacles for boss scenes (Scene 4)
            if self.scene_id == 4:  # Boss scene
                self.maze = Maze(num_crosses=2)  # Fewer obstacles for boss fights
            else:
                self.maze = Maze()
            self.grid = self.maze.grid
            self.width = self.maze.width
            self.height = self.maze.height
            self.entry = self.maze.entry
            self.exit = self.maze.exit

            # Load area-specific floor and wall PNGs
            floor_paths = {
                0: AREA_0_FLOOR,
                1: AREA_1_FLOOR,
                2: AREA_2_FLOOR,
                3: AREA_3_FLOOR,
                4: AREA_4_FLOOR,
                5: AREA_5_FLOOR
            }
            wall_paths = {
                0: AREA_0_WALL,
                1: AREA_1_WALL,
                2: AREA_2_WALL,
                3: AREA_3_WALL,
                4: AREA_4_WALL,
                5: AREA_5_WALL
            }
            floor_path = floor_paths.get(area_id, None)
            wall_path = wall_paths.get(area_id, None)
            self.wall_tile = None
            self.floor_tile = None
            try:
                print(f"Attempting to load floor tile from: {floor_path}")
                if not os.path.exists(floor_path):
                    raise FileNotFoundError(f"File not found: {floor_path}")
                self.floor_tile = pygame.image.load(floor_path).convert_alpha()
                self.floor_tile = pygame.transform.scale(self.floor_tile, (TILE_SIZE, TILE_SIZE))

                print(f"Attempting to load wall tile from: {wall_path}")
                if not os.path.exists(wall_path):
                    raise FileNotFoundError(f"File not found: {wall_path}")
                self.wall_tile = pygame.image.load(wall_path).convert_alpha()
                self.wall_tile = pygame.transform.scale(self.wall_tile, (TILE_SIZE, TILE_SIZE))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load floor/wall tiles: {e}. Will use procedural rendering.")

            # Load sprites for sword, tokens, checkpoints, fragments
            try:
                print(f"Attempting to load sword sprite from: {SWORD_SPRITE}")
                if not os.path.exists(SWORD_SPRITE):
                    raise FileNotFoundError(f"File not found: {SWORD_SPRITE}")
                self.sword_sprite = pygame.image.load(SWORD_SPRITE).convert_alpha()
                self.sword_sprite = pygame.transform.scale(self.sword_sprite, (TILE_SIZE, TILE_SIZE))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load sword sprite at {SWORD_SPRITE}. Error: {e}. Using placeholder.")
                self.sword_sprite = None

            try:
                print(f"Attempting to load token sprite from: {TOKEN_SPRITE}")
                if not os.path.exists(TOKEN_SPRITE):
                    raise FileNotFoundError(f"File not found: {TOKEN_SPRITE}")
                self.token_sprite = pygame.image.load(TOKEN_SPRITE).convert_alpha()
                self.token_sprite = pygame.transform.scale(self.token_sprite, (TILE_SIZE, TILE_SIZE))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load token sprite at {TOKEN_SPRITE}. Error: {e}. Using placeholder.")
                self.token_sprite = None

            try:
                print(f"Attempting to load checkpoint sprite from: {CHECKPOINT_SPRITE}")
                if not os.path.exists(CHECKPOINT_SPRITE):
                    raise FileNotFoundError(f"File not found: {CHECKPOINT_SPRITE}")
                self.checkpoint_sprite = pygame.image.load(CHECKPOINT_SPRITE).convert_alpha()
                self.checkpoint_sprite = pygame.transform.scale(self.checkpoint_sprite, (TILE_SIZE, TILE_SIZE))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load checkpoint sprite at {CHECKPOINT_SPRITE}. Error: {e}. Using placeholder.")
                self.checkpoint_sprite = None

            try:
                print(f"Attempting to load fragment sprite from: {FRAGMENT_SPRITE}")
                if not os.path.exists(FRAGMENT_SPRITE):
                    raise FileNotFoundError(f"File not found: {FRAGMENT_SPRITE}")
                self.fragment_sprite = pygame.image.load(FRAGMENT_SPRITE).convert_alpha()
                self.fragment_sprite = pygame.transform.scale(self.fragment_sprite, (TILE_SIZE, TILE_SIZE))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load fragment sprite at {FRAGMENT_SPRITE}. Error: {e}. Using placeholder.")
                self.fragment_sprite = None

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

            # Only place the sword in Area 0, Scene 4 if the player doesn't have it
            if self.area_id == 0 and self.scene_id == 4 and not self.player.inventory.has_sword:
                x, y = self.find_open_position()
                self.sword = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            if self.scene_id == 4:
                x, y = self.find_open_position()
                fragment = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                self.fragments.append(fragment)

                # Place a boss at fragment locations, passing player.level
                if self.area_id == 0:
                    self.boss = BossArea1(self, self.player.level)
                elif self.area_id == 1:
                    self.boss = BossArea2(self, self.player.level)
                elif self.area_id == 2:
                    self.boss = BossArea3(self, self.player.level)
                elif self.area_id == 3:
                    self.boss = BossArea4(self, self.player.level)
                elif self.area_id == 4:
                    self.boss = BossArea5(self, self.player.level)
                elif self.area_id == 5:
                    self.boss = Skuld(self, self.player.level)

            # Ensure start and goal positions are within grid bounds
            start_x = max(0, min(self.player.rect.x // TILE_SIZE, self.width - 1))
            start_y = max(0, min((self.player.rect.y - HUD_HEIGHT) // TILE_SIZE, self.height - 1))
            start = (start_x, start_y)

            for token in self.tokens:
                goal_x = max(0, min(token.x // TILE_SIZE, self.width - 1))
                goal_y = max(0, min((token.y - HUD_HEIGHT) // TILE_SIZE, self.height - 1))
                goal = (goal_x, goal_y)
                if not self.is_connected(start, goal):
                    print(f"Carving path to token at {goal}...")
                    self.carve_path(start, goal)
            for checkpoint in self.checkpoints:
                goal_x = max(0, min(checkpoint.x // TILE_SIZE, self.width - 1))
                goal_y = max(0, min((checkpoint.y - HUD_HEIGHT) // TILE_SIZE, self.height - 1))
                goal = (goal_x, goal_y)
                if not self.is_connected(start, goal):
                    print(f"Carving path to checkpoint at {goal}...")
                    self.carve_path(start, goal)
            if self.sword:
                goal_x = max(0, min(self.sword.x // TILE_SIZE, self.width - 1))
                goal_y = max(0, min((self.sword.y - HUD_HEIGHT) // TILE_SIZE, self.height - 1))
                goal = (goal_x, goal_y)
                if not self.is_connected(start, goal):
                    print(f"Carving path to sword at {goal}...")
                    self.carve_path(start, goal)
            for fragment in self.fragments:
                goal_x = max(0, min(fragment.x // TILE_SIZE, self.width - 1))
                goal_y = max(0, min((fragment.y - HUD_HEIGHT) // TILE_SIZE, self.height - 1))
                goal = (goal_x, goal_y)
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
            # Only relocate the sword if the player doesn't have it
            if not self.player.inventory.has_sword:
                x, y = self.find_open_position()
                self.sword = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                print("Sword relocated successfully.")
            else:
                print("Player already has the sword; not relocating.")
        except Exception as e:
            print(f"Error in Scene.relocate_sword: {e}")
            raise

    def draw(self, screen):
        print("Drawing scene...")
        try:
            # Draw the area-specific background
            screen.blit(self.background, (0, 0))

            # Calculate the playable area height (excluding HUD)
            playable_height = SCREEN_HEIGHT - HUD_HEIGHT
            # Calculate a scaling factor to fit the maze height within the playable area
            tile_height = playable_height / self.height

            # Draw the maze using floor and wall tiles
            if self.wall_tile and self.floor_tile:
                for y in range(self.height):
                    # Calculate screen_y to fit within the playable area (HUD_HEIGHT to SCREEN_HEIGHT)
                    screen_y = HUD_HEIGHT + y * tile_height
                    for x in range(self.width):
                        if self.grid[y][x] == 1:
                            # Scale the wall tile to the calculated tile_height
                            scaled_wall = pygame.transform.scale(self.wall_tile, (TILE_SIZE, int(tile_height)))
                            screen.blit(scaled_wall, (x * TILE_SIZE, int(screen_y)))
                        else:
                            # Scale the floor tile to the calculated tile_height
                            scaled_floor = pygame.transform.scale(self.floor_tile, (TILE_SIZE, int(tile_height)))
                            screen.blit(scaled_floor, (x * TILE_SIZE, int(screen_y)))
            else:
                # Fallback to procedural rendering
                for y in range(self.height):
                    screen_y = HUD_HEIGHT + y * tile_height
                    for x in range(self.width):
                        if self.grid[y][x] == 1:
                            pygame.draw.rect(screen, (100, 100, 100),
                                             (x * TILE_SIZE, int(screen_y), TILE_SIZE, int(tile_height)))

            # Draw tokens, checkpoints, sword, and fragments with sprites
            for token in self.tokens:
                if self.token_sprite:
                    screen.blit(self.token_sprite, (token.x, token.y))
                else:
                    pygame.draw.rect(screen, (0, 255, 255), (token.x, token.y, token.width, token.height))
            for checkpoint in self.checkpoints:
                if self.checkpoint_sprite:
                    screen.blit(self.checkpoint_sprite, (checkpoint.x, checkpoint.y))
                else:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (checkpoint.x, checkpoint.y, checkpoint.width, checkpoint.height))
            if self.sword:
                if self.sword_sprite:
                    screen.blit(self.sword_sprite, (self.sword.x, self.sword.y))
                else:
                    pygame.draw.rect(screen, (255, 255, 0),
                                     (self.sword.x, self.sword.y, self.sword.width, self.sword.height))
            for fragment in self.fragments:
                if self.fragment_sprite:
                    screen.blit(self.fragment_sprite, (fragment.x, fragment.y))
                else:
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