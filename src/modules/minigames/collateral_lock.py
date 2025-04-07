# src/modules/minigames/collateral_lock.py
import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT


def play_collateral_lock(screen, clock):
    print("Entering Collateral Lock minigame...")
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
    running = True
    result_message = ""
    result_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in Collateral Lock.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    player_input.append(int(pygame.key.name(event.key)))
                    if len(player_input) == len(sequence):
                        running = False
                        success = player_input == sequence
                        result_message = "Success! Sequence matched!" if success else "Failed! Wrong sequence."

        screen.blit(background, (0, 0))
        sequence_text = font.render("Sequence: " + " ".join(map(str, sequence)), True, WHITE)
        sequence_shadow = font.render("Sequence: " + " ".join(map(str, sequence)), True, BLACK)
        screen.blit(sequence_shadow, (SCREEN_WIDTH // 2 - sequence_text.get_width() // 2 + 2, 100 + 2))
        screen.blit(sequence_text, (SCREEN_WIDTH // 2 - sequence_text.get_width() // 2, 100))

        input_text = font.render("Your input: " + " ".join(map(str, player_input)), True, WHITE)
        input_shadow = font.render("Your input: " + " ".join(map(str, player_input)), True, BLACK)
        screen.blit(input_shadow, (SCREEN_WIDTH // 2 - input_text.get_width() // 2 + 2, 200 + 2))
        screen.blit(input_text, (SCREEN_WIDTH // 2 - input_text.get_width() // 2, 200))

        if result_message:
            result_text = font.render(result_message, True, WHITE)
            result_shadow = font.render(result_message, True, BLACK)
            screen.blit(result_shadow, (SCREEN_WIDTH // 2 - result_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2))
            result_timer += 1
            if result_timer > FPS * 2:
                break

        pygame.display.flip()
        clock.tick(FPS)

    success = player_input == sequence
    print("Exiting Collateral Lock minigame. Success:", success)
    return success