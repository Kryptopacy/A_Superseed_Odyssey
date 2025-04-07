# src/modules/player.py
import pygame
import random
from src.config import TILE_SIZE, PLAYER_SPEED, CRITICAL_TINT, FPS
from src.modules.inventory import Inventory

class Player:
    def __init__(self, x, y, name, gender, sprite):
        print("Entering Player.__init__...")
        try:
            self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            self.name = name
            self.gender = gender
            self.sprite = sprite
            self.hp = 100
            self.infection_level = 50
            self.inventory = Inventory()
            self.ranged_attacks = 0
            self.attack_power = 10
            self.optimism_ring_duration = 5
            self.optimism_ring_timer = 0
            self.facing_right = True
            self.easy_mode = False
            self.shake_timer = 0  # For hit indication
            self.shake_offset = (0, 0)  # Offset for shaking
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
        self.hp -= amount
        self.shake_timer = 20  # Increased to 20 frames for more noticeable effect

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
            if self.optimism_ring_timer > 0:
                pygame.draw.circle(screen, (255, 255, 0), (self.rect.centerx + self.shake_offset[0], self.rect.centery + self.shake_offset[1]), 40, 2)
            print("Player drawn successfully.")
        except Exception as e:
            print(f"Error in Player.draw: {e}")
            raise

    def update(self):
        print("Entering Player.update...")
        try:
            if self.optimism_ring_timer > 0:
                self.optimism_ring_timer -= 1
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
            if self.optimism_ring_timer <= 0:
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