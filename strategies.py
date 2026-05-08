import random
from config import (
    ENERGY_LOSS_PER_RUN_SKIER,
    ENERGY_LOSS_PER_RUN_SNOWBOARDER,
    LEAVE_ENERGY_THRESHOLD,
    CAFE_VISIT_CHANCE,
    RESTAURANT_VISIT_CHANCE,
    APRES_SKI_VISIT_CHANCE,
    SKILL_EFFECTS,
    WEATHER_EFFECTS,
    AGE_EFFECTS,
)


def _pick_slope_for(visitor_type, age_group, skill_level, is_ski_school, weather):
    """
    Rules:
    - Ski-school visitors        -> always Green
    - Children                   -> Green or Blue only
    - Seniors                    -> Green or Blue only
    - Everyone else              -> preferred slopes from their skill level
    - Foggy / snowy weather      -> drop one level safer for all
    """
    if is_ski_school:
        return "Green"

    if age_group == "child":
        pool = ["Green", "Blue"]
    elif age_group == "senior":
        pool = ["Green", "Blue"]
    else:
        pool = list(SKILL_EFFECTS[skill_level]["preferred_slopes"])

    weather_effect = WEATHER_EFFECTS.get(weather, WEATHER_EFFECTS["sunny"])
    fall_mult = weather_effect["fall_multiplier"]
    if fall_mult >= 1.5:
        pool = [pool[0]]
    elif fall_mult >= 1.2:
        if len(pool) > 1:
            pool = pool[:-1]

    return random.choice(pool)


class BaseStrategy:
    ENERGY_THRESHOLD = LEAVE_ENERGY_THRESHOLD

    def __init__(self, age_group: str, skill_level: str):
        self.age_group = age_group
        self.skill_level = skill_level

    def choose_slope(self, visitor):
        weather = "sunny"
        if visitor.resort and hasattr(visitor.resort, "weather"):
            weather = visitor.resort.weather
        return _pick_slope_for(
            visitor.visitor_type,
            self.age_group,
            self.skill_level,
            visitor.is_ski_school,
            weather,
        )

    def energy_cost(self):
        raise NotImplementedError

    def should_leave(self, visitor):
        if visitor.resort and getattr(visitor.resort, "is_closing", False):
            return True
        too_tired   = visitor.energy < self._energy_threshold()
        enough_runs = visitor.runs_completed >= visitor.target_runs
        return too_tired or enough_runs

    def _energy_threshold(self):
        if self.age_group == "senior":
            return self.ENERGY_THRESHOLD + 10
        if self.age_group == "child":
            return self.ENERGY_THRESHOLD + 5
        return self.ENERGY_THRESHOLD

    def wants_cafe(self):
        base = CAFE_VISIT_CHANCE * AGE_EFFECTS[self.age_group]["break_multiplier"]
        return random.random() < base

    def wants_restaurant(self):
        base = RESTAURANT_VISIT_CHANCE * AGE_EFFECTS[self.age_group]["break_multiplier"]
        return random.random() < base

    def wants_apres_ski(self, visitor):
        if self.age_group == "child":
            return False
        if visitor.is_ski_school:
            return False
        return random.random() < APRES_SKI_VISIT_CHANCE


class SkierStrategy(BaseStrategy):
    ENERGY_COST = ENERGY_LOSS_PER_RUN_SKIER

    def __init__(self, age_group: str = "adult", skill_level: str = "intermediate"):
        super().__init__(age_group, skill_level)

    def energy_cost(self):
        base = self.ENERGY_COST
        age_mult = AGE_EFFECTS[self.age_group]["energy_multiplier"]
        return (base * age_mult) + random.randint(-3, 5)


class SnowboarderStrategy(BaseStrategy):
    ENERGY_COST = ENERGY_LOSS_PER_RUN_SNOWBOARDER

    def __init__(self, age_group: str = "adult", skill_level: str = "intermediate"):
        super().__init__(age_group, skill_level)

    def energy_cost(self):
        base = self.ENERGY_COST
        age_mult = AGE_EFFECTS[self.age_group]["energy_multiplier"]
        return (base * age_mult) + random.randint(-3, 8)