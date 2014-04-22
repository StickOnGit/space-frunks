Wanted to see if I could roll my own pubsub library.

Nothing fancy here, nothing about concurrency or messaging servers, it's all just durdles.

Events are a subclass of list which can be called:

    myevent = Event(obj.foo, obj.bar)
    myevent() #will call the events in that order

Events are internally created by ListenObj instances.

    class MyClass(listenobj.ListenObj):
    	def __init__(self, x):
        	self.x = x
        	super(MyClass, self).__init__()
        def foo(self):
            self.x += 1
        def bar(self, y):
        	self.x += y

    Stick = MyClass(15)

Objects create their own events when they subscribe to a message.

    Stick.sub_to("tick", Stick.foo)

This subscribes the object to the "tick" message and creates an Event that contains Stick.foo.
Objects send messages using obj.pub().

    Stick.pub("tick")
    
Objects can unsubscribe using obj.unsub().

    Stick.unsub("tick")
    
On this initial commit, it's not a particularly fancy or smart library, it just does what it does. Perhaps it will do more later. But not now.
