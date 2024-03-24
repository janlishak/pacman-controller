points = {}
def debug_ping(x, color=None, tag="frame"):
    if(points.get(tag) == None):
        points[tag] = []
    points[tag].append((x, color))
def debug_points():
    points_list = []
    for key in points:
        # print(points[key])
        points_list = points_list + points[key]
    return points_list

def debug_clear(tag):
    if(points.get(tag) == None):
        print("wtf")
        return

    points[tag]=[]
def debug_use_color():
    return False

def debug_get_speed():
    return 1

def debug_get_fps():
    return 60