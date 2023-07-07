
import os
import re
from time import sleep

# глобальные библиотеки
import pygame

# локальные библиотеки
from utils import *


mods = {}
app.mods = mods

class Register:
	def __init__(self, mod):
		self.mod = mod

	def block(self, cls):
		name = re.findall(r"\w+(?='>)", str(cls))[0].lower()

		if name in self.mod.images:
			cls.image = self.mod.images[name]
		else:
			cls.image = mods['core'].images['error']

		app.map.reg(name, cls)
		self.mod.blocks[name] = cls
		self.mod.print(f'регистрирую блок: {name}')


class Mod:
	alive = False

	def __init__(self, name):
		path = 'mods/'+name

		if not os.path.isdir(path): return
		if not os.path.isfile(path+"/main.py"): return

		with open(path+'/main.py', 'r', encoding='utf-8') as file:
			self.text = file.read()

		self.name = name
		self.register = Register(self)
		self.print = Print(name)
		self.images = {}
		self.blocks = {}

		if os.path.isdir(path+'/images'):
			for name in os.listdir(path+'/images'):
				if not name.endswith('.png'): continue
				image = pygame.image.load(path+'/images/'+name)
				name = name[:-4]
				self.images[name] = image

		self.alive = True

	def __call__(self, **kwargs):
		if not self.alive: return
		kwargs['app'] = app
		kwargs['mod'] = self
		kwargs['print'] = self.print
		exec(self.text, kwargs)
		mods[self.name] = self


for name in os.listdir('mods'):
	mod = Mod(name)
	mod()