# src/modules/player.py
import pygame
import random
import os
from src.config import TILE_SIZE, PLAYER_SPEED, CRITICAL_TINT, FPS, HUD_HEIGHT, OPTIMISM_RING_EFFECT
from src.modules.inventory import Inventory

class Player:
    def __init__(self, x, y, name, gender, sprite):
        print("Entering Player.__init__...")
        try:
            self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            self.name = name
            self.gender = gender
            self.sprite = sprite
            self.max_hp = 100
            self.hp = self.max_hp
            self.infection_level = 50
            self.inventory = Inventory()
            self.ranged_attacks = 0
            self.attack_power = 2
            self.level = 1
            self.xp = 0
            self.xp_to_next_level = 10
            self.optimism_ring_fill = 0  # Percentage (0-100)
            self.optimism_ring_fill_rate = 1.0  # 1% per second at level 1
            self.optimism_ring_duration = 5  # Seconds at level 1
            self.optimism_ring_cooldown = 0  # Seconds remaining
            self.optimism_ring_cooldown_max = 60  # 60 seconds cooldown
            self.optimism_ring_active = False
            self.optimism_ring_timer = 0  # Frames remaining for active effect
            self.facing_right = True
            self.easy_mode = False
            self.shake_timer = 0  # For hit indication
            self.shake_offset = (0, 0)  # Offset for shaking
            self.world_choice_made = False  # Track if the player chose the "world" path

            # Load Optimism Ring effect sprite
            self.optimism_ring_sprite = None
            try:
                print(f"Attempting to load Optimism Ring effect sprite from: {OPTIMISM_RING_EFFECT}")
                if not os.path.exists(OPTIMISM_RING_EFFECT):
                    raise FileNotFoundError(f"File not found: {OPTIMISM_RING_EFFECT}")
                self.optimism_ring_sprite = pygame.image.load(OPTIMISM_RING_EFFECT).convert_alpha()
                self.optimism_ring_sprite = pygame.transform.scale(self.optimism_ring_sprite, (80, 80))  # Larger than player sprite to encompass
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load Optimism Ring effect sprite at {OPTIMISM_RING_EFFECT}. Error: {e}. Using placeholder.")
                self.optimism_ring_sprite = None

            print("Player initialized successfully.")
        except Exception as e:
            print(f"Error in Player.__init__: {e}")
            raise

    def move(self, keys, maze):
        print("Entering Player.move...")
        try:
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx -= PLAYER_SPEED
                self.facing_right = False
            if keys[pygame.K_RIGHT]:
                dx += PLAYER_SPEED
                self.facing_right = True
            if keys[pygame.K_UP]:
                dy -= PLAYER_SPEED
            if keys[pygame.K_DOWN]:
                dy += PLAYER_SPEED

            new_rect = self.rect.copy()
            new_rect.x += dx
            if not maze.collides(new_rect):
                self.rect.x = new_rect.x

            new_rect = self.rect.copy()
            new_rect.y += dy
            if not maze.collides(new_rect):
                self.rect.y = new_rect.y

            print("Player moved successfully.")
        except Exception as e:
            print(f"Error in Player.move: {e}")
            raise

    def take_damage(self, amount):
        if self.optimism_ring_active:
            print("Player is invincible due to Optimism Ring!")
            return
        self.hp -= amount
        self.shake_timer = 20  # Increased to 20 frames for more noticeable effect
        if self.hp < 0:
            self.hp = 0

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)  # Increase XP needed for next level
        self.max_hp += 10
        self.hp = self.max_hp  # Restore HP on level up
        self.attack_power += 2
        self.optimism_ring_duration = min(10, self.optimism_ring_duration + 1)  # Cap at 10 seconds
        print(f"Player leveled up to level {self.level}! HP: {self.max_hp}, Attack Power: {self.attack_power}, Optimism Ring Duration: {self.optimism_ring_duration}s")

    def draw(self, screen):
        print("Entering Player.draw...")
        try:
            # Apply shake effect if active
            if self.shake_timer > 0:
                self.shake_offset = (random.randint(-2, 2), random.randint(-2, 2))
                self.shake_timer -= 1
            else:
                self.shake_offset = (0, 0)

            # Draw sprite with shake offset
            draw_pos = (self.rect.x + self.shake_offset[0], self.rect.y + self.shake_offset[1])
            screen.blit(self.sprite, draw_pos)

            # Draw Optimism Ring effect if active
            if self.optimism_ring_active:
                if self.optimism_ring_sprite:
                    # Calculate pulsing alpha (128 to 255)
                    alpha = int(128 + 127 * (pygame.time.get_ticks() % 1000) / 1000)  # Oscillates every second
                    effect_surface = self.optimism_ring_sprite.copy()
                    effect_surface.set_alpha(alpha)
                    # Center the effect on the player
                    sprite_pos = (
                    self.rect.centerx - 40 + self.shake_offset[0], self.rect.centery - 40 + self.shake_offset[1])
                    screen.blit(effect_surface, sprite_pos)
                else:
                    # Fallback: Draw a pulsing circle
                    alpha = int(128 + 127 * (pygame.time.get_ticks() % 1000) / 1000)
                    circle_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
                    pygame.draw.circle(circle_surface, (255, 255, 0, alpha), (40, 40), 40, 2)
                    screen.blit(circle_surface, (
                    self.rect.centerx - 40 + self.shake_offset[0], self.rect.centery - 40 + self.shake_offset[1]))
            print("Player drawn successfully.")
        except Exception as e:
            print(f"Error in Player.draw: {e}")
            raise

    def update(self):
        print("Entering Player.update...")
        try:
            # Update Optimism Ring fill
            if not self.optimism_ring_active and self.optimism_ring_cooldown <= 0:
                self.optimism_ring_fill = min(100, self.optimism_ring_fill + self.optimism_ring_fill_rate / FPS)
            elif self.optimism_ring_cooldown > 0:
                self.optimism_ring_cooldown -= 1 / FPS

            # Update Optimism Ring active timer
            if self.optimism_ring_active:
                self.optimism_ring_timer -= 1
                if self.optimism_ring_timer <= 0:
                    self.optimism_ring_active = False
                    self.optimism_ring_fill = 0
                    self.optimism_ring_cooldown = self.optimism_ring_cooldown_max

            print("Player updated successfully.")
        except Exception as e:
            print(f"Error in Player.update: {e}")
            raise

    def update_infection(self, increment):
        print("Entering Player.update_infection...")
        try:
            if self.inventory.has_sword:
                increment = 0
            self.infection_level += increment
            if self.infection_level >= 100:
                print("Infection level reached 100%. Game over.")
                return True
            if self.infection_level < 0:
                self.infection_level = 0
            print(f"Infection level updated to: {self.infection_level}")
            return False
        except Exception as e:
            print(f"Error in Player.update_infection: {e}")
            raise

    def collect_fragment(self):
        print("Entering Player.collect_fragment...")
        try:
            self.inventory.add_fragment()
            if self.inventory.fragments == 1:
                self.infection_level = 0
            print(f"Fragment collected. Total fragments: {self.inventory.fragments}")
        except Exception as e:
            print(f"Error in Player.collect_fragment: {e}")
            raise

    def activate_optimism_ring(self):
        print("Entering Player.activate_optimism_ring...")
        try:
            if self.optimism_ring_fill >= 100 and not self.optimism_ring_active and self.optimism_ring_cooldown <= 0:
                self.optimism_ring_active = True
                self.optimism_ring_timer = self.optimism_ring_duration * FPS
                print("Optimism Ring activated.")
        except Exception as e:
            print(f"Error in Player.activate_optimism_ring: {e}")
            raise

    def lose_sword(self):
        print("Entering Player.lose_sword...")
        try:
            self.inventory.remove_sword()
            print("Sword lost.")
        except Exception as e:
            print(f"Error in Player.lose_sword: {e}")
            raise