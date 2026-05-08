import threading
from collections import deque
import random
import time

from config import (
    NUM_SKIS,
    NUM_SNOWBOARDS,
    RENTAL_STAFF,
    RENTAL_TIME_MIN,
    RENTAL_TIME_MAX,
    NUM_LIFTS,
    LIFT_CAPACITY,
    LIFT_RIDE_TIME_MIN,
    LIFT_RIDE_TIME_MAX,
    FALL_CHANCE,
    FALL_DELAY,
    SLOPE_CONFIGS,
    WEATHER_EFFECTS,
    AGE_EFFECTS,
    RETURN_STAFF,
    RETURN_TIME_MIN,
    RETURN_TIME_MAX,
    RESTAURANT_SEATS,
    RESTAURANT_STAFF,
    RESTAURANT_TIME_MIN,
    RESTAURANT_TIME_MAX,
    APRES_SKI_CAPACITY,
    APRES_SKI_TIME_MIN,
    APRES_SKI_TIME_MAX,
    PARAMEDICS,
    SERIOUS_FALL_CHANCE,
    FIRST_AID_TIME_MIN,
    FIRST_AID_TIME_MAX,
    EMERGENCY_PRIORITY_ENABLED,
    NUM_INSTRUCTORS,
    STAFF_FATIGUE_MULTIPLIER,
    LUNCH_SERVICE_SLOWDOWN_FACTOR,
    CLOSING_SERVICE_SLOWDOWN_FACTOR,
    PEAK_SERVICE_SLOWDOWN_FACTOR,
    CAFE_SEATS,
    CAFE_STAFF,
    CAFE_TIME_MIN,
    CAFE_TIME_MAX,
)

def _weather_for(visitor):
    resort = getattr(visitor, "resort", None)
    if resort is None:
        return "sunny"
    return getattr(resort, "weather", "sunny")


def _phase_for(visitor):
    resort = getattr(visitor, "resort", None)
    if resort is None:
        return "normal"
    return getattr(resort, "phase", "normal")


def _service_multiplier(visitor):
    phase = _phase_for(visitor)

    multiplier = 1.0

    age_group = getattr(visitor, "age_group", "adult")
    multiplier *= AGE_EFFECTS.get(age_group, {}).get("break_multiplier", 1.0)

    if getattr(visitor, "is_peak_arrival", False):
        multiplier *= PEAK_SERVICE_SLOWDOWN_FACTOR

    if phase == "lunch":
        multiplier *= LUNCH_SERVICE_SLOWDOWN_FACTOR
    elif phase == "closing":
        multiplier *= CLOSING_SERVICE_SLOWDOWN_FACTOR

    if getattr(visitor, "staff_fatigue_active", False):
        multiplier *= STAFF_FATIGUE_MULTIPLIER

    return multiplier

def _lift_multiplier(visitor):
    weather = _weather_for(visitor)
    return WEATHER_EFFECTS.get(weather, {}).get("lift_multiplier", 1.0) * _service_multiplier(visitor)


def _slope_multiplier(visitor):
    weather = _weather_for(visitor)
    return WEATHER_EFFECTS.get(weather, {}).get("slope_multiplier", 1.0) * _service_multiplier(visitor)


def _fall_multiplier(visitor):
    weather = _weather_for(visitor)
    age_group = getattr(visitor, "age_group", "adult")
    skill_level = getattr(visitor, "skill_level", "intermediate")

    total = WEATHER_EFFECTS.get(weather, {}).get("fall_multiplier", 1.0)
    total *= AGE_EFFECTS.get(age_group, {}).get("fall_multiplier", 1.0)

    skill_effects = {
        "beginner": 1.3,
        "intermediate": 1.0,
        "advanced": 0.8,
    }
    total *= skill_effects.get(skill_level, 1.0)

    return total

def _indoor_weather_multiplier(visitor):
    weather = _weather_for(visitor)
    return WEATHER_EFFECTS.get(weather, {}).get("break_multiplier", 1.0)


def _log(visitor, event_type, area, wait_time=0, severity=None):
    resort = getattr(visitor, "resort", None)
    if resort is not None and getattr(resort, "database", None) is not None:
        resort.database.log_event(
            visitor.visitor_id,
            event_type,
            area,
            wait_time,
            severity=severity,
            weather=_weather_for(visitor),
            age_group=getattr(visitor, "age_group", None),
            skill_level=getattr(visitor, "skill_level", None),
            own_equipment=getattr(visitor, "has_own_equipment", False),
            ski_school=getattr(visitor, "is_ski_school", False),
        )

SLOPE_PROFILE_LOOKUP = {item["name"]: item for item in SLOPE_CONFIGS}

