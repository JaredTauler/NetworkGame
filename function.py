import copy
import pygame as pg

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def RangeChange(Old, New, val):
    OldRange = (Old[1] - Old[0])
    NewRange = (New[1] - New[0])
    return (((val - Old[0]) * NewRange) / OldRange) + Old[0]


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

def SumTup(a, b):
	return (
		a[0] + b[0],
		a[1] + b[1]
	)

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
