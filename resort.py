import random

from observers import StatsManager
from visitor import Visitor
from resources import RentalShop, LiftStation, Cafe, Slope
from database_manager import DatabaseManager
from config import NUM_VISITORS, VISITOR_TYPES, NUM_SLOPES


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
        self.slopes = [Slope(i) for i in range(NUM_SLOPES)]

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

            # Stats
            self.stats.update("visitor_type", visitor_type)

            # Database
            self.database.save_visitor(visitor)
            self.database.log_event(visitor.visitor_id, "created", "resort", 0)

    def start_threads(self):
        for visitor in self.visitors:
            visitor.start()

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
        self.database.close()