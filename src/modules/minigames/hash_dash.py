# src/modules/minigames/hash_dash.py
import pygame
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT


def play_hash_dash(screen, clock):
    print("Entering Hash Dash minigame...")
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
    obstacles = []
    for _ in range(5):
        x = random.randint(0, SCREEN_WIDTH - 20)
        obstacles.append(pygame.Rect(x, 0, 20, 20))
    speed = 5
    score = 0
    running = True
    result_message = ""
    result_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in Hash Dash.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= speed
        if keys[pygame.K_RIGHT] and player.right < SCREEN_WIDTH:
            player.x += speed

        for obstacle in obstacles[:]:
            obstacle.y += speed
            if obstacle.colliderect(player):
                running = False
                result_message = "Game Over! You hit an obstacle."
            if obstacle.y > SCREEN_HEIGHT:
                obstacles.remove(obstacle)
                obstacles.append(pygame.Rect(random.randint(0, SCREEN_WIDTH - 20), 0, 20, 20))
                score += 1

        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, (0, 255, 0), player)
        for obstacle in obstacles:
            pygame.draw.rect(screen, (255, 0, 0), obstacle)

        score_text = font.render(f"Score: {score}", True, WHITE)
        score_shadow = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_shadow, (20 + 2, 20 + 2))
        screen.blit(score_text, (20, 20))

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

    success = score >= 10
    if success and not result_message:
        result_message = "Success! You scored 10 points!"
        for _ in range(FPS * 2):
            screen.blit(background, (0, 0))
            result_text = font.render(result_message, True, WHITE)
            result_shadow = font.render(result_message, True, BLACK)
            screen.blit(result_shadow, (SCREEN_WIDTH // 2 - result_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            clock.tick(FPS)

    print("Exiting Hash Dash minigame. Success:", success)
    return success