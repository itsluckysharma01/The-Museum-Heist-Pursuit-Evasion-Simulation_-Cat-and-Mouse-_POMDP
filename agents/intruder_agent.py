import random


class Intruder:

    ACTIONS=["UP","DOWN","LEFT","RIGHT"]

    def choose_action(self):

        return random.choice(self.ACTIONS)