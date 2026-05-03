import threading
from collections import deque
import random
import time


class RentalShop:
    def __init__(self):
        self.skis_available = 45
        self.snowboards_available = 30
        self.staff_available = 4

        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def rent_equipment(self, visitor):
        with self.lock:
            if visitor.type == "skier" and self.skis_available > 0 and self.staff_available > 0:
                self.skis_available -= 1
                self.staff_available -= 1
                self.notify_observers("rental_wait", 0.0)
                return True

            elif visitor.type == "snowboarder" and self.snowboards_available > 0 and self.staff_available > 0:
                self.snowboards_available -= 1
                self.staff_available -= 1
                self.notify_observers("rental_wait", 0.0)
                return True

            else:
                self.queue.append(visitor)
                self.notify_observers("rental_queue", len(self.queue))
                return False

    def return_equipment(self, visitor):
        with self.lock:
            if visitor.type == "skier":
                self.skis_available += 1
            else:
                self.snowboards_available += 1

            self.staff_available += 1

            if self.queue:
                return self.queue.popleft()


class LiftStation:
    def __init__(self):
        self.capacity = 3 * 6
        self.current = 0
        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def use_lift(self, visitor):
        with self.lock:
            if self.current < self.capacity:
                self.current += 1
                self.notify_observers("lift_wait", 0.0)
                return True
            else:
                self.queue.append(visitor)
                self.notify_observers("lift_queue", len(self.queue))
                return False

    def leave_lift(self):
        with self.lock:
            if self.current > 0:
                self.current -= 1


class Cafe:
    def __init__(self):
        self.capacity = 25
        self.current = 0
        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def visit(self, visitor):
        with self.lock:
            if self.current < self.capacity:
                self.current += 1
                self.notify_observers("cafe_wait", 0.0)
            else:
                self.queue.append(visitor)
                self.notify_observers("cafe_queue", len(self.queue))
                return False

        time.sleep(random.uniform(2.0, 5.0))

        with self.lock:
            if self.current > 0:
                self.current -= 1
            if self.queue:
                self.queue.popleft()

        return True


class Slope:
    def __init__(self):
        self.capacity = 5 * 20
        self.current = 0
        self.queue = deque()
        self.lock = threading.Lock()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event_type, data=None):
        for obs in self.observers:
            obs.update(event_type, data)

    def go_down(self, visitor):
        with self.lock:
            if self.current < self.capacity:
                self.current += 1
            else:
                self.queue.append(visitor)
                return False

        self.notify_observers("run")

        time.sleep(random.uniform(3.0, 6.0))

        fall = False
        if random.random() < 0.08:
            fall = True
            print(f"Visitor {visitor.id} fell!")
            self.notify_observers("fall")
            time.sleep(2.0)

        with self.lock:
            if self.current > 0:
                self.current -= 1
            if self.queue:
                self.queue.popleft()

        return True