class RentalShop:
    def __init__(self):
        self.skis_available = NUM_SKIS
        self.snowboards_available = NUM_SNOWBOARDS
        self.staff_available = RENTAL_STAFF

        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor.visitor_id not in self.queue_ids:
            self.queue.append(visitor)
            self.queue_ids.add(visitor.visitor_id)
            self.wait_start_times[visitor.visitor_id] = time.time()

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)

            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def rent_equipment(self, visitor):
        with self.lock:
            can_rent = (
                self.staff_available > 0
                and (
                    (visitor.visitor_type == "skier" and self.skis_available > 0)
                    or (visitor.visitor_type == "snowboarder" and self.snowboards_available > 0)
                )
            )

            if not can_rent:
                self._add_to_queue_if_needed(visitor)
                queue_length = len(self.queue)
                self.notify_observers("rental_queue", queue_length)
                return False

            self.staff_available -= 1

            if visitor.visitor_type == "skier":
                self.skis_available -= 1
            else:
                self.snowboards_available -= 1

            wait_time = self._get_wait_time(visitor)
            self._remove_from_queue_if_present(visitor)

        service_time = random.uniform(RENTAL_TIME_MIN, RENTAL_TIME_MAX) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor)
        time.sleep(service_time)

        with self.lock:
            self.staff_available += 1

        self.notify_observers("rental_wait", wait_time)

        if visitor.resort is not None:
            visitor.resort.database.log_event(
                visitor.visitor_id,
                "rental_wait",
                "RentalShop",
                wait_time
            )

        return True

    def return_equipment(self, visitor):
        with self.lock:
            if visitor.visitor_type == "skier":
                self.skis_available += 1
            else:
                self.snowboards_available += 1

            self._remove_from_queue_if_present(visitor)
            self.wait_start_times.pop(visitor.visitor_id, None)


class LiftStation:
    def __init__(self):
        self.capacity = NUM_LIFTS * LIFT_CAPACITY
        self.current = 0

        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor.visitor_id not in self.queue_ids:
            self.queue.append(visitor)
            self.queue_ids.add(visitor.visitor_id)
            self.wait_start_times[visitor.visitor_id] = time.time()

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)

            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def use_lift(self, visitor):
        with self.lock:
            if self.current >= self.capacity:
                self._add_to_queue_if_needed(visitor)
                queue_length = len(self.queue)
                self.notify_observers("lift_queue", queue_length)
                return False

            self.current += 1
            wait_time = self._get_wait_time(visitor)
            self._remove_from_queue_if_present(visitor)

        self.notify_observers("lift_wait", wait_time)

        if visitor.resort is not None:
            visitor.resort.database.log_event(
                visitor.visitor_id,
                "lift_wait",
                "LiftStation",
                wait_time
            )

        ride_time = random.uniform(LIFT_RIDE_TIME_MIN, LIFT_RIDE_TIME_MAX) * _lift_multiplier(visitor)
        time.sleep(ride_time)

        return True

    def leave_lift(self):
        with self.lock:
            if self.current > 0:
                self.current -= 1


class Cafe:
    def __init__(self):
        self.capacity = CAFE_SEATS
        self.staff_available = CAFE_STAFF
        self.current = 0

        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor.visitor_id not in self.queue_ids:
            self.queue.append(visitor)
            self.queue_ids.add(visitor.visitor_id)
            self.wait_start_times[visitor.visitor_id] = time.time()

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)

            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def visit(self, visitor):
        with self.lock:
            if self.current >= self.capacity or self.staff_available <= 0:
                self._add_to_queue_if_needed(visitor)
                queue_length = len(self.queue)
                self.notify_observers("cafe_queue", queue_length)
                return False

            self.current += 1
            self.staff_available -= 1

            wait_time = self._get_wait_time(visitor)
            self._remove_from_queue_if_present(visitor)

        service_time = random.uniform(CAFE_TIME_MIN, CAFE_TIME_MAX) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor)
        time.sleep(service_time)

        with self.lock:
            if self.current > 0:
                self.current -= 1
            self.staff_available += 1

        self.notify_observers("cafe_wait", wait_time)
        self.notify_observers("cafe", None)

        if visitor.resort is not None:
            visitor.resort.database.log_event(
                visitor.visitor_id,
                "cafe_wait",
                "Cafe",
                wait_time
            )

            visitor.resort.database.log_event(
                visitor.visitor_id,
                "cafe",
                "Cafe",
                0
            )

        return True


