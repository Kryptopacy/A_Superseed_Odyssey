# src/modules/minigames/color_match.py
import pygame
import random
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT, UI_BACKGROUND

# --- Constants ---
# Colors (Using config WHITE/BLACK)
SHADOW_COLOR = (50, 50, 50)
GRADIENT_START = (14, 39, 59)
GRADIENT_END = (50, 70, 100)
PROMPT_COLOR = (200, 200, 200)
# Game specific colors
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_LIST = [COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]
COLOR_NAMES = ["Red", "Green", "Blue", "Yellow"] # Must match COLOR_LIST order

# Font
MAIN_FONT_SIZE = 48
SCORE_FONT_SIZE = 36
INSTR_FONT_SIZE = 24
PROMPT_FONT_SIZE = 20
DEFAULT_FONT_NAME = DEFAULT_FONT

# Layout
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
INSTR_Y = 30
SCORE_POS = (20, 20)
TIMER_POS_X = SCREEN_WIDTH - 20 # Anchor timer to the right
TIMER_POS_Y = 20
RECT_SIZE = (150, 150)
RECT_POS = (CENTER_X - RECT_SIZE[0] // 2, CENTER_Y - RECT_SIZE[1] // 2 - 30) # Position rect slightly above center
NAME_Y_OFFSET = RECT_SIZE[1] // 2 + 30 # Offset name below the rect center
RESULT_Y_OFFSET = 60 # Offset below center for result message
PROMPT_Y_OFFSET = 40 # Offset below result for prompts
SHADOW_OFFSET = (2, 2)

# Timing / Gameplay
TIME_LIMIT_SECONDS = 15
TARGET_SCORE = 5
# Display time for SUCCESS message only (if needed, or just exit)
RESULT_SUCCESS_DISPLAY_SECONDS = 1.5
RESULT_SUCCESS_DISPLAY_FRAMES = int(FPS * RESULT_SUCCESS_DISPLAY_SECONDS)

# Keys
START_KEY = pygame.K_RETURN
YES_KEY = pygame.K_y
NO_KEY = pygame.K_n
RETRY_KEY = pygame.K_r
# Using Enter to continue after failure
CONTINUE_KEY = pygame.K_RETURN


# --- Helper Function ---
# Assume draw_text_with_shadow is available
def draw_text_with_shadow(screen, text, font, position, color, shadow_color, shadow_offset=SHADOW_OFFSET, center=True, topright=False):
    """Renders text with shadow. Can align center (default) or topright."""
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

def play_color_match(screen, clock):
    """
    Runs the Color Match minigame with manual start, timer, score goal, and retry.
    Returns: True (success), False (failure), None (cancelled).
    """
    print("Entering Color Match minigame...")

    # --- Initialization ---
    try:
        main_font = pygame.font.SysFont(DEFAULT_FONT_NAME, MAIN_FONT_SIZE)
        score_font = pygame.font.SysFont(DEFAULT_FONT_NAME, SCORE_FONT_SIZE)
        instr_font = pygame.font.SysFont(DEFAULT_FONT_NAME, INSTR_FONT_SIZE)
        prompt_font = pygame.font.SysFont(DEFAULT_FONT_NAME, PROMPT_FONT_SIZE)
    except Exception as e:
        print(f"Failed to load system font '{DEFAULT_FONT_NAME}': {e}. Using default.")
        main_font = pygame.font.Font(None, MAIN_FONT_SIZE)
        score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        instr_font = pygame.font.Font(None, INSTR_FONT_SIZE)
        prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)

    # --- Load Background ---
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

    # --- Game State Variables ---
    score = 0
    start_time = 0 # Ticks when PLAYING state begins
    elapsed_time = 0
    current_color = None
    current_name = None
    is_match = False # Does the current name match the current color?
    success = False # Did player meet the goal?
    result_message = ""
    result_timer = 0 # Frame counter for success message display

    # Game states: WAITING_START, PLAYING, SHOWING_RESULT, EXITING
    game_state = "WAITING_START"
    final_outcome = None # Stores True/False when decided

    def _setup_new_pair():
        """Chooses a new color/name pair and determines if it's a match."""
        nonlocal current_color, current_name, is_match
        # Ensure color and name lists have same length
        if len(COLOR_LIST) != len(COLOR_NAMES):
             print("Error: COLOR_LIST and COLOR_NAMES must have the same number of items!")
             # Handle error appropriately - maybe return False from main function
             return False # Indicate setup failure

        color_index = random.randrange(len(COLOR_LIST))
        name_index = random.randrange(len(COLOR_NAMES))

        current_color = COLOR_LIST[color_index]
        current_name = COLOR_NAMES[name_index]
        is_match = (color_index == name_index)
        # print(f"New pair: Color={COLOR_NAMES[color_index]}, Name={current_name}, Match={is_match}") # Debug
        return True # Indicate setup success

    # --- Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None # Cancel
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None # Cancel

                if game_state == "WAITING_START":
                    if event.key == START_KEY:
                        print("Starting Color Match...")
                        score = 0 # Reset score
                        if not _setup_new_pair(): # Setup first pair
                             # Handle setup error (e.g., mismatched lists)
                             return False # Or None? False indicates failure within the game logic.
                        start_time = pygame.time.get_ticks()
                        game_state = "PLAYING"

                elif game_state == "PLAYING":
                    player_said_match = None
                    if event.key == YES_KEY:
                        player_said_match = True
                    elif event.key == NO_KEY:
                        player_said_match = False

                    if player_said_match is not None:
                        if player_said_match == is_match:
                            # Correct Answer
                            score += 1
                            print(f"Correct! Score: {score}")
                            # Check for win condition
                            if score >= TARGET_SCORE:
                                success = True
                                result_message = f"Success! Reached {TARGET_SCORE} points!"
                                final_outcome = True
                                game_state = "SHOWING_RESULT"
                                result_timer = 0
                            else:
                                # Setup next pair if game not won yet
                                if not _setup_new_pair(): return False # Handle setup error
                        else:
                            # Incorrect Answer
                            print("Incorrect match!")
                            success = False
                            result_message = "Incorrect Match!"
                            final_outcome = False # Failure due to wrong answer
                            game_state = "SHOWING_RESULT"

                elif game_state == "SHOWING_RESULT":
                     if not success: # Options only available on failure
                        if event.key == RETRY_KEY:
                            print("Retrying Color Match...")
                            # Resetting requires going back to start
                            game_state = "WAITING_START"
                            # State variables (score, time, pair) reset automatically on transition
                        elif event.key == CONTINUE_KEY:
                            print("Continuing after failure.")
                            # final_outcome already set to False
                            game_state = "EXITING"

        # --- State Machine Logic ---
        if game_state == "PLAYING":
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
            if elapsed_time >= TIME_LIMIT_SECONDS:
                print("Time's up!")
                if score >= TARGET_SCORE:
                     success = True
                     result_message = f"Time's Up! Final Score: {score} - Success!"
                     final_outcome = True
                else:
                     success = False
                     result_message = f"Time's Up! Final Score: {score} - Failed!"
                     final_outcome = False # Failure due to time out
                game_state = "SHOWING_RESULT"
                result_timer = 0

        elif game_state == "SHOWING_RESULT" and success:
             # Automatically exit after showing success message
             result_timer += 1
             if result_timer > RESULT_SUCCESS_DISPLAY_FRAMES:
                  game_state = "EXITING"


        # --- Drawing ---
        screen.blit(background_surface, (0, 0))

        if game_state == "WAITING_START":
            instr_text_line1 = f"Does the color name match the square's color?"
            instr_text_line2 = f"Press Y for Yes, N for No. Reach {TARGET_SCORE} points in {TIME_LIMIT_SECONDS} seconds."
            instr_text_line3 = "Press Enter to Start"
            draw_text_with_shadow(screen, instr_text_line1, instr_font, (CENTER_X, CENTER_Y - 60), WHITE, SHADOW_COLOR)
            draw_text_with_shadow(screen, instr_text_line2, instr_font, (CENTER_X, CENTER_Y - 30), WHITE, SHADOW_COLOR)
            draw_text_with_shadow(screen, instr_text_line3, main_font, (CENTER_X, CENTER_Y + 30), WHITE, SHADOW_COLOR)

        elif game_state == "PLAYING" or game_state == "SHOWING_RESULT":
             # Draw Score
             draw_text_with_shadow(screen, f"Score: {score}", score_font, SCORE_POS, WHITE, SHADOW_COLOR, center=False)
             # Draw Timer
             time_left = max(0, TIME_LIMIT_SECONDS - int(elapsed_time))
             draw_text_with_shadow(screen, f"Time: {time_left}s", score_font, (TIMER_POS_X, TIMER_POS_Y), WHITE, SHADOW_COLOR, topright=True)

             # Draw Color Rectangle and Name (only if valid)
             if current_color and current_name:
                 pygame.draw.rect(screen, current_color, RECT_POS + RECT_SIZE)
                 draw_text_with_shadow(screen, current_name, main_font, (CENTER_X, RECT_POS[1] + NAME_Y_OFFSET), WHITE, SHADOW_COLOR)

             # Draw Result Message and Options (only in result state)
             if game_state == "SHOWING_RESULT":
                  result_color = (0, 200, 0) if success else (200, 0, 0) # Use tuple colors
                  draw_text_with_shadow(screen, result_message, score_font, (CENTER_X, CENTER_Y + RESULT_Y_OFFSET), result_color, SHADOW_COLOR)
                  if not success:
                       draw_text_with_shadow(screen, "Press R to Retry, Enter to Continue", prompt_font, (CENTER_X, CENTER_Y + RESULT_Y_OFFSET + PROMPT_Y_OFFSET), PROMPT_COLOR, SHADOW_COLOR)

        # --- Update Display ---
        pygame.display.flip()
        clock.tick(FPS)

        # --- Check for Exit State ---
        if game_state == "EXITING":
            running = False


    # --- End of Game Loop ---
    print(f"Exiting Color Match. Final Outcome: {final_outcome}")
    return final_outcome


# --- Example usage ---
if __name__ == '__main__':
    print("Running Color Match standalone test...")
    pygame.init()
    pygame.font.init()

    try: from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT, UI_BACKGROUND
    except ImportError:
        print("Warning: Using default values for testing.")
        SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600; FPS = 60
        WHITE, BLACK = (240, 240, 242), (8, 8, 6); DEFAULT_FONT = "Arial"; UI_BACKGROUND = ""

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Color Match Test")
    clock = pygame.time.Clock()

    # Add helper function if needed
    # def draw_text_with_shadow(...): ...

    game_result = play_color_match(screen, clock)
    print(f"Minigame result: {game_result}")

    pygame.quit()
    print("Standalone test finished.")