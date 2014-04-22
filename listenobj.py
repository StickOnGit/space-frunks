from event import Event
from weakmethod import WeakMethod
import eventhandler

class ListenObj(object):
	"""Base class for objects that can pubsub."""
	def __init__(self, *args, **kwargs):
		self._listening_for = {}
		
	def _got_msg(self, msg, *args, **kwargs):
		"""Used by the eventhandler to call the Event."""
		if msg in self._listening_for:
			self._listening_for[msg](*args, **kwargs)
	
	def sub_to(self, msg, *args):
		"""Subscribes the object to an event.
		Use a string to denote the event, and methods to 
		denote what the object will do in response.
		For example, subscribing to "click" would look like:
		
		obj.sub_to("click", self.foo)
		"""
		self._listening_for[msg] = Event()
		for arg in args:
			self._listening_for[msg].append(WeakMethod(self, arg))
		eventhandler._handler._add_listener(self, msg)
	
	def unsub(self, msg):
		"""Unsubscribes object from an event."""
		del self._listening_for[msg]
		eventhandler._handler._rm_listener(self, msg)
		
	def pub(self, msg, *args, **kwargs):
		"""Publish a message."""
		eventhandler._handler._tell(msg, *args, **kwargs)
