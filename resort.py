import random
import time

from observers import StatsManager
from visitor import Visitor
from database_manager import DatabaseManager
from strategies import SkierStrategy, SnowboarderStrategy

from resources import (
    RentalShop,
    LiftStation,
    Cafe,
    Slope,
    Restaurant,
    ApresSki,
    FirstAidStation,
    InstructorPool,
    EquipmentReturnDesk
)

from config import (
    NUM_VISITORS,
    VISITOR_TYPES,
    SLOPE_CONFIGS,
    WEATHER_OPTIONS,
    AGE_GROUPS,
    AGE_GROUP_PROBABILITIES,
    SKILL_LEVELS,
    SKILL_LEVEL_PROBABILITIES,
    OWN_EQUIPMENT_CHANCE,
    SKI_SCHOOL_CHANCE,
    CHILD_SKI_SCHOOL_CHANCE,
    ARRIVAL_INTERVAL_MIN,
    ARRIVAL_INTERVAL_MAX,
    PEAK_START_VISITOR,
    PEAK_END_VISITOR,
    PEAK_ARRIVAL_INTERVAL_MIN,
    PEAK_ARRIVAL_INTERVAL_MAX,
    LUNCH_START_VISITOR,
    LUNCH_END_VISITOR,
    LAST_LIFT_VISITOR,
    RESORT_CLOSE_VISITOR,
    STARTING_ENERGY,
    MIN_RUNS_PER_VISITOR,
    MAX_RUNS_PER_VISITOR,
    AGE_EFFECTS
)


