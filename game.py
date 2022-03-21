import json

import pygame
import pygame.draw
import pygame.gfxdraw as gfx
import client
# import game
import server
from timer import Timer
t = Timer()
import pytmx
import xml.etree.ElementTree as ET

import pymunk as pm

from function import *

# class Bomb():
# 	def __init__(self, parent, space):
# 		self.body = pm.Body()
# 		self.body.position = (100,100)
# 		self.radius = 20
# 		self.shape = pm.Circle(self.body, self.radius)
# 		self.shape.density = 1
# 		self.shape.friction = 1
# 		self.shape.elasticity = .3
# 		space.add(self.body, self.shape)
# 		self.shape.collision_type = 1
#
# 		# self.surf = pg.image.load("bomb")
# 		self.surf = pg.transform.scale(
# 			pg.image.load("map/map1/bomb.png"),
# 			(self.radius*2, self.radius*2)
# 		)
# 		self.surf.set_colorkey((0, 0, 0))
#
# 	def draw(self, screen, space):
#
# 		loc = SumTup(self.shape.body.position, screen.location)
# 		x = int(loc[0]-self.radius)
# 		y = int(loc[1] - self.radius)
# 		screen.surf.blit(
# 			rot_center(self.surf, self.body.angle, 0, 0)[0],
# 			(x,y)
# 		)
#
# 	def update(self, screen, group, input, space):
# 		print(self.shape.body.position)
# 		self.draw(screen, space)
#
# class Projectile():
# 	def __init__(self, parent, space):
# 		self.body = pm.Body()
# 		self.body.position = (100,100)
# 		self.radius = 20
# 		self.shape = pm.Circle(self.body, self.radius)
# 		self.shape.density = 1
# 		self.shape.friction = 1
# 		self.shape.elasticity = .3
# 		space.add(self.body, self.shape)
# 		self.shape.collision_type = 1
#
# 	def update(self, screen, group, input, space):
# 		pass
# 		# print(self.shape.body.position)
# 		# self.draw(screen, space)


class Player():
	def __init__(self, screen, space, netplayer):
		# net
		self.netplayer = netplayer
		self.ticklist = []

		# pm
		self.body = pm.Body()
		self.body.position = (100,100)
		self.shape = pm.Poly.create_box(self.body, (30,30))
		self.shape.density = 1
		self.shape.friction = 1
		self.shape.elasticity = .3
		space.add(self.body, self.shape)
		self.shape.collision_type = 1

	def update(self, screen, group, input, space):

		while len(self.ticklist) != 0:
			t = self.ticklist[0]
			self.body.position = t["location"]
			self.body.velocity = t["velocity"]
			self.ticklist.pop(0)
			# print("BRUH")
		key = {"left": 97, "up": 119, "down": 115, "right": 100, "action": 102}
		dir = [0,0]
		action = False
		if not self.netplayer:
			if pg.key.get_pressed()[key["left"]]:
				dir = SumTup(dir, (-1, 0))
			if pg.key.get_pressed()[key["right"]]:
				dir = SumTup(dir, (1, 0))
			if pg.key.get_pressed()[key["up"]]:
				dir = SumTup(dir, (0, -1))
			if pg.key.get_pressed()[key["down"]]:
				dir = SumTup(dir, (0, 1))
			if pg.key.get_pressed()[key["action"]]:
				action = True

		# if action:
		# 	group["entity"].append(Bomb(self, space))

		mvspd = .2
		self.body.velocity = SumTup((dir[0]*mvspd, dir[1]*mvspd), self.body.velocity)

		if not self.netplayer:
			# Update camera location
			screen.location = (
				-self.body.position.x + screen.rect.center[0],
				-self.body.position.y + screen.rect.center[1]
			)

		# pg.draw.polygon(screen.surf, [255, 0, 0], verts(self.shape, screen))
		x = int(self.shape.body.position[0] + screen.location[0])
		y = int(self.shape.body.position[1] + screen.location[1])
		pygame.draw.rect(
			screen.surf,
			[255, 255, 255],
			(x, y, 30, 30)
		)


# Tiles
class TileLayer():
	def __init__(self):
		self.tiles = []
		self.tilemap = {}
		# self.surf = pg.Surface((10000, 10000))

	def draw(self, screen, space):
		# return
		for tile in self.tiles:
			# if overlap(  # blit if screen is overlapping rectangle
			# 		(
			# 				(-screen.location[0], -screen.location[1]),
			# 				(screen.rect.w, screen.rect.h)
			# 		),
			# 		(tile.shape.body.position, (60, 60))
			# ):
			# try:
				x = int(tile.shape.body.position[0] + screen.location[0])
				y = int(tile.shape.body.position[1] + screen.location[1])
				# x = int( +screen.location[0])
				# y = int( -screen.location[1])
				# gfx.textured_polygon(
				# 	screen.surf,
				# 	verts(tile.shape, screen),
				# 	self.tilemap[tile.textureid],
				# 	x, y
				# )
				# gfx.polygon(
				#
				# )
				# gfx.filled_polygon(
				# 	screen.surf,
				# 	verts(tile.shape, screen),
				# 	[0, 0, 0]
				# )
				# print()
				pygame.draw.rect(
					screen.surf,
					[255,255,255],
					(x, y, 30, *30)
				)
				# print(verts(tile.shape, screen))
				pass
			# except:
			# 	pass

	def update(self, screen, group, input, space):
		self.draw(screen, space)


