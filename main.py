import pygame
from pygame import draw, display
from pygame.locals import *

import random
import json
import os

import core
from core import Camera, Player, DebugInfo, Map

from importlib import import_module

class ObjSpace(dict):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __getattr__(self, name):
		if name in self: return self[name]

	def __setattr__(self, name, value):
		self[name] = value

pygame.init()

app = ObjSpace()
app.win = pygame.display.set_mode((512,512))
pygame.display.set_caption("Cubic")
app.map = Map(app)
app.camera = Camera(app, smooth=0.05)

# player = Player(0,-16, 4, 3, 32)
app.player = Player(app, 0,-16, 2, 1, 32)
		
app.debug = DebugInfo(lambda: \
	f"Позиция: {app.player.rect.x},{app.player.rect.y}\n" \
	f"Смещение: {round(app.camera.offset[0])},{round(app.camera.offset[1])}\n" \
	f"Эффекты: {app.player.effects}"
)

app.camera += app.player
app.camera += app.debug
		

with open('modloader.py', 'r', encoding='utf-8') as file:
	text = file.read()
	exec(text, {'app':app})


def load_map(name):
	l = os.listdir('maps')
	if (name+'.json' not in l) or (name+'.map' not in l):
		raise Exception(f'карта {name} не найдена')

	with open(f'maps/{name}.json', 'rb') as file:
		map_info = json.load(file)
		ox = int(map_info['size'][0] // 2)
		oy = int(map_info['size'][1] // 2)

	with open(f'maps/{name}.map', 'rb') as file:
		map_data = file.read()

	for index in range(len(map_data)):
		num = map_data[index] - 1
		if num < 0: continue
		if num < len(map_info['blocks']):
			id = map_info['blocks'][num]
		else:
			id = 'error'

		pos = ( int(index % map_info['size'][0])-ox, int(index // map_info['size'][0])-oy )

		block = app.map.table[id](*pos)
		# block = app.camera.add_block(id, *pos)
		app.map.data[pos] = block

load_map('default')

clock = pygame.time.Clock()

running = True
while running:
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

		elif event.type == KEYDOWN:
			if event.key == K_SPACE:
				if app.player.onGround:
					app.player.isJump = True

			elif event.key == K_F3:
				app.debug.show = not app.debug.show
				
		keys = pygame.key.get_pressed()
		app.player.moving[0] = keys[K_d] - keys[K_a]

	app.camera.draw()

	if app.player.rect.y > 512:
		app.player.respawn()

	app.camera.offset_lerp(app.player.rect.center)

	display.flip()
	clock.tick(60)
	
pygame.quit()