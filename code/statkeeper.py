from tenfwd import subscribe as sub

class StatKeeper(dict):
    def __init__(self, *args, **kwargs):
        super(StatKeeper, self).__init__(*args, **kwargs)
        sub(self, 'save')
        sub(self, 'give')
        
    def save(self, k, v):
        self[k] = v
    
    def give(self, k):
        return self[k] if k in self else None