import random


class Guard:

    ACTIONS=["UP","DOWN","LEFT","RIGHT"]

    def __init__(self,belief):

        self.belief=belief


    def choose_action(self,guard_pos):

        target=self.belief.most_likely()

        dx=target[0]-guard_pos[0]
        dy=target[1]-guard_pos[1]

        if abs(dx)>abs(dy):

            return "DOWN" if dx>0 else "UP"

        else:

            return "RIGHT" if dy>0 else "LEFT"