from collections import deque

DANGER_RADIUS = 4   # BFS hops — if guard is this close, switch to FLEE
LOOT_RADIUS   = 4   # grab an exhibit only if reachable within this many steps


class Intruder:

    ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
    _DELTA  = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    def choose_action(self, intruder_pos, env, artifact_collected):
        """
        Returns (action, goal_desc, mode, threat_dist).

        MODE logic (priority order):
          FLEE       — guard within DANGER_RADIUS; move to maximise distance
          FLEE→EXIT  — guard close AND has artifact; flee toward exit
          ESCAPE     — safe distance and has artifact; BFS straight to exit
          HEIST      — safe; grab nearby exhibit then artifact
        """
        ipos      = tuple(intruder_pos)
        guard_pos = tuple(env.guard)

        # Full BFS distance maps
        guard_dist    = self._dist_map(guard_pos, env)
        threat_dist   = guard_dist.get(ipos, 999)

        in_danger = threat_dist <= DANGER_RADIUS

        if in_danger:
            if artifact_collected:
                action, goal_desc = self._flee_to_exit(ipos, guard_dist, env)
                return action, goal_desc, "FLEE→EXIT", threat_dist
            else:
                action, goal_desc = self._flee(ipos, guard_dist, env)
                return action, goal_desc, "FLEE", threat_dist

        # Safe — heist or escape
        if artifact_collected:
            action = self._bfs_action(ipos, tuple(env.exit), env)
            return action, f"EXIT {env.exit}", "ESCAPE", threat_dist

        # Opportunistically loot a nearby exhibit if safe
        nearby = self._nearest_safe(ipos, [tuple(o) for o in env.objects],
                                    env, guard_dist)
        if nearby is not None:
            action = self._bfs_action(ipos, nearby, env)
            return action, f"OBJ {nearby}", "HEIST", threat_dist

        # No safe exhibit nearby — go for artifact directly
        action = self._bfs_action(ipos, tuple(env.artifact), env)
        return action, f"ART {env.artifact}", "HEIST", threat_dist

    # ── flee helpers ─────────────────────────────────────────────────

    def _flee(self, ipos, guard_dist, env):
        """Move to the reachable neighbour that maximises BFS dist from guard."""
        best_action, best_score = None, -1
        for action, (dx, dy) in self._DELTA.items():
            npos = self._clamp(ipos[0] + dx, ipos[1] + dy, env)
            if npos in env.walls:
                continue
            score = guard_dist.get(npos, 0)
            if score > best_score:
                best_score, best_action = score, action
        return best_action or "DOWN", f"FLEE (guard dist={best_score})"

    def _flee_to_exit(self, ipos, guard_dist, env):
        """
        Flee AND head toward exit: score = guard_distance * 10 - exit_distance.
        This balances safety with making progress toward escape.
        """
        exit_dist = self._dist_map(tuple(env.exit), env)
        best_action, best_score = None, float("-inf")
        for action, (dx, dy) in self._DELTA.items():
            npos = self._clamp(ipos[0] + dx, ipos[1] + dy, env)
            if npos in env.walls:
                continue
            score = guard_dist.get(npos, 0) * 10 - exit_dist.get(npos, 999)
            if score > best_score:
                best_score, best_action = score, action
        return best_action or "DOWN", f"FLEE→EXIT"

    # ── heist helpers ────────────────────────────────────────────────

    def _nearest_safe(self, start, targets, env, guard_dist):
        """Return the exhibit reachable in ≤LOOT_RADIUS steps whose cell is safe."""
        if not targets:
            return None
        intruder_dist = self._dist_map(start, env)
        best, best_d  = None, 999
        for t in targets:
            t = tuple(t)
            d = intruder_dist.get(t, 999)
            if d <= LOOT_RADIUS and guard_dist.get(t, 999) > DANGER_RADIUS and d < best_d:
                best_d, best = d, t
        return best

    # ── BFS utilities ────────────────────────────────────────────────

    def _dist_map(self, start, env):
        """BFS distance from start to every reachable cell → dict {cell: dist}."""
        dist  = {start: 0}
        queue = deque([start])
        while queue:
            pos = queue.popleft()
            for dx, dy in self._DELTA.values():
                npos = self._clamp(pos[0] + dx, pos[1] + dy, env)
                if npos not in env.walls and npos not in dist:
                    dist[npos] = dist[pos] + 1
                    queue.append(npos)
        return dist

    def _bfs_action(self, start, goal, env):
        """Return the first action of the optimal (BFS) path from start to goal."""
        start, goal = tuple(start), tuple(goal)
        if start == goal:
            return "DOWN"
        queue, visited = deque([(start, None)]), {start}
        while queue:
            pos, first = queue.popleft()
            for action, (dx, dy) in self._DELTA.items():
                npos = self._clamp(pos[0] + dx, pos[1] + dy, env)
                if npos in env.walls or npos in visited:
                    continue
                taken = first if first is not None else action
                if npos == goal:
                    return taken
                visited.add(npos)
                queue.append((npos, taken))
        # Fallback: greedy direction
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        return ("DOWN" if dx > 0 else "UP") if abs(dx) >= abs(dy) else ("RIGHT" if dy > 0 else "LEFT")

    def _clamp(self, x, y, env):
        return (max(0, min(env.size - 1, x)), max(0, min(env.size - 1, y)))

