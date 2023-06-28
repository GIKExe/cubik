import pygame
import threading


fonts = []
def get_font(name,size):
  global fonts
  for i in fonts:
    if i[0] == name and i[1] == size:
      return i[3]
  f = pygame.font.SysFont(name,size)
  fonts.append([name,size,f])
  return f

class PriorityLimitException(Exception):
	"Priority limits from -1024 to 1024"
	pass

class Ticker:
	def __init__(self, name=None, tps=20):
		self._run = True
		self._callbacks = []
		self._ticks_alive = 0
		self._tps = tps
		self._clock = pygame.time.Clock()
		self._thread = threading.Thread(
			target = self._main,
			daemon = True,
			name = name)
		self._thread.start()
    
	def is_alive(self):
		return self._run
	
	def get_ticks_alive(self):
		return self._ticks_alive
	
	def get_tps(self):
		return self._tps

	def _main(self):
		while self._run:
			for t in sorted(self._callbacks,key=lambda x:x.priority,reverse=True): t()
			self._ticks_alive += 1
			self._clock.tick(self._tps)

	def has_callback(self,name):
		for i in self._callbacks:
			if i.name == name:
				return True
		return False
	
	def _get_callback(self,name):
		for i in self._callbacks:
			if i.name == name:
				return i

	def add_callback(self,name,cb=None,priority=0):
		if type(name) == Callback:
			if name.priority > 1024 or name.priority < -1024:
				raise PriorityLimitException()
			self._callbacks.append(name)
		elif cb != None and not self.has_callback(name):
			if priority > 1024 or priority < -1024:
				raise PriorityLimitException()
			self._callbacks.append(Callback(name,cb,priority))

	def remove_callback(self,name):
		if self.has_callback(name):
			c = self._get_callback(name)
			self._callbacks.remove(c)
			c.close()
		
	def close(self):
		self._run = False
		self._thread.join()


class Callback:
	def __init__(self, name, func, priority=0):
		self.name = name
		self.priority = priority
		self._func = func

	def __call__(self):
		self._func()

	def close(self):
		pass
