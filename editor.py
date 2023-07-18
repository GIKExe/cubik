import random
import json
import os

# глобальные библиотеки
import pygame
from pygame import draw, display
from pygame.locals import *

# локальные библиотеки
import core
from core import Camera, DebugInfo, Map
from utils import *

pygame.init()

class Player:
	def __init__(self):
		self.rect = Rect(0,0,16,16)

	def draw(self):
		pass

center = (0,0)
app = core.components
app.block_id = 0
app.player = Player()
app.clock = pygame.time.Clock()
app.win = pygame.display.set_mode((512,512))
pygame.display.set_caption("Cubik by IvanExe")


def get_block_id():
	if app.block_id == -1:
		return 'center'

	l = list(app.map.table.keys())
	if app.block_id < len(l):
		return l[app.block_id]
	else:
		return 'error'

DebugInfo(lambda: \
	f"FPS/TPS: {int(app.clock.get_fps())}\n" \
	f"Смещение: {round(app.camera.offset[0])},{round(app.camera.offset[1])}\n" \
	f"Выбраный блок: {app.block_id} {get_block_id()}\n" \
)
Camera(smooth=0.05)
Map()

with open('modloader.py', 'r', encoding='utf-8') as file:
	text = file.read()
	exec(text, {'app':app})

if 'map_name' in globals():
	app.map.load(map_name)
else:
	app.map.load('default')

running = True
while running:
	buttons = pygame.mouse.get_pressed()
	x,y = pygame.mouse.get_pos()
	xb = int((x-app.camera.offset[0])//16)
	yb = int((y-app.camera.offset[1])//16)
	pos = (xb, yb)

	if buttons[0]:
		if app.block_id == -1:
			center = tuple(pos)
		else:
			name = get_block_id()
			app.map.add_block(name, pos)

	elif buttons[2]:
		if pos in app.map.map:
			del app.map.map[pos]

	keys = pygame.key.get_pressed()
	app.player.rect.x += (keys[K_d] - keys[K_a]) * 4
	app.player.rect.y += (keys[K_s] - keys[K_w]) * 4

	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

		elif event.type == KEYDOWN:
			if event.key == K_F3:
				app.debug.show = not app.debug.show

			elif event.key == K_ESCAPE:
				running = False

			elif keys[K_LCTRL] and event.key == K_s:
				app.map.center = (app.map.center[0]+center[0], app.map.center[1]+center[1])
				app.map.save()
				print('карта сохранена')
				# exit()
				running = False
				continue

		elif event.type == MOUSEBUTTONDOWN:
			if event.button == 4:  # Прокрутка вверх
				if app.block_id < 251:
					app.block_id += 1

			elif event.button == 5:  # Прокрутка вниз
				if app.block_id > -1:
					app.block_id -= 1

	app.camera.draw()
	app.camera.offset_lerp(app.player.rect.center)

	draw.rect(app.win, (200,0,200), ( 
		center[0]*16+app.camera.offset[0],
		center[1]*16+app.camera.offset[1],
		16, 16)
	)

	if app.debug.show:
		app.win.blit(app.debug.font.render(str((xb, yb)), True, (200,0,0)), (x+5,y+5))

	display.flip()
	app.clock.tick(60)