# src/modules/npcs.py
import pygame
import random
import sys
import os
from src.config import TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT, FPS, VITALIK_SPRITE, NPC_MALE_SPRITE, NPC_FEMALE_SPRITE ,VENDOR_SPRITE, CRYPTO_SCHOLAR_SPRITE

class NPC:
    def __init__(self, scene, is_vitalik=False, is_vendor=False, is_crypto_scholar=False):
        print("Entering NPC.__init__...")
        try:
            self.scene = scene
            self.is_vitalik = is_vitalik
            self.is_vendor = is_vendor
            self.is_crypto_scholar = is_crypto_scholar
            self.is_freed = False if self.is_vitalik else True
            self.following = False
            self.invulnerable = True
            self.width = TILE_SIZE
            self.height = TILE_SIZE

            # Assign gender for regular NPCs (not Vitalik, vendors, or crypto scholars)
            self.gender = None
            if not self.is_vitalik and not self.is_vendor and not self.is_crypto_scholar:
                self.gender = random.choice(["male", "female"])

            # Determine sprite path based on NPC type and gender
            if self.is_vitalik:
                sprite_path = VITALIK_SPRITE
                fallback_color = (255, 255, 0)  # Yellow for Vitalik
            elif self.is_vendor:
                sprite_path = VENDOR_SPRITE
                fallback_color = (0, 255, 255)  # Cyan for Vendor
            elif self.is_crypto_scholar:
                sprite_path = CRYPTO_SCHOLAR_SPRITE
                fallback_color = (0, 255, 255)  # Cyan for Crypto Scholar
            elif self.gender == "male":
                sprite_path = NPC_MALE_SPRITE
                fallback_color = (0, 255, 255)  # Cyan for Male NPC
            else:  # gender == "female"
                sprite_path = NPC_FEMALE_SPRITE
                fallback_color = (0, 255, 255)  # Cyan for Female NPC

            # Load sprite with fallback
            try:
                print(f"Attempting to load NPC sprite from: {sprite_path}")
                if not os.path.exists(sprite_path):
                    raise FileNotFoundError(f"File not found: {sprite_path}")
                self.image = pygame.image.load(sprite_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except (pygame.error, FileNotFoundError, Exception) as e:
                print(f"Failed to load NPC sprite {sprite_path}: {e}. Using placeholder.")
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(fallback_color)

            self.rect = self.place_in_maze()
            self.vitalik_comment_timer = 0  # Timer for Vitalik's random comments
            self.vitalik_comment_interval = FPS * 30  # Comment every 30 seconds
            self.lore = self.generate_lore()
            self.upgrades = self.generate_upgrades() if self.is_vendor else {}
            print("NPC initialized successfully.")
        except Exception as e:
            print(f"Error in NPC.__init__: {e}")
            raise

    def place_in_maze(self):
        print("Placing NPC in maze...")
        max_attempts = 100
        attempt = 0
        try:
            while attempt < max_attempts:
                # Find a position near a wall to avoid Sapa paths
                x = random.randint(1, MAZE_WIDTH - 2) * TILE_SIZE
                y = random.randint(1, MAZE_HEIGHT - 2) * TILE_SIZE
                rect = pygame.Rect(x, y, self.width, self.height)
                entry_x, entry_y = self.scene.maze.entry
                exit_x, exit_y = self.scene.maze.exit
                entry_distance = ((x - entry_x * TILE_SIZE) ** 2 + (y - entry_y * TILE_SIZE) ** 2) ** 0.5
                exit_distance = ((x - exit_x * TILE_SIZE) ** 2 + (y - exit_y * TILE_SIZE) ** 2) ** 0.5
                # Check if the position is near a wall (at least one adjacent tile is a wall)
                grid_x = x // TILE_SIZE
                grid_y = y // TILE_SIZE
                near_wall = False
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = grid_x + dx, grid_y + dy
                    if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and self.scene.maze.grid[ny][nx] == 1:
                        near_wall = True
                        break
                if (not self.scene.maze.collides(rect) and
                    entry_distance > 100 and
                    exit_distance > 100 and
                    near_wall):
                    player_x, player_y = self.scene.player.rect.x, self.scene.player.rect.y
                    player_distance = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
                    if player_distance > 200:  # Ensure NPC spawns at least 200 pixels away from player
                        print("NPC placed successfully.")
                        return rect
                attempt += 1
            print("Warning: Failed to place NPC after maximum attempts. Placing at default position (1, 1).")
            return pygame.Rect(TILE_SIZE, TILE_SIZE, self.width, self.height)
        except Exception as e:
            print(f"Error in NPC.place_in_maze: {e}")
            raise

    def follow_player(self, player, dialogue_box):
        print("Entering NPC.follow_player...")
        try:
            if not self.following or not self.is_freed or not self.is_vitalik:
                return

            # Move towards the player at a slower speed
            speed = 2
            new_rect = self.rect.copy()
            if player.rect.x > self.rect.x + TILE_SIZE:
                new_rect.x += speed
            elif player.rect.x < self.rect.x - TILE_SIZE:
                new_rect.x -= speed
            if player.rect.y > self.rect.y + TILE_SIZE:
                new_rect.y += speed
            elif player.rect.y < self.rect.y - TILE_SIZE:
                new_rect.y -= speed

            if not self.scene.maze.collides(new_rect):
                self.rect = new_rect

            # Vitalik occasionally shares lore-based facts
            if self.is_vitalik and self.following:
                self.vitalik_comment_timer += 1
                if self.vitalik_comment_timer >= self.vitalik_comment_interval:
                    vitalik_facts = [
                        f"The Superseed wasn’t just a source of light—it was Krypto’s heart, binding all life together.",
                        f"Skuld wasn’t always evil; he was once a guardian, corrupted by his own ambition.",
                        f"Skuld’s fall began when he sought immortality, a gift the Superseed could never grant.",
                        f"The people of KRYPTO that the ElPee, live and die protecting, disregarded them as a myth. Skuld was fed up",
                        f"The ElPee’s final stand at Seisan Spires was a tragedy—the entire clan fell to protect the fragments.",
                        f"Krypto’s slums were once a thriving market, before the Sapa curse turned it into a wasteland.",
                        f"The Sword of Solvency was forged by the ElPee to channel the Superseed’s power against Seisan."
                    ]
                    dialogue_box.show([random.choice(vitalik_facts), "Press SPACE to continue, or ESC to close."])
                    self.vitalik_comment_timer = 0
        except Exception as e:
            print(f"Error in NPC.follow_player: {e}")
            raise

    def generate_lore(self):
        print("Generating lore for NPC...")
        try:
            if self.is_vendor:
                return [
                    "Welcome to my shop, traveler!",
                    "I’ve got some upgrades that might help you on your journey."
                ]

            if self.is_crypto_scholar:
                crypto_facts = [
                    "The Superseed Protocol is an Ethereum L2 built on the OP Stack.",
                    "SuperCDP allows users to mint stablecoins with overcollateralized assets.",
                    "Proof-of-Repayment distributes tokens daily to repay Supercollateral loans.",
                    "Supercollateral users need a 500% collateralization ratio for interest-free loans.",
                    "The Superseed Stablecoin maintains a peg through overcollateralization.",
                    "Dynamic Repayment Vaults stabilize the repayment rate for Supercollateral users."
                ]
                return [random.choice(crypto_facts)]
            else:
                npc_facts = [
                    "My cousin in the MEV gang turned into a Sapa overnight—it was horrifying! I hated him but still sad",
                    "They say the ElPee fought bravely at Seisan Spires, but I don’t believe they ever existed.",
                    "I found a fragment once—it hummed softly, but I was too scared to keep it.",
                    "I heard Skuld used to be human, you know? Now he’s the Debt King, ruling over our misery.",
                    "The Sapa-curse started in the slums—I’ve seen people change with my own eyes.",
                    "I heard the ElPee trained their minds and bodies to fight Seisan, but it was all for nothing.",
                    "They say Krypto was once a paradise, but now it’s just darkness and despair"
                ]
                return [random.choice(npc_facts)]
        except Exception as e:
            print(f"Error in generate_lore: {e}")
            raise

    def generate_upgrades(self):
        return {
            "Optimism Ring Fill Rate": {"description": "Increase Optimism Ring fill rate by 0.1%", "cost": 10, "value": 0.1},
            "Attack Power": {"description": "Increase attack power by 2", "cost": 15, "value": 2},
            "Ranged Attacks": {"description": "Add 3 ranged attacks", "cost": 20, "value": 3}
        }

    def draw(self, screen):
        print("Entering NPC.draw...")
        try:
            # Draw Vitalik even if not freed; other NPCs are always drawn
            screen.blit(self.image, self.rect)
            print("NPC drawn successfully.")
        except Exception as e:
            print(f"Error in NPC.draw: {e}")
            raise

def vitalik_cutscene(screen, clock, player, dialogue_box, ui_background):
    print("Entering vitalik_cutscene...")
    pronoun = "he" if player.gender == "male" else "she"
    lines = [
        f"Vitalik: I am Sage Vitalik, trapped by the Sapa curse.",
        f"You, {player.name}, have been bitten—your time is short.",
        f"The Sword of Solvency can halt the curse, but only the Superseed fragments can cure {pronoun}.",
        "Complete a trial to free me, and I’ll guide you. Press SPACE to continue, or ESC to close."
    ]
    dialogue_box.show(lines)
    running = True

    while running and dialogue_box.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in vitalik_cutscene.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dialogue_box.next_line()
                elif event.key == pygame.K_ESCAPE:
                    print("Vitalik cutscene skipped by user.")
                    return False

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    print("Exiting vitalik_cutscene...")
    return True

def vitalik_choice(screen, clock, player, dialogue_box, ui_background):
    print("Entering vitalik_choice...")
    lines = [
        f"Vitalik: You’ve braved many dangers to claim the Sword of Solvency, {player.name}.",
        "Now, a choice lies before you.",
        "Will you use its power to save yourself, or risk everything to save Krypto?",
        "Press Y to save yourself, N to save Krypto. You must choose to proceed."
    ]
    dialogue_box.show(lines)
    choice = None

    while choice is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in vitalik_choice.")
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and dialogue_box.active:
                    dialogue_box.next_line()
                elif event.key == pygame.K_y and not dialogue_box.active:
                    choice = "self"
                elif event.key == pygame.K_n and not dialogue_box.active:
                    choice = "world"

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    print(f"Vitalik choice made: {choice}")
    return choice