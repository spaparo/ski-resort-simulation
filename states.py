import time
import random


class State:
    def handle(self, visitor):
        raise NotImplementedError


class ArrivingState(State):
    def handle(self, visitor):
        visitor.log("arrives at the resort.")
        time.sleep(random.uniform(0.1, 0.5))


        if visitor.has_own_equipment:
            visitor.log("has own equipment...")
            visitor.has_equipment = True
            if visitor.is_ski_school:
                visitor.log("joining ski school...")
                return SkiSchoolState()
            return WaitingLiftState()

        visitor.log("moving to rental shop...")
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
        visitor.log("has equipment...")

        if visitor.is_ski_school:
            visitor.log("joining ski school...")
            return SkiSchoolState()

        visitor.log("Moving to the lift...")
        return WaitingLiftState()


class SkiSchoolState(State):
    def handle(self, visitor):
        visitor.log("is waiting for a ski school instructor...")

        ski_school = getattr(visitor.resort, "ski_school", None)
        if ski_school is None:
            visitor.log("no ski school available")
            return WaitingLiftState()

        success = ski_school.join_lesson(visitor)
        if not success:
            visitor.log("ski school is full, waiting for a spot...")
            time.sleep(0.5)
            return SkiSchoolState()

        visitor.log("completed ski school lesson! Heading to the beginner slope.")
        return SlopeState(force_beginner=True)

class WaitingLiftState(State):
    def handle(self, visitor):
        if visitor.resort and getattr(visitor.resort, "is_closing", False):
            visitor.log("resort is closing...leaving the resort.")
            return ExitState()
        visitor.log("is waiting in the lift queue...")

        success = visitor.resort.lift_station.use_lift(visitor)

        if not success:
            visitor.log("lift is full, waiting in lift queue...")
            time.sleep(0.5)
            return WaitingLiftState()

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
    def __init__(self, force_beginner=False):
        self.force_beginner = force_beginner

    def handle(self, visitor):
        if visitor.resort and getattr(visitor.resort, "is_closing", False):
            visitor.log("resort is closing...leaving.")
            return ExitState()

        if self.force_beginner:
            slope_name = "Beginner"
        else:
            slope_name = visitor.strategy.choose_slope(visitor)

        selected_slope = None
        for s in visitor.resort.slopes:
            if getattr(s, "name", None) == slope_name:
                selected_slope = s
                break
        if selected_slope is None:
            selected_slope = random.choice(visitor.resort.slopes)
            slope_name = getattr(selected_slope, "name", "Unknown")


        if getattr(selected_slope, "is_closed", False):
            visitor.log(f"{slope_name} is closed. Choosing a different slope...")

            open_slopes = [
                s for s in visitor.resort.slopes
                if not getattr(s, "is_closed", False)
            ]
            if not open_slopes:
                visitor.log("all slopes are closed! Heading to the café...")
                return CafeState()
            selected_slope = random.choice(open_slopes)
            slope_name = getattr(selected_slope, "name", "Unknown")

        cost = visitor.strategy.energy_cost()
        visitor.log(f"starting run #{visitor.runs_completed + 1} on {slope_name}")

        success, fell = selected_slope.go_down(visitor)


        energy_before = visitor.energy
        visitor.energy = max(0, visitor.energy - cost)
        visitor.runs_completed += 1
        visitor.log(f"finished run #{visitor.runs_completed}")
        visitor.log(
            f"energy used: {cost} — before: {energy_before}/100 — after: {visitor.energy}/100"
        )

        if fell:
            serious = _is_serious_fall(visitor)
            if serious:
                visitor.log("had a SERIOUS fall and needs first aid!")
                visitor.injury_status = "serious"
                return FirstAidState()
            else:
                visitor.log("fell but recovered.")
                visitor.injury_status = "minor"

        if visitor.strategy.should_leave(visitor):
            visitor.log("is too tired or done enough runs. Leaving!")

            if visitor.strategy.wants_apres_ski(visitor):
                visitor.log("stopping by après-ski first...")
                return ApresSkiState()
            return ExitState()

        if visitor.strategy.wants_restaurant():
            visitor.log("going to the restaurant for lunch...")
            return RestaurantState()

        if visitor.strategy.wants_cafe():
            visitor.log("going to the café for a quick break...")
            return CafeState()

        visitor.log("heading back to the lift!")
        return WaitingLiftState()

    def _is_serious_fall(visitor) -> bool:
        base_chance = 0.20  # 20% of falls become serious by default
        if visitor.age_group == "child":
            base_chance = 0.25
        elif visitor.age_group == "senior":
            base_chance = 0.35

        weather = "sunny"
        if visitor.resort and hasattr(visitor.resort, "weather"):
            weather = visitor.resort.weather
        if weather == "stormy":
            base_chance += 0.15
        elif weather == "snowy":
            base_chance += 0.08
        return random.random() < base_chance


class CafeState(State):
    ENERGY_RESTORE = 25

    def handle(self, visitor):
        visitor.log("is taking a break at the cafe...")

        success = visitor.resort.cafe.visit(visitor)

        if not success:
            visitor.log("cafe is full, waiting for a seat...")
            time.sleep(0.5)
            return CafeState()

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