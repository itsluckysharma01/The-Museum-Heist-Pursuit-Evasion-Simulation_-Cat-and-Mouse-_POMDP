import pygame
from env.grid_world import GridWorld
from env.sensors import MotionSensor
from pomdp.belief_update import Belief
from agents.guard_agent import Guard
from visualization.viewer import Viewer

env = GridWorld()
sensor = MotionSensor()
belief = Belief(env.size)
guard = Guard(belief)
viewer = Viewer(env.size)

env.reset()
clock = pygame.time.Clock()

score             = 0
artifact_collected = False
turn              = 0          # counts completed full turns
whose_turn        = "INTRUDER" # intruder always goes first each turn
last_observation  = None       # last sensor reading
last_guard_action = "-"

print("=== Cat & Mouse Museum Heist (Turn-Based) ===")
print("Each WASD keypress = one full turn:")
print("  1. Intruder moves  (you)")
print("  2. Guard responds  (AI, belief-based)")
print("  3. Sensor fires    (motion detection)")
print("  4. Belief updates  (POMDP)")
print("Collect OBJ +10 | Steal ART +50 | Escape +100")
print("=============================================")

running = True
while running:
    intruder_action = None

    # ── Event pump ───────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                intruder_action = "UP"
            elif event.key == pygame.K_s:
                intruder_action = "DOWN"
            elif event.key == pygame.K_a:
                intruder_action = "LEFT"
            elif event.key == pygame.K_d:
                intruder_action = "RIGHT"
            elif event.key == pygame.K_ESCAPE:
                running = False

    # ── Process one full turn when intruder presses a key ────────────
    if intruder_action:
        turn += 1
        print(f"\n--- Turn {turn} ---")

        # 1. INTRUDER moves
        whose_turn = "INTRUDER"
        env.intruder = env.move(env.intruder, intruder_action)
        pos = tuple(env.intruder)
        print(f"  Intruder moves {intruder_action:5s} → {pos}")

        if pos in env.objects:
            env.objects.remove(pos)
            score += 10
            print(f"  [+10] Exhibit collected!  Score: {score}")

        if not artifact_collected and pos == env.artifact:
            artifact_collected = True
            score += 50
            print(f"  [+50] ARTIFACT STOLEN!    Score: {score}")

        if pos == env.exit:
            if artifact_collected:
                score += 100
                print(f"  [+100] Intruder ESCAPED!  Final Score: {score}  -- INTRUDER WINS!")
                running = False
            else:
                print("  [!] Reached exit without the artifact — keep heisting!")

        # 2. GUARD moves (AI)
        whose_turn = "GUARD"
        last_guard_action = guard.choose_action(env.guard, env)
        env.guard = env.move(env.guard, last_guard_action)
        print(f"  Guard   moves {last_guard_action:5s} → {tuple(env.guard)}  "
              f"(targeting belief peak {belief.most_likely()})")

        # 3. Sensor fires
        last_observation = sensor.detect(env.guard, env.intruder)
        obs_str = "DETECTED" if last_observation else "clear"
        print(f"  Sensor  → {obs_str}")

        # 4. Belief update
        belief.update(last_observation, env.guard)
        print(f"  Belief  → peak at {belief.most_likely()}")

        whose_turn = "INTRUDER"  # next waiting state

        # Check catch after guard moved
        if env.guard == env.intruder:
            print(f"  [!!] Guard CAUGHT the intruder!  Final Score: {score}  -- GUARD WINS!")
            running = False

    viewer.draw(env, belief, score, artifact_collected,
                turn, whose_turn, last_observation, last_guard_action)

    clock.tick(60)

pygame.quit()