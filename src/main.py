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
from src.modules.ui import DialogueBox, show_tutorial, show_pause_menu, prompt_easy_mode, prompt_game_over
from src.modules.world import World
from src.modules.game_state import save_game, load_game
from src.modules.setup import get_player_info
from src.modules.interactions import vendor_interaction, play_sword_puzzle, play_vitalik_puzzle, play_quest_minigame, final_cutscene, get_minigames
from src.modules.rendering import draw_ui, draw_labels, draw_exits, draw_minimap, apply_critical_tint
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE, WHITE, BLACK, GOLD, HUD_HEART_ICON, HUD_COIN_ICON, HUD_VIRUS_ICON, HUD_RING_ICON, MALE_SPRITE, FEMALE_SPRITE, EXIT_ARROW_SPRITE , DEFAULT_FONT, UI_BACKGROUND, MAZE_WIDTH, MAZE_HEIGHT, SOUND_GAME_MUSIC, SOUND_CUTSCENE_MUSIC, HUD_HEIGHT, SAPA_PROJECTILE

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

    # Load Sapa projectile sprite
    sapa_projectile_sprite = None
    try:
        print(f"Attempting to load Sapa projectile sprite from: {SAPA_PROJECTILE}")
        if not os.path.exists(SAPA_PROJECTILE):
            raise FileNotFoundError(f"File not found: {SAPA_PROJECTILE}")
        sapa_projectile_sprite = pygame.image.load(SAPA_PROJECTILE).convert_alpha()
        sapa_projectile_sprite = pygame.transform.scale(sapa_projectile_sprite, (10, 10))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load Sapa projectile sprite at {SAPA_PROJECTILE}. Error: {e}. Using placeholder.")
        sapa_projectile_sprite = None

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

    # Load Exit Arrow sprite
    exit_arrow_sprite = None
    try:
        print(f"Attempting to load exit arrow sprite from: {EXIT_ARROW_SPRITE}")
        if not os.path.exists(EXIT_ARROW_SPRITE):
            raise FileNotFoundError(f"File not found: {EXIT_ARROW_SPRITE}")
        exit_arrow_sprite = pygame.image.load(EXIT_ARROW_SPRITE).convert_alpha()
        exit_arrow_sprite = pygame.transform.scale(exit_arrow_sprite, (30, 30))
    except (pygame.error, FileNotFoundError, Exception) as e:
        print(f"Failed to load exit arrow sprite at {EXIT_ARROW_SPRITE}. Error: {e}. Using placeholder.")
        exit_arrow_sprite = None

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

    # Use the minigames list from interactions.py
    minigames = get_minigames()
    vitalik_freed = game_state['vitalik_freed'] if game_state else False
    choice_made = game_state['choice_made'] if game_state else False
    self_save_choice_made = game_state['self_save_choice_made'] if game_state else False
    world_choice_made = game_state.get('world_choice_made', False) if game_state else False
    first_vendor_spawn = True  # Flag to track first vendor spawn

    # Place Vitalik in Area 0, Scene 2, and multiple regular NPCs in the same scene
    for area in world.areas:
        for scene in area.scenes:
            if area.area_id == 0 and scene.scene_id == 2 and not vitalik_freed:
                scene.npc = NPC(scene, is_vitalik=True)
                # Add multiple regular NPCs to show people escaping the Sapa
                scene.npcs = []
                # First NPC with specific lore
                npc_with_lore = NPC(scene, is_vitalik=False)
                npc_with_lore.lore = ["The gods rendered this area free of Sapa while Vitalik remained trapped."]
                scene.npcs.append(npc_with_lore)
                # Add 2-4 additional regular NPCs
                num_additional_npcs = random.randint(2, 4)
                for _ in range(num_additional_npcs):
                    new_npc = NPC(scene, is_vitalik=False)
                    scene.npcs.append(new_npc)
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
                    show_minimap = show_pause_menu(screen, player, dialogue_box, ui_background, world, checkpoints, music_volume, sfx_volume, vitalik_freed, choice_made, self_save_choice_made, vitalik, current_scene)
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
                                if not vitalik_cutscene(screen, clock, player, dialogue_box, ui_background):
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
                            if self_save_choice_made and player.inventory.has_sword:
                                choice_made = False
                                self_save_choice_made = False
                                infection_active = False
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
            # Sapa spawning logic: Maintain up to 5 Sapa as per screenshot
            if (world.current_area > 0 or world.current_scene != 2) and len(sapas) < 5:
                if random.random() < 0.05:  # Adjusted probability to maintain 5 Sapa
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
                    print(f"Spawned new Sapa: {new_sapa.name}, Total Sapa: {len(sapas)}")

            keys = pygame.key.get_pressed()
            player.move(keys, current_scene.maze)

            entry_x, entry_y = current_scene.entry
            exit_x, exit_y = current_scene.exit

            # Calculate tile_height to match Scene.draw
            playable_height = SCREEN_HEIGHT - HUD_HEIGHT
            tile_height = playable_height / MAZE_HEIGHT

            # Adjust entry_rect and exit_rect to cover the entire opening (2 tiles wide/tall)
            if entry_x == 0:  # Left side
                entry_rect = pygame.Rect(0, (entry_y * tile_height) + HUD_HEIGHT, TILE_SIZE, 2 * tile_height)
            elif entry_y == 0:  # Top side
                entry_rect = pygame.Rect(entry_x * TILE_SIZE, HUD_HEIGHT, 2 * TILE_SIZE, tile_height)
            else:  # Bottom side
                entry_rect = pygame.Rect(entry_x * TILE_SIZE, (entry_y * tile_height) + HUD_HEIGHT, 2 * TILE_SIZE,
                                         tile_height)

            if exit_x == MAZE_WIDTH - 1:  # Right side
                exit_rect = pygame.Rect((exit_x * TILE_SIZE), (exit_y * tile_height) + HUD_HEIGHT, TILE_SIZE,
                                        2 * tile_height)
            elif exit_y == MAZE_HEIGHT - 1:  # Bottom side
                exit_rect = pygame.Rect(exit_x * TILE_SIZE, SCREEN_HEIGHT - 2 * tile_height, 2 * TILE_SIZE,
                                        2 * tile_height)
            else:  # Top side
                exit_rect = pygame.Rect(exit_x * TILE_SIZE, HUD_HEIGHT, 2 * TILE_SIZE, tile_height)

            # Debug entry/exit collision
            if "west" in current_scene.exits and player.rect.colliderect(entry_rect):
                print(f"Player collided with entry at ({entry_x}, {entry_y}), moving west.")
                world.move_to_scene("west")
                current_scene = world.get_current_scene()
                start_x, start_y = current_scene.maze.find_open_start_position()
                player.rect.x, player.rect.y = start_x, start_y
                if vitalik and vitalik.following:
                    vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                current_scene.sapas.clear()
                current_scene.npcs = []  # Reset NPCs
                current_scene.sword = None  # Reset sword
                current_scene.minigame = None  # Reset minigame
                projectiles.clear()

            if "east" in current_scene.exits and player.rect.colliderect(exit_rect):
                # Prevent moving east from Area 0, Scene 2 if Vitalik is not freed
                if world.current_area == 0 and world.current_scene == 2 and not vitalik_freed:
                    paused = True  # Pause the game to handle the prompt
                    dialogue_box.show(["Vitalik: You must free me before we can proceed! Press E to interact."])
                    while dialogue_box.active:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                print("Quit event in prompt.")
                                game_over = True
                                break
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    dialogue_box.next_line()
                                elif event.key == pygame.K_ESCAPE:
                                    dialogue_box.active = False
                        screen.fill(BLACK)
                        current_scene.draw(screen)
                        for sapa in sapas:
                            sapa.draw(screen)
                        for proj in projectiles:
                            rect, dx, dy = proj
                            if sapa_projectile_sprite:
                                screen.blit(sapa_projectile_sprite, (rect.x, rect.y))
                            else:
                                pygame.draw.rect(screen, (255, 0, 0), rect)
                        if current_scene.npc:
                            current_scene.npc.draw(screen)
                        if hasattr(current_scene, 'npcs'):
                            for npc in current_scene.npcs:
                                npc.draw(screen)
                        player.draw(screen)
                        combat.draw(screen)
                        draw_ui(screen, player, world, font, heart_icon, coin_icon, virus_icon, ring_icon,
                                infection_active)
                        draw_labels(screen, current_scene, player, font)
                        draw_exits(screen, current_scene, font, exit_arrow_sprite)
                        if show_minimap:
                            draw_minimap(screen, current_scene, player, font)
                        apply_critical_tint(screen, infection_active, player)
                        dialogue_box.draw(screen)
                        pygame.display.flip()
                        clock.tick(FPS)
                    paused = False
                    continue
                print(f"Player collided with exit at ({exit_x}, {exit_y}), moving east. Exit rect: {exit_rect}")
                world.move_to_scene("east")
                current_scene = world.get_current_scene()
                start_x, start_y = current_scene.maze.find_open_start_position()
                player.rect.x, player.rect.y = start_x, start_y
                if vitalik and vitalik.following:
                    vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                current_scene.sapas.clear()
                current_scene.npcs = []  # Reset NPCs
                # Only reset the sword if the player doesn't have it and hasn't chosen the "world" option
                if not player.inventory.has_sword or not world_choice_made:
                    current_scene.sword = None
                current_scene.minigame = None  # Reset minigame
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
                if not vitalik_cutscene(screen, clock, player, dialogue_box, ui_background):
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
                choice = vitalik_choice(screen, clock, player, dialogue_box, ui_background)
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
                    world_choice_made = True
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
                            current_scene.npcs = []  # Reset NPCs
                            # Only reset the sword if the player doesn't have it and hasn't chosen the "world" option
                            if not player.inventory.has_sword or not world_choice_made:
                                current_scene.sword = None
                            current_scene.minigame = None  # Reset minigame
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
                    choice = prompt_game_over(screen, dialogue_box, player, world, checkpoints, ui_background)
                    if choice == "start_over":
                        # Full reset of game state
                        world.current_area = 0
                        world.current_scene = 0
                        world = World(player, vitalik_freed=False)  # Reinitialize world
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
                        world_choice_made = False
                        first_vendor_spawn = True
                        vitalik = None
                        current_scene.sapas.clear()
                        current_scene.npcs = []  # Reset NPCs
                        current_scene.sword = None  # Reset sword
                        current_scene.minigame = None  # Reset minigame
                        projectiles.clear()
                        consecutive_losses = 0
                        print("Game state fully reset after 'start over'.")
                    elif choice == "resume":
                        checkpoints.load(player)
                        current_scene.sapas.clear()
                        current_scene.npcs = []  # Reset NPCs
                        current_scene.sword = None  # Reset sword
                        current_scene.minigame = None  # Reset minigame
                        projectiles.clear()
                        consecutive_losses = 0
                    elif choice == "restart_area":
                        world.current_scene = 0
                        current_scene = world.get_current_scene()
                        start_x, start_y = current_scene.maze.find_open_start_position()
                        player.rect.x, player.rect.y = start_x, start_y
                        player.hp = 100  # Reset HP but keep other progress
                        player.infection_level = 50  # Reset infection
                        if vitalik and vitalik.following:
                            vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                        current_scene.sapas.clear()
                        current_scene.npcs = []  # Reset NPCs
                        current_scene.sword = None  # Reset sword
                        current_scene.minigame = None  # Reset minigame
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

            paused = True
            choice = prompt_game_over(screen, dialogue_box, player, world, checkpoints, ui_background)
            if choice == "start_over":
                # Full reset of game state
                world.current_area = 0
                world.current_scene = 0
                world = World(player, vitalik_freed=False)  # Reinitialize world
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
                world_choice_made = False
                first_vendor_spawn = True
                vitalik = None
                current_scene.sapas.clear()
                current_scene.npcs = []  # Reset NPCs
                current_scene.sword = None  # Reset sword
                current_scene.minigame = None  # Reset minigame
                projectiles.clear()
                consecutive_losses = 0
                last_scene = None
                last_area = -1
                print("Game state fully reset after 'start over'.")
            elif choice == "resume":
                checkpoints.load(player)
                current_scene.sapas.clear()
                current_scene.npcs = []  # Reset NPCs
                current_scene.sword = None  # Reset sword
                current_scene.minigame = None  # Reset minigame
                projectiles.clear()
                consecutive_losses = 0
            elif choice == "restart_area":
                world.current_scene = 0
                current_scene = world.get_current_scene()
                start_x, start_y = current_scene.maze.find_open_start_position()
                player.rect.x, player.rect.y = start_x, start_y
                player.hp = 100  # Reset HP but keep other progress
                player.infection_level = 50  # Reset infection
                if vitalik and vitalik.following:
                    vitalik.rect.x, vitalik.rect.y = start_x + TILE_SIZE, start_y
                current_scene.sapas.clear()
                current_scene.npcs = []  # Reset NPCs
                current_scene.sword = None  # Reset sword
                current_scene.minigame = None  # Reset minigame
                projectiles.clear()
                consecutive_losses = 0
            paused = False
            continue

        # Ensure the background is drawn first to avoid overwriting tiles
        screen.fill(BLACK)  # Clear the screen to prevent artifacts
        current_scene.draw(screen)
        for sapa in sapas:
            sapa.draw(screen)
        for proj in projectiles:
            rect, dx, dy = proj
            if sapa_projectile_sprite:
                screen.blit(sapa_projectile_sprite, (rect.x, rect.y))
            else:
                pygame.draw.rect(screen, (255, 0, 0), rect)
        if current_scene.npc:
            current_scene.npc.draw(screen)
        if hasattr(current_scene, 'npcs'):
            for npc in current_scene.npcs:
                npc.draw(screen)
        player.draw(screen)
        combat.draw(screen)
        draw_ui(screen, player, world, font, heart_icon, coin_icon, virus_icon, ring_icon, infection_active)
        draw_labels(screen, current_scene, player, font)
        draw_exits(screen, current_scene, font, exit_arrow_sprite)  # Pass exit_arrow_sprite here
        if show_minimap:
            draw_minimap(screen, current_scene, player, font)
        apply_critical_tint(screen, infection_active, player)
        dialogue_box.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    print("Game over. Exiting...")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()