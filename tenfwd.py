from collections import defaultdict

Obvs = defaultdict(set)	#dict to hold observers. key:value is "message":set("objects")


def add_observer(obj, message):
	"""Adds key-value pairs to the Obvs dict.
	Keys are messages, values are placed in a set."""
	Obvs[message].add(obj)
	
def rm_observer(obj, message):
	"""Removes an observer from a message."""
	Obvs[message].remove(obj)
	
def rm_from_all(obj):
	for message in Obvs:
		if obj in Obvs[message]:
			Obvs[message].remove(obj)

def msg(obj, message=None, *args, **kwargs):
	if message is not None:
		return getattr(obj, message)(*args, **kwargs)
	else:
		if 'get' in kwargs:
			return getattr(obj, kwargs['get'])
		elif 'set' in kwargs:
			return setattr(obj, kwargs['set'][0], kwargs['set'][1])
			
def notify(obj, message, *args, **kwargs):
	"""Sends message to target and observers."""
	msg(obj, message, *args, **kwargs)
	publish(message, *args, **kwargs)
	
def publish(message, *args, **kwargs):
	"""Sends message to observers. No target."""
	for peep in Obvs[message]:
		msg(peep, message, *args, **kwargs)

###test class
class A(object):
	def __init__(self):
		self.x = 1235
	
	def foo(self, value=1):
		self.x += value
	
	def bar(self):
		return "Bar called - x is %d" % self.x
