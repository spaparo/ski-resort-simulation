from threading import Thread
import random

from states import ArrivingState
from config import (
    MIN_RUNS_PER_VISITOR,
    MAX_RUNS_PER_VISITOR,
    STARTING_ENERGY
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
        self.first_aid_visits = 0
        self.instructor_visits = 0
        self.equipment_returns = 0

        self.current_state = ArrivingState()
        self.has_equipment = False
        self.has_own_equipment = False

        self.age_group = None
        self.skill_level = None
        self.is_ski_school = False
        self.group_id = None
        self.injury_status = "none"

        self.staff_fatigue_active = False
        self.is_peak_arrival = False
        self.day_phase = "morning"


        self.energy = STARTING_ENERGY
        self.target_runs = random.randint(
            MIN_RUNS_PER_VISITOR,
            MAX_RUNS_PER_VISITOR
        )
        self.strategy = None

        Thread.__init__(self, name=f"Thread-{visitor_id}", daemon=True)

    def log(self, message):
        ski_tag = " [SKI-SCHOOL]" if self.is_ski_school else ""
        print(
            f"[{self.visitor_id} | {self.visitor_type} | "
            f"{self.age_group} | {self.skill_level}{ski_tag}] {message}",
            flush=True
        )

    def run(self):
        self.log("thread started.")

        try:
            while self.current_state is not None:
                next_state = self.current_state.handle(self)
                self.current_state = next_state

        except Exception as e:
            self.log(f"error occurred: {e}")

            # Safety cleanup: if something breaks, return rented equipment.
            if self.resort is not None and getattr(self, "has_equipment", False):
                if not getattr(self, "has_own_equipment", False):
                    self.resort.return_desk.return_equipment(self)
                self.has_equipment = False

        finally:
            self.log("thread ended.")