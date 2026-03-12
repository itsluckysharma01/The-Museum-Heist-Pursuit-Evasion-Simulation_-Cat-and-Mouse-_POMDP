import random

class MotionSensor:

    def __init__(self,fp=0.1,fn=0.2):

        self.fp=fp
        self.fn=fn


    def detect(self,guard,intruder):

        if guard==intruder:

            if random.random()<self.fn:
                return False

            return True

        else:

            if random.random()<self.fp:
                return True

            return False