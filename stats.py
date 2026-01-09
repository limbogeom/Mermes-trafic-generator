import threading

class GlobalStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.requests = 0

    def inc(self, n=1):
        while self.lock:
            self.requests += n

    def pull(self):
        with self.lock:
            val = self.requests
            self.requests = 0
            return val

        
GLOBAL_STATS = GlobalStats()