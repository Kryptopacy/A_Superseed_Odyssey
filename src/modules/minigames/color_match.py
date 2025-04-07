# src/modules/minigames/color_match.py
import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT


def play_color_match(screen, clock):
    print("Entering Color Match minigame...")
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

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    color_names = ["Red", "Green", "Blue", "Yellow"]
    current_color = random.choice(colors)
    current_name = random.choice(color_names)
    correct = color_names[colors.index(current_color)] == current_name
    score = 0
    timer = 0
    running = True
    result_message = ""
    result_timer = 0

    while running and timer < FPS * 15:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in Color Match.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_y:
                    if correct:
                        score += 1
                    else:
                        running = False
                        result_message = "Game Over! Wrong match."
                    current_color = random.choice(colors)
                    current_name = random.choice(color_names)
                    correct = color_names[colors.index(current_color)] == current_name
                elif event.key == pygame.K_n:
                    if not correct:
                        score += 1
                    else:
                        running = False
                        result_message = "Game Over! Wrong match."
                    current_color = random.choice(colors)
                    current_name = random.choice(color_names)
                    correct = color_names[colors.index(current_color)] == current_name

        timer += 1

        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, current_color, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 50, 100, 100))
        name_text = font.render(current_name, True, WHITE)
        name_shadow = font.render(current_name, True, BLACK)
        screen.blit(name_shadow, (SCREEN_WIDTH // 2 - name_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 60 + 2))
        screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        score_text = font.render(f"Score: {score}", True, WHITE)
        score_shadow = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_shadow, (20 + 2, 20 + 2))
        screen.blit(score_text, (20, 20))

        timer_text = font.render(f"Time: {(FPS * 15 - timer) // FPS}s", True, WHITE)
        timer_shadow = font.render(f"Time: {(FPS * 15 - timer) // FPS}s", True, BLACK)
        screen.blit(timer_shadow, (SCREEN_WIDTH - timer_text.get_width() - 20 + 2, 20 + 2))
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 20))

        if result_message:
            result_text = font.render(result_message, True, WHITE)
            result_shadow = font.render(result_message, True, BLACK)
            screen.blit(result_shadow,
                        (SCREEN_WIDTH // 2 - result_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 120 + 2))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))
            result_timer += 1
            if result_timer > FPS * 2:
                break

        pygame.display.flip()
        clock.tick(FPS)

    success = score >= 5
    if success and not result_message:
        result_message = "Success! You scored 5 points!"
        for _ in range(FPS * 2):
            screen.blit(background, (0, 0))
            result_text = font.render(result_message, True, WHITE)
            result_shadow = font.render(result_message, True, BLACK)
            screen.blit(result_shadow, (SCREEN_WIDTH // 2 - result_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            clock.tick(FPS)

    print("Exiting Color Match minigame. Success:", success)
    return success