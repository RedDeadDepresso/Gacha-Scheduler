class GameConfig:
    observers = []

    def __init__(self, name):
        self.name = name
        self.iconPath = None
        self.gamePath = None
        self.scriptPath = None

    def addNotify(self):
        for observer in self.observers:
            observer.addNotify(self)

    def removeNotify(self):
        for observer in self.observers:
            observer.removeNotify(self)