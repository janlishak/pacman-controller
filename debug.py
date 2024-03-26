points = {}
def debug_point(xy, color=None, tag="frame"):
    if(points.get(tag) == None):
        points[tag] = []
    points[tag].append(("point", color, xy))

def debug_line(xy1, xy2, color=None, tag="frame"):
    if(points.get(tag) == None):
        points[tag] = []
    points[tag].append(("line", color, xy1, xy2))
def debug_points():
    points_list = []
    for key in points:
        # print(points[key])
        points_list = points_list + points[key]
    return points_list

def debug_clear(tag):
    if(points.get(tag) == None):
        # print("wtf")
        return

    points[tag]=[]

def debug_clear_all():
    global points
    points = {}
def debug_use_color():
    return False

def debug_get_speed():
    return 0.1

def debug_get_fps():
    return 60