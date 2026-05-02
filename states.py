import time
import random


class State:
    def handle(self, visitor):
        raise NotImplementedError


class ArrivingState(State):
    def handle(self, visitor):
        visitor.log("arrives at the resort. Goes to rentals...")
        time.sleep(random.uniform(0.3, 0.7))
        return RentingState()


class RentingState(State):
    def handle(self, visitor):
        visitor.log("is getting equipment at the rental shop...")
        # TODO: replace with Marie's method -> rental_shop.rent_equipment(visitor)
        time.sleep(random.uniform(0.5, 1.0))
        visitor.log("has collected gear. Heading to the lift!")
        return WaitingLiftState()


class WaitingLiftState(State):
    def handle(self, visitor):
        visitor.log("is waiting for the lift...")
        # TODO: replace with Marie's method -> lift.use_lift(visitor)
        time.sleep(random.uniform(0.3, 0.8))
        return RidingLiftState()


class RidingLiftState(State):
    def handle(self, visitor):
        visitor.log("is riding the lift up the mountain...")
        time.sleep(random.uniform(0.5, 1.0))
        visitor.log("has reached the top")
        return SlopeState()


class SlopeState(State):
    def handle(self, visitor):
        slope = visitor.strategy.choose_slope()
        cost = visitor.strategy.energy_cost()

        visitor.log(f"is going down {slope}! (energy cost: {cost})")
        # TODO: replace with Marie's method -> slope.go_down(visitor)
        time.sleep(random.uniform(0.6, 1.2))

        visitor.energy = max(0, visitor.energy - cost)
        visitor.runs_completed += 1

        visitor.log(f"finished run #{visitor.runs_completed}. Energy: {visitor.energy}/100")

        if visitor.strategy.should_leave(visitor):
            visitor.log("is exhausted or satisfied. Time to leave!")
            return ExitState()

        if visitor.strategy.wants_cafe():
            return CafeState()

        return WaitingLiftState()


class CafeState(State):
    ENERGY_RESTORE = 25

    def handle(self, visitor):
        visitor.log("is taking a break at the cafe!")
        # TODO: replace with Marie's method -> cafe.visit(visitor)
        time.sleep(random.uniform(0.5, 1.0))

        visitor.energy = min(100, visitor.energy + self.ENERGY_RESTORE)
        visitor.cafe_visits += 1

        visitor.log(f"finished cafe break #{visitor.cafe_visits}. Energy restored to {visitor.energy}/100")

        if visitor.strategy.should_leave(visitor):
            return ExitState()

        return WaitingLiftState()


class ExitState(State):
    def handle(self, visitor):
        # TODO: replace with Marie's method -> rental_shop.return_equipment(visitor)
        visitor.log(
            f"is leaving. Summary -> "
            f"runs: {visitor.runs_completed}, "
            f"cafe visits: {visitor.cafe_visits}, "
            f"energy left: {visitor.energy}/100"
        )
        time.sleep(0.2)
        return None