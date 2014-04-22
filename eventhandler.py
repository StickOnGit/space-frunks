from weakref import ref


class Satellite(dict):
	"""Coordinates the message passing between
	ListenObj instances.
	
	At present the goal is to never have to think about
	this, so it is basically setup to durdle in the background.
	"""
	def __init__(self):
		super(dict, self).__init__()

	def __repr__(self):
		msgs = ""
		for k, v in self.iteritems():
			msgs += "\n(Message: {}, Listeners: {})\n".format(k, len(v))
		return "Satellite({})".format(msgs)

	def _tell(self, msg, *args, **kwargs):
		"""If the message is a key, send message to the live references in the value."""
		if msg in self:
			for live_listener in [listener for listener in self[msg] if listener() is not None]:
				live_listener()._got_msg(msg, *args, **kwargs)

	def _add_listener(self, listener, msg):
		if msg not in self:
			self[msg] = []
		if listener not in self[msg]:
			self[msg].append(ref(listener))

	def _rm_listener(self, listener, msg):
		if msg in self:
			if listener in self[msg]:
				self[msg].remove(listener)
			if not self[msg]:
				del self[msg]

	def _cleanse(self):
		"""Get a list of dead references and remove them."""
		for msg in self:
			for dead_listener in [listener for listener in self[msg] if listener() is None]:
				self[msg].remove(dead_listener)


_handler = Satellite()
