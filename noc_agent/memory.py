import time

class Memory:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self.store = {}  # key -> timestamp

    def seen_recently(self, key: str) -> bool:
        ts = self.store.get(key)
        if not ts:
            return False
        return (time.time() - ts) < self.ttl

    def mark(self, key: str):
        self.store[key] = time.time()
