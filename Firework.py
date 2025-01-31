"""
                             [ DISCLAIMER ]
                             
This code and its associated logic were authored by GuestAUser(Lk10). 
Any use, distribution, or modification of this code MUST include proper credit to the original author. 
Failure to attribute the original author is a violation of intellectual property rights. 
By using this code, you agree to comply with these terms.

Thank you for respecting the work of the original creator.

[TIMESTAMP OF PROJECT] (01/30/2025)
"""

import asyncio
import pygame, random, math, time
from pygame.math import Vector2

pygame.init()

async def main():
    WIDTH, HEIGHT = 1600, 900
    SCREEN = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.DOUBLEBUF | pygame.SCALED,
        vsync=1
    )
    pygame.display.set_caption("Starry Fireworks Simulation (OPTIMIZED-RELEASE)")
    CLOCK = pygame.time.Clock()

    BLACK = (0, 0, 0)

    class Particle:
        def __init__(self, pos, vel, color, radius, life, drag=0.96, gravity=0.1):
            self.pos = Vector2(pos)
            self.vel = Vector2(vel)
            self.color = color
            self.radius = radius
            self.life = life
            self.drag = drag
            self.gravity = gravity

        def update(self, dt):
            self.vel *= self.drag
            self.vel.y += self.gravity * dt * 60
            self.pos += self.vel * dt * 60
            self.life -= dt

        def draw(self, surf):
            if self.life > 0:
                base_size = max(2, int(self.radius * 5))
                glow = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
                for i in range(4):
                    r = max(0, int(self.radius) + 3 - i * 2)
                    a = max(0, 120 - i * 28)
                    pygame.draw.circle(glow, (*self.color, a), (base_size // 2, base_size // 2), r)
                surf.blit(
                    glow,
                    (int(self.pos.x - base_size // 2), int(self.pos.y - base_size // 2)),
                    special_flags=pygame.BLEND_ADD
                )

    class Firework:
        def __init__(self, pos, mode):
            self.pos = Vector2(pos)
            self.color = (
                random.randint(128, 255),
                random.randint(128, 255),
                random.randint(128, 255)
            )
            self.rocket = Particle(
                self.pos,
                (random.uniform(-2, 2), random.uniform(-22, -18)),
                self.color,
                1.0,
                2.2,
                drag=0.96,
                gravity=0.05
            )
            self.exploded = False
            self.particles = []
            self.mode = mode
            self.secondary = []
            self.second_exploded = False

        def update(self, dt):
            if not self.exploded:
                self.rocket.update(dt)
                if self.rocket.life <= 0 or self.rocket.vel.y >= 0:
                    self.exploded = True
                    self.explode()
            else:
                for p in self.particles:
                    p.update(dt)
                self.particles = [p for p in self.particles if p.life > 0]
                if (
                    not self.second_exploded
                    and random.random() < 0.02
                    and len(self.particles) > 15
                ):
                    self.second_exploded = True
                    center = random.choice(self.particles).pos
                    self.secondary_explode(center)
                for s in self.secondary:
                    s.update(dt)
                self.secondary = [p for p in self.secondary if p.life > 0]

        def draw(self, surf):
            if not self.exploded:
                self.rocket.draw(surf)
            else:
                for p in self.particles:
                    p.draw(surf)
                for p in self.secondary:
                    p.draw(surf)

        def explode(self):
            if self.mode == "burst":
                for _ in range(60):
                    a = random.uniform(0, 2 * math.pi)
                    spd = random.uniform(3, 7)
                    vx, vy = math.cos(a) * spd, math.sin(a) * spd
                    self.particles.append(
                        Particle(
                            self.rocket.pos,
                            (vx, vy),
                            self.color,
                            1.3,
                            random.uniform(1.5, 2.5)
                        )
                    )
            elif self.mode == "ring":
                for i in range(36):
                    a = i * (2 * math.pi / 36)
                    vx, vy = math.cos(a) * 6, math.sin(a) * 6
                    self.particles.append(
                        Particle(
                            self.rocket.pos,
                            (vx, vy),
                            self.color,
                            1.2,
                            random.uniform(1.2, 2.0)
                        )
                    )
            elif self.mode == "star":
                for i in range(5):
                    a = i * (2 * math.pi / 5)
                    for r in [1, 2, 3]:
                        vx = math.cos(a) * r * 4
                        vy = math.sin(a) * r * 4
                        spark = (
                            min(255, self.color[0] + random.randint(-30, 30)),
                            min(255, self.color[1] + random.randint(-30, 30)),
                            min(255, self.color[2] + random.randint(-30, 30)),
                        )
                        self.particles.append(
                            Particle(
                                self.rocket.pos,
                                (vx, vy),
                                spark,
                                1.2,
                                random.uniform(1, 2),
                                drag=0.92
                            )
                        )
            else:
                for i in range(20):
                    a = i * (2 * math.pi / 20)
                    s = random.uniform(2, 4)
                    vx, vy = math.cos(a) * s, math.sin(a) * s
                    self.particles.append(
                        Particle(
                            self.rocket.pos,
                            (vx, vy),
                            self.color,
                            1.6,
                            random.uniform(1, 2),
                            drag=0.96,
                            gravity=0.12
                        )
                    )

        def secondary_explode(self, center):
            for _ in range(30):
                a = random.uniform(0, 2 * math.pi)
                s = random.uniform(2, 5)
                cx, cy = math.cos(a) * s, math.sin(a) * s
                c = (
                    min(255, self.color[0] + random.randint(-60, 60)),
                    min(255, self.color[1] + random.randint(-60, 60)),
                    min(255, self.color[2] + random.randint(-60, 60)),
                )
                self.secondary.append(
                    Particle(center, (cx, cy), c, 1.2, random.uniform(1, 2), 0.95, 0.1)
                )

    class UI:
        def __init__(self):
            self.modes = ["burst", "ring", "star", "trail"]
            self.idx = 0
            self.font = pygame.font.SysFont(None, 28)

        @property
        def mode(self):
            return self.modes[self.idx]

        def next_mode(self):
            self.idx = (self.idx + 1) % len(self.modes)

        def prev_mode(self):
            self.idx = (self.idx - 1) % len(self.modes)

        def draw(self, surf):
            pygame.draw.rect(surf, (25, 25, 25), (10, 10, 280, 80))
            t1 = self.font.render(f"Effect: {self.mode}", True, (255, 255, 255))
            t2 = self.font.render("Hold LMB: fireworks", True, (255, 255, 255))
            t3 = self.font.render("Q/E: change | ESC: quit", True, (255, 255, 255))
            surf.blit(t1, (20, 15))
            surf.blit(t2, (20, 40))
            surf.blit(t3, (20, 65))

    class Starfield:
        def __init__(self, star_count):
            self.stars = []
            self.surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for _ in range(star_count):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                base_c = random.randint(180, 255)
                phase = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.3, 2)
                self.stars.append([x, y, base_c, phase, speed])

        def update(self, dt):
            for s in self.stars:
                s[3] += s[4] * dt
                s[2] += int(30 * math.sin(s[3]) * dt)
                s[2] = max(150, min(255, s[2]))

        def draw(self, surf):
            self.surf.fill((0, 0, 0, 0))
            for s in self.stars:
                c = s[2]
                color = (c, c, c, 255)
                pygame.draw.circle(self.surf, color, (s[0], s[1]), 1)
            surf.blit(self.surf, (0, 0))

    class CloudLayer:
        def __init__(self):
            self.offset_x = 0
            self.offset_y = 0
            self.scroll_speed_x = 20
            self.scroll_speed_y = 10
            self.alpha = 70
            self.noise_surf = self.generate_noise_surf()

        def generate_noise_surf(self):
            w2, h2 = WIDTH // 2, HEIGHT // 2
            surf = pygame.Surface((w2, h2), pygame.SRCALPHA)
            for y in range(h2):
                for x in range(w2):
                    val = random.randint(0, 80)
                    surf.set_at((x, y), (val, val, val, 255))
            return pygame.transform.smoothscale(surf, (WIDTH, HEIGHT))

        def update(self, dt):
            self.offset_x += self.scroll_speed_x * dt
            self.offset_y += self.scroll_speed_y * dt

        def draw(self, surf):
            ox = int(self.offset_x) % WIDTH
            oy = int(self.offset_y) % HEIGHT
            tmp = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            tmp.blit(self.noise_surf, (-ox, -oy))
            tmp.blit(self.noise_surf, (-ox + WIDTH, -oy))
            tmp.blit(self.noise_surf, (-ox, -oy + HEIGHT))
            tmp.blit(self.noise_surf, (-ox + WIDTH, -oy + HEIGHT))
            tmp.set_alpha(self.alpha)
            surf.blit(tmp, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

    def bloom_pass(surf):
        scale = 0.25
        w, h = int(surf.get_width() * scale), int(surf.get_height() * scale)
        small = pygame.transform.smoothscale(surf, (w, h))
        for _ in range(2):
            small = pygame.transform.smoothscale(small, (w, h))
        bloom = pygame.transform.smoothscale(small, surf.get_size())
        final = surf.copy()
        final.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)
        return final

    ui = UI()
    starfield = Starfield(star_count=200)
    clouds = CloudLayer()

    fireworks = []
    launching = False
    time_since_launch = 0
    launch_interval = 0.15

    running = True
    while running:
        dt = CLOCK.tick(0) / 1000 # Avoid capping FPS | Let it rely on vsync;
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_q:
                    ui.prev_mode()
                elif e.key == pygame.K_e:
                    ui.next_mode()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                launching = True
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                launching = False

        time_since_launch += dt
        if launching and time_since_launch >= launch_interval:
            fireworks.append(Firework(pygame.mouse.get_pos(), ui.mode))
            time_since_launch = 0

        starfield.update(dt)
        clouds.update(dt)

        for f in fireworks:
            f.update(dt)
        fireworks = [f for f in fireworks if not (f.exploded and not f.particles and not f.secondary)]

        buffer_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        buffer_surf.fill(BLACK)
        starfield.draw(buffer_surf)
        clouds.draw(buffer_surf)

        for f in fireworks:
            f.draw(buffer_surf)
        buffer_surf = bloom_pass(buffer_surf)

        SCREEN.blit(buffer_surf, (0, 0))
        ui.draw(SCREEN)
        pygame.display.flip()

        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())
