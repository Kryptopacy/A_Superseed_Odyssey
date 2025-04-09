# src/main.py
import pygame
import sys
import random
import os
from src.modules.player import Player
from src.modules.cutscenes import play_intro_cutscene, play_area_cutscene
from src.modules.checkpoint import CheckpointSystem
from src.modules.enemies import Sapa, SplitterSapa, ProjectileSapa, ChaserSapa, DiagonalSapa, BossArea1, BossArea2, \
    BossArea3, BossArea4, BossArea5, Skuld
from src.modules.combat import CombatSystem
from src.modules.npcs import NPC, vitalik_cutscene, vitalik_choice
from src.modules.minigames.hash_dash import play_hash_dash
from src.modules.minigames.collateral_lock import play_collateral_lock
from src.modules.minigames.gas_fee_gauntlet import play_gas_fee_gauntlet
from src.modules.minigames.anagram import play_anagram
from src.modules.minigames.memory_sequence import play_memory_sequence
from src.modules.minigames.color_match import play_color_match
from src.modules.ui import DialogueBox, show_tutorial, show_pause_menu, prompt_easy_mode
from src.modules.world import World
from src.modules.game_state import save_game, load_game
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE, WHITE, CRITICAL_TINT, MORNING_GLORY, BLACK, \
    GOLD, HUD_HEART_ICON, HUD_COIN_ICON, HUD_VIRUS_ICON, HUD_RING_ICON, MALE_SPRITE, FEMALE_SPRITE, DEFAULT_FONT, \
    UI_BACKGROUND, MAZE_WIDTH, MAZE_HEIGHT, SOUND_GAME_MUSIC, SOUND_CUTSCENE_MUSIC, HUD_HEIGHT

