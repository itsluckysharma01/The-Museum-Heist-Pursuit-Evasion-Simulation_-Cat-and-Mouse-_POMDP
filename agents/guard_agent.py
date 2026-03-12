import random
from collections import deque


class Guard:

    ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
    _DELTA  = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    def __init__(self, belief):
        self.belief = belief

    def choose_action(self, guard_pos, env):
        """
        BFS to belief peak — guaranteed minimum-step path through the real grid.
        Falls back to random exploration when guard is already at the peak.
        """
        target = self.belief.most_likely(exclude=tuple(guard_pos))

        action = self._bfs(guard_pos, target, env)
        return action

    # ── BFS shortest-path planner ─────────────────────────────────────
    def _bfs(self, start, goal, env):
        start = tuple(start)
        goal  = tuple(goal)

        if start == goal:
            # Already at peak — explore toward grid centre to find intruder
            cx, cy = env.size // 2, env.size // 2
            dx, dy = cx - start[0], cy - start[1]
            if abs(dx) >= abs(dy):
                return "DOWN" if dx > 0 else "UP"
            return "RIGHT" if dy > 0 else "LEFT"

        queue   = deque([(start, None)])  # (position, first_action_taken)
        visited = {start}

        while queue:
            pos, first_action = queue.popleft()

            for action, (dx, dy) in self._DELTA.items():
                nx = max(0, min(env.size - 1, pos[0] + dx))
                ny = max(0, min(env.size - 1, pos[1] + dy))
                npos = (nx, ny)

                # Wall blocks; doors are passable
                if npos in env.walls:
                    continue
                if npos in visited:
                    continue

                taken = first_action if first_action is not None else action

                if npos == goal:
                    return taken          # optimal first step found

                visited.add(npos)
                queue.append((npos, taken))

        # No BFS path (goal walled off) — fall back to direct direction
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        if abs(dx) >= abs(dy):
            return "DOWN" if dx > 0 else "UP"
        return "RIGHT" if dy > 0 else "LEFT"
