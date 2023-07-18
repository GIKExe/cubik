from datetime import datetime

# глобальные библиотеки
import pygame


_print = print
class Print:
	def __init__(self, name=''):
		self.name = str(name)

	def __call__(self, *args, **kwargs):
		text = datetime.now().strftime("[%H:%M:%S]")
		text += f'{" " if self.name else ""}{self.name}:'
		return _print(text, *args, **kwargs)


class PythonData(dict):
	def __call__(self, name, value=None):
		if value is None:
			return name in self
		else:
			self[name] = value

	def __getattr__(self, name):
		if name in self: return self[name]

	def __setattr__(self, name, value):
		self[name] = value


fonts = {}
def font(name, size):
	if name not in fonts:
		fonts[name] = {}
	if size not in fonts[name]:
		fonts[name][size] = pygame.font.SysFont(name, size)
	return fonts[name][size]
