class DynamicObject:
    def __init__(self):
        pass

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self.__dict__[name] = value

class GameState:
    def __init__(self):
        self.next = None