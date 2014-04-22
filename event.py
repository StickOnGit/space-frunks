class Event(list):
	"""A list of functions to execute in the order given.
	Subclass of list, so has all the same methods as a list
	in addition to one additional to __call__ which allows the 
	Event object to be called as 'Event()'. Can pass it any 
	arguments and/or keyword arguments.
	"""
	def __init__(self, *args):
		super(Event, self).__init__(*args)

	def __call__(self, *args, **kwargs):
		"""This is what allows the object to be 
		called like a method.
		"""
		for func in self:
			func(*args, **kwargs)

	def __repr__(self):
		return "Event({})".format(list.__repr__(self))
