# src/modules/minigames/anagram.py
import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT


def play_anagram(screen, clock):
    print("Entering Anagram minigame...")
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

    words = ["BLOCK", "CHAIN", "TOKEN", "WALLET"]
    word = random.choice(words)
    scrambled = "".join(random.sample(word, len(word)))
    player_input = ""
    running = True
    result_message = ""
    result_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in Anagram.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN:
                    running = False
                    success = player_input == word
                    result_message = "Success! Correct word!" if success else f"Failed! The word was {word}."
                elif event.key == pygame.K_BACKSPACE:
                    player_input = player_input[:-1]
                elif event.unicode.isalpha():
                    player_input += event.unicode.upper()

        screen.blit(background, (0, 0))
        scrambled_text = font.render(f"Scrambled: {scrambled}", True, WHITE)
        scrambled_shadow = font.render(f"Scrambled: {scrambled}", True, BLACK)
        screen.blit(scrambled_shadow, (SCREEN_WIDTH // 2 - scrambled_text.get_width() // 2 + 2, 100 + 2))
        screen.blit(scrambled_text, (SCREEN_WIDTH // 2 - scrambled_text.get_width() // 2, 100))

        input_text = font.render(f"Your guess: {player_input}", True, WHITE)
        input_shadow = font.render(f"Your guess: {player_input}", True, BLACK)
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

    success = player_input == word
    print("Exiting Anagram minigame. Success:", success)
    return success