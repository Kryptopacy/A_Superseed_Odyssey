# src/modules/ui.py
import pygame
import sys
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, GOLD, DEFAULT_FONT
from src.utils import wrap_text

class DialogueBox:
    def __init__(self):
        self.active = False
        self.lines = []
        self.current_line = 0
        try:
            self.font = pygame.font.SysFont(DEFAULT_FONT, 36)
            self.speaker_font = pygame.font.SysFont(DEFAULT_FONT, 24, bold=True)
            self.prompt_font = pygame.font.SysFont(DEFAULT_FONT, 20)
        except:
            print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
            self.font = pygame.font.Font(None, 36)
            self.speaker_font = pygame.font.Font(None, 24)
            self.prompt_font = pygame.font.Font(None, 20)
        self.max_width = int(SCREEN_WIDTH * 0.8) - 20
        self.show_prompt = True

    def show(self, lines, show_prompt=True):
        self.lines = lines
        self.current_line = 0
        self.active = True
        self.show_prompt = show_prompt

    def next_line(self):
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.active = False

    def draw(self, screen):
        if not self.active or self.current_line >= len(self.lines):
            return

        box_width = int(SCREEN_WIDTH * 0.8)
        box_height = 150
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = SCREEN_HEIGHT - box_height - 20

        dialogue_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        dialogue_box.fill((0, 0, 0, 180))
        pygame.draw.rect(dialogue_box, WHITE, (0, 0, box_width, box_height), 3)

        glow_surface = pygame.Surface((box_width + 20, box_height + 20), pygame.SRCALPHA)
        for i in range(5):
            pygame.draw.rect(glow_surface, (GOLD[0], GOLD[1], GOLD[2], 50 - i * 10),
                             (i, i, box_width + 20 - 2 * i, box_height + 20 - 2 * i), 2)

        screen.blit(glow_surface, (box_x - 10, box_y - 10))
        screen.blit(dialogue_box, (box_x, box_y))

        line = self.lines[self.current_line]
        if ": " in line:
            speaker, text = line.split(": ", 1)
            speaker_text = self.speaker_font.render(speaker + ": ", True, GOLD)
            speaker_shadow = self.speaker_font.render(speaker + ": ", True, BLACK)
            wrapped_lines = wrap_text(text, self.font, self.max_width - speaker_text.get_width())
            screen.blit(speaker_shadow, (box_x + 12, box_y + 12))
            screen.blit(speaker_text, (box_x + 10, box_y + 10))
            for i, wrapped_line in enumerate(wrapped_lines):
                # Highlight action keys in gold
                parts = wrapped_line.split()
                x_offset = speaker_text.get_width() + 10
                for part in parts:
                    color = GOLD if part in ("S", "R", "ESC", "Y", "N", "1", "2", "3", "4", "5") else WHITE
                    text_surface = self.font.render(part + " ", True, color)
                    text_shadow = self.font.render(part + " ", True, BLACK)
                    screen.blit(text_shadow, (box_x + x_offset + 2, box_y + 12 + i * 40))
                    screen.blit(text_surface, (box_x + x_offset, box_y + 10 + i * 40))
                    x_offset += text_surface.get_width()
        else:
            wrapped_lines = wrap_text(line, self.font, self.max_width)
            for i, wrapped_line in enumerate(wrapped_lines):
                # Highlight action keys in gold
                parts = wrapped_line.split()
                x_offset = 10
                for part in parts:
                    color = GOLD if part in ("S", "R", "ESC", "Y", "N", "1", "2", "3", "4", "5") else WHITE
                    text_surface = self.font.render(part + " ", True, color)
                    text_shadow = self.font.render(part + " ", True, BLACK)
                    screen.blit(text_shadow, (box_x + x_offset + 2, box_y + 12 + i * 40))
                    screen.blit(text_surface, (box_x + x_offset, box_y + 10 + i * 40))
                    x_offset += text_surface.get_width()

        # Render prompt externally
        if self.show_prompt:
            prompt_text = self.prompt_font.render("Press SPACE to continue, or ESC to skip", True, WHITE)
            prompt_shadow = self.prompt_font.render("Press SPACE to continue, or ESC to skip", True, BLACK)
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            screen.blit(prompt_shadow, (prompt_rect.x + 2, prompt_rect.y + 2))
            screen.blit(prompt_text, prompt_rect)

