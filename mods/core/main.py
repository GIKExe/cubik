from time import sleep
from threading import Thread
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
			self.image,
			(
				self.rect.x+offset[0],
				self.rect.y+offset[1]
			)
		)


class Killer(Block):
	def on_collide(self, player):
		player.respawn()


class Jump(Block):
	def on_collide(self, player):
		if 'усиленный прыжок' in player.effects: return
		player.jumpPower = 64
		player.effects.append('усиленный прыжок')
		def reset():
			sleep(1)
			player.jumpPower = 32
			player.effects.pop(player.effects.index('усиленный прыжок'))
		Thread(target=reset, daemon=True).start()


class Speed(Block):
	def on_collide(self, player):
		if 'ускорение' in player.effects: return
		player.speed = 16
		player.effects.append('ускорение')
		def reset():
			sleep(1)
			player.speed = 4
			player.effects.pop(player.effects.index('ускорение'))
		Thread(target=reset, daemon=True).start()


class Home(Block):
	def on_collide(self, player):
		player.spawnPos = (self.rect.x, self.rect.y+1)


class Error(Block):
	pass


mod.register.block(Block)
mod.register.block(Killer)
mod.register.block(Jump)
mod.register.block(Speed)
mod.register.block(Home)
mod.register.block(Error)