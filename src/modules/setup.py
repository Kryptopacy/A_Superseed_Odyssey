# src/modules/setup.py
import pygame
import sys
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, MORNING_GLORY, DEFAULT_FONT, MALE_SPRITE, FEMALE_SPRITE, TILE_SIZE

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