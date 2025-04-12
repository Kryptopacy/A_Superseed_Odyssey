# src/modules/minigames/anagram.py
import pygame
import random
import os
# Ensure all necessary imports are present, remove unused (like BLACK)
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, DEFAULT_FONT,
    UI_BACKGROUND, ROOT_DIR, SOUND_CUTSCENE_MUSIC
)

# --- Constants ---

# Colors
SHADOW_COLOR = (50, 50, 50)
GRADIENT_START = (14, 39, 59)
GRADIENT_END = (50, 70, 100)
PROMPT_COLOR = (200, 200, 200)
HINT_COLOR = (180, 180, 220)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)

# Font
FONT_SIZE = 36
INSTR_FONT_SIZE = 24
PROMPT_FONT_SIZE = 20
HINT_FONT_SIZE = 28
DEFAULT_FONT_NAME = DEFAULT_FONT

# Layout
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
INSTR_Y = 40
SCRAMBLED_Y = 120
HINT_Y = 180
INPUT_Y = 250
RESULT_Y = CENTER_Y + 100
PROMPT_Y_OFFSET = 40
SHADOW_OFFSET = (2, 2)

# Timing
RESULT_SUCCESS_DISPLAY_SECONDS = 1.5
RESULT_SUCCESS_DISPLAY_FRAMES = int(FPS * RESULT_SUCCESS_DISPLAY_SECONDS)

# Word list file
WORD_LIST_FILENAME = "anagram_words.txt"
# Construct path robustly
WORD_LIST_PATH = os.path.join("data", WORD_LIST_FILENAME) # Default relative path
if 'ROOT_DIR' in globals() and ROOT_DIR: # Check if ROOT_DIR is defined and not empty
    WORD_LIST_PATH = os.path.join(ROOT_DIR, "data", WORD_LIST_FILENAME)
else:
    print("Warning: ROOT_DIR not found in config, using relative path for word list.")

# Keys
START_KEY = pygame.K_RETURN
SUBMIT_KEY = pygame.K_RETURN
RETRY_KEY = pygame.K_r
CONFIRM_KEY = pygame.K_RETURN
SKIP_KEY = pygame.K_TAB


# --- Helper Functions ---

def draw_text_with_shadow(screen, text, font, position, color, shadow_color, shadow_offset=SHADOW_OFFSET, center=True, topright=False):
    """Renders text with shadow. Uses SHADOW_OFFSET constant as default."""
    try:
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
    except Exception as e:
        print(f"Error drawing text '{text}': {e}")


def load_words(filename):
    """Loads words from a file, one word per line."""
    default_words = ["BLOCK", "CHAIN", "TOKEN", "WALLET", "MINING", "CRYPTO"] # Fallback
    if not os.path.exists(filename):
        print(f"Warning: Word file '{filename}' not found. Using default words.")
        return default_words
    try:
        with open(filename, 'r') as f:
            words = [line.strip().upper() for line in f if line.strip()]
        if not words:
            print(f"Warning: Word file '{filename}' is empty. Using default words.")
            return default_words
        print(f"Loaded {len(words)} words from {filename}")
        return words
    except Exception as e:
        print(f"Error loading word file '{filename}': {e}. Using default words.")
        return default_words

# --- Main Minigame Function ---

