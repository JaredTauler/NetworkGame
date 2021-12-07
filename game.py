import pygame as pg
import pygame.font as pgfont
from function import *
import math

class Player:
	def __init__(self, screen):
		self.surf = pg.Surface((20, 20))
		self.rect = self.surf.get_rect()
		self.rect.center = screen.rect.center

		pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())

		self.location = (500, -200)
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
		# # Calculate next position.
		# newloc = (
		# 	self.location[0] + (self.velocity["x"]),
		# 	self.location[1] + (self.velocity["y"])
		# )
		# # Move to calculated new position
		# self.location = (
		# 	newloc[0],
		# 	newloc[1]
		# )
		#
		#
		# # a = SubTuple(self.rect, newloc)
		# # Update camera location
		# # screen.location = (
		# # 	self.rect[0] - newloc[0],
		# # 	self.rect[1] + newloc[1]
		# # )
		# screen.location(0,0)

		# Calculate next position.
		newloc = (
			self.location[0] + (self.velocity["x"]),
			self.location[1] + (self.velocity["y"])
		)
		# Move to calculated new position
		self.location = (newloc)
		self.rect = ToWorld(screen.location, self.location)


		# a = SubTuple(self.rect, newloc)
		# Update camera location
		# screen.location = (
		# 	self.rect[0] - newloc[0],
		# 	self.rect[1] + newloc[1]
		# )
		screen.location = (
			self.rect[0],
			self.rect[1]
		)
		screen.location = newloc
		print(screen.location)
		# print(newloc[0], self.rect[0], self.rect[1], newloc[1])

def ToWorld(a, b):
	return (
		a[0] + b[0],
		a[1] - b[1]
	)

class Tile():
	def __init__(self, size, loc):
		self.surf = pg.Surface(size)
		self.rect = self.surf.get_rect()
		self.location = loc

	def update(self, screen, group, input):
		# print(self.rect)
		self.rect = ToWorld(screen.location, self.location)
		# print(self.location, group["player"][0].location, screen.location)

class Game:
	def __init__(self, screen):
		self.group = {}
		self.group["player"] = []
		self.group["player"].append(Player(screen))
		self.group["entity"] = []



		self.group["world"] = []
		# self.group["world"].append(Tile((100, 100), (0,0)))
		self.group["world"].append(Tile((100, 100), (500, -200)))



	def update(self, screen, group, input):
		screen.surf.fill([121, 100, 100])
		for e in self.group.values():
			for obj in e:
				act = obj.update(screen, self.group, input)
				screen.surf.blit(obj.surf, obj.rect)