def get_player_info(screen):
    print("Entering get_player_info...")
    try:
        font = pygame.font.SysFont(DEFAULT_FONT, 36)
    except:
        print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
        font = pygame.font.Font(None, 36)
    try:
        title_font = pygame.font.SysFont(DEFAULT_FONT, 48, bold=True)
    except:
        print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
        title_font = pygame.font.Font(None, 48)

    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        r = 14 + (y / SCREEN_HEIGHT) * (50 - 14)
        g = 39 + (y / SCREEN_HEIGHT) * (70 - 39)
        b = 59 + (y / SCREEN_HEIGHT) * (100 - 59)
        pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))

    panel = pygame.Surface((300, 200), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    pygame.draw.rect(panel, WHITE, (0, 0, 300, 200), 3)

    name = ""
    name_input_active = True
    error_message = ""

    while name_input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in name input.")
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in name input: {event.key}")
                if event.key == pygame.K_RETURN and name:
                    name_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum():
                    name += event.unicode
                else:
                    error_message = "Invalid key! Use letters/numbers for name."

        screen.blit(background, (0, 0))
        screen.blit(panel, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))

        title_text = title_font.render("Enter Your Name", True, WHITE)
        title_shadow = title_font.render("Enter Your Name", True, BLACK)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 50 + 2))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        name_text = font.render(f"Name: {name}", True, WHITE)
        name_shadow = font.render(f"Name: {name}", True, BLACK)
        screen.blit(name_shadow, (SCREEN_WIDTH // 2 - name_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 - 20 + 2))
        screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        error_text = font.render(error_message, True, (255, 0, 0)) if error_message else None
        if error_text:
            screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.time.delay(1000)
            error_message = ""

        pygame.display.flip()

    name = name.upper()

    gender = None
    gender_input_active = True
    error_message = ""

    try:
        print(f"Attempting to load male sprite from: {MALE_SPRITE}")
        if not os.path.exists(MALE_SPRITE):
            raise FileNotFoundError(f"File not found: {MALE_SPRITE}")
        male_sprite = pygame.image.load(MALE_SPRITE).convert_alpha()
        male_sprite = pygame.transform.scale(male_sprite, (TILE_SIZE, TILE_SIZE))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load male sprite at {MALE_SPRITE}. Error: {e}. Using placeholder.")
        male_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
        male_sprite.fill(MORNING_GLORY)

    try:
        print(f"Attempting to load female sprite from: {FEMALE_SPRITE}")
        if not os.path.exists(FEMALE_SPRITE):
            raise FileNotFoundError(f"File not found: {FEMALE_SPRITE}")
        female_sprite = pygame.image.load(FEMALE_SPRITE).convert_alpha()
        female_sprite = pygame.transform.scale(female_sprite, (TILE_SIZE, TILE_SIZE))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load female sprite at {FEMALE_SPRITE}. Error: {e}. Using placeholder.")
        female_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
        female_sprite.fill((255, 105, 180))

    male_sprite_y = SCREEN_HEIGHT // 2 + 20
    female_sprite_y = SCREEN_HEIGHT // 2 + 20
    male_sprite_timer = 0
    female_sprite_timer = 0
    male_sprite_direction = 1
    female_sprite_direction = -1

    while gender_input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in gender input.")
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in gender input: {event.key}")
                if event.key in (pygame.K_m, pygame.K_f):
                    gender = "male" if event.key == pygame.K_m else "female"
                    gender_input_active = False

        male_sprite_timer += 1
        female_sprite_timer += 1
        if male_sprite_timer % 10 == 0:
            male_sprite_y += male_sprite_direction * 2
            if male_sprite_y > SCREEN_HEIGHT // 2 + 30 or male_sprite_y < SCREEN_HEIGHT // 2 + 10:
                male_sprite_direction *= -1
        if female_sprite_timer % 10 == 0:
            female_sprite_y += female_sprite_direction * 2
            if female_sprite_y > SCREEN_HEIGHT // 2 + 30 or female_sprite_y < SCREEN_HEIGHT // 2 + 10:
                female_sprite_direction *= -1

        screen.blit(background, (0, 0))
        print("Drawing background during gender selection")
        screen.blit(panel, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
        print("Drawing panel during gender selection")

        title_text = title_font.render("Select Your Gender", True, WHITE)
        title_shadow = title_font.render("Select Your Gender", True, BLACK)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 50 + 2))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        print("Drawing title text during gender selection")

        gender_text = font.render(f"Gender: {gender or 'Press M/F'}", True, WHITE)
        gender_shadow = font.render(f"Gender: {gender or 'Press M/F'}", True, BLACK)
        screen.blit(gender_shadow, (SCREEN_WIDTH // 2 - gender_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 - 20 + 2))
        screen.blit(gender_text, (SCREEN_WIDTH // 2 - gender_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        print("Drawing gender text during gender selection")

        screen.blit(male_sprite, (SCREEN_WIDTH // 2 - 75, male_sprite_y))
        screen.blit(female_sprite, (SCREEN_WIDTH // 2 + 25, female_sprite_y))
        print("Drawing sprites during gender selection")

        error_text = font.render(error_message, True, (255, 0, 0)) if error_message else None
        if error_text:
            screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.time.delay(1000)
            error_message = ""

        pygame.display.flip()

    player_sprite = male_sprite if gender == "male" else female_sprite

    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(background, (0, 0))
        print("Drawing background during fade-out")
        screen.blit(panel, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
        print("Drawing panel during fade-out")
        title_text = title_font.render("Select Your Gender", True, WHITE)
        title_shadow = title_font.render("Select Your Gender", True, BLACK)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 50 + 2))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        print("Drawing title text during fade-out")
        gender_text = font.render(f"Gender: {gender}", True, WHITE)
        gender_shadow = font.render(f"Gender: {gender}", True, BLACK)
        screen.blit(gender_shadow, (SCREEN_WIDTH // 2 - gender_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 - 20 + 2))
        screen.blit(gender_text, (SCREEN_WIDTH // 2 - gender_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        print("Drawing gender text during fade-out")
        screen.blit(male_sprite, (SCREEN_WIDTH // 2 - 75, male_sprite_y))
        screen.blit(female_sprite, (SCREEN_WIDTH // 2 + 25, female_sprite_y))
        print("Drawing sprites during fade-out")
        screen.blit(fade_surface, (0, 0))
        print(f"Fade-out alpha: {alpha}")
        pygame.display.flip()
        pygame.time.delay(20)

    screen.fill(BLACK)
    pygame.display.flip()
    print("Cleared screen before transition")
    pygame.event.clear()
    print("Cleared event queue before transition")
    pygame.time.delay(500)

    print("Exiting get_player_info with name:", name, "and gender:", gender)
    return name, gender, player_sprite

def vendor_interaction(screen, clock, player, vendor, dialogue_box, ui_background):
    print("Entering vendor_interaction...")
    try:
        font = pygame.font.SysFont(DEFAULT_FONT, 36)
    except:
        print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
        font = pygame.font.Font(None, 36)

    panel = pygame.Surface((SCREEN_WIDTH - 80, SCREEN_HEIGHT - 100), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    pygame.draw.rect(panel, WHITE, (0, 0, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 100), 3)

    options = list(vendor.upgrades.keys()) + ["Exit"]
    selected = 0
    running = True

    while running:
        lines = ["Vendor: Welcome to my shop!", f"Vendor: Supercollateral: {player.inventory.supercollateral}"]
        for i, option in enumerate(options):
            if option != "Exit":
                upgrade = vendor.upgrades[option]
                lines.append(f"{i+1}: {option}: {upgrade['description']} (Cost: {upgrade['cost']}) - Press {i+1} to buy")
            else:
                lines.append(f"{len(options)}: Exit - Press {len(options)} to leave or ESC to close")
        dialogue_box.show(lines, show_prompt=False)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in vendor_interaction.")
                return False
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in vendor_interaction: {event.key}")
                if event.key in range(pygame.K_1, pygame.K_9 + 1):
                    index = event.key - pygame.K_1 + 1
                    if 1 <= index <= len(options):
                        selected = index - 1
                        if options[selected] == "Exit":
                            running = False
                        else:
                            upgrade = vendor.upgrades[options[selected]]
                            if player.inventory.spend_supercollateral(upgrade["cost"]):
                                if options[selected] == "Optimism Ring Fill Rate":
                                    player.optimism_ring_fill_rate += upgrade["value"]
                                elif options[selected] == "Attack Power":
                                    player.attack_power += upgrade["value"]
                                elif options[selected] == "Ranged Attacks":
                                    player.ranged_attacks += upgrade["value"]
                                dialogue_box.show([f"Vendor: Purchased {options[selected]}!"])
                            else:
                                dialogue_box.show(["Vendor: Not enough Supercollateral!"])
                elif event.key == pygame.K_ESCAPE:
                    running = False

        screen.blit(ui_background, (0, 0))
        screen.blit(panel, (40, 50))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting vendor_interaction...")
    return True

def final_cutscene(screen, clock, player, ui_background):
    print("Entering final_cutscene...")
    pronoun = "his" if player.gender == "male" else "her"
    lines = [
        f"Vitalik: With Skuld defeated, {player.name} stands before the restored Superseed.",
        f"Vitalik: The fragments pulse with light, merging into a radiant whole.",
        f"Vitalik: Krypto’s darkness lifts—Seisan’s chaos is balanced once more.",
        f"Vitalik: {player.name} has fulfilled {pronoun} destiny as the Sapa Slayer.",
        f"Vitalik: The ElPee rise again, and Krypto blooms under the Superseed’s glow.",
        f"Vitalik: Thank you for playing A Superseed Odyssey!"
    ]
    dialogue_box = DialogueBox()
    dialogue_box.show(lines)
    running = True

    while running and dialogue_box.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in final_cutscene.")
                return False
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in final_cutscene: {event.key}")
                if event.key == pygame.K_SPACE:
                    dialogue_box.next_line()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting final_cutscene...")
    return True

def draw_ui(screen, player, world, font, heart_icon, coin_icon, virus_icon, ring_icon, infection_active):
    hud_panel = pygame.Surface((SCREEN_WIDTH, 30), pygame.SRCALPHA)
    hud_panel.fill((0, 0, 0, 180))
    pygame.draw.rect(hud_panel, WHITE, (0, 0, SCREEN_WIDTH, 30), 2)

    hp_bar = pygame.Surface((100, 15), pygame.SRCALPHA)
    hp_width = (player.hp / player.max_hp) * 100
    for x in range(int(hp_width)):
        r = 255 if player.hp > 50 else int(255 * (player.hp / 50))
        g = 255 if player.hp < 50 else int(255 * (1 - (player.hp - 50) / 50))
        b = 0
        pygame.draw.line(hp_bar, (r, g, b), (x, 0), (x, 15))
    alpha = 255 if player.hp > 30 else int(128 + 127 * (pygame.time.get_ticks() % 1000) / 1000)
    hp_bar.set_alpha(alpha)

    infection_bar = pygame.Surface((100, 15), pygame.SRCALPHA)
    infection_width = (player.infection_level / 100) * 100
    for x in range(int(infection_width)):
        alpha = int(255 * (x / infection_width))
        pygame.draw.line(infection_bar, (255, 0, 0, alpha), (x, 0), (x, 15))

    # Optimism Ring fill bar
    ring_fill_bar = pygame.Surface((100, 15), pygame.SRCALPHA)
    ring_fill_width = player.optimism_ring_fill
    for x in range(int(ring_fill_width)):
        alpha = int(255 * (x / 100))
        pygame.draw.line(ring_fill_bar, (255, 215, 0, alpha), (x, 0), (x, 15))

    screen.blit(hud_panel, (0, 20))

    screen.blit(heart_icon, (10, 25))
    screen.blit(hp_bar, (40, 25))
    hp_text = font.render(f"{player.hp}", True, WHITE)
    hp_shadow = font.render(f"{player.hp}", True, BLACK)
    screen.blit(hp_shadow, (150 + 2, 25 + 2))
    screen.blit(hp_text, (150, 25))

    if infection_active:
        screen.blit(virus_icon, (180, 25))
        screen.blit(infection_bar, (210, 25))
        infection_text = font.render(f"{int(player.infection_level)}%", True, WHITE)
        infection_shadow = font.render(f"{int(player.infection_level)}%", True, BLACK)
        screen.blit(infection_shadow, (320 + 2, 25 + 2))
        screen.blit(infection_text, (320, 25))

    sapa_count = len(world.get_current_scene().sapas)
    sapa_text = font.render(f"{sapa_count} Sapa", True, WHITE)
    sapa_shadow = font.render(f"{sapa_count} Sapa", True, BLACK)
    screen.blit(sapa_shadow, (360 + 2, 25 + 2))
    screen.blit(sapa_text, (360, 25))

    area_text = font.render(f"Area: {world.areas[world.current_area].name}", True, WHITE)
    area_shadow = font.render(f"Area: {world.areas[world.current_area].name}", True, BLACK)
    screen.blit(area_shadow, (450 + 2, 25 + 2))
    screen.blit(area_text, (450, 25))

    screen.blit(coin_icon, (650, 25))
    currency_text = font.render(f"{player.inventory.supercollateral}", True, WHITE)
    currency_shadow = font.render(f"{player.inventory.supercollateral}", True, BLACK)
    screen.blit(currency_shadow, (680 + 2, 25 + 2))
    screen.blit(currency_text, (680, 25))

    # Draw Optimism Ring fill bar
    screen.blit(ring_icon, (720, 25))
    screen.blit(ring_fill_bar, (750, 25))
    if player.optimism_ring_cooldown > 0:
        cooldown_text = font.render(f"CD: {int(player.optimism_ring_cooldown)}s", True, WHITE)
        cooldown_shadow = font.render(f"CD: {int(player.optimism_ring_cooldown)}s", True, BLACK)
        screen.blit(cooldown_shadow, (850 + 2, 25 + 2))
        screen.blit(cooldown_text, (850, 25))
    else:
        fill_text = font.render(f"{int(player.optimism_ring_fill)}%", True, WHITE)
        fill_shadow = font.render(f"{int(player.optimism_ring_fill)}%", True, BLACK)
        screen.blit(fill_shadow, (850 + 2, 25 + 2))
        screen.blit(fill_text, (850, 25))

    # Add player level and XP
    level_text = font.render(f"Level: {player.level}", True, WHITE)
    level_shadow = font.render(f"Level: {player.level}", True, BLACK)
    screen.blit(level_shadow, (10 + 2, 55 + 2))
    screen.blit(level_text, (10, 55))

    xp_text = font.render(f"XP: {player.xp}/{player.xp_to_next_level}", True, WHITE)
    xp_shadow = font.render(f"XP: {player.xp}/{player.xp_to_next_level}", True, BLACK)
    screen.blit(xp_shadow, (100 + 2, 55 + 2))
    screen.blit(xp_text, (100, 55))

def draw_labels(screen, scene, player, font):
    label_font = pygame.font.SysFont(DEFAULT_FONT, 20)

    label = label_font.render(player.name, True, WHITE)
    label_rect = label.get_rect(center=(player.rect.centerx, player.rect.top - 10))
    pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
    screen.blit(label, label_rect)

    for token in scene.tokens:
        label = label_font.render("Token", True, (0, 255, 255))
        label_rect = label.get_rect(center=(token.centerx, token.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    for checkpoint in scene.checkpoints:
        label = label_font.render("Checkpoint", True, (0, 255, 0))
        label_rect = label.get_rect(center=(checkpoint.centerx, checkpoint.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    if scene.sword:
        label = label_font.render("Sword", True, (255, 255, 0))
        label_rect = label.get_rect(center=(scene.sword.centerx, scene.sword.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    for fragment in scene.fragments:
        label = label_font.render("Fragment", True, (255, 165, 0))
        label_rect = label.get_rect(center=(fragment.centerx, fragment.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    for enemy in scene.sapas:
        label = label_font.render(f"{enemy.name} (Lvl {enemy.level})", True, (255, 0, 0))
        label_rect = label.get_rect(center=(enemy.rect.centerx, enemy.rect.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    if scene.npc:
        label = label_font.render("NPC" if not scene.npc.is_vitalik else "Vitalik", True, (255, 255, 0) if scene.npc.is_vitalik else (0, 255, 255))
        label_rect = label.get_rect(center=(scene.npc.rect.centerx, scene.npc.rect.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    if hasattr(scene, 'npcs'):
        for npc in scene.npcs:
            label = label_font.render("NPC" if not npc.is_vitalik else "Vitalik", True, (255, 255, 0) if npc.is_vitalik else (0, 255, 255))
            label_rect = label.get_rect(center=(npc.rect.centerx, npc.rect.top - 10))
            pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
            screen.blit(label, label_rect)

def draw_exits(screen, scene, font):
    entry_x, entry_y = scene.entry
    exit_x, exit_y = scene.exit

    # Load exit arrow sprite (if available)
    exit_arrow_sprite = None
    try:
        exit_arrow_sprite = pygame.image.load("assets/sprites/exit_arrow.png").convert_alpha()
        exit_arrow_sprite = pygame.transform.scale(exit_arrow_sprite, (30, 30))
    except:
        print("Failed to load exit arrow sprite. Using fallback.")

    if "west" in scene.exits:
        if entry_x == 0:
            if exit_arrow_sprite:
                screen.blit(exit_arrow_sprite, (10, (entry_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT - 15))
            else:
                pygame.draw.polygon(screen, WHITE, [(10, (entry_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT), (30, (entry_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT), (30, (entry_y * TILE_SIZE + TILE_SIZE + 10 + 20) + HUD_HEIGHT)])
            exit_text = font.render("Previous Scene", True, WHITE)
            screen.blit(exit_text, (40, (entry_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT))
        elif entry_y == 0:
            if exit_arrow_sprite:
                screen.blit(pygame.transform.rotate(exit_arrow_sprite, 90), (entry_x * TILE_SIZE + TILE_SIZE - 15, HUD_HEIGHT + 20))
            else:
                pygame.draw.polygon(screen, WHITE, [(entry_x * TILE_SIZE + TILE_SIZE, HUD_HEIGHT + 20), (entry_x * TILE_SIZE + TILE_SIZE - 10, HUD_HEIGHT + 40), (entry_x * TILE_SIZE + TILE_SIZE + 10, HUD_HEIGHT + 40)])
            exit_text = font.render("Previous Scene", True, WHITE)
            screen.blit(exit_text, (entry_x * TILE_SIZE + TILE_SIZE - 40, HUD_HEIGHT + 30))

    if "east" in scene.exits:
        if exit_x == MAZE_WIDTH - 1:
            if exit_arrow_sprite:
                screen.blit(pygame.transform.flip(exit_arrow_sprite, True, False), (SCREEN_WIDTH - 40, (exit_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT - 15))
            else:
                pygame.draw.polygon(screen, WHITE, [(SCREEN_WIDTH - 10, (exit_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT), (SCREEN_WIDTH - 30, (exit_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT), (SCREEN_WIDTH - 30, (exit_y * TILE_SIZE + TILE_SIZE + 10 + 20) + HUD_HEIGHT)])
            exit_text = font.render("Next Scene", True, WHITE)
            screen.blit(exit_text, (SCREEN_WIDTH - 150, (exit_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT))
        elif exit_y == MAZE_HEIGHT - 1:
            if exit_arrow_sprite:
                screen.blit(pygame.transform.rotate(exit_arrow_sprite, -90), (exit_x * TILE_SIZE + TILE_SIZE - 15, SCREEN_HEIGHT - 70))
            else:
                pygame.draw.polygon(screen, WHITE, [(exit_x * TILE_SIZE + TILE_SIZE, SCREEN_HEIGHT - 50), (exit_x * TILE_SIZE + TILE_SIZE - 10, SCREEN_HEIGHT - 70), (exit_x * TILE_SIZE + TILE_SIZE + 10, SCREEN_HEIGHT - 70)])
            exit_text = font.render("Next Scene", True, WHITE)
            screen.blit(exit_text, (exit_x * TILE_SIZE + TILE_SIZE - 40, SCREEN_HEIGHT - 60))

def draw_minimap(screen, scene, player, font, ui_background):
    print("Drawing minimap...")
    minimap_size = 200
    scale = minimap_size / max(MAZE_WIDTH * TILE_SIZE, MAZE_HEIGHT * TILE_SIZE)
    minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
    minimap_surface.blit(ui_background, (0, 0), (0, 0, minimap_size, minimap_size))

    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if scene.grid[y][x] == 1:
                pygame.draw.rect(minimap_surface, (100, 100, 100), (x * scale * TILE_SIZE, y * scale * TILE_SIZE, scale * TILE_SIZE, scale * TILE_SIZE))

    player_x = player.rect.x * scale
    player_y = (player.rect.y - HUD_HEIGHT) * scale
    pygame.draw.rect(minimap_surface, MORNING_GLORY if player.gender == "male" else (255, 105, 180), (player_x, player_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for enemy in scene.sapas:
        enemy_x = enemy.rect.x * scale
        enemy_y = (enemy.rect.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (255, 0, 0), (enemy_x, enemy_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for token in scene.tokens:
        token_x = token.x * scale
        token_y = (token.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (0, 255, 255), (token_x, token_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for checkpoint in scene.checkpoints:
        checkpoint_x = checkpoint.x * scale
        checkpoint_y = (checkpoint.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (0, 255, 0), (checkpoint_x, checkpoint_y, scale * TILE_SIZE, scale * TILE_SIZE))

    if scene.sword:
        sword_x = scene.sword.x * scale
        sword_y = (scene.sword.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (255, 255, 0), (sword_x, sword_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for fragment in scene.fragments:
        fragment_x = fragment.x * scale
        fragment_y = (fragment.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (255, 165, 0), (fragment_x, fragment_y, scale * TILE_SIZE, scale * TILE_SIZE))

    if scene.npc:
        npc_x = scene.npc.rect.x * scale
        npc_y = (scene.npc.rect.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (0, 255, 255) if not scene.npc.is_vitalik else (255, 255, 0), (npc_x, npc_y, scale * TILE_SIZE, scale * TILE_SIZE))

    if hasattr(scene, 'npcs'):
        for npc in scene.npcs:
            npc_x = npc.rect.x * scale
            npc_y = (npc.rect.y - HUD_HEIGHT) * scale
            pygame.draw.rect(minimap_surface, (0, 255, 255) if not npc.is_vitalik else (255, 255, 0), (npc_x, npc_y, scale * TILE_SIZE, scale * TILE_SIZE))

    screen.blit(minimap_surface, (SCREEN_WIDTH - minimap_size - 10, SCREEN_HEIGHT - minimap_size - 10))
    close_text = font.render("Press M to close", True, WHITE)
    screen.blit(close_text, (SCREEN_WIDTH - minimap_size - 10, SCREEN_HEIGHT - 25))

def prompt_game_over(screen, dialogue_box, player, checkpoints, ui_background):
    print("Prompting game over...")
    has_checkpoint = checkpoints.has_checkpoint()
    message = [f"Vitalik: Infection has taken over! Start over (S) or {'resume at checkpoint (R)' if has_checkpoint else 'quit (ESC)'}?"]
    dialogue_box.show(message, show_prompt=False)
    choice_made = False
    choice = None

    prompt_font = pygame.font.SysFont(DEFAULT_FONT, 20)
    prompt_text = prompt_font.render(f"Press S to start over{' or R to resume' if has_checkpoint else ''}, or ESC to quit", True, WHITE)
    prompt_shadow = prompt_font.render(f"Press S to start over{' or R to resume' if has_checkpoint else ''}, or ESC to quit", True, BLACK)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in game over prompt.")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in game over prompt: {event.key}")
                if event.key == pygame.K_s:
                    choice = "start_over"
                    choice_made = True
                elif event.key == pygame.K_r and has_checkpoint:
                    choice = "resume"
                    choice_made = True
                elif event.key == pygame.K_ESCAPE:
                    print("Game over prompt closed by user.")
                    pygame.quit()
                    sys.exit()

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        screen.blit(prompt_shadow, (prompt_rect.x + 2, prompt_rect.y + 2))
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    return choice

def play_sword_puzzle(screen, clock, dialogue_box, ui_background):
    print("Entering play_sword_puzzle...")
    minigames = [
        play_hash_dash,
        play_collateral_lock,
        play_gas_fee_gauntlet,
        play_anagram,
        play_memory_sequence,
        play_color_match
    ]
    selected_minigame = random.choice(minigames)
    dialogue_box.show(["Vitalik: A puzzle guards the Sword of Solvency! Solve it to proceed. Press Y to start, N to skip, or ESC to close."])
    choice_made = False
    result = False

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in play_sword_puzzle.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    if callable(selected_minigame) and selected_minigame(screen, clock):
                        result = True
                        choice_made = True
                    else:
                        dialogue_box.show(["Vitalik: Puzzle failed! Try again. Press Y to retry, N to skip, or ESC to close."])
                elif event.key == pygame.K_n:
                    choice_made = True
                elif event.key == pygame.K_ESCAPE:
                    choice_made = True

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting play_sword_puzzle...")
    return result

def play_vitalik_puzzle(screen, clock, dialogue_box, ui_background):
    print("Entering play_vitalik_puzzle...")
    minigames = [
        play_hash_dash,
        play_collateral_lock,
        play_gas_fee_gauntlet,
        play_anagram,
        play_memory_sequence,
        play_color_match
    ]
    selected_minigame = random.choice(minigames)
    dialogue_box.show(["Vitalik: I’m trapped! Solve this puzzle to free me. Press Y to start, N to skip, or ESC to close."])
    choice_made = False
    result = False

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in play_vitalik_puzzle.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    if callable(selected_minigame) and selected_minigame(screen, clock):
                        result = True
                        choice_made = True
                    else:
                        dialogue_box.show(["Vitalik: Puzzle failed! Try again. Press Y to retry, N to skip, or ESC to close."])
                elif event.key == pygame.K_n:
                    choice_made = True
                elif event.key == pygame.K_ESCAPE:
                    choice_made = True

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting play_vitalik_puzzle...")
    return result

def play_quest_minigame(screen, clock, dialogue_box, ui_background, minigame_func, player):
    print("Entering play_quest_minigame...")
    dialogue_box.show(["NPC: Complete this challenge for a reward! Press Y to start, N to skip, or ESC to close."])
    choice_made = False
    reward = 10  # Supercollateral reward for completing the minigame

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in play_quest_minigame.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    if callable(minigame_func) and minigame_func(screen, clock):
                        player.inventory.add_supercollateral(reward)
                        dialogue_box.show([f"NPC: Well done! Here's your reward: {reward} Supercollateral."])
                        return True
                    else:
                        dialogue_box.show(["NPC: Challenge failed! Try again. Press Y to retry, N to skip, or ESC to close."])
                elif event.key == pygame.K_n:
                    return False
                elif event.key == pygame.K_ESCAPE:
                    return False

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting play_quest_minigame...")
    return False

def main():
    print("Starting game...")
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("A Superseed Odyssey: Rise of the Sapa Slayer")
    clock = pygame.time.Clock()

    print("Pygame initialized. Screen and clock created.")

    try:
        pygame.mixer.music.load(SOUND_CUTSCENE_MUSIC)
        pygame.mixer.music.play(-1)
        print("Cutscene music loaded and playing.")
    except pygame.error as e:
        print(f"Failed to load cutscene music: {e}. Continuing without music.")

    try:
        font = pygame.font.SysFont(DEFAULT_FONT, 24)
    except:
        print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
        font = pygame.font.Font(None, 24)

    try:
        print(f"Attempting to load heart icon from: {HUD_HEART_ICON}")
        if not os.path.exists(HUD_HEART_ICON):
            raise FileNotFoundError(f"File not found: {HUD_HEART_ICON}")
        heart_icon = pygame.image.load(HUD_HEART_ICON).convert_alpha()
        heart_icon = pygame.transform.scale(heart_icon, (20, 20))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load heart icon at {HUD_HEART_ICON}. Error: {e}. Using placeholder.")
        heart_icon = pygame.Surface((20, 20))
        heart_icon.fill((255, 0, 0))

    try:
        print(f"Attempting to load coin icon from: {HUD_COIN_ICON}")
        if not os.path.exists(HUD_COIN_ICON):
            raise FileNotFoundError(f"File not found: {HUD_COIN_ICON}")
        coin_icon = pygame.image.load(HUD_COIN_ICON).convert_alpha()
        coin_icon = pygame.transform.scale(coin_icon, (20, 20))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load coin icon at {HUD_COIN_ICON}. Error: {e}. Using placeholder.")
        coin_icon = pygame.Surface((20, 20))
        coin_icon.fill(GOLD)

    try:
        print(f"Attempting to load virus icon from: {HUD_VIRUS_ICON}")
        if not os.path.exists(HUD_VIRUS_ICON):
            raise FileNotFoundError(f"File not found: {HUD_VIRUS_ICON}")
        virus_icon = pygame.image.load(HUD_VIRUS_ICON).convert_alpha()
        virus_icon = pygame.transform.scale(virus_icon, (20, 20))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load virus icon at {HUD_VIRUS_ICON}. Error: {e}. Using placeholder.")
        virus_icon = pygame.Surface((20, 20))
        virus_icon.fill((200, 0, 0))

    try:
        print(f"Attempting to load ring icon from: {HUD_RING_ICON}")
        if not os.path.exists(HUD_RING_ICON):
            raise FileNotFoundError(f"File not found: {HUD_RING_ICON}")
        ring_icon = pygame.image.load(HUD_RING_ICON).convert_alpha()
        ring_icon = pygame.transform.scale(ring_icon, (20, 20))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load ring icon at {HUD_RING_ICON}. Error: {e}. Using placeholder.")
        ring_icon = pygame.Surface((20, 20))
        ring_icon.fill(GOLD)

    ui_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    try:
        print(f"Attempting to load UI background from: {UI_BACKGROUND}")
        if not os.path.exists(UI_BACKGROUND):
            raise FileNotFoundError(f"File not found: {UI_BACKGROUND}")
        ui_background = pygame.image.load(UI_BACKGROUND).convert()
        ui_background = pygame.transform.scale(ui_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load UI background at {UI_BACKGROUND}. Error: {e}. Using placeholder.")
        for y in range(SCREEN_HEIGHT):
            r = 14 + (y / SCREEN_HEIGHT) * (50 - 14)
            g = 39 + (y / SCREEN_HEIGHT) * (70 - 39)
            b = 59 + (y / SCREEN_HEIGHT) * (100 - 59)
            pygame.draw.line(ui_background, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))

    # Check for saved game
    game_state = load_game()
    if game_state:
        player_name = game_state['player']['name']
        player_gender = game_state['player']['gender']
        player_sprite = pygame.image.load(MALE_SPRITE if player_gender == "male" else FEMALE_SPRITE).convert_alpha()
        player_sprite = pygame.transform.scale(player_sprite, (TILE_SIZE, TILE_SIZE))
    else:
        player_name, player_gender, player_sprite = get_player_info(screen)
    print(f"Player info collected: Name={player_name}, Gender={player_gender}")

    try:
        print("Creating Player object...")
        player = Player(0, 0, player_name, player_gender, player_sprite)
        if game_state:
            player.rect.x, player.rect.y = game_state['player']['rect']
            player.hp = game_state['player']['hp']
            player.max_hp = game_state['player']['max_hp']
            player.infection_level = game_state['player']['infection_level']
            player.attack_power = game_state['player']['attack_power']
            player.ranged_attacks = game_state['player']['ranged_attacks']
            player.optimism_ring_fill = game_state['player']['optimism_ring_fill']
            player.optimism_ring_fill_rate = game_state['player']['optimism_ring_fill_rate']
            player.optimism_ring_duration = game_state['player']['optimism_ring_duration']
            player.optimism_ring_cooldown = game_state['player']['optimism_ring_cooldown']
            player.optimism_ring_active = game_state['player']['optimism_ring_active']
            player.optimism_ring_timer = game_state['player']['optimism_ring_timer']
            player.easy_mode = game_state['player']['easy_mode']
            player.level = game_state['player']['level']
            player.xp = game_state['player']['xp']
            player.xp_to_next_level = game_state['player']['xp_to_next_level']
            player.inventory.supercollateral = game_state['player']['inventory']['supercollateral']
            player.inventory.fragments = game_state['player']['inventory']['fragments']
            player.inventory.has_sword = game_state['player']['inventory']['has_sword']
        print(f"Player created: Name={player.name}, Gender={player.gender}")
    except Exception as e:
        print(f"Error creating Player object: {e}")
        pygame.quit()
        sys.exit()

    try:
        print("Creating World object...")
        vitalik_freed = game_state['vitalik_freed'] if game_state else False
        world = World(player, vitalik_freed)
        if game_state:
            world.current_area = game_state['world']['current_area']
            world.current_scene = game_state['world']['current_scene']
        print("World object created.")
    except Exception as e:
        print(f"Error creating World object: {e}")
        pygame.quit()
        sys.exit()

    current_scene = world.get_current_scene()
    start_x, start_y = current_scene.maze.find_open_start_position()
    player.rect.x, player.rect.y = start_x, start_y
    print(f"Player positioned at: ({player.rect.x}, {player.rect.y})")

    print("Creating Checkpoints, Combat, and DialogueBox...")
    try:
        print("Creating Checkpoints object...")
        checkpoints = CheckpointSystem()
        print("Checkpoints object created.")
    except Exception as e:
        print(f"Error creating Checkpoints object: {e}")
        pygame.quit()
        sys.exit()

    try:
        print("Creating Combat object...")
        combat = CombatSystem()
        print("Combat object created.")
    except Exception as e:
        print(f"Error creating Combat object: {e}")
        pygame.quit()
        sys.exit()

    try:
        print("Creating DialogueBox object...")
        dialogue_box = DialogueBox()
        print("DialogueBox object created.")
    except Exception as e:
        print(f"Error creating DialogueBox object: {e}")
        pygame.quit()
        sys.exit()

    print("World, Checkpoints, Combat, and DialogueBox created.")

    minigames = [
        play_hash_dash,
        play_collateral_lock,
        play_gas_fee_gauntlet,
        play_anagram,
        play_memory_sequence,
        play_color_match
    ]
    vitalik_freed = game_state['vitalik_freed'] if game_state else False
    choice_made = game_state['choice_made'] if game_state else False
    self_save_choice_made = game_state['self_save_choice_made'] if game_state else False
    first_vendor_spawn = True  # Flag to track first vendor spawn

    # Place Vitalik in Area 0, Scene 2, and a random NPC in the same scene
    for area in world.areas:
        for scene in area.scenes:
            if area.area_id == 0 and scene.scene_id == 2 and not vitalik_freed:
                scene.npc = NPC(scene, is_vitalik=True)
                # Add a random NPC for context
                random_npc = NPC(scene, is_vitalik=False)
                random_npc.lore = ["NPC: Although trapped, the gods marked this area untouchable by Sapa till Vitalik can be freed."]
                scene.npcs = [random_npc]  # Add a list to store multiple NPCs
            elif area.area_id == 0 and scene.scene_id == 4 and not player.inventory.has_sword:
                x, y = scene.find_open_position()
                scene.sword = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            else:
                # Vendor NPCs can spawn after Vitalik is freed (Area 0, Scene 3 onwards)
                if vitalik_freed and (area.area_id > 0 or scene.scene_id >= 3) and random.random() < 0.3:
                    if not scene.npc or not scene.npc.is_vitalik:
                        new_vendor = NPC(scene, is_vendor=True)
                        if not hasattr(scene, 'npcs'):
                            scene.npcs = []
                        scene.npcs.append(new_vendor)
                # Other NPCs spawn only after the player has the sword
                if player.inventory.has_sword and random.random() < 0.3:
                    if not scene.npc or not scene.npc.is_vitalik:
                        is_crypto_scholar = random.random() < 0.2
                        new_npc = NPC(scene, is_crypto_scholar=is_crypto_scholar)
                        if not hasattr(scene, 'npcs'):
                            scene.npcs = []
                        scene.npcs.append(new_npc)
            if random.random() < 0.2:
                scene.minigame = random.choice(minigames)
    print("NPCs, vendors, and minigames placed in scenes.")

    if not game_state:
        try:
            play_intro_cutscene(screen, clock, player, ui_background)
            print("Intro cutscene completed.")
        except Exception as e:
            print(f"Error during intro cutscene: {e}")
            pygame.quit()
            sys.exit()

    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(SOUND_GAME_MUSIC)
        pygame.mixer.music.play(-1)
        print("Game music loaded and playing.")
    except pygame.error as e:
        print(f"Failed to load game music: {e}. Continuing without music.")

    choice_made = game_state['choice_made'] if game_state else False
    self_save_choice_made = game_state['self_save_choice_made'] if game_state else False
    vitalik = None
    if game_state and game_state['vitalik']['rect']:
        vitalik = NPC(current_scene, is_vitalik=True)
        vitalik.is_freed = game_state['vitalik']['is_freed']
        vitalik.following = game_state['vitalik']['following']
        vitalik.invulnerable = game_state['vitalik']['invulnerable']
        vitalik.rect.x, vitalik.rect.y = game_state['vitalik']['rect']
        current_scene.npc = vitalik

    last_time = pygame.time.get_ticks()
    paused = False
    show_minimap = False
    consecutive_losses = 0
    last_scene = None
    last_area = -1
    projectiles = []
    infection_active = True
    game_over = False
    music_volume = 1.0
    sfx_volume = 1.0
    pygame.mixer.music.set_volume(music_volume)
    fullscreen = False

    while not game_over:
        delta_time = 0
        if not paused:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0
            last_time = current_time

        current_scene = world.get_current_scene()
        sapas = current_scene.sapas

        if world.current_area != last_area:
            paused = True
            if not play_area_cutscene(screen, clock, player, world.current_area, ui_background):
                print("Area cutscene skipped or failed, continuing to game loop.")
            last_area = world.current_area
            paused = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in main loop.")
                game_over = True
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in main loop: {event.key}")
                if event.key == pygame.K_p and not dialogue_box.active:
                    paused = True
                    show_minimap = show_pause_menu(screen, player, dialogue_box, ui_background, world, checkpoints, music_volume, sfx_volume)
                    paused = False
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                if not paused:
                    if event.key == pygame.K_r:
                        checkpoints.load(player)
                    if event.key == pygame.K_j:
                        if player.inventory.has_sword:
                            combat.melee_attack(player)
                    if event.key == pygame.K_k:
                        if player.inventory.has_sword and player.ranged_attacks > 0:
                            combat.ranged_attack(player)
                            player.ranged_attacks -= 1
                    if event.key == pygame.K_SPACE and dialogue_box.active:
                        dialogue_box.next_line()
                    if event.key == pygame.K_e:
                        if current_scene.npc and player.rect.colliderect(current_scene.npc.rect):
                            if current_scene.npc.is_vendor:
                                paused = True
                                vendor_interaction(screen, clock, player, current_scene.npc, dialogue_box, ui_background)
                                paused = False
                            elif current_scene.npc.is_crypto_scholar and current_scene.npc.minigame:
                                paused = True
                                play_quest_minigame(screen, clock, dialogue_box, ui_background, current_scene.npc.minigame, player)
                                paused = False
                            elif current_scene.npc.is_vitalik and not vitalik_freed:
                                paused = True
                                if not vitalik_cutscene(screen, clock, player, dialogue_box):
                                    game_over = True
                                if play_vitalik_puzzle(screen, clock, dialogue_box, ui_background):
                                    vitalik_freed = True
                                    current_scene.npc.is_freed = True
                                    current_scene.npc.following = True
                                    vitalik = current_scene.npc
                                    dialogue_box.show(["Vitalik: I am freed! Let’s find the Sword of Solvency together."])
                                else:
                                    game_over = True
                                paused = False
                            else:
                                paused = True
                                dialogue_box.show(current_scene.npc.lore)
                                paused = False
                        # Handle other NPCs in the scene
                        if hasattr(current_scene, 'npcs'):
                            for npc in current_scene.npcs:
                                if player.rect.colliderect(npc.rect):
                                    if npc.is_vendor:
                                        if first_vendor_spawn and vitalik:
                                            dialogue_box.show(["Vitalik: Oh, a vendor! Interact to get upgrades."])
                                            first_vendor_spawn = False
                                        paused = True
                                        vendor_interaction(screen, clock, player, npc, dialogue_box, ui_background)
                                        paused = False
                                    elif npc.is_crypto_scholar and npc.minigame:
                                        paused = True
                                        play_quest_minigame(screen, clock, dialogue_box, ui_background, npc.minigame, player)
                                        paused = False
                                    else:
                                        paused = True
                                        dialogue_box.show(npc.lore)
                                        paused = False
                        elif current_scene.minigame and player.rect.colliderect(
                                pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, TILE_SIZE, TILE_SIZE)):
                            paused = True
                            dialogue_box.show(["Vitalik: Press Y to play minigame, N to skip, or ESC to close."])
                            paused = False
                        elif current_scene.sword and player.rect.colliderect(current_scene.sword) and vitalik_freed:
                            paused = True
                            if play_sword_puzzle(screen, clock, dialogue_box, ui_background):
                                player.inventory.add_sword()
                                infection_active = False
                                current_scene.sword = None
                                dialogue_box.show([f"Vitalik: {player.name} acquired the Sword of Solvency!"])
                            paused = False
                    if event.key == pygame.K_y and not dialogue_box.active and current_scene.minigame:
                        print("Starting minigame...")
                        minigame_func = current_scene.minigame
                        if callable(minigame_func):
                            if minigame_func(screen, clock):
                                player.inventory.add_supercollateral(10)
                        print("Minigame completed.")
                    if event.key == pygame.K_n and not dialogue_box.active:
                        current_scene.minigame = None
                    if event.key == pygame.K_o:
                        player.activate_optimism_ring()
                    if event.key == pygame.K_t and current_scene.npc and current_scene.npc.is_vitalik and player.rect.colliderect(
                            current_scene.npc.rect):
                        paused = True
                        show_tutorial(screen, dialogue_box, ui_background)
                        paused = False
                    if event.key == pygame.K_m:
                        show_minimap = not show_minimap

        if not paused and not dialogue_box.active:
            # Sapa spawning logic
            if (world.current_area > 0 or world.current_scene != 2) and random.random() < 0.05 and len(sapas) < 5:
                available_sapa_types = [Sapa, DiagonalSapa]
                if world.current_area >= 1 and player.inventory.has_sword:
                    available_sapa_types.append(ChaserSapa)
                if world.current_area >= 2:
                    available_sapa_types.append(SplitterSapa)
                if world.current_area >= 3:
                    available_sapa_types.append(ProjectileSapa)
                sapa_type = random.choice(available_sapa_types)
                new_sapa = sapa_type(current_scene, player.level)
                sapas.append(new_sapa)

            keys = pygame.key.get_pressed()
            player.move(keys, current_scene.maze)

            entry_x, entry_y = current_scene.entry
            exit_x, exit_y = current_scene.exit

            entry_rect = pygame.Rect(entry_x * TILE_SIZE, (entry_y * TILE_SIZE) + HUD_HEIGHT, 2 * TILE_SIZE, TILE_SIZE)
            exit_rect = pygame.Rect(exit_x * TILE_SIZE, (exit_y * TILE_SIZE) + HUD_HEIGHT, 2 * TILE_SIZE, TILE_SIZE)

            if "west" in current_scene.exits and player.rect.colliderect(entry_rect):
                world.move_to_scene("west")
                current_scene = world.get_current_scene()
                start_x, start_y = current_scene.maze.find_open_start_position()
                player.rect.x, player.rect.y = start_x, start_y
                if vitalik and vitalik.following:
                    vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                current_scene.sapas.clear()
                projectiles.clear()

            if "east" in current_scene.exits and player.rect.colliderect(exit_rect):
                world.move_to_scene("east")
                current_scene = world.get_current_scene()
                start_x, start_y = current_scene.maze.find_open_start_position()
                player.rect.x, player.rect.y = start_x, start_y
                if vitalik and vitalik.following:
                    vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                current_scene.sapas.clear()
                projectiles.clear()

            if vitalik and vitalik.following:
                vitalik.follow_player(player, dialogue_box)

            for token in current_scene.tokens[:]:
                if player.rect.colliderect(token):
                    current_scene.tokens.remove(token)
                    if player.inventory.has_sword:
                        player.inventory.add_supercollateral(5)
                    else:
                        player.update_infection(-10)
            for checkpoint in current_scene.checkpoints:
                if player.rect.colliderect(checkpoint):
                    checkpoints.save(player)
            if current_scene.npc and current_scene.npc.is_vitalik and not vitalik_freed and player.rect.colliderect(
                    current_scene.npc.rect):
                paused = True
                if not vitalik_cutscene(screen, clock, player, dialogue_box):
                    game_over = True
                if play_vitalik_puzzle(screen, clock, dialogue_box, ui_background):
                    vitalik_freed = True
                    current_scene.npc.is_freed = True
                    current_scene.npc.following = True
                    vitalik = current_scene.npc
                    dialogue_box.show(["Vitalik: I am freed! Let’s find the Sword of Solvency together."])
                else:
                    game_over = True
                paused = False
            if current_scene.npc and current_scene.npc.is_vitalik and current_scene.npc.is_freed and not choice_made and player.inventory.has_sword:
                paused = True
                choice = vitalik_choice(screen, clock, player, dialogue_box)
                choice_made = True
                if choice == "self" and not self_save_choice_made:
                    self_save_choice_made = True
                    player.lose_sword()
                    infection_active = True
                    # Relocate sword far from player
                    while True:
                        x, y = current_scene.find_open_position()
                        distance = ((x - player.rect.x) ** 2 + (y - player.rect.y) ** 2) ** 0.5
                        if distance > 5 * TILE_SIZE:
                            current_scene.sword = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                            break
                    # Spawn Sapa horde
                    for _ in range(5):
                        new_sapa = Sapa(current_scene, player.level)
                        sapas.append(new_sapa)
                elif choice == "world":
                    dialogue_box.show([
                        f"Vitalik: A true hero rises! I knew you had it in you, {player.name}! The first fragment’s light will cleanse your infection completely.",
                        "Vitalik: Together, we’ll gather the fragments, defeat Skuld, and bring prosperity back to Krypto—let’s do this!"
                    ])
                    choice_made = True
                paused = False
            if current_scene.sword and player.rect.colliderect(current_scene.sword) and vitalik_freed and not player.inventory.has_sword:
                paused = True
                if play_sword_puzzle(screen, clock, dialogue_box, ui_background):
                    player.inventory.add_sword()
                    infection_active = False
                    current_scene.sword = None
                    dialogue_box.show([f"Vitalik: {player.name} acquired the Sword of Solvency!"])
                if self_save_choice_made and player.inventory.has_sword:
                    choice_made = False
                    self_save_choice_made = False
                    infection_active = False
                paused = False
            for fragment in current_scene.fragments[:]:
                if player.rect.colliderect(fragment):
                    if current_scene.boss and current_scene.boss.hp > 0:
                        dialogue_box.show(["Vitalik: Defeat the boss to claim the fragment!"])
                    else:
                        player.collect_fragment()
                        infection_active = False
                        current_scene.fragments.remove(fragment)
                        if player.inventory.fragments == 1:
                            infection_active = False
                            dialogue_box.show(["Vitalik: The first fragment has fully cured your infection!"])
                        if player.inventory.fragments < 6:
                            world.current_area += 1
                            world.current_scene = 0
                            current_scene = world.get_current_scene()
                            start_x, start_y = current_scene.maze.find_open_start_position()
                            player.rect.x, player.rect.y = start_x, start_y
                            if vitalik and vitalik.following:
                                vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                            current_scene.sapas.clear()
                            projectiles.clear()

            for sapa in sapas[:]:
                sapa.move(current_scene.maze, player)
                if player.optimism_ring_active:
                    continue  # Skip Sapa attacks if player is invincible
                projectile = sapa.attack(player)
                if projectile:
                    if isinstance(projectile, list):
                        for new_sapa in projectile:
                            new_sapa.level = sapa.level
                            sapas.extend(projectile)
                    else:
                        projectiles.append(projectile)
                if vitalik and not vitalik.invulnerable and sapa.rect.colliderect(vitalik.rect):
                    print("Sapa attempted to attack Vitalik, but he's invulnerable.")
                if player.hp <= 0:
                    game_over = True

            for proj in projectiles[:]:
                rect, dx, dy = proj
                rect.x += dx * 5
                rect.y += dy * 5
                if rect.colliderect(player.rect) and not player.optimism_ring_active:
                    player.take_damage(5)
                    projectiles.remove(proj)
                elif rect.x < 0 or rect.x > SCREEN_WIDTH or rect.y < 0 or rect.y > SCREEN_HEIGHT:
                    projectiles.remove(proj)

            combat.update(sapas, player)
            player.update()

            if infection_active and not dialogue_box.active:
                infection_rate_per_second = 1.0 if not player.easy_mode else 0.5
                infection_increment = infection_rate_per_second * delta_time
                if player.update_infection(infection_increment):
                    paused = True
                    choice = prompt_game_over(screen, dialogue_box, player, checkpoints, ui_background)
                    if choice == "start_over":
                        world.current_area = 0
                        world.current_scene = 0
                        current_scene = world.get_current_scene()
                        start_x, start_y = current_scene.maze.find_open_start_position()
                        player.rect.x, player.rect.y = start_x, start_y
                        player.hp = 100
                        player.max_hp = 100
                        player.infection_level = 50
                        player.level = 1
                        player.xp = 0
                        player.xp_to_next_level = 10
                        player.attack_power = 2
                        player.optimism_ring_fill = 0
                        player.optimism_ring_fill_rate = 1.0
                        player.optimism_ring_duration = 5
                        player.optimism_ring_cooldown = 0
                        player.optimism_ring_active = False
                        player.optimism_ring_timer = 0
                        player.inventory.supercollateral = 0
                        player.inventory.fragments = 0
                        player.inventory.has_sword = False
                        infection_active = True
                        vitalik_freed = False
                        choice_made = False
                        self_save_choice_made = False
                        first_vendor_spawn = True
                        vitalik = None
                        current_scene.sapas.clear()
                        projectiles.clear()
                        consecutive_losses = 0
                    elif choice == "resume":
                        checkpoints.load(player)
                        current_scene.sapas.clear()
                        projectiles.clear()
                        consecutive_losses = 0
                    paused = False
                    continue

            print(f"Player infection level: {player.infection_level}, HP: {player.hp}")

            if player.inventory.fragments == 6:
                paused = True
                if final_cutscene(screen, clock, player, ui_background):
                    game_over = True
                paused = False

        if player.hp <= 0:
            current_scene_index = (world.current_area, world.current_scene)
            if last_scene == current_scene_index:
                consecutive_losses += 1
            else:
                consecutive_losses = 1
            last_scene = current_scene_index

            print(f"Consecutive losses: {consecutive_losses}")
            if consecutive_losses >= 3 and not player.easy_mode:
                paused = True
                prompt_easy_mode(screen, dialogue_box, player, ui_background)
                paused = False
                consecutive_losses = 0

            world.current_area = 0
            world.current_scene = 0
            current_scene = world.get_current_scene()
            start_x, start_y = current_scene.maze.find_open_start_position()
            player.rect.x, player.rect.y = start_x, start_y
            player.hp = 100
            player.max_hp = 100
            player.infection_level = 50
            player.level = 1
            player.xp = 0
            player.xp_to_next_level = 10
            player.attack_power = 2
            player.optimism_ring_fill = 0
            player.optimism_ring_fill_rate = 1.0
            player.optimism_ring_duration = 5
            player.optimism_ring_cooldown = 0
            player.optimism_ring_active = False
            player.optimism_ring_timer = 0
            player.inventory.supercollateral = 0
            player.inventory.fragments = 0
            player.inventory.has_sword = False
            infection_active = True
            vitalik_freed = False
            choice_made = False
            self_save_choice_made = False
            first_vendor_spawn = True
            vitalik = None
            current_scene.sapas.clear()
            projectiles.clear()
            continue

        current_scene.draw(screen)
        for sapa in sapas:
            sapa.draw(screen)
        for proj in projectiles:
            pygame.draw.rect(screen, (255, 0, 0), proj[0])
        if current_scene.npc:
            current_scene.npc.draw(screen)
        if hasattr(current_scene, 'npcs'):
            for npc in current_scene.npcs:
                npc.draw(screen)
        player.draw(screen)
        combat.draw(screen)
        draw_ui(screen, player, world, font, heart_icon, coin_icon, virus_icon, ring_icon, infection_active)
        draw_labels(screen, current_scene, player, font)
        draw_exits(screen, current_scene, font)
        if show_minimap:
            draw_minimap(screen, current_scene, player, font, ui_background)
        if infection_active and player.infection_level >= 80 and not player.inventory.has_sword:
            tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            tint.fill(CRITICAL_TINT)
            screen.blit(tint, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    print("Game over. Exiting...")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()