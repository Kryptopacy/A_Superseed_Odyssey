# src/modules/minigames/gas_fee_gauntlet.py
import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT


def play_gas_fee_gauntlet(screen, clock):
    print("Entering Gas Fee Gauntlet minigame...")
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

    player = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, 30, 30)
    fees = []
    for _ in range(3):
        x = random.randint(0, SCREEN_WIDTH - 20)
        fees.append(pygame.Rect(x, 0, 20, 20))
    speed = 3
    timer = 0
    running = True
    result_message = ""
    result_timer = 0

    while running and timer < FPS * 10:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in Gas Fee Gauntlet.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= speed
        if keys[pygame.K_RIGHT] and player.right < SCREEN_WIDTH:
            player.x += speed

        for fee in fees[:]:
            fee.y += speed
            if fee.colliderect(player):
                running = False
                result_message = "Game Over! You hit a fee."
            if fee.y > SCREEN_HEIGHT:
                fees.remove(fee)
                fees.append(pygame.Rect(random.randint(0, SCREEN_WIDTH - 20), 0, 20, 20))

        timer += 1

        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, (0, 255, 0), player)
        for fee in fees:
            pygame.draw.rect(screen, (255, 215, 0), fee)

        timer_text = font.render(f"Time: {(FPS * 10 - timer) // FPS}s", True, WHITE)
        timer_shadow = font.render(f"Time: {(FPS * 10 - timer) // FPS}s", True, BLACK)
        screen.blit(timer_shadow, (20 + 2, 20 + 2))
        screen.blit(timer_text, (20, 20))

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

    success = timer >= FPS * 10
    if success and not result_message:
        result_message = "Success! You survived 10 seconds!"
        for _ in range(FPS * 2):
            screen.blit(background, (0, 0))
            result_text = font.render(result_message, True, WHITE)
            result_shadow = font.render(result_message, True, BLACK)
            screen.blit(result_shadow, (SCREEN_WIDTH // 2 - result_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            clock.tick(FPS)

    print("Exiting Gas Fee Gauntlet minigame. Success:", success)
    return success