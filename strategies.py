import random


class SkierStrategy:

    ENERGY_COST = 20
    CAFE_PROBABILITY = 0.3
    ENERGY_THRESHOLD = 25
    MAX_RUNS = 6

    def choose_slope(self):
        slopes = ["Blue Slope", "Red Slope", "Black Slope"]
        return random.choice(slopes)

    def energy_cost(self):
        return self.ENERGY_COST + random.randint(-5, 5)

    def cafe_probability(self):
        return self.CAFE_PROBABILITY

    def should_leave(self, visitor):
        too_tired = visitor.energy < self.ENERGY_THRESHOLD
        enough_runs = visitor.runs_completed >= self.MAX_RUNS
        return too_tired or enough_runs

    def wants_cafe(self):
        return random.random() < self.CAFE_PROBABILITY


class SnowboarderStrategy:

    ENERGY_COST = 28
    CAFE_PROBABILITY = 0.5
    ENERGY_THRESHOLD = 20
    MAX_RUNS = 5

    def choose_slope(self):
        slopes = ["Red Slope", "Black Slope", "Blue Slope"]
        return random.choice(slopes)

    def energy_cost(self):
        return self.ENERGY_COST + random.randint(-3, 8)

    def cafe_probability(self):
        return self.CAFE_PROBABILITY

    def should_leave(self, visitor):
        too_tired = visitor.energy < self.ENERGY_THRESHOLD
        enough_runs = visitor.runs_completed >= self.MAX_RUNS
        return too_tired or enough_runs

    def wants_cafe(self):
        return random.random() < self.CAFE_PROBABILITY