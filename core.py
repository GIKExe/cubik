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
	def __init__(self, x, y, speed, gravity, jumpPower):
		self.rect = Rect(x,y,16,16)
		self.moving = [0,0]
		self.gravity = gravity
		self.speed = speed
		self.isJump = False
		self.jumpPower = jumpPower
		self.jumpCount = self.jumpPower
		self.onGround = True
		self.spawnPos = (x,y)

	def respawn(self):
		self.rect.topleft = self.spawnPos

	def draw(self, camera, offset):
		draw.rect(
			camera.win, 
			(200,200,200),
			Rect(
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


class Camera:
	def __init__(self, win, background=(25,25,25), smooth=0.125):
		self.win = win
		self.offset = [256,256]
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
		self.objs.append(self.block_table[id](*args, **kwargs))

	def draw(self):
		self.win.fill(self.background)
		for obj in self.objs:
			if obj.rect == None or ((obj.rect.right+self.offset[0] > 0) and \
					(obj.rect.x+self.offset[0] < self.win.get_width()) and \
					(obj.rect.bottom+self.offset[1] > 0) and \
					(obj.rect.y+self.offset[1] < self.win.get_height())):
				obj.draw(self, self.offset)
			obj.tick(self)

	def offset_lerp(self,pos):
		self.offset = [
			lerp(self.offset[0],256-pos[0],self.smooth),
			lerp(self.offset[1],256-pos[1],self.smooth)
		]


def lerp(a, b, t):
	return (1 - t) * a + t * b