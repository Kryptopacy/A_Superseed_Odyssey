# src/modules/minigames/complete_the_seed.py
import pygame
import random
import os
# Removed BLACK from import, ensure others are correct
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, DEFAULT_FONT, # Removed BLACK
    UI_BACKGROUND, ROOT_DIR
)

# --- Constants ---
# Colors
SHADOW_COLOR = (50, 50, 50)
GRADIENT_START = (14, 39, 59)
GRADIENT_END = (50, 70, 100)
PROMPT_COLOR = (200, 200, 200)
INPUT_BOX_COLOR = (50, 50, 70)
INPUT_BOX_ACTIVE_COLOR = (80, 80, 110)
INPUT_TEXT_COLOR = WHITE
CORRECT_COLOR = (0, 200, 0)
INCORRECT_COLOR = (200, 0, 0)

# Font
WORD_FONT_SIZE = 28
INDEX_FONT_SIZE = 18
INSTR_FONT_SIZE = 24
PROMPT_FONT_SIZE = 20
DEFAULT_FONT_NAME = DEFAULT_FONT

# Layout
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
WORD_LIST_START_X = 100
WORD_LIST_START_Y = 100 # Base starting Y, adjusted dynamically later
WORD_SPACING_Y = 45
WORD_INDEX_OFFSET_X = -30
INPUT_BOX_WIDTH = 150
INPUT_BOX_HEIGHT = 35
INSTR_Y = 30
RESULT_Y_OFFSET = 0
PROMPT_Y_OFFSET = 40
SHADOW_OFFSET = (2, 2) # <<< DEFINED HERE <<<

# Gameplay
SEQUENCE_LENGTH = 6
NUM_WORDS_TO_HIDE = 2
VIEW_TIME_SECONDS = 5
CHALLENGE_PAUSE_SECONDS = 1.5

# Timing
RESULT_SUCCESS_DISPLAY_SECONDS = 1.5
RESULT_SUCCESS_DISPLAY_FRAMES = int(FPS * RESULT_SUCCESS_DISPLAY_SECONDS)

# Word list file
WORD_LIST_FILENAME = "seed_words.txt"
if 'ROOT_DIR' in globals(): WORD_LIST_PATH = os.path.join(ROOT_DIR, "data", WORD_LIST_FILENAME)
else: WORD_LIST_PATH = os.path.join("data", WORD_LIST_FILENAME)


# Keys
START_KEY = pygame.K_RETURN
NEXT_INPUT_KEY = pygame.K_RETURN
ALT_NEXT_INPUT_KEY = pygame.K_TAB
CONFIRM_KEY = pygame.K_RETURN
RETRY_KEY = pygame.K_r


# --- Helper Functions --- <<< DEFINED *AFTER* CONSTANTS

def draw_text_with_shadow(screen, text, font, position, color, shadow_color, shadow_offset=SHADOW_OFFSET, center=True, topright=False):
    """Renders text with shadow. Uses SHADOW_OFFSET constant as default."""
    # This function should now correctly find SHADOW_OFFSET as its default
    text_surface = font.render(text, True, color)
    shadow_surface = font.render(text, True, shadow_color)
    if topright: text_rect = text_surface.get_rect(topright=position); shadow_rect = shadow_surface.get_rect(topright=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    elif center: text_rect = text_surface.get_rect(center=position); shadow_rect = shadow_surface.get_rect(center=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    else: text_rect = text_surface.get_rect(topleft=position); shadow_rect = shadow_surface.get_rect(topleft=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]))
    screen.blit(shadow_surface, shadow_rect); screen.blit(text_surface, text_rect)

def load_words(filename):
    """Loads words from a file, one word per line."""
    default_words = ["abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse", "access", "accident"] # Fallback List
    if not os.path.exists(filename):
        print(f"Warning: Word file '{filename}' not found. Using default words.")
        return default_words
    try:
        with open(filename, 'r') as f:
            words = [line.strip().lower() for line in f if line.strip()]
        if not words:
            print(f"Warning: Word file '{filename}' is empty. Using default words.")
            return default_words
        print(f"Loaded {len(words)} words from {filename}")
        return words
    except Exception as e:
        print(f"Error loading word file '{filename}': {e}. Using default words.")
        return default_words

# --- Main Minigame Function --- <<< DEFINED *AFTER* HELPERS