def show_tutorial(screen, dialogue_box, ui_background):
    print("Showing tutorial...")
    tutorial_lines = [
        "Welcome to A Superseed Odyssey!",
        "Controls: Arrow keys to move, J to melee attack, K for ranged attack, E to interact.",
        "O to activate Optimism Ring, R to load checkpoint, Y/N to play/skip minigames.",
        "Objective: Navigate the maze, collect tokens to reduce infection, and find the Sword of Solvency.",
        "Reach the checkpoint or collect the fragment to progress.",
        "Move to exit to transition between scenes."
    ]
    dialogue_box.show(tutorial_lines)
    while dialogue_box.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in tutorial.")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in tutorial: {event.key}")
                if event.key == pygame.K_SPACE:
                    dialogue_box.next_line()

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()

def show_pause_menu(screen, player, dialogue_box, ui_background, world, checkpoints, music_volume, sfx_volume):
    print("Showing pause menu...")
    try:
        font = pygame.font.SysFont("Arial", 36)
    except:
        print("Failed to load font 'Arial'. Using default font.")
        font = pygame.font.Font(None, 36)

    options = ["Resume", "Tutorial", "Toggle Minimap", "Toggle Easy Mode", "Restart", "Adjust Sound", "Save Game", "Load Game", "Quit"]
    settings_options = ["Toggle Easy Mode", "Back"]
    restart_options = ["Restart from Checkpoint", "Restart Area", "Back"]
    sound_options = ["Music Volume Up", "Music Volume Down", "SFX Volume Up", "SFX Volume Down", "Back"]
    selected = 0
    in_settings = False
    in_restart = False
    in_sound = False
    running = True
    show_minimap = False

    while running:
        current_options = options
        if in_settings:
            current_options = settings_options
        elif in_restart:
            current_options = restart_options
        elif in_sound:
            current_options = sound_options

        lines = []
        if in_sound:
            lines.append(f"Music Volume: {int(music_volume * 100)}%")
            lines.append(f"SFX Volume: {int(sfx_volume * 100)}%")
        for i, option in enumerate(current_options):
            prefix = "> " if i == selected else "  "
            if in_settings and option == "Toggle Easy Mode":
                mode = "Easy" if player.easy_mode else "Normal"
                lines.append(f"{prefix}Toggle Easy Mode: {mode}")
            else:
                lines.append(f"{prefix}{option}")
        dialogue_box.show(lines)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in pause menu.")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in pause menu: {event.key}")
                if event.key == pygame.K_SPACE and dialogue_box.active:
                    dialogue_box.next_line()
                elif event.key == pygame.K_UP and not dialogue_box.active:
                    selected = (selected - 1) % len(current_options)
                elif event.key == pygame.K_DOWN and not dialogue_box.active:
                    selected = (selected + 1) % len(current_options)
                elif event.key == pygame.K_RETURN and not dialogue_box.active:
                    if in_settings:
                        if current_options[selected] == "Toggle Easy Mode":
                            player.easy_mode = not player.easy_mode
                            dialogue_box.show([f"Mode switched to {'Easy' if player.easy_mode else 'Normal'}!"])
                        elif current_options[selected] == "Back":
                            in_settings = False
                            selected = 0
                    elif in_restart:
                        if current_options[selected] == "Restart from Checkpoint":
                            checkpoints.load(player)
                            running = False
                        elif current_options[selected] == "Restart Area":
                            world.current_scene = 0
                            current_scene = world.get_current_scene()
                            start_x, start_y = current_scene.maze.find_open_start_position()
                            player.rect.x, player.rect.y = start_x, start_y
                            player.hp = 100
                            player.infection_level = 50
                            player.inventory.supercollateral = 0
                            player.inventory.fragments = 0
                            player.inventory.has_sword = False
                            running = False
                        elif current_options[selected] == "Back":
                            in_restart = False
                            selected = 0
                    elif in_sound:
                        if current_options[selected] == "Music Volume Up":
                            music_volume = min(1.0, music_volume + 0.1)
                            pygame.mixer.music.set_volume(music_volume)
                        elif current_options[selected] == "Music Volume Down":
                            music_volume = max(0.0, music_volume - 0.1)
                            pygame.mixer.music.set_volume(music_volume)
                        elif current_options[selected] == "SFX Volume Up":
                            sfx_volume = min(1.0, sfx_volume + 0.1)
                        elif current_options[selected] == "SFX Volume Down":
                            sfx_volume = max(0.0, sfx_volume - 0.1)
                        elif current_options[selected] == "Back":
                            in_sound = False
                            selected = 0
                    else:
                        if current_options[selected] == "Resume":
                            running = False
                        elif current_options[selected] == "Tutorial":
                            show_tutorial(screen, dialogue_box, ui_background)
                        elif current_options[selected] == "Toggle Minimap":
                            show_minimap = not show_minimap
                            dialogue_box.show([f"Minimap {'enabled' if show_minimap else 'disabled'}!"])
                        elif current_options[selected] == "Toggle Easy Mode":
                            in_settings = True
                            selected = 0
                        elif current_options[selected] == "Restart":
                            in_restart = True
                            selected = 0
                        elif current_options[selected] == "Adjust Sound":
                            in_sound = True
                            selected = 0
                        elif current_options[selected] == "Save Game":
                            save_game(player, world, vitalik_freed, choice_made, self_save_choice_made, vitalik)
                            dialogue_box.show(["Game saved successfully!"])
                        elif current_options[selected] == "Load Game":
                            game_state = load_game()
                            if game_state:
                                player.rect.x, player.rect.y = game_state['player']['rect']
                                player.hp = game_state['player']['hp']
                                player.infection_level = game_state['player']['infection_level']
                                player.attack_power = game_state['player']['attack_power']
                                player.ranged_attacks = game_state['player']['ranged_attacks']
                                player.optimism_ring_duration = game_state['player']['optimism_ring_duration']
                                player.optimism_ring_timer = game_state['player']['optimism_ring_timer']
                                player.easy_mode = game_state['player']['easy_mode']
                                player.inventory.supercollateral = game_state['player']['inventory']['supercollateral']
                                player.inventory.fragments = game_state['player']['inventory']['fragments']
                                player.inventory.has_sword = game_state['player']['inventory']['has_sword']
                                world.current_area = game_state['world']['current_area']
                                world.current_scene = game_state['world']['current_scene']
                                vitalik_freed = game_state['vitalik_freed']
                                choice_made = game_state['choice_made']
                                self_save_choice_made = game_state['self_save_choice_made']
                                if game_state['vitalik']['rect']:
                                    vitalik = NPC(current_scene, is_vitalik=True)
                                    vitalik.is_freed = game_state['vitalik']['is_freed']
                                    vitalik.following = game_state['vitalik']['following']
                                    vitalik.invulnerable = game_state['vitalik']['invulnerable']
                                    vitalik.rect.x, vitalik.rect.y = game_state['vitalik']['rect']
                                    current_scene.npc = vitalik
                                dialogue_box.show(["Game loaded successfully!"])
                            else:
                                dialogue_box.show(["No saved game found!"])
                        elif current_options[selected] == "Quit":
                            pygame.quit()
                            sys.exit()

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()

    return show_minimap

def prompt_easy_mode(screen, dialogue_box, player, ui_background):
    print("Prompting easy mode switch...")
    dialogue_box.show(["You've lost 3 times in a row...switch to easy mode? Press Y/N to decide."], show_prompt=False)
    choice_made = False
    prompt_font = pygame.font.SysFont(DEFAULT_FONT, 20)
    prompt_text = prompt_font.render("Press Y/N to decide", True, WHITE)
    prompt_shadow = prompt_font.render("Press Y/N to decide", True, BLACK)
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in easy mode prompt.")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in easy mode prompt: {event.key}")
                if event.key == pygame.K_y:
                    player.easy_mode = True
                    choice_made = True
                    dialogue_box.show(["Switched to Easy Mode!"])
                elif event.key == pygame.K_n:
                    choice_made = True
                    dialogue_box.show(["Continuing in Normal Mode."])

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        screen.blit(prompt_shadow, (prompt_rect.x + 2, prompt_rect.y + 2))
        screen.blit(prompt_text, prompt_rect)
        pygame.display.flip()