def play_anagram(screen, clock):
    """
    Runs the Anagram minigame with hint, skip, manual start, and retry option.
    Returns: True (success), False (failure after choosing not to retry), None (cancelled).
    """
    print("Entering Anagram minigame...")
    # --- Initialization ---
    # One assignment per line for clarity
    main_font = None
    instr_font = None
    prompt_font = None
    hint_font = None
    try:
        main_font = pygame.font.SysFont(DEFAULT_FONT_NAME, FONT_SIZE)
        instr_font = pygame.font.SysFont(DEFAULT_FONT_NAME, INSTR_FONT_SIZE)
        prompt_font = pygame.font.SysFont(DEFAULT_FONT_NAME, PROMPT_FONT_SIZE)
        hint_font = pygame.font.SysFont(DEFAULT_FONT_NAME, HINT_FONT_SIZE)
    except Exception as e:
        print(f"Font load error: {e}. Using default fonts.")
        # Fallback fonts
        main_font = pygame.font.Font(None, FONT_SIZE)
        instr_font = pygame.font.Font(None, INSTR_FONT_SIZE)
        prompt_font = pygame.font.Font(None, PROMPT_FONT_SIZE)
        hint_font = pygame.font.Font(None, HINT_FONT_SIZE)

    word_list = load_words(WORD_LIST_PATH)
    if not word_list:
        print("Error: No words available for the anagram game. Exiting.")
        return False # Treat as failure

    # --- Load Background ---
    background_surface = None
    try:
        if 'UI_BACKGROUND' in globals() and UI_BACKGROUND and os.path.exists(UI_BACKGROUND):
            background_surface = pygame.image.load(UI_BACKGROUND).convert()
            background_surface = pygame.transform.scale(background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Loaded UI_BACKGROUND asset.")
        else:
            print("UI_BACKGROUND path not found, empty, or variable missing.")
    except pygame.error as e:
        print(f"Failed to load UI_BACKGROUND (Pygame Error): {e}")
    except Exception as e:
        print(f"Failed to load UI_BACKGROUND (Other Error): {e}")

    if background_surface is None: # Fallback background
        print("Using fallback gradient background.")
        background_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Use fill for potentially better performance on some systems
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(GRADIENT_START[0] + t * (GRADIENT_END[0] - GRADIENT_START[0]))
            g = int(GRADIENT_START[1] + t * (GRADIENT_END[1] - GRADIENT_START[1]))
            b = int(GRADIENT_START[2] + t * (GRADIENT_END[2] - GRADIENT_START[2]))
            background_surface.fill((r, g, b), (0, y, SCREEN_WIDTH, 1))

    # --- Load and Play Music ---
    music_playing = False
    try:
        pygame.mixer.init() # Safe to call multiple times
        # Check SOUND_CUTSCENE_MUSIC exists and is valid before loading
        if 'SOUND_CUTSCENE_MUSIC' in globals() and SOUND_CUTSCENE_MUSIC and os.path.exists(SOUND_CUTSCENE_MUSIC):
            pygame.mixer.music.load(SOUND_CUTSCENE_MUSIC)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)
            music_playing = True
            print("Music loaded and playing.")
        else:
            print("SOUND_CUTSCENE_MUSIC path not found, empty, or variable missing.")
    except pygame.error as e:
        print(f"Failed to load or play music (Pygame Error): {e}")
    except Exception as e:
        print(f"An unexpected error occurred during music setup: {e}")

    # --- Game State Variables ---
    word = ""
    scrambled = ""
    hint_letter = ""
    hint_index = -1
    player_input = ""
    success = False
    submitted = False
    result_message = ""
    result_timer = 0

    game_state = "WAITING_START"
    final_outcome = None # Stores True/False/None result

    def _setup_new_word():
        """Selects, scrambles a word, and determines a hint."""
        nonlocal word, scrambled, player_input, submitted, result_message, hint_letter, hint_index
        if not word_list: # Should not happen based on check above, but safety first
            print("Error: Word list is empty in _setup_new_word.")
            # How to handle this? Maybe force an exit? For now, use a placeholder.
            word = "ERROR"
            scrambled = "RORRE"
            hint_index = 0
            hint_letter = "E"
            return

        word = random.choice(word_list)
        # Ensure scrambling actually changes the word
        scramble_attempts = 0
        scrambled = "".join(random.sample(word, len(word)))
        while scrambled == word and len(word) > 1 and scramble_attempts < 10:
             scrambled = "".join(random.sample(word, len(word)))
             scramble_attempts += 1

        # Generate hint
        if len(word) > 0:
            hint_index = random.randrange(len(word))
            hint_letter = word[hint_index]
        else:
            hint_index = -1
            hint_letter = ""

        player_input = ""
        submitted = False
        result_message = ""
        print(f"New anagram word: {word} (Scrambled: {scrambled}), Hint: '{hint_letter}' at index {hint_index}")

    # --- Main Loop Wrapped in Try/Finally ---
    running = True
    try: # Ensure music stops even if errors occur or loop exits unexpectedly
        while running:
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    final_outcome = None; running = False; break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        final_outcome = None; running = False; break

                    # State-specific key handling
                    if game_state == "WAITING_START":
                        if event.key == START_KEY:
                            print("Starting anagram...")
                            _setup_new_word()
                            game_state = "WAITING_INPUT"
                    elif game_state == "WAITING_INPUT":
                        if event.key == SUBMIT_KEY:
                            if player_input: # Can only submit if input exists
                                success = (player_input == word)
                                submitted = True
                                result_message = "Success! Correct word!" if success else f"Failed! The word was {word}."
                                game_state = "SHOWING_RESULT"
                                result_timer = 0 # Reset timer only used for success display
                                print(f"Player submitted: {player_input}. Correct: {success}")
                        elif event.key == pygame.K_BACKSPACE:
                            player_input = player_input[:-1]
                        elif event.key == SKIP_KEY:
                            print("Word skipped by player.")
                            _setup_new_word() # Get a new word immediately
                        elif event.unicode.isalpha(): # Only append letters
                            player_input += event.unicode.upper()
                    elif game_state == "SHOWING_RESULT":
                        if not success: # Only handle keys on failure screen
                            if event.key == RETRY_KEY:
                                print("Retrying anagram...")
                                player_input = ""; submitted = False; result_message = ""
                                game_state = "WAITING_INPUT" # Go back to input for same word
                            elif event.key == CONFIRM_KEY:
                                print("Continuing after failure.")
                                final_outcome = False # Set failure outcome
                                running = False; break # Exit loop

            if not running: break # Exit while loop if running became False

            # --- State Machine Logic ---
            if game_state == "SHOWING_RESULT" and success:
                result_timer += 1 # Use frame counter
                if result_timer > RESULT_SUCCESS_DISPLAY_FRAMES:
                    final_outcome = True # Set success outcome
                    running = False # Exit loop

            # --- Drawing ---
            screen.blit(background_surface, (0, 0))

            # Title / Instructions
            instr_pos = (CENTER_X, INSTR_Y)
            if game_state == "WAITING_START":
                draw_text_with_shadow(screen, "Unscramble the Word!", instr_font, instr_pos, WHITE, SHADOW_COLOR)
                draw_text_with_shadow(screen, "Press Enter to Start", main_font, (CENTER_X, CENTER_Y), WHITE, SHADOW_COLOR)
            else:
                 draw_text_with_shadow(screen, "Unscramble!", instr_font, instr_pos, WHITE, SHADOW_COLOR)

            # Gameplay Elements
            if game_state == "WAITING_INPUT":
                draw_text_with_shadow(screen, f"{scrambled}", main_font, (CENTER_X, SCRAMBLED_Y), WHITE, SHADOW_COLOR)
                # Hint Display
                hint_display_string = ""
                if hint_index != -1 and word: # Ensure word is not empty
                     hint_display_string = ("_ " * hint_index) + hint_letter + (" _" * (len(word) - 1 - hint_index))
                draw_text_with_shadow(screen, f"Hint: {hint_display_string}", hint_font, (CENTER_X, HINT_Y), HINT_COLOR, SHADOW_COLOR)
                # Input Area
                input_display = player_input if player_input else "_"
                draw_text_with_shadow(screen, f"Your guess: {input_display}", main_font, (CENTER_X, INPUT_Y), WHITE, SHADOW_COLOR)
                # Prompts
                draw_text_with_shadow(screen, "Press Enter to Submit  |  Tab to Skip Word", prompt_font, (CENTER_X, INPUT_Y + PROMPT_Y_OFFSET), PROMPT_COLOR, SHADOW_COLOR)

            elif game_state == "SHOWING_RESULT":
                # Final state display
                draw_text_with_shadow(screen, f"{scrambled}", main_font, (CENTER_X, SCRAMBLED_Y), WHITE, SHADOW_COLOR)
                draw_text_with_shadow(screen, f"Your guess: {player_input}", main_font, (CENTER_X, INPUT_Y), WHITE, SHADOW_COLOR)
                # Result message
                result_color = COLOR_GREEN if success else COLOR_RED
                draw_text_with_shadow(screen, result_message, main_font, (CENTER_X, RESULT_Y), result_color, SHADOW_COLOR)
                # Options on failure
                if not success:
                    draw_text_with_shadow(screen, "Press R to Retry, Enter to Continue", prompt_font, (CENTER_X, RESULT_Y + PROMPT_Y_OFFSET), PROMPT_COLOR, SHADOW_COLOR)

            # --- Update Display ---
            pygame.display.flip()
            clock.tick(FPS)

    finally:
        # --- Stop Music --- <<< Ensure music stops in finally block
        if music_playing:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                print("Music stopped.")
            except pygame.error as e:
                print(f"Error stopping music: {e}")
            except Exception as e: # Catch other potential errors during cleanup
                 print(f"Unexpected error stopping music: {e}")


    # --- Return Outcome ---
    print(f"Exiting Anagram. Final Outcome: {final_outcome}")
    return final_outcome


