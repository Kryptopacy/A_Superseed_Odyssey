# src/modules/minigames/sapa_dodge.py
import pygame
import random
import os
# Import necessary assets from config
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT,
    UI_BACKGROUND, SAPA_SPRITE, MALE_SPRITE, FEMALE_SPRITE
)

# --- Constants ---
# Colors (Used mainly for fallbacks and text)
SHADOW_COLOR = (50, 50, 50)
GRADIENT_START = (14, 39, 59)
GRADIENT_END = (50, 70, 100)
PROMPT_COLOR = (200, 200, 200)
FALLBACK_PLAYER_COLOR = (0, 200, 0)
FALLBACK_SAPA_COLOR = (200, 0, 0) # Sapa represented as red if sprite fails
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)

# Font
SCORE_FONT_SIZE = 36 # For timer display
INSTR_FONT_SIZE = 24
PROMPT_FONT_SIZE = 20
DEFAULT_FONT_NAME = DEFAULT_FONT

# Layout
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
INSTR_Y = 30
TIMER_POS = (20, 20) # Top-left
RESULT_Y_OFFSET = 0
PROMPT_Y_OFFSET = 40
SHADOW_OFFSET = (2, 2)

# Gameplay Elements - Fallback sizes if sprites fail
FALLBACK_PLAYER_WIDTH = 30
FALLBACK_PLAYER_HEIGHT = 30
FALLBACK_SAPA_WIDTH = 20
FALLBACK_SAPA_HEIGHT = 20

# Initial difficulty tuning (adjust as needed)
PLAYER_SPEED = 5
SAPA_SPEED = 6
INITIAL_SAPA_COUNT = 10

# Timing / Goal
SURVIVAL_TIME_SECONDS = 20
# Display time for SUCCESS message
RESULT_SUCCESS_DISPLAY_SECONDS = 1.5
RESULT_SUCCESS_DISPLAY_FRAMES = int(FPS * RESULT_SUCCESS_DISPLAY_SECONDS)

# Keys
START_KEY = pygame.K_RETURN
RETRY_KEY = pygame.K_r
CONTINUE_KEY = pygame.K_RETURN


