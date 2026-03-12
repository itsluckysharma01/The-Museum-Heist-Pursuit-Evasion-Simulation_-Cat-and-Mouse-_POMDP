import numpy as np

class GridWorld:

    ACTIONS = ["UP","DOWN","LEFT","RIGHT"]

    def __init__(self, size=10):

        self.size = size

        self.artifact = (8,8)
        self.exit = (0,9)

        self.reset()


    def reset(self):

        self.guard = [0,0]
        self.intruder = [9,9]

        return self.get_state()


    def get_state(self):

        return {
            "guard": self.guard,
            "intruder": self.intruder,
            "artifact": self.artifact,
            "exit": self.exit
        }


    def move(self,pos,action):

        x,y = pos

        if action=="UP":
            x-=1

        elif action=="DOWN":
            x+=1

        elif action=="LEFT":
            y-=1

        elif action=="RIGHT":
            y+=1

        x=max(0,min(self.size-1,x))
        y=max(0,min(self.size-1,y))

        return [x,y]