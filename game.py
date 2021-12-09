import pygame as pg
import pygame.font as pgfont
from function import *
import math
import os

class Player(pg.sprite.Sprite):
	def __init__(self, screen):
		pg.sprite.Sprite.__init__(self)
		self.surf = pg.Surface((20, 20))
		self.rect = self.surf.get_rect()
		self.rect.center = screen.rect.center

		pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())

		self.location = (500, 200)
		self.velocity = {"x": 0, "y": 0}

	def update(self, screen, group, input):
		key = {"left": 97, "up": 119, "down": 115, "right": 100}
		Dir = {"x": 0, "y": 0}
		if pg.key.get_pressed()[key["left"]]:
			Dir["x"] = -1
		if pg.key.get_pressed()[key["right"]]:
			Dir["x"] = 1
		if pg.key.get_pressed()[key["up"]]:
			Dir["y"] = 1
		if pg.key.get_pressed()[key["down"]]:
			Dir["y"] = -1

		# Friction
		self.velocity["x"] *= .96
		self.velocity["y"] *= .96

		# Will endlessly multiply little tiny floats that make the player move when they shouldnt be.
		if round(self.velocity["x"], 1) == 0:
			self.velocity["x"] = 0
		if round(self.velocity["y"], 1) == 0:
			self.velocity["y"] = 0

		# Calculate Velocity
		self.velocity["x"] = self.velocity["x"] + (Dir["x"] / 4)
		self.velocity["y"] = self.velocity["y"] + (Dir["y"] / 4)

		# Calculate next position.
		newloc = (
			self.location[0] + (self.velocity["x"]),
			self.location[1] + (self.velocity["y"])
		)

		# Collision (evil)
		# Use location in the world, not rect location. rect location is for drawing only.
		# AABB collision: only rectangles.
		def parse(n):
			rect = {
				"x": n.location[0], "y": n.location[1],
				"w": n.rect[2], "h": n.rect[3]
			}
			side = {}
			side["left"] = rect["x"] # x
			side["right"] = rect['x'] + rect['w'] # x + width
			side["top"] = rect['y'] # y
			side["bottom"] = rect['y'] + rect['h']
			return rect, side
		rect1, side1 =  parse(self)
		rect2, side2 =  parse(group["world"][0])
		os.system('cls')
		print(rect1, rect2)
		print(rect1["x"] < rect2["x"] + rect2["w"],
			  rect1["x"] + rect1["w"] > rect2["x"],
			  rect1["y"] < rect2["y"] + rect2["h"],
			  rect1["y"] + rect1["h"] > rect2["y"]

		)
		# print(a["left"] >= b["right"])

		# print(a, b)



		# Move to calculated new position
		self.location = newloc
		self.rect[0], self.rect[1] = ToWorld(screen.location, self.location)


		# Update camera location
		pg.display.set_caption(str(screen.location))
		screen.location = (
			-newloc[0] + screen.rect.center[0],
			newloc[1]+ screen.rect.center[1]
		)
		# print(pg.surfarray.pixels2d(self.surf))
		# print(geometry.collide())


def ToWorld(a, b):
	return (
		a[0] + b[0],
		a[1] - b[1]
	)

class Tile(pg.sprite.Sprite):
	def __init__(self, size, loc):
		pg.sprite.Sprite.__init__(self)
		self.surf = pg.Surface(size)
		self.rect = self.surf.get_rect()
		self.location = loc

	def update(self, screen, group, input):
		# print(self.rect)
		self.rect[0], self.rect[1] = ToWorld(screen.location, self.location)
		# print(self.location, group["player"][0].location, screen.location)

class Game:
	def __init__(self, screen):
		self.group = {}
		self.group["player"] = []
		self.group["player"].append(Player(screen))
		self.group["entity"] = []



		self.group["world"] = []
		# self.group["world"].append(Tile((100, 100), (0,0)))
		self.group["world"].append(Tile((100, 100), (500, 200)))



	def update(self, screen, group, input):
		screen.surf.fill([121, 100, 100])
		for e in self.group.values():
			for obj in e:
				act = obj.update(screen, self.group, input)
				screen.surf.blit(obj.surf, obj.rect)
