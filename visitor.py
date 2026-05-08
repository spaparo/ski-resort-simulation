from threading import Thread
import time
import random

from states import ArrivingState
from strategies import SkierStrategy, SnowboarderStrategy
from config import (
    #MIN_RUNS_PER_VISITOR,
    #MAX_RUNS_PER_VISITOR,
    #AGE_GROUPS,
    #SKI_SCHOOL_CHANCE_CHILD,
   # SKI_SCHOOL_CHANCE_ADULT,
    #FAST_PASS_CHANCE,
    #OWN_EQUIPMENT_CHANCE,
)




class Visitor(Thread):
    def __init__(self, visitor_id, visitor_type, resort=None):
        self.visitor_id = visitor_id
        self.visitor_type = visitor_type
        self.resort = resort

        self.energy = 100
        self.runs_completed = 0
        self.cafe_visits = 0
        self.restaurant_visits = 0
        self.apres_ski_visits = 0
        self.current_state = None
        self.has_equipment = False

        self.age_group = random.choice(AGE_GROUPS)

        self.has_own_equipment = random.random() < OWN_EQUIPMENT_CHANCE

        if self.age_group == "child":
            self.is_ski_school = random.random() < SKI_SCHOOL_CHANCE_CHILD

        elif self.age_group == "adult":
            self.is_ski_group = random.random() < SKI_SCHOOL_CHANCE_ADULT

        else:
            self.is_ski_group = False

        self.injury_status = "none"

        self.target_runs = random.randint(MIN_RUNS_PER_VISITOR, MAX_RUNS_PER_VISITOR)

        if self.age_group == "child":
            self.target_runs = max(MIN_RUNS_PER_VISITOR, self.target_runs - 1)

         elif self.age_group == "senior":
             self.target_runs = max(MIN_RUNS_PER_VISITOR, self.target_runs - 2)

        if self.age_group == "senior":
            self.energy = 80
        elif self.age_group == "child":
            self.energy = 90
        else:
            self.energy = 100

        if visitor_type == "skier":
            self.strategy = SkierStrategy(self.age_group)
        else:
            self.strategy = SnowboarderStrategy(self.age_group)


        self.current_state = ArrivingState()

        Thread.__init__(self, name=f"Thread-{visitor_id}", daemon=True)

    def log(self, message):
        age_tag = f"{self.age_group}"
        ski_tag = " [SKI-SCHOOL]" if self.is_ski_school else ""
        print(
            f"[{self.visitor_id} | {self.visitor_type} | {age_tag}{fp_tag}{ski_tag}] {message}",
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

if __name__ == "__main__":

    visitors = [
        Visitor("V-001", "skier"),       # resort is None for now
        Visitor("V-002", "snowboarder"),
        Visitor("V-003", "skier"),
    ]

    for v in visitors:
        v.start()
        time.sleep(0.1)

    for v in visitors:
        v.join()