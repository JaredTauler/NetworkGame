import json

import client
import server
import math


from openpyxl import load_workbook

from function import *

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
		if not self.netplayer:
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
		hit = {}
		# Check collision against collidable objects.
		for i in group["world"]:
			closest, rect2 = CollideWorldRect(newloc, i.location)
			if closest is not None: # If colliding
				if not hit.get(closest): hit[closest] = []
				hit[closest].append(
					(i, rect2)
				)

		# A ton of for loops but each only dealing with 1 or 2 objects.
		if hit.get("top"):
			for obj in hit["top"]:
				# This is to solve problem where player would get stuck on flat surfaces made of multipl tiles.
				if len(hit) >= 2: # If other sides were hit on other objects
					for list in hit:
						if list == "top": continue
						for i, obj2 in enumerate(hit[list]):
							a = lambda a: a[0].location.y # For readability.
							if a(obj) == a(obj2): # If they have the same Y value BUT are in diff lists
								hit[list].pop(i) # Ignore the collision

				newloc.y = obj[1].y - newloc.h
				self.velocity[1] = 0
				self.floored = True

		if hit.get("bottom"):
			for obj in hit["bottom"]:
				newloc.y = obj[1].bottom()
				self.velocity[1] = 0

		if hit.get("left"):
			for obj in hit["left"]:
				if self.velocity[0] > 0: # Check if moving towards side too. Will get stuck on corners if else.
					newloc.x = obj[1].x - newloc.w
					self.velocity[0] = 0

		if hit.get("right"):
			for obj in hit["right"]:
				if self.velocity[0] < 0:
					newloc.x = obj[1].x + obj[1].h
					self.velocity[0] = 0

		# Move to calculated new position
		self.location = newloc

		if not self.netplayer:
			# Update camera location
			screen.location = (
				-self.location.x + screen.rect.center[0],
				-self.location.y + screen.rect.center[1]
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
		# if self.net.response != []: print(self.net.response)
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
									self.group[client_id].append(Player(screen, True))
								# Pass tickdata to said netplayer for processing
								self.group[client_id][0].ticklist.append(
									tick.get("netplayer")[player]
								)

			self.net.response.pop(0)  # Tick has been processed, remove it from the list

		screen.surf.fill([121, 100, 100])
		# Update entities
		for e in self.group.values():
			for tick in e:
				act = tick.update(screen, self.group, input)

				screen.surf.blit(
					tick.surf,
					SumTup(screen.location, tick.location.xy())
				)

		# Send data to server
		data = {}
		for i, p in enumerate(self.group["player"]):
			pdata = {"location": p.location.xy(), "velocity": p.velocity, "dir": p.dir}
			data["netplayer"] = {i: pdata}

		# Dont send if already sent same data last time.
		if self.lastresponse != data:
			self.net.send(data)
		self.lastresponse = data
