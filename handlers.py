import random


class Handler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, visitor):
        if self.next_handler:
            return self.next_handler.handle(visitor)
        return True


class RentalHandler(Handler):
    def __init__(self, rental_shop, next_handler=None):
        super().__init__(next_handler)
        self.rental_shop = rental_shop

    def handle(self, visitor):
        success = self.rental_shop.rent_equipment(visitor)

        if success:
            return super().handle(visitor)
        else:
            return False


class LiftHandler(Handler):
    def __init__(self, lift, next_handler=None):
        super().__init__(next_handler)
        self.lift = lift

    def handle(self, visitor):
        success = self.lift.use_lift(visitor)

        if success:
            return super().handle(visitor)
        else:
            return False


class SlopeHandler(Handler):
    def __init__(self, slope, next_handler=None):
        super().__init__(next_handler)
        self.slope = slope

    def handle(self, visitor):
        success = self.slope.go_down(visitor)

        if success:
            return super().handle(visitor)
        else:
            return False


class CafeHandler(Handler):
    def __init__(self, cafe, next_handler=None):
        super().__init__(next_handler)
        self.cafe = cafe

    def handle(self, visitor):
        # 35% chance to visit cafe
        if random.random() < 0.35:
            success = self.cafe.visit(visitor)
            if not success:
                return False

        return super().handle(visitor)



class ExitHandler(Handler):
    def handle(self, visitor):
        print(f"Visitor {visitor.id} finished the resort")
        return True