class GameConfig:
    observers = []

    def __init__(self, name, iconPath, gamePath, scriptPath):
        self.name = name
        self.iconPath = None
        self.gamePath = None
        self.scriptPath = None

    def addNotify(self):
        for observer in self.observers:
            observer.addGame(self)

    def removeNotify(self):
        for observer in self.observers:
            observer.removeGame(self)