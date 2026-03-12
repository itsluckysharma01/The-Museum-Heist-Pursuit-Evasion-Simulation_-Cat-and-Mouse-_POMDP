import pygame
import numpy as np

CELL        = 60
PANEL_W     = 210   # side-panel width

BG_COLOR       = (20, 20, 30)
GRID_LINE      = (50, 50, 60)
WALL_COLOR     = (80, 80, 95)
DOOR_COLOR     = (139, 90, 43)
OBJECT_COLOR   = (218, 165, 32)
ARTIFACT_COLOR = (255, 215, 0)
EXIT_COLOR     = (0, 200, 100)
GUARD_COLOR    = (30, 100, 255)
INTRUDER_COLOR = (220, 50, 50)
PANEL_BG       = (12, 14, 26)
PANEL_BORDER   = (70, 80, 130)
TITLE_COLOR    = (180, 200, 255)
LABEL_COLOR    = (140, 150, 180)
VALUE_COLOR    = (230, 240, 255)
SEP_COLOR      = (50, 60, 90)

_TOTAL_OBJECTS = 6   # keep track of original count


class Viewer:

    def __init__(self, size):
        pygame.init()
        self.size = size
        win_w = size * CELL + PANEL_W
        win_h = size * CELL
        self.screen = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Cat & Mouse Museum Heist")
        self.font       = pygame.font.SysFont("Arial", 13, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 14, bold=True)
        self.val_font   = pygame.font.SysFont("Consolas", 14)

    def draw(self, env, belief, score=0, artifact_collected=False,
             turn=0, whose_turn="INTRUDER", last_obs=None, last_guard_action="-"):
        self.screen.fill(BG_COLOR)

        for x in range(self.size):
            for y in range(self.size):
                rect = pygame.Rect(y * CELL, x * CELL, CELL, CELL)
                pos = (x, y)

                if pos in env.walls:
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                elif pos in env.doors:
                    pygame.draw.rect(self.screen, DOOR_COLOR, rect)
                    lbl = self.font.render("DOOR", True, (255, 220, 150))
                    self.screen.blit(lbl, (y * CELL + 6, x * CELL + 22))
                else:
                    prob = belief.map[x][y]
                    heat = int(min(255, prob * 4000))
                    pygame.draw.rect(self.screen, (heat, 0, 0), rect)

                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)

        # Exit
        ex, ey = env.exit
        pygame.draw.rect(self.screen, EXIT_COLOR,
                         pygame.Rect(ey * CELL + 4, ex * CELL + 4, CELL - 8, CELL - 8), 3)
        self.screen.blit(self.font.render("EXIT", True, EXIT_COLOR),
                         (ey * CELL + 8, ex * CELL + 22))

        # Museum objects
        for ox, oy in env.objects:
            pygame.draw.rect(self.screen, OBJECT_COLOR,
                             pygame.Rect(oy * CELL + 10, ox * CELL + 10, CELL - 20, CELL - 20))
            self.screen.blit(self.font.render("OBJ", True, (30, 20, 0)),
                             (oy * CELL + 12, ox * CELL + 22))

        # Artifact — only draw if not yet collected
        if not artifact_collected:
            ax, ay = env.artifact
            pygame.draw.rect(self.screen, ARTIFACT_COLOR,
                             pygame.Rect(ay * CELL + 6, ax * CELL + 6, CELL - 12, CELL - 12))
            self.screen.blit(self.font.render("ART", True, (0, 0, 0)),
                             (ay * CELL + 12, ax * CELL + 22))

        # Guard (blue circle)
        gx, gy = env.guard
        pygame.draw.circle(self.screen, GUARD_COLOR,
                           (gy * CELL + CELL // 2, gx * CELL + CELL // 2), CELL // 2 - 4)
        self.screen.blit(self.font.render("G", True, (255, 255, 255)),
                         (gy * CELL + CELL // 2 - 5, gx * CELL + CELL // 2 - 8))

        # Intruder (red circle)
        ix, iy = env.intruder
        pygame.draw.circle(self.screen, INTRUDER_COLOR,
                           (iy * CELL + CELL // 2, ix * CELL + CELL // 2), CELL // 2 - 4)
        self.screen.blit(self.font.render("I", True, (255, 255, 255)),
                         (iy * CELL + CELL // 2 - 4, ix * CELL + CELL // 2 - 8))

        # ── Side-panel metrics box ──────────────────────────────────────
        px = self.size * CELL          # panel left edge x
        ph = self.size * CELL          # panel height

        pygame.draw.rect(self.screen, PANEL_BG,    pygame.Rect(px, 0, PANEL_W, ph))
        pygame.draw.rect(self.screen, PANEL_BORDER, pygame.Rect(px, 0, PANEL_W, ph), 2)

        def sep(y):
            pygame.draw.line(self.screen, SEP_COLOR, (px + 10, y), (px + PANEL_W - 10, y), 1)

        def row(label, value, y, val_color=VALUE_COLOR):
            self.screen.blit(self.title_font.render(label, True, LABEL_COLOR), (px + 12, y))
            self.screen.blit(self.val_font.render(str(value),  True, val_color),  (px + 12, y + 16))

        # Title
        title = self.title_font.render("METRICS", True, TITLE_COLOR)
        self.screen.blit(title, (px + PANEL_W // 2 - title.get_width() // 2, 10))
        sep(30)

        # Turn counter + whose turn
        turn_color = INTRUDER_COLOR if whose_turn == "INTRUDER" else GUARD_COLOR
        row("TURN", turn, 36, VALUE_COLOR)
        row("WAITING FOR", whose_turn, 68, turn_color)
        sep(100)

        # Score
        row("SCORE", score, 106, (100, 255, 140))
        sep(138)

        # Artifact
        art_val   = "STOLEN ✓" if artifact_collected else "In museum"
        art_color = (255, 220, 60) if artifact_collected else (200, 200, 200)
        row("ARTIFACT", art_val, 144, art_color)
        sep(176)

        # Exhibits collected
        collected = _TOTAL_OBJECTS - len(env.objects)
        row("EXHIBITS", f"{collected} / {_TOTAL_OBJECTS}", 182)
        sep(214)

        # Last sensor observation
        if last_obs is None:
            obs_str, obs_color = "--", LABEL_COLOR
        elif last_obs:
            obs_str, obs_color = "DETECTED !", (255, 80, 80)
        else:
            obs_str, obs_color = "clear", (100, 220, 100)
        row("LAST SENSOR", obs_str, 220, obs_color)
        sep(252)

        # Last guard action
        row("GUARD ACTION", last_guard_action, 258, GUARD_COLOR)
        sep(290)

        # Positions
        gx, gy = env.guard
        row("GUARD POS", f"({gx}, {gy})", 296, GUARD_COLOR)

        ix, iy = env.intruder
        row("INTRUDER POS", f"({ix}, {iy})", 328, INTRUDER_COLOR)
        sep(360)

        # Belief peak
        bx, by = belief.most_likely()
        row("GUARD BELIEF", f"({bx}, {by})", 366, (200, 160, 255))
        sep(398)

        # Controls guide
        controls = [
            "CONTROLS",
            "W / A / S / D  =  move",
            "Guard responds each turn",
            "ESC  =  Quit",
        ]
        cy = 406
        for line in controls:
            color = TITLE_COLOR if line == "CONTROLS" else LABEL_COLOR
            self.screen.blit(self.val_font.render(line, True, color), (px + 12, cy))
            cy += 17

        pygame.display.update()