class Resort:
    def __init__(self):
        self.stats = StatsManager()
        self.database = DatabaseManager()
        self.visitors = []

        self.is_open = False
        self.is_closing = False
        self.weather = random.choice(WEATHER_OPTIONS)
        self.phase = "morning"

        self.rental_shop = None
        self.lift_station = None
        self.cafe = None
        self.restaurant = None
        self.apres_ski = None
        self.first_aid = None
        self.instructor_pool = None
        self.ski_school = None
        self.return_desk = None
        self.equipment_return = None
        self.slopes = []

    def weighted_choice(self, items, probabilities):
        weights = [probabilities[item] for item in items]
        return random.choices(items, weights=weights, k=1)[0]

    def get_phase(self, visitor_index):
        if visitor_index >= RESORT_CLOSE_VISITOR:
            return "closed"

        if visitor_index >= LAST_LIFT_VISITOR:
            return "closing"

        if LUNCH_START_VISITOR <= visitor_index <= LUNCH_END_VISITOR:
            return "lunch"

        if visitor_index > LUNCH_END_VISITOR:
            return "afternoon"

        return "morning"

    def create_resources(self):
        self.rental_shop = RentalShop()
        self.lift_station = LiftStation()
        self.cafe = Cafe()
        self.restaurant = Restaurant()
        self.apres_ski = ApresSki()
        self.first_aid = FirstAidStation()
        self.instructor_pool = InstructorPool()
        self.ski_school = self.instructor_pool
        self.return_desk = EquipmentReturnDesk()
        self.equipment_return = self.return_desk

        self.slopes = [
            Slope(slope_config=slope_config)
            for slope_config in SLOPE_CONFIGS
        ]

        resources = [
            self.rental_shop,
            self.lift_station,
            self.cafe,
            self.restaurant,
            self.apres_ski,
            self.first_aid,
            self.instructor_pool,
            self.equipment_return
        ]

        for resource in resources:
            resource.add_observer(self.stats)

        for slope in self.slopes:
            slope.add_observer(self.stats)

        self.stats.update("weather", self.weather)

    def create_visitors(self):
        for i in range(NUM_VISITORS):
            visitor_type = random.choice(VISITOR_TYPES)

            age_group = self.weighted_choice(
                AGE_GROUPS,
                AGE_GROUP_PROBABILITIES
            )

            skill_level = self.weighted_choice(
                SKILL_LEVELS,
                SKILL_LEVEL_PROBABILITIES
            )

            has_own_equipment = random.random() < OWN_EQUIPMENT_CHANCE

            if age_group == "child":
                is_ski_school = random.random() < CHILD_SKI_SCHOOL_CHANCE
            else:
                is_ski_school = random.random() < SKI_SCHOOL_CHANCE

            visitor = Visitor(
                visitor_id=i,
                visitor_type=visitor_type,
                resort=self
            )

            # Visitor profile is assigned here only.
            visitor.age_group = age_group
            visitor.skill_level = skill_level
            visitor.has_own_equipment = has_own_equipment
            visitor.is_ski_school = is_ski_school
            visitor.group_id = i // 8 if is_ski_school else None
            visitor.injury_status = "none"
            visitor.staff_fatigue_active = False
            visitor.is_peak_arrival = False
            visitor.day_phase = "morning"

            # Energy depends on age group.
            energy_multiplier = AGE_EFFECTS[age_group]["energy_multiplier"]
            visitor.energy = STARTING_ENERGY / energy_multiplier

            # Target runs also depends on age group.
            visitor.target_runs = random.randint(
                MIN_RUNS_PER_VISITOR,
                MAX_RUNS_PER_VISITOR
            )

            if age_group == "child":
                visitor.target_runs = max(
                    MIN_RUNS_PER_VISITOR,
                    visitor.target_runs - 1
                )
            elif age_group == "senior":
                visitor.target_runs = max(
                    MIN_RUNS_PER_VISITOR,
                    visitor.target_runs - 2
                )

            # Strategy depends on visitor type, age group, and skill level.
            if visitor_type == "skier":
                visitor.strategy = SkierStrategy(age_group, skill_level)
            else:
                visitor.strategy = SnowboarderStrategy(age_group, skill_level)

            self.visitors.append(visitor)

            # Stats tracking
            self.stats.update("visitor_type", visitor_type)
            self.stats.update("age_group", age_group)
            self.stats.update("skill_level", skill_level)

            if has_own_equipment:
                self.stats.update("own_equipment")
            else:
                self.stats.update("rental_equipment")

            if is_ski_school:
                self.stats.update("ski_school")

            # Database logging
            self.database.save_visitor(visitor)

            self.database.log_event(
                visitor.visitor_id,
                "created",
                "resort",
                0,
                weather=self.weather,
                age_group=age_group,
                skill_level=skill_level,
                own_equipment=has_own_equipment,
                ski_school=is_ski_school
            )

    def start_threads(self):
        for index, visitor in enumerate(self.visitors):
            self.phase = self.get_phase(index)
            self.is_closing = self.phase in ["closing", "closed"]

            visitor.day_phase = self.phase
            visitor.is_peak_arrival = PEAK_START_VISITOR <= index <= PEAK_END_VISITOR

            if index == PEAK_START_VISITOR:
                print("\n--- MIDDAY PEAK ARRIVAL PERIOD STARTED ---\n")

            if index == LUNCH_START_VISITOR:
                print("\n--- LUNCH PERIOD STARTED ---\n")

            if index == LUNCH_END_VISITOR:
                print("\n--- LUNCH PERIOD ENDED ---\n")

            if index == LAST_LIFT_VISITOR:
                print("\n--- LAST LIFT PERIOD STARTED ---\n")

            visitor.start()

            if visitor.is_peak_arrival:
                time.sleep(random.uniform(
                    PEAK_ARRIVAL_INTERVAL_MIN,
                    PEAK_ARRIVAL_INTERVAL_MAX
                ))
            else:
                time.sleep(random.uniform(
                    ARRIVAL_INTERVAL_MIN,
                    ARRIVAL_INTERVAL_MAX
                ))

            if index == PEAK_END_VISITOR:
                print("\n--- MIDDAY PEAK ARRIVAL PERIOD ENDED ---\n")

    def join_threads(self):
        for visitor in self.visitors:
            visitor.join()

    def start_simulation(self):
        self.is_open = True
        self.is_closing = False

        print("Opening full ski resort simulation...")
        print(f"Visitors: {NUM_VISITORS}")
        print(f"Weather today: {self.weather}")

        self.database.create_tables()
        self.create_resources()
        self.create_visitors()
        self.start_threads()
        self.join_threads()

        self.phase = "closed"
        self.is_closing = True
        self.is_open = False

        print("Closing ski resort simulation...")

        self.stats.show_summary()
        self.stats.show_graphs()

        self.database.close()