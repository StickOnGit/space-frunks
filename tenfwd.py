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

def publish(message, *args, **kwargs):
	"""Sends message to observers."""
	for obj in Obvs[message]:
		getattr(obj, message)(*args, **kwargs)
		
def publish_with_results(message, *args, **kwargs):
	"""Same as publish, but returns list of results."""
	return [getattr(obj, message)(*args, **kwargs) for obj in Obvs[message]]
