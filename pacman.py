import pygame
from pygame.locals import *

from debug import debug_point, debug_clear, debug_line, debug_clear_all
from do import DynamicObject, GameState, SymmetricHashMap
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites


class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node )
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.ghosts = None
        self.visited = None

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def update(self, dt):
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt

        if self.overshotTarget():
            # PAC-MAN AT CROSS ROAD
            self.node = self.target
            debug_clear_all()

            # PORTALS
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            init_gs = GameState()

            # pacman state
            init_gs.level = 0
            init_gs.pacman_s = self.speed
            init_gs.pacman_node = self.node
            init_gs.dir = self.direction

            # blinky state
            init_gs.g[BLINKY].a = self.ghosts.blinky.node.position
            init_gs.g[BLINKY].b = self.ghosts.blinky.target.position
            init_gs.g[BLINKY].bn = self.ghosts.blinky.target
            init_gs.g[BLINKY].p = self.ghosts.blinky.position
            init_gs.g[BLINKY].s = self.ghosts.blinky.speed
            init_gs.g[BLINKY].d = self.ghosts.blinky.direction
            init_gs.g[BLINKY].dv = DIR2VEC[self.ghosts.blinky.direction]
            init_gs.g[BLINKY].c = self.ghosts.blinky.color
            init_gs.g[BLINKY].m = self.ghosts.pinky.mode

            # pinky state
            init_gs.g[PINKY].a = self.ghosts.pinky.node.position
            init_gs.g[PINKY].b = self.ghosts.pinky.target.position
            init_gs.g[PINKY].bn = self.ghosts.pinky.target
            init_gs.g[PINKY].p = self.ghosts.pinky.position - DIR2VEC[self.ghosts.pinky.direction * -1] * 3
            init_gs.g[PINKY].s = self.ghosts.pinky.speed
            init_gs.g[PINKY].d = self.ghosts.pinky.direction
            init_gs.g[PINKY].dv = DIR2VEC[self.ghosts.pinky.direction]
            init_gs.g[PINKY].c = self.ghosts.pinky.color
            init_gs.g[PINKY].m = self.ghosts.pinky.mode

            # inky state
            init_gs.g[INKY].a = self.ghosts.pinky.node.position
            init_gs.g[INKY].b = self.ghosts.pinky.target.position
            init_gs.g[INKY].bn = self.ghosts.pinky.target
            init_gs.g[INKY].p = self.ghosts.pinky.position - DIR2VEC[self.ghosts.pinky.direction * -1] * 3
            init_gs.g[INKY].s = self.ghosts.pinky.speed
            init_gs.g[INKY].d = self.ghosts.pinky.direction
            init_gs.g[INKY].dv = DIR2VEC[self.ghosts.pinky.direction]
            init_gs.g[INKY].c = self.ghosts.pinky.color
            init_gs.g[INKY].m = self.ghosts.pinky.mode

            # clyde state
            init_gs.g[CLYDE].a = self.ghosts.pinky.node.position
            init_gs.g[CLYDE].b = self.ghosts.pinky.target.position
            init_gs.g[CLYDE].bn = self.ghosts.pinky.target
            init_gs.g[CLYDE].p = self.ghosts.pinky.position - DIR2VEC[self.ghosts.pinky.direction * -1] * 3
            init_gs.g[CLYDE].s = self.ghosts.pinky.speed
            init_gs.g[CLYDE].d = self.ghosts.pinky.direction
            init_gs.g[CLYDE].dv = DIR2VEC[self.ghosts.pinky.direction]
            init_gs.g[CLYDE].c = self.ghosts.pinky.color
            init_gs.g[CLYDE].m = self.ghosts.pinky.mode

            # score
            init_gs.visited = self.visited
            init_gs.score = 0

            # MAKE PREDICTIONS
            options = []
            predict(init_gs, options)
            # print(len(options))

            overthink = 6
            for level in range(overthink):
                leafs = []
                for option in options:
                    predict(option, leafs)
                options = leafs

            # print(len(options))
            # print(options)

            # find the best
            if len(options) > 0:
                best_option = options[-1]
                index = len(options) - 1
                while index >= 0:
                    if best_option.score < options[index].score:
                        best_option = options[index]
                    index -= 1

                # back track
                # print(best_option.dir_tag)
                keepTags = [best_option.dir_tag]
                current = best_option
                print("turn:")
                print(best_option)
                while current.level > 1:
                    current = current.parent
                    keepTags.append(current.dir_tag)
                    # print(current)

                print(current)
                # print(current, keepTags)

                # print(init_gs.child[0].dir_tag,init_gs.child[1].dir_tag,init_gs.child[2].dir_tag)
                # remove debug by tag

                # print("considered: ")
                def remove_debug(gs, rm):
                    if rm:
                        # print(gs)
                        debug_clear(gs.dir_tag)
                    if gs.child is not None:
                        for child in gs.child:
                            if child.dir_tag not in keepTags:
                                remove_debug(child, True)
                            else:
                                remove_debug(child, False)
                remove_debug(init_gs, True)
                # print()

                # debug_point((16,64), (92,242,53), "df")


            # CHOOSE
            direction = current.dir
            self.visited = current.visited
            # print(current.pacman_node.position)

            # set new target_node
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()


        else:
            # PAC-MAN BETWEEN CROSSROADS
            direction = self.getValidKey()
            if self.oppositeDirection(direction):
                self.reverseDirection()


