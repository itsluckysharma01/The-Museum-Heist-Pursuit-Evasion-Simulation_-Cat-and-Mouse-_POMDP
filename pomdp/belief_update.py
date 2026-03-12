import numpy as np

NOISE_FLOOR = 0.001


class Belief:

    def __init__(self, size):
        self.size = size
        # Start belief concentrated near intruder's starting corner [9,9]
        self.map = np.zeros((size, size))
        for x in range(size):
            for y in range(size):
                self.map[x][y] = np.exp(-((x - (size - 1)) ** 2 + (y - (size - 1)) ** 2) / 4.0)
        self._normalise()

    def _normalise(self):
        self.map = np.clip(self.map, 1e-9, None)
        self.map += NOISE_FLOOR / (self.size * self.size)
        self.map /= self.map.sum()

    def update(self, observation, guard_pos):
        gx, gy = guard_pos

        # --- Diffuse: intruder may have moved one step ---
        diffused = self.map.copy()
        diffused[1:,  :]  += self.map[:-1, :] * 0.12
        diffused[:-1, :]  += self.map[1:,  :] * 0.12
        diffused[:,  1:]  += self.map[:, :-1] * 0.12
        diffused[:, :-1]  += self.map[:, 1:]  * 0.12
        self.map = diffused

        if observation:
            # DETECTED: intruder is within sensor range — tight Gaussian spike
            # around guard's position (radius 2) to lock on fast
            DETECT_RADIUS = 2
            for dx in range(-DETECT_RADIUS, DETECT_RADIUS + 1):
                for dy in range(-DETECT_RADIUS, DETECT_RADIUS + 1):
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        dist_sq = dx * dx + dy * dy
                        # Strong spike: closer cells get much higher boost
                        boost = np.exp(-dist_sq / 1.5) * 12.0
                        self.map[nx][ny] *= (1 + boost)

            # Zero-out cells far from guard — intruder can't be far if detected
            FAR_RADIUS = 4
            for x in range(self.size):
                for y in range(self.size):
                    if abs(x - gx) + abs(y - gy) > FAR_RADIUS:
                        self.map[x][y] *= 0.05
        else:
            # NOT DETECTED: intruder is outside sensor range — decay nearby cells
            SENSOR_RADIUS = 3
            for dx in range(-SENSOR_RADIUS, SENSOR_RADIUS + 1):
                for dy in range(-SENSOR_RADIUS, SENSOR_RADIUS + 1):
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        dist = abs(dx) + abs(dy)
                        weight = 1.0 - dist / (SENSOR_RADIUS + 1)
                        self.map[nx][ny] *= max(0.10, 1 - 0.65 * weight)

        self._normalise()

    def most_likely(self, exclude=None):
        """Return [x, y] of the highest-probability cell, skipping `exclude`."""
        m = self.map.copy()
        if exclude is not None:
            ex, ey = exclude
            if 0 <= ex < self.size and 0 <= ey < self.size:
                m[ex][ey] = 0.0
        idx = np.argmax(m)
        x = idx // self.size
        y = idx % self.size
        return [x, y]

