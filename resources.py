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
    NUM_SLOPES,
    SLOPE_CAPACITY,
    SLOPE_TIME_MIN,
    SLOPE_TIME_MAX,
    FALL_CHANCE,
    FALL_DELAY,
    CAFE_SEATS,
    CAFE_STAFF,
    CAFE_TIME_MIN,
    CAFE_TIME_MAX,
)


class RentalShop:
    def __init__(self):
        self.skis_available = NUM_SKIS
        self.snowboards_available = NUM_SNOWBOARDS
        self.staff_available = RENTAL_STAFF

        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor not in self.queue:
            self.queue.append(visitor)

    def _remove_from_queue_if_present(self, visitor):
        if visitor in self.queue:
            self.queue.remove(visitor)

    def rent_equipment(self, visitor):
        # Critical region: equipment count, staff count, and rental queue are shared by all visitor threads.
        with self.lock:
            can_rent = (
                self.staff_available > 0 and
                (
                    (visitor.visitor_type == "skier" and self.skis_available > 0) or
                    (visitor.visitor_type == "snowboarder" and self.snowboards_available > 0)
                )
            )

            if not can_rent:
                self._add_to_queue_if_needed(visitor)
                queue_length = len(self.queue)
                wait_time = round(queue_length * random.uniform(RENTAL_TIME_MIN, RENTAL_TIME_MAX), 2)
                self.notify_observers("rental_queue", queue_length)
                self.notify_observers("rental_wait", wait_time)
                return False

            self.staff_available -= 1

            if visitor.visitor_type == "skier":
                self.skis_available -= 1
            else:
                self.snowboards_available -= 1

            self._remove_from_queue_if_present(visitor)

        service_time = random.uniform(RENTAL_TIME_MIN, RENTAL_TIME_MAX)
        time.sleep(service_time)

        with self.lock:
            self.staff_available += 1

        self.notify_observers("rental_wait", round(service_time, 2))
        return True

    def return_equipment(self, visitor):
        # Critical region: equipment count is shared by all visitor threads.
        with self.lock:
            if visitor.visitor_type == "skier":
                self.skis_available += 1
            else:
                self.snowboards_available += 1

            self._remove_from_queue_if_present(visitor)


class LiftStation:
    def __init__(self):
        self.capacity = NUM_LIFTS * LIFT_CAPACITY
        self.current = 0

        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor not in self.queue:
            self.queue.append(visitor)

    def _remove_from_queue_if_present(self, visitor):
        if visitor in self.queue:
            self.queue.remove(visitor)

    def use_lift(self, visitor):
        # Critical region: lift capacity and lift queue are shared by all visitor threads.
        with self.lock:
            if self.current >= self.capacity:
                self._add_to_queue_if_needed(visitor)
                queue_length = len(self.queue)
                wait_time = round(queue_length * random.uniform(0.5, 1.5), 2)
                self.notify_observers("lift_queue", queue_length)
                self.notify_observers("lift_wait", wait_time)
                return False

            self.current += 1
            self._remove_from_queue_if_present(visitor)

        self.notify_observers("lift_wait", 0.0)
        return True

    def leave_lift(self):
        # Critical region: lift capacity is shared by all visitor threads.
        with self.lock:
            if self.current > 0:
                self.current -= 1


class Cafe:
    def __init__(self):
        self.capacity = CAFE_SEATS
        self.staff_available = CAFE_STAFF
        self.current = 0

        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor not in self.queue:
            self.queue.append(visitor)

    def _remove_from_queue_if_present(self, visitor):
        if visitor in self.queue:
            self.queue.remove(visitor)

    def visit(self, visitor):
        # Critical region: cafe seats, cafe staff, and cafe queue are shared by all visitor threads.
        with self.lock:
            if self.current >= self.capacity or self.staff_available <= 0:
                self._add_to_queue_if_needed(visitor)
                queue_length = len(self.queue)
                wait_time = round(queue_length * random.uniform(CAFE_TIME_MIN, CAFE_TIME_MAX), 2)
                self.notify_observers("cafe_queue", queue_length)
                self.notify_observers("cafe_wait", wait_time)
                return False

            self.current += 1
            self.staff_available -= 1
            self._remove_from_queue_if_present(visitor)

        service_time = random.uniform(CAFE_TIME_MIN, CAFE_TIME_MAX)
        time.sleep(service_time)

        with self.lock:
            if self.current > 0:
                self.current -= 1
            self.staff_available += 1

        self.notify_observers("cafe_wait", round(service_time, 2))
        self.notify_observers("cafe", None)
        return True


class Slope:
    def __init__(self):
        self.capacity = NUM_SLOPES * SLOPE_CAPACITY
        self.current = 0

        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def _add_to_queue_if_needed(self, visitor):
        if visitor not in self.queue:
            self.queue.append(visitor)

    def _remove_from_queue_if_present(self, visitor):
        if visitor in self.queue:
            self.queue.remove(visitor)

    def go_down(self, visitor):
        # Critical region: slope capacity and current visitors are shared by all visitor threads.
        with self.lock:
            if self.current >= self.capacity:
                self._add_to_queue_if_needed(visitor)
                return False, False

            self.current += 1
            self._remove_from_queue_if_present(visitor)

        self.notify_observers("run")

        time.sleep(random.uniform(SLOPE_TIME_MIN, SLOPE_TIME_MAX))

        fell = False
        if random.random() < FALL_CHANCE:
            fell = True
            print(f"Visitor {visitor.visitor_id} fell!")
            self.notify_observers("fall")
            time.sleep(FALL_DELAY)

        with self.lock:
            if self.current > 0:
                self.current -= 1

        return True, fell