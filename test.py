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

# import re 

# components = PythonData()
# wait_components = PythonData()


# def my_decorator(*args, **kwargs):
# 	def decorator(func):
# 		def wrapper(*args, **kwargs):
# 			# Код, выполняющийся перед вызовом функции
# 			print("До выполнения функции")

# 			# Вызов функции с передачей аргументов
# 			result = func(*args, **kwargs)

# 			# Код, выполняющийся после вызова функции
# 			print("После выполнения функции")

# 			return result

# 		return wrapper

# 	if callable(param):
# 		return decorator(param)
# 	else:
# 		return decorator
		

# def component(*args, **kwargs):
# 	def _decorator(cls, id=None, req=[], *cls_args, **cls_kwargs):
# 		id = (id or re.findall(r"\w+(?='>)", str(cls))[0]).lower()
# 		for name in req:
# 			if not components(name):
# 				wait_components(id, [req, [cls, cls_args, cls_kwargs]])
# 				return

# 		print(cls_args)
# 		components(id, cls(components, *cls_args, **cls_kwargs))
# 		for id2, data in list(wait_components.items()):
# 			req = data[0]
# 			if id in req:
# 				req.pop(req.index(id))
# 			if len(req) == 0:
# 				cls, cls_args, cls_kwargs = data[1]
# 				components(id2, cls(components, *cls_args, **cls_kwargs))
# 				del wait_components[id2]


# 	if len(args) == 1 and type(args[0]) == type:
# 		cls = args[0]
# 		def _get_args(*cls_args, **cls_kwargs):
# 			_decorator(cls, cls_args=cls_args, cls_kwargs=cls_kwargs)
# 		return _get_args
# 	else:
# 		def _get_cls(cls):
# 			def _get_args(*cls_args, **cls_kwargs):
# 				return _decorator(cls, *args, cls_args=cls_args, cls_kwargs=cls_kwargs, **kwargs)
# 			return _get_args
# 		return _get_cls


# @component(req=('test2'))
# class Test:
# 	def __init__(self, app, name):
# 		self.app = app
# 		print(name)


# Test(123)


# @component()
# class Test2:
# 	def __init__(self, app, name):
# 		self.app = app
# 		print(name)


# Test2(321)

# import pickle

# class MapFile(dict):
# 	def __init__(self, mf=None):
# 		self.version = (0,0,0)
# 		self.name = None
# 		self.size = (0,0)
# 		self.data = b''
# 		self.metadata = []

# 		if type(mf) is dict:
# 			super().__init__(**mf)

# 	def __getattr__(self, name):
# 		if name in self: return self[name]

# 	def __setattr__(self, name, value):
# 		self[name] = value


# def save_map(path, mf):
# 	if not path.endswith('.pickle'):
# 		path += '.pickle'
# 	data = pickle.dumps(dict(mf))
# 	with open(path, 'wb') as file:
# 		file.write(data)

# def load_map(path):
# 	if not path.endswith('.pickle'):
# 		path += '.pickle'
# 	with open(path, 'rb') as file:
# 		data = file.read()
# 	return MapFile(pickle.loads(data))


# mf = MapFile()
# mf.size = (5,3)
# mf.data = bytes([0]*10) + bytes([255,1, 1, 1, 1, 255,2])
# mf.metadata.append({'teleport_to': (4,0)})
# mf.metadata.append({'teleport_to': (-4,0)})

# save_map('test.map', mf)

