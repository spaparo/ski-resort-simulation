import random


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
        success = self.rental_shop.rent_equipment(visitor)

        if success:
            self.db.log_event(visitor.id, "rental", "RentalShop", 0)
            return super().handle(visitor)
        else:
            return False


class LiftHandler(Handler):
    def __init__(self, lift, db, next_handler=None):
        super().__init__(next_handler)
        self.lift = lift
        self.db = db

    def handle(self, visitor):
        success = self.lift.use_lift(visitor)

        if success:
            self.db.log_event(visitor.id, "lift", "LiftStation", 0)
            return super().handle(visitor)
        else:
            return False


class SlopeHandler(Handler):
    def __init__(self, slope, db, next_handler=None):
        super().__init__(next_handler)
        self.slope = slope
        self.db = db

    def handle(self, visitor):
        success = self.slope.go_down(visitor)

        if success:
            self.db.log_event(visitor.id, "slope", "Slope", 0)
            return super().handle(visitor)
        else:
            return False


class CafeHandler(Handler):
    def __init__(self, cafe, db, next_handler=None):
        super().__init__(next_handler)
        self.cafe = cafe
        self.db = db

    def handle(self, visitor):
        if random.random() < 0.35:
            success = self.cafe.visit(visitor)
            if success:
                self.db.log_event(visitor.id, "cafe", "Cafe", 0)
            else:
                return False

        return super().handle(visitor)



class ExitHandler(Handler):
    def __init__(self, db):
        super().__init__(None)
        self.db = db

    def handle(self, visitor):
        print(f"Visitor {visitor.id} finished the resort")
        self.db.log_event(visitor.id, "completed", "resort", 0)
        return True