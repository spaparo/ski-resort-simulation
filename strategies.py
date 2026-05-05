import random
from config import (
    ENERGY_LOSS_PER_RUN_SKIER,
    ENERGY_LOSS_PER_RUN_SNOWBOARDER,
    LEAVE_ENERGY_THRESHOLD,
    MAX_RUNS_PER_VISITOR,
    CAFE_VISIT_CHANCE
)


class SkierStrategy:
    ENERGY_COST = ENERGY_LOSS_PER_RUN_SKIER
    CAFE_PROBABILITY = CAFE_VISIT_CHANCE
    ENERGY_THRESHOLD = LEAVE_ENERGY_THRESHOLD
    MAX_RUNS = MAX_RUNS_PER_VISITOR


def choose_slope(self):
    slopes = ["Blue Slpe", "Red Slope", "Black Slope"]
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
    ENERGY_COST = ENERGY_LOSS_PER_RUN_SNOWBOARDER
    CAFE_PROBABILITY = 0.5
    ENERGY_THRESHOLD = LEAVE_ENERGY_THRESHOLD
    MAX_RUNS = MAX_RUNS_PER_VISITOR


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
