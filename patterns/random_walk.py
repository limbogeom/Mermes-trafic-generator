import random
from patterns.base import Pattern

class RandomWalkPattern(Pattern):
    def next_rate(self, base_rate: float) -> float:
        change = random.uniform(0.5, 1.5)
        return max(0.1, base_rate * change)