# src/modules/minigames/memory_sequence.py
import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT


def play_memory_sequence(screen, clock):
    print("Entering Memory Sequence minigame...")
    try:
        font = pygame.font.SysFont(DEFAULT_FONT, 36)
    except:
        print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
        font = pygame.font.Font(None, 36)

    # Gradient background
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        r = 14 + (y / SCREEN_HEIGHT) * (50 - 14)
        g = 39 + (y / SCREEN_HEIGHT) * (70 - 39)
        b = 59 + (y / SCREEN_HEIGHT) * (100 - 59)
        pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))

    sequence = [random.randint(1, 4) for _ in range(4)]
    player_input = []
    showing_sequence = True
    current_display = 0
    timer = 0
    running = True
    result_message = ""
    result_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in Memory Sequence.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not showing_sequence and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    player_input.append(int(pygame.key.name(event.key)))
                    if len(player_input) == len(sequence):
                        running = False
                        success = player_input == sequence
                        result_message = "Success! Sequence matched!" if success else "Failed! Wrong sequence."

        if showing_sequence:
            timer += 1
            if timer >= FPS:
                current_display += 1
                timer = 0
                if current_display >= len(sequence):
                    showing_sequence = False

        screen.blit(background, (0, 0))
        if showing_sequence and current_display < len(sequence):
            seq_text = font.render(str(sequence[current_display]), True, WHITE)
            seq_shadow = font.render(str(sequence[current_display]), True, BLACK)
            screen.blit(seq_shadow, (
            SCREEN_WIDTH // 2 - seq_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 - seq_text.get_height() // 2 + 2))
            screen.blit(seq_text, (
            SCREEN_WIDTH // 2 - seq_text.get_width() // 2, SCREEN_HEIGHT // 2 - seq_text.get_height() // 2))
        elif not showing_sequence:
            input_text = font.render("Your input: " + " ".join(map(str, player_input)), True, WHITE)
            input_shadow = font.render("Your input: " + " ".join(map(str, player_input)), True, BLACK)
            screen.blit(input_shadow, (
            SCREEN_WIDTH // 2 - input_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 - input_text.get_height() // 2 + 2))
            screen.blit(input_text, (
            SCREEN_WIDTH // 2 - input_text.get_width() // 2, SCREEN_HEIGHT // 2 - input_text.get_height() // 2))

        if result_message:
            result_text = font.render(result_message, True, WHITE)
            result_shadow = font.render(result_message, True, BLACK)
            screen.blit(result_shadow,
                        (SCREEN_WIDTH // 2 - result_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 50 + 2))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            result_timer += 1
            if result_timer > FPS * 2:
                break

        pygame.display.flip()
        clock.tick(FPS)

    success = player_input == sequence
    print("Exiting Memory Sequence minigame. Success:", success)
    return success