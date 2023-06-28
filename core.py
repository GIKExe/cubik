
class Rect:
	def __init__(self, pos, size):
		self.pos = list(pos)
		self.size = list(size)

	@property
	def left(self): return self.pos[0]
	@left.setter
	def left(self, value): self.pos[0] = value

	@property
	def top(self): return self.pos[1]
	@top.setter
	def top(self, value): self.pos[1] = value

	@property
	def width(self): return self.size[0]
	@width.setter
	def width(self, value): self.size[0] = value

	@property
	def height(self): return self.size[1]
	@height.setter
	def height(self, value): self.size[1] = value

	@property
	def right(self): return self.left + self.width
	@right.setter
	def right(self, value): self.left = value - self.width

	@property
	def bottom(self): return self.top + self.height
	@bottom.setter
	def bottom(self, value): self.top = value - self.height


import pygame
from pygame import draw, display, Rect
from pygame.locals import *

import utils
import time

from threading import Thread


class Base:
	rect = None
	def draw(self, *args, **kwargs): pass
	def tick(self, *args, **kwargs): pass


class DebugInfo:
	def __init__(self, info):
		self.rect = None
		self.show = False
		self.font = utils.get_font("arial", 15)
		self.info = info

	def tick(*args, **kwargs):
		pass

	def draw(self, camera, offset):
		if self.show:
			lines = self.info().split("\n")
			y = 0
			for text in lines:
				surf = self.font.render(text, True, (250,250,250))
				camera.win.blit(surf,(0,y))
				y += surf.get_height()
			draw.line(camera.win,(250,0,0),(256,0),(256,512))
			draw.line(camera.win,(250,0,0),(512,256),(0,256))


class Player:
	def __init__(self, app, x, y, speed, gravity, jumpPower):
		self.app = app
		self.rect = Rect(x,y,16,16)
		self.moving = [0,0]
		self.gravity = gravity
		self.speed = speed
		self.isJump = False
		self.jumpPower = jumpPower
		self.jumpCount = self.jumpPower
		self.onGround = True
		self.spawnPos = (x, y)
		self.effects = []

	def respawn(self):
		self.rect.topleft = self.spawnPos

	def draw(self, camera, offset):
		# data = self.app.map.get_neighbors(self.rect.topleft)
		for spos in self.app.map.sposs:
			sx, sy = spos
			draw.rect(
				camera.win, 
				(200,0,200),
				(
					(self.rect.x//16+sx)*16+offset[0],
					(self.rect.y//16+sy)*16+offset[1],
					16, 16
				),
				1
			)

		# draw.rect(
		# 	camera.win, 
		# 	(200,0,200),
		# 	(
		# 		(self.rect.x//16)*16+offset[0],
		# 		(self.rect.y//16+1)*16+offset[1],
		# 		self.rect.width,
		# 		self.rect.height
		# 	),
		# 	2
		# )

		draw.rect(
			camera.win, 
			(200,200,200),
			(
				self.rect.x+offset[0],
				self.rect.y+offset[1],
				self.rect.width,
				self.rect.height
			)
		)

	def collision(self, cam, type):
		c = cam.collide(self)
		if type == "y":
			self.onGround = False
		if c:
			if hasattr(c,"on_collide"):
				c.on_collide(self)

			if type == "x":
				if self.moving[0] > 0:
					self.rect.right = c.rect.left
				elif self.moving[0] < 0:
					self.rect.left = c.rect.right

			if type == "y":
				if self.moving[1] > 0:
					self.rect.bottom = c.rect.top
					self.onGround = True
				elif self.moving[1] < 0:
					self.rect.top = c.rect.bottom

			elif type == "g":
				if self.gravity > 0:
					self.rect.bottom = c.rect.top
					self.onGround = True
				elif self.gravity < 0:
					self.rect.top = c.rect.bottom

	def tick(self, camera):
		self.rect.x += self.moving[0] * self.speed
		self.collision(camera,"x")

		self.rect.y += self.moving[1] * self.speed
		self.collision(camera,"y")
		
		self.rect.y += self.gravity
		self.collision(camera,"g")
		
		if self.isJump:
			if self.jumpCount > 0:
				self.rect.y -= self.jumpCount * 0.225
				self.collision(camera, "g")
				self.jumpCount -= 1
			else:
				self.isJump = False
				self.jumpCount = self.jumpPower


class Map:
	def __init__(self, app, diagonally=True):
		self.app = app
		self.table = {}
		self.data = {}
		if diagonally:
			self.sposs = [(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)]
		else:
			self.sposs = [(0,1),(1,0),(0,-1),(-1,0)]

	def get_neighbors(self, pos):
		x, y = pos
		x = int(x//16)
		y = int(y//16)
		res = {}

		for spos in self.sposs:
			sx, sy = spos
			pos = (x+sx, y+sy)
			if pos in self.data:
				res[spos] = self.data[pos]

		return res


class Camera:
	def __init__(self, app, background=(25,25,25), smooth=0.125):
		self.app = app
		self.win = app.win

		width, height = self.win.get_size()
		# self.offset = [256,256]
		self.offset = [width//2, height//2]
		self.objs = []
		self.background = background
		self.smooth = smooth

		# временное имя
		self.block_table = {}

	def collide(self, a):
		for b in self.objs:
			if a != b and b.rect != None \
				and a.rect.colliderect(b.rect):
				return b
		return None

	def __iadd__(self, obj):
		self.objs.append(obj)
		return self

	def add_block(self, id, *args, **kwargs):
		block = self.block_table[id](*args, **kwargs)
		self.objs.append(block)
		return block

	def draw(self):
		self.win.fill(self.background)

		for obj in list(self.app.map.data.values()):
			if ((obj.rect.right+self.offset[0] > 0) and \
					(obj.rect.x+self.offset[0] < self.win.get_width()) and \
					(obj.rect.bottom+self.offset[1] > 0) and \
					(obj.rect.y+self.offset[1] < self.win.get_height())):
				obj.draw(self, self.offset)
			obj.tick(self)

		for obj in self.objs:
			if obj.rect == None or ((obj.rect.right+self.offset[0] > 0) and \
					(obj.rect.x+self.offset[0] < self.win.get_width()) and \
					(obj.rect.bottom+self.offset[1] > 0) and \
					(obj.rect.y+self.offset[1] < self.win.get_height())):
				obj.draw(self, self.offset)
			obj.tick(self)

	def offset_lerp(self, pos):
		width, height = self.win.get_size()

		# self.offset = [
		# 	lerp(self.offset[0],256-pos[0],self.smooth),
		# 	lerp(self.offset[1],256-pos[1],self.smooth)
		# ]

		self.offset = [
			lerp(self.offset[0], width//2-pos[0], self.smooth),
			lerp(self.offset[1], height//2-pos[1], self.smooth)
		]


def lerp(a, b, t):
	return (1 - t) * a + t * b