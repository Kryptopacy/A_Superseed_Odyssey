import pygame
import random
import math
import os
from src.config import TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT, FPS, SAPA_SPRITE, SPLITTER_SAPA_SPRITE, \
    PROJECTILE_SAPA_SPRITE, CHASER_SAPA_SPRITE, DIAGONAL_SAPA_SPRITE, BOSS_1_SPRITE, BOSS_2_SPRITE, \
    BOSS_3_SPRITE, BOSS_4_SPRITE, BOSS_5_SPRITE, SKULD_SPRITE, HUD_HEIGHT

class Enemy:
    def __init__(self, scene, name, sprite_path, player_level, width=TILE_SIZE, height=TILE_SIZE, speed=2, base_hp=10):
        self.scene = scene
        self.name = name
        self.width = width
        self.height = height
        self.speed = speed
        self.hp = int(base_hp * (1 + player_level * 0.2))
        self.damage = int(2 * (1 + player_level * 0.1))
        self.level = player_level
        self.rect = self.place_in_maze()
        try:
            print(f"Attempting to load sprite from: {sprite_path}")
            if not os.path.exists(sprite_path):
                raise FileNotFoundError(f"File not found: {sprite_path}")
            self.image = pygame.image.load(sprite_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError, Exception) as e:
            print(f"Failed to load sprite {sprite_path}: {e}. Using placeholder.")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((150, 0, 0))
        self.attack_cooldown = 0
        self.attack_cooldown_max = FPS
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.hit_timer = 0
        self.patrol_timer = 0
        self.patrol_interval = FPS * 3

    def place_in_maze(self):
        max_attempts = 100
        attempt = 0
        # Divide the scene into quadrants to ensure distribution
        quadrants = [
            (0, MAZE_WIDTH // 2, 0, MAZE_HEIGHT // 2),  # Top-left
            (MAZE_WIDTH // 2, MAZE_WIDTH, 0, MAZE_HEIGHT // 2),  # Top-right
            (0, MAZE_WIDTH // 2, MAZE_HEIGHT // 2, MAZE_HEIGHT),  # Bottom-left
            (MAZE_WIDTH // 2, MAZE_WIDTH, MAZE_HEIGHT // 2, MAZE_HEIGHT)  # Bottom-right
        ]
        # Choose a quadrant based on the number of Sapas already in each quadrant
        quadrant_counts = [0] * 4
        for sapa in self.scene.sapas:
            for i, (x_min, x_max, y_min, y_max) in enumerate(quadrants):
                if x_min * TILE_SIZE <= sapa.rect.x < x_max * TILE_SIZE and \
                   y_min * TILE_SIZE <= (sapa.rect.y - HUD_HEIGHT) < y_max * TILE_SIZE:
                    quadrant_counts[i] += 1
                    break
        # Prefer the quadrant with the fewest Sapas
        min_count = min(quadrant_counts)
        possible_quadrants = [i for i, count in enumerate(quadrant_counts) if count == min_count]
        chosen_quadrant = random.choice(possible_quadrants)
        x_min, x_max, y_min, y_max = quadrants[chosen_quadrant]

        while attempt < max_attempts:
            x = random.randint(x_min, x_max - 1) * TILE_SIZE
            y = random.randint(y_min, y_max - 1) * TILE_SIZE + HUD_HEIGHT
            rect = pygame.Rect(x, y, self.width, self.height)
            entry_x, entry_y = self.scene.entry
            exit_x, exit_y = self.scene.exit
            entry_distance = ((x - entry_x * TILE_SIZE) ** 2 + (y - (entry_y * TILE_SIZE + HUD_HEIGHT)) ** 2) ** 0.5
            exit_distance = ((x - exit_x * TILE_SIZE) ** 2 + (y - (exit_y * TILE_SIZE + HUD_HEIGHT)) ** 2) ** 0.5
            player_distance = ((x - self.scene.player.rect.x) ** 2 + (y - self.scene.player.rect.y) ** 2) ** 0.5
            too_close_to_sapa = False
            for sapa in self.scene.sapas:
                sapa_distance = ((x - sapa.rect.x) ** 2 + (y - sapa.rect.y) ** 2) ** 0.5
                if sapa_distance < 200:  # Increased minimum distance to 200 pixels
                    too_close_to_sapa = True
                    break
            if (not self.scene.maze.collides(rect) and
                entry_distance > 100 and
                exit_distance > 100 and
                player_distance > 150 and  # Relaxed player distance to ensure placement
                not too_close_to_sapa):
                return rect
            attempt += 1
        # Fallback: Relax constraints if no position found
        attempt = 0
        while attempt < max_attempts:
            x = random.randint(0, MAZE_WIDTH - 1) * TILE_SIZE
            y = random.randint(0, MAZE_HEIGHT - 1) * TILE_SIZE + HUD_HEIGHT
            rect = pygame.Rect(x, y, self.width, self.height)
            if not self.scene.maze.collides(rect):
                return rect
            attempt += 1
        return pygame.Rect(TILE_SIZE, TILE_SIZE + HUD_HEIGHT, self.width, self.height)

    def move(self, maze, player):
        self.patrol_timer += 1
        if self.patrol_timer >= self.patrol_interval:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.patrol_timer = 0

        new_rect = self.rect.copy()
        dx, dy = self.direction
        new_rect.x += dx * self.speed
        new_rect.y += dy * self.speed

        if not maze.collides(new_rect):
            self.rect = new_rect
        else:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.patrol_timer = 0

    def attack(self, player):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return None
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            self.attack_cooldown = self.attack_cooldown_max
        return None

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_timer = 10
        return self.hp <= 0

    def draw(self, screen):
        if self.hit_timer > 0:
            if self.hit_timer % 2 == 0:
                temp_surface = pygame.Surface((self.width, self.height))
                temp_surface.fill((255, 255, 255))
                screen.blit(temp_surface, self.rect)
            else:
                screen.blit(self.image, self.rect)
            self.hit_timer -= 1
        else:
            screen.blit(self.image, self.rect)

class Sapa(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Sapa", SAPA_SPRITE, player_level)

class SplitterSapa(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Splitter Sapa", SPLITTER_SAPA_SPRITE, player_level, base_hp=10)
        self.split_count = 0

    def take_damage(self, damage):
        self.hp -= damage
        self.hit_timer = 10
        if self.hp <= 0 and self.split_count < 2:
            self.split_count += 1
            new_sapa1 = Sapa(self.scene, self.level)
            new_sapa2 = Sapa(self.scene, self.level)
            new_sapa1.rect.x = self.rect.x + TILE_SIZE
            new_sapa1.rect.y = self.rect.y
            new_sapa2.rect.x = self.rect.x - TILE_SIZE
            new_sapa2.rect.y = self.rect.y
            return [new_sapa1, new_sapa2]
        return [] if self.hp <= 0 else None

class ProjectileSapa(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Projectile Sapa", PROJECTILE_SAPA_SPRITE, player_level)
        self.projectile_cooldown = 0
        self.projectile_cooldown_max = FPS * 3

    def attack(self, player):
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1
            return super().attack(player)
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            projectile = pygame.Rect(self.rect.centerx, self.rect.centery, 10, 10)
            self.projectile_cooldown = self.projectile_cooldown_max
            return (projectile, dx, dy)
        return None

class ChaserSapa(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Chaser Sapa", CHASER_SAPA_SPRITE, player_level)

    def move(self, maze, player):
        new_rect = self.rect.copy()
        if player.rect.x > self.rect.x:
            new_rect.x += self.speed
        elif player.rect.x < self.rect.x:
            new_rect.x -= self.speed
        if player.rect.y > self.rect.y:
            new_rect.y += self.speed
        elif player.rect.y < self.rect.y:
            new_rect.y -= self.speed

        if not maze.collides(new_rect):
            self.rect = new_rect
        else:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

class DiagonalSapa(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Diagonal Sapa", DIAGONAL_SAPA_SPRITE, player_level)
        self.direction = random.choice([(1, 1), (-1, -1), (1, -1), (-1, 1)])

    def move(self, maze, player):
        new_rect = self.rect.copy()
        dx, dy = self.direction
        new_rect.x += dx * self.speed
        new_rect.y += dy * self.speed

        if not maze.collides(new_rect):
            self.rect = new_rect
        else:
            self.direction = random.choice([(1, 1), (-1, -1), (1, -1), (-1, 1)])

class BossArea1(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Boss Area 1", BOSS_1_SPRITE, player_level, width=TILE_SIZE * 2, height=TILE_SIZE * 2, speed=2, base_hp=50)
        self.projectile_cooldown = 0
        self.projectile_cooldown_max = FPS * 2

    def attack(self, player):
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1
            return super().attack(player)
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
            projectile = pygame.Rect(self.rect.centerx, self.rect.centery, 15, 15)
            self.projectile_cooldown = self.projectile_cooldown_max
            return (projectile, dx * 2, dy * 2)
        return None

class BossArea2(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Boss Area 2", BOSS_2_SPRITE, player_level, width=TILE_SIZE * 2, height=TILE_SIZE * 2, speed=2, base_hp=50)
        self.sweep_cooldown = 0
        self.sweep_cooldown_max = FPS * 5

    def attack(self, player):
        if self.sweep_cooldown > 0:
            self.sweep_cooldown -= 1
            return super().attack(player)
        sweep_rect = pygame.Rect(self.rect.centerx - 50, self.rect.centery - 50, 100, 100)
        self.sweep_cooldown = self.sweep_cooldown_max
        return (sweep_rect, 0, 0)

class BossArea3(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Boss Area 3", BOSS_3_SPRITE, player_level, width=TILE_SIZE * 2, height=TILE_SIZE * 2, speed=2, base_hp=50)
        self.minion_cooldown = 0
        self.minion_cooldown_max = FPS * 10

    def attack(self, player):
        if self.minion_cooldown > 0:
            self.minion_cooldown -= 1
            return super().attack(player)
        self.minion_cooldown = self.minion_cooldown_max
        minion1 = Sapa(self.scene, self.level)
        minion2 = Sapa(self.scene, self.level)
        minion1.rect.x = self.rect.x + TILE_SIZE * 2
        minion1.rect.y = self.rect.y
        minion2.rect.x = self.rect.x - TILE_SIZE * 2
        minion2.rect.y = self.rect.y
        return [minion1, minion2]

class BossArea4(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Boss Area 4", BOSS_4_SPRITE, player_level, width=TILE_SIZE * 2, height=TILE_SIZE * 2, speed=2, base_hp=50)
        self.dash_cooldown = 0
        self.dash_cooldown_max = FPS * 3
        self.dashing = False

    def move(self, maze, player):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
            if self.dashing:
                new_rect = self.rect.copy()
                dx = (player.rect.x - self.rect.x) / 10
                dy = (player.rect.y - self.rect.y) / 10
                new_rect.x += dx * self.speed * 2
                new_rect.y += dy * self.speed * 2
                if not maze.collides(new_rect):
                    self.rect = new_rect
                self.dashing = False
            else:
                super().move(maze, player)
        else:
            self.dash_cooldown = self.dash_cooldown_max
            self.dashing = True

class BossArea5(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Boss Area 5", BOSS_5_SPRITE, player_level, width=TILE_SIZE * 2, height=TILE_SIZE * 2, speed=2, base_hp=50)
        self.circle_cooldown = 0
        self.circle_cooldown_max = FPS * 4

    def attack(self, player):
        if self.circle_cooldown > 0:
            self.circle_cooldown -= 1
            return super().attack(player)
        projectiles = []
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            projectile = pygame.Rect(self.rect.centerx, self.rect.centery, 10, 10)
            projectiles.append((projectile, dx, dy))
        self.circle_cooldown = self.circle_cooldown_max
        return projectiles

class Skuld(Enemy):
    def __init__(self, scene, player_level):
        super().__init__(scene, "Skuld", SKULD_SPRITE, player_level, width=TILE_SIZE * 3, height=TILE_SIZE * 3, speed=2, base_hp=100)
        self.phase = 1
        self.projectile_cooldown = 0
        self.projectile_cooldown_max = FPS * 2
        self.minion_cooldown = 0
        self.minion_cooldown_max = FPS * 10
        self.sweep_cooldown = 0
        self.sweep_cooldown_max = FPS * 5

    def attack(self, player):
        attacks = []
        if self.hp > 75:
            if self.projectile_cooldown > 0:
                self.projectile_cooldown -= 1
            else:
                dx = player.rect.x - self.rect.x
                dy = player.rect.y - self.rect.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    dx = dx / distance
                    dy = dy / distance
                    projectile = pygame.Rect(self.rect.centerx, self.rect.centery, 15, 15)
                    attacks.append((projectile, dx * 2, dy * 2))
                    self.projectile_cooldown = self.projectile_cooldown_max
        elif self.hp > 50:
            if self.minion_cooldown > 0:
                self.minion_cooldown -= 1
            else:
                minion1 = Sapa(self.scene, self.level)
                minion2 = Sapa(self.scene, self.level)
                minion1.rect.x = self.rect.x + TILE_SIZE * 2
                minion1.rect.y = self.rect.y
                minion2.rect.x = self.rect.x - TILE_SIZE * 2
                minion2.rect.y = self.rect.y
                attacks.extend([minion1, minion2])
                self.minion_cooldown = self.minion_cooldown_max
        else:
            if self.sweep_cooldown > 0:
                self.sweep_cooldown -= 1
            else:
                sweep_rect = pygame.Rect(self.rect.centerx - 50, self.rect.centery - 50, 100, 100)
                attacks.append((sweep_rect, 0, 0))
                self.sweep_cooldown = self.sweep_cooldown_max
        return attacks