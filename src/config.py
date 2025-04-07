# src/config.py
import os

# Determine the root directory (A_Superseed_Odyssey)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40
MORNING_GLORY = (147, 208, 207)
TANGOA = (14, 39, 59)
ALUMINUM = (128, 131, 134)
WHITE = (240, 240, 242)
BLACK = (8, 8, 6)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
CRITICAL_TINT = (255, 0, 0, 100)
PLAYER_SPEED = 5
MAZE_WIDTH = 20
MAZE_HEIGHT = 13
EASY_MODE_FACTOR = 0.5
SCENE_WIDTH = 20
SCENE_HEIGHT = 13
HUD_HEIGHT = 50

# Sound paths
SOUND_FRAGMENT = os.path.join(ROOT_DIR, "assets/sounds/effects/fragment_collect.wav")
SOUND_ATTACK = os.path.join(ROOT_DIR, "assets/sounds/effects/attack.wav")
SOUND_VICTORY = os.path.join(ROOT_DIR, "assets/sounds/effects/victory.wav")
SOUND_PLAYER_HIT = os.path.join(ROOT_DIR, "assets/sounds/effects/player_hit.wav")
SOUND_ENEMY_HIT = os.path.join(ROOT_DIR, "assets/sounds/effects/enemy_hit.wav")
SOUND_BOSS_DEATH = os.path.join(ROOT_DIR, "assets/sounds/effects/boss_death.wav")
SOUND_GAME_MUSIC = os.path.join(ROOT_DIR, "assets/sounds/music/game_background_music.mp3")
SOUND_CUTSCENE_MUSIC = os.path.join(ROOT_DIR, "assets/sounds/music/cutscene_music.mp3")
SOUND_BOSS_MUSIC = os.path.join(ROOT_DIR, "assets/sounds/music/boss_music.mp3")

# Image paths
UI_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/ui_background.png")
HUD_HEART_ICON = os.path.join(ROOT_DIR, "assets/images/heart_icon.png")
HUD_COIN_ICON = os.path.join(ROOT_DIR, "assets/images/coin_icon.png")
HUD_VIRUS_ICON = os.path.join(ROOT_DIR, "assets/images/virus_icon.png")
HUD_RING_ICON = os.path.join(ROOT_DIR, "assets/images/ring_icon.png")
MALE_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/male_sprite.png")
FEMALE_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/female_sprite.png")

# Area-specific tilesheets (each 80x40, with wall at (0,0) and floor at (40,0))
AREA_0_TILESHEET = os.path.join(ROOT_DIR, "assets/images/area_0_tilesheet.png")  # Dirt floor, wooden wall
AREA_1_TILESHEET = os.path.join(ROOT_DIR, "assets/images/area_1_tilesheet.png")  # Grass floor, stone wall
AREA_2_TILESHEET = os.path.join(ROOT_DIR, "assets/images/area_2_tilesheet.png")  # Stone floor, brick wall
AREA_3_TILESHEET = os.path.join(ROOT_DIR, "assets/images/area_3_tilesheet.png")  # Purple dungeon floor, purple wall
AREA_4_TILESHEET = os.path.join(ROOT_DIR, "assets/images/area_4_tilesheet.png")  # Dark stone floor, dark wall
AREA_5_TILESHEET = os.path.join(ROOT_DIR, "assets/images/area_5_tilesheet.png")  # Water floor, dark stone wall

# Sprite paths for enemies, sword, tokens, checkpoints, fragments
SAPA_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/sapa_sprite.png")
SPLITTER_SAPA_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/splitter_sapa_sprite.png")
PROJECTILE_SAPA_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/projectile_sapa_sprite.png")
CHASER_SAPA_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/chaser_sapa_sprite.png")
DIAGONAL_SAPA_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/diagonal_sapa_sprite.png")
BOSS_1_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/boss_1_sprite.png")
BOSS_2_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/boss_2_sprite.png")
BOSS_3_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/boss_3_sprite.png")
BOSS_4_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/boss_4_sprite.png")
BOSS_5_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/boss_5_sprite.png")
SKULD_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/skuld_sprite.png")
SWORD_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/sword_sprite.png")
TOKEN_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/token_sprite.png")
CHECKPOINT_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/checkpoint_sprite.png")
FRAGMENT_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/fragment_sprite.png")

# Area-specific background paths
AREA_0_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/area_0_background.png")
AREA_1_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/area_1_background.png")
AREA_2_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/area_2_background.png")
AREA_3_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/area_3_background.png")
AREA_4_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/area_4_background.png")
AREA_5_BACKGROUND = os.path.join(ROOT_DIR, "assets/images/backgrounds/area_5_background.png")

DEFAULT_FONT = "Open Sans"