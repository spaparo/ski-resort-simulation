import time
import random


class State:
    def handle(self, visitor):
        raise NotImplementedError


class ArrivingState(State):
    def handle(self, visitor):
        visitor.log("arrives at the resort.")
        visitor.log("moving to rental shop...")
        time.sleep(random.uniform(0.1, 0.5))
        return RentingState()


class RentingState(State):
    def handle(self, visitor):
        visitor.log("is getting equipment at the rental shop...")

        success = visitor.resort.rental_shop.rent_equipment(visitor)

        if not success:
            visitor.log("rental shop is busy, waiting in rental queue...")
            time.sleep(0.5)
            return RentingState()

        visitor.has_equipment = True

        visitor.resort.database.log_event(
            visitor.visitor_id,
            "rental",
            "RentalShop",
            0
        )

        visitor.log("has collected gear. Moving to the lift...")
        return WaitingLiftState()


class WaitingLiftState(State):
    def handle(self, visitor):
        visitor.log("is waiting in the lift queue...")

        success = visitor.resort.lift_station.use_lift(visitor)

        if not success:
            visitor.log("lift is full, waiting in lift queue...")
            time.sleep(0.5)
            return WaitingLiftState()

        visitor.resort.database.log_event(
            visitor.visitor_id,
            "lift",
            "LiftStation",
            0
        )

        visitor.log("got on the lift!")
        return RidingLiftState()


class RidingLiftState(State):
    def handle(self, visitor):
        visitor.log("is riding the lift up the mountain...")
        time.sleep(random.uniform(0.5, 1.0))
        visitor.resort.lift_station.leave_lift()
        visitor.log("has reached the top!")
        return SlopeState()


class SlopeState(State):
    def handle(self, visitor):
        slope = visitor.strategy.choose_slope()
        cost = visitor.strategy.energy_cost()

        visitor.log(f"starting run #{visitor.runs_completed + 1} on {slope}")

        visitor.resort.slopes[0].go_down(visitor)

        visitor.resort.database.log_event(
            visitor.visitor_id,
            "slope",
            "Slope",
            0
        )

        energy_before = visitor.energy
        visitor.energy = max(0, visitor.energy - cost)
        visitor.runs_completed += 1

        visitor.log(f"finished run #{visitor.runs_completed}")
        visitor.log(f"energy used: {cost} — before: {energy_before}/100 — after: {visitor.energy}/100")

        if visitor.strategy.should_leave(visitor):
            visitor.log("is too tired or done enough runs. Leaving!")
            return ExitState()

        if visitor.strategy.wants_cafe():
            visitor.log("going to the cafe...")
            return CafeState()

        visitor.log("heading back to the lift!")
        return WaitingLiftState()


class CafeState(State):
    ENERGY_RESTORE = 25

    def handle(self, visitor):
        visitor.log("is taking a break at the cafe...")

        success = visitor.resort.cafe.visit(visitor)

        if not success:
            visitor.log("cafe is full, waiting for a seat...")
            time.sleep(0.5)
            return CafeState()

        visitor.resort.database.log_event(
            visitor.visitor_id,
            "cafe",
            "Cafe",
            0
        )

        energy_before = visitor.energy
        visitor.energy = min(100, visitor.energy + self.ENERGY_RESTORE)
        visitor.cafe_visits += 1

        visitor.log(f"cafe visit #{visitor.cafe_visits} done!")
        visitor.log(f"energy: {energy_before}/100 -> {visitor.energy}/100")

        if visitor.strategy.should_leave(visitor):
            visitor.log("still too tired. Heading home...")
            return ExitState()

        visitor.log("feeling better! Back to the lift...")
        return WaitingLiftState()


class ExitState(State):
    def handle(self, visitor):
        visitor.log("is returning equipment and leaving...")

        visitor.resort.rental_shop.return_equipment(visitor)
        visitor.has_equipment = False

        visitor.log(
            f"--- SUMMARY --- "
            f"runs: {visitor.runs_completed} | "
            f"cafe visits: {visitor.cafe_visits} | "
            f"energy left: {visitor.energy}/100"
        )

        if visitor.resort is not None:
            visitor.resort.stats.update("visitor_summary", {
                "runs": visitor.runs_completed,
                "cafe_visits": visitor.cafe_visits,
                "energy_left": visitor.energy,
                "type": visitor.visitor_type
            })

            visitor.resort.database.log_event(
                visitor.visitor_id,
                "completed",
                "resort",
                0
            )

            visitor.resort.database.update_visitor_summary(visitor)

        return None