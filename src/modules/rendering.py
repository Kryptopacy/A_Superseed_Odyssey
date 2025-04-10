# src/modules/rendering.py
import pygame
import os
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, GOLD, DEFAULT_FONT, HUD_HEIGHT, MAZE_WIDTH, MAZE_HEIGHT, EXIT_ARROW_SPRITE, MORNING_GLORY, CRITICAL_TINT, TILE_SIZE

def draw_ui(screen, player, world, font, heart_icon, coin_icon, virus_icon, ring_icon, infection_active):
    hud_panel = pygame.Surface((SCREEN_WIDTH, 30), pygame.SRCALPHA)
    hud_panel.fill((0, 0, 0, 180))
    pygame.draw.rect(hud_panel, WHITE, (0, 0, SCREEN_WIDTH, 30), 2)

    hp_bar = pygame.Surface((100, 15), pygame.SRCALPHA)
    hp_width = (player.hp / player.max_hp) * 100
    for x in range(int(hp_width)):
        r = 255 if player.hp > 50 else int(255 * (player.hp / 50))
        g = 255 if player.hp < 50 else int(255 * (1 - (player.hp - 50) / 50))
        b = 0
        pygame.draw.line(hp_bar, (r, g, b), (x, 0), (x, 15))
    alpha = 255 if player.hp > 30 else int(128 + 127 * (pygame.time.get_ticks() % 1000) / 1000)
    hp_bar.set_alpha(alpha)

    infection_bar = pygame.Surface((100, 15), pygame.SRCALPHA)
    infection_width = (player.infection_level / 100) * 100
    for x in range(int(infection_width)):
        alpha = int(255 * (x / infection_width))
        pygame.draw.line(infection_bar, (255, 0, 0, alpha), (x, 0), (x, 15))

    # Optimism Ring fill bar
    ring_fill_bar = pygame.Surface((100, 15), pygame.SRCALPHA)
    ring_fill_width = player.optimism_ring_fill
    for x in range(int(ring_fill_width)):
        alpha = int(255 * (x / 100))
        pygame.draw.line(ring_fill_bar, (255, 215, 0, alpha), (x, 0), (x, 15))

    screen.blit(hud_panel, (0, 20))

    screen.blit(heart_icon, (10, 25))
    screen.blit(hp_bar, (40, 25))
    hp_text = font.render(f"{player.hp}", True, WHITE)
    hp_shadow = font.render(f"{player.hp}", True, BLACK)
    screen.blit(hp_shadow, (150 + 2, 25 + 2))
    screen.blit(hp_text, (150, 25))

    if infection_active:
        screen.blit(virus_icon, (180, 25))
        screen.blit(infection_bar, (210, 25))
        infection_text = font.render(f"{int(player.infection_level)}%", True, WHITE)
        infection_shadow = font.render(f"{int(player.infection_level)}%", True, BLACK)
        screen.blit(infection_shadow, (320 + 2, 25 + 2))
        screen.blit(infection_text, (320, 25))

    sapa_count = len(world.get_current_scene().sapas)
    sapa_text = font.render(f"{sapa_count} Sapa", True, WHITE)
    sapa_shadow = font.render(f"{sapa_count} Sapa", True, BLACK)
    screen.blit(sapa_shadow, (360 + 2, 25 + 2))
    screen.blit(sapa_text, (360, 25))

    area_text = font.render(f"Area: {world.areas[world.current_area].name}", True, WHITE)
    area_shadow = font.render(f"Area: {world.areas[world.current_area].name}", True, BLACK)
    screen.blit(area_shadow, (450 + 2, 25 + 2))
    screen.blit(area_text, (450, 25))

    screen.blit(coin_icon, (650, 25))
    currency_text = font.render(f"{player.inventory.supercollateral}", True, WHITE)
    currency_shadow = font.render(f"{player.inventory.supercollateral}", True, BLACK)
    screen.blit(currency_shadow, (680 + 2, 25 + 2))
    screen.blit(currency_text, (680, 25))

    # Draw Optimism Ring fill bar
    screen.blit(ring_icon, (720, 25))
    screen.blit(ring_fill_bar, (750, 25))
    if player.optimism_ring_cooldown > 0:
        cooldown_text = font.render(f"CD: {int(player.optimism_ring_cooldown)}s", True, WHITE)
        cooldown_shadow = font.render(f"CD: {int(player.optimism_ring_cooldown)}s", True, BLACK)
        screen.blit(cooldown_shadow, (850 + 2, 25 + 2))
        screen.blit(cooldown_text, (850, 25))
    else:
        fill_text = font.render(f"{int(player.optimism_ring_fill)}%", True, WHITE)
        fill_shadow = font.render(f"{int(player.optimism_ring_fill)}%", True, BLACK)
        screen.blit(fill_shadow, (850 + 2, 25 + 2))
        screen.blit(fill_text, (850, 25))

    # Add player level and XP
    level_text = font.render(f"Level: {player.level}", True, WHITE)
    level_shadow = font.render(f"Level: {player.level}", True, BLACK)
    screen.blit(level_shadow, (10 + 2, 55 + 2))
    screen.blit(level_text, (10, 55))

    xp_text = font.render(f"XP: {player.xp}/{player.xp_to_next_level}", True, WHITE)
    xp_shadow = font.render(f"XP: {player.xp}/{player.xp_to_next_level}", True, BLACK)
    screen.blit(xp_shadow, (100 + 2, 55 + 2))
    screen.blit(xp_text, (100, 55))

