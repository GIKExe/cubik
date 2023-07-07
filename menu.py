
# глобальные библиотеки
import pygame
from pygame import display, draw, Rect, Surface
from pygame.locals import *

# локальные библиотеки
from utils import *


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
			self.tick()
		return self

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

	def draw(self):
		if self.key not in self:
			return
		page = self[self.key]
		page.draw()


class Label:
	app = None
	page = None

	def __init__(self, text, color):
		self.color = color
		self.text = text

	def __setattr__(self, name, value):
		super().__setattr__(name, value)
		if name == 'text':
			self.generate_image()

	def generate_image(self):
		image = font.render(self.text, True, self.color)
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()

	def draw(self):
		self.app.win.blit(self.image, self.rect)


class Button:
	app = None
	page = None

	def __init__(self, name, func=None):
		self.name = name
		self.func = func

	def __setattr__(self, name, value):
		super().__setattr__(name, value)
		if name == 'name':
			self.generate_image()

	def generate_image(self):
		image = font.render(self.name, True, (0,0,0))
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		self.image.fill((90,90,90))
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()
		draw.rect(self.image, (0,0,0), self.rect, 1)

	def tick(self):
		if self.func is None: return
		self.func()

	def draw(self):
		self.app.win.blit(self.image, self.rect)


if __name__ == '__main__':
	pygame.init()
	font = pygame.font.SysFont('Consolas', 17)

	app = ObjSpace()
	app.win = display.set_mode((800, 450), RESIZABLE)
	display.set_caption('Тест менюшки')

	app.pages = Pages(app, 'main')

	page = Page(app, 'main')
	page += Button('Локальная игра', lambda: app.pages('local'))
	page += Button(' Сетевая игра ', lambda: app.pages('online'))
	page += Button('  Настройки   ', lambda: app.pages('settings'))
	page += Button('    Выход     ', lambda: exit())
	app.pages += page

	def run_game():
		with open('main.py', 'r', encoding='utf-8') as file:
			text = file.read()
		wh = app.win.get_size()
		exec(text, {})
		# app.win = display.set_mode(wh, RESIZABLE)
		app.win = display.set_mode((800, 450), RESIZABLE)

	page = Page(app, 'local')
	page += Label('*список с картами', (0,200,0))
	page += Button('    Играть    ', run_game)
	page += Button('    Назад     ', lambda: app.pages('main'))
	app.pages += page

	page = Page(app, 'online')
	page += Label('*поле для ввода адреса', (0,200,0))
	page += Button(' Подключиться ')
	page += Button('    Назад     ', lambda: app.pages('main'))
	app.pages += page

	page = Page(app, 'settings')
	page += Button('    Назад     ', lambda: app.pages('main'))
	app.pages += page

	running = True
	clock = pygame.time.Clock()

	while running:
		for event in pygame.event.get():
			if event.type == QUIT:
				running = False

			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = False

			elif event.type == MOUSEBUTTONDOWN:
				for obj in app.pages[app.pages.key]:
					if (type(obj) == Button) and obj.rect.collidepoint(event.pos):
						obj.tick()
						break

			elif event.type == VIDEORESIZE:
				pass

		app.win.fill((30,30,30))
		app.pages.draw()
		display.flip()
		clock.tick(60)