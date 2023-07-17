
# class Rect:
# 	def __init__(self, pos, size):
# 		self.pos = list(pos)
# 		self.size = list(size)

# 	@property
# 	def left(self): return self.pos[0]
# 	@left.setter
# 	def left(self, value): self.pos[0] = value

# 	@property
# 	def top(self): return self.pos[1]
# 	@top.setter
# 	def top(self, value): self.pos[1] = value

# 	@property
# 	def width(self): return self.size[0]
# 	@width.setter
# 	def width(self, value): self.size[0] = value

# 	@property
# 	def height(self): return self.size[1]
# 	@height.setter
# 	def height(self, value): self.size[1] = value

# 	@property
# 	def right(self): return self.left + self.width
# 	@right.setter
# 	def right(self, value): self.left = value - self.width

# 	@property
# 	def bottom(self): return self.top + self.height
# 	@bottom.setter
# 	def bottom(self, value): self.top = value - self.height

import re
import time
from threading import Thread

# глобальные библиотеки
import pygame
from pygame import draw, display, Rect
from pygame.locals import *

# локальные библиотеки
from utils import *


class PythonData(dict):
	def __call__(self, name, value=None):
		if value is None:
			return name in self
		else:
			self[name] = value

	def __getattr__(self, name):
		if name in self: return self[name]

	def __setattr__(self, name, value):
		self[name] = value


components = PythonData()
components_wait = PythonData()
class component:
	def __init__(self, id=None, req=[]):
		if type(id) == type:
			raise Exception('используй скобки для декоратора')
		self.id = id
		self.req = req

	def check_req(self):
		# проверяем наличие нашего компонента в списках других компонентов
		for id in list(components_wait.keys()):
			req, cls, args, kwargs = components_wait[id]
			for name in req:
				if name in components:
					req.pop(req.index(name))
			if not req:
				del components_wait[id]
				components(id, cls(components, *args, **kwargs))
				self.check_req()

	def __call__(self, cls):
		self.cls = cls
		self.id = (self.id or re.findall(r"\w+(?='>)", str(cls))[0]).lower()

		def wrapper(*args, **kwargs):
			# если нет компонентов в списке, то будем их ждать
			for id in self.req:
				if not components(id):
					return components_wait(self.id, [self.req, self.cls, args, kwargs])

			# иначе добавляем в список компонентов
			components(self.id, self.cls(components, *args, **kwargs))
			self.check_req()

		return wrapper


@component('debug', req=['camera', 'player'])
class DebugInfo:
	def __init__(self, app, info):
		self.app = app
		self.rect = None
		self.show = False
		self.font = font("Consolas", 16)
		self.info = info

	def tick(*args, **kwargs): pass

	def draw(self):
		if not self.show: return
		win = self.app.camera.win

		lines = self.info().split("\n")
		y = 5
		for text in lines:
			surf = self.font.render(text, True, (250,250,250))
			win.blit(surf,(5,y))
			y += surf.get_height()
		draw.line(win, (250,0,0),(256,0),(256,512))
		draw.line(win, (250,0,0),(512,256),(0,256))


@component(req=['camera', 'map'])
class Player:
	def __init__(self, app, pos, speed, jump_power):
		self.app = app
		self.rect = Rect(*pos,16,16)
		self.moving = [0,0]
		
		self.jump_power = jump_power
		self.spawn_pos = tuple(pos)
		self.effects = {}

		self.speed = speed
		self.spx = 0
		self.spy = 0
		self.is_jump = False
		self.on_ground = False

	def effect(self, name, time=None, func=lambda: 0):
		if time is None:
			return name in self.effects
		else:
			self.effects[name] = {
				'time':int(time * 60), # 60=fps
				'func':func
			} 

	def respawn(self):
		self.spx = 0
		self.spy = 0
		self.rect.topleft = self.spawn_pos
		self.effects = {}

	def draw(self):
		offset = self.app.camera.offset
		win = self.app.camera.win

		draw.rect(
			win, (200,200,200),
			(
				self.rect.x+offset[0],
				self.rect.y+offset[1],
				self.rect.width,
				self.rect.height
			)
		)

	def get_collided(self):
		collided = []
		for block in self.app.map.get_neighbors(self.rect.topleft).values():
			if self.rect.colliderect(block.rect):
				collided.append(block)
		return collided

	def tick(self):
		# обновление эффектов
		for name in tuple(self.effects.keys()):
			if self.effects[name]['time'] <= 0:
				self.effects.pop(name)['func']()
			else:
				self.effects[name]['time'] -= 1

		# влияние гравитации на скорость
		if self.is_jump and (self.spy >= -0.5):
			self.is_jump = False

		key = pygame.key.get_pressed()
		if self.effect('полёт'):
			self.spy = (key[K_s] - key[K_w]) * self.speed
		else:
			if self.spy < 10:
				self.spy += 1 / (abs(self.spy)+1) ** 1.7

			if key[K_SPACE] and self.on_ground:
				self.rect.y += 2
				collided = self.get_collided()
				if len(collided) > 0:
					self.spy = self.jump_power
				self.rect.y -= 2

		self.rect.y += self.spy
		#-------------------------------------------
		collided = self.get_collided()
		self.on_ground = False
		for block in collided:
			block.on_collide(self)
		for block in collided:
			if self.spy > 0:
				self.rect.bottom = block.rect.top
				self.spy = 0
				self.on_ground = True
			elif self.spy < 0:
				self.rect.top = block.rect.bottom
				self.spy = 0
		#===========================================
		self.spx = (key[K_d] - key[K_a]) * self.speed
		self.rect.x += self.spx
		#-------------------------------------------
		collided = self.get_collided()
		for block in collided:
			block.on_collide(self)
		for block in collided:
			if self.spx > 0: self.rect.right = block.rect.left
			elif self.spx < 0: self.rect.left = block.rect.right
		#===========================================


@component()
class Map:
	def __init__(self, app, diagonally=True):
		self.app = app
		self.table = {}
		self.data = {}
		if diagonally:
			self.sposs = [(0,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)]
		else:
			self.sposs = [(0,0),(0,1),(1,0),(0,-1),(-1,0)]

	def reg(self, name, cls):
		self.table[name] = cls

	def add_block(self, name, pos):
		if name in self.table:
			self.data[pos] = self.table[name](*pos)
		else:
			self.data[pos] = self.table['error'](*pos)

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


@component(req=['map'])
class Camera:
	def __init__(self, app, background=(25,25,25), smooth=0.125):
		self.app = app
		self.win = app.win
		self.map = app.map

		width, height = self.win.get_size()
		self.offset = [width//2, height//2]
		self.background = background
		self.smooth = smooth

	def draw(self):
		self.win.fill(self.background)

		# отрисовка блоков из карты
		for obj in list(self.app.map.data.values()):
			if ((obj.rect.right+self.offset[0] > 0) and \
					(obj.rect.x+self.offset[0] < self.win.get_width()) and \
					(obj.rect.bottom+self.offset[1] > 0) and \
					(obj.rect.y+self.offset[1] < self.win.get_height())):
				obj.draw(self, self.offset)
			obj.tick(self)

		self.app.player.draw()
		self.app.debug.draw()
		
		draw.rect(self.win, (200,0,200), (self.offset[0], self.offset[1], 16, 16), 2)

	def offset_lerp(self, pos):
		width, height = self.win.get_size()

		self.offset = [
			lerp(self.offset[0], width//2-pos[0], self.smooth),
			lerp(self.offset[1], height//2-pos[1], self.smooth)
		]


def lerp(a, b, t):
	return (1 - t) * a + t * b