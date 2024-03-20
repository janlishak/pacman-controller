points = []
def debug_ping(x, color=None):
    points.append((x, color))
def debug_points():
    return points

def debug_clear():
    points.clear()
def debug_use_color():
    return False

def debug_get_speed():
    return 1

def debug_get_fps():
    return 60