import os

# глобальные библиотеки
import pygame
from pygame import draw, display
from pygame.locals import *

# локальные библиотеки
from ui import *

pygame.init()

app = ObjSpace()
app.pages = pages = Pages(app, 'main')

page = Page(app, 'main')
page += Button(' Выбрать карту ', func=lambda: pages('maps'))
page += Button('     Выход     ', func=lambda: exit())
pages += page

page = Page(app, 'maps')
page += Input(15, comment='Имя карты')
page += Button('    Выбрать    ', func=lambda: print(pages['maps'][0].text))
page += Button('     Назад     ', func=lambda: pages('main'))
pages += page

app.win = win = display.set_mode((800, 450), RESIZABLE)
display.set_caption('Редактор карты')
clock = pygame.time.Clock()

running = True
while running:
	app.events = pygame.event.get()
	for event in app.events:
		if event.type == QUIT:
			running = False

		elif event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				running = False

	pages.tick()

	win.fill((30,30,30))
	pages.draw()
	display.flip()
	clock.tick(60)

pygame.quit()