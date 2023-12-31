import os

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


class Label(Widget):
	def __init__(self, text, color=(200,200,200), background=None):
		self.text = text
		self.color = color
		self.background = background
		self.generate_image()

	def generate_image(self):
		image = self.font.render(str(self.text), True, self.color)
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		if self.background:
			self.image.fill(self.background)
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()

	def update(self):
		self.app.win.blit(self.image, self.rect)
		self.generate_image()


class Button(Widget):
	def __init__(self, text, color=(200,200,200), background=(90,90,90), func=None, center=16):
		self.center = center
		self.text = text
		self.color = color
		self.background = background
		self.func = func
		self.generate_image()

	def generate_image(self):
		w = self.center - len(self.text)
		text = (' '*(w//2)) + self.text + (' '*(w//2+w%2))
		image = self.font.render(text, True, self.color)
		w,h = image.get_size()
		self.image = Surface((w+10, h+10), SRCALPHA)
		if self.background:
			self.image.fill(self.background)
		self.image.blit(image, (5,7))
		self.rect = self.image.get_rect()

	def update(self):
		if self.func is not None:
			for event in self.app.events:
				if event.type == MOUSEBUTTONDOWN:
					if self.rect.collidepoint(event.pos):
						self.func()

		self.app.win.blit(self.image, self.rect)
		self.generate_image()


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
		draw.rect(self.image, (200,0,0) if self.active else (0,0,0), (0,0,w+10,h+10), 1)

	def update(self):
		for event in self.app.events:
			if event.type == MOUSEBUTTONDOWN:
				self.active = self.rect.collidepoint(event.pos)

			elif event.type == KEYDOWN and self.active:
				if event.key == K_BACKSPACE:
					if len(self.text) > 0:
						self.text = self.text[:-1]

				elif (len(self.text) < self.size) and (event.unicode in self.chars): 
					self.text += event.unicode

		self.app.win.blit(self.image, self.rect)
		self.generate_image()


class Line(list, Widget):
	def __init__(self, indent=10):
		self.indent = indent
		self.rect = Rect(0,0,0,0)

	def __iadd__(self, obj):
		if type(obj) == Line:
			raise Exception('не пиши фигню')
		if obj.rect.height > self.rect.height:
			self.rect.height = obj.rect.height
		
		self.append(obj)
		obj.app = self.app
		obj.page = self.page
		return self

	def update(self):
		x = self.rect.x
		self.rect.width = 0
		for obj in self:
			self.rect.width += obj.rect.width
			obj.rect.topleft = (x, self.rect.y)
			obj.update()
			x += obj.rect.width
			x += self.indent
		self.rect.width += len(self) * self.indent


class Page(list):
	def __init__(self, obj, name, indent=10):
		self.name = name
		if type(obj) == Pages:
			self.app = obj.app
			obj[name] = self
		else:
			self.app = obj
		self.indent = indent
		self.start_pos = (0,0)

	def __iadd__(self, obj):
		self.append(obj)
		obj.app = self.app
		obj.page = self
		return self

	def update(self):
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
			obj.update()
			y += obj.rect.height
			y += self.indent


class Pages(PythonData):
	def __init__(self, app, key=None):
		self.app = app
		self.key = key

	def __call__(self, key):
		self.key = key

	def update(self):
		if self.key not in self: return
		self[self.key].update()

from tkinter import Tk, filedialog

if __name__ == '__main__':
	pygame.init()

	app = PythonData()
	app.win = display.set_mode((800, 450))
	display.set_caption('Тест менюшки')

	app.pages = pages = Pages(app, 'main')

	def chose_map():
		root = Tk()
		root.withdraw()
		filetypes = (
			("Файл карты", "*.pickle"),
			("Все файлы", "*.*")
		)
		path = filedialog.askopenfilename(
			title='Выбор карты',
			initialdir="maps/",
			filetypes=filetypes
		)
		root.destroy()
		return path

	# =========================================================================
	page = Page(pages, 'main')
	page += Button('Локальная игра', func=lambda: pages('local'))
	page += Button('Сетевая игра', func=lambda: pages('online'))
	page += Button('Редактор', func=lambda: pages('editor'))
	page += Button('Настройки', func=lambda: pages('settings'))
	page += Button('Выход', func=exit)
	back = lambda: pages('main')

	# =========================================================================
	page = Page(pages, 'local')

	def run_game():
		path = pages.local[0][1].text
		if not path:
			return
		filename = path.split('/')[-1]
		name = filename.split('.')[0]
		with open('main.py', 'r', encoding='utf-8') as file:
			text = file.read()
		os.system('cls')
		exec(text, {'map_name': name})
		app.win = display.set_mode((800, 450))

	def local():
		path = chose_map()
		if not path:
			path = None
		pages.local[0][1].text = path

	line = Line()
	page += line
	line += Label('Выбранная карта:')
	line += Label(None, (200,0,0))

	page += Button('Выбрать карту...', func=local)
	page += Button('Играть', func=run_game)
	page += Button('Назад', func=back)

	# =========================================================================
	page = Page(pages, 'online')
	line = Line()
	page += line
	line += Input(32, comment='Айпи')
	line += Input(5, comment='Порт', chars='1234567890')
	page += Button('Подключиться', func=lambda: print(line[0].text+':'+line[1].text))
	page += Button('Назад', func=back)

	# =========================================================================
	page = Page(pages, 'editor')

	def run_editor():
		path = pages.editor[0][1].text
		if not path:
			return
		filename = path.split('/')[-1]
		name = filename.split('.')[0]
		with open('editor.py', 'r', encoding='utf-8') as file:
			text = file.read()
		os.system('cls')
		exec(text, {'map_name': name})
		app.win = display.set_mode((800, 450))

	def local():
		path = chose_map()
		if not path:
			path = None
		pages.editor[0][1].text = path

	line = Line()
	page += line
	line += Label('Выбранная карта:')
	line += Label(None, (200,0,0))

	page += Button('Выбрать карту...', func=local)
	page += Button('Редактировать', func=run_editor)
	page += Button('Назад', func=back)

	# =========================================================================
	page = Page(pages, 'settings')
	page += Button('Назад', func=back)

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

		app.win.fill((30,30,30))
		pages.update()
		display.flip()
		clock.tick(60)