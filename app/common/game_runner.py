import ctypes
import os
import subprocess
import pythoncom
import psutil
import time
import win32com.client

from ..common.config import cfg
from PySide6.QtCore import QRunnable, Slot
from win11toast import toast


class GameRunner(QRunnable):
    def __init__(self, gameConfig):
        super().__init__()
        self.gameConfig = gameConfig

    @property
    def gameName(self):
        return self.gameConfig.name
    
    @property
    def gamePath(self):
        return self.gameConfig.gamePath.value
    
    @property
    def iconPath(self):
        return self.gameConfig.iconPath.value
    
    @property
    def scriptPath(self):
        return self.gameConfig.scriptPath.value

    @property
    def scriptDelay(self):
        h, m, s = map(int, cfg.scriptDelay.value.split(':'))
        return (h * 3600000) + (m * 60000) + (s * 1000)

    def extractArgs(self, programPath):
        # Resolve the emulator's actual executable path from a shortcut if provided
        if programPath.endswith('.lnk'):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(programPath)
            programPath = os.path.abspath(shortcut.Targetpath)
            
            # Extract command line arguments from the shortcut
            args = shortcut.Arguments
            args = args.split(" ")
            if args == [""]:
                args = []
        else:
            # No .lnk file, so there are no additional arguments
            args = []
        
        return programPath, args
    
    def showToast(self):
        if os.path.exists(self.iconPath):
            iconPath = self.iconPath
        else:
            iconPath = None

        toast(self.gameName, 
              f'{self.gameName} will open in 30 seconds', 
              icon=iconPath)
    
    def showMessageBox(self):
        # Display a single confirmation dialog for all programs
        confirmation = ctypes.windll.user32.MessageBoxW(
            0, f"Do you want to run {self.gameConfig.name}?", 
            "Confirmation", 4)  # 4 means Yes/No

        if confirmation != 6:  # 6 corresponds to "Yes" button
            return False
        else: 
            return True
        
    def openProgram(self, path):
        if path.endswith(".py"):
            subprocess.Popen(['python', path], shell=True)
        else:
            path, args = self.extractArgs(path)
            subprocess.Popen([path] + args, shell=True)

    def run(self):
        if os.path.exists(self.gamePath):
            if cfg.toastEnabled.value:
                self.showToast()
                time.sleep(30)

            if cfg.messageBoxEnabled.value and not self.showMessageBox():
                return
            
            self.openProgram(self.gamePath)
            
        if os.path.exists(self.scriptPath):
            time.sleep(self.scriptDelay)
            self.openProgram(self.scriptPath)

        




