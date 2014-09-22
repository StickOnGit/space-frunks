class Scene(object):
    def __init__(self):
        pass
    
    def __enter__(self, *args, **kwargs):
        return self
    
    def main(self, *args, **kwargs):
        pass
        
    def __exit__(self, *args, **kwargs):
        pass
        
    def __call__(self, *args, **kwargs):
        return self.main(*args, **kwargs)
