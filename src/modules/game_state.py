# src/modules/game_state.py
import pickle
from src.modules.npcs import NPC

def save_game(player, world, vitalik_freed, choice_made, self_save_choice_made, vitalik):
    print("Saving game state...")
    try:
        game_state = {
            'player': {
                'name': player.name,
                'gender': player.gender,
                'rect': (player.rect.x, player.rect.y),
                'hp': player.hp,
                'infection_level': player.infection_level,
                'attack_power': player.attack_power,
                'ranged_attacks': player.ranged_attacks,
                'optimism_ring_duration': player.optimism_ring_duration,
                'optimism_ring_timer': player.optimism_ring_timer,
                'easy_mode': player.easy_mode,
                'level': player.level,
                'xp': player.xp,
                'xp_to_next_level': player.xp_to_next_level,
                'inventory': {
                    'supercollateral': player.inventory.supercollateral,
                    'fragments': player.inventory.fragments,
                    'has_sword': player.inventory.has_sword
                }
            },
            'world': {
                'current_area': world.current_area,
                'current_scene': world.current_scene
            },
            'vitalik_freed': vitalik_freed,
            'choice_made': choice_made,
            'self_save_choice_made': self_save_choice_made,
            'vitalik': {
                'is_freed': vitalik.is_freed if vitalik else False,
                'following': vitalik.following if vitalik else False,
                'invulnerable': vitalik.invulnerable if vitalik else False,
                'rect': (vitalik.rect.x, vitalik.rect.y) if vitalik else None
            }
        }
        with open('savegame.pkl', 'wb') as f:
            pickle.dump(game_state, f)
        print("Game state saved successfully.")
    except Exception as e:
        print(f"Failed to save game state: {e}")

def load_game():
    print("Loading game state...")
    try:
        with open('savegame.pkl', 'rb') as f:
            game_state = pickle.load(f)
        return game_state
    except Exception as e:
        print(f"Failed to load game state: {e}. Starting new game.")
        return None