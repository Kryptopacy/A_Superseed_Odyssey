# src/modules/minigames/memory_sequence.py
import pygame
import random
import time # For sleep
import os # If needed for helpers
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT

# --- Constants ---
# Colors
SHADOW_COLOR = (50, 50, 50)
GRADIENT_START = (14, 39, 59)
GRADIENT_END = (50, 70, 100)
COLOR_RED = (200, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_BLUE = (0, 0, 200)
COLOR_YELLOW = (200, 200, 0)
PROMPT_COLOR = (200, 200, 200) # Color for prompts like "Press Enter"

# Font
FONT_SIZE = 48
INSTRUCTION_FONT_SIZE = 24
PROMPT_FONT_SIZE = 20 # Smaller font for prompts
DEFAULT_FONT_NAME = DEFAULT_FONT

# Layout
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
INSTR_Y = 50
INPUT_DISPLAY_Y = CENTER_Y
SEQUENCE_DISPLAY_Y = CENTER_Y
PROMPT_Y_OFFSET = 40 # Offset below input/result for prompts
RESULT_Y_OFFSET = 60 # Offset below center for result message
SHADOW_OFFSET = (2, 2)

# Timing / Gameplay
SEQUENCE_LENGTH = 4 # Base length
NUMBER_MIN = 0
NUMBER_MAX = 9
DISPLAY_TIME_SECONDS = 0.8
PAUSE_TIME_SECONDS = 0.2
PRE_INPUT_PAUSE_SECONDS = 1.0
RESULT_DISPLAY_SECONDS = 2.0
RESULT_DISPLAY_FRAMES = int(FPS * RESULT_DISPLAY_SECONDS)

# Key mapping
ALLOWED_KEYS = {
    pygame.K_0: 0, pygame.K_KP0: 0,
    pygame.K_1: 1, pygame.K_KP1: 1,
    pygame.K_2: 2, pygame.K_KP2: 2,
    pygame.K_3: 3, pygame.K_KP3: 3,
    pygame.K_4: 4, pygame.K_KP4: 4,
    pygame.K_5: 5, pygame.K_KP5: 5,
    pygame.K_6: 6, pygame.K_KP6: 6,
    pygame.K_7: 7, pygame.K_KP7: 7,
    pygame.K_8: 8, pygame.K_KP8: 8,
    pygame.K_9: 9, pygame.K_KP9: 0,
}
START_KEY = pygame.K_RETURN # Or pygame.K_SPACE
SUBMIT_KEY = pygame.K_RETURN

# --- Helper Function (reuse or define here) ---
def draw_text_with_shadow(screen, text, font, position, color, shadow_color, shadow_offset=SHADOW_OFFSET, center=True):
    """Renders and draws text with a simple shadow."""
    text_surface = font.render(text, True, color)
    shadow_surface = font.render(text, True, shadow_color)
    if center:
        text_rect = text_surface.get_rect(center=position)
        shadow_rect = shadow_surface.get_rect(center=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    else:
        text_rect = text_surface.get_rect(topleft=position)
        shadow_rect = shadow_surface.get_rect(topleft=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    screen.blit(shadow_surface, shadow_rect)
    screen.blit(text_surface, text_rect)


# --- Main Minigame Function ---
def play_memory_sequence(screen, clock, sequence_length=SEQUENCE_LENGTH):
    """
    Runs a single round of the Memory Sequence minigame with manual start and submit confirmation.
    Returns: True (success), False (failure), None (cancelled).
    """
    print(f"Entering Memory Sequence minigame (Length: {sequence_length})...")

    # --- Initialization ---
    try:
        main_font = pygame.font.SysFont(DEFAULT_FONT_NAME, FONT_SIZE)
        instr_font = pygame.font.SysFont(DEFAULT_FONT_NAME, INSTRUCTION_FONT_SIZE)
        prompt_font = pygame.font.SysFont(DEFAULT_FONT_NAME, PROMPT_FONT_SIZE)
    except Exception as e:
        print(f"Failed to load system font '{DEFAULT_FONT_NAME}': {e}. Using default.")
        main_font = pygame.font.Font(None, FONT_SIZE)
        instr_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)
        prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)

    sequence = [random.randint(NUMBER_MIN, NUMBER_MAX) for _ in range(sequence_length)]
    player_input = []
    player_input_complete = False # Flag: Has player entered enough digits?
    success = False
    submitted = False # Flag: Has player pressed Submit Key?
    result_message = ""
    result_timer = 0

    # Game states: WAITING_START, SHOWING_SEQUENCE, SHOWING_PAUSE, PRE_INPUT_PAUSE, WAITING_INPUT, SHOWING_RESULT, EXITING
    game_state = "WAITING_START"
    current_display_index = 0
    state_timer = 0.0 # Use float seconds for timing state changes

    # --- Pre-render Background ---
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        r = GRADIENT_START[0] + t * (GRADIENT_END[0] - GRADIENT_START[0])
        g = GRADIENT_START[1] + t * (GRADIENT_END[1] - GRADIENT_START[1])
        b = GRADIENT_START[2] + t * (GRADIENT_END[2] - GRADIENT_START[2])
        pygame.draw.line(background, (int(r), int(g), int(b)), (0, y), (SCREEN_WIDTH, y))

    # --- Game Loop ---
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event received.")
                return None # Cancel

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Escape key pressed.")
                    return None # Cancel

                # --- Start Game ---
                if game_state == "WAITING_START":
                    if event.key == START_KEY:
                        print("Starting sequence display...")
                        game_state = "SHOWING_SEQUENCE"
                        state_timer = 0
                        current_display_index = 0

                # --- Handle Player Input ---
                elif game_state == "WAITING_INPUT":
                    # Handle number input (only if not complete)
                    if not player_input_complete and event.key in ALLOWED_KEYS:
                        pressed_num = ALLOWED_KEYS[event.key]
                        player_input.append(pressed_num)
                        # Check if input length now matches sequence length
                        if len(player_input) == len(sequence):
                            player_input_complete = True

                    # Handle submission (only if complete)
                    elif player_input_complete and event.key == SUBMIT_KEY:
                        success = player_input == sequence
                        submitted = True
                        result_message = "Success! Sequence matched!" if success else "Failed! Wrong sequence."
                        game_state = "SHOWING_RESULT"
                        state_timer = 0 # Reset timer for result display


        # --- State Machine Logic ---
        state_timer += dt

        # Note: WAITING_START state change is now handled purely by key press event

        if game_state == "SHOWING_SEQUENCE":
            if state_timer >= DISPLAY_TIME_SECONDS:
                game_state = "SHOWING_PAUSE"
                state_timer = 0

        elif game_state == "SHOWING_PAUSE":
             if state_timer >= PAUSE_TIME_SECONDS:
                current_display_index += 1
                if current_display_index >= len(sequence):
                     game_state = "PRE_INPUT_PAUSE"
                     state_timer = 0
                else:
                    game_state = "SHOWING_SEQUENCE"
                    state_timer = 0

        elif game_state == "PRE_INPUT_PAUSE":
             if state_timer >= PRE_INPUT_PAUSE_SECONDS:
                 game_state = "WAITING_INPUT"
                 state_timer = 0

        elif game_state == "SHOWING_RESULT":
            result_timer += 1 # Use frame count
            if result_timer > RESULT_DISPLAY_FRAMES:
                 game_state = "EXITING"


        # --- Drawing ---
        screen.blit(background, (0, 0))

        # Persistent Instructions
        instr_pos = (CENTER_X, INSTR_Y)
        instr_text = "Memorize the sequence! Repeat using keys 0-9."
        draw_text_with_shadow(screen, instr_text, instr_font, instr_pos, WHITE, SHADOW_COLOR)

        # State-specific drawing
        if game_state == "WAITING_START":
             start_prompt_pos = (CENTER_X, CENTER_Y)
             draw_text_with_shadow(screen, "Press Enter to Start", main_font, start_prompt_pos, WHITE, SHADOW_COLOR)

        elif game_state == "SHOWING_SEQUENCE":
            num_to_show = str(sequence[current_display_index])
            draw_text_with_shadow(screen, num_to_show, main_font, (CENTER_X, SEQUENCE_DISPLAY_Y), WHITE, SHADOW_COLOR)

        elif game_state == "PRE_INPUT_PAUSE":
             draw_text_with_shadow(screen, "Your Turn!", main_font, (CENTER_X, CENTER_Y), WHITE, SHADOW_COLOR)

        elif game_state == "WAITING_INPUT":
            input_str = " ".join(map(str, player_input)) if player_input else "_ " * sequence_length # Show placeholders maybe?
            draw_text_with_shadow(screen, f"{input_str}", main_font, (CENTER_X, INPUT_DISPLAY_Y), WHITE, SHADOW_COLOR)
            # Show submit prompt only when input is complete
            if player_input_complete:
                 submit_prompt_pos = (CENTER_X, INPUT_DISPLAY_Y + PROMPT_Y_OFFSET)
                 draw_text_with_shadow(screen, "Press Enter to Submit", prompt_font, submit_prompt_pos, PROMPT_COLOR, SHADOW_COLOR)

        elif game_state == "SHOWING_RESULT":
            input_str = " ".join(map(str, player_input))
            draw_text_with_shadow(screen, f"{input_str}", main_font, (CENTER_X, INPUT_DISPLAY_Y), WHITE, SHADOW_COLOR)
            result_color = COLOR_GREEN if success else COLOR_RED
            draw_text_with_shadow(screen, result_message, main_font, (CENTER_X, INPUT_DISPLAY_Y + RESULT_Y_OFFSET), result_color, SHADOW_COLOR)

        # --- Update Display ---
        pygame.display.flip()

        # --- Check for Exit State ---
        if game_state == "EXITING":
            running = False


    # --- End of Game Loop ---
    if submitted:
        print(f"Exiting Memory Sequence. Success: {success}")
        return success
    else:
        # This case means the player quit (Esc/Quit) before submitting.
        # The direct return None in event handling covers this.
        # If somehow the loop exits otherwise without submission, treat as failure/cancel.
        print("Exiting Memory Sequence without submission (likely cancelled).")
        # We return None for explicit cancels, so returning False here might be better
        # if the loop termination was truly abnormal. But None seems safer if unsure.
        return None # Align with Esc/Quit behaviour


# --- Example usage (for testing standalone) ---
if __name__ == '__main__':
    print("Running Memory Sequence standalone test...")
    pygame.init()
    # Make sure fonts are available or handle errors
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Memory Sequence Test")
    clock = pygame.time.Clock()

    # Add the helper function here if not imported
    # def draw_text_with_shadow(...): ...

    game_result = play_memory_sequence(screen, clock, sequence_length=4)
    print(f"Minigame result: {game_result}")

    pygame.quit()
    print("Standalone test finished.")