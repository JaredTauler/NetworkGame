import json

import pygame.draw
import pymunk

import client
import server
import math

import pymunk as pm
from openpyxl import load_workbook

from function import *

def spacestate(space):
	print_options = pymunk.SpaceDebugDrawOptions()
	space.debug_draw(print_options)

class Player(pg.sprite.Sprite):

	def __init__(self, screen, netplayer, space):
		pg.sprite.Sprite.__init__(self)
		# net
		self.netplayer = netplayer
		self.ticklist = []

		# pm
		self.body = pm.Body()
		self.body.position = (100,100)
		self.shape = pm.Poly.create_box(self.body, (30,30))
		self.shape.density = 10
		self.shape.elasticity = 1
		space.add(self.body, self.shape)
		self.shape.collision_type = 1

		# pg
		self.surf = pg.Surface((20, 20))
		self.rect = self.surf.get_rect()
		self.rect.center = screen.rect.center

		pg.draw.rect(self.surf, (255, 0, 0), self.surf.get_rect())


	def update(self, screen, group, input, space):

		while len(self.ticklist) != 0:
			t = self.ticklist[0]
			self.body.position = t["location"]
			self.body.velocity = t["velocity"]
			self.ticklist.pop(0)
			print("BRUH")

		key = {"left": 97, "up": 119, "down": 115, "right": 100}
		dir = [0,0]
		if not self.netplayer:
			if pg.key.get_pressed()[key["left"]]:
				dir = SumTup(dir, (-1, 0))
			if pg.key.get_pressed()[key["right"]]:
				dir = SumTup(dir, (1, 0))
			if pg.key.get_pressed()[key["up"]]:
				dir = SumTup(dir, (0, -1))
			if pg.key.get_pressed()[key["down"]]:
				dir = SumTup(dir, (0, 1))
		mvspd = .2
		self.body.velocity = SumTup((dir[0]*mvspd, dir[1]*mvspd), self.body.velocity)

		if not self.netplayer:
			# Update camera location
			screen.location = (
				-self.body.position.x + screen.rect.center[0],
				-self.body.position.y + screen.rect.center[1]
			)

class Tile(pg.sprite.Sprite):
	def __init__(self, size, loc, space):
		pg.sprite.Sprite.__init__(self)
		self.surf = pg.Surface(size)
		# self.rect = self.surf.get_rect()
		# self.location = WorldRect(loc, self.rect)

		# pm
		self.body = pm.Body(body_type=pm.Body.STATIC)
		self.body.position = loc
		self.shape = pm.Poly.create_box(self.body, size)
		self.shape.density = 1
		self.shape.elasticity = 1
		space.add(self.body, self.shape)
		self.shape.collision_type = 1


	def update(self, screen, group, input, space):
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

		self.space = pm.Space()  # PyMunk simulation
		self.space.gravity = (0, .1)
		self.group = {}
		self.group["player"] = []
		self.group["player"].append(Player(screen, False, self.space))

		self.group["entity"] = []

		self.group["world"] = []

		self.LoadMap()

	def LoadMap(self):
		# self.group["world"].append(Tile((40, 40), (0,0), self.space))
		loc = ("map.xlsx")

		wb = load_workbook(loc)
		ws = wb.active
		m = 70
		for row in range(0, ws.max_row):
			for i, col in enumerate(ws.iter_cols(1, ws.max_column)):
				if col[row].value == 1:
					self.group["world"].append(Tile((m, m), (i*m, row*m), self.space))


	def update(self, screen, group, input):
		if self.net.response != []: print(self.net.response)
		# Made in such a way that new ticks can come in while this process is happening.
		while self.net.response:
			for res in self.net.response[0]: # First response in list of responses
				for client_id in res: # Process each computers info seperate
					# Finally processing ticks.
					for tick in res[client_id]:
						print(tick)
						if type(tick) is str:
							tick = json.loads(tick)
						if client_id == "0":
							if res.get("id"):
								id = res.get("id")
								self.client_id = id
								print("Client ID set to " + str(id))
						else:
							for player in tick.get("netplayer"): # If client has more than 1 player
								print("Moving Netplayer")
								# Create netplayer
								if not self.group.get(client_id):
									self.group[client_id] = []
								if len(self.group.get(client_id)) == 0:
									self.group[client_id].append(Player(screen, True, self.space))
								# Pass tickdata to said netplayer for processing
								self.group[client_id][0].ticklist.append(
									tick.get("netplayer")[player]
								)

			self.net.response.pop(0)  # Tick has been processed, remove it from the list

		# Step pymunk sim
		self.space.step(1)

		screen.surf.fill([121, 100, 100])
		# Update entities
		for e in self.group.values():
			for tick in e:
				act = tick.update(screen, self.group, input, self.space)

				def draw_poly(shape):
					verts = []
					for v in shape.get_vertices():
						a = SumTup(screen.location, shape.body.position)
						x = v.rotated(shape.body.angle)[0] + a[0]
						y = v.rotated(shape.body.angle)[1] + a[1]
						verts.append((x, y))
					pygame.draw.polygon(screen.surf, [255, 255, 255], verts)
				draw_poly(tick.shape)

		# Send data to server
		data = {}
		for i, p in enumerate(self.group["player"]):
			pdata = {"location": p.body.position, "velocity": p.body.velocity}
			data["netplayer"] = {i: pdata}

		# Dont send if already sent same data last time.
		if self.lastresponse != data:
			self.net.send(data)
		self.lastresponse = data
