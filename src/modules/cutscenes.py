# src/modules/cutscenes.py
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TANGOA, WHITE, BLACK, UI_BACKGROUND
from src.modules.ui import DialogueBox

def play_intro_cutscene(screen, clock, player, ui_background):
    print("Entering play_intro_cutscene...")
    try:
        pronoun = "he" if player.gender == "male" else "she"
        lines = [
            f"Vitalik: Welcome to the world of Krypto, {player.name}.",
            "Vitalik: Long ago, Krypto thrived under the Superseed’s radiant glow, a beacon of peace and prosperity.",
            "Vitalik: The ElPee, its protectors, stood as sentinels against Seisan, the embodiment of chaos and liquidation.",
            "Vitalik: But Seisan corrupted Skuld, promising power and immortality, and together they shattered the Superseed.",
            "Vitalik: With its fragments scattered, Krypto fell into darkness—famine, disease, and the Sapa curse emerged.",
            f"Vitalik: You, {player.name}, a miscreant of the MEV gang, have been bitten by a Sapa, half-claiming your soul.",
            f"Vitalik: Determined to defy your fate, you must rise as the Sapa Slayer."
        ]
        dialogue_box = DialogueBox()
        dialogue_box.show(lines)
        running = True

        while running and dialogue_box.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit event in intro_cutscene.")
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        dialogue_box.next_line()
                    elif event.key == pygame.K_ESCAPE:
                        print("Intro cutscene skipped by user.")
                        return False

            screen.blit(ui_background, (0, 0))
            dialogue_box.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        # Add fade-out effect
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill(BLACK)
        for alpha in range(0, 255, 5):
            fade_surface.set_alpha(alpha)
            screen.blit(ui_background, (0, 0))
            pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 0)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)

        screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.delay(500)

        print("Exiting intro_cutscene successfully.")
        return True
    except Exception as e:
        print(f"Error in intro_cutscene: {e}")
        raise

def play_area_cutscene(screen, clock, player, area_id, ui_background):
    print(f"Entering play_area_cutscene for Area {area_id}...")
    try:
        # Add fade-in effect
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill(BLACK)
        for alpha in range(255, 0, -5):
            fade_surface.set_alpha(alpha)
            screen.blit(ui_background, (0, 0))
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)

        pronoun = "he" if player.gender == "male" else "she"
        if area_id == 0:
            lines = [
                f"Vitalik: You’ve arrived at the Slums of Krypto, {player.name}.",
                "Vitalik: Once a bustling hub, now a cursed wasteland where the Sapa roam.",
                f"Vitalik: A Sapa’s bite courses through you, spreading the curse—seek me, Sage Vitalik, for the Sword of Solvency.",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]
        elif area_id == 1:
            lines = [
                f"Vitalik: You enter Seisan Spires, {player.name}.",
                "Vitalik: The air grows darker as Seisan’s chaos takes hold.",
                "Vitalik: The ElPee, protectors of the Superseed, were wiped out by Seisan and Skuld, the Debt King.",
                f"Vitalik: {'With the Sword of Solvency, your infection is halted.' if player.inventory.has_sword else 'Find the Sword of Solvency to halt your infection.'} Collect the first fragment to cure yourself.",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]
        elif area_id == 2:
            lines = [
                f"Vitalik: You enter the Ethereum Chain Ruins, {player.name}.",
                "Vitalik: Ancient ruins pulse with forgotten power.",
                "Vitalik: Seisan promised Skuld unlimited power, immortality, and a crown to rule Krypto, shattering the Superseed.",
                "Vitalik: Collect fragments to weaken Skuld’s grip. Beware of stronger Sapas.",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]
        elif area_id == 3:
            lines = [
                f"Vitalik: You enter Optimism’s Echo, {player.name}.",
                "Vitalik: A faint light shines amidst the chaos.",
                "Vitalik: With the Superseed destroyed, Krypto fell into darkness, famine, and disease.",
                "Vitalik: The fragments are closer, but so is danger. Keep going!",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]
        elif area_id == 4:
            lines = [
                f"Vitalik: You enter the MEV Gang Hideout, {player.name}.",
                "Vitalik: The MEV gang’s corruption fuels the Sapa curse.",
                f"Vitalik: {pronoun.capitalize()} once reveled in Krypto’s underbelly as part of this gang, but now you fight against them.",
                "Vitalik: Prepare for a fierce battle ahead.",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]
        elif area_id == 5:
            lines = [
                f"Vitalik: You enter Skuld’s Lair, {player.name}.",
                "Vitalik: The Debt King awaits, surrounded by chaos.",
                "Vitalik: This is your final stand to restore the Superseed and save Krypto.",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]
        else:
            lines = [
                f"Vitalik: Entering an unknown region, {player.name}.",
                "Vitalik: Press P to access the menu for tutorial, minimap, and more."
            ]

        dialogue_box = DialogueBox()
        dialogue_box.show(lines)
        running = True

        while running and dialogue_box.active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit event in area_cutscene.")
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        dialogue_box.next_line()
                    elif event.key == pygame.K_ESCAPE:
                        print(f"Area {area_id} cutscene skipped by user.")
                        return False

            screen.blit(ui_background, (0, 0))
            dialogue_box.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)

        print(f"Exiting area_cutscene for Area {area_id} successfully.")
        return True
    except Exception as e:
        print(f"Error in area_cutscene: {e}")
        raise