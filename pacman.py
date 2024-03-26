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
        self.visited = SymmetricHashMap()

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

            # blinky state
            init_gs.blinky_a = self.ghosts.blinky.node.position
            init_gs.blinky_b = self.ghosts.blinky.target.position
            init_gs.blinky_bn = self.ghosts.blinky.target
            init_gs.blinky_p = self.ghosts.blinky.position
            init_gs.blinky_s = self.ghosts.blinky.speed
            init_gs.blinky_d = self.ghosts.blinky.direction
            init_gs.blinky_dv = DIR2VEC[self.ghosts.blinky.direction]

            # score
            init_gs.visited = self.visited
            init_gs.score = 0

            # MAKE PREDICTIONS
            options = []
            predict(init_gs, options)
            # print(len(options))

            for level in range(1):
                leafs = []
                for option in options:
                    predict(option, leafs)
                options = leafs

            # print(len(options))
            # print(options)

            # find the best
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
                print(current)


            # print(current, keepTags)

            # print(init_gs.child[0].dir_tag,init_gs.child[1].dir_tag,init_gs.child[2].dir_tag)
            # remove debug by tag

            def remove_debug(gs, rm):
                if rm:
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
    for dir in init_gs.pacman_node.neighbors:
        target_node = init_gs.pacman_node.neighbors[dir]
        if target_node is not None and PACMAN in init_gs.pacman_node.access[dir]:
            # create new game_state
            gs = GameState()
            gs.level = init_gs.level + 1
            gs.dir = dir
            # gs.dir_tag = str(gs.level) + ":" + str(dir)
            gs.dir_tag = str(gs.level) + "#" + str(target_node.position.x//TILEWIDTH) + ":" + str(target_node.position.y//TILEWIDTH)


            gs.parent = init_gs
            gs.score = init_gs.score

            # blinky clone
            gs.blinky_a = init_gs.blinky_a
            gs.blinky_b = init_gs.blinky_b
            gs.blinky_bn = init_gs.blinky_bn
            gs.blinky_p = init_gs.blinky_p
            gs.blinky_s = init_gs.blinky_s
            gs.blinky_d = init_gs.blinky_d
            gs.blinky_dv = init_gs.blinky_dv

            distance = init_gs.pacman_node.position.distanceTo(target_node.position)
            delta = distance / init_gs.pacman_s
            remaining_move_time = delta
            time_to_target = gs.blinky_p.distanceTo(gs.blinky_b) / gs.blinky_s
            segment_num = 0

            # (debug) draw purple dot and line
            debug_point(target_node.position.asTuple(), (200, 0, 200), gs.dir_tag)
            debug_line(target_node.position.asTuple(), init_gs.pacman_node.position.asTuple(), (200, 0, 200), gs.dir_tag)

            while time_to_target < remaining_move_time:
                # blinky first segment
                blinky_next_point = gs.blinky_p + (gs.blinky_dv * gs.blinky_s * time_to_target)
                debug_line(gs.blinky_a.asTuple(), blinky_next_point.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                segment_num = (segment_num + 1) % 4

                # predict next direction
                remaining_move_time -= time_to_target
                best_direction = None
                best_neigh = None
                best_h = 100000000
                goal = init_gs.pacman_node.position + (
                            DIR2VEC[dir] * (delta - remaining_move_time) * init_gs.pacman_s)
                # debug_point(goal.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                for next_direction in [UP, DOWN, LEFT, RIGHT]:
                    neigh = gs.blinky_bn.neighbors[next_direction]
                    if next_direction != gs.blinky_d * -1 and neigh is not None and BLINKY in \
                            gs.blinky_bn.access[next_direction]:
                        h = (neigh.position - goal).magnitudeSquared()
                        # debug_line(goal.asTuple(), neigh.position.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                        if h < best_h:
                            best_h = h
                            best_direction = next_direction
                            best_neigh = neigh
                if not best_direction:
                    print("No blinky direction found")
                    print("this is a bug")
                    for next_direction in [UP, DOWN, LEFT, RIGHT]:
                        neigh = gs.blinky_bn.neighbors[next_direction]
                        if next_direction != gs.blinky_d * -1 and neigh is not None and PACMAN in \
                                gs.blinky_bn.access[next_direction]:
                            h = (neigh.position - goal).magnitudeSquared()
                            # debug_line(goal.asTuple(), neigh.position.asTuple(), LINE_COLORS[segment_num], tag=gs.dir_tag)
                            if h < best_h:
                                best_h = h
                                best_direction = next_direction
                                best_neigh = neigh

                # check for collision
                if gs.blinky_b == target_node.position:
                    if best_direction == dir * -1:
                        gs.score -= 1000
                    else:
                        d = goal - gs.blinky_b
                        dSquared = d.magnitudeSquared()
                        rSquared = (5 + 5) ** 2
                        if dSquared <= rSquared:
                            gs.score -= 1000

                if gs.blinky_b == init_gs.pacman_node.position:
                    d = goal - gs.blinky_b
                    dSquared = d.magnitudeSquared()
                    rSquared = (5 + 5) ** 2
                    if dSquared <= rSquared:
                        gs.score -= 1000

                # move blinky
                gs.blinky_p = gs.blinky_b
                gs.blinky_a = gs.blinky_b
                gs.blinky_bn = best_neigh
                gs.blinky_b = best_neigh.position
                gs.blinky_d = best_direction
                gs.blinky_dv = DIR2VEC[best_direction]
                time_to_target = gs.blinky_p.distanceTo(gs.blinky_b) / gs.blinky_s

            # blinky last segment
            blinky_next_point = gs.blinky_p + (gs.blinky_dv * gs.blinky_s * remaining_move_time)
            gs.blinky_p = blinky_next_point
            debug_line(gs.blinky_a.asTuple(), blinky_next_point.asTuple(), LINE_COLORS[segment_num],
                       tag=gs.dir_tag)

            # move pacman
            gs.pacman_s = init_gs.pacman_s
            gs.pacman_node = target_node

            # rate the choice
            A = init_gs.pacman_node.position.asTuple()
            B = target_node.position.asTuple()

            gs.visited = init_gs.visited.clone()
            if not gs.visited.check(A, B):
                gs.score += 10
                gs.visited.visit(A, B)

            # add to the list of options
            next_options.append(gs)

            # add as child
            init_gs.child.append(gs)
