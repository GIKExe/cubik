import pygame
from pygame import draw, display
from pygame.locals import *

import random
import json
import os

import core
from core import Camera, Player, DebugInfo

from importlib import import_module

pygame.init()

win = pygame.display.set_mode((512,512))
pygame.display.set_caption("Cubic")

player = Player(0,-16, 4,3, 32)

camera = Camera(win, smooth=0.05)

modloader = import_module("modloader")
modloader.camera = camera
modloader.init()

camera += player

# добавление блоков
# for i in [-5,-4,-3,-1,0,1]:
#   camera.add_block('block', i, 2)

# camera.add_block('home', -2, 2)

# camera.add_block('block', 3, 0)

# for i in [2,3,4]:
#   camera.add_block('killer', i, 2)

# for i in range(10):
#   camera.add_block('block', 5+i, 2)
#   camera.add_block('block', 5+i, -2)

# camera.add_block('block', 0, 0)

# без функции загрузка карты
# не безопасная

def load_map(name):
  l = os.listdir('maps')
  if (name+'.json' not in l) or (name+'.map' not in l):
    raise Exception(f'карта {name} не найдена')

  with open(f'maps/{name}.json', 'rb') as file:
    map_info = json.load(file)
    ox = map_info['size'][0] // 2
    oy = map_info['size'][1] // 2

  with open(f'maps/{name}.map', 'rb') as file:
    map_data = file.read()

  for index in range(len(map_data)):
    num = map_data[index] - 1
    if num < 0: continue
    if num < len(map_info['blocks']):
      id = map_info['blocks'][num]
    else:
      id = 'error'
    camera.add_block(id,
      (index % map_info['size'][0])-ox, 
      (index // map_info['size'][0])-oy
    )

load_map('default')

debug = DebugInfo(lambda: f"Player pos: {player.rect.x},{player.rect.y}\n"\
    f"Camera offset: {round(camera.offset[0])},{round(camera.offset[1])}\n")
camera += debug

clock = pygame.time.Clock()
 
running = True
while running:
  for event in pygame.event.get():
    if event.type == QUIT:
      running = False

    elif event.type == KEYDOWN:
      if event.key == K_SPACE:
        if player.onGround:
          player.isJump = True

      elif event.key == K_F3:
        debug.show = not debug.show
        
    keys = pygame.key.get_pressed()
    player.moving[0] = keys[K_d] - keys[K_a]

  camera.draw()

  if player.rect.y > 512:
    # player.rect.x = 0
    # player.rect.y = 0
    player.respawn()

  camera.offset_lerp(player.rect.center)

  display.flip()
  clock.tick(60)
  
pygame.quit()