# --- Example usage ---
if __name__ == '__main__':
    print("Running Anagram minigame standalone test...")
    # Initialize Pygame modules
    pygame.init()
    pygame.font.init()
    pygame.mixer.init() # <<< Initialize mixer for testing

    # Fallback / Import config safely for testing
    try: from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, DEFAULT_FONT, UI_BACKGROUND, ROOT_DIR, SOUND_CUTSCENE_MUSIC
    except ImportError: print("Warning: Using default values for testing."); SCREEN_WIDTH, SCREEN_HEIGHT=800,600; FPS=60; WHITE=(240, 240, 242); DEFAULT_FONT="Arial"; UI_BACKGROUND=""; SOUND_CUTSCENE_MUSIC=""
    if 'ROOT_DIR' not in locals(): ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # --- Removed dummy directory/file creation ---
    # Relies on data/anagram_words.txt existing or load_words() fallback
    print(f"Attempting to use word list at: {WORD_LIST_PATH}")
    # ---

    # Check sound path
    sound_path = SOUND_CUTSCENE_MUSIC
    if 'ROOT_DIR' in locals() and SOUND_CUTSCENE_MUSIC and not os.path.exists(sound_path) and not os.path.isabs(sound_path): sound_path = os.path.join(ROOT_DIR, SOUND_CUTSCENE_MUSIC) # Allow relative path in config
    if not os.path.exists(sound_path): print(f"Warning: Music file not found at {sound_path}.")

    # Setup screen and clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)); pygame.display.set_caption("Anagram Minigame Test"); clock = pygame.time.Clock()
    # Call the main function
    game_result = play_anagram(screen, clock)
    print(f"Minigame result: {game_result}")
    # Quit Pygame
    pygame.quit()
    print("Standalone test finished.")