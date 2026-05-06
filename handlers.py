import random
from config import CAFE_VISIT_CHANCE


class Handler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, visitor):
        if self.next_handler:
            return self.next_handler.handle(visitor)
        return True


class RentalHandler(Handler):
    def __init__(self, rental_shop, db, next_handler=None):
        super().__init__(next_handler)
        self.rental_shop = rental_shop
        self.db = db

    def handle(self, visitor):
        success, wait_time = self.rental_shop.rent_equipment(visitor)

        if success:
            self.db.log_event(visitor.visitor_id, "rental", "RentalShop", wait_time)
            return super().handle(visitor)
        return False


class LiftHandler(Handler):
    def __init__(self, lift, db, next_handler=None):
        super().__init__(next_handler)
        self.lift = lift
        self.db = db

    def handle(self, visitor):
        success, wait_time = self.lift.use_lift(visitor)

        if success:
            self.db.log_event(visitor.visitor_id, "lift", "LiftStation", wait_time)
            return super().handle(visitor)
        return False


class SlopeHandler(Handler):
    def __init__(self, slope, db, next_handler=None):
        super().__init__(next_handler)
        self.slope = slope
        self.db = db

    def handle(self, visitor):
        success, fell, wait_time = self.slope.go_down(visitor)

        if success:
            self.db.log_event(visitor.visitor_id, "slope", "Slope", wait_time)
            if fell:
                self.db.log_event(visitor.visitor_id, "fall", "Slope", 0)
            return super().handle(visitor)
        return False


class CafeHandler(Handler):
    def __init__(self, cafe, db, next_handler=None):
        super().__init__(next_handler)
        self.cafe = cafe
        self.db = db

    def handle(self, visitor):
        if random.random() < CAFE_VISIT_CHANCE:
            success, wait_time = self.cafe.visit(visitor)
            if success:
                self.db.log_event(visitor.visitor_id, "cafe", "Cafe", wait_time)
            else:
                return False

        return super().handle(visitor)


class ExitHandler(Handler):
    def __init__(self, db):
        super().__init__(None)
        self.db = db

    def handle(self, visitor):
        print(f"Visitor {visitor.visitor_id} finished the resort")
        self.db.log_event(visitor.visitor_id, "completed", "resort", 0)
        return True