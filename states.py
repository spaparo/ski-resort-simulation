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
            visitor.log("has own equipment — skipping rental shop.")
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
        visitor.log("has collected gear.")

        if visitor.is_ski_school:
            visitor.log("joining ski school before hitting the slopes...")
            return SkiSchoolState()

        visitor.log("moving to the lift...")
        return WaitingLiftState()


class SkiSchoolState(State):
    def handle(self, visitor):
        visitor.log("is waiting for a ski school instructor...")

        ski_school = getattr(visitor.resort, "ski_school", None)

        if ski_school is None:
            visitor.log("no ski school available — going straight to the lift.")
            return WaitingLiftState()

        success = ski_school.join_lesson(visitor)

        if not success:
            visitor.log("ski school is full, waiting for a spot...")
            time.sleep(0.5)
            return SkiSchoolState()

        visitor.instructor_visits += 1
        visitor.log("completed ski school lesson! Heading to the Green slope.")
        return SlopeState(force_beginner=True)


class WaitingLiftState(State):
    def handle(self, visitor):
        if visitor.resort and getattr(visitor.resort, "is_closing", False):
            visitor.log("resort is closing — heading home without another run.")
            visitor.resort.stats.update("closing_affected")
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
            visitor.log("resort is closing — skipping this run and leaving.")
            visitor.resort.stats.update("closing_affected")
            return ExitState()

        if self.force_beginner:
            slope_name = "Green"
        else:
            slope_name = visitor.strategy.choose_slope(visitor)

        selected_slope = None

        for slope in visitor.resort.slopes:
            if getattr(slope, "name", None) == slope_name:
                selected_slope = slope
                break

        if selected_slope is None:
            selected_slope = random.choice(visitor.resort.slopes)
            slope_name = getattr(selected_slope, "name", "Unknown")

        if not getattr(selected_slope, "is_open", True):
            visitor.log(f"{slope_name} is closed. Choosing a different slope...")

            open_slopes = [
                slope for slope in visitor.resort.slopes
                if getattr(slope, "is_open", True)
            ]

            if not open_slopes:
                visitor.log("all slopes are closed! Heading to the café...")
                return CafeState()

            selected_slope = random.choice(open_slopes)
            slope_name = getattr(selected_slope, "name", "Unknown")

        cost = visitor.strategy.energy_cost()

        visitor.log(f"starting run #{visitor.runs_completed + 1} on {slope_name}")

        success, fell = selected_slope.go_down(visitor)

        if not success:
            visitor.log("could not use this slope, trying again...")
            time.sleep(0.5)
            return SlopeState(force_beginner=self.force_beginner)

        energy_before = visitor.energy
        visitor.energy = max(0, visitor.energy - cost)
        visitor.runs_completed += 1

        visitor.log(f"finished run #{visitor.runs_completed}")
        visitor.log(
            f"energy used: {cost:.1f} — before: {energy_before:.1f}/100 "
            f"— after: {visitor.energy:.1f}/100"
        )

        if fell:
            if visitor.injury_status == "serious":
                visitor.log("had a SERIOUS fall and needs first aid!")
                return FirstAidState()

            visitor.log("fell but recovered.")
            visitor.injury_status = "minor"

        if visitor.strategy.should_leave(visitor):
            visitor.log("is done for the day. Heading home!")

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


class CafeState(State):
    ENERGY_RESTORE = 25

    def handle(self, visitor):
        visitor.log("is taking a quick break at the café...")

        success = visitor.resort.cafe.visit(visitor)

        if not success:
            visitor.log("café is full, waiting for a seat...")
            time.sleep(0.5)
            return CafeState()

        energy_before = visitor.energy
        visitor.energy = min(100, visitor.energy + self.ENERGY_RESTORE)
        visitor.cafe_visits += 1

        visitor.log(f"café visit #{visitor.cafe_visits} done!")
        visitor.log(f"energy: {energy_before:.1f}/100 -> {visitor.energy:.1f}/100")

        if visitor.strategy.should_leave(visitor):
            visitor.log("still too tired after the café. Heading home...")
            return ExitState()

        visitor.log("feeling better! Back to the lift...")
        return WaitingLiftState()


