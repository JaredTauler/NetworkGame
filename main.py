import math
from function import *

import pygame as pg
from pygame.locals import (
    MOUSEBUTTONDOWN,
    KEYDOWN,
    KEYUP,
    QUIT
)

class Player():
    def __init__(self):
        pass

class ClassPlayArea():
    def __init__(self, surfsize):
        self.surf = pg.Surface(surfsize)
        self.rect = self.surf.get_rect()

def EventHandle():
    input = {}
    input["key"] = []
    input["mouse"] = []
    for event in pg.event.get():
        # if event.type == pg.USEREVENT:
        #     frame += 1
        if event.type in [KEYDOWN, KEYUP]:
            input["key"].append(event)
        elif event.type == MOUSEBUTTONDOWN:
            input["mouse"].append(event)
        elif event.type == QUIT:
            quit()
    return input

pg.init()

SCREEN = pg.display.set_mode((1200, 800))
CLOCK = pg.time.Clock()

GROUP = {}
GROUP["gui"] = {}
GROUP["entity"] = {}

PLAYAREA = [ClassPlayArea((1000, 1000))]
from gui import * # Have to import after i declare constants.

# Initial GUI menu.
GROUP["gui"][0] = MainMenu(PLAYAREA[0])
while True:
    input = EventHandle()

    keys = pg.key.get_pressed()  # checking pressed keys

    # Update Everything.
    for g in GROUP.values():
        for obj in g.values():
            obj.update(PLAYAREA[0], GROUP, input)

    SCREEN.blit(PLAYAREA[0].surf, (0,0))
    pg.display.set_caption(str(CLOCK.get_fps()))
    pg.display.update()
    CLOCK.tick(60)