def predict(init_gs, next_options):
    if init_gs.score < -1500:
        # print("yeah, no thanks")
        return
    for dir in init_gs.pacman_node.neighbors:
        target_node = init_gs.pacman_node.neighbors[dir]
        # if target_node is not None and PACMAN in init_gs.pacman_node.access[dir] and init_gs.dir * -1 is not dir:
        if target_node is not None and PACMAN in init_gs.pacman_node.access[dir]:

            # create new game_state
            gs = GameState()
            gs.level = init_gs.level + 1
            gs.dir = dir
            gs.dir_tag = str(gs.level) + "#" + str(target_node.position.x//TILEWIDTH) + ":" + str(target_node.position.y//TILEWIDTH) + str(hash(gs))
            gs.parent = init_gs
            gs.score = init_gs.score

            # state reusable
            distance = init_gs.pacman_node.position.distanceTo(target_node.position)
            delta = distance / init_gs.pacman_s

            # (debug) draw purple dot and line
            debug_point(target_node.position.asTuple(), (200, 0, 200), gs.dir_tag)
            debug_line(target_node.position.asTuple(), init_gs.pacman_node.position.asTuple(), (200, 0, 200), gs.dir_tag)

            ##### ##### ##### GHOST n STUFF ##### ##### #####
            should_skip = False
            for ghost in [BLINKY, PINKY, INKY, CLYDE]:

                # ghost clone
                gs.g[ghost].a = init_gs.g[ghost].a
                gs.g[ghost].b = init_gs.g[ghost].b
                gs.g[ghost].bn = init_gs.g[ghost].bn
                gs.g[ghost].p = init_gs.g[ghost].p
                gs.g[ghost].s = init_gs.g[ghost].s
                gs.g[ghost].d = init_gs.g[ghost].d
                gs.g[ghost].dv = init_gs.g[ghost].dv
                gs.g[ghost].c = init_gs.g[ghost].c
                gs.g[ghost].m = init_gs.g[ghost].m
                LINE_COLORS = [gs.g[ghost].c]
                # LINE_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255),(255, 0, 255)]


                # if pacman has power pill
                if gs.g[ghost].m.current not in [SCATTER, CHASE]:
                    continue

                # check for obvious collision
                if target_node.position == gs.g[ghost].a:
                    if gs.g[ghost].d == dir * -1:
                        should_skip = True
                        break
                    else:
                        gs.score -= 300

                if target_node.position == gs.g[ghost].b:
                    gs.score -= 300

                remaining_move_time = delta
                time_to_target = gs.g[ghost].p.distanceTo(gs.g[ghost].b) / gs.g[ghost].s
                segment_num = 0

                dbg_count = 0
                while time_to_target <= remaining_move_time:
                    dbg_count += 1
                    if dbg_count > 10:
                        break
                    # ghost first segment

                    ghost_next_point = gs.g[ghost].p + (gs.g[ghost].dv * gs.g[ghost].s * time_to_target)
                    debug_line(gs.g[ghost].a.asTuple(), ghost_next_point.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                    segment_num = (segment_num + 1) % len(LINE_COLORS)
    
                    # predict next direction
                    remaining_move_time -= time_to_target
                    best_direction = None
                    best_neigh = None
                    best_h = 100000000


                    # pacman as goal
                    goal = init_gs.pacman_node.position + (DIR2VEC[dir] * (delta - remaining_move_time) * init_gs.pacman_s)

                    # pinky goal
                    if ghost == PINKY:
                        goal = init_gs.pacman_node.position + (DIR2VEC[dir] * (delta - remaining_move_time) * init_gs.pacman_s) + (DIR2VEC[dir] * TILEWIDTH * 4)

                    debug_point(goal.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                    for next_direction in [UP, DOWN, LEFT, RIGHT]:
                        neigh = gs.g[ghost].bn.neighbors[next_direction]
                        if next_direction != gs.g[ghost].d * -1 and neigh is not None and ghost in \
                                gs.g[ghost].bn.access[next_direction]:
                            h = (neigh.position - goal).magnitudeSquared()
                            # if ghost is []:
                            #     debug_line(goal.asTuple(), neigh.position.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                            if h < best_h:
                                best_h = h
                                best_direction = next_direction
                                best_neigh = neigh

                    if not best_direction:
                        continue
                        print("No ghost direction found")
                        for next_direction in [UP, DOWN, LEFT, RIGHT]:
                            neigh = gs.g[ghost].bn.neighbors[next_direction]
                            if next_direction != gs.g[ghost].d * -1 and neigh is not None and PACMAN in \
                                    gs.g[ghost].bn.access[next_direction]:
                                h = (neigh.position - goal).magnitudeSquared()
                                # debug_line(goal.asTuple(), neigh.position.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                                if h < best_h:
                                    best_h = h
                                    best_direction = next_direction
                                    best_neigh = neigh

                    # move ghost
                    gs.g[ghost].p = gs.g[ghost].b
                    gs.g[ghost].a = gs.g[ghost].b
                    gs.g[ghost].bn = best_neigh
                    gs.g[ghost].b = best_neigh.position
                    gs.g[ghost].d = best_direction
                    gs.g[ghost].dv = DIR2VEC[best_direction]
                    time_to_target = gs.g[ghost].p.distanceTo(gs.g[ghost].b) / gs.g[ghost].s

                    # check for collision
                    gs.dbg += f" [{GHOST2NAME[ghost]}]"
                    if gs.g[ghost].b == init_gs.pacman_node.position:
                        if best_direction == dir * -1:
                            gs.dbg += f" face"
                            gs.score -= 1000
                        else:
                            d = goal - gs.g[ghost].b
                            dSquared = d.magnitudeSquared()
                            rSquared = (15) ** 2
                            if dSquared <= rSquared:
                                gs.dbg += " catch"
                                gs.score -= 1000
                            else:
                                gs.dbg += " ok"
    
                # ghost last segment
                ghost_next_point = gs.g[ghost].p + (gs.g[ghost].dv * gs.g[ghost].s * remaining_move_time)
                gs.g[ghost].p = ghost_next_point
                debug_line(gs.g[ghost].a.asTuple(), ghost_next_point.asTuple(), LINE_COLORS[segment_num],
                           tag=gs.dir_tag)

            if should_skip:
                continue

            ##### ##### ##### GHOST n STUFF ##### ##### #####

            # move pacman
            gs.pacman_s = init_gs.pacman_s
            gs.pacman_node = target_node

            # rate the choice
            A = init_gs.pacman_node.position.asTuple()
            B = target_node.position.asTuple()

            if gs.parent and gs.parent.dir:
                if gs.parent.dir * -1 == dir:
                    gs.score -= 1


            gs.visited = init_gs.visited.clone()
            if not gs.visited.check(A, B):
                gs.score += 100/gs.level
                gs.visited.visit(A, B)

            # add to the list of options
            next_options.append(gs)

            # add as child
            init_gs.child.append(gs)