class RestaurantState(State):
    ENERGY_RESTORE = 40

    def handle(self, visitor):
        visitor.log("is sitting down for lunch at the restaurant...")

        restaurant = getattr(visitor.resort, "restaurant", None)

        if restaurant is None:
            visitor.log("no restaurant available — going to the café instead.")
            return CafeState()

        success = restaurant.visit(visitor)

        if not success:
            visitor.log("restaurant is full, waiting for a table...")
            time.sleep(0.5)
            return RestaurantState()

        energy_before = visitor.energy
        visitor.energy = min(100, visitor.energy + self.ENERGY_RESTORE)
        visitor.restaurant_visits += 1

        visitor.log(
            f"restaurant visit #{visitor.restaurant_visits} done! "
            f"energy: {energy_before:.1f}/100 -> {visitor.energy:.1f}/100"
        )

        if visitor.strategy.should_leave(visitor):
            visitor.log("feeling full but still tired. Heading home...")
            return ExitState()

        visitor.log("well fed! Back to the slopes...")
        return WaitingLiftState()


class ApresSkiState(State):
    def handle(self, visitor):
        visitor.log("is enjoying après-ski!")

        apres_ski = getattr(visitor.resort, "apres_ski", None)

        if apres_ski is None:
            visitor.log("no après-ski bar yet — heading straight home.")
            return ExitState()

        success = apres_ski.visit(visitor)

        if not success:
            visitor.log("après-ski is packed, skipping it...")
            return ExitState()

        visitor.apres_ski_visits += 1
        visitor.log("had a great time at après-ski! Now heading home.")

        return ExitState()


class FirstAidState(State):
    ENERGY_RESTORE_SERIOUS = 10
    ENERGY_RESTORE_MINOR = 20

    def handle(self, visitor):
        is_serious = visitor.injury_status == "serious"

        if is_serious:
            visitor.log("SERIOUS injury — being rushed to first aid!")
        else:
            visitor.log("minor injury — heading to first aid.")

        first_aid = getattr(visitor.resort, "first_aid", None)

        if first_aid is None:
            visitor.log("no first aid station — resting and heading home.")
            time.sleep(1.0)
            visitor.injury_status = "treated"
            return ExitState()

        success = first_aid.treat(visitor)

        if not success:
            visitor.log("first aid is busy, waiting...")
            time.sleep(0.5)
            return FirstAidState()

        visitor.first_aid_visits += 1

        if is_serious:
            energy_restore = self.ENERGY_RESTORE_SERIOUS
        else:
            energy_restore = self.ENERGY_RESTORE_MINOR

        energy_before = visitor.energy
        visitor.energy = min(100, visitor.energy + energy_restore)
        visitor.injury_status = "treated"

        visitor.log(
            f"has been treated! energy: {energy_before:.1f}/100 "
            f"-> {visitor.energy:.1f}/100"
        )

        visitor.log("doctor's orders: calling it a day.")
        return ExitState()


class ExitState(State):
    def handle(self, visitor):
        visitor.log("is returning equipment and leaving...")

        if visitor.has_equipment and not visitor.has_own_equipment:
            success = visitor.resort.return_desk.return_equipment(visitor)

            if not success:
                visitor.log("equipment return is busy, waiting...")
                time.sleep(0.5)
                return ExitState()

            visitor.equipment_returns += 1
            visitor.has_equipment = False

        visitor.log(
            f"--- SUMMARY --- "
            f"runs: {visitor.runs_completed} | "
            f"café: {visitor.cafe_visits} | "
            f"restaurant: {visitor.restaurant_visits} | "
            f"après-ski: {visitor.apres_ski_visits} | "
            f"first aid: {visitor.first_aid_visits} | "
            f"equipment returns: {visitor.equipment_returns} | "
            f"injury: {visitor.injury_status} | "
            f"energy left: {visitor.energy:.1f}/100"
        )

        if visitor.resort is not None:
            visitor.resort.stats.update("visitor_summary", {
                "type": visitor.visitor_type,
                "age_group": visitor.age_group,
                "skill_level": visitor.skill_level,
                "has_own_equipment": visitor.has_own_equipment,
                "is_ski_school": visitor.is_ski_school,
                "runs": visitor.runs_completed,
                "cafe_visits": visitor.cafe_visits,
                "restaurant_visits": visitor.restaurant_visits,
                "apres_ski_visits": visitor.apres_ski_visits,
                "first_aid_visits": visitor.first_aid_visits,
                "instructor_visits": visitor.instructor_visits,
                "equipment_returns": visitor.equipment_returns,
                "injury_status": visitor.injury_status,
                "energy_left": visitor.energy,
            })

            visitor.resort.database.log_event(
                visitor.visitor_id,
                "completed",
                "resort",
                0
            )

            visitor.resort.database.update_visitor_summary(visitor)

        return None