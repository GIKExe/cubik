
import re
import os
import time
from threading import Thread
from datetime import datetime

# глобальные библиотеки
import pickle
import pygame
from pygame import draw, display, Rect
from pygame.locals import *

# локальные библиотеки
from utils import *


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
class Map(PythonData):
	def __init__(self, app):
		self.app = app
		self.table = {}
		self.map = {}

	def reg(self, name, cls):
		self.table[name] = cls

	def add_block(self, name, pos):
		if name not in self.table:
			name = 'error'
		self.map[pos] = self.table[name](self.app, pos)

	def get_neighbors(self, pos):
		sposs = [(0,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)]
		x = int(pos[0] // 16)
		y = int(pos[1] // 16)
		res = {}

		for spos in sposs:
			sx, sy = spos
			pos = (x+sx, y+sy)
			if pos in self.map:
				res[spos] = self.map[pos]

		return res

	def load(self, name):
		filename = name + '.pickle'

		if not os.path.isdir('maps'):
			raise Exception(f'папка maps не существует')
		if filename not in os.listdir('maps'):
			raise Exception(f'Файл карты {filename} не найден')
		if not os.path.isfile('maps/'+filename):
			raise Exception(f'Путь maps/{filename} не является файлом')

		with open('maps/'+filename, 'rb') as file:
			data = pickle.load(file)
		super().__init__(data)

		for name in ['version', 'name', 'size', 'data', 'metadata', 'palette']:
			if not self(name): raise Exception(f'Файл {filename} повреждён, нету переменной {name}')

		ox = int(self.size[0] // 2)
		oy = int(self.size[1] // 2)
		index = 0
		index_block = 0

		while index < len(self.data):
			num = self.data[index]
			if num == 255:
				index += 1
				index_meta = self.data[index+1]
			elif num == 254:
				index += 2
				index_meta = int.from_bytes(self.data[index+1:index+3], byteorder='little')
			elif num == 253:
				index += 3
				index_meta = int.from_bytes(self.data[index+1:index+4], byteorder='little')
			elif num == 252:
				index += 4
				index_meta = int.from_bytes(self.data[index+1:index+5], byteorder='little')
			elif num > 0:
				index_meta = -1
			else:
				index_meta = None

			if index_meta != None:
				if index_meta > -1:
					try:
						data = self.metadata[index_meta]
					except:
						# print(len(self.metadata), index_meta)
						# raise
						index += 1
						index_block += 1
						continue
					else:
						num = data['id']

				id = self.palette[num - 1]
				pos = ( int(index_block % self.size[0])-ox, int(index_block // self.size[0])-oy )
				self.add_block(id, pos)

			index += 1
			index_block += 1


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
		x = int(self.app.player.rect.x // 16)
		y = int(self.app.player.rect.y // 16)

		for ix in range(-15-2,16+2):
			for iy in range(-15-2,16+2):
				pos = (x+ix, y+iy)
				if pos not in self.app.map.map: continue
				self.app.map.map[pos].draw()

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