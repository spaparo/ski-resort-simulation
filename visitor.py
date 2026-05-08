from threading import Thread
import time
import random
from states import ArrivingState
from strategies import SkierStrategy, SnowboarderStrategy
from config import (
    MIN_RUNS_PER_VISITOR,
    MAX_RUNS_PER_VISITOR,
    STARTING_ENERGY,
    AGE_GROUPS,
    AGE_GROUP_PROBABILITIES,
    AGE_EFFECTS,
    SKILL_LEVELS,
    SKILL_LEVEL_PROBABILITIES,
    OWN_EQUIPMENT_CHANCE,
    SKI_SCHOOL_CHANCE,
    CHILD_SKI_SCHOOL_CHANCE,
)


class Visitor(Thread):
    def __init__(self, visitor_id, visitor_type, resort=None):
        self.visitor_id = visitor_id
        self.visitor_type = visitor_type
        self.resort = resort

        self.runs_completed = 0
        self.cafe_visits = 0
        self.restaurant_visits = 0
        self.apres_ski_visits = 0
        self.current_state = None
        self.has_equipment = False

        self.age_group = random.choices(
            AGE_GROUPS,
            weights=[AGE_GROUP_PROBABILITIES[a] for a in AGE_GROUPS]
        )[0]

        self.skill_level = random.choices(
            SKILL_LEVELS,
            weights=[SKILL_LEVEL_PROBABILITIES[s] for s in SKILL_LEVELS]
        )[0]


        energy_multiplier = AGE_EFFECTS[self.age_group]["energy_multiplier"]
        self.energy = STARTING_ENERGY / energy_multiplier


        self.has_own_equipment = random.random() < OWN_EQUIPMENT_CHANCE


        if self.age_group == "child":
            self.is_ski_school = random.random() < CHILD_SKI_SCHOOL_CHANCE
        else:
            self.is_ski_school = random.random() < SKI_SCHOOL_CHANCE


        self.injury_status = "none"


        self.target_runs = random.randint(MIN_RUNS_PER_VISITOR, MAX_RUNS_PER_VISITOR)

        if self.age_group == "child":
            self.target_runs = max(MIN_RUNS_PER_VISITOR, self.target_runs - 1)
        elif self.age_group == "senior":
            self.target_runs = max(MIN_RUNS_PER_VISITOR, self.target_runs - 2)


        if visitor_type == "skier":
            self.strategy = SkierStrategy(self.age_group, self.skill_level)
        else:
            self.strategy = SnowboarderStrategy(self.age_group, self.skill_level)

        self.current_state = ArrivingState()
        Thread.__init__(self, name=f"Thread-{visitor_id}", daemon=True)

    def log(self, message):
        ski_tag = " [SKI-SCHOOL]" if self.is_ski_school else ""
        print(
            f"[{self.visitor_id} | {self.visitor_type} | {self.age_group} | {self.skill_level}{ski_tag}] {message}",
            flush=True,
        )

    def run(self):
        self.log("thread started.")
        try:
            while self.current_state is not None:
                next_state = self.current_state.handle(self)
                self.current_state = next_state
        except Exception as e:
            self.log(f"error occurred: {e}")
            if self.resort is not None and getattr(self, "has_equipment", False):
                self.resort.rental_shop.return_equipment(self)
                self.has_equipment = False
        finally:
            self.log("thread ended.")