def draw_labels(screen, scene, player, font):
    label_font = pygame.font.SysFont(DEFAULT_FONT, 20)

    label = label_font.render(player.name, True, WHITE)
    label_rect = label.get_rect(center=(player.rect.centerx, player.rect.top - 10))
    pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
    screen.blit(label, label_rect)

    for token in scene.tokens:
        label = label_font.render("Token", True, (0, 255, 255))
        label_rect = label.get_rect(center=(token.centerx, token.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    for checkpoint in scene.checkpoints:
        label = label_font.render("Checkpoint", True, (0, 255, 0))
        label_rect = label.get_rect(center=(checkpoint.centerx, checkpoint.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    if scene.sword:
        label = label_font.render("Sword", True, (255, 255, 0))
        label_rect = label.get_rect(center=(scene.sword.centerx, scene.sword.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    for fragment in scene.fragments:
        label = label_font.render("Fragment", True, (255, 165, 0))
        label_rect = label.get_rect(center=(fragment.centerx, fragment.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    for enemy in scene.sapas:
        label = label_font.render(f"{enemy.name} (Lvl {enemy.level})", True, (255, 0, 0))
        label_rect = label.get_rect(center=(enemy.rect.centerx, enemy.rect.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    if scene.npc:
        label = label_font.render("NPC" if not scene.npc.is_vitalik else "Vitalik", True, (255, 255, 0) if scene.npc.is_vitalik else (0, 255, 255))
        label_rect = label.get_rect(center=(scene.npc.rect.centerx, scene.npc.rect.top - 10))
        pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
        screen.blit(label, label_rect)

    if hasattr(scene, 'npcs'):
        for npc in scene.npcs:
            label = label_font.render("NPC" if not npc.is_vitalik else "Vitalik", True, (255, 255, 0) if npc.is_vitalik else (0, 255, 255))
            label_rect = label.get_rect(center=(npc.rect.centerx, npc.rect.top - 10))
            pygame.draw.rect(screen, (0, 0, 0, 180), label_rect.inflate(4, 4))
            screen.blit(label, label_rect)

def draw_exits(screen, scene, font, exit_arrow_sprite):
    entry_x, entry_y = scene.entry
    exit_x, exit_y = scene.exit

    if "west" in scene.exits:
        if entry_x == 0:  # Left side
            if exit_arrow_sprite:
                screen.blit(exit_arrow_sprite, (10, (entry_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT - 15))
            else:
                pygame.draw.polygon(screen, WHITE, [(10, (entry_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT), (30, (entry_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT), (30, (entry_y * TILE_SIZE + TILE_SIZE + 10 + 20) + HUD_HEIGHT)])
            exit_text = font.render("Previous Scene", True, WHITE)
            screen.blit(exit_text, (40, (entry_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT))
        elif entry_y == 0:  # Top side
            if exit_arrow_sprite:
                screen.blit(pygame.transform.rotate(exit_arrow_sprite, 90), (entry_x * TILE_SIZE + TILE_SIZE - 15, HUD_HEIGHT + 20))
            else:
                pygame.draw.polygon(screen, WHITE, [(entry_x * TILE_SIZE + TILE_SIZE, HUD_HEIGHT + 20), (entry_x * TILE_SIZE + TILE_SIZE - 10, HUD_HEIGHT + 40), (entry_x * TILE_SIZE + TILE_SIZE + 10, HUD_HEIGHT + 40)])
            exit_text = font.render("Previous Scene", True, WHITE)
            screen.blit(exit_text, (entry_x * TILE_SIZE + TILE_SIZE - 40, HUD_HEIGHT + 30))
        else:  # Bottom side
            if exit_arrow_sprite:
                screen.blit(pygame.transform.rotate(exit_arrow_sprite, -90), (entry_x * TILE_SIZE + TILE_SIZE - 15, SCREEN_HEIGHT - 70))
            else:
                pygame.draw.polygon(screen, WHITE, [(entry_x * TILE_SIZE + TILE_SIZE, SCREEN_HEIGHT - 50), (entry_x * TILE_SIZE + TILE_SIZE - 10, SCREEN_HEIGHT - 70), (entry_x * TILE_SIZE + TILE_SIZE + 10, SCREEN_HEIGHT - 70)])
            exit_text = font.render("Previous Scene", True, WHITE)
            screen.blit(exit_text, (entry_x * TILE_SIZE + TILE_SIZE - 40, SCREEN_HEIGHT - 60))

    if "east" in scene.exits:
        if exit_x == MAZE_WIDTH - 1:  # Right side
            if exit_arrow_sprite:
                screen.blit(pygame.transform.flip(exit_arrow_sprite, True, False), (SCREEN_WIDTH - 40, (exit_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT - 15))
            else:
                pygame.draw.polygon(screen, WHITE, [(SCREEN_WIDTH - 10, (exit_y * TILE_SIZE + TILE_SIZE + 20) + HUD_HEIGHT), (SCREEN_WIDTH - 30, (exit_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT), (SCREEN_WIDTH - 30, (exit_y * TILE_SIZE + TILE_SIZE + 10 + 20) + HUD_HEIGHT)])
            exit_text = font.render("Next Scene", True, WHITE)
            screen.blit(exit_text, (SCREEN_WIDTH - 150, (exit_y * TILE_SIZE + TILE_SIZE - 10 + 20) + HUD_HEIGHT))
        elif exit_y == MAZE_HEIGHT - 1:  # Bottom side
            if exit_arrow_sprite:
                screen.blit(pygame.transform.rotate(exit_arrow_sprite, -90), (exit_x * TILE_SIZE + TILE_SIZE - 15, SCREEN_HEIGHT - 70))
            else:
                pygame.draw.polygon(screen, WHITE, [(exit_x * TILE_SIZE + TILE_SIZE, SCREEN_HEIGHT - 50), (exit_x * TILE_SIZE + TILE_SIZE - 10, SCREEN_HEIGHT - 70), (exit_x * TILE_SIZE + TILE_SIZE + 10, SCREEN_HEIGHT - 70)])
            exit_text = font.render("Next Scene", True, WHITE)
            screen.blit(exit_text, (exit_x * TILE_SIZE + TILE_SIZE - 40, SCREEN_HEIGHT - 60))
        else:  # Top side
            if exit_arrow_sprite:
                screen.blit(pygame.transform.rotate(exit_arrow_sprite, 90), (exit_x * TILE_SIZE + TILE_SIZE - 15, HUD_HEIGHT + 20))
            else:
                pygame.draw.polygon(screen, WHITE, [(exit_x * TILE_SIZE + TILE_SIZE, HUD_HEIGHT + 20), (exit_x * TILE_SIZE + TILE_SIZE - 10, HUD_HEIGHT + 40), (exit_x * TILE_SIZE + TILE_SIZE + 10, HUD_HEIGHT + 40)])
            exit_text = font.render("Next Scene", True, WHITE)
            screen.blit(exit_text, (exit_x * TILE_SIZE + TILE_SIZE - 40, HUD_HEIGHT + 30))

def draw_minimap(screen, scene, player, font):
    print("Drawing minimap...")
    minimap_size = 200
    scale = minimap_size / max(MAZE_WIDTH * TILE_SIZE, MAZE_HEIGHT * TILE_SIZE)
    minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
    # Use a solid color background for better contrast instead of UI_BACKGROUND
    minimap_surface.fill((50, 50, 50))  # Dark gray background for contrast

    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if scene.grid[y][x] == 1:
                pygame.draw.rect(minimap_surface, (100, 100, 100), (x * scale * TILE_SIZE, y * scale * TILE_SIZE, scale * TILE_SIZE, scale * TILE_SIZE))

    player_x = player.rect.x * scale
    player_y = (player.rect.y - HUD_HEIGHT) * scale
    pygame.draw.rect(minimap_surface, MORNING_GLORY if player.gender == "male" else (255, 105, 180), (player_x, player_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for enemy in scene.sapas:
        enemy_x = enemy.rect.x * scale
        enemy_y = (enemy.rect.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (255, 0, 0), (enemy_x, enemy_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for token in scene.tokens:
        token_x = token.x * scale
        token_y = (token.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (0, 255, 255), (token_x, token_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for checkpoint in scene.checkpoints:
        checkpoint_x = checkpoint.x * scale
        checkpoint_y = (checkpoint.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (0, 255, 0), (checkpoint_x, checkpoint_y, scale * TILE_SIZE, scale * TILE_SIZE))

    if scene.sword:
        sword_x = scene.sword.x * scale
        sword_y = (scene.sword.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (255, 255, 0), (sword_x, sword_y, scale * TILE_SIZE, scale * TILE_SIZE))

    for fragment in scene.fragments:
        fragment_x = fragment.x * scale
        fragment_y = (fragment.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (255, 165, 0), (fragment_x, fragment_y, scale * TILE_SIZE, scale * TILE_SIZE))

    if scene.npc:
        npc_x = scene.npc.rect.x * scale
        npc_y = (scene.npc.rect.y - HUD_HEIGHT) * scale
        pygame.draw.rect(minimap_surface, (0, 255, 255) if not scene.npc.is_vitalik else (255, 255, 0), (npc_x, npc_y, scale * TILE_SIZE, scale * TILE_SIZE))

    if hasattr(scene, 'npcs'):
        for npc in scene.npcs:
            npc_x = npc.rect.x * scale
            npc_y = (npc.rect.y - HUD_HEIGHT) * scale
            pygame.draw.rect(minimap_surface, (0, 255, 255) if not npc.is_vitalik else (255, 255, 0), (npc_x, npc_y, scale * TILE_SIZE, scale * TILE_SIZE))

    screen.blit(minimap_surface, (SCREEN_WIDTH - minimap_size - 10, SCREEN_HEIGHT - minimap_size - 10))
    close_text = font.render("Press M to close", True, WHITE)
    screen.blit(close_text, (SCREEN_WIDTH - minimap_size - 10, SCREEN_HEIGHT - 25))

def apply_critical_tint(screen, infection_active, player):
    if infection_active and player.infection_level >= 80 and not player.inventory.has_sword:
        tint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        tint.fill(CRITICAL_TINT)
        screen.blit(tint, (0, 0))