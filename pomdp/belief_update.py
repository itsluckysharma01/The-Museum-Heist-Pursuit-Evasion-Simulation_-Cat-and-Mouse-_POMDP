import numpy as np


class Belief:

    def __init__(self,size):

        self.size=size

        self.map=np.ones((size,size))

        self.map/=self.map.sum()


    def update(self,observation):

        if observation:

            self.map*=1.3

        else:

            self.map*=0.8

        self.map/=self.map.sum()


    def most_likely(self):

        idx=np.argmax(self.map)

        x=idx//self.size
        y=idx%self.size

        return [x,y]