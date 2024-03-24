import pygame
from pygame.locals import *

from debug import debug_ping, debug_clear
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
            debug_clear('cross')

            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]

            option = DynamicObject()
            option.xy = self.target.position.asTuple()
            option.options = []
            dc = 0
            for dir in self.node.neighbors:
                dc+=1
                # if dc==2:
                #     break
                if dir == -1 * self.direction:
                    continue
                node = self.node.neighbors[dir]
                if node is not None:

                    # next option
                    debug_ping(node.position.asTuple(), (200, 0, 200), "cross")
                    next_option = DynamicObject()
                    next_option.xy = node.position.asTuple()
                    next_option.weight = node.position.distanceTo(self.target.position)
                    next_option.delta = next_option.weight/self.speed
                    # print(next_option.delta)

                    # blinky
                    blinky = self.ghosts.blinky
                    fblinky = {"a": blinky.node.position, "b": blinky.target.position,
                               "p": blinky.position + blinky.directions[
                                   blinky.direction] * blinky.speed * next_option.delta}
                    debug_ping(fblinky["p"].asTuple(), (0, 200, 0), "cross")

                    # check for over shooting
                    # vec1 = fblinky["a"] - fblinky["b"]
                    # vec2 = fblinky["p"] - fblinky["a"]
                    # node2Target = vec1.magnitudeSquared()
                    # node2Self = vec2.magnitudeSquared()
                    time_to_target = fblinky["p"].distanceTo(fblinky["b"])/blinky.speed
                    print(time_to_target, next_option.delta)
                    time_diff = next_option.delta - time_to_target
                    if time_diff<0:
                        print("done")
                    else:
                        fblinky["a"] = fblinky["b"]
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






                    option.options.append(next_option)

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
