#!/bin/env python3

from importlib.resources import files

import pygame
import pygame._sdl2 as sdl2

from lfo import LFO
from rpeasings import out_elastic
from pgcooldown import Cooldown

pygame.mixer.init()

TITLE = 'pygame minimal template'
SCREEN = pygame.Rect(0, 0, 1024, 768)
FPS = 60
DT_MAX = 3 / FPS

ASSETS = files('oiiai.assets')
TINYKETT_RADIUS = 128
BPM = 150
BEAT = 60 / BPM


def main():
    clock = pygame.time.Clock()
    window = pygame.Window(title=TITLE, size=SCREEN.size)
    renderer = sdl2.Renderer(window)

    orbit = LFO(8 * BEAT)
    color = LFO(4 * BEAT)
    pump = LFO(2 * BEAT)
    rotate = LFO(16 * BEAT)
    toggle = LFO(4 * BEAT)
    kick = Cooldown(BEAT, cold=True)
    hihat = Cooldown(BEAT / 4, cold=True)
    oiiai = Cooldown(8 * BEAT, cold=True)

    kick_sample = pygame.mixer.Sound(ASSETS / 'kick.wav')
    hihat_sample = pygame.mixer.Sound(ASSETS / 'hi-hat.wav')
    oiiai_sample = pygame.mixer.Sound(ASSETS / 'oiiai.wav')
    synth_sample = pygame.mixer.Sound(ASSETS / 'psy-short.wav')
    synth_sample.set_volume(0.5)

    img = pygame.image.load(ASSETS / 'cat.png')
    kett = sdl2.Texture.from_surface(renderer, pygame.transform.scale(img, (128, 128)))
    tinykett = sdl2.Texture.from_surface(renderer, pygame.transform.scale(img, (32, 32)))
    tinyrect = tinykett.get_rect()

    rotation_rect = kett.get_rect().move_to(center=SCREEN.center)
    pump_rect = kett.get_rect().move_to(center=(SCREEN.centerx, SCREEN.height // 4))
    other_pump_rect = kett.get_rect().move_to(center=(SCREEN.centerx, 3 * SCREEN.height // 4))
    toggle_rect = (kett.get_rect().move_to(midleft=SCREEN.midleft),
                   kett.get_rect().move_to(midright=SCREEN.midright))

    def play_sample_or_not(cooldown, *samples):
        if cooldown.cold():
            cooldown.reset(wrap=True)
            for s in samples:
                s.play()

    running = True
    while running:
        # No need to use dt here, LFOs and cooldown track their own time
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        play_sample_or_not(kick, kick_sample, synth_sample)
        play_sample_or_not(hihat, hihat_sample)
        play_sample_or_not(oiiai, oiiai_sample)

        renderer.draw_color = pygame.Color.from_hsva(color.sawtooth * 360, 100, 100, 100)
        renderer.clear()

        kett.draw(dstrect=rotation_rect, angle=rotate.sawtooth * 360)
        kett.draw(dstrect=pump_rect.scale_by(out_elastic(pump.inv_triangle)))
        kett.draw(dstrect=other_pump_rect.scale_by(out_elastic(pump.triangle)))
        kett.draw(dstrect=toggle_rect[int(toggle.square)])

        for r in (rotation_rect, pump_rect, other_pump_rect, *toggle_rect):
            rect = tinyrect.move_to(center=(r.centerx + orbit.cosine * TINYKETT_RADIUS,
                                            r.centery + orbit.sine * TINYKETT_RADIUS))
            tinykett.draw(dstrect=rect, angle=orbit.inv_sawtooth * 360 + 90)

        renderer.present()

        window.title = f'{TITLE} - time={pygame.time.get_ticks() / 1000:.2f}  fps={clock.get_fps():.2f}'
