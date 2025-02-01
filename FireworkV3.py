"""
                             [ DISCLAIMER ]
                             
This code and its associated logic were authored by GuestAUser(Lk10). 
Any use, distribution, or modification of this code MUST include proper credit to the original author. 
Failure to attribute the original author is a violation of intellectual property rights. 
By using this code, you agree to comply with these terms.

Thank you for respecting the work of the original creator.

[TIMESTAMP OF PROJECT] (01/30/2025)
"""

import asyncio, pygame, random, math, time
from pygame.math import Vector2
import pygame_gui
pygame.init()
def get_all_ui_elements(container):
    elements = []
    if hasattr(container, 'get_children'):
        for child in container.get_children():
            elements.append(child)
            elements.extend(get_all_ui_elements(child))
    return elements
async def main():
    WIDTH, HEIGHT = 1600, 900
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
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
                    col = (max(0, min(255, int(self.color[0]))),
                           max(0, min(255, int(self.color[1]))),
                           max(0, min(255, int(self.color[2]))),
                           int(a))
                    pygame.draw.circle(glow, col, (base_size // 2, base_size // 2), r)
                surf.blit(glow, (int(self.pos.x - base_size // 2), int(self.pos.y - base_size // 2)), special_flags=pygame.BLEND_ADD)
    class Firework:
        def __init__(self, pos, mode, color=None):
            self.pos = Vector2(pos)
            if color is not None:
                self.color = tuple(max(0, min(255, int(x))) for x in color[:3])
            else:
                self.color = (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
            self.rocket = Particle(self.pos, (random.uniform(-2, 2), random.uniform(-22, -18)), self.color, 1.0, 2.2, drag=0.96, gravity=0.05)
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
                if not self.second_exploded and random.random() < 0.02 and len(self.particles) > 15:
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
                    self.particles.append(Particle(self.rocket.pos, (vx, vy), self.color, 1.3, random.uniform(1.5, 2.5)))
            elif self.mode == "ring":
                for i in range(36):
                    a = i * (2 * math.pi / 36)
                    vx, vy = math.cos(a) * 6, math.sin(a) * 6
                    self.particles.append(Particle(self.rocket.pos, (vx, vy), self.color, 1.2, random.uniform(1.2, 2.0)))
            elif self.mode == "star":
                for i in range(5):
                    a = i * (2 * math.pi / 5)
                    for r in [1, 2, 3]:
                        vx = math.cos(a) * r * 4
                        vy = math.sin(a) * r * 4
                        spark = (int(min(255, self.color[0] + random.randint(-30, 30))),
                                 int(min(255, self.color[1] + random.randint(-30, 30))),
                                 int(min(255, self.color[2] + random.randint(-30, 30))))
                        self.particles.append(Particle(self.rocket.pos, (vx, vy), spark, 1.2, random.uniform(1, 2), drag=0.92))
            else:
                for i in range(20):
                    a = i * (2 * math.pi / 20)
                    s = random.uniform(2, 4)
                    vx, vy = math.cos(a) * s, math.sin(a) * s
                    self.particles.append(Particle(self.rocket.pos, (vx, vy), self.color, 1.6, random.uniform(1, 2), drag=0.96, gravity=0.12))
        def secondary_explode(self, center):
            for _ in range(30):
                a = random.uniform(0, 2 * math.pi)
                s = random.uniform(2, 5)
                cx, cy = math.cos(a) * s, math.sin(a) * s
                c = (min(255, self.color[0] + random.randint(-60, 60)),
                     min(255, self.color[1] + random.randint(-60, 60)),
                     min(255, self.color[2] + random.randint(-60, 60)))
                self.secondary.append(Particle(center, (cx, cy), c, 1.2, random.uniform(1, 2), 0.95, 0.1))
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
    class Settings:
        def __init__(self):
            self.modes = ["burst", "ring", "star", "trail"]
            self.effect_mode = self.modes[0]
            self.color_mode = "random"
            self.custom_color = [255, 0, 0]
    settings = Settings()
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    effect_mode_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=settings.modes, starting_option=settings.effect_mode, relative_rect=pygame.Rect((10, 10), (150, 30)), manager=manager)
    toggle_color_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 50), (150, 30)), text="Color Mode: Random", manager=manager)
    pick_color_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 90), (150, 30)), text="Pick Custom Color", manager=manager)
    if settings.color_mode == "random":
        pick_color_button.disable()
    starfield = Starfield(200)
    clouds = CloudLayer()
    fireworks = []
    launching = False
    time_since_launch = 0
    launch_interval = 0.15
    running = True
    while running:
        dt = CLOCK.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                ui_under_mouse = False
                for element in get_all_ui_elements(manager.get_root_container()):
                    if element.visible and element.combined_rect.collidepoint(event.pos):
                        ui_under_mouse = True
                        break
                if not ui_under_mouse:
                    launching = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                launching = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == toggle_color_button:
                    if settings.color_mode == "random":
                        settings.color_mode = "custom"
                        pick_color_button.enable()
                        toggle_color_button.set_text("Color Mode: Custom")
                    else:
                        settings.color_mode = "random"
                        pick_color_button.disable()
                        toggle_color_button.set_text("Color Mode: Random")
                if event.ui_element == pick_color_button:
                    pygame_gui.windows.UIColourPickerDialog(rect=pygame.Rect(160, 50, 400, 400), manager=manager, window_title="Select Custom Color", initial_colour=pygame.Color(*settings.custom_color))
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == effect_mode_dropdown:
                    settings.effect_mode = event.text
            if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                settings.custom_color = [event.colour.r, event.colour.g, event.colour.b]
        manager.update(dt)
        time_since_launch += dt
        if launching and time_since_launch >= launch_interval:
            firework_color = settings.custom_color if settings.color_mode == "custom" else None
            fireworks.append(Firework(pygame.mouse.get_pos(), settings.effect_mode, firework_color))
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
        manager.draw_ui(SCREEN)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(main())
