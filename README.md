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
If you use emulator instances, you should provide .lnk or .bat file that can launch the game.

.lnk files has been tested and confirmed to work with the following emulators:
- Bluestacks 5
- MuMu Player
- LDPlayer9 (through [LDPlayer-Shortcut-Creator](https://github.com/shazzaam7/LDPlayer-Shortcut-Creator))

## Installation and Usage
1. Download the latest release or clone the repository and install the required packages with the command `pip3 install -r requirements.txt`.
2. Add games by specifying their names and path and optionally an icon and script.
3. Add a time to the schedule to launch the game.
4. Remove an entry in the schedule with Right Click.
5. With the keyboard shortcut `Ctrl+Alt+H` you can hide/show Gacha-Scheduler from the system tray.
6. [OPTIONAL] [Set Gacha-Scheduler on startup](https://support.microsoft.com/en-us/windows/add-an-app-to-run-automatically-at-startup-in-windows-10-150da165-dcd9-7230-517b-cf3c295d89dd)

Please feel free to use and modify Gacha-Scheduler as you see fit. Your feedback and contributions are always welcome.

## Acknowledgment
The program is a modified version of [zhiyiYo's Fluent Gallery](https://github.com/zhiyiYo/PyQt-Fluent-Widgets).
