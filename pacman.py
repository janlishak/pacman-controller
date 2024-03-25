import pygame
from pygame.locals import *

from debug import debug_point, debug_clear, debug_line
from do import DynamicObject
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

    def update(self, dt):
        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt

        if self.overshotTarget():
            # print("decision point")
            # clear debug
            debug_clear('up')

            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            option = DynamicObject()
            option.xy = self.target.position.asTuple()
            option.options = []
            dc = 0
            for dir in self.node.neighbors:
                dc+=1
                if dc==2:
                    break
                # if dir == -1 * self.direction:
                #     continue
                node = self.node.neighbors[dir]
                if node is not None:
                    # next option
                    debug_point(node.position.asTuple(), (200, 0, 200), "cross")
                    debug_line(node.position.asTuple(), option.xy, (200, 0, 200), "cross")

                    next_option = DynamicObject()
                    next_option.xy = node.position.asTuple()
                    next_option.weight = node.position.distanceTo(self.target.position)
                    next_option.delta = next_option.weight/self.speed
                    # print(next_option.delta)

                    # blinky
                    blinky = self.ghosts.blinky
                    blnk = {
                        "a": blinky.node.position,
                        "b": blinky.target.position,
                        "bn": blinky.target,
                        "p": blinky.position,
                        "s": blinky.speed,
                        "d": blinky.directions[blinky.direction],
                        "dn": blinky.direction,
                        "q": "hunt"
                    }

                    # print(blnk)

                    # debug_point(blnk["p"].asTuple(), (0, 200, 0), "cross")

                    # check for over shooting
                    # vec1 = blnk["a"] - blnk["b"]
                    # vec2 = blnk["p"] - blnk["a"]
                    # node2Target = vec1.magnitudeSquared()
                    # node2Self = vec2.magnitudeSquared()
                    # time_to_target = blnk["p"].distanceTo(blnk["b"])/blinky.speed

                    remaining_move_time = next_option.delta
                    time_to_target = blnk["p"].distanceTo(blnk["b"]) / blnk["s"]
                    part_count = 0
                    colors = [RED, GREEN, TEAL, WHITE]
                    while time_to_target < remaining_move_time:
                        # this
                        blinky_next_point = blnk["p"] + (blnk["d"] * blnk["s"] * time_to_target)
                        debug_line(blnk["a"].asTuple(), blinky_next_point.asTuple(), colors[part_count], tag="cross")
                        part_count = (part_count+1)%4

                        # predict next
                        remaining_move_time -= time_to_target
                        best_direction = None
                        best_neigh = None
                        best_h = 100000000
                        print(next_option.delta-remaining_move_time)
                        # wrong
                        goal = self.node.position + (blinky.directions[dir] * (next_option.delta-remaining_move_time) * self.speed)
                        debug_point(goal.asTuple(), colors[part_count], tag="cross")
                        for next_direction in [UP, DOWN, LEFT, RIGHT]:
                            neigh = blnk["bn"].neighbors[next_direction]
                            if next_direction != blnk["dn"] * -1 and neigh is not None and neigh.access[next_direction]:
                                vec = (blnk["p"] - goal)
                                h = vec.magnitudeSquared()
                                if h<best_h:
                                    best_h = h
                                    best_direction = next_direction
                                    best_neigh = neigh
                        blnk["p"] = blnk["b"]
                        blnk["a"] = blnk["b"]
                        blnk["bn"] = best_neigh
                        blnk["b"] = best_neigh.position
                        blnk["dn"] = best_direction
                        blnk["d"] = blinky.directions[best_direction]
                        time_to_target = blnk["p"].distanceTo(blnk["b"]) / blnk["s"]
                    # last
                    blinky_next_point = blnk["p"] + (blnk["d"] * blnk["s"] * remaining_move_time)
                    debug_line(blnk["a"].asTuple(), blinky_next_point.asTuple(), colors[part_count], tag="cross")
                    part_count = (part_count+1)%4
                        # print("k")
                        #     print(blnk["bn"])
                        #     if blnk["bn"].neighbors[next_direction] is not None:
                        #         print(next_direction)
                                # if key != self.direction * -1 or direction is not STOP or self.name in self.node.access[direction]
                        # blnk["d"] = blnk["d"] #to change
                        # blnk["b"] = 0
                        # time_to_target = blnk["p"].distanceTo(blnk["b"]) / blnk["s"]

                    # print(time_to_target, next_option.delta, time_to_target<next_option.delta)
                    # time_diff = next_option.delta - time_to_target
                    # if time_diff<0:
                    #     print("done")
                    # else:
                    #     blnk["a"] = blnk["b"]
                        # directions = blinky.validDirections()
                        # direction = self.directionMethod(directions)
                        # if not self.disablePortal:
                        #     if self.node.neighbors[PORTAL] is not None:
                        #         self.node = self.node.neighbors[PORTAL]
                        # self.target = self.getNewTarget(direction)
                        # if self.target is not self.node:
                        #     self.direction = direction
                        # else:
                        #     self.target = self.getNewTarget(self.direction)
                        #
                        # self.setPosition()



                    # second check
                    # if(node2Self >= node2Target):
                    # option.options.append(next_option)

            # print(self.ghosts)
            # print(self.ghosts.blinky.)
            direction = self.getValidKey()
            self.target = self.getNewTarget(direction)

            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            # print("elsewhere")
            direction = self.getValidKey()
            if self.oppositeDirection(direction):
                self.reverseDirection()

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
