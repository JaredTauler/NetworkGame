import pygame as pg
import pygame.font as pgfont
from function import *
import math

class WorldRect():
	def __init__(self, xy, wh):
		self.x, self.y = xy
		if type(wh) is pg.Rect:
			self.w, self.h = wh.w, wh.h
		else:
			self.w, self.h = wh

	def xy(self):
		return self.x, self.y
	def left(self):
		return self.x
	def right(self):
		return self.x + self.w
	def top(self):
		return self.y
	def bottom(self):
		return self.y + self.h

def CollideWorldRect(rect1: WorldRect, rect2: WorldRect):
	# Determine if a collision is happening
	if (
		rect1.x < rect2.x + rect2.w and
		rect1.x + rect1.w > rect2.x and
		rect1.y < rect2.y + rect2.h and
		rect1.h + rect1.y > rect2.y
	):
		# OK. collision is happening, which side is closest?
		side = {
			"left": abs(rect1.right() - rect2.left()), # left
			"top": abs(rect1.bottom() - rect2.top()), # top
			"right": abs(rect1.left() - rect2.right()), # right
			"bottom": abs(rect1.top() - rect2.bottom()) # bottom
		}

		# Determine which is closest just by comparing
		closest = "top"
		for i in side.keys():
			if side[i] < side[closest]:
				closest = i
		print(closest)
		return closest, rect2

	return None, None

class Player(pg.sprite.Sprite):
	def __init__(self, screen):
		pg.sprite.Sprite.__init__(self)
		self.surf = pg.Surface((20, 20))
		self.rect = self.surf.get_rect()
		self.rect.center = screen.rect.center

		pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())

		self.location = WorldRect((100, -10),(self.rect))
		self.velocity = {"x": 0, "y": 0}

		self.jumping = False
		self.jumpframes = 0
		self.jumpmax = 20
		self.floored = False
		self.air = 0

	def update(self, screen, group, input):
		key = {"left": 97, "up": 119, "down": 115, "right": 100}
		Dir = {"x": 0, "y": 0}
		if pg.key.get_pressed()[key["left"]]:
			Dir["x"] = -1
		if pg.key.get_pressed()[key["right"]]:
			Dir["x"] = 1
		if pg.key.get_pressed()[key["up"]]:
			Dir["y"] = -1
		if pg.key.get_pressed()[key["down"]]:
			Dir["y"] = 1

		# Friction
		self.velocity["x"] *= .96

		# Will endlessly multiply little tiny floats that make the player move when they shouldnt be.
		if round(self.velocity["x"], 1) == 0:
			self.velocity["x"] = 0

		# Calculate Velocity and gravity
		self.velocity["x"] = self.velocity["x"] + (Dir["x"] / 4)
		self.velocity["y"] = self.velocity["y"] + (Dir["y"] / 4)

		# # Jumping off ground
		# if pg.key.get_pressed()[key["up"]] and self.floored:
		# 	print("BRUH")
		# 	self.jumping = True
		# 	self.velocity["y"] = -1
		# 	self.jumpframes = 0
		# # Jumping while not touching the ground
		# elif pg.key.get_pressed()[key["up"]] and self.jumpframes != self.jumpmax and self.jumping:
		# 	self.velocity["y"] += -3*self.jumpframes
		# 	self.jumpframes += 1
		# # If falling
		# else:
		# 	# self.jumping = False
		# 	self.velocity["y"] += 1
		# 	self.air += 1
		#
		# # Apply velocity
		# self.velocity["y"] = clamp(self.velocity["y"] + (1 / 60)/2, -15, 15)

		# Calculate next position.
		newloc = self.location
		newloc.x, newloc.y  = (
			self.location.x + (self.velocity["x"]),
			self.location.y + (self.velocity["y"])
		)

		self.floored = False
		for i in group["world"]:
			closest, rect2 = CollideWorldRect(newloc, i.location)
			if closest is not None:
				print("BRUUUUUH")
				if closest == "top":
					print(newloc.y)
					newloc.y = rect2.y - newloc.h
					self.velocity["y"] = 0
					self.floored = True
					print(newloc.y)

				elif closest == "bottom":
					newloc.y = rect2.bottom()
					self.velocity["y"] = 0


				elif closest == "left":
					newloc.x = rect2.x - newloc.w
					self.velocity["x"] = 0
				elif closest == "right":
					newloc.x = rect2.x + rect2.h
					self.velocity["x"] = 0

		# Move to calculated new position

		self.location = newloc
		self.rect[0], self.rect[1] = ToWorld(screen.location, self.location.xy())


		# Update camera location
		pg.display.set_caption(str(screen.location))
		screen.location = (
			-newloc.x + screen.rect.center[0],
			-newloc.y + screen.rect.center[1]
		)
		# print(geometry.collide())


def ToWorld(a, b):
	return (
		a[0] + b[0],
		a[1] + b[1]
	)

class Tile(pg.sprite.Sprite):
	def __init__(self, size, loc):
		pg.sprite.Sprite.__init__(self)
		self.surf = pg.Surface(size)
		self.rect = self.surf.get_rect()
		self.location = WorldRect(loc, self.rect)

	def update(self, screen, group, input):
		# print(self.rect)
		self.rect[0], self.rect[1] = ToWorld(screen.location, self.location.xy())
		# print(self.location, group["player"][0].location, screen.location)

class Game:
	def __init__(self, screen):
		self.group = {}
		self.group["player"] = []
		self.group["player"].append(Player(screen))
		self.group["entity"] = []



		self.group["world"] = []
		# self.group["world"].append(Tile((100, 100), (0,0)))
		self.group["world"].append(Tile((100, 100), (100, 100)))
		# self.group["world"].append(Tile((100, 100), (100, 300)))
		# self.group["world"].append(Tile((100, 100), (300, 300)))



	def update(self, screen, group, input):
		screen.surf.fill([121, 100, 100])
		for e in self.group.values():
			for obj in e:
				act = obj.update(screen, self.group, input)
				screen.surf.blit(obj.surf, obj.rect)