class Tile(pg.sprite.Sprite):
	def __init__(self, size, loc, space, textureid):
		pg.sprite.Sprite.__init__(self)
		# textures make game slow. idk why.
		self.textureid = textureid # Remember texture ID rather than texture
		# pm
		self.body = pm.Body(body_type=pm.Body.STATIC)
		self.body.position = loc
		self.shape = pm.Poly.create_box(self.body, size)
		self.shape.density = 1
		self.shape.elasticity = 1
		space.add(self.body, self.shape)
		self.shape.collision_type = 1




class BG:
	def __init__(self, bg):
		dir = "map/map1/"
		img = pg.image.load(dir + bg).convert()

		self.surf = pg.transform.scale(img, (1800,1800))

	def draw(self, screen, space):
		x = int(screen.location[0] * .3)
		y = int(screen.location[1] * .3)
		screen.surf.blit(self.surf, (x,y))

	def update(self, screen, group, input, space):
		self.draw(screen, space)

class Game:

	def LoadMap(self, TL, space):
		dir = "map/map1/"  # base dir from which files being getten from.

		# PARSE TSX FILE
		tree = ET.parse(dir + "base.tsx")
		root = tree.getroot()
		tiles = {}  # surfs
		for child in root:  # For elem in XML
			if child.tag == "tile":  # Make sure getting a tile
				for i in child:
					loc = dir + i.attrib["source"]
					surf = pygame.image.load(dir + i.attrib["source"]).convert()
					tiles[int(child.attrib["id"]) + 1] = surf
		TL.tilemap = tiles
		tm = pytmx.load_pygame(dir + ".tmx")  # FIXME stop this from auto loading images... ill do it myself thank you.
		for x, y, gid, in tm.get_layer_by_name("terrain"):
			# print(gid)
			if gid == 0:
				continue
			n = 30
			TL.tiles.append(Tile((n, n), (x * n, y * n), space, gid))

	def __init__(self, screen, Forclient):
		self.screen = screen

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

		self.Terrain = TileLayer()
		self.LoadMap(self.Terrain, self.space)
		bg = BG("bg.png")

		self.group = {}


		self.group["world"] = []
		self.group["world"].append(bg)
		self.group["world"].append(self.Terrain)

		self.group["player"] = []
		self.group["player"].append(Player(screen, self.space, False))
		self.group["entity"] = []

	def processtick(self, screen):
		if self.net.response != []:
			# print(self.net.response)
			pass
		# Made in such a way that new ticks can come in while this process is happening.
		while self.net.response:
			for res in self.net.response[0]: # First response in list of responses
				for client_id in res: # Process each computers info seperate
					# Finally processing ticks.
					for tick in res[client_id]:
						# print(tick)
						if type(tick) is str:
							tick = json.loads(tick)
						if client_id == "0":
							if res.get("id"):
								id = res.get("id")
								self.client_id = id
								print("Client ID set to " + str(id))
						else:
							for player in tick.get("netplayer"): # If client has more than 1 player
								# print("Moving Netplayer")
								# Create netplayer
								if not self.group.get(client_id):
									self.group[client_id] = []
								if len(self.group.get(client_id)) == 0:
									self.group[client_id].append(Player(screen, self.space, True))
								# Pass tickdata to said netplayer for processing
								self.group[client_id][0].ticklist.append(
									tick.get("netplayer")[player]
								)

			self.net.response.pop(0)  # Tick has been processed, remove it from the list

	def toserver(self):
		# Send data to server
		data = {}
		for i, p in enumerate(self.group["player"]):
			pdata = {"location": p.body.position, "velocity": p.body.velocity}
			data["netplayer"] = {i: pdata}

		# Dont send if already sent same data last time.
		if self.lastresponse != data:
			self.net.send(data)
		self.lastresponse = data

	def update(self, screen, group, input):
		# self.processtick(screen) # Process ticks
		self.space.step(1) # Step pymunk sim


		# Update entities
		# t.start()
		for e in self.group.values():
			for obj in e:
				obj.update(screen, self.group, input, self.space)
		# t.stop()

		# self.toserver()
