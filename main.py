import time

from env.grid import GridWorld
from env.sensors import MotionSensor

from pomdp.belief import Belief

from agents.guard import Guard
from agents.intruder import Intruder

from visualization.viewer import Viewer


env=GridWorld()

sensor=MotionSensor()

belief=Belief(env.size)

guard=Guard(belief)

intruder=Intruder()

viewer=Viewer(env.size)

env.reset()

for step in range(200):

    guard_action=guard.choose_action(env.guard)

    intruder_action=intruder.choose_action()

    env.guard=env.move(env.guard,guard_action)

    env.intruder=env.move(env.intruder,intruder_action)

    observation=sensor.detect(env.guard,env.intruder)

    belief.update(observation)

    viewer.draw(env,belief)

    if env.guard==env.intruder:

        print("Guard caught intruder")

        break

    time.sleep(0.2)