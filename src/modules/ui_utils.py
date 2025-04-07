# src/modules/ui_utils.py
import pygame
import sys
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


def show_tutorial(screen, dialogue_box, ui_background):
    print("Showing tutorial...")
    tutorial_lines = [
        "Welcome to A Superseed Odyssey!",
        "Controls: Arrow keys to move, J to melee attack, K for ranged attack, E to interact.",
        "O to activate Optimism Ring, R to load checkpoint, Y/N to play/skip minigames.",
        "Objective: Navigate the maze, collect tokens to reduce infection, and find the Sword of Solvency.",
        "Reach the green checkpoint or collect the orange fragment to progress.",
        "Move to the edges of the screen to transition between scenes."
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


def show_pause_menu(screen, player, dialogue_box, ui_background, world, checkpoints):
    print("Showing pause menu...")
    try:
        font = pygame.font.SysFont("Arial", 36)
    except:
        print("Failed to load font 'Arial'. Using default font.")
        font = pygame.font.Font(None, 36)

    options = ["Resume", "Tutorial", "Settings", "Restart", "Quit"]
    settings_options = ["Toggle Easy Mode", "Back"]
    restart_options = ["Restart from Checkpoint", "Restart Area", "Back"]
    selected = 0
    in_settings = False
    in_restart = False
    running = True

    while running:
        current_options = options
        if in_settings:
            current_options = settings_options
        elif in_restart:
            current_options = restart_options

        lines = []
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
                            start_x, start_y = current_scene.find_open_start_position()
                            player.rect.x, player.rect.y = start_x, start_y
                            player.hp = 100
                            player.infection_level = 50  # Reset to 50%
                            player.supercollateral = 0
                            player.fragments = 0
                            player.has_sword = False
                            running = False
                        elif current_options[selected] == "Back":
                            in_restart = False
                            selected = 0
                    else:
                        if current_options[selected] == "Resume":
                            running = False
                        elif current_options[selected] == "Tutorial":
                            show_tutorial(screen, dialogue_box, ui_background)
                        elif current_options[selected] == "Settings":
                            in_settings = True
                            selected = 0
                        elif current_options[selected] == "Restart":
                            in_restart = True
                            selected = 0
                        elif current_options[selected] == "Quit":
                            pygame.quit()
                            sys.exit()

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()


def prompt_easy_mode(screen, dialogue_box, player, ui_background):
    print("Prompting easy mode switch...")
    dialogue_box.show(["You've lost 3 times in a row...switch to easy mode? Press Y/N to decide."])
    choice_made = False
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
        pygame.display.flip()