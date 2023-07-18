from time import sleep
from threading import Thread

# глобальные библиотеки
from pygame import Rect


@mod.reg.block
class Block:
	image = None

	def __init__(self, app, pos):
		self.app = app
		self.rect = Rect(pos[0]*16,pos[1]*16,16,16)

	def draw(self):
		if self.image is None: return
		self.app.win.blit(
			self.image, (self.rect.x+self.app.camera.offset[0], self.rect.y+self.app.camera.offset[1])
		)

	def on_collide(*args, **kwargs): pass


@mod.reg.block
class Killer(Block):
	def on_collide(self, player):
		player.respawn()


@mod.reg.block
class Jump(Block):
	def on_collide(self, player):
		player.jump_power = -6
		def reset():
			player.jump_power = -4
		player.effect('усиленный прыжок', 2, reset)
		

@mod.reg.block
class Speed(Block):
	def on_collide(self, player):
		player.speed = 16
		def reset():
			player.speed = 4
		player.effect('ускорение', 1, reset)


@mod.reg.block
class Home(Block):
	def on_collide(self, player):
		player.spawn_pos = (self.rect.x, self.rect.y-16)


@mod.reg.block
class Error(Block):
	pass


@mod.reg.block
class Fly(Block):
	def on_collide(self, player):
		player.effect('полёт', 60)