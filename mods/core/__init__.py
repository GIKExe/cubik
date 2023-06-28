from time import sleep
from threading import Thread
from pygame import Rect

def init():

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
      player.jumpPower = 128
      def reset():
        sleep(1)
        player.jumpPower = 32
      Thread(target=reset, daemon=True).start()


  class Speed(Block):
    def on_collide(self, player):
      player.speed = 16
      def reset():
        sleep(1)
        player.speed = 4
      Thread(target=reset, daemon=True).start()


  class Home(Block):
    def on_collide(self, player):
      player.spawnPos = (self.rect.x, self.rect.y+1)


  class Error(Block):
    pass


  register.block(Block)
  register.block(Killer)
  register.block(Jump)
  register.block(Speed)
  register.block(Home)
  register.block(Error)