from collections import defaultdict

Topics = defaultdict(list)	#dict to hold observers. key:value is "topic":list("objects")


def subscribe(obj, topic):
	"""Adds key-value pairs to the Topics dict.
	Keys are topics, values are placed in a list."""
	if obj not in Topics[topic]:
		Topics[topic].append(obj)
	
def unsub(obj, topic):
	"""Removes an observer from a topic."""
	try:
		Topics[topic].remove(obj)
	except ValueError:
		pass
	
def unsub_all(obj):
	for topic in Topics:
		try:
			Topics[topic].remove(obj)
		except ValueError:
			pass

def publish(topic, *args, **kwargs):
	"""Sends topic to observers."""
	for obj in Topics[topic]:
		getattr(obj, topic)(*args, **kwargs)
		
def publish_with_results(topic, *args, **kwargs):
	"""Same as publish, but returns list of results."""
	return [getattr(obj, topic)(*args, **kwargs) for obj in Topics[topic]]