class Slope:
    def __init__(self, slope_name=None, slope_config=None):
        if slope_config is None:
            if slope_name is None:
                slope_config = SLOPE_CONFIGS[0]
            else:
                slope_config = SLOPE_PROFILE_LOOKUP[slope_name]

        self.name = slope_config["name"]
        self.difficulty = slope_config["difficulty"]
        self.capacity = slope_config["capacity"]
        self.run_time_min = slope_config["time_min"]
        self.run_time_max = slope_config["time_max"]
        self.fall_modifier = slope_config["fall_modifier"]

        self.current = 0
        self.is_open = True

        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor.visitor_id not in self.queue_ids:
            self.queue.append(visitor)
            self.queue_ids.add(visitor.visitor_id)
            self.wait_start_times[visitor.visitor_id] = time.time()

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)
            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def go_down(self, visitor):
        weather = _weather_for(visitor)

        if not self.is_open:
            self.notify_observers("slope_closed", self.name)
            _log(visitor, "slope_closed", self.name, 0)
            return False, False

        if weather == "foggy" and random.random() < WEATHER_EFFECTS["foggy"]["slope_closure_chance"]:
            self.is_open = False
            self.notify_observers("slope_closed", self.name)
            _log(visitor, "slope_closed", self.name, 0)
            return False, False

        with self.lock:
            if self.current >= self.capacity:
                self._add_to_queue_if_needed(visitor)
                self.notify_observers("slope_queue", len(self.queue))
                return False, False

            self.current += 1
            self._remove_from_queue_if_present(visitor)
            self.wait_start_times.pop(visitor.visitor_id, None)

        self.notify_observers("run", 1)
        self.notify_observers("slope_used", self.name)
        _log(visitor, "slope_run", self.name, 0)

        run_time = random.uniform(self.run_time_min, self.run_time_max) * _slope_multiplier(visitor)
        time.sleep(run_time)

        fall_risk = visitor.strategy.base_fall_risk() if hasattr(visitor.strategy, "base_fall_risk") else FALL_CHANCE
        fall_risk *= self.fall_modifier
        fall_risk *= _fall_multiplier(visitor)

        fell = False

        if random.random() < fall_risk:
            fell = True
            self.notify_observers("fall", 1)
            _log(visitor, "fall", self.name, 0)

            serious = random.random() < SERIOUS_FALL_CHANCE
            if serious:
                visitor.injury_status = "serious"
                self.notify_observers("serious_fall", 1)
                _log(visitor, "serious_fall", self.name, 0, severity="serious")
            else:
                visitor.injury_status = "minor"
                _log(visitor, "minor_fall", self.name, 0, severity="minor")

            time.sleep(FALL_DELAY * _service_multiplier(visitor))

        with self.lock:
            if self.current > 0:
                self.current -= 1

        return True, fell

class Restaurant:
    def __init__(self):
        self.capacity = RESTAURANT_SEATS
        self.staff_available = RESTAURANT_STAFF
        self.current = 0

        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def visit(self, visitor):
        with self.lock:
            if self.current >= self.capacity or self.staff_available <= 0:
                if visitor.visitor_id not in self.queue_ids:
                    self.queue.append(visitor)
                    self.queue_ids.add(visitor.visitor_id)
                    self.wait_start_times[visitor.visitor_id] = time.time()
                self.notify_observers("restaurant_queue", len(self.queue))
                return False

            self.current += 1
            self.staff_available -= 1
            wait_time = self._get_wait_time(visitor)
            self._remove_from_queue_if_present(visitor)

        service_time = random.uniform(RESTAURANT_TIME_MIN, RESTAURANT_TIME_MAX) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor)
        time.sleep(service_time)

        with self.lock:
            if self.current > 0:
                self.current -= 1
            self.staff_available += 1

        self.notify_observers("restaurant_wait", wait_time)
        self.notify_observers("restaurant", 1)
        _log(visitor, "restaurant_wait", "Restaurant", wait_time)
        _log(visitor, "restaurant", "Restaurant", 0)
        return True

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)
            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

class ApresSki:
    def __init__(self):
        self.capacity = APRES_SKI_CAPACITY
        self.current = 0

        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def visit(self, visitor):
        with self.lock:
            if self.current >= self.capacity:
                if visitor.visitor_id not in self.queue_ids:
                    self.queue.append(visitor)
                    self.queue_ids.add(visitor.visitor_id)
                    self.wait_start_times[visitor.visitor_id] = time.time()
                self.notify_observers("apres_queue", len(self.queue))
                return False

            self.current += 1
            wait_time = self._get_wait_time(visitor)
            if visitor.visitor_id in self.queue_ids:
                self.queue_ids.remove(visitor.visitor_id)
                for queued_visitor in list(self.queue):
                    if queued_visitor.visitor_id == visitor.visitor_id:
                        self.queue.remove(queued_visitor)
                        break

        service_time = random.uniform(APRES_SKI_TIME_MIN, APRES_SKI_TIME_MAX) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor)
        time.sleep(service_time)

        with self.lock:
            if self.current > 0:
                self.current -= 1

        self.notify_observers("apres_wait", wait_time)
        self.notify_observers("apres_ski", 1)
        _log(visitor, "apres_wait", "ApresSki", wait_time)
        _log(visitor, "apres_ski", "ApresSki", 0)
        return True

