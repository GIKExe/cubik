# import re 

# class mod:
# 	class reg:
# 		def block(self, *args, **kwargs):
# 			print(self)
# 			def _block(cls, id=None, name=None):
# 				id = (id or re.findall(r"\w+(?='>)", str(cls))[0]).lower().replace(' ', '_')
# 				name = name or id
# 				print(f'регистрирую блок {id} под названием: {name}')

# 			if len(args) > 0 and type(args[0]) == type:
# 				# регистрация блока по имени его класса
# 				cls = args[0]
# 				_block(cls)
# 				return cls

# 			else:
# 				def _cls(cls):
# 					_block(cls, *args, **kwargs)
# 					return cls
# 				return _cls

# reg = mod.reg()

# @reg.block(name='Super Block')
# class Test:
# 	def __init__(self, name):
# 		print(name)

# Test(123)

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

import os
import pickle


# @component()
class Map(PythonData):
	def __init__(self, app):
		self.app = app
		self.table = {}
		self.map = {}

	def reg(self, name, cls):
		self.table[name] = cls

	def add_block(self, name, pos):
		if name in self.table:
			self.map[pos] = self.table[name](*pos)
		else:
			self.map[pos] = self.table['error'](*pos)

	def get_neighbors(self, pos):
		sposs = [(0,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0)]
		x = int(pos[0] // 16)
		y = int(pos[1] // 16)
		res = {}

		for spos in sposs:
			sx, sy = spos
			pos = (x+sx, y+sy)
			if pos in self.map:
				res[spos] = self.map[pos]

		return res

	def load(self, name):
		filename = name + '.pickle'

		if not os.path.isdir('maps'):
			raise Exception(f'папка maps не существует')
		if filename not in os.listdir('maps'):
			raise Exception(f'Файл карты {filename} не найден')
		if not os.path.isfile('maps/'+filename):
			raise Exception(f'Путь maps/{filename} не является файлом')

		with open('maps/'+filename, 'rb') as file:
			data = pickle.load(file)
		super().__init__(data)
		
		for name in ['version', 'name', 'size', 'data', 'metadata', 'palette']:
			if not self(name): raise Exception(f'Файл {filename} повреждён, нету переменной {name}')
		if self.name != name:
			raise Exception('Файл повреждён, имя файла и карты не совпадают')

		# подготовка к загрузке
		ox = int(self.size[0] // 2)
		oy = int(self.size[1] // 2)
		index = 0
		index_block = 0

		# загрузка карты
		while index < len(self.data):
			num = self.data[index]
			if num == 255:
				index += 1
				index_meta = int.from_bytes(self.data[index+1], byteorder='little')
			elif num == 254:
				index += 2
				index_meta = int.from_bytes(self.data[index+1:index+3], byteorder='little')
			elif num == 253:
				index += 3
				index_meta = int.from_bytes(self.data[index+1:index+4], byteorder='little')
			elif num == 252:
				index += 4
				index_meta = int.from_bytes(self.data[index+1:index+5], byteorder='little')
			elif num > 0:
				index_meta = -1
			else:
				index_meta = None

			if index_meta > -1:
				data = self.metadata[index_meta]
				num = data['id']

			if index_meta != None:
				id = self.palette[num]
				pos = ( int(index_block % self.size[0])-ox, int(index_block // self.size[0])-oy )
				self.add_block(id, pos)

			index += 1
			index_block += 1

# перевод старых карт в новые
# with open('maps/default.map', 'rb') as file:
# 	fdata = file.read()

# data = {
# 	'version': (0,0,1),
# 	'name': 'default',
# 	'size': (29, 11),
# 	'data': fdata,
# 	'metadata': [],
# 	'palette': {
# 		0: 'block',
# 		1: 'killer',
# 		2: 'jump',
# 		3: 'speed',
# 		4: 'home',
# 		5: 'fly',
# 	}
# }

# with open('maps/default.pickle', 'wb') as file:
# 	pickle.dump(data, file)


# data = {
# 	'version': (0,0,1),
# 	'name': 'test',
# 	'size': (1000, 1000),
# 	'data': b'',
# 	'metadata': [],
# 	'palette': {i: 'block' for i in range(251)}
# }


# import random

# counter = 0
# _1 = 2**8
# _2 = 2**16
# _3 = 2**24
# _4 = 2**32
# for _ in range(1000**2):
# 	if random.randint(0,99) < 50:
# 		if random.randint(0,99) < 10:
# 			if counter < _1:
# 				data['data'] += bytes([255])+counter.to_bytes(1, byteorder='little')
# 			elif counter < _2:
# 				data['data'] += bytes([254])+counter.to_bytes(2, byteorder='little')
# 			elif counter < _3:
# 				data['data'] += bytes([253])+counter.to_bytes(3, byteorder='little')
# 			elif counter < _4:
# 				data['data'] += bytes([252])+counter.to_bytes(4, byteorder='little')
# 			else:
# 				raise Exception('переполнение байтов')

# 			x = random.randint(-_2, _2)
# 			y = random.randint(-_2, _2)
# 			data['metadata'].append(
# 				{'tp':(x,y), 'id':random.randint(1,251)}
# 			)
# 			counter += 1
# 		else:
# 			data['data'] += bytes([random.randint(1,251)])
# 	else:
# 		data['data'] += bytes([0])


# with open('maps/test.pickle', 'wb') as file:
# 	pickle.dump(data, file)





# with open('maps/test.pickle', 'rb') as file:
# 	data = pickle.load(file)

# data['center'] = (0,0)

# with open('maps/test.pickle', 'wb') as file:
# 	pickle.dump(data, file)