# --- Helper Function ---
# Assume draw_text_with_shadow is available
def draw_text_with_shadow(screen, text, font, position, color, shadow_color, shadow_offset=SHADOW_OFFSET, center=True, topright=False):
    """Renders text with shadow. Can align center, topright, or topleft."""
    text_surface = font.render(text, True, color)
    shadow_surface = font.render(text, True, shadow_color)
    if topright:
        text_rect = text_surface.get_rect(topright=position)
        shadow_rect = shadow_surface.get_rect(topright=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    elif center:
        text_rect = text_surface.get_rect(center=position)
        shadow_rect = shadow_surface.get_rect(center=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    else: # top-left
        text_rect = text_surface.get_rect(topleft=position)
        shadow_rect = shadow_surface.get_rect(topleft=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    screen.blit(shadow_surface, shadow_rect)
    screen.blit(text_surface, text_rect)


# --- Main Minigame Function ---

# Updated function signature to accept player_gender
def play_sapa_dodge(screen, clock, player_gender):
    """
    Runs the Sapa Dodge minigame (survival objective) with sprites and retry.
    player_gender should be a string ('male', 'female', etc.) to select the correct sprite.
    Returns: True (survived), False (hit sapa), None (cancelled).
    """
    print(f"Entering Sapa Dodge minigame for player gender: {player_gender}...")

    # --- Initialization ---
    try:
        timer_font = pygame.font.SysFont(DEFAULT_FONT_NAME, SCORE_FONT_SIZE)
        instr_font = pygame.font.SysFont(DEFAULT_FONT_NAME, INSTR_FONT_SIZE)
        prompt_font = pygame.font.SysFont(DEFAULT_FONT_NAME, PROMPT_FONT_SIZE)
    except Exception as e:
        print(f"Failed to load system font '{DEFAULT_FONT_NAME}': {e}. Using default.")
        timer_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        instr_font = pygame.font.Font(None, INSTR_FONT_SIZE)
        prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)

    # --- Load Assets ---
    # Background
    background_surface = None
    try:
        if UI_BACKGROUND and os.path.exists(UI_BACKGROUND):
            background_surface = pygame.image.load(UI_BACKGROUND).convert()
            background_surface = pygame.transform.scale(background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Loaded UI_BACKGROUND asset.")
        else: print("UI_BACKGROUND path not found or empty.")
    except Exception as e: print(f"Failed to load UI_BACKGROUND: {e}")

    if background_surface is None:
        print("Using fallback gradient background.")
        background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = GRADIENT_START[0] + t * (GRADIENT_END[0] - GRADIENT_START[0])
            g = GRADIENT_START[1] + t * (GRADIENT_END[1] - GRADIENT_START[1])
            b = GRADIENT_START[2] + t * (GRADIENT_END[2] - GRADIENT_START[2])
            background_surface.fill((int(r), int(g), int(b)), (0, y, SCREEN_WIDTH, 1))

    # Player Sprite
    player_sprite = None
    player_width, player_height = FALLBACK_PLAYER_WIDTH, FALLBACK_PLAYER_HEIGHT
    player_sprite_path = MALE_SPRITE if player_gender.lower() == 'male' else FEMALE_SPRITE
    try:
        if player_sprite_path and os.path.exists(player_sprite_path):
            player_sprite = pygame.image.load(player_sprite_path).convert_alpha()
            # Optional: Scale player sprite if needed
            # player_sprite = pygame.transform.scale(player_sprite, (desired_w, desired_h))
            player_width, player_height = player_sprite.get_size()
            print(f"Loaded player sprite: {player_sprite_path}")
        else: print(f"Player sprite path not found or empty: {player_sprite_path}")
    except Exception as e: print(f"Failed to load player sprite: {e}")

    if player_sprite is None:
        print("Using fallback rect for player.")

    # Sapa Sprite
    sapa_sprite = None
    sapa_width, sapa_height = FALLBACK_SAPA_WIDTH, FALLBACK_SAPA_HEIGHT
    try:
        if SAPA_SPRITE and os.path.exists(SAPA_SPRITE):
            sapa_sprite = pygame.image.load(SAPA_SPRITE).convert_alpha()
            # Optional: Scale sapa sprite if needed
            # sapa_sprite = pygame.transform.scale(sapa_sprite, (desired_w, desired_h))
            sapa_width, sapa_height = sapa_sprite.get_size()
            print(f"Loaded sapa sprite: {SAPA_SPRITE}")
        else: print(f"Sapa sprite path not found or empty: {SAPA_SPRITE}")
    except Exception as e: print(f"Failed to load sapa sprite: {e}")

    if sapa_sprite is None:
        print("Using fallback rect for sapa.")

    # --- Game State Variables ---
    player_start_y = SCREEN_HEIGHT - player_height - 10
    player = pygame.Rect(CENTER_X - player_width // 2, player_start_y, player_width, player_height)
    sapa_list = [] # Store Rects for falling sapa
    start_time = 0
    elapsed_time = 0
    success = False
    result_message = ""
    result_timer = 0

    game_state = "WAITING_START"
    final_outcome = None

    def _reset_game():
        """Resets player position and sapa."""
        nonlocal player, sapa_list, start_time, elapsed_time
        player.centerx = CENTER_X
        player.bottom = player_start_y + player_height
        sapa_list.clear()
        for _ in range(INITIAL_SAPA_COUNT):
            x = random.randint(0, SCREEN_WIDTH - sapa_width)
            y = random.randint(-SCREEN_HEIGHT // 2, 0)
            sapa_list.append(pygame.Rect(x, y, sapa_width, sapa_height))
        start_time = pygame.time.get_ticks()
        elapsed_time = 0

    # --- Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None

                if game_state == "WAITING_START":
                    if event.key == START_KEY:
                        print("Starting Sapa Dodge...")
                        _reset_game()
                        game_state = "PLAYING"

                elif game_state == "SHOWING_RESULT":
                     if not success:
                        if event.key == RETRY_KEY:
                            print("Retrying Sapa Dodge...")
                            game_state = "WAITING_START"
                        elif event.key == CONTINUE_KEY:
                            print("Continuing after failure.")
                            final_outcome = False
                            game_state = "EXITING"

        # --- Game Logic ---
        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0: player.x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] and player.right < SCREEN_WIDTH: player.x += PLAYER_SPEED

            collision_detected = False
            for sapa_rect in sapa_list[:]:
                sapa_rect.y += SAPA_SPEED
                if sapa_rect.colliderect(player):
                    print("Collision detected!")
                    success = False
                    result_message = "Hit by Sapa!"
                    final_outcome = False
                    game_state = "SHOWING_RESULT"
                    collision_detected = True
                    break # Exit fee processing loop on collision
                if sapa_rect.top > SCREEN_HEIGHT:
                    sapa_list.remove(sapa_rect)
                    x = random.randint(0, SCREEN_WIDTH - sapa_width)
                    sapa_list.append(pygame.Rect(x, -sapa_height - random.randint(10, 100), sapa_width, sapa_height))

            # Only check timer if no collision occurred this frame
            if not collision_detected:
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
                if elapsed_time >= SURVIVAL_TIME_SECONDS:
                    print("Survival time reached!")
                    success = True
                    result_message = f"Survived {SURVIVAL_TIME_SECONDS} Seconds!"
                    final_outcome = True
                    game_state = "SHOWING_RESULT"
                    result_timer = 0

        elif game_state == "SHOWING_RESULT" and success:
             result_timer += 1
             if result_timer > RESULT_SUCCESS_DISPLAY_FRAMES:
                  game_state = "EXITING"


        # --- Drawing ---
        screen.blit(background_surface, (0, 0))

        if game_state == "WAITING_START":
            instr_text_line1 = f"Dodge Sapa for {SURVIVAL_TIME_SECONDS} seconds!"
            instr_text_line2 = f"Use LEFT/RIGHT arrow keys to move."
            instr_text_line3 = "Press Enter to Start"
            draw_text_with_shadow(screen, instr_text_line1, instr_font, (CENTER_X, CENTER_Y - 60), WHITE, SHADOW_COLOR)
            draw_text_with_shadow(screen, instr_text_line2, instr_font, (CENTER_X, CENTER_Y - 30), WHITE, SHADOW_COLOR)
            draw_text_with_shadow(screen, instr_text_line3, instr_font, (CENTER_X, CENTER_Y + 30), WHITE, SHADOW_COLOR, center=True)


        elif game_state == "PLAYING" or game_state == "SHOWING_RESULT":
             # Draw Player (Sprite or Fallback)
             if player_sprite:
                 screen.blit(player_sprite, player.topleft)
             else:
                 pygame.draw.rect(screen, FALLBACK_PLAYER_COLOR, player)

             # Draw Sapa (Sprite or Fallback)
             for sapa_rect in sapa_list:
                 if sapa_sprite:
                     screen.blit(sapa_sprite, sapa_rect.topleft)
                 else:
                     pygame.draw.rect(screen, FALLBACK_SAPA_COLOR, sapa_rect)

             # Draw Timer (only during PLAYING)
             if game_state == "PLAYING":
                 time_left = max(0, SURVIVAL_TIME_SECONDS - int(elapsed_time))
                 draw_text_with_shadow(screen, f"Time Left: {time_left}s", timer_font, TIMER_POS, WHITE, SHADOW_COLOR, center=False)

             # Draw Result Message and Options (only in result state)
             if game_state == "SHOWING_RESULT":
                  result_color = COLOR_GREEN if success else COLOR_RED
                  draw_text_with_shadow(screen, result_message, timer_font, (CENTER_X, CENTER_Y + RESULT_Y_OFFSET), result_color, SHADOW_COLOR)
                  if not success:
                       draw_text_with_shadow(screen, "Press R to Retry, Enter to Continue", prompt_font, (CENTER_X, CENTER_Y + RESULT_Y_OFFSET + PROMPT_Y_OFFSET), PROMPT_COLOR, SHADOW_COLOR)

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(FPS)

        # --- Check for Exit State ---
        if game_state == "EXITING":
            running = False

    # --- End of Game Loop ---
    # Phase 2 Comment: For Arcade mode, remove SURVIVAL_TIME_SECONDS check.
    # Instead, let elapsed_time increase indefinitely. Failure occurs only on collision.
    # Track high_score (max elapsed_time survived). Increase SAPA_SPEED and/or INITIAL_SAPA_COUNT
    # based on elapsed_time or score (if score is reintroduced for arcade). Add varied movement?
    print(f"Exiting Sapa Dodge. Final Outcome: {final_outcome}")
    return final_outcome


# --- Example usage ---
if __name__ == '__main__':
    print("Running Sapa Dodge standalone test...")
    pygame.init()
    pygame.font.init()

    # Mock necessary config vars if not available
    try: from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT, UI_BACKGROUND, SAPA_SPRITE, MALE_SPRITE, FEMALE_SPRITE
    except ImportError:
        print("Warning: Using default values for testing.")
        SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600; FPS = 60
        WHITE, BLACK = (240, 240, 242), (8, 8, 6); DEFAULT_FONT = "Arial"; UI_BACKGROUND = ""
        # Provide dummy paths or empty strings for sprites to test fallbacks
        SAPA_SPRITE = ""
        MALE_SPRITE = ""
        FEMALE_SPRITE = ""

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sapa Dodge Test")
    clock = pygame.time.Clock()

    # Add helper function if needed
    # def draw_text_with_shadow(...): ...

    # Test with 'female' gender - requires calling code to pass this
    test_gender = random.choice(['male', 'female'])
    print(f"Testing with gender: {test_gender}")
    game_result = play_sapa_dodge(screen, clock, player_gender=test_gender)
    print(f"Minigame result: {game_result}")

    pygame.quit()
    print("Standalone test finished.")