def play_complete_the_seed(screen, clock):
    """
    Runs the Complete the Seed minigame.
    Returns: True (success), False (failure), None (cancelled).
    """
    print("Entering Complete the Seed minigame...")

    # --- Initialization ---
    try:
        word_font = pygame.font.SysFont(DEFAULT_FONT_NAME, WORD_FONT_SIZE)
        index_font = pygame.font.SysFont(DEFAULT_FONT_NAME, INDEX_FONT_SIZE)
        instr_font = pygame.font.SysFont(DEFAULT_FONT_NAME, INSTR_FONT_SIZE)
        prompt_font = pygame.font.SysFont(DEFAULT_FONT_NAME, PROMPT_FONT_SIZE)
    except Exception as e:
        print(f"Failed to load system font '{DEFAULT_FONT_NAME}': {e}. Using default.")
        word_font = pygame.font.Font(None, WORD_FONT_SIZE)
        index_font = pygame.font.Font(None, INDEX_FONT_SIZE)
        instr_font = pygame.font.Font(None, INSTR_FONT_SIZE)
        prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)


    # --- Load Background ---
    background_surface = None
    try: # Asset loading block
        # Check if variable exists and has a non-empty value before checking path
        if 'UI_BACKGROUND' in globals() and UI_BACKGROUND and os.path.exists(UI_BACKGROUND):
            background_surface = pygame.image.load(UI_BACKGROUND).convert()
            background_surface = pygame.transform.scale(background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Loaded UI_BACKGROUND asset.")
        else: print("UI_BACKGROUND path not found, empty, or doesn't exist.")
    except pygame.error as e: print(f"Failed to load UI_BACKGROUND (Pygame Error): {e}")
    except Exception as e: print(f"Failed to load UI_BACKGROUND (Other Error): {e}")

    if background_surface is None: # Fallback background
        print("Using fallback gradient background."); background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT; r = GRADIENT_START[0] + t * (GRADIENT_END[0] - GRADIENT_START[0])
            g = GRADIENT_START[1] + t * (GRADIENT_END[1] - GRADIENT_START[1]); b = GRADIENT_START[2] + t * (GRADIENT_END[2] - GRADIENT_START[2])
            background_surface.fill((int(r), int(g), int(b)), (0, y, SCREEN_WIDTH, 1))

    # --- Load Word List ---
    word_list = load_words(WORD_LIST_PATH)
    if not word_list or len(word_list) < SEQUENCE_LENGTH:
        print(f"Error: Not enough words in word list ({len(word_list)}) for sequence length {SEQUENCE_LENGTH}. Exiting.")
        # TODO: Display an error message on screen?
        return False # Treat as failure

    # --- Game State Variables ---
    full_sequence = []
    display_sequence = []
    hidden_indices = []
    player_inputs = {}
    current_input_index = -1
    current_input_string = ""
    success = False
    result_message = ""
    state_timer = 0.0

    game_state = "WAITING_START"
    final_outcome = None

    def _reset_game():
        nonlocal full_sequence, display_sequence, hidden_indices, player_inputs
        nonlocal current_input_index, current_input_string, state_timer
        # Ensure sample size k is not larger than population size
        k = min(SEQUENCE_LENGTH, len(word_list))
        full_sequence = random.sample(word_list, k)
        actual_sequence_length = len(full_sequence)
        actual_num_to_hide = min(NUM_WORDS_TO_HIDE, actual_sequence_length)
        display_sequence = list(full_sequence)
        hidden_indices = sorted(random.sample(range(actual_sequence_length), actual_num_to_hide)) if actual_num_to_hide > 0 else []
        for idx in hidden_indices: display_sequence[idx] = None
        player_inputs = {idx: "" for idx in hidden_indices}
        current_input_index = hidden_indices[0] if hidden_indices else -1
        current_input_string = ""
        state_timer = 0.0
        print(f"New sequence generated ({actual_sequence_length} words). Hidden indices: {hidden_indices}")

    # --- Game Loop ---
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None

                if game_state == "WAITING_START":
                    if event.key == START_KEY:
                        print("Starting Complete the Seed..."); _reset_game()
                        if not full_sequence: print("Error during game reset."); return False
                        game_state = "SHOWING_PHRASE"; state_timer = 0.0
                elif game_state == "WAITING_INPUT":
                    if current_input_index != -1:
                        if event.key == pygame.K_BACKSPACE: current_input_string = current_input_string[:-1]
                        elif event.key == NEXT_INPUT_KEY or event.key == ALT_NEXT_INPUT_KEY:
                            player_inputs[current_input_index] = current_input_string.lower().strip()
                            try:
                                current_hidden_idx_pos = hidden_indices.index(current_input_index)
                                if current_hidden_idx_pos + 1 < len(hidden_indices):
                                    current_input_index = hidden_indices[current_hidden_idx_pos + 1]
                                    current_input_string = player_inputs.get(current_input_index, "") # Use get for safety
                                else: game_state = "CHECKING_ANSWER"
                            except ValueError: # Should not happen if logic is correct
                                print(f"Error: current_input_index {current_input_index} not in hidden_indices {hidden_indices}")
                                game_state = "CHECKING_ANSWER" # Proceed to check anyway
                        elif event.unicode.isalpha(): current_input_string += event.unicode
                elif game_state == "SHOWING_RESULT":
                     if not success:
                        if event.key == RETRY_KEY: print("Retrying..."); game_state = "WAITING_START"
                        elif event.key == CONFIRM_KEY: print("Continuing after failure."); final_outcome = False; game_state = "EXITING"

        # --- State Machine Logic ---
        state_timer += dt
        if game_state == "SHOWING_PHRASE":
            if state_timer >= VIEW_TIME_SECONDS: game_state = "SHOWING_CHALLENGE"; state_timer = 0.0; current_input_index = hidden_indices[0] if hidden_indices else -1
        elif game_state == "SHOWING_CHALLENGE":
             if state_timer >= CHALLENGE_PAUSE_SECONDS: game_state = "CHECKING_ANSWER" if not hidden_indices else "WAITING_INPUT"; state_timer = 0.0
        elif game_state == "CHECKING_ANSWER":
             correct_count = 0
             if not hidden_indices: success = True
             else:
                 for idx in hidden_indices:
                     if player_inputs.get(idx, "").lower().strip() == full_sequence[idx]: correct_count += 1
                 success = (correct_count == len(hidden_indices))
             final_outcome = success; result_message = "Seed Phrase Correct!" if success else "Incorrect Seed Phrase!"
             print(f"Checking complete. Correct: {correct_count}/{len(hidden_indices)}. Success: {success}")
             game_state = "SHOWING_RESULT"; state_timer = 0.0
        elif game_state == "SHOWING_RESULT" and success:
             if state_timer >= RESULT_SUCCESS_DISPLAY_SECONDS: game_state = "EXITING"

        # --- Drawing ---
        screen.blit(background_surface, (0, 0))
        # (Drawing logic remains largely the same as previous correct version)
        if game_state == "WAITING_START":
             instr_text_line1 = f"Memorize the {len(full_sequence) if full_sequence else SEQUENCE_LENGTH}-word seed phrase." # Show actual length if list was short
             instr_text_line2 = f"{len(hidden_indices) if hidden_indices else NUM_WORDS_TO_HIDE} words will disappear. Fill them correctly." # Show actual hidden count
             instr_text_line3 = "Press Enter to Start"
             draw_text_with_shadow(screen, instr_text_line1, instr_font, (CENTER_X, CENTER_Y - 60), WHITE, SHADOW_COLOR)
             draw_text_with_shadow(screen, instr_text_line2, instr_font, (CENTER_X, CENTER_Y - 30), WHITE, SHADOW_COLOR)
             draw_text_with_shadow(screen, instr_text_line3, instr_font, (CENTER_X, CENTER_Y + 30), WHITE, SHADOW_COLOR, center=True)
        elif game_state != "EXITING":
             instr_text = "Complete the Seed Phrase!"
             draw_text_with_shadow(screen, instr_text, instr_font, (CENTER_X, INSTR_Y), WHITE, SHADOW_COLOR)

        if game_state in ["SHOWING_PHRASE", "SHOWING_CHALLENGE", "WAITING_INPUT", "SHOWING_RESULT"]:
            sequence_to_draw = full_sequence if game_state == "SHOWING_PHRASE" else display_sequence
            list_height = len(full_sequence) * WORD_SPACING_Y
            dynamic_start_y = max(INSTR_Y + 40, CENTER_Y - list_height // 2)
            for i, word in enumerate(sequence_to_draw):
                word_y = dynamic_start_y + i * WORD_SPACING_Y
                index_text = f"{i+1}."
                draw_text_with_shadow(screen, index_text, index_font, (WORD_LIST_START_X + WORD_INDEX_OFFSET_X, word_y + 5), WHITE, SHADOW_COLOR, center=False)
                if word is not None:
                    display_word = full_sequence[i] if game_state == "SHOWING_RESULT" else word
                    word_color = WHITE
                    if game_state == "SHOWING_RESULT" and i in hidden_indices: word_color = CORRECT_COLOR if player_inputs.get(i,"").lower().strip() == full_sequence[i] else INCORRECT_COLOR
                    draw_text_with_shadow(screen, display_word, word_font, (WORD_LIST_START_X, word_y + (INPUT_BOX_HEIGHT - word_font.get_height()) // 2), word_color, SHADOW_COLOR, center=False)
                else:
                    box_rect = pygame.Rect(WORD_LIST_START_X, word_y, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
                    box_color = INPUT_BOX_ACTIVE_COLOR if i == current_input_index and game_state == "WAITING_INPUT" else INPUT_BOX_COLOR
                    pygame.draw.rect(screen, box_color, box_rect, border_radius=3); pygame.draw.rect(screen, WHITE, box_rect, width=1, border_radius=3)
                    input_text = ""; text_color = INPUT_TEXT_COLOR
                    if game_state == "WAITING_INPUT" and i == current_input_index: input_text = current_input_string; input_text += "|" if int(pygame.time.get_ticks() / 500) % 2 == 0 else ""
                    elif game_state in ["WAITING_INPUT", "SHOWING_RESULT"]: input_text = player_inputs.get(i, ""); text_color = CORRECT_COLOR if game_state == "SHOWING_RESULT" and player_inputs.get(i,"").lower().strip() == full_sequence[i] else INCORRECT_COLOR if game_state == "SHOWING_RESULT" else INPUT_TEXT_COLOR
                    if input_text:
                         text_surf = word_font.render(input_text, True, text_color); text_rect = text_surf.get_rect(centery=box_rect.centery); text_rect.left = box_rect.left + 5
                         shadow_surf = word_font.render(input_text, True, SHADOW_COLOR); shadow_rect = shadow_surf.get_rect(centery=box_rect.centery + SHADOW_OFFSET[1]); shadow_rect.left = box_rect.left + 5 + SHADOW_OFFSET[0] # Use constant here
                         screen.blit(shadow_surf, shadow_rect); screen.blit(text_surf, text_rect)

        if game_state == "SHOWING_CHALLENGE": draw_text_with_shadow(screen, "Fill in the blanks!", instr_font, (CENTER_X, SCREEN_HEIGHT - 50), WHITE, SHADOW_COLOR)
        elif game_state == "WAITING_INPUT": draw_text_with_shadow(screen, "Type the word, press Enter/Tab for next", prompt_font, (CENTER_X, SCREEN_HEIGHT - 50), PROMPT_COLOR, SHADOW_COLOR)
        elif game_state == "SHOWING_RESULT":
             result_color = CORRECT_COLOR if success else INCORRECT_COLOR
             draw_text_with_shadow(screen, result_message, instr_font, (CENTER_X, SCREEN_HEIGHT - 80), result_color, SHADOW_COLOR)
             if not success: draw_text_with_shadow(screen, "Press R to Retry, Enter to Continue", prompt_font, (CENTER_X, SCREEN_HEIGHT - 50), PROMPT_COLOR, SHADOW_COLOR)

        pygame.display.flip()
        if game_state == "EXITING": running = False

    print(f"Exiting Complete the Seed. Final Outcome: {final_outcome}")
    return final_outcome

# --- Example usage ---
# (Standalone test code remains the same)
if __name__ == '__main__':
    print("Running Complete the Seed standalone test...")
    pygame.init(); pygame.font.init()
    try: from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT, UI_BACKGROUND, ROOT_DIR
    except ImportError:
        print("Warning: Using default values for testing."); SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600; FPS = 60
        WHITE, BLACK = (240, 240, 242), (8, 8, 6); DEFAULT_FONT = "Arial"; UI_BACKGROUND = ""
        if 'ROOT_DIR' not in locals(): ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if 'ROOT_DIR' in locals() and not os.path.exists(os.path.join(ROOT_DIR, "data")): WORD_LIST_PATH = os.path.join("data", WORD_LIST_FILENAME)
    else: WORD_LIST_PATH = os.path.join(ROOT_DIR, "data", WORD_LIST_FILENAME)
    data_dir = os.path.dirname(WORD_LIST_PATH)
    if not os.path.exists(data_dir):
        try: os.makedirs(data_dir)
        except OSError as e: print(f"Could not create data directory: {e}")
    if not os.path.exists(WORD_LIST_PATH):
        print(f"Creating dummy word file: {WORD_LIST_PATH}")
        try:
            default_words_text = "\n".join(["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine"])
            with open(WORD_LIST_PATH, "w") as f: f.write(default_words_text + "\n")
        except IOError as e: print(f"Could not write dummy word file: {e}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)); pygame.display.set_caption("Complete the Seed Test"); clock = pygame.time.Clock()
    game_result = play_complete_the_seed(screen, clock); print(f"Minigame result: {game_result}"); pygame.quit(); print("Standalone test finished.")