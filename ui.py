
# глобальные библиотеки
import pygame
from pygame import display, draw, Rect, Surface
from pygame.locals import *

# локальные библиотеки
from utils import *


pygame.font.init()


class Widget:
	app = None
	page = None
	font = font('Consolas', 17)
	triger_active = False
	triger_generate_image = ['text', 'background', 'color']

	def __setattr__(self, name, value):
		super().__setattr__(name, value)
		if name in self.triger_generate_image and self.triger_active:
			self.generate_image()

	def tick(*args, **kwargs): pass
	def draw(*args, **kwargs): pass
	def generate_image(*args, **kwargs): pass


class Label(Widget):
	def __init__(self, text, color=(200,200,200), background=(90,90,90)):
		self.text = text
		self.color = color
		self.background = background

		self.generate_image()
		self.triger_active = True

	def generate_image(self):
		image = self.font.render(self.text, True, self.color)
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		if self.background:
			self.image.fill(self.background)
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()

	def draw(self):
		self.app.win.blit(self.image, self.rect)


class Button(Widget):
	def __init__(self, text, color=(200,200,200), background=(90,90,90), func=None):
		self.text = text
		self.color = color
		self.background = background
		self.func = func

		self.generate_image()
		self.triger_active = True

	def generate_image(self):
		image = self.font.render(self.text, True, self.color)
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		if self.background:
			self.image.fill(self.background)
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()

	def tick(self):
		if self.func is None: return
		self.func()

	def draw(self):
		self.app.win.blit(self.image, self.rect)


class Input(Widget):
	active = False

	def __init__(self, size=16, color=(200,200,200), 
		comment='', comment_color=(100,100,100), background=(60,60,60), chars=None):
		self.text = ''
		self.size = size
		self.color = color

		self.comment = comment
		self.comment_color = comment_color
		self.background = background

		self.chars = chars or R"""
			abcdefghijklmnopqrstuvwxyz
			ABCDEFGHIJKLMNOPQRSTUVWXYZ
			абвгдеёжзийклмнопрстуфхцчшщъыьэюя
			АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ
			`1234567890-=~!@#$%^&*()_+"'№;:?_{}[]/|\,.
		""".replace('\n', '').replace('\t', '')

		self.generate_image()
		self.triger_active = True
		self.triger_generate_image += ['size', 'comment', 'comment_color']

	def generate_image(self):
		if self.text:
			image = self.font.render(self.text+' '*(self.size-len(self.text)), True, self.color)
		else:
			image = self.font.render(self.comment+' '*(self.size-len(self.comment)), 
				True, self.comment_color)
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		if self.background:
			self.image.fill(self.background)
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()
		draw.rect(self.image, (0,0,0), (0,0,w+10,h+10), 1)

	def tick(self, event):
		if event.key == K_BACKSPACE:
			if len(self.text) > 0:
				self.text = self.text[:-1]
		elif (len(self.text) < self.size) and (event.unicode in self.chars): 
			self.text += event.unicode

	def draw(self):
		self.app.win.blit(self.image, self.rect)


class Line(list, Widget):
	def __init__(self, indent=10):
		self.indent = indent
		self.rect = Rect(0,0,0,0)

	def __iadd__(self, obj):
		self.append(obj)
		obj.app = self.app
		obj.page = self.page
		if obj.rect.height > self.rect.height:
			self.rect.height = obj.rect.height
		self.rect.width += obj.rect.width + self.indent
		return self

	def __isub__(self, obj):
		if obj in self:
			self.pop(self.index(obj))
			self.rect.width -= obj.rect.width + self.indent
		return self

	def draw(self):
		x = self.rect.x
		for obj in self:
			obj.rect.topleft = (x, self.rect.y)
			obj.draw()
			x += obj.rect.width
			x += self.indent


class Page(list):
	def __init__(self, app, name, indent=10):
		self.app = app
		self.name = name
		self.indent = indent
		self.start_pos = (0,0)

	def __iadd__(self, obj):
		self.append(obj)
		obj.app = self.app
		obj.page = self
		return self

	def __isub__(self, obj):
		if obj in self:
			self.pop(self.index(obj))
		return self

	def tick(self):
		objs = []
		for obj in self:
			if type(obj) == Line:
				objs += obj
			else:
				objs.append(obj)

		for event in self.app.events:
			if event.type == MOUSEBUTTONDOWN:
				for obj in objs:
					if not obj.rect.collidepoint(event.pos):
						if type(obj) == Input:
							obj.active = False
						continue

					if type(obj) == Button:
						obj.tick()

					elif type(obj) == Input:
						obj.active = True

			elif event.type == KEYDOWN:
				for obj in objs:
					if type(obj) == Input and obj.active:
						obj.tick(event)

	def draw(self):
		w, h = self.app.win.get_size()
		w//=2
		h//=2

		h2 = (len(self)-1)*self.indent
		for obj in self:
			h2 += obj.rect.height

		y = h - h2//2
		for obj in self:
			x = w - obj.rect.width//2
			obj.rect.topleft = (x,y)
			obj.draw()
			y += obj.rect.height
			y += self.indent


class Pages(dict):
	def __init__(self, app, key=None):
		self.app = app
		self.key = key

	def __call__(self, key):
		self.key = key

	def __iadd__(self, page):
		if type(page) != Page:
			raise Exception('Хранить можно только страницы')
		self[page.name] = page
		return self

	def __isub__(self, page):
		if type(page) not in [Page, str]:
			raise Exception('Удалить можно только по объекту или строке') 
		if type(page) == str:
			if page in self:
				self.pop(page)
		else:
			if page.name in self:
				self.pop(page.name)
		return self

	def tick(self):
		if self.key not in self: return
		self[self.key].tick()

	def draw(self):
		if self.key not in self: return
		self[self.key].draw()


if __name__ == '__main__':
	pygame.init()

	app = ObjSpace()
	app.win = display.set_mode((800, 450), RESIZABLE)
	display.set_caption('Тест менюшки')

	app.pages = pages = Pages(app, 'main')

	page = Page(app, 'main')
	page += Button('Локальная игра', func=lambda: pages('local'))
	page += Button(' Сетевая игра ', func=lambda: pages('online'))
	page += Button('  Настройки   ', func=lambda: pages('settings'))
	page += Button('    Выход     ', func=lambda: exit())
	pages += page

	def run_game():
		with open('main.py', 'r', encoding='utf-8') as file:
			text = file.read()
		exec(text, {})
		app.win = display.set_mode((800, 450), RESIZABLE)

	page = Page(app, 'local')
	page += Label('*список с картами', (0,200,0))
	page += Button('    Играть    ', func=run_game)
	page += Button('    Назад     ', func=lambda: pages('main'))
	pages += page

	page = Page(app, 'online')
	line = Line()
	page += line
	line += Input(32, comment='Айпи')
	line += Input(5, comment='Порт', chars='1234567890')
	page += Button(' Подключиться ')
	page += Button('    Назад     ', func=lambda: pages('main'))
	pages += page

	page = Page(app, 'settings')
	page += Button('    Назад     ', func=lambda: pages('main'))
	pages += page

	running = True
	clock = pygame.time.Clock()

	while running:
		app.events = pygame.event.get()
		for event in app.events:
			if event.type == QUIT:
				running = False

			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = False

		app.pages.tick()

		app.win.fill((30,30,30))
		app.pages.draw()
		display.flip()
		clock.tick(60)