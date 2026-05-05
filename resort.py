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
    ARRIVAL_INTERVAL_MAX
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

    def calculate_wait_time(self, queue_length, area):
        service_times = {
            "rental": 1.5,
            "lift": 2.2,
            "cafe": 1.8,
            "slope": 2.0
        }

        congestion_multiplier = {
            "rental": 1.0,
            "lift": 1.3,
            "cafe": 1.1,
            "slope": 1.2
        }

        base_time = queue_length * service_times[area]
        random_delay = random.uniform(0.5, 2.0)

        wait_time = (base_time * congestion_multiplier[area]) + random_delay

        return round(wait_time, 2)

    def record_queue_and_wait(self, area, queue_length, visitor_id=None):
        wait_time = self.calculate_wait_time(queue_length, area)

        self.stats.update(f"{area}_queue", queue_length)
        self.stats.update(f"{area}_wait", wait_time)

        if visitor_id is not None:
            self.database.log_event(visitor_id, f"{area}_wait", area, wait_time)

        return wait_time

    def start_threads(self):
        for visitor in self.visitors:
            visitor.start()

            # Stagger arrivals so visitors enter the resort gradually instead of all at once.
            time.sleep(random.uniform(ARRIVAL_INTERVAL_MIN, ARRIVAL_INTERVAL_MAX))

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
