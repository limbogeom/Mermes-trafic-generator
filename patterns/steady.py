from patterns.base import Pattern

class SteadyPattern(Pattern):
    def next_rate(self, base_rate: float) -> float:
        return base_rate