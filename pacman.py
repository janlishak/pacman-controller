import pygame
from pygame.locals import *

from debug import debug_point, debug_clear, debug_line
from do import DynamicObject, GameState
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
            debug_clear(self.direction)

            # PORTALS
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            init_gs = GameState()

            # pacman state
            init_gs.pacman_s = self.speed
            init_gs.pacman_node = self.node

            # blinky state
            init_gs.blinky_a = self.ghosts.blinky.node.position
            init_gs.blinky_b = self.ghosts.blinky.target.position
            init_gs.blinky_bn = self.ghosts.blinky.target
            init_gs.blinky_p = self.ghosts.blinky.position
            init_gs.blinky_s = self.ghosts.blinky.speed
            init_gs.blinky_dv = DIR2VEC[self.ghosts.blinky.direction]
            init_gs.blinky_d = self.ghosts.blinky.direction

            # init_gs -->
            next_options = []
            predict(init_gs, next_options)

            print(next_options)



            # finally, set the direction
            direction = self.getValidKey()

            # set new target_node
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()

            # clear other tags
            for dd in self.directions:
                if dd != self.direction:
                    debug_clear(dd)
        else:
            # PAC-MAN BETWEEN CROSSROADS
            direction = self.getValidKey()
            if self.oppositeDirection(direction):
                self.reverseDirection()


def predict(init_gs, next_options):
    for dir in init_gs.pacman_node.neighbors:
        target_node = init_gs.pacman_node.neighbors[dir]
        if target_node is not None:
            # (debug) draw purple dot and line
            dir_tag = dir
            debug_point(target_node.position.asTuple(), (200, 0, 200), dir_tag)
            debug_line(target_node.position.asTuple(), init_gs.pacman_node.position.asTuple(),
                       (200, 0, 200), dir_tag)

            # create new game_state
            gs = GameState()

            # blinky clone
            gs.blinky_a = init_gs.blinky_a
            gs.blinky_b = init_gs.blinky_b
            gs.blinky_bn = init_gs.blinky_bn
            gs.blinky_p = init_gs.blinky_p
            gs.blinky_s = init_gs.blinky_s
            gs.blinky_d = init_gs.blinky_dv
            gs.blinky_dn = init_gs.blinky_d

            distance = init_gs.pacman_node.position.distanceTo(target_node.position)
            delta = distance / init_gs.pacman_s
            remaining_move_time = delta
            time_to_target = gs.blinky_p.distanceTo(gs.blinky_b) / gs.blinky_s
            segment_num = 0

            while time_to_target < remaining_move_time:
                # blinky first segment
                blinky_next_point = gs.blinky_p + (gs.blinky_d * gs.blinky_s * time_to_target)
                debug_line(gs.blinky_a.asTuple(), blinky_next_point.asTuple(), LINE_COLORS[segment_num],
                           tag=dir_tag)
                segment_num = (segment_num + 1) % 4

                # predict next direction
                remaining_move_time -= time_to_target
                best_direction = None
                best_neigh = None
                best_h = 100000000
                goal = init_gs.pacman_node.position + (
                            DIR2VEC[dir] * (delta - remaining_move_time) * init_gs.pacman_s)
                debug_point(goal.asTuple(), LINE_COLORS[segment_num], tag=dir_tag)
                for next_direction in [UP, DOWN, LEFT, RIGHT]:
                    neigh = gs.blinky_bn.neighbors[next_direction]
                    if next_direction != gs.blinky_dn * -1 and neigh is not None and BLINKY in \
                            gs.blinky_bn.access[next_direction]:
                        h = (neigh.position - goal).magnitudeSquared()
                        # debug_line(goal.asTuple(), neigh.position.asTuple(), LINE_COLORS[segment_num], tag=dir_tag)
                        if h < best_h:
                            best_h = h
                            best_direction = next_direction
                            best_neigh = neigh

                # move blinky
                gs.blinky_p = gs.blinky_b
                gs.blinky_a = gs.blinky_b
                gs.blinky_bn = best_neigh
                gs.blinky_b = best_neigh.position
                gs.blinky_dn = best_direction
                gs.blinky_d = DIR2VEC[best_direction]
                time_to_target = gs.blinky_p.distanceTo(gs.blinky_b) / gs.blinky_s

            # blinky last segment
            blinky_next_point = gs.blinky_p + (gs.blinky_d * gs.blinky_s * remaining_move_time)
            debug_line(gs.blinky_a.asTuple(), blinky_next_point.asTuple(), LINE_COLORS[segment_num],
                       tag=dir_tag)

            # move pacman
            gs.pacman_s = init_gs.pacman_s
            gs.pacman_node = target_node

            next_options.append(gs)
