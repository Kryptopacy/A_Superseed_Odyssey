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
OPTIMISM_RING_EFFECT = os.path.join(ROOT_DIR, "assets/sprites/optimism_ring_effect.png")  # Added for Optimism Ring effect

# Area-specific floor and wall PNGs (32x32, will be scaled to 40x40)
AREA_0_FLOOR = os.path.join(ROOT_DIR, "assets/images/area_0_floor.png")  # Slums: dirt floor
AREA_0_WALL = os.path.join(ROOT_DIR, "assets/images/area_0_wall.png")    # Slums: wooden wall
AREA_1_FLOOR = os.path.join(ROOT_DIR, "assets/images/area_1_floor.png")  # Spires: stone floor
AREA_1_WALL = os.path.join(ROOT_DIR, "assets/images/area_1_wall.png")    # Spires: crystal wall
AREA_2_FLOOR = os.path.join(ROOT_DIR, "assets/images/area_2_floor.png")  # Ruins: brick floor
AREA_2_WALL = os.path.join(ROOT_DIR, "assets/images/area_2_wall.png")    # Ruins: cracked stone wall
AREA_3_FLOOR = os.path.join(ROOT_DIR, "assets/images/area_3_floor.png")  # Echo: purple mystical floor
AREA_3_WALL = os.path.join(ROOT_DIR, "assets/images/area_3_wall.png")    # Echo: glowing wall
AREA_4_FLOOR = os.path.join(ROOT_DIR, "assets/images/area_4_floor.png")  # Hideout: dark tech floor
AREA_4_WALL = os.path.join(ROOT_DIR, "assets/images/area_4_wall.png")    # Hideout: metal wall
AREA_5_FLOOR = os.path.join(ROOT_DIR, "assets/images/area_5_floor.png")  # Lair: water floor
AREA_5_WALL = os.path.join(ROOT_DIR, "assets/images/area_5_wall.png")    # Lair: dark stone wall

# Attack visualization sprites
MELEE_ATTACK_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/melee_attack_sprite.png")
RANGED_ATTACK_SPRITE = os.path.join(ROOT_DIR, "assets/sprites/ranged_attack_sprite.png")

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