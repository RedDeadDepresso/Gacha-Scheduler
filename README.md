# Gacha-Scheduler
Gacha-Scheduler is an application to quickly launch and schedule gacha games along with their scripts, a software to automate the game.

You can find some examples [here](https://github.com/stars/LmeSzinc/lists/awesome-nijigen-mobile-game-bots).

<img width="715" alt="Screenshot 2024-04-03 014048" src="https://github.com/RedDeadDepresso/Gacha-Scheduler/assets/94017243/57f1f777-dae3-49ba-a32d-eba9aefeada9">

## Table of Contents
- [Requirements](#requirements)
- [Supported Emulators](#supported-emulators)
- [Installation and Usage](#installation-and-usage)
- [Acknowledgment](#acknowledgment)
  
## Requirements
- Windows 10 or 11
- If you plan to run Python scripts, Python must be added to your system's PATH.

## Supported Emulators
Gacha-Scheduler should be able to launch most applications and emulators.
If you use emulator instances, you should provide .lnk or .bat file that can launch the game.

.lnk files has been tested and confirmed to work with the following emulators:
- Bluestacks 5
- MuMu Player
- LDPlayer9 (through [LDPlayer-Shortcut-Creator](https://github.com/shazzaam7/LDPlayer-Shortcut-Creator))

## Installation and Usage
1. Download the latest release or clone the repository and install the required packages with the command `pip3 install -r requirements.txt`.
2. Add games by specifying their names and path and optionally an icon and script.
3. Add a time to the schedule to launch the game.
4. With the keyboard shortcut `Ctrl+Alt+H` you can hide/show Gacha-Scheduler from the system tray.

Please feel free to use and modify Gacha-Scheduler as you see fit. Your feedback and contributions are always welcome.

## Acknowledgment
The program is a modified version of [zhiyiYo's Fluent Gallery](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).
