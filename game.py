import pygame as pg
import pygame.font as pgfont

import client
import server
from function import *
import math
import copy

from openpyxl import load_workbook

class WorldRect():
	def __init__(self, xy, wh):
		self.x, self.y = copy.copy(xy)
		if type(wh) is pg.Rect:
			self.w, self.h = copy.copy(wh.w), copy.copy(wh.h)
		else:
			self.w, self.h = wh

	def set(self, iter):
		self.x = iter[0]
		self.y = iter[1]

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

# AABB Collision.
def CollideWorldRect(rect1: WorldRect, rect2: WorldRect):
	# Determine if a collision is happening
	if (
		rect1.left() < rect2.right() and
		rect1.right() > rect2.left() and
		rect1.top() < rect2.bottom() and
		rect1.bottom() > rect2.top()
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
		return closest, rect2

	return None, None

class Player(pg.sprite.Sprite):
	def __init__(self, screen, netplayer):
		pg.sprite.Sprite.__init__(self)
		self.netplayer = netplayer
		self.ticklist = []
		self.dir = [0,0]

		self.surf = pg.Surface((20, 20))
		self.rect = self.surf.get_rect()
		self.rect.center = screen.rect.center

		pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())

		self.location = WorldRect((100, -10),(self.rect))
		self.velocity = [0,0]

		self.jumping = False
		self.jumpframes = 0
		self.jumpmax = 20
		self.floored = False
		self.air = 0

	def update(self, screen, group, input):
		self.dir = [0, 0]
		while len(self.ticklist) != 0:
			t = self.ticklist[0]
			self.location.set(t["location"])
			self.velocity = t["velocity"]
			self.dir = t["dir"]
			self.ticklist.pop(0)

		key = {"left": 97, "up": 119, "down": 115, "right": 100}
		if not self.netplayer:
			if pg.key.get_pressed()[key["left"]]:
				self.dir[0] = -1
			if pg.key.get_pressed()[key["right"]]:
				self.dir[0] = 1
			if pg.key.get_pressed()[key["up"]]:
				self.dir[1] = -1
			if pg.key.get_pressed()[key["down"]]:
				self.dir[1] = 1

		# Friction
		self.velocity[0] *= .96

		# Will endlessly multiply little tiny floats that make the player move when they shouldnt be.
		if round(self.velocity[0], 1) == 0:
			self.velocity[0] = 0

		# Calculate Velocity and gravity
		self.velocity[0] = self.velocity[0] + (self.dir[0] / 4)
		self.velocity[1] = self.velocity[1] + (self.dir[1] / 4)

		# # Jumping off ground
		if pg.key.get_pressed()[key["up"]] and self.floored:
			self.jumping = True
			self.velocity[1] = -1
			self.jumpframes = 0

		# Jumping while not touching the ground
		elif pg.key.get_pressed()[key["up"]] and self.jumpframes != self.jumpmax and self.jumping:
			self.velocity[1] += -.5 *self.jumpframes
			self.jumpframes += 1

		# If falling
		else:
			# self.jumping = False
			self.velocity[1] += 1
			self.air += 1

		# Apply velocity
		self.velocity[1] = clamp(self.velocity[1], -15, 15)

		# Calculate next position.
		newloc = copy.copy(self.location)
		newloc.x, newloc.y  = (
			self.location.x + (self.velocity[0]),
			self.location.y + (self.velocity[1])
		)
		# print(newloc.y - self.location.y, group["world"])

		self.floored = False
		for i in group["world"]:
			# print(newloc.y, self.location.y)
			closest, rect2 = CollideWorldRect(newloc, i.location)
			if closest is not None:
				if closest == "top":
					newloc.y = rect2.y - newloc.h
					self.velocity[1] = 0
					self.floored = True

				elif closest == "bottom":
					newloc.y = rect2.bottom()
					self.velocity[1] = 0


				elif closest == "left":
					newloc.x = rect2.x - newloc.w
					self.velocity[0] = 0
				elif closest == "right":
					newloc.x = rect2.x + rect2.h
					self.velocity[0] = 0

		# Move to calculated new position
		self.location = newloc

		if not self.netplayer:
			# Update camera location
			screen.location = (
				-self.location.x + screen.rect.center[0],
				-self.location.y + screen.rect.center[1]
			)


def SumTup(a, b):
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
		pass


class Game:
	def __init__(self, screen, Forclient):
		if not Forclient:
			pg.display.set_caption(str("SERVER"))
			self.server = server.Server()
		else:
			pg.display.set_caption(str("CLIENT"))
		self.net = client.Network()
		import socket
		self.net.connect((socket.gethostname(), 5059))

		self.lastresponse = None


		self.group = {}
		self.group["player"] = []
		self.group["player"].append(Player(screen, False))

		self.group["entity"] = []



		self.group["world"] = []

		self.LoadMap()

	def LoadMap(self):
		loc = ("map.xlsx")

		wb = load_workbook(loc)
		ws = wb.active
		for row in range(0, ws.max_row):
			for i, col in enumerate(ws.iter_cols(1, ws.max_column)):
				if col[row].value == 1:
					self.group["world"].append(Tile((100, 100), (i*100, row*100)))


	def update(self, screen, group, input):
		if self.net.response != []: print(self.net.response)
		# Made in such a way that new ticks can come in while this process is happening.
		while self.net.response:
			res = self.net.response[0]
			print(res)

			if res.get("id"):
				id = res.get("id")
				self.client_id = id
				print("Client ID set to " + str(id))

			else:
				for client_id in self.net.response[0]: # For each client tick list
					ticklist = self.net.response[0].get(client_id)
					for tick in ticklist:
						for player in tick.get("netplayer"):
							print("Moving Netplayer")
							# Create netplayer
							if not self.group.get(client_id):
								self.group[client_id] = []
							if len(self.group.get(client_id)) == 0:
								self.group[client_id].append(Player(screen, True))
							# Pass tickdata to said netplayer for processing
							self.group[client_id][0].ticklist.append(
								tick.get("netplayer")[player]
							)


			self.net.response.pop(0)  # Tick has been processed, remove it from the list

		screen.surf.fill([121, 100, 100])
		for e in self.group.values():
			for tick in e:
				act = tick.update(screen, self.group, input)

				screen.surf.blit(
					tick.surf,
					SumTup(screen.location, tick.location.xy())
				)

		data = {}
		for i, p in enumerate(self.group["player"]):
			pdata = {"location": p.location.xy(), "velocity": p.velocity, "dir": p.dir}
			data["netplayer"] = {i: pdata}

		if self.lastresponse != data:
			self.net.send(data)
		self.lastresponse = data
