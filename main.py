import pygame
from env.grid_world import GridWorld
from env.sensors import MotionSensor
from pomdp.belief_update import Belief
from agents.intruder_agent import Intruder
from visualization.viewer import Viewer

env      = GridWorld()
sensor   = MotionSensor()
belief   = Belief(env.size)
intruder = Intruder()
viewer   = Viewer(env.size)

env.reset()
clock = pygame.time.Clock()

theft_score        = 0
artifact_collected = False
turn               = 0
whose_turn         = "GUARD"
last_observation   = None
last_guard_action  = "-"
intruder_goal_desc = "scanning..."
intruder_mode      = "HEIST"     # HEIST / FLEE / FLEE→EXIT / ESCAPE
threat_dist        = 999         # BFS distance guard→intruder

print("=== Cat & Mouse Museum Heist (Guard Mode) ===")
print("YOU are the GUARD  :  Arrow keys / WASD to move")
print("INTRUDER is AI     :  steals opportunistically, FLEES when you get close")
print("Intruder can escape WITHOUT the artifact if cornered!")
print("Turn sequence per keypress:")
print("  1. Guard moves       (you)")
print("  2. Intruder AI moves (flee / heist / escape)")
print("  3. Sensor fires      (motion detection)")
print("  4. Belief updates    (POMDP heatmap)")
print("==============================================")

running = True
while running:
    guard_action = None

    # ── Event pump ──────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP    or event.key == pygame.K_w:
                guard_action = "UP"
            elif event.key == pygame.K_DOWN  or event.key == pygame.K_s:
                guard_action = "DOWN"
            elif event.key == pygame.K_LEFT  or event.key == pygame.K_a:
                guard_action = "LEFT"
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                guard_action = "RIGHT"
            elif event.key == pygame.K_ESCAPE:
                running = False

    # ── One full turn triggered by guard (user) keypress ────────────
    if guard_action:
        turn += 1
        print(f"\n--- Turn {turn} ---")

        # 1. GUARD moves (user)
        whose_turn        = "GUARD"
        last_guard_action = guard_action
        env.guard = env.move(env.guard, guard_action)
        print(f"  Guard    moves {guard_action:5s} → {tuple(env.guard)}")

        # Check catch right after guard steps
        if env.guard == env.intruder:
            print(f"  [!!] Guard CAUGHT the intruder!  Theft Score: {theft_score}  -- GUARD WINS!")
            running = False

        # 2. INTRUDER moves (AI – flee / heist / escape)
        if running:
            whose_turn = "INTRUDER"
            intruder_action, intruder_goal_desc, intruder_mode, threat_dist = \
                intruder.choose_action(env.intruder, env, artifact_collected)
            env.intruder = env.move(env.intruder, intruder_action)
            ipos = tuple(env.intruder)
            print(f"  Intruder moves {intruder_action:5s} → {ipos}  "
                  f"[{intruder_mode}] goal: {intruder_goal_desc}  threat={threat_dist}")

            # Collect exhibit (opportunistic)
            if ipos in env.objects:
                env.objects.remove(ipos)
                theft_score += 10
                print(f"  [+10] Intruder grabbed exhibit!  Theft: {theft_score}")

            # Steal artifact
            if not artifact_collected and ipos == env.artifact:
                artifact_collected = True
                theft_score += 50
                print(f"  [+50] Intruder STOLE THE ARTIFACT!  Theft: {theft_score}")

            # Intruder escapes via exit — allowed with OR without artifact
            if ipos == env.exit:
                if artifact_collected:
                    theft_score += 100
                    print(f"  [+100] Intruder ESCAPED with the artifact!  "
                          f"Total Theft: {theft_score}  -- INTRUDER WINS!")
                else:
                    theft_score += 20
                    print(f"  [+20] Intruder ESCAPED safely (no artifact)!  "
                          f"Total Theft: {theft_score}  -- INTRUDER SURVIVES!")
                running = False

            # Check catch after intruder steps into guard
            if running and env.guard == env.intruder:
                print(f"  [!!] Guard CAUGHT the intruder!  Theft Score: {theft_score}  -- GUARD WINS!")
                running = False

        # 3. Sensor fires
        if running:
            last_observation = sensor.detect(env.guard, env.intruder)
            obs_str = "DETECTED" if last_observation else "clear"
            print(f"  Sensor   → {obs_str}")

            # 4. Belief update (POMDP heatmap from guard's perspective)
            belief.update(last_observation, env.guard)
            print(f"  Belief   → peak at {belief.most_likely()}")

        whose_turn = "GUARD"   # back to waiting for user

    viewer.draw(env, belief, theft_score, artifact_collected,
                turn, whose_turn, last_observation, last_guard_action,
                intruder_goal_desc, intruder_mode, threat_dist)

    clock.tick(60)

pygame.quit()