class FirstAidStation:
    def __init__(self):
        self.capacity = PARAMEDICS
        self.current = 0

        self.queue = deque()
        self.priority_queue = deque()
        self.queue_ids = set()
        self.priority_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def treat(self, visitor):
        serious = getattr(visitor, "injury_status", None) == "serious"
        use_priority = serious and EMERGENCY_PRIORITY_ENABLED

        with self.lock:
            if self.current >= self.capacity:
                target_queue = self.priority_queue if use_priority else self.queue
                target_ids = self.priority_ids if use_priority else self.queue_ids

                if visitor.visitor_id not in target_ids:
                    target_queue.append(visitor)
                    target_ids.add(visitor.visitor_id)
                    self.wait_start_times[visitor.visitor_id] = time.time()

                if use_priority:
                    self.notify_observers("first_aid_priority_queue", len(self.priority_queue))
                else:
                    self.notify_observers("first_aid_queue", len(self.queue))

                return False

            self.current += 1
            wait_time = self._get_wait_time(visitor)

        time.sleep(random.uniform(FIRST_AID_TIME_MIN, FIRST_AID_TIME_MAX) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor))

        with self.lock:
            if self.current > 0:
                self.current -= 1

        visitor.injury_status = "treated"
        self.notify_observers("first_aid_wait", wait_time)
        self.notify_observers("first_aid", 1)
        _log(visitor, "first_aid_wait", "FirstAidStation", wait_time)
        _log(visitor, "first_aid", "FirstAidStation", 0)
        return True

class InstructorPool:
    def __init__(self):
        self.instructors_available = NUM_INSTRUCTORS
        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def book(self, visitor):
        with self.lock:
            if self.instructors_available <= 0:
                if visitor.visitor_id not in self.queue_ids:
                    self.queue.append(visitor)
                    self.queue_ids.add(visitor.visitor_id)
                    self.wait_start_times[visitor.visitor_id] = time.time()
                self.notify_observers("instructor_queue", len(self.queue))
                return False

            self.instructors_available -= 1
            wait_time = self._get_wait_time(visitor)
            self._remove_from_queue_if_present(visitor)

        time.sleep(random.uniform(0.4, 0.9) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor))

        with self.lock:
            self.instructors_available += 1

        self.notify_observers("instructor_wait", wait_time)
        _log(visitor, "instructor_wait", "InstructorPool", wait_time)
        return True

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)
            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break


class EquipmentReturnDesk:
    def __init__(self):
        self.staff_available = RETURN_STAFF
        self.queue = deque()
        self.queue_ids = set()
        self.wait_start_times = {}

        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _get_wait_time(self, visitor):
        start_time = self.wait_start_times.pop(visitor.visitor_id, None)
        if start_time is None:
            return 0.0
        return round(time.time() - start_time, 2)

    def return_equipment(self, visitor):
        if getattr(visitor, "has_own_equipment", False):
            _log(visitor, "equipment_return_skip", "EquipmentReturnDesk", 0)
            return True

        with self.lock:
            if self.staff_available <= 0:
                if visitor.visitor_id not in self.queue_ids:
                    self.queue.append(visitor)
                    self.queue_ids.add(visitor.visitor_id)
                    self.wait_start_times[visitor.visitor_id] = time.time()
                self.notify_observers("return_queue", len(self.queue))
                return False

            self.staff_available -= 1
            wait_time = self._get_wait_time(visitor)
            self._remove_from_queue_if_present(visitor)

        time.sleep(random.uniform(RETURN_TIME_MIN, RETURN_TIME_MAX) * _service_multiplier(visitor) * _indoor_weather_multiplier(visitor))

        with self.lock:
            self.staff_available += 1

        resort = getattr(visitor, "resort", None)
        if resort is not None and getattr(resort, "rental_shop", None) is not None:
            with resort.rental_shop.lock:
                if visitor.visitor_type == "skier":
                    resort.rental_shop.skis_available += 1
                else:
                    resort.rental_shop.snowboards_available += 1

        self.notify_observers("return_wait", wait_time)
        _log(visitor, "equipment_return", "EquipmentReturnDesk", wait_time)
        return True

    def _remove_from_queue_if_present(self, visitor):
        if visitor.visitor_id in self.queue_ids:
            self.queue_ids.remove(visitor.visitor_id)
            for queued_visitor in list(self.queue):
                if queued_visitor.visitor_id == visitor.visitor_id:
                    self.queue.remove(queued_visitor)
                    break

