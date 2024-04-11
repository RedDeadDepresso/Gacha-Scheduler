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
        return (h * 3600) + (m * 60) + s

    def extractArgs(self, programPath):
        # Resolve the emulator's actual executable path from a shortcut if provided
        if programPath.endswith('.lnk'):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(programPath)
            programPath = os.path.abspath(shortcut.Targetpath)
            
            # Extract command line arguments from the shortcut
            args = shortcut.Arguments
            args = args.split(" ")
            for i, arg in enumerate(args):
                if set(arg) == {'"'} or set(arg) == {"'"}:
                    args[i] = ''
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

        result = toast(self.gameName, 
              f'{self.gameName} will open in 30 seconds', 
              button='Cancel',
              icon=iconPath,
              duration='long'
              )
        return result
            
    def openProgram(self, path):
        directory = os.path.dirname(path)
        if path.endswith(".py"):
            subprocess.Popen(['python', path], shell=True, cwd=directory, creationflags=subprocess.DETACHED_PROCESS)
        else:
            path, args = self.extractArgs(path)
            subprocess.Popen([path] + args, shell=True, cwd=directory,  creationflags=subprocess.DETACHED_PROCESS)

    def run(self):
        if os.path.exists(self.gamePath):
            if cfg.toastEnabled.value and self.showToast() == {'arguments': 'http:Cancel', 'user_input': {}}:
                return 
            self.openProgram(self.gamePath)
            
        if os.path.exists(self.scriptPath):
            time.sleep(self.scriptDelay)
            self.openProgram(self.scriptPath)

        




