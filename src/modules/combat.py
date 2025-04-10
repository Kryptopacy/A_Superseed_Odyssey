# src/modules/combat.py
import pygame
import os
from src.config import TILE_SIZE, FPS, MELEE_ATTACK_SPRITE, RANGED_ATTACK_SPRITE, SOUND_ENEMY_HIT
from src.modules.enemies import SplitterSapa

class CombatSystem:
    def __init__(self):
        print("Entering CombatSystem.__init__...")
        try:
            self.attacks = []
            self.hit_effects = []
            # Load attack sprites
            self.melee_attack_sprite = None
            self.ranged_attack_sprite = None
            try:
                print(f"Attempting to load melee attack sprite from: {MELEE_ATTACK_SPRITE}")
                if not os.path.exists(MELEE_ATTACK_SPRITE):
                    raise FileNotFoundError(f"File not found: {MELEE_ATTACK_SPRITE}")
                self.melee_attack_sprite = pygame.image.load(MELEE_ATTACK_SPRITE).convert_alpha()
                self.melee_attack_sprite = pygame.transform.scale(self.melee_attack_sprite, (TILE_SIZE, TILE_SIZE))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load melee attack sprite: {e}. Using placeholder.")
                self.melee_attack_sprite = None

            try:
                print(f"Attempting to load ranged attack sprite from: {RANGED_ATTACK_SPRITE}")
                if not os.path.exists(RANGED_ATTACK_SPRITE):
                    raise FileNotFoundError(f"File not found: {RANGED_ATTACK_SPRITE}")
                self.ranged_attack_sprite = pygame.image.load(RANGED_ATTACK_SPRITE).convert_alpha()
                self.ranged_attack_sprite = pygame.transform.scale(self.ranged_attack_sprite, (10, 10))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load ranged attack sprite: {e}. Using placeholder.")
                self.ranged_attack_sprite = None

            print("CombatSystem initialized successfully.")
        except Exception as e:
            print(f"Error in CombatSystem.__init__: {e}")
            raise

    def melee_attack(self, player):
        print("Entering CombatSystem.melee_attack...")
        try:
            if player.inventory.has_sword:  # Ensure melee attack only works with the sword
                attack_rect = pygame.Rect(
                    player.rect.x + player.rect.width if player.facing_right else player.rect.x - TILE_SIZE,
                    player.rect.y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                self.attacks.append(Attack(attack_rect, player.attack_power, player.facing_right, lifetime=5, sprite=self.melee_attack_sprite))
                print("Melee attack initiated.")
            else:
                print("Melee attack failed: Player does not have the sword.")
        except Exception as e:
            print(f"Error in CombatSystem.melee_attack: {e}")
            raise

    def ranged_attack(self, player):
        print("Entering CombatSystem.ranged_attack...")
        try:
            if player.inventory.has_sword and player.ranged_attacks > 0:  # Ensure ranged attack only works with the sword
                dx = 1 if player.facing_right else -1
                attack_rect = pygame.Rect(player.rect.centerx, player.rect.centery, 10, 10)
                self.attacks.append(Attack(attack_rect, player.attack_power, player.facing_right, dx=dx * 10, lifetime=50, sprite=self.ranged_attack_sprite))
                print("Ranged attack initiated.")
            else:
                print("Ranged attack failed: Player does not have the sword or has no ranged attacks remaining.")
        except Exception as e:
            print(f"Error in CombatSystem.ranged_attack: {e}")
            raise

    def update(self, enemies, player):
        print("Entering CombatSystem.update...")
        try:
            # Update attacks
            for attack in self.attacks[:]:
                attack.update()
                for enemy in enemies[:]:
                    if attack.rect.colliderect(enemy.rect):
                        result = enemy.take_damage(attack.power)
                        if isinstance(result, list):
                            enemies.extend(result)
                            enemies.remove(enemy)
                        elif result:
                            enemies.remove(enemy)
                            player.gain_xp(5)  # Gain XP for defeating an enemy
                        self.hit_effects.append(HitEffect(enemy.rect.centerx, enemy.rect.centery))
                        self.attacks.remove(attack)
                        break
                if attack.lifetime <= 0:
                    self.attacks.remove(attack)

            # Update hit effects
            for effect in self.hit_effects[:]:
                effect.update()
                if effect.lifetime <= 0:
                    self.hit_effects.remove(effect)
            print("CombatSystem updated successfully.")
        except Exception as e:
            print(f"Error in CombatSystem.update: {e}")
            raise

    def draw(self, screen):
        print("Entering CombatSystem.draw...")
        try:
            for attack in self.attacks:
                attack.draw(screen)
            for effect in self.hit_effects:
                effect.draw(screen)
            print("CombatSystem drawn successfully.")
        except Exception as e:
            print(f"Error in CombatSystem.draw: {e}")
            raise

class Attack:
    def __init__(self, rect, power, facing_right, dx=0, lifetime=10, sprite=None):
        print("Entering Attack.__init__...")
        try:
            self.rect = rect
            self.power = power
            self.dx = dx
            self.lifetime = lifetime if dx == 0 else 50  # Melee attacks last shorter than ranged
            self.sprite = sprite
            self.color = (255, 255, 255) if dx == 0 else (255, 255, 0)  # White for melee, yellow for ranged
            print("Attack initialized successfully.")
        except Exception as e:
            print(f"Error in Attack.__init__: {e}")
            raise

    def update(self):
        print("Entering Attack.update...")
        try:
            self.rect.x += self.dx
            self.lifetime -= 1
            print(f"Attack updated: Lifetime remaining: {self.lifetime}")
        except Exception as e:
            print(f"Error in Attack.update: {e}")
            raise

    def draw(self, screen):
        print("Entering Attack.draw...")
        try:
            if self.sprite:
                screen.blit(self.sprite, (self.rect.x, self.rect.y))
            else:
                pygame.draw.rect(screen, self.color, self.rect)
            print("Attack drawn successfully.")
        except Exception as e:
            print(f"Error in Attack.draw: {e}")
            raise

class HitEffect:
    def __init__(self, x, y):
        print("Entering HitEffect.__init__...")
        try:
            self.x = x
            self.y = y
            self.lifetime = 10
            self.color = (255, 0, 0)
            print("HitEffect initialized successfully.")
        except Exception as e:
            print(f"Error in HitEffect.__init__: {e}")
            raise

    def update(self):
        print("Entering HitEffect.update...")
        try:
            self.lifetime -= 1
            print(f"HitEffect updated: Lifetime remaining: {self.lifetime}")
        except Exception as e:
            print(f"Error in HitEffect.update: {e}")
            raise

    def draw(self, screen):
        print("Entering HitEffect.draw...")
        try:
            if self.lifetime > 0:
                alpha = int(255 * (self.lifetime / 10))
                surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(surface, (self.color[0], self.color[1], self.color[2], alpha), (10, 10), 10)
                screen.blit(surface, (self.x - 10, self.y - 10))
            print("HitEffect drawn successfully.")
        except Exception as e:
            print(f"Error in HitEffect.draw: {e}")
            raise