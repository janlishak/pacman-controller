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
        # state
        self.level = None
        self.dir = None
        self.dir_tag = None
        self.child = []
        self.parent = None

        # pacman
        self.pacman_s = None
        self.pacman_node = None

        # blinky
        self.blinky_a = None
        self.blinky_b = None
        self.blinky_bn = None
        self.blinky_p = None
        self.blinky_s = None
        self.blinky_dv = None
        self.blinky_d = None

        # score
        self.score = None
        self.visited = None

    def __str__(self):
        return f"Level: {self.level}, Direction: {self.dir}, Score: {self.score}"


class SymmetricHashMap:
    def __init__(self):
        self.map = {}

    def normalize_key(self, vertex_a, vertex_b):
        return tuple(sorted((vertex_a, vertex_b)))

    def visit(self, vertex_a, vertex_b):
        key = self.normalize_key(vertex_a, vertex_b)
        self.map[key] = True

    def check(self, vertex_a, vertex_b):
        key = self.normalize_key(vertex_a, vertex_b)
        return self.map.get(key, False)

    def clone(self):
        copy_map = SymmetricHashMap()
        copy_map.map = self.map.copy()
        return copy_map