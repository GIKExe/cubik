from time import sleep
from threading import Thread

# глобальные библиотеки
from pygame import Rect


class Block:
	image = None

	def __init__(self, x, y):
		self.rect = Rect(x*16,y*16,16,16)

	def tick(*args, **kwargs):
		pass

	def draw(self, camera, offset):
		if self.image is None: return
		camera.win.blit(
			self.image, (self.rect.x+offset[0], self.rect.y+offset[1])
		)

	def on_collide(self, player):
		pass


class Killer(Block):
	def on_collide(self, player):
		player.respawn()
		player.effects = {}

class Jump(Block):
	def on_collide(self, player):
		name = 'усиленный прыжок'
		if name in player.effects: return
		player.jump_power = -6
		player.effects[name] = 1
		def reset():
			sleep(2)
			player.jump_power = -4
			if name in player.effects:
				del player.effects[name]
		Thread(target=reset, daemon=True).start()


class Speed(Block):
	def on_collide(self, player):
		name = 'ускорение'
		if name in player.effects: return
		player.speed = 16
		player.effects[name] = 1
		def reset():
			sleep(1)
			player.speed = 4
			if name in player.effects:
				del player.effects[name]
		Thread(target=reset, daemon=True).start()


class Home(Block):
	def on_collide(self, player):
		player.spawn_pos = (self.rect.x, self.rect.y-16)


class Error(Block):
	pass


class Fly(Block):
	def on_collide(self, player):
		name = 'полёт'
		if name in player.effects: return
		player.effects[name] = 1
		def reset():
			sleep(60)
			if name in player.effects:
				del player.effects['полёт']
		Thread(target=reset, daemon=True).start()


mod.register.block(Block)
mod.register.block(Killer)
mod.register.block(Jump)
mod.register.block(Speed)
mod.register.block(Home)
mod.register.block(Error)
mod.register.block(Fly)