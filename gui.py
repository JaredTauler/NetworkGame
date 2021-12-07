import pygame
import pygame as pg
import pygame.font as pgfont
from function import *
import math

def SurfCenter(s1, s2):
    return (
        s1.get_rect().center[0] - s2.get_rect().center[0],
        s1.get_rect().center[1] - s2.get_rect().center[1]
    )

def MouseOver(r):
    m = pg.mouse.get_pos()
    return (
        m[0] in range(r.x, r.width + r.x)
        and
        m[1] in range(r.y, r.height + r.y)
    )


class ClassButton():
    def __init__(self, surf, rect, render, font, trigger):
        self.surf = pg.Surface(surf, pygame.SRCALPHA)
        self.rect = self.surf.get_rect()
        self.rect.x = rect[0]
        self.rect.y = rect[1]

        self.trigger = trigger

        self.color = [255, 0, 0]
        self.fade = 10
        self.fadeindex = 0
        self.render=render
        self.font =font


    def update(self, screen, Input):
        def FadeMath(color):
            if self.fadeindex != 0:
                h = RangeChange(
                    (0, self.fade),
                    (0, 1),
                    self.fadeindex
                )

                a = 1  # max
                b = 1
                k = 0  # min
                mod = ((a * math.sin((h / b))) + k)
                return clamp(
                    255 - (mod * 100),
                    0, 255
                )
            return color

        Return = False
        if MouseOver(self.rect):
            for i in Input.get("mouse"):
                if i.__dict__.get("button") == 1:
                    return self.trigger
            if self.fadeindex < self.fade:
                self.fadeindex += 1

        else:
            if self.fadeindex > 0:
                self.fadeindex -= 1

        pg.draw.rect(
            self.surf,
            [FadeMath(255), 0, 0],
            self.surf.get_rect(),
            border_radius=20
        )

        font = pg.font.SysFont("calibri", 18)

        text = self.font.render(
                self.render["text"],
                self.render["antialias"],
                self.render["color"],
            )

        self.surf.blit(
            text,
            (SurfCenter(self.surf, text))
        )
        screen.surf.blit(self.surf, self.rect)


class MainMenu:
    def __init__(self, screen):
        # self.surf = pg.Surface(surf)
        # self.rect = self.surf.get_rect()
        self.elem = {}

        font = pg.font.SysFont("calibri", 100)

        render = {
            "text": "Host",
            "color": (255, 255, 255),
            "antialias": True,
        }
        self.elem["host"] = ClassButton(
            (200, 100), (100, 0), render, font, trigger="host"
        )

        render = {
            "text": "Join",
            "color": (255, 255, 255),
            "antialias": True,
        }
        self.elem["join"] = ClassButton(
            (200, 100), (100, 100), render, font, trigger="join"
        )

        render = {
            "text": "Options",
            "color": (255, 255, 255),
            "antialias": True,
        }
        self.elem["options"] = ClassButton(
            (400, 100), (100, 200), render, font, trigger="options"
        )

        render = {
            "text": "Exit",
            "color": (255, 255, 255),
            "antialias": True,
        }
        self.elem["exit"] = ClassButton(
            (200, 100), (100, 300), render, font, trigger="exit"
        )

    def update(self, screen, group, Input):
        screen.surf.fill([121, 100, 100])
        for e in self.elem.values():
            act = e.update(screen, Input)
            if act != None:
                if act == "join":
                    group["gui"][0] = JoinMenu(screen) # replace self with join menu
                    return

class JoinMenu:
    def __init__(self, screen):
        # self.surf = pg.Surface(surf)
        # self.rect = self.surf.get_rect()
        self.elem = {}

        font = pg.font.SysFont("calibri", 100)

        render = {
            "text": "Hi",
            "color": (255, 255, 255),
            "antialias": True,
        }
        self.elem["host"] = ClassButton(
            (400, 300), (100, 32), render, font, trigger="host"
        )

        render = {
            "text": "Join",
            "color": (255, 255, 255),
            "antialias": True,
        }
        self.elem["join"] = ClassButton(
            (400, 300), (100, 400), render, font, trigger="join"
        )

    def update(self, screen, group, input):
        screen.surf.fill([121, 100, 100])
        for e in self.elem.values():
            act = e.update(screen, input)
            if act != None:
                if act == "join":
                    pass
