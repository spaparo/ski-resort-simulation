import random
import time

from observers import StatsManager
from visitor import Visitor
from resources import RentalShop, LiftStation, Cafe, Slope
from database_manager import DatabaseManager
from config import (
    NUM_VISITORS,
    VISITOR_TYPES,
    NUM_SLOPES,
    ARRIVAL_INTERVAL_MIN,
    ARRIVAL_INTERVAL_MAX,
    PEAK_START_VISITOR,
    PEAK_END_VISITOR,
    PEAK_ARRIVAL_INTERVAL_MIN,
    PEAK_ARRIVAL_INTERVAL_MAX
)


class Resort:
    def __init__(self):
        self.stats = StatsManager()
        self.database = DatabaseManager()
        self.visitors = []
        self.is_open = False

        self.rental_shop = None
        self.lift_station = None
        self.cafe = None
        self.slopes = []

    def create_resources(self):
        self.rental_shop = RentalShop()
        self.lift_station = LiftStation()
        self.cafe = Cafe()
        self.slopes = [Slope() for _ in range(NUM_SLOPES)]

        self.rental_shop.add_observer(self.stats)
        self.lift_station.add_observer(self.stats)
        self.cafe.add_observer(self.stats)

        for slope in self.slopes:
            slope.add_observer(self.stats)

    def create_visitors(self):
        for i in range(NUM_VISITORS):
            visitor_type = random.choice(VISITOR_TYPES)

            visitor = Visitor(
                visitor_id=i,
                visitor_type=visitor_type,
                resort=self
            )

            self.visitors.append(visitor)
            self.stats.update("visitor_type", visitor_type)

            self.database.save_visitor(visitor)
            self.database.log_event(visitor.visitor_id, "created", "resort", 0)

    def start_threads(self):
        for index, visitor in enumerate(self.visitors):
            visitor.is_peak_arrival = PEAK_START_VISITOR <= index <= PEAK_END_VISITOR

            if index == PEAK_START_VISITOR:
                print("\n--- MIDDAY PEAK ARRIVAL PERIOD STARTED ---\n")

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
        print("Opening ski resort simulation...")

        self.database.create_tables()
        self.create_resources()
        self.create_visitors()

        self.start_threads()
        self.join_threads()

        self.is_open = False
        print("Closing ski resort simulation...")

        self.stats.show_summary()
        self.stats.show_graphs()

        self.database.close()