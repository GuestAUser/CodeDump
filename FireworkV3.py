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
import math
import random
import time
import threading
from typing import List, Optional, Tuple

import numpy as np  # Optimized: NOISE-GEN;
import pygame
import pygame_gui
from pygame.math import Vector2

pygame.init()


def get_all_ui_elements(container) -> List[pygame_gui.core.UIElement]:
    """Recursively get all UI elements from a container."""
    elements = []
    if hasattr(container, "get_children"):
        for child in container.get_children():
            elements.append(child)
            elements.extend(get_all_ui_elements(child))
    return elements


class Particle:
    # Cache for pre-rendered glow surfaces: key -> surface;
    _glow_cache: dict = {}

    def __init__(
        self,
        pos: Tuple[float, float],
        vel: Tuple[float, float],
        color: Tuple[int, int, int],
        radius: float,
        life: float,
        drag: float = 0.96,
        gravity: float = 0.1,
    ):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.color = color
        self.radius = radius
        self.life = life
        self.drag = drag
        self.gravity = gravity

    def update(self, dt: float) -> None:
        self.vel *= self.drag
        self.vel.y += self.gravity * dt * 60
        self.pos += self.vel * dt * 60
        self.life -= dt

    def draw(self, surf: pygame.Surface) -> None:
        if self.life <= 0:
            return

        base_size = max(2, int(self.radius * 5))
        cache_key = (base_size, int(self.radius), self.color)
        if cache_key in Particle._glow_cache:
            glow = Particle._glow_cache[cache_key]
        else:
            glow = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
            for i in range(4):
                r = max(0, int(self.radius) + 3 - i * 2)
                a = max(0, 120 - i * 28)
                col = (
                    max(0, min(255, int(self.color[0]))),
                    max(0, min(255, int(self.color[1]))),
                    max(0, min(255, int(self.color[2]))),
                    int(a),
                )
                pygame.draw.circle(glow, col, (base_size // 2, base_size // 2), r)
            Particle._glow_cache[cache_key] = glow

        surf.blit(
            glow,
            (int(self.pos.x - base_size // 2), int(self.pos.y - base_size // 2)),
            special_flags=pygame.BLEND_ADD,
        )


class Firework:
    def __init__(self, pos: Tuple[int, int], mode: str, color: Optional[Tuple[int, int, int]] = None):
        self.pos = Vector2(pos)
        if color is not None:
            self.color = tuple(max(0, min(255, int(x))) for x in color[:3])
        else:
            self.color = (
                random.randint(128, 255),
                random.randint(128, 255),
                random.randint(128, 255),
            )
        self.rocket = Particle(
            pos,
            (random.uniform(-2, 2), random.uniform(-22, -18)),
            self.color,
            1.0,
            2.2,
            drag=0.96,
            gravity=0.05,
        )
        self.exploded = False
        self.particles: List[Particle] = []
        self.mode = mode
        self.secondary: List[Particle] = []
        self.second_exploded = False

    def update(self, dt: float) -> None:
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

    def draw(self, surf: pygame.Surface) -> None:
        if not self.exploded:
            self.rocket.draw(surf)
        else:
            for p in self.particles:
                p.draw(surf)
            for p in self.secondary:
                p.draw(surf)

    def explode(self) -> None:
        if self.mode == "burst":
            for _ in range(60):
                a = random.uniform(0, 2 * math.pi)
                spd = random.uniform(3, 7)
                vx, vy = math.cos(a) * spd, math.sin(a) * spd
                self.particles.append(
                    Particle(self.rocket.pos, (vx, vy), self.color, 1.3, random.uniform(1.5, 2.5))
                )
        elif self.mode == "ring":
            for i in range(36):
                a = i * (2 * math.pi / 36)
                vx, vy = math.cos(a) * 6, math.sin(a) * 6
                self.particles.append(
                    Particle(self.rocket.pos, (vx, vy), self.color, 1.2, random.uniform(1.2, 2.0))
                )
        elif self.mode == "star":
            for i in range(5):
                a = i * (2 * math.pi / 5)
                for r in [1, 2, 3]:
                    vx = math.cos(a) * r * 4
                    vy = math.sin(a) * r * 4
                    spark = (
                        int(min(255, self.color[0] + random.randint(-30, 30))),
                        int(min(255, self.color[1] + random.randint(-30, 30))),
                        int(min(255, self.color[2] + random.randint(-30, 30))),
                    )
                    self.particles.append(
                        Particle(self.rocket.pos, (vx, vy), spark, 1.2, random.uniform(1, 2), drag=0.92)
                    )
        else:
            for i in range(20):
                a = i * (2 * math.pi / 20)
                s = random.uniform(2, 4)
                vx, vy = math.cos(a) * s, math.sin(a) * s
                self.particles.append(
                    Particle(self.rocket.pos, (vx, vy), self.color, 1.6, random.uniform(1, 2), drag=0.96, gravity=0.12)
                )

    def secondary_explode(self, center: Vector2) -> None:
        for _ in range(30):
            a = random.uniform(0, 2 * math.pi)
            s = random.uniform(2, 5)
            cx, cy = math.cos(a) * s, math.sin(a) * s
            c = (
                min(255, self.color[0] + random.randint(-60, 60)),
                min(255, self.color[1] + random.randint(-60, 60)),
                min(255, self.color[2] + random.randint(-60, 60)),
            )
            self.secondary.append(Particle(center, (cx, cy), c, 1.2, random.uniform(1, 2), drag=0.95, gravity=0.1))


class Starfield:
    def __init__(self, star_count: int, width: int, height: int):
        self.stars: List[List] = []
        self.width = width
        self.height = height
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for _ in range(star_count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            base_c = random.randint(180, 255)
            phase = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.3, 2)
            self.stars.append([x, y, base_c, phase, speed])

    def update(self, dt: float) -> None:
        for s in self.stars:
            s[3] += s[4] * dt
            s[2] += int(30 * math.sin(s[3]) * dt)
            s[2] = max(150, min(255, s[2]))

    def draw(self, surf: pygame.Surface) -> None:
        self.surf.fill((0, 0, 0, 0))
        for s in self.stars:
            c = s[2]
            color = (c, c, c, 255)
            pygame.draw.circle(self.surf, color, (s[0], s[1]), 1)
        surf.blit(self.surf, (0, 0))


class CloudLayer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0
        self.scroll_speed_x = 20
        self.scroll_speed_y = 10
        self.alpha = 70
        self.noise_surf = self.generate_noise_surf()

    def generate_noise_surf(self) -> pygame.Surface:
        w2, h2 = self.width // 2, self.height // 2
        noise = np.random.randint(0, 81, (h2, w2), dtype=np.uint8)
        noise_rgb = np.stack([noise] * 3, axis=-1)
        alpha = np.full((h2, w2, 1), 255, dtype=np.uint8)
        noise_rgba = np.concatenate([noise_rgb, alpha], axis=-1)
        surf = pygame.image.frombuffer(noise_rgba.tobytes(), (w2, h2), "RGBA")
        surf = pygame.transform.smoothscale(surf, (self.width, self.height))
        return surf.convert_alpha()

    def update(self, dt: float) -> None:
        self.offset_x += self.scroll_speed_x * dt
        self.offset_y += self.scroll_speed_y * dt

    def draw(self, surf: pygame.Surface) -> None:
        ox = int(self.offset_x) % self.width
        oy = int(self.offset_y) % self.height
        tmp = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        tmp.blit(self.noise_surf, (-ox, -oy))
        tmp.blit(self.noise_surf, (-ox + self.width, -oy))
        tmp.blit(self.noise_surf, (-ox, -oy + self.height))
        tmp.blit(self.noise_surf, (-ox + self.width, -oy + self.height))
        tmp.set_alpha(self.alpha)
        surf.blit(tmp, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)


def bloom_pass(surf: pygame.Surface) -> pygame.Surface:
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
        self.modes: List[str] = ["burst", "ring", "star", "trail"]
        self.effect_mode: str = self.modes[0]
        self.color_mode: str = "random"
        self.custom_color: List[int] = [255, 0, 0]


class FireworksSimulation:
    def __init__(self, width: int = 1600, height: int = 900):
        self.WIDTH = width
        self.HEIGHT = height
        self.SCREEN = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), pygame.DOUBLEBUF | pygame.SCALED, vsync=1
        )
        pygame.display.set_caption("Starry Fireworks Simulation (OPTIMIZED-RELEASE)")
        self.CLOCK = pygame.time.Clock()
        self.BLACK = (0, 0, 0)

        self.settings = Settings()
        self.starfield = Starfield(200, self.WIDTH, self.HEIGHT)
        self.clouds = CloudLayer(self.WIDTH, self.HEIGHT)
        self.fireworks: List[Firework] = []
        self.launching = False
        self.time_since_launch = 0
        self.launch_interval = 0.15

        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT))
        self.effect_mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.settings.modes,
            starting_option=self.settings.effect_mode,
            relative_rect=pygame.Rect((10, 10), (150, 30)),
            manager=self.manager,
        )
        self.toggle_color_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 50), (150, 30)),
            text="Color Mode: Random",
            manager=self.manager,
        )
        self.pick_color_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 90), (150, 30)),
            text="Pick Custom Color",
            manager=self.manager,
        )
        if self.settings.color_mode == "random":
            self.pick_color_button.disable()

    async def run(self) -> None:
        running = True
        while running:
            dt = self.CLOCK.tick(60) / 1000.0

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.manager.process_events(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    ui_under_mouse = False
                    for element in get_all_ui_elements(self.manager.get_root_container()):
                        if element.visible and element.combined_rect.collidepoint(event.pos):
                            ui_under_mouse = True
                            break
                    if not ui_under_mouse:
                        self.launching = True

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.launching = False

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.toggle_color_button:
                        if self.settings.color_mode == "random":
                            self.settings.color_mode = "custom"
                            self.pick_color_button.enable()
                            self.toggle_color_button.set_text("Color Mode: Custom")
                        else:
                            self.settings.color_mode = "random"
                            self.pick_color_button.disable()
                            self.toggle_color_button.set_text("Color Mode: Random")
                    if event.ui_element == self.pick_color_button:
                        pygame_gui.windows.UIColourPickerDialog(
                            rect=pygame.Rect(160, 50, 400, 400),
                            manager=self.manager,
                            window_title="Select Custom Color",
                            initial_colour=pygame.Color(*self.settings.custom_color),
                        )

                if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.effect_mode_dropdown:
                        self.settings.effect_mode = event.text

                if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                    self.settings.custom_color = [event.colour.r, event.colour.g, event.colour.b]

            self.manager.update(dt)

            # --- Simulation Updates ---
            self.time_since_launch += dt
            if self.launching and self.time_since_launch >= self.launch_interval:
                firework_color = (
                    self.settings.custom_color
                    if self.settings.color_mode == "custom"
                    else None
                )
                self.fireworks.append(
                    Firework(pygame.mouse.get_pos(), self.settings.effect_mode, firework_color)
                )
                self.time_since_launch = 0

            self.starfield.update(dt)
            self.clouds.update(dt)
            for f in self.fireworks:
                f.update(dt)
            self.fireworks = [
                f for f in self.fireworks if not (f.exploded and not f.particles and not f.secondary)
            ]

            # --- Drawing ---
            buffer_surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            buffer_surf.fill(self.BLACK)
            self.starfield.draw(buffer_surf)
            self.clouds.draw(buffer_surf)
            for f in self.fireworks:
                f.draw(buffer_surf)

            buffer_surf = await asyncio.to_thread(bloom_pass, buffer_surf)

            self.SCREEN.blit(buffer_surf, (0, 0))
            self.manager.draw_ui(self.SCREEN)
            pygame.display.flip()

            await asyncio.sleep(0)
        pygame.quit()

async def main() -> None:
    sim = FireworksSimulation()
    await sim.run()

if __name__ == "__main__":
    asyncio.run(main())
