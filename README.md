# Gacha-Scheduler
Gacha-Scheduler is an application to quickly launch and schedule gacha games along with their scripts, a software to automate the game. You can find some examples of scripts [here](https://github.com/stars/LmeSzinc/lists/awesome-nijigen-mobile-game-bots).
<p align="center">
<img width="720" alt="Screenshot 2024-09-25 211345" src="https://github.com/user-attachments/assets/efbdaf38-21e0-4b4e-ac02-d5d7077ceec4">
</p>
  
## Requirements
- Windows 10 or 11
- If you plan to run Python scripts, Python must be added to your system's PATH.

## Supported Emulators
Gacha-Scheduler should be able to launch most applications and emulators.
If you use emulator instances, you should provide a .lnk or .bat file that can launch the game.

.lnk files have been tested and confirmed to work with the following emulators:
- Bluestacks 5
- MuMu Player
- LDPlayer9 (through [LDPlayer-Shortcut-Creator](https://github.com/shazzaam7/LDPlayer-Shortcut-Creator))

## Installation and Usage
Download the latest release and extract it, then run Gacha-Scheduler.exe.

If you want to run from source code, follow these steps:
1. Clone or download this repository.
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already.
3. Run `uv sync` in the repository folder to create the virtual environment and install dependencies.
4. Run `uv run gacha_scheduler.py`.
5. Add games by specifying their names and path, and optionally an icon and script.
6. Add a time to the schedule to launch the game.
7. Remove an entry in the schedule with Right Click.
8. Use the keyboard shortcut (default `Ctrl+Alt+H`) to hide/show Gacha-Scheduler. The shortcut can be changed in Settings.
9. [OPTIONAL] [Set Gacha-Scheduler on startup](https://support.microsoft.com/en-us/windows/add-an-app-to-run-automatically-at-startup-in-windows-10-150da165-dcd9-7230-517b-cf3c295d89dd)

Please feel free to use and modify Gacha-Scheduler as you see fit. Your feedback and contributions are always welcome.

## Acknowledgment
The program is a modified version of [zhiyiYo's Fluent Gallery](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).