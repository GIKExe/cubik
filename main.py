import random
import json
import os

# глобальные библиотеки
import pygame
from pygame import draw, display
from pygame.locals import *

# локальные библиотеки
import core
from core import Camera, Player, DebugInfo, Map
from utils import *

pygame.init()

app = core.components
app.clock = pygame.time.Clock()
app.win = pygame.display.set_mode((512,512))
pygame.display.set_caption("Cubik by IvanExe")


Player((0, -16), 3, -4)
DebugInfo(lambda: \
	f"FPS/TPS: {int(app.clock.get_fps())}\n" \
	f"Позиция: {app.player.rect.x},{app.player.rect.y}\n" \
	f"Смещение: {round(app.camera.offset[0])},{round(app.camera.offset[1])}\n" \
	f"Эффекты: {[(k,d['time']) for k,d in app.player.effects.items()]}\n" \
	f"Спавн: {app.player.spawn_pos}"
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
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

		elif event.type == KEYDOWN:
			if event.key == K_F3:
				app.debug.show = not app.debug.show

			elif event.key == K_ESCAPE:
				running = False

	app.player.tick()

	if app.player.rect.y > 512:
		app.player.respawn()

	app.camera.draw()
	app.camera.offset_lerp(app.player.rect.center)
	display.flip()
	app.clock.tick(60)