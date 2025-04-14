# A Superseed Odyssey: Rise of the Sapa Slayer

## Overview
A Superseed Odyssey: Rise of the Sapa Slayer is a 2D maze-based adventure game built with Python and Pygame. Players navigate through randomly generated mazes across six unique areas, battling enemies, collecting tokens, and gathering fragments to defeat the final boss, Skuld. The game features dynamic gameplay with infection mechanics, combat, minigames, and a narrative-driven progression.

## Features
- **Random Maze Generation**: Each playthrough features procedurally generated mazes with random entry and exit points.
- **Unique Area Themes**: Six areas with distinct visual themes, using individual floor and wall PNGs for each area (scaled to 40x40 pixels).
- **Combat System**: Melee and ranged attacks with visual effects (sprites for attacks with fallbacks).
- **Infection Mechanic**: Manage your infection level by collecting tokens, or risk game over.
- **Minigames**: Solve puzzles to progress, with random quest NPCs offering minigames for rewards.
- **Custom Sprites**: Enemies, sword, tokens, checkpoints, and fragments use custom sprites with fallbacks.
- **Soundtrack**: Separate music for cutscenes and gameplay, with sound effects for actions.
- **Pause Menu**: Access tutorial, toggle minimap, switch easy mode, restart, adjust sound, save/load game, and quit.
- **Auto-Scaling Assets**: All assets are automatically scaled to 40x40 pixels to match the game’s tile size.

## Installation

### Prerequisites
- **Python 3.8+**: Ensure Python is installed on your system.
- **Pygame**: Install Pygame using pip:
  ```bash
  pip install pygame



# Gameplay

## Controls

- Arrow Keys: Move the player.
- J: Melee attack (requires the Sword of Solvency).
- K: Ranged attack (requires the Sword of Solvency and ranged attack charges).
- E: Interact with NPCs, minigames, or the sword.
- O: Activate the Optimism Ring (if available).
- R: Load from the last checkpoint.
- Y/N: Play or skip minigames.
- P: Pause the game to access the menu (tutorial, minimap, easy mode, restart, sound, save/load, quit).
- M: Toggle the minimap.
- SPACE: Advance dialogue.
- ESC: Skip dialogue or quit from the game over screen.
- 1-9: Select options in vendor and other interactive prompts.

## Objective
- Navigate through mazes in six areas: The Slums of Krypto, Seisan Spires, Ethereum Chain Ruins, Optimism’s Echo, MEV Gang Hideout, and Skuld’s Lair.
- Collect tokens to reduce infection, reach checkpoints, and gather fragments.
- Complete optional minigames from random quest NPCs for rewards.
- Defeat the final boss, Skuld, to restore the Superseed and save Krypto.


## Fallbacks

The game includes fallbacks to ensure it runs even if assets are missing:

- If floor/wall tiles fail to load, the maze uses gray rectangles for walls.
- If sprites fail to load, colored rectangles are used (e.g., cyan for tokens, yellow for the sword).
- If sounds fail to load, the game continues without audio.

# Contributing
Fork the repository.
Create a new branch (git checkout -b feature/your-feature).
Make your changes and commit (git commit -m "Add your feature").
Push to your branch (git push origin feature/your-feature).
Open a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

# Credits
- Developer: [KRYPTOPACY]
- Assets: 
#### Built with: Python, Pygame



---




