
import os
import re
import core
import pygame

import importlib


def import_module(path, **kwargs):
  mod = importlib.import_module(path)
  for name in kwargs:
    setattr(mod, name, kwargs[name])
  if hasattr(mod, 'init') and callable(mod.init):
    mod.init()
  return mod

mods = {}

def mod_init(name):
  path = 'mods/'+name

  if not os.path.isdir(path): return
  if not os.path.isfile(path+"/__init__.py"): return

  data = {'images': {}, 'blocks': {}}
  mods[name] = data

  if os.path.isdir(path+'/images'):
    for image_name in os.listdir(path+'/images'):
      if not image_name.endswith('.png'): continue
      image = pygame.image.load(path+'/images/'+image_name)
      image_name = image_name[:-4]
      data['images'][image_name] = image

  register = Register(name)

  mod = import_module("mods."+name, mods=mods, register=register)


def init():
  global Register

  class Register:
    def __init__(self, name):
      self.name = name

    def block(self, cls):
      id = re.findall(r"\w+(?='>)", str(cls))[0].lower()

      if id in mods[self.name]['images']:
        cls.image = mods[self.name]['images'][id]
      else:
        cls.image = mods['core']['images']['error']

      mods[self.name]['blocks'][id] = cls
      camera.block_table[id] = cls
      # print(f'мод {self.name} регистрирует блок: {id}')


  # нужна ли проверка на мод core?
  for name in os.listdir('mods'):
    mod_init(name)