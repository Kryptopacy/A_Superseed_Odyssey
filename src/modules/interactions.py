import pygame
import sys
import random
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DEFAULT_FONT
from src.modules.ui import DialogueBox
from src.modules.minigames.complete_the_seed import play_complete_the_seed
from src.modules.minigames.sapa_dodge import play_sapa_dodge
from src.modules.minigames.anagram import play_anagram
from src.modules.minigames.memory_sequence import play_memory_sequence
from src.modules.minigames.color_match import play_color_match

def get_minigames():
    return [
        {"func": play_complete_the_seed, "requires_gender": False},
        {"func": play_sapa_dodge, "requires_gender": True},
        {"func": play_anagram, "requires_gender": False},
        {"func": play_memory_sequence, "requires_gender": False},
        {"func": play_color_match, "requires_gender": False}
    ]

def vendor_interaction(screen, clock, player, vendor, dialogue_box, ui_background):
    print("Entering vendor_interaction...")
    try:
        font = pygame.font.SysFont(DEFAULT_FONT, 36)
    except:
        print(f"Failed to load font '{DEFAULT_FONT}'. Using default font.")
        font = pygame.font.Font(None, 36)

    panel = pygame.Surface((SCREEN_WIDTH - 80, SCREEN_HEIGHT - 100), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    pygame.draw.rect(panel, WHITE, (0, 0, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 100), 3)

    options = list(vendor.upgrades.keys()) + ["Exit"]
    selected = 0
    running = True

    while running:
        lines = ["Vendor: Welcome to my shop!", f"Vendor: Supercollateral: {player.inventory.supercollateral}"]
        for i, option in enumerate(options):
            if option != "Exit":
                upgrade = vendor.upgrades[option]
                lines.append(f"{i+1}: {option}: {upgrade['description']} (Cost: {upgrade['cost']}) - Press {i+1} to buy")
            else:
                lines.append(f"{len(options)}: Exit - Press {len(options)} to leave or ESC to close")
        dialogue_box.show(lines, show_prompt=False, context="vendor")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in vendor_interaction.")
                return False
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in vendor_interaction: {event.key}")
                if event.key in range(pygame.K_1, pygame.K_9 + 1):
                    index = event.key - pygame.K_1 + 1
                    if 1 <= index <= len(options):
                        selected = index - 1
                        if options[selected] == "Exit":
                            running = False
                        else:
                            upgrade = vendor.upgrades[options[selected]]
                            if player.inventory.spend_supercollateral(upgrade["cost"]):
                                if options[selected] == "Optimism Ring Fill Rate":
                                    player.optimism_ring_fill_rate += upgrade["value"]
                                elif options[selected] == "Attack Power":
                                    player.attack_power += upgrade["value"]
                                elif options[selected] == "Ranged Attacks":
                                    player.ranged_attacks += upgrade["value"]
                                dialogue_box.show([f"Vendor: Purchased {options[selected]}!"], context="default")
                            else:
                                dialogue_box.show(["Vendor: Not enough Supercollateral!"], context="default")
                elif event.key == pygame.K_ESCAPE:
                    running = False

        screen.blit(ui_background, (0, 0))
        screen.blit(panel, (40, 50))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting vendor_interaction...")
    return True

def play_sword_puzzle(screen, clock, dialogue_box, ui_background, player_gender):
    print("Entering play_sword_puzzle...")
    minigames = get_minigames()
    available_minigames = minigames.copy()
    dialogue_box.show(["Vitalik: A puzzle guards the Sword of Solvency! Solve it to proceed. Press Y to start, N to skip, or ESC to close."], context="default")
    choice_made = False
    result = False

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in play_sword_puzzle.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    while available_minigames:
                        selected_minigame = random.choice(available_minigames)
                        try:
                            if selected_minigame["requires_gender"]:
                                puzzle_result = selected_minigame["func"](screen, clock, player_gender)
                            else:
                                puzzle_result = selected_minigame["func"](screen, clock)
                            if puzzle_result is True:
                                result = True
                                choice_made = True
                                break
                            elif puzzle_result is False:
                                dialogue_box.show(["Vitalik: Puzzle failed! Try again. Press Y to retry, N to skip, or ESC to close."], context="default")
                                break
                            elif puzzle_result is None:
                                dialogue_box.show(["Vitalik: Puzzle cancelled. Try again. Press Y to retry, N to skip, or ESC to close."], context="default")
                                break
                        except Exception as e:
                            print(f"Error in play_sword_puzzle with minigame {selected_minigame['func'].__name__}: {e}")
                            available_minigames.remove(selected_minigame)
                            if not available_minigames:
                                dialogue_box.show(["Vitalik: All puzzles failed! You cannot proceed."], context="default")
                                choice_made = True
                                result = False
                                break
                            dialogue_box.show(["Vitalik: That puzzle failed to load. Let's try another one. Press Y to continue, N to skip, or ESC to close."], context="default")
                            break
                elif event.key == pygame.K_n:
                    choice_made = True
                elif event.key == pygame.K_ESCAPE:
                    choice_made = True

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting play_sword_puzzle...")
    return result

def play_vitalik_puzzle(screen, clock, dialogue_box, ui_background, player_gender):
    print("Entering play_vitalik_puzzle...")
    minigames = get_minigames()
    available_minigames = minigames.copy()
    dialogue_box.show(["Vitalik: I’m trapped! Solve this puzzle to free me. Press Y to start, N to skip, or ESC to close."], context="default")
    choice_made = False
    result = False

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in play_vitalik_puzzle.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    while available_minigames:
                        selected_minigame = random.choice(available_minigames)
                        try:
                            if selected_minigame["requires_gender"]:
                                puzzle_result = selected_minigame["func"](screen, clock, player_gender)
                            else:
                                puzzle_result = selected_minigame["func"](screen, clock)
                            if puzzle_result is True:
                                result = True
                                choice_made = True
                                break
                            elif puzzle_result is False:
                                dialogue_box.show(["Vitalik: Puzzle failed! Try again. Press Y to retry, N to skip, or ESC to close."], context="default")
                                break
                            elif puzzle_result is None:
                                dialogue_box.show(["Vitalik: Puzzle cancelled. Try again. Press Y to retry, N to skip, or ESC to close."], context="default")
                                break
                        except Exception as e:
                            print(f"Error in play_vitalik_puzzle with minigame {selected_minigame['func'].__name__}: {e}")
                            available_minigames.remove(selected_minigame)
                            if not available_minigames:
                                dialogue_box.show(["Vitalik: All puzzles failed! You cannot proceed."], context="default")
                                choice_made = True
                                result = False
                                break
                            dialogue_box.show(["Vitalik: That puzzle failed to load. Let's try another one. Press Y to continue, N to skip, or ESC to close."], context="default")
                            break
                elif event.key == pygame.K_n:
                    choice_made = True
                elif event.key == pygame.K_ESCAPE:
                    choice_made = True

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting play_vitalik_puzzle...")
    return result

def play_quest_minigame(screen, clock, dialogue_box, ui_background, minigame_dict, player, player_gender):
    print("Entering play_quest_minigame...")
    minigame_func = minigame_dict["func"]
    requires_gender = minigame_dict["requires_gender"]
    available_minigames = get_minigames().copy()
    dialogue_box.show(["NPC: Complete this challenge for a reward! Press Y to start, N to skip, or ESC to close."], context="default")
    choice_made = False
    reward = 10  # Supercollateral reward for completing the minigame

    while not choice_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in play_quest_minigame.")
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    while available_minigames:
                        minigame_dict = available_minigames[available_minigames.index({"func": minigame_func, "requires_gender": requires_gender})]
                        try:
                            if requires_gender:
                                minigame_result = minigame_func(screen, clock, player_gender)
                            else:
                                minigame_result = minigame_func(screen, clock)
                            if minigame_result is True:
                                player.inventory.add_supercollateral(reward)
                                dialogue_box.show([f"NPC: Well done! Here's your reward: {reward} Supercollateral."], context="default")
                                return True
                            elif minigame_result is False:
                                dialogue_box.show(["NPC: Challenge failed! Try again. Press Y to retry, N to skip, or ESC to close."], context="default")
                                return False
                            elif minigame_result is None:
                                dialogue_box.show(["NPC: Challenge cancelled. Press Y to retry, N to skip, or ESC to close."], context="default")
                                return False
                        except Exception as e:
                            print(f"Error in play_quest_minigame with minigame {minigame_func.__name__}: {e}")
                            available_minigames.remove(minigame_dict)
                            if not available_minigames:
                                dialogue_box.show(["NPC: All challenges failed to load. No reward this time."], context="default")
                                return False
                            minigame_dict = random.choice(available_minigames)
                            minigame_func = minigame_dict["func"]
                            requires_gender = minigame_dict["requires_gender"]
                            dialogue_box.show(["NPC: That challenge failed to load. Let's try another one. Press Y to continue, N to skip, or ESC to close."], context="default")
                            break
                elif event.key == pygame.K_n:
                    return False
                elif event.key == pygame.K_ESCAPE:
                    return False

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting play_quest_minigame...")
    return False

def final_cutscene(screen, clock, player, ui_background):
    print("Entering final_cutscene...")
    pronoun = "his" if player.gender == "male" else "her"
    lines = [
        f"Vitalik: With Skuld defeated, {player.name} stands before the restored Superseed.",
        f"Vitalik: The fragments pulse with light, merging into a radiant whole.",
        f"Vitalik: Krypto’s darkness lifts—Seisan’s chaos is balanced once more.",
        f"Vitalik: {player.name} has fulfilled {pronoun} destiny as the Sapa Slayer.",
        f"Vitalik: The ElPee rise again, and Krypto blooms under the Superseed’s glow.",
        f"Vitalik: Thank you for playing A Superseed Odyssey!"
    ]
    dialogue_box = DialogueBox()
    dialogue_box.show(lines, context="default")
    running = True

    while running and dialogue_box.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event in final_cutscene.")
                return False
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed in final_cutscene: {event.key}")
                if event.key == pygame.K_SPACE:
                    dialogue_box.next_line()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        screen.blit(ui_background, (0, 0))
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    dialogue_box.active = False
    dialogue_box.lines = []
    dialogue_box.current_line = 0
    print("Exiting final_cutscene...")
    return True