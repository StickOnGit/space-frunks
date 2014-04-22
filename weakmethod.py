from weakref import ref

class WeakMethod(object):
	"""Allows for a weak reference to a bound method."""
	def __init__(self, obj, func):
		self.obj = ref(obj)
		self.func = ref(func.__func__)
		
	def __call__(self, *args, **kwargs):
		if self.living():
			self.func()(self.obj(), *args, **kwargs)
			
	def living(self):
		if self.obj() is not None:
			return True
		else:
			return False

