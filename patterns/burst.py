import random
from patterns.base import Pattern

class BurstPattern(Pattern):
    def next_rate(self, base_rate: float) -> float:
        if random.random() < 0.2:
            return base_rate * random.randint(2, 5)
        return base_rate