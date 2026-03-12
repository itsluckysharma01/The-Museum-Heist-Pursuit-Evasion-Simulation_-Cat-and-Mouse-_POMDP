import pygame
import numpy as np

CELL=60


class Viewer:

    def __init__(self,size):

        pygame.init()

        self.size=size

        self.screen=pygame.display.set_mode((size*CELL,size*CELL))


    def draw(self,env,belief):

        self.screen.fill((30,30,30))

        for x in range(self.size):

            for y in range(self.size):

                prob=belief.map[x][y]

                color=(255*prob,0,0)

                rect=pygame.Rect(y*CELL,x*CELL,CELL,CELL)

                pygame.draw.rect(self.screen,color,rect)

                pygame.draw.rect(self.screen,(50,50,50),rect,1)


        gx,gy=env.guard
        ix,iy=env.intruder

        pygame.draw.rect(self.screen,(0,0,255),(gy*CELL,gx*CELL,CELL,CELL))

        pygame.draw.rect(self.screen,(255,0,0),(iy*CELL,ix*CELL,CELL,CELL))

        